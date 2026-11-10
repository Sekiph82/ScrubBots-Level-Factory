"""P0-B regression: tests can no longer leak synthetic records into the owner's
real data/Release Pool (root cause of the 9 phantom `owner-upload-000..0001..9`
FAILED Batch Issues observed 2026-11-10)."""
from pathlib import Path

import pytest

from scrubbots_pixel_factory import owner_release_library


def test_transition_without_isolated_root_is_refused() -> None:
    real_failed = Path(__file__).resolve().parents[2] / "data" / "Release Pool" / "Failed"
    before = sorted(p.name for p in real_failed.glob("*.json")) if real_failed.exists() else []
    with pytest.raises(RuntimeError, match="real data/Release Pool"):
        owner_release_library.transition(
            "owner-upload-" + format(1, "064x"), "FAILED", source_sha256=format(1, "064x"),
            provider="OWNER_UPLOAD", original_source_path="", reason="guard probe",
        )
    after = sorted(p.name for p in real_failed.glob("*.json")) if real_failed.exists() else []
    assert after == before
