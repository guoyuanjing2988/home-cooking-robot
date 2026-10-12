# Wang Gang (美食作家王刚) — cooking actions for a home cooking robot

Generated 2026-10-11. Data: `wanggang_cooking.json` (42 recipes, 258 phases). Companion to `wanggang_recipes.md` (seasoning events).

## Method

- **Source.** Same 42 videos as the seasoning pass. 23 have zh subtitles (his narration). 19 have only the channel's en translation.
- **Phase.** One vessel doing one thing. Quick additions in the same vessel at the same heat are merged.
- **Scope.** Heat steps, soaks in hot water, cold mixing and plating. Cutting, marinating and egg beating are left out.
- **No invention.** Unknown amounts and times are `null`. His wording is kept (适量, 'some', 'until fragrant').
- **Quotes.** Every phase has a verbatim quote with its subtitle cue number. A script checked all 280 quote fragments against the .srt files: 0 mismatches.
- **Durations.** `stated` = he gives the time. `est` = my estimate from his wording:
  - `few_stirs`: 翻炒几下 / 翻几下 / a few (couple of) stirs / give a little stir ≈ 3 s
  - `mix`: 炒匀 / 拌匀 / until well mixed ≈ 10 s
  - `fragrant`: 炒香 / 炒出香味 / 炒出红油 / until fragrant or coloured ≈ 20 s (range 10–30)
  - `thicken`: starch sauce (碗汁/水淀粉) poured into the hot wok until it thickens ≈ 10 s
  - `just_cooked`: 断生 / 变色 / until just cooked (shredded or thin items) ≈ 30 s (range 20–60)
  - `video_1take`: read from timestamps of an uncut one-take video (干煸四季豆, 手撕包菜 only). Other videos are edited, so video time is not used.
- **Temperatures.** `stated` or `conv`: his 6成 ≈ 180 °C, other 成 at 30 °C per 成 (4成 = 120, 5成 = 150, 8成 = 240 °C).
- **Masses.** 1斤 = 500 g, 1两 = 50 g, thin liquids ≈ 1 g/ml. Food mass is the sum of stated masses; '≥' means some items were not weighed.
- **Variants.** Three videos teach extra variants (西兰花 白灼/蚝油, 炝炒油麦菜, 鲈鱼 进阶 sauce). They count for presence statistics, not for per-dish timing.
- **Vessel '锅 unspecified'.** He often says only 锅 for boiling or blanching. I did not guess wok vs pot.
- **'Toss'.** Only 蛋炒饭 (en-only video) says 'toss' (4 times). That may translate 翻炒. No zh transcript says 颠锅.

### Spot-check (5 random recipes, re-read against the transcript)

Picked with `random.seed(20261011)`: 黄焖鸡 (`huangmenji`), 葱爆羊肉 (`congbaoyangrou`), 京酱肉丝 (`jingjiangrousi`), 蚂蚁上树 (`mayishangshu`), 麻婆豆腐 (`mapodoufu`).

- **黄焖鸡**: 11 phases match cues #13–60 in order: 焯水 → 炸 potatoes 2 min → 炒糖色 小火 → chicken 2 min 中小火 → 料头 → 酱 1 min → 黄酒 from edge → 盖上锅盖焖 15 min 中火 → potatoes 小火 10 min → 汤汁浓稠 + 青红椒 断生. No change needed.
- **葱爆羊肉**: 6 phases match cues #45–64. Confirmed he never says when the lamb goes back in (kept as an ambiguity). No change needed.
- **京酱肉丝**: 5 phases match cues #33–56 (炒勺涮冷, 请勿翻动 until set, 炒散, excess oil out, 甜面酱 then water from the edge, 中小火 收汁). No change needed.
- **蚂蚁上树**: 7 phases match cues #4–36. Found one coding error: 'Cook on lower heat' was mapped to the same level as 'low heat', hiding a turn-down. Fixed: 'lower' now counts as a relative turn-down (heat changes 0 → 1).
- **麻婆豆腐**: 12 phases match cues #6–51, including the 4-minute 烧 with 水淀粉 at minutes 2, 3 (off the burner) and 4 (off heat) and the ladle push. No change needed.

## Aggregates

### 1. Vessels

| vessel | recipes |
|---|---|
| wok | 38 |
| bowl (soak / sauce) | 9 |
| deep oil in wok | 8 |
| 锅 unspecified (wok or pot) | 8 |
| bowl/plate (cold mixing) | 4 |
| steamer | 3 |
| other (heated) | 2 |
| pot | 1 |
| any wok use (wok or deep oil in wok) | 38 |

- 'other (heated)' = an oil-heating vessel he does not name, for 泼油 in 白切鸡 and 清蒸鲈鱼 (probably the wok).
- **Two heated vessels at the same time:** 0 stated. He works one burner at a time. Even 担担面 does the pork first, then the noodle water.
- **Two vessels in use together:** 1 stated. 白切鸡 / 口水鸡: hot 桶 (heat off) and a cold-water basin used alternately for the dip/lift cycles.
- **Needs hot water from a second heater (kettle or pot) while cooking:** 7 recipes. 清炒菠菜 / 炝炒油麦菜 (boiled water in the wok spoon); 红烧肉 (prepared boiling water); 脑花豆腐 (boiling water from a pot boiled in advance + salt); 蚂蚁上树 (hot water); 酸菜鱼 (hot water); 鸡蛋肉丝炒面 (≥90 °C water); 麻婆豆腐 (90 °C salted water).
- **Needs a steamer or pot besides the wok (used in sequence):** 4 recipes. 糖醋排骨 (steamer + wok + 锅 unspecified (wok or pot)); 鱼香茄子 (steamer + wok); 白切鸡 / 口水鸡 (other (heated) + pot); 清蒸鲈鱼 (other (heated) + steamer + 锅 unspecified (wok or pot)).
- **Boil/blanch in a 锅 he does not name** (could be the same wok): 8 recipes (糖醋排骨, 清炒西兰花 (+白灼/蚝油), 地三鲜, 担担面, 酸辣汤, 黄焖鸡, 清蒸鲈鱼, 土豆烧牛腩).
- 脑花豆腐 is served in a 煲仔 (clay pot) kept hot by an alcohol burner. It is a serving vessel, not a cooking one.

### 2. Manipulations

| manipulation | recipes | dishes |
|---|---|---|
| 翻炒 stir with spatula | 34 | 京酱肉丝, 可乐鸡翅, 回锅肉, 土豆烧牛腩, 地三鲜, 宫保鸡丁, 小炒肉, 小炒茄子(肉片), 干煸四季豆, 手撕包菜, 椒盐排骨, 水煮肉片 … |
| 颠锅 toss (en 'toss' only) | 1 | 蛋炒饭 |
| 翻面 flip single pieces | 4 | 可乐鸡翅, 红烧鲤鱼, 西红柿炒蛋, 酱油炒饭 |
| 划散 separate strands/pieces | 6 | 京酱肉丝, 干煸四季豆, 焦溜肉段, 葱爆羊肉, 青椒肉丝, 鸡蛋肉丝炒面 |
| 不动 leave to set first | 11 | 京酱肉丝, 回锅肉, 焦溜肉段, 红烧肉, 红烧鲤鱼, 茄汁糖醋里脊, 葱爆羊肉, 西红柿炒蛋, 韭菜炒鸡蛋, 鱼香肉丝, 鸡蛋肉丝炒面 |
| 推炒 gentle push | 3 | 脑花豆腐, 酸菜鱼, 麻婆豆腐 |
| 撇浮沫 skim | 4 | 可乐鸡翅, 土豆烧牛腩, 红烧肉, 酸菜鱼 |
| 捞出 lift out with strainer/ladle | 16 | 可乐鸡翅, 土豆烧牛腩, 地三鲜, 担担面, 椒盐排骨, 清炒西兰花 (+白灼/蚝油), 焦溜肉段, 白切鸡 / 口水鸡, 红烧肉, 红烧鲤鱼, 茄汁糖醋里脊, 葱爆羊肉 … |
| 舀汤浇 ladle / baste | 3 | 白切鸡 / 口水鸡, 红烧鲤鱼, 酸菜鱼 |
| 淋 along the wok edge (锅边) | 18 | 京酱肉丝, 回锅肉, 土豆烧牛腩, 地三鲜, 小炒肉, 小炒茄子(肉片), 手撕包菜, 炝炒/酸辣土豆丝, 红烧肉, 红烧鲤鱼, 葱爆羊肉, 蚂蚁上树 … |
| 晃锅 swirl oil (润锅/滑锅; 'swirl' said in 2) | 18 | 京酱肉丝, 回锅肉, 小炒肉, 小炒茄子(肉片), 水煮肉片, 红烧肉, 葱爆羊肉, 蚂蚁上树, 蛋炒饭, 西红柿炒蛋, 酱油炒饭, 酸菜鱼 … |
| 搅拌 stir a bowl or pot | 7 | 宫保鸡丁, 拍黄瓜, 白切鸡 / 口水鸡, 脑花豆腐, 酸辣汤, 鱼头豆腐汤, 鱼香肉丝 |
| 洗锅 wash wok mid-recipe | 3 | 小炒肉, 手撕包菜, 酸菜鱼 |
| lid on | 3 | 土豆烧牛腩, 糖醋排骨, 黄焖鸡 |

- 翻炒 without any toss: 33 of 34 stir-fry recipes.
- Lid: he states 盖上锅盖 in 黄焖鸡 and 土豆烧牛腩 (both 焖, and the 牛腩 pre-boil). 糖醋排骨 steamer lid is inferred ('你来打开'). Everything else: lid unknown.

### 3. Heat

- Heat changes per dish (primary variant, 41 heated recipes): median **1**, max **6** (回锅肉).
- A change = a new stated level (大火 / 中火 / 小火 / 关火 …) or 'turn up/down'. Preheat words (烧热, smoking hot) are not counted.
- 关火/离火 events: 19 in total. 13 are **mid-cooking** (food or sauce is handled off the heat). 6 are the final 关火 or end of a boil.

