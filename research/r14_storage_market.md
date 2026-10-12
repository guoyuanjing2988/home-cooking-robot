# R14 — Storage and dosing market scan: seasonings, staples, fridge access

Date: 2026-10-11. Read-only web research only: no login, cart, purchase or seller contact.

**Context.** One UR5e on a docked cart in a small L-shaped home kitchen (probably Singapore, humid), with a gas hob. Upper cabinets are 33–35 cm deep, with a 50–55 cm gap above a 0.85–0.9 m counter. The robot cooks Chinese home dishes (Wang Gang recipes) end to end.

**Tags**

| Tag | Meaning |
|---|---|
| **[M]** | Read in the primary source (maker page, manual, datasheet, standard, paper, patent). |
| **[O]** | Secondary source (news, review, reseller, forum). |
| **[O, snip]** | Seen only in a search-result snippet. Weaker. |
| **est.** | My own calculation or engineering judgement. |

**Prices.** Prices are in the source currency. CNY conversions are marked est. and use the R10 rates (1 USD≈7.1, 1 SGD≈5.5, 1 JPY≈0.048 CNY).

**Coverage limits (read first)**
- **Search budget.** The session's shared WebSearch budget (200 calls) ran out about halfway through. After that, only known pages were fetched directly. Several brands were never searched; they are listed in §7.
- **Domestic prices.** I tried to read a Taobao search page through Claude in Chrome, but the extension's site-permission prompt timed out because nobody was there to click Allow. JD, Tmall and 1688 were not used (login or captcha). **So almost no domestic marketplace (CNY) prices were collected.** The CNY figures below come from maker pages, smzdm, 36kr or news.

---

## 0. Bottom line

| Need | Most useful concrete option found | Key numbers | Price | Confidence |
|---|---|---|---|---|
| Thin liquids: light/dark soy, vinegar, cooking wine, sesame oil, cooking oil | Bank of stepper **peristaltic pumps** (Kamoer class), food-grade silicone or BPT tube | Kamoer KCS PLUS 15–80 ml/min, flow accuracy **±10% open loop**. KCM up to 600 ml/min. Viscosities are only 1–70 mPa·s | ≈€50/pump (KCM) | High. Calibrate each pump, or close the loop by weight |
| Oyster sauce | Peristaltic pump with large-bore (≈4.8 mm ID), thick-wall BPT/Norprene tube, run slowly | Oyster sauce is shear-thinning, ≈0.15–1.5 Pa·s at 10 s⁻¹ (est. from power-law fits). Silicone tube is rated to ≈8,000 cP, BPT to ≈10,000 cP | as above | Medium. Above ≈100 cP, open-loop accuracy degrades |
| Chunky pastes: 豆瓣酱, 甜面酱 | (a) Lead-screw **syringe/cartridge extruder** with ≥6–8 mm outlet, **or** (b) the UR5e squeezes a 16 oz squeeze bottle. Kitchen Artist did this with a **UR5e + WSG50** on 25 liquids from 1 to 70,000 cP | Kitchen Artist flow-rate prediction error 0.096 ml/s. ViscoTec vipura hygienic pump passes 20 mm lumps but is industrial | DIY (est.) | Medium |
| 火锅底料 (solid at room temperature) | Pre-portioned cubes picked by the arm | Not pumpable | — | High (est.) |
| Salt, sugar | **Dissolve them (brine, syrup) and pump as liquids.** This is what the Tineco 食万 home machine does. It avoids caking at Singapore humidity | Saturated NaCl is 26.4 wt%, so 3 g salt ≈ 11 g brine (≈8 g water) (est.) | — | High |
| MSG, chicken powder, white pepper, five-spice | 4–6 **sealed auger canisters** with agitator, desiccant and shutter. **Dose by weight** into a cup on a 0.3–1 kg load cell: fast feed, then a slow trickle | Volumetric augers alone give ±1–5% (CV 4–6%). Load cell + HX711 on a small cell ≈0.01–0.05 g rms (est.) | DIY. The smallest market auger filler is US$3,400 / 30 kg / ±3–5% | Medium. Build, don't buy |
| Starch (勾芡, 上浆) | Pump it as **水淀粉 slurry**, stirring before each dose, or use an auger as above | Starch does not dissolve in cold water, so the slurry settles. No settling-time data found | — | Medium |
| Whole spices: 花椒, 八角, 干辣椒, 桂皮, 香叶 | **The user fills a weekly kit of lidded cups; the arm tips them.** A vibratory feeder only makes sense for 花椒 | Recipes count these in pieces, not 0.1 g | Cups only | High (est.) |
| Weighing | Dose cup on a 0.3–1 kg cell (HX711), plus a pan scale for liquids and vegetables. Off-the-shelf with open API: **Decent Scale** | Decent: 2 kg / 0.1 g, BLE API at 10 Hz. A&D EK-6100i: 6 kg / 0.1 g, RS-232C | EK-6100i ≈US$351 (eBay) | High |
| Rice | (a) **Panasonic SR-AX1**: augers wash-free rice and pumps water by itself, app start; **or** (b) a mechanical **150 g/press** rice dispenser pressed N times by the arm, plus a Mi Home cooker whose MIoT spec exposes **Start Cook** | SR-AX1: 2 kg rice tank, 600 ml water tank, 0.5–2合, 176×336×336 mm | SR-AX1 ≈¥46,000 JPY (≈CNY 2,200 est.), Japan only (100 V). Press bins ≈CNY 42–51 | Medium |
| Cooking oil, bulk | 5 L jug in a dark lower cabinet + peristaltic or gear pump to the pan | Oils ≈35–70 mPa·s. Shelf life (Singapore HealthHub): peanut 2 yr, soy 1 yr, sesame 6 mo | pumps as above | High |
| Deep-fry oil | **Tefal Oleoclean**: drains through a filter into a storage box once cool | Compact: 2 L oil. Pro: 3.5 L. Discard at TPC >27% (HK, China) | — | Medium |
| Fridge | **Under-counter full-extension drawer fridge** (F&P CoolDrawer RB9064S1, SG) + OPEX1 knock/push-to-open accessory | 855 W × 640 H × 557 D mm, 104 L gross / 80 L net, 5 modes. Measured door-seal breakaway is 27–116 N, above the UR5e F/T range of ±50 N | **SGD 5,000** + OPEX1 NZD 599 | Medium–high |
| Staging time out of fridge | Fetch just in time. Cap raw meat or seafood at **≤1 h** at 30–32 °C ambient | USDA: 2 h, or 1 h above 32.2 °C. FSANZ 2 h/4 h rule (cumulative). SFA danger zone 5–60 °C | — | High |

**Main conclusion.** No market product covers the job. Home "seasoning machines" are either liquid-only cooking pots (Tineco) or powder pods (Posha, Spicerr). Commercial seasoning dosers (Huayi 8 liquid + 6 powder; Botinkit up to 16 seasonings) don't publish size or API, and integrated wok robots weigh about 180 kg.

The workable path is a **DIY bank**:
- 8–10 peristaltic liquid channels (salt and sugar dissolved);
- 1–2 paste extruders;
- 4–6 sealed powder augers;
- a load cell;
- a weekly whole-spice kit;
- a drawer fridge with assisted opening.

---

## 1. Automatic seasoning dispensers on the market

### 1.1 Home products

