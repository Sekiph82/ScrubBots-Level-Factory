from __future__ import annotations

import pytest

from scrubbots_pixel_factory.studio_extensions import StudioExtensionError, extensions_root, record_failure, retry_failure


def test_product_launcher_has_no_caller_created_failure_operation() -> None:
    launcher = (extensions_root().parents[2] / "level_factory" / "scripts" / "factory_core_launcher.py").read_text(encoding="utf-8")
    assert 'operation == "record-failure"' not in launcher


def test_retry_preserves_failure_and_disables_unavailable_stage() -> None:
    failure = record_failure("import-validation", "VALIDATE", "REJECTED", "FOREIGN_COLORS", {"source_id": "owner-upload-test"})
    try:
        with pytest.raises(StudioExtensionError, match="canonical scanner"):
            retry_failure(failure["failure_id"], {"operator_note": "recheck"})
        unavailable = record_failure("pipeline", "SOLVE", "INCONCLUSIVE", "M03 unavailable", {})
        with pytest.raises(StudioExtensionError, match="canonical scanner"):
            retry_failure(unavailable["failure_id"])
    finally:
        for directory in ("failures", "retries"):
            root = extensions_root() / directory
            if root.exists():
                for path in root.glob("*.json"): path.unlink()
