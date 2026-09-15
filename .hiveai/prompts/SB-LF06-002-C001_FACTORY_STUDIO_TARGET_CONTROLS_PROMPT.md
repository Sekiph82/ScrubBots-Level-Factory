# SB-LF06-002-C001 — Factory Studio Target Controls
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Implement only:

`SB-LF06-002 — Target difficulty/dimensions/seed/mode/candidate controls. [PARTIAL]`

This cycle resumes M06 after the independently audited closure of `SB-LF01-005`. The Factory Studio shell is real and the canonical Python Factory Core now has the owner-locked independent dimension contract.

Build the **Generate target-control presentation surface** for Factory Studio. It must collect operator intent for future generation without implementing generation itself and without creating a second compiler or second semantic truth.

Do not begin `SB-LF06-003`, any `SB-LFX-*` task, Dashboard operational behavior, Import, Source Art Library, solver, provider/API/network integration, Content Platform, or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this prompt;
3. `.hiveai/audits/SB-LF01-005-C001-R01_MANIFEST_VERSION_GATE_AND_WORKLOAD_GUIDANCE_REMEDIATION_STRICT_AUDIT.md`;
4. `.hiveai/audits/SB-LF06-001-C001-R01_FACTORY_STUDIO_RUNTIME_NODE_CONTRACT_REMEDIATION_STRICT_AUDIT.md`;
5. `level_factory/scenes/factory_studio.tscn`;
6. `level_factory/scripts/factory_studio_shell.gd`;
7. `level_factory/scripts/factory_studio_navigation.gd`;
8. `level_factory/scripts/factory_studio_workspace_page.gd`;
9. `level_factory/scripts/factory_core_gateway.gd`;
10. `tests/support/factory_studio_runtime_contract.gd`;
11. `tests/unit/test_sb_lf06_001_factory_studio_workspace.py`;
12. canonical Python contracts for `Difficulty`, `GeneratorMode`, `GenerationRequest`, and `PRODUCTION_DIMENSION_ENVELOPE`;
13. relevant retained PAG-SP09 / Windows Factory Studio evidence if present, using it only as migration/UI evidence rather than canonical compiler truth.

Before implementation create and verify:

