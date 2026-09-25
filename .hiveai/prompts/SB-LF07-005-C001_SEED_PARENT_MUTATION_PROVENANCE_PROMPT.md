# SB-LF07-005-C001 — Seed / Parent / Mutation Provenance — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_AUDIT_CRITERIA.md`

Implement SB-LF07-005 complete mutation provenance.

Create a closed versioned provenance record binding request digest, deterministic seed/derivation version, lineage root + immediate parent, exact parent LevelData/source/art digests, operator id/version/intent/authority, attempt ordinal, pre/post child digests, disposition/reason and post-mutation evidence digests when available. Derived hashes must not be caller-overridable.

Reject self-parenting, cycles, mixed roots, seed/operator/authority drift and conflicting duplicate-child provenance. Canonical identity must exclude paths/timestamps/wall-clock. Prove deterministic replay from parent + request + seed + operator version. Run required gates and publish the task log/commits.

Builder log: `.hiveai/codex-logs/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md`
