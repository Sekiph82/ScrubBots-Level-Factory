# M17-CP06-C001 MASTER | Rollback, Disable & Scheduling

Repository: `Sekiph82/ScrubBots-Level-Factory` ONLY.
Implementer: CODEX. Root `TASKS.md` lifecycle and independent audits: ChatGPT ONLY.
Matching strict criteria: `.hiveai/audit-criteria/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_AUDIT_CRITERIA.md`
Single builder log: `.hiveai/codex-logs/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_CODEX_LOG.md`
Scope: **ALL canonical M17 child requirements `SB-CP06-001..012`**, preserving `SB-CP06-004` and `SB-CP06-010` as external GAME_RUNTIME gates.

## 0. Execution authority / current owner report

Owner supplied the previous R04 local log summary: A READY / B structural rejection / C READY with distinct identities and contiguous CampaignBuilder Levels 11–12; 150 **real PNGs were imported with hashes** but only **2/150 reached official SOLVED/WIN/READY**, 148 pipelines NOT RUN; one new run-owned 384,233-byte scratch directory could not be cleaned due approval policy, and four earlier R03 roots also remain. N->N+1->N+2 real provider/history, full LF pytest, native Windows file chooser visual, installation and **independent R05 audit are still OPEN**; local builder log/source changes remain unpublished. Do not rewrite this as R05 PASS or pretend the published GitHub branch contains them.

**2026-10-10 GPT AUTHORIZATION SUPERSEDES THE QUEUE-ONLY STOP: M17 STAGE 1 IS AUTHORIZED NOW, IN PARALLEL WITH OPEN R05.** The previous stop `M17_QUEUED_WAITING_FOR_R05_AUDIT` caused two no-op Codex resumes. That stop is retired for **non-live, independent, bounded M17 engineering**; it is NOT permission to mark R05 PASS, install a Factory build, alter ScrubBots, publish to R2 production, or finalize M17. Consult updated LF root `TASKS.md` and proceed with Stage 1 even if R05 remains `R05_UNVERIFIED`.

**STAGE 1 / START NOW:** Use the existing clean `M17-CP06-C001` TEMP worktree. Implement and test LF-owned provider-neutral rollback/known-good/disable and scheduling/report modules for `SB-CP06-001..003,005..009,011..012`, reusing the current published CP03/CPX/M18 APIs and avoiding the local uncommitted R05 code entirely. Use tiny self-owned fixtures and focused deterministic/in-memory or stateful local provider checks. Do **not** start full multi-GB regression or write real R2 production. Log per child DONE/INCOMPLETE/BLOCKED with no fake PASS; record `SB-CP06-004/010` as external game-runtime contracts, NOT implemented here. If changes require direct edits to source files also modified in the uncommitted R05 worktree, stop **only those conflicting edits**, record exact paths and implement independent interfaces/tests elsewhere. Work through all independent children in one continuous cycle rather than returning the queue status.

**STAGE 1 HANDOFF:** Preserve implementation/tests and log in this M17 worktree, with clean intentional commits if possible. **Do not push M17 product changes to `main` while R05's overlapping uncommitted work is unresolved**, unless independent GPT review confirms non-overlap and an explicit fast-forward safe route. No destructive cleanup, rebase/reset, or silent cherry-pick. A valid interim status is `M17_STAGE1_IMPLEMENTED_R05_INTEGRATION_PENDING` or a specific genuinely technical blocker, never `M17_QUEUED_WAITING_FOR_R05_AUDIT` solely because R05 is open. If unpublished, supply exact local worktree path/commit and log path truthfully, not a fabricated GitHub URL.

**STAGE 2 / FINAL INTEGRATION:** Once independent GPT audit makes R05 `PASS/CLOSED` and the corresponding implementation is safely integrated on LF `main`, synchronize/reconcile the M17 work without destroying local changes, integrate any Release Pool UI and production-history dependencies, run the mandatory end-to-end, full regression, actual provider + approval gates, and only then request independent GPT M17 audit. If R05 does not close, Stage 1 still delivers useful independently testable M17 progress; M17 itself remains OPEN.

