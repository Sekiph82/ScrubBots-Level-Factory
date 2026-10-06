# Remote Content Manifest V1

The canonical local contract is `scrubbots.content.manifest.v1` with integer
`schema_version: 1`. Its root is closed and contains only `schema`,
`schema_version`, positive integer `content_version`, canonical
`minimum_game_version`, `disabled_levels`, `schedules`, `packs`, and `levels`. Unknown
properties and unsupported identity or version values fail closed. Add future
fields only through an explicit versioned schema evolution.

External input must enter through `parse_content_manifest_v1(raw_bytes)`, which
accepts strict UTF-8 bytes and constructs the immutable model only after JSON
and V1 validation. It rejects duplicate keys and non-finite numbers, and uses
fixed limits of 1 MiB per manifest, 32 nested arrays/objects, 4,096 items per
collection, and 16,384 Unicode code points per string. It rejects unknown
fields at the root and every nested record. Callers must not trust pre-parsed
objects at the external bytes boundary.

Each pack entry owns a canonical lowercase `pack_id`, positive `pack_version`,
provider-neutral `object_key`, lowercase SHA-256, and positive exact archive
`byte_length`. Pack IDs use `[a-z0-9][a-z0-9._-]{0,63}` and are compared
case-insensitively for collision checks. Object keys are relative forward-slash
keys rooted at `packs/`, with safe lowercase segments and a final
`.scrubpack` suffix; URLs, hosts, absolute paths, traversal, backslashes,
query/fragment syntax, and credentials are rejected. Each level entry owns a
stable `level_id` and its declared `pack_id`. Model types are immutable,
pack records are sorted by canonical pack ID, while level entries preserve the
declared array order. Level IDs use the existing path-safe grammar and are
casefold-unique, while their supplied spelling is preserved in the model and
serialized JSON. Logical collision, reference, and disabled-state comparisons
use casefold identity; IDs are not rewritten to lowercase. IDs may be nonnumeric
or gapped; no catalog order is inferred
from a numeric suffix or from sorting IDs. V1 has no explicit presentation
order field, so this contract does not renumber levels. `to_dict()` and
canonical JSON serialization are deterministic, including per-pack
`to_json_bytes()`. The empty fixture at
`content_pipeline/schemas/v1/examples/content-manifest-minimal.json` is the
canonical minimal V1 value.

`disabled_levels` is a canonical ASCII-sorted list of unique path-safe level
IDs. It records declarative state only: it does not delete the level metadata,
remove pack references, rewrite or mutate `.scrubpack` bytes, or reject an
unknown level reference at parse time. `is_level_disabled()` is a pure query
that compares valid level IDs using casefold identity;
full reference validation is owned by the later publish-validation child.

`schedules` contains zero or one canonical UTC window per `(target_kind,
target_id)`, where the target kind is `pack` or `level`. UTC instants use
whole-second `YYYY-MM-DDTHH:MM:SSZ` form; a supplied `not_after` must be later
than `not_before`. Schedule records are sorted by target kind and ID. Target
existence is checked by the later reference validator. `is_schedule_active()`
requires an explicit `at_utc`: it is inactive before start, active at start,
and inactive at or after the optional end. No clock or timezone lookup occurs.

`content_version` is a positive integer revision identity. A proposed
successor is accepted only when its version is numerically greater than the
previous accepted version; gaps are allowed, while equal or lower versions
fail closed. `check_manifest_successor()` is a pure local check and does not
persist history.

`minimum_game_version` and the explicitly supplied current game version use
the strict `MAJOR.MINOR.PATCH` grammar. Each component is a non-negative
decimal integer with no leading zero unless the component is `0`; whitespace,
signs, missing components, booleans, and other forms are rejected. The
compatibility helper compares numeric triplets: equal/newer current versions
are compatible and older versions are not. It performs no project, filesystem,
clock, network, or runtime lookup.

`check_app_content_compatibility()` is the pure app/content gate. The caller
supplies the current game version, an explicit mapping from supported manifest
schema identifiers to positive schema-version sets/sequences or ranges, and the
manifest's schema identifier, schema version, and minimum game version. It
returns one deterministic reason code and fails closed for malformed app
versions/capabilities, invalid manifest compatibility fields, unsupported
schemas, or an app version below the manifest minimum. It does not inspect or
change `content_version` history and does not parse payloads, resolve pack
references, apply disabled levels, evaluate schedules, download, activate, or
mutate content.

M15 runtime integration must later provide its current game version and
supported schema-version declaration explicitly, read the manifest's schema,
schema version, and minimum game version, and consume this compatibility result
before passing the manifest to the matching parser. A `COMPATIBLE` result is
only permission to continue to the separate parse and content-validation steps:
M15 must still run reference validation, disabled-level handling, and schedule
evaluation using their own contracts and explicit inputs. Compatibility PASS
does not bypass or imply success for those checks. This repository does not
implement that runtime integration.

This manifest is declarative local data. It contains no executable payload,
provider choice, URL, credential, or runtime operation. It does not publish,
upload, download, resolve references, or change `.scrubpack` identity. Level
metadata, schedules, reference validation, history, and parser workflows are
defined by later M13 child contracts.