| Product | Liquid / powder / paste channels | Accuracy | Capacity | Refill & cleaning | Interface | Size / weight | Price | Src |
|---|---|---|---|---|---|---|---|---|
| Tineco 添可 食万 3.0 | 5 liquid: water, oil, **salt water**, light soy, dark soy. No powder, no paste | 1 g (scale in the base) | Water 800 ml, oil 400 ml, 3 × 200 ml | Rotating removable box; machine self-cleans | Brand app only; no open API found | n/a | ¥6,090 (smzdm, 2022-04) | [O] https://zhongce.sina.com.cn/iframe/article/view/133609/ ; [O] https://post.smzdm.com/p/agqkwdr7/ |
| Tineco 食万 3.0 Pro | 8 liquid: adds cooking wine, vinegar, **sugar water**. One source lists water 1,000 ml + 7 × 200 ml | "Weighing + pump dual sensing"; claims "0.02%"; 10 kg scale | see left | 30 s steam clean | App. Uses QR-coded pre-cut ingredient packs (食万净菜) | n/a | ¥3,990 (date not stated) | [O] https://cn.chinadaily.com.cn/a/202209/28/WS6333d809a310817f312f02be.html ; [O] https://www.pingwest.com/a/269931 |
| 饭来 cooking machine | Reported 2 solid + 3 liquid boxes, plus water and oil bottles (unverified) | — | — | — | App, cloud recipes | — | ¥2,199 (one model) | [O] https://post.smzdm.com/p/ag89dwgm/ |
| Posha (ex-Nymble), US | 20 refillable **powder** spice pods on a carousel; 1 oil-and-water container; 4 ingredient containers | Not published | — | Pods refillable; containers dishwasher-safe | Touchscreen and app; needs internet; no API | 405 × 530 × 454 mm, 20 kg | US$1,750 ($1,500 promo) + $14.95/mo | [M] https://www.posha.com/private-chef ; [M] https://posha.com/how-posha-works |
| Nosh One (Euphotic Labs, India) | 8 spice containers × 100 cc; water 1.7 L; oil; 5 ingredient slots × 2.5 L | Spice "1/4 tsp (1.25 ml)"; liquids "1 tsp (5 ml)" | — | — | — | 523 W × 424 H × 565 D mm, 26 kg | $1,499 pledge | [O] https://newatlas.com/around-the-home/nosh-one-ai-robotic-chef/ ; patent [M] https://patents.google.com/patent/US12075933 |
| Spicerr (handheld) | 6 powder capsules | Teaspoon steps on a touchscreen | 8–12 tsp per capsule | Proprietary capsules, $2.50 each | Bluetooth app | — | $128–180 (Kickstarter, 2025-03) | [O] https://newatlas.com/around-the-home/smart-spice-dispenser/ |
| TasteTro (2018–19) | 20 sealed RFID powder pods | tsp/tbsp steps | — | Not refillable | BT + touchscreen | — | $299 pre-order | [O] https://thespoon.tech/tastetro-spice-connected-dispenser-launches-indiegogo-campaign |
| Press-button salt/spice bottle | 1 powder | 0.5 g per press | 170 g | Manual | Mechanical button (the arm could press it) | — | $12.99 | [O] https://techfixai.com/best-smart-spice-dispensers-for-cooking-enthusiasts/ |
| KitchenArt Select-A-Spice | 12 powders | ¼ tsp per twist | — | Manual | Mechanical dial | Ø 9.5" × 6" | $39.99 | [O] same URL |

### 1.2 Commercial standalone seasoning dosers (配料机 / 调料机)

| Product | Channels | Accuracy | Capacity / speed | Cleaning | Interface | Price | Src |
|---|---|---|---|---|---|---|---|
| Shandong Huayi 团餐配料机 HY-DISP-ROBOT-001 | 10 liquid / 6 powder standard; **paste module built to order** | "克级" (gram level) | 3,000–5,000 servings/h | — | Touchscreen + PC + phone; no API or serial port documented | **¥28,000 list**; rental deposit ¥13,800 + ¥500/mo software | [M] https://zycfcy.com/products/group-catering-dosing-machine |
| Huayi 小餐饮配料机 (A) -005 | **8 liquid / 6 powder** | — | ≈3 斤 (1.5 kg) per box; 2–3 s per portion | Suck-back (回抽) line cleaning; wipe daily | — | Quote only | [M] https://zycfcy.com/products/automatic-dosing-machine |
| Huayi (C) -003 | Liquid hopper (with optional stirring) + powder hopper | **0.1 g** (best published) | 3 s per portion; 90 recipes | — | — | Quote only | [M] https://zycfcy.com/products/small-catering-dosing-machine |
| Huayi -002 (factory) | Liquids, powders, **pastes**, compound sauces; configured per project | — | — | — | — | Quote only | [M] https://zycfcy.com/products/industrial-prepared-food-dosing-machine |
| Shenzhen Hongbo 调料机器人 | Powder + liquid | — | — | Stainless | **One-touch infrared trigger** | — | [M] https://www.szhbzc.com/pengjiagongxilie/32-25.html |
| Server Products IxD Multi+ (US) | Up to 6 pumpable condiments | — | 1.5 or 3 gal pouches | Clean-in-place | **Push button**, <1 s | — | [M] https://server-products.com/Multi |

Sizes are not published for any of these. A lead I could not verify: 长膳智能 XA-460 is said to have "11 liquid + 4 powder" channels (search summary only).

### 1.3 Findings
- **No product publishes an open API, SDK, serial or RS485 interface.** Units that a robot could still trigger: Hongbo (IR one-touch), Server (push button), press bottles, Posha/Tineco only through their own apps. Ask Huayi whether its PC control exposes commands.
- **Only commercial equipment doses paste:** Botinkit OMNI (oyster sauce, 沙茶酱, ketchup, honey), Huayi -002, Huayi -001 option and Server (pumpable condiments).
- **Home machines do liquids only.** Tineco dissolves salt and sugar into solutions. Home spice gadgets do dry powder in teaspoon steps.
- **Published accuracy:**
  - Huayi (C): 0.1 g.
  - Tineco: 1 g, from a scale under the pot.
  - Press bottle: 0.5 g per press.
  - Nosh: 1.25 ml for spices, 5 ml for liquids.
  - Most commercial makers publish none.
- **Lead not followed up:** milk-tea **果糖机** (multi-channel syrup dosers) are a mass-market Chinese product that could serve as a ready-made liquid bank. I could not search them (budget).

---

## 2. Components

### 2.1 Liquid pumps and valves

