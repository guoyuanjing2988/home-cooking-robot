# PARK IN WOK (Mac, 2026-10-13): NOT PASSED. Stopped at the 16:52 hard stop

**Result: FAIL.** (a) passes. (c) passes only with the spatula left at the **stroke-1** start, not stroke 0. (b) failed every method tried at both stroke 0 and stroke 1. Each time the blocker was the closed wall-cabinet door, not the spatula. There is no video, because no full chain passed.

Idea under test: the spatula never leaves the wok. At a stir stroke-start state the jaws open, the empty gripper backs off 6 cm, goes to the cup, does the cup chain, comes back and closes. It is then in exactly the same q, so the stir cycle stays on its own IK branch by construction.

## How it was modelled
- **Park pose.** The first state of stroke k (`work<k>`) of `results/r19/stir/stirwalk2_h_scrape_dice_r17.json` (jaw sign -1, cart 0.55).
  - Stroke 0: q = (.55, -.21, 0, -0.071, -1.139, -2.352, -1.249, 1.943, 6.207, .015, .015).
- **Spatula left in the wok.** The 6 `R_gripper_spatula*` geoms (5 blade parts + handle) of the R15 stir model (`r15_spatula=.45, r15_spatula_jaw=-1`) are taken at that q. They are copied as world geoms (`park_*`) at exactly that pose, with the same type, size and contact classes as `kitchen16._add`. So the spatula sits at the held pose.
  - The handle top is at z ≈ 1.15-1.16 m.
- **Checks.** The unchanged `checker.py`, by way of the `r19hub_cup` machinery:
  - `check_path`: segments are cut to a ≤ 4 mm point bound, then the fast screen and the full check run on every state.
  - The union scene, plus the spatula in the wok.
  - The cup play states are re-checked the way `r19cup_recheck.py` does it.

