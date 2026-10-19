# SB-LFX-018 R05 M03 | V07 Complete-Game Startup and Asset Import | Independent Audit V08

Date: 2026-10-19, Europe/Istanbul
Auditor: ChatGPT, independent remote GitHub and recorded builder-log source review. No direct execution of Godot on owner's Windows machine; no attempt to clean owner's TEMP or bypass agent policy.

**Decision:** GameFeelFlow **autoload and isolated headless main-scene startup GATE PASS for the exact tested checkout**, but **Godot project import NOT CLEAN** due to five tracked raster assets, and **forced-quit resource diagnostics remain unresolved**. Exact task TEMP cleanup **BLOCKED BY CODEX POLICY**; owner-controlled cleanup requires separately authorized local action. CPX001/STAGING/CPX002 engineering PASS remains retained. M03 full / R05 production OPEN.

## Verification and source provenance

- Remote `Sekiph82/ScrubBots-Level-Factory/main` independently fetched at `20f131033263569fd5105079c0096ce446b3e817`.
- GitHub compare `1b8e2e7d033d9982bb0a07d780242812ea1dcefe...20f131033263569fd5105079c0096ce446b3e817`: **2 commits ahead, zero behind; only** `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md` changed (11 added lines, no substantive product asset/code changes). Current user's local `HEAD == origin/main`, 0/0 and clean tracked status are supported by the Codex builder handoff, not independently inspected on Windows by GPT.
- Log section `V07 complete-game GameFeelFlow startup gate — 2026-10-19 18:57 +03:00` documents exact runner, source, environment and raw stdout/stderr hashes. **Raw stdout/stderr remain on local TEMP only, not GitHub**, so GPT assessed reported error classifications and evidence hashes, but did not independently parse the raw output bytes.
- Game authority: complete clean shallow checkout `Sekiph82/ScrubBots/main` pinned at `9663c44c0b40dd08b082e4c5a54f808efb481704`, reported by builder as identical to `git ls-remote`. Godot `4.7.2.stable.official.ed1daf0bf`. GPT earlier independently fetched canonical game's `project.godot` and GFF source at corresponding main.

## Two actual bounded run records

1. Isolated Godot editor import: `--headless --editor --path <complete game checkout> --import --quit`. **Exit 0**, elapsed **278.31 s**. `APPDATA`, `LOCALAPPDATA`, `TEMP`, `TMP` redirected to exact task-only runtime paths before launch.
2. Isolated actual main-scene startup: `--headless --path <complete game checkout> --quit-after 12`. **Exit 0**, elapsed **5.40 s**. Deliberate early shutdown, not an interactive gameplay/family APK test.

GameFeelFlow autoload is present in `project.godot:21` at `res://addons/game_feel_flow/core/game_feel_flow.gd`. `GFFEffectConfigManager: Registered configs` appears in both import and startup stdout, associated with `addons/game_feel_flow/core/gff_effect_config_manager.gd:100`. **No GameFeelFlow SCRIPT ERROR / parse / failed-load diagnostics in captured stderr per builder.** No GFF source fix is justified by this run. This bounded successful test does **not** establish that previously summarized, unpreserved parse errors never occurred, or that all effects render correctly on devices.

## Import diagnostics: real tracked assets, distinct from GFF

Full import recorded **four tracked WebP decode failures** under `coordination/sessions/M42-C003/evidence_v03/runtime_captures/`:
- `wave_runtime_24fps.webp`, 1,357,874 bytes, SHA256 `216913F8CBADEEC91C591DF688514CBD7C9FEE82542879C140B95F10E3861B72`.
- `turn_runtime_24fps.webp`, 1,341,774 bytes, SHA256 `7B4559004560F40B82807E8BAF2C549B451E237C32B08536F54BF327D664AA4B`.
- `full_turn_runtime_24fps.webp`, 1,489,048 bytes, SHA256 `5B823292F990B74B12574510C6D8DE106C2AED442BD2DB7BA213CFB9092F3071`.
- `bow_runtime_24fps.webp`, 1,307,220 bytes, SHA256 `830FD71856A4C61846BBE5BD0582EEE4D20779EAAF29E5E90A4DAB3E5B41CBE1`.

