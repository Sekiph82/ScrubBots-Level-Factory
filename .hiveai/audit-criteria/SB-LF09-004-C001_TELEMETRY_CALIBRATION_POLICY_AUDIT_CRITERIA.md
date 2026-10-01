# SB-LF09-004-C001 — Telemetry-Calibrated Difficulty Policy — Strict Audit Criteria

Target:
`SB-LF09-004 — Telemetry-calibrated difficulty only after approved analytics/data policy`

Owner-approved policy:
`docs/policies/SB_LF09_004_ANALYTICS_DATA_POLICY_V01.md`

## Global rules

- Root `TASKS.md` is ChatGPT-owned.
- The owner-approved V01 policy is authoritative.
- M03/M04 deterministic solver/difficulty remains canonical truth.
- Telemetry is advisory-only.
- No automatic canonical Challenge Score or lane mutation.
- No production promotion from telemetry alone.
- No provider/network spend merely for tests.
- Missing analytics evidence remains UNAVAILABLE / INSUFFICIENT_DATA / INCONCLUSIVE.
- Core gameplay and Level Factory must remain functional with analytics fully absent.
- Do not introduce PII collection outside the approved fields.

## Required data contract

Implement a closed, versioned telemetry/calibration contract that permits only approved gameplay evidence, including:
- pseudonymous analytics/session identity;
- level/candidate identity;
- game/build/version;
- start/win/loss;
- attempts;
- move/action count;
- completion duration;
- restart/quit;
- booster usage;
- deterministic Challenge Score/lane/version;
- cohort/calibration version.

Reject unknown/unapproved personal or unrelated fields.

Canonical calibration identity must exclude:
- player name;
- email;
- phone;
- precise location;
- contacts;
- free-form text/chat;
- ad-profile data;
- raw IP as analytics identity;
- secrets/credentials.

## Retention contract

V01 limits:
- raw gameplay telemetry <= 90 days;
- aggregate calibration statistics <= 12 months.

Expired raw/aggregate evidence must not participate in active calibration.

Retention behavior must be deterministic/testable without depending on wall-clock values inside canonical report identity.

## Sample threshold

A calibration recommendation requires >= 100 valid gameplay sessions for the exact supported level/cohort scope.

Below threshold:
- disposition = INSUFFICIENT_DATA;
- deterministic M03/M04 classification is unchanged;
- no recommendation may masquerade as calibrated truth.

Duplicate/invalid sessions must not inflate sample size.

## Calibration report

Create an immutable versioned advisory calibration report bound to:
- exact deterministic M04 difficulty analysis / Challenge Score / lane identity;
- exact cohort/version;
- valid session count;
- accepted aggregate evidence digest;
- observed metrics;
- divergence from deterministic prediction;
- disposition;
- advisory review flag/recommendation if evidence is sufficient.

Allowed dispositions must explicitly distinguish:
- ADVISORY_READY;
- INSUFFICIENT_DATA;
- UNAVAILABLE;
- INCONCLUSIVE;
- ERROR.

The report must never claim that telemetry becomes canonical difficulty truth.

## Allowed advisory metrics

Metrics may include deterministic aggregate forms of:
- win rate;
- loss rate;
- completion rate;
- median/percentile completion duration;
- retry/restart rate;
- quit/abandon rate;
- booster-use rate;
- observed attempt distribution;
- predicted-vs-observed divergence.

Do not infer player health, identity, demographics, or unrelated traits.

## Canonical authority / mutation prohibition

Fail if implementation:
- rewrites canonical Challenge Score;
- silently changes lane/class;
- changes LevelData;
- changes gameplay mechanics;
- mutates owner art;
- performs per-player difficulty personalization;
- trains/updates a live model in gameplay;
- uses telemetry as a substitute for M03/M04 evidence.

V01 output is advisory evidence only.

## Offline / failure behavior

With no analytics provider/data:
- gameplay continues;
- generation continues;
- solver/difficulty continues;
- Level Factory continues;
- telemetry calibration truthfully returns UNAVAILABLE.

No runtime internet dependency may be added to core generation/difficulty.

## Privacy / storage tests

Required adversarial coverage:
- prohibited PII field;
- unknown field;
- malformed pseudonymous ID;
- raw IP field;
- duplicate session;
- expired raw record;
- expired aggregate;
- below 100 sessions;
- exactly 100 valid sessions;
- mixed stale/current sessions;
- cohort mismatch;
- level mismatch;
- stale/wrong M04 analysis digest;
- tampered aggregate digest;
- analytics unavailable;
- rerun determinism.

## Required gates

Focused SB-LF09-004 tests; retained SB-LF09-001/002/003; retained M03/M04/M05/M06/M07/M08 and Palette V3 relevant regressions; full pytest green except accepted capability skips; compileall; Godot headless; git diff --check; TASKS/audits no-diff proof.

## PASS rule

PASS only when privacy-safe telemetry can generate a deterministic, provenance-bound, advisory difficulty-calibration report without becoming canonical difficulty truth and while respecting the owner-approved 90-day / 12-month retention and >=100-session threshold.
