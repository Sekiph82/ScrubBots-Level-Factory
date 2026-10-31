# SB-LFX OWNER GOAL | AUTONOMOUS OPEN-BACKLOG EXECUTION | 2026-10-31

Document role: LATEST OWNER AUTHORIZATION TO AUTO-SELECT NEXT ELIGIBLE TASK FROM THE EXISTING ROOT TASKS.md BACKLOG.

This is NOT a replacement or rewrite of the owner's Codex goal-objective. The owner's original Goal text and already accepted visual decisions stay unchanged. The owner explicitly now says: Codex reads TASKS.md, selects the next work itself, updates TASKS.md after each task, closes genuinely finished tasks, and immediately proceeds to another existing task. The owner wants all **artificial administrative BLOCKED/STOP gates** removed so the agent does not stop after one stage or ask ChatGPT to pick tasks.

## SCOPE AND INSTRUCTION PRECEDENCE

- Repo: https://github.com/Sekiph82/ScrubBots-Level-Factory; main ONLY.
- Canonical local folder ONLY: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Game repo `Sekiph82/Scrubbots` is READ-ONLY unless a separately expressly authorized game modification exists.
- Root `TASKS.md` remains the SINGLE live task ledger; **this document is a stable scope/selection contract, not a second tracker**. Use the same exact URL of THIS prompt in both `Current Task` and `Next Task/Action` on every transition, `Required Actor: CODEX`. Do NOT change the queue guard; it intentionally checks clean checkout, canonical root, GitHub main and matching task-prompt URL.
- Root TASKS.md contains **73 unchecked `- [ ]` requirements as of initial inspection**, including owner-facing Studio, Level Factory, provider/content and game-runtime tasks. **There is an actual backlog. The prior text "No preauthorized safe stage remains" was false as a GLOBAL description of project work**. Earlier A–E subtasks are done, but the owner has now explicitly expanded Codex's selection authority to *already recorded* TODO/PARTIAL requirements tied to the standing Goal. Do not invent new feature requests, auto-generate novel milestone IDs, or turn historical diary entries into new tasks.
- SUPERSEDES previous artificial gates: Codex does not wait for ChatGPT audit, a new GPT prompt, a manually assigned next phase or an owner reply if the next existing task is independently safe and in the owner's Goal. The owner did not authorize bypass of actual permissions or safety checks.

## REAL BLOCKERS VS ADMINISTRATIVE STOP SIGNS

**Remove workflow-level BLOCKED/STOP** from the active Goal/current/next tracker fields. Use `IN_PROGRESS`, `BUILDER_VERIFIED`, `NOT_RUN`, `EXTERNAL_PERMISSION_REQUIRED`, `SOURCE_EVIDENCE_MISSING` or `DEPENDENCY_PENDING` *on the particular subtask* to describe reality.

**Do not erase/hide historical BLOCKED incidents, prior tests, previous rejection evidence or source-level failures.** Do not turn a real external permission into a PASS. Distinguish:
1. Administrative scheduling block: **REMOVED**. Pick another eligible existing backlog row and continue.
2. External permission (paid PixelLab/ALPIX remote operation, R2 PUT/DELETE/Promotion, Production deployment/activation, CI/Actions, explicit owner data change, unauthorized live GUI): **STILL REQUIRED**. Record exact missing authorization and never perform that operation automatically.
3. Source/test error (including the 2 failing 002 restoration fixture tests): diagnose and repair within a scope already allowed by the owner; do not call entire Goal BLOCKED.
4. Tool-policy denial on removal of 8 test fixture folders: never bypass, change file deletion technique to evade enforcement, wipe owner data or loop retries; record `CLEANUP_POLICY_DENIED_NONBLOCKING`, keep owner untracked items untouched, prevent new scratch, proceed to other permitted tasks.

## AUTONOMOUS NEXT-TASK SELECTION (NO NEW CHATGPT HANDOFF)

