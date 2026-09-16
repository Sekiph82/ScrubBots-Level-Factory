extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const TEST_OUTPUT_PATH := "res://output/.lf06-003-action-test"
const SEED_VALUE := "77"
const PRESENTATION_LABEL := "presentation-only-label"
const SCENE_LOADER_METHOD := "load"

var failures: Array[String] = []
var test_output_absolute := ""


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	test_output_absolute = ProjectSettings.globalize_path(TEST_OUTPUT_PATH)
	_remove_tree(test_output_absolute)
	var missing_core := FactoryCoreGateway.new("definitely;missing-scrubbots-python")
	_check(missing_core.status_name() == "UNAVAILABLE", "Invalid canonical Core executable was not reported unavailable")
	var missing_result: Dictionary = missing_core.call("run_action", "Generate", {"seed": "77"})
	_check(missing_result.get("state") == "UNAVAILABLE", "Missing canonical Core did not keep Generate unavailable")
	var packed_scene := ResourceLoader.call(SCENE_LOADER_METHOD, MAIN_SCENE_PATH) as PackedScene
	_check(packed_scene != null, "Factory Studio scene did not load")
	if packed_scene == null:
		_finish()
		return
	var instance := packed_scene.instantiate()
	_check(instance != null, "Factory Studio scene did not instantiate")
	if instance == null:
		_finish()
		return
	root.add_child(instance)
	await process_frame

	var navigation := instance.get_node_or_null(NAVIGATION_NODE_PATH)
	var workspace := instance.get_node_or_null(WORKSPACE_NODE_PATH)
	_check(navigation != null and workspace != null, "Studio navigation/workspace did not instantiate")
	if navigation == null or workspace == null:
		instance.queue_free()
		_finish()
		return
	navigation.emit_signal("surface_selected", "Generate")
	await process_frame
	var target := workspace.get_node_or_null(TARGET_NODE_PATH)
	_check(target != null and target.visible, "Generate target controls are not visible")
	if target == null:
		instance.queue_free()
		_finish()
		return

	var gateway: RefCounted = instance.get("core_gateway")
	_check(gateway != null, "Studio did not construct the canonical Core gateway")
	if gateway == null:
		instance.queue_free()
		_finish()
		return
	gateway.call("set_output_root", TEST_OUTPUT_PATH)
	_check(gateway.call("status_name") == "AVAILABLE", "Canonical Python Core gateway did not become available")
	var capability_matrix: Dictionary = gateway.call("capability_matrix")
	_check(bool(capability_matrix["Generate"]["available"]), "Generate capability was not derived as available")
	_check(not bool(capability_matrix["Solve"]["available"]), "Solve became available without M03")
	_check(not bool(capability_matrix["Validate"]["available"]), "Validate became available without standalone canonical validation")
	_check(not bool(capability_matrix["Analyze"]["available"]), "Analyze became available without M04")
	var incompatible_core := FactoryCoreGateway.new(str(gateway.get("python_executable")), "res://tests/factory_studio_action_integration_suite.gd")
	_check(incompatible_core.status_name() == "UNAVAILABLE", "Executable-present but incompatible launcher path was reported available")
	var incompatible_matrix: Dictionary = incompatible_core.call("capability_matrix")
	_check(not bool(incompatible_matrix["Generate"]["available"]), "Generate was enabled for an incompatible launcher/Core path")
	var invalid_request: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "NOT_A_DIFFICULTY", "width": 20, "height": 21, "seed": "77", "mode": "RULES"}, TEST_OUTPUT_PATH)
	_check(invalid_request.get("state") == "FAILED" and int(invalid_request.get("exit_code", 0)) != 0, "Canonical nonzero action failure was not mapped to FAILED")
	var invalid_reason := str(invalid_request.get("reason", "")).to_lower()
	_check("invalid choice" in invalid_reason or "invalid generation request" in invalid_reason, "Canonical stderr diagnostic was not preserved in the failed action reason")
	_check("success candidate_id=" not in str(invalid_request.get("captured_output", "")).to_lower(), "Unrelated output was allowed to promote a failed action")

	var difficulty := target.get_node_or_null("DifficultyRow/Difficulty") as OptionButton
	var width := target.get_node_or_null("WidthRow/Width") as SpinBox
	var height := target.get_node_or_null("HeightRow/Height") as SpinBox
	var seed := target.get_node_or_null("SeedRow/Seed") as LineEdit
	var mode := target.get_node_or_null("ModeRow/Mode") as OptionButton
	var candidate := target.get_node_or_null("CandidatepresentationlabelRow/CandidatePresentation") as LineEdit
	_check(difficulty != null and width != null and height != null and seed != null and mode != null and candidate != null, "Action integration controls are incomplete")
	if difficulty == null or width == null or height == null or seed == null or mode == null or candidate == null:
		instance.queue_free()
		_finish()
		return
	width.value = 20
	height.value = 21
	seed.text = SEED_VALUE
	seed.text_changed.emit(seed.text)
	mode.select(1)
	mode.item_selected.emit(1)
	candidate.text = PRESENTATION_LABEL
	candidate.text_changed.emit(candidate.text)
	await process_frame

	var generate_button := target.get_node_or_null("ActionArea/GenerateAction") as Button
	var reproduce_button := target.get_node_or_null("ActionArea/ReproduceAction") as Button
	_check(generate_button != null and reproduce_button != null, "Generate/Reproduce action controls are missing")
	_check(generate_button != null and not generate_button.disabled, "Generate was not enabled for a complete canonical draft")
	for action in ["Solve", "Validate", "Analyze"]:
		var button := target.get_node_or_null("ActionArea/" + action + "Action") as Button
		_check(button != null and button.disabled and "UNAVAILABLE" in button.tooltip_text, action + " is not visibly unavailable with a truthful reason")
	if generate_button == null or reproduce_button == null:
		instance.queue_free()
		_finish()
		return
	var preview_before_action := target.get_node_or_null("ActionArea/CanonicalArtworkPreview")
	_check(preview_before_action != null, "Canonical artwork preview component is missing before execution")
	if preview_before_action != null:
		var empty_preview: Dictionary = preview_before_action.call("snapshot")
		_check(empty_preview.get("state") == "EMPTY", "Preview was not EMPTY before a successful canonical action")
		_check(preview_before_action.get_node_or_null("ArtworkImage").texture == null, "Preview fabricated a texture before canonical success")

	generate_button.pressed.emit()
	await process_frame
	var generated: Dictionary = target.call("action_result_snapshot")
	_check(generated.get("action") == "Generate" and generated.get("state") == "SUCCESS", "Real Studio Generate did not return canonical success evidence")
	_check(generated.get("exit_code") == 0, "Canonical Generate did not exit with code 0")
	_check(str(generated.get("candidate_id", "")) != PRESENTATION_LABEL, "Candidate presentation label was used as a canonical candidate ID")
	_check(str(generated.get("captured_output", "")).contains("SUCCESS candidate_id="), "Generate did not capture the canonical CLI summary")
	_check(str(generated.get("metadata_path", "")).ends_with("metadata.json"), "Generate did not expose metadata.json evidence")
	_check(_under_output_area(str(generated.get("output_path", ""))), "Generate output escaped the approved Factory output area")
	var generate_detail := workspace.get_node_or_null("Padding/Content/Detail") as Label
	_check(generate_detail != null and "No generation has occurred" not in generate_detail.text, "Generate workspace retained a false post-success no-generation statement")
	_check(not reproduce_button.disabled, "Reproduce was not enabled after a successful Generate")
	var last_success_after_generate: Dictionary = target.call("last_successful_core_evidence_snapshot")
	_check(last_success_after_generate == generated, "Successful Generate evidence was not retained separately")
	var preview := target.get_node_or_null("ActionArea/CanonicalArtworkPreview")
	_check(preview != null, "Canonical artwork preview component is missing")
	if preview == null:
		instance.queue_free()
		_finish()
		return
	var preview_before_success: Dictionary = preview.call("snapshot")
	_check(preview_before_success.get("state") == "READY", "Successful Generate did not produce a READY canonical preview")
	_check(preview_before_success.get("source_action") == "Generate", "Preview source action was not Generate")
	_check(preview_before_success.get("candidate_id") == generated.get("candidate_id"), "Preview candidate identity was not taken from canonical Core evidence")
	_check(preview_before_success.get("candidate_id") != PRESENTATION_LABEL, "Preview used the candidate presentation label as identity")
	_check(preview_before_success.get("artwork_path") == str(generated.get("output_path")).path_join("artwork.png"), "Preview did not derive artwork.png from Generate output_path")
	_check(preview_before_success.get("logical_width") == 20 and preview_before_success.get("logical_height") == 21, "Preview did not inspect the real 20x21 rectangular artwork dimensions")
	var expected_scale := maxi(1, mini(16, floori(512.0 / 21.0)))
	_check(preview_before_success.get("presentation_scale") == expected_scale, "Preview presentation scale was not the deterministic bounded integer scale")
	_check(preview_before_success.get("displayed_width") == 20 * expected_scale and preview_before_success.get("displayed_height") == 21 * expected_scale, "Preview display dimensions do not equal logical dimensions multiplied by scale")
	var source_image := Image.load_from_file(str(preview_before_success.get("artwork_path")))
	_check(source_image != null, "Canonical Generate artwork.png could not be loaded by the integration test")
	var displayed_texture := preview.get_node_or_null("ArtworkImage").texture as ImageTexture
	_check(displayed_texture != null, "Canonical preview did not create an ImageTexture")
	var displayed_image := displayed_texture.get_image() if displayed_texture != null else null
	_check(displayed_image != null, "Canonical preview texture did not expose a displayed image")
	if displayed_image != null:
		for y in range(21):
			for x in range(20):
				var expected_color := source_image.get_pixel(x, y)
				for dy in range(expected_scale):
					for dx in range(expected_scale):
						_check(displayed_image.get_pixel(x * expected_scale + dx, y * expected_scale + dy) == expected_color, "Preview introduced a blended or foreign pixel at logical block %s,%s" % [x, y])
		_check(displayed_image.get_width() == 20 * expected_scale and displayed_image.get_height() == 21 * expected_scale, "Displayed texture dimensions are not deterministic")

	var metadata_path := str(generated.get("metadata_path", ""))
	var metadata_file := FileAccess.open(metadata_path, FileAccess.READ)
	_check(metadata_file != null, "Generated metadata.json could not be opened for failure-retention regression")
	var original_metadata := metadata_file.get_as_text() if metadata_file != null else ""
	if metadata_file != null:
		metadata_file.close()
	_write_text(metadata_path, "{\"corrupted\":true}")
	reproduce_button.pressed.emit()
	await process_frame
	var failed_reproduce: Dictionary = target.call("action_result_snapshot")
	_check(failed_reproduce.get("action") == "Reproduce" and failed_reproduce.get("state") == "FAILED", "Corrupt metadata did not produce a failed Reproduce action")
	_check(int(failed_reproduce.get("exit_code", 0)) != 0, "Failed Reproduce did not preserve its nonzero Core exit")
	_check("metadata" in str(failed_reproduce.get("reason", "")).to_lower() or "mismatch" in str(failed_reproduce.get("reason", "")).to_lower(), "Failed Reproduce did not expose its canonical diagnostic")
	var last_success_after_failure: Dictionary = target.call("last_successful_core_evidence_snapshot")
	_check(last_success_after_failure == last_success_after_generate, "Failed Reproduce erased last-success Core evidence")
	var result_readout := target.get_node_or_null("ActionArea/ActionResult") as Label
	_check(result_readout != null and "Last successful Core evidence retained" in result_readout.text, "Last-success evidence was not visibly retained after failure")
	var preview_after_failure: Dictionary = preview.call("snapshot")
	_check(preview_after_failure.get("state") == "READY" and preview_after_failure.get("retained_after_failure") == true, "Failed action did not retain and label the last successful preview")
	_check(preview_after_failure.get("artwork_path") == preview_before_success.get("artwork_path"), "Failed action silently changed the retained preview source")
	var preview_state_label := preview.get_node_or_null("PreviewState") as Label
	_check(preview_state_label != null and "RETAINED LAST SUCCESS" in preview_state_label.text, "Retained preview was not visibly labeled")
	_write_text(metadata_path, original_metadata)

	reproduce_button.pressed.emit()
	await process_frame
	var reproduced: Dictionary = target.call("action_result_snapshot")
	_check(reproduced.get("action") == "Reproduce" and reproduced.get("state") == "SUCCESS", "Real Studio Reproduce did not return canonical success evidence")
	_check(reproduced.get("disposition") == "MATCH", "Canonical Reproduce did not report MATCH")
	_check(reproduced.get("candidate_id") == generated.get("candidate_id"), "Reproduce candidate identity drifted")
	_check(reproduced.get("grid_hash") == generated.get("grid_hash"), "Reproduce grid hash did not match Generate")
	_check(str(reproduced.get("output_path", "")) != str(generated.get("output_path", "")), "Reproduce targeted the original Generate bundle")
	_check(_under_output_area(str(reproduced.get("output_path", ""))), "Reproduce output escaped the approved Factory output area")
	var preview_after_reproduce: Dictionary = preview.call("snapshot")
	_check(preview_after_reproduce.get("state") == "READY", "Reproduce MATCH did not produce a READY preview")
	_check(preview_after_reproduce.get("source_action") == "Reproduce", "Reproduce preview retained the Generate source action")
	_check(preview_after_reproduce.get("artwork_path") == str(reproduced.get("output_path")).path_join("artwork.png"), "Reproduce preview did not point at the reproduction bundle artwork.png")
	var reproduced_image := Image.load_from_file(str(preview_after_reproduce.get("artwork_path")))
	_check(reproduced_image != null, "Reproduce artwork.png could not be loaded")
	_check(source_image != null and reproduced_image != null and source_image.get_width() == reproduced_image.get_width() and source_image.get_height() == reproduced_image.get_height(), "Reproduce preview dimensions changed")
	if source_image != null and reproduced_image != null and source_image.get_width() == reproduced_image.get_width() and source_image.get_height() == reproduced_image.get_height():
		for y in range(source_image.get_height()):
			for x in range(source_image.get_width()):
				_check(source_image.get_pixel(x, y) == reproduced_image.get_pixel(x, y), "Reproduce MATCH preview pixels differ from Generate artwork")
	var reproduced_artwork_path := str(preview_after_reproduce.get("artwork_path"))
	var reproduced_artwork_bytes := FileAccess.get_file_as_bytes(reproduced_artwork_path)
	DirAccess.remove_absolute(reproduced_artwork_path)
	preview.call("consume_action_result", reproduced)
	var corrupt_preview: Dictionary = preview.call("snapshot")
	_check(corrupt_preview.get("state") == "ERROR", "Missing canonical artwork did not produce truthful preview ERROR")
	_check(corrupt_preview.get("retained_after_failure") == true, "Missing canonical artwork did not label prior preview as retained/stale")
	_check("no draft preview" in str(corrupt_preview.get("error", "")).to_lower(), "Preview failure did not state that no draft artwork was fabricated")
	var restored_artwork := FileAccess.open(reproduced_artwork_path, FileAccess.WRITE)
	if restored_artwork != null:
		restored_artwork.store_buffer(reproduced_artwork_bytes)
		restored_artwork.close()

	instance.queue_free()
	_finish()


func _under_output_area(path: String) -> bool:
	var output_root := ProjectSettings.globalize_path("res://output").simplify_path().replace(char(92), "/").to_lower()
	var normalized := path.simplify_path().replace(char(92), "/").to_lower()
	return normalized.begins_with(output_root + "/")


func _write_text(path: String, contents: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file != null:
		file.store_string(contents)
		file.close()


func _remove_tree(path: String) -> void:
	var directory := DirAccess.open(path)
	if directory == null:
		return
	directory.list_dir_begin()
	var entry := directory.get_next()
	while not entry.is_empty():
		if entry != "." and entry != "..":
			var child_path := path.path_join(entry)
			if directory.current_is_dir():
				_remove_tree(child_path)
			else:
				DirAccess.remove_absolute(child_path)
		entry = directory.get_next()
	directory.list_dir_end()
	DirAccess.remove_absolute(path)


func _finish() -> void:
	_remove_tree(test_output_absolute)
	if failures.is_empty():
		print("SB-LF06-003-C001 Studio/Core action integration PASS")
		print("SB-LF06-004-C001 crisp preview integration PASS")
		quit(0)
		return
	for failure in failures:
		push_error(failure)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
