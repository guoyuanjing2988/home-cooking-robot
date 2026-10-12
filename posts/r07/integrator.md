本轮针对进料空间、收料碗和折叠路径继续修改柜下轨道方案。新增 12 组布局研究，最终选择 L101。静态动作通过 **45/59**，内部路径通过 **43/59**；全部 110 个相邻动作连接都实际运行了规划器，但执行完成的整餐连接仍为 **0/110**。停放快照通过，折叠／展开未通过，完整闲置验收未通过。没有完成从装料到输出碗的完整蔬菜流程；整餐时间为 null，规划预算 **344884.95 元**。

本轮修复了抓取窗口只信任名称的漏洞：权限现在绑定当前场景登记的真实对象、抓取面、完整部件及其坐标。错误对象、错误支持面、伪造坐标或部件、过期几何和非工作路径上的工作许可均有负向测试。前移全部收料碗会与削皮机和其他工位相交，因此未采用；后续保留后排碗体，转动完整提手，并根据实测相交量前移完整削皮工位。未缩小机器人、食物、碗或设备，也未放宽验收门槛。

按停止条件 **(b)** 交付：至少六轮后续布局已有可复查的可达性和障碍证据；不是证明柜下轨道不可行。最终 59/59 个动作各完成 96 次起点搜索，未解决起点分配 20 秒。历史 [v1](integrator_v1.md)、[v2](integrator_v2.md)、[v3](integrator_v3.md)、[v4](integrator_v4.md)、[v5](integrator_v5.md)、[v6](integrator_v6.md) 保留；第六版代码和交付快照另存于 history/v6。

## Selected geometry and cutting interface

L101 uses one full UR5e on one wall-mounted lane. Mount Y=0.520, Z=1.153 m, tilt 90°. The rail and complete cable-chain covers stay behind the Y=0.23 m cabinet front and below Z=1.35 m. The existing 3.7 m wall, 0.85 m counter, sink, stove exclusion and upper cabinets remain. There is no portal, front leg, elevator, pallet, wall extension or increased room height. One arm avoids a second shoulder and carriage crossing; the passing render is labelled not applicable.

| Arm | Evidence and decision |
|---|---|
| UR5e principal | Public 5 kg / 850 mm; full inherited OEM solids/inertias, 151 mm base reservation and ±160° elbow. Retains 3 kg plus 1.2 kg EOAT under the actual-mount rated-payload envelope. |
| xArm6 | Full inherited alternative model and earlier reach studies. Its offset-payload curve does not qualify this 3 kg plus EOAT principal configuration; an additional capped helper consumes the parked band. |
| UR3e helper | Public 3 kg / 500 mm: a possible task-capped helper, but insufficient for 3 kg plus nonzero EOAT as principal. No scaled surrogate is used. |

