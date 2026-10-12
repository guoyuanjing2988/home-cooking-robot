SCOPE: appliances, containers and process concepts for the workstation (robot_rail/sim/r06/stations/). This is research and design; no motion simulation yet.

1. **Product requirements.** Restate each product's finished specs from cook_ref in a table: carrot, potato, bok choy, tomato.
2. **Appliance and fixture survey, with China prices and real dimensions.** For each step, find buyable household or small-commercial devices with public specs:
   - **wash:** produce washers, spray/brush washers, basket rinsers;
   - **peel:** abrasive-roller potato/carrot peelers, small household electric peelers;
   - **eyes/core:** tools and methods;
   - **slice 5 mm:** guarded electric slicers/dicers with feed chutes;
   - **bok choy:** root trim, split, 40 mm sections;
   - **tomato:** eight wedges;
   - **drain/spin.**

   For each device, record:
   - dimensions and loading geometry (hopper/chute shape and size, lid, controls);
   - power;
   - capacity and cycle time;
   - cleanability;
   - whether a robot can operate it: buttons, lids, pushers, interlocks, and whether it can be powered and controlled by a relay or smart plug;
   - how well it meets the cut/peel specs, from product data, independent reviews or papers;
   - where the evidence is weak.

   Also give custom alternatives where no device fits, such as a guillotine bok-choy sectioner or a wedger with a robot pusher.
3. **Containers.** Choose a standardized basket/pan/cassette system that fits the devices, is food-safe and is robot-graspable: handles, keying, stackability, drainage.
4. **Process concepts.** Give 2–3 complete concepts for the module. For each:
   - the station layout (plan drawing with dimensions, within about 1.2–1.5 m × 0.6–0.75 m footprint, height ≤ 2.0 m);
   - the number of arms and their mounting (fixed, or on a short rail);
   - the event list for the reference meal: target ≤ 80 events; count them;
   - the forces arms must apply (sourced);
   - the expected time (appliances run in parallel; target ≤ 45 min);
   - the BOM and cost under the home tier (one safety package: enclosure/door interlock, E-stop, RCD and so on);
   - the risks.

   Recommend one.
5. **Interface spec for the integrator.** Write results/stations.json with geometry primitives (boxes and cylinders with poses), masses, grasp handles, support faces, approach axes, appliance openings, intended contacts and force vectors. It must be complete enough to build the MuJoCo scene directly.

Deliver results/survey.csv, results/stations.json, results/concepts.json, plan drawings (≤1600 px) and robot_rail/posts/r06/stations.md.
Final reply: `DONE stations recommended=<concept> arms=<n> events=<n> est_min=<v> est_cny=<v>`.
