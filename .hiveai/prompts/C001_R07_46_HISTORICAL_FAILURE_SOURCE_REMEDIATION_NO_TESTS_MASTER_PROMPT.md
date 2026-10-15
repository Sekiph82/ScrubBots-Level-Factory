# C001-R07 | ALL REMAINING HISTORICAL FAIL/ERROR/SKIP SOURCE REMEDIATION | ZERO TEST RUNS

## Authority
Owner specifically requires Codex to FIX the failures from the already-executed regressions, **without running the tests again**. R06 has already been implemented/published. This R07 is its **independent-audit-driven continuation**, not a rerun, not a new feature milestone, and not a request for permission to run GitHub Actions. Do not end after inventory or one tiny fix when further independently repairable code remains.

Start with a non-destructive `git fetch` and `git merge --ff-only` of the *existing Desktop checkout* of `Sekiph82/ScrubBots-Level-Factory`. Preserve all dirty/untracked user files, stashes, old worktrees and original Release. Latest Codex handoff `3e783c4758beadd96fc7e730c3c0ff615459acb9`; newer GPT independent-audit commit `564919f87976b302886fca8a556319aa78552955`. Re-read live HEAD and do NOT reset, clean, force, stash, delete or overwrite the user workspace.

Read FIRST:
1. `TASKS.md` (GPT-only), `AGENTS.md`, `GOVERNANCE.md`, latest owner process decisions.
2. Existing sole R05 builder log `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`, especially `C001-R01 resumed regression triage` and `C001-R06 source review and remediation`. Use the actual prior test report, not newly imagined failures.
3. GPT audit `.hiveai/audits/C001_R06_GPT_SOURCE_AUDIT_V01.md`, plus previous C001-R05 source audit for context.
4. The R06 exact SIX changed test files in product/test commit `27c262f26afb2c62791c6f5a4ac8ae2693599432`; compare to CURRENT runtime implementation and separate negative/positive coverage.

## ABSOLUTE ZERO-TEST AND ZERO-OWNER-DATA RULES
- **NO TEST EXECUTION of ANY KIND**: no pytest, unittest, `python -B` test invocation, test collection, test import through runpy, Godot, solver, smoke, screenshot check, test job, GitHub Actions dispatch, remote CI, fake end-to-end dry run, or any background work. Even one focused test is FORBIDDEN. You MAY READ/EDIT test files and production source, use nonexecuting AST/source reasoning and `git diff --check`; static checks must be labeled STATIC, not PASS.
- Do not create Windows/system TEMP, temp worktrees, new clones or large local artifact backups; no cleanup/delete/copy/rename of owner files. Do not solve *any* of the owner's 140 currently loaded PNGs, individually or collectively. Never overwrite/recreate the earlier nine authentic 9/9 READY files (3/4/5 column mix 4/4/1), accepted 002 run, Release Pool, gallery, PNG hashes, installed Studio or shortcut. Do not change current source-specific SOURCE_ONLY vs historical READY statuses.
- No real R2 provider read/write, STAGING/PRODUCTION, mobile publication, paid APIs, or game repo source writes. Missing genuine Scrubbots gameplay/owner-release proof must remain honest `UNAVAILABLE`, never faked as READY. No SECRET or credential handling.
- Codex NEVER edits root `TASKS.md` or GPT independent audits. **One log only**, append to existing R05 builder log; no new tracker, dashboard or session-index files.

## Required work, in this order

### R07-A: reconcile historical issue identities before patching
Canonical *historical* bounded run: **1,813 PASS / 43 FAIL / 3 ERROR / 17 SKIP / 26 subtests PASS**. This was prior to multiple corrective commits and therefore IS NOT a current regression count.

R06 log incorrectly reconciles groups: its printed category counts total **42 purported recovered failures**, then adds 2 missing = **44**, though actual FAIL=43 and prose claimed 41 recovered + 2 missing. Resolve the duplicated or overlapping historical categorization by checking the retained failure triage, historical commit snippets and exact test source identifiers. Show arithmetic (recovered unique node IDs + unidentified nodes = 43), without inventing absent node IDs. The seven PNG batch FAILs are grouped with missing exact per-node names: label `GROUP_COUNT_WITHOUT_NODE_IDENTITIES` and avoid claiming seven independently identified names. If arithmetic cannot be fully established from preserved evidence, record the precise overlap/uncertainty and leave counting **UNRECONCILED** without a false per-node closure. Capture 3 exact CP03 setup errors by name. The 17 SKIPs have no retained node IDs/reasons: inspect source decorators only, label explicitly `SKIP_IDENTITIES_UNRECOVERABLE` if no matching historical proof. Distinguish the six excluded `--ignore` modules from the 17 skips.

