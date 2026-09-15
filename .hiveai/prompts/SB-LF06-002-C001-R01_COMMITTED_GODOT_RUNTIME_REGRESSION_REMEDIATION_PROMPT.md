# SB-LF06-002-C001-R01 — Committed Godot Runtime Regression Remediation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Remediate only the strict-audit finding for:

`SB-LF06-002 — Target difficulty/dimensions/seed/mode/candidate controls. [PARTIAL]`

Source audit:

`.hiveai/audits/SB-LF06-002-C001_FACTORY_STUDIO_TARGET_CONTROLS_STRICT_AUDIT.md`

The C001 target-control product implementation is retained. Do not redesign it.

The only acceptance blocker is that the real Godot interaction regression was executed through a disposable project-local runner that was deleted before publication. A clean checkout therefore does not preserve the exact executable runtime-test path.

R01 must make the LF06-001/LF06-002 Godot scene-interaction regression **repository-native, committed, and repeatable from a clean checkout**.

Do not begin `SB-LF06-003` or any `SB-LFX-*` task.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this R01 prompt;
3. `.hiveai/audits/SB-LF06-002-C001_FACTORY_STUDIO_TARGET_CONTROLS_STRICT_AUDIT.md`;
4. original `SB-LF06-002-C001` prompt and finalized builder log;
5. `.hiveai/audits/SB-LF06-001-C001-R01_FACTORY_STUDIO_RUNTIME_NODE_CONTRACT_REMEDIATION_STRICT_AUDIT.md`;
6. `level_factory/project.godot`;
7. `level_factory/scenes/factory_studio.tscn`;
8. current Factory Studio scripts;
9. `tests/support/factory_studio_runtime_contract.gd`;
10. `tests/support/factory_studio_target_controls_contract.gd`;
11. focused LF06-001/LF06-002 Python tests;
12. `level_factory/README.md`, `level_factory/GOVERNANCE.md`, and directory-boundary tests.

Before implementation create and verify:

`.hiveai/codex-logs/SB-LF06-002-C001-R01_COMMITTED_GODOT_RUNTIME_REGRESSION_REMEDIATION_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## F-SB-LF06-002-MAJOR-001 — Preserve a clean-checkout executable Godot regression

### Required outcome

A freshly synchronized checkout must contain everything required to run a deterministic headless command that:

1. starts under the real `level_factory/` Godot project;
2. loads and instantiates `res://scenes/factory_studio.tscn`;
3. verifies the accepted LF06-001 runtime node/navigation contract;
4. navigates to Generate;
5. verifies the real LF06-002 target controls;
6. edits representative controls including an independent rectangle;
7. verifies deterministic draft snapshot state;
8. verifies `DRAFT`, Core `UNAVAILABLE`, and no generation execution claim;
9. verifies leaving/re-entering Generate preserves the current scene-session draft;
10. exits nonzero on any failed assertion and zero on success.

### Preferred implementation shape

Prefer a very small **project-local committed SceneTree/MainLoop test entrypoint** under the existing `level_factory/tests/` boundary, for example conceptually:

`level_factory/tests/factory_studio_runtime_suite.gd`

that can be invoked directly from a clean checkout with a stable command such as:

`godot --headless --path level_factory --script res://tests/factory_studio_runtime_suite.gd`

Exact filename may differ if repository conventions justify it, but the runner must be committed and the command must use only committed files.

Do not rely on creating/copying/deleting temporary runner scripts or temporarily replacing `run/main_scene` merely to execute the acceptance test.

If the existing root `tests/support/*.gd` contracts are reused, the project-local committed entrypoint may coordinate them only if that works without `res://../` escape references or other project-boundary violations. Otherwise consolidate the runtime assertions cleanly into the project-local entrypoint and keep/remove old support scripts only as justified by tests and boundary rules.

Avoid duplicated product logic. Test assertions may naturally restate expected UI behavior.

## Clean-checkout reproducibility rule

The R01 builder log must record the exact committed command and demonstrate that the command succeeds **after all temporary/disposable files are absent**.

Before the final runtime invocation:

- confirm there are no untracked test-runner files other than the four pre-existing owner-local UID files already documented;
- confirm no temporary `project.godot` mutation exists;
- confirm the runner itself is tracked;
- run the committed command from the canonical synchronized repository;
- record stdout/stderr summary and exit code.

Do not claim clean-checkout reproducibility if an uncommitted helper is required.

## Python regression protection

Add/adjust narrow Python tests so the committed repository protects the runtime-test entrypoint itself.

At minimum, assert:

- the project-local runner exists at the expected committed path;
- it is inside `level_factory/` and does not escape via `res://../`;
- it loads the real Factory Studio scene;
- it contains fail-closed/nonzero termination behavior;
- it exercises Generate target controls rather than only checking source strings.

If it is practical without making Python-only environments fail spuriously, a Python test may invoke Godot when an approved executable is available. However the core acceptance requirement is the committed standalone Godot command plus actual builder execution of that command from the clean tracked tree.

Do not add a hard dependency that makes the ordinary Python test suite unusable on machines that legitimately do not have Godot installed unless the repository already requires that dependency.

## Preserve accepted product behavior

Do not change the following unless the committed runner discovers a real defect:

- canonical difficulty presentation choices;
- canonical generator-mode presentation choices;
- independent width/height 20..59 bounds;
- candidate presentation label boundary;
- deterministic draft snapshot semantics;
- `DRAFT` / `UNAVAILABLE` / `NOT EXECUTED` truthfulness;
- existing inert Dashboard/other surfaces;
- status-only `FactoryCoreGateway`;
- no operational Generate/Solve/Validate behavior.

If the new clean-checkout runner discovers a product/runtime defect, fix only that directly evidenced defect and record it explicitly in the builder log. Do not broaden scope silently.

## Forbidden scope

Do not implement:

- `SB-LF06-003` actions;
- canonical-Core process/CLI integration;
- Dashboard operations;
- Import or Source Art Library;
- provider/network/API behavior;
- solver;
- Content Platform;
- main-game work;
- a new test framework;
- a second tracker;
- edits to root `TASKS.md`.

No provider/network calls and no provider credits.

## Required verification

Run and record at minimum:

1. the new committed clean-checkout Godot runtime command;
2. LF06-001 focused Python tests;
3. LF06-002 focused Python tests;
4. canonical LF01 dimension/request focused tests;
5. full `python -m pytest -q`;
6. `python -m compileall -q src tests`;
7. normal `godot --headless --path level_factory --quit` project smoke;
8. `git diff --check`;
9. `git ls-files` or equivalent evidence proving the runtime runner is tracked;
10. changed-file/scope review proving root `TASKS.md`, providers, solver, Content Platform, main-game and SB-LF06-003 are untouched.

Record failed commands and corrections truthfully.

## Acceptance criteria

PASS eligibility requires all of the following:

- [ ] C001 target-control product implementation remains retained;
- [ ] a project-local runtime-test entrypoint is committed;
- [ ] exact headless runtime command uses only committed files;
- [ ] clean tracked tree can execute the command without a disposable runner;
- [ ] real `factory_studio.tscn` is instantiated;
- [ ] LF06-001 node/navigation contract remains covered;
- [ ] LF06-002 Generate target controls are interacted with at runtime;
- [ ] independent rectangle/difficulty behavior remains covered;
- [ ] draft/Core-unavailable/no-operation truth remains covered;
- [ ] failed runtime assertions produce nonzero exit;
- [ ] focused and full regression pass;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] no scope creep;
- [ ] finalized R01 builder log is published truthfully;
- [ ] builder stops for independent ChatGPT strict audit.

## Publication discipline

Use the already accepted non-self-referential pattern:

1. implementation commit;
2. push and record implementation equality checkpoint;
3. final log-only publication commit;
4. hand the actual final publication SHA to the user externally.

Do not create another post-final equality-log commit.

## GitHub handoff

Push remediation/tests and finalized R01 builder log to `main`.

At completion give the user only:

1. full GitHub URL of the finalized R01 builder log;
2. remediation implementation commit SHA;
3. actual final publication commit SHA.

Then stop for independent ChatGPT strict audit.
