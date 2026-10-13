# R19 prep methods for the 16 no-method operations (2026-10-13)

**Issue:** #33 "[process] 16 prep operations have no robot method (peeling, florets, scoring, husking)".

**Rules applied**
- DECISIONS 10-09: the appliance does the precise work and the arm loads, unloads and pulls levers; domestic market first; multi-function bases over single-purpose machines; 3D printing for jigs and fixtures.
- DECISIONS 10-13: prep is the robot's job; ingredients arrive as the reference cook buys them (`research/r19_asbought.md`).
- Robot: one UR5e-class arm, DH PGC-140-50 (50 mm stroke, 40–140 N per jaw, 7 N·m), swappable printed finger sets P1–P4, a camera, the sink with the arm-opened faucet. The arm pushes about 100 N on a keyed pusher (R11).

**Labels**
- **[C]**: an e-commerce or search-result snippet, not verified on a product page. All 1688 prices are wholesale list prices read on 2026-10-13 from 1688 market pages (`https://www.1688.com/market/-<GBK hex>.html`); retail is usually higher (market_r10 13.6). The 1688 offer pages need JS and could not be read, so **sizes, power and weights are mostly ND**.
- **[O]**: another web source (patent, article, maker page), read directly or as a search snippet where stated.
- **[concept]**: my design idea (3D-printed parts plus a bought blade). Not simulated, not benched.
- **[est]**: my estimate, with its basis.
- **ND**: not found. Nothing is invented.

Nothing was bought, and no seller was contacted. Taobao and JD product pages were not opened (no browser automation); WebSearch and WebFetch only.

---

## 1. Summary

1. **The list (16 instances, 11 operations).** It comes from `R19_RELIABILITY.md` §2.3:
   - A: luffa peeling, broccoli florets, garlic peeling, ginger peeling;
   - B: bamboo husking, fish back-split, tomato peeling, fine 葱丝, okra trim and halve, garlic, ginger, dried-chili snipping;
   - C: squid opening and scoring, garlic, ginger, dried-chili snipping.

   The issue body leaves out **fine 葱丝 (B)**. Without it the count is 15. It is covered here in §3.11.
2. **A bought product does the precise work for only 4 operations.** They are ginger, garlic, dried chili and 葱丝, and they remove 9 of the 16 user steps:
   - **Ginger:** the 85 W abrasive peeler already in the design. Add the knob to the potato or taro batch.
   - **Garlic:** a household tumbling garlic peeler, ¥25–122 [C]. Add a printed head-crack plate and a fan chute that blows the skins off [concept].
   - **Dried chili:** the AY-403's own 13 mm grid plate, which is already in the D1 set. Better still, batch-cut the chili weekly into the chili portioner at the wok.
   - **葱丝:** a ¥2 葱丝刀 sleeve blade [C] in a printed holder; the arm pushes the scallion through it.
3. **Luffa and tomato can use a cheap rotary electric peeler** (Rotato class, ¥31–37 on 1688 [C]). A Starfrit listing names tomatoes [C]. Whether it works on tender luffa and ripe tomato is **unproven**. Tomato peeling after scalding has no robot-grade method otherwise.
4. **Five operations have no fitting product,** and each gets a printed jig concept:
   - **Okra:** a comb press that trims the caps and halves 10 pods in one press.
   - **Squid:** a scoring die on the lever base whose blades stand out only to the scoring depth.
   - **Broccoli:** a coring tube pushed down along the stem.
   - **Bamboo shoot:** halve it lengthwise on a long-blade 铡刀, then push the flesh out of the husk shells.
   - **Sea bass:** a sled pushed past a fixed blade.

   In China, every machine for these jobs is canteen or factory equipment at ¥1,000–368,000 [C]. A 1688 search for broccoli and okra machines found none.
5. **Ranking** (§4).
   - The easy, product-based four (ginger, garlic, chili, 葱丝) remove **2 / 4 / 3** of the **4 / 8 / 4** steps in A / B / C.
   - The hardest are the fish back-split, bamboo husking and tomato peel-off. They are concepts with low confidence, and the stall-purchase alternatives are a user decision.
