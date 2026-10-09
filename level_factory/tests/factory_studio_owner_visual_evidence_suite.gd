extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const MASTERS := ["PIXEL ART", "LEVEL FACTORY", "RELEASE POOL"]
const FILE_NAMES := ["PIXEL_ART_FINAL.png", "LEVEL_FACTORY_FINAL.png", "RELEASE_POOL_FINAL.png"]
const REQUIRED_SIZE := Vector2i(1536, 1024)


func _init() -> void:
	call_deferred("_capture_all")


func _capture_all() -> void:
	var packed_scene := ResourceLoader.call("load", MAIN_SCENE_PATH) as PackedScene
	if packed_scene == null:
		push_error("Factory Studio scene did not load for exact-master evidence.")
		quit(1)
		return
	var instance := packed_scene.instantiate()
	root.add_child(instance)
	await process_frame
	var master_ui := instance.get_node_or_null("MasterUI")
	var output_directory := OS.get_environment("SB_LFX_018_SCREENSHOT_DIR").strip_edges()
	if master_ui == null or output_directory.is_empty():
		push_error("MasterUI or SB_LFX_018_SCREENSHOT_DIR is unavailable.")
		quit(1)
		return
	var directory_error := DirAccess.make_dir_recursive_absolute(output_directory)
	if directory_error != OK:
		push_error("Could not create owner evidence directory: %s" % error_string(directory_error))
		quit(1)
		return
	for index in range(MASTERS.size()):
		master_ui.call("_show_screen", MASTERS[index])
		await process_frame
		await process_frame
		var image := root.get_texture().get_image()
		if image == null or image.is_empty() or image.get_size() != REQUIRED_SIZE:
			push_error("Rendered exact-master viewport must be 1536x1024 for %s." % MASTERS[index])
			quit(1)
			return
		var path := output_directory.path_join(FILE_NAMES[index])
		var save_error := image.save_png(path)
		if save_error != OK:
			push_error("Could not save master screenshot %s: %s" % [path, error_string(save_error)])
			quit(1)
			return
		print("OWNER_MASTER_SCREENSHOT %s %s %dx%d" % [MASTERS[index], path, image.get_width(), image.get_height()])
	instance.queue_free()
	await process_frame
	quit(0)
