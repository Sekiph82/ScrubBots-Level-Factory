# SB-CPX-001-C001 — Solver-Proven Supply Identity Pack Binding

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CPX-001 / SB-CPX-001-C001` or M12 master authority `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CPX-001-C001` if needed. M12 master mode reuses the single master worktree.
6. No Desktop sibling clone/worktree.
7. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Close the owner-approved M12 extension:

Bind every explicit packaged `scrubbots.level_supply_plan.v1` to the exact initial supply state that received the canonical current Factory solver PASS.

## Production authority rule

Do not use `src/scrubbots_pixel_factory/solver_evidence.py` as production authority; it is explicitly `LEGACY_NON_PRODUCTION`.

Inspect and reuse the current canonical READY/Release Pool/supply pipeline evidence already accepted by current Factory flows.

If the current canonical pipeline lacks one required digest field, derive/add that digest at the narrow canonical evidence boundary without re-running or duplicating a separate solver implementation.

## Required binding per level

Pack manifest/evidence must bind at minimum:
- exact LevelData ID and LevelData SHA-256;
- exact supply-plan SHA-256;
- exact FIFO columns, batch IDs, CIDs and robot counts or a canonical digest that commits to those exact values;
- columnCount;
- visiblePreviewDepth;
- maxRobotsPerBatch where present;
- canonical initial solver-state digest;
- canonical solver-evidence/result digest identifying the PASS/SOLVED evidence;
- source READY/pipeline/release-pool authority identity.

The packaged supply-plan bytes must be the exact bytes whose digest is bound.

Missing, stale, mutated, cross-level or cross-pipeline identity must fail closed before final pack emission.

## Current authority and regression

Use real current canonical Factory evidence in focused integration tests. Synthetic fixtures may supplement but cannot be the sole proof.

Prove:
- valid exact identity packages successfully;
- one robot count change fails;
- batch reorder fails;
- CID change fails;
- level mismatch fails;
- supply-plan byte mutation fails;
- solver-state digest mismatch fails;
- solver-evidence digest mismatch fails;
- stale READY/review/pipeline identity fails.

Do not perform M14 current-game promotion replay here. SB-CPX-002 owns that future gate.

## Verification and publication

Run focused tests, all prior M12 child regressions, M11 regressions, governance, full pytest, compileall, and `git diff --check`.

Create/update builder log:
`.hiveai/codex-logs/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

If green:
- commit implementation;
- commit child log separately;
- fetch/prune;
- normal non-force push to `main`;
- verify 0/0 parity.

Standalone mode: stop for ChatGPT audit.
M12 master mode: continue immediately to `M12 MASTER COMPLETE` without human handoff.