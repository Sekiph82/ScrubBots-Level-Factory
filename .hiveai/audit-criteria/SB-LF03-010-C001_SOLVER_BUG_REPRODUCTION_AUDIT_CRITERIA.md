# SB-LF03-010-C001 - Solver Bug Reproduction by Candidate/Seed/Config/Version - Strict Audit Criteria

Target:
`SB-LF03-010 - Reproduce solver bugs by candidate/seed/config/version.`

## Reproduction identity

A reproducible solver case must bind at minimum:
- candidate/source identity;
- immutable LevelData/source hash;
- generation seed;
- normalized generation config;
- generator version;
- exact gameplay authority SHA;
- solver/search/provider versions;
- ordering/pruning policy versions;
- deterministic budgets;
- operation/goal;
- expected or observed disposition;
- trace/evidence identity when available.

Do not use timestamps, absolute local paths or transient object IDs as reproduction identity.

## Replay

A reproduction bundle must be closed-schema, versioned and deterministic.

Replay must:
- revalidate all referenced immutable identities;
- fail closed when required authority/provider capability is unavailable;
- reproduce the same deterministic verdict/evidence when dependencies and versions match;
- report DIVERGED rather than silently accepting mismatched results.

Do not regenerate missing owner/source artifacts.

## Privacy/secrets

Do not persist:
- API keys;
- OAuth tokens;
- machine-specific secrets;
- unrestricted environment dumps.

## Tests

Prove:
- byte-identical reproduction manifest for identical inputs;
- replay match;
- seed/config/version change causes identity divergence;
- tampered LevelData/candidate hash fails closed;
- authority version mismatch fails closed;
- unavailable provider remains unavailable.

## PASS

PASS when solver failures and anomalies can be carried as durable deterministic replay bundles without embedding mutable/local-only truth.
