# MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01 — ChatGPT Strict Re-Audit V01

Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Audited implementation chain:
- `8a4d7e111be4dfc83eb7ed8f19c4860a389bdc68`
- `fafd7dd0b4b5c206aa05ced1bc4dfdc78147fed2`
- `e936b54025973c5094b5dc9669d0e36e1687a062`

Builder log publication:
`a5b79b4bbc2aa9b9261f8a1f1ca35502bc3320fd`

Builder evidence:
`.hiveai/codex-logs/MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01_DURABLE_INSTALL_CODEX_LOG.md`

Criteria:
`.hiveai/audit-criteria/MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01_DURABLE_INSTALL_AUDIT_CRITERIA.md`

## VERDICT

**PASS / CLOSED**

The Desktop Factory Studio launcher is now durable, owner-usable and independent of disposable TEMP task worktrees.

No launcher R02 is required.

## A — stable owner runtime: PASS

The committed installer binds the runtime to the owner-authorized path:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

Source review confirms:

- final runtime is explicitly rejected if under `%TEMP%`;
- source must be the canonical GitHub repository;
- source HEAD must equal fetched `origin/main`;
- tracked source must be clean;
- runtime is populated from tracked published files;
- a deterministic local install manifest binds managed files and source revision;
- unknown owner files are preserved or cause fail-closed collision behavior;
- modified previously-managed files cause fail-closed behavior;
- reparse-point escape is rejected;
- repair is staged and rollback-aware;
- the dirty persistent owner source checkout is not reset/cleaned/rebased/stashed.

Builder evidence proves the installed runtime contains 1,991 tracked files and its sourceRevision matched the published installer revision.

## B — shortcut durability: PASS

Actual COM readback proves:

- shortcut:
  `C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk`
- TargetPath:
  Windows PowerShell
- launcher argument:
  `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio\scripts\launch_factory_studio.ps1`
- WorkingDirectory:
  `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`
- Description:
  `ScrubBots Factory Studio`
- icon:
  stable-runtime byte-identical owner ICO.

No shortcut field references the implementation TEMP worktree.

## C — TEMP independence: PASS

Builder renamed/made the implementation TEMP path unavailable before launching the actual Desktop shortcut.

While that TEMP path was unavailable:

- all shortcut-referenced stable files still resolved;
- the real Desktop shortcut launched successfully from the Release runtime.

Therefore the owner launcher no longer depends on the implementation task worktree.

## D — real shortcut launch: PASS

The actual `.lnk` was executed.

Captured process evidence:

- new Godot process PID: `19400`;
- executable: `Godot_v4.7.2-stable_win64.exe`;
- command line project path:
  `...\Release\ScrubBots Factory Studio\level_factory`;
- `--editor` absent;
- normal owner launch required no terminal command;
- seven pre-existing Godot processes were inventoried and left untouched;
- only the process created by this smoke was closed.

This satisfies the double-click-equivalent acceptance requirement.

## E — install/repair safety and idempotency: PASS

The initial installer revision exposed two defects during builder verification and they were corrected before final publication:

1. PowerShell pipeline timing incorrectly obscured `$LASTEXITCODE` after canonical-origin lookup.
2. An optional timestamp in the install manifest produced locale-dependent byte drift after `ConvertFrom-Json`.

Final source fixes both.

A second repair run:

- preserved an unknown owner-output sentinel byte-for-byte;
- preserved install-manifest SHA;
- did not silently remove unknown owner data.

Focused source tests cover the stable runtime, canonical source binding, unknown-owner-data boundaries and idempotent repair behavior.

## F — focused and runtime regression: PASS

Accepted evidence:

- focused launcher/icon/Studio suites: **25 passed**;
- Godot stable-runtime import: PASS;
- Godot stable-runtime direct headless boot: PASS;
- PowerShell parser: PASS;
- compileall: PASS;
- diff check: PASS;
- credential-pattern scan: PASS;
- no dependency/license changes.

## G — full-suite disposition: PASS after independent closure of both reported failures

The builder's unfiltered full pytest run reported:

**1722 passed, 6 skipped, 2 failed**

Neither failure represents a launcher regression.

### G1 — CPX-002 current-game authority race

During the long full run the clean game authority became stale because `origin/main` advanced.

The builder then refreshed the clean exact-current game authority and reran the exact failed integration test:

**1 passed**

This closes the environment-race failure.

### G2 — TASKS denominator mismatch

The second failure was:

`test_current_tasks_rows_are_parser_safe_and_declared_denominator_matches`

Repository inspection confirms the cause was ChatGPT-owned tracker state:

- parser row count: 250;
- declared denominator: 248;
- new owner-approved `SB-LFX-018` and `SB-LFX-019` rows had been added after the historical 248 declaration.

ChatGPT corrected the canonical declaration on 2026-10-08:

`250 = 224 + 3 + 19 + 4`

Tracker correction commit:

`e152570a188878f4546bd59657e4592ba00c9f9a`

The failing assertion is a direct equality between that declared integer and parsed task-row count. No product/test workaround was required.

Because both observed failures have exact, independently verified closure and neither is a launcher implementation defect, another launcher remediation cycle is not justified. The next full repository suite will naturally include the corrected tracker state during SB-LFX-019 execution.

## H — governance: PASS

Builder correctly did not edit:

- root `TASKS.md`;
- `.hiveai/audits/**`.

Persistent dirty owner Desktop work was preserved.

Implementation and builder log were published by normal fast-forward pushes.

## I — known UI follow-up, not launcher blocker

The real launched window still showed:

`ScrubBots Factory Studio (DEBUG)`

This is **not** a launcher durability defect. The owner-approved Simple Owner UI task `SB-LFX-018-C001` already requires the normal owner runtime title to become exactly:

`ScrubBots Factory Studio`

That UI task remains sequenced after LF VOID integration so the final owner UI is redesigned once against the final transparent-art contract.

## FINAL

**PASS / CLOSED**

Launcher sequencing gate is satisfied.

Next canonical implementation task:

`SB-LFX-019-C001 — Transparent Artwork -> VOID End-to-End`

After SB-LFX-019 closes:

`SB-LFX-018-C001 — Simple Owner UI`

Then M17.
