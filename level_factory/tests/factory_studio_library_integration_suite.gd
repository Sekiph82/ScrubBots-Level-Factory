extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const IMPORT_NODE_PATH := NodePath("Frame/Layout/Body/Workspace/Padding/Content/OperationsImport")
const LIBRARY_NODE_PATH := NodePath("Frame/Layout/Body/Workspace/Padding/Content/SourceArtLibrary")
const PASS_MARKER := "SB-LFX-003-C001 SOURCE ART LIBRARY integration PASS"

var _errors: Array[String] = []
var _fixture_root := ""
var _source_ids: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var packed_scene := ResourceLoader.load(MAIN_SCENE_PATH) as PackedScene
	_require(packed_scene != null, "Factory Studio scene did not load")
	if packed_scene == null:
		_finish()
		return
	var instance := packed_scene.instantiate()
	root.add_child(instance)
	await process_frame
	var navigation := instance.get_node_or_null("Frame/Layout/Body/NavigationPanel/Navigation")
	var import_surface := instance.get_node_or_null(IMPORT_NODE_PATH)
	var library := instance.get_node_or_null(LIBRARY_NODE_PATH)
	_require(navigation != null and import_surface != null and library != null, "real Import and Library surfaces did not instantiate")
	if navigation == null or import_surface == null or library == null:
		_finish()
		return
	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_003_library_fixture")
	_remove_tree(_fixture_root)
	DirAccess.make_dir_recursive_absolute(_fixture_root)
	var first := _fixture_root.path_join("library-a.png")
	var second := _fixture_root.path_join("library-b.png")
	_write_fixture(first, Color(0.9, 0.1, 0.1, 1.0))
	_write_fixture(second, Color(0.1, 0.2, 0.9, 1.0))
	for path in [first, second]:
		import_surface.call("set_source_path", path)
		import_surface.call("import_selected")
		await process_frame
		var imported: Dictionary = import_surface.call("snapshot")
		_require(imported.get("state") in ["IMPORTED", "ALREADY_IMPORTED"], "fixture did not import: %s" % imported)
		_source_ids.append(str(imported.get("source_id", "")))
	navigation.emit_signal("surface_selected", "Library")
	await process_frame
	library.call("refresh_library")
	await process_frame
	var view: Dictionary = library.call("snapshot")
	_require(view.get("filtered_sources", []).size() >= 2, "Library did not show both verified sources")
	var selected := str(_source_ids[0])
	library.call("select_source", selected)
	library.call("save_selected_metadata", "Library Fixture", ["fixture", "owner"])
	await process_frame
	var saved: Dictionary = library.call("snapshot")
	_require(saved.get("selected_source_id") == selected, "Library selection changed during metadata save")
	var saved_source_found := false
	for saved_source in saved.get("filtered_sources", []):
		if str(saved_source.get("source_id", "")) == selected:
			saved_source_found = str(saved_source.get("catalog", {}).get("label", "")) == "Library Fixture"
	_require(saved_source_found, "Library metadata did not persist through the real Gateway boundary: %s" % saved)
	library.call("set_search", "Library Fixture")
	await process_frame
	var searched: Dictionary = library.call("snapshot")
	_require(searched.get("filtered_sources", []).size() == 1 and str(searched.get("filtered_sources", [])[0].get("source_id", "")) == selected, "Library label search did not filter deterministically")
	_cleanup(instance)


func _write_fixture(path: String, color: Color) -> void:
	var image := Image.create(20, 20, false, Image.FORMAT_RGBA8)
	image.fill(color)
	image.save_png(path)


func _cleanup(instance: Node) -> void:
	for source_id in _source_ids:
		var source_root := ProjectSettings.globalize_path("res://output/owner-uploads").path_join(source_id)
		_remove_tree(source_root)
		var metadata := ProjectSettings.globalize_path("res://output/studio-extensions/source-library/metadata").path_join(source_id + ".json")
		if FileAccess.file_exists(metadata):
			DirAccess.remove_absolute(metadata)
	_remove_tree(_fixture_root)
	instance.queue_free()
	_finish()


func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		return
	var directory := DirAccess.open(path)
	if directory == null:
		return
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next()
		if entry.is_empty():
			break
		if entry in [".", ".."]: continue
		var child := path.path_join(entry)
		if directory.current_is_dir(): _remove_tree(child)
		else: DirAccess.remove_absolute(child)
	directory.list_dir_end()
	DirAccess.remove_absolute(path)


func _require(condition: bool, message: String) -> void:
	if not condition: _errors.append(message)


func _finish() -> void:
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for error in _errors: push_error(error)
	quit(1)
