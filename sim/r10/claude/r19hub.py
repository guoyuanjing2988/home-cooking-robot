"""R19 hub roadmap: pre-verified free moves of the EMPTY arm between the checked whole actions.

Why: r17seq.py / meal16.py join the checked actions with ESTIMATED, unchecked free moves
(cart |dx|/0.25 m/s + 1 s + arm 90 deg at 90 deg/s + 0.6 s). Here every free move is a path that
the unchanged checker passes at every state, so any sequence of actions joined through the hubs
is checked by construction.

Free-move endpoints (nodes 'E'): the state where each checked action hands the arm back empty, i.e.
the END of its grasp approach / release retreat (approach_qs[k][-1]: jaws open 25 mm, gripper 6 cm
back from the grasp). play[0] / play[-1] are the arm HOLDING the object (8 mm lifted), the approach
between them belongs to the action and was checked by r17chain.py.
 WOK      results/r17/chain_wok_s-1_final.json      (start = end; also the 2nd plating spot chain)
 LEV_C    results/r17/chain_lever_s+1_final.json    faucet lever closed (open starts / close ends here)
 LEV_O    same file                                 lever open (open ends / close starts here)
 LID_POT  results/r17/chain_lid_s-1_final.json      lid on the pot (lid off starts / lid on ends)
 LID_RACK same file                                 lid in the rack
 SPIDER   results/r17/chain_spider_s+1_final.json   spider on its rest (start = end)
 SPAT     results/r17/chain_spatula_s-1_r18roll-1.15_.30.json  spatula flat on the counter, (-1.15, .30)

Scene of every free move (one 'union' checker): the R18 kitchen of r17chain.py (BASE, the spatula on
its R18b rest SPATREST=-1.15,.30 SPATELEV=8 SPATROLL=180, spider on its rest, ladle off) with BOTH
positions of every object that the actions move while the arm is free elsewhere: faucet lever closed
AND open (30 deg), lid on the pot AND in the rack, a dish on BOTH plating spots (x .43 and .17).
Clearance is pairwise, so a state that passes this scene passes every combination: an edge is valid
in any world state of a meal, which is what makes sequences 'checked by construction'.
Joint angles: the actions were planned with arbitrary multi-turn values (e.g. the lid's shoulder
lift is near +2pi, the wok's near -2pi). The same poses with joint j shifted by 2pi*k are the same
geometry; a whole action may be relabelled by k if ALL its states stay within the joint ranges. The
shift is chosen per action (not for the spatula: its chain ends in the R15 stir cycle, whose states
are not stored) and reported; it changes no checked geometry.
Check of an edge: straight segments in (cart, joints) space, cut into states so that between any two
consecutive states point_bound.segment_bound (a valid bound on the displacement of every robot point)
is <= 4 mm (the bound is taken per short piece of the segment, see states_on); every
state is screened by the fast checker, then ALL states get the full checker (exact bounds,
10 mm robot-environment, 5 mm gripper-environment, self, joint ranges, cart floor / tip). An edge is
'checked' only if every state passed. Blocked edges try joint-ordered via poses, then planner.plan
(RRT-Connect with restarts, staging = the via poses, shortcutting, full <=4 mm replay; PLAN_S>=60 s).
Time: the r17chain.py caps, joints <= 60 deg/s, cart <= 0.25 m/s, + 0.6 s per edge (as its joins):
sum over consecutive checked states of max(max|dq|/60 deg/s, |dx|/0.25 m/s), + 0.6 s.

Commands (each one is short; the controller runs the full list, see 'commands'):
 python r19hub.py endpoints                          -> results/r19/hub/endpoints.json
 python r19hub.py tuck [ELBOW=pos|neg] [SEED=1] [ITER=100] [POP=12]  -> results/r19/hub/tuck_<ELBOW>.json (DE search)
 python r19hub.py hubs [TUCK=neg]                    -> results/r19/hub/hubs.json (stations, 2pi relabels)
 python r19hub.py screen [TUCK=neg]                  straight spurs, fast checker only (a screen, NOT a check)
 python r19hub.py edge A=<node> B=<node> [PLAN_S=120] [SEED=8] [NOPLAN=1] [NOVIA=1]  -> results/r19/hub/edge_<A>__<B>.json
   (SCREENONLY=1: fast checker only, to rank via poses quickly; NOT a check -> screen_edge_<A>__<B>.json)
 python r19hub.py graph                              -> results/r19/hub/graph.json (+ routes vs estimate)
 python r19hub.py meals                              -> results/r19/hub/meal_transitions.json
 python r19hub.py commands                           (prints the edge commands still to run)
 python r19hub_render.py                             -> results/r19/hub/hubs_sheet.png
Nodes: endpoints (above), hubs H_SPAT / H_SINK / H_WOK / H_POT (the tuck at a station), feet F_<E>
(the tuck at the endpoint's own cart x, fallback when a blended spur fails).
Edges: spur endpoint -> home hub (phase 1), corridor hub -> hub (arm fixed in the tuck, cart only),
express endpoint -> endpoint for the plating trip, spur endpoint -> neighbouring hub (phase 2).
Via poses tried in order when the straight edge fails: the tuck at the middle / either cart ('floating
hub', express edges), Cartesian retreats of the TCP toward the aisle (RETREATS) alone or with the
floating hub, joint-ordered vias (VIA_SETS); then, cart fixed only, planner.plan."""
import sys,os,json,time,math
sys.path.insert(0,'.')
import numpy as np,mujoco
import chain,planner   # chain.py sets planner.carry_clear = the R10 dock carry envelope (dock_carry)
from scene import build,save
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
CMD=sys.argv[1] if len(sys.argv)>1 else 'commands'
KV=dict(a.split('=',1) for a in sys.argv[2:])
import arms;ARM=arms.current()   # R19 arm option (ARM=<id>; default ur5e: everything as before)
OUT='results/r19/hub'+arms.tag(ARM)
K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)   # as r17chain.py DESIGN
K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_ROLL=180.   # R18b: spatula flat left of the sink, flipped
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r15_drum_taken=True,r16_tools={'ladle':None})
PLATE2=[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]]   # a dish waiting at the 2nd plating spot too
QW,CW,JOIN_S,STEP=math.radians(60.),.25,.6,.004
QW=min(QW,math.radians(min(arms.speeds(ARM))))   # R19: never above the arm's slowest joint (60 deg/s stays for ur5e / fr5)
SCREEN_ONLY=bool(KV.get('SCREENONLY'))   # fast checker only: NOT a check, saved as screen_edge_*.json
JAW=.025;TWO_PI=2*np.pi
ACT={'wok':['results/r17/chain_wok_s-1_final.json','results/r17/chain_wok_s-1_r18plate2b.json'],
 'lever':['results/r17/chain_lever_s+1_final.json'],'lid':['results/r17/chain_lid_s-1_final.json'],
 'spider':['results/r17/chain_spider_s+1_final.json'],'spatula':['results/r17/chain_spatula_s-1_r18roll-1.15_.30.json']}
