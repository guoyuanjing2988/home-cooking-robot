# R19 #42: a buildable gripper mount for the PGC-140 (Windows, 2026-10-14)

Checking standard: the pot-zone layer (`RACK=keyed SPX=1.56 SPY=.20`, `PY=.15`). Gates: 10 mm robot↔environment, 5 mm gripper/held↔environment, 0 mm self, states ≤ 4 mm apart. The checker is unchanged, and nothing was loosened.
Labels: **[M]** measured (in the sim, or on DH's CAD), **[S]** sourced (file or URL), **[E]** estimate or design choice. No git, no GitHub writes, no supplier contact.

## 0. Answer first

**Recommendation: m2, the wedge adapter (candidate C2).** The gripper keeps its 26.6° tilt. It sits on the inclined top face of a one-piece 6061 wedge bolted to the ISO 50 flange. DH's standard flange stays on the gripper.

**Why m2:**
1. **It can be built, and it clears the wrist** [M].
   - It is one compact block on the flange, with nothing beside the wrist.
   - The wedge body is **8.76 mm** from wrist 3 on the UR5e and **9.0 mm** on the FR5, against the 5 mm gate. The housing is 22.7 / 23.0 mm away.
   - Wrist 2 is ≥ 10 mm away over the whole J6 turn. There is no contact with wrist 1 anywhere in J5 × J6.
   - Only the 8 mm mating boss is closer (0.76 / 1.0 mm). Its bottom face is the bolted mating face, and the hulls include the flange.
2. **The TCP moves only along the gripper's own axis: 94.1 mm, with 0° rotation** [M].
   - The task-space keyframes are unchanged, and for most sets the certified object path carries over exactly.
   - **Every pilot set is certified on both arms:** wok, lid, spatula (the stir entry) and carrot. Each passed the ≤ 4 mm re-check with the bracket in the model: 0 hits.
   - I extended the pilots on m2 to the other adopted sets:
     - **15 of the UR5e's 19 sets** are certified: all six chains, the #4 prep sets, ctray, tubfill, soak, stgwok, fold and unfold;
     - **15 of the FR5's 17 sets** are certified (the FR5 tomato is still being re-planned in another agent's round).
3. **Payload stays inside both arms' ratings** [M + S].
   - Wok: 4.48 kg at 223 mm CoG offset. FR5 margin 0.52 kg; CoG reserve 77 mm to the 300 mm limit.
   - Full soak tub: 4.31 kg at 284 mm. This is the tightest number, 16 mm under the FR5's 300 mm.
   - The PGC jaw moment is unchanged: wok 6.23 N·m (7 N·m limit), because the grasp is the same.
4. **Mass 0.27 kg** [M from the geometry], plus DH's standard flange, 0.06 kg [E].

**Why not the others:**
- **m3, inline (C3).** Gripper axis on J6, on an 8 mm spacer. It has the smallest position change (63.9 mm) and the lightest part (0.06 kg). **But the TCP also turns 26.6°, and then the wok's 90° tip over the plate passes a wrist singularity on both arms.**
  - Every candidate jumps more than 10° per step. This also holds with the wok grasp leaned 0° or 40°.
  - The exact re-target hits the base plate (UR5e) and the sink rim (FR5).
  - The wok is the hardest and most used chain, so m3 would need new wok keyframes.
- **m1, the same pose moved 77.5 mm out along the flange axis on an L bracket (C1).**
  - It needs the heaviest bracket (0.33 kg), which sits over wrist 3.
  - On the FR5, its spatula pick is blocked: every candidate fails on the known MuJoCo box-box false hit, 4.9 mm reported against an exact 9.8 mm. Its lid and carrot needed second attempts.
  - The wok passes only as a re-plan. The exact re-target is reach-limited, with pose errors up to 1.4 mm.
- **Single-block offset bracket (C1/C4 explored).** It needs 105 mm of axial move, worse than both C1 and C2.

