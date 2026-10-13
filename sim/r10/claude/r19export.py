"""R19 #6: exporter for checked paths -> a neutral controller format (JSON + CSV), thin UR / FR5 writers
(r19export_writers.py) and the round-trip test. New file; it imports the existing modules and changes none.

In (any result file of these kinds; the kind is read from the file):
 chain  results/r17/chain_*_<arm>.json  (r17chain play + keyframes + approach_qs; certificate = its
        'adopted.play_recheck' file, r19enc_check.py recheck; approaches checked by r19enc_adopt.py)
 prep   results/r19/prep*/chain_*_<arm>.json  (r19prepchain style; certificate <file>_verify4mm[_pot].json,
        r19prep[4|5]_verify.py)
 hub    results/r19/hub_*/edge_*.json  (r19hub.py edge: straight (cart, joint) segments, union scene)
 stir   results/r19/stir/lib_stir_cycle_*.json  (library entry: C2 B-spline cycle, its certificate, from-rest law)

Export (results/r19/export/<name>/export.json, format "r19export/1"; R19_EXPORT.md 2 has the full spec):
 - joint labels: the stored play unwrapped exactly as its certificate's checker did (r19smooth.unwrap /
   r19prep_verify.unwrap); for an arm with a hub roadmap (ur5e_enc2_pgc) the whole action is relabelled by the
   roadmap's 2pi shift, so the exported hubs are the roadmap's endpoint vectors (checked, 'hubs.roadmap_match');
 - sequence: motion pieces between mandatory stops and holds (grasp / release 0.8 s, dwells), hub state at both ends;
   motion = B-spline over the 7 moving coordinates [carriage_x, q1..q6] (m, rad), parameter s in [0, L]; the
   other 4 state values (base_y, base_yaw, jaws) are constant per piece;
     chain/prep play: r19smooth.py's segmentation (start, end, dwells, grasp/release pieces, reversals > 150 deg);
       free pieces = r19smooth.fit_spline (cubic smoothing spline, ends exact) through the stored states AND joint-linear
       points of the certified polyline between them (<= DENS = 8 mm apart by point bound), each within clip(RF x its own
       clearance reserve from the certificate, TMIN, TMAX) by the global point bound; contact windows (the straight
       grasp/release pieces, the approaches, the seat lift / set-down links) = interpolating cubic through the stored
       states (r19smooth.fit_fixed) or an exact straight line; a coordinate whose stored states come within SQ_MARGIN
       = 0.05 (m / rad) of its range limit is fitted as limit + sign h^2 (r19smooth's rule; stored per span as 'sq');
       REFIT=1 = r19smooth's repair round: the stored states near the previous export's re-check hits get 1/4 tolerance;
     hub edge: every straight segment is an exact cubic (collinear control points); vias are stops;
     stir: the stored certified C2 B-spline segments unchanged (quintic / cubic, one 'limit + h^2' coordinate kept
       as stored), one periodic piece;
 - check: per motion piece the scene its certificate used (spec + md5 of the model XML) or the rule that exempts it
   (seat lift / set-down: support contact window, not a checked state in r17chain / r19prep_verify either);
 - time law, generated here (not stored as truth): per motion piece rest to rest, r19stir2_law.timelaw (TOPP by
   reachability + r19smooth erosion / moving-average filter W + local slow-downs until every limit holds on the
   2 ms grid) with joint and cart speed / acceleration / JERK limits and a TCP speed / rotation cap; the stir keeps
   its stored jerk-limited from-rest law (r19stir2_retime / r19spill_cycle, J 8000 deg/s^3);
 - playback: stream.csv (500 Hz = UR RTDE servoj period, all 11 state values) + the arm's writer.
Round trip (the acceptance): 1. state fit (export: the stored states vs the exported spline at their parameters,
 evaluated from export.json + states.npz alone); 2. dense re-check (recheck: the exported splines cut at <= 4 mm by
 point bound, every state through the same checker as the certificate); 3. limits (export: v / a / jerk of the
 500 Hz stream by finite differences, and of the written UR / FR5 file).
python r19export.py export FILE=<result json> [NAME=] [REVERSE=1] [RF=.5 TMIN=.0005 TMAX=.008] [A_JOINT=1.4 J_JOINT=14
                    V_TCP=.25 ...]                     -> results/r19/export/<name>/{export.json,states.npz,stream.csv,...}
python r19export.py recheck NAME=<name>[,<name>...] [WORKERS=20]  -> results/r19/export/<name>/recheck.json
python r19export.py report                            -> results/r19/export/summary.json (+ the table printed)"""
import sys,os,json,time,math,hashlib,glob,importlib
sys.path.insert(0,'.')
import numpy as np
CMD=sys.argv[1] if len(sys.argv)>1 else ''
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
OUT='results/r19/export';FORMAT='r19export/1'
TWO=2*np.pi;H=.002
COLS=[0,3,4,5,6,7,8]   # carriage x + the 6 arm joints (state indices)
STATE='[carriage_x, base_y, base_yaw, q1, q2, q3, q4, q5, q6, finger_l, finger_r] (m, m, rad, rad x6, m, m)'
CART_TRAVEL=(-1.48,1.46)   # r17chain.solve_free / r19smooth cart travel (m)
SQ_MARGIN=float(KV.get("SQ_MARGIN",.05))   # a coordinate whose stored states come within this (m or rad) of a range limit is fitted as limit + h^2
DENS=float(KV.get('DENS',.008))   # max point-bound spacing of the fitting data along the certified polyline (m)
GRASP_S=.8                 # r17chain GRASP: grasp / release hold (s)
ROADMAP={'ur5e_enc2_pgc':('results/r19/hub_py.15_ur5e_enc2_pgc/hubs.json',.15)}
RF,TMIN,TMAX=float(KV.get('RF',.5)),float(KV.get('TMIN',.0005)),float(KV.get('TMAX',.008))
LIM=dict(a_joint=float(KV.get('A_JOINT',1.4)),j_joint=float(KV.get('J_JOINT',14.)),v_cart=float(KV.get('V_CART',.25)),a_cart=float(KV.get('A_CART',.5)),
 j_cart=float(KV.get('J_CART',5.)),W=float(KV.get('W',.2)),
 free=dict(v_joint=None,v_tcp=float(KV.get('V_TCP',.25)),w_tcp=float(KV.get('W_TCP',90.))),contact=dict(v_joint=60.,v_tcp=.10,w_tcp=45.),w_tcp_wok=45.)
LIM_SRC=dict(
 v_joint_free='arm datasheet (arms.speeds: UR5e 180 deg/s, FR5 180 deg/s) [S]',
 a_joint='1.4 rad/s^2: URScript movej default a [S] (https://www.universal-robots.com/manuals/EN/HTML/SW5_24/Content/prod-scriptmanual/all_scripts/movej_qa14v105t0r.htm)',
 j_joint='14 rad/s^3: R19_SMOOTH rule "full acceleration in >= 0.1 s" [E] (no OEM joint jerk limit published for the UR5e)',
 cart='0.25 m/s (r17chain CW), 0.5 m/s^2 (R19_SMOOTH fastcart, sim tip-over model r19smooth_cart.py; quasi-static, GitHub #14 open), 5 m/s^3 (R19_SMOOTH assumption) [E]',
 tcp='free: 0.25 m/s (ISO 10218-1 reduced speed = URScript movel default v) [S], rotation 90 deg/s (wok held: 45 deg/s, R15 pour physics) [E]; '
     'contact windows: R17 caps 0.10 m/s, 45 deg/s, joints 60 deg/s (r17chain VW/WW/QW) [E]',
 W='0.2 s moving-average window: filter jerk ~ 2 a / W stays at the jerk limits (R19_SMOOTH)',
 holds='grasp / release 0.8 s each (r17chain GRASP), process dwells as the source set (r17chain / r19prepchain keyframes)',
 not_in_law='jaw moment, food acceleration and cart tip-over are not re-evaluated by this law (R19_SMOOTH: non-binding at these caps)')
# ===================================================================== scenes = the certificates' checkers
_SC={}
def _bad_rc(o):return bool(o['hits']) or not o['ranges'] or ('plume' in o and o['plume'][0]<0)
def _row_rc(o):
 env=[v[0] for k,v in o['cl'].items() if k!='self'];return dict(bad=_bad_rc(o),hits=list(o['hits'])[:2],ranges=bool(o['ranges']),env=min(env) if env else None,
  self=o['cl']['self'][0] if 'self' in o['cl'] else None,plume=o['plume'][0] if 'plume' in o else None)
def _row_ch(r,okkey=False):
 cl=r['clearance'];env=[v['reserve_mm'] for k,v in cl.items() if k!='self']
 bad=(not r['ok']) if okkey else (bool(r['hits']) or not r['ranges'])
 return dict(bad=bad,hits=[h['pair'] for h in r['hits']][:2],ranges=bool(r['ranges']),env=min(env) if env else None,self=cl['self']['reserve_mm'] if 'self' in cl else None,plume=None)
