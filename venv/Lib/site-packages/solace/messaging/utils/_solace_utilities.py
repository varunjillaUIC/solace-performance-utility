# solace-messaging-python-client
#
# Copyright 2021-2025 Solace Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Module for solace internal utilities"
# pylint: disable=missing-module-docstring,too-many-arguments,inconsistent-return-statements,no-else-raise
# pylint: disable=missing-function-docstring,no-else-return,missing-class-docstring
# pylint: disable=line-too-long
import concurrent
import itertools
import logging
import queue
import weakref
from queue import Full, Empty
import threading
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from time import time
from typing import Callable

from solace.messaging import _SolaceServiceAdapter
from solace.messaging._solace_logging._core_api_log import last_error_info
from solace.messaging.config._solace_message_constants import INVALID_DATATYPE, TOPIC_NAME_MAX_LENGTH, \
    TOPIC_NAME_TOO_LONG, VALUE_CANNOT_BE_NEGATIVE, GRACE_PERIOD_MIN_INVALID_ERROR_MESSAGE, DICT_CONTAINS_NONE_VALUE, \
    CCSMP_INFO_SUB_CODE, CCSMP_SUB_CODE, CCSMP_CALLER_DESC, CCSMP_INFO_CONTENTS, \
    CCSMP_RETURN_CODE, THREAD_TIMEOUT_MAX_VALUE, GRACE_PERIOD_MAX_TIMEOUT_ERROR_MESSAGE, GRACE_PERIOD_MIN_MS, \
    INVALID_EXPECTED_DATATYPE, VALUE_OUT_OF_RANGE
from solace.messaging.config.solace_properties.message_properties import APPLICATION_MESSAGE_TYPE, ELIDING_ELIGIBLE, \
    PRIORITY, HTTP_CONTENT_TYPE, HTTP_CONTENT_ENCODING, CORRELATION_ID, PERSISTENT_TIME_TO_LIVE, PERSISTENT_EXPIRATION, \
    PERSISTENT_DMQ_ELIGIBLE, PERSISTENT_ACK_IMMEDIATELY, SEQUENCE_NUMBER, APPLICATION_MESSAGE_ID, SENDER_ID
from solace.messaging.config.solace_properties._legacy_properties import _CORRELATION_ID_v1_2_0
from solace.messaging.errors.pubsubplus_client_error import InvalidDataTypeError, IllegalArgumentError, \
    PubSubPlusCoreClientError


class _PythonQueueEventExtension(queue.Queue):
    # enhanced python queue for registering callbacks on important internal queue events

    # defined queue event callbacks
    ON_FULL_EVENT: int = 0
    # on full event when queue goes from having available capacity to not
    # Note this event is not called if the queue is already full on put
    ON_AVAILABLE_EVENT: int = 1

    # on available event when queue goes from not having capacity to having available capacity
    # Note this event is not called if the queue already has capacity on get

    ON_BUFFER_OVERFLOW_EVENT: int = 2
    # on buffer overflow event when queue does not have capacity but there is an inbound message.
    # Note: this event is used at least by the direct receiver when DropOldest or DropLatest
    # back pressure strategies are enabled for that direct receiver.

    ON_PUT_ITEM_EVENT: int = 3
    @abstractmethod
    def register_on_event(self, event: int, event_handler: Callable[[], None]):
        """ registers defined event callbacks """

    @abstractmethod
    def register_on_low_watermark(self, handler: Callable[[], None], threshold: int):
        """ registers low watermark handler callback for a given threadhold """

    @abstractmethod
    def register_on_high_watermark(self, handler: Callable[[], None], threshold: int):
        """ registers high watermark handler callback for a given threadhold """

class QueueShutdown(Exception):
    'Exception raised by _PubSubPlusQueue.put(block=0)/put_nowait()/get()/get_nowait. After a call to shutdown'

