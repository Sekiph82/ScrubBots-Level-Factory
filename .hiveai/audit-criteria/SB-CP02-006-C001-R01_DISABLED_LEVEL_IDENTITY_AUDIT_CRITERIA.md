# SB-CP02-006-C001-R01 — Disabled Level Logical Identity — Audit Criteria

## PASS rule

PASS only if disabled-level lookup uses the same logical level-identity semantics already used by manifest collision and reference validation, while preserving exact serialized ID spelling.

## A. Logical identity consistency

Require:
- level IDs remain stored/serialized exactly as supplied;
- logical comparisons for disabled-state lookup use the same casefold rule as CP02-008/009;
- a declared `Level-A` and disabled entry `level-a` represent the same logical level;
- `is_level_disabled(manifest, "Level-A")` returns true in that case;
- equivalent valid case variants also resolve consistently;
- unrelated valid IDs remain false.

## B. Preserve fail-closed model behavior

Retain:
- path-safe ID grammar;
- duplicate disabled IDs rejected;
- casefold-colliding disabled IDs rejected;
- casefold-colliding level IDs rejected;
- exact manifest serialization spelling;
- deterministic disabled_levels ordering;
- unknown disabled references remain syntactically representable until CP02-009;
- no pack deletion/mutation;
- no game/runtime behavior.

## C. CP02-009 consistency

Add focused regression proving:
- a case-variant disabled reference to a declared level is accepted by reference validation;
- the pure disabled helper reports that same declared logical level as disabled.

Do not weaken unknown-reference rejection.

## D. CP02-012 corpus closure

Add/update parser corpus coverage for the mixed-case logical disabled-level scenario so the cross-child regression would fail if exact-string lookup returns.

No parser architecture redesign is required.

## E. Regression

Require:
- CP006 focused tests PASS;
- CP008/009 focused tests PASS;
- CP012 focused corpus PASS;
- all M13 children PASS;
- M12/M11 regressions PASS;
- governance/tracker PASS;
- safe unfiltered full pytest PASS except truthful explicit capability skips;
- compileall PASS;
- schema/example JSON parse PASS;
- git diff --check PASS.

The full-suite run must preserve M13-CONT-001: no implicit owner Desktop Scrubbots checkout discovery.

Codex must not edit root `TASKS.md` or `.hiveai/audits/**`.
