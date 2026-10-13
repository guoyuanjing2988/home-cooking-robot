# R10: orchestrator hands-on work on the tethered cart (2026-10-09)

The starting point was the R09 package (copied); R09 itself was untouched. The checker rules are unchanged: the inherited R05 reference via `checker.py`. All runs used the R09 venv with ≤4 workers.

## Design changes vs R09, and why
| Change | Why (evidence) | Flag |
|---|---|---|
| No ballast; controller off-board (tethered); two ZLTECH drive wheels + two casters; mass about 63–67 kg (R09 was 132 kg) | User: "为啥要这么重". R09 mass was 46.6 kg ballast + 13.6 kg controller + 4 drive wheels. | `dock` |
| A named dock bumper bears on the base-cabinet fronts (y=0). The cart is docked at base y=-0.21, yaw 0. Forward tip is resisted by the bumper (≤250 N, ≤μW). | Removes the need for ballast; the tip margin is about +0.08 m including the 1.5 dynamic factor. | `dock`, `mobile.dock_stability` |
| Deeper base: drive wheels moved back to -0.22 | A mandoline push away from the robot otherwise tips it backward. | `deep_cart` |
| Arm (UR5e) at 1.12 m, tilted 20° toward the counter (envelope_-20 computed), hung from a cantilever beam; mast moved back to -0.17 | A 0.85 m counter-level mount hit the sink rim. The mast and the controller were in the arm's way. Tilt 0 gives a ≈0 pan-axis envelope, so every lateral load failed. | `mount_height`, `mount_tilt_deg=-20`, `cantilever`, `mast_y` |
| Longer, higher wall spout (jet at y=.33, z≈.97) | Washing at y=.43 was under the cabinets: wrist vs rim, carrot vs spout. | `long_spout` |
| Peeler station open-top, shallow, front-loaded; the carrot is gripped with vertical jaws, the lower finger between the cradles | A top-down peel forced the elbow into the cabinets (0–2.5 mm reserves). | `peel_open`, `peel_fwd` |
| Raw tray with two ribs under the carrot; front horizontal grasp | Same elbow problem as peeling. A side grasp with fixed jaws now matches the real lying orientation. | `rib_tray`, `fixed_jaws` |
| Tools fetched per step (DECISIONS 2026-10-09); only the active step's stations are present | User decision. Per-step presence removed collisions with idle stations. | `per_step` / chain `PRESENT` |
| Mandoline raised, with the output bowl underneath; no catch tray | Removes the catch-tray pick and deliver strokes, which collided with cabinets and the wall. | `mand_raise`, `bowl_r` |

## Results (chain.py, preset AI)
- **Groups G1–G3 execute as continuous, fully checked paths:**
  - G1, raw pick: grasp on the ribs, then lift;
  - G2, wash: load under the jet, then the scrub stroke;
  - G3, peel: load, release-retreat-return (finger proximity to the just-released carrot is allowed only within the ≤50 mm release window, never penetration), then retrieve.
  
  R09 had 2/11 local strokes.
- **Connections between groups:**
  - The straight retreat and pre-approach lines and the base drive (pure x, arm frozen in carry) pass.
  - Fold and unfold between the stroke ends and the carry pose still fail on near-misses, about 9.85/10 mm and 4.96/5 mm.
- **G4, mandoline (golden holder push):**
  - Not closed. The blockers moved from window rotation tolerance (2e-4 rad), to tipping (fixed by the deep cart), to wrist/elbow at about 9.7/10 mm from the cabinet doors.
  - One AD candidate passed holder_load and the stroke, then failed the lift.
- Market research (`research/market_r10.md`) recommends replacing the mandoline with an electric vegetable cutter (华菱 HLC-300) whose chute sits in the open front strip.

## Files
- `mystat.py`: per-endpoint statics screens (presets A…AI).
- `chain.py`: group and connection execution.
- `results/chain_*/`, `logs/`: outputs.

# R11 (2026-10-10): the market tool set in the sim

Decisions: `DECISIONS.md` (2026-10-10, R11 tool set; mesh-box modelling fix). Market sources: `research/market_r10.md` §13.

## Tools modelled
| Function | Product class | Sim station | Placement |
|---|---|---|---|
| Root slicing / dicing | 卓晋 3-in-1 electric cutter (10×7 cm top chute, lid interlock) | `slicer` (`scene.py`): 33×21×20 cm body, chute walls to 28 cm, output bowl | Counter-resident |
| Tomato wedges (and greens sections via 3D-printed plates) | AY-403 class lever cutter base | `lever_base`: blade plate, guide rails, round 110 mm pusher disc with knob | Fetched (per-step presence) |
| Peeling | open cradle peeler (abstracted transformation) | `peeler` (cradle depth 35 mm, `peel_hover` 1 mm) | Fetched |
| Grasping 30–80 mm produce | 3D-printed finger pads | `finger_offset=.015`, per-object `jaw_q` | — |

## Results
**Carrot (preset AS): closed end-to-end.** `results/chain_AS/full.json`, 6,367 states, every state fully checked.
- Groups: raw pick (rib tray) → wash load + scrub → peel load, release/return, retrieve → vertical drop into the slicer chute, release, retreat.
- Connections: C1, C2 and C3 all pass as direct carry transitions (retreat → fold → pure-x drive → unfold → pre-approach).
- Continuity: the largest joint/base step is 0.0047. The only jaw event is the chute release. Base travel is 1.97 m. Motion-only duration is about 24 s.

**Tomato (preset AT/AU).**
- Groups pass:
  - pick from a 45 mm pad;
  - rinse under the jet;
  - slide in 6 mm above the blade plate, then set down;
  - release-retreat (release-window rule);
  - knob grasp, 102 mm press, return, release.
- Push capacity is about 100 N along the whole press. The limit is the keyed grip (150 N key / SF 1.5), not the joint torque. The tomato wedging force is still unsourced.
- Connections: C1 and C2 pass. C3 (release → knob grasp) failed with the top-down knob grasp: the shoulder flips about 140° and the cart moves 66 cm. AU switches to a front knob grasp (same posture as placing).
- **Preset AW closes the tomato end-to-end.** `results/chain_AW/full.json`, 6,653 states, every state fully checked.
  - Layout: front knob grasp, station 35 mm forward and 30 mm lower.
  - Continuity: the largest joint/base step is 0.0072.
  - Jaw events: tomato release, pusher close and pusher release, plus the empty-gripper jaw interpolation during C3.
  - Base travel is 1.74 m. Motion-only duration is about 25 s.

## Root causes found and fixed this round
1. **Joint wraps.** The ±2π joints left independently solved groups 1–2 turns apart.
   - `normalize` shifts whole groups.
   - `first_stroke` wraps each group start to the nearest reference.
2. **IK branch changes between groups** (elbow sign, shoulder flips). `SEQ` mode now solves groups in order: warm-started from the previous group's end, candidates ranked by joint distance, with a fallback to any branch.
3. **MuJoCo 3.2.5 box-box distance inside the margin is wrong.**
   - Standalone it is 0.500×; along real paths 0.39–1.4×.
   - Mesh-box and capsule-box measure 1.000×.
   - Fix: `mesh_tool` (tool-side boxes become box meshes), and produce/pusher are cylinders.
4. **Arm self pairs (capsule-mesh) are also off in MuJoCo.** The planner slack uses the exact GJK bound for self pairs.
5. **Loose stroke IK on seats.** The inherited 5 mm / 3° tolerance tipped the carrot 4 mm into the cradle.
   - `refine` polishes each group start.
   - `precise_line` tracks windowed seat/lift strokes at 1 mm steps within 0.5 mm / 0.2°.
6. **Connection planning.**
   - `planner.plan_swept` is a leveled, swept-sampled RRT-Connect; full replay still decides.
   - `connection` screens 7 compact carry candidates with direct edges first, then targeted RRT fallbacks.
7. **Mirrored jaw sense** misplaced offset held items. The tomato and the front-grasped pusher now use a single jaw sense.

## Files (new or changed this round)
- `chain.py`: groups G1–G4S and GT1–GT4; `SEQ`, `N` (normalize) and `A` (assemble) modes; connection screening.
- `planner.py`: `plan_swept`, `slack`, `swept`.
- `scene.py`: slicer, lever base, tomato pad and cylinder, finger pads, `mesh_tool`.
- `checker.py`: cylinder/mesh held extents, keyed pusher grip, `wedge_load` window, `peel_hover`.
- `solver.py`: warm-start ranking.

### R11 replay videos
`video.py <preset> <out.mp4>` renders a closed chain (`results/chain_<P>/full.json`) with MuJoCo:
each motion frame is a checked state, using the checker's collision geometry and the per-segment held/scene state as checked in `chain.py`.
Jaw open/close frames and process holds are inserted and captioned; the on-screen timer counts motion only (arm 0.8 rad/s, base 0.25 m/s).
For the carrot, the G3 release / return (checked in `chain.py` but not stored in `full.json`) is replayed as the reversed and then forward `peel_load` path with the jaws open.
The inset is a tool close-up with the arm links and upper cabinets drawn translucent.
Output: `renders/carrot_AS.mp4`, `renders/tomato_AW.mp4` (about 31 s each).

#### Dressed render (dress.py)
`dress.py` gives the render model its look, and the checker never uses it:
- the UR5e visual meshes from MuJoCo Menagerie (`sim/r01/concept/sources/menagerie/universal_robots_ur5e`);
- RoboCasa textures in the user's kitchen colours (warm wood cabinets, dark red-brown granite, white tiles, stainless);
- RoboCasa food meshes (tomato, carrot, potato, lettuce);
- two shadowing spot lights and a skybox.

Food meshes are fitted inside the checked shapes and verified. For example, the carrot visual is 15.5 × 3.4 cm and its checked mesh is 16 × 3.5 cm.

Checked geometry stays in the model, moved to geom group 5 (not drawn). The arm collision capsules, the camera-side walls and the stove keep-out envelope are hidden the same way.

RoboCasa 1.0.1 is installed only as an asset library, under `sim/vendor/robocasa` with the conda env `robocasa`. Rendering still runs in the checker venv (MuJoCo 3.2.5).

The earlier collision-geometry videos are kept as `renders/*_geom.mp4`.

### R11 dynamics check (dyn.py), 2026-10-11
`dyn.py` re-runs the handling steps of a closed chain with MuJoCo rigid-body dynamics, and the food is never welded.

**Setup:**
- **Gripper:** a floating copy of the R_tool subtree, welded with a stiff mocap weld to the planned tool pose. Timing is trapezoidal: 0.8 rad/s and 0.25 m/s, 0.5 s ramps, stopping at every joint-space corner.
- **Jaws:** synchronised by an equality constraint and run in force mode (PGC-140-50 minimum, 40 N per jaw).
- **Food:** a free body. The tomato is an ellipsoid 70×70×60 mm, 0.15 kg; the carrot is a capsule Ø35×160 mm, 0.12 kg.
- **Friction:** set on both the food and the pads, because MuJoCo takes the max of the pair.

**Not simulated:** cutting, peeling, water, tomato softness and crushing, controller error.

| Case | μ | Tomato | Carrot |
|---|---|---|---|
| Current design (fingertip pinch; tomato gripped 20 mm above centre) | 0.6 | drops in C1 | drops in C1 (into the sink) |
| Pads +30 mm, item mid-pad, tomato at its equator | 0.6 | slip 8 mm, ends on the blade plate | slip 4 mm, cradle and regrasp ok, drops into the chute |
| same | 0.3 | slip 7.8 mm, 2°, on plate | slip 3.9 mm, in chute |
| same | 0.2 | slip 7.8 mm, 1°, on plate | slip 3.8 mm, in chute |

**Root causes found:**
1. The R_tool TCP sits at the fingertip, so items are centred on it. Contact is in the last 2.5 mm of the 37.5 mm pad that protrudes past the palm, and a round item is squeezed out.
2. `TOMATO_DZ`, a grip 20 mm above the centre, puts the contact normal about 30° off horizontal, so it needs μ > 0.58.

The geometric checker cannot see either problem because it models the tomato as a vertical-walled cylinder and keeps held items welded.

