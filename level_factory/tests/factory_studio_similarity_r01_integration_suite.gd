extends SceneTree

const PASS_MARKER := "SB-LFX-016-C001 SIMILARITY identity integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway"); var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/VisualSimilarity"); var candidates_surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/CandidateInbox"); var comparison_surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/CandidateComparison"); var search_surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/DiscoverySearch")
	_require(gateway != null and surface != null and candidates_surface != null and comparison_surface != null and search_surface != null, "similarity/candidate/comparison/search surfaces did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx016-similarity-a")); _remove_tree(ProjectSettings.globalize_path("res://output/.lfx016-similarity-b")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var first: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "16016", "mode": "MASK"}, "res://output/.lfx016-similarity-a")
	var second: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "16017", "mode": "RULES"}, "res://output/.lfx016-similarity-b")
	_require(first.get("state") == "SUCCESS" and second.get("state") == "SUCCESS", "similarity fixtures failed")
	var left_id := str(first.get("candidate_id", "")); var right_id := str(second.get("candidate_id", "")); var exact: Dictionary = gateway.call("run_studio_extension", "similarity", {"left_id": left_id, "right_id": left_id, "threshold": 0.92})
	_require(exact.get("disposition") == "EXACT_DUPLICATE" and exact.get("left_identity") == left_id and exact.get("policy") == "SIMILARITY_POLICY_V1", "canonical exact identity was not stronger than advisory similarity: %s" % exact)
	var arbitrary: Dictionary = gateway.call("run_studio_extension", "similarity", {"left": {"cells": ["C01"]}, "right": {"cells": ["C01"]}}); _require(arbitrary.get("state") == "ERROR", "arbitrary caller representation was accepted")
	var artwork := JSON.parse_string(FileAccess.get_file_as_string(str(first.get("metadata_path", "")).get_base_dir().path_join("artwork.json"))) as Dictionary; var cells: Array = artwork.get("cells", []).duplicate()
	var root_revision: Dictionary = gateway.call("run_studio_extension", "revision-create", {"candidate_id": left_id, "width": 20, "height": 20, "cells": cells, "change_summary": "similarity root"}); var root_id := str(root_revision.get("revision", {}).get("revision_id", "")); var changed := cells.duplicate(); changed[0] = "C01" if changed[0] != "C01" else "C02"
	var near_revision: Dictionary = gateway.call("run_studio_extension", "revision-create", {"candidate_id": left_id, "width": 20, "height": 20, "cells": changed, "parent_revision_id": root_id, "change_summary": "similarity one cell"}); var near_id := str(near_revision.get("revision", {}).get("revision_id", ""))
	var near: Dictionary = gateway.call("run_studio_extension", "similarity", {"left_id": left_id, "right_id": near_id, "threshold": 0.92}); _require(near.get("disposition") == "POSSIBLE_SIMILAR" and int(near.get("distance", 0)) == 1 and near.get("advisory") == true, "near duplicate did not use canonical revision identity: %s" % near)
	var repeated: Dictionary = gateway.call("run_studio_extension", "similarity", {"left_id": left_id, "right_id": near_id, "threshold": 0.92}); _require(repeated == near, "repeated identical similarity comparison was not deterministic")
	var boundary: Dictionary = gateway.call("run_studio_extension", "similarity", {"left_id": left_id, "right_id": near_id, "threshold": near.get("score", 0.0)}); _require(boundary.get("disposition") == "POSSIBLE_SIMILAR", "threshold-boundary comparison was not inclusive")
	_require(near.get("left_grid_hash") != near.get("right_grid_hash") and near.get("distance") == 1, "explicit palette-cell change did not produce changed revision identity")
	var distinct: Dictionary = gateway.call("run_studio_extension", "similarity", {"left_id": left_id, "right_id": right_id, "threshold": 0.99}); _require(distinct.get("left_identity") == left_id and distinct.get("right_identity") == right_id and distinct.get("advisory") == true, "distinct comparison was not canonical/advisory: %s" % distinct)
	var review: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": left_id, "disposition": "ACCEPT", "reason": "similarity matrix"}); var review_before: Dictionary = _snapshot_tree(ProjectSettings.globalize_path("res://output/studio-extensions/owner-review")); var similarity_before: Dictionary = gateway.call("run_studio_extension", "similarity", {"left_id": left_id, "right_id": near_id}); var review_after: Dictionary = _snapshot_tree(ProjectSettings.globalize_path("res://output/studio-extensions/owner-review")); _require(review_before == review_after, "similarity changed candidate-bound owner review evidence")
	surface.call("set_ids", left_id, near_id); surface.call("compare"); await process_frame; _require(surface.call("snapshot").get("projection", {}).get("policy") == "SIMILARITY_POLICY_V1", "similarity UI did not invoke canonical policy")
	var comparison: Dictionary = gateway.call("run_studio_extension", "comparison", {"candidate_ids": [left_id, right_id]}); _require(comparison.get("similarity_advisory", {}).get("policy") == "SIMILARITY_POLICY_V1" and comparison.get("similarity_advisory", {}).get("advisory") == true, "Comparison surface did not consume canonical similarity evidence")
	var inbox: Dictionary = gateway.call("run_studio_extension", "candidate-inbox", {}); _require(inbox.get("candidates", []).any(func(item): return item.get("similarity_advisory", {}).get("disposition") == "NOT AVAILABLE"), "Candidate surface did not expose explicit advisory similarity state")
	candidates_surface.call("refresh_inbox"); candidates_surface.call("set_comparison_ids", left_id, right_id); candidates_surface.call("compare_selected"); await process_frame
	_require(str(candidates_surface.call("rendered_text")).contains("advisory only") and str(candidates_surface.call("rendered_text")).contains("owner review decides significance"), "Candidate surface did not render advisory peer comparison language")
	var search: Dictionary = gateway.call("run_studio_extension", "discover", {"filters": {"record_type": "CANDIDATE"}, "similarity_peer_id": right_id}); _require(search.get("records", []).any(func(item): return item.get("record_id") == left_id and item.get("similarity_advisory", {}).get("disposition") != "NOT AVAILABLE"), "Search backend did not bind canonical peer similarity evidence")
	search_surface.call("set_similarity_peer", right_id); search_surface.call("refresh_search"); await process_frame
	_require(str(search_surface.call("rendered_text")).contains("Similarity advisory only") and str(search_surface.call("rendered_text")).contains("score="), "Search surface dropped operator-visible similarity advisory evidence")
	var revision_path := ProjectSettings.globalize_path("res://output/studio-extensions/revisions").path_join(left_id).path_join("%s.json" % near_id); var before := FileAccess.get_file_as_bytes(revision_path); var tamper := FileAccess.open(revision_path, FileAccess.WRITE); tamper.store_string("{\"tampered\":true}\n"); tamper.close(); var stale: Dictionary = gateway.call("run_studio_extension", "similarity", {"left_id": left_id, "right_id": near_id}); _require(stale.get("state") == "ERROR", "tampered canonical revision was not rejected"); var restore := FileAccess.open(revision_path, FileAccess.WRITE); restore.store_buffer(before); restore.close()
	_cleanup(instance)

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx016-similarity-a")); _remove_tree(ProjectSettings.globalize_path("res://output/.lfx016-similarity-b")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); instance.queue_free(); _finish()

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

func _snapshot_tree(path: String) -> Dictionary:
	var snapshot := {}
	if not DirAccess.dir_exists_absolute(path): return snapshot
	var directory := DirAccess.open(path); if directory == null: return snapshot
	directory.list_dir_begin()
	while true:
		var entry := directory.get_next(); if entry.is_empty(): break
		if entry in [".", ".."]: continue
		var child := path.path_join(entry)
		if directory.current_is_dir(): snapshot[entry] = _snapshot_tree(child)
		else: snapshot[entry] = FileAccess.get_file_as_bytes(child)
	directory.list_dir_end()
	return snapshot

func _require(condition: bool, message: String) -> void:
	if not condition: _errors.append(message)

func _finish() -> void:
	if _errors.is_empty(): print(PASS_MARKER); quit(0); return
	for error in _errors: push_error(error)
	quit(1)
