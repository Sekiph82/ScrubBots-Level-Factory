# SB-LF07-002-C001 — Safe Hardening Mutations / Canonical Mechanics — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-002-C001_SAFE_HARDENING_CANONICAL_MECHANICS_AUDIT_CRITERIA.md`

Implement SB-LF07-002 using the accepted SB-LF07-001 mutation boundary.

Inspect current Sekiph82/Scrubbots@main and implement only hardening mutation operators whose semantics and legal mutation surfaces are directly provable from canonical mechanics. Record exact repo/SHA/source-path/contract authority for every operator. At least one real hardening operator must work end-to-end. Do not invent mechanics and do not use dimensions, color count, visual complexity or difficulty labels as hardening proxies.

Use a closed operator registry with deterministic preconditions/transform/invariants. Unsupported or unavailable mechanics fail closed. Child output remains a candidate and parent/source/main-game checkout stays immutable. Add adversarial authority, precondition, illegal-field, shortcut and replay tests. Run required gates and publish separate implementation + terminal log commits.

Builder log: `.hiveai/codex-logs/SB-LF07-002-C001_SAFE_HARDENING_CANONICAL_MECHANICS_CODEX_LOG.md`
