中文摘要：本轮新建独立的紧凑实现，完成 **9 轮有记录的结构布局比较**。移除顶端进料处理机，改为完整尺寸的水平曼陀林切片台，并保留原 UR5e、L101 单轨、小车、拖链、水嘴及厨房。最终 I09 固定工位相交为 **0**，篮口中心与实际水轴重合；主要加工台顶部为 1.030–1.043 m。完整输出碗提手最高 1.0593 m，比严格的 200 mm 台上目标高 9.3 mm，未缩小几何或隐瞒此项。

胡萝卜仅 **1/11 个静态动作模板**通过，内部路径 **0/11**，已执行连接 **0/10**，成品 **0/4**。全部十个连接均实际给出 65 秒规划预算；不能把搜索次数、独立姿态或局部前缀算成连续制作。停放快照 **通过**，完整折叠／展开与胡萝卜执行未闭合，idle=fail。采用停止条件 **(b)** 交付，不是可制造方案或不可行性证明。备菜时间为 **null**，预算 **338,215.00 元**；未采购、联系供应商或进行实物试验。

**Result and scope.** The selected scene is I09. This is a failed carrot-first feasibility delivery, not a completed four-product controller. All four finished-product definitions and the 0.57 kg food ledger remain unchanged. The denominator 11 is this round's declared carrot manipulation-template set; it is not comparable to R07's 59 templates or 110 expanded meal connections. Missing physical guard, holder, drawer and transfer bindings are reported, not treated as appliance-internal food transformations. Other product motion sequences were deferred after the carrot failure.

The package is in [sim/r08/integrator](../../sim/r08/integrator/README.md). It contains one scene builder, checker adapter, solver, planner, transactional food-state module and foreground runners. Only the two mesh files actually referenced by the compiled L101 arm, original robot primitives/inertias, complete bowls, selected vendor metadata and source contract were copied. It does not import the old versioned solver stack. [Provenance](../../sim/r08/integrator/results/provenance.json), [final audit](../../sim/r08/integrator/results/delivery_audit.json).

**Geometry decisions.** The counter remains at 0.85 m, cabinet underside at 1.35 m and cabinet front at Y=0.23 m. The complete robot and rail geometry and inertias compare unchanged. Door sensors were rigidly shifted 10 mm wallward to provide 20 mm sweep separation. Closed leaves and cabinet bodies are obstacles during all motion; full opening sweeps apply only to park. No processor is installed and none is charged in the BOM.

The right-front mandoline retains the golden 330 × 120 × 60 mm deck, **65 mm radius** holder sphere, 80 mm work/CoM offset, 0.55 kg loaded-holder budget and 200 mm horizontal stroke. The nominal load is −40 N feed, ±10 N lateral, +20 N up; the binding R05 P06/T08 review check is −60 N, ±10 N, +20 N. The golden file's separate 70/100 N exploration is not substituted for that check. Both lateral signs are checked. Guards are actual obstacles. The custom catch tray uses one identical full geometry definition in its stored and held states; it is not replaced by a bare TCP during delivery.

The P16 envelope remains 480 × 50 × 50 mm, with the complete separate guide and cutter. Its low roof and front drawer replace the raised-lid interface. The retained sourced loads are 63 N tangential and 7.5 N normal. The 200 mm P16 has a 4 N lateral limit, requiring that separate guide; 150 N at 3.4 mm/s and the duty-cycle allowance underlie the inherited 2,823.529 s per-root design time. This is component sizing, not measured peel quality or cycle completion. [Actuonix datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf).

Greens use a low guillotine/splitting fixture; tomato uses a low lever/eight-sector fixture. Their inherited design loads are 348.8516 N and 636.3651 N, respectively, with the original source IDs and proxy limitations preserved. Their complete actuation, lever advantage, tooling travel and food-quality performance remain unqualified. The new low fixtures are custom design envelopes, not matched commercial appliance CAD. [Source and force record](../../sim/r08/integrator/results/sources.json), [unchanged source contract](../../sim/r08/integrator/assets/process_contract.json).

