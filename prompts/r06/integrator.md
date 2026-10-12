SCOPE: build and verify the workstation in simulation (robot_rail/sim/r06/integrator/). You own all geometry.

Inputs: posts/r06/stations.md and sim/r06/stations/results/*.json (the recommended concept). Reuse sim/r04/integrator and sim/r05/integrator code: the reference checker, planner, motion checks and rated-payload envelope. Copy them; do not modify them.

1. **Build the module scene** from stations.json: frame, worktop, basin, appliances, containers, input tray, output port, waste bin, enclosure/door, rails and arms (real arm models). You may adjust the layout and the arm choice/mounting to improve reach and clearance. Record each change and its reason, and keep the footprint within about 1.2–1.5 m × 0.75 m.
2. **Statics.** Verify every stroke with ≥96 solver starts. Report witnesses, torque ratios, grip margins and the **clearance reserve** distribution above the gates.
3. **Full meal.** Build one persistent state sequence: every event, jaw, container, lid, appliance state and food ownership. Plan every internal path and every connection under the DECISIONS.md path rules and budget. If two arms are used, check the overlaps simultaneously.
4. **Iterate.** For each failure, fix the layout or the poses (not the rules) and re-run. Keep results/iterations.csv.
5. **Timeline and cost.** Build an executed-path timeline: path durations at home-tier speeds, appliance cycle times and parallelism, soaking and draining. Report the prep time for the reference meal and the cost (one 15% reserve, one safety package).
6. **Renders** (≤1600 px): an overview, the door open for loading/unloading, each main station, and a frame strip of about 24 frames from the executed meal. Label the frames honestly.

Deliver results/phase_summary.json, results/motion.json, results/schedule.json, results/costs.csv, results/iterations.csv, results/clearance.json, renders and robot_rail/posts/r06/integrator.md.
Final reply: `DONE integrator strokes=<p>/<t> connections=<c>/<m> meal=<pass|fail> prep_min=<v> cost_cny=<v> min_reserve_mm=<v>`.
