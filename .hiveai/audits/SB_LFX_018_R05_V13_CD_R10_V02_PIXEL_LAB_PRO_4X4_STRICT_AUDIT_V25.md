# SB-LFX-018 R05 V13-C/D | GPT V25 INDEPENDENT STRICT AUDIT | R10 V02 PIXELLAB PRO 4×4

**Date:** 2026-10-27 Europe/Istanbul
**Evidence SHA under review:** `cce335681ec3c63cd2ca35bbb627ee5ff55ba5b0`
**Reviewed:** R10 product commit `b56fafec978fcf13fbb94b59284282c77a4c8377`, R10 builder report, M03 builder log, source launcher/atlas/adapter/UI, focused test source and `TASKS.md`; official current PixelLab OpenAPI and Creator Pro docs.
**Audit method:** Read actual GitHub main code and report and compare source behavior with owner contract. No owner's Windows process/Release/credential accessed, no local Python/Godot test performed by GPT, no billable PixelLab request sent.

## VERDICT
**R10 V02 CONDITIONALLY ACCEPTED FOR SOURCE-LEVEL OFFLINE WORK, NOT ACCEPTED FOR PAID OR INSTALLED STUDIO USE.** Builder's focused mock tests 45/45 PASS and AST 7/7 PASS are credible logged evidence, not independent test execution. Mandatory atlas assembly/re-slicing is implemented in `pixellab_pro_atlas.py`: `export_frames -> normalize_frames -> _persist_atlas -> inspect_atlas -> 16 pixel-exact slices`; `export_atlas` splits imported atlas; Photopea ZIP `export_photopea_zip -> frames_from_photopea_zip -> export_frames` also assembles/re-slices. The source enforces 51..59 W and H, V3 palette, per-frame max 3..12, alpha/occupancy and 16 independent PNG records. Historical Pro Flash active dispatch rejects new use, ALPIX provider route remains in source. BUT owner GUI/installed Release, real ALPIX availability, real PixelLab API/credential/billing, true imported Photopea ZIP and solver/WIN/QA were not run.

## GitHub provenance
Main observed `cce335681ec3c63cd2ca35bbb627ee5ff55ba5b0`. Product/test commit `b56fafec978fcf13fbb94b59284282c77a4c8377` changes Pixel Art UI GDScript, launcher, `studio_extensions.py`, `pixellab_pro_atlas.py`, test files. Report commit `55bd0f44`, append-only builder evidence `c1312907`, publication receipt `cce33568`. Report states 45/45 selected offline tests passed, with earlier fixture/adapter failures fixed in the same source revision. No native Godot code execution after edited GDScript; parse AST checks on Python files cannot validate GDScript compile/runtime.

## Source contract pass, within limitations
1. PixelLab Pro `/v2/generate-image-v2` request asks for exact W/H 51..59 each, `target_palette` canonical 16 C IDs, owner-selected max 3..12, `no_background`; 16 inline frames required and background job polled by GET, no POST retry inside adapter.
2. `normalize_frames` creates a true 4×4 4W×4H composite and `_persist_atlas` always extracts sixteen W×H crops even when API returns sixteen frames. A real raw atlas and coordinate-labelled ZIP similarly pass through the splitter. No resize or remap; RGBA bytes compared in memory. Each source has separate intake status and recorded hashes.
3. Only PASS frames are imported into existing source library via `extensions.batch_import`; none is labeled READY in the R10 source route. Level Factory solve/replay/difficulty/QA is NOT invoked by this path; explicit later job/run remains necessary for READY.
4. Fixed game max 59, independent W/H 51..59 Pro 16-grid intersection. Official REST documentation lists 51..64 for 16 frames, but that does NOT authorize >59 game sizes. Creator browser screenshot's ten generations do not prove API wallet costs.
5. Provider picker leaves ALPIX route present; no live Claude/MCP or old subscription-runtime test. Photopea ZIP accepts strict position-labelled names such as sprite-01..16 or row-1-col-1..4, but actual unmodified Photopea All Slices ZIP filename structure has not been evidenced to conform.

## HIGH-SEVERITY LIVE BILLING SAFETY FINDING: incomplete job deduplication

File: `level_factory/scripts/factory_core_launcher.py`, function `_semantic_generate_pixellab_pro_4x4`.

