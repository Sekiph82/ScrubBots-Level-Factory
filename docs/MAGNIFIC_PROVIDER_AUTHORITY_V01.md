# Magnific Semantic Provider Authority V01

Date: 2026-09-11
Status: OWNER-APPROVED

## Decision

Magnific is the **primary semantic AI image provider** for the ScrubBots Semantic Pixel Studio while the owner has usable Magnific credits.

This decision supersedes any provider-specific wording in `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md` that names local ComfyUI as the first/default provider.

It does **not** supersede the provider-neutral architecture. The Factory core must remain able to replace Magnific later without rewriting M00-M10 infrastructure or semantic contracts.

## Architecture

```text
ScrubBots SemanticGenerationRequest
        ↓
provider-neutral SemanticGeneratorProvider
        ↓
MAGNIFIC semantic generation/orchestration
        ↓
raw semantic image + provider provenance
        ↓
existing local ScrubBots Factory
        ↓
normalize / palette / quality / semantic review
        ↓
M08 export + M09 batch/reproduce + Level Factory handoff
```

## Automation boundary

The local Python Factory must **not scrape or automate the Magnific website UI**.

The supported initial integration model is:

1. Factory emits canonical/versioned semantic job specifications.
2. Magnific generation is invoked through an authorized Magnific integration/orchestration surface available to the owner, including the connected Magnific tool in ChatGPT.
3. Generated images and Magnific creation/model metadata are returned through an explicit import/result manifest boundary.
4. The local Factory ingests immutable raw bytes and provenance, then performs normalization, semantic/structural QA, deterministic batch bookkeeping and export.
5. If Magnific later exposes an owner-usable direct API surface, a direct adapter may be added behind the same provider interface without changing semantic request/result contracts.

No browser scraping, credential extraction, undocumented private endpoint use or UI-driving automation is part of the architecture.

## Magnific capabilities already available to the project

The connected Magnific integration supports text-to-image generation and reference-guided generation. Available generation models are selected by model slug rather than hard-coded into the Factory.

The currently surfaced recommended model catalog includes, among others:

- `recraft-v4-1` — strong pure text-to-image / illustration generation;
- `seedream-5-pro` — high-quality general/reference-guided generation;
- `imagen-nano-banana-2-lite` — faster/lower-cost draft/high-volume generation;
- `imagen-nano-banana-2` — higher-fidelity reference-guided work;
- `gpt-2` — non-photorealistic/layout/design-oriented generation.

None is accepted as the ScrubBots default pixel-art model merely because it exists. SP04 must qualify candidate models/workflows using metadata-blind recognizability and small-pixel-art normalization evidence.

## Product strategy

For credit efficiency, the planned qualification path is:

- use a fast/lower-cost model for broad prompt/style iteration and batch candidate exploration;
- use a higher-fidelity model only when evidence shows it materially improves recognizability/style consistency;
- preserve prompt, references, model slug and all available provider metadata in provenance;
- never let Magnific output bypass local ScrubBots validation.

## Revised roadmap effects

### SP01

Still provider-neutral. Implement semantic request/result/provider contracts only. Magnific-specific implementation is forbidden in SP01 except provider-id examples/tests that do not couple the core.

### SP02 — Magnific Provider Bridge & Result Ingestion

Replaces the previous local-ComfyUI-first SP02.

SP02 must provide:

- `MAGNIFIC` provider identity/capability declaration;
- canonical Magnific job specification derived from `SemanticGenerationRequest`;
- model slug/config provenance;
- reference/style input mapping;
- result/import manifest schema;
- raw image hash/bytes ingestion boundary;
- explicit success/failure/retry semantics;
- mocked provider tests;
- a real owner-authorized Magnific smoke generation through the available integration surface;
- no browser scraping or undocumented private API usage.

### SP04 — Magnific Model/Workflow Qualification

Benchmark multiple available Magnific models/workflows against the semantic benchmark set. Acceptance is based on recognizable small pixel-art outcomes after deterministic ScrubBots normalization, not on photorealistic image quality.

### SP10 — Weekly Semantic Batch

The semantic generation stage may be Magnific-backed while owner credits are available. The batch manifest must separate paid-provider attempts from accepted normalized ScrubBots candidates so credits, failures and rejections are auditable.

## Preserve existing infrastructure

This decision does not reopen accepted M00-M10 technical contracts. Keep and reuse:

- deterministic request/RNG/provenance;
- LEVEL_ART dimensions and C01..C16 legality;
- MASK/RULES/WFC/HYBRID as control/post/puzzle infrastructure;
- M07 structural QA/diversity;
- M08 exact export;
- M09 batch/reproduce;
- M10 property/performance/review infrastructure.

## Cost rule

Magnific credits are an owner-approved project resource, but credit consumption must be visible and bounded. Future batch tooling must support explicit generation-count/credit-budget limits and must never enter an unbounded retry loop.
