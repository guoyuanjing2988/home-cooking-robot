# R19 prep layout and the core prep sets in today's kitchen (issue #4, steps 1–2, 2026-10-13)

**Round 2 (true-geometry arm `ur5e_enc2_pgc`): see §9. All three sets pass there too, with no layout move.**

**Why.** The user: "备菜是最重要你要做的之一了，肯定不是人来做". The prep audit (`R19_PREP_AUDIT.md`) found that the only two checked prep chains (carrot SD, tomato WD, R12) no longer work in today's (R18b) kitchen:
- the wall spout they wash under is gone;
- the peeler stands on the spatula rest;
- the slicer stands on both plating spots;
- the old tool spot blocks the wok and faucet actions.

This round does the audit's steps 1 and 2:
- new spots for the fetched-tool work spot, the slicer, the peeler and the fridge cold box (screened against every saved checked path, plus a reach check);
- the core prep sets re-planned in today's kitchen as whole actions (`r17chain.py` method): wash under today's faucet; tray → carry → slicer chute; tomato onto the lever cutter; the lever press.

**Labels**
- **[checked]**: a whole action planned with the `r17chain.py` method (unchanged checker), *and* re-checked state by state at ≤ 4 mm with the full checker (`r19prep_verify.py`).
- **[screen]**: the fast checker (`full=False`) on stored states, as in `r18spatreplay.py` / `r19prep_spotreplay.py`. A screen, not a check.
- **[probe]**: 96-start collision-aware IK (192 starts with two seeds) with the unchanged checker at one pose, as `r14reach.py`.
- **[est]**: an estimate, with its basis stated.

**Rules (unchanged):**
- gaps: 10 mm robot ↔ environment, 5 mm gripper/held ↔ environment;
- states ≤ 4 mm apart;
- contact windows only during the ≤ 50 mm straight grasp approach / release retreat, for that grasp's own contacts;
- no process force tuned: none is applied (rinse only; the press reports the available push force only).

**Files.** No existing file was changed.
- `kitchen19.py`: the layer on top of kitchen17. It holds the stations at new poses (exact R11 geometry copied from a `scene.build` donor), the R19 objects (carrot, tomato, pusher, cold box), the candidates, the reach probes and the chosen `LAYOUT`.
- `r19prep_layout.py`: modes `map`, `screen`, `replay` and `reach`.
- `r19prepchain.py`: the whole-action prep sets (ACT=carrot | tomato | press | tap).
- `r19prep_verify.py`: the ≤ 4 mm full re-check of a stored set.
- `r19prep_render.py`: the top view.

Results are in `results/r19/prep/` (explorations in `results/r19/prep/explore/`). Renders: `renders/r19/prep_layout_r19.png` and `renders/r19/prep_layout_map.png`.

---

## 1. Answer first

1. **Chosen layout** (sim kitchen, all sizes are the R11/R14 estimates). See `renders/r19/prep_layout_r19.png`.

   | Item | Spot | Status |
   |---|---|---|
   | 卓晋 slicer (6.8 kg, resident) | Far-left column, **turned 90°**: body x −1.795…−1.585, y 0.06–0.39. The chute is at the front, (−1.69, 0.145), top at 1.13 m, in the open strip. The out bowl is under the cabinet at (−1.69, 0.50). | Clear of every saved cooking path [screen: 0/106 segments flagged, no hits in 2,003 replayed states]. Chute drop reachable [probe: 41 good starts, 12.5 mm reserve]. Used by the checked carrot set. |
   | Fetched-tool work spot (lever base AY-403 class; also the cold box, one at a time) | Left counter by the sink, **set back**: lever origin (−0.86, 0.21). Base plate x −0.97…−0.75, y 0.115–0.375; knob at 1.152 m. | No hits on the 6 stored cooking chains (wok plate + rinse at both spots, faucet, lid, spider, spatula fetch; 2,003 states) [screen]. The flagged hub edges are only partly replayed (4 edges, 6,808 states, 0 hits). Reach [probe]: place 40, knob 32, pressed 40 good starts. Used by the checked tomato and press sets. |
   | Fridge cold box set-down | At the same work spot, box along x, centre (−0.86, 0.17), bar at 1.06 m. Never out together with the lever base. | No hits on the 6 stored chains [screen]. Reach [probe]: 39 good starts, 4.0 mm reserve. The R14 spot (−1.70, 0.18) is now under the slicer. |
   | Raw tray | Unchanged (x −1.515…−1.195, y 0.04–0.34). The tomato is on the R11 pad at the tray front; the potato moves to the tray's back right. | Picks reachable [probe: carrot 52, tomato 37 good starts]. Used by both sets. |
   | Peeler | **No spot.** The R11 cradle-peeler model (0.48 m wide drive) fails reach at all three tried spots [probe 0/192 each]. | Open: use the real batch abrasive peeler (傲宏 85 W class) at the work spot; its pour-in / pour-out is the BASKET family (audit step 3). Not modelled. |
   | R07 tomato staging bowl (x −0.96…−0.76, y 0.36–0.56) | Must move: it would overlap the lever base plate by about 2 cm. | Removing an obstacle cannot create a hit in the checked cooking paths. |

