from __future__ import annotations

import hashlib
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from scrubbots_content_pipeline.config import Environment, PRODUCTION_TARGET
from scrubbots_content_pipeline.manifest_history import ManifestHistoryV1, append_manifest_history
from scrubbots_content_pipeline.production_manifest_activation import (
    ProductionManifestReasonCode, activate_versioned_production_manifest,
)
from scrubbots_content_pipeline.production_promotion import (
    ProductionManifestPrecondition, promote_verified_staging_to_production,
)
from scrubbots_content_pipeline.release_state import ReleaseState
from test_sb_cp03_007_staging_download_verify import _candidate, MANIFEST_KEY
from test_sb_cp03_008_production_promotion import _case


SCHEMA_SUPPORT = {"scrubbots.content.manifest.v1": (1,)}


def _activated_case():
    args, provider = _case()
    promoted = promote_verified_staging_to_production(**args)
    assert promoted.accepted and not promoted.manifest_write_attempted
    candidate = _candidate()
    activation_args = dict(
        staging_report=args["staging_report"], staging_pack_bytes=args["downloaded_pack_bytes"],
        pack_builds=candidate.pack_builds, promotion_report=promoted,
        replay_receipt=args["replay_receipt"], owner_approval=args["owner_approval"],
        owner_approval_check=args["owner_approval_check"], game_authority_check=args["game_authority_check"],
        production_target_id=PRODUCTION_TARGET.logical_target_id, manifest_object_key=MANIFEST_KEY,
        precondition=args["precondition"], manifest_history=ManifestHistoryV1(),
        release_events=args["release_events"], recorded_at_utc="2026-10-07T00:00:00Z",
        current_game_version="2.4.1", supported_manifest_schema_versions=SCHEMA_SUPPORT,
        provider=provider,
    )
    return activation_args, provider, promoted, candidate


def test_activates_exact_staging_manifest_after_write_readback_and_appends_m13_m11_history():
    args, provider, promoted, candidate = _activated_case()
    result = activate_versioned_production_manifest(**args)
    assert result.accepted and result.reason_code is ProductionManifestReasonCode.ACTIVATED
    receipt = result.receipt
    assert receipt is not None
    assert receipt.manifest_bytes == args["staging_report"].receipt.manifest_bytes
    assert receipt.manifest_sha256 == promoted.manifest_sha256
    assert receipt.content_version == 3
    assert receipt.history_record.manifest_bytes == receipt.manifest_bytes
    assert receipt.manifest_history.records[-1] == receipt.history_record
    assert receipt.history_record.recorded_at_utc == "2026-10-07T00:00:00Z"
    assert receipt.packs and all(item.verified_before_write and item.verified_after_write for item in receipt.packs)
    assert receipt.reference_validation.eligible and receipt.compatibility.compatible
    assert receipt.production_promoted_event.to_state is ReleaseState.PRODUCTION_PROMOTED
    assert result.release_event == receipt.production_promoted_event
    calls = [call[0] for call in provider.calls]
    write_at = calls.index("manifest")
    assert calls.index("read") < write_at
    assert calls.index("read", write_at + 1) > write_at
    assert calls[-1] == "event"
    assert provider.objects[(Environment.PRODUCTION, MANIFEST_KEY)] == candidate.manifest_bytes


def test_manifest_cas_requires_history_digest_version_and_byte_identity():
    args, provider, _, candidate = _activated_case()
    old = replace(candidate.manifest, content_version=2).to_json_bytes()
    history = append_manifest_history(ManifestHistoryV1(), old, recorded_at_utc="2026-10-06T12:00:00Z")
    args["manifest_history"] = history
    args["precondition"] = ProductionManifestPrecondition(PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY,
        hashlib.sha256(old).hexdigest(), 2, old)
    provider.objects[(Environment.PRODUCTION, MANIFEST_KEY)] = old
    result = activate_versioned_production_manifest(**args)
    assert result.accepted and result.receipt is not None and result.receipt.prior_content_version == 2
    assert result.receipt.content_version == 3

    args, provider, _, candidate = _activated_case()
    equal_version = replace(candidate.manifest, content_version=3).to_json_bytes()
    args["manifest_history"] = append_manifest_history(ManifestHistoryV1(), equal_version,
                                                       recorded_at_utc="2026-10-06T12:00:00Z")
    args["precondition"] = ProductionManifestPrecondition(PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY,
        hashlib.sha256(equal_version).hexdigest(), 3, equal_version)
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.VERSION_NOT_INCREASED
    assert not any(call[0] == "manifest" for call in provider.calls)


