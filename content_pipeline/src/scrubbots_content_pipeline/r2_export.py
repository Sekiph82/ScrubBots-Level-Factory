"""Read-only production content export with exact-byte verification."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from .config import Environment
from .manifest_parser import ManifestParseError, parse_content_manifest_v1
from .provider import ProviderObjectBytesResult, ProviderResultCategory

_SAFE_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,511}$")
MANIFEST_KEY = "manifests/current.json"


class ProductionContentReader(Protocol):
    def read_object_bytes(self, environment: Environment, object_key: str) -> ProviderObjectBytesResult: ...


class ExportReason(StrEnum):
    EXPORTED = "EXPORTED"
    INVALID_PROVIDER = "INVALID_PROVIDER"
    MANIFEST_UNAVAILABLE = "MANIFEST_UNAVAILABLE"
    MANIFEST_INVALID = "MANIFEST_INVALID"
    PACK_UNAVAILABLE = "PACK_UNAVAILABLE"
    PACK_INTEGRITY_MISMATCH = "PACK_INTEGRITY_MISMATCH"
    DESTINATION_CONFLICT = "DESTINATION_CONFLICT"
    DESTINATION_ERROR = "DESTINATION_ERROR"


@dataclass(frozen=True, slots=True)
class ProductionExportReport:
    accepted: bool
    reason_code: ExportReason
    receipt_bytes: bytes | None
    exported_paths: tuple[str, ...]


def export_current_production(provider: object, destination: str | Path) -> ProductionExportReport:
    """Download current manifest and referenced packs without any provider mutation."""
    read = getattr(provider, "read_object_bytes", None)
    if not callable(read):
        return ProductionExportReport(False, ExportReason.INVALID_PROVIDER, None, ())
    try:
        manifest_result = read(Environment.PRODUCTION, MANIFEST_KEY)
    except Exception:
        return ProductionExportReport(False, ExportReason.MANIFEST_UNAVAILABLE, None, ())
    raw_manifest = _accepted_bytes(manifest_result, MANIFEST_KEY)
    if raw_manifest is None:
        return ProductionExportReport(False, ExportReason.MANIFEST_UNAVAILABLE, None, ())
    try:
        manifest = parse_content_manifest_v1(raw_manifest)
        if manifest.to_json_bytes() != raw_manifest:
            return ProductionExportReport(False, ExportReason.MANIFEST_INVALID, None, ())
    except Exception:
        return ProductionExportReport(False, ExportReason.MANIFEST_INVALID, None, ())

    manifest_sha = hashlib.sha256(raw_manifest).hexdigest()
    objects: dict[str, bytes] = {MANIFEST_KEY: raw_manifest}
    packs: list[dict[str, object]] = []
    for pack in sorted(manifest.packs, key=lambda item: item.pack_id.encode("ascii")):
        key = pack.object_key
        if not isinstance(key, str) or not _SAFE_KEY.fullmatch(key) or any(p in {".", ".."} for p in key.split("/")):
            return ProductionExportReport(False, ExportReason.MANIFEST_INVALID, None, ())
        try:
            result = read(Environment.PRODUCTION, key)
        except Exception:
            return ProductionExportReport(False, ExportReason.PACK_UNAVAILABLE, None, ())
        raw = _accepted_bytes(result, key)
        if raw is None:
            return ProductionExportReport(False, ExportReason.PACK_UNAVAILABLE, None, ())
        digest = hashlib.sha256(raw).hexdigest()
        if len(raw) != pack.byte_length or digest != pack.sha256:
            return ProductionExportReport(False, ExportReason.PACK_INTEGRITY_MISMATCH, None, ())
        objects[key] = raw
        packs.append({"pack_id": pack.pack_id, "object_key": key,
                      "sha256": digest, "byte_length": len(raw)})

    receipt = _canonical({
        "format_version": "1.0",
        "manifest": {"object_key": MANIFEST_KEY, "sha256": manifest_sha,
                     "byte_length": len(raw_manifest), "content_version": manifest.content_version},
        "packs": packs,
    })
    try:
        root = Path(destination).expanduser().resolve()
        project_root = Path(__file__).resolve().parents[3]
        if root == project_root or root.is_relative_to(project_root):
            return ProductionExportReport(False, ExportReason.DESTINATION_ERROR, None, ())
        targets = {key: _safe_destination(root, key) for key in objects}
        receipt_target = _safe_destination(root, "export-receipt.json")
        if any(path.exists() for path in (*targets.values(), receipt_target)):
            return ProductionExportReport(False, ExportReason.DESTINATION_CONFLICT, None, ())
        root.mkdir(parents=True, exist_ok=True)
        for path in targets.values():
            _make_safe_parents(root, path.parent)
        for key, raw in objects.items():
            with targets[key].open("xb") as stream:
                stream.write(raw)
        _make_safe_parents(root, receipt_target.parent)
        with receipt_target.open("xb") as stream:
            stream.write(receipt)
    except FileExistsError:
        return ProductionExportReport(False, ExportReason.DESTINATION_CONFLICT, None, ())
    except Exception:
        return ProductionExportReport(False, ExportReason.DESTINATION_ERROR, None, ())
    paths = tuple(sorted((*objects.keys(), "export-receipt.json")))
    return ProductionExportReport(True, ExportReason.EXPORTED, receipt, paths)


def _accepted_bytes(result: object, key: str) -> bytes | None:
    if (not isinstance(result, ProviderObjectBytesResult)
            or result.category is not ProviderResultCategory.SUCCESS
            or result.environment is not Environment.PRODUCTION
            or result.object_key != key or type(result.content_bytes) is not bytes):
        return None
    return result.content_bytes


def _safe_destination(root: Path, key: str) -> Path:
    if not _SAFE_KEY.fullmatch(key) or any(part in {".", ".."} for part in key.split("/")):
        raise ValueError("unsafe export key")
    target = root.joinpath(*key.split("/"))
    if not target.resolve().is_relative_to(root):
        raise ValueError("export escaped destination")
    return target


def _make_safe_parents(root: Path, parent: Path) -> None:
    relative = parent.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise ValueError("symlink destination")
        current.mkdir(exist_ok=True)


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8") + b"\n"


__all__ = ["ExportReason", "ProductionExportReport", "export_current_production"]
