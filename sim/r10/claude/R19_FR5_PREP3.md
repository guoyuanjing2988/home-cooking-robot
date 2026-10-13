# R19 FR5 tomato vs the folded T2L cradle (GitHub #2 / #38): pick cart moved, set re-certified (Windows, 2026-10-14)

- **Arm:** `ARM=fr5_j6_pgc_sp20`, unchanged. **Cradle:** the adopted swing-away T2L cradle (Route B, `R19_PREP_T2L.md`, `kitchen19p5.py`), folded, pan aboard, unchanged.
- **Unchanged:** gates, fixtures, the tomato's position, object sizes, the arm, the adapter and the cradle design. The checker and rules are as in `R19_FR5_PREP2.md`.
- **Labels:** **[M]** sim-measured, **[E]** estimate or interpretation.

## 0. Answer first: **PASS**

- **The fix [M]:** one motion setting. The cart at the tomato pick is **fixed at x = −0.90** instead of free.
  - Before, the solver chose about −0.76 (candidates −0.73…−0.83).
  - The option is the existing `XCART=pick:-0.90` of the unchanged runner `r19fr5prep_actions.py`. No new runner code is needed for the adopted set.
- **The rest is unchanged:** the grasp, its approach direction, the keyframes, the tap and the lever-side motion. The arm branch at the pick is also the same (J1 ≈ 110°, elbow −, wrist −).
- **The cause [M]:** at the old pick cart, the wrist-1 housing sits 25 mm from the parked pan (gate 15.3 mm). The 50 mm straight pick approach (toward −y, toward the robot) then drives it 27.9 mm into the pan body (63 of 90 states).
  - At −0.90, the tomato is 0.345 m left of the arm base instead of 0.49 m.
  - The wrist then hangs clear of the folded pan [E: geometry reading]. In the cart frame, the pan body is Ø140 mm at x −0.54, y −0.17, z 0.93–1.01, and its lug block reaches x −0.415.
  - The measured gate is ≥ 30.1 mm everywhere.
- **All four acceptance checks pass at smoke settings [M]**, and again at full settings (SEEDS=3 TRIES=12 KEEP=4).
  - The full run took 150 s, so it was run here.
  - It picked the same anchors as the smoke run: its play and approaches are bit-identical to the smoke's (max |Δq| = 0).
- **Time [M]:** **38.5 s** vs 38.4 s. The +0.08 s is the first lane join: 4.8° + 0.028 m cart shuffle, against 0.2° + 0.001 m.
- **With the new tomato, all 9 adopted FR5 prep sets clear the folded cradle with the pan [M]:** 28 paths, 0 hits, min gate 23.4 mm (bascarrot, unchanged).

## 1. Results (adopted: `chain_tomato_fr5yfull_fr5_j6_pgc_sp20.json` = smoke `chain_tomato_fr5y_p90_…`, identical play)

| Check | Old `tomato_fr5xfull` | **New `tomato_fr5yfull`** (smoke `fr5y_p90`) |
|---|---|---|
| Chain ok / time (r17 timing, dwells incl.) | ok / 38.4 s | **ok / 38.5 s** |
| Pick cart / branch | −0.756 (free) / J1 109° E− W− | **−0.90 (fixed)** / J1 112° E− W− |
| Joins (lane 1, lane 2) | 0.2° (0.001 m) + 180° wrist flip | **4.8° (0.028 m shuffle)** + 180° wrist flip (unchanged) |
| Largest following step | 5.33° | 5.33° (pick piece 2.28°; rule 10°) |
| ≤ 4 mm re-check (`r19prep_verify.py`): states, hits | 3,445 + 90 + 52, 0 | **3,440 + 90 + 52, 0** (unwrapped labels 0) |
| Reserve play / pick approach / release; self | 2.13 / 11.12 / 1.0; 1.74 mm | **2.14 / 11.09 / 1.0; 2.0 mm** |
| Cable `fr5_j6_pgc_sp20c_yp_a-45` (`r19cable_check.py prep`) | 0 hits (3,590) | **0 hits (3,585)** |
| Cable groups, play: cable env / self; gripper; wrist | 62.0 / 15.8; 9.0 / 17.6; 47.6 / 1.7 mm | 62.0 / 15.8; 9.0 / 17.5; 47.6 / 2.2 mm |
| **Fold screen** (`r19prep5_screen.py MODE=fold P5_kind=swing PAN=1`) | 63 hit states (pick approach), 27.9 mm deep | **0 hits; min gate 30.1 mm** (play, wrist-1 housing vs pan body), pick approach 34.5 mm, release 164.6 mm |
| ≤ 4 mm re-check **with the folded cradle + pan + pot-zone layer** (`r19prep5_verify.py`) | **fails**: 63 hit states, approach 0 (negative control) | **ok, 0 hits** (3,440 + 90 + 52 states; same reserves) |
| Cable re-check with the folded cradle (`r19prep5_cable.py`) | — | **ok, 0 hits** (3,585) |
| Joint-load ratio / PGC moment | 0.50 / ≈ 0 | 0.496 / 0.0 N·m |

