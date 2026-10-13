# R19 — Seasoning in cups: per-dish cup plan, station re-size, cup hardware, staging, timing

Date: 2026-10-13. This follows the user decision in `DECISIONS.md` (last entry):

> "我还是觉得直接放锅上不靠谱啊，不能用容器装好然后拿起来这种吗。或者是每道菜提前准备好料汁之类的。我给你的视频里是怎么做的"

That decision supersedes option (d), "dose directly at the wok".

The rule implemented here:
- During prep, the automatic station doses every seasoning, weighed, into containers in a dry place away from the wok.
- The arm stages the containers at the heat zone and pours each one at its moment.
- The 4-compartment pour drum takes the stir-fry bursts.
- Real ingredients are used: real white sugar, real 八角/桂皮, and 十三香.
- Nobody doses by hand. The person only restocks bulk containers (an assumption, still to confirm).

**Files**
- New: `sim/r10/claude/r19seas_cups.py` → `results/r19seas/cups.json`.
- The script holds:
  - every addition moment of the 3 meals, with its container, dose and evidence;
  - the move and time model;
  - the parts table.
- Every quoted phrase was checked by the script against `homestyle_meals.json` and the session transcripts `home3/v1-3.txt`: 0 missing.
- No existing file was changed. No sim was run. No web search was needed: all prices come from the existing research files.

**Tags**

| Tag | Meaning |
|---|---|
| **seen** | Visible in the 2 s frames (`home3/sheet_v*_*.jpg`). |
| **stated** | He says it (transcript). |
| **est.** | My estimate. Every gram figure is est. unless he says a spoon count, and even then the grams are est. |
| **[1688] / [r14] / [r19]** | Price from `r19_seasoning_sizing.md`, `r14_storage_market.md` or `r19_system_cost.md`. All prices are **unconfirmed**. |

---

## 0. Bottom line

1. **He works exactly this way himself (seen).**
   - Every addition is staged beside the wok in a small bowl, plate or spoon before the stir-fry:
     - ginger on a plate;
     - dried chili and 花椒 together on one plate;
     - garlic, red pepper and dried chili in one bowl;
     - 蒜苗 and 红椒 on a plate.
   - Each dish's liquids are premixed in a bowl:
     - the 蚝油 sauce, the 调味水 and the 鱿鱼 sauce;
     - the 白灼汁 and 丝瓜 sauce bowls;
     - for 红烧肉, even the 糖色 and the wine and soy (poured from small bowls, seen [v2 1:18, 1:26]).
   - The cup plan is therefore a faithful copy of his own mise en place.
2. **Containers per meal (seasoning-bearing / including the aromatics cups), as he does it:**
   - A **10 / 12**, B **15 / 20**, C **12 / 16**;
   - plus 1 / 0 / 2 doses straight into a prep vessel (stew cups, marinade, 上浆).
   - Four taste-neutral merges (est.) save 1–3 containers per meal (§2).
3. **Arm moves for seasoning, per meal A / B / C (model):**

   | Plan | Moves A / B / C | Time A / B / C (s) |
   |---|---|---|
   | **Recommended: P2**, a caddy per dish group, plus drums in the servo rim holder for bursts | **24 / 35 / 34** | **164 / 257 / 228** |
   | P2, including the aromatics cups | 29 / 39 / 36 | 193 / 281 / 240 |
   | Cups only (same accounting as R19) | 32 / 46 / 40 | — |
   | R19 cups only | 33 / 45 / 42 | — |
   | R14 today (with the drum) | 18 / 27 / 24 | — |
   | Option (d) | 12 / 3 / 6 | — |

   - The cup rule costs moves, as expected.
   - The drums cut the cup pours made **while stirring** from 6–8 to 1–3 per meal. Those pours are the ones that make the spatula stop.
4. **Station (re-sized, dry, ¥4.9–16.2k; ¥5.5–18.0k with 3 spare channels; unconfirmed):**
   - 9 pumped liquids, each bottle on a load cell: oil, water, 生抽, 老抽, 蚝油, 蒸鱼豉油, 料酒, 陈醋, 白醋. These are the only liquids in the 15 dishes.
   - 3 sealed dry dosers: real salt, real white sugar, potato starch.
   - 2 whole-spice portioners: 干辣椒段, 花椒.
   - A spice tray for arm picks: 八角, 桂皮, whole chili.
   - 2 shaker-tappers: 十三香, 胡椒粉.
   - 2 squeeze bottles: 豆瓣, 糖桂花.
   - A weigh bucket for all dry doses.
   - A caddy XY indexer, so the station fills the cups without the arm.

   For comparison: option (a) ¥7.3–17.6k, (b) ¥3.4–10.0k (+0.3–0.8k), (d) ¥4.5–12.5k.
5. **Cups:**
   - Two sizes, S ≈ 100 ml and L ≈ 300 ml (est.).
   - Material: 304 stainless.
   - Each cup has a side lug carrying **the same keyed 30 mm block as the spatula, lid, carrier, spider and faucet lever**. The cooking finger set therefore takes the cups, with no finger change.
   - Cups ride in 2×3 stainless wire caddies that double as dishwasher baskets.
   - Per meal: 9 / 13 / 10 cups, 3 / 4 / 3 caddies and 1 / 2 / 3 drums.
6. **Staging candidates to check in the sim** (§6):
   - **T1:** back-counter strip behind the plating spots;
   - **T2:** a caddy on the cart;
   - **T3:** a narrow rack between plating spot 1 and the cooker.

   The **drum's servo rim holder** is still unplaced since R15/R17; P2 depends on it.

---

## 1. What the videos show (the basis of the plan)

