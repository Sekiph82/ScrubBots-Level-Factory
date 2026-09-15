# SB-LF00-007-C001 — Governance & Coordination Authority Normalization
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Owner-corrected architecture

This prompt contains the owner's final correction made before builder execution.

H!veAI uses **GitHub TASKS-only project tracking**:

- GitHub repository metadata supplies repository/branch/HEAD/latest-commit context;
- root uppercase `TASKS.md` is the **only repository file used as project-management/task-state truth**;
- H!veAI must not need `.hiveai` state files, cycle indexes, prompts, logs, audits, README, AGENTS, CLAUDE, or other docs to determine task state;
- `.hiveai/prompts/`, `.hiveai/codex-logs/`, and `.hiveai/audits/` are process/evidence archives only;
- `.hiveai/CYCLE_INDEX.md` is obsolete tracker/control-plane residue and must be deleted;
- legacy `.hiveai` tracker files must remain absent;
- lowercase root `tasks.md` must remain absent.

The real H!veAI parser fetches `/TASKS.md` directly and recognizes the Project Status fields and Markdown checkbox rows. This cycle must normalize this repository to that actual parser contract.

## Repository-specific ownership rule

Normally, ChatGPT is the sole writer of root `TASKS.md` task state and Codex must not edit it.

**One-time explicit exception for this cycle:** Codex is authorized to perform only a mechanical parser-format normalization of task rows in root `TASKS.md`, exactly as specified below. Codex must not change any task's checkbox state, task identity, title semantics, current milestone/sprint/task/status, next action, required actor, counts, denominators, ordering, or roadmap meaning.

After this cycle, root `TASKS.md` returns to ChatGPT-only task-state ownership.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. previous strict PASS audit:
   `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF00-008-C001_CLEAN_CHECKOUT_HEADLESS_BOOT_PROOF_STRICT_AUDIT.md`;
3. this complete prompt from its GitHub URL;
4. `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`;
5. `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`;
6. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`;
7. root `README.md`, `GOVERNANCE.md`, `AGENTS.md`, `CLAUDE.md`;
8. current `.hiveai/CYCLE_INDEX.md` only as obsolete-state/deletion input, never as authority;
9. `level_factory/GOVERNANCE.md` and `level_factory/README.md`;
10. current `.hiveai/` tree.

Before any edit create and verify:

`.hiveai/codex-logs/SB-LF00-007-C001_GOVERNANCE_AND_COORDINATION_AUTHORITY_NORMALIZATION_CODEX_LOG.md`

## Mission

Implement only:

`SB-LF00-007 — Establish Factory coordination structure while root TASKS remains sole ledger.`

Final tracking model:

```text
GitHub repository metadata
          +
     root TASKS.md
          |
          v
       H!veAI
