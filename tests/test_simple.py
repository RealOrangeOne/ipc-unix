from functools import partial
from unittest import TestCase

from ipc_unix.simple import send_to
from ipc_unix.utils import BUFFER_SIZE
from tests import EchoServer, get_temp_file_path


class SimpleServerTestCase(TestCase):
    def setUp(self):
        self.socket_path = get_temp_file_path()
        self.server = EchoServer(self.socket_path)
        self.server.serve_in_thread()
        self.send_to_client = partial(send_to, self.socket_path)

    def tearDown(self):
        self.server.close()

    def test_sending_dict(self):
        data = {"foo": "bar"}
        response = self.send_to_client(data)
        self.assertEqual(response, data)

    def test_sending_full_buffer(self):
        data = {"foo" + str(i): i for i in range(BUFFER_SIZE)}
        response = self.send_to_client(data)
        self.assertEqual(response, data)

    def test_multiple_send_to_same_server(self):
        data = {"foo": "bar"}
        for _ in range(10):
            response = self.send_to_client(data)
            self.assertEqual(response, data)
