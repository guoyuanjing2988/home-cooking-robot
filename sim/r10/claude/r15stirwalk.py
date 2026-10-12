"""R15 stir stroke as one continuous arm motion: follow the stir bench's spatula trajectory
(the same cubic / rotation splines through the exported keyframes) for one full 5-stroke cycle
by IK continuation (each DT step starts the pose-only least squares from the previous joint
vector, cart fixed), with the unchanged checker (collisions every step, full Bounds check every
0.25 s) and the plume rule; record the joint speeds the arm needs.
Start: the collision-free, plume-clear candidates of the r15reach probe at keyframe 0, best
reserve first, until one walks the whole cycle. If a joint needs more than 180 °/s (UR5e
datasheet), the stroke must be slowed by max_speed / 180 (reported as the feasible period).
python r15stirwalk.py KEYS=<keys json> START=<reach json, key 0> [GRIP=.45] [LIFT=.004] [DT=.01] [TRIES=10]
-> results/r15/stirwalk_<tag>.json"""
import sys,os,json,numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,RotationSpline
from scipy.interpolate import CubicSpline
import chain
from scene import build,save,fmt
from checker import Checker,reference
import kitchen15 as K
KV=dict(a.split('=',1) for a in sys.argv[1:])
GRIP=float(KV.get('GRIP',.45));LIFT=float(KV.get('LIFT',.004));DT=float(KV.get('DT',.01));TRIES=int(KV.get('TRIES',10));PLUME=.20
keys=json.load(open(KV['KEYS']))['keys'];KT=np.array([k['t'] for k in keys])
PS=CubicSpline(KT,np.array([k['p'] for k in keys]),bc_type='clamped');RSPL=RotationSpline(KT,Rotation.from_matrix(np.array([k['R'] for k in keys])))
T0=KT[0];T1=T0+float(KV.get('CYCLE',12.0))   # one full 5-stroke pattern (5 x 2.4 s)
b=K.SP.grip_point(GRIP);ex=np.array([1.,0,0])
def tcp(t,sign):
 p=PS(t);R=RSPL(t).as_matrix();n=K.SP.C-p;n/=np.linalg.norm(n);pw=p+LIFT*n+K.WOK0
 return pw+R@b,reference.rotation(R@(-K.HD),R@(sign*ex))
st=json.load(open(KV['START']));cands=sorted([c for c in st['cands'] if c['plume_mm'] is not None and c['plume_mm']>=0],key=lambda c:-c['reserve_mm'])[:TRIES]
def walk(c):
 sign=c['jaw_sign'];cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=GRIP,r15_spatula_jaw=sign);tree,meta=build(cfg,None);ch=Checker(tree,meta)
 E.SubElement(tree.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K.WOK0[0],K.WOK0[1],(K.RIM_Z+1.25)/2]),size=fmt([PLUME,(1.25-K.RIM_Z)/2]),contype='0',conaffinity='0')
 pm=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));pd=mujoco.MjData(pm);pl=pm.geom('r15_plume').id
 rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(('R_gripper_spatula','R_cart','R_dock'))]
 m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
 lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
 q=np.array(c['q'],float);vmax=np.zeros(len(ids));minres=1e9;minplume=1e9;rows=[];prev=q[ids].copy()
 for i,t in enumerate(np.arange(T0,T1+1e-9,DT)):
  p,Rt=tcp(t,sign)
  def res(x):
   q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  sol=least_squares(res,np.clip(q[ids],lo+1e-8,hi-1e-8),bounds=(lo+1e-9,hi-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10);q[ids]=sol.x
  pe,re=ch.pose_error(q,p,Rt)
  if i:vmax=np.maximum(vmax,np.degrees(np.abs(sol.x-prev))/DT)
  prev=sol.x.copy()
  full=i%int(round(.25/DT))==0;chk=ch.check(q,full=full,mass=0.)
  if full:minres=min(minres,min((v['reserve_mm'] for cat,v in chk['clearance'].items() if cat!='self'),default=1e9))
  pd.qpos[:]=q;mujoco.mj_forward(pm,pd);ft=np.zeros(6);pdist=1000*min(mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft) for g in rob);minplume=min(minplume,pdist)
  if i%10==0:rows.append(dict(t=round(t,2),q=q.tolist()))
  if pe>.005 or re>np.radians(3) or chk['hits'] or pdist<0:
   return False,dict(stop_t=round(t,3),stroke=int((t-T0)//2.4),phase=round(((t-T0)%2.4)/2.4,2),pose_mm=round(pe*1000,1),hits=[h['pair'] for h in chk['hits']][:3],plume_mm=round(pdist,1),vmax=vmax.round(0).tolist())
 close=float(np.degrees(np.max(np.abs((q[ids]-np.array(c['q'])[ids]+np.pi)%(2*np.pi)-np.pi))))
 return True,dict(joint_speed_max_degps=vmax.round(0).tolist(),speed_ratio=round(float(vmax.max()/180),2),feasible_period_s=round(2.4*max(1,vmax.max()/180),2),
  min_reserve_mm=round(minres,1),min_plume_mm=round(minplume,1),cycle_closure_deg=round(close,2),jaw_sign=sign,path=rows)
out=[];best=None
for k,c in enumerate(cands):
 ok,r=walk(c);print(k,ok,{kk:v for kk,v in r.items() if kk!='path'},flush=True);out.append(dict(ok=ok,**{kk:v for kk,v in r.items() if kk!='path'}))
 if ok:best=r;break
tag=os.path.basename(KV['KEYS'])[5:-10]
res=dict(keys=KV['KEYS'],grip_m=GRIP,dt_s=DT,ok=best is not None,attempts=out,**({kk:v for kk,v in best.items()} if best else {}))
save(f'results/r15/stirwalk_{tag}.json',res);print(json.dumps({k:v for k,v in res.items() if k not in ('path','attempts')}))
