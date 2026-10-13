# R19 prep audit: what the reference meals need, what is covered, what to check next (2026-10-13)

**Why.** The user decided: "备菜是最重要你要做的之一了，肯定不是人来做". Washing, peeling and cutting stay with the robot (DECISIONS 2026-10-13; option O7 rejected). Until now, `meal16.py` does not count prep ("Knife work is NOT scheduled here"), and R19 estimated it at 10–20 min per meal. This audit:
- lists what the reference meals A/B/C need;
- says what is designed and what is checked;
- checks the R11/R12 prep chains against today's R18 kitchen;
- proposes options for the gaps;
- frames prep as R19 movement sets, with a verification plan.

**Labels**
- **[checked]**: a closed chain that passed the unchanged checker (and the physics gate where stated) in some round.
- **[screen]**: run in this round with the fast checker (`full=False`, as `r18spatreplay.py`) or the R19 voxel screen. A screen is not a full check.
- **[bench]**: R13 floating-gripper physics only, with no kitchen path.
- **[designed]**: the product and the robot interface are described in DECISIONS or the market research, but nothing is simulated.
- **[missing]**: no design at all.
- **[est]**: my estimate, with its basis stated.
- **[C]**: from an e-commerce or search snippet, not verified.

**New files** (no existing file was changed):
- `r19prep_replay.py`: replays `chain_SD` and `chain_WD` in today's kitchen.
- `r19prep_screen.py`: screens candidate appliance spots against the stored swept volumes.
- `r19prep_spotreplay.py`: a screen-level ground-truth replay for one spot.
- `r19prep_demand.py`: the demand table and the arm-time estimate.
- Results in `results/r19/prep/`: `replay_{SD,WD}_{r18,orig}.json`, `screen.json`, `spot_*.json`, `prep_demand.json`.

Every run was under 2 minutes. Python: `C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe`, run from `sim/r10/claude`.

---

## 1. Summary

1. **Demand.** The three meals have 38 prep items (A 12, B 14, C 12; family of 4, masses [est]).
   - About 32 washes, 13 peels, 23 produce cuts, 6 mince/chop jobs, 4 meat cuts plus squid scoring, 5 eggs, 2 marinades, 7 soaks, 2–3 scalds.
   - Plus portioning: 16 rib pieces and 12 clams go into 4 stew cups (meal A).
   - The R11–R13 work covered the root/tomato/greens cutting path, and the grasps of about 40 foods. The meals also need these, which have **no design**:
     - meat slicing and cubing;
     - mincing aromatics;
     - eggs;
     - marinating;
     - soaking and scalding;
     - broccoli florets;
     - peeling luffa, bamboo shoot and garlic;
     - squid scoring and fine scallion shreds;
     - arranging food for steaming.
2. **What is actually checked in the sim for prep:** two single-piece chains, both in the **R11/R12 layout**:
   - carrot: tray → wash → cradle peel → slicer chute;
   - tomato: pad → rinse → lever 8-wedge press.
3. **Those chains are not valid in today's kitchen, for three reasons:**
   - **Washing:** both chains wash under the R07 wall spout at x −0.58. R17 removed that spout; the water now comes from the user's faucet at (−0.40, 0.37, 1.10).
   - **Carrot peel step:** replayed in today's kitchen [screen], the carrot chain's wrist-2 links pass through the **R18b spatula handle**. That is 423 of 7,431 states, all 216 states at the peeler, with up to 12 mm penetration. The peeler station itself overlaps the spatula on its rest by up to 94 mm (static).
   - **Slicer:** the counter-resident slicer spot (0.30, 0.13) is now **both plating spots** (77 mm overlap). Its output bowl overlaps plate 1 and the cooker.
   - The tomato chain hits no R14+ fixture [screen].
4. **The left counter front is a corridor for the cooking motions.**
   - A tool left at the R11 work spot (−1.00, front) is hit [screen] by:
     - the wok sink trip (both plating spots);
     - the faucet lever (60 mm penetration);
     - the spatula fetch;
     - 8 of the 13 flagged hub edges.
   - So every fetched prep tool must be stowed before each plating, dump or fill trip and each spatula fetch, or it must move.
   - A lever-base envelope at **(−1.62, front)** is hit by nothing [screen: 6 chains + 6 hub edges]. A 3-in-1 slicer at **(−1.00, back)** is also clear.
   - The reach to feed them is **not checked**. Under the upper cabinets, R14 found reach only up to z 1.05–1.12 at y 0.40–0.48.
   - (−1.62, front) also collides with the R14 fridge cold-box set-down spot (−1.70, 0.18).
5. **Arm time [est].**
   - Prep adds about **21–40 min of arm time per meal**: A 27–40, B 22–32, C 21–30. That is more than R19's 10–20 min, because of the cup portioning, sectioning presses, tool handling and finger swaps.
   - Packed into the arm's idle windows (rice by the user), it needs a **prep-first block of 5–17 min** before the meal clock starts.
   - Meals with prep: A ≈ 45–56, B ≈ 82–86, C ≈ 41–48 min (were 38.2 / 75.6 / 35.6).
6. **Options for the gaps (domestic market first).**
   - Counter-resident 850 W 切肉切菜一体机 for meat: ¥474–1,080 [C], ~21 kg.
   - A fetched 2 L bowl chopper (绞肉机 class) for garlic, ginger, chili, celery, 肉末, and for beating eggs: ~¥60–200 [C].
   - A lever egg cracker on a printed stand.
   - Lever-base plates for sections, halves, cubes and tofu grids.
   - A soak tub with a basket insert.
   - Fridge thawing via the R14 cold box (FSIS-approved methods).
   - Several items need either a **purchase-form decision by the user** or a recipe change: chopped ribs, cleaned fish and squid, florets, shelled bamboo shoots, peeled garlic.
7. **Movement sets.**
   - Prep needs about 20 set families on about 7 hubs. Two of the hubs exist already: H_SPAT (cart −1.48, the raw tray) and H_SINK (−0.68).
   - Reuse per 3 meals: lever press 45, piece placement 32, single-piece cycle 34, basket 18, finger swap 15, output transfer 14, tool fetch 9.
   - **Verify first:**
     - the layout fix;
     - wash-under-the-R17-faucet;
     - pick/carry/chute and lever in today's kitchen;
     - the basket family;
     - the tool drawer;
     - the finger swap.

---

## 2. Prep demand (task 1)

Source: `research/homestyle_meals.md/.json`, his own steps.
- **Shapes** are his where stated. **Sizes** are [est] typical.
- **Masses and piece counts** are [est] for his family of 4. He states only: 4 rib pieces + 3 clams per cup, 4 cups, 5 eggs, 400 g rice.
- Rice is now the user's (2026-10-13).
- Machine-readable: `results/r19/prep/prep_demand.json`.

