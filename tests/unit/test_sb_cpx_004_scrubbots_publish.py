from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scrubbots_content_pipeline.one_command_publisher import PublisherMode, PublisherRunRequest
from scrubbots_content_pipeline.config import PipelineConfig
import scrubbots_publish_handoff as handoff


SHA = "a" * 40
AUTHORITY = {"repository": "Sekiph82/Scrubbots", "branch": "main", "commit": SHA,
             "source_sha256": {"project.godot": "b" * 64}}


def _request(**overrides):
    value = {"candidate_ids": ["accepted-1"], "pack_id": "levels-11-50", "content_version": 7,
             "created_at_utc": "2026-10-07T12:00:00Z"}
    value.update(overrides)
    return value


def _build(*_args, **_kwargs):
    return SimpleNamespace(evidence=SimpleNamespace(
        level_ids=("level-11",), pack_id="levels-11-50", archive_sha256="b" * 64,
        archive_byte_length=4321,
    ))


def _accepted_pool():
    return ({"schema": "scrubbots-release-pool-entry/v1", "candidate_id": "accepted-1",
             "review_id": "review-1", "pipeline_run_id": "run-1", "pipeline_sha256": "c" * 64,
             "pipeline": {"candidate_id": "accepted-1", "run_id": "run-1", "disposition": "READY",
                          "primary": {"state": "READY", "disposition": "READY"}}},)


def test_default_release_pool_import_uses_canonical_service_without_injection(monkeypatch):
    from scrubbots_pixel_factory.supply_pipeline import release_pool
    monkeypatch.setattr(release_pool, "release_entries", _accepted_pool)
    result = handoff.publish_preflight(_request(), pack_builder=_build,
                                       game_authority_reader=lambda: AUTHORITY)
    assert result["state"] == "PREFLIGHT_READY"
    assert result["mutation_performed"] is False
    assert result["reviewed_identity"]["candidate_ids"] == ["accepted-1"]
    assert result["reviewed_identity"]["packs"] == [{
        "pack_id": "levels-11-50", "sha256": "b" * 64, "byte_length": 4321}]
    assert result["reviewed_identity"]["scrubbots_main_sha"] == SHA
    assert result["reviewed_identity"]["bucket"] == handoff.R2_BUCKET
    assert result["reviewed_identity"]["public_read_base"] == handoff.PUBLIC_READ_BASE


@pytest.mark.parametrize("pool", [(), ({"candidate_id": "accepted-1", "pipeline": "READY"},)])
def test_empty_or_ready_only_release_pool_cannot_become_publishable(pool):
    result = handoff.publish_preflight(_request(), release_pool_reader=lambda: pool,
                                       pack_builder=_build, game_authority_reader=lambda: AUTHORITY)
    assert result["state"] == "AWAITING_OWNER_RELEASE_BATCH"
    assert result["mutation_performed"] is False


def test_stale_pipeline_identity_cannot_become_publishable():
    entry = dict(_accepted_pool()[0])
    entry["pipeline"] = {"candidate_id": "accepted-1", "run_id": "old-run", "disposition": "READY",
                          "primary": {"state": "READY", "disposition": "READY"}}
    result = handoff.publish_preflight(_request(), release_pool_reader=lambda: (entry,),
                                       pack_builder=_build, game_authority_reader=lambda: AUTHORITY)
    assert result["state"] == "AWAITING_OWNER_RELEASE_BATCH"
    assert result["mutation_performed"] is False


def test_preflight_identity_is_deterministic_and_authority_sha_is_not_owner_input():
    first = handoff.publish_preflight(_request(scrubbots_main_sha="f" * 40),
                                      release_pool_reader=_accepted_pool, pack_builder=_build,
                                      game_authority_reader=lambda: AUTHORITY)
    second = handoff.publish_preflight(_request(), release_pool_reader=_accepted_pool,
                                       pack_builder=_build, game_authority_reader=lambda: AUTHORITY)
    assert first["reviewed_identity"] == second["reviewed_identity"]
    assert first["scrubbots_main_sha"] == SHA
    assert first["mutation_performed"] is False


def test_serializable_publish_staging_revalidates_exact_review_and_assembles_typed_m14(monkeypatch):
    for name in ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(name, "test-only-configured")
    request = _request()
    preflight = handoff.publish_preflight(request, release_pool_reader=_accepted_pool,
                                          pack_builder=_build, game_authority_reader=lambda: AUTHORITY)
    request["reviewed_identity"] = preflight["reviewed_identity"]
    typed = PublisherRunRequest(PublisherMode.STAGING_ONLY, PipelineConfig())
    assembled = []
    monkeypatch.setattr(handoff, "_assemble_staging_request",
                        lambda values, **_kwargs: (assembled.append(dict(values)) or typed))
    seen = []
    class Report:
        accepted = True
        def to_dict(self):
            return {"accepted": True, "candidate_manifest_sha256": "c" * 64}
    result = handoff.publish_to_staging(
        request, release_pool_reader=_accepted_pool, pack_builder=_build,
        game_authority_reader=lambda: AUTHORITY, publisher_runner=lambda value: (seen.append(value) or Report()),
    )
    assert result["state"] == "STAGING_PUBLISHED", result
    assert result["production"] == "AWAITING_OWNER_PRODUCTION_PROMOTION"
    assert seen == [typed]
    assert assembled and assembled[0]["candidate_ids"] == ["accepted-1"]


