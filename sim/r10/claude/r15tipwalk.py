"""R15 plating: one continuous tip of the held wok from A0 to A1 deg (as r15reach.py pour: rim-centre
pivot, lip DROP above the plate; TIP=y sideways, TIP=x toward the robot), by IK continuation: each 1° step starts the pose-only least-squares IK from the
previous joint vector (cart fixed), so the arm stays on its branch; the unchanged checker
(collisions, joint ranges, rated load) runs at every step (full Bounds check every 5°).
Start poses: the collision-free candidates of a r15reach pour probe at A0 (START=<json>),
tried best-reserve first until one walks through to A1.
python r15tipwalk.py START=<reach json at A0> [TIP=y|x] [GRASP=top|end] [A0=15] [A1=90] [DROP=.03] [TRIES=12] [PH=plate height] [R16=1: R16 kitchen]
-> results/r15/tipwalk_<cart x>.json (per-degree joint steps, min reserve, q path)"""
import sys,os,json,numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import chain
from scene import build,save
from checker import Checker,reference
import kitchen15 as K
KV=dict(a.split('=',1) for a in sys.argv[1:])
A0,A1=float(KV.get('A0',15)),float(KV.get('A1',90));DROP=float(KV.get('DROP',.03));TRIES=int(KV.get('TRIES',12));TIP=KV.get('TIP','y');GRASP=KV.get('GRASP','top')
PLATE_C=np.array(K.PLATE['c'],float)
def Ry(a):
 a=np.radians(a)
 if TIP=='x':return np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
 return np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
lip,toward=(np.array([0,-K.A_RIM,0]),np.array([0,-1.,0])) if TIP=='x' else (np.array([K.A_RIM,0,0]),np.array([1.,0,0]))
PH=float(KV.get('PH',K.PLATE['h']))   # R16: PH=.15 = waste bucket at the plating spot (wok rinse)
target=PLATE_C+[0,0,PH+DROP]-.05*toward;piv=target-Ry(90)@lip
a_w,j_w=(np.array([0,0,-1.]),np.array([0,1.,0])) if GRASP=='top' else (np.array([1.,0,0]),np.array([0,0,1.]))
bc=K.GRIP['c']-K.WOK0
st=json.load(open(KV['START']));cands=sorted(st['cands'],key=lambda c:-c['reserve_mm'])[:TRIES]
def run(sign,q0):
 Rwt=reference.rotation(a_w,sign*j_w);T=np.eye(4);T[:3,:3]=Rwt.T;T[:3,3]=-Rwt.T@bc
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_wok_held=dict(T_tool_wok=T.tolist()),r15_plate_c=PLATE_C.tolist(),r15_plate_h=PH,r16='R16' in KV)
 tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id
 lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids];hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids]
 q=np.array(q0,float);path=[];worst=0.;minres=1e9
 for A in np.arange(A0,A1+1e-9,1.):
  R=Ry(A);o=piv-R@np.array([0,0,K.DEPTH]);p=o+R@bc;Rt=reference.rotation(R@a_w,sign*(R@j_w))
  def res(x):
   q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-p)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  x0=np.clip(q[ids],lo+1e-8,hi-1e-8);sol=least_squares(res,x0,bounds=(lo+1e-9,hi-1e-9),max_nfev=200,xtol=1e-10,ftol=1e-10)
  q[ids]=sol.x;pe,re=ch.pose_error(q,p,Rt)
  stepd=float(np.degrees(np.max(abs(sol.x-x0))));worst=max(worst,stepd)
  full=abs(A-round(A/5)*5)<1e-6;chk=ch.check(q,full=full,mass=0.)
  rmin=min((v['reserve_mm'] for cat,v in chk['clearance'].items() if cat!='self'),default=None) if full else None
  ok=pe<=.005 and re<=np.radians(3) and not chk['hits']
  path.append(dict(A=float(A),step_deg=round(stepd,2),pose_mm=round(pe*1000,2),ok=bool(ok),reserve_mm=None if rmin is None else round(rmin,1),hits=[h['pair'] for h in chk['hits']][:3],q=q.tolist()))
  if rmin is not None:minres=min(minres,rmin)
  if not ok:return False,path,worst,minres
 return True,path,worst,minres
best=None
for i,c in enumerate(cands):
 ok,path,worst,minres=run(c['jaw_sign'],c['q']);print(i,'ok' if ok else f"stops at {path[-1]['A']}° {path[-1]['hits'] or path[-1]['pose_mm']}",'max step/°',round(worst,2),flush=True)
 if ok and (best is None or worst<best[1]):best=(path,worst,minres,c)
 if ok and worst<3:break
cx=st['best']['q'][0] if st.get('best') else None
res=dict(start=KV['START'],a0=A0,a1=A1,ok=best is not None,max_joint_step_per_deg=round(best[1],2) if best else None,min_reserve_mm=round(best[2],1) if best else None,
 tip_rate_limit_degps=round(180/best[1],0) if best else None,jaw_sign=best[3]['jaw_sign'] if best else None,path=best[0] if best else path)
os.makedirs('results/r15',exist_ok=True);save(f"results/r15/tipwalk_tip{TIP}_{GRASP}_cx{round(cands[0]['q'][0],2):g}"+(f"_ph{PH:g}" if "PH" in KV else "")+".json",res);print(json.dumps({k:v for k,v in res.items() if k!='path'}))
