def encrypt_fid(fid: str, key: bytes) -> str:
    """TODO: replace with real ASCON encryption."""
    _ = key
    return f"enc::{fid}"


def decrypt_fid(ciphertext: str, key: bytes) -> str:
    """TODO: replace with real ASCON decryption."""
    _ = key
    if ciphertext.startswith("enc::"):
        return ciphertext.split("enc::", 1)[1]
    return ""
