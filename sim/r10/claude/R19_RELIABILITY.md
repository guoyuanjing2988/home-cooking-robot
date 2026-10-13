# R19 reliability model: failure-prone events per meal × per-event success (2026-10-13)

**Issue:** #27 "[process] Reliability model: steps per meal x per-step success target".

**Why.** A meal is a long chain of grasps, seatings, pours and decisions. With independent events, meal success is roughly the product of the per-event successes. Nothing in the repo modelled failure rates, retries or the schedule spread; the meal times are single numbers. This study:
- counts every failure-prone event in meals A/B/C, prep included;
- collects published success rates and separates structured (keyed, fixtured, repeated) tasks from unstructured food handling;
- models meal success, user interventions and meal time, with and without recovery;
- derives the per-type success targets for 90 / 95 / 99 % meals;
- ranks the design levers;
- gives a verdict and the evidence needed.

**Labels**
- **[sourced]**: a published number (S1–S18 in section 3.1).
- **[assumed]**: my estimate, with its anchor stated. Most rates are this.
- **[est]**: a count or template I made from the repo's own files.
- **[model]**: an output of `r19rel.py`.

**Files** (all new; no existing file was changed):
- `r19rel.py` → `results/r19/rel/inventory.json`, `rates.json`, `mc.json`, `exposure.json`, `targets.json`, `levers.json`, and `stdout.md` (all tables of one run).
- Run: `python r19rel.py N=20000 SEED=1` from `sim/r10/claude` (about 20 s, plain Python + numpy).
- Inputs, read only:
  - `results/r19/prim/library_size.json` (cooking set instances, the R19 mapping of `meal16.py SET=stew ARM=r18`);
  - `results/r19/prep/prep_demand.json` (prep set instances, R19_PREP_AUDIT §6.2);
  - `results/r19seas/cups.json` (seasoning containers under the 10-13 cup rule; plan **P2**, recommended in `research/r19_seasoning_cups.md`);
  - `meal16.py`: its source is executed only up to its `run()` definition, with `SET=stew ARM=r18 USERRICE=1`. Nothing is written by it.

---

## 1. Summary

1. **Event count per meal [est].** Prep included, meal A has about **870** failure-prone events, B **920** and C **690**.
   - Grasps plus releases: 330 / 310 / 230.
   - Prep is 46–60 % of all events.
   - About 120–190 arm "actions" (set instances) per meal, close to the issue's 110–160.
   - 67–78 % of the events are structured (keyed tools, cups, seats, appliance commands). 21–32 % are unstructured: food grasps, food pours, process outcomes, food-state judgements.
2. **Some operations have no robot method at all [est].** A has 4, B 8 and C 4 operations that the as-bought rule leaves to the robot but no design covers: luffa, ginger and garlic peeling, florets, bamboo husking, the fish back-split, squid scoring, tomato peeling, fine 葱丝, okra trimming, chili snipping.
   - **Each one is a certain user step today.** No meal can be rescue-free until these get a method.
   - Buying the stall or 净菜 forms (a user decision; closed by the 10-13 rule) leaves 2 / 4 / 1.
3. **Published per-event data [sourced].**
   - **Structured, near-industrial:** 10⁶–10⁷ cycles between failures for wafer handlers (S1), 96–99 % for bin picking of known parts (S2), 100/100 for learned precise insertion (S5).
   - **Unstructured food:** 75 % autonomous lettuce grasps (S7), 83–91 % food acquisition from plates (S8), 60–85 % for whole kitchen tasks with learned policies (S9).
   - Industry's own bar for little human help is **99–99.5 % per pick** (S6).
   - **No published per-event data exist for home cooking.** The rates used here are mostly assumptions anchored on these sources.
4. **Meal success [model]** (mid rates, ±25 % counts, retry once, then the user). K counts user interventions plus silent defects.

   | Meal | P(clean meal) no recovery | P(clean) with retry | P(K ≤ 1) | E[interventions] | E[silent defects] | Time p50 / p90 min (failure-free) |
   |---|---|---|---|---|---|---|
   | A | 0.08 | **0.27** | 0.62 | 0.72 | 0.60 | 55.3 / 61.9 (50.8 / 55.4) |
   | B | 0.15 | **0.35** | 0.71 | 0.57 | 0.50 | 88.0 / 94.0 (84.3 / 88.4) |
   | C | 0.31 | **0.51** | 0.86 | 0.34 | 0.33 | 47.5 / 52.5 (44.7 / 48.6) |

   - With the optimistic rates: 0.76 / 0.81 / 0.87 clean. With the pessimistic rates: ≤ 3 %.
   - The structural steps of item 2 are **not** in these numbers.
5. **What drives failures [model].** 87–92 % of the expected failures come from the unstructured quarter of the events:
   - process outcomes of prep appliances (22–26 %);
   - food-state perception (22–26 %);
   - food pours, small-item grasps and food contact.

   By set family: the 32 stew-cup placements and the lever presses in A, the presses and piece cycles in B, the seasoning doses and peeled-piece cycles in C. Keyed tools, cups and seats are 7–13 %.
6. **Targets [model]** (worst meal, all rates scaled by one factor, retry as designed):
   - **90 % clean meals:**
     - about **99.84–99.96 %** first-attempt success for every food-handling type;
     - about **99.99–99.996 %** for keyed grasps, seats and contact;
     - all rates about 13× better than the mid assumption.
   - **≤ 1 intervention in 90 % of meals:** food grasps 99.2–99.8 %, process outcomes 99.6 %, keyed grasps 99.98 % (2.5× better).
   - **"≤ 1 a week":** 99.8–99.95 % for food, 99.995 % for keyed parts.
   - Without recovery, each target needs about 2× better rates again.
   - Even with perfect food handling, the keyed events at mid rates alone cost about 0.1 failures per meal. A 95 % clean meal therefore also needs better keyed parts.
