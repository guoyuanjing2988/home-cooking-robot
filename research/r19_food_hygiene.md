# R19 food hygiene: parts, cross-contamination, 30 °C exposure, doneness, cleaning (2026-10-14)

**Issue:** #23 "[safety] Food hygiene: cleaning procedure, cross-contamination, 30 °C exposure timeline, materials". Cross-refs: #31 (dishwasher), #15 (heat at the wok), #28 (user workload), #4 (prep), #5 (seasoning cups).

**Tags**
- **[S]**: sourced. Either a repo file and line (`file:line`) or a URL read on 2026-10-14. "[S, snip]" means only a search-result summary was read, not the page.
- **[M]**: computed by me from repo model outputs: `sim/r10/claude/results/r16/meal_stew_r18_userrice.json` (the meal16 timeline, rice by the user) and `sim/r10/claude/results/r19/prep/prep_demand.json` (prep arm time, prep-first block, per-item deadlines). It is arithmetic on modelled numbers, not a measurement.
- **[E]**: my estimate, with its basis stated.
- **ND**: searched, not found. Nothing is invented.

Nothing was bought and nobody was contacted. Web use was read-only. Only this file was created.

---

## 0. Answer first

1. **Exposure at 30 °C is within 1 h for most items, but the plan has no margin and two items break it.** With today's model (one cold-box fetch per meal, at the start of the prep-first block):
   - meal B sea bass: **52–56 min** out before it goes into the steamer [M];
   - meal B eggs: **68–72 min** [M];
   - meal A pork belly: 34–44 min; meal C lean pork: 33–41 min [M].

   None of these figures counts the market-to-home trip. FSANZ counts all time in 5–60 °C cumulatively [S: `research/r14_storage_market.md:357`]. **Fix:** fetch just in time, one cold-box trip per protein group, and hold every raw protein in a lidded, chilled box until it goes into its container. That cuts every raw item to about ≤ 10 min out [E]. The repo already costs 2–3 trips at about 45 s each [S: `research/r19_system_cost.md:148`].
2. **The cold box is too small for meal B.** It is 0.30 × 0.08 × 0.10 m, which is 2.4 L [S: `DECISIONS.md:270`; volume M]. The sea bass alone is 336–367 mm long [S: `research/r19_prep_methods.md:63`]. Meal B also has 600 g of pork belly and 500 g of ribs [S: `R19_PREP_AUDIT.md:118,123`]. The door bin is also the warmest place in the fridge. A Korean household survey measured door compartments at **5.06 ± 1.69 °C**, which is at or above SFA's 5 °C danger-zone edge [S, snip: koreascience JAKO202332472161643]. Measure the user's own door bin.
3. **Cross-contamination.** Three rules do most of the work:
   - **(a) Raw protein travels in containers.** Fingers don't touch it: it is poured from a lidded tray or bowl into the chute, pot, plate or wok. Where a grasp can't be avoided, use a dedicated **red finger set**.
   - **(b) Order:** produce first, raw protein last, on every shared tool (lever base, chopper, soak tub, sink).
   - **(c) No raw-meat rinsing at the sink.** SFA tells food businesses to "Avoid washing raw meat to prevent the spread of pathogens" [S: SFA advisory Dec 2024, p.3]. Use the scald (blanch) step instead.

   The spatula pad becomes a removable stainless or silicone tray that goes in the dishwasher.
4. **Doneness.** SFA tells food businesses to check meat with a probe thermometer for "an internal temperature of at least 75°C for 2 minutes" [S: SFA advisory Dec 2024, p.3]. USDA minimums are lower: pork 63 °C with a 3 min rest, ground meat 71 °C, poultry 74 °C, fish 63 °C, egg dishes 71 °C [S, snip: FSIS / foodsafety.gov]. **Proposal:**
   - an arm-held probe on the standard keyed 30 mm block checks every thick protein: steamed ribs, the fish, rib cups, braised belly;
   - thin stir-fried slices get a time-at-heat rule, validated once with the probe on the bench.

   The camera stays the cue for texture, not for safety.
5. **Materials.** Food-contact printed PETG fails on two counts:
   - **Heat:** the NSF/ANSI 184 dishwasher sanitize cycle's final rinse is 150 °F = 65.6 °C [S, snip: nsf.org]. PETG HDT is 69 °C (Bambu PETG Basic, retailer table) and Tg is 68–80 °C [S, snip: matterhackers; S: `research/finger_design_inputs.md:96`].
   - **Hygiene:** FDM grooves trap residue [S: `research/finger_design_inputs.md:101`; `research/r14_storage_market.md:222`].

   **Rule:** food contact uses stainless, moulded or machined PP/HDPE, or platinum silicone with a GB 4806 / EU 10/2011 / FDA declaration. PETG only for parts that never touch food.
6. **Cleaning.** Nearly everything goes into the dishwasher. Until #31 automates loading, the user needs about **17–28 min per meal** [E, §6]. About half of that is items that cannot go into the dishwasher: the wok, the meat slicer, the 卓晋 slicer, the abrasive peeler and the fish sled. Add about 15–25 min per week [E]. These minutes feed #28.

---

## 1. Inputs used

