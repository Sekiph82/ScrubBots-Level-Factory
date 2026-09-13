# SP02 Magnific Live Smoke — 2026-09-13

Document role: CHATGPT LIVE PROVIDER SMOKE EVIDENCE

## Disposition

**PROVIDER GENERATION: PASS**

**EXACT 24x24 DERIVATIVE: PASS**

**OWNER VISUAL ACCEPTANCE: PASS**

**OWNER 24x24 BASELINE ACCEPTANCE: PASS**

**LOCAL FACTORY RAW-BYTE IMPORT: UNVERIFIED**

The owner explicitly authorized one live Magnific smoke generation using available credits and subsequently approved both the resulting visual direction and the 24x24 px dimensions.

## Requested target

- Output class intent: `ASSET_ART`
- Logical/display target: `24x24 px`
- Subject: recognizable tiny wizard character
- Count: `1`
- Provider: `MAGNIFIC`
- Explicit model: `recraft-v4-1`
- Aspect ratio: `1:1`
- References: none

## Generation prompt

> Create one highly recognizable tiny pixel-art wizard character designed specifically to remain readable when reduced to a 24x24 pixel sprite. Full body, centered, front-facing, large pointed wizard hat, clear face, short robe, one hand holding a small staff, strong clean silhouette, simple chunky pixel clusters, very limited internal detail, crisp hard pixel edges, no anti-aliasing, no gradients, no text, no border, isolated subject on a plain empty background. Prioritize instant recognizability at 24x24 over realism or fine detail.

## Live provider result

The connected Magnific generation completed successfully.

Observed provider metadata:

- provider model: `recraft-v4-1`
- raw provider raster: `2048x2048`
- provider-reported generation seed: `151569`
- generation credit charge reported by provider surface: `60`
- generation timestamp: `2026-09-13T06:31:59Z`

This confirms the SP02 contract assumption that Magnific may return a large raw raster while ScrubBots retains a much smaller logical target.

## Exact 24x24 derivative

The completed raw Magnific creation was passed through Magnific's non-AI exact resize operation.

Observed derivative metadata:

- final raster dimensions: `24x24`
- resize operation: exact pixel resize, non-AI
- resize credit charge reported by provider surface: `40`
- resize timestamp: `2026-09-13T06:32:23Z`

Total provider-surface credit charge observed for this owner-authorized smoke sequence: `100`.

## Owner acceptance

Owner decision recorded on 2026-09-13:

- the generated visual is accepted as a valid semantic direction;
- the 24x24 px dimensions are accepted;
- 24x24 becomes the first owner-approved `ASSET_ART` baseline target for Semantic Pixel Studio qualification and normalization work;
- this approval does not modify the separate `LEVEL_ART` 20–59 difficulty-dimension contracts;
- this approval does not yet imply C01..C16 palette compliance or SP03 normalization acceptance.

The accepted 24x24 wizard should be treated as the first positive semantic reference, while the rejected M10 100-image pack remains the negative semantic regression set.

## Privacy / repository provenance policy

Private Magnific creation identifiers, signed CDN URLs and account-specific asset links are intentionally **not committed to the public project repository**. They remain available in the owner's connected Magnific account/chat surface.

## Remaining verification boundary

The connected Magnific surface provided creation metadata and rendered artifacts, but this audit environment did not obtain the immutable raw PNG bytes through the local Factory bridge. Therefore the following are not claimed by this evidence file:

- local `MagnificResultManifest.import_result()` execution against the live image bytes;
- project-owned SHA-256 of the live raw PNG bytes;
- end-to-end request -> external provider -> local raw-byte import proof;
- SP03 deterministic normalization;
- palette quantization or ScrubBots C01..C16 compliance.

The next engineering step is SP03 normalization, using the owner-approved 24x24 wizard as the first positive target/evidence artifact. The raw provider creation must be ingested as immutable bytes before it can become a canonical normalization fixture.

## Smoke conclusion

The live provider is reachable, generated the requested recognizable wizard candidate with the pinned `recraft-v4-1` model, and produced an exact 24x24 derivative. The owner accepted both the visual direction and 24x24 target size.

SP02 code remains technically accepted by the C003 strict audit. Live provider generation and owner visual acceptance are now proven. Local Factory live-byte ingestion remains the only unverified smoke leg and becomes an SP03 input-capture requirement rather than a reason to reopen SP02 code.