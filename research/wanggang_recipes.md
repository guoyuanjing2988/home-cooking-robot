# Wang Gang (美食作家王刚) recipes → storage / dispensing / fridge requirements

Generated 2026-10-11. Structured data: `wanggang_recipes.json` (42 recipes, every seasoning event, plus aggregates). Build script and transcripts are in the session scratchpad and can be regenerated.

## Source and method

- **Source:** all 42 recipes come from subtitles on Wang Gang's own YouTube channel, *Chef Wang 美食作家王刚* (channel id `UCg0m_Ah8P_MQbnn77-vYnYw`). I fetched them read-only with `yt-dlp --skip-download --write-subs`.
  - 22 videos have **zh** subtitles. These are his narration word for word.
  - 20 videos have only **en** subtitles. These are the channel's official translation of what he says.
  - In both cases the amounts are his own. No recipe comes from a third-party rewrite.
  - One exception: in 风味茄子 the English subtitle garbled the sauce amounts. For that sauce I used the 下厨房 fan transcription of the same video (recipe 103708953) and labelled it `fan`.
- **Substitutions:** 13 older videos from 2018 had no subtitles at all. Where possible I replaced them with a newer video of the same dish that does have subtitles (鱼香肉丝 重庆版, 糖醋排骨 老式, 干煸四季豆 一镜版, 手撕包菜 一镜版). Dishes I could not find on his YouTube channel: 炸酱面 (担担面 used instead), 红烧茄子 (风味茄子 / 小炒茄子 used instead), 凉拌黄瓜 (拍黄瓜 used).
- **No amounts were invented.** Of 510 seasoning or aromatic mentions:
  - 191 (37 %) have grams stated by him.
  - 7 are conversions I made, each labelled.
  - 2 come from the fan transcription.
  - **310 (61 %) have no amount** (适量 / 少许 / "some"), and that is how they are recorded.
  - He reliably gives grams for the flavour-defining items: salt, sugar, vinegar, soy, 豆瓣, starch in 碗汁. He leaves out amounts for oil, aromatics and water.
- **Conversions:** 1 斤 = 500 g and 1 两 = 50 g. Thin liquids are taken as ≈1 g/ml. A spoon (勺) is converted only with his own stated equivalences (table below). For oil heat, he says 6成热 ≈ 180 °C; I scaled the other 成 levels at 30 °C per 成.
- **Timing:** `gap_s` is the time between two consecutive wok additions.
  - `stated` means he gives the time.
  - `est` means I estimated it from his wording: 翻炒几下 ≈ 3 s, "stir a bit" ≈ 5 s, "until fragrant" ≈ 10–30 s.
  - Video time is not cooking time, because the videos are edited, so I did not use it.

### His own spoon-to-gram equivalences
His seasoning spoon holds roughly 3–5 ml.

| item | equivalence he states | dish |
|---|---|---|
| 盐 | 1勺 ≈ 3 g; 2勺 ≈ 7 g; 1勺 ≈ 2 g / 1.5 g; 1 tsp ≈ 2 g; 小半勺 ≈ 0.5 g | 酸菜鱼, 酸辣汤, 红烧鲤鱼, 韭菜炒蛋, 炒面 |
| 盐 (for washing) | 1勺 ≈ 10 g (a larger spoon) | 椒盐排骨 |
| 白糖 | 7大勺 ≈ 30 g (4.3 g/勺); 2勺 ≈ 5 g | 鱼香肉丝, 京酱肉丝 |
| 甜面酱 | 3勺 ≈ 10 g; 1 tsp = 4 g | 京酱肉丝, 回锅肉 |
| 鸡精 / 味精 | 1勺 ≈ 2 g / 1勺 ≈ 1 g | 酸辣汤, 黄焖鸡 |
| 胡椒粉 | 2.5勺 ≈ 4 g; ½ tsp ≈ 1 g | 酸辣汤, 韭菜炒蛋 |

**→ "1勺" is not a fixed unit: for salt it means 1.5–3.5 g.** The robot therefore needs gram-based recipes, not spoon counts.

## Recipe index
Videos are at `https://youtube.com/watch?v=<id>`. Doses are in g as he states them. "→" marks the order of wok additions.

