import pytest

from scrubbots_pixel_factory.core import DeterministicRNG, RNG_ALGORITHM, RNGContractError, STAGE_DOMAINS


def test_rng_identity_and_known_vector() -> None:
    rng = DeterministicRNG(123, "root")
    assert RNG_ALGORITHM == "SCRUBBOTS_SHA256_COUNTER_V1"
    assert rng.next_u64() == 801623960106958567


def test_rng_same_seed_domain_and_call_order_properties() -> None:
    assert DeterministicRNG(5).next_bytes(64) == DeterministicRNG(5).next_bytes(64)
    assert DeterministicRNG(5).next_bytes(32) != DeterministicRNG(6).next_bytes(32)
    assert DeterministicRNG(5, "a").next_bytes(32) != DeterministicRNG(5, "b").next_bytes(32)
    left = DeterministicRNG(5)
    left.next_bytes(100)
    assert left.stage_seed("geometry") == DeterministicRNG(5).stage_seed("geometry")


def test_empty_string_seed_is_deterministic_and_typed_distinct() -> None:
    assert DeterministicRNG("").next_bytes(32) == DeterministicRNG("").next_bytes(32)
    assert DeterministicRNG("").next_bytes(32) != DeterministicRNG(0).next_bytes(32)
    assert DeterministicRNG("").next_bytes(32) != DeterministicRNG("0").next_bytes(32)


def test_randbelow_choice_and_shuffle_are_bounded_and_ordered() -> None:
    rng = DeterministicRNG(9)
    values = [rng.randbelow(7) for _ in range(1000)]
    assert all(0 <= value < 7 for value in values)
    assert rng.choice(("a", "b", "c")) in {"a", "b", "c"}
    shuffled = rng.shuffle(("a", "b", "c", "d"))
    assert sorted(shuffled) == ["a", "b", "c", "d"]


def test_stage_and_retry_seeds_are_stable_distinct_and_call_order_independent() -> None:
    first = DeterministicRNG("seed")
    second = DeterministicRNG("seed")
    assert first.stage_seeds() == second.stage_seeds()
    assert len(set(first.stage_seeds().values())) == len(STAGE_DOMAINS)
    assert first.retry_seed(0) == second.retry_seed(0)
    assert first.retry_seed(0) != first.retry_seed(1)
    assert first.stage_rng("geometry").next_bytes(16) == second.stage_rng("geometry").next_bytes(16)


@pytest.mark.parametrize("call", [lambda: DeterministicRNG(1).randbelow(0), lambda: DeterministicRNG(1).randbelow(-1), lambda: DeterministicRNG(1).retry_seed(-1), lambda: DeterministicRNG(1).stage_seed("unknown")])
def test_invalid_rng_inputs_fail_closed(call) -> None:
    with pytest.raises(RNGContractError):
        call()
