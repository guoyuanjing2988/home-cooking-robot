# R19 hub roadmap: pre-verified free moves between the checked actions (2026-10-13)

**Question.** `r17seq.py` and `meal16.py` join the checked whole actions with estimated, unchecked free moves of the empty arm: `|dx|/0.25 m/s + 1 s + 1.6 s`. Can a small set of fixed "hub" postures replace them with checked paths? Every action would then start and end at a hub, so any sequence of actions is checked by construction, with nothing re-checked per move.

**Files**
- `r19hub.py`: one short command per step or edge.
- `r19hub_render.py`: renders the contact sheet.
- `results/r19/hub/`:
  - `endpoints.json`, `tuck_neg.json`, `tuck_pos.json`, `hubs.json`;
  - `edge_*.json` (checked edges) and `screen_edge_*.json` (fast-checker screens, **not checks**);
  - `graph.json`, `meal_transitions.json`, `hubs_sheet.png`.

## Status at hand-off (be precise about what is checked)
| | Edges | Meaning |
|---|---|---|
| **Checked** (full checker on every state) | 4 + 3 derived | 3 corridor pieces (hub to hub) and the WOK spur. The 3 derived corridor edges join collinear checked pieces, so no new states. |
| **Screened only** (fast checker, MuJoCo contacts) | 18 | All 18 pass the screen. **Not a check.** The full runs are in the controller command list below. |
| Failed | 0 checked edges failed | Straight-line attempts that failed are listed under "What fails" (fast-checker results). |

## 1. Which free moves occur in meals A/B/C (`python r19hub.py meals`)
The meals are taken from `results/r16/meal_stew_r18.json` (meal16 `SET=stew ARM=r18`), in schedule order. Each step is split into arm actions (`STEPS` in `r19hub.py`):
- **Checked actions:**
  - a stir dish: `SPAT_FETCH`, `STIR`, `SPAT_STOW`, `LEV_OPEN`, `WOK`, `LEV_CLOSE` (r17seq order);
  - dump / fill: `LEV_OPEN`, `WOK`, `LEV_CLOSE`;
  - `LID_OFF` / `LID_ON`;
  - `SPIDER*` (its endpoints are checked; at the fryer or wok its interior is not).
- **Unchecked actions (`U:`):** pours and cups, carriers in and out (checked in R16 but no `play` stored), rice, wok lid, hot-oil pour, the stew-pot lid, arranging.

| Meal | Actions (checked) | Free moves checked↔checked | checked↔unchecked | unchecked↔unchecked | Spatula hand-offs (no free move) |
|---|---|---|---|---|---|
| A | 39 (17) | 7 | 12 | 15 | 4 |
| B | 68 (29) | 15 | 15 | 31 | 6 |
| C | 49 (27) | 16 | 10 | 16 | 6 |
| **Total** | 156 (73) | **38** | **37** | **62** | 16 |

**What is in the hand.**
- In **every** free move: **nothing**. The gripper is empty with its jaws open 25 mm.
- The spatula is held only inside fetch → stir → stow. The R18 hand-offs into and out of the stir cycle are already checked and are not free moves.
- Not covered: if the arm had to set the spatula down for a main-ingredient addition in the middle of a stir, a "spatula-held" hub would be needed. The plan has no such move: additions come from the R15 drum.

**The 38 checked↔checked moves:**
- **Plating, dump and fill trips (31):**
  - LEV_O→WOK ×12 and WOK→LEV_O ×12;
  - SPAT→LEV_C ×7 (spatula rest to faucet).
- **Other pairs:**
  - LEV_C→LID_POT ×2;
  - SPIDER→LEV_C ×1.
- **No motion (4):**
  - LID_POT→LID_POT ×1 (lid on, then lid off after steaming; the arm waits at a hub);
  - SPIDER→SPIDER ×1;
  - LEV_C→LEV_C ×2: the faucet is closed, then re-opened at once. Two meals do this (a plating trip followed directly by a fill trip). **Skipping that close/open saves about 7 s and two free moves.**

**Gap in the meal model.** meal16 counts free moves only inside the plating, dump and fill trip: r17seq's four moves. The moves to and from the lid, spider, carriers, cups and rice (the 37 + 62 others) are either hidden in the assumed step times or not counted at all.

