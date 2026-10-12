"""Bounded append-only live activity receipts for the Factory Studio UI."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


_RUN_ID = re.compile(r"^pipeline-ui-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}$")
_SOURCE_ID = re.compile(r"^owner-upload-[0-9a-f]{64}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MAX_BYTES = 256 * 1024


class PipelineActivityWriter:
    """Write hash-chained events to one unique file under LF's output directory."""

    def __init__(self, repository_root: Path, run_id: str, source_id: str, source_sha256: str) -> None:
        if not _RUN_ID.fullmatch(run_id) or not _SOURCE_ID.fullmatch(source_id) or not _SHA256.fullmatch(source_sha256):
            raise ValueError("pipeline activity identity is invalid")
        output_root = (repository_root.resolve() / "level_factory" / "output" / "studio-pipeline-activity").resolve()
        output_root.mkdir(parents=True, exist_ok=True)
        self.path = output_root / f"{run_id}.jsonl"
        if self.path.resolve().parent != output_root or self.path.exists():
            raise ValueError("pipeline activity output identity already exists or escaped LF output")
        self.path.touch(exist_ok=False)
        self.run_id = run_id
        self.source_id = source_id
        self.source_sha256 = source_sha256
        self.started_ns = time.monotonic_ns()
        self.sequence = 0
        self.previous_sha256 = "0" * 64
        self.size_bytes = 0
        self.terminal_emitted = False

    def emit(self, stage: str, state: str, message: str, *, backend_disposition: str | None = None) -> None:
        if not re.fullmatch(r"[A-Z][A-Z /_-]{0,47}", stage) or not re.fullmatch(r"[A-Z_]{1,24}", state):
            raise ValueError("pipeline activity stage or state is invalid")
        if stage == "PIPELINE" and self.terminal_emitted:
            raise ValueError("pipeline activity terminal event was already emitted")
        self.sequence += 1
        body: dict[str, Any] = {
            "seq": self.sequence,
            "run_id": self.run_id,
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "stage": stage,
            "state": state,
            "elapsed_ms": max(0, (time.monotonic_ns() - self.started_ns) // 1_000_000),
            "message": str(message)[:240],
            "previous_sha256": self.previous_sha256,
        }
        if backend_disposition is not None:
            body["backend_disposition"] = str(backend_disposition)[:64]
        canonical = json.dumps(body, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        line = json.dumps({"body": body, "body_sha256": digest}, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        if self.size_bytes + len(line) > _MAX_BYTES:
            raise ValueError("pipeline activity log exceeded its 256 KiB bound")
        with self.path.open("ab") as stream:
            stream.write(line)
            stream.flush()
        self.size_bytes += len(line)
        self.previous_sha256 = digest
        if stage == "PIPELINE":
            self.terminal_emitted = True


__all__ = ["PipelineActivityWriter"]
