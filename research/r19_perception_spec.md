# R19 — Perception spec beyond the wok; IR emissivity on steel (GitHub #25)

Status: laptop study, 2026-10-14. Nothing is bought or built. Every number is tagged:
**[S]** source (repo `file:line` or URL), **[E]** estimate / engineering judgement, **[M]** my own calculation (method stated).
Web sources were read read-only; where only a search-result summary was available (page blocked or certificate error), that is said.
Cross-refs: #21 (safety / presence), #26 (failure detection, force control), #30 (demo wok-vision is synthetic), #32 (routine stop conditions), #19 (heat cut), #36 (tool cable).

---

## Answer first

1. **Cues.** The 157 camera cues, 40 thermometer cues and 43 smell cues [S `sim/r10/claude/README_R10.md:497`; `research/wanggang_cooking.md:274-296`] reduce to **nine measurable signals**: oil temperature, wok surface temperature, food colour / browning, doneness, sauce thickness, boil / simmer, smoke, steam (an interferer more than a cue) and sizzle sound. Smell has no sensor that can stand in for it. It is replaced, as the repo already says, by **time + oil temperature** [S `research/wanggang_cooking.md:296`]. A VOC sensor in the hood is added only as a burn monitor. Every cue keeps a **time-based fallback**, because the reference cook gives 74 time cues anyway [S `research/wanggang_cooking.md:276`].
2. **IR on a wok works for oil and food, and fails for dry steel.**
   - Oil and food emit at about **0.95** in 8–14 µm [S ATK, ThermoWorks]. The round wok pools the oil: 30 g sits about **7 mm deep in an 11 cm disc** [M]. That pool is about 70 thermal pixels across [M], so pooled-oil readings can reach **about −10…+5 °C** (instrument ±2 °C / 2 % [S InfiRay], plus ε 0.90–0.95 [M]).
   - A dry or thinly oiled seasoned wok has an unknown ε of roughly 0.5–0.9. That gives **−54…+7 °C at 200 °C** with ε set to 0.85 [M, Planck model below].
   - Scraped bright spots (ε 0.1–0.4) read **60–120 °C when the true value is 200 °C** [M].
   - Reflections of the hot opposite wall push readings up by up to **+21 °C** [M].
   - Steam reads low, and a fogged lens blinds the camera [S Exergen].
   - So the demo's choice ("dry seasoned wok → `None`", issue #25) is correct.
3. **Mitigation stack (recommended).**
   - (a) Measure the **oil pool or the food**, never the bare steel.
   - (b) Make the planned **spring-loaded type-K contact probe** on the wok's outer wall (already the hardware high limit [S `research/r19_fire_heatcut.md:51`]) the **reference for dry-wok and preheat** readings, and the online check of the IR. Class 1 type K is ±1.5 °C up to 375 °C [S tcdirect / IEC 60584-1].
   - (c) Use a bench-fitted per-wok ε map. An in-view high-ε reference patch is optional.
   - (d) Lock the Tiny1-C in **low gain (50–550 °C)**. High gain stops at 150 °C, right inside the 120–240 °C oil range [S InfiRay; S `README_R10.md:493`].
   - (e) Add a lens purge / window, and treat steam frames as invalid.
   - The cooker's own NTC reads the back of the glass and lags [S `research/r15_cooking_market.md:296`]. It is a coarse dry-burn guard only.
4. **Outside the wok** the robot needs four sensor kinds, each tied to a planner tolerance:
   - **one or two fixed overhead RGB-D cameras** under the upper cabinets: presence, a coarse pose to ±5 mm, and spills and occupancy at 10 mm voxels;
   - **a wrist RGB-D or RGB camera** for close checks before a grasp, to ±1–2 mm at 0.15–0.3 m [E];
   - **force and weight**: the finger-root FSR, the arm's joint torque / flange F/T, and the existing load cells;
   - **presence sensing** in the aisle, which is rated per #21.
   - Most fixtures are **keyed** (wok slot, lid rack, cup lug, plate stand). For those, perception only has to confirm presence or seating; it does not supply the pose.
   - Two items have no fixture and need real pose sensing: **food on the prep tray** (15 mm half-range [S `R19_TOLERANCE.md:114`]) and **plates placed by hand** (10 mm [S `R19_TOLERANCE.md:112`]).
5. **After a person steps in**, a **re-scan routine** runs before any set restarts:
   - hub match;
   - the held-object check;
   - an overhead depth diff against the layout's reference map;
   - per-station checks of the next sets' pre-conditions;
   - a wok thermal snapshot;
   - a touch-off if a docking or fixture term changed;
   - the user confirms on an annotated image.
   - Estimated time is about 20–60 s, plus 10–20 s per touch-off [E; touch-off from S `R19_TOLERANCE.md:285`].
6. **Added cost, about ¥4–9k** [S/E, table §5]. The ¥18k safety allowance stays separate: the rated scanner belongs to #21.

---

## 1. Cue inventory → measurable signals

### 1.1 What the recipes ask for

Counts are phase mentions in 42 Wang Gang recipes [S `research/wanggang_cooking.md:274-290`; aggregates in `research/wanggang_cooking.json` `8_endpoint_cues`].

| Cue type | Mentions | Recipes | Repo's sensor column |
|---|---|---|---|
| time | 74 | 32 | timer |
| smell | 43 | 30 | none direct |
| texture | 42 | 29 | camera (+probe) |
| temperature | 40 | 26 | thermometer |
| other (mostly "mixed well") | 38 | 24 | varies |
| colour | 37 | 23 | camera |
| bubbles | 27 | 17 | camera |
| thickness | 25 | 21 | camera |
| shape | 12 | 12 | camera |
| smoke | 11 | 10 | camera |
| probe (chopstick, pinch) | 6 | 6 | probe / force |
| taste | 4 | 3 | taste |
| liquid level | 2 | 2 | camera |
| sound | 1 | 1 | microphone |
| oil clarity | 1 | 1 | camera |

