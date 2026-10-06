# SB-CP02-007-C001 — Scheduled Activation Windows

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation: `740598054dbc7afe260a4f1c6edf8e92fdfef237`

## VERDICT

**PASS / CLOSED**

Verified:
- explicit pack/level target kind;
- canonical whole-second UTC timestamps;
- optional end must be strictly later than start;
- one schedule per casefold-normalized target identity;
- deterministic serialization/order;
- evaluation receives explicit `at_utc`;
- before start inactive;
- at start active;
- at/after end inactive;
- open-ended schedules remain active after start;
- no hidden clock/local timezone/network/runtime dependency.

Target-existence checking remains correctly separated into CP02-009.

`SB-CP02-007 = PASS / CLOSED`