| Meal / dish | His containers (seen unless marked) | Notes |
|---|---|---|
| A 干锅土豆 | Fried potato on a plate. Ginger slices [2:14], then 豆瓣 on a spoon [2:16]. **Dried-chili segments + 花椒 on one plate [2:18].** 生抽 (stated) + a pinch of 十三香 [2:26]. 蒜苗 + 红椒 on a plate [2:28]. | Five additions in ~16 s of edited video. A burst. |
| A 蚝油西兰花 | **Bowl: half a bowl of water + 1 spoon 蚝油, stirred** [2:39–2:44]. Oil [2:46], broccoli, salt [2:50], sauce [2:52], lid. | ASR "我用勾芡的" likely means "不用勾芡的"; the sauce has no starch. |
| A 桂花糖芋头 | 糖桂花酱 drizzled from a porcelain spoon [3:12–3:14]. | Off-wok, onto the plate. |
| A 蒜蓉蒸丝瓜 | **Bowl of garlic + red chili [3:34]**; hot oil from the wok poured in [3:36]; 蒸鱼豉油 (squeeze bottle) and 陈醋 [3:38–3:40]; the sauce spooned over [3:42]. | The bowl is the sauce vessel. |
| A 蛤蜊排骨盅 | "就一点盐就行了" per stew cup (stated [0:12]). | Dosed into the dish's own cups. |
| B 红烧肉 | Blanch: scallion, ginger, wine into cold water [0:38–0:40]. Braise: oil [1:01]; **葱姜 on one spoon [1:14]; 八角, 桂皮 and whole dried chili on another [1:16]; 糖色 poured from a small bowl [1:18]** (made beforehand: "我前面的作品有发布过了"); one small spoon of salt [1:24]; **dark liquid poured from a bowl [1:26]** (料酒 + 生抽 per the speech); boiling water [1:28]. | Even this braise is staged in containers. |
| B 清蒸鲈鱼 + 白灼汁 | Pour off the fish water; 蒸鱼豉油; 三丝 (soaked in water) [2:16–2:20]. **Bowl: garlic, scallion white, dried chili [2:24]**. One hot-oil heating serves both, "剩下的油淋这边" [2:26–2:30]. Then 陈醋 [2:32] and sugar on a spoon [2:34]. | |
| B 番茄炒蛋 | Oil, eggs set and out. Oil, 葱段 [3:32]; tomato; salt + sugar (stated [3:35]); **a small metal bowl of water [3:36]**; lid 30 s; eggs back; 葱叶 [3:46]. | |
| B 白灼 / 汤 | Wok water + oil [3:52–3:54] + 1 spoon salt (stated). Soup: salt, then celery [4:20–4:24]. | |
| C 芋头蒸排骨 | Marinade into the rib bowl [0:19–0:28]: 老抽, 蚝油, pepper from **a shaker**, starch, 1 spoon oil; mixed by gloved hand. White vinegar on the taro "against itching" [0:30]. End: 红椒末 + 葱花, 1 spoon hot oil [3:56–3:58]. | The vinegar is for his hands. A robot does not need it (est.). |
| C 酸辣土豆丝 | Blanch: oil, salt [2:08–2:10]. Oil [2:18]; **garlic + red pepper + dried chili from one bowl [2:22]**; shreds; **调味水 in a bowl: water + salt, 白醋, 陈醋, 生抽 [2:26–2:34]**; scallion [2:36]. | |
| C 青瓜肉片汤 | 上浆: salt + "多一点" potato starch (stated [2:00]). Ginger, cucumber, pork, salt [2:46–2:56]. **Celery + white pepper (shaker) in the serving bowl [3:04].** | In the robot plan the soup stays in the stew pot; the user serves. |
| C 青椒炒鱿鱼 | Oil; 葱姜蒜 [3:14]; green pepper; 料酒 [3:16]; squid. **Bowl: water + 生抽 + 蚝油 + salt + potato starch [3:20–3:24]**, poured [3:26]. | The starch must be re-stirred. |
| C 清炒荷兰豆 | Oil [3:36]; garlic; peas [3:38]; salt + a little water [3:40]. | |

---

## 2. Cup plan per dish and per meal

**Container types:**
- **L:** 料汁 cup (his premix).
- **S:** single-moment cup (what he adds straight from a bottle or spoon at one moment).
- **D:** dry-spice cup.
- **A:** aromatics cup (prep output; may carry a dose on top). **A\*** is a sauce bowl at the plating spot.
- **V:** dosed at the station straight into the prep vessel (no cup).
- **→drum:** goes into a drum compartment in plan P2.
- **(m)**: taste-neutral merge candidate (est.).

**Cup size:**
- S ≈ 100 ml brimful: content ≤ 50 ml.
- L ≈ 300 ml brimful: ≤ 160 ml of liquid or ≤ 220 ml of loose aromatics.

**Drum compartment limits** (est.; liquids never simulated): ≤ 35 ml of liquid or ≤ 100 ml of bulk.

### Meal A — caddies A1 (干锅), A2 (西兰花), A3 (芋头 + 丝瓜)

