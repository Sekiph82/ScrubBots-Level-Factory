# ScrubBots Level Factory — Canonical GitHub Task State

This root `TASKS.md` is the only authoritative project-status tracker consumed by H!veAI for this repository. GitHub repository metadata and the latest commit are supporting project-truth inputs. Hidden `.hiveai` control-plane tracker files are historical evidence only and are not read for live project state.

## Project Status

- Current Milestone: LF02 — Semantic / Constraint Candidate Generator
- Current Sprint: PAG-SP05-C002 — Difficulty V1 Contract Convergence & Trusted Compilation Evidence Closure
- Current Task: SB-LF02-004 — Support ART_FIRST mode consuming owner/AI-approved pixel art, masks or semantic provider output
- Current Task Status: AUDIT_REQUIRED
- Next Task/Action: ChatGPT independently audits PAG-SP05-C002. On PASS, map only directly proven evidence into the canonical SB-LF/SB-CP task rows, update this root tracker, and issue the next implementation prompt. On FAIL, issue a bounded remediation cycle without granting canonical completion credit.
- Required Actor: CHATGPT
- Tracking Repository: Sekiph82/ScrubBots-Level-Factory
- Tracking Branch: main
- Progress: 0 / 224 = 0.00%

## Program Scope

- Program: SCRUBBOTS Content Production Platform
- Canonical Task Count: 224
- Level Factory / Campaign tasks: 112 (`SB-LF00-*` .. `SB-LF10-*`)
- Content / Update Platform tasks: 112 (`SB-CP00-*` .. `SB-CP09-*`)
- Accepted canonical tasks: 0 / 224
- Active evidence cycle: PAG-SP05-C002
- Last builder publication: `1a2c29bec920abdf7f90cc914b18ba1ac18ca166`
- Current evidence mapping: LF02 semantic ART_FIRST candidate generation + LF05 validation/trust evidence candidate; canonical completion remains gated on independent audit.
- Main Game Runtime Repository: `Sekiph82/Scrubbots`
- Tracker Rule: ChatGPT is the sole writer of canonical task acceptance/checklist state. Codex/Claude read this file but do not edit it.

Owner decision: `coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md`
Architecture: `docs/CONTENT_PLATFORM_ARCHITECTURE_V01.md`
Cross-repo contract: `docs/CROSS_REPO_CONTRACT_V01.md`
Migration matrix: `docs/CONTENT_PLATFORM_MIGRATION_MATRIX_V01.md`
Studio migration: `docs/STUDIO_INTEGRATION_PLAN_V01.md`

> Tracker normalization does not create completion credit. Historical PAG M00-M10 / PAG-SP evidence remains valuable and is mapped onto the 224 canonical tasks only after independent audit.

## Status / ownership vocabulary

- `[x]` = independently audited and accepted against the current canonical task contract.
- `[~]` = active / in progress / awaiting the next lifecycle gate; not completed.
- `[ ]` = planned/open, not yet accepted under the current canonical task contract.
- `[!]` = blocked.
- `FACTORY` = implementation in this repository.
- `GAME_RUNTIME` = implementation primarily in `Sekiph82/Scrubbots`, tracked here for end-to-end program completion.
- `CROSS_REPO` = producer and consumer changes/tests required.
- `OWNER_DECISION` = closure requires an explicit owner choice/gate.

## Canonical owner-locked program rules

1. The shipping game never imports/preloads Factory/Publisher source.
2. Remote content is declarative only, never executable code/plugins/native libraries.
3. Runtime downloaded content lives under `user://`, never rewrites `res://`.
4. Main-game Difficulty V1 overrides stale class=dimension or class=color-count rules.
5. Production logical art uses C01..C16 and current 3..12 used-color envelope unless a newer audited family rule narrows it.
6. Rectangular boards are legal; 20..59 remains the current engine/content envelope, not difficulty identity.
7. Challenge, Session Load and Frustration Risk are separate.
8. CampaignBuilder sequences accepted immutable levels; it does not rewrite accepted logical cells.
9. Owner-original art is immutable unless the owner explicitly replaces it.
10. Studio/UI is an operator layer over canonical Factory Core, not a second compiler.
11. Publishing is validation-first, staging-first, integrity-checked, versioned, reversible and auditable.
12. No secrets in Git.

