# import time
# import threading
# from solengineer.publisher.topic_publisher import TopicPublisher
# from solengineer.subscriber.topic_subscriber import TopicSubscriber


# class PerfTester:

#     def __init__(self, service):
#         self.service = service
#         self.results = {}

#     def run(self, topic: str, message_count: int, message_size: int, on_progress=None):
#         payload = "X" * message_size
#         latencies = []
#         received = []
#         errors = 0

#         subscriber = TopicSubscriber(self.service)
#         subscriber.start(topic)

#         publisher = TopicPublisher(self.service)

#         start_time = time.time()

#         def publish_messages():
#             nonlocal errors
#             for i in range(message_count):
#                 try:
#                     stamped = f"{time.time()}|{payload}"
#                     publisher.publish(topic, stamped)
#                 except Exception:
#                     errors += 1

#         pub_thread = threading.Thread(target=publish_messages)
#         pub_thread.start()

#         deadline = time.time() + 30
#         while len(received) < message_count and time.time() < deadline:
#             msg = subscriber.receive(timeout=2000)
#             if msg:
#                 raw = msg.get_payload_as_string()
#                 try:
#                     sent_time = float(raw.split("|")[0])
#                     latency_ms = (time.time() - sent_time) * 1000
#                     latencies.append(latency_ms)
#                     received.append(1)
#                     if on_progress:
#                         on_progress(len(received), message_count)
#                 except Exception:
#                     pass

#         pub_thread.join()
#         subscriber.stop()
#         publisher.stop()

#         total_time = time.time() - start_time
#         throughput = len(received) / total_time if total_time > 0 else 0

#         self.results = {
#             "message_count": message_count,
#             "message_size_bytes": message_size,
#             "sent": message_count,
#             "received": len(received),
#             "errors": errors,
#             "total_time_sec": round(total_time, 2),
#             "throughput_msg_per_sec": round(throughput, 2),
#             "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
#             "min_latency_ms": round(min(latencies), 2) if latencies else 0,
#             "max_latency_ms": round(max(latencies), 2) if latencies else 0,
#         }

#         return self.results



# Updated with new features

# import time
# import threading
# import random
# import string
# from solace.messaging.resources.topic import Topic
# from solace.messaging.resources.topic_subscription import TopicSubscription
# from solace.messaging.resources.queue import Queue


# def build_message(template: str, index: int, size: int) -> str:
#     if not template.strip():
#         return "X" * size
#     msg = template
#     msg = msg.replace("{{index}}", str(index))
#     msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
#     msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
#     return msg


# class PerfTester:

#     def __init__(self, service):
#         self.service = service
#         self.results = {}
#         self._stop = False

#     def stop(self):
#         self._stop = True

#     def run(
#         self,
#         target: str,
#         target_type: str,
#         message_count: int,
#         message_size: int,
#         message_template: str,
#         on_progress=None
#     ):
#         self._stop = False
#         latencies = []
#         received_count = [0]
#         errors = [0]
#         throughput_samples = []

#         # --- Build publisher (always direct for perf) ---
#         publisher = self.service.create_direct_message_publisher_builder().build()
#         publisher.start()

#         # --- Build receiver based on target type ---
#         if target_type == "topic":
#             receiver = self.service.create_direct_message_receiver_builder() \
#                 .with_subscriptions([TopicSubscription.of(target)]) \
#                 .build()
#             receiver.start()
#             is_persistent = False
#         else:
#             queue = Queue.durable_exclusive_queue(target)
#             receiver = self.service.create_persistent_message_receiver_builder() \
#                 .build(queue)
#             receiver.start()
#             is_persistent = True

#         start_time = time.time()
#         last_sample_time = start_time
#         last_sample_count = 0

#         # --- Publish in background thread ---
#         def publish_messages():
#             topic_obj = Topic.of(target)
#             for i in range(message_count):
#                 if self._stop:
#                     break
#                 try:
#                     payload = build_message(message_template, i, message_size)
#                     stamped = f"{time.time()}||{payload}"
#                     msg = self.service.message_builder().build(stamped)
#                     publisher.publish(msg, topic_obj)
#                 except Exception as e:
#                     errors[0] += 1

