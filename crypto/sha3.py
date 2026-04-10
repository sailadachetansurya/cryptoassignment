import hashlib


def sha3_hex(data: str) -> str:
    """Return SHA3-256 hex digest for input string."""
    return hashlib.sha3_256(data.encode("utf-8")).hexdigest()
