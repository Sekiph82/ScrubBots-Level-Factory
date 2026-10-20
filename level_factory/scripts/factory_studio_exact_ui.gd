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
var _screen := "PIXEL ART"
var _last_candidate_id := ""
var _last_source_id := ""
var _last_pipeline: Dictionary = {}
var _owner_review_status := ""
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
var _supply_dialog: AcceptDialog
var _replay_dialog: AcceptDialog
var _replay_step_label: RichTextLabel
var _replay_trace: Array = []
var _replay_step := 0
var _details_rows: Array[Label] = []
var _results_panel: Panel
var _results_summary: Label
var _results_scroll: ScrollContainer
var _results_rows: VBoxContainer
var _results_nav: HBoxContainer
var _results_mode := ""
var _results_source_id := ""
var _results_run_id := ""
var _batch_job_id := ""
var _batch_import_id := ""
var _batch_snapshot: Dictionary = {}
var _batch_composite_snapshot: Dictionary = {}
var _batch_legacy_reconciliation := false
var _batch_job_source_mismatch := false
var _batch_last_read_msec := 0
var _batch_pause_button: Button
var _batch_stop_button: Button
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
var _canonical_palette_colors: Array = []
var _master_buttons: Array[Button] = []
var _grid_lines: Array[Line2D] = []
var _preview_host: Control
var _preview_content: Control
var _preview_rect: TextureRect
var _selected_art_path := ""
var _active_preview_path := ""
var _preview_paths_by_screen := {"PIXEL ART": "", "LEVEL FACTORY": "", "RELEASE POOL": ""}
var _imported_sources: Array[Dictionary] = []
var _gameplay_sources: Array[Dictionary] = []
var _source_batch_by_id: Dictionary = {}
var _rejected_imports: Array[Dictionary] = []
var _imported_window_start := 0
var _selected_import_source_id := ""
var _seed := ""
var _background_intent := "TRANSPARENT"
const _REFERENCE_SIZE := Vector2(1536.0, 1024.0)
var _canonical_palette_hex_by_id: Dictionary = {}
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
var _studio_read_thread: Thread
var _studio_read_mutex := Mutex.new()
var _studio_read_done := false
var _studio_read_result: Dictionary = {}
var _studio_read_context: Dictionary = {}
var _studio_read_queue: Array[Dictionary] = []
var _pixel_art_thread: Thread
var _pixel_art_mutex := Mutex.new()
var _pixel_art_worker_done := false
var _pixel_art_worker_result: Dictionary = {}
var _candidate_inbox_cache: Dictionary = {}
var _candidate_inbox_last_request_msec := -60000
var _selection_restore_token := ""
var _batch_worker_active := false
var _studio_cancel_marker_path := ""
var _studio_cancel_previous_environment := ""
var _shutdown_requested := false
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
var _batch_follow_item: Dictionary = {}
var _batch_follow_pipeline: Dictionary = {}
var _batch_follow_token := ""
var _batch_observed_item_states: Dictionary = {}
var _release_candidate_scroll: ScrollContainer
var _release_candidate_rows: VBoxContainer
var _release_candidate_signature := ""
var _release_candidate_row_height := 36.0
var _release_activity_title: Label
var _release_activity_scroll: ScrollContainer
var _release_activity_rows: VBoxContainer
var _release_activity_events: Array[Dictionary] = []
var _release_help_dialog: AcceptDialog
var _activity_previous_sha256 := "0000000000000000000000000000000000000000000000000000000000000000"
var _activity_stage := "IDLE"
var _activity_message := "Select an imported PNG, then run the pipeline."
var _activity_terminal_state := ""
var _activity_backend_disposition := ""
var _activity_event_backend_disposition := ""
var _activity_integrity_error := ""
const _PINNED_002_SOURCE_ID := "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
const _PINNED_GAME_COMMIT := "aef60a616d4ac401e9dfac15df6fe56e671c0053"
var _pinned_source_preflight_ok := false
var _pinned_source_preflight_message := "PINNED_SOURCE_SCOPE_NOT_VERIFIED"


func _ready() -> void:
	# Retire a legacy selection on startup without changing saved asset provenance.
	if _provider_model == "MAGNIFIC":
		_provider_model = "ALPIX (Claude)"
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
	_build_master_controls()
	_show_screen(_screen)
	call_deferred("_restore_imported_sources")
	_capture_responsive_layout()
	resized.connect(_apply_responsive_layout)
	_apply_responsive_layout()


func _process(_delta: float) -> void:
	_poll_studio_read_extension()
	_start_next_studio_read_extension()
	if _shutdown_requested and _studio_read_thread == null and _pipeline_thread == null and _pixel_art_thread == null:
		get_tree().quit()
		return
	_poll_pixel_art_worker()
	if not _batch_job_id.is_empty() and not _batch_job_source_mismatch:
		_refresh_batch_progress()
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
		_finish_worker_cancel_marker()
		_complete_level_pipeline(result)
		if _shutdown_requested:
			get_tree().quit()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		if _studio_read_thread != null:
			_shutdown_requested = true
			_studio_read_queue.clear()
			_activity_message = "Closing after the active local read finishes."
			_activity_stage = "CLOSING"
			_refresh_activity_header()
			return
		if _operation_running and _pipeline_thread != null:
			_shutdown_requested = true
			_signal_worker_cancel_marker()
			if not _batch_job_id.is_empty():
				_request_batch_control("CANCEL_NOW")
			_activity_message = "Closing after the active Python and game solver processes stop."
			_activity_stage = "CANCELLING"
			_refresh_activity_header()
			return
		if _operation_running and _pixel_art_thread != null:
			_shutdown_requested = true
			_signal_worker_cancel_marker()
			_report("Closing after the active PixelLab job is cancelled or reaches a terminal state.")
			return
		get_tree().quit()


func _prepare_worker_cancel_marker() -> void:
	if not _studio_cancel_marker_path.is_empty():
		_finish_worker_cancel_marker()
	_studio_cancel_marker_path = ProjectSettings.globalize_path("res://output/.studio-cancel-%d.flag" % Time.get_ticks_usec())
	_studio_cancel_previous_environment = OS.get_environment("SCRUBBOTS_FACTORY_STUDIO_CANCEL_FILE")
	OS.set_environment("SCRUBBOTS_FACTORY_STUDIO_CANCEL_FILE", _studio_cancel_marker_path)


func _signal_worker_cancel_marker() -> void:
	if _studio_cancel_marker_path.is_empty():
		return
	var marker := FileAccess.open(_studio_cancel_marker_path, FileAccess.WRITE)
	if marker != null:
		marker.store_string("CANCEL_NOW\n")
		marker.close()


func _finish_worker_cancel_marker() -> void:
	if not _studio_cancel_marker_path.is_empty():
		OS.set_environment("SCRUBBOTS_FACTORY_STUDIO_CANCEL_FILE", _studio_cancel_previous_environment)
	if not _studio_cancel_marker_path.is_empty() and FileAccess.file_exists(_studio_cancel_marker_path):
		DirAccess.remove_absolute(_studio_cancel_marker_path)
	_studio_cancel_marker_path = ""
	_studio_cancel_previous_environment = ""


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
	_responsive_scale = 1.0
	_responsive_offset = Vector2.ZERO
	var scale_x := float(geometry.get("scale_x", 1.0))
	var scale_y := float(geometry.get("scale_y", 1.0))
	var center_start := float(geometry.get("center_start", 389.0))
	var right_start := float(geometry.get("right_start", 1205.0))
	var left_scale := float(geometry.get("left_scale", 1.0))
	var center_scale := float(geometry.get("center_scale", 1.0))
	var right_scale := float(geometry.get("right_scale", 1.0))
	for node in _responsive_nodes:
		if not is_instance_valid(node):
			continue
		var base: Dictionary = _responsive_base.get(node.get_instance_id(), {})
		if base.is_empty():
			continue
		if node is Control:
			var control := node as Control
			var position: Vector2 = base.position
			var item_scale := center_scale
			if position.y < 100.0:
				position.x *= scale_x
				item_scale = scale_x
			elif position.x < 380.0:
				position.x = 18.0 + (position.x - 18.0) * left_scale
				item_scale = left_scale
			elif position.x >= 1193.0:
				position.x = right_start + (position.x - 1205.0) * right_scale
				item_scale = right_scale
			else:
				position.x = center_start + (position.x - 389.0) * center_scale
			control.position = Vector2(position.x, position.y * scale_y)
			control.size = Vector2(base.size.x * item_scale, base.size.y * scale_y)
			control.scale = base.scale
		elif node is Line2D:
			var line := node as Line2D
			line.position = Vector2(base.position.x * scale_x, base.position.y * scale_y)
			line.scale = base.scale * Vector2(scale_x, scale_y)
	# Anchor long panels and the image strip to the real client bottom; no 1536x1024 letterbox remains.
	var bottom_margin := 18.0 * scale_y
	var main_top := 116.0 * scale_y
	var dock_height := 106.0 * scale_y
	if _screen == "LEVEL FACTORY":
		dock_height = clampf(164.0 * scale_y, 128.0, 182.0)
	var bottom_y := size.y - bottom_margin - dock_height
	var left_panel := get_node_or_null("RuntimeLeftPanel") as Control
	var details_panel := get_node_or_null("RuntimeDetailsPanel") as Control
	var center_panel := get_node_or_null("RuntimeCanvasPanel") as Control
	var bottom_panel := get_node_or_null("RuntimeBottomStrip") as Control
	var background := get_node_or_null("RuntimeBackground") as Control
	var header_panel := get_node_or_null("RuntimeHeader") as Control
	if background != null: background.size = size
	if header_panel != null: header_panel.size.x = size.x
	if left_panel != null: left_panel.size.y = maxf(220.0, size.y - left_panel.position.y - bottom_margin)
	if details_panel != null: details_panel.size.y = maxf(220.0, size.y - details_panel.position.y - bottom_margin)
	if bottom_panel != null:
		bottom_panel.position.y = bottom_y
		bottom_panel.size.y = dock_height
	if center_panel != null:
		center_panel.size.x = maxf(300.0, right_start - center_start - 16.0)
		center_panel.size.y = maxf(220.0, bottom_y - main_top - 12.0 * scale_y)
	if _preview_host != null:
		_preview_host.position = Vector2(center_start + 12.0 * center_scale, 160.0 * scale_y)
		_preview_host.size = Vector2(maxf(280.0, center_panel.size.x - 24.0 * center_scale), maxf(180.0, bottom_y - _preview_host.position.y - 24.0 * scale_y))
		_preview_content.pivot_offset = _preview_host.size * 0.5
		_fit_preview_image_to_host()
	if _results_panel != null:
		var panel_bottom := size.y - bottom_margin
		_results_panel.size.y = maxf(180.0, panel_bottom - _results_panel.position.y)
	if _activity_panel != null:
		_activity_panel.size.y = maxf(220.0, size.y - _activity_panel.position.y - bottom_margin)
		if _activity_scroll != null:
			_activity_scroll.position = Vector2(10.0 * left_scale, 116.0 * scale_y)
			_activity_scroll.size = Vector2(maxf(120.0, _activity_panel.size.x - 20.0 * left_scale), maxf(80.0, _activity_panel.size.y - _activity_scroll.position.y - 10.0 * scale_y))
		if _batch_pause_button != null and _batch_stop_button != null:
			var button_gap := 5.0 * left_scale
			var action_width := maxf(70.0, (_activity_panel.size.x - 20.0 * left_scale - button_gap) * 0.5)
			_batch_pause_button.position = Vector2(10.0 * left_scale, 80.0 * scale_y)
			_batch_pause_button.size = Vector2(action_width, 30.0 * scale_y)
			_batch_stop_button.position = Vector2(_batch_pause_button.position.x + action_width + button_gap, 80.0 * scale_y)
			_batch_stop_button.size = Vector2(action_width, 30.0 * scale_y)
	_layout_level_factory_thumbnail_dock(center_scale, scale_y)
	_layout_release_pool_dashboard(left_scale, right_start, float(geometry.get("right_width", 313.0)), scale_y)


func _layout_level_factory_thumbnail_dock(center_scale: float, scale_y: float) -> void:
	var dock := get_node_or_null("RuntimeBottomStrip") as Control
	var heading := get_node_or_null("RuntimeBottomHeading") as Label
	if dock == null or heading == null:
		return
	var slots := ["LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5"]
	var horizontal_padding := 8.0
	var vertical_padding := 8.0
	var card_gap := clampf(6.0 * center_scale, 3.0, 6.0)
	var heading_height := clampf(15.0 * scale_y, 13.0, 18.0)
	var heading_gap := maxf(2.0, 3.0 * scale_y)
	var content_width := maxf(0.0, dock.size.x - horizontal_padding * 2.0)
	var card_width := (content_width - card_gap * float(slots.size() - 1)) / float(slots.size())
	var card_height := dock.size.y - vertical_padding * 2.0 - heading_height - heading_gap
	if card_width <= 0.0 or card_height <= 0.0:
		return
	# These controls are siblings of the dock, so add its local position exactly once.
	heading.position = dock.position + Vector2(horizontal_padding, vertical_padding)
	heading.size = Vector2(content_width, heading_height)
	heading.add_theme_font_size_override("font_size", clampi(roundi(12.0 * center_scale), 10, 12))
	var card_font_size := clampi(roundi(12.0 * minf(center_scale, scale_y)), 9, 12)
	for index in range(slots.size()):
		var button := get_node_or_null(slots[index]) as Button
		if button == null:
			continue
		var x := horizontal_padding + float(index) * (card_width + card_gap)
		button.position = dock.position + Vector2(x, vertical_padding + heading_height + heading_gap)
		button.size = Vector2(card_width, card_height)
		button.add_theme_font_size_override("font_size", card_font_size)
		for state in ["normal", "hover", "pressed", "focus"]:
			var current_style := button.get_theme_stylebox(state) as StyleBoxFlat
			if current_style == null:
				continue
			if (is_equal_approx(current_style.content_margin_left, 2.0)
					and is_equal_approx(current_style.content_margin_right, 2.0)
					and is_equal_approx(current_style.content_margin_top, 2.0)
					and is_equal_approx(current_style.content_margin_bottom, 2.0)):
				continue
			var compact_style := current_style.duplicate() as StyleBoxFlat
			compact_style.content_margin_left = 2.0
			compact_style.content_margin_right = 2.0
			compact_style.content_margin_top = 2.0
			compact_style.content_margin_bottom = 2.0
			button.add_theme_stylebox_override(state, compact_style)


func _fit_preview_image_to_host() -> void:
	if _preview_host == null or _preview_rect == null or _preview_content == null:
		return
	if _preview_rect.texture == null:
		return
	var texture_size := _preview_rect.texture.get_size()
	if texture_size.x <= 0.0 or texture_size.y <= 0.0:
		return
	var fit_scale := minf(_preview_host.size.x / texture_size.x, _preview_host.size.y / texture_size.y)
	var fitted_size := texture_size * fit_scale
	_preview_rect.size = fitted_size
	_preview_rect.position = (_preview_host.size - fitted_size) * 0.5
	_preview_rect.pivot_offset = fitted_size * 0.5
	_preview_content.size = _preview_host.size
	_preview_content.pivot_offset = _preview_host.size * 0.5


func _layout_release_pool_dashboard(left_scale: float, right_start: float, right_width: float, scale_y: float) -> void:
	var left_panel := get_node_or_null("RuntimeLeftPanel") as Control
	var dock := get_node_or_null("RuntimeBottomStrip") as Control
	if left_panel != null and _release_candidate_scroll != null:
		var bottom := left_panel.position.y + left_panel.size.y
		var outer_padding := 8.0 * left_scale
		var button_gap := 6.0 * scale_y
		var select_height := 36.0 * scale_y
		var manage_height := 36.0 * scale_y
		var controls_bottom := bottom - 8.0 * scale_y
		var clear_y := controls_bottom - select_height
		var manage_y := clear_y - button_gap - manage_height
		var controls_x := left_panel.position.x + outer_padding
		var controls_width := maxf(160.0, left_panel.size.x - outer_padding * 2.0)
		var manage := get_node_or_null("ManageSelection") as Control
		var select_all := get_node_or_null("SelectAllRelease") as Control
		var clear := get_node_or_null("ClearRelease") as Control
		if manage != null:
			manage.position = Vector2(controls_x, manage_y)
			manage.size = Vector2(controls_width, manage_height)
		if select_all != null:
			select_all.position = Vector2(controls_x, clear_y)
			select_all.size = Vector2((controls_width - button_gap) * 0.5, select_height)
		if clear != null:
			clear.position = Vector2(controls_x + (controls_width + button_gap) * 0.5, clear_y)
			clear.size = Vector2((controls_width - button_gap) * 0.5, select_height)
		var list_top := 292.0 * scale_y
		_release_candidate_scroll.position = Vector2(controls_x, list_top)
		_release_candidate_scroll.size = Vector2(controls_width, maxf(80.0, manage_y - list_top - button_gap))
		_release_candidate_row_height = clampf((_release_candidate_scroll.size.y - 42.0) / 15.0, 29.0 * scale_y, 42.0 * scale_y)
		_release_candidate_signature = ""
		_refresh_release_candidate_rows()
	if dock == null:
		return
	var heading := get_node_or_null("RuntimeBottomHeading") as Label
	if heading != null:
		heading.text = "SELECTED FOR RELEASE" if _screen == "RELEASE POOL" else "VARIATIONS  /  RECENT ITEMS · %d PNG" % _gameplay_sources.size()
	var names := ["SelectedReleaseCard1", "SelectedReleaseCard2", "SelectedReleaseCard3", "AddMoreLevels"]
	var removals := ["RemoveSelected1", "RemoveSelected2", "RemoveSelected3"]
	var pad := 8.0 * maxf(0.75, float(dock.size.x) / 804.0)
	var gap := 8.0 * maxf(0.75, float(dock.size.x) / 804.0)
	var heading_gap := 28.0 * scale_y
	var row_height := maxf(34.0, dock.size.y - heading_gap - 8.0 * scale_y)
	var row_width := (dock.size.x - pad * 2.0 - gap * 3.0) / float(names.size())
	if row_width <= 0.0:
		return
	var row_y := dock.position.y + heading_gap
	if heading != null:
		heading.position = dock.position + Vector2(8.0, 12.0 * scale_y)
		heading.size = Vector2(dock.size.x - 16.0, 20.0 * scale_y)
	var card_controls: Array[Button] = []
	for node_name in names:
		var button := get_node_or_null(node_name) as Button
		if button != null:
			card_controls.append(button)
	var card_font_size := 9
	for candidate_font_size in range(12, 8, -1):
		var all_captions_fit := true
		for button in card_controls:
			button.add_theme_font_size_override("font_size", candidate_font_size)
			if button.get_combined_minimum_size().x > row_width:
				all_captions_fit = false
		if all_captions_fit:
			card_font_size = candidate_font_size
			break
	for button in card_controls:
		button.add_theme_font_size_override("font_size", card_font_size)
	for index in range(names.size()):
		var control := get_node_or_null(names[index]) as Control
		if control == null:
			continue
		var x := dock.position.x + pad + float(index) * (row_width + gap)
		control.position = Vector2(x, row_y)
		control.size = Vector2(row_width, row_height)
		if index < removals.size():
			var remove := get_node_or_null(removals[index]) as Control
			if remove != null:
				remove.position = Vector2(x + row_width - 28.0 * scale_y, row_y + 2.0 * scale_y)
				remove.size = Vector2(24.0 * scale_y, 24.0 * scale_y)
	var release_help_names := ["ReleaseStagingHelp", "ReleaseProductionHelp", "PreflightReleaseHelp", "ValidateReleaseAssetsHelp", "BuildReleasePackHelp", "UploadR2StatusHelp", "UploadSelectedHelp", "PreviewReleaseManifestHelp"]
	var action_names := ["ReleaseStaging", "ReleaseProduction", "PreflightRelease", "ValidateReleaseAssets", "BuildReleasePack", "UploadR2Status", "UploadSelected", "PreviewReleaseManifest"]
	var details_panel := get_node_or_null("RuntimeDetailsPanel") as Control
	var panel_rect := details_panel.get_global_rect() if details_panel != null else Rect2(right_start, 116.0 * scale_y, right_width, size.y - 134.0 * scale_y)
	var right_scale := panel_rect.size.x / 313.0
	var action_inset := 10.0 * right_scale
	var help_width := 30.0 * right_scale
	var help_gap := 5.0 * right_scale
	var action_x := panel_rect.position.x + action_inset
	var action_width := maxf(120.0, panel_rect.size.x - action_inset * 2.0 - help_width - help_gap)
	var release_action_row_height := clampf(34.0 * scale_y, 28.0, 36.0)
	var row_gap := clampf(6.0 * scale_y, 4.0, 7.0)
	var actions_top := 398.0 * scale_y
	for index in range(action_names.size()):
		var action := get_node_or_null(action_names[index]) as Control
		var info := get_node_or_null(release_help_names[index]) as Control
		if action == null or info == null:
			continue
		var action_y := actions_top + float(index) * (release_action_row_height + row_gap)
		action.position = Vector2(action_x, action_y)
		action.size = Vector2(action_width, release_action_row_height)
		info.position = Vector2(action_x + action_width + help_gap, action_y)
		info.size = Vector2(help_width, release_action_row_height)
	if _release_activity_title != null and _release_activity_scroll != null:
		var last_action := get_node_or_null("PreviewReleaseManifest") as Control
		var last_help := get_node_or_null("PreviewReleaseManifestHelp") as Control
		var last_row_bottom := maxf(last_action.get_global_rect().end.y, last_help.get_global_rect().end.y) if last_action != null and last_help != null else actions_top
		var activity_top := last_row_bottom + 8.0 * scale_y
		var activity_x := panel_rect.position.x + action_inset
		var activity_width := panel_rect.size.x - action_inset * 2.0
		var title_height := clampf(18.0 * scale_y, 16.0, 20.0)
		var activity_bottom := panel_rect.end.y - 8.0 * scale_y
		_release_activity_title.position = Vector2(activity_x, activity_top)
		_release_activity_title.size = Vector2(activity_width, title_height)
		_release_activity_scroll.position = Vector2(activity_x, activity_top + title_height + 3.0 * scale_y)
		_release_activity_scroll.size = Vector2(activity_width, maxf(80.0, activity_bottom - _release_activity_scroll.position.y))
		_release_activity_title.visible = _screen == "RELEASE POOL"
		_release_activity_scroll.visible = _screen == "RELEASE POOL"
		_release_candidate_scroll.visible = _screen == "RELEASE POOL"
	_refresh_release_pool_activity()


