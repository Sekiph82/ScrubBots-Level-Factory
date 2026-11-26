from pathlib import Path

p = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\level_factory\scripts\factory_studio_exact_ui.gd")
s = p.read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new, 1)


# Owner 2026-11-24: the three tabs sit exactly over the Visual Review Canvas (389..1193),
# Settings at the far right over the Details panel (right edge 1518), same height as the tabs.
rep('''	_place_control("PixelArtTab", Rect2(365, 22, 255, 72), _show_screen.bind("PIXEL ART"))
	_place_control("LevelFactoryTab", Rect2(633, 22, 270, 72), _show_screen.bind("LEVEL FACTORY"))
	_place_control("ReleasePoolTab", Rect2(918, 22, 270, 72), _show_screen.bind("RELEASE POOL"))
	_place_control("SettingsGear", Rect2(1320, 15, 55, 60), _open_settings)
''', '''	# Owner 2026-11-24: tabs span exactly the Visual Review Canvas (389..1193, 12 px gaps);
	# Settings sits at the far right over the Details panel, on the tabs' row.
	_place_control("PixelArtTab", Rect2(389, 22, 260, 72), _show_screen.bind("PIXEL ART"))
	_place_control("LevelFactoryTab", Rect2(661, 22, 260, 72), _show_screen.bind("LEVEL FACTORY"))
	_place_control("ReleasePoolTab", Rect2(933, 22, 260, 72), _show_screen.bind("RELEASE POOL"))
	_place_control("SettingsGear", Rect2(1398, 22, 120, 72), _open_settings)
''')

# Owner 2026-11-24: the "-" button sits as close to ZoomSlider as "+" does (4 px).
rep('''	_place_control("ZoomOut", Rect2(650, 124, 34, 34), _adjust_zoom.bind(-1.0))''',
    '''	_place_control("ZoomOut", Rect2(697, 124, 34, 34), _adjust_zoom.bind(-1.0))''')

# Header tabs and Settings follow the centre/right panel zones instead of the plain window
# scale, so they stay aligned with the canvas and the Details panel at every window size.
rep('''			if position.y < 100.0:
				position.x *= scale_x
				item_scale = scale_x
			elif position.x < 380.0:''', '''			var header_zoned := control.name in ["PixelArtTab", "LevelFactoryTab", "ReleasePoolTab", "SettingsGear"]
			if position.y < 100.0 and not header_zoned:
				position.x *= scale_x
				item_scale = scale_x
			elif position.x < 380.0:''')

# Owner 2026-11-24: the two-line Size caption widened its button past Single/Prompt.
rep('''	var size_button := get_node_or_null("GenerationSize") as Button
	if size_button != null:
		size_button.text = _size_caption()
''', '''	var size_button := get_node_or_null("GenerationSize") as Button
	if size_button != null:
		size_button.text = _size_caption()
		# Keep the same width as Single/Prompt: the caption must not grow the button.
		size_button.clip_text = true
		size_button.add_theme_font_size_override("font_size", 11)
''')
p.write_text(s, encoding="utf-8")
print("applied")
