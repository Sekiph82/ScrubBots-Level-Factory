# MAINT-ZIP-CORE-V02-C001 — Level Factory Only — Strict Audit

Date: 2026-10-02
Auditor: ChatGPT
Verdict: **CHANGES_REQUIRED**

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-LF_ONLY_CODEX_LOG.md`

Primary implementation commit:
`8bf28292fa77b09016289ebe81fd6150ef516562`

Current `main` is a descendant of the implementation commit.

Owner authority:
`docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md`

Game-side prerequisite:
`MAINT-SUPPLY-COLUMNS-C001 = PASS/CLOSED`
by:
`Sekiph82/Scrubbots/coordination/sessions/MAINT-SUPPLY-COLUMNS-C001/CHATGPT_AUDIT_V01.md`

## Executive result

The ZIP-derived supply core is retained and several important pieces are correct:

- explicit 3/4/5 Level Factory column contract exists;
- default column count remains 3;
- visible preview depth remains 3;
- ZIP candidates remain 300 by default;
- screening and viability budgets remain 3000;
- original + max-three-mutation behavior remains intact;
- SupplyScorer source was not retuned by this task;
- mean-batch-size seed ranges remain unchanged;
- no global robot/batch cap was reintroduced;
- canonical logical-grid input can now enter `SupplyOptimizer.run_grid()` without PNG roundtrip;
- canonical game solve + replay/WIN remains acceptance authority;
- official Difficulty V1 is required by the optimizer acceptance path;
- generated candidate grids and exact OWNER_UPLOAD grids can converge on the ZIP route;
- 4- and 5-column LF-side solver/export evidence was produced;
- owner review ACCEPT/REJECT is connected to a publication hook.

However, the owner-approved V02 cutover is not complete.

## Blocking findings

### F01 — Requested difficulty still exists in the active artwork-generation contract

Owner decision:
requested difficulty is removed from Level Factory and artwork generation must not ask for or silently inject EASY/MEDIUM/HARD/VERY_HARD.

Current active code still has:

- `GenerationRequest.difficulty` as a required field;
- `GenerationRequest.__post_init__()` parses it;
- dimension resolution still depends on difficulty;
- palette subset resolution still depends on difficulty;
- canonical request serialization still writes difficulty;
- CLI `generate` / `batch` still expose `--difficulty`;
- `factory_core_gateway.gd::_generate_arguments()` still injects:
  `--difficulty EASY`;
- quality policy creation still derives from `request.difficulty`.

Removing the Studio dropdown did not remove requested difficulty from the product system.

**Disposition: BLOCKER.**

### F02 — FactoryCoreGateway Solve/Analyze remain hard-coded UNAVAILABLE

Current:
`level_factory/scripts/factory_core_gateway.gd`

still declares:
- Solve = UNAVAILABLE;
- Analyze = UNAVAILABLE.

This contradicts the owner-approved ZIP-primary cutover and the fact that the ZIP/game bridge now exists.

When the current game checkout + Godot + ZIP bridge are available:
- Solve must route to the ZIP backend;
- Analyze must surface official Difficulty V1 from that same run.

When capability is unavailable:
- report truthful UNAVAILABLE.

Hard-coded permanent UNAVAILABLE is not the canonical cutover.

**Disposition: BLOCKER.**

### F03 — Background intent is not wired into the active artwork-generation UI/request

The semantic generation subsystem already contains a `no_background` concept, but the active Factory Studio target controls/current classic generation request do not expose and propagate the owner decision:

- background requested => generate/fill background during artwork creation;
- background not requested => preserve transparency.

No later silent background fill is allowed.

The current cutover removed Difficulty UI but did not complete this owner-approved artwork input.

**Disposition: BLOCKER.**

### F04 — “Automatic publish” currently publishes only inside Level Factory staging

Current:
`studio_extensions._auto_publish_candidate()`

copies files into:

`level_factory/output/studio-extensions/published/<candidate>/`

and writes a Level Factory-local publication manifest.

It does not publish the accepted level into the configured Scrubbots game checkout:
- `data/levels/`;
- `data/levels/supply/`;
- metadata/preview as required;
- production catalog.

This is useful isolated staging, but it is not the owner-approved:
`Owner ACCEPT -> automatic publish to Scrubbots`.

Builder implementation must remain LF-only source-code work; runtime publisher tests must use isolated/temp game roots, not mutate the owner's live checkout during validation.

**Disposition: BLOCKER.**

### F05 — Progression placement is not bound to the real game progression/catalog contract

Current:
`supply_pipeline/progression.py`

simply sorts:
`difficulty_score ascending -> level_id ascending`

and writes an isolated LF `progression.json`.

The actual game has owner-locked progression/cadence authority:
- `data/config/level_progression_v1.json`;
- `scripts/difficulty/difficulty_progression_v1.gd`;
- `data/levels/catalog/production_catalog_v1.json`.

The game cadence is not a global easy-to-hard sort.

Progression placement must use official Difficulty V1 plus the current game progression/campaign contract, with deterministic tie-break and stable immutable IDs.

Do not destructively rename immutable level IDs.

Do not silently renumber live save identities without an explicit safe migration contract.

**Disposition: BLOCKER.**

### F06 — Shipping load-check is still not a required pre-publication step

The owner V02 flow retains ZIP/game load-check as file compatibility validation.

Current primary/artwork routes:
- solve;
- replay;
- official Difficulty V1;
- export;
then can be treated as READY/publishable without executing the exact exported level + supply through the shipping loader check.

`verify_exported_supply()` exists but is not a mandatory publication gate.

Load-check is not a second solver authority, but it must pass before auto-publish.

**Disposition: BLOCKER.**

### F07 — Competing legacy production solver/difficulty backend was not actually retired

The builder did not remove or formally decommission the old M03/M04 production architecture.

Legacy modules remain in active source, including:
- `compact_solver_state.py`;
- `legal_move_provider.py`;
- `baseline_search.py`;
- `visited_memoization.py`;
- `solver_evidence.py`;
- `search_policy.py`;
- `solution_analysis.py`;
- `canonical_bridge.py`;
- `solver_budget.py`;
- `simulation_boundary.py`;
- `difficulty_analysis.py`;
- `level_metrics.py`.

The task required a dependency scan:
- delete modules/tests used solely by the retired production backend;
- or document a minimal non-competing historical/evidence role and prove the ZIP production path cannot call them.

That closure evidence is absent.

**Disposition: BLOCKER.**

### F08 — Full Level Factory regression suite is not green

Builder result:
- `1117 passed`
- `3 skipped`
- `15 failed`

Some failures are indeed stale expectations for the removed Difficulty control/M03/M04 wording, but stale tests are still repository defects after a product contract cutover.

The task explicitly required:
- update/remove obsolete tests;
- preserve only valid historical compatibility;
- finish with a green full suite except truthful capability skips.

**Disposition: BLOCKER.**

### F09 — Current game 3/4/5 support must now be revalidated end-to-end from Level Factory

At builder time, the separate game task was still moving.

It is now independently audited PASS/CLOSED.

R01 must run authentic LF-to-current-game:
- 3-column;
- 4-column;
- 5-column;
solve/replay/export/load-check flows against the now-current game contract.

This is validation work, not permission for Codex to edit Scrubbots source.

**Disposition: REQUIRED CLOSURE.**

## Non-blocking positives retained

### ZIP locked parameters — PASS

Current source independently confirms:
- `candidates=300`;
- `screen_budget=3000`;
- `viability_budget=3000`;
- candidate mutation loop screens original + at most three mutations;
- mean-batch seed table remains unchanged;
- no task change to SupplyScorer weights.

Do not retune these in remediation.

### ZIP acceptance authority — PASS

No mandatory ProductionGameplayHost gate was added.

The approved authority remains:
- ScreeningSimulator = ranking only;
- real `SolvabilitySolver.solve`;
- real `SolvabilitySolver.replay`;
- ZIP `SolutionVerifier`;
- official Difficulty V1.

### Column support — PASS on LF side

The Level Factory product contract now explicitly supports:
- 3;
- 4;
- 5 columns;
with default 3 and preview depth 3.

Game-side compatibility is separately PASS/CLOSED.

## Final disposition

`MAINT-ZIP-CORE-V02-C001 = CHANGES_REQUIRED`

The ZIP-derived backend stays.

R01 must fix only the remaining Level Factory product-shell/cutover defects:
1. remove requested difficulty from active artwork generation;
2. wire real Solve/Analyze capability to ZIP;
3. wire background intent;
4. implement actual configured-game auto-publish after ACCEPT;
5. bind progression placement to the current game progression/catalog authority;
6. require shipping load-check before publish;
7. remove/decommission the competing legacy production solver/difficulty path;
8. make full tests green;
9. re-run live 3/4/5 cross-repo validation against the now-passing game contract.
