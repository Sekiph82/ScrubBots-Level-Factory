# MAINT-SUPPLY-PIPELINE-V01-R01 — Strict Closure Remediation

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Game authority:
https://github.com/Sekiph82/Scrubbots

Parent audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/MAINT-SUPPLY-MASTER-C001_PRIMARY_PIPELINE_STRICT_AUDIT.md

R01 audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/MAINT-SUPPLY-PIPELINE-V01-R01_STRICT_CLOSURE_AUDIT_CRITERIA.md

Owner primary-pipeline decision:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V01.md

## Mandatory local ↔ GitHub sync preflight

Before product edits:

### Level Factory
1. Work only in `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
2. Verify repo = `Sekiph82/ScrubBots-Level-Factory`, branch = `main`.
3. `git fetch origin --prune`.
4. Inspect HEAD, origin/main, dirty state, stashes, worktrees, ahead/behind.
5. Clean/behind => `git merge --ff-only origin/main`.
6. Preserve legitimate local work non-destructively.
7. Never reset, rebase, stash, clean, force checkout, force push, discard owner work.
8. Never create a branch or Desktop sibling clone/worktree.
9. Begin only after safe sync.

### Scrubbots read-only authority
1. Verify canonical local game repo identity and `main`.
2. Fetch/prune.
3. Verify current game main includes uncapped commit `e1a36d317ef79d2e877aa1402d7bbca3f00606b1` or a descendant.
4. Do not edit game product files in this R01.
5. If relevant authority source files are dirty/incompatible, Level Factory production acceptance must fail closed and the builder must report the blocker.

## Objective

Close every F01..F10 finding from the parent audit.

Do NOT replace the existing owner ZIP-derived optimizer architecture.
Do NOT revert the uncapped batch rule.
Do NOT resume SB-LF09-004.

## R01 implementation requirements

### R01.1 — Add authentic production runtime WON gate

Strengthen the bridge/orchestration so a production candidate is READY only after:
- real `SolvabilitySolver.solve == SOLVED`;
- real solver replay solved;
- same ordered click sequence is driven through current shipping runtime, using `ProductionGameplayHost` or the exact accepted equivalent exercised by current M52 production tests;
- runtime reaches WON / exact complete end-state.

Return structured runtime evidence.

No proof-kernel-only substitute.

### R01.2 — Execute exact shipping load check before READY

Use the existing/adapted `godot/load_check.gd` or an equivalent exact-game loader bridge.

After export:
- load exact emitted level via `LevelLoader`;
- load exact emitted supply plan via `SupplyPlanLoader`;
- require PASS before production READY.

Bind exact file digests to the result.

### R01.3 — Require official Difficulty V1

Production READY requires:
- `difficultyV1.ok == true`;
- final score/class from official current game analyzer.

If missing:
- production disposition cannot be READY.

Transparent/non-full-canvas:
- may return PROVISIONAL/non-production analysis;
- must not emit production-ready level/supply claim.

### R01.4 — Make canonical candidate/logical-grid route primary

Add an exact-grid entrypoint accepting existing Factory canonical:
- candidate ID/bundle;
- width/height;
- exact Cxx logical cells/palette identity;
- source/grid provenance.

Do not encode to PNG then decode again.

Connect existing `run_pipeline(candidate_id=...)` eligible candidates to the ZIP primary pipeline instead of legacy M03/M04 pending states.

Preserve owner review as independent.

Image-path route may remain as auxiliary.

### R01.5 — Fix FactoryCoreGateway capability truth

Update `level_factory/scripts/factory_core_gateway.gd`.

When authenticated game bridge is available:
- Solve = AVAILABLE;
- Analyze = AVAILABLE.

Capability reason must be current and truthful.

When Godot/game authority missing/dirty:
- UNAVAILABLE.

Remove stale active messages that say M03/M04 are pending.

### R01.6 — Authority cleanliness/fingerprint

Strengthen `GameRules`/bridge authority.

At minimum:
- verify repo identity;
- verify branch main;
- record HEAD;
- verify relevant authority paths are clean OR hash all relevant game source files and bind hashes;
- include runtime host path/identity in authority surface;
- include bridge version.

Relevant files include at least:
- supply loader/engine/color batch;
- ProofState/SolvabilitySolver/ProofKernel;
- runtime ProductionGameplayHost or accepted runtime seam;
- Difficulty V1 analyzer;
- LevelData/LevelLoader;
- targeting/routing dependencies materially used by proof/runtime.

Do not reject unrelated owner files unless they affect authority.

### R01.7 — Remove bridge literal 3/3 seam

Use:
- `SupplyPlanLoader.COLUMN_COUNT`
- `SupplyPlanLoader.VISIBLE_PREVIEW_DEPTH`
for engine creation and validation.

### R01.8 — Complete authentic 37x37 and 59x59 full pipelines

Produce deterministic full-canvas 37x37 and 59x59 cases that complete the entire authentic pipeline.

Required stages:
- analyze;
- candidate generate/mutate;
- screening;
- scorer;
- game solve;
- replay;
- runtime WON;
- Difficulty V1;
- export;
- load check.

If current ranking/search wastes time, optimize Level Factory orchestration/ranking only.

Do not weaken game authority.

The final run must actually complete, not be interrupted.

Record:
- size;
- seed;
- candidate count;
- supply rows;
- total batches;
- max batch amount;
- solver visited;
- trace length/hash;
- runtime WON;
- challenge score/class;
- export/load status;
- elapsed time as noncanonical diagnostic.

### R01.9 — Complete 12/12 adapted ZIP tests

Final canonical validation run on owner machine:
- 12 passed;
- no deselected slow test.

### R01.10 — Full regressions

After implementation:
- full pytest;
- compileall;
- Factory Studio Godot headless suite;
- relevant game read-only M52/solver/runtime/load tests;
- diff check.

The active-task contract should now match the auditor-updated R01 tracker state.

## New tests required

Add explicit tests for:
- runtime gate missing/failing => no READY;
- load-check failure => no READY;
- official Difficulty V1 missing => no READY;
- transparent input => PROVISIONAL/not production READY;
- dirty relevant game solver source => UNAVAILABLE;
- clean relevant authority + unrelated dirty file => capability remains truthful;
- canonical candidate exact-grid path performs no PNG roundtrip;
- Gateway Solve/Analyze availability toggles with game/Godot authority;
- bridge uses authoritative column/preview constants;
- 37/59 closure run.

## Builder governance

Do not edit:
- root `TASKS.md`;
- `.hiveai/audits/**`.

Create builder log before product edits:
`.hiveai/codex-logs/MAINT-SUPPLY-PIPELINE-V01-R01_STRICT_CLOSURE_CODEX_LOG.md`

Commit product changes separately from log publication.

Push directly to `main`.
Fetch again and prove local HEAD == origin/main, divergence 0/0.
Stop for independent audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-SUPPLY-PIPELINE-V01-R01_STRICT_CLOSURE_CODEX_LOG.md
