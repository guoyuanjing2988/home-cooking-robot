# R19: Commandable small cooking appliances that could simplify the robot (market scan)

Date: 2026-10-14. User request: "尽量去市场上再探索探索可以自动化的各种家用小电器，可以远程操控或者至少是按钮类型，大幅简化".
Desk study only: WebSearch/WebFetch, read-only. No logins, carts, purchases, forms or seller contact. No other repo file changed.

**Tags**
- **[S]** sourced: URL, or repo `file:line`. "(snip)" = seen only in a search-result summary, weaker.
- **[E]** my estimate or judgement.
- **ND** = looked for, not found.
- Currents are [E] = rated W / 230 V.
- Prices are CNY launch, crowdfunding or deal prices from news/deal sites. None is a live Tmall/JD price, so all are **unconfirmed**.

**Not repeated here** (already in the repo):
- auto stir-fry machines (pot, drum, commercial): `research/r19_autostir_market.md`;
- concave induction, MIoT flat induction (米家电磁炉2), hob sensors, Home Connect: `research/r15_cooking_market.md` §1;
- stew pot, rice cooker, fryer prices: `research/r19_system_cost.md:69-73`.

This file adds:
- steamers and steam ovens;
- pressure cookers;
- air fryers;
- hot-water dispensers;
- Thermomix-class machines;
- button-pusher retrofits;
- which of these the robot PC can command **locally**.

---

## 0. Answer first

The meals are 5 steamed dishes, 3 soups, 7 wok dishes and 1 deep-fry out of 15 [S `research/homestyle_meals.md:27-33`]. Three cheap Xiaomi-ecosystem (MIoT) appliances can take over most of the non-wok work. Their documented commands are start, cancel, mode, temperature, time and status/"done".

| Rank | Pick | Takes over | What it removes from the robot | Interface |
|---|---|---|---|---|
| 1 | **Steaming appliance with MIoT.** Either the **米家智能电蒸锅 12L** (1,500 W, 2 tiers, 29 cm rack, ¥269–299), or a countertop **steam oven**: 米家智能蒸烤箱 S1 30L (¥1,599) or the 20L `chunmi.oven.x14` | All **5 steamed dishes**, plus the steamed soup cups (蛤蜊排骨盅) | 1. The zone-2 pot, rack, water fill and pot lid under the hood. That geometry is so tight that a steamer tier was already rejected [S `DECISIONS.md:362`]. 2. Watching the time and turning the heat off. 3. With the oven, the plate goes in **sideways through a front door at counter height**, not down into a pot under the hood | MIoT: set mode, time and temperature; start/cancel; status and a "cooking finished" event. The oven also reports door state and water tank [S, §2.1] |
| 2 | **Electric pressure cooker with MIoT** (米家智能电压力锅 2 Pro 5L, 2,200 W IH; older 5L ¥299) | The **soups** (1 h clay-pot soup) and **红烧肉** (40 min braise), with an open-lid mode for 收汁 | The long stew pot or clay pot on a heat zone, its lid handling, and the heat-zone time. The arm only drops food and liquid in, closes the lid, starts it, and later serves from it or pours | MIoT: `start-cook(cook-mode)` incl. soup and open-lid modes; target time; pressure stage, lid and status readout [S, §2.2] |
| 3 | **Air fryer with MIoT** (米家智能空气炸锅 6.5L 嫩烤版, 1,800 W, ¥449, **LAN-controllable**) | The single deep-fry (干锅土豆 potato slices) | The whole fryer: 1+ L of hot oil, oil filtering, the spider at the fryer [S `DECISIONS.md:245`]. Taste trade-off | MIoT: temperature 40–230 °C, time, start, status [S, §2.3] |
| 4 | **Button pushers**: SwitchBot Bot (mechanical) and Tuya **Fingerbot Touch** (capacitive, 2 fingers) | Pressing panels on any button-only appliance: concave induction, drum stir-fryer, rice cooker | Arm trips to press keys, and reaches under the hood to the cooker panel | Local BLE via Home Assistant [S, §2.5] |
| 5 | **Drum stir-fryer** (6 L, IH) | The 7 wok dishes' stirring | The spatula and the wok lift and carry. Already analysed: **no API**, hand tilt [S `research/r19_autostir_market.md:152-172`] | Buttons, so pair it with rank 4 |