## Pieces (stroke 0 = `work0`)
| piece | result | time | min reserve | file |
|---|---|---|---|---|
| (a) open the jaws at the stroke start, retreat 6 cm along the approach axis (-R_prep x = (0, -.47, +.88): up and toward the aisle; 6 IK steps of 1 cm, pose error 0.0 mm, ≤ 1.6 deg per step) | **pass** | 0.5 s jaws (assumed) + 0.75 s retreat (with the 0.6 s join) | env 27.0 mm, self 2.0 mm | `results/mac/park_in_wok_a.json` |
| (b) retreated state -> CUP (CUP relabelled by 2pi on joints 4, 6, 8 within the cup action's allowed shifts; pan -0.07 -> -3.17 rad, cart .55 -> .05) | **fail**, all 21 tries | - | - | `results/mac/park_in_wok_b.json` |
| (c) the cup chain (`chain_cup_final.json`, 224 play states) with the spatula at the stroke-0 pose | **fail**: 123/224 states hit | (20.6 s) | -10 mm | `results/mac/park_in_wok_c.json` |
| (d) reverse of (b) + (a) | not reached (needs (b)) | - | - | - |

**Why (b) failed.** It is not the spatula: every try is stopped by the **closed upper cabinet door `r07_closed_door_1_0`**.
- The straight move fails at 11 % with `R_geom_16`.
- The tuck at the mid, retreat, CUP or H_WOK cart fails at 33-38 % with `R_geom_21`.
- The joint-ordered vias fail with the gripper OEM envelope or the arm against the same door.
- The cause is the stroke-start posture. The wrist is high (the retreat goes up), and the pan has to swing about 177 deg to face the cup pad. That sweep goes through the wall cabinet.
- The planner was not run, because the cart moves (.55 -> .05).

**Why (c) failed at stroke 0.** The spatula handle, sticking up out of the wok, is hit by the arm (`R_geom_25/26/28`) in play steps 49-68 and later. These are the steps where the held cup goes over the wok.

## Other stroke starts as the park pose (piece (c) only, `park_in_wok_keys.py`)
| park pose | (c) result | states hit | min reserve | file |
|---|---|---|---|---|
| work0 | fail | 123 | -10 mm | `park_in_wok_c.json` |
| **work1** | **pass** | 0 | **2.0 mm** (robot-env, step 126). The cup chain alone has 2.2 mm | `park_in_wok_c_work1.json` |
| work2 | fail | 125 | -10 mm | `park_in_wok_c_work2.json` |
| work3 | fail | 20 (steps 79-88, 132-141) | -1.6 mm | `park_in_wok_c_work3.json` |
| work4 | fail | 131 | -10 mm | `park_in_wok_c_work4.json` |

In every failing case the only part hit is the spatula handle.

## Stroke-1 park (work1): (a) and (b)
Stroke 1 start: q = (.55, -.21, 0, 0.042, -1.499, -2.067, -1.143, 1.941, 5.800, .015, .015).

| piece | result | time | min reserve | file |
|---|---|---|---|---|
| (a) open the jaws + retreat 6 cm (axis (.23, -.41, +.88), pose error 0.0 mm, ≤ 1.6 deg per step) | **pass** | 0.5 s + 0.75 s | env 2.3 mm (the open jaws are at 8.4 mm), self 3.9 mm | `results/mac/park_in_wok_a_work1.json` |
| (b) retreated state -> CUP. 16 tries before the 330 s budget ran out: straight, 4 tucks, 3 r19hub TCP retreats alone and with the mid tuck, and joint-ordered vias | **fail** | - | - | `results/mac/park_in_wok_b_work1.json` |
| (c) cup chain with the spatula at the stroke-1 pose | **pass** | 20.6 s | 2.0 mm | `results/mac/park_in_wok_c_work1.json` |
| (d) | not reached | - | - | - |

**Why (b) failed at stroke 1.** The obstacle is the same as at stroke 0, the wall cabinet doors:
- 7 tries stopped on `R_geom_21`/`r07_closed_door_1_0`;
- 7 on `R_geom_16`/`r07_closed_door_1_0` or `_1_1`;
- 1 on the gripper envelope against the door;
- 1 on `R_geom_16`/`sink_front_rim`.

The 2pi-relabelled CUP needs the pan to swing about 180 deg, and the upper arm sweeps through the cabinet. The spatula did not block any try.

## Totals
No total, because (b) is unresolved. Old sequence: 27.4 + 20.6 + 27.4 = **75.4 s**.
- If (b) passed with a transit of t seconds, the new sequence would be 2 × (0.5 + 0.75 + t) + 20.6 s.
- That stays below 75.4 s as long as t < 25.8 s.

## Files
- `park_in_wok.py`: pieces (a), (b) and (c).
  - Options: `KEY=work<k>` (default work0), `PIECES=abc`, `BUDGET_S`.
  - It imports `r19hub_cup.py` and swaps in the union scene with the spatula added. No existing file was edited.
- `park_in_wok_keys.py`: piece (c) for other stroke starts.
- Logs:
  - `logs/mac/park_in_wok1.log`
  - `logs/mac/park_in_wok_keys1.log`
  - `logs/mac/park_in_wok_work1.log`

## Caveats
- With the jaws closed (.015) at the stroke start, the checker reports a 17 mm env reserve, so the fingers are not in contact with the copied spatula geoms. That is how the R15 stir model grips the spatula (`R_gripper_spatula` is welded to the gripper), and it is not verified as a physical grasp. Re-closing in (d) therefore depends on the R15 grip model, not on a contact model.
- (c) re-checks the play states only (as `r19cup_recheck.py` does), not the cup chain's own grasp approaches.

## Next steps
- (b) needs a route around the wall cabinet. One option is an arm-only planner move at cart .55 to a low "elbow-down" via first, then the cart move.
- Another option is a lower stroke start: work1's is the one that also clears the cup chain.
