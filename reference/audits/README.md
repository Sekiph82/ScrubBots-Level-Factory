# SCRUBBOTS Audit Reference Archive

This directory is a **read-only historical reference** copied from the main SCRUBBOTS repository for the Pixel Art Generator / Level Factory work.

Source repository:
- https://github.com/Sekiph82/Scrubbots

Source main commit when this archive was assembled:
- `a438799498e71a8108ca65943dea9becb0fdb5e3`

## Why these audits are here

The Pixel Art Generator V1 depends on decisions and validated contracts established in the main game. Keeping the relevant audit history locally prevents later implementation agents from accidentally reviving rejected assumptions or weakening owner-locked rules.

Included audit chains:

- **M07-C001** — visual/reference asset intake and classification relevant to pixel artwork.
- **M09-C001** — pixel-art importer and exact pixel/Level Data conversion.
- **M09-C002** — batch importer, validation, destination safety and catalog ownership.
- **M10-C001** — ACTIVE/CLEARED renderer model and transparency behavior.
- **META-C004** — canonical ACTIVE/CLEARED gameplay-cell semantics.
- **META-C005** — canonical C01..C16 palette, BG01 background and visual-contract lock.
- **AUDIT_INDEX.md** and **AUDIT_POLICY.md** — source audit history/index and audit governance.

## Authority

These files are historical evidence only.

They do **not** replace:
1. the current owner instructions,
2. the current `tasks.md` in this repository,
3. the live canonical contracts in `Sekiph82/Scrubbots`.

If this archive conflicts with a later owner-approved rule in the main SCRUBBOTS repository, the later owner-approved rule wins.

## Preservation rule

Do not edit archived audit contents to make them match current implementation. If a correction is needed, create a new audit in this repository and leave the historical source copy unchanged.
