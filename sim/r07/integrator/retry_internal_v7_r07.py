"""One alternate clearance/staging attempt for a failed admitted template path."""
import os,sys,json,copy,hashlib,time,types
from pathlib import Path
import numpy as np
ID=sys.argv[1];index=int(sys.argv[2]);os.environ['R07_LAYOUT']=ID;H=Path(__file__).resolve().parent;O=H/'results';file=O/'motion_v7'/ID/f'internal_{index}.json';old=json.loads(file.read_text());source=O/'static_v7'/ID/f'{index}.json';saved=json.loads(source.read_text());assert saved['witness'] and saved['complete'] and not old['ok']
if old.get('retry_policy'):print('RETRY_ALREADY_RECORDED',index);raise SystemExit(0)
history=H/'history/v7_path_retries';history.mkdir(exist_ok=True);prior=history/f'{ID}_internal_{index}.json'
assert not prior.exists() or prior.read_bytes()==file.read_bytes()
if not prior.exists():prior.write_bytes(file.read_bytes())
code=(H/'motion_v7_r07.py').read_text(encoding='utf-8-sig').replace('from least_analytic_v4_r07 import solve as avoid','from least_analytic_v7_r07 import solve as avoid').replace('ch.lock_initial_carriage=False;candidate,errors,hh,_=avoid','ch.lock_initial_carriage=False;ch.night_robust=True;candidate,errors,hh,_=avoid')
module=types.ModuleType('robust_motion_retry_v7');module.__file__=str(H/'motion_v7_r07.py');exec(compile(code,module.__file__,'exec'),module.__dict__)
v=module.v;mo=module.mo;w=saved['witness'];ph,sg,key=v.items[index];ch=v.scene(index);ch.witness_k=w['k'];ch.refine_support_endpoints=True;edges=[];stage=np.array(w['poses'][0]['q']);stage_source='current start';best=-1e9
if sg['action']!='process':
 probe=module.Planner(ch,sg['poses'][0],seconds=65)
 for candidate_file in (O/'static_v7'/ID).glob('*.json'):
  cw=json.loads(candidate_file.read_text()).get('witness')
  if not cw:continue
  for j,pose in enumerate(cw['poses']):
   q=np.array(pose['q']);q[ch.qa['R_jaw_minus']]=stage[ch.qa['R_jaw_minus']];q[ch.qa['R_jaw_plus']]=stage[ch.qa['R_jaw_plus']]
   if not probe.state(q,sg['poses'][0]):continue
   sid=ch.m.site('R_prep').id;pos=ch.d.site_xpos[sid].copy();score=float(pos[2]-2*max(pos[1]-.20,0))
   if score>best:stage=q.copy();best=score;stage_source=f'{candidate_file.name}:pose{j}'
v.s.PARK=stage.copy()
for j in range(len(w['poses'])-1):
 a=np.array(edges[-1]['path'][-1]) if edges and edges[-1]['ok'] else np.array(w['poses'][j]['q']);b=mo.shortq(ch,a,w['poses'][j+1]['q']);ch.refine_start_allowed=j==0
 edge=mo.plan_section(ch,a,b,sg['poses'][j],sg['poses'][j+1],989000+index*10+j,process=sg['action']=='process');edge['working_ik_diagnostics']=getattr(ch,'working_ik_diagnostics',[]);edges.append(edge);print('RETRY_EDGE',index,j,edge['ok'],flush=True)
final=module.replay(ch,sg,w,edges);row=dict(index=index,stroke=key,layout=ID,ok=final['pass_'],edges=edges,final_replay=final,meal_state_verified=False,jaw_axis_branch=w['k'],endpoint_witness=w,source_static_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),retry_policy=dict(prior_result=str(prior.relative_to(H)),prior_pass=old['ok'],stage_source=stage_source,stage_q=stage.tolist(),per_edge_budget_s=65,reason='Collision-aware continuation seeks10mm extra; nonworking staging uses full-scene-clear existing configurations. Different deterministic restart seeds; all original poses, geometry, forces, windows and final gates retained.'))
file.write_text(json.dumps(row,indent=None,allow_nan=False));print('RETRY_INTERNAL',index,row['ok'],flush=True)
