# R19b: Machines that stir and empty themselves (market survey)

Date: 2026-10-13. The user asked "比较难吧，市面上有这种产品吗" about a motorised stirrer and a tilt (tip-out) mechanism at the wok. This file answers with a market survey. Research was read-only, using WebSearch and WebFetch only (no browser automation, no logins, carts, purchases or seller contact). No existing file was changed.

**Tags**
- **[M]** maker page or maker spec sheet.
- **[O]** secondary source: review, news, reseller.
- **[O, snip]** seen only in a search-result snippet. Weaker.
- **inferred**: my own calculation or judgement.
- **ND**: looked for, not found.

**Prices.** All prices are **unconfirmed**. 1688 prices are wholesale or teaser start prices, seen 2026-10-13. smzdm prices are past deal posts. I could not read JD/Tmall item pages, 1688 offer pages, Zhihu, Amazon item pages or the Hong Kong retailers (HTTP 403/500 or login). Every page was accessed 2026-10-13; article dates are given where shown.

---

## 0. Direct answer: do such products exist?

1. **Machines that stir by themselves: yes, many.**
   - Home pot-type machines (a paddle in a lidded pot) cost ¥500–9,000.
   - Home drum machines cost about ¥1,300–1,900.
   - Thermomix-type machines cost ¥5,999 and up.
2. **Machines that stir AND tip the food out by motor: only commercial ones.**
   - Restaurant stir-fry robots that feed, stir, tip out and wash by themselves:
     - ≈ ¥1.8–11万;
     - 8–16 kW, often 380/415 V three-phase;
     - the smallest one with a public datasheet weighs 420 kg.
   - Canteen tilting braising pans (可倾式炒锅/汤锅) and planetary stir kettles: 40–145 L and up in China. In the US, the smallest stir-and-tilt kettle is 19 L, 6–8 kW, ≤148 °C, with a **hand** tilt.
   - **No home-sized product with a motorised tip-out was found.** One US Amazon listing claims a 6 L drum that "pours out ... without manual operation". It is unverified (§1.2).
3. **The closest home product: the 6 L induction drum stir-fryer (滚筒炒菜机).**
   - The drum turns by itself.
   - The **whole body pivots 0–135/150° by hand**: from upright (stew), through 45–60° (stir-fry), to 90–135° (serving). The maker's words: "握著機身，即可輕力調校角度" [M German Pool ISF-622].
   - The arm could do this tilt by **pushing the body around its own pivot**. It would no longer lift and carry a 2.95 kg wok.
4. **A stand-alone stirrer for an existing wok at stir-fry heat: none found.** The products that exist are battery pot stirrers for sauces: ≤30 rpm, plastic rated ≤204 °C, for pots up to 30 cm. Domestic searches (懒人搅拌器, 自动锅铲, 炒锅搅拌器) only returned cup stirrers or 40 L+ planetary kettles.
5. **Control:**
   - The only home stir-fryers with a documented command interface are **Xiaomi-ecosystem (MIoT) models**: the 九阳/Solista SD-CJ01. Its current availability is ND.
   - Every other brand uses an app, a touchscreen or buttons, with **no public API**.
   - Behaviour after a power cut is ND for every model. So a smart plug is only a safe kill switch, not a "start" button.

**So the user's instinct is right.** A motorised stirrer plus tilt cradle **on our own wok** would be custom-built. The buyable route is a drum machine that stirs, with the arm doing the tilt and the loading.

---

## 1. Product table

Each subsection is one product class. The column "Discharge" says how the food leaves the machine.

### 1.1 Household pot-type auto stir-fry machines (paddle in a lidded pot)

