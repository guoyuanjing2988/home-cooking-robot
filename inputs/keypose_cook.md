# T03 keypose_cook — washing and cutting

**Reject this common candidate for hardware freeze.** Galley: **1/57 phases OK**; L kitchen: **1/57 phases OK**. All 402 independent key poses in each kitchen were evaluated, including neighbourhoods, even after an upstream failure. This is a hardware key-pose screen; no continuous path was requested or used as a criterion.

The proposed changes add **0.863079 kg to the robot**. The current 1130.4 ×700 mm base, 720 mm wheelbase, 500–1300 mm lift and integrated brakes remain in the pose model. Off-robot fixture masses are separate. Failed poses give numerical rejection witnesses, not proof that every possible design or stance fails.

## Scope and process definition

The [cooking reference](cook_ref.md) and [prep_spec.json](../../sim/t03/cook_ref/prep_spec.json) determine the sequence: take each ingredient; park before operating water; rinse/rub; peel carrot and potato; remove potato eyes; rinse fragments and clean the board; trim/facet roots; trim and separate greens and clean basal creases; core and cut tomato; transfer small batches; park each separate bowl; return, rinse and supported-wipe the knife. Both kitchens use these same 57 required definitions. Common calls are expanded at each use; four root orientations and eight board-cleaning extremes and fifteen clean-bowl reset poses produce 402 poses per kitchen. Optional potato julienne is deferred.

Quality requirements remain 5 ±1 mm root slices with ≤1 mm within-slice variation; 40 ±10 mm greens; eight radial tomato wedges, nominal angular sector 45 ±10 degrees and specified mass balance; peel depth 0.2–0.8 mm, gouge ≤2 mm; and ≥98% edible transfer. First/middle/last root cuts include the actual 10 mm terminal stub and 5 mm final slice. The holding target sits on remaining food, not an imaginary 30 mm grip beyond the end. Tomato cuts pass through the half's radial origin, including ±45 degree extremes. Transfer uses 50 g root or ≤25 g greens/tomato batches above the 90 mm bowl rim. These are pose/control and nominal-volume requirements, not a claim of measured cleanliness, bruising or edible yield.

## Numerical method and limits

Stance search ranges over each complete free-floor rectangle in x, y, yaw and lift; mink solves both arms together where required. Search budget is 3 seconds with 16 requested Sobol samples; actual returned candidate counts and runtime are saved. Unchanged pose targets reuse searched stances after physical re-evaluation; moved tools and new poses receive fresh search. A FAIL labelled reach reports the residual of that bounded search. It is not a certified minimum reach deficit over all configurations.

The copied fixed T02 ACM retains five sampled always-touching OEM pairs, same-rigid-body contacts and static scene internal contacts. It has no extra finger, held-object or nonadjacent-arm exemptions. Final hardware was re-sampled at 400 configurations. All shapes have 10 mm padding; reported real gap is padded-contact distance plus 20 mm. Forbidden gaps must be ≥10 mm. With no contact, 10 mm is recorded as a lower bound. Held tools, food, bowls, colander and scoop batches are present. Only named distal grasp-package and actual blade/food/board contact pairs are intentional.

Each pose also checks 12 actual ±20 mm/±5 degree axis extremes. No downward sample is projected back onto the board. Consequently a pose that only works exactly at a support can fail this required clearance neighbourhood. These finite samples do not certify every combination inside a six-dimensional ball. Every loaded cutting pose and neighbour checks all three downward forces with both signs of a 10 N lateral force along both horizontal axes. Gravity, tool and food payload, both arms and lift are included; board carries the main downward food reaction, holding hand resists the lateral reaction.

Dexterity JSON reports all seven distances to limits, minimum limit distance, singular values, raw Jacobians and scaled manipulability for both arms at every nominal and neighbourhood pose. Translation rows use a 0.5 m characteristic length for dimensionless scaled manipulability. A dexterity number is descriptive, not an arbitrary extra pass gate.