| # | Dish, t | Goes in (dose) | Container | Size | P2 | Evidence |
|---|---|---|---|---|---|---|
| A01 | 蛤蜊排骨盅 [0:12] | salt ≈ 0.5 g × 4 stew cups ("一点盐") | V | — | — | stated |
| A02 | 西兰花 soak [1:34] | salt "一勺" ≈ 5 g into the soak water | V, optional (a wash step; not counted) | — | — | stated |
| A03 | 干锅 | oil ≈ 10 g (the robot fries in the fryer, so the wok needs its own) | S | S | cup | est. |
| A04 | 干锅 [2:14–2:16] | ginger ≈ 5 g + 豆瓣 ≈ 10 g (one heaped spoon) | A + paste | S | →drum (paste residue: bench) | seen |
| A05 | 干锅 [2:18] | 干辣椒段 ≈ 8 g + 花椒 ≈ 3 g | D | S | →drum | seen |
| A06 | 干锅 [2:23–2:26] | 生抽 ≈ 10 g + 十三香 ≈ 0.5 g | S | S | →drum | stated + seen |
| A07 | 干锅 [2:28] | 蒜苗 + 红椒 ≈ 60 g (~170 ml loose) | A | L | cup (too big for a compartment) | seen |
| A08 | 西兰花 [2:46] | oil ≈ 15 g | S | S | cup | seen |
| A09 | 西兰花 [2:50] | salt ≈ 2 g | S (m → A10) | S | cup | seen |
| A10 | 西兰花 [2:39–2:52] | water "半碗" ≈ 120 ml + 蚝油 "一勺" ≈ 12 g | L | L | cup | seen + stated |
| A11 | 芋头 [3:12] | 糖桂花酱 ≈ 20 g, over the taro plate | S | S | cup | seen |
| A12 | 丝瓜 [3:33] | oil ≈ 30 g, heated in the wok and tipped over the bowl | S | S | cup | seen |
| A13 | 丝瓜 [3:34] | garlic + red chili ≈ 25 g; receives the hot oil, then is poured over the luffa | A\* | L | cup | seen |
| A14 | 丝瓜 [3:38–3:40] | 蒸鱼豉油 ≈ 20 g + 陈醋 ≈ 8 g, into the bowl | L | S | cup | seen |

### Meal B — caddies B1 (红烧肉), B2 (鱼 + 白灼汁), B3 (番茄炒蛋), B4 (白灼 blanch + soup end)

| # | Dish, t | Goes in (dose) | Container | Size | P2 | Evidence |
|---|---|---|---|---|---|---|
| B03 | 红烧肉 blanch [0:38–0:40] | scallion, ginger ≈ 20 g + 料酒 ≈ 15 g | A + wine | L | cup | stated + seen |
| B04 | 红烧肉 [1:01] | oil ≈ 15 g | S | S | cup | stated |
| B05 | 红烧肉 [1:14] | 葱姜 ≈ 20 g | A (m → B06) | L | →drum | seen |
| B06 | 红烧肉 [1:16] | 八角 1–2 pieces, 桂皮 1 piece, 3–4 whole chilies (≈ 7 g) | D | S | →drum | seen |
| B07 | 红烧肉 [1:18] | real white sugar ≈ 20 g for the 糖色 | S | S | →drum | seen (his 糖色 was ready-made) |
| B08 | 红烧肉 [1:23–1:26] | 料酒 ≈ 20 g + salt "一勺" ≈ 4 g + 生抽 "少许" ≈ 8 g | L | S | →drum (28 ml) | stated + seen |
| B09 | 鲈鱼 [2:18] | 蒸鱼豉油 ≈ 25 g, over the fish | S | S | cup | seen |
| B10 | 鲈鱼 [2:20] | 三丝 ≈ 20 g (soaked: perforated cup) | A | L | cup | seen |
| B11 | 鲈鱼 + 白灼汁 [2:21–2:28] | oil ≈ 60 g, one heating for both | S | L | cup | seen |
| B12 | 白灼汁 [2:24] | garlic + scallion white ≈ 25 g + 干辣椒段 ≈ 3 g; receives the hot oil | A\* | L | cup | seen |
| B13 | 白灼汁 [2:30–2:34] | 蒸鱼豉油 ≈ 25 g + 陈醋 ≈ 10 g + sugar ≈ 5 g | L | S | cup | seen |
| B14 | 番茄炒蛋 [3:26] | oil ≈ 20 g | S | S | cup | stated |
| B15 | 番茄炒蛋 [3:32] | oil ≈ 10 g | S | S | cup | seen |
| B16 | 番茄炒蛋 [3:32] | 葱段 ≈ 10 g | A | S | →drum | seen |
| B17 | 番茄炒蛋 [3:35] | salt ≈ 3 g + sugar ≈ 6 g | S (m → B18) | S | →drum | stated |
| B18 | 番茄炒蛋 [3:36] | water ≈ 60 ml | S | L | cup (over the drum limit) | seen |
| B19 | 番茄炒蛋 [3:46] | 葱叶 ≈ 8 g | A | S | →drum | seen |
| B20 | 白灼 [3:52–3:54] | oil ≈ 10 g + salt "一勺" ≈ 6 g into the water | S | S | cup | stated + seen |
| B01 | 汤 [4:20] | salt ≈ 6 g into the pot | S (m → B02) | S | cup | stated |
| B02 | 汤 [4:24] | celery ≈ 15 g | A | S | cup | seen |

### Meal C — caddies C1 (土豆丝), C2 (汤 + 鱿鱼), C3 (荷兰豆 + 排骨 end)

