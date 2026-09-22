# SB-LF03-010-C001 - Solver Bug Reproduction by Candidate/Seed/Config/Version

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-010 - Reproduce solver bugs by candidate/seed/config/version.`

Create first:

`.hiveai/codex-logs/SB-LF03-010-C001_SOLVER_BUG_REPRODUCTION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Implementation

Add a versioned closed-schema reproduction manifest/bundle for LF03 solver/search executions.

Bind:
- candidate/source/LevelData hashes;
- seed + canonical normalized config;
- generator version;
- canonical gameplay authority SHA/source contract;
- provider/bridge/search/memo/order/pruning versions;
- deterministic budgets;
- operation/goal;
- observed verdict and deterministic evidence digest/path when available.

Replay must use existing canonical providers and accepted search layers. Do not reimplement gameplay.

Add MATCH / DIVERGED / UNAVAILABLE / ERROR replay truth.

Never regenerate or mutate the source merely to make replay succeed.

No secrets or absolute-machine paths in durable bundle identity.

## Tests

Use deterministic fixture cases and, when available, canonical bridge integration to prove replay match, tamper fail-closed, seed/config/version divergence and unavailable behavior.

Run retained LF03 + full gates. Publish task implementation, evidence docs/tests and task log, then terminal log-only commit.
