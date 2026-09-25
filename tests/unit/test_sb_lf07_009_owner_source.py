from __future__ import annotations

import hashlib
import pytest

from scrubbots_pixel_factory import MutationContractError, AuthenticTargetCandidate, SafetyConstraintEvidence, TypedChallengeTarget, build_typed_target, revalidate_mutation_from_authentic_adapters, run_authentic_bounded_mutations
from scrubbots_pixel_factory.mutation_source import SourceLinkedMutationContext
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord
from test_sb_lf07_004_revalidation import _authentic_chain
from test_sb_lf07_007_attempts import _StaticEngine


def _record(tmp_path) -> tuple[M05OwnerSourceRecord, bytes]:
    raw = b"immutable-owner-source-png-bytes"
    source = tmp_path / "source.png"
    source.write_bytes(raw)
    return M05OwnerSourceRecord("source-1", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20), raw


def test_valid_candidate_only_mutation_preserves_owner_bytes_length_dimensions_and_identity(tmp_path) -> None:
    record, raw = _record(tmp_path)
    context = SourceLinkedMutationContext.establish(record)
    checked = context.verify_after(derived_artifact_paths=(str(tmp_path / "derived-preview.png"),))
    assert checked.passed
    assert checked.after is not None and checked.after.source_sha256 == record.source_sha256


def test_source_byte_mutation_and_dimension_change_fail_closed(tmp_path) -> None:
    record, raw = _record(tmp_path)
    source = tmp_path / "source.png"
    context = SourceLinkedMutationContext.establish(record)
    source.write_bytes(raw + b"x")
    report = context.verify_after()
    assert report.after is not None and report.after.disposition == "FAIL"


def test_corrupt_record_and_path_metadata_alias_are_rejected(tmp_path) -> None:
    record, raw = _record(tmp_path)
    corrupt = M05OwnerSourceRecord("source-1", record.source_path, record.source_sha256, record.byte_length + 1, 20, 20)
    with pytest.raises(MutationContractError):
        SourceLinkedMutationContext.establish(corrupt)
    context = SourceLinkedMutationContext.establish(record)
    assert context.verify_after(derived_artifact_paths=(record.source_path,)).after.disposition == "FAIL"  # type: ignore[union-attr]


def test_repeated_verification_is_idempotent(tmp_path) -> None:
    record, _ = _record(tmp_path)
    first = SourceLinkedMutationContext.establish(record).verify_after()
    second = SourceLinkedMutationContext.establish(record).verify_after()
    assert first.after == second.after


def test_only_m05_owner_upload_record_can_be_adapted_to_source_identity() -> None:
    raw = b"immutable-owner-source-png-bytes"
    record = M05OwnerSourceRecord.from_m05_owner_upload({
        "source_id": "owner-upload-" + "a" * 64,
        "origin": "OWNER_UPLOAD",
        "status": "SOURCE_ONLY",
        "validation_state": "UNVALIDATED",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "original_width": 20,
        "original_height": 20,
        "immutable_relative_path": "owner-uploads/owner-upload-" + "a" * 64 + "/source.png",
    })
    assert record.source_id.startswith("owner-upload-")
    with pytest.raises(Exception):
        M05OwnerSourceRecord.from_m05_owner_upload({"source_id": record.source_id, "origin": "SYNTHETIC", "status": "SOURCE_ONLY", "validation_state": "UNVALIDATED"})


def test_source_linked_context_uses_m05_verifier_and_requires_before_after_pass(tmp_path) -> None:
    raw = b"accepted-m05-source"
    source = tmp_path / "source.png"
    source.write_bytes(raw)
    record = M05OwnerSourceRecord("owner-upload-r02", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    context = SourceLinkedMutationContext.establish(record)
    assert context.before.disposition == "PASS"
    checked = context.verify_after()
    assert checked.passed
    with pytest.raises(MutationContractError):
        SourceLinkedMutationContext.establish(M05OwnerSourceRecord(record.source_id, str(source) + ".missing", record.source_sha256, record.byte_length, 20, 20))


def test_source_linked_runner_requires_precheck_and_runs_postcheck_before_target_match(tmp_path) -> None:
    raw = b"runner-owned-source"
    source = tmp_path / "source.png"
    source.write_bytes(raw)
    parent, request, mutation, solver, analysis, score, qa, solver_adapter, difficulty_adapter, qa_adapter = _authentic_chain(raw)
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver_adapter, difficulty_adapter, qa_adapter)
    candidate = AuthenticTargetCandidate(envelope, solver_adapter, difficulty_adapter, qa_adapter)
    base_target = build_typed_target(0.0, 100.0, difficulty_adapter, qa_adapter)
    target = TypedChallengeTarget(0.0, 100.0, base_target.policy_digest, SafetyConstraintEvidence("m05", "1", base_target.policy_digest, True, True, True, qa_adapter.producer_digest))
    record = M05OwnerSourceRecord("runner-owned", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    context = SourceLinkedMutationContext.establish(record)
    success = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=__import__("scrubbots_pixel_factory").AttemptBudget(1), request_factory=lambda parent, ordinal, seed: request, engine=_StaticEngine(__import__("scrubbots_pixel_factory").MutationDisposition.APPLIED, mutation), validator=lambda result: candidate, target=target, source_context=context)
    assert success.disposition.value == "TARGET_MATCH"
    assert source.read_bytes() == raw
    context = SourceLinkedMutationContext.establish(record)
    def mutate_then_return(result):
        source.write_bytes(raw + b"changed")
        return candidate
    failed = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=__import__("scrubbots_pixel_factory").AttemptBudget(1), request_factory=lambda parent, ordinal, seed: request, engine=_StaticEngine(__import__("scrubbots_pixel_factory").MutationDisposition.APPLIED, mutation), validator=mutate_then_return, target=target, source_context=context)
    assert failed.disposition.value == "ERROR"
