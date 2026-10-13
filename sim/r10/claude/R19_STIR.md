# R19 stir: velocity-continuous returns, stored and certified (2026-10-13, GitHub #3)

Issue #3: "[control] Stir cycle has velocity jumps and no stored states". `R19_SMOOTH.md` §5 found that each working part of the R15 stir ends at 0.54–0.88 m/s at the grip point, while each return starts from rest. That is 10 velocity jumps per 5-stroke cycle, so the checked 2.63 s per stroke could not be executed.

This round:
- builds velocity-continuous returns (C2: q, q̇, q̈ matched at every hand-off) and the stop-at-hand-off variant for comparison;
- does this for the checking standard `ARM=ur5e_enc2_pgc` and for the cheap-arm candidate `ARM=fr5_j6_pgc_sp20`;
- re-checks every state at ≤ 4 mm, plume included;
- times the cycle under sourced or labelled joint limits;
- stores the certified cycle as a library entry with its certificate.

Code (all new; no existing file was changed, `results/r15` was not written):
- `r19stir_reach.py`: the R15 stroke-start reach probes (unchanged `r15reach.py`), written to `results/r19/stir/reach/`;
- `r19stir_cycle.py`: working parts, returns, chain choice, certification, time laws, library entry;
- `r19stir_report.py`: an independent re-evaluation of the stored library entries.

## Answer first

| | UR5e `ur5e_enc2_pgc` | FR5 `fr5_j6_pgc_sp20` |
|---|---|---|
| **Velocity-continuous (A), joint accel ≤ 800 °/s²** | **2.32 s per stroke** (11.60 s per 5-stroke cycle) | **2.29 s** (11.43 s) |
| Velocity-continuous (A), ≤ 360 °/s² (R15 assumption) | 2.77 s | 2.64 s |
| Stop at every hand-off (B), ≤ 800 °/s² | 3.16 s | 3.10 s |
| Stop at every hand-off (B), ≤ 360 °/s² | 3.70 s | 3.58 s |
| Certified states (A), ≤ 4 mm apart | 4,484: 0 hits, 0 out of range | 3,973: 0 hits, 0 out of range |
| Min reserve: held/gripper vs environment / self / robot vs environment | 2.0 / 2.0 / 21.6 mm | 2.0 / 2.0 / 10.0 mm |
| Plume margin (arm ≥ 0.20 m from the wok axis) | 25.8 mm, 0 violations | 25.8 mm, 0 violations |
| Peak joint speed / acceleration (A, 800 °/s²) | 176 °/s / 785 °/s² (limits 180 / 800) | 177 °/s / 795 °/s² |
| Peak grip-point (TCP) speed | 0.86 m/s | 0.87 m/s (FR5 limit 1 m/s) |
| Library entry | `results/r19/stir/lib_stir_cycle_ur5e_enc2_pgc.json` | `results/r19/stir/lib_stir_cycle_fr5_j6_pgc_sp20.json` |

- **The velocity-continuous cycle is faster than the old 2.63 s and is executable.**
  - The returns take 0.34–0.49 s, against the R15 rest-to-rest trapezoids of 0.50–0.77 s.
  - The working parts run at or a little below bench speed (median 0.98 × bench).
  - It is also faster than the bench stroke itself (2.4 s).
