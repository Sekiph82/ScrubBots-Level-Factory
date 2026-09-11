# Semantic Provider Authority V02

Date: 2026-09-11
Status: OWNER-APPROVED

## Decision

The ScrubBots Semantic Pixel Studio is now a **multi-provider semantic system**.

Approved semantic providers:

1. **MAGNIFIC** — owner-authorized external orchestration while owner credits are available.
2. **PIXELLAB** — official Pixel Lab Developer API / Python SDK direct provider.

The provider-neutral SP01 contracts remain authoritative. Neither provider may leak provider-specific assumptions into the Factory core.

`docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md` remains valid for Magnific-specific behavior. This V02 document supersedes any wording that implies Magnific is the only authorized semantic provider.

## Product strategy

Provider selection is explicit per semantic request/job. The Studio may later recommend a provider based on evidence, but SP02 must not silently auto-switch providers.

PixelLab is especially relevant to small pixel-art generation because its official API exposes exact `image_size` and deterministic `seed` inputs, while the currently authorized Magnific surface exposes neither exact logical raster dimensions nor provider seed forwarding.

SP04 qualification must compare providers/workflows on actual ScrubBots acceptance criteria rather than brand/model reputation.

## PIXELLAB official integration authority

Official reference implementation:

- Repository: `https://github.com/pixellab-code/pixellab-python`
- SDK package: `pixellab`
- Current inspected SDK version: `1.0.8`
- Official default API base URL: `https://api.pixellab.ai/v1`
- Official environment prefix: `PIXELLAB_`
- Secret environment variable: `PIXELLAB_SECRET`
- Optional base URL variable supported by the official settings model: `PIXELLAB_BASE_URL`

Secrets must never be committed, printed in logs, serialized into job/result manifests, or included in canonical digests.

### PixFlux generation surface

Official SDK method: `generate_image_pixflux` / endpoint `/generate-image-pixflux`.

The inspected official SDK exposes:

- description;
- exact image size;
- negative description;
- text guidance scale;
- outline;
- shading;
- detail;
- camera view;
- direction;
- isometric;
- no-background / transparent-background intent;
- coverage percentage;
- init image + strength;
- color image as forced palette;
- deterministic seed.

### BitForge generation surface

Official SDK method: `generate_image_bitforge` / endpoint `/generate-image-bitforge`.

In addition to the relevant controls above, the inspected official SDK exposes:

- style image + style strength;
- extra/style guidance;
- inpainting image;
- mask image;
- optional skeleton guidance;
- color image as forced palette;
- deterministic seed.

SP02 does not need to enable every BitForge feature. Capabilities must be declared only when the adapter actually maps and tests them truthfully.

### Official control vocabularies inspected

PixelLab SDK control literals include:

- Camera view: `side`, `low top-down`, `high top-down`;
- Direction: south, south-east, east, north-east, north, north-west, west, south-west;
- Outline: single color black outline, single color outline, selective outline, lineless;
- Shading: flat, basic, medium, detailed, highly detailed shading;
- Detail: low, medium, highly detailed.

ScrubBots controls must use an explicit deterministic mapping table. Unsupported semantic values must fail closed or be represented only as clearly documented prompt guidance; they must never be silently mislabeled as native PixelLab controls.

## MAGNIFIC authority

Magnific remains approved and preferred while the owner wants to use existing credits. The local Factory still must not scrape/drive the Magnific website or use undocumented/private endpoints.

The initial Magnific integration remains an external-orchestration bridge:

`SemanticGenerationRequest -> canonical Magnific job spec -> owner-authorized Magnific execution -> result manifest/raw bytes -> Factory import`.

## Network boundary

The historical procedural M00-M10 pipeline remains offline-safe.

The semantic provider layer is an explicit post-M10 exception:

- `MAGNIFIC`: local Factory remains non-networked; execution occurs via an owner-authorized external integration.
- `PIXELLAB`: direct network access to the official PixelLab API is allowed **only inside the explicit PixelLab provider adapter and only when that provider is deliberately invoked**.

Importing the package, running existing generators, tests, normalization, validation, export, or selecting another provider must not trigger PixelLab network access.

Do not weaken the general offline/network guard globally merely to make the PixelLab adapter work. Scope the exception to the explicit provider module/operation and test that boundary.

## Cost / credit rule

Magnific credits and PixelLab API usage are owner-approved resources only when explicitly invoked.

All provider attempts must later be auditable by provider, engine/model/workflow, request digest, result status and available cost/usage metadata.

Codex must not perform live paid generation during implementation unless the owner explicitly authorizes that exact run. Mocked/provider-client tests are required first.

## SP02 revised scope

SP02 is now:

**PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion**

SP02-C001 must establish:

- shared provider selection/registry boundary;
- existing Magnific external job-spec/result-import bridge;
- PixelLab direct API job mapping and adapter boundary;
- PixelLab PixFlux support sufficient for text-to-image smoke generation;
- BitForge mapping foundation, with style-image support if implemented/tested;
- exact provider/request/result provenance;
- secret-safe configuration;
- no normalization yet;
- mocked/offline tests for both bridges;
- deterministic smoke fixtures for both providers.

A live Magnific smoke may be executed later through the connected owner-authorized Magnific integration. A live PixelLab smoke requires owner-provided `PIXELLAB_SECRET` in a local environment and explicit execution authorization.

## Downstream qualification

SP04 is renamed conceptually to **Semantic Provider / Model / Workflow Qualification** and must compare Magnific and PixelLab candidates where cost/access permits.

No permanent provider/model default is owner-accepted merely by completing SP02 connectivity.