## 1. Preflight / preservation

1. Follow `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`: verify LF repo remote, fetch exact current `origin/main`, inspect Desktop checkout, local changes, worktrees, ownership, active work; non-destructive fast-forward when safe. If owner workspace dirty, preserve it and reuse one narrowly scoped worktree under `%TEMP%\ScrubBots-Level-Factory\M17-CP06-C001`. Never reset, clean, rebase, force checkout, force push, discard owner-local work or allocate repeated large game clones.
2. Record BASE SHA, existing CP03/M14 publisher, CPX-002 current-main replay, CPX-004 Studio handoff, M18/CP07 Cloudflare R2 adapter, canonical release history, accepted Release Pool/owner approval, and project/generator/VOID contracts. **No second publisher, no duplicate manifest/history authority.**
3. Codex cannot edit root `TASKS.md` or `.hiveai/audits/**`. Do not modify `Sekiph82/Scrubbots`; only document explicit external GAME_RUNTIME contracts and evidence needed. Avoid extra progress trackers; use ONE builder log with a section per task.
4. R2 bucket `scrubbots-content-prod` and public read endpoint exist, but credentials are NOT in code. No live production R2 mutation without separately explicit exact owner approval. Synthetic provider integration is allowed; no fake live receipt.

## 2. Core control-plane safety invariant

Every rollback/disable/schedule must reuse canonical CP03 provider, pack/manifest and immutable history contracts. A change is a **new, monotonic, auditably versioned content state**, never a silent overwrite or history decrement. Preserve original LevelData/solver-proven supply SHA/replay/Difficulty/VOID and pack bytes exactly. Validate stateful history, exact active manifest hash/version, new candidate hash, known-good references and provider CAS, schema/current-main replay, compatibility and explicit owner PRODUCTION approval bound to action, target, expected current, new version and candidate SHA. Pack writes precede manifest activation; fail closed on stale approval/history, corrupted objects, hash drift, game authority drift, missing packs and interruption. End-to-end readback and idempotent retry are essential.

## 3. M17.01 | SB-CP06-001..004

- **001 rollback-as-new-version:** Recover previous verified known-good content in new release `N+1` (or `N+2` after an intervening bad release), retaining full immutable original history, exact source pack hashes, reason and owner approval receipt.
- **002 known-good selection:** Durable history lookup + verified re-download/hash/schema/length for manifest and every referenced pack + current-main compatibility/replay. Wrong/stale/missing/compromised known-good fails without live mutation.
- **003 per-level disable:** Versioned declarative enable/disable state for specific level IDs; exact remaining IDs/order unaffected, packs untouched; unknown/duplicate/conflicting IDs, pack cross-binding, invalid re-enable are rejected. Support audited re-enable as successor operation.
- **004 GAME_RUNTIME external:** Do NOT edit Scrubbots. Define exact declarative disabled-level consumer behavior, adjacent-level/offline/LKG compatibility and independent game audit evidence needed. Keep `EXTERNAL_GAME_RUNTIME_PENDING` unless such evidence is independently provided.

## 4. M17.02 | SB-CP06-005..008

- **005 schedule:** Persist durable, immutable intent to activate an already verified candidate at a future time. Scheduling is never auto-publication. Implement explicit deterministic `run-due` activation operation, specifying how it is triggered; no imaginary background scheduler or extra hosting.
- **006 time source:** ISO-8601 timezone-aware schedule inputs; unambiguous UTC normalization, original zone/offset retained, DST folds/gaps handled, boundary and clock-backward/skew tests. No unsafe naive local time/lexicographic timestamp comparison or client clock used as sole production authority.
- **007 due-time revalidation:** Repeat exact current state/version/CAS, approval scope, all referenced pack hash/schema/compatibility/CPX-002 current-main SOLVED proof on activation, NOT solely at scheduling. Invalid/missing/mutated candidate or stale owner approval cannot promote.
- **008 cancel/edit:** Append-only schedule revisions, explicit cancel/supersede, no destructive rewrite; cancel-vs-fire and edit-vs-fire races safe, exactly-once or idempotent promotion; revocation and stale schedule cannot fire.

