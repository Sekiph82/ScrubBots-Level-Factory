# SB-LF08-009-C001 — High-Rejection Stress Safety — Strict Audit Criteria

Target: `SB-LF08-009`

## Goal

Prove M08 production batches remain bounded, truthful, resumable and idempotent under very high rejection / duplicate / unavailable rates.

This is not a performance benchmark and must not weaken acceptance thresholds.

## Required stress matrix

Deterministic offline fixtures must cover at least:
- 100% M05/validation reject until budget exhaustion;
- mostly rejected with one late accepted candidate;
- repeated duplicates;
- M03/M04/M05 unavailable/inconclusive outcomes;
- one lane exhausted while another lane completes;
- interruption/resume after long rejection history;
- rerun of COMPLETE and EXHAUSTED batches;
- source-linked candidate preservation where applicable.

## Safety invariants

- Every lane and overall run have finite explicit attempt budgets.
- No retry recursion/unbounded loop.
- Acceptance policy/Challenge Score range/QA thresholds are never relaxed to hit requested counts.
- rejected/inconclusive/unavailable/duplicate candidates never increment accepted count.
- rejection statistics exactly reconcile with attempt history.
- accepted IDs/artifacts remain unique.
- resume continues from exact deterministic next attempt and does not redo accepted work.
- terminal states distinguish COMPLETE / PARTIAL or EXHAUSTED / UNAVAILABLE truthfully.
- no provider/network spending in stress tests.
- canonical truth excludes wall-clock/resource timing.

## Idempotence / corruption

Repeated resume/rerun of terminal batches produces no meaningful artifact diff.
Tampered high-rejection history must fail closed under existing PAG-M09 semantic manifest validation.

## Required gates

Focused stress suite plus 001/006/007/008 and accepted 002–005/010; PAG-M09 corruption/resume tests; retained M03–M07/Palette; full pytest/compileall/Godot/diff/protected-file gates.

## PASS rule

PASS only when extreme rejection cannot cause infinite work, false acceptance, threshold relaxation, duplicate outputs, corrupted resume state or nondeterministic terminal evidence.
