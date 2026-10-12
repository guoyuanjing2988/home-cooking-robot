本轮继续做了 19 个安装／布局版本，其中 12 个版本完成了双臂独立可达性图，完整双臂图共 6048 个目标，另有 252 个单侧图目标，合计 3096 个通过单臂几何检查。最终采用 L13 作为报告中的候选；静态行程为 6/105，独立内部路径为 3/105，整餐连接仍为 0/156。累计保留 1285 次新一轮静态起点尝试；最终候选有 2/105 条行程完成至少 96 次起点搜索。失败的局部搜索没有被当作机构不可能的证明。已记录安装角、墙距、高度、轨道方案和完整工装位置的迭代，以及固定肩部、龙头阻断滑台和不能换序的几何证据。L18/L19 的完整尺寸停放姿态已通过几何检查，但折叠路径仍未通过；主表选用已验证静态及内部路径最多的 L13，不混用不同布局的成绩；整餐备菜时间为 null。预算仍为 436,079.95 元，含一次 15% 预留和一套 18,000 元家用安全配置。旧交付保存在 [integrator_v1.md](integrator_v1.md)。本报告是有明确失败项和覆盖范围的工程记录，不能据此断言所有吊柜下轨道都不可行。

## Result and evidence

The binding basis is the later **Both concepts run in parallel** entry in [DECISIONS.md](../../DECISIONS.md), together with [R05 integrator](../r05/integrator.md), [R05 reviewer](../r05/reviewer.md) and [R04 reviewer](../r04/reviewer.md). This delivery uses the user’s alternative **(b)** stopping basis: at least six documented layout iterations with reachability evidence and specific blockers. It has not recovered R05’s 105/105 result. A failed optimizer is not a general geometric impossibility proof.

| Gate | Result |
|---|---:|
| Logical static phases | 0/27 |
| Canonical static strokes | 6/105 |
| Final-candidate strokes with ≥96 starts | 2/105 |
| Independently replayed local internal paths | 3/105 |
| Conserved-meal connections | 0/156 |
| Persistent event paths | 0/557 |
| Corrected populated idle, including fold/unfold | FAIL |
| Executed complete-meal preparation time | null |
| Candidate allowance, CNY | 436,079.95 |

[phase_summary.json](../../sim/r07/integrator/results/phase_summary.json) gives each stroke’s exact start count, actual time, witness and unresolved status. [motion.json](../../sim/r07/integrator/results/motion.json) separates verified local paths from meal/event precondition failures. The saved count per stroke is literal. A witnessed pass can have fewer than96 starts; unresolved under-budget strokes remain unresolved, never certified impossible. Full96-start coverage of all105 strokes has not been claimed. Every unresolved start has a 20-second allowance; genuine gradient convergence and fully solved poses rejected by the reference can finish early. Numerical step stagnation with a large gradient is not convergence: those interrupted pilot rows are archived under `results/static_v2_numerical_stagnation/` and excluded from the required-start count. No failed or missing pose is promoted to a success.

The gates remain 5 mm / 3°, 10 mm robot/environment and arm/arm, 5 mm gripper/held/environment, PAD=0, μ=0.5, SF=1.5 and 150 N / 15 Nm keyed retention. All 17 force models, tool geometry and finished-product requirements remain unchanged. No purchased item, supplier contact or physical bench test was performed.

## Reachability-first iteration

The grid contains 252 targets per arm: counter/sink samples at eight X coordinates, three depths and three heights with down/front/side approaches, plus samples around both sides of the fixed faucet. Each target receives up to 12 map starts with carriage optimization. The full fixed kitchen, OEM solids, rails, brackets and chain envelopes are present. Opposite-arm geometry is excluded **only from these independent maps**; movable fixtures are omitted there so their locations can be chosen. Final stroke, park and path checks retain both arms and all populated-scene obstacles. These map counts are not substitutes for the 96-start static budget.

