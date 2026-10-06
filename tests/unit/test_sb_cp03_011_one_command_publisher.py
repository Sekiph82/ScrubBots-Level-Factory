from __future__ import annotations

import hashlib
import json
import sys
import threading
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

import scrubbots_content_pipeline.one_command_publisher as orchestrator
from scrubbots_content_pipeline.config import (
    PRODUCTION_TARGET, STAGING_TARGET, Environment, PipelineConfig,
)
from scrubbots_content_pipeline.current_main_replay import AUTHORITY_SOURCE_PATHS, CurrentMainReplayReceipt
from scrubbots_content_pipeline.manifest_v1 import CONTENT_MANIFEST_SCHEMA
from scrubbots_content_pipeline import scrubpack_solver_identity
from scrubbots_content_pipeline.production_promotion import (
    OwnerPromotionApproval, ProductionManifestPrecondition,
)
from scrubbots_content_pipeline.provider import (
    ProviderCapability, ProviderFeature, ProviderIdentity, ProviderObjectBytesResult,
    ProviderResult, ProviderResultCategory,
)
from scrubbots_content_pipeline.publication_plan import build_publication_plan
from scrubbots_content_pipeline.release_state import replay_release_events
from scrubbots_content_pipeline.scrubpack_builder import ScrubpackBuildResult
from scrubbots_content_pipeline.staging_manifest_publish import StagingManifestPrecondition
from scrubbots_content_pipeline.payload_validation import validate_remote_payload
from test_sb_cp03_006_staging_manifest_publish import EXAMPLES, _build

MANIFEST_KEY = "manifests/current.json"


class PipelineMemoryProvider:
    identity = ProviderIdentity("cp03-011-memory", "1.0")
    capabilities = ProviderCapability(
        "cp03-011-capability", "1.0", tuple(sorted((Environment.STAGING, Environment.PRODUCTION),
                                                    key=lambda item: item.value)),
        tuple(sorted((ProviderFeature.STAGING_PUBLISH, ProviderFeature.OBJECT_WRITE,
                      ProviderFeature.INTEGRITY_VERIFY, ProviderFeature.CONDITIONAL_WRITE,
                      ProviderFeature.ATOMIC_MANIFEST_PUBLISH, ProviderFeature.PRODUCTION_PROMOTION),
                     key=lambda item: item.value)),
    )

    def __init__(self):
        self.objects: dict[tuple[Environment, str], bytes] = {}
        self.release_events = []
        self.calls: list[tuple] = []
        self.lock = threading.Lock()
        self.fail_pack_write = False

    def read_release_events(self):
        return tuple(self.release_events)

    def write_object_bytes(self, environment, object_key, content_digest, content_bytes, *, if_absent):
        self.calls.append(("object-write", environment, object_key))
        if self.fail_pack_write or environment is not Environment.STAGING or if_absent is not True:
            return ProviderResult("1.0", ProviderResultCategory.TRANSIENT_FAILURE,
                                  self.identity.provider_id, environment)
        slot = (environment, object_key)
        if slot in self.objects:
            digest = hashlib.sha256(self.objects[slot]).hexdigest()
            return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                  self.identity.provider_id, environment, digest)
        digest = hashlib.sha256(content_bytes).hexdigest()
        if digest != content_digest:
            return ProviderResult("1.0", ProviderResultCategory.INTEGRITY_MISMATCH,
                                  self.identity.provider_id, environment)
        self.objects[slot] = bytes(content_bytes)
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS,
                              self.identity.provider_id, environment, digest)

    def verify_object(self, environment, object_key, expected_digest):
        self.calls.append(("object-verify", environment, object_key))
        raw = self.objects.get((environment, object_key))
        digest = hashlib.sha256(raw).hexdigest() if raw is not None else None
        category = ProviderResultCategory.SUCCESS if digest == expected_digest else ProviderResultCategory.INTEGRITY_MISMATCH
        return ProviderResult("1.0", category, self.identity.provider_id, environment, digest)

    def read_object_bytes(self, environment, object_key):
        self.calls.append(("object-read", environment, object_key))
        raw = self.objects.get((environment, object_key))
        return ProviderObjectBytesResult(
            "1.0", ProviderResultCategory.SUCCESS,
            self.identity.provider_id, environment, object_key, raw,
        )

    def write_manifest_conditionally(
        self, environment, target_id, object_key, content_digest, content_bytes, *,
        expected_prior_sha256, expected_prior_content_version=None,
        expected_release_state_sequence=None, expected_release_state_tip_digest=None,
        promotion_pending_event_digest=None,
    ):
        self.calls.append(("manifest-write", environment, object_key))
        slot = (environment, object_key)
        with self.lock:
            old = self.objects.get(slot)
            old_digest = hashlib.sha256(old).hexdigest() if old is not None else None
            if old_digest != expected_prior_sha256:
                return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                      self.identity.provider_id, environment, old_digest)
            if environment is Environment.PRODUCTION:
                old_version = json.loads(old.decode("utf-8")).get("content_version") if old is not None else None
                tip = self.release_events[-1].event_digest if self.release_events else "0" * 64
                if (old_version != expected_prior_content_version
                        or len(self.release_events) != expected_release_state_sequence
                        or tip != expected_release_state_tip_digest
                        or tip != promotion_pending_event_digest):
                    return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                          self.identity.provider_id, environment, old_digest)
            digest = hashlib.sha256(content_bytes).hexdigest()
            if digest != content_digest:
                return ProviderResult("1.0", ProviderResultCategory.INTEGRITY_MISMATCH,
                                      self.identity.provider_id, environment)
            self.objects[slot] = bytes(content_bytes)
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS,
                              self.identity.provider_id, environment, content_digest)

    def promote_object(self, source_environment, source_object_key, target_environment,
                       target_object_key, expected_sha256):
        self.calls.append(("promote", source_environment, source_object_key, target_environment, target_object_key))
        raw = self.objects.get((source_environment, source_object_key))
        if raw is None or hashlib.sha256(raw).hexdigest() != expected_sha256:
            return ProviderResult("1.0", ProviderResultCategory.INTEGRITY_MISMATCH,
                                  self.identity.provider_id, target_environment)
        self.objects[(target_environment, target_object_key)] = raw
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS,
                              self.identity.provider_id, target_environment, expected_sha256)

    def append_release_event(self, event, *, expected_prior_sequence, expected_prior_event_digest):
        self.calls.append(("event", event.to_state, event.event_digest))
        with self.lock:
            tip = self.release_events[-1].event_digest if self.release_events else "0" * 64
            if (len(self.release_events) != expected_prior_sequence or tip != expected_prior_event_digest
                    or not replay_release_events((*self.release_events, event)).accepted):
                return ProviderResult("1.0", ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                      self.identity.provider_id, event.environment, tip)
            self.release_events.append(event)
        return ProviderResult("1.0", ProviderResultCategory.SUCCESS,
                              self.identity.provider_id, event.environment, event.event_digest)


