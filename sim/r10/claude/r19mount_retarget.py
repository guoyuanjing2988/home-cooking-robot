"""R19 #42: carry a CHECKED chain over to a mount option by IK re-targeting: the object path is kept EXACTLY, only the
arm links move (the method of r19fr5_retarget.py, R19_FR5.md 1.1, for a general flange -> TCP change). New file.

Why: the question of #42 is whether the existing task-space keyframes (and the certified object paths between them)
still work when the gripper sits on a buildable bracket. A re-target answers it directly: every stored state of the
source play and of each grasp approach / release retreat gives the TCP pose (site R_prep) the SOURCE arm option had
there; the TARGET option (same arm, other mount) is solved to that pose.

KIND=chain (r17chain.py chains: wok, plate 2, lid, spider, spatula, lever), r17chain.py executed from its source up to
its planning loop (as r19fr5_retarget.py / r19pot_chain.py; with the kitchen19pot layer RACK= SPX= SPY=, and WINDOW=1 the
declared lid rack window in the checker, as r19pot_chain.py), with the chain's own r17chain options given on the command
line (ACT SIGN GTILT L2X SINKC SPATREST SPATELEV SPATROLL TOOLS_OFF PY ...: they set the held object's grasp and the
scene) and ARM=<target>:
 - source TCP at a state q = flange(q) . T_ft(source option): the flange pose is the same on both models (same arm;
   asserted at the stored states), T_ft is measured once on a model built with the source option;
 - play start: the source state itself, plus up to NSTART collision-aware solver starts at that pose with the cart
   fixed (solver.solve, 1 seed); each is continued over the whole play with the fast check; the one with the fewest
   failing states is kept (as r19fr5prep_retarget.py);
 - IK continuation (r17chain solve_to: bounded least squares inside the joint ranges) from the previous state, cart and
   jaws at the stored values; a failed solve retries from the source state; joint labels nearest the previous state;
 - each approach starts from the re-targeted play state nearest (in the source) to its first state;
 - every kept state gets r17chain's planning check (Checker.check full: 10 mm robot-environment, 5 mm gripper /
   held-environment, self, ranges). Accepted per state: TCP within POSE_MM (0.5 mm) / 0.2 deg of the source, joint
   step <= 10 deg, no hits. A pass is an ordinary chain json and must still pass the <= 4 mm re-check
   (r19mount_check.py).
KIND=prep (r19prepchain.py sets): r19fr5prep_retarget.py executed unchanged from its source (it is already general:
the source TCP from a model built with the source arm), only its output written to results/r19/mount/; CHAINSRC=
r19prep4chain.py | r19prep5_chain.py for the step-4 / step-5 (T2L) sets (copies of r19prepchain.py with the same names).
python r19mount_retarget.py SRC=<chain json> ARM=<target> [KIND=chain|prep] <r17chain options> [RACK=keyed SPX= SPY=]
       [WINDOW=1] [NSTART=6] [TAG=rt]   -> results/r19/mount/chain_<act>_s<sign>_<TAG>_<arm>.json (prep: chain_<act>_<TAG>_<arm>.json)
python r19mount_retarget.py KIND=prep [CHAINSRC=r19prep5_chain.py] SRC=<prep chain json> ARM=<target> [TAG=rt]"""
import sys,os,json,time
sys.path.insert(0,'.')
import numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
if KV.get('KIND')=='prep':
 _s=open('r19fr5prep_retarget.py',encoding='utf-8').read();_a="os.makedirs('results/r19/fr5/prep',exist_ok=True)";_b='fn=f"results/r19/fr5/prep/chain_'
 assert _s.count(_a)==1 and _s.count(_b)==1
 _s=_s.replace(_a,"os.makedirs('results/r19/mount',exist_ok=True)").replace(_b,'fn=f"results/r19/mount/chain_')
 if KV.get('CHAINSRC'):   # the step-4 / step-5 sets: their runner (r19prep4chain.py / r19prep5_chain.py, copies of r19prepchain.py) instead
  _c="src=open('r19prepchain.py',encoding='utf-8').read()";_d="g={'__name__':'r19prepchain_fr5rt','__file__':os.path.abspath('r19prepchain.py')}";_e="exec(compile(src[:cut],'r19prepchain.py','exec'),g)"
  assert _s.count(_c)==1 and _s.count(_d)==1 and _s.count(_e)==1
  _s=_s.replace(_c,_c.replace('r19prepchain.py',KV['CHAINSRC'])).replace(_d,_d.replace('r19prepchain.py',KV['CHAINSRC'])).replace(_e,_e.replace('r19prepchain.py',KV['CHAINSRC']))
 sys.argv=[sys.argv[0]]+[a for a in sys.argv[1:] if not a.startswith(('KIND=','CHAINSRC='))]
 exec(compile(_s,'r19fr5prep_retarget.py','exec'));sys.exit(0)