| # | dish | video | key amounts and sequence |
|---|---|---|---|
| 1 | 回锅肉 | v72yoabCHXA | 后腿肉 500 g boiled 30 min with 料酒 30 g. Stir-fry: pork 60 s → 豆豉 → 豆瓣 5 g (off heat) → 姜 20 g + 蒜 + 红椒 15 g → premixed 甜面酱 4 g + 老抽 4 g → 味精 1 g + 糖 + 米醋 1 g (wok edge) → 蒜苗 150 g for 8–15 s |
| 2 | 鱼香肉丝 (重庆) | t-gEVqs_Fg0 | 里脊 300 g marinated with 盐 2 g, 料酒 5 g, ½ egg white. 碗汁: 盐 2, 味精 1, 鸡精 1, 糖 30, 保宁醋 20, 生抽 5, 汤 40, 水淀粉. Meat at 180 °C together with 红油豆瓣 1勺 → 30 s → 姜蒜 (蒜 30 g) → 10 s → 葱 → ~60 s → 碗汁 (re-stirred) |
| 3 | 宫保鸡丁 | wEkVkT6IU9M | Marinade: 盐 0.5, 料酒 5, 老抽 1, 玉米淀粉 3. 碗汁: 料酒 15, 生抽 5, 醋 2, 味精 1, 糖 5, starch. Meat passed through ~750 g oil (wok off fire). Then 干辣椒 5 g + 花椒 → 姜 10 g 蒜 → chicken → 碗汁 → 花生 30 g + 葱 → 红油 |
| 4 | 麻婆豆腐 | RU-0vjjvSiI | Tofu 400 g soaked in 90 °C salted water; 牛肉 50 g, 1 min → 花椒 1 min → 豆瓣 + 豆豉 → 姜蒜葱 + 辣椒面 → water → 盐/味精/胡椒/糖/老抽 → tofu 4 min. 水淀粉 at minutes 2, 3 and 4 (the last two off heat) → 花椒油 |
| 5 | 西红柿炒蛋 | 2hvQFxZBTVY | 3 eggs + 白醋 1 g, fried at 120 °C; tomato 300 g → 番茄酱 5 → water, 60 s → 盐 1 + 糖 1 → 水淀粉 → 明油 → eggs |
| 6 | 红烧肉 | K0_6YfqXYhA | 糖色 from 冰糖 30 + 水 30; blanch with 料酒 15; spices (八角 2, 香叶 2, 桂皮, 姜 15) → 酱油 5 (from the side) → water 1 cm over the meat → 糖色 → 60 min; salt etc. at minute 50 |
| 7 | 糖醋排骨 (老式) | slckZcok4eo | 排骨 750 g; steam 2–3 h; fry at 190–200 °C; reduce with 冰糖 + 老抽 → 白糖 "一两多" (~55 g, conv) → 醋 "about the same as the sugar"; tasted |
| 8 | 青椒肉丝 | wn0_7SMpw6o | Pork 300 g: 盐 1, 生抽 4, 老抽 2, egg white, starch. Cooked in 猪油 40 g at 120 °C; 蒜 20 + 姜 20 at 150 °C → 青椒 200 → pork → 盐 1.5 + 味精 1 → 生抽 3 (edge) → cold 明油 |
| 9 | 炝炒/酸辣土豆丝 | 9HbErcNKAIk | Potato 400 g blanched 20 s with vinegar; 6成 oil; chili + garlic → potato 15–40 s → 盐 1.5 + 糖 → 生抽 3 ml (edge; vinegar for the 酸辣 version) → 葱 |
| 10 | 干煸四季豆 | 4WU7xDeRZQc | Beans 400 g in 100 g oil at 4成, slow 煸 ~5–8 min with a little salt; 肉末 → 花椒 + 干辣椒 (one bowl per bowl of beans) → 蒜 (to cool) → beans → salt by hand, about twice the normal amount → 花椒油 |
| 11 | 水煮肉片 | hyiGCNwCMxU | 里脊 300 g: 盐 1.5, 胡椒 1, 酱油 5, 料酒 3, egg white + 土豆淀粉 7. 刀口辣椒: 干辣椒 15 + 花椒 3. Wok 1: vegetables. Wok 2: 姜蒜 20 + 泡椒 20 at 170 °C → 豆瓣 10 → water → 盐 2.5, 味精 1.5 → 水淀粉 → pork; finish with 210 °C 菜籽油 poured over |
| 12 | 可乐鸡翅 | mmzoO7e4j-8 | Wings fried at 150 °C on ginger, 6 min → 可乐 ~600 g → 糖 10, 生抽 3, 糖色 → 15 min, then reduce |
| 13 | 清炒/白灼/蚝油 西兰花 | U_Xkq3Ots3w | Soak in salt water 10 min; blanch with 盐 2勺 + oil; 清炒: 蒜 → water → 盐 + 糖 → thin 芡 → broccoli → 明油 |
| 14 | 地三鲜 | h3Jtrv7Y6Jc | Potato and eggplant (dusted with starch) deep-fried 80 s at 6成; 蒜 20 → 蚝油 5 → 酱油 3 (edge) → water → 老抽 → 盐/糖 → 水淀粉 → 明油 → vegetables |
| 15 | 小炒肉 | kwhW6LOpfZo | 里脊 marinated with 盐 1 and slide-cooked in oil; 五花 100 g sliced 1 mm (from frozen), 60 s → 姜蒜 10/10 + 二荆条 150, 40 s → 盐 1, 味精 1, 鸡精 1, 蚝油 2 → 生抽 2 (edge) → 蒜苗 |
| 16 | 风味茄子 | sa2ayPSYEBk | Eggplant coated 3 times with 土豆淀粉 (10 + 30 + 40 = 80 g); fried at 180 °C. Sauce: 水 30, 生抽 8, 蚝油 3 (fan), 鸡精 0.5 → 明油 → eggplant |
| 17 | 鱼香茄子 (少油) | bJLjJ-qF89I | Eggplant 500 g steamed 15 min; 肉末 150 → 蒜 20, 姜 15, 泡椒 30 → 鱼香汁 (盐 1, 味精 1, 糖 20, 酱油 10, 醋 6, 水 30, 淀粉 3) → eggplant 30 s |
| 18 | 蚂蚁上树 | cb342Wl_yVc | 红薯粉 150 g soaked 15 min; 花椒 → 肉末 100 g for 40 s → 姜蒜 + 泡椒 15 → 豆瓣 3 → noodles 30 s → 生抽 2 (edge), 老抽 2, 盐, 味精 1, 糖 → 蒜苗 + 葱 → 葱油. No water |
| 19 | 辣子鸡 | NqHI1CJU-Rg | Marinade: 盐 2.5, 淀粉 3, oil 10. Fried at 210 °C, 60 s, then 240 °C off the stove, 20 s. 菜籽油 20 g at 180 °C: 花椒 30 → chili mix 80 → 姜 30, 蒜 20, 葱头 20, 30 s → chicken, 2 min → 味精 2 + 糖 → 米醋 1 (edge) → 花生 40 + 芝麻 10 → 花椒油 5 + 香油 10 |
| 20 | 酸菜鱼 | gONExIBbazI | 草鱼 1 kg; fillets: 盐 2, 啤酒 20, ½ egg white, 淀粉 5. Pickles 380 g; fish bones 2 min → pickles → hot water, 3 min → 盐 2, 糖 1, 胡椒, 白醋 → fish off heat, 15 s → pour oil heated to 8成 |
| 21 | 茄汁糖醋里脊 | TDWG-pCFiAY | Batter: 面粉 50, 玉米淀粉 90, 啤酒 15, 水 40. Fried at 5成 for 2 min, then 200 °C for 90 s. Sauce: 番茄酱 50 + 橙汁 + 白醋 + 冰糖 → 水淀粉 → 明油 |
| 22 | 京酱肉丝 | JKFpxkeXwyQ | 里脊 300 g: 料酒 15, 老抽 3. 蒜蓉 → 生抽 ~2 → 料酒 ~4 (edge) → 甜面酱 3勺 ≈ 10 g → water (edge) → 糖 2勺 ≈ 5 g |
| 23 | 葱爆羊肉 | BdTZURT3uL4 | Lamb soaked in 小苏打 water. 碗芡: 料酒 30, 生抽 5, 老抽 5, 蚝油 5, 糖 1, 味精 2, 鸡精 2, 汤 30, 玉米淀粉 10. 姜蒜 → 大葱 250 g → 碗芡. He says the 碗芡 is mandatory for this dish |
| 24 | 蛋炒饭 | EvE5cYNXufY | Cold rice (amount not given) + 2 eggs; very low heat 5 min; a little soy along the edge; no salt |
| 25 | 担担面 | X3MyQUEQ5Wo | Bowl seasoning (no wok): 芝麻酱 ~3 g, 猪油, 盐, 糖, 芽菜, 红油, 花椒面, 蒜泥; 五花 150 g fried crisp |
| 26 | 酸辣汤 | mQ_2W5zUd44 | 盐 ~7 g, 鸡精 ~2 g, 胡椒 ~4 g → 勾芡 off heat until it forms 20 cm strands → 香醋 ×2 additions; 3 eggs, 虾米 20 g |
| 27 | 拍黄瓜 | x6_aDVi4_uY | Dressing: 蒜 15, 小米辣 10, 盐 2, 味精 1, 酱油 3, 香醋 1, 香油, 红油 20 |
| 28 | 白切鸡 / 口水鸡 | 27qBWkkr8HY | Poaching: 盐 "二三两" (100–150 g) in a big pot, steep 30+10 min. 口水鸡 sauce: 蚝油 1.5勺, 糖 3勺, 醋 2勺, 红油 (lots), 花椒面 |
| 29 | 红烧鲤鱼 | cHXO5befcUI | Fish 900 g fried 5 min (salt 1勺 ≈ 2 g in the oil); 五花 → 姜蒜 → 香菇/葱 → 蚝油 10 → 生抽 6 (edge) → beer 500 ml → 盐 1.5, 五香粉 ½勺, 糖色 4 → 6 min → 水淀粉 → 明油 |
| 30 | 手撕包菜 | JZutepq2GLM | Blanch to 30–40 % done → char with oil only on high → little lard + chili + seeds + garlic → cabbage → salt/味精/糖 → 酱油 (edge) → 醋 (edge) |
| 31 | 小炒茄子 | Kjkr27b3YwA | 五花 200 g, 1 min → 蒜 + chilies → eggplant 4 min → 盐 ~2, 味精 ~1, 蚝油 3 → 生抽 ~3 (edge) → 老抽 |
| 32 | 黄焖鸡 | oD20MDwF5no | Half a chicken; 冰糖 20 g 糖色 → chicken 2 min → 香菇/姜蒜 → 蚝油 10 + 黄豆酱 10 + 老抽 → 黄酒 (edge) → water → 盐 ~2, 味精 ~1 → 15 + 10 min |
| 33 | 韭菜炒鸡蛋 | XmTJrRilq40 | 韭菜 130 g, 5 eggs. All seasoning goes into the egg: 盐 ~2, 胡椒 ~1, vinegar drops, 水淀粉 |
| 34 | 清蒸鲈鱼 | mVZC-iu60BQ | 鲈鱼 600 g rubbed with 姜葱猪油, steamed 8 min; hot oil poured over + 鱼酱油 200 g |
| 35 | 清炒菠菜 / 炝炒油麦菜 | YRWN6seKz2w | Amounts not given. 清炒: salt + sugar dissolved in hot water in the ladle first. 炝炒: more oil, no water |
| 36 | 鱼头豆腐汤 | BvG46EWuH9E | Fish head fried in ~500 g oil, which is **kept and reused**; water 2 kg, low heat 15 min; only salt (<3 g), added in the serving bowl |
| 37 | 椒盐排骨 | vFevFLKHn4o | 排骨 1 kg; marinade 盐 ~2; 蒜 150 g fried; ribs fried at 6成 then 210 °C for 3 min; 椒盐粉 3 g (homemade from 盐 150 g + spices, ground, mixed 2:1 with 味精) |
| 38 | 焦溜肉段 | JDnC-M2Bq48 | Batter: 土豆淀粉 140 + 水 80. Fried at 150–160 °C, then 200 °C for 20 s. 碗汁: 汤 140, 米醋 20, 绍酒 15, 水淀粉 25, 生抽 25, 糖 10, 香油 10. Done in 40 g oil |
| 39 | 土豆烧牛腩 | 0Kb1S6MgUZE | Brisket boiled 60 min; spices (off heat) → 豆瓣 → 甜面酱 1勺 → beef → 料酒 (edge) → 老抽 → 泡椒 → water → potato → salt/pepper/sugar → 30 min → 糖 3 + 生抽 5, reduce 2 min → 葱油 |
| 40 | 鸡蛋肉丝炒面 | qY04dt5FFfI | 2 blocks of instant noodles soaked 7 min; 盐 ~1 + 鸡精 ~1 → 生抽 ~3 (edge) → 老抽 → vegetables → oil (edge) → egg strips |
| 41 | 酱油炒饭 | 1Q-5eIBfBDQ | 隔夜饭 + 3 eggs + 萝卜干; oil (edge) → 生抽 10 g once the rice starts jumping → oil (edge), 1 min → 葱 |
| 42 | 脑花豆腐 | ivcFXtMGdE8 | 内酯豆腐 380 g; 菜籽油 ~30 g → 火锅底料 ~50 g → 豆瓣 一瓢半 → water → seasoning (tasted) → 10–20 min → 水淀粉 in 4 small additions, judged by eye |

