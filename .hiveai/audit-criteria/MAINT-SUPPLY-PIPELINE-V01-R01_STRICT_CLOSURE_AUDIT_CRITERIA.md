# MAINT-SUPPLY-PIPELINE-V01-R01 — Strict Closure Audit Criteria

Parent audit:
`.hiveai/audits/MAINT-SUPPLY-MASTER-C001_PRIMARY_PIPELINE_STRICT_AUDIT.md`

Parent verdict:
`CHANGES_REQUIRED`

Game uncapped prerequisite:
`PASS/CLOSED`

## R01 PASS rule

PASS only if all parent F01..F10 findings are closed without replacing the owner ZIP-derived optimizer architecture.

## F01 runtime admission

A production READY result must include authentic current-game runtime admission after solver replay.

Required evidence:
- same emitted supply/click sequence;
- real shipping runtime seam, preferably `ProductionGameplayHost` or the accepted equivalent used by current M52 production tests;
- reaches WON;
- no synthetic proof-state-only substitute;
- runtime failure => REJECTED/ERROR, never READY.

Bind runtime evidence to level, supply, click sequence and game authority identity.

## F02 shipping load check

Before READY:
- exact emitted LevelData file must load through current `LevelLoader`;
- exact emitted supply plan must load through current `SupplyPlanLoader`;
- load check must be executed, not merely exist as a script;
- failure => REJECTED/ERROR.

## F03 official difficulty required

For production READY:
- `difficultyV1.ok == true`;
- final Challenge Score/class must derive from current `LevelDifficultyAnalyzerV1`;
- provisional heuristic score may be displayed only with state `PROVISIONAL`/non-production;
- transparent/non-full-canvas input must never return production READY.

## F04 canonical Factory input/default path

Existing canonical Factory candidates/logical grids must reach the new primary ZIP pipeline directly.

Required:
- candidate/source route consumes exact canonical cells + palette identity without PNG re-encode/re-read;
- new ZIP pipeline becomes default Solve/Difficulty path for eligible canonical candidates;
- existing provenance/QA/review identity remains bound;
- image-path helper may remain but cannot be the only production route;
- legacy “M03/M04 pending” path must not intercept eligible canonical candidate runs.

## F05 Gateway capabilities

When:
- local canonical game checkout exists;
- authority validation passes;
- Godot exists;

FactoryCoreGateway must expose:
- Solve AVAILABLE;
- Analyze AVAILABLE;
- reasons must reference authenticated current game bridge.

When unavailable/dirty/incompatible:
- truthful UNAVAILABLE.

Remove stale “pending M03/M04” claims from active capability truth.

## F06 clean authority proof

Production acceptance must fail closed if relevant game authority is dirty or unverifiable.

At minimum bind:
- repository identity;
- branch;
- HEAD SHA;
- clean-status proof for relevant authority paths OR versioned hashes of every relevant authority source file;
- loader/solver/proof/runtime/difficulty identities;
- bridge version.

A dirty unrelated user file such as `project.godot` may be tolerated only if proven irrelevant to the authority surface and explicitly classified.

Relevant authority modification => UNAVAILABLE/ERROR.

## F07 no retyped shipping constants

Bridge engine construction/validation must use current imported game authority:
- `SupplyPlanLoader.COLUMN_COUNT`;
- `SupplyPlanLoader.VISIBLE_PREVIEW_DEPTH`;
and equivalent authoritative constants where available.

No literal 3/3 acceptance seam in the bridge core.

## F08 37x37 and 59x59 authentic end-to-end evidence

Both sizes must complete successfully through:
- primary optimizer;
- screening ranking;
- authentic game solve;
- game replay;
- real runtime WON gate;
- official Difficulty V1;
- export;
- shipping load check.

Do not mark an interrupted/timeout run PASS.

Performance remediation may:
- reduce wasted candidate screening work;
- improve batching/orchestration;
- choose deterministic full-canvas test images/supplies that exercise the real pipeline;
- improve ranking to reach a solvable candidate sooner.

It may NOT:
- weaken game solver bounds to produce false success;
- bypass solver/runtime;
- substitute a pre-authored supply without passing through the primary pipeline;
- skip 59x59.

Record elapsed time as noncanonical evidence only.

## F09 all 12 ZIP-derived tests

The adapted full test module must complete:
- 12/12 pass when game/Godot capability is available;
- no deselected slow closure test in the final acceptance run.

Capability skips are allowed only on machines genuinely lacking the capability, not on the owner's canonical validation machine.

## F10 full regression

After ChatGPT-owned tracker is synchronized to R01:
- full Level Factory pytest must be green except accepted capability skips;
- compileall PASS;
- Factory Studio headless suite PASS;
- relevant Scrubbots read-only regression PASS;
- git diff --check PASS.

## Additional acceptance protections

- ScreeningSimulator remains ranking-only.
- No global robot-count max is reintroduced.
- No fixed 18 supply rows.
- NumPy/Pillow stay local/offline.
- No network/cloud/API dependency.
- No new branch/Desktop sibling worktree.
- Builder must not edit `TASKS.md` or `.hiveai/audits/**`.
