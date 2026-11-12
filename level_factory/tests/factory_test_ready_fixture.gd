extends RefCounted

## Test-only hash-bound READY pipeline fixture (2026-11-12).
##
## Replaces the owner's saved 002 READY run (deleted 2026-11-07). The level,
## supply-plan and result files are written inside the isolated checkout copy
## (factory_test_paths.gd refuses the owner's real data), and the pipeline's
## solver_supply_identity binds their exact bytes, so the Studio's
## _verify_saved_solver_artifacts() check runs for real.

const TEST_PATHS := preload("res://tests/factory_test_paths.gd")


static func sha256(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()


static func write_text(path: String, text: String) -> String:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var handle := FileAccess.open(path, FileAccess.WRITE)
	handle.store_string(text)
	handle.close()
	return path


## `batches` recorded moves spread round-robin over four supply columns.
static func build(source_id: String, run_id: String, batches: int = 4) -> Dictionary:
	var work := TEST_PATHS.data("Release Pool/Pending/Pipelines/Work/%s" % run_id)
	var level_text := JSON.stringify({"version": 1, "id": run_id, "name": "Fixture", "difficulty": "EASY",
		"width": 20, "height": 20, "palette": ["#FF4500FF", "#FFA800FF"], "cells": []})
	var supply_text := JSON.stringify({"schema": "scrubbots.level_supply_plan.v1", "version": 1, "columnCount": 4})
	var level_path := write_text(work.path_join("level.json"), level_text)
	var supply_path := write_text(work.path_join("level_supply_v1.json"), supply_text)
	var identity := {"level_data_sha256": sha256(level_text.to_utf8_buffer()), "supply_plan_sha256": sha256(supply_text.to_utf8_buffer())}
	var columns := [[], [], [], []]
	var totals := [0, 0, 0, 0]
	var trace := []
	var remaining := batches * 3
	for step in range(batches):
		var column := step % 4
		var batch := {"color": "C%02d" % (column + 1), "amount": 3}
		columns[column].append(batch)
		totals[column] += 3
		remaining -= 3
		trace.append({"column": column + 1, "batch": batch, "clears": 3, "pixels_left": remaining})
	var result_text := JSON.stringify({"solver_supply_identity": identity, "supply_columns": columns, "column_pixel_totals": totals,
		"total_batches": batches, "visible_preview_depth": 3, "solution_trace": trace,
		"solution_replay": {"ok": true, "solved": true, "finalActive": 0}, "color_conservation_verification": {"all_ok": true}})
	var result_path := write_text(work.path_join("result.json"), result_text)
	var result: Dictionary = JSON.parse_string(result_text)
	return {"run_id": run_id, "source_id": source_id, "disposition": "READY",
		"request": {"source_id": source_id, "activity_source_sha256": source_id.trim_prefix("owner-upload-"), "activity_run_id": "activity-" + run_id},
		"primary": {"state": "READY", "solver_supply_identity": identity, "result": result,
			"files": {"level": level_path, "supply_plan": supply_path, "result": result_path},
			"acceptance": {"replay": "WIN"}, "difficulty": {"class": "MEDIUM"}}}
