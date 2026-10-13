# SPATULA_PARK_CUP_POUR (Mac, 2026-10-13): NOT PASSED. Stopped at 16:15, partial pieces only

**Result: FAIL.** No continuous chain exists. Two pieces pass on their own: the park chain (10.2 s) and the cup chain re-checked with the spatula parked. Two parts were not solved:
1. **Exact join to the R18b stroke-start state.** The park chain only passes when it reaches the stir stroke start in its own IK state. That state is on a different branch from the R18b chain's end state (pan -119 deg, wrist 1 / wrist 2 about 170 deg apart, cart 1.08 m against 0.47 m). It is the same blade pose, but it is not the state the R15 stir cycle starts from.
2. **Empty-gripper transit park <-> cup pad.** It failed every method in `r19hub` (straight, tuck vias, retreats, 16 joint-ordered vias). The straight move fails at once: a finger meets the parked spatula handle. Cart 0.83 to 0.05 m, so the planner (cart fixed only) does not apply.

So there is no total time to compare against 75.4 s. Indicative only, not a check: park 10.2 s + cup 20.6 s + unpark 10.2 s + two transits (about 6 s each if one were found) is about 53 s.

## Park (assumption)
- The spatula lies flat on a 2 cm pad (the R18b cradle, `SPATELEV=8 SPATROLL=180`, handle toward the robot). Blade centre at (0.55, 0.445, 0.93), `TOOL_XY` (0.55, 0.40).
- Where: on the counter strip between plating spot 1 (x 0.31-0.55) and the cooker (x >= 0.63), behind the wok grip block.
- Why there:
  - x 0.575 / 0.56 failed: the blade or handle comes within 5 mm of the cooker and of the wok's keyed grip block (x 0.573-0.617, z 1.01-1.04).
  - x 0.55 clears both.
- Plume: the gripper at the park is about 0.3 m from the wok axis (0.83, 0.17). The rule needs >= 0.20 m.
- Cost of this spot: the handle passes about 5 cm above the rim of plating spot 1, at y 0.03-0.36. A dish taller than about 4 cm at spot 1 would touch it.
- A raised cradle (15 cm post) let the park chain pass too. It was then dropped: the cup chain's carry from the pad to the lane hits the raised handle.

## Pieces that pass (unchanged checker)
| piece | file | result |
|---|---|---|
| park pick -> stroke start, run in reverse for the park | `results/mac/combo_spatula_park48.json` | pass. **10.2 s** against 26.9 s for the far rest. Min reserve 2.6 mm, approach 23 mm, PGC 1.3 N·m, joint ratio 0.32. Cart 0.83 -> 1.11 |
| cup chain with the spatula on the park | `results/mac/combo_cup_park.json` | pass, **20.6 s**, 2.2 mm, the same as `chain_cup_final` |
| PARK -> CUP transit | `results/mac/combo/edge_PARK__CUPC.json` | **fail** (see above) |

## Attempt log (`logs/mac/combo_park*.log`)
| runs | change | what failed |
|---|---|---|
| park1 | park x .575, R18b method (two anchors, lane at y -.02) | blade 5 mm from the cooker |
| park2 | x .56 | handle vs wok grip block; lane join blocked (spatula over the robot base in the shuffle) |
| park3-4 | x .55, LANEP .66,.18,1.16, PICKC .24 | pick-side and stroke-side lane arrivals on different elbow branches (+1.7 against -1.96 rad); join 212-220 deg, self / upper-door hits |
| park5-14 | follow back from the pinned stroke start only, lane variants | 10-12 deg IK jump near 'out and up' (wrist singularity) |
| park15-19 | SPATROLL / SPATYAW | handle meets the forearm, or the same jumps |
| park20-33 | finer steps (FSTEP .4/.25); fixed park cart (and a cart-continuity fix in the copy) | past the jump, then the pose error stays at 5-6 mm going down to 'lifted' (reach / joint limit on the pinned branch) |
| park34-42 | raised cradle .10/.15, elbow-negative pick filter, fixed lane cart, PLAN=1 | joins still blocked (shuffle / self), planner failed. Note: in park34-37 zsh did not split the MODE argument, so ELBOW/SPATLANEC were not applied |
| park43-48 | `STROKEFREE=1`: one piece from the park anchor straight to the stroke start (no pinned state) | **pass** (park48 chosen); the stroke-start state differs from R18b (see above) |
| combo_cup_park | cup chain with the spatula on the park | pass |
| combo edge | PARK -> CUPC (both chains relabelled by 2pi to sit close) | fail |
| combo edge foot | PARK -> F_PARK (arm-only to the tuck at the park cart, straight then `planner.plan` 90 s) | fail: straight hits the cart mast (`R_geom_21` / `R_cart_mast`); planner budget exhausted. `results/mac/combo/edge_PARK__F_PARK.json` |

## Files
- `r19combo_chain.py`: copy of `r19bowl_chain.py`.
  - The cup station is at .45 and the cup is on it (except ACT=cup).
  - New options: `FIXQ`, `LANEP`, `PICKC`, `NOPICKANCHOR`, `ELBOW`, `FSTEP`, `CRADLEH`, `STROKEFREE`.
  - A cart-continuity fix after free-cart frames, in the copy only.
- `r19hub_combo.py`: copy of `r19hub_cup.py`. The spatula is on the park, plus nodes PARK / CUPC and command `hubs_combo`.

## Next steps if continued
- Re-plan the R15 stroke-0 entry from the park branch, or add a stroke-start re-grasp state.
- For the transit, first an arm-only retreat from the park (planner, cart fixed), then a tuck at the park cart.
