"""R19 #40 gap 1: the spatula hand-off into and out of the stored stir cycle (#3), built, re-checked at <= 4 mm and
stored, for ARM=ur5e_enc2_pgc and ARM=fr5_j6_pgc_sp20. New file; no shared file is changed.

Ends of the join (11-value states: cart x, base y, base yaw, q1..q6, jaws):
 - SPATULA_FETCH end = the adopted spatula chain's last play state ('stroke start#5'):
   UR5e results/r17/chain_spatula_s-1_r18roll-1.15_.30_ur5e_enc2_pgc.json, FR5 ..._fr5_j6_pgc_sp20.json.
   Its play is 2pi-unwrapped as r19hub.unwrapped() (the stored play jumps 2pi at the lane join) and, for the UR5e,
   relabelled by the hub roadmap's action shift for the spatula (results/r19/hub_py.15_ur5e_enc2_pgc/hubs.json:
   pan -1 turn), i.e. the labels a controller runs. The FR5 has no roadmap: unwrapped labels.
 - H_stir0 of the stored cycle (results/r19/stir/lib_stir_cycle_<arm>.json), with the per-joint 2pi relabel of the
   WHOLE cycle that is nearest to the spatula end while every certified cycle state stays in the joint ranges
   (r19stir_cycle.label_shift rule). A relabel is the same pose: geometry and certificate are unchanged; the
   range check is redone here on every certified state and on the geometry (2 ms grid).
 - Both ends hold the spatula at the SAME tool pose (the R15 stroke-0 start, blade 1 cm off the steel): only the
   cart (7.8 cm UR5e, 14.3 cm FR5) and the arm's posture differ. Does the spatula chain end moving? No: every stored
   law of the spatula chain ends at rest (r17chain: rest at the end of an action; R19_SMOOTH rest-to-rest per
   piece, results/r19/smooth/spatula.json). So the join is timed FROM REST, rest to rest; the stir cycle is
   entered from rest at H_stir0 exactly as its library entry states ("from rest the same geometry is run with a
   ramp").
Geometry: the tool-fixed self-motion. The cart is stepped from the spatula end to the stir cart (1 mm steps) and
 the 6 arm joints are solved at every step for the unchanged tool pose (least squares from the previous step, as
 r15stirwalk2 / r19stir_cycle.follow): the blade holds still in the wok while the cart slides and the arm
 re-configures. It must arrive exactly at H_stir0 (same IK branch); else the join FAILS (no fallback is taken).
 Stored as an interpolating quintic B-spline over (cart, q1..q6), parameter u = cart travel (m).
 For comparison the straight (cart, joint) line is screened as well (not stored).
Certificate (a state fails on any hit or range violation; no gate loosened): the spline cut at <= 4 mm
 (r19smooth.FastBound point bound over sub-steps <= 0.5 mm, cart included), every state through
 Checker.check(full=True) (MuJoCo contacts + GJK lower-bound certificate, 10 mm robot-environment, 5 mm
 gripper/held-environment, 0 mm self, joint ranges; R11 held-box mesh rule; hit pairs classed by
 r19enc_check.one), in two scenes:
   stir  the scene the cycle is certified in (r19stir_cycle.model: R17 kitchen, R15 held spatula, jaw -1), with
         the plume rule (every robot geom except the spatula, cart and dock >= 0 mm outside the 0.20 m cylinder
         about the wok axis, rim .. 1.25 m);
   std   the current checking layout: the spatula chain's own R18b scene (held spatula_b, r17chain BASE) with the
         plating spot at y .15 (PY=.15) and the pot-zone layer (kitchen19pot: keyed lid rack, spider rest at
         (1.56, .20), R19_POTZONE.md 5-6); plume rule too (held spatula parts excluded).
Exit (stir end -> spatula return): STIR_EXIT = the same geometry reversed, H_stir0 -> SPATULA_FETCH end, from
 where SPATULA_STOW (the fetch reversed) returns the spatula to its rest. A reversed path has the same states and
 scene (R19_MOTION_LIBRARY rule 4); its states are stored in exit order and its own law is computed.
Time law (rest to rest): TOPP + filter + slow-downs (r19stir2_law) on (cart, q1..q6):
 joint speed = arms.speeds (datasheet), joint acceleration 800 deg/s^2 (A_UR, UR forum guidance; ASSUMPTION for
 the FR5) and 360 deg/s^2 (A_R15 assumption); cart 0.25 m/s (r17chain CW) and 0.5 m/s^2 ('fastcart',
 R19_SMOOTH: sim tip-over check) or 0.15 m/s^2 ('same', mobile.py design case); filter W = 0.2 s (cart jerk <=
 2 a / W = 5 m/s^3, R19_SMOOTH's cart-jerk assumption); joint jerk limit J if given (JERK=<deg/s^3>).
python r19stir2_join.py join ARM=<arm> [WORKERS=24] [JERK=<deg/s^3>]
  -> results/r19/stir/join_<arm>/join.json (all numbers), results/r19/stir/lib_stir_join_<arm>.json (library entry)"""
