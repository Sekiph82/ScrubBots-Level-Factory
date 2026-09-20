# SB-LFX-005-C001 — One-Click Pipeline Truthful Orchestration — Strict Audit Criteria

Target:
`SB-LFX-005 — Build bounded one-click pipeline orchestration across applicable Import/Generate→Normalize→Validate→Candidate→Solve→Difficulty→QA→Review stages. [EXTENSION]`

## Principle

The pipeline is an orchestrator over canonical subsystems. It is never a second compiler, solver, QA engine, review database or source store.

## BLOCKERS

FAIL if it:
- fabricates a missing stage;
- treats WFC as gameplay solver;
- invents measured Difficulty V1;
- converts QA PASS into owner acceptance;
- mutates OWNER_UPLOAD source bytes;
- redoes successful durable stages without reason;
- hides a failed/unavailable stage and continues as if successful;
- creates a parallel production truth database;
- edits TASKS or adds provider/network credentials.

## Required stage model

Represent the ordered stage family explicitly:
SOURCE → NORMALIZE/DERIVE (when required) → PALETTE/STRUCTURE VALIDATION → CANDIDATE → SOLVE → DIFFICULTY → QA → REVIEW.

Each stage record must have a truthful disposition such as:
PENDING / RUNNING / PASS / FAIL / BLOCKED / INCONCLUSIVE / NOT_APPLICABLE / NOT_AVAILABLE.

Each stage must bind canonical input/output identities and exact failure reason.

## Applicable-path behavior

- Exact-valid OWNER_UPLOAD may skip normalization as NOT_APPLICABLE and consume LFX-004 evidence.
- Non-canonical OWNER_UPLOAD may only enter derivation if a real canonical transform path exists; otherwise stop truthfully.
- Procedural Generate must reuse canonical Generate output/bundle rather than reconstruct it in Studio.
- Missing authoritative M03 solver means SOLVE = NOT_AVAILABLE and downstream solver-dependent stages must not be fabricated.
- Missing M04/M05/owner-review dependencies must remain explicit.

The pipeline may stop at the first hard unavailable dependency. A truthful partial pipeline is acceptable; a fictional complete pipeline is not.

## Durable run evidence

Persist a versioned pipeline-run record containing references/dispositions only. It must not copy source/candidate truth as a new authority.

A rerun/resume must preserve prior stage evidence and avoid silently overwriting history.

## Real UI/integration

Studio must provide one bounded Run Pipeline action with stage timeline and exact stop reason.

Real integration must exercise at least:
- exact OWNER_UPLOAD path;
- Generate path;
- one validation failure;
- one unavailable dependency stop;
- deterministic retained stage evidence;
- source immutability;
- no false review/ready state.

## Batch-mode note

Previous LFX tasks may be implemented but unaudited. Consume only concrete committed contracts, not assumed acceptance.

## PASS rule

PASS when one-click orchestration uses canonical stage implementations, persists truthful stage lineage, stops safely at real failure/unavailability, and never fabricates downstream success.
