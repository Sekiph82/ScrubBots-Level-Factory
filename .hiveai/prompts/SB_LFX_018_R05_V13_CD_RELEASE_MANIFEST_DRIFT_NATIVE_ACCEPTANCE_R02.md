# SB-LFX-018 R05 M03 | EXECUTION UNBLOCK + REAL OWNER-002 NATIVE REPLAY | UNRESTRICTED ENGINEERING MASTER V02

Document role: CODEX BUILDER PROMPT
**Execution scope:** SAME existing SB-LFX-018 R05 V13-C/D continuation, Release manifest drift + native/installed proof R02. **No new milestone, no V13-A/B restart.**
**Canonical repo:** https://github.com/Sekiph82/ScrubBots-Level-Factory
**Only allowed development checkout:** C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator
**Canonical tracker:** root TASKS.md.
**GitHub verified starting published V13-C/D source SHA:** `29d0360033643eacec36d732415fa21b0697bcd9` (verify current `origin/main` after fetch; audit/prompt/TASKS GitHub commits may advance it).

## Objective and authority

V13-C/D product source **IS ALREADY ON MAIN**. Original owner local code/log commits were recovered as `d247b82`, `c695146`, `41b474d` and follow-up one-native-solver-evidence fix `7bf85b2`; builder receipts `535969d`, `29d0360`. Do NOT repeat that work or force any rebase, merge, rollback, regenerated PNG, 140 replay, or lost-commit recovery.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md; the original SAME V13 master and strict V13 criteria; GPT independent `.hiveai/audits/SB_LFX_018_R05_V13_CD_RECOVERY_SOURCE_PUBLICATION_AUDIT_V16.md`; the existing M03 builder log; and `scripts/install_factory_studio_scoped_overlay.ps1`. Follow strongest owner rule **DESKTOP ONLY / NO TEMP worktree, clone, extracted project/copy or new scratch**, including historical worktree exceptions. Builder does not edit TASKS.md, published used prompts, GPT audits or HANDOFF. Append only to existing log with original H1 and `Document role: CODEX BUILDER LOG`.

**Owner cost/safety locks:** ZERO Actions, CI, paid test provider/credit use, Claude probing while cooldown, automation billing, R2/staging/production; no secrets. No repaint/reclassify/auto retry of 34 REJECTED or four FAILED. Keep immutable original complete job `png-batch-875545d48a14a0d6b4d542f554919e8d` (140 total /102 READY /4 FAILED /34 REJECTED /0 remaining) and Release Pool unchanged. Do not ask user to resend 38 issue PNGs; V15 independently examined all 38.

## Phase 0: Canonical repo, preflight, baseline

- Confirm exact canonical root, origin, current branch, Git status, stashes/worktrees, current `main`/`origin/main`; run fetch/prune. If checkout is dirty/unsafe, preserve exact owner bytes; no reset, forced clean, autostash, rebase, or alternate clone. For a fast-forward-safe clean same-Desktop checkout, use only normal ff-only sync.
- Confirm current GitHub code and logs already include the V13-C/D single-process staged solver and single-export-proof fix. Do NOT re-run 23/16 or 13/16 unchanged tests; re-use their actual immutable prior evidence, state the missing owner fixture honestly. No claims of full R09 or native PASS.
- Baseline READ-ONLY real Release manifest (mode `OWNER_APPROVED_SCOPED_OVERLAY`, 2,318 managed items reported), managed/overlay path entries, installed relative files, executable launch path/import graph, SHA256, owner symlinks/reparse points, exact worker/Studio PID tree. Baseline batch JSON SHA `33c11885032f9b9b6050ea642c4870e04e8424dacc00de749b51234ce9f94193`, state digest `56823da1561858e6275e180b0c766b46daacf6f735e7200cfce47b0369d98490`; Pool 131 JSON tree SHA `e227c95f85635a48522dbdd5aefeb2ead51f2e25070fb8f4b315746ebbc9a81d`. Treat builder SHA evidence as baseline to reverify, not authority to rewrite it.

## Phase 1: Resolve exact installed manifest drift (not a blanket installer)

Prior Codex read-only evidence:
- Manifest SHA for `src/scrubbots_pixel_factory/supply_pipeline/verify.py`: `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2`.
- Actual installed `verify.py` SHA: `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744`.
- Source `verify.py` has further V13 follow-up changes; `supply_exporter.py` also changed. Neither is in scoped updater `relativePaths`; its `authorizedRepairHashes` covers specific historical solver/optimizer variants, NOT verify.py.
- Installed `alpix_batch.py` reportedly exists, is manifest managed and SHA equals source `e1059e832152829c0874b15958f1fa0be61fe20beccf218df3fefede4aad7282`; the prior `provider_credentials.py` standalone SOURCE was removed and the needed API moved into managed `studio_extensions.py`. Verify installed-source-only import chain (no accidental Desktop sys.path imports).

