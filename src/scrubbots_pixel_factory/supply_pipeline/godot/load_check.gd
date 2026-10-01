extends SceneTree
## Loads an exported level + supply plan with the game's own LevelLoader/SupplyPlanLoader.
##   godot --headless --path <ScrubBots> -s <this> -- <level.json> <supply_plan.json>
const LevelLoader = preload("res://scripts/data/level_loader.gd")
const SupplyPlanLoader = preload("res://scripts/gameplay/supply/supply_plan_loader.gd")
func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var lr = LevelLoader.load_from_path(args[0])
	if lr.level_data == null:
		print("LOAD_FAIL level: %s" % str(lr.errors))
		quit(1)
		return
	var r := SupplyPlanLoader.load_engine(args[1], lr.level_data)
	print("LOAD_OK" if r["ok"] else "LOAD_FAIL supply: %s" % r["error"])
	quit(0 if r["ok"] else 1)


