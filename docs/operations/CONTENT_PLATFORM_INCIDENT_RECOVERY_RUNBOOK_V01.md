# Content Platform Incident and Recovery Runbook V01

Status: local operator procedure; no live-provider action authorization.

## Evidence and health checks

1. Record the task/run ID, UTC time, environment, content version, and manifest SHA-256 using `OperationRecord`. Use opaque IDs and bounded reason codes only; never put tokens, credentials, player identifiers, email addresses, or free-form exception text in operational records.
2. `UNKNOWN` means bytes were not read. Do not convert a missing provider response, skipped integration test, or configured endpoint into healthy status.
3. A content-health check is meaningful only when it receives the expected manifest digest and object digest map from the validated local manifest parser, plus the exact bytes actually read from an authorized source. A matching hash report proves integrity of those observed bytes, not app activation or player availability.
4. Keep STAGING and PRODUCTION as distinct environments and record each version separately. Record disable, schedule, cancellation, and rollback as separate immutable events with the affected content version and manifest digest.

## Incident response

1. Stop new publication attempts. Preserve the first failing operation ID, run ID, environment, version, manifest digest, object key, observed digest and reason code.
2. Do not retry a mutation until the existing publication receipt and idempotency state prove whether it took effect. Escalate ambiguous post-activation state to the named operator; do not synthesize a success receipt.
3. Read only the exact manifest and objects needed to establish current state. `verify_content_health` returns `UNKNOWN` if those bytes were not observed and `FAIL` for missing or mismatched content.
4. A rollback is a new auditable content version using the previously validated known-good manifest and exact pack set. Never rewrite a prior version or overwrite a live object in place.
5. Keep user impact descriptions free of personal data. Store only safe reason codes in machine logs; put restricted diagnostic detail in the owner's approved secure incident system, never in Git or this repository.

## Backup and recovery drill

1. Export a bounded, exact object set with `export_recovery_bundle`; keep the bundle outside live publication paths and protect it using the owner's approved backup controls.
2. Run `restore_recovery_bundle` against the export. It verifies bundle and per-object SHA-256 values before returning bytes. Hashes detect corruption only when the expected bundle digest is anchored in a separate trusted record; this bundle is not signed and does not establish publisher authenticity. This helper is in-memory and does not write, upload, activate, or replace any content.
3. Before any future live restore, require independent review of the intended environment, exact object inventory, all verified digests, a tested recovery target, and explicit owner authorization for the actual mutation. No such live restore is covered by this runbook.

## Release / dry-run boundary

The local deterministic summary and mock recovery tests are not a clean-machine acceptance run, remote health check, R2 read/write, STAGING publication, production promotion, mobile-store approval, or player-delivery proof. Record those states as `UNKNOWN`, `NOT_RUN`, or owner-gated until the corresponding environment and evidence exist.