| Topic | Repo evidence |
|---|---|
| 1 h staging rule | `DECISIONS.md:252`; rule and sources `research/r14_storage_market.md:351-361` |
| Cold box | `DECISIONS.md:270` (size, door bin 0.85 m), `:281` ("warmest zone … same-day staging only"); set-down at the lever work spot, "never out together with the lever base" `sim/r10/claude/R19_PREP_LAYOUT.md:46`; 2–3 trips × (25 + 20 s) `research/r19_system_cost.md:148`; ice-packed counter cooler option O8, hold time "not sourced" `research/r19_system_cost.md:225` |
| Prep time | +21–40 arm-min; meals with prep A 45–56, B 82–86, C 41–48 min `sim/r10/claude/R19_PREP_AUDIT.md:64-66` |
| Shared fingers | pork/chicken pinch and fork on the same P1–P4 sets as produce `R19_PREP_AUDIT.md:214`; R13 methods `DECISIONS.md:196-198` |
| Sink | produce washing and wok rinse share the user's sink `DECISIONS.md:392` |
| Spatula | rests flat on a small pad left of the sink `DECISIONS.md:439` |
| Fingers | PETG body, TPU 92A or Smooth-Sil 940 skin, 2 stainless springs `DECISIONS.md:163-166`; swappable sets with dovetail and spring pin, finger-root force sensor `DECISIONS.md:190-193` |
| Materials | Kimya PETG-S Tg 80 °C, EU 10/2011 + FDA (natural only) `finger_design_inputs.md:96`; Kimya TPU-92A EU/FDA (not black) `:95`; Smooth-Sil 940 on the 21 CFR 177.2600 list `:97`; FDM caveat `:101`; "3D prints: only for non-wetted parts, or brief dry contact" `r14_storage_market.md:227`; GB 4806.7/.9/.11/.16 `r14_storage_market.md:212-215`; "接触食物的件用 FDM PP" `market_r10.md:897` |
| Dishwasher | user has one; cups, caddies and tools "dishwasher-safe", caddies double as baskets `DECISIONS.md:540`; cup material 304, "Printed PETG is not dishwasher-safe (est.)" `research/r19_seasoning_cups.md:346` |
| Seasoning line | 蚝油 refrigerate, ≤ 8 weeks `r19_seasoning_sizing.md:184`; slurry ≤ 2 days `:185`; pet-feeder donor "Not food-certified" `:172`; silicone tube with a GB 4806.16 declaration `:222`; silicone tube life 200 h `r14_storage_market.md:105` |
| Doneness | "157 cue mentions … need a camera; 40 need a thermometer" `sim/r10/claude/README_R10.md:497` |
| As bought | ribs chopped, fish gutted, squid cleaned tubes, clams live `research/r19_asbought.md:27-29,65-66,90` |

---

## 2. Inventory of robot food-contact parts

**Contact type:** **R** = raw meat, seafood or raw egg; **P** = produce (raw vegetables); **C** = cooked or ready-to-eat; **S** = seasoning only.

