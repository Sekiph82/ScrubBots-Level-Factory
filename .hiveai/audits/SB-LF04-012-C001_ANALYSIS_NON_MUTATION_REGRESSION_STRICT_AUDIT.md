# SB-LF04-012-C001 — Analysis Non-Mutation / M04 Regression Closure — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 2
- MINOR: 0

## Audited chain

- implementation: `79c21fccbafeac44b22e624ea39515175fb7b8d8`
- terminal builder-log commit: `2f71952484bd82451e78c3d6f4a48873cdab9596`
- M04 master builder publication: `a9e63bc272646eccb88bef7672752132f9d3fb0a`
- final builder full suite: `937 passed, 1 capability skip`
- compileall / Godot / diff-check / TASKS no-diff: PASS

Builder logs and green tests were treated as evidence, not acceptance.

## Independent finding

## MAJOR-001 — The declarative corpus is checksummed but is not behavior-driving regression evidence

`sb_lf04_m04_regression_v1.json` contains one compact entry per task, and the regression test validates only schema/version/checksum and the ordered list of IDs.

The test does not execute the declared 002–011 payload values/contracts from the corpus. Many fields such as expected solution_depth, slot_pressure, bait ratio, score and thresholds are never consumed by the regression test.

Therefore corpus drift can remain green as long as its checksum is recomputed.

## MAJOR-002 — The required non-mutation proof is incomplete

The task requires exact pre/post proof for:
- Level Data source;
- relevant art/logical source fixture;
- canonical ScrubBots checkout files/status where bridge is invoked.

The dedicated 012 test only snapshots `tests/fixtures/lf03_solver_regression_v1.json` and a LevelMetrics object. It does not snapshot an art/logical-grid source, and it does not establish canonical checkout file/status immutability in the M04 regression itself.

Full-suite M03 bridge tests are useful retained evidence, but they do not replace the explicit M04 non-mutation closure required here.

## Global invariant review

No board-size/color-count difficulty inference, source-art mutation, runtime network/provider-credit use, gameplay-rule clone, or builder TASKS mutation was accepted.

## Final disposition

**CHANGES_REQUIRED / IMPLEMENTATION RETAINED**

## Required remediation

Turn the M04 corpus into executable declarative cases whose payloads drive each task-family regression and expected result. Add explicit pre/post SHA/bytes for a real Level Data source fixture and an art/logical source fixture. Where the M04 regression invokes or depends on the canonical bridge, prove exact ScrubBots checkout status/source immutability in the same closure path (capability-gated only when genuinely absent). Keep the full suite green and incorporate all R01 fixes.
