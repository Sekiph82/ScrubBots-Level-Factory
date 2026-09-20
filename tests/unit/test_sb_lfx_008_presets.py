from __future__ import annotations

from pathlib import Path

import pytest

from scrubbots_pixel_factory.studio_extensions import StudioExtensionError, delete_preset, expand_preset, load_preset, save_preset


def test_presets_expand_full_request_and_history_survives_update_delete() -> None:
    preset_id = "lfx008-test"
    try:
        first = save_preset(preset_id, "First recipe", "Generate", {"difficulty": "EASY", "width": 20, "height": 21, "seed": 7, "mode": "MASK"})
        expanded = expand_preset(preset_id)
        assert expanded["settings"] == first["settings"]
        save_preset(preset_id, "Updated recipe", "Generate", {"difficulty": "HARD", "width": 22, "height": 23, "seed": 9, "mode": "RULES"})
        assert expanded["settings"]["seed"] == 7
        delete_preset(preset_id)
        assert expanded["settings"]["width"] == 20
    finally:
        delete_preset(preset_id)


def test_presets_reject_unsupported_secret_or_truth_fields() -> None:
    with pytest.raises(StudioExtensionError):
        save_preset("lfx008-invalid", "Bad", "Generate", {"api_key": "secret"})