| Model | Price | Capacity / power / max °C | Stirs by | Discharge | Lid; adding mid-cook | Control | Cleaning | Src |
|---|---|---|---|---|---|---|---|---|
| **九阳 CJ-A9** | ¥508–649 (smzdm deals); "from ¥514" | 3.5 L; 1,200 W heating plate (not IH); oil "<200 °C"; 6.8 kg | Paddle (搅拌铲) | **Lift the inner pot** (a 内胆把手 pot handle is in the box) | Damped lid, closed. 5 seasoning boxes auto-dosed | Electronic/microcomputer panel. App: ND. API: none | Removable black-crystal pot | [O] https://wiki.smzdm.com/p/prrdxj5/canshu/ ; [O, snip] https://www.smzdm.com/p/139910487/ |
| 九阳 J7 | ¥1,999 [r15] | "<200 °C" | Magnetic double-wing paddle | Lift the pot | **Lid must stay closed**; opening it interrupts the cycle | App (unreliable in test) | ND | [r15] https://post.smzdm.com/p/a83dp03q/ |
| **九阳 / Solista SD-CJ01** (Xiaomi Youpin, 2019) | "<¥1,000" (crowdfunding, 2019) | 3 L; max-temperature property 50–160 °C (v1 spec), 0–250 °C (v2 spec) | Double-wing paddle | Removable pot, lift out | Closed glass/steel lid | **MIoT spec (only real interface found)**: actions start recipe, **DIY start**, **pause/resume**, cancel, set temperature, set heat 0–3; properties status (standby/preheat/cooking/收汁/done/paused), remaining time, faults (dry-burn, no pot, lid); v2 adds stir-paddle time 0–2000 ms. Driven via Mi cloud, e.g. the community Home Assistant integration hass-xiaomi-miot (`call_action`). Dial on the handle. **Sold today: ND** | Non-stick, water rinse | [M] https://home.miot-spec.com/spec/jyaiot.cm.jycj01 ; https://home.miot-spec.com/spec/jyaiot.cm.jycj02 ; [O] https://post.smzdm.com/p/akm75lor/ (2019-09-10); https://github.com/al-one/hass-xiaomi-miot |
| **美的 PY18-X1S** | ND | 3.6 L; 1,800 W IH, 18 levels, ±1 °C | Paddle | Lift the pot | 5 seasoning boxes; weighing cup | **Wi-Fi app**, 108 recipes. Public API: none found | "支持全身水洗" | [O] https://wiki.smzdm.com/p/1wej5j3/ |
| 美的 Quick1 MJ-ECE15Q1 | ¥899 (deal) | ND | Paddle | Lift the pot | ND | ND | ND | [O, snip] https://www.smzdm.com/p/79546950/ |
| **添可 食万 3.0 Pro** | ¥3,990 [r15]; 食万 3.0 listed "¥8,890 起" | 4.5 L; 2,000 W IH; room temperature to 210 °C | 8-in-1 paddle, forward/reverse | Lift the pot | **Lid opens itself to 75°** at prompts; 8 liquid boxes (3.0: 5); built-in scale | App + 7.84" screen + knob. No public API | **Steam self-clean** (user empties the waste water) | [r15]; [O] https://post.smzdm.com/ju/aeppq7m/ |
| 添可 食万天工 | ¥8,500 | 4.5 L; 3,200 W; ≤210 °C | Paddle | ND | ND | App | ND | [O, snip] https://product.pconline.com.cn/cooker/ . Sina (2026-09-17): 添可 is "no longer producing new home models" |
| 苏泊尔 C30FS10 / C30HS12 / COOK3 Pro | ¥999–1,389; COOK3 Pro "约1,299 起" | 3 L (Cook3 series); ND | Paddle; COOK3 Pro "颠勺式" | Lift the pot | ND | ND | **Hot-water self-clean** | [O, snip] pconline guide, either https://best.pconline.com.cn/guide/91464.html or /91470.html (C30FS10 ¥999); [r19] 1688 (C30HS12); https://finance.sina.com.cn/tech/roll/2026-09-17/doc-iniscqyc0311210.shtml |
| 饭来 M1 (FL-M1301) | ≈¥699 (snip); 2019 model ¥2,199 | 2.2 L; 275×200×407 mm | Wave paddle "掂勺式" | Pot with handles, lift out | Flip lid; **small top feed port** (reviewer wanted a funnel) | **App only** (2019 model). No API | One-button auto clean | [O] https://post.smzdm.com/p/ag89dwgm/ (2019-02-26); [O] https://post.smzdm.com/ju/aeppq7m/ |
| 捷赛 E15 / D10 / JSC-M1 | ND | 3.5 L (E15); 4.5 kg (M1) | Double-wing paddle | Lift the pot | "Dry until oil comes out" method (倒炝锅); timer/预约 (E15) | Microcomputer buttons | Removable paddle | [O, snip] https://g.pconline.com.cn/x/1639/16396287.html ; [O] https://wiki.smzdm.com/p/3q9jd88/canshu/ |
| **海尔 AI厨天才 CR3** (launched Aug 2026, with 橡鹿) | **Not yet priced** | 3,500 W; **pot 140–180 °C** | Two stir paddles on a 4-axis mechanism | **ND** (articles say only "出锅后" steam rinse) | **Lid opens and closes by itself**; **4 ingredient bins drop in order**; 8 seasoning boxes "to the gram" | AI recipe model; app: ND | **100 °C steam self-rinse** | [M] https://www.haier.com/about_haier/xinwen/20260825_294291.shtml ; [O] https://global.hk01.com/数码生活/60383073/ |
| 京东 七鲜大厨 robot | ¥19,888 incl. ¥15,000 ingredient credit | ND | ND | ND | Pre-cut 净菜 delivered | ND | ND | [O] https://news.qq.com/rain/a/20260918A00KKC00 (2026-09-18) |

