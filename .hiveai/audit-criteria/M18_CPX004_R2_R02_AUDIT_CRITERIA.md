# M18 + CPX-004 R02 — STRICT RE-AUDIT CRITERIA

Repository: `Sekiph82/ScrubBots-Level-Factory`

R02 is a narrow CPX-004 closure. Retain the accepted R01 provider fixes.

## A. Default Release Pool authority

PASS only if:

- `publish_preflight()` resolves the canonical `scrubbots_pixel_factory.supply_pipeline.release_pool.release_entries` authority without dependency injection;
- READY-only or stale/non-current review evidence cannot pass;
- owner-ACCEPT + READY + current hash-bound Release Pool membership is revalidated;
- a no-injection/default-path regression proves the real import/service path.

## B. Executable owner-facing/headless handoff

PASS only if:

- Studio exposes a real STAGING publish action after preflight, not preflight-only;
- headless/operator path can execute the same action from serializable input;
- no JSON path is expected to carry an in-memory `PublisherRunRequest`;
- trusted operator/service code internally assembles the typed M14 request from canonical reviewed state;
- all mutations still go through `run_one_command_publisher`;
- UI/GDScript never calls boto3/R2 directly;
- preflight remains mutation-free;
- missing credentials stop before mutation;
- deterministic retry/idempotency receipt remains secret-free.

## C. Current-main authority

PASS only if:

- preflight identity reuses the accepted CPX-002 TEMP-only exact-current ScrubBots authority/check;
- no owner-typed SHA is treated as current-main authority;
- canonical remote, clean TEMP authority and exact current `origin/main` are enforced;
- production still performs the authentic M14 current-main replay.

## D. Production approval boundary

PASS only if:

- STAGING publication does not imply production approval;
- production requires a separate explicit owner approval bound to exact candidate/staged manifest SHA + content_version;
- missing approval rejects;
- mismatched approval rejects;
- exact approval fixture reaches the existing M14 production gates;
- no real production mutation is performed without the external owner approval.

## E. Regression

Require:

- R02 focused tests green;
- R01 ledger/idempotency tests remain green;
- CP07 suite green except truthful live-secret skip;
- M11-M14 regressions green;
- CPX-002 authentic replay regression rerun with valid exact-current TEMP ScrubBots authority;
- governance/tracker tests green;
- relevant Release Pool/CampaignBuilder/Factory Studio tests green;
- safe full pytest green or only independently proven unrelated baseline skips;
- compileall/JSON/schema/diff/secret checks green;
- no builder edit to root `TASKS.md`;
- no builder write to `.hiveai/audits/**`.

## External gates

Real R2 credentials, a real owner-approved batch and exact live production approval are NOT required for implementation-only R02 PASS.

No live R2 PASS may be claimed without real readback/hash evidence.

## Re-audit outcome

If A-E pass while only external live gates remain, R02 may receive:

`TECHNICAL PASS / EXTERNAL LIVE GATES PENDING`

M18 live publication itself remains open until real R2 evidence exists.
