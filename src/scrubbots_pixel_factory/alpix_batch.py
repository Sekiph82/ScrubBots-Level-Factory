"""Claude Code + installed Alpix image generation and resumable CSV jobs.

Claude authentication belongs to the owner's Claude Code subscription session.
This adapter never accepts an API key and removes ANTHROPIC_API_KEY from the
child environment so the CLI cannot silently fall back to API billing.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence


JOB_SCHEMA = "scrubbots-alpix-art-job"
JOB_VERSION = 1
_LIMIT_MARKERS = ("usage limit", "rate limit", "quota exceeded", "limit reached", "out of extra usage")


class AlpixUnavailable(RuntimeError):
    pass


class AlpixUsageLimit(RuntimeError):
    pass


def find_claude(*, user_home: Path | None = None) -> str | None:
    """Resolve the installed Claude Code executable without scanning other apps."""
    home = user_home or Path.home()
    if user_home is None:
        found = shutil.which("claude")
        if found:
            return found
    candidates = (
        home / ".local" / "bin" / "claude.exe", home / ".local" / "bin" / "claude",
        home / "AppData" / "Local" / "Programs" / "claude" / "claude.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def _discover_account_synced_alpix(
    executable: str,
    *,
    runner: Callable[..., object] | None = None,
) -> dict[str, object] | None:
    """Probe Claude Code's account-synced Alpix connector without invoking tools."""
    run = runner or subprocess.run
    try:
        completed = run(
            [executable, "mcp", "get", "claude.ai Alpix"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "state": "unverified",
            "reason": "Claude Code did not finish the read-only Alpix connector status check.",
        }
    except OSError:
        return {
            "state": "unverified",
            "reason": "Claude Code could not run the read-only Alpix connector status check.",
        }

    output = "\n".join((str(getattr(completed, "stdout", "")), str(getattr(completed, "stderr", ""))))
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if not any(line.casefold() == "claude.ai alpix:" for line in lines):
        if int(getattr(completed, "returncode", 1)) != 0 and "not found" not in output.casefold():
            return {
                "state": "unverified",
                "reason": "Claude Code could not verify the account-synced Alpix connector.",
            }
        return None

    scope = next((line.split(":", 1)[1].strip() for line in lines if line.casefold().startswith("scope:")), "")
    status = next((line.split(":", 1)[1].strip() for line in lines if line.casefold().startswith("status:")), "")
    if scope.casefold() != "claude.ai config":
        return None
    if "connected" in status.casefold():
        return {
            "state": "connected",
            "plugin_id": "claude.ai connector",
            "mcp_servers": "claude.ai Alpix",
            "route_scope": scope,
            "reason": "Claude Code reports the account-synced Alpix connector connected; its drawing/export tools are not yet verified.",
        }
    if "authentication" in status.casefold() or "auth" in status.casefold():
        return {
            "state": "auth_required",
            "reason": "Claude Code sees the account-synced Alpix connector, but it needs authentication.",
        }
    return {
        "state": "unverified",
        "reason": "Claude Code sees the account-synced Alpix connector but did not report it connected.",
    }


def discover_alpix(*, user_home: Path | None = None,
                  project_root: Path | None = None) -> dict[str, object]:
    """Discover an enabled Alpix plugin and its configured MCP identity.

    Claude user configuration and installed plugin manifests are inspected, as
    well as project-scoped settings and MCP names when an explicit project root
    is supplied. Credentials, history, and session files are never read.
    """
    home = user_home or Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())
    config_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR", "")).expanduser() if user_home is None and os.environ.get("CLAUDE_CONFIG_DIR") else home / ".claude"
    executable = find_claude(user_home=user_home)
    if not executable:
        return {"available": False, "status": "CLAUDE_CLI_MISSING", "reason": "CLAUDE_CLI_MISSING: Claude Code executable is not available on this Studio process PATH or the current user-local install path."}
    settings_path = config_dir / "settings.json"
    installed_path = config_dir / "plugins" / "installed_plugins.json"
    project_settings_paths = (() if project_root is None else (
        Path(project_root) / ".claude" / "settings.json",
        Path(project_root) / ".claude" / "settings.local.json",
    ))
    scope_unread = False
    scope_invalid = False
    project_settings: list[Mapping[str, object]] = []

    def read_optional_object(path: Path) -> Mapping[str, object] | None:
        nonlocal scope_unread, scope_invalid
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except (OSError, UnicodeError):
            scope_unread = True
            return None
        except json.JSONDecodeError:
            scope_invalid = True
            return None
        if not isinstance(value, Mapping):
            scope_invalid = True
            return None
        return value

    settings = read_optional_object(settings_path) or {}
    installed = read_optional_object(installed_path) or {"plugins": {}}
    enabled = settings.get("enabledPlugins", {})
    plugins = installed.get("plugins", {})
    if not isinstance(enabled, Mapping) or not isinstance(plugins, Mapping):
        return {"available": False, "status": "ALPIX_INVALID_CONFIG", "reason": "ALPIX_INVALID_CONFIG: Claude plugin settings or installed plugin map is invalid."}
    for project_settings_path in project_settings_paths:
        project_setting = read_optional_object(project_settings_path)
        if project_setting is not None:
            project_settings.append(project_setting)
    effective_enabled = dict(enabled)
    for project_setting in project_settings:
        project_enabled = project_setting.get("enabledPlugins", {})
        if isinstance(project_enabled, Mapping):
            effective_enabled.update(project_enabled)
    identities: list[dict[str, str]] = []
    for plugin_id, records in plugins.items():
        if not isinstance(plugin_id, str) or not isinstance(records, list):
            continue
        paths = [Path(str(row.get("installPath", ""))) for row in records if isinstance(row, Mapping)]
        manifest_text = ""
        mcp_names: list[str] = []
        for install_path in paths:
            for relative in (".claude-plugin/plugin.json", ".mcp.json", "plugin.json", "mcp.json"):
                config_path = install_path / relative
                if not config_path.is_file():
                    continue
                try:
                    value = json.loads(config_path.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError):
                    continue
                manifest_text += " " + " ".join(str(value.get(key, "")) for key in ("name", "description", "displayName"))
                servers = value.get("mcpServers", value.get("servers", {}))
                if isinstance(servers, Mapping):
                    mcp_names.extend(str(name) for name in servers if isinstance(name, str))
        if "alpix" in (plugin_id + manifest_text + " " + " ".join(mcp_names)).lower():
            identities.append({"plugin_id": plugin_id, "enabled": str(enabled.get(plugin_id, False)).lower(),
                               "mcp_servers": ",".join(sorted(set(mcp_names)))})
    active = next((item for item in identities
                   if str(effective_enabled.get(item["plugin_id"], item["enabled"])).lower() == "true"
                   and item["mcp_servers"]), None)
    if project_root is not None:
        project_mcp = read_optional_object(Path(project_root) / ".mcp.json")
        project_servers = project_mcp.get("mcpServers", {}) if project_mcp is not None else {}
        if not isinstance(project_servers, Mapping):
            return {"available": False, "status": "ALPIX_INVALID_CONFIG",
                    "reason": "ALPIX_INVALID_CONFIG: project .mcp.json mcpServers must contain an object."}
        project_alpix_servers = sorted(name for name in project_servers
                                       if isinstance(name, str) and "alpix" in name.lower())
        if active is None and project_alpix_servers:
            active = {"plugin_id": "claude-project-mcp@project-config", "enabled": "true",
                      "mcp_servers": ",".join(project_alpix_servers)}
    global_config_path = home / ".claude.json"
    global_mcp_names: list[str] = []
    global_config = read_optional_object(global_config_path)
    global_servers = global_config.get("mcpServers", {}) if global_config is not None else {}
    if isinstance(global_servers, Mapping):
        global_mcp_names = [name for name in global_servers if isinstance(name, str) and "alpix" in name.lower()]
    if active is None and global_mcp_names:
        active = {"plugin_id": "claude-user-mcp@global-config", "enabled": "true",
                  "mcp_servers": ",".join(sorted(set(global_mcp_names)))}
    account_route = None
    if active is None and user_home is None and not scope_unread and not scope_invalid:
        account_route = _discover_account_synced_alpix(executable)
        if account_route and account_route.get("state") == "connected":
            active = {
                "plugin_id": str(account_route["plugin_id"]),
                "mcp_servers": str(account_route["mcp_servers"]),
                "route_scope": str(account_route["route_scope"]),
                "route_kind": "claude.ai_connector",
            }
    if active is None:
        if account_route and account_route.get("state") == "auth_required":
            return {"available": False, "status": "ALPIX_AUTH_REQUIRED",
                    "reason": str(account_route["reason"])}
        if account_route and account_route.get("state") == "unverified":
            return {"available": False, "status": "ALPIX_SYNC_UNVERIFIED",
                    "reason": str(account_route["reason"])}
        if scope_unread:
            return {"available": False, "status": "CONFIG_SCOPE_UNREAD",
                    "reason": "CONFIG_SCOPE_UNREAD: one or more Claude configuration scopes could not be read; ALPIX availability is unknown."}
        if scope_invalid:
            return {"available": False, "status": "ALPIX_INVALID_CONFIG",
                    "reason": "ALPIX_INVALID_CONFIG: a Claude configuration scope contains invalid JSON or a non-object value."}
        return {"available": False, "status": "ALPIX_PLUGIN_MISSING",
                "reason": "ALPIX_PLUGIN_MISSING: Claude Code is installed, but no enabled ALPIX plugin/MCP server was found in the current user configuration."}
    account_synced = active.get("route_kind") == "claude.ai_connector"
    return {"available": True, "status": "ALPIX_AVAILABLE_DISCOVERY_ONLY",
            "session_status": "CLAUDEAI_CONNECTOR_CONNECTED" if account_synced else "CLAUDE_SESSION_UNVERIFIED",
            "reason": ("Claude Code reports the account-synced Alpix MCP connector connected; drawing/export capabilities and usage-limit health are not probed."
                       if account_synced else "ALPIX MCP route is configured. Claude session authentication is not probed; usage-limit health is not probed."),
            "executable": executable, **active}


