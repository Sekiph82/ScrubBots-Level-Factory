# SB-LFX-018-C001-R02-R05-B01-R03 — Disk Accounting Forensics and Safe R05 Resume

ROLE: CODEX continuation under the existing R05. This is NOT a new milestone, permission for a large test, or permission to disregard B01-R02 safeguards.

Repository: `Sekiph82/ScrubBots-Level-Factory`

Parent:
- `.hiveai/prompts/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_PROMPT.md`
- `.hiveai/prompts/SB-LFX-018-C001-R02-R05-B01-R02_DISK_FOOTPRINT_OPTIMIZATION_PROMPT.md`
- `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-B01-R02_DISK_FOOTPRINT_OPTIMIZATION_AUDIT_CRITERIA.md`

Strict R03 criteria: `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-B01-R03_DISK_ACCOUNTING_FORENSICS_AND_SAFE_RESUME_AUDIT_CRITERIA.md`.

## Trigger: builder's 2026-10-09 STOP

Codex reported a prior full-suite window coinciding with a **22,604,811,520-byte fall in C: free space**. Its measured pytest basetemp contained **1,484,869,840 bytes**, leaving **21,119,941,680 bytes not attributed by that basetemp accounting**. The optimized archive fixture is estimated at approximately 2.54 GB per test. At the report time C: had 191,108,395,008 bytes free. These are *observations*, NOT proof that pytest created all 22.6 GB.

The two formerly blocked `pytest-2308` targets and their parent were already absent at last read-only inventory; Codex did not delete them. Do not attempt another delete of these names or claim Codex removed them. R05 TEMP worktree was at `72f4170e…` matching the then-observed `origin/main`, with valuable uncommitted source/log changes. Preserve all of them.

**Current disposition: R05_UNVERIFIED / NO_TEST_NO_INSTALL_NO_PUSH until the test-storage-accounting gate is defensibly resolved.**

## Phase 0 — non-destructive source preflight

1. Read existing R05 builder log and uncommitted diff without writing or staging changes. Record exact Git HEAD, `origin/main`, ahead/behind, worktree roots, all local modifications, running Godot/pytest/Claude processes and the durable installed runtime status. Reconcile origin/main carefully if it advanced for this R03 prompt; never reset, clean, stash/drop, rebase or overwrite owner/TEMP work. Fetch/read the remote R03 prompt and criteria without creating a second giant checkout.
2. Root `TASKS.md` and `.hiveai/audits/**` are GPT-owned. Codex only implements and appends the SAME existing local R05 builder log; no secondary status dashboard. Never delete or silently replace historical evidence.
3. NO new pytest, solver stress, archive, clone, installation, regeneration, full disk crawl, or bulk change during Phase 1. The owner has expressly rejected 65 GB-class duplication and wants optimization rather than perpetual stop/retry cycles.

## Phase 1 — read-only disk forensic attribution

4. Capture timestamped available/free bytes for the correct C: NTFS volume and identify measurement semantics (decimal GB vs GiB; free-space counters vs actual directory sizes; apparent size vs allocated size). Verify what the previous samples did/did not measure, sampling timestamps and any concurrent activity. Do not treat a one-time volume-free-space delta as equivalent to pytest-generated files.
5. Inventory the previous test's known destinations/retained outputs and possible writes OUTSIDE basetemp, including only relevant locations after checking test/harness code: independent pytest temp roots and retention, `%TEMP%`, repo/TEMP worktrees, `.godot` import/cache, Git pack/clone/archive/extract outputs, Python/uv/pip caches, build/screenshot/evidence outputs, game/user data and explicitly configured `TMP`/`TEMP`/`XDG_CACHE_HOME` targets. Record paths, size-on-disk where available, last-write timestamps and ownership/association evidence. Avoid a whole-drive recursive crawl. Read-only query OS-backed large consumers (e.g. pagefile/hiberfile, restore/VSS, Windows Update, Docker/WSL VHDX, Recycle Bin) ONLY insofar as they plausibly explain concurrent change. Do not delete or modify them.
6. Inspect all relevant tests and `conftest.py`/fixtures statically for temp allocations outside `--basetemp`, large duplicated trees, retained pytest runs, background subprocess descendants, unbounded solver jobs, or cleanup after sampling. Include the optimized stream-archive implementation in the uncommitted diff. Build a concise **path-by-path size reconciliation**: baseline/end free-space delta, known new/test files, known external/OS changes, overlap/hardlink/sparse/reparse caveats, and still-unattributed remainder. Do not force a sum to match by inventing causes.
7. If historical evidence cannot reliably identify the missing 21,119,941,680 bytes, explicitly say **HISTORICAL_CAUSE_UNPROVEN**. It is acceptable to prove that the historical attribution is unrecoverable; it is NOT acceptable to label the entire volume delta a pytest footprint or casually dismiss it as Windows cache. Then design a verifiable prospective accounting gate before considering any future run.

