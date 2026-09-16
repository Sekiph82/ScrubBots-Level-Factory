@tool
class_name FactoryStudioEvidencePanel
extends VBoxContainer

## Read-only presentation over a successful canonical metadata.json bundle.
## It does not validate, recompute, or persist canonical evidence.

const EMPTY := "EMPTY"
const READY := "READY"
const ERROR := "ERROR"
const METADATA_SCHEMA := "scrubbots-output-metadata"
const METADATA_SCHEMA_VERSION := 1
const QUALITY_BINDING_SCHEMA := "scrubbots-output-quality-binding"
const QUALITY_BINDING_VERSION := 1
const QUALITY_SCHEMA := "scrubbots-quality"
const QUALITY_VERSION := 1
const GENERATION_REQUEST_SCHEMA := "scrubbots-generation-request"
const SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS: Array[int] = [1, 2]

var _state := EMPTY
var _source_action := ""
var _source_bundle_path := ""
var _metadata_path := ""
var _attempted_metadata_path := ""
var _candidate_id := ""
var _grid_hash := ""
var _logical_width := 0
var _logical_height := 0
var _generation_mode := ""
var _generator_id := ""
var _generator_version := ""
var _request_schema := ""
var _request_schema_version := 0
var _request_difficulty := ""
var _quality_schema := ""
var _quality_schema_version := 0
var _quality_policy_version := ""
var _quality_decision := ""
var _quality_rejection_codes: Array = []
var _structural_metrics: Dictionary = {}
var _canonical_quality_evidence: Dictionary = {}
var _solution_disposition := "UNAVAILABLE — gameplay solver pending M03."
var _difficulty_disposition := "UNAVAILABLE — Difficulty Intelligence pending M04."
var _load_risk_disposition := "UNAVAILABLE — no canonical gameplay load/risk model exists yet."
var _retained_after_failure := false
var _error_message := ""
var _state_label: Label
var _identity_label: Label
var _quality_label: Label
var _solution_label: Label
var _difficulty_label: Label
var _load_risk_label: Label


func _ready() -> void:
	if get_child_count() == 0:
		_build_panel()
	_refresh_labels()


func _build_panel() -> void:
	var heading := Label.new()
	heading.name = "EvidenceHeading"
	heading.text = "Canonical evidence / metrics — read-only"
	heading.add_theme_font_size_override("font_size", 16)
	add_child(heading)

	_state_label = _add_section_label("EvidenceState")
	_identity_label = _add_section_label("IdentityProvenance")
	_quality_label = _add_section_label("StructuralArtQA")
	_solution_label = _add_section_label("SolutionValue")
	_difficulty_label = _add_section_label("DifficultyValue")
	_load_risk_label = _add_section_label("LoadRiskValue")


func _add_section_label(label_name: String) -> Label:
	var label := Label.new()
	label.name = label_name
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(label)
	return label


func consume_action_result(result: Dictionary) -> void:
	var state := str(result.get("state", ""))
	if state == "SUCCESS":
		_load_successful_metadata(result)
		return
	if _state == EMPTY:
		_refresh_labels()
		return
	_retained_after_failure = true
	_refresh_labels()


func snapshot() -> Dictionary:
	return {
		"state": _state,
		"source_action": _source_action,
		"source_bundle_path": _source_bundle_path,
		"metadata_path": _metadata_path,
		"attempted_metadata_path": _attempted_metadata_path,
		"candidate_id": _candidate_id,
		"grid_hash": _grid_hash,
		"logical_width": _logical_width,
		"logical_height": _logical_height,
		"generation_mode": _generation_mode,
		"generator_id": _generator_id,
		"generator_version": _generator_version,
		"request_schema": _request_schema,
		"request_schema_version": _request_schema_version,
		"request_difficulty": _request_difficulty,
		"quality_schema": _quality_schema,
		"quality_schema_version": _quality_schema_version,
		"quality_policy_version": _quality_policy_version,
		"quality_decision": _quality_decision,
		"quality_rejection_codes": _quality_rejection_codes.duplicate(),
		"structural_metrics": _structural_metrics.duplicate(true),
		"canonical_quality_evidence": _canonical_quality_evidence.duplicate(true),
		"solution": _solution_disposition,
		"difficulty_analysis": _difficulty_disposition,
		"load_risk": _load_risk_disposition,
		"retained_after_failure": _retained_after_failure,
		"error": _error_message,
	}


func last_successful_evidence_snapshot() -> Dictionary:
	return _last_successful_evidence.duplicate(true)


var _last_successful_evidence: Dictionary = {}


func _load_successful_metadata(result: Dictionary) -> void:
	var output_path := str(result.get("output_path", "")).strip_edges()
	_attempted_metadata_path = output_path.path_join("metadata.json")
	var failure_reason := _validate_and_load_metadata(result, _attempted_metadata_path)
	if not failure_reason.is_empty():
		_state = ERROR
		_error_message = "ERROR — canonical metadata was not safely presentable: " + failure_reason
		_retained_after_failure = not _last_successful_evidence.is_empty()
		_refresh_labels()
		return

	_state = READY
	_error_message = ""
	_retained_after_failure = false
	_last_successful_evidence = snapshot()
	_refresh_labels()


