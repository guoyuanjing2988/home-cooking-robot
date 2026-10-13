"""R19 #2 diagnosis (not a check, not a plan): can another arm follow the UR5e's own checked path?

The stored UR5e chain (play, unwrapped) is replayed on the UR5e model to get the TCP pose of every state; the other
arm follows those poses by IK continuation (start: the UR5e state mapped through arms.py's mount yaw / gripper
clocking, then each state from the previous one, joint windows on), in the same scene (r19enc_check.ctx). Every
state gets the fast checker, every 10th the full one. Reported: where the arm loses the pose (a joint window) and
which pairs hit, with design variants: SPACER=<m> (a gripper adapter longer by that much along the flange axis),
PY=<y> (plating spot y, wok sets).
python r19arm_pathdiag.py SET=wok|wok_plate2b|lid UR=<suffix of the UR5e chain, e.g. _py.15_ur5e_enc2_pgc> ARM2=fr5_j6_pgc [SPACER=.02] [PY=.17]
-> results/r19/armswap/pathdiag_<set>_<arm>[_sp<spacer>][_py<y>].json"""
import sys,os,json,time
KV0=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
ARM2=KV0['ARM2'];SP=float(KV0.get('SPACER',0));KEY=KV0['SET']
sys.argv=[sys.argv[0],'recheck','SET='+KEY,'SUFFIX='+KV0.get('UR',''),'NEW=ur5e_enc2_pgc']+(['PY='+KV0['PY']] if 'PY' in KV0 else [])
import numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import arms,r19enc_check as C
from r19smooth import unwrap
if SP:
 _orig=arms.swap
 def _swap(tree,arm):
  _orig(tree,arm)
  if arm==ARM2:   # the gripper adapter SP longer along the flange axis (FR5 / CS66 flange site: identity in the wrist-3 frame)
   t=tree.find(".//body[@name='R_tool']");p=np.fromstring(t.get('pos'),sep=' ');p[2]+=SP;t.set('pos',arms.fmt(p))
  return tree
 arms.swap=_swap
def run():
 cu=C.ctx(KEY,'ur5e_enc2_pgc')['ch']
 cf=C.ctx(KEY,ARM2)['ch'];m,d=cf.m,cf.d;ids=cf.arm_ids;sid=m.site('R_prep').id;lo,hi=m.jnt_range[ids,0],m.jnt_range[ids,1]
 r=json.load(open(C.CHAINS[KEY][0][:-5]+KV0.get('UR','')+'.json'));P=unwrap(r['play'])
 sp=cu.m.site('R_prep').id;T=[]
 for q in P:
  cu.d.qpos[:]=q;mujoco.mj_kinematics(cu.m,cu.d);T.append((cu.d.site_xpos[sp].copy(),cu.d.site_xmat[sp].reshape(3,3).copy()))
 A=arms.ARMS[ARM2];q=np.array(P[0],float);q[3]-=np.radians(A.get('mount_yaw_deg',0.));q[8]-=np.radians(A.get('clock_deg',0.))
 for j in range(6):
  c_=[q[3+j]+i*2*np.pi for i in (-2,-1,0,1,2) if lo[j]<=q[3+j]+i*2*np.pi<=hi[j]]
  if c_:q[3+j]=min(c_,key=abs)
 rows=[];pairs={};first=None;lost=None
 for i,(pt,Rt) in enumerate(T):
  q[0]=P[i][0]
  def res(x):
   q[ids]=x;d.qpos[:]=q;mujoco.mj_kinematics(m,d);return np.r_[(d.site_xpos[sid]-pt)*10,Rotation.from_matrix(Rt@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  s=least_squares(res,np.clip(q[ids],lo+1e-8,hi-1e-8),bounds=(lo+1e-9,hi-1e-9),max_nfev=300,xtol=1e-12,ftol=1e-12);q[ids]=s.x
  pe,re=cf.pose_error(q,pt,Rt)
  if (pe>.005 or re>np.radians(3)) and lost is None:
   lost=dict(state=i,pose_mm=round(pe*1e3,1),rot_deg=round(float(np.degrees(re)),1),at_limit=[f'J{j+1}' for j in range(6) if min(q[ids][j]-lo[j],hi[j]-q[ids][j])<np.radians(.5)],q_deg=np.degrees(q[ids]).round(1).tolist())
  c=cf.check(q,full=(i%10==0),mass=0.)
  h=[' | '.join(sorted(x['pair'])) for x in c['hits']]
  for k in set(h):pairs[k]=pairs.get(k,0)+1
  if h and first is None:first=dict(state=i,pairs=sorted(set(h))[:3])
  rows.append(dict(i=i,pose_mm=round(pe*1e3,2),hits=sorted(set(h))[:2]))
 hit_states=[x['i'] for x in rows if x['hits']]
 runs=[]
 for i in hit_states:
  if runs and i==runs[-1][1]+1:runs[-1][1]=i
  else:runs.append([i,i])
 out=dict(set=KEY,ur_chain=C.CHAINS[KEY][0][:-5]+KV0.get('UR','')+'.json',arm=ARM2,spacer_m=SP,plate_y=KV0.get('PY'),states=len(P),
  pose_lost=lost,first_hit=first,hit_states=len(hit_states),hit_runs=runs[:20],pairs=dict(sorted(pairs.items(),key=lambda x:-x[1])),method=__doc__)
 os.makedirs('results/r19/armswap',exist_ok=True)
 fn=f"results/r19/armswap/pathdiag_{KEY}_{ARM2}{'_sp'+KV0['SPACER'] if SP else ''}{'_py'+KV0['PY'] if 'PY' in KV0 else ''}.json";json.dump(out,open(fn,'w'),indent=1)
 print(json.dumps({k:v for k,v in out.items() if k!='method'}));print(fn)
if __name__=='__main__':run()