**Market context.**
- Sina (2026-09-17) says machines around ¥1,000 make up 60 % of sales.
- Machines with auto-feeding, seasoning and self-clean "普遍超过万元".
- Most products "只解决翻炒，备菜、清洁仍需人工".

### 1.2 Home / light drum machines (滚筒, the whole pot rotates)

| Model | Price | Capacity / power / size / max °C | Stirs by | Discharge | Lid; adding mid-cook | Control | Cleaning | Src |
|---|---|---|---|---|---|---|---|---|
| **德莱利 CM-800** / "德国IH多功能炒菜机家用商用滚筒式" (same class on 1688) | ¥1,300–1,499 [1688] | 6 L; ≈2,000 W IH; 220 V. Reseller data: 3 heat levels, 310×370×365 mm, 7.4 kg. Max °C ND | Drum rotates 360° | **Body tilts to 3 positions. Manual or motor: ND** for this listing (see the rows below) | Open mouth | Touch panel, "one-button start" ([O, snip]: "infrared touch") | Non-stick drum | [1688] https://www.1688.com/market/-B9F6CDB2B3B4B2CBBBFA.html ; JD brand page https://www.jd.com/brand/737a8ee9e9d77634176.html |
| **German Pool ISF-623** (HK brand of the same class; used here for its documented specs) | HK$6,880 (sold out) | 6 L, pot Ø230 × 170 mm; 2,400 W IH; **60–240 °C**, 10 levels; **24 rpm**; 405×360×385 mm; 9.8 kg | Drum rotation | **Body inclines 0–135°**; serving position 135° | Lid "可隨時掀開…加入配料或調味" | 4 programmes, voice prompts; buttons ND | **Inner pot twists to unlock and lifts out** | [M] https://www.germanpool.com/chi/products/sf_isf.php?mdl=623 ; [O, snip] spec list |
| **German Pool ISF-622** | ND (sold out) | 6 L; 2,200 W; 65–200 °C, 7 levels | Drum rotation | **Tilt by hand**: "握著機身，即可輕力調校角度"; 0–150°; serving at 135°; stir-fry 60°, pan-fry 75°, stew 45–60°, rice 0° | Lid recommended for 炆/煲 | ND | Inner pot lifts out | [M] https://www.germanpool.com/chi/products/sf_isf.php?mdl=622 ; [M] https://www.germanpool.com/eng/faq/FaqDetail.php?id=200 |
| 德莱德利 drum (2018 review) | ¥1,889 (2018) | ND | Drum + IR thermometer | **Press a release switch and push the body down by hand**: upright (stew) → 45° (stir) → 90° (serve). The last liquid needs the inner pot lifted out | Lid fully removable | 3 heat levels, timer | Residue sticks at the baffle root | [O] https://post.smzdm.com/p/awxlen6k/ (2018-12-07) |
| US Amazon listings of the same OEM class | ND | 6 L, 2,000–3,400 W; one says 50–240 °C | Drum | 3-level tilt / 0–135° / 0–150° "arbitrary positioning"; **one says "pour out … without manual operation" (2,200 W, 150°): motorised? unverified** | ND | Touch panel | ND | [O, snip] https://www.amazon.com/Automatic-Processor-Stir-fry-Rotatable-Restaurants/dp/B0DWDYC9TM ; https://www.amazon.com/Automatic-Stirring-Restaurant-Commercial-Induction/dp/B09D8YLPQQ |

