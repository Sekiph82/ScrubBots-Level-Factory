extends SceneTree

const Analyzer = preload("res://scripts/difficulty/level_difficulty_analyzer_v1.gd")

func _initialize() -> void:
	var vector := {
		"W": 0.245925159801821,
		"C": 0.611507793811217,
		"A": 0.713455265535767,
		"U": 0.314177286356822,
		"B": 0.498039215686275,
		"R": 0.33571558906664,
		"S": 0.580441390530011,
	}
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		var parsed: Variant = JSON.parse_string(args[0])
		if not parsed is Dictionary:
			push_error("Optional stored official vector argument must be a JSON dictionary.")
			quit(2)
			return
		vector = parsed
	var first: Dictionary = Analyzer.profile(vector)
	var second: Dictionary = Analyzer.profile(vector)
	if first != second or not first.has("dominant") or not first.has("scores") or not first.has("runnerUp"):
		push_error("Pinned Difficulty V1 profile computation was not repeatable or complete.")
		quit(1)
		return
	print("R09-R02-R04-R01 pinned official profile: " + JSON.stringify(first))
	print("R09-R02-R04-R01 profile derivation focused suite: PASS (pinned static function, stored official vector, repeated exact output; no solver)")
	quit(0)
