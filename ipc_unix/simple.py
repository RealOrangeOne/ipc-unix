import os
import socket
import socketserver
import threading

import ujson
from ipc_unix.utils import NEW_LINE, read_payload


class Client:
    def __init__(self, socket_path):
        self.socket_path = socket_path

    def send(self, data: dict):
        with socket.socket(socket.AF_UNIX, type=socket.SOCK_STREAM) as sock:
            sock.connect(self.socket_path)
            sock.sendall(ujson.dumps(data).encode() + NEW_LINE)
            return read_payload(sock)[0]


class RequestHandler(socketserver.BaseRequestHandler):
    def handle_request(self, request: dict):
        raise NotImplementedError("Failed to override `handle_request`")

    def handle(self):
        data = read_payload(self.request)[0]
        response = self.handle_request(data)
        self.request.sendall(ujson.dumps(response).encode())


class Server:
    def __init__(self, socket_path):
        class InstanceRequestHandler(RequestHandler):
            handle_request = self.handle_request

        self.socket_path = socket_path
        self.server = socketserver.ThreadingUnixStreamServer(
            self.socket_path, InstanceRequestHandler
        )

    def serve_forever(self):
        self.server.serve_forever()

    def serve_in_thread(self):
        thread = threading.Thread(target=self.serve_forever)
        thread.start()
        return thread

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        os.remove(self.socket_path)

    def handle_request(self, request: dict):
        raise NotImplementedError("Must override `handle_request`")