def scene(spec):
 """the checker of a scene spec (as stored in export.json) -> dict(ch=Checker, check_many=f(Qs) -> rows, md5); cached
 per process. Every spec rebuilds the scene exactly as the certificate's script does (one spec type per process)."""
 key=json.dumps(spec,sort_keys=True)
 if key in _SC:return _SC[key]
 t=spec['type'];arm=spec['arm']
 import r19stir2_law   # imports r19stir_cycle, which sets $ARM at import: import it first, then set the arm
 os.environ['ARM']=arm
 if t=='chain_play':   # r19enc_check.py recheck (r19smooth.setup scene, R18b layout, PY plate, R11 held-box mesh rule)
  import r19enc_check as RC
  RC.KV.clear();RC.KV.update({k:v for k,v in (('SUFFIX',spec.get('suffix')),('PY',spec.get('py'))) if v})
  c=RC.ctx(spec['key'],arm);M=dict(ch=c['ch'],check_many=lambda Qs,c=c:[_row_rc(RC.one(c,np.asarray(q))) for q in Qs])
 elif t=='chain_app':   # r19enc_adopt.py: r17chain.py run up to its main loop with the chain's options, its empty-gripper scene of that keyframe
  import r19enc_adopt as AD
  src,opts=AD.OPTS[spec['key']]
  sys.argv=['r17chain.py']+opts.split()+(['PY='+spec['py']] if spec.get('py') else [])+['ARM='+arm]
  s=open('r17chain.py',encoding='utf-8').read();g={'__name__':'r17chain_defs','__file__':os.path.abspath('r17chain.py')}
  exec(compile(s[:s.index('t0=time.monotonic();pieces={}')],'r17chain.py','exec'),g)
  assert g['ARM']==arm,(g['ARM'],arm)
  world=[w for k,w in g['GR'] if k==spec['kf']][0];ch=g['model'](world)
  M=dict(ch=ch,check_many=lambda Qs,ch=ch:[_row_ch(ch.check(np.asarray(q),full=True,mass=0.)) for q in Qs])
 elif t=='prep':   # r19prep[4|5]_verify.py: the play scene (object held) or an approach scene (object in the world, food contact window)
  sys.argv=['r19prep_verify.py','FILE='+spec['file']]+[f'{k}={v}' for k,v in spec.get('kv',{}).items()]
  PV=importlib.import_module(spec['verifier'])
  part=spec['part'] if spec['part']=='play' else list(spec['part'])
  R=json.load(open(spec['file']));c,win=PV.scene_for(R,'play' if part=='play' else tuple(part))
  def cm(Qs,PV=PV,part=part):
   out=[]
   for o in PV.work((part,[list(map(float,q)) for q in Qs])):
    out.append(dict(bad=bool(o['hits']) or not o['ranges'] or bool(o['touch']),hits=o['hits'][:2],ranges=bool(o['ranges']),env=o['res'],self=o['self_mm'],plume=o.get('plume_mm')))
   return out
  M=dict(ch=c,check_many=cm,PV=PV)
 elif t=='hub':   # r19hub.py edge: the union scene, Checker.check(full=True) 'ok' (hits, ranges, cart floor / tip)
  sys.argv=['r19hub.py','edge']+([f"PY={spec['py']}"] if spec.get('py') else [])
  import r19hub as HB;ch=HB.union_checker()
  M=dict(ch=ch,check_many=lambda Qs,ch=ch:[_row_ch(ch.check(np.asarray(q),full=True,mass=0.),okkey=True) for q in Qs])
 elif t=='stir':   # r19stir_cycle.model(sign) + r19enc_check.one: stir scene, plume rule
  import r19stir_cycle as C,r19enc_check as RC
  C.ARM=arm;M_=C.model(spec['sign'])
  M=dict(ch=M_['ch'],check_many=lambda Qs,M_=M_:[_row_rc(RC.one(M_,np.asarray(q))) for q in Qs])
 else:raise KeyError(t)
 M['md5']=hashlib.md5(M['ch'].xml.encode()).hexdigest();_SC[key]=M;return M
# ===================================================================== spline pieces
class Piece:
 """a motion piece of export.json: q(s) for s in [0, L] (periodic: s mod L); spans of clamped B-splines over the 7
 coordinates; a coordinate j listed in a span's 'sq' is stored as h with q_j = limit + sign * h^2 (exact, as stored)"""
 def __init__(self,el):
  from scipy.interpolate import BSpline
  sp=el['spline'];self.L=float(sp['length']);self.per=bool(sp.get('periodic'));self.q0=np.array(el['const_state'],float)
  self.sp=[(float(a['s0']),float(a['s1']),BSpline(np.array(a['knots'],float),np.array(a['coef'],float),int(a['degree'])),{int(j):tuple(v) for j,v in a.get('sq',{}).items()}) for a in sp['spans']]
  self.B=np.array([a[0] for a in self.sp]+[self.sp[-1][1]])
 def y(self,s,nu=0):
  s=np.atleast_1d(np.asarray(s,float))
  if self.per:r=np.mod(s,self.L);s=np.where((r<1e-12)&(s>1e-12),self.L,r)
  else:s=np.clip(s,0.,self.L)
  k=np.clip(np.searchsorted(self.B,s,side='right')-1,0,len(self.sp)-1);out=np.zeros((len(s),7))
  for j in np.unique(k):
   a,b,bs,sq=self.sp[j];m=k==j;x=s[m]
   Hs=[bs(x,n) for n in range(nu+1)] if sq else None;y=np.array(Hs[nu] if sq else bs(x,nu),float)
   for c,(lim,sg) in sq.items():
    h=[v[:,c] for v in Hs]
    y[:,c]=lim+sg*h[0]**2 if nu==0 else sg*(2*h[0]*h[1] if nu==1 else 2*(h[1]**2+h[0]*h[2]) if nu==2 else 2*(3*h[1]*h[2]+h[0]*bs(x,3)[:,c]))
   out[m]=y
  return out
 def q(self,s,nu=0):   # r19smooth.Path interface (sample_path): full states for nu = 0
  if nu:return self.y(s,nu)
  Y=self.y(s);Q=np.tile(self.q0,(len(Y),1));Q[:,COLS]=Y;return Q
 def __call__(self,x,nu=0):return self.y(x,nu)
def span_bs(bs,w,s0=0.):
 """scipy BSpline fitted in r19smooth's scaled space (coordinate x lever w) -> span in m / rad, knots shifted to start at s0"""
 t=np.asarray(bs.t,float);k=int(bs.k);a=t[k];b=t[-k-1];c=np.asarray(bs.c,float)/w
 return dict(s0=float(s0),s1=float(s0+b-a),degree=k,knots=(t-a+s0).tolist(),coef=c.tolist())
def span_line(A,B,L):
 """the straight line A -> B (7 values) over s in [0, L] as an exact clamped cubic (collinear control points)"""
 A,B=np.asarray(A,float),np.asarray(B,float)
 return dict(s0=0.,s1=float(L),degree=3,knots=[0.,0.,0.,0.,float(L),float(L),float(L),float(L)],coef=[(A+(B-A)*i/3).tolist() for i in range(4)])
def motion(name,spans,L,const,cls,check,contact=None,held=None,periodic=False,fit=None):
 return dict(type='motion',name=name,cls=cls,contact=contact,held=held,check=check,const_state=np.asarray(const,float).tolist(),
  spline=dict(length=float(L),periodic=periodic,spans=spans),fit=fit or {})
def hold(name,dur,state,jaws_to=None):
 return dict(type='hold',name=name,duration_s=float(dur),state=np.asarray(state,float).tolist(),jaws_to=None if jaws_to is None else list(map(float,jaws_to)))
# ===================================================================== kinds
def kind_of(r,f):
 if r.get('id')=='STIR_CYCLE':return 'stir'
 if 'qs' in r and 'segments' in r and 'a' in r and 'b' in r:return 'hub'
 if 'play' in r and 'grasps' in r and 'layout' in r:return 'prep'
 if 'play' in r and 'keyframes' in r and 'approach_qs' in r:return 'chain'
 raise SystemExit(f'{f}: unknown result kind')
def md5f(f):return hashlib.md5(open(f,'rb').read()).hexdigest()
def geo_md5(seq):
 """md5 of the exported geometry (every motion piece's spline + constant state + check spec): a re-check holds for it only"""
 return md5j([[e['spline'],e['const_state'],{'scene':e['check']['scene']} if 'scene' in e['check'] else {'rule':'unchecked by rule'}] for e in seq if e['type']=='motion'])   # the rule's wording is not geometry
def md5j(x):return hashlib.md5(json.dumps(x,default=float).encode()).hexdigest()
def in_range(m,Q):
 lo,hi=m.jnt_range[:,0],m.jnt_range[:,1];return bool(np.all(Q>=lo-1e-9) and np.all(Q<=hi+1e-9))
