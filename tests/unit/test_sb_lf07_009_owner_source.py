from __future__ import annotations

import hashlib
import pytest

from scrubbots_pixel_factory import MutationContractError, OwnerSourceRecord, verify_owner_source_immutable
from scrubbots_pixel_factory.mutation_source import SourceLinkedMutationContext
from scrubbots_pixel_factory.qa import OwnerSourceRecord as M05OwnerSourceRecord


def _record() -> tuple[OwnerSourceRecord, bytes]:
    raw = b"immutable-owner-source-png-bytes"
    return OwnerSourceRecord("source-1", hashlib.sha256(raw).hexdigest(), len(raw), 20, 20, "owner-uploads/source-1/source.png"), raw


def test_valid_candidate_only_mutation_preserves_owner_bytes_length_dimensions_and_identity() -> None:
    record, raw = _record()
    report = verify_owner_source_immutable(record, raw, raw, before_dimensions=(20, 20), after_dimensions=(20, 20), derived_paths=("owner-uploads/source-1/derived-preview.png",))
    assert report.disposition == "PASS"
    assert report.before_sha256 == record.source_sha256 == report.after_sha256


def test_source_byte_mutation_and_dimension_change_fail_closed() -> None:
    record, raw = _record()
    assert verify_owner_source_immutable(record, raw, raw + b"x", before_dimensions=(20, 20), after_dimensions=(20, 20)).disposition == "FAIL"
    assert verify_owner_source_immutable(record, raw, raw, before_dimensions=(20, 20), after_dimensions=(21, 20)).disposition == "FAIL"
    assert verify_owner_source_immutable(record, raw + b"x", raw, before_dimensions=(20, 20), after_dimensions=(20, 20)).disposition == "ERROR"


def test_corrupt_record_and_path_metadata_alias_are_rejected() -> None:
    record, raw = _record()
    corrupt = OwnerSourceRecord("source-1", record.source_sha256, record.byte_length + 1, 20, 20, record.source_path)
    assert verify_owner_source_immutable(corrupt, raw, raw, before_dimensions=(20, 20), after_dimensions=(20, 20)).disposition == "ERROR"
    assert verify_owner_source_immutable(record, raw, raw, derived_paths=("OWNER-UPLOADS/./SOURCE-1/SOURCE.PNG",)).disposition == "ERROR"


def test_repeated_verification_is_idempotent() -> None:
    record, raw = _record()
    first = verify_owner_source_immutable(record, raw, raw, before_dimensions=(20, 20), after_dimensions=(20, 20))
    second = verify_owner_source_immutable(record, raw, raw, before_dimensions=(20, 20), after_dimensions=(20, 20))
    assert first == second


def test_only_m05_owner_upload_record_can_be_adapted_to_source_identity() -> None:
    raw = b"immutable-owner-source-png-bytes"
    record = OwnerSourceRecord.from_m05_owner_upload({
        "source_id": "owner-upload-" + "a" * 64,
        "origin": "OWNER_UPLOAD",
        "status": "SOURCE_ONLY",
        "validation_state": "UNVALIDATED",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "original_width": 20,
        "original_height": 20,
        "immutable_relative_path": "owner-uploads/owner-upload-" + "a" * 64 + "/source.png",
    })
    assert record.source_id.startswith("owner-upload-")
    with pytest.raises(MutationContractError):
        OwnerSourceRecord.from_m05_owner_upload({"source_id": record.source_id, "origin": "SYNTHETIC", "status": "SOURCE_ONLY", "validation_state": "UNVALIDATED"})


def test_source_linked_context_uses_m05_verifier_and_requires_before_after_pass(tmp_path) -> None:
    raw = b"accepted-m05-source"
    source = tmp_path / "source.png"
    source.write_bytes(raw)
    record = M05OwnerSourceRecord("owner-upload-r02", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    context = SourceLinkedMutationContext.establish(record)
    assert context.before.disposition == "PASS"
    checked = context.verify_after()
    assert checked.passed
    with pytest.raises(MutationContractError):
        SourceLinkedMutationContext.establish(_record()[0])  # type: ignore[arg-type]