| # | Dish, t | Goes in (dose) | Container | Size | P2 | Evidence |
|---|---|---|---|---|---|---|
| C01 | 芋头蒸排骨 [0:19–0:28] | 生抽 ≈ 10, 老抽 ≈ 4, 蚝油 ≈ 10, pepper ≈ 0.5, starch "两勺" ≈ 15, oil "一勺" ≈ 10 g, into the rib bowl | V | — | — | seen + stated |
| C02 | 芋头 [0:30] | white vinegar against itchy hands | skipped (not needed by a robot, est.) | — | — | stated |
| C05 | 土豆丝 blanch [2:08] | oil ≈ 5 g + salt ≈ 3 g | S | S | cup | stated + seen |
| C06 | 土豆丝 [2:18] | oil ≈ 20 g | S | S | cup | seen |
| C07 | 土豆丝 [2:22] | garlic + red pepper ≈ 25 g + 干辣椒段 ≈ 3 g | A | L | →drum | seen |
| C08 | 土豆丝 [2:26–2:34] | 调味水: water ≈ 40 + salt ≈ 3 + 白醋 ≈ 10 + 陈醋 ≈ 10 + 生抽 ≈ 5 | L | L | cup (65 ml) | seen |
| C09 | 土豆丝 [2:36] | scallion ≈ 8 g | A | S | →drum | seen |
| C10 | 肉片汤 上浆 [2:00] | salt ≈ 1.5 g + potato starch "多一点" ≈ 12 g, into the pork bowl | V | — | — | stated |
| C11 | 肉片汤 [2:56] | salt ≈ 3 g into the stew pot | S | S | cup | seen |
| C12 | 肉片汤 [3:04] | celery ≈ 10 g + white pepper ≈ 0.3 g | A + shaker | S | cup | seen |
| C13 | 鱿鱼 [3:12] | oil ≈ 15 g | S | S | cup | seen |
| C14 | 鱿鱼 [3:14] | 葱姜蒜 ≈ 15 g | A | S | →drum | seen |
| C15 | 鱿鱼 [3:16] | 料酒 ≈ 10 g | S | S | →drum | seen |
| C16 | 鱿鱼 [3:20–3:26] | water ≈ 60 + 生抽 ≈ 10 + 蚝油 ≈ 10 + salt ≈ 1.5 + starch ≈ 5 g | L (re-stir) | L | cup (80 ml) | seen |
| C17 | 荷兰豆 [3:36] | oil ≈ 15 g | S | S | cup | seen |
| C18 | 荷兰豆 [3:38] | garlic ≈ 8 g | A | S | →drum | seen |
| C19 | 荷兰豆 [3:40] | salt ≈ 2.5 g + water ≈ 30 ml | S | S | →drum (32 ml) | stated + seen |
| C03 | 排骨 end [3:56] | 红椒末 + 葱花 ≈ 10 g, over the plate | A | S | cup | seen |
| C04 | 排骨 end [3:58] | oil "一勺" ≈ 15 g, heated and poured over | S | S | cup | seen |

**Merges (est., taste-neutral):**
- A09 salt into the A10 sauce;
- B05 葱姜 with the B06 spices;
- B17 salt and sugar into the B18 water;
- B01 salt onto the B02 celery.

Each saves a container. A08-type oil cups cannot merge: the oil must heat first.

---

## 3. Counts and arm moves per meal

**Plans**
- **P0, cups only:** stage, pick-pour, return; 3 moves per cup. This is R19's accounting.
- **P1, caddy + cups:**
  - one 2×3 caddy per dish group goes from the station to the staging spot in 1 move and is cleared in 1 move;
  - each cup costs 2 moves: pick-pour, and return to its slot.
- **P2, P1 plus drums in the servo rim holder:**
  - loading the drum and unloading it are 2 moves;
  - the servo pours while the arm keeps stirring.
- **P2h:** P2 with the drum held by the arm, 3 moves. The spatula is parked while the arm rolls the drum.

In every plan:
- a V dose is 2 moves (the bowl to the station and back);
- a sauce bowl takes +1 move (to the plating spot for the hot-oil tip).

**Counts** (`r19seas_cups.py`). Moves are seasoning-bearing / including the aromatics cups.

| Meal | Variant | Containers | V | Caddies | Drums (compartments) | Cups left in P2 (S/L) | P0 | P1 | **P2** | P2h | In-stir cup pours P1 → P2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | as he does | 10 / 12 | 1 | 3 | 1 (3) | 9 (6/3) | 32 / 39 | 28 / 33 | **24 / 29** | 25 / 30 | 6 → 3 |
| A | merged | 9 / 11 | 1 | 3 | 1 (3) | 8 (5/3) | 29 / 36 | 26 / 31 | **22 / 27** | 23 / 28 | 5 → 2 |
| B | as he does | 15 / 20 | 0 | 4 | 2 (7) | 13 (8/5) | 46 / 61 | 39 / 49 | **35 / 39** | 37 / 41 | 8 → 1 |
| B | merged | 14 / 17 | 0 | 4 | 2 (5) | 12 (7/5) | 43 / 52 | 37 / 43 | **35 / 37** | 37 / 39 | 6 → 1 |
| C | as he does = merged | 12 / 16 | 2 | 3 | 3 (6) | 10 (8/2) | 40 / 52 | 34 / 42 | **34 / 36** | 37 / 39 | 8 → 2 |

**Comparison:** seasoning moves per meal A / B / C, with seconds.

| Design | Moves | Time (s) | Status |
|---|---|---|---|
| R14 today: station cups + drum, user weekly kit | 18 / 27 / 24 | 132 / 198 / 176 | The kit breaks "nobody doses by hand". Fewer events: no caddies or returns modelled. |
| R19 cups only | 33 / 45 / 42 | 242 / 330 / 308 | **This study's P0 reproduces it: 32 / 46 / 40**. |
| R19 (b) right-sized, cups kept | 22 / 27 / 24 | 162 / 198 / 176 | Same accounting as R14. |
| R19 (d) direct at the wok | 12 / 3 / 6 | 88 / 22 / 42 | Rejected by the user. |
| **This plan, P2** | **24 / 35 / 34** (merged 22 / 35 / 34) | **164 / 257 / 228** | Recommended. |
| This plan, P1 (no drum) | 28 / 39 / 34 | 180 / 265 / 204 | |

