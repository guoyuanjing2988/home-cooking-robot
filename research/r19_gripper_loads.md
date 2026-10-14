# R19 gripper loads: PGC-140-50 moment margin, stir jams, fatigue, keyed wok coupling (GitHub #16, 2026-10-14)

Labels:
- **[S]** sourced (repo file:line, or a URL read today);
- **[M]** measured in the repo's own sim results (file given);
- **[E]** my estimate or inference (basis given).

Scope: a desk study. I ran no simulation and edited no other file. I read the JSON results with short Python scripts.
"Moment at the PGC" in the repo means the moment of the held load about the **TCP site `R_prep`**, which is the held item's centre between the pads (`sim/r10/claude/r17chain.py:259`, `fingers.py:4-7`) [S].

## Answer first

1. **The 6.47 N·m wok number is a worst-orientation static moment about the TCP.** DH never says where its 7 N·m is referenced.
   - The wok load is 2.95 kg with its CoG at (54, −25, 215) mm in the TCP frame, so |r| = 223.5 mm and 2.95 × 9.81 × 0.2235 = 6.47 N·m (`results/r19/fr5/payload_fr5_j6_pgc_sp20.json`) [M].
   - Inertia adds nothing: the dynamic peak is also 6.467 N·m (`R19_SMOOTH.md:211-218`) [M].
   - **If DH's reference is the housing face** (35 mm behind the TCP, `fingers.py:6`), the worst moment becomes **6.78 N·m (97 %)**. At the jaw guides, about 72 mm behind, it becomes **7.27 N·m (104 %)** [E, vector arithmetic on the [M] CoG].
   - The component about the approach axis, **6.27 N·m**, does not depend on this shift.
   - **Not modelled:** food sliding to the lip during the 90° tip. At 1.15 kg it can move the moment by up to about ±1.9 N·m [E]. The sign has not been checked.
   - **Verdict:** the plating margin is between +8 % and −4 % before slosh. It is not a rated margin.
2. **The stir jam is not a rare corner case in the rigid-dice sim.**
   - On seeds 1–8, every 12 s run on every driver has a single-sample grip-moment peak above 7 N·m (9–367 N·m) [M].
   - The adopted spill-fix cycles have peaks above 50 N·m in 3 of 8 runs per arm. Seed 8 has a sustained p95 of 8.3 N·m (UR5e) and 17.3 N·m (FR5) (`results/r19/stir/spill/stir2_nw_*`) [M].
   - Scaled to about 82 strokes per meal, that is several hard jams per meal: an upper bound from rigid dice and a stiff weld [E].
   - The jaws must not be the load path for this.
