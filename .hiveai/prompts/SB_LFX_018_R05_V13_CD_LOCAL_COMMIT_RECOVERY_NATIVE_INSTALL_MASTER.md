# SB-LFX-018 R05 M03 | EXECUTION UNBLOCK + REAL OWNER-002 NATIVE REPLAY | UNRESTRICTED ENGINEERING MASTER V02

Document role: CODEX BUILDER PROMPT
Active continuation: **SB-LFX-018 R05 V13-C/D RECOVERY + NATIVE/INSTALLED ACCEPTANCE**, 2026-10-21.
This is NOT a fresh milestone, reimplementation, or permission to touch the original 140 PNGs.
Exact repo: https://github.com/Sekiph82/ScrubBots-Level-Factory
Only permissible working checkout: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator
Authoritative task ledger: root TASKS.md. Main is canonical GitHub authority.

## OWNER DIRECTIVE AND VERIFIED HANDOFF FACTS

Owner reports that V13-C/D is implemented and TESTED **locally only**:
- Local code/tests commit 04c9f40; builder-log commits 8597265 and 94c71d7, in that order. Their Git objects have NOT been independently inspected by GPT and were NOT on GitHub main when this handoff was written. Verify objects, parent chain and actual diffs on Desktop before treating anything as PASS.
- Local report: 240s soft deadline, 480s TOTAL hard deadline in SAME surviving Godot native process, extension status/progress, process-tree termination at hard deadline; provider_credentials.py logic relocated into manifest-managed studio_extensions.py. No Release install.
- Builder-reported tests: 23 PASS + 16 subtests PASS, 8 Python AST files PASS, git diff --check PASS. These are **builder-reported only**, not native Godot 4.7.2 / actual installed GUI proof.
- At local attempted push, local was 3 commits ahead and 1 behind origin/main (remote then 2f8a961). GPT later verified remote main advanced to af4c0f0, a TASKS.md-only commit, before this handoff; this NEW prompt and TASKS update also advance remote further. ALWAYS fetch current origin/main; do not hardcode those old tips as current.
- The full 38 uploaded original problem PNGs were ALREADY received and independently assessed in V15: 34/34 REJECTED match strict V3 source-rejection metrics, 4/4 FAILED are pixel-contract valid; 019 has a saved WinError 5 pipeline failure; 056/058/060 have saved native 240s timeout evidence. All 38 original images exist in prior user attachments. No more owner PNG requests, original SHA changes, recoloring or replay.
- Protected immutable owner complete job png-batch-875545d48a14a0d6b4d542f554919e8d: 140 COMPLETE, 102 READY, 4 FAILED, 34 REJECTED, zero remaining. Do not resume, re-run, reclassify, publish or mutate. 102 READY Release Pool records and all source/owner data immutable.
- V13-A 38 individual issue ledger is already in existing M03 builder log, around line 470; V13-B UI/providers/source improvements already published. NEVER redo V13-A or V13-B.

## REQUIRED AUTHORITY AND HARD POLICIES

READ before edits:
1. root TASKS.md, AGENTS.md, GOVERNANCE.md;
2. docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md, especially 2026-10-10 OWNER DESKTOP ONLY / NO TEMP;
3. SAME original V13 master .hiveai/prompts/SB_LFX_018_R05_V13_BATCH140_38_ISSUE_AUDIT_PIXEL_ART_PROVIDERS_UI_REPAIR_MASTER.md and strict acceptance .hiveai/audit-criteria/SB_LFX_018_R05_V13_BATCH_ISSUES_PROVIDER_UI_STRICT_GATES.md;
4. .hiveai/audits/SB_LFX_018_R05_V13_A_B_SOURCE_38_ISSUE_INDEPENDENT_AUDIT_V14.md and .hiveai/audits/SB_LFX_018_R05_V13_OWNER_19_PNG_PIXEL_COMPARISON_AUDIT_V15.md;
5. append-only existing log .hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md; retain its existing H1 exactly (the prompt H1 intentionally matches it).

Current 2026-10-15 owner cost lock: **ZERO GitHub Actions, ZERO CI (hosted or self-hosted), ZERO paid cloud tests**. No triggering, changing workflows or billing. No extra PixelLab credits, Claude calls during cooldown, secret disclosure, network provider smoke, R2, STAGING or PRODUCTION. Only bounded local no-cache tests in existing permitted Desktop repo. No new or reused TEMP worktrees, clones, project copies, Desktop siblings, unapproved pytest/temp scratch or Godot import copies. Do NOT modify TASKS.md, audits, past prompts or .hiveai/HANDOFF.md: GPT owns them. Preserve existing local owner files, untracked .uid/import/.godot/cache, credentials, manifests, Pool, PNGs; no reset/rebase/force/clean/autostash/blanket deletion. Do not kill an owner process to enable install.

