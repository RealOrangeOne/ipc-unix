from unittest import TestCase

from ipc_unix import pubsub
from tests import get_temp_file_path


class PubSubTestCase(TestCase):
    def setUp(self):
        self.socket_path = get_temp_file_path()
        self.publisher = pubsub.Publisher(self.socket_path)
        self.subscriber = pubsub.Subscriber(self.socket_path)
        self.publisher.accept_outstanding_connections()

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
        self.publisher.accept_outstanding_connections()
        self.publisher.write({"foo": "bar"})
        self.assertEqual(self.subscriber.get_latest_message(), {"foo": "bar"})
        self.assertEqual(subscriber_2.get_latest_message(), {"foo": "bar"})

    def test_lots_of_subscribers(self):
        subscribers = []
        for i in range(100):
            subscribers.append(pubsub.Subscriber(self.socket_path))
        self.publisher.accept_outstanding_connections()
        self.publisher.write({"foo": "bar"})
        for subscriber in subscribers:
            self.assertEqual(subscriber.get_latest_message(), {"foo": "bar"})
            subscriber.close()

    def test_no_subscribers(self):
        self.subscriber.close()
        self.publisher.write({"foo": "bar"})

    def test_cant_accept_connections_with_thread_running(self):
        self.publisher.start()
        with self.assertRaises(Exception) as e:
            self.publisher.accept_outstanding_connections()
        self.assertIn(
            "Cannot accept connections manually whilst thread is running",
            str(e.exception),
        )

    def test_accepts_connections(self):
        self.assertEqual(len(self.publisher.connections), 1)
        pubsub.Subscriber(self.socket_path)
        self.assertEqual(len(self.publisher.connections), 1)
        self.publisher.accept_outstanding_connections()
        self.assertEqual(len(self.publisher.connections), 2)
