# R19 appliance scan: automatable small appliances for prep, dosing and water (2026-10-14)

**User request:** "尽量去市场上再探索探索可以自动化的各种家用小电器，可以远程操控或者至少是按钮类型，大幅简化".

**Scope:** prep (cutting, chopping, peeling, washing, eggs, rice), seasoning and oil dosing, water. Only products that are **new to the repo**, or new facts about known ones, are covered in depth. Earlier work is cited, not repeated:
- `research/market_r10.md`: the switch-type rule (§2.1), washers (§3), 卓晋 / HLC-300 slicers (§13);
- `research/r19_prep_methods.md`: garlic peeler, abrasive peeler, Rotato, jigs;
- `sim/r10/claude/R19_PREP_AUDIT.md` §5: 2 L chopper, egg cracker, meat slicer;
- `research/r19_seasoning_sizing.md` §3: 添可, 果糖机, aquarium dosers, filling machines;
- `research/r14_storage_market.md`: Decent Scale, auto-loading rice cookers.

**Tags**
- **[S]**: sourced (URL, or repo file:line). "snippet" means a search-result summary, not a product page I read.
- **[E]**: my estimate; the basis is given.
- **ND**: not found.

1688 prices are wholesale list prices read on 2026-10-14 from 1688 market pages (`https://www.1688.com/market/-<GBK hex>.html`); offer IDs are given. Retail is usually higher (`market_r10.md` 13.6). No login, cart, purchase or contact; WebSearch/WebFetch only.

---

## 1. Answer first

Ranked by how much robot work each one removes. Every item still needs a bench or sim check before purchase (§6).

