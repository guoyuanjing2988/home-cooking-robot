"""R19 #2 (FR5): carry a checked chain of one FR5 option over to the same arm with the gripper further out on the
flange (fr5_j6_pgc -> fr5_j6_pgc_sp20, +20 mm adapter along the flange axis). New file; nothing shared is edited.

Method (IK re-targeting of a checked path, the object path kept exactly):
 - every stored state of the source play, and of each grasp approach / release retreat, gives the TCP pose the
   SOURCE arm had there. The two options differ only by arms.py tool_spacer_m (the gripper is moved over unchanged,
   at +spacer along the flange z axis), so at the same q: TCP_source = TCP_target - d_spacer * z_flange (asserted
   below: every other field of the two arms.ARMS entries is identical);
 - the target arm is solved to that TCP pose by IK continuation from the previous re-targeted state, the cart fixed
   at the stored value (r17chain.solve_to: bounded least squares inside the joint ranges);
 - so the held object, the gripper and the cart follow EXACTLY the source chain's checked path (its keyframes,
   pieces, joins, shuffles and approaches); only the arm links move (the wrist is pulled back along the tool axis);
 - each state is then checked with r17chain's planning check (Checker.check full, unchanged gates); the result is an
   ordinary chain json (play + approach_qs) that must pass r19pot_check.py / r19fr5_check.py (<= 4 mm) like any other.
Accepted per state: TCP within POSE_MM (default 0.5 mm) and 0.2 deg of the source TCP, largest joint step <= 10 deg
(r17chain follow()'s rule), joint ranges by construction.
python r19fr5_retarget.py SRC=<chain json> ARM=fr5_j6_pgc_sp20 [SPX= SPY= RACK=keyed] PY=.15 [TAG=..]
 -> results/r19/fr5/chain_<act>_s<sign>_<TAG>_<arm>.json"""
import sys,os,json,time
sys.path.insert(0,'.')
import numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
import kitchen19pot as P
LAYER=P.install_kv(KV)
SRC=json.load(open(KV['SRC'],encoding='utf-8'))
import arms
ARM=KV['ARM'];SARM=SRC['arm']
_a={k:v for k,v in arms.ARMS[ARM].items() if k not in ('name','tool_spacer_m')};_b={k:v for k,v in arms.ARMS[SARM].items() if k not in ('name','tool_spacer_m')}
assert _a==_b,('the two arm options differ in more than the spacer',ARM,SARM)
DSP=arms.ARMS[ARM].get('tool_spacer_m',0.)-arms.ARMS[SARM].get('tool_spacer_m',0.)
POSE_MM=float(KV.get('POSE_MM',.5))
src=open('r17chain.py',encoding='utf-8').read();cut=src.index('t0=time.monotonic();pieces={}')
sys.argv=[sys.argv[0],f"ACT={SRC['act']}",f"SIGN={SRC['grasp_sense']}",f'ARM={ARM}']+[f'{k}={KV[k]}' for k in ('SPX','SPY','PY') if k in KV]
g={'__name__':'r17chain_fr5','__file__':os.path.abspath('r17chain.py')}
exec(compile(src[:cut],'r17chain.py','exec'),g)
ch,sid=g['ch'],g['sid'];K=g['K']
def src_tcp(c,q):
 """The source arm's TCP at q (computed on the target model: minus the spacer difference along the flange z)."""
 c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d);att=c.m.site('R_attachment_site').id
 return c.d.site_xpos[sid]-DSP*c.d.site_xmat[att].reshape(3,3)[:,2],c.d.site_xmat[sid].reshape(3,3).copy()
def wrap(dq):return (dq+np.pi)%(2*np.pi)-np.pi
def retarget(c,Q,label):
 Q=np.array(Q,float);out=[];rows=[];prev=None
 for i,qs in enumerate(Q):
  pt_,Rt_=src_tcp(c,qs)
  seed=qs.copy() if prev is None else prev.copy();seed[0]=qs[0];seed[-2:]=qs[-2:]
  q,pe,re,dq=g['solve_to'](c,seed,pt_,Rt_)
  if pe>POSE_MM/1000 or re>np.radians(.2):   # retry from the source state itself (a stored join / 2pi relabel)
   s2=qs.copy();q2,pe2,re2,dq2=g['solve_to'](c,s2,pt_,Rt_)
   if pe2+np.radians(1)*re2<pe+np.radians(1)*re:q,pe,re=q2,pe2,re2
  step=float(np.degrees(np.max(abs(q[3:9]-prev[3:9])))) if prev is not None else 0.
  hits,rmin=g['state'](c,q,True)
  rows.append(dict(i=i,pose_mm=round(pe*1000,3),rot_deg=round(float(np.degrees(re)),3),step_deg=round(step,2),dev_deg=round(float(np.degrees(np.max(abs(wrap(q[3:9]-qs[3:9]))))),2),
   reserve_mm=None if rmin is None else round(rmin,2),hits=[h['pair'] for h in hits][:3]))
  out.append(q.copy());prev=q.copy()
 bad=[r for r in rows if r['pose_mm']>POSE_MM or r['rot_deg']>.2 or r['step_deg']>10 or r['hits']]
 print(label,len(rows),'states; bad',len(bad),'max pose %.3f mm, rot %.3f deg, step %.2f deg, dev from source %.2f deg, min reserve %s mm'%(
  max(r['pose_mm'] for r in rows),max(r['rot_deg'] for r in rows),max(r['step_deg'] for r in rows),max(r['dev_deg'] for r in rows),
  min((r['reserve_mm'] for r in rows if r['reserve_mm'] is not None),default=None)),flush=True)
 for r in bad[:12]:print('  bad',r,flush=True)
 return out,rows,bad