import sys,os,json,time,math,hashlib
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
ARM=KV.get('ARM','ur5e_enc2_pgc');os.environ['ARM']=ARM
OUT=f'results/r19/stir/join_{ARM}';LIBF=f'results/r19/stir/lib_stir_join_{ARM}.json'
SPAT={'ur5e_enc2_pgc':'results/r17/chain_spatula_s-1_r18roll-1.15_.30_ur5e_enc2_pgc.json','fr5_j6_pgc_sp20':'results/r17/chain_spatula_s-1_r18roll-1.15_.30_fr5_j6_pgc_sp20.json'}
HUBS={'ur5e_enc2_pgc':'results/r19/hub_py.15_ur5e_enc2_pgc/hubs.json'}
CYC=f'results/r19/stir/lib_stir_cycle_{ARM}.json'
TWO=2*np.pi;STEP=.004;SUB=.0005;DX=.001;WK=int(KV.get('WORKERS',24));SIGN=-1
LAYER=dict(rack='keyed',spider=(1.56,.20),plate_y=.15)
CART=dict(v=.25,a_fast=.5,a_same=.15,j_assumed=5.)   # m/s, m/s^2, m/s^3: R19_SMOOTH limits (CW; fastcart / same; cart jerk assumption)
W_JOIN=2*CART['a_fast']/CART['j_assumed']             # 0.2 s: the moving-average window that keeps cart jerk <= 5 m/s^3
COLS=[0,3,4,5,6,7,8]   # cart x + the 6 arm joints
# ---------------------------------------------------------------- the two ends
def spat_end():
 """the spatula chain (adopted file), unwrapped as r19hub.unwrapped and relabelled by the roadmap shift -> play, shift"""
 r=json.load(open(SPAT[ARM]));P=np.array(r['play'],float);U=P.copy()
 for i in range(1,len(U)):U[i:,3:9]-=np.round((U[i,3:9]-U[i-1,3:9])/TWO)*TWO
 sh=np.zeros(11);src='none (no hub roadmap for this arm): unwrapped labels'
 if ARM in HUBS:
  for j,k in json.load(open(HUBS[ARM]))['action_shifts'].get('spatula',{}).items():sh[int(j)]=TWO*k
  src=f"{HUBS[ARM]} action_shifts['spatula']"
 return r,U+sh,dict(unwrap_net_2pi=np.round((U[-1]-P[-1])[3:9]/TWO).astype(int).tolist(),roadmap_shift_2pi=np.round(sh[3:9]/TWO).astype(int).tolist(),roadmap=src)
def cycle_relabel(L,E,lo,hi):
 """per-joint 2pi shift of the whole stored cycle nearest to the spatula end, every certified state in range"""
 Q=np.array(L['states']['q'],float);S=np.array(L['hub']['state'],float);k=[]
 for j in range(6):
  best=None
  for n in (-1,0,1):
   x=Q[:,3+j]+TWO*n
   if x.min()<lo[j]-1e-9 or x.max()>hi[j]+1e-9:continue
   d=abs(S[3+j]+TWO*n-E[3+j])
   if best is None or d<best[0]:best=(d,n)
  if best is None:raise SystemExit(f'joint {j+1}: no 2pi label of the cycle stays in range')
  k.append(best[1])
 return np.array(k)