**Caveat:** the +30 mm what-if replays the old checked paths with the longer pads and the shifted item. Those geometries have **not** been through the clearance checker. The chains must be re-planned with the new pads before this counts as closed.

Physics video: `renders/physics_grasp.mp4` (`dynvideo.py`).

**Debugging lessons**, so the earlier false failures are not repeated:
- Prescribing robot joints by resetting qpos/qvel with a large armature gave non-physical contact creep.
- Independent force-limited jaws let the item and jaws float sideways.
- A position-mode jaw gives a grip force that drops with closure.

# R12 (2026-10-11): finger and hand design study

The user asked for many options, with the fingers and hand designed in-house (3D printing etc.). Everything below runs with the dynamics gate from R11, with one correction (next paragraph). Research inputs live in `robot_rail/research/finger_design_inputs.md` (PGC-140 interface, tomato damage, friction, Fin Ray) and `robot_rail/research/hand_options.md` (other grippers, UR5e tool flange).

**Correction to the R11 dynamics result.** With `NOSLIP=10` (MuJoCo no-slip solver, exact Coulomb friction), the stock fingers **hold** at μ ≥ 0.6 and **drop** at μ 0.3. The R11 statement "drops in C1 at μ 0.6" was inflated by soft-contact creep, which makes low-force grips sag slowly even below the friction limit. The tomato agrees with hand theory: a grip 20 mm above centre needs μ > 0.58. The R11 decision (longer fingers) stands, but the reason is no margin on wet friction, not a certain drop. From R12, every grasp check runs with noslip on.

**New constraint from the research:** a tomato stays undamaged below about **11 N** of clamping force (Zhou 2022, padded plates), and a design guideline gives **< 10 N per finger** (Zheng 2022). The PGC-140-50 **cannot go below 40 N per jaw** in force mode. Its manual says it moves to a position target and stops early only at the current limit, so a compliant finger driven in position mode can set a lower force.

## Designs (`fingers.py`)
All designs put the item centre at the TCP and **grip at mid-pad**: the pad protrudes 75 mm (Fin Ray 85 mm) past the housing face, the item centre sits 45 mm in front of the face, and a 20 mm crank lifts the housing above the pad centre. The tomato is gripped at its equator (`tomato_dz` 0).

| Key | Design | Pad | Closed half gap |
|---|---|---|---|
| — | stock (R11) | rigid stub, item at the fingertip | 0 / 15 mm |
| L | long flat | 4 mm TPU on PETG, 40 mm tall | 15 mm |
| V | horizontal V groove (cradle) | 30° faces, 40 mm wide groove, 46 mm tall | 22.5 mm (rims 11 mm) |
| K | pyramid pocket | 4 faces at 30° around the TCP | 22.5 mm |
| R | Fin Ray | PRB linkage: 6 front/back strap segments, ribs tilted 25° to the tip, about 0.8 N/mm at mid-span (Festo DHAS-80 ≈ 1.0 N/mm) | 15 mm |
| D | **dual zone** | rigid PETG rims at abs(z) ≥ 19 mm, flush with the datum; a sprung soft centre (1.5 N/mm, 6 mm travel, protrudes 1 mm) | 16 mm |

Each planning model uses one convex box hull per finger, so the checker's grasp registry is unchanged. The dynamics model (`dyn_parts`) has the real faces, facets, linkage or sprung pad. `finray_cal.py` checks the Fin Ray stiffness and wrap.

## Dynamics sweep (old R11 paths, noslip, 174 runs)
`jobs/j7.txt` and `j8.txt`; `sweep_table.py` gives the table, and `renders/r12/sweep_heatmap.png` the figure.
- **Tomato:**
  - Stock drops it in 10/12 conditions.
  - L, V and D at 40 N pass all 12 (μ 0.1–0.6, Ø60/80 mm, ±8 mm and 6 mm offsets), but **40 N per finger is about 4× the damage limit**.
  - K fails the large tomato. The Fin Ray at 40 N fails only the worst case.
- **Gentle tomato grasp (D, position mode, 6 mm squeeze):** about **5 N per finger** median (transient max 10 N). It holds at μ 0.1–0.3, for Ø60 and Ø80 (0.22 kg), and with an 8 mm or 6 mm offset.
  - It fails in the combined worst case (Ø80, 0.22 kg, μ 0.2, 8 mm off).
  - It fails when the width estimate is **2 mm too large** at μ 0.2; 2 mm too small is fine. The robot must know the tomato width to about ±2 mm, e.g. from an RGB-D camera.
  - At a 4 mm squeeze (3.5 N) it slips at μ ≤ 0.2.
- **Carrot (40 N):**
  - V passes all 12 conditions.
  - L, K and D pass everything except the Ø28 carrot (the jaws close fully before touching: the stroke budget) and the Ø40 carrot, which the 35 mm peeler cradle twists by about 36°. That is a station sizing issue.
  - The Fin Ray fails, because a 35 mm carrot leaves it only 2.5 mm of jaw travel, about 2 N.
- **A low-force hand** (a gripper that could clamp at 8 N in force mode): L, V, D and the Fin Ray all hold the tomato at μ 0.1–0.3, and 25 N holds the carrot with L, V and D. With such a gripper no width estimate is needed.

**Why not V, K or the Fin Ray on the PGC:**
- V and K: the raised groove edges cut the open width, so a 70 mm tomato has only about 1 mm clearance at release. The WV re-plan fails the tomato release-retreat (−2.5 mm).
- Fin Ray: it needs ≥ 10 mm of squeeze per jaw, so with a 50 mm stroke it cannot cover Ø30–80 mm (see `hand_options.md` §0).
- **D gets around the stroke budget:** hard items press the soft centre back and bear on the rigid rims, while round items touch only the soft centre.
- D range on the PGC: carrot ≥ Ø33 mm, tomato ≤ Ø78 mm.

## Hand options (`research/hand_options.md`)
- **Off the shelf, no gripper is both gentle and waterproof.** Only the OnRobot RG2 / RG2-FT (3–40 N, 110 / 100 mm), the Robotiq 2F-140 (10 N spec, **15 N measured** in its manual) and the discontinued Weiss WSG 50-110 (5–80 N) reach ≤ 10 N with ≥ 80 mm stroke. All are IP54 or worse. Every IP67 option (PGC-140-50, Robotiq Hand-E, OnRobot 2FG7/2FG14) has a minimum force of ≥ 20 N.
- **RG2 caveats:** ±25 % force deviation; 40 N max (a 40 N setting may give 30–50 N), so it has little margin for scrubbing the carrot.
- **DIY servo hand:** an XM430-W350 has current-based position control and runs on the UR's 12 V and RS485, but no Dynamixel is IP-rated.
- **Recommendation:** keep the IP67 PGC-140-50 with the D fingers and position-mode tomato grasps. Treat an RG2-class gripper as the fallback if the width estimate proves unreliable. Buying one is the user's call.

## Printable parts (`cad_fingers.py`, build123d in the conda env `robocasa`; output `cad/`)
- **finger_body:** PETG, food-contact grade, e.g. Kimya PETG-S natural. 27 cm³, one solid. Jaw mount: 2× M4 counterbored plus a Ø3 dowel pin. Rigid rims and the pad pocket.
- **pad_carrier:** PETG. Floats on 2 stainless compression springs (about 0.75 N/mm each) on 2 M3 shoulder screws, which are also the stops. Travel 6 mm.
- **pad_skin:** TPU 92A, food-contact grade (Kimya), with a 3 mm grid of 1.0 × 0.8 mm grooves (texture finding in Guo 2017). Alternatively cast Smooth-Sil 940 in **pad_mold**.
- STEP and STL files for the minus and plus (mirror) fingers, plus `finger_D_minus_assembly.step`. Render: `renders/r12/finger_D_cad.png`; gallery of all designs: `renders/r12/finger_gallery.png`.
- **Check before printing:**
  - the jaw hole layout, read from the manual drawing: line direction and position are assumed, so check DH's STEP file;
  - the spring part numbers;
  - the knob adapter of the lever cutter: it must be about 34 mm wide so the rims clamp it, and it is not yet drawn.
- **PGC moment check:** 40 N at 45 mm out and 20 mm crank gives about 2 N·m, against an allowable 7 N·m.

## Re-planned chains with the new fingers (clearance checker + physics gate)
Presets: `S<k>` is the carrot chain from AS and `W<k>` the tomato chain from AW, each with finger design k (`mystat.py`). Driver: `replan.py`, which runs SEQ, N, C1–C3 and A.

| Chain | Clearance re-plan | Physics gate (noslip) |
|---|---|---|
| **SD** carrot, dual zone | closed, 7,431 states, max step 0.0049; carrot ~28 s | μ 0.15/0.2/0.3 and +8 mm offset: slip ≤ 0.4 mm, in the chute. Ø32: dropped (below the Ø33 minimum). Ø40: the 35 mm peeler cradle twists it 36° |
| **WD** tomato, dual zone, position mode with 6 mm squeeze | closed, 5,992 states, max step 0.0067; tomato ~22 s | μ 0.15–0.3, Ø60, Ø80 0.22 kg and +8 mm: on the plate within 1–3 mm at **≈ 5 N per finger** (p95 6 N). Width estimate 2 mm too small: OK at 6.8 N. **Width estimate 2 mm too large: rolls off at μ 0.2** |
| SL carrot, long flat | closed, 7,432 states | μ 0.2/0.3: slip 0.3 mm, in the chute |
| WL tomato, long flat, 40 N | closed, 5,982 states | μ 0.2/0.3: slip 0.2 mm, but **40 N per finger, which bruises the tomato** |
| SV carrot, V groove | C1 fails | — |
| WV tomato, V groove | the release-retreat fails, with the rims 2.5 mm into the tomato | — |

**Fixes needed on the way:**
- **SD C1 (raw tray → sink).** Every direct fold was rejected on the forearm vs the cart mast at 9.4–9.99 mm (the gate is 10 mm), and a 1,600 s RRT failed too. SL's C1 path has the same endpoints and passes the SD model, so `transplant.py SL SD 1` replays every edge with the SD model (`edge()`, ≤ 4 mm steps).
- **WD/WL C1.** The unfold to the sink swept wrist 2 through the arm base plate. The fix bridges from the old AW C1 (`transplant.py AW WD 1`): end gaps 0.044 and 0.076 rad are joined by direct edges and everything is re-replayed with the new model.
- **WD/WL C3.** GT4 had fallen back to a far IK branch (elbow flip, 68 cm cart move) because lifting the open gripper 6 cm **up** after releasing the knob brings the upper arm 9.86 mm from the closed cabinet door, under the 10 mm gate; the housing now rides 20 mm higher on the crank. GT4 now retreats straight **back** (−y, 6 cm) when the lift fails. Re-running GT4 with `SEQREF=1` keeps GT3's branch, and C3 then passes with a direct carry.
- Earlier attempts are kept as `C1_try*.json`, `C3_try1.json` and `GT4_try1.json`.

Physics video: `renders/r12/physics_fingers.mp4`. Stock vs dual zone, tomato and carrot, μ 0.3, on the new paths.

## Open items
1. **Tomato width:** the gentle grasp needs the width to about ±2 mm, from RGB-D or by closing the PGC in position steps until a pad force sensor (an FSR under the soft carrier, about ¥20–50) reads about 6 N. I recommend the sensor; it removes the width estimate.
2. **Big tomatoes (Ø80):** the rims engage at about 5.8 mm squeeze, causing transient 33 N peaks. Either use a size-dependent squeeze of about 5 mm, or move the rims further out in z (bounded below by the 5 mm plate clearance).
3. **Carrots below Ø33 mm:** grip them where they are thick (vision), or use fo = 14 (carrot ≥ Ø29, tomato ≤ Ø74).
4. **Peeler cradle:** size it for Ø40.
5. **Lever-cutter knob adapter:** 34 mm wide, keyed for the press; not drawn yet.
6. **Jaw interface:** verify the hole pattern against DH's STEP file before printing.
7. **Not simulated:** water, the cutting force, and tomato visco-elasticity (it was modelled as a rigid ellipsoid).

# R13 (2026-10-11): every ingredient, not just carrot and tomato

