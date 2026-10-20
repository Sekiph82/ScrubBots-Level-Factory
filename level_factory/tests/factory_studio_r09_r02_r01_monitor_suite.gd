extends SceneTree

const MAIN_SCENE := "res://scenes/factory_studio.tscn"
const RUN_ID := "pipeline-ui-20261012T170355Z-97fdc47b8773"
const SOURCE_ID := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const SOURCE_SHA := "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const ZERO_HASH := "0000000000000000000000000000000000000000000000000000000000000000"
const EXPECTED_EVENT_HASHES := [
	"1739a4cd12afaca39553ed9a061374f7c9f47c90f712feb0260a5cef3d63544f",
	"4be7e26c9e2e9b76240f56df2248866bd9875fef6f2c91027206405b2a915098",
	"080dfc831d78afbd774c009eddbca0c16d6771d4f55ef3a5c16096f15ee262a3",
	"2a3fdbc96a1f641249b5a700bbcf242a9c2337f616ed292c381c34e22ca9e444",
	"fdf1dd03a13c2b282bb81177d69af6deed325f8e3be2d4791ddfea0c9d1e07e5",
]


class FakeAppendReader extends RefCounted:
	var bytes := PackedByteArray()

	func get_length() -> int:
		return bytes.size()

	func read_from(offset: int) -> PackedByteArray:
		return bytes.slice(offset)

	func append(value: PackedByteArray) -> void:
		bytes.append_array(value)


