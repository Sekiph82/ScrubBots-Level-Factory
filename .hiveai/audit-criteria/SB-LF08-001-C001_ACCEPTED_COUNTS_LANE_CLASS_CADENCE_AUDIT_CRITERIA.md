# SB-LF08-001-C001 — Requested Accepted Counts by Lane/Class Cadence — Strict Audit Criteria

Target: `SB-LF08-001`

## Prerequisites / accepted foundation
- M03 Puzzle Intelligence = COMPLETE / VERIFIED.
- M04 Difficulty Intelligence = COMPLETE / VERIFIED.
- M05 Unified Factory Validation & Level QA = COMPLETE / VERIFIED.
- M06 Factory Studio + SB-LFX-001..017 = PASS / CLOSED.
- M07 Mutation & Automatic Difficulty Targeting = COMPLETE / VERIFIED.
- PAG-M08 output/export contract = PASS / CLOSED.
- PAG-M09 deterministic local batch/resume foundation = PASS / CLOSED.
- Existing SB-LF08-002/003/004/005/010 remain accepted and must not be regressed.

## Global M08 invariants
- Root `TASKS.md` and `.hiveai/audits/**` are ChatGPT-owned.
- Do not duplicate PAG-M09 deterministic batch/resume logic; reuse or factor it into an accepted shared service.
- `generated/attempted` is never the same as `factory accepted`.
- M08 production acceptance requires current accepted M03/M04/M05 evidence. Legacy PAG-M09 M07 quality ACCEPT alone is not sufficient production truth.
- Difficulty/lane class is derived from accepted M04 evidence, never board dimensions, color count, request label or generator mode.
- Owner review is separate from Factory acceptance and belongs to SB-LF08-007.
- No provider/network spend merely for tests.
- Missing solver/difficulty/QA capability remains UNAVAILABLE/INCONCLUSIVE; never count it as accepted.
- No owner-source, accepted LevelData, canonical bundle, or main-game checkout mutation.

## Task contract

Implement a versioned deterministic production plan that requests **accepted counts by lane/class cadence**, not merely generated attempts.

The plan must bind:
- exact plan schema/version;
- ordered lane/class cadence;
- requested factory-accepted count per lane;
- finite attempt budget per lane and/or total;
- deterministic root seed/seed namespace;
- exact generation/mutation/validation policy identity;
- exact accepted current M04 lane policy/version;
- batch environment/provenance identities.

Supported production lane names must come from the accepted M04 lane/class contract. Do not create new difficulty classes.

## Counting semantics

A candidate may increment a lane accepted count only when:
1. exact candidate identity is unique;
2. current accepted M03 evidence is production-eligible;
3. current accepted M04 analysis places it in the requested lane/class;
4. current M05 MachineReadableQAReport disposition is ACCEPT;
5. any M07 mutation used is fully revalidated and provenance-bound.

A request label, PAG-M09 quality ACCEPT, generator success, mutation success, owner review or preview existence cannot substitute for those gates.

Each candidate may count once in one lane only.

## Cadence / resume

- Lane scheduling order must be deterministic and versioned.
- Same plan + same accepted starting evidence => same lane/attempt sequence.
- Resume must bind the exact plan digest and prior immutable batch histories.
- Already accepted lane counts must never be regenerated or double-counted.
- A lane may COMPLETE, PARTIAL/EXHAUSTED, or UNAVAILABLE truthfully without corrupting another lane.
- No unbounded “keep generating until enough accepted” loop.

## Negative tests

Reject or fail closed on:
- wrong M04 lane;
- M03 inconclusive/unavailable;
- M05 reject/unavailable;
- duplicate candidate identity;
- reused accepted record across lanes;
- plan/cadence tamper;
- seed/budget tamper on resume;
- accepted-count inflation;
- request-label-only lane spoofing;
- size/color difficulty shortcut.

## Required gates

Focused SB-LF08-001 tests plus accepted SB-LF08-002..005/010 regressions; retained M03/M04/M05/M06/M07 + Palette V3; PAG-M09 batch/resume regressions; full pytest green except accepted capability skips; compileall; Godot headless; git diff --check; TASKS/audits no-diff proof.

## PASS rule

PASS only when requested **factory-accepted** counts by lane/class are deterministic, bounded, resumable, evidence-derived, and cannot be inflated by generated/rejected/unavailable candidates.
