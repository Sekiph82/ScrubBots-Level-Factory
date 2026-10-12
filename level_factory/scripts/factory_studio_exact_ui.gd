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
var _zoom := 1.0
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
var _preview_host: Control
var _preview_content: Control
var _preview_rect: TextureRect
var _selected_art_path := ""
var _active_preview_path := ""
var _preview_paths_by_screen := {"PIXEL ART": "", "LEVEL FACTORY": "", "RELEASE POOL": ""}
var _imported_sources: Array[Dictionary] = []
var _rejected_imports: Array[Dictionary] = []
var _imported_page := 0
var _selected_import_source_id := ""
var _seed := ""
var _background_intent := "TRANSPARENT"
const _REFERENCE_SIZE := Vector2(1536.0, 1024.0)
var _responsive_nodes: Array[CanvasItem] = []
var _responsive_base: Dictionary = {}
var _responsive_scale := 1.0
var _responsive_offset := Vector2.ZERO
var _last_import_summary: Dictionary = {}
var _file_selection_action := "PNG_IMPORT"
var _activity_panel: Panel
var _activity_title: Label
var _activity_state_chip: Panel
var _activity_state_label: Label
var _activity_source_label: Label
var _activity_phase_label: Label
var _activity_scroll: ScrollContainer
var _activity_rows: VBoxContainer
var _activity_events: Array[Dictionary] = []
var _pipeline_thread: Thread
var _pipeline_mutex := Mutex.new()
var _pipeline_worker_done := false
var _pipeline_worker_result: Dictionary = {}
var _activity_file_path := ""
var _activity_stream_reader_override: Object
var _activity_run_id := ""
var _activity_source_id := ""
var _activity_source_sha256 := ""
var _activity_source_filename := ""
var _activity_started_msec := 0
var _activity_finished_msec := 0
var _activity_seen_sequence := 0
var _activity_read_offset := 0
var _activity_pending_bytes := PackedByteArray()
var _activity_previous_sha256 := "0000000000000000000000000000000000000000000000000000000000000000"
var _activity_stage := "IDLE"
var _activity_message := "Select an imported PNG, then run the pipeline."
var _activity_terminal_state := ""
var _activity_backend_disposition := ""
var _activity_event_backend_disposition := ""
var _activity_integrity_error := ""


func _ready() -> void:
	_canvas = get_node_or_null("MasterCanvas") as TextureRect
	_status = get_node_or_null("Status") as Label
	_file_dialog = get_node_or_null("FileDialog") as FileDialog
	if _canvas == null or _file_dialog == null:
		return
	_file_dialog.file_selected.connect(_on_file_selected)
	_file_dialog.files_selected.connect(_on_files_selected)
	_build_live_chrome()
	_preview_host = Control.new()
	_preview_host.name = "VisualReviewClip"
	_preview_host.position = Vector2(401, 160)
	_preview_host.size = Vector2(780, 640)
	_preview_host.clip_contents = true
	_preview_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_preview_host)
	_preview_content = Control.new()
	_preview_content.name = "VisualReviewContent"
	_preview_content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_preview_content.pivot_offset = _preview_host.size * 0.5
	_preview_host.add_child(_preview_content)
	_preview_rect = TextureRect.new()
	_preview_rect.name = "SelectedArtworkPreview"
	_preview_rect.position = Vector2.ZERO
	_preview_rect.size = _preview_host.size
	_preview_rect.pivot_offset = _preview_rect.size * 0.5
	_preview_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_preview_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_preview_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_preview_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_preview_rect.visible = false
	_preview_content.add_child(_preview_rect)
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
	_level_number_label.position = Vector2(187, 172)
	_level_number_label.size = Vector2(150, 28)
	_level_number_label.add_theme_color_override("font_color", Color.WHITE)
	_level_number_label.add_theme_font_size_override("font_size", 16)
	_level_number_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_level_number_label.text = "Auto"
	_level_number_label.visible = true
	add_child(_level_number_label)
	_build_master_controls()
	_level_number_label.move_to_front()
	_show_screen(_screen)
	call_deferred("_restore_imported_sources")
	_capture_responsive_layout()
	resized.connect(_apply_responsive_layout)
	_apply_responsive_layout()


func _process(_delta: float) -> void:
	if not _activity_run_id.is_empty() and _activity_terminal_state.is_empty() and _operation_running:
		_poll_pipeline_activity()
		_refresh_activity_header()
	if _pipeline_thread == null:
		return
	_pipeline_mutex.lock()
	var completed := _pipeline_worker_done
	var result := _pipeline_worker_result.duplicate(true) if completed else {}
	_pipeline_mutex.unlock()
	if completed and not _pipeline_thread.is_alive():
		_pipeline_thread.wait_to_finish()
		_pipeline_thread = null
		_complete_level_pipeline(result)


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


func imported_queue_snapshot() -> Array[Dictionary]:
	return _imported_sources.duplicate(true)


