# Cross-Repository Schemas

This directory is the target home for versioned declarative contracts shared between the Content Platform and the SCRUBBOTS game runtime.

Authority: `docs/CROSS_REPO_CONTRACT_V01.md`.

Planned schema families:

- LevelData compatibility vectors;
- Factory QA report;
- Campaign manifest;
- `.scrubpack`;
- remote content manifest;
- runtime content registry fixtures.

Every schema family requires deterministic golden fixtures and producer/consumer tests. A schema file existing here does not by itself prove runtime compatibility.

No executable payload schema is permitted.
