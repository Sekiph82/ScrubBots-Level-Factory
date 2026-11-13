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
PROJECT_SHA256 = "81c36123d8a368226e7d9764bce5ad6de9d2d057054eef9f133ba37b0abae617"
RUNTIME_KIND = "LF_PINNED_SOURCE_MINIMAL_RUNTIME"
MAX_RUNTIME_SOURCE_FILES = 400

# Every attested runtime the Factory has solved with. New solves use
# PINNED_MAIN_SHA; existing READY evidence keeps being verified with the exact
# runtime its run recorded (primary.authority.git_head).
ATTESTED_RUNTIMES: dict[str, dict[str, Any]] = {
    # 2026-10-12 pin. Its commit and VOID anchor were later rewritten out of the
    # game history; the attested source bytes stay the authority for its runs.
    "aef60a616d4ac401e9dfac15df6fe56e671c0053": {
        "tree_sha": "ac2dc5e22991f30db1e7a4a546ba4261b8ef6841",
        "attestation_sha256": "1761f5a78ebe582a11202ab4016b17a1db240692e66dce156616b7aa7543814c",
        "source_files": 232,
        "source_bytes": 1_977_597,
        "void_anchor": "7d0d148b8609ec04852fdee02f6b8ef37598c616",
    },
    # Owner decision 2026-11-12: re-pin to game main dd54007a (ADR-030 D2 drops the
    # 25%-of-board ratio). VOID anchor = 0b6dfc35 "audit(void): close SB-VOID-C001".
    "dd54007abb59863bc753c1a029b9db227fb4f89f": {
        "tree_sha": "38c3a7c9953355bac446687056b43c63fb64b011",
        "attestation_sha256": "3d6813513263a023c2f10d94763106b3302f4fd5a2a2a70f66eabb6c123a465e",
        "source_files": 283,
        "source_bytes": 2_535_120,
        "void_anchor": "0b6dfc359d3bf34afa4e78d53a68b788088a863a",
    },
    # Owner decision 2026-11-13: re-pin to game 6534537c (faster ProofKernel and
    # Difficulty V1 with byte-identical output; also carries the slot pop hold
    # 628ab240 that real play already used). Same VOID anchor as dd54007a.
    "6534537ceb4c71c63286614b74e4801145d5fb4d": {
        "tree_sha": "96a9806e94d80a51905680bd45f7a2fb4f2c0ab2",
        "attestation_sha256": "1e41805de360e81814ed262d19e28dd89c85a039192f4ebe3179fc1c5d48c45e",
        "source_files": 283,
        "source_bytes": 2_540_029,
        "void_anchor": "0b6dfc359d3bf34afa4e78d53a68b788088a863a",
    },
}
PINNED_MAIN_SHA = "6534537ceb4c71c63286614b74e4801145d5fb4d"
PINNED_TREE_SHA = ATTESTED_RUNTIMES[PINNED_MAIN_SHA]["tree_sha"]
ATTESTATION_SHA256 = ATTESTED_RUNTIMES[PINNED_MAIN_SHA]["attestation_sha256"]
RUNTIME_SOURCE_BYTES = ATTESTED_RUNTIMES[PINNED_MAIN_SHA]["source_bytes"]
RUNTIME_SOURCE_FILES = ATTESTED_RUNTIMES[PINNED_MAIN_SHA]["source_files"]
AUDITED_VOID_COMMIT = ATTESTED_RUNTIMES[PINNED_MAIN_SHA]["void_anchor"]
_SOURCE_PATH = re.compile(r"(?:scripts/.+\.gd|data/(?:config|palettes)/[^/]+\.json)\Z")
_PROOF_DOCS = {"docs/05_TECH_DECISIONS.md", "docs/03_LEVEL_DATA_SPEC.md"}


class PinnedGameSourceError(ValueError):
    """The attested mini runtime is missing, altered, or outside its authority."""


def repository_root() -> Path:
    # The attested runtime lives in the canonical checkout's data/, never beside
    # an installed Release copy of this module.
    from ..owner_art_storage import factory_repository_root

    return factory_repository_root(__file__)


