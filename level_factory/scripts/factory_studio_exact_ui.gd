@tool
extends Control

@export var pixel_art_master: Texture2D
@export var level_factory_master: Texture2D
@export var release_pool_master: Texture2D

var _gateway: RefCounted
var _canvas: TextureRect
var _status: Label
var _file_dialog: FileDialog
var _level_dialog: ConfirmationDialog
var _level_number_input: SpinBox
var _level_number_label: Label
var _screen := "PIXEL ART"
var _last_candidate_id := ""
var _last_source_id := ""
var _last_pipeline: Dictionary = {}
var _selected_release_ids: Array[String] = []
var _release_selection_manage_mode := false
var _release_pool: Dictionary = {}
var _operation_running := false
var _column_count := 4
var _level_number := 11
var _manual_level_override := false
var _prompt := "pixel art owl"
var _generation_style := "CREATURE"
var _width := 32
var _height := 32
var _provider_model := "ALPIX (Claude)"
var _generation_mode := "SINGLE"
var _batch_csv_path := ""
var _release_target := "STAGING"
var _release_query := ""
var _difficulty_filter := "All Difficulties"
var _columns_filter := "All Columns"
var _visible_release_ids: Array[String] = []
var _selected_release_id := ""
var _grid_enabled := false
var _zoom := 8.0
var _supply_expanded := false
var _settings_dialog: AcceptDialog
var _prompt_dialog: ConfirmationDialog
var _prompt_input: TextEdit
var _settings_python: LineEdit
var _settings_game: LineEdit
var _release_search: LineEdit
var _release_filter_dialog: ConfirmationDialog
var _filter_difficulty: OptionButton
var _filter_columns: OptionButton
var _release_confirmation: ConfirmationDialog
var _semantic_progress := {"completed": 0, "failed": 0, "remaining": 0}
var _master_buttons: Array[Button] = []
var _grid_lines: Array[Line2D] = []
var _preview_rect: TextureRect
var _selected_art_path := ""
var _seed := ""
var _background_intent := "TRANSPARENT"


func _ready() -> void:
	_canvas = get_node_or_null("MasterCanvas") as TextureRect
	_status = get_node_or_null("Status") as Label
	_file_dialog = get_node_or_null("FileDialog") as FileDialog
	if _canvas == null or _file_dialog == null:
		return
	_file_dialog.file_selected.connect(_on_file_selected)
	_file_dialog.files_selected.connect(_on_files_selected)
	_preview_rect = TextureRect.new()
	_preview_rect.name = "SelectedArtworkPreview"
	_preview_rect.position = Vector2(486, 176)
	_preview_rect.size = Vector2(600, 580)
	_preview_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_preview_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_preview_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_preview_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_preview_rect.visible = false
	add_child(_preview_rect)
	_build_grid_overlay()
	_level_dialog = ConfirmationDialog.new()
	_level_dialog.title = "Level Settings"
	_level_dialog.dialog_text = "Level Number"
	_level_number_input = SpinBox.new()
	_level_number_input.min_value = 1
	_level_number_input.max_value = 999
	_level_number_input.step = 1
	_level_number_input.value = _level_number
	_level_number_input.custom_minimum_size = Vector2(220, 40)
	_level_dialog.add_child(_level_number_input)
	_level_dialog.confirmed.connect(_save_level_number)
	add_child(_level_dialog)
	_build_secondary_surfaces()
	_level_number_label = Label.new()
	_level_number_label.position = Vector2(187, 353)
	_level_number_label.size = Vector2(150, 28)
	_level_number_label.add_theme_color_override("font_color", Color.WHITE)
	_level_number_label.add_theme_font_size_override("font_size", 16)
	_level_number_label.text = "Auto"
	_level_number_label.visible = true
	add_child(_level_number_label)
	_build_hotspots()
	_show_screen(_screen)


func configure_gateway(gateway: RefCounted) -> void:
	_gateway = gateway


func active_master() -> String:
	return _screen


func master_names() -> Array[String]:
	return ["PIXEL ART", "LEVEL FACTORY", "RELEASE POOL"]