### 1.3 Small commercial drum / rotary machines that fit a counter

| Model | Price | Power / size / capacity | Stirs by | Discharge | Control | Src |
|---|---|---|---|---|---|---|
| **Chefmax CM05-DL-TGS20** (…TGS26/30/36) | ND | **220 V, 3.5 kW** (5 kW larger); pan Ø200 mm; 2/4 L; 0.2–1.5 kg per batch; **525×475×530 mm** | Drum | **Manual tilt, 13–20 angle steps** | Digital display | [r15]; [O, snip] https://china.org.ru/product/1600173111549 |
| 赛米控 260 mm desktop drum; "赛米控台式电磁滚筒炒菜机 多功能圆底家用" | ¥9,800 [1688] | 3,500 W, 1–3 servings (JD) | Drum | ND | ND | [O, snip] JD brand page; [1688] |
| 1688 tabletop/commercial electric drums | ¥4,800–10,712 [1688] | ND | Drum | ND ("自动出料" in some titles) | ND | [1688] |
| ATEAGO AT-28 "spin cooking robot" | US$2,818.65 | 1.5–9.3 L; induction or gas; 470×690×700 mm; **61 kg** | Rotating pot + stirrer | "Tilting pot for waste disposal": manual or motor ND | One button | [O, snip] https://ca.robotshop.com/products/ateago-ateago-automatic-spin-cooking-robot-smart-robot-cooker |

### 1.4 Commercial cooking robots (feed, stir, tip out and wash by themselves)

| Model | Price | Power / size / weight | Discharge, cleaning | Src |
|---|---|---|---|---|
| **RoboChef MSS2K** (美膳狮 / 橡鹿. Inferred to be the "小钢炮2K" from the name) | AUD 24,999 ex GST | **415 V 3-phase, 8.7 kW; 720×960×1,535 mm; 420 kg**; pot 400×400 mm; >300 °C; 10–30 rpm | Auto adds sauces and ingredients; **tilts out** into a residue tank; **auto wash**; Wi-Fi cloud | [O] https://commercialequipmentonline.com.au/products/robochef-cooking-robot-mss2k ; https://kwcommercial.com.au/product/robochef-mss2k-cooking-robot |
| 橡鹿 range (小钢炮2K / 2K PRO, 中钢炮7K, 火箭炮400 PRO) | ≤¥5万 to ≈¥11万; 火箭炮 <¥6万 | 火箭炮400 PRO: 14 kW, 4 dishes at once | Auto | [O] https://www.36kr.com/p/3461709115889282 (2025-09-11) |
| 爱餐 天使 / 厨神 / 小牛 / 野牛 | ND | Large unit 230 °C in 38 s; ≤90 dB(A) | Auto feed, stir, clean | [O] https://m.tech.china.com/hea/articles/20260701/202607011906730.html |
| 佩厨 4-pot robot | ¥4–30万 | 16 kW, PROMAX 380 V; 0.42 m² footprint | Auto feed, 7 seasonings | [O] https://tech.china.com/articles/20260707/202607071910755.html |
| Botinkit [r14] | — | 827×920×1,769 mm, 12 kW | Auto | [r14] |

