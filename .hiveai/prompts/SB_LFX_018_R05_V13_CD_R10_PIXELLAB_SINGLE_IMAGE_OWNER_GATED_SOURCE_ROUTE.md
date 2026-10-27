# SB-LFX-018 R05 V13-C/D R10 | PIXELLAB 32x32 SINGLE-IMAGE OWNER-GATED PATH

**Document role:** GPT Codex handoff, conditional execution only
**Date:** 2026-10-27 Europe/Istanbul
**Repo:** https://github.com/Sekiph82/ScrubBots-Level-Factory
**Only local checkout:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
**GPT-owned tracker:** root `TASKS.md`, Codex READ-ONLY
**Independent V24 R09 audit:** https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R09_PIXELLAB_ZERO_SPEND_INDEPENDENT_AUDIT_V24.md
**Existing R09 readiness report:** https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R09_PIXELLAB_ZERO_SPEND_READINESS.md
**Append-only M03 builder log:** https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md

## Authority status and target

**PENDING TWO EXPLICIT OWNER GATES. R10 paid stage MUST NOT auto-run solely because this prompt is in GitHub.** Gate 1: owner puts their own PixelLab API token (not PixelLab Creator/MCP-only sign-in) in **Windows Generic Credential target `ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN`**, user name `token`, secret in Windows only. Do NOT ask to paste/show token in ChatGPT, GitHub, Codex logs or command line. Gate 2: owner explicitly authorizes **one potentially billable PixelLab Pro Flash v2 32x32 request**, knowing exact current debit is not independently confirmed, and chooses whether initial one-shot may use **canonical source-level direct launcher without installed Studio GUI**. Without Gate 2, NO network request, no paid image.

Owner wants actual pixel-art creation, not repetition of R09. R09 corrected PNG signature, fixed PIXELLAB UI/worker requests at 32x32, mock tests 14 PASS, but app credential `PIXELLAB_API_TOKEN_NOT_CONFIGURED` and installed Studio Release drift remain. A source-level one-shot trial is a potential faster path to a new PNG, **not** installed GUI acceptance and NOT proof it works until actually tested.

## First safe actions only after owner gate is explicitly recorded

1. Safely check current `TASKS.md` queue guard, this exact tracked prompt, canonical checkout, SHA/ff-only origin main and protected untracked data. Never new clone/worktree/TEMP/rebase/reset/clean/force. Do not mix the separately inventoried `ScrubBots-factory` game project into Factory. R09 original 140 COMPLETE=102 READY/4 FAILED/34 REJECTED/0 pending and Pool 131 JSON stay untouched. Do not run R01–R09 again.
2. Perform a **status-only** local worker credential presence check using existing `pixellab_secret_status()` or safest exact equivalent; never log, hash, emit, dump, upload or compare token content. Do not run ALPIX discovery if unnecessary. If `PIXELLAB_API_TOKEN_NOT_CONFIGURED` / CONFLICT, return OWNER_TOKEN_SETUP_REQUIRED and STOP without test code or report-only iteration.
3. If credential presence READY, inspect current canonical source `factory_core_launcher.py` and `studio_extensions.py` to locate existing exact support for one durable unique-operation-id PixelLab Pro Flash v2 request and valid 32x32; local destination must be NEW noncolliding image/job record UNDER canonical `level_factory/output/semantic-generated` or an existing verified safe project output. Do not invent an execution CLI or blindly construct POST payload. Need protective operation dedup/no retry and preservation of original 140. Can run a **fully offline** dry-run with synthetic provider response only if it verifies a genuinely new untested launcher/output gap; no paid call. No more repeated unchanged mocks.
4. If Gate 2 (separate owner express approval of ONE paid source-direct image, prompt/image subject, potential credit spend) has NOT been given, stop exactly at `AWAITING_OWNER_ONE_PIXEL_LAB_PAID_IMAGE_APPROVAL`; provide the evidence that credential exists and source path is ready, no job submission. Do not infer this approval from old 2,000-credit subscription, past 5-credit examples, or this prompt.
5. Once BOTH gates are explicitly met: one 32×32 Pro Flash v2 generation through existing canonical SOURCE launcher only if its safe noncollision path and durable operation ID are demonstrated. Record request before POST, submit **once**, poll same returned job ID, no automatic POST retry if outcome unknown. Validate image 8-byte PNG signature, exact 32x32, V3 canonical 16-color palette allowing at most 12 distinct used colors and alpha 0/255, record result to new safe path without touching installed Release, the original 140 job, or Pool. Report exact observed debit only if confirmed in user-visible provider response, otherwise UNKNOWN. Owner-selected prompt must be used; do not improvise a paid test prompt if owner has not provided one. On partial/unknown submission, never issue second POST.
6. Only if any actual new source/test/image result happened, publish accurate source/test evidence under `docs/process/` and append M03 builder log, normal safe nonforce main; don't commit generated owner image, secrets or binary unless specifically owner-authorized. No extra pointless report-only tasks.

## Absolute locks

**Do not install or update Release; `verify.py` manifest mismatch remains `INSTALL_BLOCKED_MANIFEST_DRIFT` and global legacy-writer exclusion `PROCESS_QUIESCENCE_UNPROVEN`.** Source-generated PNG in canonical output does NOT mean `PIXEL ART` installed GUI is ready; owner GUI requires a separate safe installer authorization and runtime visual test. No Godot process/editor/parse, installed Studio GUI, CI/Actions, paid ALPIX/Claude, R2/prod, secondary-folder deletion, Windows processes kill, original PNG remake, broad cleanup, unsafe files, or changing GPT-owned `TASKS.md`.

Return precisely: local credential READY/NOT_CONFIGURED/CONFLICT, owner charge authorization YES/NO, SOURCE trial ACTUAL one image PASS/FAIL/NOT_RUN, output path if any, installed Studio NOT_VERIFIED, original data preserved, and any true next blocked permission. Source trials are optional and only possible after BOTH separate owner gates.
