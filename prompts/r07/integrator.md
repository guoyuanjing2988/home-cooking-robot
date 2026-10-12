SCOPE: R07, the in-kitchen under-cabinet rail with folding park, connected meal (robot_rail/sim/r07/integrator/).

1. **Remove the R05 additions:** storage elevator, pallet, wall extension, portal header and front legs. Keep the original kitchen: wall, counter, sink/faucet, stove exclusion and upper cabinets.
2. **Rails.**
   - Mount the rail(s) on the back wall, under the cabinets, entirely behind the cabinet front plane, below the cabinet bottom, with ≥10 mm gaps.
   - Use one rail, or two stacked lanes, so that the arms can pass. State which, and why.
   - Model the cable chains in the same band.
3. **Arms.** Choose arms whose **folded** envelope fits the under-cabinet band (about 0.37 m deep × 0.50 m tall, minus gaps) and that still reach the counter front, the sink and the appliances. Compare at least a 5 kg-class principal arm (UR5e, xArm6, JAKA Zu5, Elite CS66, Dobot CR5, AUBO i5, as models allow) with smaller helper options. Use the rated-payload envelope.
4. **Appliances.** The full Robot-Coupe R211 is 510 mm tall and protrudes above the 1.35 m cabinet bottom. Either:
   - place appliances where no cabinet is above them;
   - choose a lower guarded slicer with public data (see R05's research.py household candidates);
   - or justify an alternative.
   
   Appliances may stay on the counter when idle; report which counter area stays free for a person.
5. **Parking.** Find folded park poses and the fold/unfold **paths** from the working poses that satisfy the corrected idle check.
6. **Statics.** Re-verify every stroke under the new geometry.
7. **Full meal.** One persistent, conserved state sequence; plan every internal path and every connection under the DECISIONS.md rules and budget. **Reduce the event count where possible**: R05 had about 600 event paths. Fewer regrasps, containers carried between stations, and simpler tool handling are allowed if the finished products are kept. Keep results/iterations.csv.
8. **Timeline and cost.** An executed-path-based timeline (home-tier speeds, appliance times, soaking, draining) and the cost (one 15% reserve, one safety package). Report the clearance reserve distribution above the gates.
9. **Renders** (≤1600 px): an overview; parked with all doors open; the under-cabinet band close-up; passing; a frame strip of about 24 frames from executed paths, honestly labelled.

Deliver results/phase_summary.json, results/motion.json, results/idle.json, results/schedule.json, results/costs.csv, results/clearance.json, results/iterations.csv, renders and robot_rail/posts/r07/integrator.md.
Final reply: `DONE integrator strokes=<p>/<t> connections=<c>/<m> meal=<pass|fail> idle=<pass|fail> prep_min=<v> cost_cny=<v>`.
