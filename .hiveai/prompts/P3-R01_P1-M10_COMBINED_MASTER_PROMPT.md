# P3-R01 + P1-M10 — Concurrent Remediation and CampaignBuilder

Document role: CODEX COMBINED MASTER IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

## Mandatory local ↔ GitHub main synchronization preflight

Before ANY implementation/test edits:

1. Work only in:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity:
   `Sekiph82/ScrubBots-Level-Factory`
3. Verify branch:
   `main`
4. Run `git fetch origin --prune`.
5. Inspect local HEAD, `origin/main`, status, ahead/behind, stashes and worktrees.
6. If clean and only behind, fast-forward with `git merge --ff-only origin/main`.
7. Preserve legitimate owner/local material non-destructively.
8. Never reset, rebase, stash, clean, force checkout, force push, or discard owner work.
9. Do not create a sibling Desktop clone/worktree/copy.
10. If safe reconciliation is impossible, stop before implementation.

## TWO CO-CURRENT WORKSTREAMS

Execute BOTH workstreams in this one builder cycle.

Neither workstream is paused behind the other.
Interleave implementation/tests where safe.

Do not rewrite either authoritative prompt.

---

# WORKSTREAM A — P3-R01 remediation

Execute exactly:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_PROMPT.md

Audit criteria:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CRITERIA.md

Parent strict audit:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/P3_HEADLESS_BATCH_PIPELINE_STRICT_AUDIT.md

Required builder log:

`.hiveai/codex-logs/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CODEX_LOG.md`

Preserve the original P3 product behavior.

---

# WORKSTREAM B — P1 M10 CampaignBuilder

Execute exactly:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md

P1 exact SHA-256:

`09de3ed5f15edf47a56f0135299467abacda2560c1381ec9ec888ef2fbc0afe1`

Audit criteria:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/P1_M10_CAMPAIGN_BUILDER_AUDIT_CRITERIA.md

Owner decision:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md

Required builder log:

`.hiveai/codex-logs/P1_M10_CAMPAIGN_BUILDER_CODEX_LOG.md`

Tracker IDs covered:
- SB-LF10-001
- SB-LF10-002
- SB-LF10-003
- SB-LF10-004
- SB-LF10-005
- SB-LF10-006
- SB-LF10-007
- SB-LF10-008

## Owner publication decision is already recorded

Do not restore the old behavior:
`owner ACCEPT -> immediate publish`.

Current owner rule:
- owner ACCEPT -> Release Pool;
- CampaignBuilder builds deterministic batch plan;
- owner APPROVE plan;
- approved contiguous batch publishes in one transaction.

P3 remains Review Queue only and never ACCEPTs or publishes.

---

# SCRUBBOTS GAME AUTHORITY — READ ONLY

P1 requires current game rules.

You are explicitly authorized to read the canonical local game checkout if present:

`C:\Users\sekip\Desktop\Scrubbots`

Repository authority:
`Sekiph82/Scrubbots`

Read-only scope includes the exact P1-required files:
- `docs/10_LEVEL_FACTORY_GENERATION_SCORING_ARCHITECTURE.md`
- `docs/09_DIFFICULTY_PROGRESSION_RETENTION_SYSTEM.md`
- `data/config/level_progression_v1.json`
- `data/levels/catalog/production_catalog_v1.json`
- `scripts/data/level_catalog.gd`
- any directly referenced current game validation/config code needed to consume those rules truthfully.

Do NOT modify Scrubbots.
Do NOT commit/push Scrubbots.
Do NOT create a Scrubbots branch/worktree.

If the canonical local game checkout is unavailable, use GitHub read-only authority if available.
Do not invent game rules.

---

# P2 BOUNDARY

P1 references separate prompt P2 for Route A branch/PR/store-update distribution.

No P2 authoritative prompt is currently present in Level Factory.

