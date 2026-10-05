# .scrubpack V1 Declarative Container Specification

## Status and boundary

`.scrubpack` V1 is a ZIP-based, offline, local data container. Its contents are declarative JSON only. It carries no executable behavior and must never contain scripts, expressions, bytecode, plugins, add-ons, application resources, shaders, native binaries, symlinks, or other executable-capable entries. Inspection and extraction must treat every entry as untrusted data and must never execute or import content.

The format reuses the existing Content Pipeline allow-listed payload families and their validators: Level Data V1, `scrubbots.level_supply_plan.v1`, and `scrubbots.level.metadata.v1`. Their payload contracts remain authoritative; the pack manifest does not redefine them.

## Container identity

- Filename extension: `.scrubpack`.
- Container format: ZIP.
- Manifest path: `pack.json` at the archive root.
- Manifest schema: `scrubbots.scrubpack.manifest.v1`, version `1`.
- Container media type: `application/vnd.scrubbots.scrubpack+zip`.
- Each manifest records a lowercase pack ID, positive pack version, explicit timezone-aware creation time normalized to whole-second UTC `Z`, exact ordered level membership, and matching level count.
- Manifest media type: `application/vnd.scrubbots.scrubpack.manifest+json`.
- Per-level data media type: `application/vnd.scrubbots.level+json`.
- Per-level supply-plan media type: `application/vnd.scrubbots.supply-plan+json`.
- Per-level metadata media type: `application/vnd.scrubbots.approved-metadata+json`.

The machine-readable manifest contract is `content_pipeline/schemas/v1/scrubpack-manifest.schema.json`; the corresponding Python model, path helpers, and strict `from_dict()` round-trip validator are in `scrubbots_content_pipeline.scrubpack_spec`. For every level, `pack.json` records lowercase SHA-256 digests for the exact bytes at its three fixed member paths. Inspection can recompute these values to detect member tampering. The model rejects missing, malformed, or mismatched digest entries, level-count mismatches, and paths that do not match their level IDs.

The local `scrubbots_content_pipeline.build_scrubpack()` API accepts an explicit sequence of level inputs. Each input carries the exact descriptor and bytes for Level Data, supply plan, and metadata; a caller may construct those byte inputs from named local files with `ScrubpackPayloadInput.from_path()`. The builder validates each descriptor and payload with the existing Content Boundary and payload validator before writing any ZIP member. It returns archive bytes and frozen evidence containing the lowercase SHA-256 and byte length of the exact completed archive plus the matching pack ID/version. `verify_scrubpack_build()` checks exact archive bytes, receipt-to-manifest identity, and all internal member digests. This receipt digest is external and is never embedded in the archive it hashes. The builder does not enumerate directories or contact a remote service.

## Fixed member layout

Each level ID matches `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`. Its three files have fixed paths derived from that ID:

```text
pack.json
levels/{level_id}/level.json
levels/{level_id}/supply-plan.json
levels/{level_id}/metadata.json
```

`pack.json` lists level IDs, their three fixed member paths, and the SHA-256 of each exact payload. It cannot assign arbitrary paths. V1 archive member names are case-sensitive, relative POSIX paths. Only `pack.json` and the three `.json` paths for each declared level are permitted. Directory entries are not needed and are rejected by the member-name contract.

## Path and entry rules

Reject an archive with an absolute path, drive prefix, UNC path, backslash, empty or dot segment, `..` traversal, non-canonical separator, duplicate member name, undeclared member, unsupported extension, or a path not matching the fixed layout. Reject duplicate level IDs. No first-wins or last-wins interpretation is defined for duplicate names.

Every permitted entry is a regular JSON data file. Symlinks, encrypted or special files, Unix executable permissions, and any entry whose ZIP metadata does not describe a regular non-executable file are forbidden. A safe reader must inspect ZIP metadata and enforce these checks before reading or extracting bytes. No member may be imported, evaluated, executed, or used as an application resource.

## Versioning and deterministic extensions

This document fixes the V1 container identity, member paths, payload families, pack identity/version/time, exact ordered level membership, and safety boundary. The builder validates each explicitly supplied payload with its M11 validator and never reads the wall clock. Per-member payload digests are stored in `pack.json`; exact-pack SHA-256 remains external immutable evidence and is never embedded in the bytes it hashes. The verifier checks the receipt against the exact archive bytes, the manifest's pack identity/version, and each payload digest. Deterministic code receives time as explicit input.

The container has no network, provider, upload, CDN, credential, or runtime dependency. It does not authorize publishing or gameplay mutation.
