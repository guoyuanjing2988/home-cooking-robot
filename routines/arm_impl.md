# Arm implementation of the cooking routines (2026-10-13 15:43 SGT)

Every routine type in `routines.json` expanded into atomic steps with actor, movement set, how, and an honest status. Full data: `arm_impl.json`. Inputs were read only.

**Status scale:** checked_path (continuous path checked in the R17/R18 kitchen) > checked_old_layout (R11/R12 layout) > checked_pose (single poses) > bench_only (physics bench, no arm) > planned (concrete design, nothing checked) > no_design.

## Counts

- 57 routine types, 505 dish calls, 437 atomic steps (311 by the arm).
- All steps by status: checked_path 198, checked_old_layout 9, checked_pose 4, bench_only 9, planned 157, no_design 60.
- Arm steps by status: checked_path 198, checked_old_layout 9, checked_pose 4, bench_only 3, planned 42, no_design 55.
- 90 distinct movement sets used (54 new, not in R19_MOTION_LIBRARY); arm sets by status: checked_path 26, checked_old_layout 5, checked_pose 4, bench_only 2, planned 9, no_design 34.
- Routines whose every arm step is checked_path: **7** (stir_fry, drum_add_stir, thicken, simmer_open, reduce_sauce, wok_fill_water, wash_wok), covering 112 of 505 calls. Their servo / drum / station steps are still not checked (knob servo planned, drum release bench_only, drum swing-away no_design).
- Dish calls whose applicable arm steps are all checked_path (variants resolved from the call params, e.g. take_out into=plate): **147 of 505** (drum_add_stir 54, take_out 44, thicken 14, simmer_open 11, wok_fill_water 8, reduce_sauce 7, wash_wok 5, stir_fry 4).
- Routines with no arm step: heat_to, fry_still, rice_cooker, grind_spice.

## Top 10 unchecked or undesigned arm movement sets by uses (the priorities)

"Unlocks" = dish calls whose arm steps would all be checked_path if only this set were checked.

| # | Movement set | Status | Uses | Unlocks | Used by (routines) | What is missing |
|---|---|---|---|---|---|---|
| 1 | `TRANSIT_CUP_PORT` (new) | planned | 214 | 103 | 19: add_off_heat, add_stir_fry, blanch_lift, bloom_aromatics, caramelize_sugar, cold_mix_bowl … | The spur is not run: the cup port is not yet a hub node, so the free moves to and from it are unchecked. |
| 2 | `WOK_OIL_POUR` | planned | 25 | 2 | 4: dry_stir, pour_off_excess_oil, take_out, wok_grease | Pieces are checked, but the no-sink return was never joined or run; the oil cup is narrower than a plate; who empties the hot oil cup? |
| 3 | `HOLDING_BOWL_POUR` (new) | no_design | 23 | 20 | 2: pour_off_excess_oil, return_and_toss | Missing: holding-bowl grasp feature (not a robot cup), bowl size, path. |
| 4 | `GENTLE_SEPARATE_STROKE` (new) | no_design | 23 | 0 | 2: deep_fry, slide_oil_meat | Missing: stroke design and bench. |
| 5 | `STIR_CYCLE_shreds_leafy` | bench_only | 19 | 0 | 2: add_stir_fry, slide_oil_meat | No stroke has been shown to work for shreds/leafy food; needs a real-food test before any arm path. |
| 6 | `CUP_POUR_pot` (new) | no_design | 19 | 0 | 1: blanch_lift | Missing: a pour pose under the hood (0.40 m above the cooktop; R16: gripper + wrist do not fit from above). |
| 7 | `WOK_TIP_HOLDING_BOWL` (new) | planned | 17 | 10 | 3: egg_set_and_hold, slide_oil_meat, take_out | A bowl ≥ 6 cm tall was hit at spot 1; spot 2 with a bowl is unchecked. |
| 8 | `SPIDER_SCOOP_wok` | planned | 14 | 4 | 5: blanch_lift, deep_fry, fish_out_item, poach_slices, pour_off_excess_oil | Scoop path in the wok under the hood (hood 23 cm above the rim at the right) not planned; lane hub may not serve the wok. |
| 9 | `SPIDER_SCOOP_fryer` | no_design | 14 | 0 | 1: deep_fry | Missing: the fryer's place and its hub; nothing described beyond "a fryer". |
| 10 | `CUP_POUR_fryer` | no_design | 14 | 0 | 1: deep_fry | Missing: fryer place; splash rule for hot oil. |

## Checked movement sets (checked_path), with uses

`SPATULA_STOW` (311), `CUP_RETURN` (215), `SPATULA_FETCH` (214), `TRANSIT_TO_SPAT` (214), `CUP_FETCH` (214), `STIR_CYCLE_dice` (184), `CUP_POUR_wok` (162), `FAUCET_OPEN` (71), `FAUCET_CLOSE` (71), `TRANSIT_SPAT_LEV_C` (68), `TRANSIT_LEV_C_SPAT` (68), `TRANSIT_LEV_O_WOK` (68), `TRANSIT_WOK_LEV_O` (68), `TRANSIT_TO_SPIDER` (47), `SPIDER_FETCH` (47), `SPIDER_DUMP_plate` (47), `SPIDER_STOW` (47), `WOK_PLATE_RINSE` (44), `LID_OFF_pot` (31), `TRANSIT_TO_LID` (28), `WOK_FILL` (19), `SPIDER_SCOOP_pot` (19), `LID_ON_pot` (11), `CARRIER_IN` (8), `CARRIER_OUT` (8), `WOK_DUMP_RINSE` (5). Evidence per set is in `arm_impl.json` movement_sets.

