"""Offline R10 Pro 4x4 request contract tests; request_json is always mocked."""

import base64
import csv
from contextlib import contextmanager
from hashlib import sha256
from io import BytesIO
import json
import multiprocessing
from pathlib import Path
import shutil
import sys

import pytest
from PIL import Image, ImageDraw

from scrubbots_pixel_factory import studio_extensions as extensions
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.studio_extensions import PixelLabProviderError, generate_pixellab_pro_4x4_frames


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


def _independent_claim_worker(repository_root: str, claim_path: str, barrier, outcomes) -> None:
    scripts = str(Path(repository_root) / "level_factory" / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import factory_core_launcher as launcher

    barrier.wait(timeout=10)
    won = launcher._create_exclusive_json(
        Path(claim_path), {"operation_id": multiprocessing.current_process().name}
    )
    if won:
        outcomes.put("PSEUDO_POST")
    else:
        outcomes.put("BLOCKED")


def _launcher_module():
    repository_root = Path(__file__).resolve().parents[2]
    scripts = str(repository_root / "level_factory" / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import factory_core_launcher

    return factory_core_launcher


def _runtime_root() -> Path:
    # A fresh temp directory per test: the old fixed tests/unit/.r10-... path made
    # every later run fail after one interrupted run left it behind.
    import tempfile

    return Path(tempfile.mkdtemp(prefix="r10-pixellab-runtime-"))


@contextmanager
def _runtime_sandbox():
    from scrubbots_pixel_factory import owner_art_storage

    root = _runtime_root()
    (root / "repo").mkdir()
    # archive_pixellab_export resolves the owner-art root itself; without this
    # the fixtures exported synthetic atlases into the owner's real PixelLab Final.
    original_root = owner_art_storage.factory_repository_root
    owner_art_storage.factory_repository_root = lambda *_args, **_kwargs: root / "repo"
    try:
        yield root
    finally:
        owner_art_storage.factory_repository_root = original_root
        shutil.rmtree(root, ignore_errors=True)


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
    assert result.http_request_count == len(calls) == 2
    assert accepted == ["job-r10"]
    assert len([call for call in calls if call[1]["method"] == "POST"]) == 1
    post = next(call[1] for call in calls if call[1]["method"] == "POST")
    assert calls[0][0] == "https://api.pixellab.ai/v2/generate-image-v2"
    assert post["payload"]["image_size"] == {"width": width, "height": height}
    assert post["payload"]["no_background"] is True
    assert post["payload"]["target_palette"]["colors"] == [color.hex.upper() for color in CANONICAL_PALETTE.colors]
    assert post["payload"]["target_palette"]["max_colors"] == 7
    assert post["payload"]["style_options"] == {"color_palette": False}


def test_semantic_dispatch_preserves_csv_prompt_verbatim_when_style_is_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    launcher = _launcher_module()
    observed: dict[str, object] = {}

    def dispatch(**kwargs: object) -> dict[str, object]:
        observed.update(kwargs)
        return {"state": "DISPATCHED"}

    monkeypatch.setattr(launcher, "_semantic_generate_pixellab_pro_4x4", dispatch)
    prompt = "CSV prompt with C01 #FF4500 and fixed sprite details."
    result = launcher._semantic_generate({
        "prompt": prompt, "style": "", "provider_id": "PIXELLAB", "provider_model": "PRO_4X4",
        "width": 56, "height": 56, "max_colors": 12, "seed": 20261105,
        "background_intent": "TRANSPARENT", "operation_id": "csv-prompt-style-empty",
    })

    assert result == {"state": "DISPATCHED"}
    assert observed["prompt"] == prompt
    assert observed["style"] == ""


@pytest.mark.parametrize("width,height", [(50, 56), (60, 56), (56, 60), (64, 64)])
def test_invalid_pro_4x4_dimensions_reject_before_credential_or_request(
    width: int, height: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: pytest.fail("credential lookup must not run"))
    calls: list[object] = []
    with pytest.raises(PixelLabProviderError, match="GAME_DIMENSIONS_OUT_OF_RANGE|PRO_4X4_FRAME_COUNT_INCOMPATIBLE"):
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
    with pytest.raises(PixelLabProviderError, match="MAX_COLORS_OUT_OF_RANGE"):
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
            raise PixelLabProviderError("POLL_NETWORK_ERROR", "offline")
        return _success(), {}

    result = generate_pixellab_pro_4x4_frames(
        description="poll only", width=56, height=56, seed=5,
        request_json=request_json, sleep=lambda _: None, on_job_accepted=accepted.append,
    )
    assert result.job_id == "durable-job"
    assert accepted == ["durable-job"]
    assert calls.count("POST") == 1
    assert calls.count("GET") == 2


def test_http_request_budget_caps_one_generation_and_returns_persistable_job_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "in-memory-test-credential")
    calls: list[str] = []

    def request_json(_url: str, **kwargs: object):
        calls.append(str(kwargs["method"]))
        if kwargs["method"] == "POST":
            return {"background_job_id": "budget-job"}, {}
        return {"status": "processing"}, {}

    request_counts: list[int] = []
    with pytest.raises(PixelLabProviderError, match="HTTP_REQUEST_BUDGET_EXHAUSTED") as caught:
        generate_pixellab_pro_4x4_frames(
            description="bounded fake request test", width=56, height=56, seed=9,
            request_json=request_json, sleep=lambda _: None, max_http_requests=2,
            on_http_request_started=request_counts.append,
        )

    assert calls == ["POST", "GET"]
    assert request_counts == [1, 2]
    assert caught.value.job_id == "budget-job"
    assert caught.value.http_request_count == 2


def test_http_request_budget_rejects_values_above_owner_authorized_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: pytest.fail("credential lookup must not run"))
    with pytest.raises(PixelLabProviderError, match="INVALID_HTTP_REQUEST_BUDGET"):
        generate_pixellab_pro_4x4_frames(
            description="no-spend invalid budget", width=56, height=56, seed=10,
            max_http_requests=11, request_json=lambda *_args, **_kwargs: pytest.fail("provider call must not run"),
        )