## 2. The endpoints, and two things found on the way
**Free-move endpoint = the end of each action's grasp approach or release retreat** (`approach_qs[k][-1]`: jaws open, gripper 6 cm back), not `play[0]` / `play[-1]`. In those, the arm still holds the object 8 mm lifted; the approach between them belongs to the action and was checked by r17chain.

There are 7 nodes:

| Node | Action file | Cart x |
|---|---|---|
| WOK (start = end; also the second plating spot chain) | `chain_wok_s-1_final.json` | 0.172 |
| LEV_C (lever closed) | `chain_lever_s+1_final.json` | −0.68 |
| LEV_O (lever open) | same file | −0.68 |
| LID_POT | `chain_lid_s-1_final.json` | 0.886 |
| LID_RACK | same file | 1.326 |
| SPIDER (start = end) | `chain_spider_s+1_final.json` | 1.093 |
| SPAT (rest) | `chain_spatula_s-1_r18roll-1.15_.30.json` | −1.48 |

**(a) The stored `play` arrays jump by exactly 2π.**
- Where:
  - wok: 6 joint jumps (rows 215 and 356);
  - lid: 2 (row 120);
  - spider: 8 (rows 51, 178, 412);
  - spatula: 1 (row 132);
  - lever: none.
- Cause: r17chain's join takes the nearest equivalent angle for the arrival, but the next piece keeps its own labels.
- Effect: same pose, same check. But a controller fed the raw arrays would spin a joint 360° there. `r17video.py` also shows a 6 s pause at each jump.
- **Unwrapped, every play stays inside the joint ranges**, so the actions are executable. r19hub uses the unwrapped labels (`unwrapped()`).
- Net change at the end:
  - the lid's rack end is +2π in pan and wrist 3;
  - the spatula's stroke-start end is **−2π in shoulder lift**. The R15 stir cycle must take the same relabel. Its states are not stored, so its range after the relabel is not re-verified here.

**(b) Relabelling whole actions.**
- Joint j shifted by 2πk is the same pose. Each action is relabelled as a whole, only where all its states stay in range (`allowed_shifts`), to sit next to the hub (`hubs.json action_shifts`):
  - wok: pan +1, lift +1, w1 −1, w2 +1, w3 −1;
  - lever: pan, lift, w1 +1;
  - lid: lift, w2 −1;
  - spider: pan +1;
  - spatula: pan −1, w2 +1. The stir cycle needs the same relabel; this is flagged, not verified.
- Without this, the lid's shoulder lift sits near +2π and the wok's near −2π: a 360° shoulder swing between them.

**The scene of every free move is one "union" scene**, `union_tree()`:
- the R18 kitchen (r17chain BASE);
- the spatula on its R18b rest; the spider on its rest;
- the faucet lever **closed and open**; the lid **on the pot and in the rack**;
- a dish on **both** plating spots (x 0.43 and 0.17).

Clearance is pairwise, so a state that passes this scene passes every world state of a meal. That makes the edges context-free.
- All 7 endpoints pass the union scene (reserve 7.2–52 mm).
- The extra copies are live obstacles: lever states hit the open-lever copy, and the rack approach binds on the rack-lid copy at its recorded clearance.

## 3. Hubs: one tucked posture at 4 cart stations
**Branches.** The endpoints fall into three IK branches:
- **B1**, pan ≈ π, elbow down: WOK, LEV_C, LEV_O;
- **B2**, elbow up: LID_POT, LID_RACK, SPIDER;
- **B3**, shoulder flipped: SPAT.

Uses in the meals: B1 71, SPAT 16, B2 26 (`endpoint_uses`).

**Search.** `r19hub.py tuck` is a differential-evolution search for **one** joint posture T, kept ≥ 11° from every joint limit. Its objective:
- the sum over the 7 endpoints of the largest joint move to T (the straight-spur time);
- a collision penalty at T over 8 cart stations, and on 6 samples of every straight spur;
- the R10 dock carry envelope (±0.40 m along x, ≤ 0.10 m over the counter edge);
- a mild height penalty.

