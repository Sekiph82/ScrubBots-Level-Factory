# SB-LF00-001-C001 — Independent level_factory Godot Project Bootstrap
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Authority and current-state precedence

Read completely from GitHub before any implementation edit:

1. root `TASKS.md`;
2. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`;
3. `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`;
4. `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`;
5. `.hiveai/audits/PAG-SP07-C001-R01_REQUIRED_IDENTITY_MUTATION_EVIDENCE_AND_PROCESS_CLOSURE_STRICT_AUDIT.md`;
6. `AGENTS.md`;
7. `GOVERNANCE.md`;
8. root `README.md`;
9. current repository root structure and `.gitignore`.

GitHub `main` is authoritative.

For live task state and task ownership, the post-cutover root `TASKS.md` plus the cutover audit/migration documents are authoritative. Some older README/GOVERNANCE/AGENTS wording still refers to lowercase `tasks.md` or a v3 `.hiveai` control plane. Do not repair that governance drift in this cycle; it belongs to dedicated M00 governance work. Do not let stale wording redirect the active task away from `SB-LF00-001`.

Do not use `C:\Users\sekip\Desktop\ScrubBots` as a substitute repository. The main game repository is out of scope.

Do not edit root `TASKS.md`; ChatGPT owns task-state promotion.

Before any product/test edit, create and verify this matching builder log:

`.hiveai/codex-logs/SB-LF00-001-C001_INDEPENDENT_LEVEL_FACTORY_GODOT_PROJECT_BOOTSTRAP_CODEX_LOG.md`

---

## Mission

Implement only canonical requirement:

`SB-LF00-001 — Establish level_factory/ as independently openable Godot project.`

Create a minimal, clean Godot 4 project boundary under:

`level_factory/`

This cycle establishes the nested project identity and openability contract. It does **not** migrate the complete Factory implementation, build Factory Studio, implement gameplay, copy the main game, or finish the rest of M00.

The existing Python semantic/pixel-art implementation remains canonical evidence and must not be moved, duplicated or rewritten merely to satisfy this bootstrap.

---

## 1. Required nested Godot project boundary

Create a valid Godot 4 project rooted at exactly:

`level_factory/`

At minimum it must contain:

- `level_factory/project.godot`;
- a deliberately minimal project-owned bootstrap scene if a main scene is configured;
- only the minimal scripts/resources required for that bootstrap.

The project must be independently openable by selecting `level_factory/` in Godot. It must not require opening the repository root as a Godot project.

Use only project-relative `res://` resource references.

Do not use absolute Windows paths in `project.godot`, scenes, resources or scripts.

Do not reference `Sekiph82/Scrubbots`, the owner’s main-game local folder, or resources outside `level_factory/`.

---

## 2. Minimal bootstrap, not architecture expansion

Keep the Godot project intentionally small.

A minimal root `Node` bootstrap scene is acceptable if needed to prove project validity. Do not invent gameplay, puzzle rules, solver behavior, UI workflows, production compiler behavior, provider orchestration or content-publishing behavior.

Do not duplicate the Python Factory Core into GDScript.

Do not introduce a second source of truth for:

- 20..59 production dimensions;
- rectangular legality;
- C01..C16 logical palette;
- 3..12 used-color envelope;
- `CELL_MAJORITY_V1`;
- `PALETTE_SNAP_V1`;
- SP05 provenance contracts;
- SP06 recognizability acceptance.

This task creates the Godot project shell only.

---

## 3. Isolation requirements

The nested project must remain self-contained at the Godot resource layer:

- no `res://../...` escape patterns;
- no absolute file dependencies;
- no main-game preload/load paths;
- no autoload pointing outside `level_factory/`;
- no editor plugin/addon dependency unless already repository-owned and explicitly required by this bootstrap, which is not expected;
- no network dependency;
- no cloud/provider call;
- no API key or credential requirement.

Do not add runtime HTTP or remote-content behavior.

---

## 4. Godot version handling

Target the repository’s current Godot 4-compatible project format. Do not download or install Godot as part of this task.

Before choosing a command, detect whether an existing Godot executable is available locally, for example `godot`, `godot4`, or the owner’s already-installed equivalent.

If Godot is available, record its exact version and run a non-interactive smoke that proves the nested project can be parsed/opened using `--path level_factory` and exits without requiring user interaction. Use the safest command supported by the detected version.

If Godot is not installed or not callable, do **not** download it and do not fabricate a runtime result. Record the smoke as unavailable and rely on the required static project-contract tests in this cycle. `SB-LF00-008` remains the later clean-checkout/headless-boot proof requirement.