## 5. M17.03 | SB-CP06-009..012

- **009 real-state negative rollback:** Isolated genuine stateful provider (not a mocked publisher) exercises good N, intentionally bad N+1, owner-authorized simulated rollback as clean new N+2, verified full readback/history, fail-closed corrupt/stale/permission negatives.
- **010 GAME_RUNTIME external:** Provide LF-side single-disabled-level fixture/contract only, no game-repo edits. Actual official game catalog/loader skip and adjacent gameplay/offline/LKG test must be independently evidenced, otherwise `EXTERNAL_GAME_RUNTIME_PENDING`.
- **011 weekly staging:** Distinct simultaneously prepared weekly accepted batches with stable immutable identity and source-to-supply/replay binding; concurrent candidates cannot race silently into production; only explicit approved CAS winner promotes.
- **012 auditable report:** Deterministic machine-readable and human-readable publish/disable/schedule/rollback receipts derived from real durable provider records: actor reference, operation, UTC, current/next version, prior/new manifest SHA, referenced pack identity, approvals, stage/readback outcomes and reproducible report digest. Never expose secrets or claim live when simulated.

## 6. UI and integration boundaries

Keep exact three-master Factory Studio `PIXEL ART | LEVEL FACTORY | RELEASE POOL` and existing real native controls. Expose safe release actions contextually within Release Pool or a narrow existing CLI/API, preserving mandatory owner dry-run/confirm; never add fourth main tab or resurrect older eight-page UI. READY auto-enters pool; Reject excludes, Accept includes, neither publishes. Final Publish and actual PRODUCTION approval remain separate explicit owner gates. Preserve 3/4/5 supply columns, 3 preview rows, independent PNG source/supply identity, current solver, VOID and 20..59 dimensions. No work on Android Family APK or other repository.

## 7. Tests / disk cleanup

For EACH child record precise positive and adversarial tests and resulting hashes/receipts, plus PASS/FAIL/NOT RUN. Cover version monotonicity N→N+1→N+2, stale state/approval, double-click/retry, scheduling race, time-zone/DST, corrupt object, wrong exact-game authority, no pack mutation and adverse provider failures.

Avoid multi-GB duplicate game clone + persisted tar + extracted copy. Prefer verified existing read-only current-game authority and bounded small fixtures; serial execution only for heavy integration. Each fresh test gets a uniquely named **run-owned** disposable root; preserve tiny result/hash/log evidence separately; clean exactly that root using legitimate permitted operations after completion and verify free space regained. **Never bypass a deletion-policy refusal.** If cleanup is denied, stop new disk-heavy tests but continue safe bounded work. No 65-GB class tests; use existing 4 GiB per-case / 8 GiB simultaneous scratch safety thresholds.

When safely possible perform one unfiltered exact-authority full LF pytest reaching 0 errors/fails, focused CP03/CPX-002/004 and M18 provider regressions, LF19/VOID, campaign identity/replay, real Godot three-module UI, compileall, schema/secret scan and `git diff --check`. Never weaken/skip/xfail a real failure to manufacture PASS.

## 8. Completion / handoff

Use ONE log `.hiveai/codex-logs/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_CODEX_LOG.md` with per-child test table, implementation SHAs, immutable before/after identity and external gate status. No changes to root TASKS/audit files. For completed LF implementation, commit source/tests separately from log/evidence and safely fast-forward push `main` with HEAD/origin parity. Retain truthful external gates; no real R2 mutation without explicit owner approval.