def runtime_root(commit: str) -> Path:
    from ..owner_art_storage import owner_art_paths

    if commit not in ATTESTED_RUNTIMES:
        raise PinnedGameSourceError(f"game commit {commit[:12]} has no attested Factory runtime")
    return owner_art_paths(repository_root())["runtime"] / commit


def expected_runtime_root() -> Path:
    """The runtime new solves use."""
    return runtime_root(PINNED_MAIN_SHA)


def runtime_root_for_run(primary: Any) -> Path:
    """The runtime an existing run was solved with, from its recorded authority."""
    authority = primary.get("authority", {}) if isinstance(primary, dict) else {}
    commit = authority.get("git_head") if isinstance(authority, dict) else None
    return runtime_root(commit) if commit in ATTESTED_RUNTIMES else expected_runtime_root()


def _attested_commit(project: str | Path) -> str | None:
    root = Path(project).expanduser().resolve()
    if root.name in ATTESTED_RUNTIMES and root == runtime_root(root.name).resolve():
        return root.name
    return None


def is_pinned_runtime(project: str | Path) -> bool:
    try:
        return _attested_commit(project) is not None
    except (OSError, RuntimeError, PinnedGameSourceError):
        return False


def verify_attested_runtime(project: str | Path) -> dict[str, Any]:
    """Revalidate the complete pinned source manifest before every runtime use."""

    root = Path(project).expanduser().resolve()
    commit = _attested_commit(root)
    if commit is None:
        raise PinnedGameSourceError("pinned runtime path is not a canonical data/Level Factory/Runtime/<attested commit> directory")
    expected = ATTESTED_RUNTIMES[commit]
    if root.is_symlink() or not (root / "project.godot").is_file():
        raise PinnedGameSourceError("pinned runtime project is missing or redirected")
    manifest_path = root / "source-attestation.json"
    try:
        manifest_raw = manifest_path.read_bytes()
        project_raw = (root / "project.godot").read_bytes()
        manifest = json.loads(manifest_raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PinnedGameSourceError("pinned runtime attestation is unreadable") from exc
    if hashlib.sha256(manifest_raw).hexdigest() != expected["attestation_sha256"]:
        raise PinnedGameSourceError("pinned runtime attestation digest mismatch")
    if hashlib.sha256(project_raw).hexdigest() != PROJECT_SHA256:
        raise PinnedGameSourceError("minimal Godot project configuration digest mismatch")
    if not isinstance(manifest, dict):
        raise PinnedGameSourceError("pinned runtime attestation must be an object")
    if (
        manifest.get("schema") != "lf-pinned-game-source-attestation/v1"
        or manifest.get("runtime_kind") != RUNTIME_KIND
        or manifest.get("repository") != REPOSITORY
        or manifest.get("source_commit") != commit
        or manifest.get("source_branch") != "main"
        or manifest.get("verified_main_at_task_start") is not True
        or manifest.get("tree_sha") != expected["tree_sha"]
        or manifest.get("tree_truncated") is not False
        or manifest.get("full_game_checkout_verified") is not False
    ):
        raise PinnedGameSourceError("pinned runtime source authority fields are invalid")
    compare = manifest.get("void_compare")
    if not isinstance(compare, dict) or (
        compare.get("merge_base") != expected["void_anchor"]
        or compare.get("behind_by") != 0
        or compare.get("status") not in {"ahead", "identical"}
    ):
        raise PinnedGameSourceError("pinned runtime does not attest the audited VOID ancestor")
    files = manifest.get("source_files")
    if not isinstance(files, list) or len(files) != expected["source_files"]:
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
    if total_bytes != expected["source_bytes"] or total_bytes > 8 * 1024 * 1024 or len(seen) > MAX_RUNTIME_SOURCE_FILES:
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
    "ATTESTED_RUNTIMES",
    "AUDITED_VOID_COMMIT",
    "PINNED_MAIN_SHA",
    "PINNED_TREE_SHA",
    "PinnedGameSourceError",
    "RUNTIME_KIND",
    "expected_runtime_root",
    "runtime_root",
    "runtime_root_for_run",
    "is_pinned_runtime",
    "verify_attested_runtime",
]
