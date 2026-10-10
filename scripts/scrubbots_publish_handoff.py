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
            or (content_version is not None and (type(content_version) is not int or content_version < 2))
            or not isinstance(created_at, str)):
        return _blocked("PREFLIGHT_INPUT_INVALID", "Pack identity and canonical UTC timestamp are required.")
    try:
        created_at = normalize_created_at_utc(created_at)
    except ValueError:
        return _blocked("PREFLIGHT_INPUT_INVALID", "created_at_utc must be an explicit timezone-aware whole-second instant.")
    try:
        next_version = _next_content_version()
    except Exception:
        return _blocked("RELEASE_HISTORY_UNAVAILABLE", "Current STAGING and PRODUCTION manifests could not establish the next content version.")
    if content_version is not None and content_version != next_version:
        return _blocked("CONTENT_VERSION_STALE", "Requested content version does not match current release history.")
    content_version = next_version
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
    manifest_sha = _candidate_manifest_sha(build, content_version)
    identity_fields = {
        "schema": "scrubbots.publish.review.v1",
        "candidate_ids": list(candidate_ids),
        "content_version": content_version,
        "created_at_utc": created_at,
        "packs": [{"pack_id": evidence.pack_id, "sha256": evidence.archive_sha256,
                   "byte_length": evidence.archive_byte_length}],
        "candidate_manifest_sha256": manifest_sha,
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
        "candidate_manifest_sha256": manifest_sha,
        "scrubbots_main_sha": game_sha, "game_authority": dict(authority),
        "bucket": R2_BUCKET, "public_read_base": PUBLIC_READ_BASE,
        "reviewed_identity": identity,
        "production": "AWAITING_OWNER_PRODUCTION_PROMOTION",
    }


