SCOPE: R09, design and verify the tethered mobile cart; the carrot runs end to end first, then the other three (robot_rail/sim/r09/integrator/).

Work plan:
1. **Hardware selection**, with public sources and China prices:
   - cart drive and wheels;
   - mount height: fixed, or a short-stroke lift only if needed (stroke, load, moment, brake);
   - cobot arm (payload envelope, reach, mass);
   - EOAT/gripper;
   - cable reel (retraction, current rating);
   - ballast.

   Give the total mass and footprint. Compare 2–3 combinations and pick one; prefer cheaper arms when the envelope allows.
2. **Clean package** in sim/r09/integrator. Start from the R08 package: scene builder, checker adapter, solver, planner and state module. Fix R08 findings 2 and 3, and add (the column axis only if a lift is used):
   - floating base pose sampling with freezing;
   - the column axis, if a lift is used;
   - tip-over margin evaluation;
   - cart floor-path planning with the cable envelope.
3. **Reachability maps** from the aisle (base x/y/yaw, plus mount height as a design variable) over the counter, sink and stations. Place the stations and bowls for clearance and few base moves.
4. **Carrot first.**
   - Steps: load → wash → peel → mandoline slices → output bowl, plus scrap; then park.
   - Solve every stroke (≥96 starts), plan every connection and base move, and check tip-over everywhere.
   - Iterate until the full carrot sequence executes as one connected, checked, conserved sequence.
5. **Then potato, bok choy and tomato.** Then the full meal and idle parking (fold, lower if a lift exists, drive to park; doors and walkway clear).
6. **Robustness pass**, plus a schedule (executed paths at home-tier speeds, station times, soak, drain), cost (one 15% reserve, one safety package) and power (arm, any lift, drive, appliances; reel rating).
7. **Renders** (≤1600 px): an overview of the cart at the counter, parked, the main stations, and a frame strip of about 24 frames from the executed carrot sequence, labelled honestly.

Keep results/iterations.csv.

**Do not deliver before** either:
- (a) the full carrot sequence including parking executes as one connected, checked sequence, with tip-over passing; or
- (b) at least 8 documented iterations with evidence show what blocks, with structural causes named.

Deliver results/hardware.json, results/phase_summary.json, results/motion.json, results/state_sequence.json, results/stability.json, results/idle.json, results/schedule.json, results/costs.csv, results/clearance.json, results/iterations.csv, renders and robot_rail/posts/r09/integrator.md.
Final reply: `DONE integrator carrot=<pass|fail> products=<n>/4 strokes=<p>/<t> connections=<c>/<m> idle=<pass|fail> min_tip_margin=<v> prep_min=<v> cost_cny=<v>`.