**Remaining scope:**
- **Re-plan at full settings:** UR5e bascarrot, basket, tubempty, ct2s; FR5 basket, ct2s; FR5 tomato after its round.
- **Rebuild:** the stir library and its entry/exit, and the 22-edge hub, per arm.
- **Redo the cable run (#36).**
- **Before machining:** check the clocking of DH's flange hole pattern against the robot-side screws (§3).
- Lanes are in §4.

## 1. The problem, measured [M]

Distances below are in mm. Negative values are penetration depths from `mj_geomDistance` with distmax 10 mm. Positive values are the checker's exact GJK lower bound, `distance.Bounds.pair`.

| Pair | UR5e `ur5e_enc2_pgc` | FR5 `fr5_j6_pgc_sp20` |
|---|---|---|
| Housing `R_gripper_oem_envelope` vs wrist 3 | **−16.87** | **−14.74** |
| `R_gripper_oem_upper` vs wrist 3 | −6.30 | +10.5 |
| **Housing vs wrist 2, over the whole J6 turn (new)** | **−1.57: in contact at every J6 angle** | 2.14: within 5 mm at every J6 angle |
| Housing vs wrist 1, over J5 × J6 | −33.9: contact in 9.6 % of the grid (\|J5\| > 112.5°) | ≥ 10 |

**New finding: wrist 2 is unchecked too.**
- R_tool has no joint, so it is welded to wrist 3, whose parent is wrist 2.
- `Checker.required` skips parent↔child weld pairs. So the tool vs wrist 2 is never checked in a path, just like the tool vs wrist 3.
- Both pairs depend only on J6, so a static sweep over the J6 turn certifies them for every path (`r19mount_static.py`).

**Measurement pitfall.**
- With a large distmax (0.2 m), `mj_geomDistance` is badly wrong for these meshes. It reported −38 mm for a pair that is 5.8 mm apart, because it inflates both shapes and takes an MPR depth.
- With distmax 10 mm it equals the exact GJK value. Every distance here uses 10 mm, cross-checked against GJK.
- The brief's −6.70 for the upper piece is the large-distmax reading.

**The R10 pose:**
- The gripper axis is 26.6° off J6.
- The mounting-face centre is 77.7 mm off the axis and 45.1 mm behind the flange plane.
- The TCP is at (13.4, 0, 127.9) mm in the flange frame.
- The gripper body leans over the flange. So a bracket from the flange can reach the gripper's mounting face only after the gripper moves out far enough: along the flange axis, along its own axis, or onto the axis turned.

## 2. Candidates and results

**Frames.** F is the UR5e flange frame (DH frame 6, z out of the flange). u = +x_F is the side the gripper base leans toward. The FR5 options use `fr5_j6_pgc`: clock 90°, so u = +y_F, and no spacer, because the bracket replaces the sp20 plate.

**What a mount is.** A rigid motion of the whole gripper. The TCP changes by exactly that motion.

**How each candidate was chosen.** The smallest move that passes all of these checks (`r19mount_design.py`, results in `design_*.json`):
- the housing and the bracket body ≥ 5 mm from wrist 3 on both arms;
- no bracket piece inside the housing;
- the buildability rules (walls ≥ 8 mm).

**Search results:**
- C1 L bracket: dz = 77–80 mm.
- C4 L bracket with a radial move (du 0–60 mm): no smaller change than C1.
- One convex block: 105 mm.
- Wedge (C2): 94.1 mm at the buildability corner. Its face low edge is 21.9 mm high, and the material over the low-side M6 screws is 12.3 mm.
- Inline (C3): 61.1 / 63.9 / 65.9 mm with a 5 / 8 / 10 mm spacer.
- **Not modelled:** a J-shaped bracket hanging the gripper beside the wrist. By geometry it could reach a TCP change of about 45 mm [E]. But its leg would come down to z ≈ −54 mm at r 45–53 mm, where wrist 2's top is at z −59 to −64 over the J6 turn [M], and it hangs the gripper about 115 mm off axis. It was not pursued.

### 2.1 Candidate table [M unless labelled]

| | **m1: C1 L bracket** | **m2: C2 wedge** | **m3: C3 inline** |
|---|---|---|---|
| Move | +77.5 mm along the flange axis, 0° | face onto a wedge over the flange: 94.1 mm along the gripper axis, 0° | turned 26.6° about the jaw axis, face on an 8 mm spacer |
| TCP change, UR5e (flange frame u, y, z) | (0, 0, +77.5) = **77.5 mm, 0°** | (−42.7, 0, +83.9) = **94.1 mm, 0°**; tool frame (94.1, 0, 0.6) | (+6.6, 0, +63.6) = **63.9 mm, 26.6°** |
| TCP change, FR5, vs `sp20` | 57.5 mm, 0° | 76.9 mm, 0°; tool frame (76.2, 0, 9.6) | 44.1 mm, 26.6° |
| Bracket mass [M geometry, 2.70 g/cm³ S] | 0.327 kg | **0.268 kg** | 0.062 kg |
| Bracket CoG in F (mm) | (39.8, 0, 16.3) | (17.3, 0, 19.1) | (0, 0, 4.1) |
| + DH standard flange | 0.061 kg in every case [S CAD volume 22.6 cm³ × E aluminium] | | |
| Wrist 3, housing / bracket body (UR5e) | 21.2 / 5.76 (arm), 13.8 (leg) | **22.7 / 8.76** | 8.76 / 5.76 |
| Wrist 3, housing / bracket body (FR5) | 17.1 / 6.0, 6.9 | **23.0 / 9.0** | 9.0 / 6.0 |
| Mating boss (exempt, bolted face) | 0.76 / 1.0 | 0.76 / 1.0 | 0.76 / 1.0 |
| Wrist 2, whole J6 turn (both arms) | ≥ 10 | ≥ 10 | ≥ 10 |
| Wrist 1, J5 × J6 (both arms) | ≥ 10, J5 free on its whole range | ≥ 10 | ≥ 10 |
| Forearm, J4 × J5 × J6, share of the grid in contact (housing / bracket), UR5e; FR5 | 12.2 / 13.6 %; 12.6 / 15.7 % | 9.6 / 8.7 %; 9.7 / 10.5 % | 8.8 / 5.2 %; 10.0 / 7.9 % |
| Wok + heaviest dish: payload, CoG offset, margin | 4.54 kg, 187 mm; UR5e 0.46 kg, FR5 0.46 kg | **4.48 kg, 223 mm; 0.52 / 0.52 kg** | 4.27 kg, 246 mm; 0.73 / 0.73 kg |
| Full soak tub | 4.37 kg, 264 mm | **4.31 kg, 284 mm** (FR5 limit 300) | 4.10 kg, 285 mm |
| Flange static moment, worst orientation (wok / tub) | 8.3 / 11.3 N·m | 9.8 / 12.0 N·m | 10.3 / 11.5 N·m |
| PGC jaw moment, wok | 6.23 N·m level, 6.47 worst (unchanged by any mount) | | |
| **Pilots certified ≤ 4 mm (wok, lid, spatula, carrot) × 2 arms** | 7 of 8 (FR5 spatula: false hit; wok only as a re-plan) | **8 of 8** | 6 of 8 (wok fails on both arms) |

Notes on the table:
- **Reference values:**
  - current UR5e: wok 4.15 kg at 157 mm, tub 3.98 kg at 213 mm;
  - FR5 `sp20` (0.25 kg plate [E]): wok 4.40 kg at 158 mm, tub 4.23 kg at 219 mm;
  - flange moment 6.4–6.8 N·m (wok) and 8.3–9.1 N·m (tub).
- **Payload rules:**
  - FR5: 5 kg at ≤ 300 mm [S, Fairino manual 3.4.5.2.5].
  - UR5e: 5 kg [S, datasheet], with the 0.35 m CoG radius the repo uses (`arms.py`). UR's payload diagram was not re-read here.
  - Every case is inside both ratings.
- **Forearm contacts:** they happen with the wrist folded back (|J5| ≈ 110–180°). The checker rejects these in paths (self, 0 mm). Every mount has a lower contact share than the current pose (UR5e 16.3 %, FR5 17.1 %).
- **Joint torque:** ≤ 0.71 of the rated envelope in every wok pilot.

Pictures: `results/r19/mount/view_ur5e_enc2_pgc_m{1,2,3}.png` and the current pose `view_ur5e_enc2_pgc.png`. Each shows the wrist (grey), the bracket (orange) and the housing, side and 3/4 views.

### 2.2 Pilots: the hardest sets on both arms [M]

**How each pilot ran:**
- **Re-target (rt):** `r19mount_retarget.py` keeps the certified object path exactly. Every stored state's TCP is solved on the new mount by IK continuation, the cart is held at its stored value, and each state gets the planning check.
- **Re-plan (plan):** the original runner at smoke settings (`r19mount_run.py`; output in `results/r19/mount/`):
  - `r19pot_chain.py` for the chains, with SEEDS=1 TRIES=8 KEEP=4 + SEEDUR (the adopted UR5e chain) and the chains' own options;
  - `r19prepchain.py` / `r19fr5prep_actions.py` for the carrot, with the R19_PREP_LAYOUT r2 / R19_FR5_PREP2 argv.
- **The binding ≤ 4 mm re-check:**
  - `r19mount_check.py`, which is `r19pot_check.py` executed unchanged, with WOKPY=1 for the wok;
  - `r19prep_verify.py` for the carrot.

**Bold** = certified: planning ok and the ≤ 4 mm re-check with 0 hits (the counts are states). Times are planning, then re-check, in seconds; each run was under 5 min. m2 certificates use the final m2 geometry (8 mm boss). Earlier m2 checks are kept as superseded.

| Set | Arm | m1 | m2 | m3 |
|---|---|---|---|---|
| wok | UR5e | rt: 17 states fail on reach (pose error ≤ 1.4 mm, no hits). **plan: ok 213 s; 0 / 4,496 (217 s); act 47.9 s** | **rt: ok 125 s; 0 / 5,115 (183 s); act 48.9 s.** plan: ok 224 s | rt: 81 fail (upper arm vs base plate). plan (4 tries, incl. GTILT 0 / 40): anchor "over the plate" fails (joint jump > 10° in the 90° tip) |
| wok | FR5 | rt: 18 fail (reach). **plan: ok 207 s; 0 / 4,594 (209 s)** | **rt: ok 116 s; 0 / 5,205 (178 s)**. plan: ok 207 s | rt: 56 fail. plan (4 tries): "over the plate" and "under the tap" fail |
| lid | UR5e | **rt: ok 54 s; 0 / 2,410 (102 s)** | **rt: ok 70 s; 0 / 2,299 (131 s)** | **rt: ok 45 s; 0 / 1,799 (77 s)** |
| lid | FR5 | rt: release retreat hits the cart beam. smoke plan: lift-off anchor fails. **SEEDS=2 TRIES=12: ok 126 s; 0 / 2,601 (77 s)** | **rt: ok 55 s; 0 / 2,269 (128 s)** | **rt: ok 43 s; 0 / 1,836 (39 s)** |
| spatula (ends at the stir stroke start) | UR5e | **rt: ok 73 s; 0 / 2,021 (84 s)** | **rt: ok 60 s; 0 / 2,457 (63 s)** | **rt: ok 74 s; 0 / 2,488 (97 s)** |
| spatula | FR5 | 4 plans and rt fail: pick → lifted, held blade vs raw tomato. **Exact gap 9.80 mm; MuJoCo box-box reports 4.9 mm (the known false-hit class, README R19)** | rt: same 1 false-hit state. **plan: ok 105 s; 0 / 2,237 (65 s)** | **rt: ok 61 s; 0 / 2,157 (93 s)** |
| carrot | UR5e | rt: 15 fail. **plan with SEEDUR = adopted carrot: ok 176 s; 0 / 2,998 (136 s)** | rt: 11 fail (upper arm vs base plate at the chute). **plan with SEEDUR: ok 183 s; 0 / 3,558 (84 s)** | **rt: ok 186 s; 0 / 5,030 (203 s)** |
| carrot | FR5 | 4 fail. **plan XTAPC=−0.15 (fixed cart under the tap): ok 170 s; 0 / 4,188 (56 s)** | rt: 3 rinse states (upper arm 7.5 mm from the door, gate 10). Under-the-tap anchor fails in 5 variants. **plan XTAPC=−0.15: ok 182 s; 0 / 3,741 (102 s); also XTAPC=+0.10 and lane yaw 45° certified** | **plan: ok 226 s; 0 / 6,300 (258 s)** |

- The re-targeted chains keep the source's action time (re-target upper bound +0.1 s).
- The re-plans: wok 47.9 / 48.3 s (m1), carrot 45.9–52.5 s, lid 20.2 s, spatula 26.6 s.
- `XTAPC` only fixes the cart along the counter under the tap. The object keyframes are the adopted FR5 ones (XL1R / XL2R y30p−30, CHAPP=0, CHUP).

### 2.3 m2 on the other adopted sets [M]

| Set | UR5e m2 | FR5 m2 |
|---|---|---|
| plate 2 | **rt: ok; 0 / 5,089** | **rt: ok; 0 / 5,185** |
| lever | rt: reach (pose error ≤ 5.7 mm). **plan smoke: ok 33 s; 0 / 180** | rt: reach. **plan: ok 25 s; 0 / 190** |
| spider | rt: 20 fail. **plan smoke: ok 182 s; 0 / 4,375** | **rt: ok; 0 / 5,841** |
| press | **rt: ok; 0 / 221** | **rt: ok; 0 / 223** |
| tomato | **rt: ok; 0 / 3,090** | not tried: being re-planned in R19_FR5_PREP3 |
| ctray | **rt: ok; 0 / 3,320** | **rt: ok; 0 / 3,456** |
| tubfill | **rt: ok; 0 / 2,932** | **rt: ok; 0 / 2,975** |
| soak | rt: 19 fail (forearm 8.9 mm from closed door 0_1, gate 10). **plan smoke + SEEDUR: ok 40 s; 0 / 2,151** | **rt: ok; 0 / 2,265** |
| tubempty | rt: 63 fail (upper arm vs closed door / cabinet over the sink). Smoke plan: every anchor fails | **rt: ok; 0 / 3,671** |
| bascarrot | rt: 1 approach state (11.5° joint step). Smoke plan: release retreat hits the base plate | rt: forearm vs base. **plan smoke + SEEDUR: ok 50 s; 0 / 1,959** |
| basket | rt: 41 fail (wrist 2 vs door 1_0 at the rinse). Smoke plan: under-the-tap anchor fails | rt: 39 fail (same). Smoke plan (fr5xfull argv): under-the-tap anchor fails |
| stgwok | **rt: ok; 0 / 1,974** | — (no FR5 set) |
| fold / unfold | **rt: ok; 0 / 511, 0 / 512** | **rt: ok; 0 / 490, 0 / 490** |
| ct2s | rt: 40 states of joint steps > 10°. Smoke plan: anchor "over the pan on the folded cradle" fails | rt: 49 (steps). Smoke plan: same anchor fails |

Per-run data is in `results/r19/mount/summary.json` (`python r19mount_table.py`).

## 3. The recommended bracket (m2) in enough detail to build it

**Coordinates.** All in F, in mm:
- origin at the robot flange face centre; z out of the flange;
- u is the direction the gripper base leans toward: UR5e +x of the flange frame (DH frame 6); FR5 +y (this repo's 90° gripper clocking);
- y is the jaw stroke (the cable outlet stays under the +y jaw).
- Geometry source: `r19mount.MOUNTS['m2']`, built by `r19mount.bracket_F`.

**One piece of 6061-T6.**
- Stock about 100 × 75 × 56 mm, plus the 2.5 mm spigot.
- Mass 0.268 kg solid (volume 99.1 cm³ after holes) [M geometry; density S]. CoG (17.3, 0, 19.1).

**1. Robot side (the ISO 9409-1-50-4-M6 tool flange of both arms [S: UR5e / Fairino manual 3.4.2]).**
- A **Ø63 × 8 mm mating boss** (z 0–8). Its flat bottom face is the mating face.
- A **Ø31.5 g6 × 2.5 mm spigot** under it, into the robot's Ø31.5 H7 recess (the same spigot as DH's standard flange [S, CAD]).
- A **Ø6 H7 × 6 pin hole** on the ISO pin position.
- **4 × Ø6.6 through holes on PCD 50**, at 45° to the pin, for M6 (8.8, 8 N·m [S, Fairino]). With u on the pin line, they sit at (±17.7, ±17.7).
  - **Low-side screws (u = −17.7):** 12.3 mm of material. Use DIN 7984 low-head M6 in Ø11 × 4.3 counterbores, which leaves 8 mm under the head [E].
  - **High-side screws (u = +17.7):** 30.1 mm of material. Use Ø11 counterbores about 22 mm deep from the inclined face, again leaving 8 mm under the head [E].
  - All four are inserted before the gripper goes on.

**2. Gripper side.**
- **The inclined seat:** the plane through (35.0, 0, 38.75) with normal (−0.448, 0, 0.894). That is 26.6° to the flange face, rising toward +u (tan = 0.50).
- **On it, a Ø75 seat for DH's standard flange,** centred at u = 35.0, z = 38.75. It is the flange's robot face: X0 in the model, so DH's 98 / 138.5 mm heights are unchanged.
- **Seat features:**
  - a Ø31.5 H7 × 3 recess for the DH flange spigot (Ø31.5 × 2.5 [S CAD]);
  - **4 × M6 tapped ≥ 12 deep on PCD 50**, perpendicular to the seat;
  - a Ø6 H7 pin hole.
  - Together these are an ISO 50 tool face, so DH's flange bolts on exactly as on a robot. Clock it so the jaw stroke runs along y.

**3. Body.**
- The solid between the boss top and the seat: the hull of the two, cut by the seat plane.
- Extent: u −31.5 to +68.5, y ±37.5, z 0–55.6.
- The +u side overhangs the flange by 37 mm under the seat's high side. The underside rises from z 8 at u = 31.5 to z 55.5 at u = 68.5.
- Seat-plane height above the flange: 8.7 at u = −25, 12.3 at −17.7, 21.2 on the axis, 37.0 at the flange edge (u = 31.5), 55.5 at the seat's high edge.
- The thinnest section is the 8 mm boss rim on the low side (the wall rule, ≥ 8 mm [E]).
- Optional: lightening pockets in the +u overhang, with walls ≥ 8 mm [E, not modelled].

**4. Assembly.**
1. Bolt the wedge to the robot flange (4 × M6 from the top).
2. Bolt DH's standard flange onto the seat with its 4 M6 screws (DH's kit) and its Ø6 pin.
3. Fit the PGC over the flange ears and tighten DH's 4 radial screws [S, R19_CABLE2 §1].
- Strength: the static flange moment is ≤ 12 N·m (tub, worst orientation). That is small for a solid 6061 block clamped by 4 × M6 8.8 [E].

