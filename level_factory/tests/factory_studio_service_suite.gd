extends SceneTree

## P0-P S4: read-only Studio calls go to the long-lived Python service; writers do not.

const GATEWAY := preload("res://scripts/factory_core_gateway.gd")
const PASS_MARKER := "P0-P S4 STUDIO SERVICE PASS"
var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var gateway: RefCounted = GATEWAY.new()
	var started := Time.get_ticks_msec()
	var first: Dictionary = gateway.call("run_studio_extension", "provider-options", {})
	_require(str(first.get("served_by", "")) == "studio-service", "provider-options was not answered by the Studio service: %s" % first)
	var warm_started := Time.get_ticks_msec()
	for _i in range(5):
		var again: Dictionary = gateway.call("run_studio_extension", "provider-options", {})
		_require(str(again.get("served_by", "")) == "studio-service", "a repeated read left the Studio service")
	var warm_ms := float(Time.get_ticks_msec() - warm_started) / 5.0
	_require(warm_ms < 500.0, "a warm service read took %.0f ms" % warm_ms)
	# A writer/unknown operation keeps the per-process path.
	var writer: Dictionary = gateway.call("run_studio_extension", "library-save", {"source_id": "owner-upload-" + "0".repeat(64)})
	_require(not writer.has("served_by"), "a writing operation was sent to the long-lived service")
	print("first read %d ms, warm read %.0f ms" % [warm_started - started, warm_ms])
	gateway = null
	_finish()


func _require(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
		push_error(message)


func _finish() -> void:
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
	else:
		quit(1)
