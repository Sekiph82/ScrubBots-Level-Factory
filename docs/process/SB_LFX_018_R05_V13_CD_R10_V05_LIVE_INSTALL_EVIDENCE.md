# SB-LFX-018 R05 V13-C/D R10 V05 | LIVE FACTORY STUDIO INSTALL EVIDENCE

Document role: CODEX BUILDER EVIDENCE

Date: 2026-10-28 (Europe/Istanbul)
Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Authoritative prompt: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB_LFX_018_R05_V13_CD_R10_V05_LIVE_ALPIX_PIXELLAB_FACTORY_STUDIO_INSTALL.md
Canonical checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Result

The approved scoped Release overlay is installed and the real Godot 4.7.2 Factory Studio opens from the managed Release project. The installed provider picker, PixelLab Pro 4×4 controls, and actual zero-spend atlas import were exercised in the Windows GUI. The ALPIX Claude Code route remains unavailable in the local runtime, so ALPIX end-to-end integration is still blocked; no fake route was configured.

## Release and writer-exclusion evidence

- Source `HEAD` and `origin/main` at the final product commit: `deb2a96ca8c54413c4a0fcad365eb0e2864f9147`.
- The approved installer returned `COMMITTED`; it updated only `level_factory/scripts/factory_studio_exact_ui.gd` in this final overlay transaction.
- Installed manifest: `Release\ScrubBots Factory Studio\.factory-studio-install-manifest.json`, SHA-256 `2c2d2d39183780efd44516f97784ee20994f3554e4d3c2eac09920058a4071f5`.
- The final receipt binds `sourceHead` to `deb2a96ca8c54413c4a0fcad365eb0e2864f9147`. All 19 installer-managed files were independently checked: source SHA = installed SHA = manifest SHA for every path. This includes the installed `pixellab_pro_atlas.py` (SHA-256 `afe51ffcc48b94ca9e81b4fbdfc54ab5d6c4e434213874573cf9e7d50c595497`) and the repaired `verify.py`.
- The receipt records actual writer exclusion: deny-write Windows file handles on every existing replacement target and manifest, independent PowerShell write-open probes denied on each live target, SHA-checked transaction staging, atomic replacement, and no-overwrite move for additions.
- The installed Godot executable is the verified Godot 4.7.2 stable build; the exact Release launcher launched the managed Release project and its window title was `ScrubBots Factory Studio (DEBUG)`.

## Real GUI and PixelLab Pro controls

- The PIXEL ART provider button and details panel both changed to `PixelLab Pro · 4×4` after selection.
- The provider dialog reported the PixelLab credential present in Windows Credential Manager. Only presence/status was read; the token value was neither displayed nor logged.
- The GUI displayed 56×56, `4×4 output: 16 frames`, 224×224 atlas, a V3 locked palette, and max 12 colours.
- In the installed dialog, manually entering width 60 and height 60 resulted in 59 for each respective axis after confirmation. Entering max colours 2 resulted in 3. The UI was returned to 56×56 and 12 colours after boundary checks.
- No Generate/Regenerate control was activated. No PixelLab request or credit was used.

## Actual zero-spend 16-PNG import

No previously owner-supplied 224×224 atlas was present in the two approved visual-evidence locations already checked for this task. To exercise the installed import flow without a provider request, a clearly synthetic V3-palette atlas was created and selected through the actual Factory Studio `LEVEL FACTORY > Select PNG` flow while PixelLab Pro was selected.

