# ScrubBots Level Factory + Content Platform — Canonical GitHub Task State

This root `TASKS.md` is the sole authoritative Level Factory + Content Platform task ledger consumed by H!veAI. It preserves accepted PAG/SP work as evidence, integrates the 224 canonical LF/CP source requirements, and prevents historical work from being counted twice.

## Project Status

- Current Milestone: M06 — ScrubBots Factory Studio
- Current Sprint: M06.01 — Studio architecture and operator controls
- Current Task: SB-LF06-003 — Generate/Solve/Validate/Analyze/Reproduce actions
- Current Task Status: FIX_REQUIRED
- Next Task/Action: Codex executes only `SB-LF06-003-C001-R01` from the published GitHub remediation prompt, preserves the accepted canonical Generate/Reproduce action bridge and dependency gates, fixes real Core availability probing, stderr/error truth, post-success workspace wording and last-success evidence retention, publishes the finalized R01 builder log to `main`, then stops for independent ChatGPT strict audit.
- Required Actor: CODEX
- Tracking Repository: Sekiph82/ScrubBots-Level-Factory
- Tracking Branch: main
- Previous Strict Audit: `.hiveai/audits/SB-LF06-003-C001_FACTORY_STUDIO_CANONICAL_ACTION_BRIDGE_STRICT_AUDIT.md`
- SB-LF06-003 C001 Disposition: CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED
- SB-LF06-003 C001 Implementation Commit: `a34107864d44118762bcde3a35f7c04a5633a4a4`
- SB-LF06-003 C001 Final Builder Publication: `9cc87b4edb493f0d3848aeaec2947b718a5c2127`
- SB-LF06-003 C001 Strict Audit Commit: `cafafa2e096ec2f5ad949da3985a106f53995c73`
- Current Prompt: `.hiveai/prompts/SB-LF06-003-C001-R01_CORE_AVAILABILITY_ERROR_AND_RESULT_TRUTH_REMEDIATION_PROMPT.md`
- Migration Cutover Date: 2026-09-14

## H!veAI Parser Contract

The six live status labels above are literal parser fields and must remain exactly:

- `Current Milestone:`
- `Current Sprint:`
- `Current Task:`
- `Current Task Status:`
- `Next Task/Action:`
- `Required Actor:`

Do not wrap those labels in Markdown emphasis and do not replace them with aliases.

## Tasks

- M00: Repository, Governance & Canonical Factory Platform — COMPLETE / VERIFIED
- M01: Deterministic Factory Core — PLANNED / PARTIALLY EVIDENCED
- M02: Semantic / Constraint Candidate Generation — PLANNED / PARTIALLY EVIDENCED
- M03: Puzzle Intelligence: Simulation, Solver & State Search — PLANNED
- M04: Difficulty Intelligence & Metrics — PLANNED / PARTIALLY EVIDENCED
- M05: Unified Factory Validation & Level QA — PLANNED / PARTIALLY EVIDENCED
- M06: ScrubBots Factory Studio — ACTIVE / PARTIALLY EVIDENCED
- M07: Mutation & Automatic Difficulty Targeting — PLANNED
- M08: Batch Factory & Weekly Production — PLANNED / PARTIALLY EVIDENCED
- M09: Advanced Generation Research & Semantic Provider Evolution — PLANNED / PARTIALLY EVIDENCED
- M10: Campaign Intelligence / Sequencing Adapter — PLANNED
- M11: Content Platform Architecture & Security Boundary — PLANNED / PARTIALLY EVIDENCED
- M12: .scrubpack Format & Packager — PLANNED / PARTIALLY EVIDENCED
- M13: Remote Manifest & Content Versioning — PLANNED
- M14: Publisher, Staging & Production Promotion — PLANNED / PARTIALLY EVIDENCED
- M15: Godot Remote Content Runtime — PLANNED
- M16: Offline Cache & Last-Known-Good Recovery — PLANNED
- M17: Rollback, Disable & Scheduling — PLANNED / PARTIALLY EVIDENCED
- M18: Storage / CDN Provider Integration — PLANNED / PARTIALLY EVIDENCED
- M19: Content Operations, QA & Observability — PLANNED / PARTIALLY EVIDENCED
- M20: Store Policy, Security & Production Release Gate — PLANNED / PARTIALLY EVIDENCED

# SCRUBBOTS LEVEL FACTORY + CONTENT PLATFORM — MASTER TASKS

Legend: `[x]` validated complete, `[~]` active/in progress, `[ ]` planned/pending, `[!]` blocked.

Additional inline tags do not replace checkbox state:

- `[PARTIAL]` — accepted implementation/evidence exists, but the complete unified requirement is not closed.
- `[MIGRATION]` — the requirement intent remains valid, but obsolete architecture/wording must be migrated.
- `[GAME_RUNTIME]` — implementation belongs in `Sekiph82/Scrubbots`; this tracker retains program-level requirement truth.
- `[DESIGN_GATE]` — owner/product semantics must not be invented.
- `[OWNER_GATE]` — technical work may exist but owner product/visual acceptance remains required.
- `[EXTENSION]` — owner-approved post-cutover product capability outside the fixed 224 LF/CP source-requirement denominator.

## Canonical tracking rules

