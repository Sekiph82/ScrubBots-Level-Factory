# PROMPT P3 — Headless, resumable batch processing of imported art (unattended runs)

Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**CONDITIONAL**

P3 product behavior is substantially correct and the implementation is scoped. Two closure items remain before unconditional PASS:

1. the interruption test does not actually interrupt the in-flight work of every canonical stage;
2. the full repository suite is not green because the owner-authorized transient P3 tracker identity is not accepted by the current governance regression.

No product finding requires redesigning the headless pipeline or changing the owner P3 prompt.

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 1
- NOTE: 2

## 2. CONTRACT RECOVERY

Authoritative owner prompt:
`.hiveai/prompts/P3_HEADLESS_BATCH_PIPELINE.md`

Prompt SHA-256 recorded by tracker:
`c310b033152ddc079d3261f12cc07d4036e5c4e921371e1bd930d8749fe8042f`

Required behavior recovered from the prompt:
- CLI `pipeline run --job`;
- CLI `pipeline status --job`;
- producer manifest is read-only;
- same canonical Studio chain and gates;
- resumable/idempotent per source;
- restart skips completed stages and redoes interrupted work only;
- stop at owner Review Queue;
- never ACCEPT and never publish;
- default bounded concurrency = 1;
- machine-readable progress and final summary;
- Studio Review Queue parity;
- tests for parity, interruption at every stage, idempotency, rejection-reason preservation, and offline core.

Audit criteria:
`.hiveai/audit-criteria/P3_HEADLESS_BATCH_PIPELINE_AUDIT_CRITERIA.md`

## 3. BRANCH / HEAD / DIFF SCOPE

Primary implementation commit:
`b9c2d844eefc0bc84a9002caa797a9fab1fb7c6e`

Builder-reported final main:
`54a0437ebfaf5e87657d980a9154f75d83766764`

Independent GitHub inspection confirms current `main` is a descendant of the implementation commit.

Diff from implementation commit to current main contains only:
`.hiveai/codex-logs/P3_HEADLESS_BATCH_PIPELINE_CODEX_LOG.md`

The product implementation commit contains exactly:
- `src/scrubbots_pixel_factory/headless_pipeline.py`
- `src/scrubbots_pixel_factory/cli/main.py`
- `tests/unit/test_p3_headless_batch_pipeline.py`
- `tests/integration/test_p3_headless_pipeline_parity.py`
- `docs/HEADLESS_BATCH_PIPELINE.md`

No prompt, audit, tracker, Scrubbots game source, or publication code was changed by the builder.

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Evidence |
|---|---|---|
| Required CLI commands | PASS | `cli/main.py` adds `pipeline run/status --job` |
| Producer manifest read-only | PASS | job bytes are hashed/rechecked; tests assert unchanged bytes |
| Same canonical solver/difficulty route | PASS | calls `studio.run_pipeline(...)`; no second solver/compiler |
| Canonical import/validation/candidate functions reused | PASS | calls `verify_owner_source`, `validate_owner_source`, `_derive_owner_candidate` |
| Review Queue terminal boundary | PASS | only queries `candidate_inbox`; no owner review write |
| No publish | PASS | no `record_owner_review`, `publish_level`, or auto-publish call |
| Default concurrency 1 | PASS | sequential source loop; no parallel executor |
| Machine-readable progress | PASS | newline-delimited JSON progress/status/summary |
| Status is read-only | PASS | `status_job` loads manifest + durable events only |
| Idempotent completed rerun | PASS | completed terminal sources skipped; tests assert no new events/calls |
| Canonical rejection preserved | PASS | validation reason is retained into terminal REJECTED |
| Offline core | PASS | no network/runtime API imports or new dependency |
| Studio/CLI canonical parity | PASS | integration test compares candidate/request/stages/acceptance/difficulty/supply |
| Every-stage true interruption + resume test | PARTIAL | parameterized test exists, but most stages interrupt after completion rather than while RUNNING |
| Full pytest green | FAIL | builder evidence: 1 failed, 1144 passed, 3 skipped |
| Compileall | PASS | builder evidence |
| Factory Studio runtime | PASS | builder evidence |
| Diff check | PASS | builder evidence |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claim: the headless CLI reuses the canonical Studio pipeline.

