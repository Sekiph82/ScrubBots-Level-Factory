# ScrubBots Level Factory and Release Pool Reset Plan

This document combines the owner's nine-step reset plan with the required manual installed-GUI acceptance loop. The active task contract remains the existing autonomous ScrubBots goal in `TASKS.md`; this file is an implementation and acceptance guide, not a second task tracker.

## 1. One canonical data tree

```text
data/
├── retained-game-levels/             # protected
├── input/                             # protected
├── palette/                           # protected
├── output/Pixellab/
│   ├── Final/                         # stable names, source PNG bytes preserved
│   ├── Grid Files/                    # stable names, atlas bytes preserved
│   ├── Transactions/                  # PixelLab atlas/import provenance
│   └── asset-name-manifest.json       # SHA, old name, stable name, atlas and frame
├── Level Factory/
│   ├── Imported/                      # immutable imported sources
│   ├── Batches/{Imports,Jobs,Control,Locks}/
│   ├── Activity/
│   ├── Workspace/{Candidates,Requests,Reproductions,Preset Runs}/
│   └── Runtime/
└── Release Pool/{Pending,Ready,Failed,Rejected}/
```

Source and installed Release code must call the same canonical-root resolver. The installed `Release` directory contains executable application files only; it is not a data source or data store.

## 2. Remove legacy path dependencies

Inventory every LF/RP reference in Python, GDScript, UI controllers, workers, importers, campaigns, settings, and installer configuration. Migrate active reads/writes to the canonical resolver. Disable old `level_factory/output`, `.objects`, `owner-uploads`, temporary solver folders, and Release-local fallback paths. Do not read or write any file under the installed `Release` tree as user data.

## 3. Reset old solver and Release Pool state

Confirm the Factory GUI and its workers are closed. Create a dry-run manifest and verify the exact removal set. Preserve `retained-game-levels`, `input`, and `palette`. Clear `data/Release Pool`, old LF batch/job/activity state, old solver caches, and obsolete non-PixelLab PNG copies. Do not keep or replay prior READY/FAILED/REJECTED solver history. Do not change protected folder contents.

## 4. Stable PixelLab filenames and metadata

Rename current files in place using deterministic names: `PX-ATLAS-000001.png` for atlases and `LF-000001.png` for Final sprites. Retain the original SHA-256, old filename, new filename, dimensions, parent-atlas SHA, and 1–16 row-major frame index in metadata. Verify each PNG's SHA before and after the rename. A later copy into `Level Factory/Imported` keeps the same short filename and bytes.

## 5. Import, solve, and Release Pool routing

Import eligible Final PNGs into `Level Factory/Imported`; enforce source SHA and deduplicate an already imported image. Keep immutable source records and batch state under `Level Factory`. Write active solver work under `Release Pool/Pending`; route genuine canonical wins to `Ready`, execution failures to `Failed`, and artwork rejection to `Rejected`. Keep clear reason and explicit retry information. Release Pool is an output, never an input source.

## 6. Batch identity, duplicate prevention, and timeout

Bind each queued PNG to its SHA-256 and immutable source record. Re-selecting the same folder must reuse the same current batch or omit previously completed SHAs; it must not create another full duplicate batch. Never solve verified READY items again. Offer explicit retry only for selected FAILED/REJECTED outcomes and retain prior attempt evidence. Set the actual solver timeout to 900 seconds end to end; timeout is inconclusive, not proof of impossibility.

## 7. Live UI and durable Activity

Write folder selection, discovered count, per-file validation progress, current PNG, solver phase, and each result to the canonical Activity store. UI and worker read that same store. Bind the main image, Details, and status to the currently processed PNG and current batch manifest. READY/FAILED/REJECTED/QUEUED totals must agree with the persisted manifest.

## 8. Close and resume

Normal app close must signal and await all app-owned solver workers and child processes. Persist the active PNG as `INTERRUPTED` before exit; no detached worker remains. Reopening the GUI must not auto-start work. On the owner's next `Run Pipeline`, select the interrupted PNG first, append the prior attempt to its history, mark the new attempt `RUNNING`, and continue with the remaining eligible PNGs.

## 9. Installed Release, LNK, and iterative manual acceptance

After the source changes and migration are verified, build/install the scoped Release update and make the Desktop LNK open that exact latest installed Release. Then run this complete Computer Use loop against the application opened from that LNK:

1. Capture a startup screenshot and verify the actual installed build/version, all three pages, and PixelLab as the Pixel Art default provider.
2. Manually exercise Pixel Art CSV selection and path display using the existing `data/input` CSV. Verify atlas/slice path routing from code and the UI without issuing a new paid generation request.
3. In Level Factory, choose `Pixellab/Final`, wait for its complete preview, and verify every current PNG appears with the short stable name, correct dimensions, and accurate counts. Import the folder and verify the resulting source list, SHA identities, and duplicate handling.
4. Start a bounded real pipeline item. Capture screenshots of the selected PNG before start, current-PNG Details while running, numeric/persisted Activity progress, and the resulting terminal status. Confirm the shown counters match the persisted batch/job state.
5. Close the application normally during an active test item. Verify the worker process exits and the current PNG is recorded as `INTERRUPTED`. Reopen through the LNK, confirm no automatic work starts, click Run, and capture evidence that this interrupted PNG resumes first.
6. Manually inspect Release Pool Pending/Ready/Failed/Rejected views and verify their counts and reasons correspond to the real batch. Do not stage or publish to external Production/R2.
7. For every observed defect: preserve the screenshot and exact log/state evidence, identify and fix its source, run the focused local check, update the scoped installed Release, close/relaunch through the LNK, and repeat the failed acceptance step. Continue until each applicable checkpoint passes or a precisely evidenced external gate remains.
8. Save dated screenshots and a test ledger under the task's builder evidence directory. The final Turkish report must state screenshot paths, app/LNK target, source and installed hashes, reset counts, protected-path before/after hashes, test outcomes, any unrun gates, and GitHub/Desktop commit parity.

No native GUI test is considered passed from static code alone. Do not claim a screenshot or manual result that was not actually observed.
