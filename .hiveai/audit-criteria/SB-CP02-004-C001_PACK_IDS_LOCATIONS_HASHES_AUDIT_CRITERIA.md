# SB-CP02-004-C001 — Audit Criteria

PASS only if each pack reference binds safe pack ID/version, provider-neutral relative object key, exact lowercase SHA-256 and positive byte length. URL/host/absolute/traversal/backslash/query/fragment/secret-bearing locations and ID collisions must fail closed. No provider-specific code or network I/O.
