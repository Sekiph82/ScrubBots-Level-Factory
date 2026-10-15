# SB-LF02-008 | GPT independent source-origin / owner-art no fabrication criteria V01

## Question
Prove, across actual current pipelines, that missing user artwork is not fabricated and AI/generated/imported art cannot become “owner-original” merely because its import path says `OWNER_UPLOAD`, it was reviewed, or a caller supplied positive metadata. Owner approval/review and upstream creator identity are independent.

## Scope / explicit limits
1. Inspect real code paths: owner-upload immutable records; semantic raw/normalizer and LEVEL_ART compiler; Studio source validation and review chain; export bundle/generator classification; Release Pool publish gates; ART_FIRST tested source consume. Use code-level evidence, not names alone.
2. Fresh visual production from AI is not required; provider credentials and owner filesystem unapproved. When credible original/AI creator authority is absent, the truthful final answer is UNKNOWN/UNVERIFIED, not a forged OWNER_ORIGINAL, APPROVED, READY or accepted GAMEPLAY.
3. Any discovered reachable bypass must be repaired narrowly with exact byte/grid/hash/current-review source truth and tests that distinguish source creator, uploader, approving user and AI provider. Preserve old historical evidence and owner artifacts. A metadata field `owner_created=true` without verified provenance must not elevate class.
4. A synthetically created canonical source/review fixture proves code contract and fail-closed behavior but **does not prove genuine owner consent**, cryptographic author identity or actual remote provider origin. If signed authority is outside present system, mark external gate OPEN.
5. Focused tests must be run **locally and safely**, bounded and synthetic, on canonical Desktop checkout. Actions, CI and hosted runners MUST remain **NOT RUN** per 2026-10-15 owner cost lock. Never mark a skipped test PASS. Never require tests touching 140 genuine PNG, accepted 002, installed Release or game solver.
6. Independent source audit checks current GitHub compare/test changes, whether normal push leaves workflow manual-only, original owner-data exclusion and exact source SHA of local focused tests; note Windows symlink behavior from LF02-004 remains unverified separately.

## Outcome
PASS/CLOSED only for actual in-repository no-fabrication/origin-label invariants with focused local evidence; PARTIAL/OPEN for any demonstrable unresolved bypass. This task may close separately from native owner proof, actual AI provider verification, real game tests, full R05. Do not reopen LF02-004 unless a real regression is found.
