extends SceneTree

## R09-R02 Pipeline Activity panel: placement, structure and screen scope.
##
## Rewritten 2026-11-12 for the current owner ruling (R09-R02-R01, master UI
## V03): the panel sits under Run Pipeline at x=27, y=412, width 334 and fills
## the remaining left-workspace height; it shows a title, state chip, source
## row, phase row and a scrollable newest-first event list (no single text
## label any more), and it is visible only on LEVEL FACTORY.

const MAIN_SCENE := "res://scenes/factory_studio.tscn"
const PASS_MARKER := "R09-R02 Studio activity UI test: PASS"

var _errors: Array[String] = []


func _init() -> void:
	call_deferred("_run")


func _check(condition: bool, message: String) -> void:
	if not condition:
		_errors.append(message)


func _run() -> void:
	var packed := load(MAIN_SCENE) as PackedScene
	if packed == null:
		push_error("R09-R02 activity test: Factory Studio scene did not load")
		quit(1)
		return
	var instance := packed.instantiate()
	root.add_child(instance)
	await process_frame
	var studio := instance.get_node_or_null("MasterUI") as Control
	if studio == null:
		push_error("R09-R02 activity test: MasterUI is missing")
		instance.free()
		quit(1)
		return
	studio.size = Vector2(1536, 1024)
	studio.call("_apply_responsive_layout")

	var panel := studio.get_node_or_null("PipelineActivityPanel") as Panel
	_check(panel != null, "PipelineActivityPanel is missing")
	if panel == null:
		_finish(instance)
		return
	for child in ["PipelineActivityTitle", "PipelineActivityStateChip/PipelineActivityState", "PipelineActivitySource",
			"PipelineActivityPhase", "PipelineActivityScroll/PipelineActivityRows", "PauseAfterCurrent", "StopAfterCurrent"]:
		_check(panel.get_node_or_null(child) != null, "activity panel child %s is missing" % child)
	var title := panel.get_node_or_null("PipelineActivityTitle") as Label
	_check(title != null and title.text == "PIPELINE ACTIVITY", "activity title is not PIPELINE ACTIVITY")

	# Responsive scaling may move edges by a fraction of a pixel.
	# Owner layout 2026-11-13: the panel starts 12 px under the status counter (y=281).
	_check(panel.position.distance_to(Vector2(27, 281)) <= 1.0 and absf(panel.size.x - 334.0) <= 1.0,
		"activity panel left edge/top/width moved from Rect2(27,281,334,…): %s" % [Rect2(panel.position, panel.size)])
	var left_panel := studio.get_node_or_null("RuntimeLeftPanel") as Control
	_check(left_panel != null and absf(panel.position.y + panel.size.y - (left_panel.position.y + left_panel.size.y)) <= 1.0,
		"activity panel does not fill the remaining left-workspace height")
	var run_button := studio.get_node_or_null("RunLevelPipeline") as Button
	_check(run_button != null and run_button.position.y + run_button.size.y <= panel.position.y,
		"Run Pipeline is not directly above the activity panel")

	_check(not panel.is_visible_in_tree(), "activity panel leaked into the initial PIXEL ART screen")
	studio.call("_show_screen", "LEVEL FACTORY")
	await process_frame
	_check(panel.is_visible_in_tree(), "activity panel did not appear inside LEVEL FACTORY")
	# The startup Final-source restore is read-only; only a pipeline worker counts.
	_check(studio.get("_pipeline_thread") == null, "opening LEVEL FACTORY automatically executed the pipeline")
	for screen in ["PIXEL ART", "RELEASE POOL"]:
		studio.call("_show_screen", screen)
		await process_frame
		_check(not panel.is_visible_in_tree(), "activity panel leaked into %s" % screen)
	_finish(instance)


func _finish(instance: Node) -> void:
	instance.free()
	if _errors.is_empty():
		print(PASS_MARKER)
		quit(0)
		return
	for error in _errors:
		push_error("R09-R02 activity test: " + error)
	quit(1)
