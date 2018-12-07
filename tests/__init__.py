from ipc_unix.simple import Server
import tempfile
import os


class EchoServer(Server):
    def handle_request(self, request):
        return request


def get_temp_file_path() -> str:
    _, temp_file_path = tempfile.mkstemp()
    os.remove(temp_file_path)
    return temp_file_path
