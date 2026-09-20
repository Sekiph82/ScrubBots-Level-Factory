@tool
class_name FactoryStudioCandidates
extends VBoxContainer

var _gateway: RefCounted
var _projection: Dictionary = {}
var _candidate_control: LineEdit
var _reason_control: LineEdit
var _state_label: Label
var _list_label: Label


func _ready() -> void:
	if get_child_count() == 0: _build_controls()
	_render()


func configure_gateway(gateway: RefCounted) -> void: _gateway = gateway


func refresh_inbox() -> void:
	_projection = _gateway.call("run_studio_extension", "candidate-inbox", {}) if _gateway != null else {"state": "UNAVAILABLE", "error": "Gateway unavailable."}
	_render()


func review_selected(disposition: String) -> void:
	if _gateway == null: return
	var result: Dictionary = _gateway.call("run_studio_extension", "owner-review", {"candidate_id": _candidate_control.text.strip_edges(), "disposition": disposition, "reason": _reason_control.text.strip_edges()})
	_projection["last_review"] = result
	refresh_inbox()


func snapshot() -> Dictionary: return _projection.duplicate(true)


func show_candidates() -> void: _render()


func _build_controls() -> void:
	var heading := Label.new(); heading.text = "Candidate Inbox / Owner Review Queue — derived canonical candidates"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
	var notice := Label.new(); notice.text = "Only real candidate bundles appear. ACCEPT/REJECT appends evidence bound to candidate and artwork identity; QA never implies owner acceptance."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
	var row := HBoxContainer.new(); _candidate_control = LineEdit.new(); _candidate_control.name = "ReviewCandidateId"; _candidate_control.placeholder_text = "candidate ID"; _candidate_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_candidate_control); _reason_control = LineEdit.new(); _reason_control.name = "ReviewReason"; _reason_control.placeholder_text = "reason/note"; _reason_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_reason_control)
	var accept := Button.new(); accept.text = "ACCEPT"; accept.pressed.connect(review_selected.bind("ACCEPT")); row.add_child(accept)
	var reject := Button.new(); reject.text = "REJECT"; reject.pressed.connect(review_selected.bind("REJECT")); row.add_child(reject)
	var refresh := Button.new(); refresh.text = "Refresh"; refresh.pressed.connect(refresh_inbox); row.add_child(refresh); add_child(row)
	_state_label = Label.new(); _state_label.name = "CandidateInboxState"; _state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_state_label)
	_list_label = Label.new(); _list_label.name = "CandidateInboxItems"; _list_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_list_label)


func _render() -> void:
	if _state_label == null: return
	_state_label.text = "Candidate Inbox: %s | owner review is append-only" % _projection.get("state", "EMPTY")
	var rows: Array[String] = []
	for candidate in _projection.get("candidates", []): rows.append("%s=%s" % [candidate.get("candidate_id", ""), candidate.get("owner_review", {}).get("disposition", "NEEDS_REVIEW")])
	_list_label.text = "Queue: %s" % ", ".join(rows) if not rows.is_empty() else "Queue: no trusted canonical candidates; unsupported origins remain unavailable."