func responsive_layout_snapshot() -> Dictionary:
	return {"reference_size": _REFERENCE_SIZE, "viewport_size": size, "scale": _responsive_scale, "offset": _responsive_offset}


func responsive_geometry(viewport_size: Vector2) -> Dictionary:
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		return {"scale": 1.0, "scale_x": 1.0, "scale_y": 1.0, "offset": Vector2.ZERO, "content_size": _REFERENCE_SIZE}
	var margin := minf(18.0, viewport_size.x * 0.02)
	var gap := minf(16.0, viewport_size.x * 0.018)
	var left_width := clampf(viewport_size.x * 0.23, 285.0, 354.0)
	var right_width := clampf(viewport_size.x * 0.204, 300.0, 420.0)
	var usable := maxf(300.0, viewport_size.x - margin * 2.0 - gap * 2.0)
	var center_width := maxf(300.0, usable - left_width - right_width)
	var center_start := margin + left_width + gap
	var right_start := center_start + center_width + gap
	var scale_y := clampf(viewport_size.y / _REFERENCE_SIZE.y, 0.72, 1.12)
	return {
		"scale": 1.0, "scale_x": viewport_size.x / _REFERENCE_SIZE.x, "scale_y": scale_y,
		"offset": Vector2.ZERO, "content_size": viewport_size,
		"left_scale": left_width / 354.0, "center_scale": center_width / 804.0,
		"right_scale": right_width / 313.0, "center_start": center_start,
		"right_start": right_start, "left_width": left_width, "center_width": center_width,
		"right_width": right_width, "minimum_supported_size": Vector2(1100.0, 720.0),
	}


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
		"SettingsGear": "Settings",
		"GeneratePixelArt": "Generate", "BatchCsvSelect": "Select CSV", "RunBatch": "Resume" if _batch_resume else "Run Batch",
		"Regenerate": "Regenerate", "EditPrompt": "Edit Prompt", "AddToLevelFactory": "Use in Level Factory",
		"GenerationPrompt": "Prompt", "RandomSeed": "↻", "GenerationStyle": "Style: %s" % _generation_style,
		"GenerationSize": "Size: %d × %d" % [_width, _height], "GenerationProvider": "Provider: %s" % _provider_model,
		"SingleMode": "Single", "BatchMode": "Batch", "BatchCsvPath": "CSV file…",
		"ArtworkVariation1": "Variation 1", "ArtworkVariation2": "Variation 2", "ArtworkVariation3": "Variation 3",
		"RemoveSelected1": "×", "RemoveSelected2": "×", "RemoveSelected3": "×",
		"ArtworkCarouselLeft": "‹", "ArtworkCarouselRight": "›", "ZoomOut": "−", "ZoomIn": "+",
		"ZoomOneToOne": "1:1", "ZoomFit": "Fit", "ToggleGrid": "Grid", "SelectArtwork": "Select PNG",
		"LevelNumber": _level_number_caption(), "SupplyColumns3": "3", "SupplyColumns4": "4", "SupplyColumns5": "5",
		"MaxRobotsAuto": "Max Robots: Auto", "BackgroundIntent": "Background: %s" % _background_intent,
		"RunLevelPipeline": "Run Pipeline", "SolveAgain": "Solve Again", "PreviewReplay": "Preview Replay",
		"ExpandSupplyPlan": "Supply Plan", "AcceptLevel": "Accept", "RejectLevel": "Reject",
		"RefreshReleasePool": "Refresh", "SelectReleaseLevel": "Select level", "ReleaseSearch": "Search levels",
		"DifficultyFilter": "Difficulty", "ColumnsFilter": "Columns", "ManageSelection": "Manage Selection",
		"SelectAllRelease": "Select All", "ClearRelease": "Clear", "ReleaseStaging": "STAGING",
		"ReleaseProduction": "PRODUCTION", "PreflightRelease": "Preflight", "ValidateReleaseAssets": "Validate Assets",
		"BuildReleasePack": "Build Scrubpack", "UploadR2Status": "Upload Status",
		"UploadSelected": "Upload Selected", "PreviewReleaseManifest": "Preview Manifest",
		"ReleaseStagingHelp": "ⓘ", "ReleaseProductionHelp": "ⓘ", "PreflightReleaseHelp": "ⓘ",
		"ValidateReleaseAssetsHelp": "ⓘ", "BuildReleasePackHelp": "ⓘ", "UploadR2StatusHelp": "ⓘ",
		"UploadSelectedHelp": "ⓘ", "PreviewReleaseManifestHelp": "ⓘ",
		"AddMoreLevels": "Add More Levels"
	}
	return str(captions.get(control_name, control_name.replace("_", " ")))


func _level_number_caption() -> String:
	return "Level: %s" % (str(_level_number) if _manual_level_override else "Auto")


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
	var live := RichTextLabel.new()
	live.name = "RuntimeLiveData"
	live.position = Vector2(1222, 170)
	live.size = Vector2(270, 120)
	live.bbcode_enabled = true
	live.fit_content = true
	live.scroll_active = false
	live.add_theme_font_size_override("font_size", 13)
	live.add_theme_color_override("font_color", Color("#dce8f8"))
	add_child(live)
	for row_index in range(5):
		var row := Label.new()
		row.name = "RuntimeDetailsRow%d" % (row_index + 1)
		row.position = Vector2(1222, 170 + row_index * 28)
		row.size = Vector2(270, 24)
		row.clip_text = true
		row.add_theme_font_size_override("font_size", 11)
		row.add_theme_color_override("font_color", Color("#dce8f8"))
		add_child(row)
		_details_rows.append(row)
	_build_inline_results()
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
	_batch_pause_button = Button.new()
	_batch_pause_button.name = "PauseAfterCurrent"
	_batch_pause_button.text = "Pause after current"
	_batch_pause_button.position = Vector2(10, 80)
	_batch_pause_button.size = Vector2(151, 30)
	_batch_pause_button.focus_mode = Control.FOCUS_ALL
	_batch_pause_button.pressed.connect(_request_batch_pause)
	_batch_pause_button.visible = false
	_activity_panel.add_child(_batch_pause_button)
	_batch_stop_button = Button.new()
	_batch_stop_button.name = "StopAfterCurrent"
	_batch_stop_button.text = "Stop after current"
	_batch_stop_button.position = Vector2(166, 80)
	_batch_stop_button.size = Vector2(158, 30)
	_batch_stop_button.focus_mode = Control.FOCUS_ALL
	_batch_stop_button.pressed.connect(_request_batch_stop)
	_batch_stop_button.visible = false
	_activity_panel.add_child(_batch_stop_button)
	_activity_scroll.position = Vector2(10, 116)
	_activity_scroll.size = Vector2(314, 370)
	_activity_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_activity_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	_activity_panel.add_child(_activity_scroll)
	_activity_rows = VBoxContainer.new()
	_activity_rows.name = "PipelineActivityRows"
	_activity_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_activity_rows.add_theme_constant_override("separation", 4)
	_activity_scroll.add_child(_activity_rows)
	_activity_panel.visible = false
	_build_release_pool_dashboard()
	_refresh_activity_header()
	_refresh_live_data()


func _build_release_pool_dashboard() -> void:
	_release_candidate_scroll = ScrollContainer.new()
	_release_candidate_scroll.name = "ReleaseCandidateScroll"
	_release_candidate_scroll.position = Vector2(25, 292)
	_release_candidate_scroll.size = Vector2(335, 480)
	_release_candidate_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_release_candidate_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	_release_candidate_scroll.visible = false
	add_child(_release_candidate_scroll)
	_release_candidate_rows = VBoxContainer.new()
	_release_candidate_rows.name = "ReleaseCandidateRows"
	_release_candidate_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_release_candidate_rows.add_theme_constant_override("separation", 3)
	_release_candidate_scroll.add_child(_release_candidate_rows)
	_release_activity_title = Label.new()
	_release_activity_title.name = "ReleasePoolActivityTitle"
	_release_activity_title.position = Vector2(1207, 774)
	_release_activity_title.size = Vector2(291, 20)
	_release_activity_title.text = "RELEASE POOL ACTIVITY"
	_release_activity_title.add_theme_font_size_override("font_size", 11)
	_release_activity_title.add_theme_color_override("font_color", Color("#91a7c5"))
	_release_activity_title.visible = false
	add_child(_release_activity_title)
	_release_activity_scroll = ScrollContainer.new()
	_release_activity_scroll.name = "ReleasePoolActivityScroll"
	_release_activity_scroll.position = Vector2(1207, 796)
	_release_activity_scroll.size = Vector2(291, 128)
	_release_activity_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_release_activity_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	_release_activity_scroll.visible = false
	add_child(_release_activity_scroll)
	_release_activity_rows = VBoxContainer.new()
	_release_activity_rows.name = "ReleasePoolActivityRows"
	_release_activity_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_release_activity_rows.add_theme_constant_override("separation", 4)
	_release_activity_scroll.add_child(_release_activity_rows)
	_release_help_dialog = AcceptDialog.new()
	_release_help_dialog.name = "ReleasePoolActionHelp"
	_release_help_dialog.title = "Release Pool Help"
	_release_help_dialog.dialog_text = ""
	_release_help_dialog.ok_button_text = "Close"
	add_child(_release_help_dialog)


func _append_release_pool_activity(action: String, state: String, detail: String, candidate_ids: Array = []) -> void:
	var timestamp := Time.get_datetime_string_from_system(true, true)
	var selected := candidate_ids.duplicate(true) if not candidate_ids.is_empty() else _selected_release_ids.duplicate()
	var full_text := "%s | %s | %s | target=%s | candidates=%s | %s" % [
		timestamp, action, state, _release_target, ", ".join(selected), detail
	]
	_release_activity_events.append({
		"timestamp_utc": timestamp,
		"action": action,
		"state": state,
		"target": _release_target,
		"candidate_ids": selected,
		"detail": detail,
		"full_text": full_text,
	})
	if _release_activity_events.size() > 200:
		_release_activity_events.pop_front()
	_refresh_release_pool_activity()


func _release_activity_result_detail(result: Dictionary) -> String:
	var safe := {}
	for key in ["state", "disposition", "target", "manifest_sha256", "candidate_manifest_sha256", "content_version", "receipt_id", "candidate_count", "error", "reason"]:
		if result.has(key):
			var value := str(result.get(key, ""))
			if key in ["error", "reason"]:
				var redact := RegEx.new()
				redact.compile("(?i)(token|secret|password|authorization)(\\s*[:=]\\s*)[^\\s,;]+")
				value = redact.sub(value, "$1$2[redacted]", true)
			safe[key] = value
	return JSON.stringify(safe)


func _refresh_release_pool_activity() -> void:
	if _release_activity_rows == null:
		return
	var scroll := _release_activity_scroll.get_v_scroll_bar() if _release_activity_scroll != null else null
	var follow_tail := scroll == null or _release_activity_scroll.scroll_vertical >= scroll.max_value - 2
	for child in _release_activity_rows.get_children():
		child.queue_free()
	if _release_activity_events.is_empty():
		var empty := Label.new()
		empty.text = "No Release Pool actions in this session."
		empty.custom_minimum_size.y = 32
		empty.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		empty.add_theme_font_size_override("font_size", 10)
		_release_activity_rows.add_child(empty)
	else:
		for event in _release_activity_events:
			var row := RichTextLabel.new()
			row.bbcode_enabled = false
			row.selection_enabled = true
			row.fit_content = true
			row.scroll_active = false
			row.custom_minimum_size = Vector2(265, 40)
			row.text = str(event.get("full_text", ""))
			row.tooltip_text = row.text
			row.add_theme_font_size_override("normal_font_size", 10)
			_release_activity_rows.add_child(row)
	if follow_tail and _release_activity_scroll != null:
		call_deferred("_scroll_release_pool_activity_to_tail")


func _scroll_release_pool_activity_to_tail() -> void:
	if _release_activity_scroll != null:
		_release_activity_scroll.scroll_vertical = int(_release_activity_scroll.get_v_scroll_bar().max_value)


func _build_inline_results() -> void:
	_results_panel = Panel.new()
	_results_panel.name = "LevelFactoryInlineResults"
	_results_panel.position = Vector2(1207, 410)
	_results_panel.size = Vector2(291, 500)
	_results_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	_results_panel.visible = false
	_results_panel.add_theme_stylebox_override("panel", _control_style(Color("#0e192a"), Color("#30415e")))
	add_child(_results_panel)
	var layout := VBoxContainer.new()
	layout.name = "InlineResultsLayout"
	layout.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layout.offset_left = 8
	layout.offset_top = 8
	layout.offset_right = -8
	layout.offset_bottom = -8
	layout.add_theme_constant_override("separation", 6)
	_results_panel.add_child(layout)
	_results_summary = Label.new()
	_results_summary.name = "InlineResultsSummary"
	_results_summary.custom_minimum_size = Vector2(0, 34)
	_results_summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_results_summary.add_theme_font_size_override("font_size", 11)
	_results_summary.add_theme_color_override("font_color", Color("#dce8f8"))
	layout.add_child(_results_summary)
	_results_nav = HBoxContainer.new()
	_results_nav.name = "ReplayNavigation"
	_results_nav.add_theme_constant_override("separation", 3)
	for definition in [["First", -2147483647], ["Previous", -1], ["Next", 1], ["Last", 2147483647]]:
		var button := Button.new()
		button.name = str(definition[0])
		button.text = str(definition[0])
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.custom_minimum_size = Vector2(0, 32)
		button.focus_mode = Control.FOCUS_ALL
		button.pressed.connect(_on_replay_navigation.bind(int(definition[1])))
		_results_nav.add_child(button)
	layout.add_child(_results_nav)
	_results_scroll = ScrollContainer.new()
	_results_scroll.name = "InlineResultsScroll"
	_results_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_results_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_results_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_results_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	layout.add_child(_results_scroll)
	_results_rows = VBoxContainer.new()
	_results_rows.name = "InlineResultsRows"
	_results_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_results_rows.add_theme_constant_override("separation", 5)
	_results_scroll.add_child(_results_rows)
	_results_nav.visible = false


func _add_result_row(text_value: String, tooltip: String = "") -> Label:
	var row := Label.new()
	row.text = text_value
	row.tooltip_text = tooltip if not tooltip.is_empty() else text_value
	row.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.custom_minimum_size = Vector2(0, 22)
	row.add_theme_font_size_override("font_size", 11)
	row.add_theme_color_override("font_color", Color("#dce8f8"))
	_results_rows.add_child(row)
	return row


func _add_supply_batch_row(color_id: String, amount: int) -> void:
	var line := HBoxContainer.new()
	line.name = "SupplyBatch_%s" % color_id
	line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	line.add_theme_constant_override("separation", 7)
	var swatch := ColorRect.new()
	swatch.name = "CanonicalColorSwatch"
	swatch.custom_minimum_size = Vector2(13, 13)
	swatch.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_ensure_canonical_palette_loaded()
	if _canonical_palette_hex_by_id.has(color_id):
		swatch.color = Color(str(_canonical_palette_hex_by_id[color_id]))
	else:
		swatch.color = Color("#7f8792")
	line.add_child(swatch)
	var caption := Label.new()
	caption.text = "%s × %d" % [color_id, amount]
	caption.tooltip_text = "Canonical palette color %s, quantity %d" % [color_id, amount]
	caption.add_theme_font_size_override("font_size", 11)
	caption.add_theme_color_override("font_color", Color("#dce8f8"))
	line.add_child(caption)
	_results_rows.add_child(line)


func _clear_result_rows() -> void:
	if _results_rows == null:
		return
	for child in _results_rows.get_children():
		_results_rows.remove_child(child)
		child.queue_free()


func _on_replay_navigation(direction: int) -> void:
	if direction == -2147483647:
		_set_replay_step(0)
	elif direction == 2147483647:
		_set_replay_step(_replay_trace.size() - 1)
	else:
		_set_replay_step(_replay_step + direction)


func _update_live_chrome() -> void:
	for node_name in ["RuntimeLeftPanel", "RuntimeCanvasPanel", "RuntimeDetailsPanel", "RuntimeBottomStrip"]:
		var panel := get_node_or_null(node_name) as Control
		if panel != null: panel.visible = true
	var title := get_node_or_null("RuntimeTitle") as Label
	if title != null: title.text = "SCRUBBOTS  /  " + _screen
	if _activity_panel != null: _activity_panel.visible = _screen == "LEVEL FACTORY"
	if _release_candidate_scroll != null: _release_candidate_scroll.visible = _screen == "RELEASE POOL"
	if _release_activity_title != null: _release_activity_title.visible = _screen == "RELEASE POOL"
	if _release_activity_scroll != null: _release_activity_scroll.visible = _screen == "RELEASE POOL"
	if _preview_host != null:
		_preview_host.position = Vector2(401, 160)
		_preview_host.size = Vector2(780, 640)
	_refresh_live_data()
	_apply_responsive_layout()