func _validate_and_load_metadata(result: Dictionary, path: String) -> String:
	if not _safe_output_path(str(result.get("output_path", ""))):
		return "successful output is outside the governed Factory output area"
	if path.is_empty():
		return "metadata path is empty"
	var metadata_text := FileAccess.get_file_as_string(path)
	if metadata_text.is_empty():
		return "metadata.json is missing or empty"
	var metadata: Variant = JSON.parse_string(metadata_text)
	if not metadata is Dictionary:
		return "metadata.json is not a JSON object"
	var root: Dictionary = metadata
	if root.get("schema") != METADATA_SCHEMA or root.get("schema_version") != METADATA_SCHEMA_VERSION:
		return "unsupported metadata schema/version"
	if typeof(root.get("candidate_id")) != TYPE_STRING or str(root.get("candidate_id")).is_empty():
		return "root metadata candidate_id is missing or not a string"
	var artwork: Variant = root.get("artwork")
	var generation: Variant = root.get("generation")
	var quality: Variant = root.get("quality")
	if not artwork is Dictionary or not generation is Dictionary or not quality is Dictionary:
		return "required canonical evidence sections are missing"
	var artwork_data: Dictionary = artwork
	var generation_data: Dictionary = generation
	var quality_data: Dictionary = quality
	var action_candidate := str(result.get("candidate_id", ""))
	var action_grid_hash := str(result.get("grid_hash", ""))
	if root.get("candidate_id") != action_candidate or artwork_data.get("candidate_id") != action_candidate or root.get("candidate_id") != artwork_data.get("candidate_id"):
		return "metadata candidate identity does not match successful action evidence"
	if artwork_data.get("grid_hash") != action_grid_hash:
		return "metadata grid identity does not match successful action evidence"
	var action_dimensions := _parse_dimensions(str(result.get("dimensions", "")))
	var artwork_width_value: Variant = artwork_data.get("width")
	var artwork_height_value: Variant = artwork_data.get("height")
	if typeof(artwork_width_value) not in [TYPE_INT, TYPE_FLOAT] or typeof(artwork_height_value) not in [TYPE_INT, TYPE_FLOAT]:
		return "metadata artwork dimensions are not numeric"
	if float(artwork_width_value) != floor(float(artwork_width_value)) or float(artwork_height_value) != floor(float(artwork_height_value)):
		return "metadata artwork dimensions are not exact integers"
	if action_dimensions.is_empty() or int(artwork_width_value) != action_dimensions[0] or int(artwork_height_value) != action_dimensions[1]:
		return "metadata dimensions do not match successful action evidence"
	if quality_data.get("schema") != QUALITY_BINDING_SCHEMA or quality_data.get("version") != QUALITY_BINDING_VERSION:
		return "unsupported canonical quality binding schema/version"
	if quality_data.get("candidate_id") != artwork_data.get("candidate_id") or quality_data.get("grid_hash") != artwork_data.get("grid_hash"):
		return "quality binding is not attached to the canonical artwork identity"
	var report: Variant = quality_data.get("report")
	if not report is Dictionary:
		return "canonical quality report is missing"
	var report_data: Dictionary = report
	if report_data.get("schema") != QUALITY_SCHEMA or report_data.get("version") != QUALITY_VERSION:
		return "unsupported structural quality schema/version"
	var analysis: Variant = report_data.get("analysis")
	var policy: Variant = report_data.get("policy")
	if not analysis is Dictionary or not policy is Dictionary:
		return "canonical structural quality analysis/policy is missing"
	var analysis_data: Dictionary = analysis
	var metrics: Variant = analysis_data.get("metrics")
	if not metrics is Dictionary:
		return "canonical structural quality metrics are missing"
	var request: Variant = generation_data.get("request")
	var generator_mode := str(generation_data.get("generator_mode", ""))
	var generator_id := str(generation_data.get("generator_id", ""))
	var generator_version := str(generation_data.get("generator_version", ""))
	if not request is Dictionary or generator_mode.is_empty() or generator_id.is_empty() or generator_version.is_empty():
		return "canonical generation provenance is missing"
	var request_data: Dictionary = request
	if typeof(request_data.get("schema")) != TYPE_STRING or request_data.get("schema") != GENERATION_REQUEST_SCHEMA:
		return "unsupported canonical GenerationRequest schema"
	var request_version_value: Variant = request_data.get("schema_version")
	if typeof(request_version_value) not in [TYPE_INT, TYPE_FLOAT] or float(request_version_value) != floor(float(request_version_value)):
		return "canonical GenerationRequest schema version is not an exact integer"
	var request_version := int(request_version_value)
	if not SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS.has(request_version):
		return "unsupported canonical GenerationRequest schema version"
	var selected_metrics: Dictionary = {}
	for key in [
		"occupied_count",
		"occupied_ratio",
		"occupied_component_count",
		"isolated_occupied_count",
		"tiny_region_count",
		"tiny_region_cell_count",
		"largest_occupied_region_dominance",
		"largest_color_dominance",
		"occupied_edge_touch_ratio",
		"aggregate_symmetry_score",
		"color_entropy",
		"checkerboard_score",
		"negative_space_ratio",
	]:
		if metrics.has(key):
			if typeof(metrics[key]) not in [TYPE_INT, TYPE_FLOAT]:
				return "canonical structural metric has an invalid type: " + key
			selected_metrics[key] = metrics[key]
	if selected_metrics.is_empty():
		return "canonical structural metric subset is empty"
	var rejection_codes_value: Variant = quality_data.get("rejection_codes")
	if typeof(rejection_codes_value) != TYPE_ARRAY:
		return "canonical quality rejection_codes is not an array"
	for rejection_code in rejection_codes_value:
		if typeof(rejection_code) != TYPE_STRING:
			return "canonical quality rejection_codes contains a non-string value"
	_source_action = str(result.get("action", ""))
	_source_bundle_path = str(result.get("output_path", ""))
	_metadata_path = path
	_candidate_id = str(artwork_data.get("candidate_id", ""))
	_grid_hash = str(artwork_data.get("grid_hash", ""))
	_logical_width = int(artwork_data.get("width", 0))
	_logical_height = int(artwork_data.get("height", 0))
	_generation_mode = generator_mode
	_generator_id = generator_id
	_generator_version = generator_version
	_request_schema = str(request_data.get("schema", ""))
	_request_schema_version = int(request_data.get("schema_version", 0))
	_request_difficulty = str(request_data.get("difficulty", ""))
	_quality_schema = str(report_data.get("schema", ""))
	_quality_schema_version = int(report_data.get("version", 0))
	_quality_policy_version = str(policy.get("version", ""))
	_quality_decision = str(quality_data.get("decision", report_data.get("accepted", "")))
	_quality_rejection_codes = rejection_codes_value.duplicate()
	_structural_metrics = selected_metrics
	_canonical_quality_evidence = quality_data.duplicate(true)
	return ""


