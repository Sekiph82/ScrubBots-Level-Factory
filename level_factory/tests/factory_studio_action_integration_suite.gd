extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const NAVIGATION_NODE_PATH := NodePath("Frame/Layout/Body/NavigationPanel/Navigation")
const WORKSPACE_NODE_PATH := NodePath("Frame/Layout/Body/Workspace")
const TARGET_NODE_PATH := NodePath("Padding/Content/TargetControls")
const TEST_OUTPUT_PATH := "res://output/.lf06-003-action-test"
const CORE_GATEWAY_SCRIPT_PATH := "res://scripts/factory_core_gateway.gd"
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
	for script_path in [
		"res://scripts/factory_core_gateway.gd",
		"res://scripts/factory_studio_navigation.gd",
		"res://scripts/factory_studio_workspace_page.gd",
		"res://scripts/factory_studio_target_controls.gd",
		"res://scripts/factory_studio_art_preview.gd",
		"res://scripts/factory_studio_evidence_panel.gd",
		"res://scripts/factory_studio_art_editor.gd",
	]:
		_check(ResourceLoader.call(SCENE_LOADER_METHOD, script_path) as Script != null, "Studio script contract did not load: %s" % script_path)
	var gateway_script := ResourceLoader.call(SCENE_LOADER_METHOD, CORE_GATEWAY_SCRIPT_PATH) as Script
	_check(gateway_script != null, "Canonical Core gateway script did not load")
	if gateway_script == null:
		_finish()
		return
	var missing_core: RefCounted = gateway_script.new("definitely;missing-scrubbots-python")
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
	var incompatible_core: RefCounted = gateway_script.new(str(gateway.get("python_executable")), "res://tests/factory_studio_action_integration_suite.gd")
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
	var evidence_before_action := target.get_node_or_null("ActionArea/CanonicalEvidencePanel")
	_check(evidence_before_action != null, "Canonical evidence panel is missing before execution")
	if evidence_before_action != null:
		var empty_evidence: Dictionary = evidence_before_action.call("snapshot")
		_check(empty_evidence.get("state") == "EMPTY", "Evidence panel was not EMPTY before a successful canonical action")
		_check(str(empty_evidence.get("candidate_id", "")).is_empty() and str(empty_evidence.get("quality_decision", "")).is_empty(), "Evidence panel fabricated identity or quality before canonical success")
	var editor_before_action := target.get_node_or_null("ActionArea/CanonicalArtEditor")
	_check(editor_before_action != null, "Non-destructive logical-pixel editor is missing before execution")
	if editor_before_action != null:
		var empty_editor: Dictionary = editor_before_action.call("snapshot")
		_check(empty_editor.get("state") == "EMPTY", "Editor was not EMPTY before a real canonical source was loaded")
		_check(editor_before_action.call("paint_cell", 0, 0, "C01") == false, "Editor fabricated an editable buffer before source load")
		_check(editor_before_action.call("working_image_snapshot") == null, "Editor exposed a working image before source load")

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
	var evidence := target.get_node_or_null("ActionArea/CanonicalEvidencePanel")
	var source_image := Image.load_from_file(str(generated.get("output_path", "")).path_join("artwork.png"))
	_check(preview != null, "Canonical artwork preview component is missing")
	_check(evidence != null, "Canonical evidence panel is missing after Generate")
	_check(source_image != null, "Canonical Generate artwork.png could not be loaded by the integration test")
	if preview == null or evidence == null or source_image == null:
		instance.queue_free()
		_finish()
		return
	var editor := target.get_node_or_null("ActionArea/CanonicalArtEditor")
	_check(editor != null, "Non-destructive logical-pixel editor is missing after Generate")
	if editor == null:
		instance.queue_free()
		_finish()
		return
	var editor_empty_after_generate: Dictionary = editor.call("snapshot")
	_check(editor_empty_after_generate.get("state") == "EMPTY", "Editor silently loaded or fabricated a source before explicit operator load")
	_check(bool(editor.call("load_current_canonical_artwork")), "Editor could not explicitly load the successful canonical artwork")
	var editor_clean: Dictionary = editor.call("snapshot")
	_check(editor_clean.get("state") == "CLEAN", "Explicit canonical artwork load did not produce a CLEAN editor")
	_check(editor_clean.get("source_action") == "Generate", "Editor source action was not bound to the real Generate result")
	_check(editor_clean.get("source_candidate_id") == generated.get("candidate_id"), "Editor source candidate was not bound to canonical Generate identity")
	_check(editor_clean.get("source_bundle_path") == generated.get("output_path"), "Editor source bundle path was not bound to canonical Generate output")
	_check(editor_clean.get("source_artwork_path") == str(generated.get("output_path")).path_join("artwork.png"), "Editor source artwork path was not derived from canonical output")
	_check(editor_clean.get("logical_width") == 20 and editor_clean.get("logical_height") == 21, "Editor did not preserve the real rectangular artwork dimensions")
	_check(editor_clean.get("validation_disposition") == "UNVALIDATED — revalidation pending SB-LF06-008", "Editor did not expose the required UNVALIDATED disposition")
	var editor_source_image: Image = editor.call("source_image_snapshot")
	var editor_working_image: Image = editor.call("working_image_snapshot")
	_check(editor_source_image != null and editor_working_image != null, "Editor did not create source and working image buffers")
	_check(editor_source_image != null and editor_source_image.get_width() == 20 and editor_source_image.get_height() == 21, "Editor source image dimensions are not canonical")
	if source_image != null and editor_source_image != null and editor_working_image != null:
		for y in range(source_image.get_height()):
			for x in range(source_image.get_width()):
				_check(editor_source_image.get_pixel(x, y) == source_image.get_pixel(x, y), "Editor source pixels differ from real canonical artwork at %s,%s" % [x, y])
				_check(editor_working_image.get_pixel(x, y) == source_image.get_pixel(x, y), "Editor working pixels differ before any edit at %s,%s" % [x, y])
	var source_artwork_path := str(editor_clean.get("source_artwork_path", ""))
	var source_bytes_before := FileAccess.get_file_as_bytes(source_artwork_path)
	var source_sha_before := str(editor_clean.get("source_artwork_sha256", ""))
	_check(not source_bytes_before.is_empty() and not source_sha_before.is_empty(), "Editor did not capture real source artwork bytes/hash before editing")
	var edited_x := 0
	var edited_y := 0
	var original_color_id := str(editor.call("canonical_color_id_for_pixel", editor_source_image.get_pixel(edited_x, edited_y))) if editor_source_image != null else ""
	_check(not original_color_id.is_empty(), "Editor could not map the source cell RGB to a canonical palette ID")
	var selected_color := _different_canonical_color(original_color_id, "C16")
	_check(bool(editor.call("select_color", selected_color)), "Editor rejected a canonical C01..C16 paint color")
	_check(bool(editor.call("paint_cell", edited_x, edited_y, selected_color)), "Editor did not paint one valid logical cell")
	var editor_dirty: Dictionary = editor.call("snapshot")
	_check(editor_dirty.get("state") == "DIRTY", "One-cell edit did not produce DIRTY state")
	_check(editor_dirty.get("dirty_cell_count") == 1, "One-cell edit did not produce exactly one dirty cell")
	_check(editor_dirty.get("working_buffer_differs") == true, "Dirty editor did not expose working-buffer difference")
	_check(editor_dirty.get("validation_disposition") == "UNVALIDATED — revalidation pending SB-LF06-008", "Dirty editor did not remain explicitly UNVALIDATED")
	var editor_working_after_edit: Image = editor.call("working_image_snapshot")
	_check(editor_working_after_edit != null, "Dirty editor did not expose a working image")
	if editor_source_image != null and editor_working_after_edit != null:
		for y in range(editor_source_image.get_height()):
			for x in range(editor_source_image.get_width()):
				if x == edited_x and y == edited_y:
					continue
				_check(editor_working_after_edit.get_pixel(x, y) == editor_source_image.get_pixel(x, y), "Edit changed an untouched logical cell at %s,%s" % [x, y])
		_check(editor_working_after_edit.get_pixel(edited_x, edited_y) == (Color8(0, 0, 0, 255) if selected_color == "C16" else Color8(233, 75, 75, 255)), "Edited cell RGB does not equal selected canonical palette RGB")
	_check(FileAccess.get_file_as_bytes(source_artwork_path) == source_bytes_before, "Editing changed canonical source artwork bytes")
	_check(str(editor_dirty.get("source_artwork_sha256", "")) == source_sha_before, "Editing changed captured canonical source artwork hash")
	_check(preview.call("snapshot").get("artwork_path") == str(generated.get("output_path")).path_join("artwork.png"), "Dirty edit relabeled canonical preview source")
	_check(evidence.call("snapshot").get("metadata_path") == str(generated.get("output_path")).path_join("metadata.json"), "Dirty edit relabeled canonical evidence source")
	_check(bool(editor.call("select_color", original_color_id)), "Editor rejected the original canonical source color ID")
	_check(bool(editor.call("paint_cell", edited_x, edited_y, original_color_id)), "Editor could not restore the last differing cell to its source color")
	var editor_clean_after_reversal: Dictionary = editor.call("snapshot")
	_check(editor_clean_after_reversal.get("state") == "CLEAN", "Restoring the last differing cell did not automatically return the editor to CLEAN")
	_check(editor_clean_after_reversal.get("dirty_cell_count") == 0 and editor_clean_after_reversal.get("working_buffer_differs") == false, "Single-cell reversal left stale dirty evidence")
	var restored_after_reversal: Image = editor.call("working_image_snapshot")
	_check(restored_after_reversal != null and editor_source_image != null and _images_equal(restored_after_reversal, editor_source_image), "Single-cell reversal did not restore exact source pixels")
	_check(FileAccess.get_file_as_bytes(source_artwork_path) == source_bytes_before, "Single-cell reversal changed canonical source artwork bytes")
	_check(preview.call("snapshot").get("artwork_path") == str(generated.get("output_path")).path_join("artwork.png"), "Single-cell reversal changed canonical preview identity")
	_check(evidence.call("snapshot").get("metadata_path") == str(generated.get("output_path")).path_join("metadata.json"), "Single-cell reversal changed canonical evidence identity")
	var multi_first_x := 0
	var multi_second_x := 1
	var multi_first_source_id := str(editor.call("canonical_color_id_for_pixel", editor_source_image.get_pixel(multi_first_x, edited_y))) if editor_source_image != null else ""
	var multi_second_source_id := str(editor.call("canonical_color_id_for_pixel", editor_source_image.get_pixel(multi_second_x, edited_y))) if editor_source_image != null else ""
	var multi_first_color := _different_canonical_color(multi_first_source_id, "C16")
	var multi_second_color := _different_canonical_color(multi_second_source_id, "C15")
	_check(bool(editor.call("paint_cell", multi_first_x, edited_y, multi_first_color)), "First multi-dirty cell could not be painted")
	_check(bool(editor.call("paint_cell", multi_second_x, edited_y, multi_second_color)), "Second multi-dirty cell could not be painted")
	var editor_multi_dirty: Dictionary = editor.call("snapshot")
	_check(editor_multi_dirty.get("state") == "DIRTY" and editor_multi_dirty.get("dirty_cell_count") == 2, "Two differing cells did not produce exact DIRTY count 2")
	_check(bool(editor.call("paint_cell", multi_first_x, edited_y, multi_first_source_id)), "First multi-dirty cell could not be restored to its source color")
	var editor_partial_restore: Dictionary = editor.call("snapshot")
	_check(editor_partial_restore.get("state") == "DIRTY" and editor_partial_restore.get("dirty_cell_count") == 1, "Partial multi-cell restoration did not remain DIRTY with exact count 1")
	_check(editor_partial_restore.get("working_buffer_differs") == true, "Partial multi-cell restoration falsely reported equal source/work buffer")
	edited_x = multi_second_x
	selected_color = multi_second_color
	var dirty_before_invalid_attempts: Image = editor.call("working_image_snapshot")
	_check(editor.call("paint_cell", -1, 0, selected_color) == false, "Out-of-bounds negative coordinate was accepted")
	_check(editor.call("paint_cell", 20, 21, selected_color) == false, "Out-of-bounds upper coordinate was accepted")
	_check(editor.call("paint_cell", edited_x, edited_y, "BG01") == false, "BG01 was accepted as a logical paint color")
	_check(editor.call("paint_cell", edited_x, edited_y, "RGB_NOT_CANONICAL") == false, "Unknown color was accepted as a logical paint color")
	var after_invalid_attempts: Image = editor.call("working_image_snapshot")
	_check(after_invalid_attempts != null and dirty_before_invalid_attempts != null, "Invalid paint regression could not inspect working images")
	if after_invalid_attempts != null and dirty_before_invalid_attempts != null:
		_check(_images_equal(after_invalid_attempts, dirty_before_invalid_attempts), "Invalid paint attempt mutated the working buffer")
	_check(bool(editor.call("paint_cell", edited_x, edited_y, selected_color)), "No-op paint was not accepted as a stable operation")
	_check(editor.call("snapshot").get("dirty_cell_count") == 1, "No-op paint created false dirty evidence")
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
	var evidence_after_generate: Dictionary = evidence.call("snapshot")
	_check(evidence_after_generate.get("state") == "READY", "Generate did not produce a READY canonical evidence panel")
	_check(evidence_after_generate.get("source_action") == "Generate", "Evidence panel source action was not Generate")
	_check(evidence_after_generate.get("metadata_path") == str(generated.get("output_path")).path_join("metadata.json"), "Evidence panel did not derive metadata.json from Generate output_path")
	_check(evidence_after_generate.get("candidate_id") == generated.get("candidate_id"), "Evidence candidate identity disagrees with Generate action evidence")
	_check(evidence_after_generate.get("grid_hash") == generated.get("grid_hash"), "Evidence grid hash disagrees with Generate action evidence")
	_check(evidence_after_generate.get("logical_width") == 20 and evidence_after_generate.get("logical_height") == 21, "Evidence dimensions were not read from canonical metadata")
	_check(evidence_after_generate.get("quality_schema") == "scrubbots-quality" and evidence_after_generate.get("quality_schema_version") == 1, "Evidence quality schema/version is not canonical")
	_check(evidence_after_generate.get("quality_decision") in ["ACCEPT", "REJECT"], "Evidence quality decision is not a canonical structural decision")
	_check(not str(evidence_after_generate.get("solution", "")).is_empty() and "UNAVAILABLE" in str(evidence_after_generate.get("solution", "")), "Solution did not remain unavailable pending M03")
	_check("UNAVAILABLE" in str(evidence_after_generate.get("difficulty_analysis", "")), "Difficulty analysis did not remain unavailable pending M04")
	_check("UNAVAILABLE" in str(evidence_after_generate.get("load_risk", "")), "Load/risk did not remain unavailable without canonical models")
	_check("Structural QA ACCEPT != OWNER ACCEPT" in str(evidence.get_node_or_null("StructuralArtQA").text), "Evidence panel did not preserve QA versus owner acceptance truth")
	var metadata_value: Variant = JSON.parse_string(FileAccess.get_file_as_string(str(generated.get("metadata_path", ""))))
	_check(metadata_value is Dictionary, "Canonical Generate metadata could not be parsed for evidence comparison")
	if metadata_value is Dictionary:
		var metadata_quality: Dictionary = metadata_value.get("quality", {})
		var metadata_report: Dictionary = metadata_quality.get("report", {})
		var metadata_analysis: Dictionary = metadata_report.get("analysis", {})
		var metadata_metrics: Dictionary = metadata_analysis.get("metrics", {})
		var displayed_metrics: Dictionary = evidence_after_generate.get("structural_metrics", {})
		for metric_name in displayed_metrics:
			_check(displayed_metrics[metric_name] == metadata_metrics.get(metric_name), "Evidence metric %s was not read from canonical metadata" % metric_name)

	var metadata_path := str(generated.get("metadata_path", ""))
	var metadata_file := FileAccess.open(metadata_path, FileAccess.READ)
	_check(metadata_file != null, "Generated metadata.json could not be opened for failure-retention regression")
	var original_metadata := metadata_file.get_as_text() if metadata_file != null else ""
	if metadata_file != null:
		metadata_file.close()
	var canonical_metadata_value: Variant = JSON.parse_string(original_metadata)
	_check(canonical_metadata_value is Dictionary, "Canonical Generate metadata could not be parsed for fail-closed gate mutations")
	if canonical_metadata_value is Dictionary:
		var root_candidate_mutation: Dictionary = canonical_metadata_value.duplicate(true)
		root_candidate_mutation["candidate_id"] = "root-mismatched-candidate"
		_assert_evidence_error_after_metadata_mutation(evidence, generated, metadata_path, original_metadata, root_candidate_mutation, "root candidate mismatch")
		var artwork_type_mutation: Dictionary = canonical_metadata_value.duplicate(true)
		var artwork_type_data: Dictionary = artwork_type_mutation.get("artwork", {})
		artwork_type_data["candidate_id"] = 17
		artwork_type_mutation["artwork"] = artwork_type_data
		_assert_evidence_error_after_metadata_mutation(evidence, generated, metadata_path, original_metadata, artwork_type_mutation, "artwork candidate type")
		var request_schema_mutation: Dictionary = canonical_metadata_value.duplicate(true)
		var request_schema_generation: Dictionary = request_schema_mutation.get("generation", {})
		var request_schema_request: Dictionary = request_schema_generation.get("request", {})
		request_schema_request["schema"] = "unsupported-generation-request"
		request_schema_generation["request"] = request_schema_request
		request_schema_mutation["generation"] = request_schema_generation
		_assert_evidence_error_after_metadata_mutation(evidence, generated, metadata_path, original_metadata, request_schema_mutation, "request schema")
		var request_version_mutation: Dictionary = canonical_metadata_value.duplicate(true)
		var request_version_generation: Dictionary = request_version_mutation.get("generation", {})
		var request_version_request: Dictionary = request_version_generation.get("request", {})
		request_version_request["schema_version"] = 999
		request_version_generation["request"] = request_version_request
		request_version_mutation["generation"] = request_version_generation
		_assert_evidence_error_after_metadata_mutation(evidence, generated, metadata_path, original_metadata, request_version_mutation, "unsupported request version")
		var request_type_mutation: Dictionary = canonical_metadata_value.duplicate(true)
		var request_type_generation: Dictionary = request_type_mutation.get("generation", {})
		var request_type_request: Dictionary = request_type_generation.get("request", {})
		request_type_request["schema_version"] = "2"
		request_type_generation["request"] = request_type_request
		request_type_mutation["generation"] = request_type_generation
		_assert_evidence_error_after_metadata_mutation(evidence, generated, metadata_path, original_metadata, request_type_mutation, "request version type")
		var rejection_type_mutation: Dictionary = canonical_metadata_value.duplicate(true)
		var rejection_type_quality: Dictionary = rejection_type_mutation.get("quality", {})
		rejection_type_quality["rejection_codes"] = "not-an-array"
		rejection_type_mutation["quality"] = rejection_type_quality
		_assert_evidence_error_after_metadata_mutation(evidence, generated, metadata_path, original_metadata, rejection_type_mutation, "rejection_codes type")
		evidence.call("consume_action_result", generated)
		var restored_generate_evidence: Dictionary = evidence.call("snapshot")
		_check(restored_generate_evidence.get("state") == "READY" and restored_generate_evidence.get("retained_after_failure") == false, "Restored canonical Generate metadata did not return evidence panel to READY")
	var editor_before_failed_action: Dictionary = editor.call("snapshot")
	_write_text(metadata_path, "{\"corrupted\":true}")
	reproduce_button.pressed.emit()
	await process_frame
	var failed_reproduce: Dictionary = target.call("action_result_snapshot")
	_check(failed_reproduce.get("action") == "Reproduce" and failed_reproduce.get("state") == "FAILED", "Corrupt metadata did not produce a failed Reproduce action")
	_check(int(failed_reproduce.get("exit_code", 0)) != 0, "Failed Reproduce did not preserve its nonzero Core exit")
	_check("metadata" in str(failed_reproduce.get("reason", "")).to_lower() or "mismatch" in str(failed_reproduce.get("reason", "")).to_lower(), "Failed Reproduce did not expose its canonical diagnostic")
	var last_success_after_failure: Dictionary = target.call("last_successful_core_evidence_snapshot")
	_check(last_success_after_failure == last_success_after_generate, "Failed Reproduce erased last-success Core evidence")
	var editor_after_failed_action: Dictionary = editor.call("snapshot")
	_check(editor_after_failed_action.get("state") == "DIRTY", "Failed action erased the DIRTY editor state")
	_check(editor_after_failed_action.get("source_action") == editor_before_failed_action.get("source_action") and editor_after_failed_action.get("source_bundle_path") == editor_before_failed_action.get("source_bundle_path"), "Failed action changed the dirty editor source identity")
	_check(editor_after_failed_action.get("dirty_cell_count") == editor_before_failed_action.get("dirty_cell_count"), "Failed action changed dirty-cell evidence")
	var result_readout := target.get_node_or_null("ActionArea/ActionResult") as Label
	_check(result_readout != null and "Last successful Core evidence retained" in result_readout.text, "Last-success evidence was not visibly retained after failure")
	var preview_after_failure: Dictionary = preview.call("snapshot")
	_check(preview_after_failure.get("state") == "READY" and preview_after_failure.get("retained_after_failure") == true, "Failed action did not retain and label the last successful preview")
	_check(preview_after_failure.get("artwork_path") == preview_before_success.get("artwork_path"), "Failed action silently changed the retained preview source")
	var preview_state_label := preview.get_node_or_null("PreviewState") as Label
	_check(preview_state_label != null and "RETAINED LAST SUCCESS" in preview_state_label.text, "Retained preview was not visibly labeled")
	var evidence_after_failure: Dictionary = evidence.call("snapshot")
	_check(evidence_after_failure.get("state") == "READY" and evidence_after_failure.get("retained_after_failure") == true, "Failed action did not retain the last successful evidence panel")
	_check(evidence_after_failure.get("metadata_path") == evidence_after_generate.get("metadata_path"), "Failed action silently changed retained evidence metadata source")
	_check("RETAINED LAST SUCCESS" in str(evidence.get_node_or_null("EvidenceState").text), "Retained evidence was not visibly labeled")
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
	var editor_after_reproduce: Dictionary = editor.call("snapshot")
	_check(editor_after_reproduce.get("state") == "DIRTY", "Successful Reproduce silently replaced the DIRTY editor")
	_check(editor_after_reproduce.get("source_action") == "Generate" and editor_after_reproduce.get("source_bundle_path") == generated.get("output_path"), "Successful Reproduce silently changed the dirty editor source identity")
	_check(editor_after_reproduce.get("latest_successful_output_path") == reproduced.get("output_path"), "Editor did not retain the newer successful Reproduce as a separately observable latest action")
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
	var evidence_after_reproduce: Dictionary = evidence.call("snapshot")
	_check(evidence_after_reproduce.get("state") == "READY", "Reproduce MATCH did not produce a READY evidence panel")
	_check(evidence_after_reproduce.get("source_action") == "Reproduce", "Reproduce evidence retained the Generate source action")
	_check(evidence_after_reproduce.get("metadata_path") == str(reproduced.get("output_path")).path_join("metadata.json"), "Reproduce evidence did not switch to the reproduction metadata.json")
	_check(evidence_after_reproduce.get("candidate_id") == generated.get("candidate_id") and evidence_after_reproduce.get("grid_hash") == generated.get("grid_hash"), "Reproduce evidence identity was not MATCH-consistent")
	var reproduction_metadata_path := str(evidence_after_reproduce.get("metadata_path"))
	var original_reproduction_metadata := FileAccess.get_file_as_string(reproduction_metadata_path)
	_write_text(reproduction_metadata_path, "{\"schema\":\"corrupt\"}")
	evidence.call("consume_action_result", reproduced)
	var corrupt_evidence: Dictionary = evidence.call("snapshot")
	_check(corrupt_evidence.get("state") == "ERROR", "Corrupt successful metadata did not produce truthful evidence ERROR")
	_check(corrupt_evidence.get("retained_after_failure") == true, "Corrupt metadata did not retain prior evidence separately")
	_check("metadata" in str(corrupt_evidence.get("error", "")).to_lower(), "Evidence metadata failure did not expose a truthful diagnostic")
	_write_text(reproduction_metadata_path, original_reproduction_metadata)
	var mismatched_metadata: Variant = JSON.parse_string(original_reproduction_metadata)
	if mismatched_metadata is Dictionary:
		var mismatched_artwork: Dictionary = mismatched_metadata.get("artwork", {})
		mismatched_artwork["candidate_id"] = "mismatched-candidate"
		mismatched_metadata["artwork"] = mismatched_artwork
		_write_text(reproduction_metadata_path, JSON.stringify(mismatched_metadata))
		evidence.call("consume_action_result", reproduced)
		var mismatch_evidence: Dictionary = evidence.call("snapshot")
		_check(mismatch_evidence.get("state") == "ERROR", "Mismatched canonical metadata did not produce truthful evidence ERROR")
		_check(mismatch_evidence.get("retained_after_failure") == true, "Mismatched metadata did not retain prior evidence separately")
	_write_text(reproduction_metadata_path, original_reproduction_metadata)
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
	_check(bool(editor.call("reset_to_source")), "Reset to source did not restore the immutable Generate source")
	var editor_after_reset: Dictionary = editor.call("snapshot")
	_check(editor_after_reset.get("state") == "CLEAN" and editor_after_reset.get("dirty_cell_count") == 0, "Reset to source did not return the editor to CLEAN")
	var reset_image: Image = editor.call("working_image_snapshot")
	_check(reset_image != null and editor_source_image != null and _images_equal(reset_image, editor_source_image), "Reset to source did not restore exact original source pixels")
	_check(bool(editor.call("load_current_canonical_artwork")), "Explicit clean load of the current Reproduce artwork failed")
	var editor_after_reproduce_load: Dictionary = editor.call("snapshot")
	_check(editor_after_reproduce_load.get("state") == "CLEAN", "Explicit Reproduce source load did not produce CLEAN state")
	_check(editor_after_reproduce_load.get("source_action") == "Reproduce", "Explicit current-source load did not switch editor source action")
	_check(editor_after_reproduce_load.get("source_bundle_path") == reproduced.get("output_path"), "Explicit current-source load did not switch editor bundle path")
	_check(editor_after_reproduce_load.get("source_candidate_id") == reproduced.get("candidate_id"), "Explicit current-source load did not preserve canonical Reproduce candidate identity")
	var reproduce_editor_image: Image = editor.call("working_image_snapshot")
	_check(reproduce_editor_image != null and reproduced_image != null and _images_equal(reproduce_editor_image, reproduced_image), "Explicit Reproduce source load changed canonical source pixels")

	instance.queue_free()
	_finish()