func preview_state_snapshot() -> Dictionary:
	return {
		"active_screen": _screen,
		"active_path": _active_preview_path,
		"visible": _preview_rect != null and _preview_rect.visible,
		"host_rect": _preview_host.get_global_rect() if _preview_host != null else Rect2(),
		"host_clip_contents": _preview_host.clip_contents if _preview_host != null else false,
		"zoom": _zoom,
		"source_id": _last_source_id
	}


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
	live.size = Vector2(270, 198)
	live.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	live.add_theme_font_size_override("font_size", 13)
	live.add_theme_color_override("font_color", Color("#dce8f8"))
	add_child(live)
	_activity_panel = Panel.new()
	_activity_panel.name = "PipelineActivityPanel"
	_activity_panel.position = Vector2(27, 412)
	_activity_panel.size = Vector2(334, 498)
	_activity_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	_activity_panel.add_theme_stylebox_override("panel", _control_style(Color("#0e192a"), Color("#30415e")))
	_activity_panel.visible = false
	add_child(_activity_panel)
	_activity_title = Label.new()
	_activity_title.name = "PipelineActivityTitle"
	_activity_title.position = Vector2(12, 8)
	_activity_title.size = Vector2(205, 24)
	_activity_title.text = "PIPELINE ACTIVITY"
	_activity_title.add_theme_font_size_override("font_size", 12)
	_activity_title.add_theme_color_override("font_color", Color("#91a7c5"))
	_activity_panel.add_child(_activity_title)
	_activity_state_chip = Panel.new()
	_activity_state_chip.name = "PipelineActivityStateChip"
	_activity_state_chip.position = Vector2(232, 8)
	_activity_state_chip.size = Vector2(88, 22)
	_activity_state_chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_activity_panel.add_child(_activity_state_chip)
	_activity_state_label = Label.new()
	_activity_state_label.name = "PipelineActivityState"
	_activity_state_label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_activity_state_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_activity_state_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_activity_state_label.add_theme_font_size_override("font_size", 10)
	_activity_state_chip.add_child(_activity_state_label)
	_activity_source_label = Label.new()
	_activity_source_label.name = "PipelineActivitySource"
	_activity_source_label.position = Vector2(12, 34)
	_activity_source_label.size = Vector2(308, 22)
	_activity_source_label.text = "Select PNG, then Run Pipeline"
	_activity_source_label.add_theme_font_size_override("font_size", 11)
	_activity_source_label.add_theme_color_override("font_color", Color("#dce8f8"))
	_activity_panel.add_child(_activity_source_label)
	_activity_phase_label = Label.new()
	_activity_phase_label.name = "PipelineActivityPhase"
	_activity_phase_label.position = Vector2(12, 57)
	_activity_phase_label.size = Vector2(308, 20)
	_activity_phase_label.add_theme_font_size_override("font_size", 10)
	_activity_phase_label.add_theme_color_override("font_color", Color("#91a7c5"))
	_activity_panel.add_child(_activity_phase_label)
	_activity_scroll = ScrollContainer.new()
	_activity_scroll.name = "PipelineActivityScroll"
	_activity_scroll.position = Vector2(10, 80)
	_activity_scroll.size = Vector2(314, 406)
	_activity_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_activity_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	_activity_panel.add_child(_activity_scroll)
	_activity_rows = VBoxContainer.new()
	_activity_rows.name = "PipelineActivityRows"
	_activity_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_activity_rows.add_theme_constant_override("separation", 4)
	_activity_scroll.add_child(_activity_rows)
	_activity_panel.visible = false
	_refresh_activity_header()
	_refresh_live_data()


func _update_live_chrome() -> void:
	for node_name in ["RuntimeLeftPanel", "RuntimeCanvasPanel", "RuntimeDetailsPanel", "RuntimeBottomStrip"]:
		var panel := get_node_or_null(node_name) as Control
		if panel != null: panel.visible = true
	var title := get_node_or_null("RuntimeTitle") as Label
	if title != null: title.text = "SCRUBBOTS  /  " + _screen
	if _activity_panel != null: _activity_panel.visible = _screen == "LEVEL FACTORY"
	if _preview_host != null:
		_preview_host.position = Vector2(401, 160)
		_preview_host.size = Vector2(780, 640)
	_refresh_live_data()
	_apply_responsive_layout()


func _refresh_live_data() -> void:
	var live := get_node_or_null("RuntimeLiveData") as Label
	if live == null: return
	var selected_source_text := ""
	if _screen == "LEVEL FACTORY" and not _selected_import_source_id.is_empty():
		selected_source_text = "\nPNG: %s\nSource:\n%s" % [_selected_import_filename(), _wrap_identity(_selected_import_source_id, 18)]
	if _screen == "PIXEL ART":
		live.text = "Provider: %s\nMode: %s\nCanvas: %d × %d\nSeed: %s\nBatch: %d complete · %d failed · %d remaining" % [_provider_model, _generation_mode, _width, _height, _seed if not _seed.is_empty() else "Auto", _semantic_progress.completed, _semantic_progress.failed, _semantic_progress.remaining]
	elif _screen == "LEVEL FACTORY":
		var primary: Dictionary = _last_pipeline.get("primary", {})
		var monitor_failed := str(_last_pipeline.get("studio_monitor_validation", "")) == "FAILED_CLOSED"
		var pipeline_state := "ERROR" if monitor_failed else str(_last_pipeline.get("disposition", _last_pipeline.get("state", "Awaiting pipeline")))
		var pipeline_reason := str(_last_pipeline.get("studio_monitor_reason", _pipeline_stop_reason(_last_pipeline))) if monitor_failed else _pipeline_stop_reason(_last_pipeline)
		var solver_text := "ERROR · activity integrity failed" if monitor_failed else str(primary.get("state", pipeline_state)) if not primary.is_empty() else pipeline_state
		var replay_text := str(primary.get("acceptance", {}).get("replay", "—")) if not primary.is_empty() and not monitor_failed else "—"
		var difficulty_text := str(primary.get("difficulty", {}).get("class", "—")) if not primary.is_empty() and not monitor_failed else "—"
		live.text = "Level: %s\nColumns: %d\nBackground: %s\nSolver: %s\nReplay: %s\nDifficulty V1: %s\n%s%s" % ["Auto" if not _manual_level_override else str(_level_number), _column_count, _background_intent, solver_text, replay_text, difficulty_text, pipeline_reason, selected_source_text]
	else:
		var entries: Array = _release_pool.get("entries", [])
		live.text = "READY levels: %d\nVisible: %d\nSelected: %d\nTarget: %s\nPreflight: %s" % [entries.size(), _visible_release_ids.size(), _selected_release_ids.size(), _release_target, str(_release_pool.get("publish_preflight", {}).get("state", "Not run"))]
	_refresh_runtime_cards()


func _set_runtime_button(button_name: String, caption: String, image_path: String = "") -> void:
	var button := get_node_or_null(button_name) as Button
	if button == null: return
	button.text = caption
	button.icon = _runtime_png_texture(image_path) if not image_path.is_empty() else null
	button.tooltip_text = ""
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