1. **A front/high-spout electric "salad maker" (cone or drum slicer, 200 W class, ¥128–245).**
   - **What it fixes:** the open slicer-output problem in `R19_PREP_STEP4.md` §1 items 3–4. The drawer chain did not close in 12 smoke configurations, and the chute is excluded by geometry: 40 mm of drop against 106–350 mm needed.
   - **How:** this class is built to cut "directly into a bowl, pot or wok", with a high spout for tall containers [S: Philips HR1388, https://www.philips.com.au/c-p/HR1388_80/viva-collection-saladmaker]. The staging pan or a prep bowl goes under the spout and the food falls straight into it. The drawer slide and the catch-tray pull/pour (`ct2p` 38.3 s, `ct2s` 26.8 s) are no longer needed.
   - **Covers:** slices, shreds (土豆丝, carrot, 青瓜) and grating.
   - **Does not cover:** dice or wedges. The 卓晋 / AY-403 stay for those.
2. **A Xiaomi water dispenser whose MIoT spec has a start action and a settable volume.**
   - **Example:** 米家台式净饮机 制冰版 `xiaomi.ysj.cmzb`: `start-out-water` action, cup volume 80–65,535 R/W, target temperature 0–95 °C [S: https://home.miot-spec.com/spec/xiaomi.ysj.cmzb]. `xiaomi.ysj.js15` also has `start-out-water` and a volume of 0–10,000 ml [S: https://home.miot-spec.com/spec/xiaomi.ysj.js15].
   - **What it removes:**
     - the person pre-filling and boiling the kettle (DECISIONS 2026-10-12, `DECISIONS.md:386-390`);
     - the station's pumped water channel (`r19_seasoning_cups.md:67`).
   - **What remains:** the arm holds a jug or cup under the spout, and the robot PC sends "N ml at T °C".
   - **Caution:** most other Xiaomi dispensers checked have **no** start action (§3.2). The user's model decides whether this pick applies (§6, Q1).
3. **Any button-start appliance + a BLE button pusher (SwitchBot Bot class, ≈ US$29–34).**
   - **What it does:** turns a momentary-button appliance (the touch-panel and lost-voltage cases in `market_r10.md` §2.1) into one the robot PC can start, while the arm does other work.
   - **Interface:** community reverse-engineered BLE libraries control it locally with no hub [S: https://python-switchbot-ble.readthedocs.io/ ; https://github.com/devWaves/SwitchBot-MQTT-BLE-ESP32].
   - **Saving:** small per press. It mainly decouples the arm from appliance start times.
4. **A mains 2 L press-top chopper (小熊 QSJ class, ¥106–143), chosen over the cordless "加特林" mini choppers.**
   - It is the audit's chopper (`R19_PREP_AUDIT.md:333-342`), with new facts:
     - the mini choppers (¥6–44) are battery, ~200–500 ml and hold-to-run [S, snippets in §4.3];
     - so the arm must keep pressing for the whole run, and the battery must be charged.
   - A mains unit started by a press-top or a pusher (item 3) is the robot-friendly form.
5. **Watch list, not a pick: a Thermomix-type cooker with MIoT recipe start (米家烹饪机器人 `chunmi.mfcp.c3`).**
   - Its spec exposes `start-cook`, `cancel-cooking`, `pause` and `start-recipe-cook` [S: https://home.miot-spec.com/spec/chunmi.mfcp.c3].
   - One bowl could mince aromatics, beat eggs and mix a 料汁 by one PC call each.
   - **But:** the spec shows no speed, temperature or weight properties, the recipe-command format is unknown, and current sale is ND.

**Searched, with no useful household product found:**
- household rice washers (only commercial 25–100 kg, ¥836–4,670);
- household automatic egg crackers (only commercial centrifugal breakers, ¥130–13,000);
- household "smart seasoning machines" (1688 returns choppers; one announced product, §4.6);
- electronic metered oil pots (only manual press pots, ¥2.5–15);
- sauce dosing machines (filling lines, ¥999–125,000);
- household vacuum marinators (no Chinese household listing found).

Details in §4.

---

## 2. Comparison table

| # | Product (class) | Robot step it removes or simplifies | Control interface | Arm load / unload | Output form | Price (CNY) | Power | 4-person capacity | Cleaning |
|---|---|---|---|---|---|---|---|---|---|
| P1 | Electric salad maker, cone/drum, front high spout (Philips HR1388 / Moulinex DJ755 class; 1688 clones) | Slicer catch drawer/tray + pour into staging pan (`ct2p`/`ct2s`, drawer chain not closed) | Rocker or momentary button (per model, ND); smart plug if latching | Feed the top chute, press the pusher with a keyed printed knob; pan or bowl stands under the spout | **Falls straight into the container under the spout** [S Philips] | 128–245 [S 1688 offers 1006051696748, 1005337229175, 1075422946024, 1085893916013, 1077955515086]; 63–69 for drum types [S 1688 989760830085, 1040601902720] | 200 W [S Philips; S Moulinex https://www.coolblue.be/fr/produit/968587/moulinex-fresh-express-plus-5-en-1-dj755g32.html] | ~0.3–0.5 kg per dish [E, audit masses] in ≤ 2 min runs (Moulinex max 2 min continuous [S, snippet, https://www.qualescegliere.it/robot-da-cucina/moulinex-dj755g-fresh-express/]) | Cones and chute rinse; dishwasher ND |
| P2 | Xiaomi dispenser with `start-out-water` (`xiaomi.ysj.cmzb`, `xiaomi.ysj.js15`) | Kettle pre-fill/boil by the person; jug fills; station water pump | **MIoT action + volume + temperature** (Wi-Fi; local or cloud, §6 Q2) | Hold the jug or cup under the spout; the PC starts it | Water at a set ml and °C into the held vessel | cmzb ¥4,499 list, ¥3,869.1 first sale, ¥3,095.28 after subsidy [S https://www.ithome.com/0/893/728.htm]; js15 ND | cmzb 2,100 W heating, 40–95 °C [S, snippet, ithome 893728] | Tank 6 L (cmzb) [S, snippet]; meal water is 4–8 L (`DECISIONS.md:390`), so it needs a refill or a plumbed model | Self-drain; filters |
| P3 | SwitchBot Bot (BLE button pusher) | Arm button presses at appliance start; lets appliances start while the arm is busy | BLE, community local libraries; official BLE doc for the Bot ND | Stuck on the appliance by the person once | — | US$29 (standard) / US$33.99 (rechargeable) [S https://www.techhive.com/article/633936/switchbot-bot-review.html ; https://finder.techleap.nl/news/feed/switchbot-launches-rechargeable-bot-with-6-month-battery-life-for-43] | Battery (370 mAh rechargeable [S, snippet]) | — | — |
| P4 | Mains 2 L chopper (小熊 QSJ-B03E1 / QSJ-F03X2) | MINCE_RUN (audit: 6 jobs per 3 meals); egg beating | Press-top or rocker (per model, ND); smart plug or P3 | Tip garlic/ginger from the basket into the bowl; lid on; press; lift the bowl out by a printed keyed handle | **Inside its own bowl:** the arm picks the bowl or scrapes it out | ¥106 (B03E1, undated) [S, snippet, https://www.dealmoon.com/en/product/bear-qsj-b03e1-bear-qsj-b03e1-2l/2622130]; ¥143 (F03X2, 2026 review) [S, snippet, https://best.pconline.com.cn/guide/31489.html] | ND | 2 L ≫ 30–50 g garlic per meal [S `R19_PREP_AUDIT.md:112,142`] | Bowl, blade; dishwasher per model ND |
| P5 | Cordless mini chopper (加特林 / JLL7006, USB) | Same as P4, smaller | **Hold-to-run** button [S, snippet, https://www.sayweee.com/en/product/Electric-Garlic-Chopper-Cordless-Chopper-250ml/2957568 class] | Arm must hold the button for the whole run | In its cup | ¥6.1–43.75 [S 1688 926195174919, 994045939368, 626545354692] | 15–60 W claimed [S, snippets] | 200–500 ml [S, snippets] | Cup rinse |
| P6 | 米家烹饪机器人 (Thermomix type) `chunmi.mfcp.c3` | Mince + egg beat + 料汁 mixing by one PC call each | **MIoT:** start/cancel/pause/recipe start; mode 0–10 unlabeled [S spec] | Tip food in, lid on; pour out of the jug | In its jug | ¥3,999 (2020) [S `research/r15_cooking_market.md:180`]; current ND | 1,700 W [S r15:180] | Jug size ND (TM-type 2.2 L [S r15:181]) | Jug + blade |
| P7 | Commercial 洗米机 (water-pressure) | Rice wash (the person does rice: `DECISIONS.md:491-493`) | ND | — | — | ¥836–4,670 [S 1688 829594885430, 1084545484359, 1079678370591] | ND | 25–100 kg | — **Rejected** |
| P8 | Commercial centrifugal egg breaker | Egg cracking (audit: lever cracker) | ND | — | Liquid egg + shells separated | ¥130–13,000 [S 1688 1081881398679, 1063717345413, 1091195369055] | ND | factory/bakery | — **Rejected** (5 eggs per meal [S `R19_PREP_AUDIT.md:128`]) |
| P9 | "Smart" quantitative oil pots | Oil dosing | Manual press/squeeze only | — | — | ¥2.5–15.1 [S 1688 651239995156, 1058047114103] | none | — | — **No electronic product found** |

---

## 3. Per-product notes

### 3.1 P1: front-spout electric salad maker (cone/drum)
- **Facts.**
  - **Philips HR1388:** 200 W; 5–6 discs (coarse and fine slicing, julienne, XL julienne); cuts "directly into a bowl, pot or wok"; high spout for taller containers; 225 × 225 × 315 mm, 2.27 kg packed. Discontinued (2013 model) [S https://www.philips.com.au/c-p/HR1388_80/viva-collection-saladmaker ; Galaxus listing, snippet].
  - **Moulinex Fresh Express DJ755:** 200 W, 5 cones, about 27.5 × 19.5 × 24.6 cm, 1.45 kg [S coolblue, above]. Maximum 2 min continuous use [S, snippet, qualescegliere].
  - **Chinese clones on 1688:** sold as 跨境电动沙拉机 / 6合1 / 7合1, ¥128–245, some with 欧规/英规 plugs (e.g. offer 959281708241, ¥203) [S 1688 电动沙拉机 page]. No wattage or spout height in the titles (ND).
- **Robot steps [E].**
  1. Place the staging pan (r 70 × 85 mm, `R19_PREP_STEP4.md` §3.1) or a prep bowl under the spout.
  2. Drop the pieces into the top chute (the existing chute-drop pattern of the carrot set).
  3. Press the pusher with a printed keyed knob, ~10–30 N [E; no source for the pushing force].
  4. Repeat per batch.
  5. Pick the filled pan. No drawer, no tray pour.
- **Why it ranks first [E].**
  - It removes the whole "get the cut food out of the slicer into a container the arm can carry" problem. In step 4 that problem cost 12 failed drawer chains and an excluded chute.
  - If the spout clears an 85 mm pan, the pan can be filled directly. That is plausible, given the "high spout for taller containers" claim, but the height is ND.
- **Limits.**
  - Cone or drum geometry: slices and shreds only, no dice or wedges [S disc lists above].
  - Feed-tube size ND for the clones. Potato (65 × 70 mm, `market_r10.md:76`) may need halving first.
  - The 2 min duty limit fits a 300–500 g dish if the feed is quick [E].
  - Cut quality for 土豆丝 (target thickness ND in the repo) is unproven.
- **Placement [E].** It must sit where the counter strip has no upper cabinet over the pan. Re-screen it with `r19prep4_screen.py` like the drawer.
- **Safety.** An open feed chute with a spinning cone is the "no exposed powered blade" case (`DECISIONS.md:15`). The pusher interlock is ND for the clones. Philips/Moulinex-class units run only while the button is held or the pusher is down (ND, verify).

### 3.2 P2: Xiaomi water dispensers: which ones are robot-commandable
MIoT specs read on 2026-10-14:

| Spec ID / product | Start action | Volume | Temperature | Verdict |
|---|---|---|---|---|
| `xiaomi.ysj.cmzb` 米家台式净饮机 制冰版 | **`start-out-water`** | `out-water-cup` 80–65,535 R/W | target 0–95 R/W | **Commandable** [S https://home.miot-spec.com/spec/xiaomi.ysj.cmzb] |
| `xiaomi.ysj.js15` (name ND) | **`start-out-water`** | `out-water-volume` 0–10,000 ml R/W; `out-water-time` 10 s or unlimited | target 16–32 (odd; likely the cold side [E]) | **Commandable** [S https://home.miot-spec.com/spec/xiaomi.ysj.js15] |
| `xiaomi.ysj.ymmax` (米家即热饮水机 Max 制冰版, ¥1,999, launched 2026-06-08 [S https://www.ithome.com/0/961/262.htm]) | none; `on` bool R/W (meaning ND) | `out-water-volume` 0–10,000 ml R/W | target −40–100 R/W | **Maybe:** a test is needed to see whether writing `on` dispenses [S https://home.miot-spec.com/spec/xiaomi.ysj.ymmax] |
| `xiaomi.ysj.v2` Smart Water Dispenser (Hot and Cold), sold in the EU as BHR8992EU, 3 L, 2,250 W | none | `set-flow` per mode | `set-temp` per mode | **Button type:** presets via the app, then the arm presses the dispense button once [S https://home.miot-spec.com/spec/xiaomi.ysj.v2 ; https://www.inserv.lv/en/products/187757/smart-water-dispenser-smart-water-dispenser-eu-2250-w-3-l-plastic-body-white-bhr8992eu-xiaomi] |
| `xiaomi.ysj.tsj15` 凉白开, `xiaomi.ysj.tsa2p` NFC | none | none | target R/W | Not commandable for volume [S spec pages] |
| `yunmi.ysj.x12` | none (drain only) | cup-size list | levels | Button type [S https://home.miot-spec.com/spec/yunmi.ysj.x12] |

- **Flow rate: ND.**
  - A heater-limited estimate for an instant-heat unit [E]: 2,100 W ÷ (4.186 J/g·K × 65 K, from 30 → 95 °C) ≈ 7.7 g/s ≈ **0.46 L/min** of near-boiling water.
  - At that rate, 1 L of blanching water takes ~2.2 min unattended and a 2 L soup base ~4.3 min.
  - Room-temperature water should be much faster (pump-limited, ND).
- **What it changes [E].**
  - The kettle step ("filled and boiled before cooking" by the person) and the "arm fills the jug at the tap" option are both replaced by a metered, heated fill. The arm only holds the vessel.
  - Small water doses (60–130 ml per meal into 料汁 cups, `r19_seasoning_cups.md:285`) could come straight from the dispenser, if its 80 ml minimum cup (cmzb) and accuracy are good enough. Accuracy ND.
- **Limits.**
  - The tank is 6 L (cmzb, snippet). The meal uses 4–8 L. Either the person refills it once per meal, or a plumbed (管线机) model is used: `xiaomi.ysj.gxj` 米家即热管线机 exists [S https://home.miot-spec.com/s/xiaomi.ysj], spec not read.
  - The spout height decides which vessels fit (ND).

### 3.3 P3: BLE button pusher
- **Facts.**
  - It presses or pulls a button or rocker [S, snippet, techhive/techradar reviews].
  - Local BLE control without a hub via community libraries, e.g. `python-switchbot-ble`, "reverse engineered … without a Hub", which also handles password-protected bots [S https://python-switchbot-ble.readthedocs.io/]. An ESP32 MQTT bridge also exists [S GitHub above].
  - No official SwitchBot BLE spec for the Bot was found (ND).
  - Press force ND.
- **Use [E].**
  - Appliances with momentary buttons and lost-voltage restart: HLC-300, Sammic, and touch-panel washers (`market_r10.md:84-86`).
  - P2 models without a start action (`v2`, `x12`): set the preset in the app once, and the pusher presses "dispense".
- **Limit.** A capacitive touch panel may not register a plastic tip (ND). The arm press stays the fallback.

### 3.4 P4 / P5: choppers
- **P4.** The audit's choice (`R19_PREP_AUDIT.md:333-342`) stands.
  - New prices: 小熊 QSJ-B03E1 2 L ¥106 [S, snippet, dealmoon]; QSJ-F03X2 ¥143 (2026) [S, snippet, pconline].
  - Power and switch type: ND. Check the product page for press-top vs rocker.
- **P5 is not recommended for the robot [E].** The hold-to-run button [S, snippet] ties the arm up for the whole mince. The USB battery adds a charging chore. The cups are small.

### 3.5 P6: MIoT Thermomix-type cookers
- **米家烹饪机器人 `chunmi.mfcp.c3`:** actions start/cancel/pause/start-recipe-cook; writable `mode` 0–10 (unlabelled), `on`; read-only `left-time`. No speed, temperature, weight or lid properties [S spec].
- **博世 Cookit `bshcn.mfcp.555cwc`:** start/stop/pause/recipe; modes guided/automatic/manual; no speed or weight [S https://home.miot-spec.com/spec/bshcn.mfcp.555cwc].
- **米家 blenders, e.g. `xiaomi.juicer.cms1`:** modes are soy milk, pulp, juice, clean, warm. **No chop or mince mode** [S https://home.miot-spec.com/spec/xiaomi.juicer.cms1]. Not useful for prep.
- **Verdict [E].** It only becomes useful if a stored "chop 5 s at speed 5" recipe can be written and started from the PC. Until that is shown, the P4 chopper + P3 pusher is cheaper and simpler.

### 3.6 Seasoning and oil dispensers (extends `r19_seasoning_sizing.md` §3)
- **1688 "智能调料机" (2026-10-14):** the top 20 results are garlic choppers and meat grinders (¥4.66–235). One commercial "智能" marinating machine costs ¥2,915.27 (offer 1075149493730). **No multi-channel household seasoning dispenser** [S https://www.1688.com/market/-D6C7C4DCB5F7C1CFBBFA.html].
- **1688 "电子定量油壶":** only manual press, squeeze or spray pots, ¥2.52–15.1. The one "smart quantitative" pot (¥15.1, offer 651239995156) does not say it is electronic [S https://www.1688.com/market/-B5E7D7D3B6A8C1BFD3CDBAF8.html].
- **1688 "酱料定量机":** packaging and filling machines, ¥999–125,000, plus a 10–100 g powder doser at ¥3,000 (offer 1070148555848) [S https://www.1688.com/market/-BDB4C1CFB6A8C1BFBBFA.html].
- **SauceIN S1 (Chongqing SauceIN Technology, founded 2025):**
  - an announced "intelligent seasoning machine" with 5 liquid + 4 solid base seasonings, a camera, refrigeration, UV, and "pipe-free" transfer;
  - output form, control, price and availability are not stated [S https://english.liangjiang.gov.cn/2026-06/08/c_1189039.htm];
  - **watch only**: its base seasonings are its own capsules, not the cook's real bottles (DECISIONS: real ingredients).
- **Conclusion:** unchanged from `r19_seasoning_sizing.md:173` and `DECISIONS.md:512`. No bought dispenser fits; the self-built pump station stays.

### 3.7 Rice (the person does rice, `DECISIONS.md:491-493`)
- **Commercial 洗米机:** 25–100 kg water-pressure units, ¥836–4,670 [S https://www.1688.com/market/-CFB4C3D7BBFA.html]. Not household.
- **New app cooker:** 米家智能变压 IH 4L, ¥1,999, 1,390 W, app remote, cloud recipes. **No rice/water auto-loading** [S, snippet, https://www.ithome.com/0/883/148.htm].
- **Auto-loading cookers** (Panasonic SR-AX1, Midea Royce, 饭小二) are already in `r14_storage_market.md:246-249`. Nothing new to add.

### 3.8 Eggs
- **Household automatic crackers:** none found. Patents and prototypes exist; commercial centrifugal breakers are bakery/factory units [S 1688 磕蛋机 page https://www.1688.com/market/-BFC4B5B0BBFA.html ; patent https://patents.justia.com/patent/20240164585].
- **1688 "自动打蛋器":** manual or semi-automatic whisks and handheld mixers, ¥1.6–28.7 [S https://www.1688.com/market/-D7D4B6AFB4F2B5B0C6F7.html].
- **The audit plan is unchanged:** lever cracker + chopper pulse (`R19_PREP_AUDIT.md:348-354`).

### 3.9 Washers, peelers, scales: already covered
- **Washers:** weak cleaning evidence and touch panels (`market_r10.md` §3, §2.1). P3 could start a touch-panel washer only if a physical button exists.
- **Peelers:** `r19_prep_methods.md` §3.
- **Scales:** Decent Scale BLE API (`r14_storage_market.md:198`). Nothing new found that would change those choices.

---

## 4. Search log (what was looked for and where)

| Category | Where searched | Result |
|---|---|---|
| 电动切菜器 / 电动切菜机家用 | 1688 market pages | Drum slicers ¥58–98 (offers 1072437798646, 974163874432, 1005207995533); 加特林 mini choppers ¥11.5–25; meat-grinder combos ¥170–419 |
| 电动沙拉机 | 1688 | 15 listings ¥128–375 (§3.1) |
| Salad-maker specs | Philips AU page, Coolblue, Galaxus, QualeScegliere | §3.1 |
| Water-dispenser MIoT specs | home.miot-spec.com: `/s/dispenser` (46 models), 7 spec pages read | §3.2 |
| Food-processor / cooker MIoT specs | miot-spec `/s/料理` (8), `/s/烹饪` (2) | §3.5 |
| Button pusher | python-switchbot-ble docs, GitHub, reviews | §3.3 |
| 智能调料机, 电子定量油壶, 酱料定量机 | 1688 | §3.6 |
| 洗米机, 磕蛋机, 自动打蛋器 | 1688 | §3.7–3.8 |
| Vacuum marinator | web | No Chinese household listing. One overseas 32 L, 350 W, 0–99 min unit [S, snippet, https://www.walmart.com/c/kp/marinating-machine]. Not pursued: the marinades are 2 per 3 meals (`R19_PREP_AUDIT.md:33`) |

---

## 5. How the prep flow changes (if P1–P4 pass their checks)

**Before** (`R19_PREP_STEP4.md`, `R19_PREP_T2L.md`):
1. Slicer → catch tray or drawer bowl.
2. The arm pulls the tray (15 cm pull past the blade plate) and pours it into the pan on the folded cradle (`ct2s`, 26.8 s).
3. Water: the person fills and boils the kettle; the arm pours from the kettle and jug (6–10 uses, 2–4 min per meal, `DECISIONS.md:390`).
4. Mince: chopper bowl, the arm presses or holds.

**After [E]:**
1. **Cut to container.** The pan (or a prep bowl) stands under the P1 spout. Feed + push. The filled pan goes straight onto the cradle.
   - Saves the tray/drawer extraction set per batch.
   - Removes the drawer/chute design branch entirely.
   - New set needed: "pan under spout" (place and pick).
2. **Water on demand.** Per water use: the arm holds the jug or pot-fill vessel under P2; the PC calls `start-out-water` with volume and temperature; the arm waits (or does other work, if a parked-vessel spot exists) and carries the vessel.
   - Removes the person's kettle chore and the boiling wait on the hob.
   - Adds ~1–4 min of unattended dispense time per meal at hot settings [E, 0.46 L/min estimate].
3. **Button starts off the arm.** P3 pushers on P4 and on any momentary-button appliance. The arm loads the appliance, leaves, and the PC starts it.
4. **Unchanged:** the lever cutter (wedges, sections), the 卓晋 dice, the peelers, the garlic peeler, the egg lever cracker, the seasoning pump station, and rice (the person).

**Net [E].** For the cut-to-container change, the step-4 numbers suggest roughly **25–40 s saved per slicer batch** (the `ct2s`/`ct2p` set times), plus the drawer branch cost. Water saves the person's pre-cook kettle step, and arm time is about neutral. These are estimates, not sim results.

---

## 6. Open questions / what to verify

1. **Q1 (user): which 小米饮水机 do you have?** Its model ID, from Mi Home device info, decides P2:
   - `cmzb` / `js15`: commandable;
   - `ymmax`: test whether `on` dispenses;
   - others: button press (arm or P3).
   Also needed: its spout height and whether it is plumbed or tank-fed.
2. **Q2: local vs cloud MIoT.**
   - Check whether `start-out-water` works over the local miio protocol with the device token (python-miio / hass-xiaomi-miot, https://github.com/dofine/hass-xiaomi-miot) or only through the cloud.
   - Check whether a remote dispense needs a cup-detection or child-lock override. `cmzb` has a hot-water unlock rule; `ymmax` child-lock modes 0–3 [S spec].
   - Safety: hot water ≥ 50 °C started by software is a scald hazard. It falls under the "heat armed" rules (#19, #22).
3. **P1 bench:**
   - spout height (does an 85 mm pan or a Ø170 × 75 mm bowl fit under it?);
   - feed-tube size;
   - pusher force;
   - switch type (latching rocker, or hold-to-run);
   - lid/pusher interlock;
   - cut quality on potato shreds, carrot, cucumber;
   - throughput per 300–500 g against the 2 min duty limit;
   - scatter outside the container.
   Then a sim screen of its spot (`r19prep4_screen.py`, new MODE).
4. **P1 plug and SAFETY Mark.**
   - A 英规 (UK 3-pin) clone physically suits SG sockets [E]. GB plugs do not [S `research/r19_sg_compliance.md:20`].
   - The clones carry no SAFETY Mark; imports for own use are probably not a CPSR offence, but insurance terms apply [S `research/r19_sg_compliance.md:18-21`].
   - An SG-retail Philips/Moulinex-class unit is preferable if one is still sold (ND).
5. **P3:** press force on the target buttons; whether it works on the dispenser's capacitive keys; BLE range from the robot PC on the cart.
6. **P4:** model with a mains press-top start; restart behaviour after power loss; garlic residue in the bowl (open in the audit).
7. **P6:** recipe-command format, and whether a custom chop step can be stored. Only worth testing if the user already owns one.
8. **Not verified anywhere:** all 1688 specs (offer pages not opened), the dispenser flow rate and volume accuracy, the SauceIN S1's real output form.
