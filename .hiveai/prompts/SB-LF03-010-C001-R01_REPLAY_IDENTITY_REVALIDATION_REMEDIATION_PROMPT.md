# SB-LF03-010-C001-R01 — Replay Identity Revalidation Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-010 — Reproduce solver bugs by candidate/seed/config/version.`

Audit:
`.hiveai/audits/SB-LF03-010-C001_SOLVER_BUG_REPRODUCTION_BY_CANDIDATE_SEED_CONFIG_VERSION_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-010-C001-R01_REPLAY_IDENTITY_REVALIDATION_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

Replay MATCH must revalidate the immutable execution/source identities recorded by the manifest, not only disposition/evidence/path.

Add a closed/versioned replay context or equivalent containing current:
- candidate source hash;
- LevelData/source hash;
- seed;
- normalized config identity;
- generator version;
- authority SHA + source contract;
- provider id/version;
- bridge version;
- search version;
- memo provider identity;
- ordering/pruning policy;
- deterministic budgets;
- operation/goal.

Before MATCH, compare every applicable context field to the manifest.

Mismatch => DIVERGED.
Missing required runtime/provider capability => UNAVAILABLE.
Malformed context => ERROR.

Do not regenerate missing source artifacts.

## Tests

Tamper independently:
- candidate hash;
- LevelData hash;
- seed;
- config;
- generator version;
- authority/source;
- provider/bridge/search/memo versions;
- search policy;
- budgets.

None may return MATCH.

Retain secrets/path protections and deterministic bundle bytes.

Run focused 010 + retained LF03 + full gates. Publish R01 implementation/log/terminal commit.
