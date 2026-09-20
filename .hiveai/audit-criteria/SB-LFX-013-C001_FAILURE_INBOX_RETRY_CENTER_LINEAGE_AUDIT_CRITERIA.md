# SB-LFX-013-C001 — Failure Inbox / Retry Center with Preserved Evidence — Strict Audit Criteria

Target:
`SB-LFX-013 — Build Failure Inbox / Retry Center that retries only eligible failed/rejected/inconclusive work while preserving failure evidence and lineage. [EXTENSION]`

## Principle

Failure Inbox is a derived view over durable failure evidence. Retry creates new lineage; it never erases or rewrites the failure that motivated it.

## Eligible evidence sources

Consume real failed/rejected/inconclusive records from available canonical batch manifests, pipeline runs, validation attempts and other committed job evidence.

Do not fabricate a failure entry from UI text alone.

## BLOCKERS

FAIL if:
- successful work is retried by “retry failed only”;
- original failure evidence is overwritten/deleted;
- retry reuses an invalid output as if successful;
- retry silently changes source identity/config without recording it;
- retry of unavailable stage is enabled without capability;
- retry creates duplicate accepted work without duplicate checks;
- TASKS is edited.

## Retry contract

Every retry attempt must record:
- new attempt ID;
- parent failure evidence ID;
- operation/stage;
- original canonical inputs/config;
- any explicitly authorized changed input;
- disposition;
- produced output identity if successful;
- lineage link.

Eligibility must be stage-specific and deterministic.

## UI

Provide Failure Inbox with filters/reasons and Retry Eligible action. Show non-retryable reason when disabled.

## Real integration

Create at least:
- validation rejection;
- generator/stage failure;
- unavailable/inconclusive stage;
- successful control item.

Prove only eligible failures retry, original evidence remains, successful stages are not redone, lineage is linked, duplicate protections remain, and retry success/failure is independently recorded.

## PASS rule

PASS when retry is selective, lineage-preserving and evidence-retaining, never a destructive “try again” shortcut.
