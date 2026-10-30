"""Owner-visible artwork folders with immutable, content-addressed copies."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any, Mapping


_FOLDER_RELATIVE_PATHS = {
    "input": "data/input",
    "alpix": "data/output/Alpix",
    "pixellab": "data/output/Pixellab",
    "pixellab_grid_files": "data/output/Pixellab/Grid Files",
    "pixellab_final": "data/output/Pixellab/Final",
    "owner_suggestions": "data/output/Owner Suggestions",
    "release_pool": "data/Release Pool",
    "pending": "data/Release Pool/Pending",
    "ready": "data/Release Pool/Ready",
    "failed": "data/Release Pool/Failed",
    "rejected": "data/Release Pool/Rejected",
}
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class OwnerArtStorageError(ValueError):
    """Raised when an owner-art path or immutable artifact is unsafe."""


def owner_art_paths(repository_root: str | Path | None = None) -> dict[str, Path]:
    root = Path(repository_root).resolve() if repository_root is not None else Path(__file__).resolve().parents[2]
    return {key: root / relative for key, relative in _FOLDER_RELATIVE_PATHS.items()}


def _is_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError:
        return True
    if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400):
        return True
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction):
        try:
            return bool(is_junction())
        except OSError:
            return True
    return False


def _verify_path_under_root(root: Path, target: Path) -> None:
    if not target.is_relative_to(root):
        raise OwnerArtStorageError("owner-art path escaped the canonical repository")
    relative = target.relative_to(root)
    current = root
    if _is_reparse_point(root):
        raise OwnerArtStorageError("canonical repository root is a reparse point")
    for component in relative.parts:
        current = current / component
        if _is_reparse_point(current):
            raise OwnerArtStorageError("owner-art path contains a symlink or reparse point")
        if current.exists() and not current.is_dir():
            raise OwnerArtStorageError("owner-art directory path collides with a non-directory")
        if current.exists() and current.resolve() != current:
            raise OwnerArtStorageError("owner-art directory resolves outside its canonical path")


def ensure_owner_art_layout(repository_root: str | Path | None = None) -> dict[str, Path]:
    paths = owner_art_paths(repository_root)
    root = paths["input"].parents[1]
    if not root.is_dir():
        raise OwnerArtStorageError("canonical repository root is unavailable")
    for directory in paths.values():
        _verify_path_under_root(root, directory)
        directory.mkdir(parents=True, exist_ok=True)
    return paths


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write_content_addressed(directory: Path, filename: str, raw: bytes, expected_sha256: str) -> Path:
    if not _SHA256.fullmatch(expected_sha256) or _hash(raw) != expected_sha256:
        raise OwnerArtStorageError("artifact bytes do not match their SHA-256 identity")
    if Path(filename).name != filename or not filename.lower().endswith(".png"):
        raise OwnerArtStorageError("artifact filename is unsafe")
    target = directory / filename
    if _is_reparse_point(target):
        raise OwnerArtStorageError("owner artifact target is a symlink or reparse point")
    if target.exists():
        if not target.is_file() or _hash(target.read_bytes()) != expected_sha256:
            raise OwnerArtStorageError("content-addressed owner artifact already exists with different bytes")
        return target

    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{expected_sha256}.", suffix=".partial", dir=directory)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            if not target.is_file() or _hash(target.read_bytes()) != expected_sha256:
                raise OwnerArtStorageError("concurrent owner artifact has a conflicting content identity")
        return target
    finally:
        temporary.unlink(missing_ok=True)


def archive_alpix_png(raw_png: bytes, *, repository_root: str | Path | None = None) -> Path:
    if type(raw_png) is not bytes or not raw_png.startswith(b"\x89PNG\r\n\x1a\n"):
        raise OwnerArtStorageError("ALPIX output is not a PNG byte stream")
    digest = _hash(raw_png)
    paths = ensure_owner_art_layout(repository_root)
    return _write_content_addressed(paths["alpix"], f"alpix-{digest}.png", raw_png, digest)


def archive_pixellab_export(
    output_directory: str | Path,
    manifest: Mapping[str, Any],
    *,
    repository_root: str | Path | None = None,
) -> dict[str, Any]:
    """Copy one verified atlas and its exact sixteen slices to owner folders."""
    if manifest.get("schema") != "scrubbots-pixellab-pro-4x4-source/v2":
        raise OwnerArtStorageError("PixelLab atlas manifest schema is invalid")
    atlas_sha = manifest.get("source_atlas_sha256")
    source_kind = manifest.get("source_kind")
    frames = manifest.get("frames")
    if not isinstance(atlas_sha, str) or not _SHA256.fullmatch(atlas_sha):
        raise OwnerArtStorageError("PixelLab atlas digest is invalid")
    if not isinstance(frames, list) or len(frames) != 16:
        raise OwnerArtStorageError("PixelLab export must contain exactly sixteen slices")
    if source_kind not in {"IMPORTED_ATLAS", "PHOTOPEA_SLICES_ZIP", "PRO_API_FRAMES"}:
        raise OwnerArtStorageError("PixelLab source kind is invalid")

    paths = ensure_owner_art_layout(repository_root)
    source_root = Path(output_directory).resolve()
    original = source_root / "original-atlas.png"
    if _is_reparse_point(original) or not original.is_file():
        raise OwnerArtStorageError("PixelLab original atlas is missing or unsafe")
    atlas_bytes = original.read_bytes()
    if _hash(atlas_bytes) != atlas_sha:
        raise OwnerArtStorageError("PixelLab original atlas does not match its manifest")
    atlas_target = _write_content_addressed(paths["pixellab_grid_files"], f"atlas-{atlas_sha}.png", atlas_bytes, atlas_sha)

    slices: list[dict[str, Any]] = []
    seen: set[int] = set()
    for frame in frames:
        if not isinstance(frame, Mapping):
            raise OwnerArtStorageError("PixelLab frame manifest entry is invalid")
        index = frame.get("index")
        frame_sha = frame.get("sha256")
        filename = frame.get("filename")
        if type(index) is not int or not 1 <= index <= 16 or index in seen:
            raise OwnerArtStorageError("PixelLab slice indexes must uniquely cover 1..16")
        if not isinstance(frame_sha, str) or not _SHA256.fullmatch(frame_sha):
            raise OwnerArtStorageError("PixelLab slice digest is invalid")
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise OwnerArtStorageError("PixelLab slice filename is unsafe")
        slice_path = source_root / filename
        if _is_reparse_point(slice_path) or not slice_path.is_file():
            raise OwnerArtStorageError("PixelLab slice is missing or unsafe")
        slice_bytes = slice_path.read_bytes()
        if _hash(slice_bytes) != frame_sha:
            raise OwnerArtStorageError("PixelLab slice bytes do not match the export manifest")
        slice_target = _write_content_addressed(
            paths["pixellab_final"], f"atlas-{atlas_sha}-sprite-{index:02d}-{frame_sha}.png", slice_bytes, frame_sha
        )
        slices.append({"index": index, "sha256": frame_sha, "path": str(slice_target)})
        seen.add(index)
    if seen != set(range(1, 17)):
        raise OwnerArtStorageError("PixelLab export is missing a row-major slice")
    slices.sort(key=lambda item: int(item["index"]))
    record = {
        "schema": "scrubbots-owner-pixellab-atlas-catalog/v1",
        "source_atlas_sha256": atlas_sha,
        "source_kind": source_kind,
        "atlas_path": str(atlas_target),
        "frame_dimensions": manifest.get("frame_dimensions"),
        "palette_enforcement": "FULL_V3_TARGET_PALETTE_AND_PER_FRAME_LOCAL_VALIDATION",
        "slices": slices,
    }
    record_path = paths["pixellab"] / f"atlas-{atlas_sha}-{source_kind.lower()}.json"
    encoded = (json.dumps(record, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if _is_reparse_point(record_path):
        raise OwnerArtStorageError("PixelLab atlas catalog target is a symlink or reparse point")
    if record_path.exists():
        if record_path.read_bytes() != encoded:
            raise OwnerArtStorageError("PixelLab atlas catalog record conflicts with existing bytes")
    else:
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{atlas_sha}.", suffix=".partial", dir=record_path.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, record_path)
            except FileExistsError:
                if record_path.read_bytes() != encoded:
                    raise OwnerArtStorageError("concurrent PixelLab atlas record conflicts")
        finally:
            temporary.unlink(missing_ok=True)
    return {**record, "catalog_path": str(record_path)}


__all__ = ["OwnerArtStorageError", "archive_alpix_png", "archive_pixellab_export", "ensure_owner_art_layout", "owner_art_paths"]
