extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PINNED_SOURCE_ID := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"


func _initialize() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error("R09-R02-R03 budget request UI suite: " + message)
	quit(1)


func _run() -> void:
	var studio := UI_SCRIPT.new()
	studio.set("_selected_import_source_id", PINNED_SOURCE_ID)
	studio.set("_pinned_source_preflight_ok", true)
	for columns in [3, 4, 5]:
		studio.set("_column_count", columns)
		var built: Dictionary = studio.call("_build_selected_source_pipeline_request")
		var request: Dictionary = built.get("request", {})
		if str(built.get("source_id", "")) != PINNED_SOURCE_ID:
			_fail("request escaped the single attested PNG source")
			return
		if int(request.get("column_count", -1)) != columns:
			_fail("selected supply columns changed while building the pipeline request")
			return
		if int(request.get("real_max_visited", -1)) != 25000 or int(request.get("solver_timeout_seconds", -1)) != 240:
			_fail("the explicit pinned solver bounds are missing or changed")
			return
	studio.set("_column_count", 4)
	var owner_request: Dictionary = studio.call("_build_selected_source_pipeline_request")
	if owner_request.get("request", {}).get("column_count") != 4:
		_fail("owner-selected 4-column request was not preserved")
		return
	studio.set("_selected_import_source_id", "owner-upload-" + "f".repeat(64))
	if str(studio.call("_build_selected_source_pipeline_request").get("reason", "")) != "PINNED_SOURCE_SCOPE_NOT_VERIFIED":
		_fail("another owner PNG was not blocked by the exact source pin")
		return
	studio.free()
	print("R09-R02-R03 budget request UI suite: PASS (3/4/5 columns, 25000 visits, 240 seconds, one pinned source; zero workers)")
	quit(0)