def publish_to_production(
    request: Mapping[str, Any], *, owner_confirmation: Mapping[str, Any],
    release_pool_reader: Callable[[], Sequence[Mapping[str, Any]]] | None = None,
    pack_builder: Callable[..., Any] | None = None,
    game_authority_reader: Callable[[], Mapping[str, object]] | None = None,
    provider_factory: Callable[[], object] | None = None,
    publisher_runner: Callable[[object], object] | None = None,
) -> dict[str, Any]:
    """Run the canonical M14 -> CP03-007 -> CPX-002 -> CP03-008/009 chain after exact owner confirmation."""
    reviewed = request.get("reviewed_identity")
    if not isinstance(reviewed, Mapping):
        return _blocked("REVIEWED_PREFLIGHT_REQUIRED", "A successful exact preflight identity is required.")
    if (not isinstance(owner_confirmation, Mapping)
            or owner_confirmation.get("confirmed") is not True
            or owner_confirmation.get("target") != "PRODUCTION"
            or owner_confirmation.get("manifest_sha256") != reviewed.get("candidate_manifest_sha256")
            or owner_confirmation.get("content_version") != reviewed.get("content_version")
            or not isinstance(owner_confirmation.get("approval_id"), str)
            or not owner_confirmation["approval_id"].strip()
            or not isinstance(owner_confirmation.get("owner_id"), str)
            or not owner_confirmation["owner_id"].strip()):
        return _blocked("EXACT_OWNER_CONFIRMATION_REQUIRED", "Owner confirmation must bind the reviewed manifest SHA-256, content version, and PRODUCTION target.")
    current_request = {key: request.get(key) for key in
                       ("candidate_ids", "pack_id", "content_version", "created_at_utc")}
    fresh = publish_preflight(current_request, release_pool_reader=release_pool_reader,
                              pack_builder=pack_builder, game_authority_reader=game_authority_reader)
    if fresh.get("state") != "PREFLIGHT_READY" or fresh.get("reviewed_identity") != dict(reviewed):
        return _blocked("REVIEWED_PREFLIGHT_STALE", "Current Release Pool, pack bytes, authority, or target differs from the reviewed preflight.")
    if (owner_confirmation.get("manifest_sha256") != fresh.get("candidate_manifest_sha256")
            or owner_confirmation.get("content_version") != fresh.get("content_version")):
        return _blocked("EXACT_OWNER_CONFIRMATION_REQUIRED", "Confirmed manifest identity no longer matches current preflight.")
    env = os.environ
    if not all(env.get(name, "").strip() for name in
               ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")):
        return _blocked("OWNER_R2_WRITE_CREDENTIAL_REQUIRED", "Secure R2 writer credentials are not available to this process.")
    try:
        from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider
        provider = (provider_factory or CloudflareR2Provider)()
        typed_request = _assemble_staging_request(
            current_request, provider_factory=lambda: provider,
            release_pool_reader=release_pool_reader, pack_builder=pack_builder,
            game_authority_reader=game_authority_reader, reviewed_identity=reviewed,
            production_confirmation=owner_confirmation,
        )
        from scrubbots_content_pipeline.one_command_publisher import run_one_command_publisher
        report = (publisher_runner or run_one_command_publisher)(typed_request)
    except Exception:
        return _blocked("M14_PRODUCTION_CHAIN_REJECTED", "Trusted M14/current-main/production authority chain failed closed.")
    to_dict = getattr(report, "to_dict", None)
    payload = to_dict() if callable(to_dict) else {"accepted": bool(getattr(report, "accepted", False))}
    history_status = None
    if payload.get("accepted") is True:
        activation = getattr(report, "production_activation", None)
        receipt = getattr(activation, "receipt", None)
        production_inputs = getattr(typed_request, "production", None)
        history = getattr(receipt, "manifest_history", None)
        manifest_bytes = getattr(receipt, "manifest_bytes", None)
        prior_history = getattr(production_inputs, "manifest_history", None)
        write_history = getattr(provider, "write_manifest_history", None)
        read_history = getattr(provider, "read_manifest_history", None)
        if (history is None or type(manifest_bytes) is not bytes or prior_history is None
                or not callable(write_history) or not callable(read_history)):
            return _post_activation_history_block(
                "PRODUCTION_HISTORY_READBACK_REQUIRED",
                "Canonical activation succeeded but the M13 durable history readback contract is unavailable.")
        try:
            persisted = write_history(
                history, expected_prior_tip_sha256=prior_history.tip_sha256,
                current_manifest_bytes=manifest_bytes,
            )
            from scrubbots_content_pipeline.provider import ProviderResultCategory
            if getattr(persisted, "category", None) is not ProviderResultCategory.SUCCESS:
                return _post_activation_history_block(
                    "PRODUCTION_HISTORY_PERSIST_FAILED",
                    "Production activated, but canonical M13 history persistence did not confirm; further promotion is blocked.")
            readback = read_history()
            if readback != history:
                return _post_activation_history_block(
                    "PRODUCTION_HISTORY_READBACK_MISMATCH",
                    "Production activated, but durable M13 history did not read back exactly.")
        except Exception:
            return _post_activation_history_block(
                "PRODUCTION_HISTORY_PERSIST_FAILED",
                "Production activated, but canonical M13 history persistence/readback failed closed.")
        history_status = "EXACT_READBACK"
    return {
        "operation": "scrubbots-publish",
        "state": "PRODUCTION_ACTIVATED" if payload.get("accepted") is True else "PRODUCTION_REJECTED",
        "m14": payload, "receipt": _receipt(payload),
        "production": "ACTIVATED" if payload.get("accepted") is True else payload.get("reason_code", "REJECTED"),
        **({"manifest_history": history_status} if history_status is not None else {}),
        "mutation_performed": True,
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
    production_confirmation: Mapping[str, Any] | None = None,
) -> object:
    from scrubbots_content_pipeline import (
        FactoryPackRequest, PublisherMode, PublisherRunRequest,
    )
    from scrubbots_content_pipeline.config import Environment, PipelineConfig, STAGING_TARGET
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
    precondition = _read_manifest_precondition(
        provider, Environment.STAGING, STAGING_TARGET.logical_target_id,
        StagingManifestPrecondition, _MANIFEST_KEY,
    )
    candidate_sha = _candidate_manifest_sha(build, version)
    if candidate_sha != reviewed_identity.get("candidate_manifest_sha256"):
        raise ValueError("candidate manifest changed after owner preflight")
    mode = PublisherMode.STAGING_ONLY
    production_inputs = None
    if production_confirmation is not None:
        from scrubbots_content_pipeline import OwnerPromotionApproval, ProductionManifestPrecondition
        from scrubbots_content_pipeline.config import PRODUCTION_TARGET
        from scrubbots_content_pipeline.manifest_history import ManifestHistoryV1
        from scrubbots_content_pipeline.one_command_publisher import ProductionRunInputs
        if (production_confirmation.get("target") != "PRODUCTION"
                or production_confirmation.get("manifest_sha256") != candidate_sha
                or production_confirmation.get("content_version") != version
                or production_confirmation.get("confirmed") is not True):
            raise ValueError("production confirmation is not bound to candidate manifest")
        approval = OwnerPromotionApproval(
            str(production_confirmation["approval_id"]), str(production_confirmation["owner_id"]),
            candidate_sha, version, PRODUCTION_TARGET.logical_target_id,
        )
        production_precondition = _read_manifest_precondition(
            provider, Environment.PRODUCTION, PRODUCTION_TARGET.logical_target_id,
            ProductionManifestPrecondition, _MANIFEST_KEY,
        )
        current_production = production_precondition.expected_prior_manifest_bytes
        history_reader = getattr(provider, "read_manifest_history", None)
        if not callable(history_reader):
            raise ValueError("canonical production manifest history is unavailable")
        manifest_history = _read_production_manifest_history(
            history_reader(), current_production, production_precondition)
        authority = dict(authority)
        game_root = Path(os.environ.get("SCRUBBOTS_PROJECT", "")).expanduser().resolve()
        def check_approval():
            return approval
        def check_authority():
            return dict((game_authority_reader or _resolve_game_authority)())
        production_inputs = ProductionRunInputs(
            game_authority=authority, authority_check=check_authority,
            game_runner=_current_game_runner(game_root), owner_approval=approval,
            owner_approval_check=check_approval,
            production_precondition=production_precondition,
            manifest_history=manifest_history, recorded_at_utc=created,
        )
        mode = PublisherMode.PRODUCTION
    return PublisherRunRequest(
        mode=mode, config=PipelineConfig(), provider=provider,
        factory_pack_requests=(FactoryPackRequest(ids, pack_id, version, created),),
        factory_pack_builder=trusted_builder, content_version=version,
        previous_content_version=version - 1,
        minimum_game_version="2.4.0", current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: (1,)},
        object_keys={pack_id: f"packs/{pack_id}/v{version}.scrubpack"},
        publication_plan=plan, current_content_digest=plan.content_digest,
        owner_approved=True, staging_precondition=precondition,
        release_events=events, manifest_object_key=_MANIFEST_KEY,
        production=production_inputs,
    )