### 2.1 Meal A: 干锅土豆, 桂花糖芋头, 蚝油西兰花, 蒜蓉蒸丝瓜, 蛤蜊排骨盅

| Ingredient | Dish | Mass [est] | His prep | Cut, size [est] |
|---|---|---|---|---|
| 排骨 rib pieces | cups | 320 g, 16 pc | 4 per cup | bone-in 段 (butcher) |
| 蛤蜊 clams | cups | 250 g, 12 pc | 3 per cup | whole; purge + scrub [typical, not stated] |
| 姜 ginger | cups, 干锅 | 30 g | 1 slice per cup | 片 2–3 mm |
| 芋头 taro | 桂花糖芋头 | 500 g, ~6 small | peeled; thick slices → strips → blocks; spaced on a plate | 块 ~2.5 cm |
| 土豆 potato | 干锅土豆 | 500 g, 3 | slices, deep-fried | 片 3–5 mm |
| 五花肉 pork belly | 干锅土豆 | 150 g | slices | 片 ~3 mm |
| 红椒 red pepper | 干锅土豆 | 100 g | pieces | 块/片 |
| 蒜苗 garlic sprouts | 干锅土豆 | 80 g | sections | 段 3–4 cm |
| 干辣椒, 花椒, 十三香 | 干锅土豆 | — | (seasoning cup kit, R14) | — |
| 西兰花 broccoli | 蚝油西兰花 | 400 g | florets cut small, soaked in salted water; stem peeled and sliced | 小朵; stem 片 |
| 胡萝卜 carrot | 西兰花 garnish | 30 g | slices | 片 |
| 丝瓜 luffa | 蒜蓉蒸丝瓜 | 500 g, 2 | peeled, segments, arranged on a plate | 段 ~3 cm |
| 蒜 garlic + 红辣椒 chili | 丝瓜 sauce | ~50 g | minced, hot oil over | 蒜蓉 / 碎 |

### 2.2 Meal B: 红烧肉, 番茄炒蛋, 白灼秋葵娃娃菜, 清蒸鲈鱼, 鲜笋排骨汤 (+ 白灼汁)

| Ingredient | Dish | Mass [est] | His prep | Cut, size [est] |
|---|---|---|---|---|
| 排骨 ribs | soup | 500 g | scalded with boiling water, soaked 5 min | 段 (butcher) |
| 鲜笋 bamboo shoot | soup | 400 g, 2 | halved, thick slices (sheath off) | 片 5–8 mm |
| 干贝 dried scallops | soup | 15 g | (rehydrate, not stated) | whole |
| 姜 ginger | soup, 红烧肉, fish | 40 g | slices | 片 |
| 芹菜 celery | soup | 30 g | chopped, added at the end | 粒/末 |
| 五花肉 pork belly | 红烧肉 | 600 g | blanched whole, skin scraped flat, cubes | 块 ~3 cm (cooked) |
| 葱 scallion | 红烧肉, fish, 番茄炒蛋, 白灼汁 | 60 g | 段; 葱花 (white/leaves apart); fine 葱丝; 葱白 | 段, 圈, 丝 1–2 mm |
| 鲈鱼 sea bass | 清蒸鲈鱼 | 600 g | split along the back, head pressed flat, on the plate with ginger/scallion | (stall) |
| 葱姜胡萝卜丝 | fish topping | 40 g | stacked and shredded, soaked | 丝 1–2 mm |
| 番茄 tomato | 番茄炒蛋 | 450 g, 3 | scalded, cross-cut, peeled, wedges | 瓣/块 |
| 鸡蛋 eggs | 番茄炒蛋 | 5 | beaten | — |
| 娃娃菜 baby cabbage | 白灼 | 400 g, 2 | (lengthwise pieces, not stated) | 条/瓣 [est] |
| 秋葵 okra | 白灼 | 150 g | whole | — |
| 蒜, 葱白, 干辣椒 | 白灼汁 | 30 g | in a bowl, hot oil over | 末 / 圈 |

### 2.3 Meal C: 芋头蒸排骨, 酸辣土豆丝, 青椒炒鱿鱼, 清炒荷兰豆, 青瓜肉片汤

| Ingredient | Dish | Mass [est] | His prep | Cut, size [est] |
|---|---|---|---|---|
| 排骨 ribs | 芋头蒸排骨 | 450 g | marinated: 生抽, 老抽, 蚝油, pepper, 2 spoons potato starch, 1 spoon oil | small 段 (butcher) |
| 芋头 taro | 芋头蒸排骨 | 300 g, ~4 | blocks as the plate bed | 块 ~2.5 cm |
| 红椒, 葱花 | 芋头蒸排骨 garnish | 20 g | chopped | 碎 / 葱花 |
| 鱿鱼 squid | 青椒炒鱿鱼 | 400 g | scored both ways (麦穗花刀), cut, scalded in a bowl | pieces |
| 青椒 green pepper | 青椒炒鱿鱼 | 150 g | pieces | 块 |
| 葱姜蒜 | squid, peas, 土豆丝 | 50 g | minced/sliced | 末/片 |
| 土豆 potato | 酸辣土豆丝 | 400 g, 2 | julienned by hand, soaked to wash off starch | 丝 ~2–3 mm |
| 红椒丝, 干辣椒 | 酸辣土豆丝 | 30 g | shreds | 丝 |
| 瘦肉 lean pork | 青瓜肉片汤 | 180 g | sliced; salt + plenty of potato starch (上浆) | 片 ~2 mm |
| 青瓜 cucumber | soup | 200 g | (slices) | 片 |
| 姜, 芹菜 | soup | 40 g | ginger slices; celery into the bowl | 片 / 末 |
| 荷兰豆 snow peas | 清炒荷兰豆 | 300 g | (wash; stringing typical, not shown) | whole |

### 2.4 Grouped into prep operations (A / B / C instances, masses [est])

