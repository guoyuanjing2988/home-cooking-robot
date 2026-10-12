from v5_common import *
import hashlib
rank=[]
for saved in read('motion.json')['internal_paths']:
 if not saved['ok']:continue
 ch=v.scene(saved['index']);ib=IndependentBound(ch);arc=sum(ib.segment(np.array(a),np.array(b)) for e in saved['edges'] for a,b in zip(e['path'],e['path'][1:]));mins=saved['final_replay']['clearance_distribution'];rank.append(dict(index=saved['index'],point_arc_bound_m=arc,minimum_submitted_reserve_mm=min(x['min_mm'] for k,x in mins.items() if k!='self')))
connections=[]
for file in sorted((I/'results/connections_v5'/v.ID).glob('*.json'),key=lambda p:int(p.stem)):
 r=json.loads(file.read_text())
 for l in r['legs']:
  if not l['planner'].get('path'):continue
  ch=v.scene(r['from_stroke']['index']);ch.xml=(I/l['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ib=IndependentBound(ch);path=l['planner']['path'];arc=sum(ib.segment(np.array(a),np.array(b)) for a,b in zip(path,path[1:]));connections.append(dict(connection=r['connection'],leg=l['name'],point_arc_bound_m=arc,states_submitted=l['replay']['states_checked']))
dump('rank.json',dict(internals=rank,connections=connections,longest_internal=max(rank,key=lambda x:x['point_arc_bound_m']),tightest_submitted_internal=min(rank,key=lambda x:x['minimum_submitted_reserve_mm']),longest_saved_connection=max(connections,key=lambda x:x['point_arc_bound_m'])))
print('RANK',max(rank,key=lambda x:x['point_arc_bound_m']),max(connections,key=lambda x:x['point_arc_bound_m']),flush=True)