**Verdict:** these are not a home option (three-phase power, 0.4 t, ¥2–11万).

### 1.5 Tilting pans and stir kettles (可倾式炒锅 / 夹层锅 / 行星搅拌炒锅)

| Item | Price | Size / power | Stirs | Tilt | Src |
|---|---|---|---|---|---|
| 1688 可倾式炒锅 / 可倾式砂锅 (NF-800, RS-1200 and others) | ¥7,358–18,800 | **60–145 L**, gas or electric | Mostly no stirrer | **Electric tilt** on many | [1688] https://www.1688.com/market/-BFC9C7E3CABDB3B4B9F8.html |
| 1688 "商用自动翻炒锅全自动电加热夹层锅倾斜式倒料"; planetary stir woks with hydraulic or auto discharge | ¥2,310–58,000 (teaser prices as low as ¥36 ignored) | Smallest seen on JD: **40 L** (宏安泽) | Planetary / multi-claw | Tilt / hydraulic | [1688] https://www.1688.com/market/-D7D4B6AFB3B4B9F8.html ; [O] https://www.jd.com/brand/6196396ad5b20460a6eb.html |
| **Groen TDB-20 (US), the smallest stir-and-tilt kettle found** | ND | **20 qt ≈ 19 L**, countertop; **6.3 kW at 208 V three-phase, or 8.4 kW at 240 V single-phase**; **66–148 °C** (150–298 °F) | Twin-shaft agitator (one scrapes the wall); it tilts out **by hand** | **Hand tilt lever**; heat cuts off above 10° | [M] https://cdn.restaurantsupply.com/pdf/1/d/e/1de55440-941f-4ebf-8326-b812882de026.pdf |
| Electrolux automatic tilting bratt pans with stirrer | ND | 150 L | Yes | Motorised | [O, snip] electroluxprofessional.com |

**A home-size version was not found.** The smallest found is 19 L and 6 kW, and it reaches ≤148 °C, so it braises but does not stir-fry.

### 1.6 Stand-alone motorised stirrers for an existing pot

| Product | Price | Facts | Fit for our wok | Src |
|---|---|---|---|---|
| StirMATE (gen 3) | US$36–88 | Battery, 10 h; ≤30 rpm; food plastic rated 400 °F (204 °C); self-adjusts to pots 6–12 in (15–30 cm) wide, 3–9 in deep | **No**: plastic, low torque, slow; sauces only | [O, snip] https://sellout.woot.com/offers/stirmate-smart-pot-stirrer-self-adjust |
| Stirio (Unikia, Norway) | ND | Clamps onto 15–25 cm pots | No | [O, snip] https://newatlas.com/stirio-pot-stirrer-version-2/35148/ |
| Stirr | US$20–70 | Tripod; nylon legs 120 °C | No | [r15] |
| Domestic searches | — | 1688 "懒人搅拌器" returns only cup/mug stirrers. JD "自动搅拌锅" returns a baby-food maker and 10–30 斤 commercial hot-pot-base stirrers | No wok clip-on product found | [1688] https://www.1688.com/market/-C0C1C8CBBDC1B0E8C6F7.html ; [O] https://www.jd.com/chanpin/83197.html |

### 1.7 Anything else that stirs and empties itself

