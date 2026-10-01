from __future__ import annotations

import pytest

from scrubbots_pixel_factory.cli.main import _parser
from scrubbots_pixel_factory.studio_extensions import _validate_generate_preset_settings
from scrubbots_pixel_factory.supply_pipeline.contracts import validate_column_count
from scrubbots_pixel_factory.supply_pipeline.progression import build_progression


@pytest.mark.parametrize("value", [3, 4, 5])
def test_zip_column_contract_is_explicit(value: int) -> None:
    assert validate_column_count(value) == value


@pytest.mark.parametrize("value", [2, 6, True, "3"])
def test_zip_column_contract_rejects_non_product_values(value: object) -> None:
    with pytest.raises(ValueError):
        validate_column_count(value)  # type: ignore[arg-type]


def test_supply_cli_exposes_column_count_and_not_target() -> None:
    parser = _parser()
    parsed = parser.parse_args(["supply-optimize", "--image", "in.png", "--output", "out", "--column-count", "5"])
    assert parsed.column_count == 5
    with pytest.raises(SystemExit):
        parser.parse_args(["supply-optimize", "--image", "in.png", "--output", "out", "--target", "HARD"])


def test_new_generate_preset_settings_have_no_requested_difficulty() -> None:
    settings = _validate_generate_preset_settings({"width": 20, "height": 20, "seed": 7, "mode": "MASK", "background_intent": "BACKGROUND"})
    assert settings == {"width": 20, "height": 20, "seed": 7, "mode": "MASK", "background_intent": "BACKGROUND"}


def test_progression_tie_break_is_immutable_level_id() -> None:
    result = build_progression([
        {"level_id": "level-b", "difficulty_score": 12.0},
        {"level_id": "level-a", "difficulty_score": 12.0},
    ])
    assert [entry["level_id"] for entry in result["levels"]] == ["level-a", "level-b"]
