extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const IMPORT_NODE_PATH := NodePath("Frame/Layout/Body/Workspace/Padding/Content/OperationsImport")
const OWNER_UPLOADS_ROOT := "res://output/owner-uploads"
const PASS_MARKER := "SB-LFX-002-C001 OWNER_UPLOAD import integration PASS"

var _errors: Array[String] = []
var _fixture_root := ""
var _first_target := ""
var _second_target := ""
var _first_preexisting := false
var _second_preexisting := false
var _first_source_backup := PackedByteArray()
var _first_record_backup := PackedByteArray()
var _second_source_backup := PackedByteArray()
var _second_record_backup := PackedByteArray()


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var packed_scene := ResourceLoader.call("load", MAIN_SCENE_PATH) as PackedScene
	_require(packed_scene != null, "Factory Studio scene did not load")
	if packed_scene == null:
		_finish()
		return
	var instance := packed_scene.instantiate()
	_require(instance != null, "Factory Studio scene did not instantiate")
	if instance == null:
		_finish()
		return
	root.add_child(instance)
	await process_frame
	var navigation := instance.get_node_or_null("Frame/Layout/Body/NavigationPanel/Navigation")
	var import_surface := instance.get_node_or_null(IMPORT_NODE_PATH)
	_require(navigation != null, "real Studio navigation did not instantiate")
	_require(import_surface != null, "real Import surface did not instantiate")
	if navigation == null or import_surface == null:
		instance.queue_free()
		_finish()
		return

	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_002_owner_upload_fixture")
	_remove_tree(_fixture_root)
	DirAccess.make_dir_recursive_absolute(_fixture_root.path_join("first"))
	DirAccess.make_dir_recursive_absolute(_fixture_root.path_join("second"))
	var first_path := _fixture_root.path_join("first").path_join("owner-art.png")
	var second_path := _fixture_root.path_join("second").path_join("owner-art.png")
	var corrupt_path := _fixture_root.path_join("corrupt.png")
	_write_fixture(first_path, Color(0.9, 0.1, 0.1, 1.0), Color(0.1, 0.8, 0.2, 1.0))
	_write_fixture(second_path, Color(0.1, 0.2, 0.9, 1.0), Color(0.8, 0.7, 0.1, 1.0))
	var first_bytes := FileAccess.get_file_as_bytes(first_path)
	var second_bytes := FileAccess.get_file_as_bytes(second_path)
	var external_first_before := first_bytes
	var external_second_before := second_bytes
	var first_id := "owner-upload-" + _sha256(first_bytes)
	var second_id := "owner-upload-" + _sha256(second_bytes)
	_first_target = ProjectSettings.globalize_path(OWNER_UPLOADS_ROOT).path_join(first_id)
	_second_target = ProjectSettings.globalize_path(OWNER_UPLOADS_ROOT).path_join(second_id)
	_first_preexisting = DirAccess.dir_exists_absolute(_first_target)
	_second_preexisting = DirAccess.dir_exists_absolute(_second_target)
	if _first_preexisting:
		_backup_target(_first_target, true)
	if _second_preexisting:
		_backup_target(_second_target, false)
	_require(not _first_preexisting and not _second_preexisting, "deterministic integration fixture identity already exists; refusing to overwrite an owner source")
	if not _errors.is_empty():
		_cleanup(instance)
		return

	navigation.emit_signal("surface_selected", "Import")
	await process_frame
	_require(import_surface.visible, "Import surface did not become visible")
	import_surface.call("set_source_path", first_path)
	import_surface.call("import_selected")
	await process_frame
	var first_result: Dictionary = import_surface.call("snapshot")
	_require(first_result.get("state") == "IMPORTED", "first source did not import: %s" % first_result)
	_require(first_result.get("source_id") == first_id, "source ID is not content-derived")
	_require(first_result.get("origin") == "OWNER_UPLOAD", "source origin is not OWNER_UPLOAD")
	_require(first_result.get("status") == "SOURCE_ONLY", "source is not marked SOURCE_ONLY")
	_require(first_result.get("validation_state") == "UNVALIDATED", "source is not marked UNVALIDATED")
	_require(str(first_result.get("source_only_notice", "")).begins_with("SOURCE ONLY"), "source-only notice is missing")
	_require(first_result.get("original_filename") == "owner-art.png", "original filename display metadata is incorrect")
	_require(first_result.get("original_width") == 4 and first_result.get("original_height") == 3, "decoded source dimensions are incorrect")
	_require(FileAccess.get_file_as_bytes(_first_target.path_join("source.png")) == first_bytes, "stored source bytes differ from selected bytes")
	_require(FileAccess.get_file_as_bytes(first_path) == external_first_before, "external owner source was modified")
	var first_record: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(_first_target.path_join("source.json")))
	_require(first_record.get("source_sha256") == _sha256(first_bytes), "source record hash does not bind selected bytes")
	_require(first_record.get("immutable_relative_path") == "owner-uploads/%s/source.png" % first_id, "source record path binding is incorrect")
	_require(not str(first_record).contains("candidate") and not str(first_record).contains("QA"), "source record contains downstream candidate/QA claims")

	var first_record_before_reimport := FileAccess.get_file_as_bytes(_first_target.path_join("source.json"))
	import_surface.call("set_source_path", first_path)
	import_surface.call("import_selected")
	await process_frame
	var already: Dictionary = import_surface.call("snapshot")
	_require(already.get("state") == "ALREADY_IMPORTED", "same-byte re-import is not idempotent: %s" % already)
	_require(already.get("source_id") == first_id, "same-byte re-import changed source identity")
	_require(FileAccess.get_file_as_bytes(_first_target.path_join("source.json")) == first_record_before_reimport, "same-byte re-import rewrote source metadata")

	import_surface.call("set_source_path", second_path)
	import_surface.call("import_selected")
	await process_frame
	var second_result: Dictionary = import_surface.call("snapshot")
	_require(second_result.get("state") == "IMPORTED", "same-name different-byte source did not import: %s" % second_result)
	_require(second_result.get("source_id") == second_id and second_id != first_id, "same-name different-byte source collided")
	_require(FileAccess.get_file_as_bytes(_first_target.path_join("source.png")) == first_bytes, "first source was overwritten by same-name collision")
	_require(FileAccess.get_file_as_bytes(_second_target.path_join("source.png")) == second_bytes, "second source bytes are not exact")
	_require(FileAccess.get_file_as_bytes(second_path) == external_second_before, "second external owner source was modified")

	var corrupt_record_backup := FileAccess.get_file_as_bytes(_first_target.path_join("source.json"))
	var corrupt_record := FileAccess.open(_first_target.path_join("source.json"), FileAccess.WRITE)
	corrupt_record.store_string("{\"corrupt\":true}")
	corrupt_record.close()
	import_surface.call("set_source_path", first_path)
	import_surface.call("import_selected")
	await process_frame
	var corrupt_result: Dictionary = import_surface.call("snapshot")
	_require(corrupt_result.get("state") == "ERROR", "corrupt existing source record did not fail closed")
	_require(not corrupt_result.has("source_id"), "corrupt source exposed trusted identity")
	var restore_record := FileAccess.open(_first_target.path_join("source.json"), FileAccess.WRITE)
	restore_record.store_buffer(corrupt_record_backup)
	restore_record.close()

	var corrupt_file := FileAccess.open(corrupt_path, FileAccess.WRITE)
	corrupt_file.store_string("not a strict PNG")
	corrupt_file.close()
	import_surface.call("set_source_path", corrupt_path)
	import_surface.call("import_selected")
	await process_frame
	var unsupported: Dictionary = import_surface.call("snapshot")
	_require(unsupported.get("state") == "ERROR", "unsupported/corrupt source did not fail closed")
	_require(not unsupported.has("source_id"), "unsupported source exposed trusted identity")
	_require(FileAccess.get_file_as_bytes(first_path) == external_first_before, "first external source changed during failure paths")
	_require(FileAccess.get_file_as_bytes(second_path) == external_second_before, "second external source changed during failure paths")

	_cleanup(instance)


