# SB-LF00-002-C001 — Factory Project Boundaries & Local Documentation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Authority and current-state precedence

Read completely from GitHub before any implementation edit:

1. root `TASKS.md`;
2. strict PASS audit for the previous cycle:
   `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF00-001-C001_INDEPENDENT_LEVEL_FACTORY_GODOT_PROJECT_BOOTSTRAP_STRICT_AUDIT.md`;
3. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`;
4. `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`;
5. `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`;
6. current `level_factory/project.godot` and `level_factory/bootstrap.tscn`;
7. root `README.md`, `GOVERNANCE.md`, `AGENTS.md`, and `.gitignore` as historical/current repository context;
8. current repository structure.

GitHub `main` is authoritative.

Do not use `C:\Users\sekip\Desktop\ScrubBots` as a substitute repository. The main game repository is out of scope.

Do not edit root `TASKS.md`; ChatGPT owns task-state promotion.

Before any product/test edit, create and verify this matching builder log:

`.hiveai/codex-logs/SB-LF00-002-C001_FACTORY_PROJECT_BOUNDARIES_AND_LOCAL_DOCUMENTATION_CODEX_LOG.md`

The builder log must be pushed to GitHub. At final handoff, do **not** paste the log body or point the user to a local filesystem path. Return the full GitHub URL of the pushed builder log, together with the implementation/final publication commit SHA(s), then stop for independent ChatGPT audit.

---

## Mission

Implement only canonical requirement:

`SB-LF00-002 — Maintain Factory-specific README/governance/docs/scenes/scripts/tests/output boundaries.`

Formalize the project-local ownership/layout contract inside `level_factory/` while preserving the accepted `SB-LF00-001` independently openable Godot project.

This cycle is about directory and documentation boundaries, not Factory feature implementation.

---

## 1. Required project-local structure

Establish a clear `level_factory/` project-local boundary containing at minimum:

- `level_factory/README.md`;
- `level_factory/GOVERNANCE.md`;
- `level_factory/docs/`;
- `level_factory/scenes/`;
- `level_factory/scripts/`;
- `level_factory/tests/`;
- `level_factory/output/`.

Empty future-use directories may use a small `.gitkeep` or a concise README where appropriate. Do not create placeholder implementation code merely to make a directory non-empty.

The root repository Python package remains where it is. Do not move the existing `src/`, root `tests/`, semantic provider code, compiler, quality gates, or CLI into `level_factory/`.

---

## 2. Scene boundary

Move the accepted minimal bootstrap scene from:

`level_factory/bootstrap.tscn`

to the project-local scene boundary, preferably:

`level_factory/scenes/bootstrap.tscn`

Update `level_factory/project.godot` to point to the new contained `res://scenes/bootstrap.tscn` path.

Do not add gameplay, UI, autoloads, plugins, scripts, external resources, or provider behavior to the bootstrap scene.

The accepted `SB-LF00-001` independent-openability contract must remain intact.

---

## 3. `level_factory/README.md` contract

Create a concise project-local README that explains:

- what `level_factory/` owns;
- that it is an independently openable Godot 4 project;
- that the existing Python Factory Core / semantic implementation remains canonical and is not duplicated into GDScript;
- the purpose of `docs/`, `scenes/`, `scripts/`, `tests/`, and `output/`;
- that root `TASKS.md` is the sole live task ledger;
- that project-local docs must not create a second tracker or acceptance authority;
- that main-game runtime implementation belongs to `Sekiph82/Scrubbots` when separately authorized;
- that generated or provider-backed features are not implied by the project shell.

Do not restate hundreds of canonical requirements or create a duplicate roadmap.

---

## 4. `level_factory/GOVERNANCE.md` contract

Create narrow project-local governance that defines ownership boundaries only.

It must explicitly defer to root repository governance and root `TASKS.md` for:

- task status;
- milestone/sprint/cycle acceptance;
- audit authority;
- builder/auditor separation.

It must not create a competing H!veAI control plane, tracker, event ledger, prompt index, task denominator, or acceptance state.

It should state that:

- ChatGPT remains independent auditor/tracker owner;
- Codex remains builder only;
- `level_factory/` may contain Godot-facing workspace/presentation/integration surfaces;
- canonical Factory algorithms remain in their accepted implementation until explicitly migrated by later audited tasks;
- main-game runtime code is not owned here.

Do not fix unrelated root governance drift in this cycle. `SB-LF00-007` remains the dedicated broader coordination/governance normalization task.

---

## 5. Directory-role documentation

Add one concise document under `level_factory/docs/` describing the project-local directory contract.

At minimum define:

- `scenes/` — Godot scenes owned by Factory project;
- `scripts/` — future Godot-side adapter/presentation/editor scripts only when authorized;
- `tests/` — future Godot-local tests/fixtures; does not replace root Python tests;
- `output/` — Factory-produced/export staging boundary; not a declaration that broader generated/cache/secret policy is complete;
- `docs/` — project-local technical docs, not tracker truth.

