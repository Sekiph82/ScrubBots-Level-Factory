from __future__ import annotations

import hashlib

from scrubbots_pixel_factory import AttemptBudget, AttemptDisposition, MutationDisposition, run_authentic_bounded_mutations, revalidate_mutation_from_authentic_adapters, AuthenticTargetCandidate, build_typed_target
from scrubbots_pixel_factory.mutation_source import SourceLinkedMutationContext
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord
from test_sb_lf07_004_revalidation import _authentic_chain
from test_sb_lf07_007_attempts import _StaticEngine


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


def test_source_context_is_idempotent_and_rejects_alias_path(tmp_path) -> None:
    raw = b"stable-owner-source"
    source = tmp_path / "source.bin"
    source.write_bytes(raw)
    record = M05OwnerSourceRecord("owner-r04", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    context = SourceLinkedMutationContext.establish(record)
    assert context.verify_after().passed
    assert context.verify_after() == context.verify_after()
