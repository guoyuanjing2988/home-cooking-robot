"""R19 tolerance (GitHub #13): how much pose error does each stored path tolerate before a hit?

Read-only use of the unchanged checker. For a stored path (the R17/R18b action plays at <= 4 mm, their grasp
approaches, the R19 hub edges) every state is re-evaluated with a PERTURBATION:
  cart   the whole robot (cart + arm + gripper + held part) moved rigidly against the kitchen:
         x, y, z (m), yaw about the arm's J1 axis, tilt_x / tilt_y about the floor line under the cart
         origin (floor tilt, tyre / caster compliance) -- the registration / docking error of a set;
  fix    one fixture group (cooker + wok on it, faucet body, lever clip, plates, spatula pad, lid rack,
         pot, spider rest, sink, prep tray, upper cabinets / hood, counter / cabinet fronts ...) moved
         by (x, y, z) -- fixture placement / kitchen survey error;
  grasp  the held part moved in the TOOL frame (x, y, z) or turned about the jaw axis -- grasp offset /
         slip of the object in the jaws.
Distance = the checker's own certificate (distance.Bounds): enclosing-AABB lower bound, refined by the
GJK dual lower bound of every pair that can be the minimum (branch and bound, so the minimum is exactly
the one Checker.check(full=True) reports for these pairs). Only pairs whose distance the perturbation can
change are evaluated (robot vs environment for 'cart', the group's pairs for 'fix', the held part's pairs
-- environment and own arm -- for 'grasp'); every other pair is unchanged and passed at nominal.
Two thresholds per state: 'gate' = distance - the checker's gap (10 mm robot / 5 mm gripper+held / 0 self,
the planning gate) and 'contact' = distance (real contact in the model).
The MuJoCo-contact part of the checker (box-box artefacts, DECISIONS R11) is not used; r19tol_replay.py
re-runs Checker.check(full=True) at the binding states as a cross-check.
Arm option: ARM=<id> as everywhere (arms.current()), layout PY=<y> (plating spot); outputs go to results/r19/tol/<arm>[_py<y>]
(UR5e default: results/r19/tol); stored
paths are taken from the tagged files if they exist (r17chain.py / r19hub.py ... ARM=<id>), else the
UR5e files (same kinematics for an enclosing-geometry model such as ARM=ur5e_enc)."""
import sys,os,json,math
sys.path.insert(0,'.')
import numpy as np,mujoco
import arms
ARM=arms.current();TAG=arms.tag(ARM)
PYARG=next((a[3:] for a in sys.argv[1:] if a.startswith('PY=')),None)   # PY=<y>: the plating spot (and the waiting dish) at this y,
   # as r17chain.py / r19hub.py PY= (R19 #12 standard: ARM=ur5e_enc2_pgc PY=.15); default unchanged
_SUB=(ARM if TAG else '')+(('_' if TAG else '')+'py'+PYARG if PYARG else '')
OUT='results/r19/tol'+('/'+_SUB if _SUB else '')   # another arm option / layout: results/r19/tol/<arm>[_py<y>]
MM,DEG=1e-3,math.pi/180
CHAINS=dict(   # action -> stored chain (as r19smooth.CHAINS) and the world of each grasp approach (r17chain.action() GR)
 wok=dict(file='results/r17/chain_wok_s-1_final.json',label='wok_plate_rinse',worlds={0:{},16:{}}),
 spatula=dict(file='results/r17/chain_spatula_s-1_r18roll-1.15_.30.json',label='spatula_fetch',worlds={0:{}}),
 lever=dict(file='results/r17/chain_lever_s+1_final.json',label='faucet_open',worlds={0:{'r17_lever':0.},1:{'r17_lever':30.}}),
 lid=dict(file='results/r17/chain_lid_s-1_final.json',label='lid_off_to_rack',worlds={0:{'r16_lid':'on'},8:{'r16_lid':'rack'}}),
 spider=dict(file='results/r17/chain_spider_s+1_final.json',label='spider_pot_to_plate',worlds={0:{},18:{}}))
