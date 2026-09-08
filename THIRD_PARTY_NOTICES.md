# Third-Party Notices and Provenance

This M00 foundation copies no third-party source code and includes no
third-party artwork, example images, or runtime algorithm package. The
repositories below are reference material approved by the authoritative task
plan. Revisions are recorded as immutable commit SHAs, not moving branch names.

Verification date: 2026-09-08. GitHub repository metadata and each repository's
license text were checked directly. The listed commit is the tip of the named
default branch at verification time.

## `ikarth/wfc_2019f`

- Repository: https://github.com/ikarth/wfc_2019f
- Verified branch: `master`
- Immutable verified commit: [`3a937fed13934722377dd7fb6dd238518fa644dd`](https://github.com/ikarth/wfc_2019f/commit/3a937fed13934722377dd7fb6dd238518fa644dd)
- License: MIT, verified from [`LICENSE`](https://github.com/ikarth/wfc_2019f/blob/3a937fed13934722377dd7fb6dd238518fa644dd/LICENSE)
- Intended role: study/reference for overlapping-pattern WFC, pattern extraction,
  retries, and rectangular output.
- Code status: reference only; no code copied or adapted in M00.

## `mxgmn/WaveFunctionCollapse`

- Repository: https://github.com/mxgmn/WaveFunctionCollapse
- Verified branch: `master`
- Immutable verified commit: [`de7d22e705e816b62b4d613199d0463820fcaef3`](https://github.com/mxgmn/WaveFunctionCollapse/commit/de7d22e705e816b62b4d613199d0463820fcaef3)
- License: MIT, verified from [`LICENSE`](https://github.com/mxgmn/WaveFunctionCollapse/blob/de7d22e705e816b62b4d613199d0463820fcaef3/LICENSE)
- Intended role: algorithm authority/reference for observation, propagation,
  contradiction, and output-periodicity concepts.
- Code status: reference only; no code copied or adapted in M00.
- Asset boundary: the upstream license distinguishes software from bundled
  sample images/tiles; no sample artwork is copied into this repository.

## `mxgmn/MarkovJunior`

- Repository: https://github.com/mxgmn/MarkovJunior
- Verified branch: `main`
- Immutable verified commit: [`42aaf24bcf54ae164fba49c0a59348297904a676`](https://github.com/mxgmn/MarkovJunior/commit/42aaf24bcf54ae164fba49c0a59348297904a676)
- License: MIT, verified from [`LICENSE`](https://github.com/mxgmn/MarkovJunior/blob/42aaf24bcf54ae164fba49c0a59348297904a676/LICENSE)
- Intended role: conceptual reference for procedural growth, regions, walks,
  rings, corridors, and rewrite-rule ideas; never a required C# runtime.
- Code status: concepts/reference only; no code copied or adapted in M00.

## `zfedoran/pixel-sprite-generator`

- Repository: https://github.com/zfedoran/pixel-sprite-generator
- Verified branch: `master`
- Immutable verified commit: [`8c2cee790b0ae5885319181e56745ae45a0f8138`](https://github.com/zfedoran/pixel-sprite-generator/commit/8c2cee790b0ae5885319181e56745ae45a0f8138)
- License: MIT, verified from [`LICENSE`](https://github.com/zfedoran/pixel-sprite-generator/blob/8c2cee790b0ae5885319181e56745ae45a0f8138/LICENSE)
- Intended role: conceptual reference for masks, symmetry, silhouettes, and
  seeded sprite mutation.
- Code status: reference only; no code copied or adapted in M00.

## Future provenance-comment convention

Any future substantial copied or adapted module must begin with a provenance
comment naming the upstream repository, immutable commit SHA, source file or
algorithm section, license, and the exact nature of the adaptation. It must
also preserve the applicable license notice in `THIRD_PARTY_NOTICES.md`.
Conceptual reimplementations must be labeled as reimplemented concepts rather
than represented as copied code. Software licensing never implies permission to
copy upstream example artwork; each asset requires separate verification.
