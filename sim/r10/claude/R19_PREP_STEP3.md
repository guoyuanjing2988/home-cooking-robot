# R19 prep audit step 3: basket, soak tub and output-transfer sets (GitHub #38, 2026-10-13)

**Scope.** The most frequent missing prep sets of `R19_PREP_AUDIT.md` §6.2, in today's prep layout (`kitchen19.LAYOUT`, `R19_PREP_LAYOUT.md` §9), checked with the true-geometry arm `ARM=ur5e_enc2_pgc` (DECISIONS 2026-10-13):
- BASKET (18 uses per 3 meals): fetch the wash basket, rinse it under the faucet, drain and shake, pour or set it down;
- SOAK (7): fill the tub at the tap, put the basket in and lift it out, empty the tub at the sink;
- OUTPUT_XFER (14): the lever plate's cut pieces into a bowl; the slicer's output bowl to the staging spot.

**Labels** (as `R19_PREP_LAYOUT.md`)
- **[checked]**: a whole action planned with the `r17chain.py` method (unchanged checker), and every state re-checked at ≤ 4 mm with the full checker (`r19prep_verify.py`). Smoke settings (1 seed), not the controller's full runs.
- **[screen]**: the fast checker on stored states (`r19prep3_screen.py`). A screen, not a check.
- **[probe]**: 96-start collision-aware IK at one pose.
- **[est]**: an estimate, with its basis stated. **[O]**: a search-result value, not read in the primary document.

**Rules (unchanged):**
- gaps: 10 mm robot ↔ environment, 5 mm gripper/held ↔ environment;
- states ≤ 4 mm apart;
- contact windows only on the ≤ 50 mm straight grasp approach / release retreat;
- no gate loosened, no force tuned. No process force is applied: rinsing, soaking and pouring are not simulated.

---

## 1. Answer first

**Six sets pass [checked]** (`ur5e_enc2_pgc`, every state re-checked at ≤ 4 mm, 0 hits). The basket pour and the slicer-bowl transfer are **not closed**.

| Set (ACT=) | What it does | Time (r17 timing), of which dwell [est] | ≤ 4 mm re-check: states (play + approaches), hits | Min reserve (re-check) | Max PGC jaw moment (held kg) | Max joint-load ratio |
|---|---|---|---|---|---|---|
| **basket** BASKET_WASH | basket out of the tub → under the running outlet (3 × 3 s, ±4 cm) → drain 4 s + 3 shakes (±15 mm) → back into the tub | **34.6 s**, 13 s | 3,535 + 85, **0** | 2.01 mm | **1.81 N·m** (1.15 kg = basket 0.35 + food 0.50 + standing water 0.30) | 0.32 |
| **tubfill** SOAK 1 | empty tub from its spot → under the outlet, filled (27 s) → back, full | **45.3 s**, 27 s | 2,813 + 85, **0** (also 0 in the final-layout scene) | 2.19 mm | **4.83 N·m** (2.78 kg = tub 0.50 + 2.28 kg water) | **0.47** |
| **soak** SOAK 2 | basket from the front spot → into the filled tub (10 s placeholder; release/regrasp in the tub checked) → lifted, drained 4 s → back | **26.9 s**, 14 s | 2,138 + 163, **0** | 2.00 mm | 1.81 N·m (1.15 kg while draining) | 0.34 |
| **tubempty** SOAK 3 | full tub → over the left half of the sink → rolled 90° about its handle (3 s) → back, empty | **22.5 s**, 3 s | 3,977 + 85, **0** | 2.06 mm | **4.84 N·m** (2.78 kg) | 0.46 |
| **ctray** OUTPUT_XFER | lever catch tray (cut pieces) pulled out 15 cm → over the staging bowl on plating spot 2 → rolled −120° (2 s) → back, slid in | **38.5 s**, 2 s | 3,506 + 182, **0** | 2.00 mm | 0.34 N·m (0.30 kg) | 0.40 |
| **bascarrot** piece into the basket | carrot off the rib tray → upright → lowered 20 mm into the basket on the front spot → released | **14.8 s**, 0 s | 2,647 + 159, **0** | 3.00 mm | ≈ 0 (food at the TCP) | 0.39 |