**Required implementation task**:
1. Produce exact side-by-side evidence `verify.py` expected managed manifest SHA / installed SHA / exact current GitHub source SHA and byte/stat/diff/provenance. Determine whether installed deviation reflects a deliberate hotfix, prior scoped installer or unauthorized drift; DO NOT relabel an unexplained mismatch as safe. Scan `overlayReceipts`, approved historical commit/receipt, actual installed file and narrow source history to determine provenance, without following links. Equivalent triple binding for `supply_exporter.py`, `alpix_batch.py`, `studio_extensions.py`, solver/optimizer and launcher. Distinguish missing manifest owner vs known owner vs owned-but-unapproved overlay path.
2. Create a dependency-closure graph for launcher → Studio extension → optimizer → exporter → verify → solver runner, plus ALPIX/PixelLab; determine exact minimal file update set. Check version/ABI/source contracts between `verify.py`, `supply_exporter.py`, `studio_extensions.py`, `scrubbots_solver.py`, `supply_optimizer.py` and `solver_budget.py`.
3. Make narrowly justified, **transactional, auditable**, allowlist-and-manifest-aware installer improvements only if root cause is proven. Do not silently approve the installed `90e560...` hash, rewrite expected SHA without provenance, copy an unowned file, widen to all managed files, or bypass hash ownership verification. Require preflight plan including source/installed/manifest triple hashes; support no-op for exact unchanged files, fail-closed on unrecognized divergence, all-or-nothing pre-stage + backup + rollback + post-hash verification. Never edit owner Release bytes merely while investigating.
4. Source fix may be safely committed and normal-pushed before native/installed acceptance, with focused test mocks for owned drift vs unauthorized drift, missing/old managed files, process-active prevention, transaction rollback, two newly scoped dependencies, zero protected-owner-file mutation. If genuine provenance is indeterminate, STOP DEPLOY and report `INSTALL_BLOCKED_MANIFEST_DRIFT` but finish safe code/tests/log publication. Do not claim resolved until reproducible clean preflight against actual installed manifest.
5. If a work directory needed for tests, use only the pre-existing owner-allowed repository location and bounded no-cache execution; do not invent TEMP exceptions.

## Phase 2: Native Godot 4.7.2 safety and process validation

- Genuine installed Godot binary reported `4.7.2.stable.official.ed1daf0bf`; the builder did NOT parse/run the owner Godot project. `.uid`, `.import`, `.godot` or generated import/cache writes in the protected Desktop project are unacceptable side effects. Read `--help` and actual script/project dependency paths to decide if there is an existing **provably read-only** bounded native parser/test invocation. No fresh copy, TEMP tree/worktree or conversion, no destructive cleaning of existing owner assets.
- If a safe native run is **provably possible**, protect read-only hash baselines and execute focused native parser/scene/GUI or native solver test WITHOUT touching original 140 PNG, Release Pool, source files or paid providers. Check same real PID/invocation 240s soft → 480s total and no second native solver, manual cancel/early result/timeout, parent/child handling, stdout orphan/IPC. Do not assume test can be completed in a short time and do not start unbounded runs. For acceptance of 480-second behavior, evidence must genuinely reach boundary or use a controlled native accelerated-clock harness whose validity is explained; Python fake clock alone never equals real process proof.
- If native safety cannot be proven, truthfully record `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK`, list exact write paths/attempted nonmutating alternatives and remaining requirement. Continue safe source/installer improvements and publish them. Do not mark native PASS and do not bypass by new workspace or implicit owner-file modification. An owner decision is needed before accepting a method that modifies their protected working project; do not ask for broad permissions if an exact narrow route can be proven safe.

## Phase 3: Scope-limited installed application and owner GUI

Only if Phase 1 manifest ownership/preflight AND Phase 2 mandatory native gate (if required by original V13 strict acceptance) can be satisfied:
- Prove no actual owner Factory Studio or writer using executable + commandline + parent identity, not stale PID; request normal UI close only if there is a real active writer; **never kill, suspend or edit in-place live worker**.
- Use approved existing `scripts/install_factory_studio_scoped_overlay.ps1` only after safe targeted modifications, explicit `PREVIEW/PREFLIGHT` then narrow transactional `Apply`; no broad reinstall, no duplicate shortcut. Verify rollback on failure and managed file/manifest hashes after. Rehash the original job and Pool and compare exactly to baseline.
- Real installed cold start screenshot owner check at PIXEL ART / LEVEL FACTORY / RELEASE POOL: no active Style/Magnific, real selected Size `W×H px`, truthful ALPIX plugin and PixelLab credential statuses without charge; COMPLETE batch 102/4/34/0, stale Resume104 absent, searchable/scrollable 38 exact issue rows and SHA-bound preview/reasons, unchanged Release Pool, actual 1536×1024 and smaller layout. Test only normal UI navigation, not Generate/Resume/Publish. Existing R09 geometry issue stays open until truly tested and fixed.
- **Never declare V13-C installed acceptance** from source import success, preflight alone, Python AST, or mock UI screenshots.

## Phase 4: Delivery

Append exact chronological timestamps, start/end SHA, commands, failures (including known missing owner-fixture test), before/after managed file/Pool/job SHAs, dependency closure, native evidence and opened gates to existing M03 builder log; source/test changes and builder log in separate commits when practical. Recheck current origin ancestry and manual-only workflow. Push **normal fast-forward only** (`git push origin HEAD:main`); fetch again and verify HEAD==origin/main, 0 ahead/behind, task tracked tree clean. No CI. If origin advances or unsafe, preserve all work and record exact blocker without rebase/force.

Report short coded outcome `V13_CD_SOURCE_ON_MAIN`; `MANIFEST_DRIFT_DIAGNOSED` plus status of safe scoped installer; `NATIVE_GODOT_PASS` or `NATIVE_GODOT_BLOCKED`; `INSTALLED_GUI_PASS` or `INSTALLED_GUI_OPEN`; protected 140/102/job SHA/Pool tree; test evidence and failures; exact GitHub code/log commits and real builder-log URL. **Do not edit TASKS.md or GPT audits.** Independent GPT review and owner screenshots remain final acceptance gates.

**Execution style:** Continue through every safe available engineering action in one session rather than stopping for routine acknowledgments. Stop *mutations* only at real technical/owner-data safety boundaries; do not invent evidence or spend extra quotas.
