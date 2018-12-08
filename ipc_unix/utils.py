import select

import ujson

BUFFER_SIZE = 4096
DEFAULT_SOCKET_TIMEOUT = 0.1


def socket_has_data(sock, timeout=DEFAULT_SOCKET_TIMEOUT) -> bool:
    readable, _, _ = select.select([sock], [], [], timeout)
    return sock in readable


def read_payload(payload):
    data = b""
    while b"\n" not in data:
        if not socket_has_data(payload):
            break
        message = payload.recv(BUFFER_SIZE)
        if message == b"":
            break
        data += message
    parsed_data = []
    for row in data.split(b"\n"):
        if not row.strip():
            continue
        parsed_data.append(ujson.loads(row))
    return parsed_data
