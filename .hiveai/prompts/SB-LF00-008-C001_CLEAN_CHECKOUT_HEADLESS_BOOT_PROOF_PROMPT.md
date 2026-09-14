# SB-LF00-008-C001 — Clean Checkout Headless Boot Proof
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Authority and current-state precedence

Read completely from GitHub before any implementation/test/documentation edit:

1. root `TASKS.md`;
2. previous strict PASS audit:
   `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF00-006-C001_FACTORY_WORKSPACE_EXCLUSIONS_AND_SECRET_BOUNDARY_STRICT_AUDIT.md`;
3. `level_factory/project.godot`;
4. `level_factory/README.md`;
5. `level_factory/GOVERNANCE.md`;
6. `level_factory/docs/DIRECTORY_BOUNDARIES.md`;
7. `docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md`;
8. current root `.gitignore`;
9. prior focused contracts:
   - `tests/unit/test_sb_lf00_001_project_contract.py`
   - `tests/unit/test_sb_lf00_002_project_boundaries.py`
   - `tests/unit/test_sb_lf00_006_workspace_policy.py`
10. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md` and `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`.

GitHub `main` is authoritative.

Do not use or modify `C:\Users\sekip\Desktop\ScrubBots` or `Sekiph82/Scrubbots`. The main-game repository is out of scope.

Do not edit root `TASKS.md`; ChatGPT owns task-state promotion.

Before any implementation/test/documentation edit, create and verify this matching builder log:

`.hiveai/codex-logs/SB-LF00-008-C001_CLEAN_CHECKOUT_HEADLESS_BOOT_PROOF_CODEX_LOG.md`

The finalized builder log must be committed and pushed to GitHub `main`. At final handoff, give the user the **full GitHub URL** of the pushed log plus implementation/final publication commit SHA(s). Do not make a local Windows path the primary log handoff and do not paste the entire log body unless explicitly asked.

---

## Mission

Implement only canonical requirement:

`SB-LF00-008 — Prove clean checkout boots nested Factory headlessly.`

The goal is not another ordinary smoke test inside the owner's existing working tree. The goal is to prove that the committed repository itself contains everything required for the minimal independent `level_factory/` Godot project to open headlessly, without relying on ignored files, untracked files, local caches, local secrets, local generated output, sibling repositories, or machine-specific project state.

This cycle is a migration/verification closure task. Preserve the accepted LF00-001/LF00-002/LF00-006 contracts.

---

## 1. Definition of a valid clean-checkout proof

A valid proof MUST execute Godot against a **tracked-only snapshot produced from the final implementation commit**, not against the ordinary canonical working tree.

Preferred proof mechanism:

1. finish implementation/tests/docs in the canonical local mirror;
2. create the product/test implementation commit locally;
3. before pushing that implementation commit, create a fresh temporary directory outside the repository;
4. materialize the committed snapshot into that directory using `git archive <implementation-commit>` (preferred) or an equivalently isolated tracked-only mechanism;
5. confirm the temporary snapshot contains no `.git/`, no pre-existing `level_factory/.godot/`, no `.env`, no secret directories, no root generated output contents, and no owner-local untracked files;
6. run the installed Godot executable against the snapshot's `level_factory/`:

   `godot --headless --path <TEMP_SNAPSHOT>\level_factory --editor --quit`

7. require exit code 0;
8. capture stdout/stderr and confirm there is no parse error, missing-resource error, failed external dependency, or absolute/sibling-project dependency failure;
9. remove the temporary snapshot after evidence is recorded.

A detached `git worktree` may be used only if it is demonstrably clean/tracked-only and does not inherit local generated/secret/cache state. `git archive` is preferred because it also proves the project does not depend on `.git` metadata.

Do not use a normal copy of the working tree that could accidentally include ignored/untracked files.

If the clean snapshot test fails after the first implementation commit, do not push. Fix the tracked source, create a new implementation commit, and repeat the clean proof against the final product commit.

---

## 2. Tracked-dependency contract

Add a focused offline structural test, preferably:

`tests/unit/test_sb_lf00_008_clean_checkout_contract.py`

It must prove at minimum:

1. `level_factory/project.godot` is tracked by Git;
2. the configured `run/main_scene` is `res://scenes/bootstrap.tscn` and the target file is tracked;
3. every `res://` resource reference found in tracked `level_factory/` project source resolves inside `level_factory/`;
4. every referenced project resource required for boot is tracked by Git, not merely present on disk;
5. the project does not reference ignored/untracked generated output, secret locations, `.godot/`, owner-local absolute paths, `res://../`, external addons/plugins, or the main-game repository;
6. there is no dependency on a sibling checkout;
7. the clean-boot contract itself does not require provider/network/credentials;
8. previous LF00-001/LF00-002/LF00-006 tests remain green.

