import json

import pytest

from scrubbots_pixel_factory.contracts.palette import (
    CANONICAL_PALETTE,
    PALETTE_DATA_PATH,
    PaletteContractError,
    load_palette,
)


EXPECTED = [
    ("C01", "#E94B4B", (233, 75, 75)),
    ("C02", "#F28C3C", (242, 140, 60)),
    ("C03", "#F2C94C", (242, 201, 76)),
    ("C04", "#55B85A", (85, 184, 90)),
    ("C05", "#63D6A3", (99, 214, 163)),
    ("C06", "#42C7D9", (66, 199, 217)),
    ("C07", "#3E7EDB", (62, 126, 219)),
    ("C08", "#3451A3", (52, 81, 163)),
    ("C09", "#845EC2", (132, 94, 194)),
    ("C10", "#E66FA5", (230, 111, 165)),
    ("C11", "#956447", (149, 100, 71)),
    ("C12", "#E8CFA0", (232, 207, 160)),
    ("C13", "#B8C2CC", (184, 194, 204)),
    ("C14", "#3D4652", (61, 70, 82)),
    ("C15", "#FFFFFF", (255, 255, 255)),
    ("C16", "#000000", (0, 0, 0)),
]


def test_pinned_palette_has_exact_immutable_values() -> None:
    assert PALETTE_DATA_PATH.is_file()
    assert [(color.id, color.hex, color.rgb) for color in CANONICAL_PALETTE.colors] == EXPECTED
    assert CANONICAL_PALETTE.ids == tuple(item[0] for item in EXPECTED)
    assert CANONICAL_PALETTE.rgb_for("C07") == (62, 126, 219)
    assert CANONICAL_PALETTE.hex_for("C07") == "#3E7EDB"
    assert CANONICAL_PALETTE.id_for_rgb((62, 126, 219)) == "C07"
    assert CANONICAL_PALETTE.id_for_hex("#3e7edb") == "C07"
    with pytest.raises(AttributeError):
        CANONICAL_PALETTE._colors = ()


@pytest.mark.parametrize("bad_hex", ["#123456", "123456", "#FFF", "#GGGGGG"])
def test_unknown_or_malformed_hex_is_rejected(bad_hex: str) -> None:
    with pytest.raises(PaletteContractError):
        CANONICAL_PALETTE.id_for_hex(bad_hex)


@pytest.mark.parametrize("bad_rgb", [(1, 2, 3), (255, 255), (256, 0, 0), (True, 0, 0)])
def test_unknown_or_malformed_rgb_is_rejected(bad_rgb: object) -> None:
    with pytest.raises(PaletteContractError):
        CANONICAL_PALETTE.id_for_rgb(bad_rgb)  # type: ignore[arg-type]


def test_bg01_is_not_a_logical_color() -> None:
    with pytest.raises(PaletteContractError, match="BG01"):
        CANONICAL_PALETTE.validate_logical_id("BG01")


@pytest.mark.parametrize("mutation", ["missing", "duplicate_id", "duplicate_rgb", "c17"])
def test_palette_schema_rejects_illegal_content(tmp_path, mutation: str) -> None:
    raw = json.loads(PALETTE_DATA_PATH.read_text(encoding="utf-8"))
    if mutation == "missing":
        raw["colors"].pop()
    elif mutation == "duplicate_id":
        raw["colors"][1]["id"] = raw["colors"][0]["id"]
    elif mutation == "duplicate_rgb":
        raw["colors"][1]["rgb"] = raw["colors"][0]["rgb"]
        raw["colors"][1]["hex"] = raw["colors"][0]["hex"]
    else:
        raw["colors"][0]["id"] = "C17"
    path = tmp_path / "invalid-palette.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(PaletteContractError):
        load_palette(path)
