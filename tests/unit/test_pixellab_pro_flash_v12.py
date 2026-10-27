from __future__ import annotations

import base64
from io import BytesIO

import pytest
from PIL import Image

from scrubbots_pixel_factory import CANONICAL_PALETTE
from scrubbots_pixel_factory.studio_extensions import (
    ProFlashError,
    generate_pro_flash_image,
    validate_pro_flash_png,
)


def _png(colors: list[tuple[int, int, int, int]], size: tuple[int, int] = (20, 20)) -> bytes:
    image = Image.new("RGBA", size)
    image.putdata((colors * ((size[0] * size[1] + len(colors) - 1) // len(colors)))[: size[0] * size[1]])
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_v3_palette_payload_is_exact_and_pro_flash_job_is_polled_without_resubmit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIXELLAB_SECRET", "test-token-never-sent-to-a-real-service")
    colors = [CANONICAL_PALETTE.rgb_for(item) + (255,) for item in ("C01", "C02", "C03")]
    png = _png(colors)
    calls: list[tuple[str, str, dict[str, object] | None]] = []
    clock = [0.0]

    def request_json(url: str, *, secret: str, method: str, payload=None, timeout=30):
        assert secret == "test-token-never-sent-to-a-real-service"
        calls.append((url, method, payload))
        if method == "POST":
            return {"background_job_id": "job-v12"}, {}
        if len([call for call in calls if call[1] == "GET"]) == 1:
            return {"status": "processing"}, {}
        return {
            "status": "completed",
            "last_response": {"images": [{"base64": base64.b64encode(png).decode()}], "source_image_id": "source-v12"},
            "usage": {"type": "generations", "generations": 5},
        }, {}

    result = generate_pro_flash_image(
        description="pixel-art seed collector",
        width=20,
        height=20,
        seed="owner-seed",
        request_json=request_json,
        sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
        monotonic=lambda: clock[0],
    )
    post = calls[0]
    assert post[0].endswith("/v2/create-image-pro-flash")
    assert post[1] == "POST"
    assert post[2] == {
        "description": "pixel-art seed collector",
        "image_size": {"width": 20, "height": 20},
        "no_background": True,
        "seed": result.request_seed,
        "target_palette": {
            "colors": [color.hex.upper() for color in CANONICAL_PALETTE.colors],
            "name": "ScrubBots Palette V3",
            "max_colors": 12,
        },
    }
    assert len([call for call in calls if call[1] == "POST"]) == 1
    assert result.job_id == "job-v12"
    assert result.source_image_id == "source-v12"
    assert result.actual_usage == {"type": "generations", "generations": 5}
    assert result.used_palette_ids == ("C01", "C02", "C03")


@pytest.mark.parametrize(
    ("colors", "expected_code"),
    [
        ([(233, 75, 75, 255), (242, 140, 60, 255), (242, 201, 76, 255)], "FOREIGN_COLOR"),
        ([CANONICAL_PALETTE.rgb_for("C01") + (255,), CANONICAL_PALETTE.rgb_for("C02") + (128,), CANONICAL_PALETTE.rgb_for("C03") + (255,)], "ALPHA_CONTRACT"),
    ],
)
def test_old_palette_and_semitransparent_pixels_fail_closed(colors, expected_code) -> None:
    with pytest.raises(ProFlashError) as error:
        validate_pro_flash_png(_png(colors), expected_width=20, expected_height=20)
    assert error.value.code == expected_code


def test_older_attached_palette_is_not_misidentified_as_scrubbots_v3() -> None:
    older_prompt_palette = [
        "#E94B4B", "#F28C3C", "#F2C94C", "#55B85A", "#63D6A3", "#42C7D9", "#3E7EDB", "#3451A3",
        "#845EC2", "#E66FA5", "#956447", "#E8CFA0", "#B8C2CC", "#3D4652", "#FFFFFF", "#000000",
    ]
    canonical = {color.hex.upper() for color in CANONICAL_PALETTE.colors}
    assert len(older_prompt_palette) == 16
    assert set(older_prompt_palette) != canonical
    with pytest.raises(ProFlashError) as error:
        validate_pro_flash_png(_png([(233, 75, 75, 255), (242, 140, 60, 255), (242, 201, 76, 255)]),
            expected_width=20, expected_height=20)
    assert error.value.code == "FOREIGN_COLOR"


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [(401, "AUTHENTICATION_FAILED"), (402, "INSUFFICIENT_CREDITS"),
     (422, "REQUEST_REJECTED"), (429, "RATE_LIMITED")],
)
def test_provider_http_errors_are_truthful_and_redacted(monkeypatch, status_code, expected_code) -> None:
    from urllib.error import HTTPError
    import scrubbots_pixel_factory.studio_extensions as adapter

    def rejected(*_args, **_kwargs):
        raise HTTPError("https://api.pixellab.ai/v2/create-image-pro-flash", status_code,
            "provider detail", {}, None)

    monkeypatch.setattr(adapter, "urlopen", rejected)
    with pytest.raises(ProFlashError) as error:
        adapter._json_request("https://api.pixellab.ai/v2/create-image-pro-flash",
            secret="never-echo-this-token", method="POST", payload={})
    assert error.value.code == expected_code
    assert "never-echo-this-token" not in str(error.value)


def test_dimension_and_used_color_envelope_fail_closed() -> None:
    rgb = [CANONICAL_PALETTE.rgb_for(color) + (255,) for color in ("C01", "C02", "C03")]
    with pytest.raises(ProFlashError, match="dimensions"):
        validate_pro_flash_png(_png(rgb, (24, 20)), expected_width=20, expected_height=20)
    with pytest.raises(ProFlashError) as error:
        validate_pro_flash_png(_png([CANONICAL_PALETTE.rgb_for("C01") + (255,)]), expected_width=20, expected_height=20)
    assert error.value.code == "USED_COLOR_COUNT"


def test_dimensions_are_four_pixel_steps_and_no_submission_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIXELLAB_SECRET", "test-token")
    calls: list[str] = []

    def request_json(url: str, **kwargs):
        calls.append(kwargs["method"])
        raise ProFlashError("SUBMISSION_UNKNOWN", "submission outcome is unknown")

    with pytest.raises(ProFlashError) as invalid:
        generate_pro_flash_image(description="sprite", width=21, height=20, seed=1, request_json=request_json)
    assert invalid.value.code == "INVALID_DIMENSIONS"
    assert calls == []
    with pytest.raises(ProFlashError) as unknown:
        generate_pro_flash_image(description="sprite", width=20, height=20, seed=1, request_json=request_json)
    assert unknown.value.code == "SUBMISSION_UNKNOWN"
    assert calls == ["POST"]


def test_preferred_api_token_and_mismatched_legacy_secret_fail_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIXELLAB_API_TOKEN", "preferred-token")
    monkeypatch.delenv("PIXELLAB_SECRET", raising=False)
    colors = [CANONICAL_PALETTE.rgb_for(item) + (255,) for item in ("C01", "C02", "C03")]
    png = _png(colors)
    requests: list[str] = []

    def request_json(url: str, *, secret: str, method: str, payload=None, timeout=30):
        assert secret == "preferred-token"
        requests.append(method)
        if method == "POST": return {"background_job_id": "token-job"}, {}
        return {"status": "completed", "last_response": {"image": base64.b64encode(png).decode()}}, {}

    result = generate_pro_flash_image(description="sprite", width=20, height=20, seed=1,
        request_json=request_json, sleep=lambda _seconds: None)
    assert result.job_id == "token-job"
    assert requests.count("POST") == 1

    monkeypatch.setenv("PIXELLAB_SECRET", "different-token")
    requests.clear()
    with pytest.raises(ProFlashError) as conflict:
        generate_pro_flash_image(description="sprite", width=20, height=20, seed=1,
            request_json=lambda *args, **kwargs: requests.append(kwargs["method"]))
    assert conflict.value.code == "CREDENTIALS_CONFLICT"
    assert requests == []


def test_provider_options_retire_magnific_and_csv_rejects_only_its_own_row(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path
    from scrubbots_pixel_factory.alpix_batch import run_csv_job
    from scrubbots_pixel_factory.semantic.providers.registry import active_factory_studio_provider_ids

    assert active_factory_studio_provider_ids() == ("ALPIX (Claude)", "PIXELLAB")
    monkeypatch.setenv("PIXELLAB_API_TOKEN", "configured-test-token")
    monkeypatch.delenv("PIXELLAB_SECRET", raising=False)
    import scrubbots_pixel_factory.alpix_batch as alpix_batch
    monkeypatch.setattr(alpix_batch, "discover_alpix", lambda: {"available": True, "reason": "mock"})
    namespace = {"__name__": "factory_core_launcher_test", "STUDIO_EXTENSION_OPERATION": "scrubbots-factory-studio-extension"}
    launcher_path = Path(__file__).resolve().parents[2] / "level_factory" / "scripts" / "factory_core_launcher.py"
    source = launcher_path.read_text(encoding="utf-8")
    import ast
    tree = ast.parse(source)
    selected = ast.Module(body=[node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {"_provider_options", "_csv_rows_for_retired_provider"}], type_ignores=[])
    exec(compile(selected, str(launcher_path), "exec"), namespace)
    options = namespace["_provider_options"]()
    ids = [item["id"] for item in options["providers"]]
    assert ids == ["ALPIX (Claude)", "PIXELLAB"]
    assert options["providers"][1]["execution_mode"] == "PRO_FLASH"
    assert options["providers"][1]["available"] is True

    source_bytes = b"prompt,width,height,provider\nretired prompt,20,20,MAGNIFIC\nactive prompt,20,20,ALPIX (Claude)\n"
    csv_path = tmp_path / "requests.csv"
    csv_path.write_bytes(source_bytes)
    rendered: list[str] = []

    def renderer(prompt, width, height, destination):
        rendered.append(prompt)
        image = Image.new("RGB", (width, height), CANONICAL_PALETTE.rgb_for("C01"))
        image.save(destination, format="PNG")
        return {"path": str(destination)}

    result = run_csv_job(csv_path, tmp_path / "jobs", renderer=renderer,
        importer=lambda _path: {"source_id": "active-row-source"})
    assert csv_path.read_bytes() == source_bytes
    assert [row["state"] for row in result.rows] == ["PROVIDER_RETIRED", "IMPORTED"]
    assert result.rows[0]["error"] == "PROVIDER_RETIRED_MAGNIFIC"
    assert rendered == ["active prompt"]
    assert result.completed == 1 and result.failed == 1


def test_semantic_generation_dispatches_to_pro_flash_without_fallback() -> None:
    import ast
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
    import factory_core_launcher

    launcher_path = Path(factory_core_launcher.__file__)
    tree = ast.parse(launcher_path.read_text(encoding="utf-8"))
    selected = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_semantic_generate"], type_ignores=[])
    observed: dict[str, object] = {}

    def pro_flash(**kwargs):
        observed.update(kwargs)
        return {"state": "PRO_FLASH_DISPATCHED"}

    namespace = {
        "STUDIO_EXTENSION_OPERATION": "scrubbots-factory-studio-extension",
        "_text": factory_core_launcher._text,
        "_exact_int": factory_core_launcher._exact_int,
        "_semantic_generate_pixellab_pro_flash": pro_flash,
    }
    exec(compile(selected, str(launcher_path), "exec"), namespace)
    result = namespace["_semantic_generate"]({
        "prompt": "moth seed collector", "style": "CREATURE", "provider_id": "PIXELLAB",
        "provider_model": "PRO_FLASH", "width": 32, "height": 32, "seed": "test-seed",
        "background_intent": "TRANSPARENT", "operation_id": "offline-dispatch-check",
    })
    assert result == {"state": "PRO_FLASH_DISPATCHED"}
    assert observed == {
        "prompt": "moth seed collector", "style": "CREATURE", "width": 32, "height": 32,
        "seed": "test-seed", "background": "TRANSPARENT", "operation_id": "offline-dispatch-check",
    }


def test_semantic_generation_rejects_non_32x32_pro_flash_before_dispatch() -> None:
    import ast
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
    import factory_core_launcher

    launcher_path = Path(factory_core_launcher.__file__)
    tree = ast.parse(launcher_path.read_text(encoding="utf-8"))
    selected = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_semantic_generate"], type_ignores=[])
    dispatched: list[dict[str, object]] = []
    namespace = {
        "STUDIO_EXTENSION_OPERATION": "scrubbots-factory-studio-extension",
        "_text": factory_core_launcher._text,
        "_exact_int": factory_core_launcher._exact_int,
        "_semantic_generate_pixellab_pro_flash": lambda **kwargs: dispatched.append(kwargs),
    }
    exec(compile(selected, str(launcher_path), "exec"), namespace)

    with pytest.raises(ValueError, match="fixed at 32x32"):
        namespace["_semantic_generate"]({
            "prompt": "moth seed collector", "style": "CREATURE", "provider_id": "PIXELLAB",
            "provider_model": "PRO_FLASH", "width": 48, "height": 56, "seed": "test-seed",
        })
    assert dispatched == []


def test_dispatch_records_exact_imported_png_and_reuses_operation_without_second_call(tmp_path, monkeypatch) -> None:
    import sys
    from pathlib import Path
    from scrubbots_pixel_factory import studio_extensions as extensions
    from scrubbots_pixel_factory.studio_extensions import ProFlashImageResult

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
    import factory_core_launcher as launcher
    ext_root = tmp_path / "extensions"
    repository = tmp_path / "repository"
    png = _png([CANONICAL_PALETTE.rgb_for(item) + (255,) for item in ("C01", "C02", "C03")])
    calls = []

    def generate(**kwargs):
        calls.append(kwargs)
        return ProFlashImageResult(png, "job-imported-v12", "source-image-v12", {"generations": 5},
            20, 20, ("C01", "C02", "C03"), 17)

    monkeypatch.setattr(extensions, "extensions_root", lambda: ext_root)
    monkeypatch.setattr(extensions, "generate_pro_flash_image", generate)
    monkeypatch.setattr(extensions, "batch_import", lambda _paths: {"items": [{"source_id": "source-imported-v12"}]})
    monkeypatch.setattr(launcher, "_repository_root", lambda: repository)
    kwargs = {"prompt": "one test sprite", "style": "CREATURE", "width": 20, "height": 20,
        "seed": "seed-v12", "background": "TRANSPARENT", "operation_id": "idempotent-v12"}
    first = launcher._semantic_generate_pixellab_pro_flash(**kwargs)
    second = launcher._semantic_generate_pixellab_pro_flash(**kwargs)
    assert first["state"] == "IMPORTED" and first["source_id"] == "source-imported-v12"
    assert first["content_sha256"] == __import__("hashlib").sha256(png).hexdigest()
    assert first["actual_usage"] == {"generations": 5}
    assert second["state"] == "NEEDS_REVIEW"
    assert len(calls) == 1
    record = __import__("json").loads((ext_root / "pixellab-jobs" / "idempotent-v12.json").read_text(encoding="utf-8"))
    assert record["content_sha256"] == first["content_sha256"]
    assert record["palette_enforcement"] == "API_TARGET_PALETTE_V3_AND_LOCAL_EXACT_VALIDATION"


def test_unknown_submission_blocks_identical_new_operation_without_resubmission(tmp_path, monkeypatch) -> None:
    import sys
    from pathlib import Path
    from scrubbots_pixel_factory import studio_extensions as extensions
    from scrubbots_pixel_factory.studio_extensions import ProFlashError

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
    import factory_core_launcher as launcher
    ext_root = tmp_path / "extensions"
    monkeypatch.setattr(extensions, "extensions_root", lambda: ext_root)
    calls = []

    def unknown(**kwargs):
        calls.append(kwargs)
        raise ProFlashError("SUBMISSION_UNKNOWN", "no automatic retry")

    monkeypatch.setattr(extensions, "generate_pro_flash_image", unknown)
    monkeypatch.setattr(launcher, "_repository_root", lambda: tmp_path / "repository")
    base = {"prompt": "same paid request", "style": "CREATURE", "width": 20, "height": 20,
        "seed": "stable-seed", "background": "TRANSPARENT"}
    try:
        launcher._semantic_generate_pixellab_pro_flash(**base, operation_id="first-unknown")
    except ValueError as error:
        assert "SUBMISSION_UNKNOWN" in str(error)
    else:
        raise AssertionError("unknown submission should fail without retry")
    result = launcher._semantic_generate_pixellab_pro_flash(**base, operation_id="second-click")
    assert result["state"] == "NEEDS_REVIEW"
    assert result["operation_id"] == "first-unknown"
    assert len(calls) == 1


def test_pixellab_pixel_art_ui_enforces_fixed_32x32_canvas() -> None:
    from pathlib import Path

    ui_path = Path(__file__).resolve().parents[2] / "level_factory" / "scripts" / "factory_studio_exact_ui.gd"
    source = ui_path.read_text(encoding="utf-8")
    generate = source.split("func _generate_art() -> void:", 1)[1].split("func _confirm_pro_flash_generation()", 1)[0]
    confirmation = source.split("func _confirm_pro_flash_generation() -> void:", 1)[1].split("func _start_pixel_art_worker", 1)[0]
    size_dialog = source.split("func _choose_size() -> void:", 1)[1].split("func _choose_provider()", 1)[0]
    provider_dialog = source.split("func _choose_provider() -> void:", 1)[1].split("func _provider_status_for", 1)[0]

    assert '_provider_model == "PIXELLAB"' in generate
    assert "_width = 32" in generate and "_height = 32" in generate
    assert "_width = 32" in confirmation and "_height = 32" in confirmation
    assert "width_input.value = 32" in size_dialog and "height_input.value = 32" in size_dialog
    assert "width_input.editable = false" in size_dialog and "height_input.editable = false" in size_dialog
    assert '_width = 32 if _provider_model == "PIXELLAB"' in size_dialog
    assert '_height = 32 if _provider_model == "PIXELLAB"' in size_dialog
    assert 'if _provider_model == "PIXELLAB":' in provider_dialog
