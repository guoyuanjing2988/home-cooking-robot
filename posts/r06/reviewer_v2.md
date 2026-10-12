中文摘要：第二次交付的进展可以独立重现：**静态义务 30/150，通过的均为整盆抓放；持久整餐连接 10/240，整餐 FAIL**。首次实际抓取、搬运、落盆、松爪、退出及洗涤站夹紧、开盖通过，随后停在缺少完整驱动、锁止和导向接口的内篮提升步骤。没有完成清洗或切割，也没有任何合格成品。第一版的支承身份校验漏洞已修复；本次未发现已接纳路径借用非工作路径上的工作接触权限，未发现通过缩小保留的机器人、夹具或食物几何取得成绩。

本次重新检查全部 **30 组、150 个静态姿态**，另独立求解并重放 **8 条支承行程**。连接复核包含 **21 条非零运动轨迹**：18 条全程通过、3 条重现碰撞；另外检查了 3 条零运动连接及 1 条无完整路径的失败搜索见证。覆盖最长已接纳连接和最小间隙连接，重新离散化的点位移上界均不超过 **4 mm**。14 个实际状态保持原料 **0.57 kg** 守恒，未发现复制、消失或所有权切换时的几何跳变。后续切块、废料、洗净判定和 ≥98% 可食部分交付仍未实现。

间隙显著改善：全部选定静态姿态有至少 **12 mm** 额外余量；实际前缀样本 **96.7%** 达到额外 10 mm，最小 **0.926 mm**。独立支承行程及有条件的原料盆演练仍在窗口退出附近达到约零余量，不能据此声称已有制造、标定和变形容差。当前外廓 **1606×906 mm**，超过约 1.2–1.5 m 的宽度目标，开门还需额外空间。完整备菜时间 **null**；前缀含 20 s 启动共 **150.779 s**。候选预算 **¥274,850**，含一次 ¥16,000 家用安全包及一次 15% 预留，仍是工程估算。结论：**不进入整机详细设计冻结或制造；继续完成工艺接口及完整守恒序列。** 共 **9 项发现**。遵守当前“不做实物试验、不采购、不联系供应商”的决定。

# R06 reviewer — second delivery

Review of the revised [integrator](integrator.md), [stations proposal](stations.md), scripts and results against [DECISIONS.md](../../DECISIONS.md), [R05 review](../r05/reviewer.md), [R04 review](../r04/reviewer.md), [R02 tools](../r02/tools.md), [cook_ref](../../inputs/cook_ref.md) and [key poses](../../inputs/keypose_cook.md). The [first review](reviewer_v1.md) remains historical. The dedicated workstation decision governs R06; the later R07 kitchen placement does not reinstate cabinets or a back-wall requirement here. Physical tests remain deferred, superseding older reviews' recommendations to begin them.

The authoritative design is **L17**, one fixed, side-mounted UR5e with no moving arm rail. The integrator's six-layout stopping condition is not workstation acceptance. New evidence is in [reviewer/v2](../../sim/r06/reviewer/v2/); upstream files were read only. Public component information was checked using the [agent-reach skill](C:/Users/admin/.codex/skills/agent-reach/SKILL.md) and primary manufacturer/paper sources.

## Verdict

**Do not proceed to integrated detailed design or build release.** Continue focused interface design and simulation. R06 demonstrates a useful first container transfer; it does not yet demonstrate a food-preparation machine.

| Item | Independently reviewed result |
|---|---|
| Static obligations | **30/150**; 30/30 handling, 0/120 processing qualified |
| Selected static poses | **150/150**, independently rechecked |
| Additional full support-stroke replays | **8/8**, fresh constrained IK continuations |
| Persistent meal connections | **10/240**; 230 have no admitted persistent connection |
| Actual sequence | One complete raw-carrot pan transfer, wash retention and lid opening; blocked at `P01_lift_insert` |
| Food conservation | Pass for the **14-state raw prefix**, **0.57 kg**; finished-food conservation unverified |
| Finished products / complete meal | **0/4; FAIL** |
| Verified complete prep time | **null** |
| Recomputed executed-prefix duration | **150.778604 s**, including 20 s startup; not meal prep time |
| Candidate cost | **CNY 274,850**, not a quote or passing-product price |
| Cheapest passing configuration | None established |
| Proceed to detailed design | **No** |