Repository truth: PASS. The module imports `studio_extensions` and invokes the existing canonical source verification/validation/candidate derivation plus `studio.run_pipeline`. It does not implement a second supply solver or Difficulty V1 engine.

Builder claim: owner Review Queue is the terminal boundary.

Repository truth: PASS. `_candidate_in_review_queue()` reads `studio.candidate_inbox()` and requires `NEEDS_REVIEW`. No owner decision writer or publisher is referenced.

Builder claim: resumable/idempotent stage processing.

Repository truth: implementation supports durable RUNNING/completed events and re-entry. Completed stages are skipped. A RUNNING stage is not considered completed and will execute again on restart.

Builder claim: interruption at every stage was tested.

Repository truth: PARTIAL. The parameterized test names all stages, but its callback deliberately waits for the second checkpoint for IMPORT/NORMALIZE/VALIDATE/CANDIDATE/ZIP, which means interruption occurs after the completed event was durably written. Those cases test “completed stage is skipped after restart”, not “interrupted stage is redone”. QA and REVIEW do interrupt at the RUNNING checkpoint.

Builder claim: only full-suite failure is governance current-task parsing.

Repository truth: PASS. The failing test’s current-task regex requires a hyphenated ID and its no-ledger-row fallback is hard-coded to one earlier maintenance task. The ChatGPT-authored tracker currently declares `P3 — ...`, which does not match that parser.

## 6. FILE / SYMBOL EVIDENCE

### `headless_pipeline.py`

Verified:
- `STAGES` explicitly models IMPORT, NORMALIZE, VALIDATE, CANDIDATE, ZIP supply/solve/difficulty, QA, REVIEW.
- `load_job()` strictly parses a bounded producer manifest.
- manifest source identity is content-bound by OWNER_UPLOAD SHA-256.
- requested dimensions are checked without resize/resample.
- `_read_events()` validates durable event schema and contiguous event sequence.
- `_append_event()` writes immutable stage events to the existing Studio extensions evidence root.
- `_process_source()` re-verifies the canonical source before trusting prior checkpoints.
- `studio.validate_owner_source()` is the validation authority.
- `studio._derive_owner_candidate()` is the canonical owner-upload candidate derivation.
- `studio.run_pipeline()` is the ZIP/supply/solve/Difficulty V1 authority.
- `studio.candidate_inbox()` is the Review Queue projection.
- terminal READY requires pipeline READY + QA PASS + Review Queue NEEDS_REVIEW.

### `cli/main.py`

Verified:
- `pipeline run --job`
- `pipeline status --job`
- run returns nonzero for FAILED/PENDING;
- status does not execute canonical work.

## 7. FOCUSED TEST EVIDENCE

Builder evidence:
- focused P3 suite: 13 passed;
- Studio parity integration: passed;
- selected SB-LFX-005/SB-LFX-015/owner-upload/CLI regressions: 23 passed.

Independent source review confirms useful coverage for:
- strict read-only manifest;
- idempotent rerun;
- dimension mismatch without resampling;
- multi-source failure isolation;
- CLI run/status;
- offline boundary;
- one authentic Studio-vs-headless happy-path parity case.

Required closure:
- true in-flight interruption at every canonical stage remains insufficiently exercised.

## 8. REGRESSION EVIDENCE

Builder full suite:
- 1144 passed
- 3 skipped
- 1 failed

The sole reported failure:
`tests/unit/test_sb_lf00_007_governance_authority.py::test_project_status_and_active_task_contract_are_exact`

Independent inspection confirms the failure is caused by tracker/parser mismatch, not P3 runtime behavior.

Nevertheless the P3 audit criteria require a green full suite except truthful capability skips. Unconditional PASS is therefore not available yet.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

PASS.

No new:
- HTTP client;
- cloud image API;
- telemetry;
- API key;
- network-only dependency.

Producer manifest paths remain local filesystem paths.

OWNER_UPLOAD source identity is verified before reuse.

The module does not call owner ACCEPT or publication.

## 10. ARCHITECTURE CONSISTENCY

PASS with one testing caveat.

The headless layer is an orchestration/checkpoint wrapper over the existing Studio truth stores and canonical functions.

It does not add:
- a second compiler;
- a second solver;
- a second Difficulty V1 implementation;
- a second candidate store;
- a second Review Queue.

