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
var _batch_resume := false
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
var _pending_production_confirmation: Dictionary = {}
var _semantic_progress := {"completed": 0, "failed": 0, "remaining": 0}
var _master_buttons: Array[Button] = []
var _grid_lines: Array[Line2D] = []
var _preview_rect: TextureRect
var _selected_art_path := ""
var _seed := ""
var _background_intent := "TRANSPARENT"
const _REFERENCE_SIZE := Vector2(1536.0, 1024.0)
var _responsive_nodes: Array[CanvasItem] = []
var _responsive_base: Dictionary = {}
var _responsive_scale := 1.0
var _responsive_offset := Vector2.ZERO
var _last_import_summary: Dictionary = {}
var _file_selection_action := "PNG_IMPORT"


func _ready() -> void:
	_canvas = get_node_or_null("MasterCanvas") as TextureRect
	_status = get_node_or_null("Status") as Label
	_file_dialog = get_node_or_null("FileDialog") as FileDialog
	if _canvas == null or _file_dialog == null:
		return
	_file_dialog.file_selected.connect(_on_file_selected)
	_file_dialog.files_selected.connect(_on_files_selected)
	_build_live_chrome()
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
	_build_master_controls()
	_show_screen(_screen)
	_capture_responsive_layout()
	resized.connect(_apply_responsive_layout)
	_apply_responsive_layout()


func _capture_responsive_layout() -> void:
	_responsive_nodes.clear()
	_responsive_base.clear()
	for child in get_children():
		if child is Control:
			var control := child as Control
			if control == _canvas or control.anchor_left != 0.0 or control.anchor_top != 0.0 or control.anchor_right != 0.0 or control.anchor_bottom != 0.0:
				continue
			_responsive_nodes.append(control)
			_responsive_base[control.get_instance_id()] = {"position": control.position, "size": control.size, "scale": control.scale}
		elif child is Line2D:
			var line := child as Line2D
			_responsive_nodes.append(line)
			_responsive_base[line.get_instance_id()] = {"position": line.position, "scale": line.scale}


func _apply_responsive_layout() -> void:
	if _responsive_nodes.is_empty() or size.x <= 0.0 or size.y <= 0.0:
		return
	var geometry := responsive_geometry(size)
	_responsive_scale = float(geometry.get("scale", 1.0))
	_responsive_offset = geometry.get("offset", Vector2.ZERO)
	for node in _responsive_nodes:
		if not is_instance_valid(node):
			continue
		var base: Dictionary = _responsive_base.get(node.get_instance_id(), {})
		if base.is_empty():
			continue
		if node is Control:
			var control := node as Control
			control.position = _responsive_offset + base.position * _responsive_scale
			if control == _preview_rect:
				control.size = base.size * _responsive_scale
				control.scale = Vector2.ONE * (_zoom / 8.0) * _responsive_scale
			else:
				control.size = base.size
				control.scale = base.scale * _responsive_scale
		elif node is Line2D:
			var line := node as Line2D
			line.position = _responsive_offset + base.position * _responsive_scale
			line.scale = base.scale * _responsive_scale


func responsive_layout_snapshot() -> Dictionary:
	return {"reference_size": _REFERENCE_SIZE, "viewport_size": size, "scale": _responsive_scale, "offset": _responsive_offset}


func responsive_geometry(viewport_size: Vector2) -> Dictionary:
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return {"scale": 1.0, "offset": Vector2.ZERO, "content_size": _REFERENCE_SIZE}
	var scale_factor := minf(viewport_size.x / _REFERENCE_SIZE.x, viewport_size.y / _REFERENCE_SIZE.y)
	var content_size := _REFERENCE_SIZE * scale_factor
	return {"scale": scale_factor, "offset": (viewport_size - content_size) * 0.5, "content_size": content_size}


func last_import_snapshot() -> Dictionary:
	return _last_import_summary.duplicate(true)


func configure_gateway(gateway: RefCounted) -> void:
	_gateway = gateway


func active_master() -> String:
	return _screen


func master_names() -> Array[String]:
	return ["PIXEL ART", "LEVEL FACTORY", "RELEASE POOL"]


