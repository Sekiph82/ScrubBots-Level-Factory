# SB-LF09-003-C001 â€” Deterministic Semantic Art Helper Boundary

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authorization

Implement only the bounded first cycle for `SB-LF09-003` after the accepted
`SB-LF09-002-C001-R01` audit. Preserve accepted M00-M08 evidence, PASS/CLOSED
`SB-LF09-001`, PASS/CLOSED `SB-LF09-002`, the existing semantic contracts and
the accepted PAG-SP07 evidence chain. Do not begin `SB-LF09-004` or any later
M09, Content Platform, main-game, provider-execution, or production-publication
work.

## Mission

Add one deterministic, provider-neutral semantic/procedural art helper
boundary that can turn the existing canonical semantic request and accepted
reference/style planning contracts into a typed, auditable local helper result
or an explicit unavailable disposition. This is a planning/helper cycle, not
an owner-visible art-acceptance cycle and not a provider implementation.

The helper must not replace owner-approved art direction, claim
recognizability, fabricate owner artwork, or silently turn a plan into a
production `LEVEL_ART`, M08 candidate, gameplay board, or promoted content.

## Required implementation

1. Reuse the existing `SemanticGenerationRequest`, content-addressed
   `ImageInputDescriptor` roles, and accepted
   `SemanticReferenceStylePlan`/variant contracts. Do not create a parallel
   request or provenance model.
2. Define a versioned, canonical helper result with explicit status/disposition,
   request/input identity, typed seed identity, stable helper version, and a
   deterministic digest. The result must be immutable or defensively restored
   and reject malformed, stale, or internally inconsistent payloads.
3. Produce deterministic helper intents/recipes in stable order for the
   requested candidate count. Repeated calls with equivalent canonical input
   must be byte-identical; reference/style/init/color roles, duplicate inputs,
   and candidate identity must remain explicit and content-addressed.
4. Keep the helper provider-neutral and offline. It may produce bounded
   structured planning or procedural intent, but it must not call provider SDKs,
   HTTP endpoints, browser automation, ComfyUI, Magnific, PixelLab, or remote
   generation, and it must not spend credits.
5. Keep output classes separate. A helper result is not semantic recognizability
   evidence, owner acceptance, a normalized `LEVEL_ART` artifact, M08
   `LevelData`, a gameplay solver result, a production candidate, or a
   promotion decision. Unavailable capability must remain explicitly
   `UNAVAILABLE` rather than being simulated as success.
6. Preserve source-art immutability, logical-pixel rules, palette/dimension
   contracts, offline runtime behavior, accepted provider-boundary contracts,
   and the explicit no-production-promotion boundary.

## Required tests

Add focused offline tests for:

- canonical request/input binding and role preservation;
- deterministic helper output, digest, candidate ordering, and seed identity;
- duplicate/malformed/stale/tampered helper payload rejection;
- candidate-count bounds and explicit unavailable behavior;
- no provider/network/credential access and no production-router integration;
- preservation of the accepted PAG-SP07 planning and semantic contract tests.

Do not weaken, skip, or xfail a meaningful failure.

## Verification and handoff

- Create the matching CODEX builder log before implementation or tests. Its H1
  must exactly match this prompt title and it must immediately declare
  `Document role: CODEX BUILDER LOG`.
- Do not edit root `TASKS.md`, `.hiveai/audits/**`, this prompt, or its audit
  criteria.
- Keep implementation and log-publication commits separate.
- Run focused SB-LF09-003 tests, retained LF09-001/LF09-002/M07/M08 regressions,
  full pytest, compileall, Godot headless boot, diff-check, protected-file
  checks, and truthful offline/provider-boundary scans.
- Report unavailable owner/native/bridge capability honestly; do not convert it
  into PASS.
- Stop after non-forceful publication with the exact marker
  `AWAITING_CHATGPT_AUDIT`.

Passing builder tests are evidence only. Independent ChatGPT audit owns
acceptance, tracker state, and any later scope authorization.