The separate durable job event store contains references/checkpoints only.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder log is appropriately explicit that P3 remains awaiting independent audit.

The builder correctly preserved:
- root `TASKS.md`;
- prompt;
- audit files;
- pre-existing untracked UID/worktree material.

The one full-suite governance failure is truthfully logged.

The current tracker mismatch was introduced by ChatGPT’s transient P3 activation format, not by Codex.

## 12. FINAL REPOSITORY STATE

Current GitHub `main` contains:
- P3 implementation;
- tests/docs;
- builder log only after the product commit.

No contradictory later product mutation was found.

## 13. OPEN CROSS-MILESTONE FINDINGS

`MAINT-ZIP-CORE-V02-C001-R02` remains paused and not cancelled.

P3 does not resolve or modify that separate ZIP final-cutover task.

P3 correctly depends on the canonical Studio/ZIP behavior already present.

## 14. DEFECTS BY SEVERITY

### MAJOR — P3-F01 — Interruption test does not truly interrupt every stage

For IMPORT/NORMALIZE/VALIDATE/CANDIDATE/ZIP, the test callback waits for the second stage checkpoint, i.e. after the stage completion record.

Required:
- interrupt once after the durable RUNNING checkpoint for each canonical stage;
- restart;
- prove that exact stage work is retried/recovered once;
- prove all earlier completed stages are not rerun;
- prove later stages continue;
- for ZIP specifically test both:
  1. crash before canonical pipeline artifact exists => ZIP stage runs on resume;
  2. crash after canonical pipeline artifact exists but before P3 completion checkpoint => existing canonical pipeline is recovered, not duplicated.

This is a test/evidence closure; current architecture may remain.

### MINOR — P3-F02 — Governance regression does not accept the owner-authorized transient P3 tracker identity

The current governance test cannot parse `Current Task: P3 — ...` and has a hard-coded no-ledger fallback for an older maintenance task.

Required:
- make the governance regression generically support an owner-authorized transient current task that is intentionally outside the 224 source-requirement denominator;
- keep the 224 denominator unchanged;
- require a well-formed transient task ID, matching Next Task/Action, status, actor, prompt and audit criteria references;
- do not special-case P3 by weakening tracker authority.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

NOTE only:
- `headless_pipeline.py` uses private Studio helpers (`_write_json`, `_derive_owner_candidate`, `_repository_root`, etc.). This is acceptable for current same-package parity, but a future public orchestration facade could reduce private-coupling risk.
- Job event timestamps intentionally make execution evidence non-byte-identical across interrupted vs uninterrupted runs; canonical source/candidate/pipeline truth remains identical. No owner requirement says checkpoint logs themselves must be byte-identical.

Neither item blocks P3.

## 16. UNVERIFIED ITEMS

- Independent execution of the full 10-minute pytest suite was not available through the GitHub connector; builder full-suite evidence was cross-checked against source.
- Real OS process termination at every stage was not independently executed.
- Performance on an actual 100-level producer job was not measured; prompt requires bounded sequential correctness, not a throughput target.

## 17. REGRESSION RISK

Overall risk: **LOW–MEDIUM**.

Low:
- new module is isolated;
- no game mutation;
- no publish;
- no network;
- canonical Studio functions remain authority.

Medium:
- durable resume state is new and should have stronger in-flight interruption tests before closure.

## 18. AUDIT CONFIDENCE

**HIGH** for architecture, scope, Review Queue boundary, offline behavior, and the identified test gap.

**MEDIUM-HIGH** for runtime resumability because independent process-kill execution was not available.

## 19. FINAL VERDICT

**CONDITIONAL**

P3 implementation is functionally well aligned with the owner prompt. No redesign is required.

Unconditional PASS requires:
- P3-F01 true in-flight interruption coverage;
- P3-F02 governance regression/tracker compatibility;
- final full suite green.

## 20. REQUIRED REMEDIATION

Create one bounded P3-R01 cycle.

Do not change the owner prompt.

Do not change P3 product behavior unless a new focused test exposes a real defect.

R01 scope is only:
1. strengthen every-stage interruption/resume evidence;
2. repair the generic transient-task governance regression;
3. rerun focused P3 tests + relevant SB-LFX-005/SB-LFX-015 regressions + full pytest + compileall + Factory Studio headless + diff check.

If all pass and no new direct defect is found, P3 may close.
