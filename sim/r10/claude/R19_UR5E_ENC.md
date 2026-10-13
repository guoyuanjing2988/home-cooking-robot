# R19 #12: the UR5e collision geoms do not enclose the real arm — re-check with `ARM=ur5e_enc`

2026-10-13. No gap, step size or limit was loosened. Default `ur5e` is unchanged (§2.4). No git or GitHub action.

## 0. Answer first

`ur5e_enc` is the same UR5e (kinematics, masses, limits, speeds, torque envelope) with collision geoms that provably
contain every point of the Menagerie visual meshes (max protrusion −0.05 mm on every link; the Menagerie geoms: up to
26.5 mm). Every state of the stored UR5e paths was re-checked with it at ≤ 4 mm point-bound spacing (full checker,
10 / 5 / 0 mm gaps), next to the old geometry on the very same states.

| Path | States checked | UR5e (old geoms) | `ur5e_enc` | Hit states | Pairs that hit (`ur5e_enc`) | Real arm surface at the worst hit state (§4) |
|---|---|---|---|---|---|---|
| wok final | 4,588 | pass | **fail** | 342 | elbow housing (R_geom_16) – `r15_plate` 158, – `sink_front_rim` 184 | **plate 7.5 mm: violates 10 mm**; sink rim 21.9 mm (enclosure bloat) |
| wok plate 2 (r18plate2b) | 4,561 | pass | **fail** | 417 | R_geom_16 – `r17_plate2` 158, – `sink_front_rim` 157, – `r15_plate` 102 | **dish at x .43: 7.5 mm, violates**; others 19.8–21.9 mm (bloat) |
| lever final | 128 | pass | pass | 0 | — | — |
| lid final | 2,410 | pass | **fail** | 118 | J2 housing (R_geom_10) – `r16_spider_block` 96, – `r14_hood` 22 | 24.7 / 24.3 mm: bloat only |
| spider final | 4,335 | pass | **fail** | 342 | R_geom_16 – `r14_upper_over_hood` 295; R_geom_10 – `r14_hood` 210; self `R_finger_minus` – R_geom_10 45 | 12.5 / 13.6 mm (bloat); finger–upper arm 1.2 mm sampled (undecided, §4) |
| spatula r18roll-1.15_.30 | 2,642 | pass | pass | 0 | — | — |
| stir (stored cycle, 5 strokes) | 4,822 | pass | pass | 0 | — (plume ≥ 25.8 mm both) | — |
| hub, 22 edges | 33,761 | 22 pass | **12 pass, 10 fail** | 2–45 per edge | wrist-2 housing (R_geom_25) – `r07_closed_door_1_0` (8 edges); R_geom_10 – `r14_hood` (2 edges) | **4 LEV_O edges: wrist 1 at 8.0–8.1 mm, violates**; other 6 edges 14.6–17.9 mm (bloat) |

Min reserve, old → new (worst state of the path; reserve = lower-bound clearance − required gap):

| Path | arm–environment | gripper/held–environment (unchanged parts) | self |
|---|---|---|---|
| wok | 2.02 → **−10.0** (R_geom_16 / plate) | 4.0 → 4.0 | 2.0 → 2.0 |
| wok plate 2 | 2.02 → **−10.0** (R_geom_16 / dish at .43) | 4.0 → 4.0 | 2.0 → 2.0 |
| lever | 19.46 → 10.62 (wrist 1 / upper cabinet) | 5.98 → 5.98 | 2.08 → 2.02 |
| lid | 2.02 → **−5.04** (R_geom_10 / spider block) | 1.0 → 1.0 | 2.0 → 2.0 |
| spider | 2.03 → **−10.0** (R_geom_16 / upper cabinet over the hood) | 2.05 → 2.05 | 2.0 → **0.0** (finger / R_geom_10, intersecting) |
| spatula | 77.9 → 43.1 | 2.04 → 2.04 | 2.0 → 2.0 |
| stir | 22.7 → 22.1 (forearm / hood) | 2.0 → 2.0 | 2.0 → 2.0 |
| hub edges | 2.03 … 210 → **−8.08** … 195 (per edge in `results/r19/enc/summary.json`) | unchanged | 2.0–3.9 → 2.0–2.4 |

