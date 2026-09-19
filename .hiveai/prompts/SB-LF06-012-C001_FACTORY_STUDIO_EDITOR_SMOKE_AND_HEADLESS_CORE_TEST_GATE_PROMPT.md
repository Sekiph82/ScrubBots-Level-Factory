# SB-LF06-012-C001 — Factory Studio Editor Smoke + Headless Core Test Gate

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF06-012 — Editor smoke + headless core tests. [PARTIAL]`

This is the final canonical M06 Studio test-closure task. It is primarily test orchestration + truthful verification documentation, not a new product feature.

Create/finalize builder log:

`.hiveai/codex-logs/SB-LF06-012-C001_FACTORY_STUDIO_EDITOR_SMOKE_AND_HEADLESS_CORE_TEST_GATE_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read:
- root `TASKS.md`;
- LF06-011 closing strict audit;
- `.hiveai/audit-criteria/SB-LF06-012-C001_EDITOR_SMOKE_AND_HEADLESS_CORE_TEST_GATE_AUDIT_CRITERIA.md`;
- `level_factory/README.md`;
- existing `factory_studio_runtime_suite.gd`;
- existing action/exact-reproduce integration suites;
- clean-checkout/project-boundary tests;
- canonical CLI Generate/Reproduce and output contracts.

## 1. Reuse existing Studio smoke

Do not write another giant Godot scenario.

Use the committed real Factory Studio runtime suite as the editor smoke lane unless a narrowly demonstrated gap prevents it.

The final focused gate must actually execute Godot headlessly and fail on a non-zero result or missing PASS marker.

## 2. Add a direct headless canonical Core smoke lane

Add one bounded focused Python test/harness that directly exercises canonical Python Core outside Godot.

Required:
1. explicit deterministic seed;
2. legal rectangular dimensions;
3. real canonical Generate;
4. bounded temporary/test output;
5. valid canonical metadata/bundle;
6. real canonical Reproduce from the generated `metadata.json`;
7. MATCH / exit 0;
8. source/reproduction canonical artifact byte identity under the accepted reproduce contract;
9. cleanup.

Do not duplicate generation/reproduction semantics in the test.

## 3. One final focused acceptance gate

The LF06-012 focused test family must fail if either:
- real Studio headless smoke fails; or
- direct canonical Core headless Generate/Reproduce smoke fails.

Keep runtime bounded. Do not invoke the full 700+ test suite from inside a test.

## 4. Correct stale README verification text

`level_factory/README.md` currently says `tests/` is reserved for future Godot-local tests. That is no longer true.

Minimally update it to document:
- committed Godot-local tests now exist;
- root Python Core remains canonical;
- the focused LF06-012 smoke command;
- `godot --headless --path level_factory --quit`;
- `python -m pytest -q` for full regression;
- smoke requires no GUI, provider network or credentials.

Do not create a second tracker/status ledger in README.

## 5. Preserve accepted architecture

No product/Core semantic changes are expected.

If the focused smoke discovers a real defect, make only the smallest bounded correction and document it. Do not refactor accepted LF06-001..011 code for style.

Preserve:
- canonical Python authority;
- Generate/Reproduce semantics;
- dependency-gated Solve/Validate/Analyze;
- preview/evidence/editor/config/revalidation truth;
- exact reproduction;
- clean-checkout/offline boundaries.

## 6. Forbidden scope

Do not implement:
- SB-LFX tasks;
- M03/M04/M05;
- persistence/revision history;
- owner acceptance/promotion;
- Content Platform;
- main-game runtime;
- providers/network/credentials.

Do not modify root `TASKS.md`.

## 7. Verification

Run and record:
- focused LF06-012 gate;
- direct committed Godot Studio runtime suite if not already executed by the gate;
- relevant retained LF06-001..011 regressions;
- full `python -m pytest -q`;
- compileall;
- Godot headless project boot;
- `git diff --check`;
- `git diff -- TASKS.md` empty;
- exact changed-file review.

Expected publication:
1. implementation/test/docs commit(s);
2. push/equality checkpoint;
3. exactly one terminal builder-log-only publication commit;
4. stop.

At completion give only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF06-012-C001_FACTORY_STUDIO_EDITOR_SMOKE_AND_HEADLESS_CORE_TEST_GATE_CODEX_LOG.md`;
2. final implementation commit SHA;
3. terminal log-only publication commit SHA.
