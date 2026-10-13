# R19: motion instructions as a library of verified movement sets (2026-10-13)

**The user's request:** "Goal is less money, more smooth movements. Could consider lots of predefined movements then movement sets. therefore no need check after each tiny movement."

**The idea:**
- Check every predefined movement once, offline, with the same checker as before.
- Join movements only at fixed **hub** states, so a sequence of sets needs no new geometric check.
- Re-check after a layout change only the sets whose stored swept volume touches the changed fixture.

Nothing is skipped. The checking moves from "every new sequence" to "every library entry, once".

**Labels used here:**
- **[measured]**: computed in this round from the saved data, or checked in the sim with the unchanged checker.
- **[proposal]**: a design choice or estimate. It has not been checked.

**Files** (all new; no existing file was changed):
- `r19prim_inventory.py` → `results/r19/prim/inventory.json`, `segments.json`
- `r19prim_swept.py` → `results/r19/prim/swept.json`, `swept_voxels.npz`
- `r19prim_transit.py` → `results/r19/prim/transit.json`
- `r19prim_library.py` → `results/r19/prim/schema.json`, `library_examples.json`, `library_size.json`

## 1. Summary

| Question | Answer | Basis |
|---|---|---|
| How much of today's motion is made of recurring sub-motions? | 7 classes recur in ≥ 3 actions (carry, seat lift, insert, extract, grasp approach, meet join, gripper). They hold 74 % of the motion time and 44 % of the states. Only the lever, the lid roll and the stir strokes are bespoke: 9 % of the time. The bespoke share of states is 45 %, because the stroke is sampled every 10 ms. | [measured] inventory of the 5 checked actions + the R15 stir cycle |
| Is re-planning repeating identical work? | Yes. The R18 second plating spot was re-planned from scratch (279 s compute), yet 283 of its 470 states are identical to the first spot. The plating tip itself is the same arm motion (0.0000° joint difference) with the cart moved 0.26 m. In the spider chain, 184 of 516 states are repeats of the same path planned twice (out and back). | [measured] |
| Do hubs exist in the data? | Yes. The wok and spider actions start and end at the identical state. The spider's out-and-back keyframes are identical states (0.0°). The wok's states before and after each 90° tip differ by ≤ 0.04°. | [measured] |
| Can new actions be made only from verified pieces? | Yes, for two of them. **WOK_DUMP_RINSE** (42.2 s) and **WOK_FILL** (36.5 s) are the verified wok chain with its tip loops left out. The only new geometry is two micro-joins (0.04° and 0.03°, checked here, no hits). FILL's 1 L of water on the way back gives PGC 5.88 N·m (limit 7) and a joint ratio of 0.55. The meal schedule had used *estimates* for these two. | [measured] |
| Re-checking after a layout change | A swept-voxel screen (67 ms per fixture) flags the segments to replay. On 4 spatula rests tried in R18 it missed no real hit. For the chosen R18b rest it flagged 4 segments (180 states, 2.9 s replay), against 1,677 states (26.7 s) for a full replay or 928 s to re-plan the chains. | [measured] |
| Free moves between actions (never checked until now) | 2 of the 4 free moves in the plating sequence are now verified: faucet ↔ wok, 6.96 s each against an estimate of 6.2 s. The 2 moves between the spatula rest and the faucet are **not straight-line feasible**: 27 straight and via candidates each hit something, and RRT-Connect (tried on one of them) found nothing in 100 s. They need designed clearance hubs and a planned transit. | [measured] |
| Library size for meals A/B/C | 34 distinct movement sets: 12 verified, 2 composed from verified pieces, 1 partly verified, 19 not verified. 8 of the 34 are plain reversals. 28 hubs, about 24 transit sets, 16 primitive classes, about 340 stored segments. The meals execute 71 / 167 / 103 set instances. | [proposal] catalogue; statuses [measured] |
| Smoothness | Today every keyframe and join is a velocity zero. In the library, sets are stored as continuous paths with blends through non-contact waypoints. Stops per set fall from 27 to 16 (wok plate + rinse), 14 to 9 (lid), 9 to 6 (spatula). | stop counts [measured] from the segment classes; the blend policy is a [proposal] |

**Recommendation** (sections 3 and 10):
- A **hub-and-spoke skill library**, verified offline with the unchanged checker.
- Movement sets carry pre/post-conditions and runtime monitors.
- Execution is a dense, time-parameterized joint trajectory streamed to the arm (UR5e: RTDE `servoj` at 500 Hz). Alternatively `movej`/`movel` with blend radii no larger than each segment's measured clearance reserve.
- No geometric planning at runtime.
- DMPs only as an offline shape generator. A PRM-style roadmap only for the hub transits.

## 2. Inventory: what the checked actions are made of [measured]

`r19prim_inventory.py` puts every saved playback state through forward kinematics to recover the held object's pose. It then splits the play at the keyframes and joins, and labels each segment with a primitive class.

The split is checked against r17chain.py's timing model. The segments add up to the saved action times: 49.0 / 3.5 / 20.2 / 52.6 / 27.0 s, against saved 48.9 / 3.5 / 20.2 / 52.6 / 26.9 s.

| Primitive class | Count | States | Time s | Actions using it | What it is |
|---|---|---|---|---|---|
| carry | 27 | 961 | 92.2 | 4 | held object moved in free space (13 of 27 are "cart-dominant": the arm joints move < 10° in total, the cart carries the object; 44.9 of 92.2 s) |
| meet_join | 8 + the 0.5 s hand-off | 18 | 6.0 | 5 | joint-space join at a meet, with cart shuffle; 5 of the 8 move 0–0.5° and cost only the fixed 0.6 s |
| approach | 9 | 63 | 5.4 | 5 | empty gripper 6 cm along the approach axis (contact window) |
| gripper | 5 | 0 | 8.0 | 5 | grasp + release 0.8 s each |
| seat_lift / seat_lower | 4 / 2 | 14 / 6 | 1.0 / 0.4 | 4 / 2 | 1.2–5.2 cm straight off / onto a support (contact window) |
| insert / extract | 4 / 3 | 54 / 46 | 5.2 / 4.4 | 4 / 3 | straight moves into or out of a tight place: under the tap, into the rack, into the pot, down to the stroke start, out from under the hood |
| tip / untip | 3 / 3 | 146 / 146 | 7.2 / 7.2 | 2 | wok 90° (plate, sink), spider 110° |
| dwell | 4 | 0 | 13.0 | 2 | plate 2 s, tap 5 s, emptied 1 s, drain 5 s |
| lever | 1 | 15 | 0.8 | 1 | faucet lever 30° about its pivot |
| reorient | 1 | 45 | 2.0 | 1 | lid rolled 90° |
| stroke / stroke_return | 5 / 5 | 915 / 195 | 9.3 / 3.1 | 1 | R15 stir: working part at 10 ms IK steps; air return in joint space |
| **Total** | | **2,624** | **165.3** | | 5 checked actions + the stir cycle + the 0.5 s hand-off |

