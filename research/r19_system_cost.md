# R19: system-level cost-down and task offload

Date: 2026-10-13. This was read-only research. Sources were the project files plus WebSearch/WebFetch: 1688 market pages, search snippets and smzdm. I did no purchasing, no logins, no carts and no supplier contact. No existing file was changed.

**Price tags used below**
- **[1688 2026-10-13]**: a 1688 wholesale listing price seen today. These are often teaser or start prices, and retail is higher. All are **unconfirmed**.
- **[R09 alw]**: a China planning allowance from `sim/r09/integrator/results/costs.csv` (2026-10-09). These were never quoted. **Unconfirmed.**
- **[mkt_r10] / [r14] / [r15]**: prices already collected in those research files, with their own dates and sources. **Unconfirmed.**
- **est.**: my own estimate. No source.

**Arm-time numbers**
- They come from the project's own `meal16.py` (SET=stew ARM=r18) schedule.
- I re-ran its scheduler from a scratch copy, with changed action times per option. No project file was written.
- Times for options are **model estimates**, not checked paths.

---

## 0. Bottom line

1. **Most of the money is not in the appliances.**
   - Every bought kitchen appliance together (cookers, pots, rice cooker, fryer, prep machines) costs about **¥5–13k**.
   - These cost more:
     - the arm (another agent; placeholder ¥45k–180k);
     - the cart and its installation (≈ ¥33–35k allowance);
     - safety plus PC, vision and the thermal camera (≈ ¥27–28k allowance);
     - qualification labour (≈ ¥20k allowance);
     - the custom seasoning station (≈ ¥7–18k in parts, plus build labour).
   - So swapping one ¥400 appliance for another barely moves the total. **Deleting a custom subsystem, or a whole family of motions that must be verified, does.**
2. **The wok is 55 % of the arm's modelled time:** 38.0 of 69.2 arm-minutes over the three meals.
   - stirring: 13.2 min;
   - plating trips with the sink rinse and the spatula round trips: 15.7 min;
   - wok to the tap or the sink (fill and dump): 6.1 min;
   - waiting at the wok: 3.0 min.
3. **The spatula round trip to its rest is the single most wasteful item.** It takes 54.8 s of every 134.3 s plating trip, which is 6.4 min over 3 meals.
4. **Next biggest:** rice 13 % (an assumption, never checked), cup pours 11 % (55 pours), lids 7 %.
5. **Large amounts of arm work are not in the meal model at all:** prep, cup staging at the seasoning port, and fridge fetches. Removing them saves motions that were never timed.
6. **Best by the requested score** (money saved × motions removed / risk), as listed in §5: user-filled sauce cups instead of the dosing station, prep out of the robot loop, and rice done by the user. **All three move work to the user, so only the user can decide them.**
7. **Best pure-engineering levers** (no extra user work):
   - a **motorised stirrer and tilt cradle at the existing wok**: arm time −23 to −33 min per 3 meals;
   - the cheap pair of a **spatula holster on the cart** and a **sensor add-on on the faucet**: −9 min.

---

## 1. Rough bill of materials (current R18 design)

