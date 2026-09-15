# SB-LF06-002-C001-R01 — Committed Godot Runtime Regression Remediation

Document role: CODEX BUILDER LOG

## Start and synchronization

- Starting timestamp: 2026-09-15T20:54:00+03:00.
- Canonical repository verified as `Sekiph82/ScrubBots-Level-Factory`; canonical origin is `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Synchronization used `git fetch origin main` followed by non-destructive `git merge --ff-only origin/main`.
- Starting synchronized local HEAD: `d58c43f99df333075cfaa2089d1d09066b3cb382`.
- Starting `origin/main`: `d58c43f99df333075cfaa2089d1d09066b3cb382`; ahead/behind: `0/0`.
- Initial tracked worktree was clean. The only untracked files were the five pre-existing owner-local Godot UID files under `level_factory/scripts/`; they are preserved and will not be read, edited, staged, or deleted.
- One canonical worktree is present. Existing stashes were observed and left unchanged.
- Root `TASKS.md` was read and remains untouched; it names this R01 as the active task and remains the sole tracker.

## Required reads before edits

- Read the complete R01 remediation prompt from the supplied GitHub URL.
- Read the complete `SB-LF06-002-C001` strict audit from the supplied GitHub URL. Its sole MAJOR finding is that the accepted Godot interaction evidence depended on a deleted disposable runner; the product implementation is retained.
- Read the complete original `SB-LF06-002-C001` prompt and finalized builder log from GitHub.
- Read the complete prior `SB-LF06-001-C001-R01` strict PASS audit from GitHub.
- Read `AGENTS.md`, `GOVERNANCE.md`, root `TASKS.md`, `level_factory/project.godot`, the Factory Studio scene/scripts, both existing root runtime-support contracts, focused LF06-001/LF06-002 Python tests, `level_factory/README.md`, `level_factory/GOVERNANCE.md`, and the project-boundary tests.

## Pre-edit inventory and remediation boundary

- The accepted product scene is `res://scenes/factory_studio.tscn` with the existing Navigation, Workspace, TargetControls, and truthful Core footer.
- Existing runtime contracts are root `tests/support/factory_studio_runtime_contract.gd` and `tests/support/factory_studio_target_controls_contract.gd`; the strict audit confirmed they contain real interaction assertions but are not directly runnable from a clean `level_factory` project command.
- Existing project-local test boundary contains only `level_factory/tests/.gitkeep`; no committed runner exists.
- R01 is limited to a committed project-local Godot runtime entrypoint, narrow Python protection for that entrypoint, and this matching log. The target-control product semantics and root support contracts remain unchanged unless the new runner reveals a directly evidenced runtime defect.

## Planned implementation

- Add one small `level_factory/tests/factory_studio_runtime_suite.gd` SceneTree entrypoint with no `res://../` references.
- Consolidate the accepted LF06-001 Navigation/Workspace checks and LF06-002 Generate/target-control interaction checks into that project-local runner so the exact clean-checkout command instantiates the real `res://scenes/factory_studio.tscn`.
- Add narrow Python assertions that the runner is inside the Factory project, is tracked/contained, loads the real scene, fail-closes with nonzero exit, and exercises the target-control interactions.
- Preserve the existing target-controls implementation, Core-unavailable boundary, inert non-Generate surfaces, Python Core, provider/network boundary, and root tracker.

## Implementation chronology

- Added only `level_factory/tests/factory_studio_runtime_suite.gd` as the project-local committed `SceneTree` entrypoint. It uses only project-contained `res://` paths and directly loads `res://scenes/factory_studio.tscn`.
- The runner preserves the prior LF06-001 assertions for Navigation/Workspace node paths, signal binding, Dashboard/Core status, and fail-closed exit behavior.
- The runner consolidates the accepted LF06-002 runtime assertions for Generate navigation, deterministic target-control node paths, canonical displayed choices, 20..59 bounds, independent `23x47` edits, draft snapshot fields/state, no-operation UI, inert Import behavior, and navigation-session draft stability.
- Updated only narrow Python protection: the existing project-boundary allowlist recognizes the authorized runner, and LF06-002 tests assert the runner is project-local, has no `res://../` escape, loads the real scene, contains nonzero/zero termination paths, and exercises Generate/draft interactions.
- No target-control product file, Python Factory Core file, root tracker, provider, solver, Content Platform, main-game, Dashboard, Import, Library, batch, or output implementation was changed.

## Verification before implementation commit

- Initial direct command from the working tree: `godot --headless --path level_factory --script res://tests/factory_studio_runtime_suite.gd` — printed `SB-LF06-002-C001-R01 committed runtime suite PASS` and exited `0`. This pre-commit run is recorded as working-tree evidence; the clean tracked-tree run is recorded after commit/push below.
- `git diff --check` passed.
- Focused Python/boundary command: `python -m pytest -q tests/unit/test_sb_lf06_001_factory_studio_workspace.py tests/unit/test_sb_lf06_002_factory_studio_target_controls.py tests/unit/test_sb_lf00_002_project_boundaries.py` — `22 passed`, one known local pytest cache-permission warning.
- `python -m compileall -q src tests` passed.
- A combined shell probe that appended an `rg` forbidden-marker search returned code 1 because the search correctly found no matches; the checks were rerun separately and the required diff/Python/compile commands passed. No forbidden marker was found in the runner.
- `git ls-files level_factory/tests/factory_studio_runtime_suite.gd` was verified after staging; the runner is in the intended project boundary and no temporary runner files or project.godot mutation exist.