**How to read the table** [M]
- The 1.0 mm release reserve is the finger 6 mm over the blade plate at opening: design geometry, as before.
- The fold-screen gate is the distance minus the checker's 10 mm arm / held vs cart-part gap.
- The negative control is the old set re-checked with the same cradle tool. It reproduces the screen's 63 hit states exactly, which shows that the re-check does see the cradle.

**Run times (smoke / full):**
- planning 112 / 150 s;
- ≤ 4 mm re-check 50 / 49 s;
- cable 57 / 57 s;
- fold screen 5 / 5 s;
- re-check with the cradle 52 / 57 s;
- cable with the cradle 65 / 77 s.

## 2. What changed in the motion

| Keyframe / setting | Before (`R19_FR5_PREP2.md`) | Now |
|---|---|---|
| cart at the `pick` anchor (and `lifted`, which keeps it) | free; the DP took −0.756 | **fixed −0.90** (`XCART=pick:-0.90`) |
| everything else | `XL1=-0.65,.06,1.10 XL1R=level LVC=-0.25 L2C=-0.25`, SEEDUR | unchanged |

- **Pick-side arm state [M].** J1–J6 change from (109.4, −164.5, −83.9, −245.3, −9.2, −45.9)° to (112.1, −162.3, −109.4, −232.1, −11.3, −35.7)°.
- **The carry.** The cart travels from −0.90 to −0.273 during the pick → lane piece, which still takes 7.5 s (TCP-speed bound).
- **The join to the tap side.** The tap-side DP now picks the tap start at cart −0.086 (before −0.064). The join is 4.8° with a 0.028 m shuffle.

## 3. How it was found (`r19fr5prep2_probe.py`: a screen, not a check)

**What the probe does, per variant:**
1. It takes the pick anchor's start candidates: the same solver, seeds and UR5e seeds.
2. Each candidate is followed to the first lane with `r19prepchain.follow()`.
3. It gets the 50 mm pick approach (`approach()`).
4. It is joined (`meet_join()`) to the adopted chain's tap-side lane state.
5. Pick, follow, join and approach states are then measured against the folded cradle + pan with `r19prep5_screen.Meas`. These are the stored states (≤ 1 cm TCP steps), not cut to 4 mm.

Result: `results/r19/fr5y/probe_v1.json`.