| # | Item | Price basis (CNY) | Source / tag | Status |
|---|---|---|---|---|
| **Robot core (placeholders, covered by another agent)** | | | | |
| 1 | Arm: UR5e + controller + pendant | **180,000** (historical 2022 China procurement); FR5 allowance 45,000 | [R09 alw], posts/r09/integrator.md | placeholder, unconfirmed |
| 2 | Gripper DH PGC-140-50 + washable keyed fingers | 12,000 | [R09 alw] | placeholder |
| 3 | Finger sets P1–P7, change rack, root force sensors | ≈1,000–3,000 | est. (print materials ¥200–400 for 2 sets [mkt_r10 §13.5]; sensors unpriced) | unpriced |
| **Base: tethered cart** (R10: 2 drive wheels + 2 casters, no ballast) | | | | |
| 4 | 2 drive wheels + drivers (ZLTECH ZLLG65 class) | 5,000 | [R09 alw] ¥10,000 for 4, halved (est.) | allowance |
| 5 | 2 spring-applied brakes + hub couplings | 4,000 | [R09 alw] ¥8,000 for 4, halved (est.) | allowance |
| 6 | Frame, mast, cantilever beam, covers, casters | 5,000–7,000 | [R09 alw] ¥7,000 included ballast | allowance |
| 7 | Cable reel, floor guide, tension system | 4,500 | [R09 alw] | allowance |
| 8 | 48 V supply and current limit | 2,500 | [R09 alw] | allowance |
| 9 | Docking stops and site installation | 12,000 | [R09 alw] | allowance |
| **Control, sensing, safety, power** | | | | |
| 10 | Industrial PC, vision, network | 8,000 | [R09 alw] | allowance |
| 11 | Wok thermal camera (256-class module) + colour camera | 950–1,430 (Tiny1-C ¥950; 256 module ¥1,430) + colour cam est. 100–500 | [1688 2026-10-13] | unconfirmed |
| 12 | Home safety package (presence sensing, E-stop, RCD/PE, interlocks) | 18,000 | [R09 alw]; DECISIONS target ¥10–20k | allowance |
| 13 | Stove guard (Innohome type), StoveTop FireStop canister, smoke detector | **not found** | [r15] lists products, no CNY price | unpriced |
| 14 | Dry power track; new 20 A point for the 3.5 kW cooker | 3,000 + electrician (unknown) | [R09 alw] | allowance / unknown |
| **Cooking** | | | | |
| 15 | Concave 3.5 kW induction (美的 MC-E35D2 / 九阳 N3501 / 美的 MC-30TC01) + bolt-on knob servo | 320–689 + servo kit est. 100–300 | [r15] (smzdm 2024-07, cnpp) | unconfirmed |
| 16 | 34 cm carbon-steel wok, keyed grip block, keyed rim slot | est. 100–300 | wok masses sourced in [r15]; prices not | unpriced |
| 17 | Spatula, spider, lid with tab, dish carrier, 2 guarded plate stands, waste basin, oil cup | est. 300–800 | — | est. |
| 18 | Zone 2 flat induction (米家电磁炉 N1) + 30 cm pot + rack | 149 + pot est. 100–300 | [1688 2026-10-13]. The writable MIoT heat level was verified only for 米家电磁炉2 [r15]; N1's control is **unknown** | unconfirmed |
| 19 | Electric water-bath stew pot + smart plug | 37–209 + 55.9 | [1688 2026-10-13]; plug [mkt_r10] | unconfirmed |
| 20 | Rice cooker with app start (米家 C1) | 145 | [1688 2026-10-13] | unconfirmed |
| 21 | Rice and flour/starch hoppers, metering augers, scale | est. 1,000–3,000 (DIY) | [r14]: no product priced | unpriced |
| 22 | Fryer with oil filtration (Tefal Oleoclean Pro FR8040) | €113–187 (EU retail) ≈ ¥900–1,500 est. | search snippets: galaxus.it/at, mediamarkt.be (2026); CNY price not found | unconfirmed |
| **Seasoning station (R14/R17)** | | | | |
| 23 | 12 stepper peristaltic channels | 3,000–5,300 (Kamoer KAS ¥248.9 … KCS ¥441.75 each) | [1688 2026-10-13] | unconfirmed |
| 24 | 4 sealed agitated powder augers | est. 1,600–4,000 (DIY). Market reference: ZONESUN servo auger US$3,400 per powder | [r14] | est. |
| 25 | 2 paste syringe extruders | est. 1,000–3,000 (DIY) | — | est. |
| 26 | 花椒 vibratory feeder | est. 300–800 | — | est. |
| 27 | 0.1 g weighing + magnetic stirrer + nozzle head + controller + enclosure | est. 1,000–3,500 (A&D EK-6100i ≈US$351 as an upper reference) | [r14] | est. |
| 28 | Rotary pour drum + servo holder + ~20 robot cups | est. 400–1,000 | — | est. |
| **Prep (R11 tool set)** | | | | |
| 29 | D1 domestic set: 卓晋 3-in-1 slicer (¥843 JD), AY-403 lever base + plates (¥269–305), peeler (¥148–155), spinner, small tools, 2 smart plugs, bowls | **1,700–2,400** (or 3,600–5,300 with HLC-300) | [mkt_r10 §13.3] | unconfirmed |
| 30 | 3D prints (guides, docks, trays, pads) | 200–400 materials, 85–95 h printing | [mkt_r10 §13.5] | est. |
| **Misc / engineering** | | | | |
| 31 | Fridge cold box with bridge bar, faucet clip-on block, water jug | est. 100–300 | — | est. |
| 32 | Qualification labour | 20,000 | [R09 alw] | allowance |
| 33 | One project reserve | 15 % | [R09 alw] practice | — |

**Totals (rough)**
- Everything except rows 1–2: **≈ ¥97k–120k**, or **≈ ¥111k–138k** with the 15 % reserve.
- Adding the arm and gripper placeholders: **≈ ¥170k–330k**.
- These are planning allowances, not quotes.

**Biggest cost drivers, in order**

| Rank | Driver | Amount |
|---|---|---|
| 1 | Arm | placeholder ¥45–180k |
| 2 | Cart hardware + docking/installation | ≈ ¥33–35k |
| 3 | Safety package + PC/vision + thermal camera | ≈ ¥27–28k |
| 4 | Qualification labour | ≈ ¥20k. It grows with every distinct motion and mechanism to verify. |
| 5 | Custom seasoning station | ≈ ¥7–18k in parts, plus build labour (unknown, large: about 19 actuators) |
| 6 | Cooking appliances | ≈ ¥3–7k |
| 7 | Prep set | ≈ ¥2–6k |

**Not priced at all:** fire suppression, the 20 A circuit, the wok, the DIY hoppers, finger sensors, and every build-labour hour.

---

## 2. Biggest arm-motion drivers