- **Stopping at each hand-off costs 0.8–0.9 s per stroke** (+36 %) at 800 °/s², and 0.9–0.95 s at 360 °/s². The stops also slow the working parts to 1.2–1.3 × bench time, because each must start and end at rest. R19_SMOOTH estimated about 3.6 s for this variant; that matches B at 360 °/s².
- **The 2.63 s cycle was not executable for a second reason too: acceleration.** At bench timing the working parts alone need peak joint accelerations of 760–1,520 °/s² (UR5e strokes 0–3; 2,010 °/s² in the smoothed stroke 4) and 730–1,730 °/s² (FR5). Both are above UR's 800 °/s² guidance. Every variant therefore retimes the working parts along their checked path, never faster than the bench. The UR5e cycle stored in R19 (`stirwalk2_h_scrape_dice_r17.json`) also has a kink in stroke 4: its IK sits on the elbow limit (−160°) and leaves it with a jump of about 80 °/s in one 10 ms step (§3.2).
- **No via was needed, and no via helped.**
  - Among the branch combinations that work, every velocity-matched quintic passes without a via.
  - For the returns that fail, none of 16 via sets passes. The vias were lifted 3–15 cm at the midpoint, or lift-off and set-down, either straight up or drawn back along the handle. Lifting puts the spatula handle into the hood or the camera. Drawing back puts the elbow or forearm into closed upper-cabinet door 1.
