# R19: tether redesign for the cart with an off-board controller (GitHub #18)

Date: 2026-10-14. Desk study only: repo files plus read-only WebSearch/WebFetch. Nothing bought, no logins, no forms, nobody contacted. No other file was changed.

**Labels**
- **[S]**: sourced. Either a repo `file:line` or a URL (official vendor pages are marked "UR", "igus", etc.; shops and distributors are named).
- **[M]**: my arithmetic on [S] inputs (the formula is given).
- **[E]**: my engineering estimate; not sourced.

---

## 0. Answer first

**Recommended architecture: put the arm controller back on the cart in its small DC version. The tether then becomes one slim 48 V SELV/PELV bundle (power, PE, Ethernet, a 2-channel E-stop pair) in a small energy chain on one straight leg. The chain lies on its side in the void under the base cabinets, behind a slotted kickboard.** In more detail:

1. **The proprietary arm cable never moves.** FR5: the FAIRINO DC control box is 245 × 180 × 44.5 mm, **2.04 kg**, 30–60 VDC in [S FAIRINO brochure, see §9 S5]. UR5e: the UR OEM Control Box DC is 451 × 150 × 168 mm, **4.3 kg**, 19 / 24–48 / 72 VDC [S S3]. Those masses are not what the user objected to. R09 carried a 13.6 kg AC controller **plus 46.6 kg of ballast** (`sim/r10/claude/README_R10.md:8`). Today's cart BOM already includes 1.5 m of UR cable on the cart (`sim/r10/claude/R19_CART.md:77`).
2. **Only SELV-class DC goes through the moving part.** A 48 V supply with an inrush limiter and a regen dump sits off-board in a dry cabinet, behind a 30 mA RCBO. The cart's 48 V bus feeds the controller, the hub drive, the IPC and the dock pin.
3. **Moving part = a small igus E2.26-class chain, R 75–100 mm, about 2.5 m long, centre-fed** [M, §4]. It works for either arm and does not depend on the FR5's unknown arm-cable flex rating.
4. **Route (subject to a site check):** the chain lies on its side in the plinth void under the base cabinets, and a tow arm on the cart passes through a brush-sealed slot in the kickboard. Nothing is added to the floor in front of the doors beyond the #39 rail.
   - **If there is no void** (masonry kerb plinth, which is common in HDB flats [E]), use the fallback: an industrial spring or motor reel with a power + Ethernet slip ring (Conductix SR class [S S9]). The taut cable runs in a covered slot along the #39 floor rail.
5. **L corner: the cart and its tether stay on one straight leg.** R19_DOCK already says the cart cannot turn the corner on its rail (`sim/r10/claude/R19_DOCK.md:172`). No floor energy chain turns an L with linear travel on both legs [E]. If one cart must serve both legs, only two options exist: an overhead festoon on a curved C-track, or a battery (§5). That is a user decision.

**Fallback if the user refuses any controller on the cart (option A):**
- **UR5e:** UR officially allows its **High Flex base cable in a drag chain**: PUR, Ø 13.4 mm, dynamic bend radius 8 × d (≈ 107 mm [M]), 5 million cycles, P/N 166100 (6 m) / 166101 (12 m) [S S1, S2]. The chain then needs R ≥ 125 mm, and the same route is roughly 1.6× wider (§4).
- **FR5:** the arm-cable length and flex rating are **not published** (§1.2). This is a vendor question.

**Rejected:**
- The stock Brennenstuhl reel, which stays BLOCKING (`posts/r09/reviewer.md:58`).
- Any slip ring or reel carrying the UR base cable. UR already warns against a third connector in the arm link [S S1].
- A floor chain lying in the aisle (trip hazard, §5).

---

## 1. Arm-cable facts

### 1.1 UR5e (e-Series)