The user asked for this: "你要考虑各种各样的食材哈，都要能工作". The R12 dual-zone finger is generalised to a hand system for about 40 ingredients. The system is checked in a new physics bench, one run per item, method and condition.

Inputs:
- `robot_rail/research/food_catalog_inputs.md` / `.json`: sizes, masses, **per-finger damage limits** and friction for 42 ingredients, with sources and tags (M measured / der derived / est estimate).
- `robot_rail/research/finger_change_and_food_eoat.md`: finger quick-change systems, long-stroke IP67 grippers, and food end-effectors.

## Bench (`foodbench.py` rigid items, `softbench.py` non-rigid; MuJoCo 3.2.5, noslip 10)
- **Gripper:** a floating PGC-140-50 (synchronised jaws, PGC housing) welded to a mocap target. The fingers come from `foods.SETS` and are built by `fingers.dyn_parts`.
- **Items:**
  - RoboCasa meshes (convex parts) resized to the catalog's Chinese retail sizes (`foodmesh.py`), or primitives.
  - Non-rigid items (`softfoods.py`) are lumped multibody models. Flex FEM went unstable at meat masses and stiffness.
    - Chains with ball-joint bending stiffness E·I/L for meat and fish.
    - Bunches: a rigid base plus leaf chains (scallion, chives, spinach, bok choy, celery, enoki).
    - A tofu block; silken tofu in its box.
    - Bulk pieces in a handled basket.
  - Items are free bodies, never welded.
- **Script (per run):**
  - settle in the raw tray;
  - camera-style grasp point: the widest section at the centroid, yaw aligned to the long axis;
  - approach, close, lift 120 mm;
  - carry 0.65 m with a 90° yaw and two 45° tilts, one about the jaw axis and one about the pad axis;
  - place in a Ø240 bowl or a 0.5 × 0.34 m tray.
- **Motion profiles:**
  - **stress**: 3 m/s², 0.6 m/s, 2 rad/s, plus a **7.5 m/s² protective stop** mid-carry. That is about 2.5× the planned chains (SD/WD peaks are 1.2 m/s² and 1.8 rad/s).
  - **常速 / chain**: 1.2 m/s², 30° tilts, no stop.
- **Pass:** all of the following.
  - Not dropped, and in-grip slip < 10 mm. For bunches, rotation is allowed; they may hang.
  - In the target.
  - Peak per-finger normal force (10 ms window) ≤ the catalog damage limit.
  - PGC jaw moment ≤ 7 N·m.
  - Unstable runs are invalid.
