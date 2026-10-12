"""Integrity gate for the one owner-authorized GitHub-pinned mini runtime.

This is an offline level-generation authority only. It never grants the
separate full-game checkout or production-publication authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


REPOSITORY = "Sekiph82/Scrubbots"
PINNED_MAIN_SHA = "aef60a616d4ac401e9dfac15df6fe56e671c0053"
PINNED_TREE_SHA = "ac2dc5e22991f30db1e7a4a546ba4261b8ef6841"
ATTESTATION_SHA256 = "1761f5a78ebe582a11202ab4016b17a1db240692e66dce156616b7aa7543814c"
PROJECT_SHA256 = "81c36123d8a368226e7d9764bce5ad6de9d2d057054eef9f133ba37b0abae617"
RUNTIME_KIND = "LF_PINNED_SOURCE_MINIMAL_RUNTIME"
RUNTIME_SOURCE_BYTES = 1_977_597
RUNTIME_SOURCE_FILES = 232
AUDITED_VOID_COMMIT = "7d0d148b8609ec04852fdee02f6b8ef37598c616"
_SOURCE_PATH = re.compile(r"(?:scripts/.+\.gd|data/(?:config|palettes)/[^/]+\.json)\Z")
_PROOF_DOCS = {"docs/05_TECH_DECISIONS.md", "docs/03_LEVEL_DATA_SPEC.md"}


class PinnedGameSourceError(ValueError):
    """The attested mini runtime is missing, altered, or outside its authority."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def expected_runtime_root() -> Path:
    return repository_root() / "level_factory" / "output" / "current-game-runtime" / PINNED_MAIN_SHA


def is_pinned_runtime(project: str | Path) -> bool:
    try:
        return Path(project).expanduser().resolve() == expected_runtime_root().resolve()
    except (OSError, RuntimeError):
        return False


def verify_attested_runtime(project: str | Path) -> dict[str, Any]:
    """Revalidate the complete pinned source manifest before every runtime use."""

    root = Path(project).expanduser().resolve()
    if root != expected_runtime_root().resolve():
        raise PinnedGameSourceError("pinned runtime path is not the task-owned LF output directory")
    if root.is_symlink() or not (root / "project.godot").is_file():
        raise PinnedGameSourceError("pinned runtime project is missing or redirected")
    manifest_path = root / "source-attestation.json"
    try:
        manifest_raw = manifest_path.read_bytes()
        project_raw = (root / "project.godot").read_bytes()
        manifest = json.loads(manifest_raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PinnedGameSourceError("pinned runtime attestation is unreadable") from exc
    if hashlib.sha256(manifest_raw).hexdigest() != ATTESTATION_SHA256:
        raise PinnedGameSourceError("pinned runtime attestation digest mismatch")
    if hashlib.sha256(project_raw).hexdigest() != PROJECT_SHA256:
        raise PinnedGameSourceError("minimal Godot project configuration digest mismatch")
    if not isinstance(manifest, dict):
        raise PinnedGameSourceError("pinned runtime attestation must be an object")
    if (
        manifest.get("schema") != "lf-pinned-game-source-attestation/v1"
        or manifest.get("runtime_kind") != RUNTIME_KIND
        or manifest.get("repository") != REPOSITORY
        or manifest.get("source_commit") != PINNED_MAIN_SHA
        or manifest.get("source_branch") != "main"
        or manifest.get("verified_main_at_task_start") is not True
        or manifest.get("tree_sha") != PINNED_TREE_SHA
        or manifest.get("tree_truncated") is not False
        or manifest.get("full_game_checkout_verified") is not False
    ):
        raise PinnedGameSourceError("pinned runtime source authority fields are invalid")
    compare = manifest.get("void_compare")
    if not isinstance(compare, dict) or (
        compare.get("merge_base") != AUDITED_VOID_COMMIT
        or compare.get("behind_by") != 0
        or compare.get("status") not in {"ahead", "identical"}
    ):
        raise PinnedGameSourceError("pinned runtime does not attest the audited VOID ancestor")
    files = manifest.get("source_files")
    if not isinstance(files, list) or len(files) != RUNTIME_SOURCE_FILES:
        raise PinnedGameSourceError("pinned runtime source manifest has the wrong file count")
    seen: set[str] = set()
    total_bytes = 0
    for item in files:
        if not isinstance(item, dict):
            raise PinnedGameSourceError("pinned runtime source entry is malformed")
        relative = item.get("path")
        if type(relative) is not str or not _SOURCE_PATH.fullmatch(relative) or ".." in Path(relative).parts:
            raise PinnedGameSourceError("pinned runtime contains a disallowed source path")
        if relative in seen:
            raise PinnedGameSourceError("pinned runtime source manifest contains duplicate paths")
        seen.add(relative)
        path = root.joinpath(*relative.split("/"))
        try:
            if path.is_symlink() or not path.is_file() or path.resolve().is_relative_to(root) is False:
                raise PinnedGameSourceError(f"pinned source path is missing or redirected: {relative}")
            raw = path.read_bytes()
        except OSError as exc:
            raise PinnedGameSourceError(f"pinned source path is unreadable: {relative}") from exc
        size = item.get("bytes")
        if type(size) is not int or len(raw) != size:
            raise PinnedGameSourceError(f"pinned source byte length mismatch: {relative}")
        blob_sha = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        file_sha = hashlib.sha256(raw).hexdigest()
        if blob_sha != item.get("git_blob_sha1") or file_sha != item.get("sha256"):
            raise PinnedGameSourceError(f"pinned Git blob or SHA-256 mismatch: {relative}")
        total_bytes += len(raw)
    actual_source_paths = {
        p.relative_to(root).as_posix()
        for folder in (root / "scripts", root / "data" / "config", root / "data" / "palettes")
        if folder.exists()
        for p in folder.rglob("*")
        if p.is_file() and (p.suffix == ".gd" or p.suffix == ".json")
    }
    if actual_source_paths != seen:
        raise PinnedGameSourceError("pinned runtime source tree has missing or unmanifested script/config files")
    if total_bytes != RUNTIME_SOURCE_BYTES or total_bytes > 8 * 1024 * 1024 or len(seen) > 260:
        raise PinnedGameSourceError("pinned runtime source byte or file cap is invalid")
    docs = manifest.get("void_contract_documents")
    if not isinstance(docs, list) or {entry.get("path") for entry in docs if isinstance(entry, dict)} != _PROOF_DOCS:
        raise PinnedGameSourceError("pinned VOID ADR/spec proof is missing")
    owner = manifest.get("installed_owner_source")
    if not isinstance(owner, dict) or (
        owner.get("source_id") != "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
        or owner.get("source_sha256") != "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
        or owner.get("source_record_sha256") != "858d302c10281ab2d70d4a9e22043e4eac216ebc6b6b0d89131b6e5930c232bb"
    ):
        raise PinnedGameSourceError("pinned runtime is not bound to the authorized original owner source")
    return manifest


__all__ = [
    "ATTESTATION_SHA256",
    "AUDITED_VOID_COMMIT",
    "PINNED_MAIN_SHA",
    "PINNED_TREE_SHA",
    "PinnedGameSourceError",
    "RUNTIME_KIND",
    "expected_runtime_root",
    "is_pinned_runtime",
    "verify_attested_runtime",
]
