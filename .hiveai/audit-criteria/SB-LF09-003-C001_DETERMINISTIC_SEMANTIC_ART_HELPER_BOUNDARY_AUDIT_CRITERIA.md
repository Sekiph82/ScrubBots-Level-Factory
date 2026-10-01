# SB-LF09-003-C001 — Deterministic Semantic Art Helper Boundary

Document role: STRICT AUDIT CRITERIA

PASS requires a bounded, offline, provider-neutral semantic/procedural art
helper that reuses the accepted semantic request and planning contracts without
claiming owner-visible art acceptance or production promotion.

1. The helper reuses canonical `SemanticGenerationRequest`, typed image-input
   roles, and accepted reference/style planning contracts; no parallel request,
   identity, or provenance authority is introduced.
2. Helper results are versioned, canonical, content-addressed, deterministic,
   immutable or defensively restored, and reject malformed, stale, tampered,
   or digest-inconsistent payloads.
3. Equivalent canonical requests produce byte-identical helper results with
   stable candidate ordering, explicit seed identity, bounded candidate count,
   and explicit duplicate-input behavior.
4. Provider-neutral/offline boundaries are enforced: no SDK, HTTP, browser,
   ComfyUI, Magnific, PixelLab, credential, credit, telemetry, or remote
   generation path is called or required.
5. Output classes remain separate. The helper does not claim recognizability,
   owner acceptance, normalized `LEVEL_ART`, M08 `LevelData`, gameplay solver
   truth, production candidacy, or promotion; unavailable capability is
   explicit and fail-closed.
6. Source-art immutability, logical-pixel, palette/dimension, accepted semantic
   contract, and no-production-promotion boundaries remain intact.
7. Focused tests cover canonical binding, deterministic replay/digest,
   tamper/stale/duplicate rejection, candidate bounds, unavailable behavior,
   and offline/provider isolation. Retained LF09-001/LF09-002/M07/M08 tests
   remain green.
8. Full pytest, compileall, Godot headless boot, diff/protected-file checks,
   and truthful unavailable-capability reporting pass. No owner-only,
   subjective, physical, native-device, or unavailable bridge acceptance may
   be claimed.
