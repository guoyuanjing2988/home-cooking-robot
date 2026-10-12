SCOPE: R05, make the full reference meal run as one connected, collision-checked motion (robot_rail/sim/r05/integrator/). Start from R04 (sim/r04/integrator, posts/r04/integrator.md, posts/r04/reviewer.md). Copy the code; do not modify it.

R04 reached 27/27 static phases, but 0/104 connections. The orchestrator's diagnosis:
- The planner budget was tiny: 8–10 s per edge, 100 nodes. 100 of 151 edges ended as "budget exhausted".
- The interval certificate was over-conservative (a 2 m/rad bound).
- The endpoint-only own-support rule made lifting impossible: 49 edges failed with "endpoint outside transit free space".

DECISIONS.md (2026-10-08, "Contact windows and path checking") now fixes all three. Apply it exactly.

1. **Re-verify the statics.** Apply the restricted wall-mount rule (only the named bracket mating faces may touch the wall) and confirm that the 27 phases still hold.
2. **Model the meal state sequence.** Build every grasp, release, jaw event, lift/approach window, tool pick/return, appliance load, pusher action, bowl move, lid and brush step. Insert staging/via poses wherever useful (pose changes are allowed; rule changes are not).
3. **Plan every internal path and every inter-stroke connection:**
   - RRT-Connect or BiT*-style planning over the arm joints plus carriages, at least 60 s per connection with restarts, then shortcut smoothing;
   - discrete checking at the ≤4 mm point-displacement step;
   - two-arm simultaneity where the schedule overlaps.

   Use up to 4 worker processes, in foreground chunks under 20 minutes; run as many chunks as needed. Report connections passed/total and, for each failure, the blocker pair and what you tried.
4. **Idle kitchen.** All upper-cabinet doors must open, and a person must have a clear front corridor at the counter while the robot is parked. Arms go to the rail ends beyond the cabinet doors or into a recess. Change rail extents or park poses as needed and report any extra wall length.
5. **Schedule and cost.** Produce an executed-path-based timeline: path durations from joint/carriage speed limits under home-tier speeds, plus process times, soaking and draining. Show overlap between the two arms. Update cost and keep a cheapest variant if it still passes.
6. **Renders.** An overview, parked with the doors open, and a frame strip (about 24 frames) of the full meal.

Deliver results/phase_summary.json, results/motion.json (per-connection status, planner time, path length and blockers), results/schedule.json, results/idle.json, results/costs.csv, results/iterations.csv, renders and robot_rail/posts/r05/integrator.md.
Final reply: `DONE integrator phases=<p>/<t> internal=<i>/<n> connections=<c>/<m> idle=<pass|fail> prep_min=<v> cost_cny=<v>`.
