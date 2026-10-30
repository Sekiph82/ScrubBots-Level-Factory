"""Bounded, non-recursive folder intake for owner-selected PNG sources."""

from __future__ import annotations

from pathlib import Path
import hashlib
import stat
from typing import Any

from .owner_art_storage import OwnerArtStorageError, _is_reparse_point, owner_art_paths
from .semantic.normalization.core import RAW_ARTIFACT_MAX_BYTES, SUPPORTED_MEDIA_TYPE, SemanticRawArtifact
from .owner_upload import owner_upload_root


MAX_OWNER_FOLDER_PNGS = 150
_PROVIDER_KEYS = {
    "ALPIX": "alpix",
    "PIXELLAB": "pixellab_final",
    "OWNER_SUGGESTIONS": "owner_suggestions",
}


class OwnerFolderBatchError(ValueError):
    """Raised when an owner-selected source folder is outside the safe scope."""


def approved_owner_source_folders(repository_root: str | Path | None = None) -> dict[str, Path]:
    paths = owner_art_paths(repository_root)
    return {provider: paths[key] for provider, key in _PROVIDER_KEYS.items()}


def scan_owner_source_folder(
    folder_path: str | Path,
    *,
    repository_root: str | Path | None = None,
    explicit_alternative: bool = False,
) -> dict[str, Any]:
    """List direct-child PNG candidates; the canonical importer validates bytes.

    Approved provider folders are exact-match only. An alternate path is accepted
    only when the UI passes the explicit owner-selected flag. Traversal is never
    recursive and PixelLab raw atlas storage is always excluded.
    """
    paths = owner_art_paths(repository_root)
    root = paths["input"].parents[1]
    raw_folder = Path(folder_path).absolute()
    resolved_folder = raw_folder.resolve(strict=True)
    if _is_reparse_point(root):
        raise OwnerFolderBatchError("canonical repository root is a reparse point")
    cursor = raw_folder
    while cursor != cursor.parent:
        if _is_reparse_point(cursor):
            raise OwnerFolderBatchError("selected source path contains a symlink or reparse point")
        cursor = cursor.parent
    if not resolved_folder.is_dir():
        raise OwnerFolderBatchError("selected source is not a directory")

    grid_root = paths["pixellab_grid_files"].resolve(strict=False)
    if resolved_folder == grid_root or grid_root in resolved_folder.parents:
        raise OwnerFolderBatchError("PixelLab Grid Files stores raw atlases and is never a single-level intake source")

    provider = next((name for name, approved in approved_owner_source_folders(root).items()
                     if resolved_folder == approved.resolve(strict=False)), "")
    if not provider and not explicit_alternative:
        raise OwnerFolderBatchError("source folder is not an approved provider folder")
    if explicit_alternative:
        provider = "OWNER_SELECTED_ALTERNATIVE"

    png_files: list[Path] = []
    for entry in resolved_folder.iterdir():
        if entry.suffix.lower() != ".png":
            continue
        if _is_reparse_point(entry):
            raise OwnerFolderBatchError(f"PNG candidate is a symlink or reparse point: {entry.name}")
        if not entry.is_file():
            continue
        mode = entry.stat().st_mode
        if not stat.S_ISREG(mode):
            continue
        png_files.append(entry)
    png_files.sort(key=lambda item: (item.name.casefold(), item.name))
    if len(png_files) > MAX_OWNER_FOLDER_PNGS:
        raise OwnerFolderBatchError(
            f"folder contains {len(png_files)} direct PNG files; limit is {MAX_OWNER_FOLDER_PNGS}; no files were imported"
        )
    entries: list[dict[str, Any]] = []
    valid_paths: list[str] = []
    rejected: list[dict[str, Any]] = []
    seen_digests: set[str] = set()
    seen_names: dict[str, str] = {}
    existing_sources = owner_upload_root()
    for index, item in enumerate(png_files):
        try:
            if item.stat().st_size > RAW_ARTIFACT_MAX_BYTES:
                raise OwnerFolderBatchError("PNG exceeds the bounded source size")
            artifact = SemanticRawArtifact.from_local_file(item, media_type=SUPPORTED_MEDIA_TYPE)
            width, height = artifact.returned_width, artifact.returned_height
            digest = hashlib.sha256(bytes(artifact.raw_bytes)).hexdigest()
            result = {
                "index": index, "path": str(item), "display_path": item.name, "source_sha256": digest,
                "width": width, "height": height, "disposition": "ELIGIBLE",
            }
            filename_key = item.name.casefold()
            previous_digest = seen_names.get(filename_key)
            if previous_digest is not None and previous_digest != digest:
                result["filename_collision"] = True
                result["collision_with_sha256"] = previous_digest
                for prior_entry in entries:
                    if str(prior_entry.get("display_path", "")).casefold() == filename_key:
                        prior_entry["filename_collision"] = True
                        prior_entry["collision_with_sha256"] = digest
            else:
                seen_names[filename_key] = digest
            if not 20 <= width <= 59 or not 20 <= height <= 59:
                result["disposition"] = "REJECTED"
                result["reason"] = "GAME_ARTWORK_DIMENSIONS_MUST_BE_20_TO_59_PIXELS"
                rejected.append({
                    "index": index, "display_path": item.name, "original_source_path": str(item),
                    "source_sha256": digest, "original_width": width, "original_height": height,
                    "error": result["reason"],
                })
            else:
                source_id = f"owner-upload-{digest}"
                if digest in seen_digests:
                    result["disposition"] = "SKIPPED_DUPLICATE"
                    result["reason"] = "DUPLICATE_IDENTICAL_SHA256_IN_SELECTED_FOLDER"
                elif (existing_sources / source_id).exists():
                    from . import studio_extensions
                    try:
                        studio_extensions.verify_owner_source(source_id)
                        result["disposition"] = "ALREADY_IMPORTED"
                        result["reason"] = "IDENTICAL_SHA256_ALREADY_IMPORTED"
                    except (studio_extensions.StudioExtensionError, OSError, ValueError) as exc:
                        result["disposition"] = "FAILED"
                        result["reason"] = f"EXISTING_SOURCE_IDENTITY_CONFLICT: {str(exc)[:300]}"
                        rejected.append({
                            "index": index, "display_path": item.name, "original_source_path": str(item),
                            "source_sha256": digest, "original_width": width, "original_height": height,
                            "error": result["reason"], "disposition": "FAILED",
                        })
                seen_digests.add(digest)
                if result["disposition"] != "FAILED":
                    valid_paths.append(str(item))
            entries.append(result)
        except (OSError, TypeError, ValueError, OwnerArtStorageError) as exc:
            reason = str(exc)[:400] or "PNG could not be validated"
            result = {"index": index, "path": str(item), "display_path": item.name,
                      "disposition": "REJECTED", "reason": reason}
            entries.append(result)
            rejected.append({"index": index, "display_path": item.name,
                             "original_source_path": str(item), "error": reason})
    return {
        "provider": provider,
        "selected_folder": str(resolved_folder),
        "png_count": len(png_files),
        "paths": valid_paths,
        "entries": entries,
        "pre_rejected": rejected,
    }


def import_owner_source_folder(
    folder_path: str | Path,
    *,
    repository_root: str | Path | None = None,
    explicit_alternative: bool = False,
) -> dict[str, Any]:
    """Import a bounded owner folder through canonical OWNER_UPLOAD hashing."""
    scanned = scan_owner_source_folder(
        folder_path,
        repository_root=repository_root,
        explicit_alternative=explicit_alternative,
    )
    from . import studio_extensions

    payload = studio_extensions.batch_import(
        scanned["paths"],
        source_provider=scanned["provider"],
        source_folder=scanned["selected_folder"],
        pre_rejected=scanned["pre_rejected"],
        path_indices=[int(item["index"]) for item in scanned["entries"] if item.get("disposition") == "ELIGIBLE"],
    )
    return {**payload, "source_provider": scanned["provider"],
            "source_folder": scanned["selected_folder"], "png_count": scanned["png_count"]}


__all__ = [
    "MAX_OWNER_FOLDER_PNGS", "OwnerFolderBatchError", "approved_owner_source_folders",
    "import_owner_source_folder", "scan_owner_source_folder",
]
