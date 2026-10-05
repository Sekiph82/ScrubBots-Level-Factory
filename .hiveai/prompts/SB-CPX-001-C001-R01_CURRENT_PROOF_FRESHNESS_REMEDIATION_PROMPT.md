# SB-CPX-001-C001-R01 — Current Proof Freshness Remediation

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent strict audit:
`.hiveai/audits/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_STRICT_AUDIT.md`

M12 master audit:
`.hiveai/audits/M12_CP01_001_010_CPX001_MASTER_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/SB-CPX-001-C001-R01_CURRENT_PROOF_FRESHNESS_AUDIT_CRITERIA.md`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity, branch, origin, HEAD, dirty tracked/untracked state, stashes, and registered worktrees.
3. Run `git fetch --prune origin`.
4. Read current `origin/main:TASKS.md`; require `SB-CPX-001-C001-R01` and this exact prompt.
5. Preserve every byte of legitimate owner-local work. Do not reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
6. If persistent checkout cannot be safely synchronized, leave it untouched and create/reuse only:
   `%TEMP%\ScrubBots-Level-Factory\SB-CPX-001-C001-R01`
   from exact latest `origin/main`.
7. No Desktop sibling clone/worktree.
8. Require execution worktree clean and 0/0 with `origin/main`.
9. Stop if identity/preservation/remote overlap is ambiguous.

## Scope

Close only CPX-001 audit finding F01.

SB-CP01-001..010 are already PASS/CLOSED and must not be redesigned.

The existing cryptographic solver-supply binding is accepted. The defect is only freshness of owner/review/READY/Release Pool authority between proof resolution and final pack emission.

## R01.1 — eliminate stale-proof pack emission

Current bug pattern:

1. current owner review is ACCEPT;
2. proof is resolved;
3. owner review/pipeline state changes;
4. old proof object remains in memory;
5. low-level build can still emit a pack from the stale proof.

Fix the **production solver-proven build path** so it revalidates current Factory authority immediately before final emission.

### Accepted-READY fallback

At build time require exact current:
- candidate exists;
- latest owner review is ACCEPT;
- latest review ID exactly equals proof review ID;
- latest READY pipeline run ID exactly equals proof pipeline run ID;
- current pipeline bytes and SHA-256 equal the proof;
- current exact LevelData and supply-plan source bytes equal the proof-bound bytes.

A prior ACCEPT that is no longer current is not authorization.

### Release Pool source

At build time require:
- entry still appears in current `release_entries()`;
- exact entry digest matches;
- exact pipeline run ID/digest matches;
- exact current pipeline bytes match;
- exact current LevelData/supply bindings match.

A previously valid Release Pool snapshot that is no longer in the current pool projection is stale.

## R01.2 — preserve dependency direction

Do NOT import Factory private implementation into `content_pipeline/src/scrubbots_content_pipeline/**`.

Use a narrow explicit authority seam, for example:
- a factory-side current-authority orchestration function;
- a protocol/callback injected into the final production build;
- another dependency-inverted mechanism.

Exact design is implementation-defined.

Hard rule:
the function/API documented and used as the **production current-authority solver-proven pack build** must perform the freshness check at final emission.

A pure low-level cryptographic verification helper may remain, but it must not be presented as sufficient current authorization.

## R01.3 — race tests

Add real current Factory integration coverage:

### Race A
- owner ACCEPT;
- resolve proof;
- owner REJECT;
- call final production pack build with old proof/context;
- must fail;
- no archive/success evidence returned.

### Race B
- owner ACCEPT A;
- resolve proof;
- owner creates newer ACCEPT B with a different review ID;
- old proof build must fail.

### Race C
- resolve proof for READY run A;
- current READY authority advances/changes to run B;
- old proof build must fail.

### Race D
When Release Pool path can be constructed in focused fixtures:
- resolve current pool proof;
- remove/revoke it from current pool projection through normal authority semantics;
- old proof build must fail.

If the real current Release Pool admission gate cannot produce a truthful pool entry for the integration candidate, cover Release Pool freshness through a focused current-authority fixture without fabricating solver PASS/profile truth, and document the limitation.

### Control
Unchanged current ACCEPT/READY proof must still build and verify successfully.

## R01.4 — do not weaken accepted identity checks

Retain exact:
- LevelData ID/bytes/SHA;
- supply bytes/SHA;
- FIFO columns/order;
- batch IDs/CIDs/robot counts;
- columnCount/preview/max batch;
- solver-state digest;
- solver-evidence digest;
- SOLVED/WIN/replay zero-active;
- conservation;
- load check;
- Scrubbots authority;
- Release Pool digest;
- detached artifact digest.

`src/scrubbots_pixel_factory/solver_evidence.py` remains LEGACY_NON_PRODUCTION.

SB-CPX-002 current-main replay remains M14 scope.

## Required verification

Run:

1. R01 stale-proof race tests.
2. Original CPX-001 integration.
3. all M12 CP01 focused tests.
4. M11/CP00 regressions.
5. governance/tracker tests.
6. final cumulative M11+M12+CPX command.
7. full `python -m pytest -q`.
8. compileall.
9. schema parse.
10. `git diff --check`.

## Builder log

Create before product edits:

`.hiveai/codex-logs/SB-CPX-001-C001-R01_CURRENT_PROOF_FRESHNESS_CODEX_LOG.md`

Record:
- sync disposition;
- selected dependency-inversion design;
- exact production entry point that performs current-authority check;
- race A/B/C/D outcomes;
- focused/cumulative/full test results;
- implementation commit;
- separate log commit;
- final main parity.

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.
Do not rewrite prior M12 child/master logs.

## Publication

Only after all gates pass:
- commit remediation;
- commit builder log separately;
- fetch/prune;
- normal non-force update to main;
- fetch again;
- require execution HEAD == origin/main, 0/0 divergence, clean worktree;
- stop for ChatGPT independent R01 re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CPX-001-C001-R01_CURRENT_PROOF_FRESHNESS_CODEX_LOG.md
