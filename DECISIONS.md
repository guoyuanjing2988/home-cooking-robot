# User decisions (binding for all rounds)

- 2026-10-07 **Architecture.** Rail-mounted robot arms only: no torso, no mobile base, no battery, no humanoid arm. Back wall above the counter. Several parallel rails are allowed, and any number of arms.
- 2026-10-07 **Kitchenware.** It may be bought, adapted or custom-built, including powered appliances. Think openly.
- 2026-10-07 **Appliance power.** Use a household power track (轨道插座) in a dry position. Arm power follows the transport study: cable chains unless the arms change lanes.
- 2026-10-07 **Safety tier: home use, sized to actual use.** The user said "按实际使用来". This replaces the industrial-cell practice used in R01.
  - Standards basis: household and personal-robot practice (IEC 60335-1 style appliance safety, ISO 13482 personal care robots), not ISO 10218 production cells.
  - Primary protection:
    - collaborative arms with built-in power-and-force limiting and collision detection;
    - speed limits;
    - low-cost person-presence sensing (mmWave/ToF/camera) that slows or pauses the robot;
    - an E-stop on the unit;
    - RCD and PE;
    - de-energize-to-apply brakes on rail drives and gravity-loaded arm axes.
  - Blades are the main hazard: guarded cutting appliances with lid/door interlocks; no exposed powered blade while a person can reach in.
  - Industrial safety laser scanners, light curtains and safety PLCs are **not required**. Use them only where a specific hazard cannot be handled otherwise, with the reason stated.
  - Target safety budget on the order of CNY 10–20k, not ~110k.