def kf_index(ctxd,Q,KF):
 """r19smooth.r17_timing's keyframe matching (in order, first local minimum within 8 mm of the keyframe's object position),
 plus the object rotation where the keyframe stores one (prep sets: 'rolled +-30' keyframes share one position):
 distance = |dp| + 0.1 m x rotation angle, threshold 8 mm + 0.1 m x 2 deg"""
 import r19smooth as S
 P,R=S.fk(ctxd,Q);po,Ro=S.obj_pose(ctxd,P,R);idx=[];i0=0
 for k in KF:
  hasR=k.get('R') is not None;dd=np.linalg.norm(po[i0:]-np.array(k['p']),axis=1)
  if hasR:dd=dd+.1*S.rotang(Ro[i0:],np.array(k['R'],float))
  ok=np.where(dd<.008+(.1*np.radians(2.) if hasR else 0.))[0]
  if not len(ok):idx.append(None);continue
  j=int(ok[0])
  while j+1<len(dd) and dd[j+1]<dd[j]:j+=1
  idx.append(i0+j);i0=i0+j
 idx[0]=0;idx[-1]=len(Q)-1
 return idx
def build_chain(f,r,kind,info):
 """chain / prep: approach-in, grasp, seat lift, play pieces (+ dwells), set down, release, retreat"""
 import r19smooth as S
 arm=r['arm'];info.update(arm=arm)
 if kind=='chain':
  cf=r['adopted']['play_recheck'];cert=json.load(open(cf))
  import r19enc_check as RC
  key=max((k for k in RC.CHAINS if cert['set'].startswith(k)),key=len);sfx=cert['set'][len(key):];py=('%g'%cert['plate_y']) if 'plate_y' in cert else None
  rc_file=RC.CHAINS[key][0][:-5]+sfx+'.json';assert md5j(json.load(open(rc_file))['play'])==md5j(r['play']),('the certificate checked another play',rc_file)
  spec=dict(type='chain_play',arm=arm,key=key,suffix=sfx,py=py);P=cert['paths'][key];cs=P[arm]
  certsum=dict(file=cf,file_md5=md5f(cf),checker='r19enc_check.py recheck: Checker.check(full=True), MuJoCo contacts + GJK lower-bound certificate, 10 mm robot-environment, 5 mm gripper/held-environment, 0 mm self, joint ranges; R11 held-box mesh rule',
   rule='stored states 2pi-unwrapped, joint-linear between them, cut so that consecutive states are <= 4 mm apart (point_bound)',states=P['states'],max_step_bound_mm=P['max_step_bound_mm'],ok=cs['ok'],hit_states=cs['hit_states'],
   out_of_range_states=cs['out_of_range_states'],min_env_reserve_mm=cs['min_env_reserve_mm'],min_env_pair=cs['min_env_pair'],min_self_reserve_mm=cs['min_self_reserve_mm'],
   approaches=r['adopted'].get('approaches'),approaches_checker='r19enc_adopt.py: approach_qs cut to <= 4 mm, Checker.check(full=True) in r17chain.py\'s empty-gripper scene of that keyframe')
 else:
  ver='r19prep5_verify' if '/prep5/' in f.replace('\\','/') else 'r19prep4_verify' if '/prep4/' in f.replace('\\','/') else 'r19prep_verify'
  cands=[f[:-5]+'_verify4mm_pot.json',f[:-5]+'_verify4mm.json'];cf=[c for c in cands if os.path.exists(c)][0];cert=json.load(open(cf))
  spec=dict(type='prep',arm=arm,file=f.replace('\\','/'),part='play',verifier=ver,kv=cert.get('potzone') or {})
  sm=cert['summary']['play'];cs=dict(ok=cert['ok'],hit_states=sm['hit_states'],min_env_reserve_mm=sm['min_reserve_mm'],min_self_reserve_mm=sm['min_self_mm'])
  certsum=dict(file=cf,file_md5=md5f(cf),checker=f'{ver}.py: Checker.check(full=True), MuJoCo contacts + GJK lower-bound certificate, 10 / 5 mm, joint ranges, food contact window (touch) on approaches'+(', R15 plume rule' if cert.get('plume_m') else ''),
   rule=cert['rule'],states={k:v['states'] for k,v in cert['summary'].items()},max_step_bound_mm=max(s_['max_spacing_mm'] for s_ in cert['segments']),ok=cert['ok'],
   hit_states={k:v['hit_states'] for k,v in cert['summary'].items()},min_env_reserve_mm={k:v['min_reserve_mm'] for k,v in cert['summary'].items()},min_self_reserve_mm={k:v['min_self_mm'] for k,v in cert['summary'].items()})
 assert certsum['ok'],f'{cf}: the certificate is not clean, nothing exported'
 M=scene(spec);ch=M['ch'];fb=S.FastBound(ch);m=ch.m
 # ---- labels: unwrap as the certificate's checker did
 if kind=='chain':Q=S.unwrap(r['play']);uw='r19smooth.unwrap (cumulative removal of the 2pi label jumps)'
 else:Q,_=M['PV'].unwrap(ch,r['play']);uw=f"{spec['verifier']}.unwrap (equivalent angle nearest the previous state, in range)"
 raw=np.array(r['play'],float);jumps=int(np.sum(np.abs(np.round(np.diff(raw[:,3:9],axis=0)/TWO))>0))
 QS,src,spm=S.sample_poly(Q,fb)
 cert_states=certsum['states'] if kind=='chain' else certsum['states']['play']
 rep=dict(stored_states=len(Q),resampled_states=len(QS),certificate_states=cert_states,reproduced=len(QS)==cert_states,max_step_bound_mm=round(spm*1e3,3))
 # reserve near every stored state (r19smooth.main): min over the certificate's sub-states of its two steps
 resv=np.full(len(Q),1e9)
 if kind=='chain' and rep['reproduced']:
  ps=P['per_state'][arm]
  for rr,sv in zip(ps,src):
   v=min(x for x in (rr['env'],rr['self'],1e9) if x is not None)
   for i in {int(math.floor(sv)),int(math.ceil(sv))}:resv[i]=min(resv[i],v)
  tolsrc='per stored state: clip(RF x its own reserve from the certificate per-state results, TMIN, TMAX)'
 else:
  v=cs['min_env_reserve_mm'] if not isinstance(cs['min_env_reserve_mm'],dict) else cs['min_env_reserve_mm']['play'];v=min(v,cs.get('min_self_reserve_mm') or 1e9);resv[:]=v
  tolsrc='uniform: clip(RF x the certificate\'s minimum play reserve, TMIN, TMAX) (no per-state reserves stored)'
 tol=np.clip(RF*np.maximum(resv,0)/1e3,TMIN,TMAX)
 if 'refit' in info:   # r19smooth's repair: the stored states near a dense re-check hit of the previous export get 1/4 of their tolerance
  for i_,sc in info['refit']['scale'].items():tol[int(i_)]*=sc
 # ---- keyframes -> stored indices (r19smooth.r17_timing), contact windows, dwells, reversals
 import kitchen16 as K
 ctxd=dict(r=r,m=m,d=ch.d,sid=m.site('R_prep').id,T=K.T_tool_obj(r['obj'],r['grasp_sense']),cfg=dict(dwell={}))
 KF=r['keyframes'];kf=kf_index(ctxd,Q,KF);nk=len(KF);N=len(Q)
 apps={a_['kf']:i for i,a_ in enumerate(r['approaches']) if r['approach_qs'][i]}
 ia=apps.get(0);ib=apps.get(nk-1) if nk>1 else None
 fixed=set()
 if ia is not None and kf[1] is not None:fixed.add((0,kf[1] if nk>2 else N-1))
 if ib is not None and kf[nk-2] is not None:fixed.add((kf[nk-2] if nk>2 else 0,N-1))
 dwk={i:float(k_.get('dwell_s') or 0) for i,k_ in enumerate(KF) if k_.get('dwell_s')}
 if not dwk and kind=='chain':dwk=dict(S.CHAINS.get(r['act'],{}).get('dwell',{}))
 dwell={}
 for k,s_ in dwk.items():
  if kf[k] is not None:dwell[kf[k]]=dwell.get(kf[k],0.)+s_
 must=set([0,N-1])|set(dwell)|{a for a,b in fixed}|{b for a,b in fixed}
 tu=S.turns(Q[:,S.DOF]/np.r_[S.R17['CW'],np.full(6,np.radians(S.R17['QW']))])
 rev=[int(i) for i in np.nonzero(tu>S.REV)[0] if min(abs(int(i)-j) for j in must)>2];stops=sorted(must|set(rev))
 segs=[(a,b,(a,b) in fixed) for a,b in zip(stops[:-1],stops[1:]) if b>a]
 smooth_ref=S.CHAINS.get(r['act']) if kind=='chain' else None
 # ---- hub roadmap relabel (one 2pi shift per joint for the whole action)
 sh=np.zeros(11);rm=None
 if kind=='chain' and arm in ROADMAP and (r.get('plate_y') is None or abs(r['plate_y']-ROADMAP[arm][1])<1e-9):
  rm=json.load(open(ROADMAP[arm][0]))
  for j,k_ in rm['action_shifts'].get(r['act'],{}).items():sh[int(j)]=TWO*k_
 Q=Q+sh
 A={}
 for nm,i in (('in',ia),('out',ib)):
  if i is None:continue
  X=np.array(r['approach_qs'][i],float)+sh;end=Q[0] if nm=='in' else Q[-1];X[:,3:9]+=np.round((end[3:9]-X[0,3:9])/TWO)*TWO;A[nm]=(i,X)
 allQ=np.vstack([Q]+[X for i,X in A.values()]);assert in_range(m,allQ),'unwrapped / relabelled states leave the joint ranges'
 info['labels']=dict(unwrap=uw,stored_2pi_label_jumps=jumps,roadmap=ROADMAP[arm][0] if rm else None,roadmap_shift_2pi=np.round(sh[3:9]/TWO).astype(int).tolist(),
  approaches='each approach relabelled by the 2pi multiple nearest its play end (= r19hub.unwrapped)',all_states_in_joint_range=True)
 # ---- pieces
 w=np.r_[1.,ch.point_bound.weights.max(0)[3:9]];Y=Q[:,COLS]*w;lo,hi=m.jnt_range[COLS,0].copy(),m.jnt_range[COLS,1].copy()
 lo[0],hi[0]=max(lo[0],CART_TRAVEL[0]),min(hi[0],CART_TRAVEL[1])
 # r19smooth main: a coordinate whose stored states touch a range limit (the spatula cart at its -1.48 m travel end) is fitted as
 # q = limit + sign * h^2, so the spline can never cross that limit (stored per span as 'sq')
 SQ={dd:((lo[dd],1.) if Q[:,COLS[dd]].min()-lo[dd]<hi[dd]-Q[:,COLS[dd]].max() else (hi[dd],-1.)) for dd in range(7) if min(Q[:,COLS[dd]].min()-lo[dd],hi[dd]-Q[:,COLS[dd]].max())<SQ_MARGIN}
 def sqd(p):return {str(k_):[float(l_),float(s_)] for k_,(l_,s_) in p.sq.items()} if p.sq else None
 def excursion(pc):
  yy=pc.y(np.linspace(0,pc.L,max(400,int(pc.L/.0002))));e=np.maximum(lo-yy,yy-hi).max(0);return float(e.max()),int(np.argmax(e))
 lab={kf[k]:(k_['label'] or f'#{k}') for k,k_ in enumerate(KF) if kf[k] is not None}
 held=r['obj'];seq=[];tests=[]
 def app_spec(i):
  if kind=='chain':return dict(type='chain_app',arm=arm,key=key,py=py,kf=r['approaches'][i]['kf'])
  return dict(spec,part=['app',i])
 def interp(X,name,cls,check,contact,held_,snap=None):
  """interpolating cubic through the states X; snap=(i, state): state i is replaced by that play end when the two
  differ only by round-off (< 0.1 mm point bound), so the junction is exact; its fit error is reported"""
  X2=X.copy();tt=np.full(len(X),1e-9);note=''
  if snap is not None:
   i,qe=snap;g=float(fb.g7(X[i,COLS]-qe[COLS])[0])
   if g<1e-4:X2[i,COLS]=qe[COLS];tt[i]=max(1e-9,g*1.01);note=f'; state {i} snapped to the play end (round-off gap {g*1e3:.2e} mm point bound)'
  Ys,ix=S.dedup(X2[:,COLS]*w,list(range(len(X2))));p=S.fit_fixed(Ys,w,X2[0],SQ);sp=span_bs(p.f,w);sp.update({'sq':sqd(p)} if p.sq else {});u=S.chord(X2[:,COLS]*w)
  tests.append((len(seq),X,u,tt));return motion(name,[sp],sp['s1'],X2[0],cls,check,contact,held_,fit=dict(kind='interpolating cubic'+note,states=len(X))),X2
 sid=m.site('R_prep').id
 def tcp_mm(X):
  P_,_=fk(m,ch.d,sid,np.asarray(X,float));return float(np.linalg.norm(P_[-1]-P_[0])*1e3),float(np.sum(np.linalg.norm(np.diff(P_,axis=0),axis=1))*1e3)
 def link(a_,b_,const,name,contact):
  L=float(np.linalg.norm((b_[COLS]-a_[COLS])*w))
  if L<1e-4:return None   # < 0.1 mm: the same state up to round-off (kept as a junction jump, reported)
  contact=contact.replace('(<= 50 mm','(%.1f mm TCP;'%tcp_mm([a_,b_])[0])
  tests.append((len(seq),np.array([a_,b_]),np.array([0.,L]),np.full(2,1e-9)))
  return motion(name,[span_line(a_[COLS],b_[COLS],L)],L,const,'contact',dict(rule=contact),contact,held,fit=dict(kind='exact straight line'))
 if 'in' in A:
  i,X=A['in'];Xr=X[::-1]
  el,Xr=interp(Xr,'grasp approach','contact',dict(scene=app_spec(i)),'grasp approach: straight, %.1f mm TCP (path %.1f mm), empty gripper, jaws open'%tcp_mm(Xr),None,snap=(len(Xr)-1,Q[0]));seq.append(el)
  seq.append(hold('grasp',GRASP_S,Xr[-1],Q[0][9:]))
  e=link(Xr[-1],Q[0],Q[0],'seat lift','support contact window at the grasp (<= 50 mm along the support normal): not a checked state, as r17chain / r19prep_verify')
  if e:seq.append(e)
 for a,b,fx in segs:
  # the fitting data: the stored states plus joint-linear points of the certified polyline between them, so that no two
  # consecutive data points are more than DENS apart by point bound (the stored states are up to 30 cm apart at the
  # subsampled joins; a spline through them alone can leave the certified polyline there by more than its reserve)
  P_=[Q[a]];T_=[tol[a]];I_=[a]
  for i in range(a,b):
   n_=1 if fx else max(1,int(math.ceil(fb(Q[i],Q[i+1])/DENS)))   # contact pieces: interpolating cubic through the stored states (1 cm steps), not densified
   for k_ in range(1,n_+1):P_.append(Q[i]+(Q[i+1]-Q[i])*k_/n_);T_.append(tol[i+1] if k_==n_ else min(tol[i],tol[i+1]));I_.append(i+1 if k_==n_ else -1)
  P_=np.array(P_);T_=np.array(T_);Yd=P_[:,COLS]*w;ud=S.chord(Yd);u=ud[[j for j,x in enumerate(I_) if x>=0]]
  Ys,ix=S.dedup(Yd,list(range(len(Yd))));nm=f"{lab.get(a,a)} -> {lab.get(b,b)}"
  if fx:p=S.fit_fixed(Ys,w,Q[a],SQ);fkind='interpolating cubic (contact window: straight grasp / release piece)';tt=np.full(b-a+1,1e-9)
  else:p,dev=S.fit_spline(Ys,w,Q[a],T_[ix],fb,sq=SQ);fkind=f'r19smooth.fit_spline: {p.kind}';tt=tol[a:b+1]
  sp=span_bs(p.f,w);sp.update({'sq':sqd(p)} if p.sq else {});pc=Piece(dict(spline=dict(length=sp['s1'],spans=[sp]),const_state=Q[a]));ex,exj=excursion(pc)
  if ex>1e-9 and not fx:
   p=S.fit_fixed(Ys,w,Q[a],SQ);fkind+=f' -> refit as interpolating cubic (the smoothing spline left the range of coordinate {exj} by {ex:.2e})';sp=span_bs(p.f,w);sp.update({'sq':sqd(p)} if p.sq else {});tt=np.full(b-a+1,1e-9)
   ex,exj=excursion(Piece(dict(spline=dict(length=sp['s1'],spans=[sp]),const_state=Q[a])))
  tests.append((len(seq),Q[a:b+1],u,tt))
  cls='contact' if fx else 'free'
  seq.append(motion(nm,[sp],sp['s1'],Q[a],cls,dict(scene=spec),'grasp / release piece of the play (straight, %.1f mm TCP (path %.1f mm), slow)'%tcp_mm(Q[a:b+1]) if fx else None,held,
   fit=dict(kind=fkind,states=b-a+1,fit_points=len(Ys),stored_index=[int(a),int(b)],n_coef=len(sp['coef']),tol_mm=[round(float(tt.min()*1e3),3),round(float(tt.max()*1e3),3)],
    range_excursion=dict(max=ex,coordinate=exj,ok=ex<=1e-9,note='max over the piece (0.2 mm grid in s) of the distance beyond the joint range / cart travel (m or rad)'))))
  if b in dwell:seq.append(hold(f"dwell at '{lab.get(b,b)}'",dwell[b],Q[b]))
 if 'out' in A:
  i,X=A['out']
  e=link(Q[-1],X[0],Q[-1],'set down','support contact window at the release (<= 50 mm along the support normal): not a checked state, as r17chain / r19prep_verify')
  if e:seq.append(e)
  el,X2=interp(X,'release retreat','contact',dict(scene=app_spec(i)),'release retreat: straight, %.1f mm TCP (path %.1f mm), empty gripper, jaws open'%tcp_mm(X),None,snap=(0,Q[-1]))
  seq.append(hold('release',GRASP_S,X2[0],X[0][9:]))
  tests[-1]=(len(seq),)+tests[-1][1:];seq.append(el)
 info.update(certificate=certsum,certificate_reproduction=rep,fit_tolerance=dict(rule=tolsrc,RF=RF,TMIN_mm=TMIN*1e3,TMAX_mm=TMAX*1e3),
  limit_coordinates={str(k_):[float(l_),float(s_)] for k_,(l_,s_) in SQ.items()},
  segmentation=dict(stops=stops,reversals=rev,fixed=sorted(fixed),dwell={str(k):v for k,v in dwell.items()},r19smooth_reference=dict(fixed=smooth_ref['fixed'],dwell=smooth_ref['dwell']) if smooth_ref else None,
   keyframe_index=kf),stored_time_s=r.get('time_s'),stored_time_note='r17chain-style nominal time (unlimited acceleration: a constant speed per stored step) incl. dwells, grasp / release and approaches',
  scale_w=w.tolist(),obj=r['obj'])
 if rm:info['roadmap']=rm
 return seq,tests,M,spec
