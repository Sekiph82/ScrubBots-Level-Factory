"""F7: one release_entries() listing verifies the attested runtime once per column
count; calls outside a listing still verify on every use."""
import threading

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
    assert getattr(release_pool._PINNED_RULES, "scope", None) is None

    release_pool._validate_score_and_class(primary, official, {"kind": "DIRECT"})
    release_pool._validate_score_and_class(primary, official, {"kind": "DIRECT"})
    assert built == [4, 4, 4]


def test_parallel_listings_do_not_leak_a_scope_into_later_calls(monkeypatch) -> None:
    # Parallel batch workers (2026-11-12): a module-global scope let one thread
    # restore another thread's cache dict after both listings ended.
    monkeypatch.setattr(game_rules, "GameRules", lambda _root, column_count=None: object())
    a_inside, b_inside, a_done = threading.Event(), threading.Event(), threading.Event()

    def listing(_filter=None):
        if threading.current_thread().name == "a":
            a_inside.set()
            b_inside.wait(5)
        else:
            a_inside.wait(5)
            b_inside.set()
            a_done.wait(5)
        return []

    monkeypatch.setattr(release_pool, "_release_entries", listing)
    threads = {name: threading.Thread(target=release_pool.release_entries, name=name) for name in ("a", "b")}
    threads["a"].start()
    threads["b"].start()
    threads["a"].join(5)  # listing A ends while listing B is still open
    a_done.set()
    threads["b"].join(5)
    leaked: list[object] = []
    probe = threading.Thread(target=lambda: leaked.append(getattr(release_pool._PINNED_RULES, "scope", None)))
    probe.start()
    probe.join()
    assert leaked == [None]
    assert getattr(release_pool._PINNED_RULES, "scope", None) is None