2. **The core prep sets pass in today's kitchen** [checked]. In each, the item is grasped, carried, washed or cut, and released.

   | Set | Path | Motion time (r17 timing) | Min reserve, ≤ 4 mm re-check | Joins | States re-checked |
   |---|---|---|---|---|---|
   | **carrot**: TRAY_PICK + CARRY + WASH_HELD + CARRY + CHUTE_DROP | rib tray → under the running outlet (3 × 3 s rinse, ±5 cm along its axis) → turned upright → dropped 80 mm into the slicer chute → release, retreat | **48.6 s**, including 9 s rinse [est] | **2.01 mm** | 191°, 28° | 3,314 + 61 + 45 |
   | **tomato**: TRAY_PICK + CARRY + WASH_HELD + LEVER_PLACE | pad → under the outlet (3 × 3 s, rolled ±30°) → slid diagonally (20°) onto the blade plate 8 mm up → release, lift 8 mm, retreat | **36.7 s**, including 9 s rinse [est] | **1.0 mm** (release retreat); 2.2 mm in the play | 26°, 34° | 2,804 + 77 + 83 |
   | **press**: LEVER_PRESS | knob grasp (keyed) → press 102 mm → return → release | **4.6 s** | **1.0 mm** (disc 6 mm above the plate, as R11) | none | 364 + 90 + 90 |

   - The lever base was **out at the work spot** during the carrot set too, so the carrot set is valid whether the lever is out or stored.
   - The arm can push **102.5 N** on the knob along the press (limited by the keyed grip, as R11). The tomato wedging force is still **not sourced**.
   - PGC moment is ≈ 0 (the food is centred at the TCP). Max joint-load ratio is 0.40–0.42.
   - Washing uses today's single-lever faucet. The checked R17 lever action (`chain_lever_s+1_final.json`, 3.5 s) opens it before and closes it after. Every set's scene contains the lever both **closed and open** (union), so the sets do not depend on the faucet state.

3. **What decided the layout** (the reasons, with the evidence in §2):
   - **No back spot works.** Under the upper cabinets no probe passed for:
     - a slicer chute (0/192 at three approach directions);
     - a lever knob (0/192);
     - a raw tray (picks 0/192 at the back left and back middle; one tomato-only exception).

     So the tray, the slicer chute and the lever all need the open front strip (y < 0.21). The audit's slicer candidate (−1.00, back) is also physically invalid: its out bowl reaches over the sink (to x −0.64), it overlaps two staging bowls, and its chute is unreachable.
   - **The clear front strip is short.** The only front space that no stored cooking path sweeps is the far-left column (x < −1.55; ceiling 0.45–0.7 m). The rest of the left front is swept by:
     - the spatula fetch (down to the counter at x −1.27…−1.03);
     - the wok sink trip (0.15–0.25 m above the counter at x −1.47…−1.27);
     - see `renders/r19/prep_layout_map.png`.
   - The tray (0.32 m), the turned slicer (0.21 m) and a lever base (0.22 m) do not fit side by side in front of the R18b spatula rest (x ≤ −1.20).
   - **The robot's own upper arm sweeps the counter front at about 1.15 m** whenever the cart drives along with the arm out (`R_geom_10`, the shoulder end of the upper-arm link).
     - A lever base at the R11 front position (knob y 0.07–0.12, 1.15 m) is hit in every carry past it. This includes the wok sink trips: rails 7–10 mm from the arm at (−1.38) and (−0.90, 0.095).
     - **Set back by 11.5 cm**, the knob is behind that sweep. At (−0.86, 0.21) the lever base is no longer hit by the wok trips, the faucet or the spatula fetch (screen). The carry lane at y 0.10 passes in front of it.
     - Close neighbours fail the spatula fetch narrowly: (−0.88, 0.21) at 4.94 mm and (−0.90, 0.20) at 4.46 mm, against 5 mm required (the held spatula blade vs the pusher stem).
   - **The plating area was tried** as a "prep-time" tool spot (the plates are empty before cooking).
     - Reach was fine.
     - But the cart cannot pass in front of a lever base there either, and the tap → lever leg never joined [smoke runs in `explore/`].
     - It is also hit by the wok plating and the spider (−24 mm).

