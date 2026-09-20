# SB-LFX-008-C001-R01 — Preset Schema + Real Execution + Provenance Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0
- NOTE: 2

## Audited chain

- R01 start: `b3696cb85883774253b7229746f87399c86e4bd6`
- R01 implementation: `d89ac52888090ff8f9958a340896e4826659c935`
- R01 terminal log-only: `e005b0bcbf31d6954d1c608944bd1bfaa8624fa3`

## Prior findings

### Original MAJOR-001 — real supported action — CLOSED

Apply Preset now executes real canonical Generate using `GenerationRequest`, `GeneratorRouter` and canonical bundle export. The Studio surface no longer performs preview-only expansion.

### Original MAJOR-002 — operation validation — PARTIALLY CLOSED

The implementation now restricts presets to Generate and validates the five operator-facing fields:
- difficulty;
- width;
- height;
- seed;
- mode.

Unknown/missing fields, invalid dimensions/modes and unsupported operations fail closed.

### Original MAJOR-003 — lifecycle integration — PARTIALLY CLOSED

The real Godot integration proves:
- create;
- apply;
- update;
- second execution;
- previous execution evidence immutability;
- delete without deleting prior evidence;
- invalid unknown field rejection.

## MAJOR-001 — “expanded_request” is not the fully expanded canonical GenerationRequest

The central requirement remains that a preset is UI convenience only and every launched execution persist the **fully expanded canonical request/config**.

Current `expanded_request` / preset settings contain only:

`difficulty, width, height, seed, mode`

But the actual canonical `GenerationRequest.canonical_dict()` also carries, among other fields:
- request schema;
- schema version;
- typed seed object;
- `generator_mode`;
- style;
- theme;
- palette subset;
- versioned generator options/defaults.

Therefore the stored preset execution's `expanded_request` is a shorthand operator input mapping, not the complete canonical request.

The canonical candidate bundle itself does correctly persist `metadata.generation.request = result.request.canonical_dict()`, but the R01 integration never compares that authoritative request to a fully expanded preset resolution, and the separate preset-execution record does not persist/reference it explicitly as the expanded canonical request.

### Required remediation

Resolve the preset into a real `GenerationRequest` first, then persist the complete `request.canonical_dict()` as the expanded canonical request (or an exact immutable reference + digest to it).

The real Godot integration must:
1. read the produced candidate bundle metadata;
2. compare `metadata.generation.request` to the persisted preset expanded canonical request exactly;
3. verify typed seed, schema/version and all resolved/defaulted fields;
4. update/delete the preset and prove the prior canonical request/bundle remain unchanged and reproducible.

The five operator fields may remain the editable preset input shape, but they must not be mislabeled as the fully expanded canonical request.

## NOTE — builder-log ordering

The R01 builder log was created after initial product edits. The builder disclosed this truthfully. No acceptance evidence was rewritten, so this is retained as a process NOTE.

## NOTE — repository-wide tracker-contract test

The remediation-batch full suite retains the unrelated protected tracker-contract failure. It does not cause this task finding.

## Disposition

`SB-LFX-008` remains open pending a narrow canonical-expanded-request remediation and re-audit.
