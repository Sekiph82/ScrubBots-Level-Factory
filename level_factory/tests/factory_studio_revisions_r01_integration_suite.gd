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
	var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/ManualEditRevisions")
	_require(gateway != null and surface != null, "revision surface or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx012-revisions")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions"))
	var generated: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "12012", "mode": "MASK"}, "res://output/.lfx012-revisions")
	_require(generated.get("state") == "SUCCESS", "canonical revision fixture failed: %s" % generated)
	var candidate_id := str(generated.get("candidate_id", "")); var bundle := str(generated.get("output_path", "")); var artwork := JSON.parse_string(FileAccess.get_file_as_string(bundle.path_join("artwork.json"))) as Dictionary
	var cells: Array = artwork.get("cells", []).duplicate(); var first: Dictionary = gateway.call("run_studio_extension", "revision-create", {"candidate_id": candidate_id, "width": 20, "height": 20, "cells": cells, "change_summary": "root"})
	_require(first.get("state") == "SUCCESS", "root revision was not created: %s" % first)
	var first_id := str(first.get("revision", {}).get("revision_id", "")); var changed := cells.duplicate(); changed[0] = "C01" if changed[0] != "C01" else "C02"
	var second: Dictionary = gateway.call("run_studio_extension", "revision-create", {"candidate_id": candidate_id, "width": 20, "height": 20, "cells": changed, "parent_revision_id": first_id, "change_summary": "one cell", "edit_operations": [{"operation": "PAINT", "indices": [0], "summary": "paint cell 0"}]})
	_require(second.get("state") == "SUCCESS" and int(second.get("revision", {}).get("change_count", -1)) == 1, "child revision did not record exact change count: %s" % second)
	var listing: Dictionary = gateway.call("run_studio_extension", "revision-list", {"candidate_id": candidate_id}); _require(listing.get("state") == "SUCCESS" and (listing.get("revisions", []) as Array).size() == 2, "revision list did not expose immutable lineage: %s" % listing)
	var comparison: Dictionary = gateway.call("run_studio_extension", "revision-compare", {"candidate_id": candidate_id, "left_revision_id": first_id, "right_revision_id": str(second.get("revision", {}).get("revision_id", ""))}); _require(comparison.get("comparison", {}).get("changed_cell_count") == 1, "revision compare did not report the changed cell: %s" % comparison)
	surface.call("list_revisions"); await process_frame; _require(surface.call("snapshot").get("projection", {}).get("state") == "SUCCESS", "revision UI did not invoke the canonical list operation")
	var standalone: Dictionary = gateway.call("run_studio_extension", "revision-create", {"candidate_id": candidate_id, "width": 20, "height": 20, "cells": cells}); _require(standalone.get("state") == "ERROR", "standalone post-root revision was not rejected")
	_cleanup(instance)

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
