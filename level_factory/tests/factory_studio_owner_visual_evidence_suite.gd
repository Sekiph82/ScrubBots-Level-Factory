extends SceneTree

const MAIN_SCENE_PATH := "res://scenes/factory_studio.tscn"
const DESTINATIONS := ["HOME", "CREATE", "BATCH", "SOLVE", "REVIEW", "LIBRARY", "PUBLISH", "SETTINGS"]
const FILE_NAMES := ["01-home.png", "02-create.png", "03-batch.png", "04-solve.png", "05-review.png", "06-library.png", "07-publish.png", "08-settings.png"]


func _init() -> void:
	call_deferred("_capture_all")


func _capture_all() -> void:
	var packed_scene := ResourceLoader.load(MAIN_SCENE_PATH) as PackedScene
	if packed_scene == null:
		push_error("Factory Studio scene did not load for visual evidence.")
		quit(1)
		return
	var instance := packed_scene.instantiate()
	root.add_child(instance)
	await process_frame
	var workspace := instance.get_node("Frame/Layout/Body/Workspace")
	var output_directory := OS.get_environment("SB_LFX_018_SCREENSHOT_DIR").strip_edges()
	if output_directory.is_empty():
		push_error("SB_LFX_018_SCREENSHOT_DIR must identify the evidence output directory.")
		quit(1)
		return
	var sample_texture: ImageTexture
	var sample_path := OS.get_environment("SB_LFX_018_SAMPLE_PATH").strip_edges()
	print("SAMPLE_PREVIEW path=%s exists=%s" % [sample_path, FileAccess.file_exists(sample_path)])
	if not sample_path.is_empty() and FileAccess.file_exists(sample_path):
		var sample_image := Image.load_from_file(sample_path)
		if sample_image != null and not sample_image.is_empty():
			sample_texture = ImageTexture.create_from_image(sample_image)
			print("SAMPLE_PREVIEW loaded=%dx%d" % [sample_image.get_width(), sample_image.get_height()])
	var directory_error := DirAccess.make_dir_recursive_absolute(output_directory)
	if directory_error != OK:
		push_error("Could not create visual evidence directory: %s (%s)" % [output_directory, error_string(directory_error)])
		quit(1)
		return
	for index in range(DESTINATIONS.size()):
		workspace.call("show_surface", DESTINATIONS[index])
		await process_frame
		await process_frame
		if sample_texture != null:
			var owner_page := workspace.get_node("Padding/Content/OwnerPage")
			var preview := owner_page.get_node("ProductionWorkspace/ArtworkPreviewCard/PreviewContent/PreviewStage/PreviewCenter/ArtworkThumbnail") as TextureRect
			preview.texture = sample_texture
			preview.visible = true
			(owner_page.get_node("ProductionWorkspace/ArtworkPreviewCard/PreviewContent/PreviewStage/PreviewCenter/PreviewEmptyState") as Label).visible = false
			(owner_page.get_node("ProductionWorkspace/ArtworkPreviewCard/PreviewContent/PreviewCaption") as Label).text = "Owner sample · preview only · not imported"
			await process_frame
		var image := root.get_texture().get_image()
		if image == null or image.is_empty():
			push_error("Rendered viewport image is empty for %s." % DESTINATIONS[index])
			quit(1)
			return
		var path := output_directory.path_join(FILE_NAMES[index])
		var save_error := image.save_png(path)
		if save_error != OK:
			push_error("Could not save screenshot for %s: %s" % [DESTINATIONS[index], error_string(save_error)])
			quit(1)
			return
		print("OWNER_SCREENSHOT %s %s %dx%d" % [DESTINATIONS[index], path, image.get_width(), image.get_height()])
	instance.queue_free()
	await process_frame
	quit(0)
