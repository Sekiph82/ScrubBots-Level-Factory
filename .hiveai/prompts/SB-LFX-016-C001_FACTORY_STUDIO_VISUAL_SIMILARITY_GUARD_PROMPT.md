# SB-LFX-016-C001 — Factory Studio Advisory Visual-Similarity Guard

Builder log:
`.hiveai/codex-logs/SB-LFX-016-C001_VISUAL_SIMILARITY_GUARD_CODEX_LOG.md`

Create log first. Work only on LFX-016.

Implement one deterministic offline versioned pixel/logical-art similarity algorithm over canonical artifact representations.

Keep exact SHA/grid duplicate detection separate and stronger.

Persist/derive identity-bound pair evidence with score/distance, threshold, algorithm version and disposition:
EXACT_DUPLICATE / POSSIBLE_SIMILAR / DISTINCT.

Never auto-reject, auto-accept, rank a “winner” or mutate review state.

Expose advisory similarity in relevant comparison/search/candidate UI.

Tests must cover exact, near, different, threshold, deterministic replay, stale edited revision and zero side effects.

No external AI/provider calls, no LFX-017 work, no TASKS edit.

Commit/push implementation then one task-final log-only commit; continue only under batch master.
