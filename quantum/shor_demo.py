from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class RsaPublicKey:
    n: int
    e: int


@dataclass(frozen=True)
class RsaPrivateKey:
    n: int
    d: int


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def _mod_inverse(a: int, m: int) -> int:
    """Return x such that (a * x) % m == 1 using extended Euclid."""
    t, new_t = 0, 1
    r, new_r = m, a
    while new_r != 0:
        q = r // new_r
        t, new_t = new_t, t - q * new_t
        r, new_r = new_r, r - q * new_r
    if r > 1:
        raise ValueError("inverse does not exist")
    if t < 0:
        t += m
    return t


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    limit = int(math.isqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True


def _multiplicative_order(a: int, n: int) -> int | None:
    """Classical order-finding used to simulate Shor's quantum subroutine."""
    if _gcd(a, n) != 1:
        return None
    r = 1
    value = a % n
    while value != 1:
        value = (value * a) % n
        r += 1
        if r > n:
            return None
    return r


def shor_factor_simulated(n: int, *, max_attempts: int = 32, seed: int = 42) -> tuple[int, int]:
    """Factor n using a classical simulation of Shor's period-finding flow."""
    if n <= 1:
        raise ValueError("n must be greater than 1")
    if n % 2 == 0:
        return 2, n // 2
    if _is_prime(n):
        raise ValueError("n must be composite for Shor factoring demo")

    rng = random.Random(seed)

    for _ in range(max_attempts):
        a = rng.randrange(2, n - 1)

        g = _gcd(a, n)
        if 1 < g < n:
            return g, n // g

        r = _multiplicative_order(a, n)
        if r is None or r % 2 != 0:
            continue

        x = pow(a, r // 2, n)
        if x in (1, n - 1):
            continue

        p = _gcd(x - 1, n)
        q = _gcd(x + 1, n)
        if p * q == n and p not in (1, n) and q not in (1, n):
            return min(p, q), max(p, q)

    raise RuntimeError("failed to factor n within max_attempts")


def _build_demo_rsa_keys() -> tuple[RsaPublicKey, RsaPrivateKey]:
    """Build a tiny RSA keypair suitable for demonstration."""
    p, q = 61, 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    d = _mod_inverse(e, phi)
    return RsaPublicKey(n=n, e=e), RsaPrivateKey(n=n, d=d)


def _rsa_encrypt(message: int, public_key: RsaPublicKey) -> int:
    if message < 0 or message >= public_key.n:
        raise ValueError("message must satisfy 0 <= message < n")
    return pow(message, public_key.e, public_key.n)


def _rsa_decrypt(ciphertext: int, private_key: RsaPrivateKey) -> int:
    return pow(ciphertext, private_key.d, private_key.n)


def run_shor_demo() -> None:
    """Simulate Shor's RSA break: factor n, recover d, and decrypt ciphertext."""
    print("Quantum Vulnerability Demo: Simulated Shor Algorithm on RSA")
    print("-" * 64)

    public_key, private_key = _build_demo_rsa_keys()
    pin_as_number = 1234
    ciphertext = _rsa_encrypt(pin_as_number, public_key)

    print(f"Public key (n, e): ({public_key.n}, {public_key.e})")
    print(f"Captured ciphertext (encrypted PIN): {ciphertext}")

    p, q = shor_factor_simulated(public_key.n)
    phi = (p - 1) * (q - 1)
    recovered_d = _mod_inverse(public_key.e, phi)
    recovered_private_key = RsaPrivateKey(n=public_key.n, d=recovered_d)
    recovered_plaintext = _rsa_decrypt(ciphertext, recovered_private_key)

    print(f"Recovered factors with simulated Shor: p={p}, q={q}")
    print(f"Recovered private exponent d: {recovered_d}")
    print(f"Recovered plaintext PIN: {recovered_plaintext}")
    print(f"Ground-truth private exponent d: {private_key.d}")
    print(f"Break successful: {recovered_plaintext == pin_as_number}")


if __name__ == "__main__":
    run_shor_demo()
