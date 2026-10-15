"""Synthetic ART_FIRST source binding, exact-grid and fail-closed controls."""

from __future__ import annotations

import hashlib
from io import BytesIO
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from scrubbots_pixel_factory.core import DeterministicRNG, GenerationRequest, GenerationResult
from scrubbots_pixel_factory.core.rng import RNG_ALGORITHM
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
cli_module = importlib.import_module("scrubbots_pixel_factory.cli.main")
import scrubbots_pixel_factory.generators.router.art_first as art_first
from scrubbots_pixel_factory.generators.router.art_first import _check_mask_constraints
from scrubbots_pixel_factory.output.bundle import OutputContractError, export_candidate, read_bundle
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.quality import logical_grid_hash
from scrubbots_pixel_factory import owner_upload, studio_extensions


def _json_bytes(value: object, *, newline: bool = False) -> bytes:
    text = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    return (text + "\n" if newline else text).encode("utf-8")


def _review_record(candidate_id: str, artwork_sha: str, grid_hash: str, disposition: str, sequence: int, previous: str | None) -> dict[str, object]:
    identity = hashlib.sha256(_json_bytes({"candidate_id": candidate_id, "grid_hash": grid_hash}, newline=True)).hexdigest()
    return {
        "schema": "scrubbots-owner-review-evidence",
        "version": 1,
        "review_id": f"review-{candidate_id}-{sequence:04d}",
        "candidate_id": candidate_id,
        "candidate_identity_hash": identity,
        "artwork_sha256": artwork_sha,
        "grid_hash": grid_hash,
        "disposition": disposition,
        "reason": "synthetic binding test only",
        "note": "does not establish real owner authority",
        "sequence": sequence,
        "created_at": "2026-10-15T00:00:00+00:00",
        "previous_review_id": previous,
    }


def _source_record(source_id: str, source_sha: str, raw: bytes, width: int, height: int) -> dict[str, object]:
    return {
        "schema": "scrubbots-owner-upload-source",
        "version": 1,
        "source_id": source_id,
        "origin": "OWNER_UPLOAD",
        "source_sha256": source_sha,
        "byte_length": len(raw),
        "media_type": "image/png",
        "original_filename": "synthetic-art-first.png",
        "original_width": width,
        "original_height": height,
        "immutable_relative_path": f"owner-uploads/{source_id}/source.png",
        "source_record_relative_path": f"owner-uploads/{source_id}/source.json",
        "status": "SOURCE_ONLY",
        "validation_state": "UNVALIDATED",
    }