func _build_hotspots() -> void:
	# Header tabs are clickable overlays aligned to the owner-approved master.
	_hotspot("PixelArtTab", Rect2(365, 22, 255, 72), _show_screen.bind("PIXEL ART"))
	_hotspot("LevelFactoryTab", Rect2(633, 22, 270, 72), _show_screen.bind("LEVEL FACTORY"))
	_hotspot("ReleasePoolTab", Rect2(918, 22, 270, 72), _show_screen.bind("RELEASE POOL"))
	_hotspot("SettingsGear", Rect2(1320, 15, 55, 60), _open_settings)
	_hotspot("NativeMinimize", Rect2(1376, 14, 44, 42), _minimize_window)
	_hotspot("NativeMaximize", Rect2(1428, 14, 44, 42), _toggle_window_mode)
	_hotspot("NativeClose", Rect2(1477, 14, 48, 42), _close_window)
	# PIXEL ART actions and Batch-CSV path.
	_hotspot("GeneratePixelArt", Rect2(27, 462, 334, 49), _generate_art)
	_hotspot("BatchCsvSelect", Rect2(199, 155, 161, 43), _open_batch_csv)
	_hotspot("RunBatch", Rect2(27, 631, 334, 50), _run_batch)
	_hotspot("Regenerate", Rect2(1208, 452, 294, 48), _generate_art)
	_hotspot("EditPrompt", Rect2(1208, 506, 294, 48), _edit_prompt)
	_hotspot("AddToLevelFactory", Rect2(1208, 560, 294, 48), _send_to_level_factory)
	_hotspot("GenerationPrompt", Rect2(26, 208, 334, 92), _edit_prompt)
	_hotspot("RandomSeed", Rect2(315, 296, 42, 40), _new_seed)
	_hotspot("GenerationStyle", Rect2(27, 337, 334, 42), _choose_style)
	_hotspot("GenerationSize", Rect2(27, 385, 334, 42), _choose_size)
	_hotspot("GenerationProvider", Rect2(27, 433, 334, 42), _choose_provider)
	_hotspot("SingleMode", Rect2(27, 151, 160, 45), _set_generation_mode.bind("SINGLE"))
	_hotspot("BatchMode", Rect2(198, 151, 162, 45), _set_generation_mode.bind("BATCH"))
	_hotspot("BatchCsvPath", Rect2(27, 526, 334, 42), _open_batch_csv)
	_hotspot("ArtworkVariation1", Rect2(1205, 200, 90, 110), _select_artwork.bind(0))
	_hotspot("ArtworkVariation2", Rect2(1302, 200, 90, 110), _select_artwork.bind(1))
	_hotspot("ArtworkVariation3", Rect2(1399, 200, 100, 110), _select_artwork.bind(2))
	_hotspot("ArtworkCarouselLeft", Rect2(1205, 836, 50, 62), _page_artwork.bind(-1))
	_hotspot("ArtworkCarouselRight", Rect2(1470, 836, 50, 62), _page_artwork.bind(1))
	# Shared canvas presentation controls are UI-only and never mutate source bytes.
	_hotspot("ZoomOut", Rect2(650, 124, 34, 34), _adjust_zoom.bind(-1.0))
	_hotspot("ZoomSlider", Rect2(735, 123, 136, 32), _set_zoom_from_pointer)
	_hotspot("ZoomIn", Rect2(875, 124, 34, 34), _adjust_zoom.bind(1.0))
	_hotspot("ZoomOneToOne", Rect2(910, 124, 50, 32), _set_zoom.bind(1.0))
	_hotspot("ZoomFit", Rect2(960, 124, 50, 32), _fit_canvas)
	_hotspot("ToggleGrid", Rect2(1010, 124, 45, 32), _toggle_grid)
	# LEVEL FACTORY: select artwork, set 3/4/5 columns, run real pipeline,
	# then record append-only owner acceptance or rejection for its candidate.
	_hotspot("SelectArtwork", Rect2(42, 165, 95, 100), _open_files.bind(true))
	_hotspot("LevelNumber", Rect2(172, 346, 190, 38), _edit_level_number)
	_hotspot("SupplyColumns3", Rect2(172, 392, 56, 40), _set_columns.bind(3))
	_hotspot("SupplyColumns4", Rect2(238, 392, 56, 40), _set_columns.bind(4))
	_hotspot("SupplyColumns5", Rect2(304, 392, 56, 40), _set_columns.bind(5))
	_hotspot("MaxRobotsAuto", Rect2(172, 440, 190, 38), _keep_auto_robot_cap)
	_hotspot("BackgroundIntent", Rect2(172, 487, 190, 38), _toggle_background)
	_hotspot("RunLevelPipeline", Rect2(26, 803, 335, 52), _run_level_pipeline)
	_hotspot("SolveAgain", Rect2(1207, 625, 291, 50), _solve_again)
	_hotspot("PreviewReplay", Rect2(1368, 390, 130, 38), _preview_replay)
	_hotspot("ExpandSupplyPlan", Rect2(1207, 485, 291, 42), _toggle_supply_plan)
	_hotspot("LevelVariation1", Rect2(425, 835, 85, 88), _select_variation.bind(0))
	_hotspot("LevelVariation2", Rect2(525, 835, 85, 88), _select_variation.bind(1))
	_hotspot("LevelVariation3", Rect2(625, 835, 85, 88), _select_variation.bind(2))
	_hotspot("LevelVariation4", Rect2(725, 829, 91, 100), _select_variation.bind(3))
	_hotspot("LevelVariation5", Rect2(831, 835, 85, 88), _select_variation.bind(4))
	_hotspot("LevelVariation6", Rect2(931, 835, 85, 88), _select_variation.bind(5))
	_hotspot("LevelVariation7", Rect2(1031, 835, 85, 88), _select_variation.bind(6))
	_hotspot("LevelVariation8", Rect2(1131, 835, 85, 88), _select_variation.bind(7))
	_hotspot("AcceptLevel", Rect2(1207, 686, 138, 50), _review_candidate.bind("ACCEPT"))
	_hotspot("RejectLevel", Rect2(1360, 686, 138, 50), _review_candidate.bind("REJECT"))
	# RELEASE POOL uses canonical pool, campaign, and staging operations.
	_hotspot("RefreshReleasePool", Rect2(27, 188, 330, 46), _refresh_release_pool)
	_hotspot("SelectReleaseLevel", Rect2(25, 261, 335, 68), _select_first_release)
	_hotspot("ReleaseSearch", Rect2(25, 154, 335, 44), _edit_release_search)
	_hotspot("DifficultyFilter", Rect2(25, 211, 165, 40), _open_release_filters)
	_hotspot("ColumnsFilter", Rect2(196, 211, 164, 40), _open_release_filters)
	_hotspot("ReleaseRow2", Rect2(25, 336, 335, 62), _select_release_row.bind(1))
	_hotspot("ReleaseRow3", Rect2(25, 405, 335, 62), _select_release_row.bind(2))
	_hotspot("ReleaseRow4", Rect2(25, 474, 335, 62), _select_release_row.bind(3))
	_hotspot("ReleaseRow5", Rect2(25, 543, 335, 62), _select_release_row.bind(4))
	_hotspot("ReleaseRow6", Rect2(25, 612, 335, 62), _select_release_row.bind(5))
	_hotspot("ReleaseRow7", Rect2(25, 681, 335, 62), _select_release_row.bind(6))
	_hotspot("ReleaseRow8", Rect2(25, 750, 335, 62), _select_release_row.bind(7))
	_hotspot("ManageSelection", Rect2(25, 826, 335, 52), _manage_release_selection)
	_hotspot("SelectAllRelease", Rect2(25, 889, 164, 48), _select_all_release)
	_hotspot("ClearRelease", Rect2(198, 889, 162, 48), _clear_release_selection)
	_hotspot("SelectedReleaseCard1", Rect2(405, 839, 198, 105), _select_release_card.bind(0))
	_hotspot("SelectedReleaseCard2", Rect2(618, 839, 198, 105), _select_release_card.bind(1))
	_hotspot("SelectedReleaseCard3", Rect2(830, 839, 198, 105), _select_release_card.bind(2))
	_hotspot("RemoveSelected1", Rect2(580, 839, 24, 24), _remove_release_selection.bind(0))
	_hotspot("RemoveSelected2", Rect2(794, 839, 24, 24), _remove_release_selection.bind(1))
	_hotspot("RemoveSelected3", Rect2(1005, 839, 24, 24), _remove_release_selection.bind(2))
	_hotspot("AddMoreLevels", Rect2(1044, 839, 198, 105), _show_screen.bind("RELEASE POOL"))
	_hotspot("ReleaseStaging", Rect2(1215, 398, 280, 36), _set_release_target.bind("STAGING"))
	_hotspot("ReleaseProduction", Rect2(1215, 438, 280, 36), _set_release_target.bind("PRODUCTION"))
	_hotspot("PreflightRelease", Rect2(1207, 485, 291, 40), _preflight_release)
	_hotspot("ValidateReleaseAssets", Rect2(1207, 530, 291, 36), _show_publish_stage.bind("VALIDATE_ASSETS"))
	_hotspot("BuildReleasePack", Rect2(1207, 568, 291, 36), _show_publish_stage.bind("BUILD_SCRUBPACK"))
	_hotspot("UploadR2Status", Rect2(1207, 606, 291, 36), _show_publish_stage.bind("UPLOAD_R2"))
	_hotspot("UploadSelected", Rect2(1207, 648, 291, 54), _upload_selected)
	_hotspot("PreviewReleaseManifest", Rect2(1207, 713, 291, 50), _preview_release_manifest)
	_update_hotspot_visibility()


