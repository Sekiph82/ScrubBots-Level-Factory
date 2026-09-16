# SB-LF06-003-C001 — Factory Studio Canonical Action Bridge
Document role: CHATGPT STRICT AUDIT

Audit date: 2026-09-16
Repository: `Sekiph82/ScrubBots-Level-Factory`
Authoritative prompt: `.hiveai/prompts/SB-LF06-003-C001_FACTORY_STUDIO_CANONICAL_ACTION_BRIDGE_PROMPT.md`
Starting tracker/base commit: `6eb7803f256b43acc859039e9e74f94db5f0f9e7`
Implementation commit: `a34107864d44118762bcde3a35f7c04a5633a4a4`
Observed terminal builder publication commit: `9cc87b4edb493f0d3848aeaec2947b718a5c2127`
Builder log: `.hiveai/codex-logs/SB-LF06-003-C001_FACTORY_STUDIO_CANONICAL_ACTION_BRIDGE_CODEX_LOG.md`

## 1. VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

The architectural direction is correct and the implementation should be retained: Studio now crosses a real local process boundary into the canonical Python CLI for Generate and Reproduce; Solve/Validate/Analyze remain unavailable; candidate presentation identity is not forwarded; output is bounded beneath Factory output; and a committed Godot integration suite exercises real Generate→Reproduce `MATCH` behavior.

The cycle is not eligible for closure because capability truth and error/result truth are not yet strict enough at the Studio/Core boundary.

Finding summary:

- BLOCKER: 0
- MAJOR: 2
- MINOR: 3
- NOTE: 1

`SB-LF06-003` remains active and requires one bounded R01 remediation.

## 2. CONTRACT RECOVERY

The C001 prompt requires:

- exactly five Studio actions: Generate, Solve, Validate, Analyze, Reproduce;
- only Generate/Reproduce operational where backed by real canonical Core;
- Solve gated to M03, Validate gated pending standalone canonical validation, Analyze gated to M04;
- a narrow shell-free local process bridge;
- Core availability derived from a real local Core/entrypoint probe;
- real exit code plus safe stdout/stderr error evidence;
- canonical candidate identity controlled by Python Core, not `candidate_presentation`;
- real Generate evidence and metadata-backed Reproduce `MATCH`;
- governed output boundaries;
- draft state, action state and action evidence kept distinct;
- failed actions must not silently erase last successful evidence;
- truthful UI text;
- no provider/network/solver/difficulty/Content Platform/main-game scope creep.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub comparison `6eb7803f... -> a3410786...` shows one implementation commit changing only the matching builder log, Factory Studio docs/scripts/tests, and narrow existing boundary tests.

No root `TASKS.md`, canonical Python Core product semantics, provider code, gameplay solver, difficulty engine, Content Platform or main-game code changed.

Independent comparison `a3410786... -> 9cc87b4e...` changes only the matching builder log. Publication discipline is structurally correct.

## 4. ACCEPTANCE CRITERIA MATRIX

- Five requested action controls present: PASS.
- Generate uses canonical Python CLI: PASS.
- Reproduce uses canonical Python CLI + real metadata: PASS.
- Solve gated to M03: PASS.
- Validate unavailable: PASS.
- Analyze gated to M04: PASS.
- No WFC-as-gameplay-solver substitution: PASS.
- Candidate presentation label isolated from canonical identity: PASS.
- Shell-free discrete process invocation: PASS.
- Output beneath governed Factory output boundary: PASS.
- Real Generate→Reproduce integration: PASS.
- Capability availability based on real Core entrypoint: **FAIL**.
- Safe stderr/error evidence preserved: **FAIL**.
- UI remains truthful after successful generation: **PARTIAL / FAIL**.
- Failed action preserves last successful evidence: **FAIL**.
- Builder evidence log truthful about canonical control-plane reads: **FAIL (minor evidence issue)**.
- Root tracker unchanged by builder: PASS.
- No scope creep: PASS.

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claim: the gateway "probes availability" of the canonical Python Factory Core.

Repository truth: `_refresh_connection()` calls `_probe_executable()`, and `_probe_executable()` executes only `<configured executable> --version`. It never executes `factory_core_launcher.py` or imports the canonical package during the availability decision. Therefore a Python executable can be marked Core `AVAILABLE` even when the canonical launcher/import/CLI path is unusable.

Builder claim: the bridge captures output and maps nonzero failures safely.

Repository truth: both probe and action calls use `OS.execute(..., read_stderr=false)`. Canonical CLI errors are written to stderr, so the real diagnostic can be discarded and replaced by a generic message.

