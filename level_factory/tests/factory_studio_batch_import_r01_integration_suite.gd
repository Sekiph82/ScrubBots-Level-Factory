extends SceneTree

const PASS_MARKER := "SB-LFX-014-C001 BATCH import integration PASS"
var _errors: Array[String] = []
var _fixture_root := ""

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway"); var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/BatchImport")
	_require(gateway != null and surface != null, "batch surface or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_014_batch_fixture"); _remove_tree(_fixture_root); DirAccess.make_dir_recursive_absolute(_fixture_root); DirAccess.make_dir_recursive_absolute(_fixture_root.path_join("second-dir"))
	var first := _fixture_root.path_join("same.png"); var second := _fixture_root.path_join("second-dir").path_join("same.png"); var corrupt := _fixture_root.path_join("bad.png")
	var image := Image.create(20, 20, false, Image.FORMAT_RGB8); image.fill(Color8(20, 120, 220)); image.save_png(first); image.fill(Color8(220, 120, 20)); image.save_png(second); FileAccess.open(corrupt, FileAccess.WRITE).store_string("not png")
	var first_bytes := FileAccess.get_file_as_bytes(first); var second_bytes := FileAccess.get_file_as_bytes(second); var corrupt_bytes := FileAccess.get_file_as_bytes(corrupt)
	_remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var result: Dictionary = gateway.call("run_studio_extension", "batch-import", {"paths": [first, second, first, corrupt]})
	_require(result.get("batch_id", "") != "" and result.get("counts", {}).get("success") == 3 and result.get("counts", {}).get("failed") == 1, "batch did not preserve truthful partial outcomes: %s" % result)
	var items: Array = result.get("items", []); _require(items.size() == 4 and items[0].get("source_id") != items[1].get("source_id") and items[0].get("source_id") == items[2].get("source_id") and items[3].get("source_id") == null, "batch per-item identities are not independent/truthful: %s" % [items])
	var repeated: Dictionary = gateway.call("run_studio_extension", "batch-import", {"paths": [first, second, first, corrupt]}); _require(repeated.get("batch_id", "") != result.get("batch_id", ""), "identical batch execution reused a stable immutable run ID")
	var reloaded: Dictionary = gateway.call("run_studio_extension", "batch-load", {"batch_id": result.get("batch_id", "")}); _require(reloaded.get("state") == "SUCCESS" and reloaded.get("batch", {}).get("items", []).size() == 4 and reloaded.get("batch", {}).get("counts", {}) == result.get("counts", {}), "persisted batch record did not reload with per-item identity/count/provenance")
	_require(FileAccess.get_file_as_bytes(first) == first_bytes and FileAccess.get_file_as_bytes(second) == second_bytes and FileAccess.get_file_as_bytes(corrupt) == corrupt_bytes, "batch import mutated external input bytes")
	_require(surface.get_node_or_null("BatchFileDialog") != null, "Studio batch import did not expose a real multi-file FileDialog")
	surface.call("set_paths", "%s|%s" % [first, second]); surface.call("import_batch"); await process_frame; _require(surface.call("snapshot").get("projection", {}).get("batch_id", "") != "", "batch UI did not invoke canonical import")
	_cleanup(instance)

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(_fixture_root); instance.queue_free(); _finish()

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