def build_hub(f,r,info):
 import r19smooth as S,re
 d=os.path.basename(os.path.dirname(f));mm=re.match(r'hub(_py([0-9.]+))?(_(.+))?$',d);py=mm.group(2);arm=mm.group(4) or 'ur5e'
 assert r['ok'],'edge not ok'
 spec=dict(type='hub',arm=arm,py=py);M=scene(spec);ch=M['ch'];info.update(arm=arm)
 qs=np.array(r['qs'],float);idx=np.cumsum([0]+[s_['n']-1 for s_ in r['segments']]);assert idx[-1]==len(qs)-1
 w=np.r_[1.,ch.point_bound.weights.max(0)[3:9]];seq=[];tests=[]
 for j,(a,b) in enumerate(zip(idx[:-1],idx[1:])):
  A_,B_=qs[a],qs[b];L=float(np.linalg.norm((B_[COLS]-A_[COLS])*w));D=(B_[COLS]-A_[COLS])*w
  u=((qs[a:b+1][:,COLS]-A_[COLS])*w)@D/max(D@D,1e-30)*L
  tests.append((len(seq),qs[a:b+1],u,np.full(b-a+1,1e-9)))
  seq.append(motion(f'segment {j}'+(' (to a via)' if b<idx[-1] else ''),[span_line(A_[COLS],B_[COLS],L)],L,A_,'free',dict(scene=spec),None,None,fit=dict(kind='exact straight line (joint space), as checked',states=b-a+1)))
 certsum=dict(file=f,file_md5=md5f(f),checker='r19hub.py edge: union scene (lever closed + open, lid on the pot + in the rack, dishes at both plating spots), Checker.check(full=True) ok (hits, joint ranges, cart floor / tip)',
  rule='straight (cart, joint) segments cut so that consecutive states are <= 4 mm apart (point_bound.segment_bound per piece)',states=r['states_checked'],max_step_bound_mm=max(s_['max_step_bound_mm'] for s_ in r['segments']),
  ok=r['ok'],hit_states=0,min_env_reserve_mm=r['min_reserve_mm'],min_self_reserve_mm=r['min_self_mm'],method=r['method'])
 info.update(certificate=certsum,labels=dict(note='the edge states are stored in the roadmap labels (hubs.json q_shifted): no unwrap needed',stored_2pi_label_jumps=int(np.sum(np.abs(np.round(np.diff(qs[:,3:9],axis=0)/TWO))>0))),
  stored_time_s=r['time_s'],stored_time_note='r19hub metrics: r17chain caps (joints 60 deg/s, cart 0.25 m/s), no acceleration limit, + 0.6 s',scale_w=w.tolist(),
  certificate_reproduction=dict(stored_states=len(qs),note='the stored states ARE the certified states'))
 return seq,tests,M,spec