- This root `TASKS.md` is the sole live Level Factory + Content Platform tracker.
- ChatGPT is the sole writer of root `TASKS.md`; Codex/Claude/builders read it but do not edit task state.
- Builder logs are claims, not acceptance.
- Only independent ChatGPT audit may promote a requirement to `[x]`.
- Historical PAG-M00..M10 and PAG-SP00..SP14 prompt/log/audit chains remain immutable evidence.
- Historical work is mapped to the 224 canonical source requirements rather than counted as a second live task set.
- The canonical live source-requirement denominator is exactly 224: 112 Level Factory + 112 Content Pipeline.
- Owner-approved post-cutover extension tasks are counted only in the unified denominator and do not rewrite the historical 224-source mapping.
- Main-game runtime requirements remain visible here as `[GAME_RUNTIME]` but implementation lives in `Sekiph82/Scrubbots`.
- No accepted SP05/SP06 architecture is reopened without a new independently audited defect.
- No provider credits are spent merely for tracker migration, evidence migration, or offline planning.
- One requirement is counted exactly once.

## Current truth and progress

- Canonical LF/CP source-requirement classification: 34 VERIFIED, 51 PARTIAL, 3 MIGRATION, 108 NEW/OPEN, 28 GAME_RUNTIME.
- Canonical LF/CP source-requirement completion: **34 / 224 = 15.18%**.
- Canonical LF/CP engineering/migration coverage: **88 / 224 = 39.29%** (`VERIFIED + PARTIAL + MIGRATION`).
- Existing Semantic Pixel Studio extensions remain live: `PAG-SP11`, `PAG-SP12`, `PAG-SP13`.
- Seventeen owner-approved Factory Studio/operator extensions are retained live as `SB-LFX-001..017`; their product contract is `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`.
- Unified live task denominator: **244** = 224 LF/CP source requirements + 3 Semantic Pixel Studio extensions + 17 Factory Studio/operator extensions.
- Unified verified completion: **34 / 244 = 13.93%**.
- Direct local implementation surface excluding 28 GAME_RUNTIME rows: **216 live tasks**.
- Conservative verified local completion: **34 / 216 = 15.74%**.
- Level Factory + unique extension surface: **132 tasks**; **34 / 132 = 25.76% verified**.
- Content Platform source requirements: **112 tasks**; **0 / 112 verified** at cutover baseline.
- `PAG-SP06` is PASS/CLOSED.
- `PAG-SP07-C001-R01` is PASS/CLOSED and retained as accepted evidence under `SB-LF09-003`; the broader `SB-LF09-003` source requirement remains PARTIAL and is not counted complete.
- `SB-LF00-001` is PASS/CLOSED and establishes the independently openable `level_factory/` Godot project shell.
- `SB-LF00-002` is PASS/CLOSED and establishes the Factory-local README/governance/docs/scenes/scripts/tests/output ownership boundaries.
- `SB-LF00-006` is PASS/CLOSED and establishes the repository-wide generated/candidate/cache/log/secret workspace boundary without hiding durable evidence.
- `SB-LF00-008` is PASS/CLOSED and proves the committed tracked-only `level_factory/` snapshot boots headlessly without ignored/local dependencies.
- `SB-LF00-007` is PASS/CLOSED and establishes TASKS-only H!veAI governance with obsolete `CYCLE_INDEX` removed and parser-safe task rows.
- `SB-LF06-001` is PASS/CLOSED through `SB-LF06-001-C001-R01`; the real Factory Studio workspace shell and executable runtime node contract are accepted.
- `SB-LF01-005` is PASS/CLOSED through `SB-LF01-005-C001-R01`; current production dimensions are independently `20..59`, historical request-schema-v1 replay remains intact, manifest version parsing is strict, and workload guidance is advisory only.
- `SB-LF06-002` is PASS/CLOSED through `SB-LF06-002-C001-R01`; the Generate target form is presentation-only, cross-language guarded, independent-dimension safe, Core-unavailable truthful, and protected by a committed project-local clean-checkout Godot runtime suite.
- `SB-LF06-003-C001` product implementation is retained: real canonical Generate/Reproduce, dependency-gated Solve/Validate/Analyze, identity isolation and governed output are present; strict audit found false-positive Core availability probing, lost stderr diagnostics, stale post-success workspace wording, and last-success evidence retention gaps, so bounded R01 truth remediation is active before closure.
- M00–M10 historical PAG technical foundation remains accepted evidence except the M10 visual pack, which remains OWNER REJECTED 100/100 and is retained as negative evidence.

## Locked production contracts

- Width: 20..59 inclusive.
- Height: 20..59 independently validated; rectangular boards are legal.
- One logical artwork pixel equals one gameplay cell.
- Logical palette: C01..C16 only.
- BG01 `#202533` is presentation/background only.
- Production used-color envelope: 3..12 distinct C01..C16 colors independent of difficulty lane.
- Difficulty is not derived from board size.
- Difficulty is not derived from used-color count.
- High-resolution reduction: `CELL_MAJORITY_V1`.
- Palette policy: `PALETTE_SNAP_V1`.
- No averaging/interpolation/antialiasing inside logical cells.
- No random/forced color injection to make a candidate legal.
- Exact deterministic provenance is required.
- Trusted SP05 raw identity invariant: `report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`.
- SP06 structural diagnostics never auto-accept recognizability; explicit ACCEPT is required.
- WFC constraint solving is not the ScrubBots gameplay solver.
- Factory Studio must consume canonical Factory Core rather than maintain a second compiler.
- Factory Operations Dashboard and smart collections are derived views over canonical records, never second tracker/truth stores.
- Owner-uploaded source art is preserved byte-for-byte; transformations produce separately identified derived artifacts.
- Imported artwork is provenance-bearing content, not model-training data.
- Remote content is declarative only; executable payloads are forbidden.

---

# M00 - Repository, Governance & Canonical Factory Platform

Capability source family: `SB-LF00-xxx` from the main Scrubbots master plan.

### M00.01 - Canonical Factory platform

