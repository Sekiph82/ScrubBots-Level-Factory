class_name FactoryCoreGateway
extends RefCounted

## Narrow local-process boundary for the canonical Python Factory Core.
##
## This adapter owns discovery, bounded argument construction, process capture,
## and result translation. It does not implement generation, reproduction,
## solving, validation, analysis, or provider access.

enum ConnectionStatus {
	AVAILABLE,
	UNAVAILABLE,
	ERROR,
}

const PYTHON_ENVIRONMENT_NAME := "SCRUBBOTS_FACTORY_PYTHON"
const LAUNCHER_PATH := "res://scripts/factory_core_launcher.py"
const GENERATE_OUTPUT_PATH := "res://output/studio-runs"
const REPRODUCE_OUTPUT_PATH := "res://output/studio-reproductions"
const STUDIO_REVALIDATION_TRANSPORT_PATH := "res://output/.lf06-008-revalidation/request.json"
const STUDIO_REVALIDATION_OPERATION := "manual-art-structural-revalidation"
const DASHBOARD_INSPECTION_OPERATION := "factory-operations-dashboard-inspection"
const OWNER_UPLOAD_OPERATION := "owner-upload-import"
const STUDIO_EXTENSION_OPERATION := "studio-extension"
const READ_STDERR := true
const OPEN_CONSOLE := false
const FUTURE_ACTION_REASONS := {
	"Solve": "UNAVAILABLE — gameplay solver is pending M03; WFC is not used as the gameplay solver.",
	"Validate": "UNAVAILABLE — no standalone canonical validation capability is connected.",
	"Analyze": "UNAVAILABLE — analysis is pending M04.",
}

var python_executable := ""
var _connection_status: ConnectionStatus = ConnectionStatus.UNAVAILABLE
var _connection_detail := ""
var _last_successful_metadata_path := ""
var _last_result: Dictionary = {}
var _default_output_root := ""
var _probe_launcher_path := LAUNCHER_PATH


func _init(configured_executable: String = "", probe_launcher_path: String = LAUNCHER_PATH) -> void:
	_probe_launcher_path = probe_launcher_path if _safe_probe_launcher(probe_launcher_path) else LAUNCHER_PATH
	python_executable = configured_executable.strip_edges()
	if python_executable.is_empty():
		var configured_from_environment := OS.get_environment(PYTHON_ENVIRONMENT_NAME).strip_edges()
		python_executable = configured_from_environment if _safe_executable(configured_from_environment) else _discover_executable()
	_refresh_connection()


func status_name() -> String:
	return ConnectionStatus.keys()[_connection_status]


func status_message() -> String:
	return _connection_detail


func capability_summary() -> String:
	var matrix := capability_matrix()
	return "Generate=%s, Reproduce=%s, Solve=UNAVAILABLE, Validate=UNAVAILABLE, Analyze=UNAVAILABLE" % [
	"AVAILABLE" if matrix["Generate"]["available"] else "UNAVAILABLE",
	"AVAILABLE" if matrix["Reproduce"]["available"] else "UNAVAILABLE",
	]


func capability_matrix() -> Dictionary:
	var core_available := _connection_status == ConnectionStatus.AVAILABLE
	var reproduce_available := core_available and not _last_successful_metadata_path.is_empty()
	var reproduce_reason := "AVAILABLE — a successful Generate metadata.json is ready for canonical Reproduce." if reproduce_available else "UNAVAILABLE — run a successful canonical Generate first."
	if not core_available:
		reproduce_reason = "UNAVAILABLE — canonical Python Factory Core is not executable in this workspace."
	return {
		"Generate": {"available": core_available, "reason": _connection_detail},
		"Reproduce": {"available": reproduce_available, "reason": reproduce_reason},
		"Solve": {"available": false, "reason": FUTURE_ACTION_REASONS["Solve"]},
		"Validate": {"available": false, "reason": FUTURE_ACTION_REASONS["Validate"]},
		"Analyze": {"available": false, "reason": FUTURE_ACTION_REASONS["Analyze"]},
	}


func last_successful_metadata_path() -> String:
	return _last_successful_metadata_path


func last_result() -> Dictionary:
	return _last_result.duplicate(true)


func set_output_root(output_root: String) -> void:
	_default_output_root = output_root.strip_edges()


