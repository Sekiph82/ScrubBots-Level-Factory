# MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01 — Durable Local Install + Real Desktop Shortcut Launch

Document role: CODEX BUILDER LOG

## Chronological record

### Start and safe synchronization — 2026-10-08 10:43:55 +03:00

- Canonical persistent root: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator; verified canonical origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git, branch main.
- Persistent checkout HEAD at first preflight: 7c6051589d0a95fc785d7f182ccd0d7f8d7013ce; it had extensive tracked modifications and untracked owner files, and after fetch was 0 ahead / 474 behind. It was preserved byte-for-byte; no checkout, stash, reset, restore, clean, or merge was run there.
- First fetch observed origin/main=aa98cb3946d018ab1d19b23512748fca1d5dcb4f. A clean detached task worktree was created at %TEMP%\ScrubBots-Level-Factory\MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01-20261008 at that revision. The initial shell operation was interrupted after worktree creation; a follow-up read confirmed the worktree was clean at a98cb3 and had the canonical origin.
- At task execution start, fetched origin/main; it had advanced by 12 commits to 9b23914388c52b332336ebde9deb1612c79f989. The clean detached worktree was safely fast-forwarded with git merge --ff-only origin/main; it is now exact-current and clean, 0 ahead / 0 behind.
- Existing stashes/worktrees were inventoried and left untouched.

### Authority and contracts read

- Root TASKS.md confirms current task MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01, authorized actor CODEX, status STRICT_AUDIT_CHANGES_REQUIRED / R01_AUTHORIZED / BEFORE_M17.
- Read AGENTS.md, CLAUDE.md, GOVERNANCE.md, docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md, the active R01 prompt, .hiveai/audits/MAINT_FACTORY_STUDIO_LAUNCHER_C001_STRICT_AUDIT_V01.md, and the R01 audit criteria.
- Active prompt and prior audit require retaining accepted icon/application/header/launcher behavior, moving the installed runtime out of TEMP, preserving unknown owner data, proving TEMP independence, executing the real Desktop shortcut and only closing the process created by this smoke, adding focused regression tests, publishing implementation and builder log separately by normal fast-forward push, and returning the builder-log URL.
- No implementation, test, documentation, or governance edits have been made before creating this log.

### Implementation and verification

Pending.

### Focused regression failure and correction in progress

- Command: `python -m pytest -q tests/unit/test_maint_factory_studio_launcher_c001.py tests/unit/test_sb_lf06_001_factory_studio_workspace.py tests/unit/test_sb_lf06_002_factory_studio_target_controls.py tests/unit/test_sb_lf06_012_factory_studio_editor_smoke_and_headless_core_test_gate.py` — **23 passed, 1 failed**. Existing LF06-012 Studio smoke reported a missing imported PNG resource (`res://assets/icons/ScrubBots_Factory_Studio_256.png`) in the fresh Godot cache. Investigating the clean-checkout import precondition before rerunning; this failure is retained.

- Corrective import command: `godot --headless --editor --path level_factory --quit` — exit 0; the PNG and `.import` sidecar were present, but this fresh worktree had no `.godot` import cache.
- Reran the same focused launcher/icon/Studio regression command after import — **24 passed**. The first failing result above remains recorded.
- Godot generated 51 `.gd.uid` sidecars in the initially clean worktree; verified the exact set was confined to `level_factory/scripts` and `level_factory/tests`, removed only those 51 newly generated files, and refreshed the `.import` index entry after confirming its blob diff was empty. Ignored `.godot` cache was retained.

### Full regression — 2026-10-08