At beginning of every stage:
- `git fetch --prune origin`, verify origin/main, canonical checkout, no unsafe dirty changes. FF-only if safe; do not reset, rebase, clean, auto-stash, force-push or create worktree, clone, TEMP copied repo or unrelated folder. Validate current queue guard.
- Read existing `TASKS.md` actual checkbox sections, TAGS, Current Task Status, current source, tests, connected contracts and builder evidence. Enumerate remaining `[ ]` and `[~]` rows and the explicitly owner-goal unresolved checks.
- Exclude a candidate task only for a SPECIFIC reason: truly implemented elsewhere (first verify and close accurately), out of scope (e.g. game repo write, unrelated visual redesign), design gate awaiting semantics, external authorization, destructive side effect, forbidden CI or duplicate historical work. An item remains PENDING/EXTERNAL if excluded; it does NOT make the entire Goal blocked.
- Prioritize: a) current published source defects and failing focused tests, b) Factory Studio/Level Factory/Release Pool functionality in the owner's Goal, c) secure offline Staging/Production preflight, verification and release packaging/manifest parity, d) provider/credential integration that is zero-spend, e) existing other `[ ]` Level Factory/Content Platform offline, non-destructive requirements that directly support the Goal. In ties, choose the earliest existing requirement ID with all dependencies verifiably met. Prefer an executable artifact/test over a report-only task.
- Record the ACTUAL selected existing task ID and why it is safe, plus exact checks and intended files in the single `Current Task` and `Current Task Status`. Normal push and verify TASKS.md before implementing selected task if changing the active identity.
- Finish real work, never simply re-run an already passing suite to fill time. Test changed behavior, commit precisely, publish source and append-only builder log, fetch and verify main/Desktop HEAD equality, 0 ahead/behind, tracked clean. Then update TASKS.md with the exact task ID, evidence SHA, builder-tested state, known limitations and **next eligible existing task**. Commit/push the tracker separately, refetch and re-verify. Re-run queue guard and immediately work on the next task. **No mandatory ChatGPT audit**.
- The completion flag `[x]` is allowed only with genuine requirement-specific proof. Do not claim independent audit or real provider/gaming/Production success when not run. Preserve original 224/250 denominator historical stats unless specifically and demonstrably recomputed; do not fabricate percentages. A requested external independent audit is optional unless an already owner-locked **production safety gate** explicitly requires independent acceptance for the risky action itself. You may work on safe independent tasks meanwhile.
- If exact runtime session reaches a real model/tool/context budget limit, cannot keep executing automatically: record state honestly; NO background recursion, no scheduled polling or tool-policy bypass. Owner Goal remains open.

## IMMEDIATE REAL WORK (NOT ANOTHER 081 REPORT)

`SB-STUDIO-REAL-PLAY-GATE-081` has been coded and published (main reported at start `5a40eb0b6b5d557cea0a390d790b45580a0e0dbc`; fetch current). The gate requires exact `SOLVED + replay WIN + WON_ROBUST` from authenticated current game. Focused suite **49 passed**; wider suite **52 passed / 2 failed** because existing 002 restore fixtures do not yield expected READY/ACCEPT; actual native game replay for the new gate was NOT run; previously observed a crab `LOST` at click27. The managed installed Studio Release is NOT yet updated for 081.

**First eligible safe stage:** investigate those two failures and source/fixture/provenance compatibility. The existing 002 RESTORE fixtures and owner original art must be preserved byte-for-byte. If tests rely on stale fixture assumptions, repair TEST CODE or expected status with authentic source evidence, not by forging READY/ACCEPT or weakening `WON_ROBUST`. If genuinely new owner acceptance/production candidate is needed, mark that specific test `NOT_RUN / EXTERNAL` rather than falsify. Run affected local tests only; run safe local/read-only native CLI where actually permitted and non-destructive; no requirement to open owner live GUI. Work may include a narrow safe Studio installer preflight in read-only mode; applying Release requires explicit already existing scope and writer-exclusion proof, never assume approval.

