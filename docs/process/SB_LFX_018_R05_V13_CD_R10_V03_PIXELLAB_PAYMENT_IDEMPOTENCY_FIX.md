# SB-LFX-018 R05 V13-C/D R10 V03 | FIX PIXELLAB PRO 4×4 BILLABLE DUPLICATE-POST RISK (SOURCE ONLY)

Document role: CODEX BUILDER REPORT

## Scope

Remediate the R10 V02 V25 audit's duplicate-billing risks in the PixelLab Pro 4×4 source path only. The authoritative prompt and V25 audit remain unchanged. This report records builder evidence and does not claim independent audit acceptance or live provider readiness.

## Implementation

- Added a normalized-provider-request SHA-256 claim in the existing local `pixellab-jobs` ledger. `O_CREAT|O_EXCL` makes claim ownership atomic across processes; job and claim records are flushed and atomically replaced. Existing claims, unreadable state, matching legacy V02 records and orphaned/stale claims fail closed. No claim is reclaimed or deleted automatically.
- Added monotonic `paid_submission_possible`. It is persisted in both records immediately before the adapter's only POST. Failures before that callback are recorded as `PRE_SUBMISSION_ERROR` with the marker false; every state after the callback remains guarded, including accepted, polling, normalization, timeout, provider failure, local import failure and success.
- Normalized the claim fingerprint to the actual provider description and seed. The legacy V02 fingerprint is still checked so old paid jobs remain protected after this migration.
- Added an explicit `pixellab-pro-4x4-reconcile` operation for a persisted operation ID. It refuses without explicit `network_consent`, does not make a request if no job ID is durable, and delegates only to bounded GET polling of that stored job ID. The helper has no POST path. No real network request was made.
- Pro 4×4 sizes, locked V3 palette, adjustable 3–12 max-used-colors rule, mandatory 16-slice atlas flow, ALPIX route and historical Pro Flash retirement were not changed. No dependency was added.

## Local verification

Command:

```powershell
python -B -m pytest -p no:cacheprovider -p no:tmpdir tests/unit/test_pixellab_pro_atlas.py tests/unit/test_pixellab_pro_4x4_v02.py tests/unit/test_sb_lfx_018_c001_r02_master_control_bindings.py tests/unit/test_pixellab_pro_flash_v12.py::test_semantic_generation_dispatches_to_pro_4x4_without_fallback tests/unit/test_pixellab_pro_flash_v12.py::test_semantic_generation_retires_pro_flash_from_active_dispatch tests/unit/test_pixellab_pro_flash_v12.py::test_pixellab_pixel_art_ui_enforces_variable_51_to_59_four_by_four_canvas -q
```

Result: **60 passed**. Tests use in-memory fake credentials and mocked provider requests. They cover different operation IDs across `POLLING`, `NORMALIZING`, `POST_SUBMISSION_ERROR`, `SUBMISSION_UNKNOWN`, `SUBMITTING`, `POLL_TIMEOUT`, `SUCCEEDED` and `FAILED_AFTER_POST`; legacy V02 digest matching; one winner from two independent concurrent worker processes; stale/corrupt claim preservation; marker-before-POST ordering; pre-POST failure classification; and consent-gated GET-only recovery. No test made a provider request.

An earlier focused run had 9 failures / 17 passes because the synthetic importer returned no imported source IDs and the consent error message omitted its code. The fixtures/message were corrected; the final focused run above passed. `python -B -c` AST parsing passed for all 3 changed Python modules. `git diff --check` passed with Git's LF-to-CRLF normalization warnings for the test module.

An explicit `python -B -m py_compile` syntax command passed but wrote three bytecode files despite `-B`. Their exact paths were identified and removed with a targeted `Path.unlink` command; no unrelated cache was touched. The final pytest command disabled pytest cache/tmpdir and Python bytecode generation.

## Not run / still open

- PixelLab credential lookup, account query, paid POST, billing check and real GET: **NOT RUN**.
- Installed Factory Studio/Godot GUI, solver/WIN, Release Apply, CI/Actions, original 140 PNG processing: **NOT RUN / NOT AUTHORIZED**.
- Authentic Photopea exported ZIP mapping: **NOT VERIFIED**; no specifically owner-shared ZIP fixture was supplied or inspected.
- ALPIX route remains source-level unchanged; real local availability remains unknown.

`TASKS.md`, prompts, audits, Release files, owner data, 140-job files and historical worktrees were not edited. No TEMP, clone, new worktree, paid service or hosted CI was used.
