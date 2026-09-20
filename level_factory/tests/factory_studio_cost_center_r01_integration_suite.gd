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
	var view: Dictionary = gateway.call("run_studio_extension", "cost-center", {"scope": "runtime-test", "records": [{"provider": "FORGED", "consumed": 999999}]}); _require(view.get("version") == 2 and view.get("network_calls") == 0, "cost center did not use canonical read-only discovery: %s" % [view])
	var groups: Array = view.get("groups", []); _require(groups.size() == 2, "mixed units/providers were not separated: %s" % [groups])
	var magnific: Dictionary = groups[0] if groups[0].get("provider") == "MAGNIFIC" else groups[1]; var pixellab: Dictionary = groups[0] if groups[0].get("provider") == "PIXELLAB" else groups[1]
	_require(magnific.get("jobs") == 2 and magnific.get("success") == 1 and magnific.get("failure") == 1 and magnific.get("consumed") == 14 and magnific.get("remaining") == 86 and magnific.get("cost_per_owner_accepted") == 14, "canonical Magnific metrics were incorrect: %s" % [magnific])
	_require(pixellab.get("consumed") == null and pixellab.get("remaining") == null and "remaining" in pixellab.get("unknown", []), "unknown PixelLab accounting was fabricated")
	surface.call("refresh"); await process_frame; _require(surface.call("snapshot").get("projection", {}).get("version") == 2, "Cost Center UI did not invoke canonical accounting projection")
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

func _require(condition: bool, message: String) -> void:
	if not condition: _errors.append(message)

func _finish() -> void:
	if _errors.is_empty(): print(PASS_MARKER); quit(0); return
	for error in _errors: push_error(error)
	quit(1)
