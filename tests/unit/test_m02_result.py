import pytest

from scrubbots_pixel_factory.core import (
    FailureCode,
    GenerationResult,
    RNG_ALGORITHM,
    ResultContractError,
)
from scrubbots_pixel_factory.core.rng import DeterministicRNG
from tests.support.deterministic_probe import DeterministicContractProbeGenerator
from tests.unit.test_m02_request import make_request


def valid_result():
    request = make_request()
    return DeterministicContractProbeGenerator().generate(request)


def test_success_result_is_immutable_canonical_and_records_provenance() -> None:
    result = valid_result()
    assert result.is_success and result.ok
    assert len(result.logical_grid) == result.width * result.height
    assert result.used_palette == tuple(sorted(result.used_palette, key=lambda item: int(item[1:])))
    assert result.rng_algorithm == RNG_ALGORITHM
    assert result.canonical_bytes() == result.canonical_json().encode("utf-8")
    with pytest.raises((AttributeError, TypeError)):
        result.width = 1  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.provenance["stage_seeds"]["geometry"] = "0" * 64  # type: ignore[index]


def test_public_raw_result_construction_revalidates_all_state() -> None:
    with pytest.raises(ResultContractError):
        GenerationResult(status="SUCCESS", request=None, width=1, height=1, logical_grid=("C17",), used_palette=(), generator_mode="MASK", generator_id=None, generator_version=None, seed=1, rng_algorithm=None, provenance=None, failure_code=None, failure_reason=None)  # type: ignore[call-arg]


def _constructor_fields(result):
    fields = {
        "status": result.status,
        "request": result.request,
        "width": result.width,
        "height": result.height,
        "logical_grid": result.logical_grid,
        "used_palette": result.used_palette,
        "generator_mode": result.generator_mode,
        "generator_id": result.generator_id,
        "generator_version": result.generator_version,
        "seed": result.seed,
        "rng_algorithm": result.rng_algorithm,
        "provenance": result.provenance,
        "failure_code": result.failure_code,
        "failure_reason": result.failure_reason,
    }
    if result.provenance is not None:
        fields["provenance"] = {
            key: dict(value) if hasattr(value, "items") else value
            for key, value in result.provenance.items()
        }
    return fields


def test_no_unchecked_internal_result_builder_remains_and_valid_direct_state_works() -> None:
    result = valid_result()
    assert not hasattr(GenerationResult, "_from_validated_fields")
    direct = GenerationResult(**_constructor_fields(result))
    assert direct.canonical_bytes() == result.canonical_bytes()
    failure = GenerationResult.failure(code=FailureCode.GENERATION_FAILED, reason="bounded failure")
    direct_failure = GenerationResult(**_constructor_fields(failure))
    assert direct_failure.canonical_bytes() == failure.canonical_bytes()


@pytest.mark.parametrize("mutate", [
    lambda fields: fields.update(request=None),
    lambda fields: fields.update(logical_grid=("C17",)),
    lambda fields: fields.update(width=1, height=1, logical_grid=("C01",)),
    lambda fields: fields.update(generator_version=""),
    lambda fields: fields.update(seed=999),
    lambda fields: fields["provenance"]["stage_seeds"].update({"geometry": "0" * 64}),
])
def test_direct_constructor_rejects_each_invalid_success_state(mutate) -> None:
    fields = _constructor_fields(valid_result())
    mutate(fields)
    with pytest.raises(ResultContractError):
        GenerationResult(**fields)


@pytest.mark.parametrize("mutate", [
    lambda fields: fields.update(logical_grid=("C01",)),
    lambda fields: fields.update(width=20),
    lambda fields: fields.update(failure_reason=""),
    lambda fields: fields.update(used_palette=("C01",)),
])
def test_direct_constructor_rejects_each_invalid_failure_state(mutate) -> None:
    fields = _constructor_fields(GenerationResult.failure(code=FailureCode.GENERATION_FAILED, reason="bounded failure"))
    mutate(fields)
    with pytest.raises(ResultContractError):
        GenerationResult(**fields)


@pytest.mark.parametrize("grid", [[], ["C01"] * 399, ["C01"] * 400])
def test_success_rejects_wrong_length_or_illegal_color_count(grid) -> None:
    request = make_request(width=20, height=20)
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=request, width=20, height=20, logical_grid=grid,
            generator_id="probe", generator_version="1", rng_algorithm=RNG_ALGORITHM,
            provenance={"stage_seeds": {stage: "0" * 64 for stage in ("dimension", "palette", "geometry", "colorization", "post_processing")}},
        )


@pytest.mark.parametrize("bad", ["C17", "BG01", "#E94B4B"])
def test_success_rejects_off_palette_cells(bad) -> None:
    result = valid_result()
    cells = list(result.logical_grid)
    cells[0] = bad
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=result.request, width=result.width, height=result.height, logical_grid=cells,
            generator_id="probe", generator_version="1", rng_algorithm=RNG_ALGORITHM,
            provenance=result.provenance,
        )


