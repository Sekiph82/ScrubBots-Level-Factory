from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(ROOT / "tests" / "integration"))
sys.path.insert(0, str(ROOT / "scripts"))

import test_sb_cpx_001_solver_identity_pack as cpx001  # noqa: E402
from scrubbots_content_pipeline import (  # noqa: E402
    CONTENT_MANIFEST_SCHEMA,
    Environment,
    ProviderCapability,
    ProviderFeature,
    ProviderIdentity,
    ProviderObjectBytesResult,
    ProviderResultCategory,
    StagingDownloadReasonCode,
    StagingManifestPackDigest,
    StagingManifestReceipt,
    build_candidate_manifest,
    verify_staged_manifest_download,
)
from cpx002_current_main_replay_adapter import verify_staged_supply_with_current_main  # noqa: E402
from scrubbots_pixel_factory import owner_upload, studio_extensions as studio  # noqa: E402
from scrubbots_pixel_factory.output.png import encode_logical_png  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline.scrubpack_identity import (  # noqa: E402
    current_solver_proof_for_candidate,
    revalidate_current_solver_proofs,
)


class MemoryStagingReader:
    identity = ProviderIdentity("cpx002-current-main-test", "1.0")
    capabilities = ProviderCapability(
        "cpx002-current-main-read", "1.0", (Environment.STAGING,), (ProviderFeature.INTEGRITY_VERIFY,)
    )

    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = dict(objects)

    def read_object_bytes(self, environment: Environment, object_key: str) -> ProviderObjectBytesResult:
        if environment is not Environment.STAGING or object_key not in self.objects:
            return ProviderObjectBytesResult(
                "1.0", ProviderResultCategory.UNAVAILABLE, self.identity.provider_id,
                environment, object_key, None,
            )
        return ProviderObjectBytesResult(
            "1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id,
            environment, object_key, self.objects[object_key],
        )


def test_exact_verified_staging_pack_replays_with_current_main_godot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    game_root = Path("C:/Users/sekip/AppData/Local/Temp/ScrubBots-Level-Factory/CPX-002-GAME-AUTHORITY")
    godot = "C:/Users/sekip/AppData/Local/Microsoft/WinGet/Links/godot_console.exe"
    assert game_root.is_dir() and Path(godot).is_file(), "the authorized exact current-main Godot authority is required"
    monkeypatch.setenv("SCRUBBOTS_PROJECT", str(game_root))

    repository = tmp_path / "factory-repository"
    source_root = repository / "level_factory/output/owner-uploads"
    evidence_root = repository / "level_factory/output/studio-extensions"
    source_root.mkdir(parents=True)
    evidence_root.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)

    source = tmp_path / "current-main-replay-source.png"
    source.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = owner_upload.import_owner_upload(source)
    run = studio.run_pipeline(source_id=str(imported["source_id"]))
    assert run["disposition"] == "READY"
    review = studio.record_owner_review(str(run["candidate_id"]), "ACCEPT", "CPX-002 current-main integration", "")
    assert review["publication"]["disposition"] == "NOT_ENTERED"

    pipeline_bytes, pool_entry = current_solver_proof_for_candidate(str(run["candidate_id"]))
    proof = cpx001.ScrubpackSolverProof(pipeline_bytes, pool_entry)
    level_raw = Path(run["primary"]["files"]["level"]).read_bytes()
    plan_raw = Path(run["primary"]["files"]["supply_plan"]).read_bytes()
    level_input = cpx001._pack_level(level_raw, plan_raw)
    pack_id = "cpx002-current-main-integration"
    build = cpx001.build_solver_proven_scrubpack(
        (level_input,), proofs={level_input.level_id: proof}, pack_id=pack_id, pack_version=1,
        created_at_utc="2026-10-06T12:00:00Z", current_authority_check=revalidate_current_solver_proofs,
    )
    assert build.solver_identity_artifact_bytes is not None
    assert cpx001.verify_solver_proven_scrubpack(build.archive_bytes, build.solver_identity_artifact_bytes, build.evidence)
    object_key = "packs/cpx002-current-main-integration/v1.scrubpack"
    candidate = build_candidate_manifest(
        (build,), content_version=3, minimum_game_version="2.4.0",
        object_keys={pack_id: object_key}, current_game_version="2.4.1",
        supported_manifest_schema_versions={CONTENT_MANIFEST_SCHEMA: {1}},
        prior_accepted_content_version=2,
    )
    assert candidate.publishable, (candidate.strict_round_trip_valid, candidate.references, candidate.compatibility)
    manifest_key = "manifests/current.json"
    reader = MemoryStagingReader({manifest_key: candidate.manifest_bytes, object_key: build.archive_bytes})
    staging_write_receipt = StagingManifestReceipt(
        "1.0", candidate.manifest_bytes, candidate.manifest_sha256, candidate.manifest.content_version,
        manifest_key,
        (StagingManifestPackDigest(pack_id, object_key, build.evidence.archive_sha256, len(build.archive_bytes)),),
        reader.identity.provider_id, reader.identity.provider_version, reader.identity.contract_version,
        "cpx002-current-main-write", "1.0", Environment.STAGING.value, "staging:default",
        None, None, ("a" * 64,),
    )
    staged = verify_staged_manifest_download(
        candidate=candidate, staging_receipt=staging_write_receipt, provider=reader
    )
    assert staged.accepted and staged.reason_code is StagingDownloadReasonCode.VERIFIED
    assert staged.receipt is not None

    receipt = verify_staged_supply_with_current_main(
        staging_report=staged,
        downloaded_manifest_bytes=reader.objects[manifest_key],
        downloaded_pack_bytes={pack_id: reader.objects[object_key]},
        solver_identity_artifacts={pack_id: build.solver_identity_artifact_bytes},
        pack_build_evidence={pack_id: build.evidence},
        game_root=game_root,
        godot_executable=godot,
        timeout_seconds=900,
    )
    assert receipt.accepted, receipt.to_dict()
    assert receipt.game_repository == "Sekiph82/Scrubbots"
    assert receipt.game_branch == "main"
    artifact_doc = json.loads(build.solver_identity_artifact_bytes)
    assert receipt.game_commit == artifact_doc["levels"][0]["authority"]["git_head"]
    assert receipt.authority_source_sha256
    assert receipt.pack_results[0]["levels"][0]["solver_status"] == "SOLVED"
    assert receipt.pack_results[0]["levels"][0]["replay_solved"] is True
    assert receipt.pack_results[0]["levels"][0]["unresolved"] == 0
