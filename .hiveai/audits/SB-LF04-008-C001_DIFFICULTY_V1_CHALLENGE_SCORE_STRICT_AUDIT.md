# SB-LF04-008-C001 — Difficulty V1 Challenge Score — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Audited chain

- implementation: `32ef779d445950be75ab4728d9381c34b71defdc`
- terminal builder-log commit: `3d587e10ca7cfc43a122f9c7cee45c4891015405`
- M04 master builder publication: `a9e63bc272646eccb88bef7672752132f9d3fb0a`
- final builder full suite: `937 passed, 1 capability skip`
- compileall / Godot / diff-check / TASKS no-diff: PASS

Builder logs and green tests were treated as evidence, not acceptance.

## Independent finding

## MAJOR-001 — ChallengeScoreResult does not enforce Difficulty V1 semantic consistency

`calculate_challenge_score()` implements the required formula correctly. However the exported/public `ChallengeScoreResult` contract accepts arbitrary components and an arbitrary score as long as names and basic numeric ranges are valid.

It does not require:
- the fixed V1 coefficients (.25/.25/.15/.15/.20);
- contribution == normalized * coefficient;
- score == 100 * sum(contributions).

The SB-LF04-009 test helper demonstrates this directly by constructing five zero-coefficient/zero-contribution components and attaching arbitrary scores such as 25 or 50 while still obtaining a valid `ChallengeScoreResult`.

A versioned Difficulty V1 result must not be able to claim impossible policy output.

## Global invariant review

No board-size/color-count difficulty inference, source-art mutation, runtime network/provider-credit use, gameplay-rule clone, or builder TASKS mutation was accepted.

## Final disposition

**CHANGES_REQUIRED / IMPLEMENTATION RETAINED**

## Required remediation

Make ChallengeScoreResult self-validating for DIFFICULTY_V1: exact ordered component catalog, exact fixed coefficients, finite normalized values, contribution consistency, and score consistency with the weighted sum. Keep source LevelMetrics digest binding. Update downstream tests to construct valid scores through calculate_challenge_score or a strictly validated fixture factory.
