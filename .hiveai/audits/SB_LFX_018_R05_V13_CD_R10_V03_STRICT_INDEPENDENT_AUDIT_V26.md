# SB-LFX-018 R05 V13-C/D | GPT V26 INDEPENDENT STRICT AUDIT | R10 V03 PIXELLAB BILLING CLAIM

**Date:** 2026-10-27 Europe/Istanbul
**Reviewed main SHA:** `4f27b9d250ee0ae2f69e8db4fb45b56be615eca1`
**Actual source/test commit:** `fc246d05b3006d4fe4bb3a2e172fe3e3d34eeb08`
**Method:** Independent GitHub source/diff, builder report, tests and current TASKS read. No owner Windows, PixelLab credential, Godot or API execution by auditor.

## Final verdict

**R10 V03 narrowly ACCEPTED for simulated paid-POST replay prevention (builder says 60/60 focused offline PASS); still NOT fully ready for real PixelLab or installed Studio.** The cross-process atomic SHA claim exists and one winner was proven in a separate two-process synthetic harness. `paid_submission_possible` is persisted in job and claim BEFORE the adapter's POST; all known charged/uncertain records fail closed for a changed `operation_id`; explicit persisted job-id recovery invokes only GET after separate network approval. The report accurately labels all real provider/Godot/Release flows NOT RUN. Repo and builder log final SHA `4f27b9d...` verified through GitHub.

## Exact evidence

- `level_factory/scripts/factory_core_launcher.py`: `_create_exclusive_json` calls `os.open(O_CREAT|O_EXCL|O_WRONLY)`, fsync; `_write_durable_json` flushes, fsyncs, atomic replace for claim and job. Cross-operation SHA index is `<request_digest>.claim.json`; legacy V02 SHA scan blocks ambiguous prior states. Submission callback sets `SUBMITTING` and `paid_submission_possible=True` and persists before `request_json(POST)`. `_semantic_reconcile_pixellab_pro_4x4` refuses without `network_consent=True`, requires persisted operation+job IDs.
- `src/scrubbots_pixel_factory/studio_extensions.py`: Pro adapter calls `on_submission_started()` after local token and request-payload preparation, just before its sole POST. `reconcile_pixellab_pro_4x4_job` only calls GET on `/v2/background-jobs/{job_id}` with explicit permission.
- `tests/unit/test_pixellab_pro_4x4_v02.py`: additional tests for paid/uncertain historical states, distinct operation IDs, two independent process claim race, malformed claims, legacy fingerprint, callback-before-POST, and GET-only recovery.
- `docs/process/SB_LFX_018_R05_V13_CD_R10_V03_PIXELLAB_PAYMENT_IDEMPOTENCY_FIX.md`: final 60/60 with mocked provider; earlier failed fixture/error wording tests corrected. `py_compile` unexpectedly produced three bytecode files despite `-B`, which builder reports were targeted-removed. Local 0/0 and owner untracked protection are builder-reported only, not remotely observable.

## New material usability defect discovered by independent review: PRE-SUBMISSION claim poisoning

`_semantic_generate_pixellab_pro_4x4` ACQUIRES the permanent digest claim and writes the job record **before calling** `extensions.generate_pixellab_pro_4x4_frames`. That adapter checks `get_pixellab_secret()` and rejects `PIXELLAB_API_TOKEN_NOT_CONFIGURED` before `on_submission_started` or any POST.

The launcher correctly persists `state=PRE_SUBMISSION_ERROR`, `paid_submission_possible=False`; however, it **never releases or safely reopens that definitely-unpaid claim**, so trying the EXACT SAME prompt/settings/seed after the user later sets up the token will be blocked as `NEEDS_OWNER_REVIEW_ACTIVE_OR_STALE_CLAIM`. This is not conjecture: test `test_known_pre_post_failure_is_marked_unpaid_but_never_auto_reclaimed` intentionally proves that behavior.

**Severity MAJOR for expected first-use** (especially since last genuine R09 local credential status was `PIXELLAB_API_TOKEN_NOT_CONFIGURED`). No unsafe repeat-billing exists in this scenario because marker false and no POST occurred, but permanently consuming user intent on a local credential failure breaks the intended Factory Studio Generate flow. A safe next source change must perform credential-presence/payload validation BEFORE durable digest acquisition, or implement an **explicit atomic, owner-reviewed same-intent retry only if both claim and job have independently evidenced `paid_submission_possible=False` and the POST callback has never run**. Never auto-delete stale/unknown or chargeable claims; preserve fail closed after potential POST. In parallel, accurately explain missing credential in PIXEL ART UI so a paid Generate is not solicited while NOT_CONFIGURED.

## Cross-path limitations to retain

- Existing claim guards **same normalized request SHA**; legitimately requesting an identical prompt and seed again requires a deliberate new-intent authorization flow, not blind resubmission.
- Atomic file claim protects one digest in the same canonical local job ledger. Cross-device/shared-filesystem behavior has NOT been tested or promised.
- Two-process test mocks claim acquisition and pseudo-POST; it does not run a real PixelLab account call, Windows installed Factory Studio or two independent actual Godot GUI launchers. No mathematical guarantee against all provider-side duplicate billing without an official server idempotency API key.
- Auth/account status remains last observed NOT_CONFIGURED in R09, not independently checked again in R10 V03; Photopea actual exported ZIP filenames have not been tested against ZIP mapper; `ALPIX_PLUGIN_MISSING` local root cause remains UNKNOWN and source route unchanged.
- A recent Godot GDScript native compile is NOT established for R10 edits; prior R08 one-time global cache allowance is consumed. Installed Release still differs and has `INSTALL_BLOCKED_MANIFEST_DRIFT` / `PROCESS_QUIESCENCE_UNPROVEN`; `-Apply` not authorized.
- Original 140 job COMPLETE = 102 READY + 4 FAILED + 34 REJECTED, Pool 131 JSON, not new READY levels; builder reports untouched.

## Actionable next work

**Do not repeat R01–R10 V03 or launch any paid image.** A single narrow **R10 V04** source fix is justified by the concrete first-use failure: ensure local token configuration is checked **before** a permanent billable claim, add regression `missing local credential -> configure in-memory fake credential -> same normalized request may submit exactly once` with no unsafe claim deletion, retain all R10 V03 concurrency and paid-uncertainty guards. Then, in the SAME execution, perform **read-only actual Windows ALPIX/Claude discovery** if feasible and assess genuine Photopea ZIP filename sample only if user-authorized/attached. Do not mislabel ALPIX READY absent a successful live local status; no paid generation, Godot native, installed Release or broad tests. Source-only work should be followed by actual installed Studio/GUI action only with its required separate owner approvals, rather than indefinite paper/audit cycles.

**Disposition:** `R10_V03_OFFLINE_SAFETY_FIX_PASS_BUILDER_EVIDENCE`; `V26_INDEPENDENT_CONDITIONAL_ACCEPTANCE`; `R10_V04_PRE_CREDENTIAL_FIRST_USE_ISSUE_OPEN`; `PIXELLAB_REAL_API_NOT_RUN`; `INSTALLED_GUI_NOT_TESTED`; `ALPIX_ACTUAL_AVAILABILITY_UNKNOWN`.

[Builder R10 V03 report](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/process/SB_LFX_018_R05_V13_CD_R10_V03_PIXELLAB_PAYMENT_IDEMPOTENCY_FIX.md) | [R10 V03 source commit](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/fc246d05b3006d4fe4bb3a2e172fe3e3d34eeb08)