- [x] SB-LF00-001 — Establish `level_factory/` as independently openable Godot project.
- [x] SB-LF00-002 — Maintain Factory-specific README/governance/docs/scenes/scripts/tests/output boundaries.
- [x] SB-LF00-003 — Enforce one-way integration: Factory exports data; main game never preloads Factory scripts.
- [x] SB-LF00-004 — Keep Factory logic headless-testable/data-oriented.
- [x] SB-LF00-005 — Define Factory verification commands separately.

### M00.02 - Workspace hygiene and exclusions

- [x] SB-LF00-006 — Define generated/candidate/cache/secret folders and exclusions.
- [x] SB-LF00-008 — Prove clean checkout boots nested Factory headlessly.

### M00.03 - Tracker and coordination governance

- [x] SB-LF00-007 — Establish Factory coordination structure while root TASKS remains sole ledger.

---

# M01 - Deterministic Factory Core

Capability source family: `SB-LF01-xxx` from the main Scrubbots master plan.

### M01.01 - Generation config and seed determinism

- [x] SB-LF01-001 — Define deterministic LevelGenerationConfig.
- [x] SB-LF01-002 — Store/replay seed for every candidate.
- [x] SB-LF01-003 — Same config + seed produces byte-identical candidate data.
- [x] SB-LF01-004 — Distinct seeds can produce distinct legal candidates.

### M01.02 - Production dimensions and workload envelope

- [x] SB-LF01-005 — Support width/height selection within current engine/content envelope and workload guidance.
- [x] SB-LF01-006 — Support rectangular boards.
- [x] SB-LF01-007 — Exercise 59×59 where cost scales.

### M01.03 - Provenance and production classification

- [x] SB-LF01-008 — Record seed/config/generator-version provenance.
- [ ] SB-LF01-009 — Separate TEST/development candidates from production. [PARTIAL]
- [ ] SB-LF01-010 — Reject obsolete semantic assumptions. [MIGRATION]

---

# M02 - Semantic / Constraint Candidate Generation

Capability source family: `SB-LF02-xxx` from the main Scrubbots master plan.

### M02.01 - Candidate modes and evaluator guidance

- [ ] SB-LF02-001 — Implement evaluator-guided candidate architecture rather than blind random filling. [PARTIAL]
- [ ] SB-LF02-002 — Support reverse construction when canonical mechanics permit.
- [ ] SB-LF02-003 — Support PUZZLE_FIRST mode.
- [ ] SB-LF02-004 — Support ART_FIRST mode consuming owner/AI-approved pixel art/masks. [PARTIAL]

### M02.02 - Shape, regions and artwork provenance

- [x] SB-LF02-005 — Implement reusable shape/topology primitives without declaring them difficulty rules.
- [x] SB-LF02-006 — Implement connected color-region representation/generation.
- [x] SB-LF02-007 — Preserve one logical artwork square = one logical board cell.
- [ ] SB-LF02-008 — Never fabricate missing owner artwork or label AI output owner-original. [PARTIAL]

### M02.03 - Design gates, provenance and deterministic tests

- [ ] SB-LF02-009 — Keep unresolved dependency semantics behind design-gated adapters.
- [ ] SB-LF02-010 — Keep unresolved slot/stack quantity/order generation design-gated.
- [x] SB-LF02-011 — Record candidate provenance.
- [x] SB-LF02-012 — Add deterministic unit/property tests.

---

# M03 - Puzzle Intelligence: Simulation, Solver & State Search

Capability source family: `SB-LF03-xxx` from the main Scrubbots master plan.

### M03.01 - Headless simulation and state contract

- [ ] SB-LF03-001 — Create pure/headless puzzle simulation boundary.
- [ ] SB-LF03-002 — Define compact solver state.
- [ ] SB-LF03-003 — Define legal-move-provider interface.

### M03.02 - Deterministic search and solver evidence

- [ ] SB-LF03-004 — Implement deterministic baseline search when semantics available.
- [ ] SB-LF03-005 — Add visited-state memoization/hashing.
- [ ] SB-LF03-006 — Record solution path/states/dead ends/depth/branching/solve time.
- [ ] SB-LF03-007 — Add correctness-preserving pruning/order only with tests.
- [ ] SB-LF03-008 — Add bounded solution-count/entropy analysis.

### M03.03 - Canonical semantics, reproducibility and budgets

- [ ] SB-LF03-009 — Reuse canonical reachability/routing semantics rather than importing another game's rules.
- [ ] SB-LF03-010 — Reproduce solver bugs by candidate/seed/config/version.
- [ ] SB-LF03-011 — Define budgets/timeouts and UNSOLVED vs INCONCLUSIVE.
- [ ] SB-LF03-012 — Add regression fixtures.

---

# M04 - Difficulty Intelligence & Metrics

Capability source family: `SB-LF04-xxx` from the main Scrubbots master plan.

### M04.01 - Versioned solver-derived metrics

- [ ] SB-LF04-001 — Define versioned LevelMetrics. [PARTIAL]
- [ ] SB-LF04-002 — Record solution depth/move count where meaningful.
- [ ] SB-LF04-003 — Record states/dead ends/branching/forced moves.

### M04.02 - Canonical gameplay feature metrics

- [ ] SB-LF04-004 — Add dependency depth only when canonical.
- [ ] SB-LF04-005 — Add slot pressure only when canonical.
- [ ] SB-LF04-006 — Add bait/deadlock metrics only when canonical.
- [ ] SB-LF04-007 — Add color/remaining-state volatility where useful.

### M04.03 - Difficulty V1 challenge, provenance and calibration