## 1. Seasoning list and dose ranges
The table counts doses per addition event. These are excluded from the dose statistics: salt used for washing or soaking, the 100–150 g salt in the 白切鸡 poaching pot, the 150 g salt for the 椒盐 batch, and starch used for 挂糊 (shown in the staples section instead).

| seasoning | type | recipes (of 42) | min g | median g | max g | doses with g | variants seen |
|---|---|---|---|---|---|---|---|
| 盐 | powder | 38 | **0.5** | 2 | 7 | 28 | |
| 白糖 | powder | 31 | 1 | 7.5 | 55 (conv) | 12 | |
| 醋 | thin liquid | 20 | 1 | 2.5 | 55 (conv) | 10 | 白醋, 米醋, 保宁醋, 镇江醋, 陈醋, 香醋 |
| 生抽 | thin liquid | 19 | 2 | 3.5 | 25 | 18 | ("酱油" in en subtitles, 9 recipes, 3–10 g, is probably the same thing) |
| 味精 | powder | 19 | 1 | 1 | 2 | 13 | |
| 淀粉 (上浆/碗汁) | powder | 16 | 3 | 4 | 10 | 6 | 玉米淀粉, 土豆淀粉 |
| 老抽 | thin liquid (dark) | 15 | 1 | 2.5 | 5 | 6 | |
| 胡椒粉 | powder | 15 | 1 | 1 | 4 | 3 | 白胡椒, 黑胡椒 |
| 花椒 | whole spice | 14 | 3 | – | 30 | 2 | 红花椒, 青花椒 |
| 料酒 | thin liquid | 12 | 3 | 15 | 30 | 11 | 绍酒, 黄酒 |
| 水淀粉 | **suspension (starch settles)** | 12 | – | 25 | – | 1 | 土豆淀粉 |
| 干辣椒 | whole spice | 10 | 5 | 15 | 80 | 3 | 灯笼椒, 子弹头, 七星椒 |
| 蚝油 | viscous liquid | 9 | 2 | 5 | 10 | 7 | |
| 明油 (finishing oil) | oil | 8 | – | – | – | 0 | |
| 豆瓣酱 | paste | 7 | 3 | 4.5 | 10 | 4 | 郫县豆瓣, 红油豆瓣 |
| 鸡精 | powder | 7 | **0.5** | 1 | 2 | 6 | |
| 泡椒 (minced) | wet pickled paste | 6 | 15 | 20 | 30 | 3 | |
| 猪油 | semi-solid fat | 5 | – | 40 (as frying fat) | – | – | plain lard, 姜葱猪油 |
| 红油 (chili oil with sediment) | viscous oil | 4 | 20 | 20 | 20 | 1 | |
| 花椒面 | powder | 4 | – | – | – | 0 | 青花椒面 |
| 冰糖 | lumps | 4 | 20 | 25 | 30 | 2 | 土冰糖 |
| 香油 | oil | 4 | 5 | 10 | 10 | 4 | |
| 甜面酱 | paste | 3 | 4 | 4 | 10 | 3 | |
| 花椒油 | oil | 3 | 5 | 5 | 5 | 2 | |
| 糖色 (homemade caramel) | viscous | 3 | 4 | 4 | 4 | 1 | |
| 啤酒 | thin liquid | 3 | 15 | 20 | 500 | 3 | |
| 番茄酱 | paste | 2 | 5 | – | 50 | 2 | |
| 豆豉, 八角, 熟芝麻, 花生, 葱油 | various | 2 each | 10–40 (sesame, peanuts) | | | | |
| 1 recipe each | | 1 | | | | | 泡姜, 芽菜, 辣椒面, 桂皮, 香叶, 草果, 小茴香, 白胡椒粒, 五香粉, 黄豆酱 10, 芝麻酱 3, 火锅底料 50, 浓缩橙汁, 可乐 600, 面粉 50, 鱼酱油 200 (homemade), 椒盐粉 3 (homemade), 小苏打, 辣椒籽 |

