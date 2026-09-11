# PAG-SP01-C002 — Semantic Provenance Binding & Role Integrity Remediation
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authority

Read first:

1. `.hiveai/audits/PAG-SP01-C001_SEMANTIC_CONTRACTS_AND_PROVIDER_BOUNDARY_STRICT_AUDIT.md`
2. `.hiveai/codex-logs/PAG-SP01-C001_SEMANTIC_CONTRACTS_AND_PROVIDER_BOUNDARY_CODEX_LOG.md`
3. `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
4. `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
5. `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`

## Mission

Implement ONLY SP01-C002 and close:

- `F-PAG-SP01-C001-001`
- `F-PAG-SP01-C001-002`
- `F-PAG-SP01-C001-003`

Do not begin SP02 Magnific integration.

Preserve the C001 architecture. This is a bounded provenance and validation hardening cycle, not a redesign.

## Required remediation

### 1. Bind request provider intent before generation

`SemanticGeneratorProvider.validate_request()` / `generate_checked()` must fail closed when a concrete request provider identity contradicts the provider instance executing it.

At minimum, when the request specifies provider identity/configuration, validate the appropriate provider-bound fields rather than silently accepting a different provider.

Provider-neutral or intentionally unspecified values may be supported only through an explicit documented rule. Do not create ambiguous fallback behavior.

### 2. Bind returned candidate to the exact request/provider

After `generate()` returns and before `generate_checked()` returns success or failure to callers, validate all replay/provenance-critical bindings that can be checked at SP01:

- `result.request_digest == request.digest()`;
- `result.provider_id == provider.provider_id`;
- `result.provider_version == provider.provider_version`;
- `result.workflow_version == request.provider_workflow_version` when the request declares that workflow;
- `result.model_id == request.provider_model` when an explicit model is requested;
- `result.seed == request.seed`;
- `result.requested_width/height == request.resolved_dimensions()`;
- `result.reference_images == request.reference_images`;
- `result.style_image == request.style_image`;
- `result.init_image == request.init_image`;
- `result.color_reference == request.color_reference`.

Reject mismatches with a typed semantic/provider error. Do not silently rewrite the result to make it match.

The binding applies to SUCCESS and non-success typed results because failure provenance must also identify the exact attempted request/provider.

### 3. Enforce image-slot role integrity

Request construction must reject contradictory descriptor roles.

Required mapping:

- `reference_images[]` -> role `REFERENCE` only;
- `style_image` -> role `STYLE` only;
- `init_image` -> role `INIT` only;
- `color_reference` -> role `COLOR_REFERENCE` only.

Do not infer or mutate roles silently.

Keep `INPAINT` defined as a future capability but do not add a new SP02+ feature surface unless already required by SP01 contracts.

### 4. Harden direct candidate construction

`SemanticImageCandidate.__post_init__()` must fail closed for malformed provenance fields even when callers bypass convenience constructors.

At minimum:

- all reference/style/init/color values are actual `ImageInputDescriptor` values or accepted mappings converted deterministically;
- role mapping is enforced consistently;
- optional `model_id`, if present, is nonblank;
- invalid candidate status is surfaced as a semantic candidate/provider contract error rather than leaking an unrelated raw enum exception where practical.

Do not permit a typed immutable candidate object to exist with provenance fields that only fail later during canonical serialization.

### 5. Complete deterministic identity evidence

Add direct tests proving that request digest changes for each material change:

- description/prompt;
- seed;
- resolved or explicit dimensions;
- provider id;
- provider workflow version;
- provider model;
- provider config version;
- reference image content hash.

Also retain proof that:

- field/map ordering does not affect canonical identity where ordering is semantically irrelevant;
- audit timestamps/non-identity metadata do not affect identity;
- local path changes do not affect source/request identity for identical content.

### 6. Required mismatch tests

Add direct negative tests where a provider returns an otherwise valid typed candidate with exactly one binding corrupted at a time:

- wrong request digest;
- wrong provider id;
- wrong provider version;
- wrong workflow version;
- wrong explicit model id;
- wrong seed;
- wrong requested dimensions;
- wrong reference echo;
- wrong style/init/color echo.

Also test that a request naming provider A cannot be executed by provider B without explicit neutral-provider semantics.

Add role mismatch tests for all four input slots.

Add at least one coordinated mismatch test that changes several result fields together so they are internally self-consistent but still do not match the checked request/provider. `generate_checked()` must reject it.

### 7. Preserve accepted behavior

Do not modify accepted MASK/RULES/WFC/HYBRID/AUTO production algorithms.

Do not change M07/M08/M09/M10 contracts.

Do not add Magnific SDK/tool calls, HTTP/network runtime, ComfyUI, model weights, browser automation or scraping.

Do not normalize semantic raw images into logical grids yet. That remains later work.

## Builder log

Create BEFORE the first C002 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP01-C002_SEMANTIC_PROVENANCE_BINDING_AND_ROLE_INTEGRITY_REMEDIATION_CODEX_LOG.md`

Use exact H1:

`# PAG-SP01-C002 — Semantic Provenance Binding & Role Integrity Remediation`

Role line:

`Document role: CODEX BUILDER LOG`

Record actual current HEAD, origin/main, divergence and worktree state before implementation edits.

## Verification

Run and record at minimum:

- focused SP01 semantic tests;
- all new provenance-binding mismatch tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone package import;
- module CLI help;
- installed CLI help where practical;
- offline/provider-boundary scan;
- `git diff --check`;
- final scoped diff/status.

## Forbidden

- Do not begin SP02.
- Do not call or consume Magnific credits.
- Do not add Magnific-specific production code.
- Do not install/implement ComfyUI.
- Do not edit root `TASKS.md` acceptance state.
- Do not modify the rejected M10 visual grids.
- Do not begin M11.
- Do not self-audit.

## Stop condition

Commit and push the bounded C002 remediation to `main`. Publish the completed matching builder log. Fetch origin and verify final local HEAD == origin/main with divergence `0 0`. Stop and return the C002 builder log for independent ChatGPT strict audit.