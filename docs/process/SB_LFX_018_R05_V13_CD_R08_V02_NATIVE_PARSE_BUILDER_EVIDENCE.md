# SB-LFX-018 R05 V13-C/D R08 V02 | Native Godot Parse Builder Evidence
Document role: CODEX BUILDER EVIDENCE

## Scope and starting state

- Task: `SB-LFX-018 R05 V13-C/D R08 V02`, using `.hiveai/prompts/SB_LFX_018_R05_V13_CD_R08_V02_REAL_GODOT_ENGINE_WHITELIST_NATIVE_PARSE.md` and retaining the V22 independent audit as read-only authority.
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- The desktop task branch fast-forwarded from `bb6bed5247eb1f34bc39fb79c26c96d1d8246179` to `674f7fad41e53486a9701cfba03c127001ac3e13`, matching `origin/main` at 0 ahead / 0 behind. Incoming paths were only the revised R08 V02 prompt and `TASKS.md`; existing untracked owner paths were preserved and not staged.
- `python -B scripts/codex/scrubbots_task_queue.py --json` validated the explicit R08 V02 task and exact prompt URL. `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the sync/publish standard, V02 prompt and V22 audit were read; no tracker, prompt or audit edit was made.

## Engine identity and permitted test

- One exact-name read-only CIM filter for real Godot engine names (`Godot.exe` / `Godot_v*.exe`) returned `TRUE_GODOT_ENGINE_PROCESS_COUNT=0`. `godot-ai.exe` helpers were not treated as engine processes and were not stopped, restarted or otherwise touched. The historical PID 13860 was not queried.
- Existing binary: `C:\Users\sekip\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_Microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64.exe`; file product version `4.7.2.stable.official`; native output identified `4.7.2.stable.official.ed1daf0bf`. The install has no `_sc_` marker and no adjacent `editor_data` directory.
- Selected existing source: `res://scripts/factory_studio_exact_ui.gd`. Invocation was one finite `--headless --path <canonical level_factory> --script res://scripts/factory_studio_exact_ui.gd --check-only` parse, with stdout/stderr captured in memory and a 30-second bound. No `--editor`, `--import`, GUI, test suite, solver, batch, or owner data script execution was requested.
- Initial real parse returned exit 1 with `SCRIPT ERROR: Parse Error: Expected closing ")" after call arguments` at `factory_studio_exact_ui.gd:3777`. Inspection found the preceding `dialog.custom_action.connect(func(action: String):` lambda lacked its closing `)`. A one-character closing delimiter was added immediately before `dialog.confirmed.connect`; this was the only product source edit.
- The same bounded native parse was run after that narrow fix and exited 0. Stdout contained the Godot 4.7.2 engine banner; stderr was empty. Result: `R08_REAL_GODOT_SINGLE_SCRIPT_PARSE_PASS`. The first failed parse and correction remain recorded; no other test was run.

## Integrity observations

- `level_factory/project.godot` SHA-256 before/after: `4ADB4B9B939D8AF178516E86A170AB1E8D725F32D8B4D3F1B8464E4759C655C7`.
- Corrected `factory_studio_exact_ui.gd` SHA-256 before/after the passing parse: `D54A00B6B7808391FEE1D51433DC06765F6A31EE68E55EA2EE7124C924246C8B`. The pre-fix file at the failed parse had SHA-256 `7C4DE3F4B716F13FEADE5BBB48529A754891FD82233D25C47AC96B1FADBE0A5E`.
- Existing `level_factory/.godot` inventory: 273 files / 1,947,130 bytes; path-size-mtime inventory SHA-256 before/after both `76BBE338BDAB1E2C4B22E4178450A0A90CE48CF08E2E162F431454E356597565`.
- Existing project `.uid` / `.import` sidecar inventory: 614 entries; path-size-mtime inventory SHA-256 before/after both `FBE748CC858A27A0733D9601AD7B2FCCC9FA8C610930ECA922191BA635CCD400`.
- These are path/size/timestamp inventory hashes, not content hashes for every cached file. `--check-only` parses but does not execute the selected script; the owner job, Pool, Release files and 140 PNG source set were not opened or processed by the parse. No Release file, owner job/Pool record, PNG, manifest or generated cache/sidecar changed in the captured project scope.

## Limits and publication

- This proves only that the selected GDScript parses under the existing Godot 4.7.2 binary. It does not prove all scenes/imports, runtime UI behavior, installed Release correctness, solver behavior, full regression, writer exclusion, or owner visual acceptance.
- No CI/Actions, paid service, `Release -Apply`, R2, production, owner data mutation, 140 PNG operation, process termination, TEMP sandbox, clone or worktree was used.
- Source fix, this evidence report and the append-only M03 builder log are the only intended tracked changes. Final commit and remote parity receipts follow in the builder log.