| Layout | Principal / 252 | Helper / 252 | Principal tilt; base Y/Z, m | Lanes |
|---|---:|---:|---|---:|
| L01 | 132 | 164 | 149.236°; 0.4034/1.1937 | 2 |
| L02 | 63 | — | 155.000°; 0.3350/1.1900 | 1 |
| L03 | 128 | 156 | 180.000°; 0.3450/1.2400 | 2 |
| L05 | 80 | 72 | 210.000°; 0.3800/1.1900 | 1 |
| L07 | 155 | 173 | 155.000°; 0.3350/1.1900 | 1 |
| L08 | 125 | 159 | 165.000°; 0.4300/1.2000 | 2 |
| L09 | 140 | 162 | 149.236°; 0.4034/1.1937 | 2 |
| L14 | 152 | 171 | 170.000°; 0.3400/1.2400 | 1 |
| L15 | 0 | 157 | 90.000°; 0.5300/1.1850 | 1 |
| L16 | 0 | 0 | 90.000°; 0.4900/1.1850 | 1 |
| L17 | 147 | 162 | 90.000°; 0.4900/1.1850 | 1 |
| L18 | 144 | 155 | 90.000°; 0.4900/1.1850 | 1 |
| L19 | 136 | 163 | 170.000°; 0.3400/1.2400 | 1 |

[Reach/dexterity comparison](../../sim/r07/integrator/renders/reachability_study.png), [full flat target table](../../sim/r07/integrator/results/reachability_map.csv), and per-target joint witnesses under `results/reachability/` retain positions, orientations, failures and Jacobian singular values. Dexterity uses a 0.25 m angular characteristic length; it is a diagnostic metric, not an extra acceptance threshold.

| Iteration | Change / engineering reason |
|---|---|
| L01 | Reproduce v1 geometry at full search budget; baseline map; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L02 | Single high wall lane, bases forward of faucet, original chain band; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L03 | Inverted mounts, high principal rail, compact front stand-off; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L04 | Rear stand-off and opposite mount tilt, vary principal height; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L05 | Single high lane with outward-opening tilted mounts; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L06 | Low principal pivot and asymmetric helper tilt/stand-off; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L07 | Correct L02 cabinet-to-carriage clearance: 85mm carriage needs rail centre <=1.2975m; choose1.29m; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L08 | Intermediate165degree mount: gain front-strip reserve without degenerate vertical rated envelope; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L09 | Keep proven inclined OEM mount, raise main carriage above faucet, full carriage range and movable stations; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L10 | L09 map-selected mount; move full secondary guard and full BFP appliance forward away from lower rail; lower presence sensor out of rail band; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L11 | L10 cleared fixed fixtures; front-facing empty-hand sink control, same sensor position and unchanged process wrenches; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L12 | More vertical inclined main mount165deg, complete BFP at front counter, secondary and peel fixtures at frontmost full-footprint positions; front-facing sink controls; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L13 | Separate full output bowls from secondary guard; three front bowls and greens rear-right of secondary; map-derived sensor-control height; full front staging for inactive arm; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L14 | Forward nearly-inverted mounts: principal invariant shoulder Ymax=.3891, providing10.9mm faucet-spout clearance at carriage crossing, while Ymin=.2483 remains inside parked band; full L13 station layout retained; single lane with preserved carriage order: dual75mm lane pitch cannot pass full85mm carriages; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L15 | Horizontal principal mounting axis into kitchen: fixed shoulder spansY=.287.. .527,Z=1.125..1.245, clearing faucet top and chain underside; retain rear helper155deg and preserve carriage order on one high lane; investigate elbow-opening geometry rather than only near-inverted mounts; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L16 | Repair L15 fixed base/beam collision by moving main base40mm forward; move helper53mm rearward to clear front appliance; move full guide/brackets14mm rearward to separate bracket from chain swept envelope; lower complete dry back-wall power track to avoid carriage adapter sweep, with full presence sensor below it; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L17 | Repair L16 fixed power-track versus outlet-access collision: move complete 70mm track to Z1.100, giving 15mm vertical separation above unchanged access top Z1.050; keep main horizontal mount, rear helper, complete guides/chains and relocated stations; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L18 | Retain repaired horizontal-main rail geometry and move complete peeler/spoon docks plus stored tools to counter rear-right behind appliance, away from helper tuck envelope; no tool or fixture size changes; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |
| L19 | Combine L14 principal mount that clears fixed faucet barriers with L18 rear helper and relocated stored tools that fit the parked band; retain one rail, rear guides and corrected full power-track placement; full rigid stations relocated, bowlsfront, toolsright, stopped removable secondary lid in vertical dock |

