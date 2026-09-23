# SB-LF03-011-C001-R01 — REAL BUDGET AND TIMEOUT SEPARATION REMEDIATION — Strict Re-Audit

Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Audited chain

- C001 implementation retained
- R01 implementation: `83a12eace8d79e405580597a34f3bb98493ab76e`
- R01 terminal builder-log publication: `94637237f9bb96fac542c095ce1b7d9b14f0fb75`
- R01 master publication: `3d886d4f46eb239bd880fe70b1bef5d3ba4d3c29`
- canonical gameplay authority independently remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

## Independent finding

## MAJOR-001 — Wall-clock timeout still changes canonical solver identity

The visited-state budget is now enforced during baseline traversal and the prior post-hoc-only defect is closed.

However operational timeout remains embedded in `BudgetedSolverResult.canonical_dict()` indirectly through:
- `source_disposition = OPERATIONAL_TIMEOUT`;
- timeout-specific `reason`;
- `exhaustion = OPERATIONAL_TIMEOUT`.

`SolverEvidenceReport.canonical_dict()` embeds this budget result, so a wall-clock timeout still changes canonical evidence bytes/digest.

The focused R01 test explicitly asserts `baseline.canonical_dict() != timeout_result.canonical_dict()`, which is the opposite of the R01 requirement that machine-dependent timeout occurrence remain outside canonical deterministic identity.

## Regression evidence

R01 batch reports:
- retained LF03: `87 passed, 3 skipped, 1 warning`;
- full pytest: `842 passed, 3 skipped, 2 warnings, 6 failed`;
- compileall PASS;
- Godot headless editor boot PASS;
- TASKS builder diff zero.

The six full-suite failures are not automatically attributed to this task. Task closure is based on its own contract plus any explicit repository-wide gate in its criteria.

## Architecture / safety

No Python copy of canonical ProofState/ProofKernel gameplay mechanics was accepted. Dirty canonical authority correctly fails closed rather than being used as production truth.

## Final disposition

**CHANGES_REQUIRED**

## Required next action

Separate deterministic solver outcome from operational timeout telemetry. A wall-clock timeout may produce an operational INCONCLUSIVE notification, but timeout occurrence/reason/duration must not enter canonical evidence bytes/digest or reproduction identity. Add a dedicated operational result/telemetry object if necessary. Replace the current test with one proving identical canonical deterministic bytes regardless of timeout metadata.
