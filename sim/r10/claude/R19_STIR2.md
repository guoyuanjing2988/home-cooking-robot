# R19 stir 2: spatula hand-off, stir physics at the stored timing, sourced limits (2026-10-13, GitHub #40, follows #3)

Labels: **[M]** measured in the sim, **[E]** estimate or assumption, **[S]** sourced (URL given).
Checking standard: `ARM=ur5e_enc2_pgc PY=.15`, plus `ARM=fr5_j6_pgc_sp20`. Gates unchanged:
- 10 mm robot↔environment, 5 mm gripper/held↔environment;
- states ≤ 4 mm apart;
- plume: arm ≥ 0.20 m from the wok axis.

No gate, force or limit was loosened. No git, no downloads.

> **Incident (needs your action, §6).** I deleted the #3 FR5 library entry `results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20.json` by mistake: a `rm` glob for my own `_j<jerk>` files also matched `_j6`.
> - A copy exists in the home-cooking-robot snapshot. It is verified identical: same size, the embedded geometry/states md5 match the certificate, and its numbers equal `cycle_fr5_j6_pgc_sp20/cycle.json` and `summary.json`.
> - My restore was refused by the permission system. Lane 0 in §5 restores it.
> - All FR5 results below were computed **before** the deletion, except the FR5 retimed library entries, which wait for the restore.

## Answer first

| Gap | Answer |
|---|---|
| 1. Spatula hand-off | **Closed for both arms.** The join holds the spatula blade still at the stroke-0 start while the cart slides and the arm re-configures (a tool-fixed self-motion). It reaches `H_stir0` exactly. Certified at ≤ 4 mm: **0 hits** in the stir scene and in the current layout (`PY=.15` + pot-zone layer). Exit = the same path reversed. |
| 2. Stir physics at the stored timing | **Re-run with R15's metric, full 12 s, both arms.** The R15 bench is reproduced bit for bit. Mixing at the arm timing is within R15's own seed spread. Rare spatula load spikes are larger. |
| 3. Limits | **No OEM hard limit exists for joint acceleration or jerk on either arm** [S]. Retimed under three jerk limits. **At the conservative sourced value, 1,000 °/s³ (Fairino SDK default): 4.84 s per stroke (UR5e) and 4.35 s (FR5)**, against 2.32 / 2.29 s stored. |

Key numbers:

| | UR5e `ur5e_enc2_pgc` | FR5 `fr5_j6_pgc_sp20` |
|---|---|---|
| Join: cart move, largest joint change | 77.6 mm, 12.5° (J2) [M] | 142.6 mm, 20.5° (J2) [M] |
| Join: states, hits (stir scene / current layout) | 106, 0 / 0 [M] | 189, 0 / 0 [M] |
| Join: min reserve, held / self / robot–env; plume | 5.71 / 10.32 / 96.8 mm; 94.0 mm [M] | 5.71 / 2.01 / 53.4 mm; 94.0 mm [M] |
| Join time, rest to rest (cart 0.5 / 0.15 m/s²) | 1.28 / 1.93 s [M] | 1.64 / 2.52 s [M] |
| Hot share r 0.09 m / never-hot pieces (R15 bench: 0.448 / 15) | 0.435 / 14 [M] | 0.425 / 14 [M] |
| Period per stroke at jerk ≤ 57,296 / 8,000 / 1,000 °/s³ | 2.322 / 2.788 / **4.842 s** [M] | 2.286 / 2.613 / **4.353 s** [M]\* |

\* FR5 values come from laws solved without the 1 % jerk margin used for the UR5e (§3). Lane 1 recomputes them and writes their entries.

## 1. The spatula hand-off (gap 1)

### 1.1 The two ends and their joint labels