SRC_FN=KV['SRC'];SRC=json.load(open(SRC_FN,encoding='utf-8'));ARM=KV['ARM'];SARM=SRC.get('arm','ur5e');TAG=KV.get('TAG','rt')
POSE_MM=float(KV.get('POSE_MM',.5));NSTART=int(KV.get('NSTART',6))
import kitchen19pot as P
LAYER=P.install_kv(KV)
import checker as _chk
WIN={'W':None}
_orig_perm=_chk.Checker.permissions
def _perm(self,kind):
 allowed=_orig_perm(self,kind)
 if WIN['W']:
  sid_=self.m.site('R_prep').id;add,n=P.allowed_pairs(WIN['W'],self.gnames,self.d.site_xpos[sid_],self.d.site_xmat[sid_].reshape(3,3))
  if n:allowed=set(allowed)|add
 return allowed
if KV.get('WINDOW')=='1':_chk.Checker.permissions=_perm
src=open('r17chain.py',encoding='utf-8').read();cut=src.index('t0=time.monotonic();pieces={}')
PASS=[a for a in sys.argv[1:] if '=' in a and a.split('=',1)[0] not in ('SRC','KIND','TAG','POSE_MM','NSTART','RACK','WINDOW','POTWIN','ARM','OVERWRITE','SEEDUR')]
sys.argv=[sys.argv[0]]+PASS+[f'ARM={ARM}']
g={'__name__':'r17chain_mount','__file__':os.path.abspath('r17chain.py')}
exec(compile(src[:cut],'r17chain.py','exec'),g)
if KV.get('WINDOW')=='1':WIN['W']=P.windows(g['SIGN'],rack=KV.get('RACK')=='keyed',pot=KV.get('POTWIN')=='1')
import arms
assert g['ACT']==SRC['act'] and g['SIGN']==SRC['grasp_sense'],('ACT / SIGN must be the source chain\'s',g['ACT'],g['SIGN'])
ch,sid,K,OBJ,SIGN=g['ch'],g['sid'],g['K'],g['OBJ'],g['SIGN'];ids=list(g['ids']);lo,hi_=g['lo'],g['hi_']
c_src=g['model'](dict(g['K17'].held_cfg(OBJ,SIGN),arm=SARM))
def frames(c,q):
 c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d);a=c.m.site('R_attachment_site').id;s=c.m.site('R_prep').id
 Xf=np.eye(4);Xf[:3,:3]=c.d.site_xmat[a].reshape(3,3);Xf[:3,3]=c.d.site_xpos[a];Xt=np.eye(4);Xt[:3,:3]=c.d.site_xmat[s].reshape(3,3);Xt[:3,3]=c.d.site_xpos[s];return Xf,Xt
