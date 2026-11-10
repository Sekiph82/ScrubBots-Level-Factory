"""F7: one release_entries() listing verifies the attested runtime once per column
count; calls outside a listing still verify on every use."""
from scrubbots_pixel_factory.supply_pipeline import game_rules, release_pool


def test_runtime_rules_built_once_per_listing_and_every_time_outside(monkeypatch) -> None:
    built: list[int] = []

    class FakeRules:
        def __init__(self, _root, column_count=None):
            built.append(column_count)

        def classify(self, _score):
            return "MEDIUM"

    monkeypatch.setattr(game_rules, "GameRules", FakeRules)
    primary = {"column_count": 4, "difficulty": {"score": 12.0, "class": "MEDIUM"}}
    official = {"challengeScore": 12.0}

    def listing(_filter=None):
        for _ in range(5):
            release_pool._validate_score_and_class(primary, official, {"kind": "DIRECT"})
        return []

    monkeypatch.setattr(release_pool, "_release_entries", listing)
    release_pool.release_entries()
    assert built == [4]
    assert release_pool._PINNED_RULES_SCOPE is None

    release_pool._validate_score_and_class(primary, official, {"kind": "DIRECT"})
    release_pool._validate_score_and_class(primary, official, {"kind": "DIRECT"})
    assert built == [4, 4, 4]