The wash basket keeps its full 240 mm diameter and 140 mm height. The final full shell is tilted 55° and raised bodily 15 mm relative to I08. Its mouth centre is on the vertical jet at X=−0.58, Y=0.43 m; ray-to-mouth radial error is 0.000000 mm. Raising the entire shell eliminates the previous sink-bottom intersection and leaves approximately 11.7 mm geometric separation. **A real cradle/retention design is still required**; an unsupported tilted basket is not credited as executable washing. No spray cone or successful cleaning is inferred from axis alignment.

**Nine recorded structural iterations.** Every row has three full-scene corridor probes with 96 starts each. A clear sample is one first-pose result, not an admitted complete stroke. I01–I04 exposed an erroneous provisional bowl-centre transform; I05 corrects the complete assemblies using measured source shell-bottom centres. This placement error and its packing evidence remain visible. The later redesign relocates all four complete bowls to the left rear, spreads stations, changes wash approach and restores the original right-rear parking space.

| Iteration | Clear corridor samples | Starts | Jet hits mouth | Fixed-part intersections | Structural change |
|---|---:|---:|---|---:|---|
| I01 | 1/3 | 288 | True | 143 | Replace processor with horizontal mandoline; original upright basket centred at the jet. |
| I02 | 1/3 | 288 | False | 130 | Front mandoline corridor and basket above sink rim; test jet-height conflict. |
| I03 | 1/3 | 288 | True | 127 | Tilt full wash shell 45 degrees into sink; preserve radius and height. |
| I04 | 1/3 | 288 | True | 127 | Rotate complete mandoline and its 200 mm stroke 90 degrees to use front approach. |
| I05 | 1/3 | 288 | True | 45 | Move complete bowl assemblies to front docks and use side-loading peeler drawer. |
| I06 | 0/3 | 288 | True | 39 | Swap root-processing bays: mandoline on broad left counter; peeler on right. |
| I07 | 1/3 | 288 | True | 4 | Packing evidence moves all bowls to left rear, peeler right rear, greens left front and wedger right front; correct full raw tray arrangement. |
| I08 | 1/3 | 288 | True | 4 | Keep distributed stations; replace vertical wash loading with front-facing approach below spout and shorten peeler entry to its open mouth. |
| I09 | 1/3 | 288 | True | 0 | Restore legal right-rear park volume. Move full mandoline right-front, P16 left-front, rotate greens fixture 90deg, raise full tilted basket15mm; use horizontal-food side grasp and actual peeler cradle seat. |

[Iteration ledger](../../sim/r08/integrator/results/iterations.csv), [selected scene](../../sim/r08/integrator/models/selected.xml). Zero fixed-part intersections is necessary, not proof of mounting, stability, appliance operation or reachable motion. The support and mechanism gaps above remain real blockers.

**Checker and path evidence.** The wrapper imports the actual immutable [R05 reference](../../sim/r05/integrator/reference.py), using only a read-only metadata shim to suppress the old builder's import-time writes. Its SHA-256 remains `46e9002b222cf92970cfc5b30c10fbe23eed06470b8714fc946ffdd44d0f5681`. The collision, rotation and grip functions are used directly, with independent convex lower bounds for all eligible pairs. Pose gates stay 5 mm / 3°, robot/environment and arm/arm gaps 10 mm, held/gripper/environment gaps 5 mm, PAD=0, μ=0.5, SF=1.5 and 150 N / 15 Nm key capacity. No numerical negative reserve is treated as a build tolerance.

Eight unchanged R07 geometry verdicts from four templates reproduce. The complete test suite reports **True**. Contact declarations have explicit kinds, compiled part identities, actual support signatures and immutable registered window descriptions. Wrong object, support, part, frame, finger, stale geometry and working permission on transit reject. Support lift/approach permission ends at 50 mm; it is not renewed to disguise a longer contact path. The 200 mm cutting line is a working stroke. The conservative golden food/holder proxy has an explicitly named short lift permission only at its own mandoline surfaces. Synthetic capability tests are not motion evidence. [Regression](../../sim/r08/integrator/results/regression.json).

