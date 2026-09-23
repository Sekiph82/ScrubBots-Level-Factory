# SB-LF03-010-C001-R02 — Mandatory Replay Context Remediation

Document role: CODEX REMEDIATION PROMPT

Target: SB-LF03-010 — Reproduce solver bugs by candidate/seed/config/version.

R01 re-audit:
.hiveai/audits/SB-LF03-010-C001-R01_REPLAY_IDENTITY_REVALIDATION_REMEDIATION_STRICT_REAUDIT.md

Create first:
.hiveai/codex-logs/SB-LF03-010-C001-R02_MANDATORY_REPLAY_CONTEXT_REMEDIATION_CODEX_LOG.md

Do not edit TASKS.md.

## Finding to close

R01 compares an explicitly supplied context correctly, but omitted context is synthesized from manifest.execution_context(), which can return MATCH without checking actual replay identity.

## Required remediation

MATCH must require an explicit current replay execution context. Never synthesize current identity from the manifest.
Introduce a versioned, closed, immutable replay-context type instead of arbitrary Mapping.

It must bind current candidate source SHA-256, LevelData/source SHA-256, seed, normalized config, generator version, gameplay authority + source contract, provider id/version, bridge version, search version, memo provider identity, ordering/pruning policy, deterministic budgets, operation and goal.

Rules:
- no context => UNAVAILABLE or ERROR, never MATCH;
- malformed context => ERROR;
- any identity mismatch => DIVERGED;
- exact context + expected disposition/evidence/path => MATCH;
- secrets/absolute paths remain forbidden;
- operational wall-clock timeout metadata is not replay identity.

## Tests

Require exact explicit context MATCH, missing context cannot MATCH, each field independently tampered => DIVERGED, malformed context => ERROR, unavailable provider/bridge => UNAVAILABLE, evidence/path mismatch => DIVERGED, deterministic canonical bytes.

Update 012 regression fixtures accordingly.
Run focused 010 plus 011/012 affected tests, retained LF03 and full repository gates.
Publish R02 implementation/log/terminal commit.