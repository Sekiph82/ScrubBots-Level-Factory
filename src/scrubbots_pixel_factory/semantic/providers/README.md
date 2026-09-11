# SP02 provider bridges

SP02 adds two explicit provider boundaries while keeping the semantic core and
default installation offline:

- `MAGNIFIC` is a local job-spec/result-import bridge. It records the explicit
  model, rendered prompt, supported aspect ratio, ordered role/hash-to-creation
  bindings, logical dimensions as provenance, and the original seed without
  claiming provider seed control or exact logical output.
- `PIXELLAB` is an optional official-package adapter. Its package is lazy and
  its secret is read only from `PIXELLAB_SECRET` (with optional
  `PIXELLAB_BASE_URL`). PIXFLUX supports exact requested dimensions, including
  16×16, and a deterministic project-owned provider seed. Native controls are
  passed only through the explicit mapping table in the bridge; unsupported
  mappings fail closed. BitForge is exposed as a separately selected engine
  where its supported style/init/color bindings are explicit.

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