func run_action(action: String, draft: Dictionary, requested_output_root: String = "") -> Dictionary:
	var normalized_action := action.strip_edges()
	if normalized_action not in ["Generate", "Reproduce", "Solve", "Validate", "Analyze"]:
		return _unavailable_result(normalized_action, "UNAVAILABLE — action is not part of the Factory Studio action contract.")
	var matrix := capability_matrix()
	var capability: Dictionary = matrix.get(normalized_action, {"available": false, "reason": "UNAVAILABLE"})
	if not bool(capability.get("available", false)):
		return _unavailable_result(normalized_action, str(capability.get("reason", "UNAVAILABLE")))
	if normalized_action == "Generate" and str(draft.get("seed", "")).strip_edges().is_empty():
		return _unavailable_result(normalized_action, "UNAVAILABLE — enter a seed for a deterministic canonical Generate request.")
	if normalized_action == "Reproduce" and _last_successful_metadata_path.is_empty():
		return _unavailable_result(normalized_action, "UNAVAILABLE — no successful Generate metadata.json is available.")

	var output_root := _safe_output_root(requested_output_root, normalized_action)
	if output_root.is_empty():
		return _failed_result(normalized_action, -1, "FAILED — requested output is outside the approved Factory Studio output area.")
	var arguments := PackedStringArray()
	if normalized_action == "Generate":
		arguments = _generate_arguments(draft, output_root)
	else:
		arguments = _reproduce_arguments(_last_successful_metadata_path, output_root)
	return _execute_core(normalized_action, arguments)


func run_manual_art_revalidation(request_path: String) -> Dictionary:
	if _connection_status != ConnectionStatus.AVAILABLE:
		return {
			"operation": STUDIO_REVALIDATION_OPERATION,
			"scope": "STRUCTURAL_ART_QA_ONLY",
			"state": "UNAVAILABLE",
			"disposition": "UNAVAILABLE",
			"exit_code": -1,
			"error": "UNAVAILABLE — canonical Python Factory Core is not executable in this workspace.",
		}
	if request_path.strip_edges() != STUDIO_REVALIDATION_TRANSPORT_PATH:
		return {
			"operation": STUDIO_REVALIDATION_OPERATION,
			"scope": "STRUCTURAL_ART_QA_ONLY",
			"state": "ERROR",
			"disposition": "ERROR",
			"exit_code": -1,
			"error": "ERROR — manual artwork structural revalidation transport path is outside the fixed operation boundary.",
		}
	var captured: Array[String] = []
	var exit_code := _execute_process(python_executable, PackedStringArray([
		ProjectSettings.globalize_path(LAUNCHER_PATH),
		"studio-revalidate-art",
		"--request-file", ProjectSettings.globalize_path(request_path),
	]), captured)
	var process_output := "\n".join(captured)
	var payload := _find_studio_result(captured)
	if payload.is_empty():
		return {
			"operation": STUDIO_REVALIDATION_OPERATION,
			"scope": "STRUCTURAL_ART_QA_ONLY",
			"state": "ERROR",
			"disposition": "ERROR",
			"exit_code": exit_code,
			"error": "ERROR — manual artwork structural revalidation returned no structured result.",
			"captured_output": process_output.left(4096),
		}
	payload["exit_code"] = exit_code
	payload["captured_output"] = process_output.left(4096)
	return payload


func run_dashboard_inspection(manifest_path: String) -> Dictionary:
	if _connection_status != ConnectionStatus.AVAILABLE:
		return {
			"operation": DASHBOARD_INSPECTION_OPERATION,
			"state": "UNAVAILABLE",
			"disposition": "UNAVAILABLE",
			"error": "UNAVAILABLE — canonical Python Factory Core is not executable in this workspace.",
		}
	var raw_path := manifest_path.strip_edges()
	var normalized := raw_path.replace(char(92), "/")
	var path_parts := normalized.split("/", false)
	var relative_suffix := normalized.trim_prefix("res://output/")
	if normalized.is_empty() or raw_path.contains(char(92)) or not normalized.begins_with("res://output/") or relative_suffix.contains(":") or normalized.contains("..") or not normalized.ends_with("/batch-manifest.json") or path_parts.has("."):
		return {
			"operation": DASHBOARD_INSPECTION_OPERATION,
			"state": "ERROR",
			"disposition": "ERROR",
			"error": "ERROR — Dashboard manifest path is outside the approved res://output boundary.",
		}
	var captured: Array[String] = []
	var exit_code := _execute_process(python_executable, PackedStringArray([
		ProjectSettings.globalize_path(LAUNCHER_PATH),
		"dashboard-inspect",
		"--manifest", ProjectSettings.globalize_path(normalized),
	]), captured)
	var process_output := "\n".join(captured)
	var payload := _find_dashboard_result(captured)
	if payload.is_empty():
		return {
			"operation": DASHBOARD_INSPECTION_OPERATION,
			"state": "ERROR",
			"disposition": "ERROR",
			"exit_code": exit_code,
			"error": "ERROR — canonical dashboard inspection returned no structured result.",
			"captured_output": process_output.left(4096),
		}
	payload["exit_code"] = exit_code
	payload["captured_output"] = process_output.left(4096)
	return payload


