# SB-LFX-018 R05 M03 | V09 Campaign Contiguity and Owner Authority | Independent Audit V10

Date: 2026-10-19 (Europe/Istanbul).
Auditor: ChatGPT. Scope: GitHub sources and exact builder log only; not owner Windows runtime or approval UI.
**Verdict: CAMPAIGN F01 READ-ONLY REQUIREMENTS AUDIT PASS; ACTUAL CAMPAIGN PLACEMENT OPEN / BLOCKED ON AUTHENTIC CONTENT + OWNER DECISION.** Retain genuine CPX001/STAGING/CPX002 and bounded GFF source-startup engineering PASS; no production promotion.

## Published source evidence and independent comparison

- F01 Codex last output: `Sekiph82/ScrubBots-Level-Factory/main` at `18538a34e483cc41ed09237f46ae903af828c02d`. Independently fetched remote main; compare from `42be98aa53d388c8eae5b4adde9080aef6f96178` showed **1 commit ahead**, **0 behind**, with only `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md` altered (11 added lines, 1 removed). Local owner `HEAD=origin/main` 0/0 is builder-reported, not independently observed on Windows.
- Builder V09 section `2026-10-19 22:35 +03:00` reports read-only inspection of actual game authority `9663c44c0b40dd08b082e4c5a54f808efb481704`, true catalog and progression configs, no candidate/catalog mutations or production work.
- GPT separately fetched game `data/levels/catalog/production_catalog_v1.json` (blob `7e5a0cd7d699751d2c5ec52b7c6b903e2b847105`) and `data/config/level_progression_v1.json` (blob `251733e9d30cec8ccd2754a5f6713078a332e872`), the owner-locked `docs/09_DIFFICULTY_PROGRESSION_RETENTION_SYSTEM.md` (blob `cf08af519f5025307f2e0a7932cb7aded8b56f25`) and `docs/10_LEVEL_FACTORY_GENERATION_SCORING_ARCHITECTURE.md` (blob `97af33f728376f920f78aab8c4d8cba792f3c42f`), plus LF `.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md` and locked M03 criteria.
- Catalog has **exactly orders 1 through 10**; last = `level_010_ice_cube`, next publish slot = **11**. The official ten-slot cycle is EASY, EASY, MEDIUM, EASY, HARD, EASY, EASY, MEDIUM, EASY, VERY_HARD. Official default score tolerance ±3.5, hard no-force-label bound ±5, preferred large-pool ±2, recovery drops 15/20/15/35 at specified cycle boundaries.

## Original owner 002 at Level 48: not an assignable campaign item today

- Existing immutable source evidence `tests/evidence/SB-LFX-018-R05-M03-V02/002-difficulty-placement.json`: owner 002 `MEDIUM`, solver-authorized score `48.8166775742989`, official Challenge Vector `W,C,A,U,B,R,S`, dominant profile COLOR, second ROUTE, authentic original 002 LevelData V2/4 FIFO stable SHA and official current-main solve/WIN.
- Formula Level48 = cycle4, slot8, MEDIUM, `second_tension`, target `44.3565002099862`. Numeric delta **+4.46017736431264**, **inside ±5 hard** but **outside ±3.5 default** (tier 2 / penalty). Numeric fit alone is not automatic accept or placement.
- No orders 11–47 exist in the actual published catalog, and no owner-approved complete contiguous plan, correct predecessor profile history, adjacent novelty/similarity hashes, authoritative profile/recovery checks, or pool identity for future batch were demonstrated. Missing catalog entries must not be interpreted as a solver defect or filled with fabricated placeholders. Owner 002 stays **OWNER_ACCEPT / MEDIUM / UNASSIGNED**.
- Level11 generated seed92 remains **EASY / READY_AUTO / NOT OWNER_ACCEPT / UNASSIGNED**. Do not auto-approve just to fill slot11.

## Authority and opportunity to progress without guessing

