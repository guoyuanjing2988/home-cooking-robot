SCOPE: market and hardware research (robot_rail/sim/r01/market/). Web search is allowed.

1. **Precedents.** Rail/gantry kitchen robots and food-prep cells: Moley, Samsung Bot Chef, Miso Flippy, Dexai Alfred, Chef Robotics, Chinese examples, and others. For each: arm type and count, mounting, rail, payload, what tasks it really does, price if public, what failed or was dropped.
2. **Arm catalogue (≥10 arms).** For each: DOF, reach, rated payload, mass, mounting orientations allowed, joint brakes, collaborative/safety rating (ISO 10218 / TS 15066, force sensing), IP rating / washdown, controller size, power, **price in China (CNY)** from public listings, and whether a MuJoCo/URDF model exists (link). Short-list the 3–4 best for a kitchen wall rail.
3. **Rails.** Wall-mounted linear axes / 7th-axis tracks that carry one or more independent carriages (HepcoMotion, Bosch Rexroth, Igus drylin, Chinese belt modules, magnetic multi-mover systems), corner options, braked drives, covers for splash/grease, cable carriers. Sourced price per metre and per carriage.
4. **Wall mounting.** Anchor loads for a carriage with an arm at full reach with 3 kg (+ tool), dynamic factor 1.5; anchors for brick/concrete vs lightweight block; alternative freestanding frame behind the counter.
5. **Grippers and tools.** Electric grippers / tool changers suitable for food (and the tool handles from the task inputs), with prices.
6. **Cost table.** Installed cost for 2 arms and for 3 arms on a 2.4 m back-wall rail: arms, carriages, rail, gripper/tool changer, safety sensors, controller/electronics, installation. Compare with an R1 Pro (~CNY 470k).

Deliver results/catalog.csv, results/costs.json and robot_rail/posts/r01/market.md.
Final reply: `DONE market shortlist=<arm1,arm2,...> cost2_cny=<value> cost3_cny=<value>`.
