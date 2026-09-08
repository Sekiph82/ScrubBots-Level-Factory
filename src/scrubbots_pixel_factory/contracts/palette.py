"""Immutable, validated access to the owner-locked SCRUBBOTS palette."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from types import MappingProxyType
from typing import Any, Iterable, Mapping


_REPOSITORY_PALETTE_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "palette" / "scrubbots_palette_v2.json"
)
_INSTALLED_PALETTE_PATH = Path(sys.prefix) / "data" / "palette" / "scrubbots_palette_v2.json"
PALETTE_DATA_PATH = (
    _REPOSITORY_PALETTE_PATH
    if _REPOSITORY_PALETTE_PATH.is_file()
    else _INSTALLED_PALETTE_PATH
)
_LOGICAL_ID = re.compile(r"^C(?:0[1-9]|1[0-6])$")
_HEX = re.compile(r"^#[0-9A-F]{6}$")


class PaletteContractError(ValueError):
    """Raised when palette data or a logical color violates the M01 contract."""


@dataclass(frozen=True, slots=True)
class PaletteColor:
    id: str
    index: int
    name: str
    hex: str
    rgb: tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class BackgroundColor:
    id: str
    name: str
    hex: str
    rgb: tuple[int, int, int]


class CanonicalPalette:
    """Immutable canonical palette with fail-closed lookup methods."""

    __slots__ = ("_colors", "_by_id", "_by_rgb", "_by_hex", "background")

    def __init__(self, colors: Iterable[PaletteColor], background: BackgroundColor):
        ordered = tuple(colors)
        if tuple(color.id for color in ordered) != tuple(f"C{i:02d}" for i in range(1, 17)):
            raise PaletteContractError("canonical colors must be ordered C01 through C16")
        object.__setattr__(self, "_colors", ordered)
        object.__setattr__(self, "_by_id", MappingProxyType({c.id: c for c in ordered}))
        object.__setattr__(self, "_by_rgb", MappingProxyType({c.rgb: c.id for c in ordered}))
        object.__setattr__(self, "_by_hex", MappingProxyType({c.hex: c.id for c in ordered}))
        object.__setattr__(self, "background", background)

    def __setattr__(self, _name: str, _value: object) -> None:
        raise AttributeError("canonical palette is immutable")

    @property
    def colors(self) -> tuple[PaletteColor, ...]:
        return self._colors

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(color.id for color in self._colors)

    def color(self, color_id: str) -> PaletteColor:
        try:
            return self._by_id[color_id]
        except (KeyError, TypeError) as exc:
            raise PaletteContractError(f"unknown canonical logical color ID: {color_id!r}") from exc

    def rgb_for(self, color_id: str) -> tuple[int, int, int]:
        return self.color(color_id).rgb

    def hex_for(self, color_id: str) -> str:
        return self.color(color_id).hex

    def id_for_rgb(self, rgb: Iterable[int]) -> str:
        value = _validate_rgb_value(rgb)
        try:
            return self._by_rgb[value]
        except KeyError as exc:
            raise PaletteContractError(f"RGB value is outside canonical palette: {value!r}") from exc

    def id_for_hex(self, value: str) -> str:
        if not isinstance(value, str) or not _HEX.fullmatch(value.upper()):
            raise PaletteContractError(f"malformed HEX color: {value!r}")
        canonical = value.upper()
        try:
            return self._by_hex[canonical]
        except KeyError as exc:
            raise PaletteContractError(f"HEX value is outside canonical palette: {value!r}") from exc

    def validate_logical_id(self, value: str) -> str:
        if value == self.background.id:
            raise PaletteContractError("BG01 is presentation/background-only, not a logical cell color")
        if not isinstance(value, str) or not _LOGICAL_ID.fullmatch(value):
            raise PaletteContractError(f"malformed or off-palette logical color ID: {value!r}")
        if value not in self._by_id:
            raise PaletteContractError(f"unknown canonical logical color ID: {value!r}")
        return value

    def used_ids(self, cells: Iterable[Any]) -> tuple[str, ...]:
        used = {self.validate_logical_id(value) for value in cells}
        return tuple(sorted(used, key=lambda value: int(value[1:])))


def _validate_rgb_value(value: Iterable[int]) -> tuple[int, int, int]:
    if isinstance(value, (str, bytes)):
        raise PaletteContractError(f"RGB must contain three integer channels: {value!r}")
    try:
        channels = tuple(value)
    except TypeError as exc:
        raise PaletteContractError(f"RGB must contain three integer channels: {value!r}") from exc
    if len(channels) != 3 or any(isinstance(channel, bool) or not isinstance(channel, int) for channel in channels):
        raise PaletteContractError(f"RGB must contain three integer channels: {value!r}")
    if any(channel < 0 or channel > 255 for channel in channels):
        raise PaletteContractError(f"RGB channels must be between 0 and 255: {value!r}")
    return channels  # type: ignore[return-value]


def _load_json(path: str | Path) -> Mapping[str, Any]:
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PaletteContractError(f"canonical palette could not be read: {path}") from exc
    if not isinstance(raw, dict):
        raise PaletteContractError("canonical palette root must be an object")
    return raw


def load_palette(path: str | Path = PALETTE_DATA_PATH) -> CanonicalPalette:
    raw = _load_json(path)
    if (
        raw.get("schema") != "scrubbots-global-palette/v2"
        or raw.get("version") != 2
        or raw.get("ownerLocked") is not True
    ):
        raise PaletteContractError("unsupported canonical palette schema/version")
    production_rules = raw.get("productionRules")
    expected_bands = {
        "EASY": {"min": 3, "max": 5},
        "MEDIUM": {"min": 6, "max": 7},
        "HARD": {"min": 8, "max": 9},
        "VERY_HARD": {"min": 10, "max": 12},
    }
    if not isinstance(production_rules, dict):
        raise PaletteContractError("productionRules are required")
    if production_rules.get("offPaletteLogicalCellColors") != "FORBIDDEN":
        raise PaletteContractError("off-palette logical cell policy must be FORBIDDEN")
    if production_rules.get("difficultyColorCountBands") != expected_bands:
        raise PaletteContractError("difficulty color-count bands do not match the owner-locked contract")
    entries = raw.get("colors")
    if not isinstance(entries, list) or len(entries) != 16:
        raise PaletteContractError("canonical palette must contain exactly 16 colors")

    colors: list[PaletteColor] = []
    seen_ids: set[str] = set()
    seen_rgb: set[tuple[int, int, int]] = set()
    for expected_index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise PaletteContractError("each canonical palette color must be an object")
        color_id = entry.get("id")
        if not isinstance(color_id, str):
            raise PaletteContractError(f"malformed logical color ID: {color_id!r}")
        if color_id in seen_ids:
            raise PaletteContractError(f"duplicate canonical color ID: {color_id!r}")
        seen_ids.add(color_id)
        if not _LOGICAL_ID.fullmatch(color_id):
            raise PaletteContractError(f"malformed logical color ID: {color_id!r}")
        if color_id != f"C{expected_index + 1:02d}":
            raise PaletteContractError("canonical palette IDs/indexes must be ascending C01..C16")
        if entry.get("index") != expected_index:
            raise PaletteContractError(f"incorrect palette index for {color_id}")
        rgb = _validate_rgb_value(entry.get("rgb"))
        if rgb in seen_rgb:
            raise PaletteContractError(f"duplicate canonical RGB value: {rgb!r}")
        seen_rgb.add(rgb)
        hex_value = entry.get("hex")
        if not isinstance(hex_value, str) or not _HEX.fullmatch(hex_value):
            raise PaletteContractError(f"malformed HEX value for {color_id}")
        expected_hex = "#" + "".join(f"{channel:02X}" for channel in rgb)
        if hex_value != expected_hex:
            raise PaletteContractError(f"HEX/RGB mismatch for {color_id}")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise PaletteContractError(f"missing name for {color_id}")
        colors.append(PaletteColor(color_id, expected_index, name, hex_value, rgb))

    background_raw = raw.get("gameplayBackground")
    if not isinstance(background_raw, dict):
        raise PaletteContractError("gameplayBackground is required")
    background_rgb = _validate_rgb_value(background_raw.get("rgb"))
    background = BackgroundColor(
        id=background_raw.get("id"),
        name=background_raw.get("name"),
        hex=background_raw.get("hex"),
        rgb=background_rgb,
    )
    if background != BackgroundColor("BG01", "Midnight Slate", "#202533", (32, 37, 51)):
        raise PaletteContractError("BG01 must remain the owner-locked presentation background")
    if (
        background_raw.get("pixelArtPaletteColor") is not False
        or background_raw.get("countsTowardLevelColorTotal") is not False
        or background_raw.get("ownerLocked") is not True
    ):
        raise PaletteContractError("BG01 production role must remain presentation-only")
    if background.id in seen_ids:
        raise PaletteContractError("BG01 must not be a logical palette ID")
    return CanonicalPalette(colors, background)


CANONICAL_PALETTE = load_palette()
BG01 = CANONICAL_PALETTE.background
PALETTE = CANONICAL_PALETTE
