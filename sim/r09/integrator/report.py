"""Assemble results without turning prospective motion into execution."""
import csv,collections,hashlib
import numpy as np,mujoco
from scene import H,ROOT,load,save,build
from checker import Checker
from state import World
def main():
 cfg=load('results/selected.json')['config'];strokes=[load(f'results/strokes/{i}.json') for i in range(11)];replays=[load(f'results/replay/{i}.json') for i in range(11)];connections=[load(f'results/connections/{i}.json') for i in range(10)]
 rows=[];blockers=[]
 for i,(s,replay) in enumerate(zip(strokes,replays)):
  counts=collections.Counter();hits=collections.Counter();starts=0
  for endpoint in [0,1]:
   r=load(f'results/statics/{i}_{endpoint}.json');starts+=r['starts'];counts.update(r['status_counts'])
   for candidate in r['rows']:
    for hit in candidate.get('check',{}).get('hits',[])[:1]:hits[tuple(hit['pair'])]+=1
  row=dict(index=i,name=s['target']['name'],static_ok=s['static_ok'],internal_ok=replay['internal_pass'],starts=starts,status_counts=dict(counts),dominant_rejections=[dict(pair=list(p),count=n) for p,n in hits.most_common(3)],internal_reason=s['internal'].get('reason'),admitted_replay_states=len(replay['rows']))
  rows.append(row)
  if not row['internal_ok']:blockers.append(row)
 pass_count=sum(r['internal_ok'] for r in rows);static_count=sum(r['static_ok'] for r in rows)
 save('results/phase_summary.json',dict(carrot='fail',products_completed=0,products_total=4,strokes_pass=pass_count,strokes_total=11,static_endpoint_pairs_pass=static_count,rows=rows,meaning='11 manipulation templates, not a qualified expanded meal controller; no executions inferred from local path success',other_products=[dict(name=n,status='deferred after carrot-first failure; finished-product contract preserved') for n in ['potato','bok choy','tomato']]))
 save('results/motion.json',dict(connections_pass=0,connections_total=10,geometric_staged_connections=sum(r['planner']['ok'] for r in connections),local_internal_paths=pass_count,rows=[dict(index=r['index'],from_stroke=r['from_stroke'],to_stroke=r['to_stroke'],executed=False,geometric_ok=r['planner']['ok'],same_attachment=r['same_attachment'],stages={k:dict(ok=r['planner'][k]['ok'],reason=r['planner'][k].get('reason'),budget_s=r['planner'][k].get('budget_s'),elapsed_s=r['planner'][k].get('elapsed_s')) for k in ['fold','base_move','unfold']}) for r in connections],base_motion='freeze arm in safe carry; nonholonomic chord gate; whole cart/arm/cable checked; none credited as executed',binding='tool/food release, station latches and movable catch tray ownership remain unqualified'))
 w=World();save('results/state_sequence.json',dict(**w.snapshot(),status='UNCOMMITTED',carrot_pass=False,products_completed=0,connected_sequence=[],required_unqualified_events=['supported raw grasp with full fingers','wash ownership and surface coverage','peeler drawer/latch food seat and retrieve','post-peel rinse','holder pickup food clamp/trim including10mm terminal stub','guard closure and opening','tray detachment and edible delivery>=98percent','separate contained scrap route','tool return and park'],transformation_policy='Only contained station-owned food changes permitted; no physical robot/container event abstracted; all four source masses still raw,total0.57kg'))
 samples=[dict(x,stroke_index=r['index']) for r in replays for x in r['rows']];routes=load('results/replay/routes.json');samples+=routes['rows'];maps=load('results/replay/maps.json');samples+=maps['rows'];tiprows=[x['tip'] for x in samples]
 tree,meta=build(cfg);ch=Checker(tree,meta);park=np.array(load('assets/park_mobile.json')['q']);parkcheck=ch.check(park);tiprows.append(parkcheck['stability'])
 mintip=min(x['min_margin_m'] for x in tiprows)
 save('results/stability.json',dict(pass_for_saved_admitted_samples=all(x['ok'] for x in tiprows),min_tip_margin_m=mintip,min_tip_margin_mm=mintip*1000,min_restoring_moment_Nm=min(x['min_restoring_Nm'] for x in tiprows),samples=len(tiprows),executed_sequence_samples=0,scope='All saved admitted endpoint candidates, selected M11 maps and .85m design probes, every saved passing internal path state and folded parking. Complete meal not admitted. Final audit supersedes earlier pilot1.5-process-only figures.',method='Ground ZMP from sum(gravity moments + process moments + acceleration moments); signed distance to inset4-wheel rectangle. 1.5 multiplies moving-arm and held gravity, process loads, acceleration and cable disturbance. Minimum over both process-force signs, both horizontal acceleration directions, and any horizontal cable pull.',assumptions=['level support with four tyres in contact','inset215x175mm half support polygon','0.15m/s2 base acceleration','20N cable cap at100mm inlet','secured46.6kg ballast','drive brake coupling not mechanically qualified'],park=parkcheck['stability'],per_stroke=[dict(index=r['index'],samples=len(r['rows']),minimum_m=min((x['tip']['min_margin_m'] for x in r['rows']),default=None)) for r in replays]))
 categories={};sub2=[]
 for x in samples:
  for cat,v in x['clearance'].items():
   categories.setdefault(cat,[]).append(v['reserve_mm'])
   if v['reserve_mm']<2:
    pair=' '.join(v.get('pair',[]))
    reason='Inherited rigid palm/key shoulder self-category at zero self gate; no robot/environment gap exemption. Mechanical contact qualification remains open.' if cat=='self' else 'Faucet/gripper water-entry corridor uses almost the entire hard gap; localization and compliance make this a robustness blocker, retained as an independent diagnostic only.' if 'faucet' in pair else 'Wrist/guard loading corridor converges to a tangent clearance optimum; retained to expose the structural bottleneck, not to claim robust connected execution.' if 'mandoline_guard' in pair else 'Forearm/sink-rim approach has insufficient installation reserve; this candidate is retained as failure-analysis evidence, not a hardware-release pose.' if 'sink' in pair else 'Near-gate candidate retained for transparent evidence; no robust connected execution is credited.'
    sub2.append(dict(stroke_index=x.get('stroke_index'),label=x['label'],category=cat,clearance=v,written_reason=reason))
 dist={cat:dict(samples=len(a),min_reserve_mm=min(a),p05_reserve_mm=float(np.percentile(a,5)),fraction_at_least10mm=float(np.mean(np.array(a)>=10))) for cat,a in categories.items()}
 save('results/clearance.json',dict(scope='Saved admitted independent candidates and local stroke states; no executed meal statistics',categories=dist,under2mm=sub2,under2mm_reason='Self category can be zero at rigid palm/key shoulder faces under inherited reference policy. Nonself sub2mm entries are disclosed numerical near-gate configurations, not fabrication-ready; no gate waived.',most_states_target_pass=all(v['fraction_at_least10mm']>=.5 for cat,v in dist.items() if cat!='self'),localization_assumption=load('results/hardware.json')['mount']['localization'],robustness_status='Nominal geometrical gates only; not a calibrated-neighbourhood or compliance certificate'))
 duration=[]
 for i,s in enumerate(strokes):
  if not replays[i]['internal_pass']:continue
  q=np.array(s['internal']['path']);t,meta=build(cfg,s['target']['held']);c=Checker(t,meta);total=0.
  for a,b in zip(q[:-1],q[1:]):total+=max(c.point_bound.segment_bound(a,b)/(.02 if s['target']['kind']=='working' else .05),float(max(abs(a[3:9]-b[3:9]))/.25))
  duration.append(dict(stroke=i,duration_s=total,scope='local checked path timing only; conservative all-point speed bound, no meal execution'))
 save('results/schedule.json',dict(prep_min=None,executed_paths=[],prospective_local_path_times=duration,reason='No connected carrot path or station ownership sequence; no fabricated total preparation time',speeds=dict(tool_transfer_m_s=.05,process_m_s=.02,base_m_s=.10,base_acceleration_m_s2=.15,joint_rad_s=.25),station_times=dict(carrot_peeler_s=2823.529,potato_peeler_s=2823.529,bok_choy_soak_s=600,potato_postcut_rinse_count=[2,3],potato_drain_s=[20,30],root_wash_s=None,mandoline_complete_batch_s=None,tomato_complete_wedging_s=None),time_sources=dict(peeler='Inherited P16 sizing:150N at3.4mm/s,200mm travel,20percent duty; not observed kitchen peeling',soak_drain='inputs/cook_ref.md; stage times do not certify cleaning'),power=load('results/hardware.json')['power']))
 save('results/blockers.json',dict(numerical=blockers,structural=['Raw support does not provide clearance under full fingers; add actual end cradles before reuse','Peeler cutter/cradle/guard corridor needs a qualified food-grasp and retractable mechanism','Full tray and bails require real detachable support/grasp transitions','Wash poses do not prove every surface rubbed/rinsed; no all-surface path or contained wash ownership','Custom hub brake load path and automatic reel retrieval remain open','Unknown real end alcove; parking certification is conditional']))
 costs=load('results/cost_summary.json');reply=f'DONE integrator carrot=fail products=0/4 strokes={pass_count}/11 connections=0/10 idle=fail min_tip_margin={mintip:.6f} prep_min=null cost_cny={costs["total_cny"]:.2f}'
 (H/'results/final_reply.txt').write_text(reply,encoding='utf-8')
 save('results/delivery_audit.json',dict(stop_condition='b',documented_iterations=len(list((H/'results/iterations').glob('M??.json'))),reference_sha256=hashlib.sha256((ROOT/'sim/r05/integrator/reference.py').read_bytes()).hexdigest(),regression=load('results/regression.json'),replay_failures=sum(len(r['failures']) for r in replays),idle_connected=False,output_bytes=sum(p.stat().st_size for p in H.rglob('*') if p.is_file()),final_reply=reply))
 print(reply)
if __name__=='__main__':main()