Fresh aromatics (number of recipes): 蒜 27, 葱 (大葱/小葱/香葱) 22, 姜 20, 小米辣/二荆条 5, 蒜苗 ~6 (mostly listed as an ingredient), 香菜 2. The 酸菜鱼 pickles (酸菜 200, 泡萝卜 100, 泡姜 50, 野山椒 30 g) count as ingredients.

**Dispensing resolution:**
- The smallest doses he states are 0.5 g (盐, 鸡精) and 1 g (味精, 白糖, 醋, 老抽, 胡椒粉). Powders therefore need about ±0.2 g resolution, and thin liquids about ±0.5 g.
- The largest single seasoning doses are 30 g sugar or 料酒, 25 g 生抽, and 20–55 g vinegar or sugar in sweet-and-sour dishes. That is a dynamic range of about 100:1.
- Bulk liquids run from 30 g up to 2 kg: water or stock (30–140 g in 碗汁; 0.5–2 kg for braises and soup), beer 500 ml, cola 600 g.

**Core set** (≥7 of 42 recipes): 盐, 白糖, 醋 (at least 白醋 + one dark vinegar such as 香醋/陈醋/保宁醋), 生抽, 老抽, 味精, 鸡精, 胡椒粉, 料酒, 蚝油, 豆瓣酱, 淀粉 / 水淀粉, 花椒, 干辣椒, plus cooking oil and 明油.