def test_stale_or_unaccepted_promotion_and_owner_or_game_drift_block_activation():
    args, provider, promoted, _ = _activated_case()
    args["promotion_report"] = replace(promoted, accepted=False)
    assert activate_versioned_production_manifest(**args).reason_code is ProductionManifestReasonCode.PACK_PROMOTION_NOT_ACCEPTED
    assert not any(call[0] == "manifest" for call in provider.calls)

    args, provider, _, _ = _activated_case()
    replay = args["replay_receipt"]
    bad_pack = {**replay.pack_results[0], "pack_sha256": "0" * 64}
    args["replay_receipt"] = replace(replay, pack_results=(bad_pack, *replay.pack_results[1:]))
    assert activate_versioned_production_manifest(**args).reason_code is ProductionManifestReasonCode.GAME_AUTHORITY_STALE
    assert not any(call[0] == "manifest" for call in provider.calls)

    args, provider, _, _ = _activated_case()
    args["owner_approval_check"] = lambda: None
    assert activate_versioned_production_manifest(**args).reason_code is ProductionManifestReasonCode.OWNER_APPROVAL_LOST
    assert not any(call[0] == "manifest" for call in provider.calls)

    args, provider, _, _ = _activated_case()
    current = args["game_authority_check"]()
    stale = {**current, "commit": "b" * 40}
    args["game_authority_check"] = lambda: stale
    assert activate_versioned_production_manifest(**args).reason_code is ProductionManifestReasonCode.GAME_AUTHORITY_STALE
    assert not any(call[0] == "manifest" for call in provider.calls)


def test_production_pack_readback_and_app_compatibility_gate_prevent_manifest_write():
    args, provider, _, _ = _activated_case()
    provider.objects[(Environment.PRODUCTION, args["staging_report"].receipt.packs[0].object_key)] = b"tampered"
    assert activate_versioned_production_manifest(**args).reason_code is ProductionManifestReasonCode.PRODUCTION_PACK_MISMATCH
    assert not any(call[0] == "manifest" for call in provider.calls)

    args, provider, _, _ = _activated_case()
    args["current_game_version"] = "1.0.0"
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.MANIFEST_NOT_COMPATIBLE
    assert not any(call[0] == "manifest" for call in provider.calls)


def test_conditional_conflict_and_post_write_mismatch_do_not_append_success_history_or_state():
    args, provider, _, _ = _activated_case()
    provider.fail_manifest = True
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.PROVIDER_CONFLICT
    assert result.manifest_write_attempted and result.receipt is None
    assert not any(call[0] == "event" and call[1] is ReleaseState.PRODUCTION_PROMOTED for call in provider.calls)

    args, provider, _, _ = _activated_case()
    provider.corrupt_manifest_after_write = True
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.PRODUCTION_MANIFEST_MISMATCH
    assert result.manifest_write_attempted and result.receipt is None
    assert not any(call[0] == "event" and call[1] is ReleaseState.PRODUCTION_PROMOTED for call in provider.calls)

    args, provider, _, _ = _activated_case()
    provider.corrupt_pack_after_write = True
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.PRODUCTION_PACK_MISMATCH
    assert result.manifest_write_attempted and result.receipt is None
    assert not any(call[0] == "event" and call[1] is ReleaseState.PRODUCTION_PROMOTED for call in provider.calls)


@pytest.mark.parametrize("bad_time", ["", "2026-10-07T03:00:00+03:00", "2026-13-07T03:00:00Z"])
def test_explicit_manifest_history_timestamp_must_be_canonical_utc(bad_time: str):
    args, provider, _, _ = _activated_case()
    args["recorded_at_utc"] = bad_time
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.INVALID_INPUT
    assert result.manifest_write_attempted
