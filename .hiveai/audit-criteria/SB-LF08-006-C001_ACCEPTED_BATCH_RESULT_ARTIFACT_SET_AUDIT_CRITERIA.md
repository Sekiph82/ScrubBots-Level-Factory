# SB-LF08-006-C001 — Accepted Batch Result Artifact Set — Strict Audit Criteria

Target: `SB-LF08-006`

## Accepted foundation
M03–M07 COMPLETE / VERIFIED; PAG-M08 export PASS/CLOSED; PAG-M09 batch PASS/CLOSED; SB-LF08-001 accepted production-count contract is prerequisite during this batch.

## Truth boundary

A batch result is an immutable evidence package over canonical artifacts. It is not a second LevelData compiler, solver, QA engine, artwork renderer, review store or source database.

## Required accepted-entry contract

For every Factory-accepted candidate, bind exact:
- batch plan digest, lane/class, attempt ordinal and accepted-candidate identity;
- final LevelData V1 canonical bytes/digest;
- final logical-art PNG digest and canonical M08 candidate bundle/artwork identity;
- preview PNG digest when a preview exists, otherwise explicit NOT_AVAILABLE/NOT_REQUESTED;
- generation metadata/result/request digests;
- source provenance identity/digest;
- M03 solver evidence digest/disposition;
- M04 DifficultyAnalysis + Challenge Score/lane digest;
- M05 MachineReadableQAReport canonical bytes/digest with ACCEPT disposition;
- M07 mutation lineage/provenance digest when mutation was used, otherwise explicit NOT_APPLICABLE;
- stable relative references to immutable artifacts.

The entry must cross-bind all identities to the same candidate/LevelData/source/art lineage.

## Batch result

Create a versioned deterministic batch-result manifest containing:
- plan digest;
- requested vs attempted/generated vs factory-accepted counts per lane;
- rejection/inconclusive/unavailable statistics;
- accepted-entry digests in deterministic order;
- overall truthful status.

The manifest must be reconstructible from accepted evidence and exclude timestamps, machine paths, wall-clock timing and mutable UI state from canonical identity.

## File/materialization rules

- Reuse canonical artifact bytes. Do not silently regenerate/re-encode accepted LevelData or logical artwork merely to make the batch package.
- Safe portable relative paths only.
- No source-art overwrite.
- No duplicate candidate directories with divergent bytes.
- Missing required canonical artifact => entry is not Factory-accepted batch output.

## Negative tests

Cross-candidate swap; stale LevelData; wrong art/preview hash; QA not ACCEPT; wrong solver/difficulty digest; mutation-lineage swap; missing required artifact; path traversal; unknown fields/schema; nondeterministic ordering; duplicate accepted entry.

## Required gates

Focused 006 + 001 and accepted M05/M08/M09 output tests; full retained M03–M07/Palette; full pytest/compileall/Godot/diff/protected-file gates.

## PASS rule

PASS only when each accepted batch result is a complete provenance-bound set of final LevelData, artwork/preview, metadata and QA evidence for exactly one candidate lineage.
