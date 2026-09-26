# SB-LF07-009-C001-R03 — Strict Re-Audit

## Result
CHANGES_REQUIRED / SUCCESS PATH PROTECTED, ALL OPERATION PATHS NOT YET PROTECTED

## Closed in R03
- M07 duplicate source record/report authority was replaced with aliases to accepted M05 source-preservation types.
- Source-linked success path performs an accepted M05 pre-check and a real post-check after mutation validation before TARGET_MATCH.
- Real byte mutation on the applied/validated path is rejected.

## Remaining blocker
The authentic runner only calls post-verification after an APPLIED mutation and successful validator return. Non-applied mutation branches (ERROR/UNAVAILABLE/INAPPLICABLE/NO_CHANGE) and validator/selection/provenance error branches can return/continue without a post-check.

The original criterion requires before/after verification for **any M07 operation that has access to source records**, not only successful applied attempts. A request factory/operator/validator bug could change source bytes and then return a non-applied/error result without the runner detecting the source mutation.

## R04 requirement
Wrap each source-linked attempt in a mandatory M05 preservation lifecycle so post-check executes in a finally-style path after every attempted operation, including non-applied and exception/error outcomes, before the final AttemptReport is returned. Add adversarial tests that mutate source then return INAPPLICABLE/ERROR or raise validation/selection error.

## Disposition
OPEN / R04 REQUIRED.