HUBDIR='results/r19/hub'
def hubdir():
 """r19hub.py's folder for this arm and layout (results/r19/hub[_py<y>][_<arm>]) if it exists, else the UR5e hub."""
 d=HUBDIR+('_py'+PYARG if PYARG else '')+TAG
 return d if d!=HUBDIR and PATHS!='base' and os.path.isdir(d) else HUBDIR
PATHS=next((a[6:] for a in sys.argv[1:] if a.startswith('PATHS=')),'auto')   # PATHS=base: always the stored UR5e paths
def tagged(f):
 """The arm option's own stored path if it exists and holds states: r17chain.py / r19enc_adopt.py ... ARM=<id>
 -> *_<id>.json; with PY=<y> the wok chains of that layout, *_py<y>_<id>.json (as r19hub.py). Else the stored
 UR5e path (PATHS=base forces it)."""
 t=f[:-5]+(('_py'+PYARG) if PYARG and 'chain_wok' in f else '')+TAG+'.json'
 if t!=f and PATHS!='base' and os.path.exists(t):
  r=J(t)
  if r.get('play') or r.get('qs'):return t
 return f
def J(f):return json.load(open(f,encoding='utf-8'))
def unwrap(Q):
 Q=np.array(Q,float)
 for i in range(len(Q)-1):
  d=Q[i+1,3:9]-Q[i,3:9];Q[i+1:,3:9]-=np.round(d/(2*np.pi))*2*np.pi
 return Q
# ---------------------------------------------------------------- fixture groups (environment geoms)
GROUPS=dict(
 cooker=lambda n,p:n.startswith(('r15_cooker','r15_knob','r15_camera','r15_wok_')),   # cooker + the wok seated in its slot
 drum=lambda n,p:n.startswith('r15_drum'),
 faucet_body=lambda n,p:n.startswith(('r17_faucet','r17_lever_hub','r17_lever_bar','u_open_r17_lever_bar')),
 lever_clip=lambda n,p:n.startswith(('r17_lever_bracket','r17_lever_tip','u_open_r17_lever_bracket','u_open_r17_lever_tip')),
 plate1=lambda n,p:n=='r15_plate',
 plate2=lambda n,p:n=='r17_plate2',
 spatula_pad=lambda n,p:n.startswith(('r16_rest_spatula','r16_spatula_')),
 lid_rack=lambda n,p:n.startswith(('r16_rack_','u_rack_')) or (n.startswith('r16_lid_') and p[0]>1.55),
 pot=lambda n,p:n.startswith(('r16_pot','r16_ind2')) or (n.startswith('r16_lid_') and p[0]<=1.55),
 spider_rest=lambda n,p:n.startswith(('r16_rest_spider','r16_spider_','r16_rest_ladle')),
 sink=lambda n,p:n.startswith('sink_') and not n.startswith('sink_cabinet'),
 raw=lambda n,p:n.startswith('raw_'),
 bowls=lambda n,p:n.startswith('stored_bowl'),
 cups=lambda n,p:n.startswith(('r14_cup','r14_season','r14_staple')),
 upper=lambda n,p:n.startswith(('upper_cabinet','r07_closed_door','r14_hood','r14_upper','door_pause')),
 counter=lambda n,p:n.startswith(('counter','north_cabinet','sink_cabinet','south')),
 wall=lambda n,p:n.startswith(('north_wall','outlet','appliance_power','faucet_v3','r15_camera')))
# ---------------------------------------------------------------- scenes
def _kitchen(r):
 import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
 py=PYARG if PYARG else r.get('plate_y')   # the plating spot y: PY= for every scene, else the chain's own plate_y (py chains)
 if py is not None:K15.PLATE['c'][1]=float(py)
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
 K17.set_wok_tilt(float(r.get('wok_tilt') or 0.))
 for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
 K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.   # R18b: the spatula lies left of the sink
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
def _meshheld(tree):
 """R11 rule (DECISIONS 2026-10-10) for the held parts kitchen14+ attach after scene.build's mesh_tool pass
 (as r19smooth.setup; only the MuJoCo-contact part of the checker depends on it, not the GJK bound)."""
 import xml.etree.ElementTree as E
 from scene import fmt
 asset=tree.getroot().find('asset');tool=tree.find(".//body[@name='R_tool']")
 for g in tool.iter('geom'):
  if g.get('type')!='box':continue
  h=np.fromstring(g.get('size'),sep=' ');mn='mb19_'+g.get('name')
  E.SubElement(asset,'mesh',name=mn,vertex=' '.join(fmt([sx*h[0],sy*h[1],sz*h[2]]) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)))
  g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