**5. Check before machining [E].**
- The high-side robot screws come out on the seat 26 mm from its centre, on the same PCD-50 circle as the gripper-side M6 holes. In the seat plane they sit at ±137.5° from the uphill (+u) direction.
- The gripper-side holes must therefore sit at 0 / 90 / 180 / 270°. That leaves 18 mm between hole centres, about a 10 mm wall. They must not sit at ±135°.
- Where they land is fixed by DH's flange: its pin-to-ear clocking relative to the jaws, in its STEP. Not read here.
- If they collide, there is a two-piece fallback: a flat 8 mm ISO plate plus the wedge screwed to it from below. It moves the TCP a further 8 mm along the flange axis [E]; that variant is not piloted.

**6. Model.** In the sim the wedge is two convex pieces on R_tool:
- `R_gripper_oem_mount_base`: the boss, the exempt mating part;
- `R_gripper_oem_mount_body`: the rest. It is named like the housing, so every tool treats it as gripper body and never as held.
- Its mass, the DH flange and the existing 1.2 kg EOAT are folded into R_tool's inertial, so the checker's load check and the torque ratios include them.

**m1 and m3, for comparison.**
- **m1, L bracket (0.327 kg).** A 63 mm wide plate, 15 mm thick including the boss, from u = −31.5 to 44 over wrist 3. A solid leg (u 44–116, z 5–49) carries the inclined Ø75 seat at (77.7, 0, 32.4) with 10 mm behind it. The arm plate is 5.76 mm from wrist 3.
- **m3, inline (0.062 kg).** A Ø63 × 8 mm ISO 50 spacer, through-bolted with DH's flange (4 × M6 through both into the robot) [E]. Without the spacer, the DH flange rim would be 0.76 mm from the enclosing wrist-3 hull. The real UR mesh gap there is about 7 mm.