Explicitly state that `SB-LF00-006` still owns the broader generated/candidate/cache/secret folder and exclusion policy.

---

## 6. Boundary safety

Project-local files must not:

- contain absolute owner-local paths;
- reference `res://../`;
- depend on the main game repository;
- add external plugins/addons;
- add network/provider/credential/runtime HTTP behavior;
- copy Python compiler/semantic/quality source into GDScript;
- create a second tracker/task checklist representing canonical project state.

Do not introduce symlinks or junctions to external repositories.

---

## 7. Required focused tests

Extend/add focused offline tests proving at minimum:

1. all required project-local boundary paths exist;
2. `level_factory/README.md` exists and names root `TASKS.md` as sole live task ledger;
3. `level_factory/GOVERNANCE.md` explicitly defers acceptance/task authority to root governance/tracker and does not claim builder self-acceptance;
4. bootstrap scene resides under `level_factory/scenes/`;
5. `project.godot` points to the contained `res://scenes/...` main scene;
6. scene/resource references remain contained inside `level_factory/`;
7. no absolute owner-local or main-game path appears in project-local files;
8. no provider/network/credential/plugin dependency is introduced;
9. no Python production source is duplicated inside `level_factory/`;
10. project-local docs do not create a competing canonical task ledger;
11. existing `SB-LF00-001` structural/openability tests remain green after the scene move.

Keep tests structural and offline.

---

## 8. Explicit out of scope

Do not complete or begin:

- `SB-LF00-006` broad generated/candidate/cache/secret policy;
- `SB-LF00-007` root tracker/governance normalization;
- `SB-LF00-008` clean-checkout headless-boot proof;
- M01+ feature migrations;
- M03 solver;
- M06 Factory Studio implementation;
- Content Platform implementation;
- main-game runtime implementation;
- provider execution or model qualification.

Do not mark any task complete in `TASKS.md`.

---

## 9. Verification

Run and record at minimum:

1. focused `SB-LF00-002` tests;
2. previous `SB-LF00-001` tests;
3. full `python -m pytest -q`;
4. `python -m compileall -q src tests`;
5. Godot headless/editor smoke using `--path level_factory` if the existing executable remains available;
6. package import smoke;
7. module CLI help and installed CLI help if installed;
8. `git diff --check`;
9. scoped scan of `level_factory/` source/docs excluding `.godot/` for absolute paths, `res://../`, main-game refs, provider/network/credential markers, plugins/addons, and competing tracker claims;
10. `git diff -- TASKS.md` must be empty.

Record failed attempts and corrections truthfully.

---

## 10. Builder log requirements

H1 exactly:

`# SB-LF00-002-C001 — Factory Project Boundaries & Local Documentation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- exact starting timestamp;
- canonical repository/local root/branch/remote;
- starting HEAD and `origin/main`;
- divergence and pre-existing dirty/stash/worktree state;
- authorities read;
- exact files created/moved/changed;
- bootstrap-scene move and `project.godot` update;
- README/governance/directory-boundary decisions;
- focused tests and failures/corrections;
- previous LF00-001 regression;
- full regression;
- Godot smoke result;
- compile/import/CLI/diff checks;
- scoped safety/offline/path scan;
- dependency/license changes, expected none;
- root `TASKS.md` non-edit statement;
- main-game no-access/no-write statement;
- implementation commit SHA and push result;
- final HEAD / `origin/main` equality/divergence.

### GitHub log delivery requirement

The finalized builder log is evidence only after it is committed and pushed to GitHub `main`.

At final Codex handoff to the user:

- provide the full GitHub URL to the finalized builder log;
- provide implementation/final publication commit SHA(s);
- do not paste the log body unless explicitly asked;
- do not provide a local Windows path as the primary handoff;
- stop for independent ChatGPT audit.

---

## Acceptance criteria

`SB-LF00-002-C001` is eligible for PASS only if all are true:

- [ ] project-local README exists and correctly defines ownership/authority;
- [ ] project-local governance exists and does not compete with root governance/tracker;
- [ ] `docs/`, `scenes/`, `scripts/`, `tests/`, and `output/` boundaries exist;
- [ ] bootstrap scene is under the project-local scenes boundary;
- [ ] `project.godot` continues to open independently and points only to contained resources;
- [ ] no Python Factory Core/semantic implementation is duplicated into Godot;
- [ ] no main-game dependency or external filesystem path is introduced;
- [ ] no provider/network/credential/plugin dependency is introduced;
- [ ] broader `SB-LF00-006` exclusion policy is not falsely claimed complete;
- [ ] broader `SB-LF00-007` governance normalization is not falsely claimed complete;
- [ ] focused LF00-002 and prior LF00-001 tests are green;
- [ ] full regression remains green by builder evidence;
- [ ] Godot smoke remains green if executable available;
- [ ] root `TASKS.md` remains builder-untouched;
- [ ] no main-game write occurs;
- [ ] finalized builder log is pushed to GitHub and handed to the user by full GitHub URL;
- [ ] Codex stops after final push for independent ChatGPT strict audit.