---

## Tasks

# LF00 — Content Platform Bootstrap & Isolation

Implementation owner: `FACTORY`
Migration state: existing bootstrap/governance evidence candidate; adapt from standalone generator to full Content Platform.

- [ ] SB-LF00-001 Establish `ScrubBots-Level-Factory` as the independently runnable canonical Content Production Platform repository.
- [ ] SB-LF00-002 Maintain clear README/governance/docs/src/studio/tests/output/schemas/publishing/coordination boundaries.
- [ ] SB-LF00-003 Enforce one-way integration: Factory exports declarative data/artifacts; main game never imports Factory implementation code.
- [ ] SB-LF00-004 Keep canonical Factory Core headless-testable and data-oriented independent of Studio UI.
- [ ] SB-LF00-005 Define separate one-command verification commands for core, Studio and publishing surfaces.
- [ ] SB-LF00-006 Define generated/candidate/cache/build/secret/publishing-local folders and exclusions.
- [ ] SB-LF00-007 Establish GitHub-first coordination structure with ChatGPT-owned tracker and immutable historical evidence.
- [ ] SB-LF00-008 Prove a clean checkout can install/verify the supported core toolchain without owner-local state.

# LF01 — Deterministic Generation Configuration & Seeds

Implementation owner: `FACTORY`
Migration state: strong existing M01/M02/M09 evidence candidate; Difficulty V1 convergence required.

- [ ] SB-LF01-001 Define deterministic versioned LevelGenerationConfig.
- [ ] SB-LF01-002 Store/replay seed for every candidate.
- [ ] SB-LF01-003 Same config + seed produces byte-identical canonical candidate data where deterministic providers permit.
- [ ] SB-LF01-004 Distinct seeds can produce distinct legal candidates.
- [ ] SB-LF01-005 Support independent width/height selection within current engine/content envelope and workload guidance.
- [ ] SB-LF01-006 Support rectangular boards.
- [ ] SB-LF01-007 Exercise 59×59 where cost scales.
- [ ] SB-LF01-008 Record seed/config/generator/model/version provenance.
- [ ] SB-LF01-009 Separate TEST/development candidates from production candidates.
- [ ] SB-LF01-010 Reject obsolete semantic assumptions, including class=dimension and class=color-count difficulty identity.

# LF02 — Semantic / Constraint Candidate Generator

Implementation owner: `FACTORY`
Migration state: substantial MASK/RULES/WFC/HYBRID/AUTO + PAG-SP semantic evidence candidate.

- [ ] SB-LF02-001 Implement evaluator-guided candidate architecture rather than blind random filling.
- [ ] SB-LF02-002 Support reverse construction when canonical gameplay mechanics permit.
- [ ] SB-LF02-003 Support PUZZLE_FIRST mode.
- [~] SB-LF02-004 Support ART_FIRST mode consuming owner/AI-approved pixel art, masks or semantic provider output.
- [ ] SB-LF02-005 Implement reusable shape/topology primitives without declaring them difficulty rules.
- [ ] SB-LF02-006 Implement connected color-region representation/generation.
- [ ] SB-LF02-007 Preserve one logical artwork square = one logical gameplay cell.
- [ ] SB-LF02-008 Never fabricate missing owner artwork or label generated output as owner-original.
- [ ] SB-LF02-009 Keep unresolved dependency/mechanic semantics behind design-gated adapters.
- [ ] SB-LF02-010 Keep unresolved slot/stack quantity/order generation design-gated.
- [ ] SB-LF02-011 Record complete candidate/provenance lineage.
- [ ] SB-LF02-012 Add deterministic unit/property tests across procedural and semantic candidate paths.

# LF03 — Puzzle Simulation, Solver & State Search

Implementation owner: `FACTORY / CROSS_REPO`
Migration state: major new work; must contract-test against canonical game semantics.