# pylint: disable=too-many-instance-attributes
class _PubSubPlusQueue(_PythonQueueEventExtension):
    # extension to base fifo queue.Queue for thread safe peek
    # and wait for empty condition
    def __init__(self, maxsize=0, initial_running: bool = True):
        super().__init__(maxsize)
        self._is_empty = threading.Condition(self.mutex)
        self._registered_events = {}
        self._is_shutdown = False
        self._running = initial_running
        self._high_mark_threshold = -1
        self._high_mark_handler = None
        self._low_mark_threshold = -1
        self._low_mark_handler = None

    def register_on_event(self, event: int, event_handler: Callable[[], None]):
        with self.mutex:
            self._registered_events[event] = event_handler

    def register_on_low_watermark(self, handler: Callable[[], None], threshold: int):
        with self.mutex:
            if threshold >= 0:
                self._low_mark_threshold = threshold
                self._low_mark_handler = handler

    def register_on_high_watermark(self, handler: Callable[[], None], threshold: int):
        with self.mutex:
            if threshold > 0:
                self._high_mark_threshold = threshold
                self._high_mark_handler = handler

    def _get(self):
        # override _get note self.mutex is assumed to be held during this function
        if self.maxsize > 0:
            presize = self._qsize()
            item = super()._get()
            if presize >= self.maxsize and self._qsize() < self.maxsize:
                on_available = self._registered_events.get(_PubSubPlusQueue.ON_AVAILABLE_EVENT)
                if on_available:
                    on_available()
        else:
            item = super()._get()
        if self._low_mark_handler and self._qsize() == self._low_mark_threshold:
            self._low_mark_handler()
        if self._qsize() == 0:
            self._is_empty.notify_all()
        return item

    def get(self, block=True, timeout=None):
        '''Remove and return an item from the queue.
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        '''
        with self.not_empty:
            if self._is_shutdown:
                raise QueueShutdown
            if not block:
                if not self._qsize() or not self._running:
                    raise Empty
            elif timeout is None:
                while not self._qsize() or not self._running:
                    if self._is_shutdown:
                        raise QueueShutdown
                    self.not_empty.wait()

            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize() or not self._running:
                    if self._is_shutdown:
                        raise QueueShutdown
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            return item

    # We ignore arguements-renamed because the order of the arguements in the put() method is different than in the
    # original Queue method. This should not affect functionality since this overridden method is only used through
    # the _PubSubPlusQueue object, which expects the current interface.
    # pylint: disable=arguments-differ, too-many-branches, arguments-renamed
    def put(self, item, block=True, force=False, timeout=None):
        """Put an item into the queue.
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case)."""
        _put_has_not_been_called = True
        with self.not_full:
            if self._is_shutdown:
                raise QueueShutdown
            on_item_put = self._registered_events.get(_PubSubPlusQueue.ON_PUT_ITEM_EVENT)
            if on_item_put:
                on_item_put(item)
            removed = None
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        on_overflow = self._registered_events.get(_PubSubPlusQueue.ON_BUFFER_OVERFLOW_EVENT)
                        if on_overflow:
                            on_overflow(item)
                        raise Full
                elif timeout is None:
                    if force and (self._qsize() >= self.maxsize):
                        # The queue must be in its final state before calling the callback method.
                        # This means that the oldest message must be removed and the incoming
                        # message must be added before calling the callback method.
                        removed = self._get()
                        self._put(item)
                        _put_has_not_been_called = False
                        on_overflow = self._registered_events.get(_PubSubPlusQueue.ON_BUFFER_OVERFLOW_EVENT)
                        if on_overflow:
                            on_overflow(removed)
                    else:
                        while self._qsize() >= self.maxsize:
                            if self._is_shutdown:
                                raise QueueShutdown
                            self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        if self._is_shutdown:
                            raise QueueShutdown
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            on_overflow = self._registered_events.get(_PubSubPlusQueue.ON_BUFFER_OVERFLOW_EVENT)
                            if on_overflow:
                                on_overflow(item)
                            raise Full
                        self.not_full.wait(remaining)
            if _put_has_not_been_called:
                # If nothing has been put on the queue yet,
                # we'll add to the queue now
                self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
            return removed

    def _put(self, item):
        # override _put note self.mutex is assumed to be held during this function
        if self.maxsize > 0:
            presize = self._qsize()
            super()._put(item)
            if presize < self.maxsize and self._qsize() >= self.maxsize:
                on_full = self._registered_events.get(_PubSubPlusQueue.ON_FULL_EVENT)
                if on_full:
                    on_full()
        else:
            super()._put(item)
        if self._high_mark_handler and self._qsize() == self._high_mark_threshold:
            self._high_mark_handler()

    def wait_for_empty(self, timeout: float = None, predicate: Callable[[], bool] = None) -> float:
        with self._is_empty:
            def is_false() -> bool:
                return False

            additional_condition = is_false if predicate is None else predicate
            if timeout is None:
                starttime = time()
                while self._qsize() != 0 or additional_condition():
                    if self._is_shutdown:
                        break
                    self._is_empty.wait()
                remaining = time() - starttime
            else:
                remaining = timeout
                endtime = time() + timeout
                while self._qsize() != 0 or additional_condition():
                    remaining = endtime - time()
                    if remaining < 0.0:
                        remaining = 0.0
                        break
                    if self._is_shutdown:
                        break
                    self._is_empty.wait(remaining)
            return remaining

    def peek(self):
        # thread safe peek extension
        with self.mutex:
            if self._is_shutdown:
                return None
            return self.unsafe_peek()

    def unsafe_peek(self):
        # unsafe thread peek extension
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            return None

    def unsafe_full(self):
        # returns the internal queue full indication without mutex protection
        # used for performance first state checking not for garenteed accuracy
        return 0 < self.maxsize <= self._qsize()

    def unsafe_drain(self):
        # be careful calling from inside event callbacks
        # this changes the internal backing queue can
        # lead to undefined behaviour when getting from an
        # empty queue after an event.
        # Can be used on put events though.
        drained = []
        while self._qsize() > 0:
            # drained from backing queue
            # to not trigger events
            drained.append(super()._get())
        return drained

    def drain(self):
        # thread safe version of unsafe_drain
        # can deadlock if called from extension queue
        # event callback
        with self.mutex:
            return self.unsafe_drain()

    def suspend(self):
        # suspends all blocking get calls
        with self.not_empty:
            if self._is_shutdown:
                return
            self._running = False

    def resume(self):
        with self.not_empty:
            self._running = True
            self.not_empty.notify()


    def shutdown(self):
        with self.mutex:
            self._is_shutdown = True
            # unblock all waiters
            self._is_empty.notify_all()
            self.not_full.notify_all()
            self.not_empty.notify_all()


