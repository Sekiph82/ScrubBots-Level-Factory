@tool
class_name FactoryStudioPipeline
extends VBoxContainer

var _gateway: RefCounted
var _source_control: LineEdit
var _candidate_control: LineEdit
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
	var request := {"source_id": source} if not source.is_empty() else {"candidate_id": candidate}
	if _gateway == null or (source.is_empty() and candidate.is_empty()):
		_projection = {"state": "UNAVAILABLE", "disposition": "UNAVAILABLE", "error": "UNAVAILABLE — choose one canonical source or candidate identity."}
	else:
		_projection = _gateway.call("run_studio_extension", "pipeline", request)
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
	_state_label = Label.new(); _state_label.name = "PipelineState"; _state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_state_label)
	_timeline_label = Label.new(); _timeline_label.name = "PipelineTimeline"; _timeline_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_timeline_label)


func _render() -> void:
	if _state_label == null: return
	_state_label.text = "Pipeline: %s | run=%s\n%s" % [_projection.get("disposition", _projection.get("state", "EMPTY")), _projection.get("run_id", "NOT AVAILABLE"), _projection.get("error", "")]
	var stages: Array = _projection.get("stages", [])
	var entries: Array[String] = []
	for stage in stages: entries.append("%s=%s" % [stage.get("stage", ""), stage.get("disposition", "")])
	_timeline_label.text = "Stage timeline: %s" % " → ".join(entries) if not entries.is_empty() else "Stage timeline: NOT AVAILABLE"