func _refresh_live_data() -> void:
	var live := get_node_or_null("RuntimeLiveData") as RichTextLabel
	if live == null: return
	var level_factory_screen := _screen == "LEVEL FACTORY"
	live.visible = not level_factory_screen
	for row in _details_rows:
		row.visible = level_factory_screen
	var selected_source_text := ""
	if _screen == "LEVEL FACTORY" and not _selected_import_source_id.is_empty():
		selected_source_text = _selected_import_filename()
	if _screen == "PIXEL ART":
		_ensure_canonical_palette_loaded()
		var provider_caption := "PIXELLAB · Pro Flash" if _provider_model == "PIXELLAB" else _provider_model
		var palette_markup := "\nPalette V3 LOCKED  "
		var palette_tooltip := "Canonical palette V3 · API target palette + exact local pixel validation"
		for color in _canonical_palette_colors:
			if color is Dictionary:
				var swatch_hex := str(color.get("hex", "#000000"))
				palette_markup += "[color=%s]■[/color]" % swatch_hex
				palette_tooltip += "\n%s %s" % [str(color.get("id", "")), swatch_hex]
		live.text = "Provider: %s\nMode: %s\nCanvas: %d × %d\nBatch: %d complete · %d failed · %d remaining%s" % [provider_caption, _generation_mode, _width, _height, _semantic_progress.completed, _semantic_progress.failed, _semantic_progress.remaining, palette_markup]
		live.tooltip_text = palette_tooltip
	elif _screen == "LEVEL FACTORY":
		var primary: Dictionary = _last_pipeline.get("primary", {})
		var monitor_failed := str(_last_pipeline.get("studio_monitor_validation", "")) == "FAILED_CLOSED"
		var selected_run := str(_last_pipeline.get("source_id", "")) == _selected_import_source_id
		var active_run := _operation_running and _activity_source_id == _selected_import_source_id
		var batch_following := not _batch_follow_item.is_empty() and str(_batch_follow_item.get("source_id", "")) == _selected_import_source_id and not _batch_follow_token.is_empty()
		var batch_item_state := str(_batch_follow_item.get("status", "")) if batch_following else ""
		if batch_following and batch_item_state == "RUNNING" and str(_batch_snapshot.get("state", "")) in ["PAUSED", "INTERRUPTED"]:
			batch_item_state = str(_batch_snapshot.get("state", ""))
		var batch_active := batch_following and _operation_running and str(_batch_snapshot.get("state", "")) == "RUNNING"
		var pipeline_state := "RUNNING" if active_run else "ERROR" if monitor_failed else str(_last_pipeline.get("disposition", _last_pipeline.get("state", "SOURCE_ONLY · Awaiting run"))) if selected_run else "SOURCE_ONLY · Awaiting run"
		var pipeline_reason := "Pipeline: Running for selected source" if active_run else str(_last_pipeline.get("studio_monitor_reason", _pipeline_stop_reason(_last_pipeline))) if monitor_failed else _pipeline_stop_reason(_last_pipeline)
		var solver_text := "RUNNING" if active_run else "ERROR" if monitor_failed else str(primary.get("state", pipeline_state)) if selected_run and not primary.is_empty() else pipeline_state
		var replay_text := str(primary.get("acceptance", {}).get("replay", "—")) if not active_run and selected_run and not primary.is_empty() and not monitor_failed else "—"
		var difficulty_text := str(primary.get("difficulty", {}).get("class", "—")) if not active_run and selected_run and not primary.is_empty() and not monitor_failed else "—"
		var columns := int(primary.get("column_count", _column_count)) if selected_run and not primary.is_empty() else _selected_batch_column()
		var pool_status := _owner_review_status if not _owner_review_status.is_empty() else "—"
		var batch_caption := ""
		if not _batch_snapshot.is_empty():
			var counts_value: Variant = _batch_snapshot.get("counts", {})
			var counts: Dictionary = counts_value if counts_value is Dictionary else {}
			batch_caption = "%d loaded / %d job · %d READY · %d failed" % [_gameplay_sources.size(), int(counts.get("total", 0)), int(counts.get("ready", 0)), int(counts.get("failed", 0))]
		if batch_following:
			var item_release: Dictionary = _batch_follow_item.get("release_pool", {})
			var follow_primary: Dictionary = _batch_follow_pipeline.get("primary", {})
			pipeline_state = "RUNNING" if batch_active else batch_item_state if not batch_item_state.is_empty() else str(_batch_snapshot.get("state", "UNKNOWN"))
			pipeline_reason = str(_batch_follow_item.get("reason", ""))
			solver_text = str(follow_primary.get("state", "RUNNING" if batch_active else "—"))
			replay_text = str(follow_primary.get("acceptance", {}).get("replay", "—"))
			difficulty_text = str(follow_primary.get("difficulty", {}).get("class", "—"))
			columns = int(_batch_follow_item.get("column_count", 0))
			pool_status = str(item_release.get("disposition", "NOT ENTERED" if batch_item_state == "READY" else "—"))
			batch_caption = "%d/%d · %s · %s" % [int(_batch_follow_item.get("index", 0)) + 1, int(_batch_snapshot.get("counts", {}).get("total", 0)), batch_item_state if not batch_item_state.is_empty() else "RUNNING", str(_batch_follow_item.get("run_id", "no run ID"))]
		var facts := [
			"Level %s   |   Columns %s" % ["Auto" if not _manual_level_override else str(_level_number), str(columns) if columns > 0 else "—"],
			"Background %s   |   Pipeline %s" % [_background_intent, pipeline_state.left(11)],
			"Solver %s   |   Replay %s" % [solver_text.left(10), replay_text.left(8)],
			"Difficulty %s   |   Pool %s" % [difficulty_text.left(10), pool_status.left(12)],
			"PNG %s   |   Batch %s" % [selected_source_text.left(23) if not selected_source_text.is_empty() else "—", batch_caption if not batch_caption.is_empty() else "—"],
		]
		for row_index in range(_details_rows.size()):
			var row := _details_rows[row_index]
			row.text = facts[row_index]
			row.tooltip_text = facts[row_index] + ("\n" + pipeline_reason if row_index == 1 and not pipeline_reason.is_empty() else "")
		if _results_panel != null:
			_results_panel.visible = not _results_mode.is_empty()
	else:
		if _results_panel != null: _results_panel.visible = false
		var entries: Array = _release_pool.get("entries", [])
		live.text = "READY levels: %d\nVisible: %d\nSelected: %d\nTarget: %s\nPreflight: %s" % [entries.size(), _visible_release_ids.size(), _selected_release_ids.size(), _release_target, str(_release_pool.get("publish_preflight", {}).get("state", "Not run"))]
	_refresh_run_button_caption()
	_refresh_runtime_cards()


func _ensure_canonical_palette_loaded() -> void:
	if not _canonical_palette_hex_by_id.is_empty():
		return
	# Read the canonical JSON locally; do not spawn Python or block a screen switch.
	var palette_path := ProjectSettings.globalize_path("res://../data/palette/scrubbots_palette_v3.json")
	var palette_file := FileAccess.open(palette_path, FileAccess.READ)
	if palette_file == null:
		return
	var palette_value: Variant = JSON.parse_string(palette_file.get_as_text())
	if not palette_value is Dictionary or int(palette_value.get("version", 0)) != 3 or palette_value.get("ownerLocked") != true:
		return
	var colors: Variant = palette_value.get("colors", [])
	if not colors is Array or colors.size() != 16:
		return
	_canonical_palette_colors = colors.duplicate(true)
	for color in _canonical_palette_colors:
		if color is Dictionary and str(color.get("id", "")).begins_with("C"):
			_canonical_palette_hex_by_id[str(color.get("id", ""))] = str(color.get("hex", ""))


func _refresh_run_button_caption() -> void:
	var button := get_node_or_null("RunLevelPipeline") as Button
	if button == null or _screen != "LEVEL FACTORY":
		return
	var imported_count := _gameplay_sources.size()
	var batch_mode := imported_count > 1
	if _operation_running and not _batch_job_id.is_empty():
		var counts_value: Variant = _batch_snapshot.get("counts", {})
		var counts: Dictionary = counts_value if counts_value is Dictionary else {}
		var completed := int(counts.get("ready", 0)) + int(counts.get("failed", 0)) + int(counts.get("rejected", 0)) + int(counts.get("skipped", 0))
		button.text = "Running %d/%d" % [completed + (1 if _batch_snapshot.get("current_index") != null else 0), int(counts.get("total", imported_count))]
		button.disabled = true
	elif batch_mode:
		var state := str(_batch_snapshot.get("state", ""))
		var counts_value: Variant = _batch_snapshot.get("counts", {})
		var counts: Dictionary = counts_value if counts_value is Dictionary else {}
		if _batch_job_source_mismatch:
			button.text = "Batch mismatch"
			button.disabled = true
		elif state in ["QUEUED", "PAUSED", "STOPPED", "INTERRUPTED", "RUNNING"] and _batch_job_matches_loaded_sources():
			button.text = "Review & Resume Legacy Batch" if _batch_legacy_reconciliation else "Resume Batch · %d remaining" % int(counts.get("remaining", 0))
			button.disabled = false
		elif state == "COMPLETE" and (int(counts.get("failed", 0)) > 0 or int(counts.get("rejected", 0)) > 0):
			if int(counts.get("failed", 0)) > 0 and _batch_job_matches_loaded_sources():
				button.text = "Retry Failed (%d)" % int(counts.get("failed", 0))
				button.disabled = false
			else:
				button.text = "Finished With Failures · %d READY" % int(counts.get("ready", 0))
				button.disabled = true
		elif state == "COMPLETE":
			if _batch_job_matches_loaded_sources():
				if int(counts.get("skipped", 0)) > 0:
					button.text = "Batch Complete · %d READY · %d Skipped" % [int(counts.get("ready", 0)), int(counts.get("skipped", 0))]
				else:
					button.text = "Retry Finished · %d READY" % int(counts.get("ready", 0)) if _batch_snapshot.has("parent_job_id") else "Loaded Batch READY (%d)" % int(counts.get("ready", 0))
				button.disabled = true
			else:
				button.text = "Run Entire Loaded Batch (%d)" % imported_count
				button.disabled = false
		else:
			button.text = "Run Entire Loaded Batch (%d)" % imported_count
			button.disabled = false
	else:
		button.text = "Run Pipeline"
		button.disabled = false
	if _batch_pause_button != null:
		_batch_pause_button.visible = _operation_running and not _batch_job_id.is_empty()
	if _batch_stop_button != null:
		_batch_stop_button.visible = _operation_running and not _batch_job_id.is_empty()


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
		var image := Image.new()
		if image.load(png_path) != OK:
			continue
		source_by_id[catalog_source_id] = {
			"path": png_path, "source_id": catalog_source_id, "source_sha256": expected_sha,
			"source_record_sha256": _source_record_sha256_for_id(catalog_source_id),
			"disposition": "SOURCE_ONLY", "display_filename": str(source.get("original_filename", "image.png")),
			"width": image.get_width(), "height": image.get_height()
		}
	# Startup restore needs only the source catalog. owner-pages also validates
	# every pipeline, candidate, failure, and Release Pool entry; running it here
	# synchronously blocks Godot's main thread and is unrelated to source display.
	# Preserve the catalog's own order and let the explicit batch-composite lookup
	# below restore batch/job state when an exact source match exists.
	var order_ids: Array[String] = []
	_source_batch_by_id.clear()
	for source_variant in sources:
		if source_variant is Dictionary:
			var remaining_source_id := str(source_variant.get("source_id", ""))
			if source_by_id.has(remaining_source_id) and remaining_source_id not in order_ids:
				order_ids.append(remaining_source_id)
	for ordered_source_id in order_ids:
		_upsert_imported_source(source_by_id[ordered_source_id])
	_refresh_gameplay_sources()
	if _gameplay_sources.is_empty():
		return
	var selected_is_gameplay := _gameplay_source_index(_selected_import_source_id) >= 0
	if not selected_is_gameplay:
		_selected_import_source_id = _PINNED_002_SOURCE_ID if _gameplay_source_index(_PINNED_002_SOURCE_ID) >= 0 else str(_gameplay_sources[0].get("source_id", ""))
	_select_imported_source_by_id(_selected_import_source_id)
	_restore_loaded_png_batch_readonly()
	_refresh_runtime_cards()


func _restore_loaded_png_batch_readonly() -> void:
	if _gateway == null or _gameplay_sources.is_empty():
		return
	var source_ids: Array[String] = []
	for source in _gameplay_sources:
		var source_id := str(source.get("source_id", ""))
		if source_id.is_empty() or source_id in source_ids:
			return
		source_ids.append(source_id)
	var resolved := _extension("loaded-png-batch-find", {"source_ids": source_ids})
	var composite_value: Variant = resolved.get("batch", {})
	var composite: Dictionary = composite_value if composite_value is Dictionary else {}
	var resolution := str(resolved.get("disposition", ""))
	if resolution not in ["MATCHED", "LEGACY_EXACT_MATCH"] or composite.is_empty():
		if resolution not in ["NO_MATCHING_COMPOSITE", ""]:
			_batch_job_source_mismatch = true
			_report("Loaded PNG batch provenance could not be verified; resume and retry are blocked.")
		_refresh_run_button_caption()
		return
	_batch_legacy_reconciliation = resolution == "LEGACY_EXACT_MATCH"
	_batch_composite_snapshot = composite
	_batch_import_id = str(composite.get("batch_id", ""))
	if _batch_import_id.is_empty():
		_batch_composite_snapshot.clear()
		return
	var latest := _extension("png-batch-latest", {"batch_id": _batch_import_id})
	var job_value: Variant = latest.get("job", {})
	var job: Dictionary = job_value if job_value is Dictionary else {}
	_batch_job_source_mismatch = str(latest.get("disposition", "")) == "BATCH_JOB_SOURCE_MISMATCH"
	if _batch_job_source_mismatch:
		_batch_job_id = ""
		_batch_snapshot.clear()
		_report("A persisted PNG job has a different composite authority; it was not resumed.")
		_refresh_run_button_caption()
		return
	if job.is_empty():
		_batch_job_id = ""
		_batch_snapshot.clear()
		_refresh_run_button_caption()
		return
	_batch_snapshot = job.duplicate(true)
	var counts_value: Variant = _batch_snapshot.get("counts", {})
	if not counts_value is Dictionary:
		# Keep malformed optional backend counts local and empty; never mutate saved job data.
		_batch_snapshot["counts"] = {}
	_batch_job_id = str(job.get("job_id", ""))
	if str(job.get("state", "")) == "RUNNING":
		# Display the crash state locally. The durable job remains unchanged until
		# the owner explicitly presses Resume Batch.
		_batch_snapshot["state"] = "INTERRUPTED"
		_activity_stage = "INTERRUPTED"
		_activity_backend_disposition = "INTERRUPTED"
		_activity_terminal_state = "INTERRUPTED"
		_activity_message = "Previous batch worker stopped with the application. Resume is available; no solver was started."
	elif str(job.get("state", "")) in ["PAUSED", "STOPPED", "QUEUED"]:
		_activity_stage = str(job.get("state", ""))
		_activity_backend_disposition = _activity_stage
		_activity_terminal_state = _activity_stage
		_activity_message = "Batch is %s. Press Resume Batch to continue this saved job." % _activity_stage.to_lower()
	else:
		var restored_counts_value: Variant = job.get("counts", {})
		var counts: Dictionary = restored_counts_value if restored_counts_value is Dictionary else {}
		_activity_stage = "FINISHED WITH FAILURES" if int(counts.get("failed", 0)) > 0 or int(counts.get("rejected", 0)) > 0 else "READY"
		_activity_backend_disposition = _activity_stage
		_activity_terminal_state = _activity_stage
		_activity_message = "Restored %s · %d/%d READY · %d FAILED · no solver was run." % [str(job.get("state", "")), int(counts.get("ready", 0)), int(counts.get("total", 0)), int(counts.get("failed", 0))]
	_sync_verified_batch_follow(_batch_snapshot)
	_record_verified_batch_item_progress(_batch_snapshot)
	_render_batch_item_results(_batch_snapshot)
	_refresh_activity_header()
	_refresh_run_button_caption()


func _refresh_runtime_cards() -> void:
	_refresh_gameplay_sources()
	_request_candidate_inbox_refresh()
	var inbox := _candidate_inbox_cache
	var candidates: Array = inbox.get("candidates", [])
	var level_sources := _batch_ordered_gameplay_sources()
	var pixel_slots := ["ArtworkVariation1", "ArtworkVariation2", "ArtworkVariation3"]
	var level_slots := ["LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5"]
	for index in range(pixel_slots.size()):
		if index < candidates.size():
			var candidate: Dictionary = candidates[index]
			var caption := str(candidate.get("candidate_id", "Artwork %d" % (index + 1)))
			var image_path := str(candidate.get("artwork_path", ""))
			_set_runtime_button(pixel_slots[index], caption.left(18), image_path)
		else:
			_set_runtime_button(pixel_slots[index], "No artwork", "")
	var max_start := maxi(0, level_sources.size() - level_slots.size())
	_imported_window_start = clampi(_imported_window_start, 0, max_start)
	var bottom_heading := get_node_or_null("RuntimeBottomHeading") as Label
	if bottom_heading != null:
		bottom_heading.text = "VARIATIONS  /  RECENT ITEMS · %d PNG" % _gameplay_sources.size() if _screen == "LEVEL FACTORY" else "SELECTED FOR RELEASE" if _screen == "RELEASE POOL" else "VARIATIONS  /  RECENT ITEMS"
	for index in range(level_slots.size()):
		var source_index := _imported_window_start + index
		var button := get_node_or_null(level_slots[index]) as Button
		if source_index < level_sources.size():
			var imported: Dictionary = level_sources[source_index]
			var source_id := str(imported.get("source_id", ""))
			var filename := str(imported.get("display_filename", "image.png"))
			var disposition := str(imported.get("disposition", "IMPORTED"))
			var status_caption := _runtime_source_status_caption(source_id, disposition)
			var caption := ("● " if source_id == _selected_import_source_id else "") + filename.get_basename().left(9) + "\n" + status_caption
			_set_runtime_button(level_slots[index], caption, str(imported.get("path", "")))
			if button != null:
				button.tooltip_text = _runtime_source_status_tooltip(imported, filename, source_id, disposition)
				button.disabled = _operation_running and not _batch_job_id.is_empty()
		else:
			if button != null:
				button.disabled = true
			_set_runtime_button(level_slots[index], "No PNG", "")
	if _gameplay_sources.is_empty():
		for index in range(level_slots.size()):
			var button := get_node_or_null(level_slots[index]) as Button
			if index < candidates.size():
				var candidate: Dictionary = candidates[index]
				_set_runtime_button(level_slots[index], str(candidate.get("candidate_id", "Level %d" % (index + 1))).left(12), str(candidate.get("artwork_path", "")))
				if button != null:
					button.disabled = false
			else:
				if button != null:
					button.disabled = true
				_set_runtime_button(level_slots[index], "No artwork", "")
	_refresh_release_candidate_rows()
	var entries: Array = _release_pool.get("entries", [])
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
			var card_button := get_node_or_null(card) as Button
			if card_button != null:
				card_button.disabled = index >= _selected_release_ids.size()
		var remove_button := get_node_or_null("RemoveSelected%d" % (index + 1)) as Button
		if remove_button != null:
			remove_button.disabled = index >= _selected_release_ids.size()
	var add_more := get_node_or_null("AddMoreLevels") as Button
	if add_more != null:
		add_more.disabled = false


func _runtime_source_status_caption(source_id: String, disposition: String) -> String:
	var item := _verified_batch_item_for_source(source_id)
	if item.is_empty():
		return "UNVERIFIED" if _batch_snapshot.has("items") and _batch_job_contains_source(source_id) else "REUSED" if disposition == "ALREADY_IMPORTED" else disposition
	var status := str(item.get("status", ""))
	if str(_batch_snapshot.get("state", "")) == "INTERRUPTED" and status == "RUNNING" and not _operation_running:
		status = "INTERRUPTED"
	elif str(_batch_snapshot.get("state", "")) == "PAUSED" and status == "RUNNING":
		status = "PAUSED"
	if status == "READY" and bool(item.get("reused_existing_ready", false)):
		return "READY · REUSED PROOF · %d COL" % int(item.get("column_count", 0))
	return "%s · %d COL" % [status, int(item.get("column_count", 0))]