#         pub_thread = threading.Thread(target=publish_messages)
#         pub_thread.start()

#         # --- Receive loop ---
#         deadline = time.time() + 60
#         while received_count[0] < message_count and time.time() < deadline and not self._stop:
#             try:
#                 msg = receiver.receive_message(timeout=2000)
#                 if msg:
#                     raw = msg.get_payload_as_string() or ""
#                     if is_persistent:
#                         receiver.ack(msg)
#                     try:
#                         sent_time = float(raw.split("||")[0])
#                         latency_ms = (time.time() - sent_time) * 1000
#                         latencies.append(latency_ms)
#                     except Exception:
#                         pass
#                     received_count[0] += 1

#                     # Sample throughput every second
#                     now = time.time()
#                     if now - last_sample_time >= 1.0:
#                         sample_tps = (received_count[0] - last_sample_count) / (now - last_sample_time)
#                         throughput_samples.append(round(sample_tps, 1))
#                         last_sample_time = now
#                         last_sample_count = received_count[0]

#                     if on_progress:
#                         elapsed = time.time() - start_time
#                         tps = received_count[0] / elapsed if elapsed > 0 else 0
#                         on_progress(
#                             received_count[0],
#                             message_count,
#                             round(elapsed, 1),
#                             round(tps, 1)
#                         )
#             except Exception:
#                 pass

#         pub_thread.join()

#         # --- Cleanup ---
#         try:
#             publisher.terminate()
#         except Exception:
#             pass
#         try:
#             receiver.terminate()
#         except Exception:
#             pass

#         total_time = time.time() - start_time
#         sorted_lat = sorted(latencies)

#         self.results = {
#             "target": target,
#             "target_type": target_type,
#             "message_count": message_count,
#             "message_size_bytes": message_size,
#             "sent": message_count - errors[0],
#             "received": received_count[0],
#             "errors": errors[0],
#             "total_time_sec": round(total_time, 2),
#             "throughput_msg_per_sec": round(
#                 received_count[0] / total_time if total_time > 0 else 0, 2
#             ),
#             "avg_latency_ms": round(
#                 sum(latencies) / len(latencies), 2
#             ) if latencies else 0,
#             "min_latency_ms": round(min(latencies), 2) if latencies else 0,
#             "max_latency_ms": round(max(latencies), 2) if latencies else 0,
#             "p95_latency_ms": round(
#                 sorted_lat[int(len(sorted_lat) * 0.95)], 2
#             ) if sorted_lat else 0,
#             "p99_latency_ms": round(
#                 sorted_lat[int(len(sorted_lat) * 0.99)], 2
#             ) if sorted_lat else 0,
#             "throughput_samples": throughput_samples,
#         }

#         return self.results


# Updated new feature 21-06-2026

import time
import threading
import random
import string
from solace.messaging.resources.topic import Topic
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.resources.queue import Queue


def build_message(template: str, index: int, size: int) -> str:
    if not template.strip():
        return "X" * size
    msg = template
    msg = msg.replace("{{index}}", str(index))
    msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
    msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
    return msg


