"""Write the reviewable R08 post from final observed artifacts."""
from collections import Counter
import csv
from scene import H,ROOT,load,save
def main():
 p=load('results/phase_summary.json');idle=load('results/idle.json');cost=load('results/cost_summary.json');clear=load('results/clearance.json');area=load('results/counter_area.json');audit=load('results/delivery_audit.json');reg=load('results/regression.json');motion=load('results/motion.json')
 rows=list(csv.DictReader((H/'results/iterations.csv').open(encoding='utf-8')))
 strokes=[load(f'results/strokes/{i}.json') for i in range(11)]
 blockers=[]
 for s in strokes:
  e=next((e for e in s['endpoints'] if not e['ok']),None)
  hit=(e or {}).get('best',{}).get('check',{}).get('hits',[])
  blockers.append(dict(stroke=s['target']['name'],static_ok=s['static_ok'],internal_ok=s['internal']['ok'],first_saved_diagnostic_hit=hit[0] if hit else None,internal_reason=s['internal'].get('reason')))
 save('results/blockers.json',blockers)
 table='\n'.join(f'| {r["iteration"]} | {r["clear_samples"]}/3 | {r["starts"]} | {r["jet_hits"]} | {r["packing_intersections"]} | {r["change"]} |' for r in rows)
 reserve='\n'.join(f'| {cat} | {v["states"]} | {v["min_mm"]:.6f} | {v["p05_mm"]:.6f} | {v["fraction_ge_10mm"]:.0%} |' for cat,v in clear['distribution'].items() if v['states'])
 failures=[]
 for b in blockers:
  h=b['first_saved_diagnostic_hit']
  if h:failures.append(f'| {b["stroke"]} | {" / ".join(h["pair"])} | {h["real_gap_mm"]:.4f} / {h["required_gap_mm"]:.1f} |')
 elapsed=sum(c['planner'].get('elapsed_s',0) for c in motion['connections'])
 final=(f'DONE integrator carrot=fail products=0/4 strokes={p["strokes_passed"]}/{p["strokes_total"]} connections=0/{p["connections_total"]} idle=fail prep_min=null cost_cny={cost["total_cny"]:.2f} min_reserve_mm={clear["minimum_diagnostic_reserve_mm"]:.6f}' if clear['minimum_diagnostic_reserve_mm'] is not None else f'DONE integrator carrot=fail products=0/4 strokes={p["strokes_passed"]}/{p["strokes_total"]} connections=0/{p["connections_total"]} idle=fail prep_min=null cost_cny={cost["total_cny"]:.2f} min_reserve_mm=null')
 text=f'''中文摘要：本轮新建独立的紧凑实现，完成 **{len(rows)} 轮有记录的结构布局比较**。移除顶端进料处理机，改为完整尺寸的水平曼陀林切片台，并保留原 UR5e、L101 单轨、小车、拖链、水嘴及厨房。最终 I09 固定工位相交为 **{len(audit['final_assembly']['packing_hits'])}**，篮口中心与实际水轴重合；主要加工台顶部为 1.030–1.043 m。完整输出碗提手最高 1.0593 m，比严格的 200 mm 台上目标高 9.3 mm，未缩小几何或隐瞒此项。

胡萝卜仅 **{p['strokes_passed']}/{p['strokes_total']} 个静态动作模板**通过，内部路径 **{p['internal_paths_passed']}/11**，已执行连接 **0/10**，成品 **0/4**。全部十个连接均实际给出 65 秒规划预算；不能把搜索次数、独立姿态或局部前缀算成连续制作。停放快照 **{'通过' if idle['snapshot_pass'] else '未通过'}**，完整折叠／展开与胡萝卜执行未闭合，idle=fail。采用停止条件 **(b)** 交付，不是可制造方案或不可行性证明。备菜时间为 **null**，预算 **{cost['total_cny']:,.2f} 元**；未采购、联系供应商或进行实物试验。

**Result and scope.** The selected scene is I09. This is a failed carrot-first feasibility delivery, not a completed four-product controller. All four finished-product definitions and the 0.57 kg food ledger remain unchanged. The denominator 11 is this round's declared carrot manipulation-template set; it is not comparable to R07's 59 templates or 110 expanded meal connections. Missing physical guard, holder, drawer and transfer bindings are reported, not treated as appliance-internal food transformations. Other product motion sequences were deferred after the carrot failure.

The package is in [sim/r08/integrator](../../sim/r08/integrator/README.md). It contains one scene builder, checker adapter, solver, planner, transactional food-state module and foreground runners. Only the two mesh files actually referenced by the compiled L101 arm, original robot primitives/inertias, complete bowls, selected vendor metadata and source contract were copied. It does not import the old versioned solver stack. [Provenance](../../sim/r08/integrator/results/provenance.json), [final audit](../../sim/r08/integrator/results/delivery_audit.json).

**Geometry decisions.** The counter remains at 0.85 m, cabinet underside at 1.35 m and cabinet front at Y=0.23 m. The complete robot and rail geometry and inertias compare unchanged. Door sensors were rigidly shifted 10 mm wallward to provide 20 mm sweep separation. Closed leaves and cabinet bodies are obstacles during all motion; full opening sweeps apply only to park. No processor is installed and none is charged in the BOM.

The right-front mandoline retains the golden 330 × 120 × 60 mm deck, **65 mm radius** holder sphere, 80 mm work/CoM offset, 0.55 kg loaded-holder budget and 200 mm horizontal stroke. The nominal load is −40 N feed, ±10 N lateral, +20 N up; the binding R05 P06/T08 review check is −60 N, ±10 N, +20 N. The golden file's separate 70/100 N exploration is not substituted for that check. Both lateral signs are checked. Guards are actual obstacles. The custom catch tray uses one identical full geometry definition in its stored and held states; it is not replaced by a bare TCP during delivery.

The P16 envelope remains 480 × 50 × 50 mm, with the complete separate guide and cutter. Its low roof and front drawer replace the raised-lid interface. The retained sourced loads are 63 N tangential and 7.5 N normal. The 200 mm P16 has a 4 N lateral limit, requiring that separate guide; 150 N at 3.4 mm/s and the duty-cycle allowance underlie the inherited 2,823.529 s per-root design time. This is component sizing, not measured peel quality or cycle completion. [Actuonix datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf).

Greens use a low guillotine/splitting fixture; tomato uses a low lever/eight-sector fixture. Their inherited design loads are 348.8516 N and 636.3651 N, respectively, with the original source IDs and proxy limitations preserved. Their complete actuation, lever advantage, tooling travel and food-quality performance remain unqualified. The new low fixtures are custom design envelopes, not matched commercial appliance CAD. [Source and force record](../../sim/r08/integrator/results/sources.json), [unchanged source contract](../../sim/r08/integrator/assets/process_contract.json).

The wash basket keeps its full 240 mm diameter and 140 mm height. The final full shell is tilted 55° and raised bodily 15 mm relative to I08. Its mouth centre is on the vertical jet at X=−0.58, Y=0.43 m; ray-to-mouth radial error is {audit['final_assembly']['radial_offset_mm']:.6f} mm. Raising the entire shell eliminates the previous sink-bottom intersection and leaves approximately 11.7 mm geometric separation. **A real cradle/retention design is still required**; an unsupported tilted basket is not credited as executable washing. No spray cone or successful cleaning is inferred from axis alignment.

**Nine recorded structural iterations.** Every row has three full-scene corridor probes with 96 starts each. A clear sample is one first-pose result, not an admitted complete stroke. I01–I04 exposed an erroneous provisional bowl-centre transform; I05 corrects the complete assemblies using measured source shell-bottom centres. This placement error and its packing evidence remain visible. The later redesign relocates all four complete bowls to the left rear, spreads stations, changes wash approach and restores the original right-rear parking space.

| Iteration | Clear corridor samples | Starts | Jet hits mouth | Fixed-part intersections | Structural change |
|---|---:|---:|---|---:|---|
{table}

[Iteration ledger](../../sim/r08/integrator/results/iterations.csv), [selected scene](../../sim/r08/integrator/models/selected.xml). Zero fixed-part intersections is necessary, not proof of mounting, stability, appliance operation or reachable motion. The support and mechanism gaps above remain real blockers.

**Checker and path evidence.** The wrapper imports the actual immutable [R05 reference](../../sim/r05/integrator/reference.py), using only a read-only metadata shim to suppress the old builder's import-time writes. Its SHA-256 remains `46e9002b222cf92970cfc5b30c10fbe23eed06470b8714fc946ffdd44d0f5681`. The collision, rotation and grip functions are used directly, with independent convex lower bounds for all eligible pairs. Pose gates stay 5 mm / 3°, robot/environment and arm/arm gaps 10 mm, held/gripper/environment gaps 5 mm, PAD=0, μ=0.5, SF=1.5 and 150 N / 15 Nm key capacity. No numerical negative reserve is treated as a build tolerance.

Eight unchanged R07 geometry verdicts from four templates reproduce. The complete test suite reports **{reg['pass_']}**. Contact declarations have explicit kinds, compiled part identities, actual support signatures and immutable registered window descriptions. Wrong object, support, part, frame, finger, stale geometry and working permission on transit reject. Support lift/approach permission ends at 50 mm; it is not renewed to disguise a longer contact path. The 200 mm cutting line is a working stroke. The conservative golden food/holder proxy has an explicitly named short lift permission only at its own mandoline surfaces. Synthetic capability tests are not motion evidence. [Regression](../../sim/r08/integrator/results/regression.json).

Each selected endpoint receives 96 starts: **{p['starts']} starts** over 22 endpoint searches. The optimizer includes collision penalties, source-informed seeds and random full-range starts. Positive candidates receive independent final geometry/load admission. Internal paths must follow the Cartesian line and fixed orientation, and every interpolation uses the model-derived all-point displacement bound ≤4 mm. Only both-endpoint acceptance counts as a static stroke. The sole complete static template, holder loading, fails internally at a saved carrot/guard gap of **4.907906 mm versus 5 mm**, after 38 accepted prefix samples; the rejected edge's step bound is 3.585719 mm. This is a rejection, not an almost-pass or robust design.

Representative saved failed candidate pairs are below. They describe these finite attempts, not global impossibility certificates. Native signed contact values are retained conservatively; the old libccd discrepancy is not bypassed.

| Carrot template | Representative pair | Saved gap / gate, mm |
|---|---|---:|
{chr(10).join(failures)}

The main structural causes remain the arm/wrist corridor into the recessed sink, the under-cabinet approach to supported food and seated peeler tooling, mandoline guard/closed-door interference over the entire stroke, and full-container pickup/delivery access. Replacing the tall processor improves some static reach, but does not solve these interfaces.

All ten consecutive carrot connections actually run RRT-Connect with a **65 s allocated budget**, restarts, staging bias, shortcutting and full ≤4 mm replay for any proposed accepted path. Total recorded planner wall time is **{elapsed:.3f} s**, separate from robot preparation time. Geometric connections: **{p['connections_geometric']}/10**; committed conserved connections: **0/10**. Failed endpoints do not skip the search budget. [Motion](../../sim/r08/integrator/results/motion.json), [phase summary](../../sim/r08/integrator/results/phase_summary.json), [saved blockers](../../sim/r08/integrator/results/blockers.json).

The transactional food state starts at the actual scene input positions. Regions bind to the selected peeler and actual mandoline catch-tray interiors; a caller cannot invent a remote region to transform food. Full input extents, support ownership, unattached food, bulk capacity and mass conservation are enforced. Remote/partial/held transformations, unknown operations, negative times, overcapacity, direct bulk grasp, binding teleport and forged regions reject. The successful transformations in tests are synthetic fixtures. The committed meal remains the initial 0.57 kg state. No real container motion, lid, pusher, interlock, eye/core operation, terminal-stub handling or ≥98% delivery is abstracted away. [State sequence](../../sim/r08/integrator/results/state_sequence.json).

**Idle, reserves and human counter space.** Parked snapshot: **{idle['snapshot_pass']}**. Prospective fold: **{idle['fold']['ok']}**; unfold: **{idle['unfold']['ok']}**; complete idle: **False**. Both path attempts use the exact saved park state and closed-door scene. Open-door rendering is a prospective snapshot, not evidence that the robot reached it. [Idle](../../sim/r08/integrator/results/idle.json).

The following distributions contain admitted diagnostic endpoint/path states only; there is no executed-carrot reserve distribution. They use each state's worst eligible pair, including the original self-nonpenetration category. No accepted state below 2 mm is silently promoted to a buildable installation; any such diagnostic states receive individual reasons in clearance.json.

| Category | States | Minimum extra mm | P05 extra mm | Fraction ≥10 mm extra |
|---|---:|---:|---:|---:|
{reserve}

The fixed bowl-collar/wall-bracket pair has only **6 mm beyond its 10 mm gate**; this limits every sampled robot/environment state and fails the requested majority-at-10-mm reserve objective. The mandatory geometry is retained. Four whole bowl bails also reach 209.309 mm above the counter; strict ≤200 mm compliance is therefore false, and a further full-bail articulation/interface redesign is required. [Clearance](../../sim/r08/integrator/results/clearance.json), [height audit](../../sim/r08/integrator/results/delivery_audit.json).

Conservative free supported counter area at prospective idle is **{area['free_counter_m2']:.5f} m²**, of which **{area['free_front_strip_m2']:.5f} m²** is in the front strip. The 5 mm grid excludes the sink and stove and expands full occupied projections by 10 mm. No unexecuted station stow is credited. It is an area estimate, not ergonomic acceptance. [Counter plot](../../sim/r08/integrator/renders/counter_free_area.png).

**Time and budget.** Preparation time is **null**. The executed timeline is empty because the first connected carrot prefix is not admitted. The schedule explicitly retains the 600 s greens soak, 30 s potato drain, three fresh-water starch rinses and two component-derived root-peeling allowances; unknown washing/cutting/transfer times remain null. Proposed home-tier limits are rail 0.08 m/s, joints 0.25 rad/s, every point 0.10 m/s and acceleration 0.30 m/s². They are not a performed recipe schedule. [Schedule](../../sim/r08/integrator/results/schedule.json).

The clean BOM has base **CNY {cost['base_cny']:,.2f}**, exactly one 15% reserve **CNY {cost['reserve_cny']:,.2f}**, total **CNY {cost['total_cny']:,.2f}**. Exactly one **CNY 18,000** home-safety package covers presence/door sensors, E-stop, RCD/PE, blade/door interlocks and control. Rail brakes are already in the rail line. The processor is removed; custom mandoline, peeler, guillotine, lever wedger and tray allowances replace the old mixed tool bundle. All amounts are planning allowances, not supplier quotations or a cheapest passing design. [Costs](../../sim/r08/integrator/results/costs.csv).

All numerical chunks are CPU-only, under 20 minutes with an explicit timeout and 1,900 MiB guard, at most four numerical workers. The latest measured output is {audit['total_bytes']/1e6:.2f} MB, below 3 GB. The original R05/R07 inputs are not modified. The state/controller and fixture limitations are substantive unfinished work, not waived acceptance gates.

**Renders.** All are ≤1600 px, CPU projections of checked geometry with labelled cutaways. There is **no executed carrot frame strip**, because no carrot sequence executed. The delivered 24-frame strip explicitly shows separate failed wash IK configurations; it must not be read as chronological motion.

- [Overview](../../sim/r08/integrator/renders/overview.png)
- [Wash](../../sim/r08/integrator/renders/wash.png), [peel](../../sim/r08/integrator/renders/peel.png), [mandoline](../../sim/r08/integrator/renders/mandoline.png)
- [Greens](../../sim/r08/integrator/renders/greens.png), [tomato](../../sim/r08/integrator/renders/tomato.png), [output bowls](../../sim/r08/integrator/renders/bowls.png)
- [Prospective park with doors open](../../sim/r08/integrator/renders/parked_doors_open.png)
- [24 unexecuted carrot candidates](../../sim/r08/integrator/renders/carrot_diagnostic_strip.png)

{final}
'''
 out=ROOT/'posts/r08/integrator.md';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text,encoding='utf-8')
 (H/'results/final_reply.txt').write_text(final,encoding='utf-8');print(final,flush=True)
if __name__=='__main__':main()
