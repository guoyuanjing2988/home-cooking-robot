"""R19 #2 (FR5) prep sets: IK re-target of a checked UR5e prep chain (r19prepchain.py format) to an FR5 option.
The method of r19fr5_retarget.py (R19_FR5.md 1.1), here across different arm kinematics. New file; nothing shared is
edited (r19prepchain.py is executed from its source up to its planning loop, unchanged, as r19fr5_retarget.py does
with r17chain.py).
Method:
 - r19prepchain.py runs with the SOURCE chain's options and ARM=<target>, which gives the set's held object, keyframes,
   union scene, grasp worlds, solve_to and the planning check exactly as r19prepchain uses them. The scene and grasp
   worlds stored in the SOURCE json are used (the current code's are compared and reported);
 - every stored state of the source play and of each grasp approach / release retreat gives the TCP pose (site
   R_prep) the SOURCE arm had there, computed on a model of the same scene built with the source arm;
 - the target arm is solved to that pose by IK continuation from the previous re-targeted state (r19prepchain
   solve_to: bounded least squares inside the joint ranges), the cart, the jaws and every non-arm joint at the
   stored value;
 - start of the play: the source state mapped through arms.py mount yaw / gripper clocking (as SEEDUR) plus up to
   NSTART collision-aware solver starts at that pose with the cart fixed (solver.solve, 1 seed); each is continued
   over the whole play with the fast check; the one with the fewest failing states (then the largest step-free run)
   is kept and fully checked at every state;
 - each approach starts from the re-targeted play state that is nearest (in the source) to its first state;
 - every kept state gets the full planning check (Checker.check full: 10 mm robot-environment, 5 mm gripper/held-
   environment, ranges; in a food approach the r19prepchain contact window, never touching).
So the held object, the gripper and the cart follow EXACTLY the certified UR5e path; only the arm links differ.
Accepted per state: TCP within POSE_MM (0.5 mm) and 0.2 deg of the source, joint step <= 10 deg, no hits. A pass is
an ordinary chain json and must still pass r19prep_verify.py (<= 4 mm). A failure is reported state by state:
the failing pair, its exact clearance (distance.py lower bound) against the gate, and where (between which keyframes).
python r19fr5prep_retarget.py SRC=<UR5e chain json> ARM=fr5_j6_pgc_sp20 [NSTART=8] [TAG=rt]
 -> results/r19/fr5/prep/chain_<act>_<TAG>_<arm>.json"""
import sys,os,json,time
sys.path.insert(0,'.')
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
SRC_FN=KV['SRC'];SRC=json.load(open(SRC_FN,encoding='utf-8'));ARM=KV['ARM'];SARM=SRC['arm'];TAG=KV.get('TAG','rt')
POSE_MM=float(KV.get('POSE_MM',.5));NSTART=int(KV.get('NSTART',8))
src=open('r19prepchain.py',encoding='utf-8').read();cut=src.index('t0=time.monotonic();pieces={}')
sys.argv=[sys.argv[0]]+[a for a in SRC['argv'] if '=' in a and not a.startswith(('ARM=','TAG='))]+[f'ARM={ARM}']
g={'__name__':'r19prepchain_fr5rt','__file__':os.path.abspath('r19prepchain.py')}
exec(compile(src[:cut],'r19prepchain.py','exec'),g)
import arms
K,K17,OBJ,SIGN=g['K'],g['K17'],g['OBJ'],g['SIGN'];ids=list(g['ids']);lo,hi_=g['lo'],g['hi_'];QW=g['QW']
J=lambda o:json.loads(json.dumps(o,sort_keys=True))
cur_scene=J(g['SCENE']);same_scene=json.dumps(cur_scene,sort_keys=True)==json.dumps(J(SRC['scene']),sort_keys=True)
same_grasps=[json.dumps(J(w),sort_keys=True) for _,w,_ in g['GR']]==[json.dumps(J(x['world']),sort_keys=True) for x in SRC['grasps']]
same_kf=len(g['KF'])==len(SRC['keyframes']) and all(np.allclose(a['p'],b['p'],atol=1e-9) and np.allclose(a['R'],b['R'],atol=1e-9) for a,b in zip(g['KF'],SRC['keyframes']))
print('current code vs source: scene',same_scene,'grasp worlds',same_grasps,'keyframes',same_kf,'arm ids',ids,flush=True)
g['P3'].ensure([SRC['obj']]+[o[0] for o in (SRC['scene'].get('r19') or {}).get('objs',[])]+[o[0] for x in SRC['grasps'] for o in (x['world'] or {}).get('objs',[])])   # pitched variants named in the source (as r19prep_verify.py)
USE=KV.get('SCENE','src')   # src: the scene and grasp worlds stored in the source (default) | current: the current code's (today's layout)
if USE=='current':SRC=dict(SRC,scene=cur_scene,grasps=[dict(kf=k,world=J(w),object_in_world=inw) for k,w,inw in g['GR']])
g['SCENE']=SRC['scene']   # model() reads SCENE at call time
c_play=g['model'](K17.held_cfg(OBJ,SIGN));c_ur=g['model'](dict(K17.held_cfg(OBJ,SIGN),arm=SARM))
assert c_play.m.nq==c_ur.m.nq and c_play.m.site('R_prep').id==g['sid'],'qpos layout / site differs'
def tcp(c,q):
 c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d);s=c.m.site('R_prep').id
 return c.d.site_xpos[s].copy(),c.d.site_xmat[s].reshape(3,3).copy()
