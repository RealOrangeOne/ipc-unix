from functools import partial
from unittest import TestCase

from ipc_unix import client
from tests import EchoServer, get_random_path


class BasicServerTestCase(TestCase):
    def setUp(self):
        self.socket_path = get_random_path()
        self.server = EchoServer(self.socket_path)
        self.server.serve_in_thread()
        self.send_to_client = partial(client.send_to, self.socket_path)

    def tearDown(self):
        self.server.shutdown()

    def test_sending_dict(self):
        data = {"foo": "bar"}
        response = self.send_to_client(data)
        self.assertEqual(response, data)

    def test_sending_array(self):
        data = ["foo", "bar"]
        response = self.send_to_client(data)
        self.assertEqual(response, data)

    def test_sending_full_buffer(self):
        data = ["foo"] * 4096  # Pad out the buffer
        response = self.send_to_client(data)
        self.assertEqual(response, data)

    def test_sending_empty_payload(self):
        response = self.send_to_client("")
        self.assertEqual(response, "")

    def test_multiple_send_to_same_server(self):
        data = {"foo": "bar"}
        for _ in range(10):
            response = self.send_to_client(data)
            self.assertEqual(response, data)
