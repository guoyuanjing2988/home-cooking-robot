本轮把机构放回原厨房的吊柜下方、靠后墙的位置，取消了 R05 的升降储存架、托盘、加长墙、门架横梁和前腿。两条上下叠放的轨道及拖链都位于柜门前沿之后。修正后的柜门检查通过：候选停车姿态中的机器人与整个开门扫掠至少相隔 15 mm，也没有进入前侧台面带或站人通道。但这还不是可用的停车方案：完整场景中的储物碗与主臂相撞，三个折叠路径都未获得合格端点。新几何下重算了 105 条静态工序、256 个姿态，结果为 0/105；整餐连接为 0/156。离散物权账本有 559 个事件，其中 557 个需要运动；它保持状态连续，但尚未成为可执行的整餐。仅有一条空场景中往返 25 mm 的滑台诊断路径通过，24 帧图条明确标注了这个范围。整餐备菜时间未知，记为 null。预算为 436,079.95 元，含一次 15% 预留和一套 18,000 元家用安全配置；这是未验收方案的估算。上述失败说明本轮方案没有完成验收，不能据此断言所有吊柜下轨道方案都不可行。

## Result and binding decisions

R07 follows the later “Both concepts run in parallel” entry in [DECISIONS.md](../../DECISIONS.md). The earlier dedicated workstation decision is R06's scope. The corrected idle gate checks robot parts against opening doors and the standing corridor separately; doors are never checked against the corridor. The R05 reviewer’s first finding is addressed by explicit contact kind, own object/support identity, registered support/work faces, and a per-call working flag that is cleared after planning. [Contact declarations](../../sim/r07/integrator/results/intended_contacts.json) and [focused compiled-scene regressions](../../sim/r07/integrator/results/contact_policy_regression.json) include the nonworking spoon and wash-pad cases, forged support labels and wrong-object permissions. Neither nonworking probe retains working permission in the actual planner state filter.

| Acceptance/result | R07 |
|---|---:|
| Logical phases | 0/27 |
| Canonical static strokes | 0/105 |
| Freshly replayed canonical poses | 256 |
| Final fresh search starts | 648 |
| Canonical internal motion obligations accepted | 0/105 |
| Expanded meal connections accepted | 0/156 |
| Required event paths accepted | 0/557 |
| Populated idle, including fold paths | FAIL |
| Verified meal preparation time | null |
| Candidate planning cost, CNY | 436,079.95 |

The unchanged gates are 5 mm / 3° pose error, 10 mm robot/environment and interarm gaps, 5 mm held/gripper/environment gaps, PAD=0, μ=0.5, SF=1.5 and 150 N / 15 Nm keyed retention. [Phase summary](../../sim/r07/integrator/results/phase_summary.json) links every fresh stroke replay; [motion](../../sim/r07/integrator/results/motion.json) enumerates every motion obligation. No R05 success is credited to R07.

## Original kitchen and wall rails

The original wall, counter, sink/faucet, upper cabinets and stove exclusion remain. Cabinet front is y=0.230 m, bottom z=1.350 m; wall face is y=0.600 m and counter z=0.850 m. Active R07 models contain no storage elevator, pallet, extra wall, portal header or front legs. Inherited R05 snapshots and witnesses are archived under `sim/r07/integrator/upstream/models/`, not used as R07 evidence.

Two stacked lanes were selected to explore independent carriage movement and possible passing while keeping both lanes behind the cabinet front. Each rail has a declared 2.42 m × 60 mm × 70 mm envelope, x=[−1.76,0.66] m, y=[0.525,0.585] m. Rail centres are z=1.150 and 1.235 m. Guides, carriages, mounting plates, ties, brake housings and power adapters are included at their declared full dimensions. Four named rear bracket faces at y=0.600 m are the only wall contacts. Nonmating ties stop at y=0.589 m, giving 11 mm wall separation. No whole wall fixture is exempted.

The two conservative cable-chain swept covers occupy x=[−1.74,0.64], y=[0.240,0.485] m, z=[1.275,1.300] and [1.310,1.335] m. The 110 mm chain bend radius lies in XY; 25 mm link thickness sets cover height. These are full swept envelopes, not a claim of completed articulated chain routing. The front face has exactly 10 mm cabinet-front separation and **zero additional reserve**. The upper cover is 15 mm below cabinet/door bottom. Dry household power tracks and adapters are retained in this band.