func _hotspot(node_name: String, rect: Rect2, action: Callable) -> Button:
	var button := Button.new()
	button.name = node_name
	button.position = rect.position
	button.size = rect.size
	button.flat = true
	button.focus_mode = Control.FOCUS_NONE
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.add_theme_stylebox_override("normal", _transparent_style())
	button.add_theme_stylebox_override("hover", _transparent_style())
	button.add_theme_stylebox_override("pressed", _transparent_style())
	button.add_theme_stylebox_override("focus", _transparent_style())
	button.pressed.connect(action)
	button.set_meta("master_control", true)
	add_child(button)
	_master_buttons.append(button)
	return button


func _build_secondary_surfaces() -> void:
	_prompt_dialog = ConfirmationDialog.new()
	_prompt_dialog.title = "Prompt"
	_prompt_dialog.dialog_text = ""
	_prompt_input = TextEdit.new()
	_prompt_input.custom_minimum_size = Vector2(520, 170)
	_prompt_input.text = _prompt
	_prompt_dialog.add_child(_prompt_input)
	_prompt_dialog.confirmed.connect(func(): _prompt = _prompt_input.text.strip_edges())
	add_child(_prompt_dialog)
	_settings_dialog = AcceptDialog.new()
	_settings_dialog.title = "Settings"
	var settings := VBoxContainer.new()
	settings.custom_minimum_size = Vector2(540, 170)
	_settings_python = LineEdit.new()
	_settings_python.placeholder_text = "Factory Python executable"
	_settings_python.text = OS.get_environment("SCRUBBOTS_FACTORY_PYTHON")
	_settings_game = LineEdit.new()
	_settings_game.placeholder_text = "ScrubBots project path"
	_settings_game.text = OS.get_environment("SCRUBBOTS_PROJECT")
	settings.add_child(_settings_python)
	settings.add_child(_settings_game)
	_settings_dialog.add_child(settings)
	add_child(_settings_dialog)
	_settings_dialog.confirmed.connect(func():
		OS.set_environment("SCRUBBOTS_FACTORY_PYTHON", _settings_python.text.strip_edges())
		OS.set_environment("SCRUBBOTS_PROJECT", _settings_game.text.strip_edges())
		if _gateway != null:
			_gateway.set("python_executable", _settings_python.text.strip_edges())
			_gateway.call("_refresh_connection")
	)
	_release_filter_dialog = ConfirmationDialog.new()
	_release_filter_dialog.title = "Release Pool Filters"
	var filters := VBoxContainer.new()
	_filter_difficulty = OptionButton.new()
	for item in ["All Difficulties", "Easy", "Medium", "Hard"]: _filter_difficulty.add_item(item)
	_filter_columns = OptionButton.new()
	for item in ["All Columns", "3 columns", "4 columns", "5 columns"]: _filter_columns.add_item(item)
	filters.add_child(_filter_difficulty)
	filters.add_child(_filter_columns)
	_release_filter_dialog.add_child(filters)
	_release_filter_dialog.confirmed.connect(_apply_release_filters)
	add_child(_release_filter_dialog)
	_release_confirmation = ConfirmationDialog.new()
	_release_confirmation.title = "Confirm Production Promotion"
	add_child(_release_confirmation)
	_release_search = LineEdit.new()
	_release_search.text_changed.connect(func(value):
		_release_query = value
		_apply_release_projection()
	)
	add_child(_release_search)
	_release_search.visible = false


func _transparent_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0, 0, 0, 0)
	style.border_color = Color(0, 0, 0, 0)
	return style


func _show_screen(name: String) -> void:
	if name not in master_names() or _canvas == null:
		return
	_screen = name
	var texture: Texture2D = pixel_art_master if name == "PIXEL ART" else level_factory_master if name == "LEVEL FACTORY" else release_pool_master
	if texture == null:
		_report("Owner-approved screen master is unavailable: " + name)
		return
	_canvas.texture = texture
	_update_hotspot_visibility()
	if _status != null:
		_status.visible = false
	if name == "RELEASE POOL":
		_refresh_release_pool(false)
		_apply_release_projection()
	elif not _selected_art_path.is_empty():
		_load_selected_art_preview(_selected_art_path)