The 150 and 240 denominators are the current submission's explicit lower-bound inventories. Grouping a wash or cutting cycle does not enumerate every possible eye, leaf, cut, recovery, cleaning or quality retry. They are not directly comparable to R05's phase counts or v1's expanded ledger. The two connected appliance sweeps have no 96-start static certificate and are correctly excluded from the static numerator. [Static replay](../../sim/r06/reviewer/v2/statics.json), [metrics](../../sim/r06/reviewer/v2/metrics.json).

## Independent verification

The [new review script](../../sim/r06/reviewer/revision2.py) reconstructs the scenes and checks compiled sizes, transforms, joint axes/ranges and inertias against saved XML. It uses the previous reviewer's independently implemented pair policy, ownership permissions, wrench/Jacobian equations and displacement bound. The audited reference distance oracle is reused; this is not a second independent convex-distance implementation. All reported replays were recomputed in this review.

**Statics and strokes.** All 30 endpoint sets pass: open acquisition, closed jaws before attachment, retained seating, lifted pan and empty retreat. Maximum position residual is about **1.75×10⁻⁹ mm**; the tighter attachment solve supplements the unchanged 5 mm/3° gate. Maximum torque/envelope ratio is **0.517190**, minimum key grip margin **2.644076**. Eight independently solved 80 mm support lifts cover every ingredient and input/wash support roles; release witnesses traverse their support segment in reverse. These remain conditional local witnesses, not eight newly completed meal events.

| Stroke | Ingredient / support | Full replay states | Result |
|---|---|---:|---|
| T01_grasp | Carrot input | 160 | Pass |
| T01_release | Carrot wash | 160 | Pass |
| T04_grasp | Potato input | 240 | Pass |
| T04_release | Potato wash | 160 | Pass |
| T08_grasp | Tomato input | 160 | Pass |
| T08_release | Tomato wash | 160 | Pass |
| T11_grasp | Bok choy input | 313 | Pass |
| T11_release | Bok choy wash | 160 | Pass |

[Independent stroke checks](../../sim/r06/reviewer/v2/strokes.json). Raw 96-start searches were inspected, not rerun or counted as new searches.

**Connections.** The **25 replay records** contain **21 nonstationary trajectories**, three stationary boundaries and one rejected search without a complete path. Eighteen nonstationary trajectories pass throughout; three appliance trajectories fail at the first reproduced obstruction. This exceeds the requested 20-connection coverage without counting duplicate T01 rehearsal paths.

| Connection group | Coverage / result |
|---|---|
| Persistent T01 | All eight approach, descent, jaw-close, lift, transfer, seat, jaw-open and retreat paths pass |
| Persistent P01 | Retention and lid opening pass from the exact arrived state |
| Conditional T02 rehearsal | Descent, jaw-close and loaded lift pass; empty approach is stationary; washing is bypassed, so no meal credit |
| Conditional wash insert | 120 mm geometric lift passes; incomplete drive prevents execution credit |
| Conditional process | Retention, lid, carrier and longitudinal blade-park sweeps pass; lateral blade park, pusher and blade-down sweeps fail; two returns are stationary because preceding blocked moves were not committed |
| Failed T02 loaded transfer | No complete path exists. Ten saved candidate/rejection states were rechecked; collision rejection reproduced. Original search consumed **65.015 s**, followed by retained orientation/elevated staging attempts |

The longest retained passing connection is **T01_loaded_transfer**: **554 checked states**, conservative displacement bound **2.208479 m**, not measured tool travel. The tightest is **T02_loaded_lift**, approximately zero reserve at support-window exit. Both were replayed completely. Two-arm overlap is inapplicable to the single-arm L17. [Arm connections](../../sim/r06/reviewer/v2/paths.json), [mechanism connections](../../sim/r06/reviewer/v2/mechanisms.json).

For each segment the independent bound sums hinge enclosing radii times absolute angle changes and slide travel. A second valid bound uses starting radii plus downstream displacement; the smaller valid bound determines `ceil(D/0.004)` intervals. Jaws and moving appliance descendants are included. Free pan coordinates are asserted unchanged within each connection; ownership changes are checked separately. Every grid state, including endpoints, is checked until the first failure. Maximum step is **4.000000 mm**. Geometry-center FK differences are only a secondary sanity check, not a surface-point certificate. The inherited 1 μm comparison epsilon is not fabrication reserve; negligible negative roundoff near zero reserve is retained in the evidence.