**What the table says**
- **The cup rule costs moves.** 24–35 per meal is close to R14 and 2–10× option (d). The containers themselves are what the user asked for.
- **The drum's real value is stirring continuity, not arm time.**
  - It cuts cup pours made while stirring (the spatula must be put down) from 6–8 to 1–3 per meal.
  - Meal C's three 2-compartment drums save nothing in arm time over P1: 228 s vs 204 s seasoning-only, or 268 s vs 280 s with the aromatics.
  - Use a drum where 3–4 burst items go in together: 干锅, 红烧肉, 番茄炒蛋. For 2-item bursts it only buys stirring continuity.
- **The pours still made while stirring in P2** are the large 料汁 cups and the B18 water (60–130 ml), all over the 35 ml drum liquid limit (est.).

**Further cuts (est., by hand from the counts)**
- **One caddy per meal** (2 × 6 slots, about 0.17 × 0.50 m) instead of one per dish group: −4 / −6 / −4 moves, −40 / −60 / −40 s. It needs a larger staging spot.
- **Pour and drop:** the empty cup goes into a used basket beside the pour path instead of back to its slot: −1 move per cup (−9 / −13 / −10). Time stays about the same.
- **The 料汁 cups into the drum,** if a bench test shows that ≥ 90 ml of liquid stays in a ±25° compartment during carrying and loading: in-stir pours fall to 0–1 per meal.

**Prep-phase arm work at the station** (during prep, not in the cooking timeline):
- A: one 十三香 shake and 2 squeezes (豆瓣, 糖桂花), about 45 s;
- B: about 6 picks for 八角, 桂皮 and whole chili, about 36 s;
- C: 2 pepper shakes, about 30 s;
- plus moving the V bowls.

The shakes drop out with the motorised tappers (§4).

---

## 4. Station re-sized: dosing into cups in a dry place

### 4.1 Where

| Site | Where (sim frame) | For | Against |
|---|---|---|---|
| **S2 (proposed): the freed rice/flour port** under upper cabinet 0. The rice module was dropped on 10-13 ("电饭煲我可以做"). | x −1.05…−0.95, y 0.30–0.46, outlets z 1.31–1.35. The caddy dock under it at z ≈ 1.10–1.15. Cart station H_SINK (−0.68) or H_SPAT (−1.48). | Dry: 1.8 m from the wok, 1.0+ m from the steamer pot. Reach was ✓ in R14. Prep happens here, so the V doses (marinade, 上浆, stew-cup salt) are dosed straight into the prep bowls. | 0.6 m from the faucet: steam bursts during the hot-wok rinse. Must clear the spatula rest (−1.15, 0.30) and the leaf bowl (−1.23…−1.03, 0.36–0.56): **sim check**. Each caddy is carried 1.2 m: corridor H_SINK–H_WOK, 4.0 s checked with the empty tuck. |
| S1: the R14 seasoning port | x 0.50–0.60, under upper cabinet 1 next to the hood | No carry. Cup reach ✓ at y 0.30, z 1.05–1.20 (R14). | 0.23–0.33 m from the wok axis: steam and oil mist on the outlets. The outlet stopped the wok tip of a tall bucket in R16. Dosing only before any heat is on. |

**Dosing time:** 15 / 23 / 30 single seasoning doses for meals A / B / C at about 10 s each, so ≈ 3–5 min of station run time per meal (est.), in parallel with prep.
- The first caddy (干锅 / 红烧肉 / 土豆丝) must be ready 10–20 min into the meal (meal16 timelines).

### 4.2 How each class is dosed