func _update_hotspot_visibility() -> void:
	var shared := ["PixelArtTab", "LevelFactoryTab", "ReleasePoolTab", "SettingsGear", "ZoomOut", "ZoomSlider", "ZoomIn", "ZoomOneToOne", "ZoomFit", "ToggleGrid"]
	var pixel := ["GeneratePixelArt", "BatchCsvSelect", "RunBatch", "Regenerate", "EditPrompt", "AddToLevelFactory", "GenerationPrompt", "RandomSeed", "GenerationStyle", "GenerationSize", "GenerationProvider", "SingleMode", "BatchMode", "BatchCsvPath", "ArtworkVariation1", "ArtworkVariation2", "ArtworkVariation3", "ArtworkCarouselLeft", "ArtworkCarouselRight"]
	var level := ["SelectArtwork", "LevelNumber", "SupplyColumns3", "SupplyColumns4", "SupplyColumns5", "MaxRobotsAuto", "BackgroundIntent", "RunLevelPipeline", "SolveAgain", "PreviewReplay", "ExpandSupplyPlan", "AcceptLevel", "RejectLevel", "LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5", "LevelVariation6", "LevelVariation7", "LevelVariation8"]
	var release := ["RefreshReleasePool", "SelectReleaseLevel", "ReleaseSearch", "DifficultyFilter", "ColumnsFilter", "ReleaseRow2", "ReleaseRow3", "ReleaseRow4", "ReleaseRow5", "ReleaseRow6", "ReleaseRow7", "ReleaseRow8", "ManageSelection", "SelectAllRelease", "ClearRelease", "SelectedReleaseCard1", "SelectedReleaseCard2", "SelectedReleaseCard3", "RemoveSelected1", "RemoveSelected2", "RemoveSelected3", "AddMoreLevels", "ReleaseStaging", "ReleaseProduction", "PreflightRelease", "ValidateReleaseAssets", "BuildReleasePack", "UploadR2Status", "UploadSelected", "PreviewReleaseManifest", "NativeMinimize", "NativeMaximize", "NativeClose"]
	for button in _master_buttons:
		button.visible = button.name in shared or (_screen == "PIXEL ART" and button.name in pixel) or (_screen == "LEVEL FACTORY" and button.name in level) or (_screen == "RELEASE POOL" and button.name in release)


func _report(message: String) -> void:
	if _status == null:
		return
	_status.text = message
	_status.visible = true
	get_tree().create_timer(4.0).timeout.connect(func():
		if _status != null and _status.text == message:
			_status.visible = false
	)


func _open_files(multiple: bool) -> void:
	if _file_dialog == null:
		return
	_file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILES if multiple else FileDialog.FILE_MODE_OPEN_FILE
	_file_dialog.title = "Select artwork PNG"
	_file_dialog.clear_filters()
	_file_dialog.add_filter("*.png ; PNG image")
	if _screen == "LEVEL FACTORY": _file_dialog.add_filter("*.csv ; Level batch CSV")
	_file_dialog.popup_centered_ratio(0.72)


func _open_batch_csv() -> void:
	if _file_dialog == null:
		return
	_file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	_file_dialog.title = "Select artwork batch CSV"
	_file_dialog.clear_filters()
	_file_dialog.add_filter("*.csv ; CSV batch")
	_file_dialog.popup_centered_ratio(0.72)


func _process_level_csv(path: String) -> void:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_report("Could not read the level batch CSV")
		return
	var header := file.get_csv_line()
	var legacy := PackedStringArray(["artwork_path", "level_number", "supply_columns", "background_intent"])
	var automatic := PackedStringArray(["artwork_path", "supply_columns", "background_intent"])
	if header != legacy and header != automatic:
		file.close()
		_report("CSV columns: artwork_path,supply_columns,background_intent (optional legacy level_number is ignored)")
		return
	var ready := 0
	var failed := 0
	while not file.eof_reached():
		var row := file.get_csv_line()
		if row.size() == 1 and row[0].strip_edges().is_empty(): continue
		var col_index := 2 if header == legacy else 1
		var bg_index := 3 if header == legacy else 2
		if row.size() != header.size() or (header == legacy and not row[1].is_valid_int()) or not row[col_index].is_valid_int() or int(row[col_index]) not in [3, 4, 5] or row[bg_index] not in ["TRANSPARENT", "BACKGROUND"]:
			failed += 1
			continue
		var source_ref := row[0].strip_edges()
		var source_id := ""
		if source_ref.begins_with("source_id:"):
			source_id = source_ref.trim_prefix("source_id:")
		else:
			var artwork_path := source_ref if source_ref.is_absolute_path() else path.get_base_dir().path_join(source_ref)
			var imported := _extension("batch-import", {"paths": [artwork_path]})
			var imported_items: Array = imported.get("items", [])
			if not imported_items.is_empty(): source_id = str(imported_items[0].get("source_id", ""))
		if source_id.is_empty():
			failed += 1
			continue
		var request := {"column_count": int(row[col_index]), "level_number": _level_number if _manual_level_override else 1, "background_intent": row[bg_index], "game_project": OS.get_environment("SCRUBBOTS_PROJECT")}
		var result := _extension("pipeline", {"source_id": source_id, "request": request})
		if str(result.get("disposition", "")) == "READY":
			ready += 1
			_last_source_id = source_id
			_last_candidate_id = str(result.get("derived_candidate_id", _last_candidate_id))
			_last_pipeline = result
			_refresh_release_pool(false)
		else:
			failed += 1
	file.close()
	_report("Batch pipeline: %d READY · %d failed" % [ready, failed])


func _minimize_window() -> void:
	get_window().mode = Window.MODE_MINIMIZED


func _toggle_window_mode() -> void:
	var window := get_window()
	window.mode = Window.MODE_WINDOWED if window.mode == Window.MODE_MAXIMIZED else Window.MODE_MAXIMIZED


func _close_window() -> void:
	get_tree().quit()


func _on_file_selected(path: String) -> void:
	if path.get_extension().to_lower() == "png":
		_selected_art_path = path
		_load_selected_art_preview(path)
	if path.get_extension().to_lower() == "csv":
		_process_level_csv(path) if _screen == "LEVEL FACTORY" else _generate_batch_csv(path)
		return
	if _screen == "LEVEL FACTORY":
		var imported: Dictionary = _extension("batch-import", {"paths": [path]})
		var items: Array = imported.get("items", [])
		if not items.is_empty():
			_last_source_id = str(items[0].get("source_id", ""))
			if _last_source_id.is_empty():
				_report(str(items[0].get("state", imported.get("state", "Import unavailable"))))
			else:
				_last_candidate_id = ""
				_report("Artwork selected. Run the canonical pipeline to continue.")
		else:
			_report(str(imported.get("reason", imported.get("error", "Artwork import unavailable."))))
	else:
		var imported: Dictionary = _extension("batch-import", {"paths": [path]})
		_report(str(imported.get("state", imported.get("reason", "Artwork imported."))))


