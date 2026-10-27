# SB-LFX-018 R05 V13-C/D R10 V02 (OWNER REVISION) | PIXELLAB PRO VARIABLE-SIZE 4×4, LOCKED V3 PALETTE, CONFIGURABLE MAX COLORS, ALWAYS SLICE 16

**ROLE:** GPT-authorized Codex builder prompt. Revised in place on 2026-10-27 **BEFORE Codex execution**.
**REPO:** https://github.com/Sekiph82/ScrubBots-Level-Factory
**CANONICAL OWNER CHECKOUT ONLY:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
**SOLE TRACKER:** root `TASKS.md` (GPT edits; Codex READ ONLY).
**SUPERSEDES:** Older R10 V01 single Pro Flash source-direct/paid prompt, never given to Codex. This revision supersedes all conflicting fixed-56 or optional-splitting language in R10 V02 itself.
**PAST V24 R09 AUDIT:** `.hiveai/audits/SB_LFX_018_R05_V13_CD_R09_PIXELLAB_ZERO_SPEND_INDEPENDENT_AUDIT_V24.md`
**EXISTING M03 BUILDER LOG:** `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md` (append ONLY).

## Exact owner contract: do not simplify any of the four overrides

Owner supplied PixelLab Creator > Create Image Pro screenshots showing: (1) the exact 16-color ScrubBots palette manually entered into the **Color palette (Beta)** field, (2) **Max colours** set to 12 with a user-editable control, (3) **Output size** independently editable (56×56 is an EXAMPLE, not a fixed rule), (4) **Custom size (Beta)** reports 4×4 grid (16 variations) for the shown size. Factory Studio must reproduce these capabilities **without decoupling the game-safe palette contract**.

**Owner's mandatory 4×4 rule: EVERY successful PixelLab PRO 4×4 request or 4×4 imported atlas ALWAYS goes through ONE canonical atlas and ALWAYS runs the deterministic 16-slice extraction step, followed by 16 separate PNG and audit records.** NEVER describe separation as "if needed", "optional", "fallback" or "only for composites". Even if PixelLab API returns sixteen individual images, first assemble them in deterministic row-major order into a lossless 4×4 composite, then **always slice** the normalized atlas back into 16 independently SHA-bound crops and pixel-compare against originals. Retain the original API frames and normalized atlas for provenance. No resize, anti-alias, recolor, palette snapping or background replacement. A failed/duplicate individual sprite gets its own rejection without silently dropping or altering other sprites.

## Canonical palette and adjustable max-colors control

**Authoritative repository:** `data/palette/scrubbots_palette_v3.json`, sixteen owner-locked logical RGBs, in the exact C01..C16 order. Auto-populate, show and submit the **full** 16-color V3 palette in PixelLab Pro's `target_palette.colors` EVERY time. Do not make the target palette optional or let arbitrary external palettes silently change level semantics. Owner's current palette (lowercase on site; case-normalize to canonical uppercase without changing actual RGB):
```
#ff4500 #ffa800 #ffd635 #00cc78 #00ccc0 #51e9f4 #3690ea #2450a4
#6a5cff #ff3881 #9c6926 #fff8b8 #d4d7d9 #515252 #ffffff #000000
```
**Do not confuse sixteen ALLOWED palette colors with max per-image USED colors.**
Expose the separate owner-editable `Max colours` value (default **12**) in PIXEL ART's PixelLab Pro controls, valid **3..12** for directly game-eligible levels; send `target_palette.max_colors=owner_selection`. Every extracted sprite MUST independently have 3..chosenMax **distinct opaque C-ID colors**, not merely <=12. The API's generic 2..64 max range does NOT relax SCRUBBOTS' production 3..12 rules. Return a clear per-sprite `USED_COLOR_COUNT` rejection if under 3 or over chosenMax. Reject any opaque pixel outside V3, any alpha not 0 or 255; transparent pixels do not count as used colors. Do not display "palette PASS" just because the request contained correct HEX values: validate every returned pixel.

If style references are supported, `style_options.color_palette=false` when V3 `target_palette` is supplied (per official PixelLab API). Preserve ALPIX + Claude as the other active provider, without changing its size rules, auth or historical data. Remove Pro Flash only from **active new-generation UI/dispatch**, not archived old assets, provenance or immutable records.

## Variable size with REQUIRED 16-image 4×4 output

Provide independent owner-selectable **Width and Height**, default 56×56, NOT hard-coded 56. The desired **per-character dimensions W×H** determine a **4W × 4H** composite. Examples: W=56, H=56 => 224×224 composite and sixteen 56×56 crops; W=52, H=52 => 208×208 composite and sixteen 52×52 crops; W=59, H=59 => 236×236 composite and sixteen 59×59 crops.

