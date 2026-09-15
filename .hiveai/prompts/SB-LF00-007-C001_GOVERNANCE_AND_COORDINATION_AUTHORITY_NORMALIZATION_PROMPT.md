# SB-LF00-007-C001 — Governance & Coordination Authority Normalization
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Authority and owner correction

This prompt incorporates an owner correction made before builder execution.

The current H!veAI architecture is **GitHub TASKS-only tracking**. The H!veAI implementation uses `GITHUB_TASKS_ONLY` and fetches the root `TASKS.md` directly from GitHub. No `.hiveai` tracker/control-plane file is required for project task state.

Therefore, for this repository:

- root uppercase `TASKS.md` is the **only project-management/tracker source of truth**;
- H!veAI may additionally read ordinary GitHub repository metadata such as remote HEAD/latest commit, but no other repository file is a task-state source;
- `.hiveai/prompts/`, `.hiveai/codex-logs/`, and `.hiveai/audits/` are historical/process evidence only and must never be parsed as tracker state;
- `.hiveai/CYCLE_INDEX.md` is obsolete H!veAI tracker/control-plane residue and **must be removed** in this cycle;
- lowercase root `tasks.md` must not exist or be recreated;
- obsolete `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/TASKS.md`, `.hiveai/STATE.json`, `.hiveai/HANDOFF.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/PROJECT_DASHBOARD.md`, `.hiveai/ACTIVE_CYCLES.md`, `.hiveai/ARTIFACT_MAP.md`, and `.hiveai/PROGRESS_SNAPSHOT.md` must not be recreated;
- ChatGPT remains the repository-specific sole writer of live task/status state in root `TASKS.md` and the independent auditor;
- Codex is builder only and must not edit root `TASKS.md` in this cycle.

This owner correction supersedes any older repository wording that treats `CYCLE_INDEX`, lowercase `tasks.md`, or legacy `.hiveai` control-plane files as current tracking authority.

## Required reads before edits

Read completely from GitHub before any implementation/test/documentation edit:

1. root `TASKS.md`;
2. previous strict PASS audit:
   `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF00-008-C001_CLEAN_CHECKOUT_HEADLESS_BOOT_PROOF_STRICT_AUDIT.md`;
3. this complete prompt from its GitHub URL;
4. `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`;
5. `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`;
6. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`;
7. root `README.md`;
8. root `GOVERNANCE.md`;
9. root `AGENTS.md`;
10. root `CLAUDE.md`;
11. current `.hiveai/CYCLE_INDEX.md` only as **deletion input / obsolete state evidence**, never as authority;
12. `level_factory/GOVERNANCE.md` and `level_factory/README.md`;
13. current `.hiveai/` directory tree.

Before any governance/test/documentation edit, create and verify:

`.hiveai/codex-logs/SB-LF00-007-C001_GOVERNANCE_AND_COORDINATION_AUTHORITY_NORMALIZATION_CODEX_LOG.md`

## Mission

Implement only:

`SB-LF00-007 — Establish Factory coordination structure while root TASKS remains sole ledger.`

Normalize the repository to the same simplified tracker model that H!veAI actually uses:

```text
GitHub repository metadata
          +
     root TASKS.md
          |
          v
       H!veAI
```

For project-management state, the only repository file in that model is root `TASKS.md`.

The process/evidence workflow remains:

```text
root TASKS.md  (sole live tracker; ChatGPT-owned here)
      |
      v
.hiveai/prompts/<cycle>.md  (implementation instruction/evidence, not tracker)
      |
      v
Codex builder
      |
      v
.hiveai/codex-logs/<cycle>.md  (builder evidence, not tracker)
      |
      v
ChatGPT strict audit
      |
      v
.hiveai/audits/<cycle>.md  (audit evidence, not tracker)
      |
      v
