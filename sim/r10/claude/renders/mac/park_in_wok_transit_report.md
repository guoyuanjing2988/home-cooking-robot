# PARK IN WOK, transit (b) and return (d) (Mac, 2026-10-13, queue task 1)

**Result: PASS.** Stroke-1 park. The full sequence passes the unchanged checker on every state:
- (a) release and retreat;
- (b) the move to the cup endpoint;
- the cup chain, with the spatula standing in the wok;
- (d) the same states in reverse, back to the identical stroke-1 start.

**Total 38.3 s, against 75.4 s for the park-free baseline (37.1 s saved).**

- Video: `renders/mac/park_in_wok.mp4`, 20.9 s. It covers the empty moves plus the cup chain, with the spatula drawn in the wok (brown handle). Jaw times and the 2 s pour dwell are not shown, as in r17video.
- Results:
  - `results/mac/park_in_wok_b2_work1_r1.json`: piece (b), with its pieces and all states.
  - `results/mac/park_in_wok_seq_work1.json`: the whole sequence, its state-wise re-check and the times.

## What changed against the failed (b) of `park_in_wok_report.md`
Two things changed, and the posture is the same R19 hub tuck as before:
1. **The cup endpoint gets the other 2pi label.** The old run labelled CUP nearest the retreat state, giving pan -3.17 rad. The tuck-to-CUP leg then swung the pan about 216 deg the "negative" way, and the forearm (`R_geom_21`) went through the closed door `r07_closed_door_1_0`. That was the failing segment in all 4 old tuck tries; the old fail states show the cart at 0.13-0.38 and the pan at -0.72.
   - The fix is to label CUP nearest the tuck instead: pan +3.114, the label of the checked hub edge CUP-H_WOK. The pan then swings about 143 deg the other way and stays out of the cabinet.
   - Both labels are within the cup action's allowed shifts.
   - The relabel of the whole cup action is {pan +1, shoulder lift +1, wrist 1 -1, wrist 3 +1} x 2pi. All 238 cup states stay in range.
2. **The motion is split into three pieces.** The arm folds first with the cart fixed, then the cart drives with the arm frozen, then the arm unfolds. The old vias moved the cart and the arm together.
   - The tuck's wrist 3 is relabelled +2pi (to 4.977 rad), nearest the retreat. This gives a 41 deg wrist turn instead of 401 deg.

The RRT planner was not needed: the straight pieces passed first time. No hand-designed low pose was needed either (`LOWS` ik1-ik4 are in the script but were not run).

## The sequence (stroke-1 park, cart 0.55)
| piece | method | time | states (full check) | min reserve env / self |
|---|---|---|---|---|
| (a) jaws open .015 -> .025 at the stroke-1 start, retreat 6 cm along -approach (park_in_wok.py, recomputed; same retreat q to 1e-6) | IK steps, check_path | 0.5 s (assumed) + 0.75 s | 62 | 2.3 (open jaws to spatula handle) / 3.9 mm |
| (b1) retreat -> R19 tuck, cart fixed at 0.564 | straight in joint space | 2.44 s (110 deg, max shoulder lift) | 758 | 31.3 / 2.0 mm |
| (b2) cart 0.564 -> 0.172 (H_WOK), arm frozen in the tuck | straight, cart only | 2.17 s (0.392 m) | 105 | 60.0 / 3.9 mm |
| (b3) tuck at 0.172 -> CUP (cart 0.05) | straight (= the hub edge CUP-H_WOK, re-checked with the spatula) | 2.99 s (143.6 deg) | 895 | 2.0 / 2.0 mm |
| cup chain: approach, grasp, carry, 120 deg pour + 2 s dwell, return, release | chain_cup_final.json, relabelled | 20.6 s | 7 + 224 + 7 | 2.0 (wrist to wok tile, play step 126) / 2.3 mm |
| (d) = (b) reversed + (a) reversed, ending with the jaws closing at the identical stroke-1 q | same states | 8.85 s | (same states) | same |
| **total** | | **38.3 s** (1.25 + 7.6 + 20.6 + 7.6 + 1.25) | 1,759 distinct empty states + 224 held | **2.0 mm** |

