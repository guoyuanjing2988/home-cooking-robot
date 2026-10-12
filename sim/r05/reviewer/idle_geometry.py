"""Independent full-size idle, exact door/corridor and deployment replay."""
import os,sys,json,math,itertools,xml.etree.ElementTree as E
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import numpy as np,mujoco
from scipy.spatial import ConvexHull
from scipy.optimize import minimize
H=Path(__file__).resolve().parent;I=H.parent/'integrator';sys.path.insert(0,str(I));import final_check as f
from distance import Bounds
O=H/'results';idle=json.loads((I/'results/idle.json').read_text());q=np.array(idle['parked_snapshot']['q']);ph=f.s.P['phases'][0];sg=ph['segments'][0];ch=f.s.Checker(ph,sg)
root=E.parse(I/'models/idle_r05.xml');ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(root.getroot(),encoding='unicode')));ch.set_contacts(sg['poses'][0]);hits,mins,_=f.contacts(ch,q);oracle=Bounds(ch,f.required)
lo=np.array([-1.6,-.75,.85]);hi=np.array([.6,-.05,1.85]);robot_intrusions=[]
for g in np.flatnonzero(ch.robot):
 if ch.m.geom_type[g]==0:continue
 a=np.array([oracle.support(g,-axis)[k] for k,axis in enumerate(np.eye(3))]);b=np.array([oracle.support(g,axis)[k] for k,axis in enumerate(np.eye(3))])
 if np.all(b>lo)&np.all(a<hi):robot_intrusions.append(ch.gnames[g])
door_intrusions=[];door_records=[]
for ci,(xmin,xmax) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
 count=2 if xmax-xmin>.6 else 1;width=(xmax-xmin)/count
 for j in range(count):
  hinge=xmin if j==0 else xmax;sign=1 if j==0 else -1
  # At 90 degrees every full-width leaf occupies y=[.230-width,.230]
  # and x=[hinge-.018,hinge] left, or [hinge,hinge+.018] right.
  a=np.array([hinge-.018 if sign==1 else hinge,.230-width,1.35]);b=np.array([hinge if sign==1 else hinge+.018,.230,1.95]);name=f'open_cabinet_door_{ci}_{j}'
  intrusion=bool(np.all(b>lo)&np.all(a<hi));door_records.append(dict(name=name,min_m=a.tolist(),max_m=b.tolist(),human_intrusion=intrusion))
  if intrusion:door_intrusions.append(name)
trials=[]
for order in ('appliance_transfer_before_elevator','elevator_before_appliance_transfer'):
 r=E.parse(I/'models/idle_r05.xml')
 if order.startswith('elevator'):
  for g in r.findall('worldbody/geom'):
   if g.get('name','').startswith('slicer_'):
    pos=np.fromstring(g.get('pos'),sep=' ');pos[0]+=2.95;g.set('pos',f.s.model.fmt(pos))
 cc=f.s.Checker(ph,sg);cc.bind_model(mujoco.MjModel.from_xml_string(E.tostring(r.getroot(),encoding='unicode')));cc.set_contacts(sg['poses'][0]);body=cc.m.body('rail_structure').id;n=math.ceil(.95/.004);bad=None;ns=0
 for k in range(n+1):
  cc.m.body_pos[body,2]=k*.95/n;hh,_,_=f.contacts(cc,q);ns+=1
  if hh:bad=dict(lift_m=k*.95/n,pairs=hh[:5]);break
 trials.append(dict(order=order,pass_=bad is None,states_checked=ns,point_step_mm=.95/n*1000,rejection=bad))

# Full original box/mesh convex hulls, independent halfspace QP distances.
def vertices(c,g):
 m,d=c.m,c.d;rt=d.geom_xmat[g].reshape(3,3);typ=m.geom_type[g]
 if typ==6:v=np.array(list(itertools.product(*[[-x,x] for x in m.geom_size[g]])))
 elif typ==7:
  mid=m.geom_dataid[g];adr=m.mesh_vertadr[mid];v=m.mesh_vert[adr:adr+m.mesh_vertnum[mid]].astype(float)
 else:return None
 return v@rt.T+d.geom_xpos[g]
