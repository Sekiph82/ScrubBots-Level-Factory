@tool
class_name FactoryStudioDashboard
extends VBoxContainer

## Read-only Factory Operations Dashboard derived from a canonical batch manifest.
## Python Factory Core owns validation and replay; this node only presents its result.

const DASHBOARD_OPERATION := "factory-operations-dashboard-inspection"
const OUTPUT_PREFIX := "res://output/"

var _core_gateway: RefCounted
var _action_source: Node
var _projection: Dictionary = {}
var _manifest_path_control: LineEdit
var _state_label: Label
var _summary_label: Label
var _request_label: Label
var _disposition_label: Label
var _rejection_label: Label
var _latest_label: Label
var _unavailable_label: Label
var _studio_evidence_label: Label


func _ready() -> void:
	if get_child_count() == 0:
		_build_controls()
	_set_empty()


func configure_gateway(gateway: RefCounted) -> void:
	_core_gateway = gateway


func configure_action_source(source: Node) -> void:
	_action_source = source
	_render()


func set_manifest_relative_path(relative_path: String) -> void:
	if _manifest_path_control != null:
		_manifest_path_control.text = relative_path


func refresh_manifest() -> void:
	var relative_path := _manifest_path_control.text.strip_edges() if _manifest_path_control != null else ""
	if relative_path.is_empty():
		_set_empty()
		return
	if not _valid_relative_path(relative_path):
		_set_error("ERROR — choose a batch-manifest.json below res://output/.")
		return
	if _core_gateway == null or not _core_gateway.has_method("run_dashboard_inspection"):
		_set_error("UNAVAILABLE — canonical dashboard inspection is not connected.")
		return
	var result: Variant = _core_gateway.call("run_dashboard_inspection", OUTPUT_PREFIX + relative_path)
	if result is Dictionary:
		_projection = result.duplicate(true)
	else:
		_set_error("ERROR — dashboard inspection returned no structured result.")
	_render()


func show_dashboard() -> void:
	_render()


func snapshot() -> Dictionary:
	var result := _projection.duplicate(true)
	result["studio_evidence"] = _studio_evidence_snapshot()
	return result


func _build_controls() -> void:
	var heading := Label.new()
	heading.text = "Factory Operations Dashboard — read-only canonical batch view"
	heading.add_theme_font_size_override("font_size", 18)
	add_child(heading)

	var explanation := Label.new()
	explanation.text = "Refresh a canonical batch-manifest.json from res://output/. This view derives evidence only; it does not edit manifests, schedule work, accept ownership, solve puzzles, or measure difficulty."
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(explanation)

	var path_row := HBoxContainer.new()
	var path_label := Label.new()
	path_label.text = "Canonical batch path"
	path_label.custom_minimum_size = Vector2(180, 0)
	path_row.add_child(path_label)
	_manifest_path_control = LineEdit.new()
	_manifest_path_control.name = "ManifestPath"
	_manifest_path_control.placeholder_text = "relative path under output/.../batch-manifest.json"
	_manifest_path_control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_manifest_path_control.text_submitted.connect(_on_path_submitted)
	path_row.add_child(_manifest_path_control)
	var refresh_button := Button.new()
	refresh_button.name = "RefreshManifest"
	refresh_button.text = "Refresh canonical manifest"
	refresh_button.pressed.connect(refresh_manifest)
	path_row.add_child(refresh_button)
	add_child(path_row)

	_state_label = _make_label("State")
	_summary_label = _make_label("BatchSummary")
	_request_label = _make_label("RequestContext")
	_disposition_label = _make_label("Dispositions")
	_rejection_label = _make_label("RejectionCodes")
	_latest_label = _make_label("LatestAttempt")
	_unavailable_label = _make_label("UnavailableDomains")

	var evidence_heading := Label.new()
	evidence_heading.text = "Studio action evidence — separate from canonical batch evidence"
	evidence_heading.add_theme_font_size_override("font_size", 16)
	add_child(evidence_heading)
	_studio_evidence_label = _make_label("StudioEvidence")


func _make_label(label_name: String) -> Label:
	var label := Label.new()
	label.name = label_name
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(label)
	return label


