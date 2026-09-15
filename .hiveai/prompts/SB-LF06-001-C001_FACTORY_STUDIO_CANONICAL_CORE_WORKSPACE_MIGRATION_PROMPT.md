# SB-LF06-001-C001 — Factory Studio Canonical-Core Workspace Migration
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Implement only:

`SB-LF06-001 — Build @tool/editor-facing workspace. [MIGRATION]`

Interpret the migrated requirement according to the current repository architecture:

- `level_factory/` is already the independently openable Godot 4 Factory project;
- the Python Factory Core under repository root remains canonical;
- the Studio is an operator/presentation/orchestration surface over canonical truth;
- the Studio must never become a second compiler, solver, validator, palette authority, provenance authority, or task tracker;
- this cycle builds the real Factory Studio workspace shell and its explicit canonical-Core integration boundary only;
- do **not** implement Dashboard metrics, Pixel Art import, Source Art Library, solver, provider execution, review workflow, batch retry, or any other later task in this cycle.

The owner-approved future Studio/operator plan is:

`docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`

The new `SB-LFX-001..017` tasks are requirements for later cycles, not permission to implement them now.

## Required reads before edits

Read completely from GitHub before implementation:

1. root `TASKS.md`;
2. `GOVERNANCE.md`;
3. `AGENTS.md`;
4. `level_factory/README.md`;
5. `level_factory/GOVERNANCE.md`;
6. `level_factory/project.godot`;
7. every current file under `level_factory/scenes/`, `level_factory/scripts/`, `level_factory/docs/`, and `level_factory/tests/`;
8. `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`;
9. `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`;
10. `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`;
11. `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`;
12. the closing strict audit for SB-LF00-007:
    `.hiveai/audits/SB-LF00-007-C001_GOVERNANCE_AND_COORDINATION_AUTHORITY_NORMALIZATION_STRICT_AUDIT.md`;
13. any relevant retained PAG-SP09 / historical Factory Studio evidence that exists **inside this GitHub repository**.

Do not search sibling local repositories for missing implementation. Do not use `Sekiph82/Scrubbots` as a substitute source tree.

Before any implementation edit create and verify:

`.hiveai/codex-logs/SB-LF06-001-C001_FACTORY_STUDIO_CANONICAL_CORE_WORKSPACE_MIGRATION_CODEX_LOG.md`

## 1. Preserve canonical architecture

The repository root Python package is canonical Factory Core.

Factory Studio must not duplicate or port into GDScript:

- LevelGenerationConfig semantics;
- generator/router algorithms;
- C01..C16 legality logic;
- normalization/compiler logic;
- QA/recognizability logic;
- provenance/hashing logic;
- batch identity logic;
- future ScrubBots gameplay solver semantics.

If Studio needs any of those later, it must call a narrow adapter/gateway to canonical Core rather than implement a second truth.

This cycle may define the interface/boundary for that gateway and expose truthful connection/capability state, but it must not invent a fake integration that claims canonical actions are wired when they are not.

## 2. Build a real Godot Factory Studio workspace shell

Replace the minimal bootstrap-only experience with a maintainable Godot 4 desktop workspace shell owned by `level_factory/`.

The shell must be directly runnable as the project's main scene and must include, at minimum:

- a clear `SCRUBBOTS Level Factory` application identity;
- a persistent top/header area;
- a primary navigation area;
- a content/workspace area;
- a status/footer area suitable for canonical-Core connection/status information;
- a deterministic initial/home view that boots with no local generated data and no network.

The owner-approved future navigation model is:

`Dashboard | Generate | Import | Library | Batches | Candidates | Review | QA | Providers | Outputs | Settings`

You may implement this as tabs/sidebar/buttons or an equivalent maintainable structure.

For surfaces not implemented in this cycle:

- provide clearly labeled placeholder/disabled panels or routes;
- state `NOT IMPLEMENTED` / `NOT AVAILABLE` truthfully where appropriate;
- do not display fabricated batch counts, provider balances, solver results, QA scores, or production readiness.

The UI should be useful as a migration foundation, not a decorative mockup that cannot host later features.

## 3. Canonical-Core gateway boundary

Create a narrow Factory Studio gateway/adapter boundary under `level_factory/scripts/` or an equivalent project-owned location.

Requirements:

- presentation code depends on the gateway contract, not on duplicated Core algorithms;
- gateway state must distinguish at least `AVAILABLE`, `UNAVAILABLE`, and `ERROR` or equivalent truthful dispositions;
- the initial implementation may be capability/status-only if no audited cross-process invocation contract exists yet;
- do not shell out to arbitrary commands merely to make the UI look connected;
- do not copy Python logic into GDScript;
- do not hardcode fake generated candidate/job/provider data;
- no network/API/provider call is permitted in this cycle;
- no credentials or provider secrets may be read.

Document the intended future direction for invoking canonical local Core. If an existing accepted local CLI boundary is appropriate, document it as a candidate integration surface, but do not silently elevate an unaudited subprocess protocol into canonical truth in this cycle.

## 4. Workspace composition and maintainability

Prefer small composable scenes/scripts rather than one giant scene or script.

At minimum separate:

- application shell/navigation responsibility;
- workspace/page presentation responsibility;
- canonical-Core gateway/status responsibility.

Exact filenames are builder choice, but naming must be clear and project-local.

Do not add a second database, tracker, JSON state ledger, or hidden project-management state.

The Factory Operations Dashboard planned by `SB-LFX-001` is a future **production operations view**, not H!veAI tracking. This cycle must preserve that distinction.

## 5. Product extension readiness without premature implementation

The workspace shell must be structurally capable of later hosting:

- Factory Operations Dashboard;
- manual Pixel Art import;
- Source Art Library;
- one-click pipeline;
- Candidate Inbox / Review Queue;
- side-by-side comparison;
- presets;
- failure/retry center;
- similarity review;
- provider cost/credit center;
- exact reproduce;
- revision history;
- search/smart collections;
- Production Readiness Card;
- batch import;
- session recovery.

Do not implement those product capabilities in this cycle.

A navigation placeholder or typed capability identifier is not considered implementation of the later task as long as it carries no fake business logic or state.

## 6. Documentation

Create or update concise Factory-local documentation describing:

- Studio scene/component structure;
- canonical-Core ownership boundary;
- gateway contract and current integration status;
- navigation/page ownership;
- how later SB-LF06 / SB-LFX tasks extend the shell without duplicating Core truth;
- exact local run command / Godot project path;
- headless verification command.

Do not create another tracker or roadmap file. Root `TASKS.md` remains sole task state.

## 7. Focused tests

Add focused automated evidence for `SB-LF06-001`.

At minimum prove:

1. `level_factory/` still opens as an independent Godot project;
2. configured main scene is the real Factory Studio shell, not the 69-byte bootstrap placeholder;
3. shell can initialize headlessly without generated data, credentials or network;
4. expected navigation surfaces are represented once and are deterministic;
5. future/unimplemented pages do not claim fake operational values;
6. Studio scripts do not duplicate/import Python Factory algorithms into GDScript;
7. gateway exposes truthful unavailable/error/capability status rather than fabricated success;
8. root Python Factory Core tests remain unaffected;
9. root `TASKS.md` is untouched by builder;
10. no provider call/network dependency is introduced.

Use root Python tests and/or Godot-local tests as appropriate. Do not create brittle tests that merely grep one exact whitespace layout when a structural assertion is possible.

## 8. Required verification

Run and record at minimum:

1. focused SB-LF06-001 tests;
2. prior `SB-LF00-001`, `SB-LF00-002`, `SB-LF00-006`, `SB-LF00-008`, and `SB-LF00-007` focused governance tests;
3. full `python -m pytest -q`;
4. `python -m compileall -q src tests`;
5. package import smoke;
6. existing module CLI help smoke;
7. Godot headless project boot using `level_factory/`;
8. Godot editor/headless scene load for the new main workspace;
9. `git diff --check`;
10. changed-file review proving no provider/main-game/content-platform implementation and no root TASKS edit;
11. prove no credential/API key/network dependency is introduced.

Record failed commands and corrections truthfully.

## Allowed scope

Allowed:

- `level_factory/project.godot` as required for the real Studio shell;
- `level_factory/scenes/**`;
- `level_factory/scripts/**`;
- `level_factory/docs/**`;
- `level_factory/tests/**`;
- root focused test(s) specifically for SB-LF06-001 if useful;
- narrow `level_factory/README.md` updates for implemented workspace facts;
- matching builder log.

Do not edit root `TASKS.md`.

## Forbidden scope

Do not implement or modify:

- `SB-LFX-001..017` functional behavior beyond inert navigation/readiness scaffolding;
- gameplay solver or main-game semantics;
- Content Platform M11+;
- Magnific, PixelLab, Perchance or any provider execution;
- provider credential/account management;
- manual Pixel Art file ingestion logic;
- Source Art Library persistence;
- Dashboard production metrics;
- review acceptance workflow;
- batch retry/resume behavior beyond existing canonical Core;
- Python generation/compiler/QA algorithms unless a direct blocking defect is independently proven and a new prompt authorizes it;
- `Sekiph82/Scrubbots`.

No task-state changes. No self-audit. No self-acceptance.

## Builder log requirements

H1 exactly:

`# SB-LF06-001-C001 — Factory Studio Canonical-Core Workspace Migration`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- repo/local mirror/branch/origin/status/worktree verification;
- starting HEAD and `origin/main` equality/divergence;
- required authorities read;
- current level_factory file inventory before edits;
- architecture decisions;
- files/scenes/scripts created or changed;
- gateway boundary and what it intentionally does **not** implement;
- focused test failures/corrections/results;
- prior LF00 governance regressions;
- full regression;
- compile/import/CLI/Godot smoke;
- network/provider/credential no-use proof;
- TASKS no-change proof;
- dependency/license changes, expected none unless explicitly justified;
- implementation commit SHA and push;
- final builder-log publication checkpoint/terminal publication evidence;
- final local `HEAD` / `origin/main` state.

Never record secrets.

## Acceptance criteria

PASS eligibility requires all of the following:

- [ ] `level_factory/` boots as a real Factory Studio workspace;
- [ ] workspace has maintainable shell/header/navigation/content/status structure;
- [ ] future owner-approved surfaces are represented as truthful inert navigation/readiness scaffolding only;
- [ ] Python Factory Core remains canonical and no GDScript compiler/solver/validator clone is introduced;
- [ ] explicit gateway/integration boundary exists;
- [ ] gateway/status never fabricates Core/provider availability or data;
- [ ] no dashboard/import/library/review/provider functional scope creep occurs;
- [ ] no second tracker/state database/control plane is created;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] focused tests pass;
- [ ] prior governance regressions pass;
- [ ] full Python regression passes;
- [ ] Godot headless/editor smoke passes;
- [ ] no provider/network/credential/main-game/content-platform changes;
- [ ] builder log is finalized and pushed;
- [ ] builder stops for independent ChatGPT strict audit.

## GitHub handoff

Push implementation/tests/finalized builder log to `main`.

At final handoff provide only:

1. full GitHub URL of the finalized builder log;
2. implementation commit SHA;
3. final publication commit SHA.

Do not give a local Windows log path as the primary handoff.
Do not paste the full builder log body unless asked.
Then stop for independent ChatGPT strict audit.
