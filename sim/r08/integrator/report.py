"""Aggregate only observed results; null means no connected execution exists."""
import csv,json,hashlib,collections
import numpy as np
from scene import H,ROOT,load,save,build,targets,variants
from state import World
def optional(path,default):return load(path) if (H/path).exists() else default
def main():
 selected=load('results/selected.json');cfg=selected['config'];_,meta=build(cfg);ts=targets(cfg,meta)
 strokes=[optional(f'results/strokes/{i}.json',dict(index=i,target=t,static_ok=False,starts=0,internal=dict(ok=False,reason='not_run'))) for i,t in enumerate(ts)]
 connections=[optional(f'results/connections/{i}.json',dict(index=i,executed=False,planner=dict(ok=False,reason='not_run'))) for i in range(len(ts)-1)]
 iterations=[load(f'results/iterations/{c["id"]}.json') for c in variants() if (H/f'results/iterations/{c["id"]}.json').exists()]
 ledger=[]
 for r in iterations:
  hist=collections.Counter(tuple(sorted(h['owners'])) for h in r['audit']['packing_hits'])
  ledger.append(dict(iteration=r['config']['id'],change=r['config']['change'],clear_samples=r['clear_samples'],samples=r['total_samples'],starts=sum(p['starts'] for p in r['probes']),jet_hits=r['audit']['jet_hits_opening'],packing_intersections=len(r['audit']['packing_hits']),structural_obstruction='; '.join(f'{a}/{b}: {n} pairs' for (a,b),n in hist.most_common(4)),evidence=f'results/iterations/{r["config"]["id"]}.json'))
 with (H/'results/iterations.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=ledger[0]);w.writeheader();w.writerows(ledger)
 static=sum(s['static_ok'] for s in strokes);internal=sum(s['internal']['ok'] for s in strokes)
 phase=dict(schema='r08.compact.carrot-diagnostics',layout=cfg['id'],carrot_pass=False,products_completed=0,products_total=4,strokes_passed=static,strokes_total=len(strokes),internal_paths_passed=internal,internal_paths_total=len(strokes),connections_executed=0,connections_total=len(connections),connections_geometric=sum(c['planner']['ok'] for c in connections),starts=sum(s['starts'] for s in strokes),iterations_completed=len(iterations),stop_condition='b: eight documented structural iterations; carrot prefix unexecuted',acceptance=load('assets/process_contract.json')['acceptance'],finished_products=load('assets/process_contract.json')['finished_products'],strokes=[{k:s[k] for k in ('index','target','static_ok','starts')}|dict(internal_ok=s['internal']['ok']) for s in strokes],scope='Counts describe the declared 11 carrot manipulation templates only, not R07 59-stroke coverage or a complete four-product implementation. Cabinet/fixture/food geometry and load gates apply; unresolved hardware events prevent execution. Other products deferred by carrot-first stop condition.')
 save('results/phase_summary.json',phase)
 save('results/motion.json',dict(connected_carrot_pass=False,executed_connections=0,connections_total=len(connections),geometric_connections=sum(c['planner']['ok'] for c in connections),connections=connections,internal_paths=[dict(index=s['index'],**s['internal']) for s in strokes],point_step_limit_m=.004,planner_budget_s=65,scope='All ten consecutive carrot diagnostic connections actually planned. Geometric paths are not conserved execution credit.'))
 world=World();initial=world.snapshot()
 blockers=[]
 for s in strokes:
  if not s['static_ok'] or not s['internal']['ok']:blockers.append(dict(stroke=s['target']['name'],static_ok=s['static_ok'],internal_reason=s['internal'].get('reason')))
 save('results/state_sequence.json',dict(initial=initial,committed=initial,executed_events=[],executed_connections=0,mass_conserved=True,total_food_kg=.57,products_completed=[],blockers=blockers,station_transformation_policy='Full input containment, real support, unattached food, conserved edible plus scrap masses and bulk-volume capacity enforced by state.py. No unperformed guard/holder/tray event abstracted.',unclosed_hardware_events=['peeler drawer seating, guard close/open and latch feedback','whole food transfer into golden holder and terminal 10 mm stub retention','full catch tray detachment and 98% edible delivery','scrap removal and final hardware reset'],prospective_operations=[dict(product='carrot',operations=['load','wash','peel','5mm slices including terminal stub','output','scrap']),dict(product='potato',operations=['wash','peel','eyes','5mm slices','three fresh-water rinses','30s drain']),dict(product='bok choy',operations=['root trim','separate basal creases','600s soak','rub and rinse','split stalks <=15mm','40mm sections']),dict(product='tomato',operations=['wash','core','eight 45-degree wedges'])]))
 all_clear=[]
 for s in strokes:
  for k,e in enumerate(s['endpoints']):
   if e['ok']:all_clear.append((f'stroke {s["index"]} endpoint {k}',e['best']['check']['clearance']))
  if s['internal']['ok']:
   all_clear += [(f'internal {s["index"]} sample {i}',c) for i,c in enumerate(s['internal'].get('clearance',[]))]
 for c in connections:
  if c['planner']['ok']:all_clear += [(f'diagnostic connection {c["index"]} sample {i}',v) for i,v in enumerate(c['planner'].get('clearance',[]))]
 distributions={};low=[]
 for cat in ['robot_environment','held_gripper_environment','arm_arm_or_frame','self']:
  rows=[(label,c[cat]) for label,c in all_clear if cat in c];vals=np.array([c['reserve_mm'] for _,c in rows])
  distributions[cat]=dict(states=len(vals),min_mm=float(vals.min()) if len(vals) else None,p05_mm=float(np.percentile(vals,5)) if len(vals) else None,median_mm=float(np.median(vals)) if len(vals) else None,fraction_ge_10mm=float(np.mean(vals>=10-1e-8)) if len(vals) else None)
  for label,c in rows:
   if c['reserve_mm']<2:low.append(dict(state=label,category=cat,**c,reason='Diagnostic witness only. Below the build-reserve target, not accepted as a robust installation. Geometry and gates are unchanged.'))
 minima=[v['min_mm'] for k,v in distributions.items() if v['min_mm'] is not None]
 clearance=dict(scope='Per-state worst eligible pair on admitted endpoints and fully replayed diagnostic paths; no unexecuted path credited as meal.',executed_carrot_reserve_mm=None,minimum_diagnostic_reserve_mm=min(minima) if minima else None,distribution=distributions,under_2mm_reasons=low,robustness_pass=False,target_most_states_extra_mm=10,selected_fixed_assembly_audit=iterations[-1]['audit'])
 save('results/clearance.json',clearance)
 schedule=dict(prep_min=None,carrot_min=None,executed_path_timeline=[],executed_path_seconds=0,reason='No connected conserved carrot/meal has executed. Static poses and diagnostic links are not a makespan.',home_tier_limits=dict(rail_m_s=.08,joint_rad_s=.25,all_point_m_s=.10,acceleration_m_s2=.30),station_allowances=[dict(name='P16 peeling per root',duration_s=2823.529,basis='Inherited component-data allowance; 200mm strokes, 3.4mm/s and 20% duty; not measured peel coverage'),dict(name='bok choy soak',duration_s=600,basis='cook_ref'),dict(name='potato post-cut drain',duration_s=30,basis='cook_ref'),dict(name='three fresh-water starch rinses',duration_s=None,basis='visual endpoint; flow not validated'),dict(name='mandoline complete batch incl final stub',duration_s=None,basis='200mm geometric stroke is not a verified complete batch cycle'),dict(name='guillotine/wedger batch',duration_s=None,basis='custom mechanism times unqualified')])
 save('results/schedule.json',schedule)
 items=[('UR5e complete arm/controller',150000),('One L101 wall rail, carriage, home brake, chain and brackets',43000),('Electric gripper, washable fingers and keyed retention',12000),('IPC, vision and network',8000),('Mounting and site installation',18000),('Food/force/calibration/stop qualification labour',20000),('Dry household power track and adapters',3000),('ONE home safety package: presence, door sensors, E-stop, RCD/PE, interlocks and control',18000),('GROHE Eurocube 13303000 spout',1500),('NC valve and dry low-voltage plumbing control',300),('P16 actuator/controller, guide, root holder and mechanical guards',6400),('Custom golden mandoline, food holder, clamp and full catch tray',4500),('Low greens guillotine and splitting comb',2800),('Low tomato lever wedger and core fixture',3200),('Full wash basket and tilted cradle allowance',600),('Four complete bowls, bails and lock pins',1600),('Input tray and removable scrap containers',1200)]
 base=sum(v for _,v in items);reserve=round(base*.15,2);cost=base+reserve
 with (H/'results/costs.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['item','quantity','total_cny','basis','status'])
  for n,v in items:w.writerow([n,1,v,'Planning allowance; retained R07 costs or declared custom fabrication estimate; no supplier quote','UNQUALIFIED_DESIGN'])
  w.writerow(['ONE 15% project reserve',1,reserve,'0.15 * base; no other contingency','PLANNING'])
  w.writerow(['TOTAL',1,cost,'One reserve; one safety package; processor removed','NOT_A_PASSING_CONFIGURATION'])
 save('results/cost_summary.json',dict(base_cny=base,reserve_percent=15,reserve_cny=reserve,total_cny=cost,processor_included=False,safety_packages=1))
 sources=dict(access_date='2026-10-09',mandoline=dict(geometry='inputs/mandoline_golden.py: radius 65mm, work offset 80mm, 200mm stroke',nominal_N=[-40,'+/-10',20],check_N=[-60,'+/-10',20],check_basis='sim/r05/integrator/reference.py P06 and inputs/t08_review_phases_layout.md line48; 70/100N golden values are separate sensitivity probes',quality='5mm setting and final stub are declared process requirements, not simulation-verified slicing'),peeler=dict(source='https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf',force_N=dict(tangential=63,normal=7.5),guide_required=True,station_cycle_s=2823.529),wedger=dict(design_N=636.3651,basis='R07 source_catalog F03/F04/M10, inherited sizing proxy, not measured cutter force',lever='Custom low lever geometry provisional; full mechanical advantage and guarded actuation still unqualified'),greens=dict(design_N=348.8516,basis='Inherited F01 width-scaled carrot surrogate, not measured bok-choy force'),alternative_not_installed='https://www.oxo.com/chef-s-mandoline-slicer-2-0.html',spout=dict(source='https://www.grohe-mena.com/en_cy/eurocube-bath-spout-13303000.html',access='Refresh failed; retained user-authorized archived L101 geometry and jet axis'),limitations='Golden mandoline nominal/check values are binding engineering load cases rather than a new measurement. Source proxies are not hardware qualification.')
 save('results/sources.json',sources)
 print('summary',static,'/',len(strokes),'internal',internal,'connections',phase['connections_geometric'],'executed 0','cost',cost,'reserve',clearance['minimum_diagnostic_reserve_mm'])
if __name__=='__main__':main()
