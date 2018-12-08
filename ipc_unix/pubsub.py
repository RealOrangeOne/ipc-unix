import select
import socket

import ujson
from ipc_unix.utils import DEFAULT_SOCKET_READ_TIMEOUT, read_payload, socket_has_data


class Subscriber:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.socket = socket.socket(socket.AF_UNIX, type=socket.SOCK_STREAM)
        self.socket.connect(self.socket_path)

    @property
    def has_data(self):
        return socket_has_data(self.socket)

    def listen(self):
        while True:
            yield from self.get_message()

    def get_messages(self) -> dict:
        return read_payload(self.socket)

    def flush_data(self):
        while self.has_data:
            yield from self.get_messages()

    def get_latest_message(self):
        data = list(self.flush_data())
        return data[-1] if data else None

    def close(self):
        self.socket.close()


class Publisher:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.master_socket = socket.socket(socket.AF_UNIX, type=socket.SOCK_STREAM)
        self.master_socket.bind(self.socket_path)
        self.master_socket.listen(1)
        self.connections = []

    def close(self):
        self.master_socket.close()
        self.connections.clear()

    def accept_new_connection(self):
        if socket_has_data(self.master_socket):
            new_socket, _ = self.master_socket.accept()
            self.connections.append(new_socket)

    def write(self, message: dict):
        self.accept_new_connection()

        _, writable, errorable = select.select(
            [], self.connections, [], DEFAULT_SOCKET_READ_TIMEOUT
        )

        dead_sockets = []

        if writable:
            data = ujson.dumps(message).encode() + b"\n"
            for sock in writable:
                try:
                    sock.send(data)
                except BrokenPipeError:
                    dead_sockets.append(sock)

        for sock in dead_sockets:
            if sock in self.connections:
                self.connections.remove(sock)
            sock.close()
