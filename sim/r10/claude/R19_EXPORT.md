# R19 export: checked paths → a controller format, with a round-trip test (GitHub #6, 2026-10-14)

Task: nothing turned a checked sim path into something a real arm controller can run. This round writes an exporter that turns any checked result file into:
- a neutral JSON + CSV format;
- thin writers for UR (RTDE `servoj`) and Fairino FR5.

It then proves, for every exported set, that the exported geometry (not just the stored states) is collision-free under the same checker as the certificate.

Labels: **[M]** measured here, **[S]** sourced (link), **[E]** estimate or assumption.

Code (new files only; no existing file was changed, md5 checked before and after):
- `r19export.py`: export, recheck, report.
- `r19export_writers.py`: UR and FR5 writers.

Results are in `results/r19/export/`.

## Answer first

- **What is exported [M]: 47 sets.**
  - **UR5e `ur5e_enc2_pgc`:**
    - the 6 adopted cooking chains: wok, wok plate-spot 2, lever, lid, spatula, spider;
    - 3 reversed sets: faucet close, lid on, spatula stow;
    - all 22 hub-roadmap edges;
    - the adopted stir cycle `short01_u06_j8000`;
    - 9 prep sets.
  - **FR5 `fr5_j6_pgc_sp20`:** 6 sets: lever, spatula, wok, wok plate-spot 2, tomato prep, stir cycle.
  - **The "12 checked sets" of the issue** are the 12 `verified` sets of the movement library (`results/r19/prim/library_size.json`). 10 of the 12 are exported (table in §3.1).
    - FAUCET_OPEN / CLOSE, WOK_PLATE_RINSE, LID_OFF / ON, SPATULA_FETCH / STOW, and SPIDER_FETCH / DUMP / STOW (the spider is one sequence that contains all three).
    - **CARRIER_IN / OUT are not exported.** No carrier path was ever re-checked with the current arm geometry.
