# SB-LFX-011-C001-R01 — Exact Reproduce Real Action + Capability Remediation

Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-20 (Europe/Istanbul; exact command timestamp will be recorded at finalization).
- Canonical repository/branch: `Sekiph82/ScrubBots-Level-Factory` / `main`.
- Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Authoritative master prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LFX-004-017-C001-R01_MASTER_REMEDIATION_PROMPT.md`.
- Task R01 prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LFX-011-C001-R01_EXACT_REPRODUCE_REAL_ACTION_AND_CAPABILITY_REMEDIATION_PROMPT.md`.
- Start HEAD after fetch/equality check: `d3fd15b3b39d875a9651c6d0fbf19d674c717d68`; `origin/main` matched.
- Initial tracked status: clean; ten pre-existing untracked Godot `.uid` files remain preserved and unstaged.

## Read and findings

- Read root `TASKS.md`, governance, remediation index, SB-LFX-011 original prompt and criteria, strict audit, and exact R01 prompt from canonical `main`.
- Audited findings: MAJOR-001 no Exact Reproduce action; MAJOR-002 capability based mainly on origin string; MAJOR-003 no real canonical MATCH/draft-divergence/tamper integration.

## Scope

Validate the full canonical bundle/metadata/replay contract before enabling Exact Reproduce, invoke accepted Factory Core Reproduce with recorded metadata only, produce separate evidence/output, preserve originals, and add real integration. OWNER_UPLOAD/source retrieval remains distinct from regeneration. No `TASKS.md` edit.

Further commands, implementation, tests, failures/corrections, publication SHAs and final topology will be appended chronologically.

## Implementation and verification

- Added fail-closed `_reproduction_contract()` validation for the canonical bundle, metadata candidate/artwork identities, complete typed generation request, seed, and generator identity. Candidate discovery excludes separate reproduction outputs from the candidate catalog.
- Replaced origin-only capability inference with `EXACT_REPRODUCIBLE`, `SOURCE_RETRIEVABLE_ONLY`, or `STALE/INVALID` based on validated evidence. Added canonical `reproduce_exact()` invoking the offline Factory Core launcher, checking `MATCH`, reading the separate output bundle, comparing every bundle file byte-for-byte, and writing deterministic immutable reproduction evidence.
- Added the `reproduce-exact` launcher operation and an Exact Reproduce control on the Studio surface. No runtime network or provider dependency was added.
- First focused runtime attempt failed because the metadata request contract check omitted the recorded `seed` field; corrected the required field set. The next attempt exposed an output-path expectation mismatch and reproduction outputs being rediscovered as candidates; corrected the launcher output-root handling and excluded `studio-reproductions` from candidate discovery. These failures and corrections remain recorded here.
- `python -m compileall -q src level_factory/scripts/factory_core_launcher.py`: PASS.
- `git diff --check`: PASS.
- Real Godot R01 integration: `SB-LFX-011-C001 EXACT REPRODUCE integration PASS`.
- Retained real Godot exact-reproduction regression: `SB-LF06-011-C001 exact recorded seed/config reproduction integration PASS`.
- The R01 integration verified canonical Generate, capability gating, separate byte-identical MATCH output, source bundle immutability, tampered metadata rejection, and OWNER_UPLOAD source-retrievable-only disposition.

## Files changed

- `src/scrubbots_pixel_factory/studio_extensions.py`
- `level_factory/scripts/factory_core_launcher.py`
- `level_factory/scripts/factory_studio_reproduce.gd`
- `level_factory/tests/factory_studio_exact_reproduce_r01_integration_suite.gd`

## Scope and safety

- No `TASKS.md` or audit file was modified.
- No dependency, license, network, API-key, telemetry, or runtime cloud-generation change.
- The ten pre-existing untracked `.uid` files remain unstaged and preserved.

## Publication

- Implementation commit and final tracked diff checks will be recorded before the task-final log-only commit. The implementation commit must contain only the scoped product/test changes and this builder log; the subsequent commit will contain only this finalized log.

## Finalization before log-only commit

- Implementation commit: `4e11fbe034f154944c4c27a122b4958145ad1a83`.
- Push result: `main -> origin/main` succeeded.
- Post-push implementation equality: local `4e11fbe034f154944c4c27a122b4958145ad1a83`; `origin/main` `4e11fbe034f154944c4c27a122b4958145ad1a83`.
- `TASKS.md` diff check: unchanged.
- Tracked worktree: clean. Preserved owner `.uid` files remain untracked and unstaged.
- Final task log commit is intentionally log-only and will be published separately after this entry.
