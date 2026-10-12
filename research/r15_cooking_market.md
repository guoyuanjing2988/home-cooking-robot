# R15: Heat source, auto-stir machines, stir-fry data, wok thermal and safety facts

Date: 2026-10-11. Research was read-only, using web search and fetch. I did not log in, add to cart, buy, or contact any seller.

**Context.** The setup is one UR5e (5 kg, IP54, rated 0–50 °C) with a DH PGC-140-50 gripper, on a tethered cart. The cart docks in front of an L-shaped counter in Singapore. The kitchen has a 4-burner gas hob under a slim hood. The goal is Wang Gang (美食作家王刚) recipes: 翻炒, 爆香, 煸, 烧/焖/炖 with a lid, 勾芡, 润锅 then pouring the oil out, 滑油, edge pours, 关火/离火 additions, and plating from the wok. Deep frying goes to a separate fryer and rice to a rice cooker.

**Tags**

| Tag | Meaning |
|---|---|
| **[M]** | Read in a primary source: maker page, manual, spec sheet, regulator page, or paper. |
| **[O]** | Read in a secondary source: news, review, or reseller. |
| **[O, snip]** | Seen only in a search-result snippet. Weaker. |
| **inferred** | My own calculation or engineering judgement. Not a sourced fact. |

**Prices** are in the source currency. "Not found" means I looked and found nothing usable.

**Coverage limits (read first)**
- **Blocked (HTTP 403, captcha or 410):**
  - royalsocietypublishing.org and PMC, so I could not read the full Ko & Hu wok-toss paper;
  - theverge.com (Posha review), mi.com support pages, malaymail;
  - robotshop, chefsdeal, china.org.ru (drum machines), hkele.com.hk (Miele and Gaggenau HK prices), miele.de, cosmosmagazine, atlasobscura.
- **Not tried:** Taobao, JD and Tmall (they need login). So Chinese prices come only from smzdm or cnpp.
- **Scanned PDFs:** some Japanese gas-hob manuals and one Osaka plume paper are image or odd-font scans. I could not read their numbers.

---

## 0. Bottom line

