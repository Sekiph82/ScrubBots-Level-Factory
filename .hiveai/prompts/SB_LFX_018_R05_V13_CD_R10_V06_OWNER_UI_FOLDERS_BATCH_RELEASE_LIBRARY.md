# SB-LFX-018 R05 V13-C/D R10 V06 | OWNER PIXEL ART UI + PERSISTENT FOLDERS + FOLDER BATCH + STATUS-SEPARATED RELEASE LIBRARY

**Document role:** AUTHORITATIVE OWNER-APPROVED CODEX BUILD PROMPT
**Approved scope:** Owner's 2026-10-30 screenshot-review conversation: first complete THREE existing dirty UI/test modifications, then all requested directory, layout, bulk folder selection and release library changes, including separate REJECTED vs FAILED, then continue the ongoing project goal. The owner explicitly said: "rejected klasoru failed ile farkli olsun ... tum isteklerimin hepsini yap ... onceki ... yerel ui/test degisikliklerini de tamamla ... sonra ... goale devam et".
**Repo:** https://github.com/Sekiph82/ScrubBots-Level-Factory
**Only working tree:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
**Branch:** main, standard nonforce push `HEAD:main`.
**Existing runtime:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`.
**Authority:** root `TASKS.md` and this prompt. GPT owns `TASKS.md`, independent audits and active prompt; **Codex NEVER edits these**.
**Builder log:** append ONLY to existing `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`; add one concise fresh process report under `docs/process/` if needed.
**Current remote baseline when authored:** `3cdf49f449836e1b6ee346d6f3b49511b9d495a1`; fetch current main, do not assume static SHA.
**Existing source:** 2026-10-28 R10 V05 managed Release and real Godot 4.7.2 PIXEL ART, PixelLab Pro key/GUI, 16x 56×56 synthetic atlas import reported PASS. As of 2026-10-30 recent main already has ALPIX capability safety guard and newer code. Preserve work, inspect actual current state; DO NOT redo R10 V02–V05 as if not completed. Pollinations is CANCELLED and must NOT be added or re-enabled.

## REQUIRED ORDER, especially recovery from dirty canonical Desktop checkout

### PHASE 0. Preexisting uncommitted owner UI/test work FIRST, without queue guard bypass

Codex's 2026-10-30 local inspection documented EXACT three preexisting tracked modified paths:
1. `level_factory/scripts/factory_studio_exact_ui.gd`
2. `tests/unit/test_sb_lfx_018_c001_r02_master_control_bindings.py`
3. `tests/unit/test_sb_lfx_018_r05_v13_offline_regressions.py`

The standard `python -B scripts/codex/scrubbots_task_queue.py --json` currently returns **"Tracked working-tree changes exist; refusing to start an automated task."** This is **expected with owner's uncommitted previous work**, not permission to delete it, reset it, tamper with guard, fake a clean status or create another clone. The owner now explicitly authorized the narrow recovery/finishing of those three modifications **as phase 0 of THIS task**.

1. At the canonical Desktop path, capture read-only `git status --porcelain=v1`, `git diff --name-status`, `git diff --check`, precise diffs and baseline SHA for each of these 3 files; `git fetch --prune origin` and inspect HEAD/origin/main ancestry and incoming touched paths. Also inspect any other dirty/untracked paths without touching them. If additional owner edits exist, preserve and report them, never group-stage.
2. Verify that safe `git merge --ff-only origin/main` is possible **without overwriting any dirty bytes**; if incoming remote commits touch any dirty path, STOP only unsafe sync, preserve the exact files and report path/SHA/conflict; do not invent an alternate worktree. No forced or destructive operation.
3. Inspect the exact previous unfinished UI/test code and owner's requirements; **complete the existing changes** and run the focused tests / native checks relevant to these three paths. Do not commit half-working code as PASS. This phase's implementation and its test evidence should be one precisely staged commit/commits, not an indiscriminate `git add .`.
4. Because queue guard intentionally rejects dirty tracked work, do not rerun it repeatedly or modify guard logic. Document the owner's explicit bounded Phase-0 exception and queue refusal in the same append-only builder log. After the three existing files have been safely finished, committed, synced, and the tracked checkout is clean, **run the normal queue guard for R10 V06**. It must confirm exactly one identical authoritative URL in `Next Task/Action` and `Current Task`. If this initial recovery cannot be done safely, preserve all work and report the exact blocker; do not overwrite or leave unpublished commits.
5. At EVERY Phase-0 and subsequent phase completion, perform the mandated normal safe main push, fetch, exact `HEAD == origin/main`, 0 ahead/0 behind, clean tracked tree verification; publish append-only log receipt too. This is required before next phase or next goal task.

### PHASE 1. OWNER'S CANONICAL PIXEL ART PERSISTENT PATHS

Create/activate the following **exact owner-visible folder layout** under the sole canonical repo (subfolders are local runtime data and not bulk Git assets):

```text
data/
  input/                              # Owner CSV files for pixel-art batch jobs
  output/
    Alpix/                            # Finished ALPIX PNGs
    Pixellab/
      Grid Files/                     # Original provider 4x4 atlas PNGs
      Final/                          # ALL sixteen separately sliced PNGs per atlas
    Owner Suggestions/                # Owner manually supplied images
  Release Pool/
    Pending/                           # SOURCE_ONLY or awaiting solver/QA; NEVER mislabel READY
    Ready/                             # Only canonically verified READY
    Failed/                            # Valid input but solver/replay/difficulty/technical failure
    Rejected/                          # Invalid source, format, palette, geometry, owner reject