def mapped(qs):
 """The source state through arms.py mount yaw / clocking (r17chain ur_seeds), each joint wrapped into range."""
 q=np.array(qs,float);q[3]-=np.radians(arms.ARMS[ARM].get('mount_yaw_deg',0.)-arms.ARMS[SARM].get('mount_yaw_deg',0.));q[8]-=np.radians(arms.ARMS[ARM].get('clock_deg',0.)-arms.ARMS[SARM].get('clock_deg',0.))
 for j in range(6):
  c_=[q[3+j]+i*2*np.pi for i in (-2,-1,0,1,2) if lo[j]-1e-9<=q[3+j]+i*2*np.pi<=hi_[j]+1e-9]
  if c_:q[3+j]=min(c_,key=abs)
 return q
def hit_rows(c,q,hits,win=None):
 """Each failing pair with its exact clearance (distance.py bounds) and gate."""
 c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d);out=[]
 for h in hits[:4]:
  p=h['pair']
  if p[0] not in c.gnames or p[1] not in c.gnames:out.append(dict(pair=p));continue
  a,b=c.gnames.index(p[0]),c.gnames.index(p[1]);req=c.required(c,a,b);bd=c.bounds.pair(a,b)
  out.append(dict(pair=p,clearance_mm=round(bd['lower_m']*1000,2),upper_mm=round(bd['upper_m']*1000,2),gate_mm=None if req is None else round(req[0]*1000,1),
   short_mm=None if req is None else round(req[0]*1000-bd['lower_m']*1000,2),literal_only=bool(bd['lower_m']>1e-6 and bd['lower_m']>=(req[0] if req else 0.)-1e-6)))   # True: the exact bound clears the gate, only MuJoCo's literal contact flags it
 return out