The model's number of results changes with size; do **not** allow a freeform value which silently yields 25/36/64/9/4/1 frames while the Studio claims 16. Official current REST `POST /v2/generate-image-v2` OpenAPI defines **16 results when max(width,height) is 51..64**, while Creator docs/screen can use a somewhat different bucket: **43..64**. Rely on the ACTUAL configured route's official size/count contract, not the screenshot alone or guesses. For a conservative guaranteed 4×4 REST mode initially permit W and H independently within **51..64**, with fixed grid 4×4 and clear prediction; no "56 ONLY" restriction. If other documented rectangular sizes also produce 16 under live API, expand only with verified source-supported tests. Reject an incompatible selection BEFORE any paid submission, with an informative message. The official API returns `image_size` for ONE SPRITE (W×H), never send composite dimensions (4W×4H).

**ScrubBots Level Factory accepts native logical sources only when each axis is 20..59.** Therefore 51..59 per axis may proceed to direct level eligibility (subject to all other gates). W or H of **60..64** remains allowed for Pro generation/16-sprite SOURCE storage, but must be marked `LEVEL_DIMENSIONS_OUT_OF_RANGE`, excluded from automatic READY/Release Pool, and must NOT be silently shrunk. A separately owner-authorized, logged deterministic derivation stage would be needed to use larger frames as levels. If PixelLab selects a supported *nearest aspect ratio* and outputs a different W/H, detect the actual dimensions and fail the direct exact 4×4 geometry gate rather than silently resize or mislabel.

For manually imported atlases (including Photopea source files), require an **exact 4×4 equal-cell grid**, infer W=atlasWidth/4, H=atlasHeight/4 only if both dimensions divide evenly by 4; check documented 4×4 geometry, row/column boundaries, contents, transparent spacing and no clipped characters. Non-224 dimensions are **normal**, not errors. Native exact Level Factory range and palette/alpha still apply per extracted cell. Do not impose 56 on ALPIX or other imported sources unrelated to this 4×4 mode.

## Fixed unconditional extraction pipeline (all successful 4×4 sources)

```
PIXEL ART (ALPIX unchanged | PixelLab Pro owner selected)
→ owner prompt + editable per-sprite W/H + locked 16-V3 palette + editable maxUsedColors
→ explicit ONE chargeable Generate confirmation (NO API call without separate owner approval)
→ collect 16 original Pro API frames OR a verified original 4×4 atlas/Photopea ZIP
→ NORMALIZE: canonical 4×4 atlas of exactly 4W×4H, 16 row-major slots
→ **ALWAYS** SLICE atlas (rows 1..4, cols 1..4) into 16 exact W×H PNG
→ 16 source hashes + positions + color/alpha/occupancy/duplicates + original frame pixel-match
→ per-frame PASS / REJECT with no cross-frame data loss
→ existing immutable LEVEL FACTORY source import (only accepted sprites)
→ existing solver + WIN replay + Difficulty V1 + real QA gates
→ only genuine READY becomes RELEASE POOL eligible; never auto publish/R2
```

Never let returning sixteen API images bypass creation **and re-slicing** of the canonical atlas; never let imported composite images bypass slicing. Do not treat simply cropping into 16 valid source PNGs as `READY`. If fewer/more than 16 API frames, unexpected frame sizes or missing positional identity, fail-closed, retain evidence and **do not retry paid POST automatically**.

## Existing published code foundations, refactor rather than abandon

- `src/scrubbots_pixel_factory/pixellab_pro_atlas.py` currently hardcodes `ATLAS_SIZE=(224,224)` and `CELL_SIZE=(56,56)`. REFACTOR into a dynamic W/H grid contract and mandatory normalization/slice/reconstruction with exact RGBA byte equality, 16 coordinate records, unique folder + immutable original source/manifest and individual sprite hashes. Preserve the tested default 224→16×56 behavior, maintain the source's original bytes; give each crop its own SHA/used-color/alpha/VOID/occupancy status. If PNG library decoding preserves transparent RGB, ensure round-trip equality for all pixels (including fully transparent RGB) or fail closed. Source originals must NEVER be overwritten.
- `tests/unit/test_pixellab_pro_atlas.py` currently has five offline synthetic tests for 56-pixel crops only. Expand tests for 52, 56, 59, 64, non-square 52×56/56×59, invalid non-divisible geometry, invalid 4×4 count, return-frame normalization/mandatory re-slicing and 16 byte-identical roundtrips, palette exact-V3/no off-palette, alpha contract, adjustable max 3/7/12, below-min and over-limit color, duplicate frames, out-of-range 60..64 level statuses, bad PNG, preservation of originals.
- Source backend still routes Pro Flash `PRO_FLASH` and UI locks 32×32 from R09; change active PixelLab generation to `PRO_4X4` (or one consistent identifier), owner W/H selectors, owner max color count, cost warning, palette visible as locked V3, mandatory source atlas stage and 16-sprite preview/statuses. Keep ALPIX route and focused no-spend regression checks. Preserve legacy Pro Flash history and production records.
- Canonical palette `data/palette/scrubbots_palette_v3.json` and validator code `src/scrubbots_pixel_factory/studio_extensions.py` are single sources of truth. For VOID transparent sources, original 140 completed job + game-specific VOID capability and solver authority must remain protected. Absolute owner assets remain intact.