**Second tier:** 泡椒, 猪油, 红油, 香油, 花椒油, 花椒面, 冰糖, 甜面酱, 番茄酱, 豆豉, 八角.

## 2. Per-dish dispensing metrics
Column key:
- **seas** = distinct seasonings, excluding water and fresh aromatics.
- **arom** = distinct fresh aromatics.
- **events** = wok addition events that include a seasoning or aromatic.
- **tightest gap** = smallest gap between consecutive wok additions (`est` or `stated`).
- **stated min** = the tightest gap he explicitly gives.
- **premix** = 碗汁 / 料碗 bowls he already pre-mixes.
- **bowls** = how many bowls it would take if every pre-portionable event were prepared before heating.
- **live** = events dosed by eye or by taste during cooking (incremental 勾芡, tasting).
- **edge** = additions poured along the wok edge.
- **multi** = events where two or more seasonings go in together.

| dish | seas | arom | events | tightest gap s | stated min s | premix | bowls | live | edge | multi |
|---|---|---|---|---|---|---|---|---|---|---|
| 回锅肉 | 9 | 4 | 5 | 3 est | 60 | 1 | 5 | 0 | 1 | 2 |
| 鱼香肉丝 | 12 | 3 | 4 | **0 (豆瓣 goes in with the meat)** / 10 | 10 | 1 | 4 | 0 | 0 | 1 |
| 宫保鸡丁 | 13 | 3 | 5 | 3 est | – | 1 | 5 | 0 | 0 | 3 |
| 麻婆豆腐 | 12 | 4 | 9 | 10 est | 60 | 0 | 6 | 3 | 0 | 3 |
| 西红柿炒蛋 | 6 | 0 | 5 | 3 est | 60 | 0 | 4 | 1 | 0 | 1 |
| 红烧肉 | 10 | 2 | 5 | 5 est | 600 | 1 | 5 | 0 | 1 | 2 |
| 糖醋排骨 | 10 | 0 | 3 | 10 est | – | 0 | 1 | 2 | 0 | 1 |
| 青椒肉丝 | 9 | 2 | 4 | 3 est | – | 0 | 4 | 0 | 1 | 2 |
| 土豆丝 | 6 | 2 | 4 | 3 est | 15 | 0 | 4 | 0 | 1 | 2 |
| 干煸四季豆 | 7 | 1 | 5 | 5 est | – | 0 | 4 | 1 | 0 | 2 |
| 水煮肉片 | 12 | 3 | 7 | 5 est | 20 | 1 | 6 | 1 | 0 | 3 |
| 可乐鸡翅 | 5 | 2 | 3 | 10 est | 360 | 0 | 3 | 0 | 0 | 2 |
| 西兰花 | 7 | 2 | 5 | 3 est | – | 0 | 4 | 1 | 0 | 2 |
| 地三鲜 | 9 | 2 | 8 | 3 est | – | 0 | 7 | 1 | 1 | 2 |
| 小炒肉 | 9 | 3 | 3 | 3 est | 20 | 0 | 3 | 0 | 1 | 2 |
| 风味茄子 | 9 | 3 | 3 | 3 est | – | 1 | 3 | 0 | 0 | 1 |
| 鱼香茄子 | 7 | 2 | 2 | 15 est | – | 1 | 2 | 0 | 0 | 1 |
| 蚂蚁上树 | 9 | 2 | 5 | 3 est | 30 | 0 | 5 | 0 | 1 | 2 |
| 辣子鸡 | 14 | 3 | 7 | 3 est | 30 | 1 | 7 | 0 | 1 | 4 |
| 酸菜鱼 | 7 | 1 | 2 | 20 est | 120 | 0 | 2 | 0 | 0 | 1 |
| 茄汁糖醋里脊 | 10 | 0 | 3 | 3 est | – | 1 | 2 | 1 | 0 | 0 |
| 京酱肉丝 | 7 | 1 | 6 | 3 est | – | 0 | 6 | 0 | 2 | 0 |
| 葱爆羊肉 | 10 | 3 | 2 | 5 est | – | 1 | 2 | 0 | 0 | 1 |
| 蛋炒饭 | 1 | 1 | 2 | 5 est | – | 0 | 2 | 0 | 1 | 0 |
| 担担面 (no wok sauce) | 8 | 2 | 0 | – | – | 0 | 0 | 0 | 0 | 0 |
| 酸辣汤 | 6 | 1 | 5 | 5 est | – | 0 | 4 | 1 | 0 | 1 |
| 拍黄瓜 (cold) | 6 | 3 | 0 | – | – | 0 | 0 | 0 | 0 | 0 |
| 白切/口水鸡 (sauces) | 8 | 4 | 0 | – | – | 0 | 0 | 0 | 0 | 0 |
| 红烧鲤鱼 | 10 | 4 | 9 | 3 est | 360 | 0 | 8 | 1 | 1 | 3 |
| 手撕包菜 | 8 | 1 | 4 | 3 est | – | 0 | 4 | 0 | 2 | 2 |
| 小炒茄子 | 7 | 2 | 4 | 3 est | 60 | 0 | 4 | 0 | 1 | 2 |
| 黄焖鸡 | 11 | 3 | 8 | 3 est | 60 | 0 | 8 | 0 | 1 | 3 |
| 韭菜炒鸡蛋 | 4 | 0 | 0 | – | – | 0 | 0 | 0 | 0 | 0 |
| 清蒸鲈鱼 | 2 | 0 | 0 | – | – | 0 | 0 | 0 | 0 | 0 |
| 清炒菠菜/炝炒油麦菜 | 4 | 1 | 4 | 5 est | – | 0 | 4 | 0 | 0 | 3 |
| 鱼头豆腐汤 | 1 | 1 | 1 | – | 900 | 0 | 1 | 0 | 0 | 0 |
| 椒盐排骨 | 7 | 4 | 3 | 3 est | – | 1 | 3 | 0 | 0 | 1 |
| 焦溜肉段 | 8 | 3 | 3 | 3 est | – | 1 | 3 | 0 | 0 | 1 |
| 土豆烧牛腩 | 13 | 3 | 10 | 5 est | 120 | 0 | 10 | 0 | 1 | 3 |
| 鸡蛋肉丝炒面 | 5 | 0 | 4 | 3 est | – | 0 | 4 | 0 | 2 | 1 |
| 酱油炒饭 | 3 | 1 | 4 | 3 est | 60 | 0 | 4 | 0 | 2 | 0 |
| 脑花豆腐 | 9 | 1 | 6 | 5 est | – | 0 | 4 | 2 | 0 | 1 |

