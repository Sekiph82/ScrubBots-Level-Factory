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

## R10 V05 live account-sync and installed-route follow-up â€” 2026-10-30

This addendum supersedes the earlier ALPIX `ALPIX_PLUGIN_MISSING` observation above for the current authenticated Claude Code account. It preserves the earlier zero-spend 16-PNG import evidence; that completed flow was not repeated.

- Normal scoped-overlay preflight at published `origin/main=0fadcccd21da9180d5f16ee5f5e85c54e5de174e` returned `PREFLIGHT_ONLY`, zero manifest drift, one planned file, and `processInventoryStatus=NOT_QUERIED`. Exact change: `src/scrubbots_pixel_factory/alpix_batch.py`, installed SHA `48226e5f15ee6ef3b554c132592dd4b756ee9927755a00f0e7f6fc7f162eb510` â†’ source SHA `d30651a2c1d89720fc73e070a72282cbedcfa366159004aea327ae7937d12507`.
- The normal `-Apply` transaction returned `COMMITTED`, with `changedPaths` containing only `src/scrubbots_pixel_factory/alpix_batch.py` and verified installed SHA `d30651a2c1d89720fc73e070a72282cbedcfa366159004aea327ae7937d12507`. The manifest now has 2,319 managed entries and 21 receipts; manifest SHA-256 is `fdd2d815aafbd81706572178825abadd24a42cbd95a0e06f46a2d15317c1d4a2`. Its final receipt binds sourceHead/sourceCommit to `0fadcccd21da9180d5f16ee5f5e85c54e5de174e`, has the matching per-file hash, and records Windows deny-write handles, independent blocked-write probes, SHA-checked staging, atomic replace, and no-overwrite additions. Shortcut inspection (read-only) confirms `C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk` targets the PowerShell launcher under the exact managed Release folder and uses its `level_factory` ICO.
- Installed-runtime status-only Python check returned `ALPIX_AVAILABLE_DISCOVERY_ONLY`, `CLAUDEAI_CONNECTOR_CONNECTED`, route `claude.ai Alpix`, scope `claude.ai config`; it explicitly says drawing/export capabilities and usage-limit health are not probed. `pixellab_secret_status()` returned `READY_CREDENTIALS_CONFIGURED` / configured true; no credential value was read, displayed, or logged. No remote ALPIX tool or PixelLab request was invoked.
- Launched the installed Release with `Release\ScrubBots Factory Studio\scripts\launch_factory_studio.ps1`. The launcher selected Godot executable `C:\Users\sekip\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_Microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64.exe`; its `FileDescription` is `Godot Engine`, `ProductVersion` is `4.7.2.stable.official`, and executable SHA-256 is `ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424`. The real window title is `ScrubBots Factory Studio (DEBUG)`, opened from the managed Release project. The PIXEL ART screen's provider picker visibly lists `ALPIX (Claude)` and `PixelLab Pro Â· 4Ã—4`; the ALPIX provider dialog displays the authenticated account-connector status and the discovery-only capability limitation. The installed PixelLab dialog visibly shows W/H controls, `Max colours (3-12)`, 4Ã—4/16-frame output, and the 59Ã—59 game maximum. The currently displayed saved sprite size is 52Ã—52; no size or colour value was changed, and Generate/Regenerate was not activated.
- Earlier same-task GUI evidence above remains the acceptance evidence for the no-spend synthetic atlas import: 16 exact row-major 56Ã—56 PNG crops with verified hashes. It was not rerun because this follow-up changes only account-synced ALPIX discovery, not atlas slicing/import code. No original 140-PNG batch, Pool data, source jobs, or owner art was accessed or changed.
- Installed release status: `INSTALLED_RELEASE_SHA_MANIFEST_VERIFIED`; changed-file source/install/receipt parity PASS. Prior accepted writer exclusion remains recorded in its exact receipt (`WRITER_EXCLUSION_PROVED`). `PIXELLAB_INSTALLED_KEY_PRESENT` PASS; `PIXELLAB_PRO_GUI_4X4_PASS` current screen/controls PASS (actual paid generation NOT RUN); `ALPIX_STUDIO_GUI_PROVIDER_STATUS` connected account route shown as discovery-only; `ALPIX_CLAUDE_CODE_ROUTE` connected but tool identity/capabilities and canvas/export semantics remain NOT VERIFIED. The available connector requires Claude Code workspace trust to inspect tools; this Windows security prompt was left for the owner and not accepted by automation. Thus no ALPIX generation/export pass is claimed. The existing app currently remains open for owner review; the underlying provider is PixelLab Pro while the provider status dialog shows the ALPIX account route.
- Paid PixelLab generation, remote ALPIX generation/stamping, CI/Actions, Release Pool promotion, and R2 remain NOT RUN. `TASKS.md`, prompts, audits, the original 140 PNG job and owner files were not modified.
