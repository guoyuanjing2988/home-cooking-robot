本轮建议继续评估 xArm6×2：后墙水平轨道中心距台面 0.45 m，机械臂基座向下倾斜 30°，离墙 0.25 m，夹持点距法兰 110 mm。最佳设计在每阶段 96 个种子的检查中有 10/16 阶段找到通过模型检查的姿态。夹持、工具、载荷方向、5 mm/3° 位姿容差和碰撞间隙规则均保留原版。

这个阶段数是有条件的模型结果：xArm 的力矩参考值由厂家额定电机力矩和减速比推导，公开资料没有确认连续关节输出力矩或齿轮效率。也没有确认每个承重关节的制动器都采用弹簧施加。因此本轮没有宣称全约束已验证的可投用设计。原始种子、完整差异、力矩敏感性和未通过原因均保留在结果中。

按 3 kg 工具端载荷和原规定力矢量进行独立静载尺寸估算，单小车最大合力 240.0 N、轨道连接点最大合力矩 103.6 N·m；外侧支承处悬臂估算达到 577.1 N·m。驱动静力加声明的摩擦/线缆拖力余量为 117.2 N，动态制动载荷还需另算。

另行将通过姿态的工具端载荷提升到 3 kg，并施加原规定载荷后，最差力矩比达到 1.47，超过参考额定值。因此，5 kg 标称负载不能证明本任务的全载荷能力；原阶段通过数仍按原版规定的物料质量计算。

两臂和三臂均完成 16 阶段、每阶段至少 96 个种子的检查及黄金 mandoline 检查。第三臂没有获准分担原定义的工具力；单轨两端停车会占用篮筐附近需要的基座位置。新增机械臂是否改善并行节拍，需要另一个任务和轨道布局验证。五张图使用真实模型求得的姿态，由 Blender 在 CPU 上渲染。


English engineering record — 2026-10-07


The leading conditional model screen is **xArm6×2**, rail height **0.45 m above the 0.850 m counter**, **down30**, **0.25 m stand-off**, with a **0.110 m flange-to-grasp extension**. It admits **10/16** phases under the explicitly derived rated-motor torque reference. No fully verified continuous-output-torque admission is claimed. This is a partial concept result, not a released kitchen robot.


**Arm-family sweep comparison**


Each row is that family's best observed entry. Seed density and rating eligibility are shown because the coarse two-seed results do not support an exhaustive comparison with the final 96-seed design. The complete 754-entry CSV retains unmeasured phase fields as blank.

| Arm / count | Height / mount / stand-off | Observed phases | Seeds / stage | Admitted torque ratio | Nominal payload eligible | Torque reference |
|---|---|---:|---|---:|---|---|
| xArm6×2 | 0.45 m / down30 / 0.25 m | 10/16 | 96 / final | 0.850 | True | rated_motor_times_100_gearing_ideal |
| UR5e×3 | 0.45 m / down30 / 0.15 m | 2/16 | 2 / coarse | 0.280 | True | maximum_only_not_continuous |
| FR3×3 | 0.45 m / down30 / 0.15 m | 2/16 | 2 / coarse | 0.324 | False | maximum_only_not_continuous |
| xArm7×2 | 0.45 m / down30 / 0.15 m | 1/16 | 2 / coarse | 0.456 | False | rated_motor_times_100_gearing_ideal |
| AUBO_i5×2 | 0.3 m / horizontal / 0.05 m | 0/16 | 2 / coarse | — | True | urdf_effort_not_continuous |


**Final 96-seed results**


Each value is the input checker's admitted-seed count and the lowest worst nominal torque ratio for that phase. P11/P12 counts pair independently admitted strokes as the original checker specifies. Ratios marked † are IK/collision diagnostics for a failed phase; they are not feasible witnesses. Check-force ratios remain diagnostic.