def test_http_400_detail_is_bounded_and_api_token_is_redacted(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    token = "secret-test-token"
    monkeypatch.setattr(
        extensions,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError("https://api.pixellab.ai/v2/generate-image-v2", 400, "Bad Request",
                      {"x-request-id": "req_abc-123"},
                      BytesIO(json.dumps({"detail": f"Rejected {token}. Please update request."}).encode()))
        ),
    )
    with pytest.raises(PixelLabProviderError) as caught:
        extensions._json_request("https://api.pixellab.ai/v2/generate-image-v2", secret=token, method="POST", payload={})

    assert "HTTP_ERROR" in caught.value.code
    assert "Please update request." in str(caught.value)
    assert token not in str(caught.value)
    assert caught.value.provider_request_id == "req_abc-123"
    assert caught.value.http_status == 400


@pytest.mark.parametrize("request_id", ["has whitespace", "line\nbreak", "x" * 129, "secret/test?value"])
def test_unsafe_provider_request_ids_are_not_retained(request_id: str, monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    monkeypatch.setattr(
        extensions,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError("https://api.pixellab.ai/v2/generate-image-v2", 400, "Bad Request",
                      {"X-Request-ID": request_id}, BytesIO(b"{}"))
        ),
    )
    with pytest.raises(PixelLabProviderError) as caught:
        extensions._json_request(
            "https://api.pixellab.ai/v2/generate-image-v2", secret="test-token", method="POST", payload={}
        )

    assert caught.value.provider_request_id is None


def test_http_400_validation_errors_keep_field_and_reason_without_echoing_input(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    token = "secret-test-token"
    body = {"detail": [{"loc": ["body", "target_palette"], "msg": "invalid palette", "input": token}]}
    monkeypatch.setattr(
        extensions,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError("https://api.pixellab.ai/v2/generate-image-v2", 400, "Bad Request", {}, BytesIO(json.dumps(body).encode()))
        ),
    )
    with pytest.raises(PixelLabProviderError) as caught:
        extensions._json_request("https://api.pixellab.ai/v2/generate-image-v2", secret=token, method="POST", payload={})

    assert "Provider detail: body.target_palette: invalid palette" in str(caught.value)
    assert token not in str(caught.value)
    assert "input" not in str(caught.value)


def test_http_400_nested_provider_errors_keep_safe_message_and_redact_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    token = "secret-test-token"
    body = {"error": {"code": "INVALID_PALETTE", "message": f"Palette configuration rejected; {token}", "input": "private-prompt"}}
    monkeypatch.setattr(
        extensions,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError("https://api.pixellab.ai/v2/generate-image-v2", 400, "Bad Request", {}, BytesIO(json.dumps(body).encode()))
        ),
    )
    with pytest.raises(PixelLabProviderError) as caught:
        extensions._json_request("https://api.pixellab.ai/v2/generate-image-v2", secret=token, method="POST", payload={})

    assert "Provider detail: INVALID_PALETTE; Palette configuration rejected; [redacted]" in str(caught.value)
    assert "private-prompt" not in str(caught.value)
    assert token not in str(caught.value)