- Synthetic input: `Release\ScrubBots Factory Studio\level_factory\output\semantic-generated\r10-v05-synthetic-atlas-b5fa921dcd95406b963a52de94df8598\synthetic-atlas-224x224.png`.
- Input SHA-256: `1c924b50652b75b61b286abc6943a5080e64222082466226ed8e20ff00faa194`.
- The GUI displayed the 4×4 atlas and `16 complete · 0 failed · 0 remaining`.
- Import output: `Release\ScrubBots Factory Studio\level_factory\output\semantic-generated\pixellab-pro-4x4-import-452dc84758ab4a84be19ad5bd8caf3db`.
- Output manifest SHA-256: `a8f25cdc22177af13893ca7cf9387184926d37ee4362e65a66e8f4366baa8e33`.
- All 16 row-major `sprite-01.png` through `sprite-16.png` outputs are 56×56, use three allowed V3 colours, match the corresponding original-atlas crop pixel-for-pixel, and match their manifest SHA-256 values.
- Each crop also has a separate content-addressed OWNER_UPLOAD source record whose source bytes and SHA match the slice. Every record is `SOURCE_ONLY` / `UNVALIDATED`. No candidate, solver, WIN replay, difficulty, QA, or Release Pool acceptance was claimed. The project’s 140-PNG batch was not opened for processing, resumed, or rewritten.

## ALPIX route status and limits

The owner’s Claude Desktop screenshots show Alpix connected under both Connectors and Plugins. The authenticated local Claude Code 2.1.287 runtime reports no Alpix plugin in `claude plugin list` and no Alpix server in `claude mcp list`; installed Release `discover_alpix()` returns `ALPIX_PLUGIN_MISSING`, and the Studio provider dialog shows that status. The connected Claude Desktop account plugin is therefore not currently exposed as a usable local Claude Code worker route. No guessed MCP server, duplicated plugin, private auth/config edit, remote canvas write, or ALPIX generation was attempted. This is the remaining integration blocker.

## Checks and safety

- `tests/unit/test_scoped_overlay_transaction.ps1` — PASS.
- `tests/unit/test_scoped_writer_exclusion_windows.ps1` — PASS; actual concurrent write-open was denied while atomic replacement succeeded under the verified lease.
- `python -B -m pytest -p no:cacheprovider -q tests/unit/test_scoped_overlay_manifest_drift_contract.py` — 5 passed.
- `python -B -m pytest -p no:cacheprovider -q tests/unit/test_sb_lfx_018_c001_r02_master_control_bindings.py` — 9 passed after the provider-caption fix.
- `python -B -m pytest -p no:cacheprovider -q tests/unit/test_sb_lfx_018_c001_r02_master_control_bindings.py tests/unit/test_pixellab_pro_flash_v12.py::test_pixellab_pixel_art_ui_enforces_variable_51_to_59_four_by_four_canvas` — 10 passed after GUI-boundary validation was added.
- PowerShell AST parse and `git diff --check` — PASS. Installer preflight reported zero manifest drift before the final apply.
- Actual installed Release byte parity — 19/19 source/installed/manifest SHA matches.
- PixelLab paid API, ALPIX remote generation, CI/Actions, Godot headless test, solver, Release Pool writes, `TASKS.md`, and the original 140-PNG job — NOT RUN / NOT CHANGED.
- A direct-root `%APPDATA%\Godot` snapshot before and after the GUI check found the same three files (`editor_settings-4.7.tres`, `projects.cfg`, `recent_dirs`) with unchanged sizes and SHA-256 values. No cache cleanup or restoration was performed.

## Implementation commit trail

- `cd90c310` — keep the visible provider button in sync with the selected provider.
- `1a8e7d43` — authenticate the exact prior install receipt for a safe scoped reapply.
- `b5825a10` — clamp manually entered PixelLab dimensions and colour limit on dialog confirmation.
- `deb2a96c` — recognize only the two exact prior receipt-chain manifests and revalidate the historical verify.py and atlas-addition receipts.

The append-only M03 builder log records failed preflight/apply attempts, their no-write/rollback outcomes, fixes, focused test runs, installation, GUI checks, and final publication receipts. `TASKS.md`, prompts, and audits were not edited. This is builder evidence, not independent audit acceptance or a claim that ALPIX is fully integrated.
