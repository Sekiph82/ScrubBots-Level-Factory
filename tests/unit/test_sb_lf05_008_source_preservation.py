from __future__ import annotations

import hashlib

from scrubbots_pixel_factory.qa import OwnerSourceRecord, verify_owner_source_preservation


def test_owner_source_bytes_are_unchanged_and_derived_outputs_are_separate(tmp_path) -> None:
    source = tmp_path / "source.png"
    raw = b"owner-source-bytes"
    source.write_bytes(raw)
    record = OwnerSourceRecord("owner-upload-test", str(source), hashlib.sha256(raw).hexdigest(), len(raw), 20, 20)
    report = verify_owner_source_preservation(record, analysis=lambda: (tmp_path / "derived.json").write_text("derived", encoding="utf-8"), derived_artifact_paths=(str(tmp_path / "derived.json"),))
    assert report.disposition == "PASS"
    assert source.read_bytes() == raw
    assert report.derived_artifact_paths == (str(tmp_path / "derived.json"),)


def test_source_corruption_and_analysis_mutation_fail_closed(tmp_path) -> None:
    source = tmp_path / "source.png"
    raw = b"owner-source-bytes"
    source.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    bad = verify_owner_source_preservation(OwnerSourceRecord("owner-upload-test", str(source), "e" * 64, len(raw), 20, 20))
    assert bad.disposition == "FAIL"
    mutated = verify_owner_source_preservation(OwnerSourceRecord("owner-upload-test", str(source), digest, len(raw), 20, 20), analysis=lambda: source.write_bytes(b"mutated"))
    assert mutated.disposition == "FAIL"