- [ ] SB-LF03-001 Create pure/headless puzzle simulation boundary.
- [ ] SB-LF03-002 Define compact deterministic solver state.
- [ ] SB-LF03-003 Define legal-move-provider interface.
- [ ] SB-LF03-004 Implement deterministic baseline search when required gameplay semantics are available.
- [ ] SB-LF03-005 Add visited-state memoization/hashing.
- [ ] SB-LF03-006 Record solution path/states/dead ends/depth/branching/solve time.
- [ ] SB-LF03-007 Add correctness-preserving pruning/order only with tests.
- [ ] SB-LF03-008 Add bounded solution-count/entropy analysis.
- [ ] SB-LF03-009 Reuse/contract-test canonical reachability, target and routing laws rather than inventing another game.
- [ ] SB-LF03-010 Reproduce solver bugs by candidate/seed/config/version.
- [ ] SB-LF03-011 Define budgets/timeouts and distinguish UNSOLVED/UNSOLVABLE/INCONCLUSIVE.
- [ ] SB-LF03-012 Add regression/golden fixtures shared with game semantics where appropriate.

# LF04 — Difficulty Intelligence & Metrics

Implementation owner: `FACTORY`
Migration state: new Difficulty V1 work; existing structural metrics are evidence inputs only.

- [ ] SB-LF04-001 Define versioned LevelMetrics.
- [ ] SB-LF04-002 Record solution depth/move/action count where meaningful.
- [ ] SB-LF04-003 Record searched states/dead ends/branching/forced moves.
- [ ] SB-LF04-004 Add dependency/unlock depth only when canonical semantics support it.
- [ ] SB-LF04-005 Add slot/color pressure only from canonical mechanics.
- [ ] SB-LF04-006 Add bait/deadlock/bottleneck metrics only when canonical and measurable.
- [ ] SB-LF04-007 Add color/remaining-state volatility where useful.
- [ ] SB-LF04-008 Implement/version Difficulty V1 Challenge Score W/C/A/U/B/R/S components and coefficients.
- [ ] SB-LF04-009 Map predicted score to owner-locked lane/cadence targets without equating class to board size.
- [ ] SB-LF04-010 Keep metric/model provenance and versioning.
- [ ] SB-LF04-011 Design future calibration against approved aggregate player data without enabling analytics by default.
- [ ] SB-LF04-012 Tests prove analysis is deterministic where specified and never mutates source gameplay/art data.

# LF05 — Factory Validation & Level QA

Implementation owner: `FACTORY / CROSS_REPO`
Migration state: strong deterministic export/quality evidence candidate; solver and Difficulty V1 convergence required.

- [ ] SB-LF05-001 Compose structural LevelData validation with current production compatibility + Difficulty V1 evaluation.
- [ ] SB-LF05-002 Reuse audited main-game round-trip contracts/golden fixtures for art-first exports.
- [ ] SB-LF05-003 Validate dimensions/envelope/C01..C16/current 3..12 used-color envelope/cells/alpha/provenance/duplicate IDs.
- [ ] SB-LF05-004 Reject proven-unsolvable candidates when solver is authoritative.
- [ ] SB-LF05-005 Distinguish INCONCLUSIVE from UNSOLVABLE.
- [ ] SB-LF05-006 Emit actionable rejection reasons.
- [ ] SB-LF05-007 Emit versioned machine-readable QA reports.
- [ ] SB-LF05-008 Preserve owner/provider raw source bytes and hashes immutably.
- [ ] SB-LF05-009 Enforce visual recognizability/readability gates so structural acceptance cannot masquerade as semantic acceptance.
- [ ] SB-LF05-010 Feed accepted artifacts into game catalog/content QA through explicit contracts rather than bypassing runtime validation.

# LF06 — Human-in-the-Loop Factory Studio

Implementation owner: `FACTORY`
Migration state: owner-supplied Windows v1.3.6 Studio is an evidence/source candidate; canonical-core adapter required.

