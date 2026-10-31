from __future__ import annotations

import hashlib
import json
import struct
import zlib
from pathlib import Path

import pytest

from scrubbots_pixel_factory.contracts.candidate_provenance import (
    CandidateClass,
    CandidateProvenanceError,
    build_candidate_classification,
    validate_candidate_classification,
)
from scrubbots_pixel_factory.core import DeterministicRNG, GenerationRequest, GenerationResult, RNG_ALGORITHM
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.contracts.palette import VOID_CELL_ID
from scrubbots_pixel_factory.output.bundle import OutputContractError, build_export_bundle
from scrubbots_pixel_factory.output.png import PNGContractError, decode_logical_png, encode_logical_png
from scrubbots_pixel_factory.quality import evaluate_grid
from scrubbots_pixel_factory.supply_pipeline import release_pool
from scrubbots_pixel_factory.supply_pipeline.release_pool import ReleaseError, enter_release_pool, validate_pool_candidate_provenance


def _candidate(
    *, owner_source: bool, source_cells: tuple[str, ...] | None = None,
    candidate_cells: tuple[str, ...] | None = None, source_png: bytes | None = None,
    source_root: Path | None = None, monkeypatch: pytest.MonkeyPatch | None = None,
) -> dict[str, object]:
    cells = candidate_cells or tuple(("C01", "C02", "C03")[index % 3] for index in range(400))
    source_cells = source_cells or cells
    source_png = (source_png or encode_logical_png(20, 20, source_cells)) if owner_source else b""
    source_sha = hashlib.sha256(source_png if owner_source else b"test-seed").hexdigest()
    request = GenerationRequest(
        seed=source_sha, width=20, height=20,
        background_intent="TRANSPARENT" if VOID_CELL_ID in cells else "BACKGROUND",
    )
    candidate_id = f"candidate-owner-{source_sha[:48]}" if owner_source else "candidate-fixture"
    rng = DeterministicRNG(request.seed)
    result = GenerationResult.success(
        request=request,
        width=20,
        height=20,
        logical_grid=cells,
        generator_id="owner-upload-canonical-derive" if owner_source else "provenance-fixture",
        generator_version="1" if owner_source else "1.0.0",
        rng_algorithm=RNG_ALGORITHM,
        provenance={"stage_seeds": rng.stage_seeds()},
    )
    metadata = None
    if owner_source:
        if source_root is None or monkeypatch is None:
            raise ValueError("owner-source fixture requires a bounded repository-local root")
        from scrubbots_pixel_factory import studio_extensions as studio

        repository = source_root.resolve()
        owner_root = repository / "level_factory" / "output" / "owner-uploads"
        monkeypatch.setattr(studio, "_repository_root", lambda: repository)
        monkeypatch.setattr(studio, "owner_upload_root", lambda: owner_root)
        source_directory = owner_root / f"owner-upload-{source_sha}"
        source_directory.mkdir(parents=True, exist_ok=True)
        (source_directory / "source.png").write_bytes(source_png)
        (source_directory / "source.json").write_text(json.dumps({
            "schema": "scrubbots-owner-upload-source", "version": 1,
            "source_id": f"owner-upload-{source_sha}", "origin": "OWNER_UPLOAD",
            "source_sha256": source_sha, "byte_length": len(source_png),
            "media_type": "image/png", "original_filename": "source.png",
            "original_width": 20, "original_height": 20,
            "immutable_relative_path": f"owner-uploads/owner-upload-{source_sha}/source.png",
            "source_record_relative_path": f"owner-uploads/owner-upload-{source_sha}/source.json",
            "status": "SOURCE_ONLY", "validation_state": "UNVALIDATED",
        }, sort_keys=True), encoding="utf-8")
        metadata = {
            "namespace": "owner-upload",
            "data": {
                "source_lineage": {
                    "source_id": f"owner-upload-{source_sha}",
                    "source_sha256": source_sha,
                    "source_record": f"level_factory/output/owner-uploads/owner-upload-{source_sha}/source.json",
                    "source_bytes_unchanged": True,
                    "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
                }
            },
        }
    bundle = build_export_bundle(
        result,
        candidate_id,
        quality_report=evaluate_grid(20, 20, cells),
        generator_metadata=metadata,
    )
    return {
        "candidate_id": bundle.artwork.candidate_id,
        "artwork_sha256": hashlib.sha256(bundle.artwork_png).hexdigest(),
        "grid_hash": bundle.artwork.grid_hash,
        "width": bundle.artwork.width,
        "height": bundle.artwork.height,
        "metadata": bundle.metadata,
        "source_path": f"level_factory/output/studio-derived-candidates/{candidate_id}",
        "source_png": source_png,
        "artwork_png": bundle.artwork_png,
    }


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _filtered_owner_png(
    cells: tuple[str, ...], *, width: int = 20, height: int = 20,
    filters: tuple[int, ...] = (1, 2, 4), color_type: int = 2,
    semi_alpha_at: int | None = None, foreign_color_at: int | None = None,
    ancillary: bool = True,
) -> bytes:
    """Encode standards-compliant RGB(A) PNG bytes with specified row filters."""
    channels = 4 if color_type == 6 else 3
    rows: list[bytes] = []
    pixels: list[bytes] = []
    for index, cell in enumerate(cells):
        rgb = (1, 2, 3) if index == foreign_color_at else (
            (0, 0, 0) if cell == VOID_CELL_ID else CANONICAL_PALETTE.rgb_for(cell)
        )
        alpha = 0 if cell == VOID_CELL_ID else 255
        if index == semi_alpha_at:
            alpha = 127
        pixels.append(bytes((*rgb, alpha)) if channels == 4 else bytes(rgb))
    for row_index in range(height):
        rows.append(b"".join(pixels[row_index * width : (row_index + 1) * width]))

    scanlines = bytearray()
    previous = bytes(width * channels)
    for row_index, row in enumerate(rows):
        filter_type = filters[row_index % len(filters)]
        encoded = bytearray(len(row))
        for index, value in enumerate(row):
            left = row[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 4:
                estimate = left + up - upper_left
                distances = (abs(estimate - left), abs(estimate - up), abs(estimate - upper_left))
                predictor = (left, up, upper_left)[distances.index(min(distances))]
            else:
                raise ValueError("test PNG encoder supports filters 1, 2, and 4")
            encoded[index] = (value - predictor) & 0xFF
        scanlines.append(filter_type)
        scanlines.extend(encoded)
        previous = row

    header = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(_png_chunk(b"IHDR", header))
    if ancillary:
        png.extend(_png_chunk(b"tEXt", b"Comment\x00owner source parity fixture"))
    png.extend(_png_chunk(b"IDAT", zlib.compress(bytes(scanlines))))
    png.extend(_png_chunk(b"IEND", b""))
    return bytes(png)


def _install_fake_owner_source(candidate: dict[str, object], source_png: bytes, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, width: int = 20, height: int = 20) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio

    repository = tmp_path.resolve()
    owner_root = repository / "level_factory" / "output" / "owner-uploads"
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: owner_root)
    metadata = candidate["metadata"]
    lineage = metadata["generator_metadata"]["payload"]["data"]["source_lineage"]
    source_id = lineage["source_id"]
    source_directory = owner_root / source_id
    source_directory.mkdir(parents=True, exist_ok=True)
    source_file = source_directory / "source.png"
    if not source_file.exists():
        source_file.write_bytes(source_png)
    elif source_file.read_bytes() != source_png:
        raise AssertionError("owner source fixture changed between export and Pool checks")
    record_file = source_directory / "source.json"
    if not record_file.exists():
        record_file.write_text(json.dumps({
            "schema": "scrubbots-owner-upload-source", "version": 1,
            "source_id": source_id, "origin": "OWNER_UPLOAD",
            "source_sha256": hashlib.sha256(source_png).hexdigest(), "byte_length": len(source_png),
            "media_type": "image/png", "original_filename": "source.png",
            "original_width": width, "original_height": height,
            "immutable_relative_path": f"owner-uploads/{source_id}/source.png",
            "source_record_relative_path": f"owner-uploads/{source_id}/source.json",
            "status": "SOURCE_ONLY", "validation_state": "UNVALIDATED",
        }, sort_keys=True), encoding="utf-8")
    candidate_root = repository / str(candidate["source_path"])
    candidate_root.mkdir(parents=True)
    (candidate_root / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (candidate_root / "artwork.png").write_bytes(candidate["artwork_png"])


def _owner_accept(candidate: dict[str, object]) -> dict[str, object]:
    return {
        "disposition": "ACCEPT",
        "review_id": "review-current",
        "candidate_id": candidate["candidate_id"],
        "artwork_sha256": candidate["artwork_sha256"],
    }


def test_generated_candidate_defaults_to_test_and_is_request_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    def reject_source_verification(_candidate: object, _classification: object) -> str:
        pytest.fail("TEST candidates must be rejected before owner-source verification")

    monkeypatch.setattr(release_pool, "_verify_candidate_source_grid_binding", reject_source_verification)
    candidate = _candidate(owner_source=False)
    metadata = candidate["metadata"]
    assert isinstance(metadata, dict)
    generator = metadata["generator_metadata"]
    classification = generator["classification"]
    assert classification["candidate_class"] == CandidateClass.TEST.value
    assert classification["candidate_id"] == candidate["candidate_id"]
    assert classification["request_sha256"]
    assert classification["generator_version"] == "1.0.0"
    assert classification["attempt_id"].startswith("candidate-fixture:attempt:")

    forged = {**classification, "candidate_class": CandidateClass.PRODUCTION_CANDIDATE.value}
    with pytest.raises(CandidateProvenanceError):
        validate_candidate_classification(
            forged,
            metadata["generation"]["result"],
            candidate_id=candidate["candidate_id"],
            grid_hash=candidate["grid_hash"],
            generator_metadata=generator["payload"],
        )
    with pytest.raises(ReleaseError, match="TEST candidate"):
        validate_pool_candidate_provenance(candidate, None)
    with pytest.raises(ReleaseError, match="TEST candidate"):
        enter_release_pool(
            candidate,
            {"disposition": "READY", "primary": {"state": "READY"}},
            {"disposition": "ACCEPT", "candidate_id": candidate["candidate_id"], "artwork_sha256": candidate["artwork_sha256"]},
        )


def test_forged_production_class_still_requires_owner_source_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate(owner_source=False)
    metadata = candidate["metadata"]
    generator = metadata["generator_metadata"]
    classification = generator["classification"]
    classification["candidate_class"] = CandidateClass.PRODUCTION_CANDIDATE.value
    verification_calls: list[tuple[object, object]] = []

    def require_source_verification(candidate_arg: object, classification_arg: object) -> str:
        verification_calls.append((candidate_arg, classification_arg))
        raise ReleaseError("canonical OWNER_UPLOAD source verification required")

    monkeypatch.setattr(release_pool, "_verify_candidate_source_grid_binding", require_source_verification)
    with pytest.raises(ReleaseError, match="canonical OWNER_UPLOAD source verification required"):
        validate_pool_candidate_provenance(candidate, None)
    assert verification_calls == [(candidate, classification)]


@pytest.mark.parametrize(
    ("malformed_class", "message"),
    [(None, "no valid production candidate class"), ("OWNER_APPROVED", "invalid production candidate class")],
)
def test_malformed_candidate_class_fails_closed_before_owner_source_verification(
    malformed_class: object, message: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _candidate(owner_source=False)
    metadata = candidate["metadata"]
    classification = metadata["generator_metadata"]["classification"]
    classification["candidate_class"] = malformed_class
    monkeypatch.setattr(
        release_pool,
        "_verify_candidate_source_grid_binding",
        lambda *_args: pytest.fail("malformed classification must fail before owner-source verification"),
    )
    with pytest.raises(ReleaseError, match=message):
        validate_pool_candidate_provenance(candidate, None)


def test_owner_upload_metadata_without_source_bytes_cannot_create_production_export() -> None:
    source_sha = hashlib.sha256(b"missing owner source fixture SB-LF02-008").hexdigest()
    request = GenerationRequest(
        seed=source_sha, width=20, height=20, generator_mode="MASK",
        palette_subset=("C01", "C02", "C03"),
    )
    cells = tuple(("C01", "C02", "C03")[index % 3] for index in range(400))
    rng = DeterministicRNG(request.seed)
    result = GenerationResult.success(
        request=request, width=20, height=20, logical_grid=cells,
        generator_id="owner-upload-canonical-derive", generator_version="1",
        rng_algorithm=RNG_ALGORITHM, provenance={"stage_seeds": rng.stage_seeds()},
    )
    generator_metadata = {
        "namespace": "owner-upload",
        "data": {"source_lineage": {
            "source_id": f"owner-upload-{source_sha}",
            "source_sha256": source_sha,
            "source_record": f"level_factory/output/owner-uploads/owner-upload-{source_sha}/source.json",
            "source_bytes_unchanged": True,
            "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
        }},
    }
    classification = build_candidate_classification(
        result.canonical_dict(),
        candidate_id=f"candidate-owner-{source_sha[:48]}",
        grid_hash=hashlib.sha256(b"grid hash is bound by the bundle").hexdigest(),
        generator_metadata=generator_metadata,
    )
    assert classification["candidate_class"] == CandidateClass.TEST.value
    with pytest.raises(OutputContractError, match="canonical OWNER_UPLOAD source bytes could not be verified"):
        build_export_bundle(
            result,
            f"candidate-owner-{source_sha[:48]}",
            generator_metadata=generator_metadata,
        )


@pytest.mark.parametrize(
    "candidate_class",
    [
        CandidateClass.TEST,
        CandidateClass.DEVELOPMENT,
        CandidateClass.PREVIEW,
        CandidateClass.UNAVAILABLE,
        CandidateClass.PRODUCTION_CANDIDATE,
    ],
)
def test_non_owner_candidate_classes_fail_actual_pool_promotion(candidate_class: CandidateClass) -> None:
    candidate = _candidate(owner_source=False)
    metadata = candidate["metadata"]
    metadata["generator_metadata"]["classification"]["candidate_class"] = candidate_class.value
    review = _owner_accept(candidate)
    pipeline = {"disposition": "READY", "primary": {"state": "READY"}}
    with pytest.raises(ReleaseError):
        validate_pool_candidate_provenance(candidate, review)
    with pytest.raises(ReleaseError):
        enter_release_pool(candidate, pipeline, review)


def test_owner_source_filter_and_ancillary_png_reaches_real_pool_provenance_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cells = tuple(
        VOID_CELL_ID if index == 21 else ("C01", "C02", "C03")[index % 3]
        for index in range(400)
    )
    old_codec_input = _filtered_owner_png(cells, color_type=6, ancillary=False)
    with pytest.raises(PNGContractError):
        decode_logical_png(old_codec_input)
    source_png = _filtered_owner_png(cells, color_type=6, ancillary=True)
    from scrubbots_pixel_factory import studio_extensions as studio

    width, height, decoded_pixels = studio._validation_pixels(source_png)
    assert (width, height) == (20, 20)
    assert len(decoded_pixels) == 20 * 20 * 4
    candidate = _candidate(owner_source=True, source_cells=cells, candidate_cells=cells, source_png=source_png, source_root=tmp_path, monkeypatch=monkeypatch)
    _install_fake_owner_source(candidate, source_png, tmp_path, monkeypatch)
    classification = validate_pool_candidate_provenance(
        candidate,
        _owner_accept(candidate),
    )
    assert classification["candidate_class"] == CandidateClass.PRODUCTION_CANDIDATE.value
    assert classification["source_sha256"]
    assert studio._owner_source_grid(source_png)[2] == cells

    # Positive control reaches the next Pool stage with a synthetic canonical
    # READY record; stop before official game/runtime proof is evaluated.
    class ProvenancePassed(Exception):
        pass

    monkeypatch.setattr(
        release_pool,
        "_canonical_official_difficulty",
        lambda _primary: (_ for _ in ()).throw(ProvenancePassed()),
    )
    with pytest.raises(ProvenancePassed):
        enter_release_pool(
            candidate,
            {"disposition": "READY", "primary": {"state": "READY", "acceptance": {"solver_status": "SOLVED", "replay": "WIN"}}},
            _owner_accept(candidate),
        )

    # READY_AUTO inclusion does not need ACCEPT; only an explicitly supplied
    # stale/mismatched review must fail closed.
    assert validate_pool_candidate_provenance(candidate, None)["candidate_class"] == CandidateClass.PRODUCTION_CANDIDATE.value
    with pytest.raises(ReleaseError, match="exact current owner ACCEPT"):
        validate_pool_candidate_provenance(
            candidate,
            {"disposition": "ACCEPT", "candidate_id": "other", "artwork_sha256": candidate["artwork_sha256"]},
        )
    metadata = candidate["metadata"]
    generator = metadata["generator_metadata"]
    forged_classification = {**generator["classification"], "source_sha256": "0" * 64}
    with pytest.raises(CandidateProvenanceError, match="does not match request"):
        validate_candidate_classification(
            forged_classification,
            metadata["generation"]["result"],
            candidate_id=candidate["candidate_id"],
            grid_hash=candidate["grid_hash"],
            generator_metadata=generator["payload"],
        )

    # The claimed source identity and its PNG digest are genuine, but its
    # decoded cell grid differs from the selected candidate's artwork.
    mismatched_cells = tuple(("C04", "C05", "C06")[index % 3] for index in range(400))
    mismatched_source = _filtered_owner_png(mismatched_cells, filters=(4, 1, 2), ancillary=True)
    with pytest.raises(OutputContractError, match="exact canonical source bytes and artwork"):
        _candidate(
            owner_source=True, source_cells=mismatched_cells,
            candidate_cells=tuple(("C01", "C02", "C03")[index % 3] for index in range(400)),
            source_png=mismatched_source, source_root=tmp_path / "mismatch", monkeypatch=monkeypatch,
        )


@pytest.mark.parametrize("invalid_kind", ["semi-alpha", "foreign-color", "oversized"])
def test_owner_source_noncanonical_or_oversized_png_fails_real_pool_gate(
    invalid_kind: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if invalid_kind == "oversized":
        cells = tuple(("C01", "C02", "C03")[index % 3] for index in range(1200))
        source_png = _filtered_owner_png(cells, width=60, height=20, filters=(1, 2, 4))
        source_width, source_height = 60, 20
    else:
        cells = tuple(("C01", "C02", "C03")[index % 3] for index in range(400))
        source_png = _filtered_owner_png(
            cells,
            color_type=6,
            semi_alpha_at=17 if invalid_kind == "semi-alpha" else None,
            foreign_color_at=17 if invalid_kind == "foreign-color" else None,
        )
        source_width, source_height = 20, 20
    with pytest.raises(OutputContractError):
        _candidate(
            owner_source=True, source_cells=cells[:400], source_png=source_png,
            source_root=tmp_path, monkeypatch=monkeypatch,
        )


def test_owner_source_candidate_path_escape_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio

    candidate = _candidate(owner_source=True, source_root=tmp_path, monkeypatch=monkeypatch)
    candidate["source_path"] = "../outside-candidate"
    monkeypatch.setattr(studio, "_repository_root", lambda: tmp_path.resolve())
    with pytest.raises(ReleaseError, match="candidate source lineage path is invalid"):
        release_pool._verify_candidate_source_grid_binding(
            candidate, candidate["metadata"]["generator_metadata"]["classification"]
        )


def test_selected_plan_revalidation_uses_same_filtered_owner_source_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scrubbots_pixel_factory import studio_extensions as studio

    cells = tuple(("C01", "C02", "C03")[index % 3] for index in range(400))
    source_png = _filtered_owner_png(cells, filters=(1, 2, 4), ancillary=True)
    candidate = _candidate(owner_source=True, source_cells=cells, source_png=source_png, source_root=tmp_path, monkeypatch=monkeypatch)
    _install_fake_owner_source(candidate, source_png, tmp_path, monkeypatch)
    classification = candidate["metadata"]["generator_metadata"]["classification"]
    plan = {"plan_hash": "synthetic-filtered-plan", "K": 1, "slots": [{"n": 1, "chosen_id": candidate["candidate_id"]}]}
    entry = {
        "candidate_id": candidate["candidate_id"],
        "candidate_classification": classification,
        "candidate": candidate,
        "pipeline": {"disposition": "READY"},
        "source_bundle": candidate["source_path"],
    }
    plan_path = tmp_path / "studio-extensions" / "release" / "campaign_plan.json"
    original_json = release_pool._json
    monkeypatch.setattr(release_pool, "discover_game_project", lambda _game: tmp_path)
    monkeypatch.setattr(studio, "extensions_root", lambda: tmp_path / "studio-extensions")
    monkeypatch.setattr(
        release_pool,
        "_json",
        lambda path: plan if Path(path) == plan_path else original_json(path),
    )
    monkeypatch.setattr(release_pool, "_production_release_entries", lambda: [entry])
    monkeypatch.setattr(studio, "_latest_review", lambda _candidate_id: _owner_accept(candidate))
    monkeypatch.setattr(release_pool, "_game_authority", lambda _game: ({}, {}))
    monkeypatch.setattr(
        release_pool,
        "build_campaign_plan",
        lambda **_kwargs: {"plan_hash": "synthetic-filtered-plan"},
    )

    validated = release_pool.validate_release_plan(
        plan_hash="synthetic-filtered-plan", game_project=tmp_path
    )
    assert validated["prefix"] == plan["slots"]
    assert validated["items"][0]["candidate"]["candidate_id"] == candidate["candidate_id"]


def _release_entry(candidate_id: str, *, production: bool) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "candidate_classification": (
            {"candidate_class": CandidateClass.PRODUCTION_CANDIDATE.value} if production else None
        ),
        "eligibility_source": "OWNER_ACCEPT" if production else "READY_AUTO",
        "review_id": "review-current" if production else None,
        "candidate": {"candidate_id": candidate_id},
        "pipeline": {"disposition": "READY"},
    }


def test_legacy_ready_auto_is_visible_but_cannot_enter_plan_or_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    from scrubbots_pixel_factory import studio_extensions as studio

    legacy = _release_entry("legacy-ready-auto", production=False)
    accepted = _release_entry("owner-accepted", production=True)
    monkeypatch.setattr(release_pool, "release_entries", lambda: [legacy, accepted])
    monkeypatch.setattr(
        studio,
        "_latest_review",
        lambda candidate_id: _owner_accept({"candidate_id": candidate_id, "artwork_sha256": "art"})
        if candidate_id == "owner-accepted" else None,
    )
    monkeypatch.setattr(release_pool, "discover_game_project", lambda _game: Path("synthetic-game"))
    monkeypatch.setattr(release_pool, "_game_authority", lambda _game: ({}, {}))
    planned: dict[str, object] = {}

    def build_campaign_plan(**kwargs: object) -> dict[str, object]:
        planned["pool"] = kwargs["pool"]
        return {"plan_hash": "synthetic-plan", "slots": []}

    monkeypatch.setattr(release_pool, "build_campaign_plan", build_campaign_plan)
    monkeypatch.setattr(release_pool, "write_campaign_plan", lambda *_args: None)
    monkeypatch.setattr(studio, "extensions_root", lambda: Path("synthetic-extensions"))
    release_pool.build_release_plan(game_project="synthetic-game")
    assert [entry["candidate_id"] for entry in planned["pool"]] == ["owner-accepted"]

    legacy_plan = {"plan_hash": "legacy-plan", "K": 1, "slots": [{"n": 1, "chosen_id": "legacy-ready-auto"}]}
    monkeypatch.setattr(release_pool, "release_entries", lambda: [legacy])
    monkeypatch.setattr(release_pool, "_json", lambda _path: legacy_plan)
    with pytest.raises(ReleaseError, match="legacy or no-longer-eligible"):
        release_pool.validate_release_plan(plan_hash="legacy-plan", game_project="synthetic-game")
    publish_calls: list[object] = []
    monkeypatch.setattr(release_pool, "publish_batch", lambda **kwargs: publish_calls.append(kwargs))
    with pytest.raises(ReleaseError, match="legacy or no-longer-eligible"):
        release_pool.approve_release_plan(plan_hash="legacy-plan", game_project="synthetic-game")
    assert publish_calls == []


@pytest.mark.parametrize(
    "candidate_class",
    [CandidateClass.TEST, CandidateClass.DEVELOPMENT, CandidateClass.PREVIEW, CandidateClass.UNAVAILABLE],
)
def test_nonproduction_class_cannot_be_selected_for_approval(
    candidate_class: CandidateClass, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pathlib import Path

    from scrubbots_pixel_factory import studio_extensions as studio

    entry = _release_entry("not-production", production=True)
    entry["candidate_classification"] = {"candidate_class": candidate_class.value}
    plan = {"plan_hash": "nonproduction-plan", "K": 1, "slots": [{"n": 1, "chosen_id": "not-production"}]}
    monkeypatch.setattr(release_pool, "release_entries", lambda: [entry])
    monkeypatch.setattr(studio, "_latest_review", lambda _candidate_id: {"disposition": "ACCEPT", "review_id": "review-current"})
    monkeypatch.setattr(studio, "extensions_root", lambda: Path("synthetic-extensions"))
    monkeypatch.setattr(release_pool, "discover_game_project", lambda _game: Path("synthetic-game"))
    monkeypatch.setattr(release_pool, "_json", lambda _path: plan)
    publish_calls: list[object] = []
    monkeypatch.setattr(release_pool, "publish_batch", lambda **kwargs: publish_calls.append(kwargs))
    with pytest.raises(ReleaseError, match="legacy or no-longer-eligible"):
        release_pool.approve_release_plan(plan_hash="nonproduction-plan", game_project="synthetic-game")
    assert publish_calls == []