func _write_fixture(path: String, first: Color, second: Color) -> void:
	var image := Image.create(4, 3, false, Image.FORMAT_RGBA8)
	for y in range(3):
		for x in range(4):
			image.set_pixel(x, y, first if (x + y) % 2 == 0 else second)
	image.save_png(path)


func _sha256(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()


func _backup_target(path: String, first: bool) -> void:
	var source_path := path.path_join("source.png")
	var record_path := path.path_join("source.json")
	if first:
		_first_source_backup = FileAccess.get_file_as_bytes(source_path)
		_first_record_backup = FileAccess.get_file_as_bytes(record_path)
	else:
		_second_source_backup = FileAccess.get_file_as_bytes(source_path)
		_second_record_backup = FileAccess.get_file_as_bytes(record_path)


func _restore_target(path: String, first: bool) -> void:
	if first and not _first_source_backup.is_empty():
		var source_file := FileAccess.open(path.path_join("source.png"), FileAccess.WRITE)
		source_file.store_buffer(_first_source_backup)
		source_file.close()
		var record_file := FileAccess.open(path.path_join("source.json"), FileAccess.WRITE)
		record_file.store_buffer(_first_record_backup)
		record_file.close()
	elif not first and not _second_source_backup.is_empty():
		var source_file := FileAccess.open(path.path_join("source.png"), FileAccess.WRITE)
		source_file.store_buffer(_second_source_backup)
		source_file.close()
		var record_file := FileAccess.open(path.path_join("source.json"), FileAccess.WRITE)
		record_file.store_buffer(_second_record_backup)
		record_file.close()


func _cleanup(instance: Node) -> void:
	_restore_target(_first_target, true)
	_restore_target(_second_target, false)
	if not _first_preexisting:
		_remove_tree(_first_target)
	if not _second_preexisting:
		_remove_tree(_second_target)
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
		if entry in [".", ".."]:
			continue
		var child := path.path_join(entry)
		if directory.current_is_dir():
			_remove_tree(child)
		else:
			DirAccess.remove_absolute(child)
	directory.list_dir_end()
	DirAccess.remove_absolute(path)


func _require(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)


func _finish() -> void:
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for error in _errors:
		push_error(error)
	quit(1)