## Phase 2 — engineer reliable accounting WITHOUT a large test

8. Build a bounded, durable test-run disk budget monitor (may be a small harness tool) that snapshots the relevant write roots AND C: volume, monitors during execution rather than only at the end, follows child processes, records peak and cumulative newly allocated test-generated bytes, logs concurrent non-test volume changes separately where defensible, and retains small machine-readable evidence. Watch known external output destinations, not just pytest basetemp; no guessed exclusion of uncontrolled writes.
9. Enforce B01-R02 unchanged: **more than 4 GiB forecast for one test -> redesign before running; more than 8 GiB incremental test-generated disk in total -> immediate safe STOP; unknown growth that prevents verifying limits -> STOP**. Additionally, if total C: free space drops >8 GiB within a controlled test window and is not promptly and evidentially classified as independent external activity, fail closed. No 65 GB class tests. A monitor must never delete existing user files or earlier fixtures. Explicitly validate that the monitor handles simultaneous file growth/deletion, subprocess failure, unexpected out-of-root writes, interrupted runs, and Windows exit codes.
10. Statically rewrite/remediate the test harness where necessary to prevent unbounded temp roots, repeated multi-GB authority clones, persisted archive+extraction duplication, or pytest temp retention. Prefer the pre-existing verified exact-current game authority and ONE isolated mutable runtime. Do not weaken historical VOID/full-history/real game solver/replay requirements, or use mutable hardlinks.
11. Produce a pre-run table of all heavy tests and expected **peak** and **cumulative** allocations, with test-specific source of estimates. Any unknown or >4 GiB projected case remains blocked pending redesign; a high current free-space value never overrides the budget.

## Phase 3 — conditional, guarded resumption ONLY after clear evidence

12. Do not conduct even a small test until Phase 1/2 prove that prospective accounting covers all materially relevant write locations, and the predicted disk limits are satisfied. Run a bounded minimal monitor self-test only if it can be done without new pytest, archive, clone or substantial disk writes; otherwise rely on static/fixture-free validation. Distinguish simulator/self-test bytes from real production proof.
13. When and ONLY when the gate passes, resume *small focused* real tests with the monitor active, stop on unexpected delta, collect peak and end sizes, preserve required proof and clean only genuinely new, tool-owned, disposable files if a legitimate action policy allows. Prior `pytest-2308` targets are not a cleanup goal.
14. Re-run genuine A READY / B FAILED / C READY identity and contiguous-order proof, N->N+1->N+2 canonical CP03-008/009 repeated production proof, LF19/VOID, solver hang diagnosis, native UI/runtime and game authority gates. Do not fake SOLVED or substitute mocks for the required current-game contract. Only if full-suite predicted/monitored budget is defensible, execute ONE unfiltered exact-current authority-enabled complete pytest with 0 fail/0 error. Abort cleanly if it threatens limits.
15. Owner-visible UI issues reported from the currently installed three-master runtime remain acceptance issues before closure: maximized 1536px-wide Windows window displays only a ~920px-wide top-left application; LEVEL FACTORY does not visibly expose 150-PNG multi-selection despite the canonical multi/CSV route. Inspect existing responsive anchors/stretch and existing batch selectors, remedy without changing the three approved visual master compositions, add native runtime tests for maximize/reflow and multi-PNG selection -> per-source solver/supply/READY workflow. Reuse existing UI regions/controls; no invented fourth tab or shadow batch compiler. This work is conditional on preserving the disk budget and existing R05 authority; never install an unverified build.
16. Complete original R05 gates (production history, full regression, final installed-runtime screenshots/SHA, Godot import, launcher, secret scan, compileall, diff check), then commit implementation/tests separately from evidence/log and fast-forward publish for GPT audit. Keep the original external Alpix gate truthful.

## Mandatory builder report / stop states

Append to the EXISTING R05 builder log:
- exact phase completed, head/source preservation proof;
- timestamped disk-accounting table in **bytes**, with separately labeled GiB where used;
- historical unexplained remainder if any; monitored locations and missing coverage;
- per-test maximum forecast/observed disk bytes and total new footprint;
- PASS/FAIL/NOT RUN for every required R05 gate, with exact command/exit and evidence;
- state whether tests/install/commits/push actually occurred.

**If historical/uncontrolled disk delta cannot be resolved and monitoring cannot bound it:** `R05_BLOCKED_DISK_ACCOUNTING / NO_NEW_TESTS / NO_INSTALL / NO_PUSH`. Submit narrowly scoped forensic findings, not a fake R05 PASS; await owner/GPT remediation.

**If disk accounting is defensible but another technical gate fails:** `R05_UNVERIFIED / REMEDIATION_REQUIRED`.

**Only after all required original R05 gates pass:** publish and mark `AWAITING_GPT_R05_STRICT_REAUDIT`. Do not self-certify audit PASS.
