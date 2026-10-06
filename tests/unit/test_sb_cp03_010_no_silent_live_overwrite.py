from __future__ import annotations

import hashlib
import sys
import threading
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from scrubbots_content_pipeline.config import Environment, PRODUCTION_TARGET
from scrubbots_content_pipeline.manifest_history import ManifestHistoryV1, append_manifest_history
from scrubbots_content_pipeline.production_manifest_activation import (
    ProductionManifestReasonCode, activate_versioned_production_manifest,
)
from scrubbots_content_pipeline.production_promotion import ProductionManifestPrecondition
from scrubbots_content_pipeline.provider import ProviderResultCategory
from test_sb_cp03_009_production_manifest_activation import _activated_case, MANIFEST_KEY


def test_exact_repeat_is_already_current_only_with_m13_and_m11_promotion_proof():
    args, provider, _, _ = _activated_case()
    first = activate_versioned_production_manifest(**args)
    assert first.accepted and first.receipt is not None
    args["manifest_history"] = first.receipt.manifest_history
    args["precondition"] = ProductionManifestPrecondition(
        PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY, first.receipt.manifest_sha256,
        first.receipt.content_version, first.receipt.manifest_bytes)
    calls_before = len(provider.calls)
    ledger_before = tuple(provider.release_events)
    result = activate_versioned_production_manifest(**args)
    assert result.accepted and result.reason_code is ProductionManifestReasonCode.ALREADY_CURRENT
    assert not result.manifest_write_attempted
    assert len(provider.calls) == calls_before + 3  # two exact pack reads and the live manifest read
    assert tuple(provider.release_events) == ledger_before


def test_exact_live_bytes_without_m13_history_and_m11_promotion_proof_fail_closed():
    args, provider, _, _ = _activated_case()
    first = activate_versioned_production_manifest(**args)
    assert first.accepted and first.receipt is not None
    args["manifest_history"] = ManifestHistoryV1()
    args["precondition"] = ProductionManifestPrecondition(PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY,
                                                           None, None, None)
    ledger_before = tuple(provider.release_events)
    result = activate_versioned_production_manifest(**args)
    assert not result.accepted and result.reason_code is ProductionManifestReasonCode.PROVIDER_CONFLICT
    assert not result.manifest_write_attempted
    assert tuple(provider.release_events) == ledger_before


def test_changed_live_manifest_or_release_ledger_blocks_without_mutation():
    args, provider, _, _ = _activated_case()
    slot = (Environment.PRODUCTION, MANIFEST_KEY)
    provider.objects[slot] = b"another-live-manifest"
    object_before, ledger_before = provider.objects[slot], tuple(provider.release_events)
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.PROVIDER_CONFLICT
    assert provider.objects[slot] == object_before and tuple(provider.release_events) == ledger_before
    assert not any(call[0] == "manifest" for call in provider.calls)


def test_rejected_overwrite_preserves_existing_production_bytes_and_release_ledger():
    args, provider, _, candidate = _activated_case()
    prior_bytes = replace(candidate.manifest, content_version=2).to_json_bytes()
    args["manifest_history"] = append_manifest_history(
        ManifestHistoryV1(), prior_bytes, recorded_at_utc="2026-10-06T12:00:00Z")
    args["precondition"] = ProductionManifestPrecondition(
        PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY, hashlib.sha256(prior_bytes).hexdigest(), 2, prior_bytes)
    slot = (Environment.PRODUCTION, MANIFEST_KEY)
    provider.objects[slot] = prior_bytes
    provider.fail_manifest = True
    object_before, ledger_before = provider.objects[slot], tuple(provider.release_events)
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.PROVIDER_CONFLICT
    assert result.manifest_write_attempted
    assert provider.objects[slot] == object_before
    assert tuple(provider.release_events) == ledger_before

    args, provider, _, _ = _activated_case()
    provider.release_events.append(provider.release_events[-1])
    ledger_before = tuple(provider.release_events)
    result = activate_versioned_production_manifest(**args)
    assert result.reason_code is ProductionManifestReasonCode.PROVIDER_CONFLICT
    assert (Environment.PRODUCTION, MANIFEST_KEY) not in provider.objects
    assert tuple(provider.release_events) == ledger_before
    assert not any(call[0] == "manifest" for call in provider.calls)


def test_two_writers_with_same_expected_manifest_and_ledger_state_have_one_winner():
    args, provider, _, candidate = _activated_case()
    raw = candidate.manifest_bytes
    digest = hashlib.sha256(raw).hexdigest()
    events = tuple(provider.release_events)
    tip = events[-1].event_digest
    barrier = threading.Barrier(3)
    results = []

    def writer():
        barrier.wait()
        results.append(provider.write_manifest_conditionally(
            Environment.PRODUCTION, PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY, digest, raw,
            expected_prior_sha256=None, expected_prior_content_version=None,
            expected_release_state_sequence=len(events), expected_release_state_tip_digest=tip,
            promotion_pending_event_digest=args["promotion_report"].release_events[0].event_digest))

    workers = [threading.Thread(target=writer) for _ in range(2)]
    for worker in workers:
        worker.start()
    barrier.wait()
    for worker in workers:
        worker.join()
    assert sum(result.category is ProviderResultCategory.SUCCESS for result in results) == 1
    assert sum(result.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION for result in results) == 1
    assert provider.objects[(Environment.PRODUCTION, MANIFEST_KEY)] == raw
    assert tuple(provider.release_events) == events
