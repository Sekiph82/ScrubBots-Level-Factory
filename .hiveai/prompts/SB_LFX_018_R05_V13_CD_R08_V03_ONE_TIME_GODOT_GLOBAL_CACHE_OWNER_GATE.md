# SB-LFX-018 R05 V13-C/D R08 V03 | ONE-TIME WINDOWS GODOT CACHE OWNER PERMISSION GATE
Document role: GPT AUTHORIZED CONDITIONAL CODEX BUILDER PROMPT, **DO NOT EXECUTE NATIVE TEST UNTIL OWNER EXPLICITLY APPROVES EXPANDED GLOBAL WRITE SCOPE**
Date: 2026-10-23 Europe/Istanbul
Repo: https://github.com/Sekiph82/ScrubBots-Level-Factory
Canonical source checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Single GPT-owned root task ledger: `TASKS.md`, Codex READ-ONLY.
Previous R08 V02: `.hiveai/prompts/SB_LFX_018_R05_V13_CD_R08_V02_REAL_GODOT_ENGINE_WHITELIST_NATIVE_PARSE.md`
Parent V13-C/D remains open. R01-R07 completed; no R09 or task restart.

## Owner permission status: PENDING, must not presume approval
At R08 V02 the Codex builder freshly established zero competing true `Godot_v4.7.2-stable_win64.exe` engine processes and located the installed genuine engine, but no actual native execution. `godot-ai.exe` helpers are not itself a real editor-engine concurrency blocker. The native source-script parse remains blocked for **one new specific reason**: a non-self-contained Windows Godot engine may write shared defaults during initialization.

Godot 4.7 reference:
- `https://docs.godotengine.org/en/4.7/tutorials/io/data_paths.html`: Windows editor data and settings default `%APPDATA%\Godot\`; editor cache may use `%TEMP%\Godot\`.
- `https://docs.godotengine.org/en/4.7/classes/class_editorpaths.html`: editor config/data `%APPDATA%\Godot\`, editor cache default `%LOCALAPPDATA%\Godot\`.
- `https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html`: `--check-only` requires `--script`; `--import` starts editor and is NOT part of this task.

**Owner's earlier bounded generated-project/cache approval did NOT clearly authorize writes to existing user-global Godot settings, editor data or TEMP caches.** This V03 document IS NOT that authorization. User must explicitly approve the following ONE-TIME narrow expansion before proceeding.

### Proposed one-time owner approval scope (not granted yet)
Authorize ONLY the **identified genuine existing Godot 4.7.2 process**, for ONE finite `--headless --path <canonical level_factory> --script <existing safe script> --check-only` parse. During that one invocation, permit Godot-engine-attributable creation/modification of files in:
- Canonical `level_factory/.godot/**`, exact tool-generated `*.uid`, `*.import` within the *same* project;
- `%APPDATA%\Godot\**` including Godot-specific editor settings/cache/data files if the engine writes them;
- `%LOCALAPPDATA%\Godot\**` if actually used as an editor cache path by this Godot 4.7.2 build;
- `%TEMP%\Godot\**` **only as Godot's ordinary own cache during this parse**, not permission to create TEMP clones/worktrees/projects/other scratch.
No writing permissions are expanded to directories other than these exact Godot scopes. Existing settings or cache files under these scopes may be modified by Godot; this is a real consequence to disclose before owner approval. Any unknown/unattributable or outside-scope write is unauthorized. No removal of cache files, resets, modifications to other Godot projects, general AppData, Windows global environment variables, executable folder `_sc_` marker, broader OS settings, source files, owner PNG/job/Pool, original Release manifests or production deploy.

**Owner must be asked once, clearly:** "Bu tek Godot 4.7.2 native parse için `%APPDATA%\Godot`, `%LOCALAPPDATA%\Godot` ve `%TEMP%\Godot` altındaki Godot'a ait cache/ayar dosyalarının gerekirse oluşturulmasını veya değiştirilmesini onaylıyor musun?" If the owner has not replied affirmatively in the active conversation, do not execute test; do not infer approval from this repository document or earlier limited project-cache consent.

## Once AND ONLY once owner has approved, Codex execution sequence

1. Read current `TASKS.md`, this V03, minimal prior V02 context. Safely FF-only synchronize canonical repo main without overwriting any owner tracked/untracked data. No new worktree/clone, TEMP project/scratch, force/rebase/reset/clean.
2. One fresh, bounded read-only check identifying **true Godot engine** processes, not `godot-ai.exe`. Never terminate or modify unrelated programs. Verify exact installed Godot 4.7.2 engine path/version and existing side-effect-free project script. If a competing true engine now exists and writes shared Godot paths, stop with exact process evidence.
3. Prepare before-state bounded SHA/path inventory of affected `%APPDATA%\Godot`, `%LOCALAPPDATA%\Godot`, `%TEMP%\Godot` *Godot-only* trees and permitted `level_factory/.godot/.uid/.import`; also hash exact protected source/manifest/job/Pool files without recursive system-wide scanning. Do not read credentials or log contents of sensitive editor settings; compare hashes and minimal filenames only. Note if inventory is impossible and don't claim data was unchanged.
4. Run at most **ONE** finite, non-editor, non-import, non-job `--headless --path <canonical level_factory> --script <existing safe .gd> --check-only` Godot 4.7.2 parser command. Never `--editor`, `--import`, open installed GUI, run solver/batches, start paid PixelLab/ALPIX, call CI or Actions, trigger credential or network operations. Timebox with safe process-tree handling: do not kill third-party processes, and do not leave a new Godot test running after the deadline. If a bounded timeout cannot be enforced without affecting owner processes, block before launch.
5. Collect actual command/version/exit/stderr/stdout, compare hashes in the above exact scopes and protected owner files before/after, distinguish changed existing editor settings from cache additions, and report any unapproved mutations precisely. If unusual writes occur, stop without cleanup/restore/delete; do not rerun automatically.
6. If actual native parse runs, append real results to existing append-only M03 builder log and create one concise GitHub evidence report in `docs/process/`; normal FF-only publish to `main`, fetch and verify parity. Do not edit GPT-owned TASKS.md or audits/prompts/old builder history.
7. If test does not run or approval absent, do not create a redundant report-only commit, extra R09 prompt or repeated full inventories; just report the precise blocker.

Success is at most `R08_REAL_GODOT_SINGLE_SCRIPT_PARSE_PASS`. It is NOT complete project scene/UID import testing or three-screen GUI acceptance. `INSTALL_BLOCKED_MANIFEST_DRIFT`, `PROCESS_QUIESCENCE_UNPROVEN`, `RELEASE_APPLY_NOT_AUTHORIZED`, `INSTALLED_GUI_OPEN` and original COMPLETE 140+Pool preserved continue regardless.

### Absolute exclusions
No Release `-Apply`, writing installed manifest or trusting `verify.py`, new TEMP/worktree/clone, destructive cleanup, workflow CI/Actions, paid provider, original 140 job rerun, other project Godot template install interference, stopping user processes, credential logging, broad global Godot settings modifications for convenience, or subsequent extra parse runs without new authority.
