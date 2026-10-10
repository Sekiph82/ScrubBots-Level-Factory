# M17-CP06-C001 Stage 1: Independent Strict Audit V01

Date: 2026-10-10
Authority: `Sekiph82/ScrubBots-Level-Factory` `main`
Verdict: **STAGE1_CHANGES_REQUIRED / TWO TARGETED FIXES**. Full M17 remains OPEN; R05 remains UNVERIFIED.

## Reviewed evidence (without running tests)

- `content_pipeline/src/scrubbots_content_pipeline/m17_release_controls.py` published blob `7520c63b79781354f208c6cdbbadd383dfa3c080`.
- `tests/unit/test_m17_release_controls.py` published blob `dfd6c7d462348fca498fd67dd8923eec973879b8`.
- `.hiveai/codex-logs/M17_CP06_C001_ROLLBACK_DISABLE_SCHEDULING_MASTER_CODEX_LOG.md` published blob `3e6983029a60d174051b3309017b88caf429233b`.
- Published implementation `6d5c5d06e5750d8c9fc04696fe6fc0d7b34532c3` (original `e980ff2fbc3a2b7c0441d85c2bf51791d5ac0f81`); published builder log `d721844a0fb7d6f124aaaa5108fa1939d87a1e87` (original `ac0335d7ebbb08ba3703826b8e75a9d441c8a33c`). Builder reports latest Desktop/origin/main parity `d569d075`, 0 ahead/behind.
- Builder reports 7 focused tests and 63 bounded regression PASS, py_compile/compileall, diff and targeted secret scan PASS. Earlier failing attempts were corrected. **These existing tests were not rerun for this independent audit.** GitHub-published identical source blobs and log were independently inspected.

## Accepted work / retained

- Correct bounded Stage 1 architectural separation from CP03 production activation: no live R2 writing/real publication claim, no alternative manifest history. `select_known_good` checks history, manifest/schema/compatibility, pack byte length/SHA and replay receipt; the existing tests use a local SQLite provider and synthetic current-game replay receipt, with the limitation disclosed.
- `prepare_rollback_candidate` creates a monotonic successor with owner approval binding and immutable source packs; `prepare_disable_candidate` changes disabled levels declaratively; schedule intent has IANA-zone/DST handling, revision hashing/CAS, cancel/edit/supersede, and due-run interfaces; control receipts and weekly identity are deterministic for the tested cases. External `SB-CP06-004/010`, production provider/activation, durable weekly batch registration and M17 final regression remain OPEN.
- Desktop owner-local 55 untracked paths were preserved; **actual names are not in the published log**. The two known new test-owned untracked paths are `.m17-cp06-c001-pytest-focused-20261010` and `.m17-cp06-c001-pytest-regression-20261010`, and deletion was denied by shell policy. Do not claim these were cleaned. Never delete unknown local owner files.
- Prior 63-test evidence accepted as historical builder verification. No new test suite run required for already unchanged code.

## Blocking issues identified by source inspection

**F01. Unstable candidate manifest bytes for multi-disable/re-enable.** `m17_release_controls.py` `prepare_disable_candidate()` (~228-271) constructs an unordered `set` of disabled levels and passes `disabled_levels=tuple(updated)` to the canonical manifest. When multiple IDs are disabled, tuple order may vary between processes/interpreter hash seeds, changing manifest bytes/SHA and invalidating otherwise unchanged dry-run/owner-bound approval. Existing Stage 1 test covers only a single ID. Required remediation: derive a deterministic order from immutable manifest level ordering (or the canonical validated ordering contract), preserving exact identity across retries/processes; add **one narrowly targeted multi-ID/order stability regression**, not the old 63-test suite again.

**F02. `run_due()` crash/retry after FIRING cannot recover the original claim identity.** `m17_release_controls.py` `run_due()` (~907-959) derives `claim_key` from `revision.revision`, then `claim_due` advances schedule state SCHEDULED revision 1 to FIRING revision 2. A later run sees revision 2 and derives a *different* key; the SQLite journal's `claim_due` implementation only accepts the original persisted key for an already FIRING record. If activation or finalization is interrupted, the schedule can be stranded in FIRING and never safely retried. The existing Stage 1 test validates immediate happy-path and cancellation race but not this crash window. Required remediation: durable stable claim/idempotency key persisted across SCHEDULED→FIRING, original-claim retry semantics, fail-closed no-double-activation proof, **focused interrupted-FIRING recovery test only**. Do not weaken CAS/approval checks.

No real CP03 activation/provider publication was assessed or authorized in this partial stage.

## Strict disposition

- **M17 Stage 1: CHANGES_REQUIRED / F01+F02 only.** All accepted existing functionality retained. Do not reimplement completed features or repeat 7/63 tests. Codex should correct these specific issues using ONLY canonical Desktop LF checkout; no TEMP or AppData worktrees, no repeated full regression/150 PNG operations.
- Remediation tests: **new/changed affected cases ONLY**, requiring recorded source diff and objective assertions. ChatGPT will independently audit the new code and existing log, and solely update LF `TASKS.md`. Existing M17 stage remains partial, with R05 and Stage 2 gates open.
- The 55 existing Git-untracked Desktop paths **cannot be enumerated from GitHub**. A separate read-only local `git status --porcelain=v1 -uall` inventory is needed if owner wants exact names, sizes and classification. Never add, publish or delete them without owner approval.
