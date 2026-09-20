extends SceneTree

const PASS_MARKER := "SB-LFX-005-C001 ONE-CLICK PIPELINE integration PASS"
var _errors: Array[String] = []
var _fixture_root := ""
var _source_id := ""


func _init() -> void: call_deferred("_run_suite")


func _run_suite() -> void:
	var packed := ResourceLoader.load("res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var navigation := instance.get_node_or_null("Frame/Layout/Body/NavigationPanel/Navigation")
	var import_surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/OperationsImport")
	var pipeline := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/OneClickPipeline")
	_require(navigation != null and import_surface != null and pipeline != null, "Pipeline surface did not instantiate")
	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_005_pipeline_fixture"); _remove_tree(_fixture_root); DirAccess.make_dir_recursive_absolute(_fixture_root)
	var image := Image.create(20, 20, false, Image.FORMAT_RGB8); image.fill(Color8(233, 75, 75)); var path := _fixture_root.path_join("pipeline.png"); image.save_png(path)
	import_surface.call("set_source_path", path); import_surface.call("import_selected"); await process_frame
	var imported: Dictionary = import_surface.call("snapshot"); _source_id = str(imported.get("source_id", "")); _require(imported.get("state") in ["IMPORTED", "ALREADY_IMPORTED"], "pipeline fixture import failed")
	navigation.emit_signal("surface_selected", "Pipeline"); await process_frame
	pipeline.call("run_pipeline", _source_id, ""); await process_frame
	var result: Dictionary = pipeline.call("snapshot"); var stage_dispositions := {}
	for stage in result.get("stages", []): stage_dispositions[stage.get("stage", "")] = stage.get("disposition", "")
	_require(stage_dispositions.get("SOURCE") == "PASS", "pipeline did not pass source stage")
	_require(stage_dispositions.get("SOLVE") == "NOT_AVAILABLE", "pipeline fabricated solver availability")
	_require(stage_dispositions.get("DIFFICULTY") == "NOT_AVAILABLE", "pipeline fabricated difficulty availability")
	_cleanup(instance)


func _cleanup(instance: Node) -> void:
	if not _source_id.is_empty(): _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads").path_join(_source_id))
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