func _under_output_area(path: String) -> bool:
	var output_root := ProjectSettings.globalize_path("res://output").simplify_path().replace(char(92), "/").to_lower()
	var normalized := path.simplify_path().replace(char(92), "/").to_lower()
	return normalized.begins_with(output_root + "/")


func _assert_evidence_error_after_metadata_mutation(evidence: Node, result: Dictionary, metadata_path: String, original_metadata: String, mutation: Dictionary, label: String) -> void:
	_write_text(metadata_path, JSON.stringify(mutation))
	evidence.call("consume_action_result", result)
	var mutated_evidence: Dictionary = evidence.call("snapshot")
	_check(mutated_evidence.get("state") == "ERROR", "" + label + " did not produce truthful evidence ERROR")
	_check(mutated_evidence.get("retained_after_failure") == true, "" + label + " did not retain prior successful evidence")
	_check(not str(mutated_evidence.get("error", "")).is_empty(), "" + label + " did not expose a bounded evidence diagnostic")
	_write_text(metadata_path, original_metadata)


func _write_text(path: String, contents: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file != null:
		file.store_string(contents)
		file.close()


func _different_canonical_color(source_id: String, preferred: String) -> String:
	var candidates := [preferred, "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16"]
	for candidate in candidates:
		if candidate != source_id:
			return candidate
	return ""


func _images_equal(left: Image, right: Image) -> bool:
	if left == null or right == null:
		return false
	if left.get_width() != right.get_width() or left.get_height() != right.get_height():
		return false
	for y in range(left.get_height()):
		for x in range(left.get_width()):
			if left.get_pixel(x, y) != right.get_pixel(x, y):
				return false
	return true


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
		print("SB-LF06-005-C001 canonical evidence integration PASS")
		print("SB-LF06-006-C001 non-destructive pixel editor integration PASS")
		quit(0)
		return
	for failure in failures:
		push_error(failure)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