- **The FR5 wall dip is fixed by a different stroke-4 start branch, not by a via.**
  - On branch 4:0 of `fr5_j6_pgc_sp20`, every return into stroke 4 fails: straight, quintic, or any of the vias. The blade goes into the wok wall within 4–17 % of the move. This is the same failure as the R15 walk's (`r15_wok_t4_4` vs the blade).
  - The other branch, 4:1 (wrist flipped; at the stroke's end the elbow is at −146° instead of −121°), passes with a plain velocity-matched return.
  - The R15 walk never saw it, because `solver.solve` keeps only the 8 best-reserve candidates per solve. The reach probes here keep 48 (`KEEP=48`); see §2.
- **For both arms, exactly one combination of IK branches gives a full cycle.**
  - UR5e: 1 of 24 combinations.
  - FR5: 1 of 12 for A, 2 of 12 for B.
  - The UR5e's working stroke 4 is the branch that rides the elbow limit, as in R15. It is stored as a range-safe smoothing spline: within 2.95 mm / 2.49° of the bench pose, against 2.03 mm / 2.62° for its own IK states and the R15 gate of 5 mm / 3°.

## 1. Joint limits used

| Limit | Value | Source |
|---|---|---|
| Joint speed, UR5e | 180 °/s, all joints | UR5e datasheet (`arms.py`) |
| Joint speed, FR5 | 180 °/s, all joints | fairino.us FR5 page; URDF 3.15–3.2 rad/s (`arms.py`) |
| Joint acceleration `A_UR` | **800 °/s²** (13.96 rad/s²) | **UR guidance, not a datasheet value.** "moveJ accelerations should be less than 800deg/sec^2", Universal Robots staff on the UR forum ([link](https://forum.universal-robots.com/t/maximum-axis-speed-acceleration/13338)). UR publishes no maximum joint acceleration; the same thread says the limit depends on payload and pose. For the FR5 the same number is an **ASSUMPTION**: Fairino publishes none. Its MoveIt `joint_limits.yaml` has 0.7 rad/s², a downscaled planning default. |
| Joint acceleration `A_R15` | 360 °/s² | **ASSUMPTION** of R15 (`r15stirwalk2.py` AMAX), run as the conservative case |
| Working parts | ds/dt ≤ 1 | Never faster than the bench stroke |
| Jerk | not limited | No OEM value found. The time law uses a moving-average filter (W = 0.1 s, `r19smooth.timelaw`). Peaks are reported (§4) |
| TCP speed | reported | FR5 TCP max 1 m/s (`R19_ARM_SWAP.md`); not a constraint here |

## 2. Method

Geometry and timing are separate, as in `R19_SMOOTH.md`. Every state of the geometry is checked once. The time law is computed afterwards on the checked path and needs no new check.

1. **Stroke-start candidates** (`r19stir_reach.py ARM=<arm> KEEP=48`). These are the R15 probes (`r15reach.py stir`, CARTX=.55, GRIP=.45), unchanged except for one thing: `solver.solve` keeps the 48 best candidates per solve instead of 8.
   - It keeps candidates by clearance reserve *before* the plume post-check. With 8, the `fr5_j6_pgc_sp20` probe at stroke 3 lost every plume-clear candidate (0 of 32; best plume −39 mm).
   - This is search breadth only. Every kept candidate passed the same checks. `solver.py` is not edited; a patched copy of `solve()` lives in the probe process.
   - Plume-clear starts per stroke:
     - UR5e: 46 / 38 / 47 / 52 / 51;
     - FR5: 37 / 41 / 37 / 41 / 30.
2. **Working parts** (`works`). Each candidate follows its stroke's working part, stroke phase 0 → 0.76 of the 2.4 s bench stroke.
   - This uses exactly the R15/`r19stir_save.py` continuation and gates: 10 ms IK steps, pose ≤ 5 mm / 3°, fast check every step, full check every 25th, plume every step.
   - The scene is `r19stir_save.py SCENE=r17`, with the R11 held-box mesh rule as in `r19enc_check.py`.
   - Passing parts per stroke:
     - UR5e: 38 / 21 / 45 / 16 / 37;
     - FR5: 25 / 15 / 37 / 15 / 22.
   - They fall into only 1–3 IK branches per stroke, i.e. distinct end states modulo 2π:
     - UR5e: 2 / 2 / 3 / 1 / 2;
     - FR5: 2 / 1 / 3 / 1 / 2.
   - A working part is stored as an interpolating quintic B-spline through its IK states, with s = bench time.
3. **Returns** (`returns`), for every combination of branches (a "chain"). The 2π labels of each part are taken nearest to the previous part's end, and the close return goes back to stroke 0's labels, so the cycle is periodic with no joint winding up.
   - **A (velocity-continuous):** a quintic spline r(u), u ∈ [0, T]. It meets both working parts' q, q′, q″ (per bench second) at the hand-offs, through 0, 1 or 2 vias. The cycle is then one **closed C2 path q(s)**, so any C2 time law gives continuous joint velocity and acceleration everywhere, including around the cycle. T runs from 0.2 to 1.2 s.
   - **B (stop at each hand-off):** a straight joint line, or a natural cubic through the vias. It is timed from rest to rest.
   - **Via sets (16), each with lift 3 / 6 / 10 / 15 cm:**
     - `mid`: the TCP half-way between the two hand-off poses, lifted;
     - `ends`: the end pose lifted (at T/3), then the start pose lifted (at 2T/3);
     - `_back` versions of both: drawn back along the tool axis (the handle) instead of up.
   - **Screening:** contacts, joint ranges and plume, at ≤ 8 mm by the global point bound.
     - Round 0: no via, the 3 cheapest durations.
     - Later rounds: every via set, only for returns with no pass yet.
     - Screened: UR5e 1,434 A + 547 B options for 50 returns; FR5 479 A + 260 B for 22.
4. **Chain:** the one with the smallest proxy time among those with a screened return at every hand-off. The proxy is the sum of the working parts' own TOPP times and the returns' T × slow-down.
5. **Certificate:** every segment cut to ≤ 4 mm by `point_bound` (`r19smooth.FastBound`, sub-steps ≤ 0.5 mm), then `Checker.check(full=True)`:
   - MuJoCo contacts plus the GJK lower-bound certificate;
   - 10 mm robot–environment, 5 mm gripper/held–environment, 0 mm self;
   - joint ranges;
   - hit pairs classed by the exact convex bound (`r19enc_check.one`).

   Plus the plume rule, unchanged: every robot geom except the spatula, cart and dock stays ≥ 0 mm outside the 0.20 m cylinder about the wok axis, from the rim to 1.25 m. A return that fails here moves to its next screened option. No gate was loosened.
6. **Time law:** TOPP by reachability analysis in closed form for per-joint limits:
   - |q′ṡ| ≤ V and |q′s̈ + q″ṡ²| ≤ A;
   - ṡ ≤ 1 on the working parts;
   - then `r19smooth.timelaw` (erosion, moving-average jerk filter W = 0.1 s, 2 ms grid);
   - then local slow-downs until every limit holds on the 2 ms grid. All laws converged: max ratio ≤ 0.995 of every limit.
   - **A** is periodic: 3 cycles are unrolled from rest to rest, with the same slow-downs in each copy, and the middle cycle is kept. ṡ at the start and end of the stored period agree to 0.01 %. Three full cycles from rest at `H_stir0` back to rest take 35.1 s (UR5e) / 34.5 s (FR5).
   - **B** is rest to rest per segment.
7. **Library entry:** written only when the re-check is clean; an existing file is renamed first, as `r19enc_adopt.py` does. See §5.

## 3. Results

### 3.1 Per segment (s), velocity-continuous variant A

| Arm, limit | work 0 | ret 0→1 | work 1 | ret 1→2 | work 2 | ret 2→3 | work 3 | ret 3→4 | work 4 | ret 4→0 | **per stroke** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bench | 1.82 | — | 1.82 | — | 1.82 | — | 1.82 | — | 1.82 | — | 2.40 (bench stroke) |
| UR5e, 800 °/s² | 1.907 | 0.341 | 1.861 | 0.347 | 1.864 | 0.413 | 1.891 | 0.492 | 2.074 | 0.416 | **2.321** |
| UR5e, 360 °/s² | 2.169 | 0.497 | 1.985 | 0.505 | 1.960 | 0.608 | 2.187 | 0.706 | 2.596 | 0.608 | 2.765 |
| FR5, 800 °/s² | 1.894 | 0.336 | 1.860 | 0.353 | 1.866 | 0.410 | 1.876 | 0.434 | 2.005 | 0.399 | **2.286** |
| FR5, 360 °/s² | 2.047 | 0.485 | 1.935 | 0.515 | 1.901 | 0.598 | 2.099 | 0.633 | 2.413 | 0.582 | 2.642 |

- **Working parts under A (800 °/s²):** 9.60 s / 9.50 s per cycle against 9.10 s at bench timing (+5.5 % / +4.4 %).
  - The median ṡ is 0.98. ṡ ≥ 0.95 for 80 % (UR5e) / 89 % (FR5) of the working time.
  - The minimum ṡ is 0.63 / 0.51, near the hand-offs, where the bench path's accelerations are highest.
- **Return nominal durations:** T = 0.3 / 0.3 / 0.4 / 0.3 / 0.3 s (UR5e) and 0.3 / 0.3 / 0.4 / 0.3 / 0.2 s (FR5). None has a via.
- **Stop variant B (800 °/s²):**
  - working parts 2.19–2.44 s, returns 0.76–1.04 s;
  - the stroke's heat-contact timing changes much more than in A.
- **For reference, "nominal" timing** (working parts at bench time, returns at T, ṡ = 1 everywhere) would be 2.14 s (UR5e) / 2.12 s (FR5) per stroke. It needs up to 288 °/s and 2,398 °/s² (UR5e), and 249 °/s and 3,528 °/s² (FR5), so it is not executable.

### 3.2 What the stored R15/R19 cycle had

`results/r19/stir/stirwalk2_h_scrape_dice_r17.json` (`ARM=ur5e`, 2.63 s):
- 10 velocity jumps per cycle;
- the working parts at bench timing need up to 1,520 °/s²;
- the stroke-4 working part is IK-pinned at the elbow limit (−160°) for 30 steps, with pose error up to 2.03 mm and 2.62°. When it leaves the limit, wrist 1 jumps from −16 to −94 °/s in one 10 ms step (7,775 °/s² by finite differences, 184 °/s peak).

With the enclosing geometry, the UR5e's only feasible chain uses that same stroke-4 branch.
- The smooth stroke-4 branch has no passing return: the spatula handle hits the camera on 3 → 4, and the blade hits the wok wall or the plume rule fails on 4 → 0.
- So the branch is stored as a **range-safe smoothing spline**:
  - the elbow is fitted as −160° + h², so it can never cross the limit;
  - this gives the most smoothing within 3.5 mm / 3° of the bench pose;
  - result: 2.95 mm / 2.49°, at most 1.13° from the IK joints.
- It is certified like every other segment.

### 3.3 Peaks (variant A, 800 °/s²), from the stored entry

| | UR5e | FR5 |
|---|---|---|
| Joint speed, by joint (°/s) | 86 / 176 / 116 / 140 / 112 / 145 | 87 / 177 / 112 / 135 / 112 / 147 |
| Joint acceleration (°/s²) | 730 / 785 / 784 / 785 / 744 / 784 | 635 / 785 / 784 / 787 / 795 / 784 |
| Joint jerk, max (°/s³) | 58,063 (smoothed stroke 4, from the path's 3rd derivative) | 32,524 (close return) |
| Grip-point speed / acceleration | 0.86 m/s / 5.6 m/s² | 0.87 m/s / 5.9 m/s² |

- **Jerk is open.** No jerk limit is sourced. Even the bench working parts alone have 14,000–15,000 °/s³. Most of the peak comes from the geometry (q‴ṡ³ on the short quintic returns and the smoothed stroke 4), not the time law (≤ 8,300 °/s³). If the real controller needs a lower jerk, longer return durations T lower it, at some cost in period.

## 4. Certificates

Both variants of both arms are certified (`cycle_<arm>/cycle.json` has the per-segment tables):

| | UR5e A | UR5e B | FR5 A | FR5 B |
|---|---|---|---|---|
| States checked (≤ 4.0 mm) | 4,484 | 4,427 | 3,973 | 3,948 |
| Hit states / out of range | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Held/gripper vs environment | 2.0 mm (blade vs `r15_wok_t3_0`) | 2.0 | 2.0 (blade vs `r15_wok_t3_6`) | 2.0 |
| Robot vs environment | 21.6 mm (forearm vs hood) | 21.6 | 10.0 mm (forearm elbow housing vs closed door 1) | 18.3 |
| Self | 2.0 mm (wrist 1 vs wrist 3) | 2.0 | 2.0 (forearm wrist-1 housing vs wrist-2 neck) | 2.0 |
| Plume: working parts / returns | 25.8 / ≥ 73.1 mm | 25.8 / ≥ 68.2 | 25.8 / ≥ 74.2 | 25.8 / ≥ 72.1 |

**Independent re-evaluation** (`r19stir_report.py` → `results/r19/stir/summary.json`). It rebuilds the geometry and the time law from the library JSON alone and finds:
- the joint jump across every hand-off and around the cycle is 0.000000° in q, 0.000000 °/s in q′ and 0.0000 °/s² in q″;
- speed ≤ 0.98 and acceleration ≤ 0.99 of the limits;
- the stored states lie on the stored geometry, to ≤ 0.00014°.

## 5. Library entry (`results/r19/stir/lib_stir_cycle_<arm>.json`, about 1.2 MB each)

- **`id`, hubs:** `STIR_CYCLE`, `start_hub` = `end_hub` = `H_stir0` (the stroke-0 start, an 11-value state), pre- and postconditions.
- **`geometry`:** 10 segments (5 working parts, 5 returns). Each is a B-spline (knots, coefficients, degree) over the 6 arm joints. A coordinate stored as limit + h² is marked `sq`. The constant cart, base and jaws are in `state_const`.
- **`time_law`:** one period of the `A_UR` law from s = 0 at t = 0, on a 2 ms grid (`t`, `s`, `period_s`). To repeat, use t + period and s + length. q(t) = q(s(t)). The peaks and per-segment times are included.
- **`time_law_A_R15`, `stop_variant`:** the 360 °/s² law summary, and variant B's periods and certificate.
- **`states`:** the 4,484 / 3,973 certified states (≤ 4 mm apart, in cycle order, with segment names).
- **`verification.certificate`:**
  - the checker, gaps, spacing rule and plume rule;
  - the md5 of the scene model, the geometry and the states;
  - states checked, hits 0, ranges, min reserve by category, plume min and violations;
  - per-segment results.

  A geometry change invalidates it; a time-law change does not.

**H_stir0, UR5e.** It is the same pose as the R15 stroke-0 start: the same candidate branch, with the 2π labels J2 +2π, J5 −2π and J6 −2π. Against the spatula fetch's end hub `H_spat_stroke`, its joints differ by up to 12.5° (J2) and the cart by 7.8 cm, and joint 1 carries a 2π label difference. That join is not re-checked here (§6). The FR5 `H_stir0` is in its own entry.

## 6. What is checked and what is not

**Checked:**
- every state of both variants' geometry at ≤ 4 mm, with the full checker, joint ranges and the plume rule;
- every time law against joint speed, acceleration and the ṡ ≤ 1 cap on a 2 ms grid;
- C2 continuity and periodicity, from the stored file.

**Not checked / open:**
- **Joint acceleration.** 800 °/s² is UR's forum guidance, not a datasheet value. For the FR5 both values are assumptions. The real limit depends on payload and pose, so it should be measured on the arm. The 360 °/s² rows show the margin.
- **Jerk** has no sourced limit (§3.3).
- **Heat-contact physics.** In A the working parts run 4–5.5 % slower in total than the bench (locally down to 0.5–0.6 × near the hand-offs). In B they run 20–35 % slower. Neither is re-simulated in `stirbench.py`.
- **The spatula hand-off.** The join from `H_spat_stroke` (spatula fetch) into `H_stir0` was not re-checked with the new labels (J1 2π) or with `fr5_j6_pgc_sp20`.
- **Entering and leaving the periodic cycle.** This is the same geometry: the stored "three cycles from rest" law covers it. It is not stored as its own law.
- **The adapter's mass on the FR5 (`_sp20`)** is still not modelled (#2).
- **Controller tracking error.** The minimum reserve is 2.0 mm (blade vs wok tile), so the servo path-following error must stay below it.
- **The other stroke patterns:** only `h_scrape_dice` was run.

## 7. Commands run (from `robot_rail/sim/r10/claude`, Python = `robot_v5/board/work/t01/.venv/Scripts/python.exe`, each < 5 min, 28 workers)

```
python r19stir_reach.py ARM=ur5e_enc2_pgc KEEP=48          # 138 s
python r19stir_reach.py ARM=fr5_j6_pgc_sp20 KEEP=48        # 120 s
python r19stir_cycle.py works ARM=ur5e_enc2_pgc            # 83 s
python r19stir_cycle.py works ARM=fr5_j6_pgc_sp20          # 69 s
python r19stir_cycle.py returns ARM=fr5_j6_pgc_sp20        # 285 s (all rounds)
python r19stir_cycle.py returns ARM=ur5e_enc2_pgc ROUNDS=0 FRESH=1
python r19stir_cycle.py returns ARM=ur5e_enc2_pgc ROUNDS=1 PART=0/2
python r19stir_cycle.py returns ARM=ur5e_enc2_pgc ROUNDS=1 PART=1/2
python r19stir_cycle.py returns ARM=ur5e_enc2_pgc ROUNDS=2,3
python r19stir_cycle.py returns ARM=ur5e_enc2_pgc REDO=4:1 ROUNDS=0,1   # after the range-safe stroke-4 spline; then ROUNDS=1 and ROUNDS=2,3 again
python r19stir_cycle.py cycle ARM=fr5_j6_pgc_sp20          # 144 s first run (certification), then cached
python r19stir_cycle.py cycle ARM=ur5e_enc2_pgc            # 192 s first run, then cached
python r19stir_report.py                                   # summary.json
```

**Outputs:**
- `results/r19/stir/reach/` (stroke-start candidates);
- `results/r19/stir/cycle_<arm>/`: `works.json`, `returns.json`, `returns_cache.json`, `work_splines.json`, `cert_cache.pkl`, `cycle.json`, logs;
- `results/r19/stir/lib_stir_cycle_<arm>.json`;
- `results/r19/stir/summary.json`.