**Non-arm steps that gate many calls** (not in the top 10, which is arm sets only): `SERVO_HEAT_KNOB` planned (331 uses); `DRUM_RELEASE` bench_only (91 uses); `DRUM_HOLDER_SWING` no_design (76 uses). The drum holder swing-away is the one with no design at all; it sits in every drum_add_stir / thicken call.

**Prep is under-weighted here:** the dish calls carry prep only as mise_en_place / prep_* routines (prep_cut 7 calls, prep_wash 0). R19_PREP_AUDIT §6.2 counts per three meals: 34 piece cycles, 45 lever presses, 36 placements (ARRANGE), 18 basket sets, 15 finger swaps, 14 output transfers - use those counts, not the uses column, to rank prep work.

## What changed during this run

- The Mac seasoning-cup chain passed at 15:36–15:40 (`robot_rail/sim/r10/claude/results/mac/chain_cup_final.json`, report `renders/mac/cup_pour_report.md`: 20.6 s, min reserve 2.2 mm, 224 states re-checked, 0 hits). CUP_FETCH / CUP_POUR_wok / CUP_RETURN are therefore checked_path (they were checked_pose from R14 in the first version). It moved the port pad to (0.45, 0.30, 1.085), 0.10 m left of the kitchen14 port box: the station hardware must follow, and the new pad was not screened against the other checked paths.

## Contradictions and stale statements found in the docs

1. **Hub edges: checked or only screened?** `R19_HUB.md` "Status at hand-off" says 4 + 3 edges are checked and 18 only screened ("Not a check"), but `README_R10.md` R19 says "All 22 edges pass the full checker". The 22 `results/r19/hub/edge_*.json` files all have ok=true, so the README is current and the R19_HUB header is stale.
2. **Spatula rest ↔ faucet transit.** `R19_MOTION_LIBRARY.md` §3, §8.4 and §11: "not found ... needs a clearance hub". `R19_HUB.md` / `edge_SPAT__LEV_C.json`: passes via the middle-cart tuck, 6.49 s, 2.3 mm. The library text is superseded.
3. **Wok chain reserve.** R17 table, MOTION_LIBRARY §8.1 and the R18 second-spot text say 3.3 mm; the R19 ≤ 4 mm re-check (`results/r19/smooth/summary.json`) gives 2.02 mm. cook_api.py already quotes 2.0 mm.
4. **Lid reserve.** Chain 1.0 mm vs 0.3 mm in the R19 library sampling; README R19 calls it unresolved. Either way the lid rack needs mechanical location.
5. **Stir cycle status.** README R18b and cook_api.py: the R15 cycle "passes as in R15" in the current kitchen. R19 library: "partially_verified" (states never stored), and README R19: 2.63 s/stroke "not executable as checked" (~3.6 s with stops). Here: checked_path for the geometry, with that caveat as the open question.
6. **Drum vs spatula.** SPATULA_FETCH was checked with the pour drum swung away (MOTION_LIBRARY §4 pre-condition; R17 "swung away from the rim except while stirring (not modeled)"), but drum_add_stir (54 calls) and thicken (14) need the drum at the rim while the spatula stirs. R15 Design 4: the behind-the-wok holder spot "is not yet checked against the stir strokes". The swing mechanism has no design.
7. **Carriers.** MOTION_LIBRARY §9 / library_size.json list CARRIER_IN/OUT as verified; R19_HUB §1 lists "carriers in and out (checked in R16 but no play stored)" under unchecked actions. Both are true: the path was checked (R17 re-check 17.7 s, 2.3 mm) but cannot be replayed or joined to a hub.
8. **Ladle "not designed".** routines.json (ladle_baste, serve_soup, hardware "ladle (not designed)") vs README R16: a ladle chain (pot → soup bowl, 64 s, 3.0 mm, `results/r16/chain_ladle.json`) passed in the R16 layout. R17 then removed the ladle from the rest and the user decided soups are served by the user. Accurate wording: "checked for the pot in R16, dropped in R17; no wok ladle".
9. **Rice.** routines.json rice_cooker is "needs_check" with RICE_DOSE / RICE_WASH / RICE_TO_COOKER, and library_size.json still counts those sets; DECISIONS 2026-10-13: the user loads and starts the rice cooker and the arm's rice sets are dropped.
10. **Seasoning containers.** DECISIONS 2026-10-13 first chose direct dosing at the wok and dropped "most robot cups" (r19_seasoning_sizing.md still recommends option (d)); later the same day the user's decision brought cups back ("containers that the arm picks up"). The routines follow the later rule, but the station re-size and the cup staging place are open.
11. **Eggs and prep.** DECISIONS 2026-10-13: prep is the robot's job ("肯定不是人来做"); the demo and prep_egg_beat keep "the user cracks and beats the eggs". R19_PREP_AUDIT lists eggs as [missing].
12. **Pot water.** blanch_lift says "(water already in the pot / wok_fill_water)", but WOK_FILL fills the wok; there is no pot-fill set (R17: pot water is put in by the user at setup).
13. **Fridge arc "checked".** R19_PREP_AUDIT §3 calls the 0–35° door arc [checked]; `fridge_arc_path.json` is a chain of checked poses every 2.5° (≤ 10.3° joint per step, reserve 0.0–5.0 mm over 0–55°) in the R14 scene, without checking between samples or the R18b spatula pad. Here: checked_pose.
14. **Counter conflicts.** The fridge cold-box set-down (-1.70, 0.18) overlaps the proposed far-left tool spot (-1.62, front) (R19_PREP_AUDIT §4.3); the R11 slicer spot overlaps both plating spots by 77 mm; the carrot peel spot overlaps the R18b spatula rest.
15. **Cup size.** R14 specifies Ø70×75 mm stainless robot cups; the sim cup in the passed chain is 60×70 mm (kitchen14 cup).

