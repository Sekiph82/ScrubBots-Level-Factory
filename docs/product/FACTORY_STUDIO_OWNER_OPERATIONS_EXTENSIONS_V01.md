# Factory Studio Owner Operations Extensions V01

Status: OWNER-APPROVED PRODUCT PLAN
Date: 2026-09-15
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Purpose

This document records owner-approved Level Factory operator workflows that are not part of the original 224 LF/CP source-requirement denominator. They are post-cutover product extensions and must be represented as explicit live extension tasks in root `TASKS.md`.

These extensions do not replace canonical Factory Core, solver, QA, provenance, owner-review, batch, or Content Platform contracts. Factory Studio is a presentation/orchestration surface over canonical truth.

## Non-negotiable architecture

- Root `TASKS.md` remains the only H!veAI project tracker. The Factory Operations Dashboard is not a project-management tracker.
- Factory Studio must consume canonical Factory Core and canonical artifact/job/evidence records. It must not maintain a second compiler or second production-truth database.
- One logical artwork pixel equals one gameplay cell.
- Production logical art remains C01..C16 only, with the current 3..12 used-color envelope.
- Owner source images are preserved byte-for-byte. Any normalization, resizing, palette snapping, or other transformation creates a separately identified derived artifact.
- `CELL_MAJORITY_V1` and `PALETTE_SNAP_V1` remain the locked high-resolution reduction and palette policies where applicable.
- No silent mutation of owner source art.
- QA PASS does not imply owner acceptance. Production promotion requires explicit owner acceptance and the existing downstream gates.
- WFC constraint solving is not the ScrubBots gameplay solver. Solver-dependent UI must report unavailable/inconclusive truthfully until M03 is authoritative.
- Imported artwork is content/provenance, not model-training data. The Factory must not claim to learn from or train itself on owner uploads.

## Operator entry points

Factory Studio should eventually offer one coherent source selector:

- Procedural generation
- Magnific
- PixelLab
- Perchance manual web/import
- Import Pixel Art
- Existing Source Art Library

Regardless of source, accepted imagery converges on the same canonical downstream pipeline.

## Owner-approved extensions

### 1. Factory Operations Dashboard

Provide a Factory-native operational dashboard showing live or persisted production state such as active job/batch, target count, generated count, QA pass/reject counts, owner-review queue, accepted count, current candidate, dimensions, difficulty target, generation mode/source, rejection reasons, elapsed/average timing, and production summaries.

The dashboard must derive state from canonical job/artifact/evidence records. It must not become a parallel task tracker or parallel truth store.

### 2. Manual Pixel Art Import

Allow the owner/operator to select or drag a pixel-art file into Factory Studio and create a candidate source from it.

For an already valid logical artwork, the source pixels must remain unchanged. For a non-canonical source, the original bytes remain immutable and any normalized result is a separate derived artifact with explicit provenance.

Import provenance must distinguish `OWNER_UPLOAD` from AI/provider/procedural origins.

### 3. Source Art Library

Maintain a searchable canonical library/index of owner-approved or retained source artworks and their immutable provenance. Suggested metadata includes source ID, name/label, origin, source SHA-256, original dimensions, derived logical dimensions, palette facts, tags, owner-review state, and level/candidate usages.

The library is an asset catalog, not a machine-learning corpus.

### 4. One-Click Full Pipeline

Provide a bounded orchestration action that can run the applicable chain:

`Import/Generate -> Normalize -> Palette/Structural Validation -> Candidate -> Solve -> Difficulty -> QA -> Review Queue`

Each stage must use the canonical subsystem, persist truthful stage disposition, stop safely on failure, and expose the exact failure reason. Missing solver capability must not be faked.

### 5. Import Validation Wizard

Immediately analyze imported artwork for format, dimensions, logical size compatibility, C01..C16 membership, foreign-color count, semi-alpha count, used-color count, transparency/opacity contract, and other canonical structural rules.

If transformation is needed, the UI must offer an explicit derived-artifact path rather than silently overwriting the source.

### 6. Unified Candidate Inbox and Review Queue

AI-generated, procedural, owner-uploaded, library-derived, and other candidate sources should converge into one review surface with common actions such as ACCEPT, REJECT, EDIT, REGENERATE/REBUILD where meaningful, REVALIDATE, and SOLVE AGAIN where solver capability exists.

Owner acceptance remains explicit and auditable.

### 7. Side-by-Side Variant Comparison