ACT={a:[f[:-5]+arms.tag(ARM)+'.json' for f in fs] for a,fs in ACT.items()}   # R19: the chains re-run on the arm option (r17chain.py ... ARM=<id> -> *_<id>.json)
ENDS={'WOK':('wok',0),'LEV_C':('lever',0),'LEV_O':('lever',1),'LID_POT':('lid',0),'LID_RACK':('lid',1),'SPIDER':('spider',0),'SPAT':('spatula',0)}
NOSHIFT=set(KV.get('NOSHIFT','').split(','))-{''}   # actions kept at their stored labels (the spatula chain ends in the R15 stir cycle, whose states
# are not stored: it is relabelled by the same 2pi multiples, valid while its joints stay in range; flagged in R19_HUB.md)
STATIONS={'H_SPAT':-1.48,'H_SINK':-.68,'H_WOK':.172,'H_POT':1.093}   # hub cart x (see R19_HUB.md)
HOME={'SPAT':'H_SPAT','LEV_C':'H_SINK','LEV_O':'H_SINK','WOK':'H_WOK','SPIDER':'H_POT','LID_POT':'H_POT','LID_RACK':'H_POT'}
EST=lambda dx:abs(dx)/.25+1.+90/90+.6   # r17seq.py free(): the estimate under test
def J(f):return json.load(open(f,encoding='utf-8'))
# ---------------- scene ----------------
_CH=None
def union_tree():
 cfg=chain.chain_cfg('SD',**{**BASE,'r17_lever':0.,'r16_lid':'on','r17_plate2':PLATE2});tree,meta=build(cfg,None);world=tree.find('worldbody')
 R,p=K17.lever_pose(K17.LEVER_OPEN);K._add(world,'u_open_',K.OBJ['lever']['parts'],R,p,rgba='.75 .77 .8 1')   # the lever open too
 R,p=K.pose('lid','rack');K._add(world,'u_rack_',K.OBJ['lid']['parts'],R,p)   # the lid in the rack too
 return tree,meta
def union_checker():
 global _CH
 if _CH is None:
  tree,meta=union_tree();_CH=Checker(tree,meta);_CH.active=_CH.arm_ids
 return _CH
# ---------------- endpoints and 2pi relabelling ----------------
def unwrapped(f):
 """The play with its 2pi label jumps removed (r17chain joins take the nearest equivalent angle, the
 next piece keeps its own labels, so the stored play jumps by exactly 2pi in some joints at a meet:
 the same pose, but a controller fed those values would turn the joint 360 deg). The approach at the
 end gets the same net relabelling as the play's last state. Returns play, approaches, net shift."""
 r=J(f);P=np.array(r['play'],float);U=P.copy()
 for i in range(1,len(U)):U[i:,3:9]-=np.round((U[i,3:9]-U[i-1,3:9])/TWO_PI)*TWO_PI
 net=U[-1]-P[-1];apps=[]
 for k,qs in enumerate(r['approach_qs']):
  if not qs:apps.append(None);continue
  A=np.array(qs,float);gk=r['approaches'][k]['kf'];apps.append(A+(net if gk==len(r['keyframes'])-1 and gk!=0 else 0.))
 return U,apps,np.round(net[3:9]/TWO_PI).astype(int)
def action_states(a):
 S=[]
 for f in ACT[a]:
  U,apps,_=unwrapped(f);S+=list(U);S+=[q for A in apps if A is not None for q in A]
 return np.array(S)
def endpoints():
 out={}
 for e,(a,k) in ENDS.items():
  r=J(ACT[a][0]);U,apps,net=unwrapped(ACT[a][0])
  out[e]=dict(action=a,file=ACT[a][0],q=apps[k][-1].tolist(),approach_ok=r['approaches'][k]['ok'],play_label_jumps=int(np.sum(np.round(abs(np.diff(np.array(r['play'])[:,3:9],axis=0))/TWO_PI))),play_net_relabel_2pi=net.tolist())
 return out
def allowed_shifts(a,ch):
 """Per joint: the 2pi multiples k for which every state of the action stays in the joint range."""
 S=action_states(a);lo=ch.m.jnt_range[:,0];hi=ch.m.jnt_range[:,1];out={}
 for j in ch.arm_ids:
  if a in NOSHIFT or j==5:out[j]=[0];continue   # elbow: +-160 deg, no second turn
  out[j]=[k for k in (-2,-1,0,1,2) if S[:,j].min()+TWO_PI*k>=lo[j]-1e-9 and S[:,j].max()+TWO_PI*k<=hi[j]+1e-9]
 return out
def best_shift(a,T,E,AS):
 """One k per joint for the whole action a: least max distance of its endpoints to the tuck T."""
 ks={}
 for j in AS[a]:
  ks[j]=min(AS[a][j],key=lambda k:max(abs(T[j-3]-(E[e]['q'][j]+TWO_PI*k)) for e in E if E[e]['action']==a))
 return ks
def shifted(q,ks):
 q=np.array(q,float)
 for j,k in ks.items():q[j]+=TWO_PI*k
 return q
