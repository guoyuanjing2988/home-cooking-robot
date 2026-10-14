# R19: market scan of automatable household appliances, and how the PC controls them

Date: 2026-10-14. Desk study, read-only. Inputs: project files, plus WebSearch/WebFetch (no logins, carts, purchases, forms or contact). Only this file was created.

**User request:** "尽量去市场上再探索探索可以自动化的各种家用小电器，可以远程操控或者至少是按钮类型，大幅简化". Find appliances the PC can command (app, API, LAN) or at least press, so the robot does less.

**Tags**
- **[S]**: sourced. A URL read on 2026-10-14, or a repo `file:line`. **[S, snip]** = only a search-result summary was seen, not the page.
- **[E]**: my estimate or proposal, with the reasoning given.
- **ND**: searched, not found. Nothing is invented. All prices are unconfirmed list or promo prices seen today.

**Scope and fixed rules from the repo**
- Heat is cut by the hardware contactor chain. Smart plugs and MIoT only set power *inside* an armed session: "A smart plug is not an interlock" [S `research/r19_fire_heatcut.md:40`]. No heater may be started from outside the flat, and heaters are controlled over the local LAN only [S `research/r19_fire_heatcut.md:187-188`]. Nothing below changes that.
- The user has a dishwasher (model unknown) and a 小米饮水机 (model unknown) [S `DECISIONS.md:540-541`; `research/r19_food_hygiene.md:370`].
- The faucet is not replaced, and the user said no water pipe or valve for the robot [S `DECISIONS.md:384-392`]. Earlier, sensor or solenoid faucets were allowed [S `DECISIONS.md:59-61`].
- The docked arm can't reach z 0.45–0.7 m (the under-counter band) [S `DECISIONS.md:251`].

---

## 0. Answer first

### 0.1 Top picks, ranked by work removed

| Rank | Pick | What it removes | Control | Price | Verdict |
|---|---|---|---|---|---|
| 1 | **A countertop dishwasher at counter height that the PC can start**: 米家智能台式洗碗机 6 套 S10 (`xiaomi.dishwasher.ts10`). Or keep the user's dishwasher if it already has an app | The key enabler for #31. The user's 10–15 min per meal of dishwasher loading and unloading moves to the robot [S `research/r19_food_hygiene.md:318`]. The robot can only reach a rack at counter height: the under-counter band is out of reach [S `DECISIONS.md:251`]. It also removes the start-button press | MIoT: `start-wash`, `mode` R/W, `door-state` R, `status`, `left-time` [S miot-spec ts10] | ¥2,299 list, ¥1,439 promo [S ithome 2025-10-15] | **Top pick for #31.** 6 place settings only. It has no auto-dosing in its spec, so detergent goes in per cycle (a robot pod drop [E]). Water supply (tank or hose) is ND |
| 2 | **A dishwasher with auto-dosing, auto door and API**: 米家 嵌入式 18 套 S20 (`xiaomi.dishwasher.16s20`) | Detergent per cycle (auto-dose), the door at cycle end, and the start press. The PC can open and close the door | MIoT: `open-door` / `close-door` actions, `detergent-self-delivery` R/W, `start-wash`, `layered-set` (upper/lower) [S miot-spec 16s20] | ¥4,299 launch, ¥3,439 with subsidy (Apr 2025) [S ithome] | Best spec found. **But it is built in, so its racks sit in the band the arm can't reach** [S `DECISIONS.md:251`]. The user would load it, or it needs raising (cabinet work) [E] |
| 3 | **Xiaomi water dispenser with an MIoT "dispense N mL" command** (`xiaomi.ysj.js15` / `ymmax` class) | The arm takes measured clean or hot water at the dispenser. No kettle filling, no faucet trips for water, no jug refills (water is 4–8 L per meal [S `DECISIONS.md:387-390`]). The user's R3 water task falls to 0–1 min [S `research/r19_user_workload.md:55`] | js15: `start-out-water` action, `out-water-volume` 0–10,000 mL R/W, `target-temperature` R/W [S miot-spec js15]. ymmax: `out-water-volume` R/W, but no dispense action listed [S] | ND | **Check the user's model first.** Two other Mijia 台式净饮机 have **no** dispense command (`tsa2p`, `tsj15`) [S]. Remote dispensing may be blocked by firmware for safety: bench-test it |
| 4 | **Faucet without a lever motion**: the clip-on IR sensor in the aerator (O5, ¥37–119) [S `research/r19_system_cost.md:221`], or a PC-switched valve | Removes 48 lever grasps and 2.4 min per 3 meals [S `research/r19_system_cost.md:221`]. A PC-switched valve also lets an E-stop close the water, which the lever can't (today the arm may leave the tap open [S `research/r19_fire_heatcut.md:106`]) | Sensor: none (the arm waves). Valve: Zigbee or Tuya Wi-Fi valve actuator on the under-sink angle valve [S Aqara, Tuya VC-106] | Sensor ¥37–119; Aqara T1 US$69.95 / €59.99; Tuya VC-106W US$14 [S] | User decision: a valve on the angle valve isn't new plumbing, but the 10-12 "no valve" answer applies [S `DECISIONS.md:384`] |
| 5 | **Button pushers for anything with a mechanical button** (SwitchBot Bot; Tuya Zigbee Fingerbot) | Arm button presses, e.g. hood, rice cooker, any no-API appliance. Each pusher replaces one checked arm path | SwitchBot: BLE, local through Home Assistant with no hub [S HA docs]. Fingerbot: Zigbee, local through Zigbee2MQTT [S Z2M] | SwitchBot S$37.05 (Challenger SG) [S]; Fingerbot €24.99 [S] | Cheap. Force is only 8 N / 1.15 kgf (SwitchBot) or 2.0 kgf (Fingerbot), and **not for touch panels** [S; E] |
| 6 | **Hood with an API** (MIoT hood, Midea B6, SG Wi-Fi hoods), or a SwitchBot on the existing hood | The user switching the hood. The PC can keep it on at E-stop (decision D5 [S `research/r19_fire_heatcut.md:105`]) | MIoT `fan-level` 0 auto / 1 / 2 / 3 爆炒 R/W, `on` R/W [S miot-spec ymv9]; Midea B6: fan speed, power, light over LAN [S midea_ac_lan] | ND for SG hoods with an API | Low saving (a few seconds per meal). Keep the existing hood unless it is replaced anyway |
| 7 | **Smart plugs with energy metering and local API** (Matter Tapo P110M, Shelly) | Nothing for the arm. They give the PC on/off **and current read-back** for the stew pot, fryer and slicer (already planned) [S `research/r19_power_budget.md:231`] | Matter (local) or Shelly RPC over HTTP (local) [S] | Tapo P110M S$15–19.90 [S] | Already in the design. Pick Matter or Shelly over Tuya or cloud-only plugs |
| — | Wok auto-washer | Would remove the user's wok final wash (1–2 min per meal [S `research/r19_food_hygiene.md:309`]) | — | Commercial only: CanCan pot washer US$5,275, wall-mounted, 16 kg [S] | **No home product found.** Not recommended |