func _pipeline_stop_reason(result: Dictionary) -> String:
	if result.is_empty():
		return "Pipeline: Awaiting run"
	var stages: Array = result.get("stages", [])
	for desired_state in ["ERROR", "TIMEOUT", "UNAVAILABLE", "INTERRUPTED", "PARTIAL / STOPPED", "BLOCKED", "FAIL"]:
		for stage_variant in stages:
			if not stage_variant is Dictionary:
				continue
			var stage: Dictionary = stage_variant
			if str(stage.get("disposition", "")) != desired_state:
				continue
			var reason := str(stage.get("reason", "")).strip_edges()
			if not reason.is_empty():
				return "%s: %s" % [str(stage.get("stage", "Pipeline")), reason.left(110)]
	var direct_reason := str(result.get("error", result.get("reason", ""))).strip_edges()
	return direct_reason.left(110) if not direct_reason.is_empty() else "Pipeline: %s" % str(result.get("disposition", result.get("state", "UNKNOWN")))


func _restore_imported_sources() -> void:
	if _gateway == null:
		return
	var catalog := _extension("library-refresh", {})
	if str(catalog.get("schema", "")) != "scrubbots-source-library-view":
		return
	var release_root := ProjectSettings.globalize_path("res://").path_join("..").simplify_path()
	var sources: Array = catalog.get("sources", [])
	var source_by_id: Dictionary = {}
	for source_variant in sources:
		if not source_variant is Dictionary:
			continue
		var source: Dictionary = source_variant
		var catalog_source_id := str(source.get("source_id", ""))
		var expected_sha := str(source.get("source_sha256", ""))
		var relative_path := str(source.get("immutable_source_path", ""))
		if not catalog_source_id.begins_with("owner-upload-") or catalog_source_id.trim_prefix("owner-upload-") != expected_sha or expected_sha.length() != 64 or relative_path.is_empty():
			continue
		var png_path := release_root.path_join(relative_path).simplify_path()
		if not FileAccess.file_exists(png_path):
			continue
		var bytes := FileAccess.get_file_as_bytes(png_path)
		var hash_ctx := HashingContext.new()
		hash_ctx.start(HashingContext.HASH_SHA256)
		hash_ctx.update(bytes)
		if hash_ctx.finish().hex_encode() != expected_sha:
			continue
		source_by_id[catalog_source_id] = {"path": png_path, "source_id": catalog_source_id, "source_sha256": expected_sha, "disposition": "SOURCE_ONLY", "display_filename": str(source.get("original_filename", "image.png"))}
	var order_ids: Array[String] = []
	var history := _extension("owner-pages", {})
	var batches: Array = history.get("batches", [])
	for batch_index in range(batches.size() - 1, -1, -1):
		if not batches[batch_index] is Dictionary:
			continue
		var items: Array = batches[batch_index].get("items", [])
		for item_variant in items:
			if not item_variant is Dictionary:
				continue
			var batch_source_id := str(item_variant.get("source_id", ""))
			if source_by_id.has(batch_source_id) and batch_source_id not in order_ids:
				order_ids.append(batch_source_id)
	for source_variant in sources:
		if source_variant is Dictionary:
			var remaining_source_id := str(source_variant.get("source_id", ""))
			if source_by_id.has(remaining_source_id) and remaining_source_id not in order_ids:
				order_ids.append(remaining_source_id)
	for ordered_source_id in order_ids:
		_upsert_imported_source(source_by_id[ordered_source_id])
	if _imported_sources.is_empty():
		return
	var selected_exists := false
	for item in _imported_sources:
		if str(item.get("source_id", "")) == _selected_import_source_id:
			selected_exists = true
			break
	if not selected_exists:
		_selected_import_source_id = str(_imported_sources[0].get("source_id", ""))
	var selected_path := ""
	for item in _imported_sources:
		if str(item.get("source_id", "")) == _selected_import_source_id:
			selected_path = str(item.get("path", ""))
			break
	if not selected_path.is_empty():
		_last_source_id = _selected_import_source_id
		_preview_paths_by_screen["LEVEL FACTORY"] = selected_path
	_refresh_runtime_cards()


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
	var page_count := maxi(1, ceili(float(_imported_sources.size()) / float(level_slots.size())))
	_imported_page = clampi(_imported_page, 0, page_count - 1)
	var bottom_heading := get_node_or_null("RuntimeBottomHeading") as Label
	if bottom_heading != null:
		bottom_heading.text = "VARIATIONS  /  RECENT ITEMS · %d PNG · %d/%d" % [_imported_sources.size(), _imported_page + 1, page_count] if _screen == "LEVEL FACTORY" else "VARIATIONS  /  RECENT ITEMS"
	for index in range(level_slots.size()):
		var source_index := _imported_page * level_slots.size() + index
		if source_index < _imported_sources.size():
			var imported: Dictionary = _imported_sources[source_index]
			var source_id := str(imported.get("source_id", ""))
			var filename := str(imported.get("display_filename", "image.png"))
			var disposition := str(imported.get("disposition", "IMPORTED"))
			var status_caption := "REUSED" if disposition == "ALREADY_IMPORTED" else disposition
			var caption := ("● " if source_id == _selected_import_source_id else "") + filename.get_basename().left(9) + "\n" + status_caption
			_set_runtime_button(level_slots[index], caption, str(imported.get("path", "")))
			var button := get_node_or_null(level_slots[index]) as Button
			if button != null:
				button.tooltip_text = "%s\n%s\n%s" % [filename, disposition, _wrap_identity(source_id, 24)]
		else:
			_set_runtime_button(level_slots[index], "—", "")
	if _imported_sources.is_empty():
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
	_place_control("ZoomOneToOne", Rect2(910, 124, 50, 32), _zoom_one_to_one)
	_place_control("ZoomFit", Rect2(960, 124, 50, 32), _fit_canvas)
	_place_control("ToggleGrid", Rect2(1010, 124, 45, 32), _toggle_grid)
	# LEVEL FACTORY: select artwork, set 3/4/5 columns, run real pipeline,
	# then record append-only owner acceptance or rejection for its candidate.
	_place_control("SelectArtwork", Rect2(42, 165, 95, 100), _open_files.bind(true))
	_place_control("LevelNumber", Rect2(172, 165, 190, 38), _edit_level_number)
	_place_control("SupplyColumns3", Rect2(172, 209, 56, 38), _set_columns.bind(3))
	_place_control("SupplyColumns4", Rect2(238, 209, 56, 38), _set_columns.bind(4))
	_place_control("SupplyColumns5", Rect2(304, 209, 56, 38), _set_columns.bind(5))
	_place_control("MaxRobotsAuto", Rect2(172, 253, 190, 38), _keep_auto_robot_cap)
	_place_control("BackgroundIntent", Rect2(172, 297, 190, 38), _toggle_background)
	_place_control("RunLevelPipeline", Rect2(26, 347, 335, 52), _run_level_pipeline)
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
		_clear_preview_for_screen("RELEASE POOL")
		_refresh_release_pool(false)
		_apply_release_projection()
		if not _selected_release_id.is_empty():
			_select_release_entry(_selected_release_id)
	else:
		_present_active_preview()
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
	var result := _extension("batch-import", {"paths": paths})
	var items: Array = result.get("items", [])
	var lines: Array[String] = []
	var item_records: Array[Dictionary] = []
	var imported_count := 0
	var reused_count := 0
	var rejected_count := 0
	var preview_path := ""
	var preview_source_id := ""
	_rejected_imports.clear()
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
			_upsert_imported_source({"path": path, "source_id": source_id, "disposition": state, "display_filename": path.get_file()})
			if preview_path.is_empty():
				preview_path = path
				preview_source_id = source_id
			var detail := "%s · %s" % [state, _wrap_identity(source_id, 24)]
			lines.append("%s\n%s" % [path.get_file(), detail])
			item_records.append({"path": path, "source_id": source_id, "disposition": state, "display_filename": path.get_file()})
		else:
			rejected_count += 1
			var reason := str(item.get("error", item.get("reason", state if not state.is_empty() else result.get("reason", "Canonical import returned no source identity."))))
			lines.append("%s\nREJECTED · %s" % [path.get_file(), reason])
			var rejected := {"path": path, "source_id": source_id, "disposition": "REJECTED", "display_filename": path.get_file(), "error": reason}
			_rejected_imports.append(rejected)
			item_records.append(rejected.duplicate(true))
	_last_import_summary = {
		"selected_count": paths.size(), "imported_count": imported_count, "reused_count": reused_count,
		"rejected_count": rejected_count, "batch_id": str(result.get("batch_id", "")),
		"preview_source_id": preview_source_id, "preview_path": preview_path,
		"accepted_source_count": _imported_sources.size(), "solver_calls": 0,
		"items": lines.duplicate(), "item_records": item_records.duplicate(true), "rejected": _rejected_imports.duplicate(true)
	}
	if not preview_path.is_empty():
		_select_imported_source_by_id(preview_source_id)
	else:
		_last_source_id = ""
		_last_candidate_id = ""
		_last_pipeline.clear()
		_selected_import_source_id = ""
		_clear_preview_for_screen("LEVEL FACTORY")
	var summary := "PNG selection: %d selected · %d imported · %d reused · %d rejected" % [paths.size(), imported_count, reused_count, rejected_count]
	if not preview_source_id.is_empty():
		summary += "\nSelected: %s · %s" % [preview_path.get_file(), _wrap_identity(preview_source_id, 24)]
	_refresh_runtime_cards()
	_refresh_live_data()
	_report(summary)
	if not paths.is_empty():
		_show_import_results(paths.size(), lines)