def _fixture(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, width: int = 20, height: int = 20, color_count: int = 3, review_disposition: str = "ACCEPT"):
    art_first_module = importlib.import_module("scrubbots_pixel_factory.generators.router.art_first")
    owner_root = tmp_path / "level_factory" / "output" / "owner-uploads"
    extensions_root = tmp_path / "level_factory" / "output" / "studio-extensions"
    derived_root = tmp_path / "level_factory" / "output" / "studio-derived-candidates"
    monkeypatch.setattr(art_first_module, "owner_upload_root", lambda: owner_root)
    monkeypatch.setattr(art_first_module, "extensions_root", lambda: extensions_root)
    monkeypatch.setattr(studio_extensions, "owner_upload_root", lambda: owner_root)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: owner_root)

    colors = tuple(f"C{index:02d}" for index in range(1, color_count + 1))
    cells = tuple(colors[index % color_count] for index in range(width * height))
    raw_png = encode_logical_png(width, height, cells)
    source_sha = hashlib.sha256(raw_png).hexdigest()
    source_id = f"owner-upload-{source_sha}"
    source_dir = owner_root / source_id
    source_dir.mkdir(parents=True)
    source_record = _source_record(source_id, source_sha, raw_png, width, height)
    source_record_bytes = _json_bytes(source_record, newline=True)
    (source_dir / "source.png").write_bytes(raw_png)
    (source_dir / "source.json").write_bytes(source_record_bytes)
    source_record_sha = hashlib.sha256(source_record_bytes).hexdigest()

    candidate_id = f"candidate-owner-{source_sha[:48]}"
    source_record_path = (source_dir / "source.json").resolve()
    try:
        source_record_ref = source_record_path.relative_to(Path(__file__).resolve().parents[2]).as_posix()
    except ValueError:
        source_record_ref = str(source_record_path)
    mask_request = GenerationRequest(seed=source_sha, width=width, height=height, generator_mode="MASK")
    rng = DeterministicRNG(source_sha)
    source_result = GenerationResult.success(
        request=mask_request,
        width=width,
        height=height,
        logical_grid=cells,
        generator_id="owner-upload-canonical-derive",
        generator_version="1",
        generator_mode="MASK",
        seed=source_sha,
        rng_algorithm=RNG_ALGORITHM,
        provenance={"stage_seeds": rng.stage_seeds()},
    )
    lineage = {
        "source_id": source_id,
        "source_sha256": source_sha,
        "source_record": source_record_ref,
        "source_bytes_unchanged": True,
        "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
    }
    from scrubbots_pixel_factory.output.bundle import export_result

    candidate_path = export_result(
        source_result,
        candidate_id,
        derived_root,
        generator_metadata={"namespace": "owner-upload", "data": {"source_lineage": lineage}},
    )
    source_bundle = read_bundle(candidate_path)
    first_review = _review_record(
        candidate_id,
        hashlib.sha256(source_bundle.artwork_png).hexdigest(),
        source_bundle.artwork.grid_hash,
        review_disposition,
        1,
        None,
    )
    review_root = extensions_root / "owner-review"
    review_root.mkdir(parents=True)
    (review_root / f"{first_review['review_id']}.json").write_bytes(_json_bytes(first_review, newline=True))
    values: dict[str, object] = {
        "source_id": source_id,
        "source_sha256": source_sha,
        "source_record_sha256": source_record_sha,
        "candidate_id": candidate_id,
        "review_id": first_review["review_id"],
    }
    request = GenerationRequest(
        seed="art-first-fixed-seed",
        width=width,
        height=height,
        generator_mode="ART_FIRST",
        generator_options={"namespace": "art-first", "version": 1, "values": values},
    )
    return {
        "owner_root": owner_root,
        "extensions_root": extensions_root,
        "derived_root": derived_root,
        "source_dir": source_dir,
        "source_id": source_id,
        "source_sha": source_sha,
        "source_record_sha": source_record_sha,
        "candidate_id": candidate_id,
        "review_id": first_review["review_id"],
        "review_root": review_root,
        "review_record": first_review,
        "request": request,
        "cells": cells,
        "width": width,
        "height": height,
    }


def _run(request: GenerationRequest):
    router_module = importlib.import_module("scrubbots_pixel_factory.generators.router.router")
    return router_module.GeneratorRouter().generate_candidate(request)


def _is_art_first_candidate(candidate: object) -> bool:
    router_module = importlib.import_module("scrubbots_pixel_factory.generators.router.router")
    return isinstance(candidate, router_module.ArtFirstCandidate)


@pytest.mark.parametrize(("width", "height", "color_count"), [(20, 59, 3), (38, 24, 5)])
def test_art_first_copies_approved_logical_source_exactly_without_resampling(monkeypatch, tmp_path, width, height, color_count):
    fixture = _fixture(monkeypatch, tmp_path, width, height, color_count)
    candidate = _run(fixture["request"])
    assert _is_art_first_candidate(candidate)
    assert candidate.result.logical_grid == fixture["cells"]
    assert (candidate.result.width, candidate.result.height) == (width, height)
    assert candidate.metadata["source_role"] == "VERIFIED_IMPORTED_ORIGIN_UNVERIFIED"
    assert candidate.metadata["upstream_creator_identity"] == "UNAVAILABLE"
    assert candidate.metadata["output_classification"] == "TEST/PREVIEW"
    assert candidate.metadata["production_candidate_created"] is False
    assert logical_grid_hash(width, height, candidate.result.logical_grid) == candidate.metadata["source_grid_hash"]


