# SB-LF03-007 Correctness-Preserving Pruning and Order V1

The Factory exposes a small, immutable `SearchPolicy` contract. Its ordering
axis is either `PROVIDER_ORDER_V1` (the baseline control) or the deterministic
`REVERSE_PROVIDER_ORDER_V1` traversal. Both consume only the already validated
legal-move tuple from the provider; neither derives gameplay moves.

The pruning axis is explicitly `NONE_V1`. No heuristic, artwork, difficulty,
or gameplay-rule pruning is justified by this boundary. Canonical visited-state
memoization remains an observation contract until a future task proves a safe
completed-state pruning protocol.

`EvidenceSearchEngine` records the selected ordering and pruning objects in its
canonical evidence. Reordered exhaustive fixtures preserve the provider truth;
bounded fixtures remain `INCONCLUSIVE` when the bound prevents proof. The
canonical ScrubBots gameplay repository remains the authority for gameplay
semantics.