Sources: [UR5e specification](https://www.universal-robots.com/manuals/EN/HTML/SW5_23/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm), [xArm manual](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf), [UR3e](https://www.universal-robots.com/products/ur3e/). Arm power-loss holding uses the binding home-tier documentary rule; the rail needs a de-energize-to-apply brake. Archived arm CAD is not claimed to be an exact current hardware revision.

The selected cutting-interface study moves the complete **395 × 295 × 395 mm BFP610 reservation** forward, with a 50 mm front setback. Its feed approaches occupy the open front strip during operation. Trials with lower side grasps failed palm/appliance clearance; L98–L101 restore the original full-food feed height. Full terminal-body support-extrema checks include templates 43, 46 and 53; remaining arm/fixture collisions still require IK and path checks.

The [current AU product page](https://www.breville.com/en-au/product/bfp610) labels dimensions 39.5 × 19.7 × 23 cm and a 120 mm chute; this does not establish a matched CAD revision for the retained conservative reservation. The [A23 manual](https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf) requires its supplied pusher and correct interlocks, stopping/unplugging for disassembly, and cautions against bench-edge placement. The 50 mm setback is a layout decision, not a demonstrated stability qualification. Exact cavity, pusher, lid, removable bowl, controls and supervised-operation interfaces remain unresolved. No shrinking or hole cut into the reservation is used to manufacture a pass.

A [manual OXO Chef’s Mandoline 2.0](https://www.oxo.com/more-oxo/chef-s-mandoline-slicer-2-0.html) was reconsidered: the published envelope is 406.4 × 177.8 × 158.75 mm with 0.5 mm setting increments. A guarded horizontal holder and the retained sourced cutting forces would require a different complete mechanism and robot operation. It was not silently substituted into top-feed templates. [Source review and limits](../../sim/r07/integrator/source_review_v7.json).

The rear bowl centers remain at their original positions; the complete tomato bowl rotates 90° for a side approach. Existing full bails articulate 45° toward the front and receive full pins/stops, 40 g added modeled mass per bowl and a CNY 1,000 mechanical allowance. The geometry regression checks all original solids, including each shell/collar under its declared rigid transform. L96 exposed two 6.155 mm bail/peeler-drive penetrations; L97 translates the complete peeler and its task targets 20 mm forward. This is a custom mechanism, with the unchanged 150 N / 15 Nm key/lock proof still required before manufacture.

L90–L95 front-bowl layouts failed packing. L96–L97 restored rear shells and tested 75° bails and lower food grasps. L98 restored feed height. L99–L100 moved the mount wallward, but a convex full-carriage certificate found only 4.475 mm between the base and beam. L101 lowers the complete base to Z=1.1535 m and raises the full beam to Z=1.285 m: its full-travel lower-bound gap is 20.975 mm. An initial large-cutoff native-distance diagnostic produced spurious values; those discarded files are preserved and replaced by the inherited convex checker’s certified bounds. None received acceptance credit.

The full GROHE Eurocube 13303000 wall spout remains below the carriage band. Its 60 × 200 × 60 mm conservative cover includes the published 170 mm projection; electrical water control removes knob manipulation. The source casting, outlet/jet, drainage, plumbing and splash qualification remain limits. [GROHE](https://www.grohe-mena.com/en_cy/eurocube-bath-spout-13303000.html).

An independent functional check rejects the forward-shifted colander rinse poses 33 and 43: their upright mouth centers are 190.263 mm from the vertical jet, versus a 119 mm usable opening radius. Even the most favorable 5 mm / 3° displacement is insufficient. They require a different wash approach or water-tool arrangement; a geometric static/path pass would not establish washing. No spray dispersion or successful rinse is invented. [Jet/alignment evidence](../../sim/r07/integrator/results/wash_alignment_v7.json).

Rotato remains removed. The custom guarded peeler retains the complete tool, guards, guide and sourced 63 N tangential / 7.5 N normal design loads. The [P16-200-256-12-P](https://www.actuonix.com/p16-200-256-12-p) supports controller operation; its [datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf) gives 200 mm stroke, 150 N at 3.4 mm/s and 20% duty. The separate guide must carry the load above the actuator’s 4 N lateral allowance. The 2,823.529 s per-root cycle is a component-data design allowance, not measured peeling performance. All inherited force models remain unchanged; they include sizing proxies, not measured appliance forces.

## Iterations and statics

Empty-EOAT reach maps include the fixed kitchen and full rail/mount/chain, with carriage optimization and dexterity. They omit movable fixtures, so a clear map sample is only a placement proposal. Full-target tolerance obstruction certificates and stored-bowl packing probes expose the fixtures separately. A failed finite search does not prove the architecture impossible.

Selection prioritizes zero stored-bowl penetrations and a legal full-travel base/beam gap over raw reach-map count. L101 has 163/300 clear samples and two target-level obstruction certificates. It is the final tested candidate, not a globally optimal or qualified installation. Greens delivery intersects the peeler open lid; the tomato handle intersects the outlet-access reservation even throughout the allowed target tolerance.

| Layout | Clear map samples | Replayed old proposals | Target obstruction certificates | Stored-bowl intersections |
|---|---:|---:|---:|---:|
| L90 | 178/300 | 37/59 | 3 | 97 |
| L91 | 175/300 | 33/59 | 15 | 103 |
| L92 | 181/300 | 33/59 | 17 | 103 |
| L93 | 173/300 | 33/59 | 17 | 87 |
| L94 | 164/300 | 33/59 | 19 | 87 |
| L95 | 173/300 | 33/59 | 19 | 87 |
| L96 | 176/300 | 47/59 | 8 | 2 |
| L97 | 167/300 | 43/59 | 8 | 0 |
| L98 | 174/300 | 43/59 | 5 | 0 |
| L99 | 0/96 | 0/59 | — | 0 |
| L100 | 0/24 | 0/59 | — | 0 |
| L101 | 163/300 | 0/59 | 2 | 0 |

[Iteration evidence](../../sim/r07/integrator/results/layout_iterations_v7.json); [every numerical start and bounded run](../../sim/r07/integrator/results/iterations.csv); [reach/dexterity map](../../sim/r07/integrator/renders/reachability_study.png).

The selected geometry completes 96 starts on every template, with 20 s available per unresolved start, full-range carriage optimization, map/staging seeds and collision-aware solvers. Positive branches use independent perturbations and unchanged final replay. Extra-clearance optimization seeks 10 mm above the gates; immobile close pairs are recorded as layout problems. Result: **45/59 statics**, **43/59 internal paths**. Remaining static indices: `[6, 10, 12, 13, 15, 24, 28, 30, 31, 33, 34, 43, 46, 53]`. [Fresh admission](../../sim/r07/integrator/results/fresh_admission.json), [phase summary](../../sim/r07/integrator/results/phase_summary.json).

The final layout does not improve the previous 47/59 static count: cleaning templates 6 and 24 also fail after the mount change. Template 6's retained compromise has 5.851 mm / 8.739° error. Template 24 reaches all four targets within 0.493 mm / 0.199°, but the full reference finds shoulder/spoon-dock interference, including 2.101 mm penetration. Carrot feed 12 reaches 0.0477 mm / 0.00147° while striking the secondary cutter guards. These distinguish reach, fixture clearance and full-scene admission; no failed search is promoted to a geometric impossibility claim.

## Contact, persistent state and paths

Acceptance stays 5 mm / 3°, PAD=0, 10 mm robot/environment and arm/arm, ordinary 5 mm gripper/held/environment, wet μ=0.5, SF=1.5, and 150 N / 15 Nm key capacity. Only named wall-bracket mating faces may touch the wall. Support/working windows have explicit kinds and own identities, straight travel ≤50 mm, and normal gaps after disengagement. No working permission is granted to a non-working transfer.

All 111 expanded robot stroke instances have an internal-path evidence mapping. Identical zero-roll repeats reuse their checked template; all 20 changed washing rolls receive separate full-budget attempts and unchanged full-geometry replay, with 2/20 passing. These checks do not inherit a 96-start static claim and remain isolated scenes, not persistent meal execution. The ordinary 59-template count is unchanged.

The new finger-grasp policy binds each permission to the compiled live world registry: object identity, its actual registered grasp faces, full part names, permitted fingers, normal/closing axes and TCP frame must match. Actual object-part world frames are checked to reject stale registries. Genuine-carrot permission passes; foreign object/support, nonexistent identities, forged frame/parts/fingers/normal, enlarged window, working kind and an XML scene without the live registry reject. [Executable negative probes](../../sim/r07/integrator/results/grasp_identity_regression_v7.json).

Food-only transformations remain transactional and mass-conserving inside their own declared station regions. Full input solids and bulk output/scrap extrema must be contained; remote input, partial outside input, wrong support, held food, overcapacity, bulk grasp and binding teleport reject. Container movement and actual lid/pusher/guard manipulation cannot be abstracted. The existing BFP region is a declared internal cover, not qualified OEM bowl CAD. A food pose above the appliance cannot become an inside-bowl batch through a name change. [State regression](../../sim/r07/integrator/results/state_model_regression_v7.json).

Every one of **110 connections** runs the planner with ≥60 s per leg (65 s configured), restarts, staging bias and shortcutting. Accepted paths get full geometry, payload/load/grip and ≤4 mm point-displacement replay. There are **25 geometric connection passes** and **0 conditionally complete diagnostics**. These are not execution credit after a failed prefix: the conserved meal remains at its initial state, with **0 executed connections** and no complete product. All four cook_ref products and the 0.57 kg food ledger remain unchanged. [Per-connection results](../../sim/r07/integrator/results/motion.json), [state sequence](../../sim/r07/integrator/results/state_sequence.json), [blockers](../../sim/r07/integrator/results/connection_summary_v7.json).

Summed connection planner time is 92.397 min, against 120.250 min of allocated leg budgets; endpoint IK and other verification work are additional. Successful direct proposals may finish early. This is compute effort, not a meal preparation timeline.

## Folding, clearances and counter access

During operation and fold/unfold, full closed leaves and cabinet bodies are obstacles; neither opening-sweep family is present. At park, every robot part, including fingers, uses 10 mm against full opening sweeps and must clear the front strip and person corridor. The doors themselves are not checked against the corridor. Five door sensors and presence-pause logic are included in the single home-safety package.

Park snapshot: **True**. Fold/unfold: **False**. Prospective meal-end return: **False**. Full idle: **False**. New attempts include closed/nearly closed jaw states, carriage-first moves, working stages and alternative park poses, all checked against full geometry. Initial raw-food deployment and prospective completed-food return are separate models; no prospective state is relabelled an executed meal. [Idle evidence](../../sim/r07/integrator/results/idle.json).

Additional Cartesian staging targets extend into the open front strip at 1.20 m and 1.50 m, with front-facing and downward tool orientations, optional carriage alignment, and full 65 s planning for each leg. The higher targets test an approach above the 1.245 m processor top. Before deployment the park uses equivalent joint-angle branches nearest the working pose; all full-geometry frames agree within 9.44e-16. This is a configuration choice, not an executed encoder reset. Accepted fold/unfold/return endpoints must match the exact recorded final park state.

Four higher-stage proposals originally exhausted their 60 s independent replay allowance. These were resumed with 240 s per replay, retaining the same geometry, path and gates; any remaining leg receives 65 s planning. The continuations complete 5 independent leg replays, with 0/4 complete routes. Search proposals alone receive no acceptance credit. [Continuation evidence](../../sim/r07/integrator/results/front_replay_continuation_summary_v7.json).

All four resumed routes reach their staging poses but exhaust a further 65 s search on the final leg. The two fold routes repeatedly encounter the full BFP610 reservation; the return routes encounter the tomato bowl/collar and counter/finger clearance. These are sampled path blockers, not global impossibility certificates. The earlier 0.138 mm self-penetration is not accepted or masked by a relaxed self-contact rule.

| Checked path category | Minimum extra reserve (mm) | 5th percentile (mm) | Fraction ≥10 mm extra |
|---|---:|---:|---:|
| self | 0.00451236 | 3.80882 | 0.0% |
| robot_environment | 0.0641044 | 0.83393 | 76.4% |
| held_gripper_environment | -1.37465e-07 | 2.50063 | 73.8% |
| arm_arm_or_frame | 10.975 | 10.975 | 100.0% |

These are per-state worst-pair reserves, not averages diluted by distant parts. Convex lower-bound refinement saturates at the 10 mm extra objective; tiny numerical clearance is not buildable tolerance. Raw signed roundoff remains visible. No installation robustness claim is made. [Clearance distributions](../../sim/r07/integrator/results/clearance.json).

For the reviewer's specific stroke 49 concern, minimum robot/environment extra reserve is now 0.996055 mm at static poses and 0.173238 mm along its checked path. Held/gripper minima are 0.5 mm and 0.5 mm respectively. These remain below the 10 mm extra objective.

With appliances and stored objects in place, conservative free supported counter area is **0.24035 m²**; **0.18210 m²** lies in the front strip. Its largest clear rectangle is **0.05040 m²**. The 5 mm grid excludes sink openings and full object projections with 10 mm expansion. This is not an idle acceptance gate or ergonomic certification. No unexecuted appliance stow is credited. [Counter-area plot](../../sim/r07/integrator/renders/counter_free_area.png).

## Timing, cost and reproducibility

Verified meal preparation time is **null**. The admitted isolated internal paths total **346.477 s**, using home-tier rail/joint/all-point speed and acceleration limits; their sum is not a connected meal timeline. The separate 600 s greens soak, 30 s potato drain, three fresh-water rinses, component-derived peeler duration and unknown appliance/water timings remain explicit. [Schedule](../../sim/r07/integrator/results/schedule.json).

Admitted additional changed-roll paths have a separate modeled duration sum of 44.731 s. Their individual timings and clearance distributions are retained; neither this diagnostic sum nor the base-template sum establishes a recipe makespan.

Base planning allowance: CNY 299899.96; exactly one 15% reserve: CNY 44984.99; total **CNY 344884.95**. Exactly one CNY 18,000 household safety package includes the CNY 600 door-sensor allocation. Bowl locks are added once. These are planning allowances, not supplier quotes or a cheapest-passing design. No purchase, supplier contact or physical testing occurred. [Cost ledger](../../sim/r07/integrator/results/costs.csv).

The copied R05 checker/planner/distance/envelope source and inherited assets are hash-audited without upstream edits. Numerical runs use four shared OS-locked slots, CPU only, a 1,900 MiB process-tree limit and foreground chunks under 20 minutes. Every run has a timeout and resource record; the final audit separates artifact fidelity from task success. [Delivery audit](../../sim/r07/integrator/results/delivery_audit.json).

To stay below 3 GB, historical v1 and v2 render-source JSONs were losslessly ZIP-archived after individual SHA-256 verification; their manifests preserve exact restoration paths. Historical posts, images, results and code remain. New render scenes share content-addressed full meshes with verified hashes; their geometry is not decimated.

## Renders

All images are ≤1600 px. The frame strip contains 24 sampled states from a fully replayed **isolated internal path**, honestly labelled as not a connected meal. No imagined vegetable completion or arm passing is rendered.

[Overview](../../sim/r07/integrator/renders/overview.png)

[Parked with doors open](../../sim/r07/integrator/renders/parked_doors_open.png)

[Under-cabinet band](../../sim/r07/integrator/renders/under_cabinet_band.png)

[Single lane; passing not applicable](../../sim/r07/integrator/renders/passing.png)

[24 checked local-path frames](../../sim/r07/integrator/renders/executed_local_strip.png)