**SPATULA_FETCH end:** the adopted chain's last play state, `stroke start#5`.
- UR5e: `results/r17/chain_spatula_s-1_r18roll-1.15_.30_ur5e_enc2_pgc.json`.
- FR5: `…_fr5_j6_pgc_sp20.json` (the #2 sp20 chain, adopted).
- Labels are the ones a controller runs:
  - The play is unwrapped as `r19hub.unwrapped()`. The stored UR5e play jumps +2π in J2 at the lane join, row 132.
  - The UR5e then takes the hub roadmap's spatula shift, pan −1 turn (`results/r19/hub_py.15_ur5e_enc2_pgc/hubs.json`).
  - The FR5 has no roadmap; its play has no jumps.

**H_stir0** of the stored cycle, with one 2π relabel of the **whole** cycle, the one nearest the spatula end:
- UR5e: **J2 −1 turn**. This is the "shoulder lift −2π" that R19_HUB.md flagged as unverified.
- FR5: **J6 −1 turn**.
- Every certified cycle state, and the geometry on a dense grid, stays in range after the relabel [M]:
  - UR5e cycle J2: −113.2° … −46.3°;
  - FR5 cycle J6: −158.2° … −101.4°.
- A relabel is the same pose, so the cycle's certificate is unchanged.
- **The J1 2π difference in R19_STIR §5 disappears once the roadmap's pan shift is used.** Relabelling the cycle in J1 instead would put it 2.5° out of range.

**Does the spatula chain end moving? No.** r17chain ends every action at rest, and R19_SMOOTH times the spatula chain rest to rest per piece. So the join is timed from rest. The cycle is entered from rest at `H_stir0`, as its library entry already states. That entry ramp costs +0.305 s (UR5e) / +0.249 s (FR5) per start-and-stop [M, from the stored three-cycles-from-rest law].

**Both ends hold the tool at the same pose** (difference 3·10⁻⁵ mm). Only the cart and the posture differ:
- UR5e: cart +77.6 mm; joints −0.86 / +12.50 / −7.76 / −5.08 / −0.02 / −0.93°.
- FR5: cart +142.6 mm; joints −3.70 / +20.52 / −14.41 / −7.53 / −0.24 / −3.95°.

### 1.2 Geometry: the tool-fixed self-motion
- **Method:** the cart is stepped in 1 mm steps from the spatula end to 0.55 m. The 6 joints are solved at each step for the unchanged tool pose (least squares from the previous step).
  - The spatula blade stays still, 1 cm off the steel at the stroke-0 start, while the cart slides.
  - Both arms arrive on `H_stir0`'s own IK branch, within 3·10⁻⁵° (UR5e) and 1·10⁻⁷° (FR5) [M].
- **Stored form:** an interpolating quintic B-spline over (cart, q1..q6), parameter = cart travel. Its tool drift is ≤ 3·10⁻⁵ mm / 3·10⁻⁵° [M].
- **Compared with the plain straight (cart, joint) line:** the line also passes (0 hits), but it moves the tool by 2.3 mm (UR5e) / 6.9 mm (FR5). Its blade reserve drops to 2.0 mm, against 5.7 mm for the self-motion [M]. It is not stored.

### 1.3 Certificate (`results/r19/stir/join_<arm>/join.json`)

Method:
- The spline is cut at ≤ 4 mm by the point bound, cart included (max 3.998 / 3.999 mm).
- Every state goes through `Checker.check(full=True)`, with hit pairs classed by `r19enc_check.one`, in two scenes:
  - **stir:** the scene the cycle is certified in (`r19stir_cycle.model`), with the plume rule;
  - **std:** the current layout. This is the spatula chain's own R18b scene with the held `spatula_b`, the plating spot at y 0.15, and the pot-zone layer (keyed rack: 7 geoms confirmed; spider rest at (1.56, 0.20); `R19_POTZONE.md` §5–6). The plume rule applies here too.

| | UR5e stir | UR5e std | FR5 stir | FR5 std |
|---|---|---|---|---|
| States / hits / out of range | 106 / 0 / 0 | 106 / 0 / 0 | 189 / 0 / 0 | 189 / 0 / 0 |
| Held vs environment | 5.71 mm (blade vs wok tile) | 5.71 | 5.71 | 5.71 |
| Self | 10.32 | 10.32 | 2.01 (wrist-1 housing vs wrist-2 J6 housing) | 2.01 |
| Robot vs environment | 96.8 (forearm vs door 1) | 96.8 | 53.4 (elbow housing vs door 1) | 53.4 |
| Plume margin / violations | 94.0 / 0 | 94.0 / 0 | 94.0 / 0 | 94.0 / 0 |

**The stored cycle itself, re-checked in the std scene:**
- UR5e: 4,484 states, 0 hits, reserves 2.0 / 2.0 / 21.6 mm, plume 25.8 mm.
- FR5: 3,973 states, 0 hits, reserves 2.0 / 2.0 / 10.0 mm, plume 25.8 mm.

These are the same as its R17-scene certificate [M], so the plate at y 0.15 and the pot-zone layer change nothing at the wok.

### 1.4 Time law and library entry
- **Method:** rest to rest. TOPP plus filter plus slow-downs (`r19stir2_law.py`) on 7 coordinates.
- **Limits:**
  - joint speed: datasheet;
  - joint acceleration: 800 or 360 °/s²;
  - cart: 0.25 m/s, with 0.5 m/s² (R19_SMOOTH "fastcart", tip-over model) or 0.15 m/s² (`mobile.py` design case);
  - W = 0.2 s, so cart jerk ≤ 5 m/s³ (R19_SMOOTH assumption).
- **Result:** the cart binds; joint acceleration does not (800 and 360 give the same time).
  - UR5e: **1.284 s** (0.5 m/s²) / 1.934 s (0.15 m/s²); peak joints 21 °/s, 52 °/s², 606 °/s³.
  - FR5: **1.640 s** / 2.516 s; peak joints 28 °/s, 57 °/s², 614 °/s³ [M].
  - The R18b estimate was 0.5 s.
- **Exit:** the same path reversed, with the same states and scenes, takes the same time.
- **Library entry:** `results/r19/stir/lib_stir_join_<arm>.json`. It holds:
  - hubs (`H_spat_stroke` and the relabelled `H_stir0`) and the label map;
  - the B-spline;
  - sets `STIR_ENTRY` and `STIR_EXIT`, each with its certified states in order;
  - the time laws (entry law on a 2 ms grid) and the certificate.
- **Chain to run:** SPATULA_FETCH → STIR_ENTRY → STIR_CYCLE (run with the relabel, from rest) → STIR_EXIT → SPATULA_STOW.

## 2. Stir physics at the stored timing (gap 2)

**R15's sim is `stirbench.py`** (MuJoCo 3.2.5, 90 rigid 15 mm dice, 320 g, compliant spatula weld). Its metric is the hot-zone contact share per piece (mean), pieces never hot, longest hot dwell, cold spells, flips, spill and spatula load. The run to compare with is `results/r15/stir_h_scrape_dice.json`, the bench whose keys the arm follows.

**`r19stir2_phys.py`** copies stirbench's model and metrics verbatim and changes only the spatula target:
- **bench:** stirbench's keyframes. **It reproduces R15 exactly:** every metric is identical, and the model XML md5 is the same for all drivers [M].
- **arm:** the stored library geometry and the stored A_UR law, entered from rest.
  - The rebuilt middle period equals the stored one to < 2 ms.
  - The blade pose comes from forward kinematics, mapped through the inverse of `r19stir_cycle.tcp()`.
  - The 1 cm planning lift is removed, so the blade scrapes as in the bench. The arm path is the bench path lifted 1 cm for the collision check.

**Run time.** One full 12 s run takes about 10 min. Each run was split into 3 commands of under 5 min, using an exact MuJoCo state checkpoint. A chunked run equals an unchunked run bit for bit; this was tested [M].

| T = 12 s, seed 1 | R15 bench (stored) | bench re-run | **UR5e arm** | **FR5 arm** |
|---|---|---|---|---|
| Strokes in the window | 5.0 (2.40 s) | 5.0 | 5.11 (2.321 s) | 5.19 (2.286 s) |
| Hot share, mean, r 0.09 / 0.13 m | **0.448 / 0.611** | 0.448 / 0.611 | **0.435 / 0.589** | **0.425 / 0.591** |
| Never hot, r 0.09 / 0.13 (of 90) | **15 / 15** | 15 / 15 | **14 / 14** | **14 / 14** |
| Longest hot dwell | 2.18 s | 2.18 | 2.27 | 2.45 |
| Cold spell, median | 3.10 s | 3.10 | 3.05 | 3.16 |
| Flips per 10 s | 3.19 | 3.19 | 4.06 | 3.47 |
| Spilled | 0 | 0 | 1 | 0 |
| Spatula force, p95 / max | 5.6 / 24.9 N | same | 10.8 / 517 N | 8.8 / 277 N |
| Grip moment, p95 / max (PGC limit 7 N·m) | 2.21 / 9.5 N·m | same | 3.93 / 164 N·m | 3.26 / 92 N·m |
| Samples > 30 N | 0 | 0 | 9 | 16 |
| Blade speed / acceleration, max | 0.53 m/s / 4.3 m/s² | same | 0.77 / 6.7 | 0.78 / 7.0 |

All values [M]. Files: `results/r19/stir/phys/stir2_full_*_s1.json`.

**Mixing.** The hot share is 1–2.3 points lower and there is one fewer never-hot piece. This is within R15's own seed-to-seed spread on the comparable push2 dice runs (seeds 1 / 2 / vid: hot 0.450 / 0.452 / 0.462, never 13 / 13 / 12) [M from R15 files]. With one seed per driver, I call the mixing unchanged [E]. Lane 2 adds seeds 2 and 3.

**Spatula load.**
- **Typical load:** the p95 moment rises from 2.2 to 3.3–3.9 N·m, still under 7 N·m.
- **Rare spikes:** single-sample spikes appear. In R15 these are rigid dice wedging under the blade. Other R15 dice runs reach 442 N·m and 39 jam samples (`f_push2_dice_mu.15`) [M].
- **Where they happen.** From the run checkpoints (up to t = 9.75 s):
  - UR5e: 2 samples > 30 N at mid-scrape of strokes 1 and 2. Its 517 N spike is later and not localized.
  - FR5: 10 samples in strokes 0–1 and near t 8.7 s.
- **What differs kinematically.** Faster air returns: blade 0.64–0.77 m/s, against 0.43–0.53 m/s on the bench. The returns rise to 56–76 mm instead of 77–88 mm. The arrival speed toward the steel is similar: ≤ 0.08 m/s against ≤ 0.09 m/s [M, `phys/diag_*.json`].
- **Consequence:** the force-limited / keyed-block requirement of R15 stands. The spike rate needs the seed lanes.

**New geometric finding [M]:** the UR5e's smoothed stroke 4 puts the **blade edge up to 15.6 mm / 2.5° off the bench path.**
- It stays on the steel (minimum edge gap 0.1 mm, as on the bench), so the offset is along the surface.
- Cause: the R15/R19 pose gate is 5 mm / 3° at the grip, 0.45 m from the edge, so 2.5° there moves the edge about 20 mm.
- FR5: 0.0 mm.

## 3. Limits: sources and the conservative period (gap 3)

**What is sourced** (read-only web research):
- **UR5e acceleration:**
  - The datasheet lists only ±360° and ±180 °/s per joint [S](https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/).
  - UR's own ROS 2 config says *"acceleration limits are not publicly available"* (`has_acceleration_limits: false`) [S](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description/blob/rolling/config/ur5e/joint_limits.yaml).
  - URScript `movej` default is a = 1.4 rad/s² (80 °/s²). It is a default, not a maximum [S](https://www.universal-robots.com/manuals/EN/HTML/SW5_24/Content/prod-scriptmanual/all_scripts/movej_qa14v105t0r.htm).
  - The **800 °/s²** stays UR staff guidance, *"moveJ accelerations should be less than 800deg/sec^2"* [S](https://forum.universal-robots.com/t/maximum-axis-speed-acceleration/13338). Staff in the same thread say the limit depends on payload and pose.
- **UR jerk:** no number is published.
  - Motion version 2 and `optimovej` are *"jerk limited"*, and *"the default jerk depends on the specific pose, payload and acceleration"*.
  - `jerk_gain_scaling_set` scales it by a factor of 0.01–1 only [S](https://www.universal-robots.com/manuals/EN/HTML/SW10_13/Content/prod-scriptmanual/all_scripts/jerk_gain_scaling_set.htm).
- **FR5:**
  - The catalogue gives ±180 °/s and 1 m/s TCP, and no acceleration.
  - The SDK `MoveJ` acceleration parameter is *"not yet available"*.
  - SDK `PtpFIRPlanningStart(double maxAcc, double maxJek = 1000)`: *"Unified joint jerk limit (deg/s3), default 1000"*, example call `(1000, 1000)` [S](https://fairino-doc-en.readthedocs.io/latest/SDKManual/CPPRobotMovement.html).
  - The MoveIt config has 0.7 rad/s², a downscaled planning default [S](https://github.com/FAIR-INNOVATION/frcobot_ros2).
- **References:**
  - MoveIt 2 Ruckig smoothing default: 1,000 rad/s³ = 57,296 °/s³ [S](https://github.com/moveit/moveit2/blob/main/moveit_core/trajectory_processing/src/ruckig_traj_smoothing.cpp).
  - Franka Panda hard limits: 3,750–10,000 rad/s³ and 7.5–20 rad/s², a different arm [S](https://github.com/frankarobotics/libfranka/blob/0.9.2/include/franka/rate_limiting.h).

**Verdict:**
- **800 °/s² is not confirmed as a hardware limit for either arm.**
  - UR5e: it is UR guidance.
  - FR5: it sits below the 1,000 °/s² of Fairino's own SDK example, but it is still an **assumption**.
- **No OEM jerk limit exists.**
  - The stored peaks are ≈ 1,012 rad/s³ (UR5e) and ≈ 570 rad/s³ (FR5). They are near MoveIt's default and 4–10× below Franka's hard limits.
  - They are **33–58× above the only OEM jerk number found (Fairino SDK default 1,000 °/s³)**.

**Retime** (`r19stir2_retime.py`):
- **Method:**
  - Same geometry, states and certificate as #3.
  - TOPP + filter + slow-downs as #3, plus |q⃛| ≤ J on the 2 ms grid.
  - For each J, filter windows W = 0.1–1.6 s were tried, with A = min(800, J·W/2); the fastest converged law is kept.
  - The UR5e laws are solved for 0.99 J. An independent finite-difference re-check of the stored entry (`check`) then stays ≤ J [M].

| Jerk limit | Source | UR5e per stroke (W, A) | FR5 per stroke (W, A) |
|---|---|---|---|
| none (stored #3) | — | 2.321 s | 2.286 s |
| 57,296 °/s³ | MoveIt 2 Ruckig default [S] | 2.322 s (0.1, 800) | 2.286 s (FR5 peak 30.6k: no change)\* |
| 8,000 °/s³ | A / 0.1 s, the R19_SMOOTH rule [E] | 2.788 s (0.1, 400) | 2.613 s (0.2, 800)\* |
| **1,000 °/s³** | **Fairino SDK default, the conservative sourced value [S]** | **4.842 s** (0.2, 100) | **4.353 s** (0.4, 200)\* |

**Independent re-check of the stored UR5e entries** (speed / acceleration / jerk ratios):
- j57296: 0.98 / 0.98 / 0.975;
- j8000: 0.75 / 0.998 / 0.986;
- j1000: 0.38 / 0.993 / 0.992.

Geometry md5 equals the certificate md5 in all three, and ṡ is periodic [M].

**What the conservative period means.** At 1,000 °/s³ the stroke takes about twice as long; 12 s holds about 2.5 strokes instead of 5. The working parts then run at a median 0.46 (UR5e) / 0.54 (FR5) × bench speed, down to 0.17–0.19 near the hand-offs [M]. At 8,000 °/s³ the median is 0.93 / 0.91. So at the conservative value the R15 stir process would change. Lane 3 runs its physics. **The real jerk and acceleration capability must be measured on the arm**, e.g. UR motion version 2 clamps to its hardware limits.

## 4. Checked / not checked
- **Checked [M]:**
  - both joins, every state at ≤ 4 mm, in two scenes, plume included;
  - the cycle relabel ranges;
  - the stored cycles in the current layout;
  - bit-exact R15 reproduction;
  - full 12 s physics for both arms (seed 1);
  - the jerk-limited laws on the 2 ms grid, with an independent re-check (UR5e).
- **Not checked:**
  - seeds 2–3 (lane 2);
  - physics at the jerk-limited timings (lane 3);
  - FR5 retimed entries and the FR5 kinematic diagnostic (lane 1, after lane 0);
  - the cart's own tracking;
  - the adapter mass on `_sp20` (as #3).

## 5. Controller lanes

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
# lane 0 (needs your OK, ~1 s): restore the #3 FR5 entry I deleted by mistake, from the verified snapshot copy
cp -p /c/Users/admin/Documents/YJGames/home-cooking-robot/sim/r10/claude/results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20.json results/r19/stir/
$PY r19stir2_retime.py check FILES=results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20.json   # expect period/stroke 2.2864, geometry_md5 = cert d13de53fac696fe01e3de74f3f463fff
# lane 1 (after lane 0, ~2 min): FR5 jerk-limited laws with the 1 % margin, their library entries, the re-check, the blade diagnostic
$PY r19stir2_retime.py ladder ARMS=fr5_j6_pgc_sp20 FORCE=1 WORKERS=8 > results/r19/stir/retime/log_ladder_fr5.txt 2>&1
F=results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20; $PY r19stir2_retime.py check FILES=$F.json,${F}_j57296.json,${F}_j8000.json,${F}_j1000.json
$PY r19stir2_phys.py DRIVER=arm ARM=fr5_j6_pgc_sp20 DIAG=1 TAG=arm_fr5_j6_pgc_sp20
# lane 2 (~10-12 min per run, run in parallel; FR5 runs after lane 0): seeds 2 and 3, to size the seed spread
D=results/r19/stir/phys
for S in 2 3; do
 $PY r19stir2_phys.py DRIVER=bench SEED=$S TAG=full_bench_s$S > $D/log_bench_s$S.txt 2>&1 &
 $PY r19stir2_phys.py DRIVER=arm ARM=ur5e_enc2_pgc SEED=$S TAG=full_arm_ur5e_enc2_pgc_s$S > $D/log_ur5e_s$S.txt 2>&1 &
 $PY r19stir2_phys.py DRIVER=arm ARM=fr5_j6_pgc_sp20 SEED=$S TAG=full_arm_fr5_j6_pgc_sp20_s$S > $D/log_fr5_s$S.txt 2>&1 &
done; wait
# lane 3 (optional, ~10-12 min each, parallel): physics at the jerk-limited timings (FR5 after lane 1)
for J in 1000 8000; do
 $PY r19stir2_phys.py DRIVER=arm ARM=ur5e_enc2_pgc LIB=results/r19/stir/lib_stir_cycle_ur5e_enc2_pgc_j$J.json LAWNPZ=results/r19/stir/retime/fromrest_ur5e_enc2_pgc_j$J.npz TAG=full_arm_ur5e_enc2_pgc_j${J}_s1 > $D/log_ur5e_j$J.txt 2>&1 &
 $PY r19stir2_phys.py DRIVER=arm ARM=fr5_j6_pgc_sp20 LIB=results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20_j$J.json LAWNPZ=results/r19/stir/retime/fromrest_fr5_j6_pgc_sp20_j$J.npz TAG=full_arm_fr5_j6_pgc_sp20_j${J}_s1 > $D/log_fr5_j$J.txt 2>&1 &
done; wait
```

## 6. Files

All new. No shared file was edited, and nothing in `results/r15` was written.
- **Code:**
  - `r19stir2_join.py` (`join`, `cycle`);
  - `r19stir2_law.py` (time law with a jerk limit, n coordinates);
  - `r19stir2_phys.py` (stirbench physics with bench / arm drivers, checkpoint / resume, `DIAG`, `LIB` / `LAWNPZ`);
  - `r19stir2_retime.py` (`law`, `pick`, `ladder`, `check`).
- **Library entries:**
  - `results/r19/stir/lib_stir_join_ur5e_enc2_pgc.json`, `lib_stir_join_fr5_j6_pgc_sp20.json`;
  - `lib_stir_cycle_ur5e_enc2_pgc_j{57296,8000,1000}.json`.
- **Results:**
  - `results/r19/stir/join_<arm>/` (`join.json`, `cycle_std_recheck.json`, log);
  - `results/r19/stir/phys/` (`stir2_full_*_s1.json`, smoke runs, `diag_*.json`, `fromrest_*.npz`, `ckpt_*.pkl`);
  - `results/r19/stir/retime/` (`law_*`, `fromrest_*_j*.npz`, `check.json`).
- **Superseded, safe to remove (mine):**
  - `lib_stir_cycle_ur5e_enc2_pgc_j*.replaced_{1,2}.json` (the no-margin versions);
  - `phys/ckpt_*.pkl`;
  - `phys/stir2_smoke_*`, `stir2_ck_*`.
- **Deleted by mistake:** `results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20.json` (lane 0).
