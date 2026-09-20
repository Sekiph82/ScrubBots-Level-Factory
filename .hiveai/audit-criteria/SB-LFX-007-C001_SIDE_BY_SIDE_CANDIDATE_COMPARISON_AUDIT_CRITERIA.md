# SB-LFX-007-C001 — Side-by-Side Candidate / Variant Comparison — Strict Audit Criteria

Target:
`SB-LFX-007 — Provide side-by-side candidate/variant comparison using canonical preview, QA, solver/difficulty, provenance and cost evidence where available. [EXTENSION]`

## Required behavior

Comparison is read-only. It may compare two or more real canonical candidates/variants but must not rank, auto-select, auto-promote or mutate them.

For each column show, where evidence exists:
- candidate identity;
- preview/artwork identity;
- dimensions;
- used colors;
- source/provenance;
- structural/QA disposition;
- owner-review disposition;
- solver and measured difficulty evidence;
- provider/cost evidence.

Missing evidence must be NOT AVAILABLE, never zero/pass/cheap by inference.

## BLOCKERS

FAIL if comparison:
- invents a winner or best candidate;
- promotes/accepts/rejects as a side effect;
- recomputes authoritative metrics in UI;
- uses stale mismatched evidence across candidate hashes;
- fabricates solver/difficulty/cost;
- mutates source/candidate/review records;
- edits TASKS.

## Identity binding

Every shown evidence card must be demonstrably bound to the candidate/artwork identity it describes. Stale evidence must be excluded or marked STALE.

## Real integration

Use at least two real different candidates and prove:
- side-by-side previews/identities differ correctly;
- shared and differing canonical metrics are correct;
- unavailable domains remain unavailable;
- owner-review evidence appears only on its bound candidate;
- no mutation occurs;
- candidate replacement/refresh cannot cross-wire evidence.

## PASS rule

PASS when comparison is a truthful, identity-bound, read-only multi-candidate view with no ranking/promotion side effect.