func _on_path_submitted(_value: String) -> void:
	refresh_manifest()


func _valid_relative_path(value: String) -> bool:
	if value.is_empty() or value.begins_with("/") or value.begins_with(char(92)) or value.contains(char(92)) or value.contains(":"):
		return false
	var parts := value.split("/", false)
	if parts.is_empty() or parts.has(".") or parts.has(".."):
		return false
	return parts[parts.size() - 1] == "batch-manifest.json"


func _set_empty() -> void:
	_projection = {
		"operation": DASHBOARD_OPERATION,
		"state": "EMPTY",
		"disposition": "EMPTY",
		"reason": "EMPTY — no canonical batch selected",
	}
	_render()


func _set_error(message: String) -> void:
	_projection = {
		"operation": DASHBOARD_OPERATION,
		"state": "ERROR",
		"disposition": "ERROR",
		"error": message,
	}
	_render()


func _studio_evidence_snapshot() -> Dictionary:
	if _action_source == null:
		return {"state": "NOT AVAILABLE", "reason": "NOT AVAILABLE — no Studio action evidence is available in this session."}
	var latest: Variant = _action_source.call("action_result_snapshot") if _action_source.has_method("action_result_snapshot") else {}
	var retained: Variant = _action_source.call("last_successful_core_evidence_snapshot") if _action_source.has_method("last_successful_core_evidence_snapshot") else {}
	return {
		"state": "AVAILABLE" if latest is Dictionary and not latest.is_empty() else "NOT AVAILABLE",
		"latest_action": latest.duplicate(true) if latest is Dictionary else {},
		"last_successful_core": retained.duplicate(true) if retained is Dictionary else {},
	}


func _render() -> void:
	if _state_label == null:
		return
	var state := str(_projection.get("state", "EMPTY"))
	var disposition := str(_projection.get("disposition", state))
	if state == "READY":
		_state_label.text = "Dashboard state: READY / %s" % disposition
		_summary_label.text = "Canonical batch: %s | terminal=%s | requested=%s | max_attempts=%s | attempts=%s | next_attempt=%s | accepted=%s | source=%s" % [
			_projection.get("batch_id", ""), _projection.get("terminal_state", ""), _projection.get("requested_count", ""), _projection.get("max_attempts", ""), _projection.get("attempt_count", ""), _projection.get("next_attempt_index", ""), _projection.get("accepted_count", ""), _projection.get("source_classification", ""),
		]
		var request_context: Dictionary = _projection.get("request_context", {})
		_request_label.text = "Request context: difficulty=%s | dimensions=%sx%s | generator_mode=%s" % [request_context.get("difficulty", ""), request_context.get("width", ""), request_context.get("height", ""), request_context.get("generator_mode", "")]
		_disposition_label.text = "Attempt dispositions: %s" % JSON.stringify(_projection.get("disposition_counts", {}), "  ")
		_rejection_label.text = "Rejection codes: %s" % JSON.stringify(_projection.get("rejection_code_counts", {}), "  ")
		_latest_label.text = "Latest attempt: %s" % JSON.stringify(_projection.get("latest_attempt", {}), "  ")
		_unavailable_label.text = "Unavailable: %s" % JSON.stringify(_projection.get("unavailable", {}), "  ")
	else:
		_state_label.text = "Dashboard state: %s / %s\n%s" % [state, disposition, _projection.get("error", _projection.get("reason", ""))]
		_summary_label.text = "Canonical batch: no trusted projection"
		_request_label.text = "Request context: not available until a validated canonical manifest is loaded."
		_disposition_label.text = "Attempt dispositions: not available"
		_rejection_label.text = "Rejection codes: not available"
		_latest_label.text = "Latest attempt: not available"
		_unavailable_label.text = "Unavailable domains remain unavailable until a canonical manifest is validated."
	var studio := _studio_evidence_snapshot()
	_studio_evidence_label.text = "Studio evidence state: %s | %s" % [studio.get("state", "NOT AVAILABLE"), studio.get("reason", "Separate from the canonical batch projection.")]
