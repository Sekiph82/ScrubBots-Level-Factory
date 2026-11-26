// ScrubBots difficulty trial: 8 sprites, 54x54 + 1px outline = 56x56, Palette V3 only.
pal({ a: "#FF4500", b: "#FFA800", c: "#FFD635", d: "#00CC78", e: "#00CCC0", f: "#51E9F4", g: "#3690EA", h: "#2450A4",
      i: "#6A5CFF", j: "#FF3881", k: "#9C6926", l: "#FFF8B8", m: "#D4D7D9", n: "#515252", o: "#FFFFFF", p: "#000000" })

// ---------- EASY: few colours, big flat areas, everything reachable from the edge ----------
sprite("easy_orange", { w: 54, h: 54, outline: "p" },
  circ(27, 30, 22, "b"), circ(20, 22, 5, "c"),
  poly([26, 8, 30, 2, 33, 9], "k"), ellipse(36, 8, 8, 4, "d"))

sprite("easy_mushroom", { w: 54, h: 54, outline: "p" },
  ellipse(27, 20, 25, 17, "a"), rect(18, 30, 18, 22, "l"),
  circ(16, 16, 4, "o"), circ(32, 11, 4, "o"), circ(39, 22, 3, "o"))

// ---------- MEDIUM: 5-6 colours, a few nested parts ----------
sprite("medium_house", { w: 54, h: 54, outline: "p" },
  rect(6, 24, 42, 29, "l"), poly([2, 25, 27, 2, 52, 25], "a"),
  rect(23, 36, 9, 17, "k"), rect(10, 30, 9, 9, "g"), rect(35, 30, 9, 9, "g"),
  rect(14, 30, 1, 9, "o"), rect(39, 30, 1, 9, "o"), rect(38, 6, 6, 12, "n"))

sprite("medium_fish", { w: 54, h: 54, outline: "p" },
  ellipse(24, 27, 21, 16, "e"), poly([42, 27, 53, 12, 53, 42], "g"),
  rect(14, 12, 4, 31, "c"), rect(24, 11, 4, 33, "c"), rect(34, 13, 4, 28, "c"),
  circ(10, 23, 3, "o"), px(10, 23, "p"))

// ---------- HARD: 8-9 colours, concentric bands and patterned body ----------
sprite("hard_shield", { w: 54, h: 54, outline: "p" },
  poly([4, 2, 50, 2, 50, 28, 27, 53, 4, 28], "h"),
  poly([8, 6, 46, 6, 46, 27, 27, 48, 8, 27], "c"),
  poly([12, 10, 42, 10, 42, 26, 27, 43, 12, 26], "a"),
  poly([16, 14, 38, 14, 38, 25, 27, 38, 16, 25], "o"),
  poly([20, 18, 34, 18, 34, 24, 27, 33, 20, 24], "d"),
  circ(27, 23, 4, "i"), circ(27, 23, 2, "j"), rect(24, 2, 6, 46, "k"))

sprite("hard_owl", { w: 54, h: 54, outline: "p" }, (c) => {
  c.ellipse(27, 30, 23, 23, "k")
  c.poly([6, 2, 16, 12, 6, 14], "k"); c.poly([48, 2, 38, 12, 48, 14], "k")
  c.ellipse(27, 36, 15, 15, "l")
  for (let y = 26; y < 50; y += 5) for (let x = 15; x < 40; x += 6) c.poly([x, y, x + 3, y + 3, x + 6, y], (x + y) % 2 ? "b" : "a")
  c.circ(18, 18, 7, "o"); c.circ(36, 18, 7, "o"); c.circ(18, 18, 4, "g"); c.circ(36, 18, 4, "g")
  c.circ(18, 18, 2, "p"); c.circ(36, 18, 2, "p"); c.poly([25, 23, 29, 23, 27, 28], "c")
})

// ---------- VERY_HARD: 11-12 colours, many small interlocking regions, deep nesting ----------
sprite("vh_mandala", { w: 54, h: 54, outline: "p" }, (c) => {
  const rings = "hgfedcbajikimn".split("")
  for (let r = 26, i = 0; r > 1; r -= 2, i++) c.circ(27, 27, r, rings[i % rings.length])
  for (let k = 0; k < 12; k++) {
    const t = (k / 12) * Math.PI * 2, x = 27 + Math.cos(t) * 18, y = 27 + Math.sin(t) * 18
    c.circ(Math.round(x), Math.round(y), 4, "abcdefghij"[k % 10]); c.circ(Math.round(x), Math.round(y), 2, "lo"[k % 2])
  }
  for (let k = 0; k < 8; k++) {
    const t = (k / 8) * Math.PI * 2 + 0.2, x = 27 + Math.cos(t) * 10, y = 27 + Math.sin(t) * 10
    c.circ(Math.round(x), Math.round(y), 2, "jihgfedc"[k])
  }
})

sprite("vh_stained_glass", { w: 54, h: 54, outline: "p" }, (c) => {
  const keys = "abcdefghijkl"
  let s = 7
  const rnd = () => (s = (s * 1103515245 + 12345) % 2147483648) / 2147483648
  for (let y = 0; y < 54; y += 6) for (let x = 0; x < 54; x += 6) {
    const k1 = keys[Math.floor(rnd() * 12)], k2 = keys[Math.floor(rnd() * 12)]
    c.rect(x, y, 6, 6, k1)
    if (rnd() < 0.5) c.poly([x, y, x + 6, y, x, y + 6], k2); else c.poly([x + 6, y, x + 6, y + 6, x, y + 6], k2)
    c.px(x, y, "n")
  }
})