def test_incompatible_frame_count_fails_closed_after_one_post(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "in-memory-test-credential")
    calls: list[str] = []
    frame = base64.b64encode(_frame()).decode("ascii")

    def request_json(url: str, **kwargs: object):
        calls.append(str(kwargs["method"]))
        if kwargs["method"] == "POST":
            return {"background_job_id": "short-job"}, {}
        return {"status": "completed", "last_response": {"images": [{"base64": frame}] * 15}}, {}

    with pytest.raises(PixelLabProviderError, match="PRO_4X4_FRAME_COUNT_INCOMPATIBLE"):
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
    launcher = _launcher_module()
    from scrubbots_pixel_factory.studio_extensions import PixelLabPro4x4Result

    with _runtime_sandbox() as sandbox:
        fake_repo = sandbox / "repo"
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": True, "status": "READY_CREDENTIALS_CONFIGURED", "reason": "offline fixture"
        })
        originals = tuple(_varied_frame(index) for index in range(16))
        submissions: list[dict[str, object]] = []
        imported: list[Path] = []

        def generate(**kwargs: object) -> PixelLabPro4x4Result:
            submissions.append(kwargs)
            started = kwargs.get("on_submission_started")
            if callable(started):
                started()
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
        # Sources are imported from their unique Final names, never staging sprite-NN.
        assert all(path.parent.name == "Final" and path.name.startswith("LF-") for path in imported)
        assert len({path.name for path in imported}) == 16
        assert second["state"] == "NEEDS_OWNER_REVIEW_IDENTICAL_REQUEST"
        assert len(submissions) == 1
        record = __import__("json").loads(
            (extensions_root / "pixellab-jobs" / "r10-offline-id.json").read_text(encoding="utf-8")
        )
        assert record["state"] == "SOURCES_IMPORTED_NOT_READY"
        assert record["paid_submission_possible"] is True
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


def test_factory_import_never_submits_rejected_atlas_slices(monkeypatch: pytest.MonkeyPatch) -> None:
    launcher = _launcher_module()
    imported_paths: list[Path] = []
    with _runtime_sandbox() as sandbox:
        fake_repo = sandbox / "repo"
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)

        def batch_import(paths: list[str]) -> dict[str, object]:
            imported_paths.append(Path(paths[0]))
            return {"items": [{"disposition": "IMPORTED", "source_id": f"accepted-{len(imported_paths)}"}]}

        monkeypatch.setattr(extensions, "batch_import", batch_import)
        atlas_image = Image.new("RGBA", (224, 224), (0, 0, 0, 0))
        for index in range(16):
            frame = Image.open(BytesIO(_varied_frame(index))).convert("RGBA")
            if index == 6:
                frame.putpixel((10, 10), (17, 19, 23, 255))
            atlas_image.paste(frame, ((index % 4) * 56, (index // 4) * 56))
        source_atlas = sandbox / "one-rejected-slice.png"
        atlas_image.save(source_atlas, format="PNG")

        result = launcher._semantic_import_pixellab_pro_4x4(
            {"path": str(source_atlas), "max_colors": 7}
        )

        rejected = result["frame_statuses"][6]
        assert result["state"] == "SOURCES_IMPORTED_NOT_READY"
        assert result["pass_count"] == 15
        assert result["rejected_count"] == 1
        assert rejected["intake_status"] == "REJECTED"
        assert "FOREIGN_COLORS" in rejected["reasons"]
        assert rejected["import_status"] == "NOT_IMPORTED"
        assert len(imported_paths) == 15
        assert all(path.parent.name == "Final" and path.name.startswith("LF-") for path in imported_paths)
        assert len({path.name for path in imported_paths}) == 15


@pytest.mark.parametrize(
    ("prior_state", "job_id"),
    [
        ("POLLING", "accepted-job"),
        ("NORMALIZING", "accepted-job"),
        ("POST_SUBMISSION_ERROR", "accepted-job"),
        ("SUBMISSION_UNKNOWN", None),
        ("SUBMITTING", None),
        ("POLL_TIMEOUT", "accepted-job"),
        ("SUCCEEDED", "accepted-job"),
        ("FAILED_AFTER_POST", "accepted-job"),
    ],
)
def test_cross_operation_digest_claim_blocks_every_paid_or_uncertain_state(
    prior_state: str, job_id: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    launcher = _launcher_module()
    from scrubbots_pixel_factory.studio_extensions import PixelLabPro4x4Result

    repository_root = Path(__file__).resolve().parents[2]
    with _runtime_sandbox() as sandbox:
        fake_repo = sandbox / "repo"
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": True, "status": "READY_CREDENTIALS_CONFIGURED", "reason": "offline fixture"
        })
        submissions: list[dict[str, object]] = []

        def generate(**kwargs: object) -> PixelLabPro4x4Result:
            submissions.append(kwargs)
            started = kwargs.get("on_submission_started")
            if callable(started):
                started()
            accepted = kwargs.get("on_job_accepted")
            if callable(accepted):
                accepted("accepted-job")
            return PixelLabPro4x4Result(
                tuple(_varied_frame(index) for index in range(16)), "accepted-job", None,
                56, 56, 12, 123,
            )

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", generate)
        monkeypatch.setattr(
            extensions, "batch_import",
            lambda paths: {"items": [{"disposition": "IMPORTED", "source_id": f"source-{Path(paths[0]).name}"}]},
        )
        first = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="same paid intent", style="CREATURE", width=56, height=56,
            max_colors=12, seed="fixed-seed", operation_id="first-operation",
        )
        assert first["state"] == "SOURCES_IMPORTED_NOT_READY"
        jobs_root = extensions_root / "pixellab-jobs"
        first_record = json.loads((jobs_root / "first-operation.json").read_text(encoding="utf-8"))
        claim_path = jobs_root / f"{first_record['request_sha256']}.claim.json"
        prior = {**first_record, "state": prior_state, "paid_submission_possible": True}
        if job_id:
            prior["job_id"] = job_id
        else:
            prior.pop("job_id", None)
        claim_path.write_text(json.dumps(prior), encoding="utf-8")
        (jobs_root / "first-operation.json").write_text(json.dumps(prior), encoding="utf-8")

        second = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="same paid intent", style="CREATURE", width=56, height=56,
            max_colors=12, seed="fixed-seed", operation_id="different-operation",
        )
        assert second["state"] == (
            "NEEDS_OWNER_REVIEW_ACCEPTED_JOB" if job_id else "NEEDS_OWNER_REVIEW_UNKNOWN_SUBMISSION"
        )
        assert len(submissions) == 1


