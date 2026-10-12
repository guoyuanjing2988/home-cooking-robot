本轮对多轨多臂与新工具完成了仿真检查，但没有得到可投用的方案。保留两条独立直轨、两只 xArm6 和固定压切机作为最简单的后续整改候选；机械臂各用一条拖链，拓扑允许在不同轨道改变前后次序，无需换轨，但全行程交会检查未通过。新流程共 27 个逻辑阶段、36 个展开实例，每个展开实例的每笔动作至少 96 个种子。按原检查器，完整阶段通过 0/27；旧单轨基线复算通过 10/16。两者的力矩结果仍是有条件的目录参考值，连续输出力矩和关节弹簧制动器证据未闭合，严格整机合格数为 0。

轨道插座用于固定电器和工具电源，按真实目录截面建成机器人实体；移动机械臂保留独立拖链和固定干区控制箱。整套含安装、安全集成和 15% 预留的预算为 493,292.45 元，是工程估算。文献载荷对应慢速切削，规划串行时间约 101.7 分钟，资源排程估算约 95.0 分钟；动作链失败，所以目前没有经验证的备菜总时间，也不能宣称已验证清洗与切割并行。所有失败、示意时间和未确认项均保留，图中的失败姿态有明确标注。

English engineering record — 2026-10-07

The result is a **negative concept screen**, not an approved home robot. The full-check candidate has two xArm6 arms, two separate X lanes, inverted mounts at z=1.230 m, y=+0.120/-0.400 m, 0.520 m lane pitch, and 110 mm flange-to-grasp extension. No battery, torso, mobile base or humanoid arm is present. A short fixed guarded cutter receives root, greens and purchased eight-sector tomato cartridges; arms load/unload and wash/peel. The XZ alternative did not earn its extra mechanism in the sparse screen, so the lower-complexity X-only candidate receives the full check.

The 1,296-entry [sweep.csv](../../sim/r02/concept2/results/sweep.csv) records every fixed-infrastructure gate and marks the sparse IK subset explicitly. It is not 1,296 fully sampled robot comparisons. Dimensions cover 2/3/4 arms; plain X, XZ and end-transfer/conductor options; three rail heights, two lateral pitches, two front stand-offs, two mount orientations, and six same/mixed arm combinations. A 440 mm pitch cannot pass the 495 mm carriage arch at the same X. Three/four full arms consume the aisle or opposite-counter volume; no task or person-access benefit is established. Source arms/limits/inertias are reused unchanged. FR3 and xArm7 are helper comparisons only (<=0.5 kg task payload); they do not meet 3 kg plus the retained gripper allocation.

Selection minimizes transport mechanisms among nominal-payload-eligible candidates after the sparse trials failed to establish an admitted phase. It is a candidate for investigating failures, not a winner hidden by a weighted score. Alternative unconventional simplifications—moving baskets/cassettes rather than arms, powered supported peeling, rotating output bowls, and one strong arm plus a narrow product conveyor—are recorded in [engineering.md](../../sim/r02/concept2/engineering.md). They require a new process contract and force evidence before substitution.

Height pruning is explicit: all 432 layouts at 1.200 m fail the fixed-envelope gate around the cutter/rail geometry; all 432 at 1.280 m fail around cabinets/door envelopes; 420 of 432 at 1.230 m are fixed-envelope clear. Consequently the current sparse IK comparison uses the 1.230 m survivors. It checks 13 configurations with 2 seeds per stroke and 7 representative instances; this screening resolution is disclosed and is not a reliable ranking of small feasibility differences.

**Full process check and old-phase justification**

Each Q stage passes only when every expanded ingredient instance and every constituent stroke has an admitted seed. The count is the minimum independently admitted stroke pool, preserving the original R01 composite-stroke semantics; it does not prove motion between strokes. A diagnostic torque is from rejected IK-complete poses and never a feasible witness. Design-margin counts additionally require process_v2 check-force torque <=1 and grip margin >=1. Binding hardware admission is zero because the inspected public tables do not establish continuous joint-output ratings.