- Full command with explicit authority: `$env:SCRUBBOTS_PROJECT=C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\MAINT-FACTORY-STUDIO-LAUNCHER-C001-GAME-AUTHORITY; python -m pytest -q` — **1722 passed, 6 skipped, 2 failed in 1195.30s**. This result is retained as a failure.
- Failure 1: `tests/integration/test_sb_cpx_002_current_main_godot_integration.py::test_exact_verified_staging_pack_replays_with_current_main_godot` observed the game checkout `HEAD=adfeba0...` while its `origin/main` advanced to `5a7ba65...` during the run (`INVALID_GAME_AUTHORITY_CHECKOUT`). The game checkout was clean and behind-only; fetched latest main and fast-forwarded it to `d5eead7d08aa3a05ad01e8553ef8a3a2c2a7312c`, then reran that exact test with the same explicit `SCRUBBOTS_PROJECT`: **1 passed in 35.13s**.
- Failure 2: `tests/unit/test_sb_lf00_007_governance_authority.py::test_current_tasks_rows_are_parser_safe_and_declared_denominator_matches` — fetched root `TASKS.md` declares 248 but parser finds 250 rows after SB-LFX-018/019 additions. Root `TASKS.md` is protected and remains untouched; no tracker/test workaround was applied.
- Full-run skips: slow supply pipeline (`SCRUBBOTS_SLOW=1`), owner R2 credential, and four optional canonical-game bridge capabilities, with exact pytest reasons preserved in the tool output.

- Final focused command after idempotent-repair additions: launcher/icon/Studio four-suite command — **25 passed in 2.71s**.
- PowerShell parser — **PASS** (2,344 tokens). `python -m compileall -q .` — **PASS**. `git diff --check` — **PASS**. Changed-file credential-pattern scan for AWS access keys, common GitHub/OpenAI-like tokens, private-key headers and Slack tokens — **PASS, no matches**. No dependencies or licenses changed.

### Published implementation install attempt and correction

- Implementation/test commit `8a4d7e111be4dfc83eb7ed8f19c4860a389bdc68` was pushed normally to `main`; post-push local `HEAD == origin/main`, clean tracked tree.
- First execution of the committed installer failed closed at canonical-origin validation before creating the runtime or changing the Desktop shortcut. Diagnostic command showed the canonical remote string was correct; PowerShell's native-command pipeline had cleared `$LASTEXITCODE` because `Select-Object` followed the command. Corrected the installer to capture the exit code immediately after `git remote get-url origin`, and added a focused assertion. No runtime files or shortcut fields were changed by the failed attempt.

- After the canonical-origin exit-code correction was published as `fafd7dd0b4b5c206aa05ced1bc4dfdc78147fed2`, installer execution succeeded. COM readback confirmed the shortcut target is Windows PowerShell, arguments/WorkingDirectory point only to the exact authorized Release runtime, description is unchanged, and the icon points to the stable runtime copy. Owner and runtime ICO SHA-256 both equal `06049274E80487BED3C23F1CC9D549B5F17F851132B2E5361F4EDA7D0ECB93FA`; install marker revision equals published `fafd7dd...`; 1,991 tracked files were installed.
- Second install preserved a temporary unknown owner-output sentinel. It exposed an idempotency defect: Windows PowerShell `ConvertFrom-Json` parses ISO timestamps into DateTime, then locale formatting changed the manifest bytes on repair. The test stopped before removing the exact probe file. Removing the optional timestamp from the local install manifest; source revision and per-file hashes remain the deterministic identity.

### Stable runtime and real Desktop shortcut evidence — 2026-10-08

- Installer was rerun after publishing final installer revision `e936b54025973c5094b5dc9669d0e36e1687a062`. Install marker `sourceRevision` exactly equals that published revision; 1,991 tracked repository files were installed. Owner-source ICO and stable runtime ICO are byte-identical at SHA-256 `06049274E80487BED3C23F1CC9D549B5F17F851132B2E5361F4EDA7D0ECB93FA`.
- A second repair run with a unique owner-output probe preserved its bytes and produced an unchanged install-manifest SHA-256. The probe was then removed by its exact path after the preservation assertion. No unknown files were overwritten or removed. The install script retains only managed app files in its manifest and preserves unrelated runtime files.
- COM readback of `C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk` after repair:
  - TargetPath: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
  - Arguments: `-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio\scripts\launch_factory_studio.ps1"`
  - WorkingDirectory: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`
  - Description: `ScrubBots Factory Studio`
  - IconLocation: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio\level_factory\assets\icons\ScrubBots_Factory_Studio.ico,0`
  - No shortcut field contains TEMP; launcher, project and icon all exist in the stable runtime.