def test_service_assembles_complete_typed_m14_request_and_stages_through_real_orchestrator(monkeypatch):
    import hashlib
    import json
    import importlib
    from scrubbots_content_pipeline import ScrubpackLevelInput, ScrubpackPayloadInput
    from scrubbots_content_pipeline import scrubpack_solver_identity
    from test_sb_cp03_006_staging_manifest_publish import EXAMPLES
    from test_sb_cp03_011_one_command_publisher import _request as m14_fixture
    import scrubbots_pixel_factory.supply_pipeline.scrubpack_identity as factory_identity
    import scrubbots_content_pipeline.one_command_publisher as orchestrator

    for name in ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(name, "test-only-configured")
    monkeypatch.setattr(orchestrator, "verify_solver_proven_scrubpack", lambda *_args: True)
    monkeypatch.setattr(scrubpack_solver_identity, "verify_solver_proven_scrubpack", lambda *_args: True)
    base_request, provider, _candidate, _approval, _authority = m14_fixture(PublisherMode.STAGING_ONLY)
    build = base_request.factory_pack_builder(base_request.factory_pack_requests[0])
    candidate_pool = ({"schema": "scrubbots-release-pool-entry/v1", "candidate_id": "candidate-accepted",
                       "review_id": "review-1", "pipeline_run_id": "run-1", "pipeline_sha256": "c" * 64,
                       "pipeline": {"candidate_id": "candidate-accepted", "run_id": "run-1", "disposition": "READY",
                                    "primary": {"state": "READY", "disposition": "READY"}}},)

    descriptor = json.loads((EXAMPLES / "level.json").read_text(encoding="utf-8"))
    payload_obj = {"version": 1, "id": "level-a", "name": "one-command fixture", "difficulty": "EASY",
                   "width": 20, "height": 20, "palette": ["#000000FF", "#FFFFFFFF"],
                   "cells": [0] * 399 + [1]}
    payload = json.dumps(payload_obj, separators=(",", ":")).encode()
    descriptor["attributes"]["level_id"] = "level-a"
    descriptor["attributes"]["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    level = ScrubpackPayloadInput(descriptor, payload)
    level_input = ScrubpackLevelInput("level-a", level, level, level)
    monkeypatch.setattr(factory_identity, "current_solver_proof_for_candidate", lambda _candidate: (b"{}", {}))
    builder_module = importlib.import_module("scripts.build_accepted_factory_output_pack")
    monkeypatch.setattr(builder_module, "_decode_object", lambda *_args, **_kwargs: {
        "primary": {"state": "READY", "disposition": "READY"}})
    monkeypatch.setattr(builder_module, "_level_input", lambda *_args, **_kwargs: ("level-a", level_input))

    values = _request(candidate_ids=["candidate-accepted"], pack_id="pack-a", content_version=2)
    preflight = handoff.publish_preflight(values, release_pool_reader=lambda: candidate_pool,
                                          pack_builder=lambda *_args, **_kwargs: build,
                                          game_authority_reader=lambda: AUTHORITY)
    values["reviewed_identity"] = preflight["reviewed_identity"]
    assembled = handoff._assemble_staging_request(
        values, provider_factory=lambda: provider, release_pool_reader=lambda: candidate_pool,
        pack_builder=lambda *_args, **_kwargs: build, game_authority_reader=lambda: AUTHORITY,
        reviewed_identity=values["reviewed_identity"])
    assert isinstance(assembled, PublisherRunRequest)
    assert assembled.mode is PublisherMode.STAGING_ONLY
    assert assembled.provider is provider and assembled.factory_pack_requests[0].candidate_ids == ("candidate-accepted",)
    result = handoff.publish_to_staging(
        values, release_pool_reader=lambda: candidate_pool,
        pack_builder=lambda *_args, **_kwargs: build,
        game_authority_reader=lambda: AUTHORITY, provider_factory=lambda: provider,
    )
    assert result["state"] == "STAGING_PUBLISHED", result
    assert result["m14"]["accepted"] is True
    assert result["m14"]["terminal_stage"] == "STAGING_DOWNLOAD_VERIFY"
    assert provider.objects
    assert result["production"] == "AWAITING_OWNER_PRODUCTION_PROMOTION"


def test_missing_writer_credentials_stop_before_assembly_or_mutation(monkeypatch):
    for name in ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        monkeypatch.delenv(name, raising=False)
    request = _request()
    preflight = handoff.publish_preflight(request, release_pool_reader=_accepted_pool,
                                          pack_builder=_build, game_authority_reader=lambda: AUTHORITY)
    request["reviewed_identity"] = preflight["reviewed_identity"]
    monkeypatch.setattr(handoff, "_assemble_staging_request",
                        lambda *_args, **_kwargs: pytest.fail("must stop before request assembly"))
    result = handoff.publish_to_staging(request, release_pool_reader=_accepted_pool,
                                        pack_builder=_build, game_authority_reader=lambda: AUTHORITY)
    assert result["state"] == "OWNER_R2_WRITE_CREDENTIAL_REQUIRED"
    assert result["mutation_performed"] is False


def test_stale_reviewed_identity_rejects_before_credentials_or_provider(monkeypatch):
    request = _request(reviewed_identity={"schema": "tampered"})
    result = handoff.publish_to_staging(request, release_pool_reader=_accepted_pool,
                                        pack_builder=_build, game_authority_reader=lambda: AUTHORITY)
    assert result["state"] == "REVIEWED_PREFLIGHT_STALE"
    assert result["mutation_performed"] is False


def test_headless_launcher_and_studio_expose_same_serializable_staging_action():
    launcher = (ROOT / "level_factory" / "scripts" / "factory_core_launcher.py").read_text(encoding="utf-8")
    studio = (ROOT / "level_factory" / "scripts" / "factory_studio_release.gd").read_text(encoding="utf-8")
    assert 'elif action == "publish-staging"' in launcher
    assert "publish_to_staging(request)" in launcher
    assert '"action": "publish-staging"' in studio
    assert '"Publish to STAGING"' in studio
    assert '"scrubbots_main_sha":' not in studio
