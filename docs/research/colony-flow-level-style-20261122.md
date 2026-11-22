# Colony Flow level picture style (research, 2026-11-22)

## Özet (sahip için)

- Kaynak: `https://colony-flow.com/all-level-walkthrough`. Sayfa engellemeden açıldı; 824 seviye görseli listeliyor (1–610 arası tam, 611–1317 arası seyrek). 824 görselin küçük kopyası geçici olarak (repo dışında) kontakt sayfalarına dizildi; **824'ünün hepsi gözle tek tek incelendi** (ilk turda 576, sahibin isteğiyle ikinci turda kalan 248). Görsellerin hiçbiri repoya kopyalanmadı; geçici küçük kopyalar yalnızca Claude oturumunun geçici klasöründe (`%TEMP%\claude\...\scratchpad\cf`) duruyor, otomatik silme izni verilmedi.
- Ortak stil: her piksel **kabartmalı, parlak bir oyuncak blok / boncuk** gibi görünüyor (her hücrede küçük üst ışık ve alt gölge). Resim kareye yakın, tek bir **ortalanmış, kalın koyu konturlu sevimli nesne** (ilk ~150 seviye) ya da arka planı tamamen dolu **sahne** (sonraki seviyeler).
- Renk: canlı, doygun, şeker renkleri (kırmızı, turuncu, sarı, pembe, turkuaz, çimen yeşili, mor). Erken seviyelerde nesne başına ~5–10 renk, düz dolgu + 1 açık + 1 koyu ton; geç seviyelerde 15–25+ renk ve degrade.
- Konular: meyve ve tatlılar, sevimli hayvanlar (kedi, köpek, hamster, tavşan, kurbağa, tilki, penguen, ahtapot), çiçek ve bitkiler, evler, oyuncak/eşya (TV, oyun kolu, kamera, kupa), doğa ikonları (güneş, ay, yıldız, gökkuşağı, kalp), bayram temaları ve desen/mandalalar. Çok sayıda seviye lisanslı karakter, futbol arması, bayrak ve ünlü portresi içeriyor — bunlar **bilinçli olarak dışarıda bırakıldı**.
- **Seviye başına prompt (güncelleme 2026-11-22, sahip isteği):** `data/input/colony_flow_level_prompts.csv` — her listelenen seviye için bir satır, ID = `CF_LVL_<seviye no>`; erken/geç ayrımı yok, sahneler dahil **hepsi arka plansız** (sahne seviyelerinde ana nesne alındı: ör. dalga, deniz feneri, şelale, ada rozeti). 824 seviyeden 7'si birebir aynı resim (310=307, 350=265, 370=364, 427=157, 430=287, 587=570, 614=608) olduğu için **817 satır**. Lisanslı karakter, kulüp arması ve ünlüler kopyalanmadı; aynı seviyeye **genel, özgün bir karşılık** yazıldı (ör. "caped masked hero", "striped football shield badge", "footballer in red kit"). Bayraklar renk/desenle tarif edildi.
- Önceki genel dosya `data/input/colony_flow_style_prompts.csv` (72 satır, `CF_ATLAS_0001..0072`) korunuyor; konular aynı, sadece ortak kuyruk cümlesi palete göre güncellendi.
- **Palet ve gölge:** Studio PixelLab'e sabit 16 renkli ScrubBots Palette V3'ü (`palette`), `max_colors=12` ve `no_background=True` olarak gönderiyor; PixelLab yeni ton üretemez. Eski "one highlight and one shadow tone" ifadesi palette olmayan açık/koyu tonlar istiyordu (paletteki pembe ve yeşilin açık/koyu karşılığı yok), bu yüzden kaldırıldı. Yeni kuyruk, gölgeyi yalnızca paletteki komşu renge geçerek yapmayı söylüyor: beyaz→açık gri→koyu gri; soluk sarı→sarı→turuncu→turuncu kırmızı→kahverengi; açık mavi→mavi→koyu mavi→periwinkle; açık turkuaz→yeşil; pembe tek ton. Kontur siyah (C16).

## Method

- Read the walkthrough page (HTTP 200, no login). It lists 824 level cards; each card is a "Colony Flow Level N Screenshot" image hosted on `gl.imgbear.xyz`. Group sub-pages `/group/100` … `/group/1400` and per-level pages `/level/N` exist; the walkthrough page already embeds every listed card, so no further pagination was needed.
- 256 px thumbnails of all 824 cards were fetched through the site's own image endpoint into a temporary scratchpad (outside the repo), tiled into 18 contact sheets of 48, and all 18 sheets (824 levels) were inspected visually (12 in the first pass, the remaining 6 in a second pass). Exact-duplicate pictures were found by hashing the thumbnails. The temporary thumbnails stay in the session scratchpad (outside the repo); deleting them was not permitted in this session.
- Per-level records are summarised by category below (level numbers are examples, not exhaustive).

## Common visual style

