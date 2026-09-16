# SB-LF06-003-C001-R01 — Core Availability, Error & Result Truth Remediation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Remediate only the findings from:

`.hiveai/audits/SB-LF06-003-C001_FACTORY_STUDIO_CANONICAL_ACTION_BRIDGE_STRICT_AUDIT.md`

for:

`SB-LF06-003 — Generate/Solve/Validate/Analyze/Reproduce actions. [PARTIAL]`

The C001 product architecture is retained. Do not redesign the action layer.

Preserve:

- real canonical Python Core Generate;
- real metadata-backed canonical Reproduce;
- `MATCH` semantics;
- Solve unavailable pending M03;
- Validate unavailable pending a standalone canonical capability;
- Analyze unavailable pending M04;
- candidate presentation label isolation;
- governed `level_factory/output/` boundary;
- shell-free discrete process invocation;
- committed Godot action integration suite;
- canonical Python Core as the only generator/request/quality/reproduction authority.

Do not begin `SB-LF06-004`, any `SB-LFX-*` task, M03, M04, M05, providers, Dashboard operations, Import, Library, Content Platform or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this R01 prompt;
3. `.hiveai/audits/SB-LF06-003-C001_FACTORY_STUDIO_CANONICAL_ACTION_BRIDGE_STRICT_AUDIT.md`;
4. original `SB-LF06-003-C001` prompt;
5. finalized C001 builder log;
6. `GOVERNANCE.md`;
7. `level_factory/scripts/factory_core_gateway.gd`;
8. `level_factory/scripts/factory_core_launcher.py`;
9. `level_factory/scripts/factory_studio_target_controls.gd`;
10. `level_factory/scripts/factory_studio_workspace_page.gd`;
11. `level_factory/tests/factory_studio_action_integration_suite.gd`;
12. focused LF06-003 Python tests;
13. canonical Python CLI error/exit behavior in `src/scrubbots_pixel_factory/cli/main.py`.

Before product edits create:

`.hiveai/codex-logs/SB-LF06-003-C001-R01_CORE_AVAILABILITY_ERROR_AND_RESULT_TRUTH_REMEDIATION_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## F-SB-LF06-003-MAJOR-001 — Probe the real canonical Core entrypoint

### Current defect

`FactoryCoreGateway._refresh_connection()` currently marks Core AVAILABLE when `_probe_executable()` can run only:

`<executable> --version`

That proves the executable exists, not that the committed launcher and canonical `scrubbots_pixel_factory.cli` path is actually executable.

A working Python with a broken/missing/incompatible Core import path can therefore produce a false `AVAILABLE` status and enable Generate.

### Required target behavior

Core status may become `AVAILABLE` only after the same selected executable successfully crosses the committed launcher/canonical CLI boundary.

Use a narrow, side-effect-free probe. Preferred shape:

- execute the selected Python executable with the committed `factory_core_launcher.py` and `--help`, or another equally narrow no-generation canonical launcher probe;
- require exit code `0`;
- confirm enough expected canonical CLI identity/capability evidence to know the launcher imported and delegated successfully;
- do not generate artifacts during probing;
- do not contact network/providers;
- do not echo the executable/environment value into logs/UI.

It is acceptable to retain a separate cheap executable sanity check, but `AVAILABLE` must depend on the actual launcher/Core probe.

If Python exists but the launcher/Core probe fails, status must remain `UNAVAILABLE` or `ERROR`, Generate must remain disabled, and the reason must be truthful.

Do not introduce a new canonical Core command merely for convenience unless there is a compelling repository-native reason. Prefer the existing launcher `--help` contract.

### Required tests

Add a regression proving a superficially executable command must not make Core AVAILABLE when the launcher/Core entrypoint itself cannot execute successfully.

Use a safe deterministic test technique. Do not depend on shell interpolation or external downloads.

Keep the existing real no-override canonical Core integration PASS path.

## F-SB-LF06-003-MAJOR-002 — Preserve canonical stderr diagnostics

### Current defect

Gateway process calls use `OS.execute(..., read_stderr=false)`.

The canonical CLI prints expected user-facing contract errors to stderr, so the Studio can lose the real diagnostic and replace it with a generic failure message.

### Required target behavior

For canonical launcher/action invocations whose diagnostics are surfaced by the gateway:

- capture stderr together with the bounded process output using the supported Godot `OS.execute` contract;
- preserve the real exit code;
- expose a safe, bounded/truncated canonical diagnostic when available;
- do not expose whole environment contents or secrets;
- success parsing must still require recognized canonical `SUCCESS`/`MATCH` evidence rather than treating arbitrary output as success.

The existing safe-message length bound may remain or be tightened.

### Required tests

The invalid canonical request integration case must assert not only nonzero/FAILED but also that the safe result reason contains the expected canonical CLI diagnostic, such as the invalid generation request/difficulty error, proving stderr reached the bridge.

Also prove a failure cannot be promoted to SUCCESS merely because unrelated stdout exists.

## F-SB-LF06-003-MINOR-003 — Remove post-success workspace contradiction

### Current defect

The Generate workspace detail always says:

`No generation has occurred.`

After real canonical Generate succeeds, the action readout displays successful evidence while this static workspace sentence remains visible and becomes false.

### Required target behavior

Make the workspace wording truthful in all states without conflating editable draft validity with action execution.

A simple static sentence that remains true before and after actions is acceptable, for example conceptually:

`Editable presentation draft; canonical execution evidence is shown separately in Action result.`

Alternatively, update the workspace from real action evidence through a narrow presentation signal. Do not add a new truth store.

Do not mark the draft VALID after Generate.

### Required tests

After a successful Generate, no visible Generate-page status/detail string may claim that no generation has occurred.

Draft readout may continue to say the **draft itself** is presentation-only/unvalidated.

## F-SB-LF06-003-MINOR-004 — Preserve last-success Core evidence across later failures

### Current defect

The target controls have only `_last_action_result`. Every subsequent FAILED/UNAVAILABLE action overwrites the successful result presented to the operator.

The C001 prompt requires a failed action not to silently erase the last successful evidence.

### Required target behavior

Maintain separate presentation state for:

- current/latest action result; and
- last successful canonical Core evidence.

On SUCCESS, update both current result and last-success evidence.

On FAILED/UNAVAILABLE, update the current result but retain the prior last-success evidence unchanged.

The last-success record must remain deterministically retrievable and/or visibly represented so an operator can still identify the previous successful candidate/metadata/output after a failure.

Do not treat retained last-success evidence as proof that the current failed action succeeded.

The gateway may continue retaining `_last_successful_metadata_path` for Reproduce; presentation evidence must not rely only on that opaque path.

### Required tests

Integration sequence must prove:

1. real Generate succeeds;
2. capture its successful evidence;
3. trigger a deterministic later FAILED action;
4. current result reports FAILED with real nonzero exit;
5. separate last-success evidence still equals the prior Generate success;
6. Reproduce can still use the retained successful metadata where otherwise legal.

## F-SB-LF06-003-MINOR-005 — Correct evidence record without rewriting history

The immutable C001 builder log claims it read:

- `.hiveai/TASKS.md`;
- `.hiveai/CYCLE_INDEX.md`;

"as required by repository instructions."

Those files were absent from the canonical GitHub starting commit. `GOVERNANCE.md` states root `TASKS.md` is the sole tracker and legacy H!veAI control-plane files must not be created or revived.

Do not edit or rewrite the C001 log.

The new R01 builder log must explicitly state:

- the prior C001 control-plane read statement was inaccurate;
- canonical GitHub did not contain those legacy files at the C001 start;
- R01 uses root `TASKS.md` plus GitHub prompt/audit/governance authority only;
- no legacy tracker/control-plane file is created or revived.

This is evidence correction only, not a product feature.

## Accepted behavior that must not regress

The R01 must preserve all of the following:

- exactly five actions visible;
- Generate operational only through canonical CLI;
- Reproduce operational only through canonical CLI and real metadata;
- Solve disabled/unavailable with M03 reason;
- Validate disabled/unavailable with standalone-canonical-validation reason;
- Analyze disabled/unavailable with M04 reason;
- candidate presentation label never passed as `--candidate-id`;
- output roots remain under governed Factory output;
- Reproduce does not overwrite the Generate bundle;
- no auto-promotion/owner acceptance;
- no WFC gameplay-solver substitution;
- no fake Analyze/Validate/Solve evidence;
- no provider/network behavior;
- no canonical Python Core semantic changes.

## Allowed scope

Only as required for these findings:

- `level_factory/scripts/factory_core_gateway.gd`;
- `level_factory/scripts/factory_studio_target_controls.gd`;
- `level_factory/scripts/factory_studio_workspace_page.gd`;
- `level_factory/tests/factory_studio_action_integration_suite.gd`;
- narrow LF06-003 Python regression tests;
- narrow docs if needed to correct bridge behavior description;
- matching R01 builder log.

Modify `factory_core_launcher.py` only if absolutely necessary for a narrow side-effect-free probe. Do not add Core semantics there.

Do not modify root `TASKS.md`.

Do not change canonical Python generator/request/quality/reproduction semantics.

## Required verification

Run and record at minimum:

1. focused LF06-003 R01 tests;
2. real committed Studio/Core integration suite;
3. retained LF06-001/LF06-002 runtime suite;
4. a probe regression showing executable-present/Core-entrypoint-unavailable remains unavailable;
5. invalid canonical request proving stderr diagnostic capture;
6. success→failure evidence-retention sequence;
7. real deterministic Generate→Reproduce `MATCH` path;
8. LF01 dimension/request regressions;
9. relevant canonical CLI Generate/Reproduce tests;
10. full `python -m pytest -q`;
11. `python -m compileall -q src` plus authorized launcher if changed;
12. `godot --headless --path level_factory --quit`;
13. `git diff --check`;
14. changed-file review proving root `TASKS.md`, providers, solver/difficulty implementation, Dashboard, Import, Library, Content Platform, main-game and SB-LF06-004+ are untouched.

Record failed commands and corrections truthfully.

## Acceptance criteria

PASS eligibility requires all of the following:

- [ ] retained C001 action bridge remains operational;
- [ ] Core `AVAILABLE` requires a successful real launcher/canonical CLI probe, not only executable `--version`;
- [ ] wrong/incompatible Core path remains UNAVAILABLE/ERROR and cannot enable Generate;
- [ ] canonical stderr diagnostics are captured safely;
- [ ] nonzero exit preserves the real exit code and meaningful bounded canonical diagnostic;
- [ ] successful Generate/Reproduce parsing still requires canonical summary evidence;
- [ ] Generate workspace has no post-success `No generation has occurred` contradiction;
- [ ] current failure and last successful Core evidence are separate states;
- [ ] a failure does not erase prior successful candidate/metadata evidence;
- [ ] candidate presentation identity isolation remains intact;
- [ ] Solve/Validate/Analyze gates remain intact;
- [ ] output containment remains intact;
- [ ] real Generate→Reproduce `MATCH` integration remains green;
- [ ] prior LF06/LF01/full regressions remain green;
- [ ] R01 log explicitly corrects the prior legacy-control-plane read statement without modifying the C001 log;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] no scope creep;
- [ ] finalized R01 log published using the non-self-referential implementation/equality/log-only pattern;
- [ ] builder stops for independent ChatGPT strict audit.

## Publication discipline

Use:

1. implementation/remediation commit(s);
2. push and record the actual final implementation equality checkpoint;
3. one final log-only publication commit;
4. hand the actual final publication SHA externally.

Do not create a post-final equality-log commit.

## GitHub handoff

Push remediation/tests/finalized R01 builder log to `main`.

At completion give the user only:

1. full GitHub URL of the finalized R01 builder log;
2. final remediation implementation commit SHA;
3. actual final publication commit SHA.

Then stop for independent ChatGPT strict audit.