func _safe_output_path(path: String) -> bool:
	if path.is_empty():
		return false
	var project_output := ProjectSettings.globalize_path("res://output").simplify_path().replace(char(92), "/").to_lower()
	var candidate := path
	if candidate.begins_with("res://") or not candidate.is_absolute_path():
		candidate = ProjectSettings.globalize_path(candidate)
	var normalized := candidate.simplify_path().replace(char(92), "/").to_lower()
	return normalized == project_output or normalized.begins_with(project_output + "/")


func _parse_dimensions(value: String) -> Array[int]:
	var parts := value.split("x")
	if parts.size() != 2 or not parts[0].is_valid_int() or not parts[1].is_valid_int():
		return []
	return [int(parts[0]), int(parts[1])]


func _refresh_labels() -> void:
	if _state_label == null:
		return
	if _state == EMPTY:
		_state_label.text = "Evidence panel: EMPTY — no successful canonical metadata.json is loaded."
		_identity_label.text = "Identity / provenance: no evidence displayed."
		_quality_label.text = "Structural / Art QA evidence: no canonical evidence displayed."
	else:
		var retention := " — RETAINED LAST SUCCESS" if _retained_after_failure else ""
		if _state == ERROR:
			_state_label.text = "Evidence panel: ERROR — %s%s" % [_error_message, " Prior evidence is retained/stale." if _retained_after_failure else ""]
		else:
			_state_label.text = "Evidence panel: READY%s" % retention
		_identity_label.text = "Identity / provenance\nCandidate=%s | grid_hash=%s | dimensions=%sx%s | action=%s\nGenerator=%s %s (%s) | request=%s v%s | target/request difficulty=%s\nBundle=%s\nMetadata=%s" % [
			_candidate_id,
			_grid_hash,
			_logical_width,
			_logical_height,
			_source_action,
			_generator_id,
			_generator_version,
			_generation_mode,
			_request_schema,
			_request_schema_version,
			_request_difficulty,
			_source_bundle_path,
			_metadata_path,
		]
		_quality_label.text = "Structural / Art QA evidence\nDecision=%s | QA schema=%s v%s | policy=%s | rejection_codes=%s\nMetrics (canonical metadata): %s\nStructural QA ACCEPT != OWNER ACCEPT" % [
			_quality_decision,
			_quality_schema,
			_quality_schema_version,
			_quality_policy_version,
			str(_quality_rejection_codes),
			str(_structural_metrics),
		]
	_solution_label.text = "Solution: %s" % _solution_disposition
	_difficulty_label.text = "Difficulty analysis: %s\nTarget/request difficulty is context only: %s" % [_difficulty_disposition, _request_difficulty if not _request_difficulty.is_empty() else "not loaded"]
	_load_risk_label.text = "Load / risk: %s" % _load_risk_disposition
