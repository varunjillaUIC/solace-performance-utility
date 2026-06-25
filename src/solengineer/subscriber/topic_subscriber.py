from solace.messaging.resources.topic_subscription import TopicSubscription
import logging

logging.getLogger("solace.messaging.receiver").setLevel(logging.ERROR)


class TopicSubscriber:

    def __init__(self, service):
        self.service = service
        self.receiver = None

    def start(self, topic: str):
        self.receiver = self.service.create_direct_message_receiver_builder() \
            .with_subscriptions([TopicSubscription.of(topic)]) \
            .build()
        self.receiver.start()

    def receive(self, timeout: int = 3000):
        if self.receiver:
            return self.receiver.receive_message(timeout=timeout)
        return None

    def stop(self):
        if self.receiver:
            self.receiver.terminate()
            self.receiver = None