def generate_alpix_png(*, prompt: str, width: int, height: int, destination: str | Path,
                       discovery: Mapping[str, object] | None = None,
                       project_root: Path | None = None,
                       runner: Callable[..., object] = subprocess.run) -> dict[str, object]:
    """Ask the discovered Alpix integration to write one exact-size PNG."""
    if type(prompt) is not str or not prompt.strip():
        raise ValueError("Prompt is required.")
    if type(width) is not int or type(height) is not int or not 1 <= width <= 8192 or not 1 <= height <= 8192:
        raise ValueError("Requested PNG size is invalid.")
    identity = dict(discovery or discover_alpix(project_root=project_root))
    if identity.get("available") is not True:
        raise AlpixUnavailable(str(identity.get("reason", "Claude Alpix is unavailable.")))
    executable = identity.get("executable")
    plugin_id = identity.get("plugin_id")
    mcp_servers = identity.get("mcp_servers")
    if not all(type(value) is str and value.strip() for value in (executable, plugin_id, mcp_servers)):
        raise AlpixUnavailable("Claude Alpix tool identity is incomplete.")
    output = Path(destination).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError("Alpix output identity already exists.")
    if identity.get("route_kind") == "claude.ai_connector":
        route_instruction = (f"Use the account-synced Claude Code MCP connector {mcp_servers!r} "
                             f"(scope {identity.get('route_scope', 'claude.ai config')!r}) to draw exactly one native-resolution pixel-art PNG. ")
    else:
        route_instruction = (f"Use the installed Claude Code plugin {plugin_id!r} and its configured MCP server(s) "
                             f"{mcp_servers!r} to draw exactly one native-resolution pixel-art PNG. ")
    task = (route_instruction
            + f"Owner prompt: {prompt.strip()}\nRequested dimensions: {width}x{height}. "
            f"Save the PNG bytes at this exact path: {str(output)}. Do not resize after drawing, "
            "do not create a prompt plan, and report completion only after the file exists.")
    child_env = os.environ.copy()
    child_env.pop("ANTHROPIC_API_KEY", None)
    child_env.pop("ANTHROPIC_AUTH_TOKEN", None)
    working_directory = str(Path(project_root).resolve()) if project_root is not None else None
    try:
        completed = runner([str(executable), "-p", task, "--output-format", "text"],
                           capture_output=True, text=True, timeout=1800, env=child_env, check=False,
                           cwd=working_directory)
    except subprocess.TimeoutExpired as exc:
        raise AlpixUnavailable("Claude Alpix generation timed out.") from exc
    output_text = "\n".join((str(getattr(completed, "stdout", "")), str(getattr(completed, "stderr", "")))).lower()
    if any(marker in output_text for marker in _LIMIT_MARKERS):
        raise AlpixUsageLimit("Claude subscription usage limit reached.")
    if getattr(completed, "returncode", 1) != 0 or not output.is_file():
        raise AlpixUnavailable("Claude Alpix did not produce the requested PNG.")
    _validate_png(output, width, height)
    raw = output.read_bytes()
    return {"path": str(output), "sha256": hashlib.sha256(raw).hexdigest(), "width": width, "height": height,
            "provider_id": "ALPIX_CLAUDE", "plugin_id": plugin_id, "mcp_servers": mcp_servers}


