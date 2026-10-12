import json,xml.etree.ElementTree as E
import numpy as np,mujoco
import r07_runtime as rt
from distance import Bounds
H=rt.H;O=rt.O
p=json.loads((O/'park_full.json').read_text());c=dict(p['config']);c.pop('transport_only',None)
tr,meta=rt.s.model.build(c);xml=E.tostring(tr.getroot(),encoding='unicode');m=mujoco.MjModel.from_xml_string(xml)
ch=object.__new__(rt.s.ck.Checker);ch.desc=rt.s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(m);ch.allowed=[]
q=np.array(p['q']);ch.d.qpos[:]=q;mujoco.mj_forward(m,ch.d)
hits,mins,audit=rt.f.contacts(ch,q);b=ch.bounds
rows=[]
for g,n in enumerate(ch.gnames):
 if not ch.robot[g]:continue
 lo=np.array([b.support(g,-v)[k] for k,v in enumerate(np.eye(3))]);hi=np.array([b.support(g,v)[k] for k,v in enumerate(np.eye(3))])
 rows.append(dict(name=n,lo=lo.tolist(),hi=hi.tolist(),band=bool(lo[1]>=.24-1e-6 and (hi[1]<=.59+1e-6 or n.startswith('r07_wall_bracket_')) and lo[2]>=.86-1e-6 and hi[2]<=1.34+1e-6)))
rt.write('snapshot_diagnostic.json',dict(config=c,q=q.tolist(),hits=hits,min_clearance=mins,robot_bounds=rows,all_in_band=all(r['band'] for r in rows),collision_pass=not hits))
(H/'models/r07_snapshot.xml').write_text(xml)
print('snapshot hits',len(hits),'band',all(r['band'] for r in rows),'first',hits[:12],flush=True)
