# SB-LFX-018 R05 V13-C/D R08 V02 | GERÇEK GODOT MOTORUNU HEDEFLE, godot-ai.exe'Yİ ENGEL SAYMA
Document role: GPT AUTHORIZED CODEX HANDOFF | REVISION of active R08 only
Date: 2026-10-23 Europe/Istanbul
Repo: https://github.com/Sekiph82/ScrubBots-Level-Factory
Canonical Desktop: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Single tracker: root `TASKS.md` (READ ONLY for Codex)
Previous R08 prompt: `.hiveai/prompts/SB_LFX_018_R05_V13_CD_R08_CONDITIONAL_NATIVE_GODOT_PARSE_ONLY.md`
Strict V22 audit: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R07_STAGED_INVENTORY_NATIVE_STRICT_AUDIT_V22.md

## Why this revision exists

Owner provided a screenshot from Windows Task Manager on **2026-10-23**: a search for `godot` shows multiple `godot-ai.exe` processes, **not** the historical actual Godot 4.7.2 editor binary `Godot_v4.7.2-stable_win64.exe`. Do not equate Godot AI helper/service processes with the Godot game engine. This is a name-based observation, not a conclusion about their full paths, child processes, writes or trust. The previous concurrent Godot engine PID 13860 belongs to the 2026-10-21 Beach Cocktails template-install snapshot; that old PID may have exited or been reused. Stop cycling through old PID 13860 and old inventories. Do NOT start the project from scratch or discard any completed R01–R07 work.

**Objective: run one genuine, scoped native Godot 4.7.2 source-script parse if safe, or report one NEW specific unavoidable blocker.**

## Mandatory start

Read current root `TASKS.md`, this exact V02 prompt, V22 audit and only R07-C relevant evidence. Check canonical checkout and `origin/main` HEAD, safe FF-only synchronization if tracked work and all owner-untracked data are safe. No clone/worktree/TEMP, reset, clean, rebase, force or old-task regeneration. Do NOT redo six manifests, 18 SHA inventory, R07-A/B, 140 PNG or prior test suites. Read-only checks may examine paths/OS process fields but never mutate unrelated process state.

## Step 1: ONE current process identity check, not global Godot name search

Use read-only `Get-CimInstance Win32_Process` or equivalent:
- Distinguish `godot-ai.exe` (Godot AI helper/service) from true Godot engine executable. Match real engine names such as `Godot.exe`, `Godot_v4.7.2-stable_win64.exe` and versioned `Godot_v*.exe`, identified by exact executable path/command line and creation time, NOT substring `godot` or stale PID.
- Check actual Godot engine parent/child relationships and whether any `godot-ai.exe` spawns or is controlling a **real** Godot engine process. The visible godot-ai services are **not by themselves** evidence of active Godot editor/cache writing. Do not kill, stop, suspend, uninstall or restart them.
- Do not demand absence of all `godot-ai.exe` helper processes. A non-engine helper with no verified shared-cache writing is not a native parse blocker. Do not mark active `godot-ai.exe` count as proof that project-native Godot cannot run.
- If actual competing `Godot_v*.exe` (e.g. Beach Cocktails template installer) is still working in the shared editor data, or command-line/exe metadata is unavailable for a suspicious real engine, block narrowly with fresh `ENGINE_CONCURRENCY_BLOCKED` evidence. If no real competing engine exists, continue. Do not launch Godot merely to count processes.

Suggested read-only filter (adapt safely, exact path checks after filtering):
```powershell
Get-CimInstance Win32_Process -ErrorAction Stop |
  Where-Object { $_.Name -match '(?i)^godot(?:_v[0-9].*)?\.exe$' } |
  Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CreationDate,CommandLine
```
The filter deliberately excludes `godot-ai.exe`; inspect those helpers as necessary for child-lineage proof only, not as engine processes.

## Step 2: native invocation scope, no shared AppData hunt loop

Use the canonical existing Godot 4.7.2 executable directly (verify binary path/version) with **one known safe existing project GDScript** in `level_factory`. Official Godot docs: `--check-only` requires `--script`, `--headless` is supported; `--import` starts editor and is outside this approval. Do not create a new project or script, use editor GUI or replay solver/batch. Document exact command and source file before execution.

Check whether the already-installed engine is independently configured as self-contained (an existing `_sc_`/editor_data layout). If yes, it can naturally avoid shared user-wide editor paths. **Do not create a new self-contained mode marker, duplicate engine, overwrite installed engine or create a TEMP sandbox under this authorization.** Otherwise, the owner's already granted bounded permission covers only directly attributable generated `level_factory/.godot/**`, `*.uid`, `*.import`, and related project-specific Godot user cache/config paths, **not uncontrolled edits to unrelated user settings or other projects**.

Take narrowly bounded before SHA/path inventory for existing source/project scripts and protected owner job/Pool/PNG/Release, and for likely permitted generated paths; avoid huge recursive scans. If allowed writes cannot be bounded due to verifiable competing engine or unknown user-global write behavior, block with the exact new concern; **do not reuse 2026-10-21 PID as blocker**. If the shared editor is idle, an engine source-script `--headless --path <canonical level_factory> --script <existing relative script> --check-only` is the preferred bounded attempt with finite timeout. This proves SINGLE SCRIPT PARSE only, NOT all scenes, imports, three-page installed GUI or end-to-end 240/480 replay. No `--import`, `--editor`, batch/workflows/paid calls.

After the bounded parse, capture actual binary/version, command, exit, stdout/stderr, affected in-scope generated files, before/after hashes and any unexpected write. Never clean/delete/restore owner files speculatively. If an unexpected write occurred, disclose it, stop and do not retry. Distinguish `R08_REAL_GODOT_SINGLE_SCRIPT_PARSE_PASS` from `R08_REAL_GODOT_PARSE_FAILED` or `R08_BLOCKED_FRESH_PROVEN_ENGINE_WRITER`.

## Step 3: publication discipline

Only if **genuine native parse executed**, append actual results to SAME M03 builder log and commit a focused report, optionally a proven necessary narrow source fix. Publish normal FF-safe to GitHub main and verify HEAD=origin/main, 0/0 and tracked clean. If blocked before invocation, return the specific new blocker in chat **without another redundant report-only commit**. Never edit GPT-owned TASKS.md or previous audit/prompt content.

Absolute exclusions: no Release `-Apply`, no installed GUI launch, no CI/Actions/paid provider/PixelLab credits, no R2/prod, no 140 PNG retry/replay, no process termination, no TEMP/new worktree, no mass disk cleanup. Preserve installed manifest `verify.py` drift and `WriterExclusionEstablished=false` gate for Release. R07-A/B remain accepted. The user's screenshot has NOT authorized deleting Godot AI processes.

Official documentation: https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html and https://docs.godotengine.org/en/4.7/classes/class_editorpaths.html

**Final one-line result:** real-Godot process whitelist state; native parse actual PASS/FAIL or new blocker; no owner data touched except narrowly approved generated Godot cache; source/report/log commit SHAs if published. No new R09 paper loop.
