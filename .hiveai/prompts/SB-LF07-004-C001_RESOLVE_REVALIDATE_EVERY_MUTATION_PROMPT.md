# SB-LF07-004-C001 — Re-solve / Revalidate Every Mutation — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_AUDIT_CRITERIA.md`

Implement SB-LF07-004 so every APPLIED mutation is automatically re-solved and revalidated against accepted M03/M04/M05 authorities.

Bind solver, difficulty and QA evidence to the exact mutated child plus its parent/operator request lineage. Parent acceptance must never be reused as child acceptance. Proven unsolvable rejects; inconclusive stays inconclusive; missing capability is UNAVAILABLE; hash/authority mismatch is ERROR. No shortcut may mark a child eligible without the complete applicable chain.

Add cross-lineage replay, stale-evidence, solver/validator failure, unavailable capability, deterministic envelope and non-mutation tests. Run all required gates and publish task-specific logs/commits.

Builder log: `.hiveai/codex-logs/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md`
