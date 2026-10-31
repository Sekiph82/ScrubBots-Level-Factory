# Codex task: gate the ScrubBots Factory Studio release pool on the game's real-play check

Document role: CODEX BUILDER LOG

## Start and authorization

- Started: 2026-10-31 16:30 UTC.
- Owner authorized this exact side task in the active Codex conversation: add it as a Factory task and implement it. Source specification: `C:\Users\sekip\Desktop\ScrubBots\factory\jobs\081-real-play-file-cli\CODEX_PROMPT_STUDIO_REAL_PLAY_GATE.md`.
- Existing goal objective file was read and left unchanged. Root `TASKS.md` now identifies SB-STUDIO-REAL-PLAY-GATE-081 in its current/next fields; queue guard passed after publication.

## Canonical checkout and starting Git state

- Repository: `Sekiph82/ScrubBots-Level-Factory`; canonical root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Branch: `codex/sb-lfx-018-r05-v13-cd-recovery-20261021` (publishes by normal `HEAD:main`).
- Starting HEAD and `origin/main`: `bcfe8ab30387ce9563941796525e1aeb38afd19f`, equal, 0 ahead / 0 behind after `git fetch --prune origin`.
- Starting tracked worktree clean; 3,471 pre-existing untracked entries (mostly owner Release files), 18 pre-existing stashes and one canonical worktree. All are preserved; no cleanup, stash, reset, rebase, clone or worktree operation was used.
- Game checkout is read-only. It was independently verified at current game `main` `7b068a8bd1a2aa135334af466796bd70bb3ae2ed`; its existing dirty status was unchanged by the prior CLI run recorded in the parent goal builder log.

## Governing files read

- Existing goal objective attachment (read-only), root `TASKS.md`, `AGENTS.md`, `CLAUDE.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, and the stable owner-goal prompt `.hiveai/prompts/SB_LFX_OWNER_GOAL_CONTINUOUS_EXECUTION_20261031.md`.
- Exact user-supplied 081 task prompt above. It requires a real `real_play_v1` fail-closed acceptance gate in addition to `SOLVED` + replay `WIN`, hash-bound evidence, robust subprocess/result validation, and focused fake-CLI coverage. It forbids edits to the ScrubBots game repository and changes to game semantics.
- Existing game `AGENTS.md` file-mode contract and `tools/real_play_file.gd` were read. A no-`--out`, no-`--search` execution of the installed crab candidate returned exit 1 / `LOST`, stuck at click 27; result and hashes are recorded in the parent goal log. This was read-only and did not change game-repo status.
- Factory policy: zero CI/Actions and paid test services; bounded local checks only; no TEMP worktree, mass regression, Production/R2 writes, paid providers, uncontrolled GUI, or owner-data edits. Installed Release remains unchanged because its source manifest is not current.

## Pre-implementation command notes

- First queue-guarded status commit helper compared the tab-separated ahead/behind output to a space-separated literal and correctly aborted before commit/push. Corrected by splitting on whitespace; the TASKS authorization commit then pushed normally and was fetched/verified.
- First TASKS field locator expected `- Next Task/Action:` although the live field carries a bracketed date; it raised `StopIteration` before writing. Corrected to match the field prefix; only the three delegated live status fields changed, `git diff --check` passed, and no historical TASKS entry changed.
- Initial implementation review found the Settings dialog remains the only UI surface; no new production screen or owner-facing card was added. Godot 4.7.2 `--headless --path . --check-only --script res://level_factory/scripts/factory_studio_exact_ui.gd` parsed the edited Studio UI script with exit 0 and no generated project cache. The executable `--help` confirmed `--check-only` is parse-only.

## Scope and safety decisions

- Implement the gate in canonical Factory Studio source and focused tests, preserving the existing `SOLVED` + replay `WIN` gate.
- Preserve owner Release contents and the installed Release copy; do not make it appear source-current by altering its manifest. Do not write to the game repository or candidate evidence during tests unless the exact test fixture is a bounded repo-local fixture owned by this task.
- No workflow, runtime network dependency, credential, provider, R2 or Production change is authorized by this task.

## Implementation and verification

