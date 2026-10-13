"""R19 #2: why an FR5 anchor has no IK start (diagnosis only; nothing is planned, no rule is changed).

For the wok anchors (lifted / over the plate / under the tap; R17 options GTILT=25, sign -1, PY) and the lid
anchors, the UR5e's checked state (ur5e_enc2_pgc chain, the play state whose TCP is nearest the anchor pose) is
mapped to the FR5 with the same tool pose (q_FR5 = q_UR - (MOUNT_YAW, 0, 0, 0, 0, CLOCK), the arms.py choices),
then solved exactly on the FR5 (local IK, joint windows free) and checked:
 - which FR5 joints leave their window (J1 +-175, J2/J4 +85/-265, J3 +-160, J5/J6 +-175 or +-360);
 - with the windows on (bounded IK from that state): the pose error and the checker's hits.
Then the same anchor is re-solved with r17chain's own 96-start solver (solver.solve, seeds 14/15) on model variants:
the stock arm, J4 (and J2) window opened to +-360 deg, the base yaw 0 instead of 77 deg, the box gripper.
python r19arm_diag.py ARM=fr5_pgc [PY=.15] [ANCHORS=lifted,over the plate,under the tap] [VARIANTS=stock,j4,j24,yaw0,box]
-> results/r19/armswap/diag_<arm>.json"""
import sys,os,json,time
import numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import chain,arms
from scene import build
from checker import Checker
from solver import solve
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spider']=(1.52,.36);K17.set_wok_tilt(25.)
ARM=arms.current();SIGN=-1;I=np.eye(3)
PYv=float(KV.get('PY',.15))
UR='results/r17/chain_wok_s-1_final_py.15_ur5e_enc2_pgc.json'
W0=K15.WOK0;PC=np.array(K15.PLATE['c'],float);PC[1]=PYv;PH=K15.PLATE['h'];target=PC+[0,0,PH+.03]+[0,.05,0]
piv=target-K.Rx(90)@np.array([0,-K15.A_RIM,0]);o0=piv-[0,0,K15.DEPTH];S=K17.SINK_WOK
ANCH={'lifted':(I,W0+[0,0,.03],None),'over the plate':(I,o0,None),'under the tap':(I,S,-1.06)}
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF))
SC=dict(r17_lever=K17.LEVER_OPEN,r15_plate_c=PC.tolist())
def tree_for(arm,variant):
 cfg=chain.chain_cfg('SD',**{**BASE,**SC,**K17.held_cfg('wok',SIGN)},arm=arm)
 if variant=='box':cfg['arm']=arm.replace('_pgc','')
 if variant=='yaw0':
  arms.ARMS['_diag_yaw0']=dict(arms.ARMS[arm],mount_yaw_deg=0.);cfg['arm']='_diag_yaw0'
 tree,meta=build(cfg,None)
 for j in tree.iter('joint'):
  n=j.get('name')
  if (variant in ('j4','j24','all') and n=='R_wrist_1_joint') or (variant in ('j24','all') and n=='R_shoulder_lift_joint') or (variant=='all' and n in ('R_shoulder_pan_joint','R_wrist_2_joint','R_wrist_3_joint')):
   j.set('range','-6.28318530718 6.28318530718')
 return Checker(tree,meta)