| Phase | Process | 2 arms: seeds / nominal ratio | 3 arms: seeds / nominal ratio | 2 arms: check ratio |
|---|---|---:|---:|---:|
| P01 | Pick carrot and lift 100 mm | 0/96 / 0.230 † | 0/96 / 0.231 † | — |
| P02 | Rinse carrot, wrist -60 to +60 deg | 4/96 / 0.334 | 1/96 / 0.273 | 0.352 |
| P03 | Place carrot on clamp board | 4/96 / 0.297 | 8/96 / 0.263 | — |
| P04 | Peel clamped carrot, 120 mm | 4/96 / 0.388 | 4/96 / 0.336 | 0.429 |
| P05 | Load carrot in holder on deck | 6/96 / 0.317 | 4/96 / 0.298 | — |
| P06 | Mandoline carrot, 200 mm | 3/96 / 0.850 | 3/96 / 0.652 | 1.149 |
| P07 | Pick potato | 2/96 / 0.422 | 0/96 / 0.234 † | — |
| P08 | Rinse potato, wrist -60 to +60 deg | 5/96 / 0.340 | 1/96 / 0.282 | 0.357 |
| P09 | Peel clamped potato, 120 mm | 3/96 / 0.408 | 3/96 / 0.371 | 0.449 |
| P10 | Mandoline potato, 200 mm | 1/96 / 0.806 | 2/96 / 0.620 | 1.106 |
| P11 | Greens into rinse basket and spinner pump | 2/96 / 0.214 | 1/96 / 0.232 | 0.214 |
| P12 | Greens knife cuts at 40 mm spacing | 0/96 / 0.163 † | 0/96 / 0.218 † | 0.316 |
| P13 | Tomato wedger, 50 N total with R handle | 0/96 / 0.123 † | 0/96 / 0.123 † | 0.123 |
| P14 | Lift loaded catch tray and tilt 60 deg over output | 0/96 / 0.394 † | 0/96 / 0.394 † | — |
| P15 | Pick Y-peeler and return | 0/96 / 0.208 † | 0/96 / 0.253 † | — |
| P16 | Pick knife and return | 0/96 / 0.281 † | 0/96 / 0.296 † | — |


| Design | Phases admitted | Worst best admitted ratio | Phases at assumed 85% gear efficiency | Min active-joint margin | Min flange reach margin |
|---|---:|---:|---:|---:|---:|
| xArm6×2 | 10/16 | 0.850 | 10/16 | 2.2° | 78.1 mm |
| xArm6×3 | 9/16 | 0.652 | 9/16 | 3.8° | 100.4 mm |


Reach margin is nominal arm reach minus mounting-plane-to-flange distance in the selected best admitted witnesses; it is a geometric diagnostic, not a workspace certificate. Joint margin is the smallest active-joint distance to a source limit. The 85% sensitivity scales all rated-motor-derived limits by 0.85 and counts the original admitted stroke pools that remain within torque; it introduces no new checker gate.


**Golden mandoline check**


| Feed reaction | 2 arms: admitted seeds / best ratio | 3 arms: admitted seeds / best ratio |
|---|---:|---:|
| 40 N, +20 N up, ±10 N lateral | 1/96 / 0.837 | 2/96 / 0.924 |
| 70 N, +20 N up, ±10 N lateral | 0/96 / 1.275 | 0/96 / 1.600 |
| 100 N, +20 N up, ±10 N lateral | 0/96 / 1.712 | 0/96 / 2.275 |


Golden IK/collision-free counts are 16/1 for two arms and 28/2 for three arms, out of 96. Force-specific counts use unrounded ratios; the original rounded display is also retained. A dagger marks a collision-rejected diagnostic pool.


**Why the remaining phases fail**


- P01: {"IK": 70, "collision": 26}; dominant local-IK witness misses by 6.2 mm / 0.6°; one rejected IK-complete seed contacts ['upper_cabinet_0', 'R_link1_collision'] at -2.4 mm gap (required 10.0 mm). Failure is a sampled result, not an exhaustive impossibility proof.

- P12: {"IK": 75, "collision": 21}; dominant local-IK witness misses by 8.5 mm / 0.3°; one rejected IK-complete seed contacts ['upper_cabinet_1', 'R_link2_collision'] at -26.5 mm gap (required 10.0 mm). Failure is a sampled result, not an exhaustive impossibility proof.