| Operation | A | B | C | ~Mass A+B+C | Items |
|---|---|---|---|---|---|
| Wash: firm single items (held under the tap) | 5 | 4 | 6 | 3.3 kg | potato, taro, carrot, ginger, pepper, cucumber, tomato, bamboo, fish rinse |
| Wash: bulk / leafy / small (basket) | 6 | 6 | 5 | 2.3 kg | ribs, clams, garlic sprouts, broccoli, scallion, celery, okra, baby cabbage, chilies, snow peas, garlic |
| Peel: roots (abrasive or cradle) | 3 | 1 | 2 | 1.8 kg | potato, taro, carrot |
| Peel: other | 3 | 3 | 1 | 1.5 kg | luffa, broccoli stem, bamboo sheath, garlic cloves, pork skin scrape, (tomato skin), (snow pea strings) |
| Slice 片 (produce) | 3 | 2 | 2 | 1.5 kg | potato, ginger, carrot, broccoli stem, bamboo, cucumber |
| Shred 丝 | 0 | 3 | 2 | 0.5 kg | potato 丝, red pepper 丝, fine 葱/姜/胡萝卜丝 |
| Blocks / wedges 块, 瓣 | 2 | 2 | 2 | 1.8 kg | taro ×2, tomato, baby cabbage, peppers |
| Sections 段 / rings | 2 | 1 | 1 | 0.7 kg | garlic sprouts, luffa, scallion, celery |
| Mince / chop 末, 蓉 | 1 | 2 | 3 | 0.2 kg | garlic, ginger, chili, celery, scallion |
| Florets | 1 | 0 | 0 | 0.4 kg | broccoli |
| Meat slices / strips | 1 | 0 | 2 | 0.7 kg | pork belly, lean pork, squid |
| Cooked meat cubes | 0 | 1 | 0 | 0.6 kg | blanched pork belly |
| Squid scoring | 0 | 0 | 1 | 0.4 kg | squid |
| Eggs: crack + beat | 0 | 5 eggs | 0 | 0.28 kg | — |
| Marinate / 上浆 | 0 | 0 | 2 | 0.6 kg | ribs, lean pork |
| Soak (purge, salt soak, starch rinse, rehydrate, curl) | 2 | 3 | 2 rinses | — | clams, broccoli, scallops, ribs 5 min, shreds, potato 丝 |
| Scald with boiling water | 0 | 1 (2 with tomato) | 1 | — | ribs, squid, (tomato peel) |
| Portion / arrange for steaming | 32 pieces + 2 plates | 1 plate | 1 plate | — | cups (16 ribs, 12 clams, 4 ginger), taro, luffa, fish, taro bed |
| Bone-in chopping, fish cleaning, squid cleaning | (bought) | (bought) | (bought) | — | done at the stall [assumption, user's OK needed] |

### 2.5 Wang Gang's 42 recipes as a wider check

Counted from the recipe index in `research/wanggang_recipes.md` (hand count), plus a keyword scan of the transcripts. The scan undercounts meat cuts in translation.
- **Meat cutting dominates.**
  - Shreds 肉丝: 鱼香, 青椒, 京酱, 炒面.
  - Slices 肉片: 回锅 (cooked, 2 mm), 水煮, 小炒肉 (五花 1 mm from frozen), 葱爆羊肉, 酸菜鱼 (fish slices).
  - Dice 丁: 宫保, 辣子鸡.
  - Mince 肉末: 麻婆, 干煸四季豆, 鱼香茄子, 蚂蚁上树, 担担面.
  - Bone-in chops: 糖醋/椒盐排骨, 黄焖鸡, 可乐鸡翅.
  - Cubes or 段: 红烧肉, 牛腩, 焦溜肉段, 糖醋里脊.
  - About 27 of the 42 recipes cut meat [hand count]. He **freezes meat to slice it thin** (小炒肉, 鱼香肉丝, 京酱肉丝).
- **Aromatics:** 葱 31/42, 蒜 28/42, 姜 25/42 (keyword scan). 姜蒜末 appear in most stir-fries, so a mincer is a core station, not an extra.
- **Others:**
  - eggs 16/42;
  - tofu 4 (麻婆: firm cubes soaked in hot salted water; 脑花豆腐: silken, whole);
  - potato 14, eggplant 6 (条/块, starch-coated);
  - whole fish 4;
  - 手撕包菜: torn by hand, a tearing gap;
  - 拍黄瓜: smashed, which a lever press could do.
- **Marinade / 上浆 with egg white and starch:** about 6 recipes, stirred "until tacky".

The meals A/B/C are a lighter prep load than Wang Gang's set. The meat-slicing, mince and egg gaps grow in the wider set.

---

## 3. Coverage map (task 2)

Grasp data: R13 (`results/r13_matrix.json`, `results/r13_soft.json`), PGC-140-50 with finger sets P1 5–45, P2 29–69, P3 53–93, P4 77–117 mm.

| Operation | Appliance / tool in the current design | Grasp, finger set | Status |
|---|---|---|---|
| Wash firm items, held under the tap | Sink. R11: R07 wall spout; R17: the user's faucet, opened by the arm (FAUCET_OPEN/CLOSE [checked], 3.5 s) | carrot pinch P1/P2 (μ 0.15 ✓); potato pinch μ ≥ 0.3, fork ✓ P2/P3; tomato position mode ~5 N or fork ✓; cucumber pinch μ ≥ 0.3, fork ✓; ginger P1/P2 ✓ | carrot (SD G2), tomato (WD GT2) [checked] **under a spout that no longer exists**; others [bench] |
| Wash bulk, leafy, small | R13 side-handle basket (Ø200, keyed 30 mm knob, 40 N) under the tap; spinner (FULLSTAR 4.2 L press type, ¥65, market_r10 13.3) | basket knob | [bench] (R13: sprouts, shrimp, cloves, beans, strawberries, cherry tomatoes, peppers 100 % poured; lettuce fails). No kitchen chain. Clams, okra, snow peas, ribs not benched |
| Peel roots | "Peeler station": R11 abstraction (open cradle). The real product is open: 傲宏 85 W abrasive, ¥148–155 (1688), 1–3 min per batch [C] | carrot pinch on the cradle | carrot [checked] (SD G3, cradle). Potato, taro [designed]. Taro not in the R13 bench (catalog: dry μ 0.20, peeled slimy) |
| Peel others: luffa, bamboo sheath, broccoli stem, garlic cloves, pork skin, snow pea strings | none | — | [missing] |
| Slice / shred / dice roots and firm veg | 卓晋 3-in-1 (21×33×28 cm, 250 W, 10×7 cm chute, lid interlock, rocker switch; slice thickness range unpublished, 5 mm TBC; **4 mm shred disc**; dice 6–22 mm grids), ¥843 JD, counter-resident (R11) | item dropped vertically into the chute | carrot chute drop [checked] (SD G4S) at (0.30, 0.13), **now the plating area**. Potato, taro, cucumber, bamboo, ginger [designed] |
| Wedges | AY-403 lever base (2.35 kg, fetched) + 8/6-wedge plates, ¥269–305 | tomato as above; bell pepper pinch fails (3 N), fork P3 / basket | tomato [checked] (WD) + physics gate (~5 N per finger). Tomato wedging force **unsourced**. Peppers [designed by analogy] |
| Sections, halves, trims | lever base + printed 40 mm section plate / single-blade plate (R11, market 13.5 item 11) | bunches at the root: scallion pinch μ ≥ 0.3 only; chives, spinach ✓; bok choy fork ✓ | [designed]; no chain. Garlic sprouts, luffa, baby cabbage not benched |
| Mince / chop (末, 蓉, 葱花) | none (R11: "绞切杯 not in scope") | garlic cloves basket ✓ | [missing] |
| Broccoli florets | none | stem only (catalog) | [missing]; broccoli not benched |
| Meat slices / shreds | none (R11 noted the 850 W 切肉机, ~21 kg, "if adopted") | pork, chicken pinch 40 N ✓ and fork ✓ (R13 soft) | [missing]; grasp [bench] |
| Cooked meat cubes, squid scoring, fine 葱丝 | none | — | [missing] |
| Eggs: crack + beat | none | egg pinch ~7 N P1/P2 ✓, fork ✓ | [missing]; grasp [bench] |
| Marinate / 上浆 | none | — | [missing] |
| Soak / purge / rehydrate / curl | none (R10's OXO basket "fill–shake–drain" idea) | basket | [missing] |
| Scald | kettle (user-filled, R16) | kettle handle | [missing] (kettle grasp and pours unchecked, R16) |
| Portion / arrange for steaming | dish carrier into the pot [checked] (R16/R17, 17.7 s); nothing for loading the dish or cups | — | [missing] |
| Tool fetch / return, plate swap | push-to-open drawer, printed tool dock and plate dock (DECISIONS 10-09; market 13.5 items 4–5) | keyed handles | [designed]; drawer never modelled |
| Finger swap | R13 dovetail + spring-pin rack (CAD) | — | [designed]; never simulated |
| Cold items out of the fridge | R14 door-bin cold box | bridge-bar pinch | reach and the 0–35° door arc [checked]; box transfer not planned |

**What R11–R13 covered, against what the meals need**
- **Covered by a checked chain:** single-piece root → slicer (carrot), and tomato → wedges. These are about 5 of the 38 meal items (carrot, tomato; potato, cucumber and ginger use the same pattern). Both were checked in the old layout.
- **Covered by the R13 grasp bench only:**
  - potato, ginger, garlic, cucumber, chili, bell pepper (basket);
  - egg, celery stalk, scallion and chives bunches;
  - pork, chicken, whole fish, fish fillet;
  - tofu (firm fork, silken in its box).
- **In the meals but not benched at all:** taro, luffa, broccoli, bamboo shoot, baby cabbage, okra, snow peas, garlic sprouts, squid, clams, bone-in ribs, dried scallops.
- **Not covered at all:**
  - meat cutting;
  - 葱姜蒜 mincing;
  - leafy and bunch cutting (designed only);
  - mushrooms (none in A/B/C; shiitake and king oyster grasps benched);
  - tofu cutting;
  - eggs;
  - marinating, soaking, scalding, arranging.

---

## 4. Layout validity (task 3)

### 4.1 Then and now

| Item | R11/R12 prep chains (SD, WD) | Today (R17/R18b, `r19hub.union_tree` scene) | Conflict |
|---|---|---|---|
| Water | R07 wall spout, jet at (−0.58, 0.33, 0.97); prep colander in the sink | spout and colander removed. User's faucet at (−0.40, 0.555), outlet (−0.40, 0.37, 1.10); single-lever, opened by the arm | **Washing is at a place with no water.** The chain is geometrically clean there today (no hits), but functionally invalid; it must be re-planned under the R17 outlet. The sim's single 0.6 m basin cannot hold the wok and the colander together (R17), so baskets must leave the sink before each wok trip. |
| Peeler / lever work spot | fetched to (−1.00, 0.20) / (−1.00, 0.095), per step | spatula flat at (−1.15, 0.30), flipped (R18b), on a 2 cm pad | **Static overlap** peeler ↔ spatula (P16 guide through the blade by up to 94 mm; peel guard 9–12 mm into the blade and pad). Lever base plate touches the pad (0.0 mm). |
| Slicer | counter-resident at (0.30, 0.13), out bowl at x 0.575 | plating spots at x 0.43 and 0.17 (y 0.13, r 0.12); cooker from x 0.63 | **Static overlap** 77 mm with both plates; out bowl 64 mm into plate 1 and 28 mm into the cooker |
| Raw tray | x −1.515…−1.195, y 0.04–0.34 | unchanged (R18 kept it) | 5 mm from the spatula pad |
| Rice/flour outlet | — | still in the sim at (−1.05…−0.95, 0.30…0.46, z 1.31) | Obsolete (the user loads the rice cooker). Removing it frees the cabinet underside above the left counter. |
| Fridge cold box set-down | — | R14: (−1.70, 0.18), the only counter spot that passed | overlaps the proposed far-left tool spot (4.4) |
| Arm / fingers | UR5e, dual-zone D fingers | same model (`chain_cfg('SD')` underlies all R17 scenes) | none |

### 4.2 Replays of the stored prep chains in today's kitchen [screen]

Run: `r19prep_replay.py SD|WD`. It uses every stored state with each chain's own stations, held item and tomato state per segment, as `chain.py` checked them. Results: `results/r19/prep/replay_*.json`.

| Chain | States | Hits on R14+ fixtures | Where | Worst |
|---|---|---|---|---|
| SD carrot | 7,431 | **423** | end of C2 (arrival at the peeler, cart −1.349), **all of G3 peel load and retrieve** (216/216), start of C3 | wrist-2 capsules `R_geom_25/26` vs `r16_spatula_handle`, **−12.0 mm** (penetration) at the start of peel_retrieve |
| WD tomato | 5,992 | 0 | — | — |

- **Control:** the same states in the chains' own R12 scenes (`SCENE=orig`, every 4th state) show only the declared contact windows: carrot on the ribs and in the cradle, tomato on its pad and on the blade plate, fingers near the released tomato. The r18 run shows the same pairs, so the screen adds nothing spurious.
- **Joint windows (side finding)**, under the same UR-convention assumption as `research/r19_arm_hand_cost.md`:
  - no 2π jumps in either chain;
  - SD's J4 spans −9…182°, outside the Fairino FR5 J4 window (+85/−265°), with or without the J6 option;
  - WD fits the FR5;
  - both fit the CS66 and the CR5A.

### 4.3 Where can prep appliances stand without blocking cooking?

**Method.**
- `r19prep_screen.py` screens envelope boxes at 8 counter spots against the 84 stored swept segments (R19) plus the 22 checked hub edges (106 in total). Flagged means "must be replayed"; not flagged means "cannot be hit" (conservative).
- `r19prep_spotreplay.py` then replays every state of the 6 cooking chains and every 4th state of the flagged hub edges with the box in the scene [screen].
- Front spots get flagged often, because the cart passes along the cabinet fronts. That is the known conservatism (R19).

| Envelope (size, basis) | Spot (centre) | Flagged / 106 | Ground-truth replay |
|---|---|---|---|
| R11 tool work spot (peeler envelope 0.39×0.26×0.45) | (−1.00, 0.155) | 40 | **hit**: wok plate+rinse at both spots (sink segments 6→13, shoulder link, gap 3.9 mm); faucet lever (−60 mm); spatula fetch; 8 of 13 flagged hub edges (LEV_C/LEV_O↔hubs, LEV_O→WOK, SPAT→LEV_C; −9.9 mm). Not hit: lid, spider, corridor, SPAT↔H_SPAT/H_SINK, WOK↔H_SINK |
| lever base (0.22×0.26×0.42, AY-403) | (−1.30, 0.155) | 20 | **hit**: wok sink segments 9→11 (9.95 mm vs 10 required); spatula fetch (−5 mm) |
| lever base | **(−1.62, 0.155)** | 10 | **no hits** (6 chains, 2,003 states + 6 hub edges) |
| 卓晋 slicer + out bowl (0.50×0.21×0.28) | **(−1.00, 0.475) back** | 3 | **no hits** |
| 850 W meat slicer (0.37×0.34×0.42) | (−1.00, 0.41) back | 4 | **hit**: spatula fetch (−43 mm; it overlaps the spatula rest) |
| any of the 5 envelopes | (−1.62) far-left back | 0 | clear by construction |
| belt cutter / lever | (−0.88) back, by the sink | 0 | clear by construction |
| any | R11 slicer spot (0.30, front) | 50–57 | overlaps the plates anyway |

**What this means**
- **The cooking layout took the prep spots.** In the R18 kitchen:
  - the right counter is the plating area;
  - the left counter front (x −1.35…−0.80) is swept by the wok sink trip, the faucet lever and the spatula fetch;
  - the spatula lies on the old peel spot.
- **Fetched tools.** A far-left front spot (−1.62, 0.155) passes [screen]. It must share that counter end with the fridge cold box (R14 set-down at (−1.70, 0.18)): never both out at once, or move the box spot. Otherwise every tool must be stowed before each plating, dump or fill trip and each spatula fetch (more fetch/return trips).
- **Counter-resident appliances:** only back spots under the upper cabinets are clear (−1.00 or −1.62 back; −0.88 back for the smaller ones).
  - Feeding there is doubtful. R14's reach probes reached a cup under the cabinets only to z 1.12 at y 0.40 and z 1.05 at y 0.48.
  - Chute tops: 卓晋 ~1.13 m, belt cutter ~1.23 m, meat slicer ~1.27 m. The cabinet bottom is at 1.35 m, which leaves 8–22 cm of headroom for a vertical drop.
  - Turning the 卓晋 so its chute sits under the cabinet front plane (y < 0.23) is the first thing to try. Its reach is **not checked**.
- **The user's real kitchen is L-shaped** (the sink leg has an estimated ~95 cm of free counter). The prep counter may belong there, which again depends on their measurements (README open item).

---

## 5. Gaps and options (task 4)

Rule: appliances do the precise work; domestic products first; multi-function bases; 3D printing allowed. Prices are from `research/market_r10.md` unless marked [C]. Nothing is bought. Process forces below are **sourced** (food catalog) and serve as orders of magnitude only. Blade geometry differs, so each needs a measurement.

**Arm force available:** about 100 N on the lever pusher, limited by the keyed grip at 150 N / SF 1.5 (R11 sim).

### 5.1 Meat slicer (切肉机)
- **Best option:** a counter-resident 850 W 切肉切菜一体机 with interchangeable blade sets.
  - 32–37 × 30–34 × 31–42 cm, ~21 kg, 150–200 kg/h.
  - Top chute 7 × 13 cm; sets 2.5/3.5/5/7/10/13/15/21 mm for slices, shreds and dice.
  - ¥474–1,080 on Taobao listings [C, market 13.7–13.8].
  - It also cuts soft vegetables (cucumber, peppers, mushrooms).
- **Limits:**
  - Fresh boneless meat only. Some export manuals exclude frozen meat, bone-in meat and hard roots [C].
  - No interlock data. DECISIONS requires guarded blades with interlocks; check before choosing.
  - 21 kg is over the 3.5 kg fetch limit, so it must stay on the counter, and a counter spot with arm access to a ~1.27 m chute must be found (4.3).
- **Robot interface:**
  - pork pinch at 40 N passes at μ 0.15 [bench];
  - drop into the chute, then the machine's pusher with a printed keyed block;
  - output tray out with a side handle.
- **Covers:**
  - meals: 干锅 pork belly slices, lean pork slices, squid strips instead of scoring;
  - Wang Gang: 肉丝, 肉片 and 丁 (about 10–15 recipes);
  - his "freeze to firm" trick fits a partly frozen block in the fridge cold box (DECISIONS: thaw rules below).
- **Cooked pork belly cubes (~3 cm, 红烧肉):** beyond the 21 mm set. Option: a printed 30 mm grid plate on the lever base. The cutting force for blanched pork belly with skin is **not sourced**; measure before relying on it.
- **Fallback (user's call):** the butcher slices or shreds at purchase.

### 5.2 Garlic / ginger mincer (绞切杯 / 料理机)
- **Best option: a fetched 2 L household chopper (家用绞肉机 class).**
  - 300 W, glass bowl, S-blade, ~¥58 for the 小熊 QSJ-E03C8 [C, JD snippet; power not confirmed].
  - Robot interface:
    - garlic cloves poured from the basket;
    - the motor head lowered onto the bowl by a printed keyed handle;
    - power by smart plug, so choose a model with a latching switch, or press the head button with the arm;
    - pulse 5–10 s, head off, pour out.
  - Residue of minced garlic in the bowl is **unmeasured**.
  - One base covers garlic, ginger, chili, celery, 葱花, 肉末 (Wang Gang's 5 mince recipes) and **beating eggs** (5.3). That fits "multi-function base".
- **Counter-resident alternative:** a commercial 蒜蓉机 (200 W, ~30 kg/h, hopper on top) [C, reseller pages only]. Too big for a few cloves.
- **Peeling cloves:**
  - Electric peelers are commercial and need dry, separated cloves [C].
  - Most robot-friendly: peeled garlic bought as a purchase form [assumption: common in Chinese supermarkets, verify locally; user's OK]. Or a household rotary peeler, if a domestic one is found.

### 5.3 Egg cracker and beater
- **Cracking:** a lever egg cracker of the EZ-Cracker type. The egg goes into a cradle, a squeeze cracks it, and the egg drops into the bowl with the shell retained [C, product pages].
  - Mount it on a printed stand over the bowl; the arm presses the handle (the lever-base pattern), then tips the shell into the waste bin.
  - Egg pinch at ~7 N and the fork both pass [bench].
  - Sourced egg loads: puncture **26.3 N** (2 mm probe, EGG2); equator rupture **38–45 N** (EGG3). Both are under the arm's ~100 N. The cracker's own lever ratio and its shell-fragment rate are not sourced: test it.
  - The Rösle Egg Clacker only cuts a cap off the egg top, so it does not fit.
- **Beating:** pulse the eggs in the chopper bowl (5.2), or use a whisk tool held by the arm like the spatula. Neither is checked, and beating quality is not sourced.
- **Covers:** 番茄炒蛋 (5 eggs) and Wang Gang's 16/42 egg recipes.

### 5.4 Tofu cutter
- Not needed for A/B/C. Wang Gang: 麻婆 (firm cubes), 脑花豆腐 (silken, whole).
- **Option:** a printed blade grid (stainless strips, 15–20 mm pitch) on the lever base. Press it into the opened box (silken, R13 in-box ✓ [bench]) or onto a firm block on a slot tray (fork ✓ [bench]), then slide it out.
- No cutting force for tofu is sourced; only the compressive stresses (silken 3.7 kPa, firm 18.9 kPa at 30 % strain, TF1).
- The R13 open item remains: the silken slide-out without a 10 cm drop.
- Domestic tofu cube cutters: no specific product found [ND]; generic cutters ¥10–40 [C].

### 5.5 Greens cutter
- **Now:** the lever base with the 40 mm section plate and the single-blade plate (R11, [designed]):
  - garlic sprouts, scallion 段, celery, luffa 段, bok choy;
  - baby cabbage halves and quarters (laid flat, two strokes);
  - one press per 30–40 mm.
- **Force risk (sourced references):**
  - chive bundle max shear **129 N** (CV1); cabbage root cutting **137 N** (CB1); spinach root shear **31 N** (SP1); carrot shear **41 N** (C1); ginger cutting **219–253 N** (Gi1).
  - Thick bundles may exceed the ~100 N direct press. Driving the AY-403's own lever handle instead of the pusher would multiply the force, but its ratio is not published.
  - Ginger goes to the powered slicer, not the lever.
- **Better if counter space frees up:** a belt cutter (切葱花机).
  - 28×26×38 cm, 8.7 kg, 200 W, cut length 1.5–35 mm, 庄得 ¥234 [C]. Items are simply laid on the belt.
  - It needs about 46 cm of permanent counter (DECISIONS R11). In the sim only back spots are clear (−0.88 or −1.62); the belt's reach there is unchecked.
- **Florets (broccoli):** no appliance cuts florets. Options:
  - purchase form (净菜 florets) [user's OK];
  - two crossed single-blade presses on the lever (rough "florets"; quality not judged);
  - drop the stem slices.

### 5.6 Soaking and thawing container
- **Soak tub:** a GN 1/3 stainless pan with a perforated basket insert carrying an R13 keyed side handle, parked at the counter end or the sink back (cost [est] ¥50–150).
  - It is filled at the running tap (the pattern of the composed WOK_FILL set) and drained by lifting the insert, so it reuses the BASKET sets.
  - Covers: clam purge, broccoli salt soak (his 10 min), potato-shred starch rinses, scallop rehydration, curling 丝 in water, the ribs' 5-min soak.
  - Purge and rehydration times are **not sourced**.
- **Scalding:** boiling water from the user-filled kettle over the basket in the tub (ribs, squid, tomatoes for peeling). The kettle grasp and pours are **unchecked** (R16 open item).
- **Thawing:** USDA FSIS lists three safe ways: refrigerator, cold water (leak-proof bag, change the water every 30 min; ~1 lb ≤ 1 h) and microwave; never on the counter or in hot water [O, FSIS "The Big Thaw", search snippet; the page refused a direct fetch].
  - Robot plan: thaw in the fridge. The user moves frozen meat into the R14 cold box the evening before, the same "user loads the cold box" interface R14 already accepted.
  - The robot cannot reach the freezer or the shelves (R14), and cannot open sealed bags, so cold-water thawing is not proposed.
  - Raw meat staging stays ≤ 1 h at room temperature (R14).

### 5.7 Other gaps, by option

| Gap | Robot option | Purchase form or recipe adaptation (user's decision) |
|---|---|---|
| Luffa peeling | none credible yet. A fixtured luffa plus an arm-held Y-peeler stroke would need force data; lotus skin peeling cut force 9–13 N (L1) is the only proxy | no peeled form is sold (it browns); swap to 西葫芦 / 节瓜 steamed unpeeled, a recipe change |
| Bamboo sheath | none | buy shelled or boiled 鲜笋 |
| Bone-in chopping (ribs) | none (bone saws are commercial and unsafe) | butcher-chopped ribs (the stall does it) |
| Fish cleaning, back-split | none | at the stall (catalog: "scaled/gutted at the stall") |
| Squid cleaning and 麦穗花刀 | strips or rings from the meat slicer | cleaned squid; accept strips instead of scoring |
| Fine 葱丝 / 姜丝 | the 4 mm shred disc for ginger and carrot; scallion needs a printed comb the arm pulls a section through (concept) | accept 4 mm or 葱段 |
| Snow pea strings | none | young peas unstrung, or bought trimmed |
| Pork skin scraping | skip, or a fixed scraper blade (concept) | buy 去毛 belly |
| Tomato peeling (scald) | the scald set + skin removal: no tool | R16 already dropped peeling |
| Portioning 16 ribs + 12 clams into 4 cups | pour-portion by weight from the basket (4 partial pours per ingredient, the scale under the cup) instead of 32 single placements | — |

**Cost of the proposed additions [C/est]:** meat slicer ¥474–1,080; chopper ~¥60–200; egg cracker plus a printed stand ~¥50; soak tub and insert ~¥50–150; printed plates and stands in the existing print budget. Optional belt cutter ¥234. That is roughly **¥0.7–1.5k** on top of the D1 prep set (¥1.7–2.4k). All prices are unconfirmed.

---

## 6. Prep as movement sets (task 5)

### 6.1 Hubs

| Hub | Cart x | Exists? | Serves |
|---|---|---|---|
| H_SPAT | −1.48 | **yes** (R19 roadmap; spatula rest, idle park) | raw tray picks (SD/WD pick at cart −1.48), fridge cold box (R14 docked at −1.48), the proposed far-left tool spot (−1.62, front) |
| H_SINK | −0.68 | **yes** (faucet) | washing (SD at −0.675, WD at −0.62), basket wash, soak tub, fills |
| H_TOOL (= H_SPAT spur) | ~−1.48…−1.62 | new | lever base, egg cracker, chopper bowl at the far-left work spot |
| H_SLICE | TBD (−1.00 back if feed reach passes) | new | 卓晋 chute |
| H_MEAT | TBD | new | meat-slicer chute |
| H_STORE | TBD | new | tool / plate drawer (never modelled) |
| H_WOK, H_POT | 0.172, 1.093 | yes | output transfers into the wok, the steamer, the stew pot |
| Held-item hubs | per station | new | carry postures with an item in hand (R12 "compact carry" candidates), one per held class: piece, basket, bowl |
| Finger rack | on the cart [proposal] | new | swaps without a transit; the R13 rack position was never fixed |

**Hub alignment:** the R12 chains already start at cart −1.48 and wash at −0.675/−0.62, so their stations line up with the R19 hubs. The new prep sets can plug into the verified corridor (H_SPAT–H_SINK 3.8 s, H_SINK–H_WOK 4.0 s [checked]).

### 6.2 Prep movement-set families, status and reuse

Reuse counts are from `prep_demand.json`; a "piece cycle" counts the pick, carry, wash and station sets together.

| Set family (primitives) | Status | A | B | C | Σ |
|---|---|---|---|---|---|
| TRAY_PICK pinch / fork / pad + CARRY to a station (approach, seat_lift, carry, meet_join) | [checked] SD G1/C1, WD GT1/C1 in the old layout; carries C2/C3 near the peeler **hit the spatula today** | 14 | 10 | 10 | 34 piece cycles |
| WASH_HELD (insert under the outlet, scrub stroke, dwell, extract) | [checked] under the removed R07 spout → **re-plan** at the R17 outlet | in the piece cycles | | | ~19 |
| FAUCET_OPEN / CLOSE + spurs | [checked] (R17, R19 hub spurs) | 2 | 2 | 2 | 6 |
| BASKET fetch / under-tap wash / drain / pour(target) / return | [bench] pour only | 7 | 5 | 6 | 18 |
| SOAK in / out (basket + fill) | [missing]; reuses BASKET + WOK_FILL pattern | 2 | 3 | 2 | 7 |
| PEEL: cradle load / retrieve (R11) or abrasive batch (pour in, clamp, run, pour out) | cradle [checked] old layout, **hits the spatula today**; batch [designed] | 2 | 0 | 2 | 4 batches |
| CHUTE_DROP (+ pusher) at the slicer | [checked] at a spot that is now the plating area | in the piece cycles | | | ~25 |
| LEVER_PLACE (+ release window) and LEVER_PRESS (pusher grasp, press, return, release) | [checked] tomato (WD), old layout; not hit today, but the base must not stay out | 27 | 18 | 0 | 45 presses |
| LEVER_PLATE_SWAP (plate + pusher from the dock) | [designed] | 2 | 3 | 2 | 7 |
| TOOL_FETCH / RETURN (drawer ↔ work spot) | [designed]; drawer not modelled | 3 | 3 | 3 | 9 |
| FINGER_SWAP (rack) | [designed] CAD only | 5 | 5 | 5 | 15 [est] |
| OUTPUT_XFER (bowl/bin → staging bowl, carrier dish, wok, cup) | [missing]; same family as the cooking CUP_POUR, also unchecked | 5 | 7 | 2 | 14 |
| MINCE_RUN (chopper) | [missing] | 1 | 2 | 3 | 6 |
| MEAT_FEED (meat slicer) | [missing] | 1 | 0 | 2 | 3 |
| EGG_CRACK, EGG_BEAT | [missing] | 0 | 5 + 1 | 0 | 6 |
| MIX_SHAKE (marinate, 上浆) | [missing] | 0 | 0 | 2 | 2 |
| SCALD (kettle pour) | [missing] | 0 | 1 | 1 | 2 |
| PLACE_PIECE / ARRANGE on a dish | [missing] (carrier into the pot [checked]) | 32 + 2 | 1 | 1 | 36 |
| FRIDGE_BOX fetch / return | reach + door arc [checked]; transfer not planned | 1 | 1 | 1 | 3 |

That is about 20 families. With reversals (return = fetch reversed, as R19 rule 4) about 25 stored sets, on about 7 hubs plus held-item hubs. Instances per meal: A 106, B 67, C 44.

### 6.3 Arm time per meal [est] and how it fits

**Unit times** (`r19prep_demand.py`, each with its basis):
- **Derived from checked paths:**
  - single-piece cycle 30–45 s (SD 28.1 s / WD 22.3 s motion, plus jaw events and windows, +30 % for smooth timing);
  - lever press 8–12 s;
  - faucet + spurs 15–20 s.
- **Estimates by analogy:**
  - basket 40–60 s (vs the spider 52.6 s [checked]);
  - tool fetch + return 40–50 s;
  - output transfer 15–20 s (vs the carrier 17.7 s [checked]);
  - batch peel 70–100 s arm (+1–3 min unattended);
  - mince 50–80 s; egg 15–25 s each; piece placement 6–10 s; finger swap 10–15 s.

**Fit:** each prep item must finish before the meal step that uses it (`meal_stew_r18_userrice.json`). Items are packed into the arm's idle windows; what does not fit goes into a prep-first block before the meal starts.

| Meal | Cook total / arm (rice by the user) | Prep arm time | Biggest items | Prep-first block | Meal incl. prep | Arm busy incl. prep |
|---|---|---|---|---|---|---|
| A | 38.2 / 13.9 min | **27–40 min** | luffa sections (20 presses) 4–6 min; tool, finger and faucet overhead 4.6–5.8; taro 3.7–5.7; cup portioning 4.5–7.2 | 6.9–17.4 min | **45–56 min** | 41–54 min |
| B | 75.6 / 28.4 | **22–32** | tools/fingers 4.2–5.3; eggs 2.3–3.4; scallion 2.2–3.3; tomatoes 1.8–2.6 | 6.0–10.4 | **82–86** | 51–61 |
| C | 35.6 / 17.9 | **21–30** | tools/fingers 4.6–5.8; taro 3.2–4.8; potato 丝 3.0–4.5 | 5.3–12.7 | **41–48** | 39–48 |

Not modelled: the sink and counter conflicts between prep and the wok trips (4.3). These may force more tool round-trips, so the numbers are a lower bound on the sequencing cost.

**What cuts the time most:**
- pour-portioning instead of 32 placements in A (saves ~3–5 min);
- the far-left tool spot, so tools need not be stowed around wok trips;
- batch peeling;
- grouping all washing into 2 faucet sessions;
- a finger set that serves several items (P2 covers carrot, egg, potato, cucumber, ginger, garlic and king oyster in R13).

### 6.4 Verification plan, in priority order

**P0. Layout: it blocks everything; cheap; first.**
1. Choose the fetched-tool work spot.
   - Candidate (−1.62, 0.155): clear [screen].
   - Resolve the clash with the fridge cold-box set-down (−1.70, 0.18): serialize the two, or find a second box spot.
2. Choose the slicer spot. Candidate: 卓晋 at (−1.00, back), clear [screen]. Its chute is under the cabinet, so the first test is a reach probe (96-start IK, the `r14reach.py` method) at the chute top with a vertical carrot. Also probe a turned slicer with its chute at y ≤ 0.23.
3. Decide the meat slicer's place. In the sim kitchen there is none with a reachable chute; this may need the user's L-shaped kitchen.
4. Remove the obsolete rice/flour outlet from the scene.
5. **Commands available now:**
   ```
   cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
   PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
   $PY r19prep_screen.py                                          # ~32 s, all spots x envelopes
   $PY r19prep_spotreplay.py NAME X Y SX SY SZ                    # 34-110 s per spot (screen-level replay)
   $PY r19prep_replay.py SD STRIDE=1; $PY r19prep_replay.py WD    # 120 s / 97 s
   ```
6. **To add next round:**
   - a `FULL=1` option for full-checker replays;
   - fridge geometry (`r14_fridge`) in the union scene;
   - a reach-probe script for the chute and knob targets.

**P1. Re-plan the two checked chains as library sets in today's kitchen. They are the most reused.**
1. **WASH_HELD under the R17 outlet.** Port G2/GT2 to an `r17chain.py`-style action that starts and ends at H_SINK hubs, reusing FAUCET_OPEN/CLOSE and the wok chain's "insert under the tap / extract" pattern (the outlet at 1.10 m sets a new insert height).
2. **TRAY_PICK + CARRY + CHUTE_DROP and LEVER_PLACE + LEVER_PRESS** at the P0 spots, ending at hubs. Re-run the physics gate (`dyn.py`, noslip, wet μ 0.15–0.3) on the new paths.
   - Through `chain.py` this needs new presets in `mystat.py`, i.e. an edit next round: stations moved, R17 kitchen keys.
   - Run order: `chain.py <P> SEQ`, `N`, `C1`…`C3`, `A` (as `replan.py`).
   - Chain runs can exceed 5 min (R12: a 1,600 s RRT). Per the project rule, run them from the controller, not a subagent.
3. **New hub spurs** for the prep endpoints: `r19hub.py edge A=<prep node> B=H_SPAT|H_SINK` after adding the nodes to `ENDS`/`STATIONS` (code change). Each spur takes 2–7 min.

**P2. Most-reused unchecked families.**
1. BASKET (18 uses) and SOAK (7): kitchen chain from the basket rest → under the tap → drain → pour into a chute, tub or bowl → rest. This is R13 open item 2.
2. TOOL_FETCH/RETURN (9) with a modelled push-to-open drawer, and LEVER_PLATE_SWAP (7).
3. OUTPUT_XFER (14): do it together with the cooking library's CUP_POUR family (same primitives: grasp, carry, tip, return).
4. FINGER_SWAP (15) in the rack: clearance check plus a physics run of the pin release. Fix the rack's place (on the cart, so no transit).

**P3. New appliances, after the user agrees to the products.**
- MINCE_RUN (6), EGG (6), MEAT_FEED (3), MIX (2), SCALD (2; needs the kettle grasp), PEEL batch (4).
- PLACE/ARRANGE (36), or replace it by pour-portioning.

**Physical tests (not sim; the user's decision, nothing bought):**
- **Cutting forces:** tomato 8-wedge (still unsourced), greens and garlic-sprout bundles on the 40 mm plate, blanched pork belly cubes, tofu grid, egg-cracker press.
- **Wet pad friction:** the tilt test (R13 open item).
- **Slicer quality:** 卓晋 slice thickness (5 mm?) and 4 mm shreds on potato.
- **Abrasive peeling** of taro.
- **Chopper residue** and egg-beating quality.
- **Meat slicer** on fresh pork belly with skin.

---

## 7. Honesty notes

- **Checked earlier** (R11–R13, unchanged checker, physics gate): only the carrot chain SD and the tomato chain WD, both in the old layout. The R13 grasps are floating-gripper bench results.
- **Screened in this round:**
  - the SD/WD replays;
  - the voxel screen;
  - five spot replays.
  These all used the fast checker (`full=False`) and every 4th state on hub edges. They show conflicts reliably, but a "no hit" here is not a full check.
- **Code state:** a parallel R19 arm study edited `checker.py` and `scene.py` (backups `*.bak_r19arm`, 12:19–12:36) while these runs went on. The diff keeps the UR5e default unchanged: same envelope file, same 0.35 m CoM radius. Two of the spot replays (lever at −1.30 and −1.62) ran after the edit; the others ran before it.
- **Not checked at all:**
  - any reach to a new appliance spot;
  - every prep set marked [designed] or [missing];
  - sink and counter sharing between prep and cooking in time.
- **Estimates:**
  - all masses, piece counts and cut sizes not stated by him;
  - all unit times marked E;
  - the prep-first block and meal totals (a packing estimate, one arm, no resource conflicts).
  - R19's "10–20 min per meal" was an order-of-magnitude figure; this one is item-by-item but still estimated.
- **Purchase forms** (butcher-chopped ribs, stall-cleaned fish and squid, shelled shoots, peeled garlic, florets) are design assumptions. They are not home prep by a person, but they change what the user buys, so they need the user's OK, like the R13 slot trays.
- **Forces:** every force quoted is from the food catalog (tags C1, CV1, CB1, SP1, Gi1, L1, EGG2, EGG3, TF1) or the R11 sim (arm push ~100 N). No cutting force was tuned or invented. The required forces for the lever operations remain to be measured.
- **New web lookups** this round (read-only; all [C]/[O]):
  - [USDA FSIS, The Big Thaw](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/big-thaw-safe-defrosting-methods) (search snippet; direct fetch 403);
  - [EZ Cracker](https://www.bettercaremarket.com.au/egg-cracker-ezcracker.html);
  - [Rösle Egg Clacker](https://www.boroughkitchen.com/products/rosle-egg-clacker);
  - [household 2 L chopper guide, pconline](https://best.pconline.com.cn/guide/92075.html);
  - [小熊 QSJ-E03C8 listing, JD](https://www.jd.com/tupian/73770788baf5683d087.html);
  - [200 W garlic peeler, reseller page](https://kingfahad.sa/products/electric-whole-garlic-peeling-machine-200w-automatic-garlic/215100033/).
  - No domestic tofu cutter product was found. No purchase or seller contact was made.
