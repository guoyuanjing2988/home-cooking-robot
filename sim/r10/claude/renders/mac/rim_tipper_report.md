# SINGLE-CUP RIM TIPPER (issue #34): where a servo cup holder can sit at the wok rim (Mac, 2026-10-13)

**Result: PASS for two places behind-left of the wok: azimuth 120 deg (recommended) and 105 deg.**
- Holder position: cup wall 35 mm outside the rim, cup bottom 30 mm above the rim height. Cup bottom centre (0.713, 0.374, 1.050).
- The recommended place (AZ 120) meets all three conditions with the unchanged checker:
  - (i) the arm sets the cup into the holder with the cup chain's grasp, as one continuous checked path from the seasoning-cup pad;
  - (ii) the holder plus cup touches no state of the stored stir cycle, with the cup upright or tipped 120 deg;
  - (iii) it touches no state of today's cup-pour or bowl-pour paths.
- Every other screened place fails at least one condition (table below).

What is not the cup chain's: the cup is turned **-30 deg about its own axis** in the holder. The grasp is the same on the cup (TCP at the cup centre, jaws across, sense 1). The approach direction is +y turned 30 deg toward +x, so the gripper comes in from the front-left instead of straight from the front. With the unturned grasp, no place behind the wok passed the static placement check (see "Why the cup is turned").

