# SB-LFX-018 R05 V13-C/D | Independent GitHub Source / Publication Audit V16

**Date:** 2026-10-21 (Europe/Istanbul)  
**Document role:** GPT INDEPENDENT AUDIT (read-only GitHub review; not Windows/native execution)  
**Repository:** Sekiph82/ScrubBots-Level-Factory  
**Audited publication head:** `29d0360033643eacec36d732415fa21b0697bcd9`  
**Overall decision:** **SOURCE PUBLICATION VERIFIED; LOCAL TEST RESULTS BUILDER-REPORTED; V13 INSTALLED/NATIVE ACCEPTANCE OPEN.** Do not mark V13 complete.

## 1. Publication provenance and preserved local changes

GitHub's commit comparison `ef0fbf643e398892f5866cb29d572089475bb41d...29d0360033643eacec36d732415fa21b0697bcd9` returns **ahead 6 / behind 0**. Verified these six main commits exist, in sequence: `d247b82f3c2d2c60447b16a3984a2da5e8b26abc` (product/tests); `c6951462ad9ed0c596a5c4465d3f32519549bd4b` (existing builder log); `41b474dd7ea23877bc3e821fbd243d20ca3b1db7` (log); `7bf85b286b5ae0bcb2c05614e5709e86c2ee8b25` (follow-up product/tests); `535969d9bdd517600e141448018bebbd5c509d0b` (log); `29d0360033643eacec36d732415fa21b0697bcd9` (final log). Source paths are not concealed by the builder log.

Original local objects `04c9f40`→`d247b82`, `8597265`→`c695146`, `94c71d7`→`41b474d` are **builder-attested** as bytewise matching the original product tree; direct Github inspection independently proves the integrated remote commits and files, but not the original unpublished Desktop worktree bytes. The builder reports local HEAD/origin equality at `29d0360`, 0/0 and clean tracked tree. This Windows claim is not independently observable via the GitHub connector.

Reviewed GitHub paths include `studio_extensions.py`, `solver_budget.py`, `scrubbots_solver.py`, `supply_optimizer.py`, `supply_exporter.py`, `verify.py`, the staged solver unit test, the existing R09 solver contract test, the scoped installer, and the chronological M03 builder log.

## 2. V13-D source design findings

- **PASS, source-design inspection:** `solver_budget.py` keeps the original 240s maximum input and exposes staged normalization with 480s absolute hard budget only for an attested runtime. `staged_solver_deadline_state` returns RUNNING, EXTENDED, TIMEOUT across exact 240/480 boundaries.
- **PASS, source-design inspection:** `scrubbots_solver.py` launches one pinned native process for a single attested candidate, tracks request/plan/source SHA, records EXTENDED and PID/progress, then bounds the same process to the absolute hard deadline and supports a scoped process-tree cancel. `supply_optimizer.py` accepts `max_native_solver_invocations=1`; `studio_extensions.py` supplies that for the pinned path.
- **PASS, source-design inspection:** The follow-up GitHub code change connects exported `verify_exported_supply(...,solver_evidence=...)` to already completed solver evidence and avoids the previous second native call on the pinned exported-plan path. `verify.py` validates one invocation, successful exit/loader status, source SHA where present, logical-level hash, ordered supply and Difficulty V1 evidence. No evidence was gathered that this has yet produced an actual pinned Godot SOLVED+WIN run.
- **BOUNDARY/OPEN:** `test_sb_lfx_018_v13_staged_solver_deadline.py` fake clock/process tests exercise helper-level transitions; they are not an actual `Popen` + Godot process lifecycle or OS descendant cleanup. The builder explicitly reports missing native process/possible orphan proof.
- **BUILDER TEST EVIDENCE ONLY:** Earlier 23 focused PASS + 16 subtests; follow-up focused 13 PASS +16 subtests. A broader run failed because the owner source fixture was absent, and that failure remains unclosed. Tests were **not rerun** by the independent auditor; no whole-suite PASS claimed.

## 3. V13-C managed Release gate remains BLOCKED