class _ThreadingUtil:
    # threading utilities
    @staticmethod
    def create_serialized_executor(name_prefix: str = None) -> 'Executor':
        # utility method for global api serialization construction
        # should ThreadPoolExecutor not be performant this can replace all constructed
        # serialized executors in the api
        prefix = name_prefix if name_prefix is not None else 'pubsubplus_python_client_thread'
        return ThreadPoolExecutor(max_workers=1, thread_name_prefix=prefix)

    @staticmethod
    def create_serialized_dispatcher(name_prefix: str = None, owner=None, logger=None):
        prefix = name_prefix if name_prefix is not None else 'pubsubplus_python_client_dispatcher_thread'
        return _SolaceSingleThreadDispatcher(prefix, owner=owner, logger=logger)


def is_type_matches(actual, expected_type, raise_exception=True, ignore_none=False, exception_message=None,
                    logger=None) -> bool:
    # Args:
    #     actual: target input parameter
    #     expected_type: compare ACTUAL data type with this
    #     raise_exception: if actual and expected date type doesn't matches
    #     ignore_none: ignore type check if ACTUAL is None
    #
    # Returns: True if actual and expected date type matches, else False
    if isinstance(actual, expected_type) or (ignore_none and actual is None):
        return True
    if raise_exception:
        if exception_message is None:
            exception_message = f'{INVALID_DATATYPE} Expected type: [{expected_type}], ' \
                                f'but actual [{type(actual)}]'
        if logger is not None:
            logger.warning(exception_message)
        raise InvalidDataTypeError(exception_message)
    return False