| Tuck family | Largest joint move per spur (WOK, LEV, LID_POT, LID_RACK, SPIDER, SPAT) | Sum | Cost |
|---|---|---|---|
| **elbow negative (chosen)** | 145, 173, 236, 264, 250, 180° | 1421° | 272.7 |
| elbow positive | 211, 160–173, 106, 97, 112, 261° | 1121° | 293.9 (more spur collisions) |

**Chosen tuck.** T = [34.8, 24.8, −149.1, −142.1, 4.0, −74.9]° (pan, lift, elbow, w1, w2, w3).
- **Why this one:**
  - it serves the 87 of 113 endpoint uses that are in the WOK, faucet and spatula branches;
  - all 7 straight spurs from it screened clear except LEV_O;
  - it satisfies the R10 carry envelope, so the cart never drives with the arm out;
  - it is low: 1.62 m;
  - it keeps 60 mm reserve at every station.
- **Cost:** the pot cluster (lid, spider) is in the other elbow branch, so each of its spurs is a 236–264° elbow flip (4.5–5.2 s, robot points up to 2.0 m; **the ceiling is not modelled**).

**Stations (`STATIONS`; the 4 hubs are also where the arm waits):**
- H_SPAT x −1.48: spatula rest, and the idle park at the counter end;
- H_SINK −0.68: faucet;
- H_WOK 0.172: wok;
- H_POT 1.093: spider, and the lid ends at 0.886 / 1.326.

The contact sheet `results/r19/hub/hubs_sheet.png` shows the tuck and the 7 endpoints.

## 4. Edges, check method and time
**Check.**
- Straight segments in (cart, joints) space. States are spaced so that `point_bound.segment_bound` (a valid displacement bound for every robot point, taken per short piece) is ≤ 4 mm between neighbours.
- Every state is screened by the fast checker, then **every** state gets the full checker: exact bounds, 10 / 5 mm gaps, self, ranges, cart floor and tip.

**If the straight move fails, these via poses are tried in order:**
1. the tuck at the middle cart or either end cart (a "floating hub", express edges only);
2. Cartesian retreats of the TCP 15–30 cm toward the aisle, same orientation, solved by IK from the endpoint;
3. joint-ordered vias;
4. with the cart fixed: `planner.plan` (RRT-Connect, restarts, staging, shortcuts, full ≤ 4 mm replay, 120 s budget).

**Time.** r17chain caps: joints ≤ 60°/s, cart ≤ 0.25 m/s, plus 0.6 s per edge. The arm stops at hubs.

| Edge | Status | Method | Time | Estimate (formula) | Min reserve | States |
|---|---|---|---|---|---|---|
| H_SPAT–H_SINK (corridor, cart only) | **checked** | straight | 3.8 s | 5.8 s | 60 mm | 209 |
| H_SINK–H_WOK | **checked** | straight | 4.0 s | 6.0 s | 60 mm | 215 |
| H_WOK–H_POT | **checked** | straight | 4.3 s | 6.3 s | 60 mm | 248 |
| H_SPAT–H_WOK / H_SINK–H_POT / H_SPAT–H_POT | **checked** (derived: collinear pieces, no stop) | — | 7.2 / 7.7 / 10.9 s | 9.2 / 9.7 / 12.9 s | 60 mm | — |
| WOK–H_WOK (spur) | **checked** | straight | 3.0 s | 2.6 s | 2.1 mm | 859 |

**Phase 1 (screened):**

| Edge | Status | Method | Time (projected) | Estimate | Note |
|---|---|---|---|---|---|
| SPAT–H_SPAT, LEV_C–H_SINK | screened | straight | 3.6, 3.5 s | 2.6 s | |
| LEV_O–H_SINK | screened | via retreat 15 cm | 4.0 s | 2.6 s | |
| SPIDER–H_POT, LID_POT–H_POT, LID_RACK–H_POT | screened | straight (elbow flip) | 4.8, 4.5, 5.0 s | 2.6–3.5 s | robot up to 2.0 m |
| **Express SPAT–LEV_C** | screened | via the tuck at the middle cart | **6.5 s** | 5.8 s | TCP up to 0.91 m/s |
| **Express LEV_O–WOK** | screened | via retreat 15 cm + the tuck at the middle cart | **6.4 s** | 6.0 s | |

**Phase 2: neighbour spurs.** The cart drives to the next hub while the arm folds.

