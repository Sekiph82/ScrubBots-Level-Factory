import pytest

from scrubbots_pixel_factory.core import (
    FailureCode,
    GenerationResult,
    RNG_ALGORITHM,
    ResultContractError,
)
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


def test_failure_requires_stable_reason_and_has_no_partial_grid() -> None:
    failure = GenerationResult.failure(code=FailureCode.RETRY_EXHAUSTED, reason="bounded retries exhausted")
    assert not failure.is_success and failure.logical_grid is None and failure.used_palette == ()
    assert failure.failure_reason == "bounded retries exhausted"
    with pytest.raises(ResultContractError):
        GenerationResult.failure(code="GENERATION_FAILED", reason="   ")


def test_explicit_very_hard_59_by_59_result_has_exact_logical_cell_count() -> None:
    request = make_request(difficulty="VERY_HARD", width=59, height=59, palette_subset=[f"C{i:02d}" for i in range(1, 11)])
    result = DeterministicContractProbeGenerator().generate(request)
    assert (result.width, result.height) == (59, 59)
    assert len(result.logical_grid) == 59 * 59
