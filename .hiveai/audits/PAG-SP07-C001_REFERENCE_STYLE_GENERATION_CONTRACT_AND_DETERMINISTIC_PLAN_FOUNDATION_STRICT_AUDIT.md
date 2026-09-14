# PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation
Document role: CHATGPT STRICT AUDIT

Audit date: 2026-09-14
Repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`
Builder implementation commit: `f55a1064fb8ccf24163cc8d3e815adb7e782674f`
Builder log publication commit: `8f7552e24f859550bbf21d9aaeb4f19b1e081077`
Audited prompt: `.hiveai/prompts/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_PROMPT.md`
Audited builder log: `.hiveai/codex-logs/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_CODEX_LOG.md`

## Verdict

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity summary:

- BLOCKER: 0
- MAJOR: 0
- MINOR: 3
- NOTE: 1

The product implementation is not rejected. The remaining defects are bounded acceptance-evidence/process defects. Do not redesign the SP07 planning architecture.

## Independent scope verification

The complete builder delta from tracker handoff `3efd0ae08a465294c218baddfae4c14945f41a08` through final builder publication `8f7552e24f859550bbf21d9aaeb4f19b1e081077` contains only:

- the SP07-C001 builder log;
- root/semantic exports;
- a concise semantic README addition;
- new `semantic/generation` package;
- new focused SP07 planning tests.

No accepted SP05 compiler source and no accepted SP06 quality/evidence source is modified by the builder delta. Root `TASKS.md` is not modified by the builder delta.

GitHub independently confirms final builder `main` at `8f7552e24f859550bbf21d9aaeb4f19b1e081077` before this audit publication.

## Accepted / retained technical work

The following C001 implementation is technically retained:

- isolated `semantic/generation` planning boundary outside SP05/SP06;
- exact canonical `SemanticGenerationRequest.digest()` binding;
- content-addressed `ImageInputDescriptor` binding by role, descriptor digest and content SHA-256;
- canonical local-path exclusion inherited from the existing descriptor contract;
- deterministic REFERENCE ordering followed by explicit STYLE / INIT / COLOR_REFERENCE role ordering;
- explicit duplicate REFERENCE `(role, content_sha256)` rejection;
- deterministic variant ordinals, candidate IDs and project-RNG seed derivation;
- exact candidate count preservation;
- explicit provider/model/workflow/config identity with no fallback path;
- sealed/fingerprinted public plan, variant and input-binding values;
- LEVEL_ART / ASSET_ART separation;
- no provider SDK/network/upload/generation path in the SP07 planning module;
- builder-reported focused, combined and full regressions green after the recorded fixture correction.

## Findings

### F-PAG-SP07-C001-001 — Required REFERENCE content-identity mutation proof is missing

Severity: **MINOR / acceptance-blocking evidence defect**

The authoritative C001 prompt requires an explicit test proving that changing REFERENCE content SHA changes plan identity.

Current focused coverage proves:

- reference order and exact content identities are preserved;
- duplicate REFERENCE content/role is rejected;
- STYLE content SHA mutation changes request/plan identity.

However, it does not independently mutate a REFERENCE descriptor's `content_sha256` while preserving its role/other metadata and assert the canonical request/plan identity change.

The product implementation appears consistent with the expected behavior because the plan binds `request.digest()` and each descriptor digest/content SHA. That inference is not a substitute for the literal required acceptance proof.

Required R01 closure:

- construct a baseline request with the existing legal reference set;
- replace one REFERENCE descriptor with the same role/metadata but a different content SHA-256;
- assert the request digest changes;
- assert the plan digest/canonical bytes change;
- preferably assert the affected input-binding digest and deterministic candidate ID set change while seed derivation remains governed by the unchanged canonical seed.

No production change is expected.

### F-PAG-SP07-C001-002 — Required INIT-strength identity mutation proof is missing

Severity: **MINOR / acceptance-blocking evidence defect**

The authoritative C001 prompt requires explicit proof that changing style/init strength changes request/plan identity.

Current focused coverage changes `style_strength` and proves a plan identity change, and separately verifies that baseline `init_strength` is preserved. It does not mutate `init_strength` and prove the resulting canonical request/plan identity change.

Required R01 closure:

- keep the same INIT descriptor and all other canonical fields;
- change only `init_strength` to another legal value;
- assert the request digest changes;
- assert the plan digest/canonical bytes change;
- do not claim the deterministic variant seed must change when the canonical seed itself is unchanged.

No production change is expected.

### F-PAG-SP07-C001-003 — Builder log was created after initial SP07 source/test edits

Severity: **MINOR / process defect, not product-blocking by itself**

The C001 prompt explicitly required the matching builder log to exist before product/test edits. The builder truthfully records that source/export/focused-test edits occurred before the log was created.

This historical ordering defect cannot be retroactively repaired and must not be rewritten or concealed. It does not invalidate the independently visible GitHub implementation diff, and the builder disclosed the incident rather than fabricating compliance.

R01 process requirement:

- create and verify the C001-R01 remediation log before any R01 test/source edit;
- preserve the original C001 log unchanged as historical evidence;
- record exact R01 start HEAD/origin/main/divergence and pre-existing dirt before edits.

### NOTE-001 — Variant seed and candidate identity have intentionally different dependencies

Candidate IDs bind the exact request digest, ordinal and derived seed. Variant seeds are derived from the canonical request seed and ordinal through project RNG. Therefore a non-seed request mutation such as reference content or init strength should change request/plan/candidate identity but need not change the derived variant seed. R01 tests should preserve that distinction rather than over-specify provider randomness semantics.

## Regression / publication evidence disposition

Builder evidence records:

- initial pre-log focused run: `1 failed, 8 passed`, caused by an incomplete alternate path-identity fixture;
- corrected focused run: `9 passed`;
- combined SP07 + SP06 + SP05 + relevant semantic/provider regression: `172 passed`;
- full repository: `564 passed`;
- compileall: passed;
- package import smoke: passed;
- module and installed CLI smoke: passed;
- `git diff --check`: passed apart from ordinary line-ending warnings;
- `git diff -- TASKS.md`: empty;
- scoped provider/network/credential/generation-runtime scan: clean;
- zero Magnific/PixelLab calls and zero provider credits.

These are retained as builder evidence. There is no independent GitHub CI result required for this local-cycle acceptance decision.

## Required remediation

Open only:

`PAG-SP07-C001-R01 — Required Identity-Mutation Evidence & Process Closure`

R01 is test/evidence-only unless the new literal tests unexpectedly expose an actual product defect.

Required closure:

1. explicit REFERENCE content-SHA mutation identity test;
2. explicit INIT-strength mutation identity test;
3. create R01 builder log before R01 edits;
4. rerun focused/combined/full regressions and required smokes/scans;
5. root `TASKS.md` remains untouched by Codex;
6. zero provider execution and zero credits;
7. publish implementation/test-evidence commit plus finalized R01 builder log and stop for ChatGPT strict audit.

## Final disposition

`PAG-SP07-C001` is **CHANGES_REQUIRED**, with the current product implementation retained.

Do not redesign `semantic/generation/plan.py`. The two missing literal mutation proofs and clean R01 process chronology are the bounded closure target.