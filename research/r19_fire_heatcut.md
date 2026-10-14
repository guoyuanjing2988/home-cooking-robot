# R19: fail-off heat cut and fire design (GitHub #19, #22)

Tags: **[S]** sourced (repo `file:line` or URL), **[E]** estimate or proposal, **[M]** sim/model value. Paths are relative to `robot_rail/`. Web sources are read-only snippets or pages, fetched 2026-10-14. Nothing was bought and nobody was contacted.

## Answer first

1. **One hardware layer decides whether any heater can have power: the "heat enable" chain.** Each heat circuit goes through a normally-open contactor (2-pole, L+N). A safety relay energises the contactor coils only while all of these hold: the E-stop chain is closed, the UR robot-stop output is high, a hardware heartbeat watchdog is being fed by the PC, an independent wok high-limit is OK, and the kitchen heat detector is quiet. A person re-arms the relay with a button at the robot. It never re-arms itself. [E]
   - Any fault, a mains outage or a PC crash opens every heat circuit. Power returns with all heat **off**, whatever the appliance does internally. This covers the fryer, which resumes by itself [S `research/r19_power_budget.md:87`], the mechanical stew pot [S `:85`], and a knob-set cooker that might resume [S issue #19].
   - **No cloud start is possible:** with the relay un-armed, a MIoT or app command reaches an appliance that has no power. This is the remote-start rule. [E]
   - Parts are about SGD 1–2k plus LEW labour [E]. The mains side is LEW work [S `research/r19_power_budget.md:206`].
2. **The cooker's knob servo stays the comfort control, and a zero-position interlock covers it.** A microswitch confirms that the knob sits at OFF. Re-arm is refused unless the switch is made. So even a cooker that resumes at its knob setting comes back at 0. [E] Whether the chosen cooker resumes is still unknown. The repo's "standby, fail-safe" entry is an estimate [S `research/r19_power_budget.md:83`, tagged E], so it needs a bench test.
3. **None of the products on the fire list fits the hood.**
   - The hood underside is 0.40 m above the counter [S `DECISIONS.md:362`; M `sim/r10/claude/kitchen14.py:14` hood z 1.25 vs counter 0.85]. The countertop cooker's top is at 0.92 [M `kitchen15.py:31`], so the hood is about 0.33 m above the cooker and **0.23 m above the wok rim** [M `kitchen15.py:13`].
   - StoveTop FireStop needs 27–35" (69–89 cm). The Plus model needs 22–32" (56–81 cm). Even the low-clearance **Microhood** needs 15–27" (38–69 cm) [S WilliamsRDM FAQ, see sources].
   - **Recommendation:** drop the canister. Put prevention first: the heat cut, an independent high limit, a heat detector, and supervision. For suppression, prototype an **automatic fail-closed wok lid** (the only concept that fits 23 cm), and mount a **fire blanket** at the hob leg (S$35). The arm placing the lid is best effort only. The robot is not the suppression [S issue #22].
4. **Supervision policy (user decision).** I recommend "a capable adult at home and awake while any heat is armed". The robot asks for an acknowledgement every 10 min [E]. A missed acknowledgement turns the heat off and parks the arm. The open-wok and fryer phases need the adult on the same floor, reachable within about 1 min [E]. "Remote monitored, nobody home" goes against SCDF's "never leave cooking unattended" [S SCDF] and is not recommended.

---

## 1. Heat sources in the current design

| # | Heat source | Power | Circuit (plan P1) | Control today | After a power cut | Src |
|---|---|---|---|---|---|---|
| H1 | Concave induction 3.5 kW (美的 MC-E35D2 / 九阳 N3501 class) | 3500 W, 15.2–15.7 A | New 20 A radial 1, hard-wired | Bolt-on knob servo, open loop | "Standby; restart needs the knob turned again" **[E]**. Issue #19 suspects it may resume at the knob setting | [S `sim/r10/claude/README_R10.md:503,506`; `research/r19_power_budget.md:83`] |
| H2 | Zone 2 flat MIoT induction (米家 N1) | 2100 W, 9.4 A | New 20 A radial 2 | MIoT; N1 writability **unknown** | Standby [E] | [S `research/r19_system_cost.md:69`; `r19_power_budget.md:84`] |
| H3 | Fryer (Tefal Oleoclean Pro FR8040), 3.5 L oil | 2300 W, 10.0 A | Radial 2 | Smart plug | **Resumes heating hot oil** (mechanical switch) [E] | [S `r19_power_budget.md:87`; `r19_system_cost.md:73`] |
| H4 | Water-bath stew pot | 656 W | Existing kitchen circuit | Smart plug | Mechanical knob unit resumes [E] | [S `r19_power_budget.md:85`; `r19_system_cost.md:70`] |
| H5 | Rice cooker 米家 C1 | 710 W | Existing kitchen circuit | App, or started by the user | Resets to standby [E] | [S `r19_power_budget.md:86`; `DECISIONS.md:243,492`] |
| H6 | Kettle (Philips HD9350 class) | 2200 W, 9.6 A | Existing kitchen circuit | None (R17 says it is optional) | Depends on the switch latch [E] | [S `r19_power_budget.md:88`; `DECISIONS.md:387`] |
| — | User's 4-burner gas hob | — | Gas | Manual | — | Not electrically switchable. The gas valve stays closed during robot sessions (issue #22 step 5) [E] |

Not heaters, but in the safety scope: the knob servo and drum servo, the seasoning pumps, the arm, the cart drives and the gripper.

---

## 2. Heat-cut architecture

### 2.1 Principle
- **De-energise to cut.** Every heater's supply passes a normally-open contactor. Its coil gets 24 V DC only from the safety relay's safety outputs, and the relay has a monitored manual reset. Loss of 24 V, a broken wire, a crashed PC or a mains outage all lead to heat off. [E]
- **Appliance controls stay functional only.** The knob servo, MIoT and smart plugs set the power level and the on/off state *inside* an armed session. "A smart plug is not an interlock" [S issue #19].
- **Feedback.** Each contactor's mirror (auxiliary NC) contact goes to the relay's feedback loop (EDM), so a welded contactor blocks re-arm [E; check the relay model]. A CT on each heat circuit tells the PC that current is actually zero (confirm off) [E].

### 2.2 Inputs that drop the heat-enable chain

| Input | Device | Channels | Trips when | Rough PL [E] |
|---|---|---|---|---|
| E-stop (robot pendant + cart + plating side) | UR pendant E-stop and an external E-stop wired in series into the UR safety inputs | 2 | Pressed | UR safety I/O is rated "PLd Category 3 (ISO 13849-1)" [S UR safety-functions table] |
| Robot stop | UR SF10 "Robot Stop" dual outputs: low during any robot stop, including an external E-stop [S UR table] | 2 | Protective or E-stop | PLd cat 3 from UR [S]; the relay keeps it at cat 3 [E] |
| PC heartbeat watchdog | Hardware watchdog relay (e.g. Red Lion 6HBWDOG1: 1–50 Hz heartbeat, 1–200 s timeout, Form C 2 A @ 30 V DC, DIN rail [S Red Lion datasheet]). The PC toggles a DO at 2 Hz, with a 1 s timeout [E] | 1 | PC hung or off, or the PC software withholds the heartbeat (see below) | about PLb–c (single channel) |
| PC-withheld heartbeat | Software. The PC stops toggling when thermal-camera frames are older than 0.5 s, the camera reads above 250 °C for more than 2 s, presence logic needs it, an acknowledgement is missed, or a CT shows unexpected current [E] | 1 | — | Not rated (comfort layer, but fails safe through the watchdog) |
| Wok high limit | Spring-loaded type-K contact thermocouple on the wok's outer wall + a standalone limit controller with a latching relay (DIN EN 14597 type limiter, or a generic 温控器 with an alarm relay) [E] | 1 | Above 300 °C [E: above the 250 °C working limit S `README_R10.md:508`, below oil auto-ignition 406–435 °C S `research/r15_cooking_market.md:37`] or sensor open while the wok is seated | about PLc |
| Kitchen heat detector | A fixed-temperature or rate-of-rise heat detector with a relay output, on the ceiling at the hob leg, outside the plume axis [E] | 1 | Fire | — |
| Stove guard (optional) | Innohome type, only if it offers a dry contact or its power unit can sit in series with K1 [E] | 1 | Rate of rise | — |

Response time [E]: watchdog 1 s + contactor drop-out < 0.1 s, so heat is off within about 1.5 s of a PC crash. The bench test in issue #19 step 4 must measure this.

### 2.3 Contactors and ratings

| Contactor | Feeds | Rating [E] |
|---|---|---|
| K1 | H1 wok cooker, hard-wired on new radial 1 (20 A MCB + 30 mA RCBO, about 4 mm²) [S `r19_power_budget.md:220`] | 2P **25 A** (≥ the 20 A MCB, so the MCB protects it). Load 15.2 A [S `README_R10.md:503`] |
| K2 | Radial 2 outlet A: H2 zone 2 | 2P 25 A (or 20 A) |
| K3 | Radial 2 outlet B: H3 fryer | 2P 25 A (or 20 A) |
| K4 | A switched outlet group on the kitchen circuit: H4 stew pot, H5 rice cooker, H6 kettle (one heater per 13 A outlet) | 2P 20–25 A, spur fused at 13 A per outlet |

- One contactor per radial would also work. Per-outlet contactors let the PC confirm each heater and let the rice cooker sit outside the chain (see decision D3) [E].
- Robot, PC, cameras, hood fan, fridge and lights are **not** behind the heat contactors.
- Example part: Schneider Acti9 iCT 25 A 2NO, 230 V coil (A9C20732), €29.19 ex tax [S one-elec]. The 24 V DC coil version (A9C21132) is SGD 227.66 ex GST at RS Singapore [S RS SG]. The iCT coil draws about 1.2–1.3 W [S RS listings]. CHINT NCH8-25/20 is the China equivalent (230 V coil 256235, 24 V 256236) [S CHINT catalogue], CNY price not found. Use 230 V-coil contactors with a 24 V interposing relay if the 24 V iCT stays that expensive [E].

### 2.4 Wiring sketch (text)

```
            DB (LEW)                               Contactor box "HEAT" (LEW, DIN rail, at hob leg)
 ┌─────────────────────┐
 │ 20A MCB+RCBO 30mA ──┼── radial 1 ──────── K1 (2P 25A NO) ── DP switch / hard wire ── H1 wok cooker
 │ 20A MCB+RCBO 30mA ──┼── radial 2 ──┬───── K2 (2P NO) ── 13A SSO ── H2 zone 2 (MIoT)
 │                     │              └───── K3 (2P NO) ── 13A SSO ── H3 fryer (smart plug, power-on OFF)
 │ existing kitchen ───┼── 13A FCU spur ──── K4 (2P NO) ── 13A SSOs ── H4 stew / H5 rice / H6 kettle
 │  circuit            │── (unswitched) ─── robot tether, PC, hood, fridge, lights
 └─────────────────────┘
                                                         coils K1..K4 (24 V DC)
 24 V DC SELV (robot side, our build) ─────────────────────────────┘
  │
  ├─ Safety relay (e.g. Omron G9SE / Pilz PNOZ class), monitored manual RESET (button at cart)
  │    CH1/CH2 ◄── UR SF10 robot-stop outputs (dual; include pendant + external E-stops)
  │    series ◄── watchdog relay NO contact  ◄── PC DO heartbeat 2 Hz
  │    series ◄── wok high-limit controller relay (latching, own reset)
  │    series ◄── heat detector relay
  │    series ◄── knob-zero microswitch (in the RESET/start path only)
  │    EDM    ◄── K1..K4 mirror NC contacts in series
  └─ CT clamps on K1..K4 outputs → PC (confirm off, stuck-on alarm)
```

[E] The "series" single-channel inputs reduce the chain's category. If a PLd target is set for them too, use a two-channel safety relay with a second input pair, or a small safety controller. DECISIONS 10-07 says safety PLCs are not required unless the hazard needs one [S `DECISIONS.md:16`].

### 2.5 E-stop scope

| Circuit | On E-stop | Note |
|---|---|---|
| Arm | Stop cat 1, then power removed; tool I/O at 0 V [S UR table SF1] | The gripper's tool power drops while it may hold a hot wok. **Issue #20 must settle this** (PGC self-locking unverified, `sim/r10/claude/hardware.py:31`) |
| Cart drives | STO + spring brakes apply [S `hardware.py:29`, de-energise-to-apply] | — |
| **All heat contactors K1–K4** | Open | Through SF10 → safety relay |
| Knob servo, drum servo, seasoning pumps | Off (24 V actuator rail via a safety-relay contact) [E] | The knob servo holds its last position mechanically, but the cooker is dead behind K1 |
| PC, cameras, network, alarm sounder | **Stay on** [E] | To log, alert and show the user what happened |
| Hood fan and light | **Stay on** [E] | Gaps_electrical #15 asks for this to be decided on purpose. See decision D5 |
| Faucet | Not electric; stays as it was | The arm may leave the tap open (#20, `DECISIONS.md:392`) |

### 2.6 Restart behaviour
1. After any trip or mains return, all contactors stay open. The safety relay needs a manual reset [E].
2. Reset is accepted only if all of these hold:
   - the knob-zero microswitch is made;
   - the PC has sent a "ready" heartbeat;
   - the limit controller is reset;
   - a person presses the button at the robot, which also gives the presence check. [E]
3. After K1 closes, the PC verifies 0 A on the cooker's CT before it turns the knob [E].
4. Appliance-specific behaviour is then a second layer. It is not relied on, but bench-check it anyway (issue #19 step 3):
   - does H1 resume at the knob setting;
   - does H2 come back in standby;
   - is the smart plug's power-on state OFF [S `r19_power_budget.md:231`];
   - does the kettle latch.
5. Interrupted dishes are not resumed automatically. The PC offers the user "discard" or "continue" [E].

### 2.7 Dry-burn and over-temperature layers

| Layer | Threshold | Basis |
|---|---|---|
| Robot software (thermal camera) | Wok below 250 °C, half power when the spatula stops | [S `README_R10.md:508,532`]. Not rated, and has emissivity errors [S `r15_cooking_market.md` §4] |
| Independent contact limiter (new) | 300 °C [E], latching | Below auto-ignition 406–435 °C [S `r15:37`]. Issue: 250 °C is already above oil smoke points of 190–234 °C [S `README_R10.md:508`], so the setpoint needs a 润锅 bench test |
| Cooker's own 防干烧 | ≈280 ± 10 °C, a **typical** value, not the chosen unit's | [S `r15_cooking_market.md:77`] |
| Heat detector → contactors | Fire | [E] |

### 2.8 Stove guard role
- With 2.1–2.7 in place, the Innohome guard is **redundant**. It is UK-market and sold at £461.86 ex VAT (Fire and Safety Centre) [S]. Its power rating and RF band are unverified for SG [S gaps_electrical #25 asks for this], and it may false-trip during normal 250 °C 润锅 [E].
- Recommendation: drop it, or keep it only as one more series input if it offers a dry contact [E].

---

## 3. Fire design

### 3.1 Hood clearance against suppression products

| Option | Required clearance / limits | Fits 0.23 m (wok rim) / 0.33 m (cooker top) under the hood? | Verdict |
|---|---|---|---|
| StoveTop FireStop Rangehood | 27–35" = 69–89 cm; fuse needs "direct, sustained contact with a flame"; oil ≤ 9.5 mm; 6-year life [S `r15_cooking_market.md:315`; FAQ] | No | Drop |
| StoveTop FireStop Plus | 22–32" = 56–81 cm [S FAQ] | No | Drop |
| StoveTop FireStop Microhood | 15–27" = 38–69 cm, wall-mounted under a microwave, ≥ 14" from the back wall [S FAQ]. A 2014 recall: the front canister could fall off [S CPSC 14-745] | No (38 cm minimum; measured to the cooker top or wok, we have 23–33 cm) | Drop |
| Glass-bulb hanging powder units (Chinese 悬挂式干粉 class) | Bulb ratings around 68 °C are common [E, not sourced] | Physically yes, but it sits near the ≈90 °C plume 30 cm above the wok [S `r15_cooking_market.md:39`, an estimate] → false-discharge risk | Not recommended |
| Commercial UL 300 hood wet-chemical | Not found for SG homes [S `r15:323`] | — | Out of scope |
| **Automatic fail-closed wok lid** (new concept) | A 34–36 cm lid on a horizontal slide or a low swing arm behind the wok. Held open electrically, it closes by spring or gravity when 24 V drops or the heat detector or limiter trips [E] | Yes if it moves horizontally: the 23 cm gap fits a flat lid. It conflicts with the drum-holder candidate "behind the wok" [S `README_R10.md:517`] and with the spatula strokes. Needs a sim check | **Recommended for prototyping** |
| Arm places the parked lid | The lid is already "parked within reach" [S `README_R10.md:524`] | Yes | Best effort only. Never relied on (the robot must not be the suppression [S issue #22]) and never with a person in reach |
| Fire blanket at the hob leg (EN 1869) | Falcon 1.2 × 1.2 m S$35 at Hardwarecity SG [S] | n/a (manual) | **Recommended** (user action) |
| Dry-powder extinguisher in the flat | "Each household has at least one dry chemical powder fire extinguisher" certified by an SAC-accredited body (SAFRA article citing SCDF) [S, secondary] | n/a (manual) | Recommended |

### 3.2 Detection
- SCDF says a home fire alarm device (HFAD) is mandatory only in new homes or homes doing fire-safety works with plans from 1 Jun 2018. It recommends smoke-type HFADs with a 10-year battery as the main protection [S SCDF HFAD page]. It gives no kitchen-specific rule [S SCDF page; `r15:328`].
- Proposal [E]:
  - a **heat detector** in the kitchen with a relay output into the heat chain (cooking smoke at 250 °C would false-trip a smoke detector);
  - a **smoke HFAD** just outside the kitchen;
  - the thermal camera as the earliest (software) warning.

### 3.3 Response sequence (proposal [E])

| t | Trigger | Action |
|---|---|---|
| 0 | Camera > 250 °C, smoke seen, or flame seen (software) | PC turns the knob to 0 or 50 %, sounds a local chime, sends a phone push |
| 0 | Limiter, heat detector, E-stop, or missed heartbeat | **All heat contactors open in hardware** (≤ about 1.5 s). The arm goes into a protective stop if the UR is involved |
| +2 s | If the arm is healthy, nobody is within reach (presence sensing), and the wok is not in the gripper | The arm places the parked lid on the wok from the front, the way it already takes lids under the hood band [S `DECISIONS.md:363`]. Otherwise it retreats out of the plume to its safe park |
| +2 s | Auto lid fitted (§3.1) | The lid closes on 24 V loss, independent of the arm |
| ongoing | — | A loud local alarm and a phone alert: "Fire suspected: heat is off. Use the blanket, do not use water on oil, call 995". The hood keeps running (decision D5). Nothing restarts until a person resets at the robot |

### 3.4 Supervision (unattended-cooking) policy

- **Context:**
  - Unattended cooking caused 318 of 1,051 SG home fires in 2025 [S `r15_cooking_market.md:38`, EdgeProp/SCDF].
  - SCDF: "Never leave cooking unattended as it can result in kitchen fires" [S SCDF festive-season page].
  - After a Nov 2025 Yishun fire, SCDF reminded "the public not to leave any cooking or heating activities unattended" [S mustsharenews 2025-11-13, reporting SCDF].
  - The design itself has "the heat source works unattended" while the arm does other things [S `README_R10.md:617`].

| Option | Rule | Pros | Cons |
|---|---|---|---|
| **A (recommended)** | A capable adult at home and awake while heat is armed. The robot asks for an acknowledgement (phone tap or button) every 10 min [E]. A miss gets one reminder, then heat off and safe park after 2 min [E]. Open wok and fryer phases: the adult acknowledges at the phase start. Children or pets are never the only people home | Matches the SCDF guidance and the meal timings | The user must stay home |
| B | A: plus an adult in the kitchen for oil phases (润锅, fryer, 泼油) | Closest to "not unattended" | Less value per meal |
| C | Remote monitoring, nobody home (camera to phone, remote kill) | Most convenient | Goes against SCDF guidance. Remote kill depends on the network and cannot fight a fire. Insurance (#24) |
| D | Never runs without a person in the kitchen | Simplest | Removes most of the robot's value |

### 3.5 Remote-start and network rule (proposal [E])
1. **No heater can be started from outside the flat.** Heat needs the local safety-relay reset, made by a person at the robot (§2.6). Cloud apps (MIoT N1, the rice-cooker app) only reach heaters inside an armed session.
2. Control heaters over the local LAN only: `miio` local for MIoT and local-API smart plugs. The robot and heaters go on their own VLAN without internet egress, except a one-way alert path [S issue #22 step 3, proposal].
3. Rice-cooker delay-start while nobody is home stays out of the robot system. It is the user's own appliance use (decision D3).
4. No remote start of motion. Remote **stop** (drop the heartbeat) is allowed.

---

## 4. Parts and prices (indicative)

| Item | Qty | Price | Tag |
|---|---|---|---|
| Acti9 iCT 25 A 2NO, 230 V coil (A9C20732) | 4 | €29.19 each ex tax | [S one-elec] |
| … or 24 V DC coil (A9C21132) | 4 | SGD 227.66 each ex GST | [S RS SG] |
| Safety relay, Omron G9SE-201 class | 1 | 1,773 SEK ex VAT (RS Sweden); £146.10 for the -221-T30 (RS UK) | [S RS] |
| Heartbeat watchdog relay, Red Lion 6HBWDOG1 | 1 | Price not found; spec sourced | [S datasheet] |
| External E-stop buttons (cart, plating side) | 2 | SGD 50–150 each | [E] |
| Type-K contact probe + latching limit controller | 1 | CNY 150–600 | [E] |
| Kitchen heat detector with relay output | 1 | SGD 50–150 | [E] |
| Knob-zero microswitch + bracket | 1 | < SGD 20 | [E] |
| CT clamps ×4 + reader (or smart meter with CTs) | 1 | SGD 100–250 | [E] |
| DIN enclosure, 24 V PSU, terminals, reset button | 1 | SGD 150–300 | [E] |
| Fire blanket 1.2 × 1.2 m EN 1869 | 1 | S$35 | [S Hardwarecity] |
| Auto-closing lid prototype | 1 | SGD 100–300 materials | [E] |
| **Total parts** | | **≈ SGD 1,000–2,000** (24 V iCT variant at the top end) | [E] |
| LEW: contactor box, the 2 radials, outlets, SS 638 certificate | — | Not quoted (#24 step 3) | [S `r19_system_cost.md:64` "electrician (unknown)"] |

**LEW note.**
- Only LEWs may do electrical work: rewiring, alterations, new points [S `r19_power_budget.md:206`, EMA]. The contactor box is on the 230 V side and is fixed wiring, so the LEW designs, installs and certifies it. It goes into the same job as the 2 new 20 A radials with RCBOs [S `r19_power_budget.md:220-222`].
- We provide only the 24 V SELV side (safety relay, watchdog, sensors) and hand the LEW a terminal list.
- Ask the LEW whether a 15.2 A appliance is allowed under the HDB 15 A rule [S `r19_power_budget.md:202`, to confirm], and whether the contactor box needs anything beyond SS 638 [E].

---

## 5. Open checks (not done here)
- Real cooker behaviour after a power cut, the knob type, and EMC near the coil (#19 step 3).
- Whether the UR5e's PolyScope version offers SF10 exactly as in the UR7e table read here [S UR manual SW5.26, UR7e pages]. The FR5 alternative was not checked.
- Placement of the auto-closing lid against the stir strokes, the drum holder and the 0.23 m hood gap (sim).
- The contact thermocouple on a wok that the arm lifts out for plating: "wok seated" logic, wear [E].
- The hood fan's effect during an oil fire (keep it on or stop it) has no source here.
- The "23 cm" and "0.40 m" hood figures are both in DECISIONS (`:328` and `:362`). They agree only if 0.23 m is measured from the wok rim [M `kitchen15.py:13`]. Measure on site.

## Decisions for the user
- **D1. Supervision rule** (§3.4): A (recommended), B, C or D. Choose the acknowledgement interval N (10 min proposed).
- **D2. Fire suppression:** drop StoveTop FireStop (it does not fit any clearance), and adopt fire blanket + powder extinguisher + an automatic-lid prototype. Yes or no.
- **D3. Rice cooker:** inside the heat chain (an E-stop leaves the rice half-cooked [S `r19_power_budget.md:86`]) or outside it (it may still run on its own app timer). Keep or drop the kettle (R17 says it is not needed).
- **D4. Keep or drop the fryer** (#22 step 4). If kept: K3, a power-on-OFF smart plug, and adult in the kitchen during frying (option B for that phase).
- **D5. On E-stop or fire:** the hood fan stays on (proposed), or it stops.
- **D6. Drop the Innohome stove guard** in favour of the contactor chain plus limiter plus heat detector (proposed), or keep it as a redundant input.
- **D7.** Gas hob valve closed during every robot session (proposed).

## Next steps / issues to file
1. **Heat-chain drawing + terminal list** (closes the design part of #19): a full schematic, the E-stop matrix, PL assignment per function.
2. **Bench: watchdog prototype.** Kill the PC process and the camera feed. Time heat-off on a dummy load (#19 step 4).
3. **Bench: 2 candidate cookers.** Power-cut behaviour, knob type, knob-zero switch fit, EMC (#19 step 3).
4. **Sim: auto-closing lid** under the 0.23 m hood gap vs the stir strokes and the drum holder (new issue, links #22).
5. **Bench: contact high-limit** on a seasoned wok during 润锅. Pick the setpoint (new issue).
6. **LEW scope add-on:** a contactor box on the 2 new radials plus a switched spur (feeds #24 step 3).
7. **DECISIONS entry** for D1–D7 once answered. Update `meal16.py` for acknowledgement pauses if option A or B is chosen (#22 step 1).
8. **Network:** local-only miio test over 500 commands, VLAN plan (#19 step 5, #22 step 3).
9. Cross-links: #20 (gripper tool power drops on E-stop while holding the wok), #21 (risk assessment uses this heat-cut PL), #24 (LEW, insurance, SAFETY Mark).

## Sources (web, read-only)
- WilliamsRDM StoveTop FireStop FAQ (Rangehood 27–35", Plus 22–32", Microhood 15–27", 6-year life, flame-contact activation): https://images.homedepot-static.com/catalog/pdfImages/15/15a57434-1b47-48d4-97bc-9c607998c992.pdf [read]
- CPSC recall 14-745, StoveTop FireStop Microhood: https://www.cpsc.gov/Recalls/2014/WilliamsRDM-Recalls-StoveTop-FireStop-Microhood [read]
- SCDF, Festive Season Fire Safety Alert ("Never leave cooking unattended…"): https://www.scdf.gov.sg/eventslisting/newsarticledetail/Festive-Season---Fire-Safety-Alert [read; page dated 2006, updated 2024]
- SCDF HFAD page: https://www.scdf.gov.sg/home/fire-safety/home-fire-alarm-device-(hfad) [read]
- Yishun fire, SCDF reminder, 13 Nov 2025: https://mustsharenews.com/yishun-kitchen-fire/ [read]
- SAFRA article, household dry-powder extinguisher: https://nsman.safra.sg/?p=15256 [search snippet]
- UR safety functions table (PLd Cat 3, SF1, SF10): https://www.universal-robots.com/manuals/EN/HTML/SW5_26/Content/prod-usr-man/complianceUR7e/safetyFunctionsAndinterfaces/safety_functions_table1.htm [read]
- Red Lion 6HBWDOG1 heartbeat watchdog relay: https://www.redlion.net/sites/default/files/138/3989/Watchdog%20Data%20Sheet_0.pdf [search snippet]
- Acti9 iCT A9C20732 €29.19: https://one-elec.com/en/a9c20732-ict-25a-2no-230240v-50hz-contactor-schneider.html ; RS SG A9C21132 SGD 227.66: https://sg.rs-online.com/web/p/contactors/2201196 [search snippets]
- CHINT NCH8 catalogue (256235 / 256236): https://npower.com.vn/cdn/shop/files/CHINT_gioithieu_NCH8-Modular_AC_Contactors-Catalog.pdf [search snippet]
- Omron G9SE prices: https://se.rs-online.com/web/p/safety-relays/2655203 , https://uk.rs-online.com/web/p/safety-relays/2655205 [search snippets]
- Innohome Stove Guard £461.86 ex VAT: https://www.fireandsafetycentre.co.uk/products/innohome-stove-guard [search snippet]
- Falcon fire blanket 1.2 × 1.2 m S$35: https://hardwarecity.com.sg/prod/falcon-fire-blanket-12m-x-12m [search snippet]
- No source found for: whether Chinese concave induction cookers resume after a power cut (pconline Q&A pages give nothing on this), SG prices for a home suppression unit rated for low clearance, or the Innohome RF band and current rating.