- **The 157 "camera" mentions** = colour 37 + texture 42 + bubbles 27 + thickness 25 + shape 12 + smoke 11 + liquid level 2 + oil clarity 1 [M, sum of the rows above].
- **Where they happen** [M, `wanggang_cooking.json`, phases × cue type]:
  - wok: 29 of the 40 temperature cues, 32 of the 37 colour cues and 22 of the 25 thickness cues;
  - deep oil in the wok or fryer: 11 temperature cues;
  - pot / steamer: a handful of bubble, time and probe cues.
- **Stated temperatures.** 34 of the 40 temperature cues give a number [S `wanggang_cooking.md:293`]. Of the phases, 36 carry a `temp_C`:
  - range 90–240 °C, median 170 °C [M];
  - values 90 ×2, 120 ×4, 150 ×10, 170 ×2, 180 ×10, 195, 200 ×2, 210 ×3, 240 ×2.
  - The scale is the creator's own: 30 °C per 成, 6成 ≈ 180 °C [S `research/wanggang_recipes.json:10`].
  - The remaining cues are "wok hot / 冒青烟 / 有点热" preheat judgements [S `wanggang_cooking.md:293`].

### 1.2 Signal table (proposal)

Rates: the Tiny1-C delivers 25 Hz [S InfiRay]. The heat-control loop needs only about 2–5 Hz:
- a stir pause at full power heats the wok +17 °C in 6 s [S `README_R10.md:532`], i.e. about 3 °C/s [M];
- so 2 Hz keeps sampling lag ≤ 1.5 °C [M].

