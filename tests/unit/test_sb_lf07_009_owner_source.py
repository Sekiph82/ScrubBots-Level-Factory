from __future__ import annotations

import hashlib

from scrubbots_pixel_factory import OwnerSourceRecord, verify_owner_source_immutable


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
