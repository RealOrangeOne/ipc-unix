import select
import socket

import ujson
from ipc_unix.utils import read_payload


class Subscriber:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.socket = socket.socket(
            socket.AF_UNIX, type=socket.SOCK_STREAM | socket.SOCK_NONBLOCK
        )
        self.socket.connect(self.socket_path)

    def listen(self):
        while True:
            yield self.get_message()

    def get_message(self):
        return read_payload(self.socket)

    def close(self):
        self.socket.close()


class Publisher:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.master_socket = socket.socket(
            socket.AF_UNIX, type=socket.SOCK_STREAM | socket.SOCK_NONBLOCK
        )
        self.master_socket.bind(self.socket_path)
        self.master_socket.listen()
        self.connections = []

    def close(self):
        self.master_socket.close()
        self.connections.clear()

    def accept_new_connection(self):
        readable, _, _ = select.select([self.master_socket], [], [], 1)

        if self.master_socket in readable:
            new_socket, _ = self.master_socket.accept()
            self.connections.append(new_socket)

    def write(self, message):
        self.accept_new_connection()

        _, writable, errorable = select.select([], self.connections, [], 1)

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
