# SB-LFX-018 R05 V13-C/D | V23 INDEPENDENT AUDIT | R08 V03 NATIVE SCRIPT PARSE

**Document role:** GPT independent GitHub evidence audit
**Date:** 2026-10-27 Europe/Istanbul
**Repository:** https://github.com/Sekiph82/ScrubBots-Level-Factory
**Source publication base reviewed:** `e22d72bd7532bfbb8d4ee29aed557ccc6c3acd95`
**Method:** Actual GitHub tracked R08 V02/V03 evidence, builder log, task tracker and relevant provider source inspected; no Windows owner process, local account/credential, installed Studio or provider API independently executed.

## 1. Verdict
**PASS WITH DISCLOSED SIDE EFFECTS FOR ONE NARROW GODOT 4.7.2 GDSCRIPT SYNTAX PARSE ONLY.** R08 V03 builder evidence reports a single `--headless --path ... --script res://scripts/factory_studio_exact_ui.gd --check-only` invocation, exit 0 in 0.43 s, no stderr. R08 V02 had previously exposed and repaired a concrete one-character syntax problem; V03 reconfirmed that exact source script parses. The one-time owner permission is consumed. **PixelLab image generation, provider credentials, paid job submission, actual installed Studio UI, runtime scene/import, Level Factory and 240/480 solver lifecycle are NOT verified.** Parent milestone remains OPEN.

## 2. Authorization and historical tasks
The owner separately approved one bounded Godot parse plus narrowly attributable Godot-generated global cache/config changes. R01–R07 work stays closed. Neither this approval nor successful syntax parsing granted additional Godot invocation, Release `-Apply`, paid PixelLab generation, CI or original 140-image replay.

## 3. GitHub scope
Read `docs/process/SB_LFX_018_R05_V13_CD_R08_V02_NATIVE_PARSE_BUILDER_EVIDENCE.md`, `docs/process/SB_LFX_018_R05_V13_CD_R08_V03_NATIVE_PARSE_EVIDENCE.md`, the appended builder log `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`, root `TASKS.md`, `level_factory/scripts/factory_studio_exact_ui.gd`, `level_factory/scripts/factory_core_launcher.py`, and `src/scrubbots_pixel_factory/studio_extensions.py`. R08 V02 source correction was separately published; R08 V03 claims no product source changes.

## 4. Native evidence
Reported current real Godot binary: `Godot_v4.7.2-stable_win64.exe`, engine banner `Godot Engine v4.7.2.stable.official.ed1daf0bf`. Owner-script path `res://scripts/factory_studio_exact_ui.gd`. Builder reports R08 V03 one invoke with `--check-only`, exit 0, elapsed 0.43 seconds, empty stderr; no editor `--import`, GUI, generation, solver, or provider call. **Auditor did not reproduce the native run on Windows**; accepted only as internally consistent builder evidence, not independent execution.

## 5. Global Godot side effects
Builder's bounded before/after SHA inventory found only attributable-or-time-correlated changes under owner-approved `%APPDATA%\Godot`:
- New/modified `app_userdata\ScrubBots Factory Studio\logs` and `app_userdata\SCRUBBOTS\logs` files;
- Three pre-existing dated Godot logs disappeared;
- Transient `.recovery_mode_lock` was present during one inventory and later absent.
No automatic cleanup or restore attempted, as instructed. The **exact cause of each log deletion is unproven**, and full original before-hashes of deleted log files were not persisted as independent artifacts. Do not claim that all existing Godot logs were preserved. Existing source/project/cache sidecars, six Release manifests, original COMPLETE 140-job and 131-file Pool were reported byte-unchanged at the bounded verification points.

## 6. Scope of code readiness vs PixelLab service
`level_factory/scripts/factory_core_launcher.py` has a PixelLab Pro Flash generation route and `provider-options` operation; `src/scrubbots_pixel_factory/studio_extensions.py` includes Windows Generic Credential Manager target `ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN`, credential presence/status logic and PixelLab API handling. **The parser test never checks the credentials, network response, PixelLab account/credits, endpoint success, image quality, palette validation through real response, generation save path, UI availability or installation.** PixelLab Creator/MCP login is separate from this app's local worker token configuration. No user PixelLab token or credit balance may be inferred from code alone.

## 7. Remaining product and Release gates
`INSTALL_BLOCKED_MANIFEST_DRIFT`: installed `verify.py` differs from manifest expected and no approval receipt proven; `PROCESS_QUIESCENCE_UNPROVEN` for all legacy writers; `RELEASE_APPLY_NOT_AUTHORIZED`; `INSTALLED_GUI_OPEN`; no real paid/authorized PixelLab Pro Flash run, no source image output, and no complete V13 acceptance.

## 8. Integrity, limitations and risk
One-line source syntax fix reported in R08 V02 and reviewed by current source. The R08 V03 hash set is builder-reported, no independent owner filesystem inspection. Hash-visible removal of pre-existing dated Godot logs deserves preserving in audit, not silently converting to 'zero writes'. Repeated native parsing would need new owner authorization. Original owner job baseline: 140 COMPLETE, 102 READY, 4 FAILED, 34 REJECTED, zero pending; Pool 131 JSON is not 131 accepted READY.

## 9. Final disposition
**R08 V03 SINGLE GDSCRIPT PARSE SOURCE GATE PASS WITH DISCLOSED GLOBAL LOG CHANGES; parent V13-C/D still OPEN.** Do not repeat R08. A next separately authorized, **no-paid-call PixelLab readiness preflight** can be limited to read-only local provider-options status, configuration-presence-only checks (never reveal token), PixelLab Pro Flash v2 configuration/contract, safe UI/install gap review and an explicit owner's opt-in before any chargeable image generation. If the user uses PixelLab Creator directly outside the Studio, that is distinct from claiming the ScrubBots Factory Studio is production ready.

## 10. Links
- [R08 V03 actual builder evidence](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R08_V03_NATIVE_PARSE_EVIDENCE.md)
- [R08 V02 parse and fix](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R08_V02_NATIVE_PARSE_BUILDER_EVIDENCE.md)
- [Builder log](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md)