| Class | Items (HS) | Mechanism | Accuracy / notes |
|---|---|---|---|
| **Pumped liquids** | oil, water, 生抽, 老抽, 蚝油, 蒸鱼豉油, 料酒, 陈醋, 白醋 (9) | Stepper peristaltic pumps (KCM-class ≥ 100–600 ml/min for oil, water, wine, vinegar) to one outlet manifold over the fill point, with suck-back after each dose. **Each bottle stands on its own load cell (loss-in-weight):** closed loop on every dose, fast feed then trickle, low-stock alarm. | HX711 noise ≈ 0.05–0.2 g rms (est. [r14]) against ±0.5 g needed. |
| Water specifically | | A 2 L jug the person fills before cooking, as already decided for the kettle; or the arm fills it at the running tap once per meal (≈ 30 s est.). | 60–130 ml per meal goes into 料汁 and water cups. |
| 蚝油 specifically | | Wide-bore tube; a small bottle. | Refrigerate after opening, 8 weeks [r19]. The Peltier box is optional. |
| **Real salt, real white sugar** | salt 4–19 g, sugar 0–31 g per meal | Sealed hopper with an agitator. **Cell wheel** (rotary pocket, 0.2–0.3 g pockets, est.): the wheel is also the seal when idle. An agitated **auger** is the alternative and is more tolerant of slightly sticky product. | All dry doses fall into a **weigh bucket** on a 1 kg cell (≈ 0.01–0.05 g rms, est. [r14]), are verified, then dumped into the cup. Salt ±0.2 g is reachable. |
| Why not a vibratory feeder | | The tray is open and sticks in humidity. Fine trickle (0.4–2 g in 7–15 s [r14]), but not chosen for Singapore humidity (est.). | |
| **Dryness** (all dry items) | | The station is a closed cabinet section: shutters or cell wheels closed when idle, a silica-gel cartridge in a perforated side compartment, an RH sensor, and only 1–2 weeks' stock per hopper. Countermeasures from [r14]. Dosing happens in prep, never at the wok. | Critical RH: NaCl 75 %, sucrose 86 %, against 70–90 % ambient [r14]. |
| **Potato starch** | 5 g in C16's 料汁; 15 g / 12 g into the marinade and 上浆 bowls | **Dry**, from an agitated auger (a cohesive fine powder bridges in cell pockets). Dry is needed anyway for the marinade and 上浆. | **Not a slurry channel**: a slurry settles in the cup just the same, needs a daily make-up and flushing (it keeps ≤ 2 days [r19]). Settled starch in the waiting 料汁 cup is handled at staging: a captive stir bar on a magnetic pad, or an arm swirl of 2–3 s before the pour. **Bench test:** does settled potato starch re-suspend? |
| **Whole spices, small** | 干辣椒段 3–8 g, 花椒 3 g | Two agitated cell-wheel portioners into the weigh bucket. A pet-feeder mechanism is the donor (¥138 [1688]; not food-certified). | He uses segments in 干锅, 白灼汁 and 土豆丝 (seen). |
| **Whole spices, pieces** | 八角 1–2 pieces, 桂皮 1 piece, 3–4 whole dried chilies | The arm picks them from a small open tray, located by a station camera, into the D cup during prep (≈ 6 picks, ≈ 36 s). | As decided 10-13. Whole chilies do not flow in a portioner (they tangle [r14]). |
| **十三香, 胡椒粉** | 0.3–0.5 g | **Shaker jars, as he uses for pepper (seen [v3 0:24, 3:04]).** A motorised tapper (an inverted sieve-lid jar on a vibration motor) shakes into the weigh bucket until the weight is reached. Fallback: the arm shakes the jar (≈ 15 s). | 0.3 g against ±0.2 g is marginal (est.). Keep in the dry enclosure. |
| **Pastes** | 豆瓣 10 g, 糖桂花酱 20 g | Squeeze bottles; the arm squeezes over the cup on the scale (as in R19), ≈ 15 s each in prep. | Residue in the cup: bench test. |

### 4.3 Parts (CNY, all unconfirmed; `PARTS` in the script)

| Part | Qty | Unit | Basis | Subtotal |
|---|---|---|---|---|
| Peristaltic pumps: oil, water, 生抽, 老抽, 蚝油, 蒸鱼豉油, 料酒, 陈醋, 白醋 | 9 | 133–442 | [1688] via r19 | 1,197–3,978 |
| Drivers, food-grade tube, bottles, fittings | 9 | 50–100 | est. (r19) | 450–900 |
| Outlet manifold, suck-back, drip tray | 1 | 100–300 | est. | 100–300 |
| Loss-in-weight cell + HX711 per bottle or jug | 9 | 10–55 | [1688] via r19 | 90–495 |
| Sealed dry dosers: salt, sugar, starch (cell wheel at the low end, auger at the high end) | 3 | 150–1,000 | est. (r14 / r19) | 450–3,000 |
| Whole-spice portioners: 干辣椒段, 花椒 | 2 | 150–400 | est.; donor [1688] | 300–800 |
| Spice tray + station colour camera | 1 | 120–550 | est. (r19 row 11) | 120–550 |
| Motorised shaker-tappers: 十三香, 胡椒粉 | 2 | 50–150 | est. | 100–300 |
| Squeeze bottles (2 HS + 3 WG) | 5 | 5–20 | est. (r19) | 25–100 |
| Weigh bucket: 1 kg cell, HX711, dump servo | 1 | 60–300 | [1688] + est. | 60–300 |
| Caddy XY indexer under the outlets | 1 | 300–600 | est., no source | 300–600 |
| Drum fill cradle | 1 | 100–200 | est. | 100–200 |
| Dry enclosure: seals, shutters, desiccant, RH sensor | 1 | 100–400 | est. (r14) | 100–400 |
| Magnetic stir pad at staging + captive bars | 1 | 50–150 | [1688] ¥43–95 + est. | 50–150 |
| Controller and enclosure | 1 | 500–1,500 | est. (r19) | 500–1,500 |
| Cups, 304 stainless with keyed lug: 12 S + 12 L | 24 | 15–40 | est., unpriced | 360–960 |
| Wire caddies 2×3 | 6 | 30–80 | est., unpriced | 180–480 |
| 3 pour drums + servo rim holder | 1 | 400–1,200 | r19 row 28 (est.), widened | 400–1,200 |
| **Total, 9 channels** | | | | **≈ ¥4.9–16.2k** |
| + 3 spare channels for Wang Gang (香油, 红油, …) | 3 | 193–597 | as above | +0.6–1.8k → **¥5.5–18.0k** |
| + chilled 蚝油 box (Peltier) | 1 | 150–400 | est. (r19 e4) | +0.15–0.4k |

**Against the earlier options** (parts only):
- (a) R14 ¥7.3–17.6k;
- (b) right-sized ¥3.4–10.0k plus 0.3–0.8k of add-ons;
- (d) direct ¥4.5–12.5k (11 channels) or ¥5.1–14.3k (14 channels).

**Where the money goes**
- The wide range comes mostly from the dry dosers (a cell wheel against an auger) and the pumps.
- The container hardware itself (cups, caddies, drums) adds ¥0.9–2.6k.
- The XY indexer (¥0.3–0.6k) saves about 2 prep-phase arm moves per cup.

**Dropped against R14:**
- the 2 paste syringes;
- the 4th auger (鸡精 is not used in HS);
- the 花椒 vibratory feeder;
- the 66 % syrup and the brine: salt and sugar are now dry and real;
- the user's weekly kit.

---

## 5. Cup hardware