| Variant | Distinct starts | Clean (follow + approach + join + fold) | Clean start: lane join / fold gate play, approach |
|---|---|---|---|
| as adopted (free cart, −0.73…−0.83) | 6 | 1 (cart −0.827, approach gate only **3.1 mm**) | 0.2° / 25.1, 3.1 mm; the other 5 hit (−10 / −8.8 mm) |
| `XCART=pick:-1.10` | 2 | 0 | wrist-1 housing vs the cart beam on the lift |
| `XCART=pick:-1.00` | 4 | 2 | 23.0° / 38.2, 94.9 mm |
| `XCART=pick:-0.95` | 4 | 2 | 15.8° / 35.2, 62.8 mm |
| **`XCART=pick:-0.90`** | 5 | **1** (E− W−; W+ starts hit door `r07_closed_door_0_1`, E+ the base plate) | **8.0° / 35.0, 34.6 mm** |
| `XCART=pick:-0.85` | 4 | 1 | 0.2° / 31.5, **10.8 mm** |
| `XCART=pick:-0.65` | 5 | 2 (both wrist +) | 204° / 42.6, 60.4 mm; the E− W− start still hits (−0.3 mm) |
| `XCART=pick:-0.60` | 6 | 3 (wrist +) | 211–278° joins |
| grasp turned +30° / +45° about the vertical (`XPY`) | 0 | — | no IK start at the pick |
| grasp turned −30° | 6 | 1 (cart −1.16) | 36° / 30.0, 216.9 mm |
| grasp turned −45° | 6 | 0 | open fingers vs the carrot on the approach; forearm vs wrist |

**Why −0.90 [E: judgement on the measured rows].**
- It is the smallest move that keeps the same branch with a small lane join (8° in the probe, 4.8° in the run) and ≥ 30 mm fold margin.
- −0.85 clears the approach by only 10.8 mm.
- −0.95 / −1.00 cost larger joins.
- Turning the grasp needs a new keyframe override, and its only clean start needs a 36° join.
- In the whole set the pick anchor has a single clean start, so the DP is deterministic: the smoke and full runs are bit-identical.

**Route choice: motion change, not planning with the cradle present.**
- `r19prepchain` and `r19prep5_chain` check the grasp approaches only after the DP has chosen the anchors. The old set's pick and play states already clear the folded pan (15.3 mm gate > 0). Planning with the cradle in the scene would therefore pick the same start and then fail at the approach: it does not steer the pick cart [E, from the code: `apps` are computed after `dp()`].
- `r19prep5_chain.py` is a copy of `r19prep4chain.py`, with stricter step-4 rules (plume rule, food join rule ≤ 5 cm / 15°) and without the FR5 keyframe overrides (`XL1R=level`). Moving the set there would mean re-qualifying the 180° wrist-flip join, a bigger change.
- Instead, the cradle is in the **certification**. `r19fr5prep2_foldcopy.py` writes a copy of the set with `scene.r19p5 = folded, swing, pan, knob top`: the dict `r19prep5_chain.py` stores for `P5STATE=folded P5PAN=1`. The unchanged `r19prep5_verify.py` / `r19prep5_cable.py` then re-check every stored state with the cradle present.

## 4. Controller lanes (optional: the full run finished here in 150 s; these reproduce it)
```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A="ARM=fr5_j6_pgc_sp20"; P="RACK=keyed SPX=1.56 SPY=.20"
F=results/r19/prep/chain_tomato_fr5yfull_fr5_j6_pgc_sp20.json
# lane 1: full run of the tomato with the adopted motion (~2.5-5 min)
$PY r19fr5prep_actions.py ACT=tomato SEEDS=3 TRIES=12 KEEP=4 SEEDUR=results/r19/prep/chain_tomato_r2_ur5e_enc2_pgc.json XL1=-0.65,.06,1.10 XL1R=level LVC=-0.25 L2C=-0.25 "XCART=pick:-0.90" TAG=fr5yfull $A
# re-checks (~1 min each)
$PY r19prep_verify.py FILE=$F NPROC=16
$PY r19cable_check.py prep FILE=$F ARM=fr5_j6_pgc_sp20c_yp_a-45
$PY r19prep5_screen.py MODE=fold P5_kind=swing PAN=1 KINDS=prep SETS=$F ARM=fr5_j6_pgc_sp20 PY=.15 TAG=fr5yfull
# with the folded cradle + pan in the scene (the copy refuses to overwrite: it exists from this round)
$PY r19fr5prep2_foldcopy.py FILE=$F
$PY r19prep5_verify.py FILE=results/r19/prep5/chain_tomato_fr5yfull_fold_fr5_j6_pgc_sp20.json NPROC=16 $P
$PY r19prep5_cable.py prep FILE=results/r19/prep5/chain_tomato_fr5yfull_fold_fr5_j6_pgc_sp20.json ARM=fr5_j6_pgc_sp20c_yp_a-45 $P WORKERS=16
# If a re-run picks a different candidate that fails a re-check, the files of this round stand (smoke fr5y_p90 = full fr5yfull).
```