## 4. Re-certification scope and controller lanes (m2)

**Options:** `ARM=ur5e_enc2_pgc_m2` and `ARM=fr5_j6_pgc_m2`.

**Already certified in this round** (≤ 4 mm, 0 hits, final geometry; files in `results/r19/mount/`):

| | Certified (file) |
|---|---|
| UR5e (15) | wok `chain_wok_s-1_rt_*`, plate 2 `chain_wok_s-1_rtplate2_*`, lever `chain_lever_s+1_mnt_*`, lid `chain_lid_s-1_rt_*`, spider `chain_spider_s+1_mnt_*`, spatula `chain_spatula_s-1_rt_*`, carrot `chain_carrot_mnt2t8_*`, press, tomato, ctray, tubfill (`*_rt_*`), soak `chain_soak_mnt_*`, stgwok, fold, unfold (`*_rt_*`) |
| FR5 (15) | wok, plate 2, lid, spider (`_rt`), lever (`_mnt`), spatula `chain_spatula_s-1_mnt_*`, carrot `chain_carrot_mnt5v3_*`, press, ctray, soak, tubempty, tubfill, fold, unfold (`_rt`), bascarrot `chain_bascarrot_mnt_*` |

Their certificates are `check_<chain>_rack_sp1.56_.20[_t8].json` and `<chain>_verify4mm[_pot].json`. The table above lists the `ur5e_enc2_pgc_m2` / `fr5_j6_pgc_m2` file of each.

