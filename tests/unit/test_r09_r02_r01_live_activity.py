from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scrubbots_pixel_factory import studio_extensions


SOURCE_SHA = "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
SOURCE_ID = f"owner-upload-{SOURCE_SHA}"
RUN_ID = "pipeline-ui-20261012T170355Z-97fdc47b8773"


class RecordingActivityWriter:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.events: list[dict[str, object]] = []
        self.terminal_emitted = False

    def emit(self, stage: str, state: str, message: str, *, backend_disposition: str | None = None) -> None:
        body: dict[str, object] = {"stage": stage, "state": state, "message": message}
        if backend_disposition is not None:
            body["backend_disposition"] = backend_disposition
        self.events.append(body)
        if stage == "PIPELINE":
            self.terminal_emitted = True


def _validation() -> dict[str, object]:
    return {
        "source_sha256": SOURCE_SHA,
        "record_path": "level_factory/output/owner-uploads/source.json",
        "evidence_path": "level_factory/output/studio-extensions/validation/void-unavailable.json",
        "exact_logical_source": False,
        "structural": {
            "disposition": "UNAVAILABLE",
            "reason": "SCRUBBOTS_PROJECT is not configured for current-game authority.",
        },
    }


def _run(*, writer_factory: object, validate: object) -> tuple[dict[str, object], RecordingActivityWriter | None]:
    writers: list[RecordingActivityWriter] = []

    def build_writer(*args: object, **kwargs: object) -> RecordingActivityWriter:
        writer = writer_factory(*args, **kwargs)  # type: ignore[operator]
        if isinstance(writer, RecordingActivityWriter):
            writers.append(writer)
        return writer

    validation_patch = (
        patch.object(studio_extensions, "validate_owner_source", side_effect=validate)
        if callable(validate)
        else patch.object(studio_extensions, "validate_owner_source", return_value=validate)
    )
    with (
        patch.object(studio_extensions, "verify_owner_source", return_value={"source_sha256": SOURCE_SHA}),
        validation_patch,
        patch.object(studio_extensions, "_pipeline_path", return_value=Path("unwritten-pipeline.json")),
        patch.object(studio_extensions, "_write_json", return_value=None),
        patch.object(studio_extensions, "_run_canonical_artwork_route", side_effect=AssertionError("native/canonical solve route must not run in these UI tests")),
        patch("scrubbots_pixel_factory.pipeline_activity.PipelineActivityWriter", side_effect=build_writer),
    ):
        result = studio_extensions.run_pipeline(
            source_id=SOURCE_ID,
            request={
                "activity_run_id": RUN_ID,
                "activity_source_sha256": SOURCE_SHA,
                "game_project": "",
                "column_count": 4,
            },
        )
    return result, writers[0] if writers else None


def test_unavailable_source_gets_truthful_single_terminal_event_without_solver() -> None:
    result, writer = _run(writer_factory=RecordingActivityWriter, validate=_validation())

    assert result["disposition"] == "UNAVAILABLE"
    assert writer is not None
    terminals = [event for event in writer.events if event["stage"] == "PIPELINE"]
    assert len(terminals) == 1
    assert terminals[0]["state"] == "UNAVAILABLE"
    assert terminals[0]["backend_disposition"] == "UNAVAILABLE"
    assert "SCRUBBOTS_PROJECT is not configured" in str(terminals[0]["message"])
    assert [event["stage"] for event in writer.events] == [
        "SOURCE",
        "SOURCE",
        "NORMALIZE/DERIVE",
        "VOID VALIDATION",
        "PIPELINE",
    ]


def test_handled_backend_exception_emits_exactly_one_error_terminal() -> None:
    def explode(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise RuntimeError("validation transport failed")

    result, writer = _run(writer_factory=RecordingActivityWriter, validate=explode)

    assert result["disposition"] == "ERROR"
    assert result["activity_transport"] == "TERMINAL_EMITTED"
    assert writer is not None
    terminals = [event for event in writer.events if event["stage"] == "PIPELINE"]
    assert len(terminals) == 1
    assert terminals[0]["state"] == "ERROR"
    assert terminals[0]["backend_disposition"] == "ERROR"
    assert "validation transport failed" in str(terminals[0]["message"])


def test_writer_initialization_failure_returns_structured_transport_error() -> None:
    def fail_writer(*_args: object, **_kwargs: object) -> RecordingActivityWriter:
        raise OSError("activity output is unavailable")

    result, writer = _run(writer_factory=fail_writer, validate=_validation())

    assert writer is None
    assert result["disposition"] == "ERROR"
    assert result["activity_transport"] == "UNAVAILABLE"
    assert "activity output is unavailable" in str(result["error"])