7. **Levers, ranked [model].**
   - **Recovery** matters most: detection plus one retry along the stored path halves the expected failures (1.87 → 1.03 per meal at mid; 9.8 → 5.3 at hi).
   - **Then convert food events into structured ones:**
     - food on keyed slot trays: −0.23;
     - a powered section cutter instead of 45 lever presses: −0.17;
     - bench-proven prep appliances: −0.17;
     - better food-state perception: −0.16;
     - a second retry: −0.15;
     - process verification by scale and camera: −0.11;
     - pour-portioning the stew cups: −0.10.
   - Finger swaps, drums, a stirring appliance and faucet batching change almost nothing (≤ 0.01).
   - **All design levers together:** 1.03 → 0.24 failures per meal, **75–81 % clean meals** at mid rates, 24–35 % at hi.
8. **Verdict.**
   - **Not plausible with today's design.**
   - **Plausible in principle**, but only if three things hold:
     - the no-method operations get methods;
     - most food handling becomes keyed or appliance work;
     - the remaining food events reach about 99.9 % first-attempt success with automatic retry.
   - Nothing published shows home food handling at that level.
   - The evidence must come from logged per-event trials: #29 for the process, #10 for the forces, the #27 stage-3 gate for the arm. Section 8 lists them.

---

## 2. Inventory per meal (task 1) [est]

### 2.1 How the events are counted

Every set instance is expanded into failure-prone events with a template (`COOK_T`, `PREP_T` in `r19rel.py`). For example:
- **WOK_PLATE_RINSE** = 1 keyed grasp, 1 food tip onto the plate, 1 water tip at the sink, 1 seating in the cooker slot, 1 release, 2 structured checks (plate present, wok seated), 1 food check (all food out).
- **PRESS** (lever cutter) = pusher grasp, press stroke, release, a re-push of the item (food contact), and the cut outcome (process).
- **PLACE** = locate the piece, small-item grasp, food release.

