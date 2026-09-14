# SB-LF00-006-C001 — Factory Workspace Exclusions & Secret Boundary Strict Audit
Document role: CHATGPT STRICT AUDIT

## Verdict

**PASS / CLOSED**

Severity summary:

- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 3

No remediation cycle is required.

## Audited requirement

`SB-LF00-006 — Define generated/candidate/cache/secret folders and exclusions.`

## Audit authority and base

Repository: `Sekiph82/ScrubBots-Level-Factory`

Builder starting base:

`8dd0dcf9bbefc6572175fce8ddbef8e162015a03`

Builder implementation commit:

`0f5ef0787b04fc86913ed495566fa03717574d48`

Final builder-log publication commit:

`b4b7ffc3da12248f4635ccf3207c4ca2ca0c59d1`

The complete builder delta from the ChatGPT-owned task-opening base to the terminal builder publication is exactly two commits ahead and zero behind.

Changed paths across the builder cycle are limited to:

1. `.gitignore`
2. `.hiveai/codex-logs/SB-LF00-006-C001_FACTORY_WORKSPACE_EXCLUSIONS_AND_SECRET_BOUNDARY_CODEX_LOG.md`
3. `docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md`
4. `tests/unit/test_sb_lf00_006_workspace_policy.py`

No root `TASKS.md` builder edit is present in the audited delta.

## Evidence inspected independently

The audit independently inspected the canonical GitHub contents and commit/diff history for:

- the finalized builder log;
- the implementation commit;
- the final evidence-only publication commit;
- the complete base-to-terminal compare;
- current `.gitignore`;
- `docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md`;
- `tests/unit/test_sb_lf00_006_workspace_policy.py`;
- the previously accepted `level_factory/` boundary contract;
- the LF/CP migration mapping and canonical repository split.

Builder runtime command output is evidence, not automatic acceptance. Source, diff, scope, policy semantics, and test semantics were reviewed independently.

---

## 1. Builder chronology and publication integrity

### PASS

The builder log records an exact starting timestamp:

`2026-09-15T01:12:14.3246250+03:00`

It records synchronization from the previous builder publication to the ChatGPT-owned current tracker head and identifies both starting `HEAD` and `origin/main` as:

`8dd0dcf9bbefc6572175fce8ddbef8e162015a03`

The log states the worktree was clean before required builder-log creation and that the builder log was created before product/test/documentation/ignore edits.

The implementation commit is:

`0f5ef0787b04fc86913ed495566fa03717574d48`

The terminal publication commit is:

`b4b7ffc3da12248f4635ccf3207c4ca2ca0c59d1`

Independent commit inspection confirms the terminal publication commit changes only the builder log and adds publication evidence. It does not modify product, test, policy, ignore, or tracker state.

The builder did not self-assert an audit PASS.

---

## 2. Scope discipline

### PASS

The implementation delta is narrowly scoped to workspace classification, ignore policy, documentation, and focused verification.

No evidence was found of:

- generator redesign;
- Factory Studio migration;
- solver work;
- Content Platform implementation;
- main-game runtime work;
- provider execution;
- OAuth or DPAPI migration;
- secret storage/encryption implementation;
- dependency/package/license changes;
- root tracker mutation;
- cleanup automation;
- generated-owner-file deletion.

The implementation does not begin `SB-LF00-007`, `SB-LF00-008`, or M01+ work.

---

## 3. Durable source and evidence protection

### PASS

The new policy explicitly classifies durable tracked surfaces separately from disposable/generated state.

Protected source/evidence includes:

- `src/`;
- root `tests/`;
- `docs/`;
- root `TASKS.md`;
- `level_factory/project.godot`;
- `level_factory/README.md`;
- `level_factory/GOVERNANCE.md`;
- `level_factory/docs/`;
- `level_factory/scenes/`;
- boundary marker files;
- `review/`;
- `reference/`;
- `data/`;
- `exemplars/`;
- `.hiveai/prompts/`;
- `.hiveai/codex-logs/`;
- `.hiveai/audits/`.

