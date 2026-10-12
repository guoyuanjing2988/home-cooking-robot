本轮继续原厨房的柜下轨道方案，保留胡萝卜、土豆、小白菜和番茄的全部成品要求。新增 6 组有实际搜索证据的布局／抓取迭代，最终检查 47/59 个静态动作模板通过，内部路径 46/59 通过。全部 110 个相邻动作连接都实际运行了规划器；几何路径通过 25 个，满足当前连接附加条件的独立诊断通过 0 个，但没有形成从装料到输出碗的完整蔬菜流程，整餐连接执行计数仍为 0/110。停放快照通过，折叠／展开未通过，完整闲置验收未通过。整餐时间为 null，预算 343734.95 元。

按停止条件 (b) 交付：至少六轮后续布局研究已有可复查证据；未达到条件 (a)，也没有证明柜下轨道不可行。59/59 个最终动作问题完成 96 次起点搜索，每个未解决起点有 20 秒预算。Rotato 已从当前模型和预算中删除，改为公开支持自动控制的 P16 驱动固定削皮工位。设备内部食物变化按新决定守恒记账；容器、工具、食物入口和盖板不能靠状态切换跳过真实动作。历史 [v1](integrator_v1.md)、[v2](integrator_v2.md)、[v3](integrator_v3.md)、[v4](integrator_v4.md)、[v5](integrator_v5.md) 保留。

Selected candidate for full checking: **L84, one complete UR5e, one carriage, one wall lane**. The arm base is Y=0.500, Z=1.160 m at 90° mounting tilt. Rail Z=1.275 m; full cable-chain cover Y=0.3825, Z=1.2855 m. The single lane removes the second shoulder and passing conflict; passing is not applicable. The existing 3.7 m wall, 0.85 m counter, sink, stove exclusion and upper cabinets remain. No portal, front legs, elevator, pallet, wall extension or taller kitchen is used. Inactive helper configuration fields are historical metadata: no helper solids exist in the compiled model.

Acceptance remains 5 mm / 3°, PAD=0, 10 mm robot/environment and arm/arm, ordinary 5 mm gripper/held/environment, μ=0.5, SF=1.5, and 150 N / 15 Nm key capacity. **Parked robot parts, including gripper fingers, use 10 mm against full door sweeps. Operating/folding/unfolding models instead include five full closed leaves and cabinet bodies at normal gaps; sweep covers are absent.** Only named bracket mating faces may touch the wall. Doors themselves are not tested against the corridor. Working-contact permission is absent from all non-working connections. Each support/grasp window identifies its own object, support and kind and ends within 50 mm. [Binding decisions](../../DECISIONS.md).

