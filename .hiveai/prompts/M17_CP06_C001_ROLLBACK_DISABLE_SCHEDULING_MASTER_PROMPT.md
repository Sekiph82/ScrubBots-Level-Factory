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

**STAGE 1 HANDOFF (OWNER-STANDARD RESTORED):** An authorized, bounded, non-overlapping M17 Stage 1 implementation is published to the LF repository's `origin/main` after passing its scoped tests, without waiting for M17 final integration or the R05 audit. TEMP worktrees are safe execution locations only, **not the final delivery**. Codex commits product/tests and builder log separately, publishes to `main` by a normal fast-forward push, verifies 0 ahead/0 behind, and returns the real GitHub log URL. If newer ChatGPT documentation commits advanced `main`, use only the explicit non-destructive reconciliation procedure below; preserve owner Desktop and R05 worktrees. ChatGPT audits after publication and alone updates root TASKS.md. A partial Stage 1 GitHub publication is NOT M17 PASS or a production R2 action.

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


## 2026-10-10 OWNER WORKFLOW CORRECTION: PUBLISH M17 STAGE 1 TO MAIN, NOT TEMP OR REVIEW BRANCH

**This is the latest controlling instruction.** The previous one-off "review branch only / keep commits in TEMP" exception is **withdrawn**. Restore `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`: direct source+builder-log GitHub `main` publication, followed by GPT independent audit and GPT-only TASKS lifecycle updates.

Known builder state: isolated M17 Stage 1 worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M17-CP06-C001` contains two committed changes, `e980ff2` (source/test) and `ac0335d` (builder log); Codex reports 63/63 focused tests, compilation and diff-check PASS, no product R2 wiring, no main publication. Treat these as builder reports until reviewed. **Do not rerun Stage 1 implementation or create fresh worktrees.**

1. **Preserve:** verify source LF repo and `origin`, owner Desktop and existing R05 TEMP worktree. Check `git status --porcelain` clean, exact commit lineage, no modified root `TASKS.md`, no secrets and that M17 changes are only new independent Stage 1 module, tests and log (no overlap with uncommitted R05 files). Never discard files or use `reset --hard`, `clean`, `rebase`, `cherry-pick` or force push.
2. **Fetch/reconcile:** `git fetch --prune origin`. If `origin/main` is an ancestor of local `HEAD`, continue. Otherwise, main may have advanced only through ChatGPT's M17 prompt/audit/TASKS documentation commits. **One-time, explicit authorization:** when the exact intervening diff consists only of those ChatGPT-authored documentation/tracker changes and has no production-source overlap, integrate `origin/main` into the current M17 task worktree using a normal **non-destructive merge commit** (`git merge --no-ff origin/main`). This preserves both original Stage 1 commits and the latest LF documentation. If there is any source overlap, merge conflict, dirty state, unexpected ancestry or safety concern, **STOP WITHOUT PUSH**, preserve commits, and report exact SHA/path conflicts. No automated resolution and no editing `TASKS.md`. Do not amend/squash/rewrite the original two commits.
3. **Validate** resulting tree: correct `m17_release_controls.py`, 63 focused tests or their exact established bounded suite, compilation, `git diff --check` and secret scan PASS; latest `origin/main:TASKS.md` bytes preserved, R05 TEMP work untouched. Do not start huge full regression or provider LIVE operations; Stage 1 remains partial.
4. **Publish normally:** ensure `origin/main` remains ancestor of `HEAD`, then `git push origin HEAD:main` without force. Fetch again; require `HEAD == origin/main`, 0/0, clean worktree. Commit implementation/tests and log stay separately visible in history.
5. **Report actual GitHub main links** to the implementation, tests and builder log, full SHAs and exact tests. Then GPT independently inspects Stage 1 evidence and records a partial verdict in LF `TASKS.md`. Provider/CP03 activation, durable weekly batches, external CP06-004/010 and final R05-dependent Stage 2 gates remain OPEN. Do not close them just because files reached GitHub.

If the one-time reconciliation conditions do not hold, do not divert to a `review/*` branch or repeat work. Return one precise blocker; GPT will resolve the integration path under the standing standard.