4. **The sets needed specific motion choices** (all found by smoke runs; the failures are listed in §3.3):
   - Under the outlet the grasp is **pitched down 30°**. With a level grasp the arm could not leave the tap without the elbow entering the cabinet doors, or folding onto its base.
   - The tomato is **turned 90° about the approach axis** at the tap (jaws vertical, as for the carrot). The pick side and the tap side then meet in nearly the same arm branch: a 26° join.
   - The tomato slides onto the blade plate **diagonally (20°)**. Straight from the front, every candidate crossed a wrist singularity (10.1–10.7° joint jump per 1 cm).
   - The meet lanes are at y 0.06–0.10 and z 1.10–1.15. Lanes at y −0.05 put the hand over the robot's own base (self-collision).
   - The release retreat first **lifts 8 mm back to the slide-in height**, then backs out 50 mm along the slide-in axis. This is the R11 WD retreat. Backing out at the seated height came within 5 mm of the blade plate in the ≤ 4 mm re-check.

5. **Not done / open** (details in §6):
   - the physics gate (`dyn.py`, noslip) on the new paths;
   - hub spurs from the set endpoints to H_SPAT / H_SINK;
   - the full hub-edge replay of the chosen work spot;
   - the enclosing arm `ARM=ur5e_enc` (its smoke runs did **not** pass: the fatter elbow capsule meets the closed upper-cabinet door at the press and at the tap);
   - the peeler;
   - the user's real L-shaped kitchen.

---

## 2. Layout: method and results (step 1)

### 2.1 Free-space map (`r19prep_layout.py map`, 26 s)
- **Input:** the 84 stored swept segments of the 6 checked cooking chains (`results/r19/prim/swept_voxels.npz`, dilated 2 voxels) plus the 22 checked hub edges (every 4th state, dilated 3), as `r19prep_screen.py`.
- **Output:** for every 2 cm column, the lowest swept voxel above the counter (`results/r19/prep/layout_map.json`, `renders/r19/prep_layout_map.png`).
- **Left counter front (y < 0.21):**
  - x −1.79…−1.55: 0.45–0.70 m free (limited by hub edges only);
  - x −1.47…−1.27: 0.15–0.25 m (wok sink trip);
  - x −1.27…−0.75: ≈ 0 (spatula fetch, wok trips).
- **Left counter back (y ≥ 0.23):** free of cooking motion everywhere except the spatula's own zone (x −1.25…−1.01, y ≤ 0.39).

### 2.2 Candidates
- **Screens:**
  - static overlap with today's fixed items;
  - the voxel screen against all 106 stored segments (`screen`, `results/r19/prep/layout_screen.json`).
- **Ground truth** (`replay`, `layout_replay_<name>.json`): the fast checker on every stored state of the 6 chains and their approach states, plus every state of each flagged hub edge, with the station's exact R11 geometry as boxes.
- **Reach** (`reach`, `layout_reach_<probe>.json`):
  - lever: place = tomato 8 mm over its seat; knob = open jaws at the knob; pressed = pusher held 102 mm down;
  - slicer: drop = upright carrot 20 mm into the chute;
  - picks: 8 mm over the support;
  - rinse: under the outlet;
  - cold box: the bar pinched from above.

| Candidate | Static overlap | Flagged / 106 | Ground-truth replay [screen] | Reach [probe, good starts of 192] |
|---|---|---|---|---|
| **Work spot: lever at (−0.86, 0.21)** (chosen) | the R07 tomato staging bowl (moved) | n/a (added after the screen; neighbour (−0.90, 0.20): 30) | 6 chains, 2,003 states: **no hits**; hub edges: 4 replayed, 0 hits, the rest pending | place 40 (3.0 mm), knob 32 (13.4), pressed 40 (1.6) |
| lever (−0.90, 0.20), set back | tomato bowl | 30 | wok trips, faucet, lid, spider: none; spatula fetch: held blade 4.46 mm from the pusher stem (12 states) | place 62, knob 31, pressed 25 |
| lever (−1.00, 0.095), the R11 spot | spatula pad (touching) | 35 | wok sink trips at both plating spots (rails 7.6–8.7 mm), spatula fetch (3.9 mm) | place 33, knob 30, pressed 28 |
| lever (−0.90, 0.095) | — | 34 | wok trips (7.1–9.8 mm), spatula fetch (4.5 mm), hub LEV_C→H_SPAT (9.9 mm, 549 states) | place 32, knob 30, pressed 28 |
| lever (−1.665, 0.095), far-left front | — | **0** | **no hits** | place 41, knob 26, pressed 15. **Taken by the slicer** |
| lever (−1.47 / −1.50, 0.095), raw-tray front | raw tray | 14 | **no hits** (10,877 states) | place 18, knob 16, pressed 14. **Taken by the tray** |
| lever (−1.38, 0.095) | raw tray | 14 | wok sink trips (rail 7.7 mm) | — |
| lever (0.30, 0.095), plating area | both plates | 47 | wok plating (−24 mm), spider (4.8 mm), hub LEV_C→H_WOK | place 33, knob 30, pressed 28 |
| lever at the back, under the cabinet (−1.665, 0.43) | — | 0 | no hits | place 9 (1.5 mm), pressed 16, but **knob 0** (elbow / forearm vs the closed doors), so no press. The back spots (−1.40 / −0.88, 0.395) overlap staging bowls. |
| **Slicer turned, far left (−1.69, 0.225)** (chosen) | — | **0** | **no hits** | drop from the front 41 (12.5 mm), from the left 14; over the chute 55 |
| slicer turned, raw-tray front (−1.36 / −1.40) | raw tray | 10–14 | no hits | drop front 14, left 7 (with the tray moved away) |
| slicer (−1.00, 0.475), audit candidate | sink, outlet, 2 staging bowls; out bowl off the counter | 5 | — | **0** at 3 approach directions (cabinet) |
| slicer (0.30, 0.13), R11 spot | cooker, both plates | 51 | — | drop front 25 |
| Peeler R11 (−1.00, 0.20) | spatula rest and blade | 22 | — | seat **0** (spatula handle, cart beam) |
| Peeler turned, far left (−1.66, 0.25) | — | 6 | no hits | seat **0** (arm over the raw tray) |
| Peeler at the back (−0.95, 0.462) | staging bowls, outlet | 3 | — | seat **0** (cabinet doors) |
| **Cold box along x (−0.86, 0.17)** (chosen) | — | n/a | **no hits** (6 chains) | **39** (4.0 mm); y 0.15 / 0.19 / 0.21: 25 / 22 / 22 |
| cold box along x (−0.90, 0.12) | — | 27 | wok sink trips (bar 8.2 mm) | 29 |
| cold box (−1.70, 0.18), R14 | — (the turned slicer now covers it) | 0 | — | 1 (2.1 mm) |
| Raw tray, back left / back middle | potato / greens bowls | 0 / 3 | no hits | picks **0** (fridge side panel, doors, self) |
| Raw tray, far-left front | — | — | — | carrot 23, tomato 26 (an alternative if the slicer moves; not used) |

