from __future__ import annotations

from dataclasses import replace
import pytest

from scrubbots_pixel_factory import MutationContractError, SafetyConstraintEvidence, TargetDisposition, TypedChallengeTarget, build_typed_target, revalidate_mutation_from_authentic_adapters, AuthenticTargetCandidate
from scrubbots_pixel_factory.mutation_targeting import select_authentic_target
from test_sb_lf07_004_revalidation import _authentic_chain


def _candidate():
    _, _, mutation, _, _, _, _, solver, difficulty, qa = _authentic_chain()
    envelope = revalidate_mutation_from_authentic_adapters(mutation, solver, difficulty, qa)
    return AuthenticTargetCandidate(envelope, solver, difficulty, qa), difficulty, qa


def test_default_safety_target_is_truthfully_unavailable() -> None:
    candidate, difficulty, qa = _candidate()
    target = build_typed_target(0.0, 100.0, difficulty, qa)
    assert target.is_authentic_sealed
    assert target.safety.availability == "UNAVAILABLE"
    assert select_authentic_target(target, (candidate,)).disposition is TargetDisposition.UNAVAILABLE


def test_explicit_no_safety_mode_is_versioned_and_selectable() -> None:
    candidate, difficulty, qa = _candidate()
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    assert target.safety.availability == "NOT_REQUESTED"
    assert select_authentic_target(target, (candidate,)).disposition is TargetDisposition.MATCH


def test_direct_safety_and_target_construction_cannot_forge_authority() -> None:
    with pytest.raises(MutationContractError):
        SafetyConstraintEvidence("forged", "1", "a" * 64, True, True, True, "b" * 64)
    with pytest.raises(MutationContractError):
        TypedChallengeTarget(0.0, 1.0, "a" * 64, object())  # type: ignore[arg-type]


def test_sealed_target_replacement_is_rejected() -> None:
    _, difficulty, qa = _candidate()
    target = build_typed_target(0.0, 100.0, difficulty, qa, required_constraints=())
    with pytest.raises(MutationContractError):
        replace(target, minimum=10.0)
