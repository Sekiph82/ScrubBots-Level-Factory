# SB-LFX-018 R05 V13-C/D R10 V04 | FIX FIRST-USE PIXELLAB CREDENTIAL CLAIM + RESTORE ALPIX DISCOVERY

**ROLE:** GPT-authorized Codex builder handoff; targeted continuation, not a new milestone.
**DATE:** 2026-10-27 Europe/Istanbul
**REPO:** https://github.com/Sekiph82/ScrubBots-Level-Factory
**CANONICAL LOCAL CHECKOUT ONLY:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
**SOLE TASK TRACKER:** root `TASKS.md`; Codex READ-ONLY.
**INDEPENDENT V26 AUDIT:** https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R10_V03_STRICT_INDEPENDENT_AUDIT_V26.md
**PRIOR R10 V03 BUILDER REPORT:** https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R10_V03_PIXELLAB_PAYMENT_IDEMPOTENCY_FIX.md
**APPEND-ONLY M03 BUILDER LOG:** `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`

## Concrete owner goal

Owner wants to **use Factory Studio PIXEL ART itself** with BOTH PixelLab Pro 4x4 and the previously usable Claude+ALPIX workflow. Do NOT divert to source-direct one-shot as the intended final product. R10 V03 60/60 mocked tests passed and duplicate POST safeguards are in source, but actual installed Studio/Godot remains unverified. This task must fix one proven source usability defect, then inspect and repair (only when supported by actual local evidence) ALPIX Claude connection discovery without spending credits.

## FIRST: direct independently proven R10 V03 defect

Exact file: `level_factory/scripts/factory_core_launcher.py`, `_semantic_generate_pixellab_pro_4x4`.

Before calling the adapter, the source creates a **permanent** `request_digest.claim.json` even if local PixelLab credentials are absent. Adapter then raises `CREDENTIALS_NOT_CONFIGURED` before `on_submission_started` (no POST), and launcher records `PRE_SUBMISSION_ERROR` + `paid_submission_possible=False`, but blocks later owner retry of identical prompt/seed **after a valid token is configured**. Existing focused test `test_known_pre_post_failure_is_marked_unpaid_but_never_auto_reclaimed` establishes this exact first-use failure. This is source-level MAJOR, NOT grounds for relaxing post-POST protection.

**Fix scope:**
1. Safely preflight PixelLab local credential **presence and conflict status only** before acquiring a durable billable digest claim or writing an operation job. Reuse existing source `pixellab_secret_status()`; NEVER print/read/log/export actual credential, request a paid auth endpoint or demand owner paste token to ChatGPT. Validate all remaining no-cost parameters before claim. On absent/conflicting credential, return explicit `PIXELLAB_API_TOKEN_NOT_CONFIGURED` / `PIXELLAB_CREDENTIALS_CONFLICT`, **do not create a claim or job**. Test with offline fake credentials.
2. For old already-existing definitely-unpaid PRE_SUBMISSION_ERROR records/claims, do **NOT** auto-delete or reset them, since original users may rely on history and cross-process races can occur. Provide a *separate, explicit owner-reviewed safe recovery* gate only after verifying both durable marker(s) are FALSE, no job_id, source legacy state, and controlled concurrent writer exclusion. Unknown/corrupt/missing/paid-possible markers must fail closed. If safe historical claim release cannot be implemented within owner-safe scope, report exact manual recovery requirement; do not skip this blocker or fabricate capability.
3. Keep all R10 V03 protections intact: true atomic O_EXCL/digest claim, marker persisted before POST, same/different operation IDs, `POLLING`, `NORMALIZING`, `POST_SUBMISSION_ERROR`, unknown/no job_id, no POST retry, GET-only consent-gated status, legacy V02 guards, cross-process protection. No changes to user original paid records except a verified explicit owner-approved recovery.
4. Add one regression demonstrating `missing token -> no claim -> later fake credential configured -> SAME normalized intent -> single mocked POST possible`, plus unknown/paid job never auto-released, two-process race still one pseudo POST, old no-POST history fail-closed, and no secret leak.

## SECOND: ALPIX + Claude live discovery (READ-ONLY FIRST, owner-local Windows)

