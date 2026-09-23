# SB-LF04-001-C001-R01 — Windows Runner Identity Portability & Full-Gate Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-001 — Define versioned LevelMetrics.`

Strict audit:
`.hiveai/audits/SB-LF04-001-C001_VERSIONED_LEVEL_METRICS_CONTRACT_STRICT_AUDIT.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-001-C001-R01_WINDOWS_RUNNER_IDENTITY_PORTABILITY_AND_FULL_GATE_CLOSURE_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## Mission

Close only the remaining acceptance-gate failure.

The LevelMetrics V1 product implementation is retained.

Do not redesign:
- `level_metrics.py`;
- M03 solver semantics;
- canonical bridge request/response semantics;
- runner operation semantics;
- Challenge Score or any later M04 metric calculation.

## Confirmed audit fact

Committed GitHub runner bytes currently hash to:

`b66f307c4103a714d02b03ce61e7413e3ff07e0e90fb19b3417cc54afef05c3f`

This exactly matches `CANONICAL_BRIDGE_RUNNER_SHA256`.

The C001 full-suite failures are caused by Windows checkout-byte line-ending drift, not by a changed committed runner.

## Required fix

Preserve exact physical runner-byte verification.

Preferred narrow repository fix:

Create/update root `.gitattributes` with an explicit rule:

`tools/scrubbots_canonical_bridge_runner.gd text eol=lf`

Keep the scope narrow. Do not globally rewrite unrelated repository line-ending policy unless demonstrably required.

### Forbidden shortcuts

Do not:
- change `CANONICAL_BRIDGE_RUNNER_SHA256` to a CRLF-derived hash;
- accept multiple runner hashes;
- normalize CRLF/LF inside `CanonicalHeadlessBridge` before hashing;
- weaken runner-path identity or runner SHA validation;
- skip/deselect/xfail the two failing canonical tests;
- modify the owner's ScrubBots checkout;
- edit root TASKS;
- start SB-LF04-002.

## Portability regression

Add a focused regression that proves repository checkout behavior, not merely the current worktree.

On Windows, create a temporary clean local clone/worktree of the Level Factory repository after the line-ending policy is committed, with `core.autocrlf=true` or equivalent Windows-style checkout configuration.

Prove:

1. `tools/scrubbots_canonical_bridge_runner.gd` materializes with byte SHA-256 exactly equal to `CANONICAL_BRIDGE_RUNNER_SHA256`;
2. `git check-attr` or equivalent confirms the runner's explicit LF policy;
3. no runner content/operation change was needed;
4. the repository remains clean.

The test must be offline/local and must not depend on network access.

## Required verification

Run without deselection:

1. focused SB-LF04-001 tests;
2. runner portability regression;
3. `tests/unit/test_sb_lf03_009_canonical_bridge.py`;
4. `tests/unit/test_sb_lf03_012_regression_fixtures.py`;
5. retained M03 + difficulty/production tests;
6. full `python -m pytest -q` with **zero failures**;
7. `python -m compileall -q src tests`;
8. Level Factory Godot headless editor boot;
9. `git diff --check`;
10. `git diff --exit-code -- TASKS.md`.

Record exact pass/skip/warning counts.

A legitimate capability skip is acceptable only where its original test contract explicitly allows capability absence. The two previously failing configured real-canonical tests must not be hidden by deselection.

## Publication

1. Create the R01 builder log before edits.
2. Implement the narrow portability fix + tests.
3. Run all gates.
4. Commit/push implementation and log.
5. Finalize the R01 log with exact SHAs/results.
6. Publish terminal log-only commit.
7. STOP for independent ChatGPT re-audit.

Do not create audit files.
