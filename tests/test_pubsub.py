from unittest import TestCase

from ipc_unix import pubsub
from tests import get_temp_file_path


class PubSubTestCase(TestCase):
    def setUp(self):
        self.socket_path = get_temp_file_path()
        self.publisher = pubsub.Publisher(self.socket_path)
        self.subscriber = pubsub.Subscriber(self.socket_path)

    def tearDown(self):
        self.publisher.close()
        self.subscriber.close()

    def test_transmits(self):
        self.publisher.write({"foo": "bar"})
        response = self.subscriber.get_latest_message()
        self.assertEqual(response, {"foo": "bar"})

    def test_no_messages(self):
        self.assertIsNone(self.subscriber.get_latest_message())
        self.assertFalse(self.subscriber.has_data)

    def test_buffers_messages(self):
        for i in range(5):
            self.publisher.write({"data": i})
        all_messages = self.subscriber.flush_data()
        message_ids = [message["data"] for message in all_messages]
        self.assertEqual(message_ids, [0, 1, 2, 3, 4])

    def test_get_latest_message(self):
        for i in range(5):
            self.publisher.write({"data": i})
        latest_message = self.subscriber.get_latest_message()
        self.assertEqual(latest_message, {"data": 4})
        self.assertIsNone(self.subscriber.get_latest_message())

    def test_multiple_subscribers(self):
        subscriber_2 = pubsub.Subscriber(self.socket_path)
        self.publisher.write({"foo": "bar"})
        self.assertEqual(self.subscriber.get_latest_message(), {"foo": "bar"})
        self.assertEqual(subscriber_2.get_latest_message(), {"foo": "bar"})
        subscriber_2.close()