Use Git as the source of truth where possible, e.g. `git ls-files`, instead of assuming `Path.exists()` means a clean checkout contains a file.

Do not weaken the prior LF00-001/LF00-002/LF00-006 tests merely to make this cycle pass.

---

## 3. Durable clean-checkout documentation

Create one concise technical proof/contract document under `level_factory/docs/`, preferably:

`level_factory/docs/CLEAN_CHECKOUT_BOOT.md`

It must state:

- `level_factory/` is expected to boot from committed tracked files alone;
- local `.godot/` is generated cache and is not required before first boot;
- local generated output is not required;
- local secrets/credentials are not required;
- sibling/main-game repository files are not required;
- the canonical proof command uses an isolated tracked-only snapshot;
- successful boot means exit code 0 with no parse/missing-resource/external-dependency failure;
- the temporary proof snapshot is disposable and not a new source-of-truth workspace;
- root `TASKS.md` remains the sole live task ledger.

Do not create a second verification tracker or permanent clean-checkout clone inside the repository.

---

## 4. Preserve accepted project boundaries

Do not change the minimal project architecture unless a real clean-checkout defect requires a narrow correction.

Expected accepted project shape remains:

- `level_factory/project.godot`
- `level_factory/scenes/bootstrap.tscn`
- `level_factory/README.md`
- `level_factory/GOVERNANCE.md`
- `level_factory/docs/`
- `level_factory/scripts/`
- `level_factory/tests/`
- `level_factory/output/`

The Python Factory Core at repository root remains canonical. Do not duplicate compiler/generator logic into GDScript.

Do not add gameplay UI, autoloads, plugins, addons, provider clients, network requests, or external package dependencies merely to prove boot.

---

## 5. Clean snapshot safety rules

The temporary proof workspace must:

- be outside the canonical repository root;
- be newly created for the proof;
- derive from the final implementation commit's tracked Git tree;
- not copy ignored or untracked files from the canonical working tree;
- not contain credentials or owner-local secret files;
- not contain a pre-existing `level_factory/.godot/` cache before Godot starts;
- not access or write the main-game repository;
- be removed only after evidence is captured.

Godot may generate its own `.godot/` cache inside the disposable proof snapshot during the smoke run. That generated cache is expected and must not be copied back or committed.

Do not use `git clean`, destructive reset, force-push, or owner-file deletion to create the proof environment.

---

## 6. Explicit out of scope

Do not begin or complete:

- `SB-LF00-007` tracker/governance normalization;
- M01+ migrations;
- Factory Studio migration;
- puzzle solver work;
- Content Platform implementation;
- main-game runtime work;
- provider execution;
- OAuth/DPAPI/credential migration;
- generated-output cleanup;
- release packaging;
- CI redesign.

Do not edit task status in root `TASKS.md`.

---

## 7. Required verification sequence

Run and record at minimum:

### Before the implementation commit