**Still to do:**
- UR5e: 4 prep sets (bascarrot, basket, tubempty, ct2s).
- FR5: 2 prep sets (basket, ct2s), plus the tomato after R19_FR5_PREP3.
- Both arms: the stir library and its entry/exit, and the hub (22 edges + graph).
- **Cable (#36):** the provisional runs belong to the old pose. There are no m2 cable options yet, because `arms.py` generates cable variants only for the two current bases. This is for the cable owner.
- **Optional:**
  - full-setting re-plans of the smoke-level files (lever, UR spider, FR5 spatula, carrots, UR soak, FR5 bascarrot);
  - the #13 tolerance runs.
- **The checker decision (#42):** the static certificate `results/r19/mount/static.json` covers both unchecked tool pairs:
  - wrist 3 at its fixed pose;
  - wrist 2 over the whole J6 turn.
  Adding them to `checker.py` is the owners' call (not edited here).

**Effort [E, from the pilot and the original run times]:** prep full re-plans 5–20 min each (×6); stir about 25–40 min per arm; hub 1–3 h per arm in 4 parallel lanes. Each re-check is 0.5–4 min.

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
D=results/r19/mount; P=results/r19/prep; G=results/r19/mount/logs; POT="RACK=keyed SPX=1.56 SPY=.20"
# ---- lane 1 (UR5e prep, full settings, each 5-20 min; output results/r19/mount/, never overwrites) ----
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=bascarrot SEEDS=3 TRIES=12 KEEP=4 SEEDUR=$P/chain_bascarrot_full_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgc_m2 TAG=full > $G/full_bascarrot_ur5e_m2.txt 2>&1
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=basket SEEDS=3 TRIES=12 KEEP=4 BYAW=-20 BPITCH=30 SEEDUR=$P/chain_basket_y20p30_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgc_m2 TAG=full > $G/full_basket_ur5e_m2.txt 2>&1
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=tubempty SEEDS=3 TRIES=12 KEEP=4 SEEDUR=$P/chain_tubempty_full_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgc_m2 TAG=full > $G/full_tubempty_ur5e_m2.txt 2>&1
$PY r19mount_run.py RUNNER=r19prep5_chain.py ACT=ct2s CP=-.52 LANEC=-.52 PLUME=0 MOUTHZ=.12 CLANE=-0.954,-.16,1.12 SEEDS=3 TRIES=12 KEEP=4 ARM=ur5e_enc2_pgc_m2 TAG=full > $G/full_ct2s_ur5e_m2.txt 2>&1
#   re-check each one that is ok (0.5-4 min each)
for s in bascarrot basket tubempty; do $PY r19prep_verify.py FILE=$D/chain_${s}_full_ur5e_enc2_pgc_m2.json NPROC=16; done
$PY r19prep5_verify.py FILE=$D/chain_ct2s_full_ur5e_enc2_pgc_m2.json NPROC=16 ARM=ur5e_enc2_pgc_m2 $POT
#   if basket / tubempty still fail (wrist 2 / upper arm vs the closed door over the sink at the tap): motion variants as
#   R19_FR5_PREP2 did; first the fixed cart under the tap that rescued the FR5 carrot here, e.g. (each < 5 min)
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=basket SEEDS=1 TRIES=8 KEEP=4 BYAW=-20 BPITCH=30 XTAPC=-0.15 SEEDUR=$P/chain_basket_y20p30_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgc_m2 TAG=xt15 > $G/xt15_basket_ur5e_m2.txt 2>&1
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=basket SEEDS=1 TRIES=8 KEEP=4 BYAW=-20 BPITCH=30 XTAPC=0.10 SEEDUR=$P/chain_basket_y20p30_ur5e_enc2_pgc.json ARM=ur5e_enc2_pgc_m2 TAG=xt10 > $G/xt10_basket_ur5e_m2.txt 2>&1
# ---- lane 2 (FR5 prep, full settings) ----
$PY r19mount_run.py RUNNER=r19fr5prep_actions.py ACT=basket SEEDS=3 TRIES=12 KEEP=4 BYAW=-20 BPITCH=30 XD=0,-.06,.02 XTAPC=-0.25 "XCART=pick:-0.55;over the tub:-0.55" SEEDUR=$P/chain_basket_y20p30_ur5e_enc2_pgc.json ARM=fr5_j6_pgc_m2 TAG=full > $G/full_basket_fr5_m2.txt 2>&1
$PY r19mount_run.py RUNNER=r19prep5_chain.py ACT=ct2s CP=-.52 PLUME=0 MOUTHZ=.12 CLANE=-0.954,-.16,1.12 SEEDS=3 TRIES=12 KEEP=4 ARM=fr5_j6_pgc_m2 TAG=full > $G/full_ct2s_fr5_m2.txt 2>&1
$PY r19prep_verify.py FILE=$D/chain_basket_full_fr5_j6_pgc_m2.json NPROC=16
$PY r19prep5_verify.py FILE=$D/chain_ct2s_full_fr5_j6_pgc_m2.json NPROC=16 ARM=fr5_j6_pgc_m2 $POT
#   tomato, after R19_FR5_PREP3 adopts its FR5 tomato chain (<chain> = that file): exact re-target, then the re-check
$PY r19mount_retarget.py KIND=prep SRC=<chain> ARM=fr5_j6_pgc_m2 TAG=rt && $PY r19prep_verify.py FILE=$D/chain_tomato_rt_fr5_j6_pgc_m2.json NPROC=16
# ---- lane 3 (stir library, per arm; steps 1-5 min each, as R19_STIR.md 7 / R19_STIR2) ----
for A in ur5e_enc2_pgc_m2 fr5_j6_pgc_m2; do
 $PY r19stir_reach.py ARM=$A KEEP=48
 $PY r19stir_cycle.py works ARM=$A
 $PY r19stir_cycle.py returns ARM=$A ROUNDS=0 FRESH=1
 $PY r19stir_cycle.py returns ARM=$A ROUNDS=1 PART=0/2
 $PY r19stir_cycle.py returns ARM=$A ROUNDS=1 PART=1/2
 $PY r19stir_cycle.py returns ARM=$A ROUNDS=2,3
 $PY r19stir_cycle.py cycle ARM=$A
 for s in works returns "cert PART=new" "cert PART=old" std "law W=.1" "law W=.2" "law W=.4" lib report; do $PY r19spill_cycle.py $s ARM=$A WORKERS=16; done
done
# ---- lane 4 (hub, per arm: r19fr5_hub.py takes all six chain files; writes results/r19/fr5/hub_<HUBTAG>/) ----
HU="RACK=keyed SPX=1.56 SPY=.20 PY=.15 ARM=ur5e_enc2_pgc_m2 HUBTAG=py.15_ur5e_enc2_pgc_m2 WOK=$D/chain_wok_s-1_rt_ur5e_enc2_pgc_m2.json WOK2=$D/chain_wok_s-1_rtplate2_ur5e_enc2_pgc_m2.json LEVER=$D/chain_lever_s+1_mnt_ur5e_enc2_pgc_m2.json LID=$D/chain_lid_s-1_rt_ur5e_enc2_pgc_m2.json SPIDER=$D/chain_spider_s+1_mnt_ur5e_enc2_pgc_m2.json SPAT=$D/chain_spatula_s-1_rt_ur5e_enc2_pgc_m2.json"
HF="RACK=keyed SPX=1.56 SPY=.20 PY=.15 ARM=fr5_j6_pgc_m2 HUBTAG=py.15_fr5_j6_pgc_m2 WOK=$D/chain_wok_s-1_rt_fr5_j6_pgc_m2.json WOK2=$D/chain_wok_s-1_rtplate2_fr5_j6_pgc_m2.json LEVER=$D/chain_lever_s+1_mnt_fr5_j6_pgc_m2.json LID=$D/chain_lid_s-1_rt_fr5_j6_pgc_m2.json SPIDER=$D/chain_spider_s+1_rt_fr5_j6_pgc_m2.json SPAT=$D/chain_spatula_s-1_mnt_fr5_j6_pgc_m2.json"
for H in "$HU" "$HF"; do
 $PY r19fr5_hub.py endpoints $H; $PY r19fr5_hub.py tuck ELBOW=neg $H; $PY r19fr5_hub.py hubs TUCK=neg $H
 for e in "H_SPAT H_SINK" "H_SINK H_WOK" "H_WOK H_POT" "SPAT H_SPAT" "SPAT H_SINK" "SPAT LEV_C" "LEV_C H_SPAT" "LEV_O H_SPAT" \
          "LEV_C H_SINK" "LEV_O H_SINK" "LEV_C H_WOK" "LEV_O H_WOK" "WOK H_WOK" "LEV_O WOK" "WOK H_SINK" "WOK H_POT" \
          "SPIDER H_POT" "LID_POT H_POT" "LID_RACK H_POT" "SPIDER H_WOK" "LID_POT H_WOK" "LID_RACK H_WOK"; do
  set -- $e; $PY r19fr5_hub.py edge A=$1 B=$2 PLAN_S=120 $H > $G/hub_$(echo $H | sed 's/.*ARM=\([^ ]*\).*/\1/')_$1__$2.txt 2>&1
 done   # split the 22 edges into 4 parallel lanes as R19_FR5.md 5 does; LID_* fallbacks (F_LID_*) as there
 $PY r19fr5_hub.py graph $H
done
# ---- lane 5 (after lanes 3 and 4): the stir entry / exit (r19stir2_join.py through the new wrapper) ----
$PY r19mount_stirjoin.py join ARM=ur5e_enc2_pgc_m2 SPATCHAIN=$D/chain_spatula_s-1_rt_ur5e_enc2_pgc_m2.json HUBSFILE=results/r19/fr5/hub_py.15_ur5e_enc2_pgc_m2/hubs.json WORKERS=24
$PY r19mount_stirjoin.py join ARM=fr5_j6_pgc_m2 SPATCHAIN=$D/chain_spatula_s-1_mnt_fr5_j6_pgc_m2.json WORKERS=24
# ---- lane 6 (optional): full-setting re-plans of the smoke-level files, e.g. the lever / spider (UR5e), as their adopted argv ----
$PY r19mount_run.py RUNNER=r19pot_chain.py ACT=spider SIGN=1 SEEDS=2 TRIES=12 KEEP=6 SEEDUR=results/r19/pot/chain_spider_s+1_pot_1.56_.20_ur5e_enc2_pgc.json $POT PY=.15 ARM=ur5e_enc2_pgc_m2 TAG=full
# ---- tables ----
$PY r19mount_table.py
```

## 5. Files

**New code** (`sim/r10/claude/`):

| File | Purpose |
|---|---|
| `r19mount.py` | the mounts (`MOUNTS` m1–m3), bracket geometry, mass properties, and the `apply()` hook |
| `r19mount_design.py` | the design search |
| `r19mount_static.py` | wrist 3 / 2 / 1 / forearm sweeps |
| `r19mount_payload.py` | the payload check |
| `r19mount_retarget.py` | IK re-target, chains and prep (`CHAINSRC=` for step 4/5) |
| `r19mount_run.py` | runs any planner unchanged, with output redirected to `results/r19/mount/` and no overwrite |
| `r19mount_check.py` | `r19pot_check.py` unchanged, with output to `results/r19/mount/` |
| `r19mount_seed.py` | FR5 seed files for SEEDUR |
| `r19mount_md5.py` | the unchanged-options proof |
| `r19mount_render.py` | the pictures |
| `r19mount_table.py` | the tables (`summary.json`) |
| `r19mount_stirjoin.py` | the stir-join wrapper for the lanes |

**Changed: `arms.py`** (backup `arms.py.bak_r19mount`).
- It imports `r19mount` and adds 6 options: `ur5e_enc2_pgc_m{1,2,3}` and `fr5_j6_pgc_m{1,2,3}`.
- It adds one line in `swap()`: `if ARMS[arm].get('mount'):_mnt.apply(...)`.
- **Proof:** all **80 options that existed before build byte-identical scenes, 98 of 98** (`results/r19/mount/md5_compare.json`, last run after the final edit).

**Results** (`results/r19/mount/`):
- `design*.json`, `static.json`, `payload.json`, `summary.json`;
- every pilot chain `chain_*` and its certificate `check_*` / `*_verify4mm*`. The m2 certificates made before the 8 mm boss are superseded by `_t8` or later files; `summary.json` flags them;
- `seed_*`, `md5_*`, `view_*.png`, `geo_cache.pkl`, `logs/`.

**Not touched:**
- `scene.py`, `checker.py`, `distance.py`, `chain.py`, `kitchen*`, `*_verify.py`, `r19cable*`, `r19tol_core.py`, `models/`, `DECISIONS.md`, READMEs, GitHub;
- the other agents' files (`r19fr5prep2_*`, dock / export);
- no process I did not start was killed.

## 6. Limits

- **Smoke settings.** Every re-plan here is a smoke run (SEEDS 1–3, TRIES 8–12), each under 5 min. Every pass was re-checked at ≤ 4 mm. A failure at smoke is not a proof of infeasibility: lane 1 runs the full settings.
- **Re-targets** keep the cart at the stored values. A re-target failure (reach, joint jumps) does not mean the set cannot be planned. The re-plans showed this for the wok, lever and spider.
- **The bracket model** is two convex hulls (circles as circumscribed polygons). Holes, the spigot and DH's flange enter the mass only.
  - The DH flange-hole clocking (§3.5) and the robot screw lengths for each arm's thread depth must be checked on the drawing.
  - The m1 leg was kept solid: an 8 mm-wall pocket did not fit.
- **Payload.**
  - The UR5e's CoG limit is the repo's 0.35 m (`arms.py`), not re-read from UR's payload diagram.
  - The DH flange mass is the CAD volume × aluminium density [E].
  - The checker's mass model now includes the bracket for the mount options. The `sp20` option still lacks its plate mass (R19_FR5 §7, owners' item).
- **The FR5 m1 spatula failure is a checker artifact:** MuJoCo 3.2.5 box-box contacts inside the margin, the R18 held-spatula boxes (README R19, "Model bug, conservative"). It is not a mount effect, and fixing it is a `scene.py` change for its owner.
- **Cable.** Not modelled for the mount options. The cable outlet (+y jaw, 21 mm above the mounting face) sits about 24 mm above the wedge top. The route back to the tool connector must be redone (#36).