## 5. Files

**New code** (nothing shared edited):
- `r19fr5prep2_actions.py`: pick-side keyframe options on top of `r19fr5prep_actions.override`. `XPY` turns the grasp about the vertical at pick / lifted / out-and-up; `XPU` sets the out-and-up position. The probe uses it. The adopted set does not need it: it uses the existing runner `r19fr5prep_actions.py`.
- `r19fr5prep2_probe.py`: the pick-variant screen against the folded cradle (§3).
- `r19fr5prep2_foldcopy.py`: a copy of a stored set with the folded cradle + pan in its scene, for `r19prep5_verify.py` / `r19prep5_cable.py`.

**New results:**
- **Adopted (full):**
  - `results/r19/prep/chain_tomato_fr5yfull_fr5_j6_pgc_sp20.json` + `_verify4mm.json`;
  - `results/r19/cable/prep/chain_tomato_fr5yfull_fr5_j6_pgc_sp20__fr5_j6_pgc_sp20c_yp_a-45.json`;
  - `results/r19/prep5/screen_fold_fr5yfull.json`;
  - `results/r19/prep5/chain_tomato_fr5yfull_fold_fr5_j6_pgc_sp20.json` + `_verify4mm_pot.json`;
  - `results/r19/prep5/cable/prep/chain_tomato_fr5yfull_fold_fr5_j6_pgc_sp20__fr5_j6_pgc_sp20c_yp_a-45.json`.
- **Smoke:** the same set of files with `fr5y_p90` in the name; the fold screen is `screen_fold_fr5y_p90.json`.
- **All 9 FR5 sets with the new tomato:** `results/r19/prep5/screen_fold_fr5final_y.json`.
- **Negative control:** `results/r19/prep5/chain_tomato_fr5xfull_fold_fr5_j6_pgc_sp20.json` + `_verify4mm_pot.json`, which fails as expected.
- `results/r19/fr5y/`: `probe_v1.json`, `vars/v1.txt`, and every log in `logs/`.
- This report.

**Not changed** (never written by me):
- md5 recorded before and after the runs: `r19prepchain.py`, `r19prep_verify.py`, `r19fr5prep_actions.py`, `r19prep5_screen.py`, `r19prep5_verify.py`, `kitchen19p5.py`, the cable files and `arms.py`;
- only imported or run: the remaining shared files.

The full list:
- `r19prepchain.py`, `r19prep3_actions.py`, `r19fr5prep_actions.py`;
- `r19prep_verify.py`, `r19prep5_*.py`, `kitchen19p5.py`;
- `r19cable*.py`, `arms.py`, `r19tol_core.py`;
- the old `tomato_fr5x*` result files.

## 6. Honesty notes

**Scope**
- **What the screen covers.** The fold screen and the cradle re-checks cover the tomato set only, with the cradle folded and the pan aboard.
- **Folded without the pan.** Removing the pan only removes pairs, so the empty folded cradle is covered too [E, as `R19_PREP_T2L.md`].
- **Deployed cradle.** Not checked: during prep the cradle is folded.

**Method**
- **The probe is a screen.** The certificates are the `_verify4mm*.json`, the cable files and the `r19prep5_screen` result.
- **Cable runs.** They used the cable files as of this session (md5 `r19cable_check.py` 56c36993…, `r19cable.py` 9f9afaf1…, `arms.py` 0816374a…, `r19tol_core.py` 4edd7dba…), unchanged during the work. Another agent is working on them; a later version may need a re-run.

**Limits of the model**
- **Timing.** r17 timing (no acceleration limit), as every prep round. The 180° wrist flip at the second lane is unchanged.
- **Not simulated:** rinse, wet friction and pan creep on the folded leaf.

**Process hygiene**
- Every command ran in the foreground under a `timeout` of 280–295 s; none hit it.
- No processes of mine remain. The 13 earlier orphan workers were not touched.