- **The round trip passes for all 47 sets [M]:**
  1. **State fit.** Every stored state is reproduced within its stated tolerance; 49,397 states were tested.
     - Contact windows, hub edges and the stir: ≤ 1·10⁻⁶ mm. They are exact or interpolating.
     - Free (smoothed) pieces: within clip(0.5 × that state's clearance reserve, 0.5, 8) mm, measured as a point bound.
     - Largest errors: wok 4.1 mm, lid 3.2 mm, spatula 3.3–3.5 mm; prep sets ≤ 1.0 mm.
  2. **Dense re-check.** Every exported spline was cut so consecutive states are ≤ 4 mm apart (point bound), and every state went through the same checker and scene as its certificate.
     - Result: 103,300 states, **0 hits**.
     - The minimum reserves equal the certificates' to within the granularity of the bound (wok 2.02 / 1.87 mm, lid 1.0 / 1.11 mm, stir 2.0 mm, plume 29.04 mm).
  3. **Limits.** On the 500 Hz stream, the largest ratio of joint or cart speed, acceleration or jerk to its limit is ≤ 1.000 (finite differences). The same holds when re-measured from the written UR / FR5 files.
- **Two first attempts failed; both are fixed and the reasons are kept in the code:**
  - **Gaps at sparse joins.** A smoothing spline through the stored states alone cut corners where consecutive stored states are 8–30 cm apart (the subsampled joins). The basket set had 13 hit states (wrist 2 against a cabinet door, −0.5 mm) and tubempty had 9. Tightening the tolerance at the stored states did not help (15 / 10 hits).
    - **Fix:** the spline is fitted through the stored states **plus joint-linear points of the certified polyline every ≤ 8 mm**. Every set then re-checked with 0 hits.
  - **Range overshoot.** The spline crossed a joint or travel limit in two places:
    - the spatula cart went 3.5 mm past its −1.48 m travel end;
    - the carrot wrist 1 went 0.4° past −360°.

    **Fix:** r19smooth's `limit + h²` rule, extended to every coordinate whose stored states come within 0.05 m or 0.05 rad of a limit. It is stored per span as `sq`.
- **Timing.**
  - **Chains** are close to the stored R17 nominal times, which assume unlimited acceleration:

    | Set | Export | R17 nominal |
    |---|---|---|
    | wok | 50.4 s | 48.9 s |
    | spider | 51.0 s | 52.6 s |
    | spatula | 22.8 s | 26.9 s |
    | lid | 23.4 s | 20.2 s |

  - **Hub edges are 1.1–2.7× slower** (1.1× for the cart-only station moves, 1.4–2.7× for the arm swings), because of finite acceleration and jerk and, mostly, because the export law caps the TCP at 0.25 m/s. The stored roadmap timing lets the hand reach 0.9 m/s. Without that cap, three edges take 3.7 / 4.3 / 6.2 s against 3.0 / 3.5 / 5.2 s stored [M, not kept].
- **Writers:**
  - **UR:** time + 6 joints at 500 Hz. Done.
  - **FR5:** time + 6 joints in degrees at the SDK `ServoJ` period of 8 ms. Done [S].
  - **FR5 TrajectoryJ file: not written [E].** The SDK has upload / load / move calls for it, but none of the public SDK or manual pages I reached publishes its file content format.

## 1. Inputs and what the exporter does with each kind

Any result file of these kinds goes in; the kind is read from the file. Nothing is hard-wired to a set, so the re-planned paths after #42 export the same way.

**chain** (`results/r17/chain_*_<arm>.json`)
- Contents: play, keyframes, approaches.
- Certificate:
  - the file's `adopted.play_recheck` (`r19enc_check.py recheck`);
  - the approaches, from `r19enc_adopt.py`.
- Scene used for the round trip:
  - play: `r19enc_check.ctx` (same key, suffix and PY plate as the certificate);
  - approaches: `r17chain.py` run up to its main loop with the chain's options, giving the empty-gripper scene of that keyframe (as `r19enc_adopt.py`).

**prep** (`results/r19/prep*/chain_*_<arm>.json`)
- Contents: play, keyframes, grasps.
- Certificate: `<file>_verify4mm[_pot].json`.
- Scene used for the round trip: `r19prep_verify.py` for `prep/`, or `r19prep4/5_verify.py` for `prep4/` and `prep5/`. That means the play scene plus each approach scene, with the food contact window (the touch test).

**hub** (`results/r19/hub_*/edge_*.json`)
- Contents: straight joint-space segments, via poses.
- Certificate: the edge file itself (`r19hub.py edge`).
- Scene used for the round trip: `r19hub.union_checker()` (same PY, same arm), using `check(full=True)['ok']`.

**stir** (`results/r19/stir/lib_stir_cycle_*.json`)
- Contents: a C2 B-spline cycle and a stored law.
- Certificate: the entry's own `verification.certificate`.
- Scene used for the round trip: `r19stir_cycle.model(sign)` + `r19enc_check.one`, plume rule included. The rebuilt model md5 equals the md5 stored in the certificate (`da5f0817…` UR, `dce91b21…` FR5).

A chain or prep file whose certificate is not clean is refused. Example: `chain_tubfill_full_ur5e_enc2_pgc` (3 hit states). Its adopted successor `chain_tubfill_t15fin` was exported instead.

### Steps for a chain or prep set

1. **Joint labels.** The play is unwrapped exactly as its certificate's checker did it:
   - chains: `r19smooth.unwrap`;
   - prep: `r19prep_verify.unwrap`.

   The stored ±2π jumps are counted in `labels.stored_2pi_label_jumps` (wok 6, spider 8, lid 2, spatula 1 joint entries).

   For `ur5e_enc2_pgc` the whole action is then relabelled by the hub roadmap's 2π shift (`hub_py.15_ur5e_enc2_pgc/hubs.json action_shifts`). Each approach gets the 2π multiple nearest its play end.

   Every resulting state is asserted inside the joint ranges.
2. **Certificate reproduction.** The stored states are resampled with the certificate's rule (joint-linear, ≤ 4 mm). The count must equal the certificate's: 128 / 2,410 / 2,642 / 4,335 / 4,588 for lever / lid / spatula / spider / wok, all equal.

   The certificate's per-state reserves then give each stored state its fit tolerance. Prep sets store no per-state reserves, so they get a uniform tolerance from the set's minimum reserve.
3. **Segmentation** (`r19smooth.py` rules), at:
   - start and end;
   - process dwells (keyframe `dwell_s`, or `r19smooth.CHAINS`);
   - the straight grasp / release pieces of the play;
   - path reversals (> 150° in velocity-scaled joint space).

   **Keyframe matching** is r19smooth's (object position within 8 mm, in order), plus the object rotation where the keyframe stores one. Without the rotation, the prep "rolled ±30°" rinse keyframes, which share one position, collapsed into one stop.

   This reproduces R19_SMOOTH's contact windows for all 5 cooking chains: wok (0,1),(15,16); lid (0,1),(7,8); spider (0,1),(17,18); spatula (0,1); lever (0,1).
4. **Geometry**, per piece, over the 7 moving coordinates `[carriage_x, q1..q6]`:
   - **Free pieces:** `r19smooth.fit_spline`, a cubic smoothing spline with a knot at every data point and exact ends. Its data are the stored states plus joint-linear points of the certified polyline every ≤ 8 mm. Every data point must lie within its tolerance by the global point bound (`FastBound.g7`).
   - **Contact windows:** an interpolating cubic through the stored states (`r19smooth.fit_fixed`). These are the straight grasp / release pieces of the play, 10–112 mm of TCP travel.
   - **Grasp approach and release retreat:** an interpolating cubic through `approach_qs`, empty gripper, jaws open. Measured TCP travel: 57.9–60 mm on the cooking chains (r17chain's 6 cm approach) and 50 mm on the prep sets.

     The chain approaches are therefore 10 mm longer than the "≤ 50 mm" wording of the contact-window rule. They are exported as planned and certified.
   - **Seat lift and set-down:** an exact straight line from the approach end to `play[0]` / `play[-1]`, 4–8 mm of TCP travel.

     These are **not checked states by rule**: they are the support contact window, exactly as in r17chain and r19prep_verify. They are listed in every `recheck.json` as `unchecked_by_rule`.

     Where the gap is only round-off (< 0.1 mm, e.g. the lever), the approach end is snapped to the play state and the gap is reported.
5. **Holds:** grasp and release (0.8 s, jaws ramp 25 → 15 mm or back) and the process dwells.

**Hub edges.** Each straight segment between waypoints becomes an exact cubic, with collinear control points. Vias are stops.

**Stir.** The stored certified segments are copied unchanged into one periodic piece:
- 9 quintic spans and 1 cubic span;
- work4 keeps its stored `limit + h²` coordinate (the elbow at −160°).

## 2. The format, `r19export/1` (`results/r19/export/<name>/`)

### Files

| File | Contents |
|---|---|
| `export.json` | The neutral description (below). |
| `states.npz` | The stored states, their spline parameter and their fit tolerance, per piece (`q_k`, `u_k`, `tol_k`), for round-trip test 1. |
| `stream.csv` | 500 Hz neutral stream: `t_s`, `carriage_x_m`, `base_y_m`, `base_yaw_rad`, `q1..q6_rad`, `finger_l_m`, `finger_r_m`, `element`. 10 decimals. |
| `ur_servoj_500hz.csv` | UR writer output. |
| `fr5_servoj_deg_8ms.csv` | FR5 writer output. |
| `recheck.json` | Round-trip test 2, tied to the geometry by `geometry_md5`. |

### `export.json`

**Header and context:**
- `format`, `name`, `kind`, `arm`, `arm_name`.
- `source`: `{file, md5}`.
- `reversed`.
- `state`: the 11-value state layout `[carriage_x, base_y, base_yaw, q1..q6, finger_l, finger_r]` in m and rad.
- `joint_convention`: sim joint coordinates (Menagerie UR5e, vendor-URDF FR5). Zero and sign against the real controller must be confirmed at commissioning [E].
- `labels`: unwrap rule, the stored 2π jumps, the roadmap shift.
- `hubs.start` / `hubs.end`: the exact unwrapped states at rest. `hubs.roadmap_match` gives the distance to each hub-roadmap endpoint of the action.

**`sequence`**: an ordered list of elements. Each element is a `motion` or a `hold`.

A **`motion`** element has:
- `cls`: `free`, `contact` or `stir`. This picks the limit class of the time law.
- `contact`: what the contact window is and its measured TCP length, or null.
- `held`: the held object.
- `check`: `{scene: <spec>}`, the scene the certificate used, rebuildable from the spec; or `{rule: …}` when the piece is exempt by rule.
- `const_state`: the 11-value state. Its `base_y`, `base_yaw` and jaw values hold during the piece.
- `spline`: `{length L, periodic, spans: [...]}`. Each span is `{s0, s1, degree, knots, coef (n × 7), sq?}`.
  - **Evaluation:** `y(s) = Σ coef_i B_i,k(s)` (a clamped B-spline, scipy `BSpline(knots, coef, degree)`) for `s ∈ [s0, s1]`.
  - **`sq`:** a coordinate `j` listed in `sq: {j: [limit, sign]}` is `q_j = limit + sign · y_j(s)²`. This is exact and keeps `q_j` on its side of the limit.
  - **Periodic pieces:** use `s mod L`.
  - **Coordinates:** `[carriage_x, q1..q6]`; the other 4 values come from `const_state`.
  - **`s`** is a geometric parameter (chord length in r19smooth's scaled joint space, ≈ m of point motion), not time.
- `fit`: method, number of stored states, fit points, tolerance range, range excursion.
- `time_law`: duration, convergence, worst ratios, the limits used, and for the stir the source of the stored law.

A **`hold`** element has: `name` (grasp, release, or a dwell), `duration_s`, `state`, and `jaws_to`.

**`certificate`** records:
- the source certificate file and its md5;
- the checker;
- the rule (≤ 4 mm point bound between consecutive states, full check);
- states checked, hit and out-of-range states, and min reserves with their pairs;
- the approach certificates;
- `scene_spec` and `scene_model_md5_now` (the md5 of the checker's model XML as rebuilt today).

Only the stir certificates stored a model md5, and it matches. **A change of geometry invalidates the export; a change of timing does not.**

**Other blocks:**
- `certificate_reproduction`: the resampled state count against the certificate's.
- `fit_tolerance`, `limit_coordinates`, `segmentation` (stops, reversals, fixed pieces, dwells, keyframe indices, the r19smooth reference).
- `time_law`: method, limits with their sources, `total_s`, `stored_time_s`, the junction jump.
- `playback`.
- `geometry_md5`: covers the splines, constant states and check specs. A `recheck.json` counts only when it carries the same md5.
- `roundtrip`: `state_fit` (test 1), `limits` (test 3 on the stream), `writers` (test 3 on the written files).

### The time law: generated at export, not stored as truth

- **Method.** Each motion piece is timed rest to rest by `r19stir2_law.timelaw`. That is r19stir_cycle's closed-form TOPP-RA, plus r19smooth's erosion and W = 0.2 s moving-average filter, plus local slow-downs until every limit holds on the 2 ms grid. It includes a **per-joint jerk limit**.
- **TCP caps.** A TCP speed and rotation cap enters as a cap on ṡ², taken from FK on a 1 mm grid.
- **Holds** are inserted at rest.
- **Stir.** The stir keeps the stored from-rest law of its entry: `r19spill_cycle` / `r19stir2_retime`, J = 8000°/s³, 3 cycles from rest. Its source md5 is recorded.

| Limit | Free pieces | Contact windows | Source |
|---|---|---|---|
| Joint speed | arm datasheet 180°/s | 60°/s | [S] arms.py; R17 cap [E] |
| Joint acceleration | 1.4 rad/s² (80.2°/s²) | same | [S] [URScript `movej` default a](https://www.universal-robots.com/manuals/EN/HTML/SW5_24/Content/prod-scriptmanual/all_scripts/movej_qa14v105t0r.htm) |
| Joint jerk | 14 rad/s³ (802°/s³) | same | [E] R19_SMOOTH "full acceleration in ≥ 0.1 s"; no OEM value |
| Cart speed / acceleration / jerk | 0.25 m/s / 0.5 m/s² / 5 m/s³ | same | [E] R19_SMOOTH `fastcart`. The tip model is quasi-static (#14 open). |
| TCP speed | 0.25 m/s | 0.10 m/s | [S] ISO 10218-1 reduced speed = `movel` default v; R17 cap [E] |
| TCP rotation | 90°/s (held wok: 45°/s) | 45°/s | [E] R19_SMOOTH |
| Stir | 180°/s, 400°/s² (FR5: 800), 8000°/s³ | — | its library entry ([E] / [S] as listed there) |

The law does not evaluate:
- the jaw moment, food acceleration or cart tip-over (R19_SMOOTH found them non-binding at these caps);
- servo tracking error.

All limits are command-line options: `A_JOINT`, `J_JOINT`, `V_TCP`, `W_TCP`, `V_CART`, `A_CART`, `J_CART`, `W`.

## 3. Results per set

### 3.0 How to read the tables

- **States.** The stored states tested in round-trip test 1: play, approaches and links. A piece-boundary state counts in both pieces.
- **Pieces.** Motion pieces between mandatory stops, plus holds.
- **Fit.** The maximum state-fit error, as a point bound in mm and as a joint error in rad.
- **Re-check.** Dense states / hits, then (minimum environment reserve / minimum self reserve) in mm.
- **T.** Time-law duration against the stored time, in s. Stored times:
  - chains and prep: r17chain-style nominal (a constant speed per stored step, unlimited acceleration), including dwells, grasp / release and approaches;
  - hub: r19hub metrics (joints 60°/s, no acceleration limit, + 0.6 s);
  - stir: the stored 3-cycles-from-rest law.
- **Peaks.** Maximum joint |q̇|, |q̈|, |q⃛| in °/s, °/s², °/s³ against the limits (speed limit 60 contact / 180 free), plus cart m/s, m/s², m/s³.
- **Ratios.** The largest ratio to the limit for v / a / j, all coordinates, from finite differences on the 500 Hz stream.

### 3.1 The library's 12 verified sets (UR5e `ur5e_enc2_pgc`)

| Set (library name) | States | Pieces | Fit | Re-check | T (s) | Peaks | Ratios |
|---|---|---|---|---|---|---|---|
| wok, WOK_PLATE_RINSE spot 1 | 493 | 10 (+5) | 4.0 mm (9.5e-4 rad) | 4,446 / **0** (2.02 / 1.87) | 50.4 / 48.9 | 84, 69, 641 vs 60/180, 80, 802; cart 0.24 / 0.49 / 4.9 | 0.97 / 0.97 / 0.97 |
| wok spot 2 (plate2b) | 493 | 10 (+5) | 4.1 mm | 4,445 / **0** (2.02 / 1.87) | 50.3 / 48.9 | 84, 69, 641; cart 0.25 / 0.48 / 4.9 | 0.98 / 0.97 / 0.97 |
| lever, FAUCET_OPEN | 30 | 3 (+2) | 0.0016 mm (6.9e-7 rad) | 152 / **0** (4.88 / 2.0) | 6.2 / 3.5 | 49, 76, 715 vs 60, 80, 802; cart 0.10 / 0.27 / 2.5 | 0.81 / 0.95 / 0.89 |
| lever reversed, FAUCET_CLOSE | 30 | 3 (+2) | 0.0016 mm | 152 / **0** (2.12 / 2.0) | 6.2 / 3.5 | 49, 76, 711 | 0.81 / 0.95 / 0.89 |
| lid, LID_OFF_pot | 225 | 7 (+2) | 3.2 mm (6.7e-4 rad) | 2,464 / **0** (1.0 / 1.11) | 23.4 / 20.2 | 79, 79, 780; cart 0.24 / 0.49 / 4.5 | 0.98 / 0.98 / 0.97 |
| lid reversed, LID_ON_pot | 225 | 7 (+2) | 3.2 mm | 2,464 / **0** (1.0 / 1.11) | 23.2 / 20.2 | 79, 79, 775 | 0.98 / 0.98 / 0.97 |
| spatula, SPATULA_FETCH | 259 | 4 (+1) | 3.3 mm (7.1e-4 rad) | 2,630 / **0** (2.02 / 2.0) | 22.8 / 26.9 | 46, 64, 790; cart 0.25 / 0.49 / 4.9 | 1.00 / 0.97 / 0.99 |
| spatula reversed, SPATULA_STOW | 259 | 4 (+1) | 3.3 mm | 2,630 / **0** (2.0 / 2.0) | 23.1 / 26.9 | 46, 64, 790 | 1.00 / 0.98 / 0.98 |
| spider, SPIDER_FETCH + SCOOP_pot + DUMP_plate + STOW | 539 | 10 (+3) | 1.1 mm (4.3e-4 rad) | 4,244 / **0** (1.12 / 0.78) | 51.0 / 52.6 | 90, 73, 783; cart 0.25 / 0.39 / 4.7 | 1.00 / 0.91 / 0.98 |
| CARRIER_IN / OUT | — | — | — | — | — | — | not exported: no carrier path for this arm |

Notes:
- The reversed sets are the same geometry run backwards (R19_MOTION_LIBRARY rule 4). They were re-checked anyway and give the same states.
- The lever's minimum reserve differs between directions (4.88 / 2.12 mm) only because the dense samples fall elsewhere. The reserve is a sampled lower bound; the certificate gives 5.98 mm.
- **Composition holds by construction [M].** The start and end hubs of all 6 chains are bit-identical (≤ 4·10⁻¹⁶) to the hub-roadmap endpoint vectors and to the first or last state of their 22 exported edges. Examples:
  - the wok's start and end = WOK = the start of WOK__H_WOK / H_SINK / H_POT and the end of LEV_O__WOK;
  - the lever's start = LEV_C, its end = LEV_O.

### 3.2 Stir cycle (adopted default)

| Set | States | Pieces | Fit | Re-check | T (s) | Peaks | Ratios |
|---|---|---|---|---|---|---|---|
| `lib_stir_cycle_ur5e_enc2_pgc_short01_u06_j8000` | 4,547 | 1 periodic (10 spans) | 1.8e-11 mm (5e-15 rad) | 4,481 / **0** (2.0 / 2.0, plume 29.04) | 42.5 / 42.454 (3 cycles from rest; period 14.03 s) | 134, 396, 7555 vs 180, 400, 8000 | 0.75 / 0.99 / 0.94 |

- The certified states lie on the stored geometry to 5·10⁻¹⁵ rad. The parameter of each state is found by nearest point plus Gauss–Newton per segment.
- The stream starts and ends at rest at H_stir0.
- The spatula → stir hand-off (`lib_stir_join_*`) is **not exported**; that kind is not implemented here. It is already a certified B-spline, so adding it would follow the stir path.

### 3.3 Hub edges (UR5e, union scene, empty gripper)

All 22 edges: fit < 1·10⁻¹¹ mm (exact lines). Re-check: 0 hits each, 32,278 states in total.

| Edge | States | Pieces | Re-check (env / self mm) | T (s) | Joint peaks v, a, j | Ratios |
|---|---|---|---|---|---|---|
| H_SINK__H_WOK | 217 | 1 | 215 / 0 (58.4 / 5.6) | 4.5 / 4.0 | cart only: 0.25 m/s, 0.39 m/s², 2.5 m/s³ | 1.00 / 0.77 / 0.50 |
| H_SPAT__H_SINK | 209 | 1 | 210 / 0 (58.4 / 5.6) | 4.3 / 3.8 | cart only | 1.00 / 0.77 / 0.50 |
| H_WOK__H_POT | 248 | 1 | 242 / 0 (58.4 / 5.6) | 4.8 / 4.3 | cart only | 1.00 / 0.77 / 0.50 |
| LEV_C__H_SINK | 1,563 | 1 | 1,458 / 0 (2.59 / 2.0) | 9.3 / 3.5 | 41, 63, 430 | 0.23 / 0.78 / 0.54 |
| LEV_C__H_SPAT | 1,763 | 1 | 1,659 / 0 (2.04 / 2.0) | 10.4 / 3.8 | 32, 58, 393 | 0.59 / 0.73 / 0.49 |
| LEV_C__H_WOK | 1,767 | 1 | 1,674 / 0 (2.22 / 2.0) | 9.1 / 4.0 | 45, 57, 372 | 0.89 / 0.70 / 0.46 |
| LEV_O__H_SINK | 1,519 | 2 | 1,398 / 0 (2.76 / 2.0) | 10.0 / 4.3 | 51, 66, 553 | 0.28 / 0.83 / 0.69 |
| LEV_O__H_SPAT | 1,721 | 2 | 1,607 / 0 (2.75 / 2.0) | 11.2 / 4.4 | 39, 62, 446 | 0.68 / 0.77 / 0.56 |
| LEV_O__H_WOK | 1,739 | 2 | 1,621 / 0 (2.76 / 2.0) | 9.9 / 4.7 | 53, 61, 393 | 0.98 / 0.76 / 0.49 |
| LEV_O__WOK | 2,582 | 3 | 2,441 / 0 (2.02 / 2.0) | 15.6 / 6.7 | 55, 66, 467 | 0.51 / 0.83 / 0.58 |
| LID_POT__H_POT | 1,774 | 1 | 1,670 / 0 (19.5 / 2.0) | 10.8 / 4.5 | 30, 56, 399 | 0.16 / 0.70 / 0.50 |
| LID_POT__H_WOK | 1,877 | 1 | 1,800 / 0 (19.5 / 2.0) | 11.5 / 4.5 | 34, 59, 399 | 0.41 / 0.74 / 0.50 |
| LID_RACK__H_POT | 2,021 | 1 | 1,915 / 0 (2.06 / 1.43) | 11.2 / 5.0 | 31, 56, 400 | 0.17 / 0.70 / 0.50 |
| LID_RACK__H_WOK | 2,245 | 1 | 2,150 / 0 (2.0 / 1.43) | 12.5 / 5.2 | 34, 59, 399 | 0.60 / 0.73 / 0.50 |
| SPAT__H_SINK | 1,390 | 1 | 1,259 / 0 (23.4 / 2.0) | 6.5 / 3.8 | 56, 58, 388 | 0.99 / 0.72 / 0.48 |
| SPAT__H_SPAT | 1,171 | 1 | 1,046 / 0 (23.7 / 2.0) | 6.3 / 3.6 | 47, 62, 389 | 0.26 / 0.78 / 0.48 |
| SPAT__LEV_C | 2,865 | 2 | 2,709 / 0 (2.48 / 2.0) | 15.9 / 6.5 | 56, 61, 426 | 0.50 / 0.77 / 0.53 |
| SPIDER__H_POT | 2,150 | 1 | 2,015 / 0 (2.01 / 1.31) | 7.4 / 4.8 | 61, 67, 394 | 0.34 / 0.84 / 0.49 |
| SPIDER__H_WOK | 2,364 | 1 | 2,263 / 0 (2.0 / 1.31) | 9.1 / 4.8 | 43, 63, 393 | 0.64 / 0.79 / 0.49 |
| WOK__H_POT | 1,191 | 1 | 1,060 / 0 (2.04 / 2.0) | 5.9 / 4.3 | 40, 61, 382 | 1.00 / 0.77 / 0.48 |
| WOK__H_SINK | 1,177 | 1 | 1,047 / 0 (2.0 / 2.0) | 7.0 / 4.0 | 30, 57, 384 | 0.70 / 0.71 / 0.48 |
| WOK__H_WOK | 913 | 1 | 819 / 0 (2.1 / 2.0) | 5.2 / 3.0 | 51, 66, 464 | 0.28 / 0.82 / 0.58 |

- The joint limits are 180°/s, 80°/s², 802°/s³.
- The edges are exported in their stored direction. The opposite direction is `REVERSE=1`: the same states, no new check needed.
- **Why the edges are slower than stored:** the 0.25 m/s TCP cap, which binds where the arm swings from a tucked posture.
  - **Without the cap** (`V_TCP=1.0 W_TCP=360`), a test run, not kept [M]:

    | Edge | Export without the cap | Stored |
    |---|---|---|
    | WOK__H_WOK | 3.7 s | 3.0 s |
    | LEV_C__H_SINK | 4.3 s | 3.5 s |
    | LID_RACK__H_WOK | 6.2 s | 5.2 s |

  - **What the cap is for:** 0.25 m/s is the collaborative reduced speed. Whether empty-hand transits may run faster is a safety-policy choice, not a geometry question.

### 3.4 Prep sets (UR5e)

| Set | States | Pieces | Fit | Re-check | T (s) | Peaks | Ratios |
|---|---|---|---|---|---|---|---|
| tomato (`chain_tomato_full`) | 322 | 10 (+5) | 0.69 mm | 2,644 / **0** (1.0 / 1.44) | 44.2 / 36.5 | 81, 77, 801; cart 0.25 / 0.41 / 4.8 | 1.00 / 0.96 / 1.00 |
| carrot | 381 | 9 (+5) | 0.97 mm | 3,886 / **0** (2.03 / 2.0) | 54.4 / 47.0 | 80, 71, 782 | 1.00 / 0.96 / 0.98 |
| press | 36 | 4 (+2) | 3e-12 mm | 216 / **0** (1.0 / 2.93) | 7.1 / 4.6 | 11, 32, 396 | 0.28 / 0.42 / 0.50 |
| bascarrot | 142 | 6 (+2) | 0.76 mm | 1,762 / **0** (3.0 / 1.55) | 21.5 / 14.4 | 67, 71, 786 | 1.00 / 0.89 / 0.98 |
| ctray | 432 | 8 (+3) | 0.93 mm | 3,149 / **0** (2.0 / 2.01) | 39.9 / 38.1 | 49, 74, 777 | 0.99 / 0.98 / 0.97 |
| soak | 129 | 9 (+4) | 0.95 mm | 1,614 / **0** (2.04 / 2.01) | 34.3 / 26.9 | 33, 67, 758 | 0.45 / 0.83 / 0.97 |
| tubempty | 300 | 10 (+3) | 0.94 mm | 4,553 / **0** (2.05 / 2.0) | 36.2 / 23.9 | 59, 70, 780 | 0.99 / 0.88 / 0.97 |
| tubfill (`t15fin`, the adopted one; `tubfill_full` is refused) | 212 | 8 (+3) | 0.92 mm | 2,790 / **0** (2.05 / 2.0) | 53.5 / 45.3 | 73, 73, 680 | 0.99 / 0.91 / 0.97 |
| basket (`y20p30`, the adopted one; `basket_full` has no play) | 253 | 15 (+6) | 1.0 mm | 3,449 / **0** (2.01 / 2.0) | 57.5 / 34.6 | 52, 75, 783 | 0.98 / 0.94 / 0.98 |

- The prep sets have no per-state reserves, so the fit tolerance is uniform: clip(0.5 × the set's minimum reserve, 0.5, 8) mm, i.e. 0.5–1.0 mm.
- Their certificate is `r19prep_verify.py` in the scene recorded with the set. The folded T2L cradle and the pot-zone layer of `r19prep5_verify.py` are **not** in these scenes, because the certificates being reproduced did not have them either.
- The times are longer than the nominal mainly for three reasons:
  - the 9–12 s of rinse and shake dwells;
  - the shakes, which become stop-and-go reversals;
  - the jerk and acceleration ramps that the nominal law does not have.

### 3.5 FR5 (`fr5_j6_pgc_sp20`)

| Set | States | Pieces | Fit | Re-check | T (s) | Peaks | Ratios |
|---|---|---|---|---|---|---|---|
| lever | 30 | 3 (+2) | 1e-12 mm | 168 / **0** (4.88 / 2.05) | 6.2 / 3.6 | 49, 79, 713 vs 60, 80, 802 | 0.82 / 0.98 / 0.89 |
| spatula | 255 | 4 (+1) | 3.5 mm | 2,306 / **0** (2.03 / 2.0) | 20.4 / 26.6 | 55, 67, 698 | 1.00 / 0.98 / 0.97 |
| wok (py .17) | 487 | 10 (+5) | 1.4 mm | 4,559 / **0** (2.07 / 2.0) | 51.2 / 49.1 | 95, 75, 724 | 1.00 / 0.94 / 0.99 |
| wok spot 2 (py .17) | 487 | 10 (+5) | 1.4 mm | 4,553 / **0** (2.07 / 2.0) | 51.1 / 49.1 | 95, 75, 727 | 1.00 / 0.94 / 0.99 |
| tomato prep (`fr5yfull`, adopted) | 326 | 10 (+5) | 1.0 mm | 3,297 / **0** (1.0 / 2.0) | 45.3 / 38.5 | 107, 79, 797 | 1.00 / 0.98 / 0.99 |
| stir cycle (`short01_u06_j8000`) | 4,039 | 1 | 1.9e-11 mm | 3,968 / **0** (2.0 / 2.0) | 40.1 / 40.094 | 163, 693, 7298 vs 180, 800, 8000 | 0.90 / 0.87 / 0.91 |

- No FR5 hub roadmap exists, so the FR5 chains keep their unwrapped labels.
- The FR5 lid and spider have no passing chain and are not exported.

### 3.6 Fit tolerance against time (wok, [M], not kept)

A uniform 0.5 mm tolerance (`TMAX=.0005`) gives a state fit of 0.46 mm and a wok time of 53.9 s, against 50.4 s at the default (≤ 4.1 mm). This was not re-checked; it is shown only as the trade-off.

## 4. Writers (`r19export_writers.py`)

Both writers read only `stream.csv` and `export.json`. They then re-read their own output and measure v / a / j by finite differences on the file's own grid.

**UR: `ur_servoj_500hz.csv`. Done.**
- Contents: `t_s, q1..q6 (rad)`, one row per 2 ms. That is the period of `servoj(q, a, v, t=0.002, lookahead_time, gain)` streamed over RTDE on an e-Series controller ([UR script manual](https://docs.universal-robots.com/PolyScopeX_SDK_Documentation/build/SDK-v0.13/_static/pdf/scriptManualG5.pdf)) [S].
- The cart is not a UR joint. Its column is in `stream.csv` on the same clock.
- Re-measured from the file: grid exact. Peaks equal the stream's; for example the wok gives 84.2°/s, 68.9°/s², 641°/s³, all ratios ≤ 1.
- At 10 decimals, the third-difference jerk from the file differs from the stream's by < 0.1 %.

**FR5: `fr5_servoj_deg_8ms.csv`. Done [S].**
- Contents: `t_s, j1..j6 (deg)`, every 4th stream row (8 ms).
- The SDK's `ServoJ(joint_pos [deg], axisPos, acc, vel, cmdT [s], filterT, gain)` is fed between `ServoMoveStart` / `ServoMoveEnd`. The SDK example streams with `cmdT = 0.008` ([Fairino SDK, motion](https://fairino-doc-en.readthedocs.io/latest/SDKManual/CPPRobotMovement.html)).
- The page prints the recommended cmdT range as "[0.001~0.0016]", which looks like a typo for 0.016 [E].
- Re-measured from the file: grid exact, all ratios ≤ 1 (wok: 94.8°/s, 74.9°/s², 712°/s³).

**FR5 on-controller trajectory file: not written [E].**
- The SDK has `TrajectoryJUpLoad(filePath)`, `LoadTrajectoryJ(name, ovl, opt)`, `MoveTrajectoryJ()` and `GetTrajectoryStartPose()`, with files in `/fruser/traj/` ([Fairino SDK, trajectory recurrence](https://fairino-doc-en.readthedocs.io/latest/SDKManual/CPPRobotTrajectoryRecurrence.html)) [S].
- None of the pages I reached publishes the file's content format: the SDK and the teach-pendant / node-editor manual pages, which say only "a discrete trajectory point file in a fixed format" (TPD records at 2 / 4 / 8 ms). Neither do the vendor SDK example files.
- A third-party GitHub tool writes a header line plus `joints, pose, …` rows, but that format is unofficial and unverified, so it is not used.
- **Next step:** export one TPD recording from a real FR5 (or ask Fairino for the template), then add a writer that converts `fr5_servoj_deg_8ms.csv`. The joint values are already in the vendor's degrees.

## 5. Commands (from `robot_rail/sim/r10/claude`, `PY=robot_v5/board/work/t01/.venv/Scripts/python.exe`)

Every command was run here and took < 5 min on this shared machine:
- an export takes 2–25 s;
- a re-check takes 50–190 s per batch of about 3–8k states with 26 workers.

**No controller lane is needed.**

To re-export after the #42 re-plan, give the new result files to the same commands:

```
# export (one set per command)
$PY r19export.py export FILE=results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json
$PY r19export.py export FILE=results/r17/chain_lever_s+1_final_ur5e_enc2_pgc.json [REVERSE=1]
$PY r19export.py export FILE=results/r19/hub_py.15_ur5e_enc2_pgc/edge_WOK__H_WOK.json
$PY r19export.py export FILE=results/r19/stir/lib_stir_cycle_ur5e_enc2_pgc_short01_u06_j8000.json
$PY r19export.py export FILE=results/r19/prep/chain_tomato_full_ur5e_enc2_pgc.json
$PY r19export.py export FILE=results/r17/chain_wok_s-1_final_py.17_fr5_j6_pgc_sp20.json
# dense re-check (round trip 2); several exports per command share one pool per scene, keep each batch <= ~7k states
$PY r19export.py recheck NAME=chain_wok_s-1_final_py.15_ur5e_enc2_pgc,chain_lid_s-1_final_ur5e_enc2_pgc WORKERS=26
# repair round if a re-check has hits (r19smooth's rule: 1/4 tolerance near the hits), then re-check again
$PY r19export.py export FILE=<same file> REFIT=1
# the summary table
$PY r19export.py report                  # -> results/r19/export/summary.json
# writers alone (from an export folder)
$PY r19export_writers.py DIR=results/r19/export/<name> [WHICH=ur|fr5] [FR5_PERIOD=.008]
```

The batches actually run are visible in each `recheck.json` (`elapsed_s_command`).

## 6. What is and is not shown

**Shown [M]:**
- For every exported set:
  - the exported spline reproduces every stored state within the stated tolerance;
  - the spline itself, sampled at ≤ 4 mm, passes the certificate's own checker and scene with 0 hits;
  - the generated time law keeps joint and cart speed, acceleration and jerk, and the TCP caps, inside the limits on the 500 Hz stream and in the written files.
- The chain hubs equal the roadmap edge endpoints exactly.

**Not shown:**
- **Seat lift and set-down links (4–8 mm)** are not checked states, by the same rule as r17chain and r19prep_verify (support contact window). They are listed per set in `recheck.json`.
- **The scene is the certificate's, not necessarily today's full layout.** Each set is checked in the scene its certificate used, so a layout change made after a certificate (e.g. the T2L cradle for UR prep sets, the pot-zone layer for chains) is in the export only if it was in that certificate.
- **Real-controller effects:**
  - servo tracking error against reserves of 1–2 mm (lid in the rack 1.0 mm, spider self 0.78 mm);
  - cart and arm synchronization;
  - the joint zero and sign convention against the real controllers [E].
- **Dynamics:** jaw moment, food slosh and cart tip-over along these laws. R19_SMOOTH found them non-binding at the same caps; they were not re-evaluated here.
- **The jerk limits are assumptions [E]:** 14 rad/s³ for the chains, 8000°/s³ for the stir. No OEM value is published.
- **Not exported:**
  - CARRIER_IN / OUT (no current-arm path);
  - the stir join;
  - the FR5 lid and spider (no passing chain);
  - the remaining FR5 prep sets (the exporter takes them as they are).
- **Disk.** The CSV streams are about 4 MB per minute of motion; `results/r19/export/` is 129 MB for 47 sets. Exclude `*.csv` from a GitHub sync if needed: the exporter regenerates them.

## 7. Files (all new)

- `r19export.py`: export, recheck, report.
- `r19export_writers.py`: UR and FR5 writers.
- `R19_EXPORT.md`: this file.
- `results/r19/export/<name>/`, one folder per set (47): `export.json`, `states.npz`, `stream.csv`, `ur_servoj_500hz.csv` or `fr5_servoj_deg_8ms.csv`, `recheck.json`.
- `results/r19/export/summary.json`.
- Read only, unchanged (md5 before = after):
  - `r19enc_check.py`, `r19enc_adopt.py`, `r19smooth.py`, `r19stir2_law.py`, `r19stir_cycle.py`, `r19hub.py`;
  - `r19prep_verify.py`, `r19prep4_verify.py`, `r19prep5_verify.py`;
  - `r17chain.py`, `arms.py`, `checker.py`, `scene.py`, `chain.py`, `kitchen16.py`.
