"""Produce the review post from current results; no numerical worker."""
import json,csv
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];R=HERE/'results'
D=json.loads((R/'transport_options.json').read_text());S=json.loads((R/'sources.json').read_text());G=json.loads((R/'geometry_check.json').read_text())
C={s['id']:s for s in S}
def cite(ids):return ', '.join('['+i+']('+C[i]['url']+')' for i in ids)
p="""推荐采用**两条独立并行轨道，每条一只机械臂，各自使用拖链**（`passing_rails_cable`）。机械臂留在各自轨道上，可以互相越过并在行程内任意位置停下；不用把机械臂本身搬过道岔。三臂运输部分预算为 **99,000 元**，两臂为 **74,000 元**，均不含机械臂、末端工具和加工电器，也不是供应商报价。备选是在每条轨道上增加 180 mm 的升降轴，三臂预算 **129,000 元**。真正的自由换轨在这间厨房里不值得新增供电、车载控制箱、锁止机构和清洁维护的成本。

本轮把轨道、拖链和支架都作为机器人实体检查。空夹爪保持安装，工具和食材先放回支撑物；两臂、三臂的静态折叠运输采样均满足环境间隙 ≥10 mm，最小值 12 mm，跨轨实体最小间隙 16.18 mm。现有番茄分瓣器必须旋转 90° 并移到 `(x,y)=(0.39,0.48)` m；不改变刀具或切割机构。三只完整协作臂会伸到对侧台面上方，不能让人同时使用过道，第三只臂的加工可达性也未成立。因此，三臂图和价格用于比较，不建议直接作为家用配置。

这是一份运输方案和仿真接口，**不是整机通过报告**。按最不利 25 kg 臂体、3 kg 食材、1.2 kg 夹爪及 1.5 动态系数，选用 60 kg / 900 N / 每轴 650 N·m 的运输设计包络。支撑梁每轨约 51 kg，墙面载荷很大，瓷砖、抹灰层、轻质砌块和吊柜柜体不能承担该方案。导轨和梁的初算有余量，但门架刚度、建筑锚固、原厂柔性线缆弯曲半径，以及机械臂重力轴弹簧制动和连续扭矩证据仍须闭合。

## Decision and scope

Date: 2026-10-07. Work used public data only; no purchasing, supplier contact or user questions. The arm is mains powered. There is no torso, mobile base or battery.

Choose two independent X lanes, with fixed OEM controllers outside the wet zone and one partitioned cable chain per lane. Passing means changing longitudinal order **on different lanes**. A carriage does not change lanes, and two carriages on the same lane cannot overtake. A three-lane/four-carriage cost-saving arrangement would therefore fail unrestricted reordering of the shared-lane pair. The four-carriage passing-rail budget below pays for four independent lanes; that expansion does not fit this galley.

The second choice adds a short Z slide to each lane, only if task IK shows a useful gain. This is a paired-guide heavy carriage with mechanical retention, not a small catalog belt module carrying a cantilevered cobot. Pass only with Z at its upper position. Complete process reach, especially the outer third arm, remains a task-team decision. The UR5e is the reused collision-model benchmark; it is not granted actuator or braking approval by this transport study.

The conventional industrial alternatives remain useful for transporting **containers**. Moving produce baskets or trays through a small product conveyor can give the kitchen much of the scheduling freedom without moving 25 kg arm bodies, large controllers or sharp tools through switches. One strong work arm plus task-specific lighter helpers is another worthwhile redesign: a 0.5–1 kg helper for a single leaf, small produce item or empty tray can have a lower payload requirement, but must be sized to its real fixture reach and gripper mass. Neither idea substitutes an untested appliance for the required finished products.

## Mass, force, moment and stiffness sizing

Use 25 kg arm body, 3 kg food payload, 1.2 kg additional gripper, 8 kg X carriage and 1 m full-reach envelope. UR5e has a shorter 850 mm catalog reach and 20.7 kg body, so the support sizing is deliberately broader. All arm mass and the food/gripper are conservatively placed at full reach rather than assuming an undocumented arm COM. The 3 kg is food at the tool; total flange load here is 4.2 kg, still subject to the chosen arm's load-COM curve. Specifications: SOURCE_ARM.

For transport, Newtonian sizing uses `F = m a` and `M = Σ(r × F)`, with dynamic factor 1.5. At the full 60 kg design mass and 1 m/s² acceleration, inertial drive force is 90 N including the factor. Do not confuse that with 900 N vertical support capacity.

```
Fg = 1.5 × 9.81 × (25 + 3 + 1.2 + 8) = 547.40 N
Mg = 1.5 × 9.81 × [(25 + 3 + 1.2) × 1 + 8 × 0.15]
   = 447.34 N·m
Freference = sqrt(100² + 10² + 20²) = 102.47 N
Mgravity+process = 447.34 + 1.5 × 102.47 × 1 = 601.04 N·m
Selected support requirement: 60 kg, 900 N, 650 N·m about each axis
```

The 100/10/20 N case comes from `inputs/mandoline_golden.py`, and is retained as a conservative reference process envelope. No cutting, peeling or appliance force was invented. The current study changes transport hardware and one fixture's mounting orientation, not the cutting mechanism. Rail and Z motion are frozen during each reference process stroke. Any later powered dicer, washer or new tool needs its own physics/literature force and reaction-load evidence before it can replace those cases.

Four HGH25HA blocks are a sizing candidate. Each block is 48 × 40 × 104.6 mm, with catalog dynamic/static load ratings 42.20/69.07 kN and static moment ratings 560/730/730 N·m. Use two guide rows 340 mm apart and two blocks per row 240 mm apart. A conservative combined reaction bound is `900/4 + 650/(2×0.34) + 2×650/(2×0.24) = 3889.22 N/block`, below `C0/3 = 23023 N`. This is a preliminary load-distribution check, not a certified assembly moment rating or a fatigue-life calculation. SOURCE_GUIDE.

Two closed steel tubes per lane, each 150 mm deep in y × 50 mm in z × 3 mm wall, provide a 300 mm beam envelope. Physical track length is 2.4 m; the **end-supported structural span is 2.8 m**. With E=200 GPa and G=77 GPa engineering material assumptions, the combined `I=1.080584e-6 m⁴` and approximate closed-section `J=2.952636e-6 m⁴` give 1.90 mm vertical sag at 900 N and 0.115° twist at 650 N·m with rigid equal-sharing restraints. Twist contributes 2.00 mm at a 1 m TCP. These contributions leave little of the 5 mm system pose budget for guide, arch, frame, anchorage and arm deformation; the calculation does not grant the 5 mm/3° task acceptance. No slot is cut in the closed tubes for the cable chain.

Tube mass is 51.17 kg/lane, or 153.51 kg for three lanes, before guides, frame and guards. Conservative simultaneous wall-root moment bounds, including service moments, support-force stand-off and beam gravity but excluding frame weight, are **MOUNT_TWO kN·m for two lanes and MOUNT_THREE kN·m for three**. The 40 mm portal sections in the clearance model are placeholders, not structural steel selections. A household wall/frame design cannot be accepted from these drawings alone.

## Commercial transport survey

Catalog values and proposed design targets are distinguished below. Unknown capacity or moment means **no credit**, even when position repeatability looks excellent. Published product-shuttle mass is not the arm's flange payload.

| Option | Carriage/load and moment assessment | Stop accuracy and stiffness | Public source |
|---|---|---|---|
| Passing rails | Custom 60 kg / 900 N / 650 N·m requirement; four guide blocks and beam calculations above | ±0.10 mm rail repeatability target using linear encoder; no measured absolute accuracy; beam sag/twist above, assembly compliance open | SOURCE_GUIDE |
| Passing rails + Z | Same support requirement; allow up to 16 kg transport hardware, total 45.2 kg with worst arm and food/EOAT | ±0.10 mm X/Z target; additional Z cantilever/rod clamp stiffness unverified | SOURCE_GUIDE, SOURCE_LINEARSTOP |
| Custom end transfers | Heavy guides potentially feasible; latch and shuttle deck must carry 650 N·m; controller/pickup mass not yet reconciled | ±0.20 mm docking target; latch and guide seams dominate | SOURCE_TMS |
| Hepco PRT2 independent loop | Family load 10 kN+ and any orientation; no matched carrier moment rating selected | Preloaded bearings; matched independent-drive stop accuracy/stiffness not found. DTS2's linked belt carriers do not give independent arbitrary stops | SOURCE_HEPCO |
| B&R ACOPOStrak | Native 1–2 kg shuttle, 85–170 N dynamics: fails the arm mass before moment | Published positioning ±50–150 µm; no 650 N·m stiffness qualification | SOURCE_ACOPOS |
| Rockwell QuickStick | Published 2–100 kg transport range can cover mass; external guides/frame must carry moment | ±0.5 mm repeatability, ±0.1 mm with calibration; guidance stiffness separate | SOURCE_QUICK |
| Rockwell iTRAK 5730 | Optimized up to 4 kg: fails arm mass. An oval alone does not create overtaking | Heavy-arm accuracy and 650 N·m stiffness unestablished | SOURCE_ITRAK |
| Beckhoff XTS/GFX/TMS | Moving track transfer exists; matched heavy carrier/load/moment not established | Track management is a topology, not proof of heavy docking stiffness; matched loaded accuracy unknown | SOURCE_TMS, SOURCE_NCT |
| Chinese magnetic tracks | MODUASM, Dongmao and QuickTrans are real product families; matched 60 kg/650 N·m and power-loss spring brakes not found | MODUASM advertises ±0.01 mm repetition; Dongmao offers absolute-position/straight-transfer hardware. Neither figure validates this arm base | SOURCE_CHINA |
| Beckhoff XPlanar | Current APM4550 is 4.5 kg, 235 mm square. At least 14 movers for 60 kg by mass alone; group-frame mass and moment derating still excluded | One nominal 2×7 group could span ~1.68×0.48 m before frame; two groups cannot pass in a 2.4×0.5 m backsplash. Heavy arm stiffness and vertical-wall qualification unestablished | SOURCE_XPLANAR |
| Rexroth FLOW6D wall | Horizontal, vertical and overhead use is explicitly offered; matched 60 kg/650 N·m proof not found | Active levitation stiffness and loaded stop accuracy not established for this arm | SOURCE_FLOW |
| Single XZ / wall XY carriage | Heavy paired guides can be designed; shared X lane blocks reordering. XY gantry rotation does not remove cantilever moment | Targets only until measured; use Z only when it earns task reach | SOURCE_GUIDE |
| Festo ELGA-TB-G-80 alone | Fy/Fz=200/800 N; Mx/My/Mz=10/60/20 N·m: fails even the 447 N·m gravity envelope | ±0.08 mm repetition, IP40; precision does not overcome load/moment rejection | SOURCE_FESTO |

A vertical-wall mover is therefore an interesting research option, not a categorical impossibility. FLOW6D specifically supports this orientation. For this kitchen, public evidence does not establish the arm's large moment, spring restraint, payload power and controller packaging together. A single levitating product mover cannot be credited with those capabilities.

## Power, loss-of-power restraint, hygiene and noise

The recommended chains work because each carriage stays on its own 2.4 m straight lane. Different lanes have independent horizontal-bending chains, each fed near x=-0.30 m. They do not cross, accumulate twist or travel through switches. OEM controllers remain fixed in dry, ventilated housing outside the work/splash volume, with mains, wired network and safety wiring fixed; OEM arm leads travel through their own chain. Do not reroute mains through an arbitrary arm connector or replace OEM safety wiring with Wi-Fi. A 6 m OEM lead is a length candidate for this travel; actual routing and strain-relief lengths remain to be confirmed.

The modeled chain has bend radius 110 mm, 245 mm swept width and 25 mm swept height. Current UR documentation lists 13.4/14.6 mm high-flex PUR cable options, while older manuals list 12.1 mm HiFlex. Cable generation and dynamic minimum radius must be matched. `110/14.6 = 7.53 D` is **not OEM approval**. The general IGUS cable-specific bend-radius examples cannot validate a UR cable; if the chosen OEM cable/chain requires more space, increase pitch/envelope and rerun. SOURCE_ARM, SOURCE_CABLE.

For truly free shuttles, evaluate enclosed conductor rails carrying rated arm-controller power plus PE, or isolated low-voltage DC only when the chosen OEM controller supports it. VAHLE KBH offers 4/5 poles and 63–200 A variants but IP23, or IP24 with strips, is not a washdown enclosure. Moving contacts need access prevention and collector-dust containment. A positive protective-earth path and supply interruption handling are mandatory for a mains controller. Electrical compatibility at transfer joints is not solved by drawing continuous red lines. SOURCE_KBH.

Inductive power is credible at arm-scale power, but carries mass, electronics and losses. VAHLE F150/RE150-LV is rated 1.5 kW at 10–80 V output with a 5 kg pickup; pickup IP54 and regulator IP20 still need housings. Some 4 kW peak units are only 1.2–1.6 kW rated, so peaks cannot be used as continuous supply capacity. It does not directly replace an AC OEM controller input. SOURCE_CPS.

Beckhoff AT8200 NCT's 24 V, 35 W rated / 75 W peak is suitable for small grippers or sensors, not a general cobot supply; the 250 µs data feature does not change its power rating. VAHLE SMGM provides an Ethernet-interface microwave guide, with a 100 Mbit/s family, rather than sending raw EtherCAT through brush contacts. Deterministic timing, watchdog behavior and certified safety integration must be established for any such bridge. Wireless supervisory data is acceptable with local safety logic and a safe response to link loss; ordinary WLAN is not credited as a safety channel. SOURCE_NCT, SOURCE_SMG.

An OEM UR5e controller is 460 × 449 × 254 mm. Putting one plus a regulator on every switching carriage would materially change the backsplash geometry and moving mass. This packaging penalty is a major reason to prefer fixed controllers and chains; the free-transfer record in the JSON is topology only and not hardware-approved. SOURCE_ARM.

Spring-applied, electrically released X brakes are required even for horizontal rails. Candidate BXR-050-10LE has 3.2 N·m holding torque. A 10:1 drive, 20 mm pinion radius and conservative 0.8 transmission factor give 1280 N static holding force. At 60 kg and 0.2 m/s, translational kinetic energy is 1.2 J; the catalog allows 200 J individual work and 40,000 J total work, but reflected rotor/drive inertia and brake wear still need allocation. The listed 60 ms engagement delay corresponds to 12 mm travel; a controlled 1 m/s² stop adds 20 mm, within the proposed 50 mm reserved end margin. This is a screening calculation, not a safety-rated stopping-distance guarantee. SOURCE_BRAKE.

Use person detection, bounded 0.2 m/s empty X speed and 0.1 m/s loaded repositioning, and coordinated Category 1 / SS1 stops before energy removal. Apply spring brakes on loss of power; monitor brake release/application and holding ability. A motor holding brake does not by itself certify the whole stop. A Z slide also needs a direct spring restraint, such as a properly sized electrically released rod brake, and mechanical end stops; screw self-locking, gear friction and permanent magnets are not substitutes. The arm must meet the same spring-on-loss requirement on gravity-loaded axes. UR's public service description says each joint has a brake/friction clutch, but the sources inspected do not explicitly close the spring-mechanism proof. SOURCE_LINEARSTOP, SOURCE_URBRAKE.

Commercial SS1/STO capability, such as iTRAK's published SIL3/PLe, does not establish a mechanical spring brake on a carrier. ACOPOStrak's permanent magnets retain attachment to its guide, not independent longitudinal spring holding. FLOW6D advertises gentle landing/parking after power loss; that is not evidence of the required mechanical spring restraint under a 650 N·m cobot moment. SOURCE_ITRAK, SOURCE_ACOPOS, SOURCE_FLOW.

The following per-option table applies in addition to the common food-zone rules: stainless removable drip skins, accessible wipe surfaces, no lubricated guide above exposed food without containment, smooth drainable covers, OEM-compatible seals, and validated food-safe contact materials for tools/containers. Rail coverings themselves do not turn IP40/54 equipment into a washdown machine. Grease accumulation remains relevant even though cooking is outside scope. Food-contact parts require their own material documentation; guide corrosion coating alone is insufficient.

SERVICE_TABLE

Noise descriptions are engineering comparisons; no matched kitchen installation dBA measurements were found. Do not equate contactless propulsion with a silent installed system, particularly when guides, cooling or power collectors remain.

## Mounting and kitchen geometry

The model uses the authoritative T08 fixture dimensions, R01 fixed galley and conservative upper-cabinet/door/outlet envelopes. Coordinates are x along the counter, y=0 at the north counter front and y=+0.60 at the back wall, z=0 at the floor. Counter height is 0.85 m; opposite counter y=-1.8…-1.2. Upper cabinets occupy y=0.23…0.60 and z=1.35…1.95; conservative door sweeps extend forward to y=-0.365. Two declared outlet access boxes at x=-0.9 and +0.15, y=0.56, z=1.01 are retained. Actual household door hinges, faucet and sockets require a site survey.

Use an engineered reinforced-concrete connection, or an independent **floor-anchored** structural portal. Typical finish tile/plaster and hollow or aerated block are not structural rail anchors; hidden pipes/wires, substrate strength and waterproofing must be assessed before installation. Upper cabinets may hide a rail, but the cabinet carcass is not its load path. The above-cabinet end portal avoids the doors and faucet. Upper crossmembers occupy z=2.05…2.15 and stop at y=0.58, leaving 100 mm above cabinet tops and 20 mm before the wall. Wall pads are the only designated wall contact surfaces. Front end uprights at y=-0.425 clear the conservative door sweep by 40 mm. Intermediate wall brackets would cross carriage travel, so they are omitted; the beam is supported at its two ends.

For a wall-independent alternative, floor posts at x=-1.78/+1.02 and y=-1.10 support the same upper assembly. The candidate footprint has 100 × 140 mm feet with only 60 mm to the opposite counter at the posts. It needs floor anchorage and real gusset/frame design, not a movable or unanchored furniture frame. Raising the support moment bound to several kN·m makes a narrow unanchored ballast design unattractive. The floor-frame alternative is a geometric envelope; its anchoring/stiffness are not numerically qualified.

| Parameter | Primary passing rails | Passing rails + Z |
|---|---|---|
| Lane arm-mount y, 2 arms | -0.06, -0.58 m | -0.06, -0.60 m |
| Lane arm-mount y, 3 arms | -0.06, -0.58, -1.10 m | -0.06, -0.60, -1.14 m |
| Arm orientation / upper mount z | inverted, quaternion wxyz `(0,1,0,0)`, z=1.230 m | same; z=1.050…1.230 m, pass at 1.230 |
| Physical track / arm-center travel | x=-1.50…+0.90 m / -1.20…+0.70 m, 1.90 m travel | same |
| Structural beam | x=-1.78…+1.02 m; center y=arm y+0.225; center z=1.270; size 2.8×0.30×0.05 m | same |
| Guide assembly swept bound | y=beam center±0.170; z=1.252…1.300 m; block rows 0.34 m apart | same |
| Moving arch envelope relative to mount | x±0.180, y=-0.075…+0.420, z=0…+0.108 m; use individual header/leg boxes in JSON, not one filled cuboid | same plus fixed Z column proxy |
| Chain per lane | x=-1.50…+0.90; y=arm y+0.100…+0.345; z=1.297…1.322; horizontal R=0.110 m | same + short Z service loop; its OEM routing still open |
| Projected carriage gap / lane pitch | 25 mm / 520 mm | 45 mm / 540 mm |
| Stops and speed | 50 mm reserved dynamic stop margin; 0.2 m/s empty, 0.1 m/s loaded | same; Z spring motor and rod restraint |
| Switch locations | none | none |

The old wedger's footprint is x=0.282…0.498, y=0.260…0.540 and z=0.85…1.3326. It collides with the new rear guide by 40.3 mm. Required layout revision: rotate the **same** fixture 90° about z, keep x center 0.39, move y center to 0.48. New bounds are x=0.250…0.530, y=0.372…0.588, same z. The wall gap is 12 mm; the moving rear carriage leg leaves 12 mm to its front, and the rear guide leaves 17 mm. Task poses and reference force directions must rotate with the local fixture frame in the process model. No contact exemption was introduced. Other stations retain their authoritative footprints. The rigid closed tubes remain intact; chains sit above them under the arch crossheads.

The empty folded UR5e plus unchanged R01 gripper has local bounds x=-0.465204…+0.065357, y=-0.217909…+0.060000, z=-0.361486…-0.001179 m. Empty jaw setting is the existing 15 mm slide opening, with palm 70×80×40 mm and fingers 75×8×20 mm, 1.2 kg total. No detachable-gripper tool changer is required. Its joint vector is recorded in JSON and the FK collision models:

```
[-0.03391418, 2.88752353, 2.70684347,
  1.33689837, -2.26572606, -2.94895479] rad
```

Two full-arm lanes leave about 402 mm of aisle at the folded arm (382 mm for Z). Three lanes overhang the opposite counter by about 118/158 mm, respectively, while the arm's lowest modeled point stays z=0.8685 above its 0.85 m top. This makes three full arms a robot-only installation; arbitrary household objects on the opposite counter must be modeled too. The outer third arm is too far from most north-counter stations for the benchmark's 850 mm reach. Its task role is not approved by a passing-clearance result. A fourth full independent lane intersects the opposite-wall/counter region and has no accepted installation model.

## Phases and finished-product contract

This scope retains the reference tools and forces; it does not replace food processing with a new force-unknown appliance. Insert the following transport sequence between old process strokes: support food and sharp tools; empty the existing gripper; adopt the admitted fold; raise Z to the passing position; verify clearance/person exclusion; release rail brake and move; execute controlled stop; engage/verify clamp and brake; then unfold and pick the next supported item. A loaded arm can reposition only on an separately admitted path and may not use the empty-passing proof.

| Old phases | Retained operation and transport integration |
|---|---|
| P01, P02, P03 | Carrot pick, rinse/rub and board placement; include supported water on/off and full-surface rotation. Rail locked for the reference wrist strokes. |
| P04, P05, P06 | Clamped carrot peel, mandoline load and slice strokes; retain all peel orientations, post-peel rinsing, end trim/facet, and first/middle/10 mm stub/final 5 mm slice. Empty-pass moves are interleaved only after support. |
| P07, P08, P09, P10 | Potato pick/wash/peel/slice; also remove eyes, rinse fragments, clean board and perform post-cut starch rinse/drain. No reference force reductions. |
| P11, P12 | Trim greens' root, separate stems, wash basal creases, drain/spin and cut 40 mm sections. Basket transfer between faucet and spinner remains a required actual transfer. |
| P13 | Wash tomato, remove hard stem tissue and make eight unpeeled radial wedges; existing wedger receives the documented 90° fixture pose update. P13 force case is retained in that local frame. |
| P14 | Transfer every ingredient into its own next-step cooking bowl/container, physically clear the rim, preserve pulp and ≥98% edible mass, then park/reset bowls. |
| P15, P16 | Pick/return peeler and knife on accepted supports, rinse and supported-wipe between dirty/clean work and after tomato; these supports precede empty transit. |

This table is a transport interface to **all full cook_ref/keypose substeps**, not a claim that the reduced P01–P16 screen covers them. The product contract remains washed produce; peeled carrot/potato slices 5±1 mm with ≤1 mm within-slice variation; greens 40±10 mm; eight radial unpeeled tomato wedges, nominal 45±10° and each piece 0.65–1.35 times mean mass; peel 0.2–0.8 mm/gouge≤2 mm; ≥98% edible transfer. The optional 2–3 mm potato julienne branch stays optional. No cooking or plating is added. The full quality poses, grasp μ=0.5, actual continuous arm torques, first/last cuts and cleaning still require the task checker.

## Costs and ranking

All complete-cell numbers below are **CNY engineering planning estimates**, not matched China supplier quotations. Public installed prices for these specific 2.4 m, heavy-arm configurations were not found. Lightweight catalog systems that fail the arm requirement retain indicative transport-demonstrator budgets only; their price is not the cost of a compliant retrofit. No supplier was asked for a quote.

Public China component anchors are much smaller: MISUMI lists E-RAM6-S-40-N-N at 1,406.61 CNY and E-RAM8-S-300-N-N at 2,123.89 CNY, both untaxed reference prices; screw-module examples C-KSC8610-B1-340-F0 / C-KSC4001-B1-100-F0 are 1,907.98 / 1,518.58 CNY; an 11-link R18 miniature chain is 58.30 CNY. These do not support a price or capacity claim for a complete 2.4 m/650 N·m arm rail and are not the selected parts. SOURCE_CHINAPRICES.

Primary budget formula: `24,000 fixed + n×9,000 rail/beam/covers/brackets + n×16,000 carriage/drive/encoder/spring brake/chain/integration`. Fixed allowance includes 18,000 for presence/safety coordination and 6,000 for calibration/assembly. Z adds 10,000 per arm. Structural frame/guards are allowances within these categories; the unqualified frame/anchor design can exceed them. Excluded: cobots, EOAT, appliances, wall reconstruction, and complete-cell certification/development. Budgets are not VAT-normalized supplier quotations. The CSV supplies low/base/high uncertainty bands; primary three-arm band is approximately 64,000–158,000 CNY. Arm purchase price must be added separately.

COST_TABLE

Scores are engineering judgements from 1 (poor) to 5 (good) for this arm application. Safety scores express the remaining integration burden, not a device certification. Capacity, spring restraint and required movement are binding gates; inexpensive ineligible devices cannot win by adding scores. Ranking orders practical candidates first and then research/rejected alternatives, rather than pretending the incomparable prototypes have precise weighted utility.

RANK_TABLE

**Free shuttling is not worth its cost for this home food-prep scope.** Even the custom two-end transfer estimate is 160,000 CNY for three carriers versus 99,000 for three independent passing lanes, before solving onboard controllers and continuous protected power pickup. Premium independent-cart and planar options add substantially more. If an arm must change lanes, the simplest starting topology is two straight tracks plus end cross-transfer decks with positive locks; heavy guides, spring brakes and power continuity must be proved before detailed CAD. A product-only container shuttle is a better candidate for those technologies.

## Verification, diagrams and handoff

The R01 concept post was not available at the read checkpoint; `sim/r01/concept/model.py`, `checker.py`, reused OEM arm XML, vendor sources and `posts/r01/market.md` were read directly. Reference checker/input hashes are stored in `transport_options.json`; no R01 or robot_v5 files were modified. No new ACM pairs or tool/contact exceptions were introduced. Physical unpadded primitives were checked with inherited same-weld/parent-weld rules, self nonpenetration, conservative 10 mm environment and cross-lane gaps (even for the gripper, stricter than its 5 mm requirement). A full task-checker integration must preserve its padding correction `c.dist+2*PAD`, μ=0.5 and 5 mm/3° pose admission.

The source UR5e base lacks collision geometry, so a 75 mm radius × 80 mm high base proxy was added. The R01 palm and empty fingers were retained; tools/food are parked for this check. Chains are full swept-envelope boxes and fixtures full conservative assembly boxes. Near pairs use MuJoCo signed distances; separated pairs use a conservative AABB distance lower bound, censored at 50 mm, avoiding a MuJoCo 3.2.5 far-pair cylinder/long-box anomaly. The plane floor is not used in the collision model because all non-mount parts stay above it; floor-frame foot contacts are designated mounting surfaces in the alternative, not a new arm-floor permission.

CHECK_TABLE

These are sampled static checks, not continuous-path, dynamic, person-access, IK, grip or torque passes. Same-lane self distance is nonnegative; the XZ flange proxy is tangent to its own beam envelope in the upper position, an assembly interface that needs CAD running clearance. No process-loaded configurations were tested. The 12 mm nominal environment gap has only 2 mm tolerance reserve: survey/CAD and loaded deformation must preserve the mandatory 10 mm gap. Three-arm clearance proof does not establish third-arm useful reach. XZ XML includes Z DOFs, tested only at their upper position; lowered-Z paths and its service loop need separate verification.

Primary installation diagram (two working arms):

![Independent passing rails in the galley](../../sim/r02/transport/renders/passing_rails_cable_2.png)

Secondary installation diagram (two working arms plus Z):

![Passing rails with short vertical slides](../../sim/r02/transport/renders/passing_xz_cable_2.png)

The [three-arm primary comparison](../../sim/r02/transport/renders/passing_rails_cable_3.png) and [three-arm Z comparison](../../sim/r02/transport/renders/passing_xz_cable_3.png) show the aisle penalty. All four drawings are 1600×1000 pixels. Cabinets/walls are partly omitted or transparent for visibility; their geometry remains in the clearance check.

Deliverables: [parametric options and geometry](../../sim/r02/transport/results/transport_options.json), [39 cost rows](../../sim/r02/transport/results/costs.csv), [sizing](../../sim/r02/transport/results/sizing.json), [27 public primary sources](../../sim/r02/transport/results/sources.json), [clearance witnesses](../../sim/r02/transport/results/geometry_check.json), [folded posture](../../sim/r02/transport/results/folded_arm.json), and [primary BOM allowances](../../sim/r02/transport/results/recommended_bom.csv). Four collision XMLs and FK drawing records are alongside the JSON.

Reproduce from the workspace using `python sim/r02/transport/bounded.py <timeout_seconds> <log_name> C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe sim/r02/transport/<script>.py`. Order: `fold_search.py` (240 s), `build_results.py` (120 s), `check_transport.py` (180 s), `render_diagrams.py` (120 s), `write_post.py` (120 s). All runs are CPU-only, foreground, one numerical worker at a time, BLAS threads=1, monitored process-tree RSS below 1900 MiB, and far below 20 minutes. Resource logs are in `audit/`; final fold/check/render runs used about 86/81/102 MiB respectively. No installed hardware performance is implied by those runtime numbers.
"""
mapping={'SOURCE_ARM':['S21'],'SOURCE_GUIDE':['S01'],'SOURCE_LINEARSTOP':['S20'],'SOURCE_TMS':['S08'],'SOURCE_HEPCO':['S02','S03'],'SOURCE_ACOPOS':['S04'],'SOURCE_QUICK':['S05','S06'],'SOURCE_ITRAK':['S07'],'SOURCE_NCT':['S09'],'SOURCE_CHINA':['S12','S13','S14'],'SOURCE_XPLANAR':['S10'],'SOURCE_FLOW':['S11'],'SOURCE_FESTO':['S15'],'SOURCE_CABLE':['S26'],'SOURCE_KBH':['S16'],'SOURCE_CPS':['S17'],'SOURCE_SMG':['S18'],'SOURCE_BRAKE':['S19'],'SOURCE_URBRAKE':['S22'],'SOURCE_CHINAPRICES':['S23','S24','S25']}
for k in sorted(mapping,key=len,reverse=True):p=p.replace(k,cite(mapping[k]))
o=sorted(D['options'],key=lambda a:a['rank'])
service=['| Option | Moving-arm power/data | Power-loss restraint | Splash/grease/cleanability | Noise |','|---|---|---|---|---|']
for a in o:service.append('| '+a['name']+' | '+a['power_data']+' | '+a['power_loss_braking']+' | '+a['splash_grease_cleanability']+' | '+a['noise']+' |')
cost=['| Rank / option | 2 carriages | 3 carriages | 4 carriages | Qualification |','|---|---:|---:|---:|---|']
rank=['| Option | Simplicity | Reliability | Safety | Cost | Freedom |','|---|---:|---:|---:|---:|---:|']
for a in o:
    cost.append('| '+str(a['rank'])+' / `'+a['id']+'` | '+ ' | '.join(f"{a['cost_cny'][str(n)]:,}" for n in (2,3,4))+' | '+a['eligibility']+' |')
    rank.append('| `'+a['id']+'` | '+' | '.join(str(i) for i in a['scores_1_to_5'].values())+' |')