## A. RECOVER THREE COMMITS AND PUBLISH SAFELY FIRST

1. Working directory EXACTLY C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator. Verify git toplevel, origin exact identity, branch, HEAD, git status --porcelain, git worktree list, stash list; inspect local and remote ahead/behind. Fetch --prune origin.
2. Independently inspect git cat-file -t and git show --stat / --format=fuller for 04c9f40, 8597265, 94c71d7, including their ancestry and each changed path. Verify reported change scope, test evidence and existing builder log; report if any named object missing or unrelated changes found. NO assumption that these unpublished local commits exist in GitHub.
3. Protect the original divergent local branch and all three exact SHAs in place. NO merge or rebase of that branch, no force push. If Desktop tracked worktree is clean and switching is proved harmless to untracked owner files, safely create ONE new local integration branch at the exact latest origin/main in the SAME Desktop checkout and targeted cherry-pick the three verified commits, original order. This is a history-preserving additive replay onto new remote baseline, NOT rewriting the original local branch; existing standard explicitly permits targeted cherry-pick. Protect all owner data and ensure git never overwrites untracked paths.
4. If branch switch/cherry-pick cannot be proven owner-safe, if protected paths collide, or if conflicts cannot be resolved based on exact evidence, STOP THAT MUTATION ONLY and label BLOCKED_LOCAL_DIVERGENCE with path/SHA. Never create another worktree/clone or bypass a policy to push. Continue read-only reviews and report. Do not use destructive checkout. If an in-progress cherry-pick must be aborted, do so only after proving it cannot discard owner changes.
5. Preserve code/test content from 04c9f40 byte-identically if possible; record original vs replayed commit tree/diff hashes. Normal publication only after rechecking remote ancestry and workflow trigger: git push origin HEAD:main, then fetch, HEAD == origin/main, zero ahead/behind, clean tracked task state. This prompt/TASKS commit may appear as additional remote-only commits since the owner's log.
6. REUSE the earlier 23 + 16 narrow test evidence for byte-identical code. Do not spend time re-running unchanged suites only to replay commits. If a conflict genuinely changed product bytes, run only relevant bounded no-cache tests and record changed code and reason. Each failed attempt remains in chronological log. Never call this GitHub CI or native PASS.

## B. INDEPENDENTLY REVIEW V13-C/D PRODUCT SAFETY AFTER REPLAY

Inspect actual source and tests, not just the reported test numbers:
- src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py, solver_budget.py, supply_optimizer.py, studio_extensions.py, launcher/worker bindings, Godot UI and related local test files.
- Assert original 240.00s soft boundary, uninterrupted SAME PID/process/invocation until total 480.00s hard boundary; one launch, not 240+480 or 720, no job duplication, status EXTENDED with original request/source SHA, live PNG/source identity, accurate elapsed/remaining/progress, correct terminal success, early fail, no solver auto-retry; manual cancel at any time; scoped exact child tree cleanup ONLY after hard deadline or user cancel. MAX_VISITS/coverage/WIN and terminal failure are independent hard gates.
- Reconcile fake-clock cases 239.99/240.00/400/479.99/480, success at 20 and 310, terminal unsolvable at 239, cancel at 300, process exit/IPC error/orphan handling; record which are actually covered and code gaps. Do NOT rerun the three failed PNGs, original 140, or update READY.

## C. CLOSE REAL RUNTIME IMPORT/INSTALL DEPENDENCY GAP

GPT's published-source inspection of scripts/install_factory_studio_scoped_overlay.ps1 at pre-handoff main confirmed its relativePaths DOES NOT include src/scrubbots_pixel_factory/alpix_batch.py or provider_credentials.py, even though V13-B runtime used these imports. A local consolidation of provider_credentials into managed studio_extensions.py may resolve ONE dependency; do not assume ALPIX is solved.

