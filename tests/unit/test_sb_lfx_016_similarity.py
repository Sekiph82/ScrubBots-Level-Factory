from __future__ import annotations

from scrubbots_pixel_factory.studio_extensions import similarity


def test_similarity_is_deterministic_advisory_and_keeps_exact_duplicates_separate() -> None:
    left = {"candidate_id": "left", "width": 20, "height": 20, "cells": ["C01"] * 400, "grid_hash": "same"}
    exact = similarity(left, {**left, "candidate_id": "exact"})
    assert exact["disposition"] == "EXACT_DUPLICATE"
    near_cells = list(left["cells"]); near_cells[0] = "C02"
    near = similarity(left, {"candidate_id": "near", "width": 20, "height": 20, "cells": near_cells, "grid_hash": "near"})
    assert near["disposition"] == "POSSIBLE_SIMILAR"
    assert near["advisory"] is True
    different = similarity(left, {"candidate_id": "different", "width": 20, "height": 20, "cells": ["C02"] * 400, "grid_hash": "different"})
    assert different["disposition"] == "DISTINCT"
