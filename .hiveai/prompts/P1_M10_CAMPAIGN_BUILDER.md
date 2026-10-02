# PROMPT P1 — M10 CampaignBuilder: batch campaign sequencing for accepted levels

Repository: `Sekiph82/ScrubBots-Level-Factory` (Level Factory). Game authority: `Sekiph82/Scrubbots`.
Tracker IDs: SB-LF10-001 … SB-LF10-008 (M10 — Campaign Intelligence / Sequencing Adapter).

## 0. Owner decision update (record it before implementation)

Owner decision 2026-10-02 (supersedes "owner ACCEPT auto-publishes" in the current TASKS
product-change list):
- Owner **ACCEPT** moves a READY level into the **Release Pool**. It no longer publishes
  immediately and no longer picks its own catalog order.
- Publication happens per **release batch** (default K = 100, configurable): CampaignBuilder
  orders the pool into the next contiguous catalog numbers `N+1 … N+K`, the owner approves the
  plan, then the whole batch is published in one transaction.
- Distribution route now: Route A (game repo branch + PR, store update) — see prompt P2.
  Route B (.scrubpack / CDN, M11–M20) continues later through the normal process.

Follow GOVERNANCE.md / AGENTS.md / CLAUDE.md (ChatGPT owns TASKS.md, Codex builds, independent
audit). Read before coding: `docs/10_LEVEL_FACTORY_GENERATION_SCORING_ARCHITECTURE.md`
(game repo; §13 profile diversity, §14 novelty signature, §15 CampaignBuilder, §16 pool
strategy), `docs/09_DIFFICULTY_PROGRESSION_RETENTION_SYSTEM.md`,
`data/config/level_progression_v1.json`, `data/levels/catalog/production_catalog_v1.json`,
`scripts/data/level_catalog.gd`, and in this repo
`src/scrubbots_pixel_factory/supply_pipeline/{progression.py,game_publisher.py}`.

## 1. Problem with the current code (evidence)

`game_publisher.publish_level` places ONE level at the FIRST order >= next free order whose
cadence target is within ±`neverForceLabelOutsidePlusMinus` (5.0) of its score. Consequences:
greedy first-fit, possible holes in the catalog order sequence, no batch optimality, no recovery
guards, no novelty/similarity/profile-diversity checks, tolerance ladder ignored.

## 2. Rules to consume (never re-type; read from the game config at run time)

- cadence (10 slots, class/modifier/role/noveltyTarget), `progression.tauCycles`,
  lanes (base/growth): `TargetChallenge(n) = clamp(base + growth*(1-exp(-k/tau)) + modifier)`,
  `slot = ((n-1) mod 10)+1`, `k = floor((n-1)/10)` (reuse `progression.describe_target`);
- `challengeTolerance`: preferredWhenPoolIsLarge 2.0, defaultPlusMinus 3.5,
  neverForceLabelOutsidePlusMinus 5.0 (never place a level outside ±5.0 — leave the slot empty);
- `recoveryGuards`: slot3->4 drop >= 15, slot5->6 drop >= 20, slot8->9 drop >= 15,
  slot10 -> next cycle slot1 drop >= 35 (on ACTUAL official challenge scores);
- docs §13: no same dominant profile more than 2 consecutive; avoid repeated high-W; no high-B /
  high-F back-to-back; recovery levels low B/U; rotate profiles;
- docs §14: novelty signature (palette set/histogram, dimensions/aspect bucket, challenge vector,
  dominant profile, silhouette/perceptual hash, unlock-wave histogram, slot-pressure bucket…);
  multi-field similarity; consecutive similarity must stay below a configured maximum;
- production envelope 20..59, 3..12 colours (already enforced upstream; re-check, never trust).

## 3. Algorithm (deterministic)

Inputs: catalog (existing N entries + their metadata challengeScore when present), progression
authority, Release Pool (each: candidate/level id, official D, vector [W,C,A,U,B,R,S], profile,
signature, session load, files + digests), K.

1. Slots n = N+1 … N+K with class, target T(n), noveltyTarget.
2. Eligibility: a candidate i is eligible for slot n only if |D_i − T(n)| <= 5.0 and its class
   label (from D) is consistent with the slot class. Cost c(i,n) = |D_i − T(n)| with tier
   penalties: <= 2.0 tier 0, <= 3.5 tier 1, <= 5.0 tier 2 (large penalty).
3. Global assignment: minimum-cost assignment over the eligible bipartite graph (Hungarian /
   min-cost flow; numpy only, no new dependency), ties broken by stable id order. Unassignable
   slots stay EMPTY.
4. Sequential repair: check recovery guards, profile/similarity rules along n; repair by
   deterministic swaps between slots of the same class (and re-assignment from unused pool
   candidates) minimizing assignment cost + constraint penalties; never break the ±5.0 bound.
5. Contiguity: the published batch must be exactly N+1 … N+M with no hole. If slot N+j cannot be
   filled, the batch stops at N+j−1 (M < K) and the rest is reported as a shortage.
6. Shortage report (SB-LF10 "request more generation"): per empty slot: n, class, target,
   allowed range, nearest unused candidates and why they failed. This report is the input for
   generation (new art, or new supply variants of existing accepted art re-planned toward the
   needed class — that is generation, not CampaignBuilder; CampaignBuilder never modifies data).
7. Output `campaign_plan.json` (schema `scrubbots-campaign-plan/v1`): input digests (catalog,
   authority, pool ids+digests), K, per slot {n, slot, class, role, target, chosen id, D, delta,
   tier, guard/similarity/profile checks}, shortages, deterministic plan hash. Rebuilding with the
   same inputs gives the identical plan (SB-LF10-005/006).

## 4. Studio + publication

- Studio "Release" view: pool size vs K, the plan table (target vs D curve, tiers, warnings),
  owner lock/swap of a slot (re-validated), APPROVE.
- On APPROVE: batch publication = ONE transaction for all M levels (extend `publish_level` with
  an explicit `level_number` per item + all-or-nothing staging/rollback). Catalog orders must be
  contiguous; existing entries are never modified (SB-LF10-003).
- Remove the greedy first-fit path from ACCEPT (it only enters the pool now).

## 5. Tests

Assignment optimality vs brute force on small pools; never outside ±5.0; contiguity/stop at first
hole; each recovery guard; profile run limit; similarity limit; shortage report content;
determinism (same inputs → same plan hash); rebuild without regenerating levels; batch publish
rollback on injected failure; catalog loads through the game's LevelCatalog after publish.

## 6. Report back

Changed files, algorithm summary, test results, an example plan for K=100 on a synthetic pool,
and any rule you could not apply (with evidence).
