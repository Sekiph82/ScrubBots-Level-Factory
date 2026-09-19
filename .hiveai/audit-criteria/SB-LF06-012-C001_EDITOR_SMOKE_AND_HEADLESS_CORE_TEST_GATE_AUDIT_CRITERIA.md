# SB-LF06-012-C001 — Editor Smoke + Headless Core Test Gate — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target requirement:

`SB-LF06-012 — Editor smoke + headless core tests. [PARTIAL]`

## 1. Purpose

Close the final canonical M06 Studio test requirement without adding another product feature or duplicating the existing LF06-001..011 integration suites.

The repository already contains substantial accepted evidence:
- committed Factory Studio headless runtime smoke;
- real Studio -> canonical Python Generate/Reproduce integration;
- preview/evidence/editor/config-gate/revalidation/truth-separation/exact-reproduce runtime suites;
- root Python Core unit/integration tests;
- clean-checkout/tracked-resource guards.

LF06-012 must add a small, explicit final acceptance gate showing that:
1. the committed editor-facing Studio shell can be smoke-tested headlessly;
2. the canonical Python Factory Core can be exercised headlessly and offline from the same repository;
3. the documented verification commands are current and reproducible.

## 2. Severity model

### BLOCKER
Automatic FAIL if:
- the smoke gate requires GUI interaction, network/provider access, credentials, sibling repositories, ignored files or local caches;
- a second Factory Core/test implementation is created in Godot;
- the test gate bypasses canonical Python CLI/Core semantics with fabricated stubs for the positive path;
- root `TASKS.md` is modified by the builder;
- product semantics are changed merely to make a test pass without a separately demonstrated defect.

### MAJOR
Examples:
- no committed real headless Godot Studio smoke is executed by the final gate;
- no direct headless canonical Python Core smoke is executed;
- the Core smoke performs only import/--help and never runs a real deterministic generation;
- generated Core smoke output cannot be reproduced or verified deterministically;
- smoke relies on untracked/local artifacts;
- README verification instructions remain materially false or omit the actual focused smoke commands;
- final gate silently skips because Godot/Python is unavailable instead of failing clearly.

### MINOR
Examples:
- correct gate but a useful command/output marker is not documented;
- redundant test work adds avoidable runtime but does not weaken truth.

## 3. Reuse, do not duplicate

Prefer orchestration/reuse over writing another giant scenario.

The focused LF06-012 gate may invoke existing committed suites such as:
- `level_factory/tests/factory_studio_runtime_suite.gd`;
- the accepted real action integration suite where useful.

It must not copy the hundreds of assertions already owned by LF06-003..011.

## 4. Required editor smoke lane

A committed automated test must run Godot headlessly against the real `level_factory/` project and prove at minimum:
- project/scene instantiation succeeds;
- navigation/workspace/Generate surface exists;
- accepted target controls and independent 20..59 dimensions are present;
- no parse/missing-resource error occurs;
- the test exits non-zero on failure and emits a stable PASS marker on success.

Reusing the accepted `factory_studio_runtime_suite.gd` is preferred if it already satisfies these checks.

## 5. Required headless Core lane

The same focused acceptance family must directly exercise canonical Python Core without Godot owning semantics.

At minimum:
1. invoke the committed canonical CLI/launcher or package entrypoint headlessly;
2. run a deterministic legal Generate using an explicit seed and rectangular dimensions;
3. write output only to a bounded temporary/test output location;
4. verify a valid canonical bundle/metadata is produced;
5. run canonical Reproduce from that recorded metadata;
6. require MATCH / successful exit;
7. prove source and reproduction logical identity and canonical artifact bytes match under the accepted reproduce contract;
8. clean temporary outputs.

The test may reuse accepted Python APIs to inspect canonical output, but generation/reproduction authority must remain the real canonical CLI/Core path.

## 6. Offline / clean environment boundary

Focused LF06-012 smoke must require no:
- HTTP/provider/cloud access;
- API keys/credentials;
- main-game/sibling repo;
- local `.godot/` cache as an input;
- owner-local UID files;
- pre-existing generated output.

It must create and clean its own bounded test artifacts.

Retain the existing clean-checkout contract.

## 7. Verification documentation

The project-local README currently describes `tests/` as reserved for future Godot-local tests, which is stale.

LF06-012 should minimally correct documentation so it truthfully states:
- committed Godot-local tests exist;
- root Python tests remain canonical for Core semantics;
- exact focused LF06-012/editor smoke command;
- exact headless Godot project boot command;
- exact full Python regression command;
- no GUI/provider/network dependency is required for the smoke gate.

Do not turn README into a second tracker or acceptance ledger.

## 8. Required focused regression

PASS requires a focused committed test that fails if either lane fails.

It should verify:
- real headless Studio smoke PASS marker / exit 0;
- real headless Core Generate + Reproduce MATCH;
- deterministic/canonical artifact identity;
- bounded cleanup;
- no network/provider dependency;
- documentation includes runnable verification commands.

Static source-string checks may supplement, not replace, runtime execution.

## 9. Retained regression / publication

Builder must record:
- focused LF06-012 test command;
- direct Godot headless boot;
- retained LF06-001..011 regressions relevant to touched boundaries;
- full `python -m pytest -q`;
- compileall;
- `git diff --check`;
- `git diff -- TASKS.md` empty;
- exact changed-file review;
- exactly one terminal builder-log-only publication commit.

## 10. Scope limits

Do not implement:
- new Studio product features;
- solver/M03;
- Difficulty V1/M04;
- unified M05 validation;
- persistence/revision history;
- owner acceptance/promotion;
- SB-LFX work;
- Content Platform;
- main-game runtime work;
- provider/network integration.

Do not rewrite accepted LF06-001..011 scenarios just for consolidation.

## PASS closure rule

`SB-LF06-012` may close when one committed focused acceptance gate proves the real Factory Studio shell and canonical Python Core both operate headlessly/offline from a clean repository boundary, deterministic Generate/Reproduce is exercised for real, documentation is current, and all prior accepted Studio contracts remain green.