## Conditions at the chosen place (AZ 120, gap 35 mm, DZ 30 mm, cup turned -30 deg)
| condition | method | result |
|---|---|---|
| (i) set the cup into the holder | `r19cuphold_chain.py ACT=cuphold` (r19cup_chain copy). The holder anchor's state is followed by IK continuation back through the vias, the cup chain's lane and the lift to the port pick. Checked at every step. Then the 6 cm grasp approach at the pad and the release retreat at the holder | **pass**. 8.6 s (r17chain timing model); 62 steps; min reserve 3.0 mm; max joint step 4.7 deg; approach at the pad 3.8 mm, release retreat 1.5 mm; joint torque ratio 0.49; PGC moment ~0 (TCP at the cup's centre of mass, as in the cup chain) |
| (i) independent re-check | `rim_tipper_load_recheck.py`: all 63 playback states, full checker, holder in the scene | **0 hits**. Tightest: self 2.2 mm (forearm to the base cover), held 3.0 mm (cup to the pad at the pick), robot-env 4.1 mm (wrist to the hood) |
| (ii) stir cycle | `rim_tipper_confirm.py`: all 1,120 states of `results/r19/stir/stirwalk2_h_scrape_dice_r17.json`, `Checker.check(full=True)`, in the stir's own scene plus the holder; cup upright and cup tipped, separately | **0 hits** in both (2 x 1,120 states) |
| (iii) pour paths | same script: all 224 states of `chain_cup_final.json` and all 272 of `chain_bowl_final.json`, in their scenes plus the holder; cup upright and tipped | **0 hits** in all four (2 x 224 + 2 x 272 states) |
| screen slack (MuJoCo distance minus the checker's required gap) | `rim_tipper3.py` | stir: upright > 40 mm, tipped 32.3 mm; cup path > 40 / > 40 mm; bowl path > 40 / > 40 mm |

The chain's keyframes (cup frame = bottom centre; yaw 0 up to the lane, then -30 deg):

| # | keyframe | cup position (m) |
|---|---|---|
| 0 | pick at the port (pad), grasp approach 6 cm | (.45, .30, 1.093) |
| 1 | lifted | (.45, .30, 1.115) |
| 2 | the cup chain's lane, already turned -30 | (.58, .10, 1.08) |
| 3 | via | (.62, .20, 1.09) |
| 4 | via, beside the holder: 10 cm back along the approach, 2 cm above the seat | (.662, .287, 1.07) |
| 5 | over the holder (2 cm) | (.712, .374, 1.07) |
| 6 | in the holder (8 mm above the seat, anchor); release, retreat 6 cm | (.712, .374, 1.058) |

The second passing place, **AZ 105**: gap 35 mm, cup turned -60 deg, cup bottom (0.769, 0.397, 1.050).
- It also passes (i): 9.5 s, min reserve 3.0 mm, re-check 75 states with 0 hits, tightest 2.1 mm.
- Its follow has one 9.4 deg joint step, under the chain's 10 deg limit but close to an IK branch change. So AZ 120 is the recommendation.
- (ii)/(iii) at AZ 105: confirmed with the checker, 0 hits (table below).

## Confirmation with the unchanged checker (every state, full check)
`rim_tipper_confirm.py`: `Checker.check(q, full=True)` on every state. The holder (seat, servo, post) is in the scene with the cup upright (`_up`) or tipped 120 deg (`_tipped`). `_base` is the same states without the holder.

| replay | states | AZ 120 (chosen): steps with hits / with the holder | AZ 105: steps with hits / with the holder | tightest pair, all variants (= the baseline; the holder is never the tightest) |
|---|---|---|---|---|
| stir base / up / tipped | 1,120 each | 0 / 0, 0 / 0, 0 / 0 | 0 / 0, 0 / 0, 0 / 0 | 2.0 mm spatula blade to wok tile (step 39); self 2.0 mm; robot-env 22.7 mm |
| cup pour base / up / tipped | 224 each | 0, 0, 0 | 0, 0, 0 | 2.2 mm wrist to wok tile (step 108) |
| bowl pour base / up / tipped | 272 each | 0, 0, 0 | 0, 0, 0 | 1.9 mm finger to wok tile (step 134) |

Both places: **`ok: true`** (`results/mac/rim_tipper_confirm_az120.json`, `rim_tipper_confirm_az105.json`).
- The checker reports only the tightest pair per category, and that pair never involves the holder. The holder's own margins are the screen slacks: at AZ 120, stir upright > 40 mm and tipped 32.3 mm; both pour paths > 40 mm.
- `rim_tipper_geomprobe.py` confirms that the holder geoms (`r34_seat`, `r34_servo`, `r34_post`, `r34_cup_body` / `r34_cup_tipped`) are built into these scenes.

**Tip swing** (`rim_tipper_swing.py`, AZ 120): the cup at 30, 60 and 90 deg, replayed the same way.
- Each angle: 1,120 stir states plus 224 cup-path and 272 bowl-path states.
- **0 hits at every angle** (`results/mac/rim_tipper_swing_az120.json`).
- With 0 and 120, the swing is checked at 30 deg intervals, not continuously.

## Screening of places (`rim_tipper_screen.py`, `rim_tipper2.py`, `rim_tipper3.py`)
Azimuth AZ is measured about the wok axis: 0 = +x (toward the pot), 90 = +y (behind, the wall), 180 = -x (left), 270 = toward the robot. GAP is the cup wall to the rim. DZ is the cup bottom above the rim (rim z 1.020).
- (ii) and (iii) were first screened with MuJoCo distances and the checker's own `required()` gaps (10 mm arm, 5 mm gripper / held), over all stored states. (i) was screened as three static states with the full checker: held 8 mm above the seat, released (jaws 25 mm), and the 6 cm retreat.

| place | AZ | (ii) stir, upright / tipped | (iii) cup and bowl paths, upright / tipped | (i) static placement | (i) chain | verdict |
|---|---|---|---|---|---|---|
| any, at rim height (DZ 0) | all | | | | | fit fails: seat and tipped cup overlap the wok tiles by 3.8-6.9 mm. DZ 30 mm is used below |
| behind-right | 45, 60, 75 (gap 35) | pass / pass (9.7, 2.9, 12.6 mm) | pass / pass | **fail** at all 7 approach turns (-90 to +90 deg): forearm `R_geom_11` against the cooker body or wok tiles | not tried | **fail (i)** |
| behind-right | 45-75 (gap 15) | pass / **fail** (tipped cup into the spatula blade, -0.9 to -19.6 mm) | pass | | | fail (ii) |
| behind | 90 (gap 35) | pass / pass (> 40) | pass / pass (> 40) | pass (turn -90: held 3.0, release 4.3 mm; turn -60) | **fail**: from the holder the wrist meets the hood or the camera (turn -60), or the pad (turn -90) | fail (i) |
| behind-left | **105** (gap 35) | pass / pass (> 40) | pass / pass (> 40) | pass (turn -60) | **pass** (turn -60) | **PASS** (9.4 deg step) |
| behind-left | **120** (gap 35) | pass / pass (32.3) | pass / pass (> 40) | pass (turns -60, -30) | **pass** (turn -30); fail (turn -60, wrist to pad) | **PASS** |
| behind-left | 90-120 (gap 15) | pass / pass (17.6-35.0) | pass / pass (bowl tipped 10.0 at 120) | pass | not tried | (ii)/(iii)/static (i) pass |
| behind-left | 135 (gap 15) | pass / 2.2 | bowl path vs tipped cup **-1.5 mm** | pass (also unturned, turn 0) | not tried | fail (iii) tipped |
| left | 150, 165 | tipped cup into the spatula (gap 15), or the bowl path (gap 35, -12 mm), or both pour paths (165) | | | | fail |
| left (wok handle) | 180 | | the handle and grip sit there | | | fail (fit) |
| **front-left** | 195-300 (screen 1) | 195-240 upright pass, tipped fail (-8 to -73 mm); 255-300 upright fail (spatula handle -37 to -120 mm) | **both pour paths run through it**: cup path -19 to -78 mm, bowl path -9 to -128 mm | | | **fail (iii)**, and (ii) tipped. The failure is from the cup itself, so it holds for any bracket |
| front-right | 315-345 | upright fails at 315 (spatula handle); tipped fails everywhere (-11 to -144 mm) | pass upright; bowl tipped fails at 315-330 | (330: servo against the palm in screen 1) | | fail (ii) |

### Why the cup is turned
- Screen 1 used the cup chain's grasp unturned (approach +y) and a servo box on the outer side.
  - Behind the wok, the gripper then lies over the wok, and the wrist meets the hood or the camera above it.
  - In front, the fingers met the outer servo box.
- `rim_tipper2.py` put the approach along the rim tangent (turns +-90 relative to the radius), with the servo beside the cup.
  - The held cup then met the servo, 2 mm against the 5 mm required. All static loads still failed.
- `rim_tipper3.py` hangs the servo under the seat and searches the turn over -90..+90 deg in 30 deg steps.
  - Static loads then pass behind the wok (90-135 deg) for turns -90 to 0.

### Why the chain needed one anchor (attempt log, `logs/mac/cuphold_*.log`)
| tries | set-up | result |
|---|---|---|
| az90, az90v/m/s, az120s, az105s, az105v2, az90a60, az120a30 | two anchors (pad, holder), meet in a lane | the pad side and the holder side never met: the wrist hit an upper-cabinet door on the way out from the pad; the holder side rose into the hood or the camera, or swept past the pad; joint jumps of 10.7-11 deg |
| az120a30r, az105r, az105p (RRT join), az105rf, az105pc25/15 | meet pre-turned; port cart free, or -0.25 / -0.15 | both sides reached the meet, but on different IK branches (180-257 deg apart): the join moved the cup 52 mm, and the cart shuffle put the forearm on the base plate. Same failure as the cup chain's r8-r12 |
| az105rc, az120rc | meet cart fixed | joint jumps of 33-42 deg |
| az105one*, o105lo, o120lo, o90lo | one anchor at the pad, followed into the holder | the pad branch's wrist went into the upper-cabinet door `r07_closed_door_1_1` behind the wok |
| **az105oneh, az120oneh30** | **one anchor at the holder**, seeded with the rim_tipper3 static state; followed back to the pad | **pass** (az90oneh60/90 and az120oneh60 fail: hood, pad) |

## Assumptions (not verified beyond the checker)
- **Holder** (`r34holder.py`, a simple box bracket):
  - a seat plate 72 x 72 x 12 mm under the cup;
  - a servo box 60 (radial) x 40 x 60 mm hung under the seat;
  - a 20 x 20 mm post down to 1 mm above the cooker top (z .921). The mounting to the cooker and the cable are not modelled.
  - No cup retainer lip is modelled; the cup is lowered the last 2 cm vertically.
- **Tipping:** the cup turns 120 deg about the rim tangent through its inner bottom edge, mouth inward.
  - At gap 35 mm, the mouth centre ends about 4 cm inside the rim and 2 cm above rim height, pointing 30 deg below horizontal.
  - Liquid flow, splash and the servo torque are not modelled. The swing is checked at 0/30/60/90/120 deg only (static poses, every stored state), not as a continuous sweep.
- **Stir cycle:** only the stored 1,120 states (5 strokes + close) are replayed. A holder at AZ 120 also screened clear of the R17 wok lift-and-plate paths: upright cup, AZ 90 at 7.7 mm and AZ 105 at 1.6 mm, by the screen only, not by the checker. AZ 120 does **not** clear them (servo -124 mm), so **the wok must not be lifted out with the AZ 120 holder fitted**. Either remove it, or use AZ 105, whose (i) has the 9.4 deg step.
- **Plume.** The holder is at the plume edge: its cup axis is 0.235 m from the wok axis and its seat's inner edge 0.199 m. When the arm loads the cup, the jaws close almost radially, so the inner finger is about 0.19 m from the wok axis. That is inside the 0.20 m plume rule, which was not measured here. **Load the cup with the heat off**, before cooking or in a heat-off pause. The holder itself may be in the plume.
- **Liquid:** 60 g, as the cup chain (LIQ .06).

## Files
New files only; no existing file was modified.
- `rim_tipper_screen.py` (written by the earlier session, run unchanged) -> `results/mac/rim_tipper_screen.json`: 48 places, unturned grasp, outer servo.
- `rim_tipper2.py` -> `results/mac/rim_tipper2_s1.json` (tangential approach, servo beside the cup).
- `rim_tipper3.py` -> `results/mac/rim_tipper3_s1.json`: servo under the seat, approach turn searched. The static load states are `results/mac/rim_tipper3_q_*.json`.
- `r34holder.py`: holder geometry and the `kitchen17.add` wrapper (`r34_holder=[az,gap,dz]`, `r34_cup`, `r34_tipped`).
- `r19cuphold_chain.py`: r19cup_chain copy with `ACT=cuphold`. Options: `HOLDER`, `ALPHA`, `MEET`, `MEETR`, `MEETC`, `VIA`, `PVIA`, `HOV`, `QSEED`, `ONE`, `ONEH`. Output: `results/mac/rim_tipper_load_<tag>.json`. Passing runs: `rim_tipper_load_az120oneh30.json`, `rim_tipper_load_az105oneh.json`.
- `rim_tipper_load_recheck.py`: registers the holder, then runs r19cup_recheck.py unchanged.
- `rim_tipper_confirm.py` -> `results/mac/rim_tipper_confirm_az105.json`, `rim_tipper_confirm_az120.json`.
- `rim_tipper_geomprobe.py`: confirms the holder geoms are built into the stir scene.
- `rim_tipper_swing.py` -> `results/mac/rim_tipper_swing_az120.json` (+ per-angle `rim_tipper_confirm_swing*_az120.json`).

Reproduce (from build_day, via `tools/runw.sh`):
```
LIMIT_MB=8000 bash tools/runw.sh logs/mac/rim_tipper3_s1.log rim_tipper3.py AZ=45,60,75,90,105,120,135,150,165,315,330,345 LOADN=10 ALPHAS=-90,-60,-30,0,30,60,90 TAG=s1
LIMIT_MB=8000 bash tools/runw.sh logs/mac/cuphold_az120oneh30.log r19cuphold_chain.py ACT=cuphold HOLDER=120,.035,.03 ALPHA=-30 SEEDS=3 TRIES=12 TAG=az120oneh30 QSEED=results/mac/rim_tipper3_q_az120_g35_a-30.json MEET=.58,.10,1.08 "VIA=.62,.20,1.09;.6625,.2869,1.07" HOV=.02 MEETR=1 ONEH=1
LIMIT_MB=8000 bash tools/runw.sh logs/mac/rim_tipper_load_recheck_az120.log rim_tipper_load_recheck.py results/mac/rim_tipper_load_az120oneh30.json
LIMIT_MB=8000 bash tools/runw.sh logs/mac/rim_tipper_confirm_az120.log rim_tipper_confirm.py HOLDER=120,.035,.03 TAG=az120
```

## Open points
- The tipping swing is checked at 30 deg intervals (0-120 deg) at AZ 120 only, not continuously, and not at AZ 105.
- AZ 120 blocks the wok lift (see Assumptions). AZ 105 does not, but has the 9.4 deg follow step. A re-run of AZ 105 with denser vias may remove the step; not done.
- The plume distance of the loading arm was estimated from geometry, not measured.
- The (i) chain ends at the release. The empty arm's path back to the hub or to the stir start was not planned.
