# SB-LF06-003-C001 — Factory Studio Canonical Action Bridge
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Implement only:

`SB-LF06-003 — Generate/Solve/Validate/Analyze/Reproduce actions. [PARTIAL]`

This cycle builds the **Factory Studio action layer** over the canonical Python Factory Core.

The accepted Studio shell (`SB-LF06-001`) and target controls (`SB-LF06-002`) must be retained. The Godot project remains presentation/orchestration. The root Python implementation remains the only generator/request/quality/reproduction authority.

At the current repository snapshot, the canonical CLI exposes these real commands:

- `generate`;
- `reproduce`;
- `batch`;
- `semantic-normalize`.

There is currently **no standalone canonical gameplay `solve` command, no standalone `validate` command, and no canonical difficulty/metrics `analyze` command**. Existing WFC code is generation-constraint infrastructure and is not the ScrubBots gameplay solver.

Therefore this task must expose the five requested Studio actions truthfully, but must operationalize only actions that have a real canonical Core capability today. Missing capabilities must be visibly unavailable, not simulated.

Do not begin any `SB-LFX-*` extension, Dashboard operations, Import, Source Art Library, Content Platform, provider integration, M03 gameplay solver implementation, M04 difficulty engine implementation, or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this prompt;
3. `.hiveai/audits/SB-LF06-002-C001-R01_COMMITTED_GODOT_RUNTIME_REGRESSION_REMEDIATION_STRICT_AUDIT.md`;
4. `.hiveai/audits/SB-LF06-001-C001-R01_FACTORY_STUDIO_RUNTIME_NODE_CONTRACT_REMEDIATION_STRICT_AUDIT.md`;
5. `level_factory/scenes/factory_studio.tscn`;
6. all current `level_factory/scripts/factory_studio_*.gd` and `factory_core_gateway.gd`;
7. `level_factory/tests/factory_studio_runtime_suite.gd`;
8. focused LF06-001/LF06-002 Python tests;
9. `src/scrubbots_pixel_factory/cli/main.py`, especially `_generate`, `_reproduce`, `_parser`, exit codes and request flags;
10. `src/scrubbots_pixel_factory/cli/__main__.py`;
11. `pyproject.toml` console-script contract;
12. canonical output/bundle contracts relevant to generated `metadata.json` and reproduction;
13. repository/project boundary tests and governance.

Before implementation create and verify:

