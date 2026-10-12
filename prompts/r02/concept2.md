SCOPE: multi-rail, multi-arm concept with the new tools, checked in simulation (robot_rail/sim/r02/concept2/).

Inputs to read first:
- posts/r01/concept.md, posts/r01/market.md and posts/r01/reviewer.md, if present: the single-rail baseline;
- posts/r02/transport.md, with results/transport_options.json;
- posts/r02/tools.md, with results/process_v2.json.

1. **Model.** Build MJCF models of the recommended transport options in the galley kitchen. Use the new tool and appliance layout. Use real arm models (reuse sim/r01/concept/models and vendor). Base the checker on R01's adapted checker. Only robot and phase plumbing may change; diff it and justify every change. Rules stay as in common.md.
2. **Sweep.**
   - transport option;
   - number of rails and their heights or stand-offs;
   - number of arms (2, 3 or 4) and arm models, mixed models allowed;
   - mount orientation;
   - with or without switching.

   Each arm's carriage position (and its rail, if switching) is sampled per phase and frozen during strokes. Arms that are not in use park, without collision.
3. **Full check.** For the best 1–2 designs, run every phase of process_v2 with ≥96 seeds each. Also run the old P01–P16 with the single-rail baseline arm, for comparison. Report:
   - feasible seeds and best torque ratios per phase;
   - pass/park conflicts between arms;
   - a simple timeline: can washing and cutting run in parallel, and what is the total prep time for the reference meal from cook_ref?
4. **Loads** on rails and carriages for mounting, at the worst case.
5. **Power-track idea (user, 2026-10-07).** The user likes the household 轨道插座 (power track: an aluminium track with copper busbars; adapters clip in anywhere). Use it as the baseline for **appliance and tool power** on and behind the counter. For the **moving arms**, use posts/r02/transport.md's addendum on power tracks: a sliding conductor rail (48 V SELV preferred near the sink), dock-and-charge at stops, or a cable carrier. Model the track/conductor envelope as a robot part. Report which one the best design uses and its power budget per arm (average and peak, from datasheets).
6. **Renders** (≤1600 px, CPU): an overview, two arms passing, each main phase, and parked.

Deliver results/sweep.csv, results/best.json, renders and robot_rail/posts/r02/concept2.md.
Final reply: `DONE concept2 best=<description> phases=<passed>/<total> arms=<n> rails=<n> cost_cny=<value>`.
