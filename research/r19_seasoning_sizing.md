# R19 — Seasoning station sizing: fully automatic, less money, fewer arm motions

Date: 2026-10-13. The user said **"调料站你定，但肯定不是由人来做"**: seasoning dosing stays automatic, and the person never doses per meal. The orchestrator sizes the station.

Research was read-only (WebSearch and WebFetch only). There was no purchasing, no login and no seller contact. No existing file was changed.

**New files**
- `sim/r10/claude/r19seas_usage.py` → `results/r19seas/usage.json`: usage, forms, bursts, coverage.
- `sim/r10/claude/r19seas_options.py` → `results/r19seas/options.json`: per-option recipe coverage and the arm-move model.

**Tags**

| Tag | Meaning |
|---|---|
| **[M]** | Maker page or primary source. |
| **[O]** | Secondary page (shop, news, review). |
| **[O, snip]** | Seen only in a search-result snippet. Weaker. |
| **[1688 2026-10-13]** | 1688 market-page listing price read today. Wholesale or teaser price; retail is higher. **Unconfirmed.** |
| **[r14] / [r19]** | Taken from `research/r14_storage_market.md` / `r19_system_cost.md`, with their own sources. |
| **est.** | My estimate or judgement. |
| **ND** | No data. |

**Recipe inputs**
- **Main reference: the home-style cook (HS).** 15 dishes in 3 meals, from `homestyle_meals.json`.
  - That file has no structured seasoning events, so I hand-coded them from its step text. Each coded event quotes the step; the script checks every quote against the JSON.
  - He almost never states grams. Doses are what he says ("1 spoon", "a little"), otherwise ND.
- **Wider check: Wang Gang (WG).** 42 recipes, from `wanggang_recipes.json`. The grams are his own; 61 % of mentions have no amount.

---

## 0. Bottom line

1. **The recipes need a liquid bank, not a cup factory.**
   - 75 % of the home-style seasoning events go into the wok, or into wok water.
   - Of those wok events, **83 % are liquid only** once salt and sugar are pumped as liquids.
   - Add two small whole-spice portioners (干辣椒, 花椒) and a spice-sachet dropper at the wok, and **96 % of the wok-bound seasoning items need no arm move at all.**
   - Wang Gang: 74 % liquid; 86 % with the portioners.
2. **The channel count is not where the money is.**
   - A pumped channel costs about ¥200–600 in parts (est.).
   - The expensive and risky parts of today's station are:
     - 4 powder augers;
     - 2 paste syringes;
     - the stirred 0.1 g weighing cup;
     - the cup staging, which costs about 11–15 cups (33–45 arm moves) per home-style meal.
3. **Recommendation: option (d) — dose directly at the wok.**
   - **11 pumped channels:** oil, saturated brine, bought fructose syrup, 生抽, 老抽, 蒸鱼豉油, 料酒, 陈醋, 白醋, 蚝油, and a starch slurry made fresh each day.
     - 3 slots are kept for the Wang Gang set: MSG solution, 香油, 红油.
   - **Each bottle stands on its own load cell**, giving closed-loop "loss-in-weight" dosing and a low-stock alarm.
   - **A nozzle cluster over the wok** delivers the doses, with a short leg to the existing cabinet port for marinades.
   - **Other dosers:**
     - two whole-spice portioners and a 卤料包 sachet dropper at the wok;
     - a ¥13–37 electric pepper grinder at the port;
     - squeeze bottles, squeezed by the arm, for the rare pastes.
   - **Drop:** the augers, the syringes, the stirred weighing cup and most robot cups.
4. **Effect on the home-style meals (model):**
   - **Seasoning arm moves per meal: 12 / 3 / 6.** Today's design with the drum needs 18 / 27 / 24; R19's cup-only accounting gives 33 / 45 / 42 (≈ 4–5.5 min per meal).
   - **Dishes that need no hand-filled kit: 14 of 15**, against 10 of 15 today. Only "a little 十三香" in 干锅土豆 is missing.
   - **Wang Gang check: 34 of 42 dishes**, against 18 of 42 today.
5. **Parts cost (est.):**
   - **¥4.5–12.5k** with 11 channels, **¥5.1–14.3k** with 14, against **¥7.3–17.6k** today [r19].
   - The saving is moderate. **The main gains are fewer arm motions, no powder or paste mechanisms, and full automation.**
6. **No bought unit can replace the build** (§3). Bought *components* replace the risky custom modules:
   - pumps, pinch valves, load cells and stirrers;
   - a pepper grinder;
   - 15 g 卤料包 sachets;
   - fructose syrup instead of home-made sugar syrup, and 鸡汁 instead of 鸡精 powder.

