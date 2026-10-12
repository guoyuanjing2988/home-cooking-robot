本轮没有做出可连续运行的整餐备菜方案。按原参考检查器复核，静态阶段通过 **19/27**，食材展开实例通过 **26/36**，动作通过 **95/105**；完整餐序列的运动检查为 **失败**。这些数字是位姿、接触、额定负载力矩包络和夹持的静态结果，不代表已经完成洗净、切菜和交付。

最终候选使用两条独立固定轨道、UR5e 主臂和 xArm6 辅臂，电缆走各自拖链。根茎切片改用商品旋转盘切菜机；保留削皮、挖眼去芯和有护罩的辅助切菜盒。没有删掉胡萝卜、土豆、小白菜或番茄，也没有放宽 5 mm／3°、间隙、摩擦或安全系数。最终每个动作都有至少 96 次求解起点，实际通过的结果另做独立复核；失败动作保留阻挡物和错误数据。

家用安全等级的工程预算为 **人民币 467,129.95 元**，其中只有一套 **18,000 元**安全包，预备费只计一次。顺序备菜计划为 **99.86 分钟**，包含 10 分钟浸泡、注水、沥水和清洁；这不是已执行的时间。未采购、未联系供应商。当前方案不能冻结为可制造或可自主运行的整机。


## Final result and evidence


Final candidate: **UR5e R + xArm6 L**, two independent fixed X lanes. Overall acceptance: **FAIL**. A finite failed search is evidence against this candidate and solver starts, not a proof that every kitchen-robot layout is impossible. The exact final reply reports the static logical phase count; complete-meal motion is separately marked fail.

The final dataset contains 10,080 solver starts across 105 strokes, with 2134 solver solutions and **2134 independently verified witnesses**. Fresh final7 starts correct the potato feed axis. Final6 starts are reused only for byte-identical geometric/force strokes with identical installed geometry, tools, food specifications and thresholds; only loop/timer annotations can differ. The replay rejects stale geometry and checks every claimed successful start. All accepted witnesses have public-range checks, every pose error, every force/moment case, clearance records, flange payload/CoM checks and grip margins. Maximum check-envelope ratio among accepted poses: **0.649926**; minimum grip margin after the required SF 1.5: **1.5822**. Published continuous joint-output torque ratios are null where no such rating is published; the xArm motor-times-gear diagnostic is explicitly separate.

Machine-readable evidence: [process_v3.json](../../sim/r03/integrator/results/process_v3.json), [best.json](../../sim/r03/integrator/results/best.json), [phase_summary.json](../../sim/r03/integrator/results/phase_summary.json), [motion.json](../../sim/r03/integrator/results/motion.json), [iterations.csv](../../sim/r03/integrator/results/iterations.csv), [costs.csv](../../sim/r03/integrator/results/costs.csv), [loads.json](../../sim/r03/integrator/results/loads.json), [power.json](../../sim/r03/integrator/results/power.json), [timeline.json](../../sim/r03/integrator/results/timeline.json), [torque_envelope.json](../../sim/r03/integrator/results/torque_envelope.json), [envelope_reachability_audit.json](../../sim/r03/integrator/results/envelope_reachability_audit.json). Per-stroke MJCF and replay records are in [witnesses](../../sim/r03/integrator/results/witnesses/). No mandoline remains, so the golden mandoline case is **not applicable**, not reported as a pass.

The compact [stroke_metrics.csv](../../sim/r03/integrator/results/stroke_metrics.csv) lists all 105 strokes, starts, solver/verified counts, pose errors, nominal/check torque ratios, grip margins and minimum clearance by category. Missing metrics identify rejected strokes; published continuous joint output ratings remain blank. [installed_parts.json](../../sim/r03/integrator/results/installed_parts.json) and [installed_parts.csv](../../sim/r03/integrator/results/installed_parts.csv) enumerate the exact full-cell collision geometry, with a [complete scene XML](../../sim/r03/integrator/models/installed_cell.xml). The inventory is an envelope model, with unresolved appliance internals and actuation explicitly identified.


## Process and unchanged finished products