func _show_import_results(selected_count: int, lines: Array[String]) -> void:
	var dialog := AcceptDialog.new()
	dialog.title = "PNG import · %d selected" % selected_count
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(660, minf(520.0, 76.0 + float(lines.size()) * 38.0))
	dialog.add_child(scroll)
	var detail := Label.new()
	detail.custom_minimum_size = Vector2(640, maxf(76.0, float(lines.size()) * 62.0))
	detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	detail.text = "\n\n".join(lines)
	scroll.add_child(detail)
	add_child(dialog)
	dialog.confirmed.connect(dialog.queue_free)
	dialog.popup_centered()


func _upsert_imported_source(record: Dictionary) -> void:
	var source_id := str(record.get("source_id", ""))
	if source_id.is_empty():
		return
	for index in range(_imported_sources.size()):
		if str(_imported_sources[index].get("source_id", "")) == source_id:
			var existing: Dictionary = _imported_sources[index]
			for key in ["path", "source_sha256", "display_filename"]:
				if not str(record.get(key, "")).is_empty(): existing[key] = record[key]
			existing["disposition"] = record.get("disposition", existing.get("disposition", "IMPORTED"))
			_imported_sources[index] = existing
			return
	_imported_sources.append(record.duplicate(true))


func _selected_import_filename() -> String:
	for record in _imported_sources:
		if str(record.get("source_id", "")) == _selected_import_source_id:
			return str(record.get("display_filename", "image.png"))
	return ""


func _wrap_identity(value: String, chunk_size: int = 24) -> String:
	var parts: Array[String] = []
	for offset in range(0, value.length(), maxi(1, chunk_size)):
		parts.append(value.substr(offset, chunk_size))
	return "\n".join(parts)


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
	var pixel_art_path := str(_preview_paths_by_screen.get("PIXEL ART", ""))
	_show_screen("LEVEL FACTORY")
	if _last_candidate_id.is_empty():
		_report("Generate or select a candidate first.")
	else:
		if not pixel_art_path.is_empty():
			_load_selected_art_preview(pixel_art_path, "LEVEL FACTORY")
		_report("Candidate %s selected. Choose supply columns and run the pipeline." % _last_candidate_id)