- [ ] SB-LF06-001 Establish a supported Factory Studio operator workspace over canonical core APIs.
- [ ] SB-LF06-002 Expose target lane/dimensions/seed/provider/mode/candidate controls without embedding independent rule truth.
- [ ] SB-LF06-003 Provide Generate / Solve / Validate / Analyze / Reproduce actions.
- [ ] SB-LF06-004 Provide crisp logical board/art preview.
- [ ] SB-LF06-005 Display solution/difficulty/load/risk/art-QA/provenance metrics.
- [ ] SB-LF06-006 Support owner/designer paint/edit where explicitly allowed.
- [ ] SB-LF06-007 Allow only approved puzzle/config edits through typed contracts.
- [ ] SB-LF06-008 Revalidate/re-solve after manual changes.
- [ ] SB-LF06-009 Never auto-promote generated candidates to production.
- [ ] SB-LF06-010 Keep Studio presentation separate from core truth.
- [ ] SB-LF06-011 Reproduce candidates by seed/config/provider provenance where the provider contract supports reproduction.
- [ ] SB-LF06-012 Studio smoke/integration tests plus headless core regressions.

# LF07 — Mutation & Automatic Difficulty Targeting

Implementation owner: `FACTORY`
Migration state: new work.

- [ ] SB-LF07-001 Define mutation interface and immutable lineage.
- [ ] SB-LF07-002 Implement only semantic-preserving/canonical hardening mutations.
- [ ] SB-LF07-003 Implement only semantic-preserving/canonical easing mutations.
- [ ] SB-LF07-004 Re-solve/revalidate after every mutation.
- [ ] SB-LF07-005 Preserve seed/parent/mutation provenance.
- [ ] SB-LF07-006 Target Challenge Score windows while respecting Session Load, Frustration Risk, readability and retention constraints.
- [ ] SB-LF07-007 Bound mutation attempts.
- [ ] SB-LF07-008 Compare mutate-vs-regenerate efficiency and quality.
- [ ] SB-LF07-009 Never mutate owner-original source art silently.
- [ ] SB-LF07-010 Add deterministic mutation regression tests.

# LF08 — Batch Factory & Weekly Production

Implementation owner: `FACTORY`
Migration state: strong CLI/batch/resume evidence candidate.

- [ ] SB-LF08-001 Generate requested accepted counts by campaign lane/target criteria.
- [ ] SB-LF08-002 Separate generated-attempt count from accepted count.
- [ ] SB-LF08-003 Record rejection statistics/reasons.
- [ ] SB-LF08-004 Support deterministic/resumable batch jobs where provider contracts permit.
- [ ] SB-LF08-005 Prevent duplicate IDs/seeds/artifacts and provenance collisions.
- [ ] SB-LF08-006 Produce accepted LevelData/previews/metadata/QA/provenance as batch output.
- [ ] SB-LF08-007 Provide owner review/approval queue before publication.
- [ ] SB-LF08-008 Produce production-ready handoff into Content Packaging/Publishing.
- [ ] SB-LF08-009 Stress high rejection/provider-failure rates safely.
- [ ] SB-LF08-010 Reruns/resume create no meaningless diffs or duplicate promotions.

# LF09 — Advanced Generation Research [EXPERIMENTAL]

Implementation owner: `FACTORY`
Migration state: existing WFC/semantic research evidence candidate; production promotion remains gated.

- [ ] SB-LF09-001 Prototype evolutionary/multi-objective selection behind an experimental flag.
- [ ] SB-LF09-002 Use versioned fitness metrics.
- [ ] SB-LF09-003 Prototype procedural/semantic art helpers without replacing owner-approved art direction.
- [ ] SB-LF09-004 Telemetry-calibrated difficulty only after explicit analytics/data-policy approval.
- [ ] SB-LF09-005 Keep live/runtime level generation disabled unless explicitly approved.
- [ ] SB-LF09-006 Preserve reproducibility/lineage.
- [ ] SB-LF09-007 Compare advanced generation quality, provider cost and compute cost.
- [ ] SB-LF09-008 Require separate audit/owner gate before production promotion of experimental paths.

# LF10 — Campaign / Sequencing Adapter

Implementation owner: `FACTORY`
Migration state: new work.

- [ ] SB-LF10-001 Define versioned CampaignBuilder interface.
- [ ] SB-LF10-002 Consume owner-locked Difficulty V1 rhythm/progression/retention rules.
- [ ] SB-LF10-003 Select accepted production levels without modifying their logical data.
- [ ] SB-LF10-004 Prevent duplicate/unavailable/disabled selection.
- [ ] SB-LF10-005 Preserve deterministic campaign-build provenance.
- [ ] SB-LF10-006 Rebuild campaign ordering without regenerating levels.
- [ ] SB-LF10-007 Represent future events/featured content as declarative data, not code.
- [ ] SB-LF10-008 Validate campaign challenge/load/frustration/recovery/novelty/similarity constraints.

