# SB-LF07-005-C001-R01 — Strict Re-Audit
Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## Result
CHANGES_REQUIRED / GRAPH CHECK PARTIAL

## Closed findings
- `MutationProvenance.from_result()` now cross-checks result operator id/version in addition to request/parent/authority.
- The ledger rejects a non-root intermediate parent when that parent is not already recorded.
- Basic ancestry walking/cycle detection was added.

## Remaining frozen findings
1. **Typed/stage-labelled evidence provenance was not implemented.** `MutationProvenance.evidence_digests` remains an anonymous `tuple[str, ...]`, so M03/M04/M05 identities can be reordered/substituted without stage authority.
2. No R01 test exercises the required real multi-edge A→B→A/cycle adversary; the added test covers only an orphan parent and operator drift.
3. Root legitimacy is inferred from `parent.parent_candidate_id is None`; the ledger has no explicit registered root identity, so a forged root-like parent can bypass the missing-parent branch.
4. Provenance still depends on the open SB-LF07-004 evidence boundary.

## R02 requirement
Introduce an explicit lineage-root registration/identity authority, require all first edges to bind that exact root, add typed stage-labelled M03/M04/M05 evidence identities, and add genuine multi-edge cycle/stage-swap tests. Consume only authentic R02 evidence receipts.

## Disposition
R01 does not close SB-LF07-005.