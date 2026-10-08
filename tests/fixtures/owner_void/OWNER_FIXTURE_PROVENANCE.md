# Owner-supplied VOID fixture provenance

Date accepted: 2026-10-08  
Purpose: `SB-LFX-019-C001-R01` owner-authentic transparent-art evidence

Canonical fixture:

`tests/fixtures/owner_void/017_a_single_brown_owl_centered_simple_clear_32px.png`

Owner supplied this exact image directly for use in the VOID closure task.

Verified properties before repository publication:

- dimensions: **32 x 32**
- total cells: **1024**
- transparent alpha-0 cells: **354**
- opaque alpha-255 cells: **670**
- semi-alpha cells: **0**
- distinct opaque RGB colors: **7**
- SHA-256: `9f3cff525745cd0623997cb0c2d99084e3c2ddb110457042ebdefe58cdcb7214`
- file size: **502 bytes**

This fixture satisfies the inherited game production minimum:

- artwork cells >= 200: **670**
- artwork fraction >= 25%: **670 / 1024 = 65.43%**
- used-color count 3..12: **7**
- binary alpha: PASS

The earlier approximate 550-transparent-pixel example was illustrative, not a requirement that overrides a later owner-supplied real fixture.

The fixture bytes are immutable test evidence. Tests may copy/read them but must not rewrite this file.