```

Process evidence remains separate:

```text
TASKS.md -> ChatGPT prompt -> Codex -> builder log -> ChatGPT audit -> TASKS.md
```

`prompts/`, `codex-logs/`, and `audits/` are not tracker inputs. There is no `CYCLE_INDEX` or second state file.

## 1. Delete obsolete tracker residue

Delete:

`.hiveai/CYCLE_INDEX.md`

Do not replace it with another index, manifest, dashboard, event ledger, JSON state file, handoff file, progress snapshot, or active-cycle file.

Historical cycle evidence remains available directly in used prompts, builder logs, audits, migration documents, Git history, and `reference/audits/`. Do not rewrite those historical records.

The following legacy tracker/control-plane files must remain absent and must not be recreated:

- `.hiveai/PROJECT.json`
- `.hiveai/RULES.md`
- `.hiveai/TASKS.md`
- `.hiveai/STATE.json`
- `.hiveai/HANDOFF.md`
- `.hiveai/EVENTS.jsonl`
- `.hiveai/PROJECT_DASHBOARD.md`
- `.hiveai/ACTIVE_CYCLES.md`
- `.hiveai/ARTIFACT_MAP.md`
- `.hiveai/PROGRESS_SNAPSHOT.md`
- root lowercase `tasks.md`

## 2. Normalize root TASKS.md for the real H!veAI parser

### Project Status contract

Preserve these literal fields near the top:

- `Current Milestone:`
- `Current Sprint:`
- `Current Task:`
- `Current Task Status:`
- `Next Task/Action:`
- `Required Actor:`

Do not change their current semantic values in this cycle.

### Task-row parser contract

H!veAI treats text immediately after the checkbox and before the first `—` as the task ID.

Therefore every actual task row must follow:

```markdown
- [STATUS] TASK-ID — Task title [OPTIONAL_METADATA_TAGS]
```

Allowed checkbox status characters already used by this repo:

- `[x]` complete
- `[~]` in progress
- `[!]` blocked
- `[ ]` open/backlog

Current parser-unsafe rows such as:

```markdown
- [~] [MIGRATION] SB-LF00-007 — Establish ...
- [ ] [PARTIAL] SB-LF02-001 — Implement ...
- [ ] [GAME_RUNTIME] SB-CP04-001 — Implement ...
```

must be mechanically rewritten to:

```markdown
- [~] SB-LF00-007 — Establish ... [MIGRATION]
- [ ] SB-LF02-001 — Implement ... [PARTIAL]
- [ ] SB-CP04-001 — Implement ... [GAME_RUNTIME]
```

Apply the same rule to `[DESIGN_GATE]`, `[OWNER_GATE]`, or any other metadata tag that currently appears before the true task ID.

### Absolute preservation rules for TASKS.md

This format-only edit MUST preserve exactly:

- every checkbox state;
- every canonical task ID;
- every task's title/meaning;
- every metadata tag;
- task ordering;
- 224 canonical LF/CP source requirements;
- 3 extension tasks;
- unified denominator 227;
- all classification counts;
- all completion counts/percentages already stated;
- current milestone/sprint/task/status;
- next action;
- required actor;
- historical evidence prose.

Do not mark anything complete/open/blocked/in-progress differently.
Do not add or remove tasks.
Do not renumber tasks.
Do not duplicate rows.

After normalization, the `Current Task:` ID must exactly equal the parsed ID of the single `[~]` active task row.

## 3. Normalize README.md

Correct stale wording so README states:

- repository is the canonical Level Factory + Content Platform repository;
- root `TASKS.md` is the sole project-management tracker file;
- H!veAI task tracking requires no other repository file;
- Python Factory Core and accepted independent `level_factory/` Godot shell exist;
- unfinished roadmap capabilities remain unfinished;
- main-game runtime belongs in `Sekiph82/Scrubbots` when separately authorized.

Remove lowercase `tasks.md` authority and obsolete “no Godot integration” wording.

## 4. Normalize GOVERNANCE.md

Remove current-authority references to lowercase `tasks.md`, legacy `.hiveai` tracker files, and `CYCLE_INDEX`.

Final model:

- root `TASKS.md` = sole live tracker;
- ChatGPT = planner/tracker owner/independent auditor;
- Codex = builder only;
- except for the one-time format-only authorization in this cycle, builders do not mutate task state;
- builder logs are evidence, not acceptance;
- prompts/logs/audits are evidence archives, not task-state sources.

## 5. Normalize AGENTS.md

Remove mandatory-current-state reads of:

- `.hiveai/RULES.md`
- `.hiveai/PROJECT.json`
- `.hiveai/TASKS.md`
- `.hiveai/EVENTS.jsonl`
- `.hiveai/CYCLE_INDEX.md`
- lowercase `tasks.md`

Normalized builder startup:

1. verify exact repo/branch;
2. safely sync only canonical mirror when instructed;
3. read root `TASKS.md` as current tracker;
4. read supplied authoritative prompt URL;
5. read previous audit/specific contracts required by prompt;
6. inspect branch/HEAD/origin/status/stash/worktree as relevant;
7. create matching builder log before edits;
8. never substitute/search sibling repo for task authority;
9. never self-audit or self-accept.

Preserve valid offline/core/source-art rules.

## 6. Normalize CLAUDE.md

Make it agree with the same TASKS-only model and remove any instruction to maintain legacy `.hiveai` tracker files or `CYCLE_INDEX`.

After this governance cycle, builders read root `TASKS.md`; ChatGPT owns subsequent task-state edits unless the owner explicitly changes that rule later.

## 7. level_factory/GOVERNANCE.md

Change only if required to defer cleanly to root `TASKS.md`/root governance. It must not define another tracker.

## 8. Focused tests

Add:

`tests/unit/test_sb_lf00_007_governance_authority.py`

It must prove at minimum:

1. root `TASKS.md` exists;
2. lowercase root `tasks.md` does not exist;
3. `.hiveai/CYCLE_INDEX.md` does not exist;
4. all listed legacy `.hiveai` tracker/control-plane files remain absent;
5. `.hiveai/` has no second live/current project-state tracker;
6. README/GOVERNANCE/AGENTS/CLAUDE identify root `TASKS.md` as sole live tracker;
7. those docs do not require `CYCLE_INDEX`, lowercase `tasks.md`, or old v3 files as current authority;
8. prompts/logs/audits are explicitly non-tracker evidence;
9. root `TASKS.md` contains all six required H!veAI Project Status fields;
10. every recognized checkbox task row has a true task ID immediately after checkbox, with no leading `[PARTIAL]`, `[MIGRATION]`, `[GAME_RUNTIME]`, `[DESIGN_GATE]`, `[OWNER_GATE]`, or other metadata tag;
11. metadata tags are retained after the title where applicable;
12. `Current Task:` ID matches the active `[~]` task-row ID exactly;
13. there is exactly one active `[~]` task row for the current cycle;
14. canonical task IDs are unique;
15. task counts/classification counts and checkbox states are unchanged from the pre-edit tracker;
16. canonical source denominator remains 224 and unified denominator remains 227;
17. `level_factory/GOVERNANCE.md` creates no second tracker;
18. previous LF00-001/LF00-002/LF00-006/LF00-008 focused suites remain green;
19. no product Python/GDScript implementation changes occur.

For the format-preservation test, record a pre-edit mechanical inventory in the builder log before changing TASKS.md, including counts by checkbox state and metadata tag. Compare the post-edit tracker against that inventory.

## Allowed scope

Allowed changes:

- delete `.hiveai/CYCLE_INDEX.md`;
- format-only parser normalization of root `TASKS.md` under the strict preservation rules above;
- `README.md`;
- `GOVERNANCE.md`;
- `AGENTS.md`;
- `CLAUDE.md`;
- `level_factory/GOVERNANCE.md` only if needed;
- `tests/unit/test_sb_lf00_007_governance_authority.py`;
- required builder log.

Forbidden:

- changing task state or roadmap meaning;
- product `src/` code changes;
- Godot scene/project changes;
- provider code/dependency changes;
- main-game repository changes;
- M01+/M03/M06/Content Platform/provider implementation work.

Do not call Magnific, PixelLab, Perchance, or any generation/provider/network service.

## Required verification

Run and record:

1. pre-edit TASKS inventory: total recognized task rows, checkbox-state counts, metadata-tag counts, unique IDs, active row;
2. focused SB-LF00-007 governance/parser tests;
3. post-edit TASKS inventory and exact comparison to pre-edit state except metadata tag placement;
4. prior LF00-001 suite;
5. prior LF00-002 suite;
6. prior LF00-006 suite;
7. prior LF00-008 suite;
8. full `python -m pytest -q`;
9. `python -m compileall -q src tests`;
10. package import smoke;
11. module CLI help and installed CLI help if available;
12. Godot headless/editor smoke against `level_factory/`;
13. `git diff --check`;
14. diff inspection proving TASKS changes are only metadata-tag relocation/parser-format normalization and no status/content loss;
15. prove `.hiveai/CYCLE_INDEX.md` deleted;
16. prove no legacy tracker/control-plane file exists;
17. prove no product Python/GDScript changed;
18. main-game no-access/no-write;
19. provider/network/credential no-use.

Record all failed commands/tests and corrections truthfully.

## Builder log requirements

H1 exactly:

`# SB-LF00-007-C001 — Governance & Coordination Authority Normalization`