def build_stir(f,L_,info):
 arm=L_['arm'];cert=L_['verification']['certificate'];sign=-1 if 'jaw sense -1' in cert['scene'] else 1
 spec=dict(type='stir',arm=arm,sign=sign);M=scene(spec);info.update(arm=arm)
 G=L_['geometry'];q0=np.array(G['state_const'],float);spans=[]
 for g in G['segments']:
  c=np.array(g['coef'],float);c=np.c_[np.full(len(c),q0[0]),c];a=g['local'][0]
  sp=dict(s0=float(g['s0']),s1=float(g['s1']),degree=int(g['k']),knots=(np.array(g['knots'],float)-a+g['s0']).tolist(),coef=c.tolist(),name=g['name'])
  if g.get('sq'):sp['sq']={str(int(j)+1):v for j,v in g['sq'].items()}
  spans.append(sp)
 el=motion('stir cycle (periodic, 5 strokes)',spans,G['length'],q0,'stir',dict(scene=spec),'stir: blade on the wok steel by design (R15 strokes); checked as stored, plume rule','spatula',periodic=True,
  fit=dict(kind='the stored certified geometry, unchanged (C2 B-spline segments)',segments=[g['name'] for g in G['segments']]))
 # certified states -> their parameter on the stored geometry (nearest point per segment kind, refined)
 pc=Piece(el);Qc=np.array(L_['states']['q'],float);kinds=L_['states']['kinds'];names=[g['name'] for g in G['segments']];u=np.zeros(len(Qc))
 from scipy.spatial import cKDTree
 for j,nm in enumerate(names):
  ii=[i for i,k_ in enumerate(kinds) if k_==nm]
  if not ii:continue
  a,b=spans[j]['s0'],spans[j]['s1'];g=np.linspace(a,b,20001);Yg=pc.y(g);tr=cKDTree(Yg[:,1:]);_,nn=tr.query(Qc[ii][:,3:9])
  x=g[nn];T=Qc[ii][:,3:9]
  for _ in range(8):   # Gauss-Newton on |q(x) - state|^2 inside the segment (vectorized), clipped to its ends
   y0=pc.y(x)[:,1:]-T;y1=pc.y(x,1)[:,1:];y2=pc.y(x,2)[:,1:]
   x=np.clip(x-np.sum(y0*y1,1)/np.maximum(np.sum(y1*y1,1)+np.sum(y0*y2,1),1e-12),a,b)
  u[ii]=x
 tests=[(0,Qc,u,np.full(len(Qc),1e-6))]
 TL_=L_['time_law'];lim=TL_['limits']
 info.update(certificate=dict(cert,file=f,file_md5=md5f(f)),labels=dict(note='the stored cycle labels (r19stir_cycle.label_shift rule; the entry is run with these labels)'),
  stored_time_s=TL_.get('three_cycles_from_rest_s'),stored_time_note='three cycles from rest (the stored law); steady period %.3f s'%TL_['period_s'],stir_limits=lim,
  certificate_reproduction=dict(stored_states=len(Qc),note='the certified states (stir scene) lie on the stored geometry: state fit = their distance to it'))
 return [el],tests,M,spec
# ===================================================================== time law
def fk(m,d,sid,Q):
 import mujoco
 P=np.zeros((len(Q),3));R=np.zeros((len(Q),3,3))
 for i,q in enumerate(Q):d.qpos[:]=q;mujoco.mj_kinematics(m,d);P[i]=d.site_xpos[sid];R[i]=d.site_xmat[sid].reshape(3,3)
 return P,R
def rotspeed(R):
 from scipy.spatial.transform import Rotation
 return np.linalg.norm(Rotation.from_matrix(R[1:]@np.transpose(R[:-1],(0,2,1))).as_rotvec(),axis=1)
def limits_for(el,arm):
 import arms
 c=LIM['contact'] if el['cls']=='contact' else LIM['free'];vj=c['v_joint'] or None
 V=np.r_[LIM['v_cart'],np.radians(vj if vj else np.array(arms.speeds(arm)))*np.ones(6)]
 A=np.r_[LIM['a_cart'],np.full(6,LIM['a_joint'])];J=np.r_[LIM['j_cart'],np.full(6,LIM['j_joint'])]
 wt=LIM['w_tcp_wok'] if (el.get('held')=='wok' and el['cls']=='free') else c['w_tcp']
 return V,A,J,c['v_tcp'],wt
def piece_law(el,M,arm):
 """rest-to-rest jerk-limited law of one motion piece: r19stir2_law.timelaw + a TCP speed / rotation cap"""
 import r19stir2_law as TL
 pc=Piece(el);L=pc.L;V,A,J,vt,wt=limits_for(el,arm);m=M['ch'].m;d=M['ch'].d;sid=m.site('R_prep').id
 n=max(60,int(math.ceil(L/.001))+1);sg=np.linspace(0,L,n);P,R=fk(m,d,sid,pc.q(sg));ds=np.diff(sg)
 dp=np.linalg.norm(np.diff(P,axis=0),axis=1)/ds;dw=rotspeed(R)/ds;seg=np.minimum((vt/np.maximum(dp,1e-12))**2,(np.radians(wt)/np.maximum(dw,1e-12))**2)
 capg=np.r_[seg[0],np.minimum(seg[1:],seg[:-1]),seg[-1]];capg=np.minimum(capg,np.r_[capg[1:],capg[-1]]);capg=np.minimum(capg,np.r_[capg[0],capg[:-1]]);capg=np.minimum(capg,1e12)
 capf=lambda s:np.interp(np.atleast_1d(s),sg,capg)
 path=TL.PathN([(pc.y,0.,L)],7);tl=TL.timelaw(path,V,A,capf,0.,0.,LIM['W'],iters=int(KV.get('ITERS',60)),J=J)
 t,s,sd=tl['t'],tl['s'],tl['sd'];stretch=None
 if not tl['converged']:   # uniform stretch of the last law (v / f, a / f^2, jerk / f^3, cap / f), resampled on the 2 ms grid
  wr=tl['worst'];f=max(1.,wr.get('v',1)**1,wr.get('cap',1)**1,wr.get('a',1)**.5,wr.get('j',1)**(1/3))*1.002
  for _ in range(8):
   tg=np.arange(0,t[-1]*f+H/2,H);s2=np.interp(tg,t*f,s);sd2=np.gradient(s2,H);rat,pk=TL.verify(path,tg,s2,sd2,V,A,capf,J);w2={k_:float(v_.max()) for k_,v_ in rat.items()}
   if max(w2.values())<=1+1e-3:break
   f*=max(w2.values())**.34
  t,s,sd=tg,s2,sd2;stretch=round(f,4);tl=dict(tl,worst={k_:round(v_,4) for k_,v_ in w2.items()},peaks=pk)
 return dict(t=t,s=s,sd=sd,time_s=float(t[-1]),worst=tl['worst'],converged=bool(tl['converged']) or (stretch is not None and max(tl['worst'].values())<=1+1e-3),iters=tl['iters'],stretch=stretch,
  limits=dict(v=V.tolist(),a=A.tolist(),j=J.tolist(),v_tcp=vt,w_tcp_degps=wt))
