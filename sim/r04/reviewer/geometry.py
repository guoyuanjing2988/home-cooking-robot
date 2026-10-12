"""Independent convex half-space QP and support-plane cross-checks."""
from reverify import *
from scipy.spatial import ConvexHull
from scipy.optimize import minimize
from distance import Bounds
import motion_check as mo

def points(ch,g):
 m,d=ch.m,ch.d;typ=int(m.geom_type[g]);sz=m.geom_size[g]
 if typ==int(mujoco.mjtGeom.mjGEOM_MESH):
  mid=m.geom_dataid[g];adr=m.mesh_vertadr[mid];v=m.mesh_vert[adr:adr+m.mesh_vertnum[mid]].astype(float);v=v[ConvexHull(v).vertices]
 elif typ==int(mujoco.mjtGeom.mjGEOM_BOX):v=np.array(list(itertools.product([-1,1],repeat=3)))*sz
 else:return None
 return v@d.geom_xmat[g].reshape(3,3).T+d.geom_xpos[g]

def qp(va,vb):
 origin=(va.mean(axis=0)+vb.mean(axis=0))/2;va=va-origin;vb=vb-origin
 aa=ConvexHull(va).equations;bb=ConvexHull(vb).equations
 mat=np.zeros((len(aa)+len(bb),6));mat[:len(aa),:3]=aa[:,:3];mat[len(aa):,3:]=bb[:,:3];off=np.r_[aa[:,3],bb[:,3]]
 def obj(x):v=x[:3]-x[3:];return .5*(v@v)
 def jac(x):v=x[:3]-x[3:];return np.r_[v,-v]
 res=minimize(obj,np.r_[va.mean(axis=0),vb.mean(axis=0)],jac=jac,method='SLSQP',constraints=[dict(type='ineq',fun=lambda x:-(mat@x+off),jac=lambda x:-mat)],options=dict(ftol=1e-14,maxiter=200))
 diff=res.x[:3]-res.x[3:];upper=float(np.linalg.norm(diff));n=diff/max(upper,1e-30)
 lower=max(0.,float(np.min(va@n)-np.max(vb@n)))-1e-8
 return dict(lower_m=max(0.,lower),upper_m=upper,max_constraint_error_m=float(max(mat@res.x+off)),success=bool(res.success),iterations=res.nit,method='Independent six-variable half-space convex QP; independent vertex projection lower bound')

def audit_motion_bounds(ch):
 m=ch.m;result=[]
 # Triangle inequality over all local serial offsets and original geometry
 # radii proves the all-angle maximum distance from every hinge axis.
 for j in range(m.njnt):
  if m.jnt_type[j]!=mujoco.mjtJoint.mjJNT_HINGE:continue
  jb=int(m.jnt_bodyid[j]);maximum=0.;which=None
  for g in range(m.ngeom):
   body=int(m.geom_bodyid[g]);dist=np.linalg.norm(m.geom_pos[g])+m.geom_rbound[g]
   while body and body!=jb:
    dist+=np.linalg.norm(m.body_pos[body]);body=int(m.body_parentid[body])
   if body!=jb:continue
   dist+=np.linalg.norm(m.jnt_pos[j])
   if dist>maximum:maximum=float(dist);which=ch.gnames[g]
  result.append(dict(joint=m.joint(j).name,all_angle_radius_upper_m=maximum,geom=which,planner_weight_m_per_rad=2.,weight_conservative=maximum<=2.))
 return result