- 2026-10-08 **Arm capability evidence (orchestrator decision under the user's "按实际使用来，你定").** Most cobot makers do not publish continuous joint-output torque, and R01/R02 were blocked on that alone. From R03 an arm's joint capability is the **rated-payload envelope**: for each joint, the largest static torque the same model needs to hold the manufacturer's rated payload, at the manufacturer's allowed payload CoM offset, over the reachable workspace in the actual mounting orientation. A phase passes torque if every joint's demand (gravity + held mass + process wrench) is ≤ that envelope. A published rated output torque, where one exists, may be used instead. Report both ratios when available.
- 2026-10-08 **Brakes (home tier).** For arm joints, the manufacturer's documented power-loss holding in the chosen mounting orientation is sufficient. Rail and vertical drives need a de-energize-to-apply brake.
- 2026-10-08 **Contact windows and path checking (orchestrator decision; this fixes a rule bug of mine in R03/R04).** "Intended contact only at grasp/release endpoints" made it literally impossible to lift an object off its support.
  - **Lift/approach window.** During a straight approach or retreat of ≤50 mm along the support's face normal (or the declared insertion axis), the specific intended contacts of that grasp/release stay allowed until the 5 mm gap is reached. The same applies to food↔work-tool contact along a working stroke. Nothing else gets a window.
  - **Wall mounts.** Only the named mating faces of rail wall brackets may touch the wall. Every other part, including connectors and covers, keeps the full gap.
  - **Path checking.** Standard practice is discrete checking with a bounded step: check consecutive states so that no robot or held-object point moves more than 4 mm between them, using a valid displacement bound. Every checked state must meet the normal gaps (10 mm / 5 mm). An exact continuous certificate is welcome but not required.
  - **Budget.** Planners get a real compute budget: ≥60 s per connection, with restarts, shortcutting and via/staging poses.
- 2026-10-08 **Dedicated robot prep workstation (user decision after R05). This supersedes the 2026-10-07 "back wall above the counter" placement.**
  - **Why:** R01–R05 retrofitted arms into a human galley kitchen (upper-cabinet doors, faucet, person corridor). Every fix made the system bigger, and the full meal never connected (0/156).
  - **The robot gets its own module**, a stand-alone prep station roughly 1.2–1.5 m wide, placed in or next to the kitchen:
    - its own worktop, frame, rails and arms;
    - its own sink or wash basin, with household water supply and drain hookups like a dishwasher;
    - no upper cabinets or other human furniture inside its workspace;
    - the person is not inside the workspace while it runs.
  - **Human interface:**
    - raw, unwashed produce goes into an input tray or bin;
    - finished produce is taken out of output bowls at a port or drawer;
    - waste (peel, roots, cores) goes to a removable bin.
  - **Simplest reliable process:**
    - Prefer commodity appliances, household or small commercial: produce washers, peelers, guarded slicers/dicers, wedgers, spinners.
    - Custom fixtures are allowed.
    - Arms mostly transfer standardized containers (baskets, GN pans, cassettes) between stations. Keep regrasps and events few.
  - **Safety:** a simple enclosure or guard with an interlocked access door is the natural home-tier safety for this module. The other home-tier items still apply.
  - **Kept unchanged:**
    - rails and arm choices are free, any number including one;
    - finished-product specs;
    - contact, IK and grip rules, contact windows, path checking;
    - sourced forces;
    - no purchasing.
  - **Physical bench tests:** not now (user, 2026-10-08).
- 2026-10-08 (later) **Both concepts run in parallel and are compared (user decision).** The orchestrator had overstated the parking problem. R05's idle failure came from a mis-specified check: the open cabinet **doors themselves** entered the declared human corridor. The R02–R05 portal frame stood in front of the cabinets because the second passing lane sat further from the wall.
  - **R06:** the dedicated workstation (entry above).
  - **R07:** the in-kitchen rail, corrected. The back-wall placement is valid again for R07:
    - Rails sit **under the upper cabinets, behind the cabinet front plane**, wall-anchored. No portal, header or front legs.
    - Use one rail, or two stacked lanes that are both behind the front plane.
    - Arms **fold to park** behind the cabinet front plane and below the cabinet bottom.
  - **Corrected idle check:**
    - every robot part (arms, carriages, rails, chains, covers) keeps ≥10 mm clear of each upper-cabinet door's full opening sweep;
    - robot parts stay out of the front counter strip (counter edge to cabinet front plane, up to the cabinet-bottom height) and out of the standing corridor in front of the counter;
    - the doors themselves are **not** checked against the corridor.
  - No elevator, pallet or wall extension.
- 2026-10-08 **The faucet may be replaced (user: "水龙头可以换的，这个简单").** The R07 reachability work showed that the tall rear-centre faucet sits in the rail/carriage line under the cabinets. For the in-kitchen rail concept:
  - Choose a real, buyable replacement with public dimensions, typically CNY 200–1500. Options: a low-profile faucet, a pull-out/pull-down sprayer, a faucet mounted at the side or rear corner of the sink, or a wall-mounted one below the rail band.
  - Water on/off may be electric: a solenoid valve or a sensor faucet. That way the robot does not have to turn knobs.
  - The arm may use a pull-out spray head as a washing tool, if that is simpler.
  - The sink itself stays.
- 2026-10-08 (night) **Continue R07 with all four vegetables; R06 workstation is paused (user: "做r07吧，菜都要").** The concept is the under-cabinet rail in the existing kitchen, with the faucet replaceable. Scope stays carrot, potato, bok choy and tomato, with the full finished-product specs. To help convergence, prefer commodity appliances with public data, so that the arms mostly load, unload and transfer; fewer strokes is better if every product is still made.
- 2026-10-09 **Appliance-internal food transformation may be abstracted (orchestrator decision under "按实际使用来，你定").** In R07d, all 110 meal connections were "BLOCKED_PERSISTENT_BINDING_OR_INTERVENING_EVENTS" and the planner never ran: the chain waited for exact piece-level geometry of washing/peeling/cutting inside appliances. That is not a robot-feasibility question, and the simulation cannot judge cut quality anyway.
  - **Inside an appliance or station**, a transformation (whole → washed / peeled / slices + scrap) is a **declared state change**. It conserves mass. The outputs become **bulk proxies** sized from mass, density and packing:
    - a bed of slices in the output container;
    - scrap in the bin or scrap tray.
    
    Each change has a duration taken from appliance data.
  - **Everything the robot touches keeps full geometry and all rules:** containers, the held food going in, appliance lids, doors and pushers.
  - The **planner must actually run every connection** between consecutive robot strokes in the sequence, using the DECISIONS.md budget. Record the reason when a connection fails.
  - Finished-product quality stays a declared assumption, to be settled by later physical tests.
- 2026-10-09 **Door-sweep scope (orchestrator clarification; fixes my over-broad idle wording).**
  - **When it applies.** The ≥10 mm clearance to each upper-cabinet door's full opening sweep is an **idle/parked-state** requirement: a person can open any door while the robot is parked.
  - **During operation and while folding or unfolding**, the doors are **closed**. The closed door leaves and the cabinet bodies are obstacles with the normal gaps.
  - **The open-sweep volumes are not obstacles in motion.** A home-tier presence sensor, and/or a door-open sensor, pauses the robot if a person approaches or opens a door during operation. Model that sensor as part of the safety package.
  - Front-strip and corridor rules for the parked state are unchanged.
- 2026-10-09 **R09: a tethered small-range mobile machine (user: "或者再试试别的方案，例如一个拖着电源线小范围可以挪动的机器").**
  - **Why:** after R07/R08 the under-cabinet band proved too tight for a 5 kg-class arm; failures were persistently at sub-mm margins.
  - **The new concept:**
    - a floor cart that moves along the counter within a small range;
    - **mains power through a cable**: a retractable reel, overhead or wall-mounted, or a floor cable guide; **no battery**;
    - a fixed mount height, or a short-stroke lift only if needed (user, same day: "升降其实没有那么长的需求，毕竟只考虑台面工作先");
    - one buyable cobot arm, a second arm optional.
  - It works from the aisle in front of the counter, like a person. During each stroke the base pose is sampled and **frozen**, as in the original T08 checker.
  - **When idle** it parks out of the way: at the end of the counter or in a corner, not blocking the walkway or the doors. Cabinet doors only need clearance when the machine is parked.
  - The rail concepts (R07/R08) stay as history. The kitchen dimensions are the standard estimates in inputs/user_kitchen/estimate.md; the gap between cabinet tops and the ceiling is unknown (user: "按常见情况假设").
- 2026-10-09 **Tools are fetched and put away, not left on the counter (user: "工具从柜子里取和放回去...又不是工具只能都放在台面上...除非特别重的或者利用率特别高的").**
  - **What is stored:** light tools and stations (mandoline, peeler cradle, wedger, guillotine, bowls, baskets; each within the arm's payload with its keyed handle) live in storage.
  - **Storage type:** preferably a drawer or a push-to-open shelf/cabinet the robot can operate without twisting handles.
  - **Use:** the robot sets out only what the current step needs on a free work spot, and puts it back afterwards.
  - **What stays out:** only heavy or very frequently used items stay on the counter permanently, for example the sink/faucet and any heavy powered appliance.
  - **Idle state:** the counter is clear.
  - **Simulation consequence:** station positions are per-step work spots; fetch/return strokes become part of the sequence.
- 2026-10-09 **Market-first per function (user: "对于各个功能，除了优化自己动作，也多去市场看看各种现有产品能不能更好适配机器人").** For every prep function, survey existing products (household, small-commercial, canteen) before designing a robot motion or a custom fixture.
  - **Preferred interfaces:** robot-friendly ones, such as an open hopper or chute, output straight into a bin or bowl, on/off controllable by a relay or smart plug, safe interlocks.
  - **Arm's role:** prefer that the appliance does the precise work, while the arm loads, unloads and transfers.
  - **Tall top-feed appliances:** in the cart concept they are acceptable if their chute sits in the open front counter strip (no cabinet above).
- 2026-10-09 **Domestic market first, 3D printing for simple bodies (user: "多去淘宝京东找，别在国外找，这个简单的机身也可以多利用3D打印机"; "切番茄怎么可能是单独一个机器呢").**
  - **Sourcing:** source appliances on 淘宝 / 京东 / 天猫 / 拼多多 with domestic prices.
  - **Multi-function cutters:** prefer one base with interchangeable blade sets, or a 切肉切菜 type of cutter, over single-purpose machines. No dedicated machine for one product such as tomato.
  - **3D printing:** simple bodies, guides, chute adapters, holders, docks, jigs and gripper finger pads may be 3D printed (PETG/PP, or food-safe resin where food touches).
  - The electric slicer may stay on the counter.
- 2026-10-10 **R11: the robot uses the tool set found in the market research (user: "我意思robot本身，用我们新的这些找到的工具").** Source: research/market_r10.md §13.3, §13.7, §13.8.
  - **Root slicing, shredding and dicing:** an electric 切片/丝/丁 machine with a top chute (卓晋 3-in-1, 10×7 cm chute, lid interlock; fallback HLC-300). It stays on the counter.
  - **Greens sections:** the same fetched lever cutter base as for tomato (below), with a 3D-printed 35–40 mm section plate and bought steel strip blades.
    - **Not the conveyor-belt cutter:** a belt cutter (切葱花机 class, about 28×26×38 cm, 8.7 kg, 1.5–35 mm) needs about 46 cm of permanent counter. That does not fit: the sim counter between sink and stove is 78 cm and the slicer with its bowl uses 50 cm, and the user's sink-leg free counter is estimated at about 95 cm.
    - **When the belt cutter returns as an option:** only if the user frees counter space (for example the microwave/blender corner).
  - **Tomato wedges and dice:** a lever cutter base with interchangeable plates (AY-403 class, 2.35 kg), fetched from storage. The robot places the tomato on the plate and pulls the lever.
    - **Lever force:** no sourced cutting force for tomato wedging or greens sectioning has been found yet. Never invent one.
    - **What the sim reports instead:** the arm's available handle force at the press poses (from the mounting torque envelope).
    - **Still to verify by a measurement later:** that this force times the lever ratio exceeds the real cutting force.
  - **Peeling:** a fetched peeler station. The physical peeler (傲宏 85 W class or the current open cradle) is still open; keep the abstracted peel transformation.
  - **Washing:** sink, plus a fetched spinner or basket.
  - **Gripper:** 3D-printed finger pads for 30–80 mm produce on the 50 mm-stroke gripper.
  - **Not in R11 scope yet:** meat (850 W 切肉机 class, about 21 kg, counter-resident if adopted), and mince (绞切杯).
  - **Approach:** appliances do the precise cutting; the arm only loads, pushes, operates a lever, or lays produce on a belt. Appliance internals are abstracted as contained, mass-conserving state changes (as decided for R07).
- 2026-10-10 **Sim modelling fix: tool-side boxes become box meshes (R11, `mesh_tool`).** The geometry is unchanged.
  - **Measured problem:** in the MuJoCo 3.2.5 used here, box-vs-box distances inside the contact margin come out at 0.500× the true gap. This holds for 60 random orientations, for both `mj_geomDistance` and contact `dist`.
  - **Effect on the binding checks:** along the carrot paths, box-box robot pairs ranged from 0.39× to 1.4×.
    - The checker stayed safe, because the independent exact GJK bound check (`distance.py`) runs on every state.
    - But it falsely rejected paths that had real clearance.
  - **Fix:** box-shaped meshes against boxes measure 1.000×, as do capsule-box pairs (the arm links). So the gripper palm, OEM envelope, fingers and held boxes are now 8-vertex box meshes.
  - **Produce shapes:** tomato and pusher are cylinders (their real shapes).
  - The cart and environment boxes are unchanged.
  - The required gaps are unchanged (10 mm robot↔environment, 5 mm gripper/held↔environment).
- 2026-10-10 **R11 lever-cutter layout (tomato), from simulation evidence.** Presets AV/AW in `sim/r10/claude`.
  - **Grasp:** the pusher knob is gripped from the front, in the same arm posture as placing the tomato. A top-down knob grasp needed a shoulder flip of about 140° and a 66 cm cart move between the two steps.
  - **Placement:** the station sits 35 mm further toward the aisle (blade plate at y = 0.095 m; base plate still inside the counter edge).
  - **Height:** the whole station is 30 mm lower above its base plate, leaving a 78 mm bin. With a 1.18 m knob, the elbow came 9.2–9.9 mm from the closed upper-cabinet doors (10 mm required).
  - **Tomato grip and placement:**
    - gripped 20 mm above its centre with the 3D-printed pads;
    - slid in 6 mm above the plate, then set down;
    - pusher pressed 102 mm, stopping 6 mm above the plate.
  - **Still to verify by measurement:** the required wedging force. The arm can push about 100 N, limited by the keyed grip.
- Scope remains **food prep only** (washing and cutting). Finished-product requirements and the contact, IK and grip rules are unchanged. Process forces must be sourced; never tune a force to pass.
- No purchasing and no supplier contact without asking the user.

## 2026-10-11 — R11 grasp geometry fails the dynamics check; finger pads must be longer
The new rigid-body check (`sim/r10/claude/dyn.py`) uses a free, unwelded item, a 40 N force-mode synchronised PGC-140 and the planned timing.

**Result:** both the closed carrot (AS) and the closed tomato (AW) chains drop the item in the first carry (C1). The causes are geometric:
- Items are centred on the fingertip TCP. The pads protrude only 37.5 mm past the palm, so contact is at the last 2–3 mm.
- The tomato is gripped 20 mm above its centre, where the contact normal is about 30° off horizontal.

**What-if:** with 3D-printed pads 30 mm longer and the item mid-pad (tomato at its equator), both chains hold the item at μ 0.2–0.6. Slip is ≤ 8 mm. The tomato ends on the blade plate and the carrot drops into the chute.

**Decision:**
- Lengthen the printed pads by about 30 mm.
- Grip round items at the equator.
- Re-plan both chains with the new pad geometry. The old AS and AW chains stay geometrically valid but are physically invalid.
- Make the dynamics check a gate for every future chain, alongside the clearance checker.

## 2026-10-11 — R12 finger and hand design: dual-zone 3D-printed fingers on the PGC-140-50
The user asked: "多试试各种可能性，手指手部自己设计设计，3d打印之类的". Six finger designs were compared with 174+ physics runs; the most promising designs were re-planned and every chain re-checked. Evidence: `sim/r10/claude/README_R10.md` (R12), `research/finger_design_inputs.md` and `research/hand_options.md`.

**Correction to the entry above:** with MuJoCo's no-slip solver (exact Coulomb friction), the stock fingers hold at μ ≥ 0.6 and drop at μ 0.3. "Drops at μ 0.6" was a soft-contact creep artefact. The decision to lengthen the fingers stands, because wet friction is unknown, so there is no margin. Grasp checks always run with noslip from now on.

**New constraint:** tomatoes are damaged above about 10 N per finger (Zhou 2022; Zheng 2022). The PGC-140-50 cannot go below 40 N in force mode. No off-the-shelf gripper is both ≤ 10 N and IP67; the low-force ones (OnRobot RG2 3–40 N and others) are IP54 or worse.

**Decision (proposed default, pending the user's comments):**
- **Keep the PGC-140-50**, which is IP67, and fit **dual-zone fingers**:
  - PETG body;
  - rigid rims flush with the pad face at the top and bottom;
  - a sprung soft centre: a TPU 92A or Smooth-Sil 940 skin on a carrier, 2 stainless springs, about 1.5 N/mm, 6 mm travel.
  - Geometry: fingers 75 mm long, the item centre 45 mm in front of the housing, a 20 mm crank, and round items gripped at the equator.
- **Grip modes:**
  - Carrot: force mode, 40 N on the rigid rims.
  - Tomato: position mode, closing 6 mm past contact into the soft centre, about 5 N per finger.
  - Range: carrot ≥ Ø33 mm, tomato ≤ Ø78 mm.
- **Re-planned and verified:** carrot (SD) and tomato (WD) are closed end to end and pass the physics gate. The tomato fails only if its width is overestimated by 2 mm.
- **Next hardware step:** a force sensor in the soft pad (FSR), so the squeeze is closed-loop instead of relying on a width estimate.
- **Fallback hand:** an RG2-class low-force gripper, if the pad sensor or width estimate proves unreliable. Buying it is the user's decision.
- **Rejected options:**
  - V groove / pyramid pocket: the rims cut the open width, leaving 1 mm clearance on a 70 mm tomato.
  - Fin Ray on the PGC: it needs ≥ 10 mm squeeze per jaw, which a 50 mm stroke can't give across 30–80 mm items.
  - Long flat pads alone: 40 N bruises the tomato.


## 2026-10-11 — R13 hand system for every ingredient (accepted by the user: "可以")
The user asked: "你要考虑各种各样的食材哈，都要能工作". The evidence is in `sim/r10/claude/README_R10.md` (R13):
- 702 rigid runs and 53 non-rigid runs in `foodbench.py` and `softbench.py`;
- the catalog in `research/food_catalog_inputs.md`;
- the quick-change research in `research/finger_change_and_food_eoat.md`.

**Finding:** no single grasp works for every food. A 50 mm-stroke parallel gripper with one finger set covers only about 40 mm of item width. Under the binding grip rule (SF 1.5 at wet μ 0.15), friction alone cannot hold the fragile items (tomato, eggplant, bell pepper, strawberry) or the slippery ones (fish, tofu) within their damage limits.

**Proposal:**
- **Gripper.** Keep the PGC-140-50 (IP67).
  - Fit **robot-swappable 3D-printed finger sets**: a dovetail jaw adapter with a spring lock pin, released by a rack ramp (the Schunk BSWS-R pattern).
  - P1–P4 (5–117 mm) cover everything except cabbage and napa cabbage; P5–P7 are for heads.
  - Each pad is the R12 dual zone plus a self-aligning rocking pad, with a finger-root force sensor.
  - Grip force is the highest safe value: ≤ damage limit / 1.4, PGC force mode at ≥ 40 N, otherwise position mode closed on the sensor.
- **Methods by item:**
  - **Pinch:** roots, tubers, onion, apple, corn, egg, chili, mushrooms, meat, banded bunches at the base.
  - **Supported fork (托底叉) from a V-rib slot tray:** the lower finger carries the weight. Tomato, eggplant, zucchini, daikon, pumpkin, peeled yam, fish, fillet, firm tofu, bok choy.
  - **Side-handle basket, poured:** sprouts, shrimp, garlic cloves, green beans, strawberries, cherry tomatoes, peppers, lettuce.
  - **In the box:** silken tofu.
- **What the user sets up:** groceries go into the robot's slot trays and baskets, one item per slot for the fork items. This is a new interface assumption and needs the user's OK.
- **Alternative (the user's decision, no purchase):** a Robotiq Hand-E 100 mm (IP67, 20–185 N) needs only 3 finger sets and holds full-size napa cabbage. On the PGC, napa is limited by the 7 N·m jaw moment to about 1.7 kg heads, or the head must be halved first.
- **Rejected:**
  - Catch lips at the fingertips: they pop round items out sideways.
  - A one-pitch fork for 70–150 mm items: it made round items worse.
  - A bridge handle on the basket: it jammed big and long items.
  - Flex FEM for meat: unstable in MuJoCo 3.2.5; lumped models used instead.
- **Before relying on it:**
  - Measure the wet friction of the pad on real produce (a tilt test). It decides pinch vs fork for about 10 items.
  - Re-plan the kitchen chains for tray picks, fork grasps, finger swaps and basket pours. The bench is a floating gripper only.
  - Check the DH jaw STEP.
  - Most damage limits are estimates.

- **User reply 2026-10-11: "可以".** R13 is accepted, including the interface assumption: the user puts groceries into the robot's slot trays and baskets, one item per slot for the fork items.

## 2026-10-11 — Goal: really cook Wang Gang's recipes; staples, seasonings and the fridge come next
The user said: "最终目标就是按王刚食谱做菜真的能做出来，所以你还要再设计下米面粮油，调料的存取，还有冰箱".
- **The end goal is no longer food prep only.** It is to cook dishes from 美食作家王刚's recipes end to end. This replaces "Scope remains food prep only" above, and cooking itself (heat, wok, timing) is in scope from now on.
- **This round (R14):** storage and retrieval for:
  - staples: rice, flour, grains and oil (米面粮油);
  - seasonings (调料);
  - the fridge.

  Requirements are derived from Wang Gang's recipes, i.e. which seasonings, how much, how precisely and when. Market products come first, then 3D printing (standing rule). No purchasing or supplier contact without asking.

## 2026-10-11 — R14 storage and dispensing design (proposed default, pending the user's comments)
Evidence: `sim/r10/claude/README_R10.md` (R14), `research/wanggang_recipes.md`, `research/r14_storage_market.md`.

**Seasonings.** One station inside the upper cabinet next to the hood.
- **Liquids:** 12 stepper peristaltic channels. Salt, sugar and MSG are dissolved, because powders cake at Singapore humidity.
- **Oil:** pumped up from a 5 L jug in a base cabinet.
- **Powders:** 4 sealed agitated augers.
- **Pastes:** 2 syringe extruders.
- **花椒:** a vibratory feeder.
- **Dosing:** every dose is weighed (0.1 g platform with a stirrer) into robot cups under the cabinet front, at about 1.10–1.15 m where the arm can reach.
- **Rare items:** a weekly kit of cups that the user fills.

**Into the wok.** Robot cups, plus the rotary 4-compartment pour drum for bursts of additions.
- With single cups, 17–25 of 42 recipes have gaps the arm can't make. With the drum, none of the 42 is too tight.
- Physics: granules come out in order, 100 % in the wok.

**Rice, flour, starch, oil.**
- A rice hopper and a flour/starch hopper with metering augers to a weighing platform.
- Rice is washed at the sink and cooked in a remotely startable rice cooker.
- Starch for thickening is a stirred slurry channel; starch for coating comes from an auger.
- Deep-frying is done in a fryer with oil filtering and storage, not in the wok.

**Fridge.**
- **Default:** the user's existing fridge. The arm opens the door with a form-closure grasp on the handle. Physics: seals of 20–140 N open, but above about 100 N the PGC jaw moment is the limit.
- The robot-shelf detail is superseded by the single-door entry below.
- **For high-seal doors:** assisted opening (Bosch/Siemens Door Assistant via Home Connect, Samsung Auto Open Door), or a drawer fridge with OPEX1 installed at counter height.
- **Rejected:** a low under-counter drawer. The docked arm can't reach z 0.45–0.7 m beside or in front of the cart.
- **Staging limit:** raw meat and seafood out ≤ 1 h.

**Waiting on the user:**
- whether to buy anything (prices still unconfirmed).

**Next round:** cooking itself (stir, heat and off-heat, oil pour-out, edge pours, vision-gated 勾芡).

## 2026-10-11 — R14 fridge: single-door, door-bin cold box (proposed; size and placement estimated)
The user said: "单开门的，不过这个相对来说简单点，你估算下". Evidence: `sim/r10/claude/README_R10.md` (R14, Evidence item 6).

**Assumed fridge.**
- 0.55 × 0.60 × 1.45 m, just left of the counter run.
- Hinge on the far side; bar handle on the robot side.
- The cart stays docked at x −1.48.

**Decision.**
- The arm swings the door to 35° by the handle in one continuous motion. Reach is ✓ at 0–55°, and 0–35° is a single joint branch.
- It does not reach onto the shelves: the forearm hits the cabinet's own front frame at every approach angle.
- The robot's cold box (冷藏料盒) sits in a door bin at 0.85 m. It is a 0.30 × 0.08 × 0.10 m tub with a bridge bar 0.11 m above the rim. The arm pinches the bar from above, lifts the box over the bin lip, slides it out along the door and sets it down on the counter end beside the cart.
- About 25 s per fetch; the door is open for about 15 s.

**Rejected.**
- R13 baskets on a fridge shelf: not reachable.
- Standing the cart in front of the fridge: outside the dock and tether envelope.
- Opening wider than 35°: needs an elbow flip and re-grasp; beyond 55° the handle is out of reach.

**Open.**
- The real door's seal force (above ~100 N → assisted opening).
- Whether the door stays at 35° by itself.
- The door bin is the warmest zone, so the cold box is for same-day staging only.

- **User reply 2026-10-11: "ok".** The single-door fridge design above is accepted as the working default.

## 2026-10-12 — R15 cooking itself: induction wok, arm-held spatula, tip-to-plate (proposed; sizes estimated)
Evidence: `sim/r10/claude/README_R10.md` (R15), `research/wanggang_cooking.md`, `research/r15_cooking_market.md`.

**Heat.**
- A countertop concave (wok-shaped) 3.5 kW induction cooker on a new 20 A point replaces the robot's use of the gas hob.
  - It puts about 3.0 kW into the wok; the user's gas burner puts in about 0.9–1.6 kW.
  - There is no flame, and power cuts are electric.
- Its knob is turned by a bolt-on servo; no mains modification.
- 离火 = power 0.
- A thermal camera and a colour camera under the hood front watch the wok.
- The robot keeps the wok below 250 °C.
- Rejected:
  - home auto-cook machines (≤ 230 °C, lid shut, no 锅气);
  - the robot operating the gas hob (push-and-hold ignition; only a licensed gas worker may modify it).

**Wok.** 34 cm round-bottom carbon steel with a short handle ending in a keyed grip block 0.235 m from the axis.
- The PGC moment is ≤ 6.3 N·m with the heaviest dish.
- A long handle gave 10.9 N·m, over the 7 N·m limit.

**Stirring.**
- The arm holds a 0.45 m spatula (keyed block).
- The stroke is scrape, lift, return through the air, about 2.6 s per stroke. The cart stays parked left of the wok.
- Checked as one continuous 5-stroke cycle within the UR5e's 180 °/s. The arm stays ≥ 0.20 m from the wok axis while the heat is on.
- Physics: pieces touch the hot zone about 61 % of the time.
- A two-layer load (320 g dice) leaves about 15 % of pieces on top for 12 s, so cook in batches of ≤ about 200 g until real food is tested.
- Rejected:
  - tossing (颠锅): no recipe needs it, and one UR5e cannot do it;
  - a spatula roll at the end of the stroke: the arm cannot follow it;
  - pull-back strokes: the handle points into the hood.

**Heat policy.** Drop to about half power whenever the spatula stops. Heat off before the wok is lifted.

**Additions.**
- With one arm fetching every addition, the spatula is idle for a median 36 % of the stir window.
- A servo pour-drum holder at the wok rim (or pumped liquids to a rim nozzle) brings this to 13 %.
- The holder's place is open: the right rim cannot be loaded by the arm; behind the wok can, with zero reserve.
- Rim pours (锅边淋) with an arm-held cup are rejected: the wrist would sit inside the plume.

**Plating and oil pour-out.**
- The arm lifts the wok by its block, the cart moves left, and the arm tips the wok toward itself to 90° over a plate on the counter left of the hood.
- Checked as one continuous tip.
- The plate stands in a holder with an 8 cm guard.
- Physics with rigid dice: 81–91 % of the food on the plate (98 % at half load).
- Rejected: tipping under the hood or right of the cooker (no room under a 23 cm hood; the arm folds onto its base).

**Open.**
- Real food stir quality.
- The concave cooker's control knob (check before buying).
- The drum holder's place and the spatula's parking place.
- The 0.8 m cart move with the wok in hand (not planned).
- Boiling, blanching, steaming, the lid, ladling oil, 勾芡 by camera.
- Placement of the fire-suppression canister.
- Nothing bought.

## 2026-10-12 — Reference cook: the user's home-style 四菜一汤 creator (R16 direction, proposed)
The user said: "你参考这位，他做的挺家常的" (three 今日食谱 videos). Evidence: `research/homestyle_meals.md`, `sim/r10/claude/README_R10.md` (R16).

- **Target.** His home-style meals: 4 dishes, 1 soup and rice for a family. They are the main reference from now on; Wang Gang's recipes stay as a wider check.
- **What it changes.**
  - Steaming (5/15), soups (3/15) and blanching come first.
  - The wok does short stir-fries (7/15).
  - Several heat sources run at once, and the robot schedules the meal: slow items first, quick wok dishes last.
- **Proposed equipment (to be checked in the sim):**
  - the R15 wok station;
  - a second robot-commandable heat zone (MIoT flat induction) with a steamer or soup pot, or an electric steamer and stew pot;
  - the rice cooker and fryer from R14;
  - a lid, spider strainer and ladle with keyed handles;
  - a plate carrier for steamer plates;
  - a wok rinse between dishes.
- **Timing estimate (one arm, knife work excluded):** 39–78 min of cooking per meal, with the arm busy 15–27 min. The wok is the bottleneck.
- **Knife work** (fish back-split, squid scoring, julienne, peeling) mostly stays outside the robot: bought prepared, the slicer disc, or the user's weekly prep.

## 2026-10-12 — R16 sim checks: second heat zone and its handling (proposed)
The user said "可以，继续" to the R16 next step. Evidence: `sim/r10/claude/README_R10.md` (R16 sim checks), `results/r16/`, `renders/r16/handling.png`.

- **Second zone.**
  - A flat MIoT induction on the right half of the hob carries a 30 cm × 12 cm pot with a 4 cm steaming rack.
  - **Rejected:** a stacked steamer tier, and a 16 cm pot. Taking a dish out of either brings the gripper into the hood, which is 0.40 m above the cooktop.
- **Grasps under the hood band are taken from the front, never from above:**
  - the lid by a front-rim tab, level;
  - the dish carrier by a bail block at 45°;
  - the spider and the ladle along their 45° handles.
- **Checked as whole continuous paths:**
  - lid off → rack: 19 s;
  - dish plate spot → pot: 18 s;
  - ladle fetch, 2 scoops, return: 64 s (34 s per scoop);
  - spider pot → plate.
- **Open:**
  - the spider's rest (the counter end is too crowded: no arm path between rest and pot);
  - carries that move the cart with the arm out break the R10 carry envelope rule. Keep the rule or relax it: decision needed;
  - water needs a valve over the wok and the pot (the R14 station has none);
  - the R15 wok pick-up, carry and tip are still not chained;
  - a spatula rest near the wok.
- **Meal timing with checked action times:**
  - A 39.6 min, B 80.1 min (was 71.8), C 38.6 min;
  - the arm is busy 17–35 min;
  - ladling the soup (5 min) is the largest single item; a pot pour or serving in the pot would cut it.
- Nothing bought; all sizes estimated.

## 2026-10-12 — Decisions on the R16 open items (user)
- **Cart moves with the arm out: allowed.** The user answered "1可以": while the cart moves, the arm may hold an object out over the counter, provided every step is collision checked. This replaces the R10 dock carry envelope for these carries.
- **No water pipe or valve.** The user answered "2不行" and asked why water cannot simply come in a container. It can: nothing needs plumbing. Water comes in containers the user fills before cooking:
  - the kettle already on the hob leg, filled and boiled before cooking, for soup, blanching and 白灼 (hot water also shortens the time to boil);
  - a jug of about 1.5 L near the wok for the rinses (about 0.3 L each, 3–5 per meal);
  - the steaming water put in the pot when the ingredients are set out, or poured from the kettle.
  - Estimate: 6–10 water uses, about 4–8 L per meal; each pour about 20–30 s of arm time, 2–4 min per meal. A full kettle is about 2.5 kg; its handle grasp and pours are not yet checked.
  - Option not chosen yet: the arm fills the jug at the sink tap (needs a tap check; about 30 s per trip).
- **Wok rinse at the sink (user: "不能把锅拿到水池去刷吗", then "你可以先开水龙头呀，浪费点水无所谓").** The wok is rinsed at the sink, not with water poured into it on the cooker. The arm first pushes the user's single-lever faucet open and leaves the water running, plates the dish, carries the wok to the sink and rinses it under the running water, sets it back on the cooker, then closes the faucet. Wasted water is acceptable. The faucet is not replaced. Wok water for blanching (≤ about 1 L, PGC moment) can be taken at the running tap the same way; the kettle remains for the soup pot and larger amounts of hot water.
  - Not yet checked: lever reach and push, the wok under the spout, scrubbing with one arm (fixed brush in the sink, or a spatula scrape on the cooker first). In the user's L-shaped kitchen the sink is on the other leg: reaching it from the hob needs their measurements.

## 2026-10-12 — R17 sim checks: faucet, wok rinse at the sink, counter-end layout (proposed)
Follows the user's decisions above (cart may move with the arm out; no pipe; wok rinsed at the sink, faucet opened first). Evidence: `sim/r10/claude/README_R10.md` (R17 sim checks), `results/r17/chain_*_final.json`, `renders/r17/*.mp4`.

**Checked as whole continuous paths:**
- faucet lever open / close: 3.5 s;
- wok plate + sink rinse + back: 48.9 s, PGC 6.47 N·m of 7;
- spider: 52.6 s;
- lid: 20.2 s;
- dish carrier: 17.7 s, re-checked.

**Design changes**
- The R15 wok handle bracket is replaced by a keyed slot in the cooker rim.
- The wok grasp leans 25° toward the robot, with grasp sense −1. This closes the R15 open item: the pick-up sense and the tip sense now match.
- The pour drum swings away except while stirring.
- The spider moves to (1.52, 0.36). The spatula and the ladle leave the counter end.
- The faucet lever gets a clip-on block, gripped from the right.

**Meals:** A 39.5 / B 79.6 / C 38.6 min, with the arm busy 17–36 min.

**Open**
- the spatula's place near the wok;
- soup serving (the user's call);
- one-arm scrubbing;
- the user's faucet and the L-shaped kitchen (sink on the other leg).

Nothing bought.
- **Serving is the user's (user: "做完上菜人类来就行").**
  - The robot cooks and plates. The user serves, soups included, from their pot. There is no ladle in the design.
  - Meal C's quick soup moves from the wok to the electric stew pot. A soup bowl at the plating spot was hit by the forearm when the arm picked the wok up.
  - Meals: A 39.5 / B 75.0 / C 38.6 min.
  - Finished plates: for now the user takes each finished dish off the plating spot (user: "暂时可以让人去挪走"). Only one plating spot has a checked tip so far; the free counter left of it (about 0.4 m in the sim) is the candidate for a second one.

## 2026-10-12 — R18 checks: second plating spot, spatula home (proposed)
- **A second plating spot 26 cm left of the R15 one passes.** It was checked as the whole wok plate + sink rinse path, with a finished dish on the first spot. The user can leave two dishes before clearing them.
- **The spatula has no home yet.** None of these work:
  - by the sink: blocks the wok and the faucet;
  - behind the plating spots: the cabinet door, and blocks the second plate;
  - the counter end: the spider;
  - the far left: the raw tray.
- The rest-to-stir path also needs grasp sense +1, while R15 checked the strokes with −1.
- Options to check next: a spatula holder on the cart, a backsplash hook rail, or the stroke cycle with sense +1.
- Evidence: `sim/r10/claude/README_R10.md` (R18 checks).

## 2026-10-12 — The spatula lies on the counter left of the sink (user's suggestion, checked)
- **The user asked "锅铲直接放桌子上可以吗".** Yes: flat on the counter left of the sink, blade centre (−1.15, 0.30), handle toward the robot, **flipped over** compared with the R16 rest, on a small pad.
- Flipped over, the robot holds it the way R15 checked the stir strokes. Laid the R16 way, the stroke starts put the arm in the steam plume.
- **Checked:**
  - rest to the wok's stroke start: 26.9 s, 6.0 mm min reserve;
  - no hits on any checked action (wok plate + rinse at both plating spots, faucet, lid, spider);
  - the hand-off to the stir start: 0.5 s;
  - the R15 stir cycle re-run in the current kitchen: passes, 2.63 s per stroke.
- **Cost:** about 41 s more per plating than the R16 estimate. Meal B 75.6 min, was 75.0; A and C unchanged.
- Evidence: `sim/r10/claude/README_R10.md` (The spatula lies on the counter).

## 2026-10-13 — R19 exploration: cost, smooth motion, pre-checked movement library (proposed; user decisions pending)
- **The user asked:** "less money, more smooth movements … lots of predefined movements then movement sets, therefore no need check after each tiny movement."
  - Five parallel studies.
  - Evidence: `sim/r10/claude/README_R10.md` (R19) and `research/r19_*.md`.
- **Proposed motion architecture:**
  - Movement sets start and end at fixed hub states.
  - Each set's geometry is checked once offline. Timing is generated at composition, with formula checks only. Sequences are then checked by construction.
  - After a layout change, only the sets whose stored swept volume is touched are re-checked.
  - The hub roadmap is fully checked: 4 stations, 22 edges, 42 routes.
- **Corrections recorded:**
  - Stored paths need 2π unwrapping before export.
  - R17 stepped coarser than the ≤ 4 mm rule. All 5 paths are now re-checked at ≤ 4 mm: all pass, with smaller true reserves.
  - R17/R18 times assumed unlimited acceleration.
  - The R15 stir period of 2.63 s has velocity jumps and is not executable as checked.
  - A conservative held-part box bug in `scene.py`.
- **Cost:**
  - The biggest saving is a domestic cobot instead of the UR5e (¥150–180k): Fairino FR5 at a ¥23.8k guide price, or Elite CS66 / Dobot CR5A.
  - The prices are unconfirmed. Any swap needs a re-check of the library.
  - Nothing is bought.
- **For the user to decide:**
  - the seasoning station's scope;
  - prep in or out of the robot;
  - who loads the rice;
  - a motorised stirrer / tilt cradle at the wok;
  - a faucet sensor add-on;
  - the fridge or a cooler;
  - the fryer;
  - the cart or a floor rail;
  - which arm.

## 2026-10-13 — User decisions on the R19 questions
- **Arm (user: "你肯定先去验证便宜的能不能用吧").** Verify the cheap arms in the sim first.
  - Start with the Fairino FR5, then the Elite CS66.
  - The UR5e stays the baseline until a cheaper arm passes the same checks.
- **Motorised stirrer / tilt cradle (user: "比较难吧，市面上有这种产品吗").** Not adopted. First survey the market for products that already stir and tip out by themselves, and how the robot could control and load them.
- **Seasoning (user: "调料站你定，但肯定不是由人来做").**
  - Dosing stays automatic. The person does not mix or dose seasonings per meal.
  - The orchestrator sizes the station.
  - Assumption to confirm with the user: the person only restocks bulk containers, like buying groceries.
- **Prep (user: "备菜是最重要你要做的之一了，肯定不是人来做").**
  - Washing, peeling and cutting stay the robot's job. Prep is a top priority, not an option to drop.
  - Option O7 (prep out of the robot) is rejected.
- **Rice (user: "电饭煲我可以做").**
  - The person loads and starts the rice cooker.
  - The rice hopper/auger module and the arm's rice actions are dropped from the design and the meal model.

## 2026-10-13 — Ingredients arrive as the reference cook buys them (user decision)
- **The user said:** "那些剁块，鱼和鱿鱼这些肯定摊主会搞定，你看我给你的视频他一般买回来什么样我们就是什么样".
- **Starting state:** every ingredient arrives in the state the reference cook brings home in the three videos. For example, ribs come chopped by the butcher, and fish and squid come cleaned by the fishmonger.
- **The robot's job:** everything he does himself in the videos (washing, peeling, cutting, scoring, mincing, marinating, soaking) stays the robot's job, per the 10-13 prep decision.
- **Source for each ingredient:** the as-bought state comes from the video frames and transcripts (`research/homestyle_meals.md`; frames in the session scratchpad `home3/`), recorded in `research/r19_asbought.md`.

## 2026-10-13 — Seasoning: dose directly at the wok (orchestrator decision under "调料站你定，但肯定不是由人来做")
- **Chosen:** option (d) of `research/r19_seasoning_sizing.md`.
  - About 11 pumped liquid channels: oil, saturated brine, sugar syrup, 生抽, 老抽, 蒸鱼豉油, 料酒, 陈醋, 白醋, 蚝油, and a starch slurry made fresh each cooking day. Three channels are spare.
  - Each bottle stands on a load cell, so a dose is weighed by the bottle's loss of weight.
  - A nozzle cluster over the wok. Chili and 花椒 portioners, plus a spice-sachet dropper, sit at the wok.
  - Rare pastes come from squeeze bottles that the arm squeezes.
- **Dropped:** the augers, the syringes, the 花椒 feeder, the weighing cup, and most robot cups.
- **Why:**
  - Seasoning arm moves fall from 18–27 to 3–12 per meal (model).
  - It covers 14 of 15 reference dishes with no person dosing, against 10 of 15 today.
  - Parts cost about ¥4.5–12.5k, against ¥7.3–17.6k (unconfirmed).
  - No bought dispenser has a robot interface.
- **Before building:**
  - a sim check of the nozzle placement against the spatula strokes and the hood gap;
  - bench tests with real liquids;
  - the user's OK on the taste-relevant substitutions: sugar as syrup, whole spices in sachets, 十三香 omitted.
- **Revised the same day after the user asked "不能用糖吗，另外那几个为什么呢". No substitutions: the real ingredients are used.**
  - **Sugar:** real white sugar.
    - First choice: a sealed dry portioner at the wok, like the chili and 花椒 portioners, with desiccant. Caking in steam needs a bench test.
    - Fallback: the station dissolves real white sugar into syrup (the R14 66 % syrup).
    - No fructose syrup.
  - **八角 / 桂皮:**
    - The arm picks the real pieces from a small open spice tray, located by the camera. Only 1 reference dish (红烧肉) and a few Wang Gang braises use them.
    - A bought 卤料包 is only a fallback, because its blend differs.
  - **十三香:** not omitted. The arm shakes a shaker jar over the wok, as a person does. It is one move, for "a little" in 干锅土豆.

## 2026-10-13 — Seasoning goes into containers that the arm picks up, premixed per dish as the reference cook does (user decision; supersedes "dose directly at the wok")
- **The user said:** "我还是觉得直接放锅上不靠谱啊，不能用容器装好然后拿起来这种吗。或者是每道菜提前准备好料汁之类的。我给你的视频里是怎么做的".
- **What he does in the videos:**
  - **Premixed in a bowl:** he mixes a dish's liquids beforehand: 蚝油西兰花 sauce, 青椒炒鱿鱼 sauce (with starch), 酸辣土豆丝 调味水, 白灼汁, the luffa sauce, the rib marinade.
  - **Added straight in:** the single items go in from the bottle or spoon at their moment: salt, sugar, 料酒, 生抽, 豆瓣, dried chili / 花椒, 八角 / 桂皮, 十三香.
- **New rule:**
  - During prep, the automatic station doses each dish's seasonings into containers in a dry place away from the wok: a 料汁 cup per premix, and a cup or compartment per single addition moment. Each dose is weighed. Dry items and the cut aromatics go into their own cups.
  - The arm stages the cups near the heat zone. At each moment it picks one up and pours it, or uses the pour drum for bursts.
  - No nozzles over the wok. Nobody doses by hand.
- **Real ingredients:** real white sugar; real 八角 / 桂皮 picked into a cup; 十三香 shaken into a cup.
- **Next:** re-size the station and count the cup moves per meal against the video's seasoning moments.

## 2026-10-13 — Seasoning cups: user answers and orchestrator decisions (user: "洗碗机有的，到时候也可以建模然后自动化。清水有小米饮水机。其他你定")
- **Dishwasher.** The user has one. Cups, caddies and robot tools are dishwasher-safe, and the caddies double as dishwasher baskets. The robot loading and unloading the dishwasher is to be modelled and automated later (its own GitHub issue).
- **Clean water.** It comes from the user's Xiaomi water dispenser (小米饮水机), feeding the station's water channel or a jug the arm fills there. The model and interface are not known yet.
- **Restocking (orchestrator decision).** The person only restocks bulk containers: bottles, salt and sugar hoppers, the spice tray, squeeze bottles. Nobody doses per meal.
- **Merges (orchestrator decision).** Items the cook adds at the same moment share one cup. All four merges are additions at the same moment in the videos, so the taste does not change:
  - salt into the 蚝油 sauce;
  - 葱姜 with 八角 / 桂皮 / chili;
  - salt and sugar into the tomato water;
  - salt with the celery.
- **糖色 (orchestrator decision).** As in the video, he pours a ready-made 糖色. The robot makes 糖色 in batches in the wok with real sugar, stores it in a jar, and doses it into a cup. The batch-making is a new movement set.
- **Station** per `research/r19_seasoning_cups.md`: about ¥4.9–16.2k (est.), at the freed rice/flour port. The cup staging spot and the pick → pour → return set still need a sim check (GitHub #5).

## 2026-10-13 — True arm geometry is the checking standard (orchestrator decision, GitHub #12)
- **What was found.** The sim's UR5e collision capsules (MuJoCo Menagerie) did not enclose the real arm, by up to 26.5 mm. Checked with geometry that does enclose it, the R17/R18 wok, lid, spider and lever paths failed.
- **The standard from now on.** Every check uses certified-enclosing arm geometry:
  - `ARM=ur5e_enc2_pgc`: k-DOP hulls around the Menagerie meshes, plus the PGC-140 gripper from DH's manual drawing (a Ø75 body);
  - for other arms, their vendor-mesh fits (`fr5`, `cs66`);
  - the old `ur5e` default stays only for reproducing old results.
- **Layout change.** The plating spot moves 20 mm toward the wall: y 0.13 → 0.15 (`PY=.15`). The elbow passed 7.5 mm above the plate rim.
- **Result.** With `ur5e_enc2_pgc` and `PY=.15`, all six stored chains re-check clean at ≤ 4 mm and are adopted (certificates attached): wok, plate 2, lid, spider, lever, spatula. The hub roadmap is rebuilt: 22 / 22 edges and 42 / 42 routes are checked.
- **Open.**
  - The PGC base cable connector is not modelled (not dimensioned on the drawing).
  - The prep sets still need re-planning for the true geometry (#4).
  - #13 is to be re-run with this arm.

## 2026-10-13 — Pot zone: spider rest moved, keyed lid rack (orchestrator decision under "其他你定", GitHub #37 / #8)
- **Spider rest** moves from (1.52, 0.36) to **(1.56, 0.20)**. On the true arm geometry, the old spot left the upper arm 10.4 mm from the cabinet over the hood, and no re-plan could keep 15 mm there. At the new spot it keeps ≥ 19.4 mm.
- **Why this spot rather than (1.62, 0.26).** Both give the same UR5e result. Only (1.56, 0.20) also clears the FR5 lid path (#2).
  - **Cost:** the spider's grip block sticks out 82 mm past the counter edge, at 1.16 m. The other spot sticks out 22 mm.
  - Revisit this if people at that corner matter more than the FR5 option.
- **Lid rack:** two V-groove pads under the upright lid's rim (`kitchen19pot.py`, `RACK=keyed`). They capture ±14.8 mm across the rim plane.
  - The last 50 mm of the straight drop into the rack is a declared contact window. Only lid parts against rack parts are exempt.
  - The stored lid path is kept unchanged.
  - **Pot lift-off window (`POTWIN=1`): adopted (10-13 evening).** The lid's straight 20 mm lift off the pot rim follows the same window rule. Docking-stop corner: +6.59 mm with it, +1.18 mm without it. Tilt tolerance: 0.43°, against 0.30° without it. Contact force at both seats goes to #26.
- **Report:** `sim/r10/claude/R19_POTZONE.md`. The hub edges, corner replays and the full tolerance set are running as controller lanes.
