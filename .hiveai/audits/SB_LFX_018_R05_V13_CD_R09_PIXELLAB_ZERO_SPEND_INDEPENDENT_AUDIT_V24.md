# SB-LFX-018 R05 V13-C/D | GPT V24 INDEPENDENT AUDIT | R09 PIXELLAB ZERO-SPEND READINESS

**Date:** 2026-10-27 (Europe/Istanbul)
**Source under review:** `eeaba621fd8e4dfb940e4fa2456bdfab473e394c`
**Audit scope:** GitHub-published R09 report, builder log, R09 code/test diff and prior task authority; not a live Windows/PixelLab account verification.

## Verdict

**PASS for R09's authorized SAFE SOURCE CHANGES and HONEST NO-SPEND REPORT, not for PixelLab real generation readiness.** Owner's 32×32 policy is now guarded in UI selection/size/Generate/confirmation and before the actual source launcher dispatch. Python parser fixes use the canonical eight-byte PNG signature (\x89PNG\r\n\x1a\n). R09 report says 14 mock/offline tests passed, with three temp-path-dependent tests excluded. No live PixelLab API request, provider authentication, cost inquiry, Godot GUI or installed Release migration was run. The parent's image generation readiness remains BLOCKED by absent app-local credential and outdated installed Release, with `verify.py` drift and writer exclusion not solved.

## Provenance / publication

GitHub main confirmed `eeaba621fd8e4dfb940e4fa2456bdfab473e394c`. R09 product/test commit `2e41598da0555801047544404e92736a27c2fa82` changed only:
- `level_factory/scripts/factory_core_launcher.py`, Pro Flash request reject if width/height not 32;
- `level_factory/scripts/factory_studio_exact_ui.gd`, PixelLab 32×32 selection, size dialog and confirmation;
- `src/scrubbots_pixel_factory/studio_extensions.py`, correct eight-byte PNG header in both result extraction and validation;
- `tests/unit/test_pixellab_pro_flash_v12.py`, new offline dimensional guard and UI source assertions.
Report commit `3c2d285c51bb7b9030becfb491f5bae35839d61f`, log receipt `52a4f4507862c2a78a982145`, final main `eeaba621...`. GitHub source reviewed directly, but owner Windows 0 ahead/behind, runtime token status and owner untracked preservation remain builder reports.

## Separate Desktop folder

R09 builder traced `C:\Users\sekip\Desktop\ScrubBots-factory\060-m43-078-shop` to **an independent SCRUBBOTS game Godot project**, with a `.git` worktree pointer outside the two approved roots. Seventeen limited level_factory/content_pipeline paths SHA-compared; three same-relative-path byte conflicts (`level_factory/README.md`, `level_factory/project.godot`, `content_pipeline/README.md`) and fourteen documents/configs from a separate project. No files copied; protected source and destination left intact. **This is a justified no-copy disposition**, not failed merging: merging unrelated project manifests/game source would corrupt provenance. Auditor cannot independently inspect Windows folder; accepts evidence/report's consistent classification.

## Focused test distinction

Builder's pre-fix synthetic suite exposed six cases that rejected valid standard PNG signatures. After focused fix and policy tests, selected cases `14 passed`; three requiring `tmp_path` were deliberately not run to prevent TEMP changes. These are mock/offline checks; no live provider network/credit test, no runtime Godot GDScript parse *after the new UI modification*, and no installer/GUI verification. Therefore source change scope PASS, full functional E2E remains OPEN. Do not label unrun test cases passing.

## Readiness blockers and exact implications

1. `PIXELLAB_API_TOKEN_NOT_CONFIGURED`: status-only credential check by builder, no value read or exposed in report. Existing app source looks for environment `PIXELLAB_API_TOKEN` / `PIXELLAB_SECRET` or Windows Generic Credential target `ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN`; PixelLab Creator/MCP sign-in is not this worker secret. Only the user can securely configure real token; no user secret is to be sent through ChatGPT/GitHub/CodeX logs.
2. Source PixelLab Pro Flash route and fixed 32×32 are present, but **installed** launcher, adapter and GDScript differ by SHA and cannot claim installed GUI functional PASS.
3. `INSTALL_BLOCKED_MANIFEST_DRIFT`: `verify.py` present bytes mismatch absent authorized per-file receipt. `PROCESS_QUIESCENCE_UNPROVEN` for old/direct writer entrypoints. `Release -Apply` remains separately unauthorized, and no safe physical transaction was run.
4. `PIXELLAB_PAID_E2E_NOT_RUN` credit cost/balance and actual endpoint acceptance unknown. The UI's cost warning cites a prior 5-credit operation only as historical, **not a current cost guarantee**.
5. Original 140 COMPLETE=102 READY, 4 FAILED, 34 REJECTED, 0 pending, protected; Pool=131 JSON is not 131 READY images.

## Risk / advice

Do not repeat R09 or demand that independent game content be merged. No value in running another unchanged offline test campaign. The immediate owner action is to configure the local PixelLab API token in Windows Credential Manager (not a chat secret), then use a narrowly authorized, one-shot source-path generation plan **only after explicit owner approval for exactly one potentially billable PixelLab request**. A source-based route may avoid the separate installed Release drift blocker, but whether it safely works must be verified in the owner environment; this is NOT permission to call it. Using installed Studio GUI requires a future separately authorized and actually safe Release migration and GUI test. No Actions/CI, auto-provider spend or original batch rerun.

## Final

**R09 source/no-spend scoped task accepted; PixelLab image production not ready in installed Studio.** Prefer stop pointless source-only loops, present a concrete token setup action and bounded next-owner-choice (one paid source-based trial vs separately gated installed GUI update). Do not automatically debit credits, alter Release or claim PixelLab success.

Links:
- [R09 builder report](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R09_PIXELLAB_ZERO_SPEND_READINESS.md)
- [R09 source commit](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/2e41598da0555801047544404e92736a27c2fa82)
- [R09 builder log](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md)
