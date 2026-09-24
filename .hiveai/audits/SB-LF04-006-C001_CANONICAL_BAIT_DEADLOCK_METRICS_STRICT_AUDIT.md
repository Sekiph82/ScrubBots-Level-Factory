# SB-LF04-006-C001 — Canonical Bait / Deadlock Metrics — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 1
- MAJOR: 0
- MINOR: 0

## Audited chain

- implementation: `a75b81a761e4671deeca2a7a029d7bce48f2d050`
- terminal builder-log commit: `6d6561da7a16d188bfd618c2f5a915c6b7c96451`
- M04 master builder publication: `a9e63bc272646eccb88bef7672752132f9d3fb0a`
- final builder full suite: `937 passed, 1 capability skip`
- compileall / Godot / diff-check / TASKS no-diff: PASS

Builder logs and green tests were treated as evidence, not acceptance.

## Independent finding

## BLOCKER-001 — Counterfactual truth can be fabricated from a tuple of dispositions

`bait_deadlock_from_children()` accepts an arbitrary tuple of `SolverOutcomeDisposition` values and defaults its provider identity to `canonical-counterfactual`. It does not prove that legal moves came from the canonical legal-move provider, that children came from canonical transitions, or that child classifications came from the canonical solver.

The function can therefore manufacture an exact AVAILABLE bait/deadlock ratio from caller-supplied enum values. This violates the explicit requirement to use M03 providers/bridge only and to leave the metric absent when canonical counterfactual proof is unavailable.

## Global invariant review

No board-size/color-count difficulty inference, source-art mutation, runtime network/provider-credit use, gameplay-rule clone, or builder TASKS mutation was accepted.

## Final disposition

**CHANGES_REQUIRED / IMPLEMENTATION RETAINED**

## Required remediation

Create a canonical counterfactual provider/evidence contract. Fixture child dispositions must be marked non-production and rejected by production population. Either execute the accepted M03 legal-move/transition/solver chain with verifiable evidence or keep production bait_deadlock UNAVAILABLE. Do not reuse dead_end_count or caller tuples as canonical proof.