- **Grip force policy (`foods.pick_mode`):** as high as is safe, not the bare minimum.
  - F = min(limit/1.4, max(2 × the rule hold force, the gripper's force-mode minimum), gripper max, PGC 7 N·m at the pad).
  - The rule is cook_ref's **SF 1.5 at wet μ 0.15**.
  - Force mode when F ≥ 40 N (PGC). Otherwise **position mode closed on a finger-root force sensor**: 20 mm/s to first touch, then 0.05 mm steps (the PGC's position resolution), then hold.
- **Finger sets (`foods.SETS`, dual-zone with a self-aligning rocking pad ±8°):**
  - The PGC's 50 mm stroke covers only about 40 mm of item width per set.
  - Neighbouring sets overlap by 16 mm, because round items need the soft centre's travel to build force.
  - **PGC: 7 sets.**
    - P1 5–45 mm, P2 29–69, P3 53–93 and P4 77–117 cover every item except cabbage and napa cabbage.
    - P5–P7 (101–189) are for heads.
  - **Hand-E 100 mm: 3 sets** (H1 5–95, H2 79–169, H3 153+).

## Three grasp methods besides the plain pinch
1. **Supported grasp (托底叉)**
   - Items rest on a **V-rib slot tray**: 35 mm ribs, a channel every 34 mm, V tops that centre round items.
   - The gripper comes in horizontally with the jaws **vertical**. A narrow 16 mm lower finger (a two-tine fork for items ≥ 150 mm long) slides under the item in a channel. A light clamp comes from above.
   - The **lower finger carries the weight**, so friction is only needed against horizontal accelerations.
   - Release: pour from above the bowl rim (open 10 mm, tip the fingertip down 55°), or set the item down on another slot tray.
   - Planner constraint: keep the jaw axis within 20° of vertical while carrying.
2. **Side-handle basket (带提手小筐)** for bulk, tiny or very fragile items.
   - A Ø200–220 basket with drain holes and a keyed 30 mm knob on a side arm, gripped at 40 N.
   - Carried level. Poured by a slow 130° tilt with the basket bottom 10 mm above the target rim.
   - A bridge handle over the top jammed the lettuce and the beans; the side handle fixed both.
3. **In its box (连盒)** for silken tofu: the box is gripped by position control at about 11 N and poured out.

A catch-lip (托唇) variant was tried and rejected. During closing the lips wedged under round items and popped them out of the cradle's open sides.

## Results
**Rigid items:** 702 runs (`jobs/r13/m3.txt`, `results/r13/`). The table comes from `r13table.py` (`results/r13_matrix.json`); figure: `renders/r13/matrix_rigid.png`.
- **Pinch at wet μ 0.15, every size, stress profile:** carrot, ginger, onion, lotus root, peeled yam, apple, chili, shiitake (by the cap), king oyster, egg (about 7 N), celery stalk, garlic clove.
- **Pinch needs μ ≥ 0.3:**
  - potato, corn, pumpkin piece, tomato (about 8 N), cherry tomato, cucumber, garlic head;
  - cabbage on PGC P7 at 60 N, moment-limited.
- **Pinch needs μ ≥ 0.5:** daikon, zucchini.
- **Pinch fails at every μ:**
  - Eggplant, because of its 10 N estimated limit (Hand-E passes at μ ≥ 0.3).
  - Bell pepper (3 N estimate).
  - Strawberry (0.6 N "safe" value).
- **Supported grasp at μ 0.15, every size:** carrot, potato, daikon, ginger, onion, lotus root, yam (also at 0.1), corn, apple, pumpkin, **tomato**, cucumber, **zucchini**, king oyster, egg, celery. Eggplant passes at normal speed; the largest (345 mm) fails.
- **Heads:**
  - **Cabbage** (1.9 kg): PGC P7 needs μ ≥ 0.3 at 60 N and 6.6 N·m, close to the 7 N·m limit. Hand-E passes at μ 0.15.
  - **Napa cabbage** (2.8 kg): the PGC fails on the jaw moment (7.3–11 N·m). Only a small napa (1.7 kg) passes at μ ≥ 0.3. Hand-E passes at μ ≥ 0.3. Otherwise, have it halved.

**Non-rigid items:** 53 runs (`jobs/r13/s3.txt`, `s4.txt`, `results/r13s/`). Table from `r13soft.py` (`results/r13_soft.json`).
- **Chicken breast and pork:** pinch at 40 N (limit 56) at μ 0.15 ✓; supported grasp ✓.
- **Whole fish:** at mucus μ 0.12 the supported grasp holds it at 16 N ✓. A pinch needs 74 N (no damage data, so not recommended).
- **Fish fillet** and **firm tofu** (μ 0.1): supported ✓ at 13–14 N (tofu limit 15). The tofu pinch fails.
- **Silken tofu:** in its box ✓, but the pour drops it about 10 cm (likely breaks). This needs a slide-out at floor level, not yet modelled.
- **Bunches gripped at the base:**
  - chives (40 N, limit 140), spinach (crown, 40–53 N), enoki ✓ at μ 0.15;
  - bok choy ✓ at μ 0.3 at normal speed, and ✓ supported at μ 0.15;
  - scallion ✓ only at μ 0.3 at normal speed, because its 16.5 N limit leaves no margin;
  - celery bunch ✓ supported (stress); at normal speed only 80 % of its segments land inside the tray, so this placement fails the 90 % gate (cause not yet inspected).
- **Side-handle basket:** bean sprouts, shrimp, garlic cloves, green beans, strawberries, cherry tomatoes, bell peppers and a lettuce head: 100 % in the target.
  - Equivalent drop 6–9 cm; shrimp 13–14 cm.
  - Bean sprouts are modelled 5 mm thick, versus 2.3 mm real, for solver stability.

**Video:** `renders/r13/foods_physics.mp4`, 16 tiles. It includes the tomato pinch at μ 0.15 dropping and the supported fork holding it.

## Printable parts (`cad_r13.py`, build123d in the conda env `robocasa`; output `cad/r13/`, render `renders/r13/cad_parts.png`)
- **jaw_adapter:** bolted to each jaw, stays on. A 60° dovetail tongue plus a cross hole for the lock pin.
- **finger_P1 … P8:** a socket that slides onto the tongue; a spring-loaded Ø4 stainless lock pin with its head outside the +z face.
  - Grip force and pad-plane loads bear on the dovetail. Only pull-off is held by the pin (steel, in shear).
- **fork_P2:** two tines and a bridge.
- **finger_rack_2pairs:** nests plus pin-lifting ramps.
  - Park: lower into the nest (the ramp retracts the pin), then lift out.
  - Pick: lower the jaws into the parked fingers, then move sideways off the ramp.
  - This is the Schunk BSWS-R "vertical in, horizontal out" pattern.
- **slot_tray_section:** 150 × 240.
- **food_basket:** Ø200.

This CAD is a concept; the jaw hole pattern still has to be checked against DH's STEP file.

## Not done yet / open
1. **Wet friction of our pad is unmeasured.** It decides between pinch and supported grasp for about 10 items. A tilt-table test with the TPU/silicone pad on wet produce is cheap and replaces every μ assumption.
2. **The bench is a floating gripper.** The kitchen chains (arm reach, clearance, cart) are not re-planned for top-down tray picks, horizontal supported grasps, finger swaps or basket pours. Next step: re-plan at least tomato (supported) and one basket item in the kitchen.
3. **Damage limits are mostly estimates** (eggplant, pepper, daikon, celery, scallion, cherry tomato). Pour impacts (6–14 cm equivalent) are not compared with any drop-damage data.
4. **Napa cabbage on the PGC:** the jaw moment limit allows only small heads. Hand-E (100 mm, IP67) or pre-halving would solve it. Buying is the user's decision.
5. **Silken tofu slide-out; scallion and bok choy at wet μ 0.15** (basket or long tray, not simulated); **the largest eggplant on the fork.**
6. **Not simulated:** water, cutting, real leaf and fruit deformation (lumped or rigid models), and a finger swap in the rack (mechanism designed, not run in physics).

# R14 (2026-10-11): staples, seasonings and the fridge, sized from Wang Gang's recipes

The user said: "最终目标就是按王刚食谱做菜真的能做出来，所以你还要再设计下米面粮油，调料的存取，还有冰箱".

Inputs:
- `robot_rail/research/wanggang_recipes.md` / `.json`: 42 recipes taken from his own channel's subtitles. Every seasoning event is recorded with grams where he states them (37 %) and with timing.
- `robot_rail/research/r14_storage_market.md`: dosing components, home and commercial seasoning machines, rice and oil handling, drawer and auto-opening fridges, opening forces, staging-time rules.

Domestic CNY prices are mostly missing: the Taobao read needs the user to click Allow in Chrome.

## What the recipes demand
- **Core seasonings (≥ 7 of 42 dishes):** 盐, 白糖, 醋 (white + dark), 生抽, 老抽, 味精, 鸡精, 胡椒粉, 料酒, 蚝油, 豆瓣酱, 淀粉/水淀粉, 花椒, 干辣椒, plus oil and 明油.
- **Doses:** 0.5 g (salt, 鸡精) up to about 55 g (sugar/vinegar in sweet-and-sour). Powders need about ±0.2 g, liquids about ±0.5 g.
- **Per dish:** median 8 seasonings and 4 wok addition events, 3–4 pre-mixable bowls.
- **Timing:** in 30 of 39 wok dishes the end of the stir-fry has 3–4 additions only 3–5 s apart (estimated from his wording). His own stated gaps include 0 s (豆瓣 with the meat) and 10 s.
- **Starch:** 水淀粉 bowls must be re-stirred just before pouring.
- **Edge pours:** in 17 dishes soy, vinegar or wine goes along the wok edge.

## Design (proposal)
- **Seasoning station in the upper cabinet next to the hood** (`cad_r14.py`; render `renders/r14/cad_station.png`):
  - **12 stepper peristaltic channels:** brine 26 % (salt), syrup 66 % (sugar), MSG 30 %, 生抽, 老抽, 料酒, 2 vinegars, 蚝油 (4.8 mm BPT tube, slow), 香油, 红油/花椒油, stirred 水淀粉.
    - Salt and sugar are pumped as solutions because they cake above about 75 % / 86 % RH, and Singapore runs at 70–90 %. This is the approach Tineco's home machine uses.
  - **Oil:** a 5 L jug in a base cabinet, pumped up.
  - **4 sealed agitated augers with desiccant:** 鸡精, 胡椒, 花椒面, 玉米淀粉.
  - **2 lead-screw syringe extruders:** 豆瓣酱 and 甜面酱; swap the cartridge for 番茄酱 / 黄豆酱.
  - **A 花椒 vibratory feeder.**
  - **Under the cabinet:** one nozzle head and a 0.1 g weighing platform with a magnetic stirrer, dosing every channel by weight into robot cups (Ø70×75 stainless). Rare items (干辣椒, 八角, 桂皮, 冰糖, 豆豉, 泡椒, 火锅底料 …) go in a weekly cup kit the user fills.
- **Rice and flour module in another upper cabinet:**
  - A 5 kg rice hopper and a 2 kg flour/starch hopper, each with a metering auger to an outlet over a weighing platform.
  - The arm washes the rice at the sink (pot + strainer lid), adds water by weight, and loads a rice cooker that can be started remotely. The Mi Home MIoT spec of one cooker lists a Start Cook action; the alternative is an SR-AX1-type cooker that loads rice and water by itself.
  - **Deep-frying:** a fryer with oil filtering and storage (Tefal Oleoclean class) instead of 0.75–1.5 L of hot oil carried in the wok.
- **Into the wok: robot cups, plus the rotary 4-compartment pour drum (分格转筒料盒; `pourbox.py`, CAD `cad/r14/drum.step`).**
  - The drum is Ø80×140 mm with 4 compartments along its axis. Each compartment has a slot; the slots are staggered at −75/−25/+25/+75° from the top, so all slots face up while it is carried.
  - The arm holds the knob and rolls its wrist: roll 120/170/220/270° and the compartments empty one by one. Gaps between additions are set by the arm and can be ≥ 1.3 s.
  - A tiered-divider box was tried first and rejected (`pourbox_tiered_rejected.py`): granules only pass a divider once the box is past vertical, so everything came out at once.
- **Fridge (the user's single-door fridge; size and placement estimated, as the user asked):**
  - Assumed: 0.55 W × 0.60 D × 1.45 H, standing just left of the counter run, hinge on the far (left) side, vertical bar handle on the robot side at 0.95–1.25 m (`kitchen14.py` option `r14_fridge`).
  - The cart stays on its dock at the leftmost dock position (x −1.48). The tether channel and floor envelope end at the counter end.
  - **Robot cold box (冷藏料盒) in a door bin at 0.85 m:**
    - a 0.30 × 0.08 × 0.10 m tub (2.4 L) with a short bridge bar 0.11 m above the rim over its centre;
    - the arm pinches the bar from above, so the box hangs with no carrying moment;
    - the user loads the dish's cold items into it (meat, tofu, eggs …), like the weekly cup kit;
    - the shelves and the rest of the fridge stay for people.
  - **Sequence:**
    1. Grasp the handle (form closure, as in `doorbench.py`) and swing the door to 35° along the hinge arc.
    2. Release the handle and pinch the box bar.
    3. Lift 70 mm over the bin lip, slide 0.33 m along the door past its free edge, and set the box down on the counter end beside the cart (box along y at x −1.70, y 0.18).
    4. Grasp the handle at 35° and swing the door shut.
  - **Estimated time per fetch:** about 25 s (open ~7 s, box out ~9 s, close ~6 s); the door is open for about 15 s. Putting the box back takes about 20 s. These are assumed arm speeds, not measured.
  - **Grip:** with the box up to 1.5 kg loaded, the pinch must be ≥ 96 N at wet μ 0.15 (SF 1.5, ×1.3 for acceleration, which is an assumption). The PGC gives up to 140 N.
  - **Fallbacks:**
    - a stiff seal (> ~100 N, PGC jaw-moment estimate) or a door that will not stay open: assisted opening (Bosch/Siemens Door Assistant via Home Connect, Samsung Auto Open Door);
    - a drawer fridge with assisted opening (F&P CoolDrawer + OPEX1, SGD 5,000) mounted at counter height.
  - Raw meat and seafood stay out ≤ 1 h at 30–32 °C, counted cumulatively.

## Evidence
1. **Reach and clearance** (`kitchen14.py` adds the stove items, hood, ports, cup rail and, optionally, the drawer fridge (`r14_drawer`); `r14reach.py` runs 96-start collision-aware IK with the unchanged checker, docked cart). 148 probes in `results/r14/reach_*.json`.
   - **Cup at the seasoning port:**
     - ✓ at y 0.30, z 1.05–1.20 (reserve 7–23 mm);
     - y 0.40 only up to z 1.12;
     - y 0.48 only at z 1.05;
     - the first port position (y 0.38, z 1.24) passes only marginally (1/96 starts).
     - **So outlets and the weighing platform sit at the front of the cabinet underside, with cups at about 1.10–1.15 m.**
   - **Rice/flour port:** ✓.
   - **Cups on a low backsplash rail (z 0.99, y 0.50):** ✗ (forearm vs base plate). Store cups under the cabinet instead.
   - **Pouring a cup over the wok:** 23/72 orientations pass. A wrist roll with a horizontal approach works.
   - **Drum over the wok held from the front:** all 4 roll angles pass with 15–24 good starts and 33 mm reserve. From the side it is marginal.
   - **Under-counter drawer (z 0.45–0.7):** ✗ from beside the docked cart (out of reach) and from in front of it (forearm hits the arm base plate). The arm reaches about 0.35–1.25 m beside the cart, but not low and close in front of itself. **A low drawer fridge would need a lift on the cart or a raised install.**
2. **Fridge door physics** (`doorbench.py`, MuJoCo noslip).
   - Setup: finger set P2 with one finger between the bar handle and the door (form closure), the arm compliant (weld solref 0.02), following the hinge arc.
   - Seal 20–140 N and door 6–14 kg: opens to 100° and closes every time. Hinge-radius error ±10 mm is fine; ±20 mm still works but lags 22 mm.
   - At a 100 N seal the finger contact peaks at 128 N. With an assumed 50 mm lever that is about 6.4 N·m, near the PGC's 7 N·m jaw limit; at 120–140 N (142–162 N contact) it would exceed it. The jaw moment was not computed in this bench.
   - Measured fridges range 27–116 N (+20 % in the morning), so high-seal doors need assisted opening.
   - Video: `renders/r14/door_drum.mp4`.
3. **Timeline for all 42 recipes** (`timeline14.py` → `results/r14/timeline.json`). Dose rates and arm handling times are assumptions, labelled in the script.
   - Station time per dish: median 2 min 16 s, p90 4 min 22 s, max 5 min 37 s.
   - Cups: median 4 per dish; kit cups: median 1.5.
   - Single-cup pours (pick, roll, return) are too slow for 25 recipes at 8 s per cycle and 17 at 4 s.
   - With the pour drum (≥ 1.5 s between compartments), none of the 42 is too tight; 17 recipes use 1–2 drums.
4. **Pour drum physics** (`pourbox.py`).
   - 4 × 30 granules (2.5 mm): all released in order, 100 % in the wok. Each compartment empties in about 0.15 s; gaps of 2.0 s (hold 1.5 s) or 1.3 s (hold 0.8 s).
   - 4 × 12 lumps (6 mm, chopped aromatics): in order, 90 % in the wok. The first compartment released only 7 of 12, so the aromatics slot must be wider (60°).
   - Liquids are not simulated (no fluid solver).
5. **Renders:** `renders/r14/overview.png` (robot at the seasoning port and at the wok with the drum, checked poses) and `renders/r14/cad_station.png`.
6. **Single-door fridge reach** (`fridge14_batch.py`, `fridge14_batch2.py`, `fridge14_batch3.py` → 176 `results/r14/reach_*_fr*.json`; continuity: `fridge14_arcdp.py` → `results/r14/fridge_arc_path.json`). Same 96-start IK and unchanged checker. The handle bar is removed from the checker while it is held.
   - **Handle from the docked cart (x −1.48):**
     - ✓ at door 0–55° (grasp z 1.00–1.20);
     - 60° misses by 0.5 mm (finger 4.5 mm from the door, 5 mm required);
     - 75–105° is 34–193 mm out of reach.
     - Cart x −1.58 is worse near the closed door (the arm folds onto itself).
   - **Cart in the aisle in front of the fridge:** many poses are collision-free, but they lie outside the dock and tether envelope (status `floor_cable`), so this option is not used.
   - **R13 knob baskets on a shelf inside the fridge:** ✗ for every approach angle (0/20/35°) at door 50–105°. The forearm hits the cabinet's right side panel, the freezer front or the arm base plate. **The robot takes nothing from the shelves.**
   - **Cold box in a door bin:**
     - with a 30 mm bridge: ✗ (the arm must dip past the cabinet's right front edge);
     - with a 110 mm bridge and the bin at 0.85 m: grasp, lift, slide and clear-of-door ✓ at door 30–55°;
     - with the bin at 0.92 m: the lift fails at 30–35°; with the bin at 1.00 m: the grasp fails.
   - **Counter set-down:** ✓ at (−1.70, 0.18) with the box along y (reserve 11.7 mm). Other counter spots hit the upper-cabinet door or the items on the counter.
   - **Continuity:** collision-free candidates at every 2.5° from 0 to 55°, best chain:
     - 0–35° is one continuous joint path (≤ 10.3° of joint per 2.5° of door);
     - 35°→37.5° needs an elbow flip (a re-grasp);
     - **so the door is opened to 35°, in one motion.** At ≤ 4.1° of joint per degree of door, a 15°/s swing keeps the joints ≤ 62°/s.
   - **Not checked:**
     - the held box's own collisions (it is not attached as a body). A 2-D check gives its hinge-side corner ≥ 6 mm in front of the cabinet front at 35°, inside the empty 0.12 m shelf setback.
     - transfer motions between the checked poses (not planned);
     - whether the door stays at 35° by itself.
   - Render: `renders/r14/fridge.png` (handle at 0° and 35° from the path; box pinch at 35°).

## Open / next
1. **Fridge:** the size, placement and handle are estimates.
   - Measure the real door's seal force and check that the door stays put at 35°. If it closes by itself, level the fridge or add a friction stop.
   - Door bins are the warmest part of a fridge. The cold box is for same-day staging, not long-term raw-meat storage.
2. **Cooking itself is the next round:**
   - stirring and tossing;
   - heat control and the off-heat steps (about 10 dishes);
   - pouring out the 润锅 oil;
   - edge pours;
   - gradual 勾芡 judged by vision;
   - hot-oil safety.
3. **Unproven assumptions:**
   - dosing accuracy by weight (Kamoer open loop is ±10 %; closed by the scale);
   - the 水淀粉 settling rate;
   - paste extrusion of chunky 豆瓣酱;
   - caking in the augers at Singapore humidity;
   - salt as brine adds about 8 g of water per 3 g of salt.
4. **Prices:** none are confirmed in CNY; nothing is bought.

# R15 (2026-10-12): cooking itself — heat, stir-frying, additions, plating

The user said "ok" to the R14 fridge design; R15 is the next round named there: the cooking itself.

Inputs:
- `robot_rail/research/wanggang_cooking.md` / `.json`: the 42 recipes split into 258 phases (vessel, action, heat, time, lid, liquid, wok load, hand motion, end cue, transfer out), each with his own words and the subtitle cue. All quotes were checked against the subtitles by script.
- `robot_rail/research/r15_cooking_market.md`: heat sources, auto-stir machines, robot stir-fry papers, wok thermal facts, hot-oil safety, wok and spatula sizes (about 137 sources).

## What the recipes demand
- **Vessels:** 38/42 use the wok (8 with deep oil, which R14 already moved to a fryer). No recipe heats two vessels at once.
- **Hand motion:** 34 stir (翻炒). No zh transcript says 颠锅; the only "toss" is in one English-only translation. 4 flip single pieces (fish, eggs), 6 separate strands (划散), 11 let food set before stirring, 18 pour along the rim, 4 skim.
- **Heat:** median one heat change per dish (max 6). 19 关火/离火 events, 13 of them mid-cooking (豆瓣 or aromatics off the heat, 勾芡 off the heat, adding fish slices). Where a level is stated, about 64 % of wok time is low or medium-low, 22 % medium, 10 % high. Oil temperatures 120–240 °C.
- **Time:** active wok time median 103 s, p90 273 s (16 dishes with every step timed). Braises up to 60 min, steaming up to 2.5 h.
- **Wok load:** median 355 g, max 1150 g (椒盐排骨). Liquids up to about 2 kg (鱼头豆腐汤).
- **Oil:** 16 dishes pour out the 润锅 oil, 9 pour off excess oil mid-recipe, 5 泼油.
- **End cues:** 157 cue mentions in 41 recipes need a camera (colour, bubbles, thickness, texture); 40 need a thermometer; smell (43) has no direct sensor.
- **One arm:** 21 steps in 15 recipes use two hands at once (hold the wok off the fire and stir, pour hot oil through a strainer, lift a whole fish).

## Design (proposal; sizes and placements are estimates)
Model: `kitchen15.py` (on top of kitchen14, cfg `r15`), shared spatula geometry `spatula15.py`.

1. **Heat: a countertop concave (wok-shaped) 3.5 kW induction cooker** (美的 MC-E35D2 / 九阳 N3501 class, ¥320–600 in China) at the hob leg, on a new 20 A point (3.5 kW draws 15.2 A, more than a 13 A plug).
   - Why not the user's gas hob: it puts only about 0.9–1.6 kW into the wok (5 kW LPG / 3.8 kW town gas at about 32 % transfer), against about 3.0 kW for the induction unit (85 %). Gas also needs push-and-hold ignition and only a licensed gas worker may modify it in Singapore.
   - Why not a home auto-cook machine (添可 食万, 九阳 J7, Thermomix …): they stop at 120–230 °C and cook with the lid shut, so no 锅气, no 润锅/rim pours/离火.
   - **Control:** no concave unit documents an app, IR or serial interface. A bolt-on servo turns the power knob (no mains modification). Fallback: the arm presses the panel.
   - **离火 = power 0.** The wok then only loses heat, which is the same as lifting a wok off a gas flame.
   - **Sensing:** a thermal camera and a colour camera under the hood front, looking into the wok (oil and seasoned-wok temperature; colour, bubbles, thickness for 勾芡). The robot holds the wok below 250 °C (oil smoke points 190–234 °C); the cooker's own dry-burn cut-off is near 280 °C.
2. **Wok:** 34 cm round-bottom carbon steel (about 1.5 kg) seated in the cooker bowl, with a **short handle ending in a keyed grip block 0.235 m from the wok axis** (form fit for the PGC fingers). The handle rests on a bracket so spatula strokes cannot spin the wok. A long handle put 10.9 N·m on the PGC (limit 7).
3. **Stirring: the arm holds a spatula** (锅铲, blade 100 × 85 mm, 0.45 m from the grip to the edge, keyed block; GSW-class spatulas are 42.5 cm). The stroke (`spatula15.py`, `stirbench.py METHOD=scrape`, about 2.6 s per stroke for the arm):
   - scrape from the near wall up the far wall with the blade under the food; the handle goes from 62° to 38° above horizontal and the blade meets the steel at 12–43°;
   - lift, and return through the air to the next line; lines cycle through yaw 0°/+30° and 0/±5–6 cm offsets (no −30° line: with the cart parked left of the wok its handle points at the arm base);
   - a variant that also rolls the spatula ±60° about its handle at the far end (`push2`) mixes about the same, but the arm cannot follow the roll (the wrist hits the gripper body in every branch tried), so it is dropped;
   - the cart stays parked at x 0.55 (left of the wok) for the whole stir-fry.
   - While the heat is on, the arm stays at least 0.20 m from the wok axis between the rim and the hood (my plume rule, from the plume estimate in the market report: about 90 °C on the axis 30 cm above an induction wok, near ambient 20 cm off it; the UR5e is rated to 50 °C).
4. **Additions while stirring: a servo pour-drum holder at the wok rim.** The arm drops a loaded R14 pour drum into it before the heat goes on; a servo rolls it on time; rim pours (锅边淋) come from the same slots.
   - **Its place is still open.** On the right rim the arm cannot load it from any cart position (it folds onto its base). Behind the wok (centre 0.83, 0.36, 1.11, jaws vertical) it can, with zero clearance reserve, and that spot is not yet checked against the stir strokes.
   - Alternative for the liquids (most of the burst additions): pipe them from the R14 pumps straight to a fixed nozzle at the rim.
5. **Plating and oil pour-out.** With the heat off, the arm lifts the wok by its grip block, the cart moves left (about 0.8 m in the sim), and the arm tips the wok **toward itself** to 90° over a plate on the counter just left of the hood (plate centre x 0.43).
   - The plate sits in a plating stand with an 8 cm curved guard on the side the food flies toward.
   - Oil is poured out the same way into a steel oil cup.
   - In the sim kitchen this spot overlaps the R11 slicer's place by about 8 cm. In the user's L-shaped kitchen it would be the corner counter beside the hob.
   - The spatula's parking place is open. A stand right of the cooker fails (the upright handle reaches into the hood); between strokes it can rest in the wok (not checked).
6. **Safety (no new physics):** no flame; the robot's temperature limit; an electric stove guard (Innohome type, cuts the 20 A circuit on rate of rise); an automatic powder canister (StoveTop FireStop) 69–89 cm above the cooker; a smoke detector; the wok lid parked within reach for smothering.

## Evidence
1. **Heat budget** (`heat15.py` → `results/r15/heat.json`; lumped wok + food model, values and their basis in the script):
   - power into the wok: induction 2975 W, LPG gas 1600 W, town gas 1216 W;
   - empty wok + 30 g oil from 30 to 180 °C (6成热): 43 s, 83 s, 114 s;
   - 355 g of food at 5 °C into a 200 °C wok: the induction wok does not drop below 180 °C for any assumed food contact conductance (150–600 W/m²K); town gas drops to 174 °C and needs 114 s to recover at the highest one;
   - heat off with food in: −6 °C in 5 s, −32 °C in 30 s (the same for 离火 on gas);
   - a 6 s stir pause at 200 °C: +17 °C at full power, +6 °C at half, −5 °C at zero. **Policy: drop to about half power whenever the spatula stops.**
2. **Stir-fry physics** (`stirbench.py`, MuJoCo 3.2.5, rigid food pieces, no heat; `results/r15/stir_*.json`; table: `r15stirsum.py`). The spatula is a free body on a compliant weld (like a force-limited arm) and scrapes the steel. Hot zone = the wok surface within 13 cm of the axis (a 3.5 kW concave coil is ≥ 26 cm across).
   - **320 g of 15 mm dice (two layers), 12 s**, either stroke:
     - pieces touch the hot zone about 61 % of the time on average;
     - the longest unbroken hot contact is 2.2 s (unstirred: 12 s);
     - spill 0–5 of 90;
     - **but 13–15 of 90 pieces stayed in the top layer and never touched the hot zone in 12 s** (unstirred: 26). Over 36 s it was 2 of 82, with 8 spilled.
   - **160 g (one layer):** 73 % hot share. Half of the pieces are off the hot zone at most 0.2 s at a time, 90 % at most 5 s. 1 of 45 stayed on top.
   - A 6 s arm-busy pause every 10 s raises the longest hot contact to 7.7 s (burn risk), hence the half-power rule.
   - Friction μ 0.15–0.5 changes little; at μ 0.5 the top layer mixes better (6 of 90 never hot).
   - **Spatula load:** contact force p95 6–8 N; moment at the grip p95 2.2–2.9 N·m (PGC limit 7 N·m). Single spikes of 8–25 N·m come when a rigid piece wedges under the blade, so the block must be keyed and the arm force-limited.
   - Earlier strokes were rejected: an upright blade 3 mm off the steel jammed thin food (hundreds of newtons) and spilled up to 27 %; a push-pull stroke could not be followed by the arm (see 3).
   - **Not credible with rigid pieces:** shreds, slices and leaves wedge under the blade or slide off (`f_push2_shreds/slices/leaf`). Real food is soft, oily and wilts.
3. **Stir reach and continuity** (cart parked at x 0.55, unchanged checker, plume rule):
   - **Every keyframe of one 5-stroke cycle** (80 poses, `r15reach.py stir`, 96-start IK): **80/80 ✓** with a 0.45 m spatula grip. With 0.40 m, 10 far-end poses brought the fingers 2–45 mm inside the plume radius.
   - **One continuous cycle** (`r15stirwalk2.py`):
     - the working part of each stroke follows the bench's spatula path exactly by IK continuation (10 ms steps);
     - the return through the air is a joint move checked at 40 points;
     - the no-roll stroke closes the whole 5-stroke cycle: reserve ≥ 2.0 mm, plume clearance ≥ 26 mm, returns ≤ 0.77 s;
     - peak joint speed is 184 °/s at the bench timing, so **about 2.6 s per stroke** at the UR5e's 180 °/s.
   - Chaining independent multi-start poses (`r15dp.py`), or following the air returns as Cartesian paths, does not work (joint jumps of 250–1600 °/s). The returns must be planned in joint space.
   - The first stroke design (upright blade, handle bent back, pull-back with the other face) failed at the far end and on every pull-back: the handle lay flat and the arm folded into the hood. That is why the handle now rises toward the robot.
4. **One-arm timeline** (`timeline15.py` → `results/r15/timeline.json`; handling times assumed as in R14): in the 35 stirred dishes the spatula stops for every addition the arm fetches.
   - The arm does every addition: the spatula is idle for a median 36 % of the stir window (p90 79 %, max 89 %).
   - With the drum holder (seasonings dispensed by the servo): median 13 % (p90 57 %); only main-ingredient additions remain (median 1 per dish, 10 s each).
5. **Plating physics** (`pourwok.py` → `results/r15/pour_*.json`; rigid 15 mm dice, 90 pieces of which 77 had settled in the wok). The bench tips sideways and the robot tips toward itself; the wok, lip, plate and guard geometry is the same, turned 90° about the vertical.
   - every run empties the wok completely;
   - on a plain 24 cm plate only 25–55 % of the settled pieces stay on it: rigid cubes roll on over the far rim;
   - a two-step tip (hold at 60°) or pieces that do not roll (a rolling-friction proxy for sauce-coated food) raise it to 79–84 %;
   - **with an 8 cm curved back guard on the plating stand: 81–91 % (rigid), 98 % with a half load, all of it with the non-rolling proxy.** Sauce and liquids are not simulated.
6. **Plating reach and load** (`r15reach.py pour`, wok geoms attached to the gripper, load from the checker's envelope; `r15tipwalk.py` for the continuous tip; `results/r15/reach_pour_*`, `tipwalk_*`):
   - lifting the wok 4 cm in place: ✓ (top grasp, cart x 0.61; end grasp, cart x 0.30);
   - **tip toward the robot over the plate, 15° → 90° as one continuous motion: ✓**
     - top grasp, cart x −0.22, lip 3 cm above the plate;
     - ≤ 2.0° of joint per degree of tip, so ≤ 90 °/s of tip;
     - reserve ≥ 2.5 mm;
   - sideways tips pass at every angle on their own but not as one motion: the forearm or a joint hits the wok or a cabinet door near 47–50°;
   - right of the cooker, under the hood: ✗ at any tip angle (the hood is only 23 cm above the rim, and the arm folds onto its base);
   - load with the heaviest dish (1.15 kg food): 2.95 kg held, 4.15 kg payload of 5; PGC moment 6.3 N·m level, 1.7 N·m at 90° (limit 7); joint torque ≤ 48 % of the rated envelope. DH recommends ≤ 3 kg for this gripper, so the heaviest dish is at the limit (the median dish is 2.2 kg).
   - The transfer between the lift and the tip (the cart moves about 0.8 m with the wok in hand) is not planned.
7. **Edge pours with a cup, arm-held** (`r15reach.py rim`, 12 rim azimuths): none pass, because the cup over the rim puts the wrist inside the plume radius, or the arm collides. Rim pours therefore come from the drum holder.
8. **Drum holder and spatula parking:**
   - the drum cannot be loaded into a right-rim holder from cart x 0.55, 0.75 or 1.2, or with the cart free: the arm folds onto its base or the cart beam;
   - behind the wok it can (9 candidates, zero reserve, heat off);
   - a spatula stand right of the cooker fails (the handle reaches into the hood).
9. **Video and render:**
   - `renders/r15/stir_plate.mp4`: the stroke in the wok, and plating into the guarded plate;
   - `renders/r15/cooking.png`: checked poses for stirring and lifting, the wok tipped to 90° (from the continuous tip), and the candidate drum spot.

## Open / next
1. **Real stir quality** with real food: thin, soft and leafy foods cannot be judged with rigid pieces, and the top layer of a 320 g load mixes slowly. Practical rule until tested: cook main ingredients in batches of about 200 g or less, or stir longer.
2. **The cooker's control path:** buy-time check that the chosen concave unit has a rotary knob the servo can turn (the touch-panel units need the arm to press buttons).
3. **Not checked:**
   - the transfers between checked poses (lift → plating spot with the cart moving, stir ↔ additions);
   - the drum holder's final place and the spatula's parking place;
   - boiling, blanching and steaming in the wok (strainer ladle, steamer basket);
   - the lid for the two braises; ladling off excess oil;
   - 勾芡 by camera;
   - the fire-suppression placement under the hood.
4. **One-arm limits that remain:** two-hand steps (holding the wok off the fire while stirring is replaced by power 0; pouring through a strainer and lifting a whole fish need other tools).
5. **Prices:** none confirmed; nothing bought.

# R16 (2026-10-12): the user's reference cook — home-style 四菜一汤 meals

The user said: "你参考这位，他做的挺家常的", with three of his videos (今日食谱 …). The analysis is in `robot_rail/research/homestyle_meals.md` / `.json`; it was built from frames every 2 s, his on-screen captions and a Whisper transcript.

## What changes compared with Wang Gang
- **The unit is a meal, not a dish:** 4 dishes, 1 soup and rice for a family. He plans it around the slow items: the long unattended item first, prep while it cooks, quick wok dishes last.
- **Steaming and soup dominate:**
  - 5 of 15 dishes are steamed, 3 are soups, 1 is blanched;
  - only 7 need the wok and spatula, each with ≤ about 2 min of stirring;
  - one toss, for show;
  - he cooks on a flat induction cooktop with flat-bottom woks.
- **New handling:**
  - lids (steamer, pot, wok, including 30 s high-heat 焖);
  - plates of food into and out of a steamer;
  - stew cups;
  - a spider strainer for blanching and lifting fried food;
  - a soup ladle;
  - hot oil poured over sauces and fish (4 of 15);
  - rinsing the wok between dishes.
- **Knife work** is, in his words, the slow part: fish split along the back, squid scored, hand julienne, peeled tomatoes and taro.

## One-arm meal timing (`meal16.py` → `results/r16/meal_*.json`, `renders/r16/meal_stew.png`)
How it works:
- Each dish is a chain of steps; arm time comes first, then the heat source works unattended.
- A list scheduler follows his cooking order, quick dishes go last, then a pass pushes every step as late as possible so dishes finish together.
- Cooking times are his. Arm handling times are assumptions in the script (load a plate 20 s, lid 8 s, plating from the wok 30 s, rinse the wok 75 s, stirring time × 1.3 for the one-arm pauses).
- Knife work and seasoning dosing are done beforehand and not counted.

| Meal | Heat sources | Cooking time | Arm busy | Longest wait of a finished dish |
|---|---|---|---|---|
| A 干锅土豆/桂花芋头/西兰花/蒜蓉丝瓜/蛤蜊排骨盅 | wok + 2nd zone (steamer) + rice cooker + fryer | 39 min | 15 min | 8 min |
| B 红烧肉/番茄炒蛋/白灼秋葵娃娃菜/清蒸鲈鱼/鲜笋排骨汤 | wok + 2nd zone, soup on it | 78 min | 27 min | 17 min |
| B, with an electric stew pot for the soup | wok + 2nd zone (steamer) + stew pot | 72 min | 27 min | 17 min |
| C 芋头蒸排骨/酸辣土豆丝/青椒炒鱿鱼/清炒荷兰豆/青瓜肉片汤 | wok + 2nd zone (steamer) + rice cooker | 39 min | 20 min | 15 min |

- One arm is enough: it is busy only 34–53 % of the time.
- The wok is the bottleneck. Every wok dish is done one after another with a rinse in between, so the first quick dish waits 8–17 min. A covered plate in a warm spot helps; a second wok zone would cut it.
- Knife work, which he calls the slow part, is not in these times.

## Proposed changes to the design (not yet checked in the sim)
1. **A second heat source next to the wok:** a flat induction zone the robot can command. 米家电磁炉2 has a writable 0–99 heat level over MIoT (r15_cooking_market.md). It carries a steamer (2–3 tiers) or the soup pot. Alternative: an electric multi-tier steamer and an electric stew pot on smart plugs.
2. **Steamer handling:**
   - plates of food (up to about 1 kg, about 100 °C) and stew cups with lids go in and out;
   - the arm needs a plate grasp: a plate carrier with a handle, as with the R13 side-handle baskets;
   - the arm needs a lid parking spot.
3. **Tools with keyed handles like the spatula:** a spider strainer, a soup ladle, a wok lid; plus a tool rack within reach.
4. **Wok rinse between dishes:** water (corrected in the R16 sim checks: the R14 station has no water channel; the user decided against a pipe, so the water comes from a jug and the kettle the user fills), scrape, then the R15 lift-and-tip into a waste basin at the plating spot.
5. **Hot-oil sauces:** heat oil in the wok and pour it over a bowl or plate at the plating spot (the same continuous tip as plating).
6. **Knife work:** buy fish and squid cleaned and cut; julienne with the slicer's disc; no tomato peeling. The rest goes to the R11 prep machines or to the user's weekly prep.

## Next
- Place the second zone / steamer and the tool rack in the sim kitchen.
- Check the reach and continuity for plates into and out of the steamer, lids, the spider strainer and the ladle (with the plume rule), and the wok rinse.
- Re-run the meal timing with checked handling times.

# R16 sim checks (2026-10-12): second heat zone, lid, dish carrier, spider, ladle

The user said "可以，继续" to the proposed next step. Model: `kitchen16.py` (hooked from `kitchen14.add` via `cfg['r16']`). Checks: `r16walk.py` (one station), `r16chain.py` (one whole action), `r16seq.py` (action times). Results: `results/r16/walk_*.json`, `chain_*.json`, `arm_checked.json`. Render: `renders/r16/handling.png`. Unchanged checker: 10 mm robot–environment, 5 mm gripper/held–environment, rated load.

## Layout (all sizes estimated)
- **Second heat zone:**
  - a flat 米家电磁炉2-class induction (MIoT heat level 0–99, writable) on the right half of the hob, ~0.29 × 0.36 × 0.06 m;
  - on it a 30 cm pot, 12 cm deep, centred under the hood front (y 0.21);
  - a 4 cm steaming rack inside the pot. Steaming happens on that rack: **no stacked steamer tier** (see below).
- **Lid:**
  - glass dome with a keyed tab on the front rim, taken level from the front;
  - parked upright in a rack at the counter end.
- **Dish carrier:**
  - the dish sits on a wire ring, with a bail over it to a keyed block above the dish's centre of mass;
  - taken from the front at 45° down.
- **Tools:**
  - spider (漏勺) and ladle (汤勺) with keyed handle blocks, both with a 45° handle;
  - they lie with the R15 spatula on a tool rest at the counter end, in their working orientation.
- **Removed from the sim:** the counter end's dish rack (the user's is on the sink leg), the right gas burners, and the R15 spatula stand.

## What failed, and the design change it caused
| Tried | Result | Change |
|---|---|---|
| Lid knob / tab and dish carrier taken from above under the hood | Gripper (~0.2 m) plus wrist do not fit under the hood; starts touching the pot also counted as hits | Lid taken level from the front, carrier at 45°; grasp and place starts 8 mm off the support |
| Dish carrier into a 9 cm steamer tier on the pot (pot y 0.17 / 0.21 / 0.25; approach 45° / 60°) | 0 starts: with the dish lifted clear of the tier, the gripper is inside the hood (hood 0.40 m above the cooktop) | Steaming rack inside the pot instead of a tier |
| 16 cm deep pot with the rack | Carrier: the gripper body passes over the high rim, then cannot rise without the hood | 12 cm pot + 4 cm rack |
| Tools standing handle-up in a caddy | 0 of 192 starts: the wrist above a 1.25 m grip meets the upper cabinets | Tools lie on a rest in their working orientation |
| Straight joint-space moves between checked stations | Collide in every action (lid / pot wall, spider / upper cabinet, ladle / pour drum) | Whole actions as one continuous path (`r16chain.py`) |
| 60° ladle handle | In the carry lane the arm folds onto its own mast | 45° handle |
| Wok rinse water into a 15 cm bucket at the plating spot | Tip stops at 39–42°: wok against the seasoning outlet | An 8 cm basin passes |

## Results
Each whole action is followed as a continuous path: the object moves ≤ 1 cm / 2° per step and the arm follows by IK continuation, with the checker at every step. Each station starts from its own checked walk, and the halves are joined in the open lane in front of the hood.

| Action | Whole path | Time | Min reserve | PGC moment | Joint load |
|---|---|---|---|---|---|
| Lid: off the pot → slide out of the hood → roll 90° → upright in the rack (lid on = reverse) | passes | 19 s | 1.0 mm (in the rack) | 1.6 N·m | ≤ 0.39 |
| Dish carrier: plate spot → lane → over the pot rim → onto the rack (out = reverse) | passes | 18 s | 2.3 mm | 0 | ≤ 0.39 |
| Ladle: fetch, scoop in the pot, pour into a soup bowl at the plate spot (×2), return | passes | 64 s; fetch 14 s, **34 s per scoop**, return 14 s | 3.0 mm | 0.8 N·m | ≤ 0.37 |
| Spider: scoop in the pot, drain 5 s, tip 110° onto a plate at the plate spot | passes | (in the 63 s below) | 2.2 mm | 1.25 N·m | ≤ 0.34 |
| Spider: rest → pot and back | **open** | — | — | — | — |
| Wok rinse water into an 8 cm basin at the plating spot (R15 tip 15→90°) | passes | — | 15.4 mm | — | — |

- **The spider's rest is open.** Every piece passes, but the arm state that picks the spider off its rest and the one that works at the pot are 155–175° apart in a joint. Straight swings collide at six tried places, and RRT-Connect (`planner.py`, 120 s) did not find a path. The counter end is crowded: three long-handled tools plus the lid rack, under an upper cabinet.
- **Cart moves with the arm out.** Carries move the cart while the arm holds the object over the counter, and every step is checked. They break the R10 dock carry envelope (≤ 0.40 m along x, ≤ 0.10 m over the counter edge) at 31/56 (lid), 88/88 (carrier) and 100/270 (ladle) cart-moving steps. Keeping that rule would need a folded carry pose for a 31 cm lid or a dish (not found); relaxing it is a design decision.
- **Water.** The R14 station has **no water channel**: the R16 note above ("water from the R14 station") was wrong. The wok rinse, soups and blanching need water. **User decision: no pipe or valve**: water comes from containers the user fills before cooking (the kettle on the hob leg for hot water, a jug of about 1.5 L for the rinses). Not simulated yet.

## Meal timing with checked action times (`meal16.py ARM=checked`, `results/r16/meal_stew_checked.json`, `renders/r16/meal_stew_checked.png`)

**Action times used** (`arm_checked.json`):
- lid 19 s;
- plate in / out 18 s;
- soup 300 s (8 scoops of 150 ml);
- spider about 70 s (estimate: the rest is open);
- wok plating about 52 s and wok rinse about 68 s. These are estimates from R15 pieces, not chained: the R15 wok pick-up (grasp sense +1) and tip walk (−1) were never joined, and the spatula goes to its rest at the counter end and back every time.

With one rack, the pot holds one carrier: in meal A the stew cups move to an electric water-bath stew pot.

| Meal | Before (assumed times) | Checked times | Arm busy | Longest wait of a finished dish |
|---|---|---|---|---|
| A | 39.4 min | 39.6 min | 17.5 min | 11 min |
| B (stew pot for the soup) | 71.8 min | **80.1 min** | 35.4 min | 26 min |
| C | 38.5 min | 38.6 min | 26.4 min | 17 min |

- **Soup.** Ladling is the largest single item: 5 min, because the soup bowl is at the plate spot 0.87 m from the pot. Faster options: pour from the pot by tipping it (needs a pot grasp check, about 3 kg) or serve in the pot.
- **Waits.** The waits stay long because the wok dishes go one after another. The single wok and the spatula round trips to the counter end are the bottleneck.

## Open
- The tool rest / spider location: the counter end is too crowded.
- The cart-moves-with-arm-out rule.
- Water from the kettle and a jug: where they stand, the handle grasps and the pours into the wok and the pot.
- Chaining the R15 wok pick-up, carry and tip.
- A spatula rest near the wok.
- The lid of the wok (焖 30 s) and of the electric stew pot.
- The stew-cup handling.
- A pot-pour soup serve.
- Steam on the fingers when the lid comes off: lid tilted away and the heat off first; not simulated.
- All of it on the user's measured kitchen; the sim kitchen is generic.

## User decisions on the R16 open items (2026-10-12)
- **Cart moves with the arm out are allowed** if every step is collision checked. The R10 dock carry envelope no longer applies to these carries.
- **No water pipe or valve.** Water comes from containers the user fills before cooking:
  - the kettle on the hob leg, for hot water;
  - a jug of about 1.5 L for the rinses.
- Estimate: 6–10 water uses and about 4–8 L per meal; each pour takes about 20–30 s of arm time.
- **Wok rinse at the sink (user decision).** The arm opens the user's single-lever faucet first and leaves it running, plates, rinses the wok at the sink, sets it back on the cooker, then closes the faucet; wasted water is acceptable. Wok water (≤ about 1 L) can be taken at the running tap. The kettle remains for the soup pot.

# R17 sim checks (2026-10-12): faucet, wok rinse at the sink, counter-end tool rest

**Why this round.** The user decided three things after R16:
- the cart may move while the arm holds things out over the counter, as long as every step is checked;
- no water pipe over the hob;
- the wok is rinsed at the sink, with the faucet opened first ("你可以先开水龙头呀，浪费点水无所谓").

**Files**
- Model: `kitchen17.py` (cfg `r17`, hooked from `kitchen14.add` after kitchen16).
- Checks: `r17chain.py`.
  - Each action is one continuous checked path.
  - Anchors are solved in place, with a DP over the anchor candidates so that every join is clear.
  - Joins carry the food within 5 cm / 15°.
  - The cart is an IK variable on the carry frames.
- R16 re-checks in the R17 layout: `r17r16recheck.py`.
- Times: `r17seq.py` -> `results/r17/arm17.json`; `meal16.py ARM=r17`.
- Videos: `renders/r17/wok_sink.mp4`, `spider.mp4`, `lid.mp4`, `lever.mp4`.
- Results: `results/r17/chain_*_final.json`.

Unchanged checker: 10 mm robot–environment, 5 mm gripper/held–environment.

## Layout (all sizes estimated)
- **Faucet.** The user's single-lever faucet (from the photo, sizes estimated): a square column behind the basin with a 0.185 m spout and a side lever. The lever end gets a clip-on keyed block on a 25 mm bracket; the PGC grips it from the right and lifts it 30°. The R07 wall spout is removed.
- **Sink.** The prep colander is out of the sink while cooking.
- **Wok.**
  - The R15 handle bracket is removed; a keyed slot in the cooker's bowl rim takes over its anti-rotation job (not modeled).
  - Grasp: the top grasp of the R15 block, leaned 25° toward the robot, grasp sense −1.
- **Pour drum.** Swung away from the rim except while stirring (not modeled).
- **Counter end.**
  - The spider lies at (1.52, 0.36), where the R16 spatula was, 6 cm further back, handle toward the robot.
  - The lid rack is unchanged.
  - **The spatula and the ladle are no longer on this rest** (open, see below).

## Results (final layout, every step checked)
| Action | Time | Min reserve | PGC moment | Joint load |
|---|---|---|---|---|
| Faucet open: approach, lever +30°, release (close = reverse) | 3.5 s | 6.0 mm | — | — |
| Wok: off the cooker → tipped 90° over the plate → sink, 5 s under the running tap → emptied (tipped 90°) → back on the cooker | 48.9 s | 3.3 mm | 6.47 N·m (limit 7; with 1.15 kg food) | ≤ 0.63 |
| Spider: rest → pot (scoop, drain 5 s) → plate (tip 110°) → rest | 52.6 s | 2.1 mm | 1.25 N·m | ≤ 0.31 |
| Lid: off the pot → upright in the rack | 20.2 s | 1.0 mm | 1.58 N·m | ≤ 0.41 |
| Dish carrier into the pot (R16 chain re-checked) | 17.7 s | 2.3 mm | 0 | — |

## What failed, and the change it caused
| Tried | Result | Change |
|---|---|---|
| Lever gripped from the front | Fingers (54 mm wide), then the PGC housing (lever up) within 5 mm of the spout | Gripped from the right; block on a 25 mm bracket |
| Jaws opened 40 mm at a front spider rest | A finger met the arm's own base cover | Jaws open 25 mm (10 mm each side of a 30 mm block) |
| Wok, vertical top grasp | Lowered onto the cooker, the forearm met the upper-cabinet door | Grasp leaned 25° toward the robot |
| Wok with the R15 handle bracket | It can leave the cooker only lifted 9 cm (wrist into the cabinet door) or slid 15 cm toward the robot (arm folds onto its base); open fingers within 5 mm of it | Bracket removed, keyed slot |
| End-on wok grasp | The elbow went into the left upper-cabinet door | Not used |
| Grasp sense +1 (lifts) vs −1 (tips), the R15 open item | +1 cannot tip over the plate; −1 had no start at the cooker below a 20° lean | −1 with a 25° lean |
| Wok tipped under the tap | Back rim met the spout | Emptied 7 cm forward and 6 cm higher (lower, the wrist met the sink's front rim) |
| Cart fixed during each carry | The arm folds onto its base or cannot reach | Cart as an IK variable (cheaper than the joints) |
| Sink posture with the cart right of the wok | Could not be joined to the plate posture (cart 0.8 m apart) | Cart 0.66 m left of the wok at the sink too, as at the cooker and the plate |
| Pour-drum holder raised 6 cm | The arm met it when the lid comes off | Swing-away drum |
| Spider at the front (1.60, 0.14) | Its grip block, 14 cm past the counter edge, met the wrist when the lid went into the rack | Spider at (1.52, 0.36), spatula and ladle off the counter end |

## Meal timing (`meal16.py ARM=r17`, `results/r16/meal_stew_r17.json`)
**Arm-time model**
- The rinse is folded into the plating trip: spatula to its rest → faucet → wok chain → faucet → spatula back. That is 101.8 s, against 52 + 68 s in R16.
- After blanching or a soup in the wok, the wok is emptied at the sink ('dump').
- A litre of water for the wok is taken at the running tap ('fill').
- Dump and fill are 82.4 s each (estimate: the same trip without the plate tip and without the spatula).
- Small amounts of water (≤ 300 ml) still come in a cup.
- The free moves between the checked actions are estimates (cart 0.25 m/s, arm 90°/s), not checked. The spatula handling still uses the R16 estimate.

| Meal | R16 checked | R17 | Arm busy |
|---|---|---|---|
| A | 39.6 min | 39.5 min | 16.6 min |
| B | 80.1 min | 79.6 min | 35.7 min |
| C | 38.6 min | 38.6 min | 29.2 min |

Every wok dish now ends with a sink trip, so the plating step is longer; this is offset by the rinses no longer needed before the next dish. Meal C's arm time rises because its blanching and soup water is now fetched from the tap (2 fills, 2 dumps).

## Open
- **Spatula.** Its rest is no longer at the counter end; it needs a place near the wok (not checked).
- **Soup serving: decided, the user serves** (see below).
- **Scrubbing with one arm** at the sink is not simulated: a fixed brush in the sink, or a spatula scrape on the cooker first.
- **Water, food and steam** are not simulated.
- **Kettle.** Not needed in this plan: the pot water is put in at setup and the wok water comes from the tap.
- **The user's faucet.** Its geometry is estimated. The clip-on block needs their real faucet.
- **The user's kitchen.** It is L-shaped and the sink is on the other leg. Whether the robot can reach the sink from the hob needs their measurements.

## Serving is the user's (2026-10-12)
The user answered the soup question with "做完上菜人类来就行": the robot cooks and plates, and the user serves.
- **No ladle.** Soups stay in their pot and the user serves from it.
  - Meal B: the soup stays in the electric stew pot; the 5 min of ladling is gone.
  - Meal A: the stew cups stay in the stew pot.
- **Meal C's quick soup (青瓜肉片汤) moves from the wok to the electric stew pot,** which is otherwise idle in that meal. The water goes in at setup, and the robot adds ginger, cucumber and pork.
  - Tried first: the robot pours the wok's soup into a soup bowl at the plating spot (`r17chain.py ACT=wok PH=.08 / .06`, `PX=.33 / .35`).
  - The pour itself and the sink trip pass. But a bowl taller than a plate, 6 cm or more, is hit by the arm's forearm when it picks the wok up off the cooker, also when moved 8–10 cm left.
- **Meals (`meal16.py ARM=r17`):**

| Meal | Total | Arm busy |
|---|---|---|
| A | 39.5 min | 15.8 min |
| B | 75.0 min | 30.7 min |
| C | 38.6 min | 19.6 min |

- **Finished plates: for now the user takes each dish off the plating spot** (user decision). Only one plating spot has a checked wok tip; a second one on the free counter left of it is the next check.
- *(earlier note)* **Finished plates at the single plating spot.** Each finished plate must leave the spot before the next dish is plated. Either the user takes each dish when it is done, or the robot moves plates on R16 carriers to a holding place (space and arm time not checked).

# R18 checks (2026-10-12): a second plating spot, a home for the spatula
Tools: `r17chain.py` (new: `ACT=spatula` from its rest to the first R15 stir stroke start; options `PX`, `PLATE2`, `SPATREST`, `SPATELEV`, `PH`) and `r18spatscan.py` (screening). Results are in `results/r17/chain_*r18*.json` and `results/r18/spatscan.json`.

**Second plating spot: passes.** With a finished dish still on the R15 plating spot (x 0.43), the wok is plated at a new spot 26 cm left (x 0.17), then rinsed at the sink and set back. The run is 48.9 s, min reserve 3.3 mm, PGC 6.47 N·m (`chain_wok_s-1_r18plate2b.json`). Two dishes can wait for the user.

**Spatula rest: not found in this first pass (found later, see "The spatula lies on the counter" below).** In the final R17 layout the spatula has no place: the counter end is taken by the lid rack and the spider.

| Tried | Result |
|---|---|
| Next to the sink (−0.85, 0.30), handle 50° up toward the robot | The rest-to-stroke-start path passes with grasp sense +1 (24 s). But the handle is hit by the upper arm when the wok goes to the sink and when the faucet is opened. |
| Screening: 90 rests (x, y, handle elevation), each replaying the checked wok / faucet / lid / spider paths | 34 do not block them. Of those, only 7 have IK starts at the rest. |
| Behind the plating spots (0.10–0.20, 0.50), 50° | Lifting it off the rest, the PGC housing meets the upper-cabinet door. The handle is also in the wok's way when it is tipped over the second plate. |
| Counter end (1.60, 0.30), nearly flat | Lifted, the blade meets the spider bowl. |
| Far left (prep counter) | No IK start at most spots. (Wrong as a summary: (−1.15, 0.30) lying flat had starts but was not run; see below.) |

- **The grasp sense matters too.** R15 checked the stir strokes with sense −1, but every rest-to-stroke path with −1 failed at the wok: the arm meets the held spatula's handle. With +1 the stroke cycle itself is unchecked.
- **Next options:**
  - a holder that carries the spatula on the robot's cart, so the arm never goes to a rest;
  - a hook rail on the backsplash at a height the wrist can reach under the cabinets;
  - re-checking the R15 stroke cycle with grasp sense +1.

## The spatula lies on the counter (2026-10-12, R18b)
The user asked whether the spatula can simply lie on the counter ("锅铲直接放桌子上可以吗"). It can: lying flat left of the sink, at blade centre (−1.15, 0.30), handle 8° up toward the robot, on a 2 cm pad, **flipped over** compared with the R16 rest, i.e. turned 180° about its handle (`SPATROLL=180`).

Which face is up matters. The gripper takes the handle the same way in both cases, but it holds the spatula one way round or the other.
- **Laid as in R16:** the spatula ends up in the hand in grasp sense +1.
  - The path to the wok passes (27.1 s, `chain_spatula_s+1_r18flat.json`).
  - But with +1, R15's reach set has no stroke start clear of the steam plume at strokes 0, 2 and 4. That is why R15 used −1.
- **Turned on the counter instead** (handle 45° or 90° to the left or right, `SPATYAW`):
  - Turned right, it is hit by the arm during the wok plate.
  - Turned left 90°, the pick fails.
  - Turned left 45°, both ends work, but the two sides never meet. With the lane cart free they arrive 1.1 m apart, and the shuffle is blocked. With the lane cart fixed (`SPATLANEC`), the rest side's handle hits the arm or the base, also with the lane orientation half or fully turned (`SPATLANE`).
- **Flipped over:** the gripper pose is the same as unflipped, and the spatula ends up in sense −1, R15's sense.

Results:

| Check | Result |
|---|---|
| Rest to stir stroke start (`r17chain.py ACT=spatula SIGN=-1 SPATREST=-1.15,.30 SPATELEV=8 SPATROLL=180`) | **Passes**: 26.9 s, min reserve 6.0 mm, PGC 1.31 N·m, grasp approach 27 mm reserve (`chain_spatula_s-1_r18roll-1.15_.30.json`). Back to the rest is the same path reversed. |
| Does it block the checked actions? (`r18spatreplay.py -1.15 .30 0 8 180`, every step) | **No hits** on the wok plate + sink rinse, the second plating spot, the faucet lever, the lid or the spider. |
| Hand-off into the R15 stir cycle | The chain ends in the same IK branch as R15's stir start: cart 7.8 cm, joints ≤ 11°, 0.5 s, no hits, min reserve 2.0 mm. |
| R15 stir cycle in the current kitchen (`r15stirwalk2.py ... SCENE=r17`) | **Passes as in R15**: 5 strokes + close, period 2.63 s, min reserve 2.0 mm, plume 25.8 mm (`results/r15/stirwalk2_h_scrape_dice_r17.json`). |
| Plating sequence (`r17seq.py SPAT=... OUT=results/r18/arm18.json`) | wok_plate 134.3 s (was 101.8 s with the R16 spatula estimate of 6.7 s each way). dump / fill 73.5 s: the faucet is now close to the spatula rest. Free moves are still estimates. |
| Meals (`meal16.py SET=stew ARM=r18`) | A 39.5 / **B 75.6** / C 38.6 min. B was 75.0 with the R17 numbers. |

The other spots tried in R18b (`results/r18/yawscan/`, `chain_spatula_s-1_r18*`):
- (−1.15, 0.22): passes every join, but the grasp approach fails.
- (−1.15, 0.18): the blade hits the raw potato when lifted.
- Turned spots: the green-leaf prep bowl (−1.23..−1.03, 0.36..0.56) is hit when lifting.

Code changes:
- `kitchen16.SPAT_YAW` and `SPAT_ROLL`, both default 0, so earlier results are unchanged.
- r17chain options `SPATYAW`, `SPATROLL`, `SPATLANE`, `SPATLANEC`.
- `r15stirwalk2.py SCENE=r17`.
- `r17seq.py SPAT` and `OUT`.
- `meal16.py ARM=r18`.

## R19: less money, smoother motion, a library of pre-checked movements (2026-10-13)
The user asked for several subagents to explore cheaper robot designs and a better way to instruct motion: "less money, more smooth movements … lots of predefined movements then movement sets, therefore no need check after each tiny movement." Five studies ran in parallel. Each wrote only new files.

| Topic | Report | Code / results |
|---|---|---|
| Arm and hand cost | `research/r19_arm_hand_cost.md` | `r19/arm_candidates.json` |
| System cost, task offload | `research/r19_system_cost.md` | — |
| Movement library design | `R19_MOTION_LIBRARY.md` | `r19prim_*.py`, `results/r19/prim/` |
| Smooth retiming | `R19_SMOOTH.md` | `r19smooth*.py`, `results/r19/smooth/` |
| Hub roadmap (free moves) | `R19_HUB.md` | `r19hub*.py`, `results/r19/hub/` |

**Money (all prices unconfirmed, nothing bought):**
- **The arm dominates.**
  - UR5e: about ¥150–180k.
  - Fairino FR5: ¥23.8k guide price (2023). It has the same 180 °/s joints and nearly the same links. It needs the ±360° wrist-3 option, because the stock ±175° range is exceeded by 5 of the 7 saved chains. IP54.
  - Elite CS66: the closest UR5e twin, IP65. No China price found.
  - Dobot CR5A: replays a stored trajectory file on the controller.
  - Any arm swap means re-checking the library.
- **Hand:** no cheaper gripper meets the force, moment and IP needs. Keep the PGC-140-50.
- **Everything else:** the appliances together are only about ¥5–13k. The rest of the money is in:
  - the cart and its installation (an allowance);
  - safety, PC and vision;
  - labour;
  - the custom seasoning station (¥7–18k in parts).

**Arm time.** The wok is 55 % of the modelled arm time: 38.0 of 69.2 min over meals A/B/C.
- Plating trips: 15.7 min, of which the spatula round trip is 6.4 min.
- Stirring: 13.2 min.
- Fill and dump: 6.1 min.

**Movement library** (measured in the sim unless marked as a proposal):
- Seven recurring sub-motion types hold 74 % of the motion time of the checked actions. Only 9 % is one-off: the lever, the lid roll and the stir strokes.
- The R18 second plating spot re-planned 283 states that were identical to the first spot.
- Swept-volume screening (84 stored segments, as voxels): after a fixture moves, a 67 ms screen picks the segments to replay. For the R18b spatula rest that was 4 segments, replayed in 2.9 s. Re-planning took 928 s.
- **Proposal for meals A/B/C:**
  - 34 movement sets: 12 checked, 2 composed from checked pieces, 1 partly checked, 19 still to check;
  - about 28 hubs;
  - 16 primitive types.

**Hub roadmap (checked):**
- **Layout:** one tucked posture at 4 cart stations (−1.48, −0.68, 0.172, 1.093), and 7 empty-hand action endpoints.
- **One union scene for every free move:** the lever closed and open, the lid on the pot and in the rack, dishes on both plating spots.
- **All 22 edges pass the full checker** (min reserve 2.0 mm). Three needed a via pose:
  - LEV_O: retreat 15 cm toward the aisle;
  - SPAT→LEV_C: tuck at the mid cart;
  - LEV_O→WOK: both.
- **All 42 routes between the 7 endpoints are checked.**
- **Times against the estimates:**
  - the checked↔checked moves in the meals are close to the estimate: WOK↔LEV_O 6.4 vs 6.0 s, SPAT→LEV_C 6.5 vs 5.8 s;
  - moves inside the pot cluster are slower (9.3–9.8 vs 3.4–4.4 s), but they don't occur between checked actions in the meals.
- These times use r17chain's speed caps. Free-move hand speed reaches 0.9 m/s, because nothing caps the TCP speed.

**Smooth retiming (checked):**
- All 5 checked actions were fitted with joint-space B-splines, and every state was re-checked at ≤ 4 mm: 0 hits, min reserve equal to the baseline.
- **With the same caps** plus sourced URScript accelerations and a jerk limit, they are slower: wok 48.9 → 67.1 s.
- **With UR5e joint speeds, 0.25 m/s TCP and cart 0.5 m/s²** they match or beat R17: wok 47.3 s, spatula 19.9 s, lid 19.9 s, spider 45.4 s.
- **Stops:** 470 → 7 for the wok.
- **The cart is the binding limit** at its 0.15 m/s². At 0.5 m/s² the sim's tip model keeps a 42.7 mm margin with the held wok. That tip model is the quasi-static `mobile.py` check, so the 0.5 m/s² timings are unverified until GitHub issue #14 is closed.

**Corrections to earlier claims (found in R19):**
- **The sim UR5e collision capsules (MuJoCo Menagerie) do not enclose the real arm.** Mesh vertices stick out by up to 26.5 mm on the upper arm, 14.1 mm on the shoulder and 11.5 mm on the forearm (`r19ur5e_enclose.py`). Every UR5e path is open until it is re-checked with enclosing geometry (GitHub issue #12, running).
- **Stored paths contain exact ±2π joint jumps** (wok 2 rows, spider 3, lid 1, spatula 1).
  - Unwrapped, they stay within ±2π. The poses are the same, so the checks hold.
  - A real controller would spin the joint 360°, so any exporter must unwrap.
- **R17 did not meet the ≤ 4 mm rule.** It stepped 10 mm TCP / 2°, and computed the full clearance bound only every 5th step.
  - R19 re-checked all 5 stored paths at ≤ 4 mm, and all pass.
  - Some true minimum reserves are lower than reported: the wok is 2.02 mm, not 3.3. The lid stays at 1.0 mm (`results/r19/smooth/summary.json`).
  - The library study measured 0.3 mm for the lid's carry down to the rack, probably with the stock held-part model; this is unresolved.
  - Either way, the lid and the rack need mechanical location (a keyed tab and a lead-in).
- **R17/R18 action times assume unlimited acceleration** (a constant speed per step). Smooth execution at the same caps is 20–50 % slower. The faster sourced caps recover it (above).
- **The R15 stir period of 2.63 s is not executable as checked.** Each working part ends at 0.54–0.88 m/s, while the return starts from rest.
  - Option 1: stop at each hand-off, about 3.6 s per stroke.
  - Option 2: velocity-matched returns, which need a re-check including the plume rule.
  - The stir states were never stored, so `r15reach.py` and a state-saving `r15stirwalk2.py` must be re-run first.
- **Model bug, conservative:** `scene.build` converts tool boxes to meshes (the R11 rule) before `kitchen14.add` adds the R15+ held parts.
  - Those parts stay box primitives, which gives false hits (34 on the spatula chain).
  - It can only reject, never pass. R18's spatula-rest rejections may include false ones.
  - The fix, in `scene.py`, is not made yet.

**Recommended architecture (proposal):**
- **Layers:** recipe step → task → movement set → primitives → controller trajectory.
- **Composition:** every set starts and ends at an exact hub state, so any sequence is checked by construction.
- **Timing:** a set's geometry is checked once. Timing is generated at composition (TOPP plus a jerk limit) and needs only formula checks: joint, cart, jaw and food limits.
- **Layout changes:** re-check only the sets whose swept volume the change touches.
- **Runtime:** hub-state match, pre/post-conditions and monitors (joint torque, gripper, cameras, person sensing). No geometry checks.
- **Stored format:**
  - unwrapped hub states;
  - cubic B-spline pieces between mandatory stops, with the contact windows flagged;
  - a check certificate.
- **Playback:** a dense joint stream (UR RTDE `servoj` at 500 Hz) or an on-controller trajectory file (Fairino, Dobot).