- P1 M10 CampaignBuilder prompt requires the batch to begin at **N+1** and stop at its **first unfillable hole**; it cannot jump straight to 48 or publish a gap, even if an individual candidate matches numerically. Plans/shortage reports are deterministic, must bind candidate digests and official progression rules. Owner review/APPROVE is a **separate gate** after genuine available READY/ACCEPT content is selected. Source `TASKS.md` already lists P1 M10 implementation/audit **PASS/CLOSED**; rebuilding CampaignBuilder itself would be redundant absent a defect.
- **Next non-mutating, actionable product step:** Ask Codex to use the *current actual installed Release Pool* and canonical CampaignBuilder to compute the **next contiguous batch dry-run starting order11** (default K=100 or the exact smaller bounded scope supported), treating stale/invalid current game candidates as ineligible. Record exact pool membership/digests and shortlist, missing earliest order(s), shortage reasons/class/target and recovery/profile/novelty gates available or absent. Put report in the **existing builder log only** or an approved evidence file without staging content, publishing campaign data, or mutating Release Pool/owner records. If tooling cannot run without creating unauthorized task TEMP, give a read-only inventory and explicit limitation. Do not re-run Godot, R2 staging, GFF, or attempt earlier proven engineering work.
- If pool cannot fill order11, the result should be `BLOCKED_CAMPAIGN_CONTENT_FIRST_HOLE_11` (or its actual first missing slot), **not** another request to fit 002 to Level48. The user may then approve an explicit generation/curation campaign for a contiguous 11+ prefix; without owner approval, keep actual publication blocked. No mass creation of 11–47 under this audit.
- Technical work not dependent on owner’s publishing 37 missing levels should continue under a separate ledger task **only upon scope confirmation**; do not force unrelated content-production work into the M03 native integration proof. If M03 milestone acceptance policy requires campaign placement/zero-residue, remain honest that full M03 stays CONDITIONAL/OPEN until those gates are satisfied, even though CPX001/STAGING/CPX002 are complete.

## Provenance/limits

- This is an independent **repository/source audit**; GPT did not observe current owner Release Pool or compute a live plan; no evidence exists yet for whether pool can fill slots11-47, or for actual owner campaign approval.
- Historical M03 strict audit criteria explicitly also require genuine zero task-owned external TEMP residue, in addition to authentic native single-candidate evidence. Prior task-only directories were reported absent by an owner-local Codex read-only check but their removal cause is unproven. No new cleanup was attempted in V09. Do not treat a previous blocked policy deletion as successful removal by Codex.
- No GitHub CI/Actions, PROD upload, staging overwrite, source image change or publication was performed by GPT.

## V10 labels

- `M03_F01_CANONICAL_CAMPAIGN_ORDER_1_TO_10_SOURCE_PASS`
- `M03_F01_LEVEL48_NUMERIC_MEDIUM_HARD_BOUND_ONLY_OUTSIDE_DEFAULT`
- `M03_F01_11_TO_47_CONTIGUOUS_CONTENT_AND_OWNER_PLAN_MISSING`
- `M03_F01_NEXT_ACTION_CANONICAL_CAMPAIGNBUILDER_REAL_POOL_DRY_RUN_ORDER_11`
- `OWNER002_OWNER_ACCEPT_MEDIUM_UNASSIGNED`
- `SEED92_READY_AUTO_NO_OWNER_ACCEPT_UNASSIGNED`
- `CPX001_STAGING_CPX002_ENGINEERING_PASS_RETAINED`
- `GFF_BOUNDED_MAIN_STARTUP_PASS_RETAINED`
- `M03_FULL_CONDITIONAL_OPEN_R05_PRODUCTION_OPEN`

**Decision:** V09 research accepted; next test is an actual *non-mutating* CampaignBuilder availability/shortage check using genuine pool state. No reason to run the same Level48 arithmetic or packaged replay again.
