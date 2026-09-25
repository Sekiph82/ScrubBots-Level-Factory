from __future__ import annotations

from scrubbots_pixel_factory import (
    AuthorityIdentity,
    CANONICAL_GAMEPLAY_REPOSITORY,
    CANONICAL_M23_CONTRACT_VERSION,
    CANONICAL_M23_SOURCE_PATH,
    CANONICAL_M39_CONTRACT_VERSION,
    CANONICAL_M39_SOURCE_PATH,
    MutationEngine,
    canonical_mutation_registry,
)


CURRENT_MAIN_SHA = "281ea38218aaf24ab88c70e998f59b14df9d1c97"
M23_BLOB_SHA = "0c13300a02d4e8b1cf04cd701d488a0bc897395b23f8ef6d2ddbb215b1bb140b"
M39_BLOB_SHA = "67096958a85b2a295ce3b574bacadec4a12e9e0badc8516f002901aa437e0518"


def m23_authority() -> AuthorityIdentity:
    return AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CURRENT_MAIN_SHA, CANONICAL_M23_SOURCE_PATH, CANONICAL_M23_CONTRACT_VERSION, M23_BLOB_SHA)


def m39_authority() -> AuthorityIdentity:
    return AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, CURRENT_MAIN_SHA, CANONICAL_M39_SOURCE_PATH, CANONICAL_M39_CONTRACT_VERSION, M39_BLOB_SHA)


def engine() -> MutationEngine:
    return MutationEngine(canonical_mutation_registry(m23_authority=m23_authority(), m39_authority=m39_authority()))
