from ipc_unix import server
import tempfile
import os


class EchoServer(server.Server):
    def handle_request(self, request):
        return request


def get_random_path() -> str:
    _, temp_file_path = tempfile.mkstemp()
    os.remove(temp_file_path)
    return temp_file_path