func _on_files_selected(paths: PackedStringArray) -> void:
	var result := _extension("batch-import", {"paths": Array(paths)})
	var items: Array = result.get("items", [])
	var succeeded := 0
	var failed := 0
	for item in items:
		var source_id := str(item.get("source_id", ""))
		if source_id.is_empty():
			failed += 1
			continue
		var pipeline := _extension("pipeline", {"source_id": source_id, "request": {"column_count": _column_count, "level_number": _level_number if _manual_level_override else 1, "background_intent": _background_intent, "game_project": OS.get_environment("SCRUBBOTS_PROJECT")}})
		if str(pipeline.get("disposition", "")) == "READY":
			succeeded += 1
			_last_source_id = source_id
			_last_candidate_id = str(pipeline.get("derived_candidate_id", _last_candidate_id))
			_last_pipeline = pipeline
			_refresh_release_pool(false)
		else:
			failed += 1
	_report("Batch pipeline: %d READY · %d failed" % [succeeded, failed])


func _generate_art() -> void:
	if _operation_running:
		return
	_last_candidate_id = ""
	_last_source_id = ""
	_last_pipeline = {}
	_seed = "pixel-art-%d" % Time.get_unix_time_from_system()
	var result := _generate_request({"prompt": _prompt, "style": _generation_style, "width": _width, "height": _height, "provider": _provider_model, "seed": _seed, "background_intent": _background_intent})
	_finish_generation(result)


func _run_batch() -> void:
	if not _batch_csv_path.is_empty() and str(_semantic_progress.get("state", "")) in ["LIMIT", "UNAVAILABLE", "NEEDS_RETRY"]:
		_generate_batch_csv(_batch_csv_path)
		return
	_open_batch_csv()


func _generate_batch_csv(path: String) -> void:
	if _gateway == null or _operation_running:
		return
	_batch_csv_path = path
	if _provider_model == "ALPIX (Claude)":
		_operation_running = true
		var job := _extension("alpix-csv-job", {"csv_path": path, "default_width": _width, "default_height": _height})
		_operation_running = false
		_semantic_progress = {"job_id": job.get("job_id", ""), "completed": job.get("completed", 0), "failed": job.get("failed", 0), "remaining": job.get("remaining", 0), "state": job.get("state", "ERROR")}
		_set_batch_action_label(str(job.get("state", "ERROR")) in ["LIMIT", "UNAVAILABLE", "NEEDS_RETRY"])
		var rows: Array = job.get("rows", [])
		for row in rows:
			if str(row.get("state", "")) == "IMPORTED":
				_last_source_id = str(row.get("source_id", _last_source_id))
				_selected_art_path = str(row.get("artifact_path", _selected_art_path))
		if not _selected_art_path.is_empty():
			_load_selected_art_preview(_selected_art_path)
		_report("ALPIX %s · %d complete · %d remaining" % [str(job.get("state", "ERROR")), int(job.get("completed", 0)), int(job.get("remaining", 0))])
		return
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_report("Could not read the selected CSV file.")
		return
	var expected := PackedStringArray(["prompt", "style", "width", "height", "provider", "seed", "background_intent"])
	var header := file.get_csv_line()
	if header != expected and header != PackedStringArray(["prompt", "style", "size", "provider", "seed", "background_intent"]):
		_report("CSV must use prompt,style,width,height,provider,seed,background_intent.")
		return
	var succeeded := 0
	var failed := 0
	var row_number := 0
	while not file.eof_reached():
		var row := file.get_csv_line()
		if row.size() == 1 and row[0].strip_edges().is_empty():
			continue
		row_number += 1
		if row_number > 100:
			_report("CSV batch stopped at the 100-row owner limit.")
			break
		if row.size() != header.size():
			_report("CSV row %d has the wrong number of fields." % row_number)
			failed += 1
			continue
		var row_values := {}
		for index in range(header.size()): row_values[str(header[index]).strip_edges()] = row[index].strip_edges()
		var dims := _csv_dimensions(row_values)
		var result := _generate_request({"prompt": str(row_values.get("prompt", "")), "style": str(row_values.get("style", _generation_style)), "width": dims.x, "height": dims.y, "provider": str(row_values.get("provider", _provider_model)), "seed": str(row_values.get("seed", "")), "background_intent": str(row_values.get("background_intent", _background_intent))})
		if str(result.get("state", "")) in ["SUCCESS", "IMPORTED"]:
			_last_candidate_id = str(result.get("candidate_id", _last_candidate_id))
			_last_source_id = str(result.get("source_id", _last_source_id))
			succeeded += 1
		else:
			failed += 1
	_operation_running = false
	_semantic_progress = {"completed": succeeded, "failed": failed, "remaining": 0}
	_report("Batch: %d succeeded · %d failed" % [succeeded, failed])
	file.close()


func _edit_prompt() -> void:
	_prompt_input.text = _prompt
	_prompt_dialog.popup_centered()


func _send_to_level_factory() -> void:
	_show_screen("LEVEL FACTORY")
	if _last_candidate_id.is_empty():
		_report("Generate or select a candidate first.")
	else:
		_report("Candidate %s selected. Choose supply columns and run the pipeline." % _last_candidate_id)


func _run_level_pipeline() -> void:
	if _gateway == null or _operation_running:
		return
	if _last_candidate_id.is_empty() and _last_source_id.is_empty():
		_report("Select or generate a candidate first.")
		return
	_operation_running = true
	var request := {"column_count": _column_count, "level_number": _level_number if _manual_level_override else 1, "game_project": OS.get_environment("SCRUBBOTS_PROJECT"), "background_intent": _background_intent, "max_robots": null, "target_difficulty": "V1_ADVISORY"}
	var pipeline_request := {"source_id": _last_source_id, "request": request} if not _last_source_id.is_empty() else {"candidate_id": _last_candidate_id, "request": request}
	var result: Dictionary = _extension("pipeline", pipeline_request)
	_last_pipeline = result
	if not str(result.get("derived_candidate_id", "")).is_empty():
		_last_candidate_id = str(result["derived_candidate_id"])
	if str(result.get("disposition", "")) == "READY":
		_refresh_release_pool(false)
	_report("Pipeline %s · %s" % [str(result.get("disposition", result.get("state", "UNKNOWN"))), str(result.get("run_id", ""))])
	_operation_running = false


func _set_columns(columns: int) -> void:
	_column_count = columns if columns in [3, 4, 5] else 4
	_report("Supply columns: %d" % _column_count)


func _edit_level_number() -> void:
	_level_number_input.value = _level_number
	_level_dialog.popup_centered()


