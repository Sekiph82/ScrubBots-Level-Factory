# SB-LF07-C001-R05 — M07 Selective Master Remediation Prompt

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: 2026-09-27T07:55:04+03:00.
- Canonical repository: https://github.com/Sekiph82/ScrubBots-Level-Factory.
- Canonical branch: `main`.
- Canonical Level Factory root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- R05 authoritative prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-C001-R05_MASTER_REMEDIATION_PROMPT.md`.
- Starting Level Factory SHA after safe fast-forward from the live authority: `cce5930faab89dfdc8f4fee5686699b30fbb9561`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Initial tracked worktree was clean. Pre-existing owner/untracked files were preserved and never staged.
- Read root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the R05 master/index, every authorized R05 task prompt, original SB-LF07 criteria/prompts, and complete C001/R01/R02/R03/R04 prompt/audit history for 005, 007, 008, 009, and 010.
- Scope executed exactly in order: `005 -> 007 -> 008 -> 009 -> 010`. Frozen PASS/CLOSED tasks 001, 002, 003, 004, and 006 were not reimplemented. M08 was not started.
- Root `TASKS.md` and `.hiveai/audits/**` were not edited or created.

## Sequential implementation and publication

### SB-LF07-005

- Implementation: removed the public raw-reference `MutationProvenance.seal_authentic(request, result, references)` production factory.
- Production sealing now uses a module-private adapter boundary requiring the exact `ValidationEnvelope`, authentic adapter token, ordered M03/M04/M05 records, and producer digest derivation; `TypedEvidenceReference` values are derived internally.
- Added forged-three-reference adversarial coverage with valid-looking M03/M04/M05 stages and arbitrary 64-hex digests. The package/class raw factory is absent and the attempted call fails; forged references cannot enter `ProvenanceLedger`.
- Implementation commit: `1a932a0634be6228c9d2ed3f7cabf089ac85092b`.
- Terminal/log-only publication commit: `3db43b37848d059cecb7d7e9a22df03668dad74c`.
- Task log: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-005-C001-R05_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md`.

### SB-LF07-007

- Implementation: source-linked parents with non-null `source_art_sha256` now require an accepted M05 `SourceLinkedMutationContext` before any request/operator/validator operation; the M05 record is cross-bound to the exact parent source identity.
- Added zero-call missing/wrong-context adversarial coverage and retained per-attempt pre-check plus finally-style post-check behavior, terminal precedence, exception conversion, and exact budgets.
- Implementation commit: `64aa6a0abfbfb0560da6464af1c612d97213e408`.
- Terminal/log-only publication commit: `486da06a7453aaa5e6083b3ae1086a9c270bba66`.
- Task log: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-007-C001-R05_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md`.

### SB-LF07-008

- Implementation: added one shared `canonical_workload_identity()` constructor binding exact `GenerationRequest.digest()`, sealed target digest, validation-policy digest, and budget digest.
- Authentic mutation reports carry this identity only when supplied an exact `GenerationRequest`; absent identity remains `UNAVAILABLE`. Regeneration consumes the same constructor from `GenerationResult.request`.
- Added a deterministic actual `MATCHED` mutation/regeneration fixture using one shared identity. Same-seed changes to width/height, mode, style, theme, palette, or generator options are unmatched/unavailable.
- Raw `GenerationResult.SUCCESS` remains produced/inconclusive without an accepted M03/M04/M05 chain. Repository capability for authenticated regeneration validation is absent, so no acceptance was fabricated. Provider accounting remains unavailable/`None`.
- Implementation commit: `b0125c79d7c05d9ae489576f11b5eeef0fc2982c`.
- Terminal/log-only publication commit: `a959373935d968385d5d8c8d96f4c5ecc9b8eff8`.
- Task log: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-008-C001-R05_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md`.

### SB-LF07-009

- Implementation: the accepted M05 `SourceLinkedMutationContext` now exposes exact parent-source binding; the runner uses it before operation and retains M05 pre/post checks on every path.
- Added applied, INAPPLICABLE, NO_CHANGE, UNAVAILABLE, ERROR, request-factory mutation/exception, validator mutation/exception, and repeated-attempt tamper coverage. Any source mutation overrides the underlying outcome to terminal `ERROR`.
- Implementation commit: `5bc132755e2f48621fcdb43da443de305494e6b2`.
- Terminal/log-only publication commit: `ca7fbd52c5c7552ffb5a688b2037735380b58445`.
- Task log: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-009-C001-R05_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md`.

### SB-LF07-010

- Implementation: rebuilt regression closure around R05 provenance, exact source context, shared workload identity, matched mutate-vs-regenerate evidence, truthful availability, and Palette V3/no-proxy invariants.
- Added forged-three-reference rejection to the regression surface and made `test_sb_lf00_007_governance_authority.py` structural: a unique `[~]` row must agree with `Current Task` when present; otherwise the declared current task must be a live non-closed row, with structural sprint/next-action/status/actor coherence and no transient R03/R05 literals.
- Implementation commit: `fa9b0dad009167cb7af5eeac9852b3b8ea4acd3d`.
- Terminal/log-only publication commit: `a0ca2b6224b7340b329010ebd6f266879e4b8fbb`.
- Task log: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF07-010-C001-R05_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md`.

## Verification evidence

- Focused SB-LF07-005 provenance test: `4 passed`.
- Affected M07 004–010 suite after final closure: `30 passed`.
- SB-LF07-010 plus governance regression: `11 passed`.
- Retained M03/M04/M05/M06/Palette V3 unit gate: `296 passed, 2 skipped`; both skips were accepted canonical ScrubBots checkout/bridge capability gates.
- Final full repository pytest: `1036 passed, 2 skipped`; both skips were the same accepted capability-gated skips.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --path level_factory --editor --quit`: passed on Godot 4.7.2.
- `git diff --check`: passed.
- Protected-file proof `git diff --name-only -- TASKS.md .hiveai/audits`: returned no paths.
- Frozen 001/002/003/004/006 behavior remained covered by the retained/full green test gates; no frozen task test or tracker state was changed.
- Final implementation/log state immediately before this master log: `a0ca2b6224b7340b329010ebd6f266879e4b8fbb`, equal to `origin/main`.

## Governance and builder boundary

- No `TASKS.md` edits.
- No `.hiveai/audits/**` edits or new audit files.
- No historical prompt/log/audit rewrite.
- No reset, rebase, stash, clean, force-push, destructive checkout, provider spend, proxy difficulty truth, or runtime network dependency was introduced.
- No task or M07 status was self-promoted to PASS/CLOSED. This is builder evidence only and is handed to ChatGPT for independent re-audit.
