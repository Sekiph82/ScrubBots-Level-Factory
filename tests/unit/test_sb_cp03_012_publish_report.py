from __future__ import annotations

import hashlib
import io
import json
import sys
from dataclasses import replace
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

import scrubbots_content_pipeline.one_command_publisher as orchestrator
from scrubbots_content_pipeline import scrubpack_solver_identity
from scrubbots_content_pipeline.current_main_replay import (
    AUTHORITY_SOURCE_PATHS, CurrentMainReplayReceipt,
)
from scrubbots_content_pipeline.publish_report import (
    PublishReport, build_publish_report, render_publish_report, serialize_publish_report,
)
from scrubbots_content_pipeline.production_manifest_activation import ProductionManifestReasonCode
from test_sb_cp03_011_one_command_publisher import _request

FACTORY_SHA = "d" * 40


def _allow_fixture_solver(monkeypatch):
    monkeypatch.setattr(orchestrator, "verify_solver_proven_scrubpack", lambda *_args: True)
    monkeypatch.setattr(scrubpack_solver_identity, "verify_solver_proven_scrubpack", lambda *_args: True)


def test_publish_report_binds_staging_evidence_and_is_canonical_and_safe(monkeypatch):
    _allow_fixture_solver(monkeypatch)
    request, _provider, candidate, _approval, _authority = _request()
    result = orchestrator.run_one_command_publisher(request)
    assert result.accepted

    first = build_publish_report(result, level_factory_commit_sha=FACTORY_SHA)
    second = build_publish_report(result, level_factory_commit_sha=FACTORY_SHA)
    assert isinstance(first, PublishReport)
    assert serialize_publish_report(first) == serialize_publish_report(second)
    assert first.report_digest == second.report_digest

    document = first.to_dict()
    assert document["schema"] == "scrubbots.content.publish-report.v1"
    assert document["level_factory_commit_sha"] == FACTORY_SHA
    assert document["candidate_manifest"] == {
        "sha256": candidate.manifest_sha256,
        "content_version": 3,
        "minimum_game_version": "2.4.0",
        "packs": [{
            "pack_id": "pack-a", "pack_version": 2,
            "object_key": "packs/pack-a/v2.scrubpack",
            "sha256": candidate.manifest.packs[0].sha256,
            "byte_length": candidate.manifest.packs[0].byte_length,
            "level_ids": ["level-a"],
        }],
    }
    assert document["validation_only_outcome"]["accepted"] is True
    assert document["staging"]["upload"]["accepted"] is True
    assert document["staging"]["integrity"]["accepted"] is True
    assert document["staging"]["manifest"]["accepted"] is True
    assert document["staging"]["download_verification"]["accepted"] is True
    assert document["owner_approval_state"] == "NOT_REQUIRED"
    assert document["production_mutated"] is False
    assert document["production_manifest_mutated"] is False
    assert document["production_mutation_state"] == "NO_NEW_MUTATION_CONFIRMED"
    assert document["current_main_replay"]["game_authority"] is None

    unsigned = dict(document)
    digest = unsigned.pop("report_digest")
    canonical = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    assert hashlib.sha256(canonical).hexdigest() == digest
    encoded = serialize_publish_report(first)
    assert b"provider_id" not in encoded and b"https://" not in encoded and b"C:\\Users\\" not in encoded
    assert digest in render_publish_report(first)


