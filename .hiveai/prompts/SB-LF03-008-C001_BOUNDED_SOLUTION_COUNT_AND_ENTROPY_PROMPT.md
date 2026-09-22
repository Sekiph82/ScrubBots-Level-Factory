# SB-LF03-008-C001 - Bounded Solution Count / Entropy Analysis

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-008 - Add bounded solution-count/entropy analysis.`

Create first:

`.hiveai/codex-logs/SB-LF03-008-C001_BOUNDED_SOLUTION_COUNT_AND_ENTROPY_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Implementation

Build bounded solution enumeration on the accepted search/provider abstractions.

Count canonical legal player move sequences only.

Expose versioned dispositions:
- EXACT;
- LOWER_BOUND;
- INCONCLUSIVE;
- UNAVAILABLE;
- ERROR.

Inputs must include deterministic state/depth/solution-count caps.

Never convert a capped or bound-exhausted run into an exact count.

Define solution equivalence explicitly and use canonical semantic key authority where state equivalence matters.

Entropy:
- exact positive count may produce versioned log2 entropy;
- capped count may produce lower-bound entropy only;
- zero exact solutions has explicit zero-solution evidence, no invalid logarithm;
- no Difficulty V1 mapping.

## Tests

Use known finite fixture graphs for 0/1/multiple solutions, cap hit, state/depth hit, repeat determinism and malformed provider paths.

Production remains unavailable until canonical provider execution exists.

Run retained LF03 and full repository gates. Publish task implementation + task log + terminal log-only commit.
