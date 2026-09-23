# SB-LF03-012-C001-R03 — Declarative Negative Corpus Closure

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF03-012 — Add regression fixtures.`

R02 re-audit:
`.hiveai/audits/SB-LF03-012-C001-R02_REAL_REGRESSION_AND_GREEN_FULL_GATE_REMEDIATION_STRICT_REAUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-012-C001-R03_DECLARATIVE_NEGATIVE_CORPUS_CLOSURE_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Retain accepted R02 behavior

Preserve:
- real clean-checkout canonical Godot regression;
- repeated legal_moves / apply_placement / solve invocation;
- deterministic real responses;
- checkout/source immutability;
- green full repository gate;
- narrowed LF00 text-only static scans;
- no hidden skip/xfail of failures.

## Dependency

Run after SB-LF03-009 R03 and SB-LF03-011 R03.

## Finding A — negative corpus must be real declarative fixtures

Remove the string-only `r01_negative_fixture_ids` pseudo-corpus.

Create actual versioned declarative fixture objects for all eight families:

1. `LF03_WRONG_QUERY_RESULT_BINDING_V1`
2. `LF03_WRONG_STATE_KEY_BINDING_V1`
3. `LF03_TRANSITION_AUTHORITY_DRIFT_V1`
4. `LF03_ENUMERATION_BINDING_V1`
5. `LF03_FRONTIER_PEAK_WIDE_SHALLOW_V1`
6. `LF03_REPLAY_IDENTITY_TAMPER_V1`
7. `LF03_MAX_VISITED_EXECUTION_STOP_V1`
8. `LF03_TIMEOUT_NONCANONICAL_V1`

Each fixture must contain:
- stable id;
- family/schema version;
- `production: false` where fixture providers are fake;
- declarative input/state/identity payload sufficient to execute the test;
- explicit expected disposition/metrics/result;
- canonical payload SHA-256.

The checksum test must recompute every fixture payload SHA-256.

Tests must load the fixture and drive behavior from its payload. Merely checking that an ID exists is forbidden.

Task-specific tests may remain, but the regression corpus itself must now be durable and executable.

## Finding B — protect the R03 009 LevelData source binding

Update canonical bridge fixture to carry exact canonical Level Data V1 source bytes or the accepted source representation introduced by 009 R03.

Regression must prove:
- source hash recomputed from exact bytes;
- one-cell tamper + stale hash fails closed;
- real legal_moves/apply_placement/solve still pass with correctly bound source.

## Finding C — protect the R03 011 timeout separation

The timeout fixture must prove:
- same deterministic result with/without operational timeout telemetry => identical canonical deterministic bytes;
- timeout-before-result => no canonical deterministic result;
- operational telemetry differs and is non-canonical.

## Full gate

Keep repository full suite green.

Run at minimum:
- focused 012;
- all remediated 009/011 tests;
- retained LF03;
- affected LF00/LF06;
- full `python -m pytest -q`;
- preferably repeat full suite from clean tracked state;
- compileall;
- Level Factory Godot headless editor boot;
- real canonical bridge regression;
- git diff --check;
- git diff --exit-code -- TASKS.md.

Do not skip/xfail failures to achieve green.

Publish R03 implementation + finalized task log + terminal log-only commit.
