建议把厨房机器人当成“小型食品加工工作站”来设计：机械臂负责装卸、清洗、检查和搬运整只容器；一台带护罩的固定切配机负责根菜切片、青菜切段和番茄八瓣。削皮仍用带限深和正向受力接口的 Y 型削皮器，蔬菜两端由被动端杯支承。洗菜不等于甩干：青菜必须拆开、逐一洗净根部褶皱，最后靠沥水完成。无需躯干、移动底座、电池、气源或自动腕部换刀机构。

本轮定义 **27 个 Q 阶段、36 个按食材展开的检查记录、1 台有源切配设备、18 种自定义零件设计**。工具范围预算 **14,149.96 元**，加 20% 预留为 **16,979.95 元**；其中已核实的中国零售价仅包括四只碗共 79.96 元，其余选中件主要是明确标注的工程预算，不是供应商报价。双夹爪另列 24,000 元，机械臂、轨道、导电轨、安全扫描器和安装费用由相应角色负责。本轮未采购、未联系供应商。

交付包含 FreeCAD 实体、STEP、1500×840 布局图、物料表、方案评分和带来源/裕量的载荷 JSON。22 项文件、几何和计算检查通过；**这不代表 IK、完整运动路径、食品质量或安全认证通过**。Nemco 刀盘接口、装卸时的连续支承、实际电机运行扭矩、机械臂输出额定扭矩与制动器证据仍是制造/集成前的验收条件。番茄与青菜的载荷明确采用物理或材料代理，不能冒充实测切割力。

**Engineering decision and deliverables**

The recommended production form is a mains-powered, fixed cutting cell with removable food-path cartridges, supported washing/peeling, and whole-container delivery. R performs loaded handling, peeling and core work; L exposes leaf creases, brushes supported produce, and indexes roots while R's peeler is parked. One arm could perform these tasks sequentially, but would need additional leaf orientation nests and more regrasping. The helper is retained for crease access rather than carrying heavy appliances.

Use the existing xArm6 model as the kinematic handover candidate: the manufacturer specifies 5 kg payload and mounting in any direction. R must qualify a 3 kg load at the tool with an end-effector allowance of at most 1.6 kg, leaving a 4.6 kg combined envelope; the proposed process actually holds at most 1.0 kg in R after removing unnecessary tool mass. L has a 1 kg task cap. Its actual peak is reported below. The xArm7's 3.5 kg allocation is insufficient for the same allowance. Exact torque/CoM and spring-brake evidence are approval gates for the selected hardware generation. [UFACTORY specifications](https://docs.xarm.ufactory.cc/8.technical_specifications.html)

Machine forces close between blade, food support and the fixed frame. Arms withdraw before powered motion. This does not erase loading forces, gravity, inertia, brush reaction or the full appliance mount load. The initial cutting speed is deliberately restricted to the literature's speed range. There is no throughput claim: a 35 mm carrot chord at 0.5 mm/s takes about 70 seconds of engaged cutting per slice. Faster production needs measured force/quality trials; commissioning this way can take tens of minutes per root batch.

Files:

- [Checker handover JSON](../../sim/r02/tools/results/process_v2.json), [expanded pose CSV](../../sim/r02/tools/results/phase_handoff.csv), [BOM](../../sim/r02/tools/results/tools_bom.csv), [cost basis](../../sim/r02/tools/results/cost_summary.json).
- [Full buy/adapt/build scoring CSV](../../sim/r02/tools/results/options_scores.csv), [scoring JSON](../../sim/r02/tools/results/options_scores.json), [source ledger](../../sim/r02/tools/research/sources.json).
- [FreeCAD custom-part library](../../sim/r02/tools/cad/custom_parts.FCStd), [custom STEP](../../sim/r02/tools/cad/custom_parts.step), [counter assembly](../../sim/r02/tools/cad/counter_layout.FCStd), [counter STEP](../../sim/r02/tools/cad/counter_layout.step), [individual STEP folder](../../sim/r02/tools/cad/step/), [CAD manifest](../../sim/r02/tools/cad/cad_manifest.json).
- [Validation evidence](../../sim/r02/tools/audit/delivery_validation.json) and [reproduction instructions](../../sim/r02/tools/README.md).

![Dimensioned plan](../../sim/r02/tools/renders/layout_plan.png)

![CAD perspective, loading doors open](../../sim/r02/tools/renders/layout_perspective.png)

**Required finished products**

These are transcribed from [cook_ref](../../inputs/cook_ref.md) and [key poses](../../inputs/keypose_cook.md). Washing/cutting only; no cooking or plating. Inspection is ten distributed pieces, or all if fewer; inspect every tomato wedge and every basal crease. At least 98% of *all cut edible mass* must reach the separate next-step containers. Rejected bad input is distinguished from edible process losses.

| Product and reference input | Required end state |
|---|---|
| Carrot, 160×35×35 mm, 0.12 kg | Fully washed and peeled. Peel depth 0.2–0.8 mm, maximum gouge 2 mm; no visible peel patches. Ends trimmed 3–5 mm. Round or half-round slices 5±1 mm; within-slice variation ≤1 mm. No bridges, crushing or splintering. Explicitly cut a 10 mm terminal stub into a 5 mm slice and release the last 5 mm edible slice intact. |
| Potato, 90×65×70 mm, 0.20 kg | Washed, peeled to the same depth/gouge limits, eyes and shallow blemishes removed. Reject green, deeply sprouted, rotten or deeply damaged input. Round/half-round 5±1 mm slices, ≤1 mm within-slice variation, terminal edible pieces included. Rinse the cut pieces with 2–3 fresh water changes until no white swirl; drain 20–30 s without a puddle. |
| Bok choy, 170×100×70 mm, 0.10 kg | Remove 5–10 mm root disk, separate stalks, expose/rub/inspect every basal crease. No soil, grit or rotten leaf tissue. Split stalks wider than 15 mm; cut 30–50 mm sections, nominal 40 mm. Bundles ≤30 mm high; fully severed fibres and no maceration. Drain without wringing. |
| Tomato, 70×70×60 mm, 0.15 kg | Wash and retain skin. Remove hard stem core without entering the seed cavity. Eight radial wedges, nominal 45°, each 35–55°; each mass 0.65–1.35 times the mean. Every skin edge severed; pulp/seeds attached, no bruising or collapse. |

Optional potato julienne retains 2–3 mm on each cross-section axis, length 30–80 mm and ≥90% intact mass. It is **not silently substituted for the slice baseline** and is not counted in the baseline hardware. A dedicated 2.5 mm cartridge would need trials; Robot-Coupe's actual 2.5×2.5 mm disc 18389 is a buy alternative. [Manufacturer disc list](https://www.robot-coupe.com/cn/zh/p/vegetable-preparation-machines-cl-50/20672)

**Broad alternatives and why this combination**

The complete scoring table below covers buy, adapt and build for washing, peeling, each food's cut, holding, transfer, peel disposal, delivery and tool exchange. Six scores run from 1 (poor) to 5 (good): finished-product quality Q, robot ease R, blade safety S, cleanability C, low cost $, and low noise N. Weighted score = 0.30Q+0.25R+0.15S+0.15C+0.10$+0.05N. Scores are engineering judgments about achievable operation, conditional on qualification; a 5 is not a measured quality result. An incompatible cut or footprint rejects an option regardless of weighted score. Noise is qualitative; no dB data were invented. The CSV additionally gives force envelope, precision, grasp/regrasp estimates and rejection reasons.