The persistent prefix contains **1,404** checked samples. All path endpoints match the complete recorded states; capture/release recompilations preserve physical geometry within the 10 μm handoff limit. Recomputed timing includes curvature: maximum robot-point acceleration bound is **0.162439 m/s²**, below the 0.30 m/s² carry assumption. [Seams, timing, envelope and inertia checks](../../sim/r06/reviewer/v2/auxiliary.json).

## Findings

1. **INFORMATIONAL — The prior support-identity defect is repaired in the exercised acceptance paths.** All **25** compared R04/R05 Python copies are byte-identical; the original-input/reference diff is preserved. Gates remain 5 mm/3°, 10 mm robot/environment and arm/arm, 5 mm held/gripper/environment, PAD=0, μ=0.5, SF=1.5 and key capacity 150 N/15 Nm. Same-arm self/adjacent-link treatment remains the audited reference policy; no new 10 mm same-arm rule is imposed.

   Support permissions resolve the named face to its support and object, check held ancestry, straight approach and face normal, and end at the 5 mm gap or 50 mm limit. The correct dock grants five specific pan/land permissions; changing support, object, face, normal, normal magnitude or kind to working-on-transit grants none. Every exercised ordinary path agrees with the independent owner policy. Capture permission is restricted to that pan's key and the two named jaws. Mechanism contacts identify the particular food/pan and retainer, pusher or blade; non-working park/return records have no working permission. The physical collisions below receive no exception.

   All **52** audited shared arm/EOAT/pan/food/key/lid named geometries retain their type and are not smaller than v1; OEM masses, inertias and CoMs also match. The full cup moves, handles/drives are added, and the old cage is explicitly replaced by new open docks. This is a fixture redesign, not a shrunken source appliance. Discarded L09 is not admitted. Custom geometry still needs construction qualification. [Diffs, geometry and probes](../../sim/r06/reviewer/v2/audit.json), [input/reference diff](../../sim/r06/reviewer/v2/input_reference.diff).

2. **BLOCKING — The meal stops before its first wash.** The former cup/backer acquisition obstruction is resolved. However, `P01_lift_insert` lacks a complete drive/latch/guide interface; brush coverage and water exchange are unconnected. **230 persistent connections remain unadmitted.** A timer, parked arm or conditional raw-pan route cannot replace them. The retained 65 s RRT search, restarts, shortcutting and staging satisfy the budget intent for the attempted free connection; downstream records containing `allocated_planner_budget_s=65` are not evidence those searches ran.

   Independent process replays reproduce **1.309524 mm penetration** between carriage plate/rear guard, **0.750000 mm** between pusher plate/lid drive, and **0.036232 mm** between blade/worktop. These are appliance interference, not food/tool contact. Rejected movements are not committed before later diagnostics. Repair the full-size interfaces and continue from the last conserved state. [Failures](../../sim/r06/reviewer/v2/mechanisms.json), [persistent obligation ledger](../../sim/r06/integrator/results/motion.json).

