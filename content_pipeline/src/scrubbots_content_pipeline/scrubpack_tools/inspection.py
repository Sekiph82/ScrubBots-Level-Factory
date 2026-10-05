"""Read-only validation and safe local extraction for untrusted .scrubpack files."""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import stat
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ..payload_validation import MAX_PAYLOAD_BYTES
from ..scrubpack_spec import (
    PACK_MANIFEST_PATH,
    SCRUBPACK_SCHEMA,
    ScrubpackManifestV1,
    ScrubpackSpecError,
    SUPPORTED_SCRUBPACK_VERSIONS,
    expected_member_names,
    validate_member_names,
)


MAX_SCRUBPACK_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_SCRUBPACK_MEMBERS = 4096

_MESSAGES = {
    "VALID": "Scrubpack is valid.",
    "SOURCE_INVALID": "Source must be an explicit local regular file.",
    "SOURCE_TOO_LARGE": "Archive exceeds the inspection size limit.",
    "INVALID_ZIP": "Archive is not a valid readable ZIP container.",
    "UNSUPPORTED_ZIP_METADATA": "Archive contains unsupported, encrypted, executable, or special entries.",
    "INVALID_MEMBER_LAYOUT": "Archive member paths or order do not match the V1 manifest.",
    "INVALID_MANIFEST": "Root manifest is malformed or unsupported.",
    "UNSUPPORTED_VERSION": "Archive uses a pack or payload contract version this reader does not support.",
    "INVALID_MEMBER_VERSION": "A payload version marker or schema identity is missing or malformed.",
    "MEMBER_DIGEST_MISMATCH": "A member's exact bytes do not match its manifest SHA-256.",
    "DESTINATION_INVALID": "Destination parent is unavailable or the destination is not a valid new directory path.",
    "DESTINATION_EXISTS": "Destination already exists; extraction will not overwrite it.",
    "EXTRACTION_FAILED": "Validated archive could not be safely extracted.",
}


@dataclass(frozen=True, slots=True)
class ScrubpackInspectionResult:
    accepted: bool
    reason_code: str
    pack_id: str | None = None
    pack_version: int | None = None
    level_ids: tuple[str, ...] = ()
    member_names: tuple[str, ...] = ()
    archive_sha256: str | None = None
    extracted: bool = False

    @property
    def message(self) -> str:
        return _MESSAGES.get(self.reason_code, "Scrubpack operation failed.")

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "archive_sha256": self.archive_sha256,
            "extracted": self.extracted,
            "level_count": len(self.level_ids),
            "level_ids": list(self.level_ids),
            "member_names": list(self.member_names),
            "message": self.message,
            "pack_id": self.pack_id,
            "pack_version": self.pack_version,
            "reason_code": self.reason_code,
        }

    def render_human(self) -> str:
        if not self.accepted:
            return f"{self.reason_code}: {self.message}"
        return (
            f"{self.message} Pack {self.pack_id} v{self.pack_version}; "
            f"{len(self.level_ids)} level(s); {len(self.member_names)} member(s); "
            f"SHA-256 {self.archive_sha256}."
        )


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _failure(reason_code: str) -> ScrubpackInspectionResult:
    return ScrubpackInspectionResult(False, reason_code)


def _manifest_version_reason(value: object) -> str | None:
    if not isinstance(value, dict) or "schema" not in value or "version" not in value:
        return "INVALID_MANIFEST"
    schema = value["schema"]
    version = value["version"]
    if not isinstance(schema, str) or type(version) is not int or version <= 0:
        return "INVALID_MANIFEST"
    if schema != SCRUBPACK_SCHEMA or version not in SUPPORTED_SCRUBPACK_VERSIONS:
        return "UNSUPPORTED_VERSION"
    return None


