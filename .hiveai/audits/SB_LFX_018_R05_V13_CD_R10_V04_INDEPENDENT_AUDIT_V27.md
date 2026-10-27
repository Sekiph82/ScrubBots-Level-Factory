# SB-LFX-018 R05 V13-C/D | GPT INDEPENDENT V27 | R10 V04 PIXELLAB FIRST-USE / ALPIX DISCOVERY

**Date:** 2026-10-27, Europe/Istanbul
**GitHub main inspected:** `4cb823f02a562647c9c630d19bc45941b457c1ea`
**Source/test commit:** `72bb6c0871eec24d2f92f8a1c1260d29d6517bf3`
**Evidence:** builder's R10 V04 report and append-only M03 log, tracked source and test diff, root TASKS. Independent GitHub review only; no Windows owner filesystem/Claude sessions/API/Godot/installed Studio operated by the auditor.

## Independent verdict

**R10 V04: PASS for its authorized source + offline-test scope, NOT a pass for actual PIXEL ART production or ALPIX generation.** Builder's final focused offline test run **70/70** and five-file Python AST **5/5** were documented, and GitHub diff corroborates relevant changes. The source-level missing-credential claim poisoning identified in V26 is corrected: it checks parameter and presence-only credential state before `job_root.mkdir`, any new job JSON or SHA claim. When status is NOT_CONFIGURED or CONFLICT it returns explicit `paid_submission_possible=False`, `job_record_created=False`, `digest_claim_created=False`. The focused regression tests missing token -> simulated configured token -> identical request -> one mock submission. Existing paid-uncertainty, two-process atomic claim, cross-operation guard and GET-only recovery remain in source and final focused mock tests.

**ALPIX is NOT restored.** Read-only current Windows environment, per builder, has Claude Code `2.1.287` installed at `C:\Users\sekip\.local\bin\claude.exe`, but **NO enabled ALPIX MCP server or plugin** in inspected user/project scopes: `ALPIX_PLUGIN_MISSING`. Source now probes explicit project `.mcp.json` and `.claude/settings(.local).json`, reading only identity names. If it finds a route, it labels `ALPIX_AVAILABLE_DISCOVERY_ONLY` / `CLAUDE_SESSION_UNVERIFIED`, not working live generation. The separate ChatGPT Alpix integration is NOT proof that a Claude Code MCP plugin is installed. A legitimate owner-authorized connection or installation is still needed to restore previous ALPIX Studio functionality.

## Actual code review and evidence

- `level_factory/scripts/factory_core_launcher.py`: validates prompt/style/seed and dimensions, computes request digest, inspects prior immutable records, then does `pixellab_secret_status()` before the durable digest claim and job record; invokes adapter only if presence check says configured. The preflight does not inspect raw credential text.
- `src/scrubbots_pixel_factory/alpix_batch.py`: `discover_alpix(user_home,project_root)` probes specifically owner-intended project-level and user-level settings and MCP names. Missing route reported accurately and no fake registration written. `generate_alpix_png` can now pass the intended canonical project cwd when explicitly invoked; no paid/user session invoked in R10 V04.
- `tests/unit/test_pixellab_pro_4x4_v02.py`: one mock test models first-use exact-intent retry; explicit conflict-no-job and preservation of historical unpaid claim tests.
- `tests/unit/test_sb_lfx_018_r05_v13_offline_regressions.py`: project MCP name only / secret-redacted result, project plugin enablement, unread scope and CLI missing cases. One older static label assertion updated to match existing UI source, not evidence of GUI runtime.
- `docs/process/SB_LFX_018_R05_V13_CD_R10_V04_PIXELLAB_CREDENTIAL_PREFLIGHT_ALPIX_DISCOVERY.md`: builder notes final 70/70, earlier failures and mock corrections without hiding them, no actual provider connection.
- GitHub final main SHA `4cb823f02a562647c9c630d19bc45941b457c1ea` contains product/report/log receipts. Builder's 0/0 branch parity and preservation of 3,003 untracked owner paths are builder assertions, not independently observed on Windows.

## Acceptance matrix