def validate_message_props(props: dict):
    properties_type_mapping = {APPLICATION_MESSAGE_TYPE: [str],
                               ELIDING_ELIGIBLE: [int],
                               PRIORITY: [int],
                               HTTP_CONTENT_TYPE: [str],
                               HTTP_CONTENT_ENCODING: [str],
                               SENDER_ID: [str, type(None)],
                               CORRELATION_ID: [str],
                               _CORRELATION_ID_v1_2_0: [str],
                               PERSISTENT_TIME_TO_LIVE: [int],
                               PERSISTENT_EXPIRATION: [int],
                               PERSISTENT_DMQ_ELIGIBLE: [int],
                               PERSISTENT_ACK_IMMEDIATELY: [int],
                               SEQUENCE_NUMBER: [int],
                               APPLICATION_MESSAGE_ID: [str]}
    for key in props:
        if key in properties_type_mapping:
            if not type(props[key]) in properties_type_mapping[key]:  # pylint: disable=unidiomatic-typecheck
                if isinstance(props[key], bool):
                    return
                raise InvalidDataTypeError(INVALID_EXPECTED_DATATYPE.substitute(actual_type=type(props[key]),
                                                                                expected_type=properties_type_mapping[
                                                                                    key]))

def get_last_error_info(return_code: int, caller_description: str, exception_message: str = None):
    last_error = last_error_info(return_code, caller_desc=caller_description)
    cleansed_last_error = f'Caller Description: {last_error[CCSMP_CALLER_DESC]}. ' \
                          f'Error Info Sub code: [{last_error[CCSMP_INFO_SUB_CODE]}]. ' \
                          f'Error: [{last_error[CCSMP_INFO_CONTENTS]}]. ' \
                          f'Sub code: [{last_error[CCSMP_SUB_CODE]}]. ' \
                          f'Return code: [{last_error[CCSMP_RETURN_CODE]}]'
    if exception_message:
        cleansed_last_error = f'{exception_message}\n{cleansed_last_error}'
    return PubSubPlusCoreClientError(cleansed_last_error, last_error[CCSMP_INFO_SUB_CODE])


def generate_exception_from_last_error_info(last_error: dict, exception_message: str):
    """
    This function allows API objects to first call last_error_info(), examine the sub code, generate and exception
    message based on that sub code, and then put it all together to make an exception.

    Args:
        last_error_info(dict): The last error info to read from.
        exception_message(str): The customizable exception string.

    Returns:
        PubSubPlusCoreClientError: The generated exception.
    """
    cleansed_last_error = f'Caller Description: {last_error[CCSMP_CALLER_DESC]}. ' \
                          f'Error Info Sub code: [{last_error[CCSMP_INFO_SUB_CODE]}]. ' \
                          f'Error: [{last_error[CCSMP_INFO_CONTENTS]}]. ' \
                          f'Sub code: [{last_error[CCSMP_SUB_CODE]}]. ' \
                          f'Return code: [{last_error[CCSMP_RETURN_CODE]}]'
    if exception_message:
        cleansed_last_error = f'{exception_message}\n{cleansed_last_error}'
    return PubSubPlusCoreClientError(cleansed_last_error, last_error[CCSMP_INFO_SUB_CODE])


def is_topic_valid(topic_name, logger, error_message):
    if topic_name is None or len(topic_name) == 0:
        logger.warning(error_message)
        raise IllegalArgumentError(error_message)
    if len(topic_name) > TOPIC_NAME_MAX_LENGTH:
        logger.warning(TOPIC_NAME_TOO_LONG)
        raise IllegalArgumentError(TOPIC_NAME_TOO_LONG)
    return True


def is_not_negative(input_value, raise_exception=True, exception_message=None, logger=None) -> bool:
    is_type_matches(input_value, int, logger=logger)
    if input_value < 0:
        error_message = VALUE_CANNOT_BE_NEGATIVE if exception_message is None else exception_message
        if logger:
            logger.warning(error_message)
        if raise_exception:
            raise IllegalArgumentError(VALUE_CANNOT_BE_NEGATIVE)
    return False

def is_value_within_expected_string_range(input_value, expected_value, raise_exception=True, exception_message=None, logger=None) -> bool:
    is_type_matches(input_value, str, logger=logger)
    if input_value not in expected_value:
        if exception_message is None:
            exception_message = f'Expected range of values: [{expected_value}], but input value: {input_value}. '
        if logger:
            logger.warning(exception_message)
        if raise_exception:
            raise IllegalArgumentError(exception_message)
    return False


