SCOPE: R08, a clean low-profile under-cabinet rail cell; make the carrot run end to end, then the other three (robot_rail/sim/r08/integrator/).

Work plan:
1. **Clean base.**
   - Build a compact package in sim/r08/integrator:
     - scene builder: the kitchen from L101 plus the new low-profile stations;
     - checker wrapper: imports and keeps the sim/r05/integrator/reference.py semantics; include a regression test that reproduces a few R07 verdicts on unchanged inputs;
     - IK/solver: collision-aware, with ≥96 starts;
     - planner: RRT-Connect with a ≤4 mm replay;
     - persistent state machine with contained transformations;
     - runner scripts.
   - Copy the needed models and vendor files. One version of each file; no v2–v7 sprawl.
2. **Layout.** Place the low-profile stations, basket and bowls by reachability maps from the rail band: maximise reserve, keep open approach corridors, and check the wash basket against the jet axis.
3. **Carrot first.**
   - Steps: load → wash → peel → mandoline slices → output bowl, plus scrap. Then park, with fold/unfold.
   - Solve every stroke, then plan every connection and the fold/unfold.
   - Iterate the layout and poses until the full carrot sequence executes as one connected, checked, conserved sequence.
4. **Then potato, bok choy and tomato** in the same scene. Then the full meal: one sequence, all connections planned. Then idle: snapshot plus fold/unfold.
5. **Robustness pass.** Raise the low-reserve states. Report the reserve distribution.
6. **Schedule and cost.**
   - An executed-path timeline at home-tier speeds, including station times, soaking and draining.
   - Cost: one 15% reserve, one safety package. Remove the processor from the BOM.
   - The free counter area left for a person when idle.
7. **Renders** (≤1600 px):
   - an overview;
   - each station;
   - a parked view with the doors open;
   - a frame strip of the executed carrot sequence (about 24 frames), labelled honestly.

Keep results/iterations.csv. Report strokes, internal paths, connections, products completed (n/4), idle and the reserve stats.

**Do not deliver before** either:
- (a) the full carrot sequence plus fold/unfold executes as one connected, checked sequence; or
- (b) at least 8 documented iterations with evidence show what blocks, with structural causes named.

Deliver results/phase_summary.json, results/motion.json, results/state_sequence.json, results/idle.json, results/schedule.json, results/costs.csv, results/clearance.json, results/iterations.csv, renders and robot_rail/posts/r08/integrator.md.
Final reply: `DONE integrator carrot=<pass|fail> products=<n>/4 strokes=<p>/<t> connections=<c>/<m> idle=<pass|fail> prep_min=<v> cost_cny=<v> min_reserve_mm=<v>`.
