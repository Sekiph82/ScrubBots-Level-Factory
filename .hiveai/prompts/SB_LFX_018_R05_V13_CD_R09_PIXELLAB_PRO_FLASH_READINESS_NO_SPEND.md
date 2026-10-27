# SB-LFX-018 R05 V13-C/D R09: PixelLab Pro Flash V2 no-spend readiness
Document role: GPT-authorized Codex builder prompt. 2026-10-27, Europe/Istanbul.
Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Only canonical Windows checkout: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator
Root TASKS.md: GPT-owned, Codex READ ONLY.
Current V23 audit: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R08_V03_GODOT_NATIVE_PARSE_INDEPENDENT_AUDIT_V23.md
Previous R08 native evidence: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R08_V03_NATIVE_PARSE_EVIDENCE.md
Append-only M03 builder log: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md

## Goal
The owner clarified the next practical goal: generate new 32x32 pixel-art images with PIXELLAB through the PIXEL ART tab, not ALPIX/Claude. R08 V03 has ALREADY run one real Godot GDScript parser successfully; DO NOT rerun or confuse this with PixelLab readiness. The single-use Godot user-cache write permission is consumed. Determine actual no-spend readiness and exact remaining gaps before the owner authorizes a chargeable image.

## Hard safety locks
NO PixelLab generation, paid API call, account-credit usage, job submission, live API trial, automatic retry or credit-balance probe. No provider secrets displayed, logged, uploaded or hashed. Do not treat PixelLab Creator/MCP login as proof of the local Python worker credential. No new native Godot invocation/editor/installed Studio GUI; no Release -Apply/manifest write/known verify.py mismatch bypass; no paid ALPIX/Claude, CI/Actions, R2/production, new TEMP/worktree/clone or broad disk cleanup. No original 140 PNG/job/Pool operation or worker/process termination. Codex must not edit TASKS.md, used prompts, prior audits or earlier builder log text.

## Step A: latest canonical sync
Read TASKS.md, V23 audit, this prompt and only relevant PixelLab code. Inspect git origin, status, branch, owner-untracked data, stashes. Fetch origin/main and fast-forward ONLY when safe, without reset/clean/rebase/force. If branch is diverged, do not secretly rewrite; report exact issue and use only established owner-approved safe merge procedure if demonstrably valid.

## Step B: real local credential status only
Read the source routes in level_factory/scripts/factory_core_launcher.py (provider-options and PixelLab generation), src/scrubbots_pixel_factory/studio_extensions.py (pixellab_secret_status, generate_pro_flash_image), and level_factory/scripts/factory_studio_exact_ui.gd (PIXEL ART controls). Safely obtain ONLY PIXELLAB local credential presence/configuration state using a no-network, no-bytecode, no-cache helper if possible; allowed status READY_CREDENTIALS_CONFIGURED, PIXELLAB_API_TOKEN_NOT_CONFIGURED, PIXELLAB_CREDENTIALS_CONFLICT or UNKNOWN. Windows Generic Credential target ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN, separate from PixelLab web/MCP account sign-in. Never reveal/print token, credential blob or sensitive env values. Avoid full provider-options if it invokes unnecessary ALPIX/Claude helpers.

## Step C: no-paid generation route contract
Check actual Studio Pixel Art selected provider, Pro Flash V2, owner fixed 32x32 policy, no Style button, canonical 16-color V3 allowed palette, at most 12 distinct used colors, binary alpha, exact output dimensions and PNG saving/preview. Source backend accepting more sizes is NOT proof UI enforces 32x32. Trace Generate -> consent/cost warning -> single job submit/poll -> validation -> owner-safe output. No real API calls, no duplicate charge, no automatic retries, no overwrites of original 140 PNG, job or Pool. Inspect source-vs-installed Release import/dependency completeness read-only; missing verify.py receipt and real writer exclusion still block install. Do not call installed GUI 'PASS' without running it under a later separately authorized scope. Check current source syntax fix is present; R08 native parse only showed one GDScript syntax PASS, not provider or runtime GUI.

## Step D: minimal tests, reporting and publication
Only bounded offline synthetic/source checks if warranted; Python -B and pytest -p no:cacheprovider; no provider network. If a safe and justified source-only fix is required, implement narrowly and test it, but NEVER touch Release/manifest or run Godot again. Publish one concise status report under docs/process and append genuine new evidence to the same M03 builder log. Clearly label PIXELLAB_LOCAL_CREDENTIAL_STATUS, PIXELLAB_SOURCE_ROUTE, PIXELLAB_INSTALLED_GUI, PIXELLAB_PAID_E2E_NOT_RUN. Note PixelLab backend status does not prove available credits or fixed cost. Owner must separately authorize one charged 32x32 Pro Flash image and use of credits after validating readiness. Preserve truthful Godot global log side effects from V23. Publish via nonforce ancestry-safe main push, verify 0/0 tracked clean; no second reporting-only cycle.

Final compact builder response: R09_PIXELLAB_ZERO_SPEND_READINESS_PASS or BLOCKED, status-only credentials, precise source/UI/install gaps, INSTALL_BLOCKED_MANIFEST_DRIFT, PROCESS_QUIESCENCE_UNPROVEN, PIXELLAB_PAID_E2E_NOT_RUN, SHA and report link. GPT separately audits and controls TASKS.md.