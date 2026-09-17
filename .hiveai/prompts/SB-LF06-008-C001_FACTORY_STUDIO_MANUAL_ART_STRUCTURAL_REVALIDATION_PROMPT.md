# SB-LF06-008-C001 — Factory Studio Manual Artwork Structural Revalidation

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF06-008 — Revalidate after manual changes. [PARTIAL]`

Implement bounded revalidation for the existing LF06-006 **memory-only DIRTY artwork working copy**.

This task is **not** permission to implement full gameplay validation.

Current repository truth:
- canonical Python `QualityPolicy` + `evaluate_grid()` can perform deterministic structural/art QA;
- canonical `read_bundle()` can fail-closed validate the immutable source bundle;
- gameplay solver authority from M03 does not exist yet;
- measured Difficulty V1 authority from M04 does not exist yet;
- unified M05 validation does not exist yet;
- LF06-003 `Validate` action must remain unavailable.

The correct product is therefore a **STRUCTURAL ART QA revalidation** surface over manual artwork edits, explicitly labeled as partial/not-full validation.

Create the matching builder log before product edits:

`.hiveai/codex-logs/SB-LF06-008-C001_FACTORY_STUDIO_MANUAL_ART_STRUCTURAL_REVALIDATION_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read completely before edits:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-007-C001-R01_WRONG_TASK_EXECUTION_RECOVERY_STRICT_AUDIT.md`;
- `.hiveai/audit-criteria/SB-LF06-008-C001_MANUAL_ART_STRUCTURAL_REVALIDATION_AUDIT_CRITERIA.md`;
- accepted LF06-003..007 Studio scripts/tests;
- `level_factory/scripts/factory_core_gateway.gd`;
- `level_factory/scripts/factory_core_launcher.py`;
- `level_factory/scripts/factory_studio_art_editor.gd`;
- `src/scrubbots_pixel_factory/output/bundle.py`;
- `src/scrubbots_pixel_factory/quality/core.py` and quality exports;
- canonical logical-grid hash implementation/export;
- relevant output/quality contract tests;
- Factory README/governance/boundary tests.

## 1. Preserve existing action truth

Do **not** enable the existing LF06-003 `Validate` action.

It must remain:

`UNAVAILABLE — no standalone canonical validation capability is connected.`

This task adds a separate, narrowly named manual-art revalidation path such as:

`Revalidate manual artwork`

The operator-facing scope must visibly say:

`STRUCTURAL ART QA ONLY — NOT FULL GAMEPLAY VALIDATION`

Do not call structural ACCEPT simply `VALID`.

## 2. Source of manual edit truth

Revalidation is allowed only against the actual LF06-006 editor working copy.

Prerequisites:
- editor source exists and is safely loaded;
- editor state is `DIRTY`;
- `dirty_cell_count > 0`;
- working dimensions equal source dimensions;
- every working logical pixel maps exactly to C01..C16;
- source candidate identity and source bundle path come from the editor's retained source state, not from the latest unrelated action.

If the editor is CLEAN/EMPTY/ERROR, revalidation must be disabled or return truthful NOT_REQUIRED/UNAVAILABLE/ERROR.

A CLEAN source must never be presented as a manually revalidated edit.

## 3. Read-only editor additions are allowed

You may add bounded read-only editor APIs needed for transport, for example:
- working logical C-ID snapshot;
- source logical C-ID snapshot;
- exact working logical-grid hash helper input;
- a narrow change signal so revalidation evidence can become STALE after later edits.

Do not add persistence or write the working edit to the canonical bundle.

The editor must remain non-destructive and memory-only.

## 4. Canonical source-bundle authority

The Python side must fail-closed validate the editor's immutable source bundle through existing canonical bundle authority, preferably `read_bundle()`.

Do not trust only GDScript metadata parsing.

The revalidation source must bind to:
- source candidate ID;
- source grid hash;
- width/height;
- source metadata/bundle identity;
- exact quality policy already recorded in the source bundle.

Any mismatch between editor source identity and canonical bundle identity must fail closed.

## 5. Exact source quality-policy reuse

This is mandatory.

Read the exact policy from the source bundle's canonical quality report/binding and reconstruct it through canonical `QualityPolicy` semantics.

Then run canonical `evaluate_grid()` over the current working logical cells.

Forbidden:
- new/default policy instead of the recorded source policy;
- current draft difficulty as policy authority;
- candidate presentation label as policy/identity;
- board-size-based difficulty inference;
- threshold duplication in GDScript;
- manual reimplementation of quality rules.

## 6. Narrow Python bridge

Do not modify canonical Python Core semantics under `src/` merely to make Studio convenient unless a genuine existing bug is independently proven.

Preferred architecture:
- preserve the existing canonical CLI delegation for normal launcher commands;
- add one fixed Studio-internal launcher operation, e.g. `studio-revalidate-art`, only if needed;
- that operation may import and invoke existing canonical `read_bundle`, `QualityPolicy`, `evaluate_grid`, and canonical logical-grid hashing;
- it is transport/orchestration, not a second validator.

If extending `factory_core_launcher.py`, preserve existing `--help`, Generate and Reproduce behavior exactly.

The operation must accept only a bounded request schema. No arbitrary Python/module/function/command fields.

Because a 59×59 grid can exceed safe Windows command-line payload size, do not serialize all cells into a giant shell/argv string. A bounded transient JSON request file is acceptable.

Transient request rules:
- safe project cache/temp or OS temp location;
- deterministic cleanup on success/failure where practical;
- never treated as canonical content;
- no secrets;
- no persistent revision artifact.

## 7. Process safety

Use `OS.execute(executable, PackedStringArray(args), ...)` or existing equivalent only.

Never use:
- `cmd /c`;
- PowerShell;
- Bash;
- shell interpolation;
- user-supplied executable or command names.

Keep stdout/stderr/exit code truthful and bounded.

Missing Python/Core must be UNAVAILABLE/ERROR, never fake success.

## 8. Revalidation result contract

Return a structured Studio result containing at least:
- operation: manual artwork structural revalidation;
- scope: `STRUCTURAL_ART_QA_ONLY` or equivalent;
- source candidate ID;
- source grid hash;
- working grid hash using the existing canonical logical-grid hash contract;
- width/height;
- dirty-cell count;
- quality schema/version;
- source quality-policy version/identity;
- accepted/rejected structural decision;
- rejection codes;
- safe diagnostic on failure.

If useful, include bounded canonical structural metrics, but do not relabel them as gameplay difficulty/load/risk.

Do not write this result into source `metadata.json`.

## 9. Studio revalidation component

Prefer a dedicated component such as:

`level_factory/scripts/factory_studio_art_revalidation.gd`

It should consume references to the existing editor and gateway, not create a second editor or truth store.

Suggested state model:
- `NOT_REQUIRED` — working copy equals canonical source;
- `AVAILABLE` — DIRTY edit can be checked;
- `RUNNING`;
- `RESULT` with qualified structural ACCEPT/REJECT;
- `ERROR` / `UNAVAILABLE`;
- `STALE` — working copy changed after the recorded result.

Display prominently:
- `STRUCTURAL ART QA ONLY`;
- `NOT FULL GAMEPLAY VALIDATION`;
- solver unavailable pending M03;
- measured difficulty unavailable pending M04;
- unified validation unavailable pending M05;
- `QA PASS != OWNER ACCEPT`;
- no production promotion occurs here.

## 10. Staleness is mandatory

A revalidation result is valid only for the exact working-grid hash it evaluated.

After any later pixel edit that changes the working grid:
- the prior result must immediately or deterministically become `STALE`;
- stale ACCEPT must never remain presented as current ACCEPT.

If the working copy is reset/restored to source:
- manual revalidation becomes NOT_REQUIRED;
- prior dirty-edit result is no longer current.

If the operator returns exactly to a previously validated dirty grid, do not silently resurrect old evidence unless the implementation explicitly rechecks identity and the audit criteria are still satisfied. Simpler behavior is to require revalidation again.

## 11. Revalidation must not mutate editor state

Running revalidation:
- must not clear DIRTY state;
- must not replace working pixels;
- must not load latest action over a retained dirty edit;
- must not change source candidate identity;
- must not change canonical preview/evidence identity.

Structural ACCEPT means only that the exact current working grid passed the current canonical structural/art QA policy.

It does not mean:
- gameplay solved;
- measured difficulty valid;
- full QA complete;
- owner accepted;
- production ready.

## 12. Source bytes are immutable

Committed runtime evidence must capture and compare source bytes before/after revalidation for at least:
- `artwork.png`;
- `artwork.json`;
- `metadata.json`.

All must remain byte-identical.

Do not persist an edited candidate bundle in this task.

## 13. Required tests

### A. Focused static/contract tests
Prove:
- new component/bridge is bounded;
- existing `Validate` action remains unavailable;
- no GDScript quality thresholds or duplicated evaluator logic;
- exact source policy is reused;
- no arbitrary shell/command path;
- no canonical bundle write path;
- no solver/difficulty/load/risk fabrication;
- no persistence/revision-history/promotion scope.

### B. Python bridge tests
If a launcher operation is added, directly test it with real canonical bundles and working grids.

Prove:
- malformed transport request fails closed;
- source bundle mismatch/corruption fails closed;
- exact source policy is used;
- working hash is canonical;
- canonical `evaluate_grid()` result and returned Studio result agree exactly;
- nonzero/error paths remain truthful.

### C. Real Godot integration
A committed headless Godot runner must exercise the real Studio/editor/gateway/Python boundary.

At minimum prove:
1. generate/load a real canonical source artwork;
2. initial editor CLEAN -> revalidation NOT_REQUIRED;
3. make a real C01..C16 edit -> editor DIRTY;
4. run real structural revalidation through Python canonical quality code;
5. result is bound to source candidate + exact working grid hash;
6. editor remains DIRTY and source bytes unchanged;
7. construct a deterministic bad manual grid and receive real structural REJECT with canonical rejection code(s);
8. make another edit after a recorded result -> result becomes STALE;
9. reset to source -> NOT_REQUIRED and exact source pixels restored;
10. canonical preview/evidence identities remain unchanged;
11. LF06-007 puzzle-config gate remains truthful UNAVAILABLE.

Also cover a deterministic structural ACCEPT path if practical. If an accepted dirty mutation is generated programmatically, the search must be bounded and test-only; do not add heuristic product behavior.

## 14. Preserve previous accepted work

Must remain green:
- LF06-001 workspace;
- LF06-002 target controls/runtime suite;
- LF06-003 Generate/Reproduce bridge and Validate=UNAVAILABLE;
- LF06-004 crisp canonical preview;
- LF06-005 canonical evidence panel;
- LF06-006 non-destructive editor;
- LF06-007 puzzle-config UNAVAILABLE gate;
- LF01 dimension contracts;
- palette/source immutability contracts.

## 15. Forbidden scope

Do not implement:
- M03 gameplay solver;
- M04 Difficulty V1;
- full M05 unified validator;
- gameplay load/risk models;
- owner acceptance;
- revision-history persistence;
- durable manual-edit candidate save/export;
- production promotion;
- Dashboard/Import/Library/provider/Content Platform/main-game features;
- SB-LF06-009+;
- any SB-LFX task.

Do not modify root `TASKS.md`.

## 16. Verification

Run and record:
- focused LF06-008 tests;
- retained LF06-001..007 tests;
- relevant quality/output/hash contract tests;
- committed real Godot revalidation integration;
- real Python bridge integration if applicable;
- full `python -m pytest -q`;
- `python -m compileall -q src tests level_factory/scripts/factory_core_launcher.py`;
- `godot --headless --path level_factory --quit`;
- `git diff --check`;
- `git diff -- TASKS.md`;
- exact changed-file/scope review.

Record all failed attempts and corrections honestly.

## Acceptance criteria

PASS eligibility requires all of the following:
- real DIRTY working-copy revalidation crosses into canonical Python structural QA;
- canonical source bundle is validated fail-closed;
- exact source quality policy is reused;
- working-grid hash binds the result;
- later edits stale the result;
- source bytes remain immutable;
- editor remains memory-only and non-destructive;
- structural ACCEPT/REJECT is clearly scoped and never presented as full validation;
- existing Validate action stays unavailable;
- missing M03/M04/M05 authority remains explicit;
- no persistence/promotion scope creep;
- retained regressions are green;
- root `TASKS.md` untouched by builder;
- implementation commit(s) are followed by exactly one terminal log-only publication commit.

## Publication

Push implementation/tests/finalized builder log to `main`.

At completion give only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF06-008-C001_FACTORY_STUDIO_MANUAL_ART_STRUCTURAL_REVALIDATION_CODEX_LOG.md`;
2. final implementation commit SHA;
3. actual terminal log-only publication commit SHA.

Then stop for independent ChatGPT strict audit.