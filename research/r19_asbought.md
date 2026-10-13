# R19 as-bought states: what the market does, what the robot does (2026-10-13)

**The user's rule (2026-10-13):** "那些剁块，鱼和鱿鱼这些肯定摊主会搞定，你看我给你的视频他一般买回来什么样我们就是什么样".
- Every ingredient starts in the state the reference cook brings home from the market.
- Everything he does himself is the robot's job.

**How I applied it.** The as-bought state is the first state shown in the videos, normally on the ingredient spread at the start. Every step from there to the pan is the robot's, **including steps he does off camera**. Example: in meal C the potatoes are unpeeled on the spread and peeled on the board, so he peeled them himself and the robot must too. Section 5 lists these off-camera steps, in case the user wants to rule on them separately.

**Sources.** The three videos (`home3/index.txt`: v1 = meal A, v2 = meal B, v3 = meal C), their Whisper transcripts, and the audit being corrected (`sim/r10/claude/R19_PREP_AUDIT.md`, 38 prep items).

**Labels**
- **[seen]**: visible in a frame.
- **[heard]**: in the transcript or the burned-in caption. Quotes give the caption wording where Whisper misheard it.
- **[inferred]**: the state before and after is seen, but the step itself is off camera.
- **[assumed]**: not shown at all. The most likely Chinese wet-market or supermarket state; this needs confirming.

**Frame references**
- `fN/NNN.jpg` is the 2 s frame of video N, at t = (NNN−1)×2 s. For example, `f1/005.jpg` = v1 at 0:08.
- `extra/vN_tS.jpg` is a frame extracted this round at S seconds, 720 px or 480 px wide. `extra/*_m_*.jpg` and `extra/*_A-B.jpg` are side-by-side strips and 0.5–1 s montages.
- All frames are in the session scratchpad folder `home3/`.

---

## 1. Summary

