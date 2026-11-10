from __future__ import annotations

from pathlib import Path

import pytest

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.studio_extensions import StudioExtensionError, record_failure, retry_failure

REPOSITORY = Path(__file__).resolve().parents[2]


def test_product_launcher_has_no_caller_created_failure_operation() -> None:
    launcher = (REPOSITORY / "level_factory" / "scripts" / "factory_core_launcher.py").read_text(encoding="utf-8")
    assert 'operation == "record-failure"' not in launcher


def test_retry_preserves_failure_and_disables_unavailable_stage(tmp_path: Path, monkeypatch) -> None:
    # Isolated evidence root: the old cleanup deleted every failures/retries
    # JSON in the owner's real Studio Extensions folder.
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: tmp_path / "Studio Extensions")
    failure = record_failure("import-validation", "VALIDATE", "REJECTED", "FOREIGN_COLORS", {"source_id": "owner-upload-test"})
    with pytest.raises(StudioExtensionError, match="canonical scanner"):
        retry_failure(failure["failure_id"], {"operator_note": "recheck"})
    unavailable = record_failure("pipeline", "SOLVE", "INCONCLUSIVE", "M03 unavailable", {})
    with pytest.raises(StudioExtensionError, match="canonical scanner"):
        retry_failure(unavailable["failure_id"])
    assert (tmp_path / "Studio Extensions" / "failures").is_dir()