checks=['| Variant | Sampled states | Environment minimum | Different-lane minimum | Screen |','|---|---:|---:|---:|---|']
for a in G:checks.append('| `'+a['variant']+'` | '+str(a['sample_states'])+' | '+f"{a['minimum_robot_environment_gap_lower_bound_m']*1000:.2f} mm"+' | '+f"{a['minimum_different_lane_robot_gap_lower_bound_m']*1000:.2f} mm"+' | '+('PASS' if a['screen_pass'] else 'FAIL')+' |')
for k,v in [('SERVICE_TABLE',service),('COST_TABLE',cost),('RANK_TABLE',rank),('CHECK_TABLE',checks)]:p=p.replace(k,'\n'.join(v))
p=p.replace('MOUNT_TWO',f"{D['sizing']['mount_load_bound']['two_lane_wall_moment_Nm']/1000:.2f}").replace('MOUNT_THREE',f"{D['sizing']['mount_load_bound']['three_lane_wall_moment_Nm']/1000:.2f}")
power_addendum=HERE/'results/power_addendum.md'
if power_addendum.is_file():
    p=p.rstrip()+'\n\n'+power_addendum.read_text(encoding='utf-8')
out=ROOT/'posts/r02/transport.md';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(p,encoding='utf-8')
print(json.dumps(dict(post=str(out.relative_to(ROOT)),characters=len(p),options=len(o),diagrams=4),ensure_ascii=False))