class PerfTester:

    def __init__(self, service):
        self.service = service
        self.results = {}
        self._stop = False

    def stop(self):
        self._stop = True

    def run(
        self,
        target: str,
        target_type: str,            # "topic" or "queue"
        message_count: int,
        message_size: int,
        message_template: str,
        delivery_mode: str = "direct",   # "direct" or "persistent"
        rate_limit: int = 0,             # msgs/sec, 0 = unlimited
        window_size: int = 50,           # only used for persistent mode
        on_progress=None
    ):
        self._stop = False
        latencies = []
        received_count = [0]
        errors = [0]
        throughput_samples = []

        # --- Build publisher based on delivery mode ---
        if delivery_mode == "persistent":
            try:
                from solace.messaging.config.solace_properties.publisher_properties import (
                    PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
                )
                pub_builder = self.service.create_persistent_message_publisher_builder()
                pub_builder = pub_builder.from_properties({
                    PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
                })
                publisher = pub_builder.build()
            except Exception:
                # Fallback if window size property import fails on this SDK version
                publisher = self.service.create_persistent_message_publisher_builder().build()
        else:
            publisher = self.service.create_direct_message_publisher_builder().build()

        publisher.start()

        # --- Build receiver based on target type ---
        if target_type == "topic":
            receiver = self.service.create_direct_message_receiver_builder() \
                .with_subscriptions([TopicSubscription.of(target)]) \
                .build()
            receiver.start()
            is_persistent_receiver = False
        else:
            queue = Queue.durable_exclusive_queue(target)
            receiver = self.service.create_persistent_message_receiver_builder() \
                .build(queue)
            receiver.start()
            is_persistent_receiver = True

        start_time = time.time()
        last_sample_time = start_time
        last_sample_count = 0

        # --- Publish in background thread, with optional rate limiting ---
        def publish_messages():
            topic_obj = Topic.of(target)
            delay = (1.0 / rate_limit) if rate_limit > 0 else 0
            for i in range(message_count):
                if self._stop:
                    break
                try:
                    payload = build_message(message_template, i, message_size)
                    stamped = f"{time.time()}||{payload}"
                    msg = self.service.message_builder().build(stamped)
                    publisher.publish(msg, topic_obj)
                except Exception:
                    errors[0] += 1
                if delay > 0:
                    time.sleep(delay)

        pub_thread = threading.Thread(target=publish_messages)
        pub_thread.start()

        # --- Receive loop ---
        deadline = time.time() + 90
        while received_count[0] < message_count and time.time() < deadline and not self._stop:
            try:
                msg = receiver.receive_message(timeout=2000)
                if msg:
                    raw = msg.get_payload_as_string() or ""
                    if is_persistent_receiver:
                        receiver.ack(msg)
                    try:
                        sent_time = float(raw.split("||")[0])
                        latency_ms = (time.time() - sent_time) * 1000
                        latencies.append(latency_ms)
                    except Exception:
                        pass
                    received_count[0] += 1

                    now = time.time()
                    if now - last_sample_time >= 1.0:
                        sample_tps = (received_count[0] - last_sample_count) / (now - last_sample_time)
                        throughput_samples.append(round(sample_tps, 1))
                        last_sample_time = now
                        last_sample_count = received_count[0]

                    if on_progress:
                        elapsed = time.time() - start_time
                        tps = received_count[0] / elapsed if elapsed > 0 else 0
                        on_progress(
                            received_count[0], message_count,
                            round(elapsed, 1), round(tps, 1)
                        )
            except Exception:
                pass

        pub_thread.join()

        try:
            publisher.terminate()
        except Exception:
            pass
        try:
            receiver.terminate()
        except Exception:
            pass

        total_time = time.time() - start_time
        sorted_lat = sorted(latencies)

        self.results = {
            "target": target,
            "target_type": target_type,
            "delivery_mode": delivery_mode,
            "rate_limit": rate_limit,
            "window_size": window_size if delivery_mode == "persistent" else None,
            "message_count": message_count,
            "message_size_bytes": message_size,
            "sent": message_count - errors[0],
            "received": received_count[0],
            "errors": errors[0],
            "total_time_sec": round(total_time, 2),
            "throughput_msg_per_sec": round(
                received_count[0] / total_time if total_time > 0 else 0, 2
            ),
            "avg_latency_ms": round(
                sum(latencies) / len(latencies), 2
            ) if latencies else 0,
            "min_latency_ms": round(min(latencies), 2) if latencies else 0,
            "max_latency_ms": round(max(latencies), 2) if latencies else 0,
            "p95_latency_ms": round(
                sorted_lat[int(len(sorted_lat) * 0.95)], 2
            ) if sorted_lat else 0,
            "p99_latency_ms": round(
                sorted_lat[int(len(sorted_lat) * 0.99)], 2
            ) if sorted_lat else 0,
            "throughput_samples": throughput_samples,
        }

        return self.results