| Aspect | Observation |
|---|---|
| Rendering | Every pixel is drawn as a raised, glossy square block (toy-brick / fuse-bead look) with a light top-left edge and darker bottom edge. Empty cells show as a faint white grid. |
| Canvas | Square or near-square (some portrait/landscape), roughly 25x25 to 40x40 cells. |
| Composition (early, ~1–150) | One centred subject filling 70–90 % of the canvas; white/empty background or a single flat colour block behind it. |
| Composition (later, ~150+) | Full-bleed scenes: sky, sea, sunsets, landscapes, interiors, portraits; background always filled. |
| Outline | Early: thick 1-cell dark outline (deep purple-brown/near black) around the subject and major parts. Later: outline often dropped, edges defined by colour contrast. |
| Shading | Flat fills with one highlight and one shadow tone per colour; occasional white sparkle pixels. Later scenes use multi-step gradients and dithering. |
| Colour count | Early: ~5–10 colours per picture. Later: ~15–25+. |
| Colour mood | Bright, saturated "candy" palette: cherry red, orange, lemon yellow, bubblegum pink, sky/turquoise blue, grass green, violet, warm brown, cream. Very little grey. |
| Faces | Kawaii: big round black eyes with white highlight, pink blush cheeks, tiny mouth. |
| Text | Rare (LOVE, Mom, PROTEIN!, LEVEL UP). |

## Subject categories seen (examples)

| Category | Example levels | Typical look |
|---|---|---|
| Fruit | 3, 14, 24, 54, 100, 195, 210, 256, 1280 | Single fruit, outlined, white bg, 5–8 colours |
| Desserts / sweets | 11, 17, 20, 33, 55, 149, 214, 483, 697 | Cupcakes, sundaes, cakes, popsicles, candy |
| Food / drink | 8, 13, 18, 22, 23, 158, 235, 266 | Burger, sushi, ramen bowl, mugs, bubble tea |
| Cats | 12, 16, 25, 106, 107, 150, 245, 253, 362 | Sitting/sleeping cats, cat faces, cats in hoods |
| Dogs | 28, 44, 71, 113, 157, 385, 396, 427 | Puppy faces, small fluffy dogs |
| Small mammals | 29, 37, 40, 64, 118, 247, 286, 351, 488 | Hamsters, bunnies, capybaras, mice |
| Wild animals | 15, 132, 135, 197, 198, 204, 265, 395 | Raccoon, giraffe, lion/tiger faces, fox, red panda |
| Birds | 7, 53, 80, 102, 109, 153, 154, 344, 800, 1197 | Penguin, rooster, duck, parrot, toucan, owl |
| Sea life | 164, 236, 397, 505, 513, 515, 516, 727 | Octopus, jellyfish, pufferfish, starfish, dolphin, turtle |
| Bugs | 137, 168, 222, 225, 420, 497, 1154 | Bee, butterfly, moth, snail, beehive |
| Frogs / reptiles | 56, 70, 159, 167, 343, 486 | Frogs, small dragon, snake |
| Flowers / plants | 9, 39, 75, 161, 213, 230, 1224, 1257 | Single blooms, potted plants, sunflowers, lotus |
| Mushrooms / houses | 4, 10, 34, 138, 215, 219, 1240, 1244 | Mushroom house, castle, cottage, gingerbread house |
| Objects / toys | 26, 61, 99, 127, 347, 482, 740 | TV, laptop, game controller, trophy, camera |
| Vehicles | 27, 103, 105, 268, 382, 417 | Van, scooter, UFO, plane, rocket, school bus |
| Sky / symbols | 1, 2, 6, 248, 249, 301, 412 | Star, heart, rainbow, moon, magic wand |
| Holidays | 190, 192, 201, 202, 231, 419 | Christmas tree, snowman, gingerbread, gift box |
| Patterns / mandalas | 5, 36, 41, 57, 82, 156, 179, 216, 1250 | Symmetric tiles, op-art, kaleidoscope |
| Scenes | 30, 47, 51, 59, 124, 221, 501, 502, 506, 1134 | Beach, wave, sunset, meadow, lighthouse |
| Excluded (licensed / real-world) | e.g. 19, 43, 50, 58, 263, 305–336, 369 | Franchise characters, club crests, flags, celebrities — not used as prompt material |

## Mapping to our PixelLab Pro 4x4 run

- Our levels are 56x56 sprites on a transparent background with at most 12 colours. The Studio sends PixelLab `create_image_pro` the fixed 16-colour ScrubBots Palette V3 (`palette`), `max_colors=12` and `no_background=True` (`src/scrubbots_pixel_factory/studio_extensions.py`, `generate_pixellab_pro_4x4_atlas_mcp`).
- Palette V3: C01 Orange Red, C02 Orange, C03 Yellow, C04 Green, C05 Light Teal, C06 Light Blue, C07 Blue, C08 Dark Blue, C09 Periwinkle, C10 Pink, C11 Brown, C12 Pale Yellow, C13 Light Gray, C14 Dark Gray, C15 White, C16 Black. Pink and green have no lighter/darker same-hue partner, so "one highlight and one shadow tone" cannot be met literally. The prompt tail now names the in-palette ramps to shade along (white–light gray–dark gray; pale yellow–yellow–orange–orange red–brown; light blue–blue–dark blue–periwinkle; light teal–green; pink flat) and forbids new tints, gradients and dithering; outline is black (C16).
- `data/input/colony_flow_level_prompts.csv`: one row per listed level (`CF_LVL_<level>`), 817 rows (824 minus 7 exact-duplicate pictures), early and late levels alike, every subject on a transparent background (scene levels reduced to their main object). Licensed characters, club crests and celebrities are replaced by a generic original subject of the same kind; flags are described by colours/pattern.
- `data/input/colony_flow_style_prompts.csv`: the earlier 72 generic rows (`CF_ATLAS_0001..0072`), same subjects, palette-aware tail.
- The glossy per-pixel block bevel is a rendering effect of their game board, not of the source art; our game board renders its own tiles, so prompts do not ask for it.