| Product | Facts | Discharge | Src |
|---|---|---|---|
| 米家烹饪机器人 (Thermomix type) | ¥5,999 presale; ≤180 °C; 40–12,000 rpm | Lift the jug by its handle and pour | [O] https://www.ithome.com/0/638/331.htm |
| Thermomix TM7 | ≤160 °C; no-lid "Open Cooking" ≤100 °C | Lift the jug | [r15] |
| Posha (US) | US$1,500–1,750; 1,800 W induction; 4 hoppers; arm with spatulas; open pan; camera | User removes the pan; parts dishwasher-safe | [O, snip] https://www.posha.com/how-to-use-posha |
| Commercial popcorn kettles | Motor stirrer in a kettle, hand dump handle | Manual tip | [O, snip] https://www.jd.com/chanpin/2407575.html . Mechanism reference only; specs ND |

---

## 2. Which homestyle dishes each class can cook

These are my judgements from the facts above, not tests. "Drum" means the 6 L 2–2.4 kW home class; "comm. drum" means the 3.5 kW tabletop class.

| Dish / step | Pot-type (lidded, ≤200–230 °C) | Drum (open mouth, tilts) |
|---|---|---|
| 红烧肉 (fry, 糖色, 40 min braise, 收汁) | **Good** (收汁 programmes) | OK upright with the lid (ISF stew 0–60°) |
| 番茄炒蛋, 蚝油西兰花 (焖 30 s) | OK | OK; lid for the 焖 |
| 清炒荷兰豆 | OK, less crisp | OK, less crisp |
| 干锅土豆 (dry stir) | Risk (steam trapped) | **Possible**: open, up to 240 °C |
| 青椒炒鱿鱼, 酸辣土豆丝 (high heat, ≤60 s) | Poor | Risk at 2–2.4 kW (inferred); comm. drum 3.5 kW is better |
| Blanch and drain (白灼, 焯水) | **Cannot drain** without lifting the pot | **Tilt over a colander set on a bowl**: food and water come out together, and the colander separates them |
| 勾芡 by camera | Lid hides the food | Possible: slurry from a cup, the drum mixes, the camera sees in through the open mouth |
| Hot oil poured over (3–4 of 15) | Needs another heater | Pouring ≈40 g of oil from a 6 L drum: ND |
| 锅气 | "Stews, no 锅气" (J7 teardown [r15]) | Better than pot-type (open, hotter), but the drum turns at 0.4 Hz versus ≈3 Hz chef tossing [r15] |
| Steaming, soups | Not this class (stew pot / steamer) | Not this class |

---

## 3. Top candidates for a robot-loaded, robot-controlled setup

### Candidate 1: a 6 L home induction drum stir-fryer (best fit)
- **Model:** 德莱利 CM-800 or the 1688 "德国IH多功能炒菜机家用商用滚筒式" (¥1,300–1,499). The German Pool ISF-622/623 has the clearest published specs for the same design.
- **What the arm does:**
  1. **Loads:** pours cups and baskets into the open drum mouth while the body sits at 45–60°. It can also drop items in mid-cook, because the mouth is open.
  2. **Controls:** presses the start and heat keys on the panel. Whether the panel is touch, "infrared" or mechanical is ND (see §4). A smart plug serves only as a kill switch.
  3. **Plates:** puts a plate in a holder under the mouth, grips the body or a 3D-printed handle adapter, and **swings the body to 135°**. Then it swings the body back to the stir angle. The body turns on its own pivot, so nothing is lifted or carried.
  4. **Drains:** tilts the drum over a colander set on a bowl.
  5. **Cleans:**
     - either rinses in place: water from the jug, a drum rotation, then a tilt into a waste basin;
     - or twists the inner pot out and carries it to the sink. This needs a rim adapter, and the pot's mass is ND.
- **What it removes from the arm:**
  - every spatula stroke: 13.2 of 69.2 arm-minutes over 3 meals [r19];
  - the spatula rest round trips: 6.4 min [r19];
  - the 2.95 kg wok lift, carry and 90° tip, which is the binding 6.47 of 7 N·m PGC case;
  - the stirring keep-out and plume rules.
