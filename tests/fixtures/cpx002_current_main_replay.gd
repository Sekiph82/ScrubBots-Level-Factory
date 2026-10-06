extends SceneTree

const LevelLoader = preload("res://scripts/data/level_loader.gd")
const SupplyPlanLoader = preload("res://scripts/gameplay/supply/supply_plan_loader.gd")
const ProofState = preload("res://scripts/gameplay/solver/proof_state.gd")
const ProofKernel = preload("res://scripts/gameplay/solver/proof_kernel.gd")
const SolvabilitySolver = preload("res://scripts/gameplay/solver/solvability_solver.gd")
const MARKER := "CPX002_RESULT_JSON="

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		_emit({"accepted": false, "reason": "job path required"}, 2)
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if typeof(parsed) != TYPE_DICTIONARY or typeof(parsed.get("levels")) != TYPE_ARRAY or parsed.levels.is_empty():
		_emit({"accepted": false, "reason": "invalid job"}, 2)
		return
	var rows: Array = []
	for item in parsed.levels:
		var row := _verify_level(item)
		rows.append(row)
		if not row.get("accepted", false):
			_emit({"accepted": false, "levels": rows}, 1)
			return
	_emit({"accepted": true, "levels": rows}, 0)

func _verify_level(item: Dictionary) -> Dictionary:
	var level_file := FileAccess.get_file_as_string(String(item.get("level_path", "")))
	var plan_file := FileAccess.get_file_as_string(String(item.get("plan_path", "")))
	var level_raw := level_file.to_utf8_buffer()
	var plan_raw := plan_file.to_utf8_buffer()
	var level_hash := _sha256(level_raw)
	var plan_hash := _sha256(plan_raw)
	var level_result = LevelLoader.load_from_text(level_file, String(item.get("level_path", "")))
	if not level_result.is_ok():
		return {"accepted": false, "reason": "level loader rejected", "level_id": item.get("level_id")}
	var level = level_result.level_data
	var plan = JSON.parse_string(plan_file)
	if typeof(plan) != TYPE_DICTIONARY or plan.get("schema") != "scrubbots.level_supply_plan.v1" or plan.get("levelId") != item.get("level_id") or level.id != item.get("level_id"):
		return {"accepted": false, "reason": "schema or level mismatch", "level_id": item.get("level_id")}
	if level_hash != item.get("level_sha256") or plan_hash != item.get("plan_sha256") or plan.get("columns") != item.get("fifo_columns"):
		return {"accepted": false, "reason": "identity mismatch", "level_id": item.get("level_id")}
	var engine_result: Dictionary = SupplyPlanLoader.build_engine(plan, level)
	if not engine_result.get("ok", false):
		return {"accepted": false, "reason": "supply loader rejected", "level_id": item.get("level_id")}
	var engine = engine_result.engine
	var proof = ProofState.from_level_and_supply(level, engine)
	var solver = SolvabilitySolver.new()
	var solved: Dictionary = solver.solve(proof, {"max_visited": 500000, "max_depth": 1000})
	if solved.get("status") != SolvabilitySolver.SOLVED:
		return {"accepted": false, "reason": "solver not solved", "solver_status": solved.get("status"), "level_id": item.get("level_id")}
	var replay: Dictionary = solver.replay(ProofState.from_level_and_supply(level, engine), solved.get("trace", []))
	if replay.get("ok") != true or replay.get("solved") != true:
		return {"accepted": false, "reason": "replay rejected", "level_id": item.get("level_id")}
	var initial = ProofState.from_level_and_supply(level, engine)
	var quiesced: Dictionary = ProofKernel.new().quiesce(initial)
	if not quiesced.get("ok", false):
		return {"accepted": false, "reason": "initial kernel state rejected", "level_id": item.get("level_id")}
	var final_state = quiesced.state
	var kernel = ProofKernel.new()
	for action in solved.get("trace", []):
		var step: Dictionary = kernel.apply_placement(final_state, int(action["column"]))
		if not step.get("ok", false):
			return {"accepted": false, "reason": "kernel replay rejected", "level_id": item.get("level_id")}
		final_state = step.state
	var active: int = final_state.active_count()
	var unresolved: int = final_state.occupied_slot_count()
	var plan_columns: Array = plan.get("columns", [])
	var fifo_exact: bool = plan_columns == item.get("fifo_columns") and int(plan.get("columnCount", -1)) == plan_columns.size() and int(plan.get("visiblePreviewDepth", -1)) == 3
	if not fifo_exact or active != 0 or unresolved != 0 or not final_state.is_supply_exhausted() or not final_state.is_solved():
		return {"accepted": false, "reason": "FIFO or final state mismatch", "level_id": item.get("level_id")}
	return {"accepted": true, "level_id": level.id, "level_sha256": level_hash, "plan_sha256": plan_hash,
		"fifo_columns": plan_columns, "solver_status": solved.get("status"), "replay_ok": replay.get("ok"),
		"replay_solved": replay.get("solved"), "final_active": active, "unresolved": unresolved,
		"supply_exhausted": final_state.is_supply_exhausted(), "solver_state_sha256": item.get("solver_state_sha256"),
		"solver_evidence_sha256": item.get("solver_evidence_sha256")}

func _sha256(raw: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(raw)
	return ctx.finish().hex_encode()

func _emit(payload: Dictionary, code: int) -> void:
	print(MARKER + JSON.stringify(payload))
	quit(code)