def _request(mode=orchestrator.PublisherMode.STAGING_ONLY, *, production=None):
    provider = PipelineMemoryProvider()
    build = _build("pack-a", "level-a")
    identity_bytes = json.dumps(
        {"schema": "scrubbots.solver_identity.v1", "version": 1,
         "pack_sha256": build.evidence.archive_sha256,
         "levels": [{"source": {"candidate_id": "candidate-accepted"}}]},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8") + b"\n"
    build = ScrubpackBuildResult(
        build.archive_bytes,
        replace(build.evidence, solver_identity_artifact_sha256=hashlib.sha256(identity_bytes).hexdigest()),
        identity_bytes,
    )
    candidate = orchestrator.build_candidate_manifest(
        (build,), content_version=3, minimum_game_version="2.4.0",
        object_keys={"pack-a": "packs/pack-a/v2.scrubpack"},
        current_game_version="2.4.1", supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: (1,)},
        prior_accepted_content_version=2,
    )
    descriptor = json.loads((EXAMPLES / "level.json").read_text(encoding="utf-8"))
    level_id = build.evidence.level_ids[0]
    payload_obj = {
        "version": 1, "id": level_id, "name": "one-command fixture", "difficulty": "EASY",
        "width": 20, "height": 20, "palette": ["#000000FF", "#FFFFFFFF"],
        "cells": [0] * 399 + [1],
    }
    payload = json.dumps(payload_obj, separators=(",", ":")).encode()
    descriptor["attributes"]["level_id"] = level_id
    descriptor["attributes"]["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    payload_result = validate_remote_payload(descriptor, payload)
    current_release_replay = replay_release_events(())
    plan = build_publication_plan(
        descriptor=descriptor, payload=payload, payload_result=payload_result,
        target=STAGING_TARGET, replay=current_release_replay, current_state=None,
        capability=provider.capabilities, owner_approved=True,
    )
    approval = OwnerPromotionApproval(
        "approval-cp03-011", "owner-test", candidate.manifest_sha256, 3,
        PRODUCTION_TARGET.logical_target_id,
    )
    source_hashes = {path: "c" * 64 for path in AUTHORITY_SOURCE_PATHS}
    authority = {"repository": "Sekiph82/Scrubbots", "branch": "main",
                 "commit": "a" * 40, "source_sha256": source_hashes}
    production_inputs = production or orchestrator.ProductionRunInputs(
        authority, lambda: authority, lambda _levels: {"accepted": False, "levels": []},
        approval, lambda: approval,
        ProductionManifestPrecondition(PRODUCTION_TARGET.logical_target_id, MANIFEST_KEY, None, None, None),
        orchestrator.ManifestHistoryV1(), "2026-10-07T00:00:00Z",
    )
    request = orchestrator.PublisherRunRequest(
        mode=mode, config=PipelineConfig(), provider=provider,
        factory_pack_requests=(orchestrator.FactoryPackRequest(("candidate-accepted",), "pack-a", 2,
                                                               "2026-10-07T00:00:00Z"),),
        factory_pack_builder=lambda _request: build,
        content_version=3, previous_content_version=2, minimum_game_version="2.4.0",
        current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: (1,)},
        object_keys={"pack-a": "packs/pack-a/v2.scrubpack"}, publication_plan=plan,
        current_content_digest=plan.content_digest, owner_approved=True,
        staging_precondition=StagingManifestPrecondition(
            STAGING_TARGET.logical_target_id, MANIFEST_KEY, False, None, None, None),
        manifest_object_key=MANIFEST_KEY, production=production_inputs,
    )
    return request, provider, candidate, approval, authority


