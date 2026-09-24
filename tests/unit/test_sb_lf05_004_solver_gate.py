from __future__ import annotations

from scrubbots_pixel_factory.baseline_search import BaselineSearchPolicy, BaselineSearchResult, SearchExecutionDisposition, SearchVerdict
from scrubbots_pixel_factory.compact_solver_state import CANONICAL_PROOF_STATE_AUTHORITY_SHA
from scrubbots_pixel_factory.qa import AuthorityIdentity, SolverGateDisposition, evaluate_solver_gate
from scrubbots_pixel_factory.solver_budget import BudgetedSolverResult, SolverBudgetPolicy, SolverOutcomeDisposition, wrap_operational_execution
from scrubbots_pixel_factory.solver_evidence import SolverEvidenceReport, SolverMetrics


AUTHORITY = AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", CANONICAL_PROOF_STATE_AUTHORITY_SHA, "scripts/gameplay/solver", "M03_SOLVER_EVIDENCE_V1")
SOURCE = "a" * 64


def _evidence(verdict: SearchVerdict, disposition: SolverOutcomeDisposition) -> SolverEvidenceReport:
    policy = SolverBudgetPolicy(max_visited_states=10, max_depth=4, max_solutions=2)
    result = BaselineSearchResult(SearchExecutionDisposition.AVAILABLE, verdict, (), "fixture", BaselineSearchPolicy(max_depth=4))
    budget = BudgetedSolverResult(disposition, policy, "fixture", verdict.value, "fixture", None)
    return SolverEvidenceReport(SearchExecutionDisposition.AVAILABLE, result, SolverMetrics((), False, 1, None, 0, 0, (1,), 1, ()), 0.0, budget_policy=policy, budget_result=budget)


def test_solved_and_exact_proven_unsolvable_are_distinct() -> None:
    solved = _evidence(SearchVerdict.SOLVED, SolverOutcomeDisposition.SOLVED)
    dead = _evidence(SearchVerdict.PROVEN_UNSOLVABLE, SolverOutcomeDisposition.PROVEN_UNSOLVABLE)
    assert evaluate_solver_gate(solved, authority=AUTHORITY, level_source_sha256=SOURCE).disposition is SolverGateDisposition.ACCEPTABLE_SOLVER_PROOF
    assert evaluate_solver_gate(dead, authority=AUTHORITY, level_source_sha256=SOURCE).disposition is SolverGateDisposition.REJECT_PROVEN_UNSOLVABLE


def test_unknown_bound_inconclusive_timeout_and_unavailable_never_become_unsolvable() -> None:
    unknown = _evidence(SearchVerdict.INCONCLUSIVE, SolverOutcomeDisposition.INCONCLUSIVE)
    assert evaluate_solver_gate(unknown, authority=AUTHORITY, level_source_sha256=SOURCE).disposition is SolverGateDisposition.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED
    timeout = wrap_operational_execution(None, timeout_seconds=1.0, timeout_occurred=True)
    assert evaluate_solver_gate(timeout, authority=AUTHORITY, level_source_sha256=SOURCE).disposition is SolverGateDisposition.INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED
    assert evaluate_solver_gate(None, authority=AUTHORITY, level_source_sha256=SOURCE).disposition is SolverGateDisposition.UNAVAILABLE


def test_budget_and_authority_identity_mismatch_fail_closed_deterministically() -> None:
    evidence = _evidence(SearchVerdict.SOLVED, SolverOutcomeDisposition.SOLVED)
    wrong_authority = AuthorityIdentity(AUTHORITY.repository, "d" * 40, AUTHORITY.source_path, AUTHORITY.contract_version)
    report = evaluate_solver_gate(evidence, authority=AUTHORITY, evidence_authority=wrong_authority, level_source_sha256=SOURCE)
    assert report.disposition is SolverGateDisposition.ERROR
    mismatch = evaluate_solver_gate(evidence, authority=AUTHORITY, expected_budget_identity_digest="e" * 64, level_source_sha256=SOURCE)
    assert mismatch.disposition is SolverGateDisposition.ERROR
    assert report.canonical_bytes() == report.canonical_bytes()