China price anchors are public observations, with their limits retained:

- IKEA BLANDA BLANK: 20 cm stainless bowl, 9 cm high, listed 19.99 CNY; 0.22 kg is package mass, conservatively used as a bowl mass allowance. IKEA UPPFYLLD: 23 cm, 16.5 cm high, manual spinner, 19.99 CNY, hand wash only. The selected insert is stainless rather than the PP spinner mechanism. [BLANDA](https://www.ikea.cn/cn/zh/p/bu-lang-da-bu-lan-ke-shang-cai-yong-wan-bu-xiu-gang-30166051/), [UPPFYLLD](https://www.ikea.cn/cn/zh/p/uppfylld-wu-pu-fei-er-de-sha-la-shuai-gan-ji-bai-se-40521951/)
- Robot-Coupe CL50 has a genuine 5 mm slicing disc. A China seller advertises the base without discs at 10,500 CNY and lists 350×320×590 mm, 550 W/230 V, 25 kg. This listing's generation must be checked. At 590 mm high it conflicts with the inherited 500 mm cabinet clearance; it also cannot replace all greens/tomato outputs. [Official cut system](https://www.robot-coupe.com/cn/zh/p/vegetable-preparation-machines-cl-50/20672), [China seller advertisement](https://www.21food.cn/productshow/3244917.html)
- Blaupunkt BP-QC02 is a real 60 W, 1.5 kg electric cutter; its manual limits continuous operation to one minute followed by at least five minutes rest. The historical China promotion lists 399 CNY before discounts. It does not establish flat 5 mm slices, so low price alone does not select it. [Manufacturer manual](https://blaupunkt.com/wp-content/uploads/2024/06/BP-QC02电动切菜机-说明书.pdf), [2024 price observation](https://www.smzdm.com/p/118488221/)
- China Post's 2025 procurement gives a 4,190 CNY unit ceiling for a 1.8 kW potato peeler. This is a procurement ceiling, not retail. Hento advertises industrial carrot peelers at 9,000–42,000 RMB. Batch abrasion cannot establish the reference peel depth, carrot coverage or complete eye removal. [Public notice](https://www.chinapost.com.cn/cn/report/2510/0438-1.htm), [Hento](https://hentomachine.cn/product/Carrot-Peeling-Machine.html)
- Antai advertises a bubble/spray wash-and-dry line at 58,000 CNY. Its narrative lists 3,600×1,440×1,520 mm, 4.6 kW and 1,200–2,000 kg/h, while the header conflicts with these dimensions/power. It is a scale/cost comparator, unsuitable here, and still does not prove inner-crease cleaning. [Manufacturer advertisement](https://www.zcatspjx.com/products/show4295932.html)

Nemco's whole manual eight-wedger is 203.2×203.2×482.6 mm and 2.04 kg. The static height leaves 17.4 mm below the assumed cabinet, so height alone does not fail the 10 mm gap. Its high handle and arm press path still need clearance, and its reaction remains an arm load. Adapting the 428-8 blade and 55434 pusher into the lower guarded frame removes that arm press operation. The manufacturer names tomato use, but this does not prove the specified mass/angle/bruise quality. China matched pricing is not disclosed; 1,300 CNY is an import allowance. [Nemco](https://nemco.com/catalog/easy-wedger/), [dimensions](https://nemco.com/wp-content/uploads/2025/06/c9bb50b8-9645-4786-b5ff-fd07fe8a7881.pdf)

Starfrit's automatic Rotato reduces robot peeling motion but leaves eyes/end touchup and unproven tapered-carrot coverage. OXO's adjustable mandoline can make nominal slices, but the holder/remnant path and repeated wet high-force arm strokes remain. Food-safe soft grippers and vacuum cups are real options; their wet-food reliability, air equipment and China price are unresolved. A vacuum cup is not credited with an untested seal on wet greens. [Starfrit](https://www.starfrit.com/en/starfrit-rotato-express-electric-peeler), [OXO](https://www.oxo.com/more-oxo/chef-s-mandoline-slicer-2-0.html), [mGrip](https://www.softroboticsinc.com/uploads/2021/03/Soft_Robotics_ModularGripping_800129_RevD_LR.pdf), [SMC food-contact vacuum cup](https://www.smc.com.cn/webcatalog/en-jp/equipment-for-the-food-manufacturing-industry/vacuum-equipment/HF3A-ZP3F-E/)

Several less conventional ideas were considered explicitly. A rotary peeling lathe could make arm motion simpler but adds washable spindles, variable-root centering and another guarded drive; end/eye cleanup remains. A spray tunnel or bubbling tank does not expose closed leaf bases. Water-flushed peel disposal risks clogging and hides contaminated wet surfaces. A bowl carousel duplicates the rails' transport function. A dock-actuated automatic wrist changer adds retention/release failure modes; gripping keyed passive implements achieves autonomous tool exchange after manual wrist setup. A sequential draw-knife cartridge is the fallback if the bought tomato grid crushes fruit; it must earn a measured force/quality model before adoption. No fallback is counted as validated or in this BOM.

The selected gripper interface uses removable food-contact pads/fingers, a bottom-support cup for soft food, and positive keyed handles for tools and bowls. DH's PGC14050 brochure lists IP67, 1 kg, 40–140 N **per jaw**, 50 mm stroke and a 7 Nm moment limit. IP67 does not make its original fingers food-safe; 7 Nm does not prove the checker's 15 Nm key proof. A stronger end effector or direct wrist load bypass is necessary if the 15 Nm proof includes the entire gripper. Loose 0.1 kg greens need only 2.943 N total normal from SF1.5·mg/μ; use bottom support and calibrated ≤5 N passive food-pad force, with motor force carried by the cup key rather than the food. Root handling uses the motor's minimum 80 N total through broad padded fingers. Do not command 35 N total on this motor. Root-damage trials are required; if 80 N marks roots, use force-limited sprung fingers or a lower-force food interface. Peeling reaction goes through the end stop, not extra squeeze. The binding checker still uses 150 N total normal and its original μ/SF. [DH brochure](https://en.dh-robotics.com/wp-content/uploads/2024/07/DH_Electric-Gripper-Brochure.pdf)

Commercial manual changers remain maintenance options, while an ATI QC18 pair adds 1.77 kg. This leaves insufficient allowance for gripper and a full 3 kg tool load on a 5 kg arm. The custom C01/C02 interface is a fixed bolted master/mate and antirotation dowels, not a claimed automatic changer. C03 is the common robot pickup interface. [SCHUNK manual system](https://schunk.com/cn/zh/press/shu-miao-nei-qing-song-huan-dao/17344), [ATI](https://www.ati-ia.com/products/toolchanger/QC.aspx?ID=QC-18)

**Process forces and load application**

All screening values come from the following models, not from an IK/torque pass target. Gravity is added once through actual held mass/CoM. Cartesian vectors in the JSON are counter/world aligned. Margin loads are evaluation cases, not commands to press produce until it yields.

| Model | Nominal → design | Derivation, application and limitation |
|---|---:|---|
| Carrot transverse cut | 76.31 → 152.62 N | (67.59 N/31 mm)·35 mm, ×2. Fixed cell. |
| Potato transverse cut | 91.58 → 183.16 N | (61.49 N/47 mm)·70 mm, ×2. Fixed cell. |
| Greens cut/root trim | 174.43 → 348.85 N | Carrot coefficient·80 mm total engaged width, ×2. Tissue surrogate, **not measured bok-choy resistance or a guaranteed upper bound**. |
| Tomato grid | 318.19 → 636.38 N | Effective penetration stress 15 N/(π·2² mm²), four diametral edges totaling 280 mm, 0.952 mm blade envelope, ×2. Structural proxy only. |
| Peeling drag | 42 → 63 N | Literature 1.68 N/mm·25 mm maximum peel ribbon, ×1.5. R load in −X; potato transfer explicitly a proxy. |
| Peeler normal | 5 → 7.5 N | Calibrated 1,000 N/m spring ×5 mm deflection, ×1.5, +Z reaction on R. |
| Eye/core tool | 26.16 → 52.33 N | Root coefficient·12 mm engaged edge, ×2; test both lateral directions and upward, plus 0.524 Nm scoop moment at 10 mm lever. Proxy, depth stops and inspection required. |
| Root brush | 6 → 9 N | 1,000 N/m ×6 mm deflection, ×1.5; root supported in sink during stroke. |
| Leaf brush / tomato wipe | 2 → 3 / 1 → 1.5 N | 400/200 N/m ×5 mm, ×1.5. Opposing reaction included on R's food cup during paired L brushing. |
| Cleaning pad | 2.5 → 3.75 N | 500 N/m ×5 mm, ×1.5. No exposed sharp-edge wipe. |
| Cold-water jet | 0.1273 → 0.1910 N | ρQ²/A at 6 L/min and 10 mm outlet, ×1.5. Add to wash loads; verify flow limiter. |
| Cassette/latch insertion | 7.7255 → 11.5883 N | μslide0.5·1.1 kg·g +1.1 kg·0.3 m/s² +2 N latch spring; ×1.5. Both ±Y directions. |
| Internal feed index | 5.7255 → 8.5883 N | Same moving-tray friction/inertia without latch spring, ×1.5. Internal drive/mount load; blade disengaged during indexing. |
| Free carry | m·0.3 → m·0.45 N | Each pose's own mass, both lateral directions and upward; gravity separate. |
| Passive end-cup preload | 10 → 15 N | 1,000 N/m ×10 mm spring, ×1.5; positive opposite axial stop also reacts 63 N peel drag. |

The root source used 0.952 mm blades, 15–25° edge angles and **20–40 mm/min**, with reported carrot/potato cutting peaks 47.90–67.59/43.68–61.49 N. Width scaling and ×2 variation factors are transparent sizing approximations, not population bounds. Initial 0.5 mm/s =30 mm/min; do not extrapolate these data to 20–60 mm/s robot motion. [Singh, Das & Das 2016](https://iseki-food-ejournal.com/article/69/pdf)

The peeling abstract reports 1.68 N/mm and 16–32 N, with 90.72% peeling rate. Full text was unavailable, so the source is explicitly abstract-level. Repeated inspection/touchup is necessary for the complete-peel requirement; this publication alone does not demonstrate it. [Xie et al. 2025 publisher record](https://www.qikan.com.cn/article/5dd020251220.html)

The tomato model uses the 2–15 N tissue peaks under a 4 mm cylindrical probe at 3 mm deformation. These are penetration/compression measurements, **not blade force**. The newer paper's N/mm skin-firmness values mean per millimetre of probe displacement and were not confused with force per millimetre of blade. The 636 N proxy sizes the structure; real force-displacement curves and wedge inspection must define operating limits. Stop/reject crushing fruit, rather than increasing force to this structural number. [Wu & Abbott 2002](https://www.sciencedirect.com/science/article/abs/pii/S0925521401001338), [Vieira et al. 2019](https://repositorio.bc.ufg.br/bitstreams/71b8aa0d-e688-48a3-9207-8166a44fe47d/download)

Own physics is explicitly dimensioned: Hooke springs are design values to be calibrated, Coulomb sliding uses a conservative assumed 0.5, and acceleration is limited to 0.3 m/s² nominal. Ensinger's 0.21 dry dynamic POM coefficient is not substituted for unknown wet friction. A 2:1 clamp lever requires 7.5 N at the handle for the 15 N preload; a 2 N latch plus 1 N friction allowance gives 10.5 N, within the 11.588 N insertion screen. That lever ratio/friction needs measurement before release. [POM manufacturer properties](https://www.ensingerplastics.com/en-us/shapes/acetal-tecaform-ah-natural)

The fixed frame's **1,000 N structural design envelope** exceeds the largest 636.38 N modeled process screen. It is a hardware rating requirement, not fabricated food force. At 5 mm screw lead and assumed efficiency 0.85, (1,000+1 kg·g)·0.005/(2π·0.85)=0.946 Nm, requiring at least 1.0 Nm continuous running torque at ≤10 rpm. The displayed 57 mm motor envelope has a public 3 Nm **holding** rating and is not approved by that fact. A spring-applied crosshead brake and mechanical parked-blade catch are mandatory. [Motor comparator](https://www.omc-stepperonline.com/nema-23-bipolar-3nm-425oz-in-4-2a-57x57x114mm-4-wires-stepper-motor-cnc-23hs45-4204s)

**Phase handover, coordinate convention and recipe loops**

Counter origin is world (0,0,0.850 m); X runs along the counter, Y from front edge toward the wall, Z upward. Hand `pos` is the gripper grasp site, not the blade point. R01 tool +X is approach; jaw/roll resolve the tool transform. Work/CoM offsets, primitives, masses and vector alternatives must be transformed together. The same actual food is both mass and collision geometry; never add its gravity twice. The CSV expands every phase, arm and endpoint. Use `checker_instances` (36 records) as the preferred sim input; 27 templates are the logical process definitions.

Q01 once; carrot Q02–Q05, Q07–Q10, Q12; potato Q02–Q12; then Q13–Q27. Carrot skips eye-removal Q06 and starch rinse Q11. Expanded Q12 delivers only that ingredient's bowl. Q05 carrot surface is (−0.935,0.170,0.1175), potato surface (−0.935,0.170,0.135); peeler grasp is 65 mm above each. Potato peeling stroke is 60 mm, carrot 120 mm, with shorter local touchup. L only indexes after R's blade is parked 80 mm above the surface.

Nominal approach/retreat is 100 mm; insertion drawer stroke 120 mm along Y. Transport through left/sink waypoints at Z=0.300; loaded bowls crossing the cell use Z=0.575 to clear the 0.375 m appliance while staying in the front travel corridor. These are route constraints, not a continuous collision verdict. The front-pointing food-cup handle uses jaw axis +X during cell loading; the candidate grasp is (0.400,0.140,0.280), with cup floor (0.400,0.290,0.180). **A support must meet the food before cup withdrawal.** The matched cartridge's loading support stroke is not resolved by public Nemco dimensions; dropping a tomato 70 mm is prohibited. This approach datum is reviewable, but the completed supported handoff/path is still an integration gate.

The four bowl output grasp sites are (−1.665,0.435,0.180), (−1.415,0.435,0.180), (−1.165,0.435,0.180), (−0.915,0.435,0.180). In the cell's withdrawn drawer the bowl bottom is Z=0.030 and grasp (0.400,0.110,0.210). Remove its bail after seating, so no bar crosses the feed path; reattach only after blade park and drawer withdrawal. Root chute top is taken from native CAD at Z≈0.11546, giving 29.54 mm initial drop from Z=0.145. Tomato pad/grid mode requires ≤10 mm drop and a separately matched nest height.

For roots choose n≈L/5 mm and require 4≤L/n≤6 mm. Retain the explicit 10 mm stub case. For greens choose an integer n between ceil(L/50 mm) and floor(L/30 mm), nearest L/40 mm. The comb's 15 mm wall pitch minus 3 mm wall thickness leaves 12 mm clear slots; use ≤12 mm strips, satisfying the ≤15 mm finished limit. If no feasible section count exists, flag finished-quality failure rather than discarding a short edible remainder as invisible trim. Emptying, missed pieces and final remnants remain in the ≥98% mass denominator. Bowl tare/inspection and recovery validate the intended yield; it has not been measured here.

**Q phase definitions**

The table gives endpoint grasp sites and current arms/tools. Every listed load uses the preceding model table with its margin; appliance cut rows still include arm loading and withdrawal segments in JSON. Paths and simultaneous paired support are fully enumerated there.

| Q | Operation | Arms/tools and endpoint grasp sites (counter m) | Loads / expected outcome |
|---|---|---|---|
| Q01 | Stage vessels and start water with produce parked | R:colander (-0.4,0.3,-0.045); R:key_handle (-0.4,0.39,0.15) | handle_carry; Dedicated dirty tray, four clean bowls; cold water flow capped6 L/min |
| Q02 | Pick and wash each root | R:root_food (-1.615,0.17,0.215); R:root_food (-0.4,0.3,0.05); L:wash_pad (-0.36,0.3,0.025) | handle_carry, root_rub, water_jet; No visible soil at ends, eyes or entire root surface |
| Q03 | Load dirty peel support and clamp | R:root_food (-0.935,0.17,0.1); R:key_handle (-0.935,0.17,0.165) | drawer_insert, handle_carry; Root supported against positive axial end stop; fingers clear of peel path |
| Q04 | Acquire retained peeler | R:peeler (0,0.105,0.195) | handle_carry; Tool retained on matching key lands |
| Q05 | Peel all root surfaces with supported indexing | R:peeler (-0.875,0.17,0.1825); L:root_food (-0.895,0.17,0.2); R:peeler (-0.935,0.17,0.2625) | handle_carry, peel_drag, peel_normal; No visible peel patches; peel.2–.8 mm and gouges<=2 mm |
| Q06 | Remove eyes and local blemishes | R:eye_core_spoon (0,0.495,0.23); R:eye_core_spoon (-0.935,0.17,0.215) | eye_core, handle_carry; No eye tissue; defective green/sprouted/rotten inputs rejected |
| Q07 | Collect peels and clean dirty work support | R:peel_bin (-0.935,0.09,0.155); R:wash_pad (-0.935,0.17,0.12) | cleanup_wipe, handle_carry; Peels contained in removable bin; dirty support clean before new root |
| Q08 | Rinse peeled root and park before water off | R:root_food (-0.4,0.3,0.05); R:key_handle (-0.4,0.39,0.15) | handle_carry, water_jet; No peel fragments; clean root supported in colander |
| Q09 | Install clean root cartridge and cooking bowl | R:cut_cassette (0.4,0.185,0.18); R:root_food (0.4,0.1,0.16); R:carried_bowl (0.4,0.11,0.21); R:bowl_bail (0.4,0.11,0.34) | drawer_insert, handle_carry; Selected clean cartridge and bowl latched; guard closed |
| Q10 | Guarded end trim and5 mm slicing | R:key_handle (0.4,0.065,0.28) | carrot_cut, handle_carry; All edible root slices4–6 mm including terminal remainder, trimmed ends in separate scrap catcher |
| Q11 | Potato pieces starch rinse and drain | R:carried_bowl (0.4,0.11,0.31); R:colander (-0.4,0.3,0.05); R:colander (-1.295,0.17,0.18) | handle_carry, water_jet; Nearly-clear last rinse; pieces separated; no free puddle |
| Q12 | Deliver separate root bowls | R:carried_bowl (-1.665,0.435,0.18) | handle_carry; Carrot and potato bowls supported in labelled left-rear bays |
| Q13 | Coarse wash greens | R:food_cup (-1.465,0.17,0.215); R:food_cup (-0.25,0.3,0.05) | handle_carry, water_jet; External soil removed; rotten/yellow leaves rejected |
| Q14 | Trim greens root disk in guarded dirty cassette | R:food_cup (0.4,0.14,0.28); R:key_handle (0.4,0.185,0.18) | drawer_insert, greens_cut, handle_carry; 5–10 mm root disk removed; stems detached |
| Q15 | Expose each loose basal crease | R:food_cup (-0.31,0.3,0.055); L:food_cup (-0.19,0.3,0.055) | leaf_separate; Every inner stalk/leaf base accessible without tearing |
| Q16 | Soak, rub each crease and fresh-water rinse | R:food_cup (-0.25,0.3,0.055); L:wash_pad (-0.4,0.3,0.04); R:food_cup (-0.25,0.3,0.055) | handle_carry, leaf_rub, water_jet; Every basal crease and final rinse free of grit |
| Q17 | Drain greens without spinner | R:colander (-0.4,0.3,0.055); R:colander (-1.295,0.17,0.18) | handle_carry; No continuous dripping stream; no torn leaves |
| Q18 | Split stalks wider than15 mm | R:food_cup (0.4,0.14,0.28); R:key_handle (0.4,0.185,0.18) | drawer_insert, greens_cut, handle_carry; Every stalk<=15 mm wide |
| Q19 | Arrange low bundle and cut40 mm sections | R:food_cup (0.4,0.14,0.28); R:key_handle (0.4,0.185,0.18) | drawer_insert, greens_cut, handle_carry; 30–50 mm sections, no attached fibres or maceration |
| Q20 | Deliver greens bowl | R:carried_bowl (0.4,0.11,0.31); R:carried_bowl (-1.165,0.435,0.18) | handle_carry; >=98%ediblegreens in next-step bowl |
| Q21 | Wash tomato in supporting cup | R:food_cup (-1.465,0.17,0.215); R:food_cup (-0.25,0.3,0.05); L:wash_pad (-0.4,0.3,0.085); R:food_cup (-0.25,0.3,0.055) | handle_carry, tomato_rub, water_jet; Clean skin retained; drain10 s; no bruising |
| Q22 | Remove hard stem core in supported cradle | R:eye_core_spoon (-0.935,0.17,0.235) | eye_core; Hard stemtissue absent; seedcavities intact |
| Q23 | Install8-sector cartridge, bowl and tomato | R:cut_cassette (0.4,0.145,0.18); R:food_cup (0.4,0.14,0.28); R:key_handle (0.4,0.185,0.18) | drawer_insert, handle_carry; Centered stemaxis, correctblade/pusher identified, bowl supported |
| Q24 | Powered8-wedge press, arms detached | R:key_handle (0.4,0.065,0.28) | handle_carry, tomato_wedge; Eight35–55deg wedges with0.65–1.35meanmass; intactpulp andseeds |
| Q25 | Recover and deliver tomato wedges | R:carried_bowl (0.4,0.11,0.31); R:carried_bowl (-0.915,0.435,0.18) | handle_carry; Eightwedges and>=98%ediblemass in next-stepcontainer |
| Q26 | Inspect all finished products and present cooking containers | R:carried_bowl (-1.665,0.435,0.18); R:carried_bowl (-1.415,0.435,0.18); R:carried_bowl (-1.165,0.435,0.18); R:carried_bowl (-0.915,0.435,0.18) | handle_carry; Allrequiredqualitygates passed or batch explicitlyrejected; fourseparatelabelledcontainers |
| Q27 | Clean, drain and dock all tools; water off | R:wash_pad (-0.4,0.3,0.025); R:peeler (0,0.105,0.095); R:wash_pad (0,0.3,0.095); R:key_handle (-0.4,0.39,0.15) | cleanup_wipe, handle_carry; Peeler,pad,spoon,coveredknifecartridges clean/dry/stored; scraplidded |


The phase operations in JSON additionally require potable cold water, supported orientation changes, no in-hand rolling, visual cleanliness rather than time-only washing, peeler depth limits, root trimming, flat registered support, width splitting, stem-axis centering and final inspection. Q26 rejects food that fails the end-state gates; expected outcomes are not assertions of trial success.

**Old P01–P16 crosswalk**

T08 was a key-pose screening list rather than a complete food recipe. Its nominal 50 N/70 N tomato press was not retained as a justified new-grid force. Its 200 mm mandoline strokes are replaced by local fixed-machine indexing. P14's tray tilt is replaced by keeping the next-step bowl under the enclosed cut and transporting that bowl. Added wash/core/eye/starch/terminal/cleanliness operations preserve the finished products instead of inheriting omissions.

| Old | What it did | New replacement |
|---|---|---|
| P01 | Pick carrot and lift100 mm | Q02 carrot root handling |
| P02 | Rinse carrot, wrist-60 to+60 deg | Q01/Q02/Q08 supported full washing |
| P03 | Place carrot on clamp board | Q03 passive end cups/axial stop |
| P04 | Peel clamped carrot,120 mm stroke | Q04/Q05/Q07 peel, index, contain scraps |
| P05 | Load carrot into mandoline holder | Q09 register clean feed cartridge |
| P06 | Push mandoline holder200 mm; carrot slices | Q10 carrot 5 mm index + explicit final stub |
| P07 | Pick potato | Q02 potato handling |
| P08 | Rinse potato, wrist-60 to+60 deg | Q01/Q02/Q08 full potato washing |
| P09 | Peel clamped potato | Q04–Q07 potato peel and eyes |
| P10 | Push mandoline holder200 mm; potato slices | Q10 potato slice; Q11 starch rinse |
| P11 | Greens placed in rinse basket; spinner pump | Q13/Q15–Q17 individual creases, gravity drain |
| P12 | Greens knife cuts at40 mm spacing | Q14 root trim; Q18 width split; Q19 sections |
| P13 | Tomato wedger press50 N nominal,70 N check | Q21–Q24 tomato wash/core/guarded grid |
| P14 | Lift catch tray, tilt60 deg into output bowl | Q09/Q11/Q12/Q20/Q25 whole bowl delivery |
| P15 | Y-peeler pickup/return | Q04/Q27 peeler pickup/clean dock |
| P16 | Knife pickup/return | Q09/Q18/Q23/Q27 covered cartridge exchange |


**Counter layout, power and free-moving rails**

Free slabs remain X=−1.80…−0.70 and −0.11…0.69, Y=0…0.60 m. The sink stays in its inherited place; stove X≥0.69 is protected. The reserved rectangles below include bails/opened doors. The minimum gap between station rectangles is 25 mm. This is a layout check only; held tools, grippers, arms and moving food need their separate path tests.

| Station | X extent m | Y extent m | Maximum reserved Z m | Power |
|---|---|---|---:|---|
| raw_tray | -1.770…-1.460 | 0.035…0.305 | 0.100 | 0 W |
| drain_colander | -1.430…-1.160 | 0.035…0.305 | 0.190 | 0 W |
| peel_fixture | -1.090…-0.780 | 0.035…0.305 | 0.160 | 0 W |
| output_carrot | -1.770…-1.560 | 0.330…0.540 | 0.190 | 0 W |
| output_potato | -1.520…-1.310 | 0.330…0.540 | 0.190 | 0 W |
| output_leafy_greens | -1.270…-1.060 | 0.330…0.540 | 0.190 | 0 W |
| output_tomato | -1.020…-0.810 | 0.330…0.540 | 0.190 | 0 W |
| tool_dock | -0.100…0.100 | 0.050…0.550 | 0.130 | 0 W |
| guarded_cutter | 0.150…0.650 | 0.010…0.560 | 0.380 | 150 W |
| sink_insert | -0.530…-0.270 | 0.185…0.415 | -0.025 | 0 W |


Native fixed-cell top is 0.375 m, leaving 125 mm below cabinet bodies and door sweeps at Z=0.500. Its plate underside is 12 mm above the counter; only four 28×28 mm mount feet contact it. Every other fixed machine component starts at least 15 mm above the environment. Two front leaves open 90° forward within Y≥0.014; their sweeps are obstacles. R01's declared representative outlet-access boxes at X=−0.90/+0.15, Y=0.52…0.60 remain clear; they are assumptions rather than a site survey. The sink insert remains below/forward of the existing faucet. No appliance occupies cabinet door sweeps or the protected stove.

Only one prep appliance is powered: the shared cell uses one dry 220 V AC to 24/48 V, 150 W supply, with approximately 90 W press and 25 W indexing drive allowances. The 150 W supply is a rating, not another 150 W load added to the drives. Dry controls and fixed mains wiring remain behind the counter; food-path cartridges detach for washing. Arm/rail power is excluded from these figures.

Two or more independently passing arm rails can carry R and L. Moving arms require conductor rails with protective earth and protected contacts, onboard mains controllers and wireless operational data; safety uses hardwired/qualified safety communication. There is no long counter tether or usual cable carrier spanning free carriage movement. Passive wrist tools have no supply hose; local wrist cables stay on the arm. The fixed cutting cell's cable does not follow a carriage. Rail/switch hardware must independently preserve the 10 mm environmental gap except mounts, cabinet-door/outlet/faucet access and spring-applied rail brakes; this role does not certify those geometries.

**CAD, materials and manufacturing intent**

The package has 18 distinct custom designs; quantities are listed below, so “18” is not the total physical piece count. FreeCAD valid solid bodies/assemblies and individual STEP are provided; library parts intentionally share local origins and are not an assembled interference test. The separate counter document is the layout. Purchased bowls and motors are conservative envelope proxies, not reverse-engineered vendor solids. C16 is a clearly labeled **review blank**, never a fitted Nemco interface. C01's nominal wrist pattern and bowl rim fit require measurement before machining. Feed transmission, supported loading handoff, blade/pusher mating, hinges, interlocks and captive retention are concept-stage mechanisms.

Production food paths use certified 304/316L stock, grade-specific food-contact POM-C and molded approved silicone pads. Machined surfaces need smooth radiused edges, continuous sanitary welds, accessible disassembly and no blind food traps. Polycarbonate guards are outside direct food contact. POM friction/yield data apply to their stated grade. Printing is limited to non-food prototypes, external handle trials and protective covers; a “food-safe filament” label is insufficient for porous FDM food paths. Final handles can be machined POM; sheet-steel wash inserts have a 0.5 mm shell with 1 mm reinforced rim. [Food-contact stock guidance](https://www.ensingerplastics.com/-/media/ensinger/files/document-teaser-files/brochures/shapes/food-technology-shapes-en.pdf)

| CAD | Custom design | Qty | Material | Bare CAD mass kg |
|---|---|---:|---|---:|
| [C01](../../sim/r02/tools/cad/step/C01.step) | wrist master plate | 2 | 316L | 0.21044 |
| [C02](../../sim/r02/tools/cad/step/C02.step) | tool mate and antirotation dowel plate | 2 | 316L | 0.15555 |
| [C03](../../sim/r02/tools/cad/step/C03.step) | positive key handle 24x8 lands | 9 | POM-C | 0.05150 |
| [C04](../../sim/r02/tools/cad/step/C04.step) | bowl collar bail and key assembly | 4 | POM-C | 0.15187 |
| [C05](../../sim/r02/tools/cad/step/C05.step) | peel end-cup support slotted tray and axial stop | 1 | POM-C | 0.35860 |
| [C06](../../sim/r02/tools/cad/step/C06.step) | sink perforated insert | 1 | 304 | 0.54519 |
| [C07](../../sim/r02/tools/cad/step/C07.step) | lidded peel bin | 1 | POM-C | 0.35841 |
| [C08](../../sim/r02/tools/cad/step/C08.step) | three covered tool support dock | 1 | POM-C | 0.82908 |
| [C09](../../sim/r02/tools/cad/step/C09.step) | press base and four mount feet | 1 | 316L | 4.21457 |
| [C10](../../sim/r02/tools/cad/step/C10.step) | press hollow post | 2 | 316L | 0.48576 |
| [C11](../../sim/r02/tools/cad/step/C11.step) | press hollow bridge | 1 | 316L | 1.14883 |
| [C12](../../sim/r02/tools/cad/step/C12.step) | press enclosure panel set | 1 | polycarbonate | 2.20224 |
| [C13](../../sim/r02/tools/cad/step/C13.step) | root feed cassette and blade clearance slot | 1 | POM-C | 0.63873 |
| [C14](../../sim/r02/tools/cad/step/C14.step) | flat follower with positive travel stop | 1 | POM-C | 0.08616 |
| [C15](../../sim/r02/tools/cad/step/C15.step) | greens longitudinal and section guide comb | 2 | POM-C | 0.66121 |
| [C16](../../sim/r02/tools/cad/step/C16.step) | wedger adapter review blank | 1 | 316L | 0.47647 |
| [C17](../../sim/r02/tools/cad/step/C17.step) | contained catch nest and sloping chute blank | 2 | POM-C | 0.40820 |
| [C18](../../sim/r02/tools/cad/step/C18.step) | bottom support cup with offset key handle | 2 | POM-C | 0.19572 |


Bare CAD masses exclude purchased blades, fasteners, retention and pads. Conservative carried budgets are 0.30 kg detachable bail; 0.52 kg bowl+bail and 0.72 kg with reference food; 0.80 kg dry wash insert and 1.00 kg wet-loaded; 0.90 kg cassette and 1.10 kg loaded; 0.30 kg support cup and 0.50 kg loaded; 0.55 kg bin and 0.60 kg including scraps. Tool definitions/poses distinguish scrap bin from cutting cassette. No CAD mass was subtracted merely to pass payload limits. The key's positive bearing must be proof-tested to the unchanged 150 N/15 Nm targets; CAD material strength alone does not prove retention.

**Bill of materials and cost limits**

All baseline lines are below. Imported/adapted/machined parts have explicit engineering allowances, and most have no verified China retail price. Historical promotions, procurement ceilings and foreign prices are kept separate from current quotes. Costs are additive here; repeated whole-cell costs in comparison rows are shared, not additive.

| BOM | Item | Qty | Unit CNY | Line CNY | Basis/scope |
|---|---|---:|---:|---:|---|
| B01 | BLANDABLAN K20cmnext-stepbowls | 4 | 19.99 | 79.96 | publicChinaIKEAretail;notstockguarantee; tools |
| B02 | Foodcontactstainlessperforatedinsert+washbowl | 2 | 160.00 | 320.00 | Chinafabricationallowance; tools |
| B03 | Peelerbladeandeyeyspoonconsumables | 1 | 180.00 | 180.00 | Chinaengineeringallowance;matchedSKUpriceND; tools |
| B04 | Nemco428-8blade+55434pusherimportallowance | 1 | 1,300.00 | 1,300.00 | engineeringimportallowance;NOTverifiedChinaprice; tools |
| B05 | Sharpstraightknifeedge+twofoodcontactbackings | 1 | 260.00 | 260.00 | Chinaengineeringallowance; tools |
| B06 | Cframe/base/bridge+guardpanelsfabrication | 1 | 2,400.00 | 2,400.00 | Chinaone-offmachiningallowance; tools |
| B07 | Continuous>=1Nmbrakedpressdrive/ballscrew/encoder | 1 | 1,800.00 | 1,800.00 | engineeringallowance;runningtorqueproofrequired; tools |
| B08 | Indexdrive/guideandcontrol | 1 | 650.00 | 650.00 | engineeringallowance; tools |
| B09 | Loadcell/guardinterlock/safetyrelay/parkcatch | 1 | 1,350.00 | 1,350.00 | engineeringallowance; tools |
| B10 | Drymains24/48V150Wsupply,fixedwiring,sealing | 1 | 700.00 | 700.00 | engineeringallowance; tools |
| B11 | Cassettesroot/greens/dirty+follower/chute/wedgerblank | 1 | 1,200.00 | 1,200.00 | ChinaPOM/316Lfabricationallowance; tools |
| B12 | Peelendcupfixture/endstop/liddedbin/rawtray | 1 | 850.00 | 850.00 | Chinafabricationallowance; tools |
| B13 | Fourbowlcollarsandkeyedbails | 4 | 240.00 | 960.00 | Chinafabricationallowance;bowlextra; tools |
| B14 | Twofixedwristadapters | 2 | 350.00 | 700.00 | Chinafabricationallowance; tools |
| B15 | Toolkeyhandles/foodsupportfingers/cups/dock | 1 | 900.00 | 900.00 | Chinafabricationallowance; tools |
| B16 | Cleaningbrushes,foodpads,seals,spares | 1 | 500.00 | 500.00 | Chinaengineeringallowance; tools |
| B17 | DHIP67gripperspair | 2 | 12,000.00 | 24,000.00 | R01engineeringChinaallowance,NOTsupplierquote; optionalEOATintegration |
| B18 | Twoarms,rails,conductorrails,controllers,scanner | 1 | 0.00 | 0.00 | EXCLUDED;arm/railteamBOM;notfree; excluded |


Baseline tools: **14,149.96 CNY**. 20% contingency: 2,829.99; baseline plus contingency: **16,979.95 CNY**. Optional two DH grippers: 24,000 allowance, giving 38,149.96 including baseline but before contingency. “Excluded 0” is accounting notation, not free arms/rails/safety. Installation, verification labor, tax/freight beyond allowances and qualified higher-moment EOAT changes remain outside this figure.

**Scored alternatives**

ND means no verified China price; it is not zero cost. All numbers are CNY. Selected options are marked *, and work together as one system.

| Step / strategy | Option | Q/R/S/C/$/N | Weighted | Price basis |
|---|---|---|---:|---|
| wash / buy | Antai bubble/spray wash-and-dry line | 3/5/5/3/1/1 | 3.50 | 58,000.00; China manufacturer public advertisement; not quotation |
| wash / adapt | * UPPFYLLD basket+keyedbail,existingcoldfaucet | 5/3/5/4/5/5 | 4.35 | 19.99; China manufacturerprice;adapterextra |
| wash / build | Spray-tunnelandbubblingtank | 3/5/5/2/2/2 | 3.50 | 1,800.00; engineeringallowance |
| peel / buy | Abrasivepotatopeeler1.8kW | 2/4/4/3/2/1 | 2.90 | 4,190.00; 2025ChinaPostprocurementceiling |
| peel / buy | StarfritRotatoExpress | 3/4/4/3/3/3 | 3.40 | ND; China price ND;foreignnotconverted |
| peel / adapt | * Ypeelerwithpositivekey+compliancedepthstop | 5/2/3/5/5/5 | 3.95 | 300.00; domesticengineeringallowance |
| peel / build | Rotarylatheandfloatingpeelhead | 4/5/4/3/2/3 | 3.85 | 3,000.00; engineeringallowance |
| cut_roots / buy | RobotCoupeCL50+5mmdisc | 5/4/4/5/1/2 | 4.05 | 10,500.00; China sellerad;baseonlydiscextra |
| cut_roots / buy | BLAUPUNKTBP-QC02 | 2/4/4/3/5/3 | 3.30 | 399.00; historical2024Chinaadvertisedbeforecoupon |
| cut_roots / adapt | OXOmandolineguard+robotkey | 4/2/2/4/3/5 | 3.15 | 1,300.00; R01domesticmodificationallowance,notquote |
| cut_roots / build | * Singleenclosedindexingpress,rootcartridge | 5/5/5/4/3/4 | 4.60 | 8,100.00; wholecellengineeringallowance,sharedacrosscuts |
| cut_greens / buy | CL50shred/saladcutdisc | 2/4/4/5/1/2 | 3.15 | 10,500.00; samebaseprice,notadditive |
| cut_greens / adapt | Keyedknife+slottedcombboard | 5/2/2/4/5/5 | 3.65 | 700.00; R01fabricationallowance |
| cut_greens / build | * Sharedguardedpress+longitudinaland40mmstops | 5/5/5/4/3/4 | 4.60 | 8,100.00; sharedcellalreadycounted |
| cut_tomato / buy | Nemco55550-8wholewedger | 4/2/2/5/3/5 | 3.30 | ND; China matchedpriceND;R01USD192.50notChina |
| cut_tomato / adapt | * Nemco428-8+55434inlowguardedpress | 5/5/5/4/3/4 | 4.60 | 1,300.00; importblade/pusherengineeringallowance;notquote |
| cut_tomato / build | Indexedhalfcradles+sequentialdrawknife | 5/4/5/3/2/4 | 4.10 | 2,000.00; fallbackcartridgeallowance,notinbaselineBOM |
| hold / buy | mGripfood-safeIP69Ksoftgripper | 5/5/5/5/1/2 | 4.45 | ND; China priceND |
| hold / adapt | * DHIP67gripper+removablefoodcups/fingers | 5/3/5/5/2/5 | 4.20 | 12,000.00; R01Chinaengineeringbudget,notpublicquote |
| hold / build | * Passiveend-cupfixtureandkeyhandles | 5/5/5/5/4/5 | 4.90 | 1,600.00; CADfabricationallowance |
| transfer / buy | BLANDABLANKeachnext-stepbowl | 5/2/5/5/5/5 | 4.25 | 19.99; China manufacturerretail |
| transfer / adapt | * Bowlcollar+verticalkeyedbail | 5/5/5/5/4/5 | 4.90 | 240.00; perassemblyfabricationallowance,bowl19.99extra |
| transfer / build | Conveyorchutetooutput | 4/5/5/2/2/3 | 3.85 | 1,800.00; engineeringallowance |
| dispose_peel / buy | Kitchenbin/bowl | 5/3/5/5/5/5 | 4.50 | 19.99; BLANDAasopenwastebowlcomparator |
| dispose_peel / adapt | * Bin+slottedpeelworktray | 5/4/5/5/4/5 | 4.65 | 350.00; engineeringfabricationallowance |
| dispose_peel / build | Waterflushedwasteconveyor | 4/5/4/1/1/1 | 3.35 | 2,500.00; engineeringallowance |
| deliver / buy | Standardhandledcookingcontainer | 5/3/5/5/4/5 | 4.40 | ND; matchedChinaSKU/priceND |
| deliver / adapt | * Fourlabelledbowlbailsandfixedparking | 5/5/5/5/4/5 | 4.90 | 1,039.96; 4*(bowl19.99+collar240) |
| deliver / build | Bowlshuttleorrotarycarousel | 5/5/4/3/2/3 | 4.15 | 4,000.00; engineeringallowance |
| tool_exchange / buy | ATIQC18electricautomaticchanger | 5/5/5/4/1/4 | 4.40 | ND; China publicpriceND;R01budget25000 |
| tool_exchange / adapt | * Fixedmanualwristadapter+gripperpickedkeyhandles | 5/4/5/5/5/5 | 4.75 | 700.00; lightmanualadaptermachiningallowance |
| tool_exchange / build | Dock-actuatedspring-latchedautochanger | 5/5/4/3/3/5 | 4.35 | 1,800.00; engineeringallowance |


**Safety, unchanged checker rules and verification**

The proposal retains 5 mm/3° pose acceptance, robot/environment 10 mm gap, gripper/held-tool 5 mm gap, μ=0.5, SF=1.5, 150 N total jaw normal and 150 N/15 Nm positive-key proof. No ACM/padding changes or new contact exemptions were added. Maps refer only to physical food contact, blade/pad work surfaces and existing supported tool/bowl lands. They never exempt an entire fixture, receiver, gripper, guard, guide or bolt. Cell parts are robot parts; only declared feet are environmental mount contacts. Actual food envelopes are collision geometry even when supported by a cup.

Read-only references were [prep_checker](../../inputs/prep_checker.py), [mandoline_golden](../../inputs/mandoline_golden.py) and [R01 adapted checker](../../sim/r01/concept/checker.py). The concept post was unavailable at this read; its checker/model were examined directly. The R01 market post was available. The R01 helper only reports certain right-hand loads; generalized left-hand loading/paired poses are required without changing grip/contact logic. The old xArm ideal motor-rated-torque×100 values are not certified continuous joint output ratings; no URDF effort or peak value replaces each purchased arm's datasheet rating.

Safety-rated presence detection interlocks both arms and the cutting cell. Commission at ≤0.05 m/s arm speed and ≤0.3 m/s² acceleration. Category 1 controlled stops precede isolation/brake application. Require spring-applied brakes on every gravity-loaded arm axis, rail drives and vertical press axis, plus blade park catch before loading. Collision detection alone is not credited as a certified collaborative safety function. Guards, covers, supported food and lidded scrap handling keep blades inaccessible during normal operation. Exact braking, stopping distance, safety circuit, IP and cleanability validation remain hardware qualification tasks.

The delivered checks validate phase sequence/expansion, provenance/formulas, fixed layout/cabinet/outlet/mount gaps, CAD validity, carried mass budgets, BOM sum, unchanged input/reference hashes, image dimensions and output size. They do not invent an IK or torque pass. Food trials must verify complete peeling, eyes/core depth, clean creases, cut thickness/angles/mass, no crush and ≥98% yield across input variability. Actual Nemco datums and the supported loading tray must close before fabrication release. Instrumented trials must replace the potato-peel/greens/tomato proxies with measured curves and uncertainty margins, while retaining the finished-product gates.

Validation status: **pass**, 22 checks; held payload peaks R=1.000 kg, L=0.400 kg. The simply supported 400 mm bridge estimate under 1,000 N is 24.82 MPa and 0.0857 mm, using assumed stainless E=193 GPa; joints/guides and screw support remain unqualified.

Runs used one CPU child plus its bounded supervisor, each below 1,900 MiB, in foreground chunks of at most 180 seconds; no GPU. FreeCAD 1.1.3 and Blender 4.5 were used, with the specified sim venv read-only. Renders are 1500×840 and were visually inspected. Reference hashes and per-run time/working-set records are in `audit/`; the output was approximately 21 MB at validation, well below 2 GB. No writes were made to sim/r01 or robot_v5.

Independent STEP re-import verified all 18 exports as valid solids with relative volume error below 0.00001; [round-trip evidence](../../sim/r02/tools/audit/step_roundtrip.json). The final [delivery manifest](../../sim/r02/tools/audit/delivery_manifest.json) hashes the exported files and post.

**Source ledger**

The JSON ledger preserves source type, retrieval date and limitations. Public advertisements are not supplier confirmations.

- F01: [Singh, Das & Das 2016, IJFS 5:22-38](https://iseki-food-ejournal.com/article/69/pdf) — primary paper.
- F02: [Xie et al., carrot peeling design and experiment, JCAM 2025(12):154-162](https://www.qikan.com.cn/article/5dd020251220.html) — journal abstract, indexed publisher text.
- F03: [Wu & Abbott 2002, tomato firmness](https://www.sciencedirect.com/science/article/abs/pii/S0925521401001338) — primary paper abstract.
- F04: [Vieira et al. 2019, tomato mechanical resistance](https://repositorio.bc.ufg.br/bitstreams/71b8aa0d-e688-48a3-9207-8166a44fe47d/download) — primary paper.
- M01: [IKEA China BLANDA BLANK 30166051](https://www.ikea.cn/cn/zh/p/bu-lang-da-bu-lan-ke-shang-cai-yong-wan-bu-xiu-gang-30166051/) — China manufacturer retail.
- M02: [IKEA China UPPFYLLD 40521951](https://www.ikea.cn/cn/zh/p/uppfylld-wu-pu-fei-er-de-sha-la-shuai-gan-ji-bai-se-40521951/) — China manufacturer retail.
- M03: [Robot-Coupe CL50 China manufacturer](https://www.robot-coupe.com/cn/zh/p/vegetable-preparation-machines-cl-50/20672) — manufacturer.
- M04: [Shanghai Zongwang CL50 China supplier advertisement](https://www.21food.cn/productshow/3244917.html) — China seller primary advertisement.
- M05: [BLAUPUNKT BP-QC02 manual](https://blaupunkt.com/wp-content/uploads/2024/06/BP-QC02电动切菜机-说明书.pdf) — manufacturer manual.
- M06: [BP-QC02 historical China promotion](https://www.smzdm.com/p/118488221/) — secondary price observation, 2024-07-07.
- M07: [China Post 2025 kitchen procurement notice](https://www.chinapost.com.cn/cn/report/2510/0438-1.htm) — China public procurement ceiling.
- M08: [Hento carrot peeler manufacturer](https://hentomachine.cn/product/Carrot-Peeling-Machine.html) — China manufacturer indexed advertisement.
- M09: [Starfrit Rotato Express093209002BLCK](https://www.starfrit.com/en/starfrit-rotato-express-electric-peeler) — manufacturer.
- M10: [Nemco Easy Wedger55550](https://nemco.com/catalog/easy-wedger/) — manufacturer.
- M11: [Nemco wedger sell sheet](https://nemco.com/wp-content/uploads/2025/06/c9bb50b8-9645-4786-b5ff-fd07fe8a7881.pdf) — manufacturer.
- M12: [OXO Chef mandoline2.0](https://www.oxo.com/more-oxo/chef-s-mandoline-slicer-2-0.html) — manufacturer.
- M13: [Etac Fix board](https://www.etac.com/products/small-aids-for-daily-living/kitchen-aids/etac-fix/) — manufacturer.
- M14: [DH electric gripper brochure](https://en.dh-robotics.com/wp-content/uploads/2024/07/DH_Electric-Gripper-Brochure.pdf) — manufacturer.
- M15: [Soft Robotics mGrip](https://www.softroboticsinc.com/uploads/2021/03/Soft_Robotics_ModularGripping_800129_RevD_LR.pdf) — manufacturer.
- M16: [SMC HF3A-ZP3F](https://www.smc.com.cn/webcatalog/en-jp/equipment-for-the-food-manufacturing-industry/vacuum-equipment/HF3A-ZP3F-E/) — manufacturer.
- M17: [SCHUNK CMS China](https://schunk.com/cn/zh/press/shu-miao-nei-qing-song-huan-dao/17344) — manufacturer.
- M18: [ATI QC18](https://www.ati-ia.com/products/toolchanger/QC.aspx?ID=QC-18) — manufacturer.
- M19: [JLCFA LCM manual changer](https://www.jlcfa.com/item/2021230053839.html) — China retail specification.
- M20: [Ensinger TECAFORM AH natural](https://www.ensingerplastics.com/en-us/shapes/acetal-tecaform-ah-natural) — manufacturer.
- M21: [Ensinger food-contact stock shapes](https://www.ensingerplastics.com/-/media/ensinger/files/document-teaser-files/brochures/shapes/food-technology-shapes-en.pdf) — manufacturer.
- M22: [OMC StepperOnline23HS45-4204S](https://www.omc-stepperonline.com/nema-23-bipolar-3nm-425oz-in-4-2a-57x57x114mm-4-wires-stepper-motor-cnc-23hs45-4204s) — manufacturer.
- M23: [Zhucheng Antai vegetable wash/dry line](https://www.zcatspjx.com/products/show4295932.html) — China manufacturer advertisement, search-indexed.
- A01: [UFACTORY xArm technical specifications](https://docs.xarm.ufactory.cc/8.technical_specifications.html) — manufacturer.
- A02: [UFACTORY joint parameters](https://docs.supportarticle.ufactory.cc/support_articles/hardware/ufactory-joint-parameters.html) — manufacturer; inherited R01 evidence.
- L01: Inherited R01 market prep price ledger — read-only local evidence; Historical foreign benchmarks: Nemco192.50 USD, mandoline34.50 USD; domestic installed2300/1300 CNY were allowances. Not real China transaction prices.
- L02: Inherited fixed kitchen XML — read-only local evidence; Faucet centre x=-0.4,y=.56; outlet near spout(-.4,.40,1.032)world. Sink bottom650 mm. T08 slabs and stove boundary supersede countertop-edge rounding.
