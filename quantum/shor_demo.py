from __future__ import annotations

import argparse
import json
import math
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNOOP_LOG_FILE = PROJECT_ROOT / "snoop_packet.log"
DECRYPTED_LOG_FILE = PROJECT_ROOT / "decrypted_snoop_packets.log"


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


def shor_factor_simulated(n: int, *, max_attempts: int = 64, seed: int = 42) -> tuple[int, int]:
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
    """Build the tiny RSA keypair used in the project simulation."""
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


def _decrypt_text_from_values(encrypted_values: list[int], n: int, d: int) -> str:
    chars: list[str] = []
    for value in encrypted_values:
        if not isinstance(value, int):
            raise ValueError("encrypted payload contains non-integer value")
        codepoint = pow(value, d, n)
        chars.append(chr(codepoint))
    return "".join(chars)


def _safe_json_loads(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _read_last_log_entry(logfile: Path) -> dict[str, Any]:
    if not logfile.exists():
        raise FileNotFoundError(f"log file not found: {logfile}")
    if logfile.stat().st_size == 0:
        raise ValueError("log file is empty")

    with logfile.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError("log file has no JSON entries")

    try:
        entry = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise ValueError("last log line is not valid JSON") from exc

    if not isinstance(entry, dict):
        raise ValueError("last log line must be a JSON object")

    return entry


def _extract_payload(entry: dict[str, Any]) -> tuple[list[int], int, int, dict[str, Any]]:
    encrypted_payload = entry.get("encrypted_payload")
    if encrypted_payload is None:
        encrypted_payload = entry.get("ciphertext")
    n = entry.get("n")
    e = entry.get("e")
    meta = entry.get("meta", {})

    if not isinstance(encrypted_payload, list) or not encrypted_payload:
        raise ValueError("entry.encrypted_payload/ciphertext must be a non-empty list")
    if not all(isinstance(v, int) for v in encrypted_payload):
        raise ValueError("entry.encrypted_payload/ciphertext must contain only integers")
    if not isinstance(n, int) or not isinstance(e, int):
        raise ValueError("entry must include integer n and e")
    if not isinstance(meta, dict):
        meta = {}

    return encrypted_payload, n, e, meta


def attack_logged_packet(entry: dict[str, Any]) -> dict[str, Any]:
    encrypted_payload, n, e, meta = _extract_payload(entry)

    p, q = shor_factor_simulated(n)
    phi = (p - 1) * (q - 1)
    d = _mod_inverse(e, phi)

    plaintext = _decrypt_text_from_values(encrypted_payload, n=n, d=d)
    parsed = _safe_json_loads(plaintext)

    recovered = {
        "meta": meta,
        "n": n,
        "e": e,
        "p": p,
        "q": q,
        "d": d,
        "plaintext_raw": plaintext,
        "plaintext_json": parsed,
    }
    return recovered


def replay_last_logged_attack() -> None:
    log_path = SNOOP_LOG_FILE
    entry = _read_last_log_entry(log_path)
    recovered = attack_logged_packet(entry)

    print("Live Quantum Attacker Demo (single-shot)")
    print("-" * 64)
    print(f"Source log file: {log_path}")
    print(f"Recovered factors: p={recovered['p']}, q={recovered['q']}")
    print(f"Recovered private exponent d: {recovered['d']}")
    print(f"Meta: {json.dumps(recovered['meta'], ensure_ascii=False)}")

    payload_json = recovered["plaintext_json"]
    if isinstance(payload_json, dict):
        print("Recovered JSON payload:")
        print(json.dumps(payload_json, indent=2, ensure_ascii=False))
        if "pin" in payload_json:
            print(f"Recovered PIN: {payload_json['pin']}")
    else:
        print("Recovered plaintext payload (non-JSON):")
        print(recovered["plaintext_raw"])


def live_attack_follow(
    interval_seconds: float = 1.0,
) -> None:
    log_path = SNOOP_LOG_FILE
    output_path = DECRYPTED_LOG_FILE
    print("Live Quantum Attacker Demo (follow mode)")
    print("-" * 64)
    print(f"Watching: {log_path}")
    print(f"Decrypted output log: {output_path}")
    print("Press Ctrl+C to stop.\n")

    last_seen_line = ""
    try:
        while True:
            try:
                if not log_path.exists() or log_path.stat().st_size == 0:
                    time.sleep(interval_seconds)
                    continue

                with log_path.open("r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    time.sleep(interval_seconds)
                    continue

                latest = lines[-1]
                if latest == last_seen_line:
                    time.sleep(interval_seconds)
                    continue

                last_seen_line = latest
                try:
                    entry = json.loads(latest)
                    recovered = attack_logged_packet(entry)
                except Exception as exc:
                    print(f"[attacker] new packet seen, but attack failed: {exc}")
                    time.sleep(interval_seconds)
                    continue

                print("=" * 64)
                print("[attacker] intercepted packet decrypted")
                print(f"meta: {json.dumps(recovered['meta'], ensure_ascii=False)}")
                print(f"factors: p={recovered['p']} q={recovered['q']}, d={recovered['d']}")
                payload_json = recovered["plaintext_json"]
                if isinstance(payload_json, dict):
                    print(json.dumps(payload_json, indent=2, ensure_ascii=False))
                    if "pin" in payload_json:
                        print(f"[attacker] RECOVERED PIN => {payload_json['pin']}")
                else:
                    print(recovered["plaintext_raw"])
                print("=" * 64)

                decrypted_entry = {
                    "decrypted_at": datetime.now(timezone.utc).isoformat(),
                    "source_entry": entry,
                    "recovered": recovered,
                }
                with output_path.open("a", encoding="utf-8") as outf:
                    outf.write(json.dumps(decrypted_entry, ensure_ascii=False) + "\n")

            except Exception as exc:
                print(f"[attacker] monitor error: {exc}")

            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopped live attacker.")


def run_shor_demo() -> None:
    """Original standalone simulation: factor n, recover d, decrypt toy ciphertext."""
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


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulated Shor demo with optional live logfile attack mode."
    )
    parser.add_argument(
        "--live-attack",
        action="store_true",
        help="Read the latest intercepted packet from logfile and attack once.",
    )
    parser.add_argument(
        "--follow",
        action="store_true",
        help="Continuously watch logfile and attack each new packet.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Polling interval seconds for --follow mode (default: 1.0).",
    )

    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    if args.follow:
        live_attack_follow(
            interval_seconds=max(args.interval, 0.1),
        )
        return

    if args.live_attack:
        replay_last_logged_attack()
        return

    run_shor_demo()


if __name__ == "__main__":
    main()