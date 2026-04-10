from __future__ import annotations

import hashlib
import hmac


_HEX_DIGITS = 16


def sha3_bytes(data: str) -> bytes:
    """Return the raw SHA3-256 digest for an input string."""
    return hashlib.sha3_256(data.encode("utf-8")).digest()


def sha3_hex(data: str) -> str:
    """Return the full SHA3-256 hexadecimal digest for an input string."""
    return sha3_bytes(data).hex()


def sha3_short_hex(data: str, length: int = _HEX_DIGITS) -> str:
    """Return a truncated hexadecimal digest, suitable for short IDs."""
    if length <= 0:
        raise ValueError("length must be positive")
    return sha3_hex(data)[:length]


def verify_sha3(data: str, expected_hex: str) -> bool:
    """Verify that an input string matches the expected SHA3-256 hex digest."""
    return hmac.compare_digest(sha3_hex(data), expected_hex.lower())


def derive_uid(mobile: str, pin: str) -> str:
    """Derive a deterministic short UID from user registration inputs."""
    return sha3_short_hex(f"user:{mobile}:{pin}")


def derive_fid(name: str, zone_code: str, password: str, created_at: str) -> str:
    """Derive a deterministic short FID from franchise registration inputs."""
    return sha3_short_hex(f"franchise:{name}:{zone_code}:{password}:{created_at}")


def derive_vmid(uid: str, mobile: str) -> str:
    """Derive a deterministic VMID from UID and mobile number."""
    return sha3_short_hex(f"vmid:{uid}:{mobile}")


def derive_transaction_id(uid: str, fid: str, timestamp: str, amount: str) -> str:
    """Derive a transaction ID from the primary transaction fields."""
    return sha3_hex(f"txn:{uid}:{fid}:{timestamp}:{amount}")


# Backward-compatible aliases for existing imports.
sha256_bytes = sha3_bytes
sha256_hex = sha3_hex
sha256_short_hex = sha3_short_hex
verify_sha256 = verify_sha3
