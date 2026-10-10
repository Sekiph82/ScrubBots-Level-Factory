# M17-CP06-C001 | Independent Master Audit Criteria

**Source:** `Sekiph82/ScrubBots-Level-Factory` only.
**Master:** `.hiveai/prompts/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_PROMPT.md`.
**Builder log:** `.hiveai/codex-logs/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_CODEX_LOG.md`.
**Audit owner:** ChatGPT; Codex implements/logs but cannot alter root TASKS.md or audits.

## Gate 0 / governance
- **STAGE 1 AUTHORIZED WHILE R05 UNVERIFIED [2026-10-10]:** bounded LF-owned CP06-001..003,005..009,011..012 implementation and focused provider-neutral/local-state tests may proceed on isolated clean M17 TEMP worktree. Prior queue-only stop `M17_QUEUED_WAITING_FOR_R05_AUDIT` is RETIRED for Stage 1. R05 is still unverified; R04 A/B/C plus 150 imported PNGs (2 actually solver-replayed) cannot close it. Stage 1 cannot deploy, mutate live R2, close M17, or start full disk-heavy tests. Final Stage 2 Release Pool integration, mandatory full regression, publication and M17 closure still wait for independent R05 PASS/CLOSED. Partial completion is `M17_STAGE1_IMPLEMENTED_R05_INTEGRATION_PENDING`, not M17 PASS.
- Correct LF origin/main authority; owner Desktop and R05 TEMP state preserved without deletion/rebase/reset/clean/force; no unauthorized game-repo edit, R2 production mutation or policy-bypass. If M17 intersects uncommitted R05 files, record exact conflict and defer only that scope; do not silently rewrite R05. Stage 1 commit work may remain locally preserved until R05 safely lands; never misrepresent local logs as GitHub publication.
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


## Stage 1 review-branch evidence audit (2026-10-10)

Builder has *reported*, not independently proved, 63 focused PASS, clean compile/diff, and two local commits `e980ff2` (source/tests) + `ac0335d` (builder log). Until source/tests/log can be read through a verified GitHub review ref, Stage 1 is **BUILDER_REPORTED / AWAITING_INDEPENDENT_STAGE1_AUDIT**, not PASS.

An isolated `review/m17-cp06-c001-stage1` branch is authorized solely to publish the existing two local commits for GPT inspection while `main` advances independently. Require no force, clean local worktree, verified matching remote tip, no `main` update, original ancestor base and unmodified root TASKS.md. A changed `main` due to documentation commits alone does not bar an isolated review branch. No secret/private credentials in branch or logs.

Once readable, independently inspect `m17_release_controls.py`, `test_m17_release_controls.py`, existing CP03/M18 controls and the builder log. Verify actual authorization/CAS, rollback monotonic history, immutable pack identities, fail-closed schedule/disable, receipts, idempotent race/DST cases, and that 63 tests did not merely assert mocks. Focused implementation PASS is **partial** and does not imply real provider wiring, CP03 activation, durable weekly registration, CP06-004/010 runtime, full LF regression or M17 closure.

Return `STAGE1_REVIEW_PENDING_SOURCE_PUBLICATION` while branch absent; `STAGE1_AUDITED_PASS_STAGE2_PENDING` or `STAGE1_CHANGES_REQUIRED` only after authentic code/tests/log inspection. Stage 2 may only finish after R05 independently PASS/CLOSED and accepted integration gates. Never claim M17 PASS based solely on locally reported tests.
