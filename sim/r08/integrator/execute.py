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
def mass(t):return {'carrot':.12,'holder':.55,'catch_tray':.55,None:0}[t['held']]
def continuation(ch,t,start,R,budget=65):
 begun=time.monotonic();deadline=begun+budget;m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.active
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
 static=all(r['ok'] for r in endpoints);internal=dict(ok=False,reason='static_endpoint_unadmitted')
 if static:
  c=endpoints[0]['best'];internal=continuation(ch,t,c['q'],np.array(c['rotation']))
 save(f'results/strokes/{index}.json',dict(index=index,layout=cfg['id'],target=t,static_ok=static,starts=sum(r['starts'] for r in endpoints),endpoints=[dict(ok=r['ok'],best=r['best'],status_counts=r['status_counts']) for r in endpoints],internal=internal))
 print('stroke',index,'static',static,'internal',internal['ok'],flush=True)
def diagnostic_q(row):
 if row['best'].get('q') is not None:return np.array(row['best']['q'])
 return np.array(load('assets/park.json')['q'])
def connection(index):
 cfg=selected();_,meta=build(cfg);ts=targets(cfg,meta);a=load(f'results/strokes/{index}.json');b=load(f'results/strokes/{index+1}.json')
 # Preserve the departing held geometry throughout the diagnostic connection.
 # A change in ownership cannot be hidden by compiling the next tool early.
 tree,meta=build(cfg,ts[index]['held']);ch=Checker(tree,meta)
 q0=diagnostic_q(a['endpoints'][-1]);q1=diagnostic_q(b['endpoints'][0]);park=np.array(load('assets/park.json')['q'])
 r=plan(ch,q0,q1,65,stages=[park],seed=300+index,mass=mass(ts[index]))
 same=ts[index]['held']==ts[index+1]['held'];endpoints=a['static_ok'] and b['static_ok']
 # These paths do not possess verified grasp/release/drawer events. They remain
 # prospective even if collision-free; the World is never incremented here.
 save(f'results/connections/{index}.json',dict(index=index,from_stroke=ts[index]['name'],to_stroke=ts[index+1]['name'],same_attachment=same,endpoints_admitted=endpoints,planner=r,executed=False,binding_ready=False,reason='Persistent station support/grasp/release events are not yet qualified; diagnostic path cannot commit food state.'))
 print('connection',index,'geometric',r['ok'],'executed False',flush=True)
def idle():
 cfg=selected();tree,meta=build(cfg);ch=Checker(tree,meta);park=np.array(load('assets/park.json')['q']);snapshot=ch.check(park)
 bounds=[];hits=[]
 for g in range(ch.m.ngeom):
  if not ch.robot[g] and not ch.gnames[g].startswith('door_pause_sensor'):continue
  lo=np.array([ch.bounds.support(g,-a)[k] for k,a in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,a)[k] for k,a in enumerate(np.eye(3))])
  # Full door sweep is below/above separated for the retained legal park band.
  sensor=ch.gnames[g].startswith('door_pause_sensor')
  door_gap=lo[1]-.230 if sensor else 1.35-hi[2]
  strip=bool(hi[0]>-1.8 and lo[0]<1.8 and hi[1]>0 and lo[1]<.23 and hi[2]>.85 and lo[2]<1.35)
  corridor=bool(hi[0]>-1.6 and lo[0]<.6 and hi[1]>-.75 and lo[1]<-.05 and hi[2]>.85 and lo[2]<1.85)
  r=dict(name=ch.gnames[g],lo=lo.tolist(),hi=hi.tolist(),door_sweep_gap_mm=door_gap*1000,front_strip=strip,corridor=corridor);bounds.append(r)
  if door_gap<.01-1e-8 or strip or corridor:hits.append(r)
 first=load('results/strokes/0.json');last=load('results/strokes/10.json')
 q0=diagnostic_q(first['endpoints'][0]);q1=diagnostic_q(last['endpoints'][-1])
 unfold=plan(ch,park,q0,65,stages=[q1],seed=990)
 fold=plan(ch,q1,park,65,stages=[q0],seed=991)
 save('results/idle.json',dict(pass_=False,snapshot_pass=bool(snapshot['ok'] and not hits),snapshot=snapshot,park_q=park.tolist(),robot_bounds=bounds,idle_hits=hits,fold=fold,unfold=unfold,reason='Idle execution requires a connected carrot sequence and exact final park. Prospective fold/unfold are diagnostic.',door_scope='closed leaves in motion; full sweeps only at park'))
 print('idle snapshot',snapshot['ok'] and not hits,'fold',fold['ok'],'unfold',unfold['ok'],flush=True)
if __name__=='__main__':
 if sys.argv[1]=='stroke':stroke(int(sys.argv[2]))
 elif sys.argv[1]=='connection':connection(int(sys.argv[2]))
 elif sys.argv[1]=='idle':idle()
