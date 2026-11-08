extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var ui := Control.new()
	ui.set_script(UI_SCRIPT)
	root.add_child(ui)
	await process_frame
	var rows := [
		{"source_id": "owner-upload-" + "f".repeat(64), "display_filename": "LF-000003.png"},
		{"source_id": "owner-upload-" + "1".repeat(64), "display_filename": "LF-000001.png"},
		{"source_id": "owner-upload-" + "a".repeat(64), "display_filename": "LF-000002.png"},
	]
	for row in rows:
		ui.call("_upsert_imported_source", {
			"path": "", "source_id": row["source_id"],
			"source_record_sha256": "b".repeat(64),
			"display_filename": row["display_filename"],
			"width": 32, "height": 32, "disposition": "IMPORTED",
		})
	var ordered: Array = ui.get("_gameplay_sources")
	var expected := ["LF-000001.png", "LF-000002.png", "LF-000003.png"]
	var failed := ordered.size() != expected.size()
	for index in range(mini(ordered.size(), expected.size())):
		if str(ordered[index].get("display_filename", "")) != expected[index]:
			push_error("numeric LF source order mismatch at %d: %s" % [index, str(ordered[index].get("display_filename", ""))])
			failed = true
	if not failed:
		print("Factory Studio numeric LF filename ordering PASS")
	ui.queue_free()
	await process_frame
	quit(1 if failed else 0)
