# SB-LF07-C001-R07 — M07 Final Provenance-Seal Remediation Prompt

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: 2026-09-27T11:20:51+03:00.
- Canonical repository: https://github.com/Sekiph82/ScrubBots-Level-Factory.
- Canonical branch: `main`.
- Canonical Level Factory root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Authoritative prompt read from the supplied live GitHub URL: `SB-LF07-C001-R07_MASTER_REMEDIATION_PROMPT.md`.
- Safe synchronization: fetched `origin/main` and fast-forwarded from `abbef08b2bc31d8e973d97a5e468f2632075a3ae` to starting authority `bad960fbd0bb7a3f4e69641821bc1ec21de0c1d6`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Initial tracked status was clean. Existing owner/untracked files were preserved and never staged.
- Read root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the R07 index, both dedicated R07 prompts, the R06 strict re-audits, and prior builder evidence.
- Scope executed exactly as authorized: `SB-LF07-008 -> SB-LF07-010`. Frozen PASS/CLOSED tasks 001,002,003,004,005,006,007,009 were not reimplemented. M08 was not started.

## SB-LF07-008 — sealed producer-derived workload provenance

- Replaced payload-controlled parent generation digest lookup with `SealedGenerationProvenance` owned by the immutable mutation substrate.
- The only production construction path accepts an actual successful `GenerationResult` retaining its exact `GenerationRequest`. It derives internally, without caller-supplied digest strings:
  - exact `GenerationRequest.digest()`;
  - exact `GenerationResult.digest()`;
  - generator id, generator version, and generator mode;
  - exact result seed and request/config identity;
  - exact `CandidateIdentity` for the parent to which the seal is bound.
- `MutationCandidate` validates the authenticity token and exact parent identity. A candidate with a seal for another parent is rejected. Tampered seal replacement is rejected by the sealed construction boundary.
- `parent_generation_request_digest()` reads only the factory-owned sealed field. Raw payload keys such as `generation_request_digest` and nested `generation_provenance` cannot establish workload availability or `MATCHED`.
- The shared canonical workload constructor remains the sole constructor for mutation and regeneration route identities. Missing sealed provenance remains `UNAVAILABLE`; request/result/seed/config drift fails closed before workload construction.
- The aligned fixture now calls the accepted `GeneratorRouter().generate(...)` route and binds that actual result to the exact parent before mutation execution. The comparison is `MATCHED` only for that aligned sealed chain.

## SB-LF07-010 — deterministic regression closure

- Rebuilt the positive regression through the sealed `GenerationResult`-derived parent path.
- Added adversarial regression coverage for forged raw 64-hex payload digest, sealed result for another request, wrong-parent binding, and tampered request/result digest.
- Retained seed-A versus workload-seed-B rejection, same-seed configuration mismatch rejection, missing provenance unavailability, authentic M03/M04/M05 validation, source preservation, safety, truthful accounting, governance, and Palette V3 regressions.

## Verification evidence

- Focused R07 suite: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_008_efficiency.py tests/unit/test_sb_lf07_010_regression.py` — `17 passed`.
- Full affected M07 004–010 gate: `38 passed`.
- Retained M03/M04/M05/M06/Palette V3 gate: `296 passed, 2 skipped`; the skips were the accepted canonical ScrubBots capability gates in SB-LF03-002 and SB-LF04-012.
- Full repository pytest: `1044 passed, 2 skipped in 334.00s`; no failure was hidden and no new skip/xfail was added.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --path level_factory --editor --quit`: passed on Godot 4.7.2.
- `git diff --check`: passed.
- Protected-file proof `git diff --name-only -- TASKS.md .hiveai/audits`: returned no paths.
- No runtime network dependency, provider spend, dependency, or license change was introduced.

## Commit and publication evidence

| Scope | Implementation commit | Terminal-log publication commit |
|---|---|---|
| SB-LF07-008 | `773ac25042917f7f8fd57e9794f0c75373f9a4f7` | `766c256d50a784c9a09fc06959ec622bab26c399` |
| SB-LF07-010 | `0a44806b98b27fb634ad62d2f11497e6f2166fce` | `1c90eef049087bba747c4ba2d7c28758905634c6` |

- Both task logs were committed and pushed separately in scope order. The final master-log commit follows.
- `TASKS.md` and `.hiveai/audits/**` were not edited or created. Existing owner/untracked files remain preserved and unstaged.

## Builder boundary

- This document and the two task logs are builder evidence for independent ChatGPT re-audit.
- No task, milestone, sprint, or M07 status was self-promoted to PASS/CLOSED.
- No history rewrite, reset, rebase, stash, clean, force-push, destructive checkout, legacy tracker edit, prompt rewrite, audit edit, or frozen-task reimplementation was performed.
