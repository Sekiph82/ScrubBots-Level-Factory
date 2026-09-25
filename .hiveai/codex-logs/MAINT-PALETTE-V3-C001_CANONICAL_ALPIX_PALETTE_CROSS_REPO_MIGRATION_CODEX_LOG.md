# MAINT-PALETTE-V3-C001 — Canonical Alpix Palette Cross-Repository Migration
Document role: CODEX BUILDER LOG

## Chronology

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Canonical repository/root: `Sekiph82/ScrubBots-Level-Factory`, `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Cross-repository target: `Sekiph82/Scrubbots`, `C:\Users\sekip\Desktop\ScrubBots`.
- Authoritative prompt: `.hiveai/prompts/MAINT-PALETTE-V3-C001_CANONICAL_ALPIX_PALETTE_CROSS_REPO_MIGRATION_PROMPT.md`.
- Canonical palette authority: `Sekiph82/Scrubbots/data/palettes/scrubbots_palette_v3.json`.
- Starting branch: `main`; Level Factory starting HEAD after safe fast-forward: `383bdb6`.
- Starting Scrubbots HEAD after safe fast-forward: `eab38e9`.
- Both repositories were fetched and fast-forwarded only; no reset, rebase, stash, force-push, or owner-file cleanup was used.
- Pre-existing owner untracked files were preserved and remain unstaged.
- Root `TASKS.md`, `.hiveai/audits/**`, and historical evidence are protected and will not be edited.

## Initial scope

The live migration must replace Palette V2 paths, schema/version checks, colors, hard-coded tables, fixtures, generated/UI consumers, and retired difficulty color-count bands wherever they are active. Historical audit/log/legacy provenance remains immutable. Level Factory adopts `usedColorEnvelopeV1 = 3..12` and `difficultyClassDerivedFromColorCount = false`.

Implementation, commands, failures/corrections, tests, changed files, commits, pushes, and final SHA verification will be appended chronologically.

## Implementation chronology

- Added the exact canonical V3 mirror at `data/palette/scrubbots_palette_v3.json` for the Level Factory package boundary; the Scrubbots root JSON remains the cross-repository authority. The historical V2 file was preserved unchanged.
- Migrated the Python palette contract, color-usage validation, package data, mask generator, review UI colors, M01/M02/M03/M04/M06/M08/M09/M10/M05/M07 fixtures and manifests to V3. The contract now exposes only the global `usedColorEnvelopeV1` `(3, 12)` and `difficulty_class_derived_from_color_count = false`.
- Removed active per-difficulty color-count enforcement. The mask generator now deterministically trims a requested canonical subset only when a geometry role assignment cannot use the full requested subset, while retaining the valid global 3..12 envelope.
- Migrated active Godot editor RGB tables and import-validation fixtures to the V3 C01..C16 values. Updated governance expectations to the authorized MAINT task without editing `TASKS.md`.
- Updated live review generators and regenerated their committed M03/M04/M05/M06/M07/M10 HTML/JSON evidence plus M08 PNG goldens from V3.
- Focused Python pytest initially exposed stale V2 expectations and review/golden artifacts; each was corrected in the corresponding live contract/test/artifact. The first focused run then exposed the governance regex still excluding the MAINT task, which was corrected.
- All Level Factory Godot integration suites were run headlessly. The import-validation suite first failed because its valid fixture still used V2 RGB values; the fixture was migrated to V3 and the full Level Factory Godot suite passed.
- `python -m compileall -q src tests`: PASS. Focused pytest: `146 passed`. Full pytest first exposed binary PNG handling in the workspace-policy test; the test was corrected to inspect UTF-8 text only, and final full pytest passed: `985 passed, 2 skipped` (one cache-permission warning; skips were pre-existing canonical-checkout capability skips).
- Final active-scope search for `scrubbots_palette_v2`, `global-palette/v2`, old V2 HEX values, and `difficultyColorCountBands` returned no matches outside explicitly historical/provenance paths and the protected `TASKS.md`/evidence archives.
- Final Level Factory working tree was reviewed with all pre-existing owner work and Godot-generated `.uid` files kept unstaged. `TASKS.md` and `.hiveai/audits/**` remain unchanged.

## Builder verification

- Level Factory headless Godot: all 23 `level_factory/tests/*.gd` suites PASS, including `factory_studio_import_validation_integration_suite`.
- Final Python gates: compileall PASS; focused pytest `146 passed`; full pytest `985 passed, 2 skipped`.
- Offline/runtime boundary: no remote runtime dependency, telemetry, API key, or cloud image generation was added.
- Dependency/license/security review: no dependency or license changes; no secrets added; binary fixtures are checked only as binary assets.
- Implementation commit SHA, evidence-log commit SHA, push results, and final local/remote equality are recorded below after publication.

## Publication

- Implementation commit: `e1cd2ad` (`MAINT-PALETTE-V3-001 migrate Level Factory to canonical V3 palette`).
- Evidence log is being published in a separate builder-log commit after this implementation commit; no product files are added to that evidence commit.

- Evidence-log commit: `fb4071a9292927d26590f715c19ec047605b67a0`.
- Push result: `origin HEAD:main` succeeded; remote advanced from `383bdb6` to `fb4071a`.
- Final Level Factory publication state before this final log-only update: local `HEAD == origin/main == fb4071a`; protected `TASKS.md` unchanged.
