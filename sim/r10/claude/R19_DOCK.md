# R19 cart docking: datum rail, station stops, registration budget (GitHub #39, 2026-10-14)

**Question (#39).** #13 (`R19_TOLERANCE.md`) showed that the stored paths keep the 10 / 5 mm gates in the real world
only if the cart is registered to about x ±1.0 mm, y ±0.5 mm, yaw ±0.05°, tilt ±0.11°. The R10 design (a rubber
bumper on the cabinet doors, x from wheel encoders) misses this by a wide margin. This study designs the docking
hardware, budgets it, screens it in the sim and re-runs the #13 worst-corner replays with what it achieves.

**Labels:** [M] measured in the sim; [S] sourced (section 9); [T] a Taobao search-result listing price, seen read-only
on 2026-10-14 (not a quote); [E] estimate, with its basis; [D] a design value chosen here.

**Standard:** `ARM=ur5e_enc2_pgc PY=.15`, the adopted chains, the pot zone of #37 / #8 (`RACK=keyed`, spider rest
1.56 / 0.20, the pot-lift window). New files only; nothing existing was edited.

## 1. Answer first

**The mechanism.** The cart's front **rides on a floor datum rail** at the foot of the base cabinets.
- **Rail.** A 40 × 30 mm aluminium extrusion runs along the plinth line, 4.6 m long, from x −1.82 to +2.80. It replaces the R10 toe channel; the tether runs inside it. It is fixed with adhesive to the floor tiles and with 12 screws into the plinth. Three things are mounted on it:
  - a hardened 90° V-edge track (DualVee size 3 class);
  - a magnetic x scale;
  - 11 hardened V-blocks, one per station.
- **Cart.** The cart carries:
  - two V-groove wheels, 0.54 m apart, that carry its front on the V-track (y, yaw and front height);
  - two anti-lift keepers that run in the rail's side slot;
  - the scale read head;
  - one electric, self-locking index pin that drops into the station's V-block.

  The #14 fixed castors are lifted 5 mm off the floor; they now only catch the cart off the rail or in a fault. The #14 hub-motor brakes hold the cart.

**Why it is a rail-borne front, not stops plus a bumper.** Two findings drove the design.
1. **The adopted paths move the cart while the arm works [M].**
   - In the wok play, 457 of 463 stored segments move the cart and the arm together. The spatula, lid, spider and all the prep sets are similar.
   - Docking stops alone therefore cannot hold x, y or lean in motion. y, yaw and lean must be held all along the travel (rail), and x must be measured all along it (scale).
   - The stops then lock the cart where it dwells for forceful or seat work, and re-zero the scale.
2. **A low horizontal bumper cannot keep the lean toward the counter ≤ 0.1° [E].**
   - Lean is a roll of the cart on its tyres. A horizontal bumper at the rail's height (h ≈ 0.05 m) adds only k·h² with the tyres' lateral compliance in series: about +7 % roll stiffness.
   - What works is carrying the cart's front **vertically** on the stiff rail.
   - Load lean along every stored path, half-range ([M] moments × [E] stiffness):
     - castor cart: **0.115°**;
     - rail-borne front: **0.037°**, with a soft-to-stiff range of 0.015–0.075° against 0.046–0.230° for the castor cart.

**Does it meet the budget?**

| Axis | Target | Tier 1: hardware + commissioning shims | Tier 2: + commissioning pose map in the certification |
|---|---|---|---|
| x | ±1.0 mm | **±0.20 mm** | ±0.20 mm |
| y | ±0.5 mm | **±0.25 mm** | ±0.25 mm |
| z | ±0.5 mm | ±1.05 mm (**misses**: traded for lean, see 3.3) | **±0.20 mm** |
| yaw | ±0.05° | **±0.015°** | ±0.015° |
| tilt_x (lean toward the counter) | ±0.11° | **±0.065°** | ±0.03° |
| tilt_y | ±0.03° | **±0.02°** | ±0.02° |

Tier 1 meets every axis except z. Tier 2 meets every axis. The worst-corner replays with these boxes [M]:

| Path | #39 table, as designed | #39 table, docking-stop target | **Tier 1** | **Tier 2** |
|---|---|---|---|---|
| wok play / approaches | −1.1 / −2.5 | +2.35 / +2.36 | **+2.25** / +2.92 | +3.35 / +4.01 |
| spatula play | −4.4 | +2.87 | **+3.87** | +4.17 |
| lever play | −2.1 | +5.03 | **+6.25** | +7.46 |
| lid play (keyed rack + pot-lift window) | (−2.8, old rest) | +6.59 | **+8.15** | +8.95 |
| spider play | −9.7 (old rest) / −3.67 (rest 1.56 / 0.20) | +3.13 (new rest) | **+4.37** | +4.37 |
| all approaches except the wok's | | ≥ +10 | ≥ +10 | ≥ +10 |
| 22 hub edges (minimum: LEV_C, SPAT→LEV_C) | −2.7 | +2.17 | **+2.55** | +3.50 |

Every corner is positive.
- **Tier 1** beats the target box everywhere except the wok play: +2.25 against +2.35, because of its extra z. That binding pair is the wok seating into the cooker slot, a contact window that is force-guided in #26 anyway.
- **Rough cost:** about ¥2.0k with domestic generic parts, ¥11.2k with the branded reference parts (DualVee, RLS) [T/E].
- **Screens:**
  - Arm-path screen: 86 adopted paths, 103,469 states, **0 hits**. The closest arm part passes **668 mm** from any dock part [M].
  - The cart's own travel keeps ≥ 5.5 mm running clearance to every fixed part, castors included [M].

## 2. The design

### 2.1 Where the cart stands: stations of the adopted paths [M]

The cart travels along `R_carriage_x` (range −1.48…2.46), docked at y −0.21 and yaw 0 in every stored path. The `base_y` joint is unused. The stations are the hub nodes of `hub_py.15_ur5e_enc2_pgc`, plus the anchors where a set dwells for a seat, a closed chain or forceful work:

| Station | Cart x (m) | Uses |
|---|---|---|
| SPAT | −1.480 | H_SPAT / SPAT hub: spatula pick (also the x travel limit) |
| PRESS | −1.274 | prep: lever-cutter press (static, forceful) |
| LEVER | −0.740 | faucet lever play (a closed chain) |
| SINK | −0.680 | H_SINK, LEV_C, LEV_O hubs |
| WOK | +0.172 | H_WOK, WOK hubs: wok pick and set-down, fold / unfold |
| STIR | +0.550 | the parked stir cycle (`lib_stir_cycle`) |
| LID_POT | +0.886 | lid lift-off (96-state dwell) |
| POT | +1.093 | H_POT, SPIDER hubs: spider pick and rest |
| STGWOK | +1.210 | `stgwok` (static) |
| LID_RACK | +1.326 | lid into the keyed rack |
| PARK | +2.400 | parking / charging in the alcove |

**11 V-blocks** in total. The closest pair is 60 mm apart, against the V-block's ±5 mm capture: no ambiguity. Each block is clamped by two T-nuts, so it slides to a new x when the paths are re-planned (#42).

### 2.2 Fixed part, at the plinth line

Cross-section (world y-z; y = 0 is the cabinet door / plinth plane; the cart is on the left):

```
   y: -60    -50    -45      -37        -27  -16   -5  0 (cabinet front)
              |keeper|        pin          V wheel      |
  z 90 ======= chassis underside (cart) ===============|     cart frame z 0.09
              |arm  |      |housing|     |plate|(  )    |
  z 62        |     |      |  pin  |     |     |(W3)    |     V-wheel centre 62.3 (OD 45.8)
  z 46        |     |      |   o   |     |     | \/     |     pin nose retracted (46)
  z 43        |     |  head|       |          /\  apex 43.2
  z 42        |     | [==] |   .   |         /track\ (22.2 x 8.7, T3)
  z 33  scale>|     |  ####+=====[V-block]==+========+===|  rail top (extrusion 40 x 30 + 3 mm bed)
  z 20        | [T]>|> slot|                         angle|  keeper T-head in the aisle-face slot (1 mm all round)
  z  0  ======+=====+======+=============================+===  floor tiles (MS-polymer / VHB bed)
```

- **Rail body.**
  - 6063-T5 extrusion, 40 (y) × 30 (z) mm, 8 mm slots, in 2 × 2.31 m lengths with a dowelled joint plate.
  - y −45…−5 mm: 5 mm in front of the plinth / door plane; the doors open above it.
  - z 0…33 mm, including a ≤ 3 mm shim / adhesive bed.
  - x −1.82…+2.80: the cart's x travel ±0.27 m truck offset + 25 mm over-travel.
  - It occupies the R10 toe-channel envelope (y −40…−10, z 0…30) and carries the tether in its bore.
- **Fixing (no damage beyond screws and adhesive).**
  - An MS-polymer bead and VHB tape on the floor tiles.
  - Six 30 × 30 × 3 angles from the rail's cabinet-face slot into the plinth / kickboard, 2 screws each (12 screws), under the cabinet run (x −1.65…+1.35 every 0.6 m). The alcove part is bonded only.
  - The rail is **anchored** (no slip) at the centre angle (x 0.15) and free to slide thermally elsewhere.
- **V-track.**
  - DualVee single-edge track size 3 class: 22.23 wide, 8.71 high, stainless AISI 420 hardened to HRC 40 [S]. A domestic hardened 90° V guide is the low-cost option.
  - It is screwed into the top slot on the cabinet half of the extrusion (centre y −16 mm). Virtual apex at z 43.2 mm.
  - It needs no precision mounting surface [S]. It is aligned by laser / taut line to ±0.2 mm and shimmed (section 3).
- **Magnetic scale.**
  - 2 mm-pole self-adhesive tape (RLS LM10 class [S], or a domestic 磁栅尺), on the upper land of the extrusion's aisle face (z 22–32 mm), under a stainless cover.
  - Accuracy grade ±40 µm (±20 / ±10 µm grades exist) [S].
  - Incremental with reference marks, or absolute (RS485 / SSI heads are listed at ¥365–400 [T]).
