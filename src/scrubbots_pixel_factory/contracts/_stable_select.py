"""Small M01-only deterministic selection helpers.

This is deliberately not the general M02 RNG abstraction. It derives stable
values from SHA-256 domain-separated inputs and never uses module-global
randomness or Python hash iteration.
"""

from hashlib import sha256


def validate_seed(seed: int | str) -> int | str:
    if isinstance(seed, bool) or not isinstance(seed, (int, str)):
        raise TypeError("M01 selection seeds must be an int or string")
    return seed


def stable_digest(domain: str, seed: int | str, item: str = "") -> bytes:
    validate_seed(seed)
    payload = f"scrubbots-m01\0{domain}\0{type(seed).__name__}:{seed}\0{item}".encode(
        "utf-8"
    )
    return sha256(payload).digest()


def stable_index(domain: str, seed: int | str, size: int) -> int:
    if size <= 0:
        raise ValueError("selection size must be positive")
    return int.from_bytes(stable_digest(domain, seed), "big") % size