def run():
 out=dict(arm=ARM,plate_y=PYv,ur_chain=UR,anchors={})
 chs={v:tree_for(ARM,v) for v in KV.get('VARIANTS','stock,j4,j24,yaw0,box').split(',')}
 ch=chs['stock'];m,d=ch.m,ch.d;ids=ch.arm_ids;sid=m.site('R_prep').id;lo,hi=m.jnt_range[ids,0],m.jnt_range[ids,1]
 os.environ['ARM']='ur5e_enc2_pgc'
 u=json.load(open(UR));cu=tree_for('ur5e_enc2_pgc','stock');P=np.array(u['play'],float)
 os.environ.pop('ARM',None)
 yaw,clk=np.radians(arms.ARMS[ARM]['mount_yaw_deg']),np.radians(arms.ARMS[ARM]['clock_deg'])
 for name in KV.get('ANCHORS','lifted,over the plate,under the tap').split(','):
  R,p,cx=ANCH[name];pt,Rt=K.tcp_pose('wok',R,p,SIGN);rec={}
  # UR5e state nearest the anchor pose
  dist=[]
  for q in P:
   cu.d.qpos[:]=q;mujoco.mj_kinematics(cu.m,cu.d);sp=cu.m.site('R_prep').id
   dist.append(np.linalg.norm(cu.d.site_xpos[sp]-pt)+.05*Rotation.from_matrix(Rt@cu.d.site_xmat[sp].reshape(3,3).T).magnitude())
  k=int(np.argmin(dist));qu=P[k].copy();rec['ur_state']=dict(index=k,match=round(float(dist[k]),4),cart=round(float(qu[0]),3),q_deg=np.degrees(qu[3:9]).round(1).tolist())
  q=qu.copy();q[3]-=yaw;q[8]-=clk
  def ik(q0,bounded):
   q=np.array(q0,float)
   def res(x):
    q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d);return np.r_[(d.site_xpos[sid]-pt)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
   b=(lo+1e-9,hi-1e-9) if bounded else (-np.inf,np.inf);x0=np.clip(q[ids],lo+1e-8,hi-1e-8) if bounded else q[ids]
   s=least_squares(res,x0,bounds=b,max_nfev=500,xtol=1e-12,ftol=1e-12);q[ids]=s.x;pe,re=ch.pose_error(q,pt,Rt);return q,pe*1000,float(np.degrees(re))
  qf,pe,re=ik(q,False);qd=np.degrees(qf[3:9])
  # the 2pi label that best fits each window
  for j in range(6):
   for kk in (0,-1,1):
    v=qd[j]+360*kk
    if np.degrees(lo[j])<=v<=np.degrees(hi[j]):qd[j]=v;break
  over=[dict(joint=f'J{j+1}',deg=round(float(qd[j]),1),window=np.degrees([lo[j],hi[j]]).round(0).tolist()) for j in range(6) if not np.degrees(lo[j])-1e-6<=qd[j]<=np.degrees(hi[j])+1e-6]
  qf[3:9]=np.radians(qd);r=ch.check(qf,full=True,mass=0.)
  rec['mapped_free_ik']=dict(pose_mm=round(pe,2),rot_deg=round(re,2),q_deg=qd.round(1).tolist(),outside_window=over,hits=[h['pair'] for h in r['hits']][:4],ok_if_windows_ignored=not r['hits'])
  qb,pe,re=ik(qf,True);r=ch.check(qb,full=True,mass=0.)
  rec['mapped_bounded_ik']=dict(pose_mm=round(pe,2),rot_deg=round(re,2),q_deg=np.degrees(qb[3:9]).round(1).tolist(),hits=[h['pair'] for h in r['hits']][:4],ok=bool(r['ok']) and pe<=5 and re<=3)
  # r17chain's anchor solve on the variants
  rec['solver']={}
  for v,c in chs.items():
   t0=time.monotonic();cnt={};hits={};n=0
   for seed in (14,15):
    t=dict(name='wok',points=[list(pt)]*2,held=None,kind='transfer',force=None,approach=list(Rt[:,0]),jaws=[tuple(SIGN*(R@K.OBJ['wok']['j']))],jaw_q=.015)
    if cx is not None:t['cart_x']=cx
    s=solve(c,pt,list(Rt[:,0]),target=t,seed=seed)
    for k_,v_ in s['status_counts'].items():cnt[k_]=cnt.get(k_,0)+v_
    n+=len(s['candidates'])
    for row in s['rows']:
     for h in (row.get('check') or {}).get('hits',[]):kk=' | '.join(sorted(h['pair']));hits[kk]=hits.get(kk,0)+1
   rec['solver'][v]=dict(status=cnt,candidates=n,top_hit_pairs=sorted(hits.items(),key=lambda x:-x[1])[:5],s=round(time.monotonic()-t0))
   print(name,v,rec['solver'][v],flush=True)
  out['anchors'][name]=rec;print(name,json.dumps({k:v for k,v in rec.items() if k!='solver'}),flush=True)
 os.makedirs('results/r19/armswap',exist_ok=True);fn=f'results/r19/armswap/diag_{ARM}.json';json.dump(out,open(fn,'w'),indent=1);print(fn)
if __name__=='__main__':run()