Source: `meal16.py SET=stew ARM=r18`, decomposed by action. The model's totals match: arm busy A 16.9 / B 31.4 / C 20.9 min, which is **69.2 arm-minutes over the 3 meals**. Meal totals are 39.5 / 75.6 / 38.6 min.

| Driver | 3-meal arm time | Share | Uses (3 meals) | Evidence status |
|---|---|---|---|---|
| **Wok plating trip**: spatula to its rest → faucet open → wok lift, tip on plate, rinse under the tap, back → faucet close → spatula back | **15.7 min** (7 × 134.3 s) | **22.6 %** | 7 | Wok chain 48.9 s, faucet lever 3.5 s and spatula 26.9 s are checked. The free moves (23.6 s per trip) are estimates. |
| · of which spatula rest ↔ stroke start | 6.4 min | 9.2 % | 14 | checked (R18b) |
| · of which the wok chain itself | 5.7 min | 8.2 % | 7 | checked (R17/R18) |
| · of which free moves | 2.8 min | 4.0 % | 28 | estimate, not collision checked |
| · of which the faucet lever | 0.8 min | 1.2 % | 14 | checked |
| **Stirring** (strokes × 1.3 for one-arm pauses) | **13.2 min** | **19.1 %** | 8 stir sets, **≈247 strokes** (A 42 / B 148 / C 57) | Stroke cycle checked (2.63 s per stroke). The 1.3 pause factor is an assumption. |
| **Rice**: dose, wash at the sink, water, load the cooker | **9.0 min** | **13.0 %** | 3 | assumption (180 s), **never checked** |
| **Cup pours** into the wok or pot | 7.3 min | 10.6 % | **55** | 8 s each, an assumption. Pour pose checked 23/72; not chained. |
| Wok to the tap for 1 L (fill) / emptied at the sink (dump) | 6.1 min | 8.9 % | 5 | estimate (73.5 s each) |
| Lids (pot, wok 焖, stew pot) | 5.1 min | 7.4 % | 16 | Pot lid checked (19–20 s, 8 uses). The wok and stew-pot lids are assumed equal. |
| Spider (wok, fryer → plate) | 4.4 min | 6.3 % | 5 | Path checked at the pot. Every meal use is at the wok or fryer: assumed equal. |
| Waiting at the wok (焖 30 s, blanch 90/30 s) | 3.0 min | 4.3 % | 4 | schedule |
| Dish carrier in/out of the steamer | 2.4 min | 3.4 % | 8 | checked (17.7 s) |
| Hot oil poured over a dish | 2.0 min | 2.9 % | 4 | assumption (30 s) |
| Stew cups, arranging | 1.0 min | 1.5 % | 5 | assumption |
| **Total** | **69.2 min** | 100 % | ≈108 action instances, ≈296 grasp/release events (est.) | |

**What this shows**
- **The wok system** (plating trips + stirring + fill/dump + waits) is **38.0 min, 55 %** of all arm time.
- **Only about 41 % of the modelled arm time comes from checked whole paths.** The rest is estimates: free moves, pours, rice, waits, dump/fill, and the spider at the wok or fryer.
- **Most motion instances are cup pours** (55 of ≈108). Each one is grasp → carry → roll → return → release. They are the "tiny movements" the user wants to stop checking one by one.
- **The heaviest and tightest load case is the wok carry with food:**
  - 2.95 kg held, 4.15 of 5 kg payload;
  - PGC jaw moment 6.47 of 7 N·m.
  - That case also sets the gripper spec.
- **The real kitchen will make sink trips longer.** In the user's L-shaped kitchen the sink is on the other leg from the hob, but the sim puts it 0.9 m from the wok. There are 12 sink trips per 3 meals (7 rinses, 2 dumps, 3 fills).

**Arm work NOT in the meal model** (it is extra on top of 69.2 min):

| Work | Estimate | Basis |
|---|---|---|
| Seasoning cup staging from the dosing port, plus kit cups | **≈4–5 min per meal**, ≈20 cups | `timeline14.py` rates (6 + 8 s per station cup, 10 s per kit cup); Wang Gang medians of 4 station cups + 1.5 kit cups per dish |
| Fridge door + cold box out and back | ≈1.5–2.3 min per meal | 25 s + 20 s per trip (R14 estimate) × 2–3 trips (est.) |
| Prep: tray picks, wash, peel, slicer, lever cutter, finger swaps, tool fetch/return | **≈10–20 min per meal**, order-of-magnitude est. only | R11/R12 chains 22–28 s per item, plus tool and finger handling. The homestyle meals have 10–20 prep items. |

**Distinct motion families to verify:** about **27**.

*Cooking phase (14 in the meal model)*
1. stir cycle
2. spatula rest ↔ stroke start
3. faucet lever
4. wok plate + rinse (×2 plating spots)
5. wok dump
6. wok fill
7. lid
8. dish carrier
9. spider
10. cup pour
11. stew cup
12. hot-oil pour
13. rice handling
14. arrange