The selected report layout is the one retaining the largest admitted full-scene static set and a replayed internal path, not the winner of the fixture-free map alone. L07 has a better independent map but an exact parked shoulder exclusion; L14 removes a fixed faucet barrier but has fewer admitted task strokes. Later horizontal-mount trials are retained as comparisons, not silently mixed into the selected robot.

| Populated park trial | Geometric park pass | Forbidden records | Maximum per-arm band violation, mm |
|---|---|---:|---:|
| L11 | False | 36 | 3.013 |
| L12 | False | 2 | 41.766 |
| L13 | False | 36 | 15.317 |
| L14 | False | 15 | 24.435 |
| L15 | False | 16 | 12.991 |
| L16 | False | 100 | 0.000 |
| L17 | False | 14 | 0.000 |
| L18 | True | 0 | 0.000 |
| L19 | True | 0 | 0.619 |

L15 exposed a fixed principal-base/beam collision. L16 moved the base and guide but its lowered full power track collided with the unchanged outlet-access keepouts. L17 restores 15 mm vertical track/access separation at Z=1.100 m. L18 additionally relocates the complete peeler and spoon docks and stored tools behind the appliance to clear the helper tuck volume. L19 combines that helper/storage arrangement with the L14 principal mount that clears the fixed faucet barrier. Both L18 and L19 obtained collision-free, full-size populated park snapshots. This is positive evidence that these arms can fit the band; it is not a folded-path or meal pass. No collision threshold, source solid or process force is reduced.

L18: 1 admitted canonical strokes across 1 searched strokes; 1 completed 96-start searches. Park snapshot=True; admitted folds=0/2. [All-doors-open snapshot](../../sim/r07/integrator/renders/comparison_L18_parked.png), [separate idle/fold evidence](../../sim/r07/integrator/results/layouts/L18_idle.json). These candidate results are not added to the selected-layout numerators.
L19: 1 admitted canonical strokes across 2 searched strokes; 1 completed 96-start searches. Park snapshot=True; admitted folds=0/2. [All-doors-open snapshot](../../sim/r07/integrator/renders/comparison_L19_parked.png), [separate idle/fold evidence](../../sim/r07/integrator/results/layouts/L19_idle.json). These candidate results are not added to the selected-layout numerators.

The [mount invariant audit](../../sim/r07/integrator/results/mount_invariants.json) uses the UR5e shoulder’s exact source capsule: its axis is J1, so first-joint rotation, downstream motion and carriage X cannot change its Y/Z bounds. L02/L07 intrude into the required parked front-strip clearance; L04/L06 violate the wall clearance for every joint pose. These are candidate-specific exclusions, not optimizer failures.

The independent fixed-carriage audits in `results/layouts/Lxx_carriage_barriers.json` identify faucet collision planes that cannot be repaired by arm IK: the implicated base parts have no arm-joint ancestors, or are the coaxial shoulder capsule. L01/L03/L05/L07/L08/L09/L13 contain such barriers. L14’s revised mount removes those particular fixed-base faucet barriers. Its principal parked geometry improves, but the helper remains in collision. Equal-carriage-X tests also prove that the trial hardware cannot swap carriage order: rigid carriage/adapter parts violate the 10 mm interarm gate at equality, which any continuous order swap must cross. An ordered one-lane meal is still a possible design direction; passing was not established.

L10–L13 relocate the full secondary station, peel fixture, appliance, output bowls and tool docks rather than reducing sizes. Wash/control approaches are moved to reachable orientations and heights. Receiving bowls stay on their own named output lands; a stopped removable full-size secondary lid has a vertical storage slot. The old target-certificate pilot incorrectly included cabinet-door sweep masks as working obstacles and is superseded. The corrected L13 target audit found **0/105** endpoint impossibility certificates; no contrary claim is retained. Map-initialization and opposite-arm filtering bugs are likewise archived and excluded. [Superseded-evidence audit](../../sim/r07/integrator/audit/superseded_v2_evidence.json).

## Selected full geometry and arms

L13 uses 2 rail lane(s), principal base Y=0.430000, Z=1.200000 m at 165.000°, helper base Y=0.427000, Z=1.212596 m at 155.143°. The rail centre heights are [1.29, 1.215] m. The two lanes are retained as a rejected passing candidate, not proof that the arms can pass.

