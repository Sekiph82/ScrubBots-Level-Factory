# SB-LF03-005-C001 - Canonical Visited-State Memoization / Hashing - Strict Audit Criteria

Target:
`SB-LF03-005 - Add visited-state memoization/hashing.`

## Core rule

Memoization equality is gameplay-semantic truth.

The Factory envelope digest from SB-LF03-002 is not automatically equivalent to canonical `ProofState.canonical_key()`.

Production memoization must use an opaque canonical state key supplied by a verified gameplay provider, or remain UNAVAILABLE.

Do not port `ProofState.canonical_key()` into Python.

## Required behavior

Add a versioned memoization/key-provider contract that:
- binds key evidence to exact authority SHA/provider version;
- accepts deterministic opaque canonical keys;
- prevents accidental use of UI identity, filesystem path, timestamps, object IDs or raw rendered pixels;
- detects duplicate visited states deterministically;
- reports memo hits separately from first visits;
- does not mutate state.

A fixture key provider may be used for unit tests only.

## Equivalence tests

Tests must prove:
- identical fixture semantic states collapse to one canonical fixture key;
- distinct fixture states remain distinct;
- repeated traversal gives identical visited/memo-hit counts;
- provider key mismatch/error fails closed;
- Factory compact-state digest is not silently substituted for canonical key authority.

## Scope

Do not add pruning beyond duplicate-state suppression.
Do not add solution metrics beyond visited/memo-hit evidence.
Do not implement main-game canonical-key semantics in Factory Python.

## PASS

PASS when search memoization consumes an explicit semantic-key authority and cannot silently downgrade to a local structural digest.