def test_art_first_replay_and_bundle_read_revalidate_current_acceptance(monkeypatch, tmp_path):
    fixture = _fixture(monkeypatch, tmp_path)
    first = _run(fixture["request"])
    replay = _run(fixture["request"])
    assert _is_art_first_candidate(first) and _is_art_first_candidate(replay)
    assert first.result.digest() == replay.result.digest()
    assert dict(first.metadata) == dict(replay.metadata)
    output = export_candidate(first, f"candidate-{fixture['request'].digest()}", tmp_path / "preview-output")
    exported = read_bundle(output)
    assert exported.artwork.cells == fixture["cells"]
    assert exported.metadata["generator_metadata"]["classification"]["candidate_class"] == "TEST"
    monkeypatch.setattr(
        cli_module,
        "_router",
        lambda _registry: importlib.import_module("scrubbots_pixel_factory.generators.router.router").GeneratorRouter(),
    )
    assert cli_module.main(["reproduce", str(output / "metadata.json")]) == 0

    review = fixture["review_record"]
    rejected = _review_record(
        fixture["candidate_id"], review["artwork_sha256"], review["grid_hash"], "REJECT", 2, fixture["review_id"],
    )
    (fixture["review_root"] / f"{rejected['review_id']}.json").write_bytes(_json_bytes(rejected, newline=True))
    with pytest.raises(OutputContractError, match="STALE_REVIEW|current review"):
        read_bundle(output)


def test_art_first_needs_current_owner_accept_and_rejects_review_mismatch(monkeypatch, tmp_path):
    fixture = _fixture(monkeypatch, tmp_path, review_disposition="REJECT")
    rejected = _run(fixture["request"])
    assert rejected.is_success is False
    assert "UNAVAILABLE/OWNER_REJECTED" in rejected.failure_reason

    fixture = _fixture(monkeypatch, tmp_path / "second")
    values = dict(fixture["request"].options.values)
    values["review_id"] = f"review-{fixture['candidate_id']}-0002"
    stale = GenerationRequest(
        seed="art-first-fixed-seed", width=fixture["width"], height=fixture["height"], generator_mode="ART_FIRST",
        generator_options={"namespace": "art-first", "version": 1, "values": values},
    )
    result = _run(stale)
    assert result.is_success is False
    assert "STALE_REVIEW" in result.failure_reason


def test_art_first_fails_closed_for_ai_unregistered_sources_and_source_byte_drift(monkeypatch, tmp_path):
    fixture = _fixture(monkeypatch, tmp_path)
    values = dict(fixture["request"].options.values)
    values["source_id"] = "semantic-ai-art-without-registered-review"
    values["source_sha256"] = "0" * 64
    unavailable = GenerationRequest(
        seed="art-first-fixed-seed", width=20, height=20, generator_mode="ART_FIRST",
        generator_options={"namespace": "art-first", "version": 1, "values": values},
    )
    result = _run(unavailable)
    assert result.is_success is False
    assert "UNAVAILABLE" in result.failure_reason

    fixture["source_dir"].joinpath("source.png").write_bytes(b"changed immutable source bytes")
    drifted = _run(fixture["request"])
    assert drifted.is_success is False
    assert "source" in drifted.failure_reason.lower()


def test_art_first_fails_closed_for_missing_file_record_hash_drift_and_path_input(monkeypatch, tmp_path):
    fixture = _fixture(monkeypatch, tmp_path)
    source_record_path = fixture["source_dir"] / "source.json"
    source_record_path.write_bytes(b"tampered source record")
    changed_record = _run(fixture["request"])
    assert changed_record.is_success is False
    assert "record" in changed_record.failure_reason.lower()

    fixture = _fixture(monkeypatch, tmp_path / "missing")
    (fixture["source_dir"] / "source.png").unlink()
    missing = _run(fixture["request"])
    assert missing.is_success is False
    assert "missing" in missing.failure_reason.lower()

    values = dict(fixture["request"].options.values)
    values["source_id"] = "../outside.png"
    traversal = GenerationRequest(
        seed="art-first-fixed-seed", width=20, height=20, generator_mode="ART_FIRST",
        generator_options={"namespace": "art-first", "version": 1, "values": values},
    )
    path_input = _run(traversal)
    assert path_input.is_success is False
    assert "identity" in path_input.failure_reason.lower()


