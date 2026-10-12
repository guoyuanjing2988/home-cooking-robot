"""Complete independent conservative convex proof of the passing edge."""
from geometry import *

def enclosing_points(ch,g):
 v=points(ch,g)
 if v is not None:return v
 m,d=ch.m,ch.d;sz=m.geom_size[g];typ=int(m.geom_type[g])
 if typ==0:return None
 if typ==int(mujoco.mjtGeom.mjGEOM_SPHERE):extent=np.array([sz[0]]*3)
 elif typ==int(mujoco.mjtGeom.mjGEOM_CAPSULE):extent=np.array([sz[0],sz[0],sz[0]+sz[1]])
 elif typ==int(mujoco.mjtGeom.mjGEOM_CYLINDER):extent=np.array([sz[0],sz[0],sz[1]])
 elif typ==int(mujoco.mjtGeom.mjGEOM_ELLIPSOID):extent=sz.copy()
 else:raise ValueError((g,typ))
 # These boxes contain the ENTIRE analytic primitive, so a proved separation
 # of their swept hull is conservative for the original full-size shape.
 v=np.array(list(itertools.product([-1,1],repeat=3)))*extent
 return v@d.geom_xmat[g].reshape(3,3).T+d.geom_xpos[g]

def original_support(ch,g,n):
 m,d=ch.m,ch.d;rot=d.geom_xmat[g].reshape(3,3);v=rot.T@n;sz=m.geom_size[g];typ=int(m.geom_type[g])
 if typ in (int(mujoco.mjtGeom.mjGEOM_BOX),int(mujoco.mjtGeom.mjGEOM_MESH)):
  verts=points(ch,g);return verts[np.argmax(verts@n)]
 if typ==int(mujoco.mjtGeom.mjGEOM_SPHERE):local=sz[0]*v/max(np.linalg.norm(v),1e-30)
 elif typ==int(mujoco.mjtGeom.mjGEOM_CAPSULE):
  local=sz[0]*v/max(np.linalg.norm(v),1e-30);local[2]+=sz[1] if v[2]>=0 else -sz[1]
 elif typ==int(mujoco.mjtGeom.mjGEOM_CYLINDER):local=np.r_[sz[0]*v[:2]/max(np.linalg.norm(v[:2]),1e-30),sz[1] if v[2]>=0 else -sz[1]]
 elif typ==int(mujoco.mjtGeom.mjGEOM_ELLIPSOID):local=sz*sz*v/max(np.linalg.norm(sz*v),1e-30)
 else:raise ValueError(typ)
 return d.geom_xpos[g]+rot@local

def original_separating_plane(ch,a,b):
 # Zero unsigned distance of enclosing boxes cannot establish non-penetration.
 # Optimize only to discover a direction; evaluate the exact original support
 # plane independently. A positive projection is a geometric certificate.
 def gap(n):return float((original_support(ch,a,-n)-original_support(ch,b,n))@n)
 def jac(n):return -(original_support(ch,a,-n)-original_support(ch,b,n))
 centre=ch.d.geom_xpos[a]-ch.d.geom_xpos[b];centre/=max(np.linalg.norm(centre),1e-30)
 starts=[centre]+[v for v in np.r_[np.eye(3),-np.eye(3)]]
 best=(-1e9,None)
 for initial in starts:
  res=minimize(lambda n:-gap(n),initial,jac=jac,method='SLSQP',constraints=[dict(type='ineq',fun=lambda n:1-n@n,jac=lambda n:-2*n)],options=dict(ftol=1e-14,maxiter=200))
  n=res.x/max(np.linalg.norm(res.x),1e-30);value=gap(n)-1e-8
  if value>best[0]:best=(value,n.tolist())
  if best[0]>1e-7:break
 return dict(lower_m=best[0],direction=best[1],method='Independent exact-original-shape support projection; positive plane proves non-penetration')

def main():
 started=time.monotonic();ch,hands=mo.empty_cell();pr=json.loads((I/'results/passing.json').read_text());a=np.array(pr['q_start']);b=np.array(pr['q_end']);ch.d.qpos[:]=a;mujoco.mj_forward(ch.m,ch.d)
 oracle=Bounds(ch,f.required);motions=np.zeros(ch.m.ngeom);vs={g:enclosing_points(ch,g) for g in range(ch.m.ngeom)}
 for g in range(ch.m.ngeom):
  body=int(ch.m.geom_bodyid[g]);anc=[]
  while body:anc.append(body);body=int(ch.m.body_parentid[body])
  for side in s.model.SIDES:
   if ch.m.body(side+'_carriage').id in anc:motions[g]=b[ch.qa[side+'_carriage_x']]-a[ch.qa[side+'_carriage_x']]
 broad=0;planes=0;narrow=[];failed=[];mins={}
 for u,v,need,cat in oracle.pairs:
  va,vb=vs[u],vs[v];dx=motions[u]-motions[v]
  if va is None or vb is None:
   plane=u if va is None else v;other=v if va is None else u;n=ch.d.geom_xmat[plane].reshape(3,3)[:,2];p=ch.d.geom_xpos[plane]
   lower=float(np.min((vs[other]-p)@n))+min(0.,float(n[0]*(motions[other]-motions[plane])));planes+=1
  else:
   if dx:va=np.vstack([va,va+[dx,0,0]])
   lower=float(np.linalg.norm(np.maximum(np.maximum(va.min(0)-vb.max(0),vb.min(0)-va.max(0)),0)))
   if lower>=need+1e-7:broad+=1
   else:
    proof=qp(va,vb);lower=proof['lower_m']
    if need==0 and lower<=1e-7:
     assert dx==0,'Self shape changes along this route'
     exact=original_separating_plane(ch,u,v);lower=exact['lower_m'];proof['original_shape_certificate']=exact
    narrow.append(dict(pair=[ch.gnames[u],ch.gnames[v]],required_mm=need*1000,**proof))
  if lower<need-1e-6 or (need==0 and lower<=0):failed.append(dict(pair=[ch.gnames[u],ch.gnames[v]],lower_mm=lower*1000,required_mm=need*1000))
  if cat not in mins or lower<mins[cat]['lower_mm']/1000:mins[cat]=dict(pair=[ch.gnames[u],ch.gnames[v]],lower_mm=lower*1000,required_mm=need*1000)
 out=dict(pass_=not failed,eligible_pairs=len(oracle.pairs),independent_AABB_pairs=broad,analytic_plane_pairs=planes,independent_QP_pairs=narrow,unresolved=failed,minima=mins,method='Every eligible pair: exact original box/mesh vertices or enclosing full analytic-primitive boxes, independent swept-relative-translation convex hull, independent half-space QP and projection lower bound. Planes use exact support of conservative enclosing primitive. Shared arm angles remain constant. No sparse-sample or submitted GJK distance used for acceptance.',elapsed_s=time.monotonic()-started)
 dump('passing_complete_independent.json',out);print('complete passing',out['pass_'],len(failed),'unresolved',len(narrow),'QP')
if __name__=='__main__':main()
