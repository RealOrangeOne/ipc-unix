import os
import select
import socket
import threading

import ujson
from ipc_unix.utils import (
    DEFAULT_SOCKET_READ_TIMEOUT,
    NEW_LINE,
    read_payload,
    socket_has_data,
)


class Subscriber:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.socket = socket.socket(
            socket.AF_UNIX, type=socket.SOCK_STREAM | socket.SOCK_NONBLOCK
        )
        self.socket.connect(self.socket_path)

    @property
    def has_data(self):
        return socket_has_data(self.socket)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

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
        self.master_socket = socket.socket(
            socket.AF_UNIX, type=socket.SOCK_STREAM | socket.SOCK_NONBLOCK
        )
        self.master_socket.bind(self.socket_path)
        self.master_socket.listen()
        self.connections = []
        self.accepting_new_connections = threading.Event()
        self.accepting_new_connections.set()
        self.new_connections_thread = threading.Thread(
            target=self._accept_new_connections
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        self.accepting_new_connections.set()
        self.new_connections_thread.start()

    def close(self):
        self.accepting_new_connections.clear()
        if self.new_connections_thread.is_alive():
            self.new_connections_thread.join()
        self.master_socket.close()
        for connection in self.connections:
            connection.close()
        self.connections.clear()
        os.remove(self.socket_path)

    def accept_outstanding_connections(self):
        if self.new_connections_thread.is_alive():
            raise Exception(
                "Cannot accept connections manually whilst thread is running"
            )
        while socket_has_data(self.master_socket):
            new_socket, _ = self.master_socket.accept()
            self.connections.append(new_socket)

    def _accept_new_connections(self):
        while self.accepting_new_connections.is_set():
            if socket_has_data(self.master_socket):
                new_socket, _ = self.master_socket.accept()
                self.connections.append(new_socket)

    def write(self, message: dict):
        _, writable, errorable = select.select(
            [],
            self.connections,
            [],
            DEFAULT_SOCKET_READ_TIMEOUT * len(self.connections),
        )

        dead_sockets = []

        if writable:
            data = ujson.dumps(message).encode() + NEW_LINE
            for sock in writable:
                try:
                    sock.send(data)
                except BrokenPipeError:
                    dead_sockets.append(sock)

        for sock in dead_sockets:
            if sock in self.connections:
                self.connections.remove(sock)
            sock.close()
