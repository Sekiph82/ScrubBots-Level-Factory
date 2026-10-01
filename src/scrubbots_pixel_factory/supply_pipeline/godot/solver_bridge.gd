extends SceneTree
## Primary Level Factory -> ScrubBots solver bridge. Lives OUTSIDE the game repo; run with the
## game project as --path so every preload below is the game's own shipping code:
##
##   godot --headless --path <ScrubBots> -s <this file> -- <request.json> <response.json>
##
## For each candidate supply (3..5 FIFO columns of {color: local palette index, count}) it:
##   1. builds a real LevelData + BatchSupplyEngine (ColorBatch.make / load_candidate);
##   2. builds the initial ProofState (transparent source pixels start CLEARED: open space);
##   3. runs the game's SolvabilitySolver.solve (bounded, deterministic DFS over the real
##      ProofKernel: M23 supply, M24 slots, M25 claims, TargetSelector, production routing);
##   4. for SOLVED: replays the trace with SolvabilitySolver.replay on a FRESH state;
##   5. optionally (full-canvas levels only) measures + scores the replayed path with the
##      official LevelDifficultyAnalyzerV1 (locked Difficulty V1 model).
## Request "replay_only" entries replay an externally supplied trace (differential tests).
## Never writes into the game project. Prints "BRIDGE <i>/<n> <id> <status>" progress lines.

const LevelData = preload("res://scripts/data/level_data.gd")
const BatchSupplyEngine = preload("res://scripts/gameplay/supply/batch_supply_engine.gd")
const ColorBatch = preload("res://scripts/gameplay/supply/color_batch.gd")
const ProofState = preload("res://scripts/gameplay/solver/proof_state.gd")
const SolvabilitySolver = preload("res://scripts/gameplay/solver/solvability_solver.gd")
const SupplyPlanLoader = preload("res://scripts/gameplay/supply/supply_plan_loader.gd")
const Analyzer = preload("res://scripts/difficulty/level_difficulty_analyzer_v1.gd")
const MIN_COLUMNS := 3
const MAX_COLUMNS := 5
const VISIBLE_PREVIEW_DEPTH := 3

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		printerr("usage: -- <request.json> <response.json>")
		quit(2)
		return
	var req = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if typeof(req) != TYPE_DICTIONARY:
		printerr("bad request json")
		quit(2)
		return
	var selected_column_count := int(req.get("column_count", MIN_COLUMNS))
	var selected_preview_depth := int(req.get("visible_preview_depth", VISIBLE_PREVIEW_DEPTH))
	var out := {"schema": "pixelartstudio.scrubbots_bridge.v1",
		"authority": req.get("game_authority", {"git_head": "UNAVAILABLE"}),
		"gameConstants": {"slotCount": ProofState.SLOT_COUNT,
			"batchCountPolicy": "positive per-plan metadata bound; no global cap",
			"columnCount": selected_column_count,
			"previewDepth": VISIBLE_PREVIEW_DEPTH},
		"results": []}
	if selected_column_count < MIN_COLUMNS or selected_column_count > MAX_COLUMNS or selected_preview_depth != VISIBLE_PREVIEW_DEPTH:
		printerr("invalid Level Factory supply contract")
		quit(2)
		return
	var lv: Dictionary = req["level"]
	var cells := PackedInt32Array()
	var transparent: Array = []
	for i in range(lv["cells"].size()):
		var c := int(lv["cells"][i])
		if c < 0:
			transparent.append(i)
			c = 0  # LevelData has no empty cell; the proof state marks it CLEARED below
		cells.append(c)
	var level = LevelData.new(1, String(lv["id"]), String(lv["id"]), "EASY", int(lv["width"]),
		int(lv["height"]), PackedStringArray(lv["palette"]), cells)
	var solver = SolvabilitySolver.new()
	var cfg := {"max_visited": int(req.get("max_visited", SolvabilitySolver.DEFAULT_MAX_VISITED)),
		"max_depth": int(req.get("max_depth", SolvabilitySolver.DEFAULT_MAX_DEPTH))}
	var stop_after := int(req.get("stop_after_solved", 1))
	var analyze: bool = bool(req.get("analyze", true)) and transparent.is_empty()
	var level_number := int(req.get("level_number", 1))
	var solved_n := 0
	var cands: Array = req.get("candidates", [])
	for i in range(cands.size()):
		var cand: Dictionary = cands[i]
		var rec := {"id": cand["id"]}
		var eng = _engine(cand["columns"], level, selected_column_count)
		if eng == null:
			rec["status"] = "MALFORMED"
			out["results"].append(rec)
			print("BRIDGE %d/%d %s MALFORMED" % [i + 1, cands.size(), cand["id"]])
			continue
		if cand.has("replay_trace"):  # differential replay of an external trace
			var rp: Dictionary = solver.replay(_initial(level, eng, transparent), cand["replay_trace"])
			rec["status"] = "REPLAY"
			rec["replay"] = {"ok": rp["ok"], "solved": rp["solved"], "finalActive": int(rp["final_active"]),
				"steps": int(rp["steps"]), "divergedAt": int(rp["diverged_at"])}
			out["results"].append(rec)
			print("BRIDGE %d/%d %s REPLAY ok=%s solved=%s" % [i + 1, cands.size(), cand["id"], rp["ok"], rp["solved"]])
			continue
		var t0 := Time.get_ticks_msec()
		var res: Dictionary = solver.solve(_initial(level, eng, transparent), cfg)
		rec["status"] = String(res["status"])
		rec["reason"] = res.get("reason", "")
		rec["solver"] = {"visited": int(res.get("visited", 0)), "memoHits": int(res.get("memo_hits", 0)),
			"frontierPeak": int(res.get("frontier_peak", 0)), "maxDepthReached": int(res.get("max_depth_reached", 0)),
			"decisions": int(res.get("decisions", 0)), "elapsedMs": Time.get_ticks_msec() - t0}
		if res["status"] == SolvabilitySolver.SOLVED:
			var trace: Array = []
			for a in res["trace"]:
				trace.append({"column": int(a["column"]), "color": int(a["placed"]["color"]),
					"count": int(a["placed"]["count"]), "clears": int(a["clears"]),
					"active_after": int(a["active_after"])})
			rec["trace"] = trace
			rec["traceHash"] = int(res["trace_hash"])
			var rp: Dictionary = solver.replay(_initial(level, eng, transparent), res["trace"])
			rec["replay"] = {"ok": rp["ok"], "solved": rp["solved"], "finalActive": int(rp["final_active"]),
				"steps": int(rp["steps"]), "divergedAt": int(rp["diverged_at"])}
			if analyze and rp["ok"] and rp["solved"]:
				rec["difficultyV1"] = _difficulty(level, eng, trace, level_number)
			solved_n += 1
		out["results"].append(rec)
		print("BRIDGE %d/%d %s %s visited=%d ms=%d" % [i + 1, cands.size(), cand["id"], rec["status"],
			rec["solver"]["visited"], rec["solver"]["elapsedMs"]])
		if solved_n >= stop_after:
			break
	var f := FileAccess.open(args[1], FileAccess.WRITE)
	f.store_string(JSON.stringify(out, "\t"))
	f.close()
	quit(0)