## Code and runtime tasks in order

A. **Queue/sync**: Safely fetch and FF-only synchronize the *single* canonical Desktop checkout, don't create extra clone/worktree/TEMP, don't clean/reset/rebase/force, don't alter 3,003+ owner-untracked files, 18 stashes, original 140 job (102 READY/4 FAILED/34 REJECTED), Pool 131 JSON or secondary ScrubBots game repo. Run read-only queue guard; `Current Task` and `Next Task/Action` must contain exactly ONE matching current R10 V02 URL. Codex NEVER edits TASKS.md. Don't redo R01-R09 or re-merge the unrelated `ScrubBots-factory` project.

B. **Exact upstream contract, no spend**: Read current official Creator documentation AND v2 OpenAPI for `/v2/generate-image-v2` and `target_palette`; check version-specific count buckets. The screenshots authorize functionality, not hidden API charges. Source test that outgoing `image_size=(W,H)` with 16-frame compatible dimensions, full exact 16 HEX palette, `target_palette.max_colors=owner value`, `no_background=true`; no actual network calls, no paid token request. Creator site showed **10 generations** per 16 at selected 56, but REST API price is not guaranteed to match site credits; describe as historical website example. Secure Windows Generic Credential `ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN` presence-only status; never print/upload secret, never claim credential configured without evidence.

C. **Dynamic local atlas engine**: Implement pure and persisted 4×4 grid normalization + unconditional slicing for all 4×4 sources; deterministic row-major order, pixel-identical extraction, transparent RGBA stability, atlas and 16 PNG SHA manifest, rejection reasons and duplicate detection. A paid PixelLab response of 16 individual images must be assembled into a new atlas then ALWAYS sliced; original images preserved with before/after SHA. Import any preexisting owner composite atlas into the same mandatory slicer; optional Photopea All Slices ZIP intake must reconstruct 4×4 deterministically and then ALWAYS slice, never shortcut 16 files directly into Level Factory. Do not silently map arbitrary ZIP filenames to row-major without reliable coordinates.

D. **Factory Studio UI**: Replace only active Pro Flash controls with PixelLab Pro: visible locked ScrubBots 16-color palette, separate adjustable maxUsedColors control (default 12; valid 3..12) and independent W/H selectors with clearly marked green direct Level Factory range 51..59, warning 60..64 as source-only. Show predicted `4×4 = 16 frames` and calculated overall composite W×4/H×4 before owner pays; disable Generate for incompatible grid count. Preserve explicit owner-generated request and separate charge confirmation; no real paid request now. Track one durable operation ID and job ID, one POST after future explicit approval, poll-only resume on uncertain outcome, no duplicate charge. 4×4 preview with numbered per-frame statuses; no UI controls suggesting "optional Split".

E. **Factory Studio/Level Factory integration**: All 16 extracted PNGs must be considered independent immutable sources; only validated PASS sources enter EXISTING Level Factory pipeline, each bound to source SHA, palette/alpha/structure and game-authorized VOID, then SOLVED+WIN+Difficulty+QA for READY. 60..64 block direct production intake, no automatic rescaling. Preserve ALPIX's prior Claude subscription/MCP integration and owner-facing provider choice, no new Claude paid API.

F. **Focused offline tests/publication**: Run new+focused tests locally (Python `-B`, pytest `-p no:cacheprovider`, no CI/Actions and avoid broad TEMP churn). Assert mandatory splitter invocation for API frames and imported atlas/ZIP, non-default dimensions, max colors, no auto POST retry, no originals mutated, correct 16 independent outputs, and no false READY. Real Godot Studio GUI run, actual PixelLab API billing/gen, Release `-Apply`, future Release migration, original 140 job retry and R2 publication all **NOT authorized**. If native Godot needed after R08 one-use permission, pause only native-dependent substep and continue independent coding. Publish source/test changes to main nonforce after FF, report in `docs/process/`, append evidence to same M03 builder log, HEAD==origin/main and clean tracked files.

## Exit contract

Return separate factual states: `DYNAMIC_ATLAS_4X4_SOURCE` PASS/FAIL, `MANDATORY_SPLIT_ALL_PATHS` PASS/FAIL, `V3_LOCKED_PALETTE` PASS/FAIL, `MAX_COLORS_ADJUSTABLE_3_12` PASS/FAIL, `VARIABLE_FRAME_SIZE_51_64` PASS/FAIL, `ALPIX_UNCHANGED` evidence, `PIXEL_ART_GUI_NOT_RUN` (until real test), `PIXELLAB_PAID_PRO_API_NOT_RUN`, `INSTALLED_RELEASE_APPLY_NOT_AUTHORIZED`. Do not mark level READY without actual solver/WIN. Do NOT start a fresh milestone or keep creating paper-only R11/R12 loops.

Official references: https://api.pixellab.ai/v2/openapi.json and https://www.pixellab.ai/docs/tools/create-sl-image-pro .