@pytest.mark.parametrize("invalid_pixel", ["foreign-color", "semi-alpha"])
def test_art_first_rejects_foreign_and_semi_alpha_png_pixels(monkeypatch, tmp_path, invalid_pixel):
    fixture = _fixture(monkeypatch, tmp_path)
    rgba = [(*CANONICAL_PALETTE.rgb_for(f"C{index % 3 + 1:02d}"), 255) for index in range(20 * 20)]
    if invalid_pixel == "foreign-color":
        rgba[0] = (1, 2, 3, 255)
    else:
        rgba[0] = (*CANONICAL_PALETTE.rgb_for("C01"), 128)
    image = Image.new("RGBA", (20, 20))
    image.putdata(rgba)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    raw = buffer.getvalue()
    source_sha = hashlib.sha256(raw).hexdigest()
    source_id = f"owner-upload-{source_sha}"
    source_dir = fixture["owner_root"] / source_id
    source_dir.mkdir()
    record_bytes = _json_bytes(_source_record(source_id, source_sha, raw, 20, 20), newline=True)
    (source_dir / "source.png").write_bytes(raw)
    (source_dir / "source.json").write_bytes(record_bytes)
    request = GenerationRequest(
        seed="art-first-invalid-pixel", width=20, height=20, generator_mode="ART_FIRST",
        generator_options={"namespace": "art-first", "version": 1, "values": {
            "source_id": source_id,
            "source_sha256": source_sha,
            "source_record_sha256": hashlib.sha256(record_bytes).hexdigest(),
            "candidate_id": f"candidate-owner-{source_sha[:48]}",
            "review_id": f"review-candidate-owner-{source_sha[:48]}-0001",
        }},
    )
    result = _run(request)
    assert result.is_success is False
    assert "foreign or semi-alpha" in result.failure_reason


def test_owner_upload_root_rejects_reparse_component_without_reading_source(monkeypatch):
    repository = owner_upload._repository_root()
    output_root = repository / "level_factory" / "output"
    original_check = owner_upload._path_is_reparse_point

    def mark_output_as_reparse(path: Path) -> bool:
        return path == output_root or original_check(path)

    monkeypatch.setattr(owner_upload, "_path_is_reparse_point", mark_output_as_reparse)
    with pytest.raises(owner_upload.OwnerUploadError, match="reparse point"):
        owner_upload.owner_upload_root()


def test_art_first_rejects_junctioned_owner_source_directory_before_file_reads(monkeypatch):
    source_sha = "c" * 64
    source_id = f"owner-upload-{source_sha}"
    source_dir = owner_upload.owner_upload_root() / source_id
    original_reparse_check = art_first._path_is_reparse_point
    original_is_dir = Path.is_dir

    def mark_source_dir_as_junction(path: Path) -> bool:
        return path == source_dir or original_reparse_check(path)

    def mark_source_dir_as_existing(path: Path) -> bool:
        return True if path == source_dir else original_is_dir(path)

    monkeypatch.setattr(art_first, "_path_is_reparse_point", mark_source_dir_as_junction)
    monkeypatch.setattr(Path, "is_dir", mark_source_dir_as_existing)
    with pytest.raises(art_first.ArtFirstUnavailable, match="source directory.*reparse point"):
        art_first._load_source(source_id, source_sha, "d" * 64)


def test_art_first_rejects_junctioned_candidate_store_before_file_reads(monkeypatch):
    source_sha = "e" * 64
    candidate_id = f"candidate-owner-{source_sha[:48]}"
    candidate_store = owner_upload.owner_upload_root().parent / "studio-derived-candidates"
    original_reparse_check = art_first._path_is_reparse_point

    def mark_candidate_store_as_junction(path: Path) -> bool:
        return path == candidate_store or original_reparse_check(path)

    monkeypatch.setattr(art_first, "_path_is_reparse_point", mark_candidate_store_as_junction)
    with pytest.raises(art_first.ArtFirstUnavailable, match="candidate store.*reparse point"):
        art_first._candidate_and_review(
            {"source_sha256": source_sha},
            "f" * 64,
            f"owner-upload-{source_sha}",
            candidate_id,
            f"review-{candidate_id}-0001",
        )