def stir_law(el,L_,f):
 """the stored from-rest jerk-limited law of the stir entry (3 cycles), or (if not found) generated with the entry's own
 limits by r19stir2_law.timelaw exactly as r19stir2_retime / r19spill_cycle"""
 TL_=L_['time_law'];lim=TL_['limits'];J=lim.get('jerk_degps3');cands=[]
 for c in L_['verification']['certificate'].get('cache','').split(','):
  c=c.strip()
  if c:cands.append(os.path.join(os.path.dirname(c),f'fromrest_j{int(J)}.npz') if J else None)
 cands.append(f"results/r19/stir/retime/fromrest_{L_['arm']}_j{int(J)}.npz" if J else None)
 for c in [c for c in cands if c]:
  if os.path.exists(c):
   z=np.load(c);t,s,sd=z['t'],z['s'],z['sd'];return dict(t=t,s=s,sd=sd,time_s=float(t[-1]),source=c,source_md5=md5f(c),converged=True,worst=None,
    limits=dict(v_degps=lim['v_degps'],A_degps2=lim.get('A_degps2_used'),J_degps3=J,W_s=lim.get('W_s')))
 raise SystemExit('no stored from-rest law for this stir entry (generate it with r19stir2_retime.py first)')
# ===================================================================== compose, sample, check
def compose(seq,laws):
 """the 500 Hz stream: motion pieces by their laws, holds as constant states (jaws ramp linearly); returns t, Q (n x 11),
 element index per sample, junction jumps"""
 T=[];Qs=[];E=[];t0=0.;jumps=[]
 for k,el in enumerate(seq):
  if el['type']=='hold':
   n=max(1,int(round(el['duration_s']/H)));q=np.tile(np.array(el['state'],float),(n+1,1))
   j0=Qs[-1][-1][9:].copy() if Qs else q[0,9:];j1=np.array(el['jaws_to'],float) if el['jaws_to'] else j0;fr=np.linspace(0,1,n+1)[:,None];q[:,9:]=j0+(j1-j0)*fr
   tt=t0+np.arange(n+1)*H
  else:
   pc=Piece(el);lw=laws[k];q=pc.q(lw['s']);tt=t0+np.arange(len(lw['s']))*H
  if Qs:
   jumps.append(float(np.abs(Qs[-1][-1][:9]-q[0][:9]).max()));q=q[1:];tt=tt[1:]
  T.append(tt);Qs.append(q);E.append(np.full(len(q),k));t0=float(tt[-1]) if len(tt) else t0
 return np.concatenate(T),np.vstack(Qs),np.concatenate(E),jumps
def fd(X,h=H):
 v=np.gradient(X,h,axis=0);a=np.gradient(v,h,axis=0);j=np.gradient(a,h,axis=0);return v,a,j
def limit_report(t,Q,E,seq,arm,M,stir=None):
 """round trip 3: speed / acceleration / jerk of the sampled stream (finite differences on the 2 ms grid) against the
 limits of the law, per coordinate; TCP speed by forward kinematics"""
 X=Q[:,COLS];v,a,j=fd(X);ok=True;out={}
 if stir:
  Vl=np.r_[1e9,np.radians(stir['v_degps'])];Al=np.r_[1e9,np.full(6,np.radians(stir['A_degps2']))];Jl=np.r_[1e9,np.full(6,np.radians(stir['J_degps3']))]
  rv=np.abs(v)/Vl;ra=np.abs(a)/Al;rj=np.abs(j)/Jl
 else:
  VV=np.zeros((len(t),7))
  for k,el in enumerate(seq):
   m_=E==k
   if el['type']=='motion':VV[m_]=limits_for(el,arm)[0]
   else:VV[m_]=1e9
  Al=np.r_[LIM['a_cart'],np.full(6,LIM['a_joint'])];Jl=np.r_[LIM['j_cart'],np.full(6,LIM['j_joint'])];rv=np.abs(v)/VV;ra=np.abs(a)/Al;rj=np.abs(j)/Jl
 out=dict(max_ratio=dict(v=round(float(rv.max()),4),a=round(float(ra.max()),4),j=round(float(rj.max()),4)),
  peak=dict(cart_v_mps=round(float(np.abs(v[:,0]).max()),4),cart_a_mps2=round(float(np.abs(a[:,0]).max()),4),cart_j_mps3=round(float(np.abs(j[:,0]).max()),3),
   joint_v_degps=np.degrees(np.abs(v[:,1:]).max(0)).round(2).tolist(),joint_a_degps2=np.degrees(np.abs(a[:,1:]).max(0)).round(2).tolist(),joint_j_degps3=np.degrees(np.abs(j[:,1:]).max(0)).round(1).tolist()),
  limits=dict(joint_a_degps2=round(float(np.degrees(Al[1])),2),joint_j_degps3=round(float(np.degrees(Jl[1])),1),cart_a_mps2=None if stir else LIM['a_cart'],cart_j_mps3=None if stir else LIM['j_cart'],
   joint_v_degps=sorted(set(np.degrees(np.r_[[limits_for(el,arm)[0][1] for el in seq if el['type']=='motion']]).round(2).tolist())) if not stir else stir['v_degps'][0]),method='np.gradient (central differences) of the 500 Hz samples, three times')
 m=M['ch'].m;d=M['ch'].d;sid=m.site('R_prep').id;P,R=fk(m,d,sid,Q);vt=np.linalg.norm(np.gradient(P,H,axis=0),axis=1)
 if not stir:
  cap=np.full(len(t),1e9)
  for k,el in enumerate(seq):
   if el['type']=='motion':cap[E==k]=limits_for(el,arm)[3]
  out['tcp']=dict(peak_mps=round(float(vt.max()),4),max_ratio_to_cap=round(float((vt/cap).max()),4))
 else:out['tcp']=dict(peak_mps=round(float(vt.max()),4))
 out['ok']=bool(max(out['max_ratio'].values())<=1.01)
 return out
def state_fit(d,M,seq):
 """round trip 1, from export.json + states.npz alone: the stored states vs the exported spline at their parameters"""
 import r19smooth as S
 E_=json.load(open(f'{d}/export.json'));z=np.load(f'{d}/states.npz');fb=S.FastBound(M['ch']);rows=[];allok=True
 for k,el in enumerate(E_['sequence']):
  if f'q_{k}' not in z:continue
  pc=Piece(el);Qs=z[f'q_{k}'];u=z[f'u_{k}'];tol=z[f'tol_{k}'];Qe=pc.q(u);D=Qs-Qe
  pb=fb.g7(D[:,COLS]);ex=int(np.sum(pb>tol+1e-9))
  rows.append(dict(element=k,name=el['name'],states=len(Qs),max_abs_rad=float(np.abs(D[:,3:9]).max()),max_abs_cart_mm=float(np.abs(D[:,0]).max()*1e3),max_point_bound_mm=float(pb.max()*1e3),
   tol_mm=[float(tol.min()*1e3),float(tol.max()*1e3)],over_tol=ex,const_ok=bool(np.abs(D[:,[1,2]]).max()<1e-12)))
  allok&=ex==0
 return dict(ok=bool(allok),states=int(sum(r_['states'] for r_ in rows)),max_point_bound_mm=max(r_['max_point_bound_mm'] for r_ in rows),max_abs_rad=max(r_['max_abs_rad'] for r_ in rows),
  max_abs_cart_mm=max(r_['max_abs_cart_mm'] for r_ in rows),pieces=rows,
  metric='global point bound (r19smooth.FastBound.g7, the bound on the displacement of every robot / held point) of the difference stored state - spline(parameter)')