func run_owner_import(source_path: String) -> Dictionary:
	if _connection_status != ConnectionStatus.AVAILABLE:
		return {
			"operation": OWNER_UPLOAD_OPERATION,
			"state": "UNAVAILABLE",
			"disposition": "UNAVAILABLE",
			"error": "UNAVAILABLE — canonical Python Factory Core is not executable in this workspace.",
		}
	var captured: Array[String] = []
	var exit_code := _execute_process(python_executable, PackedStringArray([
		ProjectSettings.globalize_path(LAUNCHER_PATH),
		"owner-upload",
		"--source", source_path,
	]), captured)
	var process_output := "\n".join(captured)
	var payload := _find_owner_upload_result(captured)
	if payload.is_empty():
		return {
			"operation": OWNER_UPLOAD_OPERATION,
			"state": "ERROR",
			"disposition": "ERROR",
			"exit_code": exit_code,
			"error": "ERROR — canonical OWNER_UPLOAD operation returned no structured result.",
			"captured_output": process_output.left(4096),
		}
	payload["exit_code"] = exit_code
	payload["captured_output"] = process_output.left(4096)
	return payload


func run_studio_extension(operation: String, request: Dictionary = {}) -> Dictionary:
	if _connection_status != ConnectionStatus.AVAILABLE:
		return {
			"operation": STUDIO_EXTENSION_OPERATION,
			"state": "UNAVAILABLE",
			"disposition": "UNAVAILABLE",
			"error": "UNAVAILABLE — canonical Python Factory Core is not executable in this workspace.",
		}
	var request_path := ProjectSettings.globalize_path("res://output/.studio-extension-request.json")
	var request_file := FileAccess.open(request_path, FileAccess.WRITE)
	if request_file == null:
		return {"operation": STUDIO_EXTENSION_OPERATION, "state": "ERROR", "disposition": "ERROR", "error": "ERROR — could not create bounded Studio extension request transport."}
	request_file.store_string(JSON.stringify(request))
	request_file.close()
	var captured: Array[String] = []
	var exit_code := _execute_process(python_executable, PackedStringArray([
		ProjectSettings.globalize_path(LAUNCHER_PATH),
		"studio-extension",
		"--operation", operation,
		"--request-file", request_path,
	]), captured)
	DirAccess.remove_absolute(request_path)
	var process_output := "\n".join(captured)
	var payload := _find_extension_result(captured)
	if payload.is_empty():
		return {
			"operation": STUDIO_EXTENSION_OPERATION,
			"state": "ERROR",
			"disposition": "ERROR",
			"exit_code": exit_code,
			"error": "ERROR — Studio extension returned no structured result.",
			"captured_output": process_output.left(4096),
		}
	payload["exit_code"] = exit_code
	payload["captured_output"] = process_output.left(4096)
	return payload


func _refresh_connection() -> void:
	if not _safe_executable(python_executable):
		_connection_status = ConnectionStatus.UNAVAILABLE
		_connection_detail = "UNAVAILABLE — configured local Python executable is outside the bounded launcher contract."
		return
	if _probe_executable(python_executable):
		_connection_status = ConnectionStatus.AVAILABLE
		_connection_detail = "AVAILABLE — committed canonical Python Factory Core launcher probe passed."
	else:
		_connection_status = ConnectionStatus.UNAVAILABLE
		_connection_detail = "UNAVAILABLE — committed canonical Python Factory Core launcher/Core probe failed."


