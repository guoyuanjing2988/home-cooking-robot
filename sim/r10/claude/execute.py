"""Selected carrot diagnostics, strict internal replay, connection and idle plans.

No failed prefix is committed. Hardware-event/food binding readiness is separate
from a geometrically passing path. CLI chunks remain independently bounded.
"""
import sys,time,math,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from scene import H,load,save,build,variants,targets
from checker import Checker
from solver import solve
from planner import plan,edge
def selected():return load('results/selected.json')['config']
def mass(t):return {'carrot':.12,'tomato':.15,'pusher':.25,'holder':.55,'catch_tray':.55,None:0}[t['held']]
def continuation(ch,t,start,R,budget=65):
 begun=time.monotonic();deadline=begun+budget;m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids
 a,b=np.array(t['points'][0]),np.array(t['points'][-1]);n=max(2,math.ceil(np.linalg.norm(b-a)/.003))
 q=np.array(start);path=[q.tolist()];clear=[];maximum=0;lo=m.jnt_range[ids,0]+1e-9;hi=m.jnt_range[ids,1]-1e-9
 ch.configure_target(t,R)
 for i in range(1,n+1):
  if time.monotonic()>deadline:return dict(ok=False,reason='cartesian_timeout',checked=len(path),elapsed_s=time.monotonic()-begun)
  target=a+(b-a)*i/n
  def residual(x):
   d.qpos[:]=q;d.qpos[ids]=x;mujoco.mj_kinematics(m,d)
   return np.r_[10*(d.site_xpos[sid]-target),Rotation.from_matrix(R@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  r=least_squares(residual,np.clip(q[ids],lo,hi),bounds=(lo,hi),max_nfev=50,gtol=1e-9,ftol=1e-9,xtol=1e-9)
  nxt=q.copy();nxt[ids]=r.x;pe,re=ch.pose_error(nxt,target,R)
  if pe>.005 or re>np.deg2rad(3):return dict(ok=False,reason='cartesian_pose_error',position_mm=pe*1000,orientation_deg=np.degrees(re),checked=len(path))
  e=edge(ch,q,nxt,deadline,kind=t['kind'],mass=mass(t),force=t['force'])
  if not e['ok']:return dict(ok=False,reason='internal_replay_rejected',rejection=e,checked=len(path))
  # Test EVERY replay state for process line and orientation, not endpoints only.
  for qq in e['path']:
   d.qpos[:]=qq;mujoco.mj_kinematics(m,d);p=d.site_xpos[sid];v=b-a;s=np.clip((p-a)@v/max(v@v,1e-12),0,1)
   pe,re=ch.pose_error(qq,a+s*v,R)
   if pe>.005 or re>np.deg2rad(3):return dict(ok=False,reason='off_working_line',position_mm=pe*1000,orientation_deg=np.degrees(re))
  path+=e['path'][1:];clear+=e['clearance'][1:];maximum=max(maximum,e['step_bound_m']);q=nxt
 return dict(ok=True,path=path,clearance=clear,step_bound_m=maximum,elapsed_s=time.monotonic()-begun,kind=t['kind'],budget_s=budget)
def stroke(index):
 cfg=selected();_,meta=build(cfg);t=targets(cfg,meta)[index];tree,meta=build(cfg,t['held']);ch=Checker(tree,meta)
 tree.write(H/'models'/f'stroke_{index}.xml',encoding='unicode');endpoints=[]
 for k,p in enumerate([t['points'][0],t['points'][-1]]):
  print('stroke',index,t['name'],'endpoint',k,'96 starts',flush=True)
  r=solve(ch,np.array(p),t['approach'],seed=1800+index*2+k,target=t)
  save(f'results/statics/{index}_{k}.json',r);endpoints.append(r)
 static=all(r['ok'] for r in endpoints);internal=dict(ok=False,reason='static_start_unadmitted');attempts=[]
 if endpoints[0]['ok']:
  for c in endpoints[0]['candidates']:
   internal=continuation(ch,t,c['q'],np.array(c['rotation']))
   attempts.append(dict(ok=internal['ok'],reason=internal.get('reason'),base=c['q'][:3]))
   if internal['ok']:break
 internal['attempts']=attempts
 save(f'results/strokes/{index}.json',dict(index=index,layout=cfg['id'],target=t,static_ok=static,starts=sum(r['starts'] for r in endpoints),endpoints=[dict(ok=r['ok'],best=r['best'],status_counts=r['status_counts']) for r in endpoints],internal=internal))
 print('stroke',index,'static',static,'internal',internal['ok'],flush=True)
def diagnostic_q(row):
 if row['best'].get('q') is not None:return np.array(row['best']['q'])
 q=np.zeros(11);q[:3]=[0,-.4,0];q[-2:]=.015;return q
def connection(index):
 cfg=selected();_,meta=build(cfg);ts=targets(cfg,meta);a=load(f'results/strokes/{index}.json');b=load(f'results/strokes/{index+1}.json')
 # Preserve the departing held geometry throughout the diagnostic connection.
 # A change in ownership cannot be hidden by compiling the next tool early.
 tree,meta=build(cfg,ts[index]['held']);ch=Checker(tree,meta)
 q0=np.array(a['internal']['path'][-1]) if a['internal']['ok'] else diagnostic_q(a['endpoints'][-1])
 q1=np.array(b['internal']['path'][0]) if b['internal']['ok'] else diagnostic_q(b['endpoints'][0])
 park=np.array(load('assets/park_mobile.json')['q'])
 # Three real connections: fold at departure, drive with frozen arm, unfold
 # at arrival. Each receives >=60s and checks unchanged held geometry.
 from parking import floor_route
 foldgoal=park.copy();foldgoal[:3]=q0[:3];arrive=park.copy();arrive[:3]=q1[:3]
 ch.active=ch.arm_ids
 fold=plan(ch,q0,foldgoal,65,stages=[foldgoal],seed=300+index,mass=mass(ts[index]))
 drive=floor_route(ch,foldgoal,arrive,65,mass=mass(ts[index]))
 unfold=plan(ch,arrive,q1,65,stages=[arrive],seed=400+index,mass=mass(ts[index]))
 r=dict(ok=bool(fold['ok'] and drive['ok'] and unfold['ok']),fold=fold,base_move=drive,unfold=unfold,budget_s=195,elapsed_s=sum(x.get('elapsed_s',0) for x in (fold,drive,unfold)),reason='staged fold-drive-unfold; full held object retained')
 same=ts[index]['held']==ts[index+1]['held'];endpoints=a['static_ok'] and b['static_ok']
 # These paths do not possess verified grasp/release/drawer events. They remain
 # prospective even if collision-free; the World is never incremented here.
 save(f'results/connections/{index}.json',dict(index=index,from_stroke=ts[index]['name'],to_stroke=ts[index+1]['name'],same_attachment=same,endpoints_admitted=endpoints,planner=r,executed=False,binding_ready=False,reason='Persistent station support/grasp/release events are not yet qualified; diagnostic path cannot commit food state.'))
 print('connection',index,'geometric',r['ok'],'executed False',flush=True)
if __name__=='__main__':
 if sys.argv[1]=='stroke':stroke(int(sys.argv[2]))
 elif sys.argv[1]=='connection':connection(int(sys.argv[2]))