The meal remains one120g carrot, one200g potato,100g bok choy and one150g tomato. Finished-product specifications are copied unchanged from R02 into process_v3.json. Root slices are nominal5mm,4–6mm with at most1mm within-slice variation; peeling0.2–0.8mm and gouges at most2mm. Every potato eye/blemish must be removed, with2–3 fresh-water starch rinses and20–30s draining. Bok choy retains the5–10mm root trim, exposure/rubbing/inspection of every basal crease, one600s soak, stalk width at most15mm, nominal40mm sections in30–50mm range and bundles at most30mm high. Tomato retains skin, hard-core removal without scooping the seed cavity, eight completely severed35–55degree wedges and0.65–1.35mean mass ratio. All edible outputs, including the10mm stub and last5mm root slice, require at least98percent transfer into separate next-step vessels; ten distributed root slices, every wedge and every crease remain inspection gates. These physical quality gates are required and **unmeasured**.

Root slicing uses the publicly specified Robot-Coupe R211XL and its5mm accessory. The OEM lists continuous ejection,87cm2 hopper,58mm cylindrical inlet,245×385×510mm body,13kg,550W and1500rpm. The geometry retains that full body; a145×60mm lumen partition with the same area is a **CAD assumption**, not proof of the actual half-moon shape or pusher compatibility. [OEM product and accessories](https://www.robot-coupe.com/export/en/p/food-processors-r-211-xl/18401), [5mm disc](https://www.robot-coupe.com/nl/nl/p/schijvenverzameling-snijschijven-5-mm/18289). Arms release food with5mm lip clearance while the appliance is stopped; an actual lever/pusher and interlocked restart sequence remains unqualified. Carrot and potato-half longitudinal feed axes preserve the terminal-stub dimensions; powered-disc forces are not inferred from low-speed press literature.

The old root slow press is removed. The guarded secondary cassette cell is retained for3–5mm end trims, terminal two5mm slices, potato longitudinal split, bok-choy root/stalk/40mm operations and eight-wedge tomato cutting, for which the selected5mm rotary disc would not meet the product specification. This still involves extra cassette transfers and slow auxiliary cycles. It is not presented as a proven commodity eight-wedger, a measured food-force bound or a fabrication-ready appliance. The plan is intentionally less optimistic than a30–35minute estimate: preserved low-speed proxies and terminal processing still dominate several operations.


| Q phase | Old P coverage | Static result | Failed strokes |
|---|---|---|---|
| Q01 | Additional R02 requirement | PASS | — |
| Q02 | P01, P02, P07, P08 | FAIL | Q02.carrot__wash, Q02.potato__wash |
| Q03 | P03 | PASS | — |
| Q04 | P15 | PASS | — |
| Q05 | P04, P09 | PASS | — |
| Q06 | P09 | PASS | — |
| Q07 | P04, P09 | PASS | — |
| Q08 | P02, P08 | FAIL | Q08.carrot__rinse, Q08.potato__rinse |
| Q09 | P05, P14 | PASS | — |
| Q10 | P06, P10 | PASS | — |
| Q11 | P14 | PASS | — |
| Q12 | P14 | FAIL | Q12.carrot__deliver |
| Q13 | P11 | FAIL | Q13__Coarse_wash_bok_choy |
| Q14 | P12 | PASS | — |
| Q15 | P11 | PASS | — |
| Q16 | P11 | FAIL | Q16__soak_bok_choy |
| Q17 | P11 | PASS | — |
| Q18 | P12 | PASS | — |
| Q19 | P12 | PASS | — |
| Q20 | P14 | PASS | — |
| Q21 | Additional R02 requirement | FAIL | Q21__Wash_unpeeled_tomato |
| Q22 | Additional R02 requirement | PASS | — |
| Q23 | P13 | PASS | — |
| Q24 | P13 | PASS | — |
| Q25 | P14 | FAIL | Q25__Deliver_tomato_next-step_bowl |
| Q26 | P14 | PASS | — |
| Q27 | P15, P16 | FAIL | Q27__wipe_secondary |


The ten failed strokes retain every rejected start in the final-stage files. The pair counts below count recorded blockers, not mutually exclusive failure categories. IK failure can accompany a geometric blocker; clearing one pair would not prove the stroke. [Failed-stroke ledger](../../sim/r03/integrator/results/failed_strokes.csv).

| Failed stroke | Starts / verified | Most frequent recorded pairs |
|---|---:|---|
| Q02.carrot__wash | 96 / 0 | root_brush_work_face / R_finger_plus (211); root_brush_work_face / R_finger_minus (161); root_brush_height_slide / R_held_food (160) |
| Q08.carrot__rinse | 96 / 0 | root_brush_work_face / R_finger_plus (207); root_brush_work_face / R_finger_minus (167); root_brush_height_slide / R_held_food (141) |
| Q12.carrot__deliver | 96 / 0 | output_carrot_land / R_held_bowl_outer_bottom (53); R_geom_11 / R_adapter_piece1 (35); output_carrot_land / R_held_bowl_outer_wall5 (34) |
| Q02.potato__wash | 96 / 0 | root_brush_work_face / R_finger_plus (194); root_brush_height_slide / R_held_food (183); root_brush_work_face / R_finger_minus (171) |
| Q08.potato__rinse | 96 / 0 | root_brush_work_face / R_finger_plus (194); root_brush_height_slide / R_held_food (183); root_brush_work_face / R_finger_minus (171) |
| Q13__Coarse_wash_bok_choy | 96 / 0 | dock_eye_core_spoon_face / R_held_contents (263); sensor_faucet_spout / R_held_cup_offset_beam (231); root_brush_work_face / R_held_cup_floor (139) |
| Q16__soak_bok_choy | 96 / 0 | sink_back / R_held_colander_shell_bottom (103); root_brush_sealed_drive / R_held_colander_shell_bottom (93); R_geom_25 / greens_crease_land (45) |
| Q21__Wash_unpeeled_tomato | 96 / 0 | root_brush_work_face / R_held_cup_floor (149); sensor_faucet_spout / R_held_cup_offset_beam (121); sensor_faucet_spout / R_held_contents (92) |
| Q25__Deliver_tomato_next-step_bowl | 96 / 0 | outlet_access_0 / R_held_collar_wall4 (98); outlet_access_0 / R_held_collar_bottom (69); outlet_access_0 / R_held_bowl_outer_wall4 (69) |
| Q27__wipe_secondary | 96 / 0 | R_geom_17 / secondary_work_face (64); R_geom_17 / R_gripper_palm (53); R_geom_21 / secondary_side_guard-1 (47) |


Q01 stages/checks the cell and water. Q02–Q08 acquire, wash, peel/index, remove potato eyes, clean and rinse roots. Q09–Q12 load/output the OEM slicer, retain terminal slices, rinse/drain potato and deliver bowls. Q13–Q20 coarse-wash, trim, separate, soak/rub/rinse/drain and section every bok-choy stalk. Q21–Q25 wash/core/wedge and deliver tomato. Q26 inspects all outputs; Q27 includes a working-face wipe, tool return and water-off. Old P01–P16 are mapped above rather than substituted by a changed meal. Recipe loops, vision-dependent operations, output ownership and cleaning disassembly still need full state expansion; the motion audit explicitly fails those omissions.


## One geometry and contact policy


Coordinates are T08 world metres. Counter slabs are onlyx[−1.80,−0.70] and[−0.11,0.69],y[0,0.60],topz0.85; the original sink and protected stove remain. The slicer casing has35mm front overhang, with all four feet on the right slab and its centre inside the footprint. No new slab or workspace is invented. Main mount isy−0.10,z1.23, helpery−0.55,z1.60, lane pitch450mm. Actual mount rotations are152.113697747degrees and225degrees. Mechanical carriage range is[−1.70,0.20]; the main search is conservatively limited tox<=0.045 near the slicer. Each rail, guide, adapter, bearing bridge, spring brake/drive, cable-chain cover, crossbar, hanger, anchor plate and stationary power track is included. Long beams are split into exact unions of shorter boxes without reducing their dimensions or repeated mass.

Raw lands are atx−1.685/−1.535, y0.095/0.245;6mm pedestal shims reach the tray. The raised peel land is(−0.935,0.17),top1.105. Secondary cell is(−1.27,0.17), worktop0.960; full lid/guard/drive envelopes remain. Four output lands are atx−1.665,−1.415,−1.165,−0.915,y0.435,top0.862. Tool docks atx−0.55,−0.325,−0.18,y0.46 have full rear-ledge posts and brackets, separated from the original spout and upper cabinets. Bowl support gaps apply to the full held assembly, including contained food within the bottom-shell proximity band; this is only its own named plane at the release endpoint, never a neighbouring fixture.

The proposed wash poses put food below the unchanged spout lower-front outlet assumption (−0.4, 0.405, 1.032). Root brush is (−0.42, 0.40); carrot grip z 0.950 and potato z 0.9475 prescribe 6 mm bristle deflection. Offset cups at (−0.25, 0.385–0.405, 1.00) are intended to put food under the outlet. These wash strokes remain rejected: finger/brush and faucet/held-assembly blockers are not intended contacts. The full 240 mm diameter, 100 mm high colander is centred at x −0.30, y 0.37–0.385. A 90 degree brush pivot permits some rinse/drain endpoints without shortening any component, but the submerged-soak stroke still fails. The full-height brush stem, slide, working face, hinge, pin and drive enclosure remain in both configurations. The brush-pivot actuator sweep is not certified. The redundant fixed nested basket is removed as a process simplification; an earlier 230 mm width, 80 mm height approximation was an invalid draft and is not credited.

The helper gripper is enlarged:110mm opening,100mm-wide palm and1.5kg EOAT instead of90mm,80mm and1.2kg; fingers and OEM arm bodies remain full size. Root gripper offsets are8mm carrot/11mm potato along approach. Wet-food normal150N and keyed150N/15Nm remain design qualification requirements, not a claim that an off-the-shelf84mm/30N xArm gripper meets them. Both actual flange payloads/CoMs are checked, including gripper mass.

Each stroke pose enumerates specific held parts, a single named support/working-face geom and a geometric reason. Top/axial contact normals and face positions are independently checked. Food-land/stop contacts apply only to food; peeler edge/skid, cleaning-pad face and spoon edge/distal neck are the working contacts. Own raw/tool/bowl/cassette support faces apply only at grasp/release endpoints. No whole guard, fixture frame, rail, wall, faucet or arm link is an intended contact. Original welded/adjacent OEM exclusions and the dedicated north-wall mounting bracket rule are retained by the unchanged checker. PAD0,10mm robot/environment and inter-arm gaps,5mm held/gripper/environment,5mm/3degree targets,mu0.5 andSF1.5 are unchanged.


## Search, torque and connected motion


SciPy least-squares searches public joint ranges and carriagex from deterministic random, parked and prior verified seeds. It includes signed MuJoCo geometry-distance penalties for actual blocker pairs, with iterative collision-aware refinement. Clearance optimisation changes joint/carriage poses, not mesh size or reference gaps. Candidate solutions are then checked with the unchanged copied reference contact/error equations, every retained nominal/check force and free moment, rated-load torque envelopes and grip equations. Independent replay performs a stricter exact-face mapping and public payload-chart check. Clearance records give the minimum among relevant contacts; where no contact lies within the20mm detection band, they explicitly report a>=20mm lower bound. Witness files distinguish that from an exact distance.

Rated capability follows the2026-10-08 decision:5kg total flange load replaces all simulated EOAT when constructing the envelope, with the OEM allowed CoM offsets. UR5e uses the5kg curve to350mm; xArm uses the5kg chart at radial30mm/axial0–15mm. Actual helper EOAT+food is screened against the conservative2kg/200mm radial/180mm axial curve. Three DE starts maximise each joint, then each retained maximum is independently checked for OEM self-collision and public ranges. One initialL5 maximum self-collided; three constrained starts replaced it, with no torque inflation. Rail/height translation does not change these static angular/gravity capabilities. [UR5e specification and curve](https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf), [xArm payload chart, printedp237](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf).


| Arm | J1–J6 rated-payload envelope, Nm |
|---|---|
| UR5e | 56.214777, 117.713063, 58.933309, 25.229634, 22.215501, 17.167500 |
| xArm6 | 49.808375, 70.412129, 37.717413, 8.657737, 8.652628, 1.482790 |


OEM model sources are the unchanged copied [Menagerie UR5e](https://github.com/google-deepmind/mujoco_menagerie/tree/main/universal_robots_ur5e) and [UFACTORY xArm description](https://github.com/xArm-Developer/xarm_ros/tree/master/xarm_description). Public current joint ranges replace wider legacy ranges; no collision hull is scaled. The copied model mass differs from the current hardware datasheet:UR5e20.9949kg model versus20.6kg including cable specification, xArm12.05164kg versus12.5kg. Thus hardware revision/inertia matching remains a prototype qualification, not a silently adjusted torque model. The [xArm motor table](https://docs.supportarticle.ufactory.cc/support_articles/hardware/ufactory-joint-parameters.html) gives motor ratings and gearing; ideal output equivalents64,64,32,32,12,12Nm are reported diagnostically rather than treated as published continuous output capacity.

OEM documented holding satisfies the revised home-tier arm-brake rule. UR permits arbitrary mount-angle gravity settings and describes powered-off brakes after a controlled stop; xArm documents power-loss brakes and any-direction mounting. This does not waive rail braking or prototype stopping/retention tests. [UR5e manual, Mounting and stop categories](https://www.universal-robots.com/manuals/EN/PDF/SW5_21/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf), [xArm safety](https://docs.xarm.ufactory.cc/1.safety.html), [xArm any-direction specifications](https://docs.xarm.ufactory.cc/8.technical_specifications.html).

Connected motion checked **38,607 states**: 39/105 intrastroke paths and 0/104 consecutive-stroke connections passed the implemented path certificate. Separate full-cell passing: **PASS**, parking: **PASS**. Both lane carriages, full held bodies, all fixtures, parked tools/bowls and raw inputs are included in the passing check. Accepted paths use conservative midpoint clearance certificates. Uncertain intervals subdivide to a 1 mm displacement bound and fail unless their separation reserve certifies the whole interval; failed compatible connections also try a folded waypoint without removing objects. This does not establish complete meal motion.

Passing uses 96 starts and 1 verified full routes. The main carriage travels from −1.70 to 0.045 m; the helper travels from 0.20 to −1.70 m, including the same-X crossover. A prior 4,000-start search over both full mechanical ranges failed because the main adapter intersects the slicer casing near the far endpoint. The corrected route uses the existing main task-solver operating limit; the rail, mechanical range [−1.70, 0.20], installed appliance and every collision gap are unchanged. This operating limit must be enforced in the controller. The archived [prior motion](../../sim/r03/integrator/results/motion_pre_passing_limit.json) preserves that failure. Empty transport passing does not certify loaded passing or the meal-to-parking connections.

The endpoint-only support-contact rule is interpreted literally. A continuous lift from zero object/support distance must traverse distances between 0 and 5 mm before reaching the required gap; those positive-time states fail when contact permission exists only at the exact endpoint. The audit records these failures without adding a contact window. Other blockers include missing static witnesses, changes in held object/food state without a certified handoff, six root-wash rolls not expanded into checked regrasp states, incomplete collection/bowl ownership, missing OEM pusher/interlock operation, helper reclamping, lid/brush actuator sweeps and disassembly/cleaning paths. Some snapshots duplicate supported-food bounding envelopes rather than track a conserved object through every transition. These failures are explicitly stored in motion.json; connected kinematics and food ownership, not merely more endpoint seeds, remain the next integration work.


## Forces, rails, power and time


All17 inherited force models and their source catalogue are embedded in process_v3.json. Magnitudes and safety margins are retained; generic bounds are completed in all six signed Cartesian directions. Peeling is42N nominal/63N check tangential plus5/7.5N normal:1.68N/mm times25mm ribbon andSF1.5, with the potato application labelled a carrot proxy. Root rub6/9N is1000N/m×6mm; leaf2/3N is400N/m×5mm; tomato1/1.5N is200N/m×5mm. These are calibrated-spring design assumptions, not existing product measurements. Jet0.1273/0.191N followsrhoQ²/A for6L/min and10mm outlet, with1.5margin. Eye/core26.1639/52.3277N and0.261639/0.523277Nm remain localized carrot-width proxies. [Peel-source abstract](https://www.qikan.com.cn/article/5dd020251220.html), [primary low-speed cutting paper](https://iseki-food-ejournal.com/article/69/pdf).

Auxiliary frame loads retain carrot152.6226N, potato183.1617N, greens348.8516N and tomato636.3651N design values, with factor2. Greens is a carrot-width surrogate; tomato is penetration/compression stress times blade area, not a measured wedger bound or permission to crush fruit. Arms are detached for cutting;0N blade reaction at the arm is conditional on a correctly latched fixture. No high-speed disc-feed force is inferred from these low-speed numbers. Food-quality, latch, spring, grip and force-displacement measurements remain required. [Tomato primary compression research](https://www.sciencedirect.com/science/article/abs/pii/S0925521401001338), [primary tomato firmness work](https://repositorio.bc.ufg.br/bitstreams/71b8aa0d-e688-48a3-9207-8166a44fe47d/download).


| Rail demand | Main R | Helper L |
|---|---:|---:|
| Moving mass incl3kg structural service load, kg | 34.40 | 26.50 |
| Factored rail force, N | 624.58 | 420.72 |
| Factored moment, Nm | 480.57 | 249.32 |
| Conservative combined block reaction, N | 2865.25 | 1510.68 |
| Guide static capacity/demand | 24.11 | 45.72 |


Each lane uses two150×50×3mm steel tubes,2.8m overall,51.16944kg; guide length2.4m. Crossbarx−1.82/−0.62 yields1.2m support spacing and maximum0.82m operating overhang. Conservative900N/650Nm design checks give0.765mm force sag,1.011mm moment displacement and0.134degree twist; these do not include unknown joints/anchor compliance. Guide block figures use retained69,070N static rating and340/240mm spacing with combined moment reactions. The3kg service load sizes the structure; it is not additional payload qualification at every food pose. Wall demand is 3409.4N and 5136.8Nm. Two100×20×300mm pads with four anchors each and250mm row spacing require 10273.5N per pad-row and 426.2N shear per anchor. No masonry survey, prying/pullout capacity or anchor SKU is certified.

Rail holding candidate is spring-applied MikiBXR-050-10LE,3.2Nm,10:1 ratio,0.8 assumed efficiency and20mm pinion:1280N static holding requirement. At0.2m/s, assumed60ms engagement plus1m/s² controlled deceleration gives12+20=32mm, within50mm reserved stop space. Engagement timing, reflected drive inertia and actual stopping must be measured. The brush drive allowance targets10Nm versus1.5×(9.191N×0.29m+1kg×g×0.29m)=8.26Nm, with1kg assembly assumption and seal/stop tests pending. [Miki spring-applied brake](https://www.mikipulley.co.jp/en/electromagnetic-clutches-brakes/offbrakes/holding/bxr-le).

Power budget is **1970W**: UR570W maximum, xArm500W supply budget, OEM slicer550W, auxiliary drive150W allowance, rails/EOAT/IPC/safety200W allowance. This is8.57A at230V or10.71A at assumedPF0.8. Fixed household tracks stay dry; OEM controllers are fixed, with independent covered moving cable chains. UR6m166100 hiflex13.4mm cable requires8d=107.2mm dynamic radius; modeled horizontal return110mm exceeds it. Full side-mount routing, strain relief, connector revision, thermal derating and circuit ampacity remain installation checks. [UR cable specification](https://www.universal-robots.com/manuals/EN/HTML/SW10_14/Content/prod-cable/cable-product-description.htm), [Eubiq fixed tracks](https://eubiq.com/product/e-track/).

The **99.86minute serial plan** is an engineering allowance, not an executable or measured preparation time. It includes22 root peel/index cycles, every trim and terminal slice, eye/core work, starch rinses/draining, every crease, one600s soak, wide-stalk splits,40mm cuts, tomato wedges, inspection and300s cleaning/disassembly allowance. Whole-sink soaking uses0.84m water over0.65m floor:0.6×0.44×0.19=50.16L; at6L/min filling takes8.36min, explicitly included. Q16 rubbing references the same completed soak, not a second clock. This water-intensive choice is recorded rather than hidden; a smaller reservoir requires new fit/path verification. Retained auxiliary0.5mm/s proxy speed and two assumed wide stalks drive the long plan. Each additional wide stalk adds340s plus handling. No soak overlap is claimed.


## Home-tier cost and reproducibility


Pre-reserve subtotal CNY406,199.96; one15percent project reserve; total **CNY467,129.95**. One inclusive CNY18,000 package covers presence sensing, E-stop, RCD/PE, stop/brake interfaces, blade/lid interlocks and wiring. Rail brakes are charged once in transport; oldB09 safety is removed from tools. No industrial scanner, light curtain or safety PLC allowance is added. Cost lines include main/controller150,000, helper/controller76,900, transport56,000, tools12,799.96, brush pivot1,500, slicer/disc18,000, two EOAT24,000, IPC8,000, installation18,000, qualification labour20,000 and dry tracks3,000. These are planning allowances/historical budgets, not current matched quotations. No purchasing or supplier contact occurred.

All numerical runs use the supplied CPU venv and copied bounded.py, foreground chunks<20minutes, at most four solver workers and1900MiB/process-tree cap. Actual elapsed/RSS records and stdout are underaudit/. Unchanged source hashes are [recorded here](../../sim/r03/integrator/audit/source_hashes.json); R01/R02 inputs were not edited. Mount-angle units were corrected after an early adapter error; the actual main orientation is retained and true helper angles retested. Superseded/incomplete/invalid drafts are separately logged, not final witness evidence.

Reproduce with the supplied robot_v5/board/work/t01/.venv Python. Use `bounded.py 1140 <log-name> <python> -B -u solver.py --ids <instances> --seeds 96 --stage <stage>` for numerical workers; run `final_check.py final7`, then `motion_check.py`, `render_setup.py`, bounded CPU `render_batch.py <view-names>`, and `report.py`. Envelope witnesses are checked by `envelope_audit.py` and repaired by `envelope_repair.py`. Build `process_v3.json` from `process.py` before numerical workers, and never change installed geometry during a run. The final7 cache proof depends on archived `process_trial_final6.json` and unchanged `model.py`/`solver.py`. The outputs are negative, provisional engineering evidence, not a validated kitchen product.


## Actual-state renders


CPU Blender renders are1440×960. Blue is the main arm, orange the helper. Every picture uses saved MuJoCo geometry andq; rejected candidates are labelled. Opposite wall/cabinets and door/outlet overlays are hidden only for visibility, while collision checks keep them. Overview and passing include staged raw inputs. No render is evidence of a complete meal by itself.

![overview](../../sim/r03/integrator/renders/overview.png)

![passing](../../sim/r03/integrator/renders/passing.png)

![Q01](../../sim/r03/integrator/renders/Q01.png)

![Q02](../../sim/r03/integrator/renders/Q02.png)

![Q03](../../sim/r03/integrator/renders/Q03.png)

![Q04](../../sim/r03/integrator/renders/Q04.png)

![Q05](../../sim/r03/integrator/renders/Q05.png)

![Q06](../../sim/r03/integrator/renders/Q06.png)

![Q07](../../sim/r03/integrator/renders/Q07.png)

![Q08](../../sim/r03/integrator/renders/Q08.png)

![Q09](../../sim/r03/integrator/renders/Q09.png)

![Q10](../../sim/r03/integrator/renders/Q10.png)

![Q11](../../sim/r03/integrator/renders/Q11.png)

![Q12](../../sim/r03/integrator/renders/Q12.png)

![Q13](../../sim/r03/integrator/renders/Q13.png)

![Q14](../../sim/r03/integrator/renders/Q14.png)

![Q15](../../sim/r03/integrator/renders/Q15.png)

![Q16](../../sim/r03/integrator/renders/Q16.png)

![Q17](../../sim/r03/integrator/renders/Q17.png)

![Q18](../../sim/r03/integrator/renders/Q18.png)

![Q19](../../sim/r03/integrator/renders/Q19.png)

![Q20](../../sim/r03/integrator/renders/Q20.png)

![Q21](../../sim/r03/integrator/renders/Q21.png)

![Q22](../../sim/r03/integrator/renders/Q22.png)

![Q23](../../sim/r03/integrator/renders/Q23.png)

![Q24](../../sim/r03/integrator/renders/Q24.png)

![Q25](../../sim/r03/integrator/renders/Q25.png)

![Q26](../../sim/r03/integrator/renders/Q26.png)

![Q27](../../sim/r03/integrator/renders/Q27.png)

![parked](../../sim/r03/integrator/renders/parked.png)


Delivery consistency: [artifact audit](../../sim/r03/integrator/results/deliverable_audit.json), [direct visual review](../../sim/r03/integrator/results/visual_qa.json), and [SHA256 manifest](../../sim/r03/integrator/results/artifact_manifest.json). The artifact audit passes; engineering acceptance remains failed.