What it means:
- **Real violations of the 10 mm rule** (the Menagerie mesh itself is closer than 10 mm; contact is not reached):
  1. **wok final and wok plate 2**: the elbow end of the **upper arm** comes **7.5 mm** from the plate (`r15_plate`; in the
     plate-2 scene the waiting dish `r17_plate2` at x .43) at the start / end pose of the wok action (stored state 0
     and the last states).
  2. **hub edges from LEV_O** (`LEV_O__H_SPAT`, `LEV_O__WOK`, `LEV_O__H_WOK`, `LEV_O__H_SINK`, all via the retreat
     (0, −0.15, 0)): **wrist 1** comes **8.0–8.1 mm** from the closed cabinet door `r07_closed_door_1_0`.
- **Spider, self**: the finger (`R_finger_minus`) intersects the fitted J2 housing in 41 states; the sampled mesh gap is
  1.2 mm, which is inside the 1.7 mm sampling cover — no real contact can be claimed or excluded from the samples.
- **Everything else that fails is enclosure bloat**: the fitted cylinders have sharp rims where the real housings end in
  domed / rounded caps, so in those spots the model is 6–20 mm outside the real surface (lid, spider env pairs, wok sink
  rim, 6 hub edges). The checker sees the model, so these paths still FAIL with `ur5e_enc`; the mesh diagnostic only
  says that the real arm is clear there. A tighter fit (stepped end caps) would turn these into passes, but it is not made.
- The UR5e path that "passed" with the Menagerie capsules is therefore **not proven** for the real arm in 4 of 6 chains
  and 10 of 22 hub edges. Lever, spatula and the stir cycle pass with the enclosing geometry.

## 1. The `ur5e_enc` model

### 1.1 What it is
- `arms.py`: new id `ur5e_enc` (`ARM=ur5e_enc` on any script). For it, `swap()` calls `enclose()`: the UR5e bodies,
  joints, inertials, site and gripper stay exactly as in `models/base.xml`; only the collision geoms change:
  - `R_geom_5 … R_geom_28` get the fitted type / pos / quat / size (same bodies, same axes);
  - 4 cylinders are added (`R_geom_enc_*`, same contact settings: contype 2, conaffinity 3, margin .01, group 3).
- Speeds 180°/s, payload 5 kg at 0.35 m and the envelope file `assets/envelope_-20.json` are the UR5e's
  (`envelope_file()` returns the UR5e file for `ur5e_enc`).
- `r17chain.py`: the checked R16 walk state (UR5e joint values) is used as a start candidate for `ur5e_enc` too
  (same arm; the state is re-checked with the new geoms like every candidate). One line.
- Outputs get the suffix `_ur5e_enc`, so no UR5e result is overwritten.

### 1.2 The fitted geoms (`r19/arm_ur5e_enc.json`, made by `r19ur5e_encfit.py`)

