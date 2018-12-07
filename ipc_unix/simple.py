import socket
import socketserver
import threading

import ujson
from ipc_unix.utils import read_payload


def send_to(socket_path, data):
    with socket.socket(socket.AF_UNIX, type=socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)
        sock.sendall(ujson.dumps(data).encode() + b"\n")
        return read_payload(sock)


class RequestHandler(socketserver.BaseRequestHandler):
    def handle_request(self, request):
        raise NotImplementedError("Failed to override `handle_request`")

    def handle(self):
        data = read_payload(self.request)
        response = self.handle_request(data)
        self.request.sendall(ujson.dumps(response).encode())


class Server:
    def __init__(self, socket_path):
        class InstanceRequestHandler(RequestHandler):
            handle_request = self.handle_request

        self.server = socketserver.UnixStreamServer(socket_path, InstanceRequestHandler)

    def serve_forever(self):
        self.server.serve_forever()

    def serve_in_thread(self):
        thread = threading.Thread(target=self.serve_forever)
        thread.start()
        return thread

    def shutdown(self):
        self.server.shutdown()

    def close(self):
        self.shutdown()
        self.server.server_close()

    def handle_request(self, request):
        raise NotImplementedError("Must override `handle_request`")