func _runtime_source_status_tooltip(imported: Dictionary, filename: String, source_id: String, disposition: String) -> String:
	var item := _verified_batch_item_for_source(source_id)
	if item.is_empty():
		return "%s\n%s\n%s" % [filename, "UNVERIFIED BATCH ITEM" if _batch_job_contains_source(source_id) else disposition, _wrap_identity(source_id, 24)]
	var reason := str(item.get("reason", ""))
	var details := "%s\nBatch %s · item %d\n%s · %d columns · attempt %s · run %s" % [filename, str(_batch_snapshot.get("job_id", "")), int(item.get("index", 0)) + 1, str(item.get("status", "")), int(item.get("column_count", 0)), str(item.get("attempt_id", "reused proof")), str(item.get("run_id", "—"))]
	if bool(item.get("reused_existing_ready", false)):
		details += "\nREADY · REUSED PROOF"
	if not reason.is_empty():
		details += "\nReason: %s" % reason
	return "%s\n%s" % [details, _wrap_identity(source_id, 24)]


func _batch_job_contains_source(source_id: String) -> bool:
	for item_variant in _batch_snapshot.get("items", []):
		if item_variant is Dictionary and str(item_variant.get("source_id", "")) == source_id:
			return true
	return false


func _verified_batch_item_for_source(source_id: String) -> Dictionary:
	if (source_id.is_empty() or _batch_snapshot.is_empty() or _batch_job_source_mismatch
			or not _batch_job_matches_loaded_sources()):
		return {}
	var items: Array = _batch_snapshot.get("items", [])
	for index in range(items.size()):
		if not items[index] is Dictionary:
			continue
		var item: Dictionary = items[index]
		if str(item.get("source_id", "")) != source_id:
			continue
		var source_index := _gameplay_source_index(source_id)
		if source_index < 0:
			return {}
		var source: Dictionary = _gameplay_sources[source_index]
		var source_sha := str(item.get("source_sha256", ""))
		var record_sha := str(item.get("source_record_sha256", ""))
		var status := str(item.get("status", ""))
		var reused_ready := status == "READY" and bool(item.get("reused_existing_ready", false)) and not str(item.get("run_id", "")).is_empty()
		var attempt_value: Variant = item.get("attempt_id", "")
		var attempt_ok := (attempt_value != null and not str(attempt_value).is_empty()) or reused_ready
		if (str(item.get("job_id", _batch_snapshot.get("job_id", ""))) != str(_batch_snapshot.get("job_id", ""))
				or int(item.get("index", -1)) != index
				or source_id.trim_prefix("owner-upload-") != source_sha
				or str(source.get("source_sha256", source_id.trim_prefix("owner-upload-"))) != source_sha
				or str(source.get("source_record_sha256", "")) != record_sha
				or record_sha.length() != 64 or not attempt_ok
				or int(item.get("column_count", 0)) not in [3, 4, 5]
				or status not in ["QUEUED", "RUNNING", "READY", "FAILED", "REJECTED", "SKIPPED"]):
			return {}
		if status == "READY" and str(item.get("run_id", "")).is_empty():
			return {}
		if _source_png_sha256(str(source.get("path", ""))) != source_sha:
			return {}
		return item.duplicate(true)
	return {}


func _build_master_controls() -> void:
	# Header tabs are explicit, visible Godot Button controls.
	_place_control("PixelArtTab", Rect2(365, 22, 255, 72), _show_screen.bind("PIXEL ART"))
	_place_control("LevelFactoryTab", Rect2(633, 22, 270, 72), _show_screen.bind("LEVEL FACTORY"))
	_place_control("ReleasePoolTab", Rect2(918, 22, 270, 72), _show_screen.bind("RELEASE POOL"))
	_place_control("SettingsGear", Rect2(1320, 15, 55, 60), _open_settings)
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
	_place_control("PreviewReplay", Rect2(1207, 316, 142, 38), _preview_replay)
	_place_control("ExpandSupplyPlan", Rect2(1356, 316, 142, 38), _toggle_supply_plan)
	_place_control("SolveAgain", Rect2(1207, 362, 94, 38), _solve_again)
	_place_control("LevelVariation1", Rect2(405, 864, 88, 58), _select_variation.bind(0))
	_place_control("LevelVariation2", Rect2(501, 864, 88, 58), _select_variation.bind(1))
	_place_control("LevelVariation3", Rect2(597, 864, 88, 58), _select_variation.bind(2))
	_place_control("LevelVariation4", Rect2(693, 864, 88, 58), _select_variation.bind(3))
	_place_control("LevelVariation5", Rect2(789, 864, 88, 58), _select_variation.bind(4))
	_place_control("AcceptLevel", Rect2(1304, 362, 94, 38), _review_candidate.bind("ACCEPT"))
	_place_control("RejectLevel", Rect2(1401, 362, 97, 38), _review_candidate.bind("REJECT"))
	# RELEASE POOL uses canonical pool, campaign, and staging operations.
	_place_control("RefreshReleasePool", Rect2(27, 202, 330, 40), _refresh_release_pool)
	_place_control("ReleaseSearch", Rect2(25, 154, 335, 44), _edit_release_search)
	_place_control("DifficultyFilter", Rect2(25, 249, 165, 38), _open_release_filters)
	_place_control("ColumnsFilter", Rect2(196, 249, 164, 38), _open_release_filters)
	_place_control("ManageSelection", Rect2(25, 784, 335, 36), _manage_release_selection)
	_place_control("SelectAllRelease", Rect2(25, 826, 164, 36), _select_all_release)
	_place_control("ClearRelease", Rect2(196, 826, 164, 36), _clear_release_selection)
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
	_place_release_help_control("ReleaseStagingHelp", "ReleaseStaging", Rect2(1466, 398, 32, 36))
	_place_release_help_control("ReleaseProductionHelp", "ReleaseProduction", Rect2(1466, 438, 32, 36))
	_place_release_help_control("PreflightReleaseHelp", "PreflightRelease", Rect2(1466, 485, 32, 40))
	_place_release_help_control("ValidateReleaseAssetsHelp", "ValidateReleaseAssets", Rect2(1466, 530, 32, 36))
	_place_release_help_control("BuildReleasePackHelp", "BuildReleasePack", Rect2(1466, 568, 32, 36))
	_place_release_help_control("UploadR2StatusHelp", "UploadR2Status", Rect2(1466, 606, 32, 36))
	_place_release_help_control("UploadSelectedHelp", "UploadSelected", Rect2(1466, 648, 32, 54))
	_place_release_help_control("PreviewReleaseManifestHelp", "PreviewReleaseManifest", Rect2(1466, 713, 32, 50))
	_update_master_control_visibility()


func _place_release_help_control(node_name: String, action_name: String, rect: Rect2) -> void:
	var info := _place_control(node_name, rect, _show_release_action_help.bind(action_name))
	info.text = "ⓘ"
	info.tooltip_text = "Help: %s" % _control_caption(action_name)
	info.add_theme_font_size_override("font_size", 14)


func _show_release_action_help(action_name: String) -> void:
	var descriptions := {
		"ReleaseStaging": "Selects STAGING as the next release target. This does not upload or publish anything.",
		"ReleaseProduction": "Selects PRODUCTION as the target. A real promotion still requires a verified STAGING manifest and explicit owner confirmation.",
		"PreflightRelease": "Runs the canonical release preflight for the currently selected READY candidate IDs and target. A passing result is shown only when returned by the backend.",
		"ValidateReleaseAssets": "Status only: displays the most recent preflight validation state. It does not start asset validation.",
		"BuildReleasePack": "Status only: displays the most recent preflight pack-build state. It does not build or upload a pack.",
		"UploadR2Status": "Status only: displays the most recent preflight upload state. It does not upload to R2.",
		"UploadSelected": "Submits the selected READY candidate IDs to the selected target. STAGING uploads through the canonical publisher; PRODUCTION requires the exact owner-confirmation flow.",
		"PreviewReleaseManifest": "Shows the most recent verified preflight manifest. It does not run preflight or publish; run Preflight separately first."
	}
	var description := str(descriptions.get(action_name, "Shows current Release Pool action information."))
	_append_release_pool_activity("HELP · %s" % _control_caption(action_name), "READ ONLY", description)
	if _release_help_dialog != null:
		_release_help_dialog.title = "%s · Help" % _control_caption(action_name)
		_release_help_dialog.dialog_text = description
		_release_help_dialog.popup_centered(Vector2i(560, 180))


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
	if name != "LEVEL FACTORY":
		_hide_review_dialogs()
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
	if name == "LEVEL FACTORY":
		if not _batch_snapshot.is_empty():
			_sync_verified_batch_follow(_batch_snapshot)
		_refresh_activity_header()
	if name == "RELEASE POOL":
		_refresh_release_pool_activity()


func _update_master_control_visibility() -> void:
	for button in _master_buttons:
		button.text = _control_caption(button.name)
	var shared := ["PixelArtTab", "LevelFactoryTab", "ReleasePoolTab", "SettingsGear", "ZoomOut", "ZoomSlider", "ZoomIn", "ZoomOneToOne", "ZoomFit", "ToggleGrid"]
	var pixel := ["GeneratePixelArt", "BatchCsvSelect", "RunBatch", "Regenerate", "EditPrompt", "AddToLevelFactory", "GenerationPrompt", "RandomSeed", "GenerationStyle", "GenerationSize", "GenerationProvider", "SingleMode", "BatchMode", "BatchCsvPath", "ArtworkVariation1", "ArtworkVariation2", "ArtworkVariation3", "ArtworkCarouselLeft", "ArtworkCarouselRight"]
	var level := ["SelectArtwork", "LevelNumber", "SupplyColumns3", "SupplyColumns4", "SupplyColumns5", "MaxRobotsAuto", "BackgroundIntent", "RunLevelPipeline", "SolveAgain", "PreviewReplay", "ExpandSupplyPlan", "AcceptLevel", "RejectLevel", "LevelVariation1", "LevelVariation2", "LevelVariation3", "LevelVariation4", "LevelVariation5"]
	var release := ["RefreshReleasePool", "ReleaseSearch", "DifficultyFilter", "ColumnsFilter", "ManageSelection", "SelectAllRelease", "ClearRelease", "SelectedReleaseCard1", "SelectedReleaseCard2", "SelectedReleaseCard3", "RemoveSelected1", "RemoveSelected2", "RemoveSelected3", "AddMoreLevels", "ReleaseStaging", "ReleaseProduction", "PreflightRelease", "ValidateReleaseAssets", "BuildReleasePack", "UploadR2Status", "UploadSelected", "PreviewReleaseManifest", "ReleaseStagingHelp", "ReleaseProductionHelp", "PreflightReleaseHelp", "ValidateReleaseAssetsHelp", "BuildReleasePackHelp", "UploadR2StatusHelp", "UploadSelectedHelp", "PreviewReleaseManifestHelp"]
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
	if _release_candidate_scroll != null:
		_release_candidate_scroll.visible = _screen == "RELEASE POOL"
	if _release_activity_title != null:
		_release_activity_title.visible = _screen == "RELEASE POOL"
	if _release_activity_scroll != null:
		_release_activity_scroll.visible = _screen == "RELEASE POOL"
	_refresh_run_button_caption()


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


func _on_file_selected(path: String) -> void:
	if _file_selection_action == "PIXEL_ART_BATCH":
		_generate_batch_csv(path)
		return
	_import_pngs([path])

func _on_files_selected(paths: PackedStringArray) -> void:
	_import_pngs(Array(paths))


func _import_pngs(paths: Array) -> void:
	var result := _extension("batch-import", {"paths": paths})
	var new_batch_id := str(result.get("batch_id", ""))
	if new_batch_id != _batch_import_id and not _operation_running:
		_batch_job_id = ""
		_batch_snapshot.clear()
		_batch_composite_snapshot.clear()
		_batch_job_source_mismatch = false
		_batch_legacy_reconciliation = false
	_batch_import_id = new_batch_id
	for imported_item in result.get("items", []):
		if imported_item is Dictionary and not str(imported_item.get("source_id", "")).is_empty():
			_source_batch_by_id[str(imported_item["source_id"])] = new_batch_id
	# Import selection only refreshes read-only thumbnails. Existing jobs stay bound
	# to their immutable import snapshot; the explicit Run action creates the union.
	if not _operation_running:
		_batch_job_id = ""
		_batch_snapshot.clear()
		_batch_composite_snapshot.clear()
		_batch_job_source_mismatch = false
		_batch_legacy_reconciliation = false
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
		"rejected_count": rejected_count, "batch_id": new_batch_id,
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
	var identity_sha := source_id.trim_prefix("owner-upload-")
	if source_id.begins_with("owner-upload-") and identity_sha.length() == 64:
		record["source_sha256"] = identity_sha
		var canonical_record_sha := _source_record_sha256_for_id(source_id)
		if not canonical_record_sha.is_empty():
			record["source_record_sha256"] = canonical_record_sha
	var image_path := str(record.get("path", ""))
	if int(record.get("width", 0)) <= 0 and not image_path.is_empty():
		var image := Image.new()
		if image.load(image_path) == OK:
			record["width"] = image.get_width()
			record["height"] = image.get_height()
	for index in range(_imported_sources.size()):
		if str(_imported_sources[index].get("source_id", "")) == source_id:
			var existing: Dictionary = _imported_sources[index]
			for key in ["path", "source_sha256", "source_record_sha256", "display_filename", "width", "height"]:
				if not str(record.get(key, "")).is_empty(): existing[key] = record[key]
			existing["disposition"] = record.get("disposition", existing.get("disposition", "IMPORTED"))
			_imported_sources[index] = existing
			_refresh_gameplay_sources()
			return
	_imported_sources.append(record.duplicate(true))
	_refresh_gameplay_sources()


func _source_record_sha256_for_id(source_id: String) -> String:
	if not source_id.begins_with("owner-upload-"):
		return ""
	var source_sha := source_id.trim_prefix("owner-upload-")
	if source_sha.length() != 64:
		return ""
	var app_root := ProjectSettings.globalize_path("res://").path_join("..").simplify_path()
	var relative_record := "level_factory/output/owner-uploads/%s/source.json" % source_id
	var record_paths := [
		app_root.path_join(relative_record),
		app_root.path_join("Release/ScrubBots Factory Studio").path_join(relative_record),
	]
	for record_path in record_paths:
		if not FileAccess.file_exists(record_path):
			continue
		var record_bytes := FileAccess.get_file_as_bytes(record_path)
		var parsed: Variant = JSON.parse_string(record_bytes.get_string_from_utf8())
		if not parsed is Dictionary:
			continue
		if (str(parsed.get("source_id", "")) != source_id
				or str(parsed.get("source_sha256", "")) != source_sha
				or str(parsed.get("immutable_relative_path", "")) != "owner-uploads/%s/source.png" % source_id):
			continue
		var hashing := HashingContext.new()
		if hashing.start(HashingContext.HASH_SHA256) != OK:
			return ""
		hashing.update(record_bytes)
		return hashing.finish().hex_encode()
	return ""


func _refresh_gameplay_sources() -> void:
	_gameplay_sources.clear()
	for source in _imported_sources:
		var width := int(source.get("width", 0))
		var height := int(source.get("height", 0))
		if width >= 20 and width <= 59 and height >= 20 and height <= 59:
			_gameplay_sources.append(source)


func _gameplay_source_index(source_id: String) -> int:
	for index in range(_gameplay_sources.size()):
		if str(_gameplay_sources[index].get("source_id", "")) == source_id:
			return index
	return -1


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
	if _provider_model == "PIXELLAB":
		if _width % 4 != 0 or _height % 4 != 0:
			_report("Pro Flash requires canvas width and height in 4-pixel increments; choose a compatible size first.")
			return
		_confirm_pro_flash_generation()
		return
	var result := _generate_request({"prompt": _prompt, "style": _generation_style, "width": _width, "height": _height, "provider": _provider_model, "seed": _seed, "background_intent": _background_intent})
	_finish_generation(result)


func _confirm_pro_flash_generation() -> void:
	var dialog := ConfirmationDialog.new()
	dialog.title = "Confirm paid PixelLab Pro Flash generation"
	dialog.dialog_text = "This will submit one paid Pro Flash image request (%d × %d). One prior request used 5 credits; actual cost may vary. Network timeouts are not automatically retried." % [_width, _height]
	dialog.confirmed.connect(func():
		if is_instance_valid(dialog): dialog.queue_free()
		_start_pixel_art_worker({"prompt": _prompt, "style": _generation_style, "width": _width, "height": _height, "provider": _provider_model, "seed": _seed, "background_intent": _background_intent})
	)
	dialog.canceled.connect(func(): dialog.queue_free())
	add_child(dialog)
	dialog.popup_centered()


func _start_pixel_art_worker(request: Dictionary) -> void:
	if _gateway == null or _operation_running or _pixel_art_thread != null:
		return
	if not _gateway.has_method("prepare_studio_extension_call") or not _gateway.has_method("execute_prepared_studio_extension_call"):
		_report("PixelLab Pro Flash is unavailable because the local Factory Core gateway is not ready.")
		return
	var operation_id := "%d-%d" % [Time.get_unix_time_from_system(), Time.get_ticks_usec()]
	var payload := {"prompt": request.get("prompt", ""), "style": request.get("style", ""), "provider_id": "PIXELLAB", "provider_model": "PRO_FLASH", "width": request.get("width", 32), "height": request.get("height", 32), "seed": request.get("seed", ""), "background_intent": request.get("background_intent", "TRANSPARENT"), "operation_id": operation_id}
	var prepared: Dictionary = _gateway.call("prepare_studio_extension_call", "semantic-generate", payload)
	if prepared.is_empty():
		_report("PixelLab Pro Flash is unavailable because the local Factory Core cannot start.")
		return
	_prepare_worker_cancel_marker()
	_pixel_art_mutex.lock()
	_pixel_art_worker_done = false
	_pixel_art_worker_result.clear()
	_pixel_art_mutex.unlock()
	_pixel_art_thread = Thread.new()
	var error := _pixel_art_thread.start(Callable(self, "_pixel_art_worker").bind(prepared))
	if error != OK:
		_pixel_art_thread = null
		_finish_worker_cancel_marker()
		_report("PixelLab Pro Flash worker could not start.")
		return
	_operation_running = true
	_semantic_progress = {"completed": 0, "failed": 0, "remaining": 1, "state": "RUNNING"}
	_report("PIXELLAB PRO FLASH · submitting one image · %d × %d · canonical palette V3" % [int(payload.width), int(payload.height)])


func _pixel_art_worker(prepared: Dictionary) -> void:
	var result: Dictionary = _gateway.call("execute_prepared_studio_extension_call", prepared)
	_pixel_art_mutex.lock()
	_pixel_art_worker_result = result
	_pixel_art_worker_done = true
	_pixel_art_mutex.unlock()


func _poll_pixel_art_worker() -> void:
	if _pixel_art_thread == null:
		return
	_pixel_art_mutex.lock()
	var completed := _pixel_art_worker_done
	var result := _pixel_art_worker_result.duplicate(true) if completed else {}
	_pixel_art_mutex.unlock()
	if not completed or _pixel_art_thread.is_alive():
		return
	_pixel_art_thread.wait_to_finish()
	_pixel_art_thread = null
	_finish_worker_cancel_marker()
	_pixel_art_mutex.lock()
	_pixel_art_worker_done = false
	_pixel_art_worker_result.clear()
	_pixel_art_mutex.unlock()
	_operation_running = false
	if str(result.get("state", "")) == "IMPORTED":
		_semantic_progress = {"completed": 1, "failed": 0, "remaining": 0, "state": "READY"}
		_finish_generation(result)
	else:
		_semantic_progress = {"completed": 0, "failed": 1, "remaining": 0, "state": str(result.get("state", "ERROR"))}
		_report("PIXELLAB PRO FLASH · %s · %s" % [str(result.get("state", "ERROR")), str(result.get("error", result.get("reason", "No image was imported.")))])
	if _shutdown_requested:
		get_tree().quit()


