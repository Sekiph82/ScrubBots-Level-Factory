from __future__ import annotations

import hashlib
import pytest

from scrubbots_pixel_factory import AttemptBudget, AttemptDisposition, MutationCandidate, MutationContractError, MutationDisposition, MutationResult, TypedChallengeTarget, build_typed_target, run_authentic_bounded_mutations, revalidate_mutation_from_authentic_adapters, AuthenticTargetCandidate
from scrubbots_pixel_factory.mutation_base import MutationEngine
from scrubbots_pixel_factory.mutation_source import SourceLinkedMutationContext
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord
from test_sb_lf07_004_revalidation import AUTHENTIC_SOURCE_PATH, _authentic_chain


class _StaticEngine:
    def __init__(self, disposition: MutationDisposition, applied=None):
        self.disposition = disposition
        self.applied = applied

    def apply(self, request, parent):
        if self.disposition is MutationDisposition.APPLIED:
            return self.applied
        return MutationResult(self.disposition, request.digest(), parent.identity, None, parent.state_digest, None, None, f"terminal {self.disposition.value}", request.operator_id, request.operator_version, request.authority)


def _fixture():
    parent, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    candidate = AuthenticTargetCandidate(envelope, solver, difficulty, qa)
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    return parent, request, mutation, candidate, target


def _run(parent, request, mutation, candidate, target, *, budget=1, engine=None, validator=None, source_context=None):
    return run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(budget), request_factory=lambda current, ordinal, seed: request, engine=engine or _StaticEngine(MutationDisposition.APPLIED, mutation), validator=validator or (lambda result: candidate), target=target, source_context=source_context)


def test_authenticated_match_is_bounded_and_records_sealed_provenance() -> None:
    parent, request, mutation, candidate, target = _fixture()
    report = _run(parent, request, mutation, candidate, target, budget=3)
    assert report.disposition is AttemptDisposition.TARGET_MATCH
    assert len(report.attempts) == 1
    assert report.attempts[0].provenance is not None and report.attempts[0].provenance.is_authentic_sealed


def test_runner_wraps_request_validator_and_selection_failures_as_error() -> None:
    parent, request, mutation, candidate, target = _fixture()
    assert _run(parent, request, mutation, candidate, target, validator=lambda _: (_ for _ in ()).throw(ValueError("validator boom"))).disposition is AttemptDisposition.ERROR
    assert _run(parent, request, mutation, candidate, target, engine=_StaticEngine(MutationDisposition.ERROR)).disposition is AttemptDisposition.ERROR
    assert _run(parent, request, mutation, candidate, target, validator=lambda _: object()).disposition is AttemptDisposition.ERROR
    assert run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda *_: (_ for _ in ()).throw(RuntimeError("request boom")), engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=lambda _: candidate, target=target).disposition is AttemptDisposition.ERROR


def test_runner_preserves_terminal_dispositions_and_exact_budget() -> None:
    parent, request, mutation, candidate, target = _fixture()
    assert _run(parent, request, mutation, candidate, target, engine=_StaticEngine(MutationDisposition.UNAVAILABLE)).disposition is AttemptDisposition.UNAVAILABLE
    assert _run(parent, request, mutation, candidate, target, engine=_StaticEngine(MutationDisposition.INAPPLICABLE)).disposition is AttemptDisposition.REJECTED
    no_match = build_typed_target(101.0, 102.0, candidate.difficulty, candidate.qa, required_constraints=())
    report = _run(parent, request, mutation, candidate, no_match, budget=2)
    assert report.disposition is AttemptDisposition.EXHAUSTED
    assert len(report.attempts) == 2


def test_runner_requires_sealed_target_and_checks_source_on_every_path(tmp_path) -> None:
    parent, request, mutation, candidate, target = _fixture()
    raw = b"runner-source"
    source = tmp_path / "source.bin"
    source.write_bytes(raw)
    record = M05OwnerSourceRecord("owner-r04", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    context = SourceLinkedMutationContext.establish(record)
    def mutate_source(_):
        source.write_bytes(raw + b"changed")
        return candidate
    failed = _run(parent, request, mutation, candidate, target, source_context=context, validator=mutate_source)
    assert failed.disposition is AttemptDisposition.ERROR
    forged = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda *_: request, engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=lambda _: candidate, target=object())  # type: ignore[arg-type]
    assert forged.disposition is AttemptDisposition.ERROR


__all__ = ["_StaticEngine", "_fixture", "_run"]
