extends SceneTree
## Primary Level Factory -> ScrubBots solver bridge. Lives OUTSIDE the game repo; run with the
## game project as --path so every preload below is the game's own shipping code:
##
##   godot --headless --path <ScrubBots> -s <this file> -- <request.json> <response.json>
##
## For each candidate supply (3..5 FIFO columns of {color: local palette index, count}) it:
##   1. builds a real LevelData + BatchSupplyEngine (ColorBatch.make / load_candidate);
##   2. builds the initial ProofState from native LevelData V2 VOID cells;
##   3. runs the game's SolvabilitySolver.solve (bounded, deterministic DFS over the real
##      ProofKernel: M23 supply, M24 slots, M25 claims, TargetSelector, production routing);
##   4. for SOLVED: replays the trace with SolvabilitySolver.replay on a FRESH state;
##   5. measures + scores the replayed path with the official LevelDifficultyAnalyzerV1
##      for both legacy V1 and native VOID V2 levels.
## Request "replay_only" entries replay an externally supplied trace (differential tests).
## Never writes into the game project. Prints "BRIDGE <i>/<n> <id> <status>" progress lines.

const LevelData = preload("res://scripts/data/level_data.gd")
const LevelLoader = preload("res://scripts/data/level_loader.gd")
const ProductionLevelValidator = preload("res://scripts/data/production_level_validator.gd")
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
			"formatVersionVoid": LevelData.FORMAT_VERSION_VOID,
			"voidCell": LevelData.VOID_CELL,
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
	var void_count := 0
	for i in range(lv["cells"].size()):
		var c := int(lv["cells"][i])
		if c == LevelData.VOID_CELL:
			void_count += 1
		elif c < 0:
			printerr("unsupported negative LevelData cell")
			quit(2)
			return
		cells.append(c)
	if void_count > 0 and (LevelData.FORMAT_VERSION_VOID != 2 or LevelData.VOID_CELL != -1 or void_count == cells.size()):
		printerr("current game does not support canonical VOID V2 LevelData")
		quit(2)
		return
	var level_version := LevelData.FORMAT_VERSION_VOID if void_count > 0 else LevelData.FORMAT_VERSION
	var level_payload := {"version": level_version, "id": String(lv["id"]), "name": String(lv.get("name", lv["id"])),
		"difficulty": String(lv.get("difficulty", "EASY")), "width": int(lv["width"]),
		"height": int(lv["height"]), "palette": lv["palette"], "cells": cells}
	var loaded = LevelLoader.load_from_text(JSON.stringify(level_payload), String(lv["id"]))
	if not loaded.is_ok():
		printerr("LevelLoader rejected bridge LevelData: %s" % "; ".join(loaded.errors))
		quit(2)
		return
	var level = loaded.level_data
	var production = ProductionLevelValidator.validate(level)
	if not production.is_ok():
		printerr("ProductionLevelValidator rejected bridge LevelData: %s" % "; ".join(production.errors))
		quit(2)
		return
	out["levelLoaderPass"] = true
	out["productionValidatorPass"] = true
	var solver = SolvabilitySolver.new()
	var cfg := {"max_visited": int(req.get("max_visited", SolvabilitySolver.DEFAULT_MAX_VISITED)),
		"max_depth": int(req.get("max_depth", SolvabilitySolver.DEFAULT_MAX_DEPTH))}
	var stop_after := int(req.get("stop_after_solved", 1))
	var analyze: bool = bool(req.get("analyze", true))
	var level_number := int(req.get("level_number", 1))
	var solved_n := 0
	var cands: Array = req.get("candidates", [])
	for i in range(cands.size()):
		var cand: Dictionary = cands[i]
		var rec := {"id": cand["id"], "artworkCellCount": level.get_artwork_cell_count(), "voidCellCount": level.get_void_cell_count(), "levelDataVersion": level.version}
		var loaded_plan := SupplyPlanLoader.load_engine(String(cand.get("supply_plan_path", "")), level)
		rec["supplyPlanLoaderPass"] = bool(loaded_plan.get("ok", false))
		if not loaded_plan.get("ok", false):
			rec["status"] = "MALFORMED"
			rec["supplyPlanError"] = loaded_plan.get("error", "loader rejected plan")
			out["results"].append(rec)
			print("BRIDGE %d/%d %s MALFORMED" % [i + 1, cands.size(), cand["id"]])
			continue
		var eng = loaded_plan["engine"]
		if cand.has("replay_trace"):  # differential replay of an external trace
			var rp: Dictionary = solver.replay(_initial(level, eng), cand["replay_trace"])
			rec["status"] = "REPLAY"
			rec["replay"] = {"ok": rp["ok"], "solved": rp["solved"], "finalActive": int(rp["final_active"]),
				"steps": int(rp["steps"]), "divergedAt": int(rp["diverged_at"])}
			out["results"].append(rec)
			print("BRIDGE %d/%d %s REPLAY ok=%s solved=%s" % [i + 1, cands.size(), cand["id"], rp["ok"], rp["solved"]])
			continue
		var t0 := Time.get_ticks_msec()
		var res: Dictionary = solver.solve(_initial(level, eng), cfg)
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
			var rp: Dictionary = solver.replay(_initial(level, eng), res["trace"])
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

func _initial(level, eng):
	return ProofState.from_level_and_supply(level, eng)

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
