# SB-CP00-001-C001 — Content Platform Control-Plane Boundary — Audit Criteria

## PASS rule

PASS only if a real root-level `content_pipeline/` control-plane project boundary exists and is mechanically separated from Level Factory generation internals and Scrubbots runtime/gameplay code.

## Required

- canonical `content_pipeline/` project/package skeleton;
- explicit config/schema boundary;
- environment abstraction placeholders;
- provider interface placeholder;
- validation-only/dry-run boundary;
- publish/promote/rollback orchestration interfaces without live mutation;
- evidence/report boundary;
- architecture documentation;
- focused tests.

## Forbidden

- live remote mutation;
- credentials/secrets;
- runtime/game imports;
- arbitrary executable remote payload support;
- duplicated generator/solver implementation;
- reverse dependency from Level Factory core;
- second task tracker.

## Regression

Require:
- focused boundary/import tests PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- git diff --check PASS;
- root governance/tracker tests PASS.

Codex must not edit root `TASKS.md` or audit files.