func _run_batch() -> void:
	if not _batch_csv_path.is_empty() and str(_semantic_progress.get("state", "")) in ["LIMIT", "UNAVAILABLE", "NEEDS_RETRY"]:
		_generate_batch_csv(_batch_csv_path)
		return
	_open_batch_csv()


func _generate_batch_csv(path: String) -> void:
	if _gateway == null or _operation_running:
		return
	_batch_csv_path = path
	if _provider_model == "PIXELLAB":
		_report("Pro Flash CSV batch is disabled to prevent unconfirmed paid calls. Use one confirmed Generate/Regenerate request at a time.")
		return
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
	if _gameplay_sources.size() > 1:
		if str(_batch_snapshot.get("state", "")) == "COMPLETE" and int(_batch_snapshot.get("counts", {}).get("failed", 0)) > 0 and _batch_job_matches_loaded_sources():
			_retry_failed_png_batch()
			return
		_run_png_batch()
		return
	_run_single_level_pipeline()


func _run_single_level_pipeline() -> void:
	if _gateway == null or _operation_running:
		return
	_activity_source_id = _selected_import_source_id
	if not _pinned_source_preflight_ok:
		_refresh_pinned_source_preflight()
		if not _pinned_source_preflight_ok:
			_report(_pinned_source_preflight_message)
			return
	var route := _build_selected_source_pipeline_request()
	if str(route.get("state", "")) != "AUTHORIZED_SOURCE_SCOPE":
		_pinned_source_preflight_ok = false
		_pinned_source_preflight_message = str(route.get("reason", "PINNED_SOURCE_SCOPE_NOT_VERIFIED"))
		_activity_stage = "AUTHORITY"
		_activity_message = _pinned_source_preflight_message
		_refresh_activity_header()
		_report(_pinned_source_preflight_message)
		return
	_operation_running = true
	_owner_review_status = "Current source run in progress; owner review is disabled."
	var request: Dictionary = route["request"]
	_activity_source_id = str(route["source_id"])
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
	_prepare_worker_cancel_marker()
	_pipeline_thread = Thread.new()
	var thread_error := _pipeline_thread.start(Callable(self, "_pipeline_worker").bind(prepared))
	if thread_error != OK:
		_pipeline_thread = null
		_finish_worker_cancel_marker()
		_complete_local_pipeline_failure("Pipeline worker could not start.")
		return
	_activity_message = "Waiting for the first backend stage."
	_activity_stage = "STARTING"
	_refresh_activity_header()
	_refresh_run_button_caption()


func _run_png_batch() -> void:
	if _gateway == null or _operation_running:
		return
	if _batch_job_source_mismatch:
		_report("Loaded PNG batch provenance does not match the current sources; no batch was created or resumed.")
		_refresh_run_button_caption()
		return
	if not _batch_job_id.is_empty() and _batch_job_matches_loaded_sources() and str(_batch_snapshot.get("state", "")) in ["QUEUED", "PAUSED", "STOPPED", "INTERRUPTED", "RUNNING"]:
		if _batch_legacy_reconciliation:
			_activity_message = "Explicit owner resume requested for the SHA-matched legacy composite."
		_dispatch_png_batch_job(_batch_job_id, _batch_import_id)
		return
	if _gameplay_sources.size() < 2:
		_report("Run Entire Loaded Batch requires at least two verified loaded PNGs.")
		return
	if _gameplay_sources.size() > 150:
		_report("Loaded PNG batch exceeds the 150-source sequential limit; no source was run.")
		return
	var source_ids: Array[String] = []
	for source in _gameplay_sources:
		var source_id := str(source.get("source_id", ""))
		if source_id.begins_with("owner-upload-") and source_id not in source_ids:
			source_ids.append(source_id)
	if source_ids.size() != _gameplay_sources.size():
		_report("Loaded gallery changed during snapshot; no batch was created.")
		return
	var composite := _extension("loaded-png-batch-create", {"source_ids": source_ids})
	_batch_import_id = str(composite.get("batch_id", ""))
	if _batch_import_id.is_empty():
		_report("Loaded PNG snapshot could not be verified: %s" % str(composite.get("error", composite.get("reason", "UNAVAILABLE"))))
		return
	_batch_composite_snapshot = composite
	var settings := {"game_project": _pinned_game_project_path(), "background_intent": _background_intent}
	var created: Dictionary = _gateway.call("run_studio_extension", "png-batch-create", {"batch_id": _batch_import_id, "settings": settings})
	var job: Dictionary = created.get("job", {})
	if job.is_empty():
		_report("PNG batch plan could not be verified: %s" % str(created.get("error", created.get("reason", "UNAVAILABLE"))))
		return
	_batch_job_id = str(job.get("job_id", ""))
	_batch_snapshot = job
	if _batch_job_id.is_empty():
		_report("PNG batch planner returned no durable job identity.")
		return
	if str(_batch_snapshot.get("state", "")) == "COMPLETE":
		var prior_counts: Dictionary = _batch_snapshot.get("counts", {})
		var prior_ready := int(prior_counts.get("ready", 0))
		var prior_failed := int(prior_counts.get("failed", 0))
		var prior_rejected := int(prior_counts.get("rejected", 0))
		var prior_skipped := int(prior_counts.get("skipped", 0))
		var terminal := "FINISHED WITH FAILURES · %d/%d READY · %d FAILED · %d REJECTED" % [prior_ready, int(prior_counts.get("total", 0)), prior_failed, prior_rejected]
		_activity_stage = "FINISHED WITH FAILURES" if prior_failed > 0 or prior_rejected > 0 else "COMPLETE WITH SKIPPED" if prior_skipped > 0 else "READY"
		_activity_backend_disposition = _activity_stage
		_activity_terminal_state = _activity_stage
		_activity_message = terminal if prior_failed > 0 or prior_rejected > 0 else "Loaded batch complete · %d READY · %d SKIPPED · no solver was run." % [prior_ready, prior_skipped] if prior_skipped > 0 else "Loaded batch already has verified READY results; no solver was run."
		if _activity_panel != null: _activity_panel.visible = true
		_render_batch_item_results(_batch_snapshot)
		_refresh_activity_header()
		_refresh_live_data()
		_refresh_run_button_caption()
		_report(_activity_message)
		return
	_dispatch_png_batch_job(_batch_job_id, _batch_import_id)


func _retry_failed_png_batch() -> void:
	if _gateway == null or _operation_running or _batch_job_id.is_empty():
		return
	var result := _extension("png-batch-retry-failed", {"job_id": _batch_job_id})
	var job: Dictionary = result.get("job", {})
	if job.is_empty() or str(job.get("job_id", "")).is_empty():
		_report("Explicit Retry Failed was not created: %s" % str(result.get("reason", result.get("disposition", "UNAVAILABLE"))))
		return
	_batch_job_id = str(job.get("job_id", ""))
	_batch_snapshot = job
	_dispatch_png_batch_job(_batch_job_id, str(job.get("import_batch_id", "")))


func _dispatch_png_batch_job(job_id: String, batch_id: String) -> void:
	if not _gateway.has_method("prepare_studio_extension_call") or not _gateway.has_method("execute_prepared_studio_extension_call"):
		_report("Canonical async PNG batch gateway is unavailable.")
		return
	var prepared: Dictionary = _gateway.call("prepare_studio_extension_call", "png-batch-run", {"job_id": job_id, "expected_batch_id": batch_id})
	if prepared.is_empty():
		_report("Canonical Python Factory Core cannot start the PNG batch.")
		return
	_pipeline_mutex.lock()
	_pipeline_worker_done = false
	_pipeline_worker_result.clear()
	_pipeline_mutex.unlock()
	_prepare_worker_cancel_marker()
	_pipeline_thread = Thread.new()
	var thread_error := _pipeline_thread.start(Callable(self, "_pipeline_worker").bind(prepared))
	if thread_error != OK:
		_pipeline_thread = null
		_finish_worker_cancel_marker()
		_report("PNG batch worker could not start.")
		return
	_batch_worker_active = true
	_operation_running = true
	for control_name in ["SolveAgain", "AcceptLevel", "RejectLevel"]:
		var guarded := get_node_or_null(control_name) as Button
		if guarded != null: guarded.disabled = true
	_activity_run_id = ""
	_activity_source_id = _selected_import_source_id
	_activity_stage = "BATCH QUEUED"
	_activity_message = "Explicit sequential PNG batch is running through canonical pipeline workers."
	_activity_backend_disposition = ""
	_activity_finished_msec = 0
	_activity_started_msec = Time.get_ticks_msec()
	_activity_source_filename = _selected_import_filename()
	_activity_terminal_state = ""
	if _activity_rows != null:
		for child in _activity_rows.get_children(): child.queue_free()
	if _activity_panel != null: _activity_panel.visible = true
	_refresh_activity_header()
	_refresh_run_button_caption()
	if _batch_pause_button != null: _batch_pause_button.visible = true
	if _batch_stop_button != null: _batch_stop_button.visible = true
	_append_activity_row({"seq": 1, "elapsed_ms": 0, "stage": "BATCH", "state": "RUNNING", "message": "Owner explicitly started the sequential PNG batch."})


func _request_batch_pause() -> void:
	_request_batch_control("PAUSE_AFTER_CURRENT")


func _request_batch_stop() -> void:
	_request_batch_control("STOP_AFTER_CURRENT")


func _request_batch_control(action: String) -> void:
	if _gateway == null or _batch_job_id.is_empty() or not _operation_running:
		return
	var result: Dictionary = _gateway.call("run_studio_extension", "png-batch-control", {"job_id": _batch_job_id, "action": action})
	if str(result.get("state", "")) != "SUCCESS":
		_report("Batch control request failed: %s" % str(result.get("error", "UNAVAILABLE")))
	else:
		_activity_message = "Batch cancellation requested; stopping the active game solver." if action == "CANCEL_NOW" else "Pause/stop requested after the current source finishes."
		_refresh_activity_header()


func _refresh_batch_progress() -> void:
	if _batch_job_id.is_empty() or not _batch_job_matches_loaded_sources() or Time.get_ticks_msec() - _batch_last_read_msec < 2500:
		return
	_batch_last_read_msec = Time.get_ticks_msec()
	_queue_studio_read_extension("png-batch-latest", {"batch_id": _batch_import_id}, {"kind": "batch-latest", "job_id": _batch_job_id})


func _apply_batch_progress_result(verified: Dictionary, expected_job_id: String) -> void:
	if expected_job_id != _batch_job_id:
		return
	if str(verified.get("disposition", "")) != "MATCHED":
		if str(verified.get("disposition", "")) == "BATCH_JOB_SOURCE_MISMATCH":
			_batch_job_source_mismatch = true
			_activity_message = "Saved batch lineage could not be authenticated. Keeping the last verified source view."
			_refresh_activity_header()
		return
	var parsed_value: Variant = verified.get("job", {})
	if not parsed_value is Dictionary:
		_batch_job_source_mismatch = true
		_activity_message = "Saved batch job could not be verified. Keeping the last verified source view; resume and retry are blocked."
		_refresh_run_button_caption()
		_refresh_activity_header()
		return
	var parsed: Dictionary = parsed_value
	if parsed.is_empty() or str(parsed.get("job_id", "")) != _batch_job_id:
		return
	var previous_snapshot := _batch_snapshot
	_batch_snapshot = parsed.duplicate(true)
	var counts_value: Variant = _batch_snapshot.get("counts", {})
	if not counts_value is Dictionary:
		_batch_snapshot["counts"] = {}
	if not _batch_job_matches_loaded_sources():
		_batch_snapshot = previous_snapshot
		_batch_job_source_mismatch = true
		_activity_message = "Saved batch source hashes do not match the loaded gallery. Keeping the last verified source view."
		_refresh_activity_header()
		return
	_batch_job_source_mismatch = false
	if not _operation_running and str(parsed.get("state", "")) == "RUNNING":
		_batch_snapshot["state"] = "INTERRUPTED"
	_sync_verified_batch_follow(_batch_snapshot)
	_record_verified_batch_item_progress(_batch_snapshot)
	_refresh_activity_header()
	_refresh_live_data()
	_refresh_run_button_caption()


func _batch_follow_index(job: Dictionary) -> int:
	var items: Array = job.get("items", [])
	if items.is_empty():
		return -1
	var current: Variant = job.get("current_index")
	if current is int and current >= 0 and current < items.size() and items[current] is Dictionary:
		if str(items[current].get("status", "")) in ["VERIFYING_EXISTING", "RUNNING"]:
			return current
	for index in range(items.size()):
		if items[index] is Dictionary and str(items[index].get("status", "")) in ["VERIFYING_EXISTING", "RUNNING"]:
			return index
	# When idle or between item hand-offs, keep the preview on the next source
	# that Resume will actually process, rather than pinning the last completed
	# thumbnail (often 002) while the queue advances elsewhere.
	for index in range(items.size()):
		if items[index] is Dictionary and str(items[index].get("status", "")) in ["QUEUED", "RETRYABLE", "INCONCLUSIVE"]:
			return index
	if current is int and current >= 0 and current < items.size():
		return current
	for index in range(items.size() - 1, -1, -1):
		if items[index] is Dictionary and str(items[index].get("status", "")) in ["READY", "FAILED", "REJECTED", "SKIPPED"]:
			return index
	return -1


func _record_verified_batch_item_progress(job: Dictionary) -> void:
	if _activity_rows == null or not _batch_job_matches_loaded_sources():
		return
	var displayed_source_id := _activity_source_id if not _activity_source_id.is_empty() else _selected_import_source_id
	var items: Array = job.get("items", [])
	for index in range(items.size()):
		if not items[index] is Dictionary:
			continue
		var item: Dictionary = items[index]
		var source_id := str(item.get("source_id", ""))
		if source_id != displayed_source_id:
			continue
		var source_index := _gameplay_source_index(source_id)
		if source_index < 0:
			continue
		var source: Dictionary = _gameplay_sources[source_index]
		if (int(item.get("index", -1)) != index
				or str(item.get("job_id", job.get("job_id", ""))) != str(job.get("job_id", ""))
				or str(item.get("source_sha256", "")) != str(source.get("source_sha256", ""))
				or str(item.get("source_record_sha256", "")) != str(source.get("source_record_sha256", ""))):
			continue
		var attempt_id := str(item.get("attempt_id", ""))
		var state := str(item.get("status", ""))
		if attempt_id.is_empty() or state not in ["READY", "FAILED", "REJECTED", "SKIPPED"]:
			continue
		if state == "READY" and (str(item.get("run_id", "")).is_empty() or str(_last_pipeline.get("run_id", "")) != str(item.get("run_id", "")) or str(_last_pipeline.get("source_id", "")) != source_id):
			continue
		if str(_batch_observed_item_states.get(attempt_id, "")) == state:
			continue
		_batch_observed_item_states[attempt_id] = state
		_append_batch_item_activity_row(item, job, true)


func _source_png_sha256(path: String) -> String:
	if path.is_empty() or not FileAccess.file_exists(path):
		return ""
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return ""
	var hashing := HashingContext.new()
	if hashing.start(HashingContext.HASH_SHA256) != OK:
		file.close()
		return ""
	while not file.eof_reached():
		hashing.update(file.get_buffer(65536))
	file.close()
	return hashing.finish().hex_encode()


func _sync_verified_batch_follow(job: Dictionary) -> void:
	if not _batch_job_matches_loaded_sources():
		return
	var items: Array = job.get("items", [])
	var item_index := _batch_follow_index(job)
	if item_index < 0 or item_index >= items.size() or not items[item_index] is Dictionary:
		return
	var item: Dictionary = items[item_index]
	var source_id := str(item.get("source_id", ""))
	var source_sha := str(item.get("source_sha256", ""))
	var record_sha := str(item.get("source_record_sha256", ""))
	var attempt_value: Variant = item.get("attempt_id", "")
	var attempt_id := "" if attempt_value == null else str(attempt_value)
	var index_value: Variant = item.get("index", -1)
	var column_value: Variant = item.get("column_count")
	var item_state := str(item.get("status", ""))
	if typeof(index_value) not in [TYPE_INT, TYPE_FLOAT] or int(index_value) != item_index or float(index_value) != float(item_index):
		return
	if typeof(column_value) not in [TYPE_INT, TYPE_FLOAT]:
		return
	var column_count := int(column_value)
	if float(column_value) != float(column_count) or column_count not in [3, 4, 5]:
		return
	var reused_ready := str(item.get("status", "")) == "READY" and bool(item.get("reused_existing_ready", false)) and not str(item.get("run_id", "")).is_empty()
	var queued_source := item_state in ["QUEUED", "RETRYABLE", "INCONCLUSIVE"]
	if (str(item.get("job_id", job.get("job_id", ""))) != str(job.get("job_id", ""))
			or source_id.trim_prefix("owner-upload-") != source_sha
			or record_sha.length() != 64 or (attempt_id.is_empty() and not reused_ready and not queued_source)):
		return
	var source_index := _gameplay_source_index(source_id)
	if source_index < 0:
		return
	var source: Dictionary = _gameplay_sources[source_index]
	var batch_position := _batch_composite_index(source_id)
	if batch_position < 0:
		return
	var path := str(source.get("path", ""))
	if (str(source.get("source_sha256", source_id.trim_prefix("owner-upload-"))) != source_sha
			or str(source.get("source_record_sha256", "")) != record_sha
			or _source_png_sha256(path) != source_sha):
		return
	var job_state := str(job.get("state", ""))
	var token := "%s|%d|%s|%s|%s|%d|%s|%s|%s" % [str(job.get("job_id", "")), item_index, source_id, source_sha, attempt_id, column_count, str(item.get("status", "")), str(item.get("run_id", "")), job_state]
	if token == _batch_follow_token and _activity_source_id == source_id and _selected_import_source_id == source_id:
		_batch_follow_item = item.duplicate(true)
		return
	if _activity_source_id != source_id:
		_clear_activity_rows()
	var item_activity_id := str(item.get("activity_run_id", ""))
	if _activity_source_id != source_id or _activity_run_id != item_activity_id:
		_activity_run_id = item_activity_id
		_activity_file_path = ProjectSettings.globalize_path("res://output/studio-pipeline-activity").path_join(item_activity_id + ".jsonl") if not item_activity_id.is_empty() else ""
		_activity_source_sha256 = source_sha
		_activity_stream_reader_override = null
		_activity_started_msec = Time.get_ticks_msec() if not item_activity_id.is_empty() else 0
		_activity_finished_msec = 0
		_activity_event_backend_disposition = ""
		_activity_read_offset = 0
		_activity_seen_sequence = 0
		_activity_pending_bytes.clear()
		_activity_previous_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"
		if not item_activity_id.is_empty():
			_clear_activity_rows()
	# Commit all source-facing regions from one exact persisted job item.
	_batch_follow_token = token
	_batch_follow_item = item.duplicate(true)
	_batch_follow_pipeline.clear()
	_selected_import_source_id = source_id
	_selected_art_path = path
	_last_source_id = source_id
	_last_candidate_id = ""
	_last_pipeline.clear()
	_owner_review_status = ""
	_imported_window_start = clampi(batch_position - 2, 0, maxi(0, _gameplay_sources.size() - 5))
	_activity_source_id = source_id
	_activity_source_filename = str(item.get("original_filename", item.get("display_name", source.get("display_filename", "PNG"))))
	var visible_item_state := job_state if item_state == "RUNNING" and job_state in ["PAUSED", "INTERRUPTED"] else item_state
	_activity_stage = "RUNNING" if _operation_running and job_state == "RUNNING" else visible_item_state if not visible_item_state.is_empty() else job_state
	_activity_backend_disposition = _activity_stage
	_activity_terminal_state = "" if _operation_running else _activity_stage
	_activity_message = "Batch item %d/%d · %s · %d columns" % [item_index + 1, items.size(), _activity_source_filename, column_count]
	_preview_paths_by_screen["LEVEL FACTORY"] = path
	_load_selected_art_preview(path, "LEVEL FACTORY")
	if item_state == "READY" and not str(item.get("run_id", "")).is_empty():
		_queue_studio_read_extension("restore-source-run-readonly", {"source_id": source_id, "game_project": _pinned_game_project_path()}, {
			"kind": "restore-batch-run", "token": token, "source_id": source_id, "source_sha256": source_sha,
			"column_count": column_count, "run_id": str(item.get("run_id", "")),
		})
	_refresh_activity_header()
	_refresh_runtime_cards()
	_refresh_live_data()