| Stage | Required operation | Replaces old phase(s) | Feasible seeds | Best admitted ratio | Rejected-pose ratio |
|---|---|---|---:|---:|---:|
|Q01|Stage vessels and start water with produce parked|added requirement|0/96|—|0.318|
|Q02|Pick and wash each root|P01, P02, P07, P08|0/96|—|0.432|
|Q03|Load dirty peel support and clamp|P03|0/96|—|0.318|
|Q04|Acquire retained peeler|P15|0/96|—|0.318|
|Q05|Peel all root surfaces with supported indexing|P04, P09|0/96|—|0.359|
|Q06|Remove eyes and local blemishes|P09|0/96|—|0.318|
|Q07|Collect peels and clean dirty work support|P04, P09|0/96|—|0.318|
|Q08|Rinse peeled root and park before water off|P02, P08|0/96|—|0.318|
|Q09|Install clean root cartridge and cooking bowl|P05, P14|0/96|—|0.335|
|Q10|Guarded end trim and5 mm slicing|P06, P10|0/96|—|0.318|
|Q11|Potato pieces starch rinse and drain|P14|0/96|—|0.318|
|Q12|Deliver separate root bowls|P14|0/96|—|0.415|
|Q13|Coarse wash greens|P11|0/96|—|0.318|
|Q14|Trim greens root disk in guarded dirty cassette|P12|0/96|—|0.318|
|Q15|Expose each loose basal crease|P11|0/96|—|0.456|
|Q16|Soak, rub each crease and fresh-water rinse|P11|0/96|—|0.448|
|Q17|Drain greens without spinner|P11|0/96|—|0.318|
|Q18|Split stalks wider than15 mm|P12|0/96|—|0.318|
|Q19|Arrange low bundle and cut40 mm sections|P12|0/96|—|0.318|
|Q20|Deliver greens bowl|P14|0/96|—|0.318|
|Q21|Wash tomato in supporting cup|added requirement|0/96|—|0.442|
|Q22|Remove hard stem core in supported cradle|added requirement|0/96|—|0.335|
|Q23|Install8-sector cartridge, bowl and tomato|P13|0/96|—|0.318|
|Q24|Powered8-wedge press, arms detached|P13|0/96|—|0.318|
|Q25|Recover and deliver tomato wedges|P14|0/96|—|0.318|
|Q26|Inspect all finished products and present cooking containers|P14|0/96|—|0.415|
|Q27|Clean, drain and dock all tools; water off|P15, P16|0/96|—|0.318|

Q02–Q12 expand separately for carrot and potato. Q06 applies to potato; Q11 includes all required potato starch rinses/drain. Q13–Q20 expose, clean and section bok choy; Q21–Q25 preserve tomato skin/core removal and produce eight wedges. Q26 inspects/presents four separate next-cooking-step containers; Q27 cleans/docks and stops water. Powered cycles replace arm-driven P06/P10/P12/P13, while Q09/Q11/Q12/Q20/Q25 replace P14 tipping with the cooking bowl directly under discharge. P15/P16 tool handling is retained/replaced by covered cartridges and peeler acquisition. Additional water-off, peel-waste, starch removal and cleanliness phases close omissions in the old coarse P list. Finished dimensions, last edible slices/stubs, washed inner creases, attached tomato pulp and >=98% edible transfer are retained as requirements. They are not measured by rigid-body IK.

Detailed instance/stroke counts and raw q/error/contact/force witnesses are in [best.json](../../sim/r02/concept2/results/best.json), [stroke_summary.json](../../sim/r02/concept2/results/stroke_summary.json) and `results/final_v4/c0684/Q*.json`. Every stroke runs all 96 seeds with the original 600-iteration Mink solve; all carriage coordinates and unused joints are frozen during the stroke. End-transfer coarse reruns sample discrete lane assignment and freeze it; no transfer-latch or powered-collector approval is implied. The literal original indexed rinse_basket work-face expansion was restored after an adapter overwrite was found. All saved seed poses were rechecked in final_v4 with identical q/errors and unchanged zero-moment force ratios, and audit/rescore_final_v4.json records the source/output hashes and changed contacts. The handed-off eye/core 0.262/0.524 Nm free moment is also applied through the angular Jacobian and keyed-grip moment demand, with no new force value or grip rule. No extra work-face permission was introduced. The circular C06 shorthand in process_v2 is replaced by the delivered CAD rectangular 260 × 230 × 80 mm shell for both held and supported states; the saved IK witnesses are checked against this box union with retained mass/COM/key interface. Revised object ownership ensures C06 is not simultaneously held and duplicated at its support; the earlier interrupted/unrevised diagnostics remain separately stored and are not counted as final checks.