| Item | Specs | Src |
|---|---|---|
| Kamoer KCM 12/24 V stepper peristaltic | Up to 600 ml/min at 24 V; tube 3.2 × 6.4 mm; ≤60 °C; sold as handling "air bubbles or granular substances"; **€50.38** | [O] https://funduino.com/en/products/kamoer-kcm-peristaltikpumpe-dosierpumpe-12v-24v-0-160ml-min-schrittmotor |
| Kamoer KCS PLUS stepper | 15–80 ml/min, **flow accuracy ±10%**. Tube life: silicone 200 h, BPT 1,000 h. Motor 6,000 h | [O, snip] https://st.robu.in/product/kamoer-kcs-plus-12v-stepper-motor-peristaltic-pump-15ml-min-8-rollers |
| Kamoer K-F01A dosing pump | Volume accuracy <±2% | [O, snip] (page not recorded) |
| Kamoer DIP1500 | ≤1,500 ml/min, 0.1–400 rpm, silicone tube 7.9 × 11.1 mm | [O] https://hybridatelier.uta.edu/equipment/150-kamoer-dip1500-peristaltic-pump- |
| Longer 兰格 BT300-2J / BT600-2J (lab) | 0.06–1,100 / 0.06–2,200 ml/min; €1,201–1,657 | [O] https://darwin-microfluidics.com/longer/ |
| FK600 (China, food lines) | Spice-oil dosing, error <±2% | [O] https://m.tech.china.com/articles/20260121/202601211800466.html |
| Tubing vs viscosity (Microlit) | Silicone ≈8,000 cP max, PharMed BPT ≈10,000 cP. Above 1,000 cP use wall ≥1.6 mm; ≈4.8 mm ID for viscous fluids | [O] https://www.microlit.com/how-viscosity-impacts-tubing-choice-in-peristaltic-pumps/ |
| 3P innovation white paper | "Once fluids surpass 100 cP, elastic recovery in tubing degrades"; closed-loop servo holds accuracy up to 2,000 cP | [O] https://www.pharmaceuticalonline.com/doc/expanding-the-viscosity-limits-of-peristaltic-dosing-0001 |
| Boyser food hose pumps (Castle Pumps) | 8,000–30,000 cP; solids 8–55 mm; sauces and purées | [O] https://castlepumps.com/pump-type/peristaltic-pumps/food-grade-peristaltic-pumps |
| DIY / bartender robots | ±0.6 ml (6.4 mm tube) to ±0.2 ml (3.2 mm tube); calibrate by a timed run | [O, snip] SparkFun 12915 (now 404); [O] https://wiki.dfrobot.com/dfr1261/docs/25074 |
| KNF SIMDOS 02/10 diaphragm | 0.03–20 / 1–100 ml/min; ±2%, repeatability ±1%; **max 150 cSt** (no oyster sauce) | [O] https://technology-products.dksh.com/product/knf-diaphragm-liquid-dosing-vacuum-pump |
| HNP micro annular gear pump | 4.8–72 ml/min; **0.3–100 mPa·s**; family claims <1% | [O, snip] https://www.designworldonline.com/microdrives-help-gear-pumps-deliver-precise-doses/ |
| Verdergear VGS870 gear pump | 1–2,000 mPa·s; 316L / PEEK / PTFE; flow far above kitchen needs | [M] https://verderliquids.com/fileadmin/user_upload/Website_documents_2016/Verdergear/Documents/Documents_EN/Technosheet_Verdergear_VGS870_24_V_INT.pdf |
| Takasago PK-0802 pinch valve | Silicone tube 6 × 8 mm; NC/NO; 12/24 VDC; 10 W; **0–20 kPa** (enough for gravity head) | [M] https://takasago-fluidics.com/products/pk-2-5 |

### 2.2 Paste dispensing

| Item | Specs | Src |
|---|---|---|
| ViscoTec preeflow eco-PEN 300/330/450/600 (progressive cavity) | Up to **1.4–16 ml/min** (eco-PEN600); ±1%; "watery to pasty"; ≤20 bar. Too slow for cooking doses: ≈40 s for 10 ml (est.) | [M] https://www.viscotec.de/media/preeflow-brochure-en-2019-web.pdf |
| ViscoTec vipura-PUMP 10T (hygienic) | Passes **lumps ≤20 mm**; 20–200 ml+ doses; BBQ and teriyaki examples | [O] https://making.com/equipment/dosing-and-filling-pump-for-liquids-and-pastes |
| Pneumatic piston filler FMSA10 | 5–50 ml, ±1%, 10 L hopper, 0.4–0.6 MPa air, ≈€165–177; listed "**without particulate**" | [O, snip] https://www.ggmgastro.com/en-gb-eur/commercial-pneumatic-liquid-und-paste-filling-machine-with-foot-pedal-for-liquids-und-pastes-5-50ml-fmsa10 |
| ZONESUN ZS-YTCP12V ceramic plunger | 1–50 ml, ≤±0.5%, 20 L hopper, $2,680 | [M] https://zonesunautopack.com/products/zs-ytcp12v-pneumatic-syringe-ceramic-plunger-pump-liquid-paste-filling-machine |
| Natural Machines Foodini (capsule extruder) | 5 × 100 ml stainless capsules; nozzles 0.8/1.5/4 mm; heats to 90 °C (could melt 火锅底料); sold out | [M] https://www.naturalmachines.com/foodini |
| **Kitchen Artist (CMU), UR5e + WSG50 squeezing a 16 oz bottle** | 25 liquids, 1–70,000 cP (water to toothpaste). Flow-rate prediction error 0.096 ml/s. Stroke-thickness error 3.06 mm (28.8%) | [M] https://arxiv.org/html/2311.12185 |
| Server condiment pump (manual piston) | 1–2 oz per stroke in ⅛ oz steps; model 87630 for thick condiments | [O, snip] https://shop.boelter.com/server-87630-condiment-pump-for-1-6-size-6-deep-pan.html |

### 2.3 Viscosity data (≈20–25 °C)

| Seasoning | Value | Src |
|---|---|---|
| Soy sauce (shoyu) | Newtonian. η = 2.03e-3·exp(7.63e7/T³) poise (Moturi 1982), giving ≈**4.2 mPa·s at 20 °C, 3.6 at 25 °C** (est.) | [M] https://hiroshima.repo.nii.ac.jp/records/2029700 |
| Dark soy (老抽), 甜面酱, 豆瓣酱 | **No numbers found.** Nagasawa et al. 2019 measured sweet bean and oyster sauce (paywalled) | cited in [M] https://arxiv.org/pdf/2201.12128 |
| Oyster sauce | Shear-thinning (Herschel-Bulkley). Lab formulas: 1% starch K 0.50 Pa·sⁿ, n 0.47; 3% starch K 8.65, n 0.24. At 10 s⁻¹ that is ≈**0.15–1.5 Pa·s** (est.) | [M] https://pmc.ncbi.nlm.nih.gov/articles/PMC11342395/ |
| Doenjang (closest proxy for 豆瓣酱) | Casson yield stress **2–64 Pa**, n 0.30–0.55 | [M, abstract] https://koreascience.or.kr/article/JAKO200211921108864.page?lang=ko |
| Vinegar (10% acetic) | 1.35 cSt at 15 °C | [O] https://engineeringtoolbox.com/kinematic-viscosity-d_397.html |
| Cooking wine (huangjiu, ≈15% ABV) | No direct data; ≈1.5–3 mPa·s (est., from ethanol–water) | est. |
| Sesame / rapeseed / peanut oil | 25 °C: sesame 63.4, rapeseed 60.1 mPa·s. Peanut 45.6 mPa·s at 35 °C | [O, snip] https://cjme.springeropen.com/articles/10.1186/s10033-023-00895-5/tables/2 ; [O] engineeringtoolbox (above) |
| Ketchup (comparator) | Yield stress ≈22 Pa; 400 mPa·s at 236 s⁻¹ | [O, snip] NETZSCH (403) |
| Honey (comparator) | 7,430 mPa·s at 20 °C | [O, snip] (source 404) |
| 火锅底料 | Solid at room temperature; no melt data | — |

### 2.4 Powder dosing

