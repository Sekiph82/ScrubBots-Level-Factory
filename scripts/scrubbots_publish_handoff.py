"""Trusted, serializable Studio/operator handoff into the M14 STAGING publisher.

Preflight is read-only. The service owns Release Pool revalidation, exact TEMP
game authority resolution, deterministic pack rebuilding, and typed M14 request
assembly. The UI never receives provider credentials or calls R2 directly.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
for _SOURCE_ROOT in (_REPOSITORY_ROOT / "src", _REPOSITORY_ROOT / "content_pipeline" / "src"):
    if str(_SOURCE_ROOT) not in sys.path:
        sys.path.insert(0, str(_SOURCE_ROOT))

from scrubbots_content_pipeline.scrubpack_spec import normalize_created_at_utc

R2_BUCKET = "scrubbots-content-prod"
PUBLIC_READ_BASE = "https://pub-dd36dd94999d4beaad95d6409ad0167e.r2.dev"
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_KEY = "manifests/current.json"


def publish_preflight(
    request: Mapping[str, Any], *,
    release_pool_reader: Callable[[], Sequence[Mapping[str, Any]]] | None = None,
    pack_builder: Callable[..., Any] | None = None,
    game_authority_reader: Callable[[], Mapping[str, object]] | None = None,
) -> dict[str, Any]:
    """Return mutation-free, deterministic review data from current authority."""
    candidate_ids = request.get("candidate_ids")
    pack_id = request.get("pack_id")
    content_version = request.get("content_version")
    created_at = request.get("created_at_utc")
    if (not isinstance(candidate_ids, list) or not candidate_ids
            or any(not isinstance(item, str) or not item for item in candidate_ids)
            or len(set(candidate_ids)) != len(candidate_ids)):
        return _blocked("AWAITING_OWNER_RELEASE_BATCH", "Select one or more current owner-accepted Release Pool entries.")
    if (not isinstance(pack_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", pack_id)
            or type(content_version) is not int or content_version < 2
            or not isinstance(created_at, str)):
        return _blocked("PREFLIGHT_INPUT_INVALID", "Pack identity, content version, and canonical UTC timestamp are required.")
    try:
        created_at = normalize_created_at_utc(created_at)
    except ValueError:
        return _blocked("PREFLIGHT_INPUT_INVALID", "created_at_utc must be an explicit timezone-aware whole-second instant.")
    try:
        entries = tuple(_release_entries(release_pool_reader))
        current = {str(entry.get("candidate_id")): entry for entry in entries if _valid_pool_entry(entry)}
        if not set(candidate_ids).issubset(current):
            return _blocked("AWAITING_OWNER_RELEASE_BATCH", "Selection is not entirely present in the current owner-accepted Release Pool.")
        authority = (game_authority_reader or _resolve_game_authority)()
        game_sha = authority.get("commit")
        if (authority.get("repository") != "Sekiph82/Scrubbots" or authority.get("branch") != "main"
                or not isinstance(game_sha, str) or not _GIT_SHA.fullmatch(game_sha)):
            return _blocked("SCRUBBOTS_MAIN_UNAVAILABLE", "The exact current TEMP ScrubBots main authority could not be verified.")
        build = _build_pack(candidate_ids, pack_id, content_version, created_at, pack_builder)
    except Exception:
        return _blocked("PREFLIGHT_REJECTED", "Current owner review, READY pipeline, source bytes, solver proof, or game authority failed revalidation.")
    evidence = build.evidence
    if not evidence.level_ids:
        return _blocked("PREFLIGHT_REJECTED", "The deterministic pack contains no levels.")
    identity_fields = {
        "schema": "scrubbots.publish.review.v1",
        "candidate_ids": list(candidate_ids),
        "content_version": content_version,
        "created_at_utc": created_at,
        "packs": [{"pack_id": evidence.pack_id, "sha256": evidence.archive_sha256,
                   "byte_length": evidence.archive_byte_length}],
        "scrubbots_main_sha": game_sha,
        "bucket": R2_BUCKET,
        "public_read_base": PUBLIC_READ_BASE,
    }
    identity = {**identity_fields, "sha256": _digest(identity_fields)}
    return {
        "operation": "scrubbots-publish", "state": "PREFLIGHT_READY",
        "mutation_performed": False, "content_version": content_version,
        "candidate_ids": list(candidate_ids), "level_ids": list(evidence.level_ids),
        "pack_ids": [evidence.pack_id], "packs": identity_fields["packs"],
        "scrubbots_main_sha": game_sha, "game_authority": dict(authority),
        "bucket": R2_BUCKET, "public_read_base": PUBLIC_READ_BASE,
        "reviewed_identity": identity,
        "production": "AWAITING_OWNER_PRODUCTION_PROMOTION",
    }


def publish_to_staging(
    request: Mapping[str, Any], *,
    release_pool_reader: Callable[[], Sequence[Mapping[str, Any]]] | None = None,
    pack_builder: Callable[..., Any] | None = None,
    game_authority_reader: Callable[[], Mapping[str, object]] | None = None,
    provider_factory: Callable[[], object] | None = None,
    publisher_runner: Callable[[object], object] | None = None,
) -> dict[str, Any]:
    """Revalidate a reviewed serializable request, assemble typed M14, and run it."""
    reviewed = request.get("reviewed_identity")
    if not isinstance(reviewed, Mapping):
        return _blocked("REVIEWED_PREFLIGHT_REQUIRED", "A successful exact preflight identity is required.")
    current_request = {key: request.get(key) for key in
                       ("candidate_ids", "pack_id", "content_version", "created_at_utc")}
    fresh = publish_preflight(current_request, release_pool_reader=release_pool_reader,
                              pack_builder=pack_builder, game_authority_reader=game_authority_reader)
    if fresh.get("state") != "PREFLIGHT_READY" or fresh.get("reviewed_identity") != dict(reviewed):
        return _blocked("REVIEWED_PREFLIGHT_STALE", "Current Release Pool, pack bytes, authority, or target differs from the reviewed preflight.")
    env = os.environ
    if not all(env.get(name, "").strip() for name in
               ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")):
        return _blocked("OWNER_R2_WRITE_CREDENTIAL_REQUIRED", "Secure R2 writer credentials are not available to this process.")
    try:
        typed_request = _assemble_staging_request(
            current_request, provider_factory=provider_factory,
            release_pool_reader=release_pool_reader, pack_builder=pack_builder,
            game_authority_reader=game_authority_reader, reviewed_identity=reviewed,
        )
        from scrubbots_content_pipeline.one_command_publisher import run_one_command_publisher
        report = (publisher_runner or run_one_command_publisher)(typed_request)
    except Exception:
        return _blocked("M14_PUBLISHER_REJECTED", "Trusted M14 request assembly or publication failed closed.")
    to_dict = getattr(report, "to_dict", None)
    payload = to_dict() if callable(to_dict) else {"accepted": bool(getattr(report, "accepted", False))}
    return {
        "operation": "scrubbots-publish",
        "state": "STAGING_PUBLISHED" if payload.get("accepted") is True else "M14_REJECTED",
        "m14": payload, "receipt": _receipt(payload),
        "production": "AWAITING_OWNER_PRODUCTION_PROMOTION",
        # M14 may have uploaded immutable packs before a later rejection. Once
        # invoked, report that remote mutation may have occurred conservatively.
        "mutation_performed": True,
    }


def _assemble_staging_request(
    request: Mapping[str, Any], *, provider_factory: Callable[[], object] | None,
    release_pool_reader: Callable[[], Sequence[Mapping[str, Any]]] | None,
    pack_builder: Callable[..., Any] | None,
    game_authority_reader: Callable[[], Mapping[str, object]] | None,
    reviewed_identity: Mapping[str, object],
) -> object:
    from scrubbots_content_pipeline import (
        FactoryPackRequest, PublisherMode, PublisherRunRequest,
    )
    from scrubbots_content_pipeline.config import PipelineConfig, STAGING_TARGET
    from scrubbots_content_pipeline.manifest_v1 import CONTENT_MANIFEST_SCHEMA
    from scrubbots_content_pipeline.payload_validation import validate_remote_payload
    from scrubbots_content_pipeline.publication_plan import build_publication_plan
    from scrubbots_content_pipeline.release_state import replay_release_events
    from scrubbots_content_pipeline.staging_manifest_publish import StagingManifestPrecondition
    from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider
    provider = (provider_factory or CloudflareR2Provider)()
    ids = tuple(request["candidate_ids"])
    pack_id, version, created = str(request["pack_id"]), int(request["content_version"]), str(request["created_at_utc"])
    entries = tuple(_release_entries(release_pool_reader))
    live_ids = {str(entry.get("candidate_id")) for entry in entries if _valid_pool_entry(entry)}
    if not set(ids).issubset(live_ids):
        raise ValueError("current owner-accepted Release Pool membership changed")
    authority = (game_authority_reader or _resolve_game_authority)()
    if authority.get("commit") != reviewed_identity.get("scrubbots_main_sha"):
        raise ValueError("exact-current TEMP game authority changed after review")
    build = _build_pack(ids, pack_id, version, created, pack_builder)
    expected_packs = reviewed_identity.get("packs")
    actual_packs = [{"pack_id": build.evidence.pack_id,
                     "sha256": build.evidence.archive_sha256,
                     "byte_length": build.evidence.archive_byte_length}]
    if expected_packs != actual_packs:
        raise ValueError("deterministic pack bytes changed after review")
    if pack_builder is None:
        from scripts.build_accepted_factory_output_pack import build_accepted_factory_output_pack
        def trusted_builder(pack_request: FactoryPackRequest):
            return build_accepted_factory_output_pack(pack_request.candidate_ids,
                pack_id=pack_request.pack_id, pack_version=pack_request.pack_version,
                created_at_utc=pack_request.created_at_utc)
    else:
        trusted_builder = lambda _pack_request: build

    # M14 validates exact pack bytes; this separately supplies a validated source
    # level descriptor/payload for its release plan and reads the remote ledger.
    from scrubbots_pixel_factory.supply_pipeline.scrubpack_identity import current_solver_proof_for_candidate
    from scripts.build_accepted_factory_output_pack import _decode_object, _level_input
    pipeline_bytes, _source = current_solver_proof_for_candidate(ids[0])
    pipeline = _decode_object(pipeline_bytes, label="READY pipeline")
    _level_id, level_input = _level_input(pipeline, repository_root=_REPOSITORY_ROOT)
    descriptor = _plain_json(level_input.level_data.descriptor)
    payload_bytes = level_input.level_data.payload
    payload_check = validate_remote_payload(descriptor, payload_bytes)
    events = tuple(provider.read_release_events())
    replay = replay_release_events(events)
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload_bytes, payload_result=payload_check,
        target=STAGING_TARGET, replay=replay, current_state=None,
        capability=provider.capabilities, owner_approved=True,
    )
    precondition = StagingManifestPrecondition(
        STAGING_TARGET.logical_target_id, _MANIFEST_KEY, False, None, None, None)
    return PublisherRunRequest(
        mode=PublisherMode.STAGING_ONLY, config=PipelineConfig(), provider=provider,
        factory_pack_requests=(FactoryPackRequest(ids, pack_id, version, created),),
        factory_pack_builder=trusted_builder, content_version=version,
        previous_content_version=version - 1,
        minimum_game_version="2.4.0", current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: (1,)},
        object_keys={pack_id: f"packs/{pack_id}/v{version}.scrubpack"},
        publication_plan=plan, current_content_digest=plan.content_digest,
        owner_approved=True, staging_precondition=precondition,
        release_events=events, manifest_object_key=_MANIFEST_KEY,
    )


def _release_entries(reader):
    if reader is not None:
        return reader()
    from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries
    return release_entries()


def _valid_pool_entry(entry: object) -> bool:
    if not isinstance(entry, Mapping) or entry.get("schema") != "scrubbots-release-pool-entry/v1":
        return False
    candidate_id = entry.get("candidate_id")
    pipeline = entry.get("pipeline")
    primary = pipeline.get("primary") if isinstance(pipeline, Mapping) else None
    return (
        isinstance(candidate_id, str) and bool(candidate_id)
        and isinstance(entry.get("review_id"), str) and bool(entry["review_id"])
        and isinstance(entry.get("pipeline_run_id"), str)
        and isinstance(entry.get("pipeline_sha256"), str) and bool(_SHA256.fullmatch(entry["pipeline_sha256"]))
        and isinstance(pipeline, Mapping) and pipeline.get("candidate_id") == candidate_id
        and pipeline.get("run_id") == entry.get("pipeline_run_id")
        and pipeline.get("disposition") == "READY"
        and isinstance(primary, Mapping) and primary.get("state") == "READY"
        and primary.get("disposition") == "READY"
    )


def _build_pack(candidate_ids, pack_id, version, created, builder):
    if builder is not None:
        return builder(tuple(candidate_ids), pack_id=pack_id, pack_version=version, created_at_utc=created)
    adapter_path = _REPOSITORY_ROOT / "scripts" / "build_accepted_factory_output_pack.py"
    spec = importlib.util.spec_from_file_location("_accepted_factory_pack_adapter", adapter_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Factory pack adapter unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_accepted_factory_output_pack(
        tuple(candidate_ids), pack_id=pack_id, pack_version=version, created_at_utc=created)


def _resolve_game_authority() -> Mapping[str, object]:
    from cpx002_current_main_replay_adapter import (
        _authority_snapshot, resolve_explicit_temp_game_authority,
    )
    root = resolve_explicit_temp_game_authority()
    return _authority_snapshot(root)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _plain_json(value: object) -> Any:
    """Thaw immutable M12 mappings into canonical JSON-compatible values."""
    if isinstance(value, Mapping):
        return {str(key): _plain_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_json(item) for item in value]
    return value


def _receipt(report: Mapping[str, Any]) -> dict[str, Any]:
    identity = f"{report.get('candidate_manifest_sha256') or ''}:{report.get('production_manifest_sha256') or ''}:{report.get('reason_code') or ''}"
    return {"schema": "scrubbots.publish.receipt.v1", "idempotency_key": hashlib.sha256(identity.encode()).hexdigest(),
            "accepted": report.get("accepted") is True,
            "candidate_manifest_sha256": report.get("candidate_manifest_sha256"),
            "production_manifest_sha256": report.get("production_manifest_sha256")}


def _blocked(state: str, reason: str) -> dict[str, Any]:
    return {"operation": "scrubbots-publish", "state": state, "reason": reason,
            "mutation_performed": False, "bucket": R2_BUCKET, "public_read_base": PUBLIC_READ_BASE,
            "production": "AWAITING_OWNER_PRODUCTION_PROMOTION"}


__all__ = ["PUBLIC_READ_BASE", "R2_BUCKET", "publish_preflight", "publish_to_staging"]
