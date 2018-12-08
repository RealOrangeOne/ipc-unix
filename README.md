# IPC-Unix

[![CircleCI](https://circleci.com/gh/RealOrangeOne/ipc-unix.svg?style=svg)](https://circleci.com/gh/RealOrangeOne/ipc-unix)

Simple Inter-Process Communication using unix sockets for Python.

## Examples

For some more concrete examples, check out the `tests/` directory.

### Call / Response

```python
from ipc_unix import Server, Client

class EchoServer(Server):
    def handle_request(self, request):
        return request

socket_path = '/tmp/sock.sock'
server = EchoServer(socket_path)
client = Client(socket_path)

print(client.send({"foo": "bar"}))
>>> {"foo": "bar"}

```

### Pub-Sub

```python
from ipc_unix import pubsub

socket_path = '/tmp/sock.sock'
publisher = pubsub.Publisher(socket_path)
subscriber = pubsub.Subscriber(socket_path)

publisher.write({"foo": "bar"})
print(self.subscriber.get_latest_message())
>>> {"foo": "bar"}

publisher.close()
subscriber.close()

```