# ---------------- checking ----------------
def reserve(r):
 c=r['clearance'];env=[v['reserve_mm'] for cat,v in c.items() if cat!='self'];return (min(env) if env else None),(c['self']['clearance_mm'] if 'self' in c else None)
def states_on(ch,a,b):
 """States on the straight segment a->b such that every consecutive pair has a valid point
 displacement bound <= 4 mm: the segment is cut into K equal pieces, each piece gets its own
 point_bound.segment_bound (tighter than one bound for the whole segment, because the lever radii
 are taken at the piece's start) and is divided uniformly by it."""
 g=ch.point_bound.segment_bound(a,b);K=max(1,min(200,math.ceil(g/.05)));s=[0.];worst=0.
 for i in range(K):
  u0,u1=i/K,(i+1)/K;bi=ch.point_bound.segment_bound(a+(b-a)*u0,a+(b-a)*u1);ni=max(1,math.ceil(bi/STEP))
  s+=[u0+(u1-u0)*k/ni for k in range(1,ni+1)];worst=max(worst,bi/ni)
 return [a+(b-a)*u for u in s],g,worst
def check_segment(ch,a,b):
 a,b=np.asarray(a,float),np.asarray(b,float);qs,bound,worst=states_on(ch,a,b);n=len(qs)-1
 for i,q in enumerate(qs):   # fast screen first (fail early), then the full checker on every state
  r=ch.check(q,full=False,mass=0.)
  if not r['ok']:return dict(ok=False,stage='fast',at=round(i/n,3),hits=[h['pair'] for h in r['hits']][:3],ranges=r['ranges'],mobile=r['mobile']['ok'],stability=r['stability']['ok'],q=q.tolist())
 if SCREEN_ONLY:return dict(ok=True,n=n+1,bound_m=round(bound,4),max_step_bound_mm=round(worst*1000,2),min_reserve_mm=None,min_self_mm=None,qs=qs,screen_only=True)
 rmin=smin=1e9
 for i,q in enumerate(qs):
  r=ch.check(q,full=True,mass=0.)
  if not r['ok']:return dict(ok=False,stage='full',at=round(i/n,3),hits=[h['pair'] for h in r['hits']][:3],ranges=r['ranges'],mobile=r['mobile']['ok'],stability=r['stability']['ok'],q=q.tolist())
  e_,s_=reserve(r);rmin=min(rmin,e_ if e_ is not None else 1e9);smin=min(smin,s_ if s_ is not None else 1e9)
 return dict(ok=True,n=n+1,bound_m=round(bound,4),max_step_bound_mm=round(worst*1000,2),min_reserve_mm=round(rmin,1),min_self_mm=round(smin,1),qs=qs)
def check_path(ch,wps):
 segs=[];qs=[np.asarray(wps[0],float)]
 for a,b in zip(wps[:-1],wps[1:]):
  s=check_segment(ch,a,b)
  if not s['ok']:return dict(ok=False,segment=len(segs),fail={k:v for k,v in s.items() if k!='qs'})
  qs+=s['qs'][1:];segs.append({k:v for k,v in s.items() if k!='qs'})
 return dict(ok=True,segments=segs,qs=qs)
def metrics(ch,qs):
 """Time at the r17chain caps, peak TCP speed, highest robot point, R10 carry envelope share."""
 m,d=ch.m,ch.d;sid=m.site('R_prep').id;Q=np.array(qs);t=JOIN_S;vmax=0.;top=0.;prev=None
 arm=[g for g in range(m.ngeom) if ch.robot[g] and not m.geom(g).name.startswith(('R_cart','R_dock'))]
 for i,q in enumerate(Q):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);p=d.site_xpos[sid].copy();top=max(top,float(np.max(d.geom_xpos[arm,2]+m.geom_rbound[arm])))
  if i:
   dq=Q[i,3:9]-Q[i-1,3:9];dt=max(float(np.max(abs(dq)))/QW,abs(Q[i,0]-Q[i-1,0])/CW)
   t+=dt
   if dt>1e-9:vmax=max(vmax,float(np.linalg.norm(p-prev))/dt)
  prev=p
 return dict(time_s=round(t,2),arm_deg=round(float(np.degrees(np.max(abs(Q[-1,3:9]-Q[0,3:9])))),1),cart_m=round(float(abs(Q[-1,0]-Q[0,0])),3),peak_tcp_mps=round(vmax,2),max_height_m=round(top,3))
# ---------------- nodes ----------------
def load_tuck():
 f=f"{OUT}/hubs.json"
 if not os.path.exists(f):raise SystemExit('run "hubs" first')
 return J(f)
def node_q(name,H=None):
 H=H or load_tuck();T=np.array(H['tuck']['q'],float)
 if name in ENDS:return np.array(H['endpoints'][name]['q_shifted'],float)
 x=STATIONS[name] if name in STATIONS else H['endpoints'][name[2:]]['q_shifted'][0] if name.startswith('F_') else None
 if x is None:raise KeyError(name)
 return np.r_[x,-.21,0.,T,JAW,JAW]
# ---------------- commands ----------------
def cmd_endpoints():
 ch=union_checker();E=endpoints();out={}
 for e,v in E.items():
  q=np.array(v['q']);r=ch.check(q,full=True,mass=0.);ra,sa=reserve(r)
  out[e]=dict(**v,ok_in_union_scene=r['ok'],reserve_mm=None if ra is None else round(ra,1),self_mm=None if sa is None else round(sa,1),hits=[h['pair'] for h in r['hits']][:3],
   wrapped_deg=[round(float(np.degrees((x+np.pi)%TWO_PI-np.pi)),1) for x in q[3:9]])
 AS={a:{str(j):k for j,k in allowed_shifts(a,ch).items()} for a in ACT}
 save(f'{OUT}/endpoints.json',dict(endpoints=out,allowed_shifts=AS,scene='union: R18 kitchen, lever closed+open, lid pot+rack, dishes at x .43 and .17'))
 for e,v in out.items():print(e,'cart',round(v['q'][0],3),'ok',v['ok_in_union_scene'],v['reserve_mm'],'mm',v['hits'],v['wrapped_deg'])
 print('allowed 2pi shifts',AS)
