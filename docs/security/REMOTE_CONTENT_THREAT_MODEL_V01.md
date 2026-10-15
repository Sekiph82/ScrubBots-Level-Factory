# Remote Content Threat Model — V01

Status: engineering preparation only; not an independent security audit or production approval.

Scope: the Level Factory content pipeline and a future SCRUBBOTS client that consumes declarative remote level packs. The core generator remains offline. This note records source-level controls and the gates that still require owner, game-runtime, or independent review.

## Assets and trust boundaries

- Shipped game code and its built-in schemas are the executable authority. Remote content is data and must not add or change client behavior.
- A release manifest names exact pack keys, byte lengths, and SHA-256 digests. Provider-neutral content schemas do not contain R2 configuration.
- The publisher process may hold provider credentials outside project data. Those credentials must never enter a client package, manifest, player payload, or operation log.
- Production activation is a separate guarded operation requiring the canonical current-main replay, exact state preconditions, and bound owner approval. Local `PREPARED` evidence means only that a local preflight passed.

## Threats and existing controls

| Threat | Source-level control | Residual boundary |
| --- | --- | --- |
| Pack or manifest bytes are corrupted or substituted | Strict schema parsing; descriptor-bound SHA-256 and byte-length checks; exact object readback; immutable pack cache policy; conditional manifest writes | A hash is only as trustworthy as the expected digest and its delivery path. Production and client/device verification still require independent review. |
| A stale publisher overwrites newer state | Monotonic manifest versioning, expected prior digest/version, release-event sequence/tip checks, and compare-and-swap preconditions | No live provider mutation or production race test is authorized by this task. |
| A schedule activates unverified content | Schedule intent binds the candidate digest, current version/digest, approval, schema and compatibility checks, verified pack hashes, and current-main replay receipt; due execution rechecks those facts and is idempotency-bound | Durable remote scheduling and activation remain distinct from the local contract and need owner-approved staging evidence. |
| A level payload carries executable behavior | Allow-listed payload fields and types; executable-like keys and values are rejected; no dynamic loading is part of the content contract | The client importer and final shipped binary need game-owner and independent review. Static LF validation does not prove runtime behavior. |
| Provider details or secrets leak through logs | Fixed-field operation records and normalized provider result categories; no free-form provider error is serialized | A clean packaged-artifact secret scan and production operational-log review are still required. No credentials were read for this preparation. |
| Content delivery collects unnecessary player data | Current project posture is offline generation and no telemetry requirement; operation records contain no player identity fields | No telemetry system or app privacy disclosure was assessed. Any future telemetry requires a separate data inventory, purpose, retention, consent, and privacy review. |
| An attacker replaces both content and its digest | SHA-256 detects mismatch but does not authenticate the publisher | Signing or another authenticated trust root may be appropriate. Key ownership, provisioning, rotation, recovery, client verification, and migration are owner/security decisions; this task does not create keys or select a signing design. |

## Fail-closed expectations

1. Reject unknown schemas, fields, object keys, non-HTTPS endpoints, malformed digests, executable-like content, and stale state preconditions.
2. Treat missing credentials, unavailable objects, unreadable history, and failed verification as unavailable or blocked; never infer empty or healthy state.
3. Preserve the prior production manifest and source packs when a new candidate fails validation or compare-and-swap.
4. Keep rollback monotonic: restore prior declarative state as a new content version, after exact history, pack bytes, compatibility, replay, and approval checks.
5. Do not claim store compliance from this engineering note. Platform requirements must be rechecked against the final client, content flow, disclosures, and distribution plan before launch.

## Open release gates

- Choose and independently review a publisher-authentication design before relying on remote hashes as an authenticity guarantee.
- Verify that the actual game client consumes only the reviewed declarative schema and that remote packs cannot alter features or execute code.
- Perform an owner-approved, bounded staging exercise with real provider evidence before considering production controls.
- Scan the exact packaged application and release logs for publishing credentials without exposing secret values.
- Keep telemetry disabled unless the owner approves a documented privacy assessment and any required user disclosure or consent flow.
- Complete independent security and store-policy review before any production remote-content launch.

## Local source references

- `content_pipeline/src/scrubbots_content_pipeline/payload_validation.py`
- `content_pipeline/src/scrubbots_content_pipeline/m17_release_controls.py`
- `content_pipeline/src/scrubbots_content_pipeline/r2_provider.py`
- `content_pipeline/src/scrubbots_content_pipeline/operations.py`
- `docs/security/MOBILE_STORE_POLICY_BOUNDARY_V01.md`
- `docs/security/MOBILE_STORE_POLICY_RECHECK_2026-10-14.md`

