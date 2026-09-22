# SB-LF03-006-C001 - Solver Evidence and Search Metrics - Strict Audit Criteria

Target:
`SB-LF03-006 - Record solution path/states/dead ends/depth/branching/solve time.`

## Evidence domains

Separate deterministic search evidence from operational timing.

Deterministic evidence may include:
- ordered decision path;
- stable state/key references;
- visited states;
- dead-end count;
- maximum depth;
- branching observations;
- frontier peak;
- memo hits;
- terminal disposition/reason from provider/search.

Elapsed solve time is observational telemetry only:
- use monotonic timing;
- do not include it in canonical result identity;
- never let elapsed time alter a deterministic verdict unless an explicit later timeout policy applies.

## Truth

Do not fabricate metrics unavailable from the executed search.

Do not label a provider UNAVAILABLE run with zero-valued metrics as if a search occurred.

Solution path must contain canonical move values, never UI coordinates.

State evidence may be bounded references/digests, not giant duplicated state blobs.

## Determinism

For identical fixture/provider/search policy:
- path and deterministic metric fields must match exactly;
- elapsed time is exempt and must be explicitly non-canonical.

## Scope

Do not implement heuristics/pruning.
Do not implement solution counting/entropy.
Do not introduce difficulty scoring.

## PASS

PASS when search produces a versioned evidence report with honest deterministic metrics and separately labeled non-canonical timing telemetry.