func _complete_png_batch(result: Dictionary) -> void:
	_operation_running = false
	_batch_worker_active = false
	_activity_finished_msec = Time.get_ticks_msec()
	if str(result.get("disposition", "")) == "BATCH_JOB_SOURCE_MISMATCH":
		_batch_job_source_mismatch = true
		_activity_stage = "BATCH_JOB_SOURCE_MISMATCH"
		_activity_backend_disposition = _activity_stage
		_activity_terminal_state = _activity_stage
		_activity_message = "The resumable job no longer matches the displayed imported batch. No source was run."
		_refresh_run_button_caption()
		_refresh_activity_header()
		return
	_batch_snapshot = result.get("job", _batch_snapshot)
	_activity_stage = str(_batch_snapshot.get("state", result.get("disposition", "ERROR")))
	var counts: Dictionary = _batch_snapshot.get("counts", {})
	var ready := int(counts.get("ready", 0))
	var failed := int(counts.get("failed", 0))
	var rejected := int(counts.get("rejected", 0))
	var total := int(counts.get("total", 0))
	var loaded := int(_batch_snapshot.get("snapshot_source_count", _gameplay_sources.size()))
	if failed > 0 or rejected > 0:
		_activity_backend_disposition = "FINISHED WITH FAILURES"
		_activity_message = "FINISHED WITH FAILURES · %d/%d READY · %d FAILED · %d REJECTED · %d remaining" % [ready, total, failed, rejected, int(counts.get("remaining", 0))]
	elif int(counts.get("skipped", 0)) > 0:
		_activity_backend_disposition = "COMPLETE WITH SKIPPED"
		_activity_message = "BATCH COMPLETE · %d/%d READY · %d SKIPPED · %d loaded" % [ready, total, int(counts.get("skipped", 0)), loaded]
	else:
		_activity_backend_disposition = "RETRY READY" if _batch_snapshot.has("parent_job_id") else "READY"
		_activity_message = "%s · %d/%d READY · %d loaded" % ["RETRY FINISHED" if _batch_snapshot.has("parent_job_id") else "BATCH READY", ready, total, loaded]
	_activity_terminal_state = _activity_backend_disposition
	_sync_verified_batch_follow(_batch_snapshot)
	_record_verified_batch_item_progress(_batch_snapshot)
	_render_batch_item_results(_batch_snapshot)
	if _pipeline_thread != null:
		_pipeline_thread = null
	var run_button := get_node_or_null("RunLevelPipeline") as Button
	if run_button != null: run_button.disabled = false
	for control_name in ["SolveAgain", "AcceptLevel", "RejectLevel"]:
		var guarded := get_node_or_null(control_name) as Button
		if guarded != null: guarded.disabled = false
	if _batch_pause_button != null: _batch_pause_button.visible = false
	if _batch_stop_button != null: _batch_stop_button.visible = false
	_refresh_release_pool(false)
	_refresh_activity_header()
	_refresh_live_data()
	_refresh_run_button_caption()
	_report(_activity_message)


func _render_batch_item_results(job: Dictionary, force_selected_item: bool = false) -> void:
	if _activity_rows == null or not _batch_job_matches_loaded_sources():
		return
	if _activity_panel != null: _activity_panel.visible = true
	var source_id := _activity_source_id if not _activity_source_id.is_empty() else _selected_import_source_id
	var items: Array = job.get("items", [])
	for index in range(items.size()):
		if not items[index] is Dictionary:
			continue
		var item: Dictionary = items[index]
		if str(item.get("source_id", "")) != source_id:
			continue
		var source_index := _gameplay_source_index(source_id)
		if source_index < 0:
			return
		var source: Dictionary = _gameplay_sources[source_index]
		if (int(item.get("index", -1)) != index
				or str(item.get("job_id", job.get("job_id", ""))) != str(job.get("job_id", ""))
				or str(item.get("source_sha256", "")) != str(source.get("source_sha256", ""))
				or str(item.get("source_record_sha256", "")) != str(source.get("source_record_sha256", ""))):
			return
		var status := str(item.get("status", ""))
		if status == "READY":
			var run_id := str(item.get("run_id", ""))
			if run_id.is_empty() or str(_last_pipeline.get("source_id", "")) != source_id or str(_last_pipeline.get("run_id", "")) != run_id:
				return
			_activity_backend_disposition = "READY"
			_activity_terminal_state = "READY"
			_activity_stage = "READY"
			_activity_message = "Verified source-bound batch result restored; no solver was run."
		elif status in ["FAILED", "REJECTED", "SKIPPED"]:
			_activity_backend_disposition = status
			_activity_terminal_state = status
			_activity_stage = status
			_activity_message = str(item.get("reason", "Batch item %s." % status.to_lower()))
		elif status in ["QUEUED", "RUNNING"]:
			var job_state := str(job.get("state", ""))
			var display_state := job_state if status == "RUNNING" and job_state in ["PAUSED", "INTERRUPTED"] else status
			_activity_backend_disposition = display_state
			_activity_terminal_state = "" if _operation_running else display_state
			_activity_stage = display_state
			_activity_message = "Current source item · %d columns" % int(item.get("column_count", 0))
		if force_selected_item:
			_append_batch_item_activity_row(item, job, true)
		if _activity_phase_label != null:
			_activity_phase_label.text = "%s · %s · %d columns" % [str(item.get("original_filename", "PNG")), status, int(item.get("column_count", 0))]
			_activity_phase_label.tooltip_text = "job_id=%s · item=%d · source_id=%s · source_sha256=%s · source_record_sha256=%s" % [str(job.get("job_id", "")), index, source_id, str(item.get("source_sha256", "")), str(item.get("source_record_sha256", ""))]
		return


func _append_batch_item_activity_row(item: Dictionary, job: Dictionary, force: bool = false) -> void:
	if _activity_rows == null or str(item.get("source_id", "")) != _activity_source_id:
		return
	var state := str(item.get("status", ""))
	var attempt_id := str(item.get("attempt_id", ""))
	if not force and not attempt_id.is_empty() and str(_batch_observed_item_states.get(attempt_id, "")) == state:
		return
	if not attempt_id.is_empty():
		_batch_observed_item_states[attempt_id] = state
	var reason := str(item.get("reason", ""))
	var filename := str(item.get("original_filename", item.get("display_name", "PNG")))
	var run_id := str(item.get("run_id", "no run ID"))
	var line := "%s · columns %d · %s · %s%s" % [filename, int(item.get("column_count", 0)), state, run_id, " · " + reason if not reason.is_empty() else ""]
	var row := Label.new()
	row.name = "BatchResult_%03d" % int(item.get("index", 0))
	row.text = line
	row.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	row.custom_minimum_size.y = 34
	row.tooltip_text = "job_id=%s\nitem_index=%d\nattempt_id=%s\nsource_id=%s\nsource_sha256=%s\nsource_record_sha256=%s\nstatus=%s\nreason=%s" % [str(job.get("job_id", "")), int(item.get("index", 0)), attempt_id, str(item.get("source_id", "")), str(item.get("source_sha256", "")), str(item.get("source_record_sha256", "")), state, reason]
	row.add_theme_font_size_override("font_size", 10)
	row.add_theme_color_override("font_color", Color("#dce8f8"))
	_activity_rows.add_child(row)


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
	if _activity_rows == null or str(body.get("source_id", _selected_import_source_id)) != _selected_import_source_id:
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


func _clear_activity_rows() -> void:
	_activity_events.clear()
	if _activity_rows == null:
		return
	for child in _activity_rows.get_children():
		_activity_rows.remove_child(child)
		child.queue_free()


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
	if not _batch_job_id.is_empty() and _operation_running:
		var counts: Dictionary = _batch_snapshot.get("counts", {})
		var current_index: Variant = _batch_snapshot.get("current_index")
		var items: Array = _batch_snapshot.get("items", [])
		var job_state := str(_batch_snapshot.get("state", ""))
		var activity_state := job_state if job_state in ["PAUSED", "INTERRUPTED", "STOPPED"] else "RUNNING"
		var current_caption := "Starting next verified PNG"
		if current_index is int and current_index >= 0 and current_index < items.size() and items[current_index] is Dictionary:
			var current: Dictionary = items[current_index]
			current_caption = "%s · %d columns" % [str(current.get("original_filename", current.get("display_name", "Selected PNG"))).left(24), int(current.get("column_count", 0))]
		_activity_state_label.text = activity_state
		var activity_color := Color("#245478") if activity_state == "RUNNING" else Color("#7a5824") if activity_state in ["PAUSED", "STOPPED"] else Color("#743d3c")
		_activity_state_chip.add_theme_stylebox_override("panel", _control_style(activity_color, activity_color.lightened(0.22)))
		_activity_source_label.text = "%s · %d/%d" % [current_caption, int(counts.get("total", 0)) - int(counts.get("remaining", 0)) + (1 if current_index is int else 0), int(counts.get("total", 0))]
		_activity_source_label.tooltip_text = "Sequential batch %s" % _batch_job_id
		_activity_phase_label.text = "Canonical pipeline · %d READY · %d failed" % [int(counts.get("ready", 0)), int(counts.get("failed", 0))]
		_activity_phase_label.tooltip_text = _activity_message
		return
	var activity_matches_selection := _activity_source_id.is_empty() or _activity_source_id == _selected_import_source_id
	if not activity_matches_selection:
		_activity_state_label.text = "SOURCE ONLY"
		_activity_state_chip.add_theme_stylebox_override("panel", _control_style(Color("#34425a"), Color("#536783")))
		_activity_source_label.text = "%s · awaiting run" % _selected_import_filename().left(22)
		_activity_source_label.tooltip_text = "Selected source %s; prior-source activity is hidden." % _selected_import_source_id
		_activity_phase_label.text = "SOURCE ONLY · explicit Run Pipeline required"
		_activity_phase_label.tooltip_text = "PNG selection and restoration are read-only."
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
	var source_id := _activity_source_id if not _activity_run_id.is_empty() else _selected_import_source_id
	_activity_source_label.tooltip_text = "Source %s  |  Run %s" % [source_id, _activity_run_id]
	_activity_phase_label.text = "" if _activity_stage in ["", "IDLE"] else "%s · %s" % [_activity_stage.replace("_", " ").left(26), _activity_message.left(40)]
	_activity_phase_label.tooltip_text = "%s · pinned %s" % [_activity_message, _PINNED_GAME_COMMIT]


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
	if _batch_worker_active:
		_complete_png_batch(result)
		return
	var completed_source_id := str(result.get("source_id", ""))
	var still_selected := completed_source_id == _selected_import_source_id and completed_source_id == _activity_source_id
	if still_selected:
		_last_pipeline = result
	_operation_running = false
	_activity_finished_msec = Time.get_ticks_msec()
	if not _activity_pending_bytes.is_empty():
		_fail_activity_monitor("Activity stream ended with an incomplete trailing event line.")
	if still_selected and not str(result.get("derived_candidate_id", "")).is_empty():
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
	if still_selected and backend_state == "READY" and (not terminal_matches or not _activity_integrity_error.is_empty()):
		_last_pipeline["studio_monitor_validation"] = "FAILED_CLOSED"
		_last_pipeline["studio_monitor_reason"] = "Backend READY is withheld because activity integrity or the terminal event did not verify."
	var run_button := get_node_or_null("RunLevelPipeline") as Button
	if run_button != null: run_button.disabled = false
	var solve_button := get_node_or_null("SolveAgain") as Button
	if solve_button != null: solve_button.disabled = false
	_refresh_activity_header()
	_refresh_live_data()
	if still_selected:
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
	var level_button := get_node_or_null("LevelNumber") as Button
	if level_button != null:
		level_button.text = _level_number_caption()
	_report("Manual level number: %d" % _level_number)


func _review_candidate(disposition: String) -> void:
	if _operation_running:
		_report("Wait for the active source run to finish before recording owner review.")
		return
	if _last_candidate_id.is_empty():
		_report("Select a candidate before recording owner review.")
		return
	var primary: Dictionary = _last_pipeline.get("primary", {})
	if str(_last_pipeline.get("source_id", "")) != _selected_import_source_id or str(_last_pipeline.get("disposition", "")) != "READY" or str(primary.get("state", "")) != "READY":
		_report("Owner review requires the selected PNG's completed canonical READY run.")
		return
	var result := _extension("owner-review", {"candidate_id": _last_candidate_id, "disposition": disposition})
	_release_pool = _extension("release-pool", {})
	_apply_release_projection()
	var publication: Dictionary = result.get("publication", {})
	var exact_readback := false
	var candidate_in_pool := false
	for entry_variant in _release_pool.get("entries", []):
		if entry_variant is Dictionary and str(entry_variant.get("candidate_id", "")) == _last_candidate_id:
			candidate_in_pool = true
			if str(entry_variant.get("pipeline_run_id", "")) == str(_last_pipeline.get("run_id", "")):
				exact_readback = true
	var readback_ok := bool(publication.get("readback_verified", false)) and exact_readback if disposition == "ACCEPT" else str(publication.get("disposition", "")) == "EXCLUDED_FROM_RELEASE_POOL" and not candidate_in_pool
	if disposition == "ACCEPT":
		_owner_review_status = "ACCEPTED / IN RELEASE POOL" if readback_ok else "ACCEPT_RECORDED_BUT_POOL_DENIED: %s" % str(publication.get("reason", "exact current candidate/run was not returned by Release Pool read-back"))
	else:
		_owner_review_status = "REJECTED / EXCLUDED FROM RELEASE POOL" if readback_ok else "REJECT_RECORDED_BUT_POOL_READBACK_FAILED: %s" % str(publication.get("reason", "candidate remained in the Release Pool"))
	_refresh_live_data()
	_report("%s · review %s" % [_owner_review_status, str(result.get("review_id", result.get("state", "UNAVAILABLE")))])


func _refresh_release_pool(show_status: bool = true) -> void:
	if show_status:
		_append_release_pool_activity("REFRESH POOL", "STARTED", "read-only Release Pool projection", _selected_release_ids)
	_queue_studio_read_extension("release-pool", {}, {"kind": "release-pool", "show_status": show_status})
	_apply_release_projection()


func _queue_studio_read_extension(operation: String, request: Dictionary, context: Dictionary) -> void:
	if _gateway == null or not _gateway.has_method("prepare_studio_extension_call"):
		return
	var context_key := str(context.get("kind", ""))
	var context_identity := context_key
	if context_key in ["restore-batch-run", "restore-selected-source"]:
		context_identity += "|" + str(context.get("token", ""))
	if context_key == "batch-latest" and str(context.get("job_id", "")) != _batch_job_id:
		return
	var active_identity := str(_studio_read_context.get("kind", ""))
	if active_identity in ["restore-batch-run", "restore-selected-source"]:
		active_identity += "|" + str(_studio_read_context.get("token", ""))
	if active_identity == context_identity:
		return
	for queued in _studio_read_queue:
		var queued_context: Dictionary = queued.get("context", {})
		var queued_identity := str(queued_context.get("kind", ""))
		if queued_identity in ["restore-batch-run", "restore-selected-source"]:
			queued_identity += "|" + str(queued_context.get("token", ""))
		if queued_identity == context_identity:
			return
	var prepared: Dictionary = _gateway.call("prepare_studio_extension_call", operation, request)
	if not prepared.is_empty():
		_studio_read_queue.append({"prepared": prepared, "context": context.duplicate(true)})


func _request_candidate_inbox_refresh(force: bool = false) -> void:
	# candidate-inbox validates complete bundles and review chains. Keep that
	# expensive read out of draw/refresh callbacks. Load it on demand once; new
	# generated art explicitly invalidates the cache. While a sequential source
	# batch is active, the cached art strip is sufficient.
	if _gateway == null or _screen != "PIXEL ART" or (_operation_running and not _batch_job_id.is_empty()):
		return
	if not force and not _candidate_inbox_cache.is_empty():
		return
	var now := Time.get_ticks_msec()
	if not force and now - _candidate_inbox_last_request_msec < 10000:
		return
	_candidate_inbox_last_request_msec = now
	_queue_studio_read_extension("candidate-inbox", {}, {"kind": "candidate-inbox"})


func _start_next_studio_read_extension() -> void:
	if _studio_read_thread != null or _studio_read_queue.is_empty():
		return
	var queued: Dictionary = _studio_read_queue.pop_front()
	_studio_read_mutex.lock()
	_studio_read_done = false
	_studio_read_result.clear()
	_studio_read_context = queued.get("context", {}).duplicate(true)
	_studio_read_mutex.unlock()
	_studio_read_thread = Thread.new()
	var error := _studio_read_thread.start(Callable(self, "_studio_read_extension_worker").bind(queued.get("prepared", {})))
	if error != OK:
		_studio_read_thread = null
		_studio_read_mutex.lock()
		_studio_read_context.clear()
		_studio_read_mutex.unlock()


func _studio_read_extension_worker(prepared: Dictionary) -> void:
	var result: Dictionary = _gateway.call("execute_prepared_studio_extension_call", prepared)
	_studio_read_mutex.lock()
	_studio_read_result = result
	_studio_read_done = true
	_studio_read_mutex.unlock()


func _poll_studio_read_extension() -> void:
	if _studio_read_thread == null:
		return
	_studio_read_mutex.lock()
	var completed := _studio_read_done
	var result := _studio_read_result.duplicate(true) if completed else {}
	var context := _studio_read_context.duplicate(true) if completed else {}
	_studio_read_mutex.unlock()
	if not completed or _studio_read_thread.is_alive():
		return
	_studio_read_thread.wait_to_finish()
	_studio_read_thread = null
	_studio_read_mutex.lock()
	_studio_read_done = false
	_studio_read_result.clear()
	_studio_read_context.clear()
	_studio_read_mutex.unlock()
	var kind := str(context.get("kind", ""))
	if kind == "candidate-inbox":
		if str(result.get("schema", "")) == "scrubbots-candidate-inbox-view" and result.get("candidates", []) is Array:
			_candidate_inbox_cache = result
			_refresh_runtime_cards()
			_refresh_live_data()
	elif kind == "batch-latest":
		_apply_batch_progress_result(result, str(context.get("job_id", "")))
	elif kind == "release-pool":
		_release_pool = result
		_apply_release_projection()
		_refresh_live_data()
		if bool(context.get("show_status", false)):
			var entries: Array = _release_pool.get("entries", [])
			_append_release_pool_activity("REFRESH POOL", str(_release_pool.get("state", _release_pool.get("disposition", "UNAVAILABLE"))), "entries=%d; visible after filters=%d" % [entries.size(), _visible_release_ids.size()], _selected_release_ids)
			_report("READY levels: %s" % str(_release_pool.get("pool_size", 0)))
	elif kind == "restore-batch-run":
		_apply_restored_batch_run(result, context)
	elif kind == "restore-selected-source":
		_apply_restored_selected_source(result, context)


