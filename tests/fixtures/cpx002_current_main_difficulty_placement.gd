extends SceneTree

const LevelLoader = preload("res://scripts/data/level_loader.gd")
const SupplyPlanLoader = preload("res://scripts/gameplay/supply/supply_plan_loader.gd")
const Analyzer = preload("res://scripts/difficulty/level_difficulty_analyzer_v1.gd")
const Progression = preload("res://scripts/difficulty/difficulty_progression_v1.gd")
const RESULT_MARKER := "M03_F01_DIFFICULTY_PLACEMENT_JSON="
const EXPECTED_LEVEL_SHA256 := "c7801f47c5efe13b3577188e71c6fdae35190bd1a798676c8c41cae2f847de3d"
const EXPECTED_PLAN_SHA256 := "c7a70c8e25b93154124446f62dce106a129d7ee7816413755ea1d0dac8be5045"
const EXPECTED_CHALLENGE_SCORE := 48.8166775742989

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	print("M03_DIFFICULTY_STAGE=begin")
	var args := OS.get_cmdline_user_args()
	if args.size() != 5:
		_finish({"status": "FAIL", "reason": "expected level path, plan path, result path, game commit, and output path"}, 2, args)
		return
	var level_path: String = args[0]
	var plan_path: String = args[1]
	var result_path: String = args[2]
	var game_commit: String = args[3]
	var output_path: String = args[4]
	var level_text := FileAccess.get_file_as_string(level_path)
	var plan_text := FileAccess.get_file_as_string(plan_path)
	var result_text := FileAccess.get_file_as_string(result_path)
	if level_text.is_empty() or plan_text.is_empty() or result_text.is_empty():
		_finish({"status": "FAIL", "reason": "one or more exact 002 inputs could not be read"}, 2, args)
		return
	var level_hash := _sha256(level_text.to_utf8_buffer())
	var plan_hash := _sha256(plan_text.to_utf8_buffer())
	if level_hash != EXPECTED_LEVEL_SHA256 or plan_hash != EXPECTED_PLAN_SHA256:
		_finish({"status": "FAIL", "reason": "exact owner 002 LevelData or supply plan hash mismatch", "level_data_sha256": level_hash, "supply_plan_sha256": plan_hash}, 2, args)
		return
	var level_result = LevelLoader.load_from_text(level_text, level_path)
	if not level_result.is_ok():
		_finish({"status": "FAIL", "reason": "LevelLoader rejected the verified LevelData"}, 1, args)
		return
	var level = level_result.level_data
	var plan = JSON.parse_string(plan_text)
	var prior = JSON.parse_string(result_text)
	if typeof(plan) != TYPE_DICTIONARY or typeof(prior) != TYPE_DICTIONARY:
		_finish({"status": "FAIL", "reason": "supply plan or prior result is malformed"}, 1, args)
		return
	if plan.get("schema") != "scrubbots.level_supply_plan.v1" or plan.get("levelId") != level.id:
		_finish({"status": "FAIL", "reason": "LevelData and supply plan identities differ", "level_id": level.id}, 1, args)
		return
	if int(plan.get("columnCount", -1)) != 4 or int(plan.get("visiblePreviewDepth", -1)) != 3 or plan.get("columns", []).size() != 4:
		_finish({"status": "FAIL", "reason": "verified owner supply plan is not the expected four-column V2 plan"}, 1, args)
		return
	if prior.get("solver_status") != "SOLVED" or prior.get("solution_final") != "WIN" or prior.get("difficulty") != "MEDIUM":
		_finish({"status": "FAIL", "reason": "canonical saved solver/difficulty result is not the expected solved Medium record"}, 1, args)
		return
	var loaded := SupplyPlanLoader.build_engine(plan, level)
	print("M03_DIFFICULTY_STAGE=loaders_complete")
	if not loaded.get("ok", false):
		_finish({"status": "FAIL", "reason": "SupplyPlanLoader rejected the verified 4-FIFO plan", "loader_error": loaded.get("error", "")}, 1, args)
		return
	var saved_trace: Array = prior.get("solution_trace", [])
	print("M03_DIFFICULTY_STAGE=prior_result_loaded")
	if saved_trace.size() != 51:
		_finish({"status": "FAIL", "reason": "saved authenticated trace length differs from the prior 51-step proof", "trace_steps": saved_trace.size()}, 1, args)
		return
	var columns: Array = []
	var expected: Array = []
	for item in saved_trace:
		var column := int(item.get("column", 0)) - 1
		columns.append(column)
		expected.append({"column": column, "clears": int(item.get("clears", -1)), "active_after": int(item.get("pixels_left", -1))})
	var analyzer = Analyzer.new()
	print("M03_DIFFICULTY_STAGE=analyzer_constructed")
	if not analyzer.is_ok():
		_finish({"status": "FAIL", "reason": "current-main Difficulty V1 analyzer failed to load", "analyzer_error": analyzer.get_error()}, 1, args)
		return
	print("M03_DIFFICULTY_STAGE=measure_start steps=%d" % columns.size())
	var raw: Dictionary = analyzer.measure(level, loaded.engine, columns, expected)
	print("M03_DIFFICULTY_STAGE=trace_measured")
	if not raw.get("ok", false) or not raw.get("path", {}).get("solved", false):
		_finish({"status": "FAIL", "reason": "Difficulty V1 measurement did not validate the saved trace", "measure_error": raw.get("error", "")}, 1, args)
		return
	var progression = Progression.new()
	if not progression.is_ok():
		_finish({"status": "FAIL", "reason": "current-main Difficulty progression failed to load", "progression_error": progression.get_error()}, 1, args)
		return
	var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Progression.DEFAULT_CONFIG_PATH))
	var hard_tolerance := float(config.get("challengeTolerance", {}).get("neverForceLabelOutsidePlusMinus", -1.0))
	var catalog = JSON.parse_string(FileAccess.get_file_as_string("res://data/levels/catalog/production_catalog_v1.json"))
	print("M03_DIFFICULTY_STAGE=progression_loaded")
	if typeof(catalog) != TYPE_DICTIONARY or typeof(catalog.get("entries")) != TYPE_ARRAY:
		_finish({"status": "FAIL", "reason": "current-main production catalog is missing or malformed"}, 1, args)
		return
	var last_order := 0
	for entry in catalog.entries:
		if typeof(entry) == TYPE_DICTIONARY:
			last_order = maxi(last_order, int(entry.get("order", 0)))
	var next_order := last_order + 1
	var score := float(analyzer.score(raw, 1).get("challengeScore", -1.0))
	if not is_equal_approx(score, EXPECTED_CHALLENGE_SCORE):
		_finish({"status": "FAIL", "reason": "current-main Difficulty score differs from the measured M03-F01 baseline", "challenge_score": score, "expected_challenge_score": EXPECTED_CHALLENGE_SCORE}, 1, args)
		return
	var first_score_fit := {}
	for n in range(next_order, 1001):
		var target: Dictionary = progression.describe(n)
		if target.get("class") == prior.get("difficulty") and absf(score - float(target.get("target_challenge", 0.0))) <= hard_tolerance:
			first_score_fit = {"level_number": n, "target": target, "delta": score - float(target["target_challenge"])}
			break
	if first_score_fit.is_empty():
		_finish({"status": "FAIL", "reason": "no future score/class-compatible campaign slot was found through level 1000"}, 1, args)
		return
	var positions := [1, next_order, int(first_score_fit.level_number)]
	var placement_results := []
	var score_results := {}
	for n in positions:
		var scored: Dictionary = analyzer.score(raw, n)
		score_results[str(n)] = scored
		placement_results.append({"level_number": n, "target": progression.describe(n), "challenge_score": scored.get("challengeScore"), "delta": scored.get("signedDelta"), "acceptance_window": scored.get("acceptanceWindow")})
	var raw_summary := {}
	for key in ["ok", "dims", "color", "peel", "colorLayers", "path", "routes", "placements", "timing"]:
		if raw.has(key):
			raw_summary[key] = raw[key]
	var payload := {
		"schema": "scrubbots-m03-f01-native-difficulty-placement/v1",
		"status": "PASS",
		"source_game_commit": game_commit,
		"candidate_id": level.id,
		"level_data_sha256": level_hash,
		"supply_plan_sha256": plan_hash,
		"candidate_difficulty_class": prior.get("difficulty"),
		"campaign_catalog_last_order": last_order,
		"next_campaign_order": next_order,
		"level_loader_pass": true,
		"supply_plan_loader_pass": true,
		"saved_trace_measure_pass": true,
		"saved_trace_steps": columns.size(),
		"challenge_score": score,
		"challenge_vector": score_results[str(positions[0])].get("vector", {}),
		"profile": score_results[str(positions[0])].get("profile", {}),
		"session_load": score_results[str(positions[0])].get("sessionLoad", {}).get("value"),
		"score_is_independent_of_level_number": score_results[str(positions[0])].get("challengeScore") == score_results[str(positions[1])].get("challengeScore") and score_results[str(positions[1])].get("challengeScore") == score_results[str(positions[2])].get("challengeScore"),
		"campaign_positions": placement_results,
		"hard_tolerance": hard_tolerance,
		"first_future_medium_score_fit": first_score_fit,
		"placement_limit": "Score/class fit only; campaign sequence, pool, novelty and owner intent are not certified by this probe.",
		"raw": {"measure": raw_summary, "scores_by_level_number": score_results},
	}
	_finish(payload, 0, args)

func _finish(payload: Dictionary, code: int, args: Array) -> void:
	var output_path := String(args[4]) if args.size() == 5 else ""
	if not output_path.is_empty():
		var output := FileAccess.open(output_path, FileAccess.WRITE)
		if output == null:
			payload["evidence_write_error"] = "could not write evidence JSON (err %d)" % FileAccess.get_open_error()
			code = 2
		else:
			output.store_string(JSON.stringify(payload, "\t") + "\n")
			output.close()
	print(RESULT_MARKER + JSON.stringify(payload))
	quit(code)

func _sha256(raw: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(raw)
	return ctx.finish().hex_encode()
