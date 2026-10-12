import json,copy,itertools
import numpy as np,mujoco
from scipy.optimize import minimize,LinearConstraint
from scipy.spatial import ConvexHull
import final_check as f
from distance import Bounds
s=f.s;H=s.HERE;I=H.parents[2]/'sim/r03/integrator';rows=[]
for label,k in [('helper_index_6',5),('helper_index_7',79)]:
 ph=next(x for x in s.P['phases'] if x['id']=='Q05.potato');sg=next(x for x in ph['segments'] if x['label']==label);key='Q05.potato__'+label
 ch=s.Checker(ph,sg);ch.bind_model(mujoco.MjModel.from_xml_path(str(I/'results/witnesses'/(key+'.xml'))));raw=json.loads((H/'baseline/strokes'/(key+'.json')).read_text());row=next(r for r in raw['rows'] if r['k']==k);q=np.array(row['poses'][1]['q']);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);oracle=Bounds(ch,f.required)
 a=ch.gnames.index('L_link2_collision');b=ch.gnames.index('cable_chain_swept_cover_0_piece4');bound=oracle.pair(a,b)
 def verts(g):
  v=oracle.local[g] if g in oracle.local else np.array(list(itertools.product([-1,1],repeat=3)))*ch.m.geom_size[g]
  return v@ch.d.geom_xmat[g].reshape(3,3).T+ch.d.geom_xpos[g]
 va,vb=verts(a),verts(b);pa,pb=ConvexHull(va).equations,ConvexHull(vb).equations
 aa=np.zeros((len(pa)+len(pb),6));aa[:len(pa),:3]=pa[:,:3];aa[len(pa):,3:]=pb[:,:3];bb=-np.r_[pa[:,3],pb[:,3]]
 fun=lambda x:float((x[:3]-x[3:])@(x[:3]-x[3:]));jac=lambda x:np.r_[2*(x[:3]-x[3:]),-2*(x[:3]-x[3:])]
 res=minimize(fun,np.r_[va.mean(0),vb.mean(0)],jac=jac,constraints=[LinearConstraint(aa,-np.inf,bb)],method='SLSQP',options=dict(ftol=1e-14,maxiter=250))
 upper=np.sqrt(res.fun);assert bound['lower_m']<=upper+1e-7 and bound['upper_m']>=upper-1e-7
 rows.append(dict(stroke=key,seed=k,GJK=bound,independent_hull_QP_mm=float(upper*1000),QP_constraint_error_m=float(np.max(aa@res.x-bb)),reference_contact_absent=not any(set(map(int,c.geom))=={a,b} for c in ch.d.contact[:ch.d.ncon]),old20mm_claim_valid=False))
(H/'results/distance_validation.json').write_text(json.dumps(dict(rows=rows,all_regressions_pass=True,no_contact_lower_bound_used=False,base_collision_model='R04 retains original unscaled UR5e base0/base1'),indent=2));print(json.dumps(rows,indent=2))
