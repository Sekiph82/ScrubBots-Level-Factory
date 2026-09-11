# SCRUBBOTS Pixel Art Generator V1

This repository is the standalone **SCRUBBOTS Procedural Pixel Art Generator
V1** foundation. It is not the complete SCRUBBOTS Level Factory and does not
contain gameplay, Godot integration, a GUI, or generator families yet.

The V1 core is local Python tooling and is explicitly offline-only. Runtime
cloud image generation, HTTP/API calls, telemetry, and API keys are forbidden.
One generated logical pixel will equal one SCRUBBOTS gameplay cell; later
milestones must never resize, resample, interpolate, or antialias logical art
to fit a board.

## Windows setup and tests

From PowerShell at the repository root, use the process-scoped execution-policy
form below. It applies the bypass only to the setup/test child processes and
does not change the owner's global PowerShell policy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

The setup script prefers `py.exe -3.12`, validates any fallback `python.exe`
before use, creates or refreshes only the repository-local `.venv`, reports the
selected Python version and executable, and installs the package plus its test
extra. It does not delete user data or modify `PATH`. The test script uses that
environment when present, otherwise the active Python.

Direct equivalents are:

```powershell
python -m pip install -e ".[test]"
python -m pytest
```

## Offline contract

The package exposes a production-owned network guard in
`scrubbots_pixel_factory.offline`. Any future generator path that attempts a
network request must route through that boundary and receive an explicit
`OfflinePolicyError`. Importing the package performs no network initialization.

No third-party implementation or example artwork is copied in M00. Reference
roles, license evidence, immutable revisions, and the future provenance-comment
convention are recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Governance

`tasks.md` is the canonical task ledger. ChatGPT is the independent auditor
and tracker owner; Codex is the implementation builder only. Passing builder
tests are evidence for later independent review and do not close tasks.

## Offline CLI (M09)

The standard-library CLI is available from PowerShell as either
`python -m scrubbots_pixel_factory.cli` or, after an editable install, the
`scrubbots-pixel` console command. It provides `generate`, `reproduce` and
finite `batch` commands and never fetches network data.

Explicit `--seed` values that are canonical decimal integers (for example
`42` or `-7`) are integer seeds; every other token is a string seed. A single
`generate` may omit `--seed`, in which case the locally selected entropy seed
is printed and recorded. Batch generation requires an explicit `--seed`, a
positive `--count` of accepted unique candidates and a positive
`--max-attempts` bound.

`generate` writes one accepted M08 bundle below `--output` (default
`output`). `reproduce path\to\metadata.json` verifies the recorded request,
logical grid, bundle bytes and rich provenance; WFC-bearing requests require
the matching local `--exemplar-json`. `batch` writes a canonical
`batch-manifest.json`, candidate bundles below `candidates/`, and deterministic
review output below `review/`; resume uses `batch --resume path\to\batch-manifest.json`.
For deliberate non-default M07 thresholds, `generate` and a new batch accept a
canonical local `--quality-policy-json`; the policy is persisted and used
exactly during reproduction and resume, while resume rejects policy overrides.

Stable domain exit codes are: `0` success, `2` argparse usage error, `3`
invalid request/config, `4` generator failure, `5` quality rejection, `6`
reproduction mismatch/unsupported metadata, `7` batch exhausted before its
accepted target, and `8` filesystem/output failure.