def follow(c,Q,q0,full,win=None,stop_after=None):
 """IK continuation of the target arm along the source states Q from q0. Rows per state; failing states listed."""
 out=[];rows=[];prev=None;nbad=0
 for i,qs in enumerate(np.array(Q,float)):
  pt_,Rt_=tcp(c_ur,qs);seed=qs.copy();seed[ids]=(q0 if prev is None else prev)[ids]
  q,pe,re,_=g['solve_to'](c,seed,pt_,Rt_)
  if pe>POSE_MM/1000 or re>np.radians(.2):   # retry from the mapped source state (a stored join / 2pi relabel)
   q2,pe2,re2,_=g['solve_to'](c,mapped(qs),pt_,Rt_)
   if pe2+re2<pe+re:q,pe,re=q2,pe2,re2
  if prev is not None:   # same pose, the joint label nearest the previous state inside the range (r19prep_verify.py unwrap)
   for k,j in enumerate(ids):q[j]=min([q[j]+2*np.pi*m for m in (-2,-1,0,1,2) if lo[k]-1e-9<=q[j]+2*np.pi*m<=hi_[k]+1e-9],key=lambda v:abs(v-prev[j]))
  step=float(np.degrees(np.max(abs(q[ids]-prev[ids])))) if prev is not None else 0.
  if full:
   r=c.check(q,full=True,mass=0.);hits=list(r['hits']);rmin=min((v['reserve_mm'] for cat,v in r['clearance'].items() if cat!='self'),default=None);smin=r['clearance'].get('self',{}).get('reserve_mm')
   if not r['ranges']:hits.append(dict(pair=['joint ranges','out of range']))
  else:hits,rmin=g['state'](c,q,False);smin=None
  if win:
   c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d)
   if min(c.bounds.pair(a,b)['upper_m'] for a in win[0] for b in win[1])<=1e-6:hits=hits+[dict(pair=['window food','touching'])]
  bad=bool(hits) or pe>POSE_MM/1000 or re>np.radians(.2) or step>10
  row=dict(i=i,pose_mm=round(pe*1000,3),rot_deg=round(float(np.degrees(re)),3),step_deg=round(step,2),src_step_deg=round(float(np.degrees(np.max(abs(qs[ids]-np.array(Q[i-1],float)[ids])))) if i else 0.,2),
   reserve_mm=None if rmin is None else round(rmin,2),self_mm=None if smin is None else round(smin,2),hits=[h['pair'] for h in hits][:3],cart=round(float(q[0]),3))
  if bad and full:row['detail']=hit_rows(c,q,[h for h in hits if 'pair' in h and h['pair'][0] in c.gnames])
  rows.append(row);out.append(q.copy());prev=q.copy();nbad+=bad
  if stop_after is not None and nbad>stop_after:break
 return out,rows
# ---- play: choose the start branch, then the full continuation ----
t0=time.monotonic();P=np.array(SRC['play'],float);pt0,Rt0=tcp(c_ur,P[0])
starts=[('mapped source state',mapped(P[0]))]
t=dict(name=f'{OBJ}_rt',points=[list(pt0)]*2,held=None,kind='transfer',force=None,approach=list(Rt0[:,0]),cart_x=float(P[0][0]),
 jaws=[tuple(SIGN*(np.array(SRC['keyframes'][0]['R'])@K.OBJ[OBJ]['j']))],jaw_q=g['JAW_HELD'])
r=g['solve'](c_play,pt0,list(Rt0[:,0]),target=t,seed=14);starts+=[(f'solver start {i} ({c_["reserve_mm"]:.1f} mm)',np.array(c_['q'],float)) for i,c_ in enumerate(r['candidates'][:NSTART])]
screen=[]
for name,q0 in starts:
 qq=q0.copy();qq[0]=P[0][0];qq[-2:]=P[0][-2:]
 o,rw=follow(c_play,P,qq,False)
 nb=sum(1 for x in rw if x['hits'] or x['pose_mm']>POSE_MM or x['rot_deg']>.2 or x['step_deg']>10);first=next((x['i'] for x in rw if x['hits'] or x['pose_mm']>POSE_MM or x['rot_deg']>.2 or x['step_deg']>10),None)
 screen.append(dict(start=name,bad_states=nb,first_bad=first,max_step_deg=max(x['step_deg'] for x in rw),q0=qq.tolist()))
 print('start',name,'bad',nb,'first bad',first,'max step %.1f'%screen[-1]['max_step_deg'],flush=True)