Permitted final statuses: `M17_STAGE1_IMPLEMENTED_R05_INTEGRATION_PENDING`, `M17_STAGE1_BLOCKED_<EXACT_REASON>`, `M17_IMPLEMENTED_AWAITING_GPT_STRICT_AUDIT`, `M17_LF_TECHNICAL_READY_EXTERNAL_GAME_RUNTIME_PENDING`, `M17_OWNER_LIVE_APPROVAL_PENDING`, or `M17_BLOCKED_<EXACT_REASON>`. **Only independent GPT audit may close M17 in TASKS.md.** Return a real published GitHub builder log link only when it exists; otherwise report exact stopped gate and preserved local evidence.


## 2026-10-10 Stage 1 builder handoff / READ-ONLY INDEPENDENT AUDIT PUBLICATION (LATEST)

Codex reports Stage 1 implemented locally in task-specific clean TEMP worktree:
- `content_pipeline/src/scrubbots_content_pipeline/m17_release_controls.py`: rollback, known-good, disable/re-enable, schedule revise/cancel/due-run, receipt and weekly batch controls.
- `tests/unit/test_m17_release_controls.py`: **63 focused tests reported PASS**; compilation and `git diff --check` reported PASS.
- Local implementation commit `e980ff2`; log commit `ac0335d`; `origin/main` ancestor, task worktree clean, **two local commits not pushed**.
- Still OPEN: real provider/CP03 activation wiring, durable weekly registration, CP06-004/010 game-runtime evidence, R05 review and all final M17 gates.

**The builder's claims are NOT yet independently audited**. Their source, tests and log are absent from public LF `main`. Do not call Stage 1 PASS until GPT can inspect these exact bytes. To allow GPT source review without changing `main`, the next Codex action is **PUBLISH EXISTING TWO COMMITS TO AN ISOLATED REVIEW BRANCH ONLY**; this is a narrow, explicit exception to the earlier Stage-1 "do not push" rule.

1. Reuse EXACT worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M17-CP06-C001`. Do not recreate or reset it. `git status --porcelain` must be clean; verify `git rev-parse HEAD` resolves to the current full `ac0335d` commit, and that `e980ff2` is its immediate parent. Verify the local `TASKS.md` was NOT modified by Codex.
2. `git fetch origin`; verify local `origin/main` is still an ancestor of `HEAD` using `git merge-base --is-ancestor origin/main HEAD`. If main advanced after local commits, **do not rebase or force**, stop and report current SHAs; request safe review branch action without changing parent history. Avoid changing any files or rerunning expensive tests.
3. Publish **only** the existing commit tip to a non-production review branch named `review/m17-cp06-c001-stage1` via standard, non-force push of `HEAD:refs/heads/review/m17-cp06-c001-stage1`. If that ref already exists, require exact matching HEAD or stop for review; do not overwrite. Absolutely do NOT push to `main`, merge, cherry-pick, deploy, or modify R05 code. GitHub review branch is temporary evidence transport, NOT a second tracker or production authority.
4. Fetch the review branch and verify its remote SHA equals local HEAD. Return the **REAL** GitHub branch links to the M17 Python implementation, focused tests and builder log plus both full local commits. Use direct links of form `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/review/m17-cp06-c001-stage1/<path>` **only after** verified push; otherwise supply local evidence and exact push blocker, with no invented GitHub links.
5. STOP FOR GPT STAGE1 INDEPENDENT AUDIT. GPT will inspect the review branch, report PASS/CHANGES_REQUIRED for the *partial Stage 1 implementation*, and update only LF root `TASKS.md`. No full M17 PASS while Stage 2 gates remain. No live R2 actions or storage cleanup retries.

This review-branch evidence handoff **supersedes** any Stage 1 sentence telling Codex to keep already-built commits local indefinitely. Original Stage 2 R05 integration gating is unchanged.
