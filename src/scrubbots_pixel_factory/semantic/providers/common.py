"""Small deterministic helpers shared by provider bridges."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from ..contracts import ImageInputDescriptor, ImageInputRole, SemanticContractError


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def typed_seed(seed: int | str) -> dict[str, object]:
    return {"type": "int" if isinstance(seed, int) else "string", "value": seed}


def image_identity(image: ImageInputDescriptor | None) -> dict[str, object] | None:
    return None if image is None else image.canonical_dict()


def role_value(role: ImageInputRole | str) -> str:
    return ImageInputRole.parse(role).value


def require_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SemanticContractError(f"{label} must be a mapping")
    return value


def bytes_sha256(value: bytes) -> str:
    if not isinstance(value, bytes):
        raise SemanticContractError("image bytes must be immutable bytes")
    return hashlib.sha256(value).hexdigest()


def require_bytes_hash(value: bytes, expected: str) -> None:
    if bytes_sha256(value) != expected:
        raise SemanticContractError("bound image bytes do not match content_sha256")