---

## 1. Seasoning usage

**Column key**
- **HS:** dishes out of 15. "wok / off" splits uses: into the wok (including blanch water and the fryer) versus a bowl, plate, stew cup or soup pot.
- **WG g:** Wang Gang's stated grams per addition, as min / median / max (n). Salt doses above 20 g (the 椒盐 batch, the poaching pot) and 挂糊 coating starch (≥ 40 g, a staple) are excluded.
- **multi:** uses in an event with ≥ 2 seasonings, out of all uses.
- **burst:** wok uses within ≤ 5 s of the previous or next wok addition. These are his gaps, mostly estimated (`gap_basis`).
- **+arom:** uses added together with fresh 葱姜蒜.

| Seasoning | Form | HS /15 | HS wok / off | HS dose said | WG /42 | WG g min/med/max (n) | WG multi | WG burst | WG +arom | Proposed handling |
|---|---|---|---|---|---|---|---|---|---|---|
| Cooking oil | oil | **11** | 14 / 1 | "1 spoon"; deep-fry "wide oil" | 22 (under-reported) | ND (1 stated) | — | 10 | 4 | pump from the 5 L jug |
| 盐 | granular, soluble | **10** | 9 / 3 | "1 spoon", "a little per cup" | 38 | 0.5 / 2 / 7 (28) | 48/58 | 13 | 7 | saturated brine (26.4 % [r14]) |
| 生抽 (incl. 酱油) | thin liquid | 5 | 4 / 1 | "a little" | 28 | 2 / 4 / 25 (23) | 17/31 | 12 | 4 | pump |
| 干辣椒 | whole spice, light, bulky | 4 | 3 / 1 | ND | 10 | 5 / 15 / 80 (4) | 10/11 | 6 | 4 | portioner (cell wheel) |
| 白糖 | granular, soluble | 3 | 2 / 1 | ND (also 糖色) | 31 | 1 / 7.5 / 55 (12) | 32/34 | 12 | 3 | fructose syrup (sub, est.) |
| 淀粉 / 水淀粉 | powder, insoluble | 3 | 1 / 2 | "2 spoons", "plenty" | 23 | 3 / 5 / 25 (7) | 21/32 | 6 | 0 | daily slurry, stirred |
| 蚝油 | viscous liquid | 3 | 2 / 1 | "1 spoon" in half a bowl of water | 9 | 2 / 5 / 10 (7) | 7/9 | 4 | 1 | wide-bore pump, chilled |
| 陈醋 (dark vinegars) | thin liquid | 3 | 1 / 2 | ND | 5 (+5 unspecified) | 1 / 2 / 20 (3) | 3/6 | 2 | 1 | pump |
| 蒸鱼豉油 | thin liquid | 3 | 0 / 3 | ND | 0 | ND | — | — | — | pump (HS only) |
| 胡椒粉 | powder, insoluble | 2 | 0 / 2 | ND | 16 | 1 / 2 / 4 (4) | 20/20 | 4 | 0 | electric grinder |
| 料酒 | thin liquid | 2 | 3 / 0 | ND | 12 | 3 / 15 / 30 (11) | 13/17 | 3 | 2 | pump |
| 老抽 | thin liquid (dark) | 1 | 0 / 1 | ND | 15 | 1 / 2.5 / 5 (6) | 14/18 | 4 | 0 | pump |
| 花椒 | whole spice | 1 | 1 / 0 | ND | 14 | 3 / 3 / 30 (3) | 13/16 | 7 | 6 | portioner |
| 白醋 / 米醋 | thin liquid | 1 | 1 / 0 | ND | 10 | 1 / 1 / 20 (5) | 7/10 | 2 | 0 | pump |
| 豆瓣酱 | chunky paste | 1 | 1 / 0 | "a little" | 7 | 3 / 4.5 / 10 (4) | 1/7 | 1 | 0 | squeeze bottle (arm) |
| 八角, 桂皮 (香叶, 草果, 小茴香) | whole spice pieces | 1 | 1 / 0 | ND | 2, 1 (1, 1, 1) | ND | — | 0 | yes | 15 g 卤料包 sachet (sub, est.) |
| 十三香 | powder blend | 1 | 1 / 0 | "a little" | 0 (五香粉 1) | ND | — | — | — | not covered (omit, or a 2nd grinder) |
| 糖桂花酱 | syrup with flowers | 1 | 0 / 1 | drizzle | 0 | ND | — | — | — | squeeze bottle (arm) |
| 味精 | granular, soluble | **0** | — | — | 19 | 1 / 1 / 2 (13) | 19/19 | 8 | 2 | WG slot: 30 % solution |
| 鸡精 | powder | **0** | — | — | 7 | 0.5 / 1 / 2 (6) | 7/7 | 2 | 0 | WG: MSG channel or 鸡汁 (sub, est.) |
| 泡椒 (minced) | wet pickled solids | 0 | — | — | 6 | 15 / 20 / 30 (3) | 1/6 | 1 | 4 | squeeze bottle (剁椒-type), est. |
| 猪油 | semi-solid fat | 0 | — | — | 5 | ND | 2/5 | 1 | 4 | cooking oil (sub, est.) |
| 冰糖 / 糖色 | lumps / intermediate | 0 | — | — | 4 / 3 | 20 / 25 / 30 (2) | — | 0–2 | 0 | syrup (sub, est.) |
| 红油, 花椒油, 香油 | oils | 0 | — | — | 4, 3, 4 | 5–20 | — | 1–2 | 0–3 | WG slots (红油 settles; stir) |
| 甜面酱, 番茄酱, 黄豆酱, 芝麻酱 | pastes | 0 | — | — | 3, 2, 1, 1 | 3–50 | — | ≤ 1 | — | squeeze bottles (arm) |
| Tail: 豆豉 2, 泡姜 1, 芽菜 1, 辣椒面 1, 五香粉 1, 火锅底料 1, homemade 刀口辣椒 / 椒盐粉 / 鱼酱油 / 葱油 | various | 0 | — | — | 1–2 each | — | — | — | — | not covered (8 WG dishes) |

