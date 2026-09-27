# SB-LF07-008-C001-R06 — Strict Re-Audit

## Result
CHANGES_REQUIRED / SEED BINDING CLOSED, PARENT GENERATION PROVENANCE STILL SELF-ASSERTED

## Closed in R06
- `generation_request.seed` must equal the mutation `base_seed`; seed-A / workload-seed-B now fails closed.
- Parent-bound config digest mismatch now fails closed.
- Missing parent provenance leaves mutation workload UNAVAILABLE.
- One shared canonical workload constructor remains in use on both routes.
- One aligned MATCHED fixture exists.
- Same-seed/different-config mismatches remain non-MATCHED.
- Regeneration acceptance, solver workload and provider accounting remain truthful.
- Full repository gate is green in builder evidence: 1039 passed, 2 accepted capability skips.

## Remaining blocker
The parent-side “generation provenance” is still only a caller-controlled payload field:

- `parent_generation_request_digest()` trusts `parent.payload["generation_request_digest"]` or `parent.payload["generation_provenance"]["generation_request_digest"]` whenever the value is syntactically a lowercase SHA-256.
- No accepted generator result/provenance object, construction seal, producer digest, or factory-owned binding proves that this digest actually produced the parent candidate.
- The aligned test fixture writes `generation_request.digest()` directly into the parent payload before calling `MutationCandidate.root(...)`.

Therefore caller code can mint a parent whose payload claims any chosen GenerationRequest digest, run mutation with that seed, and obtain an apparently provenance-bound MATCHED comparison even when the parent was not created from that generator request.

This violates the original SB-LF07-008 acceptance condition: the comparison must be **apples-to-apples and provenance-bound**, not merely self-consistent.

## R07 requirement
Introduce a sealed, producer-derived generation provenance binding for mutation parents.

Acceptable direction:
- derive the parent workload provenance from an actual accepted `GenerationResult` / canonical generation producer object, not from raw payload SHA text;
- the binding must carry exact GenerationRequest digest and producer/result identity;
- mutation comparison must require that sealed binding to belong to the exact parent candidate;
- arbitrary raw payload `generation_request_digest` values must not establish AVAILABLE/MATCHED workload authority;
- if no sealed generation provenance exists, comparison remains UNAVAILABLE.

Add adversarial tests proving a syntactically valid forged payload digest cannot establish MATCHED, plus one real sealed aligned MATCHED case built from accepted generation evidence.

## Disposition
OPEN / R07 REQUIRED.
