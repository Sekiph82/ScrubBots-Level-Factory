# MAINT-FACTORY-STUDIO-LAUNCHER-C001 — CHATGPT STRICT AUDIT V01

Date: 2026-10-08
Repository: `Sekiph82/ScrubBots-Level-Factory`
Audited implementation: `5d955491c9e2c355b749f7e7304499a558afbeeb`
Builder evidence: `62c8ff2c41b6542db7b293db2662b21ca1cf1e4f`
Builder log: `.hiveai/codex-logs/MAINT-FACTORY-STUDIO-LAUNCHER-C001_WINDOWS_LAUNCHER_ICON_CODEX_LOG.md`

## VERDICT

**CHANGES_REQUIRED / R01**

Most implementation requirements PASS. The remaining blockers are deployment/launch-proof defects, not an icon or Godot architecture rewrite.

## A — PASS: owner icon authority

Accepted evidence:

- exact owner source ICO exists at the authorized path;
- valid seven-frame ICO: 16, 24, 32, 48, 64, 128, 256 px;
- repository ICO is byte-identical to owner source;
- derived 256x256 RGBA PNG preserves the selected frame without redesign;
- source owner ICO was not modified.

## B — PASS: Godot application identity

Accepted source:

- application name is `ScrubBots Factory Studio`;
- `application/config/icon` points to the committed PNG;
- `application/config/windows_native_icon` points to the committed ICO;
- Windows runtime applies the same ICO through `DisplayServer.set_native_icon()` only when the supported native-icon feature exists;
- direct project boot and runtime suite pass.

## C — PASS: Factory Studio header identity

Accepted source:

- top-left header uses the derived icon;
- 46x46 aspect-preserving TextureRect;
- title is `SCRUBBOTS FACTORY STUDIO`;
- existing navigation/workspace runtime regression remains green.

## D — PASS: reusable direct launcher implementation

Accepted source:

- launcher resolves repository root from its own script path;
- supports `SCRUBBOTS_FACTORY_GODOT` override;
- bounded Godot 4 discovery is present;
- launcher uses `Start-Process ... --path <project>`;
- no `--editor` flag;
- clear unavailable-Godot error path;
- no global PATH/registry/policy mutation;
- resolution-only smoke resolves installed Godot 4.7.2.

## E01 — BLOCKING: Desktop shortcut is bound to a TEMP worktree

Actual COM readback in builder evidence:

- shortcut: `C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk`
- TargetPath: Windows PowerShell
- launcher argument:
  `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\MAINT-FACTORY-STUDIO-LAUNCHER-C001\scripts\launch_factory_studio.ps1`
- WorkingDirectory:
  `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\MAINT-FACTORY-STUDIO-LAUNCHER-C001`

This is not a durable owner-facing installation. The shortcut becomes broken as soon as the TEMP worktree is removed by normal cleanup, OS cleanup, or a later maintenance cycle.

The audit criteria require a real reusable Desktop launcher, not a shortcut whose executable project root is ephemeral.

The persistent Desktop repository was correctly left untouched because it is heavily dirty/stale. That safety decision is accepted. The fix must therefore use a **stable dedicated runtime/install root outside TEMP** rather than mutating or resetting the owner's persistent checkout.

### Required R01 behavior

Create/maintain a stable owner-local Factory Studio runtime root, for example:

`%LOCALAPPDATA%\ScrubBots Factory Studio\runtime`

Requirements:

1. it must not live under `%TEMP%`;
2. it must be populated from the exact audited/published repository revision without modifying the dirty Desktop checkout;
3. the committed installer must idempotently create/repair that stable runtime root and Desktop shortcut;
4. the shortcut launcher argument and WorkingDirectory must point only to that stable root;
5. the stable runtime must contain the committed launcher, `level_factory` project, and every repository runtime dependency required by Factory Studio;
6. owner-generated runtime/output data must not be silently destroyed by reinstall/repair;
7. the shortcut must remain valid after the implementation TEMP worktree is removed or renamed;
8. no network dependency may be introduced into ordinary double-click launch.

A clean dedicated LocalAppData clone/runtime snapshot is acceptable. Do not create a Desktop sibling clone/worktree.

## E02 — BLOCKING: actual Desktop shortcut launch was not proven

Builder evidence confirms installer execution, COM readback and `-ResolveOnly`, but explicitly says:

`No terminal/editor launch was performed by the dry run.`

The PASS rule requires that the real Windows Desktop shortcut actually launches Factory Studio without requiring an owner terminal command.

R01 must perform a bounded launch smoke from the actual `.lnk`:

- invoke the real Desktop shortcut;
- prove the resulting Godot process is running the stable Factory Studio project and not `--editor`;
- prove the stable project root is used;
- close only the test-launched Factory Studio process after evidence is captured;
- do not kill unrelated Godot/editor processes.

COM readback alone is insufficient for this final requirement.

## F — PASS: regression quality

Accepted builder evidence:

- focused launcher/Studio suite: **21 passed**
- final full pytest: **1721 passed, 6 skipped, 0 failed**
- Godot direct headless boot: PASS
- Factory Studio runtime suite: PASS
- compileall: PASS
- diff checks: PASS
- builder did not edit root `TASKS.md`
- builder did not edit `.hiveai/audits/**`

The initial accidental Desktop-game fallback was detected and stopped; final full regression used an explicit clean TEMP ScrubBots authority and is accepted.

## R01 disposition

R01 is authorized only to close the durable-install + real-shortcut-launch proof.

Retain all accepted icon, UI, Godot and launcher code unless a minimal deployment adjustment is required.

Do not begin M17.

## FINAL

**CHANGES_REQUIRED / R01**

Required next state after a successful remediation:

`AWAITING_GPT_MAINT_FACTORY_STUDIO_LAUNCHER_C001_R01_STRICT_REAUDIT`
