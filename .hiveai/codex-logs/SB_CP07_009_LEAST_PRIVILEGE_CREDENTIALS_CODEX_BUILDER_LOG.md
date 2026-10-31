# SB-CP07-009 — Least-Privilege Publishing Credentials

Document role: CODEX BUILDER LOG

## Start and authority

- Started: 2026-10-31 (UTC; exact local timestamp to be appended after this entry).
- Canonical Desktop root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Repository: `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting `HEAD == origin/main == 299743463ac287bf5f47a28191bbef94a978e6c4`, 0 ahead / 0 behind; queue guard selected existing `SB-CP07-009`; active prompt `.hiveai/prompts/SB_LFX_OWNER_GOAL_AUTONOMOUS_OPEN_BACKLOG_20261031.md` blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`.
- Read existing task contract in `.hiveai/prompts/M18_CPX004_R2_LIVE_PUBLISH_MASTER_PROMPT.md`, criteria in `.hiveai/audit-criteria/M18_CPX004_R2_LIVE_PUBLISH_MASTER_AUDIT_CRITERIA.md`, publisher secret boundary, threat model, current R2 provider/secret-reference source and focused tests, plus prior M18 builder evidence. No live credentials were enumerated or read.
- Selection is limited to verifying the existing least-privilege contract and secret-free offline tests. No credential creation/rotation, external IAM inspection/change, R2 API call, Production action, package scan, CI, GUI, or owner-data operation is authorized or planned.

## Planned checks

- Test the dedicated R2 secret-boundary cases, opaque secret references/redaction, sanitized provider errors, no-credential fail-closed behavior, no-delete capability, and missing publisher credentials before assembly/mutation using in-memory fakes only.
- Review documentation for bucket-scoped Object Read & Write only and no unrelated Cloudflare account/admin/DNS/billing/Worker permissions; verify tracked project diff contains only the builder log at evidence-publication time and never print secret values.
- External Cloudflare token/IAM configuration and any actual live credential scope remain NOT_RUN.

## Verification results

- Focused command: `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp07_009_r2_secret_boundary.py tests/unit/test_sb_cp00_006_secret_references.py::test_only_opaque_environment_scoped_reference_is_accepted tests/unit/test_sb_cp00_006_secret_references.py::test_raw_secret_bearing_fields_are_rejected_without_echoing_values tests/unit/test_sb_cp00_006_secret_references.py::test_secret_reference_model_has_no_value_field_and_safe_repr tests/unit/test_sb_cp00_006_secret_references.py::test_redaction_is_deterministic_for_secret_fields_tokens_assignments_and_pem tests/unit/test_sb_cp00_006_secret_references.py::test_config_report_and_event_serialization_do_not_expose_obvious_secret_material tests/unit/test_sb_cp00_006_secret_references.py::test_tracked_content_pipeline_configuration_and_source_secret_guard tests/unit/test_sb_cp07_003_r2_provider.py::test_no_credentials_or_invalid_endpoint_fail_before_mutation tests/unit/test_sb_cp07_003_r2_provider.py::test_provider_exception_text_is_not_returned_or_in_repr tests/unit/test_sb_cp07_003_r2_provider.py::test_failed_copy_is_normalized_and_cross_environment_copy_is_denied tests/unit/test_sb_cpx_004_scrubbots_publish.py::test_missing_writer_credentials_stop_before_assembly_or_mutation` — **21 passed in 0.43s**. No test accessed a live credential/provider; all provider tests use fake clients and test-only values.
- `R2_PUBLISHER_SECRET_BOUNDARY.md` documents one bucket-scoped Object Read & Write token and forbids Admin/account/DNS/billing/Worker/bucket-configuration permissions, credentials in project artifacts, and delete/ACL/bucket-create operations. It accurately notes Cloudflare groups list under Object Read & Write while the implementation itself does not list.
- Source check in `r2_provider.py`: the fixed bucket constant is `scrubbots-content-prod`; operations invoke `get_object` and conditional `put_object` only (including immutable copies via GET + conditional PUT); no delete, list, account-admin, DNS, billing, Worker, or bucket-admin client call was found. Provider repr redacts credentials; malformed/missing configuration returns unavailable before provider mutation; provider exceptions are normalized.
- Secret-free tests covered malformed endpoint/credentials before calls, provider repr/capabilities/results, exception normalization, opaque environment-scoped secret references, recursive redaction, config/report/event serialization, tracked source/config guard, no-delete capability, and missing publisher credentials before assembly/mutation.
- `git diff --check` passed. No source, test, dependency, environment, or policy file was changed; this is verification of already implemented/published behavior. No live IAM token scope, credentials, R2 API, production operation, package release artifact scan, CI/Actions, GUI, game repo, owner art, or pool record was inspected or changed. Actual external token scope remains NOT_RUN / EXTERNAL_PERMISSION_REQUIRED.
- Starting source already contained this behavior and focused tests; historical M18 builder log records its implementation commit `c8b6f61658093e4d97f871fee0358b662c5b1954` and prior focused evidence. This task's fresh evidence is limited to the exact checks above and is builder verification, not independent audit or live IAM acceptance.

## Publication and next-task selection

- Builder evidence commit and publication/parity receipt will be recorded here after normal push and fetch verification.
- Candidate next row is existing `SB-CP07-010` provider-specific isolation; its exact prompt/criteria and source will be read at the clean task boundary. No provider mutation is involved.

- Evidence commit `904f5396a35afa6852570428a6490964fa0ff84f` was pushed normally. Fetch confirmed `HEAD == origin/main`, 0 ahead / 0 behind; no tracked product changes were made. The separate TASKS transition remains to be committed.
- The first publication-receipt push command failed because `git fetch --prune origin` could not resolve `github.com`; no remote update occurred and commit `f08964e8` was preserved. Before retry, fetch and `git merge-base --is-ancestor origin/main HEAD` passed; the identical normal push succeeded. A second fetch verified `HEAD == origin/main == f08964e82982ee00ce2a5d6b7fe8add5a7b0c200`, 0/0.
