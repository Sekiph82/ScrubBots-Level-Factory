# Headless producer pipeline

The headless CLI processes images that have already been imported as immutable
`OWNER_UPLOAD` sources. It reads the producer job manifest without changing it
and writes stage references into the existing
`level_factory/output/studio-extensions/pipelines/jobs/` evidence area. Source,
candidate, supply, QA, and review records stay in their canonical stores.

## Commands

```text
scrubbots-pixel pipeline run --job <producer_job.json>
scrubbots-pixel pipeline status --job <producer_job.json>
```

`run` processes sources sequentially (concurrency 1) and resumes from durable
per-source stage events. Repeating a completed job returns its existing
terminal results. `status` only reads the manifest and saved event records; it
does not run or resume work.

## Manifest

The current manifest is UTF-8 JSON with this versioned shape:

```json
{
  "schema": "scrubbots-producer-pipeline-job",
  "schema_version": 1,
  "job_id": "october-batch-01",
  "sources": [
    {
      "source_id": "owner-upload-<64 lowercase hex digits>",
      "source_sha256": "<same 64 lowercase hex digits>",
      "requested_size": { "width": 32, "height": 32 },
      "background_intent": "FULL",
      "csv_row_id": "row-0001"
    }
  ]
}
```

`source_sha256` may be omitted when the full digest is present in `source_id`;
it may also be supplied as `sha256`. Size may be written as `requested_width`
and `requested_height`. Source and CSV row identities must be unique in a job.
Each source must already exist in the canonical owner upload store. The
requested dimensions must equal the source dimensions. The pipeline never
resizes or resamples logical source art. Unsupported palette or alpha data
retains the canonical validation rejection reason.

The CLI reports newline-delimited JSON progress events and one final summary
with `READY`, `REJECTED`, and `FAILED` counts. READY means the candidate is
visible in Studio's owner Review Queue and remains `NEEDS_REVIEW`; the CLI never
records an owner decision or publishes content.