func _run_level_pipeline() -> void:
	if _gateway == null or _operation_running:
		return
	if _last_candidate_id.is_empty() and _last_source_id.is_empty():
		_report("Select or generate a candidate first.")
		return
	_operation_running = true
	var request := {"column_count": _column_count, "level_number": _level_number if _manual_level_override else 1, "game_project": OS.get_environment("SCRUBBOTS_PROJECT"), "background_intent": _background_intent, "max_robots": null, "target_difficulty": "V1_ADVISORY"}
	_activity_source_id = _last_source_id if not _last_source_id.is_empty() else _selected_import_source_id
	if _activity_source_id.is_empty() or not _activity_source_id.begins_with("owner-upload-"):
		_operation_running = false
		_report("Select an imported PNG before starting live pipeline activity.")
		return
	_activity_source_sha256 = _activity_source_id.trim_prefix("owner-upload-")
	_activity_source_filename = _selected_import_filename()
	if _activity_source_sha256.length() != 64:
		_operation_running = false
		_report("Imported PNG identity is malformed; pipeline was not started.")
		return
	var now := Time.get_datetime_dict_from_system(true)
	var timestamp := "%04d%02d%02dT%02d%02d%02dZ" % [now.year, now.month, now.day, now.hour, now.minute, now.second]
	var suffix_context := HashingContext.new()
	suffix_context.start(HashingContext.HASH_SHA256)
	suffix_context.update((str(Time.get_ticks_usec()) + _activity_source_id).to_utf8_buffer())
	_activity_run_id = "pipeline-ui-%s-%s" % [timestamp, suffix_context.finish().hex_encode().left(12)]
	var installed_level_factory := ProjectSettings.globalize_path("res://").simplify_path()
	if not installed_level_factory.replace("/", "\\").to_lower().contains("\\release\\scrubbots factory studio\\level_factory"):
		_operation_running = false
		_report("Live activity requires the approved Release installation.")
		return
	_activity_file_path = ProjectSettings.globalize_path("res://output/studio-pipeline-activity").path_join(_activity_run_id + ".jsonl")
	_activity_started_msec = Time.get_ticks_msec()
	_activity_finished_msec = 0
	_activity_seen_sequence = 0
	_activity_read_offset = 0
	_activity_pending_bytes.clear()
	_activity_previous_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"
	_activity_stage = "QUEUED"
	_activity_message = "Canonical backend is starting for the selected PNG."
	_activity_terminal_state = ""
	_activity_backend_disposition = ""
	_activity_event_backend_disposition = ""
	_activity_integrity_error = ""
	_activity_events.clear()
	for child in _activity_rows.get_children(): child.queue_free()
	var run_button := get_node_or_null("RunLevelPipeline") as Button
	if run_button != null: run_button.disabled = true
	var solve_button := get_node_or_null("SolveAgain") as Button
	if solve_button != null: solve_button.disabled = true
	_refresh_activity_header()
	var pipeline_request_data := request.duplicate(true)
	pipeline_request_data["activity_run_id"] = _activity_run_id
	pipeline_request_data["activity_source_sha256"] = _activity_source_sha256
	var pipeline_request := {"source_id": _activity_source_id, "request": pipeline_request_data}
	if not _gateway.has_method("prepare_studio_extension_call") or not _gateway.has_method("execute_prepared_studio_extension_call"):
		_complete_local_pipeline_failure("Canonical async pipeline gateway is unavailable.")
		return
	var prepared: Dictionary = _gateway.call("prepare_studio_extension_call", "pipeline", pipeline_request)
	if prepared.is_empty():
		_complete_local_pipeline_failure("Canonical Python Factory Core is unavailable.")
		return
	_pipeline_mutex.lock()
	_pipeline_worker_done = false
	_pipeline_worker_result.clear()
	_pipeline_mutex.unlock()
	_pipeline_thread = Thread.new()
	var thread_error := _pipeline_thread.start(Callable(self, "_pipeline_worker").bind(prepared))
	if thread_error != OK:
		_pipeline_thread = null
		_complete_local_pipeline_failure("Pipeline worker could not start.")
		return
	_activity_message = "Waiting for the first backend stage."
	_activity_stage = "STARTING"
	_refresh_activity_header()


func _pipeline_worker(prepared: Dictionary) -> void:
	var result: Dictionary = _gateway.call("execute_prepared_studio_extension_call", prepared)
	_pipeline_mutex.lock()
	_pipeline_worker_result = result
	_pipeline_worker_done = true
	_pipeline_mutex.unlock()


func _poll_pipeline_activity() -> void:
	var file: FileAccess
	var length := 0
	var chunk := PackedByteArray()
	if _activity_stream_reader_override != null:
		length = int(_activity_stream_reader_override.call("get_length"))
		if length >= _activity_read_offset:
			chunk = _activity_stream_reader_override.call("read_from", _activity_read_offset)
	else:
		if _activity_file_path.is_empty() or not FileAccess.file_exists(_activity_file_path):
			return
		file = FileAccess.open(_activity_file_path, FileAccess.READ)
		if file == null:
			_fail_activity_monitor("Activity event file cannot be opened.")
			return
		length = file.get_length()
	if length > 256 * 1024 or length < _activity_read_offset:
		if file != null: file.close()
		_fail_activity_monitor("Activity stream exceeded 256 KiB or was truncated while active.")
		return
	if file != null:
		file.seek(_activity_read_offset)
		chunk = file.get_buffer(length - _activity_read_offset)
		file.close()
	_activity_read_offset += chunk.size()
	_consume_activity_bytes(chunk)