Therefore:
- do not invent P2;
- implement every P1 requirement that is self-contained in P1, including Release Pool, CampaignBuilder, Studio Release view, APPROVE boundary, and all-or-nothing batch publication transaction;
- if actual Route A branch/PR/store-update automation requires P2 details, report that exact portion as PENDING_P2 with evidence, as permitted by P1's report-back requirement.

---

# CROSS-WORKSTREAM INTEGRATION RULE

P3-R01 and P1-M10 must coexist.

Required final behavior:

```
P3 headless imported-art batch
    -> canonical Review Queue
    -> STOP

Owner reviews READY level
    -> ACCEPT
    -> Release Pool
    -> NO immediate publication

CampaignBuilder
    -> reads Release Pool + current game authority
    -> deterministic campaign_plan.json
    -> owner APPROVE
    -> contiguous batch transaction
```

Do not let CampaignBuilder auto-approve P3 output.

Do not let P3 bypass owner Review Queue.

Do not let owner ACCEPT bypass Release Pool.

---

# SHARED REGRESSION / GOVERNANCE

Root `TASKS.md` is ChatGPT-owned.
Do not edit it.

Do not edit:
- `.hiveai/audits/**`
- original P3 prompt
- P3-R01 prompt
- P1 prompt
- prior logs.

The P3-R01 governance fix must remain generic for transient current tasks and must not alter the 224 canonical task denominator.

P1 implementation must use the existing SB-LF10-001..008 tracker rows; Codex does not mark them complete.

---

# REQUIRED FINAL VALIDATION

Run all validation required by BOTH authoritative prompts and BOTH audit criteria.

At minimum:

## P3-R01
- true RUNNING-stage interruption coverage for every canonical P3 stage;
- ZIP pre-record and post-record interruption windows;
- P3 parity;
- P3 idempotency;
- P3 rejection truth;
- SB-LFX-005/SB-LFX-015 relevant regressions;
- generic transient-task governance regression.

## P1-M10
- global assignment optimality vs brute force;
- no assignment beyond current ± hard tolerance;
- tolerance tiers;
- every current recovery guard;
- profile-run constraints;
- novelty/similarity constraints;
- deterministic swaps/reassignment;
- first-hole contiguous stop;
- shortage report;
- deterministic plan hash;
- rebuild without regeneration;
- Release Pool ACCEPT behavior;
- owner lock/swap revalidation;
- APPROVE all-or-nothing batch transaction;
- injected-failure rollback;
- existing catalog entries unchanged;
- current game LevelCatalog accepts published temp fixture;
- K=100 synthetic example plan/report.

## Shared
- full pytest green except truthful capability skips;
- compileall PASS;
- Factory Studio Godot headless/runtime PASS;
- git diff --check PASS;
- offline invariant preserved;
- no new dependency unless explicitly required by P1 (P1 says numpy only / no new dependency);
- no live owner game-repo mutation during tests.

Use isolated temporary fixtures for publication tests.

---

# COMMIT / LOG DISCIPLINE

Create BOTH matching builder logs before their respective product/test edits:

1. `.hiveai/codex-logs/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CODEX_LOG.md`
2. `.hiveai/codex-logs/P1_M10_CAMPAIGN_BUILDER_CODEX_LOG.md`

Record chronology truthfully in each workstream log.

You may use separate implementation commits by workstream.
If a file legitimately serves both workstreams, record that overlap explicitly in both logs.

Do not squash away failed-test history from logs.

Push Level Factory `main` normally.

After final push:
- fetch origin;
- prove local HEAD == origin/main;
- prove ahead/behind 0/0;
- preserve untracked owner material.

STOP for independent ChatGPT audits of BOTH workstreams.

## Final response

Return only these two URLs:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P3-R01_HEADLESS_BATCH_PIPELINE_AUDIT_CLOSURE_CODEX_LOG.md

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P1_M10_CAMPAIGN_BUILDER_CODEX_LOG.md
