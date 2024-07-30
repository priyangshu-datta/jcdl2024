import hashlib
from io import BufferedReader


def chcksum(buffer: str | BufferedReader):
    if isinstance(buffer, str):
        return hashlib.sha256(buffer.encode("utf-8")).hexdigest()
    if isinstance(buffer, BufferedReader):
        return hashlib.sha256(buffer.read()).hexdigest()