The policy correctly states that `review/` is durable evidence and is not equivalent to generated `output/`.

It also explicitly distinguishes tracked builder logs under `.hiveai/codex-logs/` from ordinary ignored runtime `logs/`.

`data/` and `exemplars/` are correctly classified as durable source/evidence assets rather than disposable caches.

No broad ignore rule was introduced for any of these surfaces.

---

## 4. Generated and candidate output boundary

### PASS

The existing root generated-output convention remains intact:

- `output/*`
- `!output/.gitkeep`

The implementation adds the analogous Godot-facing staging boundary:

- `level_factory/output/*`
- `!level_factory/output/.gitkeep`

This is appropriately narrow.

The policy defines `output/candidates/` as transient candidate generation space covered by the generated-output boundary. It explicitly does not turn candidate output into a durable evidence store or accepted production content.

No root output implementation was moved into `level_factory/`.

---

## 5. Cache and temporary-state boundary

### PASS

Existing narrow local-state exclusions are preserved for:

- `.venv/` and `venv/`;
- Python bytecode/cache;
- pytest/mypy/ruff caches;
- build/dist/package metadata;
- coverage artifacts;
- WFC cache paths;
- `tmp/` and `temp/`;
- runtime `logs/` and `*.log`;
- `level_factory/.godot/`.

No destructive cleanup behavior was introduced.

No evidence/source directory was converted into a cache merely because its content may be machine-readable.

---

## 6. Secret boundary

### PASS

The implementation adds repository-local secret exclusions:

- `.env`
- `.env.*`
- `!.env.example`
- `.secrets/`
- `secrets/`
- `level_factory/.secrets/`
- `level_factory/secrets/`

This satisfies the required location-based secret policy without introducing unsafe blanket extension rules.

Independent `.gitignore` inspection confirms there is no newly introduced blanket ignore such as:

- `*.json`
- `*.md`
- `*.png`
- `*.key`
- `*.pem`

The policy explicitly forbids committing API credentials, tokens, OAuth refresh data, private keys, local secret stores, and machine-specific credential material.

No real secret file is introduced by the audited commit delta.

The builder log states that no API key, token, environment-secret value, DPAPI store, or external credential store was read or printed.

---

## 7. `.gitignore` precision

### PASS

Independent base-to-terminal comparison confirms `.gitignore` receives 13 additions and zero deletions.

The additions are limited to:

- the `level_factory/output/` generated staging rule and marker exception;
- repository-local secret-location rules and `.env.example` exception.

Existing cache/generated rules remain intact.

There is no broad ignore of:

- `review/`;
- `data/`;
- `exemplars/`;
- `.hiveai/`;
- `docs/`;
- `TASKS.md`;
- arbitrary Markdown, JSON, or image files.

This is the correct security posture for a repository where audit evidence and generated media coexist.

---

## 8. Workspace policy document quality

### PASS

`docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md` creates a single canonical classification table covering:

- tracked source;
- durable audit/review/reference evidence;
- durable source/evidence assets;
- generated output;
- candidate/transient output;
- cache/temp state;
- local runtime logs;
- tracked builder evidence;
- local-only secrets.

For each class it describes Git treatment and retention/cleanup boundaries.

The policy explicitly preserves the root `TASKS.md` as sole live task ledger and states that it does not create a cleanup scheduler, task tracker, secret manager, or operational control plane.

It does not claim broader retention or secret-management implementation is complete.

---

## 9. Focused test design

### PASS

The new focused suite uses Git itself:

`git check-ignore --no-index`

This is stronger and less error-prone than implementing a custom approximation of `.gitignore` semantics in Python.

Positive cases include representative generated/cache/temp/log/secret paths.

Negative cases include representative durable paths beneath:

- `review/`;
- `data/`;
- `exemplars/`;
- `docs/`;
- `.hiveai/audits/`;
- `.hiveai/prompts/`;
- `.hiveai/codex-logs/`;
- `level_factory/project.godot`;
- root `TASKS.md`.

The marker files `output/.gitkeep` and `level_factory/output/.gitkeep` are explicitly tested as trackable.

