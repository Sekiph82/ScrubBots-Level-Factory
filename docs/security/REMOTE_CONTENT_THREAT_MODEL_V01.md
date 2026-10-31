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
| Content delivery collects unnecessary player data | The tracked telemetry-calibration module is a legacy, offline advisory processor; it accepts existing evidence and neither collects events nor contacts a provider. Its session schema allows a pseudonymous session ID; level/candidate/build/cohort IDs; timestamps; start/win/loss/restart/quit/abandon/booster events; attempts, moves, duration; difficulty score/lane; and record digests. | Linked session and gameplay data can reveal behavior and remain correlatable without names. The owner-approved analytics policy specifies no direct identifiers, 90-day raw and 12-month aggregate retention, and a 100-session recommendation threshold; these policy limits do not prove an application collection, disclosure, deletion, or deployment path. Any live telemetry requires a separate data-flow, purpose, retention, user-notice/consent, processor, and privacy review. |
| An attacker replaces both content and its digest | SHA-256 detects mismatch but does not authenticate the publisher | Signing or another authenticated trust root may be appropriate. Key ownership, provisioning, rotation, recovery, client verification, and migration are owner/security decisions; this task does not create keys or select a signing design. |

## Authenticity upgrade options — NOT APPROVED / OWNER-SECURITY DECISION REQUIRED

The existing SHA-256 manifest and pack digests provide integrity checks only. An attacker who can replace both the content and its recorded digest can produce a matching pair; hashes alone do not establish who published it. The following are decision options, not an adopted design:

1. **Release-anchored manifest signature:** sign a canonical, versioned manifest (including the exact pack digests) with a publisher key, and verify it using a public key delivered through an independently trusted application release. Ed25519 is one standardized signature option (RFC 8032). This adds publisher authentication but does not by itself prevent replay, rollback, freeze, or stale signed content.
2. **Delegated update metadata / TUF-like trust:** use separately scoped metadata roles, trusted-root versioning and rotation, and metadata version/expiry checks to address key compromise and rollback/freeze risks. This adds key custody, threshold and recovery operations, metadata lifecycle rules, and offline-client clock/availability tradeoffs (The Update Framework specification v1.0.36).

Before choosing or implementing either option, owner/security must decide and review: the trust anchor and its delivery path; single-key versus threshold authorization and key custodians; protected storage, provisioning, rotation, revocation and compromise recovery; canonical bytes, signature context/domain separation, algorithm and format version; rollback/freeze/expiry policy and offline-device clock behavior; migration and rejection behavior for unsigned, unknown-key, unknown-schema, stale or invalidly signed content; and the independent client/security acceptance evidence required before remote content is trusted.

Until those decisions are approved and the client verifier is independently reviewed, no signing key, signature verifier, publishing service, or authenticated-publishing claim is implemented or authorized here. Do not treat matching hashes as publisher authentication. References: [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html); [The Update Framework specification v1.0.36](https://theupdateframework.github.io/specification/v1.0.36/).

## Telemetry privacy impact — SOURCE-LEVEL ONLY / NOT A DEPLOYMENT APPROVAL

The tracked `src/scrubbots_pixel_factory/telemetry_calibration.py` module is explicitly marked legacy/non-production and offline. It consumes caller-supplied session records for an advisory report; the reviewed module has no collector, network sender, or integration call site, and it does not change canonical M04 difficulty. The owner-approved `docs/policies/SB_LF09_004_ANALYTICS_DATA_POLICY_V01.md` permits this design only as optional calibration evidence, with direct identifiers and raw IP prohibited, 90-day maximum raw retention, 12-month maximum aggregate retention, a 100-valid-session recommendation threshold, and no per-person personalization or automatic difficulty changes.

Even within those limits, stable pseudonymous session IDs, timestamps, level/cohort/build context, and win/loss/retry/quit/booster events can expose behavioral patterns and may be linkable to other records. Session and aggregate digests also remain deterministic correlators; their necessity and retention should be reviewed before any real deployment. The 100-session threshold reduces small-cohort exposure in recommendations but is not a guarantee against re-identification.

This source review does not establish that a game client collects or transmits these records, that the policy's retention limits are enforced in a deployed service, or that an app privacy notice/consent flow, processor, jurisdiction, access/deletion process, or security controls exist. Keep collection and transmission disabled unless the owner approves a concrete data-flow and purpose, minimization and aggregation rules (including session-digest handling), retention/deletion enforcement, user notice and any required consent, processor/data-location terms, and a product-specific privacy review. This note is an engineering assessment, not a legal conclusion.

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
