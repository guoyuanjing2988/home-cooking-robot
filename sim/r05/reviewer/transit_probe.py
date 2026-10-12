"""Independent analytic separating-plane checks of the late margin filter."""
import json,numpy as np,mujoco
import motion_audit as a
from scipy.optimize import least_squares
H=a.H;I=a.I;O=H/'results';raw=json.loads((I/'results/motion_internal_grasp_rejected_6_7.json').read_text())['records'][0];ph,_,_=a.mo.items[6];sg=raw['segment_override'];ch=a.mo.scene(ph,sg,6);edge=raw['edges'][-1];mid=np.array(edge['lift_failures'][0]['blocker']['q']);ch.d.qpos[:]=mid;mujoco.mj_forward(ch.m,ch.d);sid=ch.m.site('L_prep').id;p=ch.d.site_xpos[sid].copy();rt=ch.d.site_xmat[sid].reshape(3,3).copy();h=sg['poses'][-1];rows=[]
ix=[ch.qa[n] for n in a.f.s.ck.ARMS['L']];limits=np.array([ch.m.jnt_range[ch.jid[n]] for n in a.f.s.ck.ARMS['L']]).T
from scipy.spatial.transform import Rotation
for mm,window in [(24,False),(24,True),(25,False),(26,False)]:
 q=mid.copy();target=p+[0,0,(mm-25)/1000]
 def res(x):
  q[ix]=x;ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d);return np.r_[(ch.d.site_xpos[sid]-target)*10,Rotation.from_matrix(rt.T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec()]
 sol=least_squares(res,q[ix],bounds=limits,xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=150);q[ix]=sol.x;ch.contact_windows=edge['contact_windows'] if window else [];hits,_,_,ds=a.state(ch,q,h);g=ch.gnames.index('L_held_food');end=ch.gnames.index('peel_endstop-1')
 # A box's exact lowest point: zcentre - sum_i |R_zi| halfsize_i.
 r=ch.d.geom_xmat[g].reshape(3,3);bottom=ch.d.geom_xpos[g,2]-abs(r[2])@ch.m.geom_size[g];top=ch.d.geom_xpos[end,2]+ch.m.geom_size[end,2];gap=bottom-top
 rows.append(dict(lift_mm=mm,window=window,accepted=not hits,analytic_vertical_lower_gap_mm=float(gap*1000),IK_residual=float(np.linalg.norm(sol.fun)),positive_margin_discrepancies=ds,rejections=hits[:4]))
(O/'transit_probe.json').write_text(json.dumps(dict(rows=rows,pass_=([r['accepted'] for r in rows]==[False,True,True,True]),policy='An independently derived exact box vertical separating plane establishes ordinary5mm/6mm clearance.4mm remains forbidden without its own validated window. Final poses use unchanged reference replay.'),indent=2));print('TRANSIT_PROBE',[(r['lift_mm'],r['window'],r['accepted'],r['analytic_vertical_lower_gap_mm']) for r in rows])
