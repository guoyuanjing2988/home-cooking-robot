"""Actual joint proposals for expanded wash rolls; no geometry relabeling."""
import os,sys,json,hashlib,time,copy
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np
from scipy.spatial.transform import Rotation
import persistent_v6_r07 as p
from motion_v6_r07 import continuation_ik
v=p.v;H=v.H;O=v.O;ID=v.ID;start=time.monotonic();out=O/'meal_pose_proposals_v6';out.mkdir(exist_ok=True);file=out/(ID+'.json');records={}
for r in p.expanded():
 i=r['index'];ch=v.scene(i);sg=v.items[i][1];saved_path=O/'static_v6'/ID/f'{i}.json';d=json.loads(saved_path.read_text());w=d.get('witness') or (d.get('best_failed') or {}).get('raw');ends=[]
 for last in (False,True):
  h=copy.deepcopy(sg['poses'][-1 if last else 0]['R']);h['roll_deg']+=r['roll_deg'];k=w.get('k',0) if w else 0;q=np.array(w['poses'][-1 if last else 0]['q']) if w and w.get('poses') else ch.m.qpos0.copy();q0=q.copy();target=ch.target_rotation(h,k)
  if r['roll_deg']:q,exact=continuation_ik(ch,q,{'R':(np.array(h['pos']),target)})
  else:exact=None
  actual=p.fk(ch,q);pe=float(np.linalg.norm(actual[:3,3]-h['pos'])*1000);oe=float(np.degrees(Rotation.from_matrix(target.T@actual[:3,:3]).magnitude()))
  ends.append(dict(q=q.tolist(),k=k,roll_deg=r['roll_deg'],position_mm=pe,orientation_deg=oe,pose_pass=pe<=5 and oe<=3,exact_roll_IK=None if exact is None else bool(exact),source_static=str(saved_path.relative_to(H)),source_sha256=hashlib.sha256(saved_path.read_bytes()).hexdigest(),source_completed96=d.get('complete',False),source_admitted_template=bool(d.get('witness')) and d.get('complete',False),rolled_internal_path_checked=False if r['roll_deg'] else None))
 records[r['id']]=ends
 file.write_text(json.dumps(dict(layout=ID,complete=len(records)==len(p.expanded()),records=records,scope='Joint-space proposals for every actual repeated stroke endpoint. Full world connection planner still decides gaps/loads. Nonzero roll changes wrist q; no food-coordinate relabeling. Rolled internal strokes are not claimed executed.'),indent=2))
 if time.monotonic()-start>1000:break
print('EXPANDED_POSE_PROPOSALS',len(records),'/',len(p.expanded()),'seconds',round(time.monotonic()-start,2))