| Device | Range | Accuracy | Notes | Src |
|---|---|---|---|---|
| ZONESUN ZS-FM100H desktop servo auger | 0.1–10 g | ±3–5% | US$3,400; 30 kg; 500 × 420 × 950 mm; one powder | [M] https://www.zonesunautopack.com/products/zonesun-zs-fm100h-semi-automatic-desktop-powder-filling-machine |
| 上海轩鹏 "50型" screw filler | 2–500 g | ≤±1% | SUS304/316L; lists pepper powder; price 电议 (on enquiry) | [O] https://m.cnpowder.com.cn/ns21711/productsdetail_116614.html |
| Alba gravimetric vibratory microdoser | 0.4–2 g | no ± given | Vibration adjusted against a load cell; 7–15 s per dose | [O] https://making.com/equipment/gravimetric-powder-microdosing-0-400-2-g |
| Mettler Quantos / Chemspeed GDU-P (lab) | mg range | ±0.1 mg (Chemspeed, "dependent on solid") | Gravimetric: coarse feed, then trickle; has a "non-flowable" algorithm | [O] https://research.yale.edu/cores/catalysis-and-separations-core/chemspeed-crystal-powderdose |
| Euphotic (Nosh) patent | — | none stated | Slot on a rotary lever under the hopper + **bladed agitator wheel against clumping** | [M] https://patents.google.com/patent/US12075933 |
| CMU MRSD 2022 cooking robot | — | "within a tolerance of 5 g" | Arm shakes containers; scale under the pot | [M] https://mrsdprojects.ri.cmu.edu/2022teamb/system-requirements/system-summary/ |
| Industrial spring-auger salt doser | 120–700 kg/h | CV 4.1–6.5% | Volumetric augers alone carry a few % error | [O, snip] https://www.mdpi.com/2673-9976/56/1/28 |

### 2.5 Humidity and caking (Singapore ambient RH ≈70–90%)

| Material | Critical RH / finding | Src |
|---|---|---|
| NaCl | **75.3% at 25 °C, 75.1% at 30 °C** | [M] https://pmc.ncbi.nlm.nih.gov/articles/PMC5295834/ |
| Sucrose | Deliquesces at 86% RH | [M] https://skoge.folk.ntnu.no/prost/proceedings/aiche-2005/topical/pdffiles/T9/papers/434g.pdf |
| Mixtures | Always lower than each ingredient alone: sucrose + citric acid 64%. Cycling 55↔72% RH caked glucose + citric acid; finer particles formed harder cakes | same; [M] https://docs.lib.purdue.edu/open_access_theses/718 |
| MSG crystal | <1% uptake at ≤70% RH; uptake surges at 80% (25 °C); dries back quickly | [M] https://surfacemeasurementsystems.com/wp-content/uploads/2022/07/App28-MSG.pdf |
| Sea salt vs refined salt | Sea salt has lower deliquescence RH and the highest caking strength | [M, abstract] https://pure.korea.ac.kr/en/publications/investigation-of-the-moisture-induced-caking-behavior-with-variou/ |
| Seasoning powder | Flow energy jumps at 80% RH (caking) | [O] https://www.rheologylab.com/articles/food/solving-humidity-induced-issues-in-seasonings/ |
| 鸡精 / chicken powder, corn starch | **No numbers found** | — |
| SiO₂ anticaking additive (US) | ≤2% of food weight | [M] https://www.law.cornell.edu/cfr/text/21/172.480 |

**Countermeasures (est.)**
- Seal every hopper and close a shutter whenever it is idle.
- Keep a silica-gel cartridge in a separate perforated compartment, never mixed into the food.
- Fill with only 1–2 weeks' stock.
- Fit an agitator.
- Use refined salt and crystal MSG.
- Ideally keep the dosing cabinet below about 60% RH.
- For a cheap caking test, a closed box over saturated brine holds about 75% RH.

### 2.6 Whole spices (花椒, 八角, 干辣椒, 桂皮, 香叶)

| Option | Evidence | Assessment (est.) |
|---|---|---|
| Vibratory feeder + weigh hopper | Suits free-flowing granules; sticky products need belts or screws [O] https://en.wikipedia.org/wiki/Multihead_weigher | Plausible for **花椒** only. Star anise, bark, leaves and long chilies bridge and tangle |
| Multihead weigher (14–28 heads) | [O] same | Industrial; far too big |
| Arm shakes a container | ±5 g [M] (CMU, above) | Too coarse for doses of 0.5–3 g |
| **Weekly kit of lidded cups, filled by the user** | Pattern used everywhere: Posha, Nosh trays, 厨纪 feed boxes, US10264914 flip compartments (§5) | **Recommended.** Recipes count these by piece |
| Retail portion packs (卤料包, single-portion 火锅底料) | Not verified (budget) | Good fit for a cup kit |

### 2.7 Load cells and scales

| Item | Capacity / resolution | Key specs | Price | Src |
|---|---|---|---|---|
| HX711 ADC | 24-bit | Noise 50 nV rms at 10 SPS, 90 nV at 80 SPS; gain drift ±5 ppm/°C; settling 400 ms | — | [M] https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf |
| HX711 in practice | — | ≈14–15 noise-free bits | — | [O] https://forum.arduino.cc/t/hx711-noise-free-resolution-tests/351959 |
| 5 kg bar cell + HX711 kit | 5 kg | ±0.02% FS ≈ ±1 g (est.); noise ≈0.06 g rms at the datasheet floor, ≈0.2 g rms measured per sample (est.) | 115 SEK | [O] https://www.electrokit.com/en/load-cell-5kg-with-hx711-amplifier-module |
| Mettler WMS6002C / WMS404C OEM modules | 6,200 g / 10 mg; 410 g / 0.1 mg | σ ≤10 mg / ≤0.1 mg; drift ≤9 mg/°C; RS232/RS422; 316L, IP54; **rated only for 20–80% RH**, 10–30 °C | n/a | [M] https://www.mt.com/dam/product_organizations/industry/apw/product_specific/wms/datasheet/30242883_A_MAR_DS_WMS_en.pdf |
| **Decent Scale** | 2,000 g / 0.1 g | **Open BLE API**, 10 Hz, documented packets; GPL3 ESP32 firmware | — | [M] https://decentespresso.com/decentscale_api |
| Acaia Lunar / Pearl | 2,000 g; ±0.05 g / 0.1 g | Community Python BLE libraries | — | [O] https://github.com/vctrd/pyacaia |
| A&D EK-6100i | 6,000 g / 0.1 g | RS-232C | ≈US$351 (eBay) | [O] https://www.ebay.de/itm/197903334859 |
| Ohaus Scout STX6201 | 6,200 g / 0.1 g | RS232/USB/Ethernet options | US$1,100–1,228 | [O] https://transcat.com/brand/ohaus-store/balances/ohaus-scout-stx-electronic-balance-6200g-0-1g |
| Chinese RS485 weighing transmitter (e.g. GM8802-F) | 24-bit, Modbus RTU | — | no CNY price found | [O] https://trends.directindustry.com/shenzhen-general-measure-technology-co-ltd/project-63947-140251.html |

**Design note (est.):**
- Weigh small doses in a **cup on a 0.3–1 kg cell** (≈0.01–0.05 g rms), then let the arm tip the cup.
- A pan scale needs ≥5–10 kg capacity, giving ≈0.1–0.4 g rms with HX711 plus heat drift from the burner. That is fine for liquids and vegetables, not for 0.5 g of pepper.

### 2.8 Food-contact material rules (tubes, printed parts)

