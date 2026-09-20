extends SceneTree

const PASS_MARKER := "SB-LFX-005-C001 ONE-CLICK PIPELINE integration PASS"
var _errors: Array[String] = []
var _fixture_root := ""
var _source_id := ""
var _failed_source_id := ""
var _generated_candidate_id := ""


func _init() -> void: call_deferred("_run_suite")


func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var navigation := instance.get_node_or_null("Frame/Layout/Body/NavigationPanel/Navigation")
	var import_surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/OperationsImport")
	var pipeline := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/OneClickPipeline")
	_require(navigation != null and import_surface != null and pipeline != null, "Pipeline surface did not instantiate")
	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_005_pipeline_fixture"); _remove_tree(_fixture_root); DirAccess.make_dir_recursive_absolute(_fixture_root)
	var image := Image.create(20, 20, false, Image.FORMAT_RGB8); image.fill(Color8(233, 75, 75)); var path := _fixture_root.path_join("pipeline.png"); image.save_png(path)
	var failed_image := Image.create(19, 20, false, Image.FORMAT_RGB8); failed_image.fill(Color8(255, 0, 255)); var failed_path := _fixture_root.path_join("failed.png"); failed_image.save_png(failed_path)
	import_surface.call("set_source_path", path); import_surface.call("import_selected"); await process_frame
	var imported: Dictionary = import_surface.call("snapshot"); _source_id = str(imported.get("source_id", "")); _require(imported.get("state") in ["IMPORTED", "ALREADY_IMPORTED"], "pipeline fixture import failed")
	var source_bytes_before := FileAccess.get_file_as_bytes(ProjectSettings.globalize_path("res://output/owner-uploads").path_join(_source_id).path_join("source.png"))
	import_surface.call("set_source_path", failed_path); import_surface.call("import_selected"); await process_frame
	var failed_import: Dictionary = import_surface.call("snapshot"); _failed_source_id = str(failed_import.get("source_id", "")); _require(failed_import.get("state") in ["IMPORTED", "ALREADY_IMPORTED"], "failed pipeline fixture import failed")
	navigation.emit_signal("surface_selected", "Pipeline"); await process_frame
	pipeline.call("run_pipeline", _source_id, ""); await process_frame
	var result: Dictionary = pipeline.call("snapshot"); var stage_dispositions := {}
	for stage in result.get("stages", []): stage_dispositions[stage.get("stage", "")] = stage.get("disposition", "")
	_require(stage_dispositions.get("SOURCE") == "PASS", "pipeline did not pass source stage")
	_require(stage_dispositions.get("SOLVE") == "NOT_AVAILABLE", "pipeline fabricated solver availability")
	_require(stage_dispositions.get("DIFFICULTY") == "NOT_AVAILABLE", "pipeline fabricated difficulty availability")
	for stage in result.get("stages", []):
		_require(stage.has("input_identities") and stage.has("output_identities") and stage.has("evidence_reference") and stage.has("reason"), "stage lineage shape is incomplete: %s" % stage)
	var first_run_id := str(result.get("run_id", ""))
	pipeline.call("run_pipeline", _source_id, ""); await process_frame
	var rerun: Dictionary = pipeline.call("snapshot")
	_require(str(rerun.get("run_id", "")) != first_run_id, "pipeline rerun did not retain a distinct run record")
	var failed_run: Dictionary = instance.get("core_gateway").call("run_studio_extension", "pipeline", {"source_id": _failed_source_id})
	var failed_dispositions := {}
	for stage in failed_run.get("stages", []): failed_dispositions[stage.get("stage", "")] = stage.get("disposition", "")
	_require(failed_dispositions.get("NORMALIZE/DERIVE") == "BLOCKED", "validation failure did not block derivation")
	_require(failed_dispositions.get("CANDIDATE") == "BLOCKED", "validation failure exposed a candidate")
	var gateway: RefCounted = instance.get("core_gateway")
	var generated: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "55005", "mode": "MASK"}, "res://output/studio-runs")
	_require(generated.get("state") == "SUCCESS", "canonical Generate path did not produce a candidate: %s" % generated)
	_generated_candidate_id = str(generated.get("candidate_id", ""))
	var candidate_run: Dictionary = gateway.call("run_studio_extension", "pipeline", {"candidate_id": _generated_candidate_id})
	var candidate_dispositions := {}
	for stage in candidate_run.get("stages", []): candidate_dispositions[stage.get("stage", "")] = stage.get("disposition", "")
	_require(candidate_dispositions.get("CANDIDATE") == "PASS", "generated canonical candidate path did not pass candidate stage")
	_require(candidate_dispositions.get("SOLVE") == "NOT_AVAILABLE", "generated pipeline fabricated solver availability")
	_require(FileAccess.get_file_as_bytes(ProjectSettings.globalize_path("res://output/owner-uploads").path_join(_source_id).path_join("source.png")) == source_bytes_before, "pipeline mutated owner source bytes")
	_cleanup(instance)


func _cleanup(instance: Node) -> void:
	if not _source_id.is_empty(): _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads").path_join(_source_id))
	if not _failed_source_id.is_empty(): _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads").path_join(_failed_source_id))
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(_fixture_root); instance.queue_free(); _finish()


func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path): return
	var directory := DirAccess.open(path); if directory == null: return
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next(); if entry.is_empty(): break
		if entry in [".", ".."]: continue
		var child := path.path_join(entry)
		if directory.current_is_dir(): _remove_tree(child)
		else: DirAccess.remove_absolute(child)
	directory.list_dir_end(); DirAccess.remove_absolute(path)


func _require(condition: bool, message: String) -> void:
	if not condition: _errors.append(message)


func _finish() -> void:
	if _errors.is_empty(): print(PASS_MARKER); quit(0); return
	for error in _errors: push_error(error)
	quit(1)