1. **What the stall does** (confirmed in the videos, so the user's OK is no longer needed):
   - **Ribs are bought chopped** in all three meals [seen]: about 3–5 cm bone-in pieces, smaller for the steamed ribs (C).
   - **The sea bass is bought whole and gutted** [seen: the belly is already open]. Whether it was also scaled cannot be told from the frames.
   - **The squid is bought as cleaned tubes** [seen]: no head, no tentacles, skin off.
2. **The stall does *not* cut the fish or the squid for him.** On camera he:
   - splits the fish along the back (开背);
   - slits the squid open, scores it both ways (麦穗花刀) and cuts the pieces.

   So "鱼和鱿鱼摊主会搞定" is true for cleaning only. Under the user's own rule, the back-split and the squid scoring stay robot work.
3. **Everything else is bought raw and whole**, apart from the dry goods:
   - taro (a large hairy corm), potatoes, luffa (unpeeled, flower still on), bamboo shoot (in its husk), broccoli (whole head);
   - garlic (heads), ginger (whole knob);
   - tomatoes, okra (with caps), baby cabbage (whole heads), cucumber, bell peppers, chilies, snow peas, garlic sprouts and scallions (whole stalks);
   - pork belly (a skin-on block in A, a long skin-on strip in B) and lean pork (a block).
4. **Recount against the audit's 38 items:**
   - **No item disappears.** The three things the stall does (rib chopping, fish gutting, squid cleaning) were already outside the audit's 38 as "(bought)".
   - **The purchase-form escape routes are closed** (audit §5.7). If the robot follows him, it cannot rely on buying shelled bamboo shoots, peeled garlic, 净菜 florets, a stall-split fish, squid strips instead of scoring, a luffa swap, or skipping the tomato peeling.
   - **About 8 operation instances are added or corrected:**
     - ginger peeling ×3 meals;
     - okra cap trimming and halving;
     - the fish back-split;
     - dried-chili snipping ×2;
     - decorative carrot slices.
   - **One audit step does not occur:** pork-belly skin scraping. He levels the top of the blanched slab instead.
   - **Net:** prep demand is the same or slightly higher. The audit's 21–40 min of arm time per meal is a lower bound.
5. **Hard operations that remain** (§4): taro peeling, luffa peeling, bamboo husking, garlic and ginger peeling, broccoli florets, raw and cooked pork-belly cutting, lean-pork slicing, the fish back-split, squid scoring, tomato peeling, egg cracking, fine 丝 (三丝, potato julienne, chili shreds, celery strips), okra halving, and arranging food on plates and in cups.

---

## 2. As-bought table per ingredient

Columns: **As bought** | **What he does (on camera unless marked)** | **Left for the robot**.

### 2.1 Meal A (v1): 干锅土豆, 桂花糖芋头, 蚝油西兰花, 蒜蓉蒸丝瓜, 蛤蜊排骨盅

Ingredient list [heard 0:00]: "准备芋头，土豆，丝瓜，西兰花，文蛤，排骨，三层肉，还有一些配料".

| Ingredient | As bought | What he does | Left for the robot |
|---|---|---|---|
| 排骨 ribs (cups) | **Chopped bone-in pieces, ~3–4 cm** [seen `f1/005`, `extra/v1_t9.0.jpg`, `v1_t10.5.jpg`] | 4 pieces per cup, 4 cups [seen `f1/007`, `extra/v1_t14.5.jpg`; heard "每盅里面下四块排骨"]. Washing is not shown. | Portion 16 pieces into 4 cups; a rinse is [assumed] |
| 文蛤 clams | **Live, in the shell**, clean shells [seen `extra/v1_t9.0.jpg`; heard "文蛤"] | 3 per cup, a little salt, water to 90 %, cling film [seen `f1/009`–`012`; heard "三个文蛤…就一点盐就行了…清水加至九分满…保鲜膜"]. Purging and scrubbing are not shown. | Portion 12 clams; purge and scrub [assumed] |
| 姜 ginger | **Whole knob** [seen `extra/v1_t9.0.jpg`, top right]. The spread also holds peeled thick pieces, cut before filming [seen `extra/v1_t5.0.jpg`]. | Peeled pieces: one slab of ~1×6 cm per cup [seen `extra/v1_t14.5.jpg`; heard "一块生姜"]. Slices into the 干锅 [seen `f1/068` 2:14]. Peeling and cutting are [inferred]. | Peel; 4 thick slabs and a few slices |
| 芋头 taro | **Whole large corm, hairy skin, unpeeled** [seen `extra/v1_t5.0.jpg`]. "这个芋头也是我之前冰箱里面剩的" [heard 0:28]: he stores it whole. | Peels it upright with the cleaver: start seen 0:26–0:27, then a jump cut to fully peeled at 0:28 [seen `extra/v1_taro_22-32.jpg`]. Thick slices → strips → blocks of ~2.5–3 cm [seen `f1/017`–`020`]; spaced on a plate [seen `f1/021`; heard "像这样间隔开来"] | Peel a large corm; slice → strip → block; place ~20 blocks spaced on a plate |
| 土豆 potato | Already **peeled** on the A spread [seen `extra/v1_t5.0.jpg`]. As bought: **unpeeled** [inferred from meal C, where the same cook's potatoes are unpeeled on the spread]. | Peeling [inferred, off camera]. Halves, then irregular slices ~5 mm [seen `f1/031`–`035`, `extra/v1_m_a.jpg`]. Deep-fried. | Peel 3; slice |
| 三层肉 pork belly | **Skin-on block, ~10 cm** [seen `extra/v1_t9.0.jpg`; heard "三层肉"] | Thin slices ~3 mm, skin on [seen `f1/026`–`027`, `extra/v1_t50.5.jpg`, `v1_t134.5.jpg`] | Slice raw skin-on belly thin |
| 红椒 red chili | **Whole fresh long red chilies ×2** [seen `extra/v1_t5.0.jpg`] | Pieces for the 干锅 [result seen `f1/075` 2:28; heard "蒜苗红椒下"]; **fine shreds** for the luffa sauce [result seen `extra/v1_t214.5.jpg`; heard "碗中准备蒜末红椒"]. Cutting [inferred]. | Destem; pieces; fine shreds |
| 蒜苗 garlic sprouts | **Whole stalks with roots** [seen `extra/v1_t5.0.jpg`] | Diagonal sections ~4 cm [seen `f1/028`–`030`, `extra/v1_t56.5.jpg`] | Trim; sections |
| 干辣椒, 花椒, 十三香 | Dry pantry goods, whole dried chilies [seen `extra/v1_t9.0.jpg`] | Used whole [seen 2:18] | None (seasoning kit) |
| 西兰花 broccoli | **Whole head with leaves** [seen `extra/v1_t9.0.jpg`, `v1_t70.5.jpg`] | Cuts small florets with the cleaver [seen `f1/045`–`047`; heard "这个也太大了，改小一点"]. Soaks them in water with 1 spoon of salt [seen `f1/048`–`049`; heard "切完泡在水里面，加一勺盐，这样洗得更干净"]. Peels the stem with the cleaver, then thick slices [seen `f1/052`–`054`, `extra/v1_t103.5.jpg`; heard "去一下皮也是可以吃的，切成厚片"] | Florets; salt soak; stem peel and slice |
| 胡萝卜 carrot (garnish) | Raw carrot **not shown** in A. [assumed] whole carrot | **Decorative** thin slices (leaf-shaped), cut off camera [result seen `f1/050`, `extra/v1_t101.0.jpg`] | Peel [assumed]; decorative slices |
| 丝瓜 luffa | **Whole, unpeeled, dark green, flower still attached** [seen `extra/v1_t5.0.jpg`, `v1_t9.0.jpg`] | Peeled off camera: pale green at 1:10 [inferred; seen `extra/v1_t70.0.jpg`]. Trims the end [seen `f1/037`]; cuts lengthwise into quarters [seen `f1/038`–`041`]; cross-cuts ~5 cm segments [seen `f1/042`–`043`]; stands them in a row on the plate [seen `f1/044`, `extra/v1_t214.5.jpg`; heard "这条丝瓜真够嫩，切的时候要谨慎"] | Peel; quarter; segment; arrange |
| 蒜 garlic (luffa sauce) | **Heads plus loose unpeeled cloves** [seen `extra/v1_t5.0.jpg`, `v1_t9.0.jpg`] | Fine mince, off camera [result seen `extra/v1_t214.5.jpg`; heard "蒜末"] | Break, peel, fine mince |

### 2.2 Meal B (v2): 红烧肉, 番茄炒蛋, 白灼秋葵娃娃菜, 清蒸海鲈鱼, 鲜笋排骨汤

| Ingredient | As bought | What he does | Left for the robot |
|---|---|---|---|
| 排骨 ribs (soup) | **Chopped bone-in chunks, ~4–5 cm** [seen `f2/010`, `extra/v2_t19.0.jpg`] | Pours boiling water over them in a bowl, soaks 5 min, drains with a spider [seen `f2/010`–`012`; heard "用开水烫一下排骨，再给它浸泡五分钟"] | Scald, soak, drain |
| 鲜笋 bamboo shoot | **Whole, in the husk**, green leaf tips, dirty base [seen `f2/003`, `extra/v2_t5.0.jpg`] | Slits the husk lengthwise with a knife tip [seen `extra/v2_t7.0.jpg`]; peels the sheath off by hand [seen `extra/v2_t9.0.jpg`]; trims the tough parts with the cleaver [seen `extra/v2_t11.0.jpg`]; halves and cuts thick slices [seen `extra/v2_t15.0.jpg`, `v2_t17.5.jpg`; heard "对半开切成厚片"]; washes ["洗净的鲜笋放进来", caption 0:28]. One shoot is shown. | Slit, husk, trim, halve, thick slices, wash |
| 干贝 dried scallops | Dry pantry good [assumed]. They look plump at 0:30, i.e. already soaked [seen `extra/v2_t30.5.jpg`] | Soaking is not shown | Soak [assumed] |
| 姜 ginger | Raw **not shown** in B. [assumed] whole knob, as in A and C | Peeled slices into the soup and the braise, under the fish, and in the 三丝 [results seen `extra/v2_t27.0.jpg`, `f2/038`, `extra/v2_m_f.jpg`]. Peeling and slicing [inferred] | Peel; slices |
| 芹菜 celery (soup) | Raw **not shown** in B | **Fine strips**, ~4 cm, scattered on at the end [seen `extra/v2_t263.5.jpg`; caption "撒点芹菜段更香"] | Strips (not 末 as the audit had) |
| 五花肉 pork belly | **One long skin-on strip, ~35–40 cm** [seen `f2/001`–`002`, `extra/v2_t37.0.jpg`] | Blanches it **whole** from cold water with scallion, ginger and wine [seen `f2/020`–`025`; heard "五花肉冷水下锅，加去腥三件套"]. On the board he **levels the top** with a horizontal cleaver cut [seen `extra/v2_m_d.jpg`; heard "会把上面先打平"]. The skin is underneath, so this is not skin scraping (my reading of the frames). Then strips → cubes of ~3–4 cm [seen `f2/028`–`031`] | Blanch whole; level; cut cooked belly into strips and cubes |
| 葱 scallion | **Whole bunch** [seen `extra/v2_t3.0.jpg`] | Long segments for the blanch, the braise and the fish; 葱段 and 葱叶 for the egg dish; 葱白 finely chopped for the sauce; green segments for the 三丝 [results seen `f2/021`, `extra/v2_aromatics_70-76.jpg`, `extra/v2_m_f.jpg`, `f2/107`, `f2/114`, `extra/v2_t144.5.jpg`]. Cutting [inferred], except the 三丝 shred [seen] | Trim; 4–5 cut forms |
| 海鲈鱼 sea bass | **Whole with head, gutted**: belly flap open [seen `extra/v2_fish_crop_t107.0.jpg`]. **Scaled: uncertain.** Fine scale rows are visible on the flank at 720p. Gills not visible | **Splits it along the back** with the cleaver flat along the spine [seen `f2/054`–`056`; heard "给它开个背"]. Presses the head so it stands [seen `f2/057`; heard "头给他压一下，站得稳"]. Tucks in ginger slices and scallion segments [seen `extra/v2_fish_crop_t114.5.jpg`]. After steaming, pours off the liquid [seen `f2/069`] | Back-split, stand on the plate, tuck aromatics; scale if the stall did not [assumed done at the stall] |
| 蒸鱼三丝 (scallion, ginger, carrot) | Carrot raw **not shown** in B | Stacks thin carrot and ginger slices and scallion-green segments (cut beforehand), presses and shreds them [seen `f2/061`–`066`; heard "把小葱，生姜，胡萝卜叠在一起，再把它压实"]. Soaks in water [seen `f2/067`; heard "泡个水，更新鲜"] | Thin slices, stack, fine shred, soak |
| 番茄 tomatoes | **Whole, ×4** [seen `extra/v2_t183.5.jpg`] | Pours boiling water over them in a bowl [seen `f2/091`–`092`; heard "用开水烫番茄表面是为了更好的去皮"]. Cross-cuts [seen `f2/093`; heard "划个十字刀"]. Peels by hand [seen `extra/v2_t186.0.jpg`]. Cuts chunks/wedges [seen `f2/095`–`101`] | Scald, cross-cut, peel, chunks |
| 鸡蛋 eggs | 5 [heard "准备五个鸡蛋"]. Shell eggs [assumed] | **Cracking not shown**: a jump cut from tomato to a bowl of eggs [seen `extra/v2_eggs_198-204.jpg`]. Beats with chopsticks [seen `f2/102`–`103`; heard "搅拌均匀"] | Crack 5; beat |
| 娃娃菜 baby cabbage | **Whole heads** [seen `extra/v2_t3.0.jpg` bottom left; `f2/088`] | Halves, then cuts lengthwise wedges [seen `extra/v2_t174.5.jpg`, `v2_t177.5.jpg`]. Washing not shown | Halve; wedges; wash [assumed] |
| 秋葵 okra | **Whole, with caps** [seen `f2/049`] | Washes in rice-rinse water [seen `f2/050`; heard "老一辈的人说啊，(淘米)水不能浪费，拿来洗菜很不错的"]. **Trims the caps and halves each pod lengthwise** [seen `f2/084`–`087`, `extra/v2_m_g.jpg`] | Wash; trim; halve (the audit had "whole") |
| 白灼汁: 蒜, 葱白, 干辣椒 | Garlic raw not shown in B | Fine garlic mince, finely chopped 葱白, dried chilies snipped into segments [results seen `extra/v2_t144.5.jpg`; heard "准备蒜末葱白，干辣椒"]. Cutting [inferred] | Peel garlic; mince; chop 葱白; snip chilies |
| 米 rice | — | The user's job (2026-10-13) | — |

### 2.3 Meal C (v3): 芋头蒸排骨, 酸辣土豆丝, 青椒炒鱿鱼, 清炒荷兰豆, 青瓜肉片汤

Ingredient list [heard 0:11–0:13; caption 0:14]: "黄瓜，青椒，芋头和土豆，瘦肉，鱿鱼，排骨，荷兰豆". Whisper heard 鱿鱼 as 油皮.

| Ingredient | As bought | What he does | Left for the robot |
|---|---|---|---|
| 排骨 ribs (steamed) | **Chopped small bone-in pieces, ~2.5–3 cm** [seen `extra/v3_t15.0.jpg`] | Marinates them: 生抽, 老抽, 蚝油, pepper, 2 spoons potato starch, 1 spoon oil; mixed with a gloved hand [seen `f3/010`–`015`, `extra/v3_m_b.jpg`; heard "生抽调味…抓拌均匀，腌制入味"]. Lays them on the taro [seen `f3/022`–`023`] | Marinate (pour, mix); arrange |
| 芋头 taro | **Whole large corm, unpeeled** [seen `extra/v3_t13.0.jpg`, `v3_t15.0.jpg`] | Peeled **off camera**: half a peeled corm at 0:29 [inferred; seen `extra/v3_t29.0.jpg`, `v3_t30.5.jpg`]. Pours white vinegar on it [seen `f3/016`–`017`; heard "有些人切芋头会痒，你可以在它表面淋点白醋"]. Thick slices → strips → blocks [seen `f3/018`–`020`; heard "先切成厚片，再切成长条，切成这种块状"]. A bed of blocks on the plate [seen `f3/021`] | Peel; vinegar; block; bed |
| 红椒末, 葱花 (garnish) | Red chili **whole** [seen `extra/v3_t15.0.jpg`]. Scallion raw not shown in C | Minced red chili and scallion rings [result seen `extra/v3_t236.5.jpg`; caption "撒点红椒末"]. Cutting [inferred] | Mince chili; 葱花 |
| 鱿鱼 squid | **Two cleaned tubes**: no head or tentacles, skin off, pale [seen `extra/v3_t15.0.jpg`] | Slits each tube open with a slicing knife [seen `extra/v3_m_squid.jpg`, 0:52–0:55]. Scores diagonally, not through [seen `f3/029`–`032`; heard "斜刀啊…不要切断"]. Turns and scores the other way [seen `f3/034`–`036`; heard "切完这边换个手势，也是不要切断"]. Cuts pieces, off camera [result seen `f3/037`]. Pours boiling water over them in a bowl, and they curl [seen `f3/038`–`041`; heard "用滚烫的开水烫一下"] | Open the tube; cross-score both ways; cut pieces; scald |
| 青椒 green bell pepper | **Whole ×2** [seen `extra/v3_t15.0.jpg`] | Pieces ~3 cm [seen `f3/042`–`044`, `extra/v3_t81.5.jpg`]. De-seeding not shown | Core and deseed [assumed]; pieces |
| 葱姜蒜 (squid, peas, 土豆丝) | Ginger **whole knob**, garlic **head plus cloves** [seen `extra/v3_t15.0.jpg`]. Scallion not on the spread | Ginger rounds, garlic slices, scallion-white segments for the squid [seen `extra/v3_t194.5.jpg`]. Coarse-chopped garlic for the peas [seen `extra/v3_t126.5.jpg`, `v3_t218.5.jpg`]. Garlic pieces for the 土豆丝 [seen `extra/v3_t142.5.jpg`]. Scallion-leaf segments [seen `f3/079`]. All cut off camera [inferred] | Peel ginger and garlic; slices and coarse chop; scallion segments |
| 土豆 potato (丝) | **Unpeeled, skin on** [seen `extra/v3_t13.0.jpg`, `v3_t15.0.jpg`] | Peeled off camera [inferred; peeled on the board in `extra/v3_t88.5.jpg`]. Thin slices → **hand julienne ~2 mm** [seen `f3/045`–`054`]. Soaks to wash off starch [seen `f3/055`; heard "第一步，泡水洗掉土豆淀粉"]. Blanches [seen `f3/065`–`069`] | Peel; julienne; soak; blanch |
| 红椒丝, 干辣椒 | Red chili **whole** [seen] | Fine shreds; dried chilies snipped into segments [result seen `extra/v3_t142.5.jpg`; caption "蒜末红椒干辣椒下"]. Cutting [inferred] | Fine shreds; snip |
| 瘦肉 lean pork | **A lean block, ~15×10×3 cm** [seen `extra/v3_t15.0.jpg`] | Slices across the grain [seen `f3/056`–`060`, `extra/v3_t112.5.jpg`; heard "竖切肉丝，横切肉片"]. Salt and plenty of potato starch, mixed by hand [seen `f3/061`–`062`; heard "肉片里面加点盐，多一点的土豆淀粉，抓拌均匀，腌制上浆"] | Slice thin; 上浆 |
| 青瓜 cucumber | **Whole, unpeeled** (spiny 黄瓜) [seen `extra/v3_t15.0.jpg`] | Not peeled. Lengthwise quarters, then thin oblique slices [seen `f3/001`–`006`, `extra/v3_m_a.jpg`; heard "挑战15秒，切一条黄瓜"] | Quarter; oblique slices |
| 姜, 芹菜 (soup) | Celery: **a few thin whole stalks** [seen `extra/v3_t15.0.jpg`, top-right plate] | Ginger slices into the boiling water [seen `f3/084`]. Celery as **fine strips of ~3–4 cm** in the serving bowl [seen `extra/v3_t184.5.jpg`; caption "碗中下芹菜"] | Celery strips (not 末) |
| 荷兰豆 snow peas + 胡萝卜 | Snow peas **whole** [seen `extra/v3_t15.0.jpg`]. Carrot: **a short smooth cut piece** [seen ibid.]; whether it was peeled is unclear | Peas go into the wok whole [seen `f3/111`, `extra/v3_t126.5.jpg`]. Ends and strings: **not visible** either way. Carrot cut into decorative slices off camera [result seen `extra/v3_t126.5.jpg`] | String and trim [assumed]; decorative carrot slices |

**His own mise en place for meal C** (`extra/v3_t126.5.jpg`, 2:06; heard "做菜其实并不难，就是前面的切配比较费时间"): every cut item is on plates and in bowls before the wok work starts. This is the target state the robot's prep must reach.

---

## 3. Recount against the audit's 38 items

### 3.1 Item by item

Codes:
- **=** unchanged;
- **S** a stall step is now confirmed (it was outside the 38 already, but needed the user's OK);
- **C** an escape route is closed (the audit's purchase form or recipe change is no longer available);
- **+** an operation is added or corrected;
- **−** an operation the audit had does not occur.

| # | Audit item | Status | Note |
|---|---|---|---|
| A1 | 排骨 cups | S | Chopped at the stall [seen]. Rib washing not shown |
| A2 | 蛤蜊 | = | Live in shell; purge and scrub still [assumed] |
| A3 | 姜 | + | Peeling added (whole knob as bought) |
| A4 | 芋头 | = | Raw whole confirmed; cleaver peel [seen] |
| A5 | 土豆 | = | Unpeeled as bought [inferred from C] |
| A6 | 五花肉 slices | = | Skin-on block [seen] |
| A7 | 红椒 | = | — |
| A8 | 蒜苗 | = | — |
| A9 | 西兰花 | C | Whole head; no 净菜 florets |
| A10 | 胡萝卜 | + | Decorative slices, not plain |
| A11 | 丝瓜 | C | Whole unpeeled; no swap to 西葫芦 |
| A12 | 蒜 + 红辣椒 | C, + | Heads, so peeling is the robot's; the chili is **shredded**, not minced |
| B1 | 排骨 soup | S | Chopped at the stall [seen] |
| B2 | 鲜笋 | C | In the husk; no shelled shoots. 1 shoot seen (the audit had 2) |
| B3 | 干贝 | = | Soaking [assumed] |
| B4 | 姜 | + | Peeling added |
| B5 | 芹菜 | + | Strips, not 末 |
| B6 | 五花肉 cubes | −, + | No skin scraping; top levelling instead; whole-strip blanch [seen] |
| B7 | 葱 | = | Whole bunch |
| B8 | 鲈鱼 | S, C, + | Gutting at the stall [seen]; scaling uncertain; **back-split is his** (the audit had it as "stall") |
| B9 | 三丝 | = | — |
| B10 | 番茄 | C | Peeling is his; R16's "drop peeling" is not available under this rule. 4 tomatoes, not 3 |
| B11 | 鸡蛋 | = | Cracking off camera; beating seen |
| B12 | 娃娃菜 | = | Shape confirmed: halves → wedges |
| B13 | 秋葵 | + | **Trim caps and halve lengthwise** (the audit had "whole"); rice-water wash |
| B14 | 蒜, 葱白, 干辣椒 | + | Dried-chili snipping added |
| C1 | 排骨 | S | Chopped at the stall [seen] |
| C2 | 芋头 | = (+) | Plus a vinegar pour (trivial) |
| C3 | 红椒, 葱花 | = | — |
| C4 | 鱿鱼 | S, C | Cleaning at the stall [seen]; **scoring and cutting are his**; no "accept strips" |
| C5 | 青椒 | = | De-seeding [assumed] |
| C6 | 葱姜蒜 | C, + | Ginger peel added; garlic is sliced or coarse-chopped, not minced; peeling is the robot's |
| C7 | 土豆丝 | = | Unpeeled as bought [seen] |
| C8 | 红椒丝, 干辣椒 | + | Dried-chili snipping |
| C9 | 瘦肉 | = | Block [seen] |
| C10 | 青瓜 | = | Not peeled; quarters → oblique slices |
| C11 | 姜, 芹菜 | + | Celery strips, not 末 |
| C12 | 荷兰豆 | = | Strings and ends [assumed] |

### 3.2 What disappears
- **Whole items: none of the 38.** Every ingredient still needs work between the market state and the pan.
- **Steps done at the stall** (confirmed; the audit had already excluded them, so the count of 38 does not move):
  - bone-in rib chopping (A1, B1, C1) [seen];
  - fish gutting (B8) [seen], and probably scaling [uncertain];
  - squid cleaning: head, innards, skin (C4) [seen].
- **A step the audit had that he does not do:** pork-belly skin scraping (B6). It is replaced by a levelling cut on the blanched slab.
- **Not shown in any video,** so it may also go, but this is unconfirmed: washing the ribs.

### 3.3 What remains, and what grows

Everything else in the audit's §2.4 operation table remains. Corrected counts (A / B / C), with the changes only:

| Operation (audit §2.4) | Audit | Now | Why |
|---|---|---|---|
| Peel: other | 3 / 3 / 1 | **4 / 4 / 2** | + ginger knob peel in all three meals (A: luffa, broccoli stem, garlic, ginger; B: bamboo, garlic, tomato scald-peel, ginger, with the skin scrape removed; C: garlic, ginger) |
| Shred 丝 | 0 / 3 / 2 | **1 / 3 / 3** | A: red-chili shreds for the luffa sauce; C: celery strips |
| Mince 末 | 1 / 2 / 3 | **1 / 2 / 2** | C: garlic is sliced or coarse-chopped (counted under slices); chili 末 + 葱花 remain |
| Sections / halves | 2 / 1 / 1 | **2 / 2 / 1** | B: okra cap trim + lengthwise halving |
| Fish back-split | (stall) | **0 / 1 / 0** | On camera, heard "给它开个背" |
| Squid opening + scoring + cut | 1 (with fallback) | **0 / 0 / 1, no fallback** | Fallback closed |
| Dried-chili snipping | — | **0 / 1 / 1** | Seen in the bowls (small task) |
| Decorative carrot slices | (plain slices) | **1 / 0 / 1** | Shape is decorative |
| Bone-in chopping, fish cleaning, squid cleaning | (bought, user's OK needed) | **bought, confirmed** | Seen in all three videos |

**Net:** about +8 operation instances and −1 (skin scraping). The prep demand does not fall. It rises slightly, and the escape routes in audit §5.7 are no longer available without a separate decision by the user. The arm-time figures in audit §6.3 (A 27–40, B 22–32, C 21–30 min) should be read as lower bounds. I did not re-run `r19prep_demand.py`.

### 3.4 Other corrections to the audit's §2 tables
- **秋葵 (B):** trimmed and halved, not whole.
- **番茄 (B):** 4 tomatoes, not 3.
- **鲜笋 (B):** one shoot is shown.
- **芹菜 (B, C):** strips or 段, not 粒/末.
- **红辣椒 (A, luffa sauce):** fine shreds, not 碎.
- **五花肉 (B):** blanched whole and levelled on top, not "skin scraped flat".
- **鲈鱼 (B):** the head is pressed so the split fish stands upright.
- **青瓜 (C):** lengthwise quarters, then thin oblique slices; not peeled.
- **葱姜蒜 (C):** garlic is sliced (squid) or coarse-chopped (peas, 土豆丝), not 末.

---

## 4. Remaining hard operations

"Hard" means no appliance in the current design covers it (audit §3: [missing] or [designed] only), or it needs knife craft on an irregular item.

| # | Operation | Meals | Evidence | Why it is hard |
|---|---|---|---|---|
| 1 | **Peel a large taro corm** (hairy, irregular, slimy and itchy once cut) | A, C | Seen start `extra/v1_taro_22-32.jpg`; C off camera | No peeler for a corm this size. Abrasive peeling of taro is untested (audit §6.4). Itch: he uses vinegar |
| 2 | **Peel luffa** (thin ridged skin, soft flesh) | A | Inferred: `extra/v1_t5.0.jpg` → `v1_t70.0.jpg` | Audit: "none credible yet"; the swap is now closed |
| 3 | **Husk a bamboo shoot** (slit, peel the sheath, trim the base) | B | Seen `extra/v2_m_b.jpg` | No tool; sheath layers need pulling by hand |
| 4 | **Peel garlic cloves** (break the head) and **peel a ginger knob** | A, B, C | Heads and knobs seen on the spreads | Garlic: domestic peelers unproven (audit §5.2). Ginger: irregular knob, not in any chain |
| 5 | **Broccoli florets + stem peel** | A | Seen `f1/045`–`054` | No appliance cuts florets (audit §5.5) |
| 6 | **Slice raw skin-on pork belly thin** (~3 mm) | A | Seen `f1/026`–`027` | Needs the meat slicer (audit §5.1); skin-on is untested |
| 7 | **Cube blanched pork belly** (~3–4 cm, after levelling) | B | Seen `extra/v2_m_d.jpg` | Beyond the slicer sets; cutting force not sourced (audit §5.1) |
| 8 | **Slice lean pork across the grain** + 上浆 by hand | C | Seen `f3/056`–`062` | Meat slicer [missing]; hand mixing [missing] |
| 9 | **Back-split a whole sea bass**, stand it on the plate | B | Seen `f2/054`–`057` | Knife along the spine on a slippery fish; no tool |
| 10 | **Open a squid tube, score 麦穗 both ways without cutting through, cut pieces** | C | Seen `extra/v3_squid_50-74.jpg` | Depth-controlled scoring; no tool |
| 11 | **Scald, cross-cut and peel tomatoes** | B | Seen `f2/091`–`094` | Peeling by hand; kettle pour unchecked (R16) |
| 12 | **Crack 5 eggs**, beat | B | Beating seen; cracking off camera | Egg cracker [missing] (audit §5.3) |
| 13 | **Fine 丝:** stacked 三丝 (scallion, ginger, carrot); potato hand julienne ~2 mm; red-chili shreds; celery strips | A, B, C | Seen `f2/061`–`066`, `f3/045`–`054`; results `extra/v1_t214.5.jpg`, `v3_t142.5.jpg`, `v3_t184.5.jpg` | 4 mm shred disc is coarser than his 2 mm; scallion 丝 has only a concept (audit §5.7) |
| 14 | **Trim okra caps and halve lengthwise** | B | Seen `extra/v2_m_g.jpg` | Small, many pieces (~15–20) |
| 15 | **Mince garlic finely; snip dried chilies; mince red chili; 葱花** | A, B, C | Results seen | Mincer [missing] (audit §5.2) |
| 16 | **Arrange:** 16 ribs + 12 clams + 4 ginger slabs into 4 cups; taro blocks spaced; luffa segments upright; taro bed + ribs; fish on its plate | A, B, C | Seen `f1/007`–`012`, `f1/021`, `f1/044`, `f3/021`–`023`, `f2/057`–`059` | PLACE/ARRANGE [missing] (audit §6.2) |

Medium operations, covered at least by design (audit §3): firm-veg slicing (potato, cucumber, bamboo slices), pepper pieces, baby-cabbage wedges, garlic-sprout and scallion sections, washing and soaking (broccoli salt soak, okra in rice water, potato starch soak, 三丝 soak, 5-min rib soak), scalding (ribs, squid), and marinating (ribs).

---

## 5. Open points for the user
1. **Off-camera steps.** His as-bought state is raw, but these are done off camera:
   - potato peeling (A, C);
   - luffa peeling;
   - taro peeling (C);
   - ginger and garlic peeling and cutting;
   - chili and scallion cuts;
   - decorative carrot slices;
   - egg cracking.

   I counted them as robot work under the rule. The user may want to confirm.
2. **Fish and squid.** The stall cleans them [seen], but he cuts them himself (back-split, 麦穗 scoring). Is asking the stall to 开背 or 切花 acceptable as "how he buys it"? The videos say no.
3. **Not shown anywhere**, so a household default is assumed:
   - washing most produce and the ribs;
   - purging the clams;
   - soaking the dried scallops;
   - de-seeding the peppers;
   - stringing the snow peas;
   - whether the fish was scaled.

---

## 6. Honesty notes
- **Frame sampling.** Every as-bought state was checked on full-resolution extracts (720×1280 source, `home3/extra/`). The 2 s frames were used for the step sequences.
  - Jump cuts hide parts of several steps: taro peeling (A, C), luffa peeling, egg cracking, and all aromatic cutting.
  - These are marked [inferred] where the before and after states are both seen.
- **Uncertain readings:**
  - Fish scaling: fine scale rows are visible at 720p, which suggests scales could still be on; not decidable.
  - The B pork-belly cut: levelling the lean top, not scraping the skin; my reading of `extra/v2_m_d.jpg`.
  - Whether the C carrot piece was peeled.
  - Snow-pea ends.
- **Whisper corrections, from the captions:** 文革 → 文蛤; 油皮 → 鱿鱼; 旁边水 → (淘米)水 (the rice water is seen poured on the okra); 芹菜蒜 → 芹菜段 (caption).
- **Not re-done:** masses, piece counts and arm-time estimates. The audit's numbers stand, with the corrections in §3.
- **Files.** Only this file was created in the project. Extracted frames are in the session scratchpad `home3/extra/`. No existing file was changed.