def read_rows(raw_csv: bytes, *, default_size: tuple[int, int] = (32, 32)) -> list[dict[str, object]]:
    """Parse the verified legacy CSV forms and normalize each request once."""
    if type(raw_csv) is not bytes:
        raise TypeError("CSV input must be bytes")
    try:
        text = raw_csv.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 text") from exc
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;") if sample.strip() else csv.excel
    except csv.Error:
        dialect = csv.excel
    records = list(csv.reader(text.splitlines(), dialect))
    records = [row for row in records if row and any(cell.strip() for cell in row)]
    if not records:
        return []
    aliases = {"prompt", "description", "request", "text", "size", "width", "height", "enabled", "active", "reference", "ref", "provider"}
    header = [cell.strip().lower() for cell in records[0]]
    has_header = bool(set(header) & aliases)
    output: list[dict[str, object]] = []
    if has_header:
        positions = {key: index for index, key in enumerate(header)}
        for raw in records[1:]:
            if len(raw) < len(header):
                raw += [""] * (len(header) - len(raw))
            row = {key: raw[index].strip() for key, index in positions.items() if index < len(raw)}
            enabled = row.get("enabled", row.get("active", "true")).lower()
            if enabled in {"0", "false", "no", "off", "disabled"}:
                continue
            prompt = next((row.get(key, "") for key in ("prompt", "description", "request", "text") if row.get(key, "")), "")
            if not prompt:
                continue
            width, height = _row_size(row, default_size)
            output.append({"prompt": prompt, "width": width, "height": height,
                           "reference": row.get("reference", row.get("ref", "")),
                           "provider_id": row.get("provider", "ALPIX (Claude)").strip() or "ALPIX (Claude)"})
    else:
        for raw in records:
            prompt = raw[0].strip()
            if not prompt:
                continue
            value = raw[1].strip() if len(raw) > 1 else ""
            row = {"size": value} if value else {}
            width, height = _row_size(row, default_size)
            output.append({"prompt": prompt, "width": width, "height": height, "reference": ""})
    return output


