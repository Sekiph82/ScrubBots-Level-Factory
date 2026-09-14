# SB-LF00-006-C001 — Factory Workspace Exclusions & Secret Boundary
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Authority and current-state precedence

Read completely from GitHub before any implementation edit:

1. root `TASKS.md`;
2. previous strict PASS audit:
   `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF00-002-C001_FACTORY_PROJECT_BOUNDARIES_AND_LOCAL_DOCUMENTATION_STRICT_AUDIT.md`;
3. `level_factory/README.md`;
4. `level_factory/GOVERNANCE.md`;
5. `level_factory/docs/DIRECTORY_BOUNDARIES.md`;
6. current root `.gitignore`;
7. root `README.md`, `GOVERNANCE.md`, and `AGENTS.md` as repository context;
8. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`;
9. current repository directory structure, especially `output/`, `review/`, `data/`, `exemplars/`, `.hiveai/`, `docs/`, `level_factory/`, and existing cache/log paths.

GitHub `main` is authoritative.

Do not use or modify `C:\Users\sekip\Desktop\ScrubBots` or `Sekiph82/Scrubbots`. The main-game repository is out of scope.

Do not edit root `TASKS.md`; ChatGPT owns task-state promotion.

Before any product/test/documentation edit, create and verify this matching builder log:

`.hiveai/codex-logs/SB-LF00-006-C001_FACTORY_WORKSPACE_EXCLUSIONS_AND_SECRET_BOUNDARY_CODEX_LOG.md`

The finalized builder log must be committed and pushed to GitHub `main`. At final handoff, give the user the **full GitHub URL** of the pushed log plus implementation/final publication commit SHA(s). Do not make a local Windows path the primary log handoff and do not paste the entire log body unless explicitly asked.

---

## Mission

Implement only canonical requirement:

`SB-LF00-006 — Define generated/candidate/cache/secret folders and exclusions.`

Establish a precise repository-wide Factory workspace policy that separates:

- tracked source and durable evidence;
- generated/export output;
- candidate/transient output;
- caches and temporary state;
- local logs;
- local-only secret material.

This cycle is primarily policy, exclusion rules, and focused verification. It must not redesign the generator, move accepted evidence, delete owner data, create a credential system, or perform provider/network work.

---

## 1. Preserve durable tracked truth

The policy must explicitly protect durable repository content from accidental blanket ignores or cleanup rules.

At minimum, treat these as tracked/source/evidence surfaces unless a later audited task says otherwise:

- `src/`;
- root `tests/`;
- `docs/`;
- `.hiveai/prompts/`;
- `.hiveai/codex-logs/`;
- `.hiveai/audits/`;
- root `TASKS.md`;
- `level_factory/project.godot`;
- `level_factory/README.md`;
- `level_factory/GOVERNANCE.md`;
- `level_factory/docs/`;
- `level_factory/scenes/`;
- project-local boundary marker files that intentionally keep empty directories in Git;
- tracked `review/` evidence;
- tracked `data/` and `exemplars/` source/evidence.

Do **not** add a broad ignore such as `review/`, `data/`, `exemplars/`, `.hiveai/`, `docs/`, `*.json`, `*.md`, `*.png`, or any equivalent pattern that could hide canonical evidence/source files.

Do not delete, relocate, rewrite, or untrack existing durable evidence merely to simplify the policy.

---

## 2. Generated and candidate output policy

Document the existing root `output/` surface as generated Factory output. Preserve the current repository convention that only the intentional directory marker remains tracked while generated contents are ignored.

Document `output/candidates/` as candidate/transient generation space when produced by current batch tooling. It is covered by the generated-output boundary and must not become a second durable evidence store.

Document `level_factory/output/` as the Godot-facing/export staging boundary established by `SB-LF00-002`.

Add the narrow Git ignore rule needed so generated contents beneath `level_factory/output/` are excluded while its intentional marker remains trackable.

Do not claim that generated outputs are accepted production content merely because they exist.

Do not move current root output/batch implementation into `level_factory/` in this cycle.

---

## 3. Cache and temporary-state policy

Preserve or formalize exclusions for local caches and temporary state, including the currently used categories where present:

- Python virtual environments and bytecode/cache directories;
- pytest/mypy/ruff caches;
- packaging/build/coverage output;
- Godot `level_factory/.godot/` editor/import cache;
- WFC cache paths;
- temporary directories;
- runtime/local logs.

Do not introduce destructive cleanup commands.

Do not broaden exclusions so far that tracked fixtures/evidence disappear from Git visibility.

---

## 4. Secret boundary

Define a local-only secret boundary without creating, reading, copying, or committing any real secret.

The policy must state that provider/API credentials, tokens, OAuth refresh data, private keys, local secret stores, and machine-specific credential material must never be committed to this repository.

Add narrowly scoped ignore patterns for standard repository-local secret locations such as:

- `.env`;
- `.env.*` local variants, while allowing an explicitly documented non-secret example/template file if the repository later needs one;
- `.secrets/`;
- `secrets/`;
- `level_factory/.secrets/`;
- `level_factory/secrets/`.

Do not create any real secret file. Do not inspect the owner’s home-directory credential stores. Do not migrate Windows DPAPI/OAuth/provider-account data in this task.

Avoid unnecessarily broad extension-wide ignores such as all `*.key`, all `*.pem`, all `*.json`, or similar patterns unless repository evidence proves they are safe and required. The goal is to exclude secret **locations**, not hide arbitrary source/evidence files.

---

## 5. Canonical policy document

Create one concise repository-wide policy document under `docs/`, preferably:

`docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md`

It must define a table or similarly explicit classification for:

- tracked source;
- durable audit/review/reference evidence;
- generated output;
- candidate/transient output;
- cache/temp state;
- local logs;
- local secrets.

For each class, state whether it is tracked, ignored, retained locally, or eligible for cleanup by an explicitly authorized later workflow.

The document must make these distinctions explicit:

- `review/` is durable tracked evidence and is **not** equivalent to generated `output/`;
- `.hiveai/codex-logs/` is tracked builder evidence even though ordinary runtime `logs/` is ignored;
- `data/` and `exemplars/` are not disposable caches merely because they are machine-readable assets;
- `level_factory/output/` is a generated/export staging surface, not canonical tracker truth;
- root `TASKS.md` remains the sole live task ledger;
- no credential is ever required to be stored in Git for this policy.

The document must not create a second cleanup scheduler, task tracker, secret manager, or operational control plane.

---

## 6. `.gitignore` contract

Update `.gitignore` only as needed to express the accepted policy.

Required properties:

1. current tracked-source/evidence surfaces remain visible to Git;
2. root `output/*` remains ignored with its intentional marker preserved;
3. `level_factory/output/*` becomes ignored with its marker preserved;
4. Godot `.godot/` remains ignored;
5. existing Python/WFC/temp/log cache rules remain effective;
6. local secret locations from this prompt are ignored;
7. no blanket rule hides `review/`, `data/`, `exemplars/`, `.hiveai/`, `docs/`, or root `TASKS.md`;
8. no real secret is added.

If an existing rule conflicts with durable evidence, make the smallest safe correction and explain it in the log.

---

## 7. Required focused tests

Add focused offline tests proving at minimum:

1. `docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md` exists;
2. policy explicitly distinguishes durable `review/` evidence from generated `output/`;
3. policy identifies `.hiveai/codex-logs/` as tracked evidence and ordinary `logs/` as local/ignored;
4. policy identifies `data/` and `exemplars/` as durable source/evidence rather than cache;
5. root `output/` generated contents are ignored while its marker remains intentionally trackable;
6. `level_factory/output/` generated contents are ignored while its marker remains intentionally trackable;
7. `level_factory/.godot/` remains ignored;
8. representative Python/WFC/temp/log cache paths remain ignored;
9. representative `.env`, `.secrets/`, `secrets/`, and project-local secret paths are ignored;
10. representative files beneath `review/`, `data/`, `exemplars/`, `docs/`, and `.hiveai/audits/` are **not** accidentally ignored;
11. root `TASKS.md` is not ignored;
12. no actual secret/token/key value is introduced by the implementation or fixtures;
13. previous LF00-001 and LF00-002 tests remain green.

Prefer using Git's own ignore semantics (`git check-ignore`, including `--no-index` when appropriate for representative non-existent paths) instead of reimplementing `.gitignore` matching incorrectly in Python.

Tests must not create persistent secret files. Temporary test paths must be cleaned automatically.

---

## 8. Security and non-destructive constraints

Do not:

- read or print environment-secret values;
- inspect Windows Credential Manager/DPAPI stores;
- read provider API keys;
- call Magnific, PixelLab, or any cloud provider;
- contact external network services;
- delete generated owner files as part of implementation;
- run recursive cleanup commands;
- use `git clean`, destructive reset, or force-push;
- modify the main-game repository;
- untrack existing evidence without explicit prompt authorization.

This cycle defines safe boundaries. It is not a cleanup operation.

---

## 9. Explicit out of scope

Do not begin or complete:

- `SB-LF00-007` broader tracker/governance normalization;
- `SB-LF00-008` clean-checkout headless boot closure;
- secret encryption/storage implementation;
- provider login/OAuth/DPAPI migration;
- M01+ migrations;
- M03 solver work;
- M06 Factory Studio migration;
- Content Platform implementation;
- main-game runtime implementation;
- automated retention/deletion scheduling.

Do not edit task status in root `TASKS.md`.

---

## 10. Verification

Run and record at minimum:

1. focused `SB-LF00-006` tests;
2. prior `SB-LF00-001` and `SB-LF00-002` focused suites;
3. full `python -m pytest -q`;
4. `python -m compileall -q src tests`;
5. Godot headless/editor smoke using `--path level_factory` if the existing executable remains available;
6. package import smoke;
7. module CLI help and installed CLI help if installed;
8. `git diff --check`;
9. explicit `git check-ignore` evidence for ignored generated/cache/secret representative paths;
10. explicit negative `git check-ignore` evidence for durable representative `review/`, `data/`, `exemplars/`, `docs/`, `.hiveai/audits/`, and `TASKS.md` paths;
11. scan the changed files for obvious credential literals or secret values without inspecting external credential stores;
12. `git diff -- TASKS.md` must be empty.

Record failed commands/tests and corrections truthfully.

---

## 11. Builder log requirements

H1 exactly:

`# SB-LF00-006-C001 — Factory Workspace Exclusions & Secret Boundary`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- exact starting timestamp;
- canonical repository/local root/branch/remote;
- starting HEAD and `origin/main`;
- divergence and pre-existing dirty/stash/worktree state;
- authorities read;
- workspace classification decisions;
- exact `.gitignore` additions/removals and rationale;
- policy document creation;
- focused test implementation;
- initial failures and corrections;
- representative positive and negative `git check-ignore` evidence;
- prior LF00-001/LF00-002 regression results;
- full regression result;
- Godot smoke result;
- compile/import/CLI/diff checks;
- credential-literal safety scan;
- dependency/license changes, expected none;
- explicit statement that no real secret was read or created;
- explicit statement that no generated owner files were deleted;
- root `TASKS.md` non-edit statement;
- main-game no-access/no-write statement;
- implementation commit SHA and push result;
- final HEAD / `origin/main` equality/divergence.

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

`SB-LF00-006-C001` is eligible for PASS only if all are true:

- [ ] one canonical workspace/exclusion policy document exists under `docs/`;
- [ ] tracked source/durable evidence is explicitly separated from generated/candidate/cache/log/secret state;
- [ ] `review/`, `data/`, `exemplars/`, `.hiveai/` evidence, docs and tracker truth are not accidentally ignored;
- [ ] root generated `output/` convention remains intact;
- [ ] `level_factory/output/` generated contents are ignored while its marker remains trackable;
- [ ] Godot/Python/WFC/temp/log cache exclusions remain correct;
- [ ] local secret locations are ignored without committing any real secret;
- [ ] no unsafe blanket ignore hides arbitrary source/evidence extensions;
- [ ] no owner-generated files are deleted;
- [ ] no external credential store is inspected;
- [ ] focused ignore-policy tests are green;
- [ ] prior LF00-001/LF00-002 focused tests remain green;
- [ ] full regression remains green by builder evidence;
- [ ] Godot smoke remains green if executable available;
- [ ] root `TASKS.md` remains builder-untouched;
- [ ] no main-game write occurs;
- [ ] no provider/network call or credit spend occurs;
- [ ] finalized builder log is pushed to GitHub and handed to the user by full GitHub URL;
- [ ] Codex stops after final push for independent ChatGPT strict audit.