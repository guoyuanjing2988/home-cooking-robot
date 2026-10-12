"""Explain the final own-support rejection without changing any geometry/rule."""
import json,numpy as np,mujoco
import motion_r05 as mo,final_check as f,policy_r05 as po
from distance import Bounds
O=f.s.HERE/'results';r=json.loads((O/'motion_internal_grasp_rejected_6_7.json').read_text())['records'][0];ph,sg,_=mo.items[r['index']];ch=mo.scene(ph,r['segment_override'],r['index']);e=r['edges'][-1];q=np.array(e['lift_failures'][0]['blocker']['q']);ch.contact_windows=e['contact_windows'];ch.set_contacts(r['segment_override']['poses'][-1]);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);ch.bounds=Bounds(ch,f.required);rows=[]
for w in ch.contact_windows:
 a=ch.gnames.index(w['face']);side=w['side'];sid=ch.m.site(side+'_prep').id;dp=ch.d.site_xpos[sid]-w['tcp_origin_m'];normal=np.array(w['normal']);cs=[]
 for part in w['held_parts']:
  b=ch.gnames.index(side+'_held_'+part)
  for c in ch.d.contact[:ch.d.ncon]:
   if set(map(int,c.geom))!={a,b}:continue
   p=ch.d.geom_xmat[a].reshape(3,3).T@(c.pos-ch.d.geom_xpos[a]);cs.append(dict(dist_mm=float(c.dist*1000),face_local_contact_m=p.tolist(),face_half_size_m=ch.m.geom_size[a].tolist(),face_test=f.intentional(ch,c),boundary_test=po.named_face_boundary(ch,w,c)))
 a=ch.gnames.index(w['face']);b=ch.gnames.index(w['side']+'_held_'+w['held_parts'][0])
 rows.append(dict(face=w['face'],valid_window=po.valid_window(ch,w),axial_mm=float(dp@normal*1000),lateral_mm=float(np.linalg.norm(dp-(dp@normal)*normal)*1000),contacts=cs,exact_pair=ch.bounds.pair(a,b),geom_position_m=[ch.d.geom_xpos[a].tolist(),ch.d.geom_xpos[b].tolist()],geom_matrix=[ch.d.geom_xmat[a].tolist(),ch.d.geom_xmat[b].tolist()]))
out=dict(stroke=r['stroke'],q=q.tolist(),rows=rows,allowed_pairs=[list(x) for x in po.window_pairs(ch)]);(O/'support_return_diagnostic.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)));print(json.dumps(out,indent=2,default=str)[:6000])