- [ ] SB-LF04-008 — Implement/version Difficulty V1 Challenge Score components/coefficients.
- [ ] SB-LF04-009 — Map predicted score to current lane/class rhythm without equating class to board size.
- [ ] SB-LF04-010 — Keep metric provenance/versioning. [PARTIAL]
- [ ] SB-LF04-011 — Design future calibration against player data under approved analytics policy.
- [ ] SB-LF04-012 — Tests prove analysis does not mutate gameplay/art source. [PARTIAL]

---

# M05 - Unified Factory Validation & Level QA

Capability source family: `SB-LF05-xxx` from the main Scrubbots master plan.

### M05.01 - Structural and production validation

- [ ] SB-LF05-001 — Compose structural LevelData validation with current production compatibility + Difficulty V1 evaluation. [PARTIAL]
- [ ] SB-LF05-002 — Reuse audited M09 round-trip contract for art-first exports. [PARTIAL]
- [ ] SB-LF05-003 — Validate dimensions/envelope/C01..C16/3..12 used colors/cells/opacity/transparency/provenance/duplicate IDs. [PARTIAL]

### M05.02 - Solver disposition

- [ ] SB-LF05-004 — Reject proven-unsolvable candidates when solver authoritative.
- [ ] SB-LF05-005 — Distinguish INCONCLUSIVE from UNSOLVABLE.

### M05.03 - QA reports, source preservation and semantic readability

- [x] SB-LF05-006 — Actionable rejection reasons.
- [ ] SB-LF05-007 — Machine-readable QA report. [PARTIAL]
- [ ] SB-LF05-008 — Preserve owner source images byte-for-byte. [PARTIAL]
- [x] SB-LF05-009 — Visual recognizability/readability gates, not structural-only false positives.

### M05.04 - Main-game acceptance handoff

- [ ] SB-LF05-010 — Feed accepted artifacts into M30/M47/M48 rather than bypassing them.

---

# M06 - ScrubBots Factory Studio

Capability source family: `SB-LF06-xxx` from the main Scrubbots master plan plus owner-approved post-cutover `SB-LFX-xxx` Studio extensions.

### M06.01 - Studio architecture and operator controls

- [x] SB-LF06-001 — Build @tool/editor-facing workspace.
- [x] SB-LF06-002 — Target difficulty/dimensions/seed/mode/candidate controls.
- [~] SB-LF06-003 — Generate/Solve/Validate/Analyze/Reproduce actions. [PARTIAL]

### M06.02 - Preview, metrics and controlled editing

- [ ] SB-LF06-004 — Crisp board/art preview.
- [ ] SB-LF06-005 — Display solution/difficulty/load/risk/art QA metrics/provenance.
- [ ] SB-LF06-006 — Owner/designer paint/edit where appropriate.
- [ ] SB-LF06-007 — Approved puzzle-config edits only.

### M06.03 - Revalidation, truth separation, reproduction and tests

- [ ] SB-LF06-008 — Revalidate after manual changes. [PARTIAL]
- [x] SB-LF06-009 — Never auto-promote generated candidate.
- [ ] SB-LF06-010 — Keep editor presentation separate from truth. [PARTIAL]
- [ ] SB-LF06-011 — Reproduce candidate by seed/config. [PARTIAL]
- [ ] SB-LF06-012 — Editor smoke + headless core tests. [PARTIAL]

### M06.04 - Owner-approved operations dashboard, import and library extensions

- [ ] SB-LFX-001 — Build Factory Operations Dashboard from canonical job/artifact/evidence truth without creating a second tracker or production truth store. [EXTENSION]
- [ ] SB-LFX-002 — Support manual Pixel Art import with explicit `OWNER_UPLOAD` provenance and immutable original bytes. [EXTENSION]
- [ ] SB-LFX-003 — Build searchable Source Art Library/index with immutable source identity, provenance, tags, review state and usage references. [EXTENSION]
- [ ] SB-LFX-004 — Add Import Validation Wizard for format/dimensions/C01..C16/foreign colors/semi-alpha/used-color and canonical structural checks. [EXTENSION]

### M06.05 - Unified operator workflow extensions

- [ ] SB-LFX-005 — Build bounded one-click pipeline orchestration across applicable Import/Generate→Normalize→Validate→Candidate→Solve→Difficulty→QA→Review stages. [EXTENSION]
- [ ] SB-LFX-006 — Build unified Candidate Inbox and owner Review Queue across provider, procedural, owner-upload and library-derived candidates. [EXTENSION]
- [ ] SB-LFX-007 — Provide side-by-side candidate/variant comparison using canonical preview, QA, solver/difficulty, provenance and cost evidence where available. [EXTENSION]
- [ ] SB-LFX-008 — Add reusable Presets / Production Recipes while always persisting the fully expanded canonical request/config. [EXTENSION]

### M06.06 - Discovery, readiness, reproduction and edit lineage extensions

- [ ] SB-LFX-009 — Add scalable search/filter/smart collections as derived views over canonical source/candidate/level records. [EXTENSION]
- [ ] SB-LFX-010 — Add Production Readiness Card exposing truthful SOURCE/PALETTE/STRUCTURE/SOLVER/DIFFICULTY/QA/OWNER/EXPORT dispositions. [EXTENSION]
- [ ] SB-LFX-011 — Expose Exact Reproduce action only where recorded canonical identities and the underlying path support truthful reproducibility. [EXTENSION]
- [ ] SB-LFX-012 — Add immutable manual-edit revision history with compare/undo/restore-source behavior and no silent source overwrite. [EXTENSION]
---

# M07 - Mutation & Automatic Difficulty Targeting

