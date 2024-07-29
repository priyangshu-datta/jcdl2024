import hashlib
from io import BufferedReader


def chcksum(buffer: str|BufferedReader):
    if isinstance(buffer, str):
        buffer = buffer.encode("utf-8")
    if isinstance(buffer, BufferedReader):
        buffer = buffer.read()
    return hashlib.sha256(buffer).hexdigest()