class FakeGateway extends RefCounted:
	var library_payload: Dictionary = {}
	var operations: Array[String] = []
	var prepare_count := 0
	var execute_count := 0
	var delay_msec := 0
	var pipeline_result: Dictionary = {}

	func run_studio_extension(operation: String, _request: Dictionary) -> Dictionary:
		operations.append(operation)
		if operation == "library-refresh": return library_payload
		return {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE"}

	func prepare_studio_extension_call(_operation: String, _request: Dictionary) -> Dictionary:
		prepare_count += 1
		return {"fake_worker": true}

	func execute_prepared_studio_extension_call(_prepared: Dictionary) -> Dictionary:
		execute_count += 1
		if delay_msec > 0: OS.delay_msec(delay_msec)
		return pipeline_result.duplicate(true)


func _init() -> void:
	call_deferred("_run")


func _fail(message: String) -> void:
	push_error("R09-R02-R01 monitor test: " + message)
	quit(1)


func _free_studio(studio: Node) -> void:
	if studio == null:
		return
	var scene_root := studio.get_parent()
	if scene_root != null:
		scene_root.free()
	await process_frame


func _make_studio() -> Node:
	var packed := load(MAIN_SCENE) as PackedScene
	if packed == null:
		_fail("Factory Studio scene did not load")
		return null
	var instance := packed.instantiate()
	root.add_child(instance)
	var workspace := instance.get_node_or_null("Frame/Layout/Body/Workspace")
	if workspace != null and workspace.get("owner_projection") is Dictionary and not (workspace.get("owner_projection") as Dictionary).is_empty():
		_fail("hidden legacy workspace loaded the synchronous owner-pages projection during startup")
		return null
	var studio := instance.get_node_or_null("MasterUI")
	if studio != null:
		# Prevent the scene's deferred startup restore from calling the real
		# owner-data gateway during this offline UI suite.
		studio.call("configure_gateway", FakeGateway.new())
		studio.set("_studio_read_queue", [])
	await process_frame
	if studio == null:
		_fail("Master UI controller did not load")
		return null
	studio.size = Vector2(1536, 1024)
	studio.call("_apply_responsive_layout")
	return studio


func _activity_body(seq: int) -> Dictionary:
	var definitions := [
		["SOURCE", "RUNNING", 0, "Validating the selected immutable PNG source."],
		["SOURCE", "PASS", 94, "Backend source validation completed."],
		["NORMALIZE/DERIVE", "BLOCKED", 95, "DERIVED_ARTIFACT_REQUIRED — no implicit transform."],
		["VOID VALIDATION", "UNAVAILABLE", 120, "SCRUBBOTS_PROJECT is not configured for current-game authority."],
		["PIPELINE", "UNAVAILABLE", 121, "PALETTE/STRUCTURE VALIDATION: SCRUBBOTS_PROJECT is not configured for current-game authority."],
	]
	var item: Array = definitions[seq - 1]
	var body := {
		"seq": seq,
		"run_id": RUN_ID,
		"source_id": SOURCE_ID,
		"source_sha256": SOURCE_SHA,
		"stage": item[0],
		"state": item[1],
		"elapsed_ms": item[2],
		"message": item[3],
		"previous_sha256": ZERO_HASH if seq == 1 else EXPECTED_EVENT_HASHES[seq - 2],
	}
	if seq == 5:
		body["backend_disposition"] = "UNAVAILABLE"
	return body


func _event_line(seq: int, corrupt_hash: bool = false) -> PackedByteArray:
	var body := _activity_body(seq)
	var canonical := JSON.stringify(body, "", true, true)
	var hash_ctx := HashingContext.new()
	hash_ctx.start(HashingContext.HASH_SHA256)
	hash_ctx.update(canonical.to_utf8_buffer())
	var digest := hash_ctx.finish().hex_encode()
	if digest != EXPECTED_EVENT_HASHES[seq - 1]:
		_fail("Godot canonical event JSON disagrees with the Python SHA-256 vector at sequence %d" % seq)
	if corrupt_hash:
		digest = ZERO_HASH
	var line := JSON.stringify({"body": body, "body_sha256": digest}, "", true, true)
	var bytes := line.to_utf8_buffer()
	bytes.append(10)
	return bytes


func _set_activity_identity(studio: Node, reader: FakeAppendReader, operation_running: bool = true) -> void:
	studio.set("_activity_stream_reader_override", reader)
	studio.set("_activity_run_id", RUN_ID)
	studio.set("_activity_source_id", SOURCE_ID)
	studio.set("_activity_source_sha256", SOURCE_SHA)
	studio.set("_activity_source_filename", "002_32x32px.png")
	studio.set("_activity_started_msec", Time.get_ticks_msec())
	studio.set("_activity_finished_msec", 0)
	studio.set("_activity_seen_sequence", 0)
	studio.set("_activity_read_offset", 0)
	studio.set("_activity_pending_bytes", PackedByteArray())
	studio.set("_activity_previous_sha256", ZERO_HASH)
	studio.set("_activity_terminal_state", "")
	studio.set("_activity_backend_disposition", "")
	studio.set("_activity_event_backend_disposition", "")
	studio.set("_activity_integrity_error", "")
	studio.set("_activity_events", [])
	studio.set("_activity_stage", "QUEUED")
	studio.set("_activity_message", "Waiting for backend stage events.")
	studio.set("_operation_running", operation_running)


func _backend_result() -> Dictionary:
	return {
		"run_id": "pipeline-offline-test",
		"disposition": "UNAVAILABLE",
		"request": {"game_project": ""},
		"stages": [
			{"stage": "NORMALIZE/DERIVE", "disposition": "BLOCKED", "reason": "DERIVED_ARTIFACT_REQUIRED — no implicit transform."},
			{"stage": "PALETTE/STRUCTURE VALIDATION", "disposition": "UNAVAILABLE", "reason": "SCRUBBOTS_PROJECT is not configured for current-game authority."},
		],
	}


func _test_layout_and_valid_incremental_stream(studio: Node) -> bool:
	var panel := studio.get_node_or_null("PipelineActivityPanel") as Panel
	var title := studio.get_node_or_null("PipelineActivityPanel/PipelineActivityTitle") as Label
	var state_label := studio.get_node_or_null("PipelineActivityPanel/PipelineActivityStateChip/PipelineActivityState") as Label
	var scroll := studio.get_node_or_null("PipelineActivityPanel/PipelineActivityScroll") as ScrollContainer
	var button := studio.get_node_or_null("RunLevelPipeline") as Button
	if panel == null or title == null or state_label == null or scroll == null or button == null:
		_fail("scrollable activity controls or Run Pipeline are missing: panel=%s title=%s state=%s scroll=%s button=%s paths=%s" % [panel != null, title != null, state_label != null, scroll != null, button != null, studio.get_path()])
		return false
	if panel.position != Vector2(27, 412) or panel.size != Vector2(334, 498):
		_fail("activity panel does not occupy the owner-approved lower workspace")
		return false
	if (studio.get_node("SelectArtwork") as Button).position != Vector2(42, 165):
		_fail("Select PNG moved from its visual-master location")
	if (studio.get_node("LevelNumber") as Button).position != Vector2(172, 165):
		_fail("level settings are not top-right beside Select PNG")
	for spec in [["SupplyColumns3", Vector2(172, 209)], ["SupplyColumns4", Vector2(238, 209)], ["SupplyColumns5", Vector2(304, 209)], ["MaxRobotsAuto", Vector2(172, 253)], ["BackgroundIntent", Vector2(172, 297)], ["RunLevelPipeline", Vector2(26, 347)]]:
		if (studio.get_node(str(spec[0])) as Button).position != spec[1]:
			_fail("owner control geometry changed for %s" % spec[0])
			return false
	if panel.visible or title.is_visible_in_tree() or state_label.is_visible_in_tree() or state_label.text != "IDLE":
		_fail("activity leaked into the initial PIXEL ART screen")
		return false
	studio.call("_show_screen", "LEVEL FACTORY")
	if not panel.visible:
		_fail("activity panel did not appear in LEVEL FACTORY")
		return false
	var reader := FakeAppendReader.new()
	_set_activity_identity(studio, reader)
	var first := _event_line(1)
	var first_cut := mini(20, first.size())
	reader.append(first.slice(0, first_cut))
	studio.call("_poll_pipeline_activity")
	if int(studio.get("_activity_seen_sequence")) != 0:
		_fail("partial JSONL tail was consumed before its newline")
		return false
	reader.append(first.slice(first_cut))
	studio.call("_poll_pipeline_activity")
	if int(studio.get("_activity_seen_sequence")) != 1:
		_fail("first incremental event did not verify: integrity=%s pending=%d offset=%d" % [studio.get("_activity_integrity_error"), (studio.get("_activity_pending_bytes") as PackedByteArray).size(), int(studio.get("_activity_read_offset"))])
		return false
	reader.append(_event_line(2))
	studio.call("_poll_pipeline_activity")
	if int(studio.get("_activity_seen_sequence")) != 2:
		_fail("second poll re-read sequence one instead of consuming the append")
		return false
	var unicode_event := _event_line(3)
	var unicode_cut := unicode_event.find(0xE2)
	if unicode_cut < 0:
		_fail("UTF-8 test event did not contain its em dash")
		return false
	reader.append(unicode_event.slice(0, unicode_cut + 1))
	studio.call("_poll_pipeline_activity")
	if int(studio.get("_activity_seen_sequence")) != 2:
		_fail("incomplete multi-byte UTF-8 line was consumed")
		return false
	reader.append(unicode_event.slice(unicode_cut + 1))
	studio.call("_poll_pipeline_activity")
	if int(studio.get("_activity_seen_sequence")) != 3:
		_fail("UTF-8 event did not verify after the remainder was appended")
		return false
	reader.append(_event_line(4))
	studio.call("_poll_pipeline_activity")
	reader.append(_event_line(5))
	studio.call("_poll_pipeline_activity")
	if int(studio.get("_activity_seen_sequence")) != 5 or str(studio.get("_activity_integrity_error")) != "":
		_fail("five independently appended events did not retain one valid hash chain")
		return false
	studio.call("_complete_level_pipeline", _backend_result())
	if state_label.text != "UNAVAILABLE" or str(studio.get("_activity_stage")) != "PIPELINE":
		_fail("verified UNAVAILABLE terminal did not reconcile with the canonical backend result")
		return false
	var details := studio.get_node("RuntimeLiveData") as Label
	if details.text.find("SCRUBBOTS_PROJECT is not configured for current-game authority") < 0 or details.text.find("Replay: —") < 0:
		_fail("Details hid the real game-authority stop reason or invented replay data")
		return false
	if (studio.get_node("RunLevelPipeline") as Button).disabled:
		_fail("Run Pipeline remained disabled after the worker reached a terminal state")
		return false
	for screen in ["PIXEL ART", "RELEASE POOL"]:
		studio.call("_show_screen", screen)
		if panel.visible:
			_fail("activity leaked outside LEVEL FACTORY")
			return false
	studio.call("_show_screen", "LEVEL FACTORY")
	if not panel.visible or scroll.get_child_count() != 1:
		_fail("activity/scroll state did not survive tab switching")
		return false
	return true


func _test_fail_closed_tamper(studio: Node) -> bool:
	var reader := FakeAppendReader.new()
	_set_activity_identity(studio, reader)
	reader.append(_event_line(1, true))
	studio.call("_poll_pipeline_activity")
	if str(studio.get("_activity_integrity_error")).is_empty() or int(studio.get("_activity_seen_sequence")) != 0:
		_fail("altered body digest did not fail closed")
		return false
	studio.set("_activity_terminal_state", "READY")
	studio.set("_activity_event_backend_disposition", "READY")
	var ready_result := _backend_result()
	ready_result["disposition"] = "READY"
	ready_result["stages"] = []
	ready_result["primary"] = {"state": "READY", "acceptance": {"replay": "WIN"}, "difficulty": {"class": "Easy"}}
	studio.call("_complete_level_pipeline", ready_result)
	studio.call("_show_screen", "LEVEL FACTORY")
	var details := studio.get_node("RuntimeLiveData") as Label
	if str(studio.get("_last_pipeline").get("studio_monitor_validation", "")) != "FAILED_CLOSED" or details.text.find("Solver: ERROR") < 0 or details.text.find("Replay: —") < 0:
		_fail("backend READY escaped an invalid monitor's fail-closed gate")
		return false
	return true


func _test_restored_import_order(studio: Node) -> bool:
	var gateway := FakeGateway.new()
	var paths := [
		"tests/fixtures/factory_studio_r04_r01/import_01_20x20.png",
		"tests/fixtures/factory_studio_r04_r01/import_02_20x59.png",
		"tests/fixtures/factory_studio_r04_r01/import_03_32x32.png",
		"tests/fixtures/factory_studio_r04_r01/import_04_59x20.png",
	]
	var sources: Array[Dictionary] = []
	var ids: Array[String] = []
	for relative in paths:
		var path := ProjectSettings.globalize_path("res://").path_join(relative)
		var bytes := FileAccess.get_file_as_bytes(path)
		if bytes.is_empty():
			_fail("verified import fixture is missing: %s" % relative)
			return false
		var hash_ctx := HashingContext.new()
		hash_ctx.start(HashingContext.HASH_SHA256)
		hash_ctx.update(bytes)
		var digest := hash_ctx.finish().hex_encode()
		var source_id := "owner-upload-" + digest
		ids.append(source_id)
		sources.append({"source_id": source_id, "source_sha256": digest, "immutable_source_path": "level_factory/" + relative, "original_filename": relative.get_file()})
	gateway.library_payload = {"schema": "scrubbots-source-library-view", "sources": sources}
	studio.call("configure_gateway", gateway)
	studio.get("_imported_sources").clear()
	studio.set("_selected_import_source_id", "")
	studio.call("_restore_imported_sources")
	var queue: Array = studio.call("imported_queue_snapshot")
	if queue.size() != 4:
		_fail("read-only verified library restore did not recover four immutable sources")
		return false
	if "owner-pages" in gateway.operations or "library-refresh" not in gateway.operations or "loaded-png-batch-find" not in gateway.operations:
		_fail("source restore called an unrelated synchronous owner-pages projection: %s" % str(gateway.operations))
		return false
	for index in range(4):
		if str(queue[index].get("source_id", "")) != ids[index] or str(queue[index].get("disposition", "")) != "SOURCE_ONLY":
			_fail("source queue order or SOURCE_ONLY status changed during restoration")
			return false
	studio.call("_select_imported_source_by_id", ids[1])
	if str(studio.get("_selected_import_source_id")) != ids[1] or str(studio.get("_last_source_id")) != ids[1]:
		_fail("selection did not retain the immutable source identity")
		return false
	studio.call("_show_screen", "PIXEL ART")
	if (studio.get("_preview_rect") as TextureRect).visible:
		_fail("restored PNG preview leaked into PIXEL ART")
		return false
	studio.call("_show_screen", "LEVEL FACTORY")
	if (studio.get("_preview_rect") as TextureRect).texture == null:
		_fail("selected restored PNG did not return with its LEVEL FACTORY preview")
		return false
	if bool(studio.get("_operation_running")) or studio.get("_pipeline_thread") != null or gateway.execute_count != 0:
		_fail("read-only import restoration automatically invoked the pipeline")
		return false
	return true


func _test_slow_worker_stream(studio: Node) -> bool:
	var gateway := FakeGateway.new()
	gateway.delay_msec = 1300
	gateway.pipeline_result = _backend_result()
	studio.call("configure_gateway", gateway)
	var reader := FakeAppendReader.new()
	_set_activity_identity(studio, reader)
	studio.set("_activity_source_filename", "002_32x32px.png")
	studio.set("_last_source_id", SOURCE_ID)
	studio.set("_selected_import_source_id", SOURCE_ID)
	var thread := Thread.new()
	if thread.start(Callable(studio, "_pipeline_worker").bind({"fake_worker": true})) != OK:
		_fail("fake delayed worker did not start")
		return false
	var frames := 0
	reader.append(_event_line(1))
	while frames < 3:
		await create_timer(0.1).timeout
		await process_frame
		studio.call("_poll_pipeline_activity")
		frames += 1
	if int(studio.get("_activity_seen_sequence")) != 1 or not thread.is_alive():
		_fail("UI did not consume the first real append while the fake worker remained active")
		thread.wait_to_finish()
		return false
	reader.append(_event_line(2))
	for _frame in range(3):
		await create_timer(0.1).timeout
		await process_frame
		studio.call("_poll_pipeline_activity")
		frames += 1
	if int(studio.get("_activity_seen_sequence")) != 2 or not thread.is_alive() or frames < 6:
		_fail("second append was not visible during the slow worker's lifetime")
		thread.wait_to_finish()
		return false
	studio.call("_run_level_pipeline")
	if gateway.prepare_count != 0:
		_fail("a second Run Pipeline click dispatched another worker while the first was active")
		thread.wait_to_finish()
		return false
	thread.wait_to_finish()
	studio.call("_complete_level_pipeline", gateway.pipeline_result)
	if gateway.execute_count != 1 or str(studio.call("_activity_display_state")) != "UNAVAILABLE":
		_fail("fake worker count or backend-truth state was incorrect")
		return false
	return true


func _run() -> void:
	if OS.get_environment("SB_LFX_R09_R02_R01_RESTORE_ONLY") == "1":
		var restore_studio := await _make_studio()
		if restore_studio == null:
			return
		if not _test_restored_import_order(restore_studio):
			await _free_studio(restore_studio)
			return
		await _free_studio(restore_studio)
		print("R09-R02-R01 immutable source restore focused suite: PASS (owner-pages not called)")
		quit(0)
		return
	var studio := await _make_studio()
	if studio == null:
		return
	if not _test_layout_and_valid_incremental_stream(studio):
		await _free_studio(studio)
		return
	var bad_studio := await _make_studio()
	if bad_studio == null:
		await _free_studio(studio)
		return
	if not _test_fail_closed_tamper(bad_studio):
		await _free_studio(bad_studio)
		await _free_studio(studio)
		return
	await _free_studio(bad_studio)
	var import_studio := await _make_studio()
	if import_studio == null:
		await _free_studio(studio)
		return
	if not _test_restored_import_order(import_studio):
		await _free_studio(import_studio)
		await _free_studio(studio)
		return
	await _free_studio(import_studio)
	var async_studio := await _make_studio()
	if async_studio == null:
		await _free_studio(studio)
		return
	if not await _test_slow_worker_stream(async_studio):
		await _free_studio(async_studio)
		await _free_studio(studio)
		return
	if OS.get_environment("SB_LFX_R09_R02_R01_CAPTURE_RELEASE_UI") == "1":
		studio.call("_show_screen", "LEVEL FACTORY")
		await process_frame
		await process_frame
		var image := root.get_viewport().get_texture().get_image()
		var evidence_path := ProjectSettings.globalize_path("res://../owner-visual-evidence/SB-LFX-018-C001-R02-R05-R09-R02-R01-installed-pipeline-monitor.png")
		if image == null or image.is_empty() or FileAccess.file_exists(evidence_path) or image.save_png(evidence_path) != OK:
			_fail("focused installed Release viewport screenshot could not be captured safely")
			await _free_studio(async_studio)
			await _free_studio(studio)
			return
	await _free_studio(async_studio)
	await _free_studio(studio)
	print("R09-R02-R01 live pipeline monitor focused suite: PASS (Python/backend calls from UI harness: zero)")
	quit(0)
