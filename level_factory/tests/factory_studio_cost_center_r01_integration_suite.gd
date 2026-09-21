extends SceneTree

const PASS_MARKER := "SB-LFX-017-C001 ACCOUNTING evidence integration PASS"
var _errors: Array[String] = []
var _accounting_root := ""

func _init() -> void: call_deferred("_run_suite")

func _run_suite() -> void:
	var packed := ResourceLoader.call("load", "res://scenes/factory_studio.tscn") as PackedScene
	_require(packed != null, "Studio scene did not load")
	if packed == null: _finish(); return
	var instance := packed.instantiate(); root.add_child(instance); await process_frame
	var gateway: RefCounted = instance.get("core_gateway"); var surface := instance.get_node_or_null("Frame/Layout/Body/Workspace/Padding/Content/ProviderCostCenter")
	_require(gateway != null and surface != null, "cost center surface or gateway did not instantiate")
	if gateway == null: _cleanup(instance); return
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx017-accounting")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); _accounting_root = ProjectSettings.globalize_path("res://output/studio-extensions/accounting"); DirAccess.make_dir_recursive_absolute(_accounting_root)
	var generated: Dictionary = gateway.call("run_action", "Generate", {"difficulty": "EASY", "width": 20, "height": 20, "seed": "17017", "mode": "MASK"}, "res://output/.lfx017-accounting"); _require(generated.get("state") == "SUCCESS", "accounting candidate fixture failed")
	var candidate_id := str(generated.get("candidate_id", "")); var review: Dictionary = gateway.call("run_studio_extension", "owner-review", {"candidate_id": candidate_id, "disposition": "ACCEPT", "reason": "accounting evidence"}); _require(review.get("disposition") == "ACCEPT", "canonical owner review fixture failed: %s" % review)
	var review_id := str(review.get("review_id", "")); _write_record({"schema": "scrubbots-provider-accounting-record", "version": 1, "record_id": "acct-magnific-success", "provider": "MAGNIFIC", "unit": "credits", "scope": "runtime-test", "status": "SUCCESS", "consumed": 10, "remaining": 90, "candidate_id": candidate_id, "owner_review_id": review_id, "recorded_at": "2026-09-20T10:00:00+00:00", "evidence_reference": "fixture/acct-magnific-success"})
	_write_record({"schema": "scrubbots-provider-accounting-record", "version": 1, "record_id": "acct-magnific-failure", "provider": "MAGNIFIC", "unit": "credits", "scope": "runtime-test", "status": "FAILED", "consumed": 4, "remaining": 86, "candidate_id": candidate_id, "owner_review_id": null, "recorded_at": "2026-09-20T11:00:00+00:00", "evidence_reference": "fixture/acct-magnific-failure"})
	_write_record({"schema": "scrubbots-provider-accounting-record", "version": 1, "record_id": "acct-pixellab-unknown", "provider": "PIXELLAB", "unit": "USD", "scope": "runtime-test", "status": "SUCCESS", "consumed": null, "remaining": null, "candidate_id": null, "owner_review_id": null, "recorded_at": "2026-09-20T12:00:00+00:00", "evidence_reference": "fixture/acct-pixellab-unknown"})
	var candidate_bytes_before := FileAccess.get_file_as_bytes(str(generated.get("metadata_path", ""))); var review_root := ProjectSettings.globalize_path("res://output/studio-extensions/owner-review"); var review_before: Dictionary = _snapshot_tree(review_root)
	var view: Dictionary = gateway.call("run_studio_extension", "cost-center", {"scope": "runtime-test", "records": [{"provider": "FORGED", "consumed": 999999}]}); _require(view.get("version") == 3 and view.get("authoritative") == false and view.get("network_calls") == 0 and view.get("credit_spend") == 0, "cost center did not truthfully report unavailable accounting: %s" % [view])
	var groups: Array = view.get("groups", []); _require(groups.size() >= 2, "cost center did not retain explicit per-provider/unit unavailable rows: %s" % [groups])
	for group in groups: _require(group.get("consumed") == null and group.get("remaining") == null and "cost_per_success" in group.get("unknown", []), "manual accounting JSON fabricated financial metrics")
	_write_record({"schema": "scrubbots-provider-accounting-record", "version": 1, "record_id": "acct-malformed-secret", "provider": "FORGED", "unit": "credits", "scope": "runtime-test", "status": "SUCCESS", "consumed": 999999, "secret": "do-not-render"})
	var refreshed: Dictionary = gateway.call("run_studio_extension", "cost-center", {"scope": "runtime-test"}); _require(refreshed.get("authoritative") == false and refreshed.get("rejected_record_ids", []).has("acct-malformed-secret") and not str(refreshed).contains("do-not-render"), "malformed/secret accounting evidence was not rejected safely")
	_require(FileAccess.get_file_as_bytes(str(generated.get("metadata_path", ""))) == candidate_bytes_before and _snapshot_tree(review_root) == review_before, "Cost Center refresh mutated candidate/review evidence")
	surface.call("refresh"); await process_frame; _require(surface.call("snapshot").get("projection", {}).get("version") == 3 and surface.call("snapshot").get("projection", {}).get("network_calls") == 0, "Cost Center UI did not render canonical unavailable accounting projection")
	_cleanup(instance)

func _write_record(value: Dictionary) -> void:
	var file := FileAccess.open(_accounting_root.path_join("%s.json" % value["record_id"]), FileAccess.WRITE); file.store_string(JSON.stringify(value)); file.close()

func _cleanup(instance: Node) -> void:
	_remove_tree(ProjectSettings.globalize_path("res://output/.lfx017-accounting")); _remove_tree(ProjectSettings.globalize_path("res://output/studio-extensions")); instance.queue_free(); _finish()

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
