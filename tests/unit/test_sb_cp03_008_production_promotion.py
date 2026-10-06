from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from scrubbots_content_pipeline.config import Environment, PRODUCTION_TARGET
from scrubbots_content_pipeline.current_main_replay import AUTHORITY_SOURCE_PATHS, CurrentMainReplayReceipt, REPOSITORY
from scrubbots_content_pipeline.provider import (
    ProviderCapability, ProviderFeature, ProviderIdentity, ProviderObjectBytesResult,
    ProviderResult, ProviderResultCategory,
)
from scrubbots_content_pipeline.production_promotion import (
    OwnerPromotionApproval, ProductionManifestPrecondition, PromotionReasonCode,
    promote_verified_staging_to_production,
)
from scrubbots_content_pipeline.release_state import ReleaseState, make_release_event
from scrubbots_content_pipeline.staging_download_verify import StagingDownloadReasonCode, StagingDownloadVerificationReport
from scrubbots_content_pipeline.manifest_parser import parse_content_manifest_v1
from test_sb_cp03_007_staging_download_verify import _setup, MANIFEST_KEY, verify_staged_manifest_download


class PromotionMemoryProvider:
    identity = ProviderIdentity("memory-promotion", "1.0")
    capabilities = ProviderCapability(
        "memory-promotion-capability", "1.0", (Environment.PRODUCTION,),
        tuple(sorted((ProviderFeature.PRODUCTION_PROMOTION, ProviderFeature.CONDITIONAL_WRITE,
                      ProviderFeature.INTEGRITY_VERIFY, ProviderFeature.ATOMIC_MANIFEST_PUBLISH),
                     key=lambda item: item.value)),
    )

    def __init__(self, staging: dict[str, bytes]):
        self.objects = {(Environment.STAGING, key): value for key, value in staging.items()}
        self.calls: list[tuple] = []
        self.bad_production_key = False
        self.fail_manifest = False
        self.corrupt_manifest_after_write = False
        self.corrupt_pack_after_write = False

    def promote_object(self, source_environment, source_object_key, target_environment, target_object_key, expected_sha256):
        self.calls.append(("promote", source_environment, source_object_key, target_environment, target_object_key))
        raw = self.objects.get((source_environment, source_object_key))
        if raw is None or hashlib.sha256(raw).hexdigest() != expected_sha256:
            return ProviderResult("1.0", ProviderResultCategory.INTEGRITY_MISMATCH, self.identity.provider_id,
                                  target_environment, None)
        self.objects[(target_environment, target_object_key)] = raw
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id,
                              target_environment, expected_sha256)

    def read_object_bytes(self, environment, object_key):
        self.calls.append(("read", environment, object_key))
        raw = self.objects.get((environment, object_key))
        if self.bad_production_key and environment is Environment.PRODUCTION and raw is not None:
            key = "other/object"
        else:
            key = object_key
        return ProviderObjectBytesResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id,
                                         environment, key, raw)

    def append_release_event(self, event):
        self.calls.append(("event", event.to_state, event.event_digest))
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id,
                              Environment.PRODUCTION, event.event_digest)

    def write_manifest_conditionally(self, environment, target_id, object_key, content_digest, content_bytes,
                                     *, expected_prior_sha256, expected_prior_content_version,
                                     promotion_pending_event_digest):
        self.calls.append(("manifest", environment, object_key, promotion_pending_event_digest))
        slot = (environment, object_key)
        current = self.objects.get(slot)
        current_digest = hashlib.sha256(current).hexdigest() if current is not None else None
        current_version = json.loads(current.decode("utf-8")).get("content_version") if current is not None else None
        if (self.fail_manifest or current_digest != expected_prior_sha256
                or current_version != expected_prior_content_version):
            return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                  self.identity.provider_id, environment, current_digest)
        if hashlib.sha256(content_bytes).hexdigest() != content_digest:
            return ProviderResult("1.0", ProviderResultCategory.INTEGRITY_MISMATCH,
                                  self.identity.provider_id, environment, None)
        if self.corrupt_manifest_after_write:
            content_bytes = content_bytes + b" "
        self.objects[(environment, object_key)] = content_bytes
        if self.corrupt_pack_after_write:
            pack_slot = next((key for env, key in self.objects if env is Environment.PRODUCTION
                              and key.startswith("packs/")), None)
            if pack_slot is not None:
                self.objects[(Environment.PRODUCTION, pack_slot)] = b"changed-after-manifest-write"
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id,
                              environment, content_digest)