| Edge | Status | Time (projected) | Estimate |
|---|---|---|---|
| SPAT–H_SINK, LEV_C–H_SPAT, LEV_C–H_WOK | screened | 3.8, 3.8, 4.0 s | 5.8–6.0 s |
| LEV_O–H_SPAT, LEV_O–H_WOK | screened | 4.2, 4.4 s | 5.8, 6.0 s |
| WOK–H_SINK, WOK–H_POT | screened | 4.0, 4.3 s | 6.0, 6.3 s |
| SPIDER–H_WOK, LID_POT–H_WOK, LID_RACK–H_WOK | screened | 4.8, 4.5, 5.2 s | 6.3, 5.5, 7.2 s |

**`graph.json`:**
- `nodes`: 4 hubs and 7 endpoints;
- `edges`: both directions, with held object, ok, method, time, estimate, reserve, peak TCP speed, height and file;
- `routes`: Dijkstra over **checked** edges, plus `projected_with_screened` (checked + screened, labelled as a projection);
- `screened_not_checked`.

## 5. Answers
**Do the estimated free-move times hold?** In total, yes, within about 10 % (projected; full checks pending).

The plating, dump and fill trip is the move that matters (31 of the 38 checked↔checked moves):

| Move | Estimate | Projected (express edge) |
|---|---|---|
| SPAT→LEV_C | 5.8 s | 6.5 s |
| LEV_O→WOK | 6.0 s | 6.4 s |
| WOK→LEV_O | 6.0 s | 6.4 s |
| LEV_C→SPAT | 5.8 s | 6.5 s |

- That is +2.2 s per trip (23.6 → 25.8 s), i.e. +12.6 s over the 34 moving checked↔checked transitions of the three meals.
- Every plating, dump or fill trip includes these four moves (2 trips in A, 5 in B, 5 in C). So arm time rises by about 4 s (A) and 11 s (B, C), and the meal totals by at most about 0.2 min (A 39.5 / B 75.6 / C 38.6).

The formula is wrong in detail:
- **For the arm.** It assumes 90° at 90°/s. The checked moves swing 145–264° at r17chain's 60°/s. SPAT↔faucet is a shoulder-branch change; the pot cluster needs an elbow flip.
- **For long moves.** The cart dominates, and folding while the cart drives hides the arm time. Through hubs:

| Long move | Projected | Estimate |
|---|---|---|
| SPAT→WOK | 7.8 s | 9.2 s |
| LEV_C→LID_RACK | 9.2 s | 10.6 s |
| SPIDER→LEV_C | 8.8 s | 9.7 s |

- **Inside the pot cluster.** LID_POT↔SPIDER, LID↔LID: 9.3–9.8 s against 3.4–4.4 s estimated, because of the elbow flip into the tuck and back. None of these occurs between checked actions in meals A/B/C. If needed, add direct pot-cluster edges, or a second tuck in the elbow-up branch.
- **Peak TCP speed in free moves** reaches 0.5–0.9 m/s at 60°/s joints: the r17chain caps do not limit TCP speed in joins. A home-tier TCP cap (for example 0.25–0.5 m/s near a person) would lengthen the spurs. That is a decision for the safety package.

**Which transitions fail, and why?** These are fast-checker results on straight paths; each one is solved by a via:
- **LEV_O → anything.** Straight, wrist 1 rises into upper cabinet 1 within the first 2 %: the lever endpoint sits under the cabinet front. Fix: first pull the TCP 15 cm toward the aisle.
- **LEV_O → WOK, straight with the cart moving.** A finger meets the backsplash power outlet (x 0.15) at 20 %: the hand still reaches back while the cart drives.
- **SPAT → LEV_C straight.** The forearm meets the closed upper-cabinet door `r07_closed_door_0_1` at 17 % of the shoulder flip. Fix: the tuck at the middle cart.
- **Every joint-ordered via** for LEV_O → WOK fails: the gripper housing meets the counter, or the wrist meets the cabinet.

No edge has yet failed the full checker. A full-check failure would be reported in the edge file's `tries`, and the command then moves on to the next via or the planner.