def refit_scale(d):
 """REFIT=1 (the r19smooth.py repair round): the dense re-check hits of the PREVIOUS export of this name (recheck.json, made
 on exactly that geometry) -> the nearest stored play states (+-3) of each hit get x 1/4 tolerance; cumulative over rounds
 (refit.json); the hit pieces are then refitted tighter by the export"""
 E_=json.load(open(f'{d}/export.json'));rc=json.load(open(f'{d}/recheck.json'));z=np.load(f'{d}/states.npz')
 assert rc['geometry_md5']==E_['geometry_md5'],'recheck.json is not of the current export'
 old=json.load(open(f'{d}/refit.json')) if os.path.exists(f'{d}/refit.json') else dict(scale={},rounds=[])
 scale={int(k):v for k,v in old['scale'].items()};mark=set();unrep=[]
 for p in rc['pieces']:
  if not p.get('hit_s'):continue
  el=E_['sequence'][p['element']];si=el.get('fit',{}).get('stored_index')
  if si is None or f"u_{p['element']}" not in z.files or el['cls']!='free':unrep.append(p['element']);continue
  u=z[f"u_{p['element']}"]
  for s_ in p['hit_s']:
   i=int(np.argmin(np.abs(u-s_)))+si[0]
   for j in range(max(si[0],i-3),min(si[1],i+3)+1):mark.add(j)
 for j in mark:scale[j]=scale.get(j,1.)*.25
 out=dict(scale={str(k):v for k,v in sorted(scale.items())},rounds=old['rounds']+[dict(from_geometry_md5=E_['geometry_md5'],hit_states=rc['hit_states'],states_tightened=len(mark),unrepairable_elements=unrep)])
 json.dump(out,open(f'{d}/refit.json','w'),indent=1);print('refit: tolerance x 1/4 at',len(mark),'stored states; unrepairable elements',unrep,flush=True)
 return out
def reverse_seq(seq,tests):
 """the same geometry run backwards (R19_MOTION_LIBRARY rule 4): pieces reversed, holds re-attached"""
 n=len(seq);out=[];T={}
 for k in range(n-1,-1,-1):
  el=json.loads(json.dumps(seq[k]))
  if el['type']=='motion':
   L=el['spline']['length'];sps=[]
   for sp in el['spline']['spans'][::-1]:
    kn=np.array(sp['knots'],float);sps.append(dict(sp,s0=L-sp['s1'],s1=L-sp['s0'],knots=(L-kn[::-1]).tolist(),coef=sp['coef'][::-1]))
   el['spline']['spans']=sps;el['name']=el['name']+' (reversed)'
  out.append(el)
 for (k,X,u,tol) in tests:L=seq[k]['spline']['length'];T[n-1-k]=(n-1-k,X[::-1],L-u[::-1],tol[::-1])
 for k,el in enumerate(out):   # a hold sits at the end state of the element before it; its jaws go to the next motion's jaws
  if el['type']=='hold':
   nx=next((e for e in out[k+1:] if e['type']=='motion'),None);el['jaws_to']=nx['const_state'][9:] if nx else el['state'][9:]
   el['name']={'grasp':'release','release':'grasp'}.get(el['name'],el['name'])
   if k>0 and out[k-1]['type']=='motion':pc=Piece(out[k-1]);el['state']=pc.q(np.array([pc.L]))[0].tolist()
 return out,[T[k] for k in sorted(T)]
# ===================================================================== commands
def export():
 import r19stir2_law   # noqa: before any arm is set (it imports r19stir_cycle, which sets $ARM)
 f=KV['FILE'].replace('\\','/');r=json.load(open(f));kind=kind_of(r,f);t0=time.monotonic()
 name=KV.get('NAME') or (os.path.basename(os.path.dirname(f))+'__'+os.path.basename(f)[:-5] if kind=='hub' else os.path.basename(f)[:-5])
 if KV.get('REVERSE')=='1':name+='__reversed'
 d=f'{OUT}/{name}';info=dict(kind=kind)
 if KV.get('REFIT')=='1':info['refit']=refit_scale(d)
 if kind in ('chain','prep'):seq,tests,M,spec=build_chain(f,r,kind,info)
 elif kind=='hub':seq,tests,M,spec=build_hub(f,r,info)
 else:seq,tests,M,spec=build_stir(f,r,info)
 if KV.get('REVERSE')=='1':seq,tests=reverse_seq(seq,tests)
 arm=info['arm'];info['certificate']['scene_spec']=spec;info['certificate']['scene_model_md5_now']=M['md5']   # md5 of the checker's model XML as rebuilt today
 os.makedirs(d,exist_ok=True)   # only once the set built (a refused certificate leaves no folder)
 import arms
 for k,el in enumerate(seq):el['id']=k
 # ---- time laws
 laws={}
 for k,el in enumerate(seq):
  if el['type']!='motion':continue
  laws[k]=stir_law(el,r,f) if kind=='stir' else piece_law(el,M,arm)
  print(f"  {k:2d} {el['name'][:60]:60s} {el['cls']:7s} L {el['spline']['length']:.3f}  T {laws[k]['time_s']:.2f} s",'' if laws[k]['converged'] else 'NOT CONVERGED','' if not laws[k].get('stretch') else f"stretch {laws[k]['stretch']}",flush=True)
 t,Q,E,jumps=compose(seq,laws)
 # ---- hubs
 hubs=dict(start=dict(state=Q[0].tolist(),kind='stop (rest)'),end=dict(state=Q[-1].tolist(),kind='stop (rest)'))
 if info.get('roadmap'):
  rm=info.pop('roadmap');act=r['act'];ends=[(e,v) for e,v in rm['endpoints'].items() if v['action']==act]
  match={e:dict(max_abs_diff_start=float(np.abs(np.array(v['q_shifted'])-Q[0]).max()),max_abs_diff_end=float(np.abs(np.array(v['q_shifted'])-Q[-1]).max())) for e,v in ends}
  hubs['roadmap_match']=dict(roadmap=ROADMAP[arm][0],endpoints=match,note='an endpoint equal to the start or end hub (diff ~ 0) joins the roadmap edges with no motion in between (R19_MOTION_LIBRARY rule 1)')
 # ---- export.json + states.npz
 for k,el in enumerate(seq):
  if k in laws:lw=laws[k];el['time_law']=dict(duration_s=round(lw['time_s'],4),converged=lw['converged'],worst_ratio=lw.get('worst'),stretch=lw.get('stretch'),limits=lw['limits'],**({'source':lw['source'],'source_md5':lw['source_md5']} if 'source' in lw else {}))
 tl_total=float(t[-1])
 out=dict(format=FORMAT,name=name,source=dict(file=f,md5=md5f(f)),arm_name=arms.ARMS[arm]['name'],reversed=KV.get('REVERSE')=='1',
  state=STATE,spline_coords='[carriage_x, q1..q6] (m, rad); the other state values are const_state of the piece',
  joint_convention='joint values are the sim joint coordinates (Menagerie UR5e / vendor URDF FR5), in the joint order q1..q6 = base / shoulder / elbow / wrist 1-3; zero and sign must match the controller at commissioning [E]')
 out.update(info);out.pop('stir_limits',None)
 out.update(hubs=hubs,sequence=seq,
  time_law=dict(method='r19stir2_law.timelaw per motion piece, rest to rest (closed-form TOPP-RA + r19smooth erosion / moving-average filter W + local slow-downs until every limit holds on the 2 ms grid) + TCP speed / rotation cap' if kind!='stir' else 'the stored from-rest jerk-limited law of the stir entry (3 cycles)',
   limits=LIM if kind!='stir' else info['stir_limits'],sources=LIM_SRC if kind!='stir' else None,total_s=round(tl_total,3),stored_time_s=info.get('stored_time_s'),junction_max_jump=max(jumps) if jumps else 0.),
  playback=dict(rate_hz=500,stream='stream.csv',columns='t_s, carriage_x_m, base_y_m, base_yaw_rad, q1..q6_rad, finger_l_m, finger_r_m, element'))
 json.dump(out,open(f'{d}/export.json','w'),default=float)
 np.savez(f'{d}/states.npz',**{f'{p}_{k}':v for k,X,u,tol in tests for p,v in (('q',X),('u',u),('tol',tol))})
 # ---- round trip 1 (from the files) and 3 (the stream)
 sf=state_fit(d,M,seq)
 lr=limit_report(t,Q,E,seq,arm,M,stir=None if kind!='stir' else dict(v_degps=r['time_law']['limits']['v_degps'],A_degps2=r['time_law']['limits']['A_degps2_used'],J_degps3=r['time_law']['limits']['jerk_degps3']))
 hdr='t_s,carriage_x_m,base_y_m,base_yaw_rad,q1_rad,q2_rad,q3_rad,q4_rad,q5_rad,q6_rad,finger_l_m,finger_r_m,element'
 with open(f'{d}/stream.csv','w',newline='') as fh:
  fh.write(hdr+'\n')
  for tt,q,e in zip(t,Q,E):fh.write(f'{tt:.3f},'+','.join(f'{x:.10f}' for x in q)+f',{int(e)}\n')
 import r19export_writers as WR
 wr=WR.write_for_arm(d,arm)
 out['geometry_md5']=geo_md5(seq)
 out['roundtrip']=dict(state_fit=sf,limits=lr,writers=wr,dense_recheck='see recheck.json (python r19export.py recheck NAME=%s)'%name)
 out['elapsed_s']=round(time.monotonic()-t0,1);json.dump(out,open(f'{d}/export.json','w'),default=float)
 print(name,'elements',len(seq),'motion',sum(1 for e in seq if e['type']=='motion'),'T %.2f s (stored %s)'%(tl_total,info.get('stored_time_s')),
  'state fit max %.4f mm ok %s'%(sf['max_point_bound_mm'],sf['ok']),'limits',json.dumps(lr['max_ratio']),'tcp',json.dumps(lr['tcp']),'writers',json.dumps({k_:v_.get('max_ratio') for k_,v_ in wr.items()}),'%.0f s'%out['elapsed_s'],flush=True)
