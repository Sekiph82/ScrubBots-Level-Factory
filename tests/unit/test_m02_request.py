import json

import pytest

from scrubbots_pixel_factory.core import GenerationRequest, GeneratorOptions, RequestContractError


def make_request(**overrides):
    values = {
        "difficulty": "EASY",
        "seed": 1,
        "generator_mode": "MASK",
        "generator_options": {"namespace": "probe", "version": 1, "values": {"z": [1, 2], "a": True}},
    }
    values.update(overrides)
    return GenerationRequest(**values)


def test_request_is_deeply_immutable_and_copies_inputs() -> None:
    nested = {"items": ["C03", {"inner": 4}]}
    options = {"namespace": "probe", "version": 1, "values": nested}
    request = make_request(generator_options=options)
    nested["items"].append("changed")
    assert request.options.values["items"] == ("C03", {"inner": 4})
    with pytest.raises(TypeError):
        request.options.values["new"] = 1  # type: ignore[index]
    with pytest.raises((AttributeError, TypeError)):
        request.generator_options = GeneratorOptions()  # type: ignore[misc]


def test_canonical_serialization_is_compact_sorted_and_order_independent() -> None:
    first = make_request(generator_options={"namespace": "probe", "version": 1, "values": {"b": 2, "a": 1}})
    second = make_request(generator_options={"namespace": "probe", "version": 1, "values": {"a": 1, "b": 2}})
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.canonical_bytes() == first.canonical_json().encode("utf-8")
    assert " " not in first.canonical_json()
    assert json.loads(first.canonical_json())["seed"] == {"type": "int", "value": 1}


def test_typed_seed_prevents_integer_string_collision() -> None:
    assert make_request(seed=1).canonical_bytes() != make_request(seed="1").canonical_bytes()


def test_empty_string_seed_preserves_m01_domain_and_is_typed() -> None:
    request = make_request(seed="")
    assert json.loads(request.canonical_json())["seed"] == {"type": "string", "value": ""}


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), {"bad"}, b"bytes", object()])
def test_generator_options_reject_non_canonical_values(bad) -> None:
    with pytest.raises(RequestContractError):
        make_request(generator_options={"namespace": "probe", "version": 1, "values": {"bad": bad}})


@pytest.mark.parametrize("kwargs", [
    {"width": 19},
    {"height": 60},
    {"palette_subset": ["C01", "C02"]},
    {"schema_version": 3},
    {"style": "   "},
])
def test_request_validation_is_strict(kwargs) -> None:
    with pytest.raises(RequestContractError):
        make_request(**kwargs)


def test_partial_dimensions_resolve_without_clamping() -> None:
    request = make_request(difficulty="HARD", width=48)
    width, height = request.resolve_dimensions()
    assert width == 48 and 20 <= height <= 59


def test_current_request_schema_is_v2_and_legacy_v1_replays_old_omitted_axis_semantics() -> None:
    current = make_request(difficulty="EASY", seed="migration")
    legacy = make_request(difficulty="EASY", seed="migration", schema_version=1)
    assert current.schema_version == 2
    assert current.canonical_dict()["schema_version"] == 2
    assert legacy.canonical_dict()["schema_version"] == 1
    assert current.resolve_dimensions() != legacy.resolve_dimensions()
    assert all(20 <= value <= 59 for value in current.resolve_dimensions())
    assert all(20 <= value <= 29 for value in legacy.resolve_dimensions())


def test_current_request_allows_cross_band_rectangles_for_every_difficulty() -> None:
    for difficulty in ("EASY", "MEDIUM", "HARD", "VERY_HARD"):
        request = make_request(difficulty=difficulty, width=20, height=59)
        assert request.resolve_dimensions() == (20, 59)
