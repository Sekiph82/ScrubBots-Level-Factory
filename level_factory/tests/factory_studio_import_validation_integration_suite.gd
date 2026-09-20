extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const IMPORT_PATH := NodePath("Frame/Layout/Body/Workspace/Padding/Content/OperationsImport")
const VALIDATION_PATH := NodePath("Frame/Layout/Body/Workspace/Padding/Content/ImportValidationWizard")
const PASS_MARKER := "SB-LFX-004-C001 IMPORT VALIDATION integration PASS"
var _errors: Array[String] = []
var _fixture_root := ""
var _source_ids: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var packed := ResourceLoader.load(MAIN_SCENE_PATH) as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate()
	root.add_child(instance)
	await process_frame
	var navigation := instance.get_node_or_null("Frame/Layout/Body/NavigationPanel/Navigation")
	var import_surface := instance.get_node_or_null(IMPORT_PATH)
	var wizard := instance.get_node_or_null(VALIDATION_PATH)
	_require(navigation != null and import_surface != null and wizard != null, "Import and validation surfaces did not instantiate")
	if navigation == null or import_surface == null or wizard == null: _finish(); return
	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_004_validation_fixture")
	_remove_tree(_fixture_root)
	DirAccess.make_dir_recursive_absolute(_fixture_root)
	var valid_path := _fixture_root.path_join("valid.png")
	var nonlogical_path := _fixture_root.path_join("nonlogical.png")
	_write_valid(valid_path)
	_write_nonlogical(nonlogical_path)
	for path in [valid_path, nonlogical_path]:
		import_surface.call("set_source_path", path)
		import_surface.call("import_selected")
		await process_frame
		var imported: Dictionary = import_surface.call("snapshot")
		_require(imported.get("state") in ["IMPORTED", "ALREADY_IMPORTED"], "validation fixture import failed: %s" % imported)
		_source_ids.append(str(imported.get("source_id", "")))
	navigation.emit_signal("surface_selected", "Import Validation")
	await process_frame
	wizard.call("set_source_id", _source_ids[0])
	wizard.call("run_validation")
	await process_frame
	var valid_report: Dictionary = wizard.call("snapshot")
	_require(valid_report.get("exact_logical_source") == true, "valid logical source was not recognized")
	wizard.call("set_source_id", _source_ids[1])
	wizard.call("run_validation")
	await process_frame
	var derived_report: Dictionary = wizard.call("snapshot")
	_require(derived_report.get("logical_dimension_status") == "DERIVED_ARTIFACT_REQUIRED", "nonlogical source did not require a derived artifact")
	_require(derived_report.get("palette", {}).get("foreign_color_count", 0) > 0, "foreign color fact was not reported")
	_cleanup(instance)


func _write_valid(path: String) -> void:
	var image := Image.create(20, 20, false, Image.FORMAT_RGB8)
	var colors := [Color8(233, 75, 75), Color8(242, 140, 60), Color8(242, 201, 76), Color8(85, 184, 90)]
	for y in range(20):
		for x in range(20): image.set_pixel(x, y, colors[(x + y) % colors.size()])
	image.save_png(path)


func _write_nonlogical(path: String) -> void:
	var image := Image.create(19, 20, false, Image.FORMAT_RGB8)
	image.fill(Color8(255, 0, 255))
	image.save_png(path)


func _cleanup(instance: Node) -> void:
	for source_id in _source_ids: _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads").path_join(source_id))
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions/validation"))
	_remove_tree(_fixture_root)
	instance.queue_free()
	_finish()


func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path): return
	var directory := DirAccess.open(path)
	if directory == null: return
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next()
		if entry.is_empty(): break
		if entry in [".", ".."]: continue
		var child := path.path_join(entry)
		if directory.current_is_dir(): _remove_tree(child)
		else: DirAccess.remove_absolute(child)
	directory.list_dir_end()
	DirAccess.remove_absolute(path)


func _require(condition: bool, message: String) -> void:
	if not condition: _errors.append(message)


func _finish() -> void:
	if _errors.is_empty(): print(PASS_MARKER); quit(0); return
	for error in _errors: push_error(error)
	quit(1)
