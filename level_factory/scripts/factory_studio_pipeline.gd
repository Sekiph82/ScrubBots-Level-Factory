@tool
class_name FactoryStudioPipeline
extends VBoxContainer

var _gateway: RefCounted
var _source_control: LineEdit
var _candidate_control: LineEdit
var _primary_image_control: LineEdit
var _column_count_control: OptionButton
var _state_label: Label
var _timeline_label: Label
var _projection: Dictionary = {}


func _ready() -> void:
	if get_child_count() == 0: _build_controls()
	_render()


func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway


func run_pipeline(source_id: String = "", candidate_id: String = "") -> void:
	var source := source_id if not source_id.is_empty() else (_source_control.text.strip_edges() if _source_control != null else "")
	var candidate := candidate_id if not candidate_id.is_empty() else (_candidate_control.text.strip_edges() if _candidate_control != null else "")
	if source.is_empty() and candidate.is_empty() and _primary_image_control != null and not _primary_image_control.text.strip_edges().is_empty():
		run_primary_pipeline()
		return
	var request := {"source_id": source} if not source.is_empty() else {"candidate_id": candidate}
	request["column_count"] = _selected_column_count()
	if _gateway == null or (source.is_empty() and candidate.is_empty()):
		_projection = {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "error": "UNAVAILABLE — choose one canonical source or candidate identity."}
	else:
		_projection = _gateway.call("run_studio_extension", "pipeline", request)
	_render()


func run_primary_pipeline(image_path: String = "", output_dir: String = "") -> void:
	var image := image_path if not image_path.is_empty() else (_primary_image_control.text.strip_edges() if _primary_image_control != null else "")
	if _gateway == null or image.is_empty():
		_projection = {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "error": "UNAVAILABLE — choose a local logical-grid image for the primary supply route."}
	else:
		_projection = _gateway.call("run_studio_extension", "pipeline", {"image_path": image, "output_dir": output_dir, "column_count": _selected_column_count()})
	_render()


func snapshot() -> Dictionary: return _projection.duplicate(true)


func show_pipeline() -> void: _render()


func _build_controls() -> void:
	var heading := Label.new(); heading.text = "One-Click Pipeline — canonical stage orchestration"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
	var notice := Label.new(); notice.text = "SOURCE → NORMALIZE/DERIVE → PALETTE/STRUCTURE VALIDATION → CANDIDATE → SOLVE → DIFFICULTY → QA → REVIEW. The first real failure or unavailable dependency stops the run."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
	var row := HBoxContainer.new()
	_source_control = LineEdit.new(); _source_control.name = "PipelineSourceId"; _source_control.placeholder_text = "OWNER_UPLOAD source ID"; _source_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_source_control)
	_candidate_control = LineEdit.new(); _candidate_control.name = "PipelineCandidateId"; _candidate_control.placeholder_text = "or candidate ID"; _candidate_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_candidate_control)
	var button := Button.new(); button.name = "RunPipeline"; button.text = "Run Pipeline"; button.pressed.connect(run_pipeline); row.add_child(button); add_child(row)
	var primary_row := HBoxContainer.new()
	_primary_image_control = LineEdit.new(); _primary_image_control.name = "PrimarySupplyImage"; _primary_image_control.placeholder_text = "local logical-grid PNG — primary ZIP supply route"; _primary_image_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; primary_row.add_child(_primary_image_control)
	var primary_button := Button.new(); primary_button.name = "RunPrimarySupplyPipeline"; primary_button.text = "Run Primary Supply"; primary_button.pressed.connect(run_primary_pipeline); primary_row.add_child(primary_button); add_child(primary_row)
	var columns_row := HBoxContainer.new()
	var columns_label := Label.new(); columns_label.text = "Supply columns (preview depth fixed at 3)"; columns_row.add_child(columns_label)
	_column_count_control = OptionButton.new(); _column_count_control.name = "SupplyColumnCount"; _column_count_control.add_item("3"); _column_count_control.add_item("4"); _column_count_control.add_item("5"); _column_count_control.select(0); columns_row.add_child(_column_count_control); add_child(columns_row)
	_state_label = Label.new(); _state_label.name = "PipelineState"; _state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_state_label)
	_timeline_label = Label.new(); _timeline_label.name = "PipelineTimeline"; _timeline_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_timeline_label)


func _render() -> void:
	if _state_label == null: return
	_state_label.text = "Pipeline: %s | run=%s\n%s" % [_projection.get("disposition", _projection.get("state", "EMPTY")), _projection.get("run_id", "NOT AVAILABLE"), _projection.get("error", "")]
	var stages: Array = _projection.get("stages", [])
	var entries: Array[String] = []
	for stage in stages: entries.append("%s=%s" % [stage.get("stage", ""), stage.get("disposition", "")])
	_timeline_label.text = "Stage timeline: %s" % " → ".join(entries) if not entries.is_empty() else "Stage timeline: NOT AVAILABLE"


func _selected_column_count() -> int:
	return int(_column_count_control.get_item_text(_column_count_control.selected)) if _column_count_control != null and _column_count_control.selected >= 0 else 3