def tuck_search():
 """Differential evolution for ONE tucked joint posture T (cart-independent):
 sum over the 7 endpoints of the largest joint move to T (the straight-spur time)
 + collision penalty at T over 7 cart stations and on 6 coarse samples of every straight spur
 + R10 dock carry envelope at T (+-0.40 m along x, <= 0.10 m over the counter edge)
 + a mild height penalty above 1.95 m (the ceiling is not modelled)."""
 from scipy.optimize import differential_evolution
 ch=union_checker();m,d=ch.m,ch.d;E=endpoints();AS=allowed_shifts_all(ch);fam=KV.get('ELBOW','pos')
 G=m.ngeom;req=np.full((G,G),np.nan)
 for a in range(G):
  for b in range(a+1,G):
   if not(ch.robot[a] or ch.robot[b]):continue
   r_=ch.required(ch,a,b)
   if r_ is not None:req[a,b]=req[b,a]=r_[0]
 arm=[g for g in range(G) if ch.robot[g] and (m.geom(g).name.startswith('R_geom_') or ch.gripper(g))]
 old=m.geom_margin.copy();BUF=.012
 def pen(q):
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_collision(m,d)
  if d.ncon==0:return 0.
  gg=d.contact.geom[:d.ncon];dist=d.contact.dist[:d.ncon];rq=req[gg[:,0],gg[:,1]];ok=~np.isnan(rq)
  buf=np.where(rq[ok]>0,BUF,.001);return float(np.sum(np.maximum(0,rq[ok]+buf-dist[ok])))*1000
 xs=[-1.48,-1.0,-.68,-.25,.172,.6,1.093,1.46]
 ends=list(E)
 def f(x):
  m.geom_margin[:]=old+.03
  try:
   T=np.array(x);cost=0.;pc=0.;ps=0.
   for e in ends:
    a=E[e]['action'];qe=np.array(E[e]['q'],float)
    for j in ch.arm_ids:qe[j]+=TWO_PI*min(AS[a][j],key=lambda k:abs(T[j-3]-qe[j]-TWO_PI*k))
    cost+=float(np.max(abs(T-qe[3:9])))
    qt=qe.copy();qt[3:9]=T;qt[-2:]=JAW
    for s in (1/7,2/7,3/7,4/7,5/7,6/7):ps+=pen(qe+(qt-qe)*s)
   q=np.r_[0.,-.21,0.,T,JAW,JAW];env=0.;top=0.
   for xx in xs:q[0]=xx;pc+=pen(q)
   q[0]=0.;d.qpos[:]=q;mujoco.mj_kinematics(m,d)
   P=d.geom_xpos[arm];r=m.geom_rbound[arm]
   env=float(np.sum(np.maximum(0,abs(P[:,0])+r-.40))+np.sum(np.maximum(0,P[:,1]+r-.10)))*1000
   top=float(np.max(P[:,2]+r))
   return cost+1.0*pc+.15*ps+.05*env+.01*max(0,top-1.95)*1000
  finally:m.geom_margin[:]=old
 lo=ch.m.jnt_range[ch.arm_ids,0].copy()+.19;hi=ch.m.jnt_range[ch.arm_ids,1].copy()-.19   # >= 0.19 rad (11 deg) from every joint limit
 if fam=='pos':lo[2]=.3
 elif fam=='neg':hi[2]=-.3
 t0=time.monotonic()
 res=differential_evolution(f,list(zip(lo,hi)),seed=int(KV.get('SEED',1)),popsize=int(KV.get('POP',12)),maxiter=int(KV.get('ITER',120)),tol=1e-7,polish=False,init='sobol')
 T=res.x;print('DE',round(time.monotonic()-t0),'s cost',round(res.fun,3),np.round(T,3),flush=True)
 # report: per endpoint largest joint move, full check of T at the stations, carry envelope
 rep={}
 for e in ends:
  a=E[e]['action'];qe=np.array(E[e]['q'],float)
  for j in ch.arm_ids:qe[j]+=TWO_PI*min(AS[a][j],key=lambda k:abs(T[j-3]-qe[j]-TWO_PI*k))
  rep[e]=round(float(np.degrees(np.max(abs(T-qe[3:9])))),1)
 st={}
 for xx in xs:
  q=np.r_[xx,-.21,0.,T,JAW,JAW];r=ch.check(q,full=True,mass=0.);ra,sa=reserve(r)
  st[str(xx)]=dict(ok=r['ok'],reserve_mm=None if ra is None else round(ra,1),self_mm=None if sa is None else round(sa,1),hits=[h['pair'] for h in r['hits']][:3],carry=bool(chain.dock_carry(ch,q)))
 q=np.r_[0.,-.21,0.,T,JAW,JAW];mt=metrics(ch,[q])
 out=dict(elbow=fam,seed=int(KV.get('SEED',1)),q=T.tolist(),cost=round(float(res.fun),3),elapsed_s=round(time.monotonic()-t0),spur_max_joint_deg=rep,spur_sum_deg=round(sum(rep.values()),1),stations=st,max_height_m=mt['max_height_m'])
 save(f"{OUT}/tuck_{fam}{('_s'+KV['SEED']) if 'SEED' in KV else ''}.json",out);print(json.dumps({k:v for k,v in out.items()},default=str))