func _consume_activity_bytes(chunk: PackedByteArray) -> void:
	_activity_pending_bytes.append_array(chunk)
	while true:
		var newline := _activity_pending_bytes.find(10)
		if newline < 0:
			break
		var line_bytes := _activity_pending_bytes.slice(0, newline)
		_activity_pending_bytes = _activity_pending_bytes.slice(newline + 1)
		if line_bytes.is_empty():
			_fail_activity_monitor("Activity stream contains an empty event line.")
			return
		var line := line_bytes.get_string_from_utf8()
		if line.to_utf8_buffer() != line_bytes:
			_fail_activity_monitor("Activity stream contains invalid UTF-8.")
			return
		var parsed: Variant = JSON.parse_string(line)
		if not parsed is Dictionary or not parsed.get("body") is Dictionary:
			_fail_activity_monitor("Backend activity event is malformed.")
			return
		var body: Dictionary = parsed["body"]
		for numeric_field in ["seq", "elapsed_ms"]:
			var numeric_value: Variant = body.get(numeric_field)
			if typeof(numeric_value) not in [TYPE_INT, TYPE_FLOAT] or not is_finite(float(numeric_value)) or int(numeric_value) != numeric_value:
				_fail_activity_monitor("Activity event numeric field %s is not a finite integer." % numeric_field)
				return
			body[numeric_field] = int(numeric_value)
		var canonical := JSON.stringify(body, "", true, true)
		var hash_ctx := HashingContext.new()
		hash_ctx.start(HashingContext.HASH_SHA256)
		hash_ctx.update(canonical.to_utf8_buffer())
		var actual_hash := hash_ctx.finish().hex_encode()
		if int(body.get("seq", -1)) != _activity_seen_sequence + 1:
			_fail_activity_monitor("Activity event sequence is missing, duplicated, or out of order.")
			return
		if str(body.get("run_id", "")) != _activity_run_id or str(body.get("source_id", "")) != _activity_source_id or str(body.get("source_sha256", "")) != _activity_source_sha256:
			_fail_activity_monitor("Activity event run or source identity does not match this selection.")
			return
		if str(body.get("previous_sha256", "")) != _activity_previous_sha256:
			_fail_activity_monitor("Activity event hash-chain predecessor does not match.")
			return
		if str(parsed.get("body_sha256", "")) != actual_hash:
			_fail_activity_monitor("Activity event SHA-256 does not match its body (record %s, computed %s)." % [str(parsed.get("body_sha256", "")).left(12), actual_hash.left(12)])
			return
		_activity_seen_sequence += 1
		_activity_previous_sha256 = actual_hash
		_activity_stage = str(body.get("stage", "UNKNOWN"))
		_activity_message = str(body.get("message", ""))
		if _activity_stage == "PIPELINE":
			_activity_terminal_state = str(body.get("state", ""))
			_activity_event_backend_disposition = str(body.get("backend_disposition", ""))
		_append_activity_row(body)
		_refresh_activity_header()


func _append_activity_row(body: Dictionary) -> void:
	if _activity_rows == null:
		return
	var scrollbar := _activity_scroll.get_v_scroll_bar()
	var follow_latest := scrollbar.value >= scrollbar.max_value - scrollbar.page - 12.0
	var row := Label.new()
	row.name = "ActivityEvent%03d" % int(body.get("seq", 0))
	row.custom_minimum_size = Vector2(292, 30)
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	row.add_theme_font_size_override("font_size", 10)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var state := str(body.get("state", "UNKNOWN"))
	var icon := "✓" if state in ["PASS", "READY"] else "!" if state in ["FAIL", "ERROR", "BLOCKED", "UNAVAILABLE", "TIMEOUT"] else "•"
	var elapsed := floori(float(maxi(0, int(body.get("elapsed_ms", 0)))) / 1000.0)
	var message := str(body.get("message", "")).replace("\n", " ").left(76)
	row.text = "%02d:%02d  %s %s · %s — %s" % [floori(float(elapsed) / 60.0), posmod(elapsed, 60), icon, str(body.get("stage", "UNKNOWN")), state.replace("_", " "), message]
	var color := Color("#7bd6a2") if icon == "✓" else Color("#f09a8a") if icon == "!" else Color("#e5bd73") if state == "WARNING" else Color("#c5d2e5")
	row.add_theme_color_override("font_color", color)
	_activity_rows.add_child(row)
	_activity_events.append(body.duplicate(true))
	while _activity_events.size() > 200:
		_activity_events.pop_front()
		var first := _activity_rows.get_child(0)
		_activity_rows.remove_child(first)
		first.queue_free()
	if follow_latest:
		_activity_scroll.call_deferred("set_v_scroll", 999999)


func _fail_activity_monitor(reason: String) -> void:
	if not _activity_integrity_error.is_empty():
		return
	_activity_integrity_error = reason.left(200)
	_activity_stage = "ERROR"
	_activity_message = _activity_integrity_error
	_append_activity_row({"seq": _activity_seen_sequence + 1, "elapsed_ms": max(0, Time.get_ticks_msec() - _activity_started_msec), "stage": "TRANSPORT", "state": "ERROR", "message": _activity_integrity_error})
	_refresh_activity_header()


func _refresh_activity_header() -> void:
	if _activity_state_label == null:
		return
	var state := _activity_display_state()
	_activity_state_label.text = state.replace("_", " ").left(13)
	var bg := Color("#34425a")
	if state == "RUNNING": bg = Color("#245478")
	elif state == "READY": bg = Color("#216444")
	elif state in ["BLOCKED", "UNAVAILABLE", "PARTIAL_STOPPED"]: bg = Color("#7a5824")
	elif state in ["ERROR", "TIMEOUT", "INTERRUPTED"]: bg = Color("#743d3c")
	_activity_state_chip.add_theme_stylebox_override("panel", _control_style(bg, bg.lightened(0.22)))
	var filename := _activity_source_filename if not _activity_run_id.is_empty() else _selected_import_filename()
	_activity_source_label.text = "%s  ·  %s" % [filename.left(22) if not filename.is_empty() else "No PNG selected", _format_activity_elapsed()]
	_activity_source_label.tooltip_text = "Source %s  |  Run %s" % [_activity_source_id, _activity_run_id]
	_activity_phase_label.text = "" if _activity_stage in ["", "IDLE"] else "%s · %s" % [_activity_stage.replace("_", " ").left(26), _activity_message.left(48)]
	_activity_phase_label.tooltip_text = _activity_message


func _activity_display_state() -> String:
	if not _activity_backend_disposition.is_empty():
		return _activity_backend_disposition.replace("PARTIAL / ", "PARTIAL_").replace(" ", "_")
	if _activity_terminal_state.is_empty():
		return "RUNNING" if _operation_running else "IDLE"
	return _activity_terminal_state


func _format_activity_elapsed() -> String:
	if _activity_started_msec <= 0:
		return "00:00"
	var finish := _activity_finished_msec if _activity_finished_msec > 0 else Time.get_ticks_msec()
	var seconds := maxi(0, int((finish - _activity_started_msec) / 1000))
	return "%02d:%02d" % [floori(float(seconds) / 60.0), posmod(seconds, 60)]