Capability source family: `SB-LF07-xxx` from the main Scrubbots master plan.

### M07.01 - Mutation contract and safe operators

- [ ] SB-LF07-001 — Mutation interface/immutable lineage.
- [ ] SB-LF07-002 — Safe hardening mutations only for canonical mechanics.
- [ ] SB-LF07-003 — Safe easing mutations only for canonical mechanics.
- [ ] SB-LF07-004 — Re-solve/revalidate after every mutation.
- [ ] SB-LF07-005 — Preserve seed/parent/mutation provenance.

### M07.02 - Difficulty targeting, bounds and regressions

- [ ] SB-LF07-006 — Target Challenge Score range while respecting load/risk/retention constraints.
- [ ] SB-LF07-007 — Bound mutation attempts.
- [ ] SB-LF07-008 — Compare mutate vs regenerate efficiency.
- [ ] SB-LF07-009 — Never mutate owner source art silently.
- [ ] SB-LF07-010 — Deterministic mutation regression tests.

---

# M08 - Batch Factory & Weekly Production

Capability source family: `SB-LF08-xxx` from the main Scrubbots master plan plus owner-approved batch-operations extensions.

### M08.01 - Batch counts, rejection statistics and resumability

- [ ] SB-LF08-001 — Generate requested accepted counts by lane/class cadence. [PARTIAL]
- [x] SB-LF08-002 — Separate generated from accepted count.
- [x] SB-LF08-003 — Rejection statistics.
- [x] SB-LF08-004 — Deterministic/resumable batch jobs.
- [x] SB-LF08-005 — Prevent duplicate IDs/seeds/artifacts.

### M08.02 - Accepted outputs, owner review and pipeline handoff

- [ ] SB-LF08-006 — Accepted LevelData/previews/metadata/QA reports as batch result. [PARTIAL]
- [ ] SB-LF08-007 — Owner review/approval queue before publication. [PARTIAL]
- [ ] SB-LF08-008 — Production-ready handoff to Content Pipeline.

### M08.03 - Stress and idempotence

- [ ] SB-LF08-009 — Stress high rejection rates safely. [PARTIAL]
- [x] SB-LF08-010 — Reruns create no meaningless diffs.

### M08.04 - Owner-approved failure, batch-import and recovery extensions

- [ ] SB-LFX-013 — Build Failure Inbox / Retry Center that retries only eligible failed/rejected/inconclusive work while preserving failure evidence and lineage. [EXTENSION]
- [ ] SB-LFX-014 — Support drag-and-drop multi-file Pixel Art batch import with independent immutable provenance per file. [EXTENSION]
- [ ] SB-LFX-015 — Add Factory Studio session recovery/autosave that resumes eligible durable jobs without redoing successful stages. [EXTENSION]

---

# M09 - Advanced Generation Research & Semantic Provider Evolution

Capability source family: `SB-LF09-xxx` from the main Scrubbots master plan plus owner-approved provider/analysis extensions.

Accepted legacy implementation/evidence chain: `PAG-SP07-C001` product implementation is retained and `PAG-SP07-C001-R01` is PASS/CLOSED; both remain evidence under `SB-LF09-003` and are not a second counted task family.

### M09.01 - Experimental evolutionary generation

- [ ] SB-LF09-001 — Prototype evolutionary selection behind experimental flag.
- [ ] SB-LF09-002 — Versioned fitness metrics. [PARTIAL]

### M09.02 - Semantic/procedural art helpers

- [ ] SB-LF09-003 — Prototype procedural/semantic art helpers without replacing owner-approved art direction. [PARTIAL]

### M09.03 - Reference / Style Generation accepted evidence chain

- `PAG-SP07-C001` remains retained product/evidence history under `SB-LF09-003`; it is not a second counted source requirement.
- `PAG-SP07-C001-R01` = PASS / CLOSED by `.hiveai/audits/PAG-SP07-C001-R01_REQUIRED_IDENTITY_MUTATION_EVIDENCE_AND_PROCESS_CLOSURE_STRICT_AUDIT.md`.
- The accepted R01 closes the missing REFERENCE content-SHA mutation, INIT-strength-only mutation and remediation-process evidence, but does not by itself complete the broader `SB-LF09-003` capability.

### M09.04 - Telemetry calibration policy

- [ ] SB-LF09-004 — Telemetry-calibrated difficulty only after approved analytics/data policy.

### M09.05 - Runtime prohibition, lineage, cost and promotion audit

- [x] SB-LF09-005 — Keep live/runtime level generation disabled unless explicitly approved.
- [x] SB-LF09-006 — Preserve reproducibility/lineage.
- [ ] SB-LF09-007 — Compare advanced generation quality/compute cost. [PARTIAL]
- [x] SB-LF09-008 — No production promotion without separate audit decision.

### M09.06 - Semantic asset extensions not represented by the 224 LF/CP source requirements

- [ ] PAG-SP11 — ASSET_ART Production. [EXTENSION]
- [ ] PAG-SP12 — Direction / Rotation Variants. [EXTENSION]
- [ ] PAG-SP13 — Animation. [EXTENSION]

### M09.07 - Owner-approved similarity and provider-accounting extensions

- [ ] SB-LFX-016 — Add advisory visual-similarity guard for near-duplicate artwork/candidates while retaining exact identity checks and avoiding silent auto-reject policy. [EXTENSION]
- [ ] SB-LFX-017 — Build Provider Cost / Credit Center for truthful jobs/success/failure/consumed/remaining/cost-per-accepted accounting where reliable provider data exists. [EXTENSION]

---

# M10 - Campaign Intelligence / Sequencing Adapter