### R07-B: restore positive and negative READY/Release Pool coverage
R06 changed `test_sb_lfx_018_r03_alpix_auto_pool.py` so the previously positive test `test_ready_auto_enters_pool_reject_excludes_and_accept_restores_without_publish` became only `test_incomplete_synthetic_ready_auto_proof_never_enters_pool`. Keep the NEW negative fail-closed test but independently RESTORE meaningful positive tests for:
- a fully authority-backed synthetic candidate, strictly with deterministic source+request+attempt+artwork+column artifact bytes, genuine schema/digest/replay/load-check/QA, accepted candidate identity and Pool readback;
- READY_AUTO entering Pool on proven eligible artifact; REJECT excluding without publication; later ACCEPT restoring with stable no-duplicate receipt and no cloud publication;
- actual accepted 002 read-only owner Pool state is **NOT** overwritten or forced to former POOL_DENIED.
If authentic current main gameplay authority cannot be built purely as a deterministic synthetic fixture, DO NOT MOCK `READY` or tamper validators. Instead preserve the negative case, restore the positive test in a clearly documented **evidence-gated conditional** form that checks real validated preexisting proof only when already present; explicitly classify `POSITIVE_PATH_OWNER_OR_GAME_AUTHORITY_GATE`. No fake PASS/skip claim.

### R07-C: avoid bypassed real evidence gates in seven PNG batch tests
R06 modified `tests/unit/test_sb_lfx_018_r09_r02_r04_r02_png_batch.py` to mock `_verify_column_artifacts`, `_candidate_has_source_lineage`, and `_pool_row_matches` as always True in selected tests. This may isolate sequencing, but must **not** produce a global illusion of validated source/Pool/column evidence.
- Restrict each unconditional mock to an explicitly named orchestration-only test scope; do NOT patch real production validators, and prevent the mocks from escaping their monkeypatch lifecycle.
- For EACH bypassed evidence gate, **add/retain independent source-examined negative tests** using complete deterministic fixtures proving missing/corrupt/wrong SHA, mismatched batch/request/attempt/column and missing Pool row reject or remain SOURCE_ONLY/UNAVAILABLE. Add a positive contract only if it genuinely supplies the exact current proof without fake authority.
- Check `_ready_result` helper's binding against existing runtime source: do not mark synthetic `solver_status='SOLVED'` or `READY` as sufficient by itself. Keep existing runtime strict producer artifact SHA checks and separate reviewer acceptance.
- Inspect R06 `test_sb_lfx_018_r09_r02_r04_r03_batch_binding.py` changes: `artwork_png` bytes/digest, source record, output SHA and matching source snapshot lineage must be internally consistent. Repair only mismatches justified by actual production API.

### R07-D: fix remaining repairable source/test problems from R01 inventory
Do not rewrite the same six files for cosmetic changes or repeat already-corrected commits `39186a4` and `27c262f`. Compare CURRENT code/test against retained originally failed assertions:
- LF00 tracked shipping source vs untracked owner addons/Release and credential false positive; LF00-007 must check latest owner-approved policy instead of exact obsolete tracker label. Change tests only if verified stale, keep security protections.
- Studio R02 three-screen UI, source-specific Activity, read-only import and displayed batch; R03 Auto label; R09 pinned source count/VOID; 002 real Pool state. Preserve already accepted current behavior.
- Native R08 timeout invocation with candidate/visit budget is already changed. Inspect API correctness only and label UNVERIFIED, no timeout execution.
- LF06 polluted HOME / Godot resource shutdown: determine whether source can be made hermetic via isolated optional environment injection without touching owner HOME or actual Godot invocation. If impossible, describe exact remaining HOST_GATE and do NOT fake a code fix.
- Three CP03 integration setup ERRORs `test_sb_cp03_002_factory_candidate_pack.py` and one CPX001 authentic solver pack: inspect `UNAVAILABLE` originating from pinned game/source artifacts, and distinguish an erroneous fixture path from a truly missing authority. Fix only clearly incorrect fixture or production adapter identity plumbing **if source proves it**. Never fabricate canonical READY or weaken PACK checks. The real owner Release install is read-only.
- Previously lost two node IDs stay unknown unless located in existing retained logs. Do not change a different test just to hit an arbitrary number.
- Review the 17 SKIP source guards; do not erase platform/game/R2 explicit skips. Diagnose unintended skip semantics when source alone proves one but label UNVERIFIED.

### R07-E: evidence-based handoff
Append to EXISTING R05 builder log, one compact matrix by original issue **group plus recovered exact node IDs**: original FAIL/ERROR/SKIP group, pre-R06 state, specific product/test source diff or ALREADY_PATCHED, what was actually changed in R07, remaining owner/game/host gate, and verdict **SOURCE_REMEDIATED_UNVERIFIED / ALREADY_PATCHED_UNVERIFIED / EXTERNAL_GATE / HISTORICAL_ID_UNKNOWN / JUSTIFIED_SKIP_SOURCE_ONLY**. Do not change numerical suite result; do not declare PASS from code inspection.

**Actively edit and publish** all justified repairable code/test sources now, not merely another plan or summary. Only when remaining independent repairs are exhausted, commit patches and single log separately, ff-push main, verify HEAD/main parity and clean tracked state without touching owner untracked paths. If a genuine safety gate blocks one subset, continue all other subsets. Explicit final summary: ZERO TESTS RUN, SOURCE REMEDIATION ONLY, last historical 1813/43/3/17 unchanged, current outcome unknown, 140 PNG NOT_RUN, R2 NOT_RUN, Release NOT_CHANGED. Do not request to rerun tests in this cycle.
