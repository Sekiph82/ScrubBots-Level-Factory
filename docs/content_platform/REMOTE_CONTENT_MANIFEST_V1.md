# Remote Content Manifest V1

The canonical local contract is `scrubbots.content.manifest.v1` with integer
`schema_version: 1`. Its root is closed and contains only `schema`,
`schema_version`, positive integer `content_version`, canonical `minimum_game_version`, `packs`, and `levels`. Unknown properties and unsupported
identity or version values fail closed. Add future fields only through an
explicit versioned schema evolution.

Each pack entry currently owns only a stable `pack_id`. Each level entry owns
a stable `level_id` and its declared `pack_id`. Model types are immutable,
collections are sorted by case-sensitive ASCII identity, and `to_dict()` and
`to_json_bytes()` are deterministic. The empty fixture at
`content_pipeline/schemas/v1/examples/content-manifest-minimal.json` is the
canonical minimal V1 value.

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

This manifest is declarative local data. It contains no executable payload,
provider choice, URL, credential, or runtime operation. It does not publish,
upload, download, resolve references, or change `.scrubpack` identity. Compatibility, pack location and hashes, level metadata, disabled
or scheduled state, reference validation, history, and parser workflows are
defined by later M13 child contracts.