func _engine(columns: Array, level, column_count: int):
	var eng = BatchSupplyEngine.create(column_count, 3)
	if eng == null or columns.size() != column_count:
		return null
	var cols: Array = []
	var n := 0
	for col in columns:
		var q: Array = []
		for b in col:
			var cb = ColorBatch.make("B%04d" % n, int(b["color"]), int(b["count"]), level.palette.size())
			if cb == null:
				return null
			q.append(cb)
			n += 1
		cols.append(q)
	if not eng.load_candidate(cols, 0, level.palette.size()):
		return null
	return eng

func _initial(level, eng, transparent: Array):
	var ps = ProofState.from_level_and_supply(level, eng)
	for i in transparent:
		ps.active[int(i)] = ProofState.CLEARED_BYTE
	return ps

func _difficulty(level, eng, trace: Array, level_number: int) -> Dictionary:
	var an = Analyzer.new()
	if not an.is_ok():
		return {"ok": false, "error": an.get_error()}
	var cols: Array = []
	for a in trace:
		cols.append(int(a["column"]))
	var raw: Dictionary = an.measure(level, eng, cols, trace)
	if not raw.get("ok", false):
		return {"ok": false, "error": raw.get("error", "measure failed")}
	var sc: Dictionary = an.score(raw, level_number)
	return {"ok": true, "challengeScore": sc["challengeScore"], "vector": sc["vector"],
		"targetChallenge": sc["targetChallenge"], "sessionLoad": sc["sessionLoad"]["value"],
		"B": sc["supporting"]["B"], "S": sc["supporting"]["S"], "U": sc["supporting"]["U"],
		"path": raw["path"]}
