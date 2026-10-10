# M17-CP06-C001 Stage 1 — Independent Strict Audit V02 (Correction)

Date: 2026-10-10
Repository: `Sekiph82/ScrubBots-Level-Factory`, published `main`
Final Stage 1 status: **CHANGES_REQUIRED / F02 ONLY**. R05 remains UNVERIFIED. M17 final Stage 2 remains OPEN.

## Corrections to V01 audit
The previous V01 audit mistakenly flagged F01 (unstable ordering of `disabled_levels` in `prepare_disable_candidate`). **F01 IS NOT A DEFECT AND IS WITHDRAWN.** Although `m17_release_controls.py` passes `tuple(updated)` from a set, the canonical `ContentManifestV1.__post_init__` in `content_pipeline/src/scrubbots_content_pipeline/manifest_v1.py` explicitly normalizes `disabled_levels` by `sorted(..., key=lambda level_id: level_id.encode("ascii"))` before canonical `to_json_bytes()` serialization. Therefore the final manifest ordering/hash is stable despite the initial tuple ordering. Do NOT change this accepted code or add a test just to repair the incorrectly alleged F01. Retain existing 7 focused and 63 bounded-regression builder test evidence without repeating it.

## Remaining demonstrated issue: F02
Published `content_pipeline/src/scrubbots_content_pipeline/m17_release_controls.py` `run_due()` derives the claim/idempotency key using the currently observed schedule `revision.revision`, then `journal.claim_due()` advances `SCHEDULED` revision 1 to `FIRING` revision 2. On a resumed call, `run_due` sees `FIRING` revision 2 and derives a **different** key. The current local SQLite `claim_due()` in `tests/unit/test_m17_release_controls.py` specifically requires the original persisted claim key for `FIRING`; the recovered attempt is rejected and the release intent remains stranded. This is a real interrupted-execution / recovery gap. Do not weaken CAS or owner approval; use a stable, durable claim identity spanning `SCHEDULED` → `FIRING` and retry/finalization. For a possible crash after actual activation but before journal finalization, require an idempotent activator contract and exact same idempotency key. Verify with one narrowly scoped interrupted `FIRING` regression, with explicit at-most-once activation expectation or documented fail-closed behavior for uncertain remote acknowledgments.

## Reviewed/retained evidence
- Source `content_pipeline/src/scrubbots_content_pipeline/m17_release_controls.py` and `tests/unit/test_m17_release_controls.py` published to GitHub `main`.
- Builder log: `.hiveai/codex-logs/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_CODEX_LOG.md`. Original source/test commits `e980ff2`/`6d5c5d0`; builder log `ac0335d`/`d721844`.
- 7 focused and 63 bounded tests PASS, compilation/diff/targeted secret scan PASS per **existing builder log**. These have NOT been rerun for V01 or V02 audits.
- Production provider + CP03 activation, durable weekly batch registry, external `SB-CP06-004/010` game-runtime evidence and final R05-dependent integration are not claimed complete.
- Owner has explicitly said the existing 55 untracked paths plus two known test scratch paths **must remain untouched**. Do not commit, delete, modify, clean, move, rename, or reclassify these paths during F02 remediation.

## Verdict and next implementation
**M17-C001 Stage 1: PARTIAL ACCEPTANCE / F02 TARGETED REMEDIATION REQUIRED ONLY.** Audit V02 supersedes the V01 F01 finding and preserves all other accepted functionality. Prepare one small Codex remediation within the Desktop LF checkout, one relevant regression for the genuinely changed F02 behavior, separate code/log commits, ordinary fast-forward GitHub main publication, followed by ChatGPT re-audit. No TEMP/AppData worktrees, extra clones, full pytest/63-test replays, owner files cleanup, R2 production actions or other-repository changes.