*Outside the meal model*
- seasoning-port cups, kit cups, drum load;
- fridge door, cold box;
- about 8 prep families: tray pinch or fork, basket pour, sink wash, peeler, slicer chute, lever cutter, finger swap, tool fetch/return.

---

## 3. Automatic stir-fry machines: market facts, and what they cannot cook

| Class | Examples and price | What it does | Limits that matter here | Src |
|---|---|---|---|---|
| **Home pot-type 炒菜机** (paddle in a lidded pot) | 九阳 CJ-A9 ¥530–549; 九阳 CJ-A8 pro ¥670; 苏泊尔 C30HS12 ¥1,300–1,389; 苏泊尔 C30FS10 ¥1,100 [1688 2026-10-13]. 九阳 J7 ¥1,999; 添可 食万 3.0 Pro ¥3,990; 食万 2.0 ¥4,890 [r15/r14] | Paddle stirs. 食万 3.0 Pro doses 8 liquids (water, oil, brine, light/dark soy, wine, vinegar, syrup) by weight and steam-cleans itself [r14/r15]. | **Lid closed while stir-frying; ≤200–230 °C.** The J7 teardown says it "stews, no 锅气" [r15]. Main ingredients go in by hand or at prompts. You lift the pot out to plate. **No public API found for any brand** [r15]: control is app or touchscreen only. | [1688] https://www.1688.com/market/-C8ABD7D4B6AFB3B4B2CBBBFABCD2D3C3.html ; [r15] |
| **Home/light drum type** (滚筒, rotating drum) | 德莱利 / 德莱德利 "多功能炒菜机家用商用滚筒式" ¥1,300–1,499; 湘庭 ¥1,500–1,599 [1688 2026-10-13] | Reseller snippets give 6 L, 2,000 W IH, 3 heat levels, 360° rotating drum, adjustable tilt angle (3 positions; "90°"), ≈7.4 kg, 310×370×365 mm [O, snip, low-quality reseller mirrors] | **Whether the tilt is motorised is not found. Max temperature not found. No API found.** 2 kW versus the 3.5 kW concave unit. Drums tumble slowly (Spyce ≈0.5 Hz [r15]). | [1688] https://www.1688.com/market/-B9F6CDB2B3B4B2CBBBFA.html ; [r15] §2.2 |
| **Commercial drum / cooking robots** | ¥4,800–30,000 (1688 drum units); 50 kg units ¥120,000; commercial robots "1–5 万, up to ≈11 万" | Auto feed, dose, stir, tilt-out, wash | Canteen size and power, 180 kg class (Botinkit 827×920×1,769 mm, 12 kW [r14]). **Not a home option.** | [1688] same page; smzdm summary https://post.smzdm.com/p/adolgvgn/ (2025-01-04) |
| **Planetary stir pans** (行星搅拌炒锅) | ¥1,100–75,200 [1688 2026-10-13] | Sauce and filling cookers with tilt-out | Industrial; useful only as a mechanism reference for a DIY wok stirrer | https://www.1688.com/market/-D7D4B6AFB7ADB3B4B9F8.html |

**Meal-list check.** Which of the 15 homestyle dishes, plus the wok helper steps, these machines can cook. These are my judgements from the facts above, not tests.

| Dish / step | Pot-type (lidded, ≤230 °C) | Drum (open mouth, 2 kW) |
|---|---|---|
| 红烧肉: fry, 糖色, braise 40 min, 收汁 | **Good fit** (九阳 CJ-A9 advertises 收汁) | Probably OK; long braise in an open drum unknown |
| 蚝油西兰花 (stir + 焖 30 s) | OK | OK |
| 番茄炒蛋 (eggs out and back) | OK as a one-pot variant | OK as a variant |
| 清炒荷兰豆 (45 s) | OK, less crisp | OK, less crisp |
| 干锅土豆 (dry stir with 豆瓣/chili) | **Quality risk**: steam is trapped under the lid | Possible |
| 青椒炒鱿鱼 (60 s high heat) | **Quality risk**: squid water, low heat | Risk |
| 酸辣土豆丝 (crisp, 45 s high heat) | **Poor** | **Poor** |
| Blanch-and-drain (红烧肉 blanch, 白灼秋葵娃娃菜, 土豆丝 blanch) | **Cannot drain**: needs a pot lift, or move it to the zone 2 pot with the spider | Tilt dumps water and food together: needs a colander under the mouth |
| Hot oil poured over (luffa, fish, ribs: 3–4 of 15) | Needs the pot lifted, or another small heater | Pouring 40 g of oil from a 6 L drum: unknown |
| Wang Gang wider check | **Cannot do** 润锅 then pour-out (16 recipes), rim pours (18) or 离火 additions (13); the lid hides the 157 camera cues [r15] | Rim pours and 离火 not possible as designed |

**Summary:**
- Either class covers about 4 of the 7 wok dishes well.
- 2 are at quality risk and 1 is poor.
- Every blanch-and-drain and hot-oil step still needs another vessel or a pot lift.

---

## 4. Offload and simplification options