The original wall, counter, fixed faucet/sink, upper cabinets and stove exclusion remain. Cabinet front Y=0.230 m, bottom Z=1.350 m, counter Z=0.850 m and wall face Y=0.600 m are unchanged. There is no portal header, front leg, elevator, storage pallet or wall extension. Each declared rail is 2.42 m × 60 mm × 70 mm. Guides, full carriages, base plates, adapters and de-energize-to-apply rail-brake envelopes are included. Only the four explicitly named bracket rear mating faces touch the wall; ties end at Y=0.589 m.

Two complete 110 mm-radius chain swept envelopes bend in XY, occupying Y=[0.240,0.485] m and Z=[1.275,1.300]/[1.310,1.335] m. Thus the top has 15 mm door-bottom separation; the front has exactly 10 mm placement clearance and zero extra reserve. This is a conservative routing envelope, not an articulated chain qualification. The dry household power track remains in the same under-cabinet band.

| Arm option | Evidence and decision |
|---|---|
| UR5e principal | Full copied 5 kg / 850 mm OEM collision and inertia model. Retains 3 kg payload + 1.2 kg EOAT allocation, subject to the full payload-CoM and mounted torque envelope; no universal 3 kg service-workspace claim. |
| xArm6 helper | Full 5 kg / 700 mm source model; capped at 0.25 kg task load + 1.5 kg EOAT, using the conservative 2 kg long-CoM curve. No helper bowl transport authorized. |
| UR3e smaller helper | 3 kg / 540 mm source specification; a shorter-arm alternative, but no source-matched R07 model, mounted envelope or full task replay admitted. |
| Lite6 | 0.6 kg payload cannot carry the retained 1.5 kg EOAT. A new light gripper and power-loss holding evidence would be required. |

