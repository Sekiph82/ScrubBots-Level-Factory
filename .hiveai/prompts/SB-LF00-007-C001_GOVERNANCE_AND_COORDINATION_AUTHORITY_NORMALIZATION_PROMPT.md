# SB-LF00-007-C001 — Governance & Coordination Authority Normalization
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Authority and current-state precedence

Read completely from GitHub before any implementation/test/documentation edit:

1. root `TASKS.md`;
2. previous strict PASS audit:
   `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF00-008-C001_CLEAN_CHECKOUT_HEADLESS_BOOT_PROOF_STRICT_AUDIT.md`;
3. `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`;
4. `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`;
5. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`;
6. root `README.md`;
7. root `GOVERNANCE.md`;
8. root `AGENTS.md`;
9. root `CLAUDE.md`;
10. `.hiveai/CYCLE_INDEX.md`;
11. `level_factory/GOVERNANCE.md`;
12. `level_factory/README.md`;
13. `docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md`;
14. current repository tree under `.hiveai/`, especially `prompts/`, `codex-logs/`, and `audits/`.

GitHub `main` is authoritative.

### Non-negotiable current-state rule

The **root uppercase `TASKS.md` is the sole live task/status ledger** for the unified Level Factory + Content Platform program.

ChatGPT is the sole owner/writer of root `TASKS.md` task-state promotion, current task, milestone/sprint/cycle status, and audit acceptance.

Codex may read root `TASKS.md`, but **must not edit it in this cycle**.

Historical prompts, builder logs, audits, and the historical cycle index are evidence. They are not a second current-state tracker.

Do not use or modify `C:\Users\sekip\Desktop\ScrubBots` or `Sekiph82/Scrubbots`. The main-game repository is out of scope.

Before any governance/test/documentation edit, create and verify this matching builder log:

`.hiveai/codex-logs/SB-LF00-007-C001_GOVERNANCE_AND_COORDINATION_AUTHORITY_NORMALIZATION_CODEX_LOG.md`

The finalized builder log must be committed and pushed to GitHub `main`. At final handoff, give the user the **full GitHub URL** of the pushed log plus implementation/final publication commit SHA(s). Do not use a local Windows path as the primary handoff and do not paste the full log body unless explicitly asked.

---

## Mission

Implement only canonical requirement:

`SB-LF00-007 — Establish Factory coordination structure while root TASKS remains sole ledger.`

Normalize the repository's builder/auditor/governance instructions after LF/CP unification so all current control documents agree on one authority model:

- root `TASKS.md` = sole live task/status ledger;
- ChatGPT = planner, tracker owner, independent auditor, task-state writer;
- Codex = implementation builder only;
- `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/` = immutable evidence families after use;
- `.hiveai/CYCLE_INDEX.md` = historical evidence/index only, **not current state**;
- absent legacy v3 control-plane files must not be mandatory reads and must not be recreated;
- lowercase `tasks.md` must not be referenced as a live ledger because it is absent and obsolete.

This task is governance/documentation/test normalization only. Do not change Factory algorithms, provider code, generation behavior, Godot scenes, gameplay, Content Platform implementation, or main-game runtime.

---

## 1. Defects and drift this cycle must close

The post-cutover repository currently contains contradictory/stale instructions. Correct them explicitly.

### A. Root `README.md`

Current stale behavior includes:

- calling lowercase `tasks.md` the canonical task ledger;
- describing the repository only as the old standalone Pixel Art Generator foundation;
- saying it does not contain Godot integration even though the accepted `level_factory/` Godot project now exists.

Normalize the README so it truthfully describes the repository as the canonical Level Factory + Content Platform program repository while distinguishing **implemented current foundation** from **planned/unimplemented capabilities**.

At minimum state:

- root `TASKS.md` is the sole live task ledger;
- the repository currently includes the canonical Python Factory Core plus the independently openable `level_factory/` Godot shell;
- Content Platform and other roadmap capabilities remain incomplete until their own audited tasks close;
- main-game runtime remains in `Sekiph82/Scrubbots` when separately authorized;
- builder tests do not self-accept work.

Do not falsely claim unfinished roadmap capabilities are implemented.

### B. Root `GOVERNANCE.md`

Remove/replace obsolete live-authority references such as:

- lowercase `tasks.md` as task-state authority;
- `.hiveai/TASKS.md` as current-state machine block;
- `.hiveai/EVENTS.jsonl` as required live workflow state;
- v3 task/event state as a second current control plane.

Preserve the useful evidence-first builder/auditor separation and strict-audit model.

Required normalized role model:

- ChatGPT owns root `TASKS.md` live status/checkbox/current-task changes;
- ChatGPT owns strict audit verdicts and acceptance;
- Codex implements/tests/logs/commits/pushes only within the active prompt;
- Codex never edits root `TASKS.md` task state;
- builder logs are evidence, not acceptance;
- used prompts/logs/audits remain immutable historical evidence;
- `.hiveai/CYCLE_INDEX.md` may remain as historical cycle evidence/index but is not live status authority.

### C. Root `AGENTS.md`

Remove contradictory mandatory-session requirements that instruct builders to read nonexistent legacy v3 files as current authority, including:

- `.hiveai/RULES.md`;
- `.hiveai/PROJECT.json`;
- `.hiveai/TASKS.md`;
- `.hiveai/EVENTS.jsonl`.

Do not recreate those files.

Remove lowercase `tasks.md` live-ledger references.

Remove any instruction that tells Codex/builders to keep root `TASKS.md` current, commit it with implementation evidence, or otherwise mutate ChatGPT-owned task state.

The normalized builder startup contract should require, at minimum:

1. exact repository/branch identity;
2. non-destructive sync of only the canonical local mirror when instructed;
3. root `TASKS.md` read-only current-state read;
4. authoritative active prompt read from the supplied GitHub URL;
5. previous strict audit and specifically required contract documents from that prompt;
6. branch/HEAD/origin/status/stash/worktree checks where relevant;
7. matching builder log created before implementation;
8. no sibling-repository discovery/substitution;
9. no builder self-audit or tracker-state mutation.

Preserve the accepted offline/core/source-art boundaries that remain valid.

### D. Root `CLAUDE.md`

Normalize it to the same authority model.

Remove contradictory instructions to:

- read nonexistent legacy v3 files as mandatory current state;
- keep/update/commit root `TASKS.md` as part of implementation.

It must state that root `TASKS.md` is read-only for builders and only ChatGPT changes live task status unless a future owner prompt explicitly changes the governance model.

### E. `.hiveai/CYCLE_INDEX.md`

This file **exists** and is tracked. The previous SB-LF00-008 builder log incorrectly claimed it was absent; strict audit finding `F-SB-LF00-008-MINOR-001` records that evidence-quality error.

Normalize this file without destroying history.

Required behavior:

- clearly label it as a **historical cycle/evidence index**, not a live task/status ledger;
- state root `TASKS.md` is the sole current-state authority;
- preserve historical failed/remediated/closed cycle records;
- do not rewrite historical outcomes to make old failures disappear;
- remove or relabel the stale `## Active cycle` block so it can no longer be interpreted as the repository's current active task;
- if preserving the old PAG-M10 active-cycle text for history, label it explicitly as a **pre-unification historical snapshot**, not current state;
- do not turn CYCLE_INDEX into a second tracker for current SB-LF cycles.