A durable `job_record` is written before POST and the same operation_id is protected. However cross-operation matching of an identical request checks only `uncertain_states = {"SUBMITTING", "SUBMISSION_UNKNOWN", "POLL_TIMEOUT", "POLL_NETWORK_ERROR"}`.

**It omits `POLLING`, `NORMALIZING`, `POST_SUBMISSION_ERROR`**, each of which can represent a provider POST that has already been accepted and charged. Example: job A is posted, accepted, `on_job_accepted(job_id)` stores `POLLING`, Studio crashes, user clicks Generate again and UI gives a fresh operation ID. Cross-operation request digest matches but `POLLING` is not in the set, so it can submit a second paid POST. Equivalent risk for `NORMALIZING` after job success and `POST_SUBMISSION_ERROR` following a post-response failure. The adapter itself never POST-retries, but UI/new operation repetition can still charge again. The reported focused tests check repeated **same** operation_id and mocked adapter, but not identical SHA across different operation IDs and persisted `POLLING` or `NORMALIZING` states. **Do not authorize a paid PixelLab E2E until this fail-closed safety gap is fixed and regression-tested.**

Suggested contract: durable accepted/uncertain/success and unknown-after-POST records for identical digest must block automatic resubmission across operation IDs, with a safe explicit recover/poll-by-job-id path. Never "fix" by blindly deleting old records or allowing auto-resubmit on timeout. A deliberately new owner-approved generation with same prompt may require a separate explicit distinct-intent/confirmation; duplicate accidental retry must not be silently treated as new work.

## Other open items

- `PIXEL_ART_GUI_NOT_RUN`: no Godot 4.7.2 scene/native/installed UI test, recent GDScript edit is unparsed natively.
- `INSTALL_BLOCKED_MANIFEST_DRIFT`: installed `verify.py` unknown authority; `PROCESS_QUIESCENCE_UNPROVEN`. Release `-Apply` still not authorized.
- `PIXELLAB_API_TOKEN_NOT_CONFIGURED` was previous R09 Windows status; no R10 read/secret verification, do not claim READY.
- Paid API cost/credits and resulting true output format remain unknown; account owner must approve exact spend separately.
- Photopea actual ZIP export naming vs strict expected positional naming not proven. Either support authentic output with verified deterministic position or give a non-destructive renaming/mapping UI; don't guess positions.
- `ALPIX_UNCHANGED` is only a source-level claim. The previously reported `ALPIX_PLUGIN_MISSING` real local readiness is unresolved and must not be advertised as working.
- Original owner 140 job COMPLETE 102 READY / 4 FAILED / 34 REJECTED and Pool 131 JSON untouched per builder; independent GPT cannot directly rehash owner Windows files.
- Full 224×224 source samples from prior conversation are not equivalent to a Godot native playable/WIN result; these 16 images per atlas remain SOURCE candidates.

## Actionable next step
**Do NOT rerun R10 V02 or advance to a new milestone just for report-writing.** A narrowly scoped R10 V03 source safety correction is justified before ANY paid generation: (a) test/fix cross-operation billable replay after `POLLING`, `NORMALIZING`, `POST_SUBMISSION_ERROR` and persisted failures with a bounded recovery path; (b) ensure one intentional owner approval is required for genuinely new identical-prompt jobs, not an unguarded retry; (c) test default Photopea ZIP filenames against a real ZIP if one exists without inventing that evidence; (d) no Godot/paid API/Release until separate consent and safe migration. A syntax-only offline GDScript static review can be completed; native runtime remains untested.

**Final disposition:** `R10_V02_SOURCE_IMPLEMENTED_OFFLINE_BUILDER_TESTS_45_45`, `R10_V02_V25_AUDIT_CONDITIONAL_PASS_BILLING_GUARD_GAP`, `PIXELLAB_LIVE_GENERATION_BLOCKED`, `INSTALLED_GUI_OPEN`, `ALPIX_REAL_AVAILABILITY_UNKNOWN`.

Source links:
- R10 builder report: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R10_V02_PIXEL_LAB_PRO_4X4_ATLAS_AUTOMATION.md
- Product patch: https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/b56fafec978fcf13fbb94b59284282c77a4c8377
- PixelLab OpenAPI: https://api.pixellab.ai/v2/openapi.json
- Creator docs: https://www.pixellab.ai/docs/tools/create-sl-image-pro