func _save_level_number() -> void:
	_level_number = int(_level_number_input.value)
	_manual_level_override = true
	_level_number_label.text = str(_level_number)
	_level_number_label.visible = true
	_report("Manual level number: %d" % _level_number)


func _review_candidate(disposition: String) -> void:
	if _last_candidate_id.is_empty():
		_report("Select a candidate before recording owner review.")
		return
	if disposition == "ACCEPT":
		var primary: Dictionary = _last_pipeline.get("primary", {})
		if str(_last_pipeline.get("disposition", "")) != "READY" or str(primary.get("state", "")) != "READY":
			_report("Accept is available only after the canonical solver, replay, Difficulty V1, and QA pipeline is READY.")
			return
	var result := _extension("owner-review", {"candidate_id": _last_candidate_id, "disposition": disposition})
	_report("Owner %s · %s" % [disposition, str(result.get("review_id", result.get("state", "UNAVAILABLE")))])
	if disposition == "ACCEPT":
		_refresh_release_pool()


func _refresh_release_pool(show_status: bool = true) -> void:
	_release_pool = _extension("release-pool", {})
	_apply_release_projection()
	if show_status:
		_report("READY levels: %s" % str(_release_pool.get("pool_size", 0)))


func _select_first_release() -> void:
	if _visible_release_ids.is_empty():
		_report("No READY, included level is available in the Release Pool.")
		return
	var id := _visible_release_ids[0]
	if id not in _selected_release_ids: _selected_release_ids.append(id)
	_selected_release_id = id
	_report("Selected %d READY level(s)" % _selected_release_ids.size())


func _preflight_release() -> void:
	if _selected_release_ids.is_empty():
		_report("Select one or more READY levels first.")
		return
	var result := _extension("scrubbots-publish", {
		"action": "preflight", "candidate_ids": _selected_release_ids,
		"pack_id": "factory-studio-release",
		"created_at_utc": Time.get_datetime_string_from_system(true, false) + "Z",
	})
	_release_pool["publish_preflight"] = result
	_report("Preflight: %s" % str(result.get("state", result.get("disposition", "UNAVAILABLE"))))


func _show_publish_stage(stage: String) -> void:
	var preflight: Dictionary = _release_pool.get("publish_preflight", {})
	_report("%s · %s" % [stage, str(preflight.get("state", "NOT_RUN"))])


func _publish_staging() -> void:
	var preflight: Dictionary = _release_pool.get("publish_preflight", {})
	var reviewed: Dictionary = preflight.get("reviewed_identity", {})
	if reviewed.is_empty():
		_report("Run publish preflight before STAGING upload.")
		return
	var result := _extension("scrubbots-publish", {
		"action": "publish-staging", "candidate_ids": _selected_release_ids,
		"pack_id": "factory-studio-release",
		"content_version": int(reviewed.get("content_version", 0)),
		"created_at_utc": str(reviewed.get("created_at_utc", "")),
		"reviewed_identity": reviewed,
	})
	_report("STAGING: %s" % str(result.get("state", result.get("disposition", "UNAVAILABLE"))))


func _generate_request(request: Dictionary) -> Dictionary:
	if _gateway == null or _operation_running:
		return {"state": "UNAVAILABLE", "reason": "Factory Core is unavailable."}
	_operation_running = true
	var result: Dictionary
	var selected_provider := str(request.get("provider", _provider_model))
	if selected_provider == "ALPIX (Claude)":
		result = _extension("alpix-generate", {"prompt": request.get("prompt", ""), "width": request.get("width", 32), "height": request.get("height", 32)})
	elif selected_provider == "MAGNIFIC":
		result = _extension("magnific-prepare", {"prompt": request.get("prompt", ""), "width": request.get("width", 32), "height": request.get("height", 32), "background_intent": request.get("background_intent", "TRANSPARENT")})
	elif selected_provider == "PIXELLAB":
		var model := "PIXFLUX"
		result = _extension("semantic-generate", {"prompt": request.get("prompt", ""), "style": request.get("style", ""), "provider_id": "PIXELLAB", "provider_model": model, "width": request.get("width", 32), "height": request.get("height", 32), "seed": request.get("seed", ""), "background_intent": request.get("background_intent", "TRANSPARENT")})
	else:
		result = {"state": "UNAVAILABLE", "reason": "Selected provider is not configured."}
	_operation_running = false
	return result


func _finish_generation(result: Dictionary) -> void:
	_last_candidate_id = str(result.get("candidate_id", _last_candidate_id))
	_last_source_id = str(result.get("source_id", _last_source_id))
	if not str(result.get("output_path", result.get("source_path", ""))).is_empty():
		_selected_art_path = str(result.get("output_path", result.get("source_path", ""))).path_join("artwork.png") if result.has("output_path") else str(result.get("source_path", ""))
		_load_selected_art_preview(_selected_art_path)
	_report("%s · %s" % [_last_candidate_id, str(result.get("state", "ERROR"))])


func _csv_dimensions(values: Dictionary) -> Vector2i:
	if values.has("size"):
		var parts := str(values["size"]).to_lower().split("x", false)
		if parts.size() == 2 and parts[0].is_valid_int() and parts[1].is_valid_int():
			return Vector2i(int(parts[0]), int(parts[1]))
	return Vector2i(int(values.get("width", 0)) if str(values.get("width", "")).is_valid_int() else 0, int(values.get("height", 0)) if str(values.get("height", "")).is_valid_int() else 0)


func _set_generation_mode(mode: String) -> void:
	_generation_mode = mode if mode in ["SINGLE", "BATCH"] else "SINGLE"
	_report("Mode: " + _generation_mode)


func _new_seed() -> void:
	_seed = "pixel-art-%d" % Time.get_unix_time_from_system()
	_report("New seed selected")


func _choose_style() -> void:
	var dialog := ConfirmationDialog.new()
	dialog.title = "Style"
	var choice := OptionButton.new()
	var styles := ["ROBOT", "CREATURE", "FISH", "SEA_CREATURE", "SPACE_SHIP", "INSECT", "FACE_EMBLEM", "TREE_PLANT", "CORAL", "ABSTRACT_SYMBOL"]
	for style in styles: choice.add_item(style)
	choice.selected = maxi(0, styles.find(_generation_style))
	dialog.add_child(choice)
	dialog.confirmed.connect(func(): _generation_style = choice.get_item_text(choice.selected); dialog.queue_free())
	dialog.canceled.connect(func(): dialog.queue_free())
	add_child(dialog)
	dialog.popup_centered()