Allow multiple variants/candidates to be compared together using preview plus relevant canonical metrics and provenance: dimensions, used colors, QA disposition, solution/difficulty evidence when available, structural facts, provider/source, and cost where available.

Comparison must not invent a winner or auto-promote a candidate.

### 8. Presets / Production Recipes

Allow reusable operator presets for common generation/import settings, for example dimensions, mode, provider controls, or strict manual-import policy.

A preset is only UI convenience. The expanded canonical request/config must still be recorded explicitly for deterministic provenance/reproduction.

### 9. Failure Inbox / Retry Center

Aggregate failed/rejected/inconclusive batch and candidate stages with exact reason and eligible retry action. Operators should be able to retry only failed work rather than regenerate successful candidates.

Retry must preserve lineage and must never erase the failed evidence record.

### 10. Duplicate and Visual-Similarity Guard

Retain existing exact identity/duplicate protections and add a separate advisory visual-similarity signal for near-duplicate artwork/candidates.

Visual similarity is not automatically authoritative unless a later audited policy explicitly makes it so. Initially it should surface `POSSIBLE_SIMILAR` evidence for review rather than silently reject artwork.

### 11. Provider Cost / Credit Center

Display truthful provider accounting when the provider exposes reliable data, including generations/jobs, success/failure, credits or cost consumed, remaining balance when available, and cost-per-accepted-artwork/level where derivable.

Unknown provider accounting must be shown as unknown, not estimated as fact. Manual/free sources may be labeled appropriately without inventing monetary precision.

### 12. Exact Reproduce Action

Expose an operator action for exact reproduction using recorded canonical seed/config/source/provenance/version identities where the underlying path is deterministic and reproducible.

If an external provider is non-deterministic or no longer reproducible, the UI must state that limitation rather than claim exact reproduction.

### 13. Revision History / Undo / Restore Source

Manual editing should create immutable revision lineage. The operator should be able to compare revisions, undo/restore through explicit revisions, and return to the immutable original source.

No edit may silently rewrite the source artifact or its provenance.

### 14. Search / Filter / Smart Collections

Provide scalable discovery across source art, candidates, review state, accepted levels, dimensions, tags, used-color counts, source/provider, QA state, difficulty/solver metrics where available, and campaign/publication usage where available.

Derived smart collections such as `Needs Review`, `Ready for Production`, `Rejected Today`, or `Unused in Campaign` must be views over canonical records, not duplicate state.

### 15. Production Readiness Card

For every candidate/level, provide a compact readiness summary derived from canonical gates, for example:

`SOURCE / PALETTE / STRUCTURE / SOLVER / DIFFICULTY / QA / OWNER / EXPORT`

Each item must expose its real disposition such as PASS, FAIL, PENDING, INCONCLUSIVE, or NOT AVAILABLE. A green presentation state may never bypass a required gate.

### 16. Drag-and-Drop Batch Import

Allow multiple owner artwork files to be imported in one operation. Every file retains its own source identity/provenance and enters the same validation/candidate pipeline independently.

A batch import must not merge provenance between files or silently overwrite same-named sources.

### 17. Session Recovery / Autosave

Factory Studio should persist enough canonical job/session progress to recover from application interruption and resume eligible work without restarting successful stages.

Recovery must rely on durable canonical job/artifact state, remain deterministic where the underlying operation is deterministic, and clearly distinguish `RESUMED`, `RETRIED`, and newly generated work.

## Suggested Studio navigation

A future Studio information architecture may expose:

`Dashboard | Generate | Import | Library | Batches | Candidates | Review | QA | Providers | Outputs | Settings`

This navigation is product guidance, not a second task hierarchy.

## Dependency notes

- Dashboard, import, library, review, comparison, search, readiness and revision UX primarily belong to M06 Factory Studio.
- Failure/retry, batch import and interruption recovery integrate strongly with M08 Batch Factory.
- Provider cost/accounting and advanced similarity/provider views integrate with M09 provider evolution.
- Actual ScrubBots solution evidence depends on authoritative M03 gameplay solver work.
- Difficulty evidence depends on M04.
- Production-ready status must consume M05 QA and owner-review truth, then hand off through M08/Content Platform rather than bypassing it.

## Counting policy

The original canonical source denominator remains exactly `224` (`112 Level Factory + 112 Content Pipeline`).

These 17 owner-approved capabilities are new Factory product extensions. Together with existing `PAG-SP11`, `PAG-SP12`, and `PAG-SP13`, the repository carries 20 live extension tasks beyond the 224 source requirements.