def _case():
    candidate, stage_receipt, source_reader = _setup()
    staging = verify_staged_manifest_download(candidate=candidate, staging_receipt=stage_receipt,
                                               provider=source_reader)
    assert staging.accepted and staging.receipt is not None
    exact = {row.pack_id: source_reader.objects[row.object_key] for row in staging.receipt.packs}
    digest = staging.receipt.manifest_sha256
    content_id = f"manifest-v{staging.receipt.content_version}-{digest[:16]}"
    record = f"staging-{digest[:32]}"
    history = []
    prior = "0" * 64
    for seq, state, before in ((1, ReleaseState.DRAFT, None), (2, ReleaseState.VALIDATED, ReleaseState.DRAFT),
                               (3, ReleaseState.STAGED, ReleaseState.VALIDATED)):
        event = make_release_event(sequence=seq, event_id=f"stage-{seq}-{digest[:8]}",
            transition_id=f"stage-transition-{seq}-{digest[:8]}", record_id=record, content_id=content_id,
            content_digest=digest, environment=Environment.STAGING, from_state=before, to_state=state,
            expected_state=before, previous_event_digest=prior)
        history.append(event)
        prior = event.event_digest
    staging = replace(staging, receipt=replace(staging.receipt,
        release_event_digests=tuple(event.event_digest for event in history)))
    packs = tuple({"pack_id": row.pack_id, "pack_sha256": row.sha256,
                   "levels": [{"level_id": level, "accepted": True, "solver_status": "SOLVED",
                               "replay_ok": True, "replay_solved": True, "final_active": 0,
                               "unresolved": 0, "supply_exhausted": True}
                              for level in row.level_ids]} for row in staging.receipt.packs)
    authority = {path: hashlib.sha256(path.encode()).hexdigest() for path in AUTHORITY_SOURCE_PATHS}
    replay = CurrentMainReplayReceipt(True, "VERIFIED", REPOSITORY, "main", "a" * 40, authority,
                                     digest, packs)
    approval = OwnerPromotionApproval("approval-1", "owner-1", digest,
                                     staging.receipt.content_version, PRODUCTION_TARGET.logical_target_id)
    provider = PromotionMemoryProvider({**{row.object_key: exact[row.pack_id]
                                          for row in staging.receipt.packs},
                                       MANIFEST_KEY: staging.receipt.manifest_bytes})
    precondition = ProductionManifestPrecondition(PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY,
                                                   None, None, None)
    current_authority = {"repository": REPOSITORY, "branch": "main", "commit": "a" * 40,
                         "source_sha256": authority}
    args = dict(staging_report=staging, downloaded_pack_bytes=exact, replay_receipt=replay,
                owner_approval=approval, owner_approval_check=lambda: approval,
                game_authority_check=lambda: current_authority, target_id=PRODUCTION_TARGET.logical_target_id,
                manifest_object_key=MANIFEST_KEY, precondition=precondition,
                release_events=tuple(history), provider=provider)
    return args, provider


def test_promotes_all_exact_pack_objects_and_re_reads_them_before_manifest_activation():
    args, provider = _case()
    result = promote_verified_staging_to_production(**args)
    assert result.accepted and result.reason_code is PromotionReasonCode.PROMOTED
    assert not result.manifest_write_attempted
    assert len(result.promoted_objects) == 2 and all(item.verified for item in result.promoted_objects)
    assert [call[0] for call in provider.calls].count("promote") == 2
    assert [call[0] for call in provider.calls].count("read") == 2
    assert provider.calls[-1][0] == "event" and provider.calls[-1][1] is ReleaseState.PROMOTION_PENDING
    assert max(i for i, call in enumerate(provider.calls) if call[0] == "promote") < min(
        i for i, call in enumerate(provider.calls) if call[0] == "read")
    assert max(i for i, call in enumerate(provider.calls) if call[0] == "read") < next(
        i for i, call in enumerate(provider.calls) if call[0] == "event" and call[1] is ReleaseState.PROMOTION_PENDING
    ) < len(provider.calls)
    assert not any(call[0] == "manifest" for call in provider.calls)
    assert [item.to_state for item in result.release_events] == [ReleaseState.PROMOTION_PENDING,
                                                                ]