def main():
 began=time.monotonic();ch,hands=mo.empty_cell();idle=json.loads((I/'results/idle.json').read_text());q=np.array(idle['q']);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
 ch.set_contacts(hands);closed_hits,mins,_=f.contacts(ch,q)
 doors=[g for g,n in enumerate(ch.gnames) if n.startswith('cabinet_door_sweep')]
 targets=[g for g,n in enumerate(ch.gnames) if g not in doors and not n.startswith(('upper_cabinet','north_wall','south_wall','south_cabinet','floor'))]
 cache={g:points(ch,g) for g in doors+targets};door_rows=[];unresolved=[]
 for a in doors:
  for b in targets:
   va,vb=cache[a],cache[b]
   if va is None or vb is None:continue
   delta=np.maximum(np.maximum(va.min(0)-vb.max(0),vb.min(0)-va.max(0)),0)
   if np.linalg.norm(delta)>=.01:continue
   proof=qp(va,vb);row=dict(pair=[ch.gnames[a],ch.gnames[b]],**proof)
   if proof['upper_m']<.01-1e-6 and proof['max_constraint_error_m']<1e-7:door_rows.append(row)
   elif proof['lower_m']<.01-1e-6:unresolved.append(row)
 # All inherited cabinet sweep unions are queried, including fixtures which
 # the ordinary arm checker masks out. No negative penetration depth claimed.
 corridor=idle['counter_corridor'];torso=[]
 for g,n in enumerate(ch.gnames):
  if not n.startswith(('rail_beam','rail_guide','cable_chain_swept')):continue
  v=cache.get(g)
  if v is None:v=points(ch,g)
  if v is not None and all(v.max(0)>=corridor['min_m']) and all(v.min(0)<=corridor['max_m']):torso.append(n)
 bounds=audit_motion_bounds(ch)
 # Check claimed static minimum categories on diverse, difficult poses.
 ws=json.loads((I/'results/static_all.json').read_text())['witnesses'];static=[]
 keys=['Q05.carrot__peel_index_0','Q05.potato__helper_index_5','Q02.carrot__wash','Q12.carrot__deliver','Q16__soak_bok_choy','Q21__Wash_unpeeled_tomato','Q22__Remove_hard_core_without_seed_cavity','Q27__wipe_secondary']
 for key in keys:
  w=ws[key];ph=next(x for x in s.P['phases'] if x['id']==w['phase']);sg=next(x for x in ph['segments'] if x['label']==w['label']);c=s.Checker(ph,sg)
  bounds+=audit_motion_bounds(c)
  for pi,po in enumerate(w['poses']):
   c.d.qpos[:]=po['q'];mujoco.mj_forward(c.m,c.d)
   for category,value in po['min_clearance'].items():
    a,b=[c.gnames.index(n) for n in value['pair']];va,vb=points(c,a),points(c,b)
    if va is None or vb is None:continue
    proof=qp(va,vb)
    static.append(dict(stroke=key,pose=pi,category=category,pair=value['pair'],submitted_lower_mm=value['clearance_mm'],required_mm=value['required_mm'],independent=proof,lower_not_overstated=value['clearance_mm']/1000<=proof['upper_m']+2e-7,independent_gap_pass=proof['lower_m']>=value['required_mm']/1000-1e-6))
 # Passing: original reference at a denser 201 states, plus independently
 # formed convex swept-translation hulls for every doubtful box/mesh pair.
 ch,hands=mo.empty_cell();passing=json.loads((I/'results/passing.json').read_text());a=np.array(passing['q_start']);b=np.array(passing['q_end']);sample_hits=[]
 for alpha in np.linspace(0,1,201):
  hits,na=contacts(ch,a+(b-a)*alpha,hands)
  if hits:sample_hits.append(dict(alpha=float(alpha),hits=hits[:6]))
 ch.d.qpos[:]=a;mujoco.mj_forward(ch.m,ch.d);oracle=Bounds(ch,f.required);motion=np.zeros(ch.m.ngeom)
 for g in range(ch.m.ngeom):
  body=int(ch.m.geom_bodyid[g]);anc=[]
  while body:anc.append(body);body=int(ch.m.body_parentid[body])
  for side in s.model.SIDES:
   if ch.m.body(side+'_carriage').id in anc:motion[g]=b[ch.qa[side+'_carriage_x']]-a[ch.qa[side+'_carriage_x']]
 verts={g:points(ch,g) for g in range(ch.m.ngeom)};narrow=[];unhandled=[];broad_count=0
 # Broadphase exact independent vertices for boxes/meshes; other types are
 # retained in the submitted analytic support oracle, not silently omitted.
 for u,v,need,cat in oracle.pairs:
  va,vb=verts[u],verts[v];dx=motion[u]-motion[v]
  if va is None or vb is None:
   unhandled.append((u,v));continue
  if dx:va=np.vstack([va,va+np.array([dx,0,0])])
  delta=np.maximum(np.maximum(va.min(0)-vb.max(0),vb.min(0)-va.max(0)),0)
  lower=float(np.linalg.norm(delta))
  if lower>=need+1e-7:broad_count+=1;continue
  proof=qp(va,vb);narrow.append(dict(pair=[ch.gnames[u],ch.gnames[v]],required_mm=need*1000,category=cat,**proof,gap_pass=proof['lower_m']>=need-1e-6))
 print('door violations',len(door_rows),'passing QP',len(narrow),'samples hit',len(sample_hits),flush=True)
 dump('geometry_independent.json',dict(parked_closed_reference_pass=not closed_hits,all_doors_open_pass=not door_rows and not unresolved,door_violations=door_rows,door_unresolved=unresolved,door_counts=dict(collections.Counter('helper' if r['pair'][1].startswith('L_') else 'slicer' if r['pair'][1].startswith('slicer_') else 'other' for r in door_rows)),human_corridor_intersections=torso,static_crosschecks=static,all_static_bounds_consistent=all(x['lower_not_overstated'] and x['independent_gap_pass'] for x in static),motion_radius_bounds=bounds,all_2m_weights_conservative=all(r['weight_conservative'] for r in bounds),passing=dict(reference_states=201,max_carriage_step_mm=1745/200,sample_violations=sample_hits,eligible_pairs=len(oracle.pairs),independent_box_mesh_broadphase=broad_count,independent_box_mesh_QP=narrow,analytic_other_pairs=len(unhandled),QP_pass=all(r['gap_pass'] for r in narrow),scope='Independent continuous convex swept hull for box/mesh pairs; analytic primitives remain covered by the submitted oracle. Denser reference samples alone are not continuous evidence.'),elapsed_s=time.monotonic()-began))
if __name__=='__main__':main()