def test_art_first_rejects_junctioned_candidate_directory_before_file_reads(monkeypatch):
    source_sha = "a" * 64
    candidate_id = f"candidate-owner-{source_sha[:48]}"
    candidate_store = owner_upload.owner_upload_root().parent / "studio-derived-candidates"
    candidate_dir = candidate_store / candidate_id
    original_reparse_check = art_first._path_is_reparse_point
    original_is_dir = Path.is_dir

    def mark_candidate_dir_as_junction(path: Path) -> bool:
        return path == candidate_dir or original_reparse_check(path)

    def mark_candidate_dir_as_existing(path: Path) -> bool:
        return True if path == candidate_dir else original_is_dir(path)

    monkeypatch.setattr(art_first, "_path_is_reparse_point", mark_candidate_dir_as_junction)
    monkeypatch.setattr(Path, "is_dir", mark_candidate_dir_as_existing)
    with pytest.raises(art_first.ArtFirstUnavailable, match="candidate directory.*reparse point"):
        art_first._candidate_and_review(
            {"source_sha256": source_sha},
            "b" * 64,
            f"owner-upload-{source_sha}",
            candidate_id,
            f"review-{candidate_id}-0001",
        )


def test_art_first_safe_file_rejects_resolved_escape_before_read(monkeypatch):
    path = Path(__file__).resolve()
    root = path.parent
    escaped = root.parent / "outside-art-first-test.py"
    original_resolve = Path.resolve

    def resolve_path(candidate: Path, strict: bool = False) -> Path:
        return escaped if candidate == path else original_resolve(candidate, strict=strict)

    monkeypatch.setattr(Path, "resolve", resolve_path)
    monkeypatch.setattr(Path, "read_bytes", lambda *_args, **_kwargs: pytest.fail("escaped file must not be read"))
    with pytest.raises(art_first.ArtFirstUnavailable, match="escaped its canonical source directory"):
        art_first._safe_file(path, root, 1024, "synthetic path")


def test_art_first_rejects_symlinked_source_and_bad_logical_dimensions(monkeypatch, tmp_path):
    fixture = _fixture(monkeypatch, tmp_path)
    png_path = fixture["source_dir"] / "source.png"
    original_is_symlink = Path.is_symlink

    def is_symlink(path: Path) -> bool:
        # Windows may deny creating a real symlink without elevated privilege;
        # this synthetic marker exercises the production fail-closed branch.
        return path == png_path or original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", is_symlink)
    symlink_result = _run(fixture["request"])
    assert symlink_result.is_success is False
    assert "symlink" in symlink_result.failure_reason.lower()

    owner_root = tmp_path / "bad-dimensions" / "level_factory" / "output" / "owner-uploads"
    art_first_module = importlib.import_module("scrubbots_pixel_factory.generators.router.art_first")
    monkeypatch.setattr(art_first_module, "owner_upload_root", lambda: owner_root)
    monkeypatch.setattr(studio_extensions, "owner_upload_root", lambda: owner_root)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: owner_root)
    bad_cells = tuple(("C01", "C02", "C03")[index % 3] for index in range(19 * 20))
    bad_png = encode_logical_png(19, 20, bad_cells)
    bad_sha = hashlib.sha256(bad_png).hexdigest()
    bad_source_id = f"owner-upload-{bad_sha}"
    bad_dir = owner_root / bad_source_id
    bad_dir.mkdir(parents=True)
    bad_record_bytes = _json_bytes(_source_record(bad_source_id, bad_sha, bad_png, 19, 20), newline=True)
    (bad_dir / "source.png").write_bytes(bad_png)
    (bad_dir / "source.json").write_bytes(bad_record_bytes)
    bad_request = GenerationRequest(
        seed="art-first-fixed-seed", width=20, height=20, generator_mode="ART_FIRST",
        generator_options={"namespace": "art-first", "version": 1, "values": {
            "source_id": bad_source_id,
            "source_sha256": bad_sha,
            "source_record_sha256": hashlib.sha256(bad_record_bytes).hexdigest(),
            "candidate_id": f"candidate-owner-{bad_sha[:48]}",
            "review_id": f"review-candidate-owner-{bad_sha[:48]}-0001",
        }},
    )
    invalid_dimensions = _run(bad_request)
    assert invalid_dimensions.is_success is False
    assert "20..59" in invalid_dimensions.failure_reason


