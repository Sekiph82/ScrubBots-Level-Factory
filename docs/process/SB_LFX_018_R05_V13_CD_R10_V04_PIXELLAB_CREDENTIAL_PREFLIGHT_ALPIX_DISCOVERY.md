# SB-LFX-018 R05 V13-C/D R10 V04 | PixelLab Credential Preflight and ALPIX Discovery

**Document role:** CODEX BUILDER RESULT
**Authority:** `.hiveai/prompts/SB_LFX_018_R05_V13_CD_R10_V04_PIXELLAB_FIRST_USE_CREDENTIAL_PREFLIGHT_ALPIX_DISCOVERY.md`
**Independent review:** V26 audit for R10 V03
**Status:** bounded source changes and offline checks complete; installed Studio/native acceptance remains unverified.

## PixelLab first-use credential outcome

`PIXELLAB_FIRST_USE_NO_CREDENTIAL_CLAIM_PASS` — `_semantic_generate_pixellab_pro_4x4` now validates no-cost inputs and checks the existing status-only `pixellab_secret_status()` before creating the job directory, operation record, or permanent digest claim. Missing credentials and credential conflicts return explicit states with `paid_submission_possible=false`, `job_record_created=false`, and `digest_claim_created=false`. The offline regression retries the exact same intent after a fake configured status and observes exactly one mocked adapter submission. No credential value is printed, logged, exported, or stored.

`R10_V03_BILLING_GUARDS_PRESERVED_PASS` — focused tests still cover permanent fail-closed claims for prior paid/uncertain states, legacy digests, corrupt/stale records, cross-process exclusive claim acquisition, and the persisted pre-POST marker. An existing known-unpaid historical claim also remains unchanged and blocked for owner review; this task does not delete or reset old records.

## Windows Claude Code / ALPIX discovery

Read-only Windows status: Claude Code `2.1.287` is installed at `C:\Users\sekip\.local\bin\claude.exe`; `CLAUDE_CONFIG_DIR` is unset. The user settings, installed plugin registry, and `~/.claude.json` were checked for status only. No enabled ALPIX plugin or ALPIX MCP server was found. Canonical project `.mcp.json`, `.claude/settings.json`, and `.claude/settings.local.json` are absent. Updated local `discover_alpix(project_root=...)` reports `ALPIX_PLUGIN_MISSING`; this is supported by the observed configuration, not a guess based only on a failed code lookup. No Claude session/auth files or secret values were read, and no provider session was started.

The source discovery gap was real: it did not inspect project `.mcp.json` or project plugin enablement, despite Claude Code documenting project MCP scope and project settings. Discovery now checks the explicitly supplied canonical project root, reads server/plugin names only, recognizes project-enabled installed plugins and project MCP server names, reports `CONFIG_SCOPE_UNREAD` when a scope cannot be read, and reports available routes only as `ALPIX_AVAILABLE_DISCOVERY_ONLY` with `session_status=CLAUDE_SESSION_UNVERIFIED`. The generation launcher passes the canonical project root so the later Claude invocation resolves project scope consistently. Offline fixtures verify project MCP discovery without exposing environment values, project plugin enablement, unread scope, CLI-missing, and actual missing-route statuses. No ALPIX generation was invoked.

Claude Code reference: [MCP installation scopes](https://code.claude.com/docs/en/mcp) and [settings file scopes](https://code.claude.com/docs/en/settings). The owner's next action, if ALPIX should be available, is to install/enable the intended ALPIX integration through the owner's Claude Code configuration and trust the project as required; no synthetic configuration was added by this task.

## Verification and limits

- Focused local command: `python -B -m pytest -p no:cacheprovider -p no:tmpdir tests/unit/test_pixellab_pro_atlas.py tests/unit/test_pixellab_pro_4x4_v02.py tests/unit/test_sb_lfx_018_c001_r02_master_control_bindings.py tests/unit/test_sb_lfx_018_r05_v13_offline_regressions.py tests/unit/test_pixellab_pro_flash_v12.py::test_semantic_generation_dispatches_to_pro_4x4_without_fallback tests/unit/test_pixellab_pro_flash_v12.py::test_semantic_generation_retires_pro_flash_from_active_dispatch tests/unit/test_pixellab_pro_flash_v12.py::test_pixellab_pixel_art_ui_enforces_variable_51_to_59_four_by_four_canvas -q` — **70 passed**.
- `python -B -c` AST parse of five changed Python files — **5/5 passed**; `git diff --check` — **passed**.
- `PIXELLAB_LOCAL_STATUS=PIXELLAB_API_TOKEN_NOT_CONFIGURED`; no PixelLab endpoint, account/credit query, paid request, or token value was accessed.
- `ALPIX_LOCAL_DISCOVERY_STATUS=ALPIX_PLUGIN_MISSING`; no Claude session, plugin install/update, or ALPIX generation was run. Session health and `RATE_LIMIT` remain unverified and were not probed.
- `PHOTOPEA_ACTUAL_ZIP_STATUS=NOT_PROVIDED`; no ZIP inspection or Downloads scan.
- `INSTALLED_FACTORY_STUDIO_GUI_NOT_RUN`; `RELEASE_MIGRATION_BLOCKED`; `PAID_PRO_API_NOT_RUN`; CI/Actions not run. No Godot GUI, Release Apply, owner files, or original 140 PNGs were touched.
- `TASKS.md`, authoritative prompt, and audit remain unchanged. Local checks are builder evidence, not independent acceptance or end-to-end Studio readiness.