- **Baseline: 75.4 s.** That is the spatula to the far rest (27.4 s), the cup chain (20.6 s) and back (27.4 s).
- **Saving: 37.1 s per cup pour during a stir.**
- Each of b1, b2 and b3 carries its own 0.6 s join (r19hub timing: joints ≤ 60 deg/s, cart ≤ 0.25 m/s).
- Joining b1 and b2, with the cart moving while the arm folds, was not tried. It could save about 1 s more.

**Independent re-check** (`park_in_wok_seq.py`): every distinct state, full checker, **0 failures**.
- Empty-gripper states run in the r19hub_cup union scene plus the spatula in the wok. That scene has lever open and closed, lid on the pot and in the rack, dishes on both plating spots, and the cup pad, post and cup.
- The held play runs in the cup chain's scene plus the spatula.
- The last state equals the stroke-1 start exactly (`end_equals_start: true`).

## Assumptions (not verified beyond the checker)
- **Park pose.** The stroke-1 start of `stirwalk2_h_scrape_dice_r17.json`, as in `park_in_wok_report.md`.
  - Stroke 0 is not usable: (c) fails there because the arm hits the spatula handle.
  - So the stir cycle has to be interrupted at the stroke-1 start, not stroke 0.
- **The spatula left in the wok.** Static world geoms at the held pose: they do not tip or slide when released.
- **Re-grasp.** Re-closing the jaws at the identical q relies on the R15 grip model (the spatula welded to the gripper), as before. The checker reports the closed state at 17 mm from the copied geoms.
- **Union scene.** It also contains the spatula on its R18b rest (-1.15, 0.30), which is conservative here.
- **Heat.** Heat is off during the cup pour (no plume rule), as in the cup chain.
- **The 1 cm grasp-approach steps.** The cup grasp approach and release states are r17chain's 1 cm IK steps, not at the 4 mm point bound. They are re-checked state-wise here, now with the spatula present.

## Attempt log
| run | change | result |
|---|---|---|
| park_in_wok.py (earlier today) | 16 vias: straight, tuck (mid / retreat / CUP / H_WOK cart, the cart moving during the unfold), TCP retreats, joint-ordered | all fail on the closed doors |
| `park_in_wok_b2.py` r1 | POSES=tuck, CUP labelled nearest the tuck, 3 pieces | **pass** at the first candidate (50 s run) |
| `park_in_wok_seq.py` | whole sequence re-check | 0 failures |
| `park_in_wok_video.py` | render | `renders/mac/park_in_wok.mp4`, 628 frames (the first render used a 1/30 s floor per state and ran to 132 s; it was re-rendered with time-model sampling) |

## Files (new, nothing existing edited)
- `park_in_wok_b2.py`: piece (b). Options: KEY, POSES (tuck, ik1..ik4), XC (cart of piece b2), PLAN_S, SEED, TAG.
- `park_in_wok_seq.py`: assembly and re-check.
- `park_in_wok_video.py`: render only.
- Logs: `logs/mac/pwb2_1.log`, `logs/mac/pw_seq.log`, `logs/mac/pw_video.log`.

Reproduce (from build_day):
```
LIMIT_MB=8000 bash tools/runw.sh logs/mac/pwb2_1.log park_in_wok_b2.py KEY=work1 POSES=tuck XC=.172 PLAN_S=150 DIAG=1 TAG=_r1
LIMIT_MB=8000 bash tools/runw.sh logs/mac/pw_seq.log park_in_wok_seq.py KEY=work1 TAG=_r1
LIMIT_MB=8000 bash tools/runw.sh logs/mac/pw_video.log park_in_wok_video.py results/mac/park_in_wok_seq_work1.json renders/mac/park_in_wok.mp4
```