- **Arm-time saving:** R19's O3a estimate was −25 to −33 min per 3 meals, assuming a motorised tilt. With a hand tilt, one short tilt motion per dish remains. That is not re-modelled.
- **Costs:**
  - 2.0–2.4 kW against today's 3.5 kW;
  - a non-stick drum at ≤240 °C;
  - a slow drum;
  - about 31–36 × 37–39 cm of counter space.

### Candidate 2: a small commercial tabletop drum, 220 V and 3.5 kW
- **Model:** Chefmax CM05-DL-TGS20/26, a 赛米控 260 mm desktop unit, or a 1688 tabletop unit (¥4,800–10,712).
- **Arm role:** the same as candidate 1. The tilt is in **13–20 manual angle steps** (Chefmax). The handle or handwheel form is ND.
- **Advantages:** the same heat as today's concave cooker; a stainless drum with no coating, so better for 爆炒.
- **Costs:**
  - 52.5 × 47.5 × 53 cm;
  - a 16 A circuit;
  - heavier (weight ND);
  - specs come from one low-quality reseller snippet.

### Candidate 3: a commandable pot-type machine for the slow one-pot dishes (side unit, not the wok replacement)
- **Model:** 九阳 / Solista SD-CJ01. It is the only home stir-fryer with a documented command interface: MIoT start, DIY start with temperature, heat and time, pause/resume, and a status/phase readout. Whether it is still sold is ND.
- **Fallback:** 美的 PY18-X1S (Wi-Fi app, no public API) or 九阳 CJ-A9 (buttons).
- **What the arm does:**
  - opens the lid or uses the feed port, and drops the food in;
  - starts it by MIoT or a key press;
  - at the end, lifts the inner pot by its handle and pours. This keeps a pot lift; the pot's mass is ND.
- **What it gives:** 红烧肉 (40 min) and similar dishes run unattended in parallel, and the drum or wok stays free for the quick dishes.

### Watch list: 海尔 CR3
- **What it does:** auto lid, 4 ingredient bins, 8 seasonings, 3.5 kW, steam self-rinse.
- **If it also tips out by itself or exposes the pot:** the arm would only fill the bins and set the plate.
- **Unknown today:** price, plating method and size. Re-check when it goes on sale.

---

## 4. Gaps
- **Tilt force and torque** of the drum bodies are not published (the maker says only "輕力"). They are needed for the arm and PGC check. Measure before buying, or ask the user.
- **Whether the 6 L drum class tilts by motor:**
  - German Pool ISF-622 (maker) and the 2018 德莱德利 review say the tilt is by hand;
  - the 1688 and Amazon listings are unclear;
  - one Amazon listing claims "without manual operation". It is unverified.
- **Panel type and power-cut behaviour:**
  - whether panels are mechanical, capacitive or infrared touch is ND for every drum and pot model;
  - whether they resume after a power cut is ND. One search snippet said "断电…自动程序又会重新开始", source unclear.
- **Real temperatures and 锅气** of the drum class: no 2024–2026 review found. The only hands-on review is from 2018.
- **Mainland retail prices:** JD, Tmall and 1688 detail pages could not be read, so prices are 1688 market-list or smzdm deal figures. German Pool is a Hong Kong product (HK$, sold out).
- **Inner-pot mass and grip** for the sink rinse: ND.
- **Haier CR3** price and plating; the maker and specs of **JD 七鲜**'s robot: ND.
- **Specs from weak sources:** the Chefmax and ATEAGO specs come from single reseller snippets. The tilt actuation of the 赛米控 desktop drum is ND.
- **Pages that would not load:** zhihu, baike, JD and 1688 item pages, Amazon item pages, the CLP, hkele and Fortress (HK) stores, chefsdeal, robotshop item pages.
