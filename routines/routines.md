# Cooking routine library (one-arm robot)

Generated 2026-10-13 from Wang Gang's 42 recipes (258 phases) and the three home-style 四菜一汤 meals (17 dishes incl. rice and 白灼汁). Data: `routines.json`.

A routine is a predefined sequence that runs straight through, with parameters and a stop condition that uses only the thermometer, the clock and simple camera rules. The planner (LLM) picks the routine and its parameters; it never decides between the steps inside one.

## Counts

- **57 routine types**, 505 routine calls across 59 dishes.
- Wang Gang: **250 / 258 phases covered**; all 42 recipes mapped. Home-style: 41 / 49 steps covered.
- Dishes fully covered (every phase): **45 / 59**.
- Dishes where every call is `demo` or `demo_ready` (runnable in the build_day demo with its wok model): jiucaichaodan, xihongshichaodan.
- "Covered" = a library routine does the phase with one arm (as written or with a workaround that keeps the dish). It does **not** mean the motions are checked: see the worst-status rows below.

| Category | Types |
|---|---|
| wok | 25 |
| prep | 10 |
| sauce | 7 |
| plating | 6 |
| pot_steam | 5 |
| fry | 1 |
| cleanup | 1 |
| stew | 1 |
| other | 1 |

| Status | Types | Calls | Phases whose worst call has this status | Dishes whose worst call has this status |
|---|---|---|---|---|
| `demo` | 10 | 168 | 41 | 0 |
| `demo_ready` | 5 | 97 | 76 | 2 |
| `sim_motion_checked` | 3 | 21 | 15 | 0 |
| `needs_check` | 25 | 169 | 132 | 22 |
| `needs_hardware` | 9 | 39 | 34 | 26 |
| `two_hands` | 5 | 11 | 9 | 9 |

Status meaning: `demo` = one of the 9 executable build_day routines; `demo_ready` = expressible with the demo's skills and wok-model ingredients; `sim_motion_checked` = every arm movement set it uses is verified (or composed from verified sets) in R19; `needs_check` = the motions exist in the design but are not verified; `needs_hardware` = equipment not designed yet; `two_hands` = one arm cannot do it as written.

Only 3 types are `sim_motion_checked`: **steam_plate** (CARRIER_IN, LID_ON_pot, LID_OFF_pot, CARRIER_OUT, all verified), **wash_wok** and **wok_fill_water** (FAUCET_OPEN/CLOSE verified; WOK_DUMP_RINSE / WOK_FILL composed from the verified wok chain). The demo routines themselves rely on CUP_POUR_wok (not verified) and STIR_CYCLE_dice (partially verified).

## Top 20 types by instances

| # | Type | 中文 | Category | Status | Calls | Dishes |
|---|---|---|---|---|---|---|
| 1 | `take_out` | 出锅 | plating | demo | 58 | 45 |
| 2 | `drum_add_stir` | 鼓仓加料翻炒 | wok | demo | 54 | 36 |
| 3 | `add_stir_fry` | 下料翻炒 | wok | demo_ready | 41 | 33 |
| 4 | `bloom_aromatics` | 爆香 | wok | needs_check | 32 | 31 |
| 5 | `add_off_heat` | 离火下料 | wok | demo | 20 | 16 |
| 6 | `return_and_toss` | 回锅翻匀 | wok | demo | 20 | 20 |
| 7 | `simmer_open` | 煮/烧(敞口) | wok | demo_ready | 20 | 14 |
| 8 | `blanch_lift` | 焯水/煮后捞出 | pot_steam | needs_check | 20 | 17 |
| 9 | `wok_grease` | 润锅/滑锅 | wok | demo_ready | 18 | 18 |
| 10 | `deep_fry` | 炸/复炸 | fry | needs_check | 17 | 12 |
| 11 | `thicken` | 勾芡/收汁(碗汁) | sauce | demo_ready | 14 | 13 |
| 12 | `render_fat` | 煸 | wok | needs_check | 12 | 12 |
| 13 | `pour_cup_over_plate` | 淋汁/撒料 | plating | needs_check | 10 | 9 |
| 14 | `prep_mince_meat_cut` | 剁末/切肉 | prep | needs_hardware | 10 | 10 |
| 15 | `hot_oil_pour_over` | 泼油/浇热油 | sauce | needs_check | 9 | 9 |
| 16 | `braise_lid` | 焖(盖盖) | wok | needs_check | 8 | 7 |
| 17 | `wok_fill_water` | 锅中加水(龙头) | wok | sim_motion_checked | 8 | 8 |
| 18 | `steam_plate` | 蒸 | pot_steam | sim_motion_checked | 8 | 7 |
| 19 | `arrange_on_plate` | 摆盘 | plating | needs_check | 8 | 8 |
| 20 | `soak_bowl` | 浸泡 | prep | needs_hardware | 8 | 8 |

