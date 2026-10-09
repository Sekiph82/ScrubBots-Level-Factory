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
    for candidate in (home / ".local" / "bin" / "claude.exe", home / ".local" / "bin" / "claude"):
        if candidate.is_file():
            return str(candidate)
    return None


def discover_alpix(*, user_home: Path | None = None) -> dict[str, object]:
    """Discover an enabled Alpix plugin and its configured MCP identity.

    Only the two Claude Code configuration files and installed plugin manifests
    are inspected. Credentials, history, and session files are never read.
    """
    home = user_home or Path.home()
    executable = find_claude(user_home=home)
    if not executable:
        return {"available": False, "reason": "Claude Code is unavailable."}
    settings_path = home / ".claude" / "settings.json"
    installed_path = home / ".claude" / "plugins" / "installed_plugins.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        installed = json.loads(installed_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"available": False, "reason": "Claude Alpix configuration is unavailable."}
    enabled = settings.get("enabledPlugins", {})
    plugins = installed.get("plugins", {})
    if not isinstance(enabled, Mapping) or not isinstance(plugins, Mapping):
        return {"available": False, "reason": "Claude Alpix configuration is invalid."}
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
    active = next((item for item in identities if item["enabled"] == "true" and item["mcp_servers"]), None)
    if active is None:
        return {"available": False, "reason": "Installed Alpix plugin/MCP is unavailable in Claude Code."}
    return {"available": True, "executable": executable, **active}


def generate_alpix_png(*, prompt: str, width: int, height: int, destination: str | Path,
                       discovery: Mapping[str, object] | None = None,
                       runner: Callable[..., object] = subprocess.run) -> dict[str, object]:
    """Ask the discovered Alpix integration to write one exact-size PNG."""
    if type(prompt) is not str or not prompt.strip():
        raise ValueError("Prompt is required.")
    if type(width) is not int or type(height) is not int or not 1 <= width <= 8192 or not 1 <= height <= 8192:
        raise ValueError("Requested PNG size is invalid.")
    identity = dict(discovery or discover_alpix())
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
    task = (f"Use the installed Claude Code plugin {plugin_id!r} and its configured MCP server(s) "
            f"{mcp_servers!r} to draw exactly one native-resolution pixel-art PNG. "
            f"Owner prompt: {prompt.strip()}\nRequested dimensions: {width}x{height}. "
            f"Save the PNG bytes at this exact path: {str(output)}. Do not resize after drawing, "
            "do not create a prompt plan, and report completion only after the file exists.")
    child_env = os.environ.copy()
    child_env.pop("ANTHROPIC_API_KEY", None)
    child_env.pop("ANTHROPIC_AUTH_TOKEN", None)
    try:
        completed = runner([str(executable), "-p", task, "--output-format", "text"],
                           capture_output=True, text=True, timeout=1800, env=child_env, check=False)
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
    aliases = {"prompt", "description", "request", "text", "size", "width", "height", "enabled", "active", "reference", "ref"}
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
                           "reference": row.get("reference", row.get("ref", ""))})
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
    state["state"] = "COMPLETE" if all(row.get("state") == "IMPORTED" for row in state["rows"]) else "NEEDS_RETRY"
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
    failed = sum(item.get("state") == "FAILED" for item in rows)
    return AlpixJobResult(job_id, str(state.get("state", "ERROR")), completed, failed,
                          sum(item.get("state") != "IMPORTED" for item in rows), rows)


__all__ = ["AlpixJobResult", "AlpixUnavailable", "AlpixUsageLimit", "discover_alpix", "find_claude",
           "generate_alpix_png", "read_rows", "run_csv_job"]