---

## 5. Required static contract tests

Add focused offline tests under the existing repository test system proving at minimum:

1. `level_factory/project.godot` exists;
2. it declares a Godot 4 project format compatible with an independently openable nested project;
3. configured main scene, if any, resolves inside `level_factory/`;
4. all bootstrap scene/script resource references are project-relative and remain inside `level_factory/`;
5. no absolute Windows path appears in the nested project files;
6. no `Sekiph82/Scrubbots` or `C:\Users\sekip\Desktop\ScrubBots` dependency appears;
7. no `res://../` escape exists;
8. no external addon/plugin dependency is required for the minimal bootstrap;
9. no network/provider/credential path is introduced;
10. the existing Python package/source layout remains present and unchanged except for narrowly justified test/ignore integration.

Keep these tests structural. Do not invent gameplay semantics.

---

## 6. `.gitignore` handling

If a local Godot smoke creates `.godot/` cache/import state, do not commit generated cache content.

A narrow ignore adjustment for the nested Godot cache is allowed only if required to keep generated editor state out of Git. Do not attempt to complete the broader workspace/cache/secret policy of `SB-LF00-006` in this cycle.

---

## 7. Explicit out-of-scope work

Do not begin or complete:

- `SB-LF00-002` full Factory README/governance/docs/scenes/scripts/tests/output boundary specification;
- `SB-LF00-006` complete generated/candidate/cache/secret folder policy;
- `SB-LF00-007` tracker/control-plane governance normalization;
- `SB-LF00-008` clean-checkout headless boot closure;
- M01+ migrations;
- M03 solver work;
- M06 Factory Studio migration;
- SP08+ semantic features;
- Content Platform implementation;
- main-game runtime implementation.

Do not opportunistically fix stale lowercase `tasks.md` references in README/GOVERNANCE/AGENTS during this task.

---

## 8. Verification

Run and record at minimum:

1. focused `SB-LF00-001` static project-contract tests;
2. existing full Python test suite: `python -m pytest -q`;
3. `python -m compileall -q src tests` where applicable;
4. Godot headless/editor smoke against `--path level_factory` if a Godot executable is already available;
5. repository/package import smoke;
6. existing CLI help smoke;
7. `git diff --check`;
8. scan changed/new nested-project files for absolute paths, `res://../`, main-game references, provider/network/credential strings and external addon dependencies;
9. `git diff -- TASKS.md` must be empty.

Record failed attempts and corrections truthfully.

---

## 9. Builder log requirements

H1 exactly:

`# SB-LF00-001-C001 — Independent level_factory Godot Project Bootstrap`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- starting timestamp;
- repository/local root/branch/remote;
- starting HEAD and `origin/main`;
- divergence and dirty-worktree state;
- authorities read;
- R01 audit acknowledgement;
- exact files created/changed;
- Godot project format/version decisions;
- bootstrap scene/resource structure;
- isolation checks;
- detected Godot executable/version or truthful absence;
- focused test results;
- full regression result;
- compile/import/CLI/diff checks;
- scoped security/offline/path scan;
- dependency/license changes, expected to be none;
- root `TASKS.md` non-edit statement;
- main-game no-access/no-write statement;
- implementation commit SHA and push result;
- final HEAD / `origin/main` equality/divergence.

Stop after final push for independent ChatGPT strict audit.

---

## Acceptance criteria

`SB-LF00-001-C001` is eligible for PASS only if all are true:

- [ ] `level_factory/project.godot` exists and is a valid Godot 4 project descriptor;
- [ ] `level_factory/` is an independent Godot project root, not dependent on opening repository root;
- [ ] any configured bootstrap/main scene is contained within `level_factory/`;
- [ ] nested project resources use only contained project-relative references;
- [ ] no absolute owner-local path or main-game dependency exists;
- [ ] no external addon/plugin is required for the minimal project shell;
- [ ] no provider/network/credential/runtime-HTTP dependency is introduced;
- [ ] existing Python Factory implementation is not moved, duplicated or rewritten;
- [ ] focused structural tests prove the boundary;
- [ ] full existing regression remains green by builder evidence;
- [ ] Godot runtime smoke is truthfully executed if Godot is available, otherwise truthfully recorded unavailable without downloading anything;
- [ ] no root `TASKS.md` builder edit;
- [ ] no main-game write;
- [ ] finalized builder log contains implementation commit SHA and push result;
- [ ] Codex stops after final push for ChatGPT strict audit.