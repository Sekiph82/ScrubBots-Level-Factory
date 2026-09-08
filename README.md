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

From PowerShell at the repository root:

```powershell
.\scripts\setup.ps1
.\scripts\test.ps1
```

The setup script creates or refreshes the local `.venv` with Python 3.12 and
installs the package plus its test extra. It does not delete user data. The
test script uses that environment when present, otherwise the active Python.

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