- Added `src/scrubbots_pixel_factory/supply_pipeline/real_play_gate.py`. It resolves Studio/environment/default settings (including `SCRUBBOTS_PROJECT` compatibility), verifies the configured checkout contains the game project and file-mode script, requires Godot 4.7.2, validates exact Factory-contained level/plan inputs and JSON hashes, launches the game via argument-list subprocess with `shell=False`, compares stdout marker data to `--out`, validates verdict/exit/path/ID/hash/commit and robust per-dt evidence, and stores the evidence next to the exact level and plan. LOST or canonical-only runs may trigger bounded game search; the adapter splices only `intendedColumnClicks`, reruns without search and requires `WON_ROBUST`. Failure is closed with explicit error detail. Result symlinks are rejected before path resolution.
- `release_pool.enter_release_pool()` now requires canonical solver `SOLVED` and replay `WIN` before real-play; only a verified robust result can create an entry. It binds the exact result file and level/plan hashes into pool evidence. Reads validate stored real-play evidence and its current file hashes while older entries without the new proof remain historical records, not newly created passes.
- Extended the existing Settings dialog with the ScrubBots checkout, Godot console executable, and timeout settings. It honors `SCRUBBOTS_REPO`, legacy `SCRUBBOTS_PROJECT`, `GODOT`, and timeout environment fallbacks; it adds no production screen.
- Added `tests/unit/test_sb_studio_real_play_gate_081.py` for fake-CLI pass/search/reject cases, settings, malformed/mismatched output, timeouts, path/hash authority and release-pool acceptance. Updated existing pool fixtures to supply `SOLVED` + replay `WIN`; the profile-pool READY fixture now uses its canonical candidate folder name and mocked immutable owner-source verification so it exercises the release writer without touching owner source files.
- Focused passing command (49 passed in 2.60s): `python -B -m pytest -p no:cacheprovider --basetemp=tests/.codex-real-play-gate-focus3 -q tests/unit/test_sb_studio_real_play_gate_081.py tests/unit/test_sb_lfx_018_r09_r02_r04_r01_profile_pool.py tests/unit/test_sb_lf01_009_010_candidate_and_semantic_contracts.py tests/unit/test_sb_lfx_018_r05_ready_auto_publisher_authority.py`.
- Focused broader command including restore evidence (52 passed, 2 failed in 42.94s): `python -B -m pytest -p no:cacheprovider --basetemp=tests/.codex-real-play-gate-focus2 -q tests/unit/test_sb_studio_real_play_gate_081.py tests/unit/test_sb_lfx_018_r09_r02_r04_r01_profile_pool.py tests/unit/test_sb_lf01_009_010_candidate_and_semantic_contracts.py tests/unit/test_sb_lfx_018_r09_r02_r04_restore_pool.py tests/unit/test_sb_lfx_018_r05_ready_auto_publisher_authority.py`. The two failures are `test_latest_002_ready_run_restores_only_when_all_saved_identity_hashes_match` (current owner fixture returns `SOURCE_ONLY`, expected `READY`) and `test_existing_002_accept_is_idempotent_and_does_not_create_duplicate_receipt` (current owner fixture has no prior `ACCEPT`). They are outside the real-play changes and were not altered.
- Fixture-debug history: the first broad run exposed a bad fixture candidate directory name; correcting the bounded test fixture then exposed that its immutable owner source must be mocked as source verification. The corrected exact writer test passed (`1 passed in 0.48s`), and the subsequent focused package passed 49/49. Initial test run had 19 passed / 1 failed because the expected plan digest used text-mode newline translation; the assertion now hashes normalized raw bytes and the new suite passed 20/20 (`python -B -m pytest -p no:cacheprovider --basetemp=tests/.codex-real-play-gate-081-r2 tests/unit/test_sb_studio_real_play_gate_081.py -q`).
- Game CLI, owner Release files, installed Release, and R2/Production paths were not written by these tests. No hosted CI, Actions, paid service or mass regression was run. Local evidence does not establish owner GUI/game acceptance or hosted CI.

## Final implementation commit

- Exact production hook: `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py::enter_release_pool`; repository search found this as the sole `scrubbots-release-pool-entry/v1` writer. `release_entries()` filters legacy rows without real-play proof and validates current result, level and plan hashes before exposing a row as ready.
- Settings are in the existing Studio `Settings` dialog in `level_factory/scripts/factory_studio_exact_ui.gd`: `scrubbotsRepoPath`, `godotExe`, `realPlayTimeoutSeconds`, backed by `SCRUBBOTS_REPO` (legacy `SCRUBBOTS_PROJECT` fallback), `GODOT` and `SCRUBBOTS_REAL_PLAY_TIMEOUT_SECONDS`.
- Release Pool entry evidence includes `real_play.model`, `verdict`, `exitCode`, `planSha256`, `levelSha256`, `gameCommit`, `resultFile`, `resultSha256`; `files.real_play_result` stores the output path and byte SHA-256. The plan file list/hash is computed after any safe click-order correction and final no-search rerun.
- Implementation/test commit: `5cefbbeb` (`Gate Studio release pool on robust real play`), six scoped files, 1,065 insertions / 8 deletions. `git diff --cached --check` passed before commit. The builder log is committed separately.
- The read-only task queue guard was attempted while implementation files were modified and rejected as designed (“Tracked working-tree changes exist”); no task selection or tracker write occurred. It can be rerun after implementation/log commits and before the delegated completion update.
- Eight uniquely named repo-local pytest basetemp directories were created by the bounded checks. Their exact absolute paths were enumerated and verified under `tests/`, but the shell policy rejected both removal attempts; they remain untracked and were excluded from commits. All pre-existing owner untracked files remain untouched.
- Review limitations: the task's optional real-game integration sequence was not rerun here; the exact installed crab candidate's read-only CLI `LOST` / click 27 evidence and game `main` SHA are recorded above and in the parent goal log. The focused fake-CLI suite is the builder proof for the new adapter. The two broader restore-fixture failures remain explicitly unresolved and out of scope.
