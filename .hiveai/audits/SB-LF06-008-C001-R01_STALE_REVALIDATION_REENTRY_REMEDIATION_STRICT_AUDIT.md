# SB-LF06-008-C001-R01 — Stale Revalidation Re-entry Remediation — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Verdict

**PASS / CLOSED**

Severity summary:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0

## Audited chain

- Remediation prompt/start authority: `9211dcb5a16b8d517a736347c93cd73d89b7cca1`
- R01 implementation commit: `ae1dcfcd6841e966f82b88eb568310ed74b25423`
- Terminal builder publication: `64a9a49baa36024f74cd1783ca80ae03b18460f6`
- Terminal publication is builder-log-only.

## Closure of the prior MAJOR finding

The C001 audit found a stale-result lifecycle dead end:

`edit -> revalidate -> edit -> STALE -> cannot revalidate again`

R01 closes that defect without redesigning accepted LF06-008 architecture.

The remediation:
- marks stale evidence non-current by setting `_result_current=false` when the working grid changes after a recorded result;
- retains `STALE` as an explicit evidence state rather than silently promoting it to current evidence;
- enables the revalidation control in both `AVAILABLE` and `STALE` states;
- keeps `STALE` stable until a fresh revalidation runs or the editor is reset;
- labels the prior result visibly as `Stale evidence:`;
- preserves Reset -> `NOT_REQUIRED` behavior.

The re-entry path therefore remains truthful while avoiding destructive Reset merely to re-run structural QA.

## Real runtime evidence

The committed Godot integration suite now exercises the actual repeatable lifecycle through the existing Studio/editor/gateway/Python boundary:

1. first manual edit -> DIRTY;
2. first real structural revalidation -> current structural ACCEPT/REJECT result A;
3. second edit -> STALE and result A non-current;
4. revalidation remains enabled while DIRTY/STALE;
5. second real revalidation runs through the canonical bridge and produces current result B;
6. result B has a different working-grid hash when the grid differs;
7. editor remains DIRTY and canonical source bytes remain unchanged;
8. third edit makes result B STALE;
9. third real canonical revalidation succeeds without Reset;
10. only afterward does Reset return the workflow to NOT_REQUIRED.

The existing deliberate bad-grid canonical REJECT path remains present.

This directly covers the missing acceptance path; the fix is not merely a source-marker assertion.

## Preserved accepted LF06-008 architecture

R01 does not modify the canonical Python Core, launcher, gateway, source-bundle authority, source-policy reconstruction, canonical `evaluate_grid()`, canonical logical-grid hashing, fixed process boundary, immutable source bundle, or memory-only editor contract.

The implementation continues to preserve:
- `read_bundle()` as source-bundle authority;
- exact recorded source `QualityPolicy` reuse;
- canonical Python structural QA rather than GDScript evaluator duplication;
- canonical working-grid hash binding;
- source candidate/source-byte identity checks;
- transient request cleanup;
- source `artwork.png`, `artwork.json`, and `metadata.json` immutability;
- `STRUCTURAL ART QA ONLY — NOT FULL GAMEPLAY VALIDATION` semantics;
- LF06-003 `Validate` remaining unavailable;
- M03 solver, M04 measured difficulty, and M05 unified validation remaining explicitly absent;
- no persistence, revision history, owner acceptance, save/export, or production promotion.

## Scope and publication audit

`9211dcb... -> ae1dcfcd...` is exactly one remediation implementation commit and changes only:
- the R01 builder log;
- `level_factory/scripts/factory_studio_art_revalidation.gd`;
- `level_factory/tests/factory_studio_art_revalidation_integration_suite.gd`;
- `tests/unit/test_sb_lf06_008_factory_studio_art_revalidation.py`.

No root `TASKS.md` change is present in the builder implementation.

`ae1dcfcd... -> 64a9a49...` changes only the finalized R01 builder log, satisfying terminal log-only publication discipline.

## Builder-reported verification

Builder evidence records:
- focused LF06-008 tests: `6 passed`;
- committed real Godot integration: exit `0` with LF06-008 PASS marker and empty stderr;
- full pytest: `722 passed, 1 warning`;
- compileall: PASS;
- Godot headless project boot: exit `0`;
- `git diff --check`: PASS;
- `git diff -- TASKS.md`: empty;
- no retained generated output under `level_factory/output/` beyond tracked `.gitkeep`.

These commands were not independently re-executed in the audit environment. The committed state-machine change, real integration path, exact changed-file scope and commit topology were independently inspected.

## Closure decision

`SB-LF06-008 — Revalidate after manual changes` is **PASS / CLOSED** for the current repository snapshot.

Closure is intentionally bounded to canonical structural/art QA revalidation of manual artwork edits. It does not imply gameplay solver completion, measured Difficulty V1 completion, unified M05 validation, owner acceptance, persistence, or production readiness.
