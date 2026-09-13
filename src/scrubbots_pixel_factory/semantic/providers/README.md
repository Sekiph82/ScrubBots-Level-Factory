# SP02 provider bridges

SP02 adds two explicit provider boundaries while keeping the semantic core and
default installation offline:

- `MAGNIFIC` is a local job-spec/result-import bridge. It records the explicit
  model, rendered prompt, model-specific capability snapshot, supported aspect
  ratio, ordered role/hash-to-creation bindings, logical dimensions as
  provenance, and the original seed without claiming provider seed control or
  exact logical output. The pinned snapshots are model-specific: `recraft-v4-1`
  supports 11 ratios excluding `21:9` and STYLE only; `seedream-5-pro` supports
  eight ratios, REFERENCE/STYLE, and `1.5k`/`2k`; `imagen-nano-banana-2-lite`
  supports ten ratios and REFERENCE/STYLE. Unknown models fail closed. Exact
  ratios win; other ratios use nearest absolute ratio distance and snapshot
  order as the deterministic tie-break. The immutable snapshot identity travels
  in job identity, so mutable catalog queries are not required at runtime.
- `PIXELLAB` is an optional official-package adapter. Its package is lazy and
  its secret is read only from `PIXELLAB_SECRET` (with optional
  `PIXELLAB_BASE_URL`). PIXFLUX supports exact requested dimensions, including
  16×16, and a deterministic project-owned provider seed. Native controls are
  passed only through the explicit mapping table in the bridge; unsupported
  mappings fail closed. BitForge is exposed as a separately selected engine
  where its supported style/init/color bindings are explicit, including the
  normalized SP01 `style_strength` mapped to the official 0–100 value.

Provider IDs are never inferred and no provider is silently substituted.
`UNSPECIFIED` remains useful only for provider-neutral SP01 construction and
tests. The registry is deterministic and imports provider modules only after a
caller explicitly selects one. No provider is called at import or construction.

SP02 stops at raw provider artwork. It does not normalize, resize, interpolate,
or quality-accept artwork; those remain later contracts. Magnific execution is
external and requires a locally supplied result manifest. PixelLab execution
is opt-in, injectable for tests, and never occurs without explicit execution
plus local credentials. Costs and usage are audit metadata, never deterministic
job identity. Neither bridge is a permanent default or a fallback for another
provider.

Magnific's negative description, transparency, camera/direction and isometric
values are prompt-guided metadata only; they are not advertised as native SP01
capabilities. Requests that require those native capabilities fail closed. The
committed smoke fixture uses the current read-only catalog snapshot observed on
2026-09-12 (`recraft-v4-1`, 1:1, single ASSET_ART candidate); this is evidence
metadata, not a permanent/default model selection.

Result manifests expose both `canonical_dict()` (full deterministic/audit
serialization) and `identity_dict()` (request/job/provider/model/status/raw
hash/dimension identity). `digest()` hashes only `identity_dict()`, excluding
failure prose, timestamps, transient URLs, audit metadata and PixelLab
usage/cost.