## What blocks coverage

**Not covered (covered=false):**

- 回锅肉 phase 1 — `prep_mince_meat_cut`: slicing cooked pork 2 mm: no meat slicer (R19_PREP_AUDIT [missing])
- 水煮肉片 phase 1 — `prep_mince_meat_cut`: mincing the fried chilies (刀口辣椒) on a board: no chopper
- 白切鸡 / 口水鸡 phase 3 — `prep_mince_meat_cut`: chopping a whole cooked chicken: no chopper
- 红烧鲤鱼 phase 0 — `take_out`: whole fish out of the wok and back later without breaking it: needs a fish turner + ladle (two hands); workaround: leave the fish in and cook the sauce around it
- 红烧鲤鱼 phase 5 — `take_out`: lift the whole fish onto the plate and keep the sauce: two hands (turner + ladle); workaround: thicken first, then tip fish + sauce together
- 清蒸鲈鱼 phase 3 — `reboil_plate_juices`: optional 进阶 step: chopsticks + plate + strainer at once
- 土豆烧牛腩 phase 0 — `prep_mince_meat_cut`: cubing the cooked brisket: no meat cutter
- 鸡蛋肉丝炒面 phase 0 — `prep_mince_meat_cut`: cutting the fried egg into strips: no cutter for it
- 蛤蜊排骨盅 (A) phase 0 — `steam_cups`: cling film needs two hands; workaround: lidded cups
- 蒜蓉蒸丝瓜 (A) phase 0 — `prep_peel`: luffa peeling: [missing] in R19_PREP_AUDIT
- 蒜蓉蒸丝瓜 (A) phase 2 — `prep_mince_meat_cut`: garlic mince: no chopper (buy minced garlic)
- 红烧肉 (B) phase 1 — `prep_mince_meat_cut`: scraping the skin + cubing cooked belly: no tool
- 清蒸海鲈鱼 (B) phase 2 — `prep_mince_meat_cut`: fine 葱姜胡萝卜丝 1–2 mm: no tool (slicer shred disc is 4 mm)
- 番茄炒蛋 (B) phase 0 — `prep_egg_beat`: crack + beat 5 eggs: user does it
- 青椒炒鱿鱼 (C) phase 0 — `prep_mince_meat_cut`: scoring squid 麦穗花刀: buy pre-scored
- 青瓜肉片汤 (C) phase 0 — `prep_mince_meat_cut`: slicing lean pork: no meat slicer

**two_hands types** (workaround in brackets):

- `pour_off_excess_oil` (3 calls): One arm cannot hold the food back and tip at once. Workaround: spider the food into the holding bowl, take_out(oil_cup), add back (3 sets, +~40 s); or use less oil so no pour-off is needed.
- `steam_cups` (3 calls): Cling film needs two hands. Workaround: cups with ceramic lids; then needs_check (STEW_CUP_IN not verified).
- `bowl_pack_invert` (1 calls): Inverting bowl + plate together needs two hands. Workaround: arrange on the plate directly (arrange_on_plate), no dome.
- `reboil_plate_juices` (1 calls): Chopsticks + plate + strainer at once. Optional 进阶 step: skip.
- `prep_egg_beat` (3 calls): One gripper cannot crack an egg. Workaround (the demo): the user cracks and beats them, cup in the cold box.

**needs_hardware types:**

