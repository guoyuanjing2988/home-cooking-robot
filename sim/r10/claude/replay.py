"""Final independent replay and stronger1.5 arm-gravity stability audit.

Finite path prefixes from failed connections are never counted as execution.
All saved admitted endpoint candidates, successful internal strokes and park
are rechecked. Connection paths are audited by report only as prospective.
"""
import sys,time,hashlib
import numpy as np,mujoco
from scene import H,ROOT,load,save,build,targets
from checker import Checker,reference
def run(index):
 cfg=load('results/selected.json')['config'];record=load(f'results/strokes/{index}.json');t=record['target'];tree,meta=build(cfg,t['held']);ch=Checker(tree,meta)
 mass={'carrot':.12,'holder':.55,'catch_tray':.55,None:0}[t['held']]
 rows=[];seen=set();failures=[]
 def check(q,R,label,previous=None,line=False):
  key=tuple(np.round(q,12))
  if (key,label) in seen:return
  seen.add((key,label));ch.configure_target(t,R);r=ch.check(q,kind=t['kind'],mass=mass,force=t['force']);bound=ch.point_bound.segment_bound(previous,q) if previous is not None else 0.
  ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);sid=ch.m.site('R_prep').id;p=ch.d.site_xpos[sid].copy()
  a,b=np.array(t['points']);v=b-a;s=np.clip((p-a)@v/max(v@v,1e-12),0,1);pe,re=ch.pose_error(q,a+s*v,R)
  pose_ok=pe<=.005 and re<=np.deg2rad(3)
  row=dict(label=label,q=list(q),ok=bool(r['ok'] and bound<=.004+1e-10 and pose_ok),tip=r['stability'],clearance=r['clearance'],load=r['load'],point_bound_m=bound,position_mm=pe*1000,orientation_deg=float(np.degrees(re)),hits=r['hits'])
  rows.append(row)
  if not row['ok']:failures.append(row)
 for endpoint in [0,1]:
  bank=load(f'results/statics/{index}_{endpoint}.json')
  for row in bank['rows']:
   if row['status']!='ok':continue
   q=np.array(row['q']);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);actual=ch.d.site_xmat[ch.m.site('R_prep').id].reshape(3,3)
   approaches=t['approach'];jaws=([(0,0,1),(0,0,-1),(1,0,0),(-1,0,0)] if abs(approaches[1])>.9 else [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)])
   rotations=[reference.rotation(approaches,j) for j in jaws if abs(np.dot(j,approaches))<.9];R=min(rotations,key=lambda rr:np.linalg.norm(rr-actual))
   check(q,R,f'endpoint{endpoint}')
 internal=record['internal'];frozen=True
 if internal['ok']:
  qs=np.array(internal['path']);frozen=bool(np.max(abs(qs[:,:3]-qs[0,:3]))<1e-10)
  bank=load(f'results/statics/{index}_0.json');candidate=min(bank['candidates'],key=lambda c:np.linalg.norm(np.array(c['q'])-qs[0]));R=np.array(candidate['rotation'])
  assert np.linalg.norm(np.array(candidate['q'])-qs[0])<1e-9
  for j,q in enumerate(qs):check(q,R,'internal',qs[j-1] if j else None,True)
 save(f'results/replay/{index}.json',dict(index=index,all_pass=not failures and frozen,internal_pass=bool(internal['ok'] and not any(x['label']=='internal' for x in failures) and frozen),frozen_base=frozen,rows=rows,failures=failures,scope='admitted candidates/prospective local paths; zero connected meal execution'))
 print('replay',index,len(rows),'failures',len(failures),flush=True)
if __name__=='__main__':
 for index in map(int,sys.argv[1:]):run(index)