`.hiveai/codex-logs/SB-LF06-003-C001_FACTORY_STUDIO_CANONICAL_ACTION_BRIDGE_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## 1. Action surface

The Generate Studio surface must expose clearly identifiable action controls for exactly:

- **Generate**;
- **Solve**;
- **Validate**;
- **Analyze**;
- **Reproduce**.

Action availability must reflect canonical capability truth, not UI ambition.

At this snapshot:

### Generate

May become operational only through the canonical Python Core `generate` path.

### Reproduce

May become operational only through the canonical Python Core `reproduce` path using a real candidate `metadata.json` bundle.

### Solve

Must be present but **UNAVAILABLE / dependency-gated** because M03 gameplay solver is not implemented. Do not route it to WFC and do not fabricate a solve result.

### Validate

Must be present but **UNAVAILABLE / dependency-gated** unless you can point to an already existing standalone canonical validation action that was missed by this prompt. The quality gate performed internally by `generate` must not be relabeled as an independent Validate action.

### Analyze

Must be present but **UNAVAILABLE / dependency-gated** because M04 canonical solver-derived difficulty/metrics analysis is not implemented. Do not invent difficulty metrics or use board size/color count as analysis.

Disabled/unavailable actions must explain the dependency truthfully.

This action layer is considered complete for the current capability snapshot when all five actions are represented and missing Core capabilities are truth-gated rather than simulated. Later M03/M04/M05 work may enable existing gates without redefining this UI contract.

## 2. Canonical Core bridge

Replace the current status-only Factory Core gateway with a **narrow local-process adapter** only as needed to execute authorized canonical Core actions.

The bridge must not implement generation or validation logic itself.

Allowed responsibilities:

- discover whether a supported local Python/Core entrypoint is executable;
- report truthful AVAILABLE / UNAVAILABLE / ERROR state;
- report a capability matrix for the Studio action layer;
- execute canonical Core commands with discrete argument arrays;
- capture exit code/stdout/stderr;
- return a small structured action result to the presentation layer;
- resolve repository-local output/metadata paths safely.

Forbidden responsibilities:

- reimplement `GenerationRequest` validation in GDScript;
- reimplement generator routing;
- reimplement quality validation;
- reimplement candidate identity;
- reimplement reproduction comparison;
- reimplement solver/difficulty logic;
- call providers or network services;
- alter canonical Python semantics just to fit the UI.

A minimal repository-local Python launcher/bridge is acceptable if required for clean-checkout invocation, but it must be a **thin transport adapter** that delegates to canonical `scrubbots_pixel_factory.cli` code. It must not become a second Core.

Do not hard-code the owner's absolute Windows path.

## 3. Process-safety contract

If Godot process execution is introduced in this cycle, it is authorized only inside the bounded canonical-Core gateway/adapter.

Requirements:

- no `cmd /c`, PowerShell, Bash or shell-string interpolation;
- pass executable and arguments as discrete values;
- do not concatenate an operator seed/path into a shell command;
- no provider/network command;
- no arbitrary user-command execution field;
- expose bounded, known canonical action names only;
- one action result must be attributable to one exact invocation;
- handle missing executable/bridge as `UNAVAILABLE`, not a crash or fake success;
- nonzero canonical Core exits must surface as failed/rejected/mismatch state with the real exit code and safe error text;
- do not leak secrets/environment contents into UI or logs.

If the local Core cannot be reached cleanly, keep Generate/Reproduce unavailable and record the blocker rather than bypassing the boundary.

## 4. Generate action contract

Generate must consume the accepted LF06-002 presentation draft:

- difficulty;
- width;
- height;
- seed text;
- generator mode.

Do not silently reinterpret values in GDScript. The canonical CLI must make the canonical validity decision.

Important identity rule:

The LF06-002 `candidate_presentation` field is **not a canonical candidate ID**. Do **not** pass it as `--candidate-id`. Let canonical Core produce its normal identity unless a separately audited canonical identity workflow later authorizes otherwise.

For the current control set, do not invent style/theme/palette/options values. Omit unsupported/unrepresented optional flags and allow the canonical CLI defaults/contracts to apply.

Generated files must be written only inside an approved Factory output/staging boundary, preferably under a dedicated Studio run area beneath `level_factory/output/` or another already governed generated-output boundary.

A Studio run/session directory may have a presentation-only run ID, but that ID must not be confused with the canonical candidate ID.

On success, the UI result state must expose at minimum, from real Core evidence where available:

- action = Generate;
- success/failure disposition;
- canonical Core exit code;
- canonical candidate ID;
- selected canonical seed as reported by Core;
- mode;
- dimensions;
- grid hash;
- output/bundle path;
- path to the resulting `metadata.json` if it can be resolved safely.

Do not invent these values from the draft if the Core did not actually return/produce them.

## 5. Reproduce action contract

Reproduce must execute canonical Core `reproduce` against a real `metadata.json`.

Support at least one truthful source path:

- the `metadata.json` from the most recent successful Generate action in the current Studio session.

You may additionally provide a bounded local metadata-path selector/text field if appropriate, but do not turn this task into Import/Library functionality.

Reproduce success requires canonical Core success and its real `MATCH` result. A mismatch/nonzero exit must be shown as failure/mismatch, never as success.

Reproduce must not silently overwrite the original candidate bundle. If an optional reproduction output is used, write it only to an approved generated-output boundary.

## 6. Action-state model

Add a small deterministic presentation model for action state, for example:

- `IDLE`;
- `RUNNING` if execution is asynchronous;
- `SUCCESS`;
- `FAILED`;
- `UNAVAILABLE`.

The exact enum/names may differ, but the UI must distinguish:

- editable draft state;
- Core connection/capability state;
- action execution state;
- action result evidence.

Do not mark a draft `VALID` merely because Generate is available.

Do not mark Solve/Validate/Analyze successful without canonical evidence.

Prevent overlapping action execution if the implementation is not explicitly concurrency-safe.

## 7. Core capability truth

`FactoryCoreGateway` must no longer use a hard-coded `AVAILABLE` status merely because this task exists.

Availability must be derived from a real local bridge/entrypoint probe or remain `UNAVAILABLE`.

Capability presentation must distinguish at least:

- Generate: supported/unavailable;
- Reproduce: supported/unavailable;
- Solve: unavailable pending M03;
- Validate: unavailable pending canonical standalone validation integration;
- Analyze: unavailable pending M04.

Do not infer Solve support from WFC.

Do not infer Analyze support from current difficulty labels, dimensions, color counts, structural QA or generation quality.

## 8. UI behavior

Preserve accepted navigation and target controls.

Required UI behavior:

- Generate page shows the target form plus action area;
- operational actions are enabled only when their canonical capability is available and required input exists;
- unavailable actions remain visible and explain why;
- action result/status area is clearly separate from draft state;
- Dashboard and all other surfaces remain truthful placeholders;
- no automatic promotion/acceptance occurs after Generate;
- leaving and returning to Generate must not corrupt the current draft/action evidence;
- a failed action must not erase the last successful evidence silently.

Do not implement Preview/metrics/editor features from SB-LF06-004+ in this cycle beyond minimal text/path evidence required for the actions.

## 9. Repository-local / clean-checkout execution

The canonical action integration must not depend on owner-specific absolute paths or untracked helper scripts.

Any bridge/helper required for Studio→Core execution must be committed.

Tests must prove that a synchronized checkout can discover/invoke the canonical Core through the documented development setup without temporary helper creation.

If Python executable discovery is configurable, document the bounded configuration mechanism and test missing/invalid configuration truthfully.

Do not commit a virtualenv or executable binary.

## 10. Required automated tests

Add/extend evidence proving at minimum:

1. accepted LF06-001/LF06-002 project-local Godot runtime suite remains green;
2. action controls for Generate/Solve/Validate/Analyze/Reproduce are present;
3. Solve/Validate/Analyze are visibly unavailable and cannot execute fake work at this snapshot;
4. candidate presentation label is never forwarded as canonical `--candidate-id`;
5. bridge uses bounded canonical commands/argument arrays, not shell interpolation;
6. missing Core/Python entrypoint produces truthful UNAVAILABLE behavior;
7. a fast deterministic real Generate integration case invokes canonical Core and produces a real candidate bundle in an isolated disposable/approved output path;
8. the resulting metadata can be passed to real canonical Reproduce and yields `MATCH`;
9. nonzero/error Core execution maps to FAILED/MISMATCH rather than success;
10. no provider/network call occurs;
11. existing cross-language difficulty/mode/dimension guards remain green;
12. root `TASKS.md` remains untouched by builder.

At least one integration test must cross the actual Studio/Core process boundary or the exact committed bridge used by Studio. Do not satisfy this cycle only with grep/source assertions.

Do not make ordinary Python-only unit tests depend unconditionally on launching the Godot editor if repository conventions do not already require that. Keep the existing committed Godot runtime command separately executable.

## 11. Required regression and verification

Run and record at minimum:

1. new focused LF06-003 tests;
2. LF06-001/LF06-002 focused regressions;
3. committed Godot runtime suite;
4. real canonical Generate→Reproduce integration smoke using deterministic small dimensions/seed and isolated output;
5. LF01 dimension/request tests;
6. relevant CLI generation/reproduce tests;
7. full `python -m pytest -q`;
8. `python -m compileall -q src tests` plus any intentionally added thin bridge/tool file;
9. normal `godot --headless --path level_factory --quit` smoke;
10. `git diff --check`;
11. changed-file review proving no root `TASKS.md`, provider, solver implementation, difficulty implementation, Dashboard operation, Import, Library, Content Platform or main-game scope creep.

Record failed commands and corrections truthfully.

## 12. Scope notes for current canonical capabilities

Do not confuse these existing features:

- `generate` already performs its canonical generation + quality acceptance path;
- `reproduce` already performs canonical recorded-bundle reproduction and comparison;
- `batch` is M08 workflow and is not part of this action cycle;
- `semantic-normalize` is not the Generate action and is not Import workflow authorization;
- WFC is not gameplay Solve;
- generation quality evaluation is not permission to invent a standalone Validate command;
- current difficulty label is not Analyze output.

If repository inspection proves a genuine canonical standalone Validate/Analyze/Solve capability already exists outside the known CLI, record the evidence before enabling it. Otherwise keep the action gated.

## 13. Allowed scope

Allowed only as needed for this task:

- `level_factory/scenes/**`;
- `level_factory/scripts/**`;
- `level_factory/tests/**`;
- narrow Factory Studio docs/README updates describing the action bridge;
- a narrowly scoped committed repository-local Python transport/launcher if required;
- focused Python tests for bridge/process/action contracts;
- matching builder log.

Canonical Python Core product semantics should remain unchanged. Do not modify generator/request/quality/reproduction semantics to make Studio integration easier.

## 14. Acceptance criteria

PASS eligibility requires all of the following:

- [ ] all five requested Studio action controls are present;
- [ ] Generate is operational only through real canonical Core when available;
- [ ] Reproduce is operational only through real canonical Core when metadata is available;
- [ ] Solve is truthfully dependency-gated to M03;
- [ ] Validate is truthfully unavailable unless a real standalone canonical validation action exists;
- [ ] Analyze is truthfully dependency-gated to M04;
- [ ] no WFC-as-gameplay-solver substitution;
- [ ] no fake validation/difficulty/analysis result;
- [ ] Factory Core gateway derives availability from real local integration state;
- [ ] process invocation is bounded and shell-free;
- [ ] no owner absolute path or untracked helper dependency;
- [ ] candidate presentation label never becomes canonical candidate identity;
- [ ] real Generate result evidence comes from Core output/artifacts;
- [ ] real Reproduce uses real metadata and canonical MATCH semantics;
- [ ] generated/reproduced files remain in governed output boundaries;
- [ ] no auto-promotion/owner acceptance;
- [ ] real integration tests and committed Godot runtime tests pass;
- [ ] prior LF06/LF01 regressions and full suite pass;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] no provider/network/solver/difficulty/Content Platform/main-game scope creep;
- [ ] finalized builder log is published truthfully;
- [ ] builder stops for independent ChatGPT strict audit.

## Publication discipline

Use the accepted non-self-referential pattern:

1. implementation commit(s);
2. push and record final implementation equality checkpoint;
3. final log-only publication commit;
4. hand the actual final publication SHA to the user externally.

Do not add a post-final equality-log commit.

## GitHub handoff

Push implementation/tests/finalized builder log to `main`.

At completion give the user only:

1. full GitHub URL of the finalized builder log;
2. final implementation commit SHA;
3. actual final publication commit SHA.

Then stop for independent ChatGPT strict audit.