| Old phase | Feasible seeds | Best ratio | Pool |
|---|---:|---:|---|
|P01|0/96|0.230|IK_diagnostic|
|P02|4/96|0.334|feasible|
|P03|4/96|0.297|feasible|
|P04|4/96|0.388|feasible|
|P05|6/96|0.317|feasible|
|P06|3/96|0.850|feasible|
|P07|2/96|0.422|feasible|
|P08|5/96|0.340|feasible|
|P09|3/96|0.408|feasible|
|P10|1/96|0.806|feasible|
|P11|2/96|0.214|feasible|
|P12|0/96|0.163|IK_diagnostic|
|P13|0/96|0.123|IK_diagnostic|
|P14|0/96|0.394|IK_diagnostic|
|P15|0/96|0.208|IK_diagnostic|
|P16|0/96|0.281|IK_diagnostic|

The baseline is freshly rerun with the exact R01 best configuration, including right-end parking and its original raised receiving supports/P11 adjustment. It retains the old tools, contacts, forces and sampling. Separate early `results/baseline` trials used opposite-end parking and are not this comparison.

**Dominant failure evidence**

- north_wall / R_link2_collision: 1365 rejected contact records (not distinct seeds).

- rail_guide_0_-1_piece5 / R_gripper_palm: 1336 rejected contact records (not distinct seeds).

- north_wall / R_link3_collision: 1210 rejected contact records (not distinct seeds).

- cell_guard_back / R_link2_collision: 1120 rejected contact records (not distinct seeds).

- front_header / R_link_base_collision: 1028 rejected contact records (not distinct seeds).

- rail_guide_0_-1_piece5 / R_link5_collision: 989 rejected contact records (not distinct seeds).

- covered_tool_support / R_held_collar_wall15: 926 rejected contact records (not distinct seeds).

- covered_tool_support / R_held_collar_wall9: 924 rejected contact records (not distinct seeds).

The stationary appliance/transport envelope audit is clear with a 12 mm smallest exact aligned-box gap, excluding only designated mounts; see [layout_audit.json](../../sim/r02/concept2/results/layout_audit.json). The model must preserve a 10 mm gap under deflection/tolerance, so the 2 mm nominal reserve is inadequate as a production proof. The process handoff has real interface problems: cartridge/vessel envelopes contact guarded-cell supports, and some presence/rinse hand poses approach the faucet too closely. Some oversized wall/counter contact diagnostics also have implausibly deep signed penetration and need an independent geometry/numerics review; they remain rejected by the literal reference rule. Finite random seeds are not a global impossibility proof. No contact exemption is introduced to make these witnesses pass.

**Passing, parking and parallel work**

The independent-lane topology permits order exchange, but actual arms must fold safely and park their tools first. [passing.json](../../sim/r02/concept2/results/passing.json) checks 41 longitudinal samples with empty grippers retained, including same-X crossing. 18/41 sampled states are clear; all-state pass=False. Parking clear=True. The crossing pose is clear, but the full sampled corridor is rejected, principally by the front arm passing the faucet. The selected per-phase parking joints are evaluated by the same collision gate and any active/parked-arm conflict rejects that seed. A crossing snapshot does not prove deployment/retraction paths, loaded overtaking or a continuous safe trajectory. No tested parallel washing/cutting schedule is claimed. The fixed machine can in principle cut while detached arms wash another ingredient, but the coupled washing pair and the shared sink/loading station limit arm concurrency.

[conflicts.json](../../sim/r02/concept2/results/conflicts.json) separates arm-arm and parked-arm failures: 67 seed-stroke witnesses include an R/L clearance conflict; 167 include a contact involving an unused parked arm. These categories may overlap and are not whole-phase seed counts. The empty transport sweep has 6/41 arm-arm conflicting states; its other failures are environmental clearances.

**Loads and 3 kg service**

[loads.json](../../sim/r02/concept2/results/loads.json) gives conservative whole-body full-reach sizing and actual saved-pose wrench envelopes, including rejected IK poses. The conservative model puts the full 12.5 kg arm plus 1.2 kg gripper and 3 kg payload at 0.7 m, with the carriage at a 225 mm eccentricity. Per carriage: static force bound 312.6 N, static moment bound 178.8 Nm; 1.5x factored bounds 468.9 N / 268.2 Nm. Two-lane wall-envelope force/moment 2118.4 N / 1871.1 Nm. These fit the transport role’s 900 N/650 Nm design envelope, not a certified built carriage. Beam/arch/anchor compliance must preserve the 5 mm pose and 10 mm clearance budgets; the nominal cabinet/arch reserve is small. Wall anchoring needs structural concrete or a verified fixed portal, not cabinet carcasses or tile. Net wall wrench is not an individual anchor reaction.