def test_digest_claim_is_atomic_between_independent_worker_processes() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    context = multiprocessing.get_context("spawn")
    with _runtime_sandbox() as sandbox:
        claim_path = sandbox / "shared-digest.claim.json"
        barrier = context.Barrier(2)
        outcomes = context.Queue()
        workers = [
            context.Process(
                target=_independent_claim_worker,
                args=(str(repository_root), str(claim_path), barrier, outcomes),
            )
            for _ in range(2)
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=20)
        assert all(not worker.is_alive() and worker.exitcode == 0 for worker in workers)
        results = [outcomes.get(timeout=2) for _ in workers]
        assert results.count("PSEUDO_POST") == 1
        assert results.count("BLOCKED") == 1
        assert json.loads(claim_path.read_text(encoding="utf-8"))["operation_id"]


def test_corrupt_or_stale_claim_is_not_reclaimed_or_overwritten(monkeypatch: pytest.MonkeyPatch) -> None:
    launcher = _launcher_module()
    from scrubbots_pixel_factory.studio_extensions import PixelLabPro4x4Result

    root = _runtime_root()
    sandbox_repo = root / "repo"
    extensions_root = root / "extensions"
    sandbox_repo.mkdir()
    from scrubbots_pixel_factory import owner_art_storage

    monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda *_args, **_kwargs: sandbox_repo)
    try:
        monkeypatch.setattr(launcher, "_repository_root", lambda: sandbox_repo)
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": True, "status": "READY_CREDENTIALS_CONFIGURED", "reason": "offline fixture"
        })
        submissions: list[dict[str, object]] = []

        def generate(**kwargs: object) -> PixelLabPro4x4Result:
            submissions.append(kwargs)
            started = kwargs.get("on_submission_started")
            if callable(started):
                started()
            accepted = kwargs.get("on_job_accepted")
            if callable(accepted):
                accepted("stale-job")
            return PixelLabPro4x4Result(
                tuple(_varied_frame(index) for index in range(16)), "stale-job", None,
                56, 56, 12, 123,
            )

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", generate)
        monkeypatch.setattr(extensions, "batch_import", lambda _: {"items": []})
        launcher._semantic_generate_pixellab_pro_4x4(
            prompt="stale claim", style="CREATURE", width=56, height=56,
            max_colors=12, seed="stale-seed", operation_id="stale-first",
        )
        jobs_root = extensions_root / "pixellab-jobs"
        record = json.loads((jobs_root / "stale-first.json").read_text(encoding="utf-8"))
        claim_path = jobs_root / f"{record['request_sha256']}.claim.json"
        claim_path.write_text("{broken", encoding="utf-8")
        original_claim = claim_path.read_bytes()
        outcome = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="stale claim", style="CREATURE", width=56, height=56,
            max_colors=12, seed="stale-seed", operation_id="stale-second",
        )
        assert outcome["state"] == "NEEDS_OWNER_REVIEW_UNKNOWN_SUBMISSION"
        assert len(submissions) == 1
        assert claim_path.read_bytes() == original_claim
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_legacy_v02_digest_remains_guarded_before_creating_new_claim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _launcher_module()
    from scrubbots_pixel_factory.contracts.palette import PALETTE_DATA_PATH

    with _runtime_sandbox() as sandbox:
        fake_repo = sandbox / "repo"
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        description = "Legacy prompt. Pixel art style: CREATURE."
        palette_sha256 = sha256(PALETTE_DATA_PATH.read_bytes()).hexdigest()
        legacy_digest = sha256(json.dumps({
            "provider": "PIXELLAB", "model": "PRO_4X4", "adapter_version": "pixellab-pro-4x4-v1",
            "api_version": "v2", "palette_sha256": palette_sha256, "description": description,
            "width": 56, "height": 56, "max_colors": 12, "seed": "legacy-seed",
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        jobs_root = extensions_root / "pixellab-jobs"
        jobs_root.mkdir(parents=True)
        (jobs_root / "old-v02-operation.json").write_text(json.dumps({
            "operation_id": "old-v02-operation", "request_sha256": legacy_digest,
            "state": "POLLING", "job_id": "old-provider-job",
        }), encoding="utf-8")
        submissions: list[object] = []
        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", lambda **kwargs: submissions.append(kwargs))

        outcome = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="Legacy prompt", style="CREATURE", width=56, height=56,
            max_colors=12, seed="legacy-seed", operation_id="new-operation",
        )
        assert outcome["state"] == "NEEDS_OWNER_REVIEW_ACCEPTED_JOB"
        assert outcome["job_id"] == "old-provider-job"
        assert submissions == []
        assert not list(jobs_root.glob("*.claim.json"))


def test_missing_credential_creates_no_claim_then_same_intent_can_submit_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _launcher_module()
    from scrubbots_pixel_factory.studio_extensions import PixelLabPro4x4Result

    with _runtime_sandbox() as sandbox:
        fake_repo = sandbox / "repo"
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: fake_repo)
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        status = {"configured": False, "status": "PIXELLAB_API_TOKEN_NOT_CONFIGURED",
                  "reason": "PIXELLAB_API_TOKEN_NOT_CONFIGURED: no local credential."}
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: dict(status))
        submissions: list[dict[str, object]] = []

        def generate(**kwargs: object) -> PixelLabPro4x4Result:
            submissions.append(kwargs)
            started = kwargs.get("on_submission_started")
            if callable(started):
                started()
            accepted = kwargs.get("on_job_accepted")
            if callable(accepted):
                accepted("mock-first-use-job")
            return PixelLabPro4x4Result(
                tuple(_varied_frame(index) for index in range(16)),
                "mock-first-use-job", None, 56, 56, 12, 123,
            )

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", generate)
        monkeypatch.setattr(
            extensions, "batch_import",
            lambda paths: {"items": [{"disposition": "IMPORTED", "source_id": "offline-source-1"}]},
        )
        first = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="same normalized first use", style="CREATURE", width=56, height=56,
            max_colors=12, seed="same-seed", operation_id="first-use-operation",
        )
        assert first["state"] == "PIXELLAB_API_TOKEN_NOT_CONFIGURED"
        assert first["paid_submission_possible"] is False
        assert first["job_record_created"] is False
        assert first["digest_claim_created"] is False
        assert submissions == []
        assert not extensions_root.exists()

        status.update({"configured": True, "status": "READY_CREDENTIALS_CONFIGURED",
                       "reason": "PixelLab credential is present (in-memory test only)."})
        second = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="same normalized first use", style="CREATURE", width=56, height=56,
            max_colors=12, seed="same-seed", operation_id="first-use-operation",
        )
        assert second["state"] == "SOURCES_IMPORTED_NOT_READY"
        assert len(submissions) == 1
        jobs_root = extensions_root / "pixellab-jobs"
        record = json.loads((jobs_root / "first-use-operation.json").read_text(encoding="utf-8"))
        claim = json.loads(next(jobs_root.glob("*.claim.json")).read_text(encoding="utf-8"))
        assert record["paid_submission_possible"] is True
        assert claim["paid_submission_possible"] is True
        assert "mock credential value" not in json.dumps(record)


