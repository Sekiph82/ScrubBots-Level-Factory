from __future__ import annotations

from scrubbots_pixel_factory.studio_extensions import cost_center


def test_cost_center_separates_units_and_uses_owner_acceptance_denominator() -> None:
    records = [
        {"provider": "Magnific", "unit": "credits", "status": "SUCCESS", "consumed": 10, "remaining": 90, "owner_acceptance": "ACCEPT"},
        {"provider": "Magnific", "unit": "credits", "status": "FAILED", "consumed": 4, "remaining": 86, "owner_acceptance": "REJECT"},
        {"provider": "PixelLab", "unit": "USD", "status": "SUCCESS", "owner_acceptance": "ACCEPT"},
    ]
    view = cost_center(records)
    magnify = next(group for group in view["groups"] if group["provider"] == "Magnific")
    pixellab = next(group for group in view["groups"] if group["provider"] == "PixelLab")
    assert magnify["jobs"] == 2 and magnify["success"] == 1 and magnify["failure"] == 1
    assert magnify["consumed"] == 14 and magnify["cost_per_owner_accepted"] == 14
    assert pixellab["consumed"] is None and pixellab["remaining"] is None
    assert "consumed" in pixellab["unknown"] and "remaining" in pixellab["unknown"]