def allowed_shifts_all(ch):return {a:allowed_shifts(a,ch) for a in ACT}
def cmd_hubs():
 ch=union_checker();E=endpoints();AS=allowed_shifts_all(ch)
 f=KV.get('TUCKFILE') or f"{OUT}/tuck_{KV.get('TUCK','pos')}.json";tk=J(f);T=np.array(tk['q'])
 ks={a:best_shift(a,T,E,AS) for a in ACT};eps={}
 for e,v in E.items():
  q=shifted(v['q'],ks[v['action']]);eps[e]=dict(action=v['action'],q_raw=v['q'],q_shifted=q.tolist(),shift_2pi={str(j):k for j,k in ks[v['action']].items() if k},home=HOME[e],
   spur_max_joint_deg=round(float(np.degrees(np.max(abs(T-q[3:9])))),1))
 st={}
 for h,x in STATIONS.items():
  q=np.r_[x,-.21,0.,T,JAW,JAW];r=ch.check(q,full=True,mass=0.);ra,sa=reserve(r);st[h]=dict(x=x,q=q.tolist(),ok=r['ok'],reserve_mm=None if ra is None else round(ra,1),carry_envelope=bool(chain.dock_carry(ch,q)))
 save(f'{OUT}/hubs.json',dict(tuck=dict(file=f,q=T.tolist()),stations=st,endpoints=eps,action_shifts={a:{str(j):k for j,k in v.items() if k} for a,v in ks.items()}))
 for h,v in st.items():print(h,v['x'],v['ok'],v['reserve_mm'],'carry',v['carry_envelope'])
 for e,v in eps.items():print(e,'->',v['home'],'max joint',v['spur_max_joint_deg'],'shift',v['shift_2pi'])
def cmd_screen():
 """Fast screen (fast checker only, every <= 4 mm) of the straight spur endpoint -> foot (tuck at the
 endpoint's cart) for a tuck file: where does each straight spur first hit? Not a check."""
 ch=union_checker();E=endpoints();AS=allowed_shifts_all(ch);tk=J(KV.get('TUCKFILE') or f"{OUT}/tuck_{KV.get('TUCK','pos')}.json");T=np.array(tk['q'])
 ks={a:best_shift(a,T,E,AS) for a in ACT};out={}
 for e,v in E.items():
  qa=shifted(v['q'],ks[v['action']]);qb=qa.copy();qb[3:9]=T;qb[-2:]=JAW;qs,_,_=states_on(ch,qa,qb);n=len(qs)-1;hit=None
  for i,q in enumerate(qs):
   r=ch.check(q,full=False,mass=0.)
   if not r['ok']:hit=dict(at=round(i/n,3),pairs=[h['pair'] for h in r['hits']][:2]);break
  out[e]=dict(max_joint_deg=round(float(np.degrees(np.max(abs(T-qa[3:9])))),1),states=n+1,first_hit=hit);print(e,out[e],flush=True)
 save(f"{OUT}/screen_{os.path.basename(tk.get('file','')) or KV.get('TUCK','pos')}.json",dict(tuck=T.tolist(),spurs=out))
VIA_SETS=[[4,5],[3],[6,7,8],[4,5,6,7,8],[3,6,7,8],[3,4,5],[5,6,7,8],[4]]
RETREATS=[(0,-.15,0),(0,-.30,0),(0,-.20,-.06)]   # TCP moves (m) toward the aisle (-y), same orientation
def retreats(ch,q):
 """Cartesian retreat via poses of an endpoint: the TCP pulled toward the aisle with the same
 orientation, cart fixed, solved by least squares from the endpoint (same IK branch)."""
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 m,d=ch.m,ch.d;sid=m.site('R_prep').id;ids=ch.arm_ids;lo=m.jnt_range[ids,0]+1e-6;hi=m.jnt_range[ids,1]-1e-6
 d.qpos[:]=q;mujoco.mj_kinematics(m,d);p0=d.site_xpos[sid].copy();R0=d.site_xmat[sid].reshape(3,3).copy();out=[]
 for dv in RETREATS:
  pt=p0+np.array(dv);qq=np.array(q,float)
  def res(x):
   qq[ids]=x;d.qpos[:]=qq;mujoco.mj_kinematics(m,d)
   return np.r_[(d.site_xpos[sid]-pt)*10,Rotation.from_matrix(R0@d.site_xmat[sid].reshape(3,3).T).as_rotvec()]
  sol=least_squares(res,np.clip(np.array(q)[ids],lo,hi),bounds=(lo,hi),max_nfev=300,xtol=1e-10,ftol=1e-10);qq[ids]=sol.x
  pe,re=ch.pose_error(qq,pt,R0)
  if pe<.001 and re<np.radians(.5) and np.max(abs(sol.x-np.array(q)[ids]))<np.radians(90) and ch.check(qq,full=False,mass=0.)['ok']:out.append((f'retreat {dv}',qq.copy()))
 return out
