extends RefCounted

## Test-only path map for the headless Studio suites.
##
## Since 2026-11-08 mutable Factory data lives under <checkout>/data
## (data/output, data/Level Factory/...), not res://output. The suites create
## and delete these folders, so they must run inside an isolated checkout copy
## (tests/conftest.py build_isolated_factory_copy). Against the owner's real
## Desktop checkout every path below is redirected to a throw-away user:// folder
## and an error is reported, so a suite can never delete owner data.

const DATA_PATHS := preload("res://scripts/factory_data_paths.gd")
const OWNER_CHECKOUT_NAME := "Scrubbots - Pixel Art Generator"


static func isolated_root() -> String:
	var root := DATA_PATHS.repository_root()
	var profile := OS.get_environment("USERPROFILE")
	var owner := profile.path_join("Desktop").path_join(OWNER_CHECKOUT_NAME).simplify_path()
	if root.is_empty() or root.replace(char(92), "/").to_lower() == owner.replace(char(92), "/").to_lower():
		push_error("Studio integration suites must run in an isolated checkout copy, not the owner's data: " + root)
		return ""
	return root


static func data(relative: String) -> String:
	var root := isolated_root()
	if root.is_empty():
		return OS.get_user_data_dir().path_join("refused-owner-data").path_join(relative)
	return root.path_join("data").path_join(relative).simplify_path()


static func output(relative: String = "") -> String:
	return data("output" if relative.is_empty() else "output/" + relative)


static func workspace(relative: String = "") -> String:
	return data("Level Factory/Workspace" if relative.is_empty() else "Level Factory/Workspace/" + relative)


static func extensions(relative: String = "") -> String:
	return workspace("Studio Extensions" if relative.is_empty() else "Studio Extensions/" + relative)


static func imported(relative: String = "") -> String:
	return data("Level Factory/Imported" if relative.is_empty() else "Level Factory/Imported/" + relative)