**How to read this table**
- "Arm" is the 3-meal arm time from re-running `meal16.py`'s scheduler with changed times (baseline 69.2 min). "Meals" is the A/B/C total time when it changes.
- "Grasps" counts grasp and release events (est.; baseline ≈296).
- "Families" is distinct motion types removed (−) or added (+).

| # | Option | Cost delta (CNY) | Arm time and motions | Verified actions replaced or broken | Risk | Fit with user decisions |
|---|---|---|---|---|---|---|
| **O1** | **Rice by the user**: rinse and load a 预约 cooker before cooking; the robot does no rice | **−1,000 to −3,000** (no rice hopper/auger/scale module, est.). Any timer cooker ¥42–152 [1688 2026-10-13] | **−9.0 min** (69.2→60.2); meals A 38.2, C 35.6 (−1.3/−3.0); −1 family; −24 grasps | None: the rice motions were never checked | Low | R14 rice design was a proposal. It adds ≈5 min of user work per meal (est.) and conflicts with "the robot cooks end to end". **User decides.** |
| **O2** | **DIY motorised stirrer + tilt cradle on the existing concave wok.** A servo paddle replaces the spatula; the cradle tips the wok onto the plate and into a waste basin; the arm only adds ingredients and pours water from the user-filled jug. | **+1,500 to +4,000** parts (2 gear motors with brakes, drivers, frame, steel paddle, prints; est., unpriced) + design labour. Small savings: spatula, faucet clip. | **(a) Full: −33.5 min** (→35.7); meal B 75.6→69.3; **−≈247 strokes**; −66 grasps; −6 families (stir, spatula rest, wok plate chain, faucet lever, dump, fill), +1 (jug pour). **(b) Keep the sink rinse** (arm carries the empty wok to the sink): **−23.3 min** (→45.9); with O5 −25.7 (→43.5). | Breaks the R15 stroke cycle, R18b spatula rest and hand-off, and in (a) the R17/R18 wok-sink chain. Removes the 6.47/7 N·m food-laden wok carry (could relax the gripper/arm spec; arm agent to judge). | **Med–high**: no open-wok paddle product found; stir quality in a round wok unknown; moving 3 kg + hot oil needs guards; the drum holder must coexist with the paddle frame | (a) **conflicts** with the user's sink-rinse decision (10-12); (b) respects it. Water from the jug fits "containers, no pipe". A permanent fixture at the hob is allowed (heavy, frequent use). **User decides (a) vs (b).** |
| **O3a** | **Buy a home drum stir-fryer** instead of the wok station | ≈ **+300 to +1,100** net: ¥1,300–1,499 [1688] − concave cooker ¥320–689 − servo kit | ≈ like O2(a), **−25 to −33 min**, **only if the tilt-out is motorised (unknown)**; else +1 lever motion | As O2(a), plus the R15 heat/plume work | **High**: specs from low-quality listings, 2 kW, max °C unknown, no API (the arm may have to press its panel), blanch/hot-oil steps need other vessels, quality (§3) | **Conflicts** with the R15 rejection of auto-cook machines (no 锅气). That was an orchestrator proposal, but it touches the user's "really cook" goal. **User decides** the taste trade. |
| **O3b** | **Home pot-type 炒菜机** (九阳 CJ-A9 / 苏泊尔 / 添可 食万) | **+0 to +3,700** net. With Tineco's 8 liquid boxes, 6–8 peristaltic channels could go (−1,500 to −3,500 est.), but you are locked to its app and recipes | **−15 to −25 min** (est.): stirring goes; a **new pot-lift-and-pour plating** motion replaces the wok tip | As O3a | **High**: lid closed, ≤230 °C, "no 锅气"; app or touchscreen only (fragile arm presses); pot grasp unknown | As O3a. **User decides.** |
| **O4** | **Spatula holster on the cart** (R18's open option), so the spatula never goes to the far counter rest | **+50 to +200** (printed holder + spring clip, est.) | **−4.8 min** (→64.4); B −1.3 min; replaces "rest ↔ stroke start" (27 s each way) with a short holster move (est. 5 s) | Replaces the R18b spatula rest path (checked); the holster is unchecked | Medium: unchecked; the holder must stay clear of the arm's own links; hot, oily spatula on the cart | No conflict (tool stays on the robot; counter stays clear) |
| **O5** | **Sensor add-on on the user's faucet** (battery/USB IR valve in the aerator; the faucet stays) | **+37 to +119** (retrofit attachments [1688 2026-10-13]) | **−2.4 min** (→66.8); **−48 grasps** (lever ×4 per sink trip ×12); −1 family | Removes the R17 faucet-lever path and the clip-on block | Low–med: the sensor must see the wok and not trigger as the arm passes; flow loss; battery | 10-12 says "the faucet is not replaced"; this adds a valve at the sink but replaces nothing (10-08 allowed sensor faucets). **User decides.** |
| **O6a** | **User-filled sauce cups** (one premixed 料汁 cup per addition, aromatics in the drum), **no dosing station** | **−7,300 to −17,600** in parts + all station build/qualification (unknown, large) | **−4 to −5 min per meal** of uncounted cup staging (est.); pours ×0.65 → −2.5 min modelled; −2 families (port cups, staging) | Removes the R14 port reach work. The drum, cups and pours stay. | Low technically. **High user burden**: daily 配料 for 3–4 dishes, ≈10–15 min per meal (est.) | R14 station was a proposal; the weekly kit is already a user-fill interface. **User decides.** |
| **O6b** | **Liquids-only station**: 6–8 peristaltic channels + scale; drop the 4 augers, 2 syringes and 花椒 feeder (user cup kit for powders and pastes) | **−3,000 to −8,000** parts (est.) + less build | ≈0 arm time; −3 station mechanisms. It removes the riskiest unproven items (paste extrusion, powder caking at 70–90 % RH). | None | Low | Fits the existing weekly-kit idea. **User decides** (more kit cups). |
| **O7** | **Prep out of the robot loop**: buy cleaned and cut produce (净菜), or the user's weekly prep; drop the R11 prep machines | **−1,900 to −5,700** (prep set + prints) + fixtures + finger sets P3–P7 partly + prep qualification; recurring 净菜 cost (not researched) | **−10 to −20 min per meal** of uncounted prep (order-of-magnitude est.); **−≈8 families** (tray pinch/fork, wash, peel, slicer, lever cutter, basket pour, finger swap, tool fetch) | Makes the R11/R12 carrot and tomato chains and the R13 bench unused | Low technically; availability of 净菜 in the user's city unknown | R16 already moved most knife work outside the robot. This finishes that move, but undoes the R07–R13 direction (R13 trays accepted). **User decides.** |
| **O8** | **Ice-packed insulated cold box on the counter**, loaded by the user at the start, instead of the robot opening the fridge | ≈0 (cooler + ice packs est. ¥30–100, not researched); avoids the high-seal fallback (F&P CoolDrawer SGD 5,000 + OPEX1 [r14]) | −1.5 to −2.3 min per meal (uncounted); −2 families (door arc, door-bin slide), +1 (cooler lid) | Makes the R14 door/box checks unused | **Food safety**: staging ≤1 h at 30–32 °C [r14]; the cooler's hold time is **not sourced** and must be measured | **Conflicts** with the accepted single-door fridge design (10-11 "ok"). **User decides.** |
| **O9** | **Floor rail (7th axis) instead of the driven cart** | Unclear: cart ≈ ¥21–23k hardware [R09 alw] vs rail listings ¥2,000–32,000 (teaser prices [1688 2026-10-13]); saving **0 to ~15k (est.)** | **0 arm time.** The docked cart already moves only along x, so a carriage with the same mount pose keeps the checked paths. Removes docking and localisation logic. | None if the mount pose matches | Medium: rail in the aisle (trip hazard, floor fixing); **cannot turn the L corner to the sink leg** | Conflicts with the user's R09 tethered movable-machine idea and parking at the counter end. **User decides.** |
| **O9′** | Fixed arm, no travel | −≈33k (cart + docking) | Breaks almost every chain: 850 mm reach cannot cover the ≈3 m spread (x −1.48…1.46) | Most | High | Conflicts with the sink rinse and fridge decisions. **Not recommended.** |
| **O10** | **Hinged-lid appliances** for steaming and soup (rice-cooker-style flip lid) instead of a loose glass lid and a lid rack | Unpriced (needs research) | ≈ −3 min (16 lids × 19 s → est. ~8 s hinge push); −1 rack spot | Replaces the R16/R17 lid-to-rack path (checked) with an unchecked hinge push | Medium: steam on the gripper; lid must open under the 0.40 m hood | No conflict |
| **O11** | **Drop the fryer** (1 of 15 homestyle dishes; shallow-fry the 干锅土豆 potato in the wok) | −≈900 to −1,500 (Oleoclean, est. conversion) + counter space | Meal A: spider from the fryer → wok time; ≈0 net | None checked | Low; 8 of 42 Wang Gang recipes deep-fry | **User decides** (dish change) |
| **O12** | **Slicer = 卓晋 (rocker switch + smart plug), not HLC-300** (green-button press) | **−1,800 to −2,900** [mkt_r10 §13.3] | −1 press motion; feed chute about 0.2 m lower (easier reach) | HLC-300 chute geometry not used | 5 mm slice setting unconfirmed [mkt_r10] | Matches the market-first and domestic rules |

**Appliance control.** Relay or app control is already mostly in place:
- the concave cooker knob is turned by a servo;
- zone 2 is MIoT;
- the stew pot and slicer use smart plugs;
- the rice cooker has an app start.

The only arm "button/knob" actions left are the HLC-300 green key (O12 removes it) and the faucet lever (O5 removes it).

**Fewer grasps and tools.** The swaps that remove a grasp or tool family:
- O2 / O3: the spatula, the keyed wok-carry grasp and the faucet block;
- O4: no far rest;
- O5: the faucet block;
- O7: finger sets P1–P7, the tray and fork grasps, the lever cutter and the peeler cradle;
- O10: the lid rack.

**Already designed but not yet placed:** the pour drum in its rim holder, used for every wok addition, would cut the 55 single-cup pours further. That belongs to the movement-design track; R15 estimated the idle spatula share falls from 36 % to 13 %.

**Bundles (model re-runs, 3 meals)**

| Bundle | Arm time | Meal totals A / B / C | Grasps | Cost |
|---|---|---|---|---|
| Baseline | 69.2 min | 39.5 / 75.6 / 38.6 | ≈296 | — |
| **Cheap engineering bundle** (O4 + O5) | **60.3 min** (−8.9) | 39.5 / 73.1 / 38.6 | ≈248 | **+≈¥90–320** |
| Stirrer, keeping the sink rinse (O2b + O5) | **43.5 min** (−25.7) | 39.5 / 72.9 / 38.6 | ≈234 | +≈¥1.5–4k est. + design |
| User-offload bundle (O1 + O4 + O5 + O6a) | 48.7 min | 38.1 / 72.1 / 35.6 | ≈186 | −≈¥8–20k |
| Stirrer + offload (O1 + O2a + O6a) | 24.0 min | 38.1 / 68.2 / 35.6 | ≈168 | −≈¥5–17k |

The user-offload bundle also removes the uncounted cup staging (≈4–5 min per meal). Uncounted prep (O7) comes on top of every bundle.

---

## 5. Ranking: money saved × motions removed / risk

**Scores**
- **Money:** 0 = adds cost; 1 = ≤ ¥1k saved; 2 = ¥1–5k; 3 = ¥5–15k; 4 = > ¥15k.
- **Motion:** 1 = < 3 min and ≤ 1 family; 2 = 3–10 min or 2 families; 3 = 10–20 min or ≥ 3 families; 4 = > 20 min or ≥ 5 families.
- **Risk:** 1 = low; 2 = medium; 3 = high.
- **Score = (1 + money) × motion / risk.** I used 1 + money so that options which cost a little are not zeroed.

| Rank | Option | Money | Motion | Risk | Score | Who decides |
|---|---|---|---|---|---|---|
| 1 | O6a user sauce cups, no dosing station | 3 | 3 | 1 | **12** | **User** (daily 配料 work) |
| 1 | O7 prep out of the robot loop | 2 | 4 | 1 | **12** | **User** (scope; recurring 净菜 cost) |
| 3 | O1 rice by the user | 2 | 2 | 1 | **6** | **User** |
| 4 | O6b liquids-only station | 2.5 | 1 | 1 | 3.5 | **User** (more kit cups) |
| 5 | O12 卓晋 slicer instead of HLC-300 | 2 | 1 | 1 | 3 | Engineering (5 mm check) |
| 5 | O11 drop the fryer | 2 | 1 | 1 | 3 | **User** (dish change) |
| 7 | O5 faucet sensor add-on | 0 | 2 | 1 | 2 | **User** (faucet decision) |
| 7 | O8 counter cold box | 1 | 2 | 2 | 2 | **User** (fridge decision, food safety) |
| 9 | O3b pot-type 炒菜机 | 0.5 | 3 | 3 | 1.5 (no API: arm presses the panel) | **User** |
| 10 | O2 stirrer + tilt cradle | 0 | 4 | 3 | 1.3 | **User** for (a); engineering prototype for (b) |
| 10 | O3a drum stir-fryer | 0 | 4 | 3 | 1.3 | **User** (锅气) |
| 12 | O4 spatula holster | 0 | 2 | 2 | 1 | Engineering |
| 12 | O9 floor rail | 1 | 1 | 2 | 1 | **User** |

**The formula's limit.** It rewards removing cost, so the biggest **smoothness** lever ranks low: O2, the stirrer, removes 34–48 % of all arm time and the most delicate checked motions (2.0 mm stir reserve, plume rule, 6.47 of 7 N·m wok carry). If smoothness is weighted over money, O2(b) moves to the top of the engineering list.

---

## 6. Top recommendations

1. **Shrink the custom seasoning station: O6b now, O6a if the user accepts daily 配料.**
   - It is the largest custom subsystem: ≈ ¥7–18k in parts plus build labour, and it carries most of R14's unproven assumptions.
   - It also generates ≈20 uncounted cup moves per meal.
2. **Take prep out of the robot loop (O7) and let the user do the rice (O1).**
   - Together they remove ≈ 9 modelled minutes over 3 meals, plus an estimated 10–20 uncounted minutes per meal.
   - They also remove about 9 motion families, the R11 prep set, and the rice hopper module.
   - These are scope decisions only the user can make.
3. **Engineering track with no user burden:**
   - **Cheap pair now:** O4 (spatula holster on the cart) + O5 (faucet sensor add-on): −8.9 min for ≈ ¥90–320.
   - **Prototype-check O2(b)** (stirrer + tilt cradle, wok still rinsed at the sink) as the main smoothness lever: −23 to −26 min, and it retires the hardest checked motions.
   - Re-check the 55 single-cup pours against the already designed pour drum.

**Note for the arm agent:** O2 or O3 removes the food-laden wok carry, which is the binding payload and jaw-moment case. That could relax the gripper and arm requirements.

---

## 7. Questions only the user can decide

1. **Seasoning.** Keep the 19-actuator dosing station? Or go liquids-only (O6b)? Or will you mix sauce cups yourself each day (O6a, ≈10–15 min per meal)?
2. **Prep.** Should washing and cutting leave the robot? Buy 净菜 or prep weekly yourself, and drop the slicer/cutter/peeler set and finger swaps (O7)?
3. **Rice.** Will you load a timer rice cooker yourself (O1)?
4. **Wok.** Is a motorised stirrer and tilt cradle at the wok acceptable instead of the arm stirring?
   - If yes: should the wok still go to the sink for rinsing (O2b, respects your 10-12 decision), or rinse in place with jug water into a waste basin (O2a, saves 10 more minutes)?
   - Would you accept a bought auto stir-fryer with less 锅气 (O3)?
5. **Faucet.** Is a clip-on sensor valve on your existing faucet acceptable (O5)? Your 10-12 decision kept the faucet unchanged.
6. **Fridge.** May cold items wait in an ice-packed cooler on the counter instead of the robot opening the fridge (O8)? This needs a hold-time test.
7. **Fryer.** Drop it and shallow-fry instead (O11)?
8. **Base.** Keep the tethered cart (it can turn your L corner), or consider a floor rail (O9)?

---

## 8. Gaps and honesty notes
- **Prices.** Every price is unconfirmed:
  - 1688 prices are wholesale or teaser prices;
  - R09 values are allowances;
  - no retail JD/Tmall page was read in this round.
- **Not found:**
  - Tineco 食万 current CNY retail (only the [r14]/[r15] figures, and a snippet "食万 3.0 ¥4,990 Tmall" that I could not pin to a page);
  - drum-machine tilt motorisation and maximum temperature;
  - 苏泊尔 C30HS12 specs;
  - fire-suppression CNY prices;
  - Oleoclean CNY price;
  - hinged-lid steamers;
  - 净菜 availability in the user's city.
- **Arm times for options** are the project's own scheduler with my changed action times (scratch copy). None of the new motions (holster, cradle, jug pour, sensor faucet) is collision checked.
- **"Uncounted" prep, staging and fridge times** are order-of-magnitude estimates from the R11/R14 rates.
- **Stir-quality and 锅气 statements** for machines come from [r15] (J7 teardown, maker temperatures). Nothing here was tested.

**Main web sources this round**
- 1688 market pages, read 2026-10-13:
  - 滚筒炒菜机: https://www.1688.com/market/-B9F6CDB2B3B4B2CBBBFA.html
  - 全自动炒菜机家用: https://www.1688.com/market/-C8ABD7D4B6AFB3B4B2CBBBFABCD2D3C3.html
  - 自动翻炒锅: https://www.1688.com/market/-D7D4B6AFB7ADB3B4B9F8.html
  - 卡默尔蠕动泵: https://www.1688.com/market/-BFA8C4ACB6FBC8E4B6AFB1C3.html
  - 感应水龙头节水器: https://www.1688.com/market/-B8D0D3A6CBAEC1FACDB7BDDACBAEC6F7.html
  - 米家电磁炉: https://www.1688.com/market/-C3D7BCD2B5E7B4C5C2AF.html
  - 隔水电炖锅: https://www.1688.com/market/-B8F4CBAEB5E7ECC0B9F8.html
  - 智能电饭煲: https://www.1688.com/market/-D6C7C4DCB5E7B7B9ECD2.html
  - 红外热成像模组: https://www.1688.com/market/-BAECCDE2C8C8B3C9CFF1C4A3D7E9.html
  - 直线模组: https://www.1688.com/market/-D6B1CFDFC4A3D7E9.html
  - 机器人地轨: https://www.1688.com/market/-BBFAC6F7C8CBB5D8B9EC.html
- smzdm cooking-robot summary (2025-01-04): https://post.smzdm.com/p/adolgvgn/
- 36kr on 添可/方太 home cooking robots (2026-03-28): https://www.36kr.com/p/3742006515642885
- Oleoclean EU prices (search snippets): https://galaxus.it/en/s2/product/tefal-fr8040-oleoclean-pro-oil-fryer-deep-fryer-fryers-3228862
- Drum-machine specs: search snippets of reseller mirror pages, low quality, e.g. https://www.notredame-high.co.uk/products/222952305/commercial-food-processor-6l-automatic-cooking-machine-multi/
- Project files: `DECISIONS.md`, `sim/r10/claude/README_R10.md`, `meal16.py`, `r17seq.py`, `results/r16/meal_stew_r18.json`, `results/r18/arm18.json`, `results/r16/arm_checked.json`, `timeline14.py`, `research/market_r10.md`, `r14_storage_market.md`, `r15_cooking_market.md`, `homestyle_meals.md`, `sim/r09/integrator/results/costs.csv`.
