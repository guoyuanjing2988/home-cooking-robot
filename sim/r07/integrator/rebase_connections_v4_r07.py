"""Replay a complete downstream local path on a continuous periodic joint branch.

This can certify a two-template local bundle, never a persistent meal event.
Original static and internal records remain immutable.
"""
import os,sys,json,copy,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np
import runtime_v4_r07 as v
from motion_v4_r07 import replay
out=v.O/'motion_v4'/v.ID
for file in sorted(out.glob('connection_*.json')):
 row=json.loads(file.read_text())
 if not row.get('geometric_path_pass') or row.get('pass_'):continue
 nxt=json.loads((v.H/row['source_paths'][1]).read_text());delta=np.array(row['endpoint_periodic_delta_rad']);ch=v.scene(nxt['index']);edges=copy.deepcopy(nxt['edges']);w=copy.deepcopy(nxt['endpoint_witness'])
 for edge in edges:edge['path']=[(np.array(q)+delta).tolist() for q in edge['path']]
 for pose in w['poses']:pose['q']=(np.array(pose['q'])+delta).tolist()
 range_ok=all(not ch.m.jnt_limited[ch.jid[n]] or ch.m.jnt_range[ch.jid[n],0]-1e-8<=q[ix]<=ch.m.jnt_range[ch.jid[n],1]+1e-8 for edge in edges for q in edge['path'] for n,ix in ch.qa.items())
 joined=bool(edges and np.max(abs(np.array(row['planner']['path'][-1])-np.array(edges[0]['path'][0])))<1e-9)
 record=dict(layout=v.ID,from_index=row['from_index'],to_index=row['to_index'],source_path=row['source_paths'][1],source_sha256=row['source_sha256'][1],periodic_delta_rad=delta.tolist(),range_pass=range_ok,joined=joined,pass_=False,persistent_meal_pass=False,scope='Same-attachment two-template local bundle only. Original path is preserved; all downstream vertices are rebased together and every <=4mm sample is replayed with original contacts and loads.')
 if range_ok and joined:
  ch.witness_k=w['k'];ch.refine_support_endpoints=True
  result=replay(ch,v.items[nxt['index']][1],w,edges);record.update(pass_=result['pass_'],final_replay=result,edges=edges,endpoint_witness=w)
 path=out/f'rebased_bundle_{row["index"]}.json';path.write_text(json.dumps(record,indent=2,allow_nan=False));row.update(rebased_downstream_bundle=str(path.relative_to(v.H)),rebased_downstream_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rebased_joint_continuity=bool(record['pass_']),pass_=bool(record['pass_']))
 file.write_text(json.dumps(row,indent=2,allow_nan=False));print('REBASED_LOCAL_BUNDLE',row['index'],record['pass_'],flush=True)
