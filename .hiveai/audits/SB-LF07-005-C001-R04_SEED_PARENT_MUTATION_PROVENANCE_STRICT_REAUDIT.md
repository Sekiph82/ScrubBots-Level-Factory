# SB-LF07-005-C001-R04 — Strict Re-Audit

## Result
CHANGES_REQUIRED / SEALED TOKEN EXISTS, PUBLIC SEAL FACTORY STILL FORGEABLE

## Closed in R04
- Typed M03/M04/M05 references are carried in authentic provenance.
- `ProvenanceLedger.record()` rejects unsealed/legacy provenance.
- `dataclasses.replace()` tampering with an already sealed provenance fails.
- Root/parent/duplicate/cycle protections remain intact.

## Remaining blocker
`MutationProvenance.seal_authentic(request, result, references)` is a public classmethod on the package-exported `MutationProvenance` type. It accepts any three syntactically valid `TypedEvidenceReference` values in the required stage order and itself installs the private authenticity token/digest.

Therefore a caller can create arbitrary 64-hex evidence/producer digests for M03/M04/M05, call `seal_authentic()`, and obtain `is_authentic_sealed == True` without any `AuthenticEvidenceAdapter` or `ValidationEnvelope`.

The R04 test checks a two-reference failure but does not test a forged three-reference success path.

## R05 requirement
The authentic sealing operation must consume and verify the exact authentic ValidationEnvelope + M03/M04/M05 adapters, not raw caller-provided references. A raw-reference seal factory must not be public/package reachable. Add a forged three-reference adversarial test proving it cannot enter ProvenanceLedger.

## Disposition
OPEN / R05 REQUIRED.