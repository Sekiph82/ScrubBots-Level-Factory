# CLAUDE.md | ScrubBots Level Factory | Active Owner Delegation (2026-11-10)

**EXECUTOR: CLAUDE ONLY.** This document supersedes older Codex-only or ChatGPT-gated execution instructions for NEW work. Old prompts, audit decisions and builder logs are historical evidence; do not rewrite them.

**Active execution contract:**
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB_LFX_OWNER_CLAUDE_AUTONOMOUS_RECOVERY_PIXEL_ART_BATCH_MISMATCH_20261110.md

**Canonical task tracker:** root `TASKS.md`. There is no second task-management file.

**Factory repo:** `Sekiph82/ScrubBots-Level-Factory`, branch `main`, Windows root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.

**Installed program:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`. Open using the existing Desktop shortcut. Do not assume editing GitHub code updates this installed copy.

**Separate ScrubBots game:** `C:\Users\sekip\Desktop\Scrubbots`, `Sekiph82/Scrubbots`. Its 30 existing campaign levels and game assets are protected. Read current engine/game host for parity; modify game code only where a specific approved requirement needs it, not as general cleanup.

## First action: TASKS.md refresh

1. Verify source checkout, GitHub `origin/main`, installed Release version/manifest and existing owner work. Read `TASKS.md`, the new active execution contract, `AGENTS.md`, `GOVERNANCE.md`, the 3-screen visual masters and recent source/error logs.
2. Audit TASKS.md against actual current code, screenshots and installed runtime. Historical status text, immutable receipts and old authorizations are evidence, not license to mark work as completed. Correct LIVE current/next/status/actor, add testable P0 defects and dependency/order guidance, and prioritize the two owner-reported failures.
3. Select the next real open/partial existing task autonomously, work to actual verifiable acceptance, then record code/test/GUI evidence, publish normally and continue. Do NOT wait for Codex or ChatGPT and do not send the user repeated approval questions for permissions already granted. If a specific external permission is required, mark ONLY that operation and do another independent task.
4. Preserve the canonical 224/250 historical denominator, task IDs, archived prompt/log/audit text and truthful partial states. Do not mass-close tasks to make the ledger look finished.

## P0 1: PIXEL ART (must fix first)

The owner started a 176-row PixelLab Pro 4x4 batch. The first 224x224 atlas/16x56x56 sliced images appear to exist, yet the UI reports one failed and 175 remaining, `STOPPED_AFTER_FAILURE`, `SOURCES_IMPORTED_NOT_READY`, and `Provider returned no detailed reason`. Trace provider/job receipt, billing claim, response, gallery asset, atlas persistence, slicer, output provenance, status transition and batch resume cursor **in both current source and installed app**. Identify the precise reason and fix it, not only the display. Never resubmit an accepted/billed row or spend credits as a diagnostic. Continue previously queued, provably unbilled rows only within the owner's existing explicit queue/available account budget and with idempotent claims. Avoid repeated paid POSTs. Preserve exact Palette V3 checks and all 16 original individual PNG outputs, including transparency. Safe read/hash verification of Final and Grid Files is allowed; destructive changes are not.

## P0 2: LEVEL FACTORY (must fix second)

Live owner screenshots show `Batch mismatch` and a stale batch of 304 SOURCE_ONLY PNGs plus `Batch 180 Pending / 116 READY / 6 FAILED / 2 REJECTED`, unresolved owner-upload source paths and stale Release Pool projections following the old cleanup. Identify correct data root and installed version, eliminate invalid restoration/index mapping and wrong phantom batch references; do not fake READY or repopulate old Release Pool. Level Factory must accept new PNG inputs only from `data\output\Pixellab\Final`. The 30 protected game levels and recovered cold archive are not new active input sources. Run a real level through the current canonical game-host solver and exact 1/60 fresh-host replay and preserve all other non-FPS checks. No 30/120 FPS robustness tests.

## Real installed app and screenshots

The owner **explicitly authorizes repeated controlled Windows GUI launches, clicks, verification and screen captures** through the existing Desktop LNK. Test the PIXEL ART and LEVEL FACTORY pages in the genuine installed app. Determine source/Release parity and deploy a bounded verified update safely with real process/writer exclusion; no blanket installer replacement or owner-file deletion. Capture truthful before/after screenshots showing actual PixelLab batch status, produced 16 images, next safe row, clean LF launch/source gallery, usable pipeline/replay result and restart persistence. Images must come from real app, never invented screenshots. Store owner-local originals outside overwritten source/archival paths, and provide paths in Turkish report. If real desktop automation is not available to the executing Claude environment, mark `NOT_RUN_WITH_REASON` accurately; do not claim GUI PASS.

The owner will personally review RELEASE POOL **after** the other two pages work. Do not prioritize Release Pool visual changes or any R2/Production publication before that review. Keep existing valid Release Pool contracts and current emptied historical pool, without false READY.

## Source integrity, cleanup and cost boundaries

- November 7 cleanup lost 20 protected owner-upload source PNG/source.json pairs; 19 exact source PNG bytes were later recovered in a cold archive, one PNG exact hash and 20 source.json remain missing; eight old installed candidate folders had denied ACL reads. Preserve archives, both retained 30-level inventories, manifests, Godot import caches and inaccessible folders. Do not repeat the destructive cleanup.
- No generic recursive deletion; no Windows separator-based unsafe allowlists. Use resolved canonical paths, explicit allowlists, before/after hash manifests and rollback for any authorized narrow migration. Never bypass ACL/tool policy.
- No GitHub Actions, hosted paid CI, unapproved billable provider requests, secret exposure, force push or destructive Git reset/clean/stash.
- R2/STAGING/Production writes and new paid requests beyond the owner's already authorized queued batch still require their actual scope permissions; don't invent blanket consent. External gates block only that specific action, never unrelated safe coding.
- Keep the existing exact three owner production tabs: `PIXEL ART | LEVEL FACTORY | RELEASE POOL`; obey `docs/product/FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md` and visual-master index.

## Execution loop

1. Start with read-only queue validation: `python -B scripts/codex/scrubbots_task_queue.py --json --allow-existing-work`. Historical filename is retained only for compatibility; CLAUDE is now the required actor.
2. Inspect current files, diffs, tests and evidence; write a focused failing regression for each proven bug.
3. Implement and run targeted local tests, native Godot where truly executable, and real installed GUI checks. Review changes yourself and use separate Claude reviewer/subagents when supported, clearly distinguishing self-review from external independent audit.
4. Safely install the tested build in Release; verify launcher and real GUI before claiming success.
5. Update root TASKS.md for each task with accurate tests, source SHAs, dependencies, next existing task and permission-specific blockers. Write append-only Claude evidence in a new dedicated file under `.hiveai/claude-logs/` or `docs/evidence/`. Never edit historical Codex logs or independent audit files.
6. Commit scoped work, normal push to GitHub main, fetch, confirm local HEAD == origin/main and ahead/behind 0/0 before moving on. Preserve local untracked owner data; do not stage unknown files.
7. Finish P0 faults first, then continue the other genuinely eligible TASKS.md backlog without a Codex/ChatGPT handoff. Don't make claims about running after the actual current Claude session ends.

## Owner report

Provide the owner with an evidence-backed **Turkish** summary: precise root causes, actual solved failures, real app screenshots and local paths, test counts including failures, task ledger changes, permission-limited residuals, exact commit hashes and synchronized Desktop state. No fabricated GUI screenshots or generic `DONE` claims.

## Historical instructions

The repository contains older Codex/H!veAI governance documents, standing prompts and activity logs. Keep them readable as historical evidence. Their Codex-only required actor, ChatGPT tracker handoff, limited GUI authorization, ban on read-only inspection of PixelLab source PNGs, or stale instruction to prioritize legacy recovery over the owner's current two functional failures are superseded for this new work by the explicit 2026-11-10 owner handoff above. Other safety boundaries, genuine user data ownership, budget and production controls still apply.
