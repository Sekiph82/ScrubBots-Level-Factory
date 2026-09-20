# SB-LFX-004-C001 — Import Validation Wizard Canonical Analysis — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target:
`SB-LFX-004 — Add Import Validation Wizard for format/dimensions/C01..C16/foreign colors/semi-alpha/used-color and canonical structural checks. [EXTENSION]`

## Acceptance intent

Build a real Import Validation Wizard over immutable OWNER_UPLOAD source truth. Validation evidence is derived and separately identified. The source bytes and source record remain immutable.

## BLOCKERS

Automatic FAIL if the implementation:
- rewrites/recompresses/resizes/quantizes the OWNER_UPLOAD source;
- performs palette snapping or CELL_MAJORITY silently;
- implements palette/structural truth in GDScript instead of canonical Python;
- fabricates C01..C16 PASS, structural PASS, QA PASS, solver, difficulty, owner acceptance or production readiness;
- treats validation evidence as a candidate/level promotion;
- edits root `TASKS.md`;
- adds provider/network/credential dependency.

## Canonical analysis requirements

For one verified OWNER_UPLOAD source, canonical Python must derive and persist versioned validation evidence bound to:
- source_id;
- source SHA-256;
- exact source-record identity;
- validation schema/version;
- analysis policy/version.

The evidence must report at least:
- input format/media disposition;
- decoded original width/height;
- whether dimensions are legal logical dimensions under current 20..59 independent contract;
- exact/derived logical-size status;
- C01..C16 exact membership facts;
- foreign-color count;
- semi-alpha count;
- transparent/opaque facts required by the existing canonical logical-art renderer contract;
- used canonical color IDs/count where exact mapping is valid;
- structural validation disposition and exact canonical rejection codes where structural validation is applicable.

Any structural PASS/FAIL must come from canonical Python structural/art QA, using an explicitly recorded canonical policy. If no approved policy applies to a non-logical source, structural state must be NOT APPLICABLE / NEEDS DERIVATION rather than guessed.

## Exact logical source behavior

If the imported raster is already an exact logical artwork:
- legal width/height;
- one raster pixel per logical cell;
- exact canonical palette/alpha contract;

the wizard may derive a logical C-ID grid without changing bytes and run canonical structural checks.

It must prove the derived logical grid is a read-only interpretation of the exact source pixels.

## Non-canonical source behavior

If transformation is required:
- source remains immutable;
- wizard reports `DERIVED_ARTIFACT_REQUIRED` or equivalent;
- it exposes the exact reason(s);
- it names the applicable locked policies where relevant, including `CELL_MAJORITY_V1` and `PALETTE_SNAP_V1`;
- it does not claim the hypothetical derived artifact already exists.

An explicit derived-artifact next-step may be presented, but silent transformation is forbidden.

## Evidence lifecycle

Revalidation of the same unchanged source + same policy must be deterministic.
Tampered/missing source or mismatched evidence must fail closed.
Validation evidence never overwrites owner source truth.

## Studio UI

The real Import surface must expose a validation workflow with:
- source identity;
- Run/Re-run validation;
- format/dimensions;
- palette facts;
- foreign/semi-alpha counts;
- used colors;
- structural disposition/rejection codes;
- immutable-source notice;
- transformation-needed notice where applicable;
- solver/difficulty/owner acceptance explicitly unavailable.

## Real integration required

Committed Godot integration must prove:
1. import an exact-valid logical PNG and validate it through real Studio -> Python;
2. compare reported dimensions/palette counts/grid identity against source pixels;
3. exercise canonical structural analysis where applicable;
4. import a source with at least one foreign color and prove rejection/fact count;
5. exercise semi-alpha or the canonical alpha-invalid case;
6. exercise illegal/non-logical dimensions and prove derived-artifact-required truth;
7. prove source.png/source.json bytes never change;
8. tamper source/evidence and prove fail-closed behavior;
9. clean bounded artifacts.

## Batch-mode note

This task may be implemented immediately after SB-LFX-003 without an intermediate ChatGPT audit. Prior SB-LFX implementation is context, not acceptance. Do not edit tracker state.

## Verification / publication

Require focused tests, real Godot integration, retained LFX-001..003/LF06 regressions, full pytest, compileall, headless boot, diff-check, empty TASKS diff, exact file review, and a separate task-final builder-log-only commit.

## PASS rule

PASS only when the wizard reports canonical import facts deterministically from immutable source truth, uses canonical Python for structural truth, distinguishes exact logical art from sources requiring derivation, and never mutates/promotes the source.
