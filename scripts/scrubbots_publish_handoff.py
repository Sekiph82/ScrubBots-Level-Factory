"""Owner-facing handoff into the M14 ScrubBots Content Pipeline.

This module owns selection/preflight presentation only. It never writes R2 or
the game repository; all mutations are delegated to the existing M14 runner.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
for _SOURCE_ROOT in (_REPOSITORY_ROOT / "src", _REPOSITORY_ROOT / "content_pipeline" / "src"):
    if str(_SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(_SOURCE_ROOT))

R2_BUCKET = "scrubbots-content-prod"
PUBLIC_READ_BASE = "https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev"
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def publish_preflight(
    request: Mapping[str, Any], *,
    release_pool_reader: Callable[[], Sequence[Mapping[str, Any]]] | None = None,
    pack_builder: Callable[..., Any] | None = None,
    game_authority_reader: Callable[[], str] | None = None,
) -> dict[str, Any]:
    """Build a byte-exact preview from current owner-accepted Release Pool entries."""
    candidate_ids = request.get("candidate_ids")
    pack_id = request.get("pack_id")
    content_version = request.get("content_version")
    game_sha = request.get("scrubbots_main_sha")
    created_at = request.get("created_at_utc")
    if (not isinstance(candidate_ids, list) or not candidate_ids
            or any(not isinstance(item, str) or not item for item in candidate_ids)
            or len(set(candidate_ids)) != len(candidate_ids)):
        return _blocked("AWAITING_OWNER_RELEASE_BATCH", "Select one or more current owner-accepted Release Pool entries.")
    if (not isinstance(pack_id, str) or not pack_id or type(content_version) is not int
            or content_version < 1 or not isinstance(game_sha, str) or not _GIT_SHA.fullmatch(game_sha)
            or not isinstance(created_at, str)):
        return _blocked("PREFLIGHT_INPUT_INVALID", "Pack identity, content version, UTC timestamp, and exact ScrubBots main SHA are required.")
    try:
        if release_pool_reader is None:
            from .release_pool import release_entries
            release_pool_reader = release_entries
        entries = tuple(release_pool_reader())
        current = {str(entry.get("candidate_id")): entry for entry in entries}
        if not set(candidate_ids).issubset(current):
            return _blocked("AWAITING_OWNER_RELEASE_BATCH", "Selection is not entirely present in the current owner-accepted Release Pool.")
        try:
            current_game_sha = game_authority_reader() if game_authority_reader else _configured_scrubbots_main_sha()
        except Exception:
            return _blocked("SCRUBBOTS_MAIN_UNAVAILABLE", "The configured canonical game main checkout could not be verified.")
        if current_game_sha != game_sha:
            return _blocked("SCRUBBOTS_MAIN_SHA_MISMATCH", "The supplied SHA does not match the verified current local main checkout.")
        if pack_builder is None:
            import importlib.util
            root = _REPOSITORY_ROOT
            adapter_path = root / "scripts" / "build_accepted_factory_output_pack.py"
            spec = importlib.util.spec_from_file_location("_factory_pack_adapter", adapter_path)
            if spec is None or spec.loader is None:
                raise RuntimeError("Factory pack adapter unavailable")
            adapter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(adapter)
            pack_builder = adapter.build_accepted_factory_output_pack
        build = pack_builder(tuple(candidate_ids), pack_id=pack_id, pack_version=content_version,
                             created_at_utc=created_at)
    except Exception:
        return _blocked("PREFLIGHT_REJECTED", "Current owner review, READY pipeline, source bytes, or solver proof failed revalidation.")
    evidence = build.evidence
    if len(evidence.level_ids) == 0:
        return _blocked("PREFLIGHT_REJECTED", "The deterministic pack contains no levels.")
    return {
        "operation": "scrubbots-publish",
        "state": "PREFLIGHT_READY",
        "mutation_performed": False,
        "content_version": content_version,
        "candidate_ids": list(candidate_ids),
        "level_ids": list(evidence.level_ids),
        "pack_ids": [evidence.pack_id],
        "packs": [{"pack_id": evidence.pack_id, "sha256": evidence.archive_sha256,
                    "byte_length": evidence.archive_byte_length}],
        "scrubbots_main_sha": game_sha,
        "bucket": R2_BUCKET,
        "public_read_base": PUBLIC_READ_BASE,
        "production": "AWAITING_OWNER_PRODUCTION_PROMOTION",
    }


def run_m14_handoff(
    publisher_request: object, *,
    publisher_runner: Callable[[object], object] | None = None,
    provider_factory: Callable[[], object] | None = None,
) -> dict[str, Any]:
    """Delegate an already assembled explicit request to the canonical M14 runner."""
    try:
        from scrubbots_content_pipeline.one_command_publisher import (
            PublisherMode, PublisherRunRequest, run_one_command_publisher,
        )
        from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider
    except Exception:
        return _blocked("M14_PUBLISHER_UNAVAILABLE", "The canonical M14 publisher is unavailable in this runtime.")
    if not isinstance(publisher_request, PublisherRunRequest):
        return _blocked("M14_REQUEST_REQUIRED", "A complete M14 PublisherRunRequest must be assembled from the reviewed preflight.")
    if publisher_request.mode not in {PublisherMode.STAGING_ONLY, PublisherMode.PRODUCTION}:
        return _blocked("M14_MODE_REJECTED", "Handoff requires the M14 staging or separately approved production mode.")
    if publisher_request.mode is PublisherMode.STAGING_ONLY:
        env = os.environ
        if not all(env.get(name, "").strip() for name in
                   ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")):
            return _blocked("OWNER_R2_WRITE_CREDENTIAL_REQUIRED", "Secure R2 writer credentials are not available to this process.")
    provider = publisher_request.provider
    request_to_run = publisher_request
    if provider_factory is not None:
        provider = provider_factory()
        from dataclasses import replace
        request_to_run = replace(publisher_request, provider=provider)
    if provider is None or (provider_factory is None and not isinstance(provider, CloudflareR2Provider)):
        return _blocked("R2_PROVIDER_REQUIRED", "The M14 request must use the Cloudflare R2 provider adapter.")
    if publisher_runner is None:
        publisher_runner = run_one_command_publisher
    report = publisher_runner(request_to_run)
    to_dict = getattr(report, "to_dict", None)
    payload = to_dict() if callable(to_dict) else {"accepted": bool(getattr(report, "accepted", False))}
    return {"operation": "scrubbots-publish", "state": "M14_COMPLETED" if payload.get("accepted") else "M14_REJECTED",
            "m14": payload, "receipt": _receipt(payload)}


def _receipt(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic, secret-free reference to the M14 result."""
    identity = f"{report.get('candidate_manifest_sha256') or ''}:{report.get('production_manifest_sha256') or ''}:{report.get('reason_code') or ''}"
    return {"schema": "scrubbots.publish.receipt.v1", "idempotency_key": hashlib.sha256(identity.encode()).hexdigest(),
            "accepted": report.get("accepted") is True,
            "candidate_manifest_sha256": report.get("candidate_manifest_sha256"),
            "production_manifest_sha256": report.get("production_manifest_sha256")}


def _blocked(state: str, reason: str) -> dict[str, Any]:
    return {"operation": "scrubbots-publish", "state": state, "reason": reason,
            "mutation_performed": False, "bucket": R2_BUCKET, "public_read_base": PUBLIC_READ_BASE}


def _configured_scrubbots_main_sha() -> str:
    project = os.environ.get("SCRUBBOTS_PROJECT", "").strip()
    if not project:
        raise ValueError("SCRUBBOTS_PROJECT is not configured")
    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", project, *args], check=True, capture_output=True,
                              text=True, timeout=15).stdout.strip()
    origin = git("config", "--get", "remote.origin.url").lower().removesuffix(".git")
    if origin not in {"https://github.com/sekiph82/scrubbots", "git@github.com:sekiph82/scrubbots"}:
        raise ValueError("configured game repository identity mismatch")
    if git("branch", "--show-current") != "main":
        raise ValueError("configured game checkout is not main")
    commit = git("rev-parse", "HEAD").lower()
    if not _GIT_SHA.fullmatch(commit):
        raise ValueError("configured game commit is invalid")
    return commit


__all__ = ["PUBLIC_READ_BASE", "R2_BUCKET", "publish_preflight", "run_m14_handoff"]