func _discover_executable() -> String:
	for name in ["python.exe", "python", "py.exe", "py"]:
		if _probe_executable(name):
			return name
	var path_value := OS.get_environment("PATH")
	for directory in path_value.split(";", false):
		var trimmed_directory := directory.strip_edges()
		if trimmed_directory.is_empty():
			continue
		for name in ["python.exe", "python", "py.exe", "py"]:
			var candidate := trimmed_directory.path_join(name)
			if _probe_executable(candidate):
				return candidate
	return "python"


func _probe_executable(executable: String) -> bool:
	if not _safe_executable(executable):
		return false
	var captured: Array[String] = []
	var exit_code := _execute_process(executable, PackedStringArray([
		ProjectSettings.globalize_path(_probe_launcher_path),
		"--help",
	]), captured)
	var identity := "\n".join(captured).to_lower()
	return exit_code == 0 and "usage: scrubbots-pixel" in identity and "reproduce" in identity


func _safe_probe_launcher(path: String) -> bool:
	return path == LAUNCHER_PATH or path.begins_with("res://" + "tests/")


func _execute_process(executable: String, arguments: PackedStringArray, captured: Array[String]) -> int:
	return OS.execute(executable, arguments, captured, READ_STDERR, OPEN_CONSOLE)


func _generate_arguments(draft: Dictionary, output_root: String) -> PackedStringArray:
	return PackedStringArray([
		ProjectSettings.globalize_path(LAUNCHER_PATH),
		"generate",
		"--difficulty", str(draft.get("difficulty", "EASY")),
		"--width", str(int(draft.get("width", 20))),
		"--height", str(int(draft.get("height", 20))),
		"--seed", str(draft.get("seed", "")),
		"--mode", str(draft.get("mode", "MASK")),
		"--output", output_root,
	])


func _reproduce_arguments(metadata_path: String, output_root: String) -> PackedStringArray:
	return PackedStringArray([
		ProjectSettings.globalize_path(LAUNCHER_PATH),
		"reproduce",
		metadata_path,
		"--output", output_root,
	])


func _execute_core(action: String, arguments: PackedStringArray) -> Dictionary:
	var captured: Array[String] = []
	var exit_code := _execute_process(python_executable, arguments, captured)
	var process_output := "\n".join(captured)
	var bounded_process_output := process_output.left(4096)
	if exit_code != 0:
		var failure := _failed_result(action, exit_code, _safe_process_message(process_output))
		failure["captured_output"] = bounded_process_output
		_last_result = failure
		return failure
	var summary_line := _find_summary_line(captured, "MATCH" if action == "Reproduce" else "SUCCESS")
	if summary_line.is_empty():
		var malformed := _failed_result(action, exit_code, "FAILED — canonical Core returned no recognized action summary.")
		malformed["captured_output"] = bounded_process_output
		_last_result = malformed
		return malformed
	var output_path := _field_value(summary_line, "output=")
	if output_path.is_empty():
		var missing_output := _failed_result(action, exit_code, "FAILED — canonical Core summary did not provide an output path.")
		missing_output["captured_output"] = bounded_process_output
		_last_result = missing_output
		return missing_output
	var result := {
		"action": action,
		"state": "SUCCESS",
		"disposition": "MATCH" if action == "Reproduce" else "SUCCESS",
		"exit_code": exit_code,
		"candidate_id": _field_value(summary_line, "candidate_id="),
		"selected_seed": _field_value(summary_line, "seed="),
		"mode": _field_value(summary_line, "mode="),
		"dimensions": _field_value(summary_line, "dimensions="),
		"grid_hash": _field_value(summary_line, "grid_hash="),
		"output_path": output_path,
		"metadata_path": output_path.path_join("metadata.json"),
		"captured_output": bounded_process_output,
	}
	if action == "Generate":
		_last_successful_metadata_path = str(result["metadata_path"])
	_last_result = result
	return result


func _safe_output_root(requested: String, action: String) -> String:
	var chosen := requested.strip_edges()
	if chosen.is_empty() and not _default_output_root.is_empty():
		chosen = _default_output_root
	if chosen.is_empty():
		chosen = GENERATE_OUTPUT_PATH if action == "Generate" else REPRODUCE_OUTPUT_PATH
	if action == "Reproduce" and (not requested.strip_edges().is_empty() or not _default_output_root.is_empty()):
		chosen = chosen.path_join("reproduction")
	var project_output := ProjectSettings.globalize_path("res://output").simplify_path()
	var candidate := ProjectSettings.globalize_path(chosen) if chosen.begins_with("res://") or not chosen.is_absolute_path() else chosen
	candidate = candidate.simplify_path()
	var normalized_project_output := project_output.replace(char(92), "/").to_lower()
	var normalized_candidate := candidate.replace(char(92), "/").to_lower()
	if normalized_candidate != normalized_project_output and not normalized_candidate.begins_with(normalized_project_output + "/"):
		return ""
	return candidate