- **Not counted in the times:** the faucet lever opening/closing, the checked R17 action, 3.5 s each. All the sets' scenes have the lever closed and open (union), so they work with the faucet in either state.
- **Real soak times** (clam purge, the broccoli salt soak, potato-starch rinses) are minutes long and are not sourced. The arm lets go of the basket in the tub and does other work. That release and regrasp is a checked approach of the soak set.
- **Timing** is r17 timing: TCP 0.10 m/s, 45°/s, joints 60°/s, cart 0.25 m/s, no acceleration limit. R19 smooth found such paths 20–50 % slower with acceleration limits.
- **Compared with the audit's estimates [est, `R19_PREP_AUDIT.md` §6.3]:**
  - basket: audit 40–60 s; here 34.6 s + 7 s faucet;
  - soak: none given; here ≈ 95 s of arm time per soak cycle (fill + in/out + empty) plus the soak itself, unattended;
  - output transfer: audit 15–20 s; here **38.5 s**.

**Not closed**
1. **Basket pour** into a bowl (BASKET_POUR, `ACT=baspour`): about 30 smoke configurations, none closed. The carrot drop shows the other half of the step-3 basket list ("put pieces in it"); the wash set ends with the basket set down, which the task allows.
   - **Into a bowl on T1** (the cups plan's strip behind the plating spots) or **on plating spot 2:** the carry to the right of the sink and the 110–130° roll fail. The causes are self contact (upper arm vs wrist 2; forearm vs the gripper) and the right upper-cabinet door.
   - **Closest attempt:** a local pour into a prep bowl on the front spot. The pick side joins at 3°, but the return to the tub found no join (§4.4).
2. **Slicer output bowl → staging spot.** The out bowl sits at (−1.69, 0.50), under the upper cabinet and 9 mm under the slicer spout. With a strut and knob added it is unreachable: 0/96 starts at its seat and 0/96 slid 10 cm right [probe]. It cannot slide forward (the slicer body) or rise (the spout). R19 #4 already found no back spot reachable. Options in §5.
3. **A staging spot for cooking.** The one spot where a pour closed, plating spot 2, is swept by both stored wok-plating paths [screen]. It is usable only before the first plating. T1 did not close in smoke runs.

---

## 2. Hardware and layout (design proposals; all sizes and masses [est])

### 2.1 Objects (`kitchen19p3.py`)

| Object | Size | Mass [est] | Grasp |
|---|---|---|---|
| **Wash basket** (R13 side-handle basket) | Ø200 × 100 mm, 69 drain holes Ø6 (R13 CAD) | 0.35 kg | Keyed 30 mm knob on a side strut, taken **end-on along the handle**, jaws across it. Knob printed **pitched 30°**, so the gripper comes from above and outside. |
| **Soak tub** | Round stainless basin, inner Ø230 × 75 mm. A GN 1/3 pan (the audit's proposal) is 176 mm wide and cannot take the Ø200 basket. | 0.50 kg | Same knob, but on a **low side bracket** (knob top 20 mm under the rim, pitched 15°). A nested basket's strut and fingers then pass 25+ mm over it. Probe: with the knob at the rim, the basket strut hit the tub knob (0/96). |
| **Staging / prep bowl** | Ø200 × 90 mm, strut + knob | 0.30 kg | Knob |
| **Lever catch tray** | 110 × 120 × 40 mm open tray under the AY-403 blade plate; front lug + knob. It catches the wedges and keeps them out of the base. | 0.15 kg | Knob from the front, jaws horizontal |

**Changes against the R13 CAD basket**
- The knob centre is **60 mm** outside the wall, against 35 mm. The PGC fingertips reach 30 mm past the TCP, and the R12 D fingers are 13 mm thick: with the R13 knob, the open finger would stand in or 5 mm from the wall.
- The keyed V grooves move to the knob's side faces.
- The knob is pitched 30°. With a level end-on grasp, the elbow entered the closed upper-cabinet door over the tub spot in every smoke run.
- The pour axis is the same as R13: the handle axis.

**Grasp choice by the R13 catalog** (`README_R10.md` R13, DECISIONS R13)
- Bulk and leafy items go in the side-handle basket.
- Cut pieces are too many and too small for pinch or fork, so both outputs travel **in a container gripped by a keyed knob**: the catch tray for the lever's wedges, and the out bowl for the slicer.
- The carrot is pinched (P1/P2, μ 0.15 ✓) and turned upright, as in the checked chute drop.

### 2.2 Prep-time layout (`r19prep3_actions.py`)
The work spot of `kitchen19.LAYOUT` still holds **one fetched item at a time**: the lever base, the cold box, or the **soak set**.

| Spot | Pose | Use | Screen against the stored cooking motion (`ur5e_enc2_pgc`, PY=.15 hub) |
|---|---|---|---|
| **Tub** (basket nested when idle) | (−0.84, 0.39), handle yaw −20° | home of the soak set | **6 chains + approaches, 2,003 states: 0 hits.** No hub edge flagged (4/106 segments flagged, all wok chains; replayed clean). It may stay out during cooking [screen]. |
| **Front spot** (basket, or a prep bowl) | (−0.86, 0.15), yaw −20° | only while the tub is filled, emptied or soaking; the carrot drop | **Hit** by both wok sink trips: upper arm 8.3–8.8 mm from the knob against 10 mm. The hub edge LEV_O→H_SPAT is clean (1,720 states). **Prep-time only**: the basket goes back into the tub before any wok trip. |
| **Staging bowl** | plating spot 2 (0.17, 0.15), knob toward −x | target of the catch-tray pour | **Hit** by both wok plating paths (first pair: upper arm vs the bowl wall, 8.4 mm). 11 flagged hub edges, 18,794 states: 0 hits. **Prep-time only**, i.e. before the first plating. |
| **Catch tray** | seated under the lever blade plate at the work spot | lever output | 6 chains: **0 hits** (inside the lever base's screened envelope anyway) |

**Why these spots**
- **Reachable [probe]:**
  - basket under the outlet: 16–45 good starts at every handle yaw tried except +45°;
  - basket nested in the tub: 8 good starts;
  - tub at the tap: 9–37;
  - catch tray: seat 3, pulled out 33.
- **Tub depth and the wall socket:** at y 0.40 the tub's back rim passed 5 mm under the wall-socket box (`outlet_access_0`, z 0.97) when lifted, so the tub moved to 0.39.
- **The front spot** is the only place by the sink with 15–20 mm clearance to the tub, the counter end and the sink rim.
- **Handle direction:** the handle points toward the sink, 20° toward the robot. The tub-fill posture passed this way; with the handle toward the robot (−90°) the lane joins kept landing in other IK branches (§4.3).

---

## 3. The sets (keyframes; `r19prep3_actions.py`, run by `r19prepchain.py`)
Common to all sets:
- object frame: the bottom centre of the container;
- the object moves ≤ 1 cm / 2° per step;
- each grasp and release is a 50 mm approach with the object in the world: 8 mm seat lift, then a retreat along the approach axis.

**Loads** are set per keyframe (`load`, `com`).

**Water** is ρ = 998.2 kg/m³ at 20 °C [O: 0.99821 g/cm³, [LibreTexts, Properties of Water](https://chem.libretexts.org/Bookshelves/Ancillary_Materials/Reference/Reference_Tables/Solvents/S2%3A_Properties_of_Water)]:
- tub water: 55 mm deep in Ø230 = **2.28 L = 2.28 kg** [est depth];
- standing water in the basket under the stream: 0.30 kg, i.e. 10 mm over the floor (see §3.1).

**Fill time:** **27 s [est]** for 2.28 L. PUB allows only 2-tick and better taps since 2019. Sink taps with 2 ticks run at > 4–6 L/min, and 3-tick taps at ≤ 4 L/min ([O, PUB WELS requirement](https://info.pub.gov.sg/Documents/WELS_Requirement.pdf)). At 4–6 L/min the fill takes 23–34 s. The user's tap is not measured.

### 3.1 BASKET_WASH (`ACT=basket`)
**Keyframes:**
- pick: nested in the tub, 8 mm; anchor;
- lifted 5 cm;
- out of the tub (+11 cm);
- **lane** (−0.62, 0.38, 0.98), the meet;
- in front of the stream (−0.40, 0.27, 0.98);
- **under the tap**, anchor: floor centre (−0.40, 0.33, 0.94). The rim is 6 cm under the spout, and the basket is 25 mm from the closed lever tip;
- rinse at +4 cm and −4 cm (3 s each [est]);
- drain 6 cm forward / 4 cm up (4 s [est]);
- 3 shakes of 15 mm;
- lane (meet);
- **over the tub** (anchor);
- lowered; set down 8 mm (release).

**Result:**
- anchors at carts −0.47 / −0.21 / −0.44;
- joins 53° and 58°;
- the largest joint step while following is 8.7° per 1 cm step, at the tap: a near-singular wrist passage under the 10° rule.

**Water in the basket:**
- The 69 Ø6 holes drain about **31 L/min** at a 10 mm head (Torricelli, Cd 0.6 [est]). The tap delivers ≤ 6–8 L/min [O], so the standing water stays well under 10 mm. The 0.30 kg used is conservative.
- **Upper bound,** basket full to the rim with the holes blocked: 3.2 kg at 0.16 m = **5.0 N·m**, still under the PGC's 7 N·m.

### 3.2 SOAK (`ACT=tubfill`, `soak`, `tubempty`)

**Tub fill** (anchors: pick, under the tap, over its spot)
- lane (−0.62, 0.38, 0.97);
- in front of the stream;
- **under the tap** (−0.40, 0.31, 0.95), 27 s fill [est];
- out of the stream;
- lane; set down.

The full tub (2.78 kg) is carried level with **20 mm freeboard**. Slosh is not simulated.

**Soak**
- One anchor, over the tub; every other keyframe has a free cart. That one IK solution is followed both ways, so there is no join.
- Sequence:
  - front-spot pick;
  - up 12 cm;
  - lane (−0.79, 0.27, 1.00), ≥ 45 mm over the tub rim;
  - over the tub;
  - lowered into the water, 8 mm over the tub floor (10 s placeholder);
  - lifted 9 cm, drain 4 s [est];
  - lane; front spot, set down.
- The three-anchor version (`SOAK3A=1`) did not join in smoke runs.

**Tub empty** (anchors: pick, over the sink, over its spot)
- lane;
- in front of the outlet;
- **over the sink** (−0.55, 0.31, 0.95);
- **rolled +90°** about the handle axis, 3 s, so the back side goes down and the water runs out toward the wall into the sink;
- level;
- back.

**What did not work for the tub empty**
- The roll **under the outlet** (x −0.40): −90° lifts the tub's back side toward the spout. With +60/90/120° the forearm came within the gap of the right upper-cabinet door on the branch that joins.
- At 60°, part of the water would stay in the tub [est].

**Jaw moment during emptying:** 4.84 N·m at the keyframes. Water shifting toward the low rim before it leaves could move the CoM about 0.10 m sideways, giving **≈ 5.5 N·m [est]**, under 7 N·m. Slosh is not simulated.

### 3.3 OUTPUT_XFER: lever catch tray (`ACT=ctray`)
**Keyframes:**
- pick, seated, 8 mm;
- **raised to 18 mm** over the base plate (the tray top is then 16 mm under the blade plate);
- pulled out 15 cm toward the robot;
- lifted;
- lane (−0.40, 0.08, 1.08) (meet);
- lane (0.0, 0.06, 1.04);
- **over the staging bowl** (anchor), knob 10 cm above the rim;
- rolled −120° about the lug axis, 2 s;
- level; back; slid in at 18 mm; set down 8 mm.

**Result:**
- joins 29° and 2°;
- **38.5 s**, longer than the audit's 15–20 s estimate, because the bowl is 1.0 m away;
- a staging bowl next to the lever would make it shorter, but none fits there in the sim (§5).

### 3.4 Piece into the basket (`ACT=bascarrot`)
**Keyframes:**
- the carrot set's tray pick (cart −1.15);
- lane (−1.05, 0.06, 1.12);
- turned upright in front of the basket (approach turned 30°, as the chute set);
- **over the basket** (anchor);
- lowered so that its bottom is 20 mm under the rim;
- released. It drops about 80 mm onto the basket floor, as in the chute drop; the drop damage is not sourced.

**Result:**
- join 20°;
- largest joint step 9.6° per 1 cm step, a near-singular wrist passage under the 10° rule.

Greens bunches (R13: base pinch for chives, spinach and bok choy; scallion only at μ ≥ 0.3) use the same drop. They are not modelled. Most bulk items are loaded into the basket by the user (R13 interface, accepted 2026-10-11).

---

## 4. What failed on the way (smoke runs; `results/r19/prep3/explore/`, probes in `results/r19/prep3/probe_*.json`)
1. **MuJoCo misreads gaps over box edges (a checker false alarm, not loosened).**
   - A held tub 8 mm over the seam between two counter boxes (x −0.975): MuJoCo reported 3.0 mm with the floor as a cylinder, 2.2 mm as a mesh prism, and 4.8 mm for a wall box mesh. The exact bound is 8.0 mm.
   - The same happened for the catch tray sliding 8 mm over the base plate's front edge.
   - The checker's literal-contact test flags these, so the designs avoid them:
     - footprints 14 mm clear of the counter seams (tub at x −0.84);
     - the catch tray slides 18 mm over the plate edge (MuJoCo reads about 0.3× the true gap there).
   - The R11 box-mesh rule makes face-to-face gaps exact, but not these edge cases. The step-3 parts follow it: boxes as 8-vertex meshes and cylinders as circumscribed 16-gon prisms, held and in the world (`kitchen19p3.mesh_held`).
2. **The cart had to stay on one side of the object.**
   - Handle toward the sink (yaw 0) with the lane at the tub's front: the pick reaches left, the tap reaches right, and the meet joins needed 200–310° (other IK branches).
   - Handle toward the robot (yaw −90°): the anchors all followed, but every join was in another branch.
   - Fixed by:
     - the handle at −20° with the pitched knob;
     - the same intermediate pose on both sides of the tap;
     - free-cart shake frames. An 'A' (anchor-cart) frame after a free-cart move snaps the cart back.
3. **The elbow and the upper-cabinet doors.**
   - With a level knob grasp, the tub and basket picks at the back of the work spot hit the closed doors (x < −0.70, z ≥ 1.35).
   - Pitching the grasp (basket 30°, tub 15°) cleared them, as the 30° rinse pitch did in R19 #4.
4. **Basket pour (open).** Tried:
   - T1 with handle yaws −45/−90/−135/180° and rolls ±110/±130°;
   - plating spot 2 with the same;
   - a local prep bowl on the front spot.

   Failures: the carry to the right of the sink (forearm vs the right upper-cabinet door, the basket content vs the spout), the roll (upper arm vs wrist 2), and branch-mismatched joins. The planner (`PLAN=1`) does not fit in a 5-minute smoke run.
5. **Basket back spot** (behind the work spot, under the cabinet): 0–3 good starts out of 96 [probe]. Rejected in favour of the front spot.
6. **Second-round runs** on the shared machine (about 84 other Python processes) were 1.5–2× slower. The final-layout tub fill could not be re-planned within 5 min. Its stored path was instead re-checked at ≤ 4 mm in the final scene (`chain_tubfill_t15fin`, 0 hits).

---

## 5. Open items and options
- **Slicer output.** Its bowl is unreachable at the R19 #4 slicer spot. Options:
  - (a) a printed side drawer under the spout that slides the bowl out toward +x;
  - (b) a short printed chute on the spout that discharges forward into a bowl in the open strip;
  - (c) put the slicer on the user's L-shaped sink leg (#11), where the layout differs.

  Each needs a reach probe and a screen; none is modelled.
- **A cooking-time staging spot** for the cut food: plating spot 2 is swept by the wok plating, and T1 did not close. This goes with the cooking library's CUP_POUR family (R19 cups: the cart caddy T2L is the spot to pursue).
- **Basket pour:** controller exploration lane in §6.
- **Physics:** wet friction (`dyn.py`), slosh of the 2.28 kg water, and the pour itself (R13 bench poured 100 % at 130° with a floating gripper; here the roll is 90° for the tub and −120° for the tray) are **not simulated**. A 60–90° tray roll may leave pieces behind [est].
- **Hub spurs** from the set endpoints, **step 4** (tool drawer, plate swap, finger swap) and **step 5** (#35) are not done.
- **Not sourced:**
  - soak, purge, drain and rinse times;
  - the faucet flow of the user's tap;
  - all masses.

---

## 6. Commands for the controller (`ur5e_enc2_pgc`)
The defaults of `r19prep3_actions.py` are the passing smoke settings. With `SEEDS=1`:
- the soak, tub-empty and catch-tray defaults were re-run and reproduce the passing runs exactly (identical plays);
- the basket and carrot sets did not change after their passing runs;
- the tub fill was re-checked in the final scene.

```
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A="ARM=ur5e_enc2_pgc"
# lane 1: full runs of the six passing sets, then the <= 4 mm re-check (smoke runs took 1-4 min each with SEEDS=1; expect ~5-15 min each)
for a in basket tubfill tubempty ctray bascarrot; do $PY r19prepchain.py ACT=$a SEEDS=3 TRIES=12 KEEP=4 TAG=full $A; done
$PY r19prepchain.py ACT=soak SEEDS=3 TRIES=12 KEEP=1 TAG=full $A          # one anchor: KEEP=1
for a in basket tubfill tubempty ctray bascarrot soak; do $PY r19prep_verify.py FILE=results/r19/prep/chain_${a}_full_ur5e_enc2_pgc.json NPROC=16; done
# if a full run picks another candidate that fails, the smoke settings reproduce the checked results:
#  basket: SEEDS=1 TRIES=8 KEEP=2 | tubfill: SEEDS=1 TRIES=10 KEEP=3 | soak: SEEDS=1 TRIES=10 KEEP=1 | tubempty: SEEDS=1 TRIES=10 KEEP=3
#  ctray: SEEDS=1 TRIES=8 KEEP=2 | bascarrot: SEEDS=1 TRIES=8 KEEP=2
# lane 2 (exploration, open): the basket pour, with the RRT planner for blocked joins (each may take 10-20 min)
$PY r19prepchain.py ACT=baspour STG=-0.86,.15,-20 PYAW=-20 PLANE1=-0.72,.30,1.02 PLANE1B=-0.72,.30,1.02 PLANE=-0.72,.30,1.02 MYAW=-20 POURDEG=-130 PKZ=.15 SEEDS=3 TRIES=12 KEEP=4 PLAN=1 PLAN_S=120 TAG=explore_front $A
$PY r19prepchain.py ACT=baspour PLANE1=-0.62,.38,.98 PLANE1B=-0.40,.27,.98 PLANE=0.0,.06,1.06 PKZ=.17 SEEDS=3 TRIES=12 KEEP=4 PLAN=1 PLAN_S=120 TAG=explore_p2 $A
# lane 3 (done here; to repeat): screen of the step-3 spots against the 6 chains and the PY=.15 hub
$PY r19prep3_screen.py MODE=screen $A ; $PY r19prep3_screen.py MODE=replay NPAR=17 $A
```

---

## 7. Files and honesty notes

**New files**
- `kitchen19p3.py`: objects, pitched-knob variants, and the box/cylinder → mesh rule for the step-3 parts.
- `r19prep3_actions.py`: keyframes and the prep-time layout.
- `r19prep3_probe.py`: reach probes.
- `r19prep3_screen.py`: screen and replay, writing only to `results/r19/prep3/`.
- This file.

**Results**
- `results/r19/prep/chain_{basket_y20p30, tubfill_t15, tubfill_t15fin, soak_so1, tubempty_ex2, ctray_cq1, bascarrot_bc1}_ur5e_enc2_pgc.json`, each with its `_verify4mm.json`.
- `results/r19/prep3/`:
  - `screen.json`, `replay_*.json`;
  - `probe_*.json`. Probes up to round 5 used intermediate geometry: a Ø220 basket, an unpitched knob, a knob at the rim of the tub;
  - `explore/` (62 smoke results, plus the press regression run).

**Edited files** (backups `*.bak_r19p3`; the R19 #4 defaults and results are unchanged)
- `r19prepchain.py`:
  - imports the step-3 modules;
  - dispatches the new ACTs;
  - per-keyframe load in `load()`;
  - the mesh rule for `R_gripper_p3_*` / `p3_*` parts only.
- `r19prep_verify.py`:
  - registers the step-3 objects;
  - the same mesh rule.
- **Regression:** `ACT=press` with its stored arguments reproduces `chain_press_r2_ur5e_enc2_pgc.json` exactly (play, loads, 102.5 N push).

**Honesty notes**
- **Smoke settings only.** Every pass is a single-seed smoke run, with every state re-checked at ≤ 4 mm. The full runs (lane 1) are the controller's.
- **Screens.** The screens are screen-level (fast checker, stored states). The hits found are real arm–fixture proximities below the 10 mm gate (8.3–8.8 mm).
- **Single anchor.** The soak set uses one anchor followed both ways. That is the same method as the other sets, without a join.
- **Near-singular wrist passages.** The basket wash (8.7°/step) and the carrot drop (9.6°/step) have them. Both are inside the 10° rule and fully re-checked. They would be slow under real acceleration limits.
- **Estimates.** Masses, the water depth, all dwell times, the 0.30 kg standing water and the water-shift moment are estimates [est]. The water density and the PUB tap ratings are search-result values [O].