`.hiveai/codex-logs/SB-LF06-002-C001_FACTORY_STUDIO_TARGET_CONTROLS_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## 1. Required Generate target controls

The `Generate` Studio surface must expose a real operator form containing at minimum:

- **Difficulty** selection for exactly the current canonical difficulty labels:
  - `EASY`
  - `MEDIUM`
  - `HARD`
  - `VERY_HARD`
- **Width** control;
- **Height** control;
- **Seed** input;
- **Generator Mode** selection for exactly the current canonical modes:
  - `MASK`
  - `RULES`
  - `WFC`
  - `HYBRID`
  - `AUTO`
- a bounded **Candidate** presentation control, such as an optional requested candidate label/ID field, that does not manufacture a canonical accepted candidate identity or bypass the existing canonical identity rules;
- a clear draft/configuration state readout.

Do not add Generate/Solve/Validate/Analyze/Reproduce buttons as operational actions in this cycle. Those belong to `SB-LF06-003`.

## 2. Independent dimension presentation

Width and height presentation must reflect the accepted current canonical envelope:

- width `20..59` inclusive;
- height `20..59` inclusive;
- axes independent;
- rectangles legal;
- no difficulty-to-size mapping;
- no square lock;
- no used-color-to-size mapping.

The Studio must visibly allow examples such as `20x59`, `59x20`, `23x47`, and `52x31` for every difficulty selection.

Do not create EASY/MEDIUM/HARD/VERY_HARD dimension bands in GDScript, scene resources, labels, presets, defaults, or tooltips.

## 3. Canonical-Core authority and cross-language drift guard

The Python Factory Core remains authoritative.

It is acceptable for the Godot presentation layer to contain the finite UI choices and widget bounds needed to render controls, but those values are **presentation affordances**, not a second validation engine.

Required safeguards:

- no GDScript reimplementation of `GenerationRequest` validation;
- no GDScript difficulty formula;
- no GDScript generator router;
- no GDScript candidate compiler;
- no claim that an edited draft is canonically valid merely because the widgets accept it;
- add automated cross-language contract tests that bind the Studio's displayed difficulty values, generator-mode values, and width/height bounds to the canonical Python `Difficulty`, `GeneratorMode`, and `PRODUCTION_DIMENSION_ENVELOPE` values;
- if the Python contract changes without the presentation being updated, tests must fail.

Do not introduce a generated duplicate truth file unless there is a compelling repository-native reason. Prefer direct regression comparison against canonical Python symbols.

## 4. Draft state contract

Create a small, deterministic presentation-state boundary for the target controls.

A draft snapshot should expose the operator-entered presentation values in a stable structure containing at least:

- difficulty;
- width;
- height;
- seed text/value as entered;
- generator mode;
- candidate presentation field.

The snapshot is **not** a canonical `GenerationRequest` and must not be labeled as one until a later audited Core integration performs canonical parsing/validation.

Recommended status language:

- `DRAFT`;
- `CORE VALIDATION: UNAVAILABLE` while `FactoryCoreGateway` remains status-only/unavailable;
- wording that explicitly says no generation has occurred.

Changing controls should update the presentation draft deterministically and may emit a local `draft_changed` signal. It must not write files, launch processes, access providers, or generate candidates.

## 5. Core unavailable behavior

`FactoryCoreGateway` is currently a truthful status-only boundary with `UNAVAILABLE` status.

This cycle must preserve that truth.

The Studio may allow an operator to edit a draft while Core is unavailable, but it must not:

- mark the draft `VALID`;
- mark Core `AVAILABLE`;
- manufacture validation results;
- create candidate output;
- invoke Python through `OS.execute` or a subprocess;
- read/write a local pseudo-Core workspace;
- call any provider/network service.

The Generate surface should make the distinction visually obvious:

`editable presentation draft != canonically validated GenerationRequest`.

## 6. Candidate control boundary

The required Candidate control is intentionally narrow in this cycle.

It may collect an optional requested candidate label/ID or other already-established presentation identifier, but it must not:

- generate final accepted candidate IDs;
- overwrite deterministic batch candidate identities;
- imply acceptance/promotion;
- create candidate files;
- expose batch-count behavior from M08;
- introduce a new candidate identity algorithm.

If historical Studio evidence contains a candidate-control concept, reuse only presentation behavior compatible with current canonical identity rules.

## 7. UI and navigation behavior

Preserve the accepted navigation list and Studio shell.

Required behavior:

- Dashboard remains truthful placeholder behavior;
- selecting `Generate` shows the real target-control form;
- returning to Dashboard and back to Generate must not crash;
- draft values should remain deterministic for the current scene/session unless an explicit reset is implemented;
- all other surfaces remain truthful `NOT IMPLEMENTED` placeholders;
- existing footer Core status remains truthful.

Do not implement the Dashboard extension in this cycle.

## 8. Required executable tests

Add/extend automated evidence proving at minimum:

1. real `factory_studio.tscn` instantiates headlessly;
2. `Generate` navigation reaches the target-control surface;
3. all required controls exist at deterministic node paths or through a deterministic component contract;
4. difficulty UI choices exactly equal canonical Python `Difficulty` values;
5. mode UI choices exactly equal canonical Python `GeneratorMode` values;
6. width/height UI bounds exactly equal `PRODUCTION_DIMENSION_ENVELOPE` `20..59`;
7. width and height are independent and representative rectangles can be entered;
8. changing difficulty does not alter width/height bounds or force a different board size;
9. draft snapshot updates deterministically after edits;
10. draft state does not claim canonical validation while Core is unavailable;
11. no candidate/generated artifact is produced;
12. navigation back to Dashboard and to another inert surface remains stable;
13. existing executable SB-LF06-001 runtime-node contract remains green.

At least one Godot headless runtime test must instantiate and interact with the real committed scene rather than only grep source text.

Cross-language Python tests must compare presentation choices/bounds to canonical Python symbols rather than hard-code a second expected semantic contract where avoidable.

## 9. Required regression and verification

Run and record at minimum:

1. new focused SB-LF06-002 tests;
2. prior SB-LF06-001 focused tests;
3. executable Godot scene/runtime contract(s);
4. SB-LF01-005 dimension tests;
5. request/difficulty contract tests affected by the cross-language guard;
6. full `python -m pytest -q`;
7. `python -m compileall -q src tests`;
8. Godot headless project smoke;
9. `git diff --check`;
10. changed-file review proving no root `TASKS.md`, provider, solver, Content Platform, main-game, Dashboard-operation, Import, Library, batch, or output scope creep.

Record failed commands and corrections truthfully.

## 10. Forbidden implementation markers

Unless the existing accepted shell already contains them for truthful inert text, new Studio implementation for this cycle must not introduce operational use of:

- `OS.execute`;
- subprocess/process launching;
- `HTTPRequest`, `HTTPClient`, WebSocket;
- `FileAccess` or `DirAccess` for pseudo-Core state;
- provider names/credentials/API keys;
- `generate(`, `solve(`, `validate(` or equivalent local compiler implementations in GDScript;
- main-game repository paths.

No network/provider calls. No credits may be spent.

## 11. Allowed scope

Allowed only as required for target-control presentation and tests:

- `level_factory/scenes/**`;
- `level_factory/scripts/**`;
- narrowly required `level_factory/docs/**` or README text;
- Factory Studio runtime support tests;
- Python regression tests that compare Studio presentation values against canonical Core symbols;
- matching builder log.

Do not modify canonical Python Core semantics merely to make the UI easier. If a genuine Core defect is discovered, stop and record it rather than silently widening scope.

## 12. Acceptance criteria

PASS eligibility requires all of the following:

- [ ] Generate surface exposes real difficulty/dimensions/seed/mode/candidate target controls;
- [ ] UI difficulty choices match canonical Python difficulty values;
- [ ] UI mode choices match canonical Python generator modes;
- [ ] width and height are independently `20..59` and rectangles remain possible for every difficulty;
- [ ] no difficulty-size coupling is introduced;
- [ ] deterministic draft snapshot/state exists;
- [ ] draft is clearly presentation-only and not falsely called canonically valid;
- [ ] Core remains truthfully `UNAVAILABLE` unless an authorized real integration exists;
- [ ] no generation/solve/validate/analyze/reproduce operation is implemented;
- [ ] no provider/network/file-backed pseudo-Core behavior;
- [ ] no candidate identity algorithm is invented;
- [ ] Dashboard and other non-target surfaces remain truthful placeholders;
- [ ] real Godot runtime interaction test passes;
- [ ] cross-language drift guards pass;
- [ ] prior LF06-001 and LF01-005 regressions remain green;
- [ ] full regression/toolchain checks pass;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] finalized builder log is pushed truthfully;
- [ ] builder stops for independent ChatGPT strict audit.

## Builder log requirements

H1 exactly:

`# SB-LF06-002-C001 — Factory Studio Target Controls`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- synchronization/base SHA/status/worktrees;
- required reads and historical Studio evidence consulted;
- pre-edit scene/control inventory;
- target-control design and why it is presentation-only;
- exact changed files/symbols/node paths;
- cross-language drift-guard strategy;
- failed commands/corrections;
- focused Python results;
- executable Godot runtime results;
- full regression/toolchain results;
- TASKS no-change proof;
- no provider/network/Core-clone/main-game scope creep;
- implementation commit and push/equality checkpoint;
- truthful final log-only publication discipline.

Do not self-audit or edit tracker state.

## GitHub handoff

Push implementation, tests, and finalized builder log to `main`.

At completion provide only:

1. full GitHub URL of the finalized builder log;
2. implementation commit SHA;
3. actual final publication commit SHA.

Then stop for independent ChatGPT strict audit.