---

# CP00 — Content Pipeline Architecture & Security

Implementation owner: `FACTORY / CROSS_REPO`
Migration state: canonical architecture established by Content Platform consolidation; implementation gates remain open.

- [ ] SB-CP00-001 Establish publisher/control-plane modules inside the Content Platform repository with clean separation from generation core.
- [ ] SB-CP00-002 Define shipping app code vs remote declarative-content boundary.
- [ ] SB-CP00-003 Enforce remote content declarative-only; forbid executable payloads.
- [ ] SB-CP00-004 Separate STAGING and PRODUCTION environments/state.
- [ ] SB-CP00-005 Define versioned/auditable publish/promotion/rollback state.
- [ ] SB-CP00-006 Define secret handling; no publishing/provider credentials in Git or content packages.
- [ ] SB-CP00-007 Require publisher dry-run/validation-only mode before remote mutation.
- [ ] SB-CP00-008 Define storage/provider abstraction.
- [ ] SB-CP00-009 Establish GitHub-first cross-repo coordination under ChatGPT-owned canonical tracker.
- [ ] SB-CP00-010 Re-verify mobile/store-policy boundary before release and when policy-sensitive architecture changes.

# CP01 — `.scrubpack` Format & Packager

Implementation owner: `FACTORY`
Migration state: new format; deterministic M08 bundle machinery is reusable evidence only.

- [ ] SB-CP01-001 Define versioned `.scrubpack` specification.
- [ ] SB-CP01-002 Package declarative approved levels/content only.
- [ ] SB-CP01-003 Record pack ID/version/build metadata/contained level IDs.
- [ ] SB-CP01-004 Compute/record per-pack SHA-256.
- [ ] SB-CP01-005 Use deterministic serialization/order where the container permits.
- [ ] SB-CP01-006 Prevent duplicate level IDs and ownership conflicts inside packs.
- [ ] SB-CP01-007 Validate every level/artifact before packaging.
- [ ] SB-CP01-008 Provide unpack/inspect tooling.
- [ ] SB-CP01-009 Prove deterministic pack bytes or explicitly document non-byte-deterministic container metadata.
- [ ] SB-CP01-010 Reject unsupported pack/schema versions safely.

# CP02 — Remote Manifest & Content Versioning

Implementation owner: `FACTORY / CROSS_REPO`
Migration state: new work.

- [ ] SB-CP02-001 Define versioned remote manifest schema.
- [ ] SB-CP02-002 Include schema_version + monotonic content_version.
- [ ] SB-CP02-003 Include minimum_game_version compatibility.
- [ ] SB-CP02-004 Include pack IDs/locations/hashes.
- [ ] SB-CP02-005 Include level metadata without unnecessary contiguous-ID assumptions.
- [ ] SB-CP02-006 Support disabled_levels.
- [ ] SB-CP02-007 Support scheduled activation windows.
- [ ] SB-CP02-008 Reject duplicate pack/level ownership conflicts.
- [ ] SB-CP02-009 Validate every manifest reference before publication.
- [ ] SB-CP02-010 Preserve prior manifests/content-version history.
- [ ] SB-CP02-011 Define app/content schema compatibility behavior.
- [ ] SB-CP02-012 Add producer/consumer parser-schema golden tests.

# CP03 — Publisher, Staging & Production Promotion

Implementation owner: `FACTORY`
Migration state: new work.

