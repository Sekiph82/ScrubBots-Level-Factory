# SB-CP02-007-C001 — Scheduled Activation Windows

Document role: CODEX BUILDER LOG

## Chronological record

### Authority and synchronization preflight

- Starting timestamp: 2026-10-06 10:57:49 +03:00 (Europe/Istanbul client context).
- Canonical persistent root verified as `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository `Sekiph82/ScrubBots-Level-Factory`, branch `main`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Canonical HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`; after fetch/prune, 0 ahead / 255 behind. It has 176 dirty rows, 18 stashes, and 20 registered worktrees; owner-local state remains untouched.
- `origin/main:TASKS.md` continues to authorize M13 continuation. Execution worktree `%TEMP%\ScrubBots-Level-Factory\M13-CONT-001` matched `origin/main` at `58a7e86ff3fd53dc19287d2132b9863ebc51a058`, clean and 0/0 before implementation.
- Read the child 007 prompt and audit criteria.
- Child prompt SHA-256: `CFD0E05F55999BF8CF20EF6955E9F57F520D59B579D21E04EC1EA38A94A07406`.

### Implementation and verification

- Work in progress. Implementation, tests, cumulative/full regression gates, commits, and publication evidence will be appended chronologically.

### Implementation and verification

- Added immutable `ManifestScheduleV1` with `target_kind` (`pack` or `level`), `target_id`, required canonical `not_before`, and optional `not_after`. UTC timestamps are strict whole-second `YYYY-MM-DDTHH:MM:SSZ`, valid calendar instants; an end must be later than the start. Duplicate/casefold-colliding target windows fail closed; unknown target references remain syntactically representable for CP02-009.
- Added deterministic target ordering/record serialization and pure `is_schedule_active(schedule, at_utc)`. Evaluation uses only the supplied canonical UTC instant: before start inactive, start inclusive, end exclusive. No clock, timezone, network, or filesystem lookup.
- Updated V1 model/parser/schema/fixture, package exports, docs, and tests for malformed UTC inputs, window boundaries, target uniqueness, serialization, and unknown reference preservation.
- Focused CP02 manifest suite: **105 passed**. Cumulative M11/M12 + CP00/CP01 + governance + CP02-001 regressions: **362 passed**.
- Unfiltered `python -m pytest -q`, checkout variables absent: **1514 passed, 19 skipped in 865.18s (0:14:25)**. Explicit capability skips only; no Desktop ScrubBots access.
- `python -m compileall -q content_pipeline/src`: PASS. All 16 Content Pipeline JSON files parsed: PASS. `git diff --check`: PASS. Protected TASKS/audits diff empty.
- No runtime activation behavior or external time/network dependency added.
- CP02-007 implementation commit: `740598054dbc7afe260a4f1c6edf8e92fdfef237` (`feat: add explicit UTC activation windows`).

### Publication

- Child log commit and normal push parity evidence will follow.
