# SB-LFX-016-C001-R02 — Revision Authority + Surface Integration + Matrix Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Material closure

R02:
- consumes the strengthened fail-closed revision reader;
- keeps similarity local, deterministic and advisory;
- proves deterministic repeated evidence, inclusive threshold boundary, one-cell palette change and validated revision identity transitions;
- snapshots owner-review evidence and proves similarity does not mutate it;
- integrates real pair similarity into the canonical Comparison projection.

## MAJOR-001 — operator-visible Candidate/Search similarity requirement remains incomplete

The authoritative criteria require advisory evidence to be shown in Candidate / Comparison / Search surfaces with clear language that owner review decides significance.

Comparison now displays a real canonical pair result and labels it advisory.

Candidate Inbox and Search backend records, however, receive only generic `NOT AVAILABLE` placeholders unless a pair is selected elsewhere. More importantly, the current Search GDScript renderer does not render `similarity_advisory` at all; it displays only record IDs and the general query reason.

The R02 integration verifies backend payload fields but does not assert operator-visible Search text/state. This leaves the explicit UI criterion open.

### Required follow-up

- Add a bounded canonical peer-selection/compare path from Candidate and Search surfaces, or clearly render NOT AVAILABLE plus the canonical compare action/reason when no peer is selected.
- Search UI must visibly render the advisory similarity state/evidence rather than silently dropping the backend field.
- Candidate/Comparison/Search wording must explicitly state similarity is advisory and owner review decides significance.
- Do not recompute similarity in GDScript.
- Runtime must inspect the rendered surface state/text, not backend payload alone.
- Retain deterministic/threshold/color/revision and review-immutability proofs.

## Disposition

`SB-LFX-016` remains open for R03.
