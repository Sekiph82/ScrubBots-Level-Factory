# SB-LF03-004 — Deterministic Baseline Search

Document role: DURABLE BUILDER BOUNDARY EVIDENCE

`baseline_search.py` provides `DFS_CANONICAL_PROVIDER_ORDER_V1`, a generic
depth-bounded depth-first orchestration layer. It receives legal moves only
through the SB-LF03-003 provider contract and receives terminal/child-state
truth only through `SearchTransitionProvider`. The engine never interprets
compact supply, slots, board masks, routing, or completion semantics.

Provider order is preserved. Repeated execution is deterministic and does not
use wall-clock time. Provider `UNAVAILABLE` and `ERROR` remain execution truth;
fixture terminal truth may report `SOLVED` or `PROVEN_UNSOLVABLE`, while depth
exhaustion and provider-defined zero-move continuation remain `INCONCLUSIVE`.
The production canonical path remains unavailable until a real canonical
transition executor exists.