### F. `level_factory/GOVERNANCE.md`

It is already largely correct. Change it only if a narrow wording adjustment is required so it cleanly defers to normalized root `GOVERNANCE.md` and root `TASKS.md`.

Do not expand it into a second governance/control plane.

---

## 2. Coordination structure after normalization

The repository coordination model must be explicit and simple:

```text
root TASKS.md
    |
    | sole live task/status state
    v
ChatGPT planner / tracker owner / independent auditor
    |
    | publishes active implementation prompt
    v
.hiveai/prompts/<cycle>.md
    |
    v
Codex builder
    |
    | implementation + tests + chronological evidence
    v
.hiveai/codex-logs/<cycle>.md
    |
    v
ChatGPT strict audit
    |
    v
.hiveai/audits/<cycle>.md
    |
    | only ChatGPT may then update root TASKS.md
    v
next cycle
```

`.hiveai/CYCLE_INDEX.md` may document historical cycles, but it must not participate as a second mutable live-state authority.

No `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `tasks.md`, `STATE.json`, `HANDOFF.md`, or dashboard file should be created/revived as current-state authority in this task.

---

## 3. Historical evidence preservation

Do not delete, rewrite, squash, or rename historical prompt/log/audit evidence merely to make the repository look cleaner.

Preserve:

- `.hiveai/prompts/` history;
- `.hiveai/codex-logs/` history;
- `.hiveai/audits/` history;
- historical cycle outcome records in `.hiveai/CYCLE_INDEX.md`;
- migration documents;
- `reference/audits/` historical evidence.

A prior false statement in a historical builder log stays historical. Correct current governance rather than rewriting old evidence.

---

## 4. Required focused governance tests

Add a focused offline test file, preferably:

`tests/unit/test_sb_lf00_007_governance_authority.py`

It must prove at minimum:

1. root uppercase `TASKS.md` exists;
2. root `README.md`, `GOVERNANCE.md`, `AGENTS.md`, and `CLAUDE.md` consistently identify root `TASKS.md` as the sole live/current task-status ledger;
3. those current control documents do not identify lowercase `tasks.md` as canonical/current;
4. those current control documents do not require absent `.hiveai/RULES.md`, `.hiveai/PROJECT.json`, `.hiveai/TASKS.md`, or `.hiveai/EVENTS.jsonl` as current-state mandatory reads;
5. builders are explicitly prohibited from changing root `TASKS.md` task/status state;
6. ChatGPT is explicitly identified as tracker owner and independent auditor;
7. builder evidence cannot self-accept or self-close a task;
8. `.hiveai/CYCLE_INDEX.md` identifies itself as historical/non-live and root `TASKS.md` as current authority;
9. `.hiveai/CYCLE_INDEX.md` no longer exposes the old PAG-M10 block as an unlabeled current `## Active cycle`;
10. representative historical cycle IDs/outcomes remain present in CYCLE_INDEX after normalization;
11. no legacy current-state files are created/revived:
    - `.hiveai/RULES.md`
    - `.hiveai/PROJECT.json`
    - `.hiveai/TASKS.md`
    - `.hiveai/EVENTS.jsonl`
    - `.hiveai/STATE.json`
    - `.hiveai/HANDOFF.md`
    - root `tasks.md`;