def test_credential_conflict_returns_without_creating_claim_or_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _launcher_module()
    with _runtime_sandbox() as sandbox:
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: sandbox / "repo")
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": False, "status": "PIXELLAB_CREDENTIALS_CONFLICT",
            "reason": "PIXELLAB_CREDENTIALS_CONFLICT: environment entries differ.",
        })
        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames",
                            lambda **kwargs: pytest.fail("provider adapter must not run"))
        result = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="credential conflict", style="CREATURE", width=56, height=56,
            max_colors=12, seed="conflict-seed", operation_id="conflict-operation",
        )
        assert result["state"] == "PIXELLAB_CREDENTIALS_CONFLICT"
        assert result["digest_claim_created"] is False
        assert not extensions_root.exists()


def test_existing_known_unpaid_claim_stays_fail_closed_without_auto_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _launcher_module()

    with _runtime_sandbox() as sandbox:
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: sandbox / "repo")
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": True, "status": "READY_CREDENTIALS_CONFIGURED", "reason": "mock only"})

        def fail_before_post(**kwargs: object):
            raise PixelLabProviderError("CREDENTIALS_NOT_CONFIGURED", "synthetic pre-submit failure")

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", fail_before_post)
        with pytest.raises(ValueError, match="CREDENTIALS_NOT_CONFIGURED"):
            launcher._semantic_generate_pixellab_pro_4x4(
                prompt="preserve old unpaid intent", style="CREATURE", width=56, height=56,
                max_colors=12, seed="old-unpaid-seed", operation_id="old-unpaid-operation",
            )
        jobs_root = extensions_root / "pixellab-jobs"
        record_path = jobs_root / "old-unpaid-operation.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record["state"] == "PRE_SUBMISSION_ERROR"
        assert record["paid_submission_possible"] is False
        claim_path = next(jobs_root.glob("*.claim.json"))
        before_claim = claim_path.read_bytes()
        before_record = record_path.read_bytes()
        outcome = launcher._semantic_generate_pixellab_pro_4x4(
            prompt="preserve old unpaid intent", style="CREATURE", width=56, height=56,
            max_colors=12, seed="old-unpaid-seed", operation_id="new-owner-intent",
        )
        assert outcome["state"] == "NEEDS_OWNER_REVIEW_ACTIVE_OR_STALE_CLAIM"
        assert claim_path.read_bytes() == before_claim
        assert record_path.read_bytes() == before_record