# ---------------------------------------------------------------- recheck (round trip 2)
def _sample(args):
 spec,el=args;import r19smooth as S;M=scene(spec);pc=Piece(el)
 if pc.per:pc.per=False   # one period (s in [0, L]): the cycle repeats the same states
 Qs,s,sp=S.sample_path(pc,S.FastBound(M['ch']));return Qs.tolist(),float(sp),M['md5'],s.tolist()
def _chk(args):
 spec,Qs=args;return scene(spec)['check_many'](Qs)
def recheck():
 """NAME=<name>[,<name>...]: the exports' motion pieces grouped by scene spec (one pool per scene, shared by the exports)"""
 import multiprocessing as mp
 names=KV['NAME'].split(',');WK=int(KV.get('WORKERS',20));t0=time.monotonic();EX={n:json.load(open(f'{OUT}/{n}/export.json')) for n in names}
 groups={};pieces={n:[] for n in names};scenes={n:[] for n in names}
 for n,E_ in EX.items():
  for el in E_['sequence']:
   if el['type']!='motion':continue
   if 'scene' in el['check']:groups.setdefault(json.dumps(el['check']['scene'],sort_keys=True),[]).append((n,el))
   else:pieces[n].append(dict(element=el['id'],name=el['name'],checked=False,rule=el['check']['rule']))
 for gk,els in groups.items():
  spec=json.loads(gk);big=spec['type'] in ('chain_play','hub','stir') or (spec['type']=='prep' and spec['part']=='play')
  with mp.Pool(WK if big else min(WK,6)) as pool:
   smp=pool.map(_sample,[(spec,el) for n,el in els],chunksize=1)
   jobs=[];own=[]
   for k,(Qs,sp,md5,ss) in enumerate(smp):
    for i in range(0,len(Qs),40):jobs.append((spec,Qs[i:i+40]));own.append(k)
   res=pool.map(_chk,jobs,chunksize=1)
  rows=[[] for _ in els]
  for k,r_ in zip(own,res):rows[k]+=r_
  for (n,el),(Qs,sp,md5,ss),rs in zip(els,smp,rows):
   if not any(s_['spec']==spec for s_ in scenes[n]):scenes[n].append(dict(spec=spec,model_md5=md5))
   Qa=np.array(Qs);bad=[i for i,x in enumerate(rs) if x['bad']];env=[x['env'] for x in rs if x['env'] is not None];se=[x['self'] for x in rs if x['self'] is not None];pl=[x['plume'] for x in rs if x.get('plume') is not None]
   cart=Qa[:,0]
   pieces[n].append(dict(element=el['id'],name=el['name'],checked=True,scene=spec['type']+(':'+str(spec.get('part',spec.get('kf',''))) if spec['type'] in ('prep','chain_app') else ''),states=len(rs),max_step_bound_mm=round(sp*1e3,3),hit_states=len(bad),
    out_of_range_states=sum(1 for x in rs if not x['ranges']),first_hits=[(i,rs[i]['hits']) for i in bad[:3]],min_env_reserve_mm=round(min(env),2) if env else None,min_self_reserve_mm=round(min(se),2) if se else None,
    min_plume_mm=round(min(pl),2) if pl else None,cart_travel_ok=bool(cart.min()>=CART_TRAVEL[0]-1e-9 and cart.max()<=CART_TRAVEL[1]+1e-9) or bool(cart.min()==cart.max()),
    hit_s=[ss[i] for i in bad][:400]))
   p_=pieces[n][-1];print(f"  {n[:40]:40s} {el['id']:2d} {el['name'][:40]:40s} {spec['type']:10s} states {len(rs):5d} step {sp*1e3:.3f} mm hits {len(bad)} env {p_['min_env_reserve_mm']} self {p_['min_self_reserve_mm']}"+(f" plume {p_['min_plume_mm']}" if pl else ''),'%.0f s'%(time.monotonic()-t0),flush=True)
 for n,E_ in EX.items():
  ps=sorted(pieces[n],key=lambda p:p['element']);ck=[p for p in ps if p['checked']]
  out=dict(name=n,geometry_md5=geo_md5(E_['sequence']),rule='every motion piece of export.json (rebuilt from the JSON alone) cut so that consecutive states are <= 4 mm apart (r19smooth.sample_path: point_bound over sub-steps <= 0.5 mm); every state through the checker of its certificate (scene spec)',
   ok=all(p['hit_states']==0 for p in ck),states=sum(p['states'] for p in ck),hit_states=sum(p['hit_states'] for p in ck),max_step_bound_mm=max(p['max_step_bound_mm'] for p in ck),
   min_env_reserve_mm=min((p['min_env_reserve_mm'] for p in ck if p['min_env_reserve_mm'] is not None),default=None),min_self_reserve_mm=min((p['min_self_reserve_mm'] for p in ck if p['min_self_reserve_mm'] is not None),default=None),
   min_plume_mm=min((p['min_plume_mm'] for p in ck if p['min_plume_mm'] is not None),default=None),unchecked_by_rule=[(p['element'],p['name']) for p in ps if not p['checked']],
   cart_travel_ok=all(p['cart_travel_ok'] for p in ck),scenes=scenes[n],pieces=ps,elapsed_s_command=round(time.monotonic()-t0,1),date=time.strftime('%Y-%m-%d'))
  json.dump(out,open(f'{OUT}/{n}/recheck.json','w'),indent=1,default=float)
  print(n,'recheck ok',out['ok'],'states',out['states'],'hits',out['hit_states'],'min env',out['min_env_reserve_mm'],'self',out['min_self_reserve_mm'],'%.0f s'%out['elapsed_s_command'])
# ---------------------------------------------------------------- report
def report():
 rows=[]
 for d in sorted(glob.glob(f'{OUT}/*/export.json')):
  E_=json.load(open(d));dd=os.path.dirname(d);rc=json.load(open(dd+'/recheck.json')) if os.path.exists(dd+'/recheck.json') else None;rt=E_.get('roundtrip',{})
  mo=[e for e in E_['sequence'] if e['type']=='motion'];sf=rt.get('state_fit',{});lr=rt.get('limits',{})
  cert=E_.get('certificate',{});rows.append(dict(name=E_['name'],kind=E_['kind'],arm=E_['arm'],reversed=E_.get('reversed'),stored_states=sum(p['states'] for p in sf.get('pieces',[])),
   pieces=len(mo),holds=len(E_['sequence'])-len(mo),max_state_fit_mm=sf.get('max_point_bound_mm'),state_fit_ok=sf.get('ok'),
   recheck_states=rc['states'] if rc else None,recheck_hits=rc['hit_states'] if rc else None,recheck_ok=rc['ok'] if rc else None,recheck_min_env_mm=rc['min_env_reserve_mm'] if rc else None,
   recheck_min_self_mm=rc['min_self_reserve_mm'] if rc else None,recheck_min_plume_mm=rc['min_plume_mm'] if rc else None,unchecked_by_rule=len(rc['unchecked_by_rule']) if rc else None,
   time_s=E_['time_law']['total_s'],stored_time_s=E_['time_law']['stored_time_s'],peak=lr.get('peak'),max_ratio=lr.get('max_ratio'),limits=lr.get('limits'),tcp=lr.get('tcp'),
   writers={k:v.get('max_ratio') for k,v in rt.get('writers',{}).items()},cert_states=cert.get('states'),cert_min_env_mm=cert.get('min_env_reserve_mm'),
   roadmap_match=E_['hubs'].get('roadmap_match',{}).get('endpoints'),junction_max_jump=E_['time_law'].get('junction_max_jump'),
   recheck_current=(rc is not None and rc.get('geometry_md5')==E_.get('geometry_md5'))))
 json.dump(rows,open(f'{OUT}/summary.json','w'),indent=1,default=float)
 for r_ in rows:
  pk=r_['peak'] or {};print(f"| {r_['name']} | {r_['stored_states']} | {r_['pieces']} | {r_['max_state_fit_mm']:.3g} | {r_['recheck_states']} / {r_['recheck_hits']} | {r_['time_s']:.1f} / {r_['stored_time_s']} | "
   f"{max(pk.get('joint_v_degps',[0])):.1f}, {max(pk.get('joint_a_degps2',[0])):.1f}, {max(pk.get('joint_j_degps3',[0])):.0f} | {json.dumps(r_['max_ratio'])} |")
if __name__=='__main__':
 {'export':export,'recheck':recheck,'report':report}[CMD]()
