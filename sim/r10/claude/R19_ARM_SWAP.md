# R19 arm swap: the sim can run the Fairino FR5 (and the Elite CS66) instead of the UR5e

2026-10-13. The user's decision: "你肯定先去验证便宜的能不能用吧" — verify the cheap arm first.

Nothing was bought, and no supplier was contacted. No gap, step size or force was changed.

**Labels:**
- [M] = manufacturer file, page or manual;
- [O] = other source;
- [E] = derived or estimated here;
- ND = not published / not found.

## 0. Status in one table

| Check | UR5e (default) | FR5 (stock J6 ±175°) | CS66 |
|---|---|---|---|
| Regression, `ACT=lever` | **identical** to `chain_lever_s+1_final.json` (every key, `play` diff 0.0) | — | — |
| Faucet lever (`ACT=lever`) | 3.5 s, 6.0 mm | **pass**: 3.6 s, min reserve 4.0 mm | **pass**: 3.5 s, 6.0 mm |
| Lid (`ACT=lid`, `TRIES=16` as in the UR5e final) | 20.2 s, 1.0 mm | **fail** (reasons in §6) | **fail** (§6) |
| Stir: the 5 stroke starts (`r15reach.py stir`) | R15: 80/80 | **5/5 reachable**: 14–20 starts clear of the plume each, best reserve 3.7–5.0 mm | not run |
| Stir cycle, wok, spider, spatula, plate 2, hub | checked in R17–R19 | not run: each takes more than 5 min; commands in §8 | not run |

**Verdict so far:** the FR5 model works in every tool. The first real difference has appeared: the stock FR5 cannot do the lid action. The FR5 is **not yet shown to pass the library**; the full lane list in §8 decides that.

## 1. How to choose the arm

Use `ARM=<id>` on any command line (all scripts take `KEY=VALUE`), or `cfg['arm']`, or the environment variable `ARM`.

| id | Arm |
|---|---|
| `ur5e` | the default; nothing in the model is touched |
| `fr5` | Fairino FR5, stock J6 ±175° |
| `fr5_j6` | FR5 with the optional J6 ±360° |
| `cs66` | Elite CS66 |

Every output of another arm gets a `_<id>` suffix:
- `results/r17/chain_*_<id>.json`;
- `results/r15/reach_*_<id>.json`;
- `results/r19/stir/stirwalk2_*_<id>.json`;
- `results/r19/hub_<id>/`;
- `assets/envelope_<id>_<tilt>.json`.

No UR5e result is overwritten.

## 2. Model sources

### FR5 (`r19/arm_fr5.json`, built by `r19arm_fit.py fr5`)

The vendor files are saved as data in `sim/vendor_r19/fairino/`; nothing in them was executed:
- `fairino5_v6.urdf`;
- MoveIt `joint_limits.yaml`, `.srdf` and `pilz_cartesian_limits.yaml`;
- the 7 link STLs;
- source: github.com/FAIR-INNOVATION/frcobot_ros2.

