# MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01 — Durable Local Install + Real Desktop Shortcut Launch

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Strict audit:
`.hiveai/audits/MAINT_FACTORY_STUDIO_LAUNCHER_C001_STRICT_AUDIT_V01.md`

Audit criteria:
`.hiveai/audit-criteria/MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01_DURABLE_INSTALL_AUDIT_CRITERIA.md`

## FIRST OPERATION — safe sync

1. Inspect:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Run `git fetch --prune origin`.
3. Preserve owner-local work byte-for-byte.
4. Never reset, clean, rebase, auto-stash, restore/discard, overwrite or force.
5. If persistent checkout remains unsafe, use a fresh clean TEMP implementation worktree at exact `origin/main`.
6. Never create a Desktop sibling clone/worktree.
7. Never edit root `TASKS.md`.
8. Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01_DURABLE_INSTALL_CODEX_LOG.md`

## R01-1 — retain accepted launcher/icon implementation

Do not redesign the icon, header, project identity, native-icon logic or Godot discovery unless required by the durable deployment fix.

Retain:

- owner ICO authority;
- byte-identical repo ICO;
- derived 256 PNG;
- `ScrubBots Factory Studio` app identity;
- top-left icon/title;
- direct `godot --path level_factory` launch;
- no editor launch;
- idempotent Desktop shortcut repair behavior.

## R01-2 — replace TEMP-bound shortcut with a durable runtime installation

Current defect:
the actual Desktop shortcut points to the implementation worktree under `%TEMP%`.

Create a stable owner-local runtime root outside TEMP, recommended:

`%LOCALAPPDATA%\ScrubBots Factory Studio\runtime`

The committed install/repair flow must populate and maintain this stable runtime from the exact published repository revision being installed. The existing dirty Desktop checkout must not be reset, cleaned, rebased, stashed, restored, overwritten, or used as source authority. The new `Release` subtree is an owner-authorized deployment destination only.

Choose a safe implementation such as a dedicated stable local clone/snapshot. Requirements:

- ordinary launch must not require network;
- create the `Release` folder if absent, then create/update only `Release\\ScrubBots Factory Studio`;
- treat any pre-existing unknown files inside that runtime destination as owner data: preserve or fail closed, never silently delete/overwrite;
- do not depend on the implementation TEMP worktree after install;
- stable runtime must include every Factory Studio runtime dependency, not only the two PowerShell scripts;
- preserve any owner-generated/output data on repair/update;
- fail closed rather than destructively replacing unknown owner data;
- record installed source commit/revision in a non-secret local marker if useful;
- installer can be rerun safely.

After installation, update:

`%USERPROFILE%\Desktop\ScrubBots Factory Studio.lnk`

so its launcher argument and WorkingDirectory point only to `C:\\Users\\sekip\\Desktop\\Scrubbots - Pixel Art Generator\\Release\\ScrubBots Factory Studio`.

No shortcut field may reference the R01 implementation TEMP worktree.

## R01-3 — prove TEMP independence

After stable install + shortcut creation:

1. COM-read and record all shortcut fields.
2. Rename or otherwise make the implementation TEMP worktree path unavailable without deleting owner data.
3. Re-read the shortcut and verify every referenced launcher/project/icon path still exists.
4. Restore/retain the implementation worktree only as needed for publishing the builder log. The installed app must not depend on it.

Do not delete the stable runtime.

## R01-4 — execute the real Desktop shortcut

Run the actual:

`C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk`

Capture bounded evidence that:

- a new Godot process was created by this shortcut;
- its command line/project path points to the stable runtime `level_factory`;
- `--editor` is absent;
- Factory Studio starts successfully.

Then close only that newly created Factory Studio process. Do not terminate pre-existing Godot/editor processes.

If process-command-line inspection is unavailable, use an equivalently strong Windows process/window identity proof tied to the newly launched PID.

## R01-5 — regression

Add focused tests for:

- installer rejects/avoids TEMP as final shortcut/runtime authority;
- exact owner-selected stable runtime path derivation (`C:\\Users\\sekip\\Desktop\\Scrubbots - Pixel Art Generator\\Release\\ScrubBots Factory Studio`);
- shortcut arguments/WorkingDirectory use stable runtime;
- repair/idempotency semantics;
- owner output preservation boundary where applicable.

Run:

- launcher/icon/Studio focused suites;
- Godot boot from the stable installed runtime;
- actual Desktop shortcut launch smoke;
- safe full pytest with explicit clean TEMP ScrubBots authority;
- compileall;
- diff checks;
- secret scan.

## Publication

Implementation/test commit separate from builder log.
Normal push only.
No force.

## Final state

If all criteria pass:

`AWAITING_GPT_MAINT_FACTORY_STUDIO_LAUNCHER_C001_R01_STRICT_REAUDIT`

Final response:
return only the R01 builder log GitHub URL.
