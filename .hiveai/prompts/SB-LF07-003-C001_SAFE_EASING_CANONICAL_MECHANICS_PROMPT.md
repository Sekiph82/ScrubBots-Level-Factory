# SB-LF07-003-C001 — Safe Easing Mutations / Canonical Mechanics — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_AUDIT_CRITERIA.md`

Implement SB-LF07-003 using the accepted mutation interface and hardening registry pattern.

Inspect current Scrubbots authority and implement only easing operators whose legal semantics are directly proven by canonical gameplay/mechanic source. At least one real easing operator must execute end-to-end. Easing must never be implemented by shrinking the board, reducing colors, recoloring art, changing a difficulty label, or deleting a mechanic without explicit canonical authority.

Bind exact repo/SHA/path/version, use deterministic closed operators with explicit preconditions/invariants, produce immutable child candidates, and fail closed on unsupported/stale inputs. Add adversarial tests and run all required gates. Publish task-specific implementation and terminal builder-log commits.

Builder log: `.hiveai/codex-logs/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_CODEX_LOG.md`