**Net effect [E]:**
- The robot's own heat handling shrinks to the wok (or drum) dishes.
- Every slow item becomes "load, close, command, wait for the done event, unload".
- The second induction zone and its pot could be dropped if blanching moves to the wok. That is a decision for the orchestrator (§4).

**Things the market does NOT offer [S/ND]:**
- No concave/wok induction cooker with an app, IR or serial interface. Same as r15; re-searched, still ND.
- No home stir-fryer with a LAN API. The one MIoT stir-fryer, 九阳/Solista SD-CJ01, is ND in stores and not on the LAN list.
- No Matter-certified cooktop products (§2.6).
- Midea's local LAN integration exposes Midea rice cookers, pressure cookers and steam ovens **read-only** (§2.6).

---

## 1. Comparison table

| Appliance | Model / MIoT id | Price CNY | Power → A @230 V | Capacity vs 4-person meal | Robot-PC control | Local (LAN) control in hass-xiaomi-miot? | Robot loading | Main limits |
|---|---|---|---|---|---|---|---|---|
| Electric steamer | 米家智能电蒸锅 12L, `xiaomi.esteamer.mes01` | 299 list / 269 crowdfunding (2023) [S kocpc] | 1,500 W → 6.5 A [S/E] | 12 L, 2 tiers, 29 cm rack ("fits a fish plate") [S kocpc; (snip) for the fish plate]. One fish plate + one other plate per tier [E] | mode (steam/stew/…), temperature 40–100 °C, time 0–840, start/pause/cancel, status incl. "add water", low-water event [S spec] | **No** (not on the LAN list), so cloud [S] | Lift the lid, lower the plate onto the tier, close the lid. Top loading; height under the hood unknown | 2 L water tank, refilled from the side without opening [S kocpc]. Plate lift from a tier = the geometry that was rejected at the hob; must be placed **outside the hood zone** [E] |
| Countertop steam oven | 米家智能蒸烤箱 S1 30L, `xiaomi.oven.cm30l` | 1,599 [S mundoxiaomi 2024-11] | Steam 1,600 W; hot air "1,800 W fan". Total rated input **ND**. If both ran at once: ≤3.4 kW → 14.8 A [E] | 30 L, "2–6 people" [S]. Two levels: cups + taro together [E] | cook-mode (nutrition steam / high-temp steam / bake / air-fry / stew), target temperature 30–230, cook-time, `start-cook`, cancel, pause, resume; status, door state, water tank, faults; events incl. cooking finished and low water [S spec] | **No** → cloud | Open the drop-down door, slide the plate or tray in, close the door. Counter height, no hood | Interior size ND. Descaling. Water tank refill (user). Rated current must be checked |
| Countertop steam oven, older/smaller | 米家智能蒸烤箱 20L, `chunmi.oven.x14` | ND | ND | 20 L | mode (pure / high-temp / low-temp steam, …), target temperature 0–300, cook-time, preheat; door, water level 0–100. **Note:** `start-cook` takes only a recipe-name and recipe-command string [S spec] | **Yes** [S LAN list] | As above | Sale status ND. The start-action format is the open point |
| Earlier 30 L steam oven (2020) | 米家智能蒸烤箱 30L | 1,299 crowdfunding / 1,499 retail (2020) [S IT之家] | ND | 30 L | Mi Home app remote control [S]. Which spec id: ND | ND | As above | Probably superseded by the S1 [E] |
| Electric pressure cooker | 米家智能电压力锅 2 Pro 5L. MIoT id ND (§2.2 shows `xiaomi.pre_cooker.eh3`) | 2 Pro: ND. Older MYL02M 5L ¥299 (2021) [S snip smzdm] | 2,200 W IH → 9.6 A [S pconline] | 5 L. 红烧肉 0.5–1 kg or a 4-person soup fits [E] | (eh3 spec) `start-cook(cook-mode)`: soup, beef/mutton, open-lid cooking, keep warm…; target time 0–1440; pressure stage, lid status, `remote-controllable` flag [S spec] | **No** for eh3; `chunmi.pre_cooker.dylg5`/`mini1` **yes** [S] | Open the lid (release mechanism ND), pour food and liquid in, close. Serve: pour from the inner pot, or the user ladles | Auto pressure release before opening [S pconline]. Lid opening force and lock ND |
| Air fryer | 米家智能空气炸锅 6.5L 嫩烤版, `careli.fryer.maf09a` | 449 crowdfunding (2023) [S IT之家 via search] | 1,800 W → 7.8 A [S] | 6.5 L. Potato slices for 4 may need 2 layers or batches [E] | MIoT (maf16 spec read; maf09a assumed similar [E]): target temperature 40–230, time, mode, start/pause/cancel, status, "turn the basket" reminder [S spec maf16] | **Yes** (maf09a) [S] | Pull the drawer by its handle, tip the cup in, push it shut. Unload: pull the drawer, tip the basket onto the plate | Not 六成-oil deep-fried; texture differs [E]. Drawer pull force ND |
| Steam air fryer | 米家智能空气炸锅 Pro 蒸烤版 6.5L, `xiaomi.fryer.st701` | 559 crowdfunding / 749 list (2026-03) [S IT之家] | Steam generator 900 W; total ND | 6.5 L | Mi Home app [S]. Spec not read | **No** | Drawer | Could steam small items too. Unclear whether it can steam a fish plate [E] |
| Hot-water dispenser | 米家智能电热水瓶 5L, `xiaomi.kettle.mek01` | 269–299 (2023) [S koc] | 1,600 W → 7.0 A [S] | 5 L | target temperature 1–100, keep-warm 40–95, `out-water-time` 0–60 **writable** (unit ND) [S spec] | **Yes** [S] | Put the jug or pot under the spout. **No** kettle carry | Whether `out-water-time` really dispenses on command: ND. Flow rate ND |
| Thermomix-class | 米家烹饪机器人 `chunmi.mfcp.c3` (¥5,999 [r19]); Bosch Cookit `bshcn.mfcp.555cwc` (1,750 W, 37–200 °C, 3 L [S snip]) | 5,999; Cookit ≈ €1,266 (DE) [S snip] | 1.75 kW → 7.6 A | 2.2–3 L, small for 4 [E] | Spec has **no temperature, speed or time writes**. Only start, pause, cancel and `start-recipe-cook(recipe-command string)` [S specs] | **No** | Lift the jug to pour [r19] | Not a stir-fry substitute (≤200 °C, closed). Low value here |
| Flat induction (zone 2) | 米家电磁炉2 `chunmi.ihcooker.v2` (already chosen) | 269 (CNPP list, date ND) [S snip] | 2,100 W → 9.1 A [S r15] | — | heat level 0–99 R/W [S r15] | **Yes** [S LAN list] | — | Becomes optional if picks 1–2 are adopted [E] |
| Button pusher, mechanical | SwitchBot Bot | ND (CNY) | battery | — | press / on / off | **Yes**: the official HA integration is local BLE, no cloud [S HA] | Stuck next to the key | ≈5–8 N press force (sources disagree) [S snip]. Cannot press capacitive keys [E] |
| Button pusher, capacitive | Tuya Fingerbot Touch | ≈US$15 (AliExpress) [S smarthomescene] | 500 mAh battery | — | 2 independent conductive "fingers", tap duration settable | **Yes**: Tuya BLE custom integration, key fetched from the cloud once [S] | Stuck on the panel | Cannot press mechanical keys (the Fingerbot Plus does that; its local control is anecdotally flaky) [S] |