| Question | Deciding facts found | Src |
|---|---|---|
| Can induction match the home gas wok burner? | **Yes, on delivered heat.** Gas: 5.0 kW on LPG or 3.8 kW on town gas, at ≈32% efficiency (water) and ≈23% (sauté). Induction: 3.3–3.7 kW at 83–86% (water) and 48–54% (sauté). So gas delivers ≈0.9–1.6 kW to the pan and a 3.5 kW induction unit ≈1.7–3.0 kW (inferred) | [Frontier 2019](https://www.caetrm.com/media/reference-documents/Induction-Range-Final-Report-July-2019.pdf), [Fujioh manual](https://www.fujioh.com/sg/wp-content/uploads/2023/02/Manual_GS25_20221101.pdf) |
| Concave (凹面) induction | Common in China at 2.2–3.5 kW: 美的 MC-E35D2 at ¥320–599, 九阳 N3501 at ¥375. US commercial Avantco IWC35: 3.5 kW, temperature mode 60–238 °C, US$230. **None of them document a remote or serial interface.** 3.5 kW / 230 V = 15.2 A, so it needs a 20 A circuit (inferred) | [smzdm](https://www.smzdm.com/p/179328503/), [cnpp](https://www.cnpp.cn/focus/231932.html), [Avantco](https://www.webstaurantstore.com/avantco-iwc35-countertop-wok-induction-range-cooker-208-240v-3500w/177IWC35.html) |
| A cooker the robot PC can command | **Xiaomi 米家电磁炉2** (flat, not concave): its MIoT spec has `加热档位` 0–99 **R/W**, power on/off R/W, mode R/W, and `实时温度` read-only. Bosch/Siemens Home Connect: "Program support is currently not planned" for cooktops | [MIoT spec](https://home.miot-spec.com/spec/chunmi.ihcooker.v2), [Home Connect](https://api-docs.home-connect.com/programs-and-options/) |
| Home auto-cook machines for 锅气 | Maximum temperatures: Thermomix TM7 160 °C, Multo 130 °C, Xiaomi cooking robot 120–180 °C, Tineco 食万 210–230 °C, 九阳 J7 "<200 °C". Lids are closed while stir-frying (J7: mandatory). A J7 teardown says it **stews and gives no 锅气** | [J7 teardown](https://post.smzdm.com/p/a83dp03q/), [TM7](https://thermomix.com/blogs/news/whats-new-in-thermomix-tm7-innovations-that-make-a-difference) |
| Wok toss kinematics | Period 0.3 s (≈2.7–3.3 Hz), 5 chefs, wok ≈2 kg with food. Power scales with f³. The wok always touches the stove rim, which acts as a fulcrum. **The amplitude was not readable** (paper blocked). Spyce drums turn at only ≈0.5 Hz | [Ko & Hu abstract](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1098/rsif.2019.0622?fields=title,abstract,year,venue,openAccessPdf), [Hu lab](https://hu2.me.gatech.edu/Ko/wp-json/wp/v2/pages/19), [ZME](https://zmescience.com/science/the-physics-of-fried-rice) |
| Temperature margins | Wok bottom on a gas burner can exceed 750 °F (399 °C). Oil auto-ignition is 406–435 °C. Safety cut-offs: Japanese Si sensor 250 °C, City Energy hob 280 °C, typical induction dry-burn ≈280 °C | [ATK](https://www.americastestkitchen.com/articles/2189-the-science-of-stir-frying-in-a-wok), [UMD](https://drum.lib.umd.edu/handle/1903/11333), [edgeprop](https://www.edgeprop.sg/property-news/city-energy-rolls-out-safety-equipped-gas-hob-curb-unattended-cooking-fires) |
| Gas in Singapore | Gas work is only by City Energy or a Licensed Gas Service Worker (LGSW). Buy cookers with the SAFETY Mark. The flame-failure device (FFD) needs the knob held in for 5 s after ignition. Unattended cooking caused 318 of 1,051 home fires in 2025 | [EMA](https://ema.gov.sg/consumer-information/gas/gas-safety), [Fujioh](https://www.fujioh.com/sg/wp-content/uploads/2023/02/Manual_GS25_20221101.pdf), [edgeprop](https://www.edgeprop.sg/property-news/city-energy-rolls-out-safety-equipped-gas-hob-curb-unattended-cooking-fires) |
| Plume vs the UR5e's 50 °C rating | No measured wok-plume data found. Heskestad plume estimate (inferred), on the plume axis 30 / 50 cm above the wok rim: **gas ≈175 / 115 °C, induction ≈90 / 67 °C** (30 °C room). Both exceed 50 °C on the axis. About 20 cm off-axis, both are close to room temperature | §5.4 |

---

## 1. Heat source

### 1.1 Concave (wok-shaped) induction cookers and hobs

**What "concave" means.** The glass is shaped like a bowl, with a bowl-shaped coil under it. Only a round-bottom wok of matching curvature couples well. A flat pan heats poorly or not at all [O, snip, [pconline 77552](https://best.pconline.com.cn/guide/77552.html)]. Buying guides say:
- the coil should be ≥180–200 mm [O, [pconline 77549](https://best.pconline.com.cn/guide/77549.html)];
- coils in 3–3.5 kW units are often ≥260 mm, and bowl depth and curvature differ by brand [O, snip, [pconline 77552](https://best.pconline.com.cn/guide/77552.html)].

| Product | Type | Power | Coil / wok | Control | Temperature sensing / limits | Price | SG availability | Src |
|---|---|---|---|---|---|---|---|---|
| 美的 MC-E35D2 | Home countertop, concave | 3500 W | Concave panel; size not found | 10 power levels; knob/touch not stated | "智能温控, 防干烧, 过热保护". Values not found | ¥319.81 promo on 天猫 (list ¥599), Jul 2024 | Not found | [O, [smzdm](https://www.smzdm.com/p/179328503/)]; [O, snip, [zol](https://jd.zol.com.cn/1216/12166269.html)] |
| 美的 MC-30TC01 | Home/light commercial, concave, wok included | Not found | "锅灶一体" | Not found | Not found | ¥689 | Not found | [O, [cnpp](https://www.cnpp.cn/focus/231930.html)] |
| 九阳 N3501 | Home, deep concave, iron wok included | 3500 W | "深凹弧面" | Not found | Not found | ¥375 | Not found | [O, [cnpp](https://www.cnpp.cn/focus/231932.html)] |
| 苏泊尔 | Only flat 2200 W units found (C22-IH68E8, C22-IA626D, …) | 2200 W | Flat | 8–9 levels, touch | — | ¥109–287 | — | [O, [cnpp](https://www.cnpp.cn/focus/231931.html)]. **No concave Supor model found** |
| 德玛仕 DMS-DCL-BC-35G1 / BC-3500A / TC-3500D | Commercial concave, single-phase 220 V | 3500 W | Copper coil | Not found | Not found | Not found | Not found | [O, snip, [Suning](https://m.suning.com/brand/C279-501437.html)] |
| Avantco IWC35 (US) | Commercial countertop wok induction | 3500 W, 208–240 V, NEMA 6-20P | ≤14" wok (36 cm). Concave surface not stated | Digital. 10 power levels **or temperature mode** | **140–460 °F (60–238 °C)**. Standby when the pan is lifted | US$229.99 | US only | [O, [Webstaurant](https://www.webstaurantstore.com/avantco-iwc35-countertop-wok-induction-range-cooker-208-240v-3500w/177IWC35.html)] |
| CookTek wok 3.5 kW (US) | Commercial wok induction | 3500 W | Wok bowl | — | 85–425 °F | Not found | US | [O, snip, [chefsdeal](https://www.chefsdeal.com/p/induction-wok-burners/cooktek-htf-9500-wk35-1)] |
| Midea MIC3400WK (US) | Commercial, recessed wok bowl | 3400 W | 34 cm wok | — | — | Not found | US | [O, snip, [Brama](https://bramainc.com/products/midea-mic3400wk-34cm-induction-wok)] |
| **Gaggenau VI 414 111** | Built-in Vario induction, made for round-bottom wok + wok ring | 2.2–3.3 kW, booster 3.7 kW | Zone Ø21 cm, auto-expands to Ø26 and Ø32 cm. Wok WP 400 001: Ø36 cm, 6 L, multilayer, round bottom | Knob, 12 levels | **Frying sensor function** | **Discontinued.** VI414110: HK$33,000 (HK) | Gaggenau is sold in SG; SG price not found | [M, [Gaggenau](https://www.gaggenau.com/gb/en/mkt-product/VI414111)]; [O, snip, [hkele](https://hkele.com.hk/en/VI414110)]; [O, snip, [viva](https://viva-interiors.com/en/catalogs/gaggenau/the-models-and-dimensions-2024/24398/page-118)] |
| **Miele CS 1223-1 I** CombiSet | Built-in, **concave ceramic bowl** | 2400 W, booster 3200 W | Ø300 mm. Wok pan CSWP 1400 fits the trough | Not found | Not found | Not found | Miele is sold in SG; SG model and price not found | [O, snip, [appliancesdirect](https://www.appliancesdirect.co.uk/p/cs1223i-1/miele-cs1223i1-1-zone-electric-hob-hob)]; [O, snip, [Miele UK](https://miele.co.uk/product/7132780/wok-pan-for-combiset-cswp-1400)] |
| Singapore mainstream built-ins: Bosch, Fujioh, Rinnai, Tecno, EF | **No concave wok-induction model found.** Hybrids exist: induction on one side, gas on the other "for round bottom wok" | 2-zone 60 cm units ≈3.0–3.5 kW "often requiring a dedicated 16A or 20A circuit" | — | — | — | — | Yes (flat only) | [O, snip, [Megafurniture](https://megafurniture.sg/blogs/articles/choosing-the-right-induction-hob-for-a-singapore-home)]; [O, snip, [Megafurniture hobs](https://megafurniture.sg/blogs/articles/best-hob-singapore-top-picks-for-a-hassle-free-cooking-experience)] |
| Commercial 3500 W induction (flat) | Portable | 3500 W | Flat | — | — | **SGD 230** new, 130 used | Carousell SG | [O, snip, [Carousell](https://www.carousell.sg/induction-cooker/q/)] |

**Control interfaces and protocols**

| Device | Interface | What a robot PC can do | Src |
|---|---|---|---|
| **米家电磁炉2** `chunmi.ihcooker.v2` (flat, 2100 W, 99 levels) | Wi-Fi, MIoT | `开关` bool **R/W/N**; `烹饪模式` **R/W** (手动/火锅/蒸煮/汤粥/炒菜/煎炸); **`加热档位` uint8 0–99 R/W/N**; `实时温度` 0–255 R/N; `设定温度` 0–255 R/N. Actions: start-cooking, pause-cooking, cancel-cooking, set-menu, next-step-cooking and others | [M, [miot-spec](https://home.miot-spec.com/spec/chunmi.ihcooker.v2)]; [O, snip, [rokomari](https://www.rokomari.com/electronics/531816/mijia-induction-cooker-2-mcl02m)] |
| 米家智能超薄电磁炉 `xiaomi.ihcooker.cmg28` | Wi-Fi, MIoT | Fire level 0–99 is **read-only**. Mode R/W. Start, pause and cancel actions take recipe data | [M, [miot-spec](https://home.miot-spec.com/spec/xiaomi.ihcooker.cmg28)] |
| TOKIT 智能热敏炉 `tokit.ihcooker.tkpro1` | Wi-Fi, MIoT | Temperature −30–100 °C R/N and cancel only. No power control | [M, [miot-spec](https://home.miot-spec.com/spec/tokit.ihcooker.tkpro1)] |
| 25 MIoT induction models (Mijia, TOKIT, VIOMI built-in hobs, …) | MIoT | All listed MIoT induction models found are flat cookers or hobs | [M, [miot-spec list](https://home.miot-spec.com/s/ihcooker)] |
| IKEA TILLREDA 2 kW (DIY) | Internal UART between panel and power board | 9600 baud, 8N1. A 10-byte frame every 100 ms. 5 bits encode power (32 values; the panel uses 0–9). An ATmega328PB intercepts the bus. The author warns of mains-voltage risk | [O, [Hackaday](https://hackaday.io/project/203350-diy-pwm-controlled-ikea-tillreda-induction-cooktop)] |
| Concave Chinese units, IR remotes | — | **Not found.** No app, IR, or serial documentation for any concave unit | — |

**Built-in limits that matter.** Typical induction "防干烧" protection cuts heating when the plate is above ≈280 ± 10 °C [O, snip, [pconline ask](https://www.pconline.com.cn/ask/231898.html)]. On some units this could interrupt 润锅 or dry-wok heating (inferred).

### 1.2 Hobs with pan or oil temperature sensors

| System | Sensor principle | Range / levels | Pan requirement | Third-party command? | Src |
|---|---|---|---|---|---|
| Bosch PerfectFry | Regulates frying-pan temperature. Visual and audible alert at the set level. Neff/Siemens say "sensors under the glass ceramic" | Series 8: **5 levels**. Series 6: 4 levels. Level names: very low → high | Bosch recommends its "system pan": 15, 19, 21 or 28 cm (HEZ3902x0) | Brochure recipe metadata has keys `Cooking.Hob.EnumType.FryingSensorLevel.Level01…05`. **Not writable** (see Home Connect row) | [M, [Bosch](https://www.bosch-home.com/mt/en/c/spotlight/blt5efb655d24c1f6d5/bosch-innovations/electric-cooktop)]; [M, [Bosch brochure](https://media3.bosch-home.com/Documents/8407182_BOFSCS5I_9001116054_EN.pdf)]; [O, snip, [Neff](https://www.neff-home.com/uk/service/support/hobs/what-is-a-frying-sensor)] |
| Siemens fryingSensor (Plus) | Not stated on page | "eleven temperature options ranging from 70°C to 220°C" | "specially selected non-stick frying pans" | As Bosch | [M, [Siemens](https://www.siemens-home.bsh-group.com/uk/inspiration/innovation/frying-sensor)] |
| Miele TempControl | "Sensors embedded in the ceramic screen" detect the pan's material and temperature | 3 ranges: **160 / 200 / 220 °C**. Miele recommends range 3 (220 °C) for wok | Any induction pan | Not found | [M, [Miele press release 2017](https://www.miele.co.nz/media/ex/nz/Press/MieleTempControlinductioncooktop_2017.pdf)] |
| Hestan Cue | Sensor in the pan; Bluetooth in the handle; 1600 W induction burner | 100–500 °F | Hestan smart pans only | Phone app only; no public API found | [O, snip, [Cook's Warehouse](https://cookswarehouse.com/hestan-cue-gen-2-smart-cooking-system-with-chefs-pot)]; [O, snip, [Digital Trends](https://digitaltrends.com/home/hestan-cue-review)] |
| Breville/PolyScience Control Freak | Through-glass sensor plus a clip-on probe. 20 readings/s | 30–250 °C, ±1 °C. 100–1800 W | Flat induction pans | Not found | [O, snip, [sousvidetools](https://www.sousvidetools.com/thepolysciencecontrol-freak)] |
| Melexis MLX90617 (component) | IR through the glass ceramic. An LED/light sensor estimates pot emissivity | Pot base 70–250 °C | — | Component for OEMs | [O, [Electropages](https://www.electropages.com/2025/01/infrared-thermometer-revolutionises-induction-hob-design)] |
| **Home Connect API** (Bosch, Siemens, Neff, Gaggenau) | — | — | — | Cooktop: "**Program support is currently not planned to be released.** Selected and active program can be already requested." So it is read-only. openHAB exposes generic `power_state` R/W channels for hobs, but the official API does not support starting programs | [M, [Home Connect API docs](https://api-docs.home-connect.com/programs-and-options/)]; [O, [openHAB](https://www.openhab.org/addons/bindings/homeconnect/)] |
| Japan "Siセンサー" gas hobs (reference) | Spring-loaded probe under the pot | Pot bottom limited to **250 °C**. A high-temperature stir-fry mode still shuts off after ≈30 min. Mandatory on all burners since 2008 | Flat pot bottom | No | [O, snip, [sunrefre](https://www.sunrefre.jp/gastable/contents/safety_select.html)]; [O, snip, [Paloma manual](https://www.paloma.co.jp/downloads/%E7%9F%A5%E8%AD%98%E6%83%85%E5%A0%B1/%E5%8F%96%E6%89%B1%E8%AA%AC%E6%98%8E%E6%9B%B8/48-30381-000-00.pdf)] |

### 1.3 Keeping the existing gas hob

**Flame-failure device (FFD) behaviour**

| Fact | Value | Src |
|---|---|---|
| Ignition on Fujioh FH-GS25 (sold in SG) | Push and turn to large flame. "**hold down the control knob for 5 seconds** to allow the flame to heat up the thermocouple" | [M, [Fujioh manual](https://www.fujioh.com/sg/wp-content/uploads/2023/02/Manual_GS25_20221101.pdf)] |
| After a flame-out | "do not attempt to re-ignite the burner for at least one minute" | [M, same] |
| Rinnai | Hold 5 s after lighting | [O, snip, [Rinnai manual](https://www.notice-facile.com/en/manual/868583/rinnai+rb-93us)] |
| Thermocouple and valve drop-out | ≈25–30 mV. The valve closes ≈10–15 s after the flame dies | [O, snip, [Kaff](https://kaff.in/articles/kitchen-safety-first-understanding-the-flame-failure-device)] |
| Catering FFDs | Hold up to 30 s. Closing delay up to 60 s | [O, snip, [gasproducts](https://www.gasproducts.co.uk/catering/flame-failure-devices.html)] |
| Knob torque | **Not found.** EN 1106 (manual gas taps) is paywalled | [O, snip, [iTeh EN 1106](https://iteh.es/catalog/standards/sist/4ee36302-9e88-4652-a9cf-5f500931e102/sist-en-1106-2022)] |

**What this means for a robot (inferred).**
- The arm must push, turn and hold for ≥5 s at each ignition. That ties up the arm.
- If the flame blows out (a boil-over, or the hood's draught), gas may flow for 10–60 s before the FFD closes. The robot must then wait ≥1 min before relighting.
- Turning a knob without pushing it in does not ignite.

**Knob actuators and retrofit kits**

| Product | How it works | Status / price | Src |
|---|---|---|---|
| Inirv React | Motorised replacement knobs plus a ceiling sensor (smoke, gas, motion). BLE between knobs and sensor, Wi-Fi to the phone. App can turn burners on/off and adjust them | 2017 launch. Current availability not found | [O, snip, [New Atlas](https://newatlas.com/inirv-react-oven-burner/47616/)]; [O, snip, [Fatherly](https://www.fatherly.com/gear/inirv-react-smart-stove-knobs/)] |
| Patents | US7156367: gas knob turned by a motor through a clutch, manual or automatic. US11162686: system for turning off stove knobs | Patents only | [O, snip, [US7156367](https://patents.google.com/patent/US7156367)]; [O, snip, [US11162686](https://patents.google.com/patent/US11162686)] |
| iGuardStove (gas) | Solenoid valve on the gas line plus a motion sensor. Cuts off after 5 min with no motion | Sold in US/CA | [O, snip, [Firefighting in Canada](https://www.firefightingincanada.com/equipment/iguardfire-creates-automatic-stove-shut-off-device-21891)] |
| FireAvert (gas) | Listens for the smoke-alarm sound. After a 30 s delay, closes a solenoid valve | Sold in US | [O, snip, [FireAvert](https://fireavert.com/products/auto-stove-shutoff-gas)] |
| 米家定时燃气灶 3 Pro 防干烧版 (China, natural gas) | **Pressure-sensing titanium probe** reads wok temperature and cuts gas on dry burn. 5.2 kW. 1–180 min timer per burner. App remote ignition: not mentioned | ¥2,299 (launch ¥1,899) | [O, [IT之家](https://www.ithome.com/0/941/210.htm)] |
| **City Energy "Küche" intelligent gas hob (Singapore)** | Thermistor. **Gas cut-off above 280 °C.** FFD. App with timers and remote shut-off "within safety limits" | May 2026. Supplied to developers as a built-in fitting. Retail "at a later stage". No price | [O, [EdgeProp](https://www.edgeprop.sg/property-news/city-energy-rolls-out-safety-equipped-gas-hob-curb-unattended-cooking-fires)] |

**Singapore rules**

| Rule | Text / value | Src |
|---|---|---|
| Who may work on gas | "Gas installation works can only be carried out by City Energy or a Licensed Gas Service Worker." Town-gas on/off only by City Energy or its agents. Check every 5 years | [M, [EMA gas safety](https://ema.gov.sg/consumer-information/gas/gas-safety)] |
| Appliances | Installing, testing, maintaining and repairing gas cookers and burners must be done by an LGSW, who certifies the appliance safe. Using an unlicensed worker is an offence: fine up to S$10,000 or jail | [O, snip, [EMA 2008 release](https://ema.gov.sg/news-events/news/media-releases/2008/new-requirements-under-the-gas-act-and-gas-supply-regulations-with-effect-from-14-february-2008)] |
| Code of practice | LGSWs must follow SS 608 (latest SS 608:2024) | [O, snip, [EMA circular](https://elise.ema.gov.sg/eguides/Circular_RD_G02_2025_ELISE.pdf)] |
| Buying | "Always purchase a gas cooker with a SAFETY Mark label" | [M, [EMA](https://ema.gov.sg/consumer-information/gas/gas-safety)] |
| CPSR (2018) | New gas-cooker registrations must be tested up to 31 mbar for town gas | [O, snip, [CPSO circular](https://www.consumerproductsafety.gov.sg/files/circulars/2018-08-01-circular.pdf)] (now 404) |
| Fire statistics | 2025: unattended cooking caused 318 of 1,051 residential fires (30%), per SCDF | [O, [EdgeProp](https://www.edgeprop.sg/property-news/city-energy-rolls-out-safety-equipped-gas-hob-curb-unattended-cooking-fires)] |

**Inferred.** A robot turning the existing knobs from outside leaves the gas train untouched. Adding a solenoid valve, a sensor or a motor inside the hob is gas service work. That needs an LGSW and may void the SAFETY Mark approval.

### 1.4 Measured efficiency and burner power

| Test | Induction | Electric resistance | Gas | Src |
|---|---|---|---|---|
| EPRI (ACEEE 2014). Water 21 → 93 °C, large and small pots | 74.9–77.6% | 75.1–83.4% (large pot); 41.5–48.2% (small pot) | 30.2–41.7% (tested at 10 °C room) | [M, [ACEEE 9-702](https://www.aceee.org/files/proceedings/2014/data/papers/9-702.pdf)] |
| DOE/LBNL 1998 values quoted by EPRI | — | 74% | 40% | [M, same] |
| Frontier Energy for SMUD (2019). Heat-up test | **83.0–86.1%** at 3.3–3.7 kW boost | 75.5–79.3% at 2.4–2.5 kW | **31.9%** at 17 kBtu/h (5.0 kW) | [M, [Frontier report](https://www.caetrm.com/media/reference-documents/Induction-Range-Final-Report-July-2019.pdf)] |
| Frontier 2019. **Sauté test** (pan, burger), closest to a wok | **47.8–54.0%** | 38.0–54.8% | **22.8%** | [M, same] |

**Burner powers**

| Burner | Power | Src |
|---|---|---|
| Fujioh FH-GS25 ultra-rapid (wok) burner, SG | **5.0 kW on LPG; 3.8 kW on town gas.** Wok rim ≤36 cm | [M, [Fujioh manual](https://www.fujioh.com/sg/wp-content/uploads/2023/02/Manual_GS25_20221101.pdf)] |
| Miele CS 7101-1 FL dual wok burner | 4.5 kW | [O, snip, [Rowley](https://rowleyhome.co.uk/products/cs-7101-1-fl-000000000011402720)] |
| US residential gas cooktops, largest burner | 15–17 kBtu/h (4.4–5.0 kW) | [M, [Frontier](https://www.caetrm.com/media/reference-documents/Induction-Range-Final-Report-July-2019.pdf)] |
| Restaurant jet burners (Thunder Group) | 62,000–160,000 Btu/h = **18–47 kW** | [O, snip, [restaurantsupply](https://www.restaurantsupply.com/products/thunder-group-irbr003cn-32-tip-jet-burner-gas-burner-62000-to-160000-btu)] |
| Cantonese wok ranges | ≥200,000 Btu/h (≈59 kW) | [O, snip, same search] |
| Wok-range test method | ASTM F1991 (Chinese wok ranges, heat-up efficiency). Values not found | [O, snip, [ASTM](https://store.astm.org/f1991-99r21.html)] |

**Delivered heat (inferred)**, as burner power × measured efficiency:

| Heat source | Into a water pot | Into a pan or wok |
|---|---|---|
| Town gas 3.8 kW | ≈1.2 kW | ≈0.9 kW |
| LPG 5.0 kW | ≈1.6 kW | ≈1.15 kW |
| Induction 3.5 kW | ≈2.9–3.0 kW | ≈1.7–1.9 kW |
| Induction 3.0 kW (13 A plug) | ≈2.5 kW | ≈1.4–1.6 kW |

- Restaurant burners are 18–47 kW. Even at a guessed ≈20% they deliver 4–9 kW. That is a different league.
- Efficiency of a **concave** coil with a round wok was **not found**.

---

## 2. Automated stirring and cooking machines

### 2.1 Home machines

| Machine | Heat / max temperature | Stirring | Capacity | Lid while cooking | Adding mid-cook | Dispensers | Control / API | Price | 锅气 / stir-fry reviews | Src |
|---|---|---|---|---|---|---|---|---|---|---|
| **Tineco 添可 食万 3.0 Pro** | 2000 W IH, 9 levels, **room temp to 210 °C**. Thermal efficiency "81%" | Paddle "8合1大厨铲", forward and reverse | 4.5 L | Lid opens automatically to 75° | At prompts, when the lid opens (inferred) | **8 liquid boxes**: water, oil, brine, light soy, dark soy, wine, vinegar, syrup. Weighing "0.02%". Steam self-clean | App, 7.84" screen, NFC. No public API found | Not found | Maker says it cooks below the smoke point | [M/O, [China Daily](https://cn.chinadaily.com.cn/a/202209/28/WS6333d809a310817f312f02be.html)]; [O, snip, [pconline](https://product.pconline.com.cn/cooker/)]; [O, snip, [zhihu](https://www.zhihu.com/tardis/jm/art/1995826610482459579)] |
| Tineco 食万 (newer, 2025) | "230°C", "32秒" heat-up | 8-in-1 paddle | — | — | — | 8 boxes | — | — | "低于油烟点" | [O, snip, [china.com](https://m.tech.china.com/redian/2025/0826/082025_1720247.html)] |
| Tineco 食万 2.0 | — | Paddle | — | **Glass lid closed during stir-fry.** Vapour drains to a rear box | "add the ingredients when prompted" | Auto condiment box on top | App and video | ¥4,890 | Low smoke. Main ingredients added by hand | [O, [smzdm](https://post.smzdm.com/p/a4d89knl/)] |
| **九阳 J7** 炒菜机 | IH. 3 temperature points. Pan bottom kept "<200 °C" | Magnetic double-wing paddle | — | **Lid must stay closed** | Opening the lid interrupts the cycle | Seasoning by hand (screen shows amounts) | App (unreliable in test) | ¥1,999 | "**stewing**", vegetables overcooked, trapped moisture, **no 锅气** | [O, [smzdm teardown](https://post.smzdm.com/p/a83dp03q/)]; [O, snip, [zhihu](https://www.zhihu.com/tardis/jm/art/2030212084928075575)] |
| 九阳 CJ-A8 pro | 2000 W IH. "Venturi" vapour removal | Double-wing paddle | — | — | — | — | — | — | — | [O, snip, [zhihu](https://www.zhihu.com/tardis/jm/art/1995826610482459579)] |
| 美的 炒菜机 | Not found | Not found | Not found | Not found | — | — | App remote start | Not found | — | [O, snip, [pconline](https://best.pconline.com.cn/guide/91470.html)] |
| 米家智能烹饪机器人 (Thermomix type) | 2020 crowdfunding: **35–120 °C**. Later spec: 1700 W rated, **max 180 °C**. 40–12,000 rpm | Blade / stir, forward and reverse | — | Lid | — | — | Mi Home app, OTA | ¥3,999 (2020). RM 4,599 (MY) | — | [O, [IT之家](https://www.ithome.com/0/522/827.htm)]; [O, snip, [nextrift](https://nextrift.com/202325880/)] |
| 米家智能料理机 MCC01M (2024) | 1700 W | Blade | 2.2 L | Lid | — | Scale | App | Not found | — | [O, snip, [Galaxus](https://galaxus.at/en/s2/product/xiaomi-smart-kitchen-machine-with-touch-display-1700-w-kitchen-machines-23600084)] |
| Thermomix TM6 | 1000 W. 37–160 °C | Blade | 2.2 L | Lid | — | Scale | Cookidoo. No public API found | Not found | — | [O, snip, [telepolis](https://www.telepolis.pl/artykuly/testy-sprzetu/thermomix-tm6-test-recenzja-opinie)] |
| **Thermomix TM7** | **Browning ≤160 °C (320 °F).** "Open Cooking" without lid ≤100 °C (212 °F) | Blade (stopped in Open Cooking) | — | Off in Open Cooking | Yes in Open Cooking ("add ingredients as you go") | — | Cookidoo | Not found | — | [M, [Thermomix](https://thermomix.com/blogs/news/whats-new-in-thermomix-tm7-innovations-that-make-a-difference)] |
| CookingPal Multo | ≤130 °C (265 °F). 10 speeds to 5,200 rpm | Blade, auto-stir sauté | 3 L | — | — | — | App | US$799–999 | — | [O, snip, [TechHive](https://www.techhive.com/article/579529/multo-review.html)] |
| **Posha** (was Nymble / Julia) | Induction. Max temperature **not found** | 2 spatulas + 1 extended arm | "Limited ingredient capacity" | Not found | From **4 hoppers** | Spice carousel, 20 pods. Top camera with vision | Tablet and app. US$15/month subscription | US$1,750 (US$1,500 pre-order) | "really good cook". Stir-fry 锅气 not reviewed | [O, [Wikipedia](https://en.wikipedia.org/wiki/Posha_(company))]; [O, [The Spoon](https://thespoon.tech/is-posha-the-robotic-heir-to-the-thermomix-the-founder-sure-hope-so/)]; [O, snip, [Posha blog](https://www.posha.com/stories/what-a-cooking-robot-costs-in-2026---and-who-it-actually-suits)] |
| Moley | Two arms on a ceiling rail, with appliances | Robot hands | — | — | — | — | — | Moley R: £248,000. Moley X: £99,099 | — | [O, snip, [Robb Report](https://robbreport.com.au/?p=40955)] |
| Samsung Bot Chef | Two 6-DoF arms (CES 2020 demo) | Arms | — | — | — | — | — | **Concept only.** Never sold | — | [O, snip, [TechCrunch](https://techcrunch.com/2020/01/07/samsungs-knife-wielding-robotic-chef-is-all-flash/amp/)] |

**Market context.**
- China's consumer cooking-robot online sales in H1 2024 were CNY 130 M and 67,000 units, from about 25 brands.
- Tineco and the next brand held 72% (CR2).
- Tineco 食万 sold about 3,000 units/month in 2024.

Source: [O, [PKU case MKT-1-20250402-340](https://hdipp.pku.edu.cn/__local/C/75/05/CA265329D0FD92C95EE74273F52_BEB9D08B_DFC31.pdf)].

### 2.2 Commercial drum and rotary stir-fry robots

| System | Power | Drum / wok | Plating | Cleaning | Src |
|---|---|---|---|---|---|
| **Spyce** (Boston) | Induction. Food cooks at 450 °F (232 °C) | 7 woks that spin to tumble the food | Wok tilts into a bowl | Hot-water jets after each meal. NSF certified | [O, snip, [MIT Tech Review](https://www.technologyreview.com/2018/08/22/240253/engineering-lunch/amp/)] |
| Spyce drum speed vs wok tossing | Drums at **≈0.5 Hz**. Ko & Hu say this is too slow next to ≈3 Hz chef tossing | — | — | — | [O, [ZME Science](https://zmescience.com/science/the-physics-of-fried-rice)] |
| Chefmax CM05-DL-TGS20…36 | 220 V, **3.5 / 5 kW** | Pan Ø200–360 mm. 2/4–12 L. 0.2–1.5 kg per batch (smallest model) in 5–10 min. 525×475×530 mm (smallest) | Manual tilt, 13–20 angle steps | Not found | [O, snip, [china.org.ru](https://china.org.ru/product/1600173111549)] |
| ATEAGO spin cooking robot | 220 V single phase | 2.5 L, pot Ø30 cm. 462×606×790 mm | Not found | Not found | [O, snip, [RobotShop](https://ca.robotshop.com/products/ateago-ateago-automatic-spin-cooking-robot-smart-robot-cooker)] |
| Generic "drum" machines, 220 V | 2000 W IH, 3 levels | 5–6 L. 31×37×36.5 cm | 3-angle tilt | Non-stick | [O, snip, [reseller listing](https://kingfahad.sa/products/drum-cooking-machine-portable-automatic-cooking-machine-comm/211117546/)]. Low-quality source |
| Commercial "炒菜机器人" claims | "350 °C", induction ">90%" | — | Fully automatic | — | [O, snip, [CSDN](https://damodev.csdn.net/6a5c37ae10ee7a33f28ee1e6.html)] |
| Patent architecture (automatic stir-fryer) | High-frequency induction around a rotating tank | Rotary tank | Tilting unit plus receiving tank with a push rod | Cleaning unit washes the tank after tilting | [O, snip, [US 2017/0354287](https://patents.justia.com/patent/20170354287)] |
| Integrated restaurant wok robots | ≈180 kg (see R14) | — | — | — | [R14 local file](r14_storage_market.md) |

### 2.3 Stand-alone pot stirrers

Stirr: battery (4×AA) tripod stirrer with 3 speeds. Nylon legs are rated to 120 °C. US$20–70. **Not relevant for a wok.** Source: [O, snip, [Housewares Live](https://housewareslive.net/stirr-a-revolution-in-your-pan-automatic-sauce-stirrer/)].

---

## 3. Robot stir-fry literature

| Study | Key numbers | Src |
|---|---|---|
| **Ko & Hu, "The physics of tossing fried rice", J. R. Soc. Interface 2020** | 5 professional chefs. "The wok toss has a **period of 0.3 s**": translation slides the rice; rotation throws it. Ranks kinematics by fraction tossed, flight height and angular displacement. **64.5%** of Chinese restaurant chefs report shoulder pain | [M abstract, [Semantic Scholar](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1098/rsif.2019.0622?fields=title,abstract,year,venue,openAccessPdf)]. Full text blocked: [DOI](https://royalsocietypublishing.org/doi/10.1098/rsif.2019.0622) |
| Same, lab page | "**3 Hz**". Wok "≈2 kg with food". Required power rises with the **cube of frequency**. "The wok is **always touching the stove rim**" (rim as fulcrum). Chefs' phase difference is the optimum | [O, [Hu lab](https://hu2.me.gatech.edu/Ko/wp-json/wp/v2/pages/19)] |
| Same, APS DFD 2018 talk | 0.32 s cycles. Translation and see-saw rotation at the same frequency, slightly out of phase | [O, [phys.org](https://phys.org/news/2018-11-subtle-science-wok-tossing.html)] |
| Press summaries | Chefs toss **2.7 times/s**. Model optimum ≈3/s with ≈1 rad phase lag. One Chinese article says the optimum is 5/s. **These conflict**; trust the abstract's 0.3 s | [O, [Science News](https://www.sciencenews.org/?p=3084879)] (3/s, 5 chefs); [O, snip, [Cosmos](https://cosmosmagazine.com/physics/the-physics-of-fried-rice)]; [O, [ifanr](https://www.ifanr.com/1309422)] |
| Translation / rotation amplitude, accelerations | **Not found** (full text blocked). Supplementary data exist on figshare | [O, snip, [figshare](https://rs.figshare.com/collections/Supplementary_material_from_The_physics_of_tossing_fried_rice_/4828269)] |
| **Liu, Chen, Dong, Wang, Calinon, Li, Chen, "Robot Cooking with Stir-fry: Bimanual Non-prehensile Manipulation of Semi-fluid Objects", RA-L 7(2):5159–5166, 2022** | Two Franka Panda arms, 58 cm apart. **A 500 g wok** and a spatula. Left arm (wok) learned by DMP; right arm (spatula) by a "Structured-Transformer" (Graph + Transformer). Demonstrations recorded with an Xsens IMU suit. Wok cycle: push forward → rotate → pull back. Spatula switches between contact and free motion. PyBullet simulation. Top RealSense camera at 10 Hz segments the food and measures its displacement. Uses poses only, no contact forces. **No heat or real cooking reported** | [M, [arXiv 2205.05960](https://arxiv.org/pdf/2205.05960)]; [M, [Calinon page](https://calinon.ch/paper4053.htm)] |
| Utensil kinematics dataset ("Flipping food during grilling tasks", Sci Data 2022) | 2,866 flips by 4 chefs and 5 home cooks. Optical motion capture. **Spatula bending force and torsion torque** measured. Values not read (PMC captcha) | [O, snip, [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8755801/)] |
| Spatula stroke frequency in human stir-fry | **Not found** | — |
| Granular food simulation | AutomaChef (2024): differentiable MLS-MPM + Drucker-Prager, scoop/transfer/pour salt. VERAGMIL: PhysX 5 position-based dynamics, xArm7 scooping granular food. DEM of stirred brown rice (2026) | [O, snip, [arXiv 2406.09178](https://arxiv.org/abs/2406.09178)]; [O, snip, [arXiv 2608.18258](https://arxiv.org/pdf/2608.18258)]; [O, snip, [PMC12840538](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12840538/)] |
| Wok-flip machine patent | Linear actuators tilt the wok up and down to throw food into the air | [O, snip, [US7930973B2](https://patents.google.com/patent/US7930973)] |

**Toss accelerations (inferred).** A sinusoidal toss with half-stroke A at frequency f has peak acceleration a = (2πf)²·A and peak speed v = 2πf·A. **The amplitude is assumed, not sourced.**

| f | A = 3 cm | A = 5 cm | A = 8 cm |
|---|---|---|---|
| 2.7 Hz | 8.6 m/s², 0.51 m/s | 14.4 m/s², 0.85 m/s | 23.0 m/s², 1.36 m/s |
| 3.0 Hz | 10.7 m/s², 0.57 m/s | 17.8 m/s², 0.94 m/s | 28.4 m/s², 1.51 m/s |

- At 3 Hz and A = 5 cm, a 3 kg wok-plus-food needs ≈53 N of peak inertial force on top of its weight (inferred).
- This is why the one real robot study used a 0.5 kg wok.

---

## 4. Thermal facts

### 4.1 Carbon-steel wok masses (30–36 cm)

| Wok | Bottom / make | Mass | Src |
|---|---|---|---|
| Joyce Chen 14" J21-9978 | Flat, spun | 3.24 lb = **1.47 kg** | [O, snip, [Kohl's](https://www.kohls.com/product/prd-6615402/joyce-chen-14-in-carbon-steel-flat-wok.jsp)] |
| Joyce Chen 14" J20-1140 | Round, spun | 3.9 lb = 1.77 kg | [O, snip, [Kohl's](https://www.kohls.com/product/prd-6615393/joyce-chen-14-in-rounded-carbon-steel-wok.jsp)] |
| Mammafong 14" (35 cm) | Round, hand-hammered | 3.35 lb = 1.52 kg | [O, snip, [eBay](https://www.ebay.de/itm/392967884295)] |
| Craft Wok 14" 731W88 | Round, hand-hammered | 4.6 lb = 2.1 kg | [O, snip, [Walmart](https://www.walmart.com/ip/seort/613583604)] |
| Craft Wok 14" (36 cm) | Flat, 1.8 mm (15 gauge) | **2.1 kg** | [O, snip, [Scope](https://shop.scope.org.uk/collections/home-2025/products/craft-wok-traditional-carbon-steel-wok-flat-bottom-14in)] |
| Yosukata 14" | Flat, blue steel | 4.72 lb = 2.14 kg | [O, snip, [Viet World Kitchen](https://www.vietworldkitchen.com/?p=18846)] |
| Yosukata 13.5" | Flat | 4.6 lb = 2.2 kg (another listing says 3.6 lb) | [O, snip, [Walmart](https://www.walmart.com/ip/YOSUKATA-Flat-Bottom-Woks-Stir-Fry-Pans-13-5-Blue-Carbon-Steel-Wok-Preseasoned-Carbon-Steel-Skillet-Wok-for-Electric-Induction-Cooktops/15968956639)] |
| Town 34804 14" Cantonese | Flat, two riveted loop handles | 3.5 lb = 1.59 kg | [O, snip, [KaTom](https://www.katom.com/296-34804.html)] |
| Emperor's Select 14" Cantonese | Flat, 1 mm, two looped handles, induction-ready | Mass not found | [O, snip, [spec sheet](https://argo.webstaurantstore.com/documents/specsheets/emperor_s_select_478cwokcs14f.pdf)] |
| 章丘铁锅 32 / 34 cm | Hand-forged, mostly round | **Not found**. Guides say 34 cm "needs more arm strength" | [O, snip, [pconline](https://best.pconline.com.cn/guide/71563.html)] |

**Summary (inferred).** 30–36 cm carbon-steel woks weigh **1.5–2.2 kg**. With 0.5–1 kg of food that is **2.0–3.2 kg**. Ko & Hu's "≈2 kg with food" suggests chefs use lighter woks or smaller portions.

### 4.2 Wok and pan temperatures

| Situation | Temperature | Src |
|---|---|---|
| Wok bottom on a conventional home gas burner | "can exceed 750 degrees" °F (≥399 °C) | [O, [America's Test Kitchen](https://www.americastestkitchen.com/articles/2189-the-science-of-stir-frying-in-a-wok)] |
| Miele recommendation for wok on TempControl | 220 °C | [M, [Miele](https://www.miele.co.nz/media/ex/nz/Press/MieleTempControlinductioncooktop_2017.pdf)] |
| Spyce woks | 450 °F (232 °C) | [O, snip, [MIT Tech Review](https://www.technologyreview.com/2018/08/22/240253/engineering-lunch/amp/)] |
| Tineco 食万 / 九阳 J7 | ≤210–230 °C / "<200 °C" | §2.1 |
| Ko & Hu ("food undergoes 1200 °C") | This is flame-gas temperature, not wok metal | [M abstract](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1098/rsif.2019.0622?fields=title,abstract,year,venue,openAccessPdf) |
| Measured wok surface during stir-fry (thermocouple or IR study) | **Not found** | — |

### 4.3 Smoke points and ignition

| Oil / fat | Smoke point | Src |
|---|---|---|
| Peanut, refined / unrefined | 232 °C / 160 °C | [M, [Wikipedia table](https://en.wikipedia.org/wiki/Smoke_point)] |
| Canola / rapeseed, refined | 204 °C | same |
| Canola, expeller-pressed | 190–232 °C | same |
| Chinese 压榨/浓香 菜籽油 specifically | **Not found** | — |
| Soybean, refined | 234 °C | same |
| Lard | 190 °C | same |
| Sesame, unrefined / semi-refined | 177 °C / 232 °C | same |
| Variability | Smoke point depends mainly on free fatty acids and proteins, so it drops as oil is reused | same |
| **Auto-ignition (UMD tests)** | **Canola 424 °C; "vegetable" 406 °C; olive 435 °C. Canola flame point 379 °C** | [M abstract, [UMD](https://drum.lib.umd.edu/handle/1903/11333)] |

**Inferred.** The gap between a home-gas wok bottom (≥399 °C) and oil auto-ignition (406–435 °C) is only tens of °C. 润锅 to smoking (≈200–235 °C) is safe. An empty wok left on a gas flame is not.

### 4.4 IR thermometry and contact sensors

| Fact | Value | Src |
|---|---|---|
| Steel emissivity, 8–14 µm | Polished ≈0.1. Oxidised 0.7–0.9 | [O, snip, [Optris](https://optris.com/us/technology/emissivity-table/)] |
| Cast iron emissivity, 8–14 µm | Unoxidised ≈0.2. Oxidised 0.6–0.95 | same |
| Food and water | Food/organics 0.95–0.97. Water 0.95. Stainless 0.59. Freshly rolled steel 0.24 | [M, [ThermoWorks](https://blog.thermoworks.com/emissivity/)] |
| ThermoWorks advice | Calibrate IR readings against a surface probe | same |
| Under-glass sensing problem | Hob control usually reads the back of the glass. That lags, and misses concave or convex pans | [O, [Electropages](https://www.electropages.com/2025/01/infrared-thermometer-revolutionises-induction-hob-design)]; [O, snip, [Sensors 2025 paper](https://citedrive.com/en/discovery/a-new-approach-for-infrared-temperature-measurement-sensor-systems-and-temperature-control-for-domestic-induction-hobs)] |
| IR through glass with emissivity estimate | Melexis MLX90617. Pot base 70–250 °C | [O, [Electropages](https://www.electropages.com/2025/01/infrared-thermometer-revolutionises-induction-hob-design)] |
| Contact probe on gas hobs | Japan Si sensor: 250 °C. Mijia 3 Pro: titanium pressure probe on the wok | [O, snip, [sunrefre](https://www.sunrefre.jp/gastable/contents/safety_select.html)]; [O, [IT之家](https://www.ithome.com/0/941/210.htm)] |
| Induction temperature-sensing patent | US5283412 | [O, snip, [patent](https://patents.google.com/patent/US5283412)] |

**Solutions (inferred)**
- Keep the wok **well seasoned**, so the black oxide layer has ε ≈0.8–0.9.
- Aim the IR sensor at the **food or oil**, not at bare shiny metal.
- Calibrate against a thermocouple touching the wok.
- On a polished spot, a gun set to ε = 0.95 would read hundreds of °C too low.

---

## 5. Safety around hot oil

### 5.1 Automatic fire suppression and stove guards

| Product | Trigger | Action | Limits | Src |
|---|---|---|---|---|
| **StoveTop FireStop Rangehood** | Fuse needs "direct, sustained contact with a flame" | Drops ≈9 oz (255 g) dry powder **by gravity**, unpressurised | Oil depth ≤3/8" (9.5 mm). Mount 27–35" (69–89 cm) above burners. Two units for a 4-burner hob. 6-year life. NRTL-tested | [M, [spec sheet](https://pdf.lowes.com/productdocuments/ffc35b6f-06cf-4059-ae61-3acea9574ed4/11006019.pdf)] |
| Thermal glass-bulb variant (patent) | Glass bulb bursts, spring opens the lid | Powder release | — | [O, snip, [patent](https://patents.justia.com/patent/20150238790)] |
| **Innohome Stove Guard** | Thermistor + IR photodiode under the hood. Uses temperature level and rate of rise; learns cooking habits | Cuts **electric** power to the cooker by RF | Electric cookers only (UK). Gas version "in development" | [O, snip, [Safelincs](https://safelincs.co.uk/innohome-stove-guard-sgk510)]; [O, snip, [A&D](https://architectureanddesign.com.au/product/innohome-stove-guard)] |
| **FireAvert** | Hears the smoke alarm, then waits 30 s | Cuts power, or closes a gas solenoid | Needs a smoke alarm in range | [O, snip, [FireAvert](https://fireavert.com/pages/senior-stove-shutoff)] |
| iGuardStove | 5 min with no motion | Power or gas solenoid off | — | [O, snip, [FFIC](https://www.firefightingincanada.com/equipment/iguardfire-creates-automatic-stove-shut-off-device-21891)] |
| Inirv React | Gas, smoke or inactivity | Motorised knobs turn off | — | [O, snip, [New Atlas](https://newatlas.com/inirv-react-oven-burner/47616/)] |
| City Energy Küche (SG) | Thermistor > 280 °C | Gas cut-off. App remote shut-off | Developers only (2026) | [O, [EdgeProp](https://www.edgeprop.sg/property-news/city-energy-rolls-out-safety-equipped-gas-hob-curb-unattended-cooking-fires)] |
| Japan Si sensor (all burners since 2008) | Pot bottom 250 °C | Lowers flame or shuts off | Heat-sensing stoves cut Japanese cooking fires from 4,507 to 3,719 in two years | [O, [EdgeProp](https://www.edgeprop.sg/property-news/city-energy-rolls-out-safety-equipped-gas-hob-curb-unattended-cooking-fires)]; [O, snip, [sunrefre](https://www.sunrefre.jp/gastable/contents/safety_select.html)] |
| Home range-hood wet-chemical systems (commercial UL 300 type) | Not found for SG homes | — | — | — |

### 5.2 Detection

- SCDF: a Home Fire Alarm Device (smoke or heat detector) is **mandatory** in new homes with plans submitted from 1 June 2018. Smoke detectors are recommended as primary protection. Source: [O, snip, [SCDF](https://www.scdf.gov.sg/home/fire-safety/home-fire-alarm-device-(hfad))].
- A kitchen-specific rule (e.g. heat detector, not smoke) was **not found**.

### 5.3 Cobot covers

| Cover | Rating | Src |
|---|---|---|
| ROBOWORLD Robosuit for UR5/UR5e (custom-made) | 1000-denier nylon: radiant ≤1250 °F. **10-mil laminated Teflon: ≤650 °F, FDA-approved.** Isotherm weld-spatter cloth: ≤500 °F sustained, 700 °F short | [O, snip, [Qviro](https://qviro.com/product/roboworld/universal-robots-ur5-ur5e-robosuit)] |
| "Chunyu Protection" high-temperature suit (UR marketplace) | Aluminium-laminated composite, "200–800 °C". UR3 to UR20. GB/T 5455 B1 flame-retardant. Sold in CN/HK/MO/TW only | [O, [UR marketplace](https://www.universal-robots.com/de/marketplace/products/01tP40000071NGvIAM/)] |
| ROBO-GEAR, FAuDE Tec ProSuit (food-grade versions exist) | Ratings not found | [O, snip, [Qviro](https://qviro.com/product/robo-gear/robo-gear-protective-cover/alternatives)] |
| UR5e itself | IP54. **Ambient 0–50 °C.** 5 kg payload, 850 mm reach, 20.6 kg | [M, [UR5e datasheet](https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/)] |

**Inferred.** A cover blocks oil splash. It does not change the 50 °C rating, and it may trap joint heat. Keep the arm out of the hot plume instead.

### 5.4 Plume above the wok

- **Measured data: not found** for a wok at a given height with a hood running.
- One real study exists: Yu, Narasaki, Satoh and Yamanaka (Osaka). They measured velocity, temperature and CO₂ at 147 points on 7 sections, 40–80 cm above a gas stove. The burners were 3.1–8.9 MJ/h (0.85–2.5 kW), with 16–28 cm pots. Profiles are Gaussian. Smaller pots and stronger burners give hotter plumes.
  - The scanned values were unreadable. [M, [AIVC airbase 4499](https://www.aivc.org/sites/default/files/airbase_4499.pdf)]
- **Estimate (inferred)** using Heskestad's plume relations [O, [Heskestad, "Engineering Relations for Fire Plumes"](https://firedoc.nist.gov/article/1HcxXYQBWEcjUZEYvA5h)]:
  - ΔT₀ = 25·Qc^(2/3)·(z−z₀)^(−5/3) (kW, m);
  - z₀ = 0.083·Q^(2/5) − 1.02·D;
  - D = 0.36 m wok, room 30 °C;
  - **no hood draught or cross-draught modelled.**

| Heat source (convective Qc, assumed) | 30 cm above rim | 50 cm | 70 cm | Plume half-width at 50 cm |
|---|---|---|---|---|
| Gas 5 kW (Qc ≈3 kW) | ≈+146 K → **≈175 °C** | ≈+86 K → 115 °C | ≈+58 K → 90 °C | ≈10 cm |
| Induction 3.5 kW (Qc ≈1 kW) | ≈+61 K → **≈90 °C** | ≈+37 K → 67 °C | ≈+26 K → 56 °C | ≈9 cm |

- About 20 cm off the plume axis, the excess falls to ≈2% of the axis value (Gaussian, r = 2b).
- So the wrist should **approach from the side and stay ≥20–25 cm off the wok axis** (inferred).
- Steam bursts when wet food hits hot oil are not covered by this estimate.

---

## 6. Wok and tools for a robot

| Item | Facts | Src |
|---|---|---|
| Gripper | DH PGC-140-50: 1 kg. 40–140 N per jaw. 50 mm stroke. **Recommended load ≤3 kg** | [O, snip, [welectron](https://www.welectron.com/DH-Robotics-PGC-140-50-Collaborative-Electric-Parallel-Gripper)] |
| Wok spatulas (锅铲 / wok chuan) | GSW TN-S: 16¾" (42.5 cm), 0.45 lb (204 g). Town 33976: 16½", 4"×3½" blade, 13" handle, ≈0.4 lb (181 g) | [O, snip, [Chefs' Toys](https://chefstoys.com/products/gsw-tn-s-stainless-steel-wok-chuan-spatula-turner-16-3-4-1300)]; [O, snip, [Webstaurant](https://Webstaurant.com/town-4-x-3-12-stainless-steel-wok-spatula-with-13-handle-33976/88533976.html)] |
| Two-loop-handle (Cantonese) woks | 14" flat, induction-ready: Town 1.59 kg; Emperor's Select 1 mm | §4.1 |
| Round wok on a flat zone | Gaggenau VI 414 + wok ring + WP 400 001 (Ø36 cm, 6 L) | [M, [Gaggenau](https://www.gaggenau.com/gb/en/mkt-product/VI414111)] |
| Fixed concave induction | Holds a round wok by geometry. Ko & Hu's chefs also use the stove rim as a pivot | §1.1; [O, [Hu lab](https://hu2.me.gatech.edu/Ko/wp-json/wp/v2/pages/19)] |
| Tilting / flipping holders | Motorised wok-flip patent (linear actuators). Tilting rotary-tank stir-fryer patents. Chefmax manual tilt, 13–20 angle steps | [O, snip, [US7930973](https://patents.google.com/patent/US7930973)]; [O, snip, [US 2017/0354287](https://patents.justia.com/patent/20170354287)]; [O, snip, [Chefmax](https://china.org.ru/product/1600173111549)] |
| Kitchen-robot tool changers | A robotic-kitchen-assistant patent with a tool changer holding spatulas, scoops and other utensils. Cobot changers: RSP CoboShift, GRIP Auto Connector. Wok-specific interfaces: **not found** | [O, snip, [US patent 12462547](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12462547)]; [O, snip, [Bibus](https://www.bibus.nl/en/blog/post/coboshift-tool-changers-for-cobots-rsp)]; [O, snip, [A3](https://www.automate.org/products/grip-usa-llc/auto-connector)] |
| UR5e payload vs centre-of-gravity offset | The curve exists (0–600 mm offset). Values were not readable. Example from the UR forum: 2 kg gripper at 50 mm + 3 kg object at 150 mm → 5 kg with CoG at 110 mm. PolyScope warns outside the curve | [O, [UR forum](https://forum.universal-robots.com/t/how-calculate-the-max-cog-center-of-gravity-offset/16158)] |

**Load budget (inferred)**
- Wok 1.5–2.2 kg + food 0.5–1.0 kg + gripper 1.0 kg = **3.0–4.2 kg** of the UR5e's 5 kg.
- The wok's centre of gravity sits ≈0.2–0.25 m from a handle grip. Static moment on the fingers: ≈2.5 kg × 9.81 × 0.22 ≈ **5.4 N·m**, rising to ≈15 N·m when tossing.
- A friction grip of 2 × 140 N, μ ≈ 0.5, over ≈30 mm pads resists only about **2 N·m**. The wok would rotate in the fingers.
- **A form-fit wok coupling is needed**: a pin and socket, or a tool-changer plate on the handle. Plain parallel-jaw friction is not enough.

---

## 7. Gaps

- **Ko & Hu amplitudes and accelerations.** The full text was blocked. The figshare data are the next step.
- **Measured wok-plume temperatures** at given heights with a hood running.
- **Spatula forces** in stir-fry. The Sci Data grilling dataset has them, but the full text was blocked.
- **Concave-coil efficiency** with a round wok.
- **Built-in temperature cut-offs** of Chinese concave units.
- **Any app or serial protocol** for a concave cooker.
- **Singapore prices** for Miele CS 1223-1 I and Gaggenau VI 414.
- **Specs** for 美的 炒菜机 and Posha (max °C), and a Midea app (美的美居) MIoT-like spec.
- **Gas-knob torque** (EN 1106 is paywalled).
- **Chinese 菜籽油 smoke point.**
- **UR5e payload-curve values.**

---

## Implications for the robot

Three options are compared:
- **(A)** arm plus spatula in a fixed wok on a concave induction hob;
- **(B)** a motorised rotating or tilting wok, or a home auto-cook machine, with the arm only adding ingredients;
- **(C)** keep the gas hob.

- **Heat delivered: A ≥ C.** A 3.5 kW concave induction unit delivers ≈1.7–3.0 kW into the pan. The home gas wok burner delivers ≈0.9–1.6 kW (32% water, 23% sauté; 3.8 kW on town gas, 5.0 kW on LPG). Even a 3 kW unit on a 13 A plug matches gas. A 3.5 kW unit draws 15.2 A, so it needs a 20 A circuit. **Inferred from** [Frontier](https://www.caetrm.com/media/reference-documents/Induction-Range-Final-Report-July-2019.pdf) and [Fujioh](https://www.fujioh.com/sg/wp-content/uploads/2023/02/Manual_GS25_20221101.pdf). **B home machines** are 1–2 kW and capped at 120–230 °C.
- **Peak wok temperature: C > A > B.** Gas can push the wok bottom past 399 °C, which is real 爆炒 and 润锅 heat, but only tens of °C below oil auto-ignition (406–435 °C). Commercial wok-induction temperature modes top out at 218–238 °C (CookTek 425 °F, Avantco 460 °F). Power mode can go hotter, but typical dry-burn cut-offs sit near 280 °C. B machines stop at ≤230 °C. Reviews say B gives **no 锅气** and stews with the lid closed (九阳 J7).
- **Controllability: A ≈ B (both poor) > C.** No concave unit documents an API. The robot must press the panel, or a qualified person must intercept the UART (TILLREDA-style, 9600 baud, 10-byte frames).
  - The only writable heat command found is MIoT `加热档位` 0–99 on the **flat** 米家电磁炉2.
  - Home Connect cooktops are read-only.
  - Gas needs push-and-turn plus a 5 s hold for every ignition. Any valve or actuator inside the hob is LGSW work.
- **The wok coupling decides A.** A UR5e plus PGC can carry 3.0–4.2 kg (wok + food + gripper) of its 5 kg. But a friction grip resists only ≈2 N·m against a ≈5 N·m static moment. So A needs a fixed wok on the concave hob (spatula only), or a form-fit handle coupling. Both are inferred.
- **Tossing (颠锅) is out of reach for one UR5e (inferred).** Chefs toss at 0.3 s period (≈3 Hz), and power rises with f³. At 3 Hz and an assumed ±5 cm, a 3 kg load needs ≈18 m/s² and ≈0.9 m/s. The only robot stir-fry study used a 0.5 kg wok on two Pandas. A, B and C can all do 翻炒 strokes. If tossing matters, only a **dedicated motorised pivot or tilt mechanism** (B-type hardware, using the hob rim as a fulcrum like chefs do) can approach it.
- **B frees the arm but loses technique.** Drums tumble at ≈0.5 Hz and tilt to plate, which solves plating. But closed lids and low temperatures rule out 润锅 → pour oil out, 滑油, rim pours and 离火 additions. Home machines also have no API. **A motorised tilt or pivot holder for the fixed wok under A** keeps the technique and adds plating and pour-out. This is a design suggestion (inferred).
- **Plume exposure: A is better than C.** Estimated plume-axis temperature 30 cm above the wok: gas ≈175 °C, induction ≈90 °C. Both exceed the UR5e's 50 °C rating, so the wrist must approach from the side, ≥20–25 cm off the wok axis, under either option (inferred). Teflon-laminated covers (≤650 °F) handle splash, not plume heat.
- **Temperature sensing is needed under A and C.** Hob sensors are coarse (Miele 160/200/220 °C) or read-only. Use an IR sensor on a well-seasoned wok (ε ≈0.8–0.9) or on the food, and check it against a contact thermocouple. Never read bare shiny steel (ε ≈0.1).
- **Fire safety: A is simpler than C.** Under A, an Innohome-type guard can cut **electric** power on heat rate of rise. Under C, the options are a FireAvert or iGuardStove **gas solenoid** (LGSW work in Singapore) or City Energy's Küche hob (280 °C cut-off, app shut-off), which is not sold at retail yet. Under either, add a StoveTop FireStop canister 69–89 cm above the burner. Unattended cooking caused 30% of Singapore home fires in 2025.
- **Cost and availability.**
  - (A) Concave units cost ¥320–689 in China and US$230 for Avantco in the US. No mainstream Singapore concave unit was found, so expect an import plus a 20 A point.
  - (B) Home machines cost ¥1,999–4,890 or US$800–1,750, and drum machines are commercial 220 V units.
  - (C) Gas is already installed.
- **Overall (inferred).** A is the only option that keeps Wang Gang's open-wok techniques and also gives an electrically interlockable, cooler and cleaner heat source. Its open risks are the control path (panel pressing vs UART), the wok coupling, and cut-offs near 280 °C during 润锅.
