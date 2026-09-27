from __future__ import annotations

import hashlib

from scrubbots_pixel_factory import AttemptBudget, AttemptDisposition, MutationDisposition, run_authentic_bounded_mutations, revalidate_mutation_from_authentic_adapters, AuthenticTargetCandidate, build_typed_target
from scrubbots_pixel_factory.mutation_source import SourceLinkedMutationContext
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord
from test_sb_lf07_004_revalidation import _authentic_chain
from test_sb_lf07_007_attempts import _StaticEngine


def _source_fixture(tmp_path, raw=b"owner-r05-source"):
    source = tmp_path / "source.bin"
    source.write_bytes(raw)
    parent, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain(raw)
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    candidate = AuthenticTargetCandidate(envelope, solver, difficulty, qa)
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    record = M05OwnerSourceRecord("owner-r05", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    return source, parent, request, mutation, candidate, target, SourceLinkedMutationContext.establish(record)


def test_source_context_checks_before_and_after_all_runner_paths(tmp_path) -> None:
    raw = b"owner-r04-source"
    source = tmp_path / "source.bin"
    source.write_bytes(raw)
    record = M05OwnerSourceRecord("owner-r04", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    context = SourceLinkedMutationContext.establish(record)
    parent, request, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain(raw)
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    candidate = AuthenticTargetCandidate(envelope, solver, difficulty, qa)
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    def mutate_source(_):
        source.write_bytes(raw + b"changed")
        return candidate
    report = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda *_: request, engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=mutate_source, target=target, source_context=context)
    assert report.disposition is AttemptDisposition.ERROR


def test_source_mutation_overrides_non_applied_and_exception_paths(tmp_path) -> None:
    source, parent, request, mutation, candidate, target, context = _source_fixture(tmp_path)
    raw = source.read_bytes()

    for disposition in (MutationDisposition.INAPPLICABLE, MutationDisposition.NO_CHANGE, MutationDisposition.UNAVAILABLE, MutationDisposition.ERROR):
        source.write_bytes(raw)
        calls = {"request": 0}

        def request_factory(*_):
            calls["request"] += 1
            source.write_bytes(raw + b"request-mutated")
            return request

        report = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=request_factory, engine=_StaticEngine(disposition, mutation), validator=lambda _: candidate, target=target, source_context=context)
        assert report.disposition is AttemptDisposition.ERROR
        assert calls["request"] == 1

    source.write_bytes(raw)

    def raising_request(*_):
        source.write_bytes(raw + b"request-raises")
        raise RuntimeError("request failure")

    assert run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=raising_request, engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=lambda _: candidate, target=target, source_context=context).disposition is AttemptDisposition.ERROR

    source.write_bytes(raw)

    def raising_validator(_):
        source.write_bytes(raw + b"validator-raises")
        raise RuntimeError("validator failure")

    assert run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(1), request_factory=lambda *_: request, engine=_StaticEngine(MutationDisposition.APPLIED, mutation), validator=raising_validator, target=target, source_context=context).disposition is AttemptDisposition.ERROR


def test_source_post_check_is_reestablished_on_repeated_attempts(tmp_path) -> None:
    source, parent, request, mutation, candidate, target, context = _source_fixture(tmp_path, b"owner-r05-repeated")
    raw = source.read_bytes()
    calls = {"request": 0}

    def request_factory(*_):
        calls["request"] += 1
        if calls["request"] == 2:
            source.write_bytes(raw + b"second-attempt-mutated")
        return request

    report = run_authentic_bounded_mutations(parent, base_seed=request.seed, budget=AttemptBudget(2), request_factory=request_factory, engine=_StaticEngine(MutationDisposition.INAPPLICABLE, mutation), validator=lambda _: candidate, target=target, source_context=context)
    assert calls["request"] == 2
    assert len(report.attempts) == 2
    assert report.disposition is AttemptDisposition.ERROR


def test_source_context_is_idempotent_and_rejects_alias_path(tmp_path) -> None:
    raw = b"stable-owner-source"
    source = tmp_path / "source.bin"
    source.write_bytes(raw)
    record = M05OwnerSourceRecord("owner-r04", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    context = SourceLinkedMutationContext.establish(record)
    assert context.verify_after().passed
    assert context.verify_after() == context.verify_after()