**What the market does *not* offer (all ND after search):**
- a knob-turner product for appliance dials (the repo's bolt-on servo stays);
- a home wok or pan auto-washer;
- an induction cooker with an IR remote;
- an API on the Samsung fridge auto-door [S, snip third-party];
- a Midea dishwasher start over the LAN integration (power, child lock and storage only) [S midea_ac_lan E1].

### 0.2 Control architecture (recommendation)

**One "appliance gateway" on the robot PC: Home Assistant, used through its WebSocket API, with local-only integrations.** The robot software sends commands and checks the state that comes back. It never fires and forgets. [E]

| Layer | Protocol / integration | Devices | Why |
|---|---|---|---|
| 1. Safety (unchanged) | Hard-wired contactor chain + safety relay | All heaters | The only thing that can cut heat [S `research/r19_fire_heatcut.md:40`] |
| 2. Main appliance bus | **MIoT over LAN**: `python-miio` (token + IP) or `hass-xiaomi-miot` in "Local" mode | Dishwasher, water dispenser, zone-2 induction, rice cooker, MIoT hood | Most Chinese-market appliances with a public spec are MIoT, and the spec site documents properties and actions per model [S miot-spec] |
| 3. Plugs and relays | **Matter over Wi-Fi** (HA Matter Server) or **Shelly Gen2 RPC** over HTTP | Functional on/off + current read-back | Local by design [S HA Matter; S Shelly RPC] |
| 4. Short-range | **BLE** (HA SwitchBot, no hub; ESP32 BLE proxy if range is short) and **Zigbee** (Zigbee2MQTT coordinator) | Button pushers, leak sensors, valve, smoke sensor | Local [S HA SwitchBot; S Z2M] |
| 5. IR | Broadlink RM4 mini (HA Broadlink, local) | Only appliances with IR remotes (none on the BOM today) | Local after app setup [S HA Broadlink] |
| 6. Cloud-only, non-critical only | Home Connect (Bosch/Siemens), SmartThings, Tuya cloud | Only for after-meal jobs (e.g. dishwasher start) | Rate limits; needs internet; the Home Connect remote start must be enabled on the appliance [S] |

Rules [E]:
- Everything time-critical in a meal is LAN or BLE/Zigbee.
- The robot VLAN keeps no internet egress, as already proposed [S `research/r19_fire_heatcut.md:188`]. MIoT tokens and Home Connect logins are fetched once on a setup network.
- Every command has a timeout and a state read-back. python-miio defaults to a 5 s timeout and 3 retries [S python-miio protocol docs].

---

## 1. Control interfaces: how a PC talks to appliances

| Interface | How the PC reaches it | Local? | Device classes | Latency, reliability [E unless S] | Setup and limits | Safety notes |
|---|---|---|---|---|---|---|
| **Xiaomi MIoT, `python-miio`** | Encrypted UDP on port 54321. Needs the device IP and token; tokens come from the cloud once (`miiocli cloud`) [S python-miio docs] | Yes, for Wi-Fi devices | Generic MIoT through `genericmiot`, plus device classes, e.g. a Viomi dishwasher with `start()` (model `viomi.dishwasher.m02`) [S python-miio viomidishwasher] | Default timeout 5 s, retry 3, periodic handshake [S python-miio protocol]. Expect 0.05–0.5 s per command on a quiet LAN [E, not measured] | Community project, not affiliated with Xiaomi [S]. Some new SKUs need the dev branch [S, snip] | Spec access (R/W) ≠ firmware behaviour. Bench every action |
| **`hass-xiaomi-miot`** (HA custom integration) | Modes: Automatic (LAN for miot-spec devices), **Local** (forces LAN; no-LAN devices go unavailable), Cloud; per-entity `miot_local` / `miot_cloud` [S README fork] | Yes in Local mode | Most MIoT devices; also `call_action` for actions [S `research/r19_autostir_market.md:53`] | As above | The README recommends cloud for miio, BLE and Zigbee devices [S] | Use Local mode so a cloud outage can't start or stop anything unexpectedly [E] |
| **Official `ha_xiaomi_home`** | Cloud by default. Local through the Central Hub Gateway, which is **mainland China only**. "LAN control" is "experimental, not recommended" [S ha_xiaomi_home README] | Partial | MIoT-Spec-V2 devices | — | China-market devices may show "not supported region" outside China. The account region may need to be Mainland China [S, snip matterxiaomi blog] | Prefer python-miio / hass-xiaomi-miot local |
| **Tuya** (`tuya-local`, LocalTuya, `tinytuya`) | LAN with a per-device local key from the Tuya developer portal [S privatehomelab] | Yes, Wi-Fi only. **BLE Tuya devices are cloud-only** [S, snip Homey thread] | Plugs, valves, pushers, many Chinese sensor gadgets | — | The local key changes on every re-pair or reset [S, snip]. Newer encryption chips may break old methods (unverified Japanese guide [S, snip]) | Use for non-critical items only |
| **Midea M-Smart** (`midea_ac_lan`, HA core `midea`) | LAN (protocol V1–V3) [S, snip HA midea] | Yes | B6 hood: fan speed, power, light [S B6.md]. E1 dishwasher: power, child lock, storage only; **mode is read-only, and no start is documented** [S E1.md] | — | Rice-cooker type is read-only [S `research/r14_storage_market.md:254`] | A Midea dishwasher can't be started over the LAN integration |
| **Bosch/Siemens Home Connect** | Cloud REST, OAuth. Dishwasher program start: `PUT /api/homeappliances/{haId}/programs/active` (e.g. `Dishcare.Dishwasher.Program.Quick45`) [S API docs] | No (cloud). Local `hcpy` is beta and needs one cloud login [S hcpy, trmm.net] | Dishwashers, hoods (venting level, automatic program [S, snip openHAB]), fridge Door Assistant [S `research/r14_storage_market.md:308`]. Cooktops are read-only [S `research/r15_cooking_market.md:89`] | Community reports of "1000 calls in 1 day" → HTTP 429 [S openHAB forum] | **Remote start must be enabled on the appliance.** The API can only disable it, and it turns off by itself, "usually in 24 hours" [S openHAB binding] | Remote start needs a person (or the arm) to press "remote start" on the appliance before each use |
| **Matter** (HA Matter Server) | Local Wi-Fi or Thread. Thread needs a border router [S HA Matter] | Yes | Plugs, some sensors and valves. No cooking appliances found | No measured figures found [S, snip] | — | Good for plugs |
| **Shelly Gen2/3** | HTTP JSON-RPC, e.g. `/rpc/Switch.Set?id=0&on=true`. HTTP has no keepalive or notifications; WebSocket or MQTT for push [S Shelly docs] | Yes | Relays (1PM), plugs | — | Digest auth optional [S] | Shelly relays are functional only, never the heat interlock |
| **SwitchBot Bot** | BLE, local through HA's SwitchBot integration; "a SwitchBot Hub is not required" [S HA docs]; `pySwitchbot` | Yes | Any mechanical push or toggle button | BLE range needs an ESP32 proxy per zone in some homes [S, snip esp32.co.uk] | 8 N / 1.15 kgf max (one listing); about 600 days at 2 presses a day [S Challenger SG]. A review says some stiff buttons are too hard [S, snip] | Never on a heater's start button outside an armed session [E] |
| **Tuya Zigbee Fingerbot (Adaprox / MOES)** | Zigbee → Zigbee2MQTT, with settable arm limits and sustain time [S Z2M TS0001] | Yes | Push buttons | — | 2.0 kgf, 12 mm stroke, CR2 battery about 1 year at 10 presses a day [S smarthomescene] | Same |
| **Broadlink RM4 mini** | Wi-Fi IR. HA `remote.learn_command` / `send_command`, plus a newer infrared entity [S HA Broadlink] | Yes (setup needs the vendor app) | IR-remote appliances | IR needs line of sight [S, snip] | €21.99 (eBay.de) [S]. SG price ND | No induction cooker with an IR remote was found (ND) |
| **Knob turners** | — | — | — | — | **No consumer product found** (only patents and the open-source haptic SmartKnob [S, snip hackaday]) | Keep the repo's bolt-on knob servo + zero microswitch [S `research/r19_fire_heatcut.md:11`] |
| **Contactor / relay modules** | Already specified: Acti9 iCT etc. [S `research/r19_fire_heatcut.md:68`] | Hard-wired | Heaters | ≤ ~1.5 s heat-off [S `:55`] | LEW work | The real interlock |

**Singapore notes**
- SG sockets are BS 1363 (UK type), so UK-plug Shelly or Tapo plugs fit physically. The Shelly Plus Plug UK is about £21 [S Pi Hut]. The Tapo P110M is sold in SG at S$19.90 RRP / S$15 [S redwhitemobile], and the P110 at S$14.63 [S sourceit].
- Smart plugs are "not clearly a listed category" of Controlled Goods [S `research/r19_sg_compliance.md:93`]. China-plug appliances need SG-plug equivalents or LEW hard-wiring. Universal adaptors can't carry the SAFETY Mark [S `research/r19_sg_compliance.md:102`].
- MIoT devices bought in China are tied to the Mainland China server. Some show "not supported region" elsewhere [S, snip]. Personal radio imports need no IMDA registration [S `research/r19_sg_compliance.md:198`].

---

## 2. Cleaning appliances

### 2.1 Dishwashers

| Model | Type | Remote start / API | Auto-dose | Door | Price | Robot loadability [E] | Src |
|---|---|---|---|---|---|---|---|
| **米家 台式 6 套 S10** `xiaomi.dishwasher.ts10` | Countertop, 35 cm thick, 60 cm door opening, magnetic folding door | MIoT `start-wash`, `pause`, `stop-washing`, `reserve`; `mode` R/W (smart / standard / quick / power / eco / pre-wash / self-clean); `status`, `run-status`, `left-time`, `fault` (incl. "water shortage") | **None in spec** | `door-state` R (open/closed). No door actions | ¥2,299 list; ¥1,439 promo after subsidy (2025-11) | **Good:** racks at counter height. 6 sets is small for 30–45 robot pieces per meal [S `research/r19_food_hygiene.md:307`]. Needs a counter spot in reach | [S miot-spec ts10](https://home.miot-spec.com/spec/xiaomi.dishwasher.ts10); [S ithome](https://www.ithome.com/0/889/756.htm) |
| **米家 嵌入式 18 套 S20** `xiaomi.dishwasher.16s20` | Built-in, under-counter | `start-wash` etc.; `mode` 12 programs R/W; `layered-set` (upper/lower/both) R/W | `detergent-self-delivery` R/W, `detergent-left-level` R | **`open-door` / `close-door` actions**, `auto-open-door` R/W, `door-state` R | Launch ¥4,299; ¥3,439.2 with subsidy (2025-04-29) | **Poor for the arm:** under-counter racks at z < 0.7 m [S `DECISIONS.md:251`]. For the user: auto door + auto-dose remove 2 steps per cycle | [S miot-spec 16s20](https://home.miot-spec.com/spec/xiaomi.dishwasher.16s20); [S ithome](https://www.ithome.com/0/849/891.htm). Note: ithome mentions a 450 mL tank lasting 3 weeks and auto venting with a 6° gap, then auto close |
| 米家 16 套 S20 | Built-in | MIoT (assumed similar [E]) | "智能投放洗碗液" on a JD listing [S, snip JD] | — | ND | Same | [S, snip](https://www.jd.com/tupian/737223ebe3ec4ed8ad8.html) |
| Siemens / Bosch China (`bshcn.dishwasher.*`, about 50 models on MIoT) | Built-in | MIoT, e.g. `bshcn.dishwasher.hx66mc`: `start-wash`, `pause`, `stop-washing`, `reserve`; `mode` R/W (daily/eco/quick/clean/smart) | Not in spec (only salt and rinse levels) | No door property | ND | Built-in | [S miot-spec list](https://home.miot-spec.com/s/dishwasher); [S hx66mc](https://home.miot-spec.com/spec/bshcn.dishwasher.hx66mc) |
| Bosch Series 6 SG (e.g. SMS6ZCI16E) | Freestanding, 14 sets, Zeolith | Home Connect (cloud). Remote start must be enabled on the appliance and lapses after about 24 h [S openHAB] | Model-dependent (ND) | — | S$2,699 (Courts SG, RRP S$3,599) | Freestanding → could stand raised [E] | [S Courts](https://www.courts.com.sg/bosch-dishwasher---14-plate-setting-exclude-installation-sms6zci16e-IP207500.html); Home Connect on SMS4HAW48E [S](https://www.bosch-home.com.sg/en/product/SMS4HAW48E) |
| Viomi / 云米 (18 models on MIoT, incl. a 4-set countertop `viomi.dishwasher.v09`, and a sink dishwasher `v05`) | Countertop and built-in | MIoT; python-miio has a class (`m02`) with `start(program)` | ND | ND | ND | Countertop ones: good | [S miot-spec](https://home.miot-spec.com/s/viomi.dishwasher); [S python-miio](https://python-miio.readthedocs.io/en/latest/api/miio.integrations.viomi.viomidishwasher.viomidishwasher.html) |
| Midea (via `midea_ac_lan` E1) | — | **No start**: power / child lock / storage only; mode read-only | — | `door` binary sensor | — | — | [S E1.md](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E1.md) |
| 方太 水槽洗碗机 E5 (sink-type, 7 sets, 2023) | Replaces the sink | ND (app not checked) | ND | Top lid | ¥8,999 (one undated snippet) | Racks at sink depth: arm reach ND | [S, snip smzdm](https://post.smzdm.com/p/a9gked65/); [S donews](https://www.donews.com/news/detail/5/3107369.html) |

**Woks in a dishwasher.** One guide says 15+-set machines generally fit a 32 cm wok and small countertop units don't [S, snip pconline]. The project's wok is a 34 cm seasoned carbon-steel wok that must never go in the dishwasher [S `research/r19_food_hygiene.md:100`]. So no dishwasher removes the wok wash.

**Dish racks.** No robot-specific rack product was found (ND). The repo's caddies already double as dishwasher baskets [S `DECISIONS.md:540`]. A countertop machine with a fixed basket layout, plus the robot's own keyed caddies, is the practical route [E].

### 2.2 Wok / pan washers (炒锅清洗, 刷锅机, 洗锅机)
- **Home products: ND.** Searches in Chinese and English return commercial machines only [S, snip pconline / search results].
- **Commercial example:** CanCan TBP-1001. Rotating brushes on a hydraulic motor, 0.37 kW, 220–240 V, 16 kg, wall-mounted or on a trolley, US$5,275 [S tribest]. It is a hand-held-pot station, not an automatic washer, so a person or the arm still holds the pot [S].
- **Proposal [E]:** keep the repo's sink rinse under running water [S `DECISIONS.md:392`]. Add a fixed brush in the sink (already listed as an unchecked option there) for a robot scrape. The user's final wash and oil (1–2 min) stay.

### 2.3 Faucets

| Option | Interface | What it does | Price | Limits | Src |
|---|---|---|---|---|---|
| **Clip-on IR sensor in the aerator (O5)** | none (the arm waves under it) | Removes the lever path | ¥37–119 | False triggers as the arm passes; flow loss; battery | [S `research/r19_system_cost.md:221`] |
| **MIoT "smart faucet"** `faucet.kettle.569077` | MIoT: `on` R/W/N; `volume` 0.1–10 (unit not stated; "水量定量值") R/W; `a-glass` 1–10 | A measured-volume faucet the PC can switch | ND (brand and product **not identified**) | Can't buy it without knowing the product | [S miot-spec](https://home.miot-spec.com/spec/faucet.kettle.569077) |
| **Moen U by Moen / 7864EVC** | Moen app, Alexa / Google (cloud). No public API found | Dispenses 1 Tbsp to 15 gal by voice. **A hand wave at the sensor starts the pour** [S Tom's Guide] | US$411.96 sale on one page [S, snip] | US market. No SG listing found | [S moen.com](https://www.moen.com/products/7864EVC); [S](https://www.tomsguide.com/news/the-perfect-pour-moens-voice-controlled-faucet-dispenses-exact-amounts-of-water) |
| **BLANCO EVOL-S Volume** | Knob preset 100 mL–5 L, touch start | Measured cold water | ND | No PC interface | [S](https://blanco.co.uk/company/newsroom/evol-s-volume/) |
| **KLUDI E-GO voice** | Wi-Fi app: preset flow per minute, child lock | — | ND | No public API found | [S, snip](https://kludi.com/sa-en/collections/kludi-e-go-voice) |
| **Under-sink valve actuator** (keep the faucet lever open, switch the angle valve) | Aqara Valve Controller T1: Zigbee via an Aqara hub, Matter-over-bridge to HA; DN15–25; 5–20 s to close; 4×AA [S ameridroid]. Tuya VC-106W: Wi-Fi + BLE, 12 V/1 A wired, DN15/20 [S reach.dog] | PC turns the sink water on/off; E-stop closes the water | T1 US$69.95 / €59.99 / £67; VC-106W US$14 | 5–20 s actuation is slow for 12 sink trips per 3 meals [S `research/r19_system_cost.md:221`]. These are built for rare shut-offs; wear and battery at about 20 cycles per meal are unknown [E]. Conflicts with the user's "no valve" answer (10-12) | [S](https://ameridroid.com/products/aqara-valve-controller-t1); [S](https://reach.dog/shop/ifreeq-expo/products/vc-106) |

- The repo's "Xiaomi water purifier faucet" is not a standalone faucet. Xiaomi warns its purifiers don't fit sensor-type faucets [S mi.com/water/specs].
- A 米家即热净水器 with an app-controlled screen faucet exists (¥3,699–4,299, 2 Pro) [S, snip ithome]. Its MIoT dispense command was not checked (ND).

### 2.4 Clean water: the user's 小米饮水机

| Model (MIoT) | Name | Dispense command | Volume | Temperature | Src |
|---|---|---|---|---|---|
| `xiaomi.ysj.js15` | (name not shown on the spec page) | **`start-out-water` action** | `out-water-volume` 0–10,000 mL R/W; `out-water-time` R/W | `target-temperature` R/W | [S](https://home.miot-spec.com/spec/xiaomi.ysj.js15) |
| `xiaomi.ysj.ymmax` | 饮水机 with ice maker | **No dispense action listed** | `out-water-volume` 0–10,000 mL R/W; `cup-setting` presets | R/W | [S](https://home.miot-spec.com/spec/xiaomi.ysj.ymmax) |
| `xiaomi.ysj.tsa2p` | 米家台式净饮机 NFC | None | None | 25–95 R/W | [S](https://home.miot-spec.com/spec/xiaomi.ysj.tsa2p) |
| `xiaomi.ysj.tsj15` | 米家台式净饮机 凉白开 | None | None | 25–100 R/W | [S](https://home.miot-spec.com/spec/xiaomi.ysj.tsj15) |
| `yunmi.kettle.r3` | 云米即热饮水吧 1A | None | None | 40–90 R/W | [S](https://home.miot-spec.com/spec/yunmi.kettle.r3) |

- **Use if the user's model has a dispense action:** the arm parks the pot or jug under the spout and the PC dispenses N mL at T °C.
  - This removes the kettle-fill chore and the faucet trips for water.
  - It also gives measured blanching or soup water.
  - Spout height vs the 30 cm pot, flow rate and the actual remote behaviour are all ND. Bench-test them.
- **If not:** the dispenser stays a manual fill point, or the arm presses its buttons (the cup-volume key on the panel). Touch panels need a conductive fingertip [E].

### 2.5 Garbage disposer, trash, steam
- **Food waste disposer:** InSinkErator S 60 at S$835 on one SG listing, out of stock [S desertcart.sg]. It would let the robot tip peel and scrap trays into the sink [E]. Plumber or LEW install; HDB/MCST rules ND. Mixing raw-meat waste at the sink conflicts with the sink-zoning rules [S `research/r19_food_hygiene.md:143-148`]. Low priority.
- **Self-sealing bin:** Townew. Motion-sensing lid, seals and changes the bag when the touch button is held. US$119.95, refill rings US$19.95 [S sunset.com]. App ND. A motion lid removes a lid-open motion for the arm's peel drops [E]. The user still empties it.
- **Steam cleaners:** no automatable product found (ND).

---

## 3. Kitchen infrastructure

### 3.1 Range hoods

| Option | Control | Notes | Src |
|---|---|---|---|
| 米家 S10 变频欧式 `xiaomi.hood.ymv9` (and about 70 MIoT hoods: Xiaomi, 云米, 方太 `hzft.hood.358v1`, 老板 `robam.hood.*`) | MIoT: `on` R/W; `fan-level` R/W **0 auto, 1 low, 2 high, 3 爆炒**; light R/W; `off-delay` R/W; `stove-hood-linkage` R/W (only with a paired Mijia gas stove); `execute-dry-cleaning` action | China market. "Auto" needs a matching stove link; with a countertop induction cooker the PC sets the level itself [E] | [S](https://home.miot-spec.com/spec/xiaomi.hood.ymv9); [S list](https://home.miot-spec.com/s/hood) |
| Midea hoods (B6) | LAN: fan speed, power, light | — | [S](https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/B6.md) |
| SG-market Wi-Fi hoods: MOWE MW980B (iAppliances app: remote shut-down, light, fan speed), Tecno TCH959DTC-WFSC, Samsung Bespoke (SmartThings), Bosch Home Connect | Vendor apps (cloud). No local API found | SG plug and SAFETY Mark route | [S MOWE](https://hardwarecity.com.sg/prod/mowe-mw980b-90cm-slim-hood-glass-black--mw390g-90cm-wifi-gas-hob-with-3-burners); [S Tecno](https://harveynorman.com.sg/home-appliances/kitchen-appliances-en/cooker-hoods-en/tecno-90cm-wifi-and-auto-clean-smart-slim-hood-tch959dtc-wfsc.html); [S Samsung](https://www.samsung.com/sg/business/cooking-appliances/hoods/nk8000am-led-36inch-bespoke-wall-mount-hood-clean-white-power-ventilation-system-nk36cb665wwhsp) |
| **Existing hood + SwitchBot Bot** on its buttons | BLE local | Cheapest. 8 N must exceed the button force (measure) | [S Challenger SG](https://online.challenger.sg/products/switchbot-s1-bot-black) |

Recommendation [E]: the hood is on the unswitched circuit and stays on at E-stop (D5) [S `research/r19_fire_heatcut.md:105`]. A SwitchBot on the existing hood gives the PC "on, high" at meal start. Replacing the hood just for an API is not worth it: the hood under-clearance is the binding constraint [S `research/r19_fire_heatcut.md:13`].

### 3.2 Fridge
- **Samsung Bespoke Auto Open Door.** Touch sensors on both sides open the door. The opening level is set in SmartThings [S Samsung SG terms]. On some US models it opens about an inch, then you nudge it [S Samsung US support]. A third-party page says there is no HA entity for it [S, snip selorahomes]. **Not PC-triggerable as found.**
- **Bosch/Siemens Door Assistant.** Settings are writable over Home Connect (Low + Push). A light tap from the arm opens the door [S `research/r14_storage_market.md:308`]. Cloud only.
- **Verdict [E]:** the R14 cold-box design (the arm opens the user's single door with a handle grasp) stands [S `DECISIONS.md:259-283`]. Only revisit if the user changes fridge anyway.

### 3.3 Automatic lids
- **Hinged-lid appliances (O10)** remain the simplest lid saver, about −3 min per 3 meals [S `research/r19_system_cost.md:228`].
- **App cookers with flip lids exist:** 米家智能多功能蒸煮锅 1.5 L, "米家 App 远程操控", ¥199 / ¥169 crowdfunding [S, snip ithome 570883]; 米家智能电压力锅 with app booking [S, snip ithome]; 米家 IH rice cooker app start [S mi.com/tw]. Their lids are manual latches (motorised lids ND).
- **Automatic fail-closed wok lid:** still a custom prototype [S `research/r19_fire_heatcut.md:15`].

### 3.4 Smoke, gas, heat, leak sensors

| Device | Interface | Role | Price | Src |
|---|---|---|---|---|
| Aqara Smoke Detector SD-S01D | Zigbee 3.0 (HA / Zigbee2MQTT tagged) | Alert layer only. Not a heat-chain input: the chain needs a relay-output heat detector [S `research/r19_fire_heatcut.md:52`] | €45 launch; £44.98 UK | [S](https://www.mac4ever.com/domotique/185419-aqara-lance-son-detecteur-de-fumee-connecte-a-45-euros) |
| 小米 天然气卫士 | Drives a solenoid valve through terminals; Mi Home push alarm | Gas hob safety (gas valve closed in sessions [S `research/r19_fire_heatcut.md:30`]) | ND | [S, snip 2021 review: zhongce.sina.com.cn/article/view/91184 or c.m.163.com L5LS9D580530JPVV, not separated] |
| Aqara Water Leak Sensor | Zigbee | Floor under the sink and dishwasher. Triggers the valve (below) and stops the meal | S$28.90 (2023) | [S](https://lesterchan.net/blog/2023/10/26/aqara-water-leak-sensor/) |
| Aqara Valve Controller T1 / Tuya VC-106 | Zigbee (Aqara hub) / Wi-Fi + BLE | Auto shut-off on a leak, and an E-stop water cut | see §2.3 | [S](https://ameridroid.com/products/aqara-valve-controller-t1) |
| DIY: motorised ball valve on a relay + Aqara leak sensors in HA | HA automation | Same, plumbed | — | [S](https://github.com/reefab/homeassistant-water-valve) |

---

## 4. Per-product notes (the shortlist)

1. **米家台式洗碗机 S10 (`ts10`).**
   - The only Wi-Fi-commandable dishwasher found whose racks are at counter height. That is the decisive fact for #31.
   - Ask: is the user's existing dishwasher countertop or built-in, and what model? If it is built-in, the robot can't load it from the dock [S `DECISIONS.md:251`].
   - Gaps: no detergent auto-dose in the spec; the water source (tank or inlet hose) is ND; 6 sets vs 30–45 pieces may need 2 cycles or fewer pieces.
   - The magnetic folding door opens to a 60 cm depth [S ithome]. Whether the gripper can work it is ND [E].
2. **米家 S20 18 套.**
   - The richest API found: door open/close actions, auto-dose, rack-layer selection.
   - Built in, so it suits the **user's** loading: auto door + auto-dose + PC start make the user's part "load, close, walk away" [E].
3. **Water dispenser with `start-out-water`.**
   - If the user's 小米饮水机 is a `js15`-type model, the PC can dispense measured hot or ambient water.
   - The js15 page doesn't show the product name, so match the user's model ID first (Mi Home → device → model).
4. **Faucet.**
   - Cheapest: the O5 clip-on sensor.
   - If the user later accepts a valve, an under-sink actuator gives PC on/off and E-stop water cut without touching the faucet. Wear at about 20 cycles per meal is unknown [E].
   - The MIoT measured-volume faucet (`569077`) is attractive but unidentified.
5. **SwitchBot Bot / Fingerbot.**
   - The universal adapter for any mechanical button: S$37 each, local BLE or Zigbee.
   - Don't use them on heater start buttons outside the armed session [S `research/r19_fire_heatcut.md:187`].
   - Check the button force with a gauge: SwitchBot 8 N, Fingerbot 2.0 kgf ≈ 19.6 N [S].
6. **Matter or Shelly plugs/relays.**
   - Local, metered, power-on state settable [S Shelly docs; E for Matter].
   - Tapo P110M is the cheapest SG option found, at S$15–19.90.
7. **Hood.** A SwitchBot on the existing hood, or an MIoT/Midea hood if it is ever replaced.

---

## 5. Comparison: work removed per meal [E unless S]

| Pick | Arm motions removed | User minutes removed per meal | One-off cost | Risk |
|---|---|---|---|---|
| Countertop DW + #31 | Enables the robot to load and unload | 10–15 [S `research/r19_food_hygiene.md:318`] | ¥1.4–2.3k | Capacity; detergent per cycle; reach check |
| Built-in auto-door / auto-dose DW (user loads) | 0 | about 1 (detergent + start + door) [E] | ¥3.4–4.3k | Built-in install |
| Dispenser dispense-by-volume | Kettle and jug fills, faucet water fills (part of the 6.1 min fill/dump per 3 meals [S `research/r19_system_cost.md` §2]) | R3: 1–3 → 0–1 [S `research/r19_user_workload.md:55`] | 0 if the user's model supports it | Firmware may forbid remote dispense |
| Faucet sensor (O5) | 48 grasps, 2.4 min per 3 meals [S `:221`] | 0 | ¥37–119 | False triggers |
| Button pushers | 1 checked path per button | small | S$37 each | Button force |
| Hood API / pusher | 0–1 | < 0.5 | S$37 (pusher) | — |

---

## 6. Open questions / what to verify

**For the user (photos or Mi Home screenshots are enough):**
1. Dishwasher: brand, model, countertop or built-in, app or none. This decides #31.
2. 小米饮水机: the model ID in Mi Home (e.g. `xiaomi.ysj.*`). Does the app have a remote "出水" button?
3. Hood: brand and model, and whether it has push buttons, a touch panel or a remote.
4. Is a valve actuator on the under-sink angle valve acceptable (it changes no plumbing)? Your 10-12 answer said no valve.
5. Is a countertop dishwasher on the robot's counter leg acceptable as a dedicated robot dishwasher?

**Bench checks (no purchase implied):**
1. MIoT `start-wash` on a countertop dishwasher over **LAN only** (internet blocked): success rate over 100 commands; latency; behaviour after a power cut.
2. Dispenser `start-out-water` + `out-water-volume` over the LAN: volume accuracy (±mL), flow rate, maximum temperature, whether a cup or presence check blocks it.
3. SwitchBot or Fingerbot on the real hood and rice-cooker buttons: force margin, 500-press reliability.
4. A China-market MIoT device registered from SG: region lock, token retrieval, local control.
5. Whether `hass-xiaomi-miot` Local mode covers the chosen models (some new SKUs are cloud-only [S, snip]).
6. The Home Connect remote-start lapse (about 24 h) if a Bosch/Siemens unit is kept: who re-enables it each day.

**Unresolved by search (ND):**
- product names for `xiaomi.ysj.js15` and `faucet.kettle.569077`;
- a countertop dishwasher with auto-dose;
- SG prices for Shelly, Broadlink and the Aqara T1;
- HDB/MCST rules for disposers;
- any home wok washer;
- any appliance knob-turner product;
- an induction cooker with an IR remote;
- a Samsung auto-door API.

---

## Sources (web, read-only, 2026-10-14)

**Control layer**
- python-miio: https://python-miio.readthedocs.io/en/stable/ ; protocol (timeout 5, retry 3): https://python-miio.readthedocs.io/en/stable/api/miio.miioprotocol.html ; Viomi dishwasher: https://python-miio.readthedocs.io/en/latest/api/miio.integrations.viomi.viomidishwasher.viomidishwasher.html
- hass-xiaomi-miot README (fork mirror of al-one): https://github.com/dofine/hass-xiaomi-miot ; upstream https://github.com/al-one/hass-xiaomi-miot
- ha_xiaomi_home README: https://raw.githubusercontent.com/XiaoMi/ha_xiaomi_home/main/README.md
- Mi Home region lock [snip]: https://blog.matterxiaomi.com/blog/region-lock/
- Tuya local [snip]: https://privatehomelab.com/tuya-tinytuya-local-control-no-home-assistant/ ; https://community.homey.app/t/app-pro-tuya-local/154077
- midea_ac_lan: https://github.com/georgezhao2010/midea_ac_lan ; E1: https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/E1.md ; B6: https://github.com/georgezhao2010/midea_ac_lan/blob/master/doc/B6.md ; HA midea [snip]: https://www.home-assistant.io/integrations/midea
- Home Connect API programs: https://api-docs.home-connect.com/programs-and-options/ ; remote-start allowance: https://v51.openhab.org/addons/bindings/homeconnect/ ; rate limit [forum]: https://community.openhab.org/t/homeconnect-the-rate-limit-1000-calls-in-1-day-was-reached-reproduceable/160866 ; hcpy: https://github.com/hcpy2-0/hcpy , https://trmm.net/homeconnect/ ; hood options [snip]: https://v41.openhab.org/addons/bindings/homeconnect/
- HA Matter: https://www.home-assistant.io/integrations/matter/
- Shelly RPC: https://shelly-api-docs.shelly.cloud/gen2/General/RPCProtocol , https://shelly-api-docs.shelly.cloud/gen2/General/RPCChannels/ ; 1PM Gen3 US$19.24/27.49: https://us.shelly.com/products/shelly-1pm-gen3 ; Plus Plug UK: https://thepihut.com/products/shelly-plus-plug-uk
- Tapo SG: https://redwhitemobile.com/phone/tp-link-tapo-p110m/ ; https://sourceit.com.sg/products/tp-link-tapo-mini-energy-monitoring-smart-wi-fi-socket-p110
- SwitchBot: https://online.challenger.sg/products/switchbot-s1-bot-black ; https://www.home-assistant.io/integrations/switchbot ; BLE proxies [snip]: https://esp32.co.uk/switchbot-ble-ecosystem-in-home-assistant-bots-curtains-lock-meters-local-first-2026-setup/
- Fingerbot: https://smarthomescene.com/reviews/tuya-zigbee-fingerbot-button-pusher-review/ ; https://www.zigbee2mqtt.io/devices/TS0001_fingerbot_1.html ; https://www.domadoo.fr/en/roller-shutter-remote-controls/6710-adaprox-smart-button-fingerbot-zigbee-30-tuya-and-zigbee2mqtt.html
- Broadlink: https://www.home-assistant.io/integrations/broadlink/ ; €21.99: https://www.ebay.de/p/17045482028
- SmartKnob [snip]: https://hackaday.com/tag/smart-knob

**MIoT spec pages:** https://home.miot-spec.com/s/hood ; https://home.miot-spec.com/spec/xiaomi.hood.ymv9 ; https://home.miot-spec.com/s/dishwasher ; https://home.miot-spec.com/s/xiaomi.dishwasher ; https://home.miot-spec.com/s/viomi.dishwasher ; https://home.miot-spec.com/spec/xiaomi.dishwasher.ts10 ; https://home.miot-spec.com/spec/xiaomi.dishwasher.16s20 ; https://home.miot-spec.com/spec/bshcn.dishwasher.hx66mc ; https://home.miot-spec.com/s/water_dispenser ; https://home.miot-spec.com/spec/xiaomi.ysj.js15 ; https://home.miot-spec.com/spec/xiaomi.ysj.ymmax ; https://home.miot-spec.com/spec/xiaomi.ysj.tsa2p ; https://home.miot-spec.com/spec/xiaomi.ysj.tsj15 ; https://home.miot-spec.com/s/kettle ; https://home.miot-spec.com/spec/yunmi.kettle.r3 ; https://home.miot-spec.com/s/faucet ; https://home.miot-spec.com/spec/faucet.kettle.569077 ; https://home.miot-spec.com/spec/faucet.kettle.569x51

**Products and prices**
- Dishwashers:
  - 米家 S20: https://www.ithome.com/0/849/891.htm
  - 米家 S10 countertop: https://www.ithome.com/0/889/756.htm
  - JD 16 套 snippet: https://www.jd.com/tupian/737223ebe3ec4ed8ad8.html
  - Bosch SG: https://www.courts.com.sg/bosch-dishwasher---14-plate-setting-exclude-installation-sms6zci16e-IP207500.html , https://www.bosch-home.com.sg/en/product/SMS4HAW48E
  - 方太: https://post.smzdm.com/p/a9gked65/ , https://www.donews.com/news/detail/5/3107369.html
  - Woks in dishwashers [snip]: https://best.pconline.com.cn/guide/89837.html
- Pot washer: https://tribest.com/products/cancan-industrial-pot-washing-machine-1001
- Faucets:
  - Moen: https://www.moen.com/products/7864EVC , https://www.tomsguide.com/news/the-perfect-pour-moens-voice-controlled-faucet-dispenses-exact-amounts-of-water
  - BLANCO: https://blanco.co.uk/company/newsroom/evol-s-volume/
  - KLUDI: https://kludi.com/sa-en/collections/kludi-e-go-voice
  - Xiaomi purifier faucet note: https://www.mi.com/water/specs/
  - 即热净水器 2 Pro [snip]: https://www.ithome.com/0/938/880.htm
- Valves and leak sensors:
  - Aqara T1: https://ameridroid.com/products/aqara-valve-controller-t1 , https://www.euronics.ee/en/it/smart-home/switches/vc-x01d/aqara-valve-controller-t1-white-smart-home-valve
  - Tuya VC-106: https://reach.dog/shop/ifreeq-expo/products/vc-106
  - Leak sensor SG: https://lesterchan.net/blog/2023/10/26/aqara-water-leak-sensor/
  - DIY valve: https://github.com/reefab/homeassistant-water-valve
- Smoke and gas:
  - Aqara smoke: https://www.mac4ever.com/domotique/185419-aqara-lance-son-detecteur-de-fumee-connecte-a-45-euros
  - 天然气卫士 [snip]: https://zhongce.sina.com.cn/article/view/91184 , https://c.m.163.com/news/a/L5LS9D580530JPVV.html
- Hoods SG:
  - MOWE: https://hardwarecity.com.sg/prod/mowe-mw980b-90cm-slim-hood-glass-black--mw390g-90cm-wifi-gas-hob-with-3-burners
  - Tecno: https://harveynorman.com.sg/home-appliances/kitchen-appliances-en/cooker-hoods-en/tecno-90cm-wifi-and-auto-clean-smart-slim-hood-tch959dtc-wfsc.html
  - Samsung: https://www.samsung.com/sg/business/cooking-appliances/hoods/nk8000am-led-36inch-bespoke-wall-mount-hood-clean-white-power-ventilation-system-nk36cb665wwhsp
  - Bosch: https://bosch-home.com.sg/highlights/homeconnect/homeconnect-hoods-and-hobs
- Fridge:
  - Samsung SG terms: https://www.samsung.com/sg/offer/bespokemylife/terms-and-conditions
  - Samsung US support: https://www.samsung.com/us/support/answer/ANS00092042/
  - Third-party HA note [snip]: https://selorahomes.com/devices/samsung/rf29db9900qd/
- Disposer SG: https://www.desertcart.sg/products/182233556-s-60.md
- Townew bin: https://sunset.com/lifestyle/tech/townew-smart-trash-can-self-sealing-changes-bag-for-you
- Mijia app cookers [snip]:
  - https://www.ithome.com/0/570/883.htm
  - https://www.ithome.com/0/525/786.htm
  - https://www.mi.com/tw/mi-induction-heating-rice-cooker/

**Repo:** `DECISIONS.md`, `research/r19_fire_heatcut.md`, `r19_power_budget.md`, `r19_system_cost.md`, `r19_food_hygiene.md`, `r19_user_workload.md`, `r19_sg_compliance.md`, `r14_storage_market.md`, `r15_cooking_market.md`, `r19_autostir_market.md`, `sim/r10/claude/README_R10.md`.
