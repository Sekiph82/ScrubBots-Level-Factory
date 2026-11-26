from pathlib import Path

p = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\level_factory\scripts\factory_studio_exact_ui.gd")
s = p.read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new, 1)


rep("var _pixel_batch_active := false\n",
    "var _pixel_batch_active := false\n"
    "## Owner request 2026-11-24: \"\" | \"PAUSE\" | \"STOP\"; applied when the running paid row finishes.\n"
    "var _pixel_batch_control := \"\"\n"
    "var _pixel_batch_paused := false\n")

# captions
rep('"SingleMode": "Single", "BatchMode": "Batch", "BatchCsvPath": "CSV file…",',
    '"SingleMode": "Single", "BatchMode": "Batch", "BatchCsvPath": "CSV file…",\n'
    '\t\t"PausePixelBatch": "Pausing…" if _pixel_batch_control == "PAUSE" else "Pause after current",\n'
    '\t\t"StopPixelBatch": "Stopping…" if _pixel_batch_control == "STOP" else "Stop after current",')

# buttons placed on the same row as CSV file | Run Batch
rep('\t_place_control("BatchCsvPath", Rect2(27, 261, 160, 45), _open_batch_csv)\n',
    '\t_place_control("BatchCsvPath", Rect2(27, 261, 160, 45), _open_batch_csv)\n'
    '\t# Owner request 2026-11-24: while a CSV batch runs, CSV file|Run Batch become Pause|Stop after current.\n'
    '\t_place_control("PausePixelBatch", Rect2(27, 261, 160, 45), _request_pixel_batch_control.bind("PAUSE"))\n'
    '\t_place_control("StopPixelBatch", Rect2(198, 261, 162, 45), _request_pixel_batch_control.bind("STOP"))\n')

rep('"SingleMode", "BatchMode", "BatchCsvPath", "ArtworkVariation1",',
    '"SingleMode", "BatchMode", "BatchCsvPath", "PausePixelBatch", "StopPixelBatch", "ArtworkVariation1",')

rep('''		if batch_path != null: batch_path.visible = _generation_mode == "BATCH"
		if run_batch != null: run_batch.visible = _generation_mode == "BATCH"
''', '''		var batch_running := _pixel_batch_active
		if batch_path != null: batch_path.visible = _generation_mode == "BATCH" and not batch_running
		if run_batch != null: run_batch.visible = _generation_mode == "BATCH" and not batch_running
		for control_name in ["PausePixelBatch", "StopPixelBatch"]:
			var control := get_node_or_null(control_name) as Button
			if control != null:
				control.visible = _generation_mode == "BATCH" and batch_running
				control.disabled = not _pixel_batch_control.is_empty()
''')

# resume a paused batch from Run Batch (shown as "Resume")
rep('''func _run_batch() -> void:
''', '''func _run_batch() -> void:
	if _pixel_batch_paused and not _pixel_batch_active and not _operation_running and _pixel_batch_index < _pixel_batch_rows.size():
		_pixel_batch_paused = false
		_pixel_batch_control = ""
		_pixel_batch_active = true
		_set_batch_action_label(false)
		_record_pixel_art_activity("BATCH", "RESUMED", "Resumed at row %d/%d; %d prompts remain." % [_pixel_batch_index + 1, _pixel_batch_rows.size(), _pixel_batch_rows.size() - _pixel_batch_index])
		_update_master_control_visibility()
		_start_next_pixellab_batch_row()
		return
''')

# act on the request after a successful row
rep('''		_pixel_batch_succeeded += 1
		_pixel_batch_index += 1
		_semantic_progress = {"completed": _pixel_batch_succeeded, "failed": 0, "remaining": _pixel_batch_rows.size() - _pixel_batch_index, "state": "RUNNING"}
		_start_next_pixellab_batch_row()
		return
''', '''		_pixel_batch_succeeded += 1
		_pixel_batch_index += 1
		_semantic_progress = {"completed": _pixel_batch_succeeded, "failed": 0, "remaining": _pixel_batch_rows.size() - _pixel_batch_index, "state": "RUNNING"}
		if _apply_pixel_batch_control():
			return
		_start_next_pixellab_batch_row()
		return
''')

# a failed row already stops the batch: clear any pending request
rep('''			_record_pixel_art_activity("BATCH", "STOPPED_AFTER_FAILURE", "Stopped after the first unsuccessful row; %d prompts remain. No retry or additional paid request was sent." % remaining)
''', '''			_record_pixel_art_activity("BATCH", "STOPPED_AFTER_FAILURE", "Stopped after the first unsuccessful row; %d prompts remain. No retry or additional paid request was sent." % remaining)
			_pixel_batch_control = ""
			_pixel_batch_paused = false
''')

rep('''func _start_next_pixellab_batch_row() -> void:
''', '''func _request_pixel_batch_control(action: String) -> void:
	if not _pixel_batch_active or not _pixel_batch_control.is_empty():
		return
	_pixel_batch_control = action
	var verb := "pause" if action == "PAUSE" else "stop"
	_record_pixel_art_activity("BATCH", action + "_REQUESTED", "The running paid row finishes and is saved first; the batch will %s before sending the next request." % verb)
	_update_master_control_visibility()


## Applies a Pause/Stop request after a finished row. Returns true when no further row starts.
func _apply_pixel_batch_control() -> bool:
	if _pixel_batch_control.is_empty():
		return false
	var remaining := maxi(0, _pixel_batch_rows.size() - _pixel_batch_index)
	var action := _pixel_batch_control
	_pixel_batch_control = ""
	_pixel_batch_active = false
	if action == "PAUSE" and remaining > 0:
		_pixel_batch_paused = true
		_semantic_progress = {"completed": _pixel_batch_succeeded, "failed": _pixel_batch_failed, "remaining": remaining, "state": "PAUSED"}
		_set_batch_action_label(true)
		_record_pixel_art_activity("BATCH", "PAUSED", "Paused after row %d/%d; %d prompts remain. Press Resume to continue; no request was sent." % [_pixel_batch_index, _pixel_batch_rows.size(), remaining])
	else:
		_pixel_batch_paused = false
		_semantic_progress = {"completed": _pixel_batch_succeeded, "failed": _pixel_batch_failed, "remaining": remaining, "state": "STOPPED_BY_OWNER"}
		_record_pixel_art_activity("BATCH", "STOPPED_BY_OWNER", "Stopped after row %d/%d; %d prompts were not sent." % [_pixel_batch_index, _pixel_batch_rows.size(), remaining])
		_batch_csv_path = ""
		_pixel_batch_rows.clear()
		_refresh_batch_csv_button()
	_report("PixelLab batch %s · %d succeeded · %d not sent" % ["paused" if _pixel_batch_paused else "stopped", _pixel_batch_succeeded, remaining])
	_update_master_control_visibility()
	return true


func _start_next_pixellab_batch_row() -> void:
''')

# a fresh confirmed batch starts with no pending request and no paused state
rep('''		_pixel_batch_failed = 0
		_pixel_batch_active = true
''', '''		_pixel_batch_failed = 0
		_pixel_batch_active = true
		_pixel_batch_control = ""
		_pixel_batch_paused = false
		_set_batch_action_label(false)
		_update_master_control_visibility()
''')
p.write_text(s, encoding="utf-8")
print("applied")
