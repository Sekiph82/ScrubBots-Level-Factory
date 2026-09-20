extends SceneTree

const PASS_MARKER := "SB-LFX-009-C001 SEARCH integration PASS"
var _errors: Array[String] = []
var _fixture_root := ""

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var search := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/DiscoverySearch")
	var gateway: RefCounted = instance.get("core_gateway")
	_require(search != null and gateway != null, "search surface or gateway did not instantiate")
	if search == null or gateway == null: _cleanup(instance); return
	_fixture_root = OS.get_temp_dir().path_join("scrubbots_lfx_009_search_fixture"); _remove_tree(_fixture_root); DirAccess.make_dir_recursive_absolute(_fixture_root)
	var image := Image.create(20, 20, false, Image.FORMAT_RGB8); image.fill(Color8(233, 75, 75)); var source_path := _fixture_root.path_join("search-source.png"); image.save_png(source_path)
	var imported: Dictionary = gateway.call("run_owner_import", source_path); var source_id := str(imported.get("source_id", "")); _require(imported.get("state") in ["IMPORTED", "ALREADY_IMPORTED"], "search source import failed")
	gateway.call("run_studio_extension", "library-save", {"source_id": source_id, "label": "Search Alpha", "tags": ["alpha"]})
	var left: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "99009", "mode": "RULES"}, "res://output/.lfx009-search")
	var right: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 21, "height": 20, "seed": "99010", "mode": "RULES"}, "res://output/.lfx009-search")
	_require(left.get("state") == "SUCCESS" and right.get("state") == "SUCCESS", "search candidates did not generate: %s / %s" % [left, right])
	var left_id := str(left.get("candidate_id", "")); var right_id := str(right.get("candidate_id", ""))
	gateway.call("run_studio_extension", "owner-review", {"candidate_id": left_id, "disposition": "ACCEPT", "reason": "search accepted"})
	var combined: Dictionary = gateway.call("run_studio_extension", "discover", {"query": "", "filters": {"record_type": "CANDIDATE", "width": 20, "review": "ACCEPT"}})
	_require(combined.get("state") == "READY" and combined.get("records", []).size() >= 1, "combined canonical filters did not find accepted candidate: %s" % combined)
	var imported_sources: Dictionary = gateway.call("run_studio_extension", "discover", {"query": "search alpha", "collection": "Imported Sources"})
	_require(imported_sources.get("records", []).size() == 1 and imported_sources.get("records", [])[0].get("record_id") == source_id, "text search/imported source collection failed")
	var needs_review: Dictionary = gateway.call("run_studio_extension", "discover", {"collection": "Needs Review"})
	_require(not needs_review.get("records", []).any(func(record): return record.get("record_type") == "SOURCE"), "source-only NOT AVAILABLE review was inferred as Needs Review")
	var unavailable: Dictionary = gateway.call("run_studio_extension", "discover", {"collection": "Ready for Production"})
	_require(unavailable.get("state") == "NOT AVAILABLE" and unavailable.get("records", []).is_empty(), "unavailable collection was guessed")
	var before: Dictionary = gateway.call("run_studio_extension", "discover", {"query": "search"})
	gateway.call("run_studio_extension", "owner-review", {"candidate_id": right_id, "disposition": "REJECT", "reason": "search rejected"})
	var after: Dictionary = gateway.call("run_studio_extension", "discover", {"collection": "Owner Rejected"})
	_require(after.get("records", []).any(func(record): return record.get("record_id") == right_id), "refresh did not reflect canonical review change")
	_require(before.get("mutated") == false and after.get("mutated") == false, "discovery mutated canonical records")
	search.call("show_search"); await process_frame
	_cleanup(instance)

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _remove_tree(ProjectSettings.globalize_path("res://output/.lfx009-search")); _remove_tree(ProjectSettings.globalize_path("res://output/owner-uploads")); _remove_tree(_fixture_root); instance.queue_free(); _finish()

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