| Item | Value | Tag |
|---|---|---|
| Arm-to-control-box cable options | Standard PVC 1 / 2 / 3 / 6 / 12 m, Ø 12.1 mm; High flex PUR 6 / 12 m, Ø 13.4 mm (an older manual also lists a 14.6 mm high-flex version) | [S S4] |
| Standard cable (ships with the arm, P/N 165100 6 m / 165101 12 m) | "no official bend cycle or dynamic bend radius"; static minimum bend radius 78 mm | [S S1] |
| **High Flex cable** (P/N 166100 6 m / 166101 12 m) | PUR, blue, Ø 13.4 mm; bend radius **4 × d static, 8 × d dynamic**; **5 million bend cycles**; "**drag chain suitable**, and allows expansion of the robot workspace using 7th axis solutions" | [S S1, S2] |
| Dynamic minimum radius for Ø 13.4 | 8 × 13.4 = **107.2 mm** → choose a chain R ≥ 125 mm | [M] / [E] |
| Smaller radius | "If used with smaller bend radius, the bend cycle life is reduced" | [S S1] |
| Length rules | Max arm-to-box length **12 m**. "Do not extend a 6 meter cable due to signal loss in having three connectors". Exception: a 6 m cable mounted on the base plate may take an extra 6 m standard or High Flex cable | [S S1] |
| Requirement | The arm needs the **Base Flange Connector** (UR5e P/N 1103xx, e.g. 110305). Arms without it can be upgraded by UR Service | [S S1] |
| High-flex price | Not listed ("Request information") | [S S2] |
| Standard control box | 460 × 449 × 254 mm, 100–240 VAC | [S S4]; 12 kg, IP44 per `research/r19_arm_hand_cost.md:128` |
| **OEM Control Box DC** | 451 × 150 × 168 mm; **DC 4.3 kg** (AC 4.7 kg); input 19 / 24–48 / 72 VDC; external fuse ≤ 100 A; **inrush ≤ 400 A**; heat ≤ 100 W for UR5e/UR3e | [S S3]; also `sim/r02/transport/results/power_addendum.md:9,23` |
| OEM box IP rating, ambient temperature, price, sale to an end user | not on the page | ND → vendor question |

**Verdict:** the UR5e arm cable **can** run in a drag chain, but only as the High Flex PUR cable. The 6 m PVC cable that ships with the arm is not dynamically rated, so the High Flex cable has to be bought separately.

### 1.2 Fairino FR5

| Item | Value | Tag |
|---|---|---|
| Arm mass | 22 kg | [S S5 p.5]; `research/r19_arm_hand_cost.md:43` |
| Arm-to-box connection | "connected using pluggable and quickly installed plugs" | [S S6] |
| **Arm cable length, diameter, bend radius, drag-chain rating** | **not published** in the English manual, the 2026 brochure or the reseller pages read | ND [S S5, S6, S7, S8] |
| 5 m cables in the brochure | these belong to the safety button box and the teach pendant, **not** the arm | [S S5 p.7] |
| DC control box | 245 × 180 × 44.5 mm, **2.044 kg**, galvanized plate, input **30–60 VDC**, output 48 VDC / 104 A max; AC box 2.5 kg (narrow-voltage 220 VAC) | [S S5 p.9] |
| DC box retail (separate SKU, "delivered without cables", IP54, 2 kW / 5 kW) | €935 ex VAT = €1,112.65 incl. VAT (2 kW); €1,886.15 (5 kW) | [S S7, welectron] |
| Grounding | "The robot needs to be electrically grounded." | [S S6] |
| Control-box mounting height (installation guide) | 0.6–1.5 m | [S S6 robot_brief_introduction] |

**Verdict:** whether the FR5 arm cable can be used in a chain is unknown [E]. Ask Fairino (§8). With the 2 kg DC box on the cart, the question goes away.

---

## 2. Conductor lists

### 2.1 Cart loads (power budget)

