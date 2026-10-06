"""Explicit STAGING to PRODUCTION object promotion with a fail-closed manifest gate."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from .config import Environment, PRODUCTION_TARGET, STAGING_TARGET
from .current_main_replay import CurrentMainReplayReceipt, REPOSITORY, _valid_authority
from .manifest_parser import parse_content_manifest_v1
from .manifest_v1 import check_manifest_successor
from .provider import (
    PROVIDER_CONTRACT_VERSION, ProviderFeature, ProviderObjectBytesResult, ProviderResult,
    ProviderResultCategory, ProductionPromotionProvider, negotiate_capabilities,
    validate_provider_capability, validate_provider_identity,
)
from .release_state import ReleaseEvent, ReleaseState, make_release_event, replay_release_events
from .staging_download_verify import (
    StagingDownloadReasonCode, StagingDownloadVerificationReport,
    serialize_staging_download_verification_receipt,
)

_SHA = re.compile(r"^[a-f0-9]{64}$")
_GIT = re.compile(r"^[a-f0-9]{40}$")
_REQUIRED = tuple(sorted((ProviderFeature.PRODUCTION_PROMOTION, ProviderFeature.CONDITIONAL_WRITE,
                          ProviderFeature.INTEGRITY_VERIFY, ProviderFeature.ATOMIC_MANIFEST_PUBLISH),
                         key=lambda item: item.value))


class PromotionReasonCode(StrEnum):
    PROMOTED = "PROMOTED"
    INVALID_INPUT = "INVALID_INPUT"
    STAGING_NOT_VERIFIED = "STAGING_NOT_VERIFIED"
    REPLAY_NOT_ACCEPTED = "REPLAY_NOT_ACCEPTED"
    OWNER_APPROVAL_REQUIRED = "OWNER_APPROVAL_REQUIRED"
    OWNER_APPROVAL_LOST = "OWNER_APPROVAL_LOST"
    GAME_AUTHORITY_STALE = "GAME_AUTHORITY_STALE"
    INVALID_HISTORY = "INVALID_HISTORY"
    INVALID_PROVIDER = "INVALID_PROVIDER"
    CAPABILITY_REJECTED = "CAPABILITY_REJECTED"
    OBJECT_PROMOTION_FAILED = "OBJECT_PROMOTION_FAILED"
    PRODUCTION_OBJECT_MISMATCH = "PRODUCTION_OBJECT_MISMATCH"
    MANIFEST_PRECONDITION_FAILED = "MANIFEST_PRECONDITION_FAILED"
    MANIFEST_WRITE_FAILED = "MANIFEST_WRITE_FAILED"
    RELEASE_EVENT_APPEND_FAILED = "RELEASE_EVENT_APPEND_FAILED"


@dataclass(frozen=True, slots=True)
class OwnerPromotionApproval:
    approval_id: str
    owner_id: str
    manifest_sha256: str
    content_version: int
    production_target_id: str


@dataclass(frozen=True, slots=True)
class ProductionManifestPrecondition:
    target_id: str
    object_key: str
    expected_prior_sha256: str | None
    expected_prior_content_version: int | None
    expected_prior_manifest_bytes: bytes | None


@dataclass(frozen=True, slots=True)
class PromotedObjectEvidence:
    pack_id: str
    source_object_key: str
    production_object_key: str
    sha256: str
    byte_length: int
    verified: bool


@dataclass(frozen=True, slots=True)
class ProductionPromotionReport:
    accepted: bool
    reason_code: PromotionReasonCode
    manifest_write_attempted: bool
    provider_id: str | None
    target_id: str
    manifest_sha256: str
    promoted_objects: tuple[PromotedObjectEvidence, ...]
    release_events: tuple[ReleaseEvent, ...]
    current_game_commit: str


def promote_verified_staging_to_production(
    *, staging_report: StagingDownloadVerificationReport,
    downloaded_pack_bytes: Mapping[str, bytes], replay_receipt: CurrentMainReplayReceipt,
    owner_approval: OwnerPromotionApproval | None,
    owner_approval_check: Callable[[], OwnerPromotionApproval | None],
    game_authority_check: Callable[[], Mapping[str, object]],
    target_id: str, manifest_object_key: str, precondition: ProductionManifestPrecondition,
    release_events: Sequence[ReleaseEvent], provider: ProductionPromotionProvider,
) -> ProductionPromotionReport:
    """Copy and re-read every verified object, then persist promotion-pending evidence.

    This function intentionally has no deletion or rollback path. Any failure leaves
    copied immutable objects in place and withholds manifest activation.
    """
    manifest_sha = ""
    try:
        if (not isinstance(staging_report, StagingDownloadVerificationReport)
                or staging_report.accepted is not True
                or staging_report.reason_code is not StagingDownloadReasonCode.VERIFIED
                or staging_report.receipt is None
                or staging_report.capability_negotiation is None
                or staging_report.capability_negotiation.accepted is not True
                or staging_report.capability_negotiation.environment != Environment.STAGING.value):
            return _report(PromotionReasonCode.STAGING_NOT_VERIFIED, target_id)
        receipt = staging_report.receipt
        serialize_staging_download_verification_receipt(receipt)
        manifest_sha = receipt.manifest_sha256
        if (receipt.target_environment != Environment.STAGING.value
                or receipt.target_id != STAGING_TARGET.logical_target_id
                or manifest_object_key != receipt.manifest_object_key
                or tuple(sorted(staging_report.downloaded_pack_ids)) != tuple(sorted(item.pack_id for item in receipt.packs))
                or not isinstance(replay_receipt, CurrentMainReplayReceipt)
                or replay_receipt.accepted is not True or replay_receipt.reason_code != "VERIFIED"
                or replay_receipt.target_environment != "STAGING"
                or replay_receipt.manifest_sha256 != manifest_sha
                or replay_receipt.game_repository != REPOSITORY or replay_receipt.game_branch != "main"
                or not _GIT.fullmatch(replay_receipt.game_commit)
                or not _valid_pack_replay(replay_receipt, receipt.packs)):
            return _report(PromotionReasonCode.REPLAY_NOT_ACCEPTED, target_id, manifest_sha)
        if (target_id != PRODUCTION_TARGET.logical_target_id or precondition.target_id != target_id
                or precondition.object_key != manifest_object_key):
            return _report(PromotionReasonCode.MANIFEST_PRECONDITION_FAILED, target_id, manifest_sha)
        if not _valid_approval(owner_approval, receipt, target_id):
            return _report(PromotionReasonCode.OWNER_APPROVAL_REQUIRED, target_id, manifest_sha)
        manifest = parse_content_manifest_v1(receipt.manifest_bytes)
        if manifest.content_version != receipt.content_version:
            return _report(PromotionReasonCode.INVALID_INPUT, target_id, manifest_sha)
        if precondition.expected_prior_sha256 is None:
            if precondition.expected_prior_content_version is not None or precondition.expected_prior_manifest_bytes is not None:
                return _report(PromotionReasonCode.MANIFEST_PRECONDITION_FAILED, target_id, manifest_sha)
        else:
            if (not _SHA.fullmatch(precondition.expected_prior_sha256)
                    or type(precondition.expected_prior_content_version) is not int
                    or type(precondition.expected_prior_manifest_bytes) is not bytes
                    or hashlib.sha256(precondition.expected_prior_manifest_bytes).hexdigest() != precondition.expected_prior_sha256):
                return _report(PromotionReasonCode.MANIFEST_PRECONDITION_FAILED, target_id, manifest_sha)
            previous = parse_content_manifest_v1(precondition.expected_prior_manifest_bytes)
            if (previous.content_version != precondition.expected_prior_content_version
                    or not check_manifest_successor(previous.content_version, manifest.to_dict()).accepted):
                return _report(PromotionReasonCode.MANIFEST_PRECONDITION_FAILED, target_id, manifest_sha)
        try:
            approval_current = callable(owner_approval_check) and owner_approval_check() == owner_approval
        except Exception:
            approval_current = False
        if not approval_current:
            return _report(PromotionReasonCode.OWNER_APPROVAL_LOST, target_id, manifest_sha)
        authority = _valid_authority({
            "repository": replay_receipt.game_repository, "branch": replay_receipt.game_branch,
            "commit": replay_receipt.game_commit, "source_sha256": replay_receipt.authority_source_sha256,
        })
        try:
            authority_current = callable(game_authority_check) and _valid_authority(game_authority_check()) == authority
        except Exception:
            authority_current = False
        if not authority_current:
            return _report(PromotionReasonCode.GAME_AUTHORITY_STALE, target_id, manifest_sha)
        identity, capability = provider.identity, provider.capabilities
        if not validate_provider_identity(identity) or not validate_provider_capability(capability):
            return _report(PromotionReasonCode.INVALID_PROVIDER, target_id, manifest_sha)
        negotiation = negotiate_capabilities(capability, Environment.PRODUCTION, _REQUIRED)
        if not negotiation.accepted:
            return _report(PromotionReasonCode.CAPABILITY_REJECTED, target_id, manifest_sha, identity.provider_id)
        if set(downloaded_pack_bytes) != {item.pack_id for item in receipt.packs}:
            return _report(PromotionReasonCode.INVALID_INPUT, target_id, manifest_sha, identity.provider_id)
        for pack in receipt.packs:
            exact = downloaded_pack_bytes.get(pack.pack_id)
            if type(exact) is not bytes or len(exact) != pack.byte_length or hashlib.sha256(exact).hexdigest() != pack.sha256:
                return _report(PromotionReasonCode.STAGING_NOT_VERIFIED, target_id, manifest_sha, identity.provider_id)
        copied_keys: list[tuple[object, str]] = []
        for pack in receipt.packs:
            try:
                result = provider.promote_object(Environment.STAGING, pack.object_key, Environment.PRODUCTION,
                                                 pack.object_key, pack.sha256)
            except Exception:
                result = None
            if not _success(result, identity.provider_id, pack.sha256):
                return _report(PromotionReasonCode.OBJECT_PROMOTION_FAILED, target_id, manifest_sha,
                               identity.provider_id, tuple(PromotedObjectEvidence(
                                   item.pack_id, item.object_key, item.object_key, item.sha256,
                                   item.byte_length, False) for item, _ in copied_keys))
            copied_keys.append((pack, pack.object_key))
        copied: list[PromotedObjectEvidence] = []
        for pack, production_key in copied_keys:
            try:
                read = provider.read_object_bytes(Environment.PRODUCTION, production_key)
            except Exception:
                read = None
            exact = downloaded_pack_bytes[pack.pack_id]
            if not _valid_read(read, identity.provider_id, production_key, exact, pack.sha256, pack.byte_length):
                return _report(PromotionReasonCode.PRODUCTION_OBJECT_MISMATCH, target_id, manifest_sha,
                               identity.provider_id, tuple(copied))
            copied.append(PromotedObjectEvidence(pack.pack_id, pack.object_key, production_key,
                                                  pack.sha256, pack.byte_length, True))
        history = tuple(release_events)
        replayed = replay_release_events(history)
        staged = next((item for item in replayed.snapshots if item.record_id == f"staging-{manifest_sha[:32]}"), None)
        expected_event_tail = receipt.release_event_digests
        if (not replayed.accepted or staged is None or staged.state is not ReleaseState.STAGED
                or staged.content_digest != manifest_sha
                or tuple(event.event_digest for event in history[-len(expected_event_tail):]) != expected_event_tail):
            return _report(PromotionReasonCode.INVALID_HISTORY, target_id, manifest_sha, identity.provider_id, tuple(copied))
        last_digest = history[-1].event_digest if history else "0" * 64
        sequence = len(history) + 1
        production_id = f"production-{manifest_sha[:32]}"
        content_id = f"manifest-v{receipt.content_version}-{manifest_sha[:16]}"
        pending = make_release_event(sequence=sequence, event_id=f"promotion-pending-{manifest_sha[:24]}",
            transition_id=f"promotion-pending-{manifest_sha[:24]}", record_id=production_id, content_id=content_id,
            content_digest=manifest_sha, environment=Environment.PRODUCTION, from_state=None,
            to_state=ReleaseState.PROMOTION_PENDING, expected_state=None, previous_event_digest=last_digest,
            promotion_intent=True, source_record_id=staged.record_id)
        pending_history = (*history, pending)
        if not replay_release_events(pending_history).accepted:
            return _report(PromotionReasonCode.INVALID_HISTORY, target_id, manifest_sha, identity.provider_id, tuple(copied))
        try:
            persisted_pending = provider.append_release_event(pending)
        except Exception:
            persisted_pending = None
        if not _success(persisted_pending, identity.provider_id, pending.event_digest, Environment.PRODUCTION):
            return _report(PromotionReasonCode.RELEASE_EVENT_APPEND_FAILED, target_id, manifest_sha,
                           identity.provider_id, tuple(copied), (), False)
        # Re-check the human approval and game source immediately at the activation boundary.
        try:
            approval_current = callable(owner_approval_check) and owner_approval_check() == owner_approval
        except Exception:
            approval_current = False
        if not approval_current:
            return _report(PromotionReasonCode.OWNER_APPROVAL_LOST, target_id, manifest_sha,
                           identity.provider_id, tuple(copied), (pending,))
        try:
            authority_current = callable(game_authority_check) and _valid_authority(game_authority_check()) == authority
        except Exception:
            authority_current = False
        if not authority_current:
            return _report(PromotionReasonCode.GAME_AUTHORITY_STALE, target_id, manifest_sha,
                           identity.provider_id, tuple(copied), (pending,))
        # CP03-008 establishes promoted, byte-verified objects and durable pending evidence.
        # CP03-009 owns the single versioned manifest activation after M13 validation/history.
        return ProductionPromotionReport(True, PromotionReasonCode.PROMOTED, False, identity.provider_id,
            target_id, manifest_sha, tuple(copied), (pending,), replay_receipt.game_commit)
    except Exception:
        return _report(PromotionReasonCode.INVALID_INPUT, target_id, manifest_sha)


def _valid_approval(value: object, receipt: object, target: str) -> bool:
    return (isinstance(value, OwnerPromotionApproval) and bool(value.approval_id) and bool(value.owner_id)
            and value.manifest_sha256 == receipt.manifest_sha256 and value.content_version == receipt.content_version
            and value.production_target_id == target)


def _valid_pack_replay(replay: CurrentMainReplayReceipt, packs: Sequence[object]) -> bool:
    rows = {row.get("pack_id"): row for row in replay.pack_results if isinstance(row, Mapping)}
    return len(rows) == len(replay.pack_results) and set(rows) == {item.pack_id for item in packs} and all(
        rows[item.pack_id].get("pack_sha256") == item.sha256
        and isinstance(rows[item.pack_id].get("levels"), list)
        and bool(rows[item.pack_id]["levels"])
        and all(isinstance(level, Mapping) and level.get("accepted") is True
                and level.get("solver_status") == "SOLVED" and level.get("replay_ok") is True
                and level.get("replay_solved") is True and level.get("final_active") == 0
                and level.get("unresolved") == 0 and level.get("supply_exhausted") is True
                for level in rows[item.pack_id]["levels"])
        for item in packs)


def _success(result: object, provider_id: str, digest: str, env: Environment = Environment.PRODUCTION) -> bool:
    return (isinstance(result, ProviderResult) and result.result_version == PROVIDER_CONTRACT_VERSION
            and result.category is ProviderResultCategory.SUCCESS and result.provider_id == provider_id
            and result.environment is env and result.content_digest == digest)


def _valid_read(result: object, provider_id: str, key: str, content: bytes, digest: str, length: int) -> bool:
    return (isinstance(result, ProviderObjectBytesResult) and result.result_version == PROVIDER_CONTRACT_VERSION
            and result.category is ProviderResultCategory.SUCCESS and result.provider_id == provider_id
            and result.environment is Environment.PRODUCTION and result.object_key == key
            and type(result.content_bytes) is bytes and len(result.content_bytes) == length
            and hashlib.sha256(result.content_bytes).hexdigest() == digest and result.content_bytes == content)


def _report(reason: PromotionReasonCode, target: str, digest: str = "", provider: str | None = None,
            objects: tuple[PromotedObjectEvidence, ...] = (), events: tuple[ReleaseEvent, ...] = (),
            attempted: bool = False) -> ProductionPromotionReport:
    return ProductionPromotionReport(False, reason, attempted, provider, target, digest, objects, events, "")


__all__ = ["OwnerPromotionApproval", "ProductionManifestPrecondition", "ProductionPromotionReport",
           "PromotionReasonCode", "PromotedObjectEvidence", "promote_verified_staging_to_production"]