- **Two sizes (est.):**
  - **S ≈ 100 ml brimful** (about Ø65 × 45 mm): dry doses, single liquids ≤ 50 ml, small aromatics.
  - **L ≈ 300 ml brimful** (about Ø85 × 70 mm): 料汁 up to 160 ml (A10 is 132 ml), loose aromatics up to 220 ml (A07 is ≈ 170 ml), the 60 ml oil and water cups, and the two **sauce bowls that take very hot oil (≈ 180–200 °C, est.)** (A13, B12).
- **Material:** deep-drawn **304 stainless** with a rolled pour lip. It is dishwasher-safe and survives the hot oil. PP would soften. Printed PETG is not dishwasher-safe (est.).
- **Grasp:**
  - A short horizontal lug at the rim carries **the keyed 30 mm block used on every cooking tool**: spatula, lid tab, dish carrier, spider, faucet lever (R16/R17). The finger set on the PGC-140-50 during cooking therefore takes cups too: no finger swap. R13: P1 covers 5–45 mm and P2 covers 29–69 mm. The 30 mm block sits in the set used by the R16/R17 tool chains.
  - **Pour** by a wrist roll about the lug axis, with the lip 90° from the lug. R14: "a wrist roll with a horizontal approach works", 23/72 orientations over the wok; never chained.
  - **Load:** a full L cup is ≈ 0.3 kg at ≈ 60 mm from the jaws, ≈ 0.2 N·m against the 7 N·m PGC limit. The block is form-fit, so it does not rely on wet friction.
  - **Block material:** PPSU or POM, or stainless (dishwasher-safe).
- **Special cups:**
  - a perforated insert for the soaked 三丝 (B10);
  - a captive PTFE stir bar under a wire bail for starch 料汁 (C16) (est.);
  - viscous items (豆瓣, 糖桂花, 蚝油 sauce) need a residue bench test: roll to 150–180°, hold 2–3 s, a small shake.
- **Nesting:** the tapered bodies nest with the lugs aligned. The pitch is about the block height, 24–30 mm, so 12 S cups stack to ≈ 0.4 m.
- **Caddy:**
  - a 2×3 stainless wire rack, about 0.17 × 0.25 m;
  - a centre bail to the same keyed block, as on the R16 dish carrier: carried level, no jaw moment;
  - taken from the front at 30–45°, because it sits under a cabinet;
  - it is also the dishwasher basket.
- **Drum:** the R14 Ø80 × 140 mm, 4 compartments. It needs a wider slot for aromatics (R14: 60°) and must be dishwasher-washable (open ends or a removable cap).
- **Per meal, P2 as he does:**

  | Meal | Cups | Caddies | Drums |
  |---|---|---|---|
  | A | 9 (6 S + 3 L) | 3 | 1 |
  | B | 13 (8 S + 5 L) | 4 | 2 |
  | C | 10 (8 S + 2 L) | 3 | 3 |

  - **A set of 24 cups (12 S + 12 L), 6 caddies and 3 drums** covers one meal with spares.
  - Two robot meals between washes need a second set of cups (+¥360–960).
- **Washing (proposed, to confirm):**
  - Used cups go back into their caddy.
  - After the meal the caddies go into the dishwasher with the plates, as baskets.
  - Clean caddies go back on the station dock, about 1 min for the person (est.).
  - The station itself never has a wet shared vessel: liquids go straight into the cups, and the weigh bucket sees only dry items.
  - **Alternative:** the arm rinses cups under the running tap, like the wok. 蚝油 and oil residue need detergent, and one-arm scrubbing is still open (R17).
  - **Unknown:** whether the user has a dishwasher.

---

## 6. Staging: where the filled cups wait (to check in the sim afterwards)

Sim frame:
- counter top z 0.85, front edge y 0;
- wok axis (0.83, 0.17);
- plating spots at x 0.43 and 0.17, y 0.13, r 0.12;
- cooker x 0.63–1.03;
- hood x 0.69–1.46, y ≥ 0.15, z ≥ 1.25;
- R14 port box x 0.50–0.60, y 0.30–0.46, z 1.31–1.35;
- spatula rest (−1.15, 0.30);
- spider (1.52, 0.36), lid rack x 1.70–1.80;
- hub cart stations −1.48 / −0.68 / 0.172 / 1.093;
- stir station x 0.55.

| Candidate | Place | For | Against / what to check |
|---|---|---|---|
| **T1: back-counter strip behind the plating spots** | A 2×3 caddy (or 2×6 per meal) at x 0.18–0.45, y 0.30–0.47, on the counter; cup tops ≈ 0.93 m. About 0.4–0.6 m from the wok axis, outside the hood and the plume rule. Cart station H_WOK (0.172). | Free counter, near the wok, one cart station for staging and pouring. | (1) The wok tipped over plating spots 1 and 2: does its body pass over y 0.20–0.35 clear of the cups? (2) Reach low and back: R14 found cups at y 0.50, z 0.99 unreachable (forearm against the base plate), so keep y ≤ 0.45 and check. (3) A dish waiting on a plating spot lies between the arm and the caddy. (4) R18 failed a spatula rest at (0.10–0.20, 0.50) on the upper-cabinet door, but that was a tall 50° handle; cups are low. |
| **T2: caddy on the cart** | A bracket beside the arm base (not in front of it) at ≈ 0.90–0.95 m. | Travels with the arm: no counter space, no carry to a spot, always at the current station. | R14: the arm reaches heights of about 0.35–1.25 m beside the cart, but not low and close in front of itself. A new body on the cart means re-checking the hub tuck and the 22 hub edges. Slosh at cart accelerations of 0.15–0.5 m/s² (the L cups are filled ≤ 55 %). |
| **T3: narrow rack left of the cooker** | A single file of 4–6 cups at x 0.57–0.62, y 0.27–0.50, between plating spot 1 (x ≤ 0.55) and the cooker (x ≥ 0.63). 0.25–0.33 m from the wok axis. | Shortest pour path. The cart stays at its stir station. | Steam and splatter on open cups for the minutes they wait. The wok grip block at (0.595, 0.17, 1.025) is 0.10 m in front of it: check the wok pick-up and tip. The R14 port box above blocks a top approach, so lugs must face the robot and cups behind the front one are hard to reach. |
| **Drum: servo rim holder** (R15/R17, swing-away) | Right rim (1.005, 0.17, 1.105), swung away except while stirring. | Pours bursts while the arm stirs. | **Still unplaced.** R15: the arm cannot load it at the right rim; behind the wok it can, with zero reserve, not checked against the strokes. If no spot is found, use P2h (arm-held drum): +1–3 moves and +10–30 s per meal, with the spatula parked in the wok (unchecked). |
| Rejected | Counter end (spider, lid rack: "too crowded", R16/R17); backsplash rail at z 0.99, y 0.50 (✗, R14); under the hood (✗); right of the cooker (the arm folds onto its base, R15). | | |