Past Factory Studio provider sometimes displayed `ALPIX_PLUGIN_MISSING` despite earlier working Claude+ALPIX. ALPIX code remains in `src/scrubbots_pixel_factory/alpix_batch.py` but uses limited settings file locations; code's discovery is NOT proof the actual currently installed Claude MCP/skill bridge is missing. The user specifically values restoring this provider. This task should therefore:
1. Read owner-local real Claude CLI identity/version and installed-plugin/MCP/skill **STATUS ONLY** from secure read-only Windows sources with bounded queries. Scope to known canonical checkout/user Claude configuration, including project-level `.mcp.json`, `~/.claude.json` and project-scoped entries where accessible WITHOUT exposing tokens/session files, private prompts or secrets. Do not follow external worktree pointer or install/update Claude/ALPIX; do not start billable generation, Claude session or provider tool. Do not modify credentials or run ALPIX provider generation.
2. Match `discover_alpix()` result with actual current CLI/provider status; distinguish `ALPIX_PLUGIN_MISSING`, `CLAUDE_CLI_MISSING`, `CLAUDE_SESSION_UNVERIFIED`, `CONFIG_SCOPE_UNREAD`, `RATE_LIMIT`, `ALPIX_AVAILABLE_DISCOVERY_ONLY`. If actual Claude config proves ALPIX available via supported plugin or project-scoped MCP, fix bounded **discovery-only** false negative with fixture-based offline tests and retain existing prompt/CSV/size semantics. DO NOT merely mark ALPIX available without evidence that selected invocation mechanism is supported. If the *installed* plugin truly absent, report exact actionable owner install/connection requirement, without altering account or speculatively creating a fake ALPIX entry.
3. Preserve ALPIX selectable in Studio. Preserve old existing game/owner output and don't let a failed provider status disable other provider.

## THIRD: Photopea and interface reality

- R10 V02 Photopea ZIP mapper currently expects explicit sprite-01..16 or row-1-col names; authentic Photopea All Slices exported ZIP file **not supplied**. If and only if an actual explicitly user-provided ZIP fixture is available in canonical owner-approved project folder, inspect filenames and verify mapping read-only, then add real format support with tests. Do not scan Downloads, assume screenshots prove a ZIP naming convention or reorder arbitrarily. Mandatory 16-crop remains.
- Validate source-level UI has no spurious claim it passed Godot parse; mock/static checks only. R08's one-time user-wide Godot cache write consent was consumed. NO native Godot GUI/editor, installed Studio GUI, Release Apply or installed manifest rewrite until separate owner authority. Source fixes do NOT imply installed Factory Studio ready.

## Execution and publication

- Safely FF only GitHub main to the SOLE canonical Desktop checkout, preserve 3,003+ owner-untracked items, original 140 COMPLETE=102 READY/4 FAILED/34 REJECTED/0 pending, Pool 131 JSON, stashes, and secondary `ScrubBots-factory` separate game. No clones, TEMP/worktrees, git clean/reset/rebase/force. Codex does NOT edit TASKS, GPT audits or used prompts.
- Run `python -B scripts/codex/scrubbots_task_queue.py --json` on synchronized **clean tracked** checkout before implementation. It must show exactly one identical R10 V04 prompt URL under both current-task and next-task fields.
- Implement source repair, add relevant mocks and tests using `python -B -m pytest -p no:cacheprovider -p no:tmpdir` where safe. No PixelLab/Claude API, billable network, CI/Actions, R2 or game solver batch. Check protections against bytecode/TEMP side effects, and report unrun integration honestly.
- Publish only focused source/tests + one concise `docs/process/` defect/ALPIX discovery result + append real proof to SAME M03 builder log. Normal nonforce safe main push, then actual HEAD==origin/main and tracked clean. Do not create another paper-only R11/R12.
- After completion, owner-facing output must separate: `PIXELLAB_FIRST_USE_NO_CREDENTIAL_CLAIM_PASS/FAIL`, `R10_V03_BILLING_GUARDS_PRESERVED_PASS/FAIL`, `ALPIX_LOCAL_DISCOVERY_STATUS=...`, `PHOTOPEA_ACTUAL_ZIP_STATUS`, `INSTALLED_FACTORY_STUDIO_GUI_NOT_RUN`, `RELEASE_MIGRATION_BLOCKED`, `PAID_PRO_API_NOT_RUN`.

**Absolute:** No paid calls, no unapproved Godot/native, no installed Release apply, no original 140 PNG change, no changing ALPIX billing account, no deleting ambiguous old job claims, and no false end-to-end READY claim. We need a working Studio; focus on the tested blocker instead of adding further planning-only cycles.