Sources: [UR5e datasheet](https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf), [xArm specifications](https://docs.xarm.ufactory.cc/8.technical_specifications.html), [xArm payload/brake manual](https://www.ufactory.cc/wp-content/uploads/2023/05/xArm-User-Manual-V2.0.0.pdf), [UR3e](https://www.universal-robots.com/products/ur3e-540/), [Lite6](https://www.ufactory.us/product/lite-6). JAKA/Elite/AUBO remain source/model screening options, not invented numerical winners.

The [mounted rated-payload envelope](../../sim/r07/integrator/results/torque_envelope.json) uses full gravity/mass/inertia, OEM 5 kg CoM bounds, two differential-evolution restarts per joint and public-range/self-clear maximizing witnesses. Feasible numerical maxima are conservative denominator estimates, not proven global maxima or published continuous joint torques. Pure base translation reuses an envelope only when mount rotation and source inertias are identical. Missing mounted envelopes now stop admission. OEM documented power-loss holding is the arm-brake basis; actual rail brake/anchor/stiffness qualification remains outstanding.

| Joint order | Rated-payload envelope, Nm |
|---|---|
| UR5e J1–J6 | 31.107, 117.713, 58.933, 25.230, 22.216, 17.168 |
| xArm6 J1–J6 | 29.610, 70.412, 37.717, 8.658, 8.653, 1.483 |

## Appliance, stored objects and corrected idle

The full 510 mm R211 is removed from the under-cabinet installation. The lower BFP610 candidate retains a conservative **395 × 295 × 395 mm solid exterior**, top Z=1.245 m. Regional published dimension ordering is ambiguous; this envelope must not be interpreted as exact feed/lid/disc/bowl geometry. Its 5 mm slicing setting is nominally compatible with the unchanged 4–6 mm root slices, but automatic feeding, batch unloading and terminal recovery remain unqualified. No opening is carved into the solid to obtain a pass. [OEM product](https://www.breville.com/en-nz/product/bfp610).

The OEM manual requires stopped/unplugged handling before lid/disc removal and batch unloading, describes the bowl/lid/pusher interlocks, and warns against unattended use and placement near the counter edge. The autonomous interface is not OEM-qualified. In the frontmost trial the base is only 2.5 mm from the counter edge; that placement remains an explicit installation limitation. All shutdown, unplug, lid, disc, bowl and unload steps remain in the event ledger. [OEM manual](https://assets.breville.com/BFP610/BFP610_ANZ_WEB_IB_A23_LR.pdf).

Appliances remain on the counter. The 5 mm occupancy grid, restricted to original solid countertop/rim surfaces and with 10 mm expansion around stored/fixed objects, leaves a largest clear front-strip rectangle X=[-0.775,-0.115], Y=[0.000,0.080] m, area **0.0528 m²**. The open sink is excluded. At 80 mm depth this is a rim strip; a full human prep bay has not been established, and the selected robot park remains rejected. [Measured counter/arm envelopes](../../sim/r07/integrator/results/counter_and_arm_envelopes.json).

Parking is evaluated with full stored tools and all four output bowls retaining completed-meal contents. Raw inputs are not duplicated after completion. Five actual 18 mm cabinet leaves are shown open at 90°; the whole 0–90° sweep remains above Z=1.350 m. A robot support bound below Z=1.340 m proves the 10 mm sweep separation when satisfied. The doors themselves are **never** tested against the standing corridor. Named wall mating faces are not incorrectly subjected to an incompatible rear-AABB wall gap.

The selected populated snapshot has 36 reported forbidden contact/proximity records (these are not necessarily unique pairs). Snapshot pass=False; full door-sweep sufficient check=True. Three fold/unfold diagnostics use the same populated model and 65-second planning budgets; none gives idle acceptance. Missing or colliding endpoints do not become a valid fold just because a nearby pose fits. [idle.json](../../sim/r07/integrator/results/idle.json).

## Paths, contact policy and conserved meal

R05 reviewer finding 1 is fixed: every window declares `grasp_release_support` or `working_stroke`, its own object identity and its named support. Working permissions are disabled on every nonworking call and cleared after planning. Wrong-object and mislabeled-work-as-support regressions exercise the actual planner state filter. Straight support approach/retreat is limited to 50 mm and its explicit normal; permission ends at the 5 mm gap. No wall, whole station or neighboring guard is a contact window. [Regression results](../../sim/r07/integrator/results/contact_policy_regression.json).

The copied planner is wrapped with the full compiled carriage ranges, removing the old proposal-only R-carriage cap. RRT-Connect has at least 65 seconds, 12-second restarts, staging proposals and 16 shortcut trials; 20 mm search edges remain proposals only. Accepted routes receive model-derived ≤4 mm point-displacement replay, endpoint 5 mm/3° checks, all check-wrench combinations, rated-envelope demand and grip checks. Working strokes must also follow their required Cartesian geometry; an RRT detour cannot replace washing or peeling. Cartesian continuation now includes carriage redundancy and equivalent-angle rebasing.

The retained discrete ledger has 157 expanded strokes, 156 connections, 559 events and 557 required event paths; 49 idempotent commands are removed. Four complete raw inputs total 0.57 kg, with single-valued ownership and 0 discrete chain errors. Full food remains until an accepted partition exists; unsupported cuts cannot delete or shrink bodies. Obsolete R211 lid/pusher proxies are removed from the new persistent scene, while the full BFP exterior stays. Exact new interfaces are marked missing, never credited as a replacement model.

This is still a proposed conserved state sequence, not an executable conserved meal. Continuous grasp/release transforms, jaws, latch/brush/lid travel, supported cup/colander/cassette storage, split-piece/scrap topology and source-matched batch interfaces remain missing. Every connection/event has an explicit precondition status. A zero-time root rejection is not described as a 65-second RRT attempt, and local paths are not concatenated across changing attachment states. [Persistent model](../../sim/r07/integrator/results/persistent_model.json), [state sequence](../../sim/r07/integrator/results/state_sequence.json).

All retained forces and products are unchanged, including 63 N peeling drag, 152.623/183.162 N carrot/potato transverse cutting checks, 348.852 N greens cutting, 636.365 N tomato wedging and 52.328 N / 0.5233 Nm eye/core work. Existing food/species/process-transfer limitations remain explicit; these are not BFP feed-force qualifications. [Primary slow-cut measurements](https://iseki-food-ejournal.com/article/69/pdf), [tomato tissue proxy study](https://www.sciencedirect.com/science/article/pii/S0925521401001338), and the source/derivation catalog in [process_v3.json](../../sim/r07/integrator/results/process_v3.json) document the basis.

## Executed-path timing, clearance and cost

The sum of verified isolated internal-path durations is **106.697 s**, on separate local clocks; complete-meal `prep_min` remains **null**. Home limits are 0.35 rad/s and 0.35 rad/s² for joints, 0.1 m/s loaded or 0.2 m/s empty rail speed, 0.3 m/s² rail acceleration, and a 0.05 m/s / 0.3 m/s² whole-geometry point bound. Timing uses rest-to-rest triangle/trapezoid segments. Required soak 600 s, fill 501.6 s at 6 L/min, three potato rinses, drain 30 s, inspection and cleaning remain explicit; unmeasured batch-appliance time is null. [schedule.json](../../sim/r07/integrator/results/schedule.json).

| Clearance reserve above gate, mm | Minimum | 5th percentile | Median |
|---|---:|---:|---:|
| robot_environment | 0.536679 | 173.773 | 642.308 |
| arm_arm_or_frame | 2.028267 | 87.758 | 474.081 |
| self | 2.000482 | 49.006 | 461.876 |
| held_gripper_environment | -0.000006 | 290.519 | 860.347 |

These are conservative lower reserves over 1259 accepted local-path states, maximum point step 3.999709 mm. Intended-contact infinite sentinels are excluded; distant pairs still dominate percentiles. Small numerical tolerance is reported separately from physical clearance. No meal distribution or positive reserve is inferred from failed poses. [clearance.json](../../sim/r07/integrator/results/clearance.json).

The allowance is CNY **379,199.96** base + **56,879.99** reserve = **436,079.95**. The reserve is 15%, applied exactly once. One 18,000 CNY home-safety package covers presence pause, E-stop, RCD/PE, interlocks and interfaces; braked rail drives remain in the rail-system allowance. No industrial safety package, elevator or pallet is added. The 43,000 CNY rail-system allowance is retained conservatively for revised mounts and two carriages even in a single-lane trial. These are historical engineering allowances, not current quotations or a cheapest passing configuration. [costs.csv](../../sim/r07/integrator/results/costs.csv).

## Renders and reproducibility

- [Overview](../../sim/r07/integrator/renders/overview.png)
- [Rejected populated park, all doors open](../../sim/r07/integrator/renders/parked_doors_open.png)
- [Under-cabinet band](../../sim/r07/integrator/renders/under_cabinet_band.png)
- [Rejected passing frame](../../sim/r07/integrator/renders/passing.png)
- [24 checked local-path frames: Q05.carrot__helper_index_4](../../sim/r07/integrator/renders/executed_local_strip.png)

CPU Blender renders actual unscaled MJCF geometry at ≤1600 px. The frame strip comes from an accepted local trajectory and is explicitly labeled as neither a connected meal nor physical-robot video. Failed park/passing frames are labeled. Source q, model, path and interpolation locations are in [frame_manifest.json](../../sim/r07/integrator/results/frame_manifest.json). Opposite wall/cabinets and symbolic masks are hidden only for display.

All 90 copied R05 Python files and upstream originals remain byte-identical. New `*_v2_r07.py` adapters implement layout search, full-range proposal IK, contact-policy reuse, path replay and aggregation without changing acceptance. The fixed kitchen and OEM solids/inertias are retained. All jobs use the supplied MuJoCo3.2.5/mink venv through `bounded.py`, foreground chunks under20minutes, at most3 numerical workers, CPU only and1900MiB worker-tree caps. Across retained v2 static attempts, actual search time is 5.616 worker-hours; this is not elapsed human time. [iterations.csv](../../sim/r07/integrator/results/iterations.csv) includes v1 history, each layout/map/start, interrupted pilots, planner attempts and resource logs. [delivery_audit.json](../../sim/r07/integrator/results/delivery_audit.json) separately reports artifact/rule fidelity, budget coverage and failed engineering gates.

Main reproduction entries: `candidate_v2_r07.py <layout>`, `static_v2_r07.py <layout> <lo> <hi> 990 96`, `motion_v2_r07.py <layout> internal <indices...>`, `idle_v2_r07.py <layout>`, `persistent_v2_r07.py <layout>`, `deliver_v2_r07.py <layout>`, `measure_export_v2_r07.py <layout>`, `render_batch_v2_r07.py` and `write_post_v2_r07.py`. A 96-start run is resumable from its last saved row; superseded pilot directories are never resume inputs.
