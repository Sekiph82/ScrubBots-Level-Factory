"""Versioned production manifest activation after CP03-008 pack promotion."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .compatibility import AppContentCompatibilityResult, check_app_content_compatibility
from .config import Environment, PRODUCTION_TARGET
from .current_main_replay import CurrentMainReplayReceipt, REPOSITORY, _valid_authority
from .manifest_history import (
    ManifestHistoryV1, ManifestHistoryRecord, append_manifest_history, verify_manifest_history,
)
from .manifest_parser import parse_content_manifest_v1
from .manifest_validation import ManifestReferenceValidationResult, validate_manifest_references
from .manifest_v1 import CONTENT_MANIFEST_SCHEMA, CONTENT_MANIFEST_SCHEMA_VERSION, check_manifest_successor
from .production_promotion import (
    OwnerPromotionApproval, ProductionManifestPrecondition, ProductionPromotionReport,
    PromotedObjectEvidence, PromotionReasonCode,
)
from .provider import (
    PROVIDER_CONTRACT_VERSION, ProviderFeature, ProviderObjectBytesResult, ProviderResult,
    ProviderResultCategory, ProductionPromotionProvider, negotiate_capabilities,
    validate_provider_capability, validate_provider_identity,
)
from .release_state import ReleaseEvent, ReleaseState, make_release_event, replay_release_events
from .scrubpack_builder import ScrubpackBuildResult
from .scrubpack_inspection import inspect_scrubpack
from .staging_download_verify import (
    StagingDownloadReasonCode, StagingDownloadVerificationReport,
    serialize_staging_download_verification_receipt,
)

_SHA = re.compile(r"^[a-f0-9]{64}$")
_GIT = re.compile(r"^[a-f0-9]{40}$")


class ProductionManifestReasonCode(StrEnum):
    ACTIVATED = "ACTIVATED"
    ALREADY_CURRENT = "ALREADY_CURRENT"
    INVALID_INPUT = "INVALID_INPUT"
    STAGING_NOT_VERIFIED = "STAGING_NOT_VERIFIED"
    PACK_PROMOTION_NOT_ACCEPTED = "PACK_PROMOTION_NOT_ACCEPTED"
    OWNER_APPROVAL_REQUIRED = "OWNER_APPROVAL_REQUIRED"
    OWNER_APPROVAL_LOST = "OWNER_APPROVAL_LOST"
    GAME_AUTHORITY_STALE = "GAME_AUTHORITY_STALE"
    INVALID_HISTORY = "INVALID_HISTORY"
    VERSION_NOT_INCREASED = "VERSION_NOT_INCREASED"
    MANIFEST_NOT_COMPATIBLE = "MANIFEST_NOT_COMPATIBLE"
    REFERENCE_VALIDATION_FAILED = "REFERENCE_VALIDATION_FAILED"
    PRODUCTION_PACK_MISMATCH = "PRODUCTION_PACK_MISMATCH"
    PROVIDER_CONFLICT = "PROVIDER_CONFLICT"
    MANIFEST_WRITE_FAILED = "MANIFEST_WRITE_FAILED"
    PRODUCTION_MANIFEST_MISMATCH = "PRODUCTION_MANIFEST_MISMATCH"
    RELEASE_EVENT_APPEND_FAILED = "RELEASE_EVENT_APPEND_FAILED"


@dataclass(frozen=True, slots=True)
class ProductionPackVerification:
    pack_id: str
    object_key: str
    sha256: str
    byte_length: int
    verified_before_write: bool
    verified_after_write: bool


@dataclass(frozen=True, slots=True)
class ProductionManifestReceipt:
    manifest_bytes: bytes
    manifest_sha256: str
    content_version: int
    production_target_id: str
    manifest_object_key: str
    provider_id: str
    prior_manifest_sha256: str | None
    prior_content_version: int | None
    compatibility: AppContentCompatibilityResult
    reference_validation: ManifestReferenceValidationResult
    packs: tuple[ProductionPackVerification, ...]
    history_record: ManifestHistoryRecord
    manifest_history: ManifestHistoryV1
    history_tip_sha256: str
    promotion_pending_event_digest: str
    production_promoted_event: ReleaseEvent
    game_commit: str


@dataclass(frozen=True, slots=True)
class ProductionManifestActivationReport:
    accepted: bool
    reason_code: ProductionManifestReasonCode
    manifest_write_attempted: bool
    receipt: ProductionManifestReceipt | None
    release_event: ReleaseEvent | None


def activate_versioned_production_manifest(
    *, staging_report: StagingDownloadVerificationReport,
    staging_pack_bytes: Mapping[str, bytes], pack_builds: Sequence[ScrubpackBuildResult],
    promotion_report: ProductionPromotionReport,
    replay_receipt: CurrentMainReplayReceipt,
    owner_approval: OwnerPromotionApproval | None,
    owner_approval_check: Callable[[], OwnerPromotionApproval | None],
    game_authority_check: Callable[[], Mapping[str, object]],
    production_target_id: str, manifest_object_key: str,
    precondition: ProductionManifestPrecondition, manifest_history: ManifestHistoryV1,
    release_events: Sequence[ReleaseEvent], recorded_at_utc: str | datetime,
    current_game_version: str, supported_manifest_schema_versions: Mapping[str, object],
    provider: ProductionPromotionProvider,
) -> ProductionManifestActivationReport:
    """CAS-activate the exact staged bytes, read them and packs back, then append M13/M11 history."""
    attempted = False
    try:
        if (not isinstance(staging_report, StagingDownloadVerificationReport)
                or staging_report.accepted is not True
                or staging_report.reason_code is not StagingDownloadReasonCode.VERIFIED
                or staging_report.receipt is None or staging_report.capability_negotiation is None
                or staging_report.capability_negotiation.accepted is not True
                or staging_report.capability_negotiation.environment != Environment.STAGING.value):
            return _failure(ProductionManifestReasonCode.STAGING_NOT_VERIFIED)
        staging = staging_report.receipt
        serialize_staging_download_verification_receipt(staging)
        manifest_bytes = staging.manifest_bytes
        manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        manifest = parse_content_manifest_v1(manifest_bytes)
        if (manifest.to_json_bytes() != manifest_bytes or manifest_sha != staging.manifest_sha256
                or manifest.content_version != staging.content_version
                or production_target_id != PRODUCTION_TARGET.logical_target_id
                or precondition.target_id != production_target_id
                or precondition.object_key != manifest_object_key
                or manifest_object_key != staging.manifest_object_key):
            return _failure(ProductionManifestReasonCode.INVALID_INPUT)
        if not _promotion_bound(promotion_report, staging, production_target_id):
            return _failure(ProductionManifestReasonCode.PACK_PROMOTION_NOT_ACCEPTED)
        if (not isinstance(replay_receipt, CurrentMainReplayReceipt)
                or replay_receipt.accepted is not True or replay_receipt.reason_code != "VERIFIED"
                or replay_receipt.target_environment != "STAGING"
                or replay_receipt.game_repository != REPOSITORY or replay_receipt.game_branch != "main"
                or not _GIT.fullmatch(replay_receipt.game_commit)
                or replay_receipt.game_commit != promotion_report.current_game_commit
                or replay_receipt.manifest_sha256 != manifest_sha
                or not _valid_replay_pack_binding(replay_receipt, staging.packs)):
            return _failure(ProductionManifestReasonCode.GAME_AUTHORITY_STALE)
        if not _valid_approval(owner_approval, staging, production_target_id):
            return _failure(ProductionManifestReasonCode.OWNER_APPROVAL_REQUIRED)
        history_check = verify_manifest_history(manifest_history)
        if not history_check.accepted:
            return _failure(ProductionManifestReasonCode.INVALID_HISTORY)
        last = manifest_history.records[-1] if manifest_history.records else None
        exact_history_repeat = False
        if last is None:
            if (precondition.expected_prior_sha256 is not None
                    or precondition.expected_prior_content_version is not None
                    or precondition.expected_prior_manifest_bytes is not None):
                return _failure(ProductionManifestReasonCode.INVALID_HISTORY)
            prior_version = None
        else:
            if (precondition.expected_prior_sha256 != last.manifest_sha256
                    or precondition.expected_prior_manifest_bytes != last.manifest_bytes
                    or precondition.expected_prior_content_version != last.content_version):
                return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT)
            prior_version = last.content_version
            prior_manifest = parse_content_manifest_v1(last.manifest_bytes)
            if prior_manifest.to_json_bytes() != last.manifest_bytes or prior_manifest.content_version != prior_version:
                return _failure(ProductionManifestReasonCode.INVALID_HISTORY)
            exact_history_repeat = (last.manifest_bytes == manifest_bytes
                                    and last.manifest_sha256 == manifest_sha
                                    and last.content_version == manifest.content_version)
            if not exact_history_repeat and not check_manifest_successor(prior_version, manifest.to_dict()).accepted:
                return _failure(ProductionManifestReasonCode.VERSION_NOT_INCREASED)
        compatibility = check_app_content_compatibility(
            current_game_version=current_game_version,
            supported_manifest_schema_versions=supported_manifest_schema_versions,
            manifest_schema=manifest.schema,
            manifest_schema_version=manifest.schema_version,
            minimum_game_version=manifest.minimum_game_version,
        )
        if not compatibility.compatible:
            return _failure(ProductionManifestReasonCode.MANIFEST_NOT_COMPATIBLE)
        if not _valid_pack_bytes(staging, staging_pack_bytes, pack_builds):
            return _failure(ProductionManifestReasonCode.REFERENCE_VALIDATION_FAILED)
        references = validate_manifest_references(manifest, tuple(pack_builds))
        if not references.eligible:
            return _failure(ProductionManifestReasonCode.REFERENCE_VALIDATION_FAILED)
        chain = tuple(release_events)
        staging_tail = staging.release_event_digests
        chain_state = replay_release_events(chain)
        state = replay_release_events((*chain, *promotion_report.release_events))
        pending_events = promotion_report.release_events
        staged_snapshot = next((item for item in chain_state.snapshots
                                if item.record_id == f"staging-{manifest_sha[:32]}"), None)
        if (not chain_state.accepted or not state.accepted or staged_snapshot is None
                or staged_snapshot.state is not ReleaseState.STAGED
                or staged_snapshot.content_digest != manifest_sha
                or not staging_tail
                or tuple(event.event_digest for event in chain[-len(staging_tail):]) != staging_tail
                or len(pending_events) != 1
                or pending_events[0].to_state is not ReleaseState.PROMOTION_PENDING
                or pending_events[0].environment is not Environment.PRODUCTION
                or pending_events[0].content_digest != manifest_sha
                or pending_events[0].content_id != f"manifest-v{staging.content_version}-{manifest_sha[:16]}"
                or pending_events[0].source_record_id != staged_snapshot.record_id
                or pending_events[0].event_digest != promotion_report.release_events[-1].event_digest):
            return _failure(ProductionManifestReasonCode.PACK_PROMOTION_NOT_ACCEPTED)
        pending = pending_events[0]
        promoted = make_release_event(
            sequence=pending.sequence + 1, event_id=f"production-promoted-{manifest_sha[:24]}",
            transition_id=f"production-promoted-{manifest_sha[:24]}", record_id=pending.record_id,
            content_id=pending.content_id, content_digest=manifest_sha, environment=Environment.PRODUCTION,
            from_state=ReleaseState.PROMOTION_PENDING, to_state=ReleaseState.PRODUCTION_PROMOTED,
            expected_state=ReleaseState.PROMOTION_PENDING, previous_event_digest=pending.event_digest,
            promotion_intent=True, source_record_id=pending.source_record_id,
        )
        if not replay_release_events((*chain, pending, promoted)).accepted:
            return _failure(ProductionManifestReasonCode.INVALID_HISTORY)
        builds_by_id = {item.evidence.pack_id: item for item in pack_builds}
        readbacks: list[ProductionPackVerification] = []
        for row in staging.packs:
            raw = staging_pack_bytes[row.pack_id]
            build = builds_by_id[row.pack_id]
            before = provider.read_object_bytes(Environment.PRODUCTION, row.object_key)
            if not _valid_object(before, provider.identity.provider_id, row.object_key, raw, row.sha256, row.byte_length):
                return _failure(ProductionManifestReasonCode.PRODUCTION_PACK_MISMATCH)
            inspection = inspect_scrubpack(raw)
            if (not inspection.accepted or inspection.pack_id != row.pack_id
                    or inspection.pack_version != next(pack.pack_version for pack in manifest.packs if pack.pack_id == row.pack_id)
                    or inspection.level_ids != row.level_ids or build.archive_bytes != raw
                    or build.evidence.archive_sha256 != row.sha256
                    or build.evidence.archive_byte_length != row.byte_length):
                return _failure(ProductionManifestReasonCode.REFERENCE_VALIDATION_FAILED)
            readbacks.append(ProductionPackVerification(row.pack_id, row.object_key, row.sha256,
                                                        row.byte_length, True, False))
        identity, capability = provider.identity, provider.capabilities
        if (not validate_provider_identity(identity) or not validate_provider_capability(capability)
                or identity.provider_id != promotion_report.provider_id):
            return _failure(ProductionManifestReasonCode.PACK_PROMOTION_NOT_ACCEPTED)
        required_features = tuple(sorted((ProviderFeature.PRODUCTION_PROMOTION, ProviderFeature.CONDITIONAL_WRITE,
            ProviderFeature.INTEGRITY_VERIFY, ProviderFeature.ATOMIC_MANIFEST_PUBLISH), key=lambda item: item.value))
        if not negotiate_capabilities(capability, Environment.PRODUCTION, required_features).accepted:
            return _failure(ProductionManifestReasonCode.PACK_PROMOTION_NOT_ACCEPTED)
        authority = _valid_authority({"repository": replay_receipt.game_repository,
            "branch": replay_receipt.game_branch, "commit": replay_receipt.game_commit,
            "source_sha256": replay_receipt.authority_source_sha256})
        if not _fresh_approval(owner_approval_check, owner_approval):
            return _failure(ProductionManifestReasonCode.OWNER_APPROVAL_LOST)
        if not _fresh_authority(game_authority_check, authority):
            return _failure(ProductionManifestReasonCode.GAME_AUTHORITY_STALE)
        # The only idempotent success is an exact live object already supported by
        # both M13 history and the complete, replayable M11 production promotion.
        try:
            live_manifest = provider.read_object_bytes(Environment.PRODUCTION, manifest_object_key)
            live_ledger = tuple(provider.read_release_events())
        except Exception:
            return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT)
        if _valid_object(live_manifest, identity.provider_id, manifest_object_key, manifest_bytes,
                         manifest_sha, len(manifest_bytes)):
            ledger_replay = replay_release_events(live_ledger)
            if (exact_history_repeat and ledger_replay.accepted
                    and ledger_replay.current_production_record_id == pending.record_id
                    and len(live_ledger) >= 2 and live_ledger[-2:] == (pending, promoted)):
                return ProductionManifestActivationReport(
                    True, ProductionManifestReasonCode.ALREADY_CURRENT, False, None, promoted)
            return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT)
        if exact_history_repeat and live_manifest.content_bytes is None:
            return _failure(ProductionManifestReasonCode.VERSION_NOT_INCREASED)
        if not _live_manifest_matches_precondition(live_manifest, identity.provider_id,
                                                   manifest_object_key, precondition):
            return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT)
        expected_ledger = (*chain, pending)
        if (not replay_release_events(live_ledger).accepted or live_ledger != expected_ledger):
            return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT)
        # Re-read both mutable authorities at the mutation boundary. The provider
        # must atomically compare these exact values inside its conditional write.
        try:
            current_manifest = provider.read_object_bytes(Environment.PRODUCTION, manifest_object_key)
            ledger_events = tuple(provider.read_release_events())
        except Exception:
            return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT)
        if (not _live_manifest_matches_precondition(current_manifest, identity.provider_id,
                                                    manifest_object_key, precondition)
                or ledger_events != expected_ledger or not replay_release_events(ledger_events).accepted):
            return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT)
        attempted = True
        try:
            write = provider.write_manifest_conditionally(
                Environment.PRODUCTION, production_target_id, manifest_object_key, manifest_sha, manifest_bytes,
                expected_prior_sha256=precondition.expected_prior_sha256,
                expected_prior_content_version=precondition.expected_prior_content_version,
                expected_release_state_sequence=len(ledger_events),
                expected_release_state_tip_digest=_ledger_tip(ledger_events),
                promotion_pending_event_digest=pending.event_digest,
            )
        except Exception:
            return _failure(ProductionManifestReasonCode.MANIFEST_WRITE_FAILED, attempted=True)
        if not _provider_success(write, identity.provider_id, manifest_sha):
            return _failure(ProductionManifestReasonCode.PROVIDER_CONFLICT, attempted=True)
        prod_manifest = provider.read_object_bytes(Environment.PRODUCTION, manifest_object_key)
        if not _valid_object(prod_manifest, identity.provider_id, manifest_object_key, manifest_bytes,
                             manifest_sha, len(manifest_bytes)):
            return _failure(ProductionManifestReasonCode.PRODUCTION_MANIFEST_MISMATCH, attempted=True)
        verified_manifest = parse_content_manifest_v1(prod_manifest.content_bytes)
        if verified_manifest.to_json_bytes() != manifest_bytes:
            return _failure(ProductionManifestReasonCode.PRODUCTION_MANIFEST_MISMATCH, attempted=True)
        after_packs: list[ProductionPackVerification] = []
        for item in readbacks:
            raw = staging_pack_bytes[item.pack_id]
            prod_pack = provider.read_object_bytes(Environment.PRODUCTION, item.object_key)
            if not _valid_object(prod_pack, identity.provider_id, item.object_key, raw, item.sha256, item.byte_length):
                return _failure(ProductionManifestReasonCode.PRODUCTION_PACK_MISMATCH, attempted=True)
            after_packs.append(ProductionPackVerification(item.pack_id, item.object_key, item.sha256,
                                                          item.byte_length, True, True))
        after_refs = validate_manifest_references(verified_manifest, tuple(pack_builds))
        after_compat = check_app_content_compatibility(current_game_version=current_game_version,
            supported_manifest_schema_versions=supported_manifest_schema_versions,
            manifest_schema=verified_manifest.schema, manifest_schema_version=verified_manifest.schema_version,
            minimum_game_version=verified_manifest.minimum_game_version)
        if not after_refs.eligible or not after_compat.compatible:
            return _failure(ProductionManifestReasonCode.PRODUCTION_MANIFEST_MISMATCH, attempted=True)
        new_history = append_manifest_history(manifest_history, manifest_bytes, recorded_at_utc=recorded_at_utc)
        record = new_history.records[-1]
        try:
            appended = provider.append_release_event(
                promoted, expected_prior_sequence=pending.sequence,
                expected_prior_event_digest=pending.event_digest)
        except Exception:
            appended = None
        if not _provider_success(appended, identity.provider_id, promoted.event_digest):
            return _failure(ProductionManifestReasonCode.RELEASE_EVENT_APPEND_FAILED, attempted=True)
        receipt = ProductionManifestReceipt(
            manifest_bytes, manifest_sha, manifest.content_version, production_target_id, manifest_object_key,
            identity.provider_id, precondition.expected_prior_sha256, prior_version, after_compat, after_refs,
            tuple(after_packs), record, new_history, new_history.tip_sha256 or "", pending.event_digest, promoted,
            replay_receipt.game_commit,
        )
        return ProductionManifestActivationReport(True, ProductionManifestReasonCode.ACTIVATED, True,
                                                 receipt, promoted)
    except Exception:
        return _failure(ProductionManifestReasonCode.INVALID_INPUT, attempted=attempted)


def _promotion_bound(report: object, staging: object, target: str) -> bool:
    if (not isinstance(report, ProductionPromotionReport) or report.accepted is not True
            or report.reason_code is not PromotionReasonCode.PROMOTED or report.manifest_write_attempted is not False
            or report.target_id != target or report.manifest_sha256 != staging.manifest_sha256
            or report.provider_id is None or not report.promoted_objects or len(report.release_events) != 1):
        return False
    expected = {row.pack_id: (row.object_key, row.sha256, row.byte_length) for row in staging.packs}
    actual = {row.pack_id: (row.production_object_key, row.sha256, row.byte_length) for row in report.promoted_objects
              if isinstance(row, PromotedObjectEvidence) and row.verified}
    return (len(actual) == len(report.promoted_objects) == len(expected) and actual == expected
            and all(row.source_object_key == expected[row.pack_id][0] for row in report.promoted_objects
                    if isinstance(row, PromotedObjectEvidence)))


def _valid_approval(value: object, staging: object, target: str) -> bool:
    return (isinstance(value, OwnerPromotionApproval) and bool(value.approval_id) and bool(value.owner_id)
            and value.manifest_sha256 == staging.manifest_sha256
            and value.content_version == staging.content_version and value.production_target_id == target)


def _valid_replay_pack_binding(replay: CurrentMainReplayReceipt, packs: Sequence[object]) -> bool:
    rows = {row.get("pack_id"): row for row in replay.pack_results if isinstance(row, Mapping)}
    return len(rows) == len(replay.pack_results) == len(packs) and set(rows) == {row.pack_id for row in packs} and all(
        rows[row.pack_id].get("pack_sha256") == row.sha256
        and isinstance(rows[row.pack_id].get("levels"), list)
        and {level.get("level_id") for level in rows[row.pack_id]["levels"] if isinstance(level, Mapping)}
            == set(row.level_ids)
        and len(rows[row.pack_id]["levels"]) == len(row.level_ids)
        and all(isinstance(level, Mapping) and level.get("accepted") is True
                and level.get("solver_status") == "SOLVED" and level.get("replay_ok") is True
                and level.get("replay_solved") is True and level.get("final_active") == 0
                and level.get("unresolved") == 0 and level.get("supply_exhausted") is True
                for level in rows[row.pack_id]["levels"])
        for row in packs)


def _fresh_approval(check: Callable[[], OwnerPromotionApproval | None], expected: OwnerPromotionApproval) -> bool:
    try:
        return callable(check) and check() == expected
    except Exception:
        return False


def _fresh_authority(check: Callable[[], Mapping[str, object]], expected: Mapping[str, object]) -> bool:
    try:
        return callable(check) and _valid_authority(check()) == expected
    except Exception:
        return False


def _valid_pack_bytes(staging: object, packs: Mapping[str, bytes], builds: Sequence[ScrubpackBuildResult]) -> bool:
    if set(packs) != {row.pack_id for row in staging.packs}:
        return False
    build_map = {build.evidence.pack_id: build for build in builds if isinstance(build, ScrubpackBuildResult)}
    if len(build_map) != len(builds) or set(build_map) != set(packs):
        return False
    for row in staging.packs:
        raw = packs[row.pack_id]
        build = build_map[row.pack_id]
        if (type(raw) is not bytes or len(raw) != row.byte_length
                or hashlib.sha256(raw).hexdigest() != row.sha256 or raw != build.archive_bytes):
            return False
    return True


def _valid_object(result: object, provider_id: str, key: str, raw: bytes, digest: str, length: int) -> bool:
    return (isinstance(result, ProviderObjectBytesResult) and result.result_version == PROVIDER_CONTRACT_VERSION
            and result.category is ProviderResultCategory.SUCCESS and result.provider_id == provider_id
            and result.environment is Environment.PRODUCTION and result.object_key == key
            and type(result.content_bytes) is bytes and len(result.content_bytes) == length
            and hashlib.sha256(result.content_bytes).hexdigest() == digest and result.content_bytes == raw)


def _provider_success(result: object, provider_id: str, digest: str) -> bool:
    return (isinstance(result, ProviderResult) and result.result_version == PROVIDER_CONTRACT_VERSION
            and result.category is ProviderResultCategory.SUCCESS and result.provider_id == provider_id
            and result.environment is Environment.PRODUCTION and result.content_digest == digest)


def _ledger_tip(events: Sequence[ReleaseEvent]) -> str:
    return events[-1].event_digest if events else "0" * 64


def _live_manifest_matches_precondition(result: object, provider_id: str, key: str,
                                        precondition: ProductionManifestPrecondition) -> bool:
    if (not isinstance(result, ProviderObjectBytesResult)
            or result.result_version != PROVIDER_CONTRACT_VERSION
            or result.category is not ProviderResultCategory.SUCCESS
            or result.provider_id != provider_id or result.environment is not Environment.PRODUCTION
            or result.object_key != key):
        return False
    if precondition.expected_prior_manifest_bytes is None:
        return (result.content_bytes is None and precondition.expected_prior_sha256 is None
                and precondition.expected_prior_content_version is None)
    raw = precondition.expected_prior_manifest_bytes
    return (type(raw) is bytes and result.content_bytes == raw
            and hashlib.sha256(raw).hexdigest() == precondition.expected_prior_sha256
            and precondition.expected_prior_sha256 is not None
            and precondition.expected_prior_content_version is not None
            and hashlib.sha256(result.content_bytes).hexdigest() == precondition.expected_prior_sha256
            and parse_content_manifest_v1(raw).content_version == precondition.expected_prior_content_version)


def _failure(reason: ProductionManifestReasonCode, *, attempted: bool = False) -> ProductionManifestActivationReport:
    return ProductionManifestActivationReport(False, reason, attempted, None, None)


__all__ = ["ProductionManifestActivationReport", "ProductionManifestReasonCode", "ProductionManifestReceipt",
           "ProductionPackVerification", "activate_versioned_production_manifest"]