**Per action:**

| Action (checked) | States | Segments | Motion time s | Compute of the final run s | Anchor candidates followed |
|---|---|---|---|---|---|
| Wok plate + sink rinse (`chain_wok_s-1_final`) | 470 | 25 | 48.9 | 275 | 26 |
| Same, plating spot 2 (`chain_wok_s-1_r18plate2b`) | 470 | 25 | 48.9 | 279 | 35 |
| Faucet lever open (`chain_lever_s+1_final`) | 16 | 4 | 3.5 | 26 | 8 |
| Lid off → rack (`chain_lid_s-1_final`) | 205 | 12 | 20.2 | 133 | 32 |
| Spider rest → pot → plate → rest (`chain_spider_s+1_final`) | 516 | 25 | 52.6 | 215 | 44 |
| Spatula rest → stroke start (`chain_spatula_s-1_r18roll-1.15_.30`) | 249 | 8 | 26.9 | 433 | 32 |
| R15 stir cycle, 5 strokes + close (`stirwalk2_h_scrape_dice_r17`) | 1,110 | 10 | 13.15 (5 × 2.63) | not recorded | — |

**Shared versus bespoke:**
- **Primitive classes.**
  - Shared (≥ 3 actions): 74 % of motion time, 44 % of states.
  - Bespoke (1 action: lever, reorient, stroke, stroke return): 9 % of time, 45 % of states (the stroke's 10 ms sampling).
  - Tip, untip, dwell and seat_lower appear in 2 actions.
- **Identical geometry already re-planned.**
  - **Plating spot 2:** 283 / 470 states are bit-identical to spot 1. Pick, lift and the whole sink half are identical. The plate tip/untip (90 states) is the same arm motion with the cart 0.26 m left: max joint difference 0.0000°. Only the two carries to and from the plate changed (46 + 44 states). The re-plan took 279 s.
  - **Spider:** 184 / 516 states are repeats. Out and back from the same anchors gave identical states at 5 keyframe pairs (0.0°).
  - **Wok:** pick and set-down share the same anchor. States 0–25 (pick → near the lane) equal states 469–444 in reverse order: the way out is the way back. The other 3 repeats are duplicated join endpoints.
  - **Faucet close, lid on, spatula back and carrier out** are plain reversals (r17seq.py and arm_checked.json already use them that way).
- **Compute history (lower bound: only the last run per file name is saved).**
  - 142 saved R17/R18 chain runs, 20 of them passing, **8.5 h of compute** for 5 actions.
  - Wok: 69 runs / 3.7 h. Spatula: 43 runs / 3.6 h. Spider: 14 runs / 0.7 h. Lid: 12 runs / 0.5 h. Lever: 4 runs.
  - Most of it is design search: the variants and failures that found the layout. A library does not remove that search. It stops repeating it.

## 3. The layered instruction set [proposal]

```
recipe step      "干锅土豆: pork, 豆瓣, chili, potato, sauce; stir 90 s; plate"        (meal16.py step)
  └ task         add_ingredients(3) · stir(90 s) · plate(spot 1)
     └ movement set (skill)   CUP_FETCH(slot k) · CUP_POUR(wok) · CUP_RETURN · STIR_CYCLE×7 ·
                              SPATULA_STOW · FAUCET_OPEN · WOK_PLATE_RINSE(spot=1) · FAUCET_CLOSE · SPATULA_FETCH
                              (+ TRANSITs between their hubs)
        └ primitive           seat_lift · carry · tip · dwell · untip · insert · extract · join · approach ...
                              (parameterized segment, stored as states, verified offline)
           └ controller command  time-parameterized joint + cart trajectory (servoj stream or movej/movel + blend r),
                                 gripper commands, cooker / drum / faucet I/O at named points
```

**Rules:**
1. **Every set starts and ends at a hub.**
   - A hub is a fixed full state: cart x, base, 6 joints with their winding, and the jaws. Each hub has a hand content: empty, wok, spatula, spider, lid, carrier, cup.
   - Two sets may follow each other only if the end hub of one is the start hub of the next, **as the same vector**. The junction is then not a motion at all, so it needs no check.
   - In the plating sequence, 8 of 8 junctions are identical state vectors [measured: `library_examples.json` plating_sequence].
2. **A set is a fixed graph of primitives.** Its geometry never changes at runtime. Only verified parameters may change (section 5).
3. **Every primitive is verified offline** with the unchanged checker: 10 mm robot-environment and 5 mm gripper/held-environment gaps; ≤ 1 cm / 2° object steps (≤ 4 mm point bound per DECISIONS); contact windows only at grasp, release and declared strokes. The record stores:
   - the min clearance reserve, which is its tolerance budget (section 5);
   - the loads (PGC moment, joint ratios);
   - the swept volume (section 6);
   - the scene version it was checked in.
4. **Reversal is free.** A primitive verified forward is verified backward: the same states, the same scene. Lid on, faucet close, spatula stow and carrier out need no extra check.
5. **Cart translation is a parameter, not a new path.**
   - Moving a primitive along the rail keeps the arm motion identical. Only its swept volume moves, so it only has to be screened against the environment at the new x (section 6).
   - Measured: the R18 plate tip at spot 2 is the spot-1 tip with the cart at −0.488 instead of −0.228.

**Hubs that come straight from the data** (`library_examples.json` hubs; q = cart, base y, base yaw, 6 joints, 2 jaws):

| Hub | Hand | q (rad, m) | Source |
|---|---|---|---|
| H_wok_pre | empty | [0.17223, −0.21, 0, −3.14504, −5.564, −1.42593, 2.89644, −5.39472, 4.28752, .025, .025] | wok chain grasp approach end (6 cm back from `pick#0`); the release retreat after `set down#16` ends at the same vector |
| H_fau_closed_pre | empty | [−0.67981, −0.21, 0, −2.64658, −6.07183, −0.50395, −5.73507, −0.65146, −3.66099, .025, .025] | lever approach at `closed#0` |
| H_fau_open_post | empty | [−0.67981, −0.21, 0, −2.6571, −6.08949, −0.76525, −5.84373, −0.63196, −2.87844, .025, .025] | lever retreat at `open#1` |
| H_lid_on_pre | empty | [0.88629, −0.21, 0, 2.70331, 6.19516, 1.51023, −0.23281, 5.38357, 0.57274, .025, .025] | lid approach at `lift off#0` |
| H_lid_rack_post | empty | [1.32563, −0.21, 0, −3.74016, 5.95982, 2.00826, −0.43955, 5.9546, −4.20824, .025, .025] | lid retreat at `in the rack#8` |
| H_spat_pre | empty | [−1.48, −0.21, 0, 6.12163, −2.7081, −2.30101, −0.25584, −3.44266, −0.57333, .025, .025] | spatula approach at `pick#0`, R18b rest |
| H_spat_stroke | spatula | [0.47238, −0.21, 0, 6.2271, 4.9264, −2.21677, −1.16078, −4.33986, −0.06022, .015, .015] | spatula chain end `stroke start#5` |
| H_stir0 | spatula | **not stored** | R15 stroke-0 start, reached by the verified 0.5 s hand-off. r15stirwalk2.py saves no joint states, so the stir cycle cannot be a library entry until it is re-run with state output. |
| (spider) lane, lane middle, over the pot, over the plate | spider | identical out/back states (0.0°) | split the spider loop into FETCH / SCOOP / DUMP / STOW at no cost |

**Travel hubs and transits** [proposal, partly measured]:
- Empty-hand moves between stations become **TRANSIT** sets, verified like any other set. They are no longer an unchecked `|dx|/0.25 + 1 + 1.6 s` estimate.
- A hub-and-spoke layout keeps the number small:
  - one tucked "travel" posture at each cluster's cart x (about 6 along the counter);
  - one spoke per station hub;
  - cart-only moves between neighbouring travel hubs.
- That is about 24 transits for the meals, against N² pairs.
- What the first check found [measured, `transit.json`, step ≤ 1° of the largest joint and ≤ 1 cm of cart, as r17chain's joins]:

| Transit | Result | Time (estimate before) | Note |
|---|---|---|---|
| faucet (open) → wok | **verified**: joints first, then cart | 6.96 s (6.2) | 227 states, reserve ≥ 11.8 mm |
| wok → faucet (open) | **verified**: cart first, then joints (the same path reversed) | 6.96 s (6.2) | reserve ≥ 16.7 mm |
| spatula rest → faucet (closed) | **not found** | (5.6) | All 27 straight / decoupled / via / other-winding candidates hit something: the wrist link meets its own finger halfway through the joint swing (wrist 2 passes ±180°), or the upper-cabinet door. RRT-Connect, 100 s: no node added, because the direct-edge check with full bounds used the whole budget. |
| faucet (closed) → spatula rest | **not found** | (5.6) | Leaving the faucet pre-grasp toward the rest, the fingers meet the lever block, spout or column within the first 1–11 % of the move in 24 of 27 candidates; the other 3 hit the counter, an upper cabinet or the arm's own finger. Planner not tried. |

- **Lesson:** a 6 cm grasp pre-pose is not a good hub for long moves.
  - Hubs need a **clearance retreat**: further out along the approach axis, then up into a tucked travel posture with the wrist kept on one side of ±180°.
  - That retreat is verified once as part of the set.
  - The meal times are almost unaffected, because the verified transits are within 0.8 s of the estimate. What changes is that the plating sequence was never fully feasible as estimated; the library makes that visible.

## 4. Pre/post-conditions, monitors, failure and recovery [proposal]

**Per set, conditions are runtime checks of state flags and sensors.** None of them is geometric. Examples, encoded in `library_examples.json`:

| Set | Pre-conditions | Post-conditions |
|---|---|---|
| FAUCET_OPEN | lever closed; hand empty; clip-on block present | water flowing (camera / sound); gripper released |
| WOK_PLATE_RINSE(spot) | wok keyed in the cooker slot; heat 0; food ≤ 1.15 kg; plate in the guarded stand at that spot; faucet open; hand empty | wok back, rinsed, empty; dish on the plate; hand empty |
| LID_OFF_TO_RACK | lid on the pot, tab to the front; rack slot free; heat off / steam vented; hand empty | lid upright in the rack; hand empty |
| SPATULA_FETCH | spatula on its pad flipped (sense −1); wok on the cooker; pour drum swung away; hand empty | spatula in hand, sense −1; blade 1 cm off the steel at stroke 0 |
| STIR_CYCLE | spatula in hand; heat ≤ half while the spatula stops; nobody within reach of the wok | spatula at stroke-0 start |

**Before a set starts:**
- The measured joint state must match the start hub within 0.05° and 0.5 mm of cart.
- Every pre-condition must be true.
- The scene version the set was verified in must equal the current layout version.

**Monitors while a set runs.** The nominal values are recorded during verification, and again on the real robot at commissioning:
- joint current / torque deviation from the model along the stored trajectory (UR5e: also its flange F/T sensor);
- gripper jaw position and force band, plus the finger-root force sensor (R12);
- camera checks at named points: object present before a grasp, food out after a tip, lid seated;
- person presence: slow, then pause;
- cooker temperature;
- trajectory tracking error.

**Failure handling.** Runtime never plans a new free path. Every state on a verified path is verified, so recovery runs **along the stored path**.

| Event | Action |
|---|---|
| Pre-condition false (plate missing, slot occupied, spatula wrong face up) | Do not start. Re-sense once; else use a verified alternative (plate spot 2 when spot 1 is full); else ask the user. |
| Hub mismatch at start (after a manual move or an E-stop) | Do not start. Recover with a dedicated, verified "home" set from the nearest hub, or the user jogs the arm to a hub (teach-pendant practice). |
| Torque/current deviation in a non-contact segment (unexpected contact) | Protective stop (the cobot's own). Then retreat backwards along the stored path to the last hub at reduced speed, and report. A held wok with food never goes back through a tip; its safe state is the nearest level, held pose. |
| Grasp outside its width/force band | Release, retreat along the approach (verified), re-sense the object's offset by camera, retry once if the offset is inside the verified tolerance (section 5), else ask the user. |
| Person in reach | Pause (speed 0, cobot holds). Heat to half during stirring (R15 policy). Resume on the same path. |
| Camera post-condition false (food left in the wok, lid not seated) | Repeat the verified set step once (e.g. a second tip) or ask the user. Never improvise a motion. |

## 5. Parameters, grids and tolerance [proposal; budgets measured]

**Tolerance budget.** A verified primitive tolerates a position error only up to its clearance reserve beyond the 10 / 5 mm gaps. The reserves measured here (full check every 5th state and at segment ends) show where the budget is tight:

| Primitive | Min reserve | Consequence |
|---|---|---|
| lid: carry down to the rack (`#6 → over the rack#7`) | **0.3 mm** (the chain's own sampled report said 1.0 mm) | Effectively no tolerance: the lid and rack must be located mechanically (keyed tab, lead-in). Store reserves from every state, not every 5th. |
| lid: into the rack | 1.0 mm | as above |
| wok grasp approach / retreat | 2.4 mm | Keyed slot in the cooker rim (R17) and keyed grip block: the wok's position is set by fixtures. |
| R15 stir strokes | 2.0 mm (plume ≥ 25.8 mm) | Wok keyed; the stroke is not re-targeted at runtime. |
| wok sink tip / untip | 3.3–3.4 mm | Sink and faucet geometry must be the measured ones (layout version). |
| wok carries, spatula lane carries | 10–83 mm | Room for blends and for small offsets. |

**Parameter types:**
- **Cart shift (along the counter):** exact. The arm motion is unchanged, so only the swept volume at the new x is screened (section 6). Verified example: plating spot 2.
- **Object offset (y, z, yaw) from perception:** verify a grid, for example 3 points per axis for ±N mm, by IK continuation from the same anchors (no anchor search). Runtime picks a verified grid point. Interpolating between grid points counts as verified only if the dilated union of their swept volumes was checked. Where the budget above is < 3 mm, use fixtures, not grids. That is the cheaper choice anyway.
- **Mass / fill:** geometry does not change. Loads are computed over the mass grid. Verified here: 1.15 kg food (chain), 0.5 kg rinse water (chain), and 1.0 kg water on the full way back from the tap (WOK_FILL: PGC 5.88 N·m < 7, joint ratio ≤ 0.55, 149 states).
- **Process timing (dwell, number of stir cycles, tip hold):** a free parameter. A dwell happens at a fixed state.
  - The WOK_FILL dwell must be V / faucet flow. The flow of the user's faucet is not measured, so the chain's 5 s is a placeholder.

## 6. What is checked when [measured method + proposal]

| When | What is checked | Cost (measured) |
|---|---|---|
| **Design time**: each primitive / set once | full path check as today; loads; parameter grid; clearance reserve per segment; swept volume stored as 2 cm voxels; scene version stamped | same planner as today (final runs 26–433 s per action). A set composed from verified primitives costs only its new joins: WOK_DUMP / FILL = 6 + 4 micro-join states + a load computation, seconds. |
| **Composition** (any sequence of sets) | hub-vector equality; scene version; pre/post-condition logic | 0 geometric checks |
| **Layout change** (a fixture moved, added or re-measured) | (1) voxel screen: which stored segments come within the gap of the changed fixture; (2) replay only those with the unchanged checker; (3) re-plan only the segments that now fail | screen 67 ms per fixture; replay 16.3 ms per state |
| **Commissioning on the real robot** | slow dry run of every set; record the nominal torque/current and camera signatures used by the monitors | real time (not simulated) |
| **Runtime** | no geometry; hub match, conditions, monitors | — |

**The screen** (`r19prim_swept.py`):
- Every robot and held-object geom is sampled every ≤ 2 cm inside its bounding box, with sub-steps of ≤ 1 cm point motion between saved states.
- Each segment's swept voxels (2 cm) are stored: 84 segments, 2.6 MB compressed.
- A segment is flagged if its voxels, dilated by 2, meet the fixture's voxels, dilated by 1. This is conservative by construction (box sampling plus the 10 mm gap).
- It is the generalized form of **R18's `r18spatreplay.py` / `r18spatscan.py`**. Those replayed *every* state of every checked action for each candidate spatula rest. The screen replays only the segments that can be affected.

**Test against the R18 replay ground truth** (spatula on the counter at the rests R18 tried; truth = r18spatreplay's method, every saved state, timed here):

| Spatula rest | R18 result | Flagged segments (states) | Truly hit segments | Missed | Replay of flagged only | Full replay |
|---|---|---|---|---|---|---|
| (−0.85, 0.30), handle 50° | rejected: hit on the wok sink trip and the faucet | 23 / 77 (706) | 13 (wok: carry to the sink lane, lane joins, under the tap, carry back; faucet lever) | 0 | 11.5 s | 27.1 s |
| (−1.15, 0.30), 50° | spatscan: blocks the wok chain at state 230 | 10 (268) | 10 (the sink: insert, extract, tip, untip, carry) | 0 | 4.4 s | 27.6 s |
| **(−1.15, 0.30), 8°, flipped (R18b choice)** | no hits | **4 (180)** | 0 | 0 | **2.9 s** | 26.7 s |
| (1.60, 0.30), 8° | (fails at pick, not in replay) | 9 (112) | 0 | 0 | 1.8 s | 27.9 s |

- Re-planning all five chains instead would cost 928 s of compute (sum of the final runs).
- **Fixture dependency** (`swept.json` fixture_dependency): the number of the 84 stored segments to re-verify if a fixture changes.

| Fixture | Segments |
|---|---|
| faucet | 13 |
| lid rack | 3 |
| zone-2 pot | 17 |
| upper cabinets | 15 |
| plating spots | 22 |
| cooker / wok zone | 30 |
| hood | 43 |
| sink | 54 |
| counters / cabinet fronts | 84 |

- Cabinet fronts flag every segment because the cart docks along them.
- **The user's real L-shaped kitchen will therefore re-verify most sets**, but only once, and the screen says which.

**Limits of the screen:**
- It is a pre-filter, not a verification.
- Ground-truth replay used the checker without full bounds at the saved states, like r18spatreplay.py. The between-state guarantee comes from the original chain check.

## 7. Smoothness [proposal; counts measured]

**Today.** Every state's time is `max(dist/0.10, angle/45°/s, joint/60°/s, cart/0.25)`, with no acceleration. Executed literally, every keyframe is a corner and every meet join a stop plus 0.6 s. That is 8 joins = 5.5 s across the 5 actions (plus the 0.5 s hand-off), and 5 of those joins move ≤ 0.5°.

**In the library:**
1. **A set is one continuous stored path.** Non-contact segments (carry, meet join, reorient, transit) are blended. Velocity goes to zero only at:
   - contact windows (approach, seat lift/lower, insert, extract, lever);
   - process dwells (tipped plate 2 s, tap 5 s, emptied 1 s, drain 5 s);
   - gripper actions.

   Stops per set [measured on the segment classes]:

| Set | Stops today | Stops with blends |
|---|---|---|
| wok plate + rinse | 27 | 16 |
| lid off → rack | 14 | 9 |
| spatula fetch | 9 | 6 |
| faucet lever | 6 | 6 |
| stir cycle | 10 | 0 (one periodic trajectory, if stored as such) |

2. **Re-timing never changes geometry.** Re-timing along a stored path, for example jerk-limited time-optimal parameterization (TOPP-RA style), keeps the swept volume, so it needs **no re-check**. Only the tracking error must stay inside the reserve.
3. **Blends that cut corners** (`movej/movel` with radius r) do change the path. Allow them only where the segment's reserve is larger than r plus the tracking error. `library_examples.json` stores `max_path_deviation_mm` = reserve − 1 mm per segment:
   - 11–25 mm on the wok carries;
   - 0 on tips and contact windows.
4. **Contact windows stay slow and straight**, exactly as checked: ≤ 50 mm along the face normal, 0.10 m/s.
5. **Exact execution: stream the dense verified states.** UR e-Series: RTDE + `servoj` at 500 Hz. This needs no corner cutting at all, and it is the most faithful way to execute what was checked.

## 8. Concrete format

**Schema.** `results/r19/prim/schema.json` (JSON Schema 2020-12) defines `Hub`, `Primitive`, `MovementSet`, `Verification`, `Condition`, `Monitor`, `Task` and `RecipeStep`. The four examples below are encoded from the data in `results/r19/prim/library_examples.json`, with every segment's play range, keyframes, start/end states and measured reserve. Shown here in YAML, abbreviated: states are referenced by play index range and hubs by name; the full vectors are in the JSON.

### 8.1 Wok plate + sink rinse (verified), and two sets composed from it

```yaml
set: WOK_PLATE_RINSE
params: {spot: {1: {plate_x: 0.43, cart_shift_m: 0.0}, 2: {plate_x: 0.17, cart_shift_m: -0.26}}, verified: [1, 2]}
start_hub: H_wok_pre          # [0.17223,-0.21,0,-3.14504,-5.564,-1.42593,2.89644,-5.39472,4.28752,.025,.025]
end_hub:   H_wok_pre          # the same vector (approach at pick#0 == retreat at set down#16)
pre:  [wok keyed in cooker slot, heat 0, food <= 1.15 kg, plate in guarded stand at spot, faucet open, hand empty]
post: [wok on cooker rinsed and empty, dish on plate, hand empty]
source: results/r17/chain_wok_s-1_final.json     # spot 2: chain_wok_s-1_r18plate2b.json
steps:   # play index ranges; reserve = min clearance beyond the 10/5 mm gaps
  - {prim: approach,   ref: "approach_qs[0] reversed", t: 0.6, reserve: 2.4, contact: true}
  - {io: grasp, t: 0.8}
  - {prim: seat_lift,  play: [0, 3],     kf: [pick#0, lifted#1],               t: 0.22, reserve: 4.0}
  - {prim: carry,      play: [3, 27],    kf: [lifted#1, lane#3],               t: 2.15, reserve: 12.0, blend_mm: 11}
  - {prim: meet_join,  play: [27, 28],   at: lane#3, arm_deg: 0.5,             t: 0.64}
  - {prim: carry,      play: [28, 48],   kf: [lane#3, over the plate#4],       t: 1.9,  reserve: 25.7, blend_mm: 24.7}   # spot 2: 46 states
  - {prim: tip,        play: [48, 93],   kf: [over the plate#4, tipped 90#5],  t: 2.36, reserve: 4.7}     # spot 2: same arm motion, cart -0.26
  - {dwell: 2.0}
  - {prim: untip,      play: [93, 138],  kf: [tipped 90#5, level#6],           t: 2.36, reserve: 4.7}
  - {prim: carry,      play: [138, 208], kf: [level#6, lane#7],                t: 6.86, reserve: 25.5, blend_mm: 24.5}  # spot 2: 44 states
  - {prim: meet_join,  play: [208, 215], at: lane#7, arm_deg: 12.3, cart_m: 0.055, t: 0.84}
  - {prim: insert,     play: [215, 232], kf: [lane#7, under the tap#8],        t: 1.66, reserve: 50.2}
  - {dwell: 5.0}                                                                # rinse under the running tap
  - {prim: extract,    play: [232, 242], kf: [under the tap#8, forward#9],     t: 0.92, reserve: 22.7}
  - {prim: tip,        play: [242, 287], kf: [forward#9, emptied#10],          t: 2.36, reserve: 3.3}
  - {dwell: 1.0}
  - {prim: untip,      play: [287, 332], kf: [emptied#10, level#11],           t: 2.36, reserve: 3.4}
  - {prim: carry,      play: [332, 349], kf: [level#11, lane#12],              t: 1.62, reserve: 22.7}
  - {prim: meet_join,  play: [349, 356], at: lane#12, arm_deg: 12.8, cart_m: 0.057, t: 0.84}
  - {prim: carry,      play: [356, 466], kf: [lane#12, lowered#15],            t: 10.85, reserve: 12.0}
  - {prim: seat_lower, play: [466, 469], kf: [lowered#15, set down#16],        t: 0.22, reserve: 4.0}
  - {io: release, t: 0.8}
  - {prim: approach,   ref: "approach_qs[1]", t: 0.6, reserve: 2.4}
time_s: 48.9
verification: {status: verified, min_reserve_mm: 3.3, max_pgc_moment_Nm: 6.47, max_joint_ratio: 0.629, elapsed_s: 275,
  fixture_dependencies: [cooker_wok_zone, counters_cabinet_fronts, faucet, hood, plating_spots, season_staple_station, sink]}
---
set: WOK_DUMP_RINSE        # after blanching / a soup in the wok: no plating
steps: "WOK_PLATE_RINSE without play [48,138] (tip, dwell, untip); micro-join play 48 -> 138"
verification: {status: composed_from_verified, micro_join: {max_joint_deg: 0.0409, cart_mm: 0.19, states: 6, hits: none, reserve_mm: 52.4}}
time_s: 42.2               # meal16 used the estimate 'dump' = 73.5 s incl. faucet + free moves; composed: 63.1 s + rest<->faucet moves
---
set: WOK_FILL              # 1 L at the running tap, nothing emptied
steps: "WOK_PLATE_RINSE without both tip loops; micro-joins 48 -> 138 and 242 -> 332 (0.0277 deg, 4 states, no hits)"
params: {water_l: 1.0, fill_dwell_s: "V / faucet flow (flow not measured; 5 s placeholder)"}
verification: {status: composed_from_verified, load_1kg_water: {states: 149, max_pgc_moment_Nm: 5.88, max_joint_ratio: 0.55}}
time_s: 36.5
```

### 8.2 Spatula fetch → stir start → R15 stir cycle

```yaml
set: SPATULA_FETCH
start_hub: H_spat_pre       # [-1.48,-0.21,0,6.12163,-2.7081,-2.30101,-0.25584,-3.44266,-0.57333,.025,.025]
end_hub:   H_spat_stroke    # [0.47238,-0.21,0,6.2271,4.9264,-2.21677,-1.16078,-4.33986,-0.06022,.015,.015]
pre:  [spatula on pad flipped (sense -1), wok on cooker, pour drum swung away, hand empty]
post: [spatula in hand sense -1, blade 1 cm off the steel at stroke 0]
source: results/r17/chain_spatula_s-1_r18roll-1.15_.30.json
steps:
  - {prim: approach,  ref: "approach_qs[0] reversed", t: 0.6, reserve: 27.0}
  - {io: grasp, t: 0.8}
  - {prim: seat_lift, play: [0, 6],     kf: [pick#0, lifted#1],          t: 0.48, reserve: 5.0}
  - {prim: carry,     play: [6, 131],   kf: [lifted#1, lane#3],          t: 12.0, reserve: 10.1, cart: -1.48 -> -0.43}
  - {prim: meet_join, play: [131, 132], at: lane#3, arm_deg: 3.4, cart_m: 0.042, t: 0.8}
  - {prim: carry,     play: [132, 232], kf: [lane#3, over the wok#4],    t: 9.93, reserve: 78.1}
  - {prim: insert,    play: [232, 248], kf: [over the wok#4, stroke start#5], t: 1.58, reserve: 5.3}
time_s: 26.9
verification: {status: verified, min_reserve_mm: 6.0, max_pgc_moment_Nm: 1.31, elapsed_s: 433}
reverse: SPATULA_STOW
---
primitive: spatula.handoff   # H_spat_stroke -> H_stir0
verification: {status: verified, evidence: "README_R10 R18b: cart 7.8 cm, joints <= 11 deg, 0.5 s, no hits, reserve 2.0 mm", state_stored: false}
---
set: STIR_CYCLE
params: {cycles: n, stroke: h_scrape_dice}
start_hub: H_stir0
end_hub:   H_stir0
pre: [spatula in hand sense -1, heat <= half while the spatula stops, nobody within reach of the wok]
steps: [stroke 0, return 1, stroke 1, return 2, stroke 2, return 3, stroke 3, return 4, stroke 4, close]
  # stroke: 183 IK states at 10 ms (0.76 x 2.4 s); return: joint move, 39 checked points, 0.50-0.77 s
time_s: 13.15            # 5 x 2.63 s
verification: {status: partially_verified, evidence: results/r15/stirwalk2_h_scrape_dice_r17.json,
  min_reserve_mm: 2.0, min_plume_mm: 25.8, peak_joint_degps: 184,
  todo: "re-run r15stirwalk2.py with joint-state output; store as one periodic trajectory"}
```

### 8.3 Lid off → rack

```yaml
set: LID_OFF_TO_RACK
start_hub: H_lid_on_pre      # [0.88629,-0.21,0,2.70331,6.19516,1.51023,-0.23281,5.38357,0.57274,.025,.025]
end_hub:   H_lid_rack_post   # [1.32563,-0.21,0,-3.74016,5.95982,2.00826,-0.43955,5.9546,-4.20824,.025,.025]
pre:  [lid on pot tab front, rack slot free, zone-2 power 0 (steam), hand empty]
post: [lid upright in rack, hand empty]
source: results/r17/chain_lid_s-1_final.json
steps:
  - {prim: approach,  ref: "approach_qs[0] reversed", t: 0.6, reserve: 10.0}
  - {io: grasp, t: 0.8}
  - {prim: seat_lift, play: [0, 2],     kf: [lift off#0, "#1"],         t: 0.12, reserve: 3.0}
  - {prim: extract,   play: [2, 25],    kf: ["#1", slide out#2],        t: 2.3,  reserve: 13.3}   # out of the hood band, level
  - {prim: carry,     play: [25, 50],   kf: [slide out#2, up#3],        t: 2.5,  reserve: 10.0}
  - {prim: reorient,  play: [50, 95],   kf: [up#3, roll 90 deg#4],      t: 2.03, reserve: 10.0}
  - {prim: carry,     play: [95, 119],  kf: [roll 90 deg#4, carry#5],   t: 1.53, reserve: 10.0}
  - {prim: meet_join, play: [119, 120], at: carry#5, arm_deg: 0.0,      t: 0.6}                   # pure overhead today
  - {prim: carry,     play: [120, 196], kf: [carry#5, over the rack#7], t: 7.58, reserve: 0.3}    # tight: no blend, fixtures
  - {prim: insert,    play: [196, 204], kf: [over the rack#7, in the rack#8], t: 0.76, reserve: 1.0}
  - {io: release, t: 0.8}
  - {prim: approach,  ref: "approach_qs[1]", t: 0.6, reserve: 7.2}
time_s: 20.2
verification: {status: verified, min_reserve_mm: 1.0 (chain) / 0.3 (every 5th state here), max_pgc_moment_Nm: 1.58, elapsed_s: 133}
reverse: LID_ON
```

### 8.4 Faucet lever

```yaml
set: FAUCET_OPEN
start_hub: H_fau_closed_pre  # [-0.67981,-0.21,0,-2.64658,-6.07183,-0.50395,-5.73507,-0.65146,-3.66099,.025,.025]
end_hub:   H_fau_open_post   # [-0.67981,-0.21,0,-2.6571,-6.08949,-0.76525,-5.84373,-0.63196,-2.87844,.025,.025]
pre:  [lever closed, hand empty, clip-on block present]
post: [lever open 30 deg, water flowing, hand empty]
source: results/r17/chain_lever_s+1_final.json
steps:
  - {prim: approach, ref: "approach_qs[0] reversed", t: 0.6, reserve: 20.0, note: "cart takes the 6 cm (x)"}
  - {io: grasp, t: 0.8}
  - {prim: lever,    play: [0, 15], kf: [closed#0, open#1], t: 0.75, reserve: 6.0}   # 30 deg about the pivot
  - {io: release, t: 0.8}
  - {prim: approach, ref: "approach_qs[1]", t: 0.6, reserve: 7.4}
time_s: 3.5
reverse: FAUCET_CLOSE
transits: {H_fau_open_post <-> H_wok_pre: "verified 6.96 s", H_fau_closed_pre <-> H_spat_pre: "NOT FOUND, needs a clearance hub"}
```

### 8.5 The plating sequence as a chain of sets (`library_examples.json` plating_sequence)

`SPATULA_STOW → T(rest→faucet)* → FAUCET_OPEN → T(faucet→wok) → WOK_PLATE_RINSE(spot) → T(wok→faucet) → FAUCET_CLOSE → T(faucet→rest)* → SPATULA_FETCH`

- All 8 junctions are identical state vectors, so no geometric check is needed between sets.
- Time: 135.8 s, against r17seq's 134.3 s.
- The two transits marked * are the unverified ones (section 3).

## 9. Library size for meals A/B/C and the checking effort

**Mapping.** Each step of `meal16.py SET=stew ARM=r18` (`results/r16/meal_stew_r18.json`) is mapped to movement sets using its own arm-time formula:
- `wok_plate` = the plating sequence;
- `dump` / `fill` = faucet + WOK_DUMP_RINSE / WOK_FILL;
- `pour` = CUP_FETCH + CUP_POUR(target) + CUP_RETURN;
- `spider` = FETCH + SCOOP(vessel) + DUMP + STOW;
- stir seconds = cycles of 13.15 s.

This mapping is a **[proposal]**, in `library_size.json`.

| Meal | Set instances executed | Distinct sets | of which verified / composed / partly / not verified | Hubs used |
|---|---|---|---|---|
| A | 71 | 28 | 12 / 0 / 1 / 15 | 21 |
| B | 167 | 30 | 12 / 2 / 1 / 15 | 20 |
| C | 103 | 26 | 12 / 2 / 1 / 11 | 15 |
| **A ∪ B ∪ C** | — | **34** (8 are reversals) | **12 / 2 / 1 / 19** | **28** (19 station, 3 held, 6 travel) |

- **Transits:** about 24 (hub-and-spoke).
- **Primitive classes:** 16.
- **Stored segments:** about 343. The verified sets contribute their measured counts, each other set the median of 12, and each transit 3.

**Still to verify, by family:**
- cup fetch / pour (wok, stew pot, plate, fryer) / return;
- wok lid off/on and its rest (A 西兰花, B 红烧肉 and 番茄炒蛋);
- stew-pot lid and stew cups;
- spider scoop from the wok and from the fryer. *The verified spider chain is the zone-2 pot, which none of these three meals uses.*
- wok hot-oil pour over a bowl. R17: a 6–8 cm bowl at the plating spot was hit by the forearm during the wok pick.
- carrier drain (fish water);
- rice dose / wash / to cooker;
- arrange;
- stir strokes for shreds and leafy food (R15: the rigid-piece bench is not credible for them);
- 2 transits (rest ↔ faucet) and the others of the hub-and-spoke set.

**Effort, today versus with the library:**

| | Today [measured] | Library [measured where stated; else proposal] |
|---|---|---|
| New action | Plan a whole chain: 26–433 s compute for the final run; 142 saved runs / 8.5 h for 5 actions (design search) | Same planner for each **new primitive**. A set made from verified primitives costs only its new joins (DUMP / FILL: 10 micro-join states + a load computation). |
| Sequence of actions | Actions checked; free moves between them **never checked** (estimates) | Junctions at identical hubs: **0 checks**. Transits verified once each (2 done, 6.96 s each). |
| Variant (plate spot 2) | Full re-plan, 279 s; 60 % of states and the whole tip came out identical | Cart-shift parameter: re-follow the 2 carries (90 states, not timed) + screen and replay the shifted tip (90 states ≈ 1.5 s) |
| Fixture moved (spatula rest) | Replay every state of every action: 1,677 states, 27 s per candidate (r18spatscan: 90 candidates) | Screen 67 ms + replay flagged: 180–706 states, 2.9–11.5 s, 0 missed in 4 queries |
| User's real kitchen (all fixtures re-measured) | Re-plan everything | Screen everything (cabinet fronts touch all 84 segments), replay all, re-plan only failing segments: one pass, done once |
| Runtime | (nothing checked between actions) | Hub match + pre/post-conditions + monitors |

**What the library does not save:**
- The design-time search for a hard new action (the spatula rest took 43 runs / 3.6 h).
- Physics and food questions (stir quality, sauce, wet friction).

**What it saves:**
- every repetition of that search for variants, layouts and sequences;
- every unchecked free move;
- the per-sequence re-checking the user asked about.

## 10. Industry practice, and what fits a UR5e or a cheaper cobot

| Practice | What it is | Fit here |
|---|---|---|
| **Taught waypoints + blends** (UR `movej`/`movel` with blend radius r; the robot does not stop at the waypoint, the path is rounded within r) | The standard cobot program: subprograms between "home / safe" waypoints | **The execution layer.** Our hubs are the safe waypoints; contact windows are `movel` without blend; free segments blend with r ≤ the stored reserve. Every cobot pendant offers this, including the cheaper ones (check the SDK of a specific model before choosing it). |
| **Dense streaming** (UR e-Series RTDE at 500 Hz + `servoj`) | The PC sends joint targets every 2 ms | The most faithful way to run a verified dense path (no corner cutting). Recommended for the UR5e. A cheaper arm needs an equivalent joint-position streaming mode. |
| **Skill libraries** (Pedersen et al. 2016: tasks → skills → motion primitives; skills with testable pre/post-conditions, concatenated by task-level programming) | Industrial mobile manipulators programmed by concatenating a small set of parametric skills | **The structure of this proposal.** Our movement sets are their skills, plus hubs so that concatenation needs no geometric check. |
| **Probabilistic roadmaps** (Kavraki et al. 1996: learning phase builds a graph of collision-free configurations and checked edges; query phase connects to it); experience-based planners that store and repair past paths (Lightning, Thunder / sparse roadmap spanners) | Pre-computed, verified graphs reused across queries | **Only for transits.** The hub graph is a tiny, hand-placed roadmap. A layout change "repairs" edges, as the screen does. A large random roadmap is not needed: the kitchen is static and the station list is short. |
| **Dynamic movement primitives** (Ijspeert et al. 2013: learned attractor systems; point and limit-cycle attractors; generalize to new goals) | Learned motion shapes that adapt online | **Offline only.** A rhythmic DMP could generate stir-stroke families. An online DMP produces unchecked paths in a cluttered kitchen (reserves of 0.3–5 mm), so every generated variant must be verified like any other primitive. Not a runtime generator here. |
| **Time-optimal path parameterization** (TOPP-RA, Pham & Pham 2018) | Fastest timing along a fixed path under velocity / acceleration limits | Smooth, fast timing for every stored path without changing its geometry, so no re-check. |
| **Recorded-motion kitchens** (Moley: a chef's motion-captured movements, cleaned and spliced into a recipe library) | A motion library | The same "library" idea, but it replays human motion on dexterous hands. Ours is engineered, collision-verified arm paths for one gripper and keyed tools: cheaper hardware and checkable. |

**Recommendation for this robot** (UR5e on the cart, or a cheaper 6-axis cobot):
1. **Keep offline verification as is.** Use the unchanged checker and r17chain-style chains to make primitives. Store every verified path with its states, reserve per segment, loads, swept voxels and scene version.
2. **Hub-and-spoke library:**
   - station hubs with a clearance retreat;
   - about 6 travel hubs along the rail;
   - transits verified once;
   - sets join only at identical hub vectors.
3. **Use the rail.** Make primitives cart-shift parameters where the arm motion is the same: plating spots, cup slots along a shelf, carriers.
4. **Execution:** stream dense, TOPP-timed joint trajectories (UR: RTDE + `servoj`). Fall back to blended waypoints with r ≤ the reserve. Contact windows stay slow and straight.
5. **Runtime:** hub match, pre/post-conditions and monitors: joint current/torque deviation, gripper band, cameras, presence. Recovery only along stored paths.
6. **Layout changes:** screen, then replay the flagged segments, then re-plan only the failures.

**Cost.** Nothing in this architecture needs runtime planning, a GPU or a premium arm feature. It needs four things:
- repeatable joint-position execution;
- blended-waypoint or streaming motion;
- current-based contact detection;
- a gripper with position and force feedback.

A cheaper cobot qualifies if it has those, but the whole library must then be re-verified with its kinematics and geometry. The pipeline carries over; the library does not. Arm pricing is outside this report.

## 11. Honesty notes and open items
- **Measured here:**
  - the inventory and its time reconstruction;
  - identical-state reuse and cart-shift identity;
  - the micro-joins and the 1 kg water loads (unchanged checker; r17chain.load() method, water CoM 2 cm above the wok bottom as r17chain's food);
  - per-segment reserves (every 5th state + segment ends);
  - the swept-voxel screen against the R18 replay method;
  - the four transits.
- **Proposal, not checked:**
  - the meal-to-set mapping and the 34-set catalogue (its statuses come from the data);
  - travel hubs and transit count;
  - blend policy and stop counts with blends;
  - monitors and recovery;
  - parameter grids.
- **The stir cycle's joint states were never saved** (r15stirwalk2.py writes summaries only), so it is "partially verified" as a library entry. It needs a re-run that stores states, as one periodic trajectory.
- **The chains' min reserve is sampled every 5th state.** For the lid, sampling here found 0.3 mm where the chain reported 1.0 mm. Store reserves from all states.
- **The faucet flow for WOK_FILL is not measured.**
- **Two transits are not found.** The spatula rest and faucet hubs need clearance retreats.
- **The real kitchen will re-flag almost everything** (cabinet fronts). The library makes that a single, targeted pass, not a repeated one.
- **Sources consulted (read-only):**
  - [UR `movej` script manual (blend radius r)](https://www.universal-robots.com/manuals/EN/HTML/SW5_24/Content/prod-scriptmanual/all_scripts/movej_qa14v105t0r.htm)
  - [UR realtime / RTDE guide](https://docs.universal-robots.com/tutorials/communication-protocol-tutorials/realtime-guide.html)
  - [MathWorks UR RTDE `servoj` at 500 Hz](https://www.mathworks.com/help/robotics/urseries/ref/urrtdeclient.html)
  - [Pedersen et al. 2016, Robot skills for manufacturing](https://vbn.aau.dk/en/publications/robot-skills-for-manufacturing-from-concept-to-industrial-deploym)
  - [Kavraki et al. 1996, PRM](https://kavrakilab.org/publications/kavraki-svestka1996probabilistic-roadmaps-for.html)
  - [Coleman et al., Thunder / experience-based planning](https://arxiv.org/html/1410.1950)
  - [Lightning (OMPL)](https://ompl.kavrakilab.org/Lightning_8h_source.html)
  - [Ijspeert et al. 2013, DMPs](https://is.mpg.de/publications/ijspeert_nc_2013)
  - [Pham & Pham 2018, TOPP-RA](https://arxiv.org/pdf/1707.07239)
  - [Moley robotic kitchen (NPR)](https://www.npr.org/transcripts/400367891)
