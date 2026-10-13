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