**Summary:**
- Distinct seasonings per dish: median 8, max 14 (辣子鸡). Fresh aromatics per dish: median 2–3.
- Wok seasoning events per dish: median 4, max 10 (土豆烧牛腩), 9 for 麻婆豆腐 and 红烧鲤鱼.
- 30 of the 39 dishes with wok events have consecutive additions ≤5 s apart. This is the typical end-of-stir-fry run: 盐 + 味精 → 生抽 (edge) → 明油 → 葱, all within about 10–15 s.
- The tightest gaps he states himself:
  - 0 s: 豆瓣 goes in together with the meat (鱼香肉丝).
  - 10 s: 姜蒜 → 葱 (鱼香肉丝).
  - 15 s: potato → salt (土豆丝).
  - 20 s: vegetables → salt (水煮肉片); aromatics → returning the meat (小炒肉).
- He pre-mixes a 碗汁 / 碗芡 in 12 of 42 dishes. He says it is mandatory for 葱爆羊肉 and that it "shortens the cooking" (宫保鸡丁).
- 11 dishes have live-dosed steps: incremental 勾芡 (麻婆 ×3, 脑花豆腐 ×4), tasting (糖醋排骨, 脑花豆腐), or salt "to taste".
- 17 dishes pour a liquid **along the wok edge** (生抽, 醋, 料酒, 黄酒, oil).

## 3. Staples: rice, flour, starch, noodles, oil

**Stated amounts:**

