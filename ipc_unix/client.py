import socket

import ujson
from ipc_unix.utils import read_payload


def send_to(socket_path, data):
    with socket.socket(socket.AF_UNIX, type=socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)
        sock.sendall(ujson.dumps(data).encode() + b"\n")
        return read_payload(sock)
