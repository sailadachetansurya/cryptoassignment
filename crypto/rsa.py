from __future__ import annotations

RSA_DEMO_PUBLIC_N = 3233
RSA_DEMO_PUBLIC_E = 17
RSA_DEMO_PRIVATE_D = 2753
#prime factors are 53 and 61

def rsa_decrypt_text(
    encrypted_values: list[int],
    private_d: int = RSA_DEMO_PRIVATE_D,
    public_n: int = RSA_DEMO_PUBLIC_N,
) -> str:
    """Decrypt toy RSA encrypted code points into text."""
    chars: list[str] = []
    for value in encrypted_values:
        if not isinstance(value, int):
            raise ValueError("encrypted_payload must contain integers")
        decrypted_code = pow(value, private_d, public_n)
        chars.append(chr(decrypted_code))
    return "".join(chars)