best=min(screen,key=lambda s:(s['bad_states'],-(s['first_bad'] if s['first_bad'] is not None else 1e9)))
play,prow=follow(c_play,P,np.array(best['q0']),True)
pbad=[x for x in prow if x['hits'] or x['pose_mm']>POSE_MM or x['rot_deg']>.2 or x['step_deg']>10]
print('play',len(prow),'states; bad',len(pbad),'start',best['start'],flush=True)
# ---- approaches (empty gripper, the object in its world; food window as r19prepchain.approach) ----
aqs=[];arows=[];abad=[]
for i,(gr,AQ) in enumerate(zip(SRC['grasps'],SRC.get('approach_qs') or [])):
 if not AQ:aqs.append(None);continue
 kf=SRC['keyframes'][gr['kf']];R_=np.array(kf['R']);p_=np.array(kf['p'])-[0,0,kf.get('seat',0.)]
 c=g['model'](dict(r19=gr['world']),(OBJ,R_.tolist(),p_.tolist()) if gr['object_in_world'] else None);win=None
 if gr['object_in_world'] and g['FOOD']:
  og=[k for k in range(c.m.ngeom) if c.m.geom(k).name==f'r19_{OBJ}'];fg=[k for k in range(c.m.ngeom) if c.m.geom(k).name.startswith(('R_finger_','R_gripper_'))]
  w={frozenset([c.m.geom(a).name,c.m.geom(b).name]) for a in og for b in fg};perm=c.permissions;c.permissions=lambda kind,perm=perm,w=w:set(perm(kind))|w;win=(og,fg)
 A0=np.array(AQ[0],float);j=int(np.argmin([np.max(abs(A0[ids]-x[ids]))+abs(A0[0]-x[0]) for x in P]))
 o,rw=follow(c,AQ,play[j],True,win);aqs.append([q.tolist() for q in o]);arows.append(rw)
 b=[x for x in rw if x['hits'] or x['pose_mm']>POSE_MM or x['rot_deg']>.2 or x['step_deg']>10];abad+=[dict(approach=i,**x) for x in b]
 print('approach',i,'kf',gr['kf'],len(rw),'states; bad',len(b),'min reserve',min((x['reserve_mm'] for x in rw if x['reserve_mm'] is not None),default=None),flush=True)
# ---- where: the keyframes around each failing play state (by the source TCP path) ----
kft=[g['K'].tcp_pose(OBJ,np.array(k['R']),np.array(k['p']),SIGN)[0] for k in SRC['keyframes']]
src_tcp=np.array([tcp(c_ur,q)[0] for q in P])
kfi=[int(np.argmin(np.linalg.norm(src_tcp-p,axis=1))) for p in kft]   # nearest play index of each keyframe (order of the play)
def where(i):
 before=[(kfi[k],k) for k in range(len(kfi)) if kfi[k]<=i];after=[(kfi[k],k) for k in range(len(kfi)) if kfi[k]>=i]
 a=max(before)[1] if before else None;b=min(after)[1] if after else None
 return dict(between=[SRC['keyframes'][a]['label'] if a is not None else None,SRC['keyframes'][b]['label'] if b is not None else None],tcp_m=np.round(src_tcp[i],3).tolist())
for x in pbad:x['where']=where(x['i'])
def runs(bad,rows_n):
 """Consecutive failing states grouped: index range, keyframes around it, pairs, worst shortfall against the gate, largest step."""
 out=[];cur=[]
 for x in bad:
  if cur and x['i']!=cur[-1]['i']+1:out.append(cur);cur=[]
  cur.append(x)
 if cur:out.append(cur)
 R_=[]
 for r_ in out:
  sh=[(d['short_mm'],d['pair'],d['clearance_mm'],d['gate_mm'],d['literal_only'],x['i']) for x in r_ for d in x.get('detail',[]) if d.get('short_mm') is not None]
  w=max(sh,key=lambda s:s[0]) if sh else None
  R_.append(dict(states=[r_[0]['i'],r_[-1]['i']],of=rows_n,n=len(r_),from_=r_[0].get('where'),to=r_[-1].get('where'),pairs=sorted({' / '.join(sorted(h)) for x in r_ for h in x['hits']}),
   worst=None if w is None else dict(short_mm=w[0],pair=w[1],clearance_mm=w[2],gate_mm=w[3],literal_only=w[4],state=w[5],where=where(w[5]) if 'where' in r_[0] else None),max_step_deg=max(x['step_deg'] for x in r_),
   max_src_step_deg=max(x['src_step_deg'] for x in r_)))
 return R_