func _complete_local_pipeline_failure(reason: String) -> void:
	_operation_running = false
	_activity_finished_msec = Time.get_ticks_msec()
	_activity_terminal_state = "ERROR"
	_activity_backend_disposition = "ERROR"
	_activity_stage = "TRANSPORT"
	_activity_message = reason
	_append_activity_row({"seq": _activity_seen_sequence + 1, "elapsed_ms": max(0, Time.get_ticks_msec() - _activity_started_msec), "stage": "TRANSPORT", "state": "ERROR", "message": reason})
	var run_button := get_node_or_null("RunLevelPipeline") as Button
	if run_button != null: run_button.disabled = false
	var solve_button := get_node_or_null("SolveAgain") as Button
	if solve_button != null: solve_button.disabled = false
	_refresh_activity_header()
	_refresh_live_data()
	_report(reason)


func _complete_level_pipeline(result: Dictionary) -> void:
	_last_pipeline = result
	_operation_running = false
	_activity_finished_msec = Time.get_ticks_msec()
	if not _activity_pending_bytes.is_empty():
		_fail_activity_monitor("Activity stream ended with an incomplete trailing event line.")
	if not str(result.get("derived_candidate_id", "")).is_empty():
		_last_candidate_id = str(result["derived_candidate_id"])
	var backend_state := str(result.get("disposition", result.get("state", "ERROR")))
	var event_backend_disposition := _activity_event_backend_disposition
	_activity_backend_disposition = backend_state
	var backend_reason := _pipeline_stop_reason(result)
	var expected_event_state := backend_state.replace("PARTIAL / ", "PARTIAL_").replace(" ", "_")
	var terminal_matches := not _activity_terminal_state.is_empty() and event_backend_disposition == backend_state and _activity_terminal_state == expected_event_state
	if not _activity_integrity_error.is_empty():
		_activity_stage = "TRANSPORT ERROR"
		_activity_message = "%s Backend: %s." % [_activity_integrity_error, backend_reason]
	elif not terminal_matches:
		_activity_stage = "TRANSPORT WARNING"
		_activity_message = "%s%s" % [backend_reason, " · terminal activity event missing or inconsistent." if _activity_terminal_state.is_empty() or event_backend_disposition != backend_state else " · terminal event state did not match backend."]
		_append_activity_row({"seq": _activity_seen_sequence + 1, "elapsed_ms": max(0, Time.get_ticks_msec() - _activity_started_msec), "stage": "TRANSPORT", "state": "WARNING", "message": _activity_message})
	else:
		_activity_stage = "PIPELINE"
		_activity_message = backend_reason
	if backend_state == "READY" and terminal_matches and _activity_integrity_error.is_empty():
		_refresh_release_pool(false)
	if backend_state == "READY" and (not terminal_matches or not _activity_integrity_error.is_empty()):
		_last_pipeline["studio_monitor_validation"] = "FAILED_CLOSED"
		_last_pipeline["studio_monitor_reason"] = "Backend READY is withheld because activity integrity or the terminal event did not verify."
	var run_button := get_node_or_null("RunLevelPipeline") as Button
	if run_button != null: run_button.disabled = false
	var solve_button := get_node_or_null("SolveAgain") as Button
	if solve_button != null: solve_button.disabled = false
	_refresh_activity_header()
	_refresh_live_data()
	_report("Pipeline %s · %s" % [backend_state, backend_reason])


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
	_select_release_entry(id)
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


func _load_selected_art_preview(path: String, screen_name: String = "") -> void:
	var target_screen := screen_name if not screen_name.is_empty() else _screen
	if target_screen not in master_names():
		return
	_preview_paths_by_screen[target_screen] = path
	if target_screen != _screen:
		return
	if path.is_empty():
		_hide_preview_display()
		return
	var global_path := ProjectSettings.globalize_path(path) if path.begins_with("res://") else path
	if not FileAccess.file_exists(global_path):
		_preview_paths_by_screen[target_screen] = ""
		_hide_preview_display()
		return
	var image := Image.load_from_file(global_path)
	if image == null or image.is_empty():
		_preview_paths_by_screen[target_screen] = ""
		_hide_preview_display()
		return
	_render_preview_image(image, path)
	var transparent := 0
	var colors: Dictionary = {}
	for y in range(image.get_height()):
		for x in range(image.get_width()):
			var pixel := image.get_pixel(x, y)
			if pixel.a < 1.0: transparent += 1
			colors[pixel.to_rgba32()] = true
	_report("%d × %d · %d colors · %d transparent · PNG" % [image.get_width(), image.get_height(), colors.size(), transparent])


func _render_preview_image(image: Image, path: String = "") -> void:
	_preview_rect.texture = ImageTexture.create_from_image(image)
	var fit_scale := minf(_preview_host.size.x / float(image.get_width()), _preview_host.size.y / float(image.get_height()))
	var fitted_size := Vector2(image.get_width(), image.get_height()) * fit_scale
	_preview_rect.size = fitted_size
	_preview_rect.position = (_preview_host.size - fitted_size) * 0.5
	_preview_rect.pivot_offset = fitted_size * 0.5
	_preview_content.size = _preview_host.size
	_preview_content.pivot_offset = _preview_content.size * 0.5
	_preview_content.scale = Vector2.ONE * _zoom
	_preview_rect.visible = true
	_active_preview_path = path
	_selected_art_path = path
	_update_grid_overlay(image.get_width(), image.get_height())


func _hide_preview_display() -> void:
	_active_preview_path = ""
	if _preview_rect != null:
		_preview_rect.texture = null
		_preview_rect.visible = false
	for line in _grid_lines:
		line.visible = false
	if _preview_content != null:
		_preview_content.scale = Vector2.ONE


func _clear_preview_for_screen(screen_name: String) -> void:
	_preview_paths_by_screen[screen_name] = ""
	if screen_name == _screen:
		_hide_preview_display()
		_selected_art_path = ""


