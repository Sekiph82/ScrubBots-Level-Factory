# PROMPT P3 — Headless, resumable batch processing of imported art (unattended runs)

Repository: `Sekiph82/ScrubBots-Level-Factory`. Follow GOVERNANCE.md / AGENTS.md / CLAUDE.md.

## Context

An external art producer (the owner's "ScrubBots Level Factory" desktop exe, which draws pixel
art with Claude from a CSV) imports each finished PNG through
`owner_upload.import_owner_upload(path)` (immutable OWNER_UPLOAD source, content-addressed).
Today the Import → Normalize → Validate → Candidate → ZIP supply/solve/Difficulty V1 → QA →
Review chain (SB-LFX-005) runs from Factory Studio (GDScript). For 100-level batches the owner
needs the same canonical chain without keeping Studio open.

## Goal

A CLI with exact parity to the Studio orchestration, e.g.

```
scrubbots-pixel pipeline run --job <producer_job.json>      # process all imported sources of a job
scrubbots-pixel pipeline status --job <producer_job.json>
```

- Input: the producer's job manifest (list of source ids / sha256 + requested sizes, background
  intent FULL, CSV row ids). Read-only for the CLI; results go to Level Factory's canonical stores.
- Runs the SAME canonical stages and gates as Studio (no second compiler, no simplified path).
- Resumable + idempotent per source: durable per-stage records; a restart skips completed stages
  and redoes only an interrupted stage of that source (same contract as SB-LFX-015).
- Ends at the owner Review Queue (READY candidates). It never ACCEPTs and never publishes.
- Bounded concurrency = 1 by default (the game solver is CPU-heavy).
- Machine-readable progress lines + a final summary (READY / REJECTED with reasons / FAILED).
- Studio's Review Queue shows the CLI results exactly as if Studio had produced them.

## Tests

Parity test (Studio path vs CLI path on the same sources → identical canonical records),
interruption at every stage + resume, idempotency on re-run, rejection reasons preserved,
offline contract preserved (no network in the core).
