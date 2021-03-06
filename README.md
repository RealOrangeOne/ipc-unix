# IPC-Unix

[![CircleCI](https://circleci.com/gh/RealOrangeOne/ipc-unix.svg?style=svg)](https://circleci.com/gh/RealOrangeOne/ipc-unix)
[![Build Status](https://travis-ci.com/RealOrangeOne/ipc-unix.svg?branch=master)](https://travis-ci.com/RealOrangeOne/ipc-unix)

Simple Inter-Process Communication using unix sockets for Python.

__Note__: Whilst mostly working, there's still some fairly common cases which haven't been tested. Use at your own risk until this message is removed.

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

server.close()s
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
