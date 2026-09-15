# SB-LF06-001-C001 — Factory Studio Canonical-Core Workspace Migration
Document role: CODEX BUILDER LOG

## 2026-09-15T09:48:25+03:00 — pre-edit session start

- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Verified repository root with `git rev-parse --show-toplevel`.
- Verified branch: `main`.
- Starting HEAD: `8532d39b8c4203f37dec79daad3d647f323c652a`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git` for fetch and push.
- Starting ahead/behind state: `0 0` relative to `origin/main`.
- Starting Git status: clean (`## main...origin/main`).
- Existing stashes and the single current worktree were inspected; no stash was applied and no sibling repository was searched or used.

## Authority and contract reads

- Read the current root `TASKS.md` completely. It names `SB-LF06-001-C001` as the current task and states that root `TASKS.md` is the sole live tracker. It will not be edited in this cycle.
- Read the current root `AGENTS.md` and `GOVERNANCE.md`.
- Read the complete authoritative GitHub prompt supplied for this cycle: `SB-LF06-001-C001_FACTORY_STUDIO_CANONICAL_CORE_WORKSPACE_MIGRATION_PROMPT.md`.
- Read the previous strict PASS audit supplied in the handoff: `SB-LF00-007-C001_GOVERNANCE_AND_COORDINATION_AUTHORITY_NORMALIZATION_STRICT_AUDIT.md`.
- Read the current Factory project contract: `level_factory/README.md`, `level_factory/GOVERNANCE.md`, `level_factory/project.godot`, `level_factory/docs/CLEAN_CHECKOUT_BOOT.md`, and `level_factory/docs/DIRECTORY_BOUNDARIES.md`.
- Read the owner-approved Factory Studio extension specification, the LF/CP migration documents, the retained Semantic Pixel Studio conversion plan, and repository-local historical references relevant to the M06 Studio migration.
- Read every current file under `level_factory/scenes/`, `level_factory/scripts/`, `level_factory/docs/`, and `level_factory/tests/`. The pre-edit project contains only `scenes/bootstrap.tscn` as its scene, `.gitkeep` placeholders for scripts/tests, and the existing boundary documentation.

## Scope and safety boundary before edits

- This cycle is limited to the Factory Studio canonical-Core workspace migration foundation for `SB-LF06-001-C001`.
- The implementation will provide a real Godot workspace shell, deterministic navigation presentation, truthful inert placeholders, and a narrow status-only canonical Python Factory Core gateway boundary.
- `SB-LFX-001..017`, later M06 behavior, solver/QA/provider execution, import/library persistence, metrics, review workflows, batch retry, Content Platform work, and main-game work are out of scope.
- The Python Factory Core remains canonical. No Python algorithm will be copied or reimplemented in GDScript.
- No Magnific, PixelLab, Perchance, provider, network, subprocess, credential, or secret access is permitted.
- No files under `Sekiph82/Scrubbots` will be read or modified.
- No generated owner files will be deleted. The root `TASKS.md` and durable evidence are preserved.

## Pre-edit inventory

- `level_factory/project.godot` points to `res://scenes/bootstrap.tscn`.
- `level_factory/scenes/bootstrap.tscn` is the existing minimal placeholder scene.
- `level_factory/scripts/` and `level_factory/tests/` contain only `.gitkeep` placeholders.
- `level_factory/docs/` contains the clean-checkout and directory-boundary contracts.
- The generated local `level_factory/.godot/` cache is not a source dependency and is not part of the implementation scope.

No implementation, test, documentation, or tracker edit has been made before this log entry.

- The first PowerShell verification used a Unix-newline `StartsWith` assertion and failed because the file was written with Windows CRLF line endings. The file contents were inspected, the exact title and role lines were confirmed, and the verification method was corrected to compare logical lines rather than raw newline bytes.

## 2026-09-15T09:55:00+03:00 — implementation foundation and focused tests

- Updated `level_factory/project.godot` so the real `factory_studio.tscn` is the configured main scene.
- Added the maintainable Studio split: application shell, navigation, workspace page, and `FactoryCoreGateway` status contract under `level_factory/scripts/`.
- Added `level_factory/scenes/factory_studio.tscn` with persistent identity/header, navigation, workspace content, and Core status footer.
- Added `level_factory/docs/FACTORY_STUDIO_WORKSPACE.md` documenting ownership, gateway status contract, run/headless commands, and future extension boundaries.
- Added `tests/unit/test_sb_lf06_001_factory_studio_workspace.py` covering main-scene identity, component split, deterministic navigation, truthful placeholders, offline gateway restrictions, no Core clone/main-game dependency, root tracker/Core protection, and untracked cache policy.
- Focused command: `python -m pytest -q tests/unit/test_sb_lf06_001_factory_studio_workspace.py`.
- Focused result: `8 passed, 1 warning in 0.12s`. The warning is an existing local Windows permission warning from pytest cache creation (`WinError 5`); it did not affect test results.

- Initial prior-regression command failed with six stale assumptions: the old LF00-002/LF00-008 tests required `bootstrap.tscn` as main scene, LF00-002 rejected all `.gd` files, and broad LF00-001/LF00-002 scans treated truthful runtime boundary words as forbidden. No product defect was hidden. The regression tests were narrowly updated to retain their original containment/offline/no-Python/no-sibling checks while accepting the explicitly authorized Studio shell and checking runtime source files for external dependency markers.
- Corrected prior-regression command: `python -m pytest -q tests/unit/test_sb_lf00_001_project_contract.py tests/unit/test_sb_lf00_002_project_boundaries.py tests/unit/test_sb_lf00_006_workspace_policy.py tests/unit/test_sb_lf00_007_governance_authority.py tests/unit/test_sb_lf00_008_clean_checkout_contract.py`.
- Corrected prior-regression result: `36 passed, 1 warning in 1.48s`; the warning is the same local pytest cache permission warning.
- Godot editor/project load command: `godot --headless --path level_factory --editor --quit`; result exit code `0`, Godot `4.7.2.stable.official.ed1daf0bf`, no parse or missing-resource error.
- Godot runtime boot command: `godot --headless --path level_factory --quit-after 1`; result exit code `0`, no parse, missing-resource, provider, network, or sibling dependency error.
- Godot generated local `.uid` files for the new scripts during load. They are owner-local generated files, remain untracked, and were not deleted or added to the implementation.

## 2026-09-15T10:02:00+03:00 — repository regression and offline checks

- Full regression command: `python -m pytest -q`.
- Full regression result: `610 passed, 1 warning in 231.87s (0:03:51)`. The warning is the existing local pytest cache permission warning (`WinError 5`).
- Compile check: `python -m compileall -q src tests` — exit code `0`.
- Import check: `python -c "import scrubbots_pixel_factory; import scrubbots_pixel_factory.cli.main; print('imports ok')"` — exit code `0`, printed `imports ok`.
- Module CLI check: `python -m scrubbots_pixel_factory.cli --help` — exit code `0`.
- Installed CLI check: `scrubbots-pixel --help` — exit code `0`.
- `git diff --check` and `git diff --cached --check` — exit code `0`; staged implementation paths contain no root `TASKS.md` or main-game path.
