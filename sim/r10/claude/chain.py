"""R10 (orchestrator, hands-on): executable carrot chain for the docked cart.

Groups of strokes that share a pose transition are solved sequentially with the
inherited 96-start solver and the inherited Cartesian continuation (<=3 mm TCP
steps, every state replayed by edge() at <=4 mm point displacement). Connections
between groups use fold (arm-only RRT) -> pure-x drive with frozen carry pose ->
unfold (arm-only RRT), every state checked. Rules are the unchanged R09 checker.
All carrot stations (peeler, mandoline) are out on the counter for the whole
chain (fetched before, returned after); greens/tomato stations are stored.
"""
import sys,time,os
import numpy as np,mujoco
from scipy.optimize import differential_evolution
from mystat import config
from scene import build,targets,save,load,jaw_q
from checker import Checker
from solver import solve
import planner
from planner import plan,edge,plan_swept
import execute,math as _m
def continuation(ch,t,start,R,budget=65):
 """Inherited continuation; working strokes use 1 mm Cartesian steps (instead of
 3 mm) so joint interpolation stays inside the unchanged 20 um / 2e-4 window
 tolerances. Every state is still replayed by edge() at <=4 mm."""
 # R11: strokes that rely on a contact window (lift/place) also use fine steps,
 # so interpolated states stay within the 20 um / 2e-4 rad window tolerance.
 windowed=t['name'].split('@')[0] in ('raw_pick','peel_load','peel_retrieve','wedge_load')
 if windowed:return precise_line(ch,t,start,R)
 if t['kind']!='working':return execute.continuation(ch,t,start,R,budget)
 orig=_m.ceil
 try:
  f=int(__import__('os').environ.get('WORK_STEP_FACTOR','3'))
  execute.math.ceil=lambda x:orig(x*f)
  return execute.continuation(ch,t,start,R,max(budget,240))
 finally:execute.math.ceil=orig
