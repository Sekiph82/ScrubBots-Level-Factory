# SB-LF03-008 Bounded Solution Count and Entropy V1

`SolutionCountEngine` enumerates only provider-defined canonical legal move
sequences. Its explicit equivalence policy is `MOVE_SEQUENCE_V1`: each ordered
legal decision sequence is one solution, and different sequences remain
distinct. The Factory compact-state digest is never treated as gameplay state
equivalence; no state deduplication is performed by this layer.

Every run has deterministic maximum depth, maximum visited states, and maximum
solutions caps. `EXACT` is emitted only after all reachable provider branches
are exhausted within those caps. A solution-cap stop is `LOWER_BOUND`; a depth
or state-cap stop is `INCONCLUSIVE`; provider availability and errors remain
separate dispositions.

Entropy uses the versioned `LOG2_COUNT_V1` measure. Positive exact counts emit
exact `log2(count)`; solution-cap counts emit lower-bound entropy; zero exact
solutions emit explicit `ZERO` entropy with no logarithm. This is analysis
evidence only and does not map to Difficulty V1.
