extends SceneTree

const PASS_MARKER := "SB-LFX-006-C001 CANDIDATE REVIEW integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var candidates := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/CandidateInbox")
	var gateway: RefCounted = instance.get("core_gateway")
	_require(candidates != null and gateway != null, "Candidate Inbox or gateway did not instantiate")
	if candidates == null or gateway == null: _cleanup(instance); return
	var output_root := "res://output/.lfx006-candidate-review"
	_remove_tree(ProjectSettings.globalize_path(output_root))
	var first: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "66006", "mode": "MASK"}, output_root)
	var second: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "66007", "mode": "RULES"}, output_root)
	_require(first.get("state") == "SUCCESS" and second.get("state") == "SUCCESS", "two canonical candidates did not generate")
	var first_id := str(first.get("candidate_id", "")); var second_id := str(second.get("candidate_id", ""))
	_require(first_id != second_id and not first_id.is_empty(), "candidate identities were not distinct")
	var first_bytes := _bundle_bytes(str(first.get("output_path", ""))); var second_bytes := _bundle_bytes(str(second.get("output_path", "")))
	var initial: Dictionary = gateway.call("run_studio_extension", "candidate-inbox", {})
	var initial_by_id := _by_id(initial.get("candidates", []))
	_require(initial_by_id.get(first_id, {}).get("owner_review", {}).get("disposition") == "NEEDS_REVIEW", "first candidate did not enter NEEDS_REVIEW")
	_require(initial_by_id.get(second_id, {}).get("owner_review", {}).get("disposition") == "NEEDS_REVIEW", "second candidate did not enter NEEDS_REVIEW")
	var accepted: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": first_id, "disposition": "ACCEPT", "reason": "first review"})
	var rejected: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": second_id, "disposition": "REJECT", "reason": "second review"})
	var second_review: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": first_id, "disposition": "REJECT", "reason": "follow-up"})
	_require(accepted.get("disposition") == "ACCEPT" and rejected.get("disposition") == "REJECT" and second_review.get("sequence") == 2, "ACCEPT/REJECT review workflow failed")
	var reloaded: Dictionary = gateway.call("run_studio_extension", "candidate-inbox", {})
	var reloaded_by_id := _by_id(reloaded.get("candidates", []))
	_require(reloaded_by_id.get(first_id, {}).get("owner_review", {}).get("disposition") == "REJECT", "latest valid review was not derived after reload")
	_require(reloaded_by_id.get(first_id, {}).get("owner_review_history", []).size() == 2, "review history was not retained")
	_require(reloaded_by_id.get(second_id, {}).get("owner_review", {}).get("disposition") == "REJECT", "review crossed candidate identity")
	_require(reloaded_by_id.get(first_id, {}).get("solver", {}).get("disposition") == "NOT AVAILABLE", "solver availability was fabricated")
	var corrupt_path := ProjectSettings.globalize_path("res://output/studio-extensions/owner-review").path_join("review-%s-0002.json" % first_id)
	var corrupt_before := FileAccess.get_file_as_bytes(corrupt_path)
	var corrupt_file := FileAccess.open(corrupt_path, FileAccess.WRITE); corrupt_file.store_string("{corrupt"); corrupt_file.close()
	var corrupted: Dictionary = gateway.call("run_studio_extension", "candidate-inbox", {})
	var corrupted_first: Dictionary = _by_id(corrupted.get("candidates", [])).get(first_id, {})
	_require(corrupted_first.get("owner_review", {}).get("disposition") == "ACCEPT", "tampered latest review was treated as current")
	_require(corrupted_first.get("owner_review_invalid", []).size() > 0, "tampered review was not reported invalid")
	var restore := FileAccess.open(corrupt_path, FileAccess.WRITE); restore.store_buffer(corrupt_before); restore.close()
	_require(first_bytes == _bundle_bytes(str(first.get("output_path", ""))) and second_bytes == _bundle_bytes(str(second.get("output_path", ""))), "candidate bytes changed during review workflow")
	candidates.call("refresh_inbox"); await process_frame
	var ui_snapshot: Dictionary = candidates.call("snapshot")
	_require(ui_snapshot.get("candidates", []).size() >= 2, "real Candidate Inbox did not render candidates")
	_cleanup(instance)

func _by_id(items: Array) -> Dictionary:
	var result := {}
	for item in items: result[str(item.get("candidate_id", ""))] = item
	return result

func _bundle_bytes(path: String) -> Dictionary:
	var result := {}
	for name in ["artwork.png", "artwork.json", "metadata.json"]: result[name] = FileAccess.get_file_as_bytes(path.path_join(name))
	return result

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx006-candidate-review"))
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	instance.queue_free(); _finish()

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