def test_publish_report_records_cpx_conservation_release_events_and_production_identity(monkeypatch):
    _allow_fixture_solver(monkeypatch)
    request, provider, candidate, approval, authority = _request(orchestrator.PublisherMode.PRODUCTION)
    build = request.factory_pack_builder(request.factory_pack_requests[0])
    with ZipFile(io.BytesIO(build.archive_bytes)) as archive:
        plan = json.loads(archive.read("levels/level-a/supply-plan.json").decode("utf-8"))

    def current_main(**_kwargs):
        level = {
            "level_id": "level-a", "level_sha256": "a" * 64, "plan_sha256": "b" * 64,
            "fifo_columns": plan["columns"], "solver_state_sha256": "e" * 64,
            "solver_evidence_sha256": "f" * 64, "accepted": True,
            "solver_status": "SOLVED", "replay_ok": True, "replay_solved": True,
            "final_active": 0, "unresolved": 0, "supply_exhausted": True,
        }
        return CurrentMainReplayReceipt(
            True, "VERIFIED", "Sekiph82/Scrubbots", "main", "a" * 40,
            authority["source_sha256"], candidate.manifest_sha256,
            ({"pack_id": "pack-a", "pack_sha256": candidate.manifest.packs[0].sha256,
              "levels": [level]},),
        )

    monkeypatch.setattr(orchestrator, "verify_current_main_supply_replay", current_main)
    result = orchestrator.run_one_command_publisher(request)
    assert result.accepted and result.production_activation is not None
    report = build_publish_report(result, level_factory_commit_sha=FACTORY_SHA,
                                  report_timestamp_utc="2026-10-07T02:00:00Z")
    doc = report.to_dict()
    replay = doc["current_main_replay"]
    assert replay["game_authority"] == {
        "repository": "Sekiph82/Scrubbots", "branch": "main", "commit": "a" * 40,
        "source_sha256": {path: "c" * 64 for path in sorted(AUTHORITY_SOURCE_PATHS)},
    }
    level = replay["packs"][0]["levels"][0]
    assert level["fifo_columns"] == plan["columns"]
    assert level["solver_status"] == "SOLVED" and level["supply_exhausted"] is True
    assert doc["owner_approval_state"] == "ACCEPTED_BY_PROMOTION_GATE"
    assert doc["production"]["pack_promotion"]["accepted"] is True
    assert doc["production"]["manifest_activation"]["accepted"] is True
    assert doc["production_mutated"] is True
    assert doc["production_mutation_state"] == "CONFIRMED"
    assert doc["production_manifest_mutated"] is True
    assert doc["production"]["resulting_identity"]["manifest_sha256"] == candidate.manifest_sha256
    assert doc["production"]["resulting_identity"]["content_version"] == 3
    assert doc["release_state"]["events"]
    assert doc["release_state"]["resulting_production_identity"]["production_promoted_event_digest"]
    assert "owner_id" not in serialize_publish_report(report).decode("utf-8")

    promoted_only_doc = build_publish_report(
        replace(result, production_activation=None), level_factory_commit_sha=FACTORY_SHA,
    ).to_dict()
    assert promoted_only_doc["production_mutated"] is True
    assert promoted_only_doc["production_mutation_state"] == "CONFIRMED"
    assert promoted_only_doc["production_manifest_mutated"] is False

    already_current = replace(
        result,
        production_activation=replace(
            result.production_activation,
            accepted=True,
            reason_code=ProductionManifestReasonCode.ALREADY_CURRENT,
            manifest_write_attempted=False,
            receipt=None,
        ),
    )
    repeat_doc = build_publish_report(already_current, level_factory_commit_sha=FACTORY_SHA).to_dict()
    assert repeat_doc["production_mutated"] is True
    assert repeat_doc["production_mutation_state"] == "CONFIRMED"
    assert repeat_doc["production_manifest_mutated"] is False
    assert repeat_doc["production_manifest_mutation_state"] == "ALREADY_CURRENT"
    assert repeat_doc["production"]["resulting_identity"]["confirmation"] == "ALREADY_CURRENT"


def test_failure_report_is_exact_and_timestamp_requires_explicit_utc(monkeypatch):
    _allow_fixture_solver(monkeypatch)
    request, provider, _candidate, _approval, _authority = _request()
    provider.fail_pack_write = True
    result = orchestrator.run_one_command_publisher(request)
    assert not result.accepted
    report = build_publish_report(result, level_factory_commit_sha=FACTORY_SHA)
    document = report.to_dict()
    assert document["failure"] == {
        "stage": "STAGING_PACK_UPLOAD", "reason_code": "OBJECT_WRITE_FAILED",
    }
    assert document["production_mutated"] is False
    with pytest.raises(ValueError):
        build_publish_report(result, level_factory_commit_sha=FACTORY_SHA,
                             report_timestamp_utc="2026-10-07T02:00:00+03:00")
    with pytest.raises(ValueError):
        build_publish_report(result, level_factory_commit_sha="C:\\owner\\repo")


def test_human_report_is_derived_from_machine_report(monkeypatch):
    _allow_fixture_solver(monkeypatch)
    request, _provider, _candidate, _approval, _authority = _request()
    result = orchestrator.run_one_command_publisher(request)
    report = build_publish_report(result, level_factory_commit_sha=FACTORY_SHA)
    human = render_publish_report(report)
    assert human == report.render_human()
    assert result.candidate.manifest_sha256 in human
    assert "STAGING" in human
    assert "Production mutated: false" in human
