# SB-LF09-004 Analytics / Data Policy V01

Status: OWNER APPROVED
Owner approval date: 2026-09-30

## Purpose

Permit privacy-safe gameplay telemetry to calibrate ScrubBots difficulty while preserving the existing deterministic M03/M04 difficulty system as canonical authority.

Telemetry is advisory calibration evidence. It must not silently override canonical difficulty truth.

## Allowed telemetry

Gameplay telemetry may include only gameplay/level behavior such as:

- pseudonymous analytics/session identifier;
- level/candidate ID;
- game/build/version identity;
- level start;
- win / loss;
- attempt count;
- move/action count;
- completion duration;
- restart;
- quit / abandon;
- booster usage;
- current deterministic Challenge Score and difficulty lane/version;
- calibration cohort/version.

## Prohibited data

Do not collect or retain for this difficulty-calibration system:

- player name;
- email;
- phone number;
- precise location;
- contacts/address book;
- free-form chat/text;
- advertising profile;
- raw IP address as an analytics identity;
- secrets or account credentials;
- unrelated device/user data.

## Identity / privacy

Use a random or pseudonymous analytics identifier where correlation is required.

Difficulty calibration must not require directly identifying a player.

## Retention

- Raw gameplay telemetry: maximum 90 days.
- Aggregated difficulty/calibration statistics: maximum 12 months.
- Retention enforcement must be explicit and testable.
- Data past retention must not remain part of active calibration evidence.

## Difficulty authority

The accepted deterministic M03/M04 system remains the canonical difficulty authority.

Telemetry may produce advisory facts such as:
- predicted lane vs observed player difficulty divergence;
- observed win/loss or completion-rate drift;
- observed retry/restart/quit pressure;
- cohort-level calibration evidence.

Telemetry must not directly mutate:
- canonical Challenge Score;
- canonical lane/class;
- accepted LevelData;
- gameplay mechanics;
- owner source art.

Any future calibrated model/coefficients must be separately versioned and audited before they can influence production classification.

## Minimum evidence

Calibration must fail closed as INSUFFICIENT_DATA unless the relevant level/cohort has at least 100 valid gameplay sessions.

A smaller sample may be displayed descriptively but may not drive a calibration recommendation.

## Offline / availability rule

Analytics/telemetry availability must never be required for:
- core gameplay;
- deterministic generation;
- deterministic solver/difficulty analysis;
- Level Factory operation.

If analytics is unavailable, stale, incomplete, below threshold, or outside policy:
- canonical deterministic difficulty remains unchanged;
- calibration disposition is UNAVAILABLE / INSUFFICIENT_DATA / INCONCLUSIVE as appropriate.

## Calibration mode

V01 is advisory-only.

Permitted output:
- advisory calibration report;
- observed-vs-predicted divergence;
- suggested review flag;
- versioned aggregate statistics.

Not permitted in V01:
- automatic canonical difficulty mutation;
- silent lane reassignment;
- online learning in live gameplay;
- personalization of difficulty per identifiable player;
- production promotion without independent audit.

## Security / governance

- No provider/network spend merely for tests.
- No telemetry or analytics secrets committed to Git.
- Canonical reports must exclude raw identifiers where an aggregate is sufficient.
- Any future expansion beyond this policy requires a new owner-approved policy version.

## Owner decision

OWNER APPROVED:
Privacy-safe, advisory-only telemetry calibration under the rules above.