Fresh aromatics are prep, not seasoning: WG uses 蒜 in 27 dishes, 葱 in 22 and 姜 in 20 [`wanggang_recipes.md`]. In HS they appear in nearly every wok dish.

**What the table says**
- **He premixes.** He puts the liquids for a dish into one bowl: 鱿鱼 sauce, 土豆丝 调味水, 西兰花 sauce, 白灼汁. Per meal there are only 8–10 seasoning events, or 11–15 counting the oil-only events (A 11, B 15, C 14).
- **Home-style is simpler than Wang Gang.** There is no MSG or 鸡精 at all, little powder (pepper only, and only off-wok), 1 paste use and 1 braise with whole spices.
  - The sauces for steamed or blanched dishes (丝瓜, 鲈鱼, 白灼汁) are poured over the plate together with hot oil from the wok.
- **Wang Gang's bursts are mostly liquids.** His typical end burst is 盐 + 味精 → 生抽 (edge) → 明油 → 葱, within about 10–15 s [`wanggang_recipes.md`].
  - The burst items are salt (13), 生抽 (12), sugar (12), oil (10), MSG (8), 花椒 (7) and 干辣椒 (6).
  - 花椒 and 干辣椒 usually go in **with the aromatics** (6/16 and 4/11 uses in the same event; most of the rest in the next 3–10 s).
- **Event statistics** (`r19seas_options.py`, d-type routing):

| | Events | Wok-bound | All-liquid wok events | Wok-bound items that are liquid | … + wok-side portioners / sachet |
|---|---|---|---|---|---|
| HS (15 dishes) | 40 | 30 (75 %) | 25 (83 %) | 37/45 (82 %) | 43/45 (**96 %**) |
| WG (42), 14-channel set | 187 | 158 (84 %) | 101 (64 %) | 214/288 (74 %) | 247/288 (**86 %**) |

## 2. Coverage curve (top N seasonings)

**Definitions**
- **Ranking:** by the number of HS dishes; ties are broken by WG dishes. Liquid forms count as the seasoning they replace (brine = 盐).
- **Uses covered:** (dish, seasoning) pairs covered.
- **Dishes full:** every seasoning of the dish is in the top N.
- **"+subs":** the dish also counts as covered if a missing item has an accepted substitute inside the top N (est., my judgement): 冰糖/糖色 → sugar, 鸡精 → MSG, 蒸鱼豉油 → 生抽 + sugar, 猪油/葱油 → oil, 花椒面 → 花椒, homemade 椒盐/刀口辣椒 → their parts.

Top-N order (HS ranking): oil, 盐, 生抽, 干辣椒, 白糖, 淀粉, 蚝油, 陈醋, 蒸鱼豉油, 胡椒粉, 料酒, 老抽, 花椒, 白醋, 豆瓣酱, 八角, 桂皮, 十三香, 糖桂花酱, 味精 …