---

## 2. Per-product notes

### 2.1 Steaming: electric steamer vs steam oven

**米家智能电蒸锅 12L** [S https://www.kocpc.com.tw/?p=513666 (2023-10-02); spec https://home.miot-spec.com/spec/xiaomi.esteamer.mes01]
- Specs: 1,500 W; 12 L; two tiers; 29 cm extended rack; 2 L tank refillable from the side without opening; NTC; 24 h delay; 8 h keep-warm; Mi Home app. ¥299 list, ¥269 crowdfunding.
- MIoT:
  - `mode` R/W: 0 custom, 1 steam, 2 stew, 3 yogurt, 4 warm;
  - `target-temperature` 40–100 step 5;
  - `target-time` 0–840;
  - actions `start-cook`, `pause`, `cancel-cooking`, `resume-cook`, `start-recipe-cook(temp, time, …)`;
  - `status` includes 5 "cooking complete" and 9 "add-water reminder";
  - events cooking-finished and low-water-level;
  - **no lid sensor**.
- Size: one search summary gave ≈400×240×370 mm, 3.7 kg [S snip, source not pinned]. Treat as ND.
- Fit [E]:
  - 蒸鲈鱼 (6 min after boil), 蒜蓉丝瓜 (3 min), 芋头蒸排骨 and 桂花芋头 (30 min) map directly to one mode, time and temperature command each;
  - "stew" mode at ≤100 °C can do the 炖盅 cups (30 min).
  - Two tiers allow the cook's own "一锅出两菜" trick [S `research/homestyle_meals.md:21`].

**米家智能蒸烤箱 S1 30L** [S https://www.mundoxiaomi.com/domotica/nuevo-xiaomi-me-va-a-ahorrar-tres-aparatos-cocina-necesito-sus-30-litros-capacidad-mi-casa-para-ayer (2024-11-15); spec https://home.miot-spec.com/spec/xiaomi.oven.cm30l; Red Dot https://www.red-dot.org/zh/project/mijia-smart-steam-oven-s1-30l-79143]
- Specs:
  - 30 L, "2–6 people";
  - 1,600 W dual steam injection, steam in 30 s;
  - "1,800 W fan" hot air;
  - 40–230 °C;
  - steam, bake, air-fry, slow-cook, self-clean modes;
  - Mi Home app with multi-stage recipes;
  - ¥1,599.
- MIoT:
  - `cook-mode` R/W (0 nutrition steam, 1 high-temp steam, 2 hot-air, 3 humid bake, 4 top-heat, 5 air-fry, 6 stew);
  - `target-temperature` 30–230; `cook-time` 0–1440;
  - `start-cook(cook-mode)`, cancel, pause, resume, `start-recipe-cook`;
  - `door-state` 1 open / 2 closed; `water-box-status`; `fault` 4 = low water;
  - status 14 "cooking done";
  - events incl. cooking-finished.
- **Why it can beat the steamer for a robot [E]:**
  - it loads from the front at counter height, away from the hood;
  - the door state lets the robot PC verify "door closed" before it starts;
  - the higher-temperature modes could also take the air-fry job, so one appliance covers ranks 1 and 3, though not both at the same time.
- Unknown: interior width and depth (the fish plate), external size, total rated current, door-opening force.
- Older/smaller models:
  - 2020 30 L, ¥1,299–1,499 [S https://www.ithome.com/0/509/963.htm];
  - 20 L `chunmi.oven.x14`, LAN-local, but its start action takes an opaque recipe-command string [S https://home.miot-spec.com/spec/chunmi.oven.x14].
- Built-in Bosch/Siemens steam ovens are also on MIoT (dozens of `bshcn.oven.*` ids [S https://home.miot-spec.com/s/oven]). Built-ins need cabinet work, so they are not pursued.

### 2.2 Electric pressure cooker (soups, 红烧肉)

- **米家智能电压力锅 2 Pro 5L** [S https://best.pconline.com.cn/yuanchuang/31114509.html]:
  - 2,200 W IH; 5 L; stainless and ceramic inner pots;
  - open-lid cooking; double automatic pressure release;
  - Mi Home app can start and stop it and adjust stew and warm time.
  - Price for the 2 Pro: ND. A ¥899 figure in the same article is another model.
- **MIoT spec read: `xiaomi.pre_cooker.eh3`** [S https://home.miot-spec.com/spec/xiaomi.pre_cooker.eh3]. Which retail model eh3 is: ND.
  - `cook-mode` R/W: 0 rice, 1 porridge, 2 beef/mutton, 3 chicken/duck, 4 warm, 5 **soup**, 6 low-temp, 7 beans/tendon, 8 **open-lid cooking**;
  - `target-time`;
  - `press-status` (0 none → 3 holding);
  - `pan-status` (lid normal/abnormal);
  - **`remote-controllable` (read-only bool)**. This suggests a panel-side "allow remote" step may be needed [E]; see §5.
- Fit [E]:
  - 鲜笋排骨汤 (60 min clay pot) → soup mode, about 30–40 min total including pressure build and release;
  - 红烧肉: the robot does the 糖色 and sear in the wok, or skips the sear; then pressure-braise; then open-lid mode to reduce (收汁);
  - meal B needs both at once, so a 2nd unit, or the steamer's stew mode for the soup.
- **Taste:** pressure-cooked 红烧肉 and soups are a mainstream home method. Taste risk is low compared with stir-fry [E].

### 2.3 Air fryer (the one deep-fry)

- **6.5L 嫩烤版 `careli.fryer.maf09a`**: 1,800 W far-IR; 40–230 °C; 7-inch window; app, knob or voice; ¥449 crowdfunding, 2023-09-27 [S search summary of https://www.ithome.com/0/720/708.htm and /722/044.htm]. On the **LAN list** [S].
- **MIoT spec read on the sibling `xiaomi.fryer.maf16` (P1 6.5L)** [S https://home.miot-spec.com/spec/xiaomi.fryer.maf16]:
  - `target-temperature` 40–230 step 5; `target-time` 1–1440;
  - `start-recipe-cook(time, temp, …)`; status incl. "basket paused" and "turn the pot";
  - P1 ≈ ¥297, 2,000 W [S snip smzdm, 2026-08-01].
- Fit [E]: 干锅土豆 potato slices (deep-fried 3 min at 六成) become about 12–18 min of oiled air-frying, then a toss in the wok.
  - Removes: the fryer, 1+ L oil, the hot-oil spider transfer, and oil filtering and storage.
  - Texture is drier.

### 2.4 Hot water without carrying a kettle

- **米家智能电热水瓶 5L `xiaomi.kettle.mek01`**: 1,600 W; 5 L; boil, then hold at 40–90 °C; app; ¥269–299 [S https://www.koc.com.tw/archives/511157].
- Spec [S https://home.miot-spec.com/spec/xiaomi.kettle.mek01]:
  - `target-temperature` 1–100 R/W; keep-warm settings;
  - `out-water-time` 0–60 **R/W** (unit and meaning ND). There is no explicit dispense action.
- On the LAN list [S]. If `out-water-time` really triggers the spout, the arm only holds the pot or jug under it. That removes the 2.5 kg kettle grasp and pour that is not yet checked [S `DECISIONS.md:390`].
- The user's existing 小米饮水机: model unknown. Xiaomi's filtered dispenser Pro sets 80–1,000 ml per dispense, but at only 0.25 L/min [S https://www.mi.com/uk/support/faq/details/KA-169069 (snip)].

### 2.5 Button pushers (make "button-only" appliances commandable)

- **SwitchBot Bot** (WoHand):
  - the official Home Assistant integration controls it locally over Bluetooth, no cloud [S https://www.home-assistant.io/integrations/switchbot/];
  - press force ≈5–8 N (sources disagree) [S snip];
  - Matter only through a SwitchBot hub, and Matter has no momentary-button type, so state can drift [S snip https://www.matteralpha.com/review/switchbot-bot-rechargeable-review].
- **Tuya Fingerbot Touch** [S https://smarthomescene.com/guides/tuya-fingerbot-touch-local-integration-in-home-assistant-over-bluetooth/]:
  - two conductive arms that tap **capacitive** panels; 38×38×28 mm; adhesive; USB-C;
  - local BLE through the `ha_tuya_ble` integration (the key is fetched from the cloud once);
  - ≈US$15; BLE range 3–4 m or an ESP32 proxy.
- Use [E]:
  - concave induction touch panels (no app exists [S r15]);
  - drum stir-fryer panels;
  - a rice cooker's start key.
  - Limits: a pusher cannot turn a rotary knob (the existing servo plan covers that [S `DECISIONS.md:292`]), and it cannot read the display. The robot PC confirms state by camera or by a power-metering plug [E].
- Heat at the panel: unrated for the hob zone; mount away from the plume [E].

### 2.6 Ecosystem checks

- **Xiaomi MIoT local control.** The Home Assistant integration hass-xiaomi-miot runs devices locally if they are on its LAN list, otherwise through the Mi cloud. Actions are sent as `call_action(siid, aiid, params)` [S https://github.com/al-one/hass-xiaomi-miot].
  - LAN list checked [S https://raw.githubusercontent.com/al-one/hass-xiaomi-miot/master/custom_components/xiaomi_miot/core/miot_local_devices.py]:
    - **on it**: `chunmi.ihcooker.v2`, `chunmi.oven.x14`, `careli.fryer.maf09a`, `xiaomi.kettle.mek01`, `chunmi.cooker.eh3` (a rice cooker id);
    - **not on it**: `xiaomi.oven.cm30l`, `xiaomi.esteamer.mes01`, `xiaomi.fryer.maf16`/`st701`, `xiaomi.pre_cooker.eh3`, `chunmi.mfcp.c3`, `jyaiot.cm.jycj01`.
  - Not on the list = cloud path, or LAN untested [E].
- **Midea M-Smart LAN** (midea_ac_lan) [S https://github.com/georgezhao2010/midea_ac_lan]:
  - covers rice cooker EA, pressure cooker EC, slow cooker E8 and steam-microwave BF;
  - the EA and BF docs list **sensors only, no services** [S …/doc/EA.md, …/doc/BF.md];
  - so Midea appliances give "done" detection, not start.
- **Matter**: no products listed for the Cooktop device type [S https://www.matteralpha.com/category/cooktop].
- **Tuya cooking appliances with local control**: not searched in depth. ND.

---

## 3. How the robot's flow changes (per meal) [E]

Meals are from `research/homestyle_meals.md:6-8`. The current plan (r16–r19) is: concave induction wok + zone-2 MIoT flat induction with a pot and rack + stew pot + user rice + fryer.

| Meal | Today | With picks 1–3 |
|---|---|---|
| A 干锅土豆 / 桂花糖芋头 / 炒西兰花 / 蒜蓉蒸丝瓜 / 蛤蜊排骨盅 | Fryer for the potatoes. Zone-2 pot for the steaming, with the lid and plate carrier under the hood | Potatoes go to the **air fryer**, then a wok toss. Taro and the soup cups go into the **steamer/oven** together (30 min). Luffa is added for 3 min at the end. Only 2 wok dishes stay with the arm |
| B 红烧肉 / 番茄炒蛋 / 白灼秋葵娃娃菜 / 清蒸鲈鱼 / 鲜笋排骨汤 | Soup on zone 2 or the stew pot (1 h). 红烧肉 40 min in the wok, which blocks the wok | Soup goes to the **pressure cooker**. 红烧肉 to a 2nd pressure cooker, or wok sear then cooker. Fish goes to the steamer for 6 min. 白灼 blanching stays in the wok (or zone 2). The wok is free for 番茄炒蛋 |
| C 芋头蒸排骨 / 酸辣土豆丝 / 青椒炒鱿鱼 / 清炒荷兰豆 / 青瓜肉片汤 | Zone-2 steamer; quick soup in the stew pot [S `DECISIONS.md:423`] | Ribs go to the steamer. The quick soup goes to the pressure cooker in open-lid mode, or to the steamer's stew mode. Three wok dishes |

**Arm actions that disappear or shrink:**
- the steamer lid and plate carrier under the hood: 2.4 min per 3 meals for the carrier, 5.1 min for lids [S `research/r19_system_cost.md:125,128`];
- the spider at the fryer;
- the kettle carry, if §2.4 works;
- the heat-zone timing.

**New arm actions:**
- an oven door, steamer lid or cooker lid, opened at counter height;
- an air-fryer drawer pull;
- a pot pour from the pressure cooker;
- refilling the steamer tank (or the user does it).

**Controller:** one Home Assistant + hass-xiaomi-miot bridge (or a direct MIoT client) on the cart PC. The meal scheduler sends:
`set mode / time / temperature → start → wait for the cooking-finished event or status = done → unload`.

**Supervision rule** [S `DECISIONS.md:670`]:
- "No remote start of heat" means no starting from outside the home. The cart PC starting appliances in the supervised kitchen is the same as the robot starting the wok [E].
- Prefer the LAN path; the cloud is a dependency.

**Power** [E]:
- steamer 6.5 A + pressure cooker 9.6 A + air fryer 7.8 A, against today's zone 2 (9.1 A) + stew pot + fryer (≈10 A [S `research/r19_power_budget.md`]).
- About the same peak, but `r19power.py` must be re-run with the new loads. The S1 oven's total rated current is unknown and could be the largest.

**Counter space**: 3–4 extra boxes. Each is about 0.3–0.4 m wide (dimensions mostly ND). Whether the user's L-kitchen has the counter length is the binding question.

---

## 4. Open questions / what to verify

1. **Remote start gate.** Does each Mijia heating appliance accept `start-cook` from the network without someone first pressing a panel key? The `remote-controllable` flag on the pressure cooker hints at a gate. If there is one, a SwitchBot or Fingerbot press is the workaround.
2. **Cloud region.** These are China-market devices on the Mi **China** cloud server. Do they bind and run from Singapore? Does the LAN path (token) work for the cloud-only ids (S1 oven, steamer, pressure cooker)? A bench test is needed.
3. **The kettle's `out-water-time` semantics**: does writing it dispense?
4. **Steam oven S1 30L**: rated input current, interior width and depth (fish plate), door force, external size. Is the 20 L `x14` still sold?
5. **Pressure cooker 2 Pro**: its MIoT id, price, lid-release method, and the force for the arm.
6. **Air fryer drawer** pull force, and the potato texture versus 六成 oil. The cook (user) should taste-judge.
7. **Plug and voltage**: CN appliances are 220 V with GB plugs; Singapore is 230 V BS 1363. The adapter or rewiring has to be decided. This is under the LEW/MCST items in `research/r19_sg_compliance.md`.
8. **Tank refills and descaling**: is the user OK refilling the steamer and oven tanks each meal day? (Same pattern as the water decision, `DECISIONS.md:694`.)
9. **Whether to drop zone 2** once steaming and soups move to appliances. Blanching (白灼, 焯水) would then need the wok or a pressure cooker in open-lid boil mode.
10. **Taste trade-offs** for the user: air-fried 干锅土豆, pressure-cooked 红烧肉 and soups. The steamed dishes are unchanged.

---

**Method note.**
- One Bash `curl` read the public GitHub LAN-list file once. It was then re-checked with WebFetch, which is the cited source.
- Pages that failed: domadoo (403). The 2 Pro price and the S1 dimensions were not found in readable sources.