func _apply_restored_selected_source(restored: Dictionary, context: Dictionary) -> void:
	if (str(context.get("token", "")) != _selection_restore_token
			or str(context.get("source_id", "")) != _selected_import_source_id):
		return
	var source_id := str(context.get("source_id", ""))
	var expected_sha := str(context.get("source_sha256", ""))
	var restored_source_run := false
	if str(restored.get("state", "")) == "READY" and str(restored.get("source_sha256", "")) == expected_sha:
		var restored_pipeline: Dictionary = restored.get("pipeline", {})
		var restored_request: Dictionary = restored_pipeline.get("request", {})
		if str(restored_request.get("source_id", "")) == source_id and str(restored_pipeline.get("disposition", "")) == "READY":
			restored_pipeline["source_id"] = source_id
			_last_pipeline = restored_pipeline
			_last_candidate_id = str(restored.get("candidate_id", ""))
			var restored_review: Dictionary = restored.get("owner_review_status", {})
			if not restored_review.is_empty():
				_owner_review_status = "%s · %s" % [str(restored_review.get("pool_state", "")), str(restored_review.get("reason", ""))]
			_activity_stage = "RESTORED"
			_activity_message = "Restored exact source-bound canonical READY result; no solver was run."
			_activity_backend_disposition = "READY"
			_activity_terminal_state = "READY"
			_append_activity_row({"seq": 1, "elapsed_ms": 0, "stage": "RESTORED", "state": "READY", "message": _activity_message, "source_id": source_id})
			restored_source_run = true
	if not restored_source_run and bool(context.get("batch_scope_matches", false)):
		_render_batch_item_results(_batch_snapshot, true)
	_refresh_activity_header()
	_refresh_runtime_cards()
	_refresh_live_data()


func _apply_restored_batch_run(restored: Dictionary, context: Dictionary) -> void:
	if (str(context.get("token", "")) != _batch_follow_token
			or str(context.get("source_id", "")) != _selected_import_source_id
			or str(context.get("source_id", "")) != str(_batch_follow_item.get("source_id", ""))):
		return
	var pipeline: Dictionary = restored.get("pipeline", {})
	var request: Dictionary = pipeline.get("request", {})
	var saved_run_id := str(restored.get("run_id", pipeline.get("run_id", "")))
	if (str(restored.get("state", "")) == "READY"
			and str(restored.get("source_sha256", "")) == str(context.get("source_sha256", ""))
			and str(request.get("source_id", "")) == str(context.get("source_id", ""))
			and int(request.get("column_count", 0)) == int(context.get("column_count", 0))
			and str(pipeline.get("run_id", saved_run_id)) == str(context.get("run_id", ""))):
		pipeline["source_id"] = str(context.get("source_id", ""))
		_batch_follow_pipeline = pipeline.duplicate(true)
		_last_pipeline = pipeline.duplicate(true)
		var review: Dictionary = restored.get("owner_review_status", {})
		_owner_review_status = str(review.get("pool_state", review.get("disposition", ""))) if not review.is_empty() else str(_batch_follow_item.get("release_pool", {}).get("disposition", ""))
		_refresh_live_data()


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
		_append_release_pool_activity("PREFLIGHT", "BLOCKED", "Select one or more READY levels first.", [])
		_report("Select one or more READY levels first.")
		return
	_append_release_pool_activity("PREFLIGHT", "STARTED", "canonical preflight requested", _selected_release_ids)
	var result := _extension("scrubbots-publish", {
		"action": "preflight", "candidate_ids": _selected_release_ids,
		"pack_id": "factory-studio-release",
		"created_at_utc": Time.get_datetime_string_from_system(true, false) + "Z",
	})
	_release_pool["publish_preflight"] = result
	_append_release_pool_activity("PREFLIGHT", str(result.get("state", result.get("disposition", "UNAVAILABLE"))), _release_activity_result_detail(result), _selected_release_ids)
	_report("Preflight: %s" % str(result.get("state", result.get("disposition", "UNAVAILABLE"))))


func _show_publish_stage(stage: String) -> void:
	var preflight: Dictionary = _release_pool.get("publish_preflight", {})
	var state := str(preflight.get("state", "NOT_RUN"))
	var detail := "%s is status-only here; last verified preflight=%s. This click did not run the stage." % [stage, state]
	_append_release_pool_activity(stage, "STATUS ONLY · %s" % state, detail)
	_report("%s · status only · %s" % [stage, state])


func _publish_staging() -> void:
	var preflight: Dictionary = _release_pool.get("publish_preflight", {})
	var reviewed: Dictionary = preflight.get("reviewed_identity", {})
	if reviewed.is_empty():
		_append_release_pool_activity("STAGING UPLOAD", "BLOCKED", "Run publish preflight before STAGING upload.", _selected_release_ids)
		_report("Run publish preflight before STAGING upload.")
		return
	_append_release_pool_activity("STAGING UPLOAD", "STARTED", "canonical STAGING publish requested", _selected_release_ids)
	var result := _extension("scrubbots-publish", {
		"action": "publish-staging", "candidate_ids": _selected_release_ids,
		"pack_id": "factory-studio-release",
		"content_version": int(reviewed.get("content_version", 0)),
		"created_at_utc": str(reviewed.get("created_at_utc", "")),
		"reviewed_identity": reviewed,
	})
	_append_release_pool_activity("STAGING UPLOAD", str(result.get("state", result.get("disposition", "UNAVAILABLE"))), _release_activity_result_detail(result), _selected_release_ids)
	_report("STAGING: %s" % str(result.get("state", result.get("disposition", "UNAVAILABLE"))))


func _generate_request(request: Dictionary) -> Dictionary:
	if _gateway == null or _operation_running:
		return {"state": "UNAVAILABLE", "reason": "Factory Core is unavailable."}
	_operation_running = true
	var result: Dictionary
	var selected_provider := str(request.get("provider", _provider_model))
	if selected_provider == "ALPIX (Claude)":
		result = _extension("alpix-generate", {"prompt": request.get("prompt", ""), "width": request.get("width", 32), "height": request.get("height", 32)})
	elif selected_provider == "PIXELLAB":
		# Paid requests only pass through explicit confirmation and the async worker.
		result = {"state": "PAID_CONFIRMATION_REQUIRED", "reason": "Start one explicit Generate/Regenerate request to confirm Pro Flash cost."}
	elif selected_provider == "MAGNIFIC":
		result = {"state": "PROVIDER_RETIRED", "reason": "PROVIDER_RETIRED_MAGNIFIC · choose ALPIX (Claude) or PIXELLAB explicitly."}
	else:
		result = {"state": "UNAVAILABLE", "reason": "Selected provider is not configured."}
	_operation_running = false
	return result