ChatGPT updates root TASKS.md
```

No cycle index or second live-state file is part of this chain.

## Required corrections

### 1. Delete `.hiveai/CYCLE_INDEX.md`

Delete the tracked file `.hiveai/CYCLE_INDEX.md`.

Reason:

- it is a superseded H!veAI-specific cycle/tracker index;
- its active-cycle state is stale;
- H!veAI does not need it to parse the project;
- keeping a second state/index file invites authority drift;
- historical prompts/logs/audits already preserve cycle evidence directly.

Do **not** migrate its active/current-state block into another tracker file.
Do **not** create a replacement cycle index, dashboard, manifest, event ledger, state JSON, handoff file, or task projection.

Deleting CYCLE_INDEX does not authorize deleting historical `.hiveai/prompts/`, `.hiveai/codex-logs/`, or `.hiveai/audits/` records.

### 2. Normalize root `README.md`

Correct stale statements so README says:

- this is the canonical Level Factory + Content Platform repository;
- root uppercase `TASKS.md` is the sole project-management tracker source;
- H!veAI requires no other repository file for task-state parsing;
- Python Factory Core and the accepted `level_factory/` Godot shell currently exist;
- unfinished roadmap capabilities remain unfinished;
- main-game runtime work belongs to `Sekiph82/Scrubbots` when separately authorized.

Remove lowercase `tasks.md` as canonical authority and obsolete claims that the repository contains no Godot integration.

### 3. Normalize root `GOVERNANCE.md`

Remove obsolete current-authority references to:

- lowercase `tasks.md`;
- `.hiveai/TASKS.md`;
- `.hiveai/EVENTS.jsonl`;
- `.hiveai/PROJECT.json` / `.hiveai/RULES.md`;
- `.hiveai/CYCLE_INDEX.md`;
- any v3 control-plane state as a second tracker.

Required model:

- root `TASKS.md` = sole live tracker;
- ChatGPT = tracker owner + independent auditor;
- Codex = builder only;
- Codex must not change root `TASKS.md` task state in this repository workflow;
- builder logs cannot self-accept work;
- prompts/logs/audits are evidence, not task-state sources.

### 4. Normalize root `AGENTS.md`

Remove mandatory reads or current-state authority for obsolete legacy files, including:

- `.hiveai/RULES.md`;
- `.hiveai/PROJECT.json`;
- `.hiveai/TASKS.md`;
- `.hiveai/EVENTS.jsonl`;
- `.hiveai/CYCLE_INDEX.md`;
- lowercase `tasks.md`.

Builder startup should require only the relevant current sources:

1. repository/branch identity;
2. safe sync of canonical local mirror when instructed;
3. root `TASKS.md` as read-only live task state;
4. supplied authoritative prompt URL;
5. previous strict audit and specific contracts required by that prompt;
6. branch/HEAD/status/stash/worktree checks as relevant;
7. builder log before edits;
8. no sibling-repository substitution;
9. no self-audit or tracker-state mutation.

Preserve valid offline/core/source-art rules.

### 5. Normalize root `CLAUDE.md`

Make it agree with the same model:

- root `TASKS.md` is the sole tracker source;
- builders read it but do not mutate ChatGPT-owned task state;
- no legacy `.hiveai` control-plane files are required;
- no `CYCLE_INDEX` tracker exists after this cycle.

### 6. `level_factory/GOVERNANCE.md`

Change only if required to make it cleanly defer live task status to root `TASKS.md` and root governance. Do not create a local tracker or second control plane.

## H!veAI parser contract that must remain compatible

Root `TASKS.md` already exposes the required literal project-status fields. Do not change the tracker in this builder cycle, but governance must protect this contract:

- `Current Milestone:`
- `Current Sprint:`
- `Current Task:`
- `Current Task Status:`
- `Next Task/Action:` (H!veAI also tolerates `Next Action:` / `Next Task:`, but this repository keeps the canonical field)
- `Required Actor:`

Task rows are root `TASKS.md` Markdown checkbox rows using statuses such as:

- `[x]` complete;
- `[~]` in progress;
- `[!]` blocked;
- `[ ]` backlog/open.

Do not add another parser-facing tracker file.

## Focused governance tests

Add:

`tests/unit/test_sb_lf00_007_governance_authority.py`

It must prove at minimum:

1. root uppercase `TASKS.md` exists;
2. lowercase root `tasks.md` does not exist;
3. `.hiveai/CYCLE_INDEX.md` does not exist after implementation;
4. no legacy tracker/control-plane file exists:
   - `.hiveai/PROJECT.json`
   - `.hiveai/RULES.md`
   - `.hiveai/TASKS.md`
   - `.hiveai/STATE.json`
   - `.hiveai/HANDOFF.md`
   - `.hiveai/EVENTS.jsonl`
   - `.hiveai/PROJECT_DASHBOARD.md`
   - `.hiveai/ACTIVE_CYCLES.md`
   - `.hiveai/ARTIFACT_MAP.md`
   - `.hiveai/PROGRESS_SNAPSHOT.md`;
5. `.hiveai/` contains no current-state tracker file outside evidence families;
6. root README/GOVERNANCE/AGENTS/CLAUDE identify root `TASKS.md` as the sole live/current project tracker source;
7. those control documents do not require `CYCLE_INDEX`, lowercase `tasks.md`, or legacy v3 files;
8. ChatGPT is identified as tracker owner / independent auditor for this repo workflow;
9. builders are prohibited from editing root `TASKS.md` task state;
10. prompts/logs/audits are explicitly non-tracker evidence;
11. root `TASKS.md` contains the six required H!veAI Project Status labels;
12. representative canonical task rows remain parseable in root `TASKS.md`;
13. `level_factory/GOVERNANCE.md` does not create another tracker;
14. previous LF00-001/LF00-002/LF00-006/LF00-008 tests remain green;
15. no product Python/GDScript implementation changes occur.

## Allowed scope

Expected changes are limited to:

- delete `.hiveai/CYCLE_INDEX.md`;
- `README.md`;
- `GOVERNANCE.md`;
- `AGENTS.md`;
- `CLAUDE.md`;
- `level_factory/GOVERNANCE.md` only if needed;
- `tests/unit/test_sb_lf00_007_governance_authority.py`;
- required builder log.

Do not edit root `TASKS.md`.
Do not modify Factory algorithms, `src/` product code, Godot scenes/project source, provider code, dependencies, Content Platform implementation, or main-game repository files.

## Explicitly out of scope

Do not begin:

- M01+ implementation/migration;
- M03 solver;
- M06 Factory Studio implementation;
- Perchance/Magnific/PixelLab integration;
- Content Platform implementation;
- main-game runtime implementation;
- secret-management implementation;
- CI redesign.

Do not call providers or external generation services.

## Required verification

Run and record:

1. focused `SB-LF00-007` governance tests;
2. prior LF00-001 suite;
3. prior LF00-002 suite;
4. prior LF00-006 suite;
5. prior LF00-008 suite;
6. full `python -m pytest -q`;
7. `python -m compileall -q src tests`;
8. package import smoke;
9. module CLI help and installed CLI help if available;
10. Godot headless/editor smoke against `level_factory/`;
11. `git diff --check`;
12. `git diff -- TASKS.md` must be empty;
13. prove `.hiveai/CYCLE_INDEX.md` is deleted;
14. prove none of the legacy H!veAI tracker/control-plane files exist;
15. prove current governance docs contain no live-authority references to those files;
16. prove no product Python/GDScript files changed;
17. main-game no-access/no-write statement;
18. provider/network/credential no-use statement.

Record any failed command/test and its correction truthfully.

## Builder log requirements

H1 exactly:

`# SB-LF00-007-C001 — Governance & Coordination Authority Normalization`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- exact starting timestamp;
- canonical repo/local root/branch/remote;
- starting HEAD / `origin/main` and divergence;
- initial status/stash/worktree state;
- authorities read;
- confirmation that `.hiveai/CYCLE_INDEX.md` existed at start and is being removed as obsolete tracker residue;
- confirmation lowercase root `tasks.md` is absent;
- inventory of stale legacy H!veAI authority references;
- exact files changed/deleted and rationale;
- focused governance tests;
- prior LF00 regression tests;
- full regression;
- compile/import/CLI/Godot checks;
- proof `TASKS.md` was not edited;
- proof no replacement tracker/control-plane file was created;
- proof no product Python/GDScript changed;
- dependency/license changes, expected none;
- main-game no-access/no-write;
- provider/network/credential no-use;
- implementation commit SHA/push;
- final builder-log publication SHA/push;
- final HEAD / `origin/main` equality.