| Rule | Content | Src |
|---|---|---|
| GB 4806.7-2023 (plastics) | In force 2024-09-06; absorbs GB 4806.6; positive list of 187 resins | [O] https://en.reach24h.com/news/industry-news/food-contact-materials/china-gb-4806-7-2023-food-contact-plastics-compliance |
| GB 4806.9-2023 (metals) | In force 2024-09-06; alloy-element migration limits; stricter Pb/Cd/As for stainless | [O] https://food.chemlinked.com/database/view/5202 (checked) |
| GB 4806.11-2023 (rubber) | In force 2024-09-06 | [O] https://food.chemlinked.com/database/view/5203 |
| **GB 4806.16-2025 (silicone rubber)** | Issued 2025-09-02, **in force 2026-09-02 (now)**; silicone split out of 4806.11 | [O] https://food.chemlinked.com/database/view/6005 (checked) |
| GB 9685-2016 (additives) | Positive list with specific migration limits | [O] https://chemical.chemlinked.com/database/view/602 |
| FDA 21 CFR 177.2600 (rubber, repeated use) | Silicone listed. Aqueous extractives ≤20 mg/in² (first 7 h), ≤1 mg/in² (next 2 h); fatty ≤175 / ≤4 | [M] https://www.law.cornell.edu/cfr/text/21/177.2600 |
| FDA 21 CFR 177.1520 | Olefin polymers, including PP | [M] https://www.law.cornell.edu/cfr/text/21/177.1520 |
| FDA 21 CFR 175.300 | Resinous and polymeric coatings | [M] https://www.law.cornell.edu/cfr/text/21/175.300 |
| EU 10/2011 | Filament declarations cite it (e.g. Ultrafuse PET); limit text not retrieved | [O] https://move.forward-am.com/hubfs/AES%20Documentation/Standard%20Filaments/PET/Sales%20Resources/Ultrafuse_PET_FCC_Statement_EN.pdf |
| Singapore SFA | Food Regulations reg. 37: no >1 ppm vinyl chloride monomer, no Pb/Sb/As/Cd; **no positive list found** | [O] https://food.chemlinked.com/foodpedia/singapore-food-contact-materials-regulation |
| 3D printing (Formlabs guide) | "No Formlabs resins are food safe unless users take additional steps." FDM layer crevices harbour bacteria; avoid leaded brass nozzles; coatings "don't guarantee" long-term safety | [M] https://formlabs.com/blog/guide-to-food-safe-3d-printing/ |

**Practical rule (est.)**
- **Wetted parts:** 304/316L stainless, PP and silicone, bought with GB 4806 / FDA / EU declarations.
- **Silicone bought after 2026-09-02:** needs a GB 4806.16 declaration.
- **3D prints:** only for non-wetted parts, or brief dry contact. Use filament that has a declaration of conformity, a stainless nozzle, and make the parts replaceable.

---

## 3. Staples

### 3.1 Rice dispensers (all mechanical; **none found that software can trigger**)

| Product | Capacity | Dose | Size | Price | Src |
|---|---|---|---|---|---|
| Morphy Richards MRRB12W | 13 kg | Dial, **150 g per cycle**; drying box. Its battery runs only a 21-day timer | 39.7 × 18.5 × 43 cm | AUD 131 | [O] https://www.jbhifi.com.au/products/morphy-richards-auto-grain-rice-dispenser-or-container-storage-box-with-timer |
| EKO stainless (sold in Singapore) | 5 kg | Press, **150 g per press** | 20 × 36.5 × 35 cm | SGD 80.64 + GST | [O] https://store.siahuat.com/product/8143424286 |
| ASVEL 計量米びつ 12 kg / 6 kg | 12 / 6 kg | Lever, 1合 / **0.5合** (≈150 / 75 g est.); gasket; works with wash-free rice | 18.1 × 41.8 × 41.1 cm (12 kg) | — | [M] https://item.rakuten.co.jp/asvel/7528/ |
| Chinese 按压米桶 (generic) | 4.5 L–"20 lb" | 150 g per press (some ≈75 g) | — | CNY 42–51 | [O, snip] https://www.smzdm.com/ju/shaiwu/s58yl9l/ |

### 3.2 Rice cookers that load rice and water themselves

| Product | Rice storage | Rice / water feed | Washing | Control | Size / price | Src |
|---|---|---|---|---|---|---|
| **Panasonic SR-AX1** (JP, 2023-07) | **2 kg (13合)**, wash-free rice only | Rice and water fed alternately in small steps from their tanks; **600 ml water tank**; weight sensing | None (無洗米) | **Kitchen Pocket app**: remote start, change finish time and portion, cancel; 0.5–2合 in 0.25合 steps | **176 × 336 × 336 mm**; ≈¥46,000 JPY expected (≈CNY 2,200 est.); 100 V Japan model | [M] https://news.panasonic.com/jp/press/jn230619-1 ; [O] https://kaden.watch.impress.co.jp/docs/news/1509274.html |
| Midea MB-30AH08 "Royce" 全自动煮饭机器人 | not stated | Negative-pressure rice suction; IR sensor sets water ratio | "Tumbling self-rinse"; water and drain details not found | Midea 美居 app | 3 L; launched ¥6,999 (2021-11), ¥2,159 with coupon (2024-04) | [O] https://www.smzdm.com/p/42622511 ; [O] https://www.smzdm.com/p/108409611/ |
| 饭小二 (Mi ecosystem, 2019) | 2.5 kg | **Plumbed** tap-water inlet + optional purified water + **drain**; needs a hole in the counter | Auto-wash, rinse count adjustable | **Mi Home app** + Xiao AI | 2.8 L pot; price not found | [O] https://post.smzdm.com/p/a78ed789/ |
| KitchenAid Grain & Rice Cooker | user adds grain | Built-in scale; pumps water from a tank | no | — | US$299.99 | [O] https://www.homepagenews.com/home-housewares/kitchenaid-introduces-automatic-grain-rice-cooker/ |
| Fujimak RicePro (commercial) | silo | Measures, washes, sets water, cooks, moves pots | yes | Schedule up to 4 days ahead | restaurant scale | [M] https://en.fujimak.co.jp/products/03/000324.html |

**Software control**
- **Mi Home:** the TOKIT 1.6 L cooker's MIoT spec lists **Start Cook / Cancel Cooking / Set Recipe / Start Recipe Cook** actions [O] https://home.miot-spec.com/spec/chunmi.cooker.017meu
- **Midea:** the Home Assistant `midea_ac_lan` rice-cooker type is **read-only** ("No services") [O] https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/EA.md
- **Panasonic:** no open API found.

### 3.3 Flour and starch

| Item | Fact | Src |
|---|---|---|
| Zevro gravity dry-food dispenser | ≈1 oz (≈28 g) per twist: too coarse for 5–30 g | [O, snip] |
| Starch in cold water | Insoluble; granules 2 µm (rice) to 100 µm (potato), so a slurry settles | [O] https://en.wikipedia.org/wiki/Starch |
| 水淀粉 (starch slurry) | Starch stirred into cold water (potato, corn, tapioca, mung bean) | [O] https://zh.wikipedia.org/wiki/勾芡 |
| Slurry stability / settling time | **Not found.** Stir before each dose and make fresh daily (est.) | — |

### 3.4 Cooking oil: dispensing and storage

