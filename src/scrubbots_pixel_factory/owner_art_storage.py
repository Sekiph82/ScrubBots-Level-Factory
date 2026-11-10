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
from io import BytesIO

from PIL import Image


_FOLDER_RELATIVE_PATHS = {
    "input": "data/input",
    "level_factory": "data/Level Factory",
    "imported": "data/Level Factory/Imported",
    "batches": "data/Level Factory/Batches",
    "batch_imports": "data/Level Factory/Batches/Imports",
    "batch_jobs": "data/Level Factory/Batches/Jobs",
    "batch_control": "data/Level Factory/Batches/Control",
    "batch_locks": "data/Level Factory/Batches/Locks",
    "activity": "data/Level Factory/Activity",
    "workspace": "data/Level Factory/Workspace",
    "runtime": "data/Level Factory/Runtime",
    "pixellab": "data/output/Pixellab",
    "pixellab_grid_files": "data/output/Pixellab/Grid Files",
    "pixellab_final": "data/output/Pixellab/Final",
    "pixellab_transactions": "data/output/Pixellab/Transactions",
    "release_pool": "data/Release Pool",
    "pending": "data/Release Pool/Pending",
    "ready": "data/Release Pool/Ready",
    "failed": "data/Release Pool/Failed",
    "rejected": "data/Release Pool/Rejected",
    "solver_jobs": "data/Release Pool/Pending/Pipelines/SolverJobs",
    "pipeline_work": "data/Release Pool/Pending/Pipelines/Work",
}
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class OwnerArtStorageError(ValueError):
    """Raised when an owner-art path or immutable artifact is unsafe."""


_REPOSITORY_ROOT_CACHE: dict[tuple[str, str], Path] = {}


def factory_repository_root(anchor: str | Path | None = None) -> Path:
    """Resolve the one canonical mutable-data root from source and installed Release."""

    # The checkout layout does not change while a worker runs; a startup refresh
    # used to re-walk the disk ~9,600 times. Only successful lookups are cached.
    key = (str(anchor if anchor is not None else __file__), os.environ.get("USERPROFILE", ""))
    cached = _REPOSITORY_ROOT_CACHE.get(key)
    if cached is not None:
        return cached
    root = _resolve_factory_repository_root(anchor)
    _REPOSITORY_ROOT_CACHE[key] = root
    return root


def _resolve_factory_repository_root(anchor: str | Path | None = None) -> Path:
    location = Path(anchor if anchor is not None else __file__).resolve()
    start = location if location.is_dir() else location.parent
    for candidate in (start, *start.parents):
        git_metadata = candidate / ".git"
        if ((git_metadata.is_dir() or git_metadata.is_file()) and (candidate / "TASKS.md").is_file()):
            return candidate
    profile = os.environ.get("USERPROFILE")
    if profile:
        canonical = Path(profile) / "Desktop" / "Scrubbots - Pixel Art Generator"
        git_metadata = canonical / ".git"
        if ((git_metadata.is_dir() or git_metadata.is_file()) and (canonical / "TASKS.md").is_file()):
            return canonical.resolve()
    # Never treat the installed Release directory as a mutable-data root. If
    # the canonical Desktop checkout cannot be identified, fail closed rather
    # than quietly writing solver/import data beside the executable.
    raise OwnerArtStorageError("canonical Factory data checkout could not be resolved")


def owner_art_paths(repository_root: str | Path | None = None) -> dict[str, Path]:
    root = Path(repository_root).resolve() if repository_root is not None else factory_repository_root()
    return {key: root / relative for key, relative in _FOLDER_RELATIVE_PATHS.items()}


def pixellab_asset_name_manifest(repository_root: str | Path | None = None) -> Path:
    root = Path(repository_root).resolve() if repository_root is not None else factory_repository_root()
    return root / "data" / "output" / "Pixellab" / "asset-name-manifest.json"


def pixellab_transaction_path(atlas_sha256: str, repository_root: str | Path | None = None) -> Path:
    """Return the transaction record beside PixelLab assets, outside solver state."""
    if not _SHA256.fullmatch(str(atlas_sha256)):
        raise OwnerArtStorageError("PixelLab atlas digest is invalid")
    paths = owner_art_paths(repository_root)
    return paths["pixellab_transactions"] / f"pixellab-atlas-{atlas_sha256}.json"


