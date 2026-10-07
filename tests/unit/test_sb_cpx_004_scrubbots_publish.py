from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(ROOT / "tests" / "unit"))
sys.path.insert(0, str(ROOT / "scripts"))

from scrubbots_content_pipeline.config import PipelineConfig
from scrubbots_content_pipeline.one_command_publisher import PublisherMode, PublisherRunRequest
from scrubbots_publish_handoff import PUBLIC_READ_BASE, R2_BUCKET, publish_preflight, run_m14_handoff


SHA = "a" * 40


def _request(**overrides):
    value = {"candidate_ids": ["accepted-1"], "pack_id": "levels-11-50", "content_version": 7,
             "scrubbots_main_sha": SHA, "created_at_utc": "2026-10-07T12:00:00Z"}
    value.update(overrides)
    return value


def _build(*_args, **_kwargs):
    return SimpleNamespace(evidence=SimpleNamespace(
        level_ids=("level-11",), pack_id="levels-11-50", archive_sha256="b" * 64,
        archive_byte_length=4321,
    ))


def test_empty_or_unaccepted_release_pool_cannot_become_publishable():
    empty = publish_preflight(_request(), release_pool_reader=lambda: (), pack_builder=_build,
                              game_authority_reader=lambda: SHA)
    ready_only = publish_preflight(_request(), release_pool_reader=lambda: ({"candidate_id": "ready-only"},), pack_builder=_build,
                                   game_authority_reader=lambda: SHA)
    assert empty["state"] == "AWAITING_OWNER_RELEASE_BATCH"
    assert ready_only["state"] == "AWAITING_OWNER_RELEASE_BATCH"
    assert empty["mutation_performed"] is ready_only["mutation_performed"] is False


def test_owner_accepted_fixture_preflight_displays_exact_pack_and_is_mutation_free():
    result = publish_preflight(_request(), release_pool_reader=lambda: ({"candidate_id": "accepted-1"},),
                               pack_builder=_build, game_authority_reader=lambda: SHA)
    assert result["state"] == "PREFLIGHT_READY"
    assert result["mutation_performed"] is False
    assert result["content_version"] == 7 and result["level_ids"] == ["level-11"]
    assert result["packs"] == [{"pack_id": "levels-11-50", "sha256": "b" * 64, "byte_length": 4321}]
    assert result["scrubbots_main_sha"] == SHA
    assert result["bucket"] == R2_BUCKET and result["public_read_base"] == PUBLIC_READ_BASE


def test_m14_handoff_requires_typed_request_and_secure_writer_environment(monkeypatch):
    request = PublisherRunRequest(PublisherMode.STAGING_ONLY, PipelineConfig())
    monkeypatch.delenv("R2_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("R2_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("R2_SECRET_ACCESS_KEY", raising=False)
    result = run_m14_handoff(request)
    assert result["state"] == "OWNER_R2_WRITE_CREDENTIAL_REQUIRED"
    assert result["mutation_performed"] is False


def test_retry_receipt_is_deterministic_and_m14_failure_is_preserved(monkeypatch):
    request = PublisherRunRequest(PublisherMode.STAGING_ONLY, PipelineConfig())
    for name in ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(name, "configured-test-value")

    class FakeReport:
        accepted = False
        def to_dict(self):
            return {"accepted": False, "reason_code": "CURRENT_MAIN_REPLAY_REJECTED",
                    "candidate_manifest_sha256": "c" * 64}

    calls = []
    first = run_m14_handoff(request, publisher_runner=lambda req: (calls.append(req) or FakeReport()),
                            provider_factory=lambda: object())
    second = run_m14_handoff(request, publisher_runner=lambda _req: FakeReport(),
                             provider_factory=lambda: object())
    assert first["state"] == second["state"] == "M14_REJECTED"
    assert first["receipt"] == second["receipt"]
    assert len(calls) == 1
    assert "configured-test-value" not in str(first)


def test_staging_handoff_uses_the_actual_m14_orchestrator_with_injected_memory_provider(monkeypatch):
    import scrubbots_content_pipeline.one_command_publisher as orchestrator
    from scrubbots_content_pipeline import scrubpack_solver_identity
    from test_sb_cp03_011_one_command_publisher import _request

    monkeypatch.setattr(orchestrator, "verify_solver_proven_scrubpack", lambda *_args: True)
    monkeypatch.setattr(scrubpack_solver_identity, "verify_solver_proven_scrubpack", lambda *_args: True)
    for name in ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(name, "configured-test-value")
    request, memory_provider, _, _, _ = _request(PublisherMode.STAGING_ONLY)
    result = run_m14_handoff(request, provider_factory=lambda: memory_provider)
    assert result["state"] == "M14_COMPLETED"
    assert result["m14"]["accepted"] is True
    assert result["m14"]["terminal_stage"] == "STAGING_DOWNLOAD_VERIFY"
    assert result["receipt"]["accepted"] is True


def test_launcher_exposes_same_preflight_service_to_headless_and_studio_paths():
    launcher = (ROOT / "level_factory" / "scripts" / "factory_core_launcher.py").read_text(encoding="utf-8")
    studio = (ROOT / "level_factory" / "scripts" / "factory_studio_release.gd").read_text(encoding="utf-8")
    assert 'elif operation == "scrubbots-publish"' in launcher
    assert "publish_preflight(request)" in launcher
    assert '"scrubbots-publish"' in studio and '"action": "preflight"' in studio