| Item | Fact | Src |
|---|---|---|
| 小熊 metered spray bottle | 0.8 ml per press | [O] https://www.smzdm.com/ju/shaiwu/sy0xxq1/ |
| Supor 550 ml tilt-open glass bottle | Opens when tilted, closes upright (non-electric; easy for a gripper) | [O] https://www.smzdm.com/ju/shaiwu/s3411ww/ |
| Dreamfarm Oileroo | 15 ml dosing button | [O] https://housewareslive.net/dreamfarm-oileroo/ |
| Frontline Box System (commercial bulk oil) | Inverted oil boxes in a rack; wand dispensing; ≤18 gal | [O] https://www.fsrmagazine.com/industry-news/frontline-introduces-redesigned-oil-dispenser-system/ |
| Singapore HealthHub storage advice | Cool, dark, tightly closed. Shelf life: peanut 2 yr; rice bran, soy, sunflower 1 yr; sesame 6 mo | [M] https://www.healthhub.sg/well-being-and-lifestyle/food-diet-and-nutrition/the-oily-truth |
| Electric gram-dosing oil dispenser for homes; Chinese 定量出油机 for restaurants | **Not found** | — |

### 3.5 Deep-fry oil handling

| Item | Fact | Src |
|---|---|---|
| **Tefal Oleoclean Compact FR701640** | 2 L oil, 800 g food, 150–190 °C, 1,600 W. "Automatic filtration" dial drains through a sieve into a removable oil box **once the oil is cool**; dishwasher-safe | [M] https://www.tefal.co.uk/Semi-professional/Tefal-Oleoclean-Compact-FR701640-Semi-Professional-Deep-Fryer--Grey--0-8kg--3-portions/p/7211002922 |
| Tefal Oleoclean Pro FR804040 | 3.5 L oil, 1.2 kg food; same filtration | [M] https://www.tefal.ie/p/7211002452 |
| Frymaster FilterQuick (commercial) | Built-in filtration; optional oil-quality sensor | [M] https://www.frymaster.com/product/filterquick |
| Hong Kong CFS | Discard at **TPC >27%**; fry at 150–180 °C; no fixed reuse count | [M] https://www.cfs.gov.hk/english/multimedia/multimedia_pub/multimedia_pub_fsf_160_02.html |
| China GB 2716-2018 | Frying oil: polar compounds ≤27%; acid value ≤5 mg KOH/g | [O, snip] |
| Singapore SFA | No TPC limit; discard on colour, odour, smoke or foam; strain; store used oil sealed and dark | [M] https://www.sfa.gov.sg/food-safety-tips/food-risk-concerns/risk-at-a-glance/reusing-cooking-oils |

---

## 4. Fridge access for the arm

### 4.1 Drawer and under-counter fridges

| Product | W × H × D (mm) | Volume | Drawers / temperatures | Opening | Price | Src |
|---|---|---|---|---|---|---|
| **Fisher & Paykel CoolDrawer RB9064S1 (SG)** | **855 × 640 × 557** | 104 L gross / 80 L net | 1 drawer, 5 modes: Fridge, Freezer −18 °C, Pantry, Chill −0.5 °C, Wine 7/12/15 °C; 230 V 10 A; 108 kWh/yr | **Full-extension runners**; optional **OPEX1** assisted opening | **SGD 5,000** | [M] https://www.fisherpaykel.com/sg/cooling/refrigeration/integrated-refrigeration/90cm-series-9-integrated-cooldrawer-multi-temperature-drawer--rb9064s1-25671.html (checked) |
| F&P OPEX1 accessory | 213 × 34 × 264 | — | — | **Knock-to-open, push-to-open or assisted pull.** Auto-closes if triggered but not fully opened. Mains plug; no app | NZD 599 | [M] https://www.fisherpaykel.com/nz/accessories/cooling-accessories/assisted-opening-accessory-opex1-26049.html |
| Liebherr UIKo1560 (60 cm under-counter) | 597 × 820 × 550 | 132 L | Pull-out drawer with lift-up box | Telescopic rails, soft-close | — | [O, snip] https://www.euronics.co.uk/p/LBHUIKO1560 |
| Café CDE06RP2NS1 (US) | ≈606 × 860 × 660 (est. from inches) | 5.7 cu ft | 2 fridge drawers | Soft-close | US$3,499; 115 V | [O] https://www.relyonpdi.com/products/cafe-cde06rp2ns1 |
| True TRCB-48 chef base (commercial) | ≈1,229 W × 648 H × 841 D (est.) | 8.4 cu ft | 2 drawers, each 2 full-size GN pans; 33–38 °F; top rated 717 lb | Tool-free slides | US$7,026; 115 V | [O] https://www.webstaurantstore.com/spec-series-refrig-chef-base-2-draw-48x20x32/890TRCB48S.html |
| Haier / Casarte / Midea (China) | No under-counter drawer model verified. The market centres on 594 mm-deep 零嵌 uprights, ≈CNY 5,000–6,500 (Haier) | | | | | [O, snip] https://www.ithome.com/0/976/442.htm |

### 4.2 Auto-opening doors and drawers

| Product | Trigger | Remote / API | Notes | Src |
|---|---|---|---|---|
| Samsung Bespoke AI SBS "Auto Open Door" RS80F65J3BSS (sold in SG) | Touch sensors (back of the hand); voice via Bixby | SmartThings only sets the mode; **no remote "open" found** | Wide-open mode 80–120°, no auto-close. Semi-open mode <30° "reduces the force required", auto-closes. 912 × 1,786 × 716 mm, 634 L | [M] https://www.samsung.com/hk_en/support/home-appliances/how-to-use-and-address-auto-open-door-function-issues-on-your-samsung-refrigerator/ ; [M] https://www.samsung.com/sg/business/refrigerators/side-by-side/refrigerator-sbs-rs90f-aod-655l-clean-black-rs80f65j3bss |
| **Bosch / Siemens Home Connect "Door Assistant"** | Push or pull on the door | **API settings (checked):** `Refrigeration.Common.Setting.Door.AssistantFridge` (bool); `AssistantForceFridge` (Low/Middle/High "pressure required to activate"); `AssistantTriggerFridge` (Push/Pull/PushPull); `AssistantTimeoutFridge` (s). A generic `BSH.Common.Command.OpenDoor` exists, but fridge support is unconfirmed | Set to Low + Push, a light tap from the robot opens the door, so the arm never fights the seal | [M] https://api-docs.home-connect.com/settings/ ; [M] https://api-docs.home-connect.com/commands/ |
| LG InstaView / SIGNATURE | "Hi LG" voice (2021); step on a projected light | ThinQ | — | [O] https://voicebot.ai/2020/12/30/lg-introduces-new-refrigerator-that-opens-on-command/ |
| Hitachi (JP) R-WXC74X and others: **motorised drawers** | Button opens and closes the freezer and vegetable drawers | — | 880 × 738 × 1,833 mm, 735 L, ≈¥369,074 JPY; Japan only | [M] https://kadenfan.hitachi.co.jp/rei/ ; [O] https://search.kakaku.com/rwxc74x/ |
| Casarte 卡萨帝 | "智能敲击开门" (knock to open) mentioned; not verified | — | ≈CNY 8,499–10,999 | [O, snip] https://jd.zol.com.cn/topic/5097610.html |

### 4.3 Opening forces, standards and the UR5e

