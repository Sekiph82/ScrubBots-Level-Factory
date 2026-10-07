# MAINT-FACTORY-STUDIO-LAUNCHER-C001 — Windows Desktop Launcher + ScrubBots Factory Studio Icon

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Audit criteria:
`.hiveai/audit-criteria/MAINT-FACTORY-STUDIO-LAUNCHER-C001_WINDOWS_LAUNCHER_ICON_AUDIT_CRITERIA.md`

Owner-provided local icon:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\ScrubBots_Factory_Studio.ico`

## EXECUTION GATE

This maintenance task is queued immediately after the currently active M18 / SB-CPX-004 R2 work and explicitly before M17.

Before doing anything:
- read current `origin/main:TASKS.md`;
- execute only when ChatGPT has made `MAINT-FACTORY-STUDIO-LAUNCHER-C001` the canonical Current Task after M18 / SB-CPX-004 is independently closed;
- if M18 / SB-CPX-004 is still the current active batch, STOP without touching the repo.

Do not run concurrently with the M18 / SB-CPX-004 TEMP worktree. This maintenance task must PASS/CLOSE before M17 is opened.

## FIRST OPERATION — mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
3. Run `git fetch --prune origin`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If persistent checkout is not safely synchronizable, use only:
   `%TEMP%\ScrubBots-Level-Factory\MAINT-FACTORY-STUDIO-LAUNCHER-C001`
6. Never create a Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before implementation.

Create builder log before edits:
`.hiveai/codex-logs/MAINT-FACTORY-STUDIO-LAUNCHER-C001_WINDOWS_LAUNCHER_ICON_CODEX_LOG.md`

## 1. Inspect owner ICO

Use exactly:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\ScrubBots_Factory_Studio.ico`

Verify:
- file exists;
- valid ICO;
- available embedded sizes;
- transparency;
- choose the largest suitable source frame for UI PNG derivation.

Do not modify the owner source ICO.

Copy it byte-for-byte to a stable repo asset such as:
`level_factory/assets/icons/ScrubBots_Factory_Studio.ico`

Derive:
`level_factory/assets/icons/ScrubBots_Factory_Studio_256.png`
or the largest actual embedded frame if 256 is unavailable.

Use nearest/lossless frame extraction, not a visual redesign.

## 2. Godot application identity

Inspect actual installed Godot 4.7.2-supported project settings/APIs before editing.

Update `level_factory/project.godot` so:
- app name is `ScrubBots Factory Studio`;
- current supported icon setting points to the stable repository icon/PNG asset;
- if Godot 4.7.2 exposes a distinct supported Windows native icon setting, use the repo ICO there;
- do not invent unsupported settings.

The app launched with `godot --path level_factory` must run the project directly, not open the editor.

Where needed and supported, use current Godot runtime DisplayServer icon API from the shell to ensure the Windows taskbar/titlebar receives the same icon identity. Any runtime icon load must fail gracefully without breaking Studio boot.

## 3. Top-left Studio icon

Modify the existing Factory Studio header cleanly.

Current header contains the title/subtitle identity area.

Add a left-side icon before that text:
- repository PNG derived from the owner ICO;
- approximately 40-48 logical px suitable for the current 640x360 layout;
- preserve aspect ratio;
- no distortion;
- transparent background;
- keep title/subtitle readable.

Update visible header title to:
`SCRUBBOTS FACTORY STUDIO`

Preserve:
- navigation;
- workspace routing;
- target controls;
- footer;
- canonical Core gateway;
- existing Studio functionality.

Update affected tests/node paths truthfully.

## 4. Windows application launcher

Create:
`scripts/launch_factory_studio.ps1`

Requirements:
- determine repo root from `$PSScriptRoot`;
- project path = `<repo>\level_factory`;
- optional explicit `SCRUBBOTS_FACTORY_GODOT` environment override;
- otherwise bounded lookup of current Godot executable using `Get-Command godot.exe` / `godot` and known current local install locations only;
- validate executable;
- launch direct project application with `--path <level_factory>`;
- DO NOT add `--editor`;
- no global policy/PATH/registry changes;
- no network;
- clear owner-facing error if Godot cannot be resolved.

Avoid keeping an unnecessary terminal window open after the Studio launches where Windows allows a clean detached Start-Process handoff.

## 5. Idempotent Desktop shortcut installer

Create:
`scripts/install_factory_studio_shortcut.ps1`

It must use the Windows `WScript.Shell` shortcut COM API.

Create/update exactly:
`$env:USERPROFILE\Desktop\ScrubBots Factory Studio.lnk`

Configure:
- TargetPath: Windows PowerShell executable or another stable Windows launcher target that invokes the committed `launch_factory_studio.ps1`;
- Arguments: safely quoted path to the committed launcher;
- WorkingDirectory: canonical repo root;
- Description: `ScrubBots Factory Studio`;
- IconLocation:
  `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\ScrubBots_Factory_Studio.ico,0`

If the authoritative local ICO path is unavailable during a later repair, the installer may fall back only to the byte-identical committed repo ICO.

Installer is idempotent: rerun repairs the same shortcut instead of creating duplicates.

## 6. Actually create the Desktop shortcut

During this task, execute the installer on the owner's Windows machine.

Then COM-read the resulting `.lnk` and record in the builder log:
- full shortcut path;
- TargetPath;
- Arguments;
- WorkingDirectory;
- IconLocation;
- Description.

Do not merely commit the installer and claim success.

## 7. Verification

Run:
- icon/PNG validation;
- Godot headless project boot;
- Factory Studio runtime/scene smoke;
- relevant Studio unit/integration tests;
- shortcut installer focused test;
- shortcut COM readback;
- launcher dry-run/resolution test without opening the editor;
- safe full pytest;
- compileall;
- diff check.

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

## Publication

If green:
- commit implementation/assets/scripts/tests;
- commit builder log separately;
- fetch/prune;
- normal non-force push to main;
- fetch again;
- require 0/0 parity and clean execution worktree;
- stop for ChatGPT independent audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-FACTORY-STUDIO-LAUNCHER-C001_WINDOWS_LAUNCHER_ICON_CODEX_LOG.md
