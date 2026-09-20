extends SceneTree

const PASS_MARKER := "SB-LFX-010-C001 READINESS integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var readiness := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/ProductionReadinessCard")
	var gateway: RefCounted = instance.get("core_gateway")
	_require(readiness != null and gateway != null, "readiness surface or gateway did not instantiate")
	if readiness == null or gateway == null: _cleanup(instance); return
	var output_root := "res://output/.lfx010-readiness"; _remove_tree(ProjectSettings.globalize_path(output_root)); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var first: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "101010", "mode": "RULES"}, output_root)
	var second: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 21, "height": 20, "seed": "101011", "mode": "RULES"}, output_root)
	var first_id := str(first.get("candidate_id", "")); var second_id := str(second.get("candidate_id", "")); _require(first.get("state") == "SUCCESS" and second.get("state") == "SUCCESS", "readiness candidates did not generate")
	var first_bytes := _bundle_bytes(str(first.get("output_path", ""))); var second_bytes := _bundle_bytes(str(second.get("output_path", "")))
	var accept: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": first_id, "disposition": "ACCEPT", "reason": "ready review"})
	var first_card: Dictionary = gateway.call("run_studio_extension", "readiness", {"candidate_id": first_id})
	var second_card: Dictionary = gateway.call("run_studio_extension", "readiness", {"candidate_id": second_id})
	_require(accept.get("disposition") == "ACCEPT", "owner acceptance did not record")
	_require(first_card.get("gates", {}).get("OWNER", {}).get("disposition") == "PASS", "ACCEPT did not map to OWNER PASS")
	_require(second_card.get("gates", {}).get("OWNER", {}).get("disposition") == "PENDING", "missing review did not remain PENDING")
	for card in [first_card, second_card]:
		_require(card.get("gates", {}).get("QA", {}).get("disposition") == "NOT_AVAILABLE", "QA fabricated M05 authority")
		_require(card.get("gates", {}).get("EXPORT", {}).get("disposition") == "NOT_AVAILABLE", "EXPORT fabricated authority from bundle presence")
		_require(card.get("gates", {}).get("SOLVER", {}).get("disposition") == "NOT_AVAILABLE" and card.get("gates", {}).get("DIFFICULTY", {}).get("disposition") == "NOT_AVAILABLE", "solver/difficulty fabricated")
		_require(card.get("overall") == "NOT READY", "readiness became READY with unavailable gates")
	var review_path := ProjectSettings.globalize_path("res://output/studio-extensions/owner-review").path_join("review-%s-0001.json" % first_id)
	var review_before := FileAccess.get_file_as_bytes(review_path); var corrupt := FileAccess.open(review_path, FileAccess.WRITE); corrupt.store_string("{corrupt"); corrupt.close()
	var stale: Dictionary = gateway.call("run_studio_extension", "readiness", {"candidate_id": first_id})
	_require(stale.get("gates", {}).get("OWNER", {}).get("disposition") == "STALE", "tampered review was not stale in readiness")
	var restore := FileAccess.open(review_path, FileAccess.WRITE); restore.store_buffer(review_before); restore.close()
	readiness.call("refresh_candidate", first_id); await process_frame
	_require(readiness.call("snapshot").get("gates", {}).get("QA", {}).get("disposition") == "NOT_AVAILABLE", "real readiness UI did not show QA unavailable")
	_require(first_bytes == _bundle_bytes(str(first.get("output_path", ""))) and second_bytes == _bundle_bytes(str(second.get("output_path", ""))), "readiness mutated candidate bytes")
	_cleanup(instance)

func _bundle_bytes(path: String) -> Dictionary:
	var result := {}
	for name in ["artwork.png", "artwork.json", "metadata.json"]: result[name] = FileAccess.get_file_as_bytes(path.path_join(name))
	return result

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx010-readiness")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); instance.queue_free(); _finish()

func _remove_tree(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path): return
	var directory := DirAccess.open(path); if directory == null: return
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next(); if entry.is_empty(): break
		if entry in [".", ".."]: continue
		var child := path.path_join(entry)
		if directory.current_is_dir(): _remove_tree(child)
		else: DirAccess.remove_absolute(child)
	directory.list_dir_end(); DirAccess.remove_absolute(path)

func _require(condition: bool, message: String) -> void:
	if not condition: _errors.append(message)

func _finish() -> void:
	if _errors.is_empty(): print(PASS_MARKER); quit(0); return
	for error in _errors: push_error(error)
	quit(1)