| staple | what he uses |
|---|---|
| Rice (米) | Fried-rice dishes use "a plate of cold or overnight rice", with no weight given. Two techniques: mix salt into overnight rice so it keeps, and add some dry starch to absorb moisture. Plain rice for the meal is not covered in his videos. |
| Noodles (面) | 担担面: any 挂面 / 水面 / handmade noodles, amount not given, boiled with cold water added to hold a gentle boil, then cooled in cold boiled water. 炒面: 2 blocks of instant noodles soaked 7 min in ≥90 °C water. 红薯粉条 150 g (蚂蚁上树). |
| Flour (面粉) | Only in batter: 50 g (糖醋里脊). |
| Starch, 上浆 (marinade) | 3–7 g per ~300 g meat. 宫保 3 g, 辣子鸡 3 g, 酸菜鱼 5 g, 水煮肉片 7 g, usually with an egg white. |
| Starch, in 碗汁 | 3–10 g (鱼香茄子 3, 葱爆羊肉 10); 25 g 水淀粉 (焦溜). |
| Starch, 挂糊/拍粉 (coating) | 80–140 g per dish: 风味茄子 80 g 土豆淀粉; 糖醋里脊 90 g 玉米淀粉 + 50 g flour; 焦溜 140 g 土豆淀粉. |
| Starch types | His starch comparison video (2e_hY2rVLrs): **玉米淀粉** for 上浆 / 挂糊 / frying; **土豆生粉** for 勾芡. Potato starch gelatinises fast and cannot be corrected once over-added, so he adds it gradually and off heat. **Stock both kinds.** |
| Oil, wok | Mostly "适量". Where stated: 20 g (辣子鸡), 30 g (脑花豆腐), 40 g (青椒肉丝 lard, 焦溜), 100 g (干煸四季豆, partly poured off). |
| Oil, 润锅 / 滑锅 | Nearly every stir-fry heats the wok, swirls in oil, **pours that oil back out**, then adds fresh oil (热锅凉油). |
| Oil, 过油 / deep-fry | 9 of 42 dishes deep-fry or pass meat through oil: 宫保, 糖醋排骨, 地三鲜, 风味茄子, 辣子鸡, 糖醋里脊, 鱼头汤, 椒盐排骨, 焦溜. 小炒肉 and 黄焖鸡 also shallow-fry. The volumes he states are 750 g (宫保 滑油) and ~500 g (鱼头); the rest are "宽油", not quantified. |
| Deep-fry temperatures | 150–160 °C (first fry), 180 °C, 190–200 °C, 210 °C, and 240 °C with the wok off the stove (second fry). |
| Oil reuse | He reuses explicitly in 鱼头汤: ginger and scallion are fried in the oil to deodorise it "so it can be used a second time". In 辣子鸡 and 焦溜 he removes debris between fries. He criticises restaurants that fry 四季豆 in reused dark oil. |
| Other fats | **Lard (猪油)** in 5 dishes (青椒肉丝, 手撕包菜, 椒盐排骨, 担担面, 鲈鱼 as 姜葱猪油); **菜籽油** for 泼油 and 辣子鸡. |

**Per-meal estimate for 2–4 people.** This is an assumption, not from his videos. His portions are about 300 g meat + 150–400 g vegetables per dish, which is one plate for 2–3 people. A meal would be 2–3 dishes + soup + rice:
- Rice: 75–100 g raw per adult, so 200–400 g raw.
- Stir-fry oil: 20–40 g per dish, so 60–120 g per meal, not counting 润锅 oil that is poured back out. The 中国居民膳食指南 target is 25–30 g/person/day.
- Starch: about 10–20 g per meal, or about 100 g if a battered dish is included.
- Deep-fry oil: design for a working volume of **0.75–1.5 L** (his stated amounts are 500–750 g) and an **oil-return/filter container** for reuse.

## 4. Fridge and freezer items
Pack sizes he states are marked *(WG)*. The others are typical Chinese retail sizes and should be verified.

| category | items in these 42 recipes | storage | typical pack |
|---|---|---|---|
| Pork | 里脊/通脊 (6 dishes), 五花/半肥瘦 (8), 后腿 (1), 前夹 (1), 排骨 (2), unspecified 猪肉 (1) | fridge 1–2 d / freezer | 300–500 g trays |
| Beef, lamb | 牛腩, 牛肉末, 羊前夹 | fridge / freezer | 300–500 g |
| Poultry | 鸡腿, 三黄鸡 (whole or half), frozen 鸡翅 | fridge / freezer | half or whole bird ~1–1.5 kg; wings 500 g |
| Fish | 草鱼 1 kg, 鲤鱼 900 g, 鲈鱼 600 g, fish head, all bought live and killed fresh | same day, fridge | whole fish |
| Offal / blood | 猪脑, 猪血 | fridge, short life | 1 副 / 1 block |
| Eggs | in 13 dishes (2–5 whole eggs, or ⅓–1 egg white/yolk for 上浆) | fridge | 10–30 |
| Tofu | 嫩豆腐 400 g, 老豆腐 (卤水), 内酯豆腐 380 g *(WG)*, 千张 | fridge, 1–3 d | 350–500 g |
| Processed | 火腿肠, 培根, 腊肠, 鲜木耳 | fridge | |
| Opened sauces | 蚝油, 豆瓣酱, 甜面酱, 黄豆酱, 番茄酱, 芝麻酱, 火锅底料 (500 g block *(WG)*, ~50 g per dish), 红油 | fridge after opening | 蚝油 ~500 g bottle; 豆瓣 500 g–1 kg; 甜面酱/番茄酱 ~300 g |
| Pickles | 泡椒/泡红椒, 泡姜, 野山椒, 酸菜, 泡萝卜, 芽菜, 萝卜干 | fridge after opening (wet, brine) | 200–500 g bags/jars |
| Homemade | 糖色, 姜葱猪油, 鱼酱油 (200 g per dish), 椒盐粉, 刀口辣椒, 红油, 葱油 | fridge (糖色, lard, 鱼酱油) / jar | batch |
| Fresh aromatics | 葱 (大葱/小葱/香葱), 姜, 蒜, 小米辣, 二荆条, 蒜苗, 香菜, 韭菜/韭黄 | 葱, 香菜, chilies, 韭菜 in the fridge crisper; 姜 and 蒜 cool and dry | per bunch |
| Leftover rice | 隔夜饭, wrapped, with salt added | fridge overnight | 1 plate |
| Freezing as a technique | 五花 frozen hard to slice 1 mm (小炒肉); 里脊 frozen 1 h before cutting shreds (鱼香肉丝, 京酱肉丝) | freezer | – |