def _payload_version_reason(name: str, payload: bytes) -> str | None:
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError):
        return "INVALID_MEMBER_VERSION"
    if not isinstance(value, dict) or "version" not in value:
        return "INVALID_MEMBER_VERSION"
    version = value["version"]
    if type(version) is not int or version <= 0:
        return "INVALID_MEMBER_VERSION"
    if version != 1:
        return "UNSUPPORTED_VERSION"
    expected_schema = {
        "level.json": None,
        "supply-plan.json": "scrubbots.level_supply_plan.v1",
        "metadata.json": "scrubbots.level.metadata.v1",
    }[name.rsplit("/", 1)[-1]]
    if expected_schema is None:
        if "schema" in value:
            return "UNSUPPORTED_VERSION" if isinstance(value["schema"], str) else "INVALID_MEMBER_VERSION"
    elif value.get("schema") != expected_schema:
        return "UNSUPPORTED_VERSION" if isinstance(value.get("schema"), str) else "INVALID_MEMBER_VERSION"
    return None


def _read_local_archive(path: str | os.PathLike[str]) -> bytes | ScrubpackInspectionResult:
    try:
        source = Path(path)
        if str(path).startswith(("\\\\", "//")) or source.is_symlink() or not source.is_file():
            return _failure("SOURCE_INVALID")
        if source.stat().st_size > MAX_SCRUBPACK_ARCHIVE_BYTES:
            return _failure("SOURCE_TOO_LARGE")
        return source.read_bytes()
    except (OSError, TypeError, ValueError):
        return _failure("SOURCE_INVALID")


def _zip_entry_is_safe(info: zipfile.ZipInfo) -> bool:
    if info.is_dir() or info.flag_bits & 0x1 or info.compress_type != zipfile.ZIP_STORED:
        return False
    if info.file_size > MAX_PAYLOAD_BYTES or info.file_size < 0 or info.compress_size != info.file_size:
        return False
    if info.create_system not in (0, 3):
        return False
    mode = (info.external_attr >> 16) & 0xFFFF
    kind = stat.S_IFMT(mode)
    if kind not in (0, stat.S_IFREG) or mode & 0o111:
        return False
    if info.create_system == 0:
        dos_attributes = info.external_attr & 0xFFFF
        if dos_attributes & (0x10 | 0x400):
            return False
    return True


def _inspect_archive_bytes(raw: bytes) -> ScrubpackInspectionResult:
    if len(raw) > MAX_SCRUBPACK_ARCHIVE_BYTES:
        return _failure("SOURCE_TOO_LARGE")
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw), mode="r")
    except (OSError, ValueError, zipfile.BadZipFile, zipfile.LargeZipFile):
        return _failure("INVALID_ZIP")
    try:
        with archive:
            infos = archive.infolist()
            if not infos or len(infos) > MAX_SCRUBPACK_MEMBERS:
                return _failure("INVALID_MEMBER_LAYOUT")
            names = tuple(info.filename for info in infos)
            if not validate_member_names(names):
                return _failure("INVALID_MEMBER_LAYOUT")
            if any(not _zip_entry_is_safe(info) for info in infos):
                return _failure("UNSUPPORTED_ZIP_METADATA")
            if names.count(PACK_MANIFEST_PATH) != 1 or names[0] != PACK_MANIFEST_PATH:
                return _failure("INVALID_MEMBER_LAYOUT")
            try:
                corrupt_member = archive.testzip()
            except (OSError, RuntimeError, zipfile.BadZipFile):
                return _failure("INVALID_ZIP")
            if corrupt_member is not None:
                return _failure("INVALID_ZIP")
            try:
                manifest_bytes = archive.read(PACK_MANIFEST_PATH)
                manifest_data = json.loads(manifest_bytes, object_pairs_hook=_reject_duplicate_keys)
                version_reason = _manifest_version_reason(manifest_data)
                if version_reason is not None:
                    return _failure(version_reason)
                manifest = ScrubpackManifestV1.from_dict(manifest_data)
                expected_names = expected_member_names(manifest.levels)
            except (OSError, ValueError, TypeError, KeyError, ScrubpackSpecError):
                return _failure("INVALID_MANIFEST")
            if names != expected_names:
                return _failure("INVALID_MEMBER_LAYOUT")
            for path, expected_digest in manifest.member_sha256.items():
                digest = hashlib.sha256()
                try:
                    with archive.open(path, mode="r") as member:
                        while chunk := member.read(64 * 1024):
                            digest.update(chunk)
                except (OSError, RuntimeError, zipfile.BadZipFile, KeyError):
                    return _failure("INVALID_ZIP")
                if digest.hexdigest() != expected_digest:
                    return _failure("MEMBER_DIGEST_MISMATCH")
                try:
                    payload = archive.read(path)
                except (OSError, RuntimeError, zipfile.BadZipFile, KeyError):
                    return _failure("INVALID_ZIP")
                version_reason = _payload_version_reason(path, payload)
                if version_reason is not None:
                    return _failure(version_reason)
            return ScrubpackInspectionResult(
                accepted=True,
                reason_code="VALID",
                pack_id=manifest.pack_id,
                pack_version=manifest.pack_version,
                level_ids=tuple(level.level_id for level in manifest.levels),
                member_names=names,
                archive_sha256=hashlib.sha256(raw).hexdigest(),
            )
    except (OSError, RuntimeError, ValueError, TypeError, zipfile.BadZipFile, zipfile.LargeZipFile):
        return _failure("INVALID_ZIP")