The full **GROHE Eurocube 13303000** wall spout stays below the carriage band at [-0.58, 0.6, 0.94] m. The 60 × 200 × 60 mm complete external reservation exceeds the public 170 mm outlet projection and includes the escutcheon/nose; concealed plumbing and valve reservations remain. It is a conservative full dimensional cover, not exact casting CAD. [Manufacturer drawing](https://www.larochenigeria.com/shop/img/product-docs/Product35617_20220616.pdf), [buyable listing](https://www.oeg.net/en/grohe-universal-cube-bath-spout-for-wall-mounting-800020267). The modeled electric valve removes knob manipulation; it does not replace a checked wash approach.

| Arm option | Public capability and model | Decision |
|---|---|---|
| UR5e | 5 kg, 850 mm; full inherited OEM solids/inertias | Principal retains 3 kg+1.2 kg EOAT. Actual mount payload envelope; selected. |
| xArm6 | 5 kg nominal, 700 mm; inherited full-model maps | Long-offset payload curve does not qualify this 3 kg+EOAT principal setup. A capped helper adds shoulder/chain clutter. |
| UR3e | 3 kg, 500 mm; public specification screen | Could be a smaller helper, but cannot carry3 kg plus nonzero EOAT as principal. Not numerically substituted with scaled UR5e. |

The [UR5e datasheet](https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf) provides the 5 kg payload curve through approximately 350 mm CoG offset and permits any mounting orientation. The current [SW5.23 specification](https://www.universal-robots.com/manuals/EN/HTML/SW5_23/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm) is conservatively covered by a 151 mm base reservation and ±160° elbow limit in these new searches. Archived solids/inertias are retained, rather than claiming a perfect current-revision CAD match. [xArm manual](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf), [UR3e](https://www.universal-robots.com/products/ur3e/). Home-tier arm power-loss holding evidence and de-energize-to-apply rail braking remain the design basis.

**Rotato is rejected**, because its manual forbids programmable-device operation. The replacement is a **custom guarded linear peeling station**, not a claimed turnkey commodity peeler: the existing full peeling tool and unchanged 63 N tangential/7.5 N normal process forces are retained. A buyable **Actuonix P16-200-256-12-P** drives a guided stroke. Its 200 mm travel and 247 mm closed hole spacing fit a full 480 ×50 ×50 mm drive/guide cover. Separate guide bearings take the radial load, since the actuator 200 mm variant allows only 4 N side load. Full guards, a 360 ×200 ×6 mm lid, handle, hinge and scrap floor remain modeled. The recipe and food-quality assumption do not certify the custom holder, guard sweep or mechanism.

The [P16 product](https://www.actuonix.com/p16-200-256-12-p) and [OEM datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf) specify 12 V, 300 N maximum force, 500 N static/backdrive holding, and 150 N at 3.4 mm/s. The datasheet expressly allows automatic position control with DPDT relay/H-bridge or LAC control. This addresses the Rotato programming prohibition. Six 160 mm out-and-return passes at 3.4 mm/s, respecting the 20% duty limit, give a **2,823.53 s design allowance per root** including cooling. This is derived from actuator data, not a measured peeling cycle; blade indexing and quality remain declared design assumptions. The inherited force evidence is retained, including the [robotic peeling research](https://arxiv.org/abs/2404.06570).

The full **Breville BFP610**395 ×295 ×395 mm reservation fits below the 1.35 m cabinet bottom when on the 0.85 m counter. It is a batch processor. Its [OEM manual](https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf) requires ordinary controls and safe stopped/unplugged bowl, lid and disc handling; external-timer operation is not used. Those full mechanical interfaces remain physical obligations. The manual does not give a qualified per-batch time for these exact roots, so that time remains null. The [Santos48](https://www.santos.fr/media/ftp/sales_leaflets/EN_english/SANTOS_48_leaflet_EN.pdf) continuous cutter was screened and rejected here because its published 520 mm height crosses the cabinet bottom. No 350 mm substitute was invented. The original R211 is not installed beneath a cabinet.

New search evidence:

The current [BFP610 product page](https://www.breville.com/en-au/product/bfp610) labels39.5 ×19.7 ×23 cm as W×D×H and advertises a 120 mm chute; the linked A23 manual also describes a 14 cm wide chute. The retained395 ×295 ×395 mm model is a larger conservative exterior reservation, not a claimed exact regional CAD revision. It has not been shrunk to resolve collisions. The internal1.92 L bowl subregion is explicitly unqualified. [Source assessment](../../sim/r07/integrator/results/research_v6.json).

A scope defect was found during this continuation: L74–L83 excluded the new idle sweep covers but still retained the inherited cabinet_door_sweep_* boxes during operation. The initial regression missed that family. Those studies and the interrupted connection searches are retained as over-constrained history and are not counted as corrected-scope evidence. L84–L89 remove both swept-volume families from operation while preserving full closed leaves and cabinet bodies. The new regression explicitly checks both families. [Correction record](../../sim/r07/integrator/audit/v6_door_scope_correction.json).

| Iteration | Mount height / tilt / stand-off | Reach-map clear targets |96-start problems complete / pass | Change |
|---|---|---:|---:|---|
| [L84](../../sim/r07/integrator/results/layouts/L84.json) | 1.160 m /90° /Y0.500 | 163/300 | 59 /47 | Complete closed-door scope correction; Corrected closed-door motion scope; identical full appliances and mounts. |
| [L85](../../sim/r07/integrator/results/layouts/L85.json) | 1.160 m /90° /Y0.500 | 163/300 | 0 /0 | Complete closed-door scope correction; Full BFP reservation and insertion targets move 12mm right, retaining stove gap. |
| [L86](../../sim/r07/integrator/results/layouts/L86.json) | 1.160 m /90° /Y0.500 | 159/300 | 0 /0 | Complete closed-door scope correction; Full processor moves20mm rearward to open parked wrist corridor. |
| [L87](../../sim/r07/integrator/results/layouts/L87.json) | 1.160 m /90° /Y0.500 | 168/300 | 0 /0 | Complete closed-door scope correction; Combined12mm right/15mm rearward processor move; full solids retained. |
| [L88](../../sim/r07/integrator/results/layouts/L88.json) | 1.160 m /90° /Y0.500 | 166/300 | 0 /0 | Complete closed-door scope correction; Move complete secondary station35mm left/30mm forward to separate processor and guard approaches. |
| [L89](../../sim/r07/integrator/results/layouts/L89.json) | 1.160 m /90° /Y0.500 | 156/300 | 0 /0 | Complete closed-door scope correction; Add20mm forward full tool-dock relocation, away from carriage and shoulder. |

L84 uses the fully corrected closed-door operating model. L85 moves the full processor12 mm in X; L86 moves it20 mm rearward; L87 combines12 mm X and 15 mm rearward; L88 also moves the secondary station35 mm left and 30 mm forward; L89 additionally moves full tool docks 20 mm forward. Each receives a fresh59-template old-branch screen, populated park check and full 65 s folding attempts. No screen replay receives inherited96-start credit. The earlier full-lid stowage, lower feed approach, locked-bail and whole-bowl yaw trials remain historical, not passing replacements. These finite studies identify retained-layout blockers; they do not establish architectural impossibility. [Iteration log](../../sim/r07/integrator/results/iterations.csv), [layout evidence](../../sim/r07/integrator/results/layout_iterations_v6.json).

The selected layout is chosen from fresh full geometry evidence. Preserved v5 working-stroke lifts remain part of the loaded working strokes, while all free paths strip working-contact permission. New collision-aware proposals use a 13-position fixed-carriage grid, global/map/staging restarts and a 10 mm extra-clearance objective on responsive pairs. Unresponsive fixed pairs are logged as layout issues; acceptance thresholds are unchanged.

Rail loads go to the named back-wall brackets. The counter-level wash-pad and spoon posts visible in the model are full tool docks. They remain physical obstacles and are among the most frequent connection endpoint blockers; the retained model does not assume tools can float in storage.

The historical L82 bowl-bail geometry regression verifies every original solid dimension, unchanged bowl/collar world poses and 16 added full locking-pin/stop solids. This is a custom mechanical proposal, not certified hardware. It is not installed or charged in the selected configuration. [Bail validation](../../sim/r07/integrator/results/bail_geometry_validation_v6.json).

Final static admission: **47/59**. Carriage, joint branches, map/staging seeds, restarts and eight extra-clearance seeds are used. Every positive needs 96 completed starts plus fresh full reference replay. A numerical local minimum or exhausted search is an unresolved configuration, not proof of geometric impossibility. [Fresh admission](../../sim/r07/integrator/results/fresh_admission.json).

Every one of the 59 templates receives an internal-path attempt. The 12 failed static templates use retained failed endpoints and 20 s proposals for missing endpoints, with full 65 s path diagnostics and no static admission credit.

Static admission concerns robot templates. Expanded persistent scenes retain all vessels and the actual conditional food locations, so a template endpoint can fail there. Each frozen endpoint currently uses one retained branch; joint endpoint/path optimization may improve connectivity. Failed finite searches do not prove the rail concept impossible.

The earlier L74 potato-wash withdrawal received an additional extra10 mm clearance-objective retry and still failed under that historical geometry. Current internal-path counts use only the selected corrected-scope layout. A free RRT route is not substituted for a specified Cartesian working stroke.

The current L84 potato-wash withdrawal also received a separate clearance-aware Cartesian continuation retry: FAIL. Its original path record, actual prior rejection and new search policy are preserved. The accepted first two edges were retained; the final edge was searched again at the unchanged gate. [Current withdrawal record](../../sim/r07/integrator/results/motion_v6/L84/internal_17.json).

| Unresolved stroke | Completed starts | Best retained error mm / degrees | Leading blocker |
|---|---:|---|---|
|10 V4_10__bowl_load|96|21.13 / 19.53|R_geom_21 ↔ linear_peeler_drive; R_geom_21 ↔ linear_peeler_drive|
|12 V4_12__load_slicer|96|0.00 / 0.00|R_geom_5 ↔ secondary_back_guard; R_geom_5 ↔ secondary_closed_lid|
|13 V4_13__withdraw|96|4.46 / 9.84|pose/orientation local minimum|
|15 V4_15__deliver|96|19.62 / 19.95|R_geom_21 ↔ linear_peeler_drive; R_geom_21 ↔ linear_peeler_drive|
|28 V4_28__bowl_load|96|51.54 / 9.31|R_geom_11 ↔ staged_raw_leafy_greens; R_geom_11 ↔ staged_raw_leafy_greens|
|30 V4_30__load_slicer|96|9.74 / 4.70|R_geom_5 ↔ secondary_back_guard; R_geom_5 ↔ secondary_closed_lid|
|31 V4_31__withdraw|96|4.45 / 9.84|pose/orientation local minimum|
|33 V4_33__rinse_pieces|96|8.25 / 8.15|greens_crease_land ↔ R_held_colander_shell_wall1; greens_crease_land ↔ R_held_colander_shell_wall1|
|34 V4_34__deliver|96|51.54 / 9.31|R_geom_11 ↔ staged_raw_leafy_greens; R_geom_11 ↔ staged_raw_leafy_greens|
|43 V4_43__Drain_greens_without_wringing|96|8.57 / 8.08|greens_crease_land ↔ R_held_colander_shell_wall1; greens_crease_land ↔ R_held_colander_shell_wall1|
|46 V4_46__Deliver_greens_next-step_bowl|96|23.36 / 0.63|dock_wash_pad_post ↔ R_mount_bracket; dock_wash_pad_post ↔ R_mount_bracket|
|53 V4_53__Deliver_tomato_next-step_bowl|96|0.50 / 0.00|R_geom_5 ↔ bfp610_complete_envelope; R_geom_10 ↔ bfp610_complete_envelope|

Admitted statics: maximum rated-envelope check-load ratio **0.7285**; minimum grip margin **1.8420**. The force models, finished products, tool definitions and acceptance dictionary match the inherited baseline. These ratios do not qualify rejected strokes.

**All 110 connections actually ran**. Each leg receives 65 s, 12 s RRT restarts, full-range carriage search, staging poses and up to 16 shortcuts; an early valid direct path may finish sooner. Staging includes admitted working configurations and carriage-first alternatives. Successful proposals undergo≤4 mm point-displacement replay, public joint-range, rated-envelope and grip checks. Per-connection files save exact populated MJCF hashes, endpoint blockers, runtime, bindings and required events. [Motion index](../../sim/r07/integrator/results/motion.json), [full connection records](../../sim/r07/integrator/results/connections_v6/L84/).

The persistent registry retains all four foods, four full bowls, full tools, the cassette and colander. Food-only transformations conserve 0.57 kg, with explicit edible/scrap partitions and beds sized as mass/(density×packing). Density/packing and yield are declared proxies, not geometry fitted to pass. Root outputs use 1030 kg/m³ and 0.55 packing; greens 1000/0.20; tomato 1000/0.60. A transformation cannot run on held food or at an unrelated support. Grasp binding rejects a 1 mm teleport and a second simultaneous object. Bulk output is not used as a smaller directly grasped object: such a conditional proposal retains the full original touched geometry and is not credited. [State regression](../../sim/r07/integrator/results/state_model_regression_v6.json).

The expanded containment regression also retains earlier peel scrap at its original station, puts new cutting scrap inside its own cutting container, rejects unknown transformations and rejects a new bulk batch in an occupied container. Station-local scraps have distinct object identities and their masses sum to the conserved scrap ledger. These checks prevent a transformation from silently transferring waste across the kitchen.

Each connection leg retains its pre-motion and post-check state. A passing carried-object leg updates the conditional object pose from the actual final joint-state FK; a rejected leg leaves that recorded pose unchanged. The audit independently reconstructs that FK from the saved full model. These local state updates do not commit a later conditional scenario as an executed meal.

Free transfers remove working-contact permissions and working wrench, while retaining payload inertia at 0.3 m/s² with SF1.5 along all six signed Cartesian axes. The actual attached mass is used in rated-envelope and grip replay; removing a process force does not remove the carried load.

Containment is transactional and geometric: the full food input must lie in its declared station region, and every output solid must fit its own interior before the mass ledger changes. Tests reject the reviewer’s [9,9,9] position, old z=1.375 m BFP bed, overcapacity, unrelated support, held food and invalid attachment changes, with rollback. BFP slice beds now occupy a station-local160 ×120 ×100 mm (1.92 L) bowl region entirely inside the unchanged full exterior. **That internal region is a declared engineering model, not an OEM-dimensioned cavity; actual cavity/access qualification remains open.** Scrap is contained in separate tray cells. A conditional secondary-lid relocation preserves its complete geometry and remains an unexecuted physical obligation.

There are **25 geometric connection passes** and **0 conditional passes after modeled binding requirements**, but **zero executed conserved-meal connections**. Later records describe explicit conditional scenarios after earlier failed transitions. Required full-food loading, lids/guards/pushers and container transfers are not silently executed by an appliance transformation. The source state and conditional assumptions are saved; the committed meal ledger stays at its initial state. Unknown appliance durations and unexecuted mechanical interfaces prevent finished-product credit. This is an actual planning result with remaining implementation/geometry blockers, not the old blanket `planner_ran=false` outcome. [State sequence](../../sim/r07/integrator/results/state_sequence.json), [persistent model](../../sim/r07/integrator/results/persistent_model.json).

The connection sweep used 96.29 actual planner minutes across 120.25 allocated leg-minutes. Status totals: {'GEOMETRIC_PLANNER_REJECTION': 81, 'POSE_OR_PHYSICAL_BINDING_REJECTED_AFTER_PLANNING': 29}. Frequent endpoint pairs: R_mount_bracket / dock_eye_core_spoon_post: 43; R_mount_arm / dock_eye_core_spoon_post: 43; R_mount_bracket / dock_wash_pad_post: 40; R_mount_arm / dock_wash_pad_post: 39; R_held_wash_pad_contact / dock_wash_pad_face: 36; R_gripper_palm / persistent_food_leafy_greens_food: 31; R_held_food / faucet_v3_fixed_spout_full_envelope: 28; R_geom_5 / linear_peeler_open_lid: 27. These frequencies identify layout and binding problems; they are not proof that all other layouts fail. [Connection diagnostics](../../sim/r07/integrator/results/connection_summary_v6.json).

85 conditional connection scenarios include a rejected preceding containment transaction. In the retained processor insertion proposals, the full food remains above the processor reservation, so the new input-containment check rejects the transformation and preserves its geometry and mass. Passing the containment regression does not qualify an actual processor loading or transformation cycle.

Parking snapshot: **PASS**. Fold/unfold: **FAIL**. Direct, carriage-first, working-stage and alternative park goals receive the full budget. Fold and final return use a prospective completed-food scene; explicit unfolding uses the initial raw-food and full stored-object registry and checks the parked pose against that environment. The same parked robot configuration retains the full-sweep/front-strip certificate. A separate return starts from the final water-off stroke. No prospective return is labeled an executed meal-end return. Only the park snapshot checks full door sweeps at 10 mm for every robot part. Motion checks full closed leaves and cabinet bodies with normal gaps. [Idle and route records](../../sim/r07/integrator/results/idle.json).

The conservative free supported counter area is **0.2558 m² overall** and **0.1976 m² in the front strip**. The largest front-strip rectangle is 0.0504 m², XY bounds [-0.7500000000000224, -0.12000000000003574, 0.0, 0.08] m; the largest whole-counter rectangle is 0.0504 m². These are separate metrics on 5 mm cells, excluding the open sink and full appliance/stored-object/parked-robot projections with 10 mm expansion through z=0.855–1.35 m. Connected idle remains unqualified. L81 tests cheap full-lid stowage but loses retained static branches, so it is not substituted without qualification. [Counter data](../../sim/r07/integrator/results/counter_area_v6.json), [counter plot](../../sim/r07/integrator/renders/counter_free_area.png).

| Static minimum-clearance category | Minimum extra mm | Median extra mm | Samples≥10 mm extra |
|---|---:|---:|---:|
|robot_environment|0.775|10.000|64.9%|
|arm_arm_or_frame|7.617|10.495|97.4%|
|self|0.536|3.901|0.0%|
|held_gripper_environment|1.064|17.581|71.9%|

| Checked path category | Minimum extra mm | Median extra mm | States ≥10 mm extra |
|---|---:|---:|---:|
| robot_environment | 0.074916 | 10.000 | 68.0% |
| arm_arm_or_frame | 7.855234 | 10.495 | 99.6% |
| self | 0.408808 | 3.901 | 0.0% |
| held_gripper_environment | -0.000000 | 20.038 | 76.8% |

Reserve refinement complete: True; evaluated {'static': 114, 'path': 4095}. Distributions use the worst eligible pair per pose/state, retaining raw signed lower bounds. Stroke49 received96 new starts and fresh internal replay after closed leaves invalidated its old branch. Its improvement is measured from the new path records, never inferred from endpoint reserve alone. Near-gate results remain inadequate for a build allowance; the 10 mm extra-clearance objective is not a relaxed gate or a robustness pass. [Clearance evidence](../../sim/r07/integrator/results/clearance.json).

For stroke49 specifically, the refined minimum reserve above the robot/environment gate is 0.074916 mm; above the held/gripper/environment gate it is 1.063765 mm. These are whole-path minima; the requested10 mm extra build allowance is still not established.

Across all accepted internal paths, the smallest signed held/gripper reserve is -3.395539e-08 mm. The raw value near the numerical boundary is retained, rather than rounded into a claimed build allowance. The unchanged reference checker admitted these paths; their marginal clearances remain a robustness failure.

**prep_min=null** because no meal was executed. Checked isolated motions total 5.783 min under rail0.1 m/s, joints0.35 rad/s, all-point0.05 m/s and rest-to-rest acceleration limits. That sum is not a meal makespan. Additive process obligations include the 600 s bok-choy soak, three fresh potato rinses, 30 s drain and data-derived peeler cycles. Missing exact batch/water times stay null. [Schedule](../../sim/r07/integrator/results/schedule.json).

Planning cost: base **CNY298899.96**, one 15% reserve **44834.99**, total **343734.95**. Exactly one 18000 CNY home safety package covers presence sensing, E-stop, RCD/PE and interlock/control, including600 CNY allocated to five door-open sensors and pause logic; the peeler guard line is mechanical fabrication only. Actuator/guide/guard amounts are engineering allowances, not quotes or currency conversions. There is no cheapest passing configuration. [Costs](../../sim/r07/integrator/results/costs.csv).

The renders show the actual saved full model and≤1600 px CPU output. The 24 frames come from a freshly checked isolated simulation path and are explicitly **not a connected meal**. Park-sweep overlays are hidden for display but checked in idle; operation uses the full closed leaves.

![Overview](../../sim/r07/integrator/renders/overview.png)

![Parked, all doors open](../../sim/r07/integrator/renders/parked_doors_open.png)

![Under-cabinet band](../../sim/r07/integrator/renders/under_cabinet_band.png)

![Passing not applicable](../../sim/r07/integrator/renders/passing.png)

![24 checked local frames](../../sim/r07/integrator/renders/executed_local_strip.png)

![Reach/dexterity study](../../sim/r07/integrator/renders/reachability_study.png)

All four cook_ref product specifications remain: carrot/potato peeling, trimming, slice tolerances and terminal pieces; potato eye removal and starch rinsing; every basal bok-choy crease, root/stalk/section limits and soaking; tomato skin, hard-core removal and eight wedges;≥98% edible transfer to separate bowls. Food quality is a declared assumption for later validation. No purchase, supplier contact or bench test occurred. Copied R05 code/source hashes, bounded foreground resource logs and artifact provenance are checked in the [delivery audit](../../sim/r07/integrator/results/delivery_audit.json).

V6 numeric runs use a four-slot OS-held file-lock semaphore, CPU only, at most1900 MiB per process tree and bounded foreground chunks below20 minutes. Slot start/end intervals and every resource result are auditable. The earlier v5 overlap incident stays in preserved history; it is not relabelled as a new incident or erased. [Resource/audit evidence](../../sim/r07/integrator/results/delivery_audit.json).

One connection chunk reached its 1060 s child timeout during a long attempt. Completed rows were retained, no orphan numerical worker was found, and the missing connection was resumed with its full budget. New chunks leave more time for final replay before the outer deadline. The failed process result is preserved in the iteration log. [Recovery record](../../sim/r07/integrator/audit/v6_connection_timeout_recovery.json).

The band close-up exceeded its initial150 s image-render limit. It was retried with a 300 s image allowance in disjoint CPU batches under the same four-worker and 1120 s outer limits; geometry and acceptance stayed unchanged. [Render recovery](../../sim/r07/integrator/audit/v6_render_timeout_recovery.json).