## 5. Techniques that affect automation
1. **Wok pre-oiling (润锅/滑锅 + 热锅凉油).** He heats the wok until it smokes, swirls oil, pours it out, then adds fresh oil (宫保: oil in, then off the fire, then meat). The robot needs to tip hot oil into a heat-proof return pot and measure oil temperature by IR: 120 / 150 / 170 / 180 / 210 / 240 °C are all named.
2. **Off-heat moments (离火).** Adding oil, spices, 豆瓣, starch or fish off the heat appears in about 10 dishes: 宫保, 小炒肉, 牛腩, 麻婆 (2 of 3 勾芡), 酸辣汤, 西兰花, 酸菜鱼, 辣子鸡 at 240 °C. With a fixed hob, this means cutting the flame instantly or lifting the wok.
3. **Edge pouring (锅边淋入).** 生抽, 醋, 料酒, 黄酒, and oil "to raise the wok temperature" are poured onto the hot wok wall, not the food (17 dishes). He says this develops the soy aroma. The liquid nozzle or pour bowl must be able to target the rim.
4. **Bursts of 3–4 additions in 10–15 s at the end of a stir-fry.** Either the dispenser cycles fast enough for that, or the robot pre-portions them: combine the seasonings into one bowl and keep only the edge-pour liquid and 明油 separate. Most of his 碗汁 contain starch and **must be re-stirred right before pouring** (he says this explicitly in 鱼香肉丝).
5. **Gradual 勾芡 judged by eye.** 麻婆: 3 additions at minutes 2, 3 and 4. 脑花豆腐: start when 30–40 % of the food is above the liquid, then 4 small additions until the bottom of the wok looks dry and the oil shines. 酸辣汤: until it forms 20 cm strands. This needs vision feedback and a small-dose 水淀粉 dispenser that agitates the suspension.
6. **Tasting and adjusting.** 糖醋排骨 (sweetness), 脑花豆腐 ("taste now, top up if needed"), salt "to taste". A robot needs fixed gram recipes plus a salinity or refractometer check, or it has to accept no adjustment.
7. **Order-critical aromatics.** 姜蒜 go in 10–40 s before 葱. Garlic is added specifically to cool the wok so dried chilies don't burn (干煸四季豆). Dried chilies are fried until dark brown but not black. 豆瓣 is fried on low heat until the oil turns red. These are vision- and temperature-gated, not just timed.
8. **Two-stage deep-fry (复炸)** with skimming between fries (辣子鸡, 糖醋里脊, 椒盐排骨, 焦溜): a hot-oil safety case for the arm.
9. **Finishing oils (淋明油 / 泼油).** 明油 at the end (8 dishes); 菜籽油 heated to 210–240 °C and poured over the plated dish (水煮肉片, 酸菜鱼). Pouring hot oil over a bowl needs a second heated vessel or the wok itself.
10. **Hand techniques:**
    - Marinades are stirred in one direction for 1–2 min until tacky (上劲), with salt added in several portions (京酱肉丝).
    - Salt is sprinkled by hand for even coverage (干煸四季豆).
    - Salt and sugar are pre-dissolved in hot water in the ladle (清炒).
    - Starch is applied in 3 coats with water sprinkled between them (风味茄子).
    - 豆瓣 and minced 泡椒 are wet, sticky pastes.

    The robot needs a mixing tool, a paste dispenser (positive displacement or scoop-and-scrape), and a lard dispenser, because lard is semi-solid.
11. **Homemade intermediates** (糖色, 椒盐粉, 刀口辣椒, 红油, 姜葱猪油, 鱼酱油) are better made in batches and stored than reproduced in each dish.
12. **Water and stock** are needed in nearly every braise and in many sauces, in amounts from 30 g to 2 kg ("适量", "to 1 cm over the meat"). A metered hot and cold water feed at the wok is required, and ideally stock too.

**Bottom line for the dispenser:**
- About 15–20 permanently loaded items cover most dishes:
  - Powders: 盐, 白糖, 味精, 鸡精, 胡椒粉, 花椒面.
  - Thin liquids: 生抽, 老抽, 料酒, 白醋, a dark vinegar, water.
  - Viscous: 蚝油.
  - Paste: 豆瓣酱.
  - Oils: cooking oil, 香油/花椒油/红油.
  - Starch: 水淀粉 (agitated), plus dry 玉米淀粉 and 土豆淀粉.
  - Whole spices: 花椒 and 干辣椒 (bulky; 5–80 g).
- Plus 5–10 manually loaded "料碗" slots per dish for pastes, pickles, aromatics and premixed 碗汁.
- Powders need 0.5 g resolution; liquids need 1 g.
- Sweet-and-sour dishes need up to about 50 g of sugar or vinegar in a single dose.