prun=runs(pbad,len(prow));arun=[dict(approach=i,**r_) for i,rw in enumerate(arows) for r_ in runs([x for x in rw if x['hits'] or x['pose_mm']>POSE_MM or x['rot_deg']>.2 or x['step_deg']>10],len(rw))]
for r_ in prun+arun:print('RUN',json.dumps(r_,default=float)[:900],flush=True)
# ---- loads at the keyframe states (r19prepchain load(): kg and CoM per keyframe) and time ----
loads=[]
for k,ii in enumerate(kfi):
 if np.linalg.norm(src_tcp[ii]-kft[k])<.001:loads.append(g['load'](np.array(play[ii]),k))
dq_t=np.degrees(np.max(abs(np.diff(np.array(play)[:,ids],axis=0)),axis=1));dq_s=np.degrees(np.max(abs(np.diff(P[:,ids],axis=0)),axis=1))
extra_s=float(np.sum(np.maximum(0.,dq_t-dq_s))/QW)
ok=not pbad and not abad
res={k:v for k,v in SRC.items() if k not in ('play','approach_qs','loads','tries','pieces')}
res.update(arm=ARM,ok=ok,play=[q.tolist() for q in play],approach_qs=aqs,
 time_s=SRC.get('time_s'),time_s_upper_E=round(SRC.get('time_s',0.)+extra_s,1),
 max_joint_ratio=max((l_['max_joint_ratio'] for l_ in loads),default=None),max_pgc_moment_Nm=max((l_['pgc_moment_Nm'] for l_ in loads),default=None),loads=loads,
 r19fr5prep=dict(method=__doc__,source=SRC_FN,source_arm=SARM,argv=sys.argv[1:],scene_used=USE,current_code_same=dict(scene=same_scene,grasp_worlds=same_grasps,keyframes=same_kf),
  bad_runs_play=prun,bad_runs_approach=arun,
  start_screen=[{k:v for k,v in s.items() if k!='q0'} for s in screen],start=best['start'],
  play_states=len(play),play_bad=len(pbad),approach_bad=len(abad),max_pose_mm=max(x['pose_mm'] for x in prow),max_rot_deg=max(x['rot_deg'] for x in prow),
  max_step_deg=max(x['step_deg'] for x in prow),min_planning_reserve_mm=min((x['reserve_mm'] for x in prow if x['reserve_mm'] is not None),default=None),
  min_self_mm=min((x['self_mm'] for x in prow if x['self_mm'] is not None),default=None),
  approach_min_reserve_mm=[min((x['reserve_mm'] for x in rw if x['reserve_mm'] is not None),default=None) for rw in arows],
  bad=(pbad+abad)[:60],timing='time_s is the source chain\'s (same object path); time_s_upper_E adds every joint-bound step that is slower on the target (sum of max(0, dq_target - dq_source) / 60 deg/s)',
  elapsed_s=round(time.monotonic()-t0)))
os.makedirs('results/r19/fr5/prep',exist_ok=True)
fn=f"results/r19/fr5/prep/chain_{SRC['act']}_{TAG}{arms.tag(ARM)}.json"
assert not os.path.exists(fn) or KV.get('OVERWRITE')=='1',('exists, not overwritten',fn)
json.dump(res,open(fn,'w'),default=float)
print(fn,'ok',ok,'elapsed',res['r19fr5prep']['elapsed_s'],'s',json.dumps({k:v for k,v in res['r19fr5prep'].items() if k not in ('method','bad','start_screen')},default=float))
for x in (pbad+abad)[:25]:print('  bad',json.dumps(x,default=float)[:600])