def cmd_edge():
 ch=union_checker();A,B=KV['A'],KV['B'];H=load_tuck();qa,qb=node_q(A,H),node_q(B,H);t0=time.monotonic();tries=[]
 def done(path,method,extra=None):
  mt=metrics(ch,path['qs']);return dict(ok=True,method=method,**mt,segments=path.get('segments'),qs=[list(map(float,q)) for q in path['qs']],**(extra or {}))
 res=None
 p=check_path(ch,[qa,qb]);tries.append(dict(method='straight',ok=p['ok'],fail=p.get('fail')));print('straight',p['ok'],p.get('fail',{}).get('hits'),flush=True)
 if p['ok']:res=done(p,'straight')
 vias=[]   # (label, intermediate waypoints)
 if res is None and not KV.get('NOVIA'):
  T=np.array(H['tuck']['q']);RA=retreats(ch,qa) if A in ENDS else [];RB=retreats(ch,qb) if B in ENDS else []
  mids=[(f'tuck at the {lab} cart',np.r_[x,-.21,0.,T,JAW,JAW]) for lab,x in (('mid',(qa[0]+qb[0])/2),('A',qa[0]),('B',qb[0]))] if A in ENDS and B in ENDS else []
  for lab,m_ in mids:vias.append((lab,[m_]))   # express edge: the tuck as a 'floating hub' (cart moving while the arm folds / unfolds)
  for la,ra in [('',None)]+RA:   # Cartesian retreat out from under the cabinets first (and back in at the far end)
   for lb,rb in [('',None)]+RB:
    if ra is None and rb is None:continue
    for lm,m_ in (mids[:1] or [('',None)]):
     wp=[x for x in (ra,m_,rb) if x is not None];vias.append((' + '.join(t for t in (la,lm,lb) if t),wp))
  for S in VIA_SETS:   # joint-ordered: some joints (and the cart) first, the rest after
   for cart_first in (False,True):
    v=qa.copy();v[S]=qb[S]
    if cart_first:v[0]=qb[0]
    vias.append((f'joints {S} first'+(', cart in the first part' if cart_first else ', cart in the second part'),[v]))
  for lab,wp in vias:
   p=check_path(ch,[qa,*wp,qb]);tries.append(dict(method='via: '+lab,ok=p['ok'],fail=p.get('fail')));print('via',lab,p['ok'],p.get('fail',{}).get('fail',{}).get('hits'),flush=True)
   if p['ok']:res=done(p,'via: '+lab);break
 if res is None and not KV.get('NOPLAN') and abs(qa[0]-qb[0])<1e-9:   # arm-only RRT-Connect (cart fixed)
  stages=[w for _,wp in vias if len(wp)==1 for w in wp]
  r=planner.plan(ch,qa,qb,budget_s=max(60.,float(KV.get('PLAN_S',120))),stages=stages,seed=int(KV.get('SEED',8)))
  tries.append(dict(method='planner.plan',ok=r['ok'],reason=r.get('reason'),elapsed_s=round(r.get('elapsed_s',0),1),restarts=r.get('restarts'),nodes=r.get('nodes')));print('planner',r['ok'],r.get('reason'),flush=True)
  if r['ok']:   # planner.edge already replayed every state at <=4 mm with the full checker
   rs=[reserve(dict(clearance=c)) for c in r['clearance'] if c]
   res=done(dict(qs=r['path']),'planner.plan (RRT-Connect, staging, shortcuts, full <=4 mm replay)',dict(min_reserve_mm=round(min(x for x,_ in rs if x is not None),1) if rs else None,planner_budget_s=r['budget_s'],planner_elapsed_s=round(r['elapsed_s'],1),max_step_bound_mm=round(r['step_bound_m']*1000,2),states_checked=len(r['path'])))
 out=dict(a=A,b=B,held='nothing: empty gripper, jaws open 25 mm each',scene='union (lever closed+open, lid pot+rack, both plating spots)',
  estimate_s=round(EST(qa[0]-qb[0]),2),elapsed_s=round(time.monotonic()-t0),tries=tries,**(res or dict(ok=False)))
 if res and 'min_reserve_mm' not in out and not SCREEN_ONLY:
  segs=res.get('segments') or [];out['min_reserve_mm']=min(s['min_reserve_mm'] for s in segs) if segs else None;out['min_self_mm']=min(s['min_self_mm'] for s in segs) if segs else None
  out['states_checked']=sum(s['n'] for s in segs) if segs else None
 if SCREEN_ONLY:out.update(ok_screen=out.pop('ok'),note='fast checker only (MuJoCo contacts), NOT a check');save(f'{OUT}/screen_edge_{A}__{B}.json',out)
 else:save(f'{OUT}/edge_{A}__{B}.json',out)
 print(json.dumps({k:v for k,v in out.items() if k not in ('qs','tries','segments')},default=str))
# ---------------- graph ----------------
EXPRESS=[('SPAT','LEV_C'),('LEV_O','WOK')]   # the checked<->checked free moves of every plating / dump / fill trip
CORRIDOR=[('H_SPAT','H_SINK'),('H_SINK','H_WOK'),('H_WOK','H_POT')]
NEIGHBOR=[('SPAT','H_SINK'),('LEV_C','H_SPAT'),('LEV_C','H_WOK'),('LEV_O','H_SPAT'),('LEV_O','H_WOK'),('WOK','H_SINK'),('WOK','H_POT'),
 ('SPIDER','H_WOK'),('LID_POT','H_WOK'),('LID_RACK','H_WOK')]   # phase 2: the cart drives to the next hub while the arm folds
def edge_list(phase=1):
 """The edges the roadmap needs. Phase 1: per endpoint its spur to the home hub (fallback: its foot +
 corridor), the hub-to-hub corridor pieces, the two express edges of the plating trip. Phase 2: spurs
 to the neighbouring hubs (faster routes; the roadmap is complete without them)."""
 L=[(e,HOME[e]) for e in ENDS]+CORRIDOR+EXPRESS
 return L+(NEIGHBOR if phase>=2 else [])
FALLBACK={'LID_POT':'H_POT','LID_RACK':'H_POT'}   # if the blended spur fails: arm-only spur to the foot (RRT allowed) + corridor
def cmd_commands():
 """Edge commands still to run (an edge counts as done when its edge_*.json says ok)."""
 py='C:/Users/admin/Documents/YJGames/robot_v5/board/work/t01/.venv/Scripts/python.exe'
 for ph in (1,2):
  print(f'# phase {ph}')
  for a,b in edge_list(ph):
   if ph==2 and (a,b) in edge_list(1):continue
   f=f'{OUT}/edge_{a}__{b}.json';ok=os.path.exists(f) and J(f).get('ok')
   print(('# done: ' if ok else '')+f'{py} r19hub.py edge A={a} B={b} PLAN_S=120'+('' if ARM=='ur5e' else f' ARM={ARM}'))
  if ph==1:
   for e,h in FALLBACK.items():print(f'# only if edge_{e}__{h}.json is not ok: {py} r19hub.py edge A={e} B=F_{e} PLAN_S=120 ; {py} r19hub.py edge A=F_{e} B={h}')
 print(f'{py} r19hub.py graph')
