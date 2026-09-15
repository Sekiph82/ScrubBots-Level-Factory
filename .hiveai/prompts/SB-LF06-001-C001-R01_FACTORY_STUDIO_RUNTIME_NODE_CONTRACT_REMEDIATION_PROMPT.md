# SB-LF06-001-C001-R01 — Factory Studio Runtime Node Contract Remediation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Remediate only the strict-audit findings for:

`SB-LF06-001 — Build @tool/editor-facing workspace. [MIGRATION]`

Source audit:

`.hiveai/audits/SB-LF06-001-C001_FACTORY_STUDIO_CANONICAL_CORE_WORKSPACE_MIGRATION_STRICT_AUDIT.md`

This is a bounded remediation. Do not begin `SB-LF06-002`, `SB-LF06-003`, `SB-LFX-001..017`, solver, Dashboard, Import, Library, provider, review, batch, Content Platform, or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this remediation prompt;
3. the strict audit above;
4. original `SB-LF06-001-C001` prompt;
5. original finalized builder log;
6. `level_factory/scenes/factory_studio.tscn`;
7. all current `level_factory/scripts/*.gd`;
8. `level_factory/project.godot`;
9. `level_factory/docs/FACTORY_STUDIO_WORKSPACE.md`;
10. `tests/unit/test_sb_lf06_001_factory_studio_workspace.py` and the LF00 focused regression tests touched by C001.

Before any implementation edit create and verify:

`.hiveai/codex-logs/SB-LF06-001-C001-R01_FACTORY_STUDIO_RUNTIME_NODE_CONTRACT_REMEDIATION_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## F-SB-LF06-001-MAJOR-001 — Repair the real scene/runtime node contract

The committed scene places Navigation at:

`Frame/Layout/Body/NavigationPanel/Navigation`

while `factory_studio_shell.gd` currently resolves:

`Frame/Layout/Body/Navigation`

Correct the contract so the shell resolves the actual committed Navigation node consistently.

Required:

- `_ready()` must resolve the real Navigation node;
- `_get_configuration_warnings()` must check the same real node contract;
- the shell must connect `surface_selected` successfully;
- the initial Dashboard presentation must be reached after `_ready()`;
- no redesign or later feature implementation is authorized merely to fix the path.

Use one maintainable source of path truth where practical so `_ready()` and configuration warnings cannot silently drift apart again.

## F-SB-LF06-001-MINOR-002 — Add genuine executable Godot runtime evidence

The existing Python focused tests are useful static guards but did not instantiate the scene, so they missed the MAJOR defect.

Add a focused executable Godot runtime/scene-instantiation regression that proves the real committed workspace initializes.

The automated runtime evidence must fail if the node contract is broken and must prove at minimum:

1. `res://scenes/factory_studio.tscn` loads and instantiates;
2. the root scene can enter the tree and execute `_ready()` without script/runtime errors;
3. Navigation resolves at its real scene path and is a `FactoryStudioNavigation`;
4. Workspace resolves and is a `FactoryStudioWorkspacePage`;
5. the navigation signal is connected to the workspace presentation path;
6. initial surface is Dashboard;
7. initial Dashboard remains truthful, with no fabricated operational values;
8. Core status remains truthful `UNAVAILABLE` in this foundation;
9. one navigation selection can be exercised deterministically without invoking providers/import/solver/QA/business logic;
10. the runtime test exits non-zero on assertion/runtime failure.

Prefer a small Godot-local headless test/smoke script under `level_factory/tests/` or an equivalently explicit executable contract. A Python grep-only test is not sufficient for this finding.

Run the actual executable test command and record stdout/stderr and exit status in the builder log. Runtime script errors in stderr/stdout must count as failure even if a surrounding Godot process would otherwise exit zero.

Also strengthen the Python focused test enough to statically bind the expected scene hierarchy/path where useful, but do not substitute that for the executable Godot test.

## F-SB-LF06-001-MINOR-003 — Publication/log discipline

Do not rewrite the original C001 builder log.

For this R01 log:

- keep entries in actual chronological order;
- distinguish implementation commit, evidence checkpoint if any, and true observed terminal publication;
- do not call a commit terminal/final if another builder commit is intentionally planned after it;
- if a self-referential final SHA cannot be embedded without creating another commit, state the last pushed equality checkpoint truthfully instead of manufacturing a false terminal claim.

## Architecture constraints

Preserve all accepted C001 architecture:

- Python Factory Core remains canonical;
- no GDScript compiler/generator/solver/validator/palette/provenance clone;
- gateway remains status-only for this remediation;
- no provider/network/API/credential/subprocess integration;
- no Studio persistence/database/tracker;
- no fake jobs, metrics, balances, candidates, QA, solver or readiness data;
- root `TASKS.md` remains sole tracker;
- no `Sekiph82/Scrubbots` access or modification.

## Allowed scope

Allowed only as required by the findings:

- `level_factory/scripts/factory_studio_shell.gd`;
- `level_factory/scenes/factory_studio.tscn` only if genuinely required for consistent node contract;
- `level_factory/tests/**` for executable runtime regression;
- `tests/unit/test_sb_lf06_001_factory_studio_workspace.py` for strengthened static evidence;
- very narrow documentation correction if behavior/command documentation changes;
- matching R01 builder log.

Do not alter root Python Factory Core production algorithms.

## Required verification

Run and record at minimum:

1. the new executable Godot runtime/scene-instantiation regression;
2. `python -m pytest -q tests/unit/test_sb_lf06_001_factory_studio_workspace.py`;
3. prior LF00-001, LF00-002, LF00-006, LF00-007, LF00-008 focused suites;
4. full `python -m pytest -q`;
5. `python -m compileall -q src tests`;
6. package import smoke;
7. module CLI help and installed CLI help if available;
8. `godot --headless --path level_factory --editor --quit`;
9. main-scene runtime boot with output inspected for runtime/script errors, not only exit code;
10. `git diff --check`;
11. changed-file inspection proving no root `TASKS.md`, `src/`, provider, Content Platform, or main-game implementation changes;
12. no credential/network/provider use.

Record every failed command and correction truthfully.

## Acceptance criteria

PASS eligibility requires all of the following:

- [ ] shell node path matches the real committed scene hierarchy;
- [ ] `_ready()` completes without node-resolution/runtime errors;
- [ ] configuration warnings use the same valid navigation contract;
- [ ] initial Dashboard state is actually reached;
- [ ] executable Godot regression would fail if the bad C001 path is restored;
- [ ] runtime regression passes with no script/runtime error output;
- [ ] Core status remains truthful `UNAVAILABLE`;
- [ ] no later M06/LFX functionality is implemented;
- [ ] root `TASKS.md` unchanged;
- [ ] Python Factory Core production code unchanged;
- [ ] static focused tests pass;
- [ ] prior LF00 regressions pass;
- [ ] full regression passes;
- [ ] Godot editor/headless smoke passes;
- [ ] no provider/network/credential/main-game/Content Platform changes;
- [ ] R01 builder log is finalized and pushed truthfully;
- [ ] builder stops for independent ChatGPT audit.

## GitHub handoff

Push remediation implementation, tests, and finalized R01 builder log to `main`.

At handoff provide only:

1. full GitHub URL of the finalized R01 builder log;
2. remediation implementation commit SHA;
3. final publication/equality checkpoint SHA, described truthfully.

Then stop for independent ChatGPT strict audit.