1. focused `SB-LF00-008` structural contract tests;
2. prior `SB-LF00-001` suite;
3. prior `SB-LF00-002` suite;
4. prior `SB-LF00-006` suite;
5. full `python -m pytest -q`;
6. `python -m compileall -q src tests`;
7. ordinary canonical-worktree Godot headless/editor smoke;
8. package import smoke;
9. module CLI help and installed CLI help if installed;
10. `git diff --check`;
11. `git diff -- TASKS.md` must be empty;
12. source scan for absolute/sibling/main-game/dependency/provider markers.

### After the product/test implementation commit and before push

13. record the exact implementation commit SHA;
14. create the isolated tracked-only snapshot from that exact commit;
15. prove excluded local state is absent before boot;
16. run Godot headlessly inside the snapshot;
17. capture exit code and relevant stdout/stderr;
18. confirm no parse/missing-resource/external-dependency failure;
19. optionally run the focused LF00-008 test from the snapshot if Python/test dependencies are available without contaminating the proof; this is supplemental, not required for the Godot boot proof;
20. remove the disposable snapshot after recording evidence;
21. only then push the implementation commit;
22. append publication evidence to the builder log and publish the final log commit.

If the post-commit clean proof fails, the failed result must be logged. Do not push the failing implementation as accepted work. Correct tracked source and repeat against the new final implementation commit.

---

## 8. Builder log requirements

H1 exactly:

`# SB-LF00-008-C001 — Clean Checkout Headless Boot Proof`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- exact starting timestamp;
- canonical repository/local root/branch/remote;
- starting HEAD and `origin/main`;
- divergence and pre-existing dirty/stash/worktree state;
- authorities read;
- focused test implementation;
- any documentation/source changes and rationale;
- ordinary worktree verification results;
- implementation commit SHA created before clean proof;
- exact temporary snapshot mechanism;
- exact temporary snapshot location category without exposing unrelated private paths beyond what is necessary;
- proof that the snapshot came from the exact implementation commit;
- proof that `.git/`, pre-existing `.godot/`, generated output contents and secret locations were absent before boot;
- exact Godot command against the temporary snapshot;
- Godot version;
- exit code;
- relevant stdout/stderr disposition;
- explicit statement whether parse errors, missing-resource errors or external dependency failures occurred;
- temporary snapshot cleanup result;
- prior LF00-001/LF00-002/LF00-006 regression results;
- full regression result;
- compile/import/CLI/diff checks;
- dependency/license changes, expected none;
- root `TASKS.md` non-edit statement;
- main-game no-access/no-write statement;
- provider/network/credential no-use statement;
- implementation push result;
- final builder-log publication result;
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

`SB-LF00-008-C001` is eligible for PASS only if all are true:

- [ ] a focused tracked-dependency clean-checkout contract test exists and passes;
- [ ] every boot-critical `level_factory/` resource is proven tracked and contained;
- [ ] no boot-critical dependency relies on ignored/untracked state;
- [ ] no sibling/main-game repository dependency exists;
- [ ] no provider/network/credential dependency exists;
- [ ] durable clean-checkout boot documentation exists under `level_factory/docs/`;
- [ ] prior LF00-001/LF00-002/LF00-006 tests remain green;
- [ ] full regression remains green by builder evidence;
- [ ] ordinary Godot smoke remains green;
- [ ] an isolated tracked-only snapshot is created from the exact final implementation commit;
- [ ] the snapshot contains no pre-existing `.godot/`, secret material, generated owner output, or ordinary worktree-only state before boot;
- [ ] Godot boots the snapshot's `level_factory/` headlessly with exit code 0;
- [ ] no parse, missing-resource, external-addon, sibling-repository, or credential dependency failure occurs;
- [ ] the disposable snapshot is cleaned up after evidence capture;
- [ ] no destructive repository cleanup command is used;
- [ ] root `TASKS.md` remains builder-untouched;
- [ ] no main-game write occurs;
- [ ] no provider/network call or credit spend occurs;
- [ ] finalized builder log is pushed to GitHub and handed to the user by full GitHub URL;
- [ ] Codex stops after final push for independent ChatGPT strict audit.
