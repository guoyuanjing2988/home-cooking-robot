from v6_common import *
from planner_r05 import Planner
data=read('idle.json');ch=v.scene(58);ch.xml=(I/data['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False;pl=Planner(ch,{},seconds=65);rows=[]
for r in data['alternative_fold_goals']['attempts']:
 rec=json.loads((I/r['candidate_file']).read_text());q=np.array(rec['q']);valid=pl.state(q,{});rows.append(dict(file=r['candidate_file'],snapshot_pass=valid,blocker=pl.last))
dump('alternative_parks.json',dict(rows=rows,passing=sum(r['snapshot_pass'] for r in rows)))
# Find the submitted tightest robot/environment internal route separately from held/support departures.
rank=[]
for r in read('motion.json')['internal_paths']:
 if r['ok']:rank.append(dict(index=r['index'],reserve=r['final_replay']['clearance_distribution'].get('robot_environment',{}).get('min_mm',1e9)))
dump('robot_tight_rank.json',dict(tightest=min(rank,key=lambda x:x['reserve'])))
print('ALTERNATIVES',len(rows),sum(r['snapshot_pass'] for r in rows),'tight_robot',min(rank,key=lambda x:x['reserve']))
