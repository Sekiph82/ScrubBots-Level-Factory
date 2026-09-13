# SP02 Magnific Live Smoke — 2026-09-13

Document role: CHATGPT LIVE PROVIDER SMOKE EVIDENCE

## Disposition

**PROVIDER GENERATION: PASS**

**EXACT 24x24 DERIVATIVE: PASS**

**LOCAL FACTORY RAW-BYTE IMPORT: UNVERIFIED**

The owner explicitly authorized one live Magnific smoke generation using available credits.

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

The 24x24 derivative is a smoke artifact only. It is **not** evidence that ScrubBots SP03 normalization is implemented or accepted, and it must not be promoted as canonical normalized artwork merely because its dimensions are 24x24.

## Privacy / repository provenance policy

Private Magnific creation identifiers, signed CDN URLs and account-specific asset links are intentionally **not committed to the public project repository**. They remain available in the owner's connected Magnific account/chat surface.

## Remaining verification boundary

The connected Magnific surface provided creation metadata and rendered artifacts, but this audit environment did not obtain the immutable raw PNG bytes through the local Factory bridge. Therefore the following are not claimed by this evidence file:

- local `MagnificResultManifest.import_result()` execution against the live image bytes;
- project-owned SHA-256 of the live raw PNG bytes;
- end-to-end request -> external provider -> local raw-byte import proof;
- SP03 deterministic normalization;
- palette quantization or ScrubBots C01..C16 compliance;
- semantic owner acceptance of the resulting artwork.

The next engineering step should ingest a real provider image as immutable bytes into the accepted SP02 bridge, then use that captured raw artifact as the first real fixture for SP03 normalization.

## Smoke conclusion

The live provider itself is reachable and generated the requested wizard candidate with the pinned `recraft-v4-1` model. The provider also produced an exact 24x24 derivative on request.

SP02 code remains technically accepted by the C003 strict audit. The live provider generation portion of the smoke is now proven. Local Factory live-byte ingestion remains the only unverified SP02 smoke leg before treating the external bridge as end-to-end exercised.
