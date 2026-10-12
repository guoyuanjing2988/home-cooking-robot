import json,numpy as np,mujoco,time,math
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from chain import checker,target
from planner import edge
G=json.load(open('results/chain_Z8/G4.json'));a=G['segments'][0];q0=np.array(a['path'][-1]);R=np.array(a['R'])
t=target('Z8','mandoline_work');ch,_=checker('Z8','holder');ch.active=ch.arm_ids
ch.configure_target(t,R);print('windows',len(ch.windows))
m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids
r=ch.check(q0,kind='working',mass=.55,force=t['force']);print('state0 ok',r['ok'],[h['pair'] for h in r['hits']][:3],'allowed',ch.permissions('working'))
A,B=np.array(t['points'][0]),np.array(t['points'][-1]);n=math.ceil(np.linalg.norm(B-A)/.001);q=q0.copy()
lo=m.jnt_range[ids,0]+1e-9;hi=m.jnt_range[ids,1]-1e-9
for i in range(1,n+1):
 tgt=A+(B-A)*i/n
 def res(x):
  d.qpos[:]=q;d.qpos[ids]=x;mujoco.mj_kinematics(m,d)
  return np.r_[10*(d.site_xpos[sid]-tgt),Rotation.from_matrix(R@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 rr=least_squares(res,np.clip(q[ids],lo,hi),bounds=(lo,hi),max_nfev=50,gtol=1e-9,ftol=1e-9,xtol=1e-9);nq=q.copy();nq[ids]=rr.x
 pass
 e=edge(ch,q,nq,time.monotonic()+60,kind='working',mass=.55,force=t['force'])
 if not e['ok']:
  qq=np.array(e['q']);d.qpos[:]=qq;mujoco.mj_kinematics(m,d);p=d.site_xpos[sid];w=ch.windows[0];nrm=np.array(w['normal']);delta=p-np.array(w['origin']);ax=delta@nrm
  print('  rejected; off-line',np.linalg.norm(delta-ax*nrm)*1000,'mm; rot',np.max(abs(d.site_xmat[sid].reshape(3,3)-R)),[h['pair'] for h in e['rejection']['hits']][:3]);break
 q=nq
print('reached',i,'of',n)
if not e['ok']:
 rej=e['rejection'];print('hits',[(h['pair'],round(h.get('real_gap_mm',0),2),h.get('reason','')) for h in rej['hits']][:5]);print('load',rej['load']['ok'],'stab',rej['stability']['ok'],'mobile',rej['mobile']['ok'],'ranges',rej['ranges'])
 for w in ch.windows:
  nrm=np.array(w['normal']);delta=p-np.array(w['origin']);ax=delta@nrm;print(w['face'],'axial',round(ax*1000,3),'lat_um',round(np.linalg.norm(delta-ax*nrm)*1e6,2),'len',w['length_m'])
