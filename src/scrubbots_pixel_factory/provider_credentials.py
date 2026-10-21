"""Owner-local credential lookup for Factory Studio image providers.

PixelLab secrets are never persisted in repository files or passed in process
arguments. The supported Windows setup is a Generic Credential Manager entry
named ``ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN``.
"""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes


PIXELLAB_CREDENTIAL_TARGET = "ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN"


def _credential_manager_secret(target: str = PIXELLAB_CREDENTIAL_TARGET) -> str:
    if os.name != "nt":
        return ""

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

    class CREDENTIAL(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
            ("LastWritten", FILETIME), ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p), ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    credential_ptr = ctypes.POINTER(CREDENTIAL)()
    advapi32 = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
    advapi32.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
    advapi32.CredReadW.restype = wintypes.BOOL
    advapi32.CredFree.argtypes = [ctypes.c_void_p]
    advapi32.CredFree.restype = None
    if not advapi32.CredReadW(target, 1, 0, ctypes.byref(credential_ptr)):
        return ""
    try:
        credential = credential_ptr.contents
        if not credential.CredentialBlob or credential.CredentialBlobSize == 0:
            return ""
        raw = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
        try:
            return raw.decode("utf-8").strip()
        except UnicodeDecodeError:
            return raw.decode("utf-16-le").strip().rstrip("\x00")
    finally:
        advapi32.CredFree(credential_ptr)


def pixellab_secret_status() -> dict[str, str | bool]:
    """Return configuration state only; never expose the credential value."""
    token = os.environ.get("PIXELLAB_API_TOKEN", "").strip()
    legacy = os.environ.get("PIXELLAB_SECRET", "").strip()
    if token and legacy and token != legacy:
        return {"configured": False, "status": "PIXELLAB_CREDENTIALS_CONFLICT",
                "reason": "PIXELLAB_CREDENTIALS_CONFLICT: PIXELLAB_API_TOKEN and PIXELLAB_SECRET do not match."}
    if token or legacy:
        return {"configured": True, "status": "READY_CREDENTIALS_CONFIGURED",
                "reason": "PixelLab credential is present in the Studio worker. This checks configuration only, not account credits."}
    if _credential_manager_secret():
        return {"configured": True, "status": "READY_CREDENTIALS_CONFIGURED",
                "reason": "PixelLab credential is present in Windows Credential Manager. This checks configuration only, not account credits."}
    return {"configured": False, "status": "PIXELLAB_API_TOKEN_NOT_CONFIGURED",
            "reason": "PIXELLAB_API_TOKEN_NOT_CONFIGURED: In Windows Credential Manager, add a Generic Credential with address ScrubBotsFactoryStudio/PIXELLAB_API_TOKEN, user name token, and the PixelLab API token as password. Restart Studio, then reopen Provider to refresh. PixelLab Creator/MCP login is separate."}


def get_pixellab_secret() -> str:
    """Resolve a provider secret in memory for the explicitly requested call."""
    token = os.environ.get("PIXELLAB_API_TOKEN", "").strip()
    legacy = os.environ.get("PIXELLAB_SECRET", "").strip()
    if token and legacy and token != legacy:
        return ""
    secret = token or legacy
    return secret or _credential_manager_secret()


__all__ = ["PIXELLAB_CREDENTIAL_TARGET", "get_pixellab_secret", "pixellab_secret_status"]
