SCOPE: multi-rail transport system (robot_rail/sim/r02/transport/).

1. **Options.** Survey and size, with sources and China prices:
   - **(a) Passing rails.** Two or three parallel rails at different heights or stand-offs. Each carriage stays on its own rail, but arms pass each other.
   - **(b) Track switches and transfer shuttles.** Examples: HepcoMotion track systems, B&R ACOPOStrak diverters, Rockwell MagneMotion/iTRAK, Beckhoff XTS/XPlanar, Festo, and Chinese magnetic linear transport makers.
   - **(c) Planar or vertical-wall movers.**
   - **(d) Simple alternatives:** a 2-axis wall-mounted XY/XZ carriage, or a rail plus a vertical slide.
   
   For each option, state:
   - the carriage payload and moment capacity, against a cobot of 15–25 kg with 3 kg at full reach and a dynamic factor of 1.5;
   - stop accuracy and stiffness;
   - braking on power loss;
   - power and data to a moving arm (conductor rail such as Vahle; inductive; wireless/EtherCAT-over-busbar);
   - splash, grease and cleanability;
   - noise;
   - mounting on a typical Chinese kitchen back wall, plus the free-standing frame option;
   - cost for a 2.4 m run with 2, 3 and 4 carriages.
2. **Rank the options** by simplicity, reliability, safety, cost and freedom of movement. Recommend one or two, and say plainly if "free shuttling" is not worth its cost versus passing rails.
3. **Geometry for the sim team.** For the recommended options, give a parametric description: rail positions, carriage envelopes, minimum passing clearances, switch locations and travel limits. Write it as results/transport_options.json, so a MuJoCo model can be built from it.
4. **Diagrams/renders** of the top two options installed in the galley kitchen (≤1600 px).

Deliver results/transport_options.json, results/costs.csv and robot_rail/posts/r02/transport.md.
Final reply: `DONE transport recommended=<option> cost_3arm_cny=<value> power=<method>`.
