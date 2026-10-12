本轮继续现有厨房的柜下轨道方案，四种蔬菜的成品要求全部保留。新增 L36–L53 布局研究后，选定单 UR5e、单滑台、水平工具座的 L53。简化工艺共有 59 个机器人动作模板，完成 96 次起点搜索并经最终检查通过 42 个；内部路径通过 41/59，食材守恒的整餐连接仍为 0/110。停放快照通过，完整停放验收未通过，整餐备菜时间为 null。预算 339249.95 元，含一次 15% 预备金和一套 18000 元家用安全包。

这次按停止条件 (b) 交付：18 组新增布局及对应的可达性、固定障碍、末端几何或路径证据已记录。没有达到条件 (a)，也没有证明柜下轨道不可行。新计数不能与旧版 105 项直接比较：重复手工削皮被机器接口方案替代，但装夹、削皮循环、停机取料等未建模动作仍作为阻断事件保留。45/59 项完成了全部 96 次搜索；其余搜索不足或未尝试的失败项均标为未解决，不能当成不可达证明。历史 [v1](integrator_v1.md)、[v2](integrator_v2.md)、[v3](integrator_v3.md) 保留。

## Selected installation and unchanged acceptance

L53 has **one complete UR5e, one carriage and one wall lane**. The entire helper, its carriage and its chain were removed from the compiled model; no invisible parked helper is assumed. The full principal mounts at Y=0.500, Z=1.170 m, tilted 90°. The rail is at Z=1.285 m; the complete chain cover is centered at Y=0.3725, Z=1.2855 m. Only the first lane/chain entry is active when count=1. The full power track moves to Z=1.195 m. No portal, front legs, elevator, pallet, taller wall or wider wall is present. The original 3.7 m wall, 0.85 m counter, sink, stove exclusion and upper cabinets remain.

Acceptance remains 5 mm / 3°, PAD=0, 10 mm robot/environment and inter-arm gaps, ordinary 5 mm held/gripper/environment gaps, μ=0.5, SF=1.5, 150 N key force and 15 Nm key moment. **Every robot part, including fingers, uses 10 mm against full door sweeps.** Only named wall-bracket rear mating faces can touch the wall. Doors themselves are not tested against the person corridor. The copied R05 checker/planner/source assets remain unchanged; R07 adapters and their own derivatives contain the changes. [Binding decisions](../../DECISIONS.md), [active contact ledger](../../sim/r07/integrator/results/intended_contacts.json).