Load-increment joint compliance uses [ZeroErr eRob manual V3.36, Table 27-1](https://zeroerr.cn/d/file/download/eRob%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%85%B3%E8%8A%82%E6%A8%A1%E7%BB%84%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_V3.36.pdf) for gear ratios ≥80. Motor angles are held; no stiffness compensation is credited. Relative blade/holding-hand feed displacement is calculated from joint torque increments and local Jacobians; machining/finger allowances add 0.025 mm feed and 0.0035 rad plane uncertainty. This can reject slice uniformity even below a continuous torque limit. It is a first-order joint-only estimate; fixture/link flexibility and real-food trials remain needed.

Static gravity uses the [MuJoCo recursive Newton–Euler function](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-rne) with zero velocity/acceleration, followed by the same world-wrench Jacobian calculation. It matched the original full-forward generalized torque vector exactly at 11 representative poses (maximum discrepancy 0.0); collision checks remain unchanged and separate. The analytic stance Jacobian also matched finite differences within 2.42×10⁻¹⁰. Validation artifacts are in results/.

Neighbourhood verdicts gate kinematic precision and forbidden-contact clearance. Offset torque and grip calculations are retained as additional diagnostics; an off-contact ±20 mm sample is not rejected merely because it is away from the nominal grasp key. Nominal key-pose torque, grip and quality remain required.

Container wrist orientation follows its body orientation through drain/shake extremes, preserving one fixed grasp transform. Positive capture checks actual key registration within 3 mm and 1 degree at the nominal pose. Sensor C03 shutoff poses stay outside the detection range; they do not re-enter the sensor field using a mechanical-lever reversal. Unused clean bowls occupy real counter supports and three resets each include pre-grasp, grasp, lift, place and release.

## Supports, tools and grip

Support polygons are the actual counter/sink/tray contacts clipped against each base footprint. COM is derived from assembly masses; bowl and colander margins include 15 and 20 mm assumed COM eccentricity respectively. Source food envelopes seat on the actual frustum wall planes. The knife rests on separate blade/handle lands at 214/201 mm above the counter; the raised holder has real posts and a deck. Its own weighted COM is checked, as are the knife and peeler separately. The L holder is rotated along world y at (−0.045, −1.64, 0.85) m; the peeler and finished bowls occupy separate front-counter locations. No unsupported pedestal is used.

kitchen_galley: setup support margins: holder 65.2 mm; knife 30.6 mm; peeler 20.7 mm; wash bowl 45.0 mm; colander 40.0 mm; board 100.0 mm. Every phase has its own support ledger, including completed bowls.

kitchen_l: setup support margins: holder 52.3 mm; knife 30.6 mm; peeler 20.7 mm; wash bowl 45.0 mm; colander 40.0 mm; board 150.0 mm. Every phase has its own support ledger, including completed bowls.

An exact-target envelope check independently rejects the current terminal root pinch: the 6 mm holding pad is centred 2.5 mm ahead of a 2 mm knife plane. Where their vertical spans overlap, ideal separation is 2.5−3−1 = **−1.5 mm**, a **11.5 mm deficit** to the required 10 mm clearance. This local conflict remains even with perfect IK. The full last slice cannot be silently omitted or replaced by a larger discarded stub.

The force caps are deliberately conservative. [Whole-fruit compression research](https://www.tandfonline.com/doi/full/10.1080/10942912.2014.917379) reports roughly 10 N at 4% deformation in one specific test, while [a separate tomato study](https://www.mdpi.com/2077-0472/13/12/2201) shows substantial rupture-force differences with ripeness and loading direction. Neither supplies a universal allowable force for these fingertip shapes; the adopted 10/15 N command caps remain declared analyst bounds.

Wet friction uses μ=0.15, 10% force derating and SF=1.5. Positive capture uses sized metal tongue/channel shoulders, through-bolted backers and the actual bearing span, capped by the OEM 15 Nm mounting limit. The right 40 mm finger span is needed for cleaver roll; the left 6 mm span has only 2.4 Nm unfactored roll capacity. The nominal 400 N key bearing capacity is an engineering design screen, not a tested rating. Clamp-force sizing, metal stress and mass reserves are recorded in changes.json.

The PGC300's 80 N/jaw minimum cannot meet the analyst-selected conservative limits of 10 N/jaw for tomato and 15 N/jaw for greens: margins are 0.125 and 0.1875 before any collision problem. Those force limits are analyst assumptions, not thresholds supplied by the cooking reference or measured bruising limits. The reference requires no visible bruising and less than 10% tomato compression; projected span, actual jaw opening and compression are saved explicitly. The model does not silently command a smaller force. Long arms or stronger joints cannot resolve this force-control mismatch. Conventional faucet operation is replaced by presence sensing, so operating torque is zero for the adopted sensor; no stove knob is analysed.

## Phase verdicts

A phase is OK only when all of its expanded key poses pass. Each FAIL below lists its first numerical witness; the full JSON retains every blocker, force case and neighbourhood. Positive gap below 10 mm is a clearance failure with zero penetration.

| Phase | Required action | Galley | L kitchen |
|---|---|---|---|
| C01 | Prepare supported stations and expose each ingredient | OK | OK |
| C02 | Turn faucet on | FAIL — lever_open: sensor_faucet_spout / prep_R_minus_tip: gap 8.8 mm, penetration 0.0 mm | FAIL — lever_pre_grasp: parked_tomato_grip_key_-1_box / ee_R_PGC300_0: gap -34.9 mm, penetration 34.9 mm |
| C03 | Turn faucet off | FAIL — lever_pre_grasp: R_arm_AR4_0484_0 / R_arm_AR4_0669_12: gap -7.6 mm, penetration 7.6 mm | FAIL — lever_pre_grasp: lift_LD5_0053 / R_arm_AR4_0503_1: gap -0.3 mm, penetration 0.3 mm |
| C04 | Pick up the knife from valid storage | FAIL — pre_grasp: R_arm_AR4_0491_0 / R_arm_AR4_0701_2: gap 2.0 mm, penetration 0.0 mm | FAIL — pre_grasp: IK residual 50.2 mm; 15.2 deg |
| C05 | Return knife to valid storage | FAIL — knife_above_dock: R_arm_AR4_0491_0 / R_arm_AR4_0701_2: gap 0.5 mm, penetration 0.0 mm | FAIL — knife_above_dock: IK residual 188.1 mm; 19.6 deg |
| C06 | Rinse and dry the knife after preparation | FAIL — knife_rinse_near: IK residual 54.8 mm; 16.8 deg | FAIL — knife_rinse_near: IK residual 107.6 mm; 34.2 deg |
| C07 | Empty/change wash water and reset bowl | FAIL — bowl_pre_grasp: IK residual 33.0 mm; 0.1 deg | FAIL — bowl_pre_grasp: L_arm_AR4_0352_0 / R_arm_AR4_0490_1: gap -33.8 mm, penetration 33.8 mm |
| carrot_01 | Take vegetable from basket | FAIL — pre_grasp: sink_cabinet / lift_LD5_0271: gap 9.0 mm, penetration 0.0 mm | FAIL — pre_grasp: IK residual 22.4 mm; 8.0 deg |
| carrot_02 | Start cold water with vegetable parked | FAIL — pre_grasp: sensor_faucet_spout / R_arm_AR4_0685_5: gap 9.969796218 mm, penetration 0.0 mm | FAIL — pre_grasp: west_cabinet / pe_PE5_00546: gap 7.9 mm, penetration 0.0 mm |
| carrot_03 | Rinse and rub every surface | FAIL — rinse_front: lift_LD5_0118 / L_arm_AR4_0071_0: gap -59.0 mm, penetration 59.0 mm | FAIL — rinse_front: IK residual 72.3 mm; 5.7 deg |
| carrot_04 | Peel the washed root | FAIL — above_board: R_arm_AR4_0484_0 / R_arm_AR4_0669_12: gap -12.8 mm, penetration 12.8 mm | FAIL — above_board: IK residual 21.3 mm; 6.3 deg |
| carrot_06 | Rinse away peel fragments; close water | FAIL — peeled_rinse: sensor_faucet_spout / ee_R_PGC300_0: gap -80.7 mm, penetration 80.7 mm | FAIL — peeled_rinse: sensor_faucet_spout / ee_R_PGC300_0: gap -80.7 mm, penetration 80.7 mm |
| carrot_07 | Move clean vegetable to cutting board | FAIL — grasp: colander_wall_14_box / ee_R_cable_jacket_22: gap 5.4 mm, penetration 0.0 mm | FAIL — pre_grasp: west_cabinet / pe_PE5_00546: gap 5.1 mm, penetration 0.0 mm |
| carrot_08 | Pick up knife | FAIL — C04/grasp: knife_dock_handle_land / prep_R_plus_tip: gap 9.998901664 mm, penetration 0.0 mm | FAIL — C04/pre_grasp: IK residual 25.0 mm; 7.4 deg |
| carrot_09 | Trim ends and create a flat support face | FAIL — first_stroke_start: lift_LD5_0119 / L_arm_AR4_0130_0: gap -55.4 mm, penetration 55.4 mm | FAIL — first_stroke_start: IK residual 127.2 mm; 33.3 deg |
| carrot_10 | Stabilise, feed and cut 5 mm slices | FAIL — first_stroke_start: IK residual 25.7 mm; 18.3 deg | FAIL — first_stroke_start: IK residual 117.5 mm; 34.2 deg |
| carrot_11 | Push/scoop pieces into the ingredient bowl | FAIL — scoop_start: lift_LD5_0053 / R_arm_AR4_0503_2: gap -20.6 mm, penetration 20.6 mm | FAIL — scoop_start: IK residual 60.5 mm; 2.1 deg |
| carrot_12 | Return knife between batches | FAIL — C05/knife_above_dock: R_arm_AR4_0490_0 / R_arm_AR4_0708_0: gap 7.9 mm, penetration 0.0 mm | FAIL — C05/knife_above_dock: IK residual 65.8 mm; 13.5 deg |
| carrot_13 | Park finished bowl and reset the active station | FAIL — filled_bowl_grasp: IK residual 15.9 mm; 0.4 deg | FAIL — filled_bowl_grasp: IK residual 410.3 mm; 27.6 deg |
| potato_01 | Take vegetable from basket | FAIL — pre_grasp: R_arm_AR4_0490_0 / R_arm_AR4_0708_0: gap 4.8 mm, penetration 0.0 mm | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm |
| potato_02 | Start cold water with vegetable parked | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm |
| potato_03 | Rinse and rub every surface | FAIL — rinse_front: lift_LD5_0070 / L_arm_AR4_0141_0: gap -76.0 mm, penetration 76.0 mm | FAIL — rinse_front: IK residual 86.4 mm; 31.6 deg |
| potato_04 | Peel the washed root | FAIL — above_board: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm | FAIL — above_board: IK residual 42.5 mm; 5.5 deg |
| potato_05 | Remove shallow eyes/blemishes on supported potato | FAIL — eye_scoop_start: lift_LD5_0002 / R_arm_AR4_0627_0: gap -58.2 mm, penetration 58.2 mm | FAIL — eye_scoop_start: IK residual 59.0 mm; 15.7 deg |
| potato_06 | Rinse away peel fragments; close water | FAIL — peeled_rinse: sensor_faucet_spout / ee_R_PGC300_0: gap -80.7 mm, penetration 80.7 mm | FAIL — peeled_rinse: sensor_faucet_spout / ee_R_PGC300_0: gap -80.7 mm, penetration 80.7 mm |
| potato_07 | Move clean vegetable to cutting board | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm |
| potato_08 | Pick up knife | FAIL — C04/pre_grasp: IK residual 33.2 mm; 7.7 deg | FAIL — C04/pre_grasp: IK residual 29.3 mm; 7.7 deg |
| potato_09 | Trim ends and create a flat support face | FAIL — first_stroke_start: prep_L_minus_beam / potato_box: gap 6.1 mm, penetration 0.0 mm | FAIL — first_stroke_start: IK residual 115.4 mm; 30.6 deg |
| potato_10 | Stabilise, feed and cut 5 mm slices | FAIL — first_stroke_start: lift_LD5_0053 / R_arm_AR4_0071_0: gap -50.3 mm, penetration 50.3 mm | FAIL — first_stroke_start: IK residual 115.4 mm; 30.6 deg |
| potato_11 | Push/scoop pieces into the ingredient bowl | FAIL — scoop_start: L_arm_AR4_0481_0 / R_arm_AR4_0421_0: gap -34.7 mm, penetration 34.7 mm | FAIL — scoop_start: IK residual 62.3 mm; 1.0 deg |
| potato_12 | Return knife between batches | FAIL — C05/knife_place: knife_dock_handle_land / prep_R_plus_pad: gap 9.999104829 mm, penetration 0.0 mm | FAIL — C05/knife_above_dock: IK residual 24.3 mm; 7.8 deg |
| potato_J03 | Rinse starch from slices or optional shreds and drain | FAIL — source_output_bowl_lift: IK residual 123.5 mm; 24.3 deg | FAIL — source_output_bowl_lift: IK residual 106.7 mm; 30.2 deg |
| potato_13 | Park finished bowl and reset the active station | FAIL — filled_bowl_grasp: lift_LD5_0323 / L_arm_AR4_0071_0: gap -39.4 mm, penetration 39.4 mm | FAIL — filled_bowl_grasp: IK residual 112.8 mm; 27.4 deg |
| greens_01 | Take the head from basket | FAIL — pre_grasp: basket_front / R_arm_AR4_0621_12: gap 0.5 mm, penetration 0.0 mm | FAIL — pre_grasp: IK residual 28.4 mm; 0.9 deg |
| greens_02 | Open cold water; park greens before operating control | FAIL — greens_bowl_park: prep_R_minus_pad / R_payload_greens_box: gap -6.2 mm, penetration 6.2 mm | FAIL — greens_bowl_park: prep_R_minus_pad / R_payload_greens_box: gap -6.2 mm, penetration 6.2 mm |
| greens_03 | Coarse rinse the head and root base | FAIL — root_base_rinse: sensor_faucet_spout / ee_R_PGC300_0: gap -80.7 mm, penetration 80.7 mm | FAIL — root_base_rinse: IK residual 97.5 mm; 30.3 deg |
| greens_04 | Trim root disk on dirty-prep area; park knife | FAIL — first_stroke_start: IK residual 23.3 mm; 6.5 deg | FAIL — first_stroke_start: IK residual 143.8 mm; 30.8 deg |
| greens_05 | Separate every stalk/leaf for access to basal creases | FAIL — leaf_pair_grasp: IK residual 12.5 mm; 3.1 deg | FAIL — leaf_pair_grasp: prep_R_minus_pad / R_payload_greens_box: gap -6.3 mm, penetration 6.3 mm |
| greens_06 | Soak, rub basal creases, lift and rinse in fresh water | FAIL — basal_crease_front: IK residual 124.2 mm; 4.8 deg | FAIL — basal_crease_front: IK residual 91.6 mm; 31.3 deg |
| greens_07 | Drain in handled colander, with gentle optional shake | FAIL — shake_left: IK residual 72.9 mm; 35.9 deg | FAIL — shake_left: IK residual 143.6 mm; 35.5 deg |
| greens_08 | Stop water and transfer drained greens to clean board | FAIL — grasp: prep_R_plus_pad / greens_box: gap -6.3 mm, penetration 6.3 mm | FAIL — pre_grasp: IK residual 105.8 mm; 27.9 deg |
| greens_09 | Split thick stalks and arrange a low bundle | FAIL — first_stroke_start: IK residual 59.6 mm; 15.7 deg | FAIL — first_stroke_start: IK residual 85.1 mm; 34.5 deg |
| greens_10 | Cut 40 mm sections | FAIL — first_stroke_start: lift_LD5_0053 / L_arm_AR4_0071_0: gap -50.7 mm, penetration 50.7 mm | FAIL — first_stroke_start: IK residual 72.9 mm; 45.1 deg |
| greens_11 | Scoop stalk and leaf sections into bowl | FAIL — scoop_start: lift_LD5_0053 / R_arm_AR4_0503_2: gap -19.6 mm, penetration 19.6 mm | FAIL — scoop_start: IK residual 75.6 mm; 0.5 deg |
| greens_12 | Return knife | FAIL — C05/knife_above_dock: carrier_14 / board_mat: gap 1.7 mm, penetration 0.0 mm | FAIL — C05/knife_above_dock: IK residual 32.1 mm; 8.6 deg |
| greens_13 | Park finished bowl and reset the active station | FAIL — filled_bowl_grasp: lift_LD5_0323 / L_arm_AR4_0071_0: gap -31.2 mm, penetration 31.2 mm | FAIL — filled_bowl_grasp: IK residual 107.5 mm; 27.4 deg |
| tomato_01 | Take vegetable from basket | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm | FAIL — pre_grasp: lift_LD5_0053 / R_arm_AR4_0503_2: gap -17.8 mm, penetration 17.8 mm |
| tomato_02 | Start cold water with vegetable parked | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm |
| tomato_03 | Rinse and rub every surface | FAIL — rinse_front: sensor_faucet_spout / ee_R_PGC300_0: gap -50.7 mm, penetration 50.7 mm | FAIL — rinse_front: lift_LD5_0070 / L_arm_AR4_0484_1: gap -80.2 mm, penetration 80.2 mm |
| tomato_04 | Drain and stop water; keep skin | FAIL — park_after_wash: colander_wall_14_box / ee_R_cable_jacket_23: gap -13.0 mm, penetration 13.0 mm | FAIL — park_after_wash: IK residual 113.4 mm; 41.9 deg |
| tomato_07 | Move clean vegetable to cutting board | FAIL — pre_grasp: ee_R_factory_slider_minus / ee_R_cable_jacket_0: gap 9.0 mm, penetration 0.0 mm | FAIL — pre_grasp: IK residual 61.9 mm; 41.1 deg |
| tomato_08 | Pick up knife | FAIL — C04/pre_grasp: carrier_14 / board_mat: gap 1.7 mm, penetration 0.0 mm | FAIL — C04/pre_grasp: IK residual 19.0 mm; 5.8 deg |
| tomato_09 | Halve tomato and remove hard stem core | FAIL — first_stroke_start: lift_LD5_0002 / L_arm_AR4_0627_0: gap -57.1 mm, penetration 57.1 mm | FAIL — first_stroke_start: IK residual 110.0 mm; 26.3 deg |
| tomato_10 | Cut each half into four attached-pulp wedges | FAIL — first_stroke_start: IK residual 60.1 mm; 16.6 deg | FAIL — first_stroke_start: IK residual 102.8 mm; 21.9 deg |
| tomato_11 | Push/scoop pieces into the ingredient bowl | FAIL — scoop_start: lift_LD5_0053 / R_arm_AR4_0072_0: gap -25.0 mm, penetration 25.0 mm | FAIL — scoop_start: IK residual 48.7 mm; 2.9 deg |
| tomato_12 | Return knife between batches | FAIL — C05/knife_above_dock: R_arm_AR4_0490_0 / R_arm_AR4_0701_2: gap -0.1 mm, penetration 0.1 mm | FAIL — C05/knife_above_dock: IK residual 72.1 mm; 16.9 deg |
| tomato_13 | Park finished bowl and reset the active station | FAIL — filled_bowl_grasp: L_arm_AR4_0270_0 / R_arm_AR4_0130_0: gap -44.3 mm, penetration 44.3 mm | FAIL — filled_bowl_grasp: IK residual 278.6 mm; 42.6 deg |

## Torque and dexterity

Worst reported ratios include failed/rejected configurations; they must not be read as a qualified operating posture.

| Kitchen | OK key poses | Worst nominal torque / continuous | Max cutting ratio 30 / 50 / 80 N | Minimum active joint-limit distance | Minimum scaled manipulability |
|---|---:|---:|---|---:|---:|
| kitchen_galley | 45/402 | 1.354 | 0.947 / 0.947 / 1.201 | 0.0000° | 0.00234 |
| kitchen_l | 50/402 | 2.479 | 0.727 / 0.727 / 1.095 | 0.0000° | 0.00399 |

## Changes tried and final common candidate

Preference order was market tools/fixtures, passive fabricated grips/storage, then robot fingers and link lengths. Earlier tiers use one independent blocking witness per required phase to reject a candidate; their nominal successes are not phase passes. Trials are retained under results/trials. The final tier evaluates every pose and neighbour. Stronger actuators were not selected simply to hide geometry or delicate-food failures; the existing braked packets are retained with their BOM continuous ratings.

| Change | Geometry / mass | Source and decision |
|---|---|---|
| M01 Ideal Standard Sensorflow A7559AA | 1.680000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.idealstandard.de/produkte/a7559?c=AA); proposed, complete-chain candidate rejected |
| M02 Victorinox Swiss Classic Chinese-style chef knife 6.8561.18G | 0.198000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.victorinox.com/en-TW/Products/Cutlery/Chef%27s-Knives/Swiss-Classic-Chinese-Style-Chef%E2%80%99s-Knife/p/6.8561.18G); proposed, complete-chain candidate rejected |
| M03 OXO Good Grips Y peeler 21081 | 0.079000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.oxo.de.com/reiben-und-hobel/y-sparschaler/); proposed, complete-chain candidate rejected |
| M04 IKEA KLOCKREN handled colander | 0.440000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.ikea.com/gb/en/p/klockren-colander-50449177/); proposed, complete-chain candidate rejected |
| M05 BLANDA BLANK wash bowl plus four separate ingredient bowls | 1.450000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.ikea.com/sg/en/p/blanda-blank-serving-bowl-stainless-steel-40179699/); proposed, complete-chain candidate rejected |
| F01 Stable preparation supports and station layout | 3.114000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](../../sim/t03/cook_ref/prep_spec.json); proposed, complete-chain candidate rejected |
| F02 Through-bolted metal faucet riser | 1.000000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.idealstandard.de/produkte/a7559?c=AA); proposed, complete-chain candidate rejected |
| F03 Metal-backed keyed sleeves and rim cuffs | 1.520000 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.aalco.co.uk/datasheets/Aluminium-Alloy-6061-T6-Extrusions_145.ashx); proposed, complete-chain candidate rejected |
| F04 Raised horizontal knife holder | 1.925840 kg; robot Δ +0.000000 kg; geometry in changes.json | [Source](https://www.aalco.co.uk/datasheets/Aluminium-Alloy-6061-T6-Extrusions_145.ashx); proposed, complete-chain candidate rejected |
| R01 Asymmetric machined fingertips | 0.430000 kg; robot Δ +0.430000 kg; geometry in changes.json | [Source](https://www.aalco.co.uk/datasheets/Aluminium-Alloy-6061-T6-Extrusions_145.ashx); proposed, complete-chain candidate rejected |
| R02 Extend existing six x arm offsets by 35 percent | 0.433079 kg; robot Δ +0.433079 kg; geometry in changes.json | [Source](../../cad/arms_d04/parts_manifest.json); proposed, complete-chain candidate rejected |

The [Sensorflow page](https://www.idealstandard.de/produkte/a7559?c=AA) supplies 71.5×180×170 mm and 1.68 kg; its [manual](https://www.idealstandard.de/dfsmedia/9e07a8a15f014cab9f19c3786cffba89/266876-source/options/download/is-sensorflow-multiproduct-iguide-nn-a7558a7559a868896r3) supplies adjustable presence sensing. The [Victorinox page](https://www.victorinox.com/en-TW/Products/Cutlery/Chef%27s-Knives/Swiss-Classic-Chinese-Style-Chef%E2%80%99s-Knife/p/6.8561.18G) supplies 309×85×18 mm and 0.198 kg. [OXO](https://www.oxo.de.com/reiben-und-hobel/y-sparschaler/) lists 127×76×25 mm and 79 g packaged; the model deliberately uses that gross mass. [KLOCKREN](https://www.ikea.com/gb/en/p/klockren-colander-50449177/) supplies 240 mm diameter and 300 mm packaged span; [Estonia's listing](https://www.ikea.ee/et/products/toiduvalmistamine/koogitarvikud/koogitarvikud/klockren-kurnsoel-art-50449177) gives 0.42 kg net /0.44 kg gross. Expanded colander/base and grip cross-sections are assumptions recorded separately. [20 cm bowls](https://www.ikea.com/gb/en/p/blanda-blank-serving-bowl-stainless-steel-20057255/) and [28 cm wash bowl](https://www.ikea.com/sg/en/p/blanda-blank-serving-bowl-stainless-steel-40179699/) use conservative packaged masses 0.22/0.57 kg.

[Aalco 6061-T6 data](https://www.aalco.co.uk/datasheets/Aluminium-Alloy-6061-T6-Extrusions_145.ashx) gives density 2700 kg/m³, modulus 70 GPa and minimum yield 240 MPa. The 4 mm U backers have 93.75 MPa conservative factored web stress for a 400 N bearing design; the narrow left finger tip's combined factored screen is 232.05 MPa. That small residual stress margin is a reason to require a released machined CAD check before construction. Printed PC skins follow [r05 fabrication](../r05/fabrication.md): ≥2.4 mm walls, dry PC, through-metal bolts and compression sleeves. No printed hot-zone part, counterbalance or new active robot mechanism is introduced.

## Evidence limits and mobility handoff

The final candidate is rejected; it is not a build-ready arm/base/gripper specification. Geometry uses conservative commercial envelopes and explicit specimen assumptions for bowl bases, handle sections, sensor field and food shape. Rectangular food envelopes are a pose/contact proxy; their inferred stable facets do not certify round produce against rolling or fluid/leaf deformation. Static container water is retained as a 1.5 kg worst payload, but fluid redistribution and food retention at drain angles are not a complete spill model. No empirical dirt-removal, bruising, peel completion or 98% transfer claim follows from these poses. Numerical failures remain FAIL; these modelling limits are not replaced by an indeterminate verdict.

At completion I read mobility/results/mobility.json and audit_v2_summary.json (snapshots and hashes included in keyposes.json). Mobility's shortened-base candidate is not adopted here: this role was instructed to use the current base for pose analysis. The original base cannot turn freely in the 1.20 m aisle; independent key stances do not imply a traversable sequence. Mobility qualification and software motion planning are separate later work, and neither suppresses the prep pose checks.

## Artifacts

- [Per-phase and per-pose results](../../sim/t03/keypose_cook/results/keyposes.json)
- [Geometry, mass and source ledger](../../sim/t03/keypose_cook/results/changes.json)
- [Galley washing](../../sim/t03/keypose_cook/keyframes/kitchen_galley_washing.png) · [Galley cutting](../../sim/t03/keypose_cook/keyframes/kitchen_galley_cutting.png)
- [L washing](../../sim/t03/keypose_cook/keyframes/kitchen_l_washing.png) · [L cutting](../../sim/t03/keypose_cook/keyframes/kitchen_l_cutting.png)

PNG views are CPU-only, 1400×1000. Red geometry identifies a forbidden contact at the illustrated nominal pose. Every image carries its actual verdict and requested grip markers; images of failed poses are not illustrations of an approved robot.
Close-up panels ghost fixtures and omit the lift/base to expose the actual hands; the whole-body panels retain those collision obstacles.