def _read_manifest_precondition(provider, environment, target_id, precondition_type, object_key):
    from scrubbots_content_pipeline.manifest_parser import parse_content_manifest_v1
    result = provider.read_object_bytes(environment, object_key)
    raw = result.content_bytes
    if raw is None:
        if precondition_type.__name__ == "StagingManifestPrecondition":
            return precondition_type(target_id, object_key, False, None, None, None)
        return precondition_type(target_id, object_key, None, None, None)
    parsed = parse_content_manifest_v1(raw)
    digest = hashlib.sha256(raw).hexdigest()
    if precondition_type.__name__ == "StagingManifestPrecondition":
        return precondition_type(target_id, object_key, True, digest, parsed.content_version, bytes(raw))
    return precondition_type(target_id, object_key, digest, parsed.content_version, bytes(raw))


def _read_production_manifest_history(history, current_manifest: bytes | None, precondition):
    """Require persisted M13 history to terminate at the exact live manifest CAS state."""
    from scrubbots_content_pipeline.manifest_history import ManifestHistoryV1, verify_manifest_history

    if not isinstance(history, ManifestHistoryV1) or not verify_manifest_history(history).accepted:
        raise ValueError("canonical production manifest history is invalid")
    if current_manifest is None:
        if history.records:
            raise ValueError("manifest history exists without a current production manifest")
    elif (not history.records
          or history.records[-1].manifest_bytes != current_manifest
          or history.records[-1].manifest_sha256 != precondition.expected_prior_sha256
          or history.records[-1].content_version != precondition.expected_prior_content_version):
        raise ValueError("current production manifest is not the exact M13 history tip")
    return history