func _choose_size() -> void:
	var dialog := ConfirmationDialog.new()
	dialog.title = "Size"
	var row := HBoxContainer.new()
	var width_input := SpinBox.new(); width_input.min_value = 20; width_input.max_value = 59; width_input.value = _width
	var height_input := SpinBox.new(); height_input.min_value = 20; height_input.max_value = 59; height_input.value = _height
	row.add_child(width_input); row.add_child(height_input); dialog.add_child(row)
	dialog.confirmed.connect(func(): _width = int(width_input.value); _height = int(height_input.value); dialog.queue_free())
	dialog.canceled.connect(func(): dialog.queue_free())
	add_child(dialog); dialog.popup_centered()


func _choose_provider() -> void:
	var dialog := ConfirmationDialog.new()
	dialog.title = "Provider"
	var choice := OptionButton.new()
	var result := _extension("provider-options", {})
	var options: Array = result.get("providers", [])
	var names: Array[String] = []
	for item in options:
		if item is Dictionary:
			names.append(str(item.get("id", "")))
	for item in names: choice.add_item(item)
	var selected := maxi(0, names.find(_provider_model))
	if not names.is_empty(): choice.select(selected)
	dialog.add_child(choice)
	dialog.confirmed.connect(func():
		if choice.item_count > 0: _provider_model = choice.get_item_text(choice.selected)
		dialog.queue_free()
	)
	dialog.canceled.connect(func(): dialog.queue_free())
	add_child(dialog); dialog.popup_centered()


func _set_batch_action_label(resume: bool) -> void:
	for button in _master_buttons:
		if button.name == "RunBatch":
			button.text = "Resume" if resume else "Run Batch"
			return


func _open_settings() -> void:
	_settings_dialog.popup_centered()


func _load_selected_art_preview(path: String) -> void:
	var global_path := ProjectSettings.globalize_path(path) if path.begins_with("res://") else path
	if not FileAccess.file_exists(global_path):
		return
	var image := Image.load_from_file(global_path)
	if image == null or image.is_empty():
		return
	_preview_rect.texture = ImageTexture.create_from_image(image)
	_preview_rect.visible = true
	var transparent := 0
	for y in range(image.get_height()):
		for x in range(image.get_width()):
			if image.get_pixel(x, y).a < 1.0: transparent += 1
	_report("%d × %d · %d colors · %d transparent · PNG" % [image.get_width(), image.get_height(), image.get_used_colors().size(), transparent])


func _select_artwork(index: int) -> void:
	_select_inbox_candidate(index)


func _page_artwork(direction: int) -> void:
	# The artwork strip is a bounded UI-only carousel over the canonical inbox.
	var inbox := _extension("candidate-inbox", {})
	var candidates: Array = inbox.get("candidates", [])
	if candidates.is_empty():
		_report("No artwork candidates")
		return
	var current := 0
	for i in range(candidates.size()):
		if str(candidates[i].get("candidate_id", "")) == _last_candidate_id: current = i
	var chosen: Dictionary = candidates[posmod(current + direction, candidates.size())]
	_last_candidate_id = str(chosen.get("candidate_id", ""))
	_report("Artwork selected")


func _select_variation(index: int) -> void:
	_select_inbox_candidate(index)


func _select_inbox_candidate(index: int) -> void:
	var inbox := _extension("candidate-inbox", {})
	var candidates: Array = inbox.get("candidates", [])
	if index < 0 or index >= candidates.size(): return
	var candidate: Dictionary = candidates[index]
	_last_candidate_id = str(candidate.get("candidate_id", ""))
	var source_path := str(candidate.get("source_path", candidate.get("artwork_path", "")))
	if source_path.ends_with("artwork.png"): _selected_art_path = source_path
	elif not source_path.is_empty(): _selected_art_path = source_path.path_join("artwork.png")
	if not _selected_art_path.is_empty(): _load_selected_art_preview(_selected_art_path)
	_report("Artwork selected")


func _adjust_zoom(amount: float) -> void:
	_set_zoom(clampf(_zoom + amount, 1.0, 16.0))


func _set_zoom(value: float) -> void:
	_zoom = clampf(value, 1.0, 16.0)
	_preview_rect.scale = Vector2.ONE * (_zoom / 8.0)


func _set_zoom_from_pointer() -> void:
	var position_x := get_viewport().get_mouse_position().x
	_set_zoom(1.0 + clampf((position_x - 735.0) / 136.0, 0.0, 1.0) * 15.0)


func _fit_canvas() -> void:
	_set_zoom(8.0)


func _toggle_grid() -> void:
	_grid_enabled = not _grid_enabled
	for line in _grid_lines: line.visible = _grid_enabled
	_report("Grid %s" % ("On" if _grid_enabled else "Off"))


func _build_grid_overlay() -> void:
	for index in range(33):
		var vertical := Line2D.new(); vertical.name = "GridVertical%02d" % index
		vertical.add_point(Vector2(486 + index * (600.0 / 32.0), 176)); vertical.add_point(Vector2(486 + index * (600.0 / 32.0), 756))
		var horizontal := Line2D.new(); horizontal.name = "GridHorizontal%02d" % index
		horizontal.add_point(Vector2(486, 176 + index * (580.0 / 32.0))); horizontal.add_point(Vector2(1086, 176 + index * (580.0 / 32.0)))
		for line in [vertical, horizontal]:
			line.width = 1.0
			line.default_color = Color(1, 1, 1, 0.22)
			line.visible = false
			add_child(line)
			_grid_lines.append(line)


func _keep_auto_robot_cap() -> void:
	_report("Max robots: Auto")


func _toggle_background() -> void:
	_background_intent = "BACKGROUND" if _background_intent == "TRANSPARENT" else "TRANSPARENT"
	_report("Background intent: " + _background_intent)


func _solve_again() -> void:
	_run_level_pipeline()


