"""ScrubBotsSolver: the ACCEPTANCE authority. Runs the game's own SolvabilitySolver,
SolvabilitySolver.replay and LevelDifficultyAnalyzerV1 through godot/solver_bridge.gd."""
import json
import hashlib
import os
import subprocess
import tempfile
import threading
import time
import uuid
from collections import deque
from pathlib import Path

from .game_rules import find_godot

BRIDGE = Path(__file__).resolve().parent / "godot" / "solver_bridge.gd"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class SolverBridgeError(RuntimeError):
    def __init__(self, message, telemetry):
        super().__init__(message)
        self.telemetry = dict(telemetry)


class ScrubBotsSolver:
    def __init__(self, rules, godot=None):
        self.rules = rules
        self.godot = godot or find_godot()
        if not self.godot:
            raise RuntimeError("Godot not found (set SCRUBBOTS_GODOT or put godot on PATH)")

    def run(self, level, candidates, stop_after=1, max_visited=None, analyze=True,
            level_number=1, progress=None, timeout=None):
        """level: {id,width,height,palette:[#RRGGBBAA local],cells:[local or -1]}
        candidates: [{id, columns:[[{color,count}]*3]} or {..., replay_trace:[...]}]"""
        attested_runtime = getattr(self.rules, "attestation", None) is not None
        if attested_runtime:
            if not isinstance(candidates, (list, tuple)) or len(candidates) != 1 or stop_after != 1:
                raise ValueError("pinned-runtime bridge requires exactly one candidate and stop_after=1")
            if max_visited is None or type(max_visited) is not int or not 0 < max_visited <= 25_000:
                raise ValueError("pinned-runtime candidate max_visited must be within 1..25000")
            if timeout is None or not 0 < float(timeout) <= 90:
                raise ValueError("pinned-runtime candidate timeout must be within (0, 90] seconds")
        if attested_runtime:
            work_root = Path(self.rules.project).resolve() / ".lf_solver_jobs"
            work = work_root / f"job-{uuid.uuid4().hex}"
            work.mkdir(parents=True, exist_ok=False)
        else:
            work = Path(tempfile.mkdtemp(prefix="sb_bridge_"))
        # Exercise the game's owner-facing loaders for every candidate, including
        # generated candidates. SupplyPlanLoader resolves canonical global C IDs
        # through the live game's palette authority before building runtime state.
        cid_by_hex = {color.upper()[:7]: cid for cid, color in self.rules.palette}
        for index, candidate in enumerate(candidates):
            if "columns" not in candidate:
                continue
            columns = []
            maximum = 1
            for column_index, column in enumerate(candidate["columns"]):
                batches = []
                for batch_index, batch in enumerate(column):
                    amount = int(batch["count"])
                    maximum = max(maximum, amount)
                    local_color = int(batch["color"])
                    if local_color < 0 or local_color >= len(level["palette"]):
                        raise ValueError("candidate batch uses a palette index outside the level")
                    local_hex = str(level["palette"][local_color]).upper()[:7]
                    cid = cid_by_hex.get(local_hex)
                    if cid is None:
                        raise ValueError(f"level palette color {local_hex} is not in the current game's canonical palette")
                    batches.append({"batchId": f"C{index:04d}-K{column_index:02d}-B{batch_index:03d}",
                                    "cid": cid, "robots": amount})
                columns.append(batches)
            plan = {"schema": "scrubbots.level_supply_plan.v1", "version": 1,
                    "levelId": str(level["id"]), "columnCount": len(columns),
                    "visiblePreviewDepth": self.rules.preview_depth,
                    "maxRobotsPerBatch": maximum, "columns": columns}
            plan_path = work / f"plan-{index}.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            candidate["supply_plan_path"] = str(plan_path)
        req = {"level": level, "candidates": candidates, "column_count": self.rules.column_count,
               "visible_preview_depth": self.rules.preview_depth, "stop_after_solved": stop_after,
               "analyze": analyze, "level_number": level_number,
               "game_authority": dict(self.rules.authority)}
        if max_visited:
            req["max_visited"] = max_visited
        (work / "req.json").write_text(json.dumps(req), encoding="utf-8")
        request_sha256 = hashlib.sha256((work / "req.json").read_bytes()).hexdigest()
        plan_path = Path(str(candidates[0].get("supply_plan_path", ""))) if candidates else None
        plan_sha256 = hashlib.sha256(plan_path.read_bytes()).hexdigest() if plan_path and plan_path.is_file() else None
        tail = deque(maxlen=30)
        output_bytes = 0
        reader_error = []
        native_solve_started = False
        native_solve_completed = False
        native_solve_status = None
        process_env = None
        if attested_runtime:
            process_env = os.environ.copy()
            bounded_temp = work / "process-tmp"
            bounded_temp.mkdir(parents=True, exist_ok=False)
            for key in ("TMP", "TEMP", "TMPDIR"):
                process_env[key] = str(bounded_temp)

        def drain_output(stream):
            nonlocal output_bytes, native_solve_started, native_solve_completed, native_solve_status
            pending = ""
            try:
                while True:
                    chunk = stream.read(1024)
                    if not chunk:
                        break
                    output_bytes += len(chunk.encode("utf-8", errors="replace"))
                    if output_bytes > 1024 * 1024:
                        reader_error.append("Godot stdout exceeded the 1 MiB capture limit")
                        break
                    pending += chunk
                    while "\n" in pending:
                        line, pending = pending.split("\n", 1)
                        line = line[-2048:].rstrip()
                        tail.append(line)
                        if line.startswith("BRIDGE_NATIVE_START "):
                            native_solve_started = True
                        elif line.startswith("BRIDGE_NATIVE_END "):
                            native_solve_completed = True
                            native_solve_status = line.split(" status=", 1)[-1].split(" ", 1)[0]
                        if line.startswith("BRIDGE") and progress:
                            progress(line)
                    if len(pending) > 4096:
                        pending = pending[-4096:]
                if pending:
                    tail.append(pending[-2048:].rstrip())
            except (OSError, UnicodeError) as exc:
                reader_error.append(str(exc)[:256])

        flags = NO_WINDOW
        if attested_runtime and os.name == "nt":
            flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        start = time.monotonic()
        hard_timeout = float(timeout if timeout is not None else (90 if attested_runtime else 0))
        timeout_limit = 90 if attested_runtime else 300
        if hard_timeout < 0 or hard_timeout > timeout_limit or (attested_runtime and hard_timeout == 0):
            raise ValueError(f"native solver timeout must be from 0 to {timeout_limit} seconds")
        p = None
        try:
            p = subprocess.Popen([self.godot, "--headless", "--path", str(self.rules.project), "-s", str(BRIDGE),
                                  "--", str(work / "req.json"), str(work / "res.json")],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 encoding="utf-8", errors="replace", creationflags=flags,
                                 env=process_env, bufsize=1)
            reader = threading.Thread(target=drain_output, args=(p.stdout,), daemon=True)
            reader.start()
            timed_out = False
            output_overflow = False
            while p.poll() is None:
                if hard_timeout and time.monotonic() - start >= hard_timeout:
                    timed_out = True
                    p.terminate()
                    try:
                        p.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        p.wait()
                    break
                if reader_error:
                    output_overflow = True
                    p.terminate()
                    try:
                        p.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        p.wait()
                    break
                time.sleep(0.05)
            reader.join(timeout=2)
            if reader.is_alive():
                p.kill()
                p.wait()
                reader.join(timeout=2)
            if p.stdout is not None:
                p.stdout.close()
            elapsed_seconds = round(time.monotonic() - start, 3)
            exit_code = p.returncode
        except OSError as exc:
            elapsed_seconds = round(time.monotonic() - start, 3)
            telemetry = {
                "invocation_count": 0, "native_solve_started": False, "native_solve_completed": False,
                "timed_out": False, "elapsed_seconds": elapsed_seconds, "process_exit_code": None,
                "process_pid": None, "request_sha256": request_sha256, "plan_sha256": plan_sha256,
                "job_path": str(work), "launch_error": str(exc)[:512], "stdout_tail": list(tail),
            }
            self._write_runner_receipt(work, telemetry)
            raise SolverBridgeError(f"bounded Godot process could not be launched: {exc}", telemetry) from exc
        telemetry = {
            "invocation_count": int(native_solve_started),
            "process_invocation_count": 1 if p is not None else 0,
            "runtime_kind": "LF_PINNED_SOURCE_MINIMAL_RUNTIME" if attested_runtime else "CONFIGURED_GAME_PROJECT",
            "timeout_seconds": hard_timeout or None, "elapsed_seconds": elapsed_seconds,
            "process_exit_code": exit_code, "process_pid": p.pid if p is not None else None,
            "timed_out": timed_out, "native_solve_started": native_solve_started,
            "native_solve_completed": native_solve_completed, "native_solve_status": native_solve_status,
            "stdout_bytes": output_bytes, "stdout_tail": list(tail),
            "request_sha256": request_sha256, "plan_sha256": plan_sha256,
            "response_sha256": None, "job_path": str(work),
        }
        self._write_runner_receipt(work, telemetry)
        if timed_out:
            raise SolverBridgeError(
                f"bounded Godot solver timed out after {hard_timeout:.1f}s; job retained at {work}", telemetry
            )
        if reader_error:
            raise SolverBridgeError("bounded Godot output capture failed: " + "; ".join(reader_error), telemetry)
        out = work / "res.json"
        if exit_code != 0 or not out.exists():
            raise SolverBridgeError("solver bridge failed:\n" + "\n".join(tail), telemetry)
        try:
            response_bytes = out.read_bytes()
            response = json.loads(response_bytes.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SolverBridgeError(f"solver bridge response is unreadable: {exc}", telemetry) from exc
        telemetry["response_sha256"] = hashlib.sha256(response_bytes).hexdigest()
        telemetry["elapsed_seconds"] = elapsed_seconds
        self._write_runner_receipt(work, telemetry)
        response["_runner"] = telemetry
        return response

    @staticmethod
    def _write_runner_receipt(work, telemetry):
        (work / "runner.json").write_text(json.dumps(telemetry, sort_keys=True, indent=2) + "\n", encoding="utf-8")