The press checks 1,000 N internal frame load, up to 636.4 N sourced-margin tomato reaction and a 200 Nm internal bridge moment envelope. Opposed blade/food-support forces close inside the fixed C frame; zero cutting force reaches a mechanically detached arm. Base loads include machine mass/dynamic reactions and must still be checked. No weak arm is credited with a missing cutting reaction. Spring-applied rail-brake sizing, translational stopping energy and the 60 ms engagement estimate are in loads.json; rotor inertia, brake monitoring, SS1/STO sequencing and certified stopping tests remain unclosed. Separate 3 kg saved-pose torque diagnostics do not create a qualified3 kg service result. The worst saved IK pose at full 3 kg has a 1.660 ideal-reference wrist ratio (R joint 5,19.91 Nm versus 12 Nm), and is already collision-rejected; therefore payload eligibility alone cannot close service torque.

**Force provenance and time**

The full inherited [process_v2.json](../../sim/r02/tools/results/process_v2.json) force ledger is used. [Singh et al.,2016](https://iseki-food-ejournal.com/article/69/pdf) supports carrot/potato per-width force sizing:152.6/183.2 N with 2× margin; greens 348.9 N is an explicit carrot-tissue proxy, not measured bok-choy resistance. Tomato 636.4 N uses the supplied 4 mm probe firmness/0.952 mm blade-width stress proxy and 2× margin; it is not a measured wedger force and cannot certify pulp quality. [Carrot peeling literature abstract](https://www.qikan.com.cn/article/5dd020251220.html) supplies 1.68 N/mm, hence 63 N at 25 mm engagement with 1.5× margin; potato remains a disclosed proxy. Eye/core 52.3 N is a 12 mm cutting-width root proxy; the supplied 0.262/0.524 Nm free moment is included. Calibrated spring kδ, jetρQ²/A, Coulomb sliding and Newtonian carry inertia retain their supplied1.5–2x margins. No force is selected from torque feasibility.

The reference meal is one specimen of each input size/mass because cook_ref supplies no larger batch quantities. [timeline.json](../../sim/r02/concept2/results/timeline.json) gives an illustrative resource schedule: serial 101.7 min; scheduled 95.0 min, using 40 mm/min engaged blade speed and declared unloaded-return/handling estimates. Slow cutting alone consumes75.4 min. Washing the next batch may overlap detached cutting. These are planning numbers; verified total prep time is **unavailable** while the motion chain fails. Faster appliances need new force-speed-quality evidence rather than reusing slow-cut forces.

Illustrative resource timeline in minutes; none of these intervals is an executable motion result.

| Interval (min) | Cutter / main activity | Possible concurrent work |
|---|---|---|
|0.0–5.9|Prepare/load carrot|Shared wash/peel pair|
|5.9–37.4|Carrot powered slicing|Prepare potato; coarse-wash greens; wash/core tomato, then wait|
|37.4–38.9|Deliver carrot; load potato|Machine exchange is serial|
|38.9–73.4|Potato powered slicing|Arms may park; shared cutter blocks greens trimming|
|73.4–87.5|Potato starch rinse/drain; greens trim/wash/split/section; load tomato|Shared sink/cutter work is serial|
|87.5–89.5|Tomato eight-wedge powered cycle|Arms detached|
|89.5–95.0|Deliver tomato; inspect four outputs; clean/dock|Cleanup completes reference meal|

**Power track and cleanable/safe construction**

The household track baseline is aluminium/copper modular outlets for **stationary appliance/tool** power, using 70 × 28 mm rail and 67 × 43 mm adapter envelopes. [Eubiq catalogue](https://eubiq.com/wp-content/uploads/2020/09/Eubiq-Catalog-2020-E-Size.pdf) and [E-Track specification](https://eubiq.com/product/e-track/) are source comparisons; model segments are split around the sink with dedicated wall mounts. The track, adapters, rail beams, guides, chains and transfer decks are robot parts in the check. Cabinet door sweeps/outlet access are fixed-hardware constraints, closed cabinet solids are arm obstacles; doors require stopped/interlocked parked arms. The transport addendum requested by the scope was absent at the read checkpoint, so no unavailable recommendation is attributed to it.

Moving arms use independent cable carriers because each has its own straight lane. Fixed dry AC controllers output 24 V through the OEM flex lead; no battery or household sliding adapter powers an arm. [UFACTORY specifications](https://docs.xarm.ufactory.cc/8.technical_specifications.html) give 200 W typical per arm and recommend 500 W supply, with 24 V / 20.8 A output. **A measured peak arm consumption is not published**: 500 W is the supply budget, 499.2 W the interface ceiling, not a claimed observed peak. Two arm supplies plus 150 W cutter and 200 W declared drive/EOAT allowance give 1.35 kW design budget (5.87 A at 230 V). Each 13 A stationary-track feed must obey its adapter/plug rating. [UFACTORY cable specification](https://docs.supportarticle.ufactory.cc/support_articles/hardware/bend-radius-for-communication-and-power-cable.html) gives 78/45 mm dynamic radii for power/data; 110 mm modeled bend radius exceeds these catalog values. [UR5e datasheet](https://www.universal-robots.com/manuals/EN/TechSheets/UR5e_techsheet_pdf_online/UR5e_techsheet_en.pdf) gives200 W moderate / 570 W maximum for the UR comparison. [power.json](../../sim/r02/concept2/results/power.json) retains average/peak unknowns and 48 V collector-current sizing.

The switching alternative has a 48 V SELV conductor envelope, xArm DC controller input 24–72 V and 672 W maximum output. A 20 A collector design target includes an assumed 90% conversion efficiency; actual sliding-contact ratings/continuity, transfer gaps, controller packaging, local safety and wireless watchdog need qualification. UR AC controller packaging cannot silently become a 48 V controller. Batteryless dock-and-power loses motion power when undocked; dock-and-charge contradicts the no-battery architecture. For the chosen straight-lane design, ordinary wired OEM safety/data stays in each chain. Person detection, speed limits, Category 1/SS1 stops and spring-applied brakes are required; household IP40 track and generic robot protection do not imply washdown. Food-contact stainless/POM/pads need grade-specific declarations, removable drainable covers, accessible cleaning and measured food trials.

**Budget and artifacts**

The installed budget is **493,292.45 CNY**, including one 15% reserve. [costs.csv](../../sim/r02/concept2/results/costs.csv) separates historical public award clues from allowances and avoids adding the tools contingency twice. It is not a supplier quote; no purchase/contact occurred. Files are confined to this role’s workspace. [reference.diff](../../sim/r02/concept2/audit/reference.diff) is empty; [adapter.diff](../../sim/r02/concept2/audit/adapter.diff), [model.diff](../../sim/r02/concept2/audit/model.diff), [phase_contract.diff](../../sim/r02/concept2/audit/phase_contract.diff), [change justification](../../sim/r02/concept2/audit/change_justification.md) and [checker_contract.json](../../sim/r02/concept2/audit/checker_contract.json) justify every changed plumbing responsibility. Original contact/pose/grip/padding rules and R01 files remain unchanged. CPU foreground chunks are individually time/memory bounded below 20 minutes/1900 MiB, with at most two numerical workers; resource records are in audit/.

![overview](../../sim/r02/concept2/renders/overview.png)

![passing](../../sim/r02/concept2/renders/passing.png)

![washing](../../sim/r02/concept2/renders/washing.png)

![peeling](../../sim/r02/concept2/renders/peeling.png)

![eye_core](../../sim/r02/concept2/renders/eye_core.png)

![root_cutting](../../sim/r02/concept2/renders/root_cutting.png)

![greens_washing](../../sim/r02/concept2/renders/greens_washing.png)

![greens_cutting](../../sim/r02/concept2/renders/greens_cutting.png)

![tomato_cutting](../../sim/r02/concept2/renders/tomato_cutting.png)

![delivery](../../sim/r02/concept2/renders/delivery.png)

![parked](../../sim/r02/concept2/renders/parked.png)

Rendered views use actual saved MuJoCo poses/geometry and carry their pass/rejection status. Images are CPU Blender Cycles, 1440 × 960; blue identifies R and orange L for visibility, without changing geometry. Cabinet-door/outlet keepout overlays and the opposite wall are hidden for visibility only; they remain collision constraints. [best_scene.xml](../../sim/r02/concept2/models/best_scene.xml) includes a checked parking keyframe; its label does not claim a clear posture when the saved gate fails. Reproduce: bounded.py <seconds> <logname> <python> -B run.py setup; run.py worker --config c0684 --seeds96 --ids <instance IDs> --stage final_v4; run.py baseline --ids P01…P16; recheck.py final_v3 final_v4; supplement.py audit power_timing mounting layout_audit option_models observed_loads transport phase_renders; then Blender render and build_report.py. All numerical subprocesses must retain the supplied bounded runner.