Rinse under the outlet [probe, z 0.97 / 1.00 m]:
- carrot: 58–64 good starts, 66–70 mm reserve;
- tomato: 76–80 good starts, 57–80 mm reserve.

Reaching the outlet is easy. **Getting in and out of it is the hard part** (§3).

---

## 3. Core prep sets (step 2)

### 3.1 Method
`r19prepchain.py` is the `r17chain.py` method (r17chain itself is unchanged):
- object keyframes, the object moving ≤ 1 cm / 2° per step;
- the arm following by IK continuation, with the cart as an IK variable on 'F' frames;
- 96-start anchors and DP over the anchor candidates, with meet joins;
- the unchanged checker at every step.

Additions:
- **R19 objects** (`kitchen19.py`):
  - carrot: Ø35 × 160 mm cylinder, front grasp, jaws vertical (rib tray, D fingers force mode);
  - tomato: Ø70 × 60 mm cylinder, front grasp at the equator, jaws horizontal, D fingers in position mode with a 4 mm squeeze;
  - pusher: disc + stem + keyed knob, front grasp (R11 AU/AW).
- **Contact window for food**, only in the ≤ 50 mm straight grasp approach / release retreat:
  - finger / gripper ↔ that food item may come closer than 5 mm, never touching it (`distance.py` upper bound > 0);
  - nothing else gets a window;
  - in the passing sets the food gap stayed ≥ 5.0 mm anyway: tomato 5.0, carrot 22.5.