| Item | Value | Src |
|---|---|---|
| **Measured seal breakaway, ≈150 fridges** | **6–26 lb (≈27–116 N)**; **+20% at the first opening in the morning** | [O] https://publichealth.buffalo.edu/cat/kt4tt/best-practices/need-to-knowledge-ntk-model/ntk-commercial-devices/case-examples/stage-3.html (checked) |
| 16 CFR 1750 (US Refrigerator Safety Act) | Door must open from inside at ≤15 lb (66.7 N) | [M] https://www.govinfo.gov/content/pkg/CFR-2002-title16-vol2/html/CFR-2002-title16-vol2-chapII-subchapF.htm |
| UL 60335-2-24 | Same 15 lb inside-release test at 3 points | [O, snip] https://ulse.org/standards-and-engagement/standards-matter/helping-prevent-child-entrapment-household |
| ADA 2010 §309.4 | Operable parts ≤22.2 N (5 lbf); applies to buildings, not appliances | [M] https://www.corada.com/documents/2010ADAStandards/309 |
| Jain et al. BioRob 2010 | Forces and paths for 29 doors + 15 drawers in 6 homes | [O, snip] https://repository.gatech.edu/entities/publication/3bda8452-1c99-48f3-b85e-89d30b3726b1 (403) |
| Drawer-slide pull forces; GB/T 8059 door-force clause | Not found | — |
| **UR5e** | Payload 5 kg, reach 850 mm. TCP F/T sensing: **±50 N range, ±3.5 N precision, ±4.0 N accuracy**; torque ±10 N·m | [O] https://www.wevolver.com/specs/universal-robots-ur5e ; [M] https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/ |

**Implication (est.).** The upper half of the measured breakaway range (50–116 N) exceeds the UR5e's force-sensing range and is a hard pull at long reach. Choose a fridge where the arm does not break the seal by pulling. Options:
- assisted opening (F&P OPEX1, or Home Connect Door Assistant on Low/Push);
- Samsung's semi-open mode;
- otherwise a hook tool pulling at the handle edge, far from the hinge.

### 4.4 Inventory cameras

| System | Function | API | Src |
|---|---|---|---|
| Samsung AI Vision Inside (2024 Family Hub) | Recognises up to 33 fresh foods; logs items in and out | SmartThings REST exists; **no camera-image endpoint documented** | [O, snip] https://www.tomsguide.com/news/samsung-unveils-2024-bespoke-family-hub-refrigerator-with-vision-ai-heres-what-it-can-do |
| Bosch/Siemens Home Connect | 2 cameras photograph the shelves at each door closing | `GET /homeappliances/{haId}/images`; **discontinued for some older models on 2026-03-31** | [M] https://api-docs.home-connect.com/images/ |
| LG ThinQ; Haier/Casarte 食材识别 | Not covered (budget) | — | — |

Conclusion (est.): use the robot's own wrist or overhead camera looking down into an open drawer.

### 4.5 Robot research on doors and drawers

| Work | Robot / tool | Result | Src |
|---|---|---|---|
| Cody (Georgia Tech, equilibrium-point control) | 7-DoF compliant arm, 3D-printed **rubber-coated hook**, wrist F/T | 37/40 trials on 10 doors and drawers. Authors say it fails on high-force mechanisms "such as most refrigerators" | [O] https://spectrum.ieee.org/050610-georgia-tech-robot-masters-art-of-opening-doors-and-drawers |
| Gupta et al. 2024, Stretch RE2 | Gripper, arm-effort contact detection | 61% zero-shot on 31 unseen objects. **Drawers 8/9**, left-hinged doors 4/9, right-hinged 7/13. 59% of failures were perception | [M] https://arxiv.org/html/2402.17767v1 |
| Mobile ALOHA (2024) | Bimanual, 750 g per arm | "Use Cabinet": 85% over 20 trials. The fridge appears only in teleoperated demos | [M] https://arxiv.org/pdf/2401.02117 |
| Virginia Tech force-feedback door opening | Joint force feedback | 83% vs 60% success, ≥33% faster | [O, snip] https://vtechworks.lib.vt.edu/handle/10919/56584 |
| Willow Garage PR2 "Beer Me" (2010) | PR2 | Opened the fridge and fetched a beer; no metrics | [O] https://laughingsquid.com/willow-garage-pr2-robot-fetching-a-beer-from-a-refrigerator/ |
| UR5 + Robotiq FT300 + 2F-140 cabinet doors | Adaptive revolute opening | No numbers read | [O, snip] https://arxiv.org/pdf/2304.14602 |

### 4.6 How long food may stay out of the fridge (staging before cooking)

| Authority | Rule | Src |
|---|---|---|
| USDA FSIS | Discard perishables after >2 h at room temperature, **or >1 h above 90 °F (32.2 °C)** | [O, snip, archived FSIS page] https://cybercemetery.unt.edu/oilspill/20130218140944mp_/http://www.fsis.usda.gov/Fact_Sheets/Safe_Handling_Take-Out_Foods/index.asp |
| FDA Food Code 3-501.19 | Time as control: max 4 h, then cook or discard; the 6 h option needs ≤21 °C ambient, so it does not apply in Singapore | [M, FDACS synopsis] https://ccmedia.fdacs.gov/content/download/65467/file/Time_as_a_Public_Health_Control_Requirements.pdf |
| FSANZ 2 h / 4 h rule | 5–60 °C: <2 h use or refrigerate; 2–4 h use now; >4 h discard. **Cumulative, including prep time** | [M] https://www.foodstandards.gov.au/business/food-safety/2-hour-4-hour-rule |
| Singapore SFA | Danger zone 5–60 °C. Ready-to-eat food not kept at 5–60 °C for >4 h (food establishments); thaw at 0–4 °C. Consumers: refrigerate perishables within 2 h | [M] https://www.sfa.gov.sg/docs/default-source/circulars/others/2024/advisory-on-food-safety-practices-for-food-establishments_dec-24.pdf ; [M] https://sfa.gov.sg/docs/default-source/educational-materials/proper-temperature-for-hot-foods.pdf |
| Shenzhen DB4403 团餐 (likely mirrors GB 31654-2021, not verified) | Cooked perishables between chill and 60 °C ≤2 h; refrigerated cooked food ≤24 h | [M] https://amr.sz.gov.cn/attachment/1/1490/1490801/9772236.pdf |

**Rule for the robot (est.).** At 30–32 °C kitchen air, stage raw meat, seafood, tofu and cut vegetables for **≤1 h** (USDA rule above 32 °C). Track the time each item spends out of the fridge, cumulatively (FSANZ). Fetch each item just before its cooking step.

---

## 5. Whole-kitchen and cooking robots: how they solve storage