def inspect_scrubpack(path: str | os.PathLike[str]) -> ScrubpackInspectionResult:
    """Inspect one explicit local pack without writing or loading its payloads."""
    raw = _read_local_archive(path)
    if isinstance(raw, ScrubpackInspectionResult):
        return raw
    return _inspect_archive_bytes(raw)


def extract_scrubpack(
    path: str | os.PathLike[str], destination: str | os.PathLike[str]
) -> ScrubpackInspectionResult:
    """Validate a pack fully, then extract into a new explicit destination directory."""
    raw = _read_local_archive(path)
    if isinstance(raw, ScrubpackInspectionResult):
        return raw
    inspection = _inspect_archive_bytes(raw)
    if not inspection.accepted:
        return inspection
    temporary_root: Path | None = None
    try:
        target_root = Path(destination)
        if not str(destination) or target_root.exists() or target_root.is_symlink():
            return _failure("DESTINATION_EXISTS" if target_root.exists() or target_root.is_symlink() else "DESTINATION_INVALID")
        parent = target_root.parent.resolve(strict=True)
        if not parent.is_dir() or target_root.name in ("", ".", ".."):
            return _failure("DESTINATION_INVALID")
        target_root = parent / target_root.name
        temporary_root = Path(tempfile.mkdtemp(prefix=".scrubpack-inspect-", dir=parent))
        root_resolved = temporary_root.resolve(strict=True)
        with zipfile.ZipFile(io.BytesIO(raw), mode="r") as archive:
            for name in inspection.member_names:
                relative = PurePosixPath(name)
                output = temporary_root.joinpath(*relative.parts)
                if not output.resolve(strict=False).is_relative_to(root_resolved):
                    return _failure("INVALID_MEMBER_LAYOUT")
                output.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(name, mode="r") as source, output.open("xb") as sink:
                    while chunk := source.read(64 * 1024):
                        sink.write(chunk)
        if target_root.exists() or target_root.is_symlink():
            return _failure("DESTINATION_EXISTS")
        os.rename(temporary_root, target_root)
        temporary_root = None
        return ScrubpackInspectionResult(
            accepted=True,
            reason_code="VALID",
            pack_id=inspection.pack_id,
            pack_version=inspection.pack_version,
            level_ids=inspection.level_ids,
            member_names=inspection.member_names,
            archive_sha256=inspection.archive_sha256,
            extracted=True,
        )
    except (OSError, RuntimeError, ValueError, TypeError):
        return _failure("EXTRACTION_FAILED")
    finally:
        if temporary_root is not None:
            shutil.rmtree(temporary_root, ignore_errors=True)


__all__ = [
    "MAX_SCRUBPACK_ARCHIVE_BYTES",
    "MAX_SCRUBPACK_MEMBERS",
    "ScrubpackInspectionResult",
    "extract_scrubpack",
    "inspect_scrubpack",
]