- [ ] SB-CP03-001 Implement publisher validation-only/dry-run mode.
- [ ] SB-CP03-002 Serialize accepted Factory/Campaign output into `.scrubpack` artifacts.
- [ ] SB-CP03-003 Generate hashes + candidate manifest.
- [ ] SB-CP03-004 Upload/version packs before any active manifest references them.
- [ ] SB-CP03-005 Verify remote object integrity after upload.
- [ ] SB-CP03-006 Publish to STAGING first.
- [ ] SB-CP03-007 Verify staging through a real download/consumer validation path.
- [ ] SB-CP03-008 Require explicit STAGING→PRODUCTION promotion.
- [ ] SB-CP03-009 Publish a new versioned production manifest.
- [ ] SB-CP03-010 Prohibit silent live overwrite.
- [ ] SB-CP03-011 Add one-command publish only after every stage is independently testable/recoverable.
- [ ] SB-CP03-012 Emit versioned publish report/evidence.

# CP04 — Godot Remote Content Runtime

Implementation owner: `GAME_RUNTIME` in `Sekiph82/Scrubbots`; tracker/e2e acceptance remains here.
Migration state: open runtime work.

- [ ] SB-CP04-001 Implement RemoteContentManager only when runtime integration milestone opens.
- [ ] SB-CP04-002 Fetch production manifest over HTTPS.
- [ ] SB-CP04-003 Compare remote/local content versions.
- [ ] SB-CP04-004 Determine missing packs without redundant downloads.
- [ ] SB-CP04-005 Download to `user://content/`, never `res://`.
- [ ] SB-CP04-006 Verify SHA-256/integrity before activation.
- [ ] SB-CP04-007 Validate pack/schema/level before activation.
- [ ] SB-CP04-008 Activate verified content while preserving last-known-good.
- [ ] SB-CP04-009 Expose remote levels to catalog/loader through a narrow declarative interface.
- [ ] SB-CP04-010 Keep generator/publisher implementation code out of shipping runtime.
- [ ] SB-CP04-011 Add INTERNET permission only when remote runtime is enabled.
- [ ] SB-CP04-012 Handle network/server/parse/hash failures without blocking offline play.
- [ ] SB-CP04-013 Add app/content version compatibility tests using shared golden vectors.
- [ ] SB-CP04-014 Reject executable remote artifacts/payloads.

# CP05 — Offline Cache & Last-Known-Good Recovery

Implementation owner: `GAME_RUNTIME` in `Sekiph82/Scrubbots`; tracker/e2e acceptance remains here.
Migration state: open runtime work.

- [ ] SB-CP05-001 Define local content registry under `user://`.
- [ ] SB-CP05-002 Preserve last-known-good manifest/packs.
- [ ] SB-CP05-003 Boot/play cached content offline.
- [ ] SB-CP05-004 Safe fallback on manifest fetch failure.
- [ ] SB-CP05-005 Reject corrupt/incomplete downloads without replacing good cache.
- [ ] SB-CP05-006 Recover/clean interrupted downloads safely.
- [ ] SB-CP05-007 Define cache size/retention policy.
- [ ] SB-CP05-008 Keep builtin app levels playable independently of remote service.
- [ ] SB-CP05-009 Test first launch with no network.
- [ ] SB-CP05-010 Test upgrade with partial/corrupt cache.
- [ ] SB-CP05-011 Define/test downgrade and compatibility behavior.
- [ ] SB-CP05-012 Never delete the only known-good set before a replacement fully validates.

# CP06 — Rollback, Disable & Scheduling

Implementation owner: `FACTORY + GAME_RUNTIME / CROSS_REPO`
Migration state: new work.

- [ ] SB-CP06-001 Implement rollback as a new auditable content version/state transition.
- [ ] SB-CP06-002 Roll back to a known-good manifest/pack set.
- [ ] SB-CP06-003 Disable individual level IDs declaratively.
- [ ] SB-CP06-004 Ensure game runtime skips disabled levels safely.
- [ ] SB-CP06-005 Support scheduled future activation.
- [ ] SB-CP06-006 Define timezone/time-source behavior.
- [ ] SB-CP06-007 Prevent schedules from activating incompatible/unverified content.
- [ ] SB-CP06-008 Cancel/edit future schedules with audit history.
- [ ] SB-CP06-009 Test rollback after a bad live release.
- [ ] SB-CP06-010 Test single-level disable end-to-end.
- [ ] SB-CP06-011 Prepare multiple weekly packs together without ambiguous activation.
- [ ] SB-CP06-012 Emit reproducible publish/rollback/disable reports.

# CP07 — Storage / CDN Provider Integration

