# SB-LF03-012-C001-R02 — Real Regression Corpus + Green Full Gate Remediation

Document role: CODEX REMEDIATION PROMPT

Target: SB-LF03-012 — Add regression fixtures.

R01 re-audit:
.hiveai/audits/SB-LF03-012-C001-R01_REGRESSION_COVERAGE_AND_CANONICAL_INVOKE_REMEDIATION_STRICT_REAUDIT.md

Create first:
.hiveai/codex-logs/SB-LF03-012-C001-R02_REAL_REGRESSION_AND_GREEN_FULL_GATE_REMEDIATION_CODEX_LOG.md

Do not edit TASKS.md.

## Dependency

Run after R02 fixes for 005, 009, 010 and 011.

## Mission A — real declarative negative fixtures

The R01 JSON list of negative fixture IDs is not enough.
For every defect family add a real versioned declarative payload with stable fixture ID, input/state/identity data, expected disposition/result, canonical payload SHA-256 and production=false for fake providers.

Required behavioral families:
- wrong legal query/result binding;
- wrong state-key binding;
- transition child authority drift;
- enumeration wrong-query/authority drift;
- wide-shallow frontier peak;
- replay identity tamper + missing-context no-MATCH;
- real max-visited stop;
- timeout non-canonical telemetry;
- canonical real invoke.

Tests must load and execute fixture payloads, not merely assert names are present.

## Mission B — real canonical invoke regression

Use the SB-LF03-009 R02 independent clean canonical checkout and committed runner.
Call CanonicalHeadlessBridge.invoke(), not only capability().
Exercise legal_moves, apply_placement or equivalent ProofKernel transition, solve through SolvabilitySolver, deterministic repeat, error/mismatch case and checkout immutability.

No silent skip when the local ScrubBots Git repository and Godot executable are available. A dirty primary checkout is not a skip reason because R02 must create an independent clean local execution checkout.

## Mission C — green repository-wide gate

R01 ended with 842 passed, 3 skipped, 2 warnings, 6 failed.
SB-LF03-012 cannot close while full pytest is red.

Diagnose the six failures rather than labeling them unrelated.
Builder reports four LF00 project-boundary readers encountered temporary/generated PNG bytes during LF06 integration ordering and two LF06 Studio integration assertions reported missing/generated output evidence.

Investigate repository-root mutation, order-dependent integration tests, temporary artifacts outside pytest tmp_path, fixture teardown, and generated-output assumptions.
Fix the narrow test/product isolation defect without weakening accepted LF00/LF06 contracts.
Do not skip, xfail or delete failing tests.
Run full pytest from a clean tracked state at least twice if practical to demonstrate order independence.

## Final gates

Must PASS: focused 012; all retained LF03; affected LF00/LF06 tests; full python -m pytest -q; compileall; Level Factory Godot headless editor boot; real canonical invoke regression; git diff --check; git diff --exit-code -- TASKS.md.

Record exact counts/skips and publish R02 implementation/log/terminal commit.