def test_validation_only_is_callable_without_provider_or_factory_adapter_and_journal_is_deterministic():
    request = orchestrator.PublisherRunRequest(
        orchestrator.PublisherMode.VALIDATION_ONLY, PipelineConfig())
    first = orchestrator.run_one_command_publisher(request)
    second = orchestrator.run_one_command_publisher(request)
    assert first.accepted and first.terminal_stage is orchestrator.PublisherStage.CONFIG_VALIDATION
    assert first.staging_upload is None and first.production_activation is None
    assert orchestrator.serialize_publisher_journal(first) == orchestrator.serialize_publisher_journal(second)
    assert len(first.journal) == 1


def test_staging_only_composes_all_staging_gates_and_never_touches_production(monkeypatch):
    monkeypatch.setattr(orchestrator, "verify_solver_proven_scrubpack", lambda *_args: True)
    monkeypatch.setattr(scrubpack_solver_identity, "verify_solver_proven_scrubpack", lambda *_args: True)
    request, provider, _, _, _ = _request()
    result = orchestrator.run_one_command_publisher(request)
    assert result.accepted and result.staging_download is not None and result.staging_download.accepted
    assert result.terminal_stage is orchestrator.PublisherStage.STAGING_DOWNLOAD_VERIFY
    stages = [item.stage for item in result.journal]
    assert stages == [
        orchestrator.PublisherStage.CONFIG_VALIDATION,
        orchestrator.PublisherStage.REQUEST_PREFLIGHT,
        orchestrator.PublisherStage.FACTORY_PACK_BUILD,
        orchestrator.PublisherStage.CANDIDATE_MANIFEST,
        orchestrator.PublisherStage.PUBLISHER_VALIDATION,
        orchestrator.PublisherStage.RELEASE_HISTORY_PREFLIGHT,
        orchestrator.PublisherStage.STAGING_PACK_UPLOAD,
        orchestrator.PublisherStage.STAGING_OBJECT_INTEGRITY,
        orchestrator.PublisherStage.STAGING_MANIFEST_PUBLISH,
        orchestrator.PublisherStage.STAGING_RELEASE_STATE,
        orchestrator.PublisherStage.STAGING_DOWNLOAD_VERIFY,
    ]
    assert not any(call[0] == "promote" for call in provider.calls)
    assert (Environment.PRODUCTION, MANIFEST_KEY) not in provider.objects


