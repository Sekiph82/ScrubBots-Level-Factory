# SB-LFX-018 R05 M03 | F01 Level 48 Numeric Fit and GameFeelFlow Startup Gate | Independent Audit V07

Date: 2026-10-19 (Europe/Istanbul)
Auditor: ChatGPT, remote GitHub source/commit evidence reviewer. No fresh native Godot run, Windows log read or production operation performed by GPT.

**Decision:** M03-F01 original owner002 has a **numerically valid MEDIUM candidate slot at Level 48 (hard tolerance)**, but **NO actual campaign placement**. GameFeelFlow whole-game startup is **NOT QUALIFIED** because exact previously alleged parse-error text was not captured. The authentic previously completed CPX001/STAGING/CPX002 engineering chain is unchanged and should not be repeated. **Full M03 and R05 production remain OPEN.**

## Independent repository checks
- F01 Codex handoff commit on `Sekiph82/ScrubBots-Level-Factory/main` independently fetched: `02c75c013f00c88fba884ef7dfb9d4fd1ed3c8d7`.
- Exact F01 findings appear in the existing builder log: `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`, section `2026-10-19 11:56 +03:00 - V06 campaign placement and GameFeelFlow gate follow-up`.
- Pinned numeric source independently retrieved: `tests/evidence/SB-LFX-018-R05-M03-V02/002-difficulty-placement.json`. The Codex log gives SHA-256 `35d5211f5d77867391e9f189d10ac8d03be878ccec96fa8ae71d4657443c7fa1` for this preexisting file; GPT fetched its current GitHub content but did not independently recompute the SHA-256. The file explicitly says `campaign_catalog_last_order=10`, `next_campaign_order=11` and disclaims proof of campaign sequencing, novelty and owner intent.
- Current `Sekiph82/Scrubbots/main` previously independently verified at `9663c44c0b40dd08b082e4c5a54f808efb481704`. Exact game `project.godot` independently fetched and references `GameFeelFlow="*res://addons/game_feel_flow/core/game_feel_flow.gd"` in `[autoload]`, with GameFeelFlow and Saltmire Spark editor plugins enabled.
- The exact `addons/game_feel_flow/core/game_feel_flow.gd` **exists in the canonical game GitHub repository** and contains `GFF...` script/type references. Therefore a broken isolated sparse checkout or missing complete addon/import may produce misleading errors. The earlier builder summary did **not** retain full parse lines, so that remains a diagnostic possibility, **not an established root cause**.

## F01 official Difficulty evidence: measured vs target

| Proposed level | Intended class | Score | Target challenge | Delta | Hard +/-5 verdict |
| --- | --- | ---: | ---: | ---: | --- |
| Level 1 | EASY | 48.8166775742989 | 20.0000000000000 | +28.8166775742989 | **OUTSIDE HARD** |
| Level 11 | EASY | 48.8166775742989 | 20.6827880569900 | +28.1338895173089 | **OUTSIDE HARD** |
| **Level 48** | **MEDIUM** | **48.8166775742989** | **44.3565002099862** | **+4.46017736431264** | **INSIDE HARD, OUTSIDE DEFAULT** |

Level 48: cycle 4, slot 8, `second_tension`, MEDIUM. This is the **first enumerated future MEDIUM score/class fit in the source record**, not a proof it is the globally best placement, not an assigned campaign slot, and **not a resolved level 11–47 schedule**. Score within the +/-5 hard bound **does not imply full content acceptance**. Original 002 remains authentic **MEDIUM, OWNER_ACCEPT, UNASSIGNED**. Any actual placement requires authentic current campaign sequence, novelty/duplicate content checks, pool/release authority and an owner's specific placement decision. Do not rewrite target, downgrade class, forcibly assign Level 48 or silently create placeholders 11–47.

Distinct generated candidate `candidate-m03-l11-void-rules-seed-92` remains **EASY READY_AUTO, NOT OWNER_ACCEPT, UNASSIGNED**. It must not be placed or published merely because score matches official Level 11 bound.

## Whole-game GameFeelFlow startup
- Builder read its **preexisting, owner-controlled** Godot log (size 1,411 bytes, SHA-256 `fde49d72aa03843a0af0bf6f534915a70866f6198088904b2307970ff28d52e`), unchanged from previously recorded digest.
- That historical log shows `Game Feel Flow: Ready (31 effects, 15 combos)`, not the alleged parse-error details. This is **not** a new whole-project startup or a failure reproduction.
- The earlier native solver bridge still has valid CPX002 `SOLVED/WIN` receipts. The earlier **summary** noted missing-GFF-symbol parse errors but neither full exact message nor affected source path/line was preserved. **Neither a clean whole-game startup nor a reproducible source bug is established by those records.**
- To qualify whole-game startup, perform one **new, distinctly scoped** run from a complete authorized clean current-main Scrubbots checkout with all required tracked addons, fresh isolated Godot editor import/cache, isolated APPDATA/LOCALAPPDATA/TEMP/TMP **before Godot starts**, bounded command and captured verbatim stdout/stderr (including file/line and type/symbol). Preserve existing Desktop owner Godot log and untracked addon data. Differentiate **headless test-run/import errors** from normal main-scene startup defects; if no error reproduced, record exact environment and pass the observed startup gate only, not general production quality. If real tracked code bug reproduces, patch the smallest tracked file, run focused regression and only then report fix. Do not invent old missing lines.
- No broad deletion, re-download of gigabytes, unnecessary full-suite/CI/R2 production operation or staging replay required.

## Status decisions
- `F01_ORIGINAL002_LEVEL48_SCORE_CLASS_WITHIN_HARD_NUMERIC_ONLY`
- `F01_ORIGINAL002_NOT_ASSIGNED_CAMPAIGN_ORDER_11_TO_47_OPEN`
- `F01_SEED92_LEVEL11_READY_AUTO_OWNER_ACCEPT_MISSING`
- `GFF_HISTORICAL_OWNER_GODOT_LOG_UNCHANGED_31_EFFECTS_15_COMBOS`
- `GFF_EARLIER_PARSE_LINES_NOT_PRESERVED_STARTUP_NOT_QUALIFIED`
- `CPX001_STAGING_CPX002_ENGINEERING_PASS_RETAIN_V06`
- `M03_FULL_OPEN_R05_PRODUCTION_OPEN`

**V07 disposition:** Accept **F01 Level 48 numeric fit** only; reject overstatement that Level 48 is already placed or that either candidate received campaign acceptance. Leave GFF whole-project startup as a separately testable evidence gap. Keep full M03, generated seed92 owner approval and R05 production acceptance open.
