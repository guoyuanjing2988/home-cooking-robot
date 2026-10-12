"""Consolidate bounded attempts without promoting snapshots to a meal."""
import json,csv,copy,time,sys,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';p=json.loads((O/'process_v3.json').read_text());sequence=json.loads((O/'state_sequence.json').read_text());items=[(ph,sg,ph['id']+'__'+sg['label'].replace(' ','_')) for ph in p['phases'] for sg in ph['segments']];internal={};connections={};attempts=[]
for path in sorted(list(O.glob('motion_internal_*.json'))+list(O.glob('motion_connection_*.json')),key=lambda x:x.stat().st_mtime):
 for r in json.loads(path.read_text())['records']:
  r['source_file']=str(path.relative_to(H));attempts.append(r);(internal if r['kind']=='internal' else connections)[r['index']]=r
for path in O.glob('history_internal_*.json'):
 for r in json.loads(path.read_text())['records']:r['source_file']=str(path.relative_to(H));attempts.append(r)
for i,(ph,sg,key) in enumerate(items):
 if i not in internal:internal[i]=dict(kind='internal',index=i,stroke=key,ok=False,reason='Required stroke has no completed planning chunk',edges=[],status='NO_COMPLETE_ATTEMPT')
for i in range(len(items)-1):
 if i not in connections:connections[i]=dict(kind='connection',index=i,from_stroke=items[i][2],to_stroke=items[i+1][2],ok=False,reason='Required connection has no completed planning chunk',status='NO_COMPLETE_ATTEMPT')
fresh={}
for path in sorted(O.glob('path_replay_*.json'),key=lambda x:x.stat().st_mtime):
 for row in json.loads(path.read_text())['rows']:fresh[row['index']]=dict(row,source_file=str(path.relative_to(H)))
for i,r in internal.items():
 r['solver_geometry_ok']=r['ok'];r['final_path_replay']=fresh.get(i)
 if r['ok'] and fresh:
  digest=hashlib.sha256(json.dumps([x['path'] for x in r['edges']],sort_keys=True).encode()).hexdigest()
  r['ok']=i in fresh and fresh[i]['pass_'] and fresh[i]['path_sha256']==digest;r['status']='PASS_ISOLATED_GEOMETRY_AND_LOAD_REPLAY' if r['ok'] else 'FAIL_FRESH_REPLAY' if i in fresh else 'PENDING_FRESH_REPLAY'
connection_fresh={}
if (O/'connection_replay.json').exists():
 for row in json.loads((O/'connection_replay.json').read_text())['rows']:connection_fresh[row['index']]=row
for i,r in connections.items():
 r['solver_geometry_ok']=r['ok'];r['final_path_replay']=connection_fresh.get(i)
 if r['ok'] and connection_fresh:
  digest=hashlib.sha256(json.dumps(r['planner']['path'],sort_keys=True).encode()).hexdigest();r['ok']=i in connection_fresh and connection_fresh[i]['pass_'] and connection_fresh[i]['path_sha256']==digest
jaws={}
for path in sorted(O.glob('jaw_events_*.json'),key=lambda x:x.stat().st_mtime):
 for row in json.loads(path.read_text())['rows']:jaws[row['event']]=dict(row,source_file=str(path.relative_to(H)))
event_failures=[]
for e in sequence['events']:
 if not e.get('motion_required'):continue
 probe=jaws.get(e['id']);blockers=[dict(type='state_model',pair=None,reason='Persistent-body source/destination transforms and actuator grasp/attachment are not bound to a conserved-scene approach, handoff and departure')]
 if probe and probe.get('probe',{}).get('blocker'):blockers.extend(probe['probe']['blocker']['blockers'])
 event_failures.append(dict(id=e['id'],phase=e['phase'],name=e['name'],stage=e.get('stage'),status='FAIL_PERSISTENT_SCENE_BINDING',ok=False,planner_time_s=0,path_length=None,blockers=blockers,jaw_geometry_probe=probe,state_before=e.get('state_before'),state_after=e.get('state_after'),tried='Full-size slide-joint jaw travel at the registered template endpoint, <=4mm point grid; globally conserved approach/departure remains missing' if probe else 'Enumerated explicit state transition, full conserved source geometry and inherited template motions; no executable actuator or handoff binding was obtained'))
expanded=[];lookup={(r['from_stroke'],r['to_stroke']):r for r in connections.values()}
for link in sequence['expanded_connections']:
 r=lookup.get((link['from_template'],link['to_template']));planner=r.get('planner',{}) if r else {};known=r.get('planner',{}).get('blockers',[]) if r else []
 expanded.append(dict(link,status='FAIL',ok=False,template_geometry_ok=r.get('ok',False) if r else False,planner_time_s=planner.get('planner_time_s',0),allocated_budget_s=planner.get('allocated_budget_s'),path_length=planner.get('path_length_scaled'),blockers=known+[dict(type='state_model',pair=None,reason='Recipe-expanded persistent scene and intervening event trajectories are unbound')],model_blocker='Recipe-expanded persistent scene and intervening events are unverified',tried='Both-arm/carriage canonical65s RRT restarts,straight support windows,warm goal IK and shortcuts; expanded ownership ledger checked but physical handoff remains unbound' if r else 'Recipe repeat and single-owner ledger checked; no conserved actor/attachment path was obtained, so no geometric RRT search or invented collision pair is claimed',template_attempt_source=r.get('source_file') if r else None))