func _present_active_preview() -> void:
	var path := str(_preview_paths_by_screen.get(_screen, ""))
	if path.is_empty():
		_hide_preview_display()
		_selected_art_path = ""
		return
	_load_selected_art_preview(path, _screen)


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
	var artwork_path := str(chosen.get("artwork_path", ""))
	if not artwork_path.is_empty():
		_load_selected_art_preview(artwork_path, "PIXEL ART")
	_report("Artwork selected")


func _select_variation(index: int) -> void:
	if not _imported_sources.is_empty():
		var queue_index := _imported_page * 8 + index
		if index >= 0 and queue_index < _imported_sources.size():
			_select_imported_source_by_id(str(_imported_sources[queue_index].get("source_id", "")))
		return
	_select_inbox_candidate(index)


func _select_imported_source_by_id(source_id: String) -> void:
	for index in range(_imported_sources.size()):
		var imported: Dictionary = _imported_sources[index]
		if str(imported.get("source_id", "")) != source_id:
			continue
		_selected_import_source_id = source_id
		_selected_art_path = str(imported.get("path", ""))
		_last_source_id = source_id
		_last_candidate_id = ""
		_last_pipeline.clear()
		_imported_page = index / 8
		_preview_paths_by_screen["LEVEL FACTORY"] = _selected_art_path
		_load_selected_art_preview(_selected_art_path, "LEVEL FACTORY")
		_refresh_runtime_cards()
		_refresh_live_data()
		_report("Selected %s · %s" % [str(imported.get("display_filename", "image.png")), _wrap_identity(source_id, 24)])
		return


func _page_imported_sources(direction: int) -> void:
	var page_count := maxi(1, ceili(float(_imported_sources.size()) / 8.0))
	if page_count <= 1:
		return
	_imported_page = posmod(_imported_page + direction, page_count)
	_refresh_runtime_cards()


func _unhandled_input(event: InputEvent) -> void:
	if _screen != "LEVEL FACTORY" or _imported_sources.size() <= 8 or _preview_host == null:
		return
	if not event is InputEventMouseButton:
		return
	var mouse := event as InputEventMouseButton
	if not mouse.pressed or mouse.button_index not in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
		return
	var strip := get_node_or_null("RuntimeBottomStrip") as Control
	if strip == null or not strip.get_global_rect().has_point(get_global_mouse_position()):
		return
	_page_imported_sources(-1 if mouse.button_index == MOUSE_BUTTON_WHEEL_UP else 1)
	get_viewport().set_input_as_handled()


func _select_inbox_candidate(index: int) -> void:
	var inbox := _extension("candidate-inbox", {})
	var candidates: Array = inbox.get("candidates", [])
	if index < 0 or index >= candidates.size(): return
	var candidate: Dictionary = candidates[index]
	_last_candidate_id = str(candidate.get("candidate_id", ""))
	_last_source_id = ""
	_selected_import_source_id = ""
	var source_path := str(candidate.get("source_path", candidate.get("artwork_path", "")))
	var artwork_path := source_path if source_path.ends_with(".png") else (source_path.path_join("artwork.png") if not source_path.is_empty() else "")
	if not artwork_path.is_empty(): _load_selected_art_preview(artwork_path, _screen)
	_report("Artwork selected")


func _adjust_zoom(amount: float) -> void:
	_set_zoom(clampf(_zoom * (1.25 if amount > 0.0 else 0.8), 0.02, 16.0))


func _set_zoom(value: float) -> void:
	_zoom = clampf(value, 0.02, 16.0)
	if _preview_content != null:
		_preview_content.scale = Vector2.ONE * _zoom


func _zoom_one_to_one() -> void:
	if _preview_rect == null or _preview_rect.texture == null:
		return
	var image_size := _preview_rect.texture.get_size()
	var fit_scale := minf(_preview_host.size.x / image_size.x, _preview_host.size.y / image_size.y)
	_set_zoom(1.0 / fit_scale)


func _set_zoom_from_pointer() -> void:
	var position_x := get_viewport().get_mouse_position().x
	_set_zoom(0.02 + clampf((position_x - 735.0) / 136.0, 0.0, 1.0) * 15.98)


func _fit_canvas() -> void:
	_set_zoom(1.0)


func _toggle_grid() -> void:
	_grid_enabled = not _grid_enabled
	for line in _grid_lines: line.visible = _grid_enabled and _preview_rect != null and _preview_rect.visible
	_report("Grid %s" % ("On" if _grid_enabled else "Off"))


func _build_grid_overlay() -> void:
	_update_grid_overlay(32, 32)


func _update_grid_overlay(image_width: int, image_height: int) -> void:
	for line in _grid_lines:
		if is_instance_valid(line):
			line.queue_free()
	_grid_lines.clear()
	if _preview_content == null or image_width <= 0 or image_height <= 0:
		return
	var fit := minf(_preview_host.size.x / float(image_width), _preview_host.size.y / float(image_height))
	var draw_size := Vector2(image_width, image_height) * fit
	var origin := (_preview_host.size - draw_size) * 0.5
	for index in range(image_width + 1):
		var x := origin.x + index * fit
		var line := Line2D.new()
		line.name = "PreviewGridVertical%03d" % index
		line.add_point(Vector2(x, origin.y))
		line.add_point(Vector2(x, origin.y + draw_size.y))
		_add_preview_grid_line(line)
	for index in range(image_height + 1):
		var y := origin.y + index * fit
		var line := Line2D.new()
		line.name = "PreviewGridHorizontal%03d" % index
		line.add_point(Vector2(origin.x, y))
		line.add_point(Vector2(origin.x + draw_size.x, y))
		_add_preview_grid_line(line)


func _add_preview_grid_line(line: Line2D) -> void:
	line.width = 1.0
	line.default_color = Color(1, 1, 1, 0.22)
	line.visible = _grid_enabled and _preview_rect != null and _preview_rect.visible
	_preview_content.add_child(line)
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
			_load_selected_art_preview(artwork, "RELEASE POOL")
		else:
			_clear_preview_for_screen("RELEASE POOL")
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
