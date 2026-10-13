# R19 tolerance budget (GitHub #13): cart docking and registration error vs the stored-path reserves (2026-10-13)

**Question (#13).** The stored paths are checked offline and replayed exactly. Do the 10 / 5 mm planning gates plus a realistic pose-error budget still leave positive real clearance? If not, which gates or which registration are needed?

**Labels:**
- **[S]** sourced (link in §8);
- **[E]** estimated (the basis is given);
- **[M]** measured in the sim with the unchanged checker's distance certificate.

**Files** (all new; no existing file was changed):
- `r19tol_core.py`: the scenes and the perturbation evaluator.
- `r19tol_replay.py`: the replays and tolerance searches.
- `r19tol_report.py`: the merge, the budget and the tables.
- Results in `results/r19/tol/`:
  - `scene_<scene>__<part>.json`;
  - `summary.json`;
  - `tables.md` (the full tables, including every hub edge);
  - logs, and a nominal cache.
- A demonstration run with enclosing arm geometry: `results/r19/tol/ur5e_enc/`.

## Answer first

1. **Most of the "~2 mm reserves" are a reporting artefact, not real clearance. [M]**
   - `Checker.check` refines a pair with GJK only when its bounding-box distance is within 2 mm of the gate. For every other pair it reports the axis-aligned bounding-box (AABB) bound, so its "min reserve" is often an AABB bound just above 2 mm. Hit / no-hit is not affected.
   - The exact minima (the same GJK certificate, evaluated on every pair that can be the minimum):

     | Path | Reported reserve | Exact reserve | Binding pair (exact) |
     |---|---|---|---|
     | wok | 2.02 mm | 4.0 mm | wok bottom vs cooker at set-down |
     | spatula | 2.04 mm | 4.8 mm | blade vs `raw_tomato` at the pick |
     | spider | 2.03 mm | 5.4 mm | |
     | lever | 5.98 mm | 8.6 mm | |
     | lid | 1.0 mm | 1.0 mm (true) | |
     | the wok's own reported binding pair (`raw_potato`) | 2.02 mm | 128.7 mm | |

   - Of the 15 hub edges reported at 2.0–2.3 mm, only the 4 LEV_O edges are really ~2 mm: the wrist is 12 mm from the closed upper-cabinet door. The others are 8.6–25.8 mm.
   - The three corridor edges reported at 60 mm are ≥ 80 mm.
2. **The binding error is cart TILT toward the counter, not x. [M]**

   | Axis | Gate tolerance | Notes |
   |---|---|---|
   | tilt_x− | 0.12–0.54° (contact 0.60–0.92°) for the 5 actions | lid 0.12°, spider approach 0.22° (forearm vs hood), spatula 0.35°, lever 0.38°, wok 0.54° |
   | yaw | ≥ 0.37° | |
   | y (toward the wall) | ≥ 3.9 mm | |
   | x (along the counter) | ≥ 15 mm | except the spatula, 4.8 mm against food on the prep tray |
   | z | 1.0 mm (lid into the rack), 4.0 mm (wok set-down), 2.3 mm (LEV_O wrist up into the door) | |

   Odometry hardly matters; floor tilt and load tilt do.
3. **As designed, the planning gates do not leave a usable margin.** As designed means: bumper fixes y, encoders give x, free-standing fixtures, the sim's nominal kinematics. With only the cart part of that budget [M, corner replays]:
   - the gate goes negative on the wok (−1.1 mm), lever (−2.1), spatula (−4.4), spider (−4.0) and the LEV_O edges (−4.0);
   - the spatula blade comes to 0.56 mm of the tomato.

   With the whole budget, the contact utilization (RSS) is 0.87–2.07 [E budget × M tolerances]. Real contact is therefore possible.
4. **The fix is mechanical station registration plus the related measures, and then force control at the seats:**
   - mechanical station registration (stops / V-block and a stiff bumper datum);
   - stations levelled and a measured tilt;
   - the robot's calibrated kinematics in the checker;
   - keyed fixtures.

   With these:
   - every free-space path keeps real clearance: the cart corners keep gate reserve ≥ +0.12 mm on every edge and ≥ +2.0 mm on the actions (the lid and spider plays' corner runs are controller commands, §7); the full-budget contact RSS is ≤ 0.82, except the spatula's food term;
   - the 5 mm gate is consumed at the seats: lid into the rack (1.0 mm), wok set-down (4.0 mm), lid off the pot (3.0 mm). These, the faucet lever (a closed chain) and the stir strokes need compliance or force control (#26), not better positioning.
5. **#12 overrides all arm-link numbers.** A preliminary run with `ARM=ur5e_enc` (§4.6) on the stored UR5e paths gives:
   - LEV_O→WOK is −8.1 mm past the gate (1.9 mm gap to the closed door);
   - SPIDER→H_POT is −0.04 mm;
   - the wok and spider grasp approaches are in contact: forearm vs plate, forearm vs the cabinet over the hood.

   The method re-runs unchanged with `ARM=ur5e_enc` (§7).

## 1. Error budget

Each term is the half-range between the stored path and the real world. There are four scenarios:
- **A: as designed (R10 / R19).**
- **B: the R09 docking requirement** (±2 mm XY, ±0.2° yaw, ±1 mm height; "a design requirement, not a measured positioning guarantee", `posts/r09/integrator.md`), with C for the rest.
- **C: docking stops.** Indexed stops / V-block at each station, a stiff bumper datum, keyed fixtures, the robot's calibration in the checker, station tilt measured at commissioning.
- **D: C plus a touch-off per set.**

| Term | Maps to | A | B | C | D | Basis |
|---|---|---|---|---|---|---|
| Docking x at set start | cart x | 2 mm | 2 | 0.3 | 0.2 | [E] No x datum today: `mobile.py:86-92`, the bumper fixes y only. Homing at the counter-end stop + encoder counts. |
| Wheel odometry in the set, 0.3–1.5 m | cart x | 5 mm (0.5 %) | (in B's 2) | 1 (0.1 %) | 1 | [E] Systematic error from the tyre's effective radius, plus slip: 1.5–7.5 mm over 0.3–1.5 m uncalibrated, 0.3–1.5 mm calibrated. The encoder is not the limit: the ZLTECH ZLLG65ASM500 has 4096 lines [S], i.e. 0.03–0.13 mm on the 165 mm wheel. |
| Docking y (bumper on the fronts) | cart y | 1.5 mm | 2 | 0.5 | 0.3 | [E] Door flushness ±1 mm, bumper compression ±0.5 mm. |
| Docking yaw | yaw (J1 axis) | 0.3° | 0.2 | 0.05 | 0.03 | [E] 0.56 m bumper on fronts flat to ±1.5 mm. MiR VL-marker docking is ±2–3 mm and ±0.3–0.5° [S]. |
| Floor height | z | 1 mm | 1 | 0.5 | 0.3 | [E] |
| Floor tilt, x / y | tilt_x / tilt_y | 0.15° / 0.07° | 0 (not specified) | 0.05 / 0.03 | 0.03 / 0.03 | [E] About 0.5 mm unevenness across the 0.21 m caster-to-drive-wheel base and the 0.44 m track. Tiled-floor flatness is commonly 2 mm / 2 m (GB 50209, not verified in the text). In C / D it is measured once per station and compensated. |
| Load tilt toward the counter (tyre / caster / bumper / cabinet-front compliance) | tilt_x | 0.25° | 0 | 0.10 | 0.10 | [E] About 60 N·m base moment with the wok at reach (#13 estimate). It depends on posture, so a touch-off at set start does not remove it. Mast bending is 0.003° (120×120×4 steel tube [E]), negligible. |
| Arm base on the mast plate | any translation / yaw | 0.5 mm / 0.2° | 0.05 / 0.02 | 0.05 / 0.02 | 0.05 / 0.02 | [S] Four M8 bolts (UR manual). [E] Clearance holes vs a dowel-pinned, calibrated plate. |
| Arm absolute accuracy | any translation | 2 mm | 0.3 | 0.3 | 0.3 | [S] ≥ 2 mm with nominal kinematics (ROS answers). [E] About 0.3 mm with the robot's factory calibration exported into the checker. |
| Arm repeatability | any | 0.03 mm | 0.03 | 0.03 | 0.03 | [S] UR5e datasheet, ISO 9283. |
| Servo tracking and cart / arm sync | any | 1.5 mm | 0.5 | 0.5 | 0.5 | [E] `servoj` following error, plus 4–10 ms clock skew × 0.25 m/s (#6). |
| Thermal growth | any | 0.3 mm | 0.3 | 0.3 | 0.3 | [E] Aluminium arm: 0.85 m × 23e-6/K × 15 K. Steel cart: 0.2 mm. Hot wok rim: +0.4 mm. |
| Fixture placement | that fixture's tolerance | see below | | | | [E] |
| Grasp offset in the jaws | grasp x / y / z | 1 mm | 0.5 | 0.5 | 0.5 | [E] Keyed blocks, form-fit pads (R11). |
| Grasp turn about the jaw axis | grasp rot | 2° | 1 | 1 | 1 | [E] The wok sits at 6.47 of the PGC's 7 N·m. |
| *Model geometry (#12)* | — | up to 26.5 mm | | | | [M, R19] Not in the budget. It is a model error, fixed by `ARM=ur5e_enc` (§4.6). |

**Fixture half-ranges, A / C / D** [E]. In A they are hand-placed or surveyed with a tape. In C / D they are located, keyed, or touched off by the robot.

| Fixture | A | C | D |
|---|---|---|---|
| Cooker, with the wok in its slot | 5 mm | 1 mm | 0.5 mm |
| Pot | 3 | 1 | 0.5 |
| Lid rack | 2 | 0.5 | 0.3 |
| Spatula pad, spider rest | 3 | 1 | 0.5 |
| Faucet body, lever clip | 2 | 0.5 | 0.3 |
| Sink, counter, wall | 2 | 0.5 | 0.3 |
| Upper cabinets / hood (survey) | 3 | 1 | 0.5 |
| Plates | 10 (by hand) | 2 (guarded stand) | 2 |
| Prep bowls | 5 | 2 | 2 |
| Food on the prep tray | 15 | 15 | 15 |

Food on the prep tray is not a fixture: no registration helps.

**Combining per action.** Each term is divided by the measured tolerance of its axis (§3). For "any" terms the worst of x, y, z is used.
- **Worst-case linear:** U = Σ e/tol.
- **RSS:** √Σ(e/tol)².
- Only the worst fixture term enters, because one pair involves at most one fixture.
- U ≤ 1 means the budget fits:
  - "gate" keeps the 10 / 5 mm gaps;
  - "contact" keeps any clearance in the model.
- Every tolerance is the minimum over all states and pairs, so U_lin ≤ 1 is sufficient to first order.
- Search caps (15 mm, 1.5°, and 4° for the grasp turn) are used as the tolerance where nothing binds. This is conservative: for example, `odometry_x 5/15` overstates x.

| Action | A: gate lin / RSS | A: contact lin / RSS | B: contact | C: gate | C: contact | D: contact | Largest terms (A, contact) |
|---|---|---|---|---|---|---|---|
| wok | 7.1 / 2.7 | 3.8 / **1.33** | 1.34 / 0.57 | 2.4 / 1.15 | 1.22 / **0.53** | 1.14 / 0.52 | grasp turn 2°/2.1°, plate 10/15 mm |
| spatula | 10.3 / 4.1 | 5.2 / **2.07** | 2.9 / 1.67 | 5.6 / 3.3 | 2.8 / 1.65 | 2.7 / 1.65 | food on the tray 15/9.8 mm, grasp turn |
| lever | 3.5 / 1.1 | 2.8 / 0.87 | 0.91 / 0.36 | 1.15 / 0.42 | 0.90 / 0.34 | 0.79 / 0.32 | load tilt 0.25°/0.60° |
| lid | 17.3 / 6.0 | 4.6 / **1.77** | 1.75 / 0.84 | 6.4 / 2.5 | 1.69 / 0.82 | 1.53 / 0.80 | grasp turn 2°/1.3°, load tilt, pot seat |
| spider | 6.5 / 2.5 | 3.2 / **1.22** | 1.17 / 0.56 | 2.4 / 1.12 | 1.15 / 0.55 | 1.04 / 0.54 | grasp turn, load tilt 0.25°/0.63° |
| LEV_O edges (4) | 5.6–7.3 / 1.8–2.3 | 1.8–2.3 / 0.57–0.85 | 0.64–0.70 / 0.26–0.28 | 1.6–2.1 / 0.55–0.69 | ≤ 0.54 / ≤ 0.19 | ≤ 0.48 / ≤ 0.18 | |
| the other 18 edges | ≤ 2.2 / ≤ 0.85 | ≤ 2.3 / ≤ 0.85 | ≤ 0.84 / ≤ 0.31 | ≤ 0.6 / ≤ 0.2 | ≤ 0.53 / ≤ 0.18 | ≤ 0.47 / ≤ 0.18 | |

How to read the table:
- **Gate utilization stays above 1 for the actions in every scenario.** The binding terms are the seats: lid z 1.0 mm, wok z 4.0 mm, lid-on-pot 3.0 mm, and the matching grasp offsets. No registration fixes a 1 mm seat height. These are contact windows (§5).
- **Under C / D the spatula's contact U is set by the food term.** It drops to about 0.5 if the prep tray is kept 15 mm farther from the spatula pad (a layout rule).

## 2. Method [M]

**Paths:**
- **The 5 checked actions.** Each stored `play` is 2π-unwrapped, joint-linear between stored states, and densified so that `point_bound.segment_bound` ≤ 4 mm per step: the r19smooth rule, the same 14,103 states as its baselines.
- **Their 9 grasp approaches / release retreats** (empty gripper, object in the world, r17chain's `approach()` scene).
- **The 22 hub edges** (stored ≤ 4 mm states, the r19hub union scene).
- **All of it in the R18b layout.** 48,503 states in total.

**Perturbations:**
- **Cart:** the whole robot moved rigidly against the kitchen:
  - x, y, z;
  - yaw about the arm's J1 axis;
  - tilt_x / tilt_y about the floor line under the cart origin. tilt_x− leans the top toward the counter.
- **Fixture groups:** moved by x, y, z.
- **Held part:** moved in the tool frame by x, y, z, and turned about the jaw axis.

**Distance.** The checker's own certificate (`distance.Bounds`):
- the AABB bound;
- an oriented-box separating-axis bound;
- the GJK dual lower bound, evaluated by branch and bound on every pair that can be the minimum, so the minimum is exact.

Only pairs that the perturbation can change are evaluated. A per-state lower bound with the displacement bound prunes states. Nothing is approximated where it matters: any pair's distance changes by at most the largest displacement of its points.

**Two thresholds:**
- **gate:** distance − 10 / 5 mm;
- **contact:** distance < 0.01 mm.

**Tolerance search:**
- exponential search (0.5 mm / 0.05° doubling), then bisection to 0.05 mm / 0.005°;
- run on a quarter of the states, then verified on all states;
- caps: 15 mm / 1.5°, and 4° for the grasp turn.

**Also run:**
- the requested grid (±1/2/5/10 mm, yaw ±0.1/0.2/0.5/1°, tilts ±0.1/0.2/0.5°);
- each budget box's worst sign corner (all 2⁶ corners; box = per-axis RSS of §1's cart terms).

**Cross-check with the unchanged checker.** `Checker.check(full=True)` was run with the error applied through the cart joints (x, y, and yaw about J1), at the binding state, just below and just above each x / y / yaw tolerance. 62 checks:
- the reserve equals the evaluator's to 0.000 mm;
- 3 % below the tolerance: no GJK hit (31/31). 3 of them have MuJoCo-contact-only hits, the known box-box artefact;
- 3 % above the tolerance: the checker's GJK hit is present (31/31).

**Not modelled:**
- tilt pivots elsewhere: a pivot on the front caster line adds ≤ 0.5 mm at 0.3°;
- dynamic deflection;
- the stir cycle: its states are not stored (R19_SMOOTH §5).

## 3. Sensitivity, measured: the reserve map

### 3.1 Exact nominal minimum (the full list, edges included, is in `tables.md`)

| Path | Exact gate reserve | Gap | Binding pair, where | Checker-reported |
|---|---|---|---|---|
| wok play | 4.00 | 9.00 | wok bottom tile / cooker, at the seat (pick and set-down) | 2.02 |
| wok grasp approach | 9.98 | 19.98 | forearm `R_geom_16` / plate | 2.4 |
| spatula play | 4.80 | 9.80 | blade / `raw_tomato`, pick → lifted | 2.04 |
| lever play | 8.61 | 13.61 | lever bar / lever hub | 5.98 |
| lid play | **1.00** | 6.00 | lid rim / rack base, over the rack → in the rack | 1.0 |
| spider play | 5.37 | 10.37 | spider bowl / pot ear, leaving the pot | 2.03 |
| spider grasp approach | 5.43 | 15.43 | `R_geom_11` / hood | 4.2 |
| LEV_O → H_SINK / H_WOK / WOK / H_SPAT | **2.03–2.39** | 12.0–12.4 | wrist `R_geom_25` / closed upper-cabinet door `r07_closed_door_1_0` | 2.0–2.1 |
| LEV_C edges, SPAT → LEV_C | 8.57 | 18.57 | same pair | 2.2–2.3 |
| SPIDER edges | 17.6 | 23.5 | `R_geom_11` / hood | 2.1–2.3 |
| WOK edges | 25.3 | 30.3 | finger / wok grip block | 2.0–2.1 |
| LID_RACK edges | 25.8 | 30.8 | finger / lid tab | 2.1–2.3 |

### 3.2 Cart pose tolerance per axis (worst sign; gate / contact)

The action rows are the play plus its approaches.

| Action / edge | x mm | y mm | z mm | yaw ° | tilt_x ° | tilt_y ° | First to bind (gate) |
|---|---|---|---|---|---|---|---|
| wok | >15 / >15 | 10.3 / >15 | 4.0 / 9.0 | 0.82 / 1.23 | 0.54 / 0.92 | **0.33** / 0.73 | wok bottom / cooker at the seat |
| spatula | **4.8** / 9.8 | 5.8 / 10.8 | 9.3 / >15 | 0.65 / 1.32 | 0.35 / 0.65 | **0.29** / 0.60 | blade / raw tomato at the pick |
| lever | >15 / >15 | 9.9 / >15 | >15 / >15 | 1.3 / >1.5 | **0.38** / 0.60 | 0.86 / 1.27 | lever bar / hub |
| lid | 14 / >15 | 10.0 / 15 | **0.99** / 6.0 | 1.4 / >1.5 | **0.12** / 0.65 | 0.14 / 0.82 | lid rim / rack base, in the rack |
| spider | >15 / >15 | 5.6 / >15 | 9.3 / 15 | >1.5 / >1.5 | **0.22** / 0.63 | 0.96 / 1.2 | `R_geom_11` / hood, at the grasp |
| LEV_O edges | >15 / >15 | 3.9 / >15 | 2.3 / 14 | 0.37 / >1.5 | 0.34 / >1.5 | **0.22** / 1.2 | wrist / closed cabinet door |
| LEV_C, SPAT→LEV_C | >15 | >15 | 10.2 / >15 | 1.26 / >1.5 | 1.26 / >1.5 | 0.82 / 1.15 | same pair |
| SPIDER edges | >15 | >15 | >15 | >1.5 | 0.73 / 1.13 | 1.1 / >1.5 | `R_geom_11` / hood |
| LID_POT edges | >15 | >15 | >15 | >1.5 | 1.29 / >1.5 | >1.5 | `R_geom_10` / hood |
| corridors, WOK, LID_RACK, SPAT spurs | >15 | >15 | >15 | >1.5 | >1.5 | >1.5 | — |

Signs and binding segments are in `summary.json`. In every action the tightest tilt is the lean toward the counter (tilt_x−), or tilt_y at the seats.

### 3.3 Grid

The requested grid: the min gate reserve over all states, worst sign. A negative value is below the gate; add 10 (robot) or 5 (gripper / held) to get the gap.

| | x ±5 | x ±10 | y ±5 | y ±10 | z ±2 | z ±5 | yaw ±0.5° | yaw ±1° | tilt_x ±0.2° | tilt_x ±0.5° | tilt_y ±0.5° |
|---|---|---|---|---|---|---|---|---|---|---|---|
| wok | 4.0 | 4.0 | 4.0 | 0.29 | 2.0 | −1.0 | 3.9 | −2.2 | 2.6 | 0.34 | −2.1 |
| spatula | −0.2 | −5.0 | 0.8 | −4.2 | 4.5 | 2.6 | 1.1 | −2.6 | 2.5 | −2.5 | −3.3 |
| lever | 8.6 | 6.0 | 4.3 | −0.1 | 7.6 | 6.4 | 5.7 | 2.8 | 4.1 | −2.6 | 6.7 |
| lid | 1.0 | 1.0 | 1.0 | 0.0 | −1.0 | −4.0 | 1.0 | 1.0 | −0.6 | −3.1 | −2.6 |
| spider | 3.4 | 1.7 | 0.6 | −4.3 | 4.2 | 2.5 | 4.4 | 3.7 | 0.6 | −6.8 | 4.2 |
| LEV_O→WOK | 2.0 | 2.0 | −0.6 | −3.1 | 0.3 | −2.3 | −0.7 | −3.5 | 0.9 | −1.0 | −2.5 |

### 3.4 Fixtures and grasp (worst axis; gate / contact)

| Action | Fixture: tolerance (binding pair) | Grasp offset | Grasp turn |
|---|---|---|---|
| wok | cooker 4.0 / 9.0 mm (seat); faucet 10.3 / 15 (rim / spout while emptying); plate 11 / 15; hood 12.6 / 15 | 4.4 / 9.9 mm | 0.94 / 2.1° |
| spatula | **food on the prep tray 4.8 / 9.8**; prep bowl 5.8 / 10.8; wok 7.5 / 14 (stroke start) | 4.8 / 9.8 | 0.95 / 1.8° |
| lever | faucet body 9.9 / 15 | 8.6 / 13.6 | >4° |
| lid | **rack 1.0 / 6.0 (z)**; pot 3.0 / 8.0 (seat); hood 10 / 15; counter 11 / 15 | **0.99 / 6.0** | 0.49 / 1.3° |
| spider | hood 5.6 / 15; pot 7.7 / 15 | 5.9 / 11.6 | 1.0 / 2.0° |

### 3.5 Budget boxes, worst corner replayed (cart terms only) [M]

Min gate reserve / min gap, mm.

| | A as designed | B R09 requirement | C docking stops | D touch-off |
|---|---|---|---|---|
| wok | −1.07 / 3.93 | 3.0 / 8.0 | 2.36 / 7.36 | 2.60 / 7.60 |
| spatula | −4.44 / **0.56** | 1.31 / 6.31 | 2.87 / 7.87 | 3.03 / 8.03 |
| lever | −2.06 / 2.94 | 5.20 / ≥10 | 5.03 / ≥10 | 5.55 / ≥10 |
| spider (approaches; the play is a controller run) | −4.01 / 5.99 | 2.15 / 7.15 | 2.03 / ≥10 | 2.45 / ≥10 |
| lid (approaches; the play is a controller run) | 3.62 / 8.62 | ≥10 | ≥10 | ≥10 |
| LEV_O edges | −3.98 / 6.02 | −0.97 / 9.03 | **0.12** / ≥10 | 0.53 / ≥10 |
| LEV_C edges, SPAT→LEV_C | 1.77 / ≥10 | 5.28 / ≥10 | 6.46 / ≥10 | 6.90 / ≥10 |
| all other edges | ≥ 7.9 | ≥10 | ≥10 | ≥10 |

The R09 requirement gives no tilt. With tilt included (A), every binding place loses its gate.

### 3.6 Preliminary: enclosing arm geometry (#12, `ARM=ur5e_enc`, stored UR5e paths)

| Scene | UR5e capsules | ur5e_enc |
|---|---|---|
| LEV_O→WOK | +2.03 | **−8.08** (gap 1.9 mm to the door; tilt_y− 0.21° and tilt_x− 0.28° to contact) |
| SPIDER→H_POT | +17.6 | **−0.04** |
| LID_POT→H_POT | +23.4 | +4.3 |
| spider grasp approach | +5.4 | **contact** (forearm / cabinet over the hood) |
| wok grasp approach | +10.0 | **contact** (forearm / plate) |
| lever play | +8.6 | +8.6 (held-part pair, unchanged) |

This run used `r19/arm_ur5e_enc.json` as it was on disk during this study; the fit may still change, and #12 owns the re-check. Every arm-link reserve above must be re-run on the final enclosing model (§7).

## 4. Registration options

| Option | Achievable | Cost | Rescues | Does not rescue |
|---|---|---|---|---|
| **Mechanical docking.** A roller bumper pressed against a straight datum rail on the plinth gives y and yaw continuously. An indexed stop / tapered pin / V-block per station gives x. | Station ±0.3–0.5 mm, ±0.05° [E]. Kinematic couplings reach µm on rigid bodies [S, general]; a commercial AMR dock is ±1 mm [S, ROEQ]. Between stations only y / yaw are held; x drifts 0.1 % from the last stop. | Est. ¥1–3k: rail, rollers, 4 receivers (3D-printed / steel), a spring plunger. | x, y, yaw at every hub; most of the cart terms. | Tilt under load (needs a stiff bumper datum low on the plinth plus stiffer casters), floor tilt (needs levelling feet or measurement), seats. |
| **Fixture keying.** Cooker locator frame on the counter, keyed lever clip, guarded plate stand, rack and pad with lead-ins. Chamfers ≥ the budget: ≥ 3 mm at the rack slot, ≥ 5 mm at the wok slot. | Fixture ±0.5–1 mm [E]. Lead-ins make the seats self-locating. | 3D-printed parts, est. < ¥1k. | Fixture terms. Wok, lid and spider seats when combined with compliance. | Food on the prep tray (keep-out rule instead). |
| **Touch-off / force-guided seating.** The UR5e has a built-in flange F/T sensor [S]. Touch 3 datum faces per station, about 10–20 s [E]. `force_mode` descent onto the seats. | ±0.2–0.5 mm, tilt ±0.03° [E]. | Software and cycle time. Per station visit, not per set: 71–167 sets per meal × 15 s = 18–42 min. | Station tilt and offset, the lid into the rack, wok set-down, lid off the pot, grasp closure. | Load tilt during a carry; free-space clearance after the touch. |
| **Camera fiducials / AprilTags.** | cm-level at 0.7–3 m in the literature; 5–8 mm at 0.7 m after improvements [S, Abbas et al. 2019]. A calibrated wrist camera at 0.2–0.3 m: est. 0.5–1 mm. | ¥1–3k camera plus calibration. | Coarse station check, plates and other movable items, a "fixture moved" detector. | Not alone for 1–4 mm reserves or 0.1° tilt. |
| **Re-localization per set.** The library's "cart within 0.5 mm of the hub" check is encoder-only (R19_MOTION_LIBRARY §4), not a pose measurement. | As good as the method used: touch-off or a fiducial. | Time per set. | Drift between stations. | — |
| **Re-planning.** A gate kept clear of the binding places: LEV_O retreat, spider approach vs the hood, the spatula pad vs the prep tray. | Needs a tilt-aware check (§6). | Sim time. | The 4 LEV_O edges, the spider, the spatula. | — |

**What cannot run as a stored position path (#26):**
- the lid into the rack: its z tolerance is 0.99 mm and its grasp-offset tolerance is 0.99 mm, below any registration budget;
- the wok set-down onto the keyed cooker slot: 4.0 mm z, 0.33° tilt_y;
- the lid off the pot: 3.0 mm;
- the faucet lever: a closed kinematic chain about the lever pivot. Any registration error becomes force in the clip; the collision tolerance does not measure that;
- the stir strokes: blade on steel;
- every grasp closure: the jaws centre the block along one axis only.

All of them need force-mode or compliant seating with lead-ins, and monitoring.

## 5. Verdict

**No.** The 10 / 5 mm gates with a realistic budget do not leave a reliable positive clearance today:
- The cart terms alone take the gate negative at 5 of 5 actions or their approaches, and at the 4 LEV_O edges.
- The spatula comes within 0.56 mm of food.
- The full budget's contact RSS is 0.87–2.07 for the actions.
- #12 has already put LEV_O→WOK and the two grasp approaches past the gate or into contact with the enclosing geometry.

**Needed, in order:**
1. **Close #12 first.** Its numbers dominate every arm-link pair. Re-run this study with `ARM=ur5e_enc` (§7).
2. **Mechanical station registration and cart stiffness.**
   - Docking stops / V-block for x.
   - A roller bumper on a datum rail for y and yaw.
   - A bumper datum low and stiff, with stiff casters, so that the lean toward the counter under load stays ≤ 0.1°.
   - Station tilt measured at commissioning and compensated (≤ 0.05°).

   This is scenario C. Measured: every free-space path keeps positive real clearance. Corner gate reserve ≥ +0.12 mm at LEV_O and ≥ +2 mm on the actions.
3. **The robot's factory kinematic calibration in the checker / exporter.** It removes about 2 mm.
4. **Keyed fixtures with lead-ins ≥ the budget, and layout rules:**
   - prep tray and bowls ≥ 15 mm farther from the spatula pad's swept volume;
   - plates only in a guarded stand.
5. **Force-guided seating for the contact windows** (lid rack, wok seat, pot lid, lever, stir, grasp), #26.
6. **Planning gates.** Keep 10 / 5 mm and add a pose-tolerance rule: a free-space set passes only if each measured tolerance (this study's method) is at least 2× the C budget on that axis. The C budget, linear per axis:
   - x 2.5 mm, y and z 1.7 mm (including the 1.2 mm "any" terms);
   - yaw 0.07°, tilt_x 0.15°, tilt_y 0.03°.

   So the thresholds are: x ≥ 5 mm, y and z ≥ 3.5 mm, yaw ≥ 0.15°, tilt_x ≥ 0.3°, tilt_y ≥ 0.1°.

   What fails today:
   - the 4 LEV_O edges: z 2.3 mm (wrist up into the closed door) — re-plan the retreat;
   - the spider at its rest (the grasp approach and the play's last segment): tilt_x 0.22–0.23° (`R_geom_11` vs the hood) — re-plan, after #12;
   - the spatula pick: x 4.8 mm against food — a layout rule;
   - the lid into the rack: z 1.0 mm, tilt_x 0.12° — a seat: force-guided, #26.

   Everything else passes the rule. A uniform 15 mm gate would also work, but at the cost of re-planning every path. The rule targets the few places that bind.

## 6. Odds and ends

- **The reported reserve.** A follow-up, not changed here: the checker could refine the per-category minimum pair until it is exact (one more GJK per category). Reports would then show true clearances. It does not change any hit.
- **The R19 motion library's tolerance table (§5) and R19_SMOOTH's "2.02 mm wok" use AABB bounds.** The exact values are in §3.1.
- **The lid's 1.0 mm is true.**

## 7. Commands

Run from `robot_rail/sim/r10/claude`, with `PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe`. Each command has an internal `DEADLINE` (seconds): at the deadline the pool is terminated and the unfinished tasks are listed.

**Already run here (each command under 5 minutes):**
```
$PY r19tol_replay.py SET=actions PARTS=nom WORKERS=14                     # nominal cache (68 s)
$PY r19tol_replay.py SET=actions PARTS=cartT,cartR WORKERS=16             # + play:lid / play:spider split per axis: PARTS=cart-x,...,cart-tilt_y
$PY r19tol_replay.py SET=actions PARTS=grid-x,grid-y,grid-z,grid-yaw,grid-tilt_x,grid-tilt_y WORKERS=16
$PY r19tol_replay.py SET=actions PARTS=fix WORKERS=16                     # play:lid split: fix-spider_rest, fix-upper, fix-lid_rack, fix-pot, fix-counter+cooker+wall
$PY r19tol_replay.py SET=actions PARTS=grasp-x,grasp-y,grasp-z WORKERS=16 ; $PY r19tol_replay.py SET=actions PARTS=grasp-rot ROTMAX=4 WORKERS=8
$PY r19tol_replay.py SET=edges PARTS=nom WORKERS=16
$PY r19tol_replay.py SET=edges PARTS=cartT,cartR WORKERS=16
$PY r19tol_replay.py SET=edges PARTS=grid,fix WORKERS=16
$PY r19tol_replay.py SET=actions PARTS=scen-R09_requirement,scen-as_designed,scen-dock_stops,scen-touch_off WORKERS=16
$PY r19tol_replay.py SET=edges PARTS=scen-R09_requirement,scen-as_designed,scen-dock_stops,scen-touch_off WORKERS=16
$PY r19tol_report.py
```

**For the controller (longer than 5 min; run in the foreground session's background):**
```
# the two corner replays not finished here (est. 10-30 min each)
$PY r19tol_replay.py SCENES=play:lid PARTS=scen-R09_requirement,scen-as_designed,scen-dock_stops,scen-touch_off WORKERS=4 DEADLINE=3600
$PY r19tol_replay.py SCENES=play:spider PARTS=scen-as_designed,scen-dock_stops,scen-touch_off WORKERS=3 DEADLINE=3600
$PY r19tol_report.py
# after #12's enclosing model is final: the whole study on the stored UR5e paths (est. 40-60 min total)
$PY r19tol_replay.py ARM=ur5e_enc PATHS=base SET=all PARTS=nom WORKERS=16 DEADLINE=900
$PY r19tol_replay.py ARM=ur5e_enc PATHS=base SET=all PARTS=cart-x,cart-y,cart-z,cart-yaw,cart-tilt_x,cart-tilt_y WORKERS=16 DEADLINE=3600
$PY r19tol_replay.py ARM=ur5e_enc PATHS=base SET=all PARTS=grid-x,grid-y,grid-z,grid-yaw,grid-tilt_x,grid-tilt_y,fix,grasp-x,grasp-y,grasp-z,grasp-rot ROTMAX=4 WORKERS=16 DEADLINE=3600
$PY r19tol_replay.py ARM=ur5e_enc PATHS=base SET=all PARTS=scen-R09_requirement,scen-as_designed,scen-dock_stops,scen-touch_off WORKERS=16 DEADLINE=3600
$PY r19tol_report.py ARM=ur5e_enc PATHS=base
```
The ur5e_enc outputs go to `results/r19/tol/ur5e_enc/`. The demonstration files already there (§3.6) may be deleted first. With `PATHS=auto` instead of `base`, an arm option's own re-planned chains are used where they hold states.

## 8. Sources

- [UR5e datasheet](https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf): repeatability ±0.03 mm (ISO 9283), built-in F/T sensor.
- [UR manual, mounting](https://www.universal-robots.com/manuals/es/HTML/SW10_13/Content/prod-cable40m/Getting_started_en.htm): four M8 bolts, 20 N·m.
- [ROS answers 324883](https://answers.ros.org/question/324883/inverse-kinematics-in-ur_driver-is-not-accurate): ≥ 2 mm off without the robot's calibration data.
- [ZLLG65ASM500 V2.0](https://aifitlab.com/products/zhongling-zllg65-asm500-v2-0-motor): 4096-line encoder.
- [MiR250 spec](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf): VL-marker docking ±3 mm, ±0.5°. MiR600 / 1350: ±2 / ±3 mm, ±0.3°.
- [Strathclyde, KUKA KMR iiwa](https://strathprints.strath.ac.uk/89779): repeatability about 2.5 mm in practice, < 7 mm with mapping.
- [Abbas et al. 2019, AprilTag state estimation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6960891/): 4.4 → 0.8 cm (x) at 70 cm; 1.6–3.4 cm at 2 m.
- GB 50209-2010 (building floor acceptance): the 2 mm / 2 m tile flatness figure is commonly cited, not verified in the text.
- ROEQ docking ±1 mm and kinematic-coupling repeatability: from the search summaries; general.
