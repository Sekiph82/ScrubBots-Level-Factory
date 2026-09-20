# SB-LFX-009-C001 — Search / Filter / Smart Collections — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 3
- MINOR: 0
- NOTE: 0

## Audited chain

- Start: `71705420e697cb9f9a08fe6275a37860071cc0a2`
- Implementation: `99170b62e85fc2dd7527bdbd57fa183e21a91b8f`
- Task-final log-only: `f78ceea282c05074ba3de94eeacadd0658705328`

## Accepted implementation semantics

Discovery is computed fresh from Library/Candidate views, ordered deterministically, persists no membership list, and correctly returns `NOT AVAILABLE` for Ready for Production and Unused in Campaign.

## BLOCKER-001 — NOT AVAILABLE owner-review truth is inferred as Needs Review

Current code defines:

`Needs Review = review in {"NEEDS_REVIEW", "NOT AVAILABLE"}`

OWNER_UPLOAD source rows intentionally carry owner-review `NOT AVAILABLE` because no canonical review record exists for source-only art.

Putting those rows into `Needs Review` converts an unavailable fact into a review-state assertion. This violates the criteria's explicit prohibition on inferring unavailable metrics.

### Required remediation

Only records with grounded `NEEDS_REVIEW` semantics may join that collection. Source-only rows with owner-review NOT AVAILABLE must remain excluded or be surfaced through a separately truthful collection such as Review State Unavailable.

## MAJOR-001 — review-based collections inherit non-fail-closed review evidence

`Owner Accepted` / `Owner Rejected` consume Candidate Inbox owner-review values. Until the SB-LFX-006 review validator is fixed, malformed/tampered review JSON can influence smart-collection membership.

### Required remediation

Build review collections only from canonically validated, candidate-identity-bound review evidence.

## MAJOR-002 — required real integration is absent

The criteria require multiple source/candidate/review records and proof of:
- combined filters;
- text search;
- smart collections;
- refresh after canonical changes;
- unavailable collections;
- no mutation.

No committed real Godot Search integration suite exists. The focused test covers one imported source plus one unavailable collection only.

## MAJOR-003 — Studio exposes no actual field filters

`discover_records()` accepts a generic filter mapping, but `FactoryStudioSearch` exposes only:
- free-text query;
- collection selector.

No operator controls expose dimensions, origin/provider, review, QA, used-color or other real-field filters required by the task.

### Required remediation

Expose a bounded set of real canonical field filters in Studio and cover combined filtering in real integration.

## Disposition

`SB-LFX-009` remains open pending remediation and re-audit.
