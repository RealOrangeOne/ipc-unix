import select

import ujson

BUFFER_SIZE = 4096
DEFAULT_SOCKET_READ_TIMEOUT = 0.01
NEW_LINE = b"\n"


def socket_has_data(sock, timeout=DEFAULT_SOCKET_READ_TIMEOUT) -> bool:
    readable, _, _ = select.select([sock], [], [], timeout)
    return sock in readable


def read_payload(payload):
    data = b""
    while NEW_LINE not in data:
        if not socket_has_data(payload):
            break
        message = payload.recv(BUFFER_SIZE)
        if message == b"":
            break
        data += message
    return [ujson.loads(row) for row in data.split(NEW_LINE) if row]
