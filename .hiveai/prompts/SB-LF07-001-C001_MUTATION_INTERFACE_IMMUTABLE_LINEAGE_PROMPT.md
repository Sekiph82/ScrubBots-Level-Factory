# SB-LF07-001-C001 — Mutation Interface / Immutable Lineage — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_AUDIT_CRITERIA.md`

Implement SB-LF07-001 exactly against its strict audit criteria.

Build the versioned mutation interface and immutable parent->child lineage substrate only. Do not implement hardening/easing policy yet. Bind every request/result to exact parent candidate/LevelData/source/art identities, deterministic seed, operator id/version and canonical authority. Parent state must remain byte/object immutable; applied mutation creates a distinct child identity. Use closed dispositions and deterministic canonical digests with no timestamps/paths/wall-clock in identity. Unknown/stale/malformed/cross-lineage inputs fail closed.

Add adversarial tests for aliasing, parent mutation, stale identity, authority/operator drift and deterministic replay. Preserve M03/M04/M05/M06 and Palette V3 contracts. Run all required gates. Create the task builder log before edits and publish implementation + terminal log-only commits. Never edit TASKS.md or ChatGPT audits.

Builder log: `.hiveai/codex-logs/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md`