- Godot 4.7.2 stable runtime import: `godot --headless --editor --path <stable runtime>\level_factory --quit` — PASS (`$? = True`). Direct headless boot: `godot --headless --path <stable runtime>\level_factory --quit` — PASS (`$? = True`). An initial wrapper check incorrectly treated empty `$LASTEXITCODE` as failure; both commands emitted only the Godot version banner and passed when checked using PowerShell's success flag. This false alarm is recorded.
- TEMP independence: renamed the implementation directory to `...-TEMP-OFFLINE-PROOF`, verified the original path was absent, then COM-read the shortcut and confirmed every referenced launcher/project/icon file existed outside TEMP. While the implementation path was unavailable, started the actual Desktop `.lnk`. New process PID `19400`, `Godot_v4.7.2-stable_win64.exe`, command line used `--path "C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio\level_factory"`, no `--editor`, window title `ScrubBots Factory Studio (DEBUG)`. `CloseMainWindow()` returned `True`; PID exited. Seven pre-existing Godot processes were inventoried and left untouched. Restored the TEMP worktree to its original path for log publication.
- The only owner-checkout deployment write was the authorized new `Release\ScrubBots Factory Studio` subtree; the existing Desktop shortcut was repointed as requested. No other owner source files were edited by this task.

### Final verification and publication state

- Product files changed: `scripts/install_factory_studio_shortcut.ps1`; `tests/unit/test_maint_factory_studio_launcher_c001.py`.
- Builder evidence file: `.hiveai/codex-logs/MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01_DURABLE_INSTALL_CODEX_LOG.md`.
- Focused launcher/icon/Studio suites: **25 passed** after final installer changes. PowerShell parser: PASS. `python -m compileall -q .`: PASS. `git diff --check`: PASS. Changed-file credential-pattern scan: PASS, no matches. No dependency or license changes.
- Full pytest result remains **1722 passed, 6 skipped, 2 failed in 1195.30s**. The game-authority race failure was resolved by fast-forwarding the clean TEMP ScrubBots checkout to current `origin/main` and rerunning the exact CPX-002 integration test: **1 passed**. The other failure remains outside launcher scope and cannot be fixed by the builder: `tests/unit/test_sb_lf00_007_governance_authority.py::test_current_tasks_rows_are_parser_safe_and_declared_denominator_matches` finds 250 task rows while protected live `TASKS.md` declares 248. `TASKS.md` was not edited. The six skips and reasons are listed above. Therefore full-suite regression is not green and no builder acceptance claim is made.
- Published implementation commits (normal fast-forward pushes, in order): `8a4d7e111be4dfc83eb7ed8f19c4860a389bdc68`, `fafd7dd0b4b5c206aa05ced1bc4dfdc78147fed2`, `e936b54025973c5094b5dc9669d0e36e1687a062`.
- The builder log is the separate evidence publication after the implementation commits above. The final pushed `main` SHA and parity are reported in the handoff.
- Immediately before log publication, the detached execution worktree was at `e936b54025973c5094b5dc9669d0e36e1687a062`, equal to `origin/main` with 0 ahead / 0 behind; the builder log was the only untracked path. Post-log push parity is reported in the handoff.

## Builder disposition

Stable installation, shortcut durability, TEMP independence, real shortcut launch and focused tests are demonstrated. Full repository regression remains blocked by the protected task-denominator mismatch above; this record is ready for independent review and does not declare acceptance.

- Builder-log pre-staging integrity check caught two NUL bytes in the recorded divergence counts where the intended digit `0` belonged. Replaced only those two bytes, confirmed UTF-8 text, and rechecked the staged log diff.
