# SB-LFX-011-C001 — Factory Studio Exact Reproduce Action

Builder log:
`.hiveai/codex-logs/SB-LFX-011-C001_EXACT_REPRODUCE_ACTION_CODEX_LOG.md`

Create log first. Work only on LFX-011.

Reuse accepted Factory Core Reproduce for deterministic generated candidates.

Add an identity-bound reproducibility capability evaluator:
- EXACT_REPRODUCIBLE;
- SOURCE_RETRIEVABLE_ONLY;
- NOT_REPRODUCIBLE;
- STALE/INVALID.

Enable Exact Reproduce only for real exact-capable records. Use recorded canonical metadata, never current drafts/presets.

For OWNER_UPLOAD, expose immutable-source retrieval/restore wording separately if useful, but never call it regenerated.

For nondeterministic/unrecorded provider paths, show NOT_REPRODUCIBLE unless exact replay is actually proven.

Successful replay creates separate output and verifies canonical MATCH while preserving originals.

Real Godot tests must cover deterministic replay, draft divergence, owner-upload distinction, unsupported path, tampered metadata, and byte immutability.

No LFX-012+ work and no TASKS edit.

Commit/push implementation, then one task-final builder-log-only commit; continue only under batch master.
