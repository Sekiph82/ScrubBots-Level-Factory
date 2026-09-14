# CONTENT PLATFORM CONSOLIDATION PLAN V01

Status: **DRAFT / NON-DESTRUCTIVE INTEGRATION PLAN — DOES NOT REPLACE CURRENT TASKS.MD**
Date: 2026-09-14
Owner direction: Şekip

## Corrected interpretation

`Sekiph82/ScrubBots-Level-Factory` is intended to grow into the SCRUBBOTS development-time Content Production Platform while preserving the repository's existing roadmap, completed milestones, active cycles, audit history and task states.

This document does **not** authorize replacing the current `TASKS.md`, resetting existing task completion, or superseding the active PAG/SP cycle.

## Existing tracker preservation rule

The current Level Factory `TASKS.md` remains authoritative for the existing project and must be preserved byte/state-wise except through the normal audit-driven tracker workflow.

Existing states such as `[x]`, `[~]`, `[ ]`, PASS/CLOSED milestones, active PAG-SP05 work and historical M00-M10 evidence remain valid unless an independent audit specifically changes an individual state.

The 224 `SB-LF*` + `SB-CP*` tasks from the main Scrubbots roadmap are an **integration target**, not a replacement tracker.

They must be introduced non-destructively through a migration/mapping layer that records for every task:

- corresponding existing Level Factory milestone/cycle/evidence where any exists;
- implementation repository (`ScrubBots-Level-Factory`, `Scrubbots`, or cross-repo);
- whether existing evidence is sufficient, partial, absent, or incompatible;
- whether a new task actually needs implementation;
- status only after independent audit.

No imported task starts as `[ ]` merely because it is newly mapped, and no imported task becomes `[x]` merely because similar code exists.

## Intended product split

### `Sekiph82/ScrubBots-Level-Factory`

Target development-time responsibilities include:

- semantic/procedural level-art generation;
- deterministic compilation and provenance;
- puzzle simulation/solver tooling;
- Difficulty/QA intelligence;
- campaign sequencing;
- Factory Studio/operator workflow;
- declarative content packaging;
- manifest/publisher/staging/production tooling;
- content operations.

### `Sekiph82/Scrubbots`

Remains the shipping game/client runtime and owns runtime content consumption such as:

- gameplay and presentation;
- LevelData/catalog runtime;
- RemoteContentManager when implemented;
- HTTPS download/integrity verification;
- `user://` cache/registry;
- last-known-good/offline behavior.

## Existing work must be reused

Accepted PAG M00-M10 and PAG-SP work is migration evidence, not disposable history. The Windows Level Factory application is also a source/evidence candidate, not permission to create a competing compiler.

Target direction remains:

`Studio UI -> canonical Factory Core -> declarative validated output -> publishing pipeline -> Scrubbots runtime`

## Migration procedure

Before changing any existing task state:

1. Inventory the current Level Factory repository and current `TASKS.md`.
2. Build a 224-row mapping against `SB-LF00..LF10` and `SB-CP00..CP09` without editing existing task states.
3. Cross-audit existing code/tests/audits against that mapping.
4. Identify overlap, genuine missing work and contract conflicts.
5. Propose additive tracker sections or linked program documents.
6. Obtain/record owner approval for tracker restructuring.
7. Only then update task state through normal independent-audit rules.

## Parallel development

Codex may continue the existing Level Factory roadmap while Claude continues the main game. The integration work must not invalidate an active Codex prompt or silently redirect the current milestone.

## Non-negotiable safety rule

Migration must be **additive and evidence-preserving**. Never erase or reset existing completed/active Level Factory tasks merely to align numbering with the main Scrubbots roadmap.