- `ladle_baste` (0 calls) — ladle (not designed). Workaround: lid on (braise_lid) instead of basting.
- `steep_off_heat` (2 calls) — whole-bird basket or hook (not designed). Workaround: chicken in a wire basket that the arm lowers and lifts.
- `cold_water_chill` (2 calls) — cold-water bowl + basket. Soak / drain has no design (R19_PREP_AUDIT [missing]).
- `serve_soup` (7 calls) — serving bowl spot; ladle (not designed). Tipping into a bowl is not simulated; soups over 1.15 kg exceed the checked wok payload.
- `cold_mix_bowl` (6 calls) — bowl fixture + mixing spoon (not designed). 
- `prep_mince_meat_cut` (10 calls) — chopper cup / meat slicer (not designed). R19_PREP_AUDIT [missing]. Practical route: buy pre-cut.
- `prep_marinate` (3 calls) — mixing bowl + paddle (not designed). R19_PREP_AUDIT [missing].
- `soak_bowl` (8 calls) — kettle, soak basket (not designed). R19_PREP_AUDIT: soak and scald [missing]; kettle grasp unchecked.
- `grind_spice` (1 calls) — spice grinder (not designed). Workaround: buy ground 椒盐.

**Biggest needs_check families** (design exists, motions not verified): cup pour into the wok (every add_off_heat-based routine), the shreds/leafy stir stroke, wok lid on/off (braise_lid), spider scoop from the wok and the fryer (deep_fry, poach_slices, fish_out_item), hot-oil pour over a bowl (forearm hit the bowl in R17), drum loading.

## 西红柿炒蛋 (xihongshichaodan) sequence

Same calls as the executed build_day run05, regrouped by Wang Gang's 6 phases. Phase 4 uses the new `thicken` routine (drum release + stir with the gloss stop) where run05 used `drum_add_stir`.

| Phase | Routine | Params |
|---|---|---|
| prep | `mise_en_place` | {"tomatoes": 2, "cups": [{"what": "oil", "grams": 40}, {"what": "oil", "grams": 25}, {"what": "salt", "grams": 1}, {"what": "sugar", "gra… |
| 0 | `wok_grease` | {"oil_g": 40, "pour_out": true, "target_C": 150, "fresh_oil_g": 25} |
| 1 | `egg_set_and_hold` | {"target_C": 120, "level": 0.3, "still_s": 50, "flip_s": 30} |
| 2 | `add_stir_fry` | {"what": "tomato", "level": 0.3, "seconds": 45, "stroke": "dice"} |
| 2 | `drum_add_stir` | {"what": "ketchup", "grams": 5, "seconds": 20} |
| 3 | `drum_add_stir` | {"what": "water", "grams": 60, "seconds": 15} |
| 3 | `season_and_toss` | {"cups": ["salt 1 g", "sugar 1 g"], "level": 0.5, "seconds": 50} |
| 4 | `thicken` | {"sauce": "starch_water", "grams": 25, "level": 0.5, "max_s": 20} |
| 4 | `drum_add_stir` | {"what": "finishing_oil", "grams": 5, "seconds": 4} |
| 5 | `return_and_toss` | {"level": 0.5, "seconds": 8} |
| 5 | `take_out` | {"into": "plate"} |

Other egg / tomato dishes: 韭菜炒鸡蛋 (all demo / demo_ready), 蛋炒饭 (demo_ready except whites/yolks separated by the user), 茄汁糖醋里脊 (deep_fry in the fryer is needs_check; the sauce part is demo_ready).

## Notes

- 53 of the 57 types are used by at least one dish; the unused ones are `ladle_baste` and `wok_toss` (mapped to lid / stirring instead) and `prep_wash` (washing is not a phase in either source).
- `mise_en_place` is written out only for the egg dishes; the other dishes assume their cups and drum are loaded the same way, and their knife work is in the prep_* types (most are [missing] in R19_PREP_AUDIT).
- Every 颠锅 is mapped to scrape-stroke stirring; deep oil in the wok is moved to the fryer.
- Long simmer / braise phases use the half-power rule only when food is unstirred at > 0.5 heat; the boil-dry guard is a thermometer rise above ~110 °C.
- Statuses come from `results/r19/prim/library_size.json`; the per-dish mapping is a proposal and has not been run.