def is_value_out_of_range(lower_bound, upper_bound, input_value, raise_exception=True, exception_message=None, logger=None) -> bool:
    is_type_matches(input_value, int, logger=logger)
    if input_value < lower_bound or input_value > upper_bound:
        error_message = VALUE_OUT_OF_RANGE + f"{lower_bound} to {upper_bound}, inclusive." if exception_message is None else exception_message
        if logger:
            logger.warning(error_message)
        if raise_exception:
            raise IllegalArgumentError(error_message)
    return False


def convert_ms_to_seconds(milli_seconds):
    return milli_seconds / 1000


def handle_none_for_str(input_value):
    if input_value is None:
        return str(None)
    return input_value


def validate_grace_period(grace_period, logger):
    if grace_period < GRACE_PERIOD_MIN_MS:
        logger.warning(GRACE_PERIOD_MIN_INVALID_ERROR_MESSAGE)
        raise IllegalArgumentError(GRACE_PERIOD_MIN_INVALID_ERROR_MESSAGE)

    if grace_period > THREAD_TIMEOUT_MAX_VALUE:
        logger.warning(GRACE_PERIOD_MAX_TIMEOUT_ERROR_MESSAGE)
        raise IllegalArgumentError(GRACE_PERIOD_MAX_TIMEOUT_ERROR_MESSAGE)


def is_none_or_empty_exists(given_dict, error_message=None, logger=None, raise_error=True):
    is_none_exists = all((value == '' or value is None) for value in given_dict.values())
    if error_message is None:
        error_message = DICT_CONTAINS_NONE_VALUE
    if is_none_exists:
        if logger:
            logger.warning(error_message)
        if raise_error:
            raise IllegalArgumentError(error_message)
        else:
            return True
    return False


def _create_completed_future():
    exc = _ThreadingUtil.create_serialized_executor()

    def _to_run():
        pass

    future = exc.submit(_to_run)
    exc.shutdown(wait=True)
    future.result()
    return future

def __create_module_dispatcher():
    return _SolaceSingleThreadDispatcher(
        worker_name_prefix='solace.module.dispatcher',
        owner="solace.messaging.utils._solace_utilities",
        logger=logging.getLogger('solace.messaging.core'))

def _shutdown_executor_sync(executor):
    executor.shutdown()

def _shutdown_executor_async(executor):
    executor.shutdown(wait=False)
    return SOLACE_MODULE_DISPATCHER.submit(_shutdown_executor_sync, executor)

COMPLETED_FUTURE = _create_completed_future()

def executor_shutdown(executor):
    try:
        if isinstance(executor, concurrent.futures.thread.ThreadPoolExecutor):
            #executor.shutdown()
            _shutdown_executor_async(executor)
    except RuntimeError as error:  # this shouldn't happen ideally when this function is called by weakref finalize
        logging.getLogger('solace.messaging').warning(str(error))


class _Released:  # this would a context to temporarily release an acquired lock for long waits
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.release()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.acquire()

class _SolaceThread(threading.Thread):
    def __init__(self, owner_id_info: str, logger: 'logging.Logger', *args, **kwargs):
        # This Event is intended to allow a means of stopping the thread
        # beyond the normal functionality of the thread, in case an error
        # occurs which prevents the normal means of stopping the thread
        # from occurring. It is set to True by default so that any calls
        # to wait() are not blocked.
        self._is_running = threading.Event()
        self._is_running.set()
        self._type = type(self).__name__
        self._id_info = f"owner: {owner_id_info}; thread {self._type}: {str(hex(id(self)))}"
        self.adapter = _SolaceServiceAdapter(logger, {'id_info': self._id_info})
        if logger.isEnabledFor(logging.DEBUG):  # pragma: no cover # Ignored due to log level
            self.adapter.debug('THREAD: [%s] initialized', self._type)
        super().__init__(*args, **kwargs)

    # The Python docs say that this method should not be overwritten,
    # so if errors are traced to joining this thread, there could be issues
    # with this extended implementation, or with the compatibility of this
    # extension with the parent method.
    def join(self, timeout=None):
        self._on_join()
        # clear the _is_running Event after _on_join() but before join()
        # so that the normal cleanup operation can occur, and only afterwards
        # update the Event in case the cleanup operation did not run as
        # expected. Clearing the event before _on_join() could block calls
        # to _is_running.wait(), if for some reason the child class needs to
        # do that in its implementation.
        self._is_running.clear()
        super().join()

    @abstractmethod
    def _on_join(self):
        """
        This method should be implemented by child classes to handle any
        cleanup required before joining to avoid hanging on thread join.
        """