- Read import graph from actual launcher level_factory/scripts/factory_core_launcher.py, studio_extensions.py, alpix_batch.py, semantic provider bridge, and all relative import/call sites after replay. Verify a fresh installed-runtime Python import can succeed without relying on source checkout modules inadvertently present on PYTHONPATH. Check current installed files and manifest read-only, paths, managed ownership and hashes.
- If provider_credentials.py really becomes unused, verify no runtime dependency remains, without deleting historically owned files. For alpix_batch.py either verify exact installed managed/allowlisted dependency safely, or make a narrow manifest-compatible correction. Installer's authorizedOverlayAdditions list is NOT automatic permission to take ownership of an unmanaged or absent installed file.
- Before any write, require exact expected manifest entry ownership, installed baseline SHA, no reparse/symlink traversal, valid rollback and owner process/writer quiescence. If dependency is unowned/missing or owner data at risk, label INSTALL_BLOCKED_MANAGED_DEPENDENCY and preserve. DO NOT silently overlay, add unowned files, perform broad installer or create new shortcuts.
- Preserve Claude Code subscription-backed ALPIX/MCP historic path; current ALPIX_PLUGIN_MISSING is distinct from quota. Do not call Claude or fabricate plugin availability. PixelLab config via user Credential Manager ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN, never print any secret; CONFIGURED is not paid generation PASS.

## D. NATIVE GODOT 4.7.2 AND INSTALLED GUI VALIDATION

- First perform READ-ONLY native preflight: exact installed Godot binary/version, process inventory scoped by executable path + commandline/parent identity (not stale PIDs), tracked and owner-generated .uid/.import/.godot/cache content & hashes, the project's write behavior and install manifest/Pool/source SHA baselines. Do not open/run the Godot editor against protected owner project if it can rewrite original .uid/import/cache; no project copy/TEMP workaround.
- Run focused REAL Godot 4.7.2 parse/scene/GUI checks ONLY if a bounded native invocation can be proved safe on the same permitted Desktop installation without mutating protected owner files or invoking a paid external route. Otherwise record exact NATIVE_GODOT_OWNER_CACHE_WRITE_RISK or another evidence-based BLOCKED reason; Python AST/PASS never substitutes for native testing. A new transient alternative project folder is NOT authorized.
- The installer may run only AFTER product source is published on main, import dependency closure is proved, a manifest preflight is clean, owner app and live writers are normally closed and no protected SHA changes occur. Do not terminate Studio or batch worker automatically; ask owner only for the precise required normal UI close if truly needed, and continue all nonblocked work.
- If all gates pass, use ONLY scripts/install_factory_studio_scoped_overlay.ps1 in its preflight and transactional narrow Apply modes, existing Release directory, backup/rollback verification, no broad install; pre/post hash the protected complete job, original 140 PNGs, source upload records, 102 READY Pool; owner screenshot of actual installed 3-page UI.
- Screens must prove: PIXEL ART provider statuses truthful, no Magnific/active Style, chosen Size W×H live; LEVEL FACTORY exact same COMPLETE 102 READY/4 FAILED/34 REJECTED/0 pending and NO old Resume104, 38 scroll/filter issue rows, original SHA-bound selected PNG and exact reason; RELEASE POOL unchanged. Guard native 1536×1024 geometry and smaller viewport, preserve previous R09 geometry failure as OPEN if still failing. No fake screenshots, no simulated GUI acceptance.

## E. REPORT AND STOP CONDITIONS

Append chronological actual steps/commands/failed attempts/PIDs only when real, SHA evidence and test results to the EXISTING M03 builder log; do not overwrite prior log history. No second tracker or new log. First publish exact recoverable code + log if safely possible even if native or install remains blocked; do NOT allow optional GUI constraints to hide safely publishable commits. Subsequent genuine fixes require narrow new code/test commit plus append-only log and normal main publication, respecting ancestry.

Return an exact short summary with: starting/ending GitHub SHA; original three commit SHAs and integrated equivalents (if safely replayed); SAFE_PUBLISHED / BLOCKED_LOCAL_DIVERGENCE; V13_D_SOURCE_VERIFIED vs unresolved tests; importer dependency closure; NATIVE_GODOT_PASS / NOT_RUN / BLOCKED; INSTALL_APPLIED / BLOCKED; actual GUI evidence/OPEN gates; immutable 140 job and 102 Pool hashes; ONLY actual GitHub URL of published existing M03 builder log. Never mark V13 complete or TASKS closed: independent GPT audit and owner native acceptance are separate. Continue through all safe tasks without stopping for routine acknowledgments; stop mutations only for true owner-data/safety/permission blockers.