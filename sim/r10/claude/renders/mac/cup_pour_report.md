# R19 seasoning cup: port -> wok -> pour -> port (Mac, 2026-10-13)

**Result: PASS.** One continuous path, checked end to end by the unchanged checker: grasp at the port pad, lift, carry to the wok, roll 120° to pour (2 s dwell), roll back, carry back, set the cup down on the pad, release.

- Video: `renders/mac/cup_pour.mp4`. It plays the held path only. The empty-gripper approach and release and the 2 s dwell are not shown, so the clip runs 9.4 s against the model's 20.6 s.
- Chain: `results/mac/chain_cup_final.json` (r17chain format).

## Numbers (`chain_cup_final.json`)

| | |
|---|---|
| cycle time (r17chain timing model) | **20.6 s** (grasp and release 0.8 s each, approach and retreat 0.6 s each, 2 s pour dwell) |
| min reserve, robot-environment | **2.2 mm**: wrist link `R_geom_26` to wok tile `r15_wok_t4_8`, 12.2 mm against the 10 mm required, during the pour |
| min reserve, self | 2.3 mm (`R_geom_17` / `R_geom_26`) |
| min reserve, held cup / gripper to environment | 3.0 mm: cup to pad, 8 mm against 5 mm required, at the 8 mm lift |
| grasp approach / release retreat | ok, 6 cm along -y, jaws open 25 mm, min reserve 2.5 mm |
| meet join (return lane) | 0.1° joint move, no cart shuffle |
| PGC moment | **0.01 N·m** max (limit 7). The TCP is at the cup centre, so the CoM sits almost on the TCP |
| max joint torque ratio | **0.459** (at the tipped frame) |
| held load | 0.18 kg (cup 0.12 + liquid 0.06) until the pour, then 0.12 kg |
| cart travel | -0.07 to 0.17 m |
| independent re-check | `r19cup_recheck.py`: all 224 playback states, full checker, **0 hits** |
| tip sensitivity | TIP=110: pass, 20.2 s, min reserve 6.1 mm. TIP=130: pass, 21.0 s, 2.2 mm |

Reproduce:

```
cd build_day && LIMIT_MB=8000 bash tools/runw.sh logs/mac/cup_final.log r19cup_chain.py ACT=cup TAG=final ONE=1 PORTC=.05 PORT=.45,.30,1.085 SEEDS=3 TRIES=12 OUTY=none LANE=.58,.10,1.08 POUR=.79,.08,1.075
LIMIT_MB=8000 bash tools/runw.sh logs/mac/cup_video.log r19cup_video.py results/mac/chain_cup_final.json renders/mac/cup_pour.mp4 CAM=120,-32,1.5 LOOK=.6,.18,1.08 "TITLE=seasoning cup: port -> wok -> pour -> port"
```

## Keyframes (cup frame = bottom centre)

| # | keyframe | cup position (m) | cart |
|---|---|---|---|
| 0 | pick at the port (anchor, 8 mm above the pad) | (.45, .30, 1.093) | 0.05 fixed |
| 1 | lifted | (.45, .30, 1.115) | anchor's |
| 2 | lane | (.58, .10, 1.08) | free |
| 3 | low at the wok rim, upright | (.79, .08, 1.075): bottom 5.5 cm above the rim (1.02), 5 cm inside the front rim | free |
| 4 | tipped 120°: wrist roll about the approach axis | mouth toward +x, 30° below horizontal; 2 s dwell | free |
| 5 | level (empty) | (.79, .08, 1.075) | free |
| 6 | lane (the only meet) | (.58, .10, 1.08) | free |
| 7 | over the pad | (.45, .30, 1.115) | anchor's |
| 8 | back on the port (anchor, release) | (.45, .30, 1.093) | 0.05 fixed |

## Assumptions (not verified beyond the checker)

- **Cup grasp.** Same as R14 (`r14reach.py cup_*`, `r14_cup`):
  - TCP at the cup's centre;
  - approach horizontal toward the wall (+y) with the cup upright;
  - jaws across x, held jaw 0.014 (the R14 value), open 0.025 for approach and release.
  - The cup is the kitchen14 cup, 60 x 70 mm. It is attached to the tool as `R_gripper_` geometry, as for every held object, so contacts between the fingers and the cup are not checked.
  - Whether the R12 dual-zone fingers really hold a 60 mm cup at jaw 0.014 is taken from R14, not re-verified.
- **Port pose (a design change).** The cup stands on a weighing pad with its bottom centre at (0.45, 0.30, 1.085), so its centre is at z 1.12. That is 5 cm left of the kitchen14 `SEASON_PORT` box (x 0.50–0.60).
  - With the cup under the port at x 0.55, every candidate failed: the wrist went into the hood, the arm folded onto itself, or the IK jumped (runs r1–r7).
  - x 0.45 is the R14 probe `pt0.45_0.30_1.12`, which passed (20/96 starts).
  - The pad is a 60 x 10 mm disc on a 24 mm post from the counter. The real station hangs the platform from the cabinet underside; that hanger is not modeled.
  - **So the station's nozzle head and weighing platform need to sit about 0.10 m further left than the kitchen14 port box.**