def qp(c,a,b):
 v1,v2=vertices(c,a),vertices(c,b)
 if v1 is None or v2 is None:return None
 origin=(v1.mean(0)+v2.mean(0))/2;v1-=origin;v2-=origin;h1=ConvexHull(v1).equations;h2=ConvexHull(v2).equations
 def fun(x):v=x[:3]-x[3:];return v@v
 def jac(x):v=x[:3]-x[3:];return np.r_[2*v,-2*v]
 con=[dict(type='ineq',fun=lambda x:-h1[:,:3]@x[:3]-h1[:,3],jac=lambda x:np.c_[-h1[:,:3],np.zeros_like(h1[:,:3])]),dict(type='ineq',fun=lambda x:-h2[:,:3]@x[3:]-h2[:,3],jac=lambda x:np.c_[np.zeros_like(h2[:,:3]),-h2[:,:3]])]
 result=minimize(fun,np.r_[v1.mean(0),v2.mean(0)],jac=jac,constraints=con,method='SLSQP',options=dict(ftol=1e-15,maxiter=250))
 violation=max(np.max(h1[:,:3]@result.x[:3]+h1[:,3]),np.max(h2[:,:3]@result.x[3:]+h2[:,3]));delta=result.x[3:]-result.x[:3];norm=np.linalg.norm(delta);axis=delta/max(norm,1e-15);sep=np.min(v2@axis)-np.max(v1@axis)
 return dict(qp_gap_mm=float(norm*1000),independent_projection_lower_mm=float(max(0,sep)*1000),feasibility_residual_m=float(violation),optimizer_success=bool(result.success),closest_world_m=(result.x.reshape(2,3)+origin).tolist())
checks=[]
for cat,val in mins.items():
 a,b=[ch.gnames.index(n) for n in val['pair']];v=qp(ch,a,b)
 if v:checks.append(dict(scene='idle',category=cat,pair=val['pair'],submitted_lower_mm=val['clearance_mm'],**v))
working=f.s.Checker(ph,sg);working.d.qpos[:]=f.s.PARK;mujoco.mj_forward(working.m,working.d);wall=working.gnames.index('north_wall');wallrows=[]
for g,name in enumerate(working.gnames):
 if name.startswith('wall_mount_'):
  req=f.required(working,g,wall);v=qp(working,g,wall);p=working.d.geom_xpos[g];sz=working.m.geom_size[g];front=working.d.geom_xpos[wall,1]-working.m.geom_size[wall,1]
  wallrows.append(dict(name=name,face_plane_m=float(p[1]+sz[1]),wall_front_m=float(front),gap_mm=float((front-p[1]-sz[1])*1000),permission=req is None,required=None if req is None else req[0],distance=v))
# Perturb a plate in memory; identity alone must not continue to exempt it.
plate=working.gnames.index('wall_mount_-1.84');working.d.geom_xpos[plate,1]+=.001
penetration_permission=f.required(working,plate,wall) is None;working.d.geom_xpos[plate,1]-=.001;working.d.geom_xmat[plate]=np.array([[1,0,0],[0,math.cos(.01),-math.sin(.01)],[0,math.sin(.01),math.cos(.01)]]).ravel();rotation_permission=f.required(working,plate,wall) is None
(O/'idle_geometry.json').write_text(json.dumps(dict(storage_static_reference_pass=not hits,static_blockers=hits,robot_corridor_intrusions=robot_intrusions,full_open_leaf_geometry=door_records,door_corridor_intrusions=door_intrusions,complete_idle_pass=False,deployment_trials=trials,wall_pairs=wallrows,penetrated_plate_exempt=penetration_permission,rotated_plate_exempt=rotation_permission,independent_convex_distances=checks),indent=2));print('IDLE_REPLAY',not hits,door_intrusions,[(x['order'],x['rejection']['lift_m']) for x in trials],flush=True)