def test_production_mode_composes_cpx002_through_no_silent_overwrite_fence(monkeypatch):
    monkeypatch.setattr(orchestrator, "verify_solver_proven_scrubpack", lambda *_args: True)
    monkeypatch.setattr(scrubpack_solver_identity, "verify_solver_proven_scrubpack", lambda *_args: True)
    request, provider, candidate, approval, authority = _request(orchestrator.PublisherMode.PRODUCTION)

    def current_main(**kwargs):
        pack = kwargs["staging_report"].receipt.packs[0]
        row = {
            "pack_id": pack.pack_id, "pack_sha256": pack.sha256,
            "levels": [{"level_id": level_id, "accepted": True, "solver_status": "SOLVED",
                        "replay_ok": True, "replay_solved": True, "final_active": 0,
                        "unresolved": 0, "supply_exhausted": True}
                       for level_id in pack.level_ids],
        }
        return CurrentMainReplayReceipt(True, "VERIFIED", "Sekiph82/Scrubbots", "main",
                                        "a" * 40, authority["source_sha256"],
                                        candidate.manifest_sha256, (row,))

    monkeypatch.setattr(orchestrator, "verify_current_main_supply_replay", current_main)
    result = orchestrator.run_one_command_publisher(request)
    assert result.accepted and result.production_activation is not None, (
        result.terminal_stage, [entry.reason_code for entry in result.journal],
        provider.calls, provider.release_events)
    assert result.production_activation.reason_code is orchestrator.ProductionManifestReasonCode.ACTIVATED
    assert [entry.stage for entry in result.journal][-4:] == [
        orchestrator.PublisherStage.CURRENT_MAIN_REPLAY,
        orchestrator.PublisherStage.PRODUCTION_PACK_PROMOTION,
        orchestrator.PublisherStage.PRODUCTION_MANIFEST_ACTIVATION,
        orchestrator.PublisherStage.CURRENT_STATE_FENCE,
    ]
    assert provider.objects[(Environment.PRODUCTION, MANIFEST_KEY)] == candidate.manifest_bytes
    assert provider.release_events[-1].to_state.value == "PRODUCTION_PROMOTED"
    assert result.production_promotion is not None and result.production_promotion.accepted
    assert result.current_main_replay is not None and result.current_main_replay.accepted
    assert result.publisher_validation is not None and result.publisher_validation.accepted
    assert result.staging_upload is not None and result.staging_publish is not None
    assert result.staging_download is not None and result.replay_pack_bytes
    assert approval.manifest_sha256 == candidate.manifest_sha256


def test_missing_explicit_owner_approval_blocks_before_factory_or_provider_work(monkeypatch):
    called = []
    request, provider, _, _, _ = _request(orchestrator.PublisherMode.PRODUCTION, production=None)
    request = replace(request, production=replace(request.production, owner_approval=None))
    request = replace(request, factory_pack_builder=lambda _request: called.append(True))
    monkeypatch.setattr(orchestrator, "verify_solver_proven_scrubpack", lambda *_args: True)
    monkeypatch.setattr(scrubpack_solver_identity, "verify_solver_proven_scrubpack", lambda *_args: True)
    result = orchestrator.run_one_command_publisher(request)
    assert not result.accepted and result.reason_code == "EXPLICIT_PRODUCTION_AUTHORITY_REQUIRED"
    assert not called and provider.calls == []


def test_first_staging_failure_stops_and_leaves_production_unchanged(monkeypatch):
    monkeypatch.setattr(orchestrator, "verify_solver_proven_scrubpack", lambda *_args: True)
    monkeypatch.setattr(scrubpack_solver_identity, "verify_solver_proven_scrubpack", lambda *_args: True)
    request, provider, _, _, _ = _request(orchestrator.PublisherMode.PRODUCTION)
    provider.fail_pack_write = True
    result = orchestrator.run_one_command_publisher(request)
    assert not result.accepted and result.terminal_stage is orchestrator.PublisherStage.STAGING_PACK_UPLOAD
    assert result.staging_publish is None and result.production_promotion is None
    assert (Environment.PRODUCTION, MANIFEST_KEY) not in provider.objects
    assert not any(call[0] == "promote" or
                   (call[0] == "manifest-write" and call[1] is Environment.PRODUCTION)
                   for call in provider.calls)