12. `level_factory/GOVERNANCE.md` continues to defer live task status and audit acceptance to root governance/root `TASKS.md`;
13. no product Python/GDScript implementation is added or modified by this governance cycle;
14. previous LF00-001/LF00-002/LF00-006/LF00-008 focused suites remain green.

Prefer structural/read-only tests. Do not create fake tracker/control-plane files as fixtures inside the repository.

---

## 5. Allowed file scope

Expected governance/documentation changes may include only what is necessary among:

- `README.md`;
- `GOVERNANCE.md`;
- `AGENTS.md`;
- `CLAUDE.md`;
- `.hiveai/CYCLE_INDEX.md`;
- `level_factory/GOVERNANCE.md` only if needed;
- `tests/unit/test_sb_lf00_007_governance_authority.py`;
- the required builder log.

Do not edit root `TASKS.md`.

Do not modify Python Factory Core source, Godot scene/project files, provider code, packaging dependencies, or main-game files.

If another current governance-facing document contains the exact same contradictory live-authority defect, you may make the smallest necessary correction and must justify it in the log. Do not expand scope into general documentation cleanup.

---

## 6. Explicit out of scope

Do not begin or complete:

- M01 migration work;
- M03 puzzle solver work;
- M06 Factory Studio migration;
- Perchance/Magnific/PixelLab/provider integration;
- Content Platform implementation;
- main-game runtime implementation;
- secret-manager implementation;
- CI redesign;
- mass historical-file renaming;
- historical audit/log rewriting;
- task-state edits in root `TASKS.md`.

Do not call Magnific, PixelLab, Perchance, or any provider/network service.

---

## 7. Required verification

Run and record at minimum:

1. focused `SB-LF00-007` governance-authority tests;
2. prior `SB-LF00-001` focused suite;
3. prior `SB-LF00-002` focused suite;
4. prior `SB-LF00-006` focused suite;
5. prior `SB-LF00-008` focused suite;
6. full `python -m pytest -q`;
7. `python -m compileall -q src tests`;
8. package import smoke;
9. module CLI help and installed CLI help if installed;
10. Godot headless/editor smoke against `level_factory/` to prove governance edits did not disturb the accepted project shell;
11. `git diff --check`;
12. `git diff -- TASKS.md` must be empty;
13. repository search proving no current governance document still names lowercase `tasks.md` as canonical/current;
14. repository search proving current governance documents do not require absent legacy v3 files as current-state authority;
15. repository check proving no forbidden legacy state files were created;
16. diff check proving no product Python/GDScript file changed;
17. main-game no-access/no-write statement;
18. provider/network/credential no-use statement.

Record failed commands/tests and corrections truthfully.

---

## 8. Builder log requirements

H1 exactly:

`# SB-LF00-007-C001 — Governance & Coordination Authority Normalization`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- exact starting timestamp;
- canonical repository/local root/branch/remote;
- starting HEAD and `origin/main`;
- divergence and initial worktree/stash/worktree state;
- authorities read;
- explicit confirmation that `.hiveai/CYCLE_INDEX.md` **exists** at cycle start;
- explicit confirmation that lowercase root `tasks.md` is absent;
- stale/contradictory governance statements identified before edits;
- exact files changed and rationale;
- README identity/current-state corrections;
- GOVERNANCE role/authority corrections;
- AGENTS builder-start/current-authority corrections;
- CLAUDE authority corrections;
- CYCLE_INDEX historical-only normalization and preservation checks;
- any level_factory governance adjustment;
- focused governance tests added;
- failed tests/commands and corrections;
- prior LF00 regression results;
- full regression result;
- compile/import/CLI/Godot/diff checks;
- proof root `TASKS.md` was not edited;
- proof no legacy v3 control files were recreated;
- proof no product Python/GDScript file changed;
- dependency/license changes, expected none;
- main-game no-access/no-write statement;
- provider/network/credential no-use statement;
- implementation commit SHA and push result;
- final log publication commit SHA and push result;
- final local HEAD / `origin/main` equality/divergence.

### GitHub log delivery requirement

The finalized builder log counts as handoff evidence only after it is committed and pushed to GitHub `main`.

At final Codex handoff to the user:

- provide the full GitHub URL to the finalized builder log;
- provide implementation/final publication commit SHA(s);
- do not paste the log body unless explicitly asked;
- do not provide a local Windows path as the primary handoff;
- stop for independent ChatGPT audit.

---

## Acceptance criteria

`SB-LF00-007-C001` is eligible for PASS only if all are true:

- [ ] root `TASKS.md` is consistently documented as the sole live task/status ledger;
- [ ] ChatGPT is consistently documented as tracker owner and independent auditor;
- [ ] Codex/builders are consistently read-only with respect to root `TASKS.md` task state;
- [ ] lowercase `tasks.md` is no longer referenced as live/canonical authority;
- [ ] absent legacy `.hiveai/RULES.md`, `PROJECT.json`, `TASKS.md`, and `EVENTS.jsonl` are not mandatory current-state reads;
- [ ] no legacy v3 control-plane files are recreated;
- [ ] `.hiveai/CYCLE_INDEX.md` is historical/non-live and no stale PAG cycle is presented as current active task;
- [ ] historical cycle outcomes remain preserved;
- [ ] README accurately reflects the current repository identity without claiming unfinished capabilities complete;
- [ ] level_factory local governance still defers to root authority;
- [ ] focused governance tests pass;
- [ ] LF00-001/LF00-002/LF00-006/LF00-008 focused regressions pass;
- [ ] full regression passes by builder evidence;
- [ ] accepted Godot project still boots headlessly;
- [ ] no product Python/GDScript implementation changes occur;
- [ ] root `TASKS.md` remains builder-untouched;
- [ ] no main-game write occurs;
- [ ] no provider/network/credential call occurs;
- [ ] finalized builder log is pushed to GitHub and handed to the user by full GitHub URL;
- [ ] Codex stops after final push for independent ChatGPT strict audit.