def test_art_first_mask_constraints_preserve_existing_required_and_forbidden_cells():
    source_cells = ("C01", "VOID", "C02", "C03")
    mask = {"width": 2, "height": 2, "cells": ["REQUIRED", "FORBIDDEN", "RANDOM", "RANDOM"]}
    digest = _check_mask_constraints(mask, 2, 2, source_cells)
    assert digest is not None
    assert source_cells == ("C01", "VOID", "C02", "C03")

    mismatch = {"width": 2, "height": 2, "cells": ["REQUIRED", "FORBIDDEN", "FORBIDDEN", "RANDOM"]}
    with pytest.raises(art_first.ArtFirstUnavailable, match="FORBIDDEN"):
        _check_mask_constraints(mismatch, 2, 2, source_cells)


def test_art_first_transparent_source_stays_unavailable_without_current_void_attestation(monkeypatch, tmp_path):
    fixture = _fixture(monkeypatch, tmp_path, width=20, height=20, color_count=3)
    cells = list(fixture["cells"])
    cells[-1] = "VOID"
    raw_png = encode_logical_png(20, 20, cells)
    source_sha = hashlib.sha256(raw_png).hexdigest()
    source_id = f"owner-upload-{source_sha}"
    source_dir = fixture["owner_root"] / source_id
    source_dir.mkdir()
    record = _source_record(source_id, source_sha, raw_png, 20, 20)
    record_bytes = _json_bytes(record, newline=True)
    (source_dir / "source.png").write_bytes(raw_png)
    (source_dir / "source.json").write_bytes(record_bytes)
    request = GenerationRequest(
        seed="void-art-first", width=20, height=20, generator_mode="ART_FIRST", background_intent="TRANSPARENT",
        generator_options={"namespace": "art-first", "version": 1, "values": {
            "source_id": source_id,
            "source_sha256": source_sha,
            "source_record_sha256": hashlib.sha256(record_bytes).hexdigest(),
            "candidate_id": f"candidate-owner-{source_sha[:48]}",
            "review_id": f"review-candidate-owner-{source_sha[:48]}-0001",
        }},
    )
    result = _run(request)
    assert result.is_success is False
    assert "VOID_CAPABILITY_REQUIRED" in result.failure_reason


def _review_root_memory_setup(reparse_path: Path | None = None, configured_root: Path | None = None):
    patch = pytest.MonkeyPatch()
    output_root = Path("C:/virtual/art-first-output")
    extensions_path = output_root / "studio-extensions"
    review_path = extensions_path / "owner-review"
    enumerated: list[Path] = []
    safe_reads: list[Path] = []

    patch.setattr(art_first, "owner_upload_root", lambda: output_root / "owner-uploads")
    patch.setattr(art_first, "extensions_root", lambda: configured_root or extensions_path)
    patch.setattr(art_first, "_path_is_reparse_point", lambda path: path == reparse_path)
    patch.setattr(Path, "is_dir", lambda self: True)
    patch.setattr(Path, "resolve", lambda self, strict=False: self)
    patch.setattr(Path, "iterdir", lambda self: (enumerated.append(self), iter(()))[1])
    patch.setattr(art_first, "_safe_file", lambda path, *args: (safe_reads.append(path), b"")[1])
    return patch, extensions_path, review_path, enumerated, safe_reads


def test_art_first_rejects_studio_extensions_reparse_before_review_access():
    marker = Path("C:/virtual/art-first-output/studio-extensions")
    patch, _, _, enumerated, safe_reads = _review_root_memory_setup(reparse_path=marker)
    try:
        with pytest.raises(art_first.ArtFirstUnavailable, match="Studio extensions root.*unsafe"):
            art_first._validated_review_root()
        assert enumerated == []
        assert safe_reads == []
    finally:
        patch.undo()