def test_success_rejects_mode_mismatch_and_malformed_provenance() -> None:
    result = valid_result()
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=result.request, width=result.width, height=result.height, logical_grid=result.logical_grid,
            generator_id="probe", generator_version="1", generator_mode="RULES",
            rng_algorithm=RNG_ALGORITHM, provenance=result.provenance,
        )
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=result.request, width=result.width, height=result.height, logical_grid=result.logical_grid,
            generator_id="probe", generator_version="1", rng_algorithm=RNG_ALGORITHM,
            provenance={"stage_seeds": {}},
        )


def _mutable_provenance(result):
    return {key: dict(value) if isinstance(value, dict) or hasattr(value, "items") else value for key, value in result.provenance.items()}


@pytest.mark.parametrize("mutate", [
    lambda provenance: provenance["stage_seeds"].update({"geometry": "0" * 64}),
    lambda provenance: provenance["stage_seeds"].pop("geometry"),
    lambda provenance: provenance["stage_seeds"].update({"unexpected": "0" * 64}),
    lambda provenance: provenance["stage_seeds"].update(DeterministicRNG(999).stage_seeds()),
    lambda provenance: provenance["retry_seeds"].update({"0": "0" * 64}),
    lambda provenance: provenance["retry_seeds"].update({"01": provenance["retry_seeds"]["0"]}),
    lambda provenance: provenance["retry_seeds"].update({"1": provenance["retry_seeds"]["0"]}),
])
def test_provenance_is_authenticated_not_only_shape_checked(mutate) -> None:
    result = valid_result()
    provenance = _mutable_provenance(result)
    mutate(provenance)
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=result.request, width=result.width, height=result.height, logical_grid=result.logical_grid,
            generator_id=result.generator_id, generator_version=result.generator_version,
            rng_algorithm=RNG_ALGORITHM, provenance=provenance,
        )


def test_provenance_from_exact_request_and_rng_remains_accepted() -> None:
    result = valid_result()
    accepted = GenerationResult.success(
        request=result.request, width=result.width, height=result.height, logical_grid=result.logical_grid,
        generator_id=result.generator_id, generator_version=result.generator_version,
        rng_algorithm=RNG_ALGORITHM, provenance=result.provenance,
    )
    assert accepted.canonical_bytes() == result.canonical_bytes()


def test_present_null_retry_provenance_is_rejected() -> None:
    result = valid_result()
    provenance = _mutable_provenance(result)
    provenance["retry_seeds"] = None
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=result.request, width=result.width, height=result.height, logical_grid=result.logical_grid,
            generator_id=result.generator_id, generator_version=result.generator_version,
            rng_algorithm=RNG_ALGORITHM, provenance=provenance,
        )


def test_success_rejects_wrong_seed_and_missing_generator_version() -> None:
    result = valid_result()
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=result.request, width=result.width, height=result.height, logical_grid=result.logical_grid,
            generator_id=result.generator_id, generator_version=result.generator_version, seed=999,
            rng_algorithm=RNG_ALGORITHM, provenance=result.provenance,
        )
    with pytest.raises(ResultContractError):
        GenerationResult.success(
            request=result.request, width=result.width, height=result.height, logical_grid=result.logical_grid,
            generator_id=result.generator_id, generator_version="", rng_algorithm=RNG_ALGORITHM,
            provenance=result.provenance,
        )


def test_failure_requires_stable_reason_and_has_no_partial_grid() -> None:
    failure = GenerationResult.failure(code=FailureCode.RETRY_EXHAUSTED, reason="bounded retries exhausted")
    assert not failure.is_success and failure.logical_grid is None and failure.used_palette == ()
    assert failure.failure_reason == "bounded retries exhausted"
    with pytest.raises(ResultContractError):
        GenerationResult.failure(code="GENERATION_FAILED", reason="   ")
    assert failure.canonical_bytes() == GenerationResult.failure(code=FailureCode.RETRY_EXHAUSTED, reason="bounded retries exhausted").canonical_bytes()
    for forbidden in ("logical_grid", "width", "height", "used_palette"):
        with pytest.raises(TypeError):
            GenerationResult.failure(code=FailureCode.GENERATION_FAILED, reason="no partial", **{forbidden: ()})  # type: ignore[call-arg]


def test_explicit_very_hard_59_by_59_result_has_exact_logical_cell_count() -> None:
    request = make_request(difficulty="VERY_HARD", width=59, height=59, palette_subset=[f"C{i:02d}" for i in range(1, 11)])
    result = DeterministicContractProbeGenerator().generate(request)
    assert (result.width, result.height) == (59, 59)
    assert len(result.logical_grid) == 59 * 59
