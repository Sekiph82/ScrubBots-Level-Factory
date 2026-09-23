extends SceneTree

## Level Factory-owned runner. It loads canonical ScrubBots scripts through res://
## and performs no gameplay calculation itself. The --path supplied by the Python
## adapter is the verified, read-only ScrubBots checkout.

const BRIDGE_SCHEMA := "scrubbots-canonical-headless-bridge"
const BRIDGE_VERSION := 1
const PROOF_STATE_SOURCE_SHA256 := "408893348e8abab089de98586999fc15bafc3b07b83f21458152788a34e78620"
const ProofState = preload("res://scripts/gameplay/solver/proof_state.gd")
const ProofKernel = preload("res://scripts/gameplay/solver/proof_kernel.gd")
const SolvabilitySolver = preload("res://scripts/gameplay/solver/solvability_solver.gd")
const LevelData = preload("res://scripts/data/level_data.gd")
const BatchSupplyEngine = preload("res://scripts/gameplay/supply/batch_supply_engine.gd")
const ColorBatch = preload("res://scripts/gameplay/supply/color_batch.gd")

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var request_path := _arg(args, "--request")
	var response_path := _arg(args, "--response")
	var response := _run(request_path)
	if response_path != "":
		var file := FileAccess.open(response_path, FileAccess.WRITE)
		if file != null:
			file.store_string(JSON.stringify(response))
			file.close()
	quit(0 if response.get("disposition", "ERROR") != "ERROR" else 1)

func _run(path: String) -> Dictionary:
	if path == "":
		return _error("request path is missing")
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return _error("request file cannot be read")
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	if not parsed is Dictionary:
		return _error("request envelope is malformed")
	var payload_text := Marshalls.base64_to_utf8(String(parsed.get("request_payload_base64", "")))
	var payload = JSON.parse_string(payload_text)
	if not payload is Dictionary:
		return _error("canonical request payload must be JSON object")
	var source_bytes = _level_data_source_bytes(payload)
	if source_bytes == null:
		return _error("exact LevelData source bytes are malformed")
	if _sha256_hex(source_bytes) != String(parsed.get("level_data_source_sha256", "")):
		return _error("LevelData source SHA-256 does not match the verified request")
	var state = _state_from_payload(payload)
	if state == null:
		return _error("canonical level and supply payload is malformed")
	var operation := String(parsed.get("operation", ""))
	var result: Dictionary
	match operation:
		"legal_moves":
			result = {"legal_columns": state.legal_action_columns(), "active_count": state.active_count()}
		"apply_placement":
			var kernel = ProofKernel.new()
			var applied := kernel.apply_placement(state, int(payload.get("column", -1)))
			if not applied.get("ok", false):
				return _error(String(applied.get("error", "placement failed")))
			var child = applied["state"]
			result = {"active_count": child.active_count(), "solved": child.is_solved(), "clears": int(applied["clears"]), "placed": applied["placed"]}
		"solve":
			result = SolvabilitySolver.new().solve(state, payload.get("config", {}))
		_:
			return _error("unsupported canonical operation")
	return {"schema": BRIDGE_SCHEMA + ".response", "version": BRIDGE_VERSION,
		"disposition": "AVAILABLE", "request_digest": parsed.get("request_digest"),
		"authority_sha": parsed.get("authority", {}).get("commit_sha"),
		"source_sha256": PROOF_STATE_SOURCE_SHA256,
		"operation": operation, "result": result, "reason": "canonical ScrubBots operation executed"}

func _state_from_payload(payload: Dictionary):
	var level_data = _level_data_source_dict(payload)
	if level_data == null:
		return null
	var width := int(level_data.get("width", 0))
	var height := int(level_data.get("height", 0))
	var cells: Array = level_data.get("cells", [])
	if width <= 0 or height <= 0 or cells.size() != width * height:
		return null
	var level = LevelData.new(int(level_data.get("version", 1)), String(level_data.get("id", "")), String(level_data.get("name", "")), String(level_data.get("difficulty", "")), width, height, PackedStringArray(level_data.get("palette", [])), PackedInt32Array(cells))
	var supply = BatchSupplyEngine.create(int(payload.get("column_count", 0)), int(payload.get("preview_depth", 3)))
	if supply == null:
		return null
	var columns: Array = []
	for raw_column in payload.get("columns", []):
		var column: Array = []
		for raw_batch in raw_column:
			var batch = ColorBatch.make(String(raw_batch.get("id", "")), int(raw_batch.get("color", -1)), int(raw_batch.get("count", 0)), int(payload.get("palette_size", 0)))
			if batch == null:
				return null
			column.append(batch)
		columns.append(column)
	if not supply.load_candidate(columns, int(payload.get("seed", 0)), int(payload.get("palette_size", 0))):
		return null
	return ProofState.from_level_and_supply(level, supply)

func _level_data_source_bytes(payload: Dictionary):
	var encoded := String(payload.get("level_data_source_base64", ""))
	if encoded.is_empty():
		return null
	var source := Marshalls.base64_to_raw(encoded)
	if source.is_empty() or source.size() > 65536:
		return null
	return source

func _level_data_source_dict(payload: Dictionary):
	var source = _level_data_source_bytes(payload)
	if source == null:
		return null
	var parsed = JSON.parse_string(source.get_string_from_utf8())
	if not parsed is Dictionary:
		return null
	for field in ["version", "id", "name", "difficulty", "width", "height", "palette", "cells"]:
		if not parsed.has(field):
			return null
	var version = _json_int(parsed.get("version"))
	if parsed.keys().size() != 8 or version == null or version != 1:
		return null
	if typeof(parsed.get("id")) != TYPE_STRING or String(parsed.get("id", "")).is_empty():
		return null
	if typeof(parsed.get("name")) != TYPE_STRING or String(parsed.get("name", "")).is_empty():
		return null
	if typeof(parsed.get("difficulty")) != TYPE_STRING or String(parsed.get("difficulty", "")).is_empty():
		return null
	var width = _json_int(parsed.get("width"))
	if width == null or width <= 0:
		return null
	var height = _json_int(parsed.get("height"))
	if height == null or height <= 0:
		return null
	var palette = parsed.get("palette", [])
	var cells = parsed.get("cells", [])
	if typeof(palette) != TYPE_ARRAY or palette.is_empty() or typeof(cells) != TYPE_ARRAY:
		return null
	if cells.size() != width * height:
		return null
	for color in palette:
		if typeof(color) != TYPE_STRING or String(color).is_empty():
			return null
	for cell in cells:
		var cell_id = _json_int(cell)
		if cell_id == null or cell_id < 0 or cell_id >= palette.size():
			return null
	return parsed

func _json_int(value):
	if typeof(value) == TYPE_INT:
		return int(value)
	if typeof(value) == TYPE_FLOAT and is_equal_approx(value, round(value)):
		return int(value)
	return null

func _sha256_hex(source: PackedByteArray) -> String:
	var hashing := HashingContext.new()
	hashing.start(HashingContext.HASH_SHA256)
	hashing.update(source)
	return hashing.finish().hex_encode()

func _arg(args: PackedStringArray, name: String) -> String:
	var index := args.find(name)
	return String(args[index + 1]) if index >= 0 and index + 1 < args.size() else ""

func _error(reason: String) -> Dictionary:
	return {"schema": BRIDGE_SCHEMA + ".response", "version": BRIDGE_VERSION, "disposition": "ERROR", "reason": reason}
