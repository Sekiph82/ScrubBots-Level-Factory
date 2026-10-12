extends SceneTree
## Read-only native canary for the GitHub-pinned LF mini runtime.
## Exercises the real LevelData V2, loaders, VOID state, proof kernel/replay,
## and Difficulty V1 configuration without invoking SolvabilitySolver.solve.

const LevelData = preload("res://scripts/data/level_data.gd")
const LevelLoader = preload("res://scripts/data/level_loader.gd")
const ProductionLevelValidator = preload("res://scripts/data/production_level_validator.gd")
const SupplyPlanLoader = preload("res://scripts/gameplay/supply/supply_plan_loader.gd")
const ProofState = preload("res://scripts/gameplay/solver/proof_state.gd")
const ProofKernel = preload("res://scripts/gameplay/solver/proof_kernel.gd")
const SolvabilitySolver = preload("res://scripts/gameplay/solver/solvability_solver.gd")
const DifficultyAnalyzer = preload("res://scripts/difficulty/level_difficulty_analyzer_v1.gd")

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		printerr("usage: -- <original-owner-png>")
		quit(2)
		return
	var image := Image.new()
	if image.load(args[0]) != OK or image.get_width() != 32 or image.get_height() != 32:
		_fail("source PNG could not be read as the exact 32x32 owner input")
		return
	var palette_json = JSON.parse_string(FileAccess.get_file_as_string("res://data/palettes/scrubbots_palette_v3.json"))
	if typeof(palette_json) != TYPE_DICTIONARY or typeof(palette_json.get("colors")) != TYPE_ARRAY:
		_fail("pinned V3 palette authority did not load")
		return
	var rgb_to_color := {}
	var cid_to_rgb := {}
	for item in palette_json["colors"]:
		var rgb: Array = item.get("rgb", [])
		if rgb.size() != 3:
			_fail("pinned V3 palette entry has malformed RGB")
			return
		var key := "%d,%d,%d" % [int(rgb[0]), int(rgb[1]), int(rgb[2])]
		rgb_to_color[key] = {"cid": String(item["id"]), "hex": String(item["hex"]) + "FF"}
		cid_to_rgb[String(item["id"])] = key
	var counts := {}
	var used_colors: Array[String] = []
	var cells := PackedInt32Array()
	var void_count := 0
	for y in range(32):
		for x in range(32):
			var color := image.get_pixel(x, y)
			if color.a == 0.0:
				cells.append(LevelData.VOID_CELL)
				void_count += 1
				continue
			if color.a != 1.0:
				_fail("source PNG contains semitransparent pixels")
				return
			var key := "%d,%d,%d" % [roundi(color.r * 255.0), roundi(color.g * 255.0), roundi(color.b * 255.0)]
			if not rgb_to_color.has(key):
				_fail("source PNG contains a color outside the pinned game palette")
				return
			if not used_colors.has(key):
				used_colors.append(key)
			cells.append(used_colors.find(key))
			counts[key] = int(counts.get(key, 0)) + 1
	if void_count != 288 or cells.count(LevelData.VOID_CELL) != 288:
		_fail("source PNG VOID count differs from the approved 288-cell record")
		return
	var palette: Array[String] = []
	for key in used_colors:
		palette.append(String(rgb_to_color[key]["hex"]))
	var level_payload := {"version": LevelData.FORMAT_VERSION_VOID, "id": "r08_canary", "name": "R08 Canary",
		"difficulty": "EASY", "width": 32, "height": 32, "palette": palette, "cells": cells}
	var load_result = LevelLoader.load_from_text(JSON.stringify(level_payload), "R08 canary")
	if not load_result.is_ok():
		_fail("canonical LevelLoader rejected the original-source LevelData V2: %s" % str(load_result.errors))
		return
	var level = load_result.level_data
	var production = ProductionLevelValidator.validate(level)
	if not production.is_ok() or level.get_artwork_cell_count() != 736 or level.get_void_cell_count() != 288:
		_fail("ProductionLevelValidator or native LevelData V2 counts failed")
		return
	var columns: Array = [[], [], []]
	var color_index := 0
	for key in used_colors:
		var column := color_index % 3
		columns[column].append({"batchId": "r08-canary-%02d" % color_index,
			"cid": String(rgb_to_color[key]["cid"]), "robots": int(counts[key])})
		color_index += 1
	var plan := {"schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level.id,
		"columnCount": 3, "visiblePreviewDepth": 3, "maxRobotsPerBatch": 736, "columns": columns}
	var loaded_plan := SupplyPlanLoader.build_engine(plan, level)
	if not loaded_plan.get("ok", false):
		_fail("native SupplyPlanLoader rejected the canary plan: %s" % str(loaded_plan.get("error", "unknown")))
		return
	var initial = ProofState.from_level_and_supply(level, loaded_plan["engine"])
	if initial == null or initial.active_count() != 736:
		_fail("native ProofState did not initialize 736 active and 288 cleared VOID cells")
		return
	var kernel := ProofKernel.new()
	var quiet: Dictionary = kernel.quiesce(initial)
	if not quiet.get("ok", false) or quiet["state"].active_count() != 736:
		_fail("native ProofKernel quiescence failed")
		return
	var solver := SolvabilitySolver.new()
	var replay: Dictionary = solver.replay(initial, [])
	if not replay.get("ok", false) or replay.get("solved", true):
		_fail("native solver replay API did not operate on the initial proof state")
		return
	var analyzer := DifficultyAnalyzer.new()
	if not analyzer.is_ok():
		_fail("official Difficulty V1 configuration did not load: %s" % analyzer.get_error())
		return
	print("R08_CANARY_PASS level_data_v2=2 void=-1 void_cells=288 artwork_cells=736 loader=PASS production_validator=PASS supply_plan_loader=PASS proof_state=PASS proof_kernel=PASS solver_replay_api=PASS difficulty_v1_config=PASS solve_invocations=0")
	quit(0)

func _fail(message: String) -> void:
	printerr("R08_CANARY_FAIL " + message)
	quit(1)
