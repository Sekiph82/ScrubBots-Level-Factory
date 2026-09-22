# SB-LF03-012-C001 - Solver Regression Fixture Suite

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-012 - Add regression fixtures.`

Create first:

`.hiveai/codex-logs/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Implementation

Create a durable LF03 regression fixture suite covering all accepted LF03 layers.

Use stable fixture IDs and declarative checked inputs.

Required coverage:
- provider schema/availability;
- deterministic branching search;
- proven no-solution fixture;
- duplicate-state/memo fixture;
- bound exhaustion -> INCONCLUSIVE;
- 0/1/multiple solution-count cases;
- solver evidence metrics;
- reproduction MATCH/DIVERGED;
- authority/source tamper fail-closed;
- real canonical bridge fixture from SB-LF03-009 when checkout capability is supplied.

Keep fake graph fixtures clearly non-production.

Do not commit machine-specific paths or transient caches.

## Final verification

Run the entire retained LF03 suite first.

Then run:
- full `python -m pytest -q`;
- compileall;
- Level Factory Godot headless editor boot;
- relevant real canonical bridge test if capability supplied;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Document exact counts and skips.

Publish fixtures/tests/docs + finalized task log, then terminal log-only commit.