| Geom | Body | Menagerie | `ur5e_enc` |
|---|---|---|---|
| R_geom_5 | shoulder | capsule r 60.0, half-length 60.0 | cylinder r 60.3, length 135.5 |
| R_geom_10 | upper arm (J2 housing) | capsule r 60.0, half 60.0 | cylinder r 61.2, length 135.3 |
| R_geom_11 | upper arm tube | capsule r 50.0, half 200 | capsule r 49.5, same segment |
| R_geom_16 | forearm (elbow housing, covers the upper arm's elbow end too) | capsule r 55.0, half 60 | cylinder r 65.8, length 249.7 |
| R_geom_17 | forearm tube | capsule r 38.0, half 190 | capsule r 38.5, same segment |
| R_geom_21 | wrist 1 | capsule r 40.0, half 70 | cylinder r 39.7, length 168.8 |
| R_geom_25 | wrist 2 (covers wrist 1's wrist-2 housing) | capsule r 40.0, half 60 | cylinder r 40.4, length 141.4 |
| R_geom_26 | wrist 2 (wrist-3 housing) | capsule r 40.0, half 40 | cylinder r 40.4, length 117.9 |
| R_geom_28 | wrist 3 | cylinder r 40.0, half 20 | cylinder r 43.6, length 38.0 |
| R_geom_enc_ua_neck_s / _e | upper arm | — | cylinders r 58.5 / 58.2 (tube-to-housing necks) |
| R_geom_enc_fa_neck_e | forearm | — | cylinder r 50.9 |
| R_geom_enc_sh_j2 | shoulder | — | cylinder r 59.3 (the shoulder's own part of the J2 housing) |

Millimetres. Labels: axes, bodies and the meshes are Menagerie [M]; sizes are fitted here [E].

How it was fitted (details in the script docstring):
- **Housings → cylinders, tubes → capsules**, on the Menagerie axes, as `r19arm_fit.py` does for FR5 / CS66.
- **Coaxial neighbours.** Like Menagerie, a housing geom of the neighbouring link on the shared joint axis may cover a
  link (rotation-invariant, checked to 1e-9).
  - Exception: the upper arm's R_geom_10 may not cover the shoulder. That part is a cylinder on the shoulder body,
    because the shoulder sits on the base (1 mm apart). A first fit put it on the upper arm, and MuJoCo then reported
    upper-arm/base contacts at −0.4 mm (the upper arm and the base are not adjacent, so they are checked).
- **Start sizes** are read off the mesh profiles. The fit then:
  1. grows the primitives (each outside point goes to the nearest primitive);
  2. shrinks the slack;
  3. runs a volume-reducing local search.
- **Enclosure is proven, not sampled.** A triangle is certified when one convex primitive holds its 3 corners, or when
  every corner is inside the union by more than (longest edge)/√3. Otherwise it is split, down to 1/2^10 of its edges.
  All 116,945 triangles of the 6 links are certified. Radii and cylinder ends get +0.05 mm.
- Run time: 3.7 min (`python r19ur5e_encfit.py`).

### 1.3 Enclosure verification (the `r19ur5e_enclose.py` measurement, in the sim model)
`python r19enc_check.py enclose N=200` → `results/r19/enc/enclose.json`.
- Setup: the Menagerie visual meshes are placed in the sim's `R_arm_*` bodies (body frames asserted equal) of
  `models/base.xml` + `arms.swap`.
- Measured: the max protrusion of any vertex outside the union of all arm capsule/cylinder geoms, over 200 configurations.

| mm | shoulder | upper arm | forearm | wrist 1 | wrist 2 | wrist 3 |
|---|---|---|---|---|---|---|
| `ur5e` (Menagerie geoms) | 14.13 | 26.49 | 11.50 | 9.14 | 9.33 | 3.56 |
| `ur5e_enc` | **−0.05** | **−0.05** | **−0.05** | **−0.05** | **−0.05** | **−0.05** |

The `ur5e` row reproduces `r19ur5e_enclose.py` exactly.

### 1.4 Tightness (how far the model is outside the real arm)
- Radii are within 0–1.2 mm of the profile radii read off the mesh, except:
  - elbow housing R_geom_16: +4.6 mm;
  - wrist 3 R_geom_28: +3.6 mm (a 10 mm wide bump on the wrist-3 cover);
  - the upper-arm tube capsule: 49.5 mm over a 46 mm tube (it also holds the flared tube ends).
- The housing ends are worse. The real ends are domed: J2 housing r 60.6 → 53.3 mm over the last 10 mm. The cylinders
  are not, so near a housing face the model can be well outside the mesh. Measured in §4: 6–20 mm at the worst spots
  found (J2 housing face, elbow housing faces, wrist-2 housing).
- Compared with Menagerie, the model is **not a superset**:
  - the Menagerie capsule caps reached further along the axis;
  - the cylinders reach further at the rims.

  So a few reserves went up (e.g. the hub tuck edges H_WOK–H_POT: arm–environment 90.8 → 133.1 mm).

### 1.5 Self-collision
`python r19enc_check.py self N=2000` → `results/r19/enc/self_random.json`. Setup: random arm poses in the lid scene;
the checker's self rule (non-adjacent robot parts, MuJoCo contact distance < 0).

| Arm | Poses with a self contact |
|---|---|
| UR5e | 38.3 % |
| `ur5e_enc` | 38.7 % |

No pair is in contact in every pose; the top pairs are the same (forearm / gripper housing).

### 1.6 Default `ur5e` unchanged
With the original `arms.py` (`arms.py.bak_r19enc`) and the new one, for the wok, lid and spatula scenes:
- the compiled scene XML (md5) is identical;
- the full check of a mid-path state is identical;
- the envelope file is identical.

The UR5e column of every re-check below reproduces the earlier baselines (`R19_SMOOTH.md`: wok 2.02, spatula 2.04,
lever 5.98, lid 1.0, spider 2.03 mm).

## 2. What was checked (re-check method)
`python r19enc_check.py recheck SET=<set>` → `results/r19/enc/<set>.json`. Each set is checked with **both** arms on
identical states.

**States.**
- The stored states are unwrapped (2π label jumps in columns 3:9 removed).
- They are joined joint-linearly and cut so that `point_bound.segment_bound` between consecutive states is ≤ 4 mm. The
  cut uses the `ur5e_enc` model (the larger bound); the max step bound is 3.84–4.00 mm in every path.
- Count: 470 stored wok states → 4,588 checked; the stir's 1,120 → 4,822; the hub's stored states were already
  ≤ 4 mm and stay 33,761.

**Checker.**
- `Checker.check(q, full=True, mass=0.)` on every state: MuJoCo contacts plus the GJK lower-bound certificate
  (`distance.Bounds`), and joint ranges.
- Gaps: 10 mm robot–environment, 5 mm gripper/held–environment, 0 mm self (non-adjacent robot parts, exactly the
  checker's rule).
- As in the `r19smooth.py` baseline, loads, cart floor and tip-over are not part of the collision verdict; they do not
  depend on the collision geoms.

**Hit classification.** Every hit pair is re-measured with the exact convex bound (`Bounds.pair`):
- **real** = the upper bound is below the required gap, or the two intersect;
- **artefact** = the lower bound clears the gap, and only MuJoCo's cylinder distance was short (`R19_ARM_SWAP.md` §7).

All `ur5e_enc` hits are real for the geoms except 4 spider self states.

**Scenes.**
- Chains: as `r19smooth.setup`, i.e. the R18b layout (spatula at (−1.15, .30), flipped). The plate-2 chain has a dish
  waiting at x .43, as `r17chain PLATE2=.43`.
- Stir: as `r19stir_save.py SCENE=r17`, with the jaw sign of its passing attempt and its plume rule (arm geoms must
  stay outside the r 0.20 m plume cylinder).
- Hub edges: `r19hub.py`'s union scene.
- R11 mesh rule: the tool-side boxes are 8-vertex box meshes in every scene (`r19smooth.py` MESHHELD), for both arms
  alike. The original hub and stir checks used the stock boxes, which gives more conservative contact distances.

Run times (24 workers): wok 128 s, plate 2 130 s, spider 77 s, stir 128 s, lid 59 s, spatula 53 s, lever 12 s, the
4 hub lanes 145–153 s each.

## 3. Failing paths: link and fixture

| Path | Link (geom) | Fixture | Stored states | Min gap (model) | Real mesh |
|---|---|---|---|---|---|
| wok final | upper arm, elbow end (R_geom_16) | `r15_plate` | 0–469 (start/end pose and on the way) | 0 (touch) | **7.5 mm** |
| wok final | upper arm, elbow end (R_geom_16) | `sink_front_rim` | 91–375 (rinse) | 4.5 | 21.9 |
| wok plate 2 | upper arm, elbow end (R_geom_16) | `r17_plate2` (dish at .43) / `sink_front_rim` / `r15_plate` | 0–469 | 0 / 4.5 / 1.1 | **7.5** / 21.9 / 19.8 |
| lid | upper arm, J2 housing face (R_geom_10) | `r16_spider_block` (180–185) / `r14_hood` (0–2.5) | | 5.0 / 9.3 | 24.7 / 24.3 |
| spider | upper arm, elbow end (R_geom_16) / J2 housing (R_geom_10) | `r14_upper_over_hood` / `r14_hood` | 0–515 | 0 / 7.2 | 12.5 / 13.6 |
| spider | finger `R_finger_minus` vs upper arm J2 housing (self) | — | 292–296 | intersect | 1.2 (undecided) |
| hub LEV_O__H_SPAT, LEV_O__WOK, LEV_O__H_WOK, LEV_O__H_SINK | wrist 1 (R_geom_25, wrist-2 housing) | `r07_closed_door_1_0` | 241–288 | 1.9 | **8.0–8.1** |
| hub SPAT__LEV_C, LEV_C__H_WOK, LEV_C__H_SINK, LEV_C__H_SPAT | wrist 1 (R_geom_25) | `r07_closed_door_1_0` | about 20 states each | 8.4 | 14.6 |
| hub SPIDER__H_POT, SPIDER__H_WOK | upper arm (R_geom_10) | `r14_hood` | 0–1 | 9.96 | 17.9 |

"Real mesh" = `python r19enc_check.py meshgap` → `results/r19/enc/meshgap.json`:
- what it measures: the smallest distance from the Menagerie visual mesh of the links that geom covers (every vertex
  plus a ≤ 2 mm grid on every triangle) to the fixture, over **every** hit state of the pair;
- accuracy: the true surface is within 1.7 mm of the samples. So "< required" is a sure violation, and "≥ required +
  1.7 mm" is sure clear.

## 4. Commands for the controller (background lanes; nothing here was run)

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A=ur5e_enc
# lane 1: wok, then the plate-2 variant (UR5e finals' options, R19_ARM_SWAP.md 8)
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 TRIES=8 TAG=final ARM=$A > results/r17/log_wok_final_$A.txt 2>&1
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PX=.17 PLATE2=.43 TRIES=16 TAG=r18plate2b ARM=$A > results/r17/log_wok_plate2b_$A.txt 2>&1
# lane 2: spider, then the lid
$PY r17chain.py ACT=spider SIGN=1 SPX=1.52 SPY=.36 TRIES=12 TAG=final ARM=$A > results/r17/log_spider_final_$A.txt 2>&1
$PY r17chain.py ACT=lid SIGN=-1 SPX=1.52 SPY=.36 TRIES=16 TAG=final ARM=$A > results/r17/log_lid_final_$A.txt 2>&1
# lane 3: lever and spatula. Their stored UR5e paths PASS with ur5e_enc; run only because r19hub.py needs all six chain_*_ur5e_enc.json
$PY r17chain.py ACT=lever SIGN=1 SPX=1.52 SPY=.36 TRIES=8 TAG=final ARM=$A > results/r17/log_lever_final_$A.txt 2>&1
$PY r17chain.py ACT=spatula SIGN=-1 SPATREST=-1.15,.30 SPATELEV=8 SPATROLL=180 SPX=1.52 SPY=.36 TRIES=16 TAG=r18roll-1.15_.30 ARM=$A > results/r17/log_spatula_$A.txt 2>&1
# after each re-plan: the <= 4 mm re-check of the new chain (r17chain's own steps are coarser than 4 mm), < 3 min each
for S in wok wok_plate2b spider lid lever spatula; do $PY r19enc_check.py recheck SET=$S SUFFIX=_ur5e_enc; done > results/r19/enc/log_recheck_replans.txt 2>&1
# hub roadmap, only when all six chains are ok (same block as R19_ARM_SWAP.md 8 with A=ur5e_enc):
mkdir -p results/r19/hub_$A
$PY r19hub.py endpoints ARM=$A > results/r19/hub_$A/log_endpoints.txt 2>&1
$PY r19hub.py tuck ELBOW=neg ARM=$A > results/r19/hub_$A/log_tuck_neg.txt 2>&1
$PY r19hub.py tuck ELBOW=pos ARM=$A > results/r19/hub_$A/log_tuck_pos.txt 2>&1
$PY r19hub.py hubs TUCK=neg ARM=$A > results/r19/hub_$A/log_hubs.txt 2>&1
for e in "SPAT LEV_C" "SPAT H_SPAT" "LID_RACK H_WOK" "WOK H_SINK" "SPAT H_SINK"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
for e in "LEV_O WOK" "LEV_O H_SINK" "SPIDER H_WOK" "WOK H_POT" "LEV_O H_SPAT"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
for e in "LID_RACK H_POT" "LEV_C H_SINK" "LID_POT H_WOK" "LEV_C H_SPAT" "WOK H_WOK"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
for e in "SPIDER H_POT" "LID_POT H_POT" "LEV_C H_WOK" "LEV_O H_WOK" "H_SPAT H_SINK" "H_SINK H_WOK" "H_WOK H_POT"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 ARM=$A > results/r19/hub_$A/log_$1__$2.txt 2>&1; done
$PY r19hub.py graph ARM=$A ; $PY r19hub.py commands ARM=$A
```

How to read the results:
- A chain passes when `chain_*_ur5e_enc.json` says `"ok": true` **and** its re-check
  (`results/r19/enc/<set>_ur5e_enc.json`, column `ur5e_enc`) has 0 hit states.
- If the lid or the spider fails to re-plan, look at the failing pair first. Those two fail today only through
  enclosure bloat (§3); a tighter end-cap fit is the next step, not a looser gap.

## 5. Files

- **New:**
  - `r19ur5e_encfit.py` (the fit + proof), producing `r19/arm_ur5e_enc.json`;
  - `r19enc_check.py` (`enclose` / `self` / `recheck` / `summary` / `meshgap`);
  - `results/r19/enc/*.json`. Per-state reserves and hits for both arms are in `<set>.json`; the table is
    `summary.json`; the mesh diagnosis is `meshgap.json`.
- **Changed, with `.bak_r19enc` backups:**
  - `arms.py`: the `ur5e_enc` entry, `enclose()`, and the envelope file for `ur5e_enc`;
  - `r17chain.py`: one line, the walk start for `ur5e_enc`.
  - `envelope.py`: one line; it refuses `ARM=ur5e_enc`, which would otherwise overwrite the UR5e's
    `assets/envelope_-20.json`.

## 6. Limits
- **Reference geometry.** The "real arm" is the Menagerie visual mesh: Menagerie's OBJ files, derived from UR's
  published meshes, not UR's CAD. Cables, the tool flange adapter and the gripper are as modelled before.
- **Stir scene.** The stir is re-checked in its own R17 scene (as stored), not in the R18b layout.
- **The 4 spider self states** classed "artefact" (MuJoCo cylinder contact only) are still hits for the checker.
- **Hub-edge states.** These are r19hub's checked states. Their spacing is ≤ 4 mm for the old bound; with the
  `ur5e_enc` bound it is still ≤ 3.98 mm, so no re-cut was needed (33,761 states, as stored).

## 7. Second round: the tighter `ur5e_enc2` (2026-10-13, after the controller's `ur5e_enc` re-plans)

### 7.0 Answer first
- **`ur5e_enc2` encloses the real arm and hugs it.**
  - Proof: every triangle of the Menagerie meshes is inside. Max protrusion is −0.3 mm on every link, in the fit and
    again in the sim model.
  - Bloat (how far the model sits outside the real surface): 6.1 / 8.7 / 6.0 / 4.7 / 4.7 / 6.6 mm for the shoulder /
    upper arm / forearm / wrist 1 / wrist 2 / wrist 3. With `ur5e_enc` it was 19.7 / 20.0 / 50.7 / 8.7 / 9.7 / 11.3 mm.
- **Lid, spider and 4 hub edges no longer fail on environment pairs.** Those failures were enclosure bloat.
- **Two real 10 mm violations remain.** In both, the model gap is within 0.7 mm of the mesh gap:
  - **Wok final / plate 2:** the elbow end of the upper arm is 7.5 mm above the front rim of the plate (dish at x .43).
    This needs a layout change (§7.5).
  - **4 `LEV_O` hub edges:** wrist 1 is 8.0 mm below the closed upper-cabinet door. A re-plan of these free moves is
    enough; no layout change.
- **New self pair:** wrist 1's wrist-2 housing vs the gripper's OEM envelope box. The real wrist-1 mesh comes within
  0.9–1.3 mm of that box in wok (434 states), lid (695), spider (1,185) and 4 hub edges.
  - Why it is new: the Menagerie geoms and `ur5e_enc` cover that housing with a geom on the wrist-2 body. That body is
    adjacent to the gripper, so the checker never compared the two.
  - What it means: a posture problem (wrist folded back), not a layout one; re-plan with `ur5e_enc2`.
  - Open question: whether the real gripper housing (not its 75 × 75 × 138.5 mm OEM box) touches is undecided.

### 7.1 The model (`r19ur5e_enc2fit.py` → `r19/arm_ur5e_enc2.json`; `ARM=ur5e_enc2`)

**Why `ur5e_enc` was loose.** Its housings are cylinders on the joint axes, and they also cover the neighbouring
link. The real housings are not bodies of revolution:
- the forearm's elbow cap reaches r 68 mm toward ±x but only 21–48 mm toward the upper arm;
- the tubes flare into the housings on one side only.

Revolving all of that around the joint axis gave up to 50 mm of bloat.

**How `ur5e_enc2` is built.** Every link is covered only by pieces on its own body, so nothing has to be revolved:
- The link's mesh points are split by the `ur5e_enc` primitive they lie nearest to (housing, neck, tube, cap).
- The two tubes keep their capsules: upper arm r 49.8 mm, forearm r 38.8 mm.
- The 16 other pieces are convex k-DOPs: 168 half-spaces, 0.3 mm margin, MuJoCo mesh geoms with 332 vertices.
- The proof of enclosure and the growth of failing parts work as in `r19ur5e_encfit.py`. Fit time: 45 s.

**Tried and dropped** (measured with the same bloat test):
- Profile bands along the joint axes: still 50 mm, because the excess is around the axis, not along it.
- 60 mm slices or k-means surface patches: 13–20 mm, with 47–117 geoms. Their hulls bridge the concave junctions.

**Bloat test** (`bloat()` in `r19ur5e_enc2fit.py`):
- Model surface: sampled every 3 mm. A point counts only if no other piece of the arm holds it and it is not inside
  the real arm.
- Inside the real arm: a 1 mm voxel solid of the Menagerie meshes, parity fill with 2 of 3 ray directions. Its volume
  matches the meshes' signed volume:
  - exactly for the base, shoulder, wrist 1 and wrist 2;
  - +6 % / +11 % for the upper arm / forearm;
  - −31 % for wrist 3, whose mesh is not closed.
- Distance: to the nearest point of the real surface (≤ 2 mm grid, so it can exceed the true distance by ≤ 1.7 mm).

**Checks.**
- In the sim model: max protrusion −0.3 mm on every link (`r19enc_check.py enclose NEW=ur5e_enc2 N=10`; own-body
  pieces make this configuration-independent).
- Default `ur5e`: the compiled scene md5 and the full checks are still identical to the original `arms.py`.
- Random-pose self-contact: 45.1 % (UR5e 38.3 %). The new top pair is the wrist-1 piece vs the gripper OEM envelope
  (314 of 2,000 poses).
- Check time: about 0.15 s per state, the same as before.

### 7.2 Re-check of the stored UR5e paths with `ur5e_enc2` (`results/r19/enc2/`, same method as §2)

| Path | `ur5e_enc` | `ur5e_enc2` | Hit states | `ur5e_enc2` pairs | Arm–env min reserve: ur5e / enc / enc2 (mm) |
|---|---|---|---|---|---|
| wok final | fail | **fail** | 452 | wrist-1 piece – OEM envelope 434 (self); elbow piece – `r15_plate` 18 | 2.02 / −10.0 / **−3.23** |
| wok plate 2 | fail | **fail** | 452 | same; elbow – `r17_plate2` 18 | 2.02 / −10.0 / **−3.23** |
| lever | pass | pass | 0 | — | 19.46 / 10.62 / 16.32 |
| lid | fail | **fail** | 695 | wrist-1 piece – OEM envelope (self) | 2.02 / −5.04 / 2.08 |
| spider | fail | **fail** | 1,185 | wrist-1 piece – OEM envelope (self) | 2.03 / −10.0 / 1.12 |
| spatula | pass | pass | 0 | — | 77.88 / 43.07 / 79.56 |
| stir | pass | pass | 0 | — (plume 25.8 mm) | 22.69 / 22.10 / 21.64 |
| hub, 22 edges | 12 pass | **14 pass** | | `LEV_O`×4: wrist-1 piece – door (23–25 states); `LID_RACK`×2 and `SPIDER`×2: wrist-1 piece – OEM envelope (250–302) | `LEV_O`: 2.03 / −8.07 / −2.72 |

Self min reserve: 2.0 mm for every UR5e path; with `ur5e_enc2` 0.0 (intersecting) wherever the wrist-1/gripper pair
hits, otherwise ≥ 2.0.

Real-mesh check of every `ur5e_enc2` hit pair (`r19enc_check.py meshgap NEW=ur5e_enc2` →
`results/r19/enc2/meshgap.json`):

| Pair | Model gap | Real-mesh gap | Verdict |
|---|---|---|---|
| upper arm (elbow end) – plate / dish at x .43 (wok, plate 2) | 6.8 | **7.5** | violates 10 mm |
| wrist 1 – `r07_closed_door_1_0` (4 `LEV_O` edges) | 7.3 | **8.0–8.1** | violates 10 mm |
| wrist 1 – gripper OEM envelope (wok, plate 2, lid, spider, 4 hub edges) | 0 (intersect) | 0.9–1.3 | undecided: within the 1.7 mm sampling cover of 0 |

### 7.3 Lever re-plan, run here (`ARM=ur5e_enc2`, 32 s)
Command: `r17chain.py ACT=lever SIGN=1 SPX=1.52 SPY=.36 TRIES=8 TAG=final ARM=ur5e_enc2`.
- **Result: fail**, as with `ur5e_enc`. The anchor is the same as the UR5e final (cart −0.736) and the play is ok.
  The approach at kf 1 stops at step 4 on the forearm tube vs `upper_cabinet_1`.
- **The stored UR5e lever passes with `ur5e_enc2`:**
  - its play, at ≤ 4 mm, has 0 hits;
  - its two stored approaches have 0 hits (arm–environment reserve 29.5 / 16.3 mm).
- **So the arm model is not the problem:** the re-plan takes a different, worse approach than the stored path.
- `results/r17/chain_lever_s+1_final_ur5e_enc2.json` (`ok: false`) is from this run.

### 7.4 Re-check fix
`r19enc_check.py recheck` now skips a chain with `"ok": false` or an empty `play`, and writes `{"skipped": ...}`.
Tested on the failed `lever_ur5e_enc`. All commands take `NEW=ur5e_enc2` (outputs in `results/r19/enc2/`).

### 7.5 Layout proposals for the real-mesh violations (not run)

**Wok final and plate 2.**
- Where:
  - plate: `r15_plate` (and the waiting dish `r17_plate2` in plate 2), r 120 mm, centre (0.43, 0.13), top z 0.875,
    front rim at y 0.014;
  - arm: the elbow end of the upper arm at (0.462, 0.012, 0.882);
  - when: the wok action's start / end pose, cart x 0.172 (the H_WOK station). The elbow passes 2 mm in front of the
    rim and 7 mm above it.
- **Smallest change:** move that plating spot 10 mm toward the wall (centre y 0.13 → 0.14). The rim moves to y 0.024
  and the gap becomes about 13.9 mm (estimate).
- Implementation: r17chain has `PX` but no `PY` option; this needs `K15.PLATE['c']` y = 0.14 or a small `PY` option.
  The plate-2 dish uses the same y.
- Alternative without a layout change: a wok start/end posture with the elbow higher, which the `ur5e_enc2` re-plan
  may find on its own.

**`LEV_O` hub edges.**
- Where: wrist 1 is 8.0 mm below the bottom edge (z 1.35, front face y 0.212) of the closed upper-cabinet door
  `r07_closed_door_1_0`, on the retreat via (0, −0.15, 0).
- **No layout change:** these are free moves. Re-plan the 4 edges with `ARM=ur5e_enc2`; the via search or planner
  takes another route.

**Gripper vs wrist 1 (self).**
- No layout change: re-plan with `ur5e_enc2`, so the planner sees the pair.
- Also worth doing: check the gripper's real housing against its OEM envelope box (75 × 75 × 138.5 mm). If the real
  housing is smaller near the flange, the pair is clear.

### 7.6 Commands for the controller (`ARM=ur5e_enc2`; background lanes)
```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A=ur5e_enc2
# lane 1: wok, then plate 2 (UR5e finals' options). Expected to keep failing on the plate unless the elbow posture changes (7.5)
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 TRIES=8 TAG=final ARM=$A > results/r17/log_wok_final_$A.txt 2>&1
$PY r17chain.py ACT=wok SIGN=-1 GTILT=25 L2X=-.25 SINKC=-1.06 SPX=1.52 SPY=.36 PX=.17 PLATE2=.43 TRIES=16 TAG=r18plate2b ARM=$A > results/r17/log_wok_plate2b_$A.txt 2>&1
# lane 2: spider, then the lid
$PY r17chain.py ACT=spider SIGN=1 SPX=1.52 SPY=.36 TRIES=12 TAG=final ARM=$A > results/r17/log_spider_final_$A.txt 2>&1
$PY r17chain.py ACT=lid SIGN=-1 SPX=1.52 SPY=.36 TRIES=16 TAG=final ARM=$A > results/r17/log_lid_final_$A.txt 2>&1
# lane 3: lever with more search (TRIES=8 failed at the kf 1 approach, 7.3), then the spatula (hub input; its UR5e path passes ur5e_enc2)
$PY r17chain.py ACT=lever SIGN=1 SPX=1.52 SPY=.36 TRIES=16 SEEDS=3 TAG=final ARM=$A > results/r17/log_lever_final_$A.txt 2>&1
$PY r17chain.py ACT=spatula SIGN=-1 SPATREST=-1.15,.30 SPATELEV=8 SPATROLL=180 SPX=1.52 SPY=.36 TRIES=16 TAG=r18roll-1.15_.30 ARM=$A > results/r17/log_spatula_$A.txt 2>&1
# after the re-plans: the <= 4 mm re-check (failed chains are skipped), < 3 min each
for S in wok wok_plate2b spider lid lever spatula; do $PY r19enc_check.py recheck SET=$S SUFFIX=_$A NEW=$A; done > results/r19/enc2/log_recheck_replans.txt 2>&1
# hub: the block of section 4 with A=ur5e_enc2 (output results/r19/hub_ur5e_enc2/), only when all six chains are ok
```

**If a layout change is chosen for the plate** (§7.5): set the plating spot to y 0.14 first, then run lane 1 again.
Every other UR5e result was checked in the current layout and stays as it is.

### 7.7 Files (round 2)
- **New:**
  - `r19ur5e_enc2fit.py`, producing `r19/arm_ur5e_enc2.json` (geoms, proof, and the bloat before / after);
  - `results/r19/enc2/*.json`;
  - `results/r17/chain_lever_s+1_final_ur5e_enc2.json` and its log.
- **Changed, with `.bak_r19enc2` backups of the round-1 versions** (`.bak_r19enc` still holds the originals):
  - `arms.py`: the `ur5e_enc2` entry; `enclose()` now handles mesh pieces and a `remove` list;
  - `r17chain.py`: the walk start for any enclosing UR5e option.
- **Changed without a backup**, all my own files from round 1:
  - `r19enc_check.py`: `NEW=`, the skip of failed chains, mesh pieces in `enclose`, cover in `meshgap`;
  - `r19ur5e_encfit.py`: a `bloat` mode; the band attempt was removed.
