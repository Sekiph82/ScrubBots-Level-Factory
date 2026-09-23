# SB-LF03-012-C001-R04 — Historical Regression Fidelity Closure

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF03-012 — Add regression fixtures.`

R03 re-audit:
`.hiveai/audits/SB-LF03-012-C001-R03_DECLARATIVE_NEGATIVE_CORPUS_CLOSURE_STRICT_REAUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-012-C001-R04_HISTORICAL_REGRESSION_FIDELITY_CLOSURE_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

Close only the remaining SB-LF03-012 regression-corpus fidelity findings.

Do not redesign accepted product/search/bridge/budget behavior.

Preserve:
- all PASS/CLOSED LF03 tasks;
- exact LevelData source binding from SB-LF03-009 R03;
- operational timeout separation from SB-LF03-011 R03;
- green repository-wide gate;
- real canonical legal_moves/apply_placement/solve regression;
- current fixture schema/checksum discipline.

## 1. Fix LF03_TRANSITION_AUTHORITY_DRIFT_V1

The current fixture does not exercise the historical defect.

Create a declarative payload that actually drives a baseline-search transition provider returning:

- execution disposition AVAILABLE;
- a validly shaped `CompactSolverState`;
- child authority different from the parent/canonical authority.

The regression test must run `BaselineSearchEngine` with that provider and prove:

- execution fails closed;
- result is ERROR;
- no foreign-authority child is traversed;
- no false SOLVED / PROVEN_UNSOLVABLE / INCONCLUSIVE verdict is derived from the foreign child.

The test must be driven by fixture payload values, not hard-coded separately from the corpus.

## 2. Fix LF03_ENUMERATION_BINDING_V1

The current fixture merely triggers move-order validation. That is not the historical enumeration binding defect.

Create declarative cases that drive `SolutionCountEngine` through the accepted interfaces.

At minimum cover one of these, preferably both:

### A. Wrong legal-result binding
Provider is queried for state/query A but returns a syntactically valid result bound to another query/state identity.

Expected:
- SolutionCountEngine returns ERROR;
- never EXACT;
- never LOWER_BOUND;
- never INCONCLUSIVE derived from the wrong graph.

### B. Foreign-authority transition child
Transition provider returns AVAILABLE with a child `CompactSolverState` under a different authority.

Expected:
- SolutionCountEngine returns ERROR;
- no recursive enumeration of foreign state.

Use the declarative fixture to specify mutation type and expected result.

## 3. Extend LF03_TIMEOUT_NONCANONICAL_V1

Keep the existing timeout-before-result case.

Add a second declarative scenario for:

- a completed deterministic solver result;
- operational timeout telemetry attached afterward;
- the same deterministic result without timeout telemetry.

Regression must prove:

- canonical deterministic bytes are identical;
- canonical digest is identical;
- only operational telemetry differs;
- no timeout marker/reason/duration enters canonical serialization.

Drive timeout seconds and expected equality from the fixture payload.

## 4. Add exact LevelData stale-hash regression to the declarative bridge corpus

The real bridge regression must also protect SB-LF03-009 R03.

Add declarative tamper data, for example:
- mutate exactly one `cells` entry while retaining the original source SHA-256.

Test must prove:
- `CanonicalBridgeRequest` or invoke fails closed before canonical gameplay execution;
- stale source SHA cannot accompany modified LevelData bytes;
- correctly bound original source still executes legal_moves/apply_placement/solve.

The stale-hash case must be declared in the fixture corpus rather than only living in SB-LF03-009 unit tests.

## 5. Payload checksums

For every changed declarative fixture:
- recompute canonical payload SHA-256 using the existing corpus checksum convention;
- checksum test must independently recompute and compare;
- no placeholder hash;
- no fixture ID-only assertions.

## 6. Scope guard

Do not:
- alter canonical gameplay rules;
- add a Python solver/gameplay clone;
- weaken provider/result validation;
- weaken state/authority binding;
- reintroduce operational timeout into canonical result identity;
- skip/xfail failures;
- modify owner ScrubBots checkout;
- edit `TASKS.md`.

Use fake providers only inside clearly non-production regression fixtures.

## Verification

Run at minimum:

1. focused SB-LF03-012 R04 regression tests;
2. focused SB-LF03-004/008/009/011 dependency tests;
3. all retained LF03 tests;
4. affected LF00/LF06 tests;
5. full `python -m pytest -q`;
6. repeat full suite from a clean tracked state if practical;
7. `python -m compileall -q src tests`;
8. Level Factory Godot headless editor boot;
9. real canonical bridge legal_moves/apply_placement/solve regression;
10. exact stale-LevelData-hash tamper regression;
11. `git diff --check`;
12. `git diff --exit-code -- TASKS.md`.

All repository-wide tests must remain green.

## Publication

Publish:
- product/test/fixture changes;
- finalized R04 task log;
- implementation commit;
- terminal log-only commit.

Then STOP for independent ChatGPT strict re-audit.