rows=[internal[i] for i in sorted(internal)];links=[connections[i] for i in sorted(connections)];edges=[e for r in rows for e in r.get('edges',[])];geometric_pass=sum(r['ok'] for r in rows)
motion=dict(schema='r05.full-meal-motion.v1',pass_=False,status='FAIL',internal=rows,between_strokes=links,expanded_connections=expanded,event_paths=event_failures,template_internal_passed=geometric_pass,template_internal_total=len(rows),template_internal_preliminary_passed=sum(r.get('solver_geometry_ok',False) for r in rows),template_connections_geometric_passed=sum(r['ok'] for r in links),template_connections_total=len(links),internal_passed=geometric_pass,internal_total=len(rows)+len(event_failures),connections_passed=0,connections_total=len(expanded),required_event_paths_passed=0,required_event_paths_total=len(event_failures),states_checked=sum(e.get('states_checked',0) for r in attempts for e in (r.get('edges',[]) if r['kind']=='internal' else [r.get('planner',{})])),planner_seconds=sum(e.get('planner_time_s',0) for r in attempts for e in (r.get('edges',[]) if r['kind']=='internal' else [r.get('planner',{})])),seeds_tried=sum(e.get('seeds_tried',0) for r in attempts for e in (r.get('edges',[]) if r['kind']=='internal' else [r.get('planner',{})])),solutions_found=sum(e.get('solutions_found',0) for r in attempts for e in (r.get('edges',[]) if r['kind']=='internal' else [r.get('planner',{})])),verified_geometric_witnesses=sum(e.get('verified_witnesses',0) for r in rows if r['ok'] for e in r.get('edges',[])),final_replay_states=sum(r['states_checked'] for r in fresh.values()),jaw_geometry_probes=len(jaws),jaw_geometry_passed=sum(r.get('probe',{}).get('pass_',False) for r in jaws.values()),path_check='Model-derived maximum robot/held point displacement <=4mm on every accepted joint segment. Search-only proposals may use20mm, then full4mm replay; proposals failing replay are not accepted.',contact_policy='Only named held part/support faces on validated straight <=50mm normal/insertion-axis windows until5mm; named food/tool working faces along required working strokes; only named rail-bracket rear mating faces touch wall.',scope='Internal numerator includes individually checked template geometries; denominator additionally includes explicit required event paths. Some event windows duplicate portions of template strokes, so this is a requirements-obligation count, not a disjoint trajectory-edge count. No persistent-meal connection or finished product is executed. Partial geometric successes do not prove a meal.',uncompleted_chunks=[r['index'] for r in rows if r.get('status')=='NO_COMPLETE_ATTEMPT'],uncompleted_template_connections=[r['index'] for r in links if r.get('status')=='NO_COMPLETE_ATTEMPT'])
motion['endpoint_ik_starts_total']=sum(len(r.get('source_ik_attempts',[]))+len(r.get('goal_ik_attempts',[])) for r in attempts)
motion['endpoint_ik_reference_solutions_total']=sum(sum(bool(x.get('reference',{}).get('ok')) for x in r.get('source_ik_attempts',[]))+sum(bool(x.get('verified')) for x in r.get('goal_ik_attempts',[])) for r in attempts)
(O/'motion.json').write_text(json.dumps(motion,indent=2))
iterations=[]
for r in attempts:
 for j,e in enumerate((r.get('edges',[]) or [{}]) if r['kind']=='internal' else [r.get('planner',{})]):
  iterations.append(dict(kind=r['kind'] if e else 'source_endpoint_ik',index=r['index'],edge=j,source=r['source_file'],pass_=e.get('ok',False),planner_s=round(e.get('planner_time_s',0),3),budget_s=e.get('allocated_budget_s',0),seeds=e.get('seeds_tried',len(r.get('source_ik_attempts',[]))),states=e.get('states_checked',len(r.get('source_ik_attempts',[]))),path_length=e.get('path_length_scaled'),blocker='; '.join(' / '.join(b['pair']) for b in e.get('blockers',[])[:2]) or r.get('reason') or ''))
with (O/'iterations.csv').open('w',newline='',encoding='utf-8') as fp:
 w=csv.DictWriter(fp,fieldnames=list(iterations[0]) if iterations else ['kind']);w.writeheader();w.writerows(iterations)
(O/'cheapest.json').write_text(json.dumps(dict(configuration=None,cost_cny=None,reason='No variant passes connected meal and idle deployment. Cheaper R04 variants remain unqualified; no loss of forces or product requirements is permitted.'),indent=2))
print('TEMPLATES internal',geometric_pass,'/',len(rows),'links',motion['template_connections_geometric_passed'],'/',len(links),'full connections0/',len(expanded),'explicit event failures',len(event_failures),'remaining',len(motion['uncompleted_chunks']),len(motion['uncompleted_template_connections']))
