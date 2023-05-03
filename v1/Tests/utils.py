import os
import json
import time
import socket
import pathlib

TIMEOUT = 10

class PathJSONEncoder(json.JSONEncoder):
    """
    Extended the Python JSON encoder to encode Pathlib objects.

    Docs: https://docs.python.org/3/library/json.html

    Usage:
    >>> json.dumps({
            "executable": TESTDATA_DIR/"exec/wc_map.sh",
        }, cls=PathJSONEncoder)
    """

    # Avoid pylint false positive.  There's a style problem in the JSON library
    # that we're inheriting from.
    # https://github.com/PyCQA/pylint/issues/414#issuecomment-212158760
    # pylint: disable=E0202

    def default(self, o):
        """Override base class method to include Path object serialization."""
        if isinstance(o, pathlib.Path):
            return str(o)
        return super().default(o)
    

def send_message(message, port):
    """Send JSON-encoded TCP message."""
    host = "localhost"
    message_str = json.dumps(message, cls=PathJSONEncoder)
    message_bytes = str.encode(message_str)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(message_bytes)

def wait_for_exists(*paths):
    """Return when paths exist."""
    for _ in range(TIMEOUT):
        if all(os.path.exists(p) for p in paths):
            return
        time.sleep(1)
    raise Exception(f"Failed to create paths: {paths}")