P0=np.array(SRC['play'],float);Xf0,Xt0=frames(c_src,P0[0]);T_src=np.linalg.inv(Xf0)@Xt0
for q in P0[::max(1,len(P0)//7)]:   # same arm on both models: the flange poses agree
 assert np.allclose(frames(c_src,q)[0],frames(ch,q)[0],atol=1e-9),'source and target arms differ (flange pose)'
 assert np.allclose(np.linalg.inv(frames(c_src,q)[0])@frames(c_src,q)[1],T_src,atol=1e-9)
Xf1,Xt1=frames(ch,P0[0]);T_tgt=np.linalg.inv(Xf1)@Xt1
from scipy.spatial.transform import Rotation
dT=np.linalg.inv(T_src)@T_tgt
def src_tcp(c,q):
 Xf,_=frames(c,q);X=Xf@T_src;return X[:3,3].copy(),X[:3,:3].copy()
def wrapq(q,prev):
 for k,j in enumerate(ids):
  c_=[q[j]+2*np.pi*m_ for m_ in (-2,-1,0,1,2) if lo[k]-1e-9<=q[j]+2*np.pi*m_<=hi_[k]+1e-9]
  if c_:q[j]=min(c_,key=lambda v:abs(v-prev[j]))
 return q
def follow(c,Q,q0,full,stop_after=None):
 out=[];rows=[];prev=None;nbad=0
 for i,qs in enumerate(np.array(Q,float)):
  pt_,Rt_=src_tcp(c,qs);seed=qs.copy();seed[ids]=(q0 if prev is None else prev)[ids]
  q,pe,re,_=g['solve_to'](c,seed,pt_,Rt_)
  if pe>POSE_MM/1000 or re>np.radians(.2):
   q2,pe2,re2,_=g['solve_to'](c,qs.copy(),pt_,Rt_)
   if pe2+re2<pe+re:q,pe,re=q2,pe2,re2
  if prev is not None:q=wrapq(q,prev)
  step=float(np.degrees(np.max(abs(q[ids]-prev[ids])))) if prev is not None else 0.
  hits,rmin=g['state'](c,q,full)
  bad=bool(hits) or pe>POSE_MM/1000 or re>np.radians(.2) or step>10
  rows.append(dict(i=i,pose_mm=round(pe*1000,3),rot_deg=round(float(np.degrees(re)),3),step_deg=round(step,2),dev_deg=round(float(np.degrees(np.max(abs((q[ids]-qs[ids]+np.pi)%(2*np.pi)-np.pi)))),2),
   reserve_mm=None if rmin is None else round(rmin,2),hits=[h['pair'] for h in hits][:3]))
  out.append(q.copy());prev=q.copy();nbad+=bad
  if stop_after is not None and nbad>stop_after:break
 return out,rows
isbad=lambda r:r['hits'] or r['pose_mm']>POSE_MM or r['rot_deg']>.2 or r['step_deg']>10
t0=time.monotonic()
pt0,Rt0=src_tcp(ch,P0[0])
starts=[('source state',P0[0].copy())]
if NSTART>0:
 t=dict(name=f'{OBJ}_rt',points=[list(pt0)]*2,held=None,kind='transfer',force=None,approach=list(Rt0[:,0]),cart_x=float(P0[0][0]),jaws=[tuple(SIGN*(g['KF'][0]['R']@K.OBJ[OBJ]['j']))],jaw_q=g['JAW_HELD'])
 try:
  r_=g['solve'](ch,pt0,list(Rt0[:,0]),target=t,seed=14);starts+=[(f'solver start {i} ({c_["reserve_mm"]:.1f} mm)',np.array(c_['q'],float)) for i,c_ in enumerate(r_['candidates'][:NSTART])]
 except Exception as e:print('solver starts failed',repr(e)[:200],flush=True)
screen=[]
for name,q0 in starts:
 qq=q0.copy();qq[0]=P0[0][0];qq[-2:]=P0[0][-2:]
 o,rw=follow(ch,P0,qq,False,stop_after=len(P0)//4)
 nb=sum(1 for x in rw if isbad(x))+(len(P0)-len(rw));first=next((x['i'] for x in rw if isbad(x)),None)
 screen.append(dict(start=name,bad_states=nb,first_bad=first,max_step_deg=max(x['step_deg'] for x in rw),q0=qq.tolist()))
 print('start',name,'bad',nb,'first bad',first,'max step %.1f'%screen[-1]['max_step_deg'],flush=True)
 if nb==0:break
best=min(screen,key=lambda s:(s['bad_states'],-(s['first_bad'] if s['first_bad'] is not None else 1e9)))
play,prow=follow(ch,P0,np.array(best['q0']),True)
pbad=[r for r in prow if isbad(r)]
print('play',len(prow),'states; bad',len(pbad),'start',best['start'],'max pose %.3f mm, step %.2f deg, dev %.1f deg, min reserve %s mm'%(max(r['pose_mm'] for r in prow),max(r['step_deg'] for r in prow),max(r['dev_deg'] for r in prow),min((r['reserve_mm'] for r in prow if r['reserve_mm'] is not None),default=None)),flush=True)
for r in pbad[:10]:print('  bad',r,flush=True)
aqs=[];arows=[];abad=[]
for (k,world),AQ in zip(g['GR'],SRC['approach_qs']):
 if not AQ:aqs.append(AQ);arows.append([]);continue
 key=json.dumps(world,sort_keys=True)
 if key not in g['_empty']:g['_empty'][key]=g['model'](world)
 c=g['_empty'][key];A0=np.array(AQ[0],float);j=int(np.argmin([np.max(abs(A0[ids]-x[ids]))+abs(A0[0]-x[0]) for x in P0]))
 o,rw=follow(c,AQ,play[j],True);aqs.append([q.tolist() for q in o]);arows.append(rw);b=[dict(approach=k,**r) for r in rw if isbad(r)];abad+=b
 print('approach kf',k,len(rw),'states; bad',len(b),'min reserve',min((r['reserve_mm'] for r in rw if r['reserve_mm'] is not None),default=None),flush=True)
# held load on the target arm at every play state (as r19fr5_retarget.py: object mass at its CoM; gravity torque ratios; PGC moment)
m,d=ch.m,ch.d;kf0=g['KF'][0];pk0,Rk0=K.tcp_pose(OBJ,kf0['R'],kf0['p'],SIGN)
parts=g['MASS'][OBJ];mass=sum(m_ for m_,_ in parts);com_o=sum(m_*c_ for m_,c_ in parts)/mass if parts else np.zeros(3);o_t=Rk0.T@(kf0['p']+kf0['R']@com_o-pk0)
jr=0.;pm=0.
if parts:
 for q in play:
  d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);com=d.site_xpos[sid]+d.site_xmat[sid].reshape(3,3)@o_t
  bid=m.site_bodyid[sid];jp=np.zeros((3,m.nv));jr_=jp.copy();mujoco.mj_jac(m,d,jp,jr_,com,bid)
  tau=d.qfrc_bias-jp.T@np.array([0,0,-mass*9.81]);jr=max(jr,max(float(abs(tau[ch.da[n]])/v) for n,v in ch.env.items()))
  pm=max(pm,float(np.linalg.norm(np.cross(com-d.site_xpos[sid],[0,0,-mass*9.81]))))
ok=not pbad and not abad
P1=np.array(play);s0=np.max(abs(np.diff(P0[:,3:9],axis=0)),axis=1);s1=np.max(abs(np.diff(P1[:,3:9],axis=0)),axis=1)
res={k:v for k,v in SRC.items() if k not in ('play','approach_qs','r19pot','loads','pieces','tries','pieces_new','adopted','adopted_from')}
res.update(arm=ARM,ok=ok,play=[q.tolist() for q in play],approach_qs=aqs,max_joint_ratio=round(jr,3),max_pgc_moment_Nm=round(pm,2),time_s=SRC.get('time_s'),
 time_s_upper_E=round((SRC.get('time_s') or 0.)+float(np.sum(np.maximum(0.,s1-s0)))*180/np.pi/g['QW'],1),
 r19mount=dict(method=__doc__,source=SRC_FN,source_arm=SARM,layer=LAYER,window=KV.get('WINDOW')=='1',argv=PASS,
  tcp_change_in_tool_frame=dict(dp_mm=np.round(dT[:3,3]*1e3,2).tolist(),rot_deg=round(float(np.degrees(np.linalg.norm(Rotation.from_matrix(dT[:3,:3]).as_rotvec()))),2)),
  start=best['start'],start_screen=[{k:v for k,v in s.items() if k!='q0'} for s in screen],play_states=len(play),play_bad=len(pbad),approach_bad=len(abad),
  max_pose_mm=max(r['pose_mm'] for r in prow),max_rot_deg=max(r['rot_deg'] for r in prow),max_step_deg=max(r['step_deg'] for r in prow),max_dev_from_source_deg=max(r['dev_deg'] for r in prow),
  min_planning_reserve_mm=min((r['reserve_mm'] for r in prow if r['reserve_mm'] is not None),default=None),
  approach_min_reserve_mm=[min((r['reserve_mm'] for r in rw if r['reserve_mm'] is not None),default=None) for rw in arows],
  max_joint_step_ratio_vs_source=round(float(np.max(np.where(s0>np.radians(.2),s1/np.maximum(s0,1e-9),1.))),3),bad=(pbad+abad)[:40],
  timing="time_s is the source chain's (same object path); time_s_upper_E adds every joint-bound step that is slower on the target (sum of max(0, dq_target - dq_source) / the joint cap)",
  elapsed_s=round(time.monotonic()-t0)))
os.makedirs('results/r19/mount',exist_ok=True)
fn=f"results/r19/mount/chain_{SRC['act']}_s{SRC['grasp_sense']:+d}_{TAG}{arms.tag(ARM)}.json"
assert not os.path.exists(fn) or KV.get('OVERWRITE')=='1',('exists, not overwritten',fn)
json.dump(res,open(fn,'w'),default=float)
print(fn,'ok',ok,'elapsed',res['r19mount']['elapsed_s'],'s',json.dumps({k:v for k,v in res['r19mount'].items() if k not in ('method','bad','layer','start_screen')},default=float))