- **Return place.** The cup goes back on the port pad, not the cup rail. R14 evidence 1 already shows the backsplash rail failing (forearm against the base plate). It was not retried here.
- **Pour.**
  - A 120° roll about the approach axis. R14: "a wrist roll with a horizontal approach works".
  - The pour goes sideways (+x) along the front of the wok, not toward the wok centre. The stream should land around (0.82–0.85, 0.08), inside the 0.17 m rim.
  - The liquid is not simulated.
  - Heat is off, so the R15 plume rule is not applied.
  - The arm stays out of the hood: the hood is a collision box, and the path never goes under it above z 1.25.
- **Loads.**
  - Cup 0.12 kg (assumed stainless), CoM at the cup centre.
  - 60 g of liquid, CoM 2 cm above the cup bottom, fixed in the cup frame until the cup is levelled after the pour.
- **Timing.** The r17chain model:
  - TCP ≤ 0.10 m/s, rotation ≤ 45°/s, joints ≤ 60°/s, cart ≤ 0.25 m/s;
  - joins at 60°/s + 0.6 s;
  - grasp and release 0.8 s each.

## Method change against r17chain (in the copy `r19cup_chain.py` only)

`ONE=1`: the pour is **not** an anchor.

- The port anchor's arm state is followed by IK continuation through the lane, the wok, the tip and the level frame to the return lane.
- The return lane is the only meet. It joins that state to the place anchor followed backward, which has the same pose and candidate as the pick.

With an independent pour anchor (runs r8–r12), both sides followed, but every lane join failed. The port side and the pour side arrived on different IK branches (elbow up against elbow down, 275–298° of joint motion). The straight join moved the cup 50–62 mm, more than the 5 cm food limit, or the forearm hit the base plate.

## Attempt log

| run | change | what failed (hits) |
|---|---|---|
| r1 | port (.55, .30), out 20 cm toward the robot, lane (.66, 0, 1.12), pour (.80, .04, 1.035) | **Port side:** pulling the cup toward the robot folds the arm (self `R_geom_10` / `R_geom_25`, `R_geom_26`); one candidate hit the cooker; one IK jump of 14.6°. **Pour side:** the gripper body hit wok tile t4_9 when rolled (pour too low); others hit the cart beam or base plate |
| (r2/r3, first try) | invalid: zsh did not split the arguments, so the parameters were not applied | output deleted, rerun |
| r2 | no out frame, lane (.68, .20, 1.15), pour (.79, .08, 1.08) | The pour now tips clear. On the way to the lane at y .20 the pour candidates hit the hood edge (gripper envelope, `R_geom_21`). The port side still self-collides |
| r3 | port cart fixed at 0.25, lane (.66, .14, 1.12), pour z 1.075 | 6 pour candidates follow. Port side: wrist link `R_geom_25` meets the hood as the cup moves right |
| r4 | lane (.60, .08, 1.04) | Port side: 11.75° IK jump (wrist branch change) between lift and lane |
| r5 / r6 / r7 | port cart 0.15 / 0.35 / free | 0.15: wrist in the hood already at the lift. 0.35: forearm against base plate. Free: self collisions |
| r8, r9 | **port pad moved to x .45**, cart .05, lane (.58, .10, 1.08) | Port and pour anchors both follow; approach and release ok. Lane join blocked (pour candidates on carts 0.42–1.04) |
| r10, r11 | pour cart fixed at .33 / .25 | Carts now 0.1–0.19 m apart, but the join is still blocked |
| r12 | join diagnostics | Different IK branches at the lane (see above) |
| r13 = final | `ONE=1` | **PASS** |
| tip110, tip130 | TIP=110 / 130 | pass / pass |

## Files

New files in the sim dir; no existing file was modified.

- `cupobj.py`: registers `kitchen16.OBJ['cup']` and wraps `kitchen17.add` to add the pad, the post and a cup on the pad. cfg keys: `r19_station`, `r19_port`, `r19_cup`.
- `r19cup_chain.py`: the r17chain copy with `ACT=cup`. Options: `PORT`, `POUR`, `LANE`, `TIP`, `PORTC`, `POURC`, `OUTY`, `LIFT`, `HOVER`, `ONE`, `JAW_HELD`, `LIQ`, `DEBUGJ`. Join failures now carry their reasons.
- `r19cup_video.py`: imports cupobj and runs `r17video.py` unchanged. For rendering only, the held cup is drawn white instead of gripper grey.
- `r19cup_recheck.py`: independent full re-check of a chain's playback states.
- `results/mac/chain_cup_final.json` (pass), `chain_cup_tip110.json`, `chain_cup_tip130.json`, and attempt files `chain_cup_r1..r13.json`. Logs are in `logs/mac/cup_*.log`.

## Open points

- The reserves are thin: 2.2 mm wrist-to-wok during the pour, 2.3 mm self. TIP=110 has 6.1 mm.
- Pouring toward the wok centre would need the grasp yawed at the wok, or a pitch tip. Neither was tried.
- On the lane the arm reaches out about 0.6 m beside the cart (cart near -0.06 with the cup at x 0.58).
- The video does not show the empty-gripper approach and release.