The sources of the set instances:
- **Cooking:** the R19 library mapping of `meal16.py SET=stew ARM=r18`.
  - Rice is left out (the user's job since 10-13).
  - The old `CUP_*` pours are replaced by:
    - the seasoning containers of `results/r19seas/cups.json` (plan P2: caddy per dish group, cups, drums in the rim holder);
    - a hand count of main-ingredient bowls from the meal16 step labels: A 4, B 11, C 7.
  - Stirring counts per 13.15 s cycle of 5 strokes, as in the library.
- **Appliance commands:** 2 per meal16 step that uses a heat resource, +2 when the wok step stirs (power changes). Plus one command per weighed seasoning dose at the station.
- **Prep:** `prep_demand.json` set instances. The food class of each grasp comes from the ingredient:
  - firm: potato, carrot, ginger, pepper, bamboo, cucumber;
  - soft: tomato, pork, luffa, egg;
  - wet: peeled taro and potato, squid, fish;
  - small: rib pieces, clams, ginger slabs, fine shreds.
  - Plus the as-bought corrections that have a method: a 4th tomato and the tomato scald (`r19_asbought.md` §3.4).
- **Transits:** 0.7 hub transits per set instance [assumed].
- **Hardware:** one "fault per meal" event.

### 2.2 Counts

| Event type | Issue category | Regime | A | B | C |
|---|---|---|---|---|---|
| g_rigid: keyed tool, cup, wok, lid, basket grasp | grasp/release (rigid) | structured | 117 | 131 | 101 |
| r_rigid: release of a seated keyed object | grasp/release (rigid) | structured | 117 | 131 | 101 |
| g_food_rigid: firm produce piece | grasp/release (rigid food) | unstructured | 3 | 3 | 4 |
| g_food_soft: tomato, egg, meat, luffa | grasp/release (soft) | unstructured | 3 | 10 | 1 |
| g_food_wet: peeled taro and potato, squid, fish | grasp/release (wet) | unstructured | 9 | 1 | 7 |
| g_food_small: rib pieces, clams, ginger slabs, spice picks | grasp/release (small) | unstructured | 32 | 8 | 0 |
| r_food: food into a chute, cradle, cup or plate | grasp/release | unstructured | 47 | 22 | 12 |
| seat: wok slot, lid on pot or rack, cup in caddy, tool dock, plate in lever base | insertion/seating | structured | 82 | 99 | 87 |
| contact_mech: faucet lever, fridge door, drawer, lever press, cracker | contact | structured | 50 | 47 | 33 |
| stir_dice: per 5-stroke cycle | contact (scraping) | semi | 9 | 35 | 6 |
| stir_shred: per cycle, shreds and leaves | contact (scraping) | unstructured | 2 | 0 | 10 |
| food_contact: spider scoop, re-push under the blade, eggs out | contact | unstructured | 28 | 22 | 1 |
| pour_liquid: keyed cup or wok, liquid | pour/tip | structured | 10 | 19 | 16 |
| pour_food: wok to plate, basket, chopper bowl, paste cup | pour/tip | unstructured | 37 | 54 | 45 |
| tool_change: finger-set swap | tool change | structured | 5 | 5 | 5 |
| appl_cmd: heat, steamer, stew pot, station dose, smart plug | appliance | structured | 41 | 51 | 61 |
| appl_proc: outcome of a peel, slice, mince, press or dry dose | appliance (process) | unstructured | 38 | 38 | 21 |
| perc_struct: presence, seated, flow, cup ID | perception | structured | 50 | 71 | 58 |
| perc_food: locate food; all out, peel done, shell-free | perception | unstructured | 74 | 62 | 46 |
| transit: hub-to-hub free move | free move | structured | 112 | 106 | 74 |
| hw: hardware fault per meal | — | — | 1 | 1 | 1 |
| **Total** | | | **868** | **916** | **690** |

| Meal | Events | Grasp + release | Of which prep | Prep share of all events | Hot-phase events | Structured / semi / unstructured | Set instances (cook + seasoning + bowls + prep) | No-method operations |
|---|---|---|---|---|---|---|---|---|
| A | 868 | 328 | 236 | 60 % | 84 | 585 / 9 / 274 | 62 + 106 = 168 | 4 |
| B | 916 | 306 | 168 | 46 % | 147 | 661 / 35 / 220 | 119 + 67 = 186 | 8 |
| C | 690 | 226 | 120 | 48 % | 102 | 537 / 6 / 147 | 75 + 44 = 119 | 4 |

**Against the issue's estimate** (110–160 actions, 190–310 grasp/release events): the action count agrees. The grasp/release count is higher because prep (R19 audit) and the 10-13 seasoning cups are now included.

### 2.3 Operations with no designed robot method (structural user steps)

Sources: `research/r19_asbought.md` §3–4 and `R19_PREP_AUDIT.md` §3 and §5.7. Until a method exists, each one is a **certain** user step per meal, independent of any success rate.

| Meal | Operations | If the user reopens the purchase forms (stall cuts, 净菜 florets, peeled garlic, shelled shoots, 辣椒段) |
|---|---|---|
| A | luffa peel; broccoli florets + stem peel; garlic clove peel; ginger knob peel | 2 left: luffa, ginger |
| B | bamboo husk; sea-bass back-split; tomato peel after scalding; fine scallion shreds (comb concept only); okra cap trim + halving (~15 pods); garlic peel; ginger peel; dried-chili snipping | 4 left: tomato peel, 葱丝, okra, ginger |
| C | squid opening + cross-scoring; garlic peel; ginger peel; dried-chili snipping | 1 left: ginger |

Other operations are counted as events even though their method is unproven. For example:
- taro in the abrasive peeler, untested;
- the meat slicer, "missing" in the audit;
- pork-belly cubes on a lever grid, cutting force unsourced;
- the egg cracker, a concept.

They therefore carry the higher process-outcome rates.

---

## 3. Per-type success rates (task 2)

### 3.1 Published data [sourced]

| # | Source | Task and regime | Number | What it does and does not tell us |
|---|---|---|---|---|
| S1 | Wafer-handling robots, Sematech target ([Semiconductor Digest](https://sst.semiconductor-digest.com/?p=40941)) | Structured, cleanroom, identical wafers | 10 million mean cycles between failures (MCBF) | The ceiling for perfectly structured pick-place: about 1e-7 per cycle. Hardware failures only; ideal objects. |
| S2 | Pickalo, UR5e + parallel jaw + D435i ([arXiv 2604.04690](https://arxiv.org/abs/2604.04690)) | Known industrial parts, cluttered bins, 30-min runs | **96–99 % grasp success**, up to 600 picks/h | The same arm class. Unfixtured parts: pose error dominates. |
| S3 | Dex-Net 4.0, Mahler et al., Science Robotics 2019 ([pdf](https://goldberg.berkeley.edu/pubs/Ambidextrous-Grasping-Science-Robotics-Jan-2019.pdf)) | Novel objects, bins of ≤ 25 | **> 95 % reliability**, > 300 picks/h | Rigid household objects, not food. |
| S4 | QT-Opt, Kalashnikov et al., CoRL 2018 ([arXiv 1806.10293](https://arxiv.org/abs/1806.10293)) | Unseen objects, closed-loop regrasping | **96 %** | 580k training grasps. Regrasping is built in. |
| S5 | HIL-SERL, Luo et al. 2024 ([arXiv 2410.21845](https://arxiv.org/abs/2410.21845)) | Precise insertion and assembly (RAM, USB, dashboard, timing belt) | **100 % over 100 trials** per task | Shows the bar for a "perfect" lab result: 100/100 only proves ≥ 97 % at 95 % confidence. |
| S6 | Covariant / Abbeel in [MIT Technology Review 2020](https://www.technologyreview.com/2020/01/29/276026/ai-powered-robot-warehouse-pickers-are-now-ready-to-go-to-work/) | Warehouse piece picking | "**99 %, maybe 99.5 %**" needed to run without much human help; 90 % is "value-losing" | Industry's own bar for little human help. |
| S7 | Misimi et al., IROS 2018 ([arXiv 2309.12856](https://arxiv.org/abs/2309.12856)) | Lettuce, learning from demonstration with tactile sensing | Autonomous **75 %** (70 grasps); human teleoperated demos **94.7 %** (497/525) | Compliant food. Even teleoperated humans fail 5 %. |
| S8 | SPANet, Feng et al., ISRR 2019 ([arXiv 1906.02350](https://arxiv.org/abs/1906.02350)) | Food acquisition (fork) from plates, 2,450 trials, 16 foods | **83–91 %** on cluttered plates | Soft or slippery items (banana, kiwi) are the worst class. |
| S9 | Mobile ALOHA, Fu et al. 2024 ([arXiv 2401.02117](https://arxiv.org/abs/2401.02117)) | Whole kitchen tasks, learned bimanual policies | Cook shrimp **60 %** (5 trials); rinse pan 80 %; use cabinet 85 %; wipe wine 100 % (20 trials each) | Learned policies, not stored verified paths. A floor for contact tasks. |
| S10 | SayCan, Ahn et al. 2022 ([arXiv 2204.01691](https://arxiv.org/abs/2204.01691)) | 101 long-horizon instructions in a mock kitchen | **74 %** execution; −14 points in the real kitchen | Long chains of learned skills. |
| S11 | BakeBot, Bollini et al., MIT 2012 ([DSpace](https://dspace.mit.edu/handle/1721.1/74451)) | PR2 baking cookies from a recipe | **16 of 27** runs edible (static state machine); 5 of 5 (dynamic) | The only whole-recipe cooking-robot success rate found. Small n. |
| S12 | OK-Robot, Liu et al., RSS 2024 ([arXiv 2401.12202](https://arxiv.org/abs/2401.12202)) | Pick-and-drop in 10 real homes | **58.5 %**; 82 % in uncluttered homes | Unstructured home manipulation. |
| S13 | TidyBot, Wu et al. 2023 ([arXiv 2305.05658](https://arxiv.org/abs/2305.05658)) | Real-world tidying | **85 %** | Unstructured home manipulation. |
| S14 | Chef Robotics, vendor case study ([Ultralytics](https://www.ultralytics.com/customers/chef-robotics-leverages-ultralytics-yolo-for-precise-food-assembly)) | Food assembly lines, 79 M+ servings | ~**99.5 %** detection accuracy | A vendor claim, for perception only. No per-pick failure rate is published. |
| S15 | Miso Robotics Flippy ([Business Wire 2025](https://www.businesswire.com/news/home/20250617965602/en)) | Fry station | "**99 % uptime**" | A vendor claim; not a per-event rate. |
| S16 | (not used) Soft-gripper food papers in the search results | Raw chicken, fruit | 63–95 % | Snippets only; I could not check the primary sources. |
| S17 | Home-automation forums ([openHAB](https://community.openhab.org/t/reliability-of-zigbee-devices/111911)) | Zigbee commands | "a few percent" fail | Anecdotal. It sets only the hi case for consumer smart plugs. |
| S18 | Do & Burgard 2018 ([arXiv 1810.03303](https://arxiv.org/abs/1810.03303)) | Robot pouring to a level, PR2, 250 pours | Mean error **13–31 ml** | Dose accuracy, not a failure rate. |

**What the data says**
- **Structured, keyed and repeated tasks** can be extremely reliable: S1 at about 1e-7, industrial cells typically far better than 99.9 %. But no source gives a per-event number for a cobot in a wet, greasy home kitchen.
- **Unstructured food handling** in the literature sits at **75–96 %** per attempt (S7, S8, S3, S4). Lab "perfect" results have n ≤ 100 (S5).
- **Whole kitchen tasks** by learned robots sit at 60–85 % (S9, S10). The one whole-recipe cooking robot reached 59 % edible runs (S11).
- **Industry's bar** for little human help is 99–99.5 % per pick (S6).

### 3.2 Rates used (first-attempt failure probability per event)

The full basis text is in `rates.json`.
- d = the share of failures the robot detects itself.
- r = the share of detected failures it can retry along stored paths (R19_MOTION_LIBRARY §4).
- A retry fails with q = max(m·p, q_floor), because failures are correlated: the item that slipped once often slips again.

| Type | Regime | lo | **mid** | hi | Label | d | r | q_floor |
|---|---|---|---|---|---|---|---|---|
| g_rigid | structured | 1e-4 | **5e-4** (99.95 %) | 2e-3 | assumed, between S2 and S1 | .95 | .9 | .05 |
| r_rigid | structured | 2e-5 | **1e-4** | 5e-4 | assumed | .8 | .5 | .05 |
| g_food_rigid | unstructured | 1e-3 | **5e-3** (99.5 %) | 3e-2 | sourced range S2–S4; mid = a known firm item on a tray | .9 | .9 | .2 |
| g_food_soft | unstructured | 3e-3 | **1.5e-2** (98.5 %) | 8e-2 | sourced range S7, S8 | .9 | .9 | .2 |
| g_food_wet | unstructured | 5e-3 | **2e-2** (98 %) | 1e-1 | sourced range S7, S8; wet μ unmeasured (#10) | .9 | .9 | .2 |
| g_food_small | unstructured | 5e-3 | **2e-2** | 1e-1 | assumed (+S8) | .9 | .9 | .2 |
| r_food | unstructured | 5e-4 | **3e-3** | 1e-2 | assumed: sticks to wet fingers, bounces out | .7 | .6 | .2 |
| seat | structured | 2e-4 | **1e-3** | 5e-3 | assumed; S5; reserves 0.3 mm (lid rack) to 2.4 mm (wok) | .9 | .8 | .05 |
| contact_mech | structured | 2e-4 | **1e-3** | 5e-3 | assumed; S9 as a floor | .9 | .7 | .05 |
| stir_dice (per cycle) | semi | 2e-4 | **1e-3** | 5e-3 | assumed; R15 rigid dice only | .7 | .6 | .1 |
| stir_shred (per cycle) | unstructured | 1e-3 | **5e-3** | 2e-2 | assumed; README_R10:544 "not credible" | .6 | .5 | .2 |
| food_contact | unstructured | 2e-3 | **1e-2** | 5e-2 | assumed; S9 cook-shrimp floor | .8 | .8 | .2 |
| pour_liquid | structured | 1e-4 | **5e-4** | 3e-3 | assumed; S18 is dose error | .6 | .7 | .1 |
| pour_food | unstructured | 1e-3 | **5e-3** | 2e-2 | assumed; sim 81–91 % of dice on the plate | .8 | .7 | .2 |
| tool_change | structured | 1e-4 | **1e-3** | 5e-3 | assumed; dovetail never simulated | .95 | .8 | .05 |
| appl_cmd | structured | 1e-5 | **1e-4** | 1e-2 | assumed: wired with read-back; hi = smart plug (S17) | .95 | .95 | .05 |
| appl_proc | unstructured | 2e-3 | **1e-2** | 5e-2 | assumed: peel incomplete, slicer jam, tomato stuck, doser caked | .7 | .5 | .3 |
| perc_struct | structured | 1e-4 | **5e-4** | 3e-3 | assumed; S14 | .5 | .8 | .05 |
| perc_food | unstructured | 1e-3 | **5e-3** | 3e-2 | assumed; S14 | .4 | .7 | .2 |
| transit | structured | 1e-5 | **1e-4** | 1e-3 | assumed: protective stop on a hub transit | 1 | .5 | .5 |
| hw (per meal) | — | 1e-4 | **1e-3** | 1e-2 | assumed: arm, gripper, PC or station fault, MTBF ~1,000 h | 1 | 0 | — |

**How to read the levels**
- **mid** puts keyed parts near the S6 industry bar or better (99.9–99.99 %), and food grasps at 98–99.5 %: better than every lab food result in 3.1.
- **lo** is optimistic for a home system.
- **hi** is roughly the published lab level for food (90–97 %) and a mediocre keyed system (99.5–99.8 %).

---

## 4. Model (task 3) [model]

**Monte Carlo per meal** (`simulate()`, N = 20,000):
1. **Counts.** Each event type's count is scaled by one common factor U(0.75, 1.25) per sample, because the templates are estimates.
2. **First attempts.** Failures are drawn Binomial(n, p).
3. **Recovery policies:**
   - **none:** every failure needs the user (the issue's pⁿ).
   - **user:** a detected failure goes to the user; an undetected one is a **silent defect** (wrong dose, food dropped, peel left on).
   - **retry (as designed):** a detected, retryable failure is retried once along the stored path (re-sense, re-grasp, repeat the tip, re-seat). If the retry fails too, it goes to the user. A non-retryable failure goes to the user.
4. **K** = interventions + silent defects. A **clean meal** has K = 0.
5. **Time.**
   - The `meal16.py` schedule is re-run per sample: arm durations ±30 % (the issue's figure), cooking times ±10 % [assumed].
   - Plus the prep-first block, uniform in the audit's range: A 6.9–17.4, B 6.0–10.4, C 5.3–12.7 min. The audit calls it a lower bound.
   - Plus the time of each retry.
   - Plus, for each intervention, the user's response (lognormal, median 90 s) and fix time (median 60 s) [assumed: the user is at home].
   - Plus 2 person-in-reach pauses of 10–60 s per meal, and a 0.3 s decision latency per set [assumed].
   - All delays are added to the meal end. Once prep is packed in, the arm is busy about 90 % of meals A and C and about 65 % of B (R19_PREP_AUDIT §6.3), so this is conservative mainly for B.
6. **Dish at risk:** an intervention during a hot phase (stirring, pours into the hot wok, the wok lid, blanch scoops, hot oil) answered after more than 60 s.

**Targets (analytic).** Poisson approximation; it matches the Monte Carlo within ±0.01.
- E[K] = Σ n·p·[d·(r·q + 1 − r) + (1 − d)].
- P(K = 0) = e^(−E[K]).
- P(K ≤ 1) = e^(−λ)(1 + λ).

Two allocations are used:
- **Equal:** every event gets the same residual probability λ / N.
- **Uniform scaling:** all mid rates × s, so the relative difficulty is kept.

Allocation 2 keeps the structured types at mid and scales only the food types.

---

## 5. Results [model]

### 5.1 Meal success, interventions and time

| Meal | Rates | Policy | P(clean) | P(K ≤ 1) | E[interv.] | E[silent] | P(hot dish at risk) | T p50 / p90 min |
|---|---|---|---|---|---|---|---|---|
| A | lo | retry | 0.76 | 0.97 | 0.15 | 0.12 | 0.4 % | 53.3 / 58.3 |
| A | mid | none | 0.08 | 0.29 | 2.50 | — | 7.8 % | 60.2 / 70.4 |
| A | mid | user | 0.09 | 0.29 | 1.91 | 0.60 | 5.2 % | 58.3 / 67.5 |
| A | **mid** | **retry** | **0.27** | **0.62** | **0.72** | **0.60** | **2.2 %** | **55.3 / 61.9** |
| A | hi | retry | 0.00 | 0.01 | 3.62 | 3.15 | 9.9 % | 65.9 / 78.3 |
| B | lo | retry | 0.81 | 0.98 | 0.11 | 0.10 | 0.8 % | 86.5 / 91.1 |
| B | mid | none | 0.15 | 0.43 | 1.92 | — | 13 % | 91.7 / 100.9 |
| B | **mid** | **retry** | **0.35** | **0.71** | **0.57** | **0.50** | **3.5 %** | **88.0 / 94.0** |
| B | hi | retry | 0.00 | 0.03 | 2.90 | 2.67 | 18 % | 96.6 / 107.4 |
| C | lo | retry | 0.87 | 0.99 | 0.07 | 0.07 | 0.5 % | 46.7 / 50.9 |
| C | mid | none | 0.31 | 0.67 | 1.17 | — | 11 % | 49.6 / 57.0 |
| C | **mid** | **retry** | **0.51** | **0.86** | **0.34** | **0.33** | **3.1 %** | **47.5 / 52.5** |
| C | hi | retry | 0.03 | 0.14 | 1.75 | 1.77 | 15 % | 52.3 / 61.2 |

- **Failure-free schedule plus prep block:** p50 / p90 = A 50.8 / 55.4, B 84.3 / 88.4, C 44.7 / 48.6 min. The meal16 single numbers are 38.2 / 75.6 / 35.6 without prep.
- **Failures and recovery** add about 3–5 min at p50 and 4–7 min at p90 at mid rates. Without recovery they add 8–15 min at p90. At hi rates they add 13–23 min at p90 with retry, and up to 60 min without recovery.
- **The issue's pⁿ, in this model:**
  - At mid rates, no recovery, meal A's 868 events give 2.5 expected failures. That is an average per-event success of **99.71 %** and P(clean) = 8 %.
  - The issue's 0.995¹⁵⁰ = 47 % assumed 150 events. Counting every grasp, seat, pour, check and command, with prep and the seasoning cups, gives 5–6× as many events.

### 5.2 Exposure: where the expected failures come from (mid rates, retry)

| Meal | E[K] | By type | By set family |
|---|---|---|---|
| A | 1.33 | appl_proc 22 %, perc_food 22 %, g_food_small 17 %, food_contact 10 %, pour_food 8 % | **PLACE 31 %** (32 stew-cup placements), **PRESS 26 %** (27 lever presses), PIECE_SHORT 9 % |
| B | 1.08 | appl_proc 26 %, perc_food 22 %, pour_food 14 %, food_contact 10 % | PRESS 22 %, PIECE 15 %, SEAS_DOSE 8 %, MAIN_BOWL 7 %, spice picks 7 %, eggs 7 % |
| C | 0.68 | perc_food 26 %, appl_proc 23 %, pour_food 18 %, g_food_wet 7 %, stir_shred 6 % | SEAS_DOSE 13 % (dry doser caking), PIECE_SHORT 11 %, MINCE 8 %, MAIN_BOWL 7 %, MEAT 7 % |

- The structured events are two thirds of the count but only **7–13 % of E[K]**.
- About **half of E[K] is silent defects**: a food-state or process error that nobody detects. Better detection turns silent defects into interventions (section 6.3): it helps the meal and costs the user.

---

## 6. Targets (task 3) [model]

### 6.1 Equal allocation and the overall scale factor

| Meal-level target | λ (expected K per meal) | Equal allocation: residual per-event success, A–C | Scale s on all mid rates, with retry (worst meal) | without recovery |
|---|---|---|---|---|
| P(clean) ≥ 90 % | 0.105 | 99.985–99.989 % | 0.079 | 0.042 |
| P(clean) ≥ 95 % | 0.051 | 99.993–99.994 % | 0.039 | 0.020 |
| P(clean) ≥ 99 % | 0.010 | 99.999 % | 0.008 | 0.004 |
| P(K ≤ 1) ≥ 90 % | 0.532 | 99.923–99.943 % | 0.40 | 0.21 |
| P(K ≤ 1) ≥ 95 % | 0.355 | 99.948–99.962 % | 0.27 | 0.14 |
| P(K ≤ 1) ≥ 99 % | 0.149 | 99.978–99.984 % | 0.11 | 0.06 |
| E[K] ≤ 1 a week (7 meals) | 0.143 | 99.979–99.985 % | 0.11 | 0.06 |

The issue's own figure (90 % meal success needs ≥ 99.93–99.96 % per action) assumed 150–250 actions. With 690–920 events per meal, the residual per-event figure is **99.985–99.989 %** (1 in 6,600–8,700).

### 6.2 Per-type first-attempt success needed (retry as designed; worst meal; all types scaled together)

| Type | Regime | Mid assumption | Clean ≥ 90 % | Clean ≥ 95 % | Clean ≥ 99 % | K ≤ 1 in 90 % | K ≤ 1 in 95 % | K ≤ 1 in 99 % | ≤ 1 a week |
|---|---|---|---|---|---|---|---|---|---|
| g_rigid | structured | 99.950 | 99.996 | 99.998 | 99.9996 | 99.980 | 99.987 | 99.994 | 99.995 |
| seat, contact_mech, tool_change, stir_dice | structured / semi | 99.900 | 99.992 | 99.996 | 99.999 | 99.960 | 99.973 | 99.989 | 99.989 |
| pour_liquid, perc_struct | structured | 99.950 | 99.996 | 99.998 | 99.9996 | 99.980 | 99.987 | 99.994 | 99.995 |
| g_food_rigid, pour_food, perc_food, stir_shred | unstructured | 99.500 | 99.960 | 99.981 | 99.996 | 99.800 | 99.866 | 99.944 | 99.946 |
| g_food_soft | unstructured | 98.500 | 99.881 | 99.942 | 99.989 | 99.399 | 99.598 | 99.832 | 99.839 |
| g_food_wet, g_food_small | unstructured | 98.000 | 99.841 | 99.923 | 99.985 | 99.199 | 99.465 | 99.776 | 99.785 |
| food_contact, appl_proc | unstructured | 99.000 | 99.921 | 99.961 | 99.992 | 99.599 | 99.732 | 99.888 | 99.892 |
| r_food | unstructured | 99.700 | 99.976 | 99.988 | 99.998 | 99.880 | 99.920 | 99.966 | 99.968 |
| appl_cmd, r_rigid, transit | structured | 99.99 | 99.999 | 99.9995 | 99.9999 | 99.996 | 99.997 | 99.999 | 99.999 |

**Allocation 2: keyed parts stay at mid; only food handling improves.**
- The structured events alone give E[K] = 0.09–0.11 per meal (keyed parts at mid, hardware 1e-3).
- **Clean ≥ 90 %:** feasible only for A and C, with the food types about 35–110× better than mid (s_u 0.009–0.029, i.e. 99.94–99.995 % food grasps). It is infeasible for B.
- **Clean ≥ 95 % or 99 %:** infeasible. The keyed parts must improve as well.
- **K ≤ 1 in 90 % of meals:** s_u = 0.36–0.75, i.e. wet and small food grasps 98.5–99.3 %, firm ones 99.6–99.8 %.
- **≤ 1 a week:** s_u = 0.03–0.09, i.e. food grasps 99.8–99.95 %.

### 6.3 Sensitivity to the recovery assumptions (mid, retry; E[K] for A / B / C)

| Variant | E[K] | E[interventions] |
|---|---|---|
| Baseline | 1.33 / 1.08 / 0.68 | 0.73 / 0.57 / 0.35 |
| Independent retries (q_floor 0) | 1.08 / 0.90 / 0.59 | 0.48 / 0.40 / 0.25 |
| Strongly correlated retries (q_floor 0.5) | 1.78 / 1.40 / 0.88 | 1.18 / 0.90 / 0.54 |
| Detection −0.2 on every type | 1.63 / 1.30 / 0.82 | 0.53 / 0.41 / 0.25 |
| Detection 0.95 on every type | 1.07 / 0.86 / 0.54 | 0.95 / 0.76 / 0.48 |

How correlated retries are is worth about ±30 % of E[K]. It must be measured: does a re-grasp of an item that slipped succeed?

---

## 7. Design levers, ranked by effect (task 4) [model]

Mean E[K] per meal over A/B/C, retry policy. "Change" is against the baseline at the same rate level. The multipliers are assumptions about what each lever achieves, stated in the lever.

| Rank | Lever | Class | mid: E[K] mean | change | P(clean) | hi: change |
|---|---|---|---|---|---|---|
| — | Baseline (as designed, retry once) | | 1.03 | — | 0.37 | (5.29) |
| 1 | **Automatic detection + retry along stored paths** (vs every failure to the user) | cheap recovery | — | **−0.84** | 0.18 → 0.37 | **−4.54** |
| 2 | Food on keyed slot trays (food grasp p ×0.3, locate ×0.5) | better per event | 0.80 | −0.23 | 0.46 | −1.29 |
| 3 | Powered section / belt cutter instead of 45 lever presses (A 27, B 18) | fewer events | 0.86 | −0.17 | 0.43 | −0.83 |
| 4 | Bench-proven prep appliances (process outcome p ×0.3) | better per event | 0.86 | −0.17 | 0.44 | −0.85 |
| 5 | Better food-state perception (perc_food p ×0.3) | better per event | 0.86 | −0.16 | 0.43 | −0.99 |
| 6 | Retry twice (k = 2) | cheap recovery | 0.88 | −0.15 | 0.43 | −0.77 |
| 7 | Process verification: scale + camera after every prep output (detection → 0.9) | cheap recovery | 0.92 | −0.11 | 0.41 | −0.62 |
| 8 | Pour-portion the stew cups (A: 32 placements → 8 pours) | fewer events | 0.93 | −0.10 (A −0.31) | 0.40 | −0.52 |
| 9 | Grasp / pour / placement sensing (detection → 0.98) | cheap recovery | 0.96 | −0.07 | 0.39 | −0.30 |
| 10 | Keyed lead-ins + force-monitored contact (keyed p ×0.3) | better per event | 0.98 | −0.04 | 0.39 | −0.22 |
| 11 | Stirring appliance at the wok | fewer events | 1.02 | −0.01 | 0.37 | −0.00 |
| 12 | One finger set for most items (5 → 1 swap) | fewer events | 1.03 | −0.00 | 0.37 | −0.01 |
| 13 | One prep faucet session instead of 2 | fewer events | 1.03 | −0.00 | 0.37 | −0.01 |
| — | No drum rim holder found (P1 instead of P2) | | 1.03 | +0.01 | 0.37 | +0.02 |
| — | Consumer smart plugs without read-back | | 1.10 | +0.07 | 0.34 | (already hi) |
| **Σ** | **All design levers 2–10, 12, 13 together** | | **0.24** (A 0.21, B 0.29, C 0.23) | **−0.78** | **0.78** | **−4.08** (hi E[K] 1.20) |

**The package in the Monte Carlo** (mid / hi rates):

| Meal | P(clean) | P(K ≤ 1) | E[interventions] | T p50 / p90 min |
|---|---|---|---|---|
| A | 0.81 / 0.35 | 0.98 / 0.72 | 0.17 / 0.81 | 53.4 / 58.4 |
| B | 0.75 / 0.24 | 0.97 / 0.58 | 0.23 / 1.06 | 86.9 / 91.9 |
| C | 0.79 / 0.33 | 0.98 / 0.69 | 0.17 / 0.84 | 47.0 / 51.5 |

Times are at mid rates.

**Structural lever (a user decision, not in the numbers above).** Reopening the purchase forms (stall back-split and scoring, 净菜 florets, peeled garlic, shelled shoots, 辣椒段) removes 2 / 4 / 3 certain user steps from A / B / C. That is larger than every stochastic lever combined. The alternative is a robot method for each (section 2.3).

**What this means**
- **Cutting structured events barely matters.** Finger swaps, drums, faucet sessions and the stirrer each change E[K] by < 0.01 at mid. Their events are already among the most reliable.
- **What matters** is the unstructured quarter:
  - make food handling keyed (slot trays, appliances that take a whole batch);
  - prove the prep appliances on real food (#10);
  - verify every prep output by weight and camera.
- **Cheap recovery is the biggest single lever.** It is software plus the sensors already designed: jaw position and force band, current monitors, cameras. It halves E[K] at any rate level. It works only if the stored-path retreat really is safe (#26).
- **Smart plugs without read-back** cost about as much as all finger swaps, faucet sessions and drums together save. Use wired I/O or plugs that report power.

---

## 8. Verdict and evidence needed (task 5)

**Is a robot that needs no user rescue in most meals plausible?**

1. **With today's design: no.**
   - 4 / 8 / 4 operations per meal have no robot method, so every meal has certain user steps.
   - Leaving those aside, at mid rates with retry only 27 / 35 / 51 % of meals are clean.
   - With the published lab level for food handling (hi rates), almost none are.
2. **"Most meals" (> 50 %) clean is plausible only if all three of these hold:**
   - the no-method operations get methods, or the user reopens the purchase forms;
   - the design levers are taken: keyed food trays, powered cutters instead of the lever, proven appliances, output verification, automatic retry;
   - food handling reaches about **99.5–99.8 % first-attempt success** and keyed parts **≥ 99.95 %**: the mid rates. The package then gives 75–81 % clean meals and ≤ 1 intervention in 97–98 % of meals.
3. **≥ 90 % clean meals** needs food handling at **99.84–99.96 %** and keyed events at **99.99 %+** (section 6). No published food-handling result is near that: the best lab numbers are 95–99 % with n ≤ a few hundred. Industrial structured tasks are near it (S1, S6). So the only credible route is to turn food events into structured ones.
4. **A realistic first claim** would be "**≤ 1 intervention in 90 % of meals**", which needs about 2.5× the mid rates: food grasps 99.2–99.8 %, process outcomes 99.6 %. That is a target a bench program can confirm or reject.

**Evidence needed, and how many trials**

At 95 % confidence, n = ln 0.05 / ln(1 − p) failure-free trials:

| Claim | Failure-free trials |
|---|---|
| per-event failure ≤ 1 % | 299 events |
| per-event failure ≤ 0.1 % | 2,995 events |
| per-event failure ≤ 0.01 % | 29,956 events |
| clean meals ≥ 90 % | 29 clean meals in a row |
| clean meals ≥ 95 % | 59 clean meals in a row |
| clean meals ≥ 99 % | 299 clean meals in a row |

What each issue can supply:
- **#29, robot-free trial** (the user cooks B and C the robot's way).
  - It measures the **process** failures the robot cannot beat: one-hand substitutes that fail, residue after tip-plating, lever cuts that stick, doneness spread. These are the appl_proc / pour_food / stir_shred rates, with a human as the executor.
  - **Add to its protocol:** log every step as done / redone / failed, per event type, so the trial yields per-type process failure rates. Two weekends give only about 100–300 events per type: enough to bound the process rates at the 1–3 % level, not at 0.1 %.
- **#10, bench forces.** Whether the tomato wedge, greens bundles, pork-belly cubes and egg cracker work at all with about 100 N. Below the force, appl_proc is 1, not 1 %.
- **#26, FMEA and fault injection.** It supplies d and r per set: the recovery side of this model (section 6.3 shows ±30 % of E[K]). The MuJoCo fault injection measures d. The bench measures whether a re-grasp after a slip succeeds (q_floor).
- **#27, stage-3 gate** (one cheap arm cooks one wok dish 30–50 times).
  - A wok dish is about 100–150 events, so 50 dishes give about 5,000–7,500 events. That bounds the aggregate per-event rate at about 5e-4 if failure-free, but not per type.
  - **Log per event type** with the same taxonomy as `rates.json`, so the run updates this model directly.
  - The gate should pass only if the measured food-handling rates reach the "K ≤ 1 in 90 %" column of section 6.2.
- **Before anything is bought:** per-type bench tests of the top exposures:
  - small-piece placement or pour-portioning (A);
  - the lever presses or a powered cutter;
  - peeled-taro and potato grasps (wet);
  - the dry dosers (caking);
  - output verification by weight.

---

## 9. Honesty notes and limits

- **Counts are estimates.** The set templates are mine. Prep counts inherit the audit's estimates, and the as-bought rule says those are lower bounds. The main-ingredient bowls are a hand count. Transits are 0.7 per set. All counts are varied ±25 % in the Monte Carlo.
- **Rates are mostly assumptions.** Only the food-grasp ranges and the structured anchors come from published numbers, and none of those is a home-kitchen cobot. The lo / mid / hi spread is wide on purpose. The ranking of the levers holds at both mid and hi; the absolute success rates do not carry over.
- **Independence.** Events are drawn independently. Common-cause failures would make the tails heavier: a fixture moved, a layout version mismatch, a wet gripper pad all afternoon, a slimy batch of taro. The model under-states the chance of bad meals with several failures.
- **Silent defects** are scored like interventions (K). Some would be harmless (slightly uneven dose), others ruin a dish. Food quality itself (doneness, taste) is not modelled.
- **Time model.** Every retry and intervention is added to the meal end. The user is assumed at home and answering in about 90 s (median). If not, the meal stalls; that case is not modelled. The schedule re-run uses meal16's list scheduler unchanged. Its durations are themselves assumptions (`meal16.py:8`). The 3.6 s executable stir period (R19_SMOOTH) and the P2 seasoning moves (+2.5–3 min of arm time, `r19_seasoning_cups.md`) are **not** added to the schedule.
- **Seasoning plan.** `results/r19seas/cups.json` (14:38) and `research/r19_seasoning_cups.md` (14:42) came from a parallel study during this one. I used its P2 counts as published. If they change, re-run `r19rel.py`; the effect of P1 vs P2 is ≤ 0.02 in E[K].
  - The later DECISIONS entry "Seasoning cups: user answers" adopts the four merges, which removes 1 / 3 / 0 containers. I kept the "as he does" counts; the effect is < 0.01 in E[K].
  - Three items from that entry are outside the meal and not counted: dishwasher loading, batch-making 糖色, and water from the dispenser. They add their own events.
- **Rice** is the user's (10-13) and is not counted. Serving is the user's (10-12) and not counted. Fridge trips: 1 per meal (prep_demand); R19 system cost estimated 2–3.
- **Sources** were read via web search and fetch (read-only). S16 is listed but not used, because its primary sources were not checked. S14, S15 and S17 are vendor or anecdotal.
