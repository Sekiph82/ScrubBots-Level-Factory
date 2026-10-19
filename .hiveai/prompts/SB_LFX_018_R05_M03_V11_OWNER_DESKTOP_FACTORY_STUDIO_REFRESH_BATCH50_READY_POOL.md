# SB-LFX-018 R05 M03 V11 | Owner Desktop Factory Studio Refresh + 40–50 Level Intake

**OWNER AUTHORIZATION (2026-10-19):** The owner explicitly wants the existing desktop **ScrubBots Factory Studio** application/shortcut updated to current validated Factory code so they can personally input/import and solve approximately **40–50 new levels**, which should enter the **Release Pool if and only if actually READY**. This overrides the previous "run campaign dry-run first" *priority*, but **does not** authorize any campaign assignment, publication, PRODUCTION upload, creation of 40–50 fake levels, mass deletion, CI or changing owner PNGs.

Repository/branch: `Sekiph82/ScrubBots-Level-Factory/main`.
**ONLY** local development checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
**EXISTING** installed application: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`.
**EXISTING** desktop shortcut: `C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk`.
Shortcut should reference the installed `scripts\launch_factory_studio.ps1` via Windows PowerShell and preserve the owner's approved icon `ScrubBots_Factory_Studio.ico`.
Codex MUST NOT create another desktop shortcut, a parallel app copy, a new worktree/clone, or a TEMP installation. Only user-visible output is the same updated app/shortcut.

## 1. Read actual authority before doing anything

- Read **latest** root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, `docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md`, `docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`, `docs/decisions/OWNER_PIXEL_ART_ALPIX_READY_AUTO_POOL_V01.md`, source of `scripts/install_factory_studio_shortcut.ps1` and `scripts/install_factory_studio_ui_overlay.ps1` and `scripts/launch_factory_studio.ps1`.
- Inspect actual installed `.factory-studio-install-manifest.json`, `sourceRevision`, `installationMode`, `managedFiles`, `overlayPaths`, controller and launcher hashes, owner icon hash, existing `.lnk` target/args/working directory/icon, and source/Release runtime existence. **Read only** initially. Record clear before/after IDs, omit secrets.
- Verify exact canonical Git origin, branch, clean tracked status, `HEAD`, `origin/main`; `git fetch --prune origin`, fast-forward ONLY when safe. Preserve all existing untracked owner inputs. Do not force-reset or create new worktrees.
- Determine existing active Godot/Factory Studio process **without reading unrelated processes**; if it is running, ask the owner to close the Studio normally using **X** before touching installed managed runtime files. Never kill the app or force-close it.
- **Important installer caution:** Current generic `scripts/install_factory_studio_shortcut.ps1` enumerates *ALL* repository tracked files for managed install, stages them, may remove prior managed runtime files, and its manifest contract is not necessarily compatible with the owner's existing `OWNER_APPROVED_SCOPED_OVERLAY` runtime/manifest. Historic `install_factory_studio_ui_overlay.ps1` has fixed revision/SHA constraints and is not a universal updater. **Do not blindly run either installer or overwrite the full installed Release**. Evaluate exact installation mode and all protected files. Protect `Release` owner data, source candidates/reviews, nine existing READY levels, 17 historical Pool entries and icon. Use the *smallest transactionally safe, manifest-aware update* of runtime files needed for the latest verified Studio; content data and historical accepted records must remain byte-identical. If no safe compatible updater exists, implement/test a **narrow additive idempotent updater** in the canonical checkout, commit it to GitHub main first and use it only after dry-run collision/hash/rollback preflight. On failed preflight, **NO WRITE**, report exact blocker and owner action.
- Refuse hidden second full-project installation, multigigabyte Git/Release duplication, or deleting untracked owner files. No global Python environment reset; no `scripts/setup.ps1` because it clears existing `.venv`. If staging is essential, do it under the approved installed runtime with quantified, bounded footprint, rollback and documented cleanup. Never evade policy-blocked operations.

## 2. Ensure the EXISTING Studio works for owner's 40–50 PNG/level batch

Do **not** create or process new levels on the owner's behalf yet: owner will bring their own 40–50 PNGs or select existing artwork and initiate the batch in the GUI.

The installed Studio must have the same real functional three-screen flow:

`PIXEL ART` → `LEVEL FACTORY` → `RELEASE POOL`.

A. In LEVEL FACTORY, confirm **multiple external PNG selection** and existing CSV/batch inputs work (where already supported), same for transfer from PIXEL ART, using **real selected images**, not art fixtures. Keep source PNG identity/hash and VOID/transparency authoritative, no synthesized palettes or mismatched bundle associations. `Level Number = Auto` by default, 3/4/5 supply-column choices respected (default 3), visible preview rows 3.

B. Every item must independently run actual existing canonical stages: validation → primary ZIP/supply optimizer → current authoritative game solver → native replay/WIN → official Difficulty V1 → QA/load check → immutable candidate bundle → canonical `READY` or explicit truthful failure/timeout. Do not mark unsolved as READY. Honor existing per-stage timeout/budgets, cancellation and idempotent retry. Never fake `current game` source authority; if authentic game executable/input is missing, report the specific blocker instead of using a fake stub.

C. Per `OWNER_PIXEL_ART_ALPIX_READY_AUTO_POOL_V01`, each genuine `READY` item **automatically appears in Release Pool**; `OWNER_ACCEPT` is **not required for pool inclusion**, and `Reject` excludes/ `Accept Level` restores it. This latest 2026-10-09 decision supersedes earlier generic 2026-10-02 wording that owner ACCEPT is always required for pool entry. **No READY item automatically publishes.** Do not assume 40–50 inputs yield 40–50 READY outcomes.

D. Show truthful **batch progress**, per-source status `READY / FAILED / INCONCLUSIVE / RETRYABLE / LIMIT` consistent with existing UI, and resumable results on restart where supported. Verify duplicate source hashes do not add duplicate releases or reorder existing candidates; failed items do not consume final campaign order. Never silently rewrite owner-002 original, seed92, older accepted/rejected items, or override historical Release Pool hashes.

E. Owners should be able to select/review genuine PNGs and pool counts through the installed `RELEASE POOL` tab after the update. **Do not invoke Publish, Upload, STAGING, PRODUCTION or any campaign plan approve on the owner's behalf.** 40–50 incoming READY levels are **candidate pool**, not automatically the exact 11–60 game levels. CampaignBuilder must later choose the next contiguous allowed order starting **11**, honor class cadence, official difficulty ±3.5 default / ±5 hard, profile/recovery/novelty, and require separate owner approval.

## 3. Safe validation and update

- Prefer source/read-only manifest tests and small focused tests over a new full game clone or huge complete suite. Use documented Godot 4.7.2 only when required for Studio smoke test. Test latest Studio launcher/shortcut against **existing installed Release project** without changing owner product data; make sure actual `.lnk` targets installed runtime, not source `level_factory` or a deleted TEMP tree. A launcher `ResolveOnly` check plus targeted GUI open only after owner has closed old session are appropriate. Do not claim the owner's UI works until truly observed.
- Preserve existing desktop shortcut name and icon; repair/refresh it **in place if needed**, not by adding another link. Avoid metadata-only shortcut refresh if both shortcut and installed runtime already match current approved build; in that case report `ALREADY_CURRENT` and ask owner to open it.
- For any changed managed file: published source SHA, previously installed owner/manifest SHA, pre/post SHA, transactional rollback, no untracked collisions, exact install receipt. If updater fails or process is active, keep installed app unchanged and report `OWNER_CLOSE_APP_REQUIRED` or `MANAGED_INSTALL_CONFLICT` with exact file; no brute force fallback.
- No test or installation may start 40–50 solver runs automatically. Owner starts real batch via UI after final link is ready. Avoid building a new feature if working batch already exists; if multi-PNG UI is genuinely broken, make the smallest test-proven correction and deploy through same safe existing Release update.
- Record final exact `HEAD == origin/main` parity, tracked clean, installed revision/source+controller/launcher hashes, stable shortcut target/args/project path/icon, true READY pool count before/after (should **not** change merely because app updated), app-open readiness or remaining hard blocker, and owner one-paragraph action instructions for selecting multiple PNGs, pressing Run Pipeline, reading statuses and verifying Release Pool. No duplicate install or huge disk residue.

## 4. Publication/owner handoff

Publish only narrow code/test or updater modifications (if needed) and **append** authentic builder findings to the **existing M03 builder log**:
`.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`.
Do not change root `TASKS.md`, prompts, audits, HANDOFF, owner originals or the game repository from Codex; those are separate authority. ChatGPT handles task/audit acceptance once real Windows installer/shortcut evidence is shared.

**Final status must be one of:**
`OWNER_DESKTOP_STUDIO_UPDATED_AND_SHORTCUT_VERIFIED`,
`OWNER_DESKTOP_STUDIO_ALREADY_CURRENT`, or
`OWNER_DESKTOP_STUDIO_UPDATE_BLOCKED:<exact cause>`.
`BATCH50_READY_POOL_UI_VERIFIED` only if genuinely tested; otherwise `BATCH50_PENDING_OWNER_GUI_CONFIRMATION`.

**Do not** confuse this setup task with M03-F01 actual Level48 campaign placement, Level11 seed92 OWNER_ACCEPT, or completed CPX001/STAGING/CPX002 proof. All production remains prohibited.
