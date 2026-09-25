"""Task-time authority and R02 service support; no batch-pinned SHA."""

import hashlib
import subprocess
from urllib.error import URLError
from urllib.request import urlopen

from scrubbots_pixel_factory import (
    AuthorityIdentity,
    CANONICAL_GAMEPLAY_REPOSITORY,
    CANONICAL_M39_CONTRACT_VERSION,
    CANONICAL_M39_SOURCE_PATH,
)


def fresh_m39_authority() -> AuthorityIdentity:
    try:
        sha = subprocess.check_output(
            ["git", "ls-remote", "https://github.com/Sekiph82/ScrubBots.git", "refs/heads/main"],
            text=True,
        ).split()[0]
        raw_url = f"https://raw.githubusercontent.com/Sekiph82/ScrubBots/{sha}/{CANONICAL_M39_SOURCE_PATH}"
        with urlopen(raw_url, timeout=20) as response:
            blob = response.read()
    except (OSError, subprocess.CalledProcessError, TimeoutError, URLError, ValueError) as exc:
        raise RuntimeError(f"current ScrubBots main authority is UNAVAILABLE: {exc}") from exc
    return AuthorityIdentity(CANONICAL_GAMEPLAY_REPOSITORY, sha, CANONICAL_M39_SOURCE_PATH, CANONICAL_M39_CONTRACT_VERSION, hashlib.sha256(blob).hexdigest())


__all__ = ["fresh_m39_authority"]
