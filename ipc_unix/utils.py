import ujson


def read_payload(payload):
    data = b""
    while b"\n" not in data:
        message = payload.recv(4096)
        if message == b"":
            break
        data += message
    return ujson.loads(data)