func _finish_generation(result: Dictionary) -> void:
	_last_candidate_id = str(result.get("candidate_id", _last_candidate_id))
	_last_source_id = str(result.get("source_id", _last_source_id))
	if not str(result.get("output_path", result.get("source_path", ""))).is_empty():
		_candidate_inbox_cache.clear()
		_selected_art_path = str(result.get("output_path", result.get("source_path", ""))).path_join("artwork.png") if result.has("output_path") else str(result.get("source_path", ""))
		_load_selected_art_preview(_selected_art_path)
		_request_candidate_inbox_refresh(true)
	var usage_text := ""
	var usage: Dictionary = result.get("actual_usage", {})
	if usage.has("generations"):
		usage_text = " · %s generation units used" % str(usage.get("generations"))
	elif usage.has("usd"):
		usage_text = " · actual usage $%s" % str(usage.get("usd"))
	if result.has("palette_validation"):
		usage_text += " · palette V3 PASS (%d colors)" % result.get("used_palette_ids", []).size()
	_report("%s · %s%s" % [_last_candidate_id, str(result.get("state", "ERROR")), usage_text])


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
	var width_input := SpinBox.new(); width_input.min_value = 20; width_input.max_value = 56; width_input.step = 4; width_input.value = _width
	var height_input := SpinBox.new(); height_input.min_value = 20; height_input.max_value = 56; height_input.step = 4; height_input.value = _height
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
	var provider_ids: Array[String] = []
	for item in options:
		if item is Dictionary:
			var provider_id := str(item.get("id", ""))
			if provider_id in ["ALPIX (Claude)", "PIXELLAB"]:
				var available := bool(item.get("available", false))
				var display_name := "PIXELLAB · Pro Flash" if provider_id == "PIXELLAB" else provider_id
				if not available: display_name += " · UNAVAILABLE"
				choice.add_item(display_name)
				choice.set_item_metadata(choice.item_count - 1, provider_id)
				choice.set_item_tooltip(choice.item_count - 1, str(item.get("reason", "")))
				names.append(display_name)
				provider_ids.append(provider_id)
	if _provider_model == "MAGNIFIC": _provider_model = "ALPIX (Claude)"
	var selected := provider_ids.find(_provider_model)
	if selected < 0: selected = provider_ids.find("ALPIX (Claude)")
	if selected < 0: selected = 0
	if not names.is_empty(): choice.select(selected)
	dialog.add_child(choice)
	dialog.confirmed.connect(func():
		if choice.item_count > 0: _provider_model = str(choice.get_item_metadata(choice.selected))
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
	_fit_preview_image_to_host()
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
	_request_candidate_inbox_refresh()
	var inbox := _candidate_inbox_cache
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
	if not _gameplay_sources.is_empty():
		if _operation_running and not _batch_job_id.is_empty():
			return
		var queue_index := _imported_window_start + index
		if index >= 0 and queue_index < _gameplay_sources.size():
			_select_imported_source_by_id(str(_gameplay_sources[queue_index].get("source_id", "")))
		return
	_select_inbox_candidate(index)


func _select_imported_source_by_id(source_id: String) -> void:
	_refresh_gameplay_sources()
	for index in range(_gameplay_sources.size()):
		var imported: Dictionary = _gameplay_sources[index]
		if str(imported.get("source_id", "")) != source_id:
			continue
		_bind_displayed_batch_to_source(source_id)
		_clear_activity_rows()
		_activity_run_id = ""
		_activity_file_path = ""
		_activity_source_sha256 = ""
		_activity_stream_reader_override = null
		_activity_started_msec = 0
		_activity_finished_msec = 0
		_activity_event_backend_disposition = ""
		_activity_integrity_error = ""
		_activity_seen_sequence = 0
		_activity_read_offset = 0
		_activity_pending_bytes.clear()
		_activity_previous_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"
		_selected_import_source_id = source_id
		_selected_art_path = str(imported.get("path", ""))
		_last_source_id = source_id
		_last_candidate_id = ""
		_last_pipeline.clear()
		_owner_review_status = ""
		_hide_review_dialogs()
		_activity_stage = "SOURCE ONLY"
		_activity_message = "Selected PNG is read-only until Run Pipeline is explicitly selected."
		_activity_backend_disposition = "SOURCE ONLY"
		_activity_terminal_state = "SOURCE ONLY"
		_activity_integrity_error = ""
		_imported_window_start = clampi(index - 2, 0, maxi(0, _gameplay_sources.size() - 5))
		_activity_source_id = source_id
		_activity_source_filename = str(imported.get("display_filename", "Selected PNG"))
		_batch_follow_item.clear()
		_batch_follow_pipeline.clear()
		_batch_follow_token = ""
		var batch_scope_matches := not _batch_snapshot.is_empty() and _batch_job_matches_loaded_sources()
		_preview_paths_by_screen["LEVEL FACTORY"] = _selected_art_path
		_load_selected_art_preview(_selected_art_path, "LEVEL FACTORY")
		_refresh_pinned_source_preflight()
		_selection_restore_token = "%s|%s|%d" % [source_id, str(imported.get("source_sha256", source_id.trim_prefix("owner-upload-"))), Time.get_ticks_usec()]
		_queue_studio_read_extension("restore-source-run-readonly", {
			"source_id": source_id,
			"game_project": _pinned_game_project_path()
		}, {
			"kind": "restore-selected-source", "token": _selection_restore_token,
			"source_id": source_id,
			"source_sha256": str(imported.get("source_sha256", source_id.trim_prefix("owner-upload-"))),
			"batch_scope_matches": batch_scope_matches,
		})
		_refresh_activity_header()
		_refresh_runtime_cards()
		_refresh_live_data()
		_report("Selected %s · %s" % [str(imported.get("display_filename", "image.png")), _wrap_identity(source_id, 24)])
		return


func _bind_displayed_batch_to_source(source_id: String) -> void:
	# Historical import membership is provenance only. Selecting a thumbnail is
	# read-only and never rebinds or replaces a loaded-source batch snapshot.
	if source_id.is_empty():
		return
	_refresh_run_button_caption()


func _batch_job_matches_loaded_sources() -> bool:
	var items: Array = _batch_snapshot.get("items", [])
	var composite_items: Array = _batch_composite_snapshot.get("items", [])
	if items.is_empty() or composite_items.is_empty() or str(_batch_snapshot.get("import_batch_id", "")) != _batch_import_id:
		return false
	if composite_items.size() != _gameplay_sources.size():
		return false
	var loaded_by_id: Dictionary = {}
	for loaded_source_variant in _gameplay_sources:
		if not loaded_source_variant is Dictionary:
			return false
		var loaded_source: Dictionary = loaded_source_variant
		var loaded_id := str(loaded_source.get("source_id", ""))
		if loaded_id.is_empty() or loaded_by_id.has(loaded_id):
			return false
		loaded_by_id[loaded_id] = loaded_source
	var composite_by_id: Dictionary = {}
	for composite_variant in composite_items:
		if not composite_variant is Dictionary:
			return false
		var composite_source: Dictionary = composite_variant
		var source_id := str(composite_source.get("source_id", ""))
		if source_id.is_empty() or composite_by_id.has(source_id) or not loaded_by_id.has(source_id):
			return false
		var loaded_source: Dictionary = loaded_by_id[source_id]
		if (str(composite_source.get("source_sha256", "")) != str(loaded_source.get("source_sha256", ""))
				or str(composite_source.get("source_record_sha256", "")) != str(loaded_source.get("source_record_sha256", ""))):
			return false
		composite_by_id[source_id] = composite_source
	var source_by_id: Dictionary = {}
	for item_variant in composite_items:
		if item_variant is Dictionary:
			source_by_id[str(item_variant.get("source_id", ""))] = item_variant
	var is_retry := _batch_snapshot.has("parent_job_id")
	if is_retry and not bool(_batch_snapshot.get("lineage_verified", false)):
		return false
	if not is_retry and items.size() != composite_items.size():
		return false
	for index in range(items.size()):
		if not items[index] is Dictionary:
			return false
		var item: Dictionary = items[index]
		var source_id := str(item.get("source_id", ""))
		if not source_by_id.has(source_id):
			return false
		var source: Dictionary = source_by_id[source_id]
		if (str(item.get("source_sha256", "")) != str(source.get("source_sha256", ""))
				or str(item.get("source_record_sha256", "")) != str(source.get("source_record_sha256", ""))):
			return false
		if is_retry and int(item.get("column_count", 0)) not in [3, 4, 5]:
			return false
		if not is_retry and str(item.get("source_id", "")) != str(composite_items[index].get("source_id", "")):
			return false
	return true


func _batch_composite_index(source_id: String) -> int:
	var composite_items: Array = _batch_composite_snapshot.get("items", [])
	for index in range(composite_items.size()):
		if composite_items[index] is Dictionary and str(composite_items[index].get("source_id", "")) == source_id:
			return index
	return -1


func _batch_ordered_gameplay_sources() -> Array:
	var composite_items: Array = _batch_composite_snapshot.get("items", [])
	if composite_items.size() != _gameplay_sources.size() or composite_items.is_empty():
		return _gameplay_sources
	var loaded_by_id: Dictionary = {}
	for source_variant in _gameplay_sources:
		if not source_variant is Dictionary:
			return _gameplay_sources
		var source: Dictionary = source_variant
		var source_id := str(source.get("source_id", ""))
		if source_id.is_empty() or loaded_by_id.has(source_id):
			return _gameplay_sources
		loaded_by_id[source_id] = source
	var ordered: Array = []
	var seen_ids: Dictionary = {}
	for composite_variant in composite_items:
		if not composite_variant is Dictionary:
			return _gameplay_sources
		var composite_source: Dictionary = composite_variant
		var source_id := str(composite_source.get("source_id", ""))
		if source_id.is_empty() or seen_ids.has(source_id) or not loaded_by_id.has(source_id):
			return _gameplay_sources
		var source: Dictionary = loaded_by_id[source_id]
		if (str(composite_source.get("source_sha256", "")) != str(source.get("source_sha256", ""))
				or str(composite_source.get("source_record_sha256", "")) != str(source.get("source_record_sha256", ""))):
			return _gameplay_sources
		seen_ids[source_id] = true
		ordered.append(source)
	return ordered


func _pinned_game_project_path() -> String:
	return ProjectSettings.globalize_path("res://output/current-game-runtime/%s" % _PINNED_GAME_COMMIT).simplify_path()


func _build_selected_source_pipeline_request() -> Dictionary:
	if _selected_import_source_id.is_empty() or not _pinned_source_preflight_ok:
		return {"state": "BLOCKED", "reason": _pinned_source_preflight_message}
	return {
		"state": "AUTHORIZED_SOURCE_SCOPE",
		"source_id": _selected_import_source_id,
		"source_sha256": _selected_import_source_id.trim_prefix("owner-upload-"),
		"request": {
			"column_count": _column_count,
			"real_max_visited": 25000,
			"solver_timeout_seconds": 240,
			"level_number": _level_number if _manual_level_override else 1,
			"game_project": _pinned_game_project_path(),
			"background_intent": _background_intent,
			"max_robots": null,
			"target_difficulty": "V1_ADVISORY",
		}
	}


func _refresh_pinned_source_preflight() -> void:
	_pinned_source_preflight_ok = false
	if _selected_import_source_id.is_empty():
		_pinned_source_preflight_message = "Select a verified owner PNG."
		_activity_stage = "AUTHORITY"
		_activity_message = _pinned_source_preflight_message
		_refresh_activity_header()
		return
	var result := _extension("validate-source-readonly", {
		"source_id": _selected_import_source_id,
		"game_project": _pinned_game_project_path()
	})
	var capability: Dictionary = result.get("void_capability", {})
	var structural: Dictionary = result.get("structural", {})
	var source_authority: Dictionary = result.get("source_authority", {})
	_pinned_source_preflight_ok = (
		str(result.get("source_sha256", "")) == _selected_import_source_id.trim_prefix("owner-upload-")
		and str(source_authority.get("source_id", "")) == _selected_import_source_id
		and str(source_authority.get("source_sha256", "")) == _selected_import_source_id.trim_prefix("owner-upload-")
		and bool(result.get("exact_logical_source", false))
		and str(capability.get("state", "")) in ["OPEN", "NOT_REQUIRED"]
		and str(structural.get("disposition", "")) == "PASS"
	)
	if _pinned_source_preflight_ok:
		_pinned_source_preflight_message = "SOURCE/VOID PASS · NOT SHIPPING"
		_activity_stage = "SOURCE VERIFIED"
		_activity_message = _pinned_source_preflight_message
	else:
		_pinned_source_preflight_message = str(result.get("reason", result.get("error", capability.get("reason", "Source preflight is unavailable."))))
		_activity_stage = "AUTHORITY"
		_activity_message = _pinned_source_preflight_message
	_refresh_activity_header()


func _page_imported_sources(direction: int) -> void:
	if _operation_running and not _batch_job_id.is_empty():
		return
	_imported_window_start = clampi(_imported_window_start + direction, 0, maxi(0, _gameplay_sources.size() - 5))
	_refresh_runtime_cards()


func _unhandled_input(event: InputEvent) -> void:
	if _screen != "LEVEL FACTORY" or _gameplay_sources.size() <= 5 or _preview_host == null:
		return
	if not event is InputEventMouseButton:
		return
	var mouse := event as InputEventMouseButton
	if not mouse.pressed or mouse.button_index not in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
		return
	var strip := get_node_or_null("RuntimeBottomStrip") as Control
	if strip == null or not strip.get_global_rect().has_point(mouse.global_position):
		return
	_page_imported_sources(-1 if mouse.button_index == MOUSE_BUTTON_WHEEL_UP else 1)
	get_viewport().set_input_as_handled()


func _select_inbox_candidate(index: int) -> void:
	_request_candidate_inbox_refresh()
	var inbox := _candidate_inbox_cache
	var candidates: Array = inbox.get("candidates", [])
	if index < 0 or index >= candidates.size():
		if candidates.is_empty():
			_report("Artwork candidates are still loading. You can keep using the other screens.")
		return
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
	_run_single_level_pipeline()


func _preview_replay() -> void:
	var primary := _pipeline_primary_for_selected_source()
	var verified := _verify_saved_solver_artifacts(primary)
	if not verified.get("ok", false):
		_show_inline_result_error("REPLAY_EVIDENCE_MISSING · %s" % str(verified.get("reason", "Source-bound proof is unavailable.")))
		return
	var result: Dictionary = primary.get("result", {})
	var replay: Dictionary = result.get("solution_replay", {})
	_replay_trace = result.get("solution_trace", [])
	if replay.is_empty() or _replay_trace.is_empty():
		_show_inline_result_error("REPLAY_EVIDENCE_MISSING · the canonical run has no recorded solution trace.")
		return
	var replay_won := bool(replay.get("ok", false)) and bool(replay.get("solved", false)) and int(replay.get("finalActive", -1)) == 0
	_results_mode = "REPLAY"
	_results_source_id = _selected_import_source_id
	_results_run_id = str(_last_pipeline.get("run_id", ""))
	_clear_result_rows()
	_results_nav.visible = true
	_results_panel.visible = true
	_replay_step = 0
	_results_summary.text = "TRACE-ONLY · %s · %d steps" % ["WIN" if replay_won else "REPLAY_NOT_WIN", _replay_trace.size()]
	_results_summary.tooltip_text = "Source %s\nRun %s\nActivity %s\nRecorded trace only; visual board states are not stored." % [
		_results_source_id, _results_run_id, str(_last_pipeline.get("request", {}).get("activity_run_id", ""))
	]
	if not replay_won:
		_add_result_row("Replay did not prove WIN.")
	_set_replay_step(0)
	_refresh_live_data()


func _set_replay_step(index: int) -> void:
	if _replay_trace.is_empty() or _results_mode != "REPLAY" or _selected_import_source_id != _results_source_id or str(_last_pipeline.get("run_id", "")) != _results_run_id:
		return
	_replay_step = posmod(index, _replay_trace.size())
	var step: Dictionary = _replay_trace[_replay_step]
	var batch: Dictionary = step.get("batch", {})
	_clear_result_rows()
	_add_result_row("Step %d / %d" % [_replay_step + 1, _replay_trace.size()])
	_add_result_row("Column: %s" % str(step.get("column", "?")))
	_add_result_row("Batch: %s × %s" % [str(batch.get("color", "?")), str(batch.get("amount", "?"))])
	_add_result_row("Clears: %s" % str(step.get("clears", "?")))
	_add_result_row("Pixels left: %s" % str(step.get("pixels_left", "?")))
	_results_scroll.scroll_vertical = 0
	_results_summary.text = "TRACE-ONLY · Step %d / %d" % [_replay_step + 1, _replay_trace.size()]


func _toggle_supply_plan() -> void:
	var primary := _pipeline_primary_for_selected_source()
	var verified := _verify_saved_solver_artifacts(primary)
	if not verified.get("ok", false):
		_show_inline_result_error("SUPPLY_PLAN_HASH_INVALID · %s" % str(verified.get("reason", "Canonical supply evidence is unavailable.")))
		return
	var result: Dictionary = primary.get("result", {})
	var columns: Array = result.get("supply_columns", [])
	if columns.is_empty():
		_show_inline_result_error("SUPPLY_PLAN_MISSING · canonical result contains no supply columns.")
		return
	_results_mode = "SUPPLY"
	_results_source_id = _selected_import_source_id
	_results_run_id = str(_last_pipeline.get("run_id", ""))
	_results_nav.visible = false
	_results_panel.visible = true
	_clear_result_rows()
	var totals: Array = result.get("column_pixel_totals", [])
	var total_robots := 0
	for column_variant in columns:
		if column_variant is Array:
			for batch_variant in column_variant:
				if batch_variant is Dictionary:
					total_robots += int(batch_variant.get("amount", 0))
	var total_pixels := 0
	for amount_variant in totals:
		total_pixels += int(amount_variant)
	_results_summary.text = "%d columns · %d batches · preview depth %d" % [columns.size(), int(result.get("total_batches", 0)), int(result.get("visible_preview_depth", 3))]
	_results_summary.tooltip_text = "Source %s\nRun %s" % [_results_source_id, _results_run_id]
	_add_result_row("Total robots: %d · total pixels: %d" % [total_robots, total_pixels])
	for column_index in range(columns.size()):
		_add_result_row("Column %d · %s pixels" % [column_index + 1, str(totals[column_index]) if column_index < totals.size() else "?"])
		for batch_variant in columns[column_index]:
			if batch_variant is Dictionary:
				_add_supply_batch_row(str(batch_variant.get("color", "?")), int(batch_variant.get("amount", 0)))
	var conservation: Dictionary = result.get("color_conservation_verification", {})
	_add_result_row("Conservation: %s" % ("PASS" if conservation.get("all_ok", false) else "NOT VERIFIED"))
	_results_scroll.scroll_vertical = 0
	_refresh_live_data()


func _show_inline_result_error(message: String) -> void:
	_results_mode = "ERROR"
	_results_source_id = _selected_import_source_id
	_results_run_id = str(_last_pipeline.get("run_id", "")) if str(_last_pipeline.get("source_id", "")) == _selected_import_source_id else ""
	_results_nav.visible = false
	_results_panel.visible = true
	_clear_result_rows()
	_results_summary.text = "Results unavailable"
	_results_summary.tooltip_text = message
	_add_result_row(message)
	_report(message)


func _selected_batch_column() -> int:
	var items: Array = _batch_snapshot.get("items", [])
	for item_variant in items:
		if item_variant is Dictionary and str(item_variant.get("source_id", "")) == _selected_import_source_id:
			return int(item_variant.get("column_count", 0))
	return 0


func _pipeline_primary_for_selected_source() -> Dictionary:
	if str(_last_pipeline.get("source_id", "")) != _selected_import_source_id or str(_last_pipeline.get("disposition", "")) != "READY":
		return {}
	var request: Dictionary = _last_pipeline.get("request", {})
	if str(request.get("source_id", "")) != _selected_import_source_id or str(request.get("activity_source_sha256", "")) != _selected_import_source_id.trim_prefix("owner-upload-") or str(request.get("activity_run_id", "")).is_empty() or str(_last_pipeline.get("run_id", "")).is_empty():
		return {}
	return _last_pipeline.get("primary", {})


func _verify_saved_solver_artifacts(primary: Dictionary) -> Dictionary:
	if primary.is_empty():
		return {"ok": false, "reason": "SOURCE_RUN_MISMATCH"}
	var result: Dictionary = primary.get("result", {})
	var identity: Dictionary = primary.get("solver_supply_identity", {})
	if result.is_empty() or identity.is_empty() or result.get("solver_supply_identity") != identity:
		return {"ok": false, "reason": "REPLAY_HASH_INVALID · solver/supply identity differs"}
	var files: Dictionary = primary.get("files", {})
	var paths := {
		"level": str(files.get("level", "")),
		"supply_plan": str(files.get("supply_plan", "")),
		"result": str(files.get("result", ""))
	}
	var digests := {
		"level": str(identity.get("level_data_sha256", "")),
		"supply_plan": str(identity.get("supply_plan_sha256", ""))
	}
	for key in ["level", "supply_plan"]:
		if paths[key].is_empty() or not FileAccess.file_exists(paths[key]):
			return {"ok": false, "reason": "missing saved %s artifact" % key}
		var bytes := FileAccess.get_file_as_bytes(paths[key])
		var hash_ctx := HashingContext.new()
		hash_ctx.start(HashingContext.HASH_SHA256)
		hash_ctx.update(bytes)
		if hash_ctx.finish().hex_encode() != digests[key]:
			return {"ok": false, "reason": "%s SHA-256 differs from solver_supply_identity" % key}
	if paths["result"].is_empty() or not FileAccess.file_exists(paths["result"]):
		return {"ok": false, "reason": "missing saved canonical result"}
	var result_data: Variant = JSON.parse_string(FileAccess.get_file_as_string(paths["result"]))
	if not result_data is Dictionary or result_data != result:
		return {"ok": false, "reason": "saved result differs from the source-bound pipeline trace"}
	return {"ok": true}


func _hide_review_dialogs() -> void:
	if _supply_dialog != null:
		_supply_dialog.hide()
	_supply_expanded = false
	if _replay_dialog != null:
		_replay_dialog.hide()
	if _results_panel != null:
		_results_panel.visible = false
	_results_mode = ""
	_results_source_id = ""
	_results_run_id = ""


func _edit_release_search() -> void:
	_release_search.text = _release_query
	var dialog := ConfirmationDialog.new(); dialog.title = "Search Levels"; dialog.add_child(_release_search)
	dialog.confirmed.connect(func():
		_release_query = _release_search.text
		_apply_release_projection()
		_append_release_pool_activity("SEARCH", "APPLIED", "query=%s; visible=%d" % [_release_query, _visible_release_ids.size()])
		dialog.remove_child(_release_search)
		dialog.queue_free()
	)
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
	_append_release_pool_activity("FILTERS", "APPLIED", "difficulty=%s; columns=%s; visible=%d" % [_difficulty_filter, _columns_filter, _visible_release_ids.size()])


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
	_release_candidate_signature = ""
	_refresh_release_candidate_rows()


func _release_entry_for_id(candidate_id: String) -> Dictionary:
	for entry_variant in _release_pool.get("entries", []):
		if entry_variant is Dictionary and str(entry_variant.get("candidate_id", "")) == candidate_id:
			return entry_variant
	return {}


func _refresh_release_candidate_rows() -> void:
	if _release_candidate_rows == null:
		return
	var signature_parts := PackedStringArray()
	for candidate_id in _visible_release_ids:
		var entry := _release_entry_for_id(candidate_id)
		var primary: Dictionary = entry.get("pipeline", {}).get("primary", {})
		signature_parts.append("%s:%s:%s" % [candidate_id, str(primary.get("disposition", primary.get("state", "READY"))), "1" if candidate_id in _selected_release_ids else "0"])
	var signature := "%s|%.2f" % [";".join(signature_parts), _release_candidate_row_height]
	if signature == _release_candidate_signature and _release_candidate_rows.get_child_count() == _visible_release_ids.size():
		return
	_release_candidate_signature = signature
	for child in _release_candidate_rows.get_children():
		_release_candidate_rows.remove_child(child)
		child.queue_free()
	for index in range(_visible_release_ids.size()):
		var candidate_id := _visible_release_ids[index]
		var entry := _release_entry_for_id(candidate_id)
		if entry.is_empty():
			continue
		var primary: Dictionary = entry.get("pipeline", {}).get("primary", {})
		var state := str(primary.get("disposition", primary.get("state", "READY"))).to_upper()
		if state.is_empty():
			state = "READY"
		var title := str(entry.get("level_id", entry.get("name", entry.get("candidate", {}).get("level_id", candidate_id))))
		var artwork := str(entry.get("files", {}).get("artwork", {}).get("path", entry.get("artwork_path", "")))
		var selected_mark := "✓ " if candidate_id in _selected_release_ids else ""
		var row := Button.new()
		row.name = "ReleaseCandidate_%d_%d" % [_release_activity_events.size(), index]
		row.text = "%s%s  ·  %s" % [selected_mark, title.left(28), state.left(12)]
		row.icon = _runtime_png_texture(artwork) if not artwork.is_empty() else null
		row.icon_alignment = HORIZONTAL_ALIGNMENT_LEFT
		row.vertical_icon_alignment = VERTICAL_ALIGNMENT_CENTER
		row.expand_icon = not artwork.is_empty()
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.custom_minimum_size = Vector2(0, _release_candidate_row_height)
		row.focus_mode = Control.FOCUS_ALL
		row.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		row.tooltip_text = "Candidate %s\nRun %s\nPipeline SHA-256 %s\nPool entry SHA-256 %s" % [candidate_id, str(entry.get("pipeline_run_id", "UNKNOWN")), str(entry.get("pipeline_sha256", "UNKNOWN")), str(entry.get("entry_digest", "UNKNOWN"))]
		row.add_theme_font_size_override("font_size", 11)
		row.add_theme_color_override("font_color", Color("#dce8f8"))
		row.add_theme_stylebox_override("normal", _control_style(Color("#17243a"), Color("#30415e")))
		row.add_theme_stylebox_override("hover", _control_style(Color("#233651"), Color("#6b8bb9")))
		row.pressed.connect(_select_release_candidate_id.bind(candidate_id))
		_release_candidate_rows.add_child(row)


func _select_release_candidate_id(candidate_id: String) -> void:
	if _release_entry_for_id(candidate_id).is_empty():
		return
	var changed := false
	if _release_selection_manage_mode:
		if candidate_id in _selected_release_ids:
			_selected_release_ids.erase(candidate_id)
		else:
			_selected_release_ids.append(candidate_id)
		changed = true
	_selected_release_id = candidate_id
	_select_release_entry(candidate_id)
	_release_candidate_signature = ""
	_refresh_release_candidate_rows()
	_append_release_pool_activity("CANDIDATE SELECTION" if changed else "CANDIDATE PREVIEW", "UPDATED" if changed else "READ ONLY", "candidate_id=%s" % candidate_id, [candidate_id])


func _select_release_row(index: int) -> void:
	if index < 0 or index >= _visible_release_ids.size(): return
	_select_release_candidate_id(_visible_release_ids[index])


func _manage_release_selection() -> void:
	_release_selection_manage_mode = not _release_selection_manage_mode
	_append_release_pool_activity("MANAGE SELECTION", "OPEN" if _release_selection_manage_mode else "CLOSED", "candidate IDs remain bound to the canonical filtered list")
	_report("Manage selection %s" % ("active" if _release_selection_manage_mode else "closed"))


func _select_all_release() -> void:
	_selected_release_ids.clear()
	for candidate_id in _visible_release_ids:
		if candidate_id not in _selected_release_ids: _selected_release_ids.append(candidate_id)
	_release_candidate_signature = ""
	_refresh_release_candidate_rows()
	_append_release_pool_activity("SELECT ALL FILTERED", "SELECTED %d" % _selected_release_ids.size(), "selected every candidate in the filtered result set")


func _clear_release_selection() -> void:
	_selected_release_ids.clear()
	_release_candidate_signature = ""
	_refresh_release_candidate_rows()
	_append_release_pool_activity("CLEAR SELECTION", "CLEARED", "all selected candidate IDs were removed")


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
	if index >= 0 and index < _selected_release_ids.size():
		var removed := _selected_release_ids[index]
		_selected_release_ids.remove_at(index)
		_release_candidate_signature = ""
		_refresh_release_candidate_rows()
		_refresh_live_data()
		_append_release_pool_activity("REMOVE SELECTION", "REMOVED", "candidate_id=%s" % removed, [removed])


func _set_release_target(target: String) -> void:
	_release_target = target if target in ["STAGING", "PRODUCTION"] else "STAGING"
	_append_release_pool_activity("TARGET", "SELECTED", "target=%s; no publish was started" % _release_target)
	if target == "PRODUCTION":
		_report("PRODUCTION requires a verified STAGING manifest and exact owner approval")


func _upload_selected() -> void:
	if _selected_release_ids.is_empty():
		_append_release_pool_activity("UPLOAD SELECTED", "BLOCKED", "Select one or more READY levels before uploading.", [])
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
		_append_release_pool_activity("PRODUCTION PROMOTION", "BLOCKED", "Current verified preflight and manifest identity are required.", _selected_release_ids)
		_report("Run a current publish preflight before requesting PRODUCTION confirmation.")
		return
	_pending_production_confirmation = {"manifest_sha256": manifest_sha, "content_version": version}
	_append_release_pool_activity("PRODUCTION PROMOTION", "OWNER CONFIRMATION REQUIRED", "Exact manifest SHA-256 %s; content version %d" % [manifest_sha, version], _selected_release_ids)
	_release_confirmation.dialog_text = "Promote this exact reviewed release?\n\nManifest SHA-256: %s\nContent version: %d\nTarget: PRODUCTION\n\nThe canonical publisher will verify STAGING bytes and current-main replay before promotion." % [manifest_sha, version]
	_release_confirmation.popup_centered()


func _publish_production_confirmed() -> void:
	if _pending_production_confirmation.is_empty(): return
	var reviewed: Dictionary = _release_pool.get("publish_preflight", {}).get("reviewed_identity", {})
	var approval_id := "factory-studio-owner-confirm-%d-%d" % [OS.get_process_id(), Time.get_ticks_usec()]
	var owner_id := OS.get_environment("USERNAME").strip_edges()
	if owner_id.is_empty(): owner_id = OS.get_environment("USER").strip_edges()
	if owner_id.is_empty():
		_append_release_pool_activity("PRODUCTION PUBLISH", "BLOCKED", "Owner identity is unavailable; no publisher call was made.", _selected_release_ids)
		_report("Production approval cannot be attributed to the current local owner session.")
		_pending_production_confirmation.clear()
		return
	var confirmation := {"confirmed": true, "approval_id": approval_id, "owner_id": owner_id,
		"manifest_sha256": _pending_production_confirmation.get("manifest_sha256", ""),
		"content_version": _pending_production_confirmation.get("content_version", 0), "target": "PRODUCTION"}
	if confirmation.manifest_sha256 != reviewed.get("candidate_manifest_sha256") or confirmation.content_version != reviewed.get("content_version"):
		_append_release_pool_activity("PRODUCTION PUBLISH", "BLOCKED", "Reviewed manifest identity changed; no publisher call was made.", _selected_release_ids)
		_report("Reviewed production identity changed. Run preflight again.")
		_pending_production_confirmation.clear()
		return
	_append_release_pool_activity("PRODUCTION PUBLISH", "STARTED", "explicit owner confirmation submitted", _selected_release_ids)
	var result := _extension("scrubbots-publish", {"action": "publish-production",
		"candidate_ids": _selected_release_ids, "pack_id": "factory-studio-release",
		"content_version": int(reviewed.get("content_version", 0)),
		"created_at_utc": str(reviewed.get("created_at_utc", "")),
		"reviewed_identity": reviewed, "owner_confirmation": confirmation})
	_pending_production_confirmation.clear()
	_append_release_pool_activity("PRODUCTION PUBLISH", str(result.get("state", result.get("disposition", "UNAVAILABLE"))), _release_activity_result_detail(result), _selected_release_ids)
	_report("PRODUCTION: %s · %s" % [str(result.get("state", "UNAVAILABLE")), str(result.get("production", ""))])


func _preview_release_manifest() -> void:
	if _release_pool.get("publish_preflight", {}).is_empty():
		_append_release_pool_activity("PREVIEW MANIFEST", "BLOCKED", "No preflight manifest is available. Run Preflight explicitly first.", _selected_release_ids)
		_report("No preflight manifest. Run Preflight explicitly first.")
		return
	var result: Dictionary = _release_pool.get("publish_preflight", {})
	_append_release_pool_activity("PREVIEW MANIFEST", str(result.get("state", "UNAVAILABLE")), "read-only preview of the last preflight response", _selected_release_ids)
	var dialog := AcceptDialog.new(); dialog.title = "Release Manifest Preview"
	var label := RichTextLabel.new(); label.custom_minimum_size = Vector2(680, 380); label.text = JSON.stringify(result, "  "); label.fit_content = true
	dialog.add_child(label); add_child(dialog); dialog.confirmed.connect(func(): dialog.queue_free()); dialog.popup_centered()


func _extension(operation: String, request: Dictionary) -> Dictionary:
	if _gateway == null or not _gateway.has_method("run_studio_extension"):
		return {"state": "UNAVAILABLE", "reason": "Canonical Factory Core gateway is unavailable."}
	var result: Variant = _gateway.call("run_studio_extension", operation, request)
	return result if result is Dictionary else {"state": "ERROR", "reason": "Canonical operation returned no structured result."}