Capability source family: `SB-LF10-xxx` from the main Scrubbots master plan.

### M10.01 - Campaign interface and Difficulty V1 rules

- [ ] SB-LF10-001 — Define CampaignBuilder interface.
- [ ] SB-LF10-002 — Consume owner-locked Difficulty V1 rhythm/progression/retention rules.
- [ ] SB-LF10-003 — Select accepted production levels without modifying their data.

### M10.02 - Selection, availability and deterministic provenance

- [ ] SB-LF10-004 — Prevent duplicate/unavailable/disabled selection.
- [ ] SB-LF10-005 — Preserve deterministic campaign-build provenance.
- [ ] SB-LF10-006 — Rebuild campaign ordering without regenerating levels.

### M10.03 - Events and campaign validation

- [ ] SB-LF10-007 — Future events/featured selection as data, not code.
- [ ] SB-LF10-008 — Campaign validation against challenge/load/frustration/similarity constraints.

---

# M11 - Content Platform Architecture & Security Boundary

Capability source family: `SB-CP00-xxx` from the main Scrubbots master plan.

### M11.01 - App/content and declarative-content boundary

- [ ] SB-CP00-001 — Establish `content_pipeline/` separate publisher/control-plane project. [MIGRATION]
- [ ] SB-CP00-002 — Define app code vs remote content boundary. [PARTIAL]
- [ ] SB-CP00-003 — Remote content declarative only; forbid executable payloads. [PARTIAL]

### M11.02 - Staging, audit state, secrets and dry-run

- [ ] SB-CP00-004 — Separate staging/production.
- [ ] SB-CP00-005 — Versioned/auditable publish/promotion/rollback state.
- [ ] SB-CP00-006 — Secret handling; no credentials in Git. [PARTIAL]
- [ ] SB-CP00-007 — Publisher dry-run/validation-only before remote mutation.

### M11.03 - Provider abstraction, tracker ownership and store-policy gate

- [ ] SB-CP00-008 — Provider abstraction. [PARTIAL]
- [ ] SB-CP00-009 — Content Pipeline GitHub coordination under ChatGPT-owned root tracker. [MIGRATION]
- [ ] SB-CP00-010 — Re-verify mobile/store-policy boundary before release.

---

# M12 - .scrubpack Format & Packager

Capability source family: `SB-CP01-xxx` from the main Scrubbots master plan.

### M12.01 - Pack spec, declarative payload and metadata

- [ ] SB-CP01-001 — Define versioned .scrubpack spec.
- [ ] SB-CP01-002 — Package declarative levels only. [PARTIAL]
- [ ] SB-CP01-003 — Record pack ID/version/time/levels. [PARTIAL]

### M12.02 - Integrity, deterministic serialization and duplicate prevention

- [ ] SB-CP01-004 — Per-pack SHA-256. [PARTIAL]
- [ ] SB-CP01-005 — Deterministic pack serialization/order. [PARTIAL]
- [ ] SB-CP01-006 — Prevent duplicate level IDs. [PARTIAL]

### M12.03 - Validation, inspection and compatibility

- [ ] SB-CP01-007 — Validate every level before pack. [PARTIAL]
- [ ] SB-CP01-008 — Unpack/inspect tooling.
- [ ] SB-CP01-009 — Deterministic bytes where container permits. [PARTIAL]
- [ ] SB-CP01-010 — Reject unsupported versions safely. [PARTIAL]

---

# M13 - Remote Manifest & Content Versioning

Capability source family: `SB-CP02-xxx` from the main Scrubbots master plan.

### M13.01 - Manifest schema and compatibility versioning

- [ ] SB-CP02-001 — Define versioned manifest schema.
- [ ] SB-CP02-002 — schema_version + monotonic content_version.
- [ ] SB-CP02-003 — minimum_game_version compatibility.

### M13.02 - Pack, level, disable and schedule metadata

- [ ] SB-CP02-004 — Pack IDs/locations/hashes.
- [ ] SB-CP02-005 — Level metadata without unnecessary contiguous-ID assumption.
- [ ] SB-CP02-006 — disabled_levels.
- [ ] SB-CP02-007 — Scheduled activation windows.

### M13.03 - Ownership conflicts, reference validation and history

- [ ] SB-CP02-008 — Reject duplicate pack/level ownership conflicts.
- [ ] SB-CP02-009 — Validate references before publish.
- [ ] SB-CP02-010 — Keep prior manifests/version history.
- [ ] SB-CP02-011 — App/content schema compatibility behavior.
- [ ] SB-CP02-012 — Parser/schema tests.

---

# M14 - Publisher, Staging & Production Promotion

Capability source family: `SB-CP03-xxx` from the main Scrubbots master plan.

### M14.01 - Validation-only packaging and candidate manifest

- [ ] SB-CP03-001 — Publisher validation-only mode.
- [ ] SB-CP03-002 — Serialize accepted Factory output into packs. [PARTIAL]
- [ ] SB-CP03-003 — Hashes + candidate manifest. [PARTIAL]

### M14.02 - Upload integrity and staging verification

- [ ] SB-CP03-004 — Upload packs before active manifest references them.
- [ ] SB-CP03-005 — Verify remote object integrity.
- [ ] SB-CP03-006 — Publish STAGING first.
- [ ] SB-CP03-007 — Verify staging through real download.

### M14.03 - Production promotion, overwrite safety and reporting

- [ ] SB-CP03-008 — Explicit staging→production promotion.
- [ ] SB-CP03-009 — New versioned production manifest.
- [ ] SB-CP03-010 — No silent live overwrite.
- [ ] SB-CP03-011 — One-command publish only after stages individually testable.
- [ ] SB-CP03-012 — Publish report.

