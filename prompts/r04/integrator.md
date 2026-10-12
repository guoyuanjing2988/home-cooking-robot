SCOPE: R04, close the connected meal and cut cost and time (robot_rail/sim/r04/integrator/). Start from R03 (sim/r03/integrator, posts/r03/integrator.md and posts/r03/reviewer.md). Copy the R03 code; do not modify it.

Targets, in priority order:
1. **Close the connected meal.**
   - Model one persistent state sequence for the reference meal: food ownership, jaw open/close, supports and clamps, tools, bowls, lids, brush, the appliance pusher.
   - Plan collision-checked paths between consecutive verified poses, including carriage moves, using a real planner (for example RRT-Connect or a lazy PRM in joint+carriage space, with MuJoCo distance checks at the same gaps and an interpolation resolution you justify).
   - Fix the failed washing, delivery and wiping strokes by changing geometry or poses only.
   - Fix the R03 reviewer's distance-evidence issue (findings 4 and 8): no "absent contact = ≥20 mm" assumption; add the UR5e base collision geometry.
2. **Idle kitchen.** Parked state with **all upper-cabinet doors openable** and the counter usable by a person: arms fold to the rail ends or into a recess; the appliances may stay.
3. **Cost-down**, without loosening any rule:
   - Compare cheaper arms that have public specs and models (for example JAKA Zu5/Zu7, Elite CS63/CS66, Dobot CR5, AUBO i5, xArm6), using the rated-payload envelope.
   - Check whether a **household** guarded slicer meets the cut specs instead of the ¥18k Robot-Coupe.
   - Check whether a wall-anchored rail can replace the 160 kg portal where the wall allows, keeping the portal as the weak-wall fallback.
   
   Report the cheapest configuration that passes, next to the best-performing one.
4. **Time.** Overlap the two arms' work: wash on one side while the other cuts. Report the scheduled prep time for the reference meal, including soaking, draining and cleaning. Target 45 min or less if feasible.

Keep the R03 rules exactly: the unchanged reference acceptance, the intended-contact policy and DECISIONS.md. Report phases, strokes, internal paths and inter-stroke connections separately. Keep results/iterations.csv.

Deliver results/best.json, results/cheapest.json, results/phase_summary.json, results/motion.json, results/schedule.json, results/costs.csv, renders (overview, parked with doors open, passing, main phases, and a short frame sequence of the full meal) and robot_rail/posts/r04/integrator.md.
Final reply: `DONE integrator phases=<p>/<t> connections=<c>/<n> motion=<pass|fail> cheapest_cny=<v> best_cny=<v> prep_min=<v>`.
