extends SceneTree

const PASS_MARKER := "SB-LFX-007-C001 COMPARISON integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var comparison := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/CandidateComparison")
	var gateway: RefCounted = instance.get("core_gateway")
	_require(comparison != null and gateway != null, "comparison surface or gateway did not instantiate")
	if comparison == null or gateway == null: _cleanup(instance); return
	var output_root := "res://output/.lfx007-comparison"
	_remove_tree(ProjectSettings.globalize_path(output_root))
	var left: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "77007", "mode": "MASK"}, output_root)
	var right: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "77008", "mode": "RULES"}, output_root)
	_require(left.get("state") == "SUCCESS" and right.get("state") == "SUCCESS", "two candidates did not generate")
	var left_id := str(left.get("candidate_id", "")); var right_id := str(right.get("candidate_id", ""))
	var left_bytes := _bundle_bytes(str(left.get("output_path", ""))); var right_bytes := _bundle_bytes(str(right.get("output_path", "")))
	var review: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": left_id, "disposition": "ACCEPT", "reason": "bound left review"})
	_require(review.get("candidate_id") == left_id, "review was not bound to left candidate")
	var first_view: Dictionary = gateway.call("run_studio_extension", "comparison", {"candidate_ids": [left_id, right_id]})
	_require(first_view.get("read_only") == true and first_view.get("winner", {}).get("disposition") == "NOT AVAILABLE", "comparison computed a winner")
	_require(first_view.get("candidates", []).size() == 2, "comparison did not return two candidates")
	_require(first_view.get("candidates", [])[0].get("owner_review", {}).get("disposition") == "ACCEPT", "left review did not stay bound")
	_require(first_view.get("candidates", [])[1].get("owner_review", {}).get("disposition") == "NOT AVAILABLE", "left review crossed to right candidate")
	for candidate in first_view.get("candidates", []):
		_require(candidate.has("provenance") and candidate.has("structural") and candidate.has("evidence_references"), "comparison evidence surface is incomplete")
		_require(candidate.get("solver", {}).get("disposition") == "NOT AVAILABLE" and candidate.get("difficulty", {}).get("disposition") == "NOT AVAILABLE", "unavailable domains were fabricated")
	var refreshed: Dictionary = gateway.call("run_studio_extension", "comparison", {"candidate_ids": [right_id, left_id]})
	_require(refreshed.get("candidates", [])[0].get("candidate_id") == right_id and refreshed.get("candidates", [])[1].get("candidate_id") == left_id, "refresh/reselection cross-wired comparison columns")
	var review_path := ProjectSettings.globalize_path("res://output/studio-extensions/owner-review").path_join("review-%s-0001.json" % left_id)
	var review_before := FileAccess.get_file_as_bytes(review_path)
	var corrupt := FileAccess.open(review_path, FileAccess.WRITE); corrupt.store_string("{tampered"); corrupt.close()
	var stale: Dictionary = gateway.call("run_studio_extension", "comparison", {"candidate_ids": [left_id, right_id]})
	_require(stale.get("candidates", [])[0].get("owner_review", {}).get("disposition") == "STALE", "tampered review was treated as current comparison evidence")
	var restore := FileAccess.open(review_path, FileAccess.WRITE); restore.store_buffer(review_before); restore.close()
	comparison.call("compare_ids", left_id, right_id); await process_frame
	var ui: Dictionary = comparison.call("snapshot")
	_require(ui.get("candidates", []).size() == 2, "real comparison UI did not render both candidates")
	_require(left_bytes == _bundle_bytes(str(left.get("output_path", ""))) and right_bytes == _bundle_bytes(str(right.get("output_path", ""))), "comparison mutated candidate bytes")
	_cleanup(instance)

func _bundle_bytes(path: String) -> Dictionary:
	var result := {}
	for name in ["artwork.png", "artwork.json", "metadata.json"]: result[name] = FileAccess.get_file_as_bytes(path.path_join(name))
	return result

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx007-comparison")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); instance.queue_free(); _finish()

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