def cmd_graph():
 H=load_tuck();nodes={e:dict(kind='endpoint',action=v['action'],cart=v['q_shifted'][0],home=v['home']) for e,v in H['endpoints'].items()}
 nodes.update({h:dict(kind='hub',cart=v['x'],q=v['q'],carry_envelope=v['carry_envelope']) for h,v in H['stations'].items()})
 edges=[];missing=[]
 import glob
 for f in sorted(glob.glob(f'{OUT}/edge_*.json')):
  r=J(f);a,b=r['a'],r['b']
  for n in (a,b):
   if n.startswith('F_') and n not in nodes:nodes[n]=dict(kind='foot',cart=node_q(n,H)[0])
  base=dict(held=r['held'],ok=r['ok'],method=r.get('method'),time_s=r.get('time_s'),estimate_s=r.get('estimate_s'),min_reserve_mm=r.get('min_reserve_mm'),
   peak_tcp_mps=r.get('peak_tcp_mps'),max_height_m=r.get('max_height_m'),states_checked=r.get('states_checked'),file=f,
   fail=None if r['ok'] else [t for t in r['tries'] if not t['ok']][:3])
  edges.append(dict(frm=a,to=b,**base));edges.append(dict(frm=b,to=a,reverse_of=f'{a}->{b}',**base))
 for a,b in edge_list(2):
  if not os.path.exists(f'{OUT}/edge_{a}__{b}.json'):missing.append(f'{a}->{b}'+(' (phase 2)' if (a,b) in NEIGHBOR else ''))
 # derived corridor edges: the hub-to-hub pieces are collinear (arm fixed in the tuck, cart only), so
 # driving through an intermediate hub needs no stop; such an edge is covered state by state by the
 # checked pieces it spans (no new check), time |dx|/0.25 + 0.6 s
 hx=sorted(STATIONS,key=STATIONS.get)
 for i in range(len(hx)):
  for j in range(i+2,len(hx)):
   pcs=[(hx[k],hx[k+1]) for k in range(i,j)];fs=[f'{OUT}/edge_{a}__{b}.json' for a,b in pcs]
   if all(os.path.exists(f) and J(f)['ok'] for f in fs):
    dx=abs(STATIONS[hx[j]]-STATIONS[hx[i]]);rs=[J(f) for f in fs]
    base=dict(held='nothing: empty gripper, jaws open 25 mm each',ok=True,method='derived: collinear checked corridor pieces '+', '.join(f'{a}-{b}' for a,b in pcs),time_s=round(dx/CW+JOIN_S,2),estimate_s=round(EST(dx),2),
     min_reserve_mm=min(r['min_reserve_mm'] for r in rs),peak_tcp_mps=CW,max_height_m=max(r['max_height_m'] for r in rs),states_checked=sum(r['states_checked'] for r in rs),file=fs,fail=None)
    edges.append(dict(frm=hx[i],to=hx[j],**base));edges.append(dict(frm=hx[j],to=hx[i],reverse_of=f'{hx[i]}->{hx[j]}',**base))
 # routes between the checked endpoints over checked edges (Dijkstra on time)
 import heapq
 adj={};adjp={}
 for e in edges:
  if e['ok']:adj.setdefault(e['frm'],[]).append((e['to'],e['time_s']));adjp.setdefault(e['frm'],[]).append((e['to'],e['time_s']))
 for f in sorted(glob.glob(f'{OUT}/screen_edge_*.json')):   # projection only: screened edges not yet checked
  r=J(f)
  if r.get('ok_screen') and not os.path.exists(f"{OUT}/edge_{r['a']}__{r['b']}.json"):
   adjp.setdefault(r['a'],[]).append((r['b'],r['time_s']));adjp.setdefault(r['b'],[]).append((r['a'],r['time_s']))
 def route(s,t,adj=adj):
  dist={s:0.};prev={};pq=[(0.,s)]
  while pq:
   dd,u=heapq.heappop(pq)
   if u==t:break
   if dd>dist.get(u,1e9):continue
   for v,w in adj.get(u,[]):
    if dd+w<dist.get(v,1e9):dist[v]=dd+w;prev[v]=u;heapq.heappush(pq,(dd+w,v))
  if t not in dist:return None
  p=[t]
  while p[-1]!=s:p.append(prev[p[-1]])
  return dict(time_s=round(dist[t],2),path=p[::-1])
 routes={}
 for s in ENDS:
  for t in ENDS:
   if s==t:continue
   r=route(s,t);rp=route(s,t,adjp);dx=nodes[s]['cart']-nodes[t]['cart']
   routes[f'{s}->{t}']=dict(estimate_s=round(EST(dx),2),checked=r,ratio=round(r['time_s']/EST(dx),2) if r else None,
    projected_with_screened=rp,projected_ratio=round(rp['time_s']/EST(dx),2) if rp else None)
 screened={}
 for f in sorted(glob.glob(f'{OUT}/screen_edge_*.json')):
  r=J(f);screened[f"{r['a']}->{r['b']}"]=dict(ok_screen=r.get('ok_screen'),method=r.get('method'),time_s=r.get('time_s'),estimate_s=r.get('estimate_s'),max_height_m=r.get('max_height_m'),note='fast checker only, NOT a check')
 save(f'{OUT}/graph.json',dict(tuck=H['tuck'],nodes=nodes,edges=edges,missing_edges=missing,routes=routes,screened_not_checked=screened,
  time_model='joints <= 60 deg/s, cart <= 0.25 m/s (r17chain.py caps) + 0.6 s per edge; estimate = |dx|/0.25 + 2.6 s (r17seq.py)'))
 print('edges',len(edges)//2,'ok',sum(e['ok'] for e in edges)//2,'missing',missing)
 for k,v in routes.items():print(k,'est',v['estimate_s'],'checked',v['checked']['time_s'] if v['checked'] else None,'projected',v['projected_with_screened']['time_s'] if v['projected_with_screened'] else None,(v['checked'] or v['projected_with_screened'] or {}).get('path',''))
# ---------------- meals: which free moves occur ----------------
SD=['SPAT_FETCH','STIR','SPAT_STOW','LEV_OPEN','WOK','LEV_CLOSE']   # a stir-fry dish: fetch, stir, stow, faucet, wok plate + sink rinse, faucet
TRIP=['LEV_OPEN','WOK','LEV_CLOSE']   # dump / fill: the same trip without the plate tip (and without the spatula)
P=lambda n:['U:pour']*n
STEPS={   # step label (meal16.py ARM=r18) -> arm actions in order; U: = not a checked action
 'taro plate into the pot steamer, lid, 30 min':['U:carrier_in','LID_ON'],
 'rice: dose, wash, cooker':['U:rice'],
 '4 cups into the electric stew pot (water bath), lid, 30 min':['U:cup']*4+['U:stew_lid'],
 'fry potato 3 min (fryer), lift out':P(1)+['SPIDER*'],
 'rinse wok; oil, broccoli, sauce; lid 30 s; stir; plate':P(2)+['U:wok_lid','U:wok_lid']+SD,
 'wok: pork, 豆瓣, chili, potato, sauce; stir 90 s; plate':P(3)+SD,
 'steamer: taro out (lid), luffa in, lid, 3 min':['LID_OFF','U:carrier_out','U:carrier_in','LID_ON'],
 'rinse wok; heat 40 g oil 60 s; pour over garlic bowl':P(1)+['U:sauce_oil'],
 'drizzle osmanthus syrup':P(1),
 'luffa out (lid), pour sauce over':['LID_OFF','U:carrier_out']+P(1),
 '(the cups stay in the stew pot; the user serves them)':[],
 'wok to the tap: 1 L cold water; pork belly in; blanch 5 min; lift out':TRIP+P(1)+['SPIDER*'],
 'scalded ribs, shoots, scallops, hot water into the pot; lid; 60 min':P(4)+['U:stew_lid'],
 '(cut cubes: prep machine / user)':[],
 'wok emptied at the sink; fry cubes, aromatics, 糖色, sauce, water (cup); lid; braise 40 min':TRIP+P(5)+['SPAT_FETCH','STIR','SPAT_STOW','U:wok_lid'],
 'fish plate into steamer, lid, 6 min':['U:carrier_in','LID_ON'],
 'fish out, pour off water, soy, shreds':['LID_OFF','U:carrier_out']+P(3),
 'lid off, reduce 3 min stirring, plate':['U:wok_lid']+SD,
 'rinse wok; heat oil 60 s; over fish + over garlic bowl; mix sauce':P(1)+['U:sauce_oil']*2+P(3),
 'oil, eggs set, out; tomato, lid 30 s, eggs back; plate':P(5)+['U:wok_lid']*2+SD,
 'wok to the tap: 1 L water; oil, salt; to boil 3 min':TRIP+P(2),
 'salt, celery (the user serves it from the pot)':P(1),
 'blanch and lift out, arrange, sauce':P(2)+['SPIDER*','SPIDER*','U:arrange']+P(1),
 'taro+rib plate into steamer, lid, 30 min':['U:carrier_in','LID_ON'],
 'stew pot (water in at setup, heating): ginger, cucumber':P(2),
 'aromatics, pepper, wine, squid, sauce; stir 60 s; plate':P(5)+SD,
 'oil, garlic, peas, salt, water; stir 45 s; plate':P(3)+SD,
 'wok to the tap: 1 L water; to boil 3 min; shreds in, back to boil':TRIP+P(1),
 'pork slices 3 min; salt (the user serves it from the pot)':P(2),
 'blanch 30 s, lift out; wok emptied at the sink; stir-fry 45 s with 调味水; plate':['SPIDER*']+TRIP+P(3)+SD,
 'out (lid), chili, scallion, hot oil from the wok':['LID_OFF','U:carrier_out']+P(2)+['U:sauce_oil']}
NODE_IN={'SPAT_FETCH':'SPAT','LEV_OPEN':'LEV_C','LEV_CLOSE':'LEV_O','WOK':'WOK','LID_OFF':'LID_POT','LID_ON':'LID_RACK','SPIDER*':'SPIDER'}
NODE_OUT={'SPAT_STOW':'SPAT','LEV_OPEN':'LEV_O','LEV_CLOSE':'LEV_C','WOK':'WOK','LID_OFF':'LID_RACK','LID_ON':'LID_POT','SPIDER*':'SPIDER'}
HANDOFF={('SPAT_FETCH','STIR'),('STIR','SPAT_STOW')}   # checked R18 hand-off with the spatula in hand, no free move
def cmd_meals():
 M=J('results/r16/meal_stew_r18.json')['meals'];out={};tot={}
 for meal,r in M.items():
  seq=[]
  for e in sorted(r['log'],key=lambda e:(e['start_s'],e['i'])):seq+=[(t,e['label']) for t in STEPS[e['label']]]
  tr=[];c=dict(checked_checked=0,checked_unchecked=0,unchecked_unchecked=0,handoff=0)
  for (a,la),(b,lb) in zip(seq[:-1],seq[1:]):
   if (a,b) in HANDOFF:kind='handoff';held='spatula (checked hand-off, not a free move)'
   else:
    fa,fb=NODE_OUT.get(a),NODE_IN.get(b);held='nothing'
    kind='checked_checked' if fa and fb else 'unchecked_unchecked' if not fa and not fb else 'checked_unchecked'
   c[kind]+=1;tr.append(dict(frm=a,to=b,frm_node=NODE_OUT.get(a),to_node=NODE_IN.get(b),kind=kind,held=held,step=lb))
  pairs={}
  for t in tr:
   if t['kind']=='checked_checked':k=f"{t['frm_node']}->{t['to_node']}";pairs[k]=pairs.get(k,0)+1
  out[meal]=dict(actions=[a for a,_ in seq],counts=c,checked_checked_pairs=pairs,transitions=tr)
  for k,v in c.items():tot[k]=tot.get(k,0)+v
  print(meal[:2],c,pairs)
 spur_uses={}
 for meal,v in out.items():
  for t in v['transitions']:
   for n in (t['frm_node'],t['to_node']):
    if n and t['kind']!='handoff':spur_uses[n]=spur_uses.get(n,0)+1
 save(f'{OUT}/meal_transitions.json',dict(source='results/r16/meal_stew_r18.json (meal16.py SET=stew ARM=r18), steps in schedule order',totals=tot,endpoint_uses=spur_uses,meals=out))
 print('totals',tot,'endpoint uses',spur_uses)
if __name__=='__main__':
 os.makedirs(OUT,exist_ok=True)
 {'endpoints':cmd_endpoints,'screen':cmd_screen,'tuck':tuck_search,'hubs':cmd_hubs,'edge':cmd_edge,'graph':cmd_graph,'meals':cmd_meals,'commands':cmd_commands}[CMD]()