| N | HS uses covered | HS dishes full (strict / +subs) | WG uses covered | WG dishes full (strict / +subs) |
|---|---|---|---|---|
| 4 | 53 % | 3 / 3 of 15 | 30 % | 2 / 3 of 42 |
| **6** | 63 % | 4 / 5 | 46 % | 3 / 5 |
| **8** | 74 % | 5 / 8 | 50 % | 4 / 6 |
| **10** | 82 % | 9 / 9 | 55 % | 4 / 7 |
| **12** | 88 % | 11 / 11 | 64 % | 4 / 7 |
| **16** | 95 % | 12 / 12 | 74 % | 7 / 12 |
| 20 | 100 % | 15 / 15 | 80 % | 8 / 21 |

The same with WG's own ranking (盐, 白糖, 生抽, 淀粉, oil, 味精, 胡椒粉, 老抽, 花椒, 料酒, 干辣椒, 白醋, 蚝油, 豆瓣 …): WG uses covered are 49 / 58 / 66 / 72 / 81 % at N = 6 / 8 / 10 / 12 / 16, with 5 / 7 / 7 / 10 / 19 of 42 dishes full (+subs).

**Reading the curve**
- **Uses saturate quickly**, at about 88 % of HS uses by N = 12. **Whole dishes do not**: almost every dish has one rare item (a whole spice, a paste or a pickle).
- **More pump channels do not close that tail.** Cheap, generic mechanisms do:
  - one portioner per whole spice (干辣椒, 花椒);
  - a sachet for the braise spices;
  - squeeze bottles for pastes;
  - a grinder for pepper.
- With them, an 11-liquid bank covers **14/15 HS dishes**. With 3 more liquid channels it covers **34/42 WG dishes**.
- **The WG dishes still not covered** (8) need 豆豉, 泡姜, 芽菜, 辣椒面, 五香粉, 火锅底料 or homemade 刀口辣椒 / 椒盐粉. Each appears in 1–2 recipes.

## 3. Market: commodity automatic dispensers (domestic first)

