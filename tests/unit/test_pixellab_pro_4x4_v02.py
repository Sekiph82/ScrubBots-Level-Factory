"""Offline R10 Pro 4x4 request contract tests; request_json is always mocked."""

import base64
from contextlib import contextmanager
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import shutil

import pytest
from PIL import Image, ImageDraw

from scrubbots_pixel_factory import studio_extensions as extensions
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.studio_extensions import ProFlashError, generate_pixellab_pro_4x4_frames


def _frame(width: int = 56, height: int = 56) -> bytes:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    palette = [color.rgb + (255,) for color in CANONICAL_PALETTE.colors[:3]]
    for index, color in enumerate(palette):
        image.paste(color, (index * width // 3, 0, (index + 1) * width // 3, height))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _success(width: int = 56, height: int = 56) -> dict[str, object]:
    frame = base64.b64encode(_frame(width, height)).decode("ascii")
    return {"status": "completed", "last_response": {"images": [{"base64": frame}] * 16}}


def _varied_frame(index: int, width: int = 56, height: int = 56) -> bytes:
    palette = [color.rgb + (255,) for color in CANONICAL_PALETTE.colors[:3]]
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((3, 3, width - 4, height - 4), fill=palette[0])
    draw.rectangle((7, 7, width // 2, height // 2), fill=palette[1])
    draw.rectangle((width // 2 + 2, height // 2 + 2, width - 8, height - 8), fill=palette[2])
    image.putpixel((1 + index % 4, 1 + index // 4), palette[2])
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


@contextmanager
def _runtime_sandbox():
    root = Path(__file__).resolve().parent / ".r10-pixellab-runtime-test-output"
    if root.exists():
        raise AssertionError(f"Refusing pre-existing test output: {root}")
    root.mkdir()
    try:
        yield root
    finally:
        if root.exists():
            if root.resolve().parent != Path(__file__).resolve().parent:
                raise AssertionError("Runtime fixture escaped its exact test-owned directory")
            shutil.rmtree(root)


@pytest.mark.parametrize("width,height", [(51, 51), (52, 56), (56, 59), (59, 51), (59, 59)])
def test_pro_4x4_submits_variable_dimensions_locked_v3_and_adjustable_max_colors(
    width: int, height: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "in-memory-test-credential")
    calls: list[tuple[str, dict[str, object]]] = []

    def request_json(url: str, **kwargs: object):
        calls.append((url, kwargs))
        if kwargs["method"] == "POST":
            return {"background_job_id": "job-r10"}, {}
        return _success(width, height), {}

    accepted: list[str] = []
    result = generate_pixellab_pro_4x4_frames(
        description="offline test sprite", width=width, height=height, max_colors=7, seed=123,
        request_json=request_json, sleep=lambda _: None, on_job_accepted=accepted.append,
    )
    assert len(result.frames_png) == 16
    assert accepted == ["job-r10"]
    assert len([call for call in calls if call[1]["method"] == "POST"]) == 1
    post = next(call[1] for call in calls if call[1]["method"] == "POST")
    assert calls[0][0] == "https://api.pixellab.ai/v2/generate-image-v2"
    assert post["payload"]["image_size"] == {"width": width, "height": height}
    assert post["payload"]["no_background"] is True
    assert post["payload"]["target_palette"]["colors"] == [color.hex.upper() for color in CANONICAL_PALETTE.colors]
    assert post["payload"]["target_palette"]["max_colors"] == 7
    assert post["payload"]["style_options"] == {"color_palette": False}


@pytest.mark.parametrize("width,height", [(50, 56), (60, 56), (56, 60), (64, 64)])
def test_invalid_pro_4x4_dimensions_reject_before_credential_or_request(
    width: int, height: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: pytest.fail("credential lookup must not run"))
    calls: list[object] = []
    with pytest.raises(ProFlashError, match="GAME_DIMENSIONS_OUT_OF_RANGE|PRO_4X4_FRAME_COUNT_INCOMPATIBLE"):
        generate_pixellab_pro_4x4_frames(
            description="no-spend invalid size", width=width, height=height, seed=1,
            request_json=lambda *args, **kwargs: calls.append(args),
        )
    assert calls == []


@pytest.mark.parametrize("max_colors", [2, 13])
def test_max_colors_out_of_range_rejects_before_credential_or_request(
    max_colors: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: pytest.fail("credential lookup must not run"))
    with pytest.raises(ProFlashError, match="MAX_COLORS_OUT_OF_RANGE"):
        generate_pixellab_pro_4x4_frames(
            description="no-spend invalid colors", width=56, height=56, max_colors=max_colors, seed=1,
            request_json=lambda *args, **kwargs: pytest.fail("network adapter must not run"),
        )


def test_poll_retries_only_safe_job_lookup_and_never_reposts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "in-memory-test-credential")
    calls: list[str] = []
    accepted: list[str] = []

    def request_json(url: str, **kwargs: object):
        calls.append(str(kwargs["method"]))
        if kwargs["method"] == "POST":
            return {"background_job_id": "durable-job"}, {}
        if calls.count("GET") == 1:
            raise ProFlashError("POLL_NETWORK_ERROR", "offline")
        return _success(), {}

    result = generate_pixellab_pro_4x4_frames(
        description="poll only", width=56, height=56, seed=5,
        request_json=request_json, sleep=lambda _: None, on_job_accepted=accepted.append,
    )
    assert result.job_id == "durable-job"
    assert accepted == ["durable-job"]
    assert calls.count("POST") == 1
    assert calls.count("GET") == 2


def test_incompatible_frame_count_fails_closed_after_one_post(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "in-memory-test-credential")
    calls: list[str] = []
    frame = base64.b64encode(_frame()).decode("ascii")

    def request_json(url: str, **kwargs: object):
        calls.append(str(kwargs["method"]))
        if kwargs["method"] == "POST":
            return {"background_job_id": "short-job"}, {}
        return {"status": "completed", "last_response": {"images": [{"base64": frame}] * 15}}, {}

    with pytest.raises(ProFlashError, match="PRO_4X4_FRAME_COUNT_INCOMPATIBLE"):
        generate_pixellab_pro_4x4_frames(
            description="short result", width=56, height=56, seed=7,
            request_json=request_json, sleep=lambda _: None,
        )
    assert calls.count("POST") == 1
    assert calls.count("GET") == 1


def test_factory_imports_only_pass_frames_as_source_only_and_reuses_job_id(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root / "level_factory" / "scripts"))
    import factory_core_launcher as launcher
    from scrubbots_pixel_factory.studio_extensions import PixelLabPro4x4Result

    with _runtime_sandbox() as sandbox:
        fake_repo = sandbox / "repo"
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        originals = tuple(_varied_frame(index) for index in range(16))
        submissions: list[dict[str, object]] = []
        imported: list[Path] = []

        def generate(**kwargs: object) -> PixelLabPro4x4Result:
            submissions.append(kwargs)
            accepted = kwargs.get("on_job_accepted")
            if callable(accepted):
                accepted("mock-job-r10")
            return PixelLabPro4x4Result(originals, "mock-job-r10", None, 56, 56, 12, 123)

        def batch_import(paths: list[str]) -> dict[str, object]:
            imported_path = Path(paths[0])
            imported.append(imported_path)
            return {"items": [{"disposition": "IMPORTED", "source_id": f"source-{len(imported):02d}"}]}

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", generate)
        monkeypatch.setattr(extensions, "batch_import", batch_import)
        first = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="offline source test", style="CREATURE", width=56, height=56,
            max_colors=12, seed="fixture-seed", operation_id="r10-offline-id",
        )
        second = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="offline source test", style="CREATURE", width=56, height=56,
            max_colors=12, seed="fixture-seed", operation_id="r10-offline-id",
        )
        assert first["state"] == "SOURCES_IMPORTED_NOT_READY"
        assert first["pass_count"] == 16 and first["rejected_count"] == 0
        assert len(first["frame_statuses"]) == 16
        assert all(frame["import_status"] == "IMPORTED" for frame in first["frame_statuses"])
        assert len(first["source_ids"]) == len(imported) == 16
        assert all(path.name.startswith("sprite-") for path in imported)
        assert second["state"] == "NEEDS_REVIEW"
        assert len(submissions) == 1
        record = __import__("json").loads(
            (extensions_root / "pixellab-jobs" / "r10-offline-id.json").read_text(encoding="utf-8")
        )
        assert record["state"] == "SOURCES_IMPORTED_NOT_READY"
        assert "SOURCE_ONLY" in record["quality_scope"]

        atlas_image = Image.new("RGBA", (224, 224), (0, 0, 0, 0))
        for index, raw in enumerate(originals):
            frame = Image.open(BytesIO(raw)).convert("RGBA")
            atlas_image.paste(frame, ((index % 4) * 56, (index // 4) * 56))
        source_atlas = sandbox / "selected-owner-atlas.png"
        atlas_image.save(source_atlas, format="PNG")
        original_sha = sha256(source_atlas.read_bytes()).hexdigest()
        imported_result = launcher._semantic_import_pixellab_pro_4x4(
            {"path": str(source_atlas), "max_colors": 7}
        )
        assert imported_result["state"] == "SOURCES_IMPORTED_NOT_READY"
        assert imported_result["source_kind"] == "IMPORTED_ATLAS"
        assert len(imported_result["frame_statuses"]) == 16
        assert len(imported_result["source_ids"]) == 16
        assert sha256(source_atlas.read_bytes()).hexdigest() == original_sha
        assert all(status["intake_status"] == "PASS" for status in imported_result["frame_statuses"])
        assert all(status["import_status"] == "IMPORTED" for status in imported_result["frame_statuses"])