def test_provider_request_id_is_persisted_with_safe_paid_failure_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _launcher_module()
    with _runtime_sandbox() as sandbox:
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: sandbox / "repo")
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": True, "status": "READY_CREDENTIALS_CONFIGURED", "reason": "offline fixture"
        })

        def rejected_submission(**kwargs: object) -> None:
            started = kwargs.get("on_submission_started")
            if callable(started):
                started()
            raise PixelLabProviderError(
                "HTTP_ERROR", "PixelLab returned HTTP 400.", http_request_count=1,
                provider_request_id="req_support_123",
            )

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", rejected_submission)
        with pytest.raises(ValueError, match="Provider request ID: req_support_123"):
            launcher._semantic_generate_pixellab_pro_4x4(
                prompt="safe test prompt", style="CREATURE", width=56, height=56,
                max_colors=12, seed=123, operation_id="provider-request-id-operation",
            )

        record_path = extensions_root / "pixellab-jobs" / "provider-request-id-operation.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record["state"] == "HTTP_ERROR"
        assert record["paid_submission_possible"] is True
        assert record["provider_http_request_count"] == 1
        assert record["provider_request_id"] == "req_support_123"
        assert "safe test prompt" not in json.dumps(record)


def test_explicit_http_400_failure_can_be_retried_in_a_later_user_intent(monkeypatch: pytest.MonkeyPatch) -> None:
    launcher = _launcher_module()
    with _runtime_sandbox() as sandbox:
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: sandbox / "repo")
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": True, "status": "READY_CREDENTIALS_CONFIGURED", "reason": "offline fixture"
        })
        calls: list[str] = []

        def rejected_submission(**kwargs: object) -> None:
            calls.append("POST")
            started = kwargs.get("on_submission_started")
            if callable(started):
                started()
            count = kwargs.get("on_http_request_started")
            if callable(count):
                count(1)
            raise PixelLabProviderError(
                "HTTP_ERROR", "PixelLab returned HTTP 400.", http_request_count=1, http_status=400
            )

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", rejected_submission)
        common = {
            "prompt": "offline test prompt", "style": "", "width": 56, "height": 56,
            "max_colors": 12, "seed": 777,
        }
        for operation_id in ("known-http-400-first", "known-http-400-retry"):
            with pytest.raises(ValueError, match="HTTP_ERROR"):
                launcher._semantic_generate_pixellab_pro_4x4(**common, operation_id=operation_id)

        jobs_root = extensions_root / "pixellab-jobs"
        records = [json.loads(path.read_text(encoding="utf-8")) for path in jobs_root.glob("*.json")
                   if not path.name.endswith(".claim.json")]
        assert calls == ["POST", "POST"]
        assert len(records) == 2
        assert all(record["provider_http_status"] == 400 for record in records)
        assert all(record["state"] == "HTTP_ERROR" for record in records)
        assert len(list(jobs_root.glob("*.claim.json"))) == 2