| Signal | Cues it serves (mentions) | Primary sensor and view | Accuracy target | Update | Fallback (time rule) |
|---|---|---|---|---|---|
| **Oil temperature** (pooled oil ≥ 10 g, deep oil) | temperature 34 numeric; part of smoke 11 | Thermal camera under the hood front, ROI = the oil pool at the wok bottom, ε 0.95, low gain. Cross-check: the contact probe's wall reading | **±10 °C p95 acceptance (issue #25 gate), ±5 °C goal**, over 120–240 °C. ±10 °C is a third of one 成 step [M from S `wanggang_recipes.json:10`] | 5 Hz filtered (25 Hz raw) | Heat-model time at a known power: 30 g oil from 30 to 180 °C takes 43 s on induction [S `README_R10.md:529`]. Calibrate the time per oil mass on the bench. The hardware high limit stays independent |
| **Wok surface temperature** (dry preheat 锅烧热, 润锅, 烙皮 / dry sear) | temperature 6 non-numeric; "smoking hot" (part of smoke) | **Contact type-K probe on the outer wall** (reference). IR only on a reference patch or with the per-wok ε map, flagged low-confidence | ±15 °C [E] (a preheat judgement, not a set-point) | 2 Hz | Preheat time at power, from the bench run. Never above the 250 °C working limit [S `README_R10.md:508`] |
| **Food colour / browning** (golden, red oil, 糖色 stages, oil clarity) | colour 37, oil clarity 1, part of shape 12 | Colour camera under the hood (fixed exposure and white balance), a **colour reference card** in view on the hood underside, a hood LED as the only light source in the cooking window [E] | Stage classification (e.g. 糖色 light yellow → reddish brown) ≥ 90 % agreement with human labels on real wok video [E]. Report ΔE on the reference card ≤ 3 per session [E] | 2–5 Hz | Recipe time at temperature (the creator's own times) |
| **Doneness** (断生, 成熟, 80 % done, pierce, pinch) | texture 42, probe 6, taste 4 | (a) IR surface temperature of food pieces (ε 0.95 [S]) integrated with time; (b) piece size from the camera (dice 15 mm per R15); (c) for braises and whole items, an **arm-held skewer thermometer** (type-K needle) or a pierce-force test on the wrist F/T | Core estimate ±5 °C [E]. Pierce force: pass/fail against a per-food threshold from the bench | 1 Hz (estimate); probe on demand | The creator's stated times (74 time cues). The taste cues (4) stay a recipe-time constant: no sensor proposed |
| **Sauce thickness / 勾芡 / reduce** | thickness 25, liquid level 2 | Colour camera: (a) the spatula trail closing time after a stroke; (b) bubble size and number (large → small); (c) IR: the wet surface sits near 100 °C and rises once the water is gone [E]. Starch is already dosed by weight (seasoning cups) | Binary "thick enough" ≥ 90 % agreement with labels [E]. Liquid level ±5 mm on the wok wall [E] | 2 Hz | Fixed seconds after the slurry goes in at the boil, per dish (bench) |
| **Boil / simmer** | bubbles 27 | IR plateau at about 100 °C on water / soup (ε 0.95 [S]) + camera bubble motion + microphone | Detect the boil within 3 s of onset [E]. Plateau ±3 °C [E] | 2 Hz | Heat-model time to boil for the liquid mass |
| **Smoke / 冒青烟 / 锅气** | smoke 11 | Colour camera: haze / plume over the oil against the hood's dark underside. Oil IR in the smoke-point band 190–234 °C [S `README_R10.md:508`]. **SGP41-class VOC** sensor in the hood duct inlet (τ63 < 10 s [S Sensirion]) as a confirm and burn alarm | Onset within 2 s [E]. VOC: trend only (device spread ±15 index points [S Sensirion]) | 5 Hz camera, 1 Hz VOC | Oil temperature of 200–210 °C as the "smoking" proxy [E], always below the 250 °C limit |
| **Steam** (interferer) | — | Colour camera haze score; IR frames inside a steam event flagged invalid [S Exergen: steam reads low] | Flag ≥ 95 % of steam frames [E] | 5 Hz | Hold the last valid IR value for ≤ 3 s, then fall back to the heat model [E] |
| **Sizzle sound** | sound 1; also a "food entered / water hit oil" event | MEMS microphone in the hood module | Event detection (food in, sizzle decay) ≥ 95 % [E]. The eye-and-ear chopstick oil test is 5–10 % accurate above 150 °C [S Waterloo] | 20 Hz features | Not needed as an endpoint. Acoustic doneness exists in fryer patents [S US5180600]. A hood microphone that detects food entry exists in a patent [S CN114811683A] |
| **Smell 炒香 / 出香味** | smell 43 | **None as an endpoint.** E-noses track frying-oil deterioration [S spkx 2013] but need per-food training. The SGP41 is a burn monitor only | — | — | **Time + oil temperature** (10–30 s at the stated 成) [S `wanggang_cooking.md:296`; S `wanggang_recipes.json` method note] |
| **Mixed well / other** | other 38 | Stroke count (motion library), camera spot-check | — | per stroke | Fixed stroke count |

---

## 2. IR on woks

### 2.1 Emissivity, 8–14 µm

| Surface | ε (8–14 µm unless noted) | Tag |
|---|---|---|
| Steel, polished | ≈ 0.1 | [S `research/r15_cooking_market.md:292` (Optris)] |
| Steel, oxidised | 0.7–0.9 | same |
| Polished iron | 0.14–0.38 (total) | [S [Engineering Toolbox](https://www.engineeringtoolbox.com/emissivity-coefficients-d_447.html), via search summary] |
| Polished cast iron at 200 °C | 0.21 (total normal) | [S [Neutrium](https://neutrium.net/heat-transfer/total-normal-emissivities-of-selected-materials/), via search summary] |
| Oxidised steel sheet at 22 °C; rough oxide layer | 0.657; 0.80 | same |
| Cast iron, unoxidised / oxidised | ≈ 0.2 / 0.6–0.95 | [S `r15_cooking_market.md:293`] |
| Stainless (ThermoWorks setting) | 0.59 | [S `r15_cooking_market.md:294`] |
| Food / organics; water | 0.95–0.97; 0.95 | [S `r15_cooking_market.md:294`] |
| Cooking oil | ≈ 0.95 | [S [America's Test Kitchen](https://www.americastestkitchen.com/articles/5433-how-to-use-an-infrared-thermometer); [blog](https://www.absurdlyoptimized.com/cooking/ir-thermometer/), vendor-side guidance, not a measurement] |
| **Seasoned carbon steel** (thin polymerised-oil layer on oxidised steel) | **No published value found.** Expected between bare steel and opaque oil, i.e. roughly 0.5–0.9, varying across the wok and over its life | [E] |
| **Thin oil film** (≈ 10–100 µm) on steel | **Thickness-dependent.** It moves from the bare-surface value toward the opaque-oil value as the film thickens [S [US patent 7075085](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7075085), via search summary]. Crude-oil slicks change ε significantly over 20–120 µm [S [Spectroscopy & Spectral Analysis 34(11) 2014](https://m.researching.cn/articles/OJ5da413dca2de919c), via search summary]. No edible-oil-on-steel data found | [S] trend / [E] magnitude |

### 2.2 Expected error [M]

Method [M]:
- Band radiance is integrated over 8–14 µm with a flat response.
- Reflected background is at 35 °C. The camera inverts with its ε setting and the same background.
- Script: session scratchpad `emis.py` (not committed).
- This is a grey-body model. It ignores spectral ε, angle and atmosphere.

| Case | Setting → truth | Error at 120 / 150 °C | Error at 200 °C | Error at 240 °C |
|---|---|---|---|---|
| Deep oil pool, ε known | 0.95 → 0.95 | 0 | 0 | 0 |
| Deep oil, ε a bit off | 0.95 → 0.90 | −3.6 (120) | ≈ −5 | −7.8 |
| Oil, ε further off | 0.95 → 0.85 | −7.2 (120) | ≈ −10 | −15.7 |
| Seasoned / thin film, mid guess | 0.85 → 0.75 / 0.95 | −10.5 / +10.1 (150) | −14.5 / +13.9 | −17.6 / +16.9 |
| Seasoned, poor | 0.85 → 0.6 / 0.5 | −27 / −39 (150) | −38 / −54 | −46 / −66 |
| Bright scraped steel | 0.95 → 0.1–0.3 | reads 52–80 at 150 | **reads 61–103** | reads 69–121 |
| **Hot wall reflected** (opposite wall at 200 °C, background assumed 35 °C) | ε 0.85 | — | **+21** | — |
| Hot hood / background at 80 °C, assumed 35 °C | ε 0.85 / 0.5 | — | +4 / +23 | — |
| Instrument alone (±2 °C or ±2 % of reading [S InfiRay]) | — | ±3 (150) | ±4 | ±4.8 |
| Steam in the path; condensation on the lens | — | reads **low**; a fogged lens is blind [S [Exergen tech note 7](https://www.exergenglobal.com/tech-notes/7-temperature-measurements-in-steaming-environments)] | | |

- Rule of thumb [M]: at 200 °C, an ε error of 0.05 gives about 7 °C (`dT/dε` at ε 0.9).
- A bare reflective surface also mirrors whatever hot or cold object it faces. A forum test shows a steel plate reading hot from the oven interior [S [pizzamaking forum](https://www.pizzamaking.com/forum/index.php?msg=651800), anecdotal]. In a concave wok, that object is often the opposite hot wall.
- **The issue's "tens of degrees" holds for dry or thin-film steel, and does not hold for pooled oil.**

### 2.3 Geometry: the oil pool is a usable target [M]

- **Wok.** Sphere radius 0.20 m, rim radius 0.17 m, 95 mm deep [S `sim/r10/claude/kitchen15.py:6`]. The hood is 23 cm above the rim [S `kitchen15.py:13`; on-site check pending, `r19_fire_heatcut.md` §5].
- **Pool size** [M, spherical cap, oil 0.91 g/ml]:

  | Oil | Pool depth | Pool diameter |
  |---|---|---|
  | 10 g | ≈ 4 mm | ≈ 8 cm |
  | 30 g | ≈ 7 mm | ≈ 11 cm |
  | 50 g | ≈ 10 mm | ≈ 12 cm |

  - A few-mm layer is opaque in 8–14 µm, so ε ≈ 0.95 holds [E, from the thin-film trend above].
- **Thermal view.**
  - The Tiny1-C 256 × 192 at 12 µm with the 3.2 mm lens gives HFOV 51° × VFOV 40° [M from S InfiRay pixel and lens data].
  - At about 0.35 m to the wok bottom, the footprint is ≈ 0.34 × 0.25 m [M], at ≈ 1.3 mm per pixel. The 11 cm pool is ≈ 80 px across.
  - The 2.0 mm lens (75° HFOV [M]) is the choice if the whole rim must be in view from the hood front.
- **Spatula.** The blade keeps the pool from being one static spot during stirring. The arm and spatula occlude the view: use a median over the pool ROI, masked by the colour camera's spatula segmentation [E].

### 2.4 Mitigations, ranked

1. **Measure the food or oil, not the steel.** All 34 numeric oil cues are about **oil**. Measure them on the pooled oil (ε 0.95), or on food pieces (ε 0.95–0.97 [S]). The ROI comes from the colour camera: segment the pool and food, and reject bright steel.
2. **Pan contact probe = reference and high limit.**
   - A spring-loaded type-K probe on the wok's outer wall is already the planned hardwired high limit [S `research/r19_fire_heatcut.md:51`], at ¥150–600 with the limit controller [S `r19_fire_heatcut.md:203`, itself E].
   - Read the **same probe** into the PC (thermocouple amplifier) for preheat and dry-wok decisions, and use it to **check the IR online**. When the pool is warm and the probe reads within its own band, the IR/probe offset is logged per session.
   - Class 1 type K: ±1.5 °C over −40…375 °C [S [TC Direct](https://tcdirect.co.uk/thermocouple-sensors/thermocouple-accuracies.aspx), citing IEC 60584-1; secondary source].
   - It reads the outer wall under the coil, not the inner surface. Expect a lag and offset on the bench [E].
   - Commercial precedent: the Mijia 3 Pro uses a titanium pressure probe on the wok; the Japan Si sensor limits the pot bottom to 250 °C [S `r15_cooking_market.md:298`].
   - Open: the wok is lifted for plating, so "wok seated" logic and wear apply [S `r19_fire_heatcut.md:224`].
3. **Per-wok ε map from the bench.**
   - Record IR vs probe over the dry seasoned wok at 100–260 °C, then fit ε per wok region.
   - Re-fit every N weeks, because seasoning changes [E].
   - Then use dry-wok IR for **trend only**: rate of rise, hot-spot shape.
4. **Emissivity reference patch (optional).**
   - A small high-ε patch in view, at the steel's temperature, gives the steel's in-situ ε by comparison.
   - Inside the wok, the patch would be scraped by the spatula and touch food. A food-safe coating at 250 °C is not sourced [E].
   - Practical variant: the **润锅 oil pool itself** is the reference patch. Alternatively, a patch on the **outer** wall seen by a second low-cost IR point sensor next to the contact probe [E].
5. **Induction cooker temperature mode / NTC.**
   - Commodity concave units read the back of the glass. That lags and misses concave pans [S `r15_cooking_market.md:296`].
   - None documents an interface; the knob is turned by a servo [S `README_R10.md:506`].
   - Hob temperature modes exist on flat-zone products only: Miele TempControl 160/200/220 °C, Bosch PerfectFry [S `r15_cooking_market.md:83-85`].
   - **Use**: the cooker's own dry-burn cut-off near 280 °C [S `README_R10.md:508`] as the last line. It is not a measurement.
6. **View geometry.**
   - Camera axis within about 45° of the pool normal [E].
   - Place the camera so that the pool's specular reflection is the cool hood underside, not the opposite hot wall or the hood lamp. Check this in the MuJoCo view study (#25 study step 2).
7. **Steam and grease.**
   - An IR-transparent protective window with an air-curtain purge (purge as in [S Exergen]) [E].
   - The colour camera flags steam frames as invalid.
   - A daily **lens check** against the probe at a stable pool temperature: an offset above 5 °C prompts the user to wipe the window [E].
8. **Gain.**
   - Lock **low gain, 50–550 °C** [S InfiRay, via search summary of the official page; the page itself returned a certificate error].
   - High gain ends at 150 °C, inside the oil range. Gain switching mid-cook adds a step error [E].
   - Boil plateaus at 100 °C are inside the low-gain range.

### 2.5 Bench calibration procedure (hardware study 3 of #25, about ¥2k)

**Kit:**
- the concave induction cooker class of the design (¥320–600 [S `r19_system_cost.md:66`]);
- the 34 cm carbon-steel wok, seasoned;
- a Tiny1-C 256 (3.2 mm lens) and the colour camera on a rig at the hood position (0.23 m above the rim, front edge);
- **3 type-K surface probes** (one spring-loaded on the outer wall at the design spot; one on the inner bottom under the pool; one ribbon probe on the inner wall at 6 cm);
- **1 immersion type-K** in the oil, tip 2 mm above the steel;
- a 4-channel logger at ≥ 5 Hz;
- a matt-black high-ε tape patch on a spare steel coupon, heated beside the wok, as an ε-reference check [E];
- a kettle for steam.

**Steps:**
1. **Probe check.** All type-K probes in boiling water (100 °C at sea level; Singapore is near sea level [E]), then in the oil bath against each other: agreement ≤ 1.5 °C [S class 1].
2. **Camera warm-up.** Run 20 min at low gain, then check against the black patch at 100 / 200 °C. Record the offset.
3. **Dry seasoned wok.** Heat at 3 fixed powers to 260 °C, then cool. Log IR (bottom ROI, wall ROIs at ε 0.85) against the probes.
   - Output: the ε map per region, the error band and the probe lag.
4. **Oil.** 10 / 30 / 50 g of oil (the issue's range). Hold set-points 100 / 120 / 150 / 180 / 210 / 240 °C, each for 60 s.
   - Log the pool ROI at ε 0.95 against the immersion probe.
   - Output: the **error band per oil mass and set-point** (p50 / p95). Also log the time-to-temperature for the fallback rule.
5. **Food.** 150 g of potato dice dropped into 180 °C oil. Compare the pool and piece IR with the immersion probe; measure the IR recovery time.
6. **Steam.** Add 100 g of water to a 150 °C wok. Measure how long IR is invalid and the size of the low bias.
7. **View angle.** Tilt the rig 0 / 30 / 45 / 60° from the pool normal. Try the spatula in view and the opposite hot wall reflected.
8. **Greased lens.** Wipe the window with an oil film. Measure the offset and test whether the daily check catches it.
9. **Repeatability.** Day 2 and day 7 on the same wok; record any ε-map drift.

**Pass criteria:**
- **Pooled oil 120–240 °C: |IR − immersion| ≤ 10 °C p95** (the issue's gate). Goal ≤ 5 °C.
- Dry wok: the contact probe within ±15 °C of the inner bottom probe.
- **If oil IR fails the 10 °C gate:** keep IR for trend and cues, and run the heat loop on the contact probe. Re-test with the probe pressed on the **inner** bottom (Mijia-style), or the cooker NTC, as the issue already proposes.

---

## 3. Sensors outside the wok, per station

### 3.1 What sets the accuracy

- **Planning gates**: 10 mm robot–environment and 5 mm gripper/held–environment [S `R19_MOTION_LIBRARY.md:110`]. A set tolerates position error only up to its reserve beyond those gates [S `R19_MOTION_LIBRARY.md:193`].
- **Measured reserves**:
  - lid into the rack 0.3–1.0 mm; wok grasp 2.4 mm; stir 2.0 mm; sink tip 3.3–3.4 mm; carries 10–83 mm [S `R19_MOTION_LIBRARY.md:197-202`];
  - real tolerances: y ≥ 3.9 mm, x ≥ 15 mm, z down to 1.0 mm [S `R19_TOLERANCE.md:44-50`].
  - **No camera fixes a 1 mm seat.** The seats are keyed fixtures plus compliance or force (#26) [S `R19_TOLERANCE.md:139`].
- **Grasp tolerances**:
  - tomato width ±2 mm, or an FSR on the pad (¥20–50, recommended) [S `README_R10.md:182,234`];
  - grasp offset in the jaws 0.5–1 mm [S `R19_TOLERANCE.md:97`];
  - lid rack capture ±14.8 mm [S `DECISIONS.md:569`];
  - perception grid: an offset is "verified" only on a pre-checked grid; **where the reserve is < 3 mm, use fixtures, not grids** [S `R19_MOTION_LIBRARY.md:206`].
- **Fixture half-ranges** in scenario C (docking stops):
  - cooker 1 mm, lid rack 0.5, faucet 0.5, sink 0.5;
  - **plates by hand 10 → 2 with the guarded stand**; prep bowls 5 → 2;
  - **food on the prep tray 15 mm, not a fixture** [S `R19_TOLERANCE.md:105-116`].
- **AprilTag fiducials.** 5–8 mm at 0.7 m in the literature; a calibrated wrist camera at 0.2–0.3 m is est. 0.5–1 mm [S `R19_TOLERANCE.md:286`, Abbas et al. 2019 as cited there]. Good for "fixture moved" detection, not for 1–4 mm reserves.

**Consequence: two perception jobs.**
- **(i) Confirm** that a keyed thing is present and seated. This is binary, with a ±5 mm / ±3° sanity band [E] that flags a fixture knocked out of its keying.
- **(ii) Measure** a pose for unkeyed things to ±2 mm (food in a V-rib channel, a hand-placed plate) so the runtime can pick a verified grid point.

### 3.2 Proposed sensor set

| ID | Sensor | Mounting | Role | Cost |
|---|---|---|---|---|
| T1 | Tiny1-C 256 thermal + colour camera (existing plan) + MEMS mic + SGP41-class VOC | Hood front module, window + purge | Wok cues (§1–2) | ¥950–1,430 + colour ¥100–500 [S `r19_system_cost.md:61`]; mic and VOC ¥50–150 [E] |
| P1 | Type-K spring probe on the wok outer wall + amplifier into the PC (shared with the limit controller) | Cooker bowl bracket | IR reference, preheat, high limit | ¥150–600 [S `r19_fire_heatcut.md:203`, E there] |
| O1–O2 | Overhead **RGB-D**, Gemini 336-class (optimal range 0.26–3 m [S [RobotShop](https://www.robotshop.com/products/orbbec-gemini-336-camera)]) | Under the upper cabinets: O1 over the prep / staging / plating run, O2 over the sink / fridge end | Presence, coarse pose (±5 mm [E]), spill and occupancy maps, re-scan | US$392 ≈ ¥2.8k each [S RobotShop; ×7.1 E] |
| W1 | **Wrist RGB-D**, D405-class (ideal 7–50 cm, ±2 % at 50 cm [S [SparkFun](https://www.sparkfun.com/intel-realsensetm-depth-camera-d405.html) / distributor listings]) or a plain wrist RGB camera + AprilTags | On the PGC flange adapter; **needs its own cable** (with the TCI on, the tool connector has no spare channel [S `research/hand_options.md:96`]; cable routing #36) | Pre-grasp checks: food channel and width, cup / caddy seated, plate edge, sink clear, cold box | US$318–460 ≈ ¥2.3–3.3k [S SparkFun retired list / [MYBOTSHOP](https://www.mybotshop.de/Intel-RealSense-Depth-Camera-D405_1)]; an RGB-only variant ¥120–550 [S `r19_seasoning_cups.md:306`] |
| F1 | Finger-root force sensor / pad FSR (in the design) | Fingers | Grasp success, width-free gentle grasp | ¥20–50 each [S `README_R10.md:234`] |
| F2 | Arm joint torque + flange F/T (UR5e built-in [S `R19_TOLERANCE.md:285`]; FR5: check) | — | Held-mass check, touch-off, contact monitors (#26) | 0 |
| L1 | Load cells: bottles (existing) + plating stand + cup staging pad | Under the stands | Plate present, dish mass (spill check), cup present / poured | ¥10–55 per cell + HX711 [S `r19_seasoning_cups.md:303`] |
| R1 | mmWave presence (LD2410-class: 0.75–6 m, 0.75 m resolution [S [Tayda](https://www.taydaelectronics.com/ld2410c-24ghz-human-presence-sensor-module.html)]) | Cart mast, aisle-facing | **Comfort layer only** (slow down, pause idle sets) | US$4.19 ≈ ¥30 [S Tayda] |
| R2 | Safety-rated area scanner / safety radar (PL d target) | Cart base, aisle + low zones | **Safety function, owned by #21** [S `research/r19_hazard_analysis.md:211`] | In the ¥18k safety allowance, unpriced [S `r19_hazard_analysis.md:298`] |
| S1 | Water-leak strip | Floor under the sink and in front of it | Water on the floor (slip hazard on the cart path) | ¥20–60 [E] |
| S2 | ToF point sensors, VL53L1X-class (to 4 m, 50 Hz [S [ST](https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html)]) | Optional: cold-box bin, fridge door gap, rice cooker lid | Cheap presence / gap checks where no camera sees | ¥20–50 each [E] |

### 3.3 Per station

| Station | Must verify (pre / post) | Sensor | Accuracy target, tied to the planner | Notes |
|---|---|---|---|---|
| **Prep tray (V-rib slot tray)** | Item present; which channel; position along the channel; yaw; width (tomato); after the pick: tray clear behind the item | O1 coarse (channel ID, ±5 mm along the channel). W1 close: width and offset. F1 confirms grasp | **Channel ID 100 %. Along-channel ±5 mm and yaw ±5° [E] against a verified grid** [S `R19_MOTION_LIBRARY.md:206`]. Width ±2 mm only if the FSR is not fitted [S `README_R10.md:182`]. Keep a 15 mm keep-out from the spatula pad (food term 15 mm [S `R19_TOLERANCE.md:114,140`]) | V-ribs self-centre round items: a channel every 34 mm [S `README_R10.md:289`], so lateral error is set by the rib. The issue's study 4 (30 tomatoes / carrots / eggplants, seated-pose spread) sets the real grid |
| **Cold box (fridge door bin)** | Door at 35°; box present in its bin; bridge bar where expected; after the set-down: box on the counter spot | Door angle from the arm's own joint state while holding the handle (form-closure grasp [S `README_R10.md:400`]). W1 sees the bin at 0.85 m. F2: held mass on lift. S2 optional for the bin | Bar position ±5 mm [E] (the grasp is from above with a 0.11 m bridge [S `README_R10.md:395`]). Set-down reserve 11.7 mm [S `README_R10.md:452`] → O2 confirms the spot is free at 10 mm voxels | "Door stays at 35°" is unmeasured [S `README_R10.md:460,465`]: watch the door edge with O2 during the transfer |
| **Fridge door** | Handle where expected; door not blocked; nobody between door and cabinet | W1 on approach. F2 force-monitored pull (#26). R1 / R2 presence (hazard H12 [S `r19_hazard_analysis.md:180`]) | Handle ±5 mm [E], inside the 23 checked door angles' reserve 0.1–4.2 mm only with a touch-off → **force-guided** | — |
| **Seasoning cups / caddy / staging** | Caddy docked and indexed; each cup present and seated; filled (dose weighed at the station); after the pour: cup empty and back in its slot | Station load cells (existing) for the fill. Staging-pad load cell (L1) for presence. O1 per slot. F2 held mass ±20 g [E] before and after the pour | Cup lug is the **keyed 30 mm block** [S `r19_seasoning_cups.md:348`] → confirm only: seated ±3 mm [E]. Empty after the pour: residual ≤ 5 g [E] (doses are 0.3–31 g [S `r19_seasoning_cups.md:287,293`]) | The spice tray uses a station colour camera to pick 八角 / 桂皮 [S `r19_seasoning_cups.md:292,306`] |
| **Prep bowls / dish carrier** | Bowl at its spot; contents present; after the pour: empty | O1 + L1 or F2 mass | Bowl ±2 mm with a locating ring [S `R19_TOLERANCE.md:113`] → confirm only | — |
| **Plates / plating spots (2)** | Plate present and seated in the **guarded stand**; plate empty before plating; after the tip: wok empty, food on the plate, **spill** on the stand or counter; plate removed by the user before the next dish | L1 under each stand (plate present, dish mass). O1 top view: food mask on the plate vs outside it. T1 colour camera: wok empty after the tip | Stand keeps the plate to 2 mm [S `R19_TOLERANCE.md:112`] → confirm only. A hand-placed plate (10 mm) needs O1 to ±2 mm or is refused. **Spill: detect ≥ 1 piece of 15 mm off the plate (O1, 10 mm voxels) and ≥ 10 % mass shortfall (L1)** [E]; sim plating keeps 81–91 % of rigid dice [S `README_R10.md:561`] | Finished plates are taken by the user [S `README_R10.md:835`] → L1 gives the "plate removed" event |
| **Wok in the cooker slot** | Wok seated and keyed; wok empty before the rinse; handle on its bracket | P1 probe contact (seated) + T1 + F2 at the set-down (force-guided seat, #26) | Keyed slot, 5 mm chamfer [S `R19_TOLERANCE.md:284`]; set-down z 4.0 mm [S `R19_TOLERANCE.md:50`] → seat by force, confirm by probe contact | — |
| **Spatula pad, spider rest, lid rack, pot (zone 2)** | Tool present and right face up (spatula sense −1 [S `R19_MOTION_LIBRARY.md:164`]); lid seated in the rack; pot on its zone | O1 (pad, rest). W1 face-up check. F2 seating. T1 lid seated over the pot (colour camera) | Keyed blocks → confirm only. Lid reserve 0.3–1.0 mm [S `R19_MOTION_LIBRARY.md:197-198`] → mechanical lead-in + compliance, perception confirms after the fact | — |
| **Sink and faucet** | Sink basin clear (dishes, hands) before the wok sink tip; lever block present; **water flowing** after FAUCET_OPEN; water off after close; sink not overflowing | O2 depth occupancy of the basin volume. Mic + O2 for flow [S `R19_MOTION_LIBRARY.md:161`, "camera / sound"]. S1 leak strip | Sink tip reserve 3.3–3.4 mm [S `R19_MOTION_LIBRARY.md:201`] → the basin must be **empty to 10 mm voxels** in the swept volume. Faucet 0.5 mm in C [S `R19_TOLERANCE.md:109`] → keyed clip, force-guided lever | A faucet sensor add-on is an open user decision [S `DECISIONS.md:473`] |
| **Rice cooker** | Started and done (the person loads and starts it [S `DECISIONS.md:491-493`]) | Cooker app state (MIoT "Start Cook" listed for one model [S `README_R10.md:385`]). No robot sensor | — | Robot actions on it were dropped |
| **Counter tops (spills, foreign objects)** | Nothing new inside any swept volume of the next sets | O1 / O2 depth diff vs the layout's reference map (2 cm swept voxels exist [S `R19_MOTION_LIBRARY.md:215`]) | Object ≥ 10 mm high detected inside the dilated swept volume [E, matches the 10 mm gate] | — |
| **Floor / aisle / people** | Nobody in reach during hot sets; children or pets at low height; cat on the counter | **R2 rated (#21)**; R1 + O1 / O2 comfort layer (counter-top cat detection [S `r19_hazard_analysis.md:276`]) | R2 detection zone and response time per #21. mmWave 0.1–0.5 s response assumed [S `r19_hazard_analysis.md:158`, E there]. The 0.75 m range resolution [S] is too coarse for anything but "someone near" | Cameras that see people raise **privacy**: process locally, keep no video by default [E] |

---

## 4. World-state check after the user intervenes

**Triggers:**
- E-stop or protective stop;
- a presence pause longer than 5 s [E];
- an app "I touched something" button;
- the fridge or cabinet door sensor;
- an unexplained load-cell change;
- a failed pre-condition.

**Routine `RESCAN` (a verified set itself, from the nearest hub; a sketch for #26 / #32):**
1. **Safe state.** Heat to half or off according to the wok state (R15 policy [S `README_R10.md:532`]). Hold or set down a held load, per #26.
2. **Proprioception.**
   - Joint state against the nearest hub: 0.05° / 0.5 mm [S `R19_MOTION_LIBRARY.md:168`]. If it does not match, run the verified "home" set or let the user jog the arm [S `R19_MOTION_LIBRARY.md:185`].
   - Gripper jaw and FSR: held object as expected?
   - F2 held mass.
3. **Global diff.** O1 and O2 depth against the reference map of the current **layout version**, at 10 mm voxels. Each changed blob is assigned to a station or flagged "unknown object in swept volume of set X".
4. **Station checks**, only for the pre-conditions of the **next N sets** in the routine (§3.3 rows). W1 looks closer where O1 / O2 flagged something.
5. **Fixture moved?**
   - AprilTags on the keyed fixtures (cooker frame, plate stand, lid rack, caddy dock), checked by O1 / W1. If a tag is off by more than 2 mm [E] → **touch-off** of that station with the flange F/T: 10–20 s, ±0.2–0.5 mm [S `R19_TOLERANCE.md:285`].
   - If the cart was pushed: re-dock and touch-off.
6. **Wok and heat.** T1 snapshot (pool or food temperature, wok empty or full), P1 reading, cooker power state.
7. **Seasoning and food inventory.** Load cells, cup presence, cold box present.
8. **User confirmation.** The app shows an annotated overhead image with the diffs, and the user taps OK. Without OK, sets marked "near people" or "hot" do not restart [E].

**World-state schema (fields → confirming sensor → staleness limit)** [E]. Seed for the issue's study 5:

| Field | Confirming sensor | Re-confirm when |
|---|---|---|
| arm at hub H | encoders | every set start |
| held object / mass | jaw + FSR + F2 | every carry start / end |
| wok seated, temperature, fill | P1 + T1 + F2 at set-down | 1 Hz while heat is on |
| heat level | servo position + cooker current (CT) [S `r19_hazard_analysis.md`, heartbeat row] | continuous |
| tool at pad / rest / rack | O1 + W1 | before each fetch |
| cup i present / full / empty | L1 + O1 + F2 | before each pour |
| plate at spot k present / empty / mass | L1 + O1 | before each plating, after each user removal |
| sink clear / water state | O2 + mic | before the sink tip / after the faucet set |
| prep-tray item poses | O1 + W1 | before each pick |
| fridge door angle, cold box | arm joints, W1, O2 | during the fridge set |
| foreign object in swept volume | O1 / O2 diff | after any trigger; before every hot set |
| person in zone | R2 (rated), R1 / O1 (comfort) | continuous |
| layout version / fixture tags | O1 / W1 tags, touch-off | after any trigger; daily |

**Fault injection for the demo (#25 study 5):** remove a cup, turn the faucet off, move a plate by 15 mm, put a mug in the sink. Each must be caught at step 3 or 4.

---

## 5. Cost summary (added perception, beyond the existing thermal + colour item)

| Item | ¥ | Tag |
|---|---|---|
| Hood module additions (mic, VOC, window + purge fan) | 100–400 | [E] |
| Contact probe P1 to the PC (amplifier; probe shared with the limit) | 50–150 extra | [E] |
| Overhead RGB-D ×1–2 | 2,800–5,600 | [S RobotShop ×7.1 E] |
| Wrist camera: RGB-D or RGB | 2,300–3,300, or 120–550 | [S SparkFun / MYBOTSHOP; S `r19_seasoning_cups.md:306`] |
| Load cells at plate stands and the staging pad (3–4) | 40–220 | [S `r19_seasoning_cups.md:303`] |
| mmWave comfort sensor, leak strip, ToF ×2 | 100–200 | [S Tayda; E] |
| AprilTags, colour reference card | < 100 | [E] |
| **Total** | **≈ ¥3.5–9.4k** | [M sum] |

- This sits inside or next to the "Industrial PC, vision, network ¥8,000" allowance [S `r19_system_cost.md:60`]. It overlaps with it, so it is not simply additive.
- The rated people sensor stays in the safety package (#21).

---

## Decisions for the user

1. **Contact probe on the wok.** Accept a spring-loaded thermocouple pressing on the wok's outer wall in the cooker bowl. It serves as the hardware high limit, the preheat sensor and the IR check. Without it, dry-wok and preheat steps run on time only.
2. **Wrist camera.** Fit a wrist RGB-D (about ¥2.3–3.3k) or a cheap RGB camera (¥120–550). Either one needs its own cable along the arm (#36). Without it, food on the tray depends on the overhead view and the V-ribs, and on the FSR for grasp success.
3. **Overhead cameras.** One or two RGB-D under the upper cabinets (¥2.8k each). They see the counter, the sink and part of the aisle. Agree a privacy rule: local processing only and no stored video by default.
4. **Smell.** Accept that "炒香 / 出香味" becomes time + oil temperature. A VOC sensor is only a burn alarm.
5. **Re-scan confirmation.** After any intervention, should the robot always ask for a tap-to-confirm on an annotated photo before restarting hot or near-person sets? Recommended: yes.
6. **Plates.** Plates go only into the guarded stands (2 mm). If the user wants to put plates down freely, the overhead camera must measure them to ±2 mm, which is not yet shown.
7. **Bench budget.** About ¥2k for the IR bench (cooker, wok, Tiny1-C, probes, logger). This is hardware the user would buy. Nothing has been bought.

## Next steps / bench tests

1. **IR bench (§2.5)**, 1–2 weeks: error band per oil mass, set-point, steam, view angle and greased lens; dry-wok ε map; probe lag. Gate: pooled oil p95 ≤ 10 °C.
2. **Real-video cue labels** (with #30): film the robot-free trial from the hood position (colour + thermal) and hand-label colour, 糖色 stage, thickness, boil and smoke onsets. Score simple detectors against the labels, not against rendered truth.
3. **MuJoCo view study** (#25 step 2): place T1, O1, O2 and W1. Ray-cast coverage of the pool ROI, tray channels, plate spots and the sink basin across the stored set states. Measure arm occlusion time per set. Check that the pool reflects the hood, not the hot wall.
4. **V-rib tray pose spread** (#25 step 4): 30 each of tomato, carrot and eggplant. Measure the seated-pose spread with RGB-D, and so the verified grid size and whether ±5 mm / ±5° holds.
5. **Load-cell plating test**: tip real stir-fry onto a stand with a load cell. Correlate the mass shortfall with the counted spill.
6. **Fault-injection demo** of the re-scan (§4).
7. **Hand the matrix to #32 / #26.** Each routine's stop condition names the signal row of §1.2 and its fallback. Each set's monitor names the station row of §3.3. Write it up as `feasibility/perception_matrix.md` (the issue's study 1 output) once the bench numbers exist.

---

### Web sources used (read-only)
- InfiRay Tiny1-C product page (via search summary; the direct fetch failed with a certificate error): https://www.infiray.com/products/tiny1-c-micro-uncooled-ir-camera-sensor-module.html. It gives 256×192 or 160×120, 12 µm, 25 Hz, −15…150 °C high gain / 50…550 °C low gain, ±2 °C or 2 %, lenses 2.0 / 3.2 / 4.3 mm.
- America's Test Kitchen, IR thermometer use (oil 0.95): https://www.americastestkitchen.com/articles/5433-how-to-use-an-infrared-thermometer
- Engineering Toolbox emissivity: https://www.engineeringtoolbox.com/emissivity-coefficients-d_447.html. Neutrium: https://neutrium.net/heat-transfer/total-normal-emissivities-of-selected-materials/
- Thin-film emissivity patent US7075085: https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7075085. Oil-slick ε vs thickness: https://m.researching.cn/articles/OJ5da413dca2de919c
- Exergen tech note 7 (steam): https://www.exergenglobal.com/tech-notes/7-temperature-measurements-in-steaming-environments
- Thermocouple tolerances: https://tcdirect.co.uk/thermocouple-sensors/thermocouple-accuracies.aspx
- Sensirion SGP41: https://sensirion.com/sgp41. E-nose on frying oil (食品科学 2013): https://www.spkx.net.cn/CN/Y2013/V34/I8/236
- Frying sound: https://uwaterloo.ca/news/node/4574; https://patents.google.com/patent/US5180600; https://patents.google.com/patent/CN114811683A/en
- Depth cameras: https://www.sparkfun.com/intel-realsensetm-depth-camera-d405.html; https://www.mybotshop.de/Intel-RealSense-Depth-Camera-D405_1; https://www.robotshop.com/products/orbbec-gemini-336-camera
- ST VL53L1X: https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html. LD2410C: https://www.taydaelectronics.com/ld2410c-24ghz-human-presence-sensor-module.html
- Reflection anecdote: https://www.pizzamaking.com/forum/index.php?msg=651800