3. **BLOCKING — The selected processing system is a custom concept, not a qualified commodity appliance.** L17 includes pan lands, lid/clamp geometry and actuator envelopes. Wash indexing, peel follower, eyes/core, food cradle, blade/pusher handoffs and retained scrap delivery remain incomplete. Food is behind a 100 mm pan wall; the pusher cannot simply pass through it. A bought blade or hand tool does not establish an appliance with robot-operable openings, controls and cleaning access.

   | Primary evidence rechecked | Established facts / remaining gap |
   |---|---|
   | [HENDI 801628](https://www.hendi.eu/de/gastronorm-behlter-14-4046.html) | 265×162×100 mm, 2.8 L, 18/8 stainless. Modeled 163 mm width is conservative. Insert, key, powered lid, seals and drain are custom; a plain pan is not a washer. |
   | [OXO 21081](https://www.oxo.com/y-peeler.html), [triangle huller](https://triangle-tools.de/en/Tomato-and-fruit-huller-Professional/10-004-25-00) | Passive tools, 152.4×76.2×25.4 mm and 145×20×13 mm. No automated coverage, peel-depth, eye-removal or core-only guarantee. |
   | [Nemco Easy Wedger](https://nemco.com/catalog/easy-wedger/) | Real 55550-8, 428-8 blade and matching **55434** pusher; tomato use listed. Custom throat/drive/guard, <10% compression and wedge-mass requirements lack proof. |
   | [CL20](https://www.robot-coupe.com/uk/en_GB/p/vegetable-preparation-machines-cl-20/18232) | 325×310×570 mm, 400 W, Ø58 mm tube, 104 cm² large hopper and nominal 5 mm disc 18289. A 65×70 mm potato does not fit the small tube. Larger-hopper area is not a fit certificate; revision-matched lid/pusher/buttons/interlocks and terminal recovery are unresolved. A closed pan is not its inlet. |
   | [Nemco 55200AN manual](https://nemco.com/wp-content/uploads/2025/06/Operations_Manual_and_Parts_Breakdown-55200AN_10-2014.pdf), [dimensions](https://nemco.com/wp-content/uploads/2025/06/55200AN_Easy_Slicer_11-2019.pdf) | Manual, no electrical drive; handle-out 533.4×279.4×406.4 mm, blade plate Ø234.95 mm. Fixed 3/16-inch **55200AN-6** gives nominal 4.7625 mm. Operation requires pusher withdrawal, cover opening/closing, coordinated crank and gentle feed. Complete automation, guarding and terminal recovery are absent. |
   | [DitoSama T-series](https://www.ditosama.com/en/products/multipurpose-peelers/) | Real 5–25 kg rated batch range; no proof for one 120 g carrot or 200 g potato, 0.2–0.8 mm peel depth or every eye. |

   The alternate stations concept's Starfrit size/power/manual-generation uncertainty remains; no new qualification is claimed. L17 correctly does not pretend to have adopted a complete CL20 or Nemco slicer. Select an evidenced commercial subsystem where its actual interfaces meet the requirements, or model and budget the whole custom mechanism. [Interface record](../../sim/r06/integrator/v2/interface_review.md).

4. **BLOCKING — Raw conservation passes; food transformation and delivered quality do not.** Each compiled prefix contains exactly one original body and solid per food under its recorded container ancestor, with unchanged geometry and mass ledger. Pan poses, ownership, jaws, every physical joint and lid open/closed state agree with the configuration. Water stays off, the door is recorded locked, no person is inside, and the final appliance state is retained/lid-open. The **0.57 kg** remains raw; no cut children or scraps exist. This proves prefix continuity, not a processing mass balance. [Independent conservation](../../sim/r06/reviewer/v2/conservation.json).

   Still required: washed/peeled roots, **0.2–0.8 mm** peel with ≤2 mm gouges, every potato eye, **5±1 mm** slices with ≤1 mm within-slice variation and recovered terminal pieces. Bok choy needs every stalk/crease, **600 s** soak, 2–5 N crease treatment, grit inspection, ≤15 mm stalk width and **30–50 mm** sections. Tomato needs hard-core-only removal, eight **35–55°** wedges of **0.65–1.35×** mean mass, severed skin, retained pulp/seeds and <10% compression. Separate bowls and **≥98% cut-edible-mass transfer** remain mandatory. Fixed leaf/eye counts, nominal blade size and timers do not establish these outcomes. Model actual child/scrap geometry, screen residue, sanitation and retries without inventing food or unexplained edible loss.

5. **HIGH — Clearance improves substantially, but installed robustness is unproved.** Reserve is the minimum over applicable checked pairs above the unchanged 10/5 mm gates, not an average of category minima.

   | Population | N | Min reserve, mm | P5 | Median | P95 | Fraction ≥10 mm |
   |---|---:|---:|---:|---:|---:|---:|
   | Selected static poses | 150 | 12.000 | 12.000 | 15.000 | 23.000 | 100% |
   | Actual prefix samples | 1,404 | 0.926 | 12.988 | 23.000 | 23.000 | 96.724% |

   T01 loaded transit has **17 mm** extra reserve; empty approach has **16.977 mm**. These are useful improvements. However, T02 lift and fresh support strokes reach approximately zero reserve at window exit. Crossing the mandatory gap is unavoidable; a sampled minimum of 0.926 mm is not a manufacturing allowance for that transition. The distribution is sample-weighted, including repeated segment endpoints, not time-weighted or a complete-meal minimum. [Distributions](../../sim/r06/reviewer/v2/metrics.json), [samples](../../sim/r06/reviewer/v2/paths.json).

   No tolerance stack covers key/pan size, absolute calibration, fixture position, frame/arm compliance and stopping deflection. Stand sections, joints, fastener load path, feet and tipping are unreleased. Apply the [OEM stand guidance](https://www.universal-robots.com/manuals/EN/HTML/SW10_13/Content/prod-usr-man/complianceUR5e/H_g5_sections/mechanical_interface_g5/dimension_stand.htm) to the selected operating/stop load cases; repeatability is not installation accuracy. Keep ≥20/15 mm nominal ordinary transit gaps and allocate reserve. Closed **1606×906 mm** is **106 mm wider** than the approximate target's upper end; retain this deviation. The outward door also needs roughly **1.6 m** front service sweep space.

6. **HIGH — Arm loads pass the tested scope; process forces remain conditional.** The [UR5e specification](https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf) supplies 5 kg payload, 850 mm reach and arbitrary mounting. Re-evaluating six side-mount envelope witnesses on the retained 5 kg/350 mm CoM basis agrees within **8×10⁻¹¹ Nm**. This is witness replay, not new global optimization or unpublished continuous-torque data. Full EOAT and added 0.40 kg pan assemblies are counted. The 3 kg external challenge plus 1.2 kg EOAT passes admitted held poses: worst ratio **0.562124**, minimum grip margin **1.874464**.

   Accepted arm paths were replayed with Cartesian ±1.89 N and the equivalent CoM moment, enclosing **4.2×0.3×1.5 N**. Reconstructed acceleration supports that bound. Cutting reactions belong to the frame only after verified retention and arm withdrawal; they cannot disappear merely by naming an appliance cycle.

   **63 N peel, 52.33 N eye/core, 348.85 N greens and 636.37 N wedge** remain proxy/design loads. The [primary cutting study](https://iseki-food-ejournal.com/article/69/pdf) used 20–40 mm/min and five replicate peaks per condition; width scaling with margin does not qualify fast operation or damage. A 1000 N press target does not specify matched actuator/brake, retention, jam response or safe tomato compression. The 2–5 N leaf band needs calibrated compliance; the [UR sensor accuracy specification](https://www.universal-robots.com/manuals/EN/HTML/SW10_6/Content/prod-usr-man/hardware/arm_e-Series/UR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm) alone cannot establish it. [Load/envelope evidence](../../sim/r06/reviewer/v2/auxiliary.json).

7. **HIGH — Home safety is appropriately scoped, but guard/stop/retention implementation is unfinished.** One **CNY 16,000** package includes enclosure, access/output interlocks, E-stop, presence/start inhibit, relay/contactor, RCD/PE and no automatic restart. Industrial scanners, light curtains and a safety PLC are not imposed. Documented arm holding in the chosen mount satisfies the binding home-brake criterion; unpublished continuous torque or brake spring construction is not reinstated as a blocker. The retained [UR brake evidence](../../sim/r06/reviewer/audit/ur_brake_read.json) and cited [OEM manual](https://www.universal-robots.com/manuals/EN/PDF/SW5_21/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf) remain the documentary basis.

   Gravity-loaded blade, lid and insert drives need matched de-energize-to-apply brakes/catches, retained loads and stop-before-access behavior. Recorded `door_locked=true` is a contract, not a hardware demonstration. The submitted service-door sweep checks robot clearance only; it does not qualify hinges/jambs, latch strength, interlock delay, tool coast-down or output access. Inhibit appliance motion and output release until guard/retention conditions are proved. Record future fault protocols; physical tests remain deferred.

8. **HIGH — Water, power and cleaning remain engineering interfaces.** A **2 L** charge in a nominal **2.8 L** pan is a preliminary budget, not proof of freeboard with food/insert displacement, agitation, overflow or drainage. Catch-basin and solid pan/land geometry do not define an executable water path. Complete inlet air break, normally closed shutoff, leak/overflow response, valves/suction, structural apertures and screened drainage to the proposed G3/4 inlet and 40 mm trapped drain. Lift food before dirty drainage, clean the pan/insert before returning clean food, and retain peels/cores/solids in the removable bin.

   Three 2 L changes at assumed 6 L/min require **60 s fill time alone**, plus lift, drain, inspection and final 20–30 s potato drainage. This replaces v1's inconsistent 6 L-per-pan assumption. Enforce ≤3 kg transport after drainage; no 2 L water carry is admitted. **1320/(230×0.8)=7.174 A** fits nominal 13 A service, but 1320 W is an allowance, not a matched inrush/leakage/thermal schedule. Hose/cable routing, strain relief, dry power track, ventilation and wet/dry barriers remain incomplete.

   Every wetted insert, key/collar crevice, hinge/seal, roller, brush, blade and pusher needs accessible removal, washing, drainage and correct reassembly. A drip shield does not qualify a controller for wet cleaning. The Nemco manual specifies cleaning/disassembly; it does not document this cell's automatic sanitation. A 300 s cleanup allowance or clean/dirty Boolean is insufficient. [Utility contract](../../sim/r06/integrator/results/utilities.json), [Nemco cleaning instructions](https://nemco.com/wp-content/uploads/2025/06/Operations_Manual_and_Parts_Breakdown-55200AN_10-2014.pdf).

9. **MEDIUM — Cost and prefix-time arithmetic pass; complete prep time and value remain unknown.** Independent addition gives **239,000+35,850=274,850 CNY**, one 15% reserve and one 16,000 safety package. The 150,000 arm/controller and custom mechanisms, installation and commissioning are allowances, not matched current quotes. Unspecified cradle, seals, wiring and qualified drive components can change the installed cost. No cheapest passing option exists.

   The **150.778604 s** prefix is reproduced, including synchronized limits and two mechanism durations; no washing is completed. `prep_min=null` is correct. Stations A's 40.52/45-minute and B's 47.32/56-minute schedules remain concept estimates. Under the adopted whole-width **0.5 mm/s** root-cut model, 2100+2520 s engagement alone is **77 minutes**, before handling, soaking, rinsing and cleaning. This is conditional on that cutter/rate, not a universal limit for another commercial slicer. Recompute the calendar from actual processing states, force/rate limits and resources. [Costs/time](../../sim/r06/reviewer/v2/metrics.json), [timing reconstruction](../../sim/r06/reviewer/v2/auxiliary.json).

## Next steps

1. Preserve the passing first transfer and owned-window regressions. Finish insert/cradle drive, retention and brush access; extend the persistent prefix through a genuine wash, drain, lid closure and release before further meal credit.
2. Repair all three process interference pairs at full size. Choose a specific commercial cutting subsystem with real cover, pusher, controls, loading and cleaning, or fully model and budget these custom mechanisms. Preserve terminal pieces and scrap paths.
3. Implement every food split, supported handoff, inspection and retry. Bind food/bowls/jaws/lids/guards/drives/water/sanitation to one sequence; check every connection with ≥60 s planner allocations, restarts/staging/shortcutting and ≤4 mm replay. Do not reset to convenient raw-pan scenes after failed processing.
4. Define clearance/tolerance and structural budgets, stop loads and tipping. Reconcile the 1606 mm width and service sweep with home installation. Complete water/power routing and removable cleaning interfaces within the home safety tier.
5. Recompute calendar and BOM. Document future food-quality, wet-retention, cleaning and power-loss protocols. **Physical tests remain deferred; no purchasing or supplier contact is authorized by this review.**

## Reproduction and delivery

Run `C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe sim/r06/reviewer/bounded_v2.py TASK`, with `TASK` = `audit`, `statics`, `paths`, `mechanisms`, `conservation`, `auxiliary`, then `metrics`. Foreground chunks use **1100 s** timeout, **1900 MiB** process/job limits, CPU only and one numerical thread. Maximum successful worker peak was about **412.5 MiB**; longest successful chunk **73.9 s**, with at most three numerical workers concurrent. Corrected initial harness errors remain in run logs; none supplies passing evidence. No new planner search or physical experiment is claimed.

Final hashes report **no changed upstream inputs, integrator/stations outputs or R04/R05 files**. Only this role's R06 scripts/evidence and `posts/r06/reviewer.md` were written. Total R06 files were about **410 MiB**, below 3 GB. Verification counts establish the scope above, not product acceptance.