def test_ambiguous_matching_record_remains_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    launcher = _launcher_module()
    with _runtime_sandbox() as sandbox:
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(launcher, "_repository_root", lambda: sandbox / "repo")
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        monkeypatch.setattr(extensions, "pixellab_secret_status", lambda: {
            "configured": True, "status": "READY_CREDENTIALS_CONFIGURED", "reason": "offline fixture"
        })
        called: list[bool] = []

        def unknown_submission(**kwargs: object) -> None:
            called.append(True)
            started = kwargs.get("on_submission_started")
            if callable(started):
                started()
            raise PixelLabProviderError(
                "SUBMISSION_UNKNOWN", "submission outcome unknown", http_request_count=1
            )

        monkeypatch.setattr(extensions, "generate_pixellab_pro_4x4_frames", unknown_submission)
        params = {"prompt": "ambiguous offline prompt", "style": "", "width": 56,
                  "height": 56, "max_colors": 12, "seed": 778}
        with pytest.raises(ValueError, match="SUBMISSION_UNKNOWN"):
            launcher._semantic_generate_pixellab_pro_4x4(**params, operation_id="ambiguous-first")
        blocked = launcher._semantic_generate_pixellab_pro_4x4(**params, operation_id="ambiguous-retry")

        assert called == [True]
        assert blocked["state"] == "NEEDS_OWNER_REVIEW_UNKNOWN_SUBMISSION"


def test_csv_resume_retries_only_explicit_unaccepted_http_400_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    launcher = _launcher_module()
    csv_path = Path(__file__).resolve().parents[2] / "data" / "input" / "scrubbots_2000_prompts.csv"
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = [row for row in csv.reader(file) if row and any(cell.strip() for cell in row)]
    header = [cell.strip().lower() for cell in rows[0]]
    prompt_column = header.index("prompt") if "prompt" in header else header.index("description")
    row = rows[1]
    prompt = row[prompt_column].strip()
    identity = row[0].strip()
    description_sha256 = sha256(prompt.encode("utf-8")).hexdigest()
    seed = extensions._resolved_seed(extensions._resolved_seed(f"sb-lfx018-csv:{identity}:{description_sha256}"))

    class FakeExtensions:
        @staticmethod
        def extensions_root() -> Path:
            return extensions_root

        @staticmethod
        def _resolved_seed(value: str | int) -> int:
            return extensions._resolved_seed(value)

    with _runtime_sandbox() as sandbox:
        extensions_root = sandbox / "extensions"
        ledger = extensions_root / "pixellab-jobs"
        ledger.mkdir(parents=True)
        common_record = {
            "schema": "scrubbots-pixellab-pro-4x4-job-v1", "provider_id": "PIXELLAB",
            "provider_model": "PRO_4X4", "description_sha256": description_sha256,
            "seed": seed, "width": 56, "height": 56, "max_colors": 12,
            "created_at_utc": "2026-11-06T07:45:34+00:00", "paid_submission_possible": True,
            "job_id": None,
        }
        (ledger / "rejected.json").write_text(json.dumps({
            **common_record, "operation_id": "rejected", "state": "HTTP_ERROR",
            "error_code": "HTTP_ERROR", "error": "PixelLab returned HTTP 400.",
            "provider_http_status": 400,
        }), encoding="utf-8")
        request = {
            "csv_path": str(csv_path), "source_sha256": sha256(csv_path.read_bytes()).hexdigest(),
            "width": 56, "height": 56, "max_colors": 12,
        }
        rejected_only = launcher._inspect_pixellab_batch(request, FakeExtensions)
        assert rejected_only["monthly_paid_requests"] == 0
        assert rejected_only["rows"][0]["disposition"] == "RETRY_ELIGIBLE"

        (ledger / "ambiguous.json").write_text(json.dumps({
            **common_record, "operation_id": "ambiguous", "state": "SUBMISSION_UNKNOWN",
            "error_code": "SUBMISSION_UNKNOWN", "error": "submission outcome unknown",
        }), encoding="utf-8")
        with_ambiguous = launcher._inspect_pixellab_batch(request, FakeExtensions)
        assert with_ambiguous["monthly_paid_requests"] == 1
        assert with_ambiguous["rows"][0]["disposition"] == "ALREADY_ATTEMPTED"