| Product / class | Channels | Accuracy | Interface | Price | Fit | Src |
|---|---|---|---|---|---|---|
| 添可 食万 3.0 Pro (Chiere One abroad) | 8 liquid (water, oil, brine, 生抽, 老抽, wine, vinegar, syrup), built into its own pot | "weighing + pump"; 1 g scale [r14] | Brand app only | ¥3,990 [r14] | **No**: not standalone. The user mixes the brine and syrup | [r14]; [O] https://www.jiemian.com/article/11593621.html ; [O] https://idsa.org/?p=96754 |
| SAUCEIN S1 (重庆, 2026) | 5 liquid + 4 solid "base seasonings" as freeze-dried capsules | ND | ND (voice mentioned) | ND ("affordable") | **No**: proprietary capsules; per-dish consumables | [O] https://english.liangjiang.gov.cn/2026-06/08/c_1189039.htm |
| 山东华毅 group-catering doser HY-DISP-ROBOT-001 | 10 liquid / 6 powder; paste to order | gram level ((C) model: 0.1 g) | Touchscreen, PC, phone; no API documented | ¥28,000 list | **No**: costs more than the DIY build, no robot interface, size unpublished | [r14] (zycfcy.com) |
| 鸿博智成 调料机器人 | powder + liquid | ND | IR one-touch | ND | Lead only; nothing published | [M] https://www.szhbzc.com/pengjiagongxilie/32-25.html |
| Tea-shop multi-material machine (e.g. ZS-P40) | up to 18 materials | ±0.2 g (weighing) | 10.1" touchscreen | ND | **No**: 1,800 × 750 × 1,406 mm | [O, snip] cpttm.org.mo catalogue (PDF not text-readable) |
| Tea-shop 果糖机, 16 keys | 1 syrup | 5–200 cc ± 0.5 cc [O, snip] | Buttons; one touchscreen model | ¥245–728; touchscreen ¥3,980 [1688 2026-10-13] | Only as a sugar channel; no better than a ¥133–442 pump | https://www.1688.com/market/-B9FBCCC7BBFA.html |
| Aquarium Wi-Fi dosers: Jebao DP-2…5; Kamoer X4 Pro | 2–5 / 4 channels | Kamoer "< ±0.5 %", 150 ml/min [O, snip]; Jebao ≈100 ml/min [O, snip] | Wi-Fi cloud app plus buttons. **Local API: ND** | Jebao ¥425–443 per unit, DOSER 3.1 ¥157 [1688 2026-10-13]; X4 Pro US$489–569 [O, snip] | Cheapest pump bank per channel (≈ ¥85–110), **but** cloud-only control and no food-contact declaration (ND) | https://www.1688.com/market/-57494649C8E4B6AFB1C3.html ; https://www.marinedepot.com/kamoer-x4-wifi-dosing-pump |
| Lab pumps with RS485 / Wi-Fi | 1 | — | RS485 / Wi-Fi / app (雷弗 BT103S) | ¥2,863 (雷弗), Kamoer KXP100 ¥617.5 [1688 2026-10-13] | Too expensive per channel | same page |
| Bare stepper / DC peristaltic pumps | 1 each | Kamoer KCS ±10 % open loop; KCM to 600 ml/min [r14] | Your own driver | ¥85–460; Kamoer ¥133 entry [1688 2026-10-13]; KAS ¥248.9 … KCS ¥441.75 [r19] | **Yes**: the building block | https://www.1688.com/market/-B2BDBDF8B5E7BBFAC8E4B6AFB1C3.html |
| Desktop powder auger fillers | 1 | ND; 10–100 g range | Buttons | ¥3,000 [1688 2026-10-13]; ZONESUN 0.1–10 g US$3,400 [r14] | **No**: wrong dose range, or too costly | https://www.1688.com/market/-B7DBC4A9B6A8C1BFBBFA.html |
| Electric pepper grinders | 1 powder (ground fresh) | ND | Battery/USB; button or gravity switch (relay-triggerable, est.) | ¥13–37 [1688 2026-10-13] | **Yes** for pepper: whole peppercorns cake less than powder (est.) | https://www.1688.com/market/-B5E7B6AFBAFABDB7D1D0C4A5C6F7.html |
| 卤料包 / 炖肉料包 sachets | 15 g single-serve non-woven pouches (八角, 桂皮, 香叶, 花椒 …) | pre-portioned | none | ¥0.40–0.46 each [1688 2026-10-13] | **Yes** for braises: the robot drops the whole pouch | https://www.1688.com/market/-C2B1C1CFB0FC.html |
| Smart pet feeder (Tuya Wi-Fi, 4 L) | 1 dry portioner | ND | Tuya app | ¥138 [1688 2026-10-13] | Donor mechanism for a chili/花椒 portioner. **Not food-certified (ND)** | https://www.1688.com/market/-B3E8CEEFCEB9CAB3C6F7.html |
| 定量出油机 / 酱料定量机 / 自动投料机 | — | — | — | ¥75–125,000 | **No home product**: lubrication pumps, filling lines, fish-pond feeders. Matches [r14] ("electric gram-dosing oil dispenser … not found") | 1688 market pages read 2026-10-13 |
| Liquid substitutes | fructose syrup F55/F60, 2.5 kg; 鸡汁 1 kg | F55 ≈ 0.9–1.1× sucrose sweetness [O, snip] | — | syrup ¥13–52 per 2.5 kg; 鸡汁 ¥7–59 per kg (家乐 ¥58) [1688 2026-10-13] | **Yes**: no sugar syrup to mix (and less risk of crystallising, est.); 鸡汁 replaces 鸡精 powder | https://www.1688.com/market/-B9FBCCC7322E356B67.html ; https://www.1688.com/market/-BCA6D6AD.html |
| Station parts | pinch valve 12/24 V for 3–8 mm tube; load cell; HX711; magnetic stirrer | — | — | valve ¥100–170; cell ¥3.8–49 (ZEMIC 1 kg ¥148); HX711 kit ¥5.98; stirrer ¥43–95 [1688 2026-10-13] | building blocks | 1688 market pages 电磁夹管阀, 称重传感器1kg, 磁力搅拌器 |
| Commercial cooking robots | built-in seasoning lines (智谷天厨 15, Botinkit 16 [r14]) | — | — | ¥30–50k, some ¥120k [O] | Not sold separately; dose **directly into the wok** — the pattern for option (d) | [O] https://news.qq.com/rain/a/20241217A034ZE00 ; [r14] |

**Answer:** no bought unit can replace the custom build. Each one fails for at least one of these reasons:
- it is closed, app- or capsule-only (Tineco, SAUCEIN);
- it is restaurant-sized with no robot interface (华毅, tea machines);
- it is a single channel (果糖机).

**Two cautions from labels and recipes**
- **Oyster sauce:** Lee Kum Kee says to refrigerate it after opening and use it within 8 weeks [O, snip: ocado / morrisons product pages]. Its bottle needs a chilled compartment, and a small reservoir.
- **Starch slurry:** it keeps "up to 2 days" even refrigerated [O] https://feelgoodfoodie.net/recipe/how-to-make-slurry/. So it must be made by the station each cooking day, not by the user.

