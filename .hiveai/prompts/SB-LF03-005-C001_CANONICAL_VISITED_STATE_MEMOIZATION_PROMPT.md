# SB-LF03-005-C001 - Canonical Visited-State Memoization / Hashing

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-005 - Add visited-state memoization/hashing.`

Create first:

`.hiveai/codex-logs/SB-LF03-005-C001_CANONICAL_VISITED_STATE_MEMOIZATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Authority

Read current main-game `ProofState.canonical_key()` only to understand authority boundaries.

Do not reimplement it.

Introduce a key-provider/memoization contract so the search layer can consume an opaque canonical semantic key when supplied by a verified canonical provider.

The SB-LF03-002 Factory envelope digest must remain structurally useful only. It must not become gameplay-equivalence authority.

## Implementation

Add:
- versioned state-key provider interface;
- deterministic visited set bookkeeping;
- memo-hit evidence;
- authority/provider binding;
- fail-closed unavailable/error paths.

Production key authority remains UNAVAILABLE until canonical runtime provides the key.

Use fixture-only providers for unit tests.

## Tests

Cover:
- deterministic duplicate collapse;
- distinct-state separation;
- repeat-identical visited/memo counts;
- malformed key/provider mismatch;
- explicit guard against substituting CompactSolverState.digest() as canonical gameplay key;
- immutability.

Run focused and retained LF03 tests, full repository gates, TASKS no-diff.

Publish task implementation and finalized task log with terminal log-only commit.