def precise_line(ch,t,start,R,step=.001,budget=300):
 """Inherited continuation logic for seat/lift strokes, with tight IK: each 1 mm
 TCP target must be met within 0.5 mm / 0.2 deg (inherited: 5 mm / 3 deg, which
 can tilt a 160 mm carrot 4 mm into a cradle). Every state replayed by edge()."""
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 begun=time.monotonic();deadline=begun+budget;m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids
 a,b=np.array(t['points'][0]),np.array(t['points'][-1]);n=max(2,int(np.ceil(np.linalg.norm(b-a)/step)))
 q=np.array(start,float);path=[q.tolist()];clear=[];maximum=0;lo=m.jnt_range[ids,0]+1e-9;hi=m.jnt_range[ids,1]-1e-9
 ch.configure_target(t,R)
 for i in range(1,n+1):
  if time.monotonic()>deadline:return dict(ok=False,reason='cartesian_timeout',checked=len(path))
  target=a+(b-a)*i/n
  def residual(x):
   d.qpos[:]=q;d.qpos[ids]=x;mujoco.mj_kinematics(m,d)
   return np.r_[10*(d.site_xpos[sid]-target),Rotation.from_matrix(R@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  r=least_squares(residual,np.clip(q[ids],lo,hi),bounds=(lo,hi),max_nfev=300,gtol=1e-14,ftol=1e-14,xtol=1e-14)
  nxt=q.copy();nxt[ids]=r.x;pe,re=ch.pose_error(nxt,target,R)
  if pe>.0005 or re>np.deg2rad(.2):return dict(ok=False,reason='cartesian_pose_error',position_mm=pe*1000,orientation_deg=np.degrees(re),checked=len(path))
  e=edge(ch,q,nxt,deadline,kind=t['kind'],mass=execute.mass(t),force=t['force'])
  if not e['ok']:return dict(ok=False,reason='internal_replay_rejected',rejection=e,checked=len(path))
  for qq in e['path']:
   d.qpos[:]=qq;mujoco.mj_kinematics(m,d);p=d.site_xpos[sid];v=b-a;s_=np.clip((p-a)@v/max(v@v,1e-12),0,1)
   pe,re=ch.pose_error(qq,a+s_*v,R)
   if pe>.005 or re>np.deg2rad(3):return dict(ok=False,reason='off_working_line',position_mm=pe*1000,orientation_deg=np.degrees(re))
  path+=e['path'][1:];clear+=e['clearance'][1:];maximum=max(maximum,e['step_bound_m']);q=nxt
 return dict(ok=True,path=path,clearance=clear,step_bound_m=maximum,elapsed_s=time.monotonic()-begun,kind=t['kind'],budget_s=budget)
PRESENT=['peeler','mandoline']
MASS={'carrot':.12,'tomato':.15,'pusher':.25,'holder':.55,None:0}
def chain_cfg(preset,**extra):
 c=config(preset);c['present']=c.get('present_chain') or (['peeler','slicer'] if c.get('slicer') else PRESENT);c.update(extra);return c
def checker(preset,held,**extra):
 c=chain_cfg(preset,**extra);tree,meta=build(c,held);return Checker(tree,meta),meta
def dock_carry(ch,q):
 """Moving-base carry envelope: every arm/gripper/held point within +/-0.40 m of
 the cart centre along the counter and no more than 0.10 m over the counter edge."""
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
 for g,n in enumerate(ch.gnames):
  if not ch.robot[g] or not (n.startswith('R_geom_') or ch.gripper(g) or ch.held[g]):continue
  if ch.bounds.support(g,np.eye(3)[0])[0]>q[0]+.40 or ch.bounds.support(g,-np.eye(3)[0])[0]<q[0]-.40:return False
  if ch.bounds.support(g,np.eye(3)[1])[1]>.10:return False
 return True
planner.carry_clear=dock_carry
def target(preset,name):
 c=chain_cfg(preset);_,meta=build(c);t=next(t for t in targets(c,meta) if t['name']==name)
 if c.get('finger_offset') or c.get('finger'):t['jaw_q']=jaw_q(c,t['held'])
 return t
def tstate(preset,name):
 from mystat import target_state
 c=chain_cfg(preset);_,meta=build(c);return target_state(c,meta,name)
REF=None  # previous group's final state (sequential solving keeps one IK branch)
def refine(ch,q,p,R):
 """Polish an admitted IK start (<=5 mm / 3 deg) to the exact target pose, so a
 tight seat does not start from a tilted held item (3 deg x 80 mm = 4.2 mm)."""
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids;q=np.array(q,float)
 lo=m.jnt_range[ids,0]+1e-9;hi=m.jnt_range[ids,1]-1e-9
 def res(x):
  d.qpos[:]=q;d.qpos[ids]=x;mujoco.mj_kinematics(m,d)
  return np.r_[10*(d.site_xpos[sid]-p),Rotation.from_matrix(R@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 r=least_squares(res,np.clip(q[ids],lo,hi),bounds=(lo,hi),max_nfev=200,ftol=1e-14,xtol=1e-14,gtol=1e-14)
 out=q.copy();out[ids]=r.x;return out
def first_stroke(preset,name,seed,after=None):
 """Admit the first stroke of a group from 96-start IK candidates. With REF set,
 candidates are warm-started from and ranked by joint distance to REF; if none
 passes (including the optional `after` continuation), retry without REF."""
 t=target(preset,name);ch,_=checker(preset,t['held'],**tstate(preset,name));ch.active=ch.arm_ids
 if t['held'] is None and (config(preset).get('finger_offset') or config(preset).get('finger')):t['jaw_q']=.025
 selfc=lambda c:(c['check'].get('clearance') or {}).get('self',{}).get('clearance_mm',99)
 def wrap(qv,ref):
  # Same pose: each +-2pi joint shifted to be nearest ref (or into (-pi,pi]).
  qv=np.array(qv,float)
  for j in ch.arm_ids:
   lo,hi=ch.m.jnt_range[ch.m.jnt_qposadr.tolist().index(j)]
   c0=ref[j] if ref is not None else 0.
   opts=[qv[j]+2*np.pi*n for n in (-2,-1,0,1,2) if lo<=qv[j]+2*np.pi*n<=hi]
   qv[j]=min(opts,key=lambda v:abs(v-c0))
  return qv
 tries=[];static=None
 for ref in ([REF,None] if REF is not None else [None]):
  r=solve(ch,np.array(t['points'][0]),t['approach'],seed=seed,target=t,warm=ref);static=r['status_counts']
  for c in r['candidates']:c['q']=wrap(c['q'],ref)
  dist=lambda c:float(np.sum(abs(c['q'][ch.arm_ids]-np.asarray(ref)[ch.arm_ids]))) if ref is not None else -c['reserve_mm']
  for c in sorted(r['candidates'],key=lambda c:(selfc(c)<2.,dist(c))):
   q0=refine(ch,c['q'],np.array(t['points'][0]),np.array(c['rotation']))
   out=continuation(ch,t,q0,np.array(c['rotation']))
   tries.append(dict(ok=out['ok'],reason=out.get('reason'),warm=ref is not None,rej=None if out['ok'] else str(out.get('rejection'))[:600]))
   if not out['ok']:continue
   res=dict(ok=True,stroke=name,R=c['rotation'],path=out['path'],step_bound_m=out['step_bound_m'],static=static,tries=tries)
   if after is None:return res
   segs=after(res)
   if all(x['ok'] for x in segs):res['after']=segs;return res
   tries[-1]['after_fail']=[(x['stroke'],x['ok'],str(x.get('rejection') or x.get('hits') or '')[:300]) for x in segs]
 return dict(ok=False,stroke=name,static=static,tries=tries)
def next_stroke(preset,name,q,R,**extra):
 t=target(preset,name);ex=tstate(preset,name);ex.update(extra);ch,_=checker(preset,t['held'],**ex);ch.active=ch.arm_ids
 out=continuation(ch,t,q,np.array(R))
 return dict(ok=out['ok'],stroke=name,R=R,path=out.get('path'),reason=out.get('reason'),rejection=out.get('rejection'),step_bound_m=out.get('step_bound_m'))
def same_pose_event(preset,held,q,**extra):
 ch,_=checker(preset,held,**extra);return ch.check(np.array(q),mass=MASS[held])
def group(preset,name):
 res=[];beg=time.monotonic()
 if name=='G1':res.append(first_stroke(preset,'raw_pick',7101))
 elif name=='G2':
  a=first_stroke(preset,'wash_load',7201);res.append(a)
  if a['ok']:res.append(next_stroke(preset,'wash_work',a['path'][-1],a['R']))
 elif name=='G3':
  a=first_stroke(preset,'peel_load',7301);res.append(a)
  if a['ok']:
   seat=a['path'][-1];seat_pos=None
   # Release: the gripper opens and retreats back up the same line with an EMPTY
   # gripper while the carrot stays seated in the cradles (now environment).
   c=chain_cfg(preset);_,meta=build(c);t=target(preset,'peel_load');seat_pos=t['points'][-1]
   ch,_=checker(preset,None,carrot_at=seat_pos);bad=[];released_contacts=[]
   for qq in a['path'][::-1]:
    qq=np.array(qq);qq[-2:]=.025  # jaws fully open for release
    r=ch.check(qq,mass=0)
    rest=[h for h in r['hits'] if not ('raw_carrot' in h['pair'] and any(n.startswith(('R_finger_','R_gripper_')) for n in h['pair']) and min(h.get('real_gap_mm',0),h.get('upper_bound_mm',h.get('real_gap_mm',0)))>=0)]
    other_ok=r['ranges'] and r['load']['ok'] and r['mobile']['ok'] and r['stability']['ok'] and r['identity_ok']
    if rest or not other_ok:bad.append(dict(q=qq.tolist(),hits=rest[:4] or r['hits'][:4]));break
    released_contacts=released_contacts+[h for h in r['hits'] if h not in rest]
   res.append(dict(ok=not bad,stroke='peel_release_retreat_and_return',checked=len(a['path']),rejection=bad[:1],min_release_gap_mm=min([min(h.get('real_gap_mm',99),h.get('upper_bound_mm',99)) for h in released_contacts] or [None]),note='finger-to-released-carrot proximity allowed only inside the <=50 mm release window and never below 0 mm; ',note2='empty gripper retreats 40 mm while the station peels, then returns along the same line'))
   if not bad:res.append(next_stroke(preset,'peel_retrieve',seat,a['R']))
 elif name=='G4':
  # Search holder_load start candidates (several solver seeds) for one whose full
  # holder_load -> mandoline_work -> holder_retreat chain passes.
  t=target(preset,'holder_load');ch,_=checker(preset,'carrot');ch.active=ch.arm_ids;tried=[]
  for seed in (7401,7402,7403,7404):
   r=solve(ch,np.array(t['points'][0]),t['approach'],seed=seed,target=t)
   for c in r['candidates']:
    out=continuation(ch,t,c['q'],np.array(c['rotation']))
    if not out['ok']:tried.append(('holder_load',out.get('reason')));continue
    b=next_stroke(preset,'mandoline_work',out['path'][-1],c['rotation'])
    if not b['ok']:tried.append(('mandoline_work',b.get('reason')));continue
    cc=next_stroke(preset,'holder_retreat',b['path'][-1],c['rotation'])
    if not cc['ok']:tried.append(('holder_retreat',cc.get('reason')));continue
    res=[dict(ok=True,stroke='holder_load',R=c['rotation'],path=out['path'],static=r['status_counts']),dict(ok=True,stroke='release_carrot_grasp_holder',note='checked as state 0 of mandoline_work'),b,cc]
    break
   if res:break
  if not res:res=[dict(ok=False,stroke='holder_chain_search',tried=tried[:40])]
 elif name in ('GT1','GT2'):
  res.append(first_stroke(preset,{'GT1':'raw_pick@tomato','GT2':'wash_load@tomato'}[name],{'GT1':7601,'GT2':7602}[name]))
 elif name=='GT3':
  # Place the tomato on the blade plate, open the jaws (80 mm), retreat the empty
  # gripper back along the approach; the tomato now rests on the plate.
  s0=first_stroke(preset,'wedge_slide@tomato',7603);res.append(s0)
  a=next_stroke(preset,'wedge_load@tomato',s0['path'][-1],s0['R']) if s0['ok'] else dict(ok=False)
  if s0['ok']:res.append(a)
  if a['ok']:
   from scene import tomato_dz
   seat=(np.array(target(preset,'wedge_load@tomato')['points'][-1])-[0,0,tomato_dz(chain_cfg(preset))]).tolist();q=np.array(a['path'][-1]);q[-2:]=.025
   # Release window rule (as for the carrot in G3): gripper/finger proximity to the
   # just-released tomato is allowed (never penetration) while the open gripper
   # retraces the placing path (6 mm up, 50 mm back), every state checked.
   ch,_=checker(preset,None,tomato_at=seat);ch.active=ch.arm_ids;bad=[];gaps=[]
   back=[np.array(x) for x in a['path'][::-1]]+[np.array(x) for x in s0['path'][::-1][1:]]
   for qq in back:
    qq=qq.copy();qq[-2:]=.025;r=ch.check(qq,mass=0)
    ok_=lambda h:'raw_tomato' in h['pair'] and any(n.startswith(('R_finger_','R_gripper_')) for n in h['pair']) and min(h.get('real_gap_mm',0),h.get('upper_bound_mm',h.get('real_gap_mm',0)))>=0
    rest=[h for h in r['hits'] if not ok_(h)];gaps+=[min(h.get('real_gap_mm',99),h.get('upper_bound_mm',99)) for h in r['hits'] if ok_(h)]
    if rest or not(r['ranges'] and r['load']['ok'] and r['mobile']['ok'] and r['stability']['ok'] and r['identity_ok']):bad.append(dict(q=qq.tolist(),hits=(rest or r['hits'])[:4]));break
   res.append(dict(ok=not bad,stroke='tomato_release_retreat',path=None if bad else [list(x[:-2])+[.025,.025] for x in back],rejection=bad[:1],min_release_gap_mm=min(gaps) if gaps else None,note='release window: proximity to the released tomato allowed, never penetration'))
 elif name=='GT4':
  # Grasp the pusher knob (open jaws over the knob, tomato on the plate), close
  # (pusher becomes held, tomato is cut = appliance-contained), press straight
  # down, return, release and lift; grasp candidates are tried until the whole
  # sequence passes. Reports the arm's available push force.
  def rest(a):
   segs=[];q=np.array(a['path'][-1]);q[-2:]=jaw_q(config(preset),'pusher')
   ch,_=checker(preset,'pusher',tomato_gone=True);r=ch.check(q,mass=MASS['pusher'])
   segs.append(dict(ok=r['ok'],stroke='pusher_close',hits=r['hits'][:4]))
   if not r['ok']:return segs
   b=next_stroke(preset,'pusher_press',q,a['R']);segs.append(b)
   if not b['ok']:return segs
   cap=[push_capacity(ch,np.array(x)) for x in b['path'][::max(1,len(b['path'])//12)]]
   segs.append(dict(ok=True,stroke='push_capacity',min_N=min(cap),per_state_N=cap,note='max downward push the arm can hold at these states: joint torque envelope, keyed grip (150 N / 15 Nm key, SF 1.5), PGC moment, cart tip; required cutting force not yet sourced'))
   c=next_stroke(preset,'pusher_return',b['path'][-1],a['R']);segs.append(c)
   if not c['ok']:return segs
   q2=np.array(c['path'][-1]);q2[-2:]=.025;ch2,_=checker(preset,None,tomato_gone=True);ch2.active=ch2.arm_ids
   r2=ch2.check(q2,mass=0);segs.append(dict(ok=r2['ok'],stroke='pusher_release',hits=r2['hits'][:4]))
   if not r2['ok']:return segs
   # R12: straight up first; if the upper arm comes within the 10 mm door gap (the crank
   # rides the housing 20 mm higher), retreat straight back out of the knob, then diagonally.
   for v_ in ([0,0,.06],-np.asarray(target(preset,'pusher_grasp')['approach'],float)*.06,[0,-.042,.042]):
    up=cart_line(ch2,q2,np.array(a['R']),np.array(v_),None)
    if up['ok']:break
   segs.append(dict(ok=up['ok'],stroke='pusher_release_lift',path=up.get('path'),reason=up.get('reason'),vector=np.asarray(v_,float).tolist()))
   return segs
  a=first_stroke(preset,'pusher_grasp',7604,after=rest);after=a.pop('after',None);res.append(a)
  if after:res+=after
 elif name=='G4S':
  # R11 slicer: lower the vertical carrot into the chute, release (the carrot
  # drops inside the chute = appliance-contained), retreat the open gripper.
  a=first_stroke(preset,'chute_load',7451);res.append(a)
  if a['ok']:
   q=np.array(a['path'][-1]);q[-2:]=.025;ch,_=checker(preset,None);r=ch.check(q,mass=0)
   res.append(dict(ok=r['ok'],stroke='chute_release',hits=r['hits'][:4]))
   if r['ok']:
    ch.active=ch.arm_ids;t=target(preset,'chute_load')
    ret=cart_line(ch,q,np.array(a['R']),-np.asarray(t['approach'],float)*.06,None)
    res.append(dict(ok=ret['ok'],stroke='chute_retreat',path=ret.get('path'),reason=ret.get('reason')))
  a=dict(ok=False)
  if False:
   # Event: release the carrot into the golden holder, grasp the holder at the
   # same TCP. The holder-on-deck state is the first state of the working stroke,
   # which continuation() checks with the configured working windows.
   res.append(dict(ok=True,stroke='release_carrot_grasp_holder',note='checked as state 0 of mandoline_work'))
   if True:
    b=next_stroke(preset,'mandoline_work',a['path'][-1],a['R']);res.append(b)
    if b['ok']:res.append(next_stroke(preset,'holder_retreat',b['path'][-1],a['R']))
 save(f'results/chain_{preset}/{name}.json',dict(group=name,ok=all(r['ok'] for r in res) and len(res)>0,segments=res,elapsed_s=time.monotonic()-beg))
 print(preset,name,[ (r['stroke'],r['ok']) for r in res],flush=True)
def push_capacity(ch,q,hi=400.):
 """Largest downward push (N) the arm can apply at q: the pusher reacts +z on
 the tool; joint torque envelope, keyed grip, PGC moment and cart tipping."""
 from mobile import stability
 lo=0.
 for _ in range(18):
  f=(lo+hi)/2;F=[0,0,f]
  ok=ch.loads(q,F,MASS['pusher'],0)['ok'] and stability(ch,q,F,MASS['pusher'],0)['ok']
  lo,hi=(f,hi) if ok else (lo,f)
 return round(lo,1)
def carry_pose(preset,held,x,seed,near=()):
 ch,_=checker(preset,held);m,d=ch.m,ch.d;q=m.qpos0.copy();q[:3]=[x,-.21,0];q[-2:]=jaw_q(config(preset),held)
 def score(v):
  q[ch.arm_ids]=v;d.qpos[:]=q;mujoco.mj_forward(m,d)
  pen=sum(.2*float(np.sum(abs((v-np.asarray(n)[ch.arm_ids]+np.pi)%(2*np.pi)-np.pi))) for n in near)
  for c in d.contact[:d.ncon]:
   a,b=map(int,c.geom);req=ch.required(ch,a,b)
   if req is not None:pen+=max(0,req[0]+.02-c.dist)*100
  for g,n in enumerate(ch.gnames):
   if not ch.robot[g] or not (n.startswith('R_geom_') or ch.gripper(g) or ch.held[g]):continue
   pen+=max(0,ch.bounds.support(g,np.eye(3)[1])[1]-.06)*20+max(0,abs(d.geom_xpos[g][0]-x)-.30)*20
  return pen
 r=differential_evolution(score,m.jnt_range[ch.arm_ids],seed=seed,popsize=12,maxiter=150,polish=True,tol=1e-7)
 q[ch.arm_ids]=r.x;return q,ch.check(q,mass=MASS[held]),dock_carry(ch,q)
def lifted(ch,q,dz,mass=0):
 """Same tool orientation, TCP raised by dz (IK from q); staging proposal only."""
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids;q=np.array(q,float)
 d.qpos[:]=q;mujoco.mj_kinematics(m,d);p=d.site_xpos[sid]+[0,0,dz];R=d.site_xmat[sid].reshape(3,3).copy()
 lo=m.jnt_range[ids,0]+1e-9;hi=m.jnt_range[ids,1]-1e-9
 def res(x):
  d.qpos[:]=q;d.qpos[ids]=x;mujoco.mj_kinematics(m,d)
  return np.r_[10*(d.site_xpos[sid]-p),Rotation.from_matrix(R@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
 r=least_squares(res,np.clip(q[ids],lo,hi),bounds=(lo,hi),max_nfev=200);out=q.copy();out[ids]=r.x
 return out if ch.check(out,mass=mass)['ok'] else None
def cart_line(ch,q,R,vec,held):
 """Straight Cartesian retreat/approach of the TCP by vec with fixed orientation:
 inherited continuation (3 mm IK steps, every state replayed by edge())."""
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_kinematics(m,d);p=d.site_xpos[m.site('R_prep').id].copy()
 t=dict(name='line',points=[p.tolist(),(p+np.asarray(vec)).tolist()],held=held,kind='transfer',force=None,approach=[0,0,-1])
 return continuation(ch,t,np.array(q),np.array(R))
def reserve(r):
 return min([v['reserve_mm'] for c,v in (r.get('clearance') or {}).items() if c!='self' and isinstance(v,dict) and 'reserve_mm' in v] or [0.])
def via_plan(ch,a,b,budget_s=300,seed=0,mass=0,min_reserve=8.):
 """Full-check via-point search: candidate via poses must pass the complete
 check with >= min_reserve mm extra clearance; every edge is replayed by edge()
 (<=4 mm, full check). Tries direct, one-via and two-via paths."""
 beg=time.monotonic();deadline=beg+budget_s;rng=np.random.default_rng(seed);a=np.asarray(a,float);b=np.asarray(b,float);ids=ch.arm_ids
 lo=ch.m.jnt_range[ids,0];hi=ch.m.jnt_range[ids,1]
 e=edge(ch,a,b,deadline,mass=mass)
 if e['ok']:return dict(ok=True,path=e['path'],method='direct',elapsed_s=time.monotonic()-beg)
 reach=[];tried=0;last=e
 while time.monotonic()<deadline:
  tried+=1
  if reach and rng.random()<.4:
   base=reach[int(rng.integers(len(reach)))][0];v=base.copy();v[ids]=np.clip(base[ids]+(b[ids]-base[ids])*rng.uniform(.2,.8)+rng.normal(0,.35,len(ids)),lo,hi)
  else:
   v=a.copy();t=rng.uniform(.15,.85);v[ids]=np.clip(a[ids]+(b[ids]-a[ids])*t+rng.normal(0,.45,len(ids)),lo,hi)
  r=ch.check(v,mass=mass)
  if not r['ok'] or reserve(r)<min_reserve:continue
  # from start, or from an already reachable via
  src=None
  e1=edge(ch,a,v,deadline,mass=mass)
  if e1['ok']:src=(v,e1['path'])
  else:
   for rv,rp in reach[-6:]:
    e1=edge(ch,rv,v,deadline,mass=mass)
    if e1['ok']:src=(v,rp+e1['path'][1:]);break
  if src is None:last=e1;continue
  e2=edge(ch,v,b,deadline,mass=mass)
  if e2['ok']:return dict(ok=True,path=src[1]+e2['path'][1:],method='via',vias=tried,elapsed_s=time.monotonic()-beg)
  reach.append(src);last=e2
 return dict(ok=False,reason='via_search_exhausted',tried=tried,reachable=len(reach),rejection=last,elapsed_s=time.monotonic()-beg)
def connection(preset,k):
 pairs={1:('G1','G2','carrot'),2:('G2','G3','carrot'),3:('G3','G4S' if config(preset).get('slicer') else 'G4','carrot')}
 extra={}
 if config(preset).get('r11_tomato'):
  pairs={1:('GT1','GT2','tomato'),2:('GT2','GT3','tomato'),3:('GT3','GT4',None)}
  if k==3:extra=tstate(preset,'pusher_grasp')
 ga,gb,held=pairs[k];A=load(f'results/chain_{preset}/{ga}.json');B=load(f'results/chain_{preset}/{gb}.json')
 qa=np.array([s_ for s_ in A['segments'] if s_.get('path')][-1]['path'][-1]);qb=np.array(B['segments'][0]['path'][0])
 ch,_=checker(preset,held,**extra);ch.active=ch.arm_ids;beg=time.monotonic()
 out=dict(k=k,held=held);cr=dict(hits=[])
 if True:
  # Retreat along the departing stroke's approach axis and pre-approach the next
  # stroke along its own axis (6 cm straight lines), then plan fold/unfold.
  ta=target(preset,A['segments'][-1]['stroke']) if A['segments'][-1]['stroke'] in [x['name'] for x in targets(chain_cfg(preset),build(chain_cfg(preset))[1])] else None
  Ra=np.array([s_ for s_ in A['segments'] if s_.get('R')][-1]['R']);Rb=np.array(B['segments'][0]['R'])
  tb=target(preset,B['segments'][0]['stroke'])
  va=-np.asarray(ta['approach'] if ta else [0,0,-1],float)*.06;vb=-np.asarray(tb['approach'],float)*.06
  def first_ok(q,R,vs):
   last=None
   for v in vs:
    last=cart_line(ch,q,R,v,held)
    if last['ok']:return last
   return last
  def unit(v):v=np.asarray(v,float);return v/max(np.linalg.norm(v),1e-12)
  ma=unit(np.subtract(ta['points'][-1],ta['points'][0])) if ta else np.zeros(3);mb=unit(np.subtract(tb['points'][-1],tb['points'][0]))
  ret=first_ok(qa,Ra,[va,ma*.06,np.array([0,0,.06])]);pre=first_ok(qb,Rb,[vb,-mb*.06,np.array([0,0,.06])])
  out.update(retreat_ok=ret['ok'],preapproach_ok=pre['ok'])
  qa2=np.array(ret['path'][-1]) if ret['ok'] else qa;qb2=np.array(pre['path'][-1]) if pre['ok'] else qb
  if abs(qa[0]-qb[0])<1e-9 and ret['ok'] and pre['ok']:
   arm=plan_swept(ch,qa2,qb2,int(os.environ.get('CONN_BUDGET',400)),stages=[x for x in (lifted(ch,qa2,.06,MASS[held]),lifted(ch,qb2,.06,MASS[held])) if x is not None],seed=700+k,mass=MASS[held])
   out.update(mode='same_cart_spot_arm_only',arm_ok=arm['ok'],ok=bool(arm['ok']),path=(ret['path']+arm['path'][1:]+pre['path'][::-1][1:]) if arm['ok'] else None,rejection=None if arm['ok'] else str(arm.get('rejection',''))[:800],elapsed_s=time.monotonic()-beg)
   save(f'results/chain_{preset}/C{k}.json',out);print(preset,'C',k,out['ok'],'same-spot arm-only',flush=True);return
  # 1) Carry-candidate screen with DIRECT edges only (cheap, fully replayed):
  #    fold qa2->c@a, drive c@a->c@b, unfold c@b->qb2, or a direct c_i->c_j
  #    re-fold at either spot. 2) Fallback: leveled RRT strategies.
  Bd=int(os.environ.get('CONN_BUDGET',400));M=MASS[held];deadline=time.monotonic()+int(os.environ.get('SCREEN_BUDGET',1500))
  rp=ret['path'] if ret['ok'] else [qa.tolist()];pp_=pre['path'] if pre['ok'] else [qb.tolist()]
  cands=[]
  for near,seeds in (((qa,qb),(0,1,2)),((qa,),(3,4)),((qb,),(5,6))):
   for sd in seeds:
    c,crc,ccc=carry_pose(preset,held,qa[0],870+10*k+sd,near=near)
    if not(crc['ok'] and ccc):continue
    for j in ch.arm_ids:
     lo,hi=ch.m.jnt_range[ch.m.jnt_qposadr.tolist().index(j)]
     c[j]=min([c[j]+2*np.pi*n for n in (-2,-1,0,1,2) if lo<=c[j]+2*np.pi*n<=hi],key=lambda v:abs(v-qa[j])+abs(v-qb[j]))
    ca=c.copy();ca[:3]=qa[:3];cb=c.copy();cb[:3]=qb[:3]
    if ch.check(cb,mass=M)['ok'] and dock_carry(ch,cb):cands.append((ca,cb))
  cache={}
  def E_(key,a,b):
   if key not in cache:cache[key]=edge(ch,a,b,deadline,mass=M) if time.monotonic()<deadline else dict(ok=False,reason='screen_budget')
   return cache[key]
  order_=sorted(range(len(cands)),key=lambda i:float(np.sum(abs(cands[i][0][3:9]-qa2[3:9]))+np.sum(abs(cands[i][1][3:9]-qb2[3:9]))))
  path=None;how=None
  for i in order_:
   ca,cb=cands[i]
   if E_(('F',i),qa2,ca)['ok'] and E_(('D',i),ca,cb)['ok'] and E_(('U',i),cb,qb2)['ok']:
    path=list(rp)+cache[('F',i)]['path'][1:]+cache[('D',i)]['path'][1:]+cache[('U',i)]['path'][1:]+pp_[::-1][1:];how=f'direct carry {i}';break
  if path is None:
   F=[i for i in order_ if cache.get(('F',i),{}).get('ok') and cache.get(('D',i),{}).get('ok')]
   U=[j for j in order_ if E_(('U',j),cands[j][1],qb2)['ok']]
   for i in F:
    for j in U:
     if i==j:continue
     if E_(('Rb',i,j),cands[i][1],cands[j][1])['ok']:
      path=list(rp)+cache[('F',i)]['path'][1:]+cache[('D',i)]['path'][1:]+cache[('Rb',i,j)]['path'][1:]+cache[('U',j)]['path'][1:]+pp_[::-1][1:];how=f'direct carry {i} refold@b {j}';break
    if path:break
  if path is None and cands:
   # RRT fallbacks targeted at the missing link (budget Bd each):
   # (a) re-fold at spot b from a fold-ok carry to an unfold-ok carry,
   # (b) unfold from a fold-ok carry, (c) fold to an unfold-ok carry (+ drive).
   F=[i for i in order_ if cache.get(('F',i),{}).get('ok') and cache.get(('D',i),{}).get('ok')]
   U=[j for j in order_ if cache.get(('U',j),{}).get('ok')]
   tries=[('a',i,j) for i in F[:2] for j in U[:2] if i!=j]+[('b',i,None) for i in F[:1]]+[('c',None,j) for j in U[:1]]
   for kind_,i,j in tries:
    if kind_=='a':
     r=plan_swept(ch,cands[i][1],cands[j][1],Bd,seed=650+k+7*i+j,mass=M);cache[('rrt_refold_b',i,j)]=r
     if r['ok']:path=list(rp)+cache[('F',i)]['path'][1:]+cache[('D',i)]['path'][1:]+r['path'][1:]+cache[('U',j)]['path'][1:]+pp_[::-1][1:];how=f'carry {i}, rrt refold@b, carry {j}';break
    elif kind_=='b':
     r=plan_swept(ch,cands[i][1],qb2,Bd,stages=[cands[i][1]],seed=600+k,mass=M);cache[('rrt_unfold',i)]=r
     if r['ok']:path=list(rp)+cache[('F',i)]['path'][1:]+cache[('D',i)]['path'][1:]+r['path'][1:]+pp_[::-1][1:];how=f'carry {i}, rrt unfold';break
    else:
     if not ch.check(cands[j][0],mass=M)['ok']:continue
     dj=E_(('D',j),cands[j][0],cands[j][1])
     if not dj['ok']:continue
     r=plan_swept(ch,qa2,cands[j][0],Bd,stages=[cands[j][0]],seed=500+k,mass=M);cache[('rrt_fold',j)]=r
     if r['ok']:path=list(rp)+r['path'][1:]+dj['path'][1:]+cache[('U',j)]['path'][1:]+pp_[::-1][1:];how=f'rrt fold, carry {j}';break
  out.update(ok=path is not None,strategy=how,path=path,candidates=len(cands),
   steps={str(x):dict(ok=r['ok'],method=r.get('method'),reason=r.get('reason'),nodes=r.get('nodes')) for x,r in cache.items()},
   ends=dict(qa2=qa2.tolist(),qb2=qb2.tolist(),cands=[[a.tolist(),b.tolist()] for a,b in cands]))
 else:out.update(ok=False,carry_hits=cr['hits'][:4])
 out['elapsed_s']=time.monotonic()-beg
 save(f'results/chain_{preset}/C{k}.json',out);print(preset,'C',k,out['ok'],out.get('strategy'),'cands',out.get('candidates'),{x:out.get(x) for x in ('retreat_ok','preapproach_ok')},flush=True)
def normalize(preset):
 """Shift each later group's whole path by 2*pi*n per arm joint (identical
 geometry, still inside joint limits) to start nearest the previous group's end."""
 names=['GT1','GT2','GT3','GT4'] if config(preset).get('r11_tomato') else ['G1','G2','G3','G4S' if config(preset).get('slicer') else 'G4'];ch,_=checker(preset,'carrot');m=ch.m
 prev=np.array([s_ for s_ in load(f'results/chain_{preset}/{names[0]}.json')['segments'] if s_.get('path')][-1]['path'][-1])
 for nm in names[1:]:
  G=load(f'results/chain_{preset}/{nm}.json');segs=[s_ for s_ in G['segments'] if s_.get('path')]
  allq=np.array([q for s_ in segs for q in s_['path']]);shift=np.zeros(m.nq)
  for j in ch.arm_ids:
   lo,hi=m.jnt_range[m.jnt_qposadr.tolist().index(j)]
   ok=[n for n in (-2,-1,0,1,2) if allq[:,j].min()+2*np.pi*n>=lo-1e-9 and allq[:,j].max()+2*np.pi*n<=hi+1e-9]
   shift[j]=2*np.pi*min(ok,key=lambda n:abs(segs[0]['path'][0][j]+2*np.pi*n-prev[j]))
  for s_ in segs:s_['path']=(np.array(s_['path'])+shift).tolist()
  G['wrap_shift']=shift.tolist();save(f'results/chain_{preset}/{nm}.json',G)
  print(preset,nm,'shift',np.round(shift[ch.arm_ids]/(2*np.pi)).tolist(),flush=True)
  prev=np.array(segs[-1]['path'][-1])
def sequential(preset):
 """Solve the groups in order; each group's first IK is warm-started from and
 ranked by joint distance to the previous group's final state."""
 global REF
 names=['GT1','GT2','GT3','GT4'] if config(preset).get('r11_tomato') else ['G1','G2','G3','G4S' if config(preset).get('slicer') else 'G4']
 REF=None
 for nm in names:
  group(preset,nm);G=load(f'results/chain_{preset}/{nm}.json')
  segs=[s_ for s_ in G['segments'] if s_.get('path')]
  if not G['ok'] or not segs:print(preset,'sequential stop at',nm,flush=True);return
  REF=np.array(segs[-1]['path'][-1])
def assemble(preset):
 """Join groups and connections into one product path; verify continuity
 (each connection starts at the previous group's end and ends at the next
 group's start) and report size, base travel and a rough duration."""
 tom=config(preset).get('r11_tomato')
 names=['GT1','GT2','GT3','GT4'] if tom else ['G1','G2','G3','G4S' if config(preset).get('slicer') else 'G4']
 full=[];labels=[];report=[]
 for i,nm in enumerate(names):
  G=load(f'results/chain_{preset}/{nm}.json')
  for s_ in G['segments']:
   if s_.get('path'):
    if full:report.append((nm+':'+s_['stroke'],float(np.max(abs(np.array(full[-1])-np.array(s_['path'][0]))))))
    full+=s_['path'] if not full else s_['path'][1:];labels+=[nm+':'+s_['stroke']]*(len(s_['path'])-(0 if len(labels)==0 else 1))
  if i<len(names)-1:
   C=load(f'results/chain_{preset}/C{i+1}.json')
   if not C.get('ok'):print(preset,'connection',i+1,'missing');return
   report.append((f'C{i+1} start',float(np.max(abs(np.array(full[-1])-np.array(C['path'][0]))))))
   full+=C['path'][1:];labels+=[f'C{i+1}']*(len(C['path'])-1)
   nxt=[s_ for s_ in load(f'results/chain_{preset}/{names[i+1]}.json')['segments'] if s_.get('path')][0]['path'][0]
   report.append((f'C{i+1} end',float(np.max(abs(np.array(full[-1])-np.array(nxt))))))
 Q=np.array(full);steps=np.max(abs(np.diff(Q,axis=0)),axis=1)
 base=float(np.sum(abs(np.diff(Q[:,0]))));arm=float(np.sum(np.max(abs(np.diff(Q[:,3:9],axis=0)),axis=1)))
 out=dict(preset=preset,states=len(full),joins=report,max_join_gap=max(g for _,g in report),max_step_rad_or_m=float(steps.max()),base_travel_m=base,arm_joint_travel_rad=arm,
  rough_duration_s=arm/0.8+base/0.25,assumption='arm limited to 0.8 rad/s on the leading joint, base 0.25 m/s, no dwell/process time',path=full,labels=labels)
 save(f'results/chain_{preset}/full.json',out)
 print(preset,'states',len(full),'max join gap',round(out['max_join_gap'],9),'max step',round(out['max_step_rad_or_m'],4),'base m',round(base,3),'arm rad',round(arm,2),'~s',round(out['rough_duration_s']),flush=True)
if __name__=='__main__':
 preset,mode=sys.argv[1],sys.argv[2]
 if mode=='A':assemble(preset)
 elif mode=='SEQ':sequential(preset)
 elif mode=='N':normalize(preset)
 elif mode.startswith('G'):
  # SEQREF=1: re-run one group keeping the IK branch of the previous group's end (as in SEQ)
  if os.environ.get('SEQREF'):
   names=['GT1','GT2','GT3','GT4'] if config(preset).get('r11_tomato') else ['G1','G2','G3','G4S' if config(preset).get('slicer') else 'G4']
   i_=names.index(mode)
   if i_>0:REF=np.array([s_ for s_ in load(f'results/chain_{preset}/{names[i_-1]}.json')['segments'] if s_.get('path')][-1]['path'][-1])
  group(preset,mode)
 else:connection(preset,int(mode[1:]))
