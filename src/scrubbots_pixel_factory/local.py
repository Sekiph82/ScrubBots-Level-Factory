"""Small dependency-free local helpers used by the M00 smoke tests."""

import hashlib


def deterministic_digest(value: str | bytes) -> str:
    """Return a stable SHA-256 digest without randomness or I/O."""

    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()
