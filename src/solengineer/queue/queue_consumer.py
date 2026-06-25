from solace.messaging.resources.queue import Queue
import logging

logging.getLogger("solace.messaging.receiver").setLevel(logging.ERROR)


class QueueConsumer:

    def __init__(self, service):
        self.service = service
        self.receiver = None

    def start(self, queue_name: str):
        queue = Queue.durable_exclusive_queue(queue_name)
        self.receiver = self.service.create_persistent_message_receiver_builder() \
            .build(queue)
        self.receiver.start()

    def receive(self, timeout: int = 3000):
        if self.receiver:
            return self.receiver.receive_message(timeout=timeout)
        return None

    def ack(self, msg):
        if self.receiver:
            self.receiver.ack(msg)

    def stop(self):
        if self.receiver:
            self.receiver.terminate()
            self.receiver = None