func _control_style(fill: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(7)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 4
	style.content_margin_bottom = 4
	return style


func _control_caption(control_name: String) -> String:
	var captions := {
		"PixelArtTab": "PIXEL ART", "LevelFactoryTab": "LEVEL FACTORY", "ReleasePoolTab": "RELEASE POOL",
		"SettingsGear": "Settings", "NativeMinimize": "−", "NativeMaximize": "□", "NativeClose": "×",
		"GeneratePixelArt": "Generate", "BatchCsvSelect": "Select CSV", "RunBatch": "Resume" if _batch_resume else "Run Batch",
		"Regenerate": "Regenerate", "EditPrompt": "Edit Prompt", "AddToLevelFactory": "Use in Level Factory",
		"GenerationPrompt": "Prompt", "RandomSeed": "↻", "GenerationStyle": "Style: %s" % _generation_style,
		"GenerationSize": "Size: %d × %d" % [_width, _height], "GenerationProvider": "Provider: %s" % _provider_model,
		"SingleMode": "Single", "BatchMode": "Batch", "BatchCsvPath": "CSV file…",
		"ArtworkVariation1": "Variation 1", "ArtworkVariation2": "Variation 2", "ArtworkVariation3": "Variation 3",
		"RemoveSelected1": "×", "RemoveSelected2": "×", "RemoveSelected3": "×",
		"ArtworkCarouselLeft": "‹", "ArtworkCarouselRight": "›", "ZoomOut": "−", "ZoomIn": "+",
		"ZoomOneToOne": "1:1", "ZoomFit": "Fit", "ToggleGrid": "Grid", "SelectArtwork": "Select PNG",
		"LevelNumber": "Level: Auto", "SupplyColumns3": "3", "SupplyColumns4": "4", "SupplyColumns5": "5",
		"MaxRobotsAuto": "Max Robots: Auto", "BackgroundIntent": "Background: %s" % _background_intent,
		"RunLevelPipeline": "Run Pipeline", "SolveAgain": "Solve Again", "PreviewReplay": "Preview Replay",
		"ExpandSupplyPlan": "Supply Plan", "AcceptLevel": "Accept", "RejectLevel": "Reject",
		"RefreshReleasePool": "Refresh", "SelectReleaseLevel": "Select level", "ReleaseSearch": "Search levels",
		"DifficultyFilter": "Difficulty", "ColumnsFilter": "Columns", "ManageSelection": "Manage Selection",
		"SelectAllRelease": "Select All", "ClearRelease": "Clear", "ReleaseStaging": "STAGING",
		"ReleaseProduction": "PRODUCTION", "PreflightRelease": "Preflight", "ValidateReleaseAssets": "Validate Assets",
		"BuildReleasePack": "Build Scrubpack", "UploadR2Status": "Upload Status",
		"UploadSelected": "Upload Selected", "PreviewReleaseManifest": "Preview Manifest",
		"AddMoreLevels": "Add More Levels"
	}
	return str(captions.get(control_name, control_name.replace("_", " ")))


func _build_live_chrome() -> void:
	_canvas.texture = null
	_canvas.visible = false
	for spec in [
		["RuntimeBackground", Rect2(0, 0, 1536, 1024), "#0b1220"],
		["RuntimeHeader", Rect2(0, 0, 1536, 100), "#101b2d"],
		["RuntimeLeftPanel", Rect2(18, 116, 354, 814), "#111d30"],
		["RuntimeCanvasPanel", Rect2(389, 116, 804, 696), "#111d30"],
		["RuntimeDetailsPanel", Rect2(1205, 116, 313, 814), "#111d30"],
		["RuntimeBottomStrip", Rect2(389, 824, 804, 106), "#111d30"]
	]:
		var panel := Panel.new()
		panel.name = spec[0]
		panel.position = spec[1].position
		panel.size = spec[1].size
		panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
		panel.add_theme_stylebox_override("panel", _control_style(Color(spec[2]), Color("#253550")))
		add_child(panel)
	var header := Label.new()
	header.name = "RuntimeTitle"
	header.position = Vector2(28, 25)
	header.size = Vector2(320, 48)
	header.text = "SCRUBBOTS  /  FACTORY STUDIO"
	header.add_theme_font_size_override("font_size", 20)
	header.add_theme_color_override("font_color", Color("#f2f6fc"))
	add_child(header)
	for item in [["RuntimeLeftHeading", Vector2(34, 126), Vector2(320, 32), "WORKSPACE"], ["RuntimeCanvasHeading", Vector2(405, 126), Vector2(560, 32), "VISUAL REVIEW CANVAS"], ["RuntimeDetailsHeading", Vector2(1222, 126), Vector2(270, 32), "DETAILS"], ["RuntimeBottomHeading", Vector2(405, 833), Vector2(560, 28), "VARIATIONS  /  RECENT ITEMS"]]:
		var label := Label.new()
		label.name = item[0]
		label.position = item[1]
		label.size = item[2]
		label.text = item[3]
		label.add_theme_font_size_override("font_size", 12)
		label.add_theme_color_override("font_color", Color("#91a7c5"))
		add_child(label)
	var live := Label.new()
	live.name = "RuntimeLiveData"
	live.position = Vector2(1222, 170)
	live.size = Vector2(270, 112)
	live.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	live.add_theme_font_size_override("font_size", 13)
	live.add_theme_color_override("font_color", Color("#dce8f8"))
	add_child(live)
	_refresh_live_data()


func _update_live_chrome() -> void:
	for node_name in ["RuntimeLeftPanel", "RuntimeCanvasPanel", "RuntimeDetailsPanel", "RuntimeBottomStrip"]:
		var panel := get_node_or_null(node_name) as Control
		if panel != null: panel.visible = true
	var title := get_node_or_null("RuntimeTitle") as Label
	if title != null: title.text = "SCRUBBOTS  /  " + _screen
	var preview_position := Vector2(430, 172)
	var preview_size := Vector2(720, 590)
	if _preview_rect != null:
		_preview_rect.position = preview_position
		_preview_rect.size = preview_size
	_refresh_live_data()
	_apply_responsive_layout()


func _refresh_live_data() -> void:
	var live := get_node_or_null("RuntimeLiveData") as Label
	if live == null: return
	if _screen == "PIXEL ART":
		live.text = "Provider: %s\nMode: %s\nCanvas: %d × %d\nSeed: %s\nBatch: %d complete · %d failed · %d remaining" % [_provider_model, _generation_mode, _width, _height, _seed if not _seed.is_empty() else "Auto", _semantic_progress.completed, _semantic_progress.failed, _semantic_progress.remaining]
	elif _screen == "LEVEL FACTORY":
		var primary: Dictionary = _last_pipeline.get("primary", {})
		live.text = "Level: %s\nColumns: %d\nBackground: %s\nSolver: %s\nReplay: %s\nDifficulty V1: %s\nSupply: %s" % ["Auto" if not _manual_level_override else str(_level_number), _column_count, _background_intent, str(primary.get("state", "Awaiting pipeline")), str(primary.get("acceptance", {}).get("replay", "—")), str(primary.get("difficulty", {}).get("class", "—")), "Ready" if not primary.is_empty() else "Awaiting pipeline"]
	else:
		var entries: Array = _release_pool.get("entries", [])
		live.text = "READY levels: %d\nVisible: %d\nSelected: %d\nTarget: %s\nPreflight: %s" % [entries.size(), _visible_release_ids.size(), _selected_release_ids.size(), _release_target, str(_release_pool.get("publish_preflight", {}).get("state", "Not run"))]
	_refresh_runtime_cards()


func _set_runtime_button(button_name: String, caption: String, image_path: String = "") -> void:
	var button := get_node_or_null(button_name) as Button
	if button == null: return
	button.text = caption
	button.icon = _runtime_png_texture(image_path) if not image_path.is_empty() else null
	button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
	button.expand_icon = not image_path.is_empty()


func _runtime_png_texture(path: String) -> Texture2D:
	var resolved := path
	if not resolved.is_absolute_path():
		resolved = ProjectSettings.globalize_path("res://").path_join("..").simplify_path().path_join(path)
	if not FileAccess.file_exists(resolved): return null
	var image := Image.load_from_file(resolved)
	if image == null or image.is_empty(): return null
	return ImageTexture.create_from_image(image)


func _refresh_runtime_cards() -> void:
	var inbox := _extension("candidate-inbox", {})
	var candidates: Array = inbox.get("candidates", [])
	var pixel_slots := ["ArtworkVariation1", "ArtworkVariation2", "ArtworkVariation3"]
	var level_slots := ["LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5", "LevelVariation6", "LevelVariation7", "LevelVariation8"]
	for index in range(pixel_slots.size()):
		if index < candidates.size():
			var candidate: Dictionary = candidates[index]
			var caption := str(candidate.get("candidate_id", "Artwork %d" % (index + 1)))
			var image_path := str(candidate.get("artwork_path", ""))
			_set_runtime_button(pixel_slots[index], caption.left(18), image_path)
		else:
			_set_runtime_button(pixel_slots[index], "No artwork", "")
	for index in range(level_slots.size()):
		if index < candidates.size():
			var candidate: Dictionary = candidates[index]
			_set_runtime_button(level_slots[index], str(candidate.get("candidate_id", "Level %d" % (index + 1))).left(12), str(candidate.get("artwork_path", "")))
		else:
			_set_runtime_button(level_slots[index], "—", "")
	var release_slots := ["SelectReleaseLevel", "ReleaseRow2", "ReleaseRow3", "ReleaseRow4", "ReleaseRow5", "ReleaseRow6", "ReleaseRow7", "ReleaseRow8"]
	var entries: Array = _release_pool.get("entries", [])
	for index in range(release_slots.size()):
		if index < _visible_release_ids.size():
			var candidate_id := _visible_release_ids[index]
			var entry: Dictionary = {}
			for value in entries:
				if str(value.get("candidate_id", "")) == candidate_id:
					entry = value
					break
			var title := str(entry.get("level_id", entry.get("name", candidate_id)))
			var artwork := str(entry.get("files", {}).get("artwork", {}).get("path", entry.get("artwork_path", "")))
			_set_runtime_button(release_slots[index], title.left(25), artwork)
		else:
			_set_runtime_button(release_slots[index], "No READY level", "")
	for index in range(3):
		var card := "SelectedReleaseCard%d" % (index + 1)
		if index < _selected_release_ids.size():
			var candidate_id := _selected_release_ids[index]
			var title := candidate_id
			var artwork := ""
			for entry in entries:
				if str(entry.get("candidate_id", "")) == candidate_id:
					title = str(entry.get("level_id", entry.get("name", candidate_id)))
					artwork = str(entry.get("files", {}).get("artwork", {}).get("path", entry.get("artwork_path", "")))
					break
			_set_runtime_button(card, title.left(20), artwork)
		else:
			_set_runtime_button(card, "Empty selection", "")


func _build_master_controls() -> void:
	# Header tabs are explicit, visible Godot Button controls.
	_place_control("PixelArtTab", Rect2(365, 22, 255, 72), _show_screen.bind("PIXEL ART"))
	_place_control("LevelFactoryTab", Rect2(633, 22, 270, 72), _show_screen.bind("LEVEL FACTORY"))
	_place_control("ReleasePoolTab", Rect2(918, 22, 270, 72), _show_screen.bind("RELEASE POOL"))
	_place_control("SettingsGear", Rect2(1320, 15, 55, 60), _open_settings)
	_place_control("NativeMinimize", Rect2(1376, 14, 44, 42), _minimize_window)
	_place_control("NativeMaximize", Rect2(1428, 14, 44, 42), _toggle_window_mode)
	_place_control("NativeClose", Rect2(1477, 14, 48, 42), _close_window)
	# PIXEL ART actions and Batch-CSV path.
	_place_control("GeneratePixelArt", Rect2(27, 558, 334, 49), _generate_art)
	_place_control("BatchCsvSelect", Rect2(199, 155, 161, 43), _open_batch_csv)
	_place_control("RunBatch", Rect2(27, 610, 334, 50), _run_batch)
	_place_control("Regenerate", Rect2(1208, 452, 294, 48), _generate_art)
	_place_control("EditPrompt", Rect2(1208, 506, 294, 48), _edit_prompt)
	_place_control("AddToLevelFactory", Rect2(1208, 560, 294, 48), _send_to_level_factory)
	_place_control("GenerationPrompt", Rect2(26, 208, 334, 92), _edit_prompt)
	_place_control("RandomSeed", Rect2(315, 296, 42, 40), _new_seed)
	_place_control("GenerationStyle", Rect2(27, 348, 334, 42), _choose_style)
	_place_control("GenerationSize", Rect2(27, 397, 334, 42), _choose_size)
	_place_control("GenerationProvider", Rect2(27, 446, 334, 42), _choose_provider)
	_place_control("SingleMode", Rect2(27, 151, 160, 45), _set_generation_mode.bind("SINGLE"))
	_place_control("BatchMode", Rect2(198, 151, 162, 45), _set_generation_mode.bind("BATCH"))
	_place_control("BatchCsvPath", Rect2(27, 558, 334, 42), _open_batch_csv)
	_place_control("ArtworkVariation1", Rect2(1208, 300, 92, 108), _select_artwork.bind(0))
	_place_control("ArtworkVariation2", Rect2(1310, 300, 92, 108), _select_artwork.bind(1))
	_place_control("ArtworkVariation3", Rect2(1412, 300, 92, 108), _select_artwork.bind(2))
	_place_control("ArtworkCarouselLeft", Rect2(1208, 840, 50, 62), _page_artwork.bind(-1))
	_place_control("ArtworkCarouselRight", Rect2(1452, 840, 50, 62), _page_artwork.bind(1))
	# Shared canvas presentation controls are UI-only and never mutate source bytes.
	_place_control("ZoomOut", Rect2(650, 124, 34, 34), _adjust_zoom.bind(-1.0))
	_place_control("ZoomSlider", Rect2(735, 123, 136, 32), _set_zoom_from_pointer)
	_place_control("ZoomIn", Rect2(875, 124, 34, 34), _adjust_zoom.bind(1.0))
	_place_control("ZoomOneToOne", Rect2(910, 124, 50, 32), _set_zoom.bind(1.0))
	_place_control("ZoomFit", Rect2(960, 124, 50, 32), _fit_canvas)
	_place_control("ToggleGrid", Rect2(1010, 124, 45, 32), _toggle_grid)
	# LEVEL FACTORY: select artwork, set 3/4/5 columns, run real pipeline,
	# then record append-only owner acceptance or rejection for its candidate.
	_place_control("SelectArtwork", Rect2(42, 165, 95, 100), _open_files.bind(true))
	_place_control("LevelNumber", Rect2(172, 346, 190, 38), _edit_level_number)
	_place_control("SupplyColumns3", Rect2(172, 392, 56, 40), _set_columns.bind(3))
	_place_control("SupplyColumns4", Rect2(238, 392, 56, 40), _set_columns.bind(4))
	_place_control("SupplyColumns5", Rect2(304, 392, 56, 40), _set_columns.bind(5))
	_place_control("MaxRobotsAuto", Rect2(172, 440, 190, 38), _keep_auto_robot_cap)
	_place_control("BackgroundIntent", Rect2(172, 487, 190, 38), _toggle_background)
	_place_control("RunLevelPipeline", Rect2(26, 803, 335, 52), _run_level_pipeline)
	_place_control("SolveAgain", Rect2(1207, 625, 291, 50), _solve_again)
	_place_control("PreviewReplay", Rect2(1368, 390, 130, 38), _preview_replay)
	_place_control("ExpandSupplyPlan", Rect2(1207, 485, 291, 42), _toggle_supply_plan)
	_place_control("LevelVariation1", Rect2(405, 864, 88, 58), _select_variation.bind(0))
	_place_control("LevelVariation2", Rect2(501, 864, 88, 58), _select_variation.bind(1))
	_place_control("LevelVariation3", Rect2(597, 864, 88, 58), _select_variation.bind(2))
	_place_control("LevelVariation4", Rect2(693, 864, 88, 58), _select_variation.bind(3))
	_place_control("LevelVariation5", Rect2(789, 864, 88, 58), _select_variation.bind(4))
	_place_control("LevelVariation6", Rect2(885, 864, 88, 58), _select_variation.bind(5))
	_place_control("LevelVariation7", Rect2(981, 864, 88, 58), _select_variation.bind(6))
	_place_control("LevelVariation8", Rect2(1077, 864, 88, 58), _select_variation.bind(7))
	_place_control("AcceptLevel", Rect2(1207, 686, 138, 50), _review_candidate.bind("ACCEPT"))
	_place_control("RejectLevel", Rect2(1360, 686, 138, 50), _review_candidate.bind("REJECT"))
	# RELEASE POOL uses canonical pool, campaign, and staging operations.
	_place_control("RefreshReleasePool", Rect2(27, 202, 330, 40), _refresh_release_pool)
	_place_control("SelectReleaseLevel", Rect2(25, 292, 335, 55), _select_first_release)
	_place_control("ReleaseSearch", Rect2(25, 154, 335, 44), _edit_release_search)
	_place_control("DifficultyFilter", Rect2(25, 249, 165, 38), _open_release_filters)
	_place_control("ColumnsFilter", Rect2(196, 249, 164, 38), _open_release_filters)
	_place_control("ReleaseRow2", Rect2(25, 353, 335, 55), _select_release_row.bind(1))
	_place_control("ReleaseRow3", Rect2(25, 414, 335, 55), _select_release_row.bind(2))
	_place_control("ReleaseRow4", Rect2(25, 475, 335, 55), _select_release_row.bind(3))
	_place_control("ReleaseRow5", Rect2(25, 536, 335, 55), _select_release_row.bind(4))
	_place_control("ReleaseRow6", Rect2(25, 597, 335, 55), _select_release_row.bind(5))
	_place_control("ReleaseRow7", Rect2(25, 658, 335, 55), _select_release_row.bind(6))
	_place_control("ReleaseRow8", Rect2(25, 719, 335, 55), _select_release_row.bind(7))
	_place_control("ManageSelection", Rect2(25, 784, 335, 42), _manage_release_selection)
	_place_control("SelectAllRelease", Rect2(25, 837, 164, 42), _select_all_release)
	_place_control("ClearRelease", Rect2(198, 837, 162, 42), _clear_release_selection)
	_place_control("SelectedReleaseCard1", Rect2(405, 888, 190, 35), _select_release_card.bind(0))
	_place_control("SelectedReleaseCard2", Rect2(611, 888, 190, 35), _select_release_card.bind(1))
	_place_control("SelectedReleaseCard3", Rect2(817, 888, 190, 35), _select_release_card.bind(2))
	_place_control("RemoveSelected1", Rect2(568, 862, 26, 24), _remove_release_selection.bind(0))
	_place_control("RemoveSelected2", Rect2(774, 862, 26, 24), _remove_release_selection.bind(1))
	_place_control("RemoveSelected3", Rect2(980, 862, 26, 24), _remove_release_selection.bind(2))
	_place_control("AddMoreLevels", Rect2(1023, 888, 170, 35), _show_screen.bind("RELEASE POOL"))
	_place_control("ReleaseStaging", Rect2(1215, 398, 280, 36), _set_release_target.bind("STAGING"))
	_place_control("ReleaseProduction", Rect2(1215, 438, 280, 36), _set_release_target.bind("PRODUCTION"))
	_place_control("PreflightRelease", Rect2(1207, 485, 291, 40), _preflight_release)
	_place_control("ValidateReleaseAssets", Rect2(1207, 530, 291, 36), _show_publish_stage.bind("VALIDATE_ASSETS"))
	_place_control("BuildReleasePack", Rect2(1207, 568, 291, 36), _show_publish_stage.bind("BUILD_SCRUBPACK"))
	_place_control("UploadR2Status", Rect2(1207, 606, 291, 36), _show_publish_stage.bind("UPLOAD_R2"))
	_place_control("UploadSelected", Rect2(1207, 648, 291, 54), _upload_selected)
	_place_control("PreviewReleaseManifest", Rect2(1207, 713, 291, 50), _preview_release_manifest)
	_update_master_control_visibility()


func _place_control(node_name: String, rect: Rect2, action: Callable) -> Button:
	var button := Button.new()
	button.name = node_name
	button.position = rect.position
	button.size = rect.size
	button.flat = false
	button.focus_mode = Control.FOCUS_ALL
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.text = _control_caption(node_name)
	button.add_theme_font_size_override("font_size", 13)
	button.add_theme_color_override("font_color", Color("#dce8f8"))
	button.add_theme_color_override("font_hover_color", Color.WHITE)
	button.add_theme_stylebox_override("normal", _control_style(Color("#17243a"), Color("#30415e")))
	button.add_theme_stylebox_override("hover", _control_style(Color("#233651"), Color("#6b8bb9")))
	button.add_theme_stylebox_override("pressed", _control_style(Color("#2d4668"), Color("#8eb7ec")))
	button.add_theme_stylebox_override("focus", _control_style(Color("#233651"), Color("#8eb7ec")))
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
	_release_confirmation.confirmed.connect(_publish_production_confirmed)
	add_child(_release_confirmation)
	_release_search = LineEdit.new()
	_release_search.text_changed.connect(func(value):
		_release_query = value
		_apply_release_projection()
	)
	add_child(_release_search)
	_release_search.visible = false


func _show_screen(name: String) -> void:
	if name not in master_names() or _canvas == null:
		return
	_screen = name
	# Owner masters are reference-only. Runtime rendering is built from live Controls.
	_canvas.texture = null
	_canvas.visible = false
	_update_live_chrome()
	_update_master_control_visibility()
	if _status != null:
		_status.visible = false
	if name == "RELEASE POOL":
		_refresh_release_pool(false)
		_apply_release_projection()
	elif not _selected_art_path.is_empty():
		_load_selected_art_preview(_selected_art_path)
	_refresh_live_data()


func _update_master_control_visibility() -> void:
	for button in _master_buttons:
		button.text = _control_caption(button.name)
	var shared := ["PixelArtTab", "LevelFactoryTab", "ReleasePoolTab", "SettingsGear", "NativeMinimize", "NativeMaximize", "NativeClose", "ZoomOut", "ZoomSlider", "ZoomIn", "ZoomOneToOne", "ZoomFit", "ToggleGrid"]
	var pixel := ["GeneratePixelArt", "BatchCsvSelect", "RunBatch", "Regenerate", "EditPrompt", "AddToLevelFactory", "GenerationPrompt", "RandomSeed", "GenerationStyle", "GenerationSize", "GenerationProvider", "SingleMode", "BatchMode", "BatchCsvPath", "ArtworkVariation1", "ArtworkVariation2", "ArtworkVariation3", "ArtworkCarouselLeft", "ArtworkCarouselRight"]
	var level := ["SelectArtwork", "LevelNumber", "SupplyColumns3", "SupplyColumns4", "SupplyColumns5", "MaxRobotsAuto", "BackgroundIntent", "RunLevelPipeline", "SolveAgain", "PreviewReplay", "ExpandSupplyPlan", "AcceptLevel", "RejectLevel", "LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5", "LevelVariation6", "LevelVariation7", "LevelVariation8"]
	var release := ["RefreshReleasePool", "SelectReleaseLevel", "ReleaseSearch", "DifficultyFilter", "ColumnsFilter", "ReleaseRow2", "ReleaseRow3", "ReleaseRow4", "ReleaseRow5", "ReleaseRow6", "ReleaseRow7", "ReleaseRow8", "ManageSelection", "SelectAllRelease", "ClearRelease", "SelectedReleaseCard1", "SelectedReleaseCard2", "SelectedReleaseCard3", "RemoveSelected1", "RemoveSelected2", "RemoveSelected3", "AddMoreLevels", "ReleaseStaging", "ReleaseProduction", "PreflightRelease", "ValidateReleaseAssets", "BuildReleasePack", "UploadR2Status", "UploadSelected", "PreviewReleaseManifest", "NativeMinimize", "NativeMaximize", "NativeClose"]
	for button in _master_buttons:
		button.visible = button.name in shared or (_screen == "PIXEL ART" and button.name in pixel) or (_screen == "LEVEL FACTORY" and button.name in level) or (_screen == "RELEASE POOL" and button.name in release)
	if _screen == "PIXEL ART":
		var generate := get_node_or_null("GeneratePixelArt") as Button
		var batch_path := get_node_or_null("BatchCsvPath") as Button
		var run_batch := get_node_or_null("RunBatch") as Button
		var batch_select := get_node_or_null("BatchCsvSelect") as Button
		if generate != null: generate.visible = _generation_mode == "SINGLE"
		if batch_path != null: batch_path.visible = _generation_mode == "BATCH"
		if run_batch != null: run_batch.visible = _generation_mode == "BATCH"
		if batch_select != null: batch_select.visible = false


func _report(message: String) -> void:
	if _status == null:
		return
	_status.text = message
	_status.visible = true
	_refresh_live_data()
	get_tree().create_timer(4.0).timeout.connect(func():
		if _status != null and _status.text == message:
			_status.visible = false
	)


func _open_files(multiple: bool) -> void:
	if _file_dialog == null:
		return
	_file_selection_action = "PNG_IMPORT"
	_file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILES if multiple else FileDialog.FILE_MODE_OPEN_FILE
	_file_dialog.title = "Select artwork PNG"
	_file_dialog.clear_filters()
	_file_dialog.add_filter("*.png ; PNG image")
	_file_dialog.popup_centered_ratio(0.72)


func _open_batch_csv() -> void:
	if _file_dialog == null:
		return
	_file_selection_action = "PIXEL_ART_BATCH"
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
	if _file_selection_action == "PIXEL_ART_BATCH":
		_generate_batch_csv(path)
		return
	_import_pngs([path])

func _on_files_selected(paths: PackedStringArray) -> void:
	_import_pngs(Array(paths))


func _import_pngs(paths: Array) -> void:
	_last_source_id = ""
	_last_candidate_id = ""
	_last_pipeline.clear()
	_selected_art_path = ""
	if _preview_rect != null:
		_preview_rect.texture = null
		_preview_rect.visible = false
	var result := _extension("batch-import", {"paths": paths})
	var items: Array = result.get("items", [])
	var lines: Array[String] = []
	var imported_count := 0
	var reused_count := 0
	var rejected_count := 0
	var preview_path := ""
	var preview_source_id := ""
	for index in range(paths.size()):
		var path := str(paths[index])
		var item: Dictionary = items[index] if index < items.size() and items[index] is Dictionary else {}
		var source_id := str(item.get("source_id", ""))
		var state := str(item.get("disposition", item.get("state", "")))
		if not source_id.is_empty() and state in ["IMPORTED", "ALREADY_IMPORTED"]:
			if state == "ALREADY_IMPORTED":
				reused_count += 1
			else:
				imported_count += 1
			if preview_path.is_empty():
				preview_path = path
				preview_source_id = source_id
			var detail := "%s · %s" % ["ALREADY_IMPORTED" if state == "ALREADY_IMPORTED" else "IMPORTED", source_id]
			lines.append("%s\n%s" % [path.get_file(), detail])
		else:
			rejected_count += 1
			var reason := str(item.get("error", item.get("reason", state if not state.is_empty() else result.get("reason", "Canonical import returned no source identity."))))
			lines.append("%s\nREJECTED · %s" % [path.get_file(), reason])
	_last_import_summary = {
		"selected_count": paths.size(), "imported_count": imported_count, "reused_count": reused_count,
		"rejected_count": rejected_count, "batch_id": str(result.get("batch_id", "")),
		"preview_source_id": preview_source_id, "preview_path": preview_path,
		"solver_calls": 0, "items": lines.duplicate()
	}
	if not preview_path.is_empty():
		_selected_art_path = preview_path
		_last_source_id = preview_source_id
		_load_selected_art_preview(preview_path)
	var summary := "PNG selection: %d selected · %d imported · %d reused · %d rejected" % [paths.size(), imported_count, reused_count, rejected_count]
	if not preview_source_id.is_empty():
		summary += "\nSelected for Run Pipeline: " + preview_source_id
	_report(summary)
	if not paths.is_empty():
		_show_import_results(paths.size(), lines)


func _show_import_results(selected_count: int, lines: Array[String]) -> void:
	var dialog := AcceptDialog.new()
	dialog.title = "PNG import · %d selected" % selected_count
	var detail := Label.new()
	detail.custom_minimum_size = Vector2(640, minf(520.0, 56.0 + float(lines.size()) * 44.0))
	detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var visible_lines := lines.slice(0, 24)
	if lines.size() > visible_lines.size():
		visible_lines.append("… %d additional file statuses are available in the batch record." % (lines.size() - visible_lines.size()))
	detail.text = "\n\n".join(visible_lines)
	dialog.add_child(detail)
	add_child(dialog)
	dialog.confirmed.connect(dialog.queue_free)
	dialog.popup_centered()


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
	_update_master_control_visibility()
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
	_batch_resume = resume
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
	var colors: Dictionary = {}
	for y in range(image.get_height()):
		for x in range(image.get_width()):
			var pixel := image.get_pixel(x, y)
			if pixel.a < 1.0: transparent += 1
			colors[pixel.to_rgba32()] = true
	_report("%d × %d · %d colors · %d transparent · PNG" % [image.get_width(), image.get_height(), colors.size(), transparent])


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
	_preview_rect.scale = Vector2.ONE * (_zoom / 8.0) * _responsive_scale


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
		vertical.add_point(Vector2(495 + index * (590.0 / 32.0), 172)); vertical.add_point(Vector2(495 + index * (590.0 / 32.0), 762))
		var horizontal := Line2D.new(); horizontal.name = "GridHorizontal%02d" % index
		horizontal.add_point(Vector2(495, 172 + index * (590.0 / 32.0))); horizontal.add_point(Vector2(1085, 172 + index * (590.0 / 32.0)))
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
	_refresh_live_data()


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
	if _selected_release_ids.is_empty():
		_report("Select one or more READY levels before uploading.")
		return
	if _release_target == "STAGING":
		_publish_staging()
		return
	var preflight: Dictionary = _release_pool.get("publish_preflight", {})
	var reviewed: Dictionary = preflight.get("reviewed_identity", {})
	var manifest_sha := str(reviewed.get("candidate_manifest_sha256", ""))
	var version := int(reviewed.get("content_version", 0))
	if preflight.get("state") != "PREFLIGHT_READY" or manifest_sha.length() != 64 or version < 2:
		_report("Run a current publish preflight before requesting PRODUCTION confirmation.")
		return
	_pending_production_confirmation = {"manifest_sha256": manifest_sha, "content_version": version}
	_release_confirmation.dialog_text = "Promote this exact reviewed release?\n\nManifest SHA-256: %s\nContent version: %d\nTarget: PRODUCTION\n\nThe canonical publisher will verify STAGING bytes and current-main replay before promotion." % [manifest_sha, version]
	_release_confirmation.popup_centered()


func _publish_production_confirmed() -> void:
	if _pending_production_confirmation.is_empty(): return
	var reviewed: Dictionary = _release_pool.get("publish_preflight", {}).get("reviewed_identity", {})
	var approval_id := "factory-studio-owner-confirm-%d-%d" % [OS.get_process_id(), Time.get_ticks_usec()]
	var owner_id := OS.get_environment("USERNAME").strip_edges()
	if owner_id.is_empty(): owner_id = OS.get_environment("USER").strip_edges()
	if owner_id.is_empty():
		_report("Production approval cannot be attributed to the current local owner session.")
		_pending_production_confirmation.clear()
		return
	var confirmation := {"confirmed": true, "approval_id": approval_id, "owner_id": owner_id,
		"manifest_sha256": _pending_production_confirmation.get("manifest_sha256", ""),
		"content_version": _pending_production_confirmation.get("content_version", 0), "target": "PRODUCTION"}
	if confirmation.manifest_sha256 != reviewed.get("candidate_manifest_sha256") or confirmation.content_version != reviewed.get("content_version"):
		_report("Reviewed production identity changed. Run preflight again.")
		_pending_production_confirmation.clear()
		return
	var result := _extension("scrubbots-publish", {"action": "publish-production",
		"candidate_ids": _selected_release_ids, "pack_id": "factory-studio-release",
		"content_version": int(reviewed.get("content_version", 0)),
		"created_at_utc": str(reviewed.get("created_at_utc", "")),
		"reviewed_identity": reviewed, "owner_confirmation": confirmation})
	_pending_production_confirmation.clear()
	_report("PRODUCTION: %s · %s" % [str(result.get("state", "UNAVAILABLE")), str(result.get("production", ""))])


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