| Load | W | Tag |
|---|---|---|
| Arm (UR5e) | 200 typical / 570 max | [S `research/r19_power_budget.md:89`] |
| IPC + sensors | 60 | [S same] |
| Gripper | 24 | [S same] |
| Drive supply (ZLAC8015D + 2 hub motors) | 270 | [S same; `sim/r10/claude/hardware.py:33`] |
| Brake coils + safety sensors | 40 + 20 | [E in `r19_power_budget.md:89`] |
| Dock pin, scale head, inclinometer (#39) | ≈ 10 | [E] |
| **Robot total** | **≈ 994 W peak**; mean 180 idle / 370 with the arm moving | [S `r19_power_budget.md:89`] + [E] 10 W |
| At 48 V | **≈ 20.7 A peak, ≈ 7.7 A mean** | [M] (994 / 48, 370 / 48) |

The FR5 draws less: 276 W average / 410 W peak (`research/r19_arm_hand_cost.md:129`).

### 2.2 Recommended: controller on the cart (option C), the moving tether

| # | Conductor | Size / type | Why | Tag |
|---|---|---|---|---|
| 1 | +48 V, 0 V | 2 × 6 mm², chain-rated single cores (PUR/TPE) | 20.7 A peak. Loop 2 × 6 m × 3.08 mΩ/m = 0.037 Ω → **0.77 V (1.6 %)** drop at peak. With 4 mm²: 1.1 V | [M] (6 m route [E]; Cu 6 mm² 3.08 Ω/km [E]) |
| 2 | PE / bonding | 1 × 6 mm² green-yellow | Treat the 48 V system as PELV: bond the cart frame, arm base, motors and floor rail. Fairino requires grounding | [S S6] + [E] |
| 3 | Ethernet | 1 × 2-pair 100 Mbit industrial (PROFINET-type), chain-rated, Ø ≈ 6.5 mm | Host / Wi-Fi bridge ↔ cart IPC and controller (UR RTDE 500 Hz needs a wire only between the IPC and the controller, and both are on the cart) | [S `r19_arm_hand_cost.md:145` RTDE]; [E] size |
| 4 | Safety | 1 × 4 × 0.5 mm² shielded | 2-channel NC loop from a wall / off-board E-stop to the controller's safety inputs. Use 8 cores if the presence sensor is off-board (2-ch OSSD + 24 V) | [E] |
| 5 | Gripper RS485 | **none in the tether** | The gripper cable plugs into the arm's tool connector (UR M8 8-pin; FR5 RS485 5-pin) | [S `DECISIONS.md:587,661`] |
| 6 | Finger force sensor | **none in the tether** | The UR TCI disables the tool analog inputs, so the sensor needs its own cable, but it runs arm → cart IPC | [S `research/hand_options.md:96-97`] |
| 7 | Arm cable | **stays on the cart** (≈ 1.5 m) | — | [S `R19_CART.md:77`] |

- **Bundle:** about 5 cables with Σ Ø ≈ 6.5 × 3 + 6.5 + 8 ≈ 34 mm [M on E diameters]. This fits a chain with inner height ≥ 12 mm and inner width ≥ 38–50 mm [E].
- **Bend radius:** igus CFBUS bus cables need 10–12.5 × d in a chain [S S11], about 65–106 mm for Ø 6.5–8.5. **Chain R 75–100 mm** [E].
- **Variant "power-only tether"** [E]: Ethernet goes over Wi-Fi (non-safety supervision only; WLAN is not credited as a safety channel, `posts/r02/transport.md`, §Power), and the E-stop stays on the cart. The tether is then 3 cores (2 × 6 mm² + PE). This is the easiest case for a reel with slip rings.

### 2.3 Option A: controller off-board, moving tether

| # | Conductor | UR5e | FR5 | Tag |
|---|---|---|---|---|
| 1 | Arm cable | **UR High Flex 6 m (166100) or 12 m (166101), Ø 13.4, R_dyn ≥ 107 mm** | ND: length, Ø, flex rating, extension | [S S1] / ND |
| 2 | Cart 48 V (drive 270 + IPC 60 + brakes and safety 60 + dock 10 ≈ 400 W → 8.3 A) | 2 × 2.5 mm² | same | [M] / [E] |
| 3 | PE | 1 × 2.5–6 mm² | same | [E] |
| 4 | Ethernet IPC ↔ controller | 1 × 2-pair, Ø ≈ 6.5 | same | [E] |
| 5 | Safety | cart E-stop 2-ch → controller safety inputs; controller safety output → drive enable / STO: 8 × 0.5 mm² | same | [E] |
| 6 | Gripper RS485 | inside the arm cable via the tool connector | inside the arm cable via the end RS485 port | [S `DECISIONS.md:587,661`] |

- **Bundle:** 13.4 + 9 + 6.5 + 8 ≈ 37 mm Σ Ø → inner width ≥ 50–77 mm, inner height ≥ 16 mm, **R ≥ 125 mm** [M / E].
- **UR 6 m length check:** 2.5 m chain + 1.5 m on the cart + ≤ 2 m fixed run. The UR control box must therefore stand within ≈ 2 m of the chain's fixed point (a base cabinet near mid-leg), or else the 12 m cable is needed [M].

---

## 3. Geometry the tether must serve

| Item | Value | Tag |
|---|---|---|
| Floor rail | 40 × 30 extrusion, **4.6 m**, x −1.82…+2.80, y −45…−5 mm (in front of the door / plinth plane), z 0…33 | [S `R19_DOCK.md:17,113-116`] |
| Cart travel | x −1.48…+2.46 → **S = 3.94 m** | [S `R19_DOCK.md:75`]; [M] |
| Cart underside | z 90 mm. Under the front: rail + V-wheels + keepers up to z ≈ 62 | [S `R19_DOCK.md:98-110`] |
| Cart moves while the arm works | 457 of 463 wok segments | [S `R19_DOCK.md:31`] |
| Tether force cap in the tip / slide checks | 20 N at 0.10 m | [S `sim/r10/claude/mobile.py:65`; `R19_CART.md:309`] |
| Corner | one rail per straight leg; the cart cannot turn the corner | [S `R19_DOCK.md:172`] |
| Real kitchen | L; sink leg ≈ 3.0–3.2 m; wok on the hob leg, sink on the other leg; the sim folds the work into one straight run | [S `inputs/user_kitchen/estimate.md`; `README_R10.md:817`; `R19_DOCK.md:172`] |
| Toe recess / plinth | **not visible in the photos; unmeasured** | [S `R19_DOCK.md:173-177`] |

**R19_DOCK.md:116 problem.** The text says the rail "carries the tether in its bore". A closed extrusion bore can only carry **fixed** wiring. A cable that pays out to a moving cart needs an open, lipped slot (reel option) or a chain [E]. That sentence should be corrected when #39 is next revised; this file does not edit it.

---

## 4. Energy-chain sizing (both options)

- **Chain length (centre feed):** L ≈ S/2 + πR + 0.1 m.
  - R 100 → 1.97 + 0.31 + 0.1 = **2.4 m**
  - R 125 → **2.5 m** [M]
  - The fixed point sits at mid-travel, x ≈ 0.49 [M].
- **Vertical-plane chain:** loop height 2R + h_o. R 75 → ≈ 185 mm; R 125 → ≈ 300 mm (h_o ≈ 35–50 mm [E]).
  - The loop always sits **beyond** the cart in x, and the lower run passes the cart's own y band [M, standard e-chain kinematics].
  - The only free band is under the cart (90 mm clear) or in front of the doors. Neither can take a 185–300 mm loop, so **a vertical-plane floor chain does not fit** [E].
- **Side-lying chain** (bend in the floor plane; igus supports side-mounted chains over long travels in a guide trough [S S12]):
  - Height = the chain's outer width ≈ 50–65 mm [E].
  - Depth = 2R + h_o: **≈ 190 mm (R 75), ≈ 240 mm (R 100), ≈ 300 mm (R 125)** [M on E h_o].
- **Candidate chains:**
  - igus E2.26 family: inner height 26 mm; inner widths seen 25 / 38 / 77 mm; radii seen 48 and 175–250 mm. Whether R 75–125 is stocked is [E] and goes to the igus configurator. Prices seen:
    - E2C.26 38 mm / R48: €1.30 per link;
    - E2.26.038.200.0 (1.012 m): US$67.47;
    - E2.38 (inner height 38 mm, inner width 50 mm): £71.65/m [S S13, S14, S15].
    - A 2.5 m chain is therefore **≈ €75–180** plus mounting brackets [M].
  - Hygienic **igus TH3** (FDA-compliant material, −40…+70 °C, open screwless design):
    - TH3.25: inner height 25.5 mm, R ≈ 70, unsupported ≤ 1.2 m;
    - TH3.45: inner height 45 mm, R ≈ 90, unsupported ≤ 1.5 m.
    - TH3 fits **option C**. At R ≈ 90 it is below the UR cable's 107 mm, so it does not fit option A as listed [S S16].
- **Mass:** chain ≈ 0.4–0.6 kg/m plus cables ≈ 0.3–0.6 kg/m → 2–3 kg moving, mostly carried by the floor [E].
- **Drag force:** a gliding side-lying chain needs a few N [E], within the 20 N cap [S `mobile.py:65`]. Check it in the bench test.
- **Cycles:** #18 asks for a 1,000-cycle bench test. UR rates the High Flex cable at 5 M cycles [S S1]. Expect hundreds of short strokes per meal [E].

---

## 5. Options compared

| | (a) Energy chain | (b) Spring / motor reel | (c) Controller on the cart (DC box) | (d) Battery on the cart |
|---|---|---|---|---|
| What moves | the bundle of §2.2 (with c) or §2.3 (alone) | a single round cable, taut | — (tether as in a or b) | nothing |
| UR arm cable | allowed (High Flex) [S S1] | **no**: a slip ring adds contacts on a link UR already limits to 2 connectors [S S1] → only with (c) | stays on the cart | stays on the cart |
| FR5 arm cable | ND, vendor question | no → only with (c) | stays on the cart | stays on the cart |
| Mass on the cart | +0.3–0.5 kg tow arm / inlet [E] | +0.3 kg inlet [E] | **+2.0 kg (FR5) / +4.3 kg (UR OEM DC)** + IP54 enclosure 1–2 kg [S S5, S3; E] | 48 V ≈ 1 kWh LiFePO4 ≈ 9–12 kg + BMS / charger contacts [E] |
| Effect on #14 sliding | — | — | **helps**: low mass; 10 kg ballast lowers the wok's μ need 0.43 → 0.36 (#14) | helps (low mass) |
| Corner (L) | **no**: one chain per leg; a corner handover needs an automated connector swap [E] | no (a straight cable path) | n/a | **yes** (no tether), if the cart itself can turn |
| Travel / size | S 3.94 m; chain 2.4–2.5 m; side-lying depth 190–300 mm × 50–65 mm high | drum + slip ring at the rail end; Ethernet over a slip ring up to 2 × CAT6, 50 m travel [S S9]; spring life ≈ 120,000 cycles (Vahle) [S S10] | DC box 245 × 180 × 45 (FR5) / 451 × 150 × 168 (UR) | pack ≈ 300 × 200 × 150 [E] |
| Price | chain €75–180 [M] + trough / brackets + slotted kickboard ¥500–1,500 [E] + chain cables ¥500–1,500 [E] | industrial SR reel with a CAT6 slip ring: ND (≥ ¥5k [E]); repo allowance ¥4,500 [S `r19_system_cost.md:56`] | FR5 DC box €935 ex VAT [S S7]; UR OEM DC price ND. 48 V PSU + current limit: allowance ¥2,500 [S `r19_system_cost.md:57`] | ¥2–4k pack [E] + dock charger |
| Home installation | plinth void + slotted kickboard (no drilling into tiles) or a raised floor duct | reel housing at one end of the rail; cable in a lipped slot of the rail | an enclosure on the chassis; 100 W heat (UR) [S S3] | charge contacts at PARK |
| Cleaning / food | at floor level, away from food. PUR/TPE jackets, open chain (TH3) [S S16]. Brush seal against mop water | a taut cable in a slot: dirt is dragged into the slot and onto the drum [E] | the enclosure needs IP54 near the wok steam; the FR5 DC box is IP54 [S S7] | sealed pack |
| Trip hazard | none if inside the void. A 190–300 mm wide floor duct in the aisle is **rejected** | low (inside the rail profile) | — | none |
| Status | proven technology; geometry depends on the site | spring tension varies with payout. The R09 consumer reel stays **BLOCKING** [S `posts/r09/reviewer.md:58`]; only an industrial powered-use reel is acceptable | **against the R10 choice** (`README_R10.md:8`), but at 1/6 – 1/3 of the controller mass that was removed and without the ballast | **against a binding decision**: "no battery" [S `DECISIONS.md:3,83`] |

**Overhead festoon or a trolley with a spring balancer** (sub-option of a): the only tether that can follow an L.
- Hardware: Conductix 0230 small C-rail, 30 × 32 mm, 20 kg per trolley, "mainly linear, curved tracks feasible to some extent" [S S17]. A drop cable to the mast, with the lead trolley towed by the drop (low-friction trolley, < 20 N [E]).
- Against it:
  - It needs a ceiling or cabinet-top run over the aisle. The gap from the cabinet tops to the ceiling is unknown [S `DECISIONS.md:88`].
  - The loops hang 0.2–0.4 m [E] and collect grease from the hob.
  - The drop line enters the arm's rear workspace and needs a collision check.
- Verdict: keep it only for the case where the cart must cross the corner.

---

## 6. Installation detail of the recommended route [E unless tagged]

- **Plinth void.**
  - Many fitted cabinets stand on adjustable legs behind a clip-on kickboard, which leaves a void about 100–150 mm high and 450–500 mm deep [E].
  - A side-lying R 75–100 chain needs 190–240 mm of depth and ≈ 60 mm of height [M].
  - It runs in a 1 mm stainless or plastic trough, behind the front leg row.
- **Tow arm.**
  - A stiff arm from the cart's front passes over the #39 rail (rail top z 33–43 [S `R19_DOCK.md:98-110`]) at z ≈ 50–80, under the cart underside at z 90.
  - It goes through a 25–30 mm slot in a replacement aluminium kickboard with a brush strip.
  - The front cabinet legs that would cross the tow-arm path must move back or be replaced by a continuous plinth beam. **This needs a site survey.**
- **Fixed point:** at mid-travel, x ≈ 0.49. The fixed cable runs inside the cabinet to the 48 V supply in a dry base cabinet, away from the sink drip line.
- **Wet zone.**
  - Inlet connectors on the cart IPX4+ (M12 / M23 class).
  - Brush seal at the slot; the trough has drain holes.
  - Nothing electrical is open below the sink edge.
  - The 48 V side stays SELV/PELV. The mains side has a 30 mA RCBO (this matches the R19 power plan, `r19_power_budget.md:59-60`).
- **48 V source.**
  - About 1–1.5 kW, current-limited.
  - Inrush limiter: the UR OEM DC box inrush is ≤ 400 A [S S3].
  - A regen dump or chopper for the hub drive and arm braking.
  - Mains side on the existing kitchen circuit: 994 W ≈ 4.5 A at 230 V [S `r19_power_budget.md:89`].
- **If there is no void (masonry plinth):** use the reel (b) with the **power-only tether** variant.
  - The cable lies in a lipped slot added to the aisle face of the #39 extrusion.
  - The drum sits in the alcove at the x +2.8 end.
  - Constant tension comes from a small torque motor rather than a spring [E].

---

## 7. Decisions for the user

1. **Controller on the cart in its DC version (recommended)?** It adds +2.0 kg (FR5) or +4.3 kg (UR OEM DC) plus an enclosure, low in the chassis. The tether then carries only 48 V + PE + Ethernet + E-stop, and the arm cable never moves. Without it: UR5e High Flex cable in an R ≥ 125 chain; FR5 blocked until Fairino answers.
2. **Corner:**
   - Keep the cart on **one leg** (current design).
   - Or require it to serve both legs (sink on the other leg, `README_R10.md:817`). Only an overhead curved festoon or a battery allows that, and a battery reverses "no battery".
3. **Allow a replacement slotted kickboard** and possibly moving front cabinet legs (route of choice), or prefer the reel in the rail profile.
4. **Wired Ethernet in the tether, or Wi-Fi for supervision only** (E-stop on the cart)? The second makes the tether 3 cores.
5. **Is a wall E-stop off the cart wanted?** It needs a 2-channel pair in the tether.

## 8. Questions for vendors (not sent)

**Universal Robots / partner**
1. Price and lead time in China/SG of the High Flex cable 166100 / 166101, and the arm's Base Flange Connector status.
2. Is the OEM Control Box DC sold to an end user for a UR5e, at what price, with which teach pendant / safety I/O, and at what IP rating and ambient range? Is mounting on a moving cart (vibration, 0.5 m/s²) approved?
3. Minimum chain radius actually tested with 166100. Is R 125 confirmed for 5 M cycles?

**Fairino**
1. FR5 arm-to-control-box cable: length, Ø, connector, minimum dynamic bend radius, drag-chain (high-flex) variant, longest available or extension.
2. DC control box: IP rating, heat, inrush, regen behaviour on a 48 V bus shared with a hub drive, and mounting on a moving cart.

**igus**
- Side-lying E2.26 / TH3 at R 75–100 over 3.94 m of travel in a 60 mm-high trough: unsupported length, drag force, and a chainflex set for 2 × 6 mm² + PE + Ethernet + 4 × 0.5.

**Conductix / Vahle**
- A small powered-use reel with a 48 V / 25 A + CAT5 slip ring, 5 m payout, constant tension ≤ 20 N, and its cycle life.

## 9. Next steps

1. **Site survey (user, 15 min):** take off one kickboard. Photograph and measure the void height and depth, leg positions and plinth material, the toe-recess depth, and the cabinet-top-to-ceiling gap.
2. Get the user's decisions in §7. Then update `hardware.py` / `R19_CART.md` with the controller mass and position (an input to the #14 tip and slide checks).
3. Draw the chain route, the tow arm and the slot (CAD in `sim/r10/claude/cad/r19_cart/`), and add the tow arm to the #39 travel screen.
4. Make the SLD: off-board PSU / RCBO / fixed point; cart 48 V bus, fuses, PE bonding, the 24 V logic branch; the network map.
5. Bench test per #18 step 5: 1,000 cycles at 0.25 m/s with a tension log, on the real chain + cables (or the reel).
6. Correct the "tether in its bore" sentence in `R19_DOCK.md:116` at the next #39 revision.

---

## Sources

- **S1** UR, "e-Series cable options": https://www.universal-robots.com/articles/ur/e-series-cable-options/
- **S2** UR Marketplace, "High Flex Cable Extension Options": https://www.universal-robots.com/marketplace/products/01tP40000071NjRIAU
- **S3** UR, OEM Control Box specifications (SW10.14, PL): https://www.universal-robots.com/manuals/pl/HTML/SW10_14/Content/prod_oem_polyx/oempsx_cb_all_specs_root.htm
- **S4** UR5e technical specifications (SW10.14): https://www.universal-robots.com/manuals/EN/HTML/SW10_14/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_UR5e.htm
- **S5** FAIRINO product brochure 2026 (World Robot Conference download), text extracted with pdftotext; page numbers are PDF pages: https://www.worldrobotconference.com/profile/robot/download/2026/07/30/20260730200732000508_20260730200732A279.pdf
- **S6** FAIRINO Cobots manual (EN): https://fairino-doc-en.readthedocs.io/latest/CobotsManual/install_power_robot.html and …/robot_brief_introduction.html
- **S7** welectron, Fairino DC control box: https://www.welectron.com/fairino-dc-control-box_1
- **S8** welectron, Fairino FR5 IP54 black: https://www.welectron.com/Fairino-FR5-Cobot-IP54-Black-Robot-Arm
- **S9** Conductix-Wampfler, SR spring reels with 1 Gbps CAT6: https://www.conductix.ch/en/ch/data-transmission/reeling-systems/sr-spring-reels-400-gbps/sr-spring-reels-1-gbps-cat6-ethernet
- **S10** VAHLE spring-operated cable reels catalogue (search snippet: ≈ 120,000 cycles, IP55 slip-ring housing): https://www.vahle.com/fileadmin/cavok_upload/US%20Catalogs/vPOWER%2009a%20Spring-Operated%20Cable%20Reels.pdf
- **S11** igus chainflex CFBUS data sheets (TPE 10–12.5 × d, PVC 12.5 × d in e-chains): https://www.mouser.lt/datasheet/3/6018/1/EU_Data_sheet_chainflex_CFBUS.pdf
- **S12** igus, side-mounted e-chains: https://www.igus.eu/info/energy-chains-side-mounted
- **S13** igus, series E2C.26 / E2i.26: https://www.igus.eu/product/series-E2C-26
- **S14** TME, igus E2.26.038.200.0: https://www.tme.eu/dk/en/details/e2.26.038.200.0/cable-chains/igus/
- **S15** igus UK, series E2.38: https://www.igus.co.uk/product/series-E2-38
- **S16** igus, TH3 hygienic e-chain: https://www.igus.eu/info/hygienic-e-chain
- **S17** Conductix-Wampfler, C-rail cable trolley series 0230: https://www.conductix.ch/en/c-rail-cable-trolley-series-0230
- Repo: `sim/r10/claude/README_R10.md`, `hardware.py`, `mobile.py`, `R19_DOCK.md`, `R19_CART.md`; `posts/r09/reviewer.md`, `posts/r09/integrator.md`; `posts/r02/transport.md`; `sim/r02/transport/results/power_addendum.md`; `research/r19_power_budget.md`, `r19_arm_hand_cost.md`, `r19_system_cost.md`, `hand_options.md`; `DECISIONS.md`; GitHub #14, #36, #39.