Main base is (carriage x,0.403386,1.193687) m with mount angle 149.236462°; helper is (carriage x,0.427000,1.212596) m at 155.143092°. The rail centres are separated by 85 mm, but the actual arm bases have only about 19 mm vertical and 24 mm depth separation. **Stacked rails did not establish passing.** The [65.109 s passing search](../../sim/r07/integrator/results/passing.json) used seven starts/restarts, checked 285 states and 189 candidate edges, and produced no accepted path. Its 20 mm proposal grid is search-only; acceptance requires the unchanged ≤4 mm replay. No passing proposal reached acceptance. Fixture/faucet, arm and mounting restrictions remain; this is a failed search for this geometry, not a proof of universal impossibility.

## Arms, folded envelope and rated-load evidence

The selected principal is the full UR5e collision/inertia model, retaining its OEM 5 kg rating and 850 mm reach. The main capability allocation remains 3 kg carried load plus 1.2 kg EOAT, 4.2 kg total, subject to the payload CoM and mounted torque envelope. There is **no accepted 3 kg service reach witness** in this round. Nominal payload is not substituted for task acceptance. [UR5e specification](https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf).

| Option | Capability comparison | R07 admission |
|---|---|---|
| UR5e principal | 5 kg, 850 mm; complete copied OEM model and documented arbitrary mounting/power-loss holding | Chosen; bare tuck found, task strokes fail |
| xArm6 helper | 5 kg nominal, 700 mm; complete copied OEM collision/inertia model, documented brakes | Chosen for model/brake evidence; task cap 0.25 kg + 1.5 kg EOAT; populated park/passing fail |
| UR3e helper | Current OEM page lists 3 kg, 540 mm and 11.2 kg arm mass; shorter reach can restrict sink/front access | Smaller candidate; no matching R07 numerical model/envelope admitted |
| Lite6 helper | 0.6 kg payload cannot carry the retained 1.5 kg helper EOAT | Requires a new light gripper, mounted brake evidence and full task replay; not admitted |