def _load_pixellab_name_map(repository_root: Path) -> dict[str, Any]:
    path = pixellab_asset_name_manifest(repository_root)
    if not path.exists():
        return {"schema": "scrubbots-pixellab-asset-names/v1", "version": 1, "atlases": {}, "sprites": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnerArtStorageError("PixelLab stable-name manifest is unreadable") from exc
    if (not isinstance(value, dict) or value.get("schema") != "scrubbots-pixellab-asset-names/v1"
            or value.get("version") != 1 or not isinstance(value.get("atlases"), dict)
            or not isinstance(value.get("sprites"), dict)):
        raise OwnerArtStorageError("PixelLab stable-name manifest has an invalid schema")
    return value


def _next_asset_name(records: Mapping[str, Any], prefix: str) -> str:
    highest = 0
    for item in records.values():
        filename = item.get("filename") if isinstance(item, Mapping) else None
        match = re.fullmatch(rf"{re.escape(prefix)}([0-9]{{6,}})\.png", str(filename or ""))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{prefix}{highest + 1:06d}.png"


def _save_pixellab_name_map(repository_root: Path, value: Mapping[str, Any]) -> None:
    path = pixellab_asset_name_manifest(repository_root)
    if _is_reparse_point(path):
        raise OwnerArtStorageError("PixelLab stable-name manifest is a reparse point")
    raw = (json.dumps(dict(value), ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{os.urandom(6).hex()}.partial")
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


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


def validate_owner_input_csv(csv_path: str | Path, *, repository_root: str | Path | None = None) -> Path:
    """Require a CSV to be a direct regular file in the canonical owner input folder."""

    candidate = Path(csv_path).expanduser()
    if not candidate.is_absolute():
        raise OwnerArtStorageError("CSV path must be absolute and selected from data/input")
    candidate = Path(os.path.abspath(candidate))
    paths = owner_art_paths(repository_root)
    root = paths["input"].parents[1]
    try:
        _verify_path_under_root(root, candidate.parent)
    except OwnerArtStorageError as exc:
        raise OwnerArtStorageError("CSV path is outside the canonical data/input directory or contains a reparse point") from exc
    if candidate.parent != paths["input"] or candidate.suffix.lower() != ".csv":
        raise OwnerArtStorageError("CSV must be a direct .csv file in the canonical data/input directory")
    if _is_reparse_point(candidate):
        raise OwnerArtStorageError("canonical data/input CSV must not be a symlink or reparse point")
    if not candidate.is_file():
        raise OwnerArtStorageError("canonical data/input CSV is missing or not a regular file")
    return candidate


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _image_dimensions(raw: bytes, label: str) -> tuple[int, int]:
    try:
        with Image.open(BytesIO(raw)) as image:
            if image.format != "PNG":
                raise OwnerArtStorageError(f"{label} is not a PNG image")
            image.verify()
        with Image.open(BytesIO(raw)) as image:
            return image.size
    except OwnerArtStorageError:
        raise
    except Exception as exc:
        raise OwnerArtStorageError(f"{label} failed PNG integrity validation") from exc


def _dimension_pair(value: object, label: str) -> tuple[int, int]:
    if isinstance(value, Mapping):
        width, height = value.get("width"), value.get("height")
    elif isinstance(value, (list, tuple)) and len(value) == 2:
        width, height = value
    else:
        raise OwnerArtStorageError(f"{label} dimensions are invalid")
    if type(width) is not int or type(height) is not int or not 51 <= width <= 59 or not 51 <= height <= 59:
        raise OwnerArtStorageError(f"{label} dimensions are outside the approved 51..59 range")
    return width, height


def _write_atlas_transaction(path: Path, value: Mapping[str, Any], *, finalized: bool) -> None:
    payload_value = dict(value)
    payload_value["state"] = "FINALIZED" if finalized else "IN_PROGRESS"
    payload = (json.dumps(payload_value, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if _is_reparse_point(path):
        raise OwnerArtStorageError("PixelLab transaction manifest path is a reparse point")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise OwnerArtStorageError("PixelLab transaction manifest is unreadable") from exc
        if not isinstance(existing, dict) or any(existing.get(key) != payload_value.get(key) for key in value):
            raise OwnerArtStorageError("PixelLab transaction manifest conflicts with the current atlas identity")
        if existing.get("state") == "FINALIZED" and not finalized:
            return
        if finalized and existing.get("state") == "FINALIZED":
            if path.read_bytes() != payload:
                raise OwnerArtStorageError("finalized PixelLab transaction manifest bytes conflict")
            return
        if existing.get("state") not in {"IN_PROGRESS", "FINALIZED"}:
            raise OwnerArtStorageError("PixelLab transaction manifest has an invalid state")
        temporary = path.with_name(f".{path.name}.{os.getpid()}.{os.urandom(6).hex()}.partial")
        try:
            with temporary.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        return
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{os.urandom(6).hex()}.partial")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    except FileExistsError:
        raise OwnerArtStorageError("concurrent PixelLab transaction manifest already exists") from None
    finally:
        temporary.unlink(missing_ok=True)


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
    canonical_root = Path(repository_root).resolve() if repository_root is not None else factory_repository_root()
    name_map = _load_pixellab_name_map(canonical_root)
    atlas_entry = name_map["atlases"].get(atlas_sha)
    if atlas_entry is None:
        atlas_name = _next_asset_name(name_map["atlases"], "PX-ATLAS-")
        atlas_entry = {"filename": atlas_name, "sha256": atlas_sha, "original_filename": "", "dimensions": None}
        name_map["atlases"][atlas_sha] = atlas_entry
    elif not isinstance(atlas_entry, Mapping) or atlas_entry.get("sha256") != atlas_sha:
        raise OwnerArtStorageError("PixelLab atlas stable-name identity conflicts with its SHA-256")
    source_root = Path(output_directory).resolve()
    original = source_root / "original-atlas.png"
    if _is_reparse_point(original) or not original.is_file():
        raise OwnerArtStorageError("PixelLab original atlas is missing or unsafe")
    atlas_bytes = original.read_bytes()
    if _hash(atlas_bytes) != atlas_sha:
        raise OwnerArtStorageError("PixelLab original atlas does not match its manifest")
    atlas_dimensions = _image_dimensions(atlas_bytes, "PixelLab original atlas")
    width, height = _dimension_pair(manifest.get("frame_dimensions"), "PixelLab frame")
    if atlas_dimensions != (4 * width, 4 * height):
        raise OwnerArtStorageError("PixelLab atlas dimensions do not match the exact 4x4 frame geometry")
    declared_atlas = manifest.get("source_dimensions")
    if declared_atlas is not None and declared_atlas != list(atlas_dimensions):
        raise OwnerArtStorageError("PixelLab atlas dimensions do not match the export manifest")

    with Image.open(BytesIO(atlas_bytes)) as atlas_image:
        atlas_rgba = atlas_image.convert("RGBA")
    prepared: list[dict[str, Any]] = []
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
        if _image_dimensions(slice_bytes, f"PixelLab slice {index}") != (width, height):
            raise OwnerArtStorageError("PixelLab slice dimensions do not match the declared frame size")
        with Image.open(BytesIO(slice_bytes)) as slice_image:
            slice_rgba = slice_image.convert("RGBA")
        x = ((index - 1) % 4) * width
        y = ((index - 1) // 4) * height
        if slice_rgba.tobytes() != atlas_rgba.crop((x, y, x + width, y + height)).tobytes():
            raise OwnerArtStorageError("PixelLab slice pixels or alpha do not match the row-major source atlas cell")
        sprite_key = f"{atlas_sha}:{index:02d}"
        sprite_entry = name_map["sprites"].get(sprite_key)
        if sprite_entry is None:
            target_name = _next_asset_name(name_map["sprites"], "LF-")
            sprite_entry = {"filename": target_name, "sha256": frame_sha, "atlas_sha256": atlas_sha, "index": index, "original_filename": filename, "dimensions": [width, height]}
            name_map["sprites"][sprite_key] = sprite_entry
        else:
            if (not isinstance(sprite_entry, Mapping) or sprite_entry.get("sha256") != frame_sha
                    or sprite_entry.get("atlas_sha256") != atlas_sha or sprite_entry.get("index") != index):
                raise OwnerArtStorageError("PixelLab sprite stable-name identity conflicts with its parent atlas")
            target_name = str(sprite_entry.get("filename", ""))
        if Path(target_name).name != target_name or not re.fullmatch(r"LF-[0-9]{6,}\.png", target_name):
            raise OwnerArtStorageError("PixelLab sprite stable filename is malformed")
        target = paths["pixellab_final"] / target_name
        if _is_reparse_point(target):
            raise OwnerArtStorageError("PixelLab Final slice target is a symlink or reparse point")
        if target.exists() and (not target.is_file() or _hash(target.read_bytes()) != frame_sha):
            raise OwnerArtStorageError("content-addressed PixelLab Final target has conflicting bytes")
        prepared.append({"index": index, "sha256": frame_sha, "filename": target_name, "path": target, "bytes": slice_bytes})
        seen.add(index)
    if seen != set(range(1, 17)):
        raise OwnerArtStorageError("PixelLab export is missing a row-major slice")
    prepared.sort(key=lambda item: int(item["index"]))

    atlas_target_name = str(atlas_entry.get("filename", ""))
    if Path(atlas_target_name).name != atlas_target_name or not re.fullmatch(r"PX-ATLAS-[0-9]{6,}\.png", atlas_target_name):
        raise OwnerArtStorageError("PixelLab atlas stable filename is malformed")
    atlas_target = paths["pixellab_grid_files"] / atlas_target_name
    if atlas_target.exists() and (not atlas_target.is_file() or _hash(atlas_target.read_bytes()) != atlas_sha):
        raise OwnerArtStorageError("content-addressed PixelLab atlas target has conflicting bytes")
    transaction = {
        "schema": "scrubbots-pixellab-atlas-transaction/v1",
        "source_atlas_sha256": atlas_sha,
        "source_kind": source_kind,
        "frame_dimensions": [width, height],
        "atlas_dimensions": list(atlas_dimensions),
        "atlas_filename": atlas_target.name,
        "slices": [{key: item[key] for key in ("index", "sha256", "filename")} for item in prepared],
    }
    transaction_path = pixellab_transaction_path(atlas_sha, canonical_root)
    _write_atlas_transaction(transaction_path, transaction, finalized=False)

    created_targets: list[Path] = []
    finalized = False
    try:
        if not atlas_target.exists():
            _write_content_addressed(paths["pixellab_grid_files"], atlas_target.name, atlas_bytes, atlas_sha)
            created_targets.append(atlas_target)
        slices: list[dict[str, Any]] = []
        for item in prepared:
            target = item["path"]
            if not target.exists():
                _write_content_addressed(paths["pixellab_final"], item["filename"], item["bytes"], item["sha256"])
                created_targets.append(target)
            slices.append({"index": item["index"], "sha256": item["sha256"], "path": str(target)})
        atlas_entry["dimensions"] = list(atlas_dimensions)
        atlas_entry["original_filename"] = original.name
        _save_pixellab_name_map(canonical_root, name_map)
        record = {
            "schema": "scrubbots-owner-pixellab-atlas-catalog/v1",
            "source_atlas_sha256": atlas_sha,
            "source_kind": source_kind,
            "atlas_path": str(atlas_target),
            "frame_dimensions": [width, height],
            "palette_enforcement": "FULL_V3_TARGET_PALETTE_AND_PER_FRAME_LOCAL_VALIDATION",
            "slices": slices,
        }
        record_path = source_root / "owner-catalog.json"
        encoded = (json.dumps(record, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        if _is_reparse_point(record_path):
            raise OwnerArtStorageError("PixelLab atlas catalog target is a symlink or reparse point")
        if record_path.exists():
            if record_path.read_bytes() != encoded:
                raise OwnerArtStorageError("PixelLab atlas catalog record conflicts with existing bytes")
        else:
            descriptor, temporary_name = tempfile.mkstemp(prefix=f".{atlas_sha}.", suffix=".partial", dir=source_root)
            temporary = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(encoded)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.link(temporary, record_path)
            except FileExistsError:
                if record_path.read_bytes() != encoded:
                    raise OwnerArtStorageError("concurrent PixelLab atlas catalog conflicts")
            finally:
                temporary.unlink(missing_ok=True)
        _write_atlas_transaction(transaction_path, transaction, finalized=True)
        finalized = True
        return {**record, "catalog_path": str(record_path), "transaction_path": str(transaction_path), "transaction_state": "FINALIZED"}
    except Exception:
        if not finalized:
            for created in reversed(created_targets):
                try:
                    if created.is_file() and not _is_reparse_point(created):
                        created.unlink()
                except OSError:
                    pass
        raise


__all__ = ["OwnerArtStorageError", "archive_pixellab_export", "ensure_owner_art_layout", "factory_repository_root", "owner_art_paths", "validate_owner_input_csv"]
