# R19 smooth: retime and blend the checked paths, then re-check them (2026-10-13)

User request: "Goal is less money, more smooth movements. Could consider lots of predefined movements then movement sets. Therefore no need check after each tiny movement."

This round takes the five checked whole-action paths:
- wok plate + sink rinse;
- R18b spatula rest → stroke start;
- faucet lever;
- lid;
- spider.

For each one it:
1. measures how they are timed today;
2. replaces their geometry with a smooth one (spline or via-point blends) and re-checks every state at ≤ 4 mm;
3. gives them a jerk-limited, near-time-optimal time law with sourced or labelled limits.

Code:
- `r19smooth.py` (everything per action);
- `r19smooth_report.py` (tables);
- `r19smooth_hub.py` (hand-off cost);
- `r19smooth_cart.py` (cart tip-over at higher acceleration);
- `r19smooth_stir.py` (stir hand-offs).

Results are in `results/r19/smooth/`. No existing file was changed and nothing was installed.

## Answer first

- **Checking and timing are separate.** A collision result depends only on the geometric path, never on its time law. A movement is therefore checked once, offline, as a geometry. Afterwards it can be sped up, slowed down or retimed with no new collision check. Only the dynamic limits (jaw moment, food acceleration, cart tipping, joint limits) depend on timing, and they are cheap formula checks.
- **Every smoothed path passes.** All 10 smoothed geometries (5 actions × spline / blend) were re-checked state by state at ≤ 4 mm point-bound spacing, with the unchanged checker (MuJoCo contacts + GJK lower-bound certificate, 10 / 5 mm gaps, joint ranges). Results: **0 hits, 0 out-of-range states, minimum reserve equal to the baseline's**.
- **R17's times assume unlimited acceleration.** R17 gives each stored step its own constant speed, so velocity jumps at every step and acceleration and jerk are unbounded. With the same speed caps plus sourced acceleration limits and a jerk limit, the same actions take 20–50 % longer: wok 48.9 → 67.1 s.
- **Faster caps recover the time.** With the sourced faster speed caps and a cart acceleration of 0.5 m/s² (checked against the sim's own tip-over model, with the held load), the actions are as fast as R17's idealized numbers or faster, and smooth:

  | Action | R17 | Smoothed |
  |---|---|---|
  | Wok | 48.9 s | 47.3 s |
  | Spatula | 26.9 s | 19.9 s |
  | Lid | 20.2 s | 19.9 s |
  | Spider | 52.6 s | 45.4 s |

  Joint jerk ≤ 14 rad/s³, cart jerk ≤ 5 m/s³.
- **The cart is the bottleneck.** Its acceleration limit is the binding constraint, not the arm. The R17 IK uses the cart as the "cheap" variable, so the cart starts and stops often. At the sim's 0.15 m/s² stability design case, smooth execution is slow.
- **Stops drop from hundreds to a handful.** Executed as stored waypoints, the wok would stop at all 470 states (221 s). Smoothed, it has 7 zero-velocity points, only where physics or process needs them:
  - grasp and release;
  - the two slow straight grasp/release pieces;
  - the three dwells.
- **Spline beats blend.** The spline variant is 10–30 % faster than UR-style via-point blending at the same deviation tolerance, because blends have to shrink to about 1 mm at tight spots.
- **Recommended stored format:** a cubic B-spline in joint space per piece, a check certificate, hub states, and a time law generated when the movements are composed (§6).

## 1. How the checked paths are timed today

`r17chain.py` gives every stored step `dt = max(object step / 0.10 m/s, rotation / 45°/s, max joint / 60°/s, cart / 0.25 m/s)`. It adds the dwells, 0.6 s per join, 0.8 s per grasp/release and 0.6 s per approach. Reconstructed from the stored states, this reproduces every reported time within 0.1 s.

| Action | R17 time (motion) | Stored states | 2π label jumps (joint entries) | Stops in the R17 law: dwell / join / reversal | Corners 30–150° | Stop at every stored state (unblended `movej`) |
|---|---|---|---|---|---|---|
| wok | 48.9 s (36.2) | 470 | 6 | 3 / 3 / 2 | 16 | 221.4 s |
| spatula | 26.9 s (24.0) | 249 | 1 | 0 / 1 / 0 | 6 | 121.6 s |
| lever | 3.5 s (0.8) | 16 | 0 | 0 / 0 / 0 | 0 | 8.6 s |
| lid | 20.2 s (16.8) | 205 | 2 | 0 / 1 / 0 | 5 | 74.8 s |
| spider | 52.6 s (43.0) | 516 | 8 | 1 / 3 / 2 | 17 | 194.0 s |

What the R17 timing law implies:

- **It is not acceleration-limited, let alone jerk-limited.** Velocity is constant over each stored step and jumps between steps, from rest at the start and to rest at the end. Finite differences at the stored steps give accelerations up to 59 m/s² on the cart and 10⁷ °/s² on the joints, and jerk up to 6·10⁹ °/s³. Formally these are unbounded: the values are sampling artefacts.
- **The only stop/start allowance is 0.6 s per join.** That is 2–5 % of motion time.
- **A real controller cannot run it as written.** It would either stop at every stored state (the right-hand column) or low-pass filter the commands, which leaves the checked path by an unknown amount.

Findings about the stored `play` data:

- **2π label jumps.** The joins leave ±2π jumps in the arm joints:
  - wok: rows 215 and 356;
  - spider: rows 51, 178 and 412;
  - lid: row 120;
  - spatula: row 132.

  They are the same pose. Unwrapped, every path stays inside every joint range (checked). Any exporter to a real robot must unwrap them, or a joint spins 360°. `r19smooth.unwrap()` does this before any analysis.
- **The stored states are not at ≤ 4 mm.** Consecutive stored states are about 20 mm apart (median point bound). The maximum gap is:

  | Action | Max gap (point bound) |
  |---|---|
  | wok | 83 mm |
  | lid | 233 mm |
  | spatula | 252 mm |

  The largest gaps are at the subsampled join states. R17 checked them at 1 cm / 2° object steps, with the full GJK bound on every 5th state. This round re-checked the stored paths (joint-linear between states) at ≤ 4 mm for the first time:

  | Action | States checked | Hits | Min reserve |
  |---|---|---|---|
  | wok | 4,588 | 0 | 2.02 mm |
  | spatula | 2,642 | 0 | 2.04 mm |
  | lever | 128 | 0 | 5.98 mm |
  | lid | 2,410 | 0 | 1.0 mm |
  | spider | 4,335 | 0 | 2.03 mm |

  The wok's 2.02 mm, against R17's reported 3.3 mm, is an arm link against `raw_potato` between the sampled states. The stored states themselves give 2.30 mm.
- **Model bug: held boxes after R15 are not meshes.** In `scene.build` the R11 box-to-mesh conversion (`mesh_tool`, DECISIONS 2026-10-10) runs before the `kitchen14` hooks. So every held part added from R15 on (wok shell tiles, spatula blade, `R_gripper_*`) is still a MuJoCo box primitive. Consequences:
  - With that stock model the spatula baseline has **34 hit states**: the blade against `raw_tomato`, MuJoCo distance 4.90 mm.
  - The exact GJK distance for the same pair is 9.81 mm, so these are the known 0.5× box-box artefact. They are false hits; the stock-model baseline is kept as `spatula_baseline_stock.json`.
  - All R19 checks apply the R11 rule to the remaining tool-side boxes (identical 8-vertex meshes, geometry unchanged). `R19MESHHELD=0` reproduces the stock model.
  - Moving the conversion after the hooks is a one-line fix in `scene.py`, not made.

## 2. Smoothing methods

The path is cut at the mandatory stops:
- start and end;
- dwells (tipped over the plate 2 s, under the tap 5 s, emptied 1 s; spider drain 5 s);
- true reversals (turn > 150° in velocity-scaled joint space).

**Fixed pieces (grasp/release windows).** These are kept as slow, straight pieces: pick → lifted, lowered → set down, lid in/out of the rack, spider off/onto its rest, spatula pick, and the whole lever lift.
- Geometry: an interpolating cubic through every stored state. It deviates ≤ 0.05 mm from the stored polyline (spatula 8 mm in point bound, because its stored steps are 8–10 cm). Its TCP stays ≤ 0.9 mm from the straight line (the lever, an arc, excluded).
- Speed: the R17 caps, in every profile.
- The grasp approach/retreat states (`approach_qs`) are unchanged.

**Free pieces** get one of two geometries:
- **(b) spline:** a weighted cubic smoothing spline with a knot at every stored state (C2, so jerk stays finite).
  - Each stored state's deviation (global point bound of the joint difference) stays within `clip(0.5 × that state's own clearance reserve, 0.5 mm, 8 mm)`.
  - States that break it get 4× weight until all pass.
  - Ends are exact.
  - A coordinate that sits on a range limit is fitted as `limit + h²`, so it can never cross the limit. This applies to the spatula cart at its −1.48 m travel end.
- **(a) blend:** Douglas–Peucker via points of the stored states (same tolerance), straight joint-space lines, and C2 quintic Hermite blends at the vias. Each blend is halved until its middle is within the via's tolerance (the UR blend-radius idea).

**(c) Time law.** Per piece, rest to rest:
1. **TOPP by reachability analysis** on a ≤ 3 mm grid, with points inside every short blend. Constraints are expressed in (s̈, ṡ²):
   - joint, cart, object and TCP speed;
   - joint, cart and TCP acceleration;
   - food centre-of-mass acceleration;
   - PGC jaw moment `|m r×(a_c+g) + Iα + ω×Iω| ≤ 7 N·m`. Mass and CoM are r17chain's; the inertia uses discs and is approximate.
2. **Erosion** of the speed profile over the distance covered in W/2.
3. **A W = 0.2 s moving average of ṡ(t)**, giving path jerk ≤ 2a/W, plus a 0.04 s one.
4. **Local slow-downs** wherever any limit is exceeded on the 2 ms grid, repeated until every ratio is ≤ 1. All final laws pass, and no uniform stretch was needed.

Limits per profile:

| Limit | `same` (R17 caps) | `fast` | `fastcart` | Source |
|---|---|---|---|---|
| Object speed | 0.10 m/s | 0.25 m/s | 0.25 m/s | R17 assumption / ISO 10218-1 reduced speed 250 mm/s = URScript `movel` default v |
| TCP speed | (none, as R17) | 0.25 m/s | 0.25 m/s | as above |
| Rotation | 45°/s | 90°/s (wok 45°/s) | same as fast | R17 / assumption; wok kept at R17 / R15 pour rate |
| Joint speed | 60°/s | 180°/s | 180°/s | R17 / UR5e datasheet ±180°/s |
| Cart speed | 0.25 m/s | 0.25 | 0.25 | r17chain CW |
| Joint acceleration | 1.4 rad/s² | 1.4 | 1.4 | URScript `movej` default a. The true maximum is unpublished; it was never binding. |
| TCP acceleration | 1.2 m/s² | 1.2 | 1.2 | URScript `movel` default a |
| Cart acceleration | 0.15 m/s² | 0.15 | **0.5 m/s²** | `mobile.py` tip case and R09 drive sizing / `r19smooth_cart.py` |
| Jerk (joint / cart) | 14 rad/s³ / 1.5 m/s³ | same | 14 / 5 | **ASSUMPTION**: full acceleration in ≥ 0.1 s (no OEM value) |
| Food CoM acceleration | 2.0 m/s² | 2.0 | 2.0 | **ASSUMPTION**, derived below |
| PGC jaw moment | 7 N·m incl. inertial | 7 | 7 | project value (DH) |

**Food acceleration assumption.** It is derived, not sourced:
- 0.3 L of sauce in the R15 wok (sphere radius 0.20 m, rim at 58.2° polar) forms a cap 22 mm deep with a 27.3° half-angle.
- Quasi-statically it reaches the rim when the effective gravity tilts 30.9°, i.e. at 5.9 m/s².
- Dividing by 2 (slosh overshoot of the first mode, pendulum period about 0.9 s) and by 1.5 margin gives 2.0 m/s².
- The literature (e.g. arXiv 2408.00215) uses pendulum slosh models and gives no single threshold.
- It is never binding: the peak food-CoM acceleration in any profile is 0.82 m/s².

**Cart acceleration 0.5 m/s².** `mobile.dock_stability` was re-evaluated with the acceleration as a parameter and the held load included (the chains were checked with `mass=0`). The model is unchanged otherwise: ×1.5 on moving masses and inertia, ±0.22 m lateral, back line, bumper ≤ 250 N.

| Action | Worst-state margin at 0.15 m/s² | Worst-state margin at 0.5 m/s² |
|---|---|---|
| wok | 67.6 mm | 42.7 mm |
| spatula | 138 mm | 112 mm |
| lid | 114 mm | 88 mm |
| spider | 136 mm | 107 mm |
| lever | 99 mm | 74 mm |

The R09 wheels (10 N·m rated) need about 2–3 N·m each at 0.5 m/s², whether the cart is the sim's 68 kg or the roughly 130 kg implied by R09's 79 N sizing. **No new hardware or money is needed**, only a controller limit; a measured tip test is still open.

## 3. Re-check of the smoothed paths (≤ 4 mm, full checker, R11 mesh rule for held boxes)

| Action | Variant | States re-checked | Max spacing | Hits | Out of range | Min reserve (baseline) | Stored size |
|---|---|---|---|---|---|---|---|
| wok | spline | 4,355 | 4.0 mm | 0 | 0 | 2.01 mm (2.02) | 486 coefficient vectors |
| wok | blend | 4,344 | 4.0 | 0 | 0 | 2.03 (2.02) | 196 vias + radii |
| spatula | spline | 2,486 | 4.0 | 0 | 0 | 2.05 (2.04) | 251 |
| spatula | blend | 2,486 | 4.0 | 0 | 0 | 2.00 (2.04) | 73 vias |
| lever | either (one fixed piece) | 119 | 4.0 | 0 | 0 | 5.98 (5.98) | 16 |
| lid | spline | 2,267 | 4.0 | 0 | 0 | 1.00 (1.00) | 213 |
| lid | blend | 2,259 | 4.0 | 0 | 0 | 1.00 (1.00) | 99 vias |
| spider | spline | 4,159 | 4.0 | 0 | 0 | 2.01 (2.03) | 529 |
| spider | blend | 4,142 | 4.0 | 0 | 0 | 2.00 (2.03) | 215 vias |

- The tolerance-tightening loop was never needed: round 0 passed everywhere.
- The `*_move.json` files rebuild each path exactly: start and end within 1e-15, no gap between pieces.

## 4. Timing before → after

Spline variant (the blend variant is 10–30 % slower; see `summary.json`):

| Action | R17 nominal | `same` | `fast` | `fastcart` | Zero-velocity points: R17 waypoints → smoothed | Peak joint jerk: R17 FD → smoothed | Stop/start time (`same`) |
|---|---|---|---|---|---|---|---|
| wok | 48.9 s | 67.1 s | 58.0 s | **47.3 s** | 470 → 7 | 6·10⁹ → 774 °/s³ (13.5 rad/s³) | 12.4 s (22 %) |
| spatula | 26.9 | 33.7 | 23.7 | **19.9** | 249 → 3 | 2·10⁷ → 738 | 7.5 s (24 %) |
| lever | 3.5 | 5.3 | 5.3 | 5.3 | 16 → 2 | 3·10⁴ → 718 | the whole lift |
| lid | 20.2 | 28.1 | 23.4 | **19.9** | 205 → 4 | 3·10⁵ → 802 | 3.8 s (15 %) |
| spider | 52.6 | 64.5 | 50.9 | **45.4** | 516 → 7 | 8·10⁸ → 795 | 7.3 s (13 %) |

How to read the table:
- **Totals** include dwells, 2 × 0.8 s grasp/release and the unchanged 6 cm approaches with an S-curve (0.78 s each instead of 0.6 s).
- **Stop/start time** is the time from rest until 90 % of the local cruise cap, plus the time back to rest.
- **The lever** is a single fixed contact piece. R17's 0.75 s assumed an instant step to 60°/s on wrist 3; with finite acceleration it takes 2.1 s.

**Peaks** (spline, all profiles):

| Quantity | Peak | Limit |
|---|---|---|
| Joint acceleration | ≤ 80°/s² | 1.4 rad/s² |
| Joint jerk | ≤ 802°/s³ | 14 rad/s³ |
| Cart acceleration | ≤ 0.15 / 0.48 m/s² | 0.15 / 0.5 m/s² |
| Cart jerk | ≤ 1.5 / 5 m/s³ | 1.5 / 5 m/s³ |
| TCP acceleration | ≤ 1.04 m/s² | 1.2 m/s² |
| Food CoM acceleration | ≤ 0.82 m/s² | 2.0 m/s² |

**PGC jaw moment with inertial loads:**

| Action | Dynamic peak | Static |
|---|---|---|
| wok | 6.467 N·m | 6.467 N·m (same: it peaks where the wok is nearly still) |
| spatula | 1.33 N·m | 1.30 N·m |
| lid | 1.64 N·m | 1.58 N·m |
| spider | 1.29 N·m | 1.25 N·m |

The 7 N·m constraint was active but never the bottleneck.

**What binds.** With R17's caps, the speed caps (object 0.10 m/s, wrist 3 at 60°/s) and the cart's 0.15 m/s² dominate. In the wok's first carry (`fast` profile) the cart is above 80 % of its acceleration limit 29 % of the time. Raising the cart to 0.5 m/s² cuts that piece from 9.9 to 7.0 s; raising joint acceleration to 4 rad/s² changes nothing. Joint speed and acceleration are far from the UR5e limits.

## 5. Hand-off between whole actions; composing pre-verified movement sets

- **Re-checking on composition.** The collision result is a property of the geometry only. A composed sequence needs no re-check if its pieces meet exactly at shared hub states (the same unwrapped 11-vector). Only the dynamic limits are evaluated per time law, and those are formulas.
- **Stop hubs (zero velocity at the shared state).** These need nothing else and are the simplest to compose in any order. Their cost was measured by cutting a free piece at its R17 meet point into two rest-to-rest movements (`r19smooth_hub.py`, `hub.json`):

  | Piece | Hub cost `same` | Hub cost `fastcart` |
  |---|---|---|
  | wok, sink → cooker | +0.36 s | +0.34 s |
  | wok, lifted → plate | −0.15 s | +0.04 s |
  | spider, plate → rest | +1.02 s | +0.51 s |

  The R17 meets are corners (shuffle/join) that the path must slow down through anyway, so a stop there costs 0–1 s. **The meet points are the natural movement-set boundaries.**
- **Flying hubs (no stop).** Both movements must share:
  - the hub state;
  - the tangent and curvature (C2);
  - one agreed hub speed with zero path acceleration.

  The practical form is a short straight joint-space "hub segment" through the hub, included in every movement that uses it, each movement timed with boundary speed v_H. This is only worth it where a stop costs more than about 1 s: a long straight cruise, not a corner.
- **R15 stir cycle, not smoothed here.** Its working parts follow the bench timing and its returns are rest-to-rest trapezoids. The bench keys (`r19smooth_stir.py`, `stir_handoff.json`) show the grip point moving at **0.54–0.88 m/s**, turning 80–140°/s and accelerating at 4–6.5 m/s² where each working part ends. That means 10 velocity jumps per 5-stroke cycle, so the checked 2.63 s period is not executable as stated. There are two options:
  - stop at each hand-off: about +1 s per stroke at 1.2 m/s², a period of about 3.6 s, which changes the R15 heat-contact physics;
  - velocity-matched returns: a quintic in joint space matching q, q̇ and q̈ at both ends. These need a re-check including the plume rule, and joint accelerations of a few rad/s². That is above the URScript default and within the R15 360°/s² assumption, but unsourced.

  This needs the stir arm states, which were never stored. The `reach_stir_h_scrape*` candidate files are not in `results/`, and regenerating them with `r15reach.py` writes into `results/r15`. **For the controller:** rerun `r15reach.py stir KEYS=results/r15/stir_h_scrape_dice_keys.json I={0,16,32,48,64} GRIP=.45`, then a copy of `r15stirwalk2.py` that also saves its states. The spatula → stir hand-off (R18b: cart 7.8 cm, joints ≤ 11°, 0.5 s) is a stop hub too.

## 6. Recommended trajectory format for stored movement sets

Store each movement (one hub to the next) as:

1. **Hubs.** `start` and `end` as exact, unwrapped 11-value states (cart, base_y, base_yaw, 6 joints, 2 jaws), plus whether each is a stop hub or a flying hub (state, tangent, speed).
2. **Geometry.** A list of pieces between its mandatory stops. Each piece holds:
   - a cubic B-spline (C2) in scaled joint space: knots, coefficients, scale `w`, and `q = f(s)/w`. Coordinates on a range limit are stored as `limit + h²`;
   - a flag: fixed (contact window, slow, R17 caps) or free;
   - the payload (mass, CoM, inertia) for the time law;
   - the dwell after the piece.

   Size: about one 7-number coefficient vector per stored R17 state, roughly 30 KB per action. A coarser B-spline would be smaller, but the corners need the knots. Spline is preferred over blend: it is 10–30 % faster at the same tolerance, and blend radii must shrink to about 1 mm at tight spots.
3. **Check certificate.** It records:
   - the scene/config hash;
   - checker and model version (with the R11 held-box mesh rule);
   - spacing rule (≤ 4 mm point bound);
   - states checked, hits = 0, ranges OK;
   - min reserve and its pair.

   Any geometry change invalidates it; a timing change does not.
4. **Time law.** Not stored as truth. It is generated when the movements are composed (TOPP + jerk filter + verification on a 2 ms grid, as in `r19smooth.py`) for the current profile. It is streamed to the UR over RTDE `servoj` at the e-Series 500 Hz rate, with the cart axis on the same clock. ruckig or toppra would do this more cleanly, but they are not installed and were not needed.
   - UR's own `optimovej`/`optimovel` are jerk-limited, but they blend between their own waypoints, not along our checked spline. Using them needs dense waypoints and a deviation bound.
   - `tool_wrench_limit_set()` is the UR-side way to cap held-load accelerations.
5. **Servo tracking error.** Reserves are about 2 mm in places (lid 1.0 mm in the rack), so the controller's path-following error must be measured and kept below the reserve. It is not modelled here.

## 7. What is checked and what is not

**Checked:**
- every state of each smoothed geometry, at ≤ 4 mm, with the full checker and joint ranges;
- the stored baselines, the same way;
- every time law against all listed limits on a 2 ms grid (max ratio ≤ 1.001);
- cart tipping at 0.5 m/s² with the static-plus-inertia model;
- the exported files rebuilding the path.

**Not checked:**
- **Grasp approach/retreat (`approach_qs`).** Unchanged, still at R17's 1 cm steps, not re-checked at 4 mm.
- **Results depend on the R11 mesh rule** for held boxes. With the stock model, the spatula re-check reports MuJoCo-only false hits. The GJK certificate does not depend on it.
- **Real-controller effects:** servo tracking error, cart/arm synchronization, real controller behaviour.
- **Dynamic tip-over along the actual trajectories.** Only the quasi-static model was evaluated.
- **Slosh and pour physics.** The food limit is an assumption. The retimed plate tip keeps R17's 45°/s rotation cap, but its acceleration profile differs from the R15 pour simulation.
- **The stir cycle** (§5).
- **The two halves in the hub experiment** (timing only, not re-checked).
- **Approximate inertia:** disc inertias for the wok, lid and food.

## 8. Commands (from `robot_rail/sim/r10/claude`, Python = `robot_v5/board/work/t01/.venv/Scripts/python.exe`, each < 5 min on 28 workers)

```
python r19smooth.py ACT=wok VARIANTS=spline          # ~2 min (first run computes the baseline, ~1 min)
python r19smooth.py ACT=wok VARIANTS=blend           # ~1.5 min
python r19smooth.py ACT=spatula                      # ~1.5 min
python r19smooth.py ACT=lid                          # ~2 min
python r19smooth.py ACT=spider VARIANTS=spline       # ~2 min
python r19smooth.py ACT=spider VARIANTS=blend        # ~1.2 min
python r19smooth.py ACT=lever                        # ~20 s
R19MESHHELD=0 python r19smooth.py ACT=spatula VARIANTS=spline   # stock model: the box-box false hits
python r19smooth_report.py                           # summary.json + tables
python r19smooth_hub.py                              # ~3 min, hub.json
python r19smooth_cart.py ACT=wok A=.15,.3,.5,.8      # tip-over margins
python r19smooth_stir.py                             # stir hand-off speeds
```

Sources:
- [UR5e datasheet](https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/) (joint speeds ±180°/s);
- [URScript `movej` (a=1.4, v=1.05)](https://www.universal-robots.com/manuals/EN/HTML/SW5_24/Content/prod-scriptmanual/all_scripts/movej_qa14v105t0r.htm);
- [URScript `movel` (a=1.2, v=0.25)](https://www.universal-robots.com/manuals/EN/HTML/SW5_20/Content/prod-scriptmanual/G5/movel_posea12v025t.htm);
- [OptiMove: jerk-limited profiles, `tool_wrench_limit_set`](https://www.universal-robots.com/manuals/EN/HTML/SW10_12_1/Content/prod-scriptmanual/all_scripts/movel_optimove.htm);
- [Spill-free liquid transport (pendulum slosh models)](https://arxiv.org/pdf/2408.00215);
- ISO 10218-1 reduced speed 250 mm/s (standard text, not re-fetched).