def test_art_first_rejects_owner_review_reparse_before_review_access():
    marker = Path("C:/virtual/art-first-output/studio-extensions/owner-review")
    patch, _, _, enumerated, safe_reads = _review_root_memory_setup(reparse_path=marker)
    try:
        with pytest.raises(art_first.ArtFirstUnavailable, match="safe durable owner-review"):
            art_first._validated_review_root()
        assert enumerated == []
        assert safe_reads == []
    finally:
        patch.undo()


def test_art_first_rejects_noncanonical_injected_extensions_root():
    patch, _, _, enumerated, safe_reads = _review_root_memory_setup(
        configured_root=Path("C:/external/owner-review-authority")
    )
    try:
        with pytest.raises(art_first.ArtFirstUnavailable, match="configured Studio extensions root is not canonical"):
            art_first._validated_review_root()
        assert enumerated == []
        assert safe_reads == []
    finally:
        patch.undo()


def test_art_first_accepts_canonical_memory_review_root():
    patch, _, expected_review_root, enumerated, safe_reads = _review_root_memory_setup()
    try:
        assert art_first._validated_review_root() == expected_review_root
        assert enumerated == []
        assert safe_reads == []
    finally:
        patch.undo()


def _candidate_flow_reparse_setup(reparse_path: Path):
    patch = pytest.MonkeyPatch()
    output_root = Path("C:/virtual/art-first-output")
    owner_root = output_root / "owner-uploads"
    extensions_path = output_root / "studio-extensions"
    source_sha = "a" * 64
    source_id = f"owner-upload-{source_sha}"
    candidate_id = f"candidate-owner-{source_sha[:48]}"
    record_bytes = b"synthetic immutable source record"
    record_sha = hashlib.sha256(record_bytes).hexdigest()
    source_record_path = owner_root / source_id / "source.json"
    lineage = {
        "source_id": source_id,
        "source_sha256": source_sha,
        "source_record": str(source_record_path),
        "source_bytes_unchanged": True,
        "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
    }
    bundle = SimpleNamespace(
        artwork=SimpleNamespace(candidate_id=candidate_id, grid_hash="synthetic-grid"),
        metadata={
            "generation": {"result": {"generator": {"mode": "MASK", "id": "owner-upload-canonical-derive", "version": "1"}}},
            "generator_metadata": {
                "payload": {"namespace": "owner-upload", "data": {"source_lineage": lineage}},
                "classification": {"candidate_class": "PRODUCTION_CANDIDATE"},
            },
        },
    )
    safe_reads: list[tuple[Path, str]] = []
    enumerated: list[Path] = []

    patch.setattr(art_first, "owner_upload_root", lambda: owner_root)
    patch.setattr(art_first, "extensions_root", lambda: extensions_path)
    patch.setattr(art_first, "_path_is_reparse_point", lambda path: path == reparse_path)
    patch.setattr(art_first, "_safe_file", lambda path, root, limit, label: (safe_reads.append((path, label)), record_bytes)[1])
    patch.setattr(art_first, "read_bundle", lambda candidate_dir: bundle)
    patch.setattr(Path, "is_dir", lambda self: True)
    patch.setattr(Path, "is_file", lambda self: True)
    patch.setattr(Path, "exists", lambda self: False)
    patch.setattr(Path, "resolve", lambda self, strict=False: self)
    patch.setattr(Path, "iterdir", lambda self: (enumerated.append(self), iter(()))[1])
    return patch, source_sha, record_sha, source_id, candidate_id, safe_reads, enumerated


def test_art_first_candidate_flow_rejects_review_reparse_before_review_access():
    for marker in (
        Path("C:/virtual/art-first-output/studio-extensions"),
        Path("C:/virtual/art-first-output/studio-extensions/owner-review"),
    ):
        patch, source_sha, record_sha, source_id, candidate_id, safe_reads, enumerated = _candidate_flow_reparse_setup(marker)
        try:
            with pytest.raises(art_first.ArtFirstUnavailable, match="reparse|unsafe|safe durable"):
                art_first._candidate_and_review(
                    {"source_sha256": source_sha},
                    record_sha,
                    source_id,
                    candidate_id,
                    f"review-{candidate_id}-0001",
                )
            assert enumerated == []
            assert all("owner-review" not in str(path) for path, _ in safe_reads)
        finally:
            patch.undo()