## GitHub handoff requirement

The finalized builder log must be committed and pushed to `main`.

At final handoff provide:

1. full GitHub URL to the finalized builder log;
2. implementation commit SHA;
3. final publication commit SHA.

Do not use a local Windows path as the primary handoff.
Do not paste the full log body unless asked.
Stop for independent ChatGPT strict audit.

## Acceptance criteria

Eligible for PASS only if all are true:

- [ ] root `TASKS.md` remains the only project-management tracker source;
- [ ] `.hiveai/CYCLE_INDEX.md` is deleted;
- [ ] no lowercase root `tasks.md` exists;
- [ ] no legacy `.hiveai` control-plane tracker files exist or are recreated;
- [ ] README/GOVERNANCE/AGENTS/CLAUDE consistently use the TASKS-only model;
- [ ] ChatGPT/Codex ownership is unambiguous;
- [ ] prompts/logs/audits remain evidence and are not tracker sources;
- [ ] root `TASKS.md` parser labels remain present and builder-untouched;
- [ ] focused governance tests pass;
- [ ] prior LF00 focused suites pass;
- [ ] full regression passes by builder evidence;
- [ ] Godot smoke still passes;
- [ ] no product Python/GDScript implementation changed;
- [ ] no main-game write/provider call/credential use occurred;
- [ ] finalized builder log is pushed and handed off by full GitHub URL;
- [ ] Codex stops for independent audit.