The xArm6 helper is deliberately capped for food indexing, rather than assumed to carry all main-arm loads. Its long retained EOAT uses the inherited conservative ≤2 kg actual flange-load curve, ≤200 mm radial and ≤180 mm axial CoM checks. The 0.25 kg task cap covers the retained 0.20 kg potato; it does not authorize helper bowl transfer. The retained model was preferred over inventing a compact OEM envelope. Public comparisons: [xArm technical specifications](https://docs.xarm.ufactory.cc/8.technical_specifications.html), [xArm manual and payload/brake basis](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf), [current UR3e](https://www.universal-robots.com/products/ur3e-540/), [Lite6](https://www.ufactory.us/product/lite-6). JAKA and Elite records remain inherited research candidates, not newly admitted arms.

Exact-support AABBs of the saved bare tuck, including each arm's carriage and EOAT, are R: **1.117 × 0.291 × 0.345 m**, L: **0.766 × 0.286 × 0.389 m**. The allowed cross section after 10 mm gaps is about 0.35 m deep × 0.48 m tall. R's elbow is nearly straight along the rail; the shoulder and wrists fold to tuck it behind the front plane. Compact positive- and negative-elbow folds were also searched and failed. The bare tuck uses longitudinal room, not shrunken links. These dimensions establish a bare snapshot fit only. [Measured envelopes](../../sim/r07/integrator/results/counter_and_arm_envelopes.json).

Rated-payload envelopes were recomputed with the actual tilted mounts, full source masses/inertias, world gravity and each OEM's allowed 5 kg payload CoM boundary. Two differential-evolution restarts per joint retain only public-range, OEM self-collision-free maximizing witnesses. Numerical maxima are conservative feasible estimates, not proven global maxima or published continuous joint-output ratings.

| Joint order J1–J6 | Envelope, Nm |
|---|---|
| UR5e | 61.476, 117.713, 58.933, 25.230, 22.216, 17.168 |
| xArm6 | 29.610, 70.412, 37.717, 8.658, 8.653, 1.483 |

The subsequent helper translation of −14.9246 mm in Y leaves its mount rotation, gravity moments and relative OEM self-collision unchanged. Every final stroke uses these envelopes. Published motor torque × gearbox ratio remains diagnostic only. [Envelope witnesses and limitations](../../sim/r07/integrator/results/torque_envelope.json). OEM documented arm power-loss holding is the home-tier brake basis; rail brake housings represent required de-energize-to-apply hardware, without a fabricated tested holding capacity. Wall anchors, stiffness, custom keyed EOAT and installed brakes remain unqualified.

## Appliance replacement and human counter area

The 510 mm R211 and its continuous-discharge geometry are removed. The candidate BFP610 has public dimensions listed as 39.5 × 19.7 × 23 cm, with uncertain regional axis ordering. The external model conservatively allocates **395 × 295 × 395 mm**, taking the largest dimension upright and adding depth allowance. Bounds are x=[0.2275,0.6225], y=[0.0125,0.3075], z=[0.850,1.245] m, leaving 105 mm below the cabinet bottom. This solid represents exterior exclusion, **not exact feed, pusher, lid, disc or removable-bowl geometry**. Lowering inherited approach targets by 115 mm cannot qualify those interfaces. [OEM product data](https://www.breville.com/en-nz/product/bfp610).

The manual's 0.3–5 mm adjustable slicing range is nominally compatible with the unchanged 4–6 mm carrot/potato product at a 5 mm setting. Bowl/lid/large-pusher interlocks and motor braking are documented. BFP610 is a **batch** processor: stop and unplug, remove lid, remove disc by its hub, then lift/unload the bowl. Twelve explicit root-batch handling events are included; there is no fictitious continuous discharge. The OEM manual also forbids unattended operation; it does not qualify this proposed autonomous interface. Feed force, disc/bowl geometry, automated unplugging, terminal recovery and cleaning are unresolved. [OEM manual](https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf).

Appliances stay on the counter. A conservative 5 mm occupancy grid projects all fixed, stored and raw objects through z=0.855–1.350 m, with a 10 mm buffer around each. The largest clear rectangle in the cabinet-front strip is x≈[−0.120,0.215], y=[0,0.215] m: **335 × 215 mm, 0.0720 m²**. This is a small available work patch in the candidate layout, not a claim that the full counter is clear or that populated idle passed. The saved robot tuck itself remains outside the complete declared front strip and person corridor.

## Corrected parking and static re-verification

Five full-size, 18 mm thick cabinet leaves are modelled at their original hinges and shown open at 90°. Their complete 0–90° opening sweep remains at z≥1.350 m. Exact support bounds put every robot part at z≤1.335 m in the saved tuck. This separating-plane argument covers every door angle and gives at least 15 mm gap; it does not test doors against the person corridor.

The **populated parked snapshot fails**: examples include `R_geom_11 / stored_bowl_leafy_greens_bail_bridge` at −24.703 mm and the bail leg at −24.708 mm, against a required +10 mm. The bare fixed-kitchen tuck passed without loose objects; restoring all original bowls/tools/raw produce removes that credit. A further populated park optimization also failed. Three fresh deployed empty-hand TCP targets near front counter, sink and appliance each received 16 endpoint starts. None produced an admitted endpoint; therefore no fold/unfold route or meal-end-to-park route is accepted. [Idle snapshot, door proof and fold obligations](../../sim/r07/integrator/results/idle.json). The path requirement is not replaced by the snapshot proof.

All 105 canonical strokes and all 256 required poses were freshly continued and replayed with the new rails, chains, mounts, lower appliance exterior and forward tool docks. Final searches used six starts per stroke, with 24 for the mobile-helper probe at stroke 0. Earlier mount/park searches and interrupted first static chunks remain in the audit. Every pose replay evaluates nominal and check wrench combinations, gravity, actual flange mass/CoM, wet grip/key limits, public ranges and eligible geometry pairs. Common blockers are fixture/faucet/carriage or chain interference and pose error in the new tilted mounts. For example Q01's recorded first pose has 26.539 mm / 6.666° error, a 7.5 mm faucet/carriage gap and cable-cover penetration. This numerical search is not exhaustive; its failure is not a proof that no alternative arm or mounting exists.

## Conserved meal, forces and planning coverage

The single initial scene retains four complete raw inputs totalling **0.57 kg**, four output vessels and registered tools. The [persistent model](../../sim/r07/integrator/results/persistent_model.json) has 18 mocap bodies and one discrete owner per registered object. The [state sequence](../../sim/r07/integrator/results/state_sequence.json) has zero discrete chain errors, 157 expanded stroke instances, 156 connections, 559 events and 557 motion obligations. Forty-nine redundant idempotent commands were removed; grasp/release, lid, brush and batch actions remain explicit. Six stalks, two wide stalks and three potato eyes are conditional planning counts; additional inspected features require added operations. Full source food remains until an accepted partition exists; unverified cuts do not silently delete or shrink it.

This is a **conserved proposed ledger**, not an executable conserved meal. Continuous attachment transforms, jaws, support releases, clamp/latch travel, source-matched BFP parts, cut-piece/scrap topology and measured yield are missing. Two inherited R211 lid/pusher placeholders in the diagnostic persistent model are explicitly marked incomplete and obsolete, never credited as BFP interfaces. Every canonical internal path, expanded connection and event path has a status and evidence link in `motion.json`; the 104 adjacent canonical links are separately enumerated.

The copied planner offers a real 65 s search budget, 12 s restarts, folded staging proposals, shortcutting and ≤4 mm model-derived point-displacement acceptance replay. The passing diagnostic consumed that budget. **Full-meal planner execution coverage was not achieved:** meal roots lack accepted R07 endpoint witnesses and a complete persistent executor, so they are rejected before RRT. Allocated budget and actual zero RRT time are recorded separately. A precondition rejection is not reported as a 60 s search, a planned path or a global infeasibility proof. No disconnected template catalog is promoted to a meal.

All 17 force models, tools and finished-product specifications remain byte-equivalent as parsed data to R05. Retained checks include 152.623 N carrot and 183.162 N potato transverse cutting, scaled from slow primary measurements with the existing 2× margin; 63 N peel drag; 348.852 N greens cutting; 636.365 N tomato wedging; and 52.328 N / 0.5233 Nm eye/core work. Greens, tomato, potato peel and eye/core transfer retain their explicit proxy limitations. None establishes BFP610 feed force. Spring, jet, acceleration and friction calculations retain their earlier assumptions and margins. [Slow transverse-cut measurements](https://iseki-food-ejournal.com/article/69/pdf), [tomato tissue measurements used only as a structural proxy](https://www.sciencedirect.com/science/article/pii/S0925521401001338), and the complete source catalog/derivations in [process_v3.json](../../sim/r07/integrator/results/process_v3.json) support the retained bounds. Food quality, peel coverage, slice variation, terminal yield and cleaning have not been physically verified; no bench tests or purchasing were requested or performed.

## Executed-path time, cost and clearance reserve

The one accepted simulated diagnostic is an empty carriage move **25 mm out and back**, retaining original fixed kitchen and installed hardware/appliance but omitting loose stored tools, bowls and raw food. It is neither meal nor populated idle evidence. Full discrete replay has maximum point step **3.571 mm**, with static empty-arm gravity demand checked at its states. [Actual path and samples](../../sim/r07/integrator/results/aux_paths.json).

Rest-to-rest timing gives **1.333 s** for this local loop at selected home limits: joint 0.35 rad/s and 0.35 rad/s², rail 0.2 m/s empty or 0.1 m/s loaded with 0.3 m/s², maximum geometry-point speed 0.05 m/s and acceleration 0.3 m/s². Only the accepted prismatic path receives timing credit. Full meal `prep_min` and verified preparation time are **null**, not zero. The full 600 s soak, 501.6 s fill at 6 L/min, three fresh potato rinses, 30 s drain, inspection and cleaning are retained required process allowances; batch appliance times are unknown. R05's disconnected 85.86 min calendar is not reused as an R07 makespan. [Schedule](../../sim/r07/integrator/results/schedule.json).

| Clearance reserve above the category gate, mm | Minimum | 5th percentile | Median |
|---|---:|---:|---:|
| Robot/environment, 10 mm gate | 0.868 | 128.594 | 799.106 |
| Interarm/frame, 10 mm gate | 3.583 | 46.739 | 513.699 |
| Gripper/environment, 5 mm gate | 17.480 | 126.069 | 946.737 |
| Nonadjacent self, 0 mm gate | 3.901 | 23.606 | 406.145 |

This distribution includes every eligible pair at every accepted shuttle state, so distant pairs dominate percentiles. It uses conservative AABB/GJK lower reserves, not exact continuous minima. It contains no carried-food clearance evidence. The separate parked door reserve is at least 5 mm above its 10 mm gate, and the front chain has zero geometric reserve above its 10 mm placement gap. Negative populated/stroke gaps are failures, not usable tolerance. [Full clearance distribution](../../sim/r07/integrator/results/clearance.json).

The base allowance is **CNY 379,199.96**, with **56,879.99** added once as 15% reserve, total **436,079.95**. It includes UR5e 150,000; xArm6 76,900; compact wall rails/guides/brakes/chains/brackets 43,000; retained food tools 12,799.96; BFP610 interfaces 4,000; EOAT 24,000; and installation/control/qualification items. The **18,000 home-safety package appears once**, covering presence pause, E-stop, RCD/PE, stop/brake interfaces, blade/lid interlocks and wiring. Rail brakes are in the rail allowance. No industrial safety package, storage elevator or pallet is added. These inherited engineering allowances are not current supplier quotations. Cheapest passing configuration is null. [Cost rows](../../sim/r07/integrator/results/costs.csv).

## Renders and reproduction

- [Overview, candidate/meal fail](../../sim/r07/integrator/renders/overview.png)
- [Candidate parked with all five doors open, populated park/fold fail](../../sim/r07/integrator/renders/parked_doors_open.png)
- [Under-cabinet band, interference labelled](../../sim/r07/integrator/renders/under_cabinet_band.png)
- [Rejected passing frame](../../sim/r07/integrator/renders/passing.png)
- [24 frames from the accepted local empty-carriage shuttle, explicitly not a meal](../../sim/r07/integrator/renders/executed_local_strip.png)

CPU Blender uses actual MJCF geometry, not illustrative or generated replacement arms. Overview/park/band/passing renders are 1440×960; the strip is 1500×880. Opposite wall/cabinets and symbolic access/sweep masks are hidden for display only, retained by collision checks. Frame manifests give exact q, model and scope. Frame sampling illustrates a simulated accepted kinematic path; it is not a recorded physical robot or meal video.

Final delivery audit reports approximately **302.35 MiB** output, longest measured run **546.75 s**, and largest worker tree **1387.51 MiB**. The 28 sequential CPU renders finished in **442.266 s**. Overview, all-open-door parking, band detail and the complete strip were visually inspected. These resource and artifact checks pass; engineering acceptance remains failed.

Use the supplied `robot_v5/board/work/t01/.venv/Scripts/python.exe`, CPU/BLAS threads limited to one. Every run goes through the copied `bounded.py`, with timeouts below 20 minutes and a 1900 MiB worker-tree cap; at most three numerical workers run concurrently. New R07 modules adapt copied geometry/checker/planner code at runtime; all 90 copied R05 Python files and their originals remain unchanged. Main entries are `engineering_metadata_r07.py`, `park_full_r07.py`, `envelope_r07.py`, `static_r07.py`, `final_stage_r07.py`, `build_sequence_r07.py`, `idle_r07.py`, `aux_paths_r07.py`, `rules_r07.py`, `deliver_r07.py`, `measure_export_r07.py`, `counter_and_arm_r07.py`, `render_batch_r07.py` and `archive_and_audit_r07.py`. Search/continuation outcomes and bounded-run records are retained in [iterations.csv](../../sim/r07/integrator/results/iterations.csv) and `audit/`, including failed imports, interrupted chunks and rejected candidates. [Delivery audit](../../sim/r07/integrator/results/delivery_audit.json) verifies files, immutable sources, counts, cost arithmetic, resource limits and render sizes; delivery completion does not change the failed engineering verdict.