---

# M15 - Godot Remote Content Runtime

Capability source family: `SB-CP04-xxx` from the main Scrubbots master plan.

### M15.01 - Remote manager, manifest fetch and version comparison

- [ ] SB-CP04-001 — Implement RemoteContentManager only when runtime integration milestone opens. [GAME_RUNTIME]
- [ ] SB-CP04-002 — Fetch production manifest over HTTPS. [GAME_RUNTIME]
- [ ] SB-CP04-003 — Compare remote/local content versions. [GAME_RUNTIME]
- [ ] SB-CP04-004 — Determine missing packs without redundant downloads. [GAME_RUNTIME]

### M15.02 - Download, integrity validation and activation

- [ ] SB-CP04-005 — Download to `user://content/`, never `res://`. [GAME_RUNTIME]
- [ ] SB-CP04-006 — Verify SHA-256. [GAME_RUNTIME]
- [ ] SB-CP04-007 — Validate pack/schema/level before activation. [GAME_RUNTIME]
- [ ] SB-CP04-008 — Activate verified content preserving last-known-good. [GAME_RUNTIME]

### M15.03 - Catalog bridge, runtime isolation and failure handling

- [ ] SB-CP04-009 — Expose remote levels to catalog/loader through narrow data interface. [GAME_RUNTIME]
- [ ] SB-CP04-010 — Keep generator/publisher code out of runtime. [GAME_RUNTIME]
- [ ] SB-CP04-011 — Add INTERNET permission only when runtime enabled. [GAME_RUNTIME]
- [ ] SB-CP04-012 — Handle network/server/parse/hash failures without blocking offline play. [GAME_RUNTIME]

### M15.04 - Compatibility and executable-payload rejection

- [ ] SB-CP04-013 — App/content version compatibility tests. [GAME_RUNTIME]
- [ ] SB-CP04-014 — Reject executable remote artifacts. [GAME_RUNTIME]

---

# M16 - Offline Cache & Last-Known-Good Recovery

Capability source family: `SB-CP05-xxx` from the main Scrubbots master plan.

### M16.01 - Local registry, last-known-good and offline boot

- [ ] SB-CP05-001 — Define local content registry under `user://`. [GAME_RUNTIME]
- [ ] SB-CP05-002 — Preserve last-known-good manifest/packs. [GAME_RUNTIME]
- [ ] SB-CP05-003 — Boot/play cached content offline. [GAME_RUNTIME]
- [ ] SB-CP05-004 — Safe fallback on manifest fetch failure. [GAME_RUNTIME]

### M16.02 - Corruption, interruption, retention and builtin levels

- [ ] SB-CP05-005 — Reject corrupt/incomplete downloads without replacing good cache. [GAME_RUNTIME]
- [ ] SB-CP05-006 — Interrupted-download recovery/cleanup. [GAME_RUNTIME]
- [ ] SB-CP05-007 — Cache size/retention policy. [GAME_RUNTIME]
- [ ] SB-CP05-008 — Builtin app levels playable independently. [GAME_RUNTIME]

### M16.03 - Cold launch, upgrade/downgrade and replacement safety

- [ ] SB-CP05-009 — First launch no-network test. [GAME_RUNTIME]
- [ ] SB-CP05-010 — Upgrade with partial/corrupt cache. [GAME_RUNTIME]
- [ ] SB-CP05-011 — Downgrade/compatibility behavior. [GAME_RUNTIME]
- [ ] SB-CP05-012 — Never delete only known-good set before replacement validates. [GAME_RUNTIME]

---

# M17 - Rollback, Disable & Scheduling

Capability source family: `SB-CP06-xxx` from the main Scrubbots master plan.

### M17.01 - Auditable rollback and individual disable

- [ ] SB-CP06-001 — Rollback as new auditable content version.
- [ ] SB-CP06-002 — Roll back to known-good manifest/pack set.
- [ ] SB-CP06-003 — Disable individual level IDs.
- [ ] SB-CP06-004 — Disabled levels skipped safely. [GAME_RUNTIME]

### M17.02 - Scheduling, time semantics and edit history

- [ ] SB-CP06-005 — Scheduled future activation.
- [ ] SB-CP06-006 — Timezone/time-source behavior. [PARTIAL]
- [ ] SB-CP06-007 — No schedule activates incompatible/unverified content. [PARTIAL]
- [ ] SB-CP06-008 — Cancel/edit future schedules with audit history.

### M17.03 - Rollback/disable tests and reproducible reports

- [ ] SB-CP06-009 — Rollback after bad live release test. [PARTIAL]
- [ ] SB-CP06-010 — Single-level disable test. [GAME_RUNTIME]
- [ ] SB-CP06-011 — Multiple weekly packs prepared together.
- [ ] SB-CP06-012 — Reproducible publish/rollback reports.

---

# M18 - Storage / CDN Provider Integration

Capability source family: `SB-CP07-xxx` from the main Scrubbots master plan.

### M18.01 - Provider selection and adapter boundary

- [ ] SB-CP07-001 — Evaluate provider candidates.
- [ ] SB-CP07-002 — Select provider with owner approval.
- [ ] SB-CP07-003 — Provider adapter; no credentials in project data. [PARTIAL]

### M18.02 - Storage separation, naming and integrity round trip

- [ ] SB-CP07-004 — Separate staging/production storage.
- [ ] SB-CP07-005 — Immutable/versioned object naming where practical.
- [ ] SB-CP07-006 — Upload/download/hash round trip.

### M18.03 - CDN strategy, backup, least privilege and schema isolation