6. **Recommended set** (§5).
   - New spend is about **¥0.3–0.9k** [C/est]: two small devices, a long-blade lever cutter, blade strips, a 葱丝刀 and printed parts. Nothing new stands on the counter.
   - **Rule fit.** Most work reuses the AY-403 base, the abrasive peeler and the soak tub. The garlic peeler and the rotary peeler are cheap, stored and close to single-purpose; flagged for the user.
   - **Safety.** In Singapore, "Kitchen machines" are a Medium-risk SAFETY Mark controlled good [O]. That bears on the mains-powered peelers (#24). Manual tools and printed jigs are not electrical goods.
7. **Everything needs bench proof (#10).** No product here has published data on this cook's items, and every jig is unbuilt. The bench list is in §6.

---

## 2. The exact list and target shapes (from `r19_asbought.md`)

| # | Operation | Meals | What arrives | Target, as he does it | Mass / count [est, audit] |
|---|---|---|---|---|---|
| 1 | Garlic: break the head, peel the cloves | A, B, C | heads plus loose unpeeled cloves | A: fine mince (luffa sauce); B: fine mince (白灼汁); C: slices (squid) and coarse chop (peas, 土豆丝). Mincing is the chopper's job (audit §5.2); **peeling** is the gap | A ~50 g with chili; B ~30 g; C part of 50 g |
| 2 | Ginger: peel the knob | A, B, C | whole knob | A: 4 thick slabs ~1×6 cm + slices; B: slices + fine shreds (三丝); C: rounds and slices | 30–50 g per meal |
| 3 | Luffa: peel, then quarter and segment | A | whole, unpeeled, flower on | end trimmed, lengthwise quarters, ~5 cm segments, stood upright in a row | 2 luffas, ~500 g |
| 4 | Broccoli: florets + stem peel | A | whole head with leaves | small florets (he re-cuts the big ones), salt soak; stem peeled, thick slices | 400 g |
| 5 | Bamboo shoot: husk | B | one shoot in its husk | slit, husk off, tough parts trimmed, halved, thick slices 5–8 mm, washed | ~400 g (audit; 1 shoot seen) |
| 6 | Sea bass: back-split | B | whole, gutted (scaling uncertain) | split along the back, cleaver along the spine; head pressed so it stands; ginger and scallion tucked in | ~600 g, 336–367 mm long, 93–100 mm high (catalog FI3) |
| 7 | Tomato: peel after scalding | B | 4 whole | boiling water poured over them in a bowl, cross-cut, peeled by hand, chunks/wedges | 4 tomatoes |
| 8 | Fine 葱丝 | B | whole scallion bunch | green segments stacked with ginger and carrot slices, pressed, fine shreds, soaked | part of 40 g 三丝 |
| 9 | Okra: trim caps, halve lengthwise | B | whole with caps | washed in rice water, caps trimmed, halved lengthwise | ~150 g, 15–20 pods |
| 10 | Dried chili: snip into segments | B, C | whole dried | segments (length not measured in the frames) | a few per dish |
| 11 | Squid: open the tube, score both ways, cut | C | 2 cleaned tubes | slit open; diagonal scoring, not through; turned and scored the other way; cut into pieces; scalded to curl | ~400 g |

User steps per meal today: A 4 (#3, 4, 1, 2), B 8 (#5, 6, 7, 8, 9, 1, 2, 10), C 4 (#11, 1, 2, 10).

---

## 3. Methods per operation

Common to all:
- **Lever base:** the AY-403 lever cutter (2.35 kg, side-slot plates, window about 10×10 cm unconfirmed; market_r10 13.2 M1).
- **Long-blade lever:** a 小型杠杆铡刀 (¥44–250 [C]; one model has a 36 cm blade and a 38.6×20×6 cm body; market_r10 §7 L1).
- **Other existing pieces:** the soak tub with basket (audit §5.6), the kettle, the R13 basket, the far-left work spot (−1.62, 0.155) and the plate dock (market_r10 13.5).
- **Blade strips:** AY450 strips, 10 for ¥30 [C].
- **Printed parts:** PP where food touches, PETG elsewhere (DECISIONS 10-09).

### 3.1 Garlic: break the head, peel the cloves (A, B, C)

| Candidate | Price, source (2026-10-13) | Size / power | Arm load and unload | Cleaning | Verdict |
|---|---|---|---|---|---|
| **G1 Household tumbling peeler (silicone friction; recommended)** | "电动硅胶剥蒜器剥蒜机家用快速大蒜去皮蒜蓉机剥蒜蒜泥" **¥122.18** (1688 offer 1089173831013; the same at ¥122.18–122.40 from 3 more sellers). USB "番茄葡萄去皮机…大蒜头剥皮机" **¥24.7** (973204315693), ¥27 (1088013001225) [C] | 1688: ND. Overseas listings of the class: 50 W, 1,300 rpm, 0.8 kg, 203×203×230 mm [C, snippet, page gone]; another 3.7 V battery, ~20 s per batch, 9.8×7.8×8.6 in, 2.2 lb, detachable dishwasher-safe parts [C, snippet] | Pour the cloves from the basket into the bowl; lid on by a printed keyed knob; start by a button press (button type ND) or by smart plug on a mains model; tip out into the winnowing chute [concept] | Bowl rinse or dishwasher [C] | Best fit. One blog: **5–10 cloves per batch, 10–20 s, dry cloves only, small cloves may be crushed** [O, anecdotal]. So a meal needs 2–3 batches [est] |
| G2 Commercial friction peeler | ¥500–1,399.93 (1688 offers 1068476885548, 944460794850, 924266938331, 1092245364853, 1088430512948) [C] | ND. A US commercial 8 lb peeler: 190 W, 13.4×13.75×21.4 in, 45 lb shipping [O, Omcan 13442] | — | — | Too big and heavy for storage; not recommended |
| G3 Air type (气脱) | ¥998 (642999207532) [C] | Needs a **2.2 kW** compressor (rotary type) or **5.5–7.5 kW at 380 V** (full auto) [O, Baidu Baike snippet] | — | — | **Rejected:** compressor, noise, power |
| G4 Chopper with a peeling function | A search summary named Joyoung JYS-A960 (2.2 L, 350 W) "with garlic peeling"; the JD page shows only an S25-LA960 with no peeling | ND | — | — | Not confirmed; ND |

Supporting [concept] parts:
- **Head-crack plate.** A printed flat pusher with a cup, used on the AY-403 with no blade, presses a head about 10–15 mm so that the cloves separate.
  - Garlic compression failure is about 40 N (catalog G1), well under the arm's ~100 N.
  - The arm then tips the cloves into the basket.
- **Winnowing chute.** A printed chute with a 5 V fan (¥10–30 [est]). Cloves fall into a cup and the light skins blow into the waste bin.
  - Without it, the skins stay mixed with the cloves in the bowl; the blog shows people pick the cloves out by hand.

**Bench (#10):**
- peel rate per batch on the cook's garlic (fresh and stored);
- crushed cloves;
- how well the fan separates the skins;
- cloves left joined after the crack;
- cloves per batch.

### 3.2 Ginger: peel the knob (A, B, C)

| Candidate | Price, source | Size / power | Arm load and unload | Cleaning | Verdict |
|---|---|---|---|---|---|
| **J1 The existing 85 W abrasive peeler (傲宏 class; recommended)** | ¥148–155 (1688, market_r10 13.3), **already in the D1 set** | 85 W; 2.5 kg shipping; 25.5×27×27 cm class (Melissa) [C] | **A and C:** the knob goes into the same batch as the potatoes or taro (no extra cycle). **B:** one batch with the knob alone (one extra peeler cycle, 70–100 s arm + 1–3 min unattended, audit unit times) | Rinse; the Gastronoma-class body is not dishwasher-safe (market_r10 §4) | Best fit; evidence is partial (below) |
| J2 Commercial brush (毛刷/毛辊) peelers | ¥500–11,800 (1688 生姜去皮机 page: 1065202616427 ¥500, 1065993748580 ¥1,100, 983265036617 ¥7,800, 1060230455965 ¥11,800) [C]. A "household" listing at ¥95 (621542961761): type ND | ND; canteen class | — | — | Rejected (size, water hookup) |

**Evidence for abrasion on ginger.** A hand-operated abrasive drum ginger peeler reached **74–81 % peeled** in 5 kg batches over 8–12 min, with 2.5–3.8 % loss [C, ICAR J. Agric. Eng. abstract snippet]. Expect skin left in the crevices between branches.

The alternative is unpeeled ginger slices. That is a user decision, because he peels.

**Bench:**
- residual skin and loss on a 30–50 g knob after 1–3 min, alone and mixed with potatoes;
- small branches breaking off.

### 3.3 Luffa: peel (A); quarter and segment

| Candidate | Price, source | Size / power | Arm load and unload | Cleaning | Verdict |
|---|---|---|---|---|---|
| **L1 Household rotary electric peeler (Rotato class)** | "多功能自动电动削皮机 土豆 苹果" ¥31.35 (597044512563), ¥37 (876720388688), ¥36 (1082918884719) [C]. Starfrit Rotato Express 2.0 (overseas reference) | Starfrit: 5.5×5.5 in footprint, just under 1 ft tall, 1.9 lb; 6 V adapter **or 4×AA**; it names tomatoes among its foods [C, snippets]. Food-length limit: R06 recorded ≤140 mm from the OEM manual (not re-verified) | 1. Cut the luffa into 2–4 pieces of ≤10 cm on the lever (single-blade plate). 2. Push each piece down onto the base prongs. 3. Lower the top arm (printed lever extension). 4. Press the button (momentary). 5. Lift the arm and pull the piece off. 4–6 cycles per meal [est] | Wipe the blade arm; rinse the prongs | **Candidate; unproven.** Tender flesh may tear on the prongs ("这条丝瓜真够嫩"). Skin thickness ND |
| L2 Commercial luffa / stem peelers | 商用莴笋黄瓜削皮机 ¥1,000 (1027049286623); 赫德丝瓜削皮机 ¥3,000 (751095811877); 全自动丝瓜刮皮机 ¥6,800 (952192395890); 毛刷 丝瓜脱皮 ¥9,800 (803122231694) [C] | ND | — | — | Rejected: canteen size, permanent counter |
| L3 **[concept]** Cradle with indexed rotation + an arm-held swivel peeler | printed parts + a bought Y-peeler with a keyed handle (¥5–10 class [C, 1688 瓜刨 ¥3.5–5.5]) | ~40×12×10 cm [est] | The luffa lies between printed centres. The arm draws the peeler along the length under force control, and the luffa turns about 30° between strokes (the arm turns a printed knob). 10–14 strokes per luffa [est] | Rinse; dishwasher | Fallback if L1 tears the flesh. Force proxy: lotus skin peeling 9–13 N (catalog L1) |

**Quarter and segment** [designed by analogy]:
- Lever base with the R11 section plate set to 50 mm for the cross-cuts.
- A printed "+" plate (2 AY450 strips) quarters each 5 cm segment standing on end.
- Standing the segments upright on the plate remains the separate PLACE gap.

**Bench:**
- L1 on tender luffa: tearing, peel depth;
- L3 force and strokes;
- "+" quartering without crushing.

### 3.4 Broccoli: florets + stem peel (A)

**Market:**
- 1688 searches for "西兰花切花机" and "西兰花切朵机" found **no floret machine**; the only listings were a freezing line and a grater [C].
- Industrial floretters exist, e.g. Floreto, 70 heads/min, 550 kg [O, hortidaily snippet]. A 2022 study says simple, inexpensive floretting machines are "in short supply" [O, Jadwisieńczak & Kaliniewicz snippet].
- One household hand tool: Lee Valley 75617 "cauliflower and broccoli prep tool", a curved paddle blade that follows the stem [O, snippet; price ND; overseas].

| Candidate | Price | Size | Arm motion | Cleaning | Verdict |
|---|---|---|---|---|---|
| **B1 [concept] Coring tube, pushed by the arm** | rolled stainless strip (a cut AY450 strip, ¥3 [C]) in a printed holder + a printed crown-down cradle, PP ~0.3 kg ≈ ¥30–40 [est] | cradle Ø ~180 mm (curds 120–170 mm, catalog BR1); tube Ø ~45 mm (stems ≤42 mm, BR2) | 1. Put the head crown-down in the cradle. 2. Seat the tube over the stem. 3. Push down 60–80 mm [est] with a keyed handle (≤100 N): this cuts the branch stalks where they join the main stem. 4. Lift the stem out inside the tube; the florets stay in the cradle. 5. Large florets go onto a printed 30 mm parallel-blade plate on the AY-403 (1–3 presses) | Dishwasher (PP) | Concept. Cutting force ND (BR3 gives only petiole compression and bending) |
| B2 Stem | the abrasive peeler (with the potatoes), then the 卓晋 slicer chute (10×7 cm) for thick slices | existing | as for potato | — | Reuse |

**Bench:**
- coring force;
- floret size spread;
- crown damage;
- how many florets stay on the stem.

### 3.5 Bamboo shoot: husk (B)

**Market (1688 剥笋机 / 竹笋剥壳机)** [C]:
- needle and drill-attachment tools for slender shoots: ¥2.2–22 (905427171325, 1014816930330);
- a handheld electric shoot and taro scraper: ¥140 (730895449176);
- a hand-crank peeler: ¥418.22 (1090590596666; the listing gives ≤3.5 cm);
- automatic machines: ¥1,900–3,938.66;
- lines: ¥38,000–368,000.

They are made for slender 小竹笋 / 青皮笋. Whether any fits a thick 鲜笋 is ND. A patent for a small peeler uses rotating forks that strip the layers one at a time [O, CN107549830A].

**Technique sources:**
- Halving the shoot lengthwise lets the husk come off easily [O, zhihu snippet].
- A deep lengthwise slit through several layers also works [O].

| Candidate | Price | Size | Arm motion | Cleaning | Verdict |
|---|---|---|---|---|---|
| **S1 [concept] 铡刀 + V-cradle + husk push-out** | 铡刀 ¥44–250 [C] + printed cradle and push-out fork ≈ ¥30–50 [est] | 铡刀 body 38.6×20×6 cm, 36 cm blade (one model [C]) | 1. Shoot in the printed V-cradle: cut the tip and the dirty base off (2 strokes; cutting the base node frees the sheath layers [est]). 2. Halve lengthwise through husk and flesh (1 stroke; he halves anyway). 3. Each half cut-face down: P2/P3 fingers hold the husk shell at its edges while a printed pusher pushes the flesh out along the axis. 4. Thick slices: 卓晋 chute or 铡刀 strokes. 5. Wash in the basket | Rinse the blade; the cradle in the dishwasher | Concept; **step 3 is unproven** |
| S2 Thin-shoot tools | ¥2.2–418 [C] | — | — | — | Fit for a thick shoot ND; not recommended |

**Bench:**
- whether a halved, base-trimmed shoot releases its flesh to an axial push, and the force;
- waste;
- the 铡刀 force on the husk.

### 3.6 Sea bass: back-split (B)

**Market:** 1688 鱼开背机 / 杀鱼开背机, ¥500–35,000 (615 results; e.g. 1084195111480 ¥4,560, 1092609304458 ¥12,800, 1084215050756 ¥35,000; mostly freshwater fish; sizes ND) [C].

**Rejected:** canteen machines and single-purpose. The stall's 开背 is closed by the user's 10-13 rule.

**Technique** [O, recipe search snippets]: cut along the back close to the bone without cutting through; some cooks also cut the spine inside the belly so the fish lies flat while steaming.

| Candidate | Price | Size | Arm motion | Cleaning | Verdict |
|---|---|---|---|---|---|
| **F1 [concept] Split sled past a fixed blade** | printed PP sled + rail ≈ ¥60–100 [est]; a bought stainless slicing blade ¥2–6 (1688 鱼刀 listings [C]) | sled ~400×120×110 mm; rail ~750 mm with the 350 mm stroke [est] | 1. Lay the fish belly-down in the sled's V; two printed side clamps hold it (mucus μ ≈ 0.12, catalog FI1, so no friction grip). 2. The arm pushes the sled head-to-tail past a vertical blade beside the dorsal line. 3. The blade height stops the cut above the belly, so the halves stay joined. 4. The arm presses the head down with a flat pad so the fish stands. 5. Carry the sled to the plate and tip it | Sled in the dishwasher; the blade rinsed; blade guard on in storage | Concept; lowest confidence: fish size and spine depth vary |
| F2 [concept] Arm-held knife (keyed handle), force-controlled along a dorsal line found by the camera, fish in the F1 sled | knife ¥2–6 [C] + keyed handle | — | one force-controlled stroke along a camera path | as F1 | More motion risk; an exposed blade in the arm |

**Safety:** a fixed open blade is a home-tier hazard (DECISIONS 10-07). It needs a guard over the blade while stored and the robot paused whenever a person is near.

**Bench:**
- push force;
- the cut path relative to the spine for 500–700 g fish;
- halves staying joined;
- the fish standing upright;
- scales, if the stall did not scale it.

### 3.7 Squid: open the tube, score both ways, cut pieces (C)

**Market:**
- 1688 鱿鱼切花机 / 鱿鱼花刀机: ¥3,800–98,000, about 1,029 results [C]. These include "多功能斜切花刀设备麦穗腰花机" ¥6,666 (944614325784, a diagonal 麦穗 cutter) and 同普 units at ¥19,800.
- A ¥288 listing (1027692518137) is probably a part or deposit price (ND).
- One belt unit: 1.5 kW, 450 mm belt, depth 2–20 mm [C, nongjx snippet].
- Principle (patent CN209498409U) [O]: a roller of parallel blades over a slotted bed; a height handle sets the depth; the squid is turned 90° for the second pass.
- 1688 "花刀器" listings are wave cutters and melon ballers with **no depth control**.

| Candidate | Price | Size | Arm motion | Cleaning | Verdict |
|---|---|---|---|---|---|
| **Q1 [concept] Scoring die on the AY-403, blades raised only to the scoring depth** | 2 printed PP plates + ~20 AY450 strips (2 packs, ¥60 [C]) ≈ ¥90–110 | each plate ~125×125×12 mm, sized like the AY-403's own plates (market_r10 13.5 #11) | 1. **Open:** lay the tube flat; one 铡刀 stroke trims a folded edge, and it opens into a sheet. 2. **Pieces:** a full-depth parallel-blade plate, about 40 mm pitch [est], two presses with the sheet turned 90° (piece size not measured from the video). 3. **Score:** each piece on the die (blades stand only h above the plate, in a ±45° crosshatch, 4–5 mm pitch); the pusher with a silicone face presses once; a printed stripper lifts the piece off. 4. Tip into the scald basket. About 10–16 presses for 400 g [est] | Plates in the dishwasher; the strips are bolted (not glued, market_r10 13.6) | Concept. Two changes from his method: **pieces before scoring**, and **vertical cuts** (crosshatch rather than slanted 麦穗) |
| Q1′ | as Q1, with the strips tilted about 45° in one direction | — | same | — | Closer to 麦穗 [concept] |
| Q2 [concept] Arm-rolled multi-wheel scorer | printed axle + stacked Ø ~40 mm circular blades with spacers + two larger end wheels that set the depth; blades ND (pizza-wheel class) | ~120 mm wide [est] | 2 rolling passes at ±45° on a non-slip silicone mat | Dishwasher if the blades allow | Fallback; more motion, less fixture |

**Depth h:** mantle thickness ND, so set h ≈ 50–60 % of a measured thickness [est].

**Bench:**
- die penetration force against the arm's ~100 N through the lever (AY-403 ratio ND);
- depth uniformity;
- squid sticking in the blades;
- curl after the scald;
- the user's view of crosshatch versus 麦穗.

### 3.8 Tomato: peel after scalding (B)

**Market:**
- Commercial steam peelers: ¥6,900 (1042683049595) to ¥271,700 (1090976269038) [C]. Rejected.
- 1688 household "去皮机" listings (¥24.7–49.9) are for grapes, cherry tomatoes and garlic. Full-size tomatoes: ND.

**Method:** blanch 20–30 s, up to 60 s for large tomatoes, after an X-score; then cold water; peel from the X [O, cooking guidance snippet].

| Candidate | Price | Arm motion | Verdict |
|---|---|---|---|
| **T1 Rotary electric peeler (the L1 device), raw tomato, no scald** | shared with luffa: ¥31–37 [C] | stem-scar down onto the prongs → arm down → button → off. 4 cycles | The Starfrit listing names tomatoes [C]. Juice loss and tearing on a ripe tomato ND. **Gives the peeler two uses** |
| T2 Scald + peel-off [concept] | X-score: a printed plate on the AY-403 with 2 strips raised ~2 mm [est]. Scald: the basket in the soak tub with kettle water (existing; he pours) | press each tomato onto the X plate → basket in the tub, kettle pour, 20–60 s → cold rinse at the tap → pinch the X flaps with fingertip pads, guided by the camera (4 flaps × 4 tomatoes) | Peel-off is the weak link; low reliability [est] |
| T3 Skip the peeling | — | — | User decision. R16 had dropped peeling; the 10-13 rule reopened it |

Chunks then use the existing 8-wedge plate.

**Bench:**
- T1 on ripe tomatoes;
- for T2, flap pick success after 20 / 40 / 60 s.

### 3.9 Okra: trim caps, halve lengthwise (B)

**Market:**
- 1688 "秋葵切头机": **0 results** [C].
- Bean (四季豆) trimmers: ¥2,850–30,000 commercial lines (e.g. 916191577631 ¥2,850, 900242253891 ¥4,750) [C]. Rejected.

| Candidate | Price | Size | Arm motion | Cleaning | Verdict |
|---|---|---|---|---|---|
| **K1 [concept] Okra comb press** | printed PP tray (10 V-slots, 25 mm pitch, 120 mm long, an end stop for the caps) + hinged printed lid holding 10 lengthwise strips over the slots and 1 cross strip at the stop line (11 AY450 strips ≈ ¥33 [C]) + PP ≈ ¥40 [est] | ~280×150×60 mm [est] | 1. Pick each pod from the basket by camera (P1 fingers; okra Ø ~15–20 mm [est]) into a slot, cap against the stop: 15–20 picks. 2. Press the lid down by a keyed knob: one press trims all caps and halves all pods; repeat for the second tray load. 3. Lift the lid (printed stripper tines between the blades). 4. Tip the halves into a bowl and the caps into the waste | Dishwasher | Concept. The 15–20 picks are the cost: about 6–10 s each by the audit's piece-placement time, so 2–3 min [est] |

**Bench:**
- placement success;
- press force (okra cutting force ND);
- halves stuck between the blades;
- cap trim position.

### 3.10 Dried chili: snip into segments (B, C)

**Market:**
- 1688 干辣椒切段机: ¥1,000–7,250.82, 181 results, roller-knife 300/500 types; sizes ND [C]. Rejected for size. An overseas snippet mentions a 550 W unit, 21×30×32 cm [C].
- Five-layer kitchen scissors (五层葱花剪): ¥4.6–9.5 [C]. A poor fit for one arm, which would have to both feed and squeeze.

| Candidate | Price | Arm motion | Verdict |
|---|---|---|---|
| **C1 The AY-403's own 13 mm grid plate (a bought product, in the ¥209–305 set)** | ¥0 if the grid set is bought | pour the dish's chilies from a cup onto the plate → 1 press → pieces fall into a cup | Pieces ≤13 mm. Chilies in random orientation are partly split lengthwise; dried chili is brittle, so expect fines |
| C1′ [concept] Printed 15 mm parallel-blade plate | the market_r10 13.5 #11c "劈梗板" geometry, ¥18 of strips | the arm lays 5–6 chilies across the blades, then 1 press | Cleaner segments; more placement moves |
| **C2 Weekly batch** | — | cut a jar of segments with C1 once a week and load the chili portioner at the wok (DECISIONS 10-13) | Removes the per-meal step entirely. How long cut chili keeps in the portioner: ND |

**Bench:**
- shatter and fines;
- seeds;
- light chilies bouncing under the pusher;
- capsaicin dust.

### 3.11 Fine 葱丝 (B; in the 16 count, missing from the issue body)

**Market:**
- Handheld 葱丝刀: ¥1.4–1.65 (742226558985, 1045310281390) [C].
- Patent CN203579692U [O]: a sleeve with a "+" blade in the middle and straight blades around the inside. Push a scallion through and it splits into strips; the fineness is set by the blade count.
- Commercial 葱丝机: ¥1,603.6 (728717864511), ¥2,880 (784376188309), up to ¥9,500 [C]. Rejected for size.

| Candidate | Price | Arm motion | Verdict |
|---|---|---|---|
| **N1 Sleeve 葱丝刀 in a printed holder** | ¥2 + PP holder ≈ ¥10 [est] | the arm pushes 6–8 cm scallion sections (P1 bunch pinch) through the fixed sleeve; the shreds fall into the soak bowl. ~5–8 pushes | A product does the cut. Whether it reaches 1–2 mm on soft greens is ND |

The ginger and carrot parts of 三丝 stay on the 4 mm shred disc. That is coarser than his, as the audit noted.

**Bench:**
- shred width;
- jamming in the sleeve;
- greens versus whites.

---

## 4. Ranking

**Difficulty:** 1 = a bought product with a simple load; 5 = an unproven knife-craft jig.

User steps removed are counted against A / B / C as they stand today (4 / 8 / 4).

| Rank | Operation | Meals | Steps removed (A/B/C) | Difficulty | Method basis | Extra arm work per meal [est] |
|---|---|---|---|---|---|---|
| 1 | Ginger peel | A, B, C | 1 / 1 / 1 | 1 | existing abrasive peeler | A, C: none (same batch); B: one peeler cycle |
| 2 | Dried chili | B, C | 0 / 1 / 1 | 1 | existing AY-403 grid, or a weekly batch | 1 pour + 1 press, or none with C2 |
| 3 | Garlic peel | A, B, C | 1 / 1 / 1 | 2 | bought peeler + printed crack plate and fan chute | 1 crack press + 2–3 peel batches |
| 4 | Fine 葱丝 | B | 0 / 1 / 0 | 2 | bought sleeve + printed holder | 5–8 pushes |
| 5 | Luffa peel (+ quarter) | A | 1 / 0 / 0 | 3 | bought rotary peeler, or an L3 jig | 4–6 peeler cycles + ~10 presses |
| 6 | Okra trim + halve | B | 0 / 1 / 0 | 3 | printed comb press | 15–20 picks + 2 presses |
| 7 | Squid open + score + cut | C | 0 / 0 / 1 | 3 | printed scoring die on the AY-403 | ~10–16 presses + 1 铡刀 stroke |
| 8 | Broccoli florets | A | 1 / 0 / 0 | 3 | printed coring tube | 1 coring push + 1–3 presses + a stem peel |
| 9 | Tomato peel | B | 0 / 1 / 0 | 4 | rotary peeler (unproven), or a weak peel-off | 4 cycles, or 16 flap pinches |
| 10 | Bamboo husk | B | 0 / 1 / 0 | 4 | 铡刀 + push-out concept | 3 strokes + 2 push-outs |
| 11 | Fish back-split | B | 0 / 1 / 0 | 5 | sled + fixed blade concept | 1 sled push + clamp and press |

**What each tier leaves** (steps left in A / B / C):
- **Ranks 1–4** (products only): 2 / 4 / 1 left. Luffa and broccoli in A; bamboo, fish, tomato and okra in B; squid in C.
- **Ranks 1–8** (with the medium printed jigs): 0 / 3 / 0 left (B: tomato, bamboo, fish).
- **All 11:** 0 / 0 / 0, if every bench test passes.

**Costs to keep in mind**
- Each new method adds failure-prone events: picks, presses, peeler cycles.
- Under `R19_RELIABILITY.md`, the jig operations add process-outcome events at about the 1 % mid rate until benched.
- The okra picks and the squid presses are the largest additions.

---

## 5. Recommended set

### 5.1 What to add (nothing counter-resident)

| Item | For | Price [C/est] | Stored size | Uses | Power |
|---|---|---|---|---|---|
| Household tumbling garlic peeler (G1) | garlic | ¥25–122 | ~20×20×23 cm, ~0.8 kg [C] | 1 in this menu | USB battery or mains (ND per model) |
| Printed head-crack plate + winnowing chute + 5 V fan | garlic | ¥10–30 fan + PP | plate in the plate dock; chute ~15×10×20 cm [est] | 1 | 5 V |
| Rotary electric peeler (L1 / T1) | luffa, tomato | ¥31–37 | ~14×14×30 cm, ~0.9 kg [C, Starfrit class] | 2 | 4×AA or adapter |
| 小型杠杆铡刀 (long-blade lever) | bamboo, squid opening, luffa and other trims | ¥44–250 | body 38.6×20×6 cm (one model); weight must be ≤3.5 kg to be stored (ND) | 3+ | none |
| AY450 blade strips, 3–4 packs | squid die and piece plate, okra press, "+" plate, X plate, coring tube, chili plate | ¥90–120 | — | many | — |
| 葱丝刀 sleeve ×2 + holder | 葱丝 | ¥3 + PP | small | 1 | none |
| Fixed blade for the fish sled | fish | ¥2–6 | in the sled | 1 | none |
| Printed parts: squid die + piece plate, okra press, coring tube and cradle, "+" and X plates, bamboo cradle and push-out fork, fish sled + rail, crack plate, holders | — | PP/PETG ~1–2 kg ≈ ¥100–260 (rates from market_r10 13.5) | okra press ~28×15×6 cm; fish sled ~40×12×11 cm + rail ~75 cm [est]; plates in the dock | — | — |
| **Total new** | | **≈ ¥0.3–0.9k** | | | |

**Reused, no new spend:**
- the AY-403 base with its 13 mm grid and 8-wedge plates;
- the 85 W abrasive peeler (ginger, broccoli stem);
- the soak tub, the basket and the kettle (scalds);
- the 卓晋 slicer (bamboo and broccoli-stem slices).

The D1 set itself costs ¥1.7–2.4k (market_r10 13.3), and the audit's §5 additions ¥0.7–1.5k.

### 5.2 Counter and storage space
- **Counter:** nothing new stays on the counter.
- **Work spots:**
  - The screened far-left front spot (−1.62, 0.155) passed only for a **0.22×0.26 m** envelope (audit §4.3).
  - Too long for that envelope [est]: the 铡刀 at ~0.39 m long, the fish sled with its ~0.75 m rail, and the okra press at ~0.28 m.
  - Each needs a new spot screen (`r19prep_screen.py`, `r19prep_spotreplay.py`) before it is adopted. The fish rail may need the user's L-shaped sink leg.
- **Storage:** about one extra drawer layer for the two small devices, the 铡刀 (blade locked) and the okra press. The fish sled is the bulkiest printed part [est].

### 5.3 The "multi-function base" rule
- **Keeps the rule:**
  - the AY-403 gains the chili, squid, X-score, "+" and crack plates, and it already holds the tomato, greens and dice plates;
  - the abrasive peeler gains ginger and the broccoli stem;
  - the 铡刀 is a second lever base used by at least 3 operations.
- **Bends the rule (user's call):**
  - **The garlic peeler** does one job in this menu. It is small (¥25–122, stored), and no confirmed multi-function alternative was found (G4 not confirmed).
  - **The rotary peeler** covers luffa and possibly tomato.
  - **The fish sled** is a single-purpose jig, but a printed fixture, not a machine.

### 5.4 Singapore SAFETY Mark (issue #24)
- **"Kitchen machines,** including mixers, blenders and mincers … for household use to prepare food or beverages, rated voltage ≤250 VAC" are a **Medium-risk controlled good** [O, CPSO list].
- **"AC Adaptors"** are also controlled.
- **What is affected:**
  - a mains garlic peeler, and the 85 W abrasive peeler already in the design, probably fall under kitchen machines (the definition says "including", so it is not limited to the three named);
  - the adapter of a USB or 6 V device is controlled.
- **What is not:** battery-only use (the Rotato class runs on 4×AA), manual lever bases, the 铡刀, the 葱丝刀 and printed jigs are not electrical goods.
- **Whether a personal overseas purchase must carry the Mark: ND.** This is the open question in #24.
- **Preference:** battery or non-powered options, and a Singapore-registered USB charger.

---

## 6. Bench proof needed (#10)

Each item needs the cook's real ingredient, a logged pass/fail per trial (`R19_RELIABILITY` §8 taxonomy), and a cutting or push force read on a scale where a press is involved.

| # | Test | Decides |
|---|---|---|
| 1 | Garlic G1: peel rate, crushed cloves, cloves per batch, fan skin separation; crack-plate clove release | garlic method |
| 2 | Ginger in the 85 W abrasive peeler: residual skin, loss, alone and mixed | ginger method; whether to ask the user about unpeeled ginger |
| 3 | Rotary peeler on tender luffa pieces and on ripe tomato: tearing, peel depth, juice loss | luffa and tomato methods |
| 4 | Squid die: penetration force, depth spread, sticking, curl after the scald; the user's view of the crosshatch | squid method |
| 5 | Okra comb press: placement success, press force, halves sticking | okra method |
| 6 | Broccoli coring: force, floret sizes, crown damage | broccoli method |
| 7 | Bamboo: flesh push-out after halving and base trim; force; waste | bamboo method |
| 8 | Fish sled: push force, cut path versus spine, halves joined, the fish standing; scaling | fish method, or ask the user to reopen 开背 at the stall |
| 9 | Dried chili on the 13 mm grid: fines and seeds; weekly-batch shelf life in the portioner | chili method |
| 10 | 葱丝 sleeve: shred width, jams | 葱丝 method |
| 11 | AY-403 lever ratio and window size (still unknown since market_r10 13.6) | every lever-base concept |

---

## 7. Open decisions for the user
1. **Order changes with the same result:** squid pieces before scoring; luffa segmented before peeling.
2. **Look changes:** squid crosshatch (straight cuts) versus true 麦穗 (one slanted direction); ginger with some skin left (abrasion).
3. **Tomato:** test the rotary peeler (T1), or accept skipping the peel (T3).
4. **Fish and bamboo:** fund the concept jigs and bench tests, or reopen the stall 开背 and shelled shoots. That is the structural lever in `R19_RELIABILITY.md` §7.
5. **Two small near-single-purpose devices** (garlic peeler, rotary peeler) under the multi-function rule.

---

## 8. Honesty notes
- **Prices and specs.** Every 1688 price is a market-page wholesale list price read on 2026-10-13, not a retail price, and not checked on the offer pages (they need JS).
  - Sizes, power and weights of the 1688 items are ND unless an overseas listing of the same class gave them, marked [C].
  - Two overseas reseller pages returned 410 and one maker page returned 429 or 403. Their numbers are from search snippets only.
- **Concepts.** All jig sizes, prices, strokes and pick counts marked [est] are mine. No jig is drawn in CAD, simulated or benched.
- **Forces.** No cutting force for garlic cracking (beyond the 40 N compression), okra, squid, broccoli coring, bamboo or fish was found. None was invented. The arm's ~100 N is from R11.
- **Not re-checked:** reach and collision for any new work spot, and the AY-403 window and lever ratio.
- **Count.** The 16 follows `R19_RELIABILITY.md` §2.3, which includes 葱丝; the issue body lists 15.
- **Files.** Only this file was created. No existing file was changed. No GitHub post or edit.

## 9. Sources (read 2026-10-13; [C] / [O] as in the text)
- 1688 market pages (WebFetch, list titles and prices only):
  - 剥蒜机 https://www.1688.com/market/-B0FECBE2BBFA.html
  - 家用剥蒜机 https://www.1688.com/market/-BCD2D3C3B0FECBE2BBFA.html
  - 生姜去皮机 https://www.1688.com/market/-C9FABDAAC8A5C6A4BBFA.html
  - 丝瓜削皮机 https://www.1688.com/market/-CBBFB9CFCFF7C6A4BBFA.html
  - 电动削皮机 https://www.1688.com/market/-B5E7B6AFCFF7C6A4BBFA.html
  - 西兰花切花机 https://www.1688.com/market/-CEF7C0BCBBA8C7D0BBA8BBFA.html
  - 西兰花切朵机 https://www.1688.com/market/-CEF7C0BCBBA8C7D0B6E4BBFA.html
  - 竹笋剥壳机 https://www.1688.com/market/-D6F1CBF1B0FEBFC7BBFA.html
  - 剥笋机 https://www.1688.com/market/-B0FECBF1BBFA.html
  - 鱼开背机 https://www.1688.com/market/-D3E3BFAAB1B3BBFA.html
  - 鱼开背器 https://www.1688.com/market/-D3E3BFAAB1B3C6F7.html
  - 鱿鱼切花机 https://www.1688.com/market/-F6CFD3E3C7D0BBA8BBFA.html
  - 鱿鱼花刀机 https://www.1688.com/market/-F6CFD3E3BBA8B5B6BBFA.html
  - 花刀器 https://www.1688.com/market/-BBA8B5B6C6F7.html
  - 番茄去皮机 https://www.1688.com/market/-B7ACC7D1C8A5C6A4BBFA.html
  - 秋葵切头机 https://www.1688.com/market/-C7EFBFFBC7D0CDB7BBFA.html
  - 四季豆切头机 https://www.1688.com/market/-CBC4BCBEB6B9C7D0CDB7BBFA.html
  - 干辣椒切段机 https://www.1688.com/market/-B8C9C0B1BDB7C7D0B6CEBBFA.html
  - 辣椒剪刀 https://www.1688.com/market/-C0B1BDB7BCF4B5B6.html
  - 葱丝机 https://www.1688.com/market/-B4D0CBBFBBFA.html
- Garlic:
  - Baidu Baike 旋转式气脱剥蒜机 (search snippet; page 403) https://baike.baidu.com/item/%E6%97%8B%E8%BD%AC%E5%BC%8F%E6%B0%94%E8%84%B1%E5%89%A5%E8%92%9C%E6%9C%BA/5865940
  - instacuppa blog https://instacuppastore.com/blogs/main-page/garlic-peeler-machine-electric-vs-silicone-vs-roller-which-works-best
  - fruugo listing (snippet) https://www.fruugo.fr/electric-garlic-and-grape-peeler-with-20second-speed-peeling-and-precision-rotary-peeling/p-449609266-946228601
  - Omcan 13442 https://www.webstaurantstore.com/electric-countertop-stainless-steel-garlic-peeler-110v/915DAL06.html
  - JD Joyoung page https://www.jd.com/tupian/73747fcd097b1270378.html
- Ginger: ICAR JAE abrasive ginger peeler (snippet) https://epubs.icar.org.in/index.php/JAE/article/view/14491
- Rotary peeler: Starfrit Rotato Express 2.0 (snippets) https://www.desertcart.com.ar/products/51578557 and https://www.10news.com/electric-peeler-veggies-fruit
- Broccoli:
  - Lee Valley 75617 (snippet; page 429) https://www.leevalley.com/en-gb/shop/kitchen/kitchen-tools/choppers/75617-cauliflower-and-broccoli-prep-tool
  - Floreto (snippet; page 403) https://hortidaily.com/article/6019923/floreto-de-coring-70-heads-of-broccoli-cauliflower-per-minute
  - Jadwisieńczak & Kaliniewicz 2022 (snippet) https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-e6f9fa95-d46b-414c-8bea-20d96103cb82/c/11-jadwisienczak_kaliniewicz_cauliflower_2022_25_171-181.pdf
- Bamboo:
  - patent CN107549830A https://patents.google.com/patent/CN107549830A/zh
  - zhihu (snippet) https://zhuanlan.zhihu.com/p/46384991
- Squid:
  - patent CN209498409U https://patents.google.com/patent/CN209498409U/zh
  - nongjx (snippet; page 468) https://www.nongjx.com/chanpin/2808066.html
- 葱丝: patent CN203579692U https://patents.google.com/patent/CN203579692U/zh
- Fish technique (search snippets, pages not opened): https://m.xiachufang.com/recipe/31685/ and https://www.toutiao.com/zixun/7543103010981988379
- Tomato blanching (snippet): https://www.jessicagavin.com/how-to-peel-a-tomato/
- Singapore CPSO list of controlled goods: https://www.consumerproductsafety.gov.sg/suppliers/cpsr/list-of-controlled-goods/
- Repo inputs:
  - `DECISIONS.md`
  - `research/r19_asbought.md`
  - `sim/r10/claude/R19_PREP_AUDIT.md`
  - `sim/r10/claude/R19_RELIABILITY.md`
  - `research/market_r10.md`
  - `research/finger_change_and_food_eoat.md`
  - `research/hand_options.md`
  - `research/food_catalog_inputs.md`