The fixed **GROHE Eurocube 13303000** wall spout replaces the tall deck mixer. Its public drawing gives 170 mm outlet projection, 60 mm square escutcheon and 8 mm mounting depth. The conservative complete 60 × 200 × 60 mm external cover includes the nose beyond the outlet axis; concealed connector, plumbing and the normally closed valve enclosure remain modeled. It is a full dimensional reservation, not OEM casting CAD. The wall connection is [-0.58, 0.6, 0.94] m. The falling-jet reference is a design point below the conservative cover, not a measured outlet offset. [Manufacturer-authored drawing](https://www.larochenigeria.com/shop/img/product-docs/Product35617_20220616.pdf), [buyable listing](https://www.oeg.net/en/grohe-universal-cube-bath-spout-for-wall-mounting-800020267). The retained [DFRobot FIT0498 valve](https://www.dfrobot.com/product-1530.html) needs potable-material, dry-enclosure, flow and shutoff qualification; electric commands do not need knob motions.

## Arm and appliance choices

| Candidate | Public capability | Decision |
|---|---|---|
| UR5e | 5 kg, 850 mm reach | Selected; full meshes/inertia, actual mounted rated-payload envelope, principal 3 kg plus 1.2 kg EOAT retained. |
| xArm6 | 5 kg nominal, 700 mm reach | Full model compared in L41 and earlier paired maps. Its long-offset payload limit with this EOAT does not qualify 3 kg + EOAT as principal. Optional capped helper adds clutter and was removed. |
| UR3e | 3 kg, 500 mm reach | Smaller helper candidate; cannot meet principal 3 kg plus positive EOAT. No invented reduced UR5e geometry. |

The [xArm manual](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf) and [UR3e specifications](https://www.universal-robots.com/products/ur3e/) support the comparisons. UR5e mounted payload-envelope and documented power-loss holding evidence are inherited; no continuous-torque publication requirement is reinstated. Rail braking remains de-energize-to-apply. Compiled mass is retained rather than rescaled to brochure nominal mass. Alternate JAKA/Elite/Dobot/AUBO candidates remain in the prior public-source screen; no new matched-model numerical pass is claimed for them.

The commodity screen considered **Sammic M-5**, **Starfrit Rotato Express**, **Nemco 55550-8**, retained **Breville BFP610**, R211 XL and HENDI 229200. [Research and dimension record](../../sim/r07/integrator/results/research_v4.json).

The [Sammic M-5](https://sammic.com/en/product/m-5) is 333 × 367 × 490 mm, 300 W, 15.5 kg, with 5 kg capacity and a 0–6 minute timer; the OEM explicitly includes carrots and potatoes. Its complete conservative box interferes with the left chain band, and the far-right bay has poorer reach. This rejects those layouts, not every possible exact M-5 casting placement. Its loading lid, interior and small-batch peeling depth/loss were not qualified.

The selected **Rotato Express 093209** concept occupies a complete **300 × 300 × 350 mm guarded design reservation** on the left counter. The [OEM product](https://www.starfrit.com/en/starfrit-electric-rotato-express) and [manual](https://www.starfrit.com/media/pdf/instrbooklet--User-manual-093209002BLCK-en2.pdf) describe the mechanism; the [supplier dimensions](https://www.odpbusiness.com/a/products/983762/Starfrit-Rotato-Express/) list 6 × 6 × 10.5 inches with ambiguous axis ordering. The reservation exceeds every listed dimension in any order. It is not matched OEM mechanism CAD and no access hole was invented. The OEM requires food longer than 140 mm to be halved: the 160 mm carrot therefore adds a guarded pre-cut and conserved-piece obligation. Lowering/raising the holder, setting cutter height, rocking food off the spike and removing eyes remain explicit events. Carrot suitability, peeling depth, gouging and yield remain unqualified. Four passing approach templates cannot establish those operations.

The full **BFP610** 395 × 295 × 395 mm reservation remains on the counter, shifted back 55 mm to improve the front-edge reserve. [OEM page](https://www.breville.com/en-nz/product/bfp610), [manual](https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf). It is a batch machine: motor stop, unplugging, lid removal, disc removal and bowl unloading are retained. It receives no R211 continuous-discharge credit. Exact interlock/pusher/chute geometry and feed force remain unqualified. The [Nemco eight-wedger](https://nemco.com/catalog/easy-wedger/) is 203.2 × 203.2 × 482.6 mm; exposed sharp manual operation would need a sourced actuator/guard interface. It was screened, not installed. The existing guarded secondary cutter remains for greens and tomato; its sourced loads were not lowered.

The retained below-counter solid named `m5_water_drain_service` is an unused conservative service reservation from the appliance screen, not an OEM Rotato drain assembly. Appliance covers reserve the full public dimensions, but the new peeler and processor interfaces lack matched mechanism geometry. This is an explicit qualification blocker, not permission to load through a solid cover.

## Layout evidence and search accounting

| Layout | Map clear/targets (R; L when present) | Complete 96-start strokes / passing | Fixed / endpoint obstructions | Main evidence |
|---|---|---:|---|---|
| L36 | R 140/252; L 140/252 | 0 / 0 | 18 fixed; 1 targets | [layout](../../sim/r07/integrator/results/layouts/L36.json) |
| L37 | R 128/252; L 138/252 | 0 / 0 | 18 fixed; 5 targets | [layout](../../sim/r07/integrator/results/layouts/L37.json) |
| L38 | R 143/300; L 153/300 | 0 / 0 | 16 fixed; 1 targets | [layout](../../sim/r07/integrator/results/layouts/L38.json) |
| L39 | R 0/300; L 157/300 | 0 / 0 | 16 fixed; 4 targets | [layout](../../sim/r07/integrator/results/layouts/L39.json) |
| L40 | R 132/300; L 151/300 | 0 / 0 | 16 fixed; 1 targets | [layout](../../sim/r07/integrator/results/layouts/L40.json) |
| L41 | R 159/300; L 160/300 | 0 / 0 | 16 fixed; 4 targets | [layout](../../sim/r07/integrator/results/layouts/L41.json) |
| L42 | not rerun | 0 / 0 | 17 fixed; 1 targets | [layout](../../sim/r07/integrator/results/layouts/L42.json) |
| L43 | not rerun | 1 / 1 | 0 fixed; 1 targets | [layout](../../sim/r07/integrator/results/layouts/L43.json) |
| L44 | R 158/300 | 1 / 1 | 0 fixed; 1 targets | [layout](../../sim/r07/integrator/results/layouts/L44.json) |
| L45 | R 158/300 reused proposal | 5 / 5 | 0 fixed; 0 targets | [layout](../../sim/r07/integrator/results/layouts/L45.json) |
| L46 | R 162/300 | 1 / 0 | 0 fixed; 0 targets | [layout](../../sim/r07/integrator/results/layouts/L46.json) |
| L47 | not rerun | 0 / 0 | 4 fixed; 12 targets | [layout](../../sim/r07/integrator/results/layouts/L47.json) |
| L48 | not rerun | 5 / 5 | 0 fixed; 12 targets | [layout](../../sim/r07/integrator/results/layouts/L48.json) |
| L49 | not rerun | 5 / 5 | 0 fixed; 12 targets | [layout](../../sim/r07/integrator/results/layouts/L49.json) |
| L50 | not rerun | 0 / 0 | 2 fixed; 0 targets | [layout](../../sim/r07/integrator/results/layouts/L50.json) |
| L51 | R 154/300 | 31 / 27 | 0 fixed; 0 targets | [layout](../../sim/r07/integrator/results/layouts/L51.json) |
| L52 | R 155/300 | 35 / 34 | 0 fixed; 0 targets | [layout](../../sim/r07/integrator/results/layouts/L52.json) |
| L53 | R 145/300 | 45 / 42 | 0 fixed; 0 targets | [layout](../../sim/r07/integrator/results/layouts/L53.json) |

Maps vary mount height, tilt, stand-off and carriage position over the counter, sink, faucet approaches and appliance openings. L36–L37 use the inherited 252 targets; later maps use 300, adding appliance openings. The common 216-grid subset is comparable. Maps omit movable fixtures and the opposite arm, and report Jacobian dexterity; final static, idle and motion admission restores the whole scene. A map miss is not an impossibility proof. L45 map reuse is labeled and supplies seeds only. [All iterations](../../sim/r07/integrator/results/iterations.csv), [layout evidence](../../sim/r07/integrator/results/layout_iterations_v4.json).

L42 removed the helper. L43 moved bowls and tools away from brackets; L44 grew wall plates and moved full beam/tie assemblies. L45 corrected inactive raw-food placement to the actual relocated lands. L46 moved full tool docks away from behind the processor. L47 rotated complete docks but hit the power track; L48/L49 cleared that hardware yet overlapped raw greens with terminal geometry. L50 raised the complete horizontal docks and enlarged stands, but a measured 1 mm post/track gap rejected the layout. L51 moved the assemblies 40 mm forward, leaving 41 mm there, without shrinking solids. The exact fixed and terminal certificates permit stopping searches on those rejected layouts; they do not prove the architecture impossible.

Selected search accounting: **42/59 admitted**, **45/59 completed 96 starts**. Every unresolved start has 20 s available; local convergence, full-reference rejection, positive termination and budget exhaustion are recorded separately. Carriage coordinates, map seeds, earlier witnesses as proposals, restarts and staging are included. Eight additional-margin starts per stroke seek 10 mm extra clearance; final gates never change. Remaining partial/unattempted indices are [10, 12, 13, 15, 28, 30, 31, 33, 34, 35, 39, 43, 46, 47, 52, 53, 54]. Fresh full-scene replay, branch and source hashes are in [fresh admission](../../sim/r07/integrator/results/fresh_admission.json).

| Unresolved template | Starts completed | Best failed pose error (mm / degrees) | Leading rejected pair |
|---|---:|---|---|
| 10: V4_10__bowl_load | 0 | no failed pose recorded | see full reference / unresolved |
| 12: V4_12__load_slicer | 0 | no failed pose recorded | see full reference / unresolved |
| 13: V4_13__withdraw | 50 | 1.67 / 8.53 | see full reference / unresolved |
| 15: V4_15__deliver | 9 | 31.02 / 22.94 | upper_cabinet_0_piece1 ↔ R_geom_17; upper_cabinet_0_piece1 ↔ R_geom_21 |
| 28: V4_28__bowl_load | 0 | no failed pose recorded | see full reference / unresolved |
| 30: V4_30__load_slicer | 0 | no failed pose recorded | see full reference / unresolved |
| 31: V4_31__withdraw | 0 | no failed pose recorded | see full reference / unresolved |
| 33: V4_33__rinse_pieces | 0 | no failed pose recorded | see full reference / unresolved |
| 34: V4_34__deliver | 0 | no failed pose recorded | see full reference / unresolved |
| 35: V4_35__Coarse_wash_bok_choy | 43 | 21.71 / 11.81 | cable_chain_cover_0 ↔ R_geom_21; cable_chain_cover_0 ↔ R_geom_26 |
| 39: V4_39__soak_bok_choy | 0 | no failed pose recorded | see full reference / unresolved |
| 43: V4_43__Drain_greens_without_wringing | 0 | no failed pose recorded | see full reference / unresolved |
| 46: V4_46__Deliver_greens_next-step_bowl | 0 | no failed pose recorded | see full reference / unresolved |
| 47: V4_47__Wash_unpeeled_tomato | 96 | 21.72 / 11.80 | cable_chain_cover_0 ↔ R_geom_21; cable_chain_cover_0 ↔ R_geom_26 |
| 52: V4_52__Withdraw_for_guarded_eight-wedge_cycle | 96 | 0.00 / 0.00 | secondary_closed_lid ↔ R_finger_minus; secondary_closed_lid ↔ R_finger_plus |
| 53: V4_53__Deliver_tomato_next-step_bowl | 0 | no failed pose recorded | see full reference / unresolved |
| 54: V4_54__Inspect_four_outputs_and_present_bowls | 96 | 24.42 / 7.90 | upper_cabinet_0_piece1 ↔ R_geom_10; upper_cabinet_0_piece1 ↔ R_geom_11 |

The table describes the best retained failed candidate, not an exhaustive reachability certificate. Partial or unattempted searches and a failed numerical solve remain unresolved. Full per-start terminations, pose errors and contact pairs are retained rather than converted into geometric-impossibility claims.

## Motion, conserved food and parking

The 160 mm carrot needs two separate holder cycles after prehalving; the ledger explicitly includes first-half removal, second-half loading/peeling and collection of both halves. These are blocked two-piece conservation/interface obligations, not a single cycle silently credited for the whole carrot. The whole-food aggregate stays unchanged in the unexecuted initial scene until that physical partition is qualified.

Among the admitted static templates, the maximum check-wrench rated-envelope ratio is 0.6937; the minimum grip margin is 1.8420. These apply only to the admitted subset, not the unresolved strokes or new appliance mechanisms. Every pose retains the public ranges and full force/moment alternatives.

**41/59 isolated internal paths pass; 0/110 conserved-meal connections pass.** The proposed recipe expands to 111 repeated strokes and 206 explicit handoff, appliance, timer and return events. The one-owner ledger is continuous and retains 0.57 kg of whole input material, but no unverified owner update is executed. Food splitting, scraps and edible yield need real geometric bindings; all four whole raw objects remain in the initial persistent model. [Motion](../../sim/r07/integrator/results/motion.json), [conserved sequence](../../sim/r07/integrator/results/state_sequence.json), [persistent model status](../../sim/r07/integrator/results/persistent_model.json).

Local connection diagnostics admit 3 transitions, at template indices [18, 3, 44]. These connect checked templates only where the complete scene and held-object signature agree. A periodic-angle continuation is credited only after the entire downstream path is rebased within public joint ranges and replayed; its saved bundle remains separate from the original path. This does not establish a complete vegetable or execute any missing initial acquisition, appliance or transfer event.

Every attempted path edge receives at least 65 s with RRT restarts, staging and shortcutting. Accepted paths undergo ≤4 mm model-derived point-displacement sampling, joint-range, load-envelope and grip replay. A missing OEM actuator or ownership binding is reported as blocked, not as a fictitious 65-second RRT failure. Working contact is absent from non-working paths; contact windows retain their own kind, object and support and the ≤50 mm normal/insertion rule. The rotated dock test rejects the back, side and wrong object. Door tests reject 5, 7.5, 9 and 9.9 mm and accept the unchanged 10 mm gate. [Policy regression](../../sim/r07/integrator/results/contact_policy_regression.json), [door regression](../../sim/r07/integrator/results/door_gate_regression_v4.json), [rotated faces](../../sim/r07/integrator/results/rotated_contact_regression_v4.json).

The populated park snapshot is **PASS** with all output contents and stored tools. Fold/unfold is **FAIL**; complete idle remains **FAIL** because a connected meal-end return has not been executed. Direct periodic-joint-rebased folding uses three 65-second attempts. Six alternative park searches retain their rejected snapshots and every attempted 65-second route; any explicit staged searches are also retained in the idle record. A free endpoint or a checked prefix is not a full fold/unfold. Passing is **not applicable** with one actual carriage. [Idle evidence](../../sim/r07/integrator/results/idle.json).

The largest conservative supported human work rectangle in the front strip is **0.0464 m²**, XY bounds [-0.705, -0.125, 0.0, 0.08] m, with appliances left in place. This is only a 580 × 80 mm rim, not a useful clear chopping area. The computation uses 5 mm cells, complete projected clutter, 10 mm expansion and the actual counter/rim support; the open sink is excluded. The full 3.6 × 0.23 m front strip is robot-free only in the parked snapshot, not necessarily empty of appliances or food fixtures. [Counter and folded-arm envelopes](../../sim/r07/integrator/results/counter_and_arm_envelopes.json).

## Robustness, timing and cost

The margin histogram drove L52 and L53. L52 moved complete bowls 8 mm forward and lowered the arm mount 5 mm; this removed the fixed 16 mm bowl/bracket bottleneck but did not lower the carriage attached to the rail. L53 therefore lowers the complete active rail/carriage and power track 5 mm together, retaining their full sizes and arm mount Z=1.170 m. The carriage top is Z=1.3275 m, giving 22.5 mm cabinet-bottom clearance. The parked arm still has only 6.167 mm extra wall clearance. Actual final margins below govern; design targets are not treated as measured outcomes.

| Static category | Minimum reserve above gate (mm) | Median of pose minima (mm) | Pose minima ≥10 mm extra |
|---|---:|---:|---:|
| arm_arm_or_frame | 0.723 | 10.495 | 97.6% |
| self | 0.765 | 3.901 | 0.0% |
| robot_environment | 0.965 | 10.000 | 75.0% |
| held_gripper_environment | 0.609 | 19.558 | 71.4% |

Distributions use each pose/state’s worst eligible pair per category, so thousands of distant pairs cannot hide a narrow approach. Self-clearance has its own zero gate and is reported separately. Intended contact sentinels are excluded. Full convex refinement covers all 84 admitted static poses and 2,564 internal-path states. Path robot/environment and held/gripper/environment minima have at least 10 mm extra reserve in 74.3% and 79.1% of samples respectively, but their minima are numerically at the gates: the peeler approach nears a cabinet and the wash-pad return nears its own dock. Raw floating-point residuals down to −5.33e−8 mm are retained in the JSON, not hidden. Those approaches lack a build allowance. No buildable robust meal is certified: rigid-model gaps do not cover rail sag, bracket/anchor compliance, calibration, cable behavior or produce variation. [Static and executed-path reserve distributions](../../sim/r07/integrator/results/clearance.json).

Executed full-meal **prep_min=null**. The sum of checked isolated path durations is 3.487 min, which is not a meal makespan. Timing applies home-tier rail 0.1 m/s, joints 0.35 rad/s and all-point 0.05 m/s with acceleration limits to saved paths. Required 600 s bok-choy soak, three conservative fresh potato rinses and 20–30 s drain remain. Peeler cycle, batch slicing, fill/drain and inspection durations are unqualified, so none is invented to complete a schedule. [Schedule](../../sim/r07/integrator/results/schedule.json).

Planning cost: base **CNY 294999.96**, one 15% reserve **44249.99**, total **339249.95**. The helper and one EOAT allowance were removed; the rail allowance was conservatively retained. Peeler, mechanical guard and stand allowances were added. The single 18000 CNY safety package includes interlocks, presence sensing, E-stop and RCD/PE; rail brakes stay in the transport line. These are allowances, not current quotations, and there is no cheapest passing configuration. [Itemized costs](../../sim/r07/integrator/results/costs.csv).

## Render evidence and limits

All views use the actual unscaled compiled solids and saved joint states, CPU rendering, maximum 1500 pixels. The 24-frame strip is a freshly checked **isolated simulated path**, not a meal video. Hidden door-sweep/access overlays remain in collision checks.

![Overview](../../sim/r07/integrator/renders/overview.png)

![Parked, doors open](../../sim/r07/integrator/renders/parked_doors_open.png)

![Under-cabinet band](../../sim/r07/integrator/renders/under_cabinet_band.png)

![Single-carriage passing not applicable](../../sim/r07/integrator/renders/passing.png)

![24 checked local frames](../../sim/r07/integrator/renders/executed_local_strip.png)

All four finished products retain cook_ref requirements: carrot/potato peel and slice tolerances and terminal pieces; potato eyes and starch rinses; every basal bok-choy crease, root/stalk/section dimensions and soak; tomato skin, hard-core removal and eight intact wedges; ≥98% edible transfer and separate outputs. All inherited process-force models remain unchanged. Commodity marketing provides no force, cleanliness or product-quality qualification. No purchasing, supplier contact or physical bench tests occurred. [Artifact and resource audit](../../sim/r07/integrator/results/delivery_audit.json).
