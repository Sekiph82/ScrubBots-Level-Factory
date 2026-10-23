# SB-LFX-018 R05 V13-C/D R08 V03 | ONE-TIME WINDOWS GODOT CACHE OWNER PERMISSION GATE
Document role: CODEX BUILDER EVIDENCE REPORT

Date: 2026-10-23 (Europe/Istanbul)
Repository: `Sekiph82/ScrubBots-Level-Factory`
Canonical checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Authoritative prompt: [R08 V03 one-time Godot global-cache permission gate](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB_LFX_018_R05_V13_CD_R08_V03_ONE_TIME_GODOT_GLOBAL_CACHE_OWNER_GATE.md)
Previous independent audit: [V22 R07 staged-inventory/native strict audit](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R07_STAGED_INVENTORY_NATIVE_STRICT_AUDIT_V22.md)

## Authority and synchronization

- The owner explicitly approved the exact one-time possible-write scope in chat: `%APPDATA%\Godot`, `%LOCALAPPDATA%\Godot`, `%TEMP%\Godot`, and project-local Godot-generated `.godot`, `.uid`, and `.import` paths for one source-script parse. This did not authorize Release installation, GUI acceptance, provider use, CI, batch replay, or data cleanup.
- Starting execution branch was `codex/sb-lfx-018-r05-v13-cd-recovery-20261021` at `585d60e0ebc0f61576130397fb0d11f7ed964033`; fetched `origin/main` was `e3d365ba239fe6da6e3f1a276ee37671dc9050e2`. The task queue initially refused the diverged checkout. Read-only `git diff`/`git merge-tree` showed disjoint tracked paths and no conflicts. At the owner's direction, `git merge --no-edit origin/main` preserved both histories and all owner-untracked files; merge HEAD became `a882ca2a436a93c64ced206024a8cb73a07f9cba`. The required `python -B scripts/codex/scrubbots_task_queue.py --json` then validated R08 V03 and its exact prompt pin, with origin SHA `e3d365ba239fe6da6e3f1a276ee37671dc9050e2`.
- Read `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, sync/publish standard, exact V03 and V02 prompts, V22 audit, R07-C evidence, existing M03 builder log, source project and prior V02 evidence. No tracker, prompt or audit was edited.

## Process and binary gate

- One fresh read-only CIM snapshot used an exact true-engine name filter. `TRUE_GODOT_ENGINE_PROCESS_COUNT=0`. There were 11 `godot-ai.exe` helper processes; they were not classified as engines or modified. No direct true-engine child of those helpers was observed. No process was terminated.
- Existing binary: `C:\Users\sekip\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_Microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64.exe`; file product version `4.7.2.stable.official`; length 180,858,888 bytes. No `_sc_` marker or adjacent `editor_data` directory was present.
- A bounded before/after SHA-256 inventory covered 21,440 files before the invocation and 21,441 after. Scope included the three named Godot global roots, project `.godot` files and project `.uid`/`.import` sidecars, the target source/project file, six named Release manifests, the exact durable job, 131 Release Pool JSON files and the Release owner-upload tree. The comparison found no changes in project source/cache/sidecars, manifests, job, Pool, or owner-upload files. The after inventory's one net additional file was in `%APPDATA%\Godot`.

## Native parse

- Exactly one current R08 V03 native parse was invoked; no import, editor GUI, scene launch, solver, batch, or other test suite ran.
- Command: `Godot_v4.7.2-stable_win64.exe --headless --path "C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\level_factory" --script res://scripts/factory_studio_exact_ui.gd --check-only`.
- Exit code: `0`; elapsed: `0.43` seconds; stdout: `Godot Engine v4.7.2.stable.official.ed1daf0bf`; stderr empty. Result: `R08_REAL_GODOT_SINGLE_SCRIPT_PARSE_PASS`.
- This proves parsing of this one existing GDScript only. It is not whole-project import, runtime UI, installed Release, solver, writer-exclusion, or owner visual acceptance.

## Observed global Godot side effects

The same inventory comparison observed changes only beneath the approved `%APPDATA%\Godot` tree:

- Added during the post-run inventory: `app_userdata\ScrubBots Factory Studio\logs\godot2026-10-23T10.55.46.log`, `app_userdata\SCRUBBOTS\.recovery_mode_lock`, and two `SCRUBBOTS\logs\godot2026-10-23T10.55.*.log` files.
- Existing `app_userdata\SCRUBBOTS\logs\godot.log` changed.
- Three pre-existing dated log files disappeared: `godot2026-10-22T23.23.47.log`, `godot2026-10-22T23.23.49.log`, and `godot2026-10-20T20.50.15.log` (the last under `ScrubBots Factory Studio\logs`, the first two under `SCRUBBOTS\logs`). The per-file pre-run hashes were compared in memory but were not retained in the command result.
- A follow-up hash-only check found `.recovery_mode_lock` no longer present. Current hashes were captured for the four remaining affected log files; log contents were not read or emitted. No attempt was made to restore deleted logs, remove generated files, or otherwise clean up. The exact attribution/timing of the log removals and transient lock disappearance is not independently established; they are disclosed as observed global-scope changes.
- Follow-up current SHA-256 values: `ScrubBots Factory Studio\logs\godot2026-10-23T10.55.46.log` = `6d1c065383a27c36804949b6ffa4b09714470b112e5dacc0bd5aeb7b9c147c4e`; `SCRUBBOTS\logs\godot2026-10-23T10.55.12.log` = `1f50bcb74a5d35a5fbef2209844e317896e3c6f988a13f78ca9332b6bf46bd7f`; `SCRUBBOTS\logs\godot2026-10-23T10.55.40.log` = `024b2969450ed1bfa8ee844688978f49dabf7526dfc26f6e764bfb65dc086d3d`; `SCRUBBOTS\logs\godot.log` = `d8d5d0203e716a27e4bb8bef4fbc867e180b58edba95682174905a3fc9c96451`. The first is 73 bytes; the others are 1,986, 1,311 and 1,311 bytes respectively.
- The first baseline attempt stopped at its 5,000-file cap (`%LOCALAPPDATA%\Godot`: 5,001 files enumerated, 68,743,035 bytes). It did not launch Godot. A subsequent standalone inventory exceeded the tool's 30-second output window; its PowerShell process exited naturally, and its result was not used. The integrated bounded before/after inventory completed successfully. A follow-up hash command first had a PowerShell parser error before execution; the corrected read-only command returned current hashes.

## Limits and disposition

- No source or product file was changed in this V03 execution. No cache cleanup or owner-data restoration was attempted. The global log removals are an unexpected side effect requiring owner awareness; no further Godot invocation is authorized by this one-time approval.
- No CI/Actions, paid provider, R2, Release `-Apply`, installed GUI, TEMP scratch, worktree, clone, process termination, or 140-item replay was used.
- Existing `INSTALL_BLOCKED_MANIFEST_DRIFT`, `PROCESS_QUIESCENCE_UNPROVEN`, `RELEASE_APPLY_NOT_AUTHORIZED`, `INSTALLED_GUI_OPEN`, and owner visual acceptance gates remain unchanged.
