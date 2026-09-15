# SB-LF06-001-C001-R01 — Factory Studio Runtime Node Contract Remediation
Document role: CODEX BUILDER LOG

## 2026-09-15T12:10:58+03:00 — pre-edit session start

- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Verified repository root with `git rev-parse --show-toplevel`.
- Verified branch: `main`.
- Starting HEAD and `origin/main`: `c799b443df49569f62766741a04b292144d0f93d`.
- Starting ahead/behind state: `0 0`.
- Starting tracked Git status: clean; four pre-existing/untracked Godot-generated `.uid` owner-local files were preserved and will not be deleted or published.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git` for fetch and push.
- No stash was applied and no sibling repository was searched or used.

## Required authority and evidence reads

- Read current root `TASKS.md` completely. It identifies `SB-LF06-001-C001-R01` as the active `FIX_REQUIRED` remediation and remains uneditable in this cycle.
- Read the complete GitHub strict audit `SB-LF06-001-C001_FACTORY_STUDIO_CANONICAL_CORE_WORKSPACE_MIGRATION_STRICT_AUDIT.md`.
- Read the complete GitHub remediation prompt `SB-LF06-001-C001-R01_FACTORY_STUDIO_RUNTIME_NODE_CONTRACT_REMEDIATION_PROMPT.md`.
- Read the original C001 prompt and finalized C001 builder log.
- Read `level_factory/scenes/factory_studio.tscn`, all current `level_factory/scripts/*.gd`, `level_factory/project.godot`, `level_factory/docs/FACTORY_STUDIO_WORKSPACE.md`, the C001 focused test, and the LF00-001/LF00-002/LF00-006/LF00-007/LF00-008 focused regression tests touched by C001.

## Audit finding and bounded remediation plan

- The strict audit found that the committed scene places Navigation at `Frame/Layout/Body/NavigationPanel/Navigation`, while `factory_studio_shell.gd` resolves `Frame/Layout/Body/Navigation` in both `_ready()` and `_get_configuration_warnings()`.
- The remediation will use one path constant for both runtime lookup and configuration warnings, then add a genuine executable Godot scene-instantiation regression under `level_factory/tests/`.
- The executable regression will load the real main scene, enter it into a tree, allow `_ready()` to run, assert Navigation and Workspace types/paths, assert the signal connection and initial Dashboard/Core status, exercise one inert navigation selection, capture stdout/stderr, and exit non-zero on any assertion or runtime error.
- Existing C001 static guards and required LF00 regressions will remain in scope and be rerun.

## Scope and prohibitions

- Only `SB-LF06-001-C001-R01` is active.
- No `TASKS.md`, root Python Factory Core, provider/network/API/credential/subprocess integration, persistence/database/tracker, main-game, Content Platform, solver, Dashboard, Import, Library, review, batch, or `SB-LFX-001..017` work is authorized.
- The original C001 builder log will not be rewritten.
- No implementation, test, documentation, or tracker edit has been made before this log entry.

## 2026-09-15T12:16:00+03:00 — first executable-regression attempt

- First command attempted: `godot --headless --path level_factory --script res://tests/factory_studio_runtime_contract.gd` inside a PowerShell wrapper that required exit code `0` and rejected `SCRIPT ERROR`/`ERROR:` output.
- The wrapper reported no usable exit code/output, and direct Godot execution returned `0` with only the engine banner and no contract PASS line. This demonstrated that the initial `SceneTree` script entrypoint was not producing executable test evidence; it was not accepted as a passing regression.
- Correction: use a `Node`-based Godot script `_ready()` entrypoint with `get_tree().root`, `get_tree().process_frame`, and `get_tree().quit()`, then rerun the actual command and require the explicit PASS line plus clean output.

## 2026-09-15T12:19:00+03:00 — second executable-regression attempt

- The corrected `Node` script was invoked with `godot --headless --path level_factory --script res://tests/factory_studio_runtime_contract.gd` and again produced only the engine banner with no PASS line, so a script-only invocation was not accepted as executable evidence in this Godot environment.
- Second correction: add a tracked Godot test runner scene whose root Node carries the contract script, and invoke that scene explicitly with `godot --headless --path level_factory --scene res://tests/factory_studio_runtime_runner.tscn`.

## 2026-09-15T12:22:00+03:00 — executable runtime regression passes

- Executable command: `godot --headless --path level_factory --scene res://tests/factory_studio_runtime_runner.tscn --log-file C:\Users\sekip\AppData\Local\Temp\scrubbots-r01-runtime.log`.
- The disposable log captured stdout/stderr: `Godot Engine v4.7.2.stable.official.ed1daf0bf` followed by `SB-LF06-001-C001-R01 runtime contract PASS`; no `SCRIPT ERROR` or `ERROR:` marker was present.
- The explicit Windows command wrapper reported `GODOT_EXIT=0`.
- The executable contract loaded and instantiated `res://scenes/factory_studio.tscn`, entered it into the tree, executed `_ready()`, resolved Navigation and Workspace at their committed paths and types, verified the signal connection, checked initial Dashboard and truthful `UNAVAILABLE` Core status, exercised `Generate` and restored `Dashboard`, and exits with `get_tree().quit(1)` after any failed assertion.
- Focused static command: `python -m pytest -q tests/unit/test_sb_lf06_001_factory_studio_workspace.py`.
- Focused static result: `9 passed, 1 warning in 0.15s`; the warning is the existing local Windows pytest cache permission warning (`WinError 5`).

## 2026-09-15T12:25:00+03:00 — prior-regression harness correction

- Initial prior-regression command: `python -m pytest -q tests/unit/test_sb_lf00_001_project_contract.py tests/unit/test_sb_lf00_002_project_boundaries.py tests/unit/test_sb_lf00_006_workspace_policy.py tests/unit/test_sb_lf00_007_governance_authority.py tests/unit/test_sb_lf00_008_clean_checkout_contract.py`.
- Initial result: `34 passed, 2 failed, 2 warnings in 9.64s`. The failures were harness scope only: LF00-002's prior C001 allowlist correctly rejects a new `.gd` implementation file, and LF00-008 sees the new runner scene as not yet tracked. No product/runtime defect was indicated.
- Correction: preserve all prior LF00 tests unchanged, remove the temporary nested runner/script, and place the equivalent executable Godot contract under `tests/support/` as an explicitly invoked absolute script against the nested `level_factory` project. This stays within the R01 equivalent executable-contract allowance and avoids broadening prior-cycle test ownership.

## 2026-09-15T12:29:00+03:00 — corrected executable contract invocation

- The root support script is executed from the nested project directory with: `godot --headless --script <absolute-repo-root>\tests\support\factory_studio_runtime_contract.gd --log-file <temporary-log>`.
- Captured result: `Godot Engine v4.7.2.stable.official.ed1daf0bf` followed by `SB-LF06-001-C001-R01 runtime contract PASS`; no `SCRIPT ERROR` or `ERROR:` marker was present.
- The Windows command returned `0` for the successful contract. The prior LF00 test suite remains unmodified and can now see only its original nested project source set.
- Corrected prior-regression command: `python -m pytest -q tests/unit/test_sb_lf00_001_project_contract.py tests/unit/test_sb_lf00_002_project_boundaries.py tests/unit/test_sb_lf00_006_workspace_policy.py tests/unit/test_sb_lf00_007_governance_authority.py tests/unit/test_sb_lf00_008_clean_checkout_contract.py`.
- Corrected prior-regression result: `36 passed, 1 warning in 1.81s`; the warning is the existing local pytest cache permission warning (`WinError 5`).
- After moving the executable contract to root `tests/support/`, the focused command was rerun: `python -m pytest -q tests/unit/test_sb_lf06_001_factory_studio_workspace.py` — `9 passed, 1 warning in 0.12s`, with the same local pytest cache permission warning.

## 2026-09-15T13:00:00+03:00 — full regression and toolchain checks

- Full regression command: `python -m pytest -q`.
- Full regression result: `611 passed, 1 warning in 343.39s (0:05:43)`. The warning is the existing local pytest cache permission warning (`WinError 5`).
- Compile check: `python -m compileall -q src tests` — exit code `0`.
- Package import smoke: `python -c "import scrubbots_pixel_factory; import scrubbots_pixel_factory.cli.main; print('imports ok')"` — exit code `0`, printed `imports ok`.
- Module CLI help: `python -m scrubbots_pixel_factory.cli --help` — exit code `0`.
- Installed CLI help: `scrubbots-pixel --help` — exit code `0`.
- Godot editor/headless check: `godot --headless --path level_factory --editor --quit` — exit code `0`, Godot `4.7.2.stable.official.ed1daf0bf`, no parse or missing-resource error.
- Corrected executable runtime command from the nested project directory: `godot --headless --script ..\tests\support\factory_studio_runtime_contract.gd --log-file %TEMP%\scrubbots-r01-runtime.log`.
- Runtime stdout/stderr capture: engine banner, `SB-LF06-001-C001-R01 runtime contract PASS`, and `GODOT_EXIT=0`; no `SCRIPT ERROR` or `ERROR:` marker.

## 2026-09-15T12:30:37+03:00 — remediation implementation checkpoint

- Remediation implementation commit: `bef6a974317e06792e882f5a645e3f6a8416c233` (`SB-LF06-001-R01 repair Studio runtime node contract`).
- The commit contains only the bounded shell path repair, executable runtime evidence, focused static-test strengthening, narrow runtime-command documentation, and this R01 log.
- Post-commit status is one commit ahead of `origin/main`; only the four pre-existing/generated local `.uid` files remain untracked and were not deleted or staged.
- Root `TASKS.md`, root `src/`, the main-game repository, and provider/network surfaces remain unchanged.

## 2026-09-15T12:31:15+03:00 — observed publication/equality checkpoint

- Pushed remediation implementation plus builder-evidence checkpoint successfully: `c799b44..d1b7c04` on `main -> main`.
- Observed local HEAD and `origin/main` equality after that push: `d1b7c04044e2b7e1fd3e6c39df8d07b7d3568583`; ahead/behind `0 0`.
- This is the last pushed equality checkpoint before the final log-only publication record below; no earlier commit is called terminal while another builder commit remains planned.

## Terminal log publication note

- The final log-only commit will publish this record and will be verified against `origin/main` after push. The preceding observed equality checkpoint is recorded above rather than making a self-referential SHA claim.