**Next examples from already existing unchecked tasks (not new tasks):**
- `SB-LFX-018`: genuine remaining implementation/verification of three-screen owner workflow, 5 FIFO slots, accurate Level Factory and Release Pool filters/ready data, under approved exact visual masters. 38px owner design ALREADY ACCEPTED; do not reopen it.
- `SB-CPX-004`: offline source implementation of one-action `Publish to ScrubBots` handoff, with dry-run/preflight only, canonical pack and exact current-game evidence; NO real publish without separate permissions.
- `SB-CP07-003`, `SB-CP07-004`, `SB-CP07-005`, `SB-CP07-007`, `SB-CP07-008`, `SB-CP07-010`: provider separation, immutable naming, least-leaky interfaces, offline security/CDN/backup plans. Real remote PUT/DELETE remains consent-gated.
- `SB-CP08-001`, `SB-CP08-002`, `SB-CP08-003`, `SB-CP08-004`, `SB-CP08-005`, `SB-CP08-006`, `SB-CP08-008`, `SB-CP08-009`, `SB-CP08-010`: builder operation reports, dry-run, records, safe alerts and secret-free logs, no remote writes.
- `SB-CP09-003`, `SB-CP09-004`, `SB-CP09-005`, `SB-CP09-007`, `SB-CP09-008`: declarative-only security, HTTPS-only, no secrets in app, authenticated artifact design without unauthorized deployment.
- `SB-LF02-002/003/009/010`: only after game-mechanics/design semantics exist; otherwise leave as specific DESIGN_PENDING, do not invent reverse construction or slot stack mechanics.
- `SB-CP04/05` marked `[GAME_RUNTIME]`: verify exact current GAME main source read-only; do NOT write into game checkout from Factory Goal without explicit game repo authorization. Do not falsely count these as absent if their current game repo already implemented them; record verified cross-repo evidence for future closure without claim of native proof if unrun.

These examples are an **owner-approved selection domain from existing TASKS**, not a directive to edit all rows or spend owner resources. If one is already genuinely complete, close that row on evidence and choose the next. If a task has a real risk boundary, implement its safe offline substeps, then advance to another eligible safe task, leaving risky action for later approval.

## DATA, EXECUTION AND FINISH

- Preserve original 140 PNG (102 READY/4 FAILED/34 REJECTED), release pool entries, owner source PNG, game source, historical 002 fixture bytes, 18 stashes, existing Release receipts and all unrelated untracked data.
- Keep `SOLVED + replay WIN + WON_ROBUST` as required for new production READY, no bypass or faker replay. No false level IDs, adjusted difficulty or fabricated supply.
- `C:\Users\sekip\.codex\attachments` houses session-managed Goal copies, NOT project artifacts. Never intentionally write durable source/evidence outside the canonical Desktop/GitHub. Don't delete session-managed artifacts. Use bounded project-owned test data and obey tool safety policy; no stealth alternate deletes for cleanup denial.
- No CI/Actions; no charged ALPIX/PixelLab calls without explicit approved budget; no Cloudflare R2 external writes/Production promotion without separately approved exact target and scope; no unauthorized live laptop GUI automation; no new clones/worktrees/TEMP test repos; no branch besides main, no owner-data deletion/overwrite.
- Safety-gated native tests: source-only/headless/non-GUI verification may run if existing game project scope and OS side effects are expressly permitted; otherwise use source contract review, mark native proof NOT_RUN, continue independent tasks.
- Project Goal is complete ONLY when all actual criteria proven. If there are no other independently safe existing tasks left, report genuine external approvals needed; don't invent busywork or make a contradictory claim of perpetual background execution.
- After every meaningful task, normal code/tests -> builder log -> GitHub commit/push+refetch+exact Desktop parity -> TASKS.md advance+push+refetch+exact parity -> next read/queue guard -> next existing safe task.

**This latest owner's direction removes the false "A–E finished therefore everything is blocked" scheduling gate. It does NOT remove real permission requirements or falsify past blockers.**