- [ ] SB-CP07-007 — Cache-control/CDN strategy.
- [ ] SB-CP07-008 — Backup/export/migration path.
- [ ] SB-CP07-009 — Least-privilege publishing credentials.
- [ ] SB-CP07-010 — Keep provider-specific code outside gameplay/content schemas. [PARTIAL]

---

# M19 - Content Operations, QA & Observability

Capability source family: `SB-CP08-xxx` from the main Scrubbots master plan.

### M19.01 - Batch/version/hash/change records

- [ ] SB-CP08-001 — Weekly batch summary. [PARTIAL]
- [ ] SB-CP08-002 — Record staging/production versions.
- [ ] SB-CP08-003 — Record hashes/remote verification. [PARTIAL]
- [ ] SB-CP08-004 — Record disabled/scheduled/rollback changes.

### M19.02 - Health checks, safe errors and incident response

- [ ] SB-CP08-005 — Content-health check.
- [ ] SB-CP08-006 — Safe operational errors/alerts without unnecessary player data. [PARTIAL]
- [ ] SB-CP08-007 — Content incident runbook.

### M19.03 - Clean-machine dry run, disaster recovery and secret-free logs

- [ ] SB-CP08-008 — Clean-machine publish dry run. [PARTIAL]
- [ ] SB-CP08-009 — Disaster recovery from backups.
- [ ] SB-CP08-010 — Logs free of secrets. [PARTIAL]

---

# M20 - Store Policy, Security & Production Release Gate

Capability source family: `SB-CP09-xxx` from the main Scrubbots master plan.

### M20.01 - Current mobile-store policy verification

- [ ] SB-CP09-001 — Re-verify current Google Play remote-content/code policy before launch.
- [ ] SB-CP09-002 — Re-verify Apple requirements before iOS remote-content launch.

### M20.02 - Declarative-only payload and transport security

- [ ] SB-CP09-003 — Prove remote payloads declarative only. [PARTIAL]
- [ ] SB-CP09-004 — Prevent content data from embedding/evaluating executable expressions/scripts. [PARTIAL]
- [ ] SB-CP09-005 — HTTPS-only endpoints.

### M20.03 - Threat model, authenticity, secret/privacy and final audit

- [ ] SB-CP09-006 — Threat-model tampering/rollback attacks.
- [ ] SB-CP09-007 — Define authenticity upgrade if hash-only insufficient.
- [ ] SB-CP09-008 — No publishing secret ships in app. [PARTIAL]
- [ ] SB-CP09-009 — Privacy impact if telemetry enabled.
- [ ] SB-CP09-010 — Independent audit before production remote-content delivery.

---

# HISTORICAL EVIDENCE LEDGER — NOT A SECOND TASK DENOMINATOR

- PAG-M00..M10 accepted technical foundation remains immutable evidence; PAG-M10 visual pack remains OWNER REJECTED 100/100 negative evidence.
- PAG-SP00..SP06 accepted/remediated history remains immutable evidence.
- PAG-SP07-C001 strict audit = CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED; PAG-SP07-C001-R01 strict audit = PASS / CLOSED; both are mapped as accepted evidence under partial `SB-LF09-003` rather than counted as separate live tasks.
- PAG-SP08 maps to Edit/Inpaint capability; PAG-SP09 to Factory Studio UI; PAG-SP10 to automated batch production.
- PAG-SP11/PAG-SP12/PAG-SP13 are the three legacy unique extension tasks retained under M09.06.
- `SB-LFX-001..017` are owner-approved post-cutover Factory Studio/operator extensions governed by `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`; they add to the unified denominator but do not alter the 224 canonical LF/CP source mapping.
- PAG-SP14 is the final semantic-to-unified-Factory bridge/closure alias and adds no duplicate denominator.
- Windows Factory Studio v1.3.6 is retained as M06 migration evidence; its operator/provider/job/accounting layers are reusable, while its legacy compiler is not canonical.

Canonical migration/evidence documents:
- `docs/migration/PRE_UNIFICATION_TASKS_SNAPSHOT_2026-09-14.md`
- `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`
- `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`

Owner-approved post-cutover product specification:
- `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`

# CROSS-REPOSITORY RUNTIME REGISTER

`SB-CP04-001..014`, `SB-CP05-001..012`, `SB-CP06-004`, and `SB-CP06-010` are `[GAME_RUNTIME]` requirements. Implementation occurs in `Sekiph82/Scrubbots`; closure here requires exact main-game audit evidence.

# EXECUTION ORDER

1. M00 migration/governance is PASS/CLOSED through `SB-LF00-007`.
2. `SB-LF01-005` canonical-Core dimension dependency and `SB-LF06-002` target-control/runtime foundation are PASS/CLOSED; M06 continues at `SB-LF06-003` and then proceeds through Factory Studio canonical-Core migration plus owner-approved `SB-LFX-001..012` extensions in dependency-safe slices.
3. M03 Puzzle Intelligence.
4. M04 Difficulty Intelligence.
5. M05 Unified QA.
6. M07 mutation/difficulty targeting.
7. M08 batch production plus `SB-LFX-013..015` failure/import/recovery extensions.
8. Continue M09 advanced generation only as justified, including `SB-LFX-016..017` similarity/provider-accounting extensions when their dependencies are real.
9. M10 Campaign Intelligence.
10. M11-M14 Content Platform architecture/pack/manifest/publisher.
11. M18-M20 storage/operations/security.
12. M17 rollback/scheduling once manifest/publisher/storage are real.
13. M15-M16 main-game runtime/offline implementation in `Sekiph82/Scrubbots`.