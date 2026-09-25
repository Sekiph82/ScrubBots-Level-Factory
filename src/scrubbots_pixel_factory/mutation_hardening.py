"""SB-LF07-002 authority-bound canonical hardening service."""

from collections.abc import Mapping

from .mutation_base import AuthorityIdentity, MutationDisposition, MutationIntent, MutationOperator, MutationRegistry
from .m07_services import (
    CANONICAL_M39_CONTRACT_VERSION,
    CANONICAL_M39_SOURCE_PATH,
    _allowed_gameplay_change,
    _copy_payload,
    _gameplay,
)

OPERATOR_ID = "CANONICAL_PLUS_ONE_SLOT_ROLLBACK_HARDEN_V1"
OPERATOR_VERSION = "1"


def rollback_sixth_slot(payload: Mapping[str, object]) -> tuple[MutationDisposition, Mapping[str, object] | None, str]:
    gameplay = _gameplay(payload)
    if gameplay is None or type(gameplay.get("slot_capacity")) is not int:
        return MutationDisposition.INAPPLICABLE, None, "canonical M39 slot capacity state is absent"
    if gameplay.get("booster") != "+1_SLOT":
        return MutationDisposition.INAPPLICABLE, None, "canonical +1 Slot booster identity is not present"
    if gameplay.get("sixth_slot_state") != "EMPTY" or gameplay.get("live_work_on_sixth", 0) != 0:
        return MutationDisposition.INAPPLICABLE, None, "canonical M39 rollback requires an empty, uncommitted sixth slot"
    if int(gameplay["slot_capacity"]) != 6:
        return (MutationDisposition.NO_CHANGE, None, "canonical M39 rollback requires active six-slot capacity") if int(gameplay["slot_capacity"]) == 5 else (MutationDisposition.ERROR, None, "canonical M39 slot capacity bounds are invalid")
    gameplay["slot_capacity"] = 5
    out = _copy_payload(payload)
    out["gameplay"] = gameplay
    if not _allowed_gameplay_change(_gameplay(payload) or {}, gameplay, "slot_capacity"):
        return MutationDisposition.ERROR, None, "hardening rollback changed an unauthorized gameplay field"
    return MutationDisposition.APPLIED, out, "rolled back the canonical M39 uncommitted temporary sixth slot to the five-slot baseline"


def build_hardening_registry(authority: AuthorityIdentity) -> MutationRegistry:
    if not isinstance(authority, AuthorityIdentity) or authority.commit_sha == "UNAVAILABLE" or authority.source_blob_sha256 is None:
        return MutationRegistry()
    if authority.source_path != CANONICAL_M39_SOURCE_PATH or authority.contract_version != CANONICAL_M39_CONTRACT_VERSION:
        return MutationRegistry()
    registry = MutationRegistry()
    registry._install(MutationOperator(OPERATOR_ID, OPERATOR_VERSION, MutationIntent.HARDEN, authority, "rollback_sixth_slot"), rollback_sixth_slot)
    return registry


__all__ = ["OPERATOR_ID", "OPERATOR_VERSION", "build_hardening_registry", "rollback_sixth_slot"]
