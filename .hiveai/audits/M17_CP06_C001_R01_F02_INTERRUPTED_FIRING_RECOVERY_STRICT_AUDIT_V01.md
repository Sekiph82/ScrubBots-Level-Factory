# M17-CP06-C001-R01 — F02 Interrupted FIRING Recovery | Independent Strict Audit V01

**Date:** 2026-10-10
**Repository:** `Sekiph82/ScrubBots-Level-Factory`, GitHub `main`
**Verdict:** **R01_F02_PASS / CLOSED**. **M17 Stage 1 technical control-plane implementation accepted, M17 as a milestone remains OPEN / Stage 2 external and integration gates pending; R05 remains UNVERIFIED.**

## Authority and material inspected

- R01 builder log `.hiveai/codex-logs/M17_CP06_C001_R01_F02_INTERRUPTED_FIRING_RECOVERY_CODEX_LOG.md` (GitHub blob `93cd8fb26fd2a69289a9a9d67c66eb097ab66c91`).
- Published implementation source `content_pipeline/src/scrubbots_content_pipeline/m17_release_controls.py` (blob `c7f38dd52efa5a4938a7138b3dca4e6f551ace49`).
- Published focused tests `tests/unit/test_m17_release_controls.py` (blob `05d99d5b9de5c971e129ed2c456385e330c59cb4`).
- GitHub implementation commit `01d65c0cc5479fa3931b5fd6e4139d739f6d0e34`; builder-log commit `9109eb7aafb7afcb975119be5ee45fe0448419f0`. Independent GitHub commit diff confirms exactly **two changed product/test files**, with no `TASKS.md`, audit, unrelated product, game repo, or F01 file changes. Builder states Desktop `HEAD == origin/main`, 0 ahead/behind, no tracked changes. Normal non-force main push recorded.
- Original M17 Stage 1 evidence already published separately: **7 focused PASS and 63 bounded regressions PASS**, compile/diff and targeted secret scan reported PASS. They were **NOT rerun for R01 or by ChatGPT**.

## Source-level verification: F02

**PASS.** Original bug was identified in `run_due()`: the durable claim key for `SCHEDULED` revision N was reconstructed incorrectly from the incremented `FIRING` revision N+1 on recovery.

- For a newly scheduled intent, `run_due()` continues to derive `schedule_id:N:candidate_sha256`.
- For a `FIRING` intent, it derives the original claim revision as `FIRING.revision - 1`, yielding the **same key** already persisted by `ScheduleJournal.claim_due()`. Invalid FIRING revision <2 fails closed.
- Journal CAS and current-head readback are preserved, followed by the existing `DueRevalidationResult` gate; on a failed revalidation the record is blocked and activation is not called.
- `CandidateActivator` explicitly requires durable side-effect deduplication by the supplied idempotency key. If activation returns false or throws, `FIRING` remains retryable with **the same key**, rather than generating a second identity. Terminal FIRED/BLOCKED/CANCELLED records are excluded from due scans.

The guarantee of **real production** at-most-once effects still depends on an actual provider-connected activator implementing this idempotency contract. **R01 does not wire CP03/R2 production activation**, so this is an accepted **Stage 1 contract plus local fixture**, not a claim of live production safety.

## Focused builder tests and owner disk protection

- The builder ran only `python -m pytest tests/unit/test_m17_release_controls.py -q -p no:cacheprovider -k f02_interrupted_firing`: **3 PASS, 7 deselected, 0 failures** in 0.82s. Two parameterized interruption windows (before activation; after activation before journal finalize) and one stale revalidation/blocked terminal case are present and source-inspected.
- Interrupted cases assert persisted claim equality, unchanged idempotency key, one deduplicated activation effect, repeated revalidation, successful FIRING→FIRED completion and zero second activation of terminal intent. Revalidation rejection yields BLOCKED and no subsequent activation.
- Existing prior 7/63 tests were not repeated; no Godot/solver/VOID/full pytest/compileall run claimed here. Staged diff check and narrow secret scan were reported PASS.
- All **57 pre-existing untracked paths**, including Godot UID/addons, `Release/`, icon and two prior test scratch folders, were **left in place at owner's explicit instruction**. No new TEMP/AppData worktrees or new test scratch roots were reported.

## Scope / remaining gates

**R01_F02_PASS / CLOSED**; F01 stays **WITHDRAWN / NOT A DEFECT** because canonical `ContentManifestV1` sorts `disabled_levels` before hashing/serialization.

**M17 Stage 1: TECHNICAL CONTROL-PLANE READY, not full production acceptance.** Still open:
- Real CP03 activation/provider integration and production readback/approval gate.
- Durable production scheduling journal and weekly accepted-batch registration/CAS winner.
- `SB-CP06-004` and `SB-CP06-010` game-runtime-specific evidence, which is outside LF implementation scope.
- R05 independent PASS/CLOSED and later full final M17 integration/regression evidence.
- Live R2 production approval; no release was attempted.

**No further R01 remediation, no repeated tests, no TEMP worktree, and no deletion/addition of the owner's 57 untracked entries.** GPT alone updates LF root `TASKS.md`. Continue the already open R05 milestone under the existing owner-locked Desktop-only workflow; resume M17 Stage 2 only when its prerequisite gates are genuinely satisfied.