The suite also checks absence of dangerous extension-wide ignore rules and performs a heuristic scan of changed files for obvious private-key/key-like/assignment-shaped credential literals.

The tests do not create persistent secret fixtures.

---

## 10. Builder runtime verification evidence

### ACCEPTED AS BUILDER EVIDENCE

The builder reports:

- `SB-LF00-006` focused suite: `7 passed`;
- prior `SB-LF00-001`: `7 passed`;
- prior `SB-LF00-002`: `9 passed`;
- full regression: `589 passed, 1 warning`;
- compileall: success;
- package import smoke: success;
- module CLI help: success;
- installed CLI help: success;
- Godot 4.7.2 headless/editor smoke: success;
- `git diff --check`: success apart from non-failing working-copy line-ending warning;
- `git diff -- TASKS.md`: empty.

The initial focused failures are disclosed chronologically. They were assertion-wording/Markdown-whitespace mismatches, and the final corrections did not broaden or weaken the workspace policy.

No failure evidence suggests a product defect.

---

## 11. Root tracker ownership

### PASS

The complete builder delta contains no `TASKS.md` modification.

The new policy reiterates that root `TASKS.md` is the sole live task ledger.

Codex remained builder-only and did not promote its own task state.

---

## 12. Main-game and provider boundary

### PASS

No changed path belongs to the main-game repository.

No runtime dependency on `Sekiph82/Scrubbots` is introduced.

No provider execution path, API call, credential migration, or credit-spending behavior is added.

This is consistent with the canonical LF/CP repository split.

---

## Notes

### NOTE-001 — Credential scan is intentionally heuristic

The focused test scans changed files for obvious credential literals. This is useful defense-in-depth but is not a complete secret-history scanner and must not be represented as one.

That limitation does not block this task because the requirement is to define safe workspace/ignore boundaries without reading external credentials, not to conduct a historical secret-forensics audit.

### NOTE-002 — Runtime commands were not re-executed by the auditor

The auditor independently inspected GitHub source, policy, tests, commit history, and diff semantics but did not execute commands on the owner's Windows workstation.

The full pytest/Godot/CLI results are therefore accepted as builder evidence, consistent with the task's audit model.

### NOTE-003 — The final publication commit cannot self-record its own SHA

The finalized log states that its evidence-only update is committed and pushed afterward. The terminal GitHub commit is independently visible as:

`b4b7ffc3da12248f4635ccf3207c4ca2ca0c59d1`

This is normal chronology and not a defect.

---

## Acceptance-criteria disposition

- canonical workspace/exclusion policy under `docs/`: PASS
- tracked source vs durable evidence vs generated/candidate/cache/log/secret separation: PASS
- durable evidence remains visible: PASS
- root generated-output convention preserved: PASS
- `level_factory/output/` exclusion with marker preservation: PASS
- Godot/Python/WFC/temp/log cache rules preserved: PASS
- repository-local secret locations ignored: PASS
- no unsafe blanket extension ignore: PASS
- no real secret introduced: PASS
- no owner-generated files deleted: PASS by diff + builder evidence
- no external credential-store inspection: PASS by builder evidence
- focused policy tests: PASS by builder evidence and independent test review
- LF00-001/LF00-002 regression suites: PASS by builder evidence
- full regression: PASS by builder evidence
- Godot smoke: PASS by builder evidence
- root `TASKS.md` builder-untouched: PASS independently verified
- no main-game write: PASS by audited repository delta + builder evidence
- no provider/network/credit spend: PASS by code/diff scope + builder evidence
- finalized builder log pushed: PASS
- independent audit stop point respected: PASS

## Final disposition

**SB-LF00-006-C001 = PASS / CLOSED.**

`SB-LF00-006` is eligible for promotion from `[PARTIAL]` to VERIFIED/`[x]` in the ChatGPT-owned root tracker.

The logical next M00 requirement is `SB-LF00-008 — Prove clean checkout boots nested Factory headlessly`, because workspace/exclusion boundaries are now defined and a clean tracked-only checkout can be tested without relying on ignored/local machine state.