```

Do not silently rename the exact case/spacing. In the UI the owner may see labels ALPIX/PixelLab; filesystem uses requested names exactly.

- User `data/input` holds selected CSVs, not unattended paid service triggers. Wire ALPIX batch CSV selector/preview to this location. Only run generations after an explicit authorized trigger; no paid/remote call automatically. Observe previous ALPIX capability guard and do not claim canvas-only plugin yields PNG. If provider unavailable, status stays truthful.
- ALPIX's verified standalone generated PNG goes to `data/output/Alpix`, preserving transparent PNG, dimensions, SHA, operation/provenance and status. If standalone PNG is unsupported by actual connected tool, do not fabricate one.
- PixelLab Pro output: immutable ORIGINAL normalized 4×4 atlas in `data/output/Pixellab/Grid Files`; ALWAYS sixteen exact row-major PNG slices into `data/output/Pixellab/Final`, with manifest mapping atlas SHA -> 16 individual SHA, width/height, palette/alpha/used-color checks. The default atlas is 224×224 (16×56×56), but a legally selected 51..59 sprite makes 4W×4H; do NOT hardcode 224 for all modes. Never resize to cheat geometry, nor overwrite a prior atlas with the same name but different bytes. Preserve PixelLab R10 V03 atomic billable digest guard, R10 V04 credential preflight and REAL generated job ledger.
- Owner-provided PNG files can be placed in `data/output/Owner Suggestions`; don't alter their original bytes or silently infer provider.
- Source factory internals already use `level_factory/output`, project root `output`, and existing content-addressed OWNER_UPLOAD records. Keep internal evidence intact and build a deliberate consistent **copy/receipt or source-of-truth mapping** to the requested `data/output`. The new owner-facing paths should be the canonical persistent art catalog, but never bulk-move/delete unknown old folders, nor replace established solver/importer authoritative paths without compatibility tests. Confirm existence of each target (local untracked may already exist) before creation and never overwrite owner data.
- Update .gitignore narrowly so generated PNG/CSV source data, approval records, local Release Pool archives and credentials are not accidentally committed; track only safe code/config and optional empty folder markers. No generic ignore swallowing source files.

### PHASE 2. OWNER'S FOLDER-BASED LEVEL FACTORY BULK INTAKE

Implement a real, accessible **Select Folder / Import Folder** flow within the installed LEVEL FACTORY page. The owner must be able to choose a provider/source:
- **ALPIX** -> `data/output/Alpix`
- **PixelLab** -> ONLY `data/output/Pixellab/Final`
- **Owner Suggestions** -> `data/output/Owner Suggestions`

Allow an explicit safe alternative folder selection only when the owner chooses it. Default selection scoped to each approved source. Never scan/download all Desktop or blindly recurse outside approved root. Identify PNGs by actual file type and real PNG validation, deterministic filename sorting, bounded count (respect currently supported 150-source snapshot maximum per batch, or transparently page large batches), and present count/preview/status before confirming.

**Hard exclusion:** `data/output/Pixellab/Grid Files` holds RAW 4×4 ATLAS, NOT a single level artwork. Never import raw atlas as a single level! It can only enter via explicit PixelLab atlas splitter -> Final. Do not let a recursive parent scan traverse Grid Files unintentionally. 224×224 is NOT an authorized single gameplay PNG; game max 59×59.

Import through existing canonical `batch_import` / `OWNER_UPLOAD` source hashing and `loaded-png-batch`, `png-batch` or equivalent actual current pipeline. Don't invent a second solver or circumvent solver/WIN/difficulty/VOID/QA gates. Use content SHA-256 + verified source ID + stable import ledger to classify:
- new file
- previously imported identical file (SKIP, don't repeat)
- same filename with different bytes (separate source ID; flag collision)
- exact same bytes in another source folder (show as duplicate, no second processing)
- invalid or missing file (REJECTED reason)
- status known from canonical prior processing (do not downgrade or treat SOURCE_ONLY as READY)

On repeated folder import, **zero previously processed files must be reprocessed automatically** even if original source PNG remains in its source folder. Include interrupted/restart and concurrent duplicate scenarios. A valid owner-requested retry is an explicit operation with a new run record and prior lineage, not a silent duplicate.

UI requirements: folder picker and provider selector; selected folder/path; PNG count; imported/skipped/failed/rejected counts; per-file reason and SHA-bound source identity; progress, pause/cancel using existing controls without blocking Godot. Do not reprocess original 140 at any point; preserve 102 READY/4 FAILED/34 REJECTED and existing Pool 131 source evidence. Bounded new fixtures only.

### PHASE 3. STATUS-SEPARATED OWNER RELEASE LIBRARY (IMPORTANT: FAILED != REJECTED)

Owner requested `data/Release Pool` to contain an independent per-PNG record (PNG + corresponding solution/plan/reason/evidence when available) for **every NEW Level Factory import**, with status separated. Build this as an **owner-facing status/provenance archive** and retrieval UI, NOT a replacement or bypass for existing canonical production-ready authority `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py::enter_release_pool`.

Directory status meanings:
- `Pending`: SOURCE_ONLY / UNVALIDATED, incomplete solver, active/review required. No fabricated solution.
- `Ready`: only when canonical pipeline has genuine solver+replay WIN+difficulty+QA evidence, and the existing release eligibility and owner-review rules are satisfied; READY can be offered to the existing approved publish route, **never publish automatically**.
- `Failed`: structurally valid artwork that failed solver, timed out, replay WIN, difficulty, QA or other reproducible execution stage. Show exact error and run/provenance; owner may select **Retry Failed** in LEVEL FACTORY to run a new approved attempt, conserving prior immutable evidence. A retry may promote to Ready only after new real proof.
- `Rejected`: art/format/alpha/palette/geometry contract rejection or explicit owner rejection. Keep distinct folder, distinct state, exact reason and provenance; do NOT feed to solver retry until a separately reviewed corrected source/new version is created. No silent move to Failed.
- A file's latest status can change only by a verified new transition. Preserve immutable historical status and run evidence. Do not destructively move source PNG files or overwrite existing history; use durable atomic ledger + immutable content-addressed objects/record links, derived indexes/views and one active status projection without duplicates.
- Every included record must bind source SHA, source ID, original provider/path, corresponding per-PNG solver plan/result if generated, current status, reason, pipeline run ID, retry lineage, version, timestamp and every relevant proof SHA. If solution is missing, explicitly state `NOT_AVAILABLE`; do not invent or copy another source's solution.
- Repeated import must yield no duplicate `data/Release Pool` entries. The original provider source copy may remain in its source folder; the source status/ledger prevents processing again.
- Never auto-publish to game/R2 and never import incomplete entries into the existing canonical READY pool. Use a distinct folder/manifest namespace to avoid aliasing `level_factory/output/studio-extensions/release-pool` (which supports READY only); make distinction visible in UI/docs.

### PHASE 4. PIXEL ART GUI LAYOUT CONTRACT

Complete the owner's screenshots-derived fixes and existing pending UI/test modifications from Phase 0:
- In the PixelLab provider selection dialog, the explanatory text and provider selection UI **must never overlap**. Make both fully readable using actual size constraints and a scrollable region if required. Keep keyboard/focus order working.
- When PixelLab Pro is selected, the right **details section must never encroach on artwork cards/gallery**. At all supported window sizes and whether details text grows/shrinks, keep an **EXACT fixed 38 native screen pixel vertical gap** between the bottom of rendered details content/panel and the TOP of artwork area; measure runtime coordinates after responsive layout, not only source arithmetic. Long content should scroll or clip within a constrained details container, never compress the gap. Avoid 38 scaled pixels.
- **ALPIX screen's currently correct layout must not change.** No regression to its provider card, details, artwork area or widgets.
- Add/modify focused source/layout tests and **real installed Godot UI screenshot/geometry evidence** at representative window sizes. Validate actual user UI, not merely static text. Do not claim pixels verified if native GUI not run.

### PHASE 5. SAFE INSTALL, TEST, SYNC, THEN CONTINUE OWNER GOAL

- Install only necessary changed code to the EXISTING managed Release via current approved scoped overlay installer, manifest receipt SHA checks, genuine Windows writer exclusion and rollback. Inspect source-vs-installed parity and installed dependencies (new modules must be included). Never bypass known manifest drift, never blanket replace the Release, never kill unrelated Godot processes. Actual Godot 4.7.2 native GUI check required if safe; if blocked, report exact status and continue independent authorized source work.
- Test on small synthetic **new** PNG/CSV fixtures: source-folder routing and no accidental Grid Files intake, sixteen PixelLab final PNGs, folder picker, skip on second import, same filename/different SHA, restart-resume, distinct Failed/Rejected, Pending->Ready only after genuine solver/WIN/QA, separate manual Retry Failed and preservation of history, absent solution recorded honestly, byte-for-byte preservation of original 140 and existing pool; real Godot PIXEL ART geometry and LEVEL FACTORY UI.
- No PixelLab paid generation, no ALPIX remote drawing/generation, no CI/Actions, no R2/prod release, no unknown external network billable action without fresh explicit owner authorization. Preserve historical 18 stashes and all owner untracked files; do not clean `.pytest_cache`, `.pytest-scratch-*` or `.sb-lfx-v12-hang-test-runtime` without exact inventory + separate deletion approval. Prevent new permanent test scratch, caches, large output. Keep all test artifacts bounded inside owner-approved repo-local test scope.
- **After EVERY complete subtask**: commit exact source/tests, separately append builder log/report, `git fetch --prune origin`, prove origin/main ancestor, normal `git push origin HEAD:main`, refetch, `HEAD == origin/main`, 0 ahead/behind, tracked clean, and installed managed checksum parity if task touched Studio; then proceed. If publication and local Desktop diverge, no next dependent subtask until safe recovery. No `git reset --hard`, `git clean`, `git rebase`, force push, auto stash, new clone/worktree/TEMP copy.
- Publish concise per-phase evidence with each status `PASS`, `PARTIAL`, `BLOCKED` or `NOT_RUN`, actual command, number of test cases, source/installed checksums, native screenshots if performed, GitHub+canonical Desktop HEAD. Once this owner-requested work is complete, return to the broad standing Claude goal and genuinely pending root `TASKS.md` items WITHOUT repeating prior milestones. GPT retains independent audit/task closure authority; Codex leaves `TASKS.md` and `.hiveai/audits/` intact.

**Strict completion:** pre-existing 3 tracked diffs safely completed/published, real GUI layout fixed with 38px invariant and ALPIX intact, new owner folder routing and 16-sprite permanent catalog, LEVEL FACTORY batch-folder import, dedupe/skipping proof, Pending/Ready/Failed/Rejected distinctly manifested with solution only if available, installed Factory Studio verified, and per-task GitHub/Desktop parity.