The published `factory_core_launcher.py` imports `pixellab_secret_status` from manifest-managed `studio_extensions.py`; separate `provider_credentials.py` was deleted from SOURCE. The owner-local builder read-only check reports installed ALPIX module `alpix_batch.py` present, manifest-managed, exact installed/source SHA `e1059e832152829c0874b15958f1fa0be61fe20beccf218df3fefede4aad7282`, and source-free imports tested using `python -B -S`. These local facts cannot be independently confirmed without the owner's Windows Release runtime.

**Hard, specific blocker:** `src/scrubbots_pixel_factory/supply_pipeline/verify.py` is reported in the installed manifest as SHA `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2`, but actual installed bytes hash to `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744`. Published `scripts/install_factory_studio_scoped_overlay.ps1` omits both `verify.py` and `supply_exporter.py` from its explicit `relativePaths`; automatic correction is not proven safe. This is **INSTALL_BLOCKED_MANAGED_DEPENDENCY / MANIFEST_DRIFT**, not permission to overwrite, update manifest hashes to whatever is present, or broad reinstall.

Before deploy, the next builder must establish actual provenance of installed `verify.py` divergence and manifest ownership/overlay allowance for both newly changed modules; produce a narrow source/installed/manifest triple-SHA inspection and rollback plan, and only then consider a scoped transactional change after exact process/writer quiescence. Do not add a permissive global mismatch exception.

## 4. Native, GUI, protected data

**NOT RUN:** real Godot 4.7.2 project parsing/editor/GUI, native solver, real process-tree/orphan tests, installed PIXEL ART / LEVEL FACTORY / RELEASE POOL GUI screenshots. Builder reasonably preserved owner `.uid`/import/cache files rather than claiming such tests passed. A safe native route must not silently manufacture a TEMP clone/worktree or mutate owner cache.

Owner-local read-only receipts record immutable job `png-batch-875545d48a14a0d6b4d542f554919e8d`: COMPLETE=140 / READY=102 / FAILED=4 / REJECTED=34 / remaining=0; JSON SHA `33c11885032f9b9b6050ea642c4870e04e8424dacc00de749b51234ce9f94193`; state digest `56823da1561858e6275e180b0c766b46daacf6f735e7200cfce47b0369d98490`. The owner-local Release Pool reports **131 JSON files** (NOT 131 READY entries) and tree SHA `e227c95f85635a48522dbdd5aefeb2ead51f2e25070fb8f4b315746ebbc9a81d`. Values are builder evidence only; no owner runtime files were available to the independent GitHub auditor. Existing V15 separately reviewed all **38/38** user-uploaded issue PNGs; no new PNG requests, reclassification, palette repair, retry or 140 replay.

## 5. Acceptance verdict and next authority

- `V13_CD_GITHUB_PUBLICATION_VERIFIED`: **PASS** (GitHub commit graph/source/log).
- `V13_D_STAGED_240_480_SOURCE_DESIGN_REVIEW`: **SUPPORTED** by inspection; **real native/process acceptance OPEN**.
- `V13_C_INSTALL_MANIFEST_DEPENDENCY`: **BLOCKED**, exact installed `verify.py` mismatch + omitted `verify.py`/`supply_exporter.py`.
- `V13_NATIVE_GODOT_4_7_2`: **NOT RUN**; owner cache/import-write risk.
- `V13_INSTALLED_GUI_OWNER_PROOF`: **OPEN**.
- `V13_140_JOB_AND_POOL_IMMUTABILITY`: owner builder read-only report, not independent runtime rehash; continue protecting.
- `V13_MILESTONE_COMPLETE`: **NO**.

**Next builder task (same V13-C/D continuation, no reimplementation):** narrowly diagnose/de-risk manifest drift and exact three-file dependency closure, create only an evidence-based scoped transactional installer fix if safe, determine a truly owner-safe native check (or explicitly retain BLOCKED), then obtain real installed 3-screen GUI proof. Keep full R09 preexisting geometry/fixture failures visible. No GitHub Actions/CI, no paid provider, no clone/worktree/TEMP, no owner file deletion, no solver/140 batch rerun and no source/image fixes without new owner authorization. GPT remains the independent auditor and sole `TASKS.md` task-state editor.
