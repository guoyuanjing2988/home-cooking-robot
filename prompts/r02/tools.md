SCOPE: robot-friendly kitchenware, tools and prep process (robot_rail/sim/r02/tools/).

1. **Products and process requirements.** For each product (carrot, potato, leafy greens, tomato), list the required end state from inputs/cook_ref.md: washed or peeled, cut shape and size, and quality. List what the old process P01–P16 did.
2. **Brainstorm widely, then choose.** For every step (wash, peel, cut, hold, transfer, dispose of peel, deliver output), compare:
   - **buy:** robot-friendly products already on the market, such as commercial and household electric dicers or slicers, peeler machines, vegetable washers, salad spinners, fixtures and grippers with food-safe fingers, and tool changers;
   - **adapt:** a commercial tool with a custom robot handle or interface;
   - **build:** custom fixtures, containers, tools or small powered devices. These can be 3D printed in food-safe material or made from stainless or POM.

   Score each option on finished-product quality, robot difficulty (forces, precision, number of grasps and regrasps), safety (exposed blades), cleanability, cost and noise. Use real product data and prices (China).
3. **Recommended prep process.** Define the new phase list (Q01…Qn). For each phase give:
   - the arm(s) needed: which arm and helper;
   - the tool;
   - the poses and paths (sites in a frame anchored to the counter);
   - the **sourced process forces with margin**: cutting/peeling literature, appliance specs, own physics. Never fabricate a number to pass.
   - the expected outcome.

   Justify it against the old P01–P16 and the finished-product list. Write results/process_v2.json in a form the sim team can turn into checker phases: tool geometry primitives, masses, work sites, force vectors, intended contacts and counter layout.
4. **Counter layout.** Place the appliances, fixtures and containers within the T08 counter: free slabs x −1.80…−0.70 and −0.11…0.69 m, y 0…0.60 m. The sink is at its existing position and the stove zone is protected. Show which tools need power. Give a bill of materials with costs.
5. **CAD.** Model the custom parts in FreeCAD, at least as solid models and STEP: tool handles and the tool-changer interface, fixtures, and any custom device. Note the printing and food-safety materials. Render the layout (≤1600 px).

Deliver results/process_v2.json, results/tools_bom.csv, cad/, renders and robot_rail/posts/r02/tools.md.
Final reply: `DONE tools phases=<n> powered_appliances=<n> custom_parts=<n> bom_cny=<value>`.
