import json

import pytest

from scrubbots_pixel_factory.contracts.palette import (
    CANONICAL_PALETTE,
    PALETTE_DATA_PATH,
    PaletteContractError,
    load_palette,
)


EXPECTED = [
    ("C01", "#FF4500", (255, 69, 0)),
    ("C02", "#FFA800", (255, 168, 0)),
    ("C03", "#FFD635", (255, 214, 53)),
    ("C04", "#00CC78", (0, 204, 120)),
    ("C05", "#00CCC0", (0, 204, 192)),
    ("C06", "#51E9F4", (81, 233, 244)),
    ("C07", "#3690EA", (54, 144, 234)),
    ("C08", "#2450A4", (36, 80, 164)),
    ("C09", "#6A5CFF", (106, 92, 255)),
    ("C10", "#FF3881", (255, 56, 129)),
    ("C11", "#9C6926", (156, 105, 38)),
    ("C12", "#FFF8B8", (255, 248, 184)),
    ("C13", "#D4D7D9", (212, 215, 217)),
    ("C14", "#515252", (81, 82, 82)),
    ("C15", "#FFFFFF", (255, 255, 255)),
    ("C16", "#000000", (0, 0, 0)),
]


def test_pinned_palette_has_exact_immutable_values() -> None:
    assert PALETTE_DATA_PATH.is_file()
    assert [(color.id, color.hex, color.rgb) for color in CANONICAL_PALETTE.colors] == EXPECTED
    assert CANONICAL_PALETTE.ids == tuple(item[0] for item in EXPECTED)
    assert CANONICAL_PALETTE.used_color_envelope == (3, 12)
    assert CANONICAL_PALETTE.difficulty_class_derived_from_color_count is False
    assert CANONICAL_PALETTE.rgb_for("C07") == (54, 144, 234)
    assert CANONICAL_PALETTE.hex_for("C07") == "#3690EA"
    assert CANONICAL_PALETTE.id_for_rgb((54, 144, 234)) == "C07"
    assert CANONICAL_PALETTE.id_for_hex("#3690ea") == "C07"
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
