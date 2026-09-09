import pytest

from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCConfig, WFCContractError


def _exemplar(ownership="SYNTHETIC_TEST_ONLY", role="TRAINING_MOTIF", approved_by=None, difficulty=None):
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, "fixture", role, 3, 3,
        ("C01", "C02", "C03", "C02", "C03", "C01", "C03", "C01", "C02"),
        "test", "project-authored fixture", ownership, approved_by, difficulty,
    )


def test_exemplar_rejects_presentation_and_noncanonical_cells() -> None:
    with pytest.raises(WFCContractError):
        Exemplar("scrubbots-wfc-exemplar", 1, "bad", "TRAINING_MOTIF", 2, 2, ("BG01",) * 4, "test", "x", "SYNTHETIC_TEST_ONLY")
    with pytest.raises(WFCContractError):
        Exemplar("scrubbots-wfc-exemplar", 1, "bad", "TRAINING_MOTIF", 2, 2, ("C17",) * 4, "test", "x", "SYNTHETIC_TEST_ONLY")
    with pytest.raises(WFCContractError):
        Exemplar("scrubbots-wfc-exemplar", 1, "bad", "TRAINING_MOTIF", 2, 2, ((1, 2, 3),) * 4, "test", "x", "SYNTHETIC_TEST_ONLY")


def test_registry_is_ordered_and_production_default_is_empty() -> None:
    assert ExemplarRegistry().exemplars == ()
    one = _exemplar()
    two = Exemplar(**{**one.__dict__, "exemplar_id": "another"}) if hasattr(one, "__dict__") else Exemplar(
        one.schema, one.version, "another", one.role, one.width, one.height, one.pixels,
        one.provenance_type, one.provenance_description, one.ownership,
    )
    registry = ExemplarRegistry((one, two))
    assert tuple(item.exemplar_id for item in registry.exemplars) == ("another", "fixture")
    assert registry.get("fixture") is one
    assert registry.eligible() == registry.exemplars


def test_owner_approval_and_production_difficulty_are_explicit() -> None:
    with pytest.raises(WFCContractError):
        _exemplar(ownership="OWNER_APPROVED")
    approved = _exemplar(ownership="OWNER_APPROVED", approved_by="owner")
    assert approved in ExemplarRegistry((approved,)).eligible()
    with pytest.raises(WFCContractError):
        _exemplar(role="PRODUCTION_ARTIFACT")


def _production(width: int, height: int, difficulty: str) -> Exemplar:
    return Exemplar(
        "scrubbots-wfc-exemplar", 1, f"production-{difficulty}-{width}x{height}", "PRODUCTION_ARTIFACT", width, height,
        tuple(("C01", "C02", "C03")[(x + y) % 3] for y in range(height) for x in range(width)),
        "owner", "owner-locked validation fixture", "OWNER_APPROVED", "test-owner", difficulty,
    )


def test_production_exemplar_dimensions_reuse_m01_contract() -> None:
    for width, height, difficulty in ((20, 20, "EASY"), (29, 23, "EASY"), (30, 39, "MEDIUM"), (48, 41, "HARD"), (59, 50, "VERY_HARD")):
        assert _production(width, height, difficulty).production_difficulty == difficulty
    for width, height in ((19, 20), (20, 30)):
        with pytest.raises(WFCContractError):
            _production(width, height, "EASY")
    with pytest.raises(WFCContractError):
        _exemplar(role="PRODUCTION_ARTIFACT", difficulty=None)
    assert _exemplar().width == 3


def test_wfc_config_gates_n4_and_bounds_attempts() -> None:
    with pytest.raises(WFCContractError):
        WFCConfig(pattern_size=4)
    with pytest.raises(WFCContractError):
        WFCConfig(pattern_size=2, experimental_n4=True)
    with pytest.raises(WFCContractError):
        WFCConfig(pattern_size=3, max_attempts=9)
    assert WFCConfig(pattern_size=4, experimental_n4=True).pattern_size == 4