| dish | phase | what he does while off heat |
|---|---|---|
| 回锅肉 | 煮 | turn off the gas, move pork into cold water |
| 回锅肉 | 爆香 | wok off heat before 豆瓣 |
| 回锅肉 | 炒 (豆瓣 off heat) | 豆瓣 5 g added and stir-fried off the heat |
| 宫保鸡丁 | 滑油 | wok moved off the fire; chicken 滑油 in the cooling oil (热锅凉油) |
| 麻婆豆腐 | 勾芡 #2 | pan off the burner; 2nd 水淀粉 added |
| 麻婆豆腐 | 勾芡 #3 | pan off heat; 3rd 水淀粉 + gentle push with ladle |
| 清炒西兰花 (+白灼/蚝油) | 煮 + 勾芡 (拉丝芡 water) [蚝油] | 锅离火 while the starch is added |
| 小炒肉 | 滑油 (里脊, off heat) | wok off the fire; oil + meat added and 滑熟 in the residual heat |
| 辣子鸡 | 复炸 (off the stove) | whole second fry is done with the wok away from the stove ('for precise frying of the crust', #85) |
| 酸菜鱼 | 煮 (滑鱼片 in the soup) | 锅离火 while slices are added one by one |
| 酸辣汤 | 勾芡 (off heat) | 锅离火 while the starch is added and stirred in |
| 白切鸡 / 口水鸡 | 煮 (water + salt + 姜葱 to a boil, then 关火) | 火关掉 before the chicken goes in (big 桶 holds enough heat) |
| 土豆烧牛腩 | 爆香 (off heat: 草果/葱/姜/花椒 → 豆瓣 → 甜面酱) | 锅离火 for aromatics + 豆瓣 + 甜面酱; return to heat not stated |

**Stated temperatures (and 成 conversions)**

| dish | phase | °C | basis |
|---|---|---|---|
| 鱼香肉丝 | 炒 (肉丝 + 豆瓣) | 180 | stated |
| 宫保鸡丁 | 爆香 | 150 | conv:5成x30 |
| 麻婆豆腐 | 浸 (tofu in hot salted water) | 90 | stated |
| 西红柿炒蛋 | 煎 (eggs) | 120 | stated |
| 糖醋排骨 | 炸 | 195 | stated (大概190度 → 190度到200度) |
| 青椒肉丝 | 滑炒 (pork in lard) | 120 | stated |
| 青椒肉丝 | 爆香 | 150 | stated |
| 炝炒/酸辣土豆丝 | 爆香 | 180 | conv:6成x30 (he says 60%) |
| 干煸四季豆 | 煸 (beans, slow) | 120 | conv:4成x30 |
| 水煮肉片 | 爆香 | 170 | stated |
| 水煮肉片 | 爆香 (姜蒜泡椒) | 170 | stated |
| 水煮肉片 | 泼油 | 210 | stated |
| 可乐鸡翅 | 爆香 (ginger slices) | 150 | stated |
| 清炒西兰花 (+白灼/蚝油) | 泼油 (onto 蒜蓉 in a bowl) | 180 | conv:6成x30 |
| 清炒西兰花 (+白灼/蚝油) | 爆香 [清炒] | 150 | conv:5成x30 |
| 地三鲜 | 炸 | 180 | conv:6成x30 (he says 60%) |
| 风味茄子(烧茄子) | 炸 (in small batches) | 180 | stated (60% (~180C)) |
| 辣子鸡 | 炸 | 210 | stated |
| 辣子鸡 | 复炸 (off the stove) | 240 | stated |
| 辣子鸡 | 爆香 | 180 | stated |
| 酸菜鱼 | 炒 (辅料) | 180 | conv:6成x30 |
| 酸菜鱼 | 煎 (fish bones + head) | 180 | conv:6成x30 |
| 酸菜鱼 | 泼油 | 240 | conv:8成x30 |
| 茄汁糖醋里脊 | 炸 | 150 | conv:5成x30 |
| 茄汁糖醋里脊 | 复炸 | 200 | stated |
| 葱爆羊肉 | 炸 (葱心 in shallow oil) | 150 | conv:5成x30 |
| 红烧鲤鱼 | 煎 (whole fish) | 150 | conv:5成x30 |
| 鱼头豆腐汤 | 炸 (fish head, then 姜 and 葱 in the same oil) | 150 | conv:5成x30 |
| 椒盐排骨 | 炸 (ribs, set the shape) | 180 | conv:6成x30 |
| 椒盐排骨 | 复炸 (ribs) | 210 | stated |
| 椒盐排骨 | 爆香 (葱椒粒 in 猪油) | 180 | conv:6成x30 |
| 焦溜肉段 | 炸 (held at 160 °C) | 150 | stated (150度 in, 维持160度) |
| 焦溜肉段 | 复炸 | 200 | stated |
| 土豆烧牛腩 | 爆香 (off heat: 草果/葱/姜/花椒 → 豆瓣 → 甜面酱) | 150 | conv:5成x30 |
| 鸡蛋肉丝炒面 | 浸 (instant noodles) | 90 | stated (90度以上) |
| 酱油炒饭 | 煎/炒 (yolk, slow) | 120 | conv:4成x30 (he says 40%) |

**Time by heat level** (phases with a stated/est duration; seconds summed over all recipes; 'mixed' = the phase names 2+ levels)

| group | off | very low | low | med-low | medium | med-high | high | down(rel) | mixed | not stated |
|---|---|---|---|---|---|---|---|---|---|---|
| liquid / steam / soak | 2410 | 0 | 6000 | 600 | 1380 | 0 | 300 | 0 | 7800 | 15200 |
| stir/fry (active wok) | 181 | 300 | 1685 | 760 | 931 | 203 | 221 | 70 | 394 | 1567 |

- Most stir/fry seconds have **no stated flame level** at all. He steers by oil temperature (成) and by cues, not by a dial setting.

### 4. Durations

Active wok time = all wok and deep-oil phases except preheat/润锅, wok washing, and boils, braises or reductions of 5 min or more. Untimed phases count 0, so most sums are lower bounds.

| set | n | median | p90 | max |
|---|---|---|---|---|
| all dishes with some timed active phase (lower bound: untimed phases count 0) | 36 | 103.0 s | 373.0 s | 625 s (酸菜鱼) |
| dishes where every active phase has a time | 16 | 103.0 s | 272.5 s | 330 s (小炒茄子(肉片)) |

| longest | duration | dish | phase | basis |
|---|---|---|---|---|
| 焖/炖/烧 | 60 min | 红烧肉 | 烧 | stated |
| 焖/炖/烧 | 15 min | 黄焖鸡 | 焖 | stated |
| 焖/炖/烧 | 15 min | 土豆烧牛腩 | 焖 (beef + potato) | stated |
| 煮 | 60 min | 土豆烧牛腩 | 煮 (whole 牛腩) | stated |
| 煮 | 30 min | 回锅肉 | 煮 | stated |
| 煮 | 15 min | 鱼头豆腐汤 | 煮 (soup, gentle) | stated |
| 蒸 | 150 min | 糖醋排骨 | 蒸 (隔水蒸, ribs in a 盆 with seasoned water) | stated |
| 蒸 | 15 min | 鱼香茄子 | 蒸 | stated |
| 蒸 | 480 s | 清蒸鲈鱼 | 蒸 (fish on a plate on 姜葱) | stated |
| 浸 (hot/warm soak) | 40 min | 黄焖鸡 | 浸 (prep: dried 香菇 in warm water) | stated |
| 浸 (hot/warm soak) | 40 min | 白切鸡 / 口水鸡 | 浸 (steep off heat) | stated |
| 浸 (hot/warm soak) | 15 min | 蚂蚁上树 | 浸 (noodles in hot water) | stated |

### 5. Liquids

| g | dish | phase | vessel | basis |
|---|---|---|---|---|
| 2000 | 鱼头豆腐汤 | 煮 (soup, gentle) | wok | conv: '一般加四斤水' (1斤=500 g) |
| 600 | 可乐鸡翅 | 煮 (cola) | wok | stated (about 600g) |
| 500 | 红烧鲤鱼 | 煮 (beer sauce) | wok | stated (啤酒1瓶（500毫升）) |
| 140 | 焦溜肉段 | other: 溜 (碗汁 gelatinised on high heat, toss to coat) | wok | stated (鲜汤140克 in the 碗汁; + 米醋 20, 绍酒 15, 水淀粉 25, 生抽 25, 香油 10) |
| 40 | 鱼香肉丝 | 收汁 (碗汁 with starch) | wok | stated (清汤或者清水40克 in 碗汁; + 醋 20, 生抽 5) |
| 30 | 鱼香茄子 | 收汁 (鱼香汁 with starch) | wok | stated (30 g of water in the sauce) |
| 30 | 风味茄子(烧茄子) | 收汁 (碗汁 with starch) | wok | stated (water 30g in the sauce; soy 80 g as subtitled) |
| 30 | 葱爆羊肉 | 收汁 (碗芡) | wok | stated (清汤 30 g in the 料汁; + 料酒 30, 生抽 5, 老抽 5) |
| 30 | 红烧肉 | 炒糖色 | wok | stated (30g of water) |

- Max liquid in one vessel: **2000 g** (鱼头豆腐汤, converted from 四斤水).
- Dishes with ≥ 500 g liquid in the wok/pot (stated): 可乐鸡翅, 红烧鲤鱼, 鱼头豆腐汤.
- Large liquids given only as a level, not a mass: 红烧肉 (level: 1 cm over the meat (mass not stated)); 白切鸡 / 口水鸡 (not weighed ('两大盆水'; '水一定要够多 一定要把鸡肉淹下去')); 土豆烧牛腩 (level: '水大概加入大半锅或者8分满' (mass not stated)); 土豆烧牛腩 (level: '适量的清水没过牛肉').

### 6. Wok load (stated food mass in the wok)

- 22 dishes have a stated mass. Max **1150 g** (椒盐排骨); median **355.0 g**. Raw weights; many are lower bounds.

| dish | g in wok |
|---|---|
| 椒盐排骨 | 1150 |
| 红烧鲤鱼 | 900 |
| 糖醋排骨 | 750 |
| 鱼香茄子 | 715 |
| 回锅肉 | 685 |
| 青椒肉丝 | 540 |
| 麻婆豆腐 | 450 |
| 炝炒/酸辣土豆丝 | 400 |
| 干煸四季豆 | 400 |
| 酸菜鱼 | 380 |
| 脑花豆腐 | 380 |
| 鱼香肉丝 | 330 |
| 西红柿炒蛋 | 300 |
| 水煮肉片 | 300 |
| 京酱肉丝 | 300 |
| 蚂蚁上树 | 285 |
| 小炒肉 | 270 |
| 葱爆羊肉 | 250 |
| 辣子鸡 | 230 |
| 小炒茄子(肉片) | 200 |
| 担担面 | 150 |
| 韭菜炒鸡蛋 | 130 |

### 7. Oil handling

- **润锅 oil poured out:** 16 dishes (京酱肉丝, 回锅肉, 小炒肉, 水煮肉片, 红烧肉, 葱爆羊肉, 蚂蚁上树, 蛋炒饭, 西红柿炒蛋, 酱油炒饭, 酸菜鱼, 青椒肉丝, 韭菜炒鸡蛋, 鱼香肉丝, 鱼香茄子, 麻婆豆腐).
- 润锅 oil kept or not said: 小炒茄子(肉片), 鸡蛋肉丝炒面.
- **Excess oil poured off mid-recipe** (after rendering, 滑炒 or frying): 9 dishes (京酱肉丝, 干煸四季豆, 椒盐排骨, 焦溜肉段, 红烧肉, 茄汁糖醋里脊, 葱爆羊肉, 风味茄子(烧茄子), 黄焖鸡).

**滑油 / 炸 / 复炸 phases**

| dish | phase | oil g | °C | s |
|---|---|---|---|---|
| 宫保鸡丁 | 滑油 | 750 | —  | — |
| 糖醋排骨 | 炸 | '不要加得太宽 稍微窄一点' (not weighed) | 195 (stated (大概190度 → 190度到200度)) | — |
| 地三鲜 | 炸 | 'a lot of oil' (not weighed) | 180 (conv:6成x30 (he says 60%)) | 80 |
| 小炒肉 | 滑油 (里脊, off heat) | 植物油 1勺 (not weighed) | —  | — |
| 风味茄子(烧茄子) | 炸 (in small batches) | deep oil (not weighed) | 180 (stated (60% (~180C))) | 60 |
| 辣子鸡 | 炸 | 'a s**tload of oil' (not weighed) | 210 (stated) | 60 |
| 辣子鸡 | 复炸 (off the stove) | same oil | 240 (stated) | 20 |
| 茄汁糖醋里脊 | 炸 | 宽油 (not weighed) | 150 (conv:5成x30) | 120 |
| 茄汁糖醋里脊 | 复炸 | — | 200 (stated) | 90 |
| 葱爆羊肉 | 炸 (葱心 in shallow oil) | 适量的冷油 | 150 (conv:5成x30) | — |
| 黄焖鸡 | 炸 (potatoes in 底油) | 适量的底油 | —  | 120 |
| 鱼头豆腐汤 | 炸 (fish head, then 姜 and 葱 in the same oil) | 500 | 150 (conv:5成x30) | — |
| 椒盐排骨 | 炸 (ribs, set the shape) | 宽油 (not weighed) | 180 (conv:6成x30) | 60 |
| 椒盐排骨 | 炸 (蒜蓉) | — | —  | — |
| 椒盐排骨 | 复炸 (ribs) | — | 210 (stated) | 180 |
| 焦溜肉段 | 炸 (held at 160 °C) | 宽油 (not weighed) | 150 (stated (150度 in, 维持160度)) | — |
| 焦溜肉段 | 复炸 | — | 200 (stated) | 20 |

**泼油 (hot oil poured over the dish)**

| dish | °C | how |
|---|---|---|
| 水煮肉片 | 210 (stated) | hot oil poured from the wok over the bowl |
| 清炒西兰花 (+白灼/蚝油) | 180 (conv:6成x30) | hot oil poured into the garlic bowl; sauce then 淋 over the unmolded broccoli |
| 酸菜鱼 | 240 (conv:8成x30) | oil ladled out with 炒勺 and splashed on the fish in one go |
| 白切鸡 / 口水鸡 | not stated  | |
| 清蒸鲈鱼 | not stated  | hot oil then 鱼酱油 poured over the fish |

**Oil reuse**

- 鱼头豆腐汤: 姜/葱 fried in the 500 g oil so it loses the fish smell and 'can be used a second time'. "还可以用第二次" [#94]
- 辣子鸡: same oil for 炸 and 复炸; debris cleaned out between. "and clean up the debris" [#55]
- 焦溜肉段: same oil for 炸 and 复炸; impurities cleared between. "再清除油里面的杂质" [#53]
- 椒盐排骨: same 宽油 for ribs → garlic → ribs again. "蒜蓉炸好之后重新把油温升至210度" [#62]
- 茄汁糖醋里脊: same oil for 炸 and 复炸. "重新把油温升至200度" [#41]
- 担担面: rendered pork lard reused to loosen the 芝麻酱. "加入适量炒肉末的猪油把芝麻酱化开" [#20]
- 干煸四季豆: he criticises restaurants frying beans in reused black oil. "就是炸四季豆这个油非常的黑" [#146]

### 8. Endpoint cues

| cue | phase mentions | recipes | sensor needed | examples |
|---|---|---|---|---|
| time | 74 | 32 | timer | simmer for 30 min (回锅肉); for 1 min (回锅肉); about 8 seconds ... home kitchen ... 15 seconds (回锅肉) |
| smell | 43 | 30 | none direct (gas sensor or time+temp proxy) | When you can smell the flavors (回锅肉); till the smells come out (回锅肉); 翻炒出香味 (鱼香肉丝) |
| texture | 42 | 29 | camera (+probe) | When the garlic sprouts are cooked (回锅肉); 肉丝成熟 (鱼香肉丝); 葱粒断生 (鱼香肉丝) |
| temperature | 40 | 26 | thermometer | when the wok is hot (回锅肉); 锅烧热 (鱼香肉丝); 6成热（约180度） (鱼香肉丝) |
| other | 38 | 24 | varies | When it's well mixed (回锅肉); After mixing it well (西红柿炒蛋); To make the oil out of pork belly (红烧肉) |
| colour | 37 | 23 | camera | until golden brown (回锅肉); This will give the meat color (回锅肉); Dried chilies must be sauteed until brown (宫保鸡丁) |
| bubbles | 27 | 17 | camera | rock sugar will bubble up ... large bubbles become small bubbles (红烧肉); boil (红烧肉); 让这个泡 / 让它顶上来 (糖醋排骨) |
| thickness | 25 | 21 | camera | 见到汤汁浓稠 (鱼香肉丝); to reduce the sauce (宫保鸡丁); to slightly thicken it (麻婆豆腐) |
| shape | 12 | 12 | camera | the meat will curl up (回锅肉); 肉丝底部成型 (鱼香肉丝); until egg is consolidated (西红柿炒蛋) |
| smoke | 11 | 10 | camera | smocking hot (回锅肉); until it starts smoking (宫保鸡丁); When you see fog coming up (青椒肉丝) |
| probe | 6 | 6 | probe / force | easily penetrate the pork with a chopstick (回锅肉); 看骨头抽得出来不 / 都脱骨了 (糖醋排骨); pierced easily by a chopstick (地三鲜) |
| taste | 4 | 3 | taste / salinity | 你尝哈咬得动不 (糖醋排骨); 尝哈看甜味够不 (糖醋排骨); 尝一下 (鱼头豆腐汤) |
| liquid_level | 2 | 2 | camera | over the pork belly one centimeter (红烧肉); 起码这个原材料 / 它要露出来至少30-40%了 (脑花豆腐) |
| sound | 1 | 1 | microphone | 听到声音没 / 呼 呼 呼的 (白切鸡 / 口水鸡) |
| oil_clarity | 1 | 1 | camera | 收这个汁一定要把油要收亮一点再出菜 (脑花豆腐) |

- Need **vision**: 157 cue mentions in 41 recipes (colour, thickness, bubbles/foam, shape-set, smoke/锅气, oil clarity, liquid level, texture).
- Need a **thermometer**: 40 mentions (26 recipes). 34 give a number (°C, 成 or %) in 22 recipes; the rest are 'wok hot' / 冒青烟 / '有点热' preheat judgements.
- Need **taste/salinity**: 4 mentions (糖醋排骨, 脑花豆腐, 鱼头豆腐汤).
- Need a **probe / force**: 6 mentions (回锅肉, 土豆烧牛腩, 地三鲜, 椒盐排骨, 白切鸡 / 口水鸡, 糖醋排骨): chopstick pierce, pinch the leg, bone pulls out, chili crumbles.
- **Smell** (43 mentions, 30 recipes) has no direct sensor. The robot must replace 炒香 with time + oil temperature.
- **Sound**: 1 mention (白切鸡 cavity filling). **Weight**: no cue relies on a scale; liquids are given as levels ('1 cm over the meat', '8分满', '没过牛肉').
- Vision-heavy examples: 勾芡 consistency (汤汁浓稠, 20厘米拉丝, 锅底 dry when pushed, 油亮), 糖色 stages (big → small bubbles, light yellow → reddish brown), 'black foam only', 鱼汤浓白, 原材料露出30–40% before 勾芡.

### 9. Plating

| method | recipes | dishes |
|---|---|---|
| wok→plate (出锅装盘; pour/scoop not specified) | 18 | 鱼香肉丝, 麻婆豆腐, 西红柿炒蛋, 青椒肉丝, 清炒西兰花 (+白灼/蚝油), 地三鲜, 小炒肉, 辣子鸡, 茄汁糖醋里脊, 京酱肉丝, 葱爆羊肉, 蛋炒饭, 小炒茄子(肉片), 黄焖鸡, 椒盐排骨, 焦溜肉段, 土豆烧牛腩, 鸡蛋肉丝炒面 |
| not stated | 14 | 回锅肉, 宫保鸡丁, 红烧肉, 糖醋排骨, 炝炒/酸辣土豆丝, 干煸四季豆, 可乐鸡翅, 风味茄子(烧茄子), 鱼香茄子, 蚂蚁上树, 手撕包菜, 韭菜炒鸡蛋, 清炒菠菜 / 炝炒油麦菜, 酱油炒饭 |
| pour hot oil / sauce over the plated food | 5 | 水煮肉片, 清炒西兰花 (+白灼/蚝油), 酸菜鱼, 红烧鲤鱼, 清蒸鲈鱼 |
| pour/ladle from wok into a bowl or clay pot | 3 | 酸辣汤, 鱼头豆腐汤, 脑花豆腐 |
| scoop/ladle components into a bowl | 2 | 水煮肉片, 酸菜鱼 |
| arrange on plate | 2 | 拍黄瓜, 白切鸡 / 口水鸡 |
| invert bowl (扣碗) | 1 | 清炒西兰花 (+白灼/蚝油) |
| assemble in bowl (noodles + toppings) | 1 | 担担面 |
| lift whole fish onto plate | 1 | 红烧鲤鱼 |
| steamed on its serving plate | 1 | 清蒸鲈鱼 |

- 'wok→plate (出锅装盘)' = he says plate it but not how. In practice this is a tilt-and-scrape of the wok.

### 10. Steps one arm cannot do alone

`explicit` = he asks a second person. `inferred` = the quoted step needs two things held at once.

| dish | what | quote [cue] | basis |
|---|---|---|---|
| 宫保鸡丁 | hold the wok away from the fire while putting chicken in and stirring it in the oil | Move the wok away from the fire once the oil is in / Put the chicken in and fry it to 80% done [#36-37] | inferred |
| 麻婆豆腐 | hold the pan off the burner while pouring starch slurry and pushing the tofu with a ladle (x2) | At the third minute, take the pan off the burner. / For the second time, add a small amount of starchy water to thicken it. [#45-46] | inferred |
| 糖醋排骨 | a helper pours the broth into the wok while he cooks | 四伯爷 帮我倒一下 / 啊 不要倒完了 [#112-113] | explicit (second person) |
| 地三鲜 | pour the whole wok of hot oil + food out and filter it (wok in one hand, strainer/oil container in the other) | Pout them all out of the pot and filter the oil. [#27] | inferred |
| 小炒肉 | hold the wok off the fire while adding oil and meat and moving it (滑熟 off heat) | 锅烧热烧透之后离火 / 加入植物油1勺 / 然后把腌制好的里脊肉下锅滑熟 [#44-46] | inferred |
| 风味茄子(烧茄子) | drain fried eggplant and pour the hot oil out of the wok | after that, take out and drain the eggplants / and pour out the hot oil [#35-36] | inferred |
| 辣子鸡 | hold a wok of 240 °C oil away from the stove while adding and frying the chicken for 20 s, then strain it | Take the wok away from the stove / Fry the chicken for a second time for 20 seconds [#58-59] | inferred |
| 辣子鸡 | lift chicken out with a strainer while holding the wok / clean debris | Now filter out the chicken with a strainer / and clean up the debris [#54-55] | inferred |
| 酸菜鱼 | hold the wok off the fire while adding fish slices one by one | 然后将锅离火 / 锅离火之后再把腌制好的鱼片依次下锅 [#94-95] | inferred |
| 酸菜鱼 | pour the soup from the wok into the 盆 while holding back the dregs | 大火烧开之后再把鱼汤倒入盆中 / 请大家注意最后有一些渣必须将其分离开 [#101-102] | inferred |
| 茄汁糖醋里脊 | lift and separate fried pieces with a 漏勺 while holding the wok | 两分钟之后再用漏勺捞出分散 / 里脊分散之后将其捞出 [#39-40] | inferred |
| 京酱肉丝 | pour excess oil out of the wok while holding the meat back | 肉丝炒熟炒散之后再倒出锅中多余的油 [#44] | inferred |
| 白切鸡 / 口水鸡 | lift a whole chicken out of hot water and tip its cavity water out, then dunk it in a second basin | 然后提起来把它肚子里面的水倒出来 [#93] | inferred |
| 白切鸡 / 口水鸡 | helper heats the oil for 泼油 while he cuts | 好 等我切好你烧点油给它浇一下 [#303] | explicit (second person) |
| 红烧鲤鱼 | flip a whole 900 g fish in the wok without breaking it | 然后中途将其翻面过来继续煎香 [#26] | inferred |
| 红烧鲤鱼 | lift the braised whole fish out onto a plate intact | 6分钟之后将鲤鱼捞出摆盘 [#47] | inferred |
| 清蒸鲈鱼 | hold the garnish shreds aside with chopsticks while tipping the plate juices out | 首先把姜葱丝和辣椒丝用筷子夹起 / 再倒出盘中的汤汁和“鱼酱油” [#45-46] | inferred |
| 清蒸鲈鱼 | pour the boiled sauce through a strainer onto the fish | 最后过滤出残渣之后再重新淋在鱼身上面即可 [#48] | inferred |
| 清炒菠菜 / 炝炒油麦菜 | hold the wok spoon with salt/sugar while pouring boiled water into it, then tip it into the wok | add some seasonings such as salt and white sugar into the wok spoon / Then add some boiled water into the spoon [#25-26] | inferred |
| 脑花豆腐 | pour tofu + brain slowly from the soak bowl into the wok without breaking them | 脑花和豆腐一起倒出来 / 一定要慢一点 / 这个一下子倒出来的话会把它冲烂 [#168-170] | inferred |
| 脑花豆腐 | shake the starch bowl, pour a little, then push in the wok, 4 rounds | 轻轻给它晃一下 / 然后倒一点下来 / 加下去了再推 [#260-267] | inferred |

## Per-recipe phase tables

Columns: vessel · action · heat (°C) · time · lid · food/liquid/oil g · hands · done when · out · quote [cue#]. `alt` = alternative variant. Full quotes and all fields are in the JSON.

### 1. 回锅肉 — `huiguorou`

Video `v72yoabCHXA` · transcript en · heat changes 6 · active wok ≥ 145 s (1 untimed) · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 煎 (烙皮: dry-sear the skin) | smoking hot → medium heat | — | | 500 / — / — | 不动 | smoke: smocking hot, colour: until golden brown | pork lifted out and cleaned in water | Prepare pork rear leg 500 g and put it skin-side down int… [#6-7] |
| 2 | wok | 煮 | bring it to boiling → simmer → turn off the gas | 30 min | | 500 / — / — | | time: simmer for 30 min, probe: easily penetrate the pork with a chopstick | turn off gas; pork moved into cold water to cool, then patted dry and sliced 2 mm | Bring it to boiling and then simmer for 30 min. [#18] |
| 3 | wok | 预热/润锅 | heat up the wok | — | | — / — / — | 晃锅 | temperature: when the wok is hot | excess oil poured out | Lubricate some oil when the wok is hot. [#41-43] |
| 4 | wok | 煸 | medium-small heat | 60 s | | 500 / — / — | 翻炒 | time: for 1 min, shape: the meat will curl up | | Stir fry under medium-small heat for 1 min. [#44] |
| 5 | wok | 爆香 | medium-small heat → remove from the heat | 20 s est | | — / — / — | 翻炒 | smell: When you can smell the flavors | | When the meat curled up, add in some fermented black soyb… [#46-47] |
| 6 | wok | 炒 (豆瓣 off heat) | off heat | 20 s est | | — / — / — | 翻炒 | colour: This will give the meat color | | Then add 5 g of chili bean sauce to stir fry. [#48] |
| 7 | wok | 爆香 | medium-small heat | 20 s est | | — / — / — | 翻炒 | smell: till the smells come out | | Stir fry under medium-small heat till the smells come out. [#51] |
| 8 | wok | 炒 (sauce + seasoning) | | 10 s est | | — / — / — | 翻炒, 淋 | other: When it's well mixed | | Then add the sauce. [#52-57] |
| 9 | wok | 炒 | medium heat | 15 s | | 685 / — / — | 翻炒 | texture: When the garlic sprouts are cooked, time: about 8 seconds ... home kitchen ... 15 seconds | dish ready (plating method not stated) | It only take about 8 seconds to cook the garlic sprouts. [#61-62] |

### 2. 鱼香肉丝 — `yuxiangrousi`

Video `t-gEVqs_Fg0` · transcript zh-Hans · heat changes 0 · active wok ≥ 103 s · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | 把锅烧热 | — | | — / — / — | 晃锅 | temperature: 锅烧热 | 热油倒出 | 锅烧热之后加入适量的油滑锅 [#44-45] |
| 2 | wok | 炒 (肉丝 + 豆瓣) | (180 °C) | 30 s | | 300 / — / — | 不动, 翻炒 | temperature: 6成热（约180度）, shape: 肉丝底部成型, time: 翻炒30秒, texture: 肉丝成熟 | | 把油温烧至6成热（约180度） [#47-51] |
| 3 | wok | 爆香 | | 10 s | | — / — / — | 翻炒 | smell: 翻炒出香味, time: 大约10秒钟 | | 姜蒜末下锅之后必须翻炒出香味 [#52-53] |
| 4 | wok | 炒 (葱粒) | | 60 s | | — / — / — | 翻炒 | time: 大概需要1分钟左右, texture: 葱粒断生 | | 家庭小灶这一步大概需要1分钟左右 [#54-55] |
| 5 | wok | 收汁 (碗汁 with starch) | | 3 s est | | 330 / 40 / — | 搅拌, 翻炒 | thickness: 见到汤汁浓稠, smell: 闻到醋香味 | 出锅装盘 | 最后料汁下锅翻炒几下 [#58-60] |

### 3. 宫保鸡丁 — `gongbaojiding`

Video `wEkVkT6IU9M` · transcript en · heat changes 2 · active wok ≥ 36 s (2 untimed) · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | fryer/deep oil in wok | 滑油 | until it starts smoking → away from the fire | — | | — / — / 750 | other | smoke: until it starts smoking, texture: fry it to 80% done | chicken drained ("put them aside to drain the oil"); fate of the 750 g oil not stated | Then add around 750 grams of cooking oil [#35-37] |
| 2 | wok | 爆香 | (150 °C, conv) | 23 s est | | — / — / — | 翻炒, 翻炒 | temperature: Once the oil is 50% hot, smell: Saute until aromatic, colour: Dried chilies must be sauteed until | | Once the oil is 50% hot we add the chilies and peppers [#41-42] |
| 3 | wok | 炒 (chicken back) | Turn up the heat | — | | — / — / — | 翻炒 | |  | Turn up the heat and saute so that the chicken can absorb… [#44] |
| 4 | wok | 收汁 (碗汁 with starch) | high heat | 10 s est | | — / — / — | 搅拌, 翻炒 | thickness: to reduce the sauce | | Add the sauce after stirring them well [#45-46] |
| 5 | wok | 炒 (花生/葱/红油) | | 3 s est | | — / — / — | 翻炒 | | done (plating method not stated) | Finish with some chili oil and give them a little stir an… [#48] |

Two hands / helper: hold the wok away from the fire while putting chicken in and stirring it in the oil (inferred)

### 4. 麻婆豆腐 — `mapodoufu`

Video `RU-0vjjvSiI` · transcript en · heat changes 5 · active wok ≥ 396 s (1 untimed) · plating: wok→plate (method not stated)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bowl | 浸 (tofu in hot salted water) | (90 °C) | 300 s | | 400 / — / — | | time: soak for 5 minutes | water drained | Pour almost boiling water(90°C) into the bowl. [#6-7] |
| 2 | wok | 预热/润锅 | After the pan heats up | — | | — / — / — | 晃锅 | temperature: After the pan heats up | excess oil poured out | After the pan heats up add an appropriate amount of oil t… [#25-26] |
| 3 | wok | 煸 (beef) | low heat | 60 s | | 50 / — / — | 翻炒 | time: for 1 minute | | Then stir-fry the diced beef on low heat for 1 minute. [#28] |
| 4 | wok | 炒 (花椒) | high heat | 60 s | | — / — / — | 翻炒 | time: for a minute | | After a minute add an appropriate amount of Sichuan pepper. [#29-30] |
| 5 | wok | 炒 (豆瓣 + 豆豉) | low | 20 s est | | — / — / — | 翻炒 | colour: until the oil is red | | Then continue frying on low until the oil is red. [#34] |
| 6 | wok | 爆香 (姜蒜葱 + 辣椒面) | low | 3 s est | | — / — / — | 翻炒 | |  | Stir fry on low a little. [#36] |
| 7 | wok | 煮 (water + seasoning) | | — | | — / — / — | |  | | After the spicy pepper is fried, add an appropriate amoun… [#37] |
| 8 | wok | 烧 (tofu) | low heat | 120 s | | 450 / — / — | | time: At the second minute | | Then we will cook the tofu for four minutes on low heat. [#42-43] |
| 9 | wok | 勾芡 #1 | low heat | 60 s | | — / — / — | 淋 | thickness: to slightly thicken it, time: At the third minute | | Add an appropriate amount of starchy water to the center … [#44] |
| 10 | wok | 勾芡 #2 | take the pan off the burner → low | 60 s | | — / — / — | 淋 | thickness: to thicken it, time: At the fourth minute | | At the third minute, take the pan off the burner. [#45-46] |
| 11 | wok | 勾芡 #3 | remove the pan from the heat | 10 s est | | — / — / — | 淋, 推炒 | thickness: Once thickened | | At the fourth minute on low, we will again remove the pan… [#47-49] |
| 12 | wok | 淋 (花椒油) | | 3 s est | | — / — / — | 淋 | | plate the dish (method not stated); garnish sprinkled on the plate | Finally, pour in a little Sichuan pepper oil. You can the… [#51] |

Two hands / helper: hold the pan off the burner while pouring starch slurry and pushing the tofu with a ladle (x2) (inferred)

### 5. 西红柿炒蛋 — `xihongshichaodan`

Video `2hvQFxZBTVY` · transcript en · heat changes 0 · active wok ≥ 143 s · plating: wok→plate (method not stated)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | Heat up the wok | — | | — / — / — | 晃锅 | | oil poured out | Heat up the wok [#11-13] |
| 2 | wok | 煎 (eggs) | low heat (120 °C) | 60 s | | — / — / — | 不动, 翻面 | temperature: When oil is heated to 120°C, time: fry for 1 minute, shape: until egg is consolidated | egg taken out (returned at the end) | When oil is heated to 120°C, add in the beaten egg mix. [#15-18] |
| 3 | wok | 炒 (tomato + ketchup) | low heat | 10 s est | | 300 / — / — | 翻炒 | other: After mixing it well | | Add chopped tomato, fry them in low heat. [#20-21] |
| 4 | wok | 煮/焖 | | 60 s | | 300 / — / — | | time: simmer for 1 min, texture: Cook until tomatoes are soft | | After mixing it well, add adequate amount of water and si… [#22] |
| 5 | wok | 勾芡 + 明油 | | 10 s est | | — / — / — | 淋 | thickness: After it's thickened | | Cook until tomatoes are soft, add some starch water mix t… [#26-27] |
| 6 | wok | 炒 (eggs back) | | 3 s est | | — / — / — | 翻炒 | | ready to be plated (method not stated) | Finally, add the fried eggs, mix it a few times, and it i… [#28] |

### 6. 红烧肉 — `hongshaorou`

Video `K0_6YfqXYhA` · transcript en · heat changes 5 · active wok ≥ 80 s (5 untimed) · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 煎 (烙皮: dry-sear skin) | heat the pot | — | | — / — / — | 不动 | colour: into golden yellow | pork fished out, washed in clean water, cut | Then we put the streaky pork skin down into the pot [#4-5] |
| 2 | wok | 炒糖色 | low heat → turn down the fire to very low | — | | 30 / 30 / — | | bubbles: rock sugar will bubble up ... large bubbles become small bubbles, colour: light yellow ... dark yello | | Then put the rock sugar in the pot and cook on low heat t… [#17-22] |
| 3 | wok | 煮 (糖色 + boiling water) | | 60 s | | — / — / — | | time: continue to boil for a minute | 糖色 poured into a bowl and set aside | Add the prepared boiling water and continue to boil for a… [#24-26] |
| 4 | wok | 焯水 | high heat | — | | — / — / — | 撇浮沫 | bubbles: boil | pork poured out (drained) | boil with high heat and remove the foam [#31-32] |
| 5 | wok | 预热/润锅 | Heat the pot | — | | — / — / — | 晃锅 | | hot oil poured out; cold oil added | Heat the pot and add some oil [#33-34] |
| 6 | wok | 煸 (render fat) | medium heat | — | | — / — / — | 翻炒 | other: To make the oil out of pork belly | excess oil poured out | Then we put the pork belly into the pot and fry it with m… [#36-39] |
| 7 | wok | 爆香 | low heat | 20 s est | | — / — / — | 翻炒 | smell: until you smell the fragrance | | fry them with low heat until you smell the fragrance [#41] |
| 8 | wok | 炒 (酱油 from side) | | — | | — / — / — | 淋 | other: Fry for a while | | Add 5g soy sauce, pour in from the side of the pot [#42-43] |
| 9 | wok | 烧 | low heat | 60 min | | — / — / — | 捞出 | time: 60 minutes, liquid_level: over the pork belly one centimeter | | It's best to pour the water over the pork belly one centi… [#44-46] |
| 10 | wok | 收汁 | medium low fire | 10 min | | — / — / — | | time: for 10 minutes, colour: until it becomes bright red, thickness: Thicken the soup | finished (plating method not stated) | Thicken the soup with medium low fire for 10 minutes [#50-51] |

Note: en subtitle says 'pot' (锅); the same vessel is used for searing, 糖色, blanching, frying and braising, so it is recorded as wok. Pork belly mass not stated.

### 7. 糖醋排骨 — `tangcupaigu`

Video `slckZcok4eo` · transcript zh-Hans · heat changes 1 · active wok ≥ 0 s (2 untimed) · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok/pot (锅 unspecified) | 焯水 | | — | | 750 / — / — | |  | 倒出来 (poured out) | 先给排骨焯下水 [#20-29] |
| 2 | steamer | 蒸 (隔水蒸, ribs in a 盆 with seasoned water) | | 150 min | on | 750 / — / — | | time: 蒸2个小时 / 有条件的话可以蒸3个小时 / 整了两个半小时, probe: 看骨头抽得出来不 / 都脱骨了, taste: 你尝哈咬得动不 | ribs and broth kept; broth reused for the 收 stage | 隔水蒸 [#46-49] |
| 3 | wok | 炸 | (195 °C) | — | | 750 / — / — | | temperature: 把油烧到大概190度, texture: 主要目的是把这个皮炸硬, colour: 你看 炸到这个样子 | not stated (ribs then returned to the wok: '直接把这个排骨放进来') | 然后把油烧到 [#91-108] |
| 4 | wok | 收汁 (炸收) | 稍微中小火 → 转小火 | — | | 750 / — / — | | colour: 深一点红一点, bubbles: 让这个泡 / 让它顶上来, taste: 尝哈看甜味够不, thickness: 汤汁儿越收越浓 | | 然后放这个汤 [#111-150] |

Two hands / helper: a helper pours the broth into the wok while he cooks (explicit (second person))

Note: Blanching vessel not named (冷水下锅). Fry duration not stated (earlier pass estimated ~2 min). Oil amount only '稍微窄一点'.

### 8. 青椒肉丝 — `qingjiaorousi`

Video `wn0_7SMpw6o` · transcript en · heat changes 2 · active wok ≥ 93 s · plating: wok→plate (method not stated)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | Heat the pan up | — | | — / — / — | 晃锅 | | hot oil poured out | Put some oil in it and pour out the hot oil. This makes t… [#27] |
| 2 | wok | 滑炒 (pork in lard) | Turn down the heat (120 °C) | 30 s est | | 300 / — / 40 | 划散 | temperature: When oil temperature reaches 120 °C, colour: When they change color, texture: separated and cooke | pork removed ('put them away for later steps'), returned later | When oil temperature reaches 120 °C (248 °F) stir in mari… [#30-32] |
| 3 | wok | 爆香 | Turn down the heat (150 °C) | 20 s est | | — / — / — | 翻炒 | temperature: heat it up to 150 °C, smell: until they are fragrant | | Add some more lard, and heat it up to 150 °C (302 °F) [#33-35] |
| 4 | wok | 炒 (green pepper) | medium heat | 30 s est | | 200 / — / — | 翻炒 | texture: until it's no longer raw, colour: look shiny and soft | | Turn to medium heat. Stir the pepper until it's no longer… [#37-38] |
| 5 | wok | 炒 (pork back + seasoning) | | 10 s est | | 540 / — / — | 翻炒, 淋 | |  | Stir in the pork from earlier. [#39-42] |
| 6 | wok | 炒 (明油 finish) | medium heat | 3 s est | | 540 / — / — | 翻炒 | smoke: When you see fog coming up | ready to plate (method not stated) | Finally, add some cold oil, and quickly stir it a few tim… [#43-44] |

### 9. 炝炒/酸辣土豆丝 — `tudousi`

Video `9HbErcNKAIk` · transcript en · heat changes 3 · active wok ≥ 90 s · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 焯水 | high heat → medium | 20 s | | 400 / — / — | | bubbles: Once boiling, time: for 20 seconds, colour: starts becoming translucent | drained and set aside | Boil the water on high heat [#17-21] |
| 2 | wok | 爆香 | (180 °C, conv) | 20 s est | | — / — / — | | temperature: Heat it to 60%, smell: Once you can smell them | | Heat it to 60% [#24-26] |
| 3 | wok | 炒 (potato) | Turn heat to high | 40 s | | 400 / — / — | 翻炒 | time: 15 seconds ... home stove ... about 40 seconds, texture: cook the potato until just done | | Turn heat to high and stirfry 15 seconds [#27-29] |
| 4 | wok | 炒 (seasoning + scallion) | medium heat | 10 s est | | — / — / — | 淋, 翻炒 | other: When all seasonings are mixed well | serve (method not stated) | Add light soy sauce, 3ml, from the edge of the pan [#33-36] |

Note: Blanch water must leave the wok before the oil step; he does not say how (drain implied).

### 10. 干煸四季豆 — `ganbiansijidou`

Video `4WU7xDeRZQc` · transcript zh-Hans · heat changes 2 · active wok ≥ 305 s · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 煸 (beans, slow) | 开小一点 (120 °C, conv) | 183 s video_1take | | 400 / — / 100 | 翻炒 | temperature: 油温让它升到四成热, colour: 四季豆变色了之后 / 有点微微发黄, texture: 表皮发皱 / 煎到起壳 | excess oil poured off mid-way ('倒一点出来'); beans then out of the wok (not stated how) and re-added later | 大概这里是二两 [#131-159] |
| 2 | wok | 煸 (肉末) | 小火 | 36 s video_1take | | — / — / — | 划散 | other: 肉末好了之后 | | 肉末放进去给它 [#179-181] |
| 3 | wok | 爆香 (花椒 + 干辣椒) | 大火 | 44 s video_1take | | — / — / — | 翻炒 | colour: 爆到它褐色 / 就是快要发黑, smell: 已经闻到了这个灯笼椒的香味了 | | 然后把辣椒爆香 [#187-192] |
| 4 | wok | 炒 (蒜 to cool the wok) | | 3 s est | | — / — / — | 翻炒 | |  | 这个时候把蒜放下去 [#194-197] |
| 5 | wok | 炒 (beans back + seasoning) | 开大火 → 关火 | 39 s video_1take | | — / — / — | other, 翻炒 | other: 不要久炒 (MSG) | | 然后把四季豆放下去 [#198-212] |

Note: Beans leave the wok between 煸 and 肉末 but he does not say how. Durations from one-take (uncut) footage, labelled video_1take.

### 11. 水煮肉片 — `shuizhuroupian`

Video `hyiGCNwCMxU` · transcript en · heat changes 5 · active wok ≥ 110 s (3 untimed) · plating: scoop/ladle into bowl + 泼油

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | preheat the wok | — | | — / — / — | 晃锅 | | hot oil poured out | First preheat the wok and add some oil to swirl the wok. [#35-36] |
| 2 | wok | 煸 (dry chilies + 花椒 for 刀口辣椒) | small flame | 20 s est | | 18 / — / — | 翻炒 | smell: until you can smell the fragrance, colour: don't make them overcooked | peppers taken out and minced on the board | Fry the peppers until you can smell the fragrance with sm… [#37-39] |
| 3 | wok | 爆香 | (170 °C) | 20 s est | | — / — / — | 翻炒 | temperature: Heat the oil to 170C, smell: Once you can smell the fragrance | | Heat the oil to 170C. [#43-45] |
| 4 | wok | 炒 (vegetable bed) | full flame | 20 s | | 100 / — / — | 翻炒 | time: for 20 seconds | scooped into the bottom of the serving bowl | then fry them with full flame for 20 seconds. [#46-49] |
| 5 | wok | 爆香 (姜蒜泡椒) | with the heat (170 °C) | 20 s est | | — / — / — | 翻炒 | temperature: heat the oil to 170C, smell: until you smell fragrance | | the same, heat the oil to 170C and add the minced ginger,… [#52-53] |
| 6 | wok | 炒 (豆瓣 10 g) | small flame | 20 s est | | — / — / — | 翻炒 | colour: until the red oil appear | | Fry the douban sauce with small flame until the red oil a… [#55] |
| 7 | wok | 煮 (soup) | full flame → small flame | — | | — / — / — | | bubbles: Once the soup is boiling | | add some water. [#56-58] |
| 8 | wok | 勾芡 (light) | small flame | 10 s est | | — / — / — | | thickness: to slightly condense the soup | | last, add some mixture of potato starch and water to slig… [#63] |
| 9 | wok | 煮 (pork slices in soup) | medium flame | — | | 300 / — / — | | texture: Once the pork is ready | pork taken to the bowl, then some soup added (ladle) | then put the seasoned pork into wok. [#64-67] |
| 10 | wok | 泼油 | medium flame (210 °C) | — | | — / — / — | 淋 | temperature: heat the oil with medium flame to 210C | hot oil poured from the wok over the bowl | heat the oil with medium flame to 210C [#72-73] |

### 12. 可乐鸡翅 — `kelejichi`

Video `mmzoO7e4j-8` · transcript en · heat changes 3 · active wok ≥ 380 s (2 untimed) · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 爆香 (ginger slices) | heat up the wok (150 °C) | 20 s est | | — / — / — | 翻炒 | temperature: heated up to about 150 ﹞C, smell: until aromatic | | When the oil is heated up to about 150 ﹞C, put in the gin… [#14] |
| 2 | wok | 煎 (wings on a ginger bed) | low heat | 360 s | | — / — / — | 翻面 | time: for 6 minutes, colour: both sides of chicken wings are golden and crispy | | Fry the chicken wings for 6 minutes in low heat [#17-19] |
| 3 | wok | 煮 (cola) | high heat | — | | — / 600 / — | 撇浮沫 | bubbles: boil it in high heat, other: Notice the drizzling foam from cola itself ... remove the black foam | | After 6 minutes, pour in the cola and boil it in high heat [#20-24] |
| 4 | wok | 焖/烧 | low heat | 15 min | | — / — / — | 捞出 | time: for 15 minutes | | After seasoning, braise for 15 minutes in low heat [#31-32] |
| 5 | wok | 收汁 | middle heat | — | | — / — / — | | thickness: thick enough to stick to the chicken wings | ready to serve (method not stated) | After 15 minutes, turn to middle heat to thicken the sauce [#33-34] |

### 13. 清炒西兰花 (+白灼/蚝油) — `xilanhua`

Video `U_Xkq3Ots3w` · transcript zh-Hans · heat changes 0 · active wok ≥ 40 s · plating: wok→plate (出锅装盘) [清炒]; invert bowl + 淋 [白灼, 蚝油]

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok/pot (锅 unspecified) | 焯水 [白灼] `alt` | 开大火 | — | | — / — / — | 捞出 | bubbles: 水开之后, texture: 焯水至断生 | 捞出 (strainer) to arrange | 锅中加入适量的清水开大火烧开 [#38-43] |
| 2 | bowl/plate (cold mixing) | other: 码碗 + 扣碗 (pack florets head-down, invert onto plate) `alt` | | — | | — / — / — | other, other, other | other: 摆放太松 倒扣的时候容易散开 | bowl inverted onto plate, lifted off later | 西蓝花捞出之后将花朝底 [#44-49] |
| 3 | wok | 泼油 (onto 蒜蓉 in a bowl) `alt` | (180 °C, conv) | — | | — / — / — | 淋 | temperature: 烧至6成热 | hot oil poured into the garlic bowl; sauce then 淋 over the unmolded broccoli | 然后准备适量的植物油烧至6成热 [#52-57] |
| 4 | wok/pot (锅 unspecified) | 煮 + 勾芡 (拉丝芡 water) [蚝油] `alt` | 将锅离火 → 开小火慢煮 | — | | — / — / — | 捞出 | thickness: 将清水勾成拉丝芡, texture: 煮至断生 | 捞出, 扣碗 onto plate | 然后将锅离火 [#63-68] |
| 5 | wok/pot (锅 unspecified) | 收汁 (蚝油汁) [蚝油] `alt` | | — | | — / — / — | 淋 | bubbles: 蚝油烧开之后, thickness: 汤汁收浓之后 | most cooking liquid poured out first ('留下少部分'); sauce 淋 over the plated broccoli | 首先将锅中煮西蓝花的汤汁倒出 [#75-80] |
| 6 | wok/pot (锅 unspecified) | 焯水 [清炒] | | — | | — / — / — | | bubbles: 锅中水烧开之后, texture: 焯水断生 | 倒出备用 (drained) | 同样锅中水烧开之后加入食用盐 [#83-88] |
| 7 | wok | 爆香 [清炒] | 开中小火 (150 °C, conv) | 20 s est | | — / — / — | | temperature: 油温5成热, smell: 料头爆香之后 | | 然后锅烧热之后加入少许的植物油 [#89-91] |
| 8 | wok | 煮 + 勾芡 (薄芡) [清炒] | | 10 s est | | — / — / — | | bubbles: 水烧开之后, thickness: 勾成薄芡 | | 再加入适量的清水 [#93-97] |
| 9 | wok | 炒 (broccoli back + 明油) [清炒] | | 10 s est | | — / — / — | 翻炒 | other: 翻炒均匀 | 出锅装盘 | 然后加入断生的西蓝花下锅 [#99-100] |

Note: Three variants in one video; 清炒 is the primary dish, 白灼/蚝油 phases are flagged alt_variant and excluded from per-dish timing. Broccoli mass '适量'.

### 14. 地三鲜 — `disanxian`

Video `h3Jtrv7Y6Jc` · transcript en · heat changes 1 · active wok ≥ 120 s · plating: wok→plate (method not stated)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok/pot (锅 unspecified) | 煮 (potato cubes) | large fire | 300 s | | — / — / — | 捞出 | time: for 5 mins, probe: pierced easily by a chopstick | lifted out of the water into a container | Boil the potatoes for 5 mins with large fire until them c… [#8-9] |
| 2 | fryer/deep oil in wok | 炸 | (180 °C, conv) | 80 s | | — / — / — | other | temperature: Heat the oil to 60% boiling, time: for about 80 seconds, texture: surface of the potatoes become  | everything poured out of the wok and the oil filtered (strainer) | Heat the oil to 60% boiling [#23-27] |
| 3 | wok | 爆香 | medium fire | 20 s est | | — / — / — | 翻炒 | smell: You can smell the scent | | Put the garlics and the stallions into the pot directly a… [#28] |
| 4 | wok | 煮 + 勾芡 (sauce) | | 10 s est | | — / — / — | 淋 | thickness: to make them ropy | | Add 3 grams of soy sauce along the edge of the pot. [#30-36] |
| 5 | wok | 炒 (fried veg back) | | 10 s est | | — / — / — | 翻炒 | other: mix them well | placed onto plate | Put in fried potatoes, eggplants and peppers and mix them… [#38] |

Two hands / helper: pour the whole wok of hot oil + food out and filter it (wok in one hand, strainer/oil container in the other) (inferred)

Note: en says 'pot' throughout; boiling vessel recorded as 锅 unspecified. Potato/eggplant mass not stated.

### 15. 小炒肉 — `xiaochaorou`

Video `kwhW6LOpfZo` · transcript zh-Hans · heat changes 2 · active wok ≥ 133 s (2 untimed) · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 滑油 (里脊, off heat) | 锅烧热烧透 → 离火 | — | | — / — / — | | temperature: 锅烧热烧透, texture: 里脊肉滑熟 | 倒出备用 (meat poured out and kept) | 锅烧热烧透之后离火 [#44-47] |
| 2 | wok | other: 洗锅 (wash the wok) | | — | | — / — / — | other | |  | 洗锅之后重新把锅烧热 [#48] |
| 3 | wok | 预热/润锅 | 重新把锅烧热 | — | | — / — / — | 晃锅 | | 热油倒出 | 加入适量的油再次滑锅 [#49-50] |
| 4 | wok | 煸 (五花 for lard) | 转小火 | 60 s | | 100 / — / — | 翻炒 | time: 翻炒1分钟, smell: 把五花肉炒香炒出猪油 | | 然后加入切好的五花肉下锅 [#51-53] |
| 5 | wok | 爆香 (姜蒜 + 辣椒) | | 40 s | | 270 / — / — | 翻炒 | time: 翻炒40秒, smell: 炒出香味 | | 五花肉爆香之后加入姜蒜末和辣椒 [#54-56] |
| 6 | wok | 炒 (锅气) | 中大火 | — | | 270 / — / — | 翻炒 | smoke: 炒出锅气 | | 继续开中大火翻炒出辣椒的锅气 [#57-59] |
| 7 | wok | 炒 (seasoning + 蒜苗) | | 33 s est | | — / — / — | 翻炒, 淋 | texture: 继续翻炒断生 | 出锅装盘 | 加入生抽2克从锅边淋入 [#65-68] |

Two hands / helper: hold the wok off the fire while adding oil and meat and moving it (滑熟 off heat) (inferred)

### 16. 风味茄子(烧茄子) — `fengweiqiezi`

Video `sa2ayPSYEBk` · transcript en · heat changes 1 · active wok ≥ 93 s · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | fryer/deep oil in wok | 炸 (in small batches) | high fire → low fire (180 °C) | 60 s | | — / — / — | other | temperature: heat the the oil to 60% (~180C), time: fry for 1 minute, colour: until golden brown | eggplants taken out and drained; hot oil poured out | use high fire to heat the the oil to 60% (~180C) [#31-36] |
| 2 | wok | 爆香 | | 20 s est | | — / — / — | 翻炒 | smell: until aromatic | | put the garlic, green onion, peppercorns and chilies in, … [#38-39] |
| 3 | wok | 收汁 (碗汁 with starch) | low fire | 10 s est | | — / 30 / — | | thickness: to thicken the sauce | | when the aroma comes out, add in the seasoning sauce [#40-41] |
| 4 | wok | 炒 (明油 + eggplant back) | | 3 s est | | — / — / — | 翻炒 | other: do not stir fry ... for too long | | after that , add a little "Ming You" (lit. "shiner oil") [#42-43] |

Two hands / helper: drain fried eggplant and pour the hot oil out of the wok (inferred)

Note: Eggplant mass not stated (2 eggplants). Sauce amounts garbled in en (earlier pass used a fan transcription).

### 17. 鱼香茄子 — `yuxiangqiezi`

Video `bJLjJ-qF89I` · transcript en · heat changes 2 · active wok ≥ 83 s · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | steamer | 蒸 | medium heating | 15 min | | 500 / — / — | | time: for 15 minutes, texture: make them soft | cooked eggplant retrieved from the steamer | Then put the eggplant pieces into the steamer [#14-16] |
| 2 | wok | 预热/润锅 | heat the wok | — | | — / — / — | 晃锅 | | excess oil poured out | Then lubricate the wok with a little oil [#35-36] |
| 3 | wok | 煸 (minced meat) | low to medium heating | 20 s est | | 150 / — / — | | smell: When you can smell the scent of meat, other: heat the oil out of the meat | | low to medium heating to heat the oil out of the meat [#38-39] |
| 4 | wok | 爆香 | low heating | 20 s est | | — / — / — | 翻炒 | smell: stir out the scent of ingredients | | low heating to stir out the scent of ingredients [#40] |
| 5 | wok | 收汁 (鱼香汁 with starch) | low heating | 10 s est | | — / 30 / — | | thickness: When the sauce is sticky | | Then put in the 'fishy sauce' [#41-43] |
| 6 | wok | 炒 (eggplant in sauce) | Low heating | 33 s | | 715 / — / — | 翻炒, 翻炒 | time: for 30 seconds, other: the eggplants must be covered with the sauce | | Low heating and stir fry for 30 seconds [#44-46] |

### 18. 蚂蚁上树 — `mayishangshu`

Video `cb342Wl_yVc` · transcript en · heat changes 1 · active wok ≥ 103 s · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bowl | 浸 (noodles in hot water) | | 15 min | | 150 / — / — | | time: rest for 15 minutes | noodles drained | Add hot water and rest for 15 minutes [#4-6] |
| 2 | wok | 预热/润锅 | heat up the wok | — | | — / — / — | 晃锅 | | heated oil poured out | First heat up the wok and add some oil [#17-18] |
| 3 | wok | 煸 (pork + 花椒) | low heat | 40 s | | 100 / — / — | | time: for 40 seconds, other: get the lard out | | Add the minced pork [#19-21] |
| 4 | wok | 炒 (aromatics + 豆瓣) | lower heat | 20 s est | | — / — / — | | colour: until the oil becomes red, smell: After the fragrance is out | | Add 3g fermented bean paste [#23-25] |
| 5 | wok | 炒 (noodles) | | 30 s | | 265 / — / — | | time: for 30 seconds, texture: soften the noodles and cook them through | | Cook the noodles for 30 seconds [#26-27] |
| 6 | wok | 炒 (seasoning) | | 10 s est | | — / — / — | 翻炒, 淋 | other: until the seasoning are well distributed | | Add 2g light soy sauce, pour from the edge of the wok [#29-34] |
| 7 | wok | 炒 (garlic sprout, scallion, 葱油) | | 3 s est | | 285 / — / — | 翻炒 | | ready to serve (method not stated) | add the garlic sprouts and chopped green onion [#35-36] |

### 19. 辣子鸡 — `laziji`

Video `NqHI1CJU-Rg` · transcript en · heat changes 3 · active wok ≥ 240 s · plating: wok→plate (method not stated)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | fryer/deep oil in wok | 炸 | Heat up the wok → medium heat (210 °C) | 60 s | | — / — / — | 捞出, other | temperature: Heat the oil up to around 210 C, time: for 1 minute, shape: fixes the shape of the chops | chicken lifted out with a strainer; debris cleaned out of the oil | Heat the oil up to around 210 C [#50-55] |
| 2 | fryer/deep oil in wok | 复炸 (off the stove) | Take the wok away from the stove (240 °C) | 20 s | | — / — / — | other, 捞出 | temperature: Heat the oil up to around 240 C, time: for 20 seconds, texture: This steps give the crispy crust | chicken filtered out | Heat the oil up to around 240 C [#57-61] |
| 3 | wok | 爆香 | medium heat (180 °C) | 30 s | | 180 / — / 20 | 翻炒 | temperature: Heat up to 180 C, time: for 30 seconds, smell: releases the aroma | | Now we add 20 grams of canola oil [#62-67] |
| 4 | wok | 炒 (chicken) | low heat | 120 s | | 180 / — / — | 翻炒 | time: for 2 minutes | | Now we add the chicken [#69-70] |
| 5 | wok | 炒 (seasoning + peanuts + oils) | low heat | 10 s est | | 230 / — / — | 淋, 翻炒 | | taken into the plate | Add 1 gram of rice vinegar from the side of wok [#75-79] |

Two hands / helper: hold a wok of 240 °C oil away from the stove while adding and frying the chicken for 20 s, then strain it (inferred); lift chicken out with a strainer while holding the wok / clean debris (inferred)

### 20. 酸菜鱼 — `suancaiyu`

Video `gONExIBbazI` · transcript zh-CN · heat changes 5 · active wok ≥ 625 s (2 untimed) · plating: scoop/ladle into 盆 + 泼油

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 焯水 (酸菜) | | 120 s | | 200 / — / — | | time: 焯水2min | 倒出备用 (drained) | 首先我们在锅中加入适量的清水 [#60-63] |
| 2 | wok | other: 洗锅 | | — | | — / — / — | other | |  | 把炒锅清洗干净之后再把焯过水的酸菜下锅翻炒2min [#64] |
| 3 | wok | 煸 (dry-fry 酸菜) | | 120 s | | 200 / — / — | 翻炒 | time: 翻炒2min, other: 把酸菜的水份炒干为止 | 倒出备用 | 把炒锅清洗干净之后再把焯过水的酸菜下锅翻炒2min [#64-67] |
| 4 | wok | 炒 (辅料) | 开中火 (180 °C, conv) | 60 s | | 380 / — / — | 翻炒 | temperature: 油烧至6成热, time: 翻炒1min, smell: 所有的辅料炒香之后 | 倒出放入碗中备用 | 油烧至6成热之后把切好的泡萝卜泡姜和野山椒下锅 [#70-74] |
| 5 | wok | other: 洗锅 | | — | | — / — / — | other | |  | 炒锅洗干净之后我们开始准备煎鱼骨头 [#75] |
| 6 | wok | 预热/润锅 | 把锅烧热 | — | | — / — / — | 晃锅 | | 滑锅的热油倒出 | 锅烧热之后加入适量的植物油滑锅 [#77-78] |
| 7 | wok | 煎 (fish bones + head) | 开中火 (180 °C, conv) | 120 s | | — / — / — | | temperature: 油温升至6成热, time: 煎2分钟, colour: 煎至金黄色为止 | | 油温升至6成热之后我们把处理好的鱼骨头下锅 [#79-80] |
| 8 | wok | 炒 (辅料 back) | 开大火 | 10 s est | | — / — / — | 翻炒 | other: 翻炒均匀 | | 鱼骨头煎好之后再把炒好的所有辅料下锅开大火翻炒均匀 [#83] |
| 9 | wok | 煮 (fish soup) | 开大火 → 转中火 | 180 s | | — / — / — | 撇浮沫, 捞出 | bubbles: 开大火烧开后, time: 煮3min, colour: 鱼汤浓白 | bones + 酸菜 捞出 into the serving 盆 as a base | 辅料翻炒均匀之后再将事先准备好的热水下锅 [#84-88] |
| 10 | wok | 煮 (滑鱼片 in the soup) | 将锅离火 → 开小火 | 15 s | | — / — / — | other, 推炒, 捞出 | time: 滑15s左右, other: 不能煮太久否则容易煮老 | slices 捞出 into the 盆 | 然后将锅离火 [#94-97] |
| 11 | wok | 煮 (soup re-boil, pour) | 开大火 | — | | — / — / — | other | bubbles: 大火烧开之后 | soup poured into the 盆; dregs held back at the end | 然后再把锅中的鱼汤开大火烧开 [#100-102] |
| 12 | wok | 泼油 | (240 °C, conv) | — | | — / — / — | 舀汤浇 | temperature: 油温烧到8成热 | oil ladled out with 炒勺 and splashed on the fish in one go | 我们把锅烧热之后再加入适量的植物油 [#107-108] |

Two hands / helper: hold the wok off the fire while adding fish slices one by one (inferred); pour the soup from the wok into the 盆 while holding back the dregs (inferred)

### 21. 茄汁糖醋里脊 — `qiezhilizhi`

Video `TDWG-pCFiAY` · transcript zh-Hans · heat changes 0 · active wok ≥ 230 s · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | fryer/deep oil in wok | 炸 | 转中小火 (150 °C, conv) | 120 s | | — / — / — | other, 不动, 捞出 | temperature: 待油温5成热, time: 炸2分钟, shape: 炸至定型 | pieces separated with a 漏勺, then lifted out | 在烧油的时候我们把处理好的里脊 [#33-39] |
| 2 | fryer/deep oil in wok | 复炸 | (200 °C) | 90 s | | — / — / — | 捞出 | temperature: 重新把油温升至200度, time: 复炸90秒, colour: 炸至金黄酥脆 | 捞出备用; hot oil then poured out | 重新把油温升至200度 [#41-44] |
| 3 | wok | 煮 + 勾芡 (茄汁) | 转中小火 | 10 s est | | — / — / — | | bubbles: 汁水烧开之后, thickness: 勾好芡汁后 | | 热油倒出之后直接下入调好的茄汁 [#47-50] |
| 4 | wok | 炒 (里脊 back) | | 10 s est | | — / — / — | 翻炒 | other: 翻炒均匀 | 出锅装盘 | 最后加入炸好的里脊翻炒均匀即可出锅装盘 [#51] |

Two hands / helper: lift and separate fried pieces with a 漏勺 while holding the wok (inferred)

### 22. 京酱肉丝 — `jingjiangrousi`

Video `JKFpxkeXwyQ` · transcript zh-Hans · heat changes 0 · active wok ≥ 53 s (1 untimed) · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | 把锅烧热 | — | | — / — / — | 晃锅 | | 热油倒出 | 锅烧热之后加入适量的油滑锅 [#34-35] |
| 2 | wok | 滑炒 (肉丝 in cold oil) | 转中小火 | 30 s est | | 300 / — / — | other, 不动, 划散 | shape: 肉丝没有定型之前 / 待肉丝底部成熟, texture: 肉丝炒熟炒散 | excess oil poured out of the wok, meat stays in | 热油倒出之后加入适量的冷油 [#36-44] |
| 3 | wok | 爆香 (蒜蓉 + 生抽 + 料酒 from edge) | | 20 s est | | — / — / — | 淋, 翻炒 | smell: 加入适量的蒜蓉爆香, smoke: 翻炒出锅气 | | 油倒出之后加入适量的蒜蓉爆香 [#45-49] |
| 4 | wok | 炒 (爆酱 甜面酱) | | 3 s est | | — / — / — | 翻炒 | other: 否则甜面酱容易炒干炒焦发苦 (#69-70) | | 锅中加入甜面酱3勺（约10克） [#50-53] |
| 5 | wok | 收汁 | 中小火 | — | | — / — / — | 淋, 翻炒 | thickness: 略微收汁, other: 翻炒均匀 | 出锅装盘 | 然后加入适量的清水从锅边淋入 [#54-56] |

Two hands / helper: pour excess oil out of the wok while holding the meat back (inferred)

### 23. 葱爆羊肉 — `congbaoyangrou`

Video `BdTZURT3uL4` · transcript zh · heat changes 1 · active wok ≥ 76 s (1 untimed) · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | 把锅烧热 | — | | — / — / — | 晃锅 | | 热油倒出 | 锅烧热之后加入适量的油润锅 [#46-47] |
| 2 | wok | 炸 (葱心 in shallow oil) | (150 °C, conv) | — | | — / — / — | 捞出 | temperature: 油温5成热, texture: 葱心熟透 | 葱心 捞出 | 重新加入适量的冷油 [#48-50] |
| 3 | wok | 滑炒 (羊肉) | 开中火 | 33 s est | | — / — / — | 不动, 划散, 捞出 | shape: 让羊肉彻底成型, colour: 炒至变色, texture: 炒至八成熟 | lamb 捞出, excess oil drained | 羊肉下锅之后先不动煎几秒 [#52-56] |
| 4 | wok | 爆香 (姜蒜 + 小米辣) | 中火 | 20 s est | | — / — / — | 翻炒 | smell: 把料头爆香 | | 然后加入剁好的姜蒜末和小米辣 [#57-58] |
| 5 | wok | 爆炒 (大葱) | 转中大火 | 20 s est | | 250 / — / — | 翻炒, 淋 | smell: 爆出葱香味 | | 然后转中大火爆炒几下爆出葱香味 [#60-61] |
| 6 | wok | 收汁 (碗芡) | | 3 s est | | — / 30 / — | 翻炒 | thickness: 把料汁收浓把汤汁包裹在羊肉上面 | 出锅装盘 | 大葱爆香之后加入调好的料汁下锅 [#62-64] |

Note: He never says when the lamb goes back into the wok (it is coated by the sauce at #63). Lamb mass not stated.

### 24. 蛋炒饭 — `danchaofan`

Video `EvE5cYNXufY` · transcript en · heat changes 2 · active wok ≥ 366 s (1 untimed) · plating: wok→plate (method not stated)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | heat up the wok | — | | — / — / — | 晃锅 | | heated oil removed; fresh oil added | First, heat up the wok. [#18-20] |
| 2 | wok | 炒 (egg whites) | | 30 s est | | — / — / — | 翻炒 | texture: until cooked | removed from wok and set aside | Add the whites, and stirfry until cooked. [#21-22] |
| 3 | wok | 炒 (yolks) | | 20 s est | | — / — / — | | smell: until fragrant | | Add a little vegetable, cook the yolks until fragrant. [#23] |
| 4 | wok | 炒 (bacon, sausage, corn) | medium-low | — | | — / — / — | | texture: to allow ingredients to cook through | | Then add the prepared bacon, sausage, and corn. [#24-25] |
| 5 | wok | 炒 (whites back) | | 10 s est | | — / — / — | 颠锅 | other: to cook everything evenly | | Then, add the egg whites back. [#26-27] |
| 6 | wok | 炒 (rice) | very low | 300 s | | — / — / — | 颠锅 | time: for five minutes, smoke: until the wok begins to smoke (wok hei) | | Turn the heat very low and toss to stir fry the rice for … [#30-32] |
| 7 | wok | 炒 (soy from edge + scallion) | Crank heat to high | 6 s est | | — / — / — | 淋, 颠锅 | | ready to plate (method not stated) | drizzle in a small amount of soy sauce from the edges of … [#34-36] |

Note: en 'toss' may translate 翻炒 rather than 颠锅; counted as toss (en).

### 25. 担担面 — `dandanmian`

Video `X3MyQUEQ5Wo` · transcript zh-Hans · heat changes 1 · active wok ≥ 20 s (1 untimed) · plating: assemble in bowl

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 煸 (肉末 to crisp) | | — | | 150 / — / — | | texture: 直到肉末酥脆, smell: 炒熟爆香 | 肉末 出锅; rendered lard kept and used to loosen the 芝麻酱 | 锅烧热之后加入适量的底油 [#11-13] |
| 2 | wok | 炒 (芽菜) | | 20 s est | | — / — / — | | smell: 芽菜炒香 | 备用 (to the sauce bowl) | 然后锅中继续加入少许的植物油烧热 [#15-16] |
| 3 | wok/pot (锅 unspecified) | 煮 (noodles) | 大火烧开 → 保持微开 | — | | — / — / — | other, 捞出 | bubbles: 大火烧开 / 保持微开, texture: 挑起一根夹断（其）中心看有没有生面 | noodles 捞出 into 凉开水 to cool, then into the bowl | 首先我们在锅中加入适量的清水大火烧开 [#31-40] |
| 4 | bowl/plate (cold mixing) | 拌 | | — | | — / — / — | other, 拌 | | eaten from the bowl | 最后冷却之后再均匀地放入碗中 [#41-44] |

Note: Noodle amount and boiling time not given.

### 26. 酸辣汤 — `suanlatang`

Video `mQ_2W5zUd44` · transcript zh-Hans · heat changes 0 · no wok phases · plating: pour/ladle soup into bowl (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok/pot (锅 unspecified) | 焯水 (猪血 + 豆腐) | | 20 s | | — / — / — | | bubbles: 烧开, time: 烫20秒 | 倒出沥干水分 (drained) | 首先我们在锅中加入适量的清水烧开 [#23-29] |
| 2 | wok/pot (锅 unspecified) | 煮 (soup base + seasoning) | | — | | — / — / — | | bubbles: 水开之后 | | 然后锅中再次加入适量的清水 [#30-32] |
| 3 | wok/pot (锅 unspecified) | 勾芡 (off heat) | 将锅离火 | 10 s est | | — / — / — | 搅拌 | thickness: 将汤汁收成拉丝状态的汤羹 / 汤汁最好能保持20厘米拉丝 | | 调好味之后将锅离火 [#38-40] |
| 4 | wok/pot (锅 unspecified) | 煮 (木耳, 火腿, 姜, 虾米) | | — | | — / — / — | | texture: 将其煮熟之后 | | 勾好芡之后加入切好的木耳丝 [#41-43] |
| 5 | wok/pot (锅 unspecified) | 煮 (egg, blood, tofu, greens) | | — | | — / — / — | 淋 | bubbles: 汤烧开之后 | 出锅装盘 (into a serving bowl) | 然后加入鸡蛋液下锅 [#44-48] |

Note: Pot vs wok not named (he stirs with a 炒勺). Tofu/blood masses '1小块'.

### 27. 拍黄瓜 — `paihuanggua`

Video `x6_aDVi4_uY` · transcript en · heat changes 0 · no wok phases · plating: arrange on plate

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bowl | 拌 (sauce) | | — | | — / — / — | 搅拌 | |  | Finally add 20g home-made red oil [#15-17] |
| 2 | bowl/plate (cold mixing) | 拌 (cucumber + sauce) | | — | | — / — / — | other, 拌 | | mixture put on the plate over the cucumber core | Put the stuffed cucumber on the bottom of the plate [#26-27] |

Note: No heat. Cucumber mass not stated.

### 28. 白切鸡 / 口水鸡 — `baiqieji_koushuiji`

Video `27qBWkkr8HY` · transcript zh-Hans · heat changes 0 · no wok phases · plating: arrange on plate

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | pot | 煮 (water + salt + 姜葱 to a boil, then 关火) | 开火 → 关掉 | — | | — / — / — | | bubbles: 水开得很厉害 | | 煮这个鸡我们把这个盐倒个二三两 [#64-74] |
| 2 | pot | 浸 (烫: dip, lift, drain cavity, cold-dip, repeat) | off | — | | — / — / — | other, other, other | sound: 听到声音没 / 呼 呼 呼的 | | 现在我们把鸡放下去 [#82-93] |
| 3 | pot | 浸 (steep off heat) | off | 40 min | | — / — / — | other, 捞出 | time: 泡它半个小时 / 再泡它个十分钟左右, probe: 用手捏一下它的腿 / 它腿的地方硬了 / 软的 它会回弹回来 就说明没有熟, other: 砍出来它骨头里面是带血的 | chicken hooked out by the neck, into cold water | 要是三斤以下的鸡的话 [#100-148] |
| 4 | bowl | 浸 (cool in clean water) | | — | | — / — / — | | other: 等它凉透了 | chicken lifted out, chopped and arranged on a plate | 现在我们这个鸡捞出来 [#153-156] |
| 5 | bowl | 拌 (口水鸡 dipping sauce) | | — | | — / — / — | 舀汤浇, 搅拌 | |  | 先倒酱油 [#241-282] |
| 6 | other (oil-heating vessel not named) | 泼油 (onto 姜葱蓉) | | — | | — / — / — | 淋 | |  | 好 等我切好你烧点油给它浇一下 [#303-308] |

Two hands / helper: lift a whole chicken out of hot water and tip its cavity water out, then dunk it in a second basin (inferred); helper heats the oil for 泼油 while he cuts (explicit (second person))

Note: Rural episode with banter; chicken mass only '三斤以下'. Oil temperature for 泼油 not stated.

### 29. 红烧鲤鱼 — `hongshaoliyu`

Video `cHXO5befcUI` · transcript zh-Hans · heat changes 1 · active wok ≥ 340 s (2 untimed) · plating: lift whole fish + pour sauce over

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 煎 (whole fish) | 开中小火 (150 °C, conv) | 300 s | | 900 / — / — | 翻面 | temperature: 烧至5成热, time: 煎5分钟, colour: 两面煎香煎黄 | 倒出备用 (fish out of the wok) | 锅烧热之后加入适量的底油烧至5成热 [#22-28] |
| 2 | wok | 煸 (五花 粒) | | — | | — / — / — | | colour: 炒至金黄, other: 出油 | | 油热之后加入切好的五花肉爆香爆出猪油 [#30-32] |
| 3 | wok | 爆香 (姜蒜) | | 20 s est | | — / — / — | | smell: 姜蒜粒炒香 | | 猪肉爆香之后加入切好的姜蒜粒爆香 [#31] |
| 4 | wok | 炒 (香菇 + 葱) | | 10 s est | | — / — / — | 翻炒 | other: 翻炒均匀 | | 姜蒜粒炒香之后加入切好的香菇和葱粒 [#33-34] |
| 5 | wok | 煮 (beer sauce) | 大火 | — | | — / 500 / — | 淋 | bubbles: 大火烧开 | | 加入生抽酱油6克从锅边淋入 [#36-38] |
| 6 | wok | 烧 (fish in sauce) | | 360 s | | 900 / — / — | 舀汤浇, 不动, 捞出 | time: 烧6分钟 | whole fish 捞出 and laid on the plate | 然后将鲤鱼下锅烧6分钟 [#44-47] |
| 7 | wok | 收汁 (勾芡 + 明油) | | 10 s est | | — / — / — | 淋 | bubbles: 汤汁烧开之后, thickness: 水淀粉收汁 | sauce poured over the plated fish | 然后将剩余的汤汁烧开 [#48-50] |

Two hands / helper: flip a whole 900 g fish in the wok without breaking it (inferred); lift the braised whole fish out onto a plate intact (inferred)

### 30. 手撕包菜 — `shousibaocai`

Video `JZutepq2GLM` · transcript zh-Hans · heat changes 1 · active wok ≥ 74 s · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 焯水 (to 3–4 成 done) | 开火 | 13 s video_1take | | — / — / — | | bubbles: 先把水烧开 / 水开了, texture: 焯水不要焯熟 / 焯个三四成就可以了 | 把水沥干 (drained) | 先把水烧开 [#117-137] |
| 2 | wok | other: 洗锅 | | — | | — / — / — | other | |  | 然后洗锅 [#139] |
| 3 | wok | 炒 (锅气 pass, oil only) | 火要大 → 开大火 | 18 s video_1take | | — / — / — | 翻炒 | colour: 有一点要糊不糊的这种感觉, smell: 这种焦香味很足 | 倒出 (cabbage out) | 现在要炒锅气 [#141-149] |
| 4 | wok | other: 洗锅 | | — | | — / — / — | other | |  | 然后重新洗锅 [#154] |
| 5 | wok | 爆香 (猪油 + 辣椒 + 辣椒籽 + 蒜) | | 12 s video_1take | | — / — / — | | smell: 爆出糊辣味 | | 加点这个猪油 [#156-160] |
| 6 | wok | 炒 (cabbage back + seasoning) | 关火 | 31 s video_1take | | — / — / — | 淋, 翻炒 | |  | 好 下去 [#161-170] |

Note: Cabbage amount used not weighed. Durations from one-take (uncut) footage.

### 31. 小炒茄子(肉片) — `xiaochaoqiezi`

Video `Kjkr27b3YwA` · transcript zh-Hans · heat changes 1 · active wok ≥ 330 s · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 (oil kept) | 将锅烧至冒青烟为止 | — | | — / — / — | 晃锅 | smoke: 冒青烟 | none (润锅 oil stays in the wok) | 首先我们把锅烧热 [#27-29] |
| 2 | wok | 煸 (五花) | 开中小火 | 60 s | | 200 / — / — | 翻炒 | time: 爆炒1分钟, other: 炒出猪油 | | 然后将切好的五花肉下锅 [#30-32] |
| 3 | wok | 爆香 (大蒜 + 辣椒) | 中火 | 20 s est | | — / — / — | 翻炒 | texture: 炒至辣椒起皮 | | 加入准备好的大蒜和辣椒 [#34-35] |
| 4 | wok | 爆炒 (茄子) | 开中火 | 240 s | | 200 / — / — | 翻炒 | time: 爆炒3分钟 / 继续开中火爆炒1分钟, other: 会把猪油吸进去 / 将吸进去的油吐出来, smoke: 炒出锅气 | | 然后开中火将茄子爆炒3分钟 [#37-41] |
| 5 | wok | 炒 (seasoning) | | 10 s est | | — / — / — | 淋, 翻炒 | other: 将所有调料翻炒均匀 | 出锅装盘 | 加入适量的生抽酱油从锅边淋入（约3克） [#48-50] |

### 32. 黄焖鸡 — `huangmenji`

Video `oD20MDwF5no` · transcript zh-Hans · heat changes 4 · active wok ≥ 353 s (1 untimed) · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bowl | 浸 (prep: dried 香菇 in warm water) | | 40 min | | — / — / — | | time: 浸泡40分钟 | | 准备干香菇几颗用温水浸泡40分钟备用 [#13] |
| 2 | wok/pot (锅 unspecified) | 焯水 (chicken, cold start) | | — | | — / — / — | | shape: 鸡肉焯水定型 | 倒出备用 | 首先我们在锅中加入适量的清水 [#22-27] |
| 3 | wok | 炸 (potatoes in 底油) | | 120 s | | — / — / — | 捞出 | time: 下锅炸2分钟, texture: 把土豆炸熟 | excess oil removed, then potatoes 捞出 | 锅烧热之后加入适量的底油 [#28-32] |
| 4 | wok | 炒糖色 | 转小火 | — | | 20 / — / — | | colour: 炒成嫩糖色, other: 不能炒过 否则糖色很容易发苦 | | 重新加入冰糖20克下锅 [#33-37] |
| 5 | wok | 炒 (chicken) | 转中小火 | 120 s | | — / — / — | 翻炒 | time: 爆炒2分钟 | | 糖色炒好之后下入处理好的鸡肉转中小火爆香 [#40-41] |
| 6 | wok | 爆香 (香菇 + 姜蒜) | | 20 s est | | — / — / — | | smell: 料头炒香 | | 鸡肉爆炒2分钟之后加入香菇和料头（姜蒜粒）炒香 [#41] |
| 7 | wok | 炒 (蚝油 + 黄豆酱 + 老抽) | | 60 s | | — / — / — | 翻炒 | time: 翻炒1分钟, colour: 炒至上色 | | 酱料下锅之后继续翻炒1分钟炒至上色 [#45] |
| 8 | wok | 炒 (黄酒 from edge) | | 3 s est | | — / — / — | 淋, 翻炒 | |  | 翻炒1分钟之后加入适量的黄酒从锅边淋入 [#46-47] |
| 9 | wok | 焖 | 大火烧开 → 转中火 | 15 min | on | — / — / — | | bubbles: 大火烧开, time: 焖15分钟 | | 黄酒翻炒几下之后加入适量的清水大火烧开 [#47-52] |
| 10 | wok | 煮 (fried potatoes in) | 小火 | 10 min | | — / — / — | | time: 小火煮10分钟 | | 焖煮15分钟之后加入炸好的土豆 [#55-56] |
| 11 | wok | 收汁 (+ 青红椒 to 断生) | | 30 s est | | — / — / — | | thickness: 待汤汁浓稠, texture: 煮至断生 | 出锅装盘 | 待汤汁浓稠之后下入切好的青红椒煮至断生 [#58-60] |

Note: Chicken and potato masses not stated.

### 33. 韭菜炒鸡蛋 — `jiucaichaodan`

Video `XmTJrRilq40` · transcript en · heat changes 1 · active wok ≥ 80 s (1 untimed) · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 预热/润锅 | heat the wok piping hot | — | | — / — / — | 晃锅 | | hot oil poured out; new oil added | Firstly, heat the wok piping hot, then add some oil to ri… [#16-17] |
| 2 | wok | 炒 (chives) | | 20 s est | | 130 / — / — | 翻炒 | texture: till soft, smell: After you smell the fragrance | | Heat up the oil, place chopped chives into the pan and stir [#18-20] |
| 3 | wok | 煎 (egg patty) | low heat | 60 s | | 130 / — / — | 不动 | time: for 1 minute, shape: for egg patty to set | | Turn into low heat, sear the egg for 1 minute [#21-23] |
| 4 | wok | 炒 (break up + 锅气) | median heat | — | | — / — / — | 翻炒 | smoke: until the "pot fragrance" is out | serve (method not stated) | After your egg is set, sauté the dish [#25-26] |

### 34. 清蒸鲈鱼 — `zhengluyu`

Video `mVZC-iu60BQ` · transcript zh-Hans · heat changes 0 · no wok phases · plating: steamed on its plate + pour over

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | steamer | 蒸 (fish on a plate on 姜葱) | 蒸锅水烧开 → 转中火 | 480 s | | 600 / — / — | | bubbles: 蒸锅水烧开之后, time: 蒸8分钟 | plate taken out of the steamer | 蒸锅水烧开之后放入鲈鱼 [#36-38] |
| 2 | bowl/plate (cold mixing) | other: 沥水 + 重新摆盘 | | — | | — / — / — | 沥油, other | |  | 过滤多余的水份之后再重新摆盘 [#39-40] |
| 3 | other (oil-heating vessel not named) | 泼油 + 淋 鱼酱油 | | — | | — / — / — | 淋 | | hot oil then 鱼酱油 poured over the fish | 然后浇上热油 [#41-42] |
| 4 | wok/pot (锅 unspecified) | 煮 (re-boil plate juices + 鱼酱油, filter) [进阶] `alt` | | — | | — / — / — | other, other, other | bubbles: 重新烧开 | filtered and poured back over the fish | 首先把姜葱丝和辣椒丝用筷子夹起 [#45-48] |

Two hands / helper: hold the garnish shreds aside with chopsticks while tipping the plate juices out (inferred); pour the boiled sauce through a strainer onto the fish (inferred)

Note: Steamer lid and 泼油 temperature not stated.

### 35. 清炒菠菜 / 炝炒油麦菜 — `qingchao_qiangchao`

Video `YRWN6seKz2w` · transcript en · heat changes 0 · active wok ≥ 33 s · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 炒 [清炒菠菜] | medium flame | 30 s est | | — / — / — | 翻炒 | texture: until 60% cooked | | Then add the minced garlic and spinach into the heated oil [#22-23] |
| 2 | wok | 炒 (seasoning dissolved in the wok spoon) [清炒菠菜] | | 3 s est | | — / — / — | other, 翻炒 | colour: becomes emerald green | done (plating method not stated) | First, add some seasonings such as salt and white sugar i… [#25-28] |
| 3 | wok | 爆香 [炝炒油麦菜] `alt` | | 20 s est | | — / — / — | | smell: until aromatic | | Note that Qiangchao dishes require more oil than Qingchao… [#31-33] |
| 4 | wok | 炒 [炝炒油麦菜] `alt` | low to medium fire | 30 s est | | — / — / — | 翻炒 | texture: until "Duan Sheng" | | After that, add in the romaine [#34-35] |
| 5 | wok | 炒 (seasoning) [炝炒油麦菜] `alt` | | 3 s est | | — / — / — | 翻炒 | | done (plating method not stated) | Same as before, add in some salt and white sugar [#37-38] |

Two hands / helper: hold the wok spoon with salt/sugar while pouring boiled water into it, then tip it into the wok (inferred)

Note: Two dishes in one video; 清炒菠菜 is primary for timing, 炝炒 phases flagged alt_variant. Vegetable mass not stated.

### 36. 鱼头豆腐汤 — `yutoudoufutang`

Video `BvG46EWuH9E` · transcript zh-Hans · heat changes 3 · active wok ≥ 0 s (2 untimed) · plating: pour from wok into bowl (盆)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | fryer/deep oil in wok | 炸 (fish head, then 姜 and 葱 in the same oil) | 油温烧高一点 (150 °C, conv) | — | | — / — / 500 | | temperature: 油温差不多五成热, colour: 金黄金黄的, texture: 葱稍微软了 | poured out ('就可以倒出来了'); oil kept for a 2nd use | 有个一斤多就可以了 [#49-79] |
| 2 | wok | 煮 (soup, gentle) | 小火 | 15 min | | — / 2000 / — | | bubbles: 最好是先把水烧开, time: 熬个十五分钟左右, colour: 这个汤是百分之百会白的 | | 然后直接加水 [#81-108] |
| 3 | wok | 煮 (tofu) | 开大火 → 转小火 → 关火 | — | | — / — / — | 捞出 | colour: 熬一下会很白 | soup poured into a 盆 that already holds the salt and 香菜根 | 下豆腐要开大火 [#110-166] |
| 4 | bowl | other: salt in the serving 盆, soup poured on, stir | | — | | — / — / — | 搅拌 | taste: 尝一下 | | 再来放盐 [#173-187] |

Note: Fish head and tofu masses not stated; tofu simmer time not stated. 4 斤 water converted to 2000 g.

### 37. 椒盐排骨 — `jiaoyanpaigu`

Video `vFevFLKHn4o` · transcript zh-Hans · heat changes 1 · active wok ≥ 560 s (2 untimed) · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 炒 (dry-roast 椒盐, no oil) | 转小火 | 300 s | | 171 / — / — | 翻炒 | time: 翻炒5分钟左右, smell: 炒出香味, probe: 炒至干辣椒一捏就碎 | 出锅, then ground to powder | 锅烧热之后加入配好的椒盐 [#39-42] |
| 2 | fryer/deep oil in wok | 炸 (ribs, set the shape) | 转中火 (180 °C, conv) | 60 s | | 1000 / — / — | 捞出 | temperature: 油温6成热, shape: 炸至定型, time: 大约1分钟左右 | ribs 捞出 | 然后加入宽油 [#52-56] |
| 3 | fryer/deep oil in wok | 炸 (蒜蓉) | | — | | 150 / — / — | other | colour: 炸至金黄色, other: 蒜蓉不能炸过头否则很容易发苦 | 备用 (lifted out; method not stated) | 然后用细漏过滤出剁好的蒜蓉 [#57-61] |
| 4 | fryer/deep oil in wok | 复炸 (ribs) | 转中火 (210 °C) | 180 s | | 1000 / — / — | 捞出 | temperature: 重新把油温升至210度, time: 复炸3分钟, colour: 炸至金黄色 | ribs 捞出; 宽油 poured out | 蒜蓉炸好之后重新把油温升至210度 [#62-66] |
| 5 | wok | 爆香 (葱椒粒 in 猪油) | (180 °C, conv) | 20 s est | | — / — / — | | temperature: 油温烧至6成热, smell: 爆香 | | 加入适量的猪油 [#68-70] |
| 6 | wok | 炒 (ribs + garlic + 椒盐粉) | | — | | 1150 / — / — | 翻炒 | smoke: 把排骨翻炒出锅气, other: 翻炒均匀 | 出锅装盘 | 葱椒粒爆香之后下入炸香的排骨翻炒均匀 [#71-74] |

Note: Garlic frying method (in the fine strainer or loose) not stated; deep-oil mass not stated.

### 38. 焦溜肉段 — `jiaoliuroduan`

Video `JDnC-M2Bq48` · transcript zh · heat changes 1 · active wok ≥ 50 s (1 untimed) · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | fryer/deep oil in wok | 炸 (held at 160 °C) | 开中火 (150 °C) | — | | — / — / — | other, 不动, 划散, 捞出, other | temperature: 油温烧至150度 / 开中火维持160度的油温, texture: 把肉段表面的淀粉炸干炸硬, other: 等待肉段完全不粘连的时候, texture: 内部熟透 | pieces 捞出; debris cleared from the oil | 油温烧至150度的时候下入肉段 [#44-53] |
| 2 | fryer/deep oil in wok | 复炸 | (200 °C) | 20 s | | — / — / — | 捞出 | temperature: 油温重新升到200度, time: 复炸20秒左右, texture: 让肉段表面起酥 | 捞出; hot oil poured out | 然后把油温重新升到200度 [#54-60] |
| 3 | wok | 爆香 (葱姜蒜 + 辅料) | | 20 s est | | — / — / 40 | | smell: 料头爆香 | | 锅中加入40克热油 [#61-62] |
| 4 | wok | other: 溜 (碗汁 gelatinised on high heat, toss to coat) | 开大火 | 10 s est | | — / 140 / — | 翻炒 | thickness: 开大火将其糊化 | 出锅装盘 | 料头爆香之后下入肉段 [#63-66] |

Note: Meat mass not stated (only the 4:2.2 meat:batter ratio). First-fry duration not stated.

### 39. 土豆烧牛腩 — `tudoushaoniunan`

Video `0Kb1S6MgUZE` · transcript zh · heat changes 5 · active wok ≥ 210 s · plating: wok→plate (出锅装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok/pot (锅 unspecified) | 煮 (whole 牛腩) | 大火烧开 → 开中小火 | 60 min | on | — / — / — | 撇浮沫, 捞出 | bubbles: 大火烧开, time: 煮60分钟, probe: 用筷子能够插透 | beef 捞出, cut into cubes | 水大概加入大半锅或者8分满 [#19-29] |
| 2 | wok | 爆香 (off heat: 草果/葱/姜/花椒 → 豆瓣 → 甜面酱) | 油温5成热 → 把锅离火 (150 °C, conv) | 60 s est | | — / — / — | | temperature: 油温5成热, colour: 红油豆瓣酱炒出颜色, smell: 甜面酱一勺炒香炒熟 | | 油温5成热之后把锅离火 [#34-40] |
| 3 | wok | 炒 (beef cubes in the paste) | | 30 s est | | — / — / — | 翻炒, 淋 | colour: 牛肉翻炒上色, smell: 泡椒炒香 | | 然后把牛肉翻炒均匀裹上酱 [#43-46] |
| 4 | wok | 焖 (beef + potato) | 大火烧开 → 开中小火 | 15 min | on | — / — / — | | bubbles: 大火烧开, time: 焖15分钟左右 | | 然后加入适量的清水没过牛肉 [#47-53] |
| 5 | wok | 焖 (+ tomato) | | 15 min | | — / — / — | | time: 焖15分钟, texture: 土豆软烂 | | 15分钟之后揭开锅盖 [#54-56] |
| 6 | wok | 收汁 (no starch) | 开中大火 | 120 s | | — / — / — | | time: 收汁2分钟, thickness: 把汤汁收到自然浓 | 出锅装盘 | 然后开中大火收汁2分钟 [#59-62] |

Note: Braise time stated as 15 + 15 min but also '总共焖20分钟'. Beef mass not stated. Boiling vessel not named (8分满 of a 锅).

### 40. 鸡蛋肉丝炒面 — `chaomian`

Video `qY04dt5FFfI` · transcript zh-Hans · heat changes 1 · active wok ≥ 46 s (1 untimed) · plating: wok→plate (装盘)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | wok | 煎 (荷包蛋) | 热锅滑油 → 小火 | — | | — / — / — | | texture: 煎成略微老一点的荷包蛋 | eggs out, cut into strips | 热锅滑油之后小火煎成略微老一点的荷包蛋 [#5] |
| 2 | bowl | 浸 (instant noodles) | (90 °C) | 420 s | | — / — / — | | time: 浸泡7分钟 | 捞出 into a basin of cold water, then drained | 加入90度以上的开水浸泡7分钟 [#21-33] |
| 3 | wok | 预热/润锅 | 把锅烧热 | — | | — / — / — | 晃锅 | | not stated ('重新加入少许油' implies it was poured out) | 锅烧热之后加入适量的底油滑锅 [#36-37] |
| 4 | wok | 滑炒 (肉丝) | | 30 s est | | — / — / — | 不动, 划散 | shape: 肉丝受热定型, texture: 肉丝滑熟 | | 肉丝受热定型之后快速滑散 [#38-40] |
| 5 | wok | 炒 (noodles + seasoning) | | 10 s est | | — / — / — | 淋, 翻炒 | colour: 老抽翻炒上色, other: 将调味料翻炒均匀 | | 加入适量的生抽酱油从锅边淋入（约3克） [#44-46] |
| 6 | wok | 炒 (veg + oil from the edge) | 开大火 | 3 s est | | — / — / — | 淋, 翻炒 | |  | 中途再加入切好的辅料下锅 [#47-51] |
| 7 | wok | 炒 (egg strips, 锅气) | | 3 s est | | — / — / — | 翻炒 | smoke: 炒出锅气 | 装盘 | 然后继续翻炒几下炒出锅气之后即可装盘 [#52] |

Note: Pork and noodle masses not stated.

### 41. 酱油炒饭 — `jiangyouchaofan`

Video `1Q-5eIBfBDQ` · transcript en · heat changes 1 · active wok ≥ 93 s (3 untimed) · plating: not stated

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bowl | 浸 (prep: dried radish) | | 10 min | | — / — / — | | time: for 10 minutes | | Soak the dried radish with some water for 10 minutes to m… [#16] |
| 2 | wok | 预热/润锅 | heat up the wok | — | | — / — / — | 晃锅 | | hot oil poured out | Then add some oil and swirl to grease the wok [#31-32] |
| 3 | wok | 煎 (egg white) | low heat | — | | — / — / — | 翻面 | smell: until aromatic, shape: it becomes solid | taken out for further use | Use low heat to fry the egg white until aromatic and it b… [#34-37] |
| 4 | wok | 煎/炒 (yolk, slow) | low heat (120 °C, conv) | — | | — / — / — | | temperature: With the oil reaching 40% hot, smell: until it smells good | | With the oil reaching 40% hot, put the yolk into the wok … [#39-40] |
| 5 | wok | 炒 (radish) | | 10 s est | | — / — / — | 翻炒 | |  | Then, add the radish into the yolk [#41-43] |
| 6 | wok | 炒 (white back) | | 20 s est | | — / — / — | 翻炒 | smell: When you can easily smell the scent | | Then add the fried white into the wok [#44-46] |
| 7 | wok | 炒 (rice, oil from the edge) | | — | | — / — / — | 淋, 翻炒 | other: When you see rice jumping in the wok | | Then, add a little oil along the edge of the wok and stir… [#47-53] |
| 8 | wok | 炒 (soy sauce, high) | middle-high heat | 63 s | | — / — / — | 淋, 翻炒 | time: stir-fry for 1 minute | ready to serve (method not stated) | Then add a little oil along the edge of the wok [#54-57] |

Note: Rice mass not stated ('a plate').

### 42. 脑花豆腐 — `naohuadoufu`

Video `ivcFXtMGdE8` · transcript zh-Hans · heat changes 2 · active wok ≥ 80 s (1 untimed) · plating: pour from wok into clay pot (煲仔)

| # | vessel | action | heat (°C) | time | lid | food / liq / oil g | hands | done when | out | quote [cue] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bowl | 浸 (tofu + 脑花 in just-boiled salted water) | | 300 s | | 380 / — / — | other | time: 5分钟 10分钟都可以 | | 然后我们提前烧了一锅水 [#41-123] |
| 2 | wok | 爆香 (葱头 → 火锅底料) | 小火 | 20 s est | | — / — / 30 | | temperature: 不要烧得太热 / 就有点热就可以, other: 开大火的话 / 这个渣的一部分就会糊 | | 大概这里就是30克的样子 [#130-139] |
| 3 | wok | 炒 (豆瓣) | 小火 | 20 s est | | — / — / — | | temperature: 你看温度起来了 | | 然后我们下这个豆瓣酱 [#150-156] |
| 4 | wok | 煮 (water + seasoning) | | — | | — / — / — | |  | | 水加完了之后调个味 [#159] |
| 5 | wok | 烧 (tofu + 脑花) | 开小火 → 开大火 (at the end) | 10 min | | 380 / — / — | other | taste: 这个时候要尝一下味道, liquid_level: 起码这个原材料 / 它要露出来至少30-40%了, time: 小火烧个十来二十分钟 | | 我们把这个泡了的豆腐 [#167-241] |
| 6 | wok | 勾芡 x4 (少量多次) + 收汁 to 亮油 | 关火 | 40 s est | | — / — / — | 搅拌, 淋, 推炒 | thickness: 推的时候它下面是干的 / 就说明芡汁已经浓了, oil_clarity: 收这个汁一定要把油要收亮一点再出菜, other: 下面有点锅巴了 | 关火, served in a 煲仔 (clay pot) on an alcohol burner | 轻轻给它晃一下 [#260-301] |

Two hands / helper: pour tofu + brain slowly from the soak bowl into the wok without breaking them (inferred); shake the starch bowl, pour a little, then push in the wok, 4 rounds (inferred)

Note: Water amount for the braise not stated. Brain mass not stated.