func _safe_executable(value: String) -> bool:
	if value.is_empty():
		return false
	for marker in ["\r", "\n", ";", "|", "&", "<", ">", "`"]:
		if marker in value:
			return false
	return true


func _find_summary_line(lines: Array[String], prefix: String) -> String:
	var combined := "\n".join(lines).replace("\r\n", "\n")
	for line in combined.split("\n"):
		if line.begins_with(prefix + " "):
			return line
	return ""


func _find_studio_result(lines: Array[String]) -> Dictionary:
	var combined := "\n".join(lines).replace("\r\n", "\n")
	var output_lines := combined.split("\n")
	for index in range(output_lines.size() - 1, -1, -1):
		var candidate_line := output_lines[index].strip_edges()
		if not candidate_line.begins_with("{") or not candidate_line.ends_with("}"):
			continue
		var parsed: Variant = JSON.parse_string(candidate_line)
		if parsed is Dictionary and str(parsed.get("operation", "")) == STUDIO_REVALIDATION_OPERATION:
			return parsed
	return {}


func _find_dashboard_result(lines: Array[String]) -> Dictionary:
	var combined := "\n".join(lines).replace("\r\n", "\n")
	var output_lines := combined.split("\n")
	for index in range(output_lines.size() - 1, -1, -1):
		var candidate_line := output_lines[index].strip_edges()
		if not candidate_line.begins_with("{") or not candidate_line.ends_with("}"):
			continue
		var parsed: Variant = JSON.parse_string(candidate_line)
		if parsed is Dictionary and str(parsed.get("operation", "")) == DASHBOARD_INSPECTION_OPERATION:
			return parsed
	return {}


func _find_owner_upload_result(lines: Array[String]) -> Dictionary:
	var combined := "\n".join(lines).replace("\r\n", "\n")
	var output_lines := combined.split("\n")
	for index in range(output_lines.size() - 1, -1, -1):
		var candidate_line := output_lines[index].strip_edges()
		if not candidate_line.begins_with("{") or not candidate_line.ends_with("}"):
			continue
		var parsed: Variant = JSON.parse_string(candidate_line)
		if parsed is Dictionary and str(parsed.get("operation", "")) == OWNER_UPLOAD_OPERATION:
			return parsed
	return {}


func _find_extension_result(lines: Array[String]) -> Dictionary:
	var combined := "\n".join(lines).replace("\r\n", "\n")
	for line in combined.split("\n"):
		var candidate_line := line.strip_edges()
		if not candidate_line.begins_with("{") or not candidate_line.ends_with("}"):
			continue
		var parsed: Variant = JSON.parse_string(candidate_line)
		if parsed is Dictionary:
			return parsed
	return {}


func _field_value(line: String, field: String) -> String:
	var start := line.find(field)
	if start < 0:
		return ""
	start += field.length()
	if field == "output=":
		return line.substr(start)
	var end := line.find(" ", start)
	return line.substr(start) if end < 0 else line.substr(start, end - start)


func _safe_process_message(process_output: String) -> String:
	var message := process_output.strip_edges()
	if message.is_empty():
		return "FAILED — canonical Python Factory Core returned a nonzero exit code without a diagnostic."
	var lines := message.replace("\r\n", "\n").split("\n", false)
	var diagnostic := lines[lines.size() - 1].strip_edges() if not lines.is_empty() else message
	if diagnostic.is_empty():
		diagnostic = message
	return "FAILED — canonical Python Factory Core: " + diagnostic.left(512)


func _unavailable_result(action: String, reason: String) -> Dictionary:
	var result := {
		"action": action,
		"state": "UNAVAILABLE",
		"disposition": "UNAVAILABLE",
		"exit_code": -1,
		"reason": reason,
	}
	_last_result = result
	return result


func _failed_result(action: String, exit_code: int, reason: String) -> Dictionary:
	return {
		"action": action,
		"state": "FAILED",
		"disposition": "FAILED",
		"exit_code": exit_code,
		"reason": reason,
	}