def _row_size(row: Mapping[str, str], default_size: tuple[int, int]) -> tuple[int, int]:
    size = row.get("size", "").lower().replace("×", "x").strip()
    if size:
        parts = size.split("x", 1)
        if len(parts) == 2 and all(part.strip().isdigit() for part in parts):
            return int(parts[0]), int(parts[1])
    width = row.get("width", "").strip()
    height = row.get("height", "").strip()
    if width.isdigit() and height.isdigit():
        return int(width), int(height)
    return default_size


@dataclass(frozen=True)
class AlpixJobResult:
    job_id: str
    state: str
    completed: int
    failed: int
    remaining: int
    rows: tuple[Mapping[str, object], ...]

    def to_dict(self) -> dict[str, object]:
        return {"job_id": self.job_id, "state": self.state, "completed": self.completed,
                "failed": self.failed, "remaining": self.remaining, "rows": [dict(row) for row in self.rows]}


def run_csv_job(csv_path: str | Path, job_root: str | Path, *,
                renderer: Callable[[str, int, int, Path], Mapping[str, object]],
                importer: Callable[[Path], Mapping[str, object]], default_size: tuple[int, int] = (32, 32)) -> AlpixJobResult:
    """Run/resume one CSV-SHA job, persisting each legacy row state transition."""
    source = Path(csv_path).resolve()
    raw_csv = source.read_bytes()
    job_id = hashlib.sha256(raw_csv).hexdigest()
    rows = read_rows(raw_csv, default_size=default_size)
    root = Path(job_root).resolve()
    job_dir = root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    state_path = root / f"{job_id}.json"
    state = _read_job(state_path, job_id, raw_csv, rows)
    state["state"] = "RUNNING"
    _save_job(state_path, state)
    for index, row in enumerate(state["rows"]):
        row_state = str(row.get("state", "PENDING"))
        provider_id = str(row.get("provider_id", "ALPIX (Claude)")).strip().upper()
        if row_state == "IMPORTED":
            continue
        if row_state == "PROVIDER_RETIRED":
            continue
        if provider_id == "MAGNIFIC":
            row.update({"state": "PROVIDER_RETIRED", "error": "PROVIDER_RETIRED_MAGNIFIC"})
            _save_job(state_path, state)
            continue
        if provider_id not in {"ALPIX", "ALPIX (CLAUDE)"}:
            row.update({"state": "FAILED", "error": "Unsupported provider in CSV row."})
            _save_job(state_path, state)
            continue
        artifact = job_dir / f"row-{index + 1:05d}.png"
        row["artifact_path"] = str(artifact)
        _save_job(state_path, state)
        if row_state == "PENDING" and artifact.is_file():
            try:
                _validate_png(artifact, int(row["width"]), int(row["height"]))
            except (OSError, ValueError):
                artifact.unlink(missing_ok=True)
            else:
                row.update({"state": "DRAWN", "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()})
                _save_job(state_path, state)
                row_state = "DRAWN"
        if row_state in {"DRAWN", "VALIDATED", "IMPORTED"} and _is_valid_artifact(artifact, row):
            if row_state == "IMPORTED":
                continue
            if row_state == "DRAWN":
                try:
                    _validate_png(artifact, int(row["width"]), int(row["height"]))
                except (OSError, ValueError):
                    row.update({"state": "PENDING", "artifact_sha256": None, "source_id": None})
                    _save_job(state_path, state)
                else:
                    row["state"] = "VALIDATED"
                    _save_job(state_path, state)
            if row.get("state") == "VALIDATED":
                imported = importer(artifact)
                source_id = imported.get("source_id")
                if not isinstance(source_id, str) or not source_id:
                    row["state"] = "FAILED"
                    row["error"] = "Canonical artwork import failed."
                else:
                    row.update({"state": "IMPORTED", "source_id": source_id})
                _save_job(state_path, state)
            continue
        row.update({"state": "PENDING", "artifact_sha256": None, "source_id": None})
        _save_job(state_path, state)
        try:
            prompt = str(row["prompt"])
            reference = str(row.get("reference", "")).strip()
            if reference:
                reference_path = Path(reference).expanduser()
                if not reference_path.is_absolute():
                    reference_path = source.parent / reference_path
                reference_path = reference_path.resolve()
                if not reference_path.is_file():
                    raise ValueError("CSV reference image is unavailable.")
                prompt += f"\nOwner-supplied reference image path: {reference_path}"
            rendered = renderer(prompt, int(row["width"]), int(row["height"]), artifact)
            if rendered.get("path") != str(artifact):
                raise ValueError("Provider output path did not match the current row.")
            _validate_png(artifact, int(row["width"]), int(row["height"]))
        except AlpixUsageLimit:
            artifact.unlink(missing_ok=True)
            row.update({"state": "PENDING", "error": None})
            state["state"] = "LIMIT"
            _save_job(state_path, state)
            return _job_result(job_id, state)
        except AlpixUnavailable:
            artifact.unlink(missing_ok=True)
            row.update({"state": "PENDING", "error": None})
            state["state"] = "UNAVAILABLE"
            _save_job(state_path, state)
            return _job_result(job_id, state)
        except Exception:
            artifact.unlink(missing_ok=True)
            row.update({"state": "FAILED", "error": "Provider did not complete this row."})
            _save_job(state_path, state)
            continue
        row.update({"state": "DRAWN", "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(), "error": None})
        _save_job(state_path, state)
        row["state"] = "VALIDATED"
        _save_job(state_path, state)
        try:
            imported = importer(artifact)
        except Exception:
            imported = {}
        source_id = imported.get("source_id")
        if isinstance(source_id, str) and source_id:
            row.update({"state": "IMPORTED", "source_id": source_id})
        else:
            row.update({"state": "FAILED", "error": "Canonical artwork import failed."})
        _save_job(state_path, state)
    state["state"] = "COMPLETE" if all(row.get("state") in {"IMPORTED", "PROVIDER_RETIRED"} for row in state["rows"]) else "NEEDS_RETRY"
    _save_job(state_path, state)
    return _job_result(job_id, state)


def _read_job(path: Path, job_id: str, raw_csv: bytes, rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    if path.exists():
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if (value.get("schema") == JOB_SCHEMA and value.get("version") == JOB_VERSION
                    and value.get("job_id") == job_id and value.get("csv_sha256") == job_id
                    and value.get("csv_bytes") == len(raw_csv) and isinstance(value.get("rows"), list)
                    and len(value["rows"]) == len(rows)):
                return value
        except (OSError, UnicodeError, json.JSONDecodeError, AttributeError):
            pass
    return {"schema": JOB_SCHEMA, "version": JOB_VERSION, "job_id": job_id, "csv_sha256": job_id,
            "csv_bytes": len(raw_csv), "state": "PENDING",
            "rows": [{**dict(row), "index": index, "state": "PENDING", "artifact_sha256": None,
                      "source_id": None, "error": None} for index, row in enumerate(rows)]}


def _save_job(path: Path, state: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def _is_valid_artifact(path: Path, row: Mapping[str, object]) -> bool:
    try:
        raw = path.read_bytes()
    except OSError:
        return False
    expected = row.get("artifact_sha256")
    return (isinstance(expected, str) and hashlib.sha256(raw).hexdigest() == expected
            and raw.startswith(b"\x89PNG\r\n\x1a\n"))


def _validate_png(path: Path, width: int, height: int) -> None:
    try:
        from PIL import Image
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != (width, height):
                raise ValueError("Provider PNG dimensions do not match the requested size.")
    except ImportError as exc:
        raise ValueError("PNG validation capability is unavailable.") from exc


def _job_result(job_id: str, state: Mapping[str, object]) -> AlpixJobResult:
    rows = tuple(dict(item) for item in state.get("rows", []) if isinstance(item, Mapping))
    completed = sum(item.get("state") == "IMPORTED" for item in rows)
    failed = sum(item.get("state") in {"FAILED", "PROVIDER_RETIRED"} for item in rows)
    return AlpixJobResult(job_id, str(state.get("state", "ERROR")), completed, failed,
                          sum(item.get("state") != "IMPORTED" for item in rows), rows)


__all__ = ["AlpixJobResult", "AlpixUnavailable", "AlpixUsageLimit", "discover_alpix", "find_claude",
           "generate_alpix_png", "read_rows", "run_csv_job"]