- **Station V-blocks.**
  - Hardened (440C or 45# HRC 45), 30 (x) × 16 (y) × 8 mm, let flush into the aisle half of the top (y −45…−29).
  - A 90° V across the rail (groove along y), 10 mm mouth, 5 mm deep, with a slotted apex so crumbs drop through.
- **End buffers:** rubber, 10 mm, at both ends (25 mm beyond the trucks at the soft x limits [M]).

### 2.3 On the cart (cart frame, docked at y −0.21)

- **Two V-wheel trucks** at cart x ±0.27 (0.54 m apart).
  - They sit inside the chassis outline and clear of the castor envelopes (|x| 0.137…0.304).
  - Each truck: a DualVee W3 wheel [S] (OD 45.8, width 15.9; working radial 5,900 N, axial 1,701 N), axis along y, rolling on the V-track. It sits on an eccentric bushing used at commissioning to set the cart level and the front height. A 6 mm steel plate (z 50–90 mm) hangs it from the chassis front cross-member.
  - Front load: **≥ 54 N per truck and ≥ 239 N for the pair** in every stored state [M moments, D masses]. The pair carries at most about 0.47 kN (CoP y range × total weight, [M/D]), 8 % of one wheel's rating.
  - The wheels seal against food, slurry and water [S]. Felt wipers clean the track.
- **Front castors (#14 fixed, x-aligned):** set 5 mm above the floor on spacers. They carry the cart off the rail, and catch it if a wheel ever leaves the track.
- **Two anti-lift keepers** at cart x ±0.11. Each is a 4 mm steel arm down the rail's aisle face to a UHMW-PE T-head inside the aisle-face slot, with 1 mm clearance all round. They never touch in normal running.
  - They engage only if a V wheel lifts or the cart is pulled away from the rail: protective stops, a person pushing the cart, the pin pushing beyond the front load.
  - With a gravity-seated V, a truck can take a lateral load of about 1.2 × its vertical load (90° V, μ 0.1 [E]) before climbing. That is ≥ 65 N at the lightest truck, against ≤ 46 N total arm reaction (R19_CART stir). Beyond that, the keepers limit any climb to 1 mm.
- **Index pin unit** at cart x 0, at the front underside (y −52…−22).
  - A 24 V self-locking mini linear actuator (20 mm stroke, ≥ 150 N; these list at ¥30–205 [T]) drives a hardened 12 mm ball-nosed pin through a disc spring.
  - Retracted: the nose is 13 mm above the rail top and 4.3 mm above the V-track top.
  - Seated: the nose touches both 45° flanks of the V (centre 8.5 mm above the apex) and travels 15.5 mm.
- **Read head:** next to the pin unit (x 40–80 mm), ride height **0.7 mm**. With the ±0.25 mm y budget the gap stays 0.45–0.95 mm (LM10 allows ≤ 1.0 mm [S]).
- **Inclinometer** (SCL3300 class [S]) on the deck: used to commission the level and as a live lean monitor.
- **The R10 door bumper (`R_dock_bumper`) is retired.** It is not needed, and a bumper on the doors would fight the rail. Keep it, if at all, only as a soft guard 10 mm off the doors. It stays in the sim model, which is unchanged.

### 2.4 How the cart engages a station and is held

1. It drives along the rail on the scale, which gives absolute x to about ±0.2 mm, and stops at the station x ± 1 mm.
2. The hub motors go to zero torque with the brakes released. The pin drives down at a force limit of **50 N** [D]. That is ≤ ½ of the 239 N minimum front load, so the V wheels stay seated.
3. The nose lands within the V's ±5 mm capture. The 45° flank pulls the cart along x with up to ~50 N; rolling needs ~10–20 N.
4. **Seat check.** The actuator stroke must be at the expected depth ±0.2 mm, and the scale must read the commissioned station x ±0.1 mm. Otherwise the pin retracts and re-seats once, then raises an alarm (debris).
5. **Hold:**
   - the lead screw self-locks;
   - the hub brakes engage (#14) and the servo holds;
   - y, z and yaw stay on the V wheels.
   x loads up to ~190 N (front load − preload, on the 45° flank) are carried without lift. Above that the keepers clamp the front at ≤ 1 mm lift. The arm's process reactions are ≤ 46 N [R19_CART].
6. The pin rises at the first cart move. During coordinated cart + arm motion x comes from the scale, which is re-zeroed at each docking.

- **Cycle:** about 2.5 s per dock + undock [E]. The mini actuators run about 12 mm/s [T].
- **When to dock:** at stations where the cart dwells for forceful or seat work (lever, press, stir, lid seats, wok set-down, stgwok) and for parking; about 10–20 times per meal, **+0.5–1 min per meal** [E]. In-motion sets do not need the pin.
- **Power loss:** the pin, if down, stays down; the keepers hold y and z; the hub brakes (#14) hold x.

### 2.5 The user's L-shaped kitchen

- **One rail per straight leg that the cart works along.** The sim (and the current layout) folds the work into one straight run, x −1.8…2.8, so one rail suffices. A second leg needs its own rail. The cart cannot turn the corner on it.
- **The plinth / kickboard is not visible in the photos** (`inputs/user_kitchen`). Measure:
  - the toe-recess depth;
  - the door bottom height;
  - the floor flatness along the leg (2 m straightedge).
- If the toe recess is ≥ 45 mm deep, the rail sits inside it and nothing sticks out past the door plane. Otherwise it is a 33–43 mm high step 45 mm in front of the doors, where the R10 toe channel already was.

## 3. Repeatability per part and the budget

### 3.1 Sources and estimates per part

| Part | Repeatability / error | Label and basis |
|---|---|---|
| Ball-nose pin in a hardened 90° V (kinematic contact, preloaded) | x ±0.02 mm | [S] kinematic couplings repeat to sub-micron when clean and preloaded (Slocum 2010). [E] ±0.02 mm allows for a kitchen: finish, debris (slotted V + seat check), cart compliance. |
| Pin-in-bushing alternative | ±(clearance/2) = ±0.01–0.03 mm with H7/g6, plus taper wear | [E] Commercial AGV pin docks are about ±3 mm overall (guide + pin, patent example) [S]. MiR VL-marker docking is ±3 mm / ±0.5° (#13 sources) [S]. |
| Magnetic scale (absolute x in motion) | ±40 µm grade over the length; hysteresis < 3 µm at 0.3 mm ride; IP68-class dirt immunity | [S] RLS LM10 |
| Rail thermal growth vs the building | ±0.16 mm at 2.4 m from the anchor (Al 23e-6/K vs about 10e-6/K, ±5 K) | [E]. A steel extrusion or a floating steel tape halves it. |
| V-wheel on V-track (y, yaw, front z) | y ±0.02 mm (bearing play / runout); track straightness after alignment ±0.2 mm (global) / ±0.05 mm (local over 0.54 m) | [S] the DualVee track needs no precision mounting surface. [E] alignment by laser / taut line. |
| Lean, rail-borne front (load) | 0.037° half-range (0.044° from a mid-posture zero); 0.015–0.075° over the stiffness range | [M] moments × [E] tyre 2e5 N/m (1e5–5e5), truck 5e6 N/m (2e6–2e7), section 3.2 |
| Lean, castor cart (as designed / #14, for comparison) | 0.115° half-range (0.046–0.230°) | same method |
| Low horizontal bumper on a datum rail (the #13 idea) | +7 % roll stiffness at h = 0.05 m; even a door bumper at 0.30 m adds only +35 % with door / hinge compliance | [E] k_bumper 1e7 N/m, tyre lateral stiffness 4 × 1.5e5 N/m, door 1e5 N/m |
| Floor under the rear wheels | ±1 mm long-wave (2 mm under a 2 m straightedge); tile joint lippage ≤ 0.5 mm | [S] GB 50209-2010 (from a search summary; the standard text was not read) |
| Station tilt / level measurement | ±0.015° | [S] SCL3300: 0.001°/√Hz noise, offset ±0.005°/K. [E] ±3 K, relative to the reference station. |

### 3.2 Load lean [M × E] (`r19dock_budget.py PART=lean`)

**Model:**
- A rigid cart on four vertical springs (small rotations).
- Moving masses: the sim arm + gripper (23.3 kg) plus the payload at the TCP: wok 2.95, spider 0.75, lid 0.8, spatula 0.3, stir 0.3, prep 1.0 kg.
- The cart from the R19_CART BOM: 51.3 kg at (0.001, −0.102, 0.353).
- Evaluated at every stored state of the adopted plays, the stir cycle and the prep sets: 8,444 states.

| Support | tilt_x half-range | max dev. from the median | tilt_y half-range | z at the J1 base | min support |
|---|---|---|---|---|---|
| **Rail-borne front** (trucks 5e6 at y_loc +0.194, tyres 2e5 at −0.22) | **0.037°** | 0.044° | 0.005° | ±0.06 mm | truck 54 N (pair ≥ 239 N), tyre 144 N |
| Castor cart (castors 2e5 at +0.11, tyres 2e5) | 0.115° | 0.138° | 0.105° | ±0.28 mm | castor 121 N, tyre 44 N |
| Soft (tyre 1e5, truck 2e6) / stiff (tyre 5e5, truck 2e7): rail | 0.075° / 0.015° | 0.090° / 0.018° | | | |
| Soft / stiff: castors | 0.230° / 0.046° | 0.277° / 0.055° | | | |

- **Per path (rail, full width):** wok 0.015°, spatula 0.031°, lid 0.023°, spider 0.026°, carrot prep 0.036° (the widest), stir 0.007°.
- **The static lean** (about 0.14° toward the aisle at rest, because the rear tyres compress) is levelled out once at commissioning with the eccentric bushings.
- **Side effects [E]:**
  - The rail moves the front support line 84 mm forward (castor line y_loc +0.11 → +0.194). That adds to the forward tip margin.
  - It takes y and yaw off the drive tyres, which then need x traction only. This removes the R19_CART side-slip / yaw-couple problem.
  - It roughly triples the roll stiffness: rocking frequency about ×1.8.
  - R19_CART's `mobile.dock_stability` must be updated (section 7, hooks).

### 3.3 Budget vs target (`r19dock_budget.py PART=budget` → `results/r19/dock/budget.json`)

Half-ranges, combined RSS per axis, rounded up.

| Axis | Term | Tier 1 | Tier 2 | Label |
|---|---|---|---|---|
| x | station pin in V-block | 0.02 mm | 0.02 | [E / S] |
| x | magnetic scale (in-set travel, re-zeroed at each dock) | 0.04 | 0.04 | [S] |
| x | tape / head / head-to-arm-base calibration | 0.03 | 0.03 | [E] |
| x | rail thermal growth | 0.16 | 0.16 | [E] |
| **x** | **RSS → box** | **0.17 → 0.20** | 0.20 | target 1.0 |
| y | V-track straightness after alignment | 0.20 | 0.20 | [E] |
| y | wheel play / runout; rail deflection; creep | 0.02; 0.05; 0.10 | same | [E] |
| **y** | **RSS → box** | **0.23 → 0.25** | 0.25 | target 0.5 |
| z | rail level at the trucks | 0.10 | 0.10 | [E] |
| z | rear floor: Tier 1 the rail follows it; Tier 2 mapped | 1.0 | 0.15 | [S / E] |
| z | load (tyre compression ×1.1 dynamic) | 0.07 | 0.02 | [M / E] |
| **z** | **RSS → box** | **1.01 → 1.05** | **0.20** | target 0.5 |
| yaw | track local straightness over 0.54 m; wheel runout | 0.0106°; 0.0042° | same | [E] |
| **yaw** | **RSS → box** | **0.015°** | 0.015° | target 0.05 |
| tilt_x | load lean (max dev. ×1.1 dynamic) | 0.049° | 0.015° | [M / E] |
| tilt_x | rear floor: short-wave residual (tile lippage) / mapped | 0.035° | 0.015° | [S / E] |
| tilt_x | measurement; tyre wear | 0.015°; 0.007° | same | [S / E] |
| **tilt_x** | **RSS → box** | **0.062 → 0.065°** | **0.03°** | target 0.11 |
| tilt_y | rail level between the trucks; load pitch; measurement | 0.011; 0.006; 0.015° | 0.011; 0.002; 0.015° | |
| **tilt_y** | **RSS → box** | **0.02°** | 0.02° | target 0.03 |

**The z trade (Tier 1).** The rear drive wheels roll on the tiles: ±1 mm long-wave [S]. Two choices:
- Shim the rail **level**: the cart then leans ±0.14° with the floor and z is ±0.28 mm. That breaks the tilt target.
- Shim the rail to **follow** the rear floor (chosen): the cart stays level to the tile-lippage residual (0.035°), but rides up and down ±1 mm.

The second is cheaper in the tolerances: about 28 mm of clearance per degree of lean against 1 mm per mm of z. The replays confirm it (section 5).

**Tier 2** needs the commissioning map (z, tilt_x, tilt_y against cart x, plus the measured lean stiffness) to be used when the stored paths are certified. That is a checker / certification hook, not hardware (section 7).

## 4. Screens [M]

### 4.1 Arm paths vs the dock hardware (`r19dock_screen.py PART=arm`, as `r19prep5_screen.py`)

**Method:**
- Every adopted stored path: cooking chains + approaches, 22 hub edges, 6 cup chains, the stir cycle, the 10 certified prep sets of r19prep5, plus fold / unfold / stgwok.
- Replayed at ≤ 4 mm with the pot-zone layer and the dock parts in its own scene.
- Only the pairs (arm / held geom) × (dock part) are measured, exactly, with the checker's gates: 10 mm arm, 5 mm gripper / held, 10 mm arm vs a cart part.

| Kind | Paths | States | Min gate (mm) | Closest pair |
|---|---|---|---|---|
| prep | 40 | 31,000 | **668.1** | wrist-1 hull `R_geom_enc2_w1_1` / left truck plate (carrot pick approach) |
| cup chains | 6 | 10,403 | 691.8 | held-cup sphere / right truck plate |
| plays | 6 | 18,437 | 735.9 | upper-arm hull / right truck plate (wok) |
| approaches | 11 | 741 | 741.8 | |
| hub edges | 22 | 34,460 | 757.7 | |
| stir | 1 | 8,428 | 843.3 | spatula blade / truck plate |
| **Total** | **86** | **103,469** | **0 hit states**, 0 errors | |

The same holds with the pin down (`screen_dock_pindown.json`): identical minima. **The hardware does not intrude on any arm path.** It sits at z ≤ 90 mm, more than 0.6 m below everything the arm sweeps.

### 4.2 The cart's own travel (`r19dock_screen.py PART=travel`)

**Method:**
- The cart at every 10 mm of its x travel (−1.48…2.46) and at y −0.21 ± 0.5 mm: 1,185 states.
- Every cart geom (chassis, drive wheels, castors and their spindles, bumper, mast, beam and the new parts) against every fixed dock part, and every new cart part against the kitchen.
- The checker's exact distance bound.

| Check | Result | Requirement |
|---|---|---|
| Cart parts vs fixed dock parts, travelling (pin up) | **min 5.5 mm** (keeper arm vs the PARK V-block edge) | ≥ 5 mm running clearance [D] |
| Original castors (sim envelope) vs rail / scale | 9.0 mm; castor spindles 9.8 mm; chassis 33.5 mm; drive wheels 339 mm | ≥ 5 mm |
| New cart parts vs the kitchen | 7.6 mm (V wheel vs the left cabinet end at x −1.48) | ≥ 5 mm |
| Docked at all 11 stations (pin down) | 3.2 mm (seated nose vs the scale tape edge) | ≥ 1 mm, static |
| Travel ends | trucks 25 mm from the end buffers at both soft limits | > 0 |
| Declared: V wheel on V track; seated pin in its V-block | contact by design | — |
| Declared running gaps: read head over the tape; keeper T-head inside the slot / vs the tape | 0.2 mm at y +0.5 mm (0.7 nominal); slot not modelled (1 mm by design); 2.5 mm | head > 0; keeper > its 1 mm clearance |
| R10 toe channel (`floor_cable_guide`) | superseded: inside the rail | — |

**Two design changes came out of this screen:**
- The read-head ride height went from 0.5 to 0.7 mm. At 0.5 mm it touched the tape at y +0.5 mm.
- The retracted pin was raised from 40 to 46 mm. At 40 mm it was 4.3 mm from the V-track, under the 5 mm rule.

The first screen also showed that a gravity-seated V alone can be lifted: the lightest truck carries 54 N. Hence the keepers and the 50 N pin force limit.

## 5. Tolerance replays (#13 tools, unchanged, through `r19dock_tol.py`)

**Method:**
- `r19tol_replay.py` scenarios with the two new boxes, worst sign corner of all 2⁶ corners, exact branch and bound.
  - Tier 1 (`dock_rail`): x 0.20 / y 0.25 / z 1.05 mm, yaw 0.015°, tilt_x 0.065°, tilt_y 0.02°.
  - Tier 2 (`dock_rail_map`): the same with z 0.20 mm and tilt_x 0.03°.
- The #13 / #37 nominal caches were found by hash and reused read-only.
- The lid play was split into 6 state chunks per box, each under 4 min, and merged by minimum.
- **Check:** the wrapper reproduces the stored #13 `dock_stops` corner of the wok play, **+2.355 mm**, both whole and as 4 merged chunks.

Min gate reserve at the worst corner, mm (the gap is that + 10 robot / + 5 gripper and held):

| Path | As designed | Target box (`dock_stops`) | **Tier 1** | **Tier 2** | Binding pair (Tier 1) |
|---|---|---|---|---|---|
| wok play | −1.07 | +2.35 | **+2.25** | +3.35 | wok bottom / cooker at the seat; corner z −1.05, tilt_x −0.065 |
| wok approaches | −2.46 | +2.36 | **+2.92** | +4.01 | upper arm / plate |
| spatula play | −4.44 | +2.87 | **+3.87** | +4.17 | blade / wok at stroke start (Tier 2: blade / tomato) |
| lever play | −2.06 | +5.03 | **+6.25** | +7.46 | lever bar / hub |
| lid play (keyed rack, pot-lift window) | — | +6.59 | **+8.15** | +8.95 | lid rim / hood |
| spider play (rest 1.56 / 0.20) | −3.67 | +3.13 | **+4.37** | +4.37 | spider bowl / pot ear (x-bound) |
| lever, spatula, lid, spider approaches | | ≥ +10 | ≥ +10 | ≥ +10 | |
| LEV_C → H_SINK / H_SPAT / H_WOK, SPAT → LEV_C | −2.69 | +2.17 | **+2.55** | +3.50 | wrist 1 / closed upper door |
| SPIDER → H_POT / H_WOK | −0.72 | +4.43 | **+5.69** | +6.45 | upper arm / hood |
| the other 16 edges | ≥ +6.49 | ≥ +10 | ≥ +10 | ≥ +10 | |

- **Contact:** every path keeps ≥ 7.2 mm real gap at the corner.
- **Not replayed here:** the prep sets, cups and stir. The #13 tools have no prep-scene adapter (open, section 7).

## 6. BOM with rough prices (`results/r19/dock/bom.json`)

Low is domestic generic parts; high is the branded reference parts. No purchase, no vendor contact.

| Item | Qty | Unit ¥ | Line ¥ | Label |
|---|---|---|---|---|
| Aluminium extrusion 40 × 30, 6063-T5, slot 8, + joint plates | 4.62 m | 30–60 | 139–277 | [E] |
| Hardened V-edge track (domestic 90° V guide … DualVee T3 stainless) | 4.62 m | 80–700 | 370–3,234 | [E] |
| V-groove wheels, sealed, + eccentric bushings (domestic machine V rollers … DualVee W3) | 2 | 30–400 | 60–800 | [T] ¥30–100 domestic; [E] DualVee |
| Truck plates, 6 mm steel, laser-cut + M8 | 2 | 40–80 | 80–160 | [E] |
| Anti-lift keepers (steel arm + UHMW-PE T-head) | 2 | 30–80 | 60–160 | [E] |
| Magnetic scale: 4.6 m tape + read head (incremental with reference, or absolute RS485 / SSI) | 1 set | 400–4,000 | 400–4,000 | [T] heads ¥20–750, absolute ¥365–400; tape [E] ¥50–150/m; LM10 [E] |
| Hardened V-block inserts, 90° V, + T-nuts | 11 | 30–80 | 330–880 | [E] machined |
| Index pin actuator: 24 V mini, 20 mm, ≥ 150 N, self-locking, limit switches / encoder | 1 | 30–205 | 30–205 | [T] |
| 12 mm ball-nosed pin, bronze bush, disc springs, housing | 1 set | 80–200 | 80–200 | [E] |
| Plinth angles (6) + 12 screws, MS-polymer, VHB, shim set | 1 set | 100–250 | 100–250 | [E] |
| Rubber end buffers | 2 | 10–30 | 20–60 | [E] |
| Inclinometer (SCL3300 class) + 0.02 mm/m level + laser line (commissioning; the inclinometer stays) | 1 set | 300–900 | 300–900 | [E] |
| Castor spacers (5 mm raise) | 2 | 0–50 | 0–100 | [E] |
| **Total** | | | **¥2.0k–11.2k** | |

Not included: the #14 hub-motor holding brakes (R19_CART: about ¥4k for two), labour, the kitchen survey.

**Generic part types:**
- precision dowel pins / ball-nosed index pin;
- hardened V-blocks;
- cam-follower-type V-groove guide wheels;
- an aluminium extrusion datum rail;
- a self-locking electric latch (the pin);
- the hub-motor brake (#14).

## 7. Controller lanes, re-runs after #42, hooks

**Every command run here took < 5 min.**

| Run | Time |
|---|---|
| travel | 2–3.5 min |
| arm | 26 s (112 s before the WMI shim) |
| lean / budget / bom / report | ≤ 1 min each |
| tol main | 118 s |
| tol pot | 270 s (the lid play hit its deadline there) |
| lid chunks | 222 s |

No result is pending. The lane below is for after the #42 re-plan, when every arm path changes. It is sequential and takes about 15 min in total. Every command keeps its own deadline.

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
export PYTHONPATH="C:/Users/admin/AppData/Local/Temp/claude/C--Users-admin-Documents-YJGames/86718cbb-b411-47ad-a94e-23d66b0c6309/scratchpad/nowmi"   # WMI shim (2026-10-14)
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
L="ARM=ur5e_enc2_pgc PY=.15"   # <- the post-#42 arm option
D=results/r19/dock; mkdir -p $D/logs
# 0. update kitchen19dock.STATIONS to the re-planned hub / anchor cart x (the V-blocks slide in the T-slot)
# 1. arm-path screen (expected to pass trivially: 668 mm today) and the cart travel / docked screen
$PY r19dock_screen.py PART=arm PIN=up KINDS=prep,play,app,edge,other,stir WORKERS=16 TLIM=270 $L > $D/logs/screen_arm.txt 2>&1
$PY r19dock_screen.py PART=travel STEP=.01 $L > $D/logs/screen_travel.txt 2>&1
# 2. load lean along the new paths -> budget boxes
$PY r19dock_budget.py PART=lean $L > $D/logs/lean.txt 2>&1
$PY r19dock_budget.py PART=lean K_TYRE=1e5 K_TRUCK=2e6 K_CASTOR=1e5 TAG=soft $L > $D/logs/lean_soft.txt 2>&1
$PY r19dock_budget.py PART=lean K_TYRE=5e5 K_TRUCK=2e7 K_CASTOR=5e5 TAG=stiff $L > $D/logs/lean_stiff.txt 2>&1
$PY r19dock_budget.py PART=budget > $D/logs/budget.txt 2>&1
# 3. worst-corner replays (needs the new nominal caches: the first run of each scene computes them, ~1 min per long play)
E=$(ls results/r19/hub_py.15_ur5e_enc2_pgc/edge_*.json | sed 's#.*/edge_#edge:#; s#\.json##' | paste -sd, -)   # <- the re-planned hub folder
$PY r19dock_tol.py SCENES=play:wok,app:wok:0,app:wok:1,play:spatula,app:spatula:0,play:lever,app:lever:0,app:lever:1,$E PARTS=scen-dock_rail,scen-dock_rail_map TOLTAG=main $L WORKERS=20 DEADLINE=280 > $D/logs/tol_main.txt 2>&1
POT="POT=1 RACK=keyed POTWIN=1 SPIDER=results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json SPX=1.56 SPY=.20"   # <- the re-planned spider / lid chains (LID=...)
$PY r19dock_tol.py $POT SCENES=app:lid19:0,app:lid19:1,play:spider19,app:spider19:0,app:spider19:1 PARTS=scen-dock_rail,scen-dock_rail_map TOLTAG=pot $L WORKERS=10 DEADLINE=280 > $D/logs/tol_pot.txt 2>&1
P=$(for b in dock_rail dock_rail_map; do for k in 0 1 2 3 4 5; do printf "scen-$b+c${k}of6,"; done; done | sed 's/,$//')
$PY r19dock_tol.py $POT SCENES=play:lid19 PARTS=$P TOLTAG=pot $L WORKERS=12 DEADLINE=280 > $D/logs/tol_pot_lid.txt 2>&1
$PY r19dock_tol.py $POT TOLTAG=pot $L MERGE=1 >> $D/logs/tol_pot_lid.txt 2>&1
$PY r19dock_budget.py PART=bom > $D/logs/bom.txt 2>&1; $PY r19dock_budget.py PART=report > $D/logs/report.txt 2>&1
```

Move the old `tol/main` and `tol/pot` result files aside before re-running. If a lid chunk hits its deadline, raise the chunk count, e.g. `c<k>of10`.

**What must be re-run after the #42 re-plan:**
- **Must:**
  - the arm-path screen (new paths);
  - lean → budget (the moments come from the paths);
  - the tolerance replays (new chains and edges);
  - the station list → PART=travel with the pin down at the new stations.
- **Not needed:** PART=travel with the pin up. It depends only on the cart geometry (#14) and the rail.
- **The hardware design itself does not depend on #42.**

**Hooks in shared files: none was needed for this study. Optional ones:**
1. `scene.py build()`: to put the dock parts into every certification scene, insert one line between `  import kitchen14;kitchen14.add(tree,cfg)` (line 333) and ` import arms` (line 334), with one-space indent:

   ` import kitchen19dock;kitchen19dock.add(tree,cfg)  # R19 #39 dock rail; no-op unless cfg['r19dock']`

   This is not needed today: the parts are 668 mm from any path.
2. **Tier 2** needs the certification to apply a measured pose map per cart x (z, tilt_x, tilt_y) to the robot geoms. That is the same operation as `r19tol_core.Ev.pose(cart=...)`, but per state. It is **not** a one-line change. It belongs in the checker / exporter work (#42 re-certification) if Tier 2 is wanted.
3. `mobile.py` `dock_stability` / R19_CART support model, to update with #14:
   - front support line y_loc +0.194 on the rail, not the castor line +0.11;
   - lateral and yaw reactions to the rail, not tyre friction;
   - no bumper on the doors.

   This is several lines; it is described here, not made.

**Open:**
- **Measure in the user's kitchen:** toe recess, door bottom height, floor flatness along the leg, the plinth material (screws or adhesive only), and the PU tyre vertical / lateral stiffness. The lean range is 0.015–0.075° over the tyre-stiffness uncertainty.
- **Prep sets, cups and stir corner replays:** need a prep-scene adapter for `r19tol_core`. The prep sets move the cart near the sink with small loads; their lean width is ≤ 0.036° [M × E].
- The keeper slot and the V-block slot are not modelled. The rail is a solid box in the sim, and both are declared running gaps / contacts.
- **Fixture keying** (cooker locator frame, keyed lever clip, guarded plate stand, rack / pad lead-ins ≥ the budget) stays as specified in #13 §4–5 and #8. With this rail the kitchen survey is referenced to the rail, which is now the world datum for y and z.

## 8. Files (all new)

- `kitchen19dock.py`: the layer. A no-op without `cfg['r19dock']`; checked byte-identical against a plain build.
  - `world_parts()`, `cart_parts(pin)`, `STATIONS`, the declared contacts / running gaps, `mesh()`, `summary()`.
- `r19dock_screen.py`: `PART=travel` (cart travel / docked clearances) and `PART=arm` (arm paths, through `r19prep5_screen`).
- `r19dock_budget.py`: `PART=lean` (load lean), `budget` (two tiers), `bom`, `report`.
- `r19dock_tol.py`: the #13 replays with the dock boxes. It adds `POT=1` for the pot zone, read-only cache reuse, state chunking (`+c<k>of<n>`) and `MERGE=1`.
- `results/r19/dock/`:
  - `screen_travel.json`, `screen_dock.json`, `screen_dock_pindown.json`;
  - `lean.json`, `lean_soft.json`, `lean_stiff.json`;
  - `budget.json`, `bom.json`, `summary.json`;
  - `tol/main/` (wok, spatula, lever + approaches + 22 edges), `tol/pot/` (lid19 chunks + merged, spider19, approaches), `tol/check/` (the +2.355 reproduction);
  - `logs/`.

## 9. Sources

- Slocum, [Kinematic couplings: a review of design principles and applications](https://dspace.mit.edu/handle/1721.1/69013), Int. J. Machine Tools & Manufacture 2010: exactly constrained couplings, sub-micron repeatability, Hertz-contact stiffness.
- Bishop-Wisecarver, [DualVee catalogue](https://crm.bwc.com/hubfs/Catalogs/DualVee-Bishop-Wisecarver-Catalog.pdf) (rev. 03/2025):
  - W3: OD 45.80, width 15.88, working radial 5,900 N, axial 1,701 N;
  - T3 track: 22.23 × 8.71, AISI 420 hardened to HRC 40;
  - "no need for precision ground or machined surfaces";
  - seals against dirt, food, slurry and water.
- RLS, [LM10 linear magnetic encoder](https://www.rls.si/en/lm10-linear-magnetic-encoder-system): accuracy ±10 / ±20 / ±40 µm, ride height up to 1.0 mm, hysteresis < 3 µm at 0.3 mm, dirt immunity to IP68.
- Murata, [SCL3300-D01 datasheet](https://www.murata.com/~/media/webrenewal/products/sensor/pdf/datasheet/datasheet_scl3300-d01.pdf): 0.001°/√Hz noise, offset temperature error ±0.005°/°C.
- GB 50209-2010, building floor acceptance: tile surface flatness 2 mm (2 m straightedge), joint height difference 0.5 mm. From search summaries; the text was not read.
- AGV docking with tapered positioning pins and guide surfaces, ±3 mm: [US patent 12242275](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12242275) (search summary). Precision indexing plungers with tapered pins: [norelem](https://norelem.co.uk/en/Product-overview/Flexible-standard-component-system/03000/Indexing-plungers/Indexing-plungers---Precision-with-tapered-pin/Precision-indexing-plungers-with-tapered-indexing-pin-Form-A-standard/p/agid.2709).
- Taobao search result pages, read-only on 2026-10-14 (no login, no item pages): 磁栅尺 读数头, V型导轮 V型导轨, 微型电动推杆 24V. Listing prices only, not quotes.
- Project: `R19_TOLERANCE.md` (#13 budget, boxes, method), `R19_CART.md` (#14 BOM masses, tyre stiffness basis, arm reactions), `R19_POTZONE.md` (#37 / #8 windows and spider rest), `R19_PREP_T2L.md` (screen method).

## 10. The adopted m2 mount (#42): re-run set-up and smoke (2026-10-14)

**Inputs.**
- Options: `ARM=ur5e_enc2_pgc_m2` and `ARM=fr5_j6_pgc_m2`.
- Files: the adopted ones of R19_MOUNT.md §4 and R19_M2FIX.md, the m2 hubs (`results/r19/fr5/hub_py.15_<arm>/`), and the stir libraries of R19_M2JOIN.md (#41 `short01_u06_j8000`, join). All of them are `ok` with an `ok` ≤ 4 mm re-check.
- UR5e: 6 chains + 13 prep sets, with **20 of 22 hub edges ok**; `SPAT__H_SPAT` and `SPAT__LEV_C` are not ok and are skipped.
- FR5: 6 chains + 12 prep sets, with 22 of 22 edges ok.
- New wrappers only (`r19dock_m2.py`, `r19dock_m2_screen.py`, `r19dock_m2_tol.py`). The r19dock / r19*_m2* / r19m2* files are unchanged.

### 10.1 Station lists (`r19dock_m2.py stations` → `results/r19/dock/m2/<arm>/stations.json`)

**Rule.** One V-groove for each of:
- every action endpoint of the m2 hub graph;
- every anchor where the cart is parked for a seat, a closed chain, or forceful or static work;
- parking.

Grooves closer than 35 mm share one **twin-V insert**, machined at their exact spacing; the 10 mm V mouths leave a land. A transit hub gets a groove only if it is ≥ 35 mm from every other groove; otherwise it is scale-only. **The two arms need different stations** [M]. The inserts slide in the T-slot.

| Station | UR5e m2 x | FR5 m2 x | Base design x |
|---|---|---|---|
| H_SPAT (hub) | = SPAT | −1.4800 | — |
| SPAT (spatula pick) | −1.4800 | **−1.3429** | −1.480 |
| PRESS | −1.2742 | −1.2854 | −1.274 |
| H_SINK (hub) | −0.6800 | −0.6800 | −0.680 |
| LEVER (lever play) | **−0.6056** | −0.6056 | −0.740 |
| LEV (LEV_C / LEV_O endpoint) | −0.5456 | −0.5456 | (at −0.680, in SINK) |
| WOK_SET (wok set-down) | = WOK | **+0.0986** | = WOK |
| WOK (wok pick) | +0.1720 (with FOLD, H_WOK) | +0.1453 **twin-V with FOLD +0.1720** | +0.172 |
| STIR | +0.5500 | **+0.4500** | +0.550 |
| LID_POT (lid lift-off) | +0.8863 | +0.8863 **twin-V with SPIDER +0.8654** | +0.886 |
| SPIDER (pick / rest) | **+1.0776** (H_POT +1.093 is 15 mm away → H_POT scale-only) | +0.8654 | +1.093 (= POT) |
| H_POT (hub) | scale-only | +1.0930 | (= POT) |
| STGWOK | +1.2100 | — (no FR5 m2 stgwok) | +1.210 |
| LID_RACK (drop into the rack: cart parked for the last 9 states) | +1.3256 | **+1.4205** | +1.326 |
| PARK | +2.4000 | +2.4000 | +2.400 |
| **Total** | **12 grooves / 12 inserts** | **15 grooves / 13 inserts (2 twin-V)** | 11 |

### 10.2 Smoke results [M] (each run < 5 min, ≤ 8 workers, WMI shim)

| Check | UR5e m2 | FR5 m2 |
|---|---|---|
| **Arm-path screen**, complete m2 set (chains + approaches, ok edges, prep + approaches, #41 stir, stir join) | 80 paths, 82,448 states, **0 hits**, min gate **680.7 mm** (wrist 1 / left truck plate, carrot approach) | 79 paths, 89,677 states, **0 hits**, min **715.3 mm** (forearm / pin housing, SPIDER→H_WOK) |
| **Travel**, 20 mm step: pin up / docked at every m2 station | ≥ 5.5 mm / ≥ 3.17 mm: **ok** | ≥ 5.5 mm / ≥ 3.17 mm: **ok** |
| **Load lean, rail** (half-range; soft–stiff) | 0.041° (0.016–0.084°) | 0.053° (0.021–0.106°) |
| Load lean, castor cart | 0.125° | 0.156° |
| **Budget box, Tier 1 / Tier 2** | as the base: x 0.2, y 0.25, z 1.05 / 0.2 mm, yaw 0.015°, tilt_x 0.065 / 0.03°, tilt_y 0.02° | the same, but **tilt_x 0.075°** in Tier 1 |
| **Corner replays** (target box / Tier 1 / Tier 2), mm | lever +5.18 / +6.30 / +7.51; **wok play +2.36 / +2.25 / +3.35; spatula +2.87 / +3.87 / +4.17**; wok, lid and spider approaches and LEV_C→H_SINK ≥ +10 | lever +5.18 / +6.08 / +7.51; wok, lid and spider approaches and LEV_C→H_SINK ≥ +10 |

- **The UR5e m2 wok and spatula numbers equal the base ones to the micron.** These chains are exact re-targets: the held-object path, where those corners bind, is unchanged. This is a consistency check of the wrapper.
- **New finding (FR5 m2): one front V-wheel truck is nearly unloaded during ct2s, 0.8 N** [M moments × D masses]. The tray is poured at the cart's left rear, at cart x −0.64…−0.30.
  - The pair still carries ≥ 198 N, so there is no lift.
  - But that wheel's V seating, and so its lateral and yaw hold, falls to almost nothing. Only the 1 mm keeper clearance remains, which is worth ≈ 0.1° of yaw.
  - The UR5e minimum is 40.7 N (fold / unfold).
  - **Design change [D]:** spring-preload the two keepers (≈ 60 N each). A small roller in the T-head bears up on the slot lip, pulling the front down. That adds ≈ 40–60 N to each truck. The geometry and the sim model are unchanged.
  - **Pin rule:** the pin preload (50 N) must stay below the lighter truck's load at the docked state. No station lies in the ct2s cart range, so the pin is never down there.

### 10.3 The full lane: `scratchpad/lanes/m2_dock.sh` (controller, background)

- **One place to edit.** Every adopted file sits in the two blocks at its top (`UR=` / `FR=`, one key per file). The lane writes the manifests from them and checks that every file exists and is `ok`.
- **Structure.** UR5e and FR5 run as two parallel groups of ≤ 16 workers each. Each group runs:
  1. manifest and stations;
  2. arm-path screen;
  3. travel (10 mm);
  4. lean ×3 and budget;
  5. replays with three boxes each (`dock_stops`, the #39 target; `dock_rail`; `dock_rail_map`):
     - wok, spatula and lever plays + approaches + all ok edges;
     - lid and spider approaches + the spider play;
     - the lid play in 6 chunks per box, then merged;
  6. report: `results/r19/dock/m2/<arm>/summary.json` and the tables.
- **Time and output.** About 30–45 min [E]. It ends with `M2_DOCK_DONE`. Earlier outputs of an arm are moved to `*.bak_<time>`, never deleted.
- **Not in the lane:** plate 2 (`wok_plate2`) replays. #13 never replayed it either; it is in the arm-path screen.
- **If the cable check changes a path,** edit its key at the top of the lane and re-run it.
