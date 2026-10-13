# R19 holding bowl: plating spot 2 -> wok -> tip 110 deg -> back (Mac, 2026-10-13)

**Result: PASS.** One continuous path, checked end to end by the unchanged checker:
- grasp the bowl's tab at the second plating spot, lift, carry to the wok;
- roll 110 deg about the tab to pour (2 s dwell, heat off), roll back level;
- carry back, set the bowl down on the spot, release.

The TOMATO variant (300 g wedges, same bowl) also passes. The path is identical; only the load is higher.

- Video: `renders/mac/bowl_pour.mp4` (held path only, 9.4 s clip against the model's 25.8 s). The held bowl is drawn in gripper grey; tipped, it is the dark cylinder over the wok.
- Chains: `results/mac/chain_bowl_final.json`, `results/mac/chain_bowl_tomato300.json` (r17chain format).

## Numbers
| | bowl + 0.25 kg food (`final`) | bowl + 0.30 kg tomato (`tomato300`) |
|---|---|---|
| cycle time (r17chain timing model) | **25.8 s** | 25.8 s |
| min reserve, chain (follow check) | **1.9 mm**: finger `R_finger_minus` to wok tile `r15_wok_t4_9`, 6.9 mm against the 5 mm required, at the tip | 1.9 mm |
| grasp approach / release retreat | ok, 6 cm along -y, jaws open 25 mm, min reserve 15.0 mm | same |
| meet join (return lane) | 0.4 deg, cart 3 mm | same |
| max PGC moment | **0.87 N·m** (limit 7) | **0.94 N·m** |
| max joint torque ratio | **0.362** (at the pick) | **0.364** |
| held load | 0.60 kg until the pour, then 0.35 kg | 0.65 kg, then 0.35 kg |
| cart travel | -0.24 to 0.61 m | same |
| independent re-check | `r19bowl_recheck.py`: all 272 playback states, full checker, **0 hits**. Tightest: held/gripper-environment 1.9 mm (finger to wok tile, step 134); self 2.1 mm (forearm `R_geom_11` to the bowl body, step 139); robot-environment 27.1 mm | not re-run (same states) |

Reproduce:
```
cd build_day && LIMIT_MB=8000 bash tools/runw.sh logs/mac/bowl_final.log r19bowl_chain.py ACT=bowl TAG=final SEEDS=3 TRIES=12 POUR=.83,.14,1.02
LIMIT_MB=8000 bash tools/runw.sh logs/mac/bowl_tomato300.log r19bowl_chain.py ACT=bowl TAG=tomato300 SEEDS=3 TRIES=12 POUR=.83,.14,1.02 FOOD=.30
LIMIT_MB=8000 bash tools/runw.sh logs/mac/bowl_recheck.log r19bowl_recheck.py results/mac/chain_bowl_final.json
LIMIT_MB=8000 bash tools/runw.sh logs/mac/bowl_video.log r19bowl_video.py results/mac/chain_bowl_final.json renders/mac/bowl_pour.mp4 CAM=75,-42,1.9 LOOK=.52,.18,1.0 "TITLE=holding bowl 0.35+0.25 kg: spot 2 -> wok -> tip 110 -> back"
```
Defaults are in `r19bowl_chain.py`: SPOT = (.17, .13, .85), LANE = (.50, .08, 1.10), LIFT .05, TIP 110, FOOD .25, ONE=1.

## Keyframes (bowl frame = bottom centre)
| # | keyframe | bowl position (m) | cart |
|---|---|---|---|
| 0 | pick at spot 2 (anchor, 8 mm above the counter) | (.17, .13, .858) | -0.239 (solved) |
| 1 | lifted | (.17, .13, .90) | anchor's |
| 2 | lane | (.50, .08, 1.10) | free |
| 3 | low over the wok, upright | (.83, .14, 1.02): bottom at rim height, the whole bowl inside the rim radius | free |
| 4 | tipped 110 deg (wrist roll about the tab axis, +y) | mouth toward +x, 20 deg below horizontal; 2 s dwell | free |
| 5 | level (empty) | (.83, .14, 1.02) | free |
| 6 | lane (the only meet) | (.50, .08, 1.10) | free |
| 7 | over the spot | (.17, .13, .90) | anchor's |
| 8 | set down (anchor, release) | (.17, .13, .858) | -0.239 |

## Assumptions (not verified beyond the checker)
- **Bowl.** Stainless, outer diameter 190 mm, 70 mm tall, 0.35 kg, CoM 3 cm above the bottom. It is modelled as a **solid** cylinder, which is conservative for clearance.
- **Grip tab** (`bowlobj.py`).
  - A steel strap welded to the rim on the robot side (-y): 30 mm wide, 20 mm thick, reaching 75 mm beyond the rim, its top 5 mm below the rim.
  - The PGC closes across x on the 30 mm faces (jaw 0.015 per side, as the wok handle block). TCP 50 mm outside the rim; approach horizontal toward the wall (+y), as the cup.
  - The key (a slot in the tab, a pin on one finger) that fixes the bowl's yaw is assumed, not modelled. Tab stiffness is not modelled.
- **Spot.** The R18 second plating spot (x 0.17, y 0.13, on the counter). Nothing else stands there in this scene. The plate at spot 1 (x 0.43) and the seasoning cup on its pad (.45, .30, 1.085) are present as obstacles.
- **Pour.**
  - The roll turns the bowl about its own front-back axis. Food leaves the lip near (0.81-0.84, 0.14, ~0.98), i.e. into the wok centre.
  - Food and flow are not simulated: the 250-300 g is a point load 2 cm above the bowl bottom, fixed in the bowl frame until the level frame.
  - Heat off, so the plume rule is not applied.
- **Loads.** PGC moment and joint torque ratios are as in r17chain `load()` (static gravity load at each keyframe).

## Attempt log
| run | change | result |
|---|---|---|
| r1 | pour bowl bottom at (.83, .14, 1.06) | the tipped bowl hits the hood colour camera `r15_camera` (x .78-.88, y .15-.19, z 1.21-1.25) on every candidate that reaches the wok; the place side followed |
| r2 | pour (.74, .14, 1.05), shifted left out from under the camera | **pass**, 24.0 s, 2.2 mm (pours 9 cm left of the wok centre) |
| r3 | pour (.76, .10, 1.04) | pass, 24.3 s, 0.3 mm (thin) |
| r4 = final | pour (.83, .14, 1.02), lowered instead of shifted | **pass**, 25.8 s, 1.9 mm. Pours into the wok centre, so it was chosen |
| tomato300 | final + FOOD=.30 | pass, same path |

## Files
New files in the sim dir; no existing file was modified.
- `bowlobj.py`: `OBJ['bowl']`; wraps `kitchen17.add` (after cupobj) for a bowl on the counter (`r19_bowl='spot'`, `r19_bowl_at`).
- `r19bowl_chain.py`: copy of `r19cup_chain.py` with `ACT=bowl` and options `SPOT`, `POUR`, `TIP`, `LANE`, `LIFT`, `FOOD`, `PORTC`, `POURC`, `ONE`. The bowl mass is in `MASS`, and the bowl counts as a food object for the join limit.
- `r19bowl_recheck.py`, `r19bowl_video.py`: wrappers that run `r19cup_recheck.py` / `r17video.py` unchanged.
- `results/mac/chain_bowl_{r1..r4,final,tomato300}.json`, logs `logs/mac/bowl_*.log`.

## Open points
- Thin reserves: 1.9 mm finger to wok tile at the tip, 2.1 mm forearm to bowl. r2, the off-centre pour, has 2.2 mm.
- The camera under the hood front limits how high the tipped bowl may be. A taller bowl, or a pour above the wok centre with more lift, needs the camera moved.
- `tomato300` was not rendered separately: its path is identical to `final`.