def test_missing_cpx_receipt_or_owner_approval_blocks_before_provider_calls():
    args, provider = _case()
    args["replay_receipt"] = None
    assert promote_verified_staging_to_production(**args).reason_code is PromotionReasonCode.REPLAY_NOT_ACCEPTED
    assert provider.calls == []
    args, provider = _case()
    args["owner_approval"] = None
    assert promote_verified_staging_to_production(**args).reason_code is PromotionReasonCode.OWNER_APPROVAL_REQUIRED
    assert provider.calls == []


def test_loss_of_owner_approval_after_pack_verification_withholds_manifest():
    args, provider = _case()
    approval = args["owner_approval"]
    checks = iter((approval, None))
    args["owner_approval_check"] = lambda: next(checks)
    result = promote_verified_staging_to_production(**args)
    assert result.reason_code is PromotionReasonCode.OWNER_APPROVAL_LOST
    assert not result.manifest_write_attempted
    assert [call[0] for call in provider.calls].count("manifest") == 0
    assert [event.to_state for event in result.release_events] == [ReleaseState.PROMOTION_PENDING]


def test_production_object_identity_mismatch_and_game_source_drift_block_manifest():
    args, provider = _case()
    provider.bad_production_key = True
    result = promote_verified_staging_to_production(**args)
    assert result.reason_code is PromotionReasonCode.PRODUCTION_OBJECT_MISMATCH
    assert not any(call[0] == "manifest" for call in provider.calls)
    args, provider = _case()
    good_authority = args["game_authority_check"]()
    drifted_authority = {"repository": REPOSITORY, "branch": "main", "commit": "b" * 40,
                         "source_sha256": args["replay_receipt"].authority_source_sha256}
    checks = iter((good_authority, drifted_authority))
    args["game_authority_check"] = lambda: next(checks)
    result = promote_verified_staging_to_production(**args)
    assert result.reason_code is PromotionReasonCode.GAME_AUTHORITY_STALE
    assert [call[0] for call in provider.calls].count("promote") == 2
    assert [call[0] for call in provider.calls].count("event") == 1
    assert not any(call[0] == "manifest" for call in provider.calls)


def test_pack_promotion_does_not_write_production_manifest():
    args, provider = _case()
    result = promote_verified_staging_to_production(**args)
    assert result.accepted and not result.manifest_write_attempted
    assert [event.to_state for event in result.release_events] == [ReleaseState.PROMOTION_PENDING]
    assert not any(call[0] == "manifest" for call in provider.calls)
    assert not any(call[0] == "delete" for call in provider.calls)


def test_capability_direct_production_and_stale_staging_receipt_are_rejected_before_mutation():
    args, provider = _case()
    provider.capabilities = ProviderCapability("no-promotion", "1.0", (Environment.PRODUCTION,),
                                                (ProviderFeature.INTEGRITY_VERIFY,))
    assert promote_verified_staging_to_production(**args).reason_code is PromotionReasonCode.CAPABILITY_REJECTED
    assert provider.calls == []
    args, provider = _case()
    args["target_id"] = "staging:default"
    args["precondition"] = replace(args["precondition"], target_id="staging:default")
    assert promote_verified_staging_to_production(**args).reason_code is PromotionReasonCode.MANIFEST_PRECONDITION_FAILED
    assert provider.calls == []
    args, provider = _case()
    args["staging_report"] = replace(args["staging_report"], accepted=False)
    assert promote_verified_staging_to_production(**args).reason_code is PromotionReasonCode.STAGING_NOT_VERIFIED
    assert provider.calls == []
    args, provider = _case()
    args["staging_report"] = replace(args["staging_report"], capability_negotiation=None)
    assert promote_verified_staging_to_production(**args).reason_code is PromotionReasonCode.STAGING_NOT_VERIFIED
    assert provider.calls == []


def test_production_manifest_content_version_must_be_a_cas_successor():
    args, provider = _case()
    current = parse_content_manifest_v1(args["staging_report"].receipt.manifest_bytes)
    prior = replace(current, content_version=current.content_version).to_json_bytes()
    args["precondition"] = ProductionManifestPrecondition(
        PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY, hashlib.sha256(prior).hexdigest(),
        current.content_version, prior)
    assert promote_verified_staging_to_production(**args).reason_code is PromotionReasonCode.MANIFEST_PRECONDITION_FAILED
    assert provider.calls == []
