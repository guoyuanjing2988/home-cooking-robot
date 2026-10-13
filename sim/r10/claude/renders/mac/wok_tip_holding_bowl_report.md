# WOK_TIP_HOLDING_BOWL: wok -> tip 90 deg into the holding bowl at spot 2 -> back to the cooker (Mac, 2026-10-13)

**Result: PASS.** One continuous path, checked end to end by the unchanged checker (`checker.py`, no edits):
- grasp the wok on the cooker (r17chain top grasp, sense -1, leaned 25 deg), lift, carry left;
- tip 90 deg toward the robot into today's holding bowl (190 x 70 mm, `bowlobj.py`) at plating spot 2 (0.17, 0.13), 2 s dwell;
- level, carry back, lower, set down on the cooker, release. **No sink trip.**

The bowl is the normal 70 mm bowl, not a lower one. At spot 2 the forearm clears it while lifting the wok, unlike the 6-8 cm bowls R17 put at spot 1.

- Video: `renders/mac/wok_to_bowl.mp4` (318 frames, held path only; jaw times and the dwell are not shown, as in r17video).
- Chain: `results/mac/wok_tip_holding_bowl_final.json` (= `_r5`, r17chain format, with `play`).

## Numbers
| | value |
|---|---|
| cycle time (r17chain timing model) | **25.9 s**. R17 `chain_wok_s-1_final` (plate + sink rinse): 48.9 s |
| min reserve, chain (follow check) | **2.7 mm**. The grasp approach / release retreat at the cooker is 2.4 mm (same as R17's pick) |
| independent re-check | `r19wokbowl_recheck.py`: all 255 playback states, full checker, **0 hits** |
| re-check, tightest per category | robot-env 2.0 mm (forearm `R_geom_16` to the bowl tab `r19_bowl_tab`, 12.0 mm against 10 mm, step 211, return leg); self 2.1 mm (`R_geom_17` to the held wok, step 10); held-env 2.9 mm (wok tile to the seasoning cup `r19_cup_body`, 7.9 mm against 5 mm, step 184); arm-frame 52.6 mm |
| max PGC moment | **6.47 N·m** (limit 7). It occurs at the tip, with the wok plus 1.15 kg food. Same as R17 |
| max joint torque ratio | **0.648** (at the tip) |
| held load | 2.95 kg until the tip, then 1.8 kg |
| meet joins | lane 0.7 deg, lane (return) 0.8 deg; cart 3 mm each |
| cart travel | +0.172 (cooker) to -0.494 (over the bowl) |

Pieces (from the anchors):

| piece | steps | time | min reserve |
|---|---|---|---|
| lifted -> pick | 3 | 0.2 s | 4.0 mm |
| lifted -> lane | 25 | 2.4 s | 3.5 mm |
| over the bowl -> via -> lane | 51 | 5.0 s | 4.5 mm |
| over the bowl -> tip -> level -> via -> lane (return) | 141 | 11.6 s | 2.7 mm |
| lowered -> lane (return) | 25 | 2.4 s | 3.5 mm |
| lowered -> set down | 3 | 0.2 s | 4.0 mm |

## Keyframes (wok frame = inner bottom point; cart 'F' = free IK variable)
| # | keyframe | wok position (m) |
|---|---|---|
| 0 | pick on the cooker (8 mm up) | (.83, .17, .933) |
| 1 | lifted (anchor) | (.83, .17, .955) |
| 2 | up and left | (.78, .17, .975) |
| 3 | lane (meet), **moved 9 cm toward the robot** (r17chain: y .17) | (.62, .08, .975) |
| 4 | **via**, 8.5 cm higher | (.30, .08, 1.06) |
| 5 | over the bowl (anchor) | (.17, .18, 1.025) |
| 6 | tipped 90 deg toward the robot, 2 s dwell. Lip 3 cm above the bowl rim, 5 cm beyond the bowl centre (+y), as r17chain over the plate | (.17, .275, 1.12) |
| 7 | level (empty) | (.17, .18, 1.025) |
| 8 | via | (.30, .08, 1.06) |
| 9 | lane (return, meet) | (.62, .08, .975) |
| 10 | (r17chain's) | (.78, .17, .975) |
| 11 | lowered (anchor) | (.83, .17, .955) |
| 12 | set down, release | (.83, .17, .933) |

Reproduce:
```
cd build_day
LIMIT_MB=8000 bash tools/runw.sh logs/mac/wokbowl_r5.log r19wokbowl2_chain.py ACT=wokbowl SIGN=-1 GTILT=25 SEEDS=3 TRIES=12 TAG=r5 L1Y=.08 "VIA=.30,.08,1.06"
LIMIT_MB=8000 bash tools/runw.sh logs/mac/wokbowl_recheck.log r19wokbowl_recheck.py results/mac/wok_tip_holding_bowl_final.json
LIMIT_MB=8000 bash tools/runw.sh logs/mac/wokbowl_video.log r19bowl_video.py results/mac/wok_tip_holding_bowl_final.json renders/mac/wok_to_bowl.mp4 CAM=75,-38,2.1 LOOK=.50,.18,1.0 "TITLE=..."
```

## Attempt log
| run | change | result |
|---|---|---|
| r1 (`r19wokbowl_chain.py`, written by the earlier session, first run now) | r17chain lanes unchanged: lane (.62, .17, .975) straight to over the bowl | **fail**. Lifting off the cooker passed (2.8 mm), so spot 2 solves R17's forearm problem. But all 12 over-the-bowl candidates failed on the way to the lane: the wok rim (`R_gripper_r15_wok_t4_1`) hit the seasoning cup `r19_cup_body` on its pad at (.45, .30, 1.085). The wok rim reaches y .34 at y .17 |
| r2 (`r19wokbowl2_chain.py`) | lane y .08, via (.30, .08, 1.00) | fail: the forearm `R_geom_16` met the bowl tab (11 of 12), or the closed door / upper cabinet |
| r3 | lane y .17, vias (.62, .06, .975) and (.45, .06, 1.00) | **pass**, 27.2 s, 2.2 mm |
| r4 | lane y .06, via (.45, .06, 1.00) | **pass**, 25.7 s, 2.2 mm |
| r5 = final | lane y .08, via (.30, .08, **1.06**) | **pass**, 25.9 s, **2.7 mm**. Chosen for the larger reserve (0.2 s slower than r4) |

## Assumptions (not verified beyond the checker)
- **Scene.** As today's hub re-check: the seasoning-cup station (pad, post, cup on its pad), the plate at spot 1, and the holding bowl at spot 2. The faucet lever is closed, since there is no sink trip. The bowl is a solid cylinder (conservative).
- **Food.** It is not simulated: 1.15 kg is a load in the wok until the tip keyframe, then 0. Whether 1.15 kg of stir-fry fits a 190 x 70 mm bowl (at most 2.0 l brim-full, on the outer size) is not checked. A bigger dish needs a wider bowl, which would have to be re-checked against the forearm at the lift.
- **Pour.** The wok tips about the r17chain pivot so that the lip ends 3 cm above the bowl rim, 5 cm past its centre. Food flow and splash are not modelled. Heat is off during the pour, so no plume rule applies.
- **Loads.** PGC moment and joint ratios are as in r17chain `load()`: static gravity at each keyframe.

## Files
New files only; no existing file was modified.
- `r19wokbowl_chain.py` (written by the earlier session at 17:10, run unchanged as r1).
- `r19wokbowl2_chain.py`: a copy of it with `L1Y` (lane y) and `VIA=x,y,z;...`. The vias go between the lane and over-the-bowl, and in reverse order on the return.
- `r19wokbowl_recheck.py`: registers the bowl and applies the chain's wok tilt (as `r17video.py` does), then runs `r19cup_recheck.py` unchanged.
- `results/mac/wok_tip_holding_bowl_{r1..r5,final}.json`; logs `logs/mac/wokbowl_*.log`.

## Open points
- The reserves are thin (2.0-2.9 mm in every category). The tightest is the forearm passing the bowl's tab on the return leg.
- The PGC moment at the tip is 6.47 of 7 N·m, as in R17. A heavier dish than 1.15 kg would exceed it.
- The seasoning cup forces the wok 9 cm toward the robot. If the cup station moves, re-check this path.