| Product | Status | Seasoning / dispensing | Cold storage & retrieval | Price | Src |
|---|---|---|---|---|---|
| Moley (UK), 2 arms on a rail | Launched Dec 2020; deliveries unverified | Ingredients in system-identified containers | Smart fridge with "eight separate sections… automatic doors" [O, snip]; **a human stocks it** | ≈£248k (with arms) | [O] https://newatlas.com/robotics/moley-robotic-kitchen-launch/ ; [O] https://thespoon.tech/moleys-robotic-kitchen-goes-on-sale/ |
| Samsung Bot Chef | CES demos only | Arms take seasoning bottles from the cabinet and put them back | Ordinary cabinets | — | [O] https://www.techradar.com/news/samsungs-bot-chef-made-me-a-salad-at-ces-2020-and-i-ate-it |
| Spyce, now Sweetgreen Infinite Kitchen | Operating | Refrigerated hoppers portion into a runner box feeding 7 woks | Hoppers **loaded by staff**; commissary does the prep | — | [O] https://www.technologyreview.com/2018/08/22/240253/engineering-lunch/ |
| Botinkit OMNI (Shenzhen; deployed in Singapore) | Commercial | Dry/sauce, liquid and oil boxes; **up to 13 dispensed at once** (16 seasonings reported); oyster sauce, ketchup, 沙茶酱, honey, salt, MSG, pepper; boxes 650–1,500 ml; auto-cleans wok and tubes. **827 × 920 × 1,769 mm, 180 kg, 12 kW** | — | A$41,550 ex GST | [M] https://www.botinkit.ai/product/cooking-robot ; [O] https://www.caterlink.com.au/shop/botinkit-intelligent-cooking-station-omni/ ; [O] https://www.fancyindus.com/botinkit-omni.htm |
| 智谷天厨 T-chef | ≈600 chain stores | **15-channel** seasoning system | Staff pour pre-cut, recipe-portioned ingredients | ≈RMB 60,000 (mid-size) | [O] https://eu.36kr.com/zh/p/3552378855242628 |
| 厨纪 F3 / 优特智厨 / 香露 | Commercial | 厨纪: 6 seasoning lines + **4 feed boxes**. 优特: salt "within 1 g" [O, snip]. 香露: "0.1 g" claim | Human-loaded feed boxes | 香露 RMB 30–100k | [O] https://www.jiemian.com/article/13889202.html |
| Peicook K8/K9 | Commercial | 7 seasoning lines (soy, salt/sugar, thickener …) | — | — | [M] https://www.peicook.com/article/llux8q6d |
| Kitchen Robotics "Beastro" | Commercial | 12 liquid + 23 non-liquid feeders; **closed loop by weight** | Raw food must arrive washed and chopped | — | [O] https://nocamels.com/2023/08/kitchen-robot-gives-chef-four-extra-pairs-of-hands/ |
| 千玺 / Foodom robot restaurant | Opened 2020 | — | Central kitchen preps; machines "automatically retrieve ingredients from the cold room" | — | [O] https://36kr.com/p/1724980822017 |
| Karakuri DK-One, Aitme, Hyphen, Chef Robotics, Miso Flippy 2, Picnic | Commercial / pilot | Portion hoppers and pans; Hyphen ±2% [O, snip] | Chilled hoppers or bins **refilled by staff** on alerts | — | [O] https://thespoon.tech/aitme-is-building-a-robot-restaurant-kiosk-in-berlin ; [O] https://thespoon.tech/picnic-debuts-second-its-generation-pizza-robot/ ; [M] https://chefrobotics.ai/post/new-ingredient-chef-robots-can-now-serve-super-sticky-foods (Karakuri and Hyphen article URLs were not fully recorded) |

**Patented mechanisms worth copying**

| Patent | Mechanism |
|---|---|
| **US11096514** [M] | Capped jars in compartmented, often refrigerated storage; transfer device → auto cap-opener → gripper inverts into the wok. Closest to a UR5e + drawer-fridge concept. |
| **US10264914** [M] | 4/6/8-compartment container flipped 180°; solenoid doors release in recipe order. |
| US12059081 (Cucina) [M] | Spice carousel + metering plate, gas-burst propelled. |

**Lessons (est.)**
1. Every system, including the £248k Moley, relies on **humans or a central kitchen to wash, cut and portion**, and to refill hoppers.
2. **Per-dish compartment trays in recipe order** are the recurring interface (4–6 boxes).
3. **Liquids are pumped; powders are often turned into liquids.**
4. **Closed-loop weighing** is the accuracy fix.
5. **Bulk rice, flour and oil are never auto-dispensed inside these robots.** They are separate modules (steamers, rice cookers).

---

## 6. Proposed storage and dosing layout for this kitchen (est., for discussion)

| Item | Where | Method | Channels |
|---|---|---|---|
| Light soy, dark soy, vinegar, cooking wine, sesame oil, brine (salt), syrup (sugar) | Seasoning box in the upper-cabinet band (33 cm deep, ≤50 cm tall) or under the counter, with tubes run to one outlet manifold at the hob | Stepper peristaltic pumps, silicone/BPT tube, suck-back after each dose; weighed | 7 |
| Oyster sauce, starch slurry (stirred) | same | Peristaltic, ≈4.8 mm ID BPT tube, slow; weighed | 2 |
| Cooking oil | 5 L jug in a dark base cabinet | Peristaltic or gear pump | 1 |
| 豆瓣酱, 甜面酱 (+ ketchup) | Small chilled cartridges | Lead-screw syringe extruder, ≥6–8 mm outlet, or the arm squeezes a bottle | 2–3 |
| MSG, chicken powder, white pepper, five-spice/chili powder | Sealed canisters with desiccant | Agitated auger → dose cup on a 0.3–1 kg load cell → arm tips the cup | 4 |
| Whole spices, 火锅底料, aromatics (葱姜蒜) | Weekly kit of lidded cups (fridge or rack) | Arm picks the cup and tips it | per dish |
| Rice | Wash-free rice | SR-AX1-type auto-loading cooker, **or** a 150 g press dispenser + a Mi Home cooker with Start Cook | — |
| Chilled ingredients | Under-counter drawer fridge (F&P CoolDrawer class) with OPEX1 | Tap to open → arm lifts lidded trays out from above | — |

**Total ≈16–17 pumped or metered channels plus a cup kit.** For scale, Huayi (A) has 8 liquid + 6 powder, T-chef 15, Botinkit 16. Every channel count and placement here is an estimate for design discussion, not a sourced fact.

---

## 7. Gaps and blocked sources

**Not covered (search budget ran out):**
- Seasoning machines: 美的, 九阳, 橙子快跑, 爱餐, 熊猫/熊喵, 繁星, 拓氪, 小饭桌 seasoning modules.
- Chinese milk-tea 果糖机 (syrup) dispensers.
- Lead Fluid 雷弗 and 保定申辰 pumps; small Chinese 单螺杆泵 (progressive-cavity) pumps; food-grade solenoid valves.
- Viscosity numbers for 老抽, 甜面酱, 豆瓣酱 and huangjiu.
- Critical RH for 鸡精 and starch; food-grade desiccant rules.
- Motorised Chinese rice bins; Joyoung, Supor, Bear, Morphy and Viomi auto-load cookers; water and drain details for the Midea MB-30AH08.
- Chinese drawer fridges with prices (Haier, Casarte, Midea, Hisense, Xiaomi); Sub-Zero, U-Line and Bosch drawer units; Blum/Hettich motorised drawer kits; drawer-slide pull forces.
- Haier 食材识别 cameras; GB 31654 primary text; EU 10/2011 limit text.

**Blocked:**
- **Taobao:** Claude in Chrome permission prompt timed out.
- **JD, Tmall, 1688:** login or captcha; not attempted.
- **403 errors:** zhihu, baike.baidu, geekwire, theverge, fsis.usda.gov, repository.gatech.edu, euronics, NETZSCH, ACM DL, sso.agc.gov.sg.
- **Security check:** 36kr.
- **Unreadable:** EUR-Lex and legislation.gov.uk returned empty pages.

**Next step suggested:** with the user present to approve the Chrome prompt, read Taobao search listings for CNY prices of:
- 果糖机;
- 抽屉式冰箱 / 嵌入式冷藏抽屉;
- 按压米桶;
- 食品级蠕动泵 (Kamoer, 兰格);
- RS485 0.1 g weighing modules;
- 卤料包 portion packs.