- **Seat lift:** food is grasped and set down 8 mm above its support (the support-normal window, as r17's 8 mm seat). After releasing the tomato on the plate, the gripper lifts back those 8 mm before it backs out.
- **Union scene:** the R18b kitchen, the fridge (door closed), the faucet lever closed and open, the slicer and the lever base out, and the raw-tray items not in the hand.
- **≤ 4 mm re-check** (`r19prep_verify.py`): the stored playback is unwrapped, then subdivided joint-linearly so no robot or held point moves more than 4 mm (point bound, the `planner.edge` rule). Every state is fully checked: contacts + GJK lower-bound certificate + ranges. The approaches are re-checked in their own empty-gripper scenes with the window.
  - The stored plays contain exact 2π label jumps at the r17-style joins (R19 finding): carrot 1 row, tomato 1 row. They are unwrapped (same poses) before interpolating.
  - The first re-check without the unwrap was spurious (360° sweeps), and is not reported.

### 3.2 Results [checked]
Smoke-run files: `results/r19/prep/chain_{carrot,tomato,press}_smoke.json`, with the re-check in `*_verify4mm.json`. The defaults of `r19prepchain.py` are these passing settings.

**Carrot**
- Anchors:
  - pick at cart −1.147 (3.0 mm start reserve);
  - tap at −0.029 (15.2);
  - over the chute at −1.319 (44.5).
- Pieces:
  - tray → lane: 9.2 s, min 26 mm;
  - tap ↔ lanes: 7.1 / 12.1 s, min 5.7 mm;
  - chute ← lane: 11.7 s, min 48 mm;
  - into the chute: 0.8 s.
- Joins:
  - 191° in 3.9 s at the first lane (an arm-branch change while holding the carrot still);
  - 28° in 1.3 s.
- Approaches:
  - grasp: min 4.5 mm reserve, food gap 22.5 mm;
  - release retreat with the carrot gone (dropped into the appliance): 31 mm.

**Tomato**
- Anchors:
  - pick at −0.874;
  - tap at −0.029;
  - in front of the plate at −0.623.
- Joins: 26° and 34°.
- Approaches:
  - pick: 11.1 mm reserve;
  - release (8 mm lift + 50 mm retreat): 1.0 mm.

**Press**
- One anchor at cart −0.476, 22 states.
- The pressed state is 1.0 mm from the blade plate: the disc stops 6 mm above it by design, R11.
- Push capacity 102.5 N all along.

**Arm time, compared with the audit [est]:**
- **Single-piece cycle:** the audit estimated 30–45 s (from SD/WD + 30 %). Here the carrot is 48.6 s and the tomato 36.7 s, at r17 timing, including 9 s of rinse dwell each and the full carries between tray, sink and station.
- **Lever press:** estimated 8–12 s; here 4.6 s.
- **Caveat:** R19 smooth found r17 timing assumes unlimited acceleration, and is 20–50 % slower at the same caps with acceleration limits.

### 3.3 What failed on the way (smoke runs, kept in `results/r19/prep/explore/`)
- **Level grasp at the tap:**
  - only the R17 outlet pose itself is easy;
  - every exit tried (straight back, back and up, sideways left or right, lower rinse height) hit the cabinet doors or cabinet over x < −0.70 with the elbow, or folded the arm onto its base or the gripper;
  - pitched down 30° (carrot) / turned 90° and pitched (tomato), the exits pass.
- **Tomato with the lever at the R11 front spot or at (−0.90, 0.095):** the carry from the tray to the tap must pass the lever base:
  - over it (lift to 1.25–1.32 m), the elbow meets the door;
  - in front of it, the hand is over the robot's own base;
  - behind it, the IK jumps.

  This, together with the shoulder-sweep finding, led to the set-back spot.
- **Lever in the plating area** (0.30, 0.095 / turned / set back): the anchors and the first join pass, but the tap → lever leg never joined.
  - The cart gap at the meet was 0.5–0.8 m.
  - Moving the cart under the held tomato collides.
  - A fixed cart makes the follows fail.
  - Passing the station with the cart hits it with the upper arm.
- **Straight front slide-in at (−0.90, 0.20):** a wrist singularity (10.1–10.7° per 1 cm step) on every candidate. The diagonal (−20°) slide-in passes.
- **Release retreat at the seated height:** 1 state in the ≤ 4 mm re-check within 5 mm of the blade plate. With the 8 mm lift first, it passes.

---

## 4. Sequencing rules that follow
- **Faucet:** open it once per wash session with the checked R17 lever action (3.5 s), run the carrot / tomato sets, close it. The sets are valid with the lever in either position.
- **Work spot:**
  - The lever base and the cold box take the same spot, one at a time. The lever base is fetched from storage per use (DECISIONS 10-09; storage drawer still unmodelled).
  - The carrot set is valid with the lever base out or stored.
  - Whether the lever base or the box may stay out **during cooking** depends on the pending full hub-edge replay; the 6 stored cooking chains do not hit either [screen].
- **Slicer:** resident; nothing in the stored cooking paths reaches it.
- **Tray contents:** the tomato pad at the tray's front right, the potato at the back right (R19 tray).
  - The audit's capacity issue (8–9 channels for 15+ items per meal) is not solved here.

## 5. The user's real kitchen
The user's kitchen is L-shaped. The sink leg is the prep zone: microwave and blender 0–0.8 m from the corner, about 0.95 m of free counter, then the double-bowl sink (`inputs/user_kitchen/estimate.md`, unmeasured).
- **What carries over:**
  - The sim's left counter (1.10 m, sink to its right) is the analogue of that free counter.
  - Putting the resident slicer at the counter end away from the sink matches the real layout: next to the corner appliances.
  - The work spot sits next to the sink.
- **What does not carry over:** the cooking-corridor conflicts found here come from a hob on the same run. On the real L, the wok reaches the sink from the other leg, so the conflicts will differ.
- **Specific to the sim:**
  - the shoulder-sweep finding (keep tall fetched tools ≥ 0.2 m behind the counter edge where the cart drives past);
  - the "no back spot" finding (the upper cabinets at 1.35 m).

  Both depend on the cart mount height (1.12 m) and the cabinet height, so they need the user's measurements.
- **The user's double sink** might offer a second work spot over the second bowl. Not modelled.

## 6. Honesty notes / not done
- **Checked:** the three sets in §3.2 (planned with the r17chain method; ≤ 4 mm full re-check of every state).
- **Screen only:** the layout replays. The fast checker on stored states:
  - the 6 cooking chains and their approaches: every state;
  - hub edges: every state where replayed, but the chosen work spot's hub edges only partly (4 edges).
- **Reach probes** are single poses, not paths.
- **Not done:**
  - **Physics gate.** The wet-friction physics gate (`dyn.py`, noslip) on the new paths: the grasps are the R12 D-finger grasps, but the paths differ.
    - The carrot is turned upright and pitched under the tap.
    - The tomato is pitched and rolled under the tap.
    - `dyn.py` reads the old `chain_<P>/full.json` format, so it needs a small adapter.
  - **Hub spurs:** from each set's endpoints (the approach start and the retreat end) to H_SPAT / H_SINK (`r19hub.py` edges).
  - **Arm swap:** FR5 / CS66 runs.
  - **Peeler:** a model of the batch peeler.
  - **Staging bowl:** a new place for the R07 tomato staging bowl.
  - **Storage drawer:** the fetch / return of the lever base from storage.
  - **Rinse quality:** no sourced washing time or flow. The 3 × 3 s dwells are [est]. There is no scrub contact, so the R10 9.19 N scrub force is not used.
- **Enclosing UR5e** (`ARM=ur5e_enc`, issue #12, by another agent; `r19/arm_ur5e_enc.json` dated 16:06). The smoke runs (1 seed, 6 tries) did **not** pass:
  - press: elbow capsule vs the closed door over the sink-left cabinet;
  - carrot: no chute anchor followed;
  - tomato: no tap anchor followed.

  The full runs with more seeds are in §7. The stored cooking chains and hub edges were themselves checked with the stock capsules, so the layout screen would also need redoing with the enclosing arm.
- **Static items:**
  - the R07 tomato staging bowl overlaps the chosen lever base plate and must move;
  - the potato and greens staging bowls stay.
- **Code state:** other agents were editing `arms.py` (the `ur5e_enc` option appeared during this round). The `ARM` default stays `ur5e`; all runs above used the stock UR5e unless marked.

## 7. Commands for the controller (round 1, stock UR5e; for round 2 see §9.1. With the round-2 defaults, the stock arm needs `PRYAW=0 CHAPP=front CHUP=0,-.10,.20 LVC=F`)
```
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe

# Layout (stock UR5e)
$PY r19prep_layout.py screen                     # ~2 min; adds the rows of the chosen spots
$PY r19prep_layout.py replay NAMES=tool_CB_-0.86_0.21,cbox_CBX_-0.86_0.17,slicer_FLT NPAR=3   # ~10 min; every state of the 6 chains and of every flagged hub edge
$PY r19prep_layout.py reach NPAR=24              # all probes, ~6 min

# Prep sets, full search (stock UR5e); ~5-10 min each
$PY r19prepchain.py ACT=carrot SEEDS=2 TRIES=8 KEEP=4 TAG=full
$PY r19prepchain.py ACT=carrot SEEDS=2 TRIES=8 KEEP=4 TOOL=none TAG=full_notool
$PY r19prepchain.py ACT=tomato SEEDS=2 TRIES=8 KEEP=4 TAG=full
$PY r19prepchain.py ACT=press  SEEDS=2 TRIES=8 KEEP=4 TAG=full
# <= 4 mm full re-check of each (~2-3 min each)
for f in carrot_full carrot_full_notool tomato_full press_full; do $PY r19prep_verify.py FILE=results/r19/prep/chain_$f.json NPROC=16; done
$PY r19prep_render.py TAG=full

# Enclosing UR5e (issue #12): outputs get the suffix _ur5e_enc
$PY r19prep_layout.py reach NPAR=24 ARM=ur5e_enc
$PY r19prepchain.py ACT=press  SEEDS=3 TRIES=12 KEEP=4 TAG=full ARM=ur5e_enc
$PY r19prepchain.py ACT=carrot SEEDS=3 TRIES=12 KEEP=4 TAG=full ARM=ur5e_enc
$PY r19prepchain.py ACT=tomato SEEDS=3 TRIES=12 KEEP=4 TAG=full ARM=ur5e_enc
for f in press_full_ur5e_enc carrot_full_ur5e_enc tomato_full_ur5e_enc; do $PY r19prep_verify.py FILE=results/r19/prep/chain_$f.json NPROC=16; done
```
- `r19prep_verify.py` takes the arm from the result file.
- If an `ur5e_enc` set still fails, the next things to try are the knobs of `r19prepchain.py`:
  - `PLAN=1 PLAN_S=120` (RRT for blocked joins);
  - `PITCH`, `TROLL`, `PYAW`, `L1`, `L2` and `LANE` (the carry lanes);
  - `LEVER=x,y`.

## 8. Smoke tests run here (each < 5 min)
- **Layout map:** 26 s.
- **Screen:** 2 min.
- **Replays:** 6 chains, 41–58 s per spot; with hub edges, up to 4 min.
- **Reach batches:** 1–2 min.
- **Chain smokes** (1 seed, 6 tries, keep 1): 30–140 s each.
- **Final passing runs:** carrot 137 s, tomato 101 s, press 30 s.
- **≤ 4 mm re-checks:** carrot 117 s, tomato 39 s, press 15 s (15–24 workers).
- **`ARM=ur5e_enc` smokes:** about 2 min each; not passing (§6).

---

## 9. Round 2: the true-geometry arm `ur5e_enc2_pgc` (issue #12; 2026-10-13, after the controller's runs)

**Why.** The controller re-ran the three sets with `ARM=ur5e_enc2_pgc` (`R19_UR5E_ENC.md` §7–8): k-DOP hulls that certifiably enclose the real UR5e, plus the PGC-140 housing from DH's drawing (Ø75 body).

| Set | Controller's result (SEEDS=3 TRIES=12 KEEP=4) |
|---|---|
| tomato | pass, but only 0.07–0.14 mm reserve |
| press | fail: the approach folds the arm (upper arm `R_geom_enc2_ua_1` vs wrist 2 `R_geom_enc2_w2_1`); one candidate hits the door with the upper arm |
| carrot | fail: no "over the chute" anchor candidate could be followed |

**Answer.** All three now pass with `ur5e_enc2_pgc`, with **no layout move**. Each is checked with the unchanged rules, and every state is re-checked fully at ≤ 4 mm.

| Set | What changed | Time | ≤ 4 mm re-check: states (play + approaches), hits | Min reserve arm/held–env; self |
|---|---|---|---|---|
| **press** | The 3D-printed knob adapter is turned **45°** on the pusher stem (`PRYAW=45`); the bought stem and disc are not turned. The gripper takes the knob diagonally, so the arm no longer folds. Anchor at cart −1.274. | 4.6 s | 155 + 36 + 36, **0** | 1.0 mm (pusher disc 6 mm above the blade plate, by design, as R11); self **14.7 mm** |
| **carrot** | The carrot comes to the chute from a direction turned **30°** (`CHAPP=30`, upright waypoint `CHUP=.05,-.087,.18`), so the gripper is front-right of the chute. Chute-anchor cart −1.28. | 49.9 s | 4,022 + 61 + 172, **0** | 2.01 mm; self 2.0 mm |
| **tomato** | The lever-side anchor cart is fixed at **−0.35** (`LVC=-0.35`), giving a more open elbow at the set-back lever. | 36.5 s | 2,680 + 77 + 53, **0** | **2.22 mm in the play** (was 0.14); release 1.0 mm (finger 6 mm above the blade plate at the moment of opening: design geometry, not the door); self 1.44 mm |

- The arm can push 102.5 N on the knob along the press, unchanged.
- Max joint-load ratio is 0.38–0.46.
- Results: `results/r19/prep/chain_{press,carrot,tomato}_r2_ur5e_enc2_pgc.json` and `*_verify4mm.json`. Explorations are in `results/r19/prep/explore2/`.
- Render: `renders/r19/prep_layout_r19_enc2pgc.png`.

**What was tried** (all `ARM=ur5e_enc2_pgc`, smoke runs of 1–2 seeds; logs in `explore2/`):
- **Press:**
  - knob yaw +30 / +45 / +60 / −45 / −60°: all pass;
  - yaw −30°: no anchor;
  - unturned knob with a fixed cart at −0.40 / −1.25: fail (upper arm vs base plate, or no anchor).
  - Chosen: +45°. It has the largest self clearance (14.7 mm, against 2.3 mm for +30 / −45).
- **Carrot:**
  - from the front with a lower waypoint or a lower over-chute height: the anchor follows, but the lane join is blocked;
  - from the right side (−x): the arm hits itself on the way to the lane;
  - slicer moved 5 cm right, or the chute-anchor cart fixed: fail;
  - **30° and 45° diagonal: pass.**
  - Chosen: 30°. Both passed the ≤ 4 mm re-check (2.01 mm); 30° has the lower joint load.
- **Tomato:**
  - slide-in yaw −25 / −30 / −35°: no lever-side candidate;
  - yaw −10°: 1.4 mm;
  - **fixed lever-side cart −0.35, yaw −20 or −30°: 3.0 mm in the planning steps, 2.22 mm in the ≤ 4 mm re-check.**

**Hardware consequence.** The keyed knob adapter is still to be drawn (R12 open item 5). It is now drawn turned 45° to the lever base's front. The bought AY-403 stem and pusher disc are unchanged.

**Re-screen of the work spot with the turned knob** (candidate `tool_CBK45`; the stem is unturned, the knob's AABB is used as its envelope). The knob adapter changes the station's top. The cold-box spot and the slicer were re-screened with the new arm too.

| Spot | 6 stored cooking chains with the `ur5e_enc2_pgc` geometry (every state + approaches) | Flagged hub edges (every state) |
|---|---|---|
| work spot `tool_CBK45` | 2,003 states, **0 hits** | 8 of 8 flagged edges, 15,666 states, **0 hits** |
| cold box `cbox_CBX_-0.86_0.17` | **0 hits** | 8 of 8 flagged edges, **0 hits** |
| slicer `slicer_FLT` | **0 hits** | 0 flagged |

Notes on the re-screen:
- **Turning the whole pusher was rejected.** It turns the bought stem too, and the turned stem (AABB) came 3.35 mm from the held spatula blade on the spatula fetch.
- **Which cooking paths were used:**
  - The cooking chains are the stored UR5e chains. `R19_UR5E_ENC.md` §8.2 adopts them unchanged for `ur5e_enc2_pgc`; wok and plate 2 are certified in the `PY=.15` layout.
  - Only hits with the candidate boxes are counted, so the plating spot's y does not change the result.
  - The hub edges are the stored UR5e roadmap with the new arm geometry.
- **The screen is less conservative here.** The voxel pre-screen (which hub edges are flagged) was built from the stock geoms. Its dilation (4 cm for chains, 6 cm for hub edges, +2 cm for the fixture) exceeds the enc2 bloat plus the real arm's protrusion beyond the stock capsules (≤ 26.5 mm) plus the 10 mm gap. Even so, it is less conservative than in round 1.
- **The `PY=.15` hub is being rebuilt by the controller.** Re-screen the spots against it when it exists (§9.1).
- **Static note.** The cold-box tub (x −1.01…−0.71) is 1 cm from the counter edge at the sink. The screen lists the sink's side wall under the counter at 0 mm (AABB); there is no physical conflict.

**Defaults of `r19prepchain.py` are now the round-2 settings:**
- `PRYAW=45`
- `CHAPP=30`, `CHUP=.05,-.087,.18`
- `LVC=-0.35`

With the stock `ARM=ur5e`:
- these defaults pass the tomato (39.2 s), but the press and the carrot fail in a 2-seed smoke (other IK branches);
- the round-1 settings still reproduce 4.6 / 48.6 / 36.7 s exactly: `PRYAW=0`, `CHAPP=front CHUP=0,-.10,.20`, `LVC=F`.

The true-geometry arm is the physically meaningful model, so round 2 is the recommendation.

**Code changes this round** (my files only):
- `r19prepchain.py`: new options
  - `SLICER`, `CHAPP`, `CHUP`, `CHOV`, `CHC`;
  - `PRYAW` (turned knob object `pusher_y<deg>`), `PRC`;
  - `LVC=F`.
- `kitchen19.py`:
  - `pusher_turned()`;
  - candidate `tool_CBK45` and its turned-knob envelope.
- `r19prep_layout.py`:
  - mode `replayedges` (one process per flagged hub edge);
  - `ONLYEDGE`, `CHAINSONLY`, `HUBFROM`;
  - `HUBDIR` (screen / replay another hub roadmap; writes `layout_screen_<hubdir>.json`);
  - arm-tagged replay outputs.
- `r19prep_verify.py`:
  - **skips a failed or empty chain** and writes `{"skipped": ...}` instead of crashing (tested on the failed press);
  - takes the turned-knob object.

### 9.1 Commands for the controller (round 2; background lanes)
```
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A="ARM=ur5e_enc2_pgc"
# lane 1: full prep sets (defaults = round 2) + <= 4 mm re-check; ~5-8 min per set, ~1.5 min per re-check
for a in press carrot tomato; do $PY r19prepchain.py ACT=$a SEEDS=3 TRIES=12 KEEP=4 TAG=full $A; done
for a in press carrot tomato; do $PY r19prep_verify.py FILE=results/r19/prep/chain_${a}_full_ur5e_enc2_pgc.json NPROC=16; done
$PY r19prep_render.py TAG=full_ur5e_enc2_pgc OUT=renders/r19/prep_layout_r19_enc2pgc.png
# lane 2 (after the controller's PY=.15 hub for ur5e_enc2_pgc has its edge_*.json): re-screen the chosen spots against it
H="HUBDIR=results/r19/hub_py.15_ur5e_enc2_pgc"
$PY r19prep_layout.py screen $H $A                                   # ~2 min; writes layout_screen_hub_py.15_ur5e_enc2_pgc.json
$PY r19prep_layout.py replayedges NAMES=tool_CBK45 NPAR=12 $H $A      # ~1-2 min
$PY r19prep_layout.py replayedges NAMES=cbox_CBX_-0.86_0.17 NPAR=12 $H $A
$PY r19prep_layout.py replayedges NAMES=slicer_FLT NPAR=12 $H $A
```
If the full press or carrot run picks another DP combination that fails, fall back to the smoke settings: `KEEP=1` gives exactly the round-2 results.
