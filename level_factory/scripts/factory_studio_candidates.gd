@tool
class_name FactoryStudioCandidates
extends VBoxContainer

var _gateway: RefCounted
var _projection: Dictionary = {}
var _candidate_control: LineEdit
var _peer_control: LineEdit
var _reason_control: LineEdit
var _state_label: Label
var _list_label: Label
var _details_label: Label
var _comparison_projection: Dictionary = {}


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
func rendered_text() -> String: return "%s\n%s\n%s" % [_state_label.text if _state_label != null else "", _list_label.text if _list_label != null else "", _details_label.text if _details_label != null else ""]
func set_comparison_ids(left_id: String, right_id: String) -> void:
	if _candidate_control != null: _candidate_control.text = left_id
	if _peer_control != null: _peer_control.text = right_id


func show_candidates() -> void: _render()


func _build_controls() -> void:
	var heading := Label.new(); heading.text = "Candidate Inbox / Owner Review Queue — derived canonical candidates"; heading.add_theme_font_size_override("font_size", 18); add_child(heading)
	var notice := Label.new(); notice.text = "Only real candidate bundles appear. ACCEPT/REJECT appends evidence bound to candidate and artwork identity; QA never implies owner acceptance."; notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(notice)
	var row := HBoxContainer.new(); _candidate_control = LineEdit.new(); _candidate_control.name = "ReviewCandidateId"; _candidate_control.placeholder_text = "candidate ID"; _candidate_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_candidate_control); _peer_control = LineEdit.new(); _peer_control.name = "SimilarityPeerId"; _peer_control.placeholder_text = "canonical peer ID"; _peer_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_peer_control); var compare := Button.new(); compare.text = "Compare canonical peer"; compare.pressed.connect(compare_selected); row.add_child(compare); _reason_control = LineEdit.new(); _reason_control.name = "ReviewReason"; _reason_control.placeholder_text = "reason/note"; _reason_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(_reason_control)
	var accept := Button.new(); accept.text = "ACCEPT"; accept.pressed.connect(review_selected.bind("ACCEPT")); row.add_child(accept)
	var reject := Button.new(); reject.text = "REJECT"; reject.pressed.connect(review_selected.bind("REJECT")); row.add_child(reject)
	var refresh := Button.new(); refresh.text = "Refresh"; refresh.pressed.connect(refresh_inbox); row.add_child(refresh); add_child(row)
	_state_label = Label.new(); _state_label.name = "CandidateInboxState"; _state_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_state_label)
	_list_label = Label.new(); _list_label.name = "CandidateInboxItems"; _list_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_list_label)
	_details_label = Label.new(); _details_label.name = "CandidateEvidenceDetails"; _details_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; add_child(_details_label)


func _render() -> void:
	if _state_label == null: return
	_state_label.text = "Candidate Inbox: %s | owner review is append-only" % _projection.get("state", "EMPTY")
	var rows: Array[String] = []
	var selected: Dictionary = {}
	for candidate in _projection.get("candidates", []):
		rows.append("%s=%s" % [candidate.get("candidate_id", ""), candidate.get("owner_review", {}).get("disposition", "NEEDS_REVIEW")])
		if str(candidate.get("candidate_id", "")) == _candidate_control.text.strip_edges(): selected = candidate
	_list_label.text = "Queue: %s\nSimilarity advisory only; owner review decides significance. Peer action: enter a canonical peer ID and Compare." % ", ".join(rows) if not rows.is_empty() else "Queue: no trusted canonical candidates; unsupported origins remain unavailable.\nSimilarity: NOT AVAILABLE — select a canonical peer before Compare."
	if _details_label != null:
		if selected.is_empty():
			_details_label.text = "Selected candidate evidence: enter a candidate ID and refresh."
		else:
			var advisory: Dictionary = _comparison_projection.get("similarity_advisory", selected.get("similarity_advisory", {}))
			_details_label.text = "Selected candidate evidence: id=%s | artwork=%s | grid=%s | dimensions=%sx%s | provenance=%s | structural/QA=%s | similarity=%s | owner-review=%s | solver=%s | difficulty=%s | immutable references=%s | invalid review=%s\nSimilarity advisory only; owner review decides significance." % [selected.get("candidate_id", ""), selected.get("artwork_sha256", ""), selected.get("grid_hash", ""), selected.get("width", ""), selected.get("height", ""), selected.get("provenance", {}), selected.get("structural", {}).get("decision", selected.get("structural", {}).get("disposition", "NOT AVAILABLE")), advisory.get("disposition", "NOT AVAILABLE"), selected.get("owner_review", {}).get("disposition", "NEEDS_REVIEW"), selected.get("solver", {}).get("disposition", "NOT AVAILABLE"), selected.get("difficulty", {}).get("disposition", "NOT AVAILABLE"), selected.get("evidence_references", []), selected.get("owner_review_invalid", [])]

func compare_selected() -> void:
	var left_id := _candidate_control.text.strip_edges() if _candidate_control != null else ""
	var right_id := _peer_control.text.strip_edges() if _peer_control != null else ""
	if left_id.is_empty() or right_id.is_empty() or left_id == right_id:
		_comparison_projection = {"similarity_advisory": {"disposition": "NOT AVAILABLE", "reason": "Select two different canonical candidate IDs before Compare; similarity is advisory only and owner review decides significance."}}
	else:
		_comparison_projection = _gateway.call("run_studio_extension", "comparison", {"candidate_ids": [left_id, right_id]}) if _gateway != null else {"similarity_advisory": {"disposition": "NOT AVAILABLE", "reason": "Gateway unavailable."}}
	_render()