t0=time.monotonic()
play,prow,pbad=retarget(ch,SRC['play'],'play')
aqs=[];arow=[];abad=[]
for (k,world),qs in zip(g['GR'],SRC['approach_qs']):
 key=json.dumps(world,sort_keys=True)
 if key not in g['_empty']:g['_empty'][key]=g['model'](world)
 o,r_,b_=retarget(g['_empty'][key],qs,f'approach kf {k}');aqs.append([q.tolist() for q in o]);arow.append(r_);abad+=b_
# held load on the target arm, every play state (r17chain load(): object mass at its CoM, gravity torque ratios, PGC moment)
OBJ=SRC['obj'];m,d=ch.m,ch.d;kf0=g['KF'][0];pt0,Rt0=K.tcp_pose(OBJ,kf0['R'],kf0['p'],SRC['grasp_sense'])
parts=g['MASS'][OBJ];mass=sum(m_ for m_,_ in parts);com_o=sum(m_*c for m_,c in parts)/mass if parts else np.zeros(3);o_t=Rt0.T@(kf0['p']+kf0['R']@com_o-pt0)
jr=0.;pm=0.
if parts:
 for q in play:
  d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d);com=d.site_xpos[sid]+d.site_xmat[sid].reshape(3,3)@o_t
  bid=m.site_bodyid[sid];jp=np.zeros((3,m.nv));jr_=jp.copy();mujoco.mj_jac(m,d,jp,jr_,com,bid)
  tau=d.qfrc_bias-jp.T@np.array([0,0,-mass*9.81]);jr=max(jr,max(float(abs(tau[ch.da[n]])/v) for n,v in ch.env.items()))
  pm=max(pm,float(np.linalg.norm(np.cross(com-d.site_xpos[sid],[0,0,-mass*9.81]))))
ok=not pbad and not abad
res={k:v for k,v in SRC.items() if k not in ('play','approach_qs','r19pot','loads','pieces','tries','pieces_new')}
res.update(arm=ARM,ok=ok,play=[q.tolist() for q in play],approach_qs=aqs,max_joint_ratio=round(jr,3),max_pgc_moment_Nm=round(pm,2),
 time_s=SRC.get('time_s'),r19fr5=dict(method=__doc__,source=KV['SRC'],source_arm=SARM,spacer_diff_m=DSP,layer=LAYER,argv=sys.argv[1:],
 play_states=len(play),play_bad=len(pbad),approach_bad=len(abad),max_pose_mm=max(r['pose_mm'] for r in prow),max_rot_deg=max(r['rot_deg'] for r in prow),
 max_step_deg=max(r['step_deg'] for r in prow),max_dev_from_source_deg=max(r['dev_deg'] for r in prow),
 min_planning_reserve_mm=min((r['reserve_mm'] for r in prow if r['reserve_mm'] is not None),default=None),bad=(pbad+abad)[:40],
 timing='time_s is the source chain\'s (same object path; the joint-speed term is checked by the max step ratio below)',
 elapsed_s=round(time.monotonic()-t0)))
P0=np.array(SRC['play'],float);P1=np.array(play);s0=np.max(abs(np.diff(P0[:,3:9],axis=0)),axis=1);s1=np.max(abs(np.diff(P1[:,3:9],axis=0)),axis=1)
res['r19fr5']['max_joint_step_ratio_vs_source']=round(float(np.max(np.where(s0>np.radians(.2),s1/np.maximum(s0,1e-9),1.))),3)
os.makedirs('results/r19/fr5',exist_ok=True)
fn=f"results/r19/fr5/chain_{SRC['act']}_s{SRC['grasp_sense']:+d}"+('_'+KV['TAG'] if 'TAG' in KV else '')+arms.tag(ARM)+'.json'
assert not os.path.exists(fn) or KV.get('OVERWRITE')=='1',('exists, not overwritten',fn)
json.dump(res,open(fn,'w'),default=float);print(fn,'ok',ok,'elapsed',res['r19fr5']['elapsed_s'],'s',json.dumps({k:v for k,v in res['r19fr5'].items() if k not in ('method','bad','layer')},default=float))