Recorded error sites are Godot engine `modules/webp/webp_common.cpp:173`, `core/io/image_loader.cpp:102`, `editor/file_system/editor_file_system.cpp:3093`. Since these files live in an evidence directory, first determine whether they should be under Godot import at all, whether any canonical runtime file references them, and whether they are malformed for the installed Godot version. Do **not** replace, delete, transcode, or re-encode original owner evidence without explicit provenance and intent. A narrowly scoped `.gdignore` may be appropriate **only after** validating it will not remove needed runtime inputs or tests; do not claim correction before testing.

Separate final UI raster:
- `assets/ui/final/gameplay/buttons/icon_pause.png`, 7,531 bytes, SHA256 `D917EC37EFDAFDA1FDD6D21F0C6DA6A390A65EEB6413CF2E04C54E4B3B30E782`.
- Warnings `read beyond end of data` at `drivers/png/png_driver_common.cpp:57`, then `ERR_FILE_CORRUPT` at `drivers/png/png_driver_common.cpp:120`, followed by import failure at image loader/file system sites. This UI file is an actual `assets/ui/final` gameplay resource and warrants **higher priority, source-backed repair**. Before editing, verify PNG signature/chunk CRC/IEND bytes, its actual file references and any authentic approved final UI source in the repo. Use only an approved genuine replacement; do not fabricate a raster, delete, blank, or silently substitute. No full-game import rerun until an actual change.

Separate **forced-quit warning:** `61 ObjectDB instances were leaked at exit`, `30 resources still in use at exit`; these occurred at `--quit-after 12` and have no source line in the retained summary. Distinguish normal forced/headless startup teardown from leaks during ordinary game exit. Do not blame GFF without stack/source evidence.

## Cleanup and scope

Exact task-owned paths remain on Windows:
- `C:\Users\sekip\AppData\Local\Temp\SB-LFX-018-R05-M03-V07-ScrubBots`.
- `C:\Users\sekip\AppData\Local\Temp\SB-LFX-018-R05-M03-V07-runtime`.

Builder estimated **about 2.24 GB** task temporary data. Prior to cleanup attempt, builder verified **no reparse points and no matching Godot process**, but actual removal was **blocked by automatic policy review**. **Do not mark these folders removed, repeat blocked calls, invoke an alternative executor solely to circumvent the restriction, or touch the owner's unrelated TEMP, existing Desktop assets or 2,972 untracked paths.** Owner may choose a direct manual, narrowly scoped removal outside Codex if desired, after local read-only revalidation that the folders are still task-only and no processes hold them. Captured raw stdout/stderr are contained in the runtime path; if independent source-line audit is desired, preserve them **before** any owner-side cleanup.

## Remaining gates

- `GFF_AUTOLOAD_COMPLETE_MAIN_STARTUP_BUILDER_PASS_BOUNDED` (not GFF all-effects visual PASS).
- `GODOT_IMPORT_NOT_CLEAN_4_WEBP_EVIDENCE_ASSETS_AND_FINAL_ICON_PAUSE_PNG`.
- `GAME_SHUTDOWN_OBJECTDB_61_AND_RESOURCES_30_WARNING_UNQUALIFIED`.
- `V07_TWO_EXACT_TASK_TEMP_DIRS_POLICY_BLOCKED_STILL_PRESENT`.
- `F01_LEVEL48_MEDIUM_HARD_SCORE_NUMERIC_ONLY_UNASSIGNED` (orders11-47 unqualified).
- `LEVEL11_SEED92_READY_AUTO_NOT_OWNER_ACCEPT_UNASSIGNED`.
- `CPX001_STAGING_CPX002_CURRENT_MAIN_ENGINEERING_PASS_RETAINED`.
- `M03_FULL_OPEN_R05_PRODUCTION_OPEN`.

**Next productive work:** source-based, read-only inspection of the five affected asset files/references and the distinction between tracked evidence folders versus shipping/runtime assets, followed by a **genuinely justified** narrow repair only with authorized authentic replacement sources. Explicitly decide whether the final pause icon is eligible for replacement. Preserve raw V07 logs if later troubleshooting is required. Campaign placement requires separate owner review/sequence; no auto assignment of 002 or seed92. No CPX002 replay or production operation needed.