- P13: {"IK": 72, "collision": 24}; dominant local-IK witness misses by 6.3 mm / 0.3°; one rejected IK-complete seed contacts ['upper_cabinet_1', 'R_link3_collision'] at -16.8 mm gap (required 10.0 mm). Failure is a sampled result, not an exhaustive impossibility proof.

- P14: {"IK": 86, "collision": 10}; dominant local-IK witness misses by 7.0 mm / 0.0°; one rejected IK-complete seed contacts ['upper_cabinet_1', 'R_base_adapter_plate'] at 9.4 mm gap (required 10.0 mm). Failure is a sampled result, not an exhaustive impossibility proof.

- P15: {"IK": 79, "collision": 17}; dominant local-IK witness misses by 6.9 mm / 0.4°; one rejected IK-complete seed contacts ['upper_cabinet_1', 'R_link3_collision'] at -49.3 mm gap (required 10.0 mm). Failure is a sampled result, not an exhaustive impossibility proof.

- P16: {"IK": 75, "collision": 21}; dominant local-IK witness misses by 5.1 mm / 0.3°; one rejected IK-complete seed contacts ['upper_cabinet_0', 'R_base_adapter_plate'] at 9.4 mm gap (required 10.0 mm). Failure is a sampled result, not an exhaustive impossibility proof.


The identical-pose replay transfers every admitted two-arm stroke into the three-arm scene while retaining R/L poses and adding only C's parked arm. It loses 2 admitted stroke witnesses. The detailed per-phase counts and collision witnesses are in `results/third_arm_replay.json`. The extra arm supplies no new T08 contact or load-sharing permission. Different independently sampled seed counts alone are not evidence of a third-arm benefit.


**Static mounting and drive inputs**


These are separate sizing calculations at all IK-complete final poses, including rejected poses for a conservative envelope. Each witness records whether its original stroke was admitted. Every carriage carries 3 kg for capacity sizing: R uses the original mass site, and unused arms use the same phase COM offset in their own tool frames. Reference phase held masses and acceptance remain unchanged.


| Quantity | Static envelope |
|---|---:|
| Per-carriage resultant force | 240.0 N |
| Per-carriage moment at carriage/rail datum | 103.6 Nm |
| Ideal X drive holding force | 100.0 N |
| Drive force plus assumed drag | 117.2 N |
| 1.5× drive-plus-drag allowance | 175.8 N |
| Outer-support cantilever moment envelope | 577.1 Nm |
| Whole rail net wall force | 758.4 N |
| Whole rail moment about central wall datum | 746.1 Nm |
| Worst admitted-pose torque ratio with 3 kg and prescribed loads | 1.473 |


The separate 3 kg capacity calculation exceeds the derived torque reference at an otherwise admitted pose (ratio 1.473). Nominal 5 kg payload alone therefore does not establish the requested 3 kg plus holder and process-force service. Original phase masses and phase gates were not changed to hide this result.


The drive allowance uses |Fx|+0.01×transverse load+15 N cable drag, all declared assumptions. Horizontal gravity does not itself require X drive force, but the rail bearings carry gravity and overturning moment. The spring brake must cover the actual drive-axis holding/stopping case; acceleration, impact and Category 1 stop loads are not included in these static values. The cantilever estimate uses link COM point loads beyond x=-1.50/+0.55 m and distributed beam/carrier weight. It is not a solved four-bracket reaction distribution. The net central-wall wrench is likewise not one anchor's load. `results/loads.json` preserves vector directions, positions and the worst-case witnesses. The final DONE moment field is the larger of the carriage-interface and outer-support cantilever moment envelopes.


**Reviewable artifacts and images**


The complete numerical grid is [sweep.csv](../../sim/r01/concept/results/sweep.csv); the leading design and both 96-seed phase tables are [best.json](../../sim/r01/concept/results/best.json). Load keyframe 0 (`P06_witness`) in [best_scene.xml](../../sim/r01/concept/models/best_scene.xml), or use the [visual scene](../../sim/r01/concept/models/best_scene_visual.xml). Both reference only assets copied into this workspace. The source manifest is [sources.json](../../sim/r01/concept/sources/sources.json).


![Overview](../../sim/r01/concept/renders/overview.png)


![Washing at the sink](../../sim/r01/concept/renders/washing.png)


