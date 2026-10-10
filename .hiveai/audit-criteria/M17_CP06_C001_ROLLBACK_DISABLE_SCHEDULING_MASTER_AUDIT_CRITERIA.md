# M17-CP06-C001 | Independent Master Audit Criteria

**Source:** `Sekiph82/ScrubBots-Level-Factory` only.
**Master:** `.hiveai/prompts/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_PROMPT.md`.
**Builder log:** `.hiveai/codex-logs/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_CODEX_LOG.md`.
**Audit owner:** ChatGPT; Codex implements/logs but cannot alter root TASKS.md or audits.

## Gate 0 / governance
- **STAGE 1 AUTHORIZED WHILE R05 UNVERIFIED [2026-10-10]:** bounded LF-owned CP06-001..003,005..009,011..012 implementation and focused provider-neutral/local-state tests may proceed only in Desktop canonical LF checkout. Prior queue-only stop `M17_QUEUED_WAITING_FOR_R05_AUDIT` is RETIRED for Stage 1. R05 is still unverified; R04 A/B/C plus 150 imported PNGs (2 actually solver-replayed) cannot close it. Stage 1 cannot deploy, mutate live R2, close M17, or start full disk-heavy tests. Final Stage 2 Release Pool integration, mandatory full regression, publication and M17 closure still wait for independent R05 PASS/CLOSED. Partial completion is `M17_STAGE1_IMPLEMENTED_R05_INTEGRATION_PENDING`, not M17 PASS.
- Correct LF origin/main authority; owner Desktop and historical R05 local state preserved without deletion/rebase/reset/clean/force; no unauthorized game-repo edit, R2 production mutation or policy-bypass. If M17 intersects uncommitted R05 files, record exact conflict and defer only that scope; do not silently rewrite R05. Stage 1 commits must be recovered into Desktop and pushed by safe fast-forward to LF GitHub main under the existing owner rule. Never claim local-only evidence is published.
- Reuse accepted CP03, CPX-002 current-game replay, CPX-004 and M18/CDN interfaces. No parallel publisher/history/status tracker, no 4th top-level Studio module.

## M17.01
- **001** rollback to known-good as strictly newer auditable content_version, immutable prior history.
- **002** real durable prior manifest and pack retrieval, byte/hash/schema/compatibility/replay checks before live mutation; corrupted or absent history fails closed.
- **003** disable/re-enable exact selected level IDs without changing pack bytes, adjacent levels/order or mandatory provenance; negative invalid IDs and stale version tested.
- **004** LF-only consumer contract; actual game runtime audit required for DISABLED skip semantics and offline/LKG. External-only gap correctly marked PENDING.

## M17.02
- **005** schedule intent durable and not LIVE until independently invoked, verified `run-due` with genuine environment trigger disclosure; no phantom background scheduler.
- **006** zone-aware ISO 8601 and deterministic UTC/DST/clock-boundary handling, not naive time strings.
- **007** full provider/CAS/approval/identity/hash/schema/current-main replay recheck at due-time; incompatible/unapproved never promoted.
- **008** append-only cancel/edit and race/duplicate/retry behavior, no superseded or cancelled intent firing.

## M17.03
- **009** stateful provider N healthy→N+1 bad→N+2 restored as a new version, real readback, adversarial corrupt/stale negatives.
- **010** official game runtime single-level-disable evidence separate from LF fixture; without independent game audit mark PENDING.
- **011** multiple accepted weekly packs staged safely, stable identity/lineage, concurrent CAS collision refusal.
- **012** deterministic reports include action, approval reference, UTC, prev/next versions and manifest/pack hashes, real provider receipts, report digest; no invented live success or leaks.

## Cross-cutting acceptance
- Explicit narrowly bound owner approval for PRODUCTION only (action, target, prev hash/version, candidate SHA/new version), immutable source/LevelData/supply/solver/replay/Difficulty/VOID and pack semantics intact.
- Tests evidence per row, adversarial auth/CAS/provider/DST/duplicate/race, exact current-game authority, Godot three-master UI, CP03/CPX2/4/M18, LF19 and full green repository regression. Distinguish product implementation from missing external live credentials/game-runtime/owner approval.
- Test disk footprint minimized; only run-owned scratch cleaned after completion when permitted; no clone/archive GB explosion or deletion-policy circumvention. No claimed PASS on unexecuted required tests.
- Separate normal fast-forward source/test and evidence/log commits, published builder log, zero ahead/behind, independent GPT strict audit. `M17_PASS` reserved for evidence-complete LF and external gates; otherwise technical-ready/PENDING/CHANGES_REQUIRED.

## Audit outcome
`M17_QUEUED_WAITING_FOR_R05_AUDIT`, `CHANGES_REQUIRED`, `M17_LF_TECHNICAL_READY_EXTERNAL_GAME_RUNTIME_PENDING`, `M17_OWNER_LIVE_APPROVAL_PENDING`, or `PASS/CLOSED` (only after mandatory evidence).

## Latest owner-locked Desktop-only Stage 1 source review / 2026-10-10

**Only permitted Codex working directory:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`. The old TEMP M17 worktree is recovery-only for existing committed Git objects; no new execution/worktrees/clones/test roots in TEMP/AppData, no project copies or large retained scratch.

M17 Stage 1 existing local commits `e980ff2` (source + tests) and `ac0335d` (builder log) and 63 focused tests were *builder-reported*, NOT independently audited. Codex is expressly authorized to inspect/recover those specific commits through Git object history in Desktop, apply them safely with targeted `git cherry-pick` only when owner-local Desktop work cannot be overwritten, **reuse the original 63-test and compile/diff evidence without re-running tests when test-relevant source is byte-equivalent**, and publish to `main` with normal non-force fast-forward. This specific recovery takes precedence over the old instruction to hold commits indefinitely in TEMP or post them to a review branch. Preserve all local owner files and Git history, stop on conflicting changes; never reset hard / clean / forced checkout/force push. Roll back a bad committed change with history-preserving Git revert when appropriate and only without harming owner work.

Audit require: exact source/test/log available on GitHub **main**, published before GPT review, original and recovered SHA lineage, actual 63-test or exact scoped test output, `diff --check`, compile, secret evidence and 0/0 Git parity. Independently verify new implementation against existing CP03 provider interfaces and adversarial invariants; publication and test PASS are not alone sufficient for Stage 1 audit PASS.

R05 remains UNVERIFIED. M17 Stage 2 provider/CP03 activation, durable weekly registration and CP06-004/010 external runtime remain pending. Mark `M17_STAGE1_PUBLISHED_AWAITING_GPT_AUDIT`, `M17_STAGE1_AUDITED_PASS_STAGE2_PENDING` or specific `CHANGES_REQUIRED` as evidence warrants, never full M17 PASS before remaining gates.


## Owner correction: no redundant re-testing on unchanged commits

The 63 Stage 1 tests have already been reported as executed once by Codex. The narrow commit-recovery/publication job requires **no new pytest, Python compilation, Godot, solver or full regression execution** when the recovered implementation/test contents remain identical to the prior completed commit. Review historical command results in the published builder log, compare Git object/tree/diff identities read-only and independently inspect code. Re-running a suite solely to copy existing commits from one checkout to another is not an acceptance requirement and wastes owner time/disk. If the source really changed or log lacks necessary evidence, record the precise gap and seek a narrowly scoped follow-up test rather than automatically rerunning 63 checks. M17 full closure is still a distinct future Stage 2 gate, not part of this recovery task.