# ---------------------------------------------------------------- scenes (one per process: the pot-zone layer patches kitchen16 for good)
_M={}
def scene(name):
 if name in _M:return _M[name]
 import mujoco,xml.etree.ElementTree as E
 import r19smooth as S
 if name=='stir':
  import r19stir_cycle as C
  M=dict(C.model(SIGN));M['name']='stir'
 elif name=='std':
  import chain,arms,kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19pot as P
  from scene import build,fmt
  from checker import Checker
  from r19enc_check import meshheld
  assert arms.current()==ARM
  r=json.load(open(SPAT[ARM]));K15.PLATE['c'][1]=LAYER['plate_y']
  K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
  for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
  K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.
  P.install(rack=LAYER['rack'],spider=LAYER['spider'])   # after the chain's tool_xy: the layer's spider rest wins
  BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
  cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])})
  tree,meta=build(cfg,None);meshheld(tree);ch=Checker(tree,meta)
  E.SubElement(tree.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K15.WOK0[0],K15.WOK0[1],(K15.RIM_Z+1.25)/2]),size=fmt([.20,(1.25-K15.RIM_Z)/2]),contype='0',conaffinity='0')
  pm=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));pd=mujoco.MjData(pm);pl=pm.geom('r15_plume').id
  rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(('R_gripper_spatula','R_gripper_r18_spat','R_cart','R_dock'))]
  def plume(q):
   pd.qpos[:]=q;mujoco.mj_forward(pm,pd);ft=np.zeros(6);best=(1e9,None)
   for g in rob:
    v=1000*mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft)
    if v<best[0]:best=(v,pm.geom(g).name)
   return best
  m=ch.m;ids=ch.arm_ids
  M=dict(name='std',ch=ch,plume=plume,fb=S.FastBound(ch),ids=ids,lo=np.array([m.jnt_range[j,0] for j in range(m.njnt)])[ids],hi=np.array([m.jnt_range[j,1] for j in range(m.njnt)])[ids],
   sid=m.site('R_prep').id,cfg_md5=hashlib.md5(ch.xml.encode()).hexdigest(),layer=dict(LAYER,spider_rest=list(K.TOOL_XY['spider']),rack_geoms=sum(1 for g in range(m.ngeom) if m.geom(g).name.startswith('r19pot_rack')),plate_c=list(K15.PLATE['c'])))
 else:raise KeyError(name)
 _M[name]=M;return M
def _chk(args):
 name,Q=args;import r19enc_check as RC;M=scene(name);return [RC.one(M,np.asarray(q)) for q in Q]
def _init():os.environ['ARM']=ARM
def certify(name,Q):
 """full check of the states Q in scene `name` (its own pool: one scene per process)"""
 import multiprocessing as mp,r19enc_check as RC
 n=max(1,math.ceil(len(Q)/(WK*2)));jobs=[(name,Q[i:i+n].tolist()) for i in range(0,len(Q),n)]
 with mp.Pool(min(WK,len(jobs)),initializer=_init) as pool:res=pool.map(_chk,jobs,chunksize=1)
 rs=[x for r_ in res for x in r_];S_=RC.summarize(rs,np.arange(len(rs)))
 return rs,dict(ok=S_['ok'],states=len(rs),hit_states=S_['hit_states'],out_of_range_states=S_['out_of_range_states'],hit_pairs=dict(list(S_['hit_pairs'].items())[:4]),
  min_env_reserve_mm=S_['min_env_reserve_mm'],min_env_pair=S_['min_env_pair'],min_self_reserve_mm=S_['min_self_reserve_mm'],min_self_pair=S_['min_self_pair'],
  min_reserve_by_category=S_['min_reserve_by_category'],min_plume_mm=S_.get('min_plume_mm'),min_plume_geom=S_.get('min_plume_geom'),plume_violations=S_.get('plume_violations'))
