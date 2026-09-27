# SB-LF07-007-C001-R04 — Strict Re-Audit

## Result
CHANGES_REQUIRED / BOUNDED SEMANTICS CLOSED, SOURCE-LINKED ENTRY BOUNDARY REGRESSED

## Closed in R04
- Sealed target is required.
- Request/engine/validator/selection/provenance exceptions are converted to deterministic ERROR reports.
- Terminal precedence and finite exact budgets remain deterministic.
- Applied attempts use authentic validation/provenance.
- Post-check runs in a finally-style block whenever a source context is supplied.

## Remaining blockers
1. The R03 guard requiring source preservation for a source-linked parent was removed. A parent with non-null `source_art_sha256` can call `run_authentic_bounded_mutations(..., source_context=None)` and still reach TARGET_MATCH.
2. When a source context is supplied, the runner does not cross-bind `source_context.record.source_sha256` to `parent.source_art_sha256` or otherwise prove the context belongs to the exact parent source.
3. R04/010 positive tests currently use an authentic parent carrying source identity without a source context, demonstrating the bypass.

## R05 requirement
A source-linked parent must fail closed before any request/operator call unless an exact accepted M05 context is supplied and bound to that parent's source identity. Keep per-attempt pre/post/finally checks after this entry gate. Add missing-context and wrong-source-context tests.

## Disposition
OPEN / R05 REQUIRED.