def test_batch_preflight_seed_matches_paid_submission_normalization() -> None:
    launcher = _launcher_module()
    csv_seed = "sb-lfx018-csv:storm-moth:example-prompt-hash"
    expected = extensions._resolved_seed(extensions._resolved_seed(csv_seed))

    assert launcher._resolved_pixellab_batch_seed(csv_seed, extensions) == expected
    assert launcher._resolved_pixellab_batch_seed(csv_seed, extensions) != extensions._resolved_seed(csv_seed)


def test_submission_marker_is_persisted_before_single_post(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "in-memory-test-credential")
    events: list[str] = []

    def started() -> None:
        events.append("DURABLE_MARKER")

    def request_json(url: str, **kwargs: object):
        events.append(str(kwargs["method"]))
        if kwargs["method"] == "POST":
            return {"background_job_id": "marker-job"}, {}
        return _success(), {}

    result = generate_pixellab_pro_4x4_frames(
        description="marker order", width=56, height=56, seed=1,
        request_json=request_json, sleep=lambda _: None,
        on_submission_started=started,
    )
    assert result.job_id == "marker-job"
    assert events[0:2] == ["DURABLE_MARKER", "POST"]
    assert events.count("POST") == 1


def test_explicit_recovery_requires_consent_and_uses_get_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "in-memory-test-credential")
    calls: list[str] = []

    def request_json(url: str, **kwargs: object):
        calls.append(str(kwargs["method"]))
        if len(calls) == 1:
            return {"status": "processing"}, {}
        return {"status": "completed", "last_response": {"images": []}}, {}

    with pytest.raises(PixelLabProviderError, match="NETWORK_CONSENT_REQUIRED"):
        extensions.reconcile_pixellab_pro_4x4_job(
            "persisted-job", request_json=request_json, sleep=lambda _: None,
        )
    assert calls == []
    recovered = extensions.reconcile_pixellab_pro_4x4_job(
        "persisted-job", network_consent=True, request_json=request_json,
        sleep=lambda _: None, max_wait_seconds=5, poll_seconds=1,
    )
    assert recovered["state"] == "COMPLETED"
    assert recovered["job_id"] == "persisted-job"
    assert calls == ["GET", "GET"]


def test_launcher_reconcile_uses_persisted_job_only_and_stores_get_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _launcher_module()
    with _runtime_sandbox() as sandbox:
        extensions_root = sandbox / "extensions"
        monkeypatch.setattr(extensions, "extensions_root", lambda: extensions_root)
        jobs_root = extensions_root / "pixellab-jobs"
        jobs_root.mkdir(parents=True)
        record_path = jobs_root / "recover-me.json"
        launcher._write_durable_json(record_path, {
            "operation_id": "recover-me", "request_sha256": "a" * 64,
            "provider_id": "PIXELLAB", "provider_model": "PRO_4X4",
            "state": "POLL_TIMEOUT", "paid_submission_possible": True,
            "job_id": "persisted-job",
        })
        calls: list[str] = []

        def reconcile(job_id: str, *, network_consent: bool):
            calls.append(job_id)
            assert network_consent is True
            return {"job_id": job_id, "state": "COMPLETED", "provider_status": {"status": "completed"}}

        monkeypatch.setattr(extensions, "reconcile_pixellab_pro_4x4_job", reconcile)
        with pytest.raises(ValueError, match="NETWORK_CONSENT_REQUIRED"):
            launcher._semantic_reconcile_pixellab_pro_4x4({"operation_id": "recover-me"})
        assert calls == []
        result = launcher._semantic_reconcile_pixellab_pro_4x4({
            "operation_id": "recover-me", "network_consent": True,
        })
        assert result["network_method"] == "GET"
        assert result["provider_state"] == "COMPLETED"
        assert result["job_id"] == "persisted-job"
        assert calls == ["persisted-job"]
        stored = json.loads(record_path.read_text(encoding="utf-8"))
        assert stored["last_reconciliation_state"] == "COMPLETED"
        assert stored["paid_submission_possible"] is True
