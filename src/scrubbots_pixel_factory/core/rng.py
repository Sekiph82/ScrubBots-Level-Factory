"""Project-owned deterministic RNG with domain-separated SHA-256 streams."""

from collections.abc import Sequence
import hashlib


RNG_ALGORITHM = "SCRUBBOTS_SHA256_COUNTER_V1"
STAGE_DOMAINS = (
    "dimension",
    "palette",
    "geometry",
    "colorization",
    "post_processing",
)


class RNGContractError(ValueError):
    """Raised when deterministic RNG inputs are invalid."""


def _typed_seed_bytes(seed: int | str) -> bytes:
    if isinstance(seed, bool) or not isinstance(seed, (int, str)):
        raise RNGContractError("seed must be an integer or string, excluding bool")
    if isinstance(seed, int):
        return f"int:{seed}".encode("utf-8")
    if not seed:
        raise RNGContractError("seed string must not be empty")
    return f"string:{len(seed)}:{seed}".encode("utf-8")


def _domain_bytes(domain: str) -> bytes:
    if type(domain) is not str or not domain:
        raise RNGContractError("RNG domain must be a non-empty string")
    return domain.encode("utf-8")


class DeterministicRNG:
    """A local counter stream; child and stage streams do not consume parents."""

    __slots__ = ("_root_material", "_key", "_counter", "domain")

    def __init__(self, seed: int | str, domain: str = "root") -> None:
        seed_bytes = _typed_seed_bytes(seed)
        domain_bytes = _domain_bytes(domain)
        root_material = b"scrubbots-rng-v1\0" + seed_bytes
        self._root_material = root_material
        self._key = hashlib.sha256(root_material + b"\0domain\0" + domain_bytes).digest()
        self._counter = 0
        self.domain = domain

    @classmethod
    def _from_material(cls, root_material: bytes, domain: str) -> "DeterministicRNG":
        stream = object.__new__(cls)
        stream._root_material = root_material
        stream._key = hashlib.sha256(root_material + b"\0domain\0" + _domain_bytes(domain)).digest()
        stream._counter = 0
        stream.domain = domain
        return stream

    def _next_block(self) -> bytes:
        counter = self._counter
        if counter >= 1 << 128:
            raise RNGContractError("RNG counter exhausted")
        self._counter += 1
        return hashlib.sha256(
            self._key + b"\0counter\0" + counter.to_bytes(16, "big")
        ).digest()

    def next_bytes(self, length: int = 32) -> bytes:
        if isinstance(length, bool) or not isinstance(length, int) or length < 0:
            raise RNGContractError("byte length must be a non-negative integer")
        output = bytearray()
        while len(output) < length:
            output.extend(self._next_block())
        return bytes(output[:length])

    def next_u64(self) -> int:
        return int.from_bytes(self._next_block()[:8], "big")

    def randbelow(self, bound: int) -> int:
        if isinstance(bound, bool) or not isinstance(bound, int) or bound <= 0:
            raise RNGContractError("randbelow bound must be a positive integer")
        bits = (bound - 1).bit_length()
        byte_count = max(1, (bits + 7) // 8)
        mask = (1 << bits) - 1
        while True:
            candidate = int.from_bytes(self.next_bytes(byte_count), "big") & mask
            if candidate < bound:
                return candidate

    def choice(self, values: Sequence[object]) -> object:
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)) or not values:
            raise RNGContractError("choice requires a non-empty ordered sequence")
        return values[self.randbelow(len(values))]

    def shuffle(self, values: Sequence[object]) -> list[object]:
        if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
            raise RNGContractError("shuffle requires an ordered sequence")
        output = list(values)
        for index in range(len(output) - 1, 0, -1):
            swap = self.randbelow(index + 1)
            output[index], output[swap] = output[swap], output[index]
        return output

    def child(self, domain: str) -> "DeterministicRNG":
        child_domain = f"{self.domain}/{domain}"
        _domain_bytes(child_domain)
        return self._from_material(self._root_material, child_domain)

    def stage_rng(self, stage: str) -> "DeterministicRNG":
        if stage not in STAGE_DOMAINS:
            raise RNGContractError(f"unknown RNG stage domain: {stage!r}")
        return self.child(stage)

    def stage_seed(self, stage: str) -> str:
        if stage not in STAGE_DOMAINS:
            raise RNGContractError(f"unknown RNG stage domain: {stage!r}")
        return hashlib.sha256(
            self._root_material + b"\0stage-seed\0" + stage.encode("utf-8")
        ).hexdigest()

    def stage_seeds(self) -> dict[str, str]:
        return {stage: self.stage_seed(stage) for stage in STAGE_DOMAINS}

    def retry_seed(self, attempt: int) -> str:
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 0:
            raise RNGContractError("retry attempt must be a non-negative integer")
        return hashlib.sha256(
            self._root_material + b"\0retry-seed\0" + attempt.to_bytes(16, "big")
        ).hexdigest()

    def retry_rng(self, attempt: int) -> "DeterministicRNG":
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 0:
            raise RNGContractError("retry attempt must be a non-negative integer")
        return self.child(f"retry/{attempt}")