def build_scene(key):
 """key: play:<act> | app:<act>:<approach index> | edge:<A>__<B>. Returns ch, states (n,11), info."""
 import chain
 from scene import build
 from checker import Checker
 kind=key.split(':')
 if kind[0] in ('play','app'):
  import kitchen17 as K17
  act=kind[1];c=CHAINS[act];f=tagged(c['file']);r=J(f);_kitchen(r)
  if kind[0]=='play':
   cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])})
   tree,meta=build(cfg,None);_meshheld(tree);ch=Checker(tree,meta)
   Q=unwrap(r['play']);lab=_labels(r,c['label'],len(Q))
   return ch,Q,dict(file=f,kind='play',act=act,obj=r['obj'],labels=lab,src_n=len(Q))
  k=int(kind[2]);ap=r['approaches'][k];kfi=ap['kf'];world=c['worlds'][kfi]
  cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),'r16_tools':{'ladle':None},**world})
  tree,meta=build(cfg,None);ch=Checker(tree,meta)
  Q=np.array(r['approach_qs'][k],float)
  return ch,Q,dict(file=f,kind='approach',act=act,kf=kfi,kf_label=r['keyframes'][kfi]['label'],r17_min_reserve_mm=ap.get('min_reserve_mm'),
   labels=[f"approach@{r['keyframes'][kfi]['label']}#{kfi} step {i} ({i} cm back)" for i in range(len(Q))],src_n=len(Q))
 if kind[0]=='edge':
  sys.argv=[sys.argv[0],'commands']+[a for a in sys.argv[1:] if a.startswith(('ARM=','PY='))]   # r19hub parses argv at import (PY= moves its plate + dish)
  import r19hub
  tree,meta=r19hub.union_tree();ch=Checker(tree,meta)
  f=f'{hubdir()}/edge_{kind[1]}.json';e=J(f)
  Q=np.array(e['qs'],float)
  return ch,Q,dict(file=f,kind='edge',edge=kind[1],method=e.get('method'),reported_min_reserve_mm=e.get('min_reserve_mm'),
   labels=[f"{e['a']}->{e['b']} {100*i/max(1,len(Q)-1):.1f}%" for i in range(len(Q))],src_n=len(Q),densified=False)
 raise KeyError(key)
def _labels(r,label,n):
 try:lab=J('results/r19/prim/segments.json')['labels'][label]
 except Exception:lab=['']*n
 kf=[k['label'] for k in r['keyframes']];out=[]
 for i in range(n):
  s=lab[i] if i<len(lab) else ''
  if '->' in s:a,b=map(int,s.split('->'));s=f"kf {a}->{b} ({kf[a] or '-'} -> {kf[b] or '-'})"
  elif s.startswith('join@'):k=int(s[5:]);s=f"join at kf {k} ({kf[k]})"
  out.append(s)
 return out
def densify(ch,Q,step=.004):
 """Stored states joint-linear in between, subdivided so that point_bound.segment_bound <= step per sub-step
 (as r19smooth.sample_poly / planner.edge). Returns states and their fractional source index."""
 pb=ch.point_bound;out=[Q[0]];src=[0.]
 for i in range(len(Q)-1):
  b=pb.segment_bound(Q[i],Q[i+1]);n=max(1,int(math.ceil(b/step)))
  for k in range(1,n+1):out.append(Q[i]+(Q[i+1]-Q[i])*k/n);src.append(i+k/n)
 return np.array(out),np.array(src)