# ---------------------------------------------------------------- geometry
def self_motion(M,E,S):
 """tool-fixed IK continuation, cart stepped E[0] -> S[0] (DX), tool pose = FK(E); -> states (n x 11), max pose error"""
 import mujoco
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 ch=M['ch'];m,d=ch.m,ch.d;ids=M['ids'];sid=M['sid'];lo,hi=M['lo'],M['hi']
 d.qpos[:]=E;mujoco.mj_kinematics(m,d);p0=d.site_xpos[sid].copy();R0=d.site_xmat[sid].reshape(3,3).copy()
 xs=np.linspace(E[0],S[0],int(math.ceil(abs(S[0]-E[0])/DX))+1);q=np.array(E,float);out=[q.copy()];pe=0.
 for x in xs[1:]:
  q[0]=x
  def res(xx):
   q[ids]=xx;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-p0)*10,Rotation.from_matrix(R0@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  sol=least_squares(res,np.clip(q[ids],lo+1e-8,hi-1e-8),bounds=(lo+1e-9,hi-1e-9),max_nfev=200,xtol=1e-12,ftol=1e-12);q[ids]=sol.x
  a,b=ch.pose_error(q,p0,R0);pe=max(pe,a);out.append(q.copy())
 return np.array(out),p0,R0,pe
def spline7(X,E):
 """interpolating quintic over (cart, q1..q6), parameter u = cart travel from E (m)"""
 from scipy.interpolate import make_interp_spline
 u=np.abs(X[:,0]-E[0]);return make_interp_spline(u,X[:,COLS],k=5)
def full(q0,Y):
 Q=np.tile(np.asarray(q0,float),(len(Y),1));Q[:,COLS]=Y;return Q
def cut7(M,q0,sp,L):
 """parameters on [0, L] with the point bound (cart included) <= STEP between consecutive states, sub-steps <= SUB"""
 fb=M['fb'];n=max(3,int(L/.0002)+1)
 while True:
  u=np.linspace(0,L,n);Q=full(q0,sp(u));bd=np.array([fb(Q[i],Q[i+1]) for i in range(n-1)])
  if bd.max()<=SUB*1.0001:break
  n=int(n*bd.max()/SUB*1.1)+2
 out=[0];acc=0.;spm=0.
 for i in range(n-1):
  if acc+bd[i]>STEP:out.append(i);spm=max(spm,acc);acc=0.
  acc+=bd[i]
 if out[-1]!=n-1:out.append(n-1)
 return u[out],max(spm,acc)
def tool_dev(M,q0,sp,L,p0,R0):
 """max tool position (mm) / rotation (deg) deviation of the spline from the held tool pose (0.02 mm cart grid)"""
 ch=M['ch'];u=np.linspace(0,L,int(L/2e-5)+1);Q=full(q0,sp(u));a_=b_=0.
 for q in Q:a,b=ch.pose_error(q,p0,R0);a_=max(a_,a);b_=max(b_,b)
 return round(a_*1e3,6),round(float(np.degrees(b_)),6)
# ---------------------------------------------------------------- time law
def law(sp,L,V7,A7,J7=None,W=W_JOIN):
 import r19stir2_law as TL
 p=TL.PathN([(sp,0.,L)],7);capf=lambda s:np.full(len(np.atleast_1d(s)),1e12)
 tl=TL.timelaw(p,V7,A7,capf,0.,0.,W,J=J7);t,s,sd=tl['t'],tl['s'],tl['sd']
 return dict(time_s=round(float(t[-1]),3),peak_v=dict(cart_mps=round(float(tl['peaks']['v'][0]),4),joints_degps=np.degrees(tl['peaks']['v'][1:]).round(1).tolist()),
  peak_a=dict(cart_mps2=round(float(tl['peaks']['a'][0]),4),joints_degps2=np.degrees(tl['peaks']['a'][1:]).round(1).tolist()),
  peak_j=dict(cart_mps3=round(float(tl['peaks']['j'][0]),3),joints_degps3=np.degrees(tl['peaks']['j'][1:]).round(0).tolist()),
  worst_ratio=tl['worst'],converged=tl['converged'],iters=tl['iters'],W_s=W),tl
def rev(sp,L):
 """the reversed spline (exit): r(u) = sp(L - u), derivatives with sign (-1)^nu"""
 class R_:
  def __init__(self,b,L):self.b=b;self.L=L;self.t=b.t;self.k=b.k;self.c=b.c
  def __call__(self,x,nu=0):return (-1)**nu*self.b(self.L-np.asarray(x,float),nu)
 return R_(sp,L)
# ---------------------------------------------------------------- main
def join():
 import arms
 t00=time.monotonic();os.makedirs(OUT,exist_ok=True)
 M=scene('stir');lo,hi=M['lo'],M['hi']
 r,U,lab=spat_end();E=U[-1].copy()
 L_=json.load(open(CYC));k=cycle_relabel(L_,E,lo,hi);S=np.array(L_['hub']['state'],float);S[3:9]+=TWO*k
 Qc=np.array(L_['states']['q'],float);Qc[:,3:9]+=TWO*k
 import r19stir_report as RP
 G=L_['geometry'];segs=[RP.Seg(g) for g in G['segments']];yy=np.vstack([sg(np.linspace(sg.a,sg.e,2000)) for sg in segs])+TWO*k
 rng=dict(cycle_relabel_2pi=k.astype(int).tolist(),certified_states_in_range=bool(np.all(Qc[:,3:9]>=lo-1e-9) and np.all(Qc[:,3:9]<=hi+1e-9)),
  geometry_in_range_2000_per_segment=bool(np.all(yy>=lo-1e-9) and np.all(yy<=hi+1e-9)),cycle_min_deg=np.degrees(Qc[:,3:9].min(0)).round(2).tolist(),cycle_max_deg=np.degrees(Qc[:,3:9].max(0)).round(2).tolist(),
  spatula_play_in_range=bool(np.all(U[:,3:9]>=lo-1e-9) and np.all(U[:,3:9]<=hi+1e-9)),spatula_min_deg=np.degrees(U[:,3:9].min(0)).round(2).tolist(),spatula_max_deg=np.degrees(U[:,3:9].max(0)).round(2).tolist())
 assert rng['certified_states_in_range'] and rng['geometry_in_range_2000_per_segment'] and rng['spatula_play_in_range'],rng
 assert np.allclose(np.delete(E,COLS),np.delete(S,COLS)),'base / jaws differ between the ends'
 print('ends: spatula end',np.round(E,5).tolist(),'H_stir0 (relabelled',k.tolist(),')',np.round(S,5).tolist(),flush=True)
 print('joint diff deg',np.degrees(S[3:9]-E[3:9]).round(2).tolist(),'cart',round(S[0]-E[0],4),flush=True)
 # ---- geometry: tool-fixed self-motion
 X,p0,R0,pe=self_motion(M,E,S);dend=np.degrees(np.abs(X[-1,3:9]-S[3:9])).max()
 ok_branch=dend<1e-4;print('self-motion',len(X),'states, max pose err %.2e m'%pe,'end vs H_stir0 %.2e deg'%dend,flush=True)
 if not ok_branch:raise SystemExit('the tool-fixed self-motion does not reach H_stir0 (another IK branch): no join stored')
 X[-1]=S;sp=spline7(X,E);L=float(abs(S[0]-E[0]));dev=tool_dev(M,E,sp,L,p0,R0)
 print('spline tool deviation mm / deg',dev,flush=True)
 # ---- the straight (cart, joint) line, for comparison only (screened at the same 4 mm states, stir scene)
 from scipy.interpolate import make_interp_spline
 line=make_interp_spline([0.,L],np.array([E[COLS],S[COLS]]),k=1);ul,_=cut7(M,E,line,L);Ql=full(E,line(ul))
 import mujoco
 ch=M['ch'];tdl=0.
 for q in Ql:a,b=ch.pose_error(q,p0,R0);tdl=max(tdl,a)
 # ---- certificate of the self-motion spline, both scenes
 u,spm=cut7(M,E,sp,L);Q=full(E,sp(u));print('states',len(Q),'max step bound %.3f mm'%(spm*1e3),flush=True)
 cert={}
 for nm in ('stir','std'):
  rs,cs=certify(nm,Q);cert[nm]=cs;print(nm,json.dumps(cs),'%.0f s'%(time.monotonic()-t00),flush=True)
  if nm=='stir':rs_stir=rs
 rsl,csl=certify('stir',Ql);print('line (comparison)',json.dumps({k_:csl[k_] for k_ in ('ok','states','hit_states','min_env_reserve_mm','min_env_pair','min_plume_mm')}),'tool dev %.2f mm'%(tdl*1e3),flush=True)
 # ---- the std scene's model facts (layer present?)
 import multiprocessing as mp
 with mp.Pool(1,initializer=_init) as pool:lay=pool.apply(_layer_facts)
 # ---- time laws
 V=np.radians(arms.speeds(ARM));J=float(KV['JERK']) if 'JERK' in KV else None
 laws={}
 for an,A_ in (('A_UR',800.),('A_R15',360.)):
  for cn,ac in (('fastcart',CART['a_fast']),('same',CART['a_same'])):
   V7=np.r_[CART['v'],V];A7=np.r_[ac,np.full(6,math.radians(A_))]
   J7=None if J is None else np.r_[1e9,np.full(6,math.radians(J))]
   for dn,spx in (('entry',sp),('exit',rev(sp,L))):
    s_,tl=law(spx,L,V7,A7,J7);laws[f'{dn}_{an}_{cn}']=s_
    if dn=='entry' and an=='A_UR' and cn=='fastcart':keep=tl
 for k_,v_ in laws.items():print(k_,json.dumps(v_),flush=True)
 # ---- the cycle entered / left from rest (stored entry: three cycles from rest)
 TLc=L_['time_law'];ramp=round(TLc['three_cycles_from_rest_s']-3*TLc['period_s'],3)
 out=dict(arm=ARM,spatula_chain=SPAT[ARM],cycle=CYC,labels=dict(lab,**rng),ends=dict(spatula_end=E.tolist(),h_stir0=S.tolist(),h_stir0_stored=L_['hub']['state'],joint_diff_deg=np.degrees(S[3:9]-E[3:9]).round(3).tolist(),cart_m=round(float(S[0]-E[0]),5)),
  spatula_chain_ends_at_rest='yes: r17chain ends every action at rest; R19_SMOOTH times the spatula chain rest to rest per piece (results/r19/smooth/spatula.json); so the join is timed from rest',
  geometry=dict(kind='tool-fixed self-motion (cart stepped %g m, 6 joints solved for the unchanged tool pose)'%DX,ik_states=len(X),ik_max_pose_err_m=pe,end_vs_h_stir0_deg=float(dend),spline='interpolating quintic over (cart, q1..q6), u = cart travel (m)',
   length_m=L,tool_dev_mm_deg=dev),
  certificate=dict(states=len(Q),max_step_bound_mm=round(spm*1e3,3),scenes=cert,std_scene=lay,checker='Checker.check(full=True) + r19enc_check.one (10 / 5 / 0 mm, joint ranges, R11 held-box mesh rule), plume rule'),
  line_comparison=dict(states=len(Ql),tool_dev_mm=round(tdl*1e3,2),**{k_:csl[k_] for k_ in ('ok','hit_states','min_env_reserve_mm','min_env_pair','min_plume_mm')}),
  laws=laws,cycle_ramp_from_rest_s=dict(value=ramp,note='three_cycles_from_rest_s - 3 x period of the stored entry: the extra time to start the cycle from rest at H_stir0 and stop it there again'),
  limits=dict(joint_v_degps=np.degrees(V).round(2).tolist(),joint_v_source=arms.ARMS[ARM]['speeds_source'],A_UR='800 deg/s^2: UR forum guidance (R19_STIR.md 1); ASSUMPTION for a non-UR arm',A_R15='360 deg/s^2: R15 ASSUMPTION',
   cart='v 0.25 m/s (r17chain CW); a 0.5 m/s^2 fastcart (R19_SMOOTH: tip-over model, r19smooth_cart.py) / 0.15 m/s^2 same (mobile.py design case); W 0.2 s keeps cart jerk <= 5 m/s^3 (R19_SMOOTH ASSUMPTION)',jerk_limit_degps3=J),
  elapsed_s=round(time.monotonic()-t00))
 json.dump(out,open(f'{OUT}/join.json','w'),indent=1,default=float)
 write_lib(out,sp,L,E,S,Q,u,keep,cert,L_,lab,k)
 print('saved',f'{OUT}/join.json',LIBF,'%.0f s'%(time.monotonic()-t00))
def _layer_facts():
 M=scene('std');return M['layer']
def write_lib(out,sp,L,E,S,Q,u,tl,cert,L_,lab,k):
 import arms
 ok=all(c['ok'] and c['hit_states']==0 and c['out_of_range_states']==0 and (c['plume_violations'] or 0)==0 for c in cert.values()) and out['certificate']['max_step_bound_mm']<=4.0+1e-9
 assert ok,'not certified: no library entry'
 geo=dict(type='bspline',k=int(sp.k),knots=sp.t.tolist(),coef=np.asarray(sp.c).tolist(),coords='[cart_x, q1..q6] (m, rad); base_y, base_yaw, jaws constant = state_const',param='u = cart travel from the SPATULA_FETCH end (m), 0 .. length',length=L,state_const=E.tolist())
 t,s=tl['t'],tl['s'];st=Q.tolist();gmd5=hashlib.md5(json.dumps(geo).encode()).hexdigest()
 def entry(eid,start,end,states,law_key,note):
  return dict(id=eid,arm=ARM,arm_name=arms.ARMS[ARM]['name'],start_hub=start,end_hub=end,note=note,
   time_law=dict(law='rest to rest, A_UR 800 deg/s^2, cart 0.5 m/s^2 (fastcart), W 0.2 s; t / u on a 2 ms grid'+(' (entry direction; the exit runs it reversed: u_exit(t) = length - u(T - t))' if eid=='STIR_EXIT' else ''),
    **out['laws'][law_key]),states=dict(layout='[carriage_x, base_y, base_yaw, q1..q6, finger_l, finger_r]',note='the certified states, <= 4 mm apart, in this set\'s order',q=states,md5=hashlib.md5(json.dumps(states).encode()).hexdigest()))
 hubs=dict(H_spat_stroke=dict(state=E.tolist(),note='SPATULA_FETCH end (stroke start#5) in the labels a controller runs: '+json.dumps(lab)),
  H_stir0=dict(state=S.tolist(),note=f'stored H_stir0 relabelled by {k.astype(int).tolist()} x 2pi per joint (the WHOLE stir cycle is run with this relabel; every certified cycle state and the geometry stay in range)'))
 lib=dict(id='STIR_JOIN',arm=ARM,hubs=hubs,label_map=out['labels'],geometry=geo,
  time_law_entry=dict(t=t.round(6).tolist(),u=s.round(9).tolist()),
  sets=[entry('STIR_ENTRY','H_spat_stroke','H_stir0',st,'entry_A_UR_fastcart','spatula in hand: the blade holds still at the stroke-0 start while the cart slides %.1f cm and the arm re-configures; then STIR_CYCLE from rest'%(100*abs(S[0]-E[0]))),
   entry('STIR_EXIT','H_stir0','H_spat_stroke',st[::-1],'exit_A_UR_fastcart','after STIR_CYCLE stops at H_stir0 (from-rest law); then SPATULA_STOW = SPATULA_FETCH reversed returns the spatula to its rest')],
  other_laws={k_:v_ for k_,v_ in out['laws'].items()},cycle_ramp_from_rest_s=out['cycle_ramp_from_rest_s'],
  verification=dict(status='verified',certificate=dict(checker=out['certificate']['checker'],spacing='consecutive states <= 4 mm by point_bound (r19smooth.FastBound, cart included, sub-steps <= 0.5 mm)',
   states=len(Q),max_step_bound_mm=out['certificate']['max_step_bound_mm'],scenes=cert,std_scene=out['certificate']['std_scene'],geometry_md5=gmd5,
   reversal='STIR_EXIT has the same states and scenes as STIR_ENTRY (R19_MOTION_LIBRARY rule 4)',date=time.strftime('%Y-%m-%d'))))
 if os.path.exists(LIBF):
  n=1
  while os.path.exists(LIBF[:-5]+f'.replaced_{n}.json'):n+=1
  os.rename(LIBF,LIBF[:-5]+f'.replaced_{n}.json')
 json.dump(lib,open(LIBF,'w'),default=float)
def cycle():
 """the stored cycle's certified states (relabelled as in join.json) re-checked in the std scene (PY=.15 + pot-zone
 layer + the chain's held spatula): the cycle was certified in the R17 scene (plating spot y .13, R16 rack)"""
 t00=time.monotonic();M=scene('stir');r,U,lab=spat_end();L_=json.load(open(CYC));k=cycle_relabel(L_,U[-1],M['lo'],M['hi'])
 Q=np.array(L_['states']['q'],float);Q[:,3:9]+=TWO*k;rs,cs=certify('std',Q)
 kinds=L_['states']['kinds'];per={}
 for kd,x in zip(kinds,rs):
  e=min(v[0] for kk,v in x['cl'].items() if kk!='self');p=per.setdefault(kd,dict(states=0,hits=0,min_env_mm=1e9,min_plume_mm=1e9));p['states']+=1;p['hits']+=bool(x['hits'] or not x['ranges']);p['min_env_mm']=min(p['min_env_mm'],e);p['min_plume_mm']=min(p['min_plume_mm'],x['plume'][0])
 out=dict(arm=ARM,cycle=CYC,relabel_2pi=k.astype(int).tolist(),scene='std: R18b chain scene, plating spot y .15, kitchen19pot keyed rack + spider rest (1.56, .20), held spatula_b, plume rule',certificate=cs,per_segment=per,elapsed_s=round(time.monotonic()-t00))
 os.makedirs(OUT,exist_ok=True);json.dump(out,open(f'{OUT}/cycle_std_recheck.json','w'),indent=1,default=float);print(json.dumps(cs),'%.0f s'%(time.monotonic()-t00))
if __name__=='__main__':
 {'join':join,'cycle':cycle}[sys.argv[1]]()