## 4. Options (all fully automatic)

**Moves:** seasoning-related arm moves per home-style meal A / B / C, and WG per dish (median / p90), from `r19seas_options.py`. These are bookkeeping estimates, not checked paths:
- cup = 3 moves (≈ 22 s, R14 rates);
- drum = 3 moves per ≤ 4 compartments;
- dish bowl to the port and back = 2 moves;
- squeeze bottle = +2 moves;
- nozzle, wok-side portioner or sachet dropper = 0 moves.

**Coverage:** dishes needing no user-filled kit, out of 15 HS and 42 WG.

| Option | What | Parts (CNY) | Moves per HS meal A/B/C (s) | WG moves per dish | Coverage HS / WG | Cleaning | Main failure risks |
|---|---|---|---|---|---|---|---|
| **(a) Today (R14)** | 12 peristaltic + oil pump, 4 augers, 2 syringes, 花椒 feeder, stirred 0.1 g cup, cups + drum. Rare items in a user-filled weekly kit. | **7.3–17.6k** [r19] + about 19 actuators to build and qualify | **18 / 27 / 24** (132 / 198 / 176 s) with the drum. Cup-only accounting [r19]: 33 / 45 / 42 (242 / 330 / 308 s) | 6 / 9 | **10 / 18**. The kit (干辣椒 in 4 HS dishes, 八角/桂皮, 十三香, 糖桂花; 泡椒, 豆豉 …) is per-meal user dosing, which is **no longer allowed** | 12 tubes, 4 augers, 2 syringes, feeder, stir cup; ≈ 11–15 cups per meal | Powder caking at 70–90 % RH (NaCl critical RH 75 %, sucrose 86 % [r14]); chunky 豆瓣 clogs the syringe; 66 % sugar syrup crystallises at the tip (est.); the 番茄酱/黄豆酱 cartridge swap needs the user; slurry settles |
| **(b) Right-sized, cups kept** | 11 liquids (oil, brine, fructose syrup, 生抽, 老抽, 蒸鱼豉油, 料酒, 陈醋, 白醋, 蚝油, slurry); 2 whole-spice portioners; pepper grinder; sachet magazine; squeeze bottles; port scale; cups + drum | **3.4–10.0k** (est., §5 parts), +0.3–0.8k for the add-ons e3/e4 that it also needs | 22 / 27 / 24 (162 / 198 / 176 s) | 6 / 10 | **14 / 16**; **14 / 34** with +MSG, 香油, 红油 | 11 tubes, 2 portioners, grinder; ≈ 11–15 cups per meal | No augers or syringes. Left: slurry, brine crust, chili bridging in the hopper. Cup staging stays (the "uncounted ≈ 20 cup moves" of R19) |
| **(c1) Commercial doser + custom extras** | 华毅-class 8–10 liquid / 6 powder into cups, plus portioners and squeeze bottles | ≈ **29–31k** (¥28k list [r14] + est.) | as (a) | as (a) | ≈ (b) minus whole spices; pastes to order | as the maker specifies | No API; size unknown; powders still cake |
| **(c2) Aquarium Wi-Fi dosers as the pump bank** of (b) or (d) | 3 × 4–5-channel units instead of bare pumps | pumps ≈ ¥1.3k instead of ¥1.5–4.9k (saves ≈ ¥0.2–3.6k) | as (b) or (d) | as (b) or (d) | as (b) or (d) | as (b) | Cloud-app control (no local API found); DC-motor accuracy for small doses ND; no food-contact declaration (ND) |
| **(d) Direct dosing at the wok (recommended)** | Liquids from (b) through a **nozzle cluster over the wok**; one tip angled at the wall for 锅边淋 (17 WG dishes); **each bottle on a load cell**; 干辣椒 / 花椒 portioners and the sachet dropper **at the wok**; HS plate sauces made in the wok and tipped over the dish with the hot oil (the R16 hot-oil pour already exists); marinades, stew cups and the soup pot via the cabinet port (6 pinch-valve diverters), or held under the nozzle with the heat off (single-outlet variant) | **4.5–12.5k** (11 ch), **5.1–14.3k** (14 ch); single outlet −¥0.6–1.0k (est., §5) | **12 / 3 / 6** (88 / 22 / 42 s) | 5 / 7 (3 / 7 with 14 ch) | **14 / 16**; **14 / 34** with 14 ch | 11–14 tubes (suck-back after every dose; water flush); nozzle tips get steam and oil splatter (daily wipe, est.); 2 portioners; ≈ 1–4 cups per meal | Nozzle place vs spatula strokes and the 23 cm hood gap (**sim check**); drips; hot tips may gel the slurry (heat shield, est.); brine crust (flush); burst speed needs ≥ 100–600 ml/min pumps run in parallel (KCS at 15–80 ml/min is too slow for 30 g); load-cell drift from tube drag (est.) |
| **(e) Add-ons that make (b) or (d) work** | e1: loss-in-weight bottles. e2: bought liquid forms (fructose syrup; brine kept saturated by excess salt crystals; 鸡汁). e3: daily slurry made by the station (dry-starch cell wheel + water channel, stirred cell; leftovers flushed into the wok before its rinse). e4: chilled compartment (Peltier) for 蚝油 and slurry. e5: water channel from a user-filled jug through the nozzle (small water; possibly the 1 L wok fill at 600 ml/min ≈ 100 s unattended, est.). e6: plate sauces made in the wok | e1 ¥10–55/ch; e3 ≈ ¥200–500; e4 ≈ ¥150–400 (est.); e5 one pump | e5 could also remove the wok-to-tap fill trips (part of R19's 6.1 min fill/dump per 3 meals) | — | e2 and e6 are substitutions (taste: est.) | e3 adds a stirred cell to rinse | e2 fructose 糖色 browns differently (test); e3 starch caking in its hopper (critical RH ND [r14]) |

**Other effects of (d)**
- **Spatula idle time.** R15 found it falls from a median 36 % to 13 % when seasonings are dispensed at the wok instead of fetched by the arm [`README_R10.md` R15, Evidence 4]. Option (d) gets the same effect without loading drums.
- **The R14/R15 pour drum becomes optional for seasonings.** It can stay for aromatics; that is the movement track's call.
- **Where the remaining moves are, in (d):**
  - meal A: the 豆瓣 and 糖桂花 squeeze-bottle doses (5 moves each) and the stew-cup salt (2);
  - meal B: soup-pot salt (3);
  - meal C: two marinades (2 each) and soup salt via the port.

## 5. Recommendation: what I would build

**Build option (d) with add-ons e1–e4 (and e5 if a jug water channel is acceptable). Install 11 channels now, with 3 empty slots for the Wang Gang set.**

| Part | Qty | Unit (CNY) | Basis | Subtotal (CNY) |
|---|---|---|---|---|
| Peristaltic pumps: oil, brine, fructose syrup, 生抽, 老抽, 蒸鱼豉油, 料酒, 陈醋, 白醋, 蚝油 (wide bore), slurry. KCM-class (≥ 100–600 ml/min) for oil, syrup, wine, vinegar, slurry | 11 (+3: MSG solution, 香油, 红油) | 133–442 | [1688 2026-10-13], [r19] | 1,460–4,860 (+400–1,330) |
| Drivers, food-grade tube (silicone with GB 4806.16 declaration, or BPT [r14]), bottles, fittings | 11 (+3) | 50–100 | est. | 550–1,100 (+150–300) |
| Loss-in-weight load cell + HX711 under each bottle (dose by weight with a slow final trickle; low-stock alarm) | 11 (+3) | 10–55 | [1688] | 110–600 (+30–165) |
| Nozzle cluster: stainless tips, one rim-aimed tip, bracket under the hood front, drip shield | 1 | 100–300 | est. | 100–300 |
| Pinch-valve diverters to the cabinet port for brine, 生抽, 老抽, 蚝油, slurry, oil (0 in the single-outlet variant) | 6 | 100–170 | [1688] | 600–1,020 |
| Daily slurry cell: magnetic stirrer + cup; dry-starch cell-wheel doser; water from the jug channel | 1 | 43–95 + 150–400 | [1688] + est. | 190–500 |
| Chilled compartment (Peltier) for 蚝油 and slurry | 1 | 150–400 | est. | 150–400 |
| Whole-spice portioners at the wok (干辣椒段, 花椒): agitated cell wheel; a pet-feeder mechanism as donor | 2 | 150–400 | est. (feeder ¥138 [1688]) | 300–800 |
| 卤料包 sachet magazine with a servo gate at the wok | 1 | 50–150 | est.; sachets ¥0.40–0.46 [1688] | 50–150 |
| Electric pepper grinder + relay, at the port, on the scale | 1 | 23–67 | [1688] + est. | 23–67 |
| Squeeze bottles: 豆瓣, 甜面酱, 番茄酱, 糖桂花, 剁椒 | 5 | 5–20 | est. | 25–100 |
| Port weighing spot (1 kg cell + HX711; ZEMIC grade at most) | 1 | 10–150 | [1688] | 10–150 |
| Controller (MCU, 14 stepper drivers, valve and servo I/O), enclosure | 1 | 500–1,500 | est. | 500–1,500 |
| Drum + holder + about 6 cups, kept for aromatics and the rare cup | — | 400–1,000 | [r19] row 28, est. | 400–1,000 |
| **Total** | | | | **≈ 4.5–12.5k (11 ch); ≈ 5.1–14.3k (14 ch)** |

**Why (d)**
- **It is fully automatic for the reference meals.**
  - 14/15 dishes; only 十三香 is missing. Use a 2nd grinder with 十三香-style whole spices, or leave it out of 干锅土豆.
  - 34/42 Wang Gang dishes with the 3 extra channels.
  - There is no per-meal kit. The person only refills bottles, tops up the brine jug with salt and water, and reloads the sachets, squeeze bottles and spice hoppers, like groceries.
- **It has the fewest arm motions:**
  - 3–12 seasoning moves per meal, against 18–27 (today with the drum) or 33–45 (R19 cup accounting);
  - it removes the cup-staging family at the port almost entirely;
  - bursts need no drum load.
- **It is cheaper than today:** ≈ ¥3–4k less in parts at mid-range (¥8.5k for 11 channels against ¥12.5k).
- **It has fewer risky custom parts.** The 4 augers, 2 syringes and the 花椒 vibratory feeder go; their caking and clogging risks were R14's main unproven items.
- **Accuracy:**
  - Loss-in-weight closes the loop on every liquid dose without a cup. HX711 noise is ≈ 0.05–0.2 g rms (est. [r14]), against the needed ±0.5 g for liquids. For brine that is ≈ ±0.05 g of salt.
  - Powder-level accuracy (±0.2 g) is needed only for pepper, which is weighed at the port.

**What to drop from the R14 station:** the 4 powder augers (鸡精, 胡椒, 花椒面, 玉米淀粉), both syringe extruders, the 花椒 vibratory feeder, the stirred 0.1 g weighing cup, the user's weekly kit, the 66 % sucrose syrup and most robot cups.

**Checks before building (none done)**
1. **Sim:** nozzle cluster and wok-side portioners under the hood front against the R15 stir strokes, the plume rule and the 23 cm hood gap. Also the single-outlet variant: a bowl held under the nozzle with the heat off.
2. **Bench, with real liquids:**
   - loss-in-weight accuracy with tube drag for 蚝油 (and 30 °C cabinet temperature);
   - brine crust at the tip;
   - slurry settling and gelling at a warm tip;
   - burst timing with parallel pumps.
3. **Bench:** cell-wheel portioning of real 干辣椒段 and 花椒 (bridging, dose spread). Pepper-grinder output per second and caking in a humid kitchen.
4. **Taste checks for the substitutions:** fructose syrup (including 糖色), 卤料包 for 八角/桂皮, sauces made in the wok, 鸡汁 or MSG for 鸡精 (WG only).

**For the user to confirm**
1. **Restocking.** The person restocks only bulk containers: about 11–14 bottles, the brine jug (salt + water), spice hoppers, sachets and squeeze bottles. Is that acceptable?
2. **Substitutions.** Are the substitutions above acceptable, and may 十三香 be omitted?
3. **Water.** May the station hold a user-filled water jug, so small water and the slurry are dosed automatically?
4. **Wang Gang slots.** Fit the 3 Wang Gang channels (MSG, 香油, 红油) now or later?

## 6. Method notes and gaps
- **The moves are a bookkeeping model** (`r19seas_options.py` docstring), not planned paths. Rates follow R14 `timeline14.py` (6 + 8 s staging, 8 s pour).
- **The HS events are hand-coded.** Uses of oil and water are partly implicit in his videos. Doses are ND except his spoons.
- **WG gaps are mostly estimated** from his wording [`wanggang_recipes.md`].
- **Prices:**
  - All 1688 figures are wholesale or teaser listings read on 2026-10-13, **unconfirmed**.
  - No Taobao, JD or Tmall page was read (browser automation was not allowed).
  - Labour and qualification are not priced.
- **Not found:**
  - a home multi-channel seasoning doser with an open API;
  - SAUCEIN S1 price and interface;
  - local-control APIs for Jebao or Kamoer Wi-Fi dosers;
  - pepper-grinder output rates;
  - starch-slurry shelf life at room temperature;
  - critical RH of 鸡精 and starch;
  - viscosities of 老抽, 豆瓣酱, 甜面酱 and fructose syrup;
  - Peltier box and controller prices (est.).
