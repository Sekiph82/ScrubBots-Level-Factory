"""SB-LF07-003 authority-bound canonical easing service."""

from collections.abc import Mapping

from .mutation_base import AuthorityIdentity, MutationDisposition, MutationIntent, MutationOperator, MutationRegistry
from .m07_services import CANONICAL_M39_CONTRACT_VERSION, CANONICAL_M39_SOURCE_PATH, _allowed_gameplay_change, _copy_payload, _gameplay

OPERATOR_ID = "CANONICAL_PLUS_ONE_SLOT_EASE_V1"
OPERATOR_VERSION = "1"


def activate_sixth_slot(payload: Mapping[str, object]) -> tuple[MutationDisposition, Mapping[str, object] | None, str]:
    gameplay = _gameplay(payload)
    if gameplay is None or type(gameplay.get("slot_capacity")) is not int:
        return MutationDisposition.INAPPLICABLE, None, "canonical M39 slot capacity state is absent"
    if gameplay.get("booster") != "+1_SLOT":
        return MutationDisposition.INAPPLICABLE, None, "canonical +1 Slot booster is not explicitly present"
    capacity = int(gameplay["slot_capacity"])
    if capacity < 5 or capacity > 6:
        return MutationDisposition.ERROR, None, "canonical M39 slot capacity bounds are invalid"
    if capacity == 6:
        return MutationDisposition.NO_CHANGE, None, "canonical M39 temporary sixth slot is already active"
    gameplay["slot_capacity"] = 6
    out = _copy_payload(payload)
    out["gameplay"] = gameplay
    if not _allowed_gameplay_change(_gameplay(payload) or {}, gameplay, "slot_capacity"):
        return MutationDisposition.ERROR, None, "easing transform changed an unauthorized gameplay field"
    return MutationDisposition.APPLIED, out, "activated the canonical M39 temporary sixth slot"


def build_easing_registry(authority: AuthorityIdentity) -> MutationRegistry:
    if not isinstance(authority, AuthorityIdentity) or authority.commit_sha == "UNAVAILABLE" or authority.source_blob_sha256 is None:
        return MutationRegistry()
    if authority.source_path != CANONICAL_M39_SOURCE_PATH or authority.contract_version != CANONICAL_M39_CONTRACT_VERSION:
        return MutationRegistry()
    registry = MutationRegistry()
    registry._install(MutationOperator(OPERATOR_ID, OPERATOR_VERSION, MutationIntent.EASE, authority, "activate_sixth_slot"), activate_sixth_slot)
    return registry


__all__ = ["OPERATOR_ID", "OPERATOR_VERSION", "activate_sixth_slot", "build_easing_registry"]
