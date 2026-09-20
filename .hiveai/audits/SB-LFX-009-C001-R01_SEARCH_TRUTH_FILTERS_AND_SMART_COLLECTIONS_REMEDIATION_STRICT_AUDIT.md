# SB-LFX-009-C001-R01 — Search Truth + Filters + Smart Collections Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `e005b0bcbf31d6954d1c608944bd1bfaa8624fa3`
- R01 implementation: `ad697899e86767cb487861f40553991f9adbcdcb`
- R01 terminal log-only: `d9672c05a3a5805a71d766e17f47ec9ddd1f62bf`

## Prior finding closure

### Original BLOCKER-001 — NOT AVAILABLE inferred as Needs Review — CLOSED

`Needs Review` now includes only records whose grounded review disposition is exactly `NEEDS_REVIEW`.

OWNER_UPLOAD source rows with review `NOT AVAILABLE` are no longer reclassified.

### Original MAJOR-001 — weak review-based collections — CLOSED

Discovery consumes Candidate Inbox, which now uses the validated owner-review chain from SB-LFX-006-R01. Owner Accepted / Owner Rejected are therefore derived only from validated current review evidence.

### Original MAJOR-002 — no real integration — SUBSTANTIALLY CLOSED

The new real Godot Search integration exercises:
- OWNER_UPLOAD source + Library metadata;
- two real canonical candidates;
- accepted and later rejected owner reviews;
- combined canonical filters;
- text search;
- Imported Sources;
- Needs Review;
- Owner Rejected refresh;
- Ready for Production unavailable behavior;
- non-mutating derived views.

### Original MAJOR-003 — no field filters — PARTIALLY CLOSED

Studio now exposes bounded controls for:
- record type;
- origin;
- owner review;
- QA;
- width;
- height.

Unknown filter names fail closed.

## MAJOR-001 — used-color filter contract is internally inconsistent and some required collection paths remain unproven

The Python discovery layer declares `used_color_count` as an allowed grounded filter:

`allowed_filters = {..., "used_color_count"}`

but candidate records contain only:

`"used_colors": candidate["used_colors"]`

and never populate `used_color_count`.

Therefore any `used_color_count` filter can never truthfully match a candidate.

The real Studio surface also exposes no used-color-count control even though the R01 prompt explicitly included used-color count where present.

In addition, the R01 runtime matrix does not directly assert:
- `Owner Accepted` collection membership;
- `Unused in Campaign` remains NOT AVAILABLE;
- deterministic ordering across repeated identical queries.

### Required remediation

1. Add a real `used_color_count = len(used_colors)` derived field for candidate records and expose a bounded optional Studio filter for it, or remove the advertised filter if intentionally unsupported. The UI/backend contract must agree.
2. Extend the existing real integration to assert:
   - Owner Accepted collection contains the accepted candidate before later review changes;
   - Unused in Campaign returns NOT AVAILABLE;
   - repeated identical query/filter calls return the same deterministic order.
3. Preserve fresh derived membership and zero mutation.

No architectural redesign is required.

## NOTE

The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## Disposition

`SB-LFX-009` remains open pending a narrow filter/runtime-evidence follow-up.
