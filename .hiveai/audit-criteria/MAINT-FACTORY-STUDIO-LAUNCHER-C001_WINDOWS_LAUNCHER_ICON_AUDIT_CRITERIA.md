# MAINT-FACTORY-STUDIO-LAUNCHER-C001 — Windows Launcher + Icon Integration — Audit Criteria

## PASS rule

PASS only if ScrubBots Factory Studio can be launched from a real Windows Desktop shortcut with the owner-provided ICO, the Godot app uses the same visual identity in the window/taskbar where supported by current Godot 4.7.2, and the Factory Studio header shows a clean derived icon at top-left.

## A. Owner icon authority

Authoritative owner-local source:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\ScrubBots_Factory_Studio.ico`

Require:
- file exists and is a valid multi-resolution ICO;
- source file is not modified;
- copy the ICO into a stable repository-owned asset path for application/export identity;
- derive a lossless PNG from the largest suitable ICO frame for Godot UI/header use;
- no image redesign, recolor, crop, resample blur or new generated art.

## B. Application identity

Require:
- Godot application name becomes `ScrubBots Factory Studio`;
- project/window icon uses the owner icon identity through current Godot 4.7.2-supported project setting/API;
- do not invent unsupported ProjectSettings keys;
- project opens/runs successfully after the icon settings;
- taskbar/titlebar/window icon uses the same identity where the Windows/Godot runtime supports it.

## C. Top-left Factory Studio UI icon

Require:
- the Factory Studio header contains a visible icon at the left of the existing title/subtitle identity area;
- source is the derived repository PNG;
- aspect ratio preserved;
- no stretching/distortion;
- icon size remains appropriate for the existing 640x360 workspace;
- existing navigation/workspace/footer behavior remains unchanged;
- update title text to `SCRUBBOTS FACTORY STUDIO` unless a stronger current accepted UI contract forbids it.

## D. Windows launcher

Create a committed reusable launcher script under `scripts/`.

Launcher must:
- resolve repository root from its own script location, not a fragile current working directory;
- launch the Godot project directly as the Factory Studio application, not open the Godot editor;
- locate a valid Godot 4 executable using bounded deterministic discovery;
- support an explicit environment override before bounded local discovery;
- fail with a clear Windows dialog/message when Godot is unavailable;
- not modify PATH, registry, PowerShell policy globally or user data;
- not require network access.

## E. Desktop shortcut

Create a committed idempotent shortcut installer script and actually execute it during builder verification.

Required Desktop shortcut:
`%USERPROFILE%\Desktop\ScrubBots Factory Studio.lnk`

Shortcut properties:
- display name exactly `ScrubBots Factory Studio`;
- target invokes the committed launcher safely;
- working directory is canonical repository root;
- description identifies ScrubBots Factory Studio;
- `IconLocation` uses:
  `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\ScrubBots_Factory_Studio.ico,0`
  or the byte-identical stable repo copy if the shortcut installer deliberately normalizes to it;
- double-click opens the Studio application without requiring a terminal command from the owner.

Installer must update/repair the shortcut idempotently if rerun.

## F. Verification

Require:
- ICO validity/multi-resolution inspection;
- derived PNG dimensions/transparency check;
- Godot project parse/headless boot PASS;
- Studio scene-instantiation regression PASS;
- shortcut file exists after installer execution;
- COM readback proves target, arguments, working directory and icon location;
- launcher smoke proves it resolves Godot/project correctly without launching the editor;
- relevant Factory Studio tests PASS;
- safe full repository regression PASS except documented capability skips;
- no M14/M13/M12/M11 regression;
- diff check PASS.

## G. Governance

Do not execute while the active M14 dirty master worktree is still in progress unless ChatGPT has explicitly switched the canonical tracker to this maintenance task.

Codex must not edit root `TASKS.md` or `.hiveai/audits/**`.
