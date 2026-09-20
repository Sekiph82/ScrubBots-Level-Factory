from __future__ import annotations

from scrubbots_pixel_factory.studio_extensions import extensions_root, record_failure, retry_failure


def test_retry_preserves_failure_and_disables_unavailable_stage() -> None:
    failure = record_failure("import-validation", "VALIDATE", "REJECTED", "FOREIGN_COLORS", {"source_id": "owner-upload-test"})
    try:
        retry = retry_failure(failure["failure_id"], {"operator_note": "recheck"})
        assert retry["parent_failure_id"] == failure["failure_id"]
        assert retry["original_inputs"]["source_id"] == "owner-upload-test"
        unavailable = record_failure("pipeline", "SOLVE", "INCONCLUSIVE", "M03 unavailable", {})
        blocked = retry_failure(unavailable["failure_id"])
        assert blocked["disposition"] == "NOT_AVAILABLE"
    finally:
        for directory in ("failures", "retries"):
            root = extensions_root() / directory
            if root.exists():
                for path in root.glob("*.json"): path.unlink()
