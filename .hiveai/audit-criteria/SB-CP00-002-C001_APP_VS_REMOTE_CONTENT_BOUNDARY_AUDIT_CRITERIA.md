# SB-CP00-002-C001 — App Code vs Remote Content Boundary — Audit Criteria

## PASS rule

PASS only if a versioned, deterministic, fail-closed app-vs-remote-content boundary exists under `content_pipeline/` and executable/application code cannot be classified as remotely deliverable.

## A. Versioned contract

Require:
- machine-readable/versioned boundary schema or model;
- deterministic classification result;
- deterministic reason codes;
- explicit REMOTE_DECLARATIVE vs APP_OWNED/REJECTED semantics.

## B. Allow-list / fail-closed

Remote eligibility must be allow-list based.

Unknown extension/type/schema/path form fails closed.

## C. Executable payload rejection

Must reject at minimum:
- GDScript/scripts;
- Python;
- executable/native binary payloads;
- plugins/addons;
- script-bearing scene/resource descriptors;
- executable expressions/script references;
- absolute paths;
- path traversal.

No payload may be executed/imported to classify it.

## D. Declarative acceptance

Tests must show valid current declarative level/supply/metadata descriptors can be accepted without importing game/runtime code.

## E. Architectural preservation

Retain SB-CP00-001:
- no live remote mutation;
- no provider implementation;
- no credentials;
- no game/runtime imports;
- no reverse dependency;
- no second tracker.

## F. Regression

Require:
- focused SB-CP00-002 tests PASS;
- prior SB-CP00-001 tests PASS;
- governance/tracker tests PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- git diff --check PASS.

Codex must not edit root `TASKS.md` or audit files.