# ---------------------------------------------------------------- the evaluator
def Rz(a):c,s=math.cos(a),math.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def Rx(a):c,s=math.cos(a),math.sin(a);return np.array([[1.,0,0],[0,c,-s],[0,s,c]])
def Ry(a):c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1.,0],[-s,0,c]])
def Rax(u,a):
 from scipy.spatial.transform import Rotation
 return Rotation.from_rotvec(np.asarray(u,float)*a).as_matrix()
CART_AXES=('x','y','z','yaw','tilt_x','tilt_y')   # m, m, m, rad, rad, rad
LIM=.08   # m: pairs farther than this past their gate at nominal are not kept per state (no perturbation here moves
          # any point by more than 20 mm + 2 deg x 1.5 m = 0.073 m); minima above LIM are reported as LIM
CONTACT_EPS=1e-5   # m: 'contact' = distance below 0.01 mm (the certificate clamps penetration to 0)
class Ev:
 def __init__(s,ch):
  m=ch.m;s.ch=ch;s.m=m;s.d=ch.d;B=ch.bounds;s.B=B;G=m.ngeom;nm=ch.gnames
  robot=np.array([bool(ch.robot[g]) for g in range(G)]);s.robot=robot
  tool=m.body('R_tool').id
  s.held=np.array([robot[g] and m.geom_bodyid[g]==tool and nm[g]!='R_gripper_palm' and not nm[g].startswith('R_gripper_oem') for g in range(G)])   # gripper housing (box, or the pgc drawing's 3 parts) is not held
  s.rob=np.flatnonzero(robot);s.hg=np.flatnonzero(s.held)
  P=B.pairs;a=np.array([p[0] for p in P]);b=np.array([p[1] for p in P]);need=np.array([p[2] for p in P],float)
  ra,rb=robot[a],robot[b];env=ra^rb
  s.pr=np.where(ra,a,b)[env];s.pe=np.where(ra,b,a)[env];s.pn=need[env]   # robot side, environment side, gap
  hs=(ra&rb)&(s.held[a]^s.held[b])   # held part vs the robot's own (non-gripper) geoms ('self', gap 0)
  s.hr=np.where(s.held[a],a,b)[hs];s.ho=np.where(s.held[a],b,a)[hs];s.hn=need[hs]
  he=s.held[s.pr];s.ph=np.flatnonzero(he)   # env pairs whose robot side is the held part
  s.gpa=np.r_[s.pr[s.ph],s.hr];s.gpb=np.r_[s.pe[s.ph],s.ho];s.gpn=np.r_[s.pn[s.ph],s.hn]   # all pairs of the held part (grasp mode)
  # static environment AABBs (the scene has no environment joints)
  mujoco.mj_kinematics(m,s.d);s.LO=np.zeros((G,3));s.HI=np.zeros((G,3))
  for g in range(G):
   if robot[g]:continue
   if m.geom_type[g]==0:s.LO[g]=-1e6;s.HI[g]=1e6;continue
   for k in range(3):e=np.eye(3)[k];s.LO[g,k]=B.support(g,-e)[k];s.HI[g,k]=B.support(g,e)[k]
  s.envpos=s.d.geom_xpos.copy()
  s.groups={}
  for gn,fn in GROUPS.items():
   mem=np.array([(not robot[g]) and fn(nm[g],s.envpos[g]) for g in range(G)])
   msk=mem[s.pe];idx=np.flatnonzero(msk)
   if len(idx):s.groups[gn]=dict(geoms=np.flatnonzero(mem),pairs=idx,mask=msk)
  # enclosing oriented boxes (geom frame centre offset, half extents) for the separating-axis lower bound
  s.oc=np.zeros((G,3));s.oe=np.zeros((G,3));s.plane=m.geom_type==0
  for g in range(G):
   t_,sz=m.geom_type[g],m.geom_size[g]
   if t_==6:s.oe[g]=sz
   elif t_==7:V=B.local[g];s.oc[g]=(V.max(0)+V.min(0))/2;s.oe[g]=(V.max(0)-V.min(0))/2
   elif t_==3:s.oe[g]=[sz[0],sz[0],sz[1]+sz[0]]
   elif t_==5:s.oe[g]=[sz[0],sz[0],sz[1]]
   elif t_==2:s.oe[g]=[sz[0]]*3
   elif t_==4:s.oe[g]=sz
  s.OR=s.d.geom_xmat.reshape(-1,3,3).copy();s.OC=s.d.geom_xpos+np.einsum('nij,nj->ni',s.OR,s.oc)
  # robot geom types for vectorized AABBs
  t=m.geom_type[s.rob];s.size=m.geom_size[s.rob]
  s.tb={k:np.flatnonzero(t==k) for k in (2,3,4,5,6)};s.tmesh=[(i,B.local[g]) for i,g in enumerate(s.rob) if t[i]==7]
  s.rb=m.geom_rbound[s.rob]
  s.mount=m.body('R_mount').id;s.cart=m.body('rail_structure').id;s.sid=m.site('R_prep').id
  # jaw axis in the tool frame (finger centres), for grasp rotations
  mujoco.mj_kinematics(m,s.d);Rt=s.d.xmat[tool].reshape(3,3);fp=[s.d.geom_xpos[m.geom(n).id] for n in ('R_finger_minus','R_finger_plus')]
  u=Rt.T@(fp[1]-fp[0]);s.jaw_axis=u/np.linalg.norm(u)
  s.cache={}
 # ---- pose of all geoms for a state and a perturbation
 def pose(s,q,cart=None,grasp=None):
  """cart: (x,y,z,yaw,tilt_x,tilt_y) rigid move of the whole robot; grasp: (dx,dy,dz,rot about the jaw
  axis) of the held part in the tool frame. Writes d.geom_xpos / geom_xmat (read by Bounds)."""
  m,d=s.m,s.d;d.qpos[:]=q;mujoco.mj_kinematics(m,d);s.cache={}
  if grasp is not None and len(s.hg):
   Rs=d.site_xmat[s.sid].reshape(3,3);ps=d.site_xpos[s.sid].copy()
   Rw=Rs@Rax(s.jaw_axis,grasp[3])@Rs.T;t=Rs@np.asarray(grasp[:3],float)
   X=d.geom_xpos[s.hg];d.geom_xpos[s.hg]=(X-ps)@Rw.T+ps+t
   M=d.geom_xmat[s.hg].reshape(-1,3,3);d.geom_xmat[s.hg]=np.einsum('ij,njk->nik',Rw,M).reshape(-1,9)
  if cart is not None and any(abs(v)>0 for v in cart):
   x,y,z,yaw,tx,ty=cart;pm=d.xpos[s.mount].copy();pc=d.xpos[s.cart].copy();pc[2]=0.
   X=d.geom_xpos[s.rob].copy();M=d.geom_xmat[s.rob].reshape(-1,3,3).copy();R=np.eye(3)
   if tx or ty:Rt_=Rx(tx)@Ry(ty);X=(X-pc)@Rt_.T+pc;M=np.einsum('ij,njk->nik',Rt_,M);pm=Rt_@(pm-pc)+pc
   if yaw:Ry_=Rz(yaw);X=(X-pm)@Ry_.T+pm;M=np.einsum('ij,njk->nik',Ry_,M)   # about the (tilted) J1 axis line, vertical
   X=X+np.array([x,y,z]);d.geom_xpos[s.rob]=X;d.geom_xmat[s.rob]=M.reshape(-1,9)
  s._aabb()
 def _aabb(s):
  d=s.d;X=d.geom_xpos[s.rob];M=d.geom_xmat[s.rob].reshape(-1,3,3);E=np.zeros((len(s.rob),3));sz=s.size
  i=s.tb[6]
  if len(i):E[i]=np.einsum('nij,nj->ni',np.abs(M[i]),sz[i])
  i=s.tb[3]
  if len(i):a=np.abs(M[i][:,:,2]);E[i]=a*sz[i,1:2]+sz[i,0:1]
  i=s.tb[5]
  if len(i):a=M[i][:,:,2];E[i]=np.abs(a)*sz[i,1:2]+sz[i,0:1]*np.sqrt(np.clip(1-a*a,0,1))
  i=s.tb[2]
  if len(i):E[i]=sz[i,0:1]
  i=s.tb[4]
  if len(i):E[i]=np.sqrt(np.einsum('nij,nj->ni',M[i]**2,sz[i]**2))
  LO=X-E;HI=X+E
  for k,V in s.tmesh:
   W=V@M[k].T+X[k];LO[k]=W.min(0);HI[k]=W.max(0)
  s.LO[s.rob]=LO;s.HI[s.rob]=HI
  s.OR[s.rob]=M;s.OC[s.rob]=X+np.einsum('nij,nj->ni',M,s.oc[s.rob])
 def sat(s,pa,pb,shift=None):
  """Separating-axis lower bound of the distance of the enclosing oriented boxes of each pair (15 axes):
  the gap along any unit axis is <= the distance, and the boxes enclose the geoms. 0 for planes."""
  CA,CB=s.OC[pa],s.OC[pb]
  if shift is not None:CB=CB+shift
  RA,RB,eA,eB=s.OR[pa],s.OR[pb],s.oe[pa],s.oe[pb];T=CB-CA;best=np.zeros(len(pa))
  ax=[RA[:,:,i] for i in range(3)]+[RB[:,:,j] for j in range(3)]+[np.cross(RA[:,:,i],RB[:,:,j]) for i in range(3) for j in range(3)]
  for L in ax:
   n=np.sqrt(np.einsum('ij,ij->i',L,L));ok=n>1e-6;L=L/np.where(ok,n,1.)[:,None]
   rA=np.einsum('ni,ni->n',np.abs(np.einsum('nki,nk->ni',RA,L)),eA);rB=np.einsum('ni,ni->n',np.abs(np.einsum('nki,nk->ni',RB,L)),eB)
   sep=np.abs(np.einsum('ij,ij->i',T,L))-rA-rB;best=np.maximum(best,np.where(ok,sep,0.))
  pl=np.flatnonzero(s.plane[pb])   # plane (floor) on the environment side: half-space distance of the robot box
  if len(pl):
   nrm=RB[pl][:,:,2];p0=CB[pl]-np.einsum('nij,nj->ni',RB[pl],s.oc[pb[pl]])
   lo=np.einsum('ij,ij->i',CA[pl],nrm)-np.einsum('ni,ni->n',np.abs(np.einsum('nki,nk->ni',RA[pl],nrm)),eA[pl])
   best[pl]=np.maximum(lo-np.einsum('ij,ij->i',p0,nrm),0.)
  best[s.plane[pa]]=0.
  return best
 def bound(s,pa,pb,shift=None):
  """max(AABB separation, oriented-box separating-axis bound): a lower bound of every pair distance."""
  LOb,HIb=s.LO[pb],s.HI[pb]
  if shift is not None:LOb=LOb+shift;HIb=HIb+shift
  dl=np.maximum(np.maximum(s.LO[pa]-HIb,LOb-s.HI[pa]),0.);ab=np.sqrt(np.einsum('ij,ij->i',dl,dl))
  if not len(pa):return ab
  return np.maximum(ab,s.sat(pa,pb,shift))
 # ---- branch and bound over a pair set
 def _gjk(s,a,b,key):
  v=s.cache.get(key)
  if v is None:v=s.cache[key]=s.B.pair(int(a),int(b))['lower_m']
  return v
 def minpairs(s,pa,pb,need,shift=None,stop=None,measure=None,cap=None,budget=None):
  """Minimum (Bounds semantics: max of the AABB and GJK lower bounds per pair) over the pairs (pa robot
  side, pb other side, need) of gate = dist - need and contact = dist, by branch and bound.
  shift: environment-side translation (fixture offset; the caller has moved d.geom_xpos of those geoms).
  measure: 'gate' or 'contact' only (the other is returned as 1e9).
  stop: return as soon as a value < stop is found (feasibility test); values >= stop are then only bounds.
  cap: only values below cap matter (a global best elsewhere); a returned value >= cap is only a bound.
  budget: at most this many GJK refinements; the result is then a valid LOWER BOUND (used for ordering).
  Without stop / cap / budget the result is exact. Returns gate, gate pair index, contact, contact pair index."""
  if not len(pa):return 1e9,-1,1e9,-1
  ab=s.bound(pa,pb,shift)
  res=[]
  for kk,key in enumerate((ab-need,ab)):
   if measure is not None and measure!=('gate','contact')[kk]:res+=[1e9,-1];continue
   thr0=min(x for x in (stop,cap,1e9) if x is not None)
   if thr0<1e8:cand=np.flatnonzero(key<thr0);cand=cand[np.argsort(key[cand],kind='stable')]   # pairs at or above the threshold cannot matter
   else:cand=np.argsort(key,kind='stable')
   best,bi,n=1e9,-1,0;lb=None
   for i in cand:
    if key[i]>=min(best,thr0):break
    if budget is not None and n>=budget:lb=float(key[i]);break   # anytime bound: min(best, next key) <= the exact minimum
    lo=max(ab[i],s._gjk(pa[i],pb[i],(int(pa[i]),int(pb[i]))));v=lo-need[i] if kk==0 else lo;n+=1
    if v<best:best,bi=v,int(i)
    if stop is not None and best<stop:break
   if lb is not None and lb<best:best=lb   # a valid lower bound, not an exact minimum
   res+=[best,bi]
  return tuple(res)
 # ---- one state under a perturbation, restricted to the pairs it can change
 def value(s,q,pert,stop=None,measure=None,cap=None,nom=None):
  """pert: dict(kind=cart|fix|grasp|none, v=vector). Returns gate_mm, gate pair names, contact_mm, contact pair names
  (measure='gate' / 'contact': only that one, the other is 1e12). nom: the state's nominal() record; then only
  the pairs whose NOMINAL gate lower bound is below (stop or cap) + D are evaluated, D = disp_bound (any pair's
  true distance changes by at most D, so the others cannot reach the threshold); without a threshold all
  pairs within LIM of the gate at nominal."""
  k=pert['kind'];v=pert.get('v');sh=None
  if k=='grasp':s.pose(q,grasp=v);base=(s.gpa,s.gpb,s.gpn);cs=nom['cg'] if nom else None;msk=None
  else:
   s.pose(q,cart=v if k=='cart' else None);base=(s.pr,s.pe,s.pn);cs=nom['ce'] if nom else None;msk=None
   if k=='fix':
    gr=s.groups[pert['group']];msk=gr['mask'];sh=np.asarray(v,float);s.d.geom_xpos[gr['geoms']]+=sh
  if cs is not None:
   thr=min(x for x in (stop,cap,1e9) if x is not None);D=disp_bound(nom,pert)
   sel=cs[0][:np.searchsorted(cs[1],thr+D,side='right')] if thr<1e8 else cs[0]
   if msk is not None:sel=sel[msk[sel]]
  else:sel=np.flatnonzero(msk) if msk is not None else np.arange(len(base[0]))
  pa,pb,nd=base[0][sel],base[1][sel],base[2][sel]
  g,gi,c,ci=s.minpairs(pa,pb,nd,shift=sh,stop=stop,measure=measure,cap=cap)
  nm=s.ch.gnames;pn=lambda i:[nm[pa[i]],nm[pb[i]]] if i>=0 else None
  return g*1e3,pn(gi),c*1e3,pn(ci)
 def rho(s,q):
  """Lever arms (m) for the rigid-move displacement bound: largest distance of any robot point (geom
  centre + bounding radius) from the J1 axis (yaw), from the floor x / y lines under the cart origin
  (tilts), and of any held point from the TCP (grasp rotation)."""
  s.pose(q);return s._rho()
 def nominal(s,q,budget=0):
  """Nominal state, as LOWER BOUNDS for the branch and bound over states (at most `budget` GJK
  refinements per measure; exact whenever the minimum is found within it): env gate / contact,
  held-part pairs, per-group AABB bounds; and the lever arms of rho()."""
  s.pose(q)
  def cands(pa,pb,nd):
   dl=np.maximum(np.maximum(s.LO[pa]-s.HI[pb],s.LO[pb]-s.HI[pa]),0.);ab=np.sqrt(np.einsum('ij,ij->i',dl,dl))
   i=np.flatnonzero(ab-nd<LIM);ab[i]=np.maximum(ab[i],s.sat(pa[i],pb[i]));kg=ab-nd
   i=i[kg[i]<LIM];i=i[np.argsort(kg[i],kind='stable')];return ab,(i.astype(np.int32),(kg[i]-1e-7).astype(np.float32))   # float32, rounded down
  ab,ce=cands(s.pr,s.pe,s.pn);sel=ce[0]
  g,gi,c,ci=s.minpairs(s.pr[sel],s.pe[sel],s.pn[sel],budget=budget)
  out=dict(gate=min(g,LIM),contact=min(c,LIM),ce=ce)
  if len(s.hg):
   _,cg=cands(s.gpa,s.gpb,s.gpn);sel=cg[0];hg,_,hc,_=s.minpairs(s.gpa[sel],s.gpb[sel],s.gpn[sel],budget=budget)
   out.update(held_gate=min(hg,LIM),held_contact=min(hc,LIM),cg=cg)
  out['group_gate_lb']={gn:float(min(np.min(ab[gr['pairs']]-s.pn[gr['pairs']]),LIM)) for gn,gr in s.groups.items()}
  out['group_contact_lb']={gn:float(min(np.min(ab[gr['pairs']]),LIM)) for gn,gr in s.groups.items()}
  out.update(s._rho())
  return out
 def _rho(s):
  d=s.d;X=d.geom_xpos[s.rob];r=s.rb;pm=d.xpos[s.mount];pc=d.xpos[s.cart].copy();pc[2]=0.
  out=dict(yaw=float(np.max(np.hypot(X[:,0]-pm[0],X[:,1]-pm[1])+r)),tilt_x=float(np.max(np.hypot(X[:,1]-pc[1],X[:,2])+r)),
   tilt_y=float(np.max(np.hypot(X[:,0]-pc[0],X[:,2])+r)))
  if len(s.hg):out['held']=float(np.max(np.linalg.norm(d.geom_xpos[s.hg]-d.site_xpos[s.sid],axis=1)+s.m.geom_rbound[s.hg]))
  return out
