extends SceneTree

const PASS_MARKER := "SB-LFX-012-C001 REVISION lineage integration PASS"
var _errors: Array[String] = []

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway")
	var target := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/TargetControls")
	var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/ManualEditRevisions")
	_require(gateway != null and surface != null and target != null, "revision surface, editor target, or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx012-revisions")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var generated: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "12012", "mode": "MASK"}, "res://output/.lfx012-revisions")
	_require(generated.get("state") == "SUCCESS", "canonical revision fixture failed: %s" % generated)
	var candidate_id := str(generated.get("candidate_id", "")); var bundle := str(generated.get("output_path", "")); var artwork := JSON.parse_string(FileAccess.get_file_as_string(bundle.path_join("artwork.json"))) as Dictionary
	var source_bytes := FileAccess.get_file_as_bytes(bundle.path_join("artwork.png"))
	var editor: Node = target.call("manual_editor_reference"); editor.call("observe_action_result", generated); _require(editor.call("load_current_canonical_artwork", true), "manual editor did not load canonical source")
	var owner_review: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": candidate_id, "disposition": "ACCEPT", "reason": "R03 revision matrix review"})
	_require(owner_review.get("disposition") == "ACCEPT", "real owner-review evidence was not created")
	var review_path := ProjectSettings.globalize_path("res://output/studio-extensions/owner-review").path_join(str(owner_review.get("review_id", "")) + ".json")
	var review_bytes := FileAccess.get_file_as_bytes(review_path)
	surface.call("configure_editor", editor); surface.call("set_candidate_id", candidate_id)
	var cells: Array = editor.call("working_logical_cells_snapshot"); var first: Dictionary = surface.call("save_revision")
	_require(first.get("state") == "SUCCESS", "root revision was not created: %s" % first)
	var first_id := str(first.get("revision", {}).get("revision_id", "")); editor.call("paint_cell", 0, 0, "C01" if cells[0] != "C01" else "C02"); var second: Dictionary = surface.call("save_revision")
	_require(second.get("state") == "SUCCESS" and int(second.get("revision", {}).get("change_count", -1)) == 1, "child revision did not record exact change count: %s" % second)
	var second_id := str(second.get("revision", {}).get("revision_id", "")); editor.call("paint_cell", 1, 0, "C03"); var third: Dictionary = surface.call("save_revision")
	_require(third.get("state") == "SUCCESS" and int(third.get("revision", {}).get("change_count", -1)) == 1, "R2 editor save did not record exact change count: %s" % third)
	var third_id := str(third.get("revision", {}).get("revision_id", "")); surface.call("set_candidate_id", candidate_id); surface.call("list_revisions"); await process_frame
	var listing: Dictionary = surface.call("snapshot").get("projection", {}); _require(listing.get("state") == "SUCCESS" and (listing.get("revisions", []) as Array).size() == 3, "revision list did not expose immutable lineage: %s" % listing)
	surface.call("set_compare_revisions", first_id, third_id)
	surface.call("compare_revisions"); await process_frame
	var comparison: Dictionary = surface.call("snapshot").get("projection", {}); _require(comparison.get("comparison", {}).get("changed_cell_count") == 2, "revision surface Compare did not report editor changes: %s" % comparison)
	surface.call("set_candidate_id", candidate_id); surface.call("set_revision_id", second_id); surface.call("select_revision"); await process_frame
	_require(editor.call("snapshot").get("dirty_cell_count") == 1, "surface Select/Undo did not replace the manual editor working grid")
	var branch_cells: Array = editor.call("working_logical_cells_snapshot"); editor.call("paint_cell", 2, 0, "C04"); var branch: Dictionary = surface.call("save_revision"); _require(branch.get("state") == "SUCCESS" and branch.get("revision", {}).get("parent_revision_id") == second_id, "edit-after-undo did not create a branch from the selected revision: %s" % branch)
	var branch_id := str(branch.get("revision", {}).get("revision_id", "")); _require(branch_id != third_id, "branch revision overwrote later R2 history")
	surface.call("restore_source"); _require(editor.call("snapshot").get("dirty_cell_count") == 0, "Restore Source did not restore editor working pixels")
	_require(FileAccess.get_file_as_bytes(review_path) == review_bytes, "revision operations mutated owner-review evidence bytes")
	var readiness: Dictionary = gateway.call("run_studio_extension", "readiness", {"candidate_id": candidate_id}); _require(readiness.get("gates", {}).get("OWNER", {}).get("disposition") == "PASS", "revision operations changed owner-review truth"); _require(readiness.get("gates", {}).get("EXPORT", {}).get("disposition") == "NOT_AVAILABLE", "revision operations fabricated export truth")
	# A real Studio teardown/reinstantiate is required; the new surface reconstructs the durable history.
	instance.queue_free(); await process_frame; await process_frame
	var restarted := packed.instantiate(); root.add_child(restarted); await process_frame
	var gateway_after_restart: RefCounted = restarted.get("core_gateway"); var target_after_restart := restarted.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/TargetControls"); var surface_after_restart := restarted.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/ManualEditRevisions")
	var editor_after_restart: Node = target_after_restart.call("manual_editor_reference"); editor_after_restart.call("observe_action_result", generated); _require(editor_after_restart.call("load_current_canonical_artwork", true), "restarted Studio did not reload canonical source")
	surface_after_restart.call("configure_editor", editor_after_restart); surface_after_restart.call("set_candidate_id", candidate_id); surface_after_restart.call("list_revisions"); await process_frame
	var persisted: Dictionary = surface_after_restart.call("snapshot").get("projection", {}); _require(persisted.get("state") == "SUCCESS" and (persisted.get("revisions", []) as Array).size() == 4, "fresh Studio did not reconstruct branch and R2 history")
	surface_after_restart.call("set_compare_revisions", first_id, branch_id); surface_after_restart.call("compare_revisions"); await process_frame
	_require(surface_after_restart.call("snapshot").get("projection", {}).get("comparison", {}).get("changed_cell_count") == 2, "restarted revision surface Compare did not reconstruct lineage")
	var restarted_readiness: Dictionary = gateway_after_restart.call("run_studio_extension", "readiness", {"candidate_id": candidate_id}); _require(restarted_readiness.get("gates", {}).get("OWNER", {}).get("disposition") == "PASS" and restarted_readiness.get("gates", {}).get("EXPORT", {}).get("disposition") == "NOT_AVAILABLE", "restart changed review/promotion truth")
	var corrupt_path := ProjectSettings.globalize_path("res://output/studio-extensions/revisions").path_join(candidate_id).path_join("revision-0001.json"); var corrupt_bytes := FileAccess.get_file_as_bytes(corrupt_path); var corrupt := FileAccess.open(corrupt_path, FileAccess.WRITE); corrupt.store_string("{\"corrupt\":true}\n"); corrupt.close(); var rejected: Dictionary = gateway_after_restart.call("run_studio_extension", "revision-list", {"candidate_id": candidate_id}); _require(rejected.get("state") == "ERROR", "corrupt revision lineage did not fail closed"); var restore := FileAccess.open(corrupt_path, FileAccess.WRITE); restore.store_buffer(corrupt_bytes); restore.close()
	surface_after_restart.call("list_revisions"); await process_frame; _require(surface_after_restart.call("snapshot").get("projection", {}).get("state") == "SUCCESS", "restored revision history did not reload through the surface")
	_require(FileAccess.get_file_as_bytes(review_path) == review_bytes, "restart/corruption recovery changed owner-review evidence bytes")
	for revision in surface_after_restart.call("snapshot").get("projection", {}).get("revisions", []): _require(revision.get("validation", {}).get("disposition") != "PASS", "manual revision leaked validation acceptance")
	_require(FileAccess.get_file_as_bytes(bundle.path_join("artwork.png")) == source_bytes, "revision operations mutated source artwork bytes")
	var standalone: Dictionary = gateway_after_restart.call("run_studio_extension", "revision-create", {"candidate_id": candidate_id, "width": 20, "height": 20, "cells": cells}); _require(standalone.get("state") == "ERROR", "standalone post-root revision was not rejected")
	_cleanup(restarted)

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx012-revisions")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); instance.queue_free(); _finish()

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