class _SolaceSingleThreadDispatcher():
        # work out if inheritence from concurrent.futures.Executor would be better for object interface contract
        #(concurrent.futures.Executor):
    class _SolaceDistpatherThread(_SolaceThread):
        def __init__(self, worker_queue, *args, **kwargs):
            self.drain = False
            self._worker_queue = worker_queue
            super().__init__(*args, **kwargs)
            self.daemon = True

        # pylint: disable=invalid-name
        def run(self):
            self.adapter.debug('THREAD: [%s] started', self.name or self._type)
            while True:
                wi = None
                try:
                    wi = self._worker_queue.get()
                except QueueShutdown:
                    if self.drain:
                        items = self._worker_queue.drain()
                        for i in items:
                            i.run()
                    break
                if wi:
                    wi.run()
            self.adapter.debug('THREAD: [%s] exited', self.name or self._type)

        def _on_join(self):
            self._worker_queue.shutdown()

    # pylint: disable=invalid-name
    class _WorkItem:
        def __init__(self, fn, args, kwargs):
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
        def run(self):
            self.fn(*self.args, **self.kwargs)

    def __init__(self, worker_name_prefix: str = None, owner=None, logger=None):
        self._prefix = worker_name_prefix if not worker_name_prefix is None else f'{type(self).__name__}_worker'
        self._suffix_gen = itertools.count()
        self._worker_queue = _PubSubPlusQueue()

        self._worker = self.__create_worker(owner, logger)
        def worker_finalize(worker):
            worker.join()
        self._worker_finalizer = weakref.finalize(self, worker_finalize, self._worker)
        self._worker.start()

    # pylint: disable=invalid-name
    def __create_worker(self, owner, logger):
        o = owner or self
        l = logger or logging.getLogger('solace.messaging.core')
        return _SolaceSingleThreadDispatcher._SolaceDistpatherThread(self._worker_queue,
                                                                     f'{type(o).__name__}-{str(hex(id(o)))}',
                                                                     l,
                                                                     name=f'{self._prefix}_{self.__next_worker_id()}')
    def __next_worker_id(self) -> int:
        # used built-in GIL lock for thread safe increment and return
        return next(self._suffix_gen)

    # pylint: disable=invalid-name
    def submit(self, fn, *args, **kwargs):
        wi = _SolaceSingleThreadDispatcher._WorkItem(fn, args, kwargs)
        try:
            self._worker_queue.put(wi)
        except QueueShutdown as qs:
            raise RuntimeError() from qs

    # pylint: disable=invalid-name
    def map(self, fn, *iterables, timeout=None, chunksize=1):
        raise NotImplementedError()


    def shutdown(self, wait: bool = True, *, cancel: bool = False):
        if not cancel:
            self._worker.drain = True
        self._worker_queue.shutdown()
        if wait:
            #self._worker.join()
            self._worker_finalizer()


# pylint: disable=too-few-public-methods
class Holder:
    # a wrapping class to allow for finalizer registration order
    # later mutate a value for the finalizer to use
    # might want to revisit the placement of this class definition
    def __init__(self):
        self.value = None


# Converts a dict of NextGen props to CCSMP props
def convert_config(config, conversion_dict):
    result = {}
    for key, value in config.items():
        if key in conversion_dict:
            # Note: Here order if elif to check bool & int is very important don't change them
            if isinstance(value, bool):
                value = str(int(value))
            elif isinstance(value, int):
                value = str(value)
            result[conversion_dict[key]] = value
        else:
            result[key] = value
    return result

SOLACE_MODULE_DISPATCHER = __create_module_dispatcher()