![Peeling](../../sim/r01/concept/renders/peeling.png)


![Mandoline slicing](../../sim/r01/concept/renders/mandoline.png)


![Parked](../../sim/r01/concept/renders/parked.png)


The task images use admitted poses where available; a rejected diagnostic would be explicitly labeled. Parking collision validation is saved separately and conservatively retains the P06 held-tool proxy. Images are 1440×960 pixels. All renders use Blender Cycles CPU.


**Scope and scene decisions**

This study covers washing, assisted peeling/cutting and tool handling only. The T08 counter remains at z=0.850 m and y=0…0.60 m. The free slabs remain x=-1.80…-0.70 and -0.11…0.69 m; the stove at x=0.69…1.47 m remains a physical protected obstacle. No torso, mobile chassis, battery, humanoid arm, cooking or plating was retained. The sink and faucet are the original fixed geometry referenced by `inputs/prep_checker.py`, extracted read-only into this directory because its external model dependency was not included in inputs. The only slab correction aligns its right-hand edge with T08's exact x=-0.110 m.

Upper cabinets are solid obstacles at z=1.35…1.95 m, depth 0.37 m, over the left slab, main preparation slab and far-right slab. Their 0.60 m height and 0.37 m depth are METOD sizes; the selected worktop gap is 0.50 m, the manufacturer's stated minimum recommendation. These are declared representative cabinets, not surveyed measurements of a particular home. Cabinet placement leaves the sink and hob bays open. [IKEA METOD guide](https://www.ikea.com/gb/en/files/pdf/f8/4f/f84f4466/metod-cabinets-guide.pdf).

The closed cabinet volumes affect every arm. A conservative 600 mm door opening envelope affects the rail, carriages, mounting plates and cable carriers. Arms operate with doors closed; opening a door requires the validated parking state and a stopped/interlocked robot. Two representative socket/plug access volumes are declared at x=-0.90 and +0.15 m, y=0.56 m, z=1.01 m because T08 supplies no socket coordinates. They are obstacles in the check. The faucet includes the riser, stem and spout; its water outlet remains (-0.40, 0.44, 1.027) m. A site survey could change the socket and cabinet conclusions.

The 4.60 m horizontal beam runs x=-2.30…+2.30 m at y=0.575 m, with 4.24 m carriage travel. It has a 30×70 mm collision envelope and a declared 24 kg mass. Dedicated wall brackets at x=-1.50, -0.75, 0 and +0.55 m provide the sole allowed wall contacts; other rail geometry has 10 mm wall clearance. This beam is a concept envelope, not a selected section proven by FEA. Its long end overhangs allow unused arms to park at x=±2.12 m. The room must provide that extra side clearance beyond the 3.60 m counter. Wall/cabinet strength is not inferred from kitchen furniture.

Each independent carriage is 8 kg: 5 kg block, 1 kg stand-off bracket, 0.3 kg connecting cleat, 0.7 kg relieved flange adapter plate, and 1 kg moving cable/drive/brake allowance. The plate collision envelope is 140×140×18 mm for xArm, 180×180×18 mm for UR5e and 200×200×18 mm for FR3/AUBO, allowing their larger mounting footprints. These are mounting envelopes and mass budgets, not uniform solid plates or finished bolt-pattern drawings. Its prismatic axis is world X. Cable carriers include fixed tracks and moving loop envelopes and are robot parts in collision checking. Mains-powered AC controllers stay fixed outside the work envelope; arm power/communications run through the carriers. xArm's published supply is 100–240 V AC through its AC controller, and mounting is permitted in any direction. [UFACTORY technical specifications](https://docs.xarm.ufactory.cc/8.technical_specifications.html).

“Horizontal” maps the arm's base +Z axis forward, toward -Y. `down30` and `down60` tilt it 30°/60° below horizontal. `vertical` points +Z upward on a wall-supported shelf; `inverted` points it down. The hanging comparison has its mounting plane at z=1.250 m, 100 mm below the modeled cabinet underside; it is supported by the wall rail, not by the cabinet carcass. Only its inverted variant is literally hanging; other orientations at that elevation are mounting comparisons.