Each selected endpoint receives 96 starts: **2112 starts** over 22 endpoint searches. The optimizer includes collision penalties, source-informed seeds and random full-range starts. Positive candidates receive independent final geometry/load admission. Internal paths must follow the Cartesian line and fixed orientation, and every interpolation uses the model-derived all-point displacement bound ≤4 mm. Only both-endpoint acceptance counts as a static stroke. The sole complete static template, holder loading, fails internally at a saved carrot/guard gap of **4.907906 mm versus 5 mm**, after 38 accepted prefix samples; the rejected edge's step bound is 3.585719 mm. This is a rejection, not an almost-pass or robust design.

Representative saved failed candidate pairs are below. They describe these finite attempts, not global impossibility certificates. Native signed contact values are retained conservatively; the old libccd discrepancy is not bypassed.

| Carrot template | Representative pair | Saved gap / gate, mm |
|---|---|---:|
| raw_pick | R_geom_11 / counter_left_piece1 | 4.6242 / 10.0 |
| wash_load | R_geom_21 / sink_front_rim | -25.4595 / 10.0 |
| wash_work | faucet_v3_fixed_spout_full_envelope / R_gripper_palm | -30.0000 / 5.0 |
| peel_load | R_held_carrot / peel_drawer_floor | 0.0000 / 5.0 |
| peel_retrieve | R_geom_26 / counter_left_piece2 | 9.4121 / 10.0 |
| mandoline_work | R_geom_21 / r07_closed_door_1_1 | 7.4504 / 10.0 |
| holder_retreat | R_geom_11 / north_wall | -50.0000 / 10.0 |
| catch_tray_pick | R_geom_11 / north_cabinet_right_piece1 | -30.9688 / 10.0 |
| bowl_deliver | R_geom_17 / upper_cabinet_0 | -27.9987 / 10.0 |
| scrap_service | R_geom_11 / north_cabinet_left_piece2 | -50.0000 / 10.0 |

The main structural causes remain the arm/wrist corridor into the recessed sink, the under-cabinet approach to supported food and seated peeler tooling, mandoline guard/closed-door interference over the entire stroke, and full-container pickup/delivery access. Replacing the tall processor improves some static reach, but does not solve these interfaces.

All ten consecutive carrot connections actually run RRT-Connect with a **65 s allocated budget**, restarts, staging bias, shortcutting and full ≤4 mm replay for any proposed accepted path. Total recorded planner wall time is **650.016 s**, separate from robot preparation time. Geometric connections: **0/10**; committed conserved connections: **0/10**. Failed endpoints do not skip the search budget. [Motion](../../sim/r08/integrator/results/motion.json), [phase summary](../../sim/r08/integrator/results/phase_summary.json), [saved blockers](../../sim/r08/integrator/results/blockers.json).

The transactional food state starts at the actual scene input positions. Regions bind to the selected peeler and actual mandoline catch-tray interiors; a caller cannot invent a remote region to transform food. Full input extents, support ownership, unattached food, bulk capacity and mass conservation are enforced. Remote/partial/held transformations, unknown operations, negative times, overcapacity, direct bulk grasp, binding teleport and forged regions reject. The successful transformations in tests are synthetic fixtures. The committed meal remains the initial 0.57 kg state. No real container motion, lid, pusher, interlock, eye/core operation, terminal-stub handling or ≥98% delivery is abstracted away. [State sequence](../../sim/r08/integrator/results/state_sequence.json).

**Idle, reserves and human counter space.** Parked snapshot: **True**. Prospective fold: **False**; unfold: **False**; complete idle: **False**. Both path attempts use the exact saved park state and closed-door scene. Open-door rendering is a prospective snapshot, not evidence that the robot reached it. [Idle](../../sim/r08/integrator/results/idle.json).

