# R19 FR5 prep sets (GitHub #2, with #4 and #38): the nine prep sets on `fr5_j6_pgc_sp20` (Windows, 2026-10-14)

- **Arm:** `ARM=fr5_j6_pgc_sp20`: Fairino FR5 with J6 ±360°, the PGC-140 from DH's drawing, on the 20 mm adapter (`R19_FR5.md`).
- **Scene and layout:** the ones the UR5e used.
  - The prep layout is `kitchen19.LAYOUT` (`R19_PREP_LAYOUT.md` §9).
  - The step-3 prep-time layout is `r19prep3_actions.py` (`R19_PREP_STEP3.md` §2.2).
  - All sets are planned with `r19prepchain.py`, unchanged, in today's code.
  - The pot-zone layer and `PY=.15` do not enter these scenes, as for the UR5e runs.
- **Checker and rules, never loosened:**
  - gates: 10 mm robot↔environment, 5 mm gripper/held↔environment;
  - states ≤ 4 mm apart (`r19prep_verify.py`, `NPROC=16`);
  - contact windows only on the ≤ 50 mm straight grasp approach / release retreat.
- **Labels:** **[M]** sim-measured, **[E]** estimate, **[S]** sourced.
- **Run type:** every FR5 result here is a **smoke run** (1 seed for the step-3 sets, 2 for the #4 sets, as their reports used). The full runs are controller lanes (§5).

## 0. Answer first

1. **Six of the nine sets pass on the FR5** [M, smoke runs]: press, tubfill, soak, tubempty, ctray, bascarrot.
   - Each was planned with the UR5e's smoke settings and re-checked at ≤ 4 mm: **0 hits** in every set.
   - Times are within 0.9 s of the UR5e's (r17 timing).
   - Reserves are the same as the UR5e's: 1.0–3.0 mm past the gate, where 1.0 mm is the press disc's design stop, as on the UR5e.
   - Joint-load ratios are 0.23–0.55.
2. **Three sets fail: tomato, carrot and basket.** All three fail at the same step, **getting out from under the tap**. Nothing tried closed them: the UR5e chain as IK seed, 3 seeds with every start tried, then the IK re-target of the certified UR5e path (§3).
   - **Tomato and carrot:** on the move from under the tap out to the first carry lane, the **FR5 touches itself** in every start that the IK carries through. That is 18 of 36 tomato starts and 12 of 35 carrot starts; the rest stop on the IK earlier.
     - The main pair is the **forearm tube against the wrist-2 J6 housing**: the wrist folds onto the forearm.
     - In the other starts the upper-arm shoulder touches the wrist-2 housing or the gripper housing.
     - Starts near the UR5e's own tap cart also touch the closed cabinet door `r07_closed_door_0_1` / `upper_cabinet_0_piece3` with the upper-arm elbow housing.
     - Exact clearance is 0 in each case: contact.

     **The adapter is not the cause:** the FR5 without it (`fr5_j6_pgc`) does the same (8 starts each, 0 clean).
   - **Basket:** at the drain pose, 6 cm in front of and 4 cm above the under-the-tap pose, the **wrist-2 J6 housing comes within 1.08 mm of the closed door `r07_closed_door_1_0`** over the sink. That is **8.9 mm short** of the 10 mm gate.
     - It happens on every one of 35 starts, at the same pose. The held pose fixes it, not the IK branch.
     - **The 20 mm adapter is the cause:** without it (`fr5_j6_pgc`), 4 of 12 starts leave the tap clean; the UR5e has 10 of 12 clean.
3. **Heavy load (tub fill, tub empty: full tub 2.78 kg)** [M + E + S], from `r19fr5_payload.py`:
   - FR5 payload **4.23 kg of 5** (margin **0.77 kg**);
   - combined CoG **219 mm** from the flange centre, inside the 300 mm full-performance limit;
   - PGC jaw moment **4.83 N·m** level and 4.84 N·m in the worst orientation, against 7 N·m;
   - the FR5 chains themselves measure at most 4.83 N·m (tub fill) and 4.84 N·m (tub empty).
4. **Controller lanes** (§5): the full runs (`SEEDS=3 TRIES=12 KEEP=4`) of the six passing sets and their re-checks. No longer run can close the three failing sets with the allowed methods: every start of their blocking anchor has already been tried (§3.1).

## 1. Pass/fail table, FR5 next to the UR5e

- **FR5 columns:** this round's smoke run, `results/r19/prep/chain_<set>_fr5_fr5_j6_pgc_sp20.json`, re-checked in `*_verify4mm.json`.
- **UR5e columns:** the certified result named in the task:
  - #4 sets: `chain_<set>_full_ur5e_enc2_pgc.json`, which re-checks the same as the round-2 smoke;
  - step 3: the `full` runs;
  - basket: the smoke `y20p30`;
  - tub fill: `t15fin`.
- **States:** the ≤ 4 mm re-check states, play + approaches.
- **Reserve:** the minimum past the gate over play and approaches (robot/held↔environment), then self.
- **Joint ratio:** the largest static gravity-torque ratio at the keyframes, against each arm's own torque envelope.
- **Time:** r17 timing [M in the sim's timing model]: TCP 0.10 m/s, 45°/s, joints 60°/s, cart 0.25 m/s, no acceleration limit.

| Set | FR5 | FR5 time | FR5 states, hits | FR5 reserve / self | FR5 joint ratio | UR5e time | UR5e states, hits | UR5e reserve / self | UR5e joint ratio |
|---|---|---|---|---|---|---|---|---|---|
| **press** (#4) | **pass** | 4.6 s | 286 + 94, **0** | 1.0 / 2.0 mm | 0.23 | 4.6 s | 155 + 72, 0 | 1.0 / 2.85 mm | 0.38 |
| **tomato** (#4) | **fail** (§3.2) | — | — | — | — | 36.5 s | 2,680 + 130, 0 | 1.0 (play 2.22) / 1.44 mm | 0.46 |
| **carrot** (#4) | **fail** (§3.3) | — | — | — | — | 47.0 s | 3,977 + 232, 0 | 2.0 / 2.0 mm | 0.43 |
| **basket** | **fail** (§3.4) | — | — | — | — | 34.6 s (smoke) | 3,535 + 85, 0 | 2.01 / 2.0 mm | 0.32 |
| **tubfill** | **pass** | 46.2 s | 3,000 + 75, **0** | 2.05 (play 2.10) / 2.0 mm | 0.47 | 45.3 s | 2,813 + 85, 0 | 2.05 (play 2.19) / 2.0 mm | 0.47 |
| **soak** | **pass** | 26.9 s | 2,223 + 143, **0** | 2.0 / 2.0 mm | 0.32 | 26.9 s | 1,573 + 131, 0 | 2.01 / 2.0 mm | 0.37 |
| **tubempty** | **pass** | 24.1 s | 4,176 + 75, **0** | 2.05 (play 2.09) / 2.0 mm | **0.55** | 23.9 s | 4,663 + 70, 0 | 2.02 / 2.0 mm | 0.44 |
| **ctray** | **pass** | 37.9 s | 3,308 + 212, **0** | 2.0 / 2.0 mm | 0.43 | 38.1 s | 3,211 + 180, 0 | 2.0 / 2.0 mm | 0.36 |
| **bascarrot** | **pass** | 14.6 s | 1,758 + 115, **0** | 3.0 / 1.37 mm | 0.43 | 14.4 s | 1,739 + 148, 0 | 3.0 / 1.55 mm | 0.39 |

**Notes on the passing sets** [M]
- **Press:**
  - the FR5 takes the knob with the cart at −0.58 (UR5e −1.27);
  - the push capacity on the keyed knob is the same, **102.5 N**, limited by the keyed grip;
  - the 1.0 mm reserve is the pusher disc stopping 6 mm above the blade plate, by design (R11), as on the UR5e.
- **Tub fill / tub empty:** the joins are 107° and 96°, each with a 0.41–0.47 m cart shuffle under the full tub (UR5e: tub fill 62° / 92°, tub empty 99° / 99°). They are included in the times.
  - The tub-empty joint-load ratio is 0.55 (UR5e 0.44–0.46). That is still about half the FR5's torque envelope.
- **Bascarrot:** the largest step while following is 9.8° per 1 cm step, the same near-singular wrist passage as the UR5e's 9.6°. It is inside the 10° rule and fully re-checked.
- **PGC jaw moments** are those of the UR5e chains, because the object path and grasp are the same: tub 4.83 / 4.84 N·m, basket in the soak 1.81, catch tray 0.34, food ≈ 0.
- **2π relabels:** the FR5 plays contain 2π joint relabels at the r17-style joins: tubfill 109, tubempty 179, ctray 116 and bascarrot 68 relabelled joint values; press and soak none (UR5e: 136–660).
  - `r19prep_verify.py` unwraps them to the same poses inside the ranges, and every unwrapped state is checked.
  - As before (README R19), an exporter must unwrap.
- **Planning runs and re-checks:** each smoke run took 46–195 s with nine running in parallel on a shared machine; the re-checks took 21–150 s (`results/r19/fr5/prep/logs/`).
- **Scenes:** the FR5 runs are in today's scenes. Two UR5e reference files were checked in slightly older ones:
  - basket `y20p30`: the tub's knob is pitched 30°; today it is 15°;
  - tub fill `t15fin`: the front-spot basket's knob is unpitched; today it is pitched 30°.

  All other sets have identical scenes, grasp worlds, keyframes and layout to their UR5e reference (compared field by field).

## 2. What was run

### 2.1 Settings
Smoke settings, UR5e argv with `ARM=fr5_j6_pgc_sp20 TAG=fr5`:

| Set | Settings | Source |
|---|---|---|
| press, carrot, tomato | `SEEDS=2 TRIES=10 KEEP=1` (round-2 defaults: `PRYAW=45`, `CHAPP=30`, `LVC=-0.35`) | the argv of the `r2` runs (`R19_PREP_LAYOUT.md` §9) |
| basket | `SEEDS=1 TRIES=8 KEEP=2 BYAW=-20 BPITCH=30` | `R19_PREP_STEP3.md` §6 |
| tubfill | `SEEDS=1 TRIES=10 KEEP=3 TPITCH=15` | same |
| soak | `SEEDS=1 TRIES=10 KEEP=1` (single anchor) | same |
| tubempty | `SEEDS=1 TRIES=10 KEEP=3 EDX=-0.15 EDEG=90` | same |
| ctray | `SEEDS=1 TRIES=8 KEEP=2 STG=0.17,.15,180 CLANE2=0.0,.06,1.04 CDEG=-120` | same |
| bascarrot | `SEEDS=1 TRIES=8 KEEP=2` | same |

Each run was hard-capped at 295 s (`timeout`), and none hit the cap.

### 2.2 For the three failures, in the order the FR5 rounds used

| Step | Tomato | Carrot | Basket |
|---|---|---|---|
| 1. Smoke | the pick and tap anchors follow no candidate | the tap and chute anchors fail | the tap anchor fails |
| 2. UR5e chain as IK seed (`SEEDUR=` the UR5e `r2` / `y20p30` chain; `r19fr5prep_chain.py`) | pick: the 12 UR seeds hit themselves on "out and up → lane"; tap still fails | **chute anchor now passes**; tap still fails | tap still fails |
| 3. More seeds / tries (`SEEDS=3 TRIES=16 KEEP=2` + `SEEDUR`) | fail (pick: candidates 0–15; tap) | fail (tap) | fail (tap) |
| 3b. Tap anchor alone, **every start** (`ANCH=under the tap`, `TRIES=40`, 3 seeds + UR seeds) | 0 of 36 leave the tap | 0 of 35 | 0 of 36 |
| 4. IK re-target of the certified UR5e path (`r19fr5prep_retarget.py`, §3.5) | fail | fail (`r2` and `full` paths) | fail (source scene and today's) |

- `r19prepchain.py` has no `SEEDUR`. `r19fr5prep_chain.py` executes its source unchanged and adds `r17chain.py`'s `ur_seeds()` verbatim, the method of the FR5 cooking rounds.
- **How far each blocking anchor is from passing** comes from `r19fr5prep_gap.py`, a diagnostic and not a check:
  - every start of the anchor is followed exactly as `r19prepchain` follows it (same steps, IK and cart rule);
  - it does not stop at a hit, and records each failing pair's exact clearance (distance.py lower bound) against its gate.

## 3. The failures: blocking pair, where, by how much [M]

### 3.1 Why no longer run helps
- An anchor passes only if at least one start follows to both of its meets. The joins (and `PLAN=1`, the planner for blocked joins) come after that.
- At the tap anchor of all three sets, every start the solver and the UR seeds produce has been followed, and none got out (step 3b).
- `r19prepchain.py` offers at most 3 seeds, so a full run would draw from the same candidates.

### 3.2 Tomato
- **Pick anchor: not blocking.** Three solver starts (candidates 27, 29 and 30, cart −1.48) reach the lane with no hit [gap diagnostic]. The smoke and the 16-try runs never got to them.
  - The other 31 fail in one of two ways:
    - the 12 UR seeds: forearm tube vs the wrist-2 J6 housing (self contact) on "out and up → lane";
    - the rest: the upper-arm elbow housing vs door `r07_closed_door_0_1`. The closest is 9.9 mm against 10 mm at pick → lifted (smoke, candidate 0).
- **Tap anchor: blocking.** It fails on the exit to the first lane, from under the outlet (−0.40, 0.37, 0.98) to (−0.80, 0.10, 1.15), i.e. out to the left along the counter front.
  - Of the 36 starts, 18 stop on the IK (pose or > 10° step) before the lane. **All 18 that reach it touch themselves.**
  - **The 11 UR seeds that reach it, and 2 solver starts near the same cart** (−0.11…+0.02; the UR5e's tap cart is −0.016):
    - **forearm tube vs the wrist-2 J6 housing** (11 of 13), or the upper-arm shoulder vs the gripper housing;
    - **and** the upper-arm elbow housing touches `upper_cabinet_0_piece3` / `r07_closed_door_0_1`;
    - first hit 15–27 of 52 steps out of the tap.
  - **The closest starts** (17, 29, 31, 35; carts −0.28…−0.37) keep clear of the environment. Late in the exit (step 39–47 of 52, near the lane) they touch themselves: upper-arm shoulder vs the wrist-2 J6 housing, shoulder J1 vs the gripper housing.
  - Candidate 30 (cart −0.38) also comes within 7.07 mm of door 0_1 (short 2.9 mm).
  - The other exit, tap → rolls → second lane, is clean for 14 starts, including most UR seeds. So the tomato is blocked by this one exit.
- **Without the adapter** (`fr5_j6_pgc`, 8 starts): the elbow touches `upper_cabinet_0_piece3` / door 0_1, and the wrist-1 housing touches the gripper housing.

### 3.3 Carrot
- **Chute anchor:** passes with `SEEDUR`.
- **Tap anchor: blocking.** Both meets are the same lane, (−0.65, 0.10, 1.15).
  - 35 starts: 23 stop on the IK (pose or > 10° step) and 12 reach both lanes. **All 12 touch themselves.**
  - **The closest are the UR seeds at the UR5e's own tap cart** (−0.016…+0.003, candidates 2, 3, 10, 19). They keep clear of the environment, but the **forearm tube touches the wrist-2 J6 housing** from step 24 of 41 out of the tap, around TCP (−0.55, 0.21, 1.08).
  - The other starts:
    - the same self pair plus the elbow housing touching door 0_1 / `upper_cabinet_0_piece3` (carts −0.06…−0.07);
    - or the upper-arm shoulder / shoulder J1 vs the wrist-2 housing or the gripper housing (carts −0.28…−0.38).
- **Without the adapter** (8 starts): the forearm tube vs the wrist-2 housing, or the elbow vs door 0_1 / `upper_cabinet_0_piece3`; contact in each.

### 3.4 Basket
- **Tap anchor: blocking.** The failure is at the keyframe 6 cm in front of and 4 cm above the under-the-tap pose: "in front of the stream" on the way in, "drain" on the way out. Its TCP is at (−0.25, 0.22, 1.09).
  - **Pair:** the wrist-2 J6 housing `R_geom_fr5_j6_pgc_sp20_wrist2_h_j6` vs the closed door `r07_closed_door_1_0`. It is the worst pair in 25 of 35 starts; `upper_cabinet_1` is next to it.
  - **Shortfall:** best clearance **1.08 mm against 10 mm, short 8.9 mm**. The first hit is already 5/8 of the way out of the tap: door 7.82 mm, cabinet 8.85 mm.
  - **Every start** reaches both lanes (35 of 36), and the best clearance is identical across them, at the same TCP pose.
  - The housing sits on the flange axis, so the held pose fixes where it is, whatever the IK branch [E, consistent with the identical numbers].
- **The adapter is the cause** [M]:
  - same diagnostic without the adapter (`fr5_j6_pgc`): 4 of 12 starts leave the tap with **no hit** (carts −0.20…−0.31);
  - `ur5e_enc2_pgc`: 10 of 12.
  - The 20 mm adapter moves the J6 housing 20 mm up the tool axis. With the basket knob pitched 30°, that is toward the door.

### 3.5 IK re-target of the certified UR5e paths (`r19fr5prep_retarget.py`)
**Method** (as `R19_FR5.md` §1.1):
- each stored UR5e state gives the TCP pose the UR5e had there;
- the FR5 is solved to that pose by IK continuation, with the cart at the UR5e's value;
- every state is fully checked.
- So the object, the gripper and the cart follow the certified path exactly; only the arm links differ.

**Results** (`results/r19/fr5/prep/chain_*_rt*_fr5_j6_pgc_sp20.json`), all **fail**:

| Source path | Failing states | Where and what (worst) |
|---|---|---|
| tomato (`r2` = `full`) | 120 of 297 play, 10 of 10 release | <ul><li>tray lift → first lane: elbow vs door 0_1, contact</li><li>at the tap: upper arm vs door 1_0 / `upper_cabinet_1`, contact</li><li>±30° rinse rolls: J4 flips 91–104° in one step</li><li>at the lever base: elbow vs door 0_1, contact</li></ul> |
| carrot `r2` | 85 of 379 | <ul><li>lane → tap: the UR5e's near-singular passage (9°/step). The FR5's J6 runs from 123° to 216° and J4 reaches its −265° stop</li><li>forearm vs wrist 2, self contact</li></ul> |
| carrot `full` | 111 of 362, 6 of 6 release | <ul><li>carry to the tap: elbow vs door 0_1, best clearance 1.52 mm (short 8.5 mm)</li><li>at the tap: upper arm vs door 1_0, contact</li><li>to and at the chute: elbow vs doors 0_0 / 0_1 and `upper_cabinet_0`, contact</li></ul> |
| basket `y20p30` | 32 of 223 (same in the source scene and today's) | <ul><li>J6 housing vs door 1_0 at the drain pose: clearance 0.11 mm, short 9.9 mm; in the shakes 6.0–7.8 mm</li><li>**J1 reaches its ±175° stop** between "over the tub" and the lane</li></ul> |

**J1 dead zone (finding)** [M]:
- The FR5 J1 dead zone, with the 77° mount yaw of `arms.py`, is UR J1 252–262°.
- The mount yaw was chosen from the cooking chains only (`R19_ARM_SWAP.md`).
- Three certified UR5e prep paths pass through that zone: basket 11 of 223 states, tub fill 31 of 189, tub empty 12 of 275.
- The FR5's own tub plans avoid it (other carts and branches), so it blocks none of the passing sets. It does block the re-target of the UR5e basket path.

### 3.6 The MuJoCo seam / edge misread
- The misread of `R19_PREP_STEP3.md` §4.1 did **not** show up for any environment pair in these runs.
- The only literal-only flags were MuJoCo-margin flags on FR5 self pairs (forearm vs wrist 2, exact clearance 0.03–0.24 mm, gate 0), in 1–11 states in five of the batches.
- Every candidate concerned goes on to real contact, so no verdict depends on them.

## 4. Payload and jaw moment with the adapter
Source: `r19fr5_payload.py ADAPTER_KG=0.25` → `results/r19/fr5/payload_fr5_j6_pgc_sp20_ad0.25.json`, the same numbers as `R19_FR5.md` §4.

- The script takes the tub grasp from the UR5e tub-fill chain.
- The FR5 tub-fill and tub-empty chains hold the tub the same way [M, compared]: object `tub_p15`, grasp sense +1, identical keyframe pose. So the numbers apply to both FR5 chains.

| Load (tub fill, tub empty) | Held | FR5 payload with the adapter | Margin to 5 kg | Combined CoG from the flange (limit 300 mm) | Held CoG alone | PGC jaw moment (limit 7 N·m) | Static flange moment, worst |
|---|---|---|---|---|---|---|---|
| full soak tub: tub 0.50 + water 2.28 kg | 2.78 kg | **4.23 kg** | **0.77 kg** | **219 mm** (axial 212) | 303 mm | **4.83 N·m** level, 4.84 worst orientation; chains: 4.83 (fill), 4.84 (empty) [M] | 9.10 N·m |

- **Labels:**
  - masses [E]: tub 0.50 kg, water 55 mm deep in Ø230, the adapter 0.25 kg;
  - the FR5 rule [S]: 5 kg rated at ≤ 300 mm CoG offset (Fairino manual §3.4.5.2.5, Fig. 3.4-19);
  - the PGC 7 N·m [S]: DH Table 1.2;
  - the geometry [M].
- **The adapter does not change the jaw moment**, because it sits above the gripper.
- **Without the adapter:** 3.98 kg, 213 mm.
- **Slosh is not simulated.** `R19_PREP_STEP3.md` §3.2 estimates ≈ 5.5 N·m with the water shifted while emptying [E], still under 7 N·m.
- The other sets hold at most 1.15 kg (basket), so no payload check is needed.

## 5. Controller lanes (each over 5 min; not run here)
```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
A="ARM=fr5_j6_pgc_sp20"
# lane 1: full runs of the six passing sets (the UR5e full runs took 3-19 min each), then the <= 4 mm re-check (0.5-3 min each)
for a in press tubfill tubempty ctray bascarrot; do $PY r19prepchain.py ACT=$a SEEDS=3 TRIES=12 KEEP=4 TAG=fr5full $A; done
$PY r19prepchain.py ACT=soak SEEDS=3 TRIES=12 KEEP=1 TAG=fr5full $A      # one anchor: KEEP=1
for a in press tubfill tubempty ctray bascarrot soak; do $PY r19prep_verify.py FILE=results/r19/prep/chain_${a}_fr5full_fr5_j6_pgc_sp20.json NPROC=16; done
# lane 1 can be split in two (press tubempty soak | tubfill ctray bascarrot) to halve the wall time.
# If a full run picks a candidate that fails the re-check (as the UR5e tub-fill full run did), this round's smoke files stand:
#   results/r19/prep/chain_<set>_fr5_fr5_j6_pgc_sp20.json (+ _verify4mm.json).
```
- **No lane is given for tomato, carrot or basket.** Every start of their blocking anchor has been tried (§3.1), and the allowed methods are used up.
- **Options outside this task's list** (not run; they change motion or hardware, not gates, positions or sizes):
  - **tomato, carrot:** another tap exit:
    - the first carry lane (`L1` / `LANE`);
    - waypoints;
    - `TROUTE=back`;
    - a different rinse pitch.
  - **basket:** a lower or further-forward drain pose (`TAPZ` / `TAPY` move it with the tap pose), or a different knob pitch (`BPITCH`).
  - **Gripper mounting:** mount the gripper without the adapter, which the basket shows would clear. But the adapter is what the cooking side needs (`R19_FR5.md`).

## 6. Files
**New code:**
- `r19fr5prep_chain.py`: `r19prepchain.py` executed unchanged from its source, plus the `SEEDUR=` opt-in (`r17chain.py`'s `ur_seeds()` verbatim);
- `r19fr5prep_retarget.py`: the IK re-target of a certified UR5e prep chain to an FR5 option, with the full check and the failing runs located;
- `r19fr5prep_gap.py`: the "how far from passing" diagnostic of one anchor (not a check).

**New results:**
- `results/r19/prep/chain_<set>_fr5_fr5_j6_pgc_sp20.json` for all nine sets, and `*_verify4mm.json` for the six passing ones;
- explorations, all failed: `chain_{tomato,carrot,basket}_fr5ur_*` (`SEEDUR`), `_fr5ur3_*` (3 seeds, 16 tries) and `_fr5tapdiag_*` (tap anchor alone, every start);
- `results/r19/fr5/prep/`:
  - re-targets: `chain_{tomato_rt, carrot_rt, carrot_rtfull, basket_rt, basket_rtcur}_fr5_j6_pgc_sp20.json`;
  - gap diagnostics: `gap_*_{fr5_j6_pgc_sp20, fr5_j6_pgc, ur5e_enc2_pgc}.json`:
    - the tomato tap batches `c0-5` … `c30-35` and the carrot tap batches `c0-8` … `c27-35` carry the per-pair minima used in §3.2–3.3;
    - the earlier batches have only the worst pair; the first tomato tap batch 0–11 hit the 5-min cap and has only its log;
  - `logs/`;
- `results/r19/fr5/payload_fr5_j6_pgc_sp20_ad0.25.json`;
- this report.

**Not changed:** `r19prepchain.py`, `r19prep_verify.py`, `r19prep3_actions.py`, `arms.py` and every other shared file. No UR5e result was overwritten.

## 7. Honesty notes
- **Smoke runs.** Every FR5 pass is a smoke run, with every state re-checked at ≤ 4 mm. The full runs are lane 1.
- **The gap diagnostic is not a check.** It runs the same follow and checker without stopping at hits, to measure how far a start is from passing.
- **"Contact"** means the exact distance lower bound is 0. A penetration depth is not computed, so "short ≥ 10 mm" is a lower bound on the shortfall.
- **Timing:** r17 timing assumes unlimited acceleration. R19 smooth found such paths 20–50 % slower with acceleration limits.
- **Run times:** the machine was shared with other agents' runs, so run times are not benchmarks.
- **Not simulated:** the process physics (rinse, slosh, pour) and wet friction, as in the UR5e rounds.