| Item | Value | Label / source |
|---|---|---|
| Joint origins and axes | URDF joint origins; they equal the Fairino DH table (d1 152, a2 −425, a3 −395, d4 102, d5 102 mm) within 0.1 mm (URDF d4 = 102.1) | [M] URDF + [M] Cobots manual Table 2.4-5 (fairino-doc-en.readthedocs.io/latest/CobotsManual/robot_brief_introduction.html) |
| Flange | **d6 = 100 mm** (DH table). The URDF has no flange frame; its wrist3 STL ends at 99.0 mm | [M] |
| Joint limits | J1 ±175, J2 +85/−265, J3 ±160, J4 +85/−265, J5 ±175, J6 ±175° | [M] fairino.us FR5 page. The URDF has J3 ±162°; the stricter ±160° is used |
| J6 ±360° | "Wrist3 ±175° (Optional ±360°)" | [M?] fairino.us only (Fairino's US site). Not found in the Fairino manual pages read (ND there). Modelled as `fr5_j6` |
| Joint speeds | 180°/s all joints. The URDF says 3.15 rad/s J1–J3 and 3.2 rad/s J4–J6 (180.5 / 183.3°/s); the lower datasheet value is used | [M] |
| Acceleration | MoveIt `joint_limits.yaml` 0.7 rad/s² is a "downscaled for beginners" planner default, not a robot limit. The manual's load curves are measured at 360°/s², the project's assumed `AMAX` | [M] manual 3.4.5.1 |
| TCP speed | max 1 m/s (UR5e 4 m/s). R19 measured the stir grip point at 0.54–0.88 m/s and hub free moves at up to 0.91 m/s, so these are inside but close. **Not checked by any script.** | [M] |
| Masses | 4.64 / 10.08 / 2.71 / 1.56 / 1.56 / 0.36 kg (arm 22.5 kg in the sim; UR5e model 21.0) | [M] DH table |
| CoMs | DH table. **The URDF carries the same numbers but in the DH frames, not its link frames** (e.g. the upper-arm CoM x = +0.212 lies outside its own mesh). They are moved into the link frames here | [M] + [E] transform |
| Inertia | URDF values, assumed to be in the same DH frames and rotated with them (dynamics only; the static checks use masses and CoMs) | [E] |
| Collision | Cylinders for the joint housings, capsules for the tubes and webs. Each **encloses every vertex and every sampled triangle point of the vendor STL** (about 90–107 k points per link, 0 outside). Radii end up 0–6 mm above the nominal profile radii read off the STL. The base is the vendor STL itself (a mesh, as the UR5e base) | [E] from [M] meshes |
| Payload | 5 kg rated **at ≤ 300 mm CoG offset from the flange centre** ("full performance", blue curve); 7 kg max only in the extended region | [M] manual 3.4.5.2.5, Fig. 3.4-19 (installation.html) |
| Mounting | "Mounting: Any orientation". The controller has a "free installation" page with **Base Rotation / Base Tilt** settings for non-floor mounts. The base must carry ≥ 5× the robot weight and ≥ 10× the J1 torque, rigid and non-resonant. **The beam's stiffness is not checked (ND).** | [M] fairino.us; [M] manual safety.html and installation.html 3.4.1 |
| Brakes | Cat 0/1 stops: "the body power is cut off, the joints execute a safe brake, and position holding is monitored" (SF01/SF02). SF25 monitors the position during brake engagement. Power-loss **holding at rated load in a 20° tilted mount: ND** | [M] safety.html. The DECISIONS 2026-10-08 brake rule asks for this document; it is still open |

### CS66 (`r19/arm_cs66.json`, `r19arm_fit.py cs66`)

The vendor files are saved as data in `sim/vendor_r19/elite/`:
- `default_kinematics.yaml`, `physical_parameters.yaml`, `joint_limits.yaml`;
- `cs_macro.xacro`;
- the 7 collision STLs;
- source: EliteRobots/Elite_Robots_CS_ROS2_Description, branch humble.

| Item | Value | Label |
|---|---|---|
| Frames | The URDF chain equals the UR-convention DH exactly (checked numerically). The base frame is base_link; the wrist3 frame is the flange | [M] |
| d6 | **0.095** in `default_kinematics.yaml` (used by the URDF) vs **0.092** in `physical_parameters.yaml`. 0.095 is used | [M], conflicting |
| Limits | ±360° on every joint except the elbow ±180° (URDF). The datasheet says J1–J6 ±360°; the stricter URDF elbow is used | [M] |
| Speeds | **Datasheet: J1–J2 150, J3 180, J4–J6 230°/s. URDF: 180 all.** The lower value per joint is used: 150/150/180/180/180/180 | [M] CS66 datasheet (Neobotix PDF; values matched to labels by their position on the page) |
| Masses, CoG | `physical_parameters.yaml` (link frames). The vendor notes the base values "might be incorrect" | [M] |
| Inertia | The yaml products look like they are about the link origin (≈ m·x·z). They are moved to the CoG by the parallel-axis theorem (dynamics only) | [E] |
| Payload | 6 kg rated [M]. **Allowed CoG offset: ND** (no CS66 payload diagram found). **0.15 m assumed** [E]: it is below the FR5's published 0.30 m and the UR5e file's 0.35 m, so the wrist envelopes are on the strict side | [E] |
| Mounting | "Any angle" [M datasheet]. Brakes: ND (not in the datasheet) | |

## 3. What changed in the code

### New files
- **`arms.py`**: the arm registry and `swap()`.
  - It replaces the UR5e bodies under `R_mount` with the chosen arm, keeping the same body, joint and site names (`R_arm_*`, `R_*_joint`, `R_attachment_site` at DH frame 6), so the checker, solver and planner work unchanged.
  - It moves the gripper (`R_tool`, with everything the scene put on it) over unchanged, at the same pose relative to DH frame 6. The Menagerie UR5e `R_attachment_site` is DH frame 6; checked: FK equal to the UR DH within 1 mm.
- **`r19arm_fit.py`**: vendor files → `r19/arm_<id>.json`. It checks the joint frames against the DH data, transforms the CoMs and fits the enclosing cylinders and capsules.
- **`r19stir_save.py`**: the state-saving copy of `r15stirwalk2.py`. Same method, checks and timing. It stores the passing cycle's states, unwrapped, in `results/r19/stir/`; `results/r15` is never written.
- **Envelopes**: `assets/envelope_fr5_-20.json`, `envelope_fr5_j6_-20.json`, `envelope_cs66_-20.json`.
- **Vendor data**: `sim/vendor_r19/{fairino,elite}/`.

### Hooks in existing files
Every modified file has a `<file>.bak_r19arm` backup. The default arm changes nothing.

| File | Change |
|---|---|
| `scene.py` | at the end of `build()`: `arms.swap(...)` if the arm is not the UR5e |
| `checker.py` | the envelope file from `arms.envelope_file(tilt, arm)` (UR5e: `assets/envelope_<tilt>.json` as before); the flange-CoM radius limit from the arm (UR5e 0.35 as before) |
| `envelope.py` | payload and CoM radius from the arm; output `arms.envelope_file` (UR5e: same file name and values) |
| `r17chain.py` | `QW = min(60, slowest joint of the arm)` (60 for all three arms); the R16 walk start (UR5e joint values) is used only for the UR5e; `arm` key in the result; `_<id>` file suffix |
| `r15stirwalk2.py` | per-joint speed limits `VJ` for the working-part slowdown and the return trapezoids (identical to `VMAX` = 180 when all joints are equal); `_<id>` suffix |
| `r15reach.py` | `_<id>` suffix |
| `r19hub.py` | `QW` as in r17chain; reads `chain_*_<id>.json`; writes `results/r19/hub_<id>/`; prints `ARM=` in its command list |

## 4. Design choices for the FR5 (made once, before any FR5 run)
- **Why they are needed:** FR5 J1 and J6 stop at ±175°, so each has a 10° dead zone. How the base is bolted to the beam (yaw) and how the gripper adapter is clocked on the flange decide where those dead zones lie.
- **Rule:** put each dead zone in the largest sector that the checked UR5e chains never use (wok, plate 2, lever, lid, spider, spatula, approaches included). This is chosen from the UR5e data only.

| Joint | Unused UR5e sector | Choice |
|---|---|---|
| J1 | 209–305°, 96° wide (the other gap is 0–92°) | base turned **77°** in the mount, so the FR5 dead zone ≡ UR J1 257° |
| J6 | the only gap: 260–280°, 20° wide | gripper turned **90°** on the flange, so the dead zone ≡ UR J6 270° |

- **Check:** with q_FR5 = q_UR − (77°, 0, 0, 0, 0, 90°), the tool orientation is identical (0.00°) and the TCP differs by 34 mm (link lengths).
- **The J6 margin is thin** (±5° around the dead zone). `fr5_j6` removes it.
- **J2 and J4** (+85/−265°) cannot be moved by any mounting choice.
- **CS66:** no choice needed (±360°); base yaw and clocking are 0, as on the UR5e.

## 5. Rated-payload torque envelopes (tilt −20°)

The DECISIONS 2026-10-08 rule, `envelope.py`: the tool is removed, the rated payload sits at the allowed CoM offset, and the result is maximised over the arm's own joint ranges.

| N·m | J1 | J2 | J3 | J4 | J5 | J6 | Payload |
|---|---|---|---|---|---|---|---|
| UR5e (existing) | 41.1 | 117.7 | 58.9 | 25.2 | 22.2 | 17.2 | 5 kg @ 0.35 m |
| **FR5** (= `fr5_j6`) | 45.6 | 131.4 | 63.8 | **23.7** | **20.1** | **14.7** | 5 kg @ 0.30 m [M] |
| CS66 | 44.2 | 126.4 | 60.8 | 18.3 | 14.8 | 8.8 | 6 kg @ 0.15 m [E] |

- The FR5 wrist envelopes are 6–14 % below the UR5e's. The same held wok therefore gives higher wrist ratios than the UR5e's 0.629; the wok lane will tell.
- The URDF "effort" values (150 / 28 N·m) are not a published rated output torque, so they are not used (ND as a rating).

## 6. Smoke tests (each < 5 min, run here)

### FR5, faucet lever: PASS
- Command: `ACT=lever SIGN=1 SPX=1.52 SPY=.36 TAG=final ARM=fr5`.
- Result: 3.6 s, min reserve 4.0 mm (UR5e 6.0), both approaches clear (20.0 / 4.0 mm). 5 of 6 IK starts followed.
- Joint margins to the FR5 limits: ≥ 37.9° on every joint; the smallest are J1 37.9° and J4 41.8°.

### FR5, lid: FAIL (with the UR5e final's search effort)
- Command: `TRIES=16`, 192 IK starts per anchor.
- **Lift-off anchor:** 10 collision-free starts.
  - 7 of them sit at the end of the cart travel (x 1.45–1.46) with **J4 exactly at its +85° limit**. Sliding the lid out needs J4 beyond +85°, so the arm loses the pose (rotation error > 3°). FR5 J4 cannot pass +85° (its window is +85/−265°).
  - The 3 others (cart about 1.03): the upper-arm shoulder housing meets the lifted lid, or the J4 housing meets the cart mast.
- **Over-the-rack anchor:** 1 of 192 starts (174 pose failures, i.e. out of reach inside the joint windows; 17 collisions). Its path back toward the carry meet loses the pose.
- **Diagnosis:** the UR5e's own posture, mapped to the FR5 by §4, is reachable and clear at lift-off. At the rack, though, the gripper's OEM housing (the 26.6° angled adapter) sits inside the FR5 wrist-1 housing.
- **What could change it, not tried:**
  - more IK seeds (`SEEDS=3`);
  - a lid rack position the FR5 can reach;
  - a different flange adapter.
- These are re-design steps, not something to do silently.

### FR5, stir
- **Reach:** all 5 stroke starts are reachable with plume-clear candidates: 16/20/16/14/16 of 26/24/32/32/23, best reserve 5.0/3.7/5.0/5.0/4.4 mm, plume clearance 74–94 mm (files `results/r15/reach_stir_h_scrape_dice_i0{00,16,32,48,64}_g0.45_cx.55_r19_fr5.json`).
- **The cycle itself** (`r19stir_save.py`) did not finish its first start within 290 s. It needs a controller lane.

### CS66
- **Lever: pass** (3.5 s, 6.0 mm).
- **Lid: fail.**
  - Lift-off: no IK start (83 collisions, 109 pose).
  - Rack: 15 starts, every path back meets itself (upper-arm web vs wrist-1 housing) or the spider block.

### Random-pose self-collision (non-adjacent links, 2000 poses)

| Arm | Poses with a self-collision |
|---|---|
| UR5e | 22 % |
| FR5 | 45 % |
| CS66 | 55 % |

- No pair of FR5 or CS66 parts touches in every pose; this was checked after replacing the housing capsules with cylinders (§7).
- The extra hits are mostly the gripper's OEM housing against the wrist-1 housing.
- **Fairness caveat:** the vendor arms are enclosed **conservatively** (≥ the STL), while the UR5e uses Menagerie's capsules. Those are approximations, not checked enclosures of the real UR5e. Part of the difference may therefore be modelling, not hardware.

## 7. Notes and known issues
- **Capsules vs cylinders.**
  - A capsule ending at a housing face sticks out up to its radius (4–6 cm) beyond every exposed face. In the first FR5 model this put the shoulder housing into the hood at the lid lift-off. So the housings are now cylinders.
  - Measured in this MuJoCo 3.2.5 against an exact optimiser (30 random cylinder–box pairs at 0.5–9 mm): `contact.dist` = **0.68–1.00 ×** the true gap, never larger.
  - Cylinders are therefore conservative in the fast check (possible false hits at true gaps of about 10–15 mm, never a false pass). The full `distance.py` bound treats them exactly.
  - The UR5e model already uses one cylinder (wrist 3). Capsule–box is exact (1.000).
- **Unchanged and still open (all arms):**
  - the held-part box bug in `scene.build` (conservative false hits);
  - r17chain steps coarser than the 4 mm rule (R19);
  - the stored `play` arrays still contain 2π label jumps (the hub's `unwrapped()` and `r19stir_save.py` unwrap; r17chain's own output is not changed).
- **Checker payload limit:** it keeps `total ≤ 5 kg`, which is stricter than the CS66's 6 kg.
- **Cart:** the arm masses (FR5 22.5 kg, CS66 19.1 kg, UR5e model 21.0 kg) enter the cart tip check automatically.

## 8. Command list for the full re-verification (controller, background, parallel lanes)

Each lane is a chain of commands; most commands take 2–10 min (UR5e: wok 275 s, spider 215 s, spatula 433 s). Options are those of the UR5e results, reconstructed from their files:
- `TRIES` from the logged tries;
- `L2X` and `SINKC` from the keyframes;
- `SPX/SPY` from `tool_xy`.

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A=fr5          # run the same lanes again with A=fr5_j6 (J6 +-360 option) and, optionally, A=cs66
# lane 1: wok plate + sink rinse, then the 2nd plating spot
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 TRIES=8 TAG=final ARM=$A > results/r17/log_wok_final_$A.txt 2>&1
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PX=.17 PLATE2=.43 TRIES=16 TAG=r18plate2b ARM=$A > results/r17/log_wok_plate2b_$A.txt 2>&1
# lane 2: spider, then the lever with the UR5e final's TRIES
$PY r17chain.py ACT=spider SIGN=1 SPX=1.52 SPY=.36 TRIES=12 TAG=final ARM=$A > results/r17/log_spider_final_$A.txt 2>&1
$PY r17chain.py ACT=lever SIGN=1 SPX=1.52 SPY=.36 TRIES=8 TAG=final ARM=$A > results/r17/log_lever_final_$A.txt 2>&1
# lane 3: spatula rest -> stroke start, then the lid (failed above with SEEDS=2; one more search effort, same rules)
$PY r17chain.py ACT=spatula SIGN=-1 SPATREST=-1.15,.30 SPATELEV=8 SPATROLL=180 SPX=1.52 SPY=.36 TRIES=16 TAG=r18roll-1.15_.30 ARM=$A > results/r17/log_spatula_$A.txt 2>&1
$PY r17chain.py ACT=lid SIGN=-1 SPX=1.52 SPY=.36 TRIES=16 SEEDS=3 TAG=final_s3 ARM=$A > results/r17/log_lid_s3_$A.txt 2>&1
# lane 4: stir (reach probes: already on disk for fr5; for fr5_j6/cs66 run them first), then the cycle with stored states
for i in 0 16 32 48 64; do [ -e results/r15/reach_stir_h_scrape_dice_i$(printf %03d $i)_g0.45_cx.55_r19_$A.json ] || $PY r15reach.py stir KEYS=results/r15/stir_h_scrape_dice_keys.json I=$i CARTX=.55 GRIP=.45 TAG=r19 ARM=$A; done > results/r19/log_stirreach_$A.txt 2>&1
$PY r19stir_save.py KEYS=results/r15/stir_h_scrape_dice_keys.json "REACH=results/r15/reach_stir_h_scrape_dice_i{i:03d}_g0.45_cx.55_r19_$A.json" GRIP=.45 SCENE=r17 ARM=$A > results/r19/log_stir_$A.txt 2>&1
# lane 5 (UR5e baseline, store the stir states that were never saved; new files only, results/r15 originals untouched)
for i in 0 16 32 48 64; do $PY r15reach.py stir KEYS=results/r15/stir_h_scrape_dice_keys.json I=$i CARTX=.55 GRIP=.45 TAG=r19; done > results/r19/log_stirreach_ur5e.txt 2>&1
$PY r19stir_save.py KEYS=results/r15/stir_h_scrape_dice_keys.json "REACH=results/r15/reach_stir_h_scrape_dice_i{i:03d}_g0.45_cx.55_r19.json" GRIP=.45 SCENE=r17 > results/r19/log_stir_ur5e.txt 2>&1
#   expected: results/r19/stir/stirwalk2_h_scrape_dice_r17.json with period 2.63 s as in R18b

# hub roadmap: ONLY after lanes 1-3 give ok chains for every action (r19hub.py needs all six chain_*_$A.json;
# with the lid still failing it stops at 'endpoints')
mkdir -p results/r19/hub_$A
$PY r19hub.py endpoints ARM=$A > results/r19/hub_$A/log_endpoints.txt 2>&1
$PY r19hub.py tuck ELBOW=neg ARM=$A > results/r19/hub_$A/log_tuck_neg.txt 2>&1      # about 70 s each (UR5e)
$PY r19hub.py tuck ELBOW=pos ARM=$A > results/r19/hub_$A/log_tuck_pos.txt 2>&1
$PY r19hub.py hubs TUCK=neg ARM=$A > results/r19/hub_$A/log_hubs.txt 2>&1          # choose neg/pos as in R19_HUB.md
# the 22 edges in 4 lanes (2-7 min each, as in R19_HUB.md 6), every command with ARM=$A:
for e in "SPAT LEV_C" "SPAT H_SPAT" "LID_RACK H_WOK" "WOK H_SINK" "SPAT H_SINK"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
for e in "LEV_O WOK" "LEV_O H_SINK" "SPIDER H_WOK" "WOK H_POT" "LEV_O H_SPAT"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
for e in "LID_RACK H_POT" "LEV_C H_SINK" "LID_POT H_WOK" "LEV_C H_SPAT" "WOK H_WOK"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
for e in "SPIDER H_POT" "LID_POT H_POT" "LEV_C H_WOK" "LEV_O H_WOK" "H_SPAT H_SINK" "H_SINK H_WOK" "H_WOK H_POT"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
$PY r19hub.py graph ARM=$A ; $PY r19hub.py commands ARM=$A
```

**Reading the results.** Each FR5 action passes if its `chain_*_fr5.json` says `"ok": true`. Compare with the UR5e: time, `min_reserve_mm`, `max_joint_ratio` (≤ 1 against the FR5 envelope), `max_pgc_moment_Nm` (≤ 7).

For the stir:
- the period and the plume;
- `working_part_joint_speed_max_degps` against 180°/s;
- the grip-point speed against the FR5's 1 m/s TCP limit, which is not checked automatically.

**Smaller UR5e regressions.** The lever regression run here (`TAG=regress_r19arm`) is the UR5e check. The UR5e envelope was not re-run, because that would overwrite `assets/envelope_-20.json`; the code path gives the same numbers by construction.

## 9. Like-for-like round under the true-geometry standard (2026-10-13, #2 after #12)

**What changed in the standard.** DECISIONS 2026-10-13, "True arm geometry is the checking standard":
- The UR5e baseline is now `ur5e_enc2_pgc`: enclosing hulls, plus the PGC-140 housing from DH's drawing (Ø75 body) instead of the 75 × 75 × 138.5 mm box.
- The plating spot is at y 0.15 (`PY=.15`).
- All six UR5e chains pass, and the hub is 22 / 22.

**The FR5 runs in §6/§8 were not like-for-like:** they used the box gripper and the old plate y. The FR5 model itself (vendor-mesh enclosing cylinders and capsules) already met the standard.

### 9.1 New arm options (`arms.py`; backup `arms.py.bak_r19arm2`)

| id | Arm | Gripper |
|---|---|---|
| `fr5_pgc`, `fr5_j6_pgc`, `cs66_pgc` | `fr5` / `fr5_j6` / `cs66` (same limits, speeds, torque envelope) | the DH-drawing PGC housing (`scene.oem_pgc_drawing`), as `ur5e_enc2_pgc` |
| `fr5_pgc_sp20`, `fr5_j6_pgc_sp20` | as above | **design proposal [E]:** the same gripper on a flange adapter 20 mm longer along the flange axis. The adapter's own mass is not modelled; the tool CoM moves 20 mm out with it |

- Defaults are unchanged. The UR5e lever regression is identical again (`chain_lever_s+1_regress_r19arm2.json`: every key, `play` diff 0.0).
- `cs66_pgc` was not run.

### 9.2 Smoke runs, each under 5 min (`ARM=fr5_j6_pgc PY=.15`)

`PY` only moves the wok's plating spot in `r17chain.py`. For the lever, spider, lid and spatula it changes nothing, exactly as for the UR5e adoption.

| Chain | Result |
|---|---|
| **Lever** (`TRIES=8`) | **pass**: 3.7 s, r17chain reserve 6.0 mm. ≤ 4 mm re-check (`r19enc_check.py`): 141 states, 0 hits, env 2.19 mm, self 2.02 mm. Approaches 0 hits. Certified (`r19enc_adopt.py`) → `chain_lever_s+1_final_fr5_j6_pgc.json` |
| **Spider**, re-plan (`TRIES=12`) | **not finished in 296 s.** The new gripper changes the search path: at "over the plate" the first candidates fail on the wrist-1 housing vs the gripper housing at the 110° tip |
| **Spider**, the stored `fr5_j6` box-gripper chain re-checked with `fr5_j6_pgc` | **pass**: 5,490 states at ≤ 4 mm, 0 hits, env 2.02 mm, self 2.0 mm. Approaches 68 + 68 states, 0 hits. 53.3 s, joint ratio 0.438. Certified → `chain_spider_s+1_final_fr5_j6_pgc.json` |

The PGC housing lies inside the box, so the box's passing paths can only gain clearance.

Further certificates from stored FR5 chains (≤ 4 mm play + approaches, 0 hits):

| Chain | Arms | ≤ 4 mm play | Reserves |
|---|---|---|---|
| spatula (from `fr5`) | `fr5_pgc`, `fr5_j6_pgc` | 2,429 states | env 2.0 mm, self 2.0 mm |
| lever (from `fr5`) | `fr5_pgc` | 136 states | env 3.99 mm |

**Like-for-like standing:**

| Chain | `fr5_pgc` | `fr5_j6_pgc` |
|---|---|---|
| lever | ✓ | ✓ |
| spatula | ✓ | ✓ |
| spider | re-plan needed (the stock-J6 `fr5` spider failed) | ✓ |
| wok, plate 2, lid | lanes below | lanes below |

### 9.3 What the earlier FR5 failures were blocked on

Two new diagnostic tools (they diagnose; they neither plan nor check):
- **`r19arm_diag.py`** re-runs r17chain's own 96-start anchor solve on model variants. It also maps the UR5e's checked anchor state through the 77° / 90° offsets and solves it exactly on the FR5.
- **`r19arm_pathdiag.py`** makes the FR5 follow the UR5e's whole checked TCP path by IK continuation. It uses the fast check at every state and the full check at every 10th.

Results: `results/r19/armswap/`.

**Wok "lifted" (and "lowered" / set down), `fr5_pgc`, `PY=.15`:**
- The random-start solver gives **0 starts in every variant**:
  - stock;
  - J4 window opened to ±360°;
  - J2 and J4 opened;
  - base rotation 0 instead of 77°;
  - box gripper.

  So the anchor is blocked by none of the joint windows, the base rotation or the gripper box.
- **The UR5e's own posture, mapped to the FR5, lies inside every FR5 window.** Its only conflict is the **FR5 upper-arm elbow housing over the plate**: true gap 0.9 mm, 10 required. With the plate at y 0.17 the same state is clear (min 2.7 mm, camera vs wrist 2).
- **Along the whole UR5e wok path** (470 states, `fr5_j6_pgc`), no joint window is left. The hits are:
  - elbow vs plate: 40 states (pick and set-down);
  - elbow vs sink front rim: 39;
  - wrist-1 housing vs gripper housing: 22 (tip, empty).

| Variant on the UR5e wok path | Hit states |
|---|---|
| none | 90 |
| `PY=.17` | 50 (the plate pair is gone) |
| 20 mm adapter | 11 |
| 20 mm adapter + `PY=.17` | **3** (elbow vs sink front rim, states 92–94) |

- **"Over the plate" and "under the tap":** the mapped UR5e states are valid on the FR5 (in every window, 0 hits). The random-start solver simply does not land in that branch (0 and 6 starts).
- **One margin to watch:** in the UR5e branch, J6 under the tap is 173.9° against the stock 175° limit. Use the J6 option.

**Lid:**
- **Not J4.** The +85° stop only appears in random-start candidates parked at the end of the cart travel. Along the UR5e lid path, no FR5 window is left.
- **Not the 77° base rotation.**
- **What blocks it:**
  - the wrist-1 housing vs the gripper housing during the slide-out and the 90° roll (43 of 205 states);
  - the upper-arm shoulder housing vs the spider-rest block near the rack (6 states).
- **Effect of the adapter:**
  - a 20 mm adapter removes the self pair along the whole path (4 spider-block states left; 60 mm leaves none);
  - a re-plan with UR5e seeds and the 20 mm adapter (`fr5_j6_pgc_sp20`): the lift-off side now follows to the carry meet. At the rack, 15 of 16 candidates meet the spider block.

**Stir (box-gripper run by the controller, `stirwalk2_h_scrape_dice_r17_fr5.json`):**
- Strokes 0–3 pass.
- The straight joint-space return into stroke 4 puts the spatula blade into the wok wall at 12 % of the move. It is the same in all 8 starts.
- This does not depend on the gripper. It needs more stroke-4 start candidates or a via on that return; open.

**Smallest changes, in order (none tried as the adopted design):**
1. **Search, not geometry:** seed each anchor with the UR5e's checked states mapped through the arm's offsets (`r17chain.py SEEDUR=<UR5e chain>`, below). This is what the random-start solver misses for the wok's "over the plate" and "under the tap" and the lid's lift-off.
2. **Gripper adapter +20 mm** along the flange axis (`*_pgc_sp20`): removes the FR5 wrist-1 vs gripper-housing pair on the wok and lid paths. The payload CoM moves out by 20 mm, and the adapter's mass must be added before adoption.
3. **Plating spot y 0.15 → 0.17:** removes the elbow vs plate pair at the wok pick.
4. **Lid only:** the spider rest moves a few cm away from the lid rack (not tested), or a 60 mm adapter.
5. **Not needed:** a different base rotation or a J4 offset. The windows never bind on the UR5e's branches. (The J6 ±360° option still removes the thin J6 margin.)

### 9.4 Code this round
- **Backups `*.bak_r19arm2`:**
  - `arms.py`: the options in §9.1;
  - `r17chain.py`: `SEEDUR=<chain json>`. Extra IK starts from that chain's states, mapped by `q1 − mount yaw`, `q6 − clocking`; each is re-solved exactly at the anchor (≤ 0.5 mm / 0.2°) and **fully checked like a solver candidate**. They go first, like the R16 walk. Default off; the result stores `seed_ur`;
  - `r19enc_check.py`: a non-UR `NEW=` writes to `results/r19/<arm>/` and is checked on that arm only; `SET=stir` takes `SUFFIX`;
  - `r19enc_adopt.py`: `SRCSFX=` adopts a stored chain of another arm option.
- **New:** `r19arm_diag.py`, `r19arm_pathdiag.py`.
- **Outputs:**
  - `results/r19/armswap/`;
  - `results/r19/fr5_pgc/`, `results/r19/fr5_j6_pgc/`;
  - `results/r17/chain_*_fr5_pgc.json`, `chain_*_fr5_j6_pgc.json` (certified);
  - `chain_lid_s-1_final_seedur_fr5_j6_pgc[_sp20].json` (exploratory, failed).

### 9.5 Controller lanes (background; `A=fr5_pgc`, then the same with `A=fr5_j6_pgc`)

Each lane is a chain of commands. The re-plans use more search than the UR5e finals (`SEEDS=3` and the UR5e seeds); the rules are unchanged. Every chain that ends `"ok": true` is then re-checked at ≤ 4 mm and certified, approaches included.

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A=fr5_pgc; U=results/r17   # UR5e seeds: the adopted ur5e_enc2_pgc chains
# lane 1: wok, then plate 2 (layout PY=.15)
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PY=.15 TRIES=16 SEEDS=3 SEEDUR=$U/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json TAG=final_py.15 ARM=$A > $U/log_wok_final_py.15_$A.txt 2>&1
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PX=.17 PLATE2=.43 PY=.15 TRIES=16 SEEDS=3 SEEDUR=$U/chain_wok_s-1_r18plate2b_py.15_ur5e_enc2_pgc.json TAG=r18plate2b_py.15 ARM=$A > $U/log_wok_plate2b_py.15_$A.txt 2>&1
# lane 2: lid; spider (fr5_pgc only: fr5_j6_pgc's spider is certified); lever/spatula are certified for both
$PY r17chain.py ACT=lid SIGN=-1 SPX=1.52 SPY=.36 TRIES=16 SEEDS=3 SEEDUR=$U/chain_lid_s-1_final_ur5e_enc2_pgc.json TAG=final ARM=$A > $U/log_lid_final_$A.txt 2>&1
[ $A = fr5_pgc ] && $PY r17chain.py ACT=spider SIGN=1 SPX=1.52 SPY=.36 TRIES=12 SEEDS=3 SEEDUR=$U/chain_spider_s+1_final_ur5e_enc2_pgc.json TAG=final ARM=$A > $U/log_spider_final_$A.txt 2>&1
# lane 3: stir with the PGC housing: reach probes, then the cycle with stored states
for i in 0 16 32 48 64; do $PY r15reach.py stir KEYS=results/r15/stir_h_scrape_dice_keys.json I=$i CARTX=.55 GRIP=.45 TAG=r19 ARM=$A; done > results/r19/log_stirreach_$A.txt 2>&1
$PY r19stir_save.py KEYS=results/r15/stir_h_scrape_dice_keys.json "REACH=results/r15/reach_stir_h_scrape_dice_i{i:03d}_g0.45_cx.55_r19_$A.json" GRIP=.45 SCENE=r17 ARM=$A > results/r19/log_stir_$A.txt 2>&1
# lane 4 (after lanes 1-3): <= 4 mm re-checks + certificates (a failed chain is skipped by the re-check and refused by the adopter)
for S in wok wok_plate2b; do $PY r19enc_check.py recheck SET=$S SUFFIX=_py.15_$A NEW=$A PY=.15; $PY r19enc_adopt.py ARM=$A SETS=$S SRCSFX=_py.15_$A PY=.15; done
for S in lid spider; do $PY r19enc_check.py recheck SET=$S SUFFIX=_$A NEW=$A; $PY r19enc_adopt.py ARM=$A SETS=$S SRCSFX=_$A; done
$PY r19enc_check.py recheck SET=stir SUFFIX=_$A NEW=$A
# lane 5 (only when all six chain_*_$A.json are ok): the hub, as R19_UR5E_ENC.md 8.6 lane A with L="ARM=$A PY=.15"
L="ARM=$A PY=.15"; D=results/r19/hub_py.15_$A; mkdir -p $D
$PY r19hub.py endpoints $L > $D/log_endpoints.txt 2>&1; $PY r19hub.py tuck ELBOW=neg $L > $D/log_tuck_neg.txt 2>&1; $PY r19hub.py tuck ELBOW=pos $L > $D/log_tuck_pos.txt 2>&1; $PY r19hub.py hubs TUCK=neg $L > $D/log_hubs.txt 2>&1
#   then the 22 edges in 4 lanes exactly as R19_UR5E_ENC.md 8.6 (each command with $L), then: $PY r19hub.py graph $L
# design-proposal lane (E): the 20 mm adapter with the plate at y .17, J6 option
B=fr5_j6_pgc_sp20
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PY=.17 TRIES=16 SEEDS=3 SEEDUR=$U/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json TAG=final_py.17 ARM=$B > $U/log_wok_final_py.17_$B.txt 2>&1
$PY r17chain.py ACT=lid SIGN=-1 SPX=1.52 SPY=.36 TRIES=16 SEEDS=3 SEEDUR=$U/chain_lid_s-1_final_ur5e_enc2_pgc.json TAG=final ARM=$B > $U/log_lid_final_$B.txt 2>&1
```

**How to read it:**
- The FR5 passes like-for-like when, for one arm id, all six `chain_*` are `"ok": true` with an `adopted` certificate (≤ 4 mm play and approaches, 0 hits), the stir certificate is clean, and the hub is 22 / 22.
- If the `fr5_pgc` / `fr5_j6_pgc` wok or lid lanes still fail on the pairs in §9.3, the proposal lane shows whether the 20 mm adapter and the plate at y 0.17 are enough. The lid also needs the spider rest moved.
