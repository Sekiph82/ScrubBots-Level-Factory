extends SceneTree

const MAIN_SCENE := "res://scenes/factory_studio.tscn"
const PINNED_SOURCE_ID := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const PINNED_SOURCE_SHA := "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const PINNED_GAME_COMMIT := "aef60a616d4ac401e9dfac15df6fe56e671c0053"


class FakeGateway extends RefCounted:
	const FAKE_PINNED_SOURCE_ID := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
	const FAKE_PINNED_SOURCE_SHA := "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
	var prepare_count := 0
	var execute_count := 0
	var prepared_operation := ""
	var prepared_payload: Dictionary = {}

	func run_studio_extension(operation: String, request: Dictionary) -> Dictionary:
		if operation == "validate-source-readonly" and str(request.get("source_id", "")) == FAKE_PINNED_SOURCE_ID:
			return {
				"source_sha256": FAKE_PINNED_SOURCE_SHA,
				"exact_logical_source": true,
				"void_capability": {"state": "OPEN", "runtime_kind": "LF_PINNED_SOURCE_MINIMAL_RUNTIME"},
				"structural": {"disposition": "PASS"},
			}
		if operation == "validate-source-readonly":
			return {"void_capability": {"state": "CLOSED", "reason_code": "PINNED_SOURCE_SCOPE_NOT_VERIFIED"}}
		return {}

	func prepare_studio_extension_call(operation: String, request: Dictionary) -> Dictionary:
		prepare_count += 1
		prepared_operation = operation
		prepared_payload = request.duplicate(true)
		return {"fake": true}

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		execute_count += 1
		return {"disposition": "UNAVAILABLE", "state": "UNAVAILABLE", "stages": []}


func _init() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error("R09-R02-R02 pinned authority UI suite: " + message)
	quit(1)


func _run() -> void:
	var packed := load(MAIN_SCENE) as PackedScene
	if packed == null:
		_fail("installed Factory Studio scene did not load")
		return
	var instance := packed.instantiate()
	var studio := instance.get_node_or_null("MasterUI")
	if studio == null:
		_fail("MasterUI is missing")
		return
	var gateway := FakeGateway.new()
	root.add_child(instance)
	studio.set("_gateway", gateway)
	await process_frame
	studio.size = Vector2(1536, 1024)
	studio.call("_apply_responsive_layout")

	for name in ["PIXEL ART", "LEVEL FACTORY", "RELEASE POOL", "LEVEL FACTORY", "PIXEL ART"]:
		studio.call("_show_screen", name)
		await process_frame
		if studio.get_node_or_null("_level_number_label") != null:
			_fail("orphan Level Auto label remains on " + name)
			return
		var level_button := studio.get_node_or_null("LevelNumber") as Button
		if level_button == null or level_button.text != "Level: Auto":
			_fail("single Level: Auto caption is missing or duplicated on " + name)
			return
		if level_button.visible != (name == "LEVEL FACTORY"):
			_fail("LevelNumber visibility leaked across master tabs")
			return
	var release_search := studio.get_node_or_null("ReleaseSearch") as Button
	if release_search == null or release_search.text != "Search levels":
		_fail("Release Pool search caption changed")
		return

	var spin := studio.get("_level_number_input") as SpinBox
	spin.value = 23
	studio.call("_save_level_number")
	if (studio.get_node("LevelNumber") as Button).text != "Level: 23" or not bool(studio.get("_manual_level_override")):
		_fail("manual level override did not update the sole button caption")
		return

	var image_path := "res://assets/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.png"
	for index in range(12):
		var source_id := PINNED_SOURCE_ID if index == 0 else "owner-upload-%064x" % (index + 1)
		var size := Vector2i(32, 32) if index < 9 else Vector2i(1536, 1024)
		studio.call("_upsert_imported_source", {
			"source_id": source_id,
			"source_sha256": PINNED_SOURCE_SHA if index == 0 else source_id.trim_prefix("owner-upload-"),
			"path": image_path if index == 0 else "",
			"display_filename": "002_32x32px.png" if index == 0 else "source_%02d.png" % index,
			"disposition": "SOURCE_ONLY",
			"width": size.x,
			"height": size.y,
		})
	studio.set("_selected_import_source_id", "")
	studio.call("_select_imported_source_by_id", PINNED_SOURCE_ID)
	studio.call("_refresh_runtime_cards")
	await process_frame
	var gameplay_sources: Array = studio.get("_gameplay_sources")
	if gameplay_sources.size() != 9:
		_fail("gameplay thumbnail view did not filter 12 source records to the 9 logical-size PNGs")
		return
	if str(studio.get("_selected_import_source_id")) != PINNED_SOURCE_ID:
		_fail("restore did not select the exact attested owner source")
		return
	studio.call("_show_screen", "LEVEL FACTORY")
	await process_frame
	if int(gateway.prepare_count) != 0 or int(gateway.execute_count) != 0:
		_fail("PNG restore or pin preflight invoked a pipeline worker")
		return
	if not bool(studio.get("_pinned_source_preflight_ok")):
		_fail("fake no-solver source/VOID preflight did not pass")
		return
	var source_label := studio.get("_activity_source_label") as Label
	if source_label == null or not source_label.text.begins_with("002_32x32px.png"):
		_fail("idle Activity source does not match the selected preview")
		return
	var preview := studio.get("_preview_rect") as TextureRect
	if preview == null or not preview.visible:
		_fail("selected source preview is not visible")
		return

	studio.call("_show_screen", "PIXEL ART")
	if preview.visible:
		_fail("LEVEL FACTORY preview leaked into PIXEL ART")
		return
	studio.call("_show_screen", "RELEASE POOL")
	if preview.visible:
		_fail("LEVEL FACTORY preview leaked into RELEASE POOL")
		return
	studio.call("_show_screen", "LEVEL FACTORY")
	if not preview.visible:
		_fail("selected LEVEL FACTORY preview did not restore")
		return

	var route: Dictionary = studio.call("_build_selected_source_pipeline_request")
	var expected_root := ProjectSettings.globalize_path("res://output/current-game-runtime/%s" % PINNED_GAME_COMMIT).simplify_path()
	var request: Dictionary = route.get("request", {})
	if str(route.get("state", "")) != "AUTHORIZED_SOURCE_SCOPE" or str(route.get("source_id", "")) != PINNED_SOURCE_ID or str(route.get("source_sha256", "")) != PINNED_SOURCE_SHA or str(request.get("game_project", "")) != expected_root:
		_fail("Run request builder did not bind selected source and task-owned pinned game root")
		return
	if gateway.prepare_count != 0 or gateway.execute_count != 0:
		_fail("source selection or request preparation invoked a solver/pipeline worker")
		return
	studio.set("_selected_import_source_id", "owner-upload-%064x" % 99)
	studio.call("_run_level_pipeline")
	if gateway.prepare_count != 0 or str(studio.get("_pinned_source_preflight_message")) != "PINNED_SOURCE_SCOPE_NOT_VERIFIED":
		_fail("an unapproved upload was not blocked before the fake worker")
		return

	instance.free()
	await process_frame
	print("R09-R02-R02 pinned authority UI focused suite: PASS (tabs, manual caption, 9/12 view, selected source, pinned Run request; zero pipeline workers)")
	quit(0)