Builder claim: prior governance/control-plane reads included `.hiveai/TASKS.md` and `.hiveai/CYCLE_INDEX.md` "as required".

Repository truth at the starting GitHub commit: those files do not exist, root `TASKS.md` is the sole tracker, and `GOVERNANCE.md` explicitly prohibits creating or reviving legacy H!veAI tracker/control-plane files. The immutable C001 log therefore contains an inaccurate process statement.

## 6. FILE / SYMBOL EVIDENCE

### Accepted bridge

`level_factory/scripts/factory_core_launcher.py` is a thin transport adapter. It adds repository `src/` to `sys.path`, imports `scrubbots_pixel_factory.cli.main`, and delegates directly to canonical `main()`. It does not duplicate generator or reproduction logic.

`factory_core_gateway.gd::_generate_arguments()` sends difficulty, width, height, seed, mode and output only. It does not pass `--candidate-id`; therefore the presentation label does not become canonical identity.

`FUTURE_ACTION_REASONS` keeps Solve, Validate and Analyze unavailable with truthful dependency language.

### Defective availability probe

`FactoryCoreGateway._refresh_connection()` marks status `AVAILABLE` when `_probe_executable(python_executable)` is true.

`_probe_executable()` runs only:

`OS.execute(executable, PackedStringArray(["--version"]), captured, true, false)`

This proves only that an executable responds successfully to `--version`; it does not prove the repository launcher or canonical Core import/CLI is executable.

### Lost stderr

`_execute_core()` calls:

`OS.execute(python_executable, arguments, captured, true, false)`

The final `false` means stderr is not captured into the action diagnostic path. Canonical CLI user-facing errors are printed to stderr.

### Stale workspace truth

`FactoryStudioWorkspacePage.show_surface("Generate")` always sets detail text to:

`Editable presentation draft only. No generation has occurred.`

That text remains visible after a successful Generate because action completion does not update the workspace detail. It directly conflicts with the successful Core evidence displayed below it.

### Last-success evidence overwrite

`FactoryStudioTargetControls._on_action_pressed()` always assigns the newest result to `_last_action_result`. `_render_action_result()` renders only that current result. A subsequent FAILED/UNAVAILABLE action therefore replaces the previously visible successful Core evidence. The gateway retains the metadata path, but the presentation does not preserve a separate last-success evidence record as required.

## 7. FOCUSED TEST EVIDENCE

The committed integration runner is substantive and should be retained. It:

- instantiates the real Studio scene;
- confirms missing configured executable is UNAVAILABLE;
- exercises a real canonical Generate;
- checks canonical candidate identity differs from presentation label;
- exercises real metadata-backed Reproduce;
- requires `MATCH`;
- checks output containment;
- verifies Solve/Validate/Analyze remain disabled.

However it does not test the false-positive availability case where the executable itself runs successfully but the canonical launcher/Core entrypoint fails. It also checks only FAILED state/nonzero exit for an invalid request, not preservation of the canonical stderr diagnostic. It does not test successful evidence retention after a later failure.

## 8. REGRESSION EVIDENCE

Builder-reported evidence includes:

- retained committed Studio runtime suite: PASS;
- real Studio/Core action integration suite: PASS;
- focused Python suite: 40 passed;
- corrected full suite: 694 passed with the known pytest cache warning;
- compile checks: PASS;
- direct canonical Generate/Reproduce smoke: PASS;
- normal Godot smoke: PASS.

These are useful builder-executed results, but they do not override the direct contract defects above.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- no shell command string, `cmd /c`, PowerShell or Bash;
- executable and arguments are discrete;
- no network/provider calls;
- output containment rejects obvious path escape;
- no candidate identity injection from the presentation label;
- no solver/difficulty fabrication.

Required hardening:

- Core availability must prove the launcher/canonical CLI path, not merely an executable version response;
- action diagnostics must capture stderr safely;
- no environment contents should be echoed while implementing the stronger probe.

## 10. ARCHITECTURE CONSISTENCY

The one-Core architecture remains intact. Godot is orchestration/presentation, and Python remains generator/request/quality/reproduction authority.

The R01 must not replace this architecture. It should only make the bridge's availability/error/result truth strict.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Root `TASKS.md` was untouched by the builder: PASS.

Publication is log-only after implementation: PASS.

C001 log control-plane statement is inaccurate: `.hiveai/TASKS.md` and `.hiveai/CYCLE_INDEX.md` are absent from canonical GitHub at the recorded start, while governance says root `TASKS.md` is sole tracker and legacy control-plane files must not be revived. The used log is immutable and must not be rewritten. R01 should record the correction explicitly in its new log.

