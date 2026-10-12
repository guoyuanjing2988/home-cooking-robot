SCOPE: integrate one consistent kitchen robot cell and make it pass (robot_rail/sim/r03/integrator/).

1. **Simplify the process first.** Prefer guarded **commodity** appliances where they meet the finished-product specs, especially a rotary-disc electric slicer with a feed chute and direct bowl output. The R02 reviewer found the custom slow press unjustified. Keep the R02 peeling/washing ideas that are sound. Fewer grasps, regrasps and tool changes is better. Write the process as process_v3.json (phases, strokes, tools, sourced forces, intended contacts) and justify it against R02's Q01–Q27 and the old P01–P16. No finished product may be dropped.
2. **Robot.**
   - Start from the R02 reviewer's best: two independent fixed lanes, an xArm6 on each, cable chains, mains.
   - You may change rail heights/stand-offs, mount angles, the arm model (keep only arms with public specs and a model; record the source) and the helper size, if it helps.
   - Model every installed part as a robot or environment part: rails, chains, covers, power track, appliances, guards.
3. **Layout.**
   - Place every station, appliance, support, bowl and faucet so that the arms reach it **with clearance**. Use the T08 counter, its free slabs and the protected stove; do not invent counter space.
   - Wash poses must sit beside or under the spout without touching it.
   - Supports must have approach directions the gripper can use.
4. **Iterate.** Run the phases, read the blocker pairs, fix the geometry or the poses (never the rules), and re-run. Keep an iteration log (results/iterations.csv) with the main blocker of each iteration.
5. **Final check.** For the final design:
   - every phase/stroke with ≥96 seeds or solver starts;
   - verified witnesses per stroke, with min clearance, torque ratios (envelope, and rated where published) and grip margins;
   - the golden mandoline check, if a mandoline is still used;
   - a **connected-motion check** of the full reference-meal sequence: collision-checked paths between consecutive verified poses, including carriage moves, arms passing each other, tool pick/return and parking.
6. **Deliverables.**
   - Loads on rails and anchors.
   - Power budget.
   - A prep timeline that includes soaking, draining and cleaning.
   - Cost under the home safety tier: one inclusive home-safety package and no duplicated allowances.
   - Renders (≤1600 px): an overview, each main phase and passing.

Deliver results/process_v3.json, results/best.json, results/phase_summary.json, results/motion.json, results/iterations.csv, results/costs.csv, renders and robot_rail/posts/r03/integrator.md.
Final reply: `DONE integrator phases=<passed>/<total> motion=<pass|fail> arms=<desc> cost_cny=<value> prep_min=<value>`.
