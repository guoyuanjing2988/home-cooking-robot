# R19 FR5 prep sets, round 2 (GitHub #2): tomato, carrot and basket on `fr5_j6_pgc_sp20` by changing the motion (Windows, 2026-10-14)

- **Arm:** `ARM=fr5_j6_pgc_sp20` (Fairino FR5, J6 ±360°, PGC-140 on the 20 mm adapter), unchanged.
- **Scene, layout, fixtures, tap, object sizes, gates:** unchanged (`R19_FR5_PREP.md`). The faucet scene is the closed + open union, as before.
- **Checker and rules, never loosened:** 10 mm robot↔environment, 5 mm gripper/held↔environment; states ≤ 4 mm apart (`r19prep_verify.py`); contact windows only on the ≤ 50 mm straight grasp approach / release retreat.
- **What changed:** only keyframes (lane poses and orientations, the basket's drain height) and fixed carts at anchors / meets. The keyframes are built by the unchanged `r19prepchain.py` / `r19prep3_actions.py` and overridden in a new module, `r19fr5prep_actions.py`.
- **Labels:** **[M]** sim-measured, **[E]** estimate or interpretation, **[S]** sourced.
- **Run type:** every result here is a **smoke run** (1–2 seeds, with the UR5e chain as extra IK seeds for the tomato and carrot). Every stored state is re-checked at ≤ 4 mm. The full runs are controller lanes (§5).

## 0. Answer first

1. **All three sets now pass on the FR5** [M, smoke runs]: 0 hits in the ≤ 4 mm re-check, and 0 hits again with the adopted cable routing `fr5_j6_pgc_sp20c_yp_a-45`.
2. **Two FR5-specific causes** blocked the three sets. The motion changes avoid both.
   - **The carry-lane pose folded the wrist.** The lane keyframes held the item with the tap's grasp, pitched 30° down, 0.2 m in front of the robot base. In that pose the FR5's wrist folds onto its forearm (forearm tube vs the wrist-2 J6 housing), or the elbow reaches the left cabinet door. **Turning the grasp at the lane** fixes it: carrot 30° about the vertical; tomato level, at the second lane's pose.
   - **The two sides of a lane meet arrived in incompatible arm states** [M], so the join (cart shuffle + straight joint move) was blocked.
     - **Basket:** the same branch, but on opposite sides of the FR5's J1 ±175° stop. The shuffle drives J1 to −175.0° at cart −0.294, and the IK loses the pose at −0.314.
     - **Carrot and tomato:** elbow-up on the chute / lever side against elbow-down on the tap side.
     - **The fix:** fixed carts (basket: tap −0.25, tub anchors −0.55 / −0.55; tomato: lever side and second lane −0.25) and the chute approach from the front (carrot). With them, both sides of every meet are elbow-down and on one side of the J1 stop.
     - Where the two sides still differ by a wrist branch, the join is a **wrist flip** while holding the item. It is a straight joint move (J4 ≈ 160°, J5 ≈ 45°, J6 180°), checked like any join, as the UR5e carrot's 186° / 158° joins.
3. **Basket:** the drain pose had to be **2 cm up instead of 4 cm** (same x/y: 6 cm in front of the under-tap pose). The wrist-2 J6 housing then clears door `r07_closed_door_1_0`. The drain is still over the sink basin, and out of the stream as before.

## 1. Pass/fail table

- **FR5 files:** `results/r19/prep/chain_{basket_fr5x_bH, carrot_fr5x_cD, tomato_fr5x_tB}_fr5_j6_pgc_sp20.json`, each with `_verify4mm.json`.
- **UR5e columns:** the certified UR5e results quoted in `R19_FR5_PREP.md` §1.
- **Time:** r17 timing [M in the sim's timing model; no acceleration limit], dwells included.
- **Reserve:** the minimum past the gate in the ≤ 4 mm re-check (robot/held↔environment), then self.

| Set | FR5 | FR5 time | FR5 states (play + approaches), hits | FR5 reserve / self | FR5 joint ratio | FR5 joins | Cable `yp_a-45` re-check | UR5e time | UR5e reserve / self |
|---|---|---|---|---|---|---|---|---|---|
| **basket** | **pass** | **32.9 s** | 2,044 + 97, **0** | 2.0 / 2.0 mm | 0.33 | 20° + 20° | **0 hits** (2,141 states) | 34.6 s (smoke) | 2.01 / 2.0 mm |
| **carrot** | **pass** | **53.1 s** | 5,059 + 130, **0** | 2.17 / 2.0 mm | 0.53 | 224° + 248° (wrist flips) | **0 hits** (5,189 states) | 47.0 s (`full`; `r2` 49.9 s) | 2.0 / 2.0 mm |
| **tomato** | **pass** | **38.4 s** | 3,445 + 142, **0** | 1.0 (release; play 2.13) / 1.74 mm | 0.50 | 0.2° + 180° (wrist flip) | **0 hits** (3,590 states) | 36.5 s | 1.0 (play 2.22) / 1.44 mm |

**Notes** [M]
- The tomato's **1.0 mm release reserve** is the finger 6 mm above the blade plate at the moment of opening: design geometry, as on the UR5e.
- **Joins:** a join's angle includes its cart shuffle.
  - Carrot: shuffles of 0.26 / 0.37 m, then wrist flips of J4 −159°, J5 −43°, J6 180°, J2 −33°, J3 11°, about 3 s each. The carrot moves while the wrist turns over, as in the UR5e carrot's joins.
  - Tomato: one wrist flip at the second lane, with no shuffle: J4 162°, J5 48°, J6 180°, J2 32°, J3 −14°.
- **Largest joint step while following:** basket 2.6°, carrot 2.2°, tomato 5.3° per step (rule: 10°).
- **PGC jaw moment:** basket 1.81 N·m, as the UR5e; food ≈ 0.
- **Joint-load ratio:** the carrot's 0.53 is the highest of the three (UR5e 0.43). It is still about half the FR5's torque envelope.
- **2π relabels** in the plays: basket 106, carrot 123, tomato 0. `r19prep_verify.py` unwraps them, as before. An exporter must unwrap.
- **Run times:** planning 73 / 204 / 115 s, ≤ 4 mm re-check 66 / 81 / 79 s, cable re-check 115 / 182 / 153 s (basket / carrot / tomato). The machine was shared with other agents' runs.

**Cable re-check** [M] (`r19cable_check.py prep ... ARM=fr5_j6_pgc_sp20c_yp_a-45`; group reserves past the gate, play):

| Set | Hit states | Cable vs environment / self | Gripper vs environment / self | Wrist vs environment / self |
|---|---|---|---|---|
| basket | 0 | 122.0 / 23.9 mm | 14.5 / 23.3 mm | 4.1 / 4.4 mm |
| carrot | 0 | 36.9 / 31.6 mm | 23.1 / 22.6 mm | 38.7 / 2.3 mm |
| tomato | 0 | 62.0 / 15.8 mm | 9.0 / 17.6 mm | 47.6 / 1.7 mm |

The approaches pass too: 0 hits; cable reserve ≥ 34 mm.

**Alternatives also certified** [M, smoke + ≤ 4 mm re-check, 0 hits; not cable-checked]:
- basket `fr5x_bE`: drain also 3 cm left and 1 cm further forward. 32.8 s, 2.0 / 2.0 mm.
- tomato `fr5x_tC`: second lane with a free cart; the join is 232° with a 0.29 m shuffle. 39.6 s, 1.0 (play 2.01) / 1.74 mm.

## 2. What changed in each motion

The purpose of each set is unchanged: same object and grasp, same pick, same pose under the tap with the same rinse, same destination and release.

### 2.1 Basket (`fr5x_bH`)
| Keyframe / setting | Before (UR5e, round 1) | Now |
|---|---|---|
| in front of the stream (in), drain (out) | under-tap pose + (0, −6 cm, **+4 cm**) | under-tap pose + (0, −6 cm, **+2 cm**), i.e. basket floor centre (−0.40, 0.27, **0.96**) |
| 3 shakes of 15 mm | 0.965–0.98 m | 0.945–0.96 m |
| cart at the anchor under the tap | free (FR5 starts −0.03…−0.54) | **fixed −0.25** (UR5e: −0.21) |
| cart at the pick and at "over the tub" anchors | free | **fixed −0.55 / −0.55** (UR5e: −0.47 / −0.44) |

- **Drain over the sink basin:** the basket footprint is x −0.50…−0.30, y 0.17…0.37, inside the basin (x −0.70…−0.10, y 0.08…0.52). Its floor stays ≥ 9.5 cm above the rim.
- **Out of the stream:** same y as before, so the stream relation is unchanged.
- **Why fixed carts** [M]:
  - The free pick-side starts (J1 −138…−168°, elbow +) and the tap side (J1 +144…+163°, elbow +) are on opposite sides of J1 ±175°.
  - With the tap at −0.25 and the tub anchors at −0.55, both sides are in the branch "J1 10–34°, elbow −, wrist +". The lane joins become 20° with a 0.11 m shuffle.

### 2.2 Carrot (`fr5x_cD`)
| Keyframe / setting | Before | Now |
|---|---|---|
| both lane meets (−0.65, 0.10, 1.15) | tap grasp: approach +y, pitched 30° down | **turned 30° about the vertical** (approach pointing left-forward, the travel direction), still pitched 30° down (`XL1R=XL2R=y30p-30`) |
| over the chute | gripper from front-right, 30° (`CHAPP=30`, UR5e round 2) | **from the front** (`CHAPP=0 CHUP=0,-.10,.18`, the UR5e round-1 setting); same upright carrot, same drop 20 mm into the chute |

- **Why** [M]:
  - The turned lane lets 5 of 12 tap starts out cleanly (0 of 12 before). Those are the starts near the UR5e's tap cart, J1 ≈ 80°, elbow −.
  - With `CHAPP=30`, every chute start is elbow +: the shuffle and join at the second lane were blocked.
  - With `CHAPP=0`, elbow-minus chute starts exist (J1 ≈ 114°).

### 2.3 Tomato (`fr5x_tB`)
| Keyframe / setting | Before | Now |
|---|---|---|
| first lane meet (pick ↔ tap) | (−0.80, 0.10, 1.15), tap grasp (pitched 30°, turned 90°) | **(−0.65, 0.06, 1.10), level grasp**: the second lane's pose (`XL1=-0.65,.06,1.10 XL1R=level`). The pick side arrives without turning the tomato; the tap side un-pitches and un-rolls on the way out, as it already did to the second lane. |
| lever-side anchor cart (in front of the blade plate) | −0.35 (`LVC`, UR5e round 2) | **−0.25** |
| second lane meet cart | free | **both arrivals at −0.25** (`L2C=-0.25`, an existing r19prepchain option) |

- **Why** [M]:
  - The tap exit to the second lane was already clean. Using the same pose for the first lane gives 10 of 12 tap starts and 12 of 12 pick starts, all in branch "elbow −, wrist −", at matching carts (join 0.2°).
  - At `LVC=-0.35`, the only clean lever-side start was elbow +.
  - At −0.25, with the lane cart fixed, an elbow-minus lever-side start reaches the lane. The join there is a 180° wrist flip.

## 3. How the variants were found (screens, then whole sets)

- **The screen** (`r19fr5prep_explore.py`; a screen, not a check):
  - For one anchor, it follows every distinct start candidate (the same solver, seeds and UR5e seeds) to the anchor's meets.
  - It uses `r19prepchain.follow()` itself: same steps, IK, cart rule and checker.
  - It is run for many keyframe variants in parallel.
- **The checks:** passing variants were then planned as whole sets (`r19fr5prep_actions.py`) and re-checked at ≤ 4 mm.
- Clean = the start reaches every meet of the anchor with no hit [M]:

| Anchor | Variant | Clean starts |
|---|---|---|
| basket, under the tap (6 starts) | before; basket turned +10° | 0 / 6 |
| | drain 2 cm up (bH); 0 cm up; 2 cm up + 2–4 cm forward | 3 / 6 |
| | drain 3–5 cm left (bE) | 4 / 6 |
| | + tap cart −0.25 | 4 / 4 distinct (−0.20: 2 / 4; −0.15: 0, > 10° steps; −0.10: no IK) |
| carrot, under the tap (12 of 27) | before; lane lower / further forward / further right / level / pitched 15° / back-out via / fixed tap carts | 0 |
| | lane turned 20° / 30° / 45° / 60° | 0 / 5 / 5 / 9 |
| carrot, over the chute (12) | approach 0° / 15° / 30° / 45° / 60° / 75° / 90° | 5 / 10 / 3 / 4 / 8 / 2 / 0; the clean starts are all elbow + except at 0° (4 elbow −, 1 elbow +) |
| tomato, under the tap (12 of 28) | before | 0 |
| | first lane turned 30° / 45° / 60° | 8 / 10 / 10 |
| | first lane = second lane, level | 10 (pick side 12 / 12) |
| tomato, lever side (LVC) | −0.35 (before) / −0.20 / −0.25 / −0.30 / −0.40…−0.70 / free | 2 (elbow + only) / 7 / 8 / 2 / 0 / 1 |

**Whole-set smoke runs that failed on the way** (kept as `chain_*_fr5x_*` results) [M]:
- **basket:**
  - `bz2`, `bx3`, `bx5`: free tap cart; lane joins blocked at the J1 stop.
  - `c25*`, `c30x3`: tap cart fixed, tub anchors free; same.
  - `bA`–`bD`: tub anchors fixed, KEEP=2; the DP saw only the tap's other branch, and the join was 282°, through the faucet spout.
  - `bF`: tap −0.30; branch mismatch.
  - `bG`: pick cart −0.60; the pick approach touches `upper_cabinet_0_piece3` (start reserve 0.1 mm).
- **carrot:**
  - `cA`: chute approach 30°; second-lane shuffle blocked, elbow + vs elbow −.
  - `cC`: lane turned 60°; no chute start reached the lane (upper-arm tube vs the base plate).
  - `cB`, `cE`, `cF` (and first tries of `cD`, `bE`, `bF`, `bH`): stopped at the 295 s cap when run three or four at a time; no file.
- **tomato:**
  - `tA`: lever cart −0.35; second-lane shuffle blocked (lever side elbow +).

## 4. Hardware

- **No hardware change is needed** for these three sets.
- **The J1 ±175° stop** with the 77° mount yaw of `arms.py` is what forces the fixed carts. A different mount yaw would move the dead zone, but it is an `arms.py` / hardware choice for all chains (`R19_ARM_SWAP.md`). It was not tried and is not proposed.

## 5. Controller lanes (each over 5 min; not run here)
```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A="ARM=fr5_j6_pgc_sp20"
# lane 1: full runs (SEEDS=3 TRIES=12 KEEP=4) of the three sets with the adopted motion; ~5-20 min each (smokes: 1.2 / 3.4 / 1.9 min)
$PY r19fr5prep_actions.py ACT=basket SEEDS=3 TRIES=12 KEEP=4 BYAW=-20 BPITCH=30 XD=0,-.06,.02 XTAPC=-0.25 "XCART=pick:-0.55;over the tub:-0.55" TAG=fr5xfull $A
$PY r19fr5prep_actions.py ACT=carrot SEEDS=3 TRIES=12 KEEP=4 SEEDUR=results/r19/prep/chain_carrot_r2_ur5e_enc2_pgc.json XL1R=y30p-30 XL2R=y30p-30 CHAPP=0 CHUP=0,-.10,.18 TAG=fr5xfull $A
$PY r19fr5prep_actions.py ACT=tomato SEEDS=3 TRIES=12 KEEP=4 SEEDUR=results/r19/prep/chain_tomato_r2_ur5e_enc2_pgc.json XL1=-0.65,.06,1.10 XL1R=level LVC=-0.25 L2C=-0.25 TAG=fr5xfull $A
# then the <= 4 mm re-check (~1-2 min each) and the cable re-check with the adopted routing (~2-3 min each)
for a in basket carrot tomato; do $PY r19prep_verify.py FILE=results/r19/prep/chain_${a}_fr5xfull_fr5_j6_pgc_sp20.json NPROC=16; done
for a in basket carrot tomato; do $PY r19cable_check.py prep FILE=results/r19/prep/chain_${a}_fr5xfull_fr5_j6_pgc_sp20.json ARM=fr5_j6_pgc_sp20c_yp_a-45; done
# If a full run picks a candidate that fails a re-check, this round's smoke files stand:
#   results/r19/prep/chain_{basket_fr5x_bH,carrot_fr5x_cD,tomato_fr5x_tB}_fr5_j6_pgc_sp20.json (+ _verify4mm.json, + results/r19/cable/prep/*__fr5_j6_pgc_sp20c_yp_a-45.json)
```
- The lane 1 commands can run as three parallel lanes.
- The carrot full run has 4 × 4 candidate pairs per meet, each with a ~230° join check, so it is the longest.

## 6. Files
**New code** (nothing shared edited):
- `r19fr5prep_actions.py`: the keyframe overrides (`X..` options) and the runner.
  - The runner is `r19prepchain.py` executed from its source, with `r19fr5prep_chain.py`'s SEEDUR opt-in and the keyframes taken from `override(action())`.
  - It also drops exact-duplicate start candidates (`XDEDUP`, default on; fixed-cart anchors return the same IK state many times).
  - With no `X` options the keyframes and grasps are identical to `r19prepchain`'s [M, compared for all three sets].
- `r19fr5prep_explore.py`: the variant screen of one anchor (§3).

**New results:**
- **adopted:** `results/r19/prep/chain_{basket_fr5x_bH, carrot_fr5x_cD, tomato_fr5x_tB}_fr5_j6_pgc_sp20.json`, each with its `_verify4mm.json`;
- **cable re-check:** `results/r19/cable/prep/chain_{basket_fr5x_bH, carrot_fr5x_cD, tomato_fr5x_tB}_fr5_j6_pgc_sp20__fr5_j6_pgc_sp20c_yp_a-45.json`;
- **alternatives:** `chain_basket_fr5x_bE_*`, `chain_tomato_fr5x_tC_*`, each with `_verify4mm.json`;
- **failed explorations:** `chain_basket_fr5x_{bz2,bx3,bx5,c25z2,c25x3,c25z0,c30x3,bA,bB,bC,bD,bF,bG}_*`, `chain_carrot_fr5x_{cA,cC}_*`, `chain_tomato_fr5x_tA_*`;
- `results/r19/fr5x/`:
  - the screens `explore_*.json`;
  - their start-candidate caches `cands_*.pkl`;
  - the variant lists `vars/`;
  - every log `logs/`;
- this report.

**Not changed:** `r19prepchain.py`, `r19prep3_actions.py`, `r19prep_verify.py`, `r19fr5prep_chain.py`, `arms.py`, the `*_fr5full_*` lane files and every other shared file.

## 7. Honesty notes
- **Smoke runs.** Every pass here is a smoke run: basket 1 seed; tomato and carrot 2 seeds plus the UR5e chain as seeds. Every stored state is re-checked at ≤ 4 mm and with the cable routing. The full runs are lane 1.
- **The screen is not a check.** `r19fr5prep_explore.py` stops at the first hit and is used only to choose variants. The certificates are the `_verify4mm.json` and cable files.
- **Interpretations:**
  - "Folds the wrist at the lane" [E] is read from the failing pairs (forearm tube vs the wrist-2 J6 housing) and from which lane turns clear them.
  - The J1-stop cause of the blocked basket shuffle is [M]: J1 reaches −175.0° at cart −0.294.
  - For the tomato and carrot joins, the cause is the branch mismatch (elbow / wrist sign) [M].
- **Wrist flips.** The carrot (224°, 248°) and tomato (180°) joins turn the wrist over while holding the item. They are fully checked straight joint moves, like the UR5e's 186° / 158° carrot joins. The held item moves along during the flip, which matters only for wet produce dripping [E].
- **Timing:** r17 timing assumes unlimited acceleration. R19 smooth found such paths 20–50 % slower with acceleration limits. The carrot's two flips cost about 10 s.
- **Not simulated:** rinse, drain and wet-friction physics, as in all prep rounds. The drain dwell is the same 4 s estimate [E], now 2 cm lower.
