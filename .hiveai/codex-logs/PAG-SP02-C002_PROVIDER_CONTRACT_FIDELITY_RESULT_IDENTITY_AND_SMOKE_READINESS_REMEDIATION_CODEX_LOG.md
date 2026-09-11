# PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation
Document role: CODEX BUILDER LOG

## Start checkpoint

- Starting timestamp: 2026-09-12T00:00:46.0474529+03:00
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Branch: `main`
- Starting local HEAD: `09d3732d529bb231d40f8f0b45bfce39fbe4ad4e`
- Starting `origin/main`: `09d3732d529bb231d40f8f0b45bfce39fbe4ad4e`
- Starting divergence: `0 0`
- Initial worktree dirt was preserved and not treated as task authority: modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`, modified `docs/migration/legacy-task-trackers/PROJECT.json`, and untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, and `.hiveai/STATE.json`.

## Authority and scope

The authoritative C002 prompt, C001 strict audit, and root `TASKS.md` were read directly from GitHub. The GitHub versions of `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`, `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`, and `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md` were also read, together with the official public PixelLab SDK contract references required by the cycle.

Root `TASKS.md` is the only current status tracker. Hidden local/legacy H!veAI files are not used as authority and remain untouched. This cycle implements only SP02-C002 and closes the bounded C001 provider-contract findings. It does not begin SP03/SP04, does not modify M00-M10 algorithms or tracker/audit state, and does not use the main ScrubBots repository.

No Magnific credits, PixelLab credentials, live API calls, browser/private endpoints, or provider generation will be used. Magnific remains a local external job/result-import bridge. PixelLab remains optional, lazy, explicitly invoked, and injectable for tests.

## Planned bounded remediation

1. Keep Magnific logical requested dimensions separate from actual raw provider raster dimensions and accept valid larger rasters without normalization.
2. Replace arbitrary aspect-ratio strings with a versioned supported vocabulary, deterministic nearest-ratio mapping, documented metric/tie-break, and model-capability restrictions.
3. Make Magnific native capability flags truthful while retaining explicitly marked prompt guidance.
4. Separate deterministic result identity digests from mutable audit/cost serialization for both providers.
5. Enforce exact Magnific request/job/actual-model binding and truthful failure manifests.
6. Map BitForge `style_strength` explicitly to the official 0–100 surface, or fail closed if the bounded mapping cannot be supported.
7. Replace the stale Magnific smoke fixture with a current read-only catalog-valid explicit model slug and record the snapshot without putting mutable time in identity.
8. Add sensitivity-safe focused tests and preserve all accepted SP01/M00-M10 behavior.

This log was created before any C002 source, test, fixture, or documentation edit.

## Chronological implementation record

### Provider-contract corrections

- Magnific success import no longer compares returned raster dimensions with the logical request. Manifest construction now requires complete positive sane dimensions, valid raw SHA-256/media/status/creation data, while import preserves requested logical dimensions and actual provider dimensions separately. Non-success manifests carry no fabricated image data or creation ID, and non-success import rejects supplied raw bytes.
- Magnific now uses the versioned static vocabulary `1:1`, `21:9`, `16:9`, `9:16`, `2:3`, `3:4`, `1:2`, `2:1`, `5:4`, `4:5`, `3:2`, `4:3`. Exact matches win; otherwise nearest absolute ratio distance wins with vocabulary-order tie-break. A model capability snapshot is included in job identity, and explicit model overrides that differ from the request are rejected.
- Magnific native capabilities now advertise only text, reference, and style support. Negative description, transparency, camera/direction, and isometric are explicitly documented as prompt-guided metadata and native-required requests fail closed.
- Both result manifests now expose `identity_dict()` and hash only stable request/job/provider/model/status/raw-hash/dimension identity. Full canonical serialization retains audit metadata, transient URLs/timestamps, PixelLab usage/cost, and failure details without affecting `digest()`.
- Magnific import rejects actual-model drift and binds candidate `model_id` to the exact requested/job model.
- BitForge now carries SP01 normalized `style_strength` in job identity, maps 0.0/0.5/1.0 to 0/50/100, and passes the value to the official method kwargs. PIXFLUX continues to reject STYLE.
- The Magnific smoke fixture now uses the current read-only catalog-valid snapshot slug `recraft-v4-1`; the observation date is documented separately and is not part of job identity.

### Test chronology

- Initial expanded focused run after the first C002 edits: 16 passed, 1 failed. The failure showed the old Magnific dimension equality check remained in `import_result()`; removed that exact check while keeping manifest-level positive/sane validation.
- Focused SP02 plus full SP01 suite after correction: 54 passed.
- Full `python -m pytest -q`: 435 passed in 302.64s. One pre-existing pytest cache-permission warning was emitted; no test failed.
- `python -m compileall -q src tests`: passed.
- Standalone import verified `providers ('MAGNIFIC', 'PIXELLAB')` and `pixellab_eager_imported False`.
- Module CLI help and installed `scrubbots-pixel --help`: passed.
- Two early combined final-check commands exited before output because of malformed PowerShell quoting in the newly written secret regex. No files or repository state were changed by those shell-parse failures.
- A simplified scan then produced false positives from intentionally broad patterns (`requests` in prose and `sk-` inside existing `mask-sprite` identifiers). Those were not findings. The corrected precise scans passed: no forbidden network/browser/private-endpoint imports and no credential literals (`sk-` long-token, `AIza`, or `ghp_` patterns).
- Final `git diff --check`: passed, with normal Git LF-to-CRLF working-copy warnings only.

### Files changed in C002

- `src/scrubbots_pixel_factory/semantic/providers/magnific/bridge.py` and `magnific/__init__.py` — raster boundary, ratio vocabulary/mapping, truthful capabilities, exact model binding, failure/result validation, and exports.
- `src/scrubbots_pixel_factory/semantic/providers/pixellab/bridge.py` — BitForge style-strength mapping and result validation/identity separation.
- `src/scrubbots_pixel_factory/semantic/providers/README.md` — provider capability, ratio, catalog-snapshot, identity, and boundary documentation.
- `tests/fixtures/sp02/magnific_smoke_job.json` and `pixellab_pixflux_job.json` — canonical fixture updates.
- `tests/unit/test_sp02_provider_bridges.py` — required C002 sensitivity and BitForge tests.

The preserved pre-existing migration modifications and untracked legacy files
remain unstaged. Root `TASKS.md`, hidden tracker files, prompts, audits,
M00-M10 production algorithms, and the main ScrubBots repository were not
modified.

## Publication checkpoint

- Remediation commit: `0131e14bb7cc43beb8216308e5a5664925f10511`.
- `git push origin main`: succeeded, advancing `origin/main` from `09d3732d529bb231d40f8f0b45bfce39fbe4ad4e`.
- Post-push fetched checkpoint timestamp: `2026-09-12T00:14:51.8930290+03:00`.
- At that checkpoint local `HEAD` and `origin/main` were both `0131e14bb7cc43beb8216308e5a5664925f10511`; `git rev-list --left-right --count HEAD...origin/main` reported `0 0`.
- Final status at the checkpoint contained only the preserved pre-existing migration modifications and untracked legacy files listed in the start checkpoint. No task, audit, prompt, or accepted-production files were dirty.

This remains builder evidence for independent ChatGPT strict audit. No
provider credits, credentials, live calls, audit verdict, acceptance state, or
downstream milestone work were performed.