| Goal | Result | Boundary |
| --- | --- | --- |
| No credential or conflict creates no new chargeable claim | **SOURCE PASS** | Mocked tests, source inspection |
| First configured-token retry of identical intent | **MOCK PASS** | No actual credential or billable API used |
| Atomic digest and post-submission safety preserved | **MOCK PASS** | No real provider billing guarantee |
| Project-scoped ALPIX discovery | **SOURCE PASS** | No actual project ALPIX integration present |
| Actual ALPIX Claude plugin/MCP available | **BLOCKED** | `ALPIX_PLUGIN_MISSING` on inspected owner machine |
| Real PixelLab credential | **NOT CONFIGURED per builder** | Account credits and API auth not tested |
| Actual PixelLab Pro 4×4 image | **NOT RUN** | Requires token + owner spending authorization |
| Actual Photopea all-slices ZIP | **NOT VERIFIED** | No authentic ZIP supplied |
| Installed Factory Studio PIXEL ART runtime | **NOT RUN** | Godot GUI and Release apply not authorized |
| Full Level Factory solver/WIN/QA and true READY | **NOT RUN** | No new playable level proof |

## Important limitations

1. Presence-only token check is not API authorization; between check and actual adapter call local credentials could change. The permanent digest claim remains fail-closed after an ambiguous failure; do not loosen this without evidence. Historical known-unpaid claims intentionally require owner review, not automatic delete.
2. The source discovery checks configured names, not MCP handshake/session/billing/Claude quotas; `ALPIX_AVAILABLE_DISCOVERY_ONLY` must never be advertised as confirmed working integration.
3. Some ALPIX configuration layouts or named plugins outside approved scopes might still exist; the Windows inspection proves no ALPIX route in *inspected* settings, not a universal proof that Alpix as a service is discontinued.
4. Owner requested 4×4 PixelLab Pro with frame W/H 51..59, immutable canonical 16-color V3, max-used 3..12, normalized atlas ALWAYS sliced to sixteen frame PNGs; R10 V04 did not change these contracts. Those are source pipelines only until installed GUI tests.
5. Real Release remains **INSTALL_BLOCKED_MANIFEST_DRIFT** because installed `verify.py` differs from manifest without legitimate receipt, and **PROCESS_QUIESCENCE_UNPROVEN** for legacy writer entrypoints. No `Release -Apply` permission. R08 one-time Godot native permission consumed. 140 job COMPLETE=102 READY/4 FAILED/34 REJECTED; Pool 131 JSON and original PNGs reported protected.

## Next action, not another duplicate source test cycle

**End R10 V04. Do NOT task Codex to repeat R01–R10 V04, run 70 mock tests again, or fabricate ALPIX setup.** The shortest route to owner's actual Factory Studio goals is external runtime prerequisites: (A) configure real PixelLab worker token locally via Windows Generic Credential target `ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN` (no token pasted into chat/GitHub), (B) restore an authentic ALPIX Claude Code plugin or MCP endpoint in the appropriate owner-approved project/user scope (not by inventing server name/config), and (C) separately authorize safe installed Release repair/Studio native GUI test after real writer exclusion and hash/receipt reconciliation. This may require separate explicit owner authorization for account/plugin configuration, actual global Godot writes or managed Release migration. A successful real 16-image PixelLab generation additionally requires express approval of its possible actual API charge, which may NOT equal the Creator web UI's 10-generation count. One real Photopea slice ZIP fixture is necessary before asserting import compatibility.

**V27 final:** `R10_V04_SOURCE_ACCEPTED`, `PIXELLAB_TOKEN_NOT_CONFIGURED`, `ALPIX_PLUGIN_MISSING_ON_INSPECTED_CLAUDE_CODE`, `INSTALLED_STUDIO_GUI_OPEN`, `PIXELLAB_PAID_API_NOT_RUN`, `RELEASE_APPLY_BLOCKED`.

Links: [R10 V04 builder report](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R10_V04_PIXELLAB_CREDENTIAL_PREFLIGHT_ALPIX_DISCOVERY.md), [R10 V04 source diff](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/72bb6c0871eec24d2f92f8a1c1260d29d6517bf3), [Claude MCP scopes](https://code.claude.com/docs/en/mcp), [Claude settings scopes](https://code.claude.com/docs/en/settings).