3. **Recommended fix, in order of value:**
   - **(a) Palm key.** Fixed tapered pins on the flange adapter carry the wok and spatula moments, and the jaws only lock the block (`research/r19_arm_hand_cost.md:218-235`) [S]. This removes the reference-point question for the two worst loads.
   - **(b) Self-resetting ball-detent breakaway in the spatula block, at 5 N·m without the key.** It carries a magnet, and a Hall sensor on the adapter reads it as a jam signal, with no tool wiring.
   - **(c) Stall response (#26).** On a jam signal or the arm's force signal: stop, back off 10 mm and up 20 mm, re-enter, with at most 2 retries. Then go to half power and hold.
   - **(d) Clamp-on PEEK-class rim collar.** It keys the wok's handle stub, so nothing is cut into the glass-ceramic bowl.
   - **(e) Grip block moved about 40 mm toward the wok axis**, if the plume and temperature allow it: 6.47 → 5.36 N·m [E].
   - Lower plating tilt rates do **not** change the static peak. They only limit slosh.
4. **Fatigue.**
   - Duty is about 30k stir strokes a year at one meal a day, or 60k at two, so 0.3–0.6 M over 10 years. On top come about 1.5k loaded wok lifts a year [S, issue #16 / `r19_system_cost.md:116-126`].
   - Printed PETG must not carry the wok or spatula moment, and must not sit on the hot block: its HDT is 68 °C [S], against a block estimated at 60–110 °C (#15) [E].
   - Use 304 stainless or hard-anodised 6061 for the blocks and the palm key. Use PA12-CF / PAHT-CF or aluminium for wok and spatula fingers. Keep PETG/TPU for cold food fingers, as consumables.
5. **Decisions needed:** palm key yes/no; the breakaway setting; the rim collar instead of a bowl slot; whether to ask DH (the questions are drafted below, not sent).

## 1. Ratings

### 1.1 DH PGC-140-50 [S]

| Item | Value | Source |
|---|---|---|
| Gripping force per jaw | 40–140 N | DH PGC catalog page via Neobotix PDF (read today): https://www.neobotix-robots.com/fileadmin/user_upload/PGC-Gripper_Datasheet.pdf |
| Stroke | 50 mm | same |
| Recommended workpiece | 3 kg, "depends on the shape of the grasping object, the material and friction of the contact surface, and the acceleration of the motion" | same |
| Vertical maximum force Fz | 300 N | same |
| Allowable moment Mx / My / Mz | 7 / 7 / 7 N·m | same; PGC-140 Short Manual v2.1, Table 1.2, "Max allowable moment Mx (static)": https://uploads.unchainedrobotics.de/media/file_upload/PGC-140-Short-Manual_v2.1_e46a3c6b.pdf |
| Recommended environment | **0–40 °C**, under 85 % RH | catalog page above |
| Self-locking | "Self-locking Mechanism" is listed as a feature (an icon, no holding value) | catalog page above |
| Weight / body | 1 kg; 138.5 × 75 × 75 mm | catalog page above |
| PGC-300-60 (upgrade) | 15 / 15 / 15 N·m, 6 kg recommended, 178 × 90 × 90 mm | catalog page above; `r19_arm_hand_cost.md:203` (1.5 kg, about +€470) |

**The reference-point problem [S].**
- The manual says only: "In the actual gripping, you should take the gripping angle and gripping position into account… The force perpendicular to the gripped flat surface is used as Fz, the x-axis direction torque is Mx…". The axes are drawn in a figure (Fig. 1.2) with no origin dimension and no finger length (manual v2.1, p. 3).
- The PGC-50 user guide uses the same text (https://funduinoshop.com/media/pdf/6f/04/13/PGC-50-Gripper-User-Guide.pdf).
- No maximum finger length is published (`research/finger_design_inputs.md:25`).
- No dynamic rating and no rated life are published.
- **How SCHUNK does it, for comparison** [S, MPC 100 page: https://schunk.com/de/de/greiftechnik/parallelgreifer/mpc/mpc-100/p/000000000001343466]:
  - the moments are static, "gelten je Grundbacke und dürfen gleichzeitig auftreten" (they apply per base jaw and may act at the same time);
  - they act "zusätzlich zu dem durch die Greifkraft erzeugten Moment" (in addition to the moment from the gripping force);
  - finger length is measured from a stated reference surface;
  - a maximum finger length is published: 40 mm for 8 N·m.
- DH states none of these.

**How to resolve it:**
1. Ask DH (§7): the origin, whether the 7 N·m is per jaw or for the gripper, whether it includes the grip-force moment, the combination rule, and the dynamic and fatigue ratings.
2. Until DH answers, **design to the conservative reading**: the origin at the jaw-guide plane inside the housing (about 72 mm behind the TCP [E]), the gripping-force moment included, and the axes combined by vector norm. Under that reading the wok is at 104 %, which is the reason for the palm key.
3. **Measure it** (§8 bench): load the PGC with a known offset weight at 3 lever arms and log jaw drift with the 0x0202 position register (`finger_design_inputs.md`, register table) and a dial gauge. The drift-vs-moment slope shows where the guides start to give.

### 1.2 Arms [S]

| | UR5e | Fairino FR5 (`fr5_j6_pgc_sp20`) |
|---|---|---|
| Rated payload | 5 kg (https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/) | 5 kg up to 300 mm CoG offset from the flange ("full performance") (`sim/r10/claude/R19_FR5.md:121-123`) |
| Wok + heaviest dish, total | 4.15 kg (`README_R10.md:570`) | 4.40 kg, CoG 158 mm, flange moment 6.84 N·m (`R19_FR5.md:132`) |
| Soak tub, total | — | 4.23 kg, flange moment 9.10 N·m (`R19_FR5.md:133`) |
| Payload CoG limit used | 5 kg at 0.35 m (`R19_ARM_SWAP.md:135`) | 300 mm (above) |
| Flange F/T sensing | built in: force ±50 N (precision 3.5 N, accuracy 4.0 N), torque ±10 N·m (0.2 / 0.3 N·m) (datasheet above) | not in the repo's sources (ND) |
| Joint load, wok chain | ≤ 0.63 of the rated envelope (`README_R10.md:773`) | `R19_FR5.md` |

A palm key adds about 0.2–0.3 kg [E]. That gives 4.40 kg (UR5e) and about 4.65 kg (FR5 sp20) of 5. It fits, but the FR5 margin falls to about 0.35 kg [E]. The PGC-300-60 instead (+0.5 kg) gives 4.65 / 4.90 kg, which is too close on the FR5 [E].

## 2. Load inventory

The moment is about the TCP as the repo reports it. The last column adds the housing-face reading where it matters [E].

| Held object / action | Held mass | Static moment at the PGC (repo) | Dynamic | vs 7 N·m | Notes / source |
|---|---|---|---|---|---|
| **Wok + 1.15 kg food, lift and carry** | 2.95 kg | 6.23 N·m level | — | 89 % | `results/r17/chain_wok_s-1_final.json` loads [M] |
| **Wok, tipped 90° over the plate** | 2.95 kg | **6.47 N·m** (= |r|·mg, worst orientation) | 6.467 (`R19_SMOOTH.md:215`) | **92 %**; housing-face reading 6.78 (97 %), jaw-guide reading 7.27 (104 %) [E] | `README_R10.md:773`, `README.md:66` (home-cooking-robot) [S] |
| Wok + 0.5 kg rinse water | 2.3 kg | 4.73–4.89 N·m | — | 70 % | chain loads [M] |
| Wok + 1 L water from the tap (WOK_FILL) | 2.8 kg | 5.88 N·m | — | 84 % | `R19_MOTION_LIBRARY.md:207` [S] |
| Wok empty | 1.8 kg | 3.58 N·m | — | 51 % | chain loads [M] |
| **Wok, food slides to the lip while tipping** | 2.95 kg | 6.47 ± up to about 1.9 N·m | not modelled | **up to about 120 %** if it adds | food fixed 20 mm above the wok origin in `r17chain.py:252` [S]; 1.15 kg × ≤ 0.17 m rim radius [E] |
| Spatula, typical stir (food contact), new cycles, seeds 1–7 | 0.3 kg | p95 2.2–3.5 N·m (food force only, about the grip point 0.45 m from the edge) | (is dynamic) | 31–50 % | `results/r19/stir/spill/stir2_nw_{ur5e,fr5}_s1..7.json` [M]; spatula weight +1.3 N·m static (`R19_SMOOTH.md:216`) |
| **Spatula, jam spikes** | — | single-sample max 9–367 N·m in every run; > 50 N·m in 3/8 runs per arm; seed 8 p95 8.3 (UR5e) / 17.3 (FR5) | — | **130 %–50×** | as above, s8 [M]; `R19_SPILL.md:87` [S]. Peak food force 930–980 N |
| Spatula, R15 bench (reference) | — | p95 2.2–2.9, spikes 8–25 N·m | — | | `README_R10.md:542` [S] |
| Lid off the pot → rack | 0.8 kg | 1.58 N·m | 1.64 | 23 % | `README_R10.md:775`, `R19_SMOOTH.md:217` |
| Spider scoop → plate | 0.45 kg + food | 1.25 N·m | 1.29 | 18 % | `README_R10.md:774`, `R19_SMOOTH.md:218` |
| Ladle scoop and pour | — | 0.8 N·m | — | 11 % | `README_R10.md:687` |
| Dish carrier (plates into the steamer) | — | 0 | — | 0 | `README_R10.md:686` |
| Seasoning cup | — | 0.22 N·m | — | 3 % | `sim/r10/claude/R19_CUPS.md:23` |
| Staging pan → wok | 0.64 kg | 0.70 N·m | — | 10 % | `R19_PREP_STEP4.md:13` |
| Soak tub, full | 2.78 kg | 4.83 / 4.84 N·m; slosh about 5.5 [E in the source] | — | 69–79 % | `R19_FR5_PREP.md:37`, `R19_PREP_STEP3.md:169` |
| Wash basket | 1.15 kg | 1.81 N·m (upper bound 5.0) | — | 26–71 % | `R19_PREP_STEP3.md:28,132` |
| Fridge door at a 100 N seal | — | ≈ 6.4 N·m [E in the source] | — | 91 % | `README_R10.md:427` |
| Cabbage 1.9 kg / napa 2.8 kg | — | 6.6 / 7.3–11 N·m | — | 94 % / fail | `README_R10.md:315-316` |
| Faucet lever lift | closed chain | unmeasured lever force | — | ? | `README_R10.md:758,816` |
| Drum into the holder | ≈ 0.35 kg [E] | < 0.3 N·m [E] | — | small | `README_R10.md:387-388,574-575` |

**Gripping force adds to this under the conservative reading.**
- A 140 N jaw force at a 45 mm grasp depth (design D, `fingers.py:24`) gives 6.3 N·m of finger-root bending.
- That alone is near 7 N·m if DH counts it, which is how `finger_design_inputs.md:25` derived "lever ≤ 50 mm at 140 N" [S].
- A form-fit block needs only the minimum force, 40 N per jaw (`finger_design_inputs.md:14`), so about 1.8 N·m [E]. **Set the wok and spatula grasps to minimum force.**

**The repo checker already uses a 150 N / 15 N·m "key rule"** for keyed blocks and keeps the OEM 7 N·m as a separate, unresolved constraint (`sim/r10/claude/hardware.py:31`) [S]. The palm key is what would make the 15 N·m key rule physically true.

## 3. Stir jam: what the sim says and what it means

**Stored metric [S, `stirbench.py:161-188`]:** `spatula_M_grip_Nm` is the norm of the moment of all **food** contact forces on the spatula about the grip point. It excludes the edge-on-steel force and the spatula's weight. Sampling is every 10 ms. The spatula is a free body on a stiff weld (`WELD='.005 1'`, `stirbench.py:44,91`), so the arm never yields.

**Per driver, seeds 1–8, 12 s per run (about 4.3–5 strokes) [M]:**

| Driver (files) | Period | Grip moment p95, s1–7 | p95, seed 8 | Max, range | Runs with max > 25 / > 50 N·m | Samples > 30 N, median per run |
|---|---|---|---|---|---|---|
| Bench (`spill/stir2_tr_bench_s1-3`, `stir2_sh_bench_s4-8`) | 2.40 s | 2.2–3.7 | 2.5 | 10–339 | 1 / 1 | 1.5 |
| UR5e old j8000 (`phys/…ur5e_enc2_pgc_j8000_s1-3`, `spill/stir2_oj_ur5e_s4-8`) | 2.79 s | 2.5–3.5 | 6.9 | 12–365 | 4 / 2 | 6.5 |
| FR5 old j8000 | 2.62 s | 2.4–3.6 | 10.3 | 12–362 | 2 / 1 | 4.0 |
| **UR5e new (spill fix)** (`spill/stir2_nw_ur5e_s1-8`) | 2.81 s | 2.2–3.5 | **8.3** | 9–367 | 3 / 3 | 4.0 |
| **FR5 new (spill fix)** (`spill/stir2_nw_fr5_s1-8`) | 2.64 s | 2.5–3.4 | **17.3** | 13–362 | 3 / 3 | 7.0 |

- **Effective lever:** at the peak sample, moment / force ≈ 0.30 m (median over 40 runs) [M]. So a 5 N·m cap corresponds to about 17 N of food force at the blade [E]. The p95 food force is 6.4–9.6 N on seeds 1–7 [M].
- **Rate, as an upper bound:**
  - 82 strokes per meal [S, 247 / 3 from `r19_system_cost.md:121`] is about 18 twelve-second windows.
  - At 3 of 8 windows with a > 50 N·m event, that is **about 7 hard jams per meal**, or about 2.5k a year [E from M].
  - Rigid 15 mm dice and an infinitely stiff "arm" overstate this. Real food is soft, wilts and is oily (`README_R10.md:544`) [S]. The real rate is unknown until a bench test.
- **Consequence:**
  - Even the typical load (p95 3.5 N·m, plus 1.3 N·m of spatula weight, ≈ 4.8 N·m) uses about 70 % of the jaw rating on every stroke.
  - The tail goes far past it.
  - So the spatula's moment path must be (a) taken off the jaws and (b) capped by something that yields.

## 4. Design changes

### 4.1 Palm key (removes the jaw from the moment path) [proposal; geometry from `r19_arm_hand_cost.md:218-235`]
- **Fork:** a 6061-T6 fork plate between the flange and the PGC (ISO 9409-1-50-4-M6, `finger_design_inputs.md` flange row). Two arms run beside the body and end in **two Ø8 mm hardened pins, 40 mm apart, with a 1:10 taper over 12 mm** and a 1 mm × 30° entry chamfer, just behind the fingertip zone.
- **Tool blocks** (wok, spatula, optionally lid, spider, ladle) get two matching tapered holes.
- **Sequence:** a straight insertion of ≤ 50 mm along the pin axis (inside the contact-window rule). Then the jaws close at **40 N** (the minimum) onto side flats, only to stop pull-off.
- **Loads [E]:**
  - wok 6.47 N·m → about 162 N couple on the pins (the source's own example);
  - a spatula breakaway at 5 N·m → 125 N;
  - Ø8 pin shear about 3 MPa: negligible.
  - Fork arm, as a 100 mm cantilever with a 30 × 10 mm section (Z = 500 mm³): about 10 N·m → 20 MPa. That is a safety factor of about 4.8 on the 6061-T6 fatigue strength of about 97 MPa at 5 × 10⁸ reversed cycles [S, search-sourced ASM figure; https://www.sdcverifier.com/wiki/fatigue-strength-and-limit/ ; verify against the ASM sheet].
- **What the jaws still see:** pull-off along the pins (≤ 30 N for the wok in the tipped pose [E]), well under Fz 300 N.
- **Cost:** about 0.2–0.3 kg of payload [E] and new tool blocks. ¥200–800 [S, `r19_arm_hand_cost.md`, "Where the money is"].
- **Still on the jaws:** cold-food grasps, the fridge door and cabbage, as today.

### 4.2 Shorter lever arm
- **Grip block nearer the wok CoG** (the block is at 0.235 m from the axis, `kitchen15.py:34`; CoG offset 215 mm along tool z) [S/M]:

  | Block moved inward | 0 | 20 mm | 40 mm | 60 mm |
  |---|---|---|---|---|
  | Worst static moment about the TCP [E] | 6.47 | 5.91 | 5.36 | 4.82 N·m |

  - The cost is a block closer to the rim, so hotter (#15), and the plume rule (arm ≥ 0.20 m from the wok axis while heat is on, `README_R10.md:515`).
  - The wok is only grasped with the heat off (`README_R10.md:519`), but the stir-time clearance to the block changes. **It needs the wok chain and stir cycle re-checked.**
- **Grasp so that the approach axis points at the wok CoG.** Today the CoG sits mostly along tool z (215 mm). If the approach axis pointed toward the CoG, more of the load would become Fz (300 N rating) and less would be moment. That is a different grasp sense and lean, so a re-plan [E].

### 4.3 Moment path through the finger base (if the palm key is rejected)
- **Finger change:** the fingers get a **palm shoulder**, a flat that bears on the PGC's top housing face (or on a bolted bridge plate that spans both jaws' outside). Under moment, the block then rotates onto the shoulder and the reaction goes into the housing rather than through the jaw guides.
- This only works if the shoulder does not touch during normal closing. A 0.3–0.5 mm gap closes only under load [E]. **Ask DH whether housing contact is permitted.**
- It is weaker than the palm key: it still loads the housing top cover, whose strength is unknown.

### 4.4 Spatula breakaway (mechanical fuse) + jam sensor
- **Where:** inside the spatula's keyed block, between the block and the handle. A ball-detent torque limiter has 3–4 balls on a preloaded disc spring, about the axis of the dominant jam moment. That axis is unknown; it needs a sim check (§9).
- **Setting:**
  - Without the palm key: release at **5.0 N·m** = 7 − 1.3 (spatula weight) − 0.7 margin [E].
  - With the palm key: about 8–10 N·m. That protects the wok seat, the arm and the food, not the jaws.
  - At 5 N·m it releases at about 17 N of food force [E], against a p95 of about 10 N. So it trips only in the tail. **The trip frequency must be read from the sim (§9) before the setting is fixed.**
- **Self-resetting:** the detent re-indexes when the arm lifts the blade. One detent position per 360° keeps the blade orientation keyed.
- **Signal:** a magnet in the rotating half and a Hall switch on the palm-key fork. That gives a jam signal with no wiring through the fingers, since the tool-flange channel is taken by the TCI (`hand_options.md:96` via #26) [S]. The spatula needs no electronics.
- **Material:** 304 stainless balls and seats. The housing is PA12-CF or aluminium, not PETG: the block is near the wok, see 5.2.
- **Spring alternative:** a preloaded spring holder (4 N·m preload, 10–15° travel to 5 N·m, then the detent). It adds the compliance that #26 and `R19_TOLERANCE.md` §4 ask for at the steel. It also absorbs the ±2 mm position error of a stiff `servoj` replay.

### 4.5 Stroke force limit, back-off and retry (#26)
- **Detector, any of:**
  - the Hall breakaway switch;
  - UR5e flange force norm above the model by > 25 N for > 20 ms. Precision is 3.5 N, so 25 N is about 7σ [E on S]. The scraping edge force alone has a p95 of 17–21 N on the new cycles (`edge_on_steel_N`, `spill/stir2_nw_*`) [M], so the threshold must be relative to a per-stroke reference trace, not absolute;
  - FR5: joint-current collision detection, sensitivity ND, so measure it.
- **Response (proposal):**
  1. Controlled stop (category 2), then reverse 10 mm along the stroke path and lift 20 mm.
  2. Re-enter the same stroke 3 mm higher, or shifted to the neighbouring line (0 / ±5–6 cm offsets exist, `README_R10.md:512`).
  3. After 2 failed retries: cooker to half power (the existing pause rule, `README_R10.md:532`), park the spatula in the wok, prompt the user.
  4. Log every event. That log is the field fatigue ledger.
- **Why both the fuse and the software:** in the sim, the jam builds in tens of ms to about 1 kN. The arm's stop latency is unknown, so ask the vendor. The fuse caps the first milliseconds; the software stops a re-load.

### 4.6 Plating tilt rate
- The dynamic peak equals the static one (`R19_SMOOTH.md:215`) [S]. A slower tilt therefore does **not** reduce the 6.47.
- It does limit food surge toward the lip, the unmodelled ±1.9 N·m. Keep the 45°/s wok rotation cap (`R19_SMOOTH.md:137`).
- Add a **hold at 60°** (it already improves plating, `README_R10.md:560`) so the food slides while the moment is lower.
- Check the lip-CoG case in the sim (§9).

## 5. Fatigue

### 5.1 Duty ledger [S counts from `research/r19_system_cost.md:116-126`; per-year at 1 or 2 meals a day is E]

| Event | Per 3 meals | Per meal | Per year, 1 meal/day | Per year, 2 meals/day | 10 years, 2/day | Load per event |
|---|---|---|---|---|---|---|
| Stir strokes | 247 | 82 | 30k | 60k | 0.6 M | p95 3–4 N·m + 1.3 N·m weight |
| Hard jams (> 50 N·m, rigid-dice bound) | — | ≈ 7 [E] | ≈ 2.5k | ≈ 5k | 50k | capped by the fuse / key |
| Spatula grasp / release | 14 | 4.7 | 1.7k | 3.4k | 34k | grip-force cycle |
| Wok plating trips (lift + tip) | 7 | 2.3 | 0.85k | 1.7k | 17k | 6.23 → 6.47 N·m |
| Wok fill / dump | 5 | 1.7 | 0.6k | 1.2k | 12k | 4.7–5.9 N·m |
| Faucet open / close | 14 | 4.7 | 1.7k | 3.4k | 34k | lever force (unmeasured) |
| Lids | 16 | 5.3 | 1.9k | 3.9k | 39k | 1.6 N·m |
| Cup pours | 55 | 18 | 6.7k | 13k | 134k | 0.2 N·m |

- The issue's "about 1.5k loaded wok lifts a year" = (7 + 5) / 3 × 365 [S, issue #16].
- **The design life target** is 10⁶ cycles for anything in the stir load path: 0.6 M plus about 1.5× for sub-cycles inside a stroke [E]. It is 10⁵ for the wok load path.

### 5.2 Materials

| Material | Strength | Temperature | Use here |
|---|---|---|---|
| PETG (Prusament, printed) | yield 47 ± 2 MPa (XY), 50 (XZ), ISO 527 [S, Prusament TDS v1.1 via search: https://www.3dprintergear.com.au/assets/files/technical-data-sheet%20(1).pdf] | **HDT 68 °C** at 0.45 and 1.8 MPa [S, same]; Kimya PETG Tg 80 °C (`finger_design_inputs.md:96`) | cold food fingers only |
| PA12-CF / PAHT-CF (printed) | Bambu PAHT-CF 88 ± 7 MPa; a JLC PA12-CF 69.3 MPa [S, retailer copies, not the maker's PDF: https://www.3dprintergear.com.au/bambu-lab-paht-cf-carbon-fibre-nylon-1kg , https://jlc3dp.com/help/article/PA12-CF-Plastic] | HDT 194 °C at 0.45 MPa (Bambu) / 105 °C at 1.8 MPa (JLC) [S, same] | wok and spatula fingers, drum holder, faucet clip |
| 6061-T6 | fatigue ≈ 97 MPa at 5 × 10⁸ reversed cycles [S, search-sourced, see 4.1] | fine | palm-key fork, alternative wok fingers |
| 304 stainless | not looked up today | fine | grip blocks, pins, detent seats |
| PETG S-N | curves exist (R = 0.2, 45° raster; R = 0.4) but no numbers were read [S, search only: https://www.mdpi.com/2504-477X/5/3/76] | — | — |

**Stress check of a printed finger [E].**
- Design L/V fingers: thickness T = 8 mm, pad height H = 40–46 mm, grasp depth D = 45 mm (`fingers.py:24-26`) [S].
- Root section in the weak direction: Z = H·T²/6 ≈ 427 mm³.
  - The wok held at 140 N: 6.3 N·m → **15 MPa**, about 32 % of the PETG yield, per grasp.
  - At 40 N: 4.2 MPa.
  - A spatula jam of 25 N·m, half per finger and in the weak axis in the worst case: **29 MPa**. That is 62 % of yield, and already beyond any credible 10⁶-cycle level for a printed thermoplastic.
- Typical stir, 3.5 N·m p95 shared: about 4 MPa amplitude, 30–60k times a year.
- **My working limit [E, rule of thumb, not sourced]:** keep the printed-part stress amplitude ≤ 10–15 % of printed yield for 10⁶ cycles at room temperature, and much less near the HDT. PETG passes the typical stir only when it is cold. It fails the jams and the hot block.
- **So:**
  - wok and spatula fingers in PA12-CF (HDT ≥ 105 °C), or a machined aluminium "tool set" (#15 already suggests a metal wok-specific set);
  - interval: replace printed tool fingers every 6 months or at 15k strokes [E], until the bench gives an S-N point;
  - the keyed slot / holder parts in stainless or 6061, never printed, because they are in the jam path.

## 6. Keyed wok coupling, faucet clip, drum holder

### 6.1 Wok side: what bolts to the handle
- **Today:** a short handle ends in a 44 × 30 × 30 mm grip block 0.235 m from the axis (`kitchen15.py:33-34`). The R15 bracket was removed, and "a keyed slot in the cooker's bowl rim takes over its anti-rotation job (not modeled)" (`README_R10.md:761`).
- **The bowl is probably glass-ceramic** (issue #16). **Do not cut it.**
- **Proposal [E]:**
  1. **Grip block**, 304 stainless or hard-anodised 6061, 44 × 30 × 30 mm:
     - two side flats with a 90° V-rib, 2 mm high, that the PA12-CF fingers form-fit over (z capture plus rotation about the jaw axis);
     - back face: two tapered holes for the palm key, 40 mm pitch, 1:10 taper, with a 1 mm × 30° lead-in;
     - all outer edges with a 3 mm × 45° chamfer;
     - machined faces ±0.05 mm; taper holes ground or reamed.
     - It bolts to the handle stub with 2 × M5 A2 plus a Ø4 dowel, through a **5 mm PEEK or G10 thermal-break spacer** (#15).
  2. **Anti-rotation key** under the handle root, 0.175 m from the axis (`kitchen15.py:33`, root at x 0.655 vs axis 0.83): a stainless tab, 15 mm wide × 8 mm deep, hanging down. It seats in a slot in the rim collar (6.2).
- **Seating sequence:**
  - the arm lowers the wok; the tab enters the collar's V-funnel first;
  - the funnel's lead-in must be ≥ the docking error box: ≥ 5 mm per side with docking stops, ≥ 12 mm as designed (the same budget as the lid rack, #8 / `R19_POTZONE.md`) [S];
  - the bottom 4 mm of travel is the wok set-down z-tolerance (`R19_TOLERANCE.md` §2) [S];
  - the jaws then release at 40 N. The wok grasp's 2.4 mm reserve is unchanged, because the block itself does not change size (`R19_MOTION_LIBRARY.md:199`).

### 6.2 Rim collar (replaces the bowl slot)
- **What it is:** a split ring that clamps to the cooker's **outer housing lip**, not the glass, with two over-centre latches and silicone pads.
- **Material:** PEEK or glass-filled PPS. It is non-metallic so the induction field does not heat it [E]. The heat rating must exceed the wok outer wall at the rim (≤ 250 °C wok, `README_R10.md:508`). Confirm the PEEK/PPS continuous-use temperatures against a TDS; I did not look them up.
- **Slot load case [E]:**
  - Typical scraping: an edge-on-steel force p95 of about 20 N (new cycles, [M]) at r ≈ 0.13 m is about 2.6 N·m about the wok axis.
  - Fused or force-limited jam: ≤ 50 N × 0.17 m ≈ 8.5 N·m.
  - Design torque **10 N·m** → tab force 57 N at 0.175 m. PEEK bearing stress on a 15 × 8 mm face: about 0.5 MPa.
  - The unfused sim jam (≈ 980 N) is not a design case. It must be prevented by the fuse and the stall response, not resisted.
- **Wok lift-out (tilt) [E]:** a jam force pointing upward could lift the wok out of the bowl. The tab slot should have a 2 mm undercut lip only if the wok must resist lift. I recommend not: let the wok lift, and treat a lift as a jam signal from the camera or the Hall switch.

### 6.3 Faucet clip
- **Today:** a clip-on keyed block on a 25 mm bracket at the lever end, gripped from the right, lifted 30° (`README_R10.md:758`). The lever force is unmeasured, and the geometry is estimated from a photo (`README_R10.md:816`) [S].
- **Load cases [E]:**
  1. The cartridge operating torque, unknown, so measure it with a luggage scale at the lever end.
  2. **The closed-chain fight.** The lever moves on an arc, the arm on a stored path. With a 4–15 mm x/y error (`R19_TOLERANCE.md` §2) and a stiff arm, the internal force is limited only by compliance. That can be tens of N on a 25 mm bracket, which is a 1–3 N·m moment at the clip and the jaws.
- **Design:**
  - the clip's block slides in a radial slot, ±6 mm along the lever, plus a ±3° rocker. Only the lift direction is constrained.
  - The lead-in on the block is ≥ 5 mm.
  - PA12-CF clip, stainless screw clamp on the lever, and a TPU pad against chrome.
  - Duty is 1.7–3.4k cycles a year: printed PA12-CF is fine at low stress [E].

### 6.4 Drum holder
- **Today:**
  - The drum is Ø80 × 140 mm (`README_R10.md:388`).
  - The holder behind the wok has **zero clearance reserve** and was not checked against the stir strokes (`README_R10.md:575`).
  - It swings away except while stirring (`README_R10.md:763`) [S].
- **Load cases [E]:**
  1. **Drop-in by the arm:** at zero reserve, the holder must have a V-cradle with ≥ 5 mm lead-in (docking-stop budget) and a spring-loaded end stop.
  2. **Servo roll:** drum about 0.35 kg [E, mass not in the repo], CoG offset ≤ 30 mm when unevenly emptied, so ≤ 0.1 N·m. Any hobby servo with ≥ 0.5 N·m stall torque works.
  3. **Spatula or wok strike:** the holder is next to the rim, so it sits in the jam path. Make the swing-arm pivot a detent breakaway, so the holder yields before the spatula fuse.
  4. **Heat:** the rim zone needs PA12-CF or aluminium, not PETG.
- **The swing-away mechanism doubles as the breakaway.**

## 7. Questions for DH / the arm vendor (not sent)

**DH Robotics (PGC-140-50 and PGC-300-60):**
1. Where is the origin of Mx / My / Mz in Fig. 1.2 (Table 1.2)? Please give a dimension: jaw-guide plane, housing top face, or finger mounting plate.
2. Is the 7 N·m per jaw or for the gripper? May Mx, My, Mz and Fz act at the same time? Does it include the moment from the gripping force?
3. What is the dynamic or fatigue-rated moment (for example at 10⁶ cycles), and the rated life of the jaw guides and rack under a constant 6.5 N·m offset load?
4. What is the maximum finger length or mass at 40 N and at 140 N?
5. Holding at power-off ("Self-locking"): what holding force at the jaws, and what does the gripper do on 24 V return (an initialisation stroke)? (#20)
6. May a finger or bridge plate bear on the housing top face to take moment (palm shoulder, 4.3)?
7. What is the allowed housing and ambient temperature beyond the stated 0–40 °C, near a 60–110 °C tool block? Which is right: IP67 (catalog) or IP54 (manual v2.1)?
8. What is the relation between the force register 0x0101 (%) and newtons, and the current-limit stall response time?

**Universal Robots (UR5e):**
1. Protective-stop latency and stopping distance for a force-limit trip at about 0.5 m/s TCP with a 4.4 kg payload.
2. Can a URCap or RTDE monitor the flange F/T against a per-stroke reference at 500 Hz and trigger a controlled stop?
3. Force-mode behaviour while scraping with a 0.45 m tool.

**Fairino (FR5):**
1. Collision-detection sensitivity levels in N or N·m, and their latency.
2. Is there an optional flange F/T sensor and price?
3. The rated flange moment (we compute 6.84–9.10 N·m static).

## 8. Decisions for the user

1. **Palm key, yes or no.** My recommendation is yes. It makes the 15 N·m key rule of the checker real, and removes the reference-point risk on the wok and spatula. The cost is about 0.25 kg of payload, which leaves the FR5 with a 0.35 kg margin.
2. **Breakaway setting:** 5 N·m without the key, about 8–10 N·m with it. Plus the Hall jam switch, yes or no.
3. **Rim collar instead of a slot in the bowl.** It is non-metallic and clamps to the housing.
4. **Tool finger material:** PA12-CF printed, or machined aluminium for the wok and spatula. PETG only for cold food.
5. **Wok grasp at minimum jaw force (40 N)** for keyed blocks.
6. **Send the DH questions?** Contacting a supplier needs your OK (`DECISIONS.md:138`).
7. If the key is rejected, do you accept the **PGC-300-60** (+0.5 kg, about +€470)? It is tight on the FR5 payload.

## 9. Next steps / sim checks to run (each < 5 min unless noted; none run by me)

1. **Lip-CoG plating case:** re-evaluate the `r17chain.load()` moment along the stored wok play with the food CoG moved from (0, 0, 20 mm) to the pouring lip. This gives the real slosh bound for the ±1.9 N·m. It is a formula over the stored states, so no re-plan.
2. **Reference-shift table:** report the wok chain's moment about the TCP, the housing face (−35 mm) and the jaw guides (about −72 mm), per DH axis, using the stored grasp frames.
3. **Jam moment direction and trip rate:** a wrapper around `r19stir2_phys.py` (as `r19spill_trace.py` does) that stores the moment **vector** in the grip frame every 10 ms.
   - Output: the dominant jam axis (for the detent axis) and the fraction of strokes with M > 4 / 5 / 6 N·m. That fixes the fuse setting.
   - 8 seeds × 2 arms, about 10–12 min per run, so this goes to controller lanes.
4. **Fuse in the sim:** replace the stiff weld with a weld plus a rotational joint with a friction-loss limit at 5 N·m. Report the mixing metric (hot share, spill) and the slip count. Controller lanes, about 12 min per run.
5. **Stall-and-retry in the sim:** on |F_food| > 30 N, stop, back 10 mm and up 20 mm, re-enter. Count the successful retries on seed 8.
6. **Block 40 mm inward:** re-run the wok chain and the stir-cycle checks with the moved block. Long, so controller lanes.
7. **Palm-key geometry in the checker:** add the fork as a gripper geom and re-check the wok, spatula, lid and spider chains. The fork arms beside the body may cost reserve.
8. **Bench (issue step 5):**
   - the PGC holding 2.95 kg at a 223 mm offset for 5,000 cycles, logging jaw drift (0x0202) and slip;
   - a print-coupon S-N for PA12-CF and PETG fingers at 4 and 15 MPa;
   - the collar and faucet clip, printed and tried.
