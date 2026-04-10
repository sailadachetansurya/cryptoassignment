from __future__ import annotations

import base64
import hashlib
import secrets

import ascon


_PREFIX = "ascon1"
_NONCE_SIZE = 16
_KEY_SIZE = 16


def _normalize_key(key: bytes) -> bytes:
    """Normalize arbitrary key material to the ASCON-128 key size."""
    if len(key) == _KEY_SIZE:
        return key
    return hashlib.sha3_256(key).digest()[:_KEY_SIZE]


def encrypt_ascon(plaintext: str, key: bytes) -> str:
    """Encrypt plaintext with ASCON-128 and return a portable string payload."""
    normalized_key = _normalize_key(key)
    nonce = secrets.token_bytes(_NONCE_SIZE)
    ciphertext = ascon.encrypt(normalized_key, nonce, b"", plaintext.encode("utf-8"), variant="Ascon-128")
    payload = base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")
    return f"{_PREFIX}:{payload}"


def decrypt_ascon(ciphertext: str, key: bytes) -> str:
    """Decrypt a payload produced by encrypt_ascon."""
    if not ciphertext.startswith(f"{_PREFIX}:"):
        return ""

    encoded_payload = ciphertext.split(":", 1)[1]
    raw_payload = base64.urlsafe_b64decode(encoded_payload.encode("ascii"))
    if len(raw_payload) <= _NONCE_SIZE:
        return ""

    nonce = raw_payload[:_NONCE_SIZE]
    encrypted_body = raw_payload[_NONCE_SIZE:]
    normalized_key = _normalize_key(key)
    plaintext = ascon.decrypt(normalized_key, nonce, b"", encrypted_body, variant="Ascon-128")
    if plaintext is None:
        return ""
    return plaintext.decode("utf-8")


# Backward-compatible aliases for older code paths and typo-tolerant usage.
enccrypt = encrypt_ascon
encrypt_fid = encrypt_ascon
decrypt_fid = decrypt_ascon
