# PAG-SP01-C003 — Non-Success Provenance Echo & Mismatch-Test Sensitivity Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authority

Read first:

1. `.hiveai/audits/PAG-SP01-C002_SEMANTIC_PROVENANCE_BINDING_AND_ROLE_INTEGRITY_REMEDIATION_STRICT_AUDIT.md`
2. `.hiveai/codex-logs/PAG-SP01-C002_SEMANTIC_PROVENANCE_BINDING_AND_ROLE_INTEGRITY_REMEDIATION_CODEX_LOG.md`
3. `.hiveai/prompts/PAG-SP01-C002_SEMANTIC_PROVENANCE_BINDING_AND_ROLE_INTEGRITY_REMEDIATION_PROMPT.md`
4. `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
5. `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`

## Mission

Implement ONLY SP01-C003 and close exactly:

- `F-PAG-SP01-C002-001`

Do not begin SP02 Magnific integration.

This is a narrow correctness/test-sensitivity closure. Preserve the accepted SP01 architecture and all C002 provider/role checks.

## Required remediation

### 1. Make ordinary non-success construction provenance-complete

`SemanticImageCandidate.failure(request, ...)` must construct a candidate that can truthfully pass `SemanticGeneratorProvider.generate_checked(request)` when the provider itself matches and no provenance corruption exists.

At minimum it must preserve all request-known replay/provenance fields that C002 requires for non-success binding:

- `request_digest = request.digest()`;
- requested provider/model intent as appropriate for the candidate boundary;
- request seed;
- resolved requested dimensions;
- `reference_images = request.reference_images`;
- `style_image = request.style_image`;
- `init_image = request.init_image`;
- `color_reference = request.color_reference`.

For an explicit requested provider model, the non-success candidate must carry the requested model identity rather than silently dropping it to `None`.

Do not weaken `generate_checked()` to accommodate missing provenance. Fix construction, not validation.

### 2. Prove a valid non-success baseline first

Add a focused test using a request that contains ALL of the following simultaneously:

- concrete provider id matching the provider instance;
- explicit provider model;
- REFERENCE image;
- STYLE image;
- INIT image;
- COLOR_REFERENCE image.

The provider should return a normal typed non-success candidate using the standard failure constructor.

Assert that:

- `generate_checked()` returns that non-success candidate without provenance error;
- status remains the intended non-success status;
- model/input echoes exactly match the request;
- it is not converted to success and still cannot masquerade as M08 artwork.

This valid baseline is mandatory before any corruption/mismatch parameterization.

### 3. Make one-field mismatch tests sensitivity-safe

Rebuild/adjust the C002 corrupted-binding tests so they mutate exactly one field from the proven-valid baseline.

For each required binding corruption, assert `SemanticProvenanceError` and make the assertion sensitive to the intended binding, e.g. by checking the error message identifies the corrupted field/label where practical.

Required individual cases remain:

- request digest;
- provider id;
- provider version;
- workflow version;
- explicit model id;
- seed;
- requested width and/or height;
- reference images;
- style image;
- init image;
- color reference.

The test must not pass merely because some unrelated baseline mismatch already exists.

### 4. Keep coordinated foreign-result rejection

Retain at least one result that is internally self-consistent for another request but foreign to the checked request/provider. `generate_checked()` must reject it.

Where helpful, construct that foreign result through the same corrected failure constructor so its internal provenance is genuinely valid for its own request.

### 5. Preserve C002 closures

Do not weaken or remove:

- concrete provider id binding with explicit `UNSPECIFIED` neutral semantics;
- provider config binding;
- exact request/result binding checks;
- image-slot role enforcement;
- direct candidate fail-closed validation;
- deterministic request identity rules.

### 6. Preserve project scope

Do not modify accepted MASK/RULES/WFC/HYBRID/AUTO production algorithms.

Do not change M07/M08/M09/M10 contracts.

Do not add Magnific SDK/tool calls, provider network code, ComfyUI, browser automation, scraping, model weights, image normalization, or SP02 implementation.

## Builder log

Create BEFORE the first C003 source/test edit:

`.hiveai/codex-logs/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_CODEX_LOG.md`

Use exact H1:

`# PAG-SP01-C003 — Non-Success Provenance Echo & Mismatch-Test Sensitivity Closure`

Role line:

`Document role: CODEX BUILDER LOG`

Record actual HEAD, origin/main, divergence, worktree state, focused test chronology, full regression, scoped diff, commits/push, and final HEAD == origin/main divergence `0 0`.

## Verification

Run and record at minimum:

- focused SP01 semantic tests;
- explicit valid reference/model-bearing non-success baseline test;
- all one-field mismatch sensitivity tests;
- coordinated foreign-result test;
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
- Do not modify rejected M10 visual grids.
- Do not begin M11.
- Do not self-audit.

## Stop condition

Commit and push the bounded C003 remediation to `main`. Publish the completed matching builder log. Fetch origin and verify final local HEAD == origin/main with divergence `0 0`. Stop for independent ChatGPT strict audit.