**Cleaning:**
- **DW** = dishwasher (user loads today; robot later, #31);
- **H** = hand wash by the user;
- **RIP** = robot rinse in place under the running tap;
- **W** = wipe.

**Survives?** means the material survives a normal dishwasher cycle, against NSF/ANSI 184 sanitize at 65.6 °C final rinse [S, snip: nsf.org].

| # | Part | Material today | Contact | Cleaning proposed | Survives? / change |
|---|---|---|---|---|---|
| 1 | **Finger sets P1–P4 (P5–P7 heads)**, dual-zone pads, rocking pad | PETG body; TPU 92A or Smooth-Sil 940 skin; 2 stainless springs in open pockets; FSR in the pad [S: `DECISIONS.md:163-173,190-193`] | **R** + P + egg (one set does everything today) [S: `R19_PREP_AUDIT.md:214`] | RIP between items; DW after the meal **only once the electronics are moved out of the washable part** | **No.** PETG HDT 69 °C / Tg 68–80 °C sits 3–14 °C above the 65.6 °C rinse; the drying phase is hotter (ND per model). FDM pores, spring pockets and the FSR can't be sanitised. **Change:** a moulded platinum-silicone sleeve (Smooth-Sil 940 class [S: `finger_design_inputs.md:97`], or bought silicone with a GB 4806.16 declaration [S: `r14_storage_market.md:215`]) over a machined PP/POM or stainless carrier; springs and FSR sealed under the sleeve; no grooves [E]. Plus a **separate red set** for raw protein (§3) |
| 2 | Dovetail jaw adapter, rack, spring lock pin | printed PA-CF / PETG or aluminium [S: `finger_change_and_food_eoat.md:71`] | none (splash only) | W weekly | OK as non-food |
| 3 | Keyed 30 mm blocks on cups, spatula, lid, carrier, spider, faucet lever | PPSU, POM or stainless [S: `r19_seasoning_cups.md:351`] | none, but touched by fingers that may carry R | DW with their tool | PPSU and stainless OK; POM OK on a normal cycle [E] |
| 4 | **Seasoning cups** S 100 ml / L 300 ml (24) | deep-drawn 304 stainless [S: `r19_seasoning_cups.md:346`] | S, aromatics (P), hot oil; marinade cups are poured onto raw ribs (one-way) | DW | Yes |
| 5 | Cup caddies 2×3 (6) | 304 wire [S: `r19_seasoning_cups.md:357-361`] | S | DW (they are the baskets) | Yes |
| 6 | Pour drum Ø80 × 140, 4 compartments (3) | **unspecified** [S: `r19_seasoning_cups.md:362`] | S, aromatics | DW; needs open ends or a removable cap | **Specify** stainless or moulded PP |
| 7 | Special cups: perforated 三丝 insert, PTFE stir bar under a bail [S: `r19_seasoning_cups.md:353-355`] | stainless / PTFE | P, S | DW | Yes |
| 8 | **R13 side-handle basket** Ø200–220, drain holes, keyed knob | **unspecified** [S: `README_R10.md:295`] | P, plus **R** in today's demand (ribs and clams wash, A and C) [S: `prep_demand.json` items] | DW | Specify 304 perforated. **Two baskets:** green for produce, red for clams and ribs (§3) |
| 9 | **V-rib slot trays** 360 × 240 × 45 | FDM PP, printed in two halves and joined [S: `market_r10.md:915`] | P, **R** (fish and fillet are forked from the slot tray; meat is pinched from the tray) [S: `DECISIONS.md:197`] | DW | PP survives the heat, but FDM PP is porous and a two-half joint is a crevice. **Change:** machine from solid PP/HDPE sheet, or use moulded PP GN trays with a moulded rib insert [E]. Separate red trays, lidded |
| 10 | **Cold box** (冷藏料盒), tub with bridge bar | **unspecified** [S: `DECISIONS.md:270`] | **R** | DW every meal | Specify moulded PP or stainless with a lid; see §4 for size |
| 11 | **Soak tub** GN 1/3 + perforated basket insert | stainless [S: `R19_PREP_AUDIT.md:382`] | P (broccoli soak, potato shreds, 三丝) **and R** (clam purge, rib soak after the scald) [S: `R19_PREP_AUDIT.md:384`] | DW after the meal; RIP between P and R use | Yes. Order P before R, or buy a second insert for R (§3) |
| 12 | **Lever base AY-403** (body, stainless plates, black pushers) | aluminium-alloy body, stainless plates [S: `market_r10.md:804`] | P (tomato, greens, chili, garlic crack) **and R** (squid die, §3.7 of prep_methods) **and C-ish** (blanched belly cubes, 30 mm grid) [S: `R19_PREP_AUDIT.md:330`] | plates and pushers DW; body W after every R use, H weekly | Aluminium in alkaline dishwasher detergent discolours or corrodes [E, general]: **don't** put the body in the dishwasher |
| 13 | Custom lever plates (section, split, trim, X, "+", okra comb, scoring die) | PETG frame + PP pusher + AY450 stainless strips [S: `market_r10.md:918`; `r19_prep_methods.md:215,256`] | P; scoring die **R** (squid) | DW top rack | PETG frame: **no** (move to PP or a machined frame). Strips are bolted, not glued [S: `r19_prep_methods.md:215`]: OK. Squid die is red-only |
| 14 | 铡刀 long-blade lever (squid opening, bamboo, luffa trims) | ND [S: `r19_prep_methods.md:77-78`] | P and **R** (squid) | H or W; blade lock on in storage | Likely too long for the rack (36 cm blade) [S: `r19_prep_methods.md:78`]: H |
| 15 | **卓晋 3-in-1 slicer** (chute, discs, lid) | plastic and steel; "刀盘和塑料推料盘可拆下，用温水冲洗 … 机身不能浸水；说明书没有写可进洗碗机" [S: `market_r10.md:382-385`] | P only | **H by the user** (spring-clip disassembly is not a robot task [E]) | Produce only; never meat |
| 16 | **850 W 切肉切菜一体机** (if adopted) | ND; cleaning ND [S: `R19_PREP_AUDIT.md:312-322`] | **R** (pork belly, lean pork, squid strips) | **H by the user after every meat run** | Make it meat-only. The audit's "also cuts soft vegetables" [S: `R19_PREP_AUDIT.md:317`] should not be used on the same day as meat without a full clean |
| 17 | 2 L chopper bowl + S-blade (garlic, ginger, chili, celery, 肉末, egg beating) [S: `R19_PREP_AUDIT.md:333-342`] | glass bowl; blade ND | P, then **R** (egg, 肉末) | DW (bowl, blade); motor head W | Order: aromatics first, egg last |
| 18 | Egg cracker on a printed stand [S: `R19_PREP_AUDIT.md:349-352`] | ND + printed stand | **R** (raw egg, shell) | DW (stand only if PP) | Stand in PP or stainless |
| 19 | Abrasive peeler (傲宏 85 W class) | plastic drum; Gastronoma class "不能进洗碗机" [S: `market_r10.md:221,243`] | P (potato, taro, ginger, broccoli stem) | RIP drum rinse + H weekly | Produce only |
| 20 | Garlic tumbling peeler; rotary peeler (Rotato class); 葱丝刀 sleeve; spinner | silicone bowl / steel prongs [C in source] | P | DW bowl, sleeve; W blade arm [S: `r19_prep_methods.md:87,125,291`] | Produce only |
| 21 | Printed jigs: broccoli coring tube + cradle, bamboo cradle + push-out fork, okra press, crack plate, chute adapters, carrot guide, tomato/potato seats, pusher rods [S: `market_r10.md:907-919`; `r19_prep_methods.md` §3] | FDM PP (some PETG) | P | DW | PP OK; replace on wear (SFA: "Equipment and utensils with permanent stains or damages should be replaced immediately" [S: SFA advisory Dec 2024, p.2]) |
| 22 | **Fish sled + rail** ~400 × 120 × 110 mm, rail ~750 mm, fixed blade [S: `r19_prep_methods.md:192`] | FDM PP + stainless blade | **R** (fish) | sled DW if it fits; rail and blade H | Red-only. The rail is probably too long for a rack [E] |
| 23 | Lever catch tray, output bowls, T2L pan on the swing cradle [S: `R19_PREP_T2L.md:37`; `DECISIONS.md:599-605`] | ND | P (and R if the squid output uses them) | DW | Specify stainless; a separate red output bowl |
| 24 | **Wok** 34 cm carbon steel [S: `DECISIONS.md:300`] | carbon steel (seasoned) | R → C | RIP at the sink between dishes (existing set) [S: `DECISIONS.md:392`]; **H** after the meal | Never DW (rust, seasoning) [E] |
| 25 | **Spatula** 0.45 m, keyed block [S: `DECISIONS.md:305`; `r15_cooking_market.md:368` stainless class] | stainless | R (stirs raw slices as they go in) → C | rinse with the wok trip; DW after the meal (check rack length, #31) | Yes |
| 26 | **Spatula pad** on the counter left of the sink [S: `DECISIONS.md:439`] | ND ("a small pad") | gets everything from the blade | DW after every meal | **Change:** a removable stainless or silicone tray with a rim, so drips stay in it [E] |
| 27 | Spider, lid, dish carrier, steaming plates, plate holder with 8 cm guard [S: `DECISIONS.md:326,350-352,365`] | stainless / ceramic [E] | the spider drains scalded ribs (R/C) and blanched vegetables; the rest C | DW | Rinse the spider between ribs and vegetables (§3) |
| 28 | Stew-pot cups (蛤蜊排骨盅), steamer plates | the user's crockery | R in, C out (heat-sanitised in use) | DW | Yes |
| 29 | Kettle, water jug | — | water | descale weekly | — |
| 30 | **Sink basin, faucet clip-on block, fridge handle** [S: `DECISIONS.md:410`] | stainless; block ND | splash from produce washing and R drains; touched by the gripper | after the meal: robot hot rinse (kettle water) of the basin [E]; user wipes the block and handle | Block in PP/POM, DW-able |
| 31 | **Seasoning station** wetted parts: bottles, silicone tubes (GB 4806.16), pinch valves, slurry cell, sugar/chili/花椒 portioners, spice tray, squeeze bottles, Peltier box [S: `r19_seasoning_sizing.md:205,222-227`] | silicone, PP, stainless; the pet-feeder donor is "Not food-certified" [S: `:172`] | S | daily flush and suck-back; weekly CIP; tube change at 200 h [S: `r14_storage_market.md:105`] or 6 months [E] | Replace the donor's food path with food-grade PP or stainless |
| 32 | **Probe thermometer** (new, §5) | stainless sheath | C (end of cook) | dip in kettle water ≥ 90 °C between pieces [E]; DW or W after the meal | Yes |
| 33 | Gripper body, jaws, arm wrist | IP67 (manual says IP54) [S: `finger_design_inputs.md:28`] | indirect | W with food-safe sanitiser daily; degrease weekly | Covers: #15 |

**Count:** about 33 part families, about 70–90 pieces with spares [E]. That is more than the issue's "about 20".

---

## 3. Cross-contamination plan

**Streams [E, after SFA's colour-coding advice [S: SFA advisory Dec 2024, p.3]]:**
- **RED** = raw meat, seafood and raw egg;
- **GREEN** = raw produce;
- **BLUE** = cooked and ready-to-eat.

Tools carry a colour on their keyed block, and the camera can check it [E].

### 3.1 Rules

1. **Containers, not fingers, for RED.** Commercial food robots "rarely squeeze food with bare jaws. They carry utensils and containers" [S: `finger_change_and_food_eoat.md:144`]. Each raw protein is loaded by the user into its own lidded red tray or bowl inside the cold box. The arm moves the container by its keyed handle and **pours** the protein into:
   - the wok (pork slices, squid);
   - the stew pot (lean-pork 上浆 slices);
   - a steaming plate (ribs on the taro bed);
   - the meat-slicer chute;
   - the fish sled, which is itself the container.
2. **Where a grasp is unavoidable** (rib and clam portioning into 4 cups; the pork-belly block into the meat-slicer chute; scalded ribs into the soup pot), use a **red finger set**: one extra P2/P3-class set [S: R13 ranges `R19_PREP_AUDIT.md:201`].
   - Swaps cost 10–15 s each [S: `prep_demand.json` units FINGER].
   - About 2–4 extra swaps per meal, i.e. 0.3–1 min of arm time [M].
   - The red set is rinsed at the tap after use (RIP) and goes to the DW after the meal.
   - Better still, replace the 28 single placements in meal A by **pour-portioning by weight** (4 partial pours per ingredient, scale under the cup) [S: `R19_PREP_AUDIT.md:405`]. That removes both the finger contact and 3–5 min of arm time [S: `R19_PREP_AUDIT.md:482`].
3. **Sequence on shared tools: GREEN first, RED last.**
   - Lever base: produce plates first; the squid die is the last lever job of the meal; then the base body is wiped.
   - Chopper: aromatics before eggs or 肉末.
   - Soak tub: broccoli, potato-shred and 三丝 soaks before the clam purge. Or use a second red insert (≈ ¥50–150 [S: `R19_PREP_AUDIT.md:382`]).
   - Spider: blanched vegetables before scalded ribs, or rinse between.
4. **This matches the exposure plan.** Raw protein is fetched just in time (§4), so it naturally comes after the produce prep that fills the prep-first block.
5. **Sink zoning.**
   - **No raw meat is washed at the sink.** SFA: "Avoid washing raw meat to prevent the spread of pathogens" [S: SFA advisory Dec 2024, p.3].
   - USDA found that 26 % of people who washed raw poultry transferred bacteria to salad lettuce. 60 % had bacteria in the sink afterwards, and 14 % still did after cleaning it [S, snip: USDA 2019 study press release].
   - The audit's assumed rib "wash/rinse" [S: `R19_PREP_AUDIT.md` items; `r19_asbought.md:65` "a rinse is [assumed]"] becomes the scald he already does in meal B [S: `r19_asbought.md:83`]: kettle water over the ribs in the red basket in the tub, drained by lifting the insert.
   - **Clams** stay in the red soak-tub insert (purge and scrub).
   - Any RED water is poured **last** in the meal's sink sequence. After it, the robot rinses the basin with the remaining kettle water [E]. No produce or wok goes into the sink after a red drain until that rinse.
   - The wok rinse is not RED (the residue is cooked).
6. **Spatula and pad.**
   - Raw protein enters the wok from its container, so the spatula only touches it in the pan, where it is being heated.
   - The pad becomes a removable rimmed tray (inventory #26), into the DW after every meal.
   - The spatula is rinsed under the tap on the existing wok-rinse trip [E: the extra time of a second item under the tap is ND].
7. **RED to BLUE.**
   - Serving vessels never hold raw food, except the steaming plates. The fish and the marinated ribs are steamed on the plate they are served on, as he does, so the heat covers the plate.
   - The probe (§5) only enters food at the end of cooking. If a check fails, it is dipped in near-boiling kettle water before the next use [E].
   - **Blanched pork-belly cubes (B)** are only part-cooked when cut. They are a RED item on the lever base: cut them last, on a dedicated 30 mm grid plate.
8. **Gripper hygiene.**
   - After any RED grasp, swap back from the red set before touching BLUE tools.
   - The cooking set only holds keyed blocks, never food.
   - Jaws and blocks are wiped daily (inventory #33).
9. **Allergens (gap #38, short):**
   - tag each recipe and station channel with its allergens: peanut oil, sesame oil, shellfish (shrimp, squid, clams), egg, soy, wheat in sauces;
   - if a household member is allergic, run a full DW clean of shared cups and drums and a line flush before that meal [E];
   - not otherwise designed here.

### 3.2 What it costs [E/M]
- **Parts [E]:** a red finger set (silicone sleeves, carrier), a red basket, a red tub insert, 2–3 red lidded trays and a red output bowl. That is about ¥300–700 [E: per-item prices from the analogues above; unpriced].
- **Arm time:**
  - 2–4 extra finger swaps, +0.3–1 min [M];
  - the end-of-meal basin rinse, about 0.5–1 min [E];
  - pour-portioning in A saves 3–5 min [S: `R19_PREP_AUDIT.md:482`].

---

## 4. Time and temperature at 30 °C

### 4.1 Guidance

| Source | Rule |
|---|---|
| USDA FSIS | Discard perishables after more than 2 h at room temperature, or more than 1 h above 32.2 °C. The danger zone is 4.4–60 °C (40–140 °F) [S: `r14_storage_market.md:355`; S, snip: usda.gov/node/26288] |
| FSANZ 2 h / 4 h | 5–60 °C: < 2 h, use or refrigerate; 2–4 h, use now; > 4 h, discard. **Cumulative, including prep time** [S: `r14_storage_market.md:357`] |
| SFA (Singapore) | Danger zone 5–60 °C; ready-to-eat food not more than 4 h in it (food establishments); thaw at 0–4 °C [S: SFA advisory Dec 2024, p.2–3; SFA "Proper temperature for hot foods" poster]. Consumers: refrigerate perishables within 2 h [S: `r14_storage_market.md:358`] |
| FDA Food Code 3-501.19 | Time as a control: 4 h maximum; the 6 h option needs ≤ 21 °C ambient, so it does not apply here [S: `r14_storage_market.md:356`] |
| Repo rule | ≤ 1 h for raw meat, seafood, tofu and cut vegetables, tracked cumulatively, fetched just before cooking [S: `r14_storage_market.md:361`; `DECISIONS.md:252`] |

The kitchen is at about 30 °C, under USDA's 32.2 °C line. Near the hood and the wok it can run warmer [E; the plume estimate in #15 is about 90 °C 30 cm above the wok, `README_R10.md:515` per #15]. **Keep the 1 h cap as a hard limit. Plan to a 45 min robot budget, which leaves about 15 min for the market trip and loading** [E].

### 4.2 Exposure per raw item, today's model

**Method [M]:**
- Meal clock and step starts: `meal_stew_r18_userrice.json`.
- Prep-first block P (low–high): A 6.9–17.4, B 6.0–10.4, C 5.3–12.7 min [S: `prep_demand.json` `fit`; `R19_PREP_AUDIT.md:475-477`].
- Today the model fetches the cold box **once per meal** (FRIDGE = 1 in A/B/C [S: `prep_demand.json` set_instances]). So every chilled item is taken as out from the start of the prep-first block until its heat step starts: exposure = P + step start.
- **Not counted:** the market-to-home trip; the cold box's own warm-up (the tub has no insulation spec); and the come-up time of slow heat (water bath, cold-water blanch) until the core passes 60 °C (ND, add it [E]).

| Meal | Item (mass [S: audit]) | Heat step and start (meal min) [S: meal json] | Exposure today [M] | Note |
|---|---|---|---|---|
| A | 排骨 ribs 320 g + 蛤蜊 clams 250 g | 4 cups into the stew-pot water bath, 7.3 | **14–25 min** | then a slow water-bath come-up (ND) |
| A | 五花肉 pork belly 150 g (raw slices) | wok 干锅, 27.0 | **34–44 min** | slices sit in the output bowl between the meat slicer and the wok |
| B | 五花肉 belly 600 g (whole strip) | cold-water blanch in the wok, 0.8 | 7–11 min | + come-up from cold water (ND) |
| B | 排骨 ribs 500 g | scald + into the soup pot, by 7.2 | 13–18 min | |
| B | 海鲈鱼 sea bass 600 g | steamer, 45.9 | **52–56 min** | over 45 min; with ≥ 4 min of transport, over 60 min |
| B | 鸡蛋 eggs ×5 (if refrigerated) | wok 番茄炒蛋, 61.6 | **68–72 min** | **over 60 min**. Eggs in shells; the user's storage practice is unknown |
| C | 排骨 ribs 450 g, marinated (raw-egg-free) | steamer, 3.6 | 9–16 min | |
| C | 鱿鱼 squid 400 g | scald + wok, 15.8 | 21–29 min | |
| C | 瘦肉 lean pork 180 g, 上浆 | stew pot, 27.8 | **33–41 min** | |

**Reading:**
- Even with a single fetch, A and C stay within 45 min.
- B fails: the fish (52–56 min) and the eggs (68–72 min).
- The longer the prep block, the worse every item gets. That is why produce should take the prep block and protein should come out later.

### 4.3 Proposed limits and cold-box arrangement

1. **Per-item must-cook-by clock in the scheduler (#4).**
   - The clock starts when the item leaves the cold box.
   - **Limits [E, based on §4.1]:**
     - plan target ≤ 30 min;
     - soft alarm at 45 min: the user is told and the scheduler re-orders;
     - hard limit 60 min: the robot does not cook it, flags it and asks the user to discard it.
   - Minutes count cumulatively (FSANZ). If the box is returned to the fridge, its out-time still counts.
2. **Just-in-time fetch per protein group.** 2–3 fetches per meal at about 45 s each, about 1.5–2.3 min of arm time per meal [S: `r19_system_cost.md:148`]:
   - A: ribs and clams at the start of the meal; belly about 5 min before 干锅.
   - B: belly and ribs at the start; fish about 5 min before steaming; eggs about 5 min before cracking.
   - C: ribs at the start; squid and lean pork together around 12–15 min.

   Expected exposure: item prep time plus the wait, about **≤ 10 min** for each item [E, from the item arm times in `prep_demand.json`, e.g. fish 50–75 s, eggs 135–205 s].
3. **The box goes back between fetches.** It shares the lever work spot and is "never out together with the lever base" [S: `R19_PREP_LAYOUT.md:46`], so it has to leave anyway when the lever is used.
4. **Size and shape.** Meal B needs about 1.7 kg of protein plus a 336–367 mm fish [S]. The 2.4 L, 300 mm tub can't take it [M].
   - **Options [E]:** a second door-bin box, or a longer box (≥ 400 mm, not possible in a door bin), or the fish on a lidded plate on a fridge shelf. Shelves are unreachable [S: `DECISIONS.md:269`], so the user would have to put the fish on the plate at the counter at fetch time, which is a user step.
   - **Simplest:** the user puts the fish in a lidded red tray in an **ice-packed cooler on the counter** (option O8) [S: `r19_system_cost.md:225`].
   - The hold time of that cooler must be measured (logger) before relying on it.
5. **Door-bin temperature.**
   - Survey data put door compartments at 5.06 ± 1.69 °C, against 3.41 °C in the inner box [S, snip: koreascience JAKO202332472161643].
   - Log the user's door bin for one week (hardware step in #23).
   - If it is above 5 °C, either lower the fridge setpoint, or let the cold box hold raw protein **only on cooking days** (same-day staging, as `DECISIONS.md:281` already says). Overnight thawing then has to happen on a shelf, loaded by the user.
6. **Lids and chill on the counter.** Every red container is lidded (pests, gap #39). An ice pack or eutectic plate under the red tray is cheap [E], but its effect is ND until measured.
7. **Other perishables.**
   - Marinated ribs (C) are prepared by the robot during the prep block; the marinade is made from station cups.
   - Cut produce and tofu fall under the same 1 h rule [S: `r14_storage_market.md:361`]. They meet it at about ≤ 45 min in A/C [M].
   - Oyster sauce stays chilled (Peltier e4) [S: `r19_seasoning_sizing.md:184,205`]. Slurry is made fresh daily [S: `:185`].

---

## 5. Doneness check

### 5.1 Targets

| Food | Sourced target | Source |
|---|---|---|
| Meat and poultry (food businesses, SG) | probe thermometer; **≥ 75 °C for 2 min** internal | [S: SFA advisory Dec 2024, p.3 "(ii) Check internal temperature of cooked food using probe thermometers … at least 75°C for 2 minutes"] |
| Reheated food (SG) | ≥ 75 °C for ≥ 2 min | [S: SFA "Proper temperature for hot foods" poster] |
| Pork cuts / ground meat / poultry / fish / egg dishes (US) | 63 °C + 3 min rest / 71 °C / 74 °C / 63 °C / 71 °C | [S, snip: FSIS es/node/3293; foodsafety.gov chart] |
| Clams (shell) | steam until open, then 4–9 min more; boil 3–5 min after opening; discard unopened shells. These sources describe oysters, "same for clams" | [S, snip: capecod.gov shellfish tips; oregon.gov ODA] |

**Proposal [E]:**
- Use SFA's **75 °C / 2 min** as the robot's pass line for every thick protein. It is the stricter rule and the local one.
- For thin stir-fry slices (≤ 3 mm pork belly, lean-pork slices, squid pieces), probing is impractical. Their rule is: wok surface ≥ T (thermal camera) for ≥ t seconds of stirring.
- T and t are set **once per dish on the bench with the probe** (#23 hardware step), not invented here.

### 5.2 Where to check (A/B/C)

| Dish | Check [E] |
|---|---|
| A 蛤蜊排骨盅 (30 min water bath) | probe the largest rib piece in one cup; cup liquid ≥ 75 °C for 2 min; camera: all clams open |
| A 干锅 pork belly slices | time-at-heat rule |
| B 红烧肉 (blanch + 40 min braise) | probe one cube at the reduce step |
| B 清蒸鲈鱼 (**6 min steam**) | **probe the thickest part at the spine.** The most critical check: a short cook on a thick, variable-size fish |
| B 鲜笋排骨汤 (60 min) | liquid boiling (temperature in the pot) + time; probe optional |
| B 番茄炒蛋 | egg set (camera) + time-at-heat; 71 °C (US egg dishes) as the bench target |
| C 芋头蒸排骨 (30 min steam) | probe the centre rib piece |
| C 青瓜肉片汤 pork slices 3 min | liquid at a boil + time |
| C 鱿鱼 | scald + time-at-heat |

### 5.3 Hardware and movement set [E]
- **Probe.** An instant-read thermocouple class is the reference: Thermapen ONE, 1 s full reading, ±0.3 °C (−20…120 °C), probe 3.0 mm tapering to 1.5 mm, IP67 [S, snip: thermoworks.com]. A robot version needs its own readout: a K-type sheathed probe on the keyed 30 mm block, wired to the controller. Price ND.
- **Movement set PROBE.**
  - Fetch the probe from its holder.
  - The camera picks the thickest piece.
  - Insert along a straight ≤ 50 mm approach. This fits the existing contact-window rule [S: `DECISIONS.md:21`].
  - Hold until the reading is stable (2–5 s [E]); log it; withdraw; dip in kettle water; return.
  - About 20–40 s per check [E]; 1–3 checks per meal.
  - Under the hood band it has to come from the front, as the spider and lid do [S: `DECISIONS.md:363-366`]. **Sim check needed.**
- **Fail path.** Below target: put the lid back on (or keep the steam or braise going) for +2 min, then re-probe. After two fails, alert the user.
- **Logging.** Every probe value and every time-at-heat is written to the meal log. That log is the evidence the issue's closing condition asks for.

---

## 6. Cleaning procedure and who does it

**Minutes:** [E] unless stated. Basis: about 10–15 s per item to load or unload a dishwasher, and the hand-wash times of household equivalents. **None is measured.** All feed #28.

### 6.1 During the meal (robot)
- Wok + spatula rinse at the running tap between dishes (existing set, 48.9 s for wok plate + rinse [S: `DECISIONS.md:400`]).
- Red finger set: rinse under the tap after the last red grasp (RIP, about 10–20 s).
- Probe dip after each check.
- Used cups back into their caddy [S: `r19_seasoning_cups.md:374`].
- End of meal: basin rinse with the remaining kettle water [E, new set].
- Faucet off (existing).

### 6.2 After each meal

| Task | Who | Items | Minutes [E] |
|---|---|---|---|
| Load DW (caddies as baskets): cups 9–13, caddies 3–4, drums 1–3 [S: `r19_seasoning_cups.md:365-370`], baskets 1–2, soak-tub insert(s), cold box(es) and red trays 2–4, slot trays 1–3, lever plates and pushers 2–4, chopper bowl + blade, egg-cracker stand (B), red finger set, spatula + pad tray, spider, carrier, probe, output bowls | **user** (robot later, #31) | about 30–45 pieces, fewer if the caddies hold the small ones | 6–9 |
| Unload DW and put away (tool dock, drawer, finger rack, caddy dock about 1 min [S: `r19_seasoning_cups.md:376`]) | user | same | 4–6 |
| Wok final wash + oil | user (robot rinse first) | wok | 1–2 |
| Meat slicer clean (A, C) | user | blades, chute, pusher | 3–6 (only A/C) |
| 卓晋 slicer disc and lid rinse (when used) | user | disc, lid, pusher | 1–2 |
| Fish sled rail and blade (B), 铡刀 (B/C) | user | | 1–3 |
| Abrasive peeler drum | robot rinse; user wipe | | 0.5–1 |
| Wipe: lever base body, work spots, faucet block, fridge handle, gripper jaws | user | | 2–3 |
| **Total per meal** | | | **A ≈ 18–28, B ≈ 17–27, C ≈ 18–28** |

**Totals [E].** Summing the rows gives about **17–28 min**. Two things change it:
- When #31 automates loading, the two dishwasher rows (10–15 min) go to the robot.
- Making the spatula pad and the slot trays dishwasher-safe is already counted.

The biggest single user items are the meat slicer and the dishwasher loading.

### 6.3 Each cooking day (robot unless stated)
- **Seasoning station:**
  - slurry cell: discard and rinse;
  - water flush and suck-back on every channel [S: `r19_seasoning_sizing.md:205` (d) cleaning column];
  - wipe any portioner chutes that saw steam.
- **Waste bin:** empty it. Lidded bin. User, about 1 min.

### 6.4 Weekly (user unless stated), about 15–25 min [E]
- Deep-clean the lever base body, the 卓晋 body (wipe, no immersion [S: `market_r10.md:385`]), the abrasive peeler and the meat-slicer body.
- Cart surfaces and arm: degrease wipe. Covers decision: #15.
- Seasoning station clean in place (CIP): about 10 min of the robot's own cycle [E] plus 2 min of the user checking tubes.
- Inspect the finger sleeves, slot trays and printed jigs for cuts, stains or delamination. Replace on damage, per SFA's replace rule [S: SFA advisory Dec 2024, p.2].
- Descale the kettle.
- Read the door-bin logger (first month).
- **Validation phase only: ATP swabs.** 10 × 10 cm area, zigzag strokes [S, snip: manitoba.ca luminometers]. Vendor default limits are 10 RLU (pass) / 30 RLU (fail), and the facility should set its own limits from clean and soiled baselines [S, snip: hygiena.com lower-and-upper-rlu-limits PDF]. ATP is a cleanliness signal, not a pathogen test.
  - Swab after cleaning: the red finger sleeve, the green finger sleeve, a slot tray, the squid die, the soak-tub insert, the sink basin, the spatula pad, the faucet block.

### 6.5 Interval items
- Silicone pump tubes: 200 h [S: `r14_storage_market.md:105`], or 6 months [E], whichever comes first.
- Finger sleeves: on wear, at least every 3 months [E].
- Printed PP jigs: on damage.

---

## 7. Material compliance path

1. **Food-contact list.**
   - Stainless 304/316L: GB 4806.9-2023 [S: `r14_storage_market.md:213`].
   - PP / HDPE: GB 4806.7-2023 [S: `:212`].
   - Silicone: GB 4806.16-2025, in force 2026-09-02 [S: `:215`].
   - Equivalents: EU 10/2011 and FDA 21 CFR 177.x.
   - Buy only with a declaration of compliance [S: `:225-226`].
2. **Printed parts.** Only for non-wetted parts or brief dry contact [S: `:227`]. Where print is the only route:
   - use a filament with its own declaration: BASF Innofil3D PP (EU 10/2011 + FDA, details behind a login [S, snip: specialchem]), or Nanovia PA Food Industry (EU 10/2011, FDA 21 CFR 178.3297 [S, snip: rs-online]);
   - print with a stainless nozzle;
   - treat the part as a consumable.

   PA absorbs water, so a dishwasher is a risk for it [E].
3. **PETG** only for non-food parts: docks, racks, keys, guides that see no food.
4. **SFA check.** Singapore-specific food-contact-material rules for home equipment: **ND** (not researched in this round). The SFA advisory covers food businesses, not home robots. It is used here as practice guidance only.

---

## 8. Honesty notes
- **Exposure numbers** are arithmetic on modelled meal and prep timelines, with a single cold-box fetch. They leave out the market trip and the core come-up time. Real values need the logger and the scheduler clock.
- **The 45 min planning budget, the 30 min target, the red/green/blue scheme, the probe set times and all user minutes are my estimates.** The SFA, USDA, FSANZ and FDA numbers are sourced.
- **Some sources were read only as search snippets:** NSF/ANSI 184, the PETG HDT, the Korean fridge survey, the USDA temperature chart, the clam guidance, the ATP limits and the Thermapen specs. Each is marked "snip". The two SFA documents were read in full (PDF text extracted).
- **No dishwasher model is known** (#31). Its sanitize-cycle temperature, rack length for the 0.45 m spatula and the fish rail, and its cycle time are ND.
- **Not checked in the sim:** the PROBE set, the red-container pours, the extra finger swaps, the basin rinse, JIT cold-box trips with the lever-spot conflict.

---

## 9. Decisions for the user

1. **Raw protein in lidded red containers, loaded by you into the cold box. The robot pours instead of grasping; a red finger set covers the rest (≈ ¥300–700 in parts [E]).** Accept?
2. **Ribs are not rinsed at the sink.** They are scalded instead, as SFA advises against washing raw meat. This differs from the audit's assumed rinse in A and C. Accept?
3. **Cold box:**
   - (a) just-in-time fetches, 2–3 per meal, about +1.5–2.3 min of arm time;
   - (b) for meal B, a second box, or an ice-packed counter cooler (O8) for the fish, which needs a hold-time test.

   Which do you prefer?
4. **Doneness by probe at SFA's 75 °C / 2 min** for thick protein (the fish, ribs, braised belly), plus a bench-set time-at-heat rule for thin slices. Accept buying a probe thermometer later (price ND)?
5. **Materials:** no printed PETG in food contact. Silicone sleeves on machined carriers for the fingers; machined or moulded PP trays; stainless for the basket, drum and pad. Accept the extra cost and lead time?
6. **Meat slicer used for meat only**, cleaned by you after each meat run (about 3–6 min). Or have the butcher slice the meat?
7. **Eggs:** do you keep them in the fridge? If so, they get a just-in-time fetch too.
8. **Your cleaning load:** about 17–28 min per meal plus 15–25 min per week [E] until #31 automates the dishwasher. Is this acceptable as the #28 input?

## 10. Next steps / issues to file
1. **[process] Per-item must-cook-by clock in the meal scheduler** (`meal16.py` / `r19prep_demand.py`): just-in-time cold-box trips, a 45/60 min alarm, a cumulative clock. Re-run A/B/C exposure. Refs #4, #23.
2. **[hardware] Log door-bin temperature for 1 week**, and the hold time of an ice-packed cooler (O8) at 30 °C.
3. **[mechanical] Cold-box sizing for meal B** (a 336–367 mm fish plus about 1.7 kg) and a red-container family with keyed handles. Then movement sets RED_POUR and a sim check at the lever spot.
4. **[mechanical] Washable finger redesign:** silicone sleeve over a machined carrier; FSR and springs sealed; red set. Refs #15 for the wok-side heat on the same parts.
5. **[sim] PROBE movement set** under the hood band (front approach), plus a holder spot.
6. **[hardware] Probe-thermometer cooks:** the fish (6 min steam), steamed ribs, rib cups, braised belly. Set time-at-heat rules for thin slices. ATP swab protocol and baseline.
7. **[process] Seasoning-line hygiene:** a daily flush and suck-back cycle; a weekly CIP; a chilled 蚝油 and slurry box; replace the pet-feeder food path; allergen tags per channel. Refs #5.
8. **[process] Dishwasher fit list for #31:** spatula 0.45 m, fish rail, 铡刀, slot trays. Which items need hand washing? Get the model's sanitize temperature.
9. **[process] Spatula pad → rimmed removable tray;** spatula rinse added to the wok-rinse set.

## 11. Sources (web, read 2026-10-14)
- SFA, "Adopting good food safety and personal hygiene practices", advisory to food business operators, 06 Dec 2024 (PDF, text extracted): https://www.sfa.gov.sg/docs/default-source/circulars/others/2024/advisory-on-food-safety-practices-for-food-establishments_dec-24.pdf
- SFA, "Proper temperature for hot foods" poster (PDF, text extracted): https://sfa.gov.sg/docs/default-source/educational-materials/proper-temperature-for-hot-foods.pdf
- USDA 2 h / 1 h rule, danger zone (snip): https://www.usda.gov/node/26288 ; archived FSIS take-out sheet (via r14): https://cybercemetery.unt.edu/oilspill/20130218140944mp_/http://www.fsis.usda.gov/Fact_Sheets/Safe_Handling_Take-Out_Foods/index.asp
- USDA safe minimum internal temperatures (snip): https://www.fsis.usda.gov/es/node/3293 ; https://www.foodsafety.gov/print/pdf/node/10
- USDA 2019 raw-poultry washing study (snip, press coverage): https://www.usda.gov/node/30846
- NSF/ANSI 184 residential dishwashers (snip): https://www.nsf.org/consumer-resources/articles/dishwasher-certification ; https://nsf.org/knowledge-library/dishwashers
- PETG Basic HDT 69 °C, Vicat 78 °C (snip, retailer spec table): https://www.matterhackers.com/store/l/bambu-lab-petg-basic-filament-175mm-1kg/sk/MS62P4MX
- Korean domestic refrigerator temperature survey (snip): https://koreascience.kr/article/JAKO202332472161643.do
- Food-contact filaments (snip): BASF Innofil3D PP https://www.specialchem.com/plastics/product/basf-3d-printing-solutions-innofil3d-pp ; Nanovia PA Food Industry https://uk.rs-online.com/web/p/3d-printing-materials/0635157
- Shellfish cooking (snip): https://www.capecod.gov/wp-content/uploads/2022/03/Tips-for-Fresh-and-Tasty-Shellfish-Handling-Storage-and-Cooking.pdf ; https://www.oregon.gov/oda/food-safety/shellfish/pages/safe-handling-consumption.aspx
- ATP limits (snip): https://www.hygiena.com/documents/64166/lower-and-upper-rlu-limits-for-atp-monitoring-programs.pdf ; https://gov.mb.ca/agriculture/food-safety/education-resources/luminometers.html
- Thermapen ONE specs (snip): https://thermoworks.com/thermapen-one-upgrade-special
- Repo files: as cited inline (`DECISIONS.md`, `research/*.md`, `sim/r10/claude/R19_*.md`, `README_R10.md`, the two results JSONs).
