from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory.pipeline_activity import PipelineActivityWriter, _MAX_BYTES


def test_activity_events_are_bounded_ordered_and_sha256_chained_without_files(monkeypatch):
    captured = io.BytesIO()

    class MemoryAppend:
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def write(self, value): return captured.write(value)
        def flush(self): return None

    def open_memory(_path, mode):
        assert mode == "ab"
        captured.seek(0, io.SEEK_END)
        return MemoryAppend()

    monkeypatch.setattr(Path, "open", open_memory)
    writer = object.__new__(PipelineActivityWriter)
    writer.path = Path("activity.jsonl")
    writer.run_id = "pipeline-ui-20261012T121314Z-0123456789ab"
    writer.source_id = "owner-upload-" + "a" * 64
    writer.source_sha256 = "a" * 64
    writer.started_ns = 100
    writer.sequence = 0
    writer.previous_sha256 = "0" * 64
    writer.size_bytes = 0

    writer.emit("SOURCE", "PASS", "source verified")
    writer.emit("PIPELINE", "READY", "backend completed")
    lines = captured.getvalue().decode("utf-8").splitlines()
    assert len(lines) == 2
    previous = "0" * 64
    for sequence, line in enumerate(lines, 1):
        envelope = json.loads(line)
        body = envelope["body"]
        digest = hashlib.sha256(json.dumps(body, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        assert envelope["body_sha256"] == digest
        assert body["seq"] == sequence
        assert body["previous_sha256"] == previous
        assert body["run_id"] == writer.run_id
        assert body["source_id"] == writer.source_id
        assert body["source_sha256"] == writer.source_sha256
        previous = digest

    writer.size_bytes = _MAX_BYTES
    with pytest.raises(ValueError, match="256 KiB"):
        writer.emit("QA", "PASS", "too large")
