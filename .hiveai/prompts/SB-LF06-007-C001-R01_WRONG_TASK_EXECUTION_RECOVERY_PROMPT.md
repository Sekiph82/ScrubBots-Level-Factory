# SB-LF06-007-C001-R01 — Wrong-Task Execution Recovery

Document role: CODEX REMEDIATION / RECOVERY PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Recover from the wrong-task execution recorded by:

`.hiveai/audits/SB-LF06-007-C001_WRONG_TASK_EXECUTION_STRICT_AUDIT.md`

Then execute the actual active task:

`SB-LF06-007 — Approved puzzle-config edits only.`

Do not modify root `TASKS.md`.

Create the recovery builder log before product edits:

`.hiveai/codex-logs/SB-LF06-007-C001-R01_WRONG_TASK_EXECUTION_RECOVERY_CODEX_LOG.md`

## 1. Synchronize and establish exact baseline

Synchronize only:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

with GitHub `main` from:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Read completely:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-007-C001_WRONG_TASK_EXECUTION_STRICT_AUDIT.md`;
- `.hiveai/prompts/SB-LF06-007-C001_FACTORY_STUDIO_APPROVED_PUZZLE_CONFIG_EDIT_GATE_PROMPT.md`;
- LF06-006 closing audit;
- current Studio scripts/tests;
- canonical Python request/result/output contracts;
- any actual LevelData/puzzle/config contracts in this repository.

## 2. Repair the wrong-task product/test changes without rewriting history

The wrong execution commits are historical evidence and must remain in Git history. Do not force-push, rewrite, delete or edit their log.

Restore these three files to their exact contents from commit:

`a35b73327f83f5b28d5e03d66f58db750cf19eb4`

Files:
- `level_factory/scripts/factory_studio_evidence_panel.gd`
- `level_factory/tests/factory_studio_action_integration_suite.gd`
- `tests/unit/test_sb_lf06_005_r01_fail_closed_metadata_gate.py`

Do NOT delete or rewrite:

`.hiveai/codex-logs/SB-LF06-005-C001-R01_FAIL_CLOSED_METADATA_PRESENTATION_GATE_REEXECUTION_CODEX_LOG.md`

That file remains durable wrong-task process evidence.

After restoration, prove with Git diff/content comparison that the three files exactly match their `a35b733...` versions before beginning LF06-007 product work.

## 3. Execute the real SB-LF06-007 contract-discovery gate

Follow the original authoritative prompt exactly:

`.hiveai/prompts/SB-LF06-007-C001_FACTORY_STUDIO_APPROVED_PUZZLE_CONFIG_EDIT_GATE_PROMPT.md`

The repository currently has an authoritative GenerationRequest contract. That is not automatically a puzzle/gameplay-config edit contract.

Search the canonical repository for a current authoritative puzzle/level configuration schema and explicit manual-editability rules.

Only fields that are both:
1. canonical; and
2. explicitly approved/safe for manual Studio editing
may become editable.

Forbidden:
- relabeling GenerationRequest fields as puzzle config;
- inventing gameplay mechanics or config keys;
- arbitrary JSON/dictionary editor;
- treating request difficulty as measured difficulty;
- using WFC options as gameplay solver configuration;
- turning artwork pixels into puzzle-config values.

## 4. Required branch behavior

### If approved editable puzzle-config fields exist

Implement only those exact fields using a memory-only working copy over a real canonical successful source. Preserve source bytes. Enforce exact canonical types/enums/ranges. CLEAN/DIRTY must derive from exact source-vs-working equality. Unknown/unsupported fields fail closed. State remains UNVALIDATED pending SB-LF06-008.

### If no approved editable puzzle-config fields exist

This is a valid and expected outcome.

Implement a dedicated Studio component/surface that truthfully reports:

`UNAVAILABLE — no approved canonical puzzle-config edit contract`

Required:
- no editable controls;
- no fake source config;
- no synthesis from GenerationRequest/draft controls;
- clear dependency explanation;
- deterministic snapshot/runtime evidence;
- retained LF06-001..006 behavior unchanged.

Do not mark this state ERROR merely because the contract does not exist. UNAVAILABLE is the correct dependency state.

## 5. Preserve accepted boundaries

Preserve all accepted LF06-001..006 behavior:
- canonical Generate/Reproduce bridge;
- crisp canonical preview;
- canonical evidence panel at the accepted pre-wrong-execution state;
- memory-only LF06-006 pixel editor;
- immutable source bytes;
- explicit UNVALIDATED edit truth;
- QA PASS != OWNER ACCEPT;
- no auto-promotion.

Do not implement:
- SB-LF06-008+;
- solver M03;
- measured Difficulty V1 M04;
- M05 unified revalidation;
- persistence/revision history;
- owner acceptance/promotion;
- Dashboard/Import/Library/providers;
- Content Platform;
- main-game runtime;
- any SB-LFX task.

## 6. Required tests

At minimum:
- focused LF06-007 tests;
- retained LF06-001..006 regressions;
- real committed Godot runtime/integration evidence for the applicable branch;
- tests proving no GenerationRequest-to-puzzle-config conflation;
- tests proving no arbitrary config/JSON editing;
- tests proving no source writes;
- full `python -m pytest -q`;
- compileall;
- Godot headless boot;
- `git diff --check`;
- changed-file/scope review;
- explicit proof root `TASKS.md` unchanged by builder.

If the outcome is UNAVAILABLE, runtime/static tests must prove the component has no mutation path and no editable puzzle-config fields.

Record every failed command and correction truthfully.

## 7. Acceptance criteria

PASS eligibility requires all of the following:
- [ ] wrong-task product/test changes are restored exactly to `a35b733...` baseline while wrong-task log remains preserved;
- [ ] actual SB-LF06-007 contract discovery is performed;
- [ ] no puzzle/config semantics are invented;
- [ ] only explicitly approved fields are editable, OR truthful UNAVAILABLE is implemented when none exist;
- [ ] GenerationRequest is not relabeled as puzzle config;
- [ ] canonical source truth remains immutable;
- [ ] any manual config edit state is memory-only and UNVALIDATED;
- [ ] LF06-001..006 retained behavior remains green;
- [ ] root `TASKS.md` unchanged;
- [ ] no forbidden scope creep;
- [ ] implementation/recovery commit(s) are followed by exactly one terminal log-only publication commit.

## 8. Publication

Push recovery + actual LF06-007 implementation/tests to GitHub `main`.

At completion give the user only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF06-007-C001-R01_WRONG_TASK_EXECUTION_RECOVERY_CODEX_LOG.md`;
2. final recovery/implementation commit SHA;
3. actual terminal log-only publication commit SHA.

Then stop for independent ChatGPT strict audit.
