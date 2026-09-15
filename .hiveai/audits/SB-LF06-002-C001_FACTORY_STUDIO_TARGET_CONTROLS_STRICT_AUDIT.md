# SB-LF06-002-C001 — Factory Studio Target Controls
Document role: CHATGPT STRICT AUDIT

Audit date: 2026-09-15
Repository: `Sekiph82/ScrubBots-Level-Factory`
Authoritative prompt: `.hiveai/prompts/SB-LF06-002-C001_FACTORY_STUDIO_TARGET_CONTROLS_PROMPT.md`
Starting tracker/base commit: `ad7805a88ca6bcd860a0e9fb06101515c9d7f43a`
Implementation commit: `d8623ab4ccc4c62c408fb8841ebfca6b7ac29b42`
Observed terminal builder publication commit: `d5d731cdac0ae5fa8e0273deb0be6b2d5d613ecd`
Builder log: `.hiveai/codex-logs/SB-LF06-002-C001_FACTORY_STUDIO_TARGET_CONTROLS_CODEX_LOG.md`

## 1. VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

The target-control product implementation is directionally correct and should be retained. The real Factory Studio Generate surface now exposes the requested presentation controls, keeps width/height independent, preserves Core `UNAVAILABLE`, avoids operational Generate/Solve/Validate behavior, and cross-language Python regression guards bind the displayed finite choices/bounds to canonical Python symbols.

The cycle is not eligible for closure because the required real Godot interaction regression is not reproducible from the committed clean checkout. Builder execution depended on a disposable project-local runner that was deleted before publication, while the committed Python tests only inspect the runtime-contract source text and do not execute the scene interaction contract.

Finding summary:

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0
- NOTE: 1

`SB-LF06-002` must remain active until a bounded R01 makes the runtime test repository-native and repeatable from the committed tree.

## 2. ACCEPTED PRODUCT IMPLEMENTATION

### 2.1 Generate target form is real and presentation-only

`level_factory/scripts/factory_studio_target_controls.gd` builds real controls for:

- Difficulty;
- independent Width;
- independent Height;
- Seed;
- Generator Mode;
- bounded Candidate presentation label;
- draft-state readout.

The snapshot explicitly reports:

- `state = DRAFT`;
- `core_validation = UNAVAILABLE`;
- `generation_state = NOT EXECUTED — presentation draft only`.

No operational action button is introduced in this cycle.

### 2.2 Canonical values are regression-bound rather than treated as a second compiler

The GDScript presentation constants expose the finite UI choices/bounds required by the form. `tests/unit/test_sb_lf06_002_factory_studio_target_controls.py` compares those values directly against canonical Python:

- `Difficulty`;
- `GeneratorMode`;
- `PRODUCTION_DIMENSION_ENVELOPE`.

This meets the prompt's cross-language drift-guard model. No GDScript `GenerationRequest` validator, generator router, difficulty formula, or candidate compiler was introduced.

### 2.3 Independent rectangles remain possible

The runtime contract exercises a `23x47` rectangle, checks independent 20..59 bounds, and iterates difficulty selections while confirming the dimension envelope remains unchanged.

The implementation has no square lock or difficulty-size mapping.

### 2.4 Core-unavailable truth is preserved

The existing `FactoryCoreGateway` remains status-only/unavailable. Generate is visibly a presentation draft and does not claim canonical validation.

Dashboard and other surfaces remain truthful placeholders.

### 2.5 Candidate identity boundary is respected

The Candidate field is explicitly a bounded presentation label. It does not generate accepted candidate IDs, write candidate files, alter deterministic batch IDs, or imply owner acceptance/promotion.

### 2.6 Scope and publication boundaries are clean

The implementation changes only the matching log, Factory Studio scene/presentation files, runtime-support contracts, and focused boundary/regression tests. Root `TASKS.md` was not changed by the builder.

The product/test tree freezes at `d8623ab4...`; `d8623ab4... -> d5d731cd...` changes only the matching builder log.

The builder also disclosed and reverted an initial pre-log uncommitted edit instead of hiding it. No published product-state ambiguity remains from that event.

## 3. FINDING

### F-SB-LF06-002-MAJOR-001 — Required real Godot interaction regression is not reproducible from the committed checkout

Severity: **MAJOR**

The authoritative prompt requires automated executable evidence and specifically requires at least one Godot headless runtime test that instantiates and interacts with the real committed `factory_studio.tscn` rather than only grepping source text.

The builder log states that the real LF06-001/LF06-002 contracts were executed through a **disposable project-local Godot runner** because the local Godot build did not reliably attach the root `tests/support` scripts directly. That runner and its temporary main-scene changes were then removed before the final diff.

The committed target runtime contract itself is under:

`tests/support/factory_studio_target_controls_contract.gd`

and now extends `Node`, not a standalone `SceneTree`/MainLoop entrypoint.

The committed Python test does not execute it. It only reads the file and asserts source markers such as:

- `runtime.startswith("extends Node")`;
- presence of `load(MAIN_SCENE_PATH)`;
- presence of `get_tree().root.add_child(instance)`.

Therefore a clean checkout can run the complete Python suite successfully while never executing the real Godot interaction contract. The exact passing runtime path recorded by the builder cannot be repeated from only the committed repository because the required runner was deleted.

This is an acceptance-evidence defect, not a reason to discard the target-control product implementation.

Required remediation:

1. commit a repository-native, project-local, headless Godot runtime runner/contract under the `level_factory/` project boundary, or otherwise make the committed contract directly runnable from a clean checkout;
2. the committed command must instantiate the real `res://scenes/factory_studio.tscn` and exercise the LF06-002 interactions, not only parse/grep files;
3. the same committed runtime path should also protect the accepted LF06-001 navigation/node contract where practical;
4. run the committed clean-checkout command with exit code 0 and record the exact command;
5. add regression coverage/documentation that protects the existence and intended executable entrypoint without requiring deleted temporary files;
6. do not broaden product behavior or begin SB-LF06-003.

A small project-local `SceneTree` test runner is sufficient. Do not build a test framework or second application.

## 4. NOTE

Builder evidence reports:

- focused Python: 11 passed;
- canonical dimension/request regression: 64 passed;
- affected boundary subset: 34 passed after cleanup;
- final full Python suite: 688 passed;
- compileall: PASS;
- `git diff --check`: PASS;
- manual/disposable-runner Godot LF06-001 and LF06-002 contracts: PASS;
- final headless Studio smoke: exit 0.

This audit independently verified committed source, tests, scope, and commit chronology through GitHub but did not independently execute the Windows Godot runtime.

The issue is not that no runtime execution ever occurred. The issue is that the runtime regression that produced the evidence is not preserved as a clean-checkout executable path.

## 5. REMEDIATION BOUNDARY

Retain the accepted target-control implementation.

R01 must be limited to:

- a committed/repeatable Godot runtime-test entrypoint;
- any minimal support change required to execute the existing LF06-001/LF06-002 contracts from the repository tree;
- narrow tests/docs proving that entrypoint;
- matching R01 builder log.

Do not change target-control semantics unless a direct runtime defect is discovered by the committed runner.

Do not begin:

- `SB-LF06-003`;
- Dashboard operational work;
- Import/Library;
- providers/network;
- solver;
- Content Platform;
- main-game work.

## 6. CLOSURE RULE

`SB-LF06-002` remains active. It may be promoted to `[x]` only after an independent ChatGPT audit confirms that the real Godot scene-interaction regression is repeatable from the committed clean checkout without recreating deleted temporary runner files.