# ---------------------------------------------------------------- perturbation helpers
def cart_vec(axis,val):
 v=[0.]*6;v[CART_AXES.index(axis)]=val;return v
def pert_of(kind,axis,val,group=None):
 """val in m or rad."""
 if kind=='cart':return dict(kind='cart',v=cart_vec(axis,val))
 if kind=='fix':v=[0.,0.,0.];v['xyz'.index(axis)]=val;return dict(kind='fix',group=group,v=v)
 if kind=='grasp':
  v=[0.,0.,0.,0.]
  if axis=='rot':v[3]=val
  else:v['xyz'.index(axis)]=val
  return dict(kind='grasp',v=v)
 raise KeyError(kind)
def disp_bound(nom,pert):
 """Upper bound (m) of the change of any evaluated pair distance in a state under pert."""
 k=pert['kind'];v=pert.get('v')
 if k=='cart':return math.sqrt(v[0]**2+v[1]**2+v[2]**2)+abs(v[3])*nom['yaw']+abs(v[4])*nom['tilt_x']+abs(v[5])*nom['tilt_y']+1e-9
 if k=='fix':return math.sqrt(sum(x*x for x in v))+1e-9
 if k=='grasp':return math.sqrt(v[0]**2+v[1]**2+v[2]**2)+abs(v[3])*nom.get('held',0.)+1e-9
 return 0.
def lower_key(nom,pert,measure):
 """Lower bound (m) of the nominal value of the pairs pert can change, per state."""
 k=pert['kind'];m=measure
 if k=='cart':return nom['gate' if m=='gate' else 'contact']
 if k=='fix':return nom['group_gate_lb' if m=='gate' else 'group_contact_lb'].get(pert['group'],1e9)
 if k=='grasp':return nom.get('held_gate' if m=='gate' else 'held_contact',1e9)
 return nom[m]