**Soup cups** (B01/B02, C11/C12) go to the electric stew pot. Its position is not in the sim yet.

---

## 7. Timing

**Time constants** (`T` in the script):

| Step | Time | Basis |
|---|---|---|
| Pick-pour | 8 s | meal16 ARM `pour`. An **assumption**: `arm18.json` has no `cup` or `pour` entry, and both stay at the 8 s defaults, never checked. |
| Cup return | 4 s | est. |
| Caddy in | 12 s | the hub corridor H_SINK–H_WOK, 4.0 s (checked, empty tuck), plus 2 spurs (est.) |
| Caddy out | 8 s | est. |
| Drum in / out | 12 / 8 s | est. |
| Arm-held drum roll | 10 s | est. |
| Vessel dose | 14 s | R19 |
| Cups-only cycle | 22 s | R14 rates |

**Seasoning arm time per meal, cooking phase:**

| Plan | A | B | C | Notes |
|---|---|---|---|---|
| **P2** | **164 s** | **257 s** | **228 s** | 193 / 281 / 240 s including the aromatics cups |
| P1 | 180 | 265 | 204 | |
| P2h | 174 | 277 | 258 | |
| P0 | 220 | 335 | 264 | |
| R14 today (for scale) | 132 | 198 | 176 | |
| Option (d) (for scale) | 88 | 22 | 42 | |

**Effect on the meal model (est.; `meal16.py` not re-run):**
- meal16 already charges some of these moments as 8 s pours. It has no staging, return, caddy or drum handling.
- **P2 adds about 2.5–3 min of arm time per meal** to the R18 arm-busy figures: A 13.9, B 28.4, C 17.9 min with the user loading the rice.
- Total meal time should rise less, because caddy staging can sit in the steaming and braising waits.
- The stir-fry quality gain: in-stir cup pours fall from 6–8 to 1–3 per meal. R15's spatula-idle estimate falls from 36 % to 13 % median.

---

## 8. Open questions and checks

**For the user**
1. **Restocking:** confirm that the person only restocks bulk containers:
   - 9 bottles, including the water jug each meal unless the arm fills it at the tap;
   - 3 dry hoppers (salt, sugar, starch) and the desiccant;
   - 2 spice hoppers and the spice tray;
   - 2 shaker jars and 2 squeeze bottles.

   Bulk use per meal (est.): oil 55–115 g, salt 4–19 g, sugar 0–31 g, starch 0–32 g, 生抽 8–25 g, 蒸鱼豉油 0–50 g, 料酒 0–35 g.
2. **Washing:** is there a dishwasher? The caddies are designed as dishwasher baskets. Otherwise, who washes about 10–13 cups and 1–3 drums per meal?
3. **Water:** may the station draw from a jug the person fills, or should the arm fill it at the running tap?
4. **Merges:** may salt go into the sauce, salt and sugar into the tomato water, and the spices together with 葱姜? This saves 1–3 containers per meal.
5. **糖色:** he pours ready-made 糖色 (seen). Should the robot caramelise the sugar in the pork fat, or make a 糖色 batch in advance?

**Sim (before building)**
- Staging candidates T1–T3.
- The drum holder's place.
- The station dock at S2 against the spatula rest and the prep bowls.
- The caddy carry H_SINK → H_WOK.
- The cup pour chained from the staging spot.

**Bench**
- Residue of viscous items in the cups (豆瓣, 糖桂花, 蚝油 sauce).
- Re-suspension of settled potato starch.
- Liquid capacity of a drum compartment during carrying.
- Salt and sugar caking in a cell wheel at 70–90 % RH.
- Shaker-tapper accuracy at 0.3–0.5 g.
- Salt left in an open cup near the wok for 10–40 min.

**Not designed**
- Mixing the marinade and the 上浆 (he does it by gloved hand). This is a prep motion.

---

## 9. Method notes

- Moments come from the frames, every 2 s, and the transcripts.
  - Boundaries follow his separate containers or actions.
  - The video is edited, so the gaps are short and are not real stir times.
- **All grams are est.**
  - He gives spoons only ("一勺", "两勺", "半碗") or "a little".
  - Spoon sizes are read from the frames (est.).
- The move model is bookkeeping, not checked paths, as in R19.
  - It reproduces R19's cup-only count, which is a consistency check, not a validation.
- No prices were read today. Every price is copied from the research files above, or est.