func _preview_replay() -> void:
	var primary: Dictionary = _last_pipeline.get("primary", {})
	var replay: Dictionary = primary.get("replay", primary.get("replay_verification", {}))
	if replay.is_empty():
		_report("Replay proof is not available")
		return
	var dialog := AcceptDialog.new()
	dialog.title = "Replay Preview"
	var text := JSON.stringify(replay, "  ")
	var label := RichTextLabel.new(); label.custom_minimum_size = Vector2(700, 420); label.text = text; label.fit_content = true
	dialog.add_child(label); add_child(dialog); dialog.confirmed.connect(func(): dialog.queue_free()); dialog.popup_centered()


func _toggle_supply_plan() -> void:
	_supply_expanded = not _supply_expanded
	var primary: Dictionary = _last_pipeline.get("primary", {})
	var supply: Variant = primary.get("supply", primary.get("supply_plan", {}))
	if _supply_expanded:
		var dialog := AcceptDialog.new(); dialog.title = "Supply Plan"
		var label := RichTextLabel.new(); label.custom_minimum_size = Vector2(520, 280); label.text = JSON.stringify(supply, "  "); label.fit_content = true
		dialog.add_child(label); add_child(dialog); dialog.confirmed.connect(func(): dialog.queue_free()); dialog.popup_centered()


func _edit_release_search() -> void:
	_release_search.text = _release_query
	var dialog := ConfirmationDialog.new(); dialog.title = "Search Levels"; dialog.add_child(_release_search)
	dialog.confirmed.connect(func(): _release_query = _release_search.text; _apply_release_projection(); dialog.remove_child(_release_search); dialog.queue_free())
	dialog.canceled.connect(func(): dialog.remove_child(_release_search); dialog.queue_free())
	add_child(dialog); dialog.popup_centered()


func _open_release_filters() -> void:
	_filter_difficulty.select(maxi(0, ["All Difficulties", "Easy", "Medium", "Hard"].find(_difficulty_filter)))
	_filter_columns.select(maxi(0, ["All Columns", "3 columns", "4 columns", "5 columns"].find(_columns_filter)))
	_release_filter_dialog.popup_centered()


func _apply_release_filters() -> void:
	_difficulty_filter = _filter_difficulty.get_item_text(_filter_difficulty.selected)
	_columns_filter = _filter_columns.get_item_text(_filter_columns.selected)
	_apply_release_projection()


func _apply_release_projection() -> void:
	_visible_release_ids.clear()
	for entry in _release_pool.get("entries", []):
		var candidate_id := str(entry.get("candidate_id", ""))
		var label := str(entry.get("level_id", entry.get("name", candidate_id))).to_lower()
		var pipeline: Dictionary = entry.get("pipeline", {})
		var primary: Dictionary = pipeline.get("primary", {})
		var difficulty := str(primary.get("difficulty_class", entry.get("difficulty_class", ""))).to_lower()
		var columns := str(primary.get("column_count", entry.get("column_count", "")))
		if not _release_query.is_empty() and not label.contains(_release_query.to_lower()) and not candidate_id.to_lower().contains(_release_query.to_lower()): continue
		if _difficulty_filter != "All Difficulties" and difficulty != _difficulty_filter.to_lower(): continue
		if _columns_filter != "All Columns" and columns != _columns_filter.get_slice(" ", 0): continue
		if not candidate_id.is_empty(): _visible_release_ids.append(candidate_id)


func _select_release_row(index: int) -> void:
	if index < 0 or index >= _visible_release_ids.size(): return
	var candidate_id := _visible_release_ids[index]
	if _release_selection_manage_mode:
		if _selected_release_ids.has(candidate_id):
			_selected_release_ids.erase(candidate_id)
		else:
			_selected_release_ids.append(candidate_id)
	_selected_release_id = candidate_id
	_select_release_entry(candidate_id)


func _manage_release_selection() -> void:
	_release_selection_manage_mode = not _release_selection_manage_mode
	_report("Manage selection %s" % ("active" if _release_selection_manage_mode else "closed"))


func _select_all_release() -> void:
	_selected_release_ids.clear()
	for candidate_id in _visible_release_ids:
		if candidate_id not in _selected_release_ids: _selected_release_ids.append(candidate_id)


func _clear_release_selection() -> void:
	_selected_release_ids.clear()


func _select_release_card(index: int) -> void:
	if index >= 0 and index < _selected_release_ids.size():
		_selected_release_id = _selected_release_ids[index]
		_select_release_entry(_selected_release_id)


func _select_release_entry(candidate_id: String) -> void:
	for entry in _release_pool.get("entries", []):
		if str(entry.get("candidate_id", "")) != candidate_id: continue
		var artwork := str(entry.get("files", {}).get("artwork", {}).get("path", ""))
		if not artwork.is_empty():
			_selected_art_path = artwork
			_load_selected_art_preview(artwork)
		_last_candidate_id = candidate_id
		return


func _remove_release_selection(index: int) -> void:
	if index >= 0 and index < _selected_release_ids.size(): _selected_release_ids.remove_at(index)


func _set_release_target(target: String) -> void:
	_release_target = target if target in ["STAGING", "PRODUCTION"] else "STAGING"
	if target == "PRODUCTION":
		_report("PRODUCTION requires a verified STAGING manifest and exact owner approval")


func _upload_selected() -> void:
	if _release_target == "STAGING":
		_publish_staging()
		return
	_report("PRODUCTION is unavailable: exact verified STAGING manifest and trusted owner-approval promotion handoff are not connected.")


func _preview_release_manifest() -> void:
	if _release_pool.get("publish_preflight", {}).is_empty():
		_preflight_release()
	var result: Dictionary = _release_pool.get("publish_preflight", {})
	var dialog := AcceptDialog.new(); dialog.title = "Release Manifest Preview"
	var label := RichTextLabel.new(); label.custom_minimum_size = Vector2(680, 380); label.text = JSON.stringify(result, "  "); label.fit_content = true
	dialog.add_child(label); add_child(dialog); dialog.confirmed.connect(func(): dialog.queue_free()); dialog.popup_centered()


func _extension(operation: String, request: Dictionary) -> Dictionary:
	if _gateway == null or not _gateway.has_method("run_studio_extension"):
		return {"state": "UNAVAILABLE", "reason": "Canonical Factory Core gateway is unavailable."}
	var result: Variant = _gateway.call("run_studio_extension", operation, request)
	return result if result is Dictionary else {"state": "ERROR", "reason": "Canonical operation returned no structured result."}
