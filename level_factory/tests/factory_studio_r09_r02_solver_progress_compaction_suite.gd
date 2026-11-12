extends SceneTree

# Non-billable local UI regression: verified backend JSONL events are NOT
# rewritten; only the visible pipeline activity presentation is compacted.
const MAIN_SCENE := "res://scenes/factory_studio.tscn"
const SOURCE_ID := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"


func _init() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error("Solver activity compaction regression: " + message)
	quit(1)


func _event(sequence: int, elapsed_ms: int, stage: String, state: String, message: String) -> Dictionary:
	return {
		"seq": sequence,
		"elapsed_ms": elapsed_ms,
		"source_id": SOURCE_ID,
		"stage": stage,
		"state": state,
		"message": message,
	}


func _run() -> void:
	var scene := load(MAIN_SCENE) as PackedScene
	if scene == null:
		_fail("Factory Studio scene is unavailable")
		return
	var root_instance := scene.instantiate()
	root.add_child(root_instance)
	await process_frame
	var studio := root_instance.get_node_or_null("MasterUI")
	if studio == null:
		_fail("MasterUI is missing")
		return
	var rows := studio.get_node_or_null("PipelineActivityPanel/PipelineActivityScroll/PipelineActivityRows") as VBoxContainer
	if rows == null:
		_fail("Activity row container is missing")
		return
	studio.set("_activity_source_id", SOURCE_ID)
	studio.set("_selected_import_source_id", SOURCE_ID)
	studio.call("_clear_activity_rows")

	# Backend reports a prefixed progress message as ANALYZE/PLAN, followed by
	# many solver heartbeats. They must occupy the SAME UI row.
	studio.call("_append_activity_row", _event(1, 6000, "ANALYZE/PLAN", "RUNNING",
		"game solver: BRIDGE_SOLVER_PROGRESS phase=Solving elapsed=5.0s"))
	if rows.get_child_count() != 1 or not str(rows.get_child(0).text).contains("00:05"):
		_fail("First five-second solver progress must occupy one row")
		return
	studio.call("_append_activity_row", _event(2, 11000, "ANALYZE/PLAN", "RUNNING",
		"game solver: BRIDGE_SOLVER_PROGRESS phase=Solving elapsed=10.0s"))
	studio.call("_append_activity_row", _event(3, 16000, "ANALYZE/PLAN", "RUNNING",
		"game solver: BRIDGE_SOLVER_PROGRESS phase=Solving elapsed=15.0s"))
	if rows.get_child_count() != 1 or not str(rows.get_child(0).text).contains("00:15"):
		_fail("Later heartbeats added extra rows or elapsed did not advance")
		return

	studio.call("_append_activity_row", _event(4, 17321, "SOLVE", "PASS",
		"Canonical solver result: SOLVED."))
	if rows.get_child_count() != 1 or not str(rows.get_child(0).text).contains("PASS") or not str(rows.get_child(0).text).contains("Total 00:16"):
		_fail("Terminal solver PASS must update the same row with total duration")
		return
	studio.call("_append_activity_row", _event(5, 17500, "REPLAY", "PASS",
		"Canonical replay result: WIN."))
	# Activity rows list the newest event first since f3003d98 (2026-11-08).
	if rows.get_child_count() != 2 or not str(rows.get_child(0).text).contains("REPLAY"):
		_fail("Pipeline must continue appending other distinct phase events")
		return
	studio.call("_clear_activity_rows")
	if rows.get_child_count() != 0 or studio.get("_activity_solver_row") != null:
		_fail("A new source/run must clear the prior solver summary")
		return
	studio.call("_append_activity_row", _event(1, 2000, "SOLVE", "RUNNING",
		"BRIDGE_SOLVER_PROGRESS phase=Solving elapsed=1.0s"))
	studio.call("_append_activity_row", _event(2, 6000, "SOLVE", "UNAVAILABLE",
		"Solver did not produce a verifiable result."))
	if rows.get_child_count() != 1 or not str(rows.get_child(0).text).contains("UNAVAILABLE") or not str(rows.get_child(0).text).contains("Total"):
		_fail("Failed solver result must complete the single row truthfully")
		return
	root_instance.queue_free()
	print("Solver Activity Compaction: PASS")
	quit(0)
