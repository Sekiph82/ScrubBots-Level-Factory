# SB-LF04-012-C001-R03 — Fully Declarative Trust-Boundary Regression Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Target:
`SB-LF04-012 — Tests prove analysis does not mutate gameplay/art source.`

R02 strict re-audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-012-C001-R02_PROVIDER_TRUST_REGRESSION_CLOSURE_STRICT_REAUDIT.md

Expected builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-012-C001-R03_FULLY_DECLARATIVE_TRUST_BOUNDARY_REGRESSION_CLOSURE_CODEX_LOG.md

Do not edit root TASKS.md.

## Scope

Product implementations for SB-LF04-001..011 are accepted.

This R03 is regression-corpus fidelity only.

Do not reopen product semantics unless a minimal compatibility change is strictly necessary.

## Required corpus changes

Update:
`tests/fixtures/sb_lf04_m04_regression_v1.json`

so the remaining trust-boundary negatives are fully declarative.

At minimum encode and consume:

### 1. VERIFIED_CANONICAL mint rejection

The corpus must provide the attempted receipt data:
- disposition = VERIFIED_CANONICAL;
- state digest;
- evidence digest source/reference;
- provider id;
- provider version;
- proof digest;
- expected = rejection.

The regression test must build the attempted `MetricEvidence` using corpus values, not hard-coded provider/digest strings.

If “generic mint helper must not exist” remains part of the invariant, put the symbol name in corpus mutation data and have the test consume it.

### 2. Cross-metric producer binding rejection

The corpus must declare:
- source result family/metric id;
- attempted target MetricId;
- expected rejection.

Drive `bind_verified_metric_producer()` or the relevant safe negative path from those payload values.

Because current providers are production-unavailable, do not create a fake positive verified receipt. The test may prove rejection before a verified binding can exist.

### 3. Cross-level/evidence binding rejection

Declare a mismatch mutation, such as:
- altered LevelData/source SHA;
- altered solver-evidence digest;
- wrong target LevelMetrics identity.

The test must consume the declared mutation and prove fail-closed.

## Existing regression guarantees to retain

Keep:
- payload-driven 001..011 task-family execution;
- checksummed corpus;
- 004–007 production UNAVAILABLE;
- 008 ChallengeScore integrity;
- 009 lane integrity;
- 010 provider-string/unavailable binding rejection;
- 011 calibration disabled;
- exact LevelData byte/SHA non-mutation;
- exact logical-art byte/SHA non-mutation;
- capability-gated canonical ScrubBots checkout non-mutation.

## Gates

Run:
1. focused SB-LF04-012 R03;
2. focused 004–010 trust/provenance tests;
3. all M04;
4. retained M03;
5. full `python -m pytest -q` with zero failures;
6. compileall;
7. Godot headless;
8. git diff --check;
9. TASKS zero diff.

Recompute corpus SHA-256 after payload changes.

Publish implementation + R03 builder log, then terminal log-only commit.

STOP for independent ChatGPT re-audit.
