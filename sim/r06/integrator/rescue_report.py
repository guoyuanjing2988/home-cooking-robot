"""Write the requested bilingual revision2 report from measured results."""
from rescue_spec import *
def read(n):return json.loads((H/n).read_text())
s=read('results/phase_summary.json');m=read('results/motion.json');t=read('results/schedule.json');cl=read('results/clearance.json');cost=read('results/cost_summary.json');ex=read('results/exit_condition.json');ff=read('results/final_force_witnesses.json');pl=read('results/final_path_loads.json');validation=read('audit/revision2_validation.json');recipe_data=read('results/recipe.json');prefix=read('results/executed_prefix.json')
max_t=max([x['torque_ratio'] for x in ff]+[x['maximum_torque_ratio'] for x in pl]);min_g=min([x['grip_margin'] for x in ff]+[x['minimum_grip_margin'] for x in pl]);pct=cl['executed_all_reserve_mm']['fraction_at_least10mm']*100;spct=cl['static_selected_endpoint_reserve_mm']['fraction_at_least10mm']*100;prefix_min=cl['persistent_prefix_min_reserve_mm']
text=f'''中文摘要：本次按独立工作站方向继续修改，保留了[第一版记录](integrator_v1.md)及其完整仿真快照。新增L08–L17布局试验，其中L08、L10、L11、L12、L13、L14各有96次独立抓取搜索；L09是未采用的早期接口草案，不计入六次有效布局迭代。最终L17采用一台固定侧装UR5e、开放式盆托、外置盆盖驱动、横向刀具停放机构，并将完整食物杯上移80 mm，闭合防护外廓为1606×906 mm。首次抓取的食物杯／背板干涉已消除，实际连续前缀完成抓取、搬运、落盆、松爪、退出，以及洗涤站夹紧和开盖。支承接触权限已绑定到所属容器及指定支承面，错误身份不能放行。

静态结果为 **{s['static_strokes_passed']}/{s['static_strokes_total']}**，其中整盆抓放为 **{s['handling_strokes_passed']}/{s['handling_strokes_total']}**；每个整盆问题有96次起点覆盖。整餐实际连接为 **{m['connections_passed']}/{m['connections_total']}，FAIL**，没有完成任何一种食材。原料保持0.57 kg守恒，未把计时、停车姿态或原料盆演练算作清洗／切割完成。实际前缀最小额外间隙 **{prefix_min:.3f} mm**，{pct:.1f}%的检查状态达到额外10 mm；所选静态端点中{spct:.1f}%达到该目标。若计入有条件的原料盆演练，支承转换处最小余量约为0 mm。完整备菜时间为`null`，已执行前缀含20 s启动准备为{t['executed_prefix_s']:.1f} s；候选预算 **¥{cost['total_cny']:,.0f}**。本次依据用户允许的“至少六次有证据的布局迭代仍有阻塞”条件交付，不声明产品通过。

# R06 integrator — revision2

**Result: useful handling progress; the meal remains incomplete.** The binding
[decisions](../../DECISIONS.md), especially the dedicated workstation and owned
contact-window rules, remain unchanged. The R06/R05/R04 reviews, R02 tools,
[food reference](../../inputs/cook_ref.md), key poses and stations proposal were
read. The later R07 placement does not apply here. All changes are confined to
this role's R06 simulation and posts. No purchase, supplier contact or physical
test was made.

The person loads the four labelled front pan bays while stopped, leaves the
workspace and closes the interlocked door. The same ingredient-specific pans
are intended to become separate output bowls; they cannot be released as
finished outputs until food acceptance passes. Waste has a removable bin.
The basin, frame, worktop, full controller, dry power partition, water/drain
hookups and one household feed belong to the module. The outward service-door
sweep requires additional access space. The footprint increase provides actual
open corridors and full base/support geometry; it is not hidden in a kitchen.

## Simplification and layout evidence

The proposal has **{recipe_data['supervisory_events']} supervisory events**,15
whole-pan transfers and30 grasp/release obligations. A combined root-processing
cycle replaces repeated arm tool exchanges. Cutting, peeling, eyes, terminal
pieces, wash coverage and clean/dirty resets remain mandatory inside each cycle.
The expanded record retains **{s['processing_obligations_total']} required
appliance operations**, all unqualified for static admission. Their repeated
food-dependent subcycles are still incomplete; this is a lower-bound obligation
inventory, not proof that all variable leaves/eyes/cuts have been enumerated.

| Layout | Physical change and evidence |
|---|---|
| L08 | Whole food cup translated140 mm; first key conflict removed but front door becomes an obstruction |
| L09 | Open docking proposal; plate obstructs shoulder; discarded prototype, no passing credit |
| L10 |1600×900 mm frame; full restored/enlarged blade/pusher and base-plane plate; fixed shoulder/plate gap3 mm fails10 mm gate |
| L11 | Fixed90° side mount; full plate recessed30 mm with four base fasteners; valid pickup branches |
| L12 |500 mm rear rail trial; valid pickup branches, but fixed layout avoids rail hardware/drive qualification |
| L13 | Connected raised keys and rear blade parking; first eight-path pan transfer passes; handle bolts obstruct lid |
| L14 | Outboard key bridge and integral lid drive; eight-path transfer passes; full shaft intersects closed lid |
| L15 | Full shaft translated rearward; gearbox enlarged; clamp and lid opening pass from actual arrival |
| L16 |250 mm lateral blade parking with full rail/motor; fixed-yaw routes still encounter the carried pan against the upper arm |
| L17 | Complete cup raised80 mm with CoM update; clears returned-pan shaft obstruction; repeated first transfer and wash clamp/lid pass |

[Iterations CSV](../../sim/r06/integrator/results/iterations.csv) links the
per-seed witnesses and retained rejected variants. No OEM link, food, cup, palm
or source pan is shrunk. The old shared cage is replaced by an explicitly
different dock/interface architecture, not hidden from collision checking.
L10 onward retains the full140×110 mm blade with larger carriage. The L09
discarded draft is excluded from the six qualifying layout trials.

The selected arm is the real, unscaled UR5e model:5 kg rated flange payload,
850 mm reach, source OEM link inertias and restored base meshes. There is no
moving arm rail in L17. The1.2 kg EOAT remains full size; each pan gains0.40 kg for
its handle/drive assembly, counted once with its actual combined CoM.
[UR5e datasheet](https://www.universal-robots.com/media/1807465/ur5e_e-series_datasheets_web.pdf).

## Interfaces and commodity decision

The named330×245 mm support lands accept the complete265×163 mm pans without
a pocket insertion. The arm approaches the exposed key from80 mm above it.
The side retainer, full hinged lid, drive housing/shaft, parked blade, pusher,
their joints, owning faces and commanded sweeps are present. The detailed
[interface record](../../sim/r06/integrator/v2/interface_review.md) identifies
every implemented boundary and missing mechanism.

Actual commodity alternatives were rechecked. The CL20 has a documented feed
tube/hopper and nominal5 mm disc; a closed pan is not that interface. The
Nemco55200AN manual defines a trough, cover, pusher and crank, so adapting it
would require those complete motions plus individual-root loading and terminal
recovery. DitoSama batch peelers do not establish this small meal's peel-depth
and eye-removal requirements. None is represented as a fictitious small
turnkey box. [CL20](https://www.robot-coupe.com/uk/en_GB/p/vegetable-preparation-machines-cl-20/18232),
[Nemco manual](https://nemco.com/wp-content/uploads/2025/06/Operations_Manual_and_Parts_Breakdown-55200AN_10-2014.pdf),
[DitoSama range](https://www.ditosama.com/en/products/multipurpose-peelers/).

**The custom processing interface is still incomplete.** The source insert has
a120 mm slide joint, whose sweep is checked conditionally. Its complete drive,
latch/guide, turn/brush trajectories and drain hardware remain unqualified.
In processing, a supported food cradle is needed above the full pan
wall before the pusher/blade can work. Controlled peel/eye access, cut child and
scrap solids, every leaf/crease, tomato core and radial slicing, final edible
stub recovery and a retained waste path are not implemented. These are design
tasks, not claims that the concept is physically impossible. Fixed structure
and plumbing apertures also need a buildable, cleanable construction model.

The conditional carrier lift clears its120 mm geometric sweep, but its drive
interface is not qualified. Further process sweeps reject carriage/rear-guard
penetration at1.310 mm, pusher/lid-drive penetration at0.750 mm, and blade/worktop
penetration at0.036 mm. No working-contact exception applies to these pairs.
[Mechanism evidence](../../sim/r06/integrator/results/mechanism_motion.json).

## Reference, statics and loads

The copied R04/R05 reference, planner, motion checks and distance/point-bound
sources remain byte-identical. Gates stay5 mm/3°,10 mm robot/environment and
arm/arm,5 mm held/gripper/environment, PAD0, μ0.5, SF1.5 and150 N/15 Nm key
capacity. The R06 adapter now resolves `support_id` to its owning support face
and object, verifies the support normal and held ancestry, and rejects working
permission on non-working motion. Adversarial wrong-support, wrong-face,
wrong-object, sideways-axis and transit tests are recorded in the
[validation](../../sim/r06/integrator/audit/revision2_validation.json).

Each handling problem has96 independent collision-aware starts and a20 s
per-start rescue budget where needed. Each candidate checks open acquisition,
closed jaws before ownership, retained seating, lifted pan and empty retreat.
Exact handoff alignment is additionally required so ownership changes preserve
all geometry within10 μm. A branch-invariant obstacle can terminate a start
with its geometric proof. Byte-identical complete scenes/targets/policies may
reference the same96-start certificate; aliases contain full hashes and are
not called additional solver executions. All other problems are independently
searched. Appliance operations without a physical target get no parked-arm
proxy credit and have **not** received the requested96 meaningful IK starts.
L17 seeds include independent0.15 rad perturbations of previously validated
branches and same-target ingredient candidates; these are new full-scene solves,
not claims of96 uniform global samples. Failed unseeded branches retain their
full20 s rescue attempts and rejection witnesses.

The90° mounting-specific payload envelope is recomputed with the unchanged
equations,5 kg and350 mm CoM radius, three optimization restarts per joint.
Numerical maxima are conservative capability estimates. All final selected
poses and accepted paths are replayed with a Cartesian±1.89 N force box at the
assembly CoM, including its equivalent moment. The bound encloses the
4.2×0.3×1.5 carry-force assumption. Maximum demand/envelope is **{max_t:.4f}**;
minimum key grip margin is **{min_g:.4f}**. The separate3 kg external-payload
challenge includes1.2 kg EOAT; its scope is the admitted witness poses.
[Force witnesses](../../sim/r06/integrator/results/final_force_witnesses.json),
[path loads](../../sim/r06/integrator/results/final_path_loads.json),
[payload challenge](../../sim/r06/integrator/results/payload_capability.json).

OEM power-off holding in the chosen arbitrary mounting meets the binding
home-tier documentary criterion. Custom gravity drives still need normally
applied brakes and catches; installed components and fault tests are not
qualified. [UR manual](https://www.universal-robots.com/manuals/EN/PDF/SW5_21/user-manual-UR5e-PDF_online/710-965-00_UR5e_User_Manual_en_Global.pdf).
The arm withdraws before appliance working force. Source cutting/peel/wedge
loads remain fixture-design proxies; the cutting study's20–40 mm/min speed
does not support an invented fast cycle. [Primary force study](https://iseki-food-ejournal.com/article/69/pdf).

## Connected execution, clearances and remaining work

The actual prefix starts with four original foods totaling0.57 kg and records
every joint, jaw, pan, lid, appliance, guard, water and ownership state. The
first pickup and all eight transfer paths pass; clamp and lid opening then
pass from that same state. No food has been duplicated, peeled, cut or declared
washed. The next blocked event is **{prefix['blocked']['event']}**.

The separate raw-pan route rehearsal has **{m['raw_pan_rehearsal']['accepted_paths']}/{m['raw_pan_rehearsal']['attempted_paths']}**
accepted paths and **{m['raw_pan_rehearsal']['completed_transfers']}/15** complete
transfers. It explicitly bypasses unqualified processing and gets zero meal
credit. Failed65 s searches and subsequent staging attempts remain in its
archives. Every admitted path is replayed at≤4 mm displacement of every point;
the planner uses restarts, shortcutting and staged routes. Unsearched downstream
meal paths remain unsearched, rather than being reported as failures after a
fictional compute budget.

The actual-prefix all-pair reserve minimum is **{prefix_min:.3f} mm above the
binding gates**. Low values occur in release/lift or jaw transitions near the
5 mm boundary. Ordinary transit for the first loaded transfer has17 mm extra
reserve; the empty approach has16.977 mm. The static and sampled-path
distributions, including all low reserves and the separate raw-pan rehearsal
minimum of approximately0 mm, are in
[clearance.json](../../sim/r06/integrator/results/clearance.json). Thus the
reserve target is measured, not asserted for every state.

The complete prep time remains`null`. The measured path timeline uses home
speed/acceleration limits, stops at retained knots, and includes only executed
mechanism durations. No unexecuted parallelism is credited. Required600 s
soaking, fresh-water exchanges, draining and feedback-driven retries remain
listed. The candidate cost is¥{cost['total_cny']:,.0f}, including exactly one
¥16,000 home safety package and one15% reserve on the full subtotal. These are
engineering allowances, not current supplier quotations or a passing-product
price. [Schedule](../../sim/r06/integrator/results/schedule.json),
[costs](../../sim/r06/integrator/results/costs.csv).

![Overview](../../sim/r06/integrator/renders/overview.png)
![Door open](../../sim/r06/integrator/renders/door_open.png)
![24 checked-prefix frames](../../sim/r06/integrator/renders/meal_prefix_24.png)

All images use the compiled collision geometry and are≤1440 px. The strip is
24 frames from the **actual raw-food prefix**, never an animation of an
unexecuted meal. Station close-ups and exact frame/model/q provenance accompany
it. Guard transparency is display-only.

Delivery follows condition(b): at least six newly documented, physically
different layouts have96-start evidence and explicit remaining blockers.
Condition(a) is not met. A completed product, full appliance interfaces,
meaningful96-start coverage of those remaining operations, and the full meal
are still outstanding; this result is not a design freeze or build approval.

Reproduce with the supplied venv and `bounded.py rescue_statics --variant 17
--seed-lo 0 --seed-hi 24 --warm-layout 15` (use the disjoint ranges
24–48,48–72,72–96; resume checkpointed runs), then `rescue_meal`,
`rescue_mechanisms`, `rescue_finish`, `rescue_validation`, `rescue_renders` and
`rescue_report`. Each foreground chunk is bounded at1100 s and1900 MiB with
one numerical thread; at most four simulation workers run together. Source
copies and binding-input hashes remain under audit. The original delivery's
artifacts are preserved under`history/v1/`.
'''
(ROOT/'posts/r06/integrator.md').write_text(text,encoding='utf-8');print('POST_WRITTEN',len(text))
