extends SceneTree

const UI_SCRIPT := preload("res://scripts/factory_studio_exact_ui.gd")
const PASS_MARKER := "Factory Studio batch CSV UI state PASS"

var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run_suite")


func _run_suite() -> void:
	var ui := Control.new()
	ui.name = "FactoryStudioBatchCsvUiState"
	ui.set_script(UI_SCRIPT)
	var batch_button := Button.new()
	batch_button.name = "BatchCsvPath"
	ui.add_child(batch_button)
	root.add_child(ui)
	await process_frame

	ui.set("_batch_csv_path", "C:/factory/input/scrubbots_2000_prompts.csv")
	ui.call("_refresh_batch_csv_button")
	_check(batch_button.text == "CSV: scrubbots_2000_prompts.csv", "selected CSV name was not shown after a screen refresh")
	_check(batch_button.tooltip_text == "C:/factory/input/scrubbots_2000_prompts.csv", "selected CSV path tooltip was not restored")

	ui.set("_batch_csv_path", "")
	ui.call("_refresh_batch_csv_button")
	_check(batch_button.text == "CSV file…", "empty selection did not restore the picker caption")
	_check(batch_button.tooltip_text.is_empty(), "empty selection retained a stale CSV tooltip")

	ui.free()
	await process_frame
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for message in _errors:
		push_error(message)
	quit(1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)