The custom end holder has a declared 1.2 kg mass, a 70×80×40 mm palm/adapter envelope, two 75×8×20 mm fingers and 90 mm maximum opening. The initial holder places its grasp 140 mm beyond the source flange; the additional compact refinement moves the jaw assembly 30 mm nearer the flange, for a 110 mm grasp extension, while keeping the palm geometry/COM fixed relative to the flange. Finger guides require internal clearance slots, as with ordinary parallel grippers; the reference intentionally exempts internal same-gripper contacts. It implements T08's positive keys and friction-pad requirements; its 150 N total normal force and keyed 150 N/15 Nm capacities remain the reference assumptions. This is a compact holder design budget, not a certified commercial gripper. In particular, it is not the native xArm gripper: that accessory's published maximum force is only 30 N. The nominal flange payload requirement is therefore 3.0+1.2=4.2 kg before any optional accessory added later.

**Sources and torque interpretation**

The model source manifest records exact commits and import files. UR5e, xArm7 and FR3 come from [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie); AUBO i5 comes from the [official AUBO description](https://github.com/AuboRobot/aubo_description); xArm6 comes from [UFACTORY's official xarm_ros description](https://github.com/xArm-Developer/xarm_ros). URDF conversion preserves the official origins, axes, joint limits, masses, inertias and collision STL. xArm6 expands the default older hardware description (`model_num=0`, `xarm6_type6_HT_BR2` inertias); its default collision geometry deliberately uses the visual-named STL paths specified by that official xacro. MuJoCo uses its usual convex collision representation for those meshes. These are source-model collision approximations, not a metrology scan or exact nonconvex CAD collision study.

| Repository | Recorded commit | Imported arm files |
|---|---|---|
| MuJoCo Menagerie | `f054586a8e90465d49ee5be15335c4a0c7f57caf` | `universal_robots_ur5e`, `ufactory_xarm7`, `franka_fr3` |
| AuboRobot/aubo_description | `47fa5e02fa873f27f7e812d31f31e3f4cf5e56b1` | `urdf/aubo_i5.urdf`, collision meshes |
| xArm-Developer/xarm_ros | `aad7e1611c9c46eb719045414394bfdd42dcb0f8` | xArm6 xacro, default kinematics YAML, `xarm6_type6_HT_BR2` inertial YAML |

Native xArm7 gripper geometry is removed and the common holder is attached to the flange. The demonstration-only 120 mm xArm7 pedestal offset is removed. Source joint limits and source collision shapes are otherwise retained. Source link body names receive an `arm` identifier so the unchanged reference floor-contact taxonomy recognizes every link as an arm. Visual-only meshes are omitted in numerical runs and restored for renders; they do not change inertias, joints or collision shapes. Actuator/controller dynamics are not used in a static IK/load study.

The old humanoid ceilings are never reused. FCI/URDF effort limits and peak motor ratings are not silently promoted to continuous joint ratings. The public data supports the following distinctions:

| Arm | Reference torque values, Nm | Meaning and limitation | Nominal 4.2 kg flange load |
|---|---|---|---|
| xArm6 | 64, 64, 32, 32, 12, 12 | Manufacturer-rated motor torque ×100:1 gearing, without overload multiplier; ideal output reference | Within published 5 kg payload |
| xArm7 | 64, 64, 32, 32, 32, 12, 12 | Same older-generation rated-motor derivation | Exceeds published 3.5 kg payload |
| UR5e | 150, 150, 150, 28, 28, 28 | Manufacturer staff's maximum values; diagnostic comparison only | Within published 5 kg payload |
| FR3 | 87, 87, 87, 87, 12, 12, 12 | FCI maximum values; diagnostic comparison only | Exceeds published 3 kg payload |
| AUBO i5 | Imported official URDF efforts | URDF effort limits, not established continuous ratings; diagnostic only | Within nominal 5 kg class |

For xArm6/7, the manufacturer's table identifies rated motor torques, transmission ratios and separate overload multipliers. The study uses rated torque times gear ratio, with no 2.55× overload benefit. Gearbox efficiency, output thermal limits and a continuous output-torque certification are unavailable in that table. Consequently, these are explicitly conditional engineering torque references, not a verified datasheet continuous-joint admission. An 85% efficiency sensitivity is reported separately, without changing the checker. [UFACTORY joint parameters](https://docs.supportarticle.ufactory.cc/support_articles/hardware/ufactory-joint-parameters.html).

UR maximum values are sourced from [manufacturer staff](https://forum.universal-robots.com/t/maximum-axis-speed-acceleration/13338). FR3 maximum values are from [Franka control parameters](https://support.franka.de/docs/control_parameters.html) and [official FR3 joint limits](https://github.com/frankarobotics/franka_ros/blob/develop/franka_description/robots/fr3/joint_limits.yaml). AUBO effort values come directly from its [official URDF](https://github.com/AuboRobot/aubo_description/blob/main/urdf/aubo_i5.urdf); its [manufacturer specification](https://aubocdn.aubo-robotics.cn/official_website/hardware/AUBO_Robotics_EN_202401_i5.pdf) gives 5 kg payload and ceiling/floor/wall installation. Rows for these arms are kinematic/load diagnostics; their numerical `FEASIBLE` verdict does not establish the user's continuous-torque requirement. Published payload classes likewise do not replace a load/COM diagram for the chosen holder. Nonselected FR3 orientations are mathematical comparisons rather than a claim of manufacturer authorization for every orientation.

**Checker preservation and audit**

`adapt_checker.py` creates the pluggable checker deterministically from the read-only input. `audit/checker.diff` is the complete unified diff and `audit/checker_ast.json` compares every original function. Forty-eight original functions are AST-identical, including all sixteen phase definitions, held-tool geometry, station construction, force/grip calculations, static torque calculation, `run_seed`, `run_phase`, and phase summarization. The seven changed functions have these robot-plumbing purposes:

Outside those functions, imports and model-path globals are replaced by `model.build` and `configure` so joint identities, limits and source torque references follow the chosen real arm. The legacy mobile-base CLI is disabled and its module description points to `run.py`, enforcing the user's two-worker limit while retaining the original legacy functions for the AST comparison. These entry-point and metadata changes introduce no phase acceptance rule.

| Function | Change and justification |
|---|---|
| `scene_tree` | Copy the selected robot template rather than load the removed humanoid model. Loose-station construction remains identical. |
| `Checker.bind_model` | Find the robot root through `rail_structure`, bind imported joint names and include a third held-tool prefix. All fixture identities and contact semantics remain. |
| `Checker.side` | Recognize R/L/C prefixes for imported arm bodies. |
| `Checker.forbidden` | Add only the dedicated wall bracket↔back-wall intended contact, as explicitly allowed by the task. Every threshold and other contact branch remains unchanged. |
| `Checker.floor_margin` | Report carriage travel margin because a floor footprint no longer exists. This is a diagnostic; it is not a new acceptance gate. |
| `Checker.initial` | Sample the active carriage and real arm joint limits; park unused arms through deterministic collision checking. No mobile-base or torso sample remains. |
| `Checker.solve` | Freeze carriages, jaws and unused arm joints in the IK QP and after each step. Remove the unnecessary left-arm parking target because its actual joints are frozen. Preserve the original tasks/costs, iteration count and pose acceptance. |

Two numerically locked, negligible-mass scalar coordinates (`anchor_lock`, `rail_lock`) are model plumbing. They separate rail/robot weld identities from world geometry so the reference parent/weld skip does not incorrectly exempt the rail from its environment. They stay frozen at zero and represent no added physical motion. Collision-generation margins are 10 mm, while geometric padding remains zero: a positive-gap contact must be generated before the reference code can enforce a 10 mm gap. Source exclusions are preserved; no broad arm/environment ACM exemption is added. Cabinet door masks implement the declared door access rule on infrastructure; physical closed cabinets still collide with all robot links.

The acceptance rules remain 5 mm/3° pose tolerance; 10 mm robot/environment and different-arm gaps; 5 mm gripper/held-tool environment gap; zero penetration for nonadjacent same-arm parts; reference parent/weld/ACM skips; prescribed nominal/check forces; μ=0.5, safety factor 1.5 and 150 N total grip normal force; keyed bearing and moment capacities unchanged. The reference admits nominal forces and reports check forces diagnostically. Those diagnostic loads are not turned into a new pass gate.

The T08 receiving-end +50 mm supports are used for P01/P03/P05 without moving the counter or entire tool deck. P11 uses the approved basket-height adjustment (bottom z=0.725 m); P14 keeps the bowl at x=0. The same adjustments apply to every candidate. In P11/P12, the input checker permits independently admitted process strokes to be paired by torque rank. The carriage stays frozen within each two-pose stroke; it may move between unrelated strokes. The reported feasible-seed counts retain exactly that input definition, and raw paired and per-stroke counts remain in the JSON.

`adapt_golden.py` creates a second full diff at `audit/golden.diff`. It replaces model/joint/root lookup and base sampling, freezes unused arm joints, and adds the same wall-mount exception. The exact golden holder sphere (65 mm radius), 80 mm work offset, 0.55 kg load, 200 mm stroke, 40/70/100 N feed reactions, +20 N up and ±10 N lateral remain. Its original station (0.45, 0.18, 0.865) m is retained as an additional golden proxy within the complete T08 fixture scene. It is not relocated to make the result easier. The original golden collision-success flag is retained; force-specific torque admission counts are additional reporting. Its torque and grasp-rotation functions are unchanged.

**Sampling, ranking and the third arm**

All 750 prescribed arm/height/orientation/stand-off/count combinations receive fixed infrastructure clearance screening. The numerical coarse sweep is a 150-design fractional factorial: all five arms, the three surviving elevations, all five orientations and both arm counts, with stand-offs distributed across orientations. It uses two seeds per phase/stroke and is a screening exercise, not a proof of infeasibility. The remaining unmeasured combinations are explicitly blank in the CSV rather than mislabeled as phase failures. Initial coarse carriage windows were ±0.55 m about the stroke's mean X, clipped at -1.90…+0.80 m. Saved IK poses were then rechecked against the physical adapter/cleat refinement; `audit/coarse_replay.json` records the changed verdicts.

Refinement expands active carriage samples to ±1.0 m about the mean stroke X, clipped to the actual -2.12…+2.12 m travel, and uses sixteen seeds. Two additional compact-holder entries and two additional parking entries supplement the original 750-grid design space. The final designs each use at least 96 seeds for every phase and for the golden check. Arm joint initial seeds cover the central half of each real joint range; IK can use the entire allowed range. The reference solver is a local IK method without collision avoidance, so a failed sample is evidence about that sample, not a proof that no solution exists. Unused-arm parking uses a deterministic full-range search with up to 400 candidates and is subsequently checked with the rest of the robot in every phase. Initial pilots picked the first collision-free parking candidate; the final parking refinement selects the candidate with the lowest static gravity-torque ratio.

The first complete 96-seed parking comparison admitted nine phases for both counts. It left L at the left rail end and C, if present, at the right end. Basket access needs a carriage beyond the left cabinet edge: a 140 mm mounting plate at this elevation requires X≤-1.88 m for 10 mm cabinet clearance. A second 240 mm carriage centered at -2.12 m requires the working carriage to stay X≥-1.87 m for 10 mm carriage clearance. Those left-side placement conditions do not overlap. Final two-arm parking moves L to +2.12 m, freeing the left end. Final three-arm parking retains L there and adds C at -2.12 m. This explains a specific single-rail crowding penalty; a longer rail or a separate parking rail could change it, but neither is admitted into the reported design without checking.

Ranking first compares phases with admitted poses, then worst best-phase torque ratio and reach/joint margins, then arm count and installation complexity. Payload-ineligible xArm7/FR3 and arms with only maximum/URDF torque data are separately marked. Cost ranking uses only relative complexity (extra arm/controller/carriage/cable track/drive/brake), not invented supplier prices. Public information does not support an installed system cost. A third arm can plausibly hold ingredients or permit parallel washing/cutting in a redesigned process, but no such force-sharing or scheduling benefit is admitted by the unchanged T08 definitions. The identical-pose replay distinguishes added-arm collision/park-gravity effects from different random samples.

The user's earlier humanoid-arm wall-rail result is 0/16; it is historical input, not a rerun here. A plausible mechanism is that hanging an upright humanoid upper body preserves shoulder offsets, torso bulk and elbow paths designed for a standing base, while constraining its position at the wall. Extra joints cannot remove collisions or supply missing reach at a downward tool pose. Independent industrial arms permit a different base orientation, stand-off and carriage position for each work stroke and omit that torso envelope. The current witnesses demonstrate the resulting improvement where reported; remaining cabinet, faucet, carriage and stored-tool collisions show why rail mounting alone does not guarantee all sixteen phases. This causal explanation is an engineering inference, not a claim that the historical failure log was inspected.

**Safety and commercial precedent**

The xArm manual states that its joint modules contain brakes and hold pose on power loss, and warns that releasing brakes requires support. It does not identify the brake mechanism as spring-applied for each gravity-loaded joint. That exact hardware requirement therefore remains unverified from public data, rather than being assumed from the word “cobot.” Every carriage drive is specified to have its own de-energize-to-apply spring brake; the model freezes rail motion but does not simulate or certify a brake. [UFACTORY safety manual](https://docs.xarm.ufactory.cc/1.safety.html).

The concept uses external person detection, monitored separation, a safety controller and a monitored controlled stop followed by power removal (Category 1/SS1). Proposed initial limits are 0.10 m/s carriage travel and 0.15 m/s tool motion, with no blade motion when a person enters the preparation envelope. These are design choices, not measured safe separation distances. Stop time, safety-rated arm interface, restart interlock, door interlock, spring-brake hardware, loss-of-power behavior and stopping load cases remain integration requirements. The unchanged quasistatic checker verifies none of those safety functions. Near a knife or mandoline, collaborative arm branding does not itself establish safe human contact. The manufacturer assigns complete-system risk assessment to the integrator. No supplier was contacted.

Moley publicly describes dexterous arms on a three-axis rail system, and Samsung describes Bot Chef as a six-DOF collaborative kitchen assistant. These precedents support fixed kitchen manipulators and assisted tools, but neither establishes that a single-axis back-wall rail passes T08. The useful lessons are to account for the whole installation, provide dedicated tool docking/fixtures, and reserve clear operating space. [Moley's technical overview](https://moleyrobotics.medium.com/moley-robotic-kitchen-has-launched-the-most-detailed-overview-of-its-innovative-technology-e194b848eac8), [Samsung technology showcase](https://news.samsung.com/global/get-a-glimpse-of-the-next-generation-innovations-on-display-at-samsungs-technology-showcase).

**Limits of the evidence**

The cooking research sets finished-product targets: carrot/potato slices 5±1 mm, bok choy lengths 40±10 mm and eight unpeeled tomato wedges. T08 evaluates key poses and prescribed forces for assisted preparation; it does not verify those food outcomes, continuous stroke clearance, grasp acquisition, tool exchange paths, carriage transitions, cycle time, water ingress or sanitation. Cooking/plating key poses do not expand this scope. A safe continuous-motion controller and a physical food-prep trial remain separate engineering work.

The host interruption left partial pilot runs. Only complete phase JSONs are used, and missing work was resumed. Abandoned geometry pilots are retained under `audit/coarse_v1…v3` and excluded from the ranking. Numerical runs use CPU only, at most two workers, a 1,140 s foreground chunk timeout and 1,900 MiB worker limit. The resumed numerical models omit inert visual meshes to avoid the earlier host memory exhaustion. Resource logs, raw seeds, exact q vectors, complete checker diffs, source commits and the delivered standalone scene make the conclusions reviewable. Rendering restores source visual geometry and exports the exact witness poses to Blender Cycles CPU; presentation hides only the opposite aisle wall/counter and transparent access envelopes, not checking obstacles.

The cable carriers are clearance and mass envelopes. Detailed chain routing, minimum bend radius, drainage and service access have not been validated. The sampled static load envelope is an input to mounting design, not a proof of the global worst load or structural capacity. `audit/final_verification.json` independently replays all 142 admitted key poses, including limits, original tolerances, contact/grip/torque gates and zero carriage movement. `audit/delivery.json` records final output size, image dimensions, source revisions and read-only input hashes.