def _candidate_manifest_sha(build, version: int) -> str | None:
    from scrubbots_content_pipeline.scrubpack_builder import ScrubpackBuildResult
    if not isinstance(build, ScrubpackBuildResult):
        return None
    from scrubbots_content_pipeline.candidate_manifest import build_candidate_manifest
    from scrubbots_content_pipeline.manifest_v1 import CONTENT_MANIFEST_SCHEMA
    candidate = build_candidate_manifest(
        (build,), content_version=version, minimum_game_version="2.4.0",
        object_keys={build.evidence.pack_id: f"packs/{build.evidence.pack_id}/v{version}.scrubpack"},
        current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: (1,)},
        prior_accepted_content_version=version - 1,
    )
    if not candidate.publishable:
        raise ValueError("candidate manifest is not publishable")
    return candidate.manifest_sha256


def _current_game_runner(game_root: Path):
    def run(levels):
        import json
        import shutil
        import tempfile
        from pathlib import Path
        from cpx002_current_main_replay_adapter import _run_godot
        executable = shutil.which("godot") or shutil.which("godot4")
        if not executable:
            raise RuntimeError("Godot executable is unavailable for exact-current replay")
        with tempfile.TemporaryDirectory(prefix="sb-lfx-production-replay-") as work:
            work_path = Path(work)
            rows = []
            for item in levels:
                level_id = str(item["level_id"])
                level_path = work_path / f"{level_id}.level.json"
                plan_path = work_path / f"{level_id}.supply.json"
                level_path.write_bytes(item["level_data_bytes"])
                plan_path.write_bytes(item["supply_plan_bytes"])
                rows.append({"level_id": level_id, "level_path": str(level_path),
                             "plan_path": str(plan_path), "level_sha256": item["level_sha256"],
                             "plan_sha256": item["plan_sha256"], "fifo_columns": item["fifo_columns"],
                             "solver_state_sha256": item["solver_state_sha256"],
                             "solver_evidence_sha256": item["solver_evidence_sha256"]})
            job = work_path / "job.json"
            job.write_text(json.dumps({"levels": rows}, sort_keys=True), encoding="utf-8")
            return _run_godot(game_root, executable, job, 900)
    return run


def _release_entries(reader):
    if reader is not None:
        return reader()
    from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries
    return release_entries()


def _next_content_version(provider_factory=None) -> int:
    """Derive the next version from both canonical current manifests, fail closed on unknown state."""
    from scrubbots_content_pipeline.config import Environment
    from scrubbots_content_pipeline.manifest_parser import parse_content_manifest_v1
    from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider, physical_object_key

    provider = (provider_factory or CloudflareR2Provider)()
    if provider._client() is None:
        raise RuntimeError("canonical release history is unavailable")
    versions: list[int] = []
    for environment in (Environment.STAGING, Environment.PRODUCTION):
        stored = provider._get(physical_object_key(environment, _MANIFEST_KEY))
        if stored is None:
            continue
        raw, _etag = stored
        parsed = parse_content_manifest_v1(raw)
        version = parsed.content_version
        if type(version) is not int or version < 1:
            raise ValueError("current release manifest version is invalid")
        versions.append(version)
    # Version 1 is the schema baseline. First publication derives to its successor.
    return max([1, *versions]) + 1


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


def _post_activation_history_block(state: str, reason: str) -> dict[str, Any]:
    """Report the already completed production write without implying full closure."""
    return {"operation": "scrubbots-publish", "state": state, "reason": reason,
            "mutation_performed": True, "bucket": R2_BUCKET, "public_read_base": PUBLIC_READ_BASE,
            "production": "ACTIVATED_HISTORY_INCOMPLETE"}


__all__ = ["PUBLIC_READ_BASE", "R2_BUCKET", "publish_preflight", "publish_to_staging", "publish_to_production"]