Immediately below:

`Document role: CODEX BUILDER LOG`

Log chronologically:

- exact starting timestamp;
- canonical repo/local root/branch/remote;
- starting HEAD/origin/main/divergence/status/stash/worktrees;
- authorities read;
- confirmation CYCLE_INDEX existed at start and is obsolete;
- confirmation lowercase `tasks.md` absent;
- pre-edit TASKS parser inventory;
- exact TASKS mechanical transformation rule;
- proof all states/counts/tags/IDs were preserved;
- governance files changed and rationale;
- CYCLE_INDEX deletion;
- focused tests and failures/corrections;
- prior LF00 regressions;
- full regression;
- compile/import/CLI/Godot checks;
- proof no replacement tracker file created;
- proof no product code changed;
- dependency/license changes, expected none;
- main-game no-access/no-write;
- provider/network/credential no-use;
- implementation commit SHA/push;
- final builder-log publication SHA/push;
- final HEAD == origin/main.

## GitHub handoff

Push implementation/tests/finalized builder log to `main`.

At final handoff provide:

1. full GitHub URL to finalized builder log;
2. implementation commit SHA;
3. final publication commit SHA.

Do not provide local log path as primary handoff.
Do not paste full log body unless asked.
Stop for independent ChatGPT strict audit.

## Acceptance criteria

PASS eligibility requires all of the following:

- [ ] root `TASKS.md` is the only project-management tracker source;
- [ ] `.hiveai/CYCLE_INDEX.md` is deleted;
- [ ] no lowercase root `tasks.md`;
- [ ] no legacy `.hiveai` tracking/control-plane files;
- [ ] all TASKS task rows are parser-safe with true ID immediately after checkbox;
- [ ] metadata tags are preserved after titles;
- [ ] task states/counts/IDs/order/meaning are unchanged;
- [ ] current-task header ID matches active row ID;
- [ ] canonical denominator remains 224 and unified denominator 227;
- [ ] governance docs consistently describe TASKS-only tracking;
- [ ] prompts/logs/audits are non-tracker evidence;
- [ ] focused tests pass;
- [ ] prior LF00 tests pass;
- [ ] full regression passes by builder evidence;
- [ ] Godot smoke passes;
- [ ] no product code/main-game/provider/credential changes;
- [ ] final builder log is pushed and handed off by full GitHub URL;
- [ ] Codex stops for independent audit.