## 12. FINAL REPOSITORY STATE

Product implementation retained at:

`a34107864d44118762bcde3a35f7c04a5633a4a4`

Observed terminal builder publication:

`9cc87b4edb493f0d3848aeaec2947b718a5c2127`

No evidence of builder modification to root tracker.

## 13. OPEN CROSS-MILESTONE FINDINGS

Solve remains correctly gated to M03.

Analyze remains correctly gated to M04.

Standalone Validate remains correctly unavailable pending a canonical capability.

These are dependency gates, not defects in C001.

## 14. DEFECTS BY SEVERITY

### F-SB-LF06-003-MAJOR-001 — Core availability can be falsely reported AVAILABLE

Affected: `level_factory/scripts/factory_core_gateway.gd`, `_refresh_connection()`, `_probe_executable()`.

Current behavior: any configured/discovered executable returning zero for `--version` is sufficient to mark canonical Core AVAILABLE.

Required behavior: AVAILABLE only after the actual committed launcher/canonical CLI entrypoint is successfully probed from the same executable. A working Python with a broken/missing/incompatible canonical Core path must remain UNAVAILABLE/ERROR and Generate must remain disabled.

### F-SB-LF06-003-MAJOR-002 — Canonical stderr diagnostics are discarded

Affected: `FactoryCoreGateway._execute_core()` and relevant probe execution.

Current behavior: `OS.execute(..., read_stderr=false)` drops canonical CLI stderr, including expected user-facing contract errors.

Required behavior: capture stderr into bounded safe diagnostics. Nonzero actions must retain the real exit code and a sanitized/truncated canonical diagnostic where available.

### F-SB-LF06-003-MINOR-003 — Generate workspace text becomes false after successful Generate

Affected: `factory_studio_workspace_page.gd` and/or action-result integration.

Current behavior: Generate page says `No generation has occurred` even after successful canonical Generate evidence is displayed.

Required behavior: use wording that remains true before and after actions, or update the workspace action state from real evidence without conflating draft validity with action execution.

### F-SB-LF06-003-MINOR-004 — Later failure silently replaces visible last-success evidence

Affected: `factory_studio_target_controls.gd` presentation state.

Current behavior: `_last_action_result` is overwritten by every result, and the result readout renders only the newest result.

Required behavior: retain a separate last-success Core evidence snapshot/path and keep it visible or deterministically retrievable after a later FAILED/UNAVAILABLE action. Current action result may still show the failure.

### F-SB-LF06-003-MINOR-005 — Builder log claims reads of nonexistent legacy control-plane files

Affected: immutable C001 builder log evidence discipline.

Current behavior: log claims `.hiveai/TASKS.md` and `.hiveai/CYCLE_INDEX.md` were read "as required", but they are absent from the canonical starting commit and conflict with governance.

Required behavior: do not edit the C001 log. R01 log must explicitly correct the record and use only canonical GitHub/root `TASKS.md` authority.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

A future bridge protocol could avoid parsing human CLI summary strings by introducing a separately audited machine-readable action-result contract. That is not required for this remediation and must not be invented in R01.

## 16. UNVERIFIED ITEMS

This audit did not independently execute the owner's Windows Godot/Python binaries. Builder runtime/test results are treated as builder evidence. GitHub source, diffs, commit boundaries, contracts and publication chronology were independently inspected.

## 17. REGRESSION RISK

R01 risk is low-to-moderate if bounded to gateway probing/error capture and presentation evidence truth. Do not change canonical Core semantics, output bundle formats, generation/reproduce commands or action dependency gates.

## 18. AUDIT CONFIDENCE

High for committed source/diff/contract findings.

Medium-high for runtime disposition because Windows-local commands were not independently rerun by ChatGPT.

## 19. FINAL VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

The action bridge is real and useful, but strict capability/error/presentation truth is not yet sufficient for closure.

## 20. REQUIRED REMEDIATION

Open one bounded R01 that:

1. probes the actual committed launcher/canonical CLI entrypoint before marking Core AVAILABLE;
2. captures and safely surfaces canonical stderr diagnostics;
3. removes the stale `No generation has occurred` contradiction;
4. preserves separate last-success action evidence across later failures;
5. adds runtime/regression tests for those cases;
6. explicitly corrects the legacy-control-plane read claim in the new immutable R01 log;
7. preserves the accepted Generate/Reproduce bridge, action gates, candidate identity isolation and output boundary;
8. does not begin SB-LF06-004 or any extension/milestone work.
