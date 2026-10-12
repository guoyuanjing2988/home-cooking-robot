"""Assemble the requested Chinese-first post from completed evidence."""
import json,csv,math,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def number(x,n=3):return '—' if x is None else f'{x:.{n}f}'
def load(p):return json.loads(p.read_text())
def main():
    b=load(HERE/'results/best.json');c=b['config'];ds=sorted(b['designs'],key=lambda d:d['config']['count']);loads=load(HERE/'results/loads.json');v=loads['maxima']
    railM=v['carriage_moment_norm_Nm']['value'];cantM=v['cantilever_moment_Nm']['value'];force=v['carriage_force_norm_N']['value'];drive=v['carriage_drive_with_assumed_drag_N']['value'];maxRailM=max(railM,cantM)
    lines=[f"本轮建议继续评估 {c['arm']}×{c['count']}：后墙水平轨道中心距台面 {c['height']:.2f} m，机械臂基座向下倾斜 30°，离墙 {c['standoff']:.2f} m，夹持点距法兰 {c.get('grip_extension',.14)*1000:.0f} mm。最佳设计在每阶段 96 个种子的检查中有 {b['phases_passed']}/16 阶段找到通过模型检查的姿态。夹持、工具、载荷方向、5 mm/3° 位姿容差和碰撞间隙规则均保留原版。",
      "这个阶段数是有条件的模型结果：xArm 的力矩参考值由厂家额定电机力矩和减速比推导，公开资料没有确认连续关节输出力矩或齿轮效率。也没有确认每个承重关节的制动器都采用弹簧施加。因此本轮没有宣称全约束已验证的可投用设计。原始种子、完整差异、力矩敏感性和未通过原因均保留在结果中。",
      f"按 3 kg 工具端载荷和原规定力矢量进行独立静载尺寸估算，单小车最大合力 {force:.1f} N、轨道连接点最大合力矩 {railM:.1f} N·m；外侧支承处悬臂估算达到 {cantM:.1f} N·m。驱动静力加声明的摩擦/线缆拖力余量为 {drive:.1f} N，动态制动载荷还需另算。",
      f"另行将通过姿态的工具端载荷提升到 3 kg，并施加原规定载荷后，最差力矩比达到 {v['admitted_pose_full_payload_torque_ratio']['value']:.2f}，超过参考额定值。因此，5 kg 标称负载不能证明本任务的全载荷能力；原阶段通过数仍按原版规定的物料质量计算。",
      "两臂和三臂均完成 16 阶段、每阶段至少 96 个种子的检查及黄金 mandoline 检查。第三臂没有获准分担原定义的工具力；单轨两端停车会占用篮筐附近需要的基座位置。新增机械臂是否改善并行节拍，需要另一个任务和轨道布局验证。五张图使用真实模型求得的姿态，由 Blender 在 CPU 上渲染。",
      "\nEnglish engineering record — 2026-10-07\n",
      f"The leading conditional model screen is **{c['arm']}×{c['count']}**, rail height **{c['height']:.2f} m above the 0.850 m counter**, **{c['orientation']}**, **{c['standoff']:.2f} m stand-off**, with a **{c.get('grip_extension',.14):.3f} m flange-to-grasp extension**. It admits **{b['phases_passed']}/16** phases under the explicitly derived rated-motor torque reference. No fully verified continuous-output-torque admission is claimed. This is a partial concept result, not a released kitchen robot.",
      "\n**Final 96-seed results**\n",
      "Each value is the input checker's admitted-seed count and the lowest worst nominal torque ratio for that phase. P11/P12 counts pair independently admitted strokes as the original checker specifies. Ratios marked † are IK/collision diagnostics for a failed phase; they are not feasible witnesses. Check-force ratios remain diagnostic.",
      "\n| Phase | Process | 2 arms: seeds / nominal ratio | 3 arms: seeds / nominal ratio | 2 arms: check ratio |",
      "|---|---|---:|---:|---:|"]
    sweep=list(csv.DictReader((HERE/'results/sweep.csv').open(encoding='utf-8',newline='')))
    measured=[r for r in sweep if r['stage']!='static']
    measured.sort(key=lambda r:(-int(r['phases_passed']),float(r['best_worst_ratio']) if r['best_worst_ratio'] else 99,int(r['count'])))
    leaders=[]
    for row in measured:
        if row['arm'] not in [x['arm'] for x in leaders]:leaders.append(row)
    ranking=["\n**Arm-family sweep comparison**\n",
        "Each row is that family's best observed entry. Seed density and rating eligibility are shown because the coarse two-seed results do not support an exhaustive comparison with the final 96-seed design. The complete 754-entry CSV retains unmeasured phase fields as blank.",
        "| Arm / count | Height / mount / stand-off | Observed phases | Seeds / stage | Admitted torque ratio | Nominal payload eligible | Torque reference |",
        "|---|---|---:|---|---:|---|---|"]
    for row in leaders:
        ratio=float(row['best_worst_ratio']) if row['best_worst_ratio'] else None
        ranking.append(f"| {row['arm']}×{row['count']} | {row['height']} m / {row['orientation']} / {row['standoff']} m | {row['phases_passed']}/16 | {row['seeds']} / {row['stage']} | {number(ratio)} | {row['nominal_payload_eligible']} | {row['rating_status']} |")
    i=lines.index('\n**Final 96-seed results**\n');lines[i:i]=ranking
    for a,z in zip(ds[0]['phases'],ds[1]['phases']):
        def entry(r):return f"{r['feasible_seeds']}/{r['seeds']} / {number(r['nominal_ratio'])}"+(' †' if not r['feasible_seeds'] and r['nominal_ratio'] is not None else '')
        lines.append(f"| {a['phase']} | {a['name']} | {entry(a)} | {entry(z)} | {number(a['check_ratio'])} |")
    lines += ["\n| Design | Phases admitted | Worst best admitted ratio | Phases at assumed 85% gear efficiency | Min active-joint margin | Min flange reach margin |",
       "|---|---:|---:|---:|---:|---:|"]
    for d in ds:lines.append(f"| {d['config']['arm']}×{d['config']['count']} | {d['phases_passed']}/16 | {number(d['worst_best_admitted_torque_ratio'])} | {d['phases_at_efficiency_0_85']}/16 | {number(d['active_arm_min_joint_limit_margin_deg'],1)}° | {number(d['active_arm_min_nominal_reach_margin_m']*1000 if d['active_arm_min_nominal_reach_margin_m'] is not None else None,1)} mm |")
    lines += ["\nReach margin is nominal arm reach minus mounting-plane-to-flange distance in the selected best admitted witnesses; it is a geometric diagnostic, not a workspace certificate. Joint margin is the smallest active-joint distance to a source limit. The 85% sensitivity scales all rated-motor-derived limits by 0.85 and counts the original admitted stroke pools that remain within torque; it introduces no new checker gate.",
      "\n**Golden mandoline check**\n","| Feed reaction | 2 arms: admitted seeds / best ratio | 3 arms: admitted seeds / best ratio |","|---|---:|---:|"]
    golden=[]
    for d in ds:
        g=load(HERE/'results/golden'/f"{d['config']['arm']}x{d['config']['count']}.json");assert g['seeds']>=96;golden.append(g)
    for F in ('40','70','100'):
        entries=[]
        for g in golden:
            ok=[r for r in g['rows'] if r.get('ok')];pool=ok or [r for r in g['rows'] if 'torque' in r]
            ratio=min((r['torque_unrounded'][F] for r in pool),default=None)
            entries.append(f"{g['rated_admission_by_force'][F]}/{g['seeds']} / {number(ratio)}"+(' †' if not ok and ratio is not None else ''))
        lines.append(f"| {F} N, +20 N up, ±10 N lateral | {entries[0]} | {entries[1]} |")
    lines += [f"\nGolden IK/collision-free counts are {golden[0]['ik_seeds']}/{golden[0]['collision_free_seeds']} for two arms and {golden[1]['ik_seeds']}/{golden[1]['collision_free_seeds']} for three arms, out of 96. Force-specific counts use unrounded ratios; the original rounded display is also retained. A dagger marks a collision-rejected diagnostic pool.",
      "\n**Why the remaining phases fail**\n"]
    for p in b['phases']:
        if p['feasible_seeds']:continue
        r=load(HERE/'results/final'/b['id']/f"{p['phase']}.json");block=r.get('dominant_blocker') or r.get('rejected_seed_dominant') or {};pair=block.get('pair')
        witness=f"; witness pair {pair}, gap {block.get('real_gap_mm')} mm against {block.get('required_gap_mm')} mm" if pair else ''
        if block.get('kind')=='IK':
            witness+=f"; dominant local-IK witness misses by {number(block.get('position_mm'),1)} mm / {number(block.get('orientation_deg'),1)}°"
        collision_rows=[x for x in r['rows'] if x.get('ik_ok') and any(s.get('hits') for s in x['segments'])]
        if collision_rows:
            candidate=min(collision_rows,key=lambda x:sum(len(s.get('hits',[])) for s in x['segments']))
            hit=next(h for s in candidate['segments'] for h in s.get('hits',[]))
            witness+=f"; one rejected IK-complete seed contacts {hit['pair']} at {number(hit['real_gap_mm'],1)} mm gap (required {number(hit['required_gap_mm'],1)} mm)"
        lines.append(f"- {p['phase']}: {json.dumps(p['blocker_counts'])}{witness}. Failure is a sampled result, not an exhaustive impossibility proof.")
    replay=load(HERE/'results/third_arm_replay.json');lost=sum(len(p['lost_witnesses']) for p in replay['phases'])
    lines += [f"\nThe identical-pose replay transfers every admitted two-arm stroke into the three-arm scene while retaining R/L poses and adding only C's parked arm. It loses {lost} admitted stroke witnesses. The detailed per-phase counts and collision witnesses are in `results/third_arm_replay.json`. The extra arm supplies no new T08 contact or load-sharing permission. Different independently sampled seed counts alone are not evidence of a third-arm benefit.",
      "\n**Static mounting and drive inputs**\n",
      "These are separate sizing calculations at all IK-complete final poses, including rejected poses for a conservative envelope. Each witness records whether its original stroke was admitted. Every carriage carries 3 kg for capacity sizing: R uses the original mass site, and unused arms use the same phase COM offset in their own tool frames. Reference phase held masses and acceptance remain unchanged.",
      "\n| Quantity | Static envelope |",
      "|---|---:|",
      f"| Per-carriage resultant force | {force:.1f} N |",
      f"| Per-carriage moment at carriage/rail datum | {railM:.1f} Nm |",
      f"| Ideal X drive holding force | {v['carriage_drive_ideal_static_N']['value']:.1f} N |",
      f"| Drive force plus assumed drag | {drive:.1f} N |",
      f"| 1.5× drive-plus-drag allowance | {1.5*drive:.1f} N |",
      f"| Outer-support cantilever moment envelope | {cantM:.1f} Nm |",
      f"| Whole rail net wall force | {v['net_wall_force_N']['value']:.1f} N |",
      f"| Whole rail moment about central wall datum | {v['net_wall_moment_Nm']['value']:.1f} Nm |",
      f"| Worst admitted-pose torque ratio with 3 kg and prescribed loads | {v.get('admitted_pose_full_payload_torque_ratio',{}).get('value',float('nan')):.3f} |",
      "\nThe separate 3 kg capacity calculation exceeds the derived torque reference at an otherwise admitted pose (ratio 1.473). Nominal 5 kg payload alone therefore does not establish the requested 3 kg plus holder and process-force service. Original phase masses and phase gates were not changed to hide this result.",
      "\nThe drive allowance uses |Fx|+0.01×transverse load+15 N cable drag, all declared assumptions. Horizontal gravity does not itself require X drive force, but the rail bearings carry gravity and overturning moment. The spring brake must cover the actual drive-axis holding/stopping case; acceleration, impact and Category 1 stop loads are not included in these static values. The cantilever estimate uses link COM point loads beyond x=-1.50/+0.55 m and distributed beam/carrier weight. It is not a solved four-bracket reaction distribution. The net central-wall wrench is likewise not one anchor's load. `results/loads.json` preserves vector directions, positions and the worst-case witnesses. The final DONE moment field is the larger of the carriage-interface and outer-support cantilever moment envelopes.",
      "\n**Reviewable artifacts and images**\n",
      "The complete numerical grid is [sweep.csv](../../sim/r01/concept/results/sweep.csv); the leading design and both 96-seed phase tables are [best.json](../../sim/r01/concept/results/best.json). Load keyframe 0 (`P06_witness`) in [best_scene.xml](../../sim/r01/concept/models/best_scene.xml), or use the [visual scene](../../sim/r01/concept/models/best_scene_visual.xml). Both reference only assets copied into this workspace. The source manifest is [sources.json](../../sim/r01/concept/sources/sources.json).",
      "\n![Overview](../../sim/r01/concept/renders/overview.png)","\n![Washing at the sink](../../sim/r01/concept/renders/washing.png)","\n![Peeling](../../sim/r01/concept/renders/peeling.png)","\n![Mandoline slicing](../../sim/r01/concept/renders/mandoline.png)","\n![Parked](../../sim/r01/concept/renders/parked.png)",
      "\nThe task images use admitted poses where available; a rejected diagnostic would be explicitly labeled. Parking collision validation is saved separately and conservatively retains the P06 held-tool proxy. Images are 1440×960 pixels. All renders use Blender Cycles CPU.",
      "\n"+(HERE/'report_details.md').read_text(encoding='utf-8')]
    body='\n\n'.join(lines)
    body=re.sub(r'(\|[^\n]*\|)\n\n(?=\|)',r'\1\n',body)
    dest=ROOT/'posts/r01/concept.md';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(body,encoding='utf-8')
    b['loads']=loads;b['max_rail_moment_Nm']=maxRailM;b['report']='posts/r01/concept.md';b['renders']=[f'renders/{name}.png' for name in ('washing','peeling','mandoline','parked','overview')]
    b['conditional_model_phases_passed']=b['phases_passed']
    b['full_payload_service_verified']=False
    capacity='The separate 3 kg capacity calculation reaches ratio 1.473 at an admitted pose; 5 kg nominal payload does not establish full process-force service.'
    if capacity not in b['open_requirements']:b['open_requirements'].append(capacity)
    (HERE/'results/best.json').write_text(json.dumps(b,indent=2));print('REPORT',dest,'bytes',dest.stat().st_size)
if __name__=='__main__':main()