**How many hubs and edges cover meals A/B/C?**
- **4 hubs, 7 endpoints.**
- **Phase 1: 12 edges** (7 spurs, 3 corridor pieces, 2 express). They cover all 34 moving checked↔checked transitions, and the checked side of all 37 checked↔unchecked transitions.
- **Phase 2:** 10 neighbour spurs, so routes reach about the estimate.
- The 62 unchecked↔unchecked transitions need movement sets for the unchecked actions first: cups and pours, carriers, rice, wok lid, hot-oil pour.

**How does this fit a "movement set" library?**
- **A movement set = hub → spur in → the action's unwrapped, relabelled play → spur out → hub.** It is checked once, in the union scene.
- Because every edge is valid in every world state that the union covers, **any sequence of sets joined by corridor edges is checked by construction**. At run time the controller replays stored joint trajectories: no online planner and no collision checking per move. That is cheaper to compute and repeats exactly.
- **Adding an action costs only its 1–3 spurs**, about 2–6 min of checking each. Existing sets are never re-checked.
- **Rules that keep it valid:**
  1. Every object place used in any set (lever angles, lid places, dishes, the spatula rest) must be in the union scene. A new place (a carrier staging spot, a soup bowl) means adding it and re-running the edges once.
  2. The cart drives only in the tuck, which is inside the R10 carry envelope, or on edges checked with the cart moving (express and neighbour spurs).
  3. Actions are fed to the controller unwrapped.
- **Suggested next sets:**
  - re-run the R16 carrier chain with its `play` stored, so it becomes a node;
  - cup pick and pour;
  - a pot-cluster tuck or direct edges;
  - skip the redundant faucet close/open between back-to-back trips.

## 6. Controller command list (the full set; each command is one edge, 2–7 min; run the 4 lanes in parallel, in the background)
Each command first tries the straight edge, then the vias, then (cart fixed only) the planner, and writes `results/r19/hub/edge_<A>__<B>.json`. Phase-1 edges come first in every lane.

```bash
cd /c/Users/admin/Documents/YJGames/robot_rail/sim/r10/claude
PY=C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe
# lane 1
for e in "SPAT LEV_C" "SPAT H_SPAT" "LID_RACK H_WOK" "WOK H_SINK" "SPAT H_SINK"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 > results/r19/hub/log_$1__$2.txt 2>&1; done
# lane 2
for e in "LEV_O WOK" "LEV_O H_SINK" "SPIDER H_WOK" "WOK H_POT" "LEV_O H_SPAT"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 > results/r19/hub/log_$1__$2.txt 2>&1; done
# lane 3
for e in "LID_RACK H_POT" "LEV_C H_SINK" "LID_POT H_WOK" "LEV_C H_SPAT"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 > results/r19/hub/log_$1__$2.txt 2>&1; done
# lane 4
for e in "SPIDER H_POT" "LID_POT H_POT" "LEV_C H_WOK" "LEV_O H_WOK"; do set -- $e; $PY r19hub.py edge A=$1 B=$2 PLAN_S=120 > results/r19/hub/log_$1__$2.txt 2>&1; done
# after all four lanes
$PY r19hub.py graph
$PY r19hub.py commands      # lists anything not ok, incl. the lid fallbacks:
#   only if edge_LID_POT__H_POT.json is not ok:  $PY r19hub.py edge A=LID_POT B=F_LID_POT PLAN_S=120 ; $PY r19hub.py edge A=F_LID_POT B=H_POT
#   only if edge_LID_RACK__H_POT.json is not ok: $PY r19hub.py edge A=LID_RACK B=F_LID_RACK PLAN_S=120 ; $PY r19hub.py edge A=F_LID_RACK B=H_POT
```

**Expected.**
- The lanes hold 7.4–9.1 k states each. At about 0.1–0.2 s per full check, expect about 15–35 min per lane.
- All 18 edges passed the fast screen with the same via the full run tries first. I expect most or all to pass the full checker, as the WOK spur and the corridor did.
- The tightest places, most likely to fail or fall through to a later via or the planner:
  - LEV_O's retreat (wrist near the upper cabinet);
  - SPAT–LEV_C (forearm near the cabinet door);
  - the lid-rack end (7.2 mm reserve at the endpoint).
- Then `graph.json` `routes.*.checked` replaces the projections. The expected times are those in section 5.
