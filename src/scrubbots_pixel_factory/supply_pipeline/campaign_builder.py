"""Deterministic CampaignBuilder over an owner-approved Release Pool."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .progression import describe_target


class CampaignError(ValueError):
    pass


_DIFFICULTY_PROFILES = {"FLOW", "COLOR", "FORTRESS", "ROUTE", "MARATHON", "BALANCED"}


def _tolerance_policy(authority: Mapping[str, Any]) -> tuple[float, float, float]:
    values = authority.get("challengeTolerance")
    if not isinstance(values, Mapping):
        raise CampaignError("current challengeTolerance authority is missing or malformed")
    names = ("preferredWhenPoolIsLarge", "defaultPlusMinus", "neverForceLabelOutsidePlusMinus")
    parsed: list[float] = []
    for name in names:
        value = values.get(name)
        if type(value) not in {int, float} or not math.isfinite(float(value)) or float(value) < 0:
            raise CampaignError(f"current challengeTolerance.{name} must be a finite nonnegative number")
        parsed.append(float(value))
    preferred, default, hard = parsed
    if not preferred <= default <= hard:
        raise CampaignError("current challengeTolerance values must satisfy preferred <= default <= hard")
    return preferred, default, hard


def _recovery_target_slots(authority: Mapping[str, Any]) -> set[int]:
    guards = authority.get("recoveryGuards")
    if not isinstance(guards, list):
        raise CampaignError("current recoveryGuards authority is missing or malformed")
    targets: set[int] = set()
    for index, guard in enumerate(guards):
        if not isinstance(guard, Mapping):
            raise CampaignError(f"current recoveryGuards[{index}] is malformed")
        from_slot = guard.get("fromSlot")
        drop = guard.get("minimumChallengeDrop")
        if type(from_slot) is not int or from_slot < 1 or type(drop) not in {int, float} or not math.isfinite(float(drop)) or float(drop) < 0:
            raise CampaignError(f"current recoveryGuards[{index}] has malformed source slot or challenge drop")
        destinations = [guard[key] for key in ("toSlot", "toNextCycleSlot") if key in guard]
        if not destinations or any(type(slot) is not int or slot < 1 for slot in destinations):
            raise CampaignError(f"current recoveryGuards[{index}] has no valid target slot")
        targets.update(destinations)
    return targets


def _bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_bytes(value)).hexdigest()


def _similarity(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    a, b = left.get("signature", {}), right.get("signature", {})
    a = a if isinstance(a, Mapping) else {}; b = b if isinstance(b, Mapping) else {}
    va, vb = a.get("challengeVector", left.get("challenge_vector", [])), b.get("challengeVector", right.get("challenge_vector", []))
    vector = 0.0
    if isinstance(va, Sequence) and isinstance(vb, Sequence) and len(va) == len(vb) == 7:
        vector = max(0.0, 1.0 - math.dist([float(x) for x in va], [float(x) for x in vb]) / math.sqrt(7))
    ca, cb = set(a.get("paletteSet", left.get("palette", []))), set(b.get("paletteSet", right.get("palette", [])))
    palette = len(ca & cb) / len(ca | cb) if ca | cb else 1.0
    da, db = a.get("dimensions", [left.get("width"), left.get("height")]), b.get("dimensions", [right.get("width"), right.get("height")])
    area_a = math.prod(da) if isinstance(da, Sequence) and len(da) == 2 else 0
    area_b = math.prod(db) if isinstance(db, Sequence) and len(db) == 2 else 0
    dimensions = min(area_a, area_b) / max(area_a, area_b) if area_a and area_b else 0.0
    return (vector + palette + dimensions) / 3.0


def _eligible(item: Mapping[str, Any], target: Mapping[str, Any], tolerance: float, envelope: Mapping[str, int]) -> bool:
    score = item.get("challenge_score")
    label = item.get("difficulty_class")
    width, height = item.get("width"), item.get("height")
    colors = item.get("used_colors", item.get("palette", []))
    return (type(score) in {int, float} and math.isfinite(float(score)) and abs(float(score) - float(target["target_challenge"])) <= tolerance and label == target["class"]
        and type(width) is int and type(height) is int and envelope["min_dimension"] <= width <= envelope["max_dimension"] and envelope["min_dimension"] <= height <= envelope["max_dimension"]
        and isinstance(colors, Sequence) and envelope["min_colors"] <= len(set(colors)) <= envelope["max_colors"])


def _assignment(costs: list[list[int]]) -> list[int]:
    """Rectangular Hungarian algorithm. Returns one column for each row."""
    n = len(costs)
    if not n: return []
    m = len(costs[0])
    u = [0] * (n + 1); v = [0] * (m + 1); p = [0] * (m + 1); way = [0] * (m + 1)
    for i in range(1, n + 1):
        p[0] = i; j0 = 0; minv = [10**30] * (m + 1); used = [False] * (m + 1)
        while True:
            used[j0] = True; i0 = p[j0]; delta = 10**30; j1 = 0
            for j in range(1, m + 1):
                if used[j]: continue
                cur = costs[i0 - 1][j - 1] - u[i0] - v[j]
                if cur < minv[j]: minv[j] = cur; way[j] = j0
                if minv[j] < delta or minv[j] == delta and j < j1: delta = minv[j]; j1 = j
            for j in range(m + 1):
                if used[j]: u[p[j]] += delta; v[j] -= delta
                else: minv[j] -= delta
            j0 = j1
            if p[j0] == 0: break
        while True:
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
            if j0 == 0: break
    result = [-1] * n
    for j in range(1, m + 1):
        if p[j]: result[p[j] - 1] = j - 1
    return result


def build_campaign_plan(*, catalog: Mapping[str, Any], authority: Mapping[str, Any], pool: Sequence[Mapping[str, Any]], k: int = 100, locks: Mapping[int, str] | None = None) -> dict[str, Any]:
    if type(k) is not int or not 1 <= k <= 1000: raise CampaignError("K must be an integer from 1 through 1000")
    entries = catalog.get("entries")
    if not isinstance(entries, list): raise CampaignError("production catalog is malformed")
    orders = [item.get("order") for item in entries if isinstance(item, Mapping)]
    start = max((int(n) for n in orders if type(n) is int), default=0) + 1
    preferred, default, hard = _tolerance_policy(authority)
    recovery_targets = _recovery_target_slots(authority)
    envelope = authority.get("_production_envelope")
    if not isinstance(envelope, Mapping) or set(envelope) != {"min_dimension", "max_dimension", "min_colors", "max_colors"}:
        raise CampaignError("current game production envelope is unavailable")
    slots = [describe_target(n, authority) for n in range(start, start + k)]
    candidates = sorted((dict(item) for item in pool), key=lambda x: str(x.get("candidate_id", "")))
    ids = [str(x.get("candidate_id", "")) for x in candidates]
    if len(ids) != len(set(ids)): raise CampaignError("Release Pool contains duplicate candidate identities")
    for identity, item in zip(ids, candidates):
        if not identity or type(item.get("challenge_score")) not in {int, float} or not math.isfinite(float(item["challenge_score"])):
            raise CampaignError("Release Pool identity or official challenge score is invalid")
        if item.get("dominant_profile") not in _DIFFICULTY_PROFILES:
            raise CampaignError("Release Pool official Difficulty V1 profile is missing or malformed")
        vector = item.get("challenge_vector")
        if not isinstance(vector, Sequence) or len(vector) != 7 or any(type(value) not in {int, float} or not math.isfinite(float(value)) for value in vector):
            raise CampaignError("Release Pool official Difficulty V1 challenge vector is missing or malformed")
    blocked: set[tuple[int, str]] = set()
    tail = authority.get("_catalog_tail")
    if tail is None:
        catalog_history: list[dict[str, Any]] = []
    elif isinstance(tail, Mapping):
        catalog_history = [dict(tail)]
    elif isinstance(tail, Sequence) and not isinstance(tail, (str, bytes)) and all(isinstance(record, Mapping) for record in tail):
        catalog_history = [dict(record) for record in tail]
    else:
        raise CampaignError("current catalog tail Difficulty V1 evidence is malformed")
    if len(catalog_history) > 2:
        catalog_history = catalog_history[-2:]
    existing_count = len(entries)
    required_history = min(existing_count, 2)
    if len(catalog_history) < required_history:
        raise CampaignError("CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE: official history for the final existing catalog levels is incomplete")
    for record in catalog_history:
        if (record.get("dominant_profile") not in _DIFFICULTY_PROFILES
            or type(record.get("challenge_score")) not in {int, float}
            or not math.isfinite(float(record["challenge_score"]))
            or not isinstance(record.get("challenge_vector"), Sequence)
            or len(record["challenge_vector"]) != 7
            or any(type(value) not in {int, float} or not math.isfinite(float(value)) for value in record["challenge_vector"])
            or not isinstance(record.get("signature"), Mapping)):
            raise CampaignError("CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE: official profile, score, vector, or signature is missing")
    previous_catalog = catalog_history[-1] if catalog_history else None
    lock_map = dict(locks or {})
    slot_indices = {int(slot["level"]): i for i, slot in enumerate(slots)}
    if any(type(number) is not int or number not in slot_indices for number in lock_map): raise CampaignError("locked slot is outside the requested campaign range")
    if len(set(lock_map.values())) != len(lock_map): raise CampaignError("one Release Pool candidate cannot be locked to multiple slots")
    candidate_indices = {identity: i for i, identity in enumerate(ids)}
    for number, identity in lock_map.items():
        if identity not in candidate_indices or not _eligible(candidates[candidate_indices[identity]], slots[slot_indices[number]], hard, envelope): raise CampaignError("locked candidate fails current class, envelope, or hard-tolerance eligibility")
    assigned: list[int] = []
    checks: dict[int, dict[str, Any]] = {}
    # Resolve sequential constraints by excluding the offending edge, then re-run
    # the global assignment. Every retry strictly removes an edge, so it ends.
    for _ in range(max(1, k * max(1, len(candidates)) + 1)):
        width = len(candidates) + len(slots)
        costs: list[list[int]] = []
        for si, target in enumerate(slots):
            row = []
            for ci, item in enumerate(candidates):
                delta = abs(float(item["challenge_score"]) - float(target["target_challenge"]))
                tier_penalty = 0 if delta <= preferred else 2000 if delta <= default else 8000
                lock_for_slot = lock_map.get(int(target["level"]))
                locked_elsewhere = ids[ci] in lock_map.values() and lock_for_slot != ids[ci]
                row.append(10**12 if not _eligible(item, target, hard, envelope) or (si, ids[ci]) in blocked or locked_elsewhere or lock_for_slot is not None and ids[ci] != lock_for_slot else round(delta * 1000) * 100 + tier_penalty + ci)
            row.extend([10**9 + di for di in range(len(slots))])
            costs.append(row)
        assigned = _assignment(costs)
        chosen: list[dict[str, Any] | None] = [candidates[col] if 0 <= col < len(candidates) and costs[i][col] < 10**9 else None for i, col in enumerate(assigned)]
        violation = None; checks = {}
        for i, (slot, item) in enumerate(zip(slots, chosen)):
            if item is None: continue
            prev = chosen[i - 1] if i else previous_catalog
            profile = str(item["dominant_profile"])
            prior_sequence = catalog_history + [entry for entry in chosen[:i]]
            same_run = 1
            for prior_item in reversed(prior_sequence):
                if prior_item is None or prior_item.get("dominant_profile") != profile:
                    break
                same_run += 1
            recovery = int(slot["slot"]) in recovery_targets
            guard_ok = True
            guards = authority.get("recoveryGuards", [])
            for guard in guards:
                from_slot = guard.get("fromSlot")
                previous_slot = slots[i - 1]["slot"] if i > 0 else (previous_catalog.get("slot") if previous_catalog else None)
                destinations = [guard[key] for key in ("toSlot", "toNextCycleSlot") if key in guard]
                if slot["slot"] in destinations and previous_slot == from_slot and prev is not None:
                    guard_ok &= float(prev["challenge_score"]) - float(item["challenge_score"]) >= float(guard["minimumChallengeDrop"])
            # Profile rotation/recovery use measured pool medians, not copied score bands.
            vector = item.get("challenge_vector", [0] * 7)
            def metric(candidate: Mapping[str, Any], index: int) -> float:
                values = candidate.get("challenge_vector", [])
                return float(values[index]) if isinstance(values, Sequence) and len(values) > index else 0.0
            w_median = sorted(metric(c, 0) for c in candidates)[len(candidates)//2] if candidates else 0.0
            u_median = sorted(metric(c, 3) for c in candidates)[len(candidates)//2] if candidates else 0.0
            b_median = sorted(metric(c, 4) for c in candidates)[len(candidates)//2] if candidates else 0.0
            low_b_recovery_ok = not recovery or metric(item, 4) <= b_median
            low_u_recovery_ok = not recovery or metric(item, 3) <= u_median
            high_w_adjacency_ok = prev is None or not (metric(item, 0) > w_median and metric(prev, 0) > w_median)
            high_b_adjacency_ok = prev is None or not (metric(item, 4) > b_median and metric(prev, 4) > b_median)
            profile_ok = same_run <= 2 and low_b_recovery_ok and low_u_recovery_ok and high_w_adjacency_ok and high_b_adjacency_ok
            similarity = _similarity(prev, item) if prev else 0.0
            novelty = 1.0 - similarity
            novelty_ok = novelty + 1e-12 >= float(slot.get("novelty_target", 0.0))
            limit = authority.get("campaignBuilder", {}).get("maxConsecutiveSimilarity") if isinstance(authority.get("campaignBuilder"), Mapping) else None
            similarity_ok = True if limit is None else similarity < float(limit)
            checks[i] = {"recovery_guard": guard_ok, "recovery_profile_target_slot": recovery, "profile": profile_ok, "profile_run_ok": same_run <= 2, "high_w_adjacency_ok": high_w_adjacency_ok, "high_b_adjacency_ok": high_b_adjacency_ok, "low_u_recovery_ok": low_u_recovery_ok, "low_b_recovery_ok": low_b_recovery_ok, "profile_medians": {"W": w_median, "U": u_median, "B": b_median}, "similarity": similarity, "novelty_score": novelty, "novelty_target": float(slot.get("novelty_target", 0.0)), "novelty_ok": novelty_ok, "similarity_ok": similarity_ok, "similarity_limit_configured": limit is not None}
            if not guard_ok or not profile_ok or not similarity_ok or not novelty_ok:
                if int(slot["level"]) in lock_map: raise CampaignError("locked candidate violates a current sequence constraint")
                violation = (i, str(item["candidate_id"])); break
        if violation is None: break
        blocked.add(violation)
    chosen = [candidates[col] if 0 <= col < len(candidates) and costs[i][col] < 10**9 else None for i, col in enumerate(assigned)]
    used: set[str] = set(); rows = []; shortages = []; stopped = False
    for i, (slot, item) in enumerate(zip(slots, chosen)):
        if item is not None and str(item["candidate_id"]) in used: item = None
        if item is None or stopped:
            stopped = True
            nearest = sorted((c for c in candidates if str(c["candidate_id"]) not in used), key=lambda x: (abs(float(x["challenge_score"]) - float(slot["target_challenge"])), str(x["candidate_id"])))
            rejected = []
            prior_item = next((candidate for candidate in candidates if rows and candidate["candidate_id"] == rows[-1].get("chosen_id")), previous_catalog if not rows else None)
            for candidate in nearest[:5]:
                score = float(candidate["challenge_score"]); reasons = []
                if candidate.get("difficulty_class") != slot["class"]: reasons.append("class mismatch")
                if abs(score - float(slot["target_challenge"])) > hard: reasons.append("outside hard tolerance")
                colors = candidate.get("used_colors", candidate.get("palette", []))
                if type(candidate.get("width")) is not int or type(candidate.get("height")) is not int or not (envelope["min_dimension"] <= candidate["width"] <= envelope["max_dimension"] and envelope["min_dimension"] <= candidate["height"] <= envelope["max_dimension"]) or not isinstance(colors, Sequence) or not (envelope["min_colors"] <= len(set(colors)) <= envelope["max_colors"]): reasons.append("outside current production envelope")
                if (i, str(candidate["candidate_id"])) in blocked: reasons.append("recovery/profile/similarity constraint")
                if prior_item is not None and 1.0 - _similarity(prior_item, candidate) < float(slot.get("novelty_target", 0.0)): reasons.append("below slot novelty target")
                if not reasons: reasons.append("sequential guard or similarity constraint")
                rejected.append({"candidate_id": candidate["candidate_id"], "score": score, "reasons": reasons})
            shortages.append({"n": slot["level"], "class": slot["class"], "target": slot["target_challenge"], "allowed_range": [float(slot["target_challenge"])-hard, float(slot["target_challenge"])+hard], "nearest_unused_candidates": rejected})
            rows.append({"n": slot["level"], "slot": slot["slot"], "class": slot["class"], "role": slot["role"], "target": slot["target_challenge"], "chosen_id": None, "D": None, "delta": None, "tier": None, "checks": checks.get(i, {})})
            continue
        used.add(str(item["candidate_id"])); delta = abs(float(item["challenge_score"]) - float(slot["target_challenge"]))
        tier = 0 if delta <= preferred else 1 if delta <= default else 2
        rows.append({"n": slot["level"], "slot": slot["slot"], "class": slot["class"], "role": slot["role"], "target": slot["target_challenge"], "chosen_id": item["candidate_id"], "D": item["challenge_score"], "delta": delta, "tier": tier, "checks": checks.get(i, {})})
    pool_digest = _digest([{k: item.get(k) for k in sorted(item) if k not in {"pipeline", "source_bundle"}} for item in candidates])
    body = {"schema": "scrubbots-campaign-plan/v1", "inputs": {"catalog_digest": _digest(catalog), "authority_digest": _digest(authority), "pool_digest": pool_digest}, "K": k, "slots": rows, "shortages": shortages, "publishable_prefix": [r["n"] for r in rows if r["chosen_id"] is not None][:next((i for i,r in enumerate(rows) if r["chosen_id"] is None),len(rows))], "warnings": []}
    if any(not row.get("checks", {}).get("similarity_limit_configured", True) for row in rows if row.get("chosen_id")):
        body["warnings"].append("Current game authority does not configure a consecutive similarity maximum; similarity is reported using the game analyzer formula without rejecting candidates.")
    body["warnings"].append("Current game analysis authority does not provide a supported scalar Frustration Risk; high-F sequencing cannot be enforced from available official data.")
    body["plan_hash"] = _digest(body)
    return body


def write_campaign_plan(path: str | Path, plan: Mapping[str, Any]) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(_bytes(plan))
    return destination


__all__ = ["CampaignError", "build_campaign_plan", "write_campaign_plan"]
