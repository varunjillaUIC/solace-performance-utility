from solace.messaging.resources.topic import Topic


class TopicPublisher:

    def __init__(self, service):
        self.service = service
        self.publisher = service.create_direct_message_publisher_builder().build()
        self.publisher.start()

    def publish(self, topic: str, message: str):
        topic_obj = Topic.of(topic)
        outbound_msg = self.service.message_builder().build(message)
        self.publisher.publish(outbound_msg, topic_obj)

    def stop(self):
        self.publisher.terminate()