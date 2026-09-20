# SB-LFX-010-C001 — Production Readiness Card Truthful Gates — Strict Audit Criteria

Target:
`SB-LFX-010 — Add Production Readiness Card exposing truthful SOURCE/PALETTE/STRUCTURE/SOLVER/DIFFICULTY/QA/OWNER/EXPORT dispositions. [EXTENSION]`

## Gate model

Every card must expose:
SOURCE / PALETTE / STRUCTURE / SOLVER / DIFFICULTY / QA / OWNER / EXPORT.

Allowed dispositions include PASS / FAIL / PENDING / INCONCLUSIVE / NOT_AVAILABLE / STALE as appropriate.

## BLOCKERS

FAIL if:
- overall READY is shown while any required gate is missing/not available/failing;
- QA PASS substitutes for OWNER;
- structural QA substitutes for gameplay solver;
- generation target difficulty substitutes for measured Difficulty V1;
- EXPORT is assumed because a file exists;
- UI computes canonical gate truth independently;
- source/candidate/review data is mutated;
- TASKS is edited.

## Authority mapping

Each gate must cite/bind the exact canonical evidence source and artifact/candidate identity. If there is no authoritative subsystem, disposition must be NOT_AVAILABLE with reason.

Overall readiness must be derived from policy, never cosmetic color.

Given current program dependencies, the card may correctly show NOT READY because M03/M04/M05/export authority is incomplete.

## Real integration

Prove cards for multiple candidates with different source/validation/review states, stale evidence handling, missing solver/difficulty/QA/export evidence, no false READY, and refresh when evidence changes.

## PASS rule

PASS when the card is a compact identity-bound truth summary that cannot bypass missing gates.