Implementation owner: `FACTORY / OWNER_DECISION`
Migration state: provider decision pending.

- [ ] SB-CP07-001 Evaluate storage/CDN provider candidates against cost, reliability, API, immutability and migration needs.
- [ ] SB-CP07-002 Select provider with owner approval.
- [ ] SB-CP07-003 Implement provider adapter; no credentials in project data.
- [ ] SB-CP07-004 Separate staging/production storage namespaces/buckets.
- [ ] SB-CP07-005 Use immutable/versioned object naming where practical.
- [ ] SB-CP07-006 Prove upload/download/hash round trip.
- [ ] SB-CP07-007 Define cache-control/CDN strategy.
- [ ] SB-CP07-008 Define backup/export/provider-migration path.
- [ ] SB-CP07-009 Use least-privilege publishing credentials.
- [ ] SB-CP07-010 Keep provider-specific code outside gameplay/content schemas.

# CP08 — Content Operations, QA & Observability

Implementation owner: `FACTORY`
Migration state: new work.

- [ ] SB-CP08-001 Produce weekly/batch production summary.
- [ ] SB-CP08-002 Record staging/production versions.
- [ ] SB-CP08-003 Record hashes and remote verification results.
- [ ] SB-CP08-004 Record disabled/scheduled/rollback changes.
- [ ] SB-CP08-005 Implement content-health checks.
- [ ] SB-CP08-006 Emit safe operational errors/alerts without unnecessary player data.
- [ ] SB-CP08-007 Maintain content incident runbook.
- [ ] SB-CP08-008 Prove clean-machine publish dry run.
- [ ] SB-CP08-009 Prove disaster recovery from backups/versioned storage.
- [ ] SB-CP08-010 Keep operational logs free of secrets.

# CP09 — Store Policy, Security & Release Gate

Implementation owner: `CROSS_REPO / OWNER_DECISION`
Migration state: release-gate work.

- [ ] SB-CP09-001 Re-verify current Google Play remote-content/code policy before launch.
- [ ] SB-CP09-002 Re-verify Apple remote-content requirements before iOS launch.
- [ ] SB-CP09-003 Prove remote payloads are declarative only.
- [ ] SB-CP09-004 Prevent content data from embedding/evaluating executable expressions/scripts.
- [ ] SB-CP09-005 Require HTTPS-only runtime endpoints.
- [ ] SB-CP09-006 Threat-model tampering, downgrade and rollback attacks.
- [ ] SB-CP09-007 Define authenticity/signature upgrade if hash-only integrity becomes insufficient.
- [ ] SB-CP09-008 Ensure no publishing/provider secret ships in the app.
- [ ] SB-CP09-009 Review privacy impact before any telemetry/analytics is enabled.
- [ ] SB-CP09-010 Require independent end-to-end audit before production remote-content delivery.

---

## Legacy PAG / Semantic Pixel Studio Evidence

Historical accepted PAG M00-M10 and PAG-SP cycles remain authoritative evidence for what was actually implemented/tested at the time. They are not deleted and are not automatically converted into `[x]` above.

Pre-consolidation tracker state is recoverable from Git history at commits before this migration, including `9f5fa4f7fabd8f7e5d12abbca5431af8b539c882` and the immediately preceding SP05 tracker update.

Current semantic direction retained from that program:

`SEMANTIC IMAGE -> CELL_MAJORITY -> PALETTE SNAP -> ONE LOGICAL PIXEL = ONE GAMEPLAY CELL -> C01..C16 -> CURRENT DIFFICULTY/QA EVALUATION -> VALIDATION/EXPORT`

The historical class-specific dimension/color bands are no longer current Difficulty V1 truth.

PAG-SP05-C001 was independently audited FAIL because of the stale Difficulty V1 contract and trusted-construction boundary. PAG-SP05-C002 is the bounded remediation. Its builder implementation and log are published, but canonical task completion credit remains withheld until independent ChatGPT audit.

## Next Action

Independently audit PAG-SP05-C002 against the current Content Platform and main-game Difficulty V1 contracts. Only after a PASS may accepted evidence close or partially advance the directly supported canonical SB-LF/SB-CP task rows.