from __future__ import annotations

from scrubbots_pixel_factory.qa import QAOutcome, SolverGateDisposition, classify_solver_qa, summarize_solver_qa


def test_closed_solver_outcomes_keep_proof_uncertainty_and_timeout_distinct() -> None:
    accepted = classify_solver_qa(SolverGateDisposition.ACCEPTABLE_SOLVER_PROOF)
    rejected = classify_solver_qa(SolverGateDisposition.REJECT_PROVEN_UNSOLVABLE)
    uncertain = classify_solver_qa("UNKNOWN_BOUND")
    timeout = classify_solver_qa("TIMEOUT_BEFORE_RESULT")
    assert accepted.outcome == QAOutcome.ACCEPTABLE_SOLVER_PROOF
    assert rejected.outcome == QAOutcome.REJECT_PROVEN_UNSOLVABLE
    assert uncertain.outcome == timeout.outcome == QAOutcome.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED
    assert uncertain.outcome != QAOutcome.REJECT_PROVEN_UNSOLVABLE


def test_rejection_statistics_preserve_each_disposition() -> None:
    stats = summarize_solver_qa([
        classify_solver_qa("REJECT_PROVEN_UNSOLVABLE"),
        classify_solver_qa("INCONCLUSIVE"),
        classify_solver_qa("UNAVAILABLE"),
        classify_solver_qa("ERROR"),
    ])
    assert stats.total == 4
    assert dict(stats.counts)[QAOutcome.REJECT_PROVEN_UNSOLVABLE] == 1
    assert dict(stats.counts)[QAOutcome.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED] == 1
    assert stats.digest() == stats.digest()