The following distributions contain admitted diagnostic endpoint/path states only; there is no executed-carrot reserve distribution. They use each state's worst eligible pair, including the original self-nonpenetration category. No accepted state below 2 mm is silently promoted to a buildable installation; any such diagnostic states receive individual reasons in clearance.json.

| Category | States | Minimum extra mm | P05 extra mm | Fraction ≥10 mm extra |
|---|---:|---:|---:|---:|
| robot_environment | 4 | 4.710286 | 4.903743 | 0% |
| held_gripper_environment | 4 | 14.999979 | 15.749945 | 100% |
| arm_arm_or_frame | 4 | 10.974996 | 10.974996 | 100% |
| self | 4 | 0.000000 | 0.000000 | 0% |

The fixed bowl-collar/wall-bracket pair has only **6 mm beyond its 10 mm gate**; this limits every sampled robot/environment state and fails the requested majority-at-10-mm reserve objective. The mandatory geometry is retained. Four whole bowl bails also reach 209.309 mm above the counter; strict ≤200 mm compliance is therefore false, and a further full-bail articulation/interface redesign is required. [Clearance](../../sim/r08/integrator/results/clearance.json), [height audit](../../sim/r08/integrator/results/delivery_audit.json).

Conservative free supported counter area at prospective idle is **0.18160 m²**, of which **0.14473 m²** is in the front strip. The 5 mm grid excludes the sink and stove and expands full occupied projections by 10 mm. No unexecuted station stow is credited. It is an area estimate, not ergonomic acceptance. [Counter plot](../../sim/r08/integrator/renders/counter_free_area.png).

**Time and budget.** Preparation time is **null**. The executed timeline is empty because the first connected carrot prefix is not admitted. The schedule explicitly retains the 600 s greens soak, 30 s potato drain, three fresh-water starch rinses and two component-derived root-peeling allowances; unknown washing/cutting/transfer times remain null. Proposed home-tier limits are rail 0.08 m/s, joints 0.25 rad/s, every point 0.10 m/s and acceleration 0.30 m/s². They are not a performed recipe schedule. [Schedule](../../sim/r08/integrator/results/schedule.json).

The clean BOM has base **CNY 294,100.00**, exactly one 15% reserve **CNY 44,115.00**, total **CNY 338,215.00**. Exactly one **CNY 18,000** home-safety package covers presence/door sensors, E-stop, RCD/PE, blade/door interlocks and control. Rail brakes are already in the rail line. The processor is removed; custom mandoline, peeler, guillotine, lever wedger and tray allowances replace the old mixed tool bundle. All amounts are planning allowances, not supplier quotations or a cheapest passing design. [Costs](../../sim/r08/integrator/results/costs.csv).

All numerical chunks are CPU-only, under 20 minutes with an explicit timeout and 1,900 MiB guard, at most four numerical workers. The latest measured output is 29.40 MB, below 3 GB. The original R05/R07 inputs are not modified. The state/controller and fixture limitations are substantive unfinished work, not waived acceptance gates.

**Renders.** All are ≤1600 px, CPU projections of checked geometry with labelled cutaways. There is **no executed carrot frame strip**, because no carrot sequence executed. The delivered 24-frame strip explicitly shows separate failed wash IK configurations; it must not be read as chronological motion.

- [Overview](../../sim/r08/integrator/renders/overview.png)
- [Wash](../../sim/r08/integrator/renders/wash.png), [peel](../../sim/r08/integrator/renders/peel.png), [mandoline](../../sim/r08/integrator/renders/mandoline.png)
- [Greens](../../sim/r08/integrator/renders/greens.png), [tomato](../../sim/r08/integrator/renders/tomato.png), [output bowls](../../sim/r08/integrator/renders/bowls.png)
- [Prospective park with doors open](../../sim/r08/integrator/renders/parked_doors_open.png)
- [24 unexecuted carrot candidates](../../sim/r08/integrator/renders/carrot_diagnostic_strip.png)

DONE integrator carrot=fail products=0/4 strokes=1/11 connections=0/10 idle=fail prep_min=null cost_cny=338215.00 min_reserve_mm=0.000000
