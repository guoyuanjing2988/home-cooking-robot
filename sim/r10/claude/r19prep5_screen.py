"""R19 prep step 5 (#38, T2L vs prep): screens of cart-mounted T2L hardware against stored certified paths, with WHERE,
WHICH LINK and HOW DEEP. New file; r19prep4_screen.py / r19pot_screen.py are imported for their scene builders and
stored-path lists and are not changed; writes only to results/r19/prep5/.
Method (as r19prep4_screen.py): each stored state is replayed in its own scene with the new cart parts added and ONLY
the pairs (moving robot / held geom) x (new part) are measured: enclosing-AABB separation, refined by the checker's
own GJK lower bound (distance.Bounds.pair) within 30 mm of the gap; gate = distance - the checker's required gap for the
pair (ch.required: 10 mm arm / held object vs a CART part). Stored states 2pi-unwrapped, joint-linear between them, cut
to <= 4 mm (r19smooth.sample_poly); the pot-zone layer (RACK=keyed, SPX 1.56, SPY 0.20) installed.
NEW here, for every state with a violated pair:
 - depth = the exact penetration depth (minimum translation distance) of the two convex shapes, by the separating-axis
   test over all face normals of both hulls and all edge x edge cross products (complete for convex polytopes; the
   checker's own hull vertices; a capsule is its two end spheres sampled at 642 points each, i.e. under-estimated by
   < 0.1 mm). A pair that does not intersect reports depth 0 and its distance.
 - depth is computed on every DSTRIDE-th (default 3rd) hit state of a path and on every hit state within DSTRIDE of the
   deepest one found (a local refinement); hit counts, links and parts are from every state.
 - where = the centre of the two geoms' AABB overlap, in the CART frame (x from the arm base axis, +y toward the counter,
   z world) and the world; the nearest keyframe of the set (by TCP distance to the keyframe's TCP pose; approaches are
   labelled by their grasp keyframe).
MODE=t2l | t2l_empty  the step-4 T2L cradle + bracket (+ the parked pan) of kitchen19p4 (prefix R_cart_p4_)
MODE=fold | deployed  the kitchen19p5 fold-away cradle, folded / deployed (prefix R_cart_p5_)
KINDS=prep[,play,app,edge,other,stir]  prep = the certified prep sets listed in SETS (default: the #38 step-5 list);
      the others are r19prep4_screen's cooking chains (+ approaches), hub edges, cup chains, stir cycle.
python r19prep5_screen.py MODE=t2l [KINDS=prep] [SETS=f1,f2] [WORKERS=16] [TAG=..] ARM=ur5e_enc2_pgc PY=.15
 -> results/r19/prep5/screen_<MODE>[_TAG].json"""
import sys,os,json,time,glob
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a);MODE=KV.get('MODE','t2l')
_argv=sys.argv;sys.argv=[sys.argv[0],'MODE=t2l'];import r19prep4_screen as S4;sys.argv=_argv
PS=S4.PS;OUT='results/r19/prep5';CAP=.030
SETS=['results/r19/prep/chain_carrot_full_ur5e_enc2_pgc.json','results/r19/prep/chain_press_full_ur5e_enc2_pgc.json','results/r19/prep/chain_tomato_full_ur5e_enc2_pgc.json',
 'results/r19/prep/chain_soak_full_ur5e_enc2_pgc.json','results/r19/prep/chain_tubempty_full_ur5e_enc2_pgc.json','results/r19/prep/chain_ctray_full_ur5e_enc2_pgc.json',
 'results/r19/prep/chain_bascarrot_full_ur5e_enc2_pgc.json','results/r19/prep/chain_tubfill_t15fin_ur5e_enc2_pgc.json','results/r19/prep/chain_basket_y20p30_ur5e_enc2_pgc.json',
 'results/r19/prep4/chain_ct2p_full_ur5e_enc2_pgc.json']
if 'SETS' in KV:SETS=[f for f in KV['SETS'].split(',') if f]
P5KV={k[3:]:v for k,v in KV.items() if k.startswith('P5_')}   # kitchen19p5 design overrides (P5_<key>=value), for design screening
def parts_cfg():
 """cfg overrides that add this MODE's parts, and the geom-name prefix of the new parts."""
 import kitchen19p4 as P4
 if MODE in ('t2l','t2l_empty'):return dict(r19p4=dict(t2l=dict(P4.T2L,present=MODE=='t2l'))),('R_cart_p4_',)
 import kitchen19p5 as P5
 st=dict(state='folded' if MODE=='fold' else 'deployed',pan=KV.get('PAN','0')=='1',**P5.parse_kv(P5KV))
 return dict(r19p5=st),('R_cart_p5_',)
def add_parts(tree):
 import kitchen19p4 as P4
 cfg,pre=parts_cfg()
 if 'r19p4' in cfg:P4.add(tree,cfg);P4.mesh(tree)
 else:
  import kitchen19p5 as P5;P5.add(tree,cfg);P5.mesh(tree)
 return pre
S4.my_parts=add_parts   # cook_scene / union_scene / stir scenes of r19prep4_screen now add THIS mode's parts
def prep_scene(R,key):
 """a stored prep set's own scene (as r19prep4_verify / r19prep4_screen.prep_scene) + this MODE's parts."""
 import chain
 from scene import build
 from checker import Checker
 import kitchen16 as K,kitchen17 as K17,kitchen19 as K19,kitchen19p3 as P3,kitchen19p4 as P4
 names=[R['obj']]+[o[0] for o in (R['scene'].get('r19') or {}).get('objs',[])]+[o[0] for g in R.get('grasps',[]) for o in ((g['world'].get('r19') if 'r19' in g['world'] else g['world']) or {}).get('objs',[])]
 P3.ensure([n for n in names if not str(n).startswith(('dbh_','stg_p'))]);P4.ensure(names)
 if R['obj'].startswith('pusher_y'):K19.pusher_turned(float(R['obj'][8:]))
 K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 K19.LAYOUT.update({k:(tuple(v) if isinstance(v,list) and k!='drop_bowls' else v) for k,v in R['layout'].items()})
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
 if key=='play':extra=K17.held_cfg(R['obj'],R['grasp_sense']);wo=None
 else:
  g=R['grasps'][key];kf=R['keyframes'][g['kf']];extra=g['world'] if 'r19' in g['world'] else dict(r19=g['world'])
  seat=kf.get('seat',.008 if R['obj'] in ('carrot','tomato') else 0.);wo=[R['obj'],kf['R'],(np.array(kf['p'])-[0,0,seat]).tolist()] if g['object_in_world'] is True else None
 cfg=chain.chain_cfg('SD',**{**BASE,**R['scene'],**extra})
 if wo is not None:cfg['r19']=dict(cfg['r19'],objs=list(cfg['r19'].get('objs',[]))+[wo])
 t2=(cfg.get('r19p4') or {}).get('t2l')
 if t2 and MODE in ('fold','deployed'):   # a set with its own step-4 cradle (stgwok, p2t2l): that cradle is REPLACED by this mode's p5 cradle, the pan parked on it as in the set
  pc,_=parts_cfg();cfg['r19p4']={k:v for k,v in cfg['r19p4'].items() if k!='t2l'};cfg['r19p5']=dict(pc['r19p5'],pan=bool(t2.get('present',True)) and pc['r19p5']['state']=='deployed')
  t2='converted'
 own=t2 or (R['scene'].get('r19p5'))
 tree,meta=build(cfg,None);K19.add(tree,cfg);P4.add(tree,cfg);P3.mesh_held(tree)
 if cfg.get('r19p5'):
  import kitchen19p5 as P5;P5.add(tree,cfg)
 Rl,p=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],Rl,p,rgba='.75 .77 .8 1')
 if own:   # the set carries its own T2L / fold state (e.g. stgwok, the fold sets): its own parts stay, nothing is added
  P4.mesh(tree)
  if cfg.get('r19p5'):P5.mesh(tree)
  pre=('R_cart_p4_cradle','R_cart_p4_bracket') if MODE.startswith('t2l') else ('R_cart_p5_',)
 else:pre=add_parts(tree)
 return Checker(tree,meta),pre
# ---------------- exact penetration depth (SAT) ----------------
def _ico(n=3):
 t=(1+5**.5)/2;V=[[-1,t,0],[1,t,0],[-1,-t,0],[1,-t,0],[0,-1,t],[0,1,t],[0,-1,-t],[0,1,-t],[t,0,-1],[t,0,1],[-t,0,-1],[-t,0,1]]
 F=[[0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],[1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],[3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],[4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]]
 V=[np.array(v,float)/np.linalg.norm(v) for v in V]
 for _ in range(n):
  cache={};F2=[]
  def mid(a,b):
   k=(min(a,b),max(a,b))
   if k not in cache:v=V[a]+V[b];V.append(v/np.linalg.norm(v));cache[k]=len(V)-1
   return cache[k]
  for a,b,c in F:ab,bc,ca=mid(a,b),mid(b,c),mid(c,a);F2+=[[a,ab,ca],[b,bc,ab],[c,ca,bc],[ab,bc,ca]]
  F=F2
 return np.array(V)
ICO=_ico(3)   # 642 unit points
_HULL={}
def local_hull(ch,g):
 """(vertices, unique face normals, unique edge directions) of geom g in its own frame (convex)."""
 if g in _HULL:return _HULL[g]
 import mujoco
 from scipy.spatial import ConvexHull
 m=ch.m;t=int(m.geom_type[g]);s=m.geom_size[g]
 if t==mujoco.mjtGeom.mjGEOM_MESH:V=ch.bounds.local[g]
 elif t==mujoco.mjtGeom.mjGEOM_BOX:V=np.array([[a*s[0],b*s[1],c*s[2]] for a in(-1,1) for b in(-1,1) for c in(-1,1)])
 elif t==mujoco.mjtGeom.mjGEOM_CAPSULE:V=np.vstack([ICO*s[0]+[0,0,s[1]],ICO*s[0]-[0,0,s[1]]])
 elif t==mujoco.mjtGeom.mjGEOM_SPHERE:V=ICO*s[0]
 elif t==mujoco.mjtGeom.mjGEOM_CYLINDER:a=np.linspace(0,2*np.pi,65)[:-1];V=np.array([[s[0]*np.cos(x),s[0]*np.sin(x),z] for x in a for z in(-s[1],s[1])])
 else:raise ValueError(('geom type',t))
 h=ConvexHull(V);V=V[h.vertices];h=ConvexHull(V)
 N=np.unique(np.round(h.equations[:,:3],9),axis=0)
 E=set()
 for s_,tri in enumerate(h.simplices):   # true hull edges only (the two adjacent triangles not coplanar): triangulation diagonals add no axis
  for j in range(3):
   nb=h.neighbors[s_][j]
   if h.equations[s_,:3]@h.equations[nb,:3]>1-1e-9:continue
   a_,b_=[tri[k] for k in range(3) if k!=j];e=V[b_]-V[a_];e=e/np.linalg.norm(e)
   k=np.argmax(abs(e));e=e if e[k]>0 else -e;E.add(tuple(np.round(e,7)))
 _HULL[g]=(V,N,np.array(sorted(E)));return _HULL[g]
def depth(ch,a,b):
 """exact penetration depth (m) of geoms a, b at the current kinematics (0 if they do not overlap)."""
 d=ch.d;out=[]
 for g in (a,b):
  V,N,E=local_hull(ch,g);R=d.geom_xmat[g].reshape(3,3);p=d.geom_xpos[g];out.append((V@R.T+p,N@R.T,E@R.T))
 (VA,NA,EA),(VB,NB,EB)=out
 C=np.cross(EA[:,None,:],EB[None,:,:]).reshape(-1,3);n=np.linalg.norm(C,axis=1);C=C[n>1e-6]/n[n>1e-6,None]
 X=np.vstack([NA,NB,C]);pa=VA@X.T;pb=VB@X.T
 o=np.minimum(pa.max(0)-pb.min(0),pb.max(0)-pa.min(0))
 return float(max(o.min(),0.))
# ---------------- measurement ----------------
class Meas:
 """per state: every violated (moving robot / held geom, new part) pair with gate, distance, depth, where."""
 def __init__(s,ch,prefix,held_sphere=False):
  m=ch.m;s.ch=ch;s.m=m;nm=ch.gnames;s.new=[g for g in range(m.ngeom) if nm[g].startswith(prefix)];w={int(ch.weld[g]) for g in s.new}
  mov=[g for g in range(m.ngeom) if (ch.robot[g] or ch.held[g]) and g not in s.new and int(ch.weld[g]) not in w and m.geom_type[g]!=0];pr=[]
  for a in mov:
   for b in s.new:
    q=ch.required(ch,a,b)
    if q is not None:pr.append((a,b,q[0]))
  s.A=np.array([p[0] for p in pr],int);s.B=np.array([p[1] for p in pr],int);s.N=np.array([p[2] for p in pr]);s.geoms=sorted(set(s.A.tolist())|set(s.new));s.sid=m.site('R_prep').id
  s.held_sphere=held_sphere;s.env_best=(1e9,None,None)
  import mujoco
  env=[g for g in range(m.ngeom) if not ch.robot[g] and not ch.held[g] and m.geom_type[g]!=0 and g not in s.new] if KV.get('ENV','1')=='1' else []
  mujoco.mj_kinematics(m,ch.d);s.elo=np.zeros((m.ngeom,3));s.ehi=np.zeros((m.ngeom,3))
  for g in env:
   R=ch.d.geom_xmat[g].reshape(3,3);c=ch.d.geom_xpos[g]+R@m.geom_aabb[g,:3];e=np.abs(R)@m.geom_aabb[g,3:];s.elo[g]=c-e;s.ehi[g]=c+e
  s.EA=np.array([b for b in s.new for e in env],int);s.EB=np.array([e for b in s.new for e in env],int)
 def __call__(s,q,want_depth=True):
  import mujoco
  m,d=s.m,s.ch.d;d.qpos[:]=q;mujoco.mj_kinematics(m,d);lo=np.zeros((m.ngeom,3));hi=np.zeros((m.ngeom,3))
  for g in s.geoms:
   R=d.geom_xmat[g].reshape(3,3);c=d.geom_xpos[g]+R@m.geom_aabb[g,:3];e=np.abs(R)@m.geom_aabb[g,3:];lo[g]=c-e;hi[g]=c+e
  best=(1e9,None,1e9);viol=[]
  if not len(s.A):return best,viol
  dl=np.maximum(np.maximum(lo[s.A]-hi[s.B],lo[s.B]-hi[s.A]),0.);ab=np.sqrt((dl*dl).sum(1));key=ab-s.N
  for i in np.argsort(key):
   if key[i]>=min(max(best[0],0.),CAP) and key[i]>=0:break
   a,b=int(s.A[i]),int(s.B[i]);dist=max(ab[i],s.ch.bounds.pair(a,b)['lower_m']);v=dist-s.N[i]
   if v<best[0]:best=(float(v),[s.ch.gnames[a],s.ch.gnames[b]],float(dist))
   if v<0:
    dp=depth(s.ch,a,b) if (want_depth and dist<=1e-9) else 0.
    ol=np.maximum(lo[a],lo[b]);oh=np.minimum(hi[a],hi[b]);c=(ol+oh)/2
    viol.append(dict(pair=[s.ch.gnames[a],s.ch.gnames[b]],gate_mm=round(v*1e3,2),dist_mm=round(dist*1e3,2),depth_mm=round(dp*1e3,1),
     where_cart=[round(c[0]-q[0],3),round(c[1]-q[1],3),round(c[2],3)],where_world=[round(x,3) for x in c]))
  if best[1] is None:i=int(np.argmin(key));best=(float(key[i]),[s.ch.gnames[s.A[i]],s.ch.gnames[s.B[i]]],float(ab[i]))
  if s.held_sphere:   # an unmodelled held object (cups) within PS.HELD_R of the TCP, 10 mm cart-part gap: point-to-AABB lower bound (as r19prep4_screen)
   p=d.site_xpos[s.sid]
   for g in s.new:
    dd=float(np.linalg.norm(np.maximum(np.maximum(lo[g]-p,p-hi[g]),0.)))-PS.HELD_R-.010
    if dd<best[0]:best=(dd,['held object within %.2f m of the TCP'%PS.HELD_R,s.ch.gnames[g]],dd+.010)
    if dd<0:viol.append(dict(pair=['held sphere',s.ch.gnames[g]],gate_mm=round(dd*1e3,2),dist_mm=None,depth_mm=0.,where_cart=None,where_world=None))
  if len(s.EA):   # environment pairs of the new (cart) parts: the checker does not gate them; screened here at 10 mm
   dl=np.maximum(np.maximum(lo[s.EA]-s.ehi[s.EB],s.elo[s.EB]-hi[s.EA]),0.);ab2=np.sqrt((dl*dl).sum(1))
   for i in np.flatnonzero(ab2<.03):
    dist=max(ab2[i],s.ch.bounds.pair(int(s.EA[i]),int(s.EB[i]))['lower_m'])
    if dist<s.env_best[0]:s.env_best=(float(dist),[s.ch.gnames[s.EA[i]],s.ch.gnames[s.EB[i]]],round(float(q[0]),3))
  return best,viol
def kf_tcps(R):
 import kitchen16 as K
 out=[]
 for k in R['keyframes']:
  try:out.append((k['label'],np.array(K.tcp_pose(R['obj'],np.array(k['R']),np.array(k['p']),R.get('grasp_sense',1))[0])))
  except Exception:pass
 return out
def run_path(task):
 kind,name,arg=task;t0=time.monotonic()
 try:
  S4.potzone();held_sphere=False;sp=None
  if kind=='prep':
   f,key=arg;R=PS.J(f);ch,pre=prep_scene(R,key);Q=R['play'] if key=='play' else R['approach_qs'][key];X,sp=PS.sample(ch,Q)
   kfs=kf_tcps(R) if key=='play' else [(f"approach of '{R['keyframes'][R['grasps'][key]['kf']]['label']}'",None)]
  elif kind in ('play','app'):   # cooking chains + approaches (r19prep4_screen.run_path scenes)
   f,plate2=arg[0],arg[1];r=PS.J(f);PS.kitchen(r);S4.potzone()
   if kind=='play':ch,pre=S4.cook_scene(r,True,{},plate2);Q=r['play'];kfs=[('play',None)]
   else:
    k=arg[2];ap=r['approaches'][k];n=len(r['keyframes']);wd=PS.APP_WORLDS.get(r['obj'],lambda n:{})(n).get(ap['kf'],{})
    ch,pre=S4.cook_scene(r,False,wd,plate2);Q=r['approach_qs'][k];kfs=[(f'approach {k}',None)]
   X,sp=PS.sample(ch,Q)
  elif kind=='stir':
   import chain,kitchen16 as K
   from scene import build
   from checker import Checker
   from r19enc_check import meshheld
   L=PS.J(arg);K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);S4.potzone()
   cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=L['params']['grip_m'],r15_spatula_jaw=-1,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
   tree,meta=build(cfg,None);meshheld(tree);pre=add_parts(tree);ch=Checker(tree,meta);X,sp=PS.sample(ch,L['states']['q']);kfs=[('stir',None)]
  else:   # hub edges / cup chains in the r19hub union scene
   import kitchen16 as K
   K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);S4.potzone();ch,pre=S4.union_scene()
   if kind=='edge':X=np.array(PS.J(arg)['qs'],float)
   else:r=PS.J(arg);X,sp=PS.sample(ch,r['play']);X=np.concatenate([X]+[np.array(a,float) for a in r.get('approach_qs',[]) if a]);held_sphere=True
   kfs=[(kind,None)]
  me=Meas(ch,pre,held_sphere);best=(1e9,None,1e9);arg_i=None;H={};ST=int(KV.get('DSTRIDE',3))
  for i,q in enumerate(X):   # pass 1: gates of every state (no depth)
   b,viol=me(q,want_depth=False)
   if b[0]<best[0]:best=b;arg_i=i
   if viol:
    if kfs[0][1] is None:lab=kfs[0][0]
    else:tc=ch.d.site_xpos[me.sid].copy();lab=min(kfs,key=lambda t:np.linalg.norm(t[1]-tc))[0]
    H[i]=dict(state=i,cart=round(float(q[0]),3),kf=lab,viol=viol,depth_mm=None)
  def dep(i):
   if H[i]['depth_mm'] is None:
    _,v=me(X[i],want_depth=True);H[i]['viol']=sorted(v,key=lambda x:-x['depth_mm'])[:3];H[i]['depth_mm']=max(x['depth_mm'] for x in v)
   return H[i]['depth_mm']
  ks=sorted(H)
  for i in ks[::ST]:dep(i)   # pass 2: exact depth on every DSTRIDE-th hit state, then all hit states within DSTRIDE of the deepest
  if ks:
   top=max((i for i in ks if H[i]['depth_mm'] is not None),key=lambda i:H[i]['depth_mm'])
   j=ks.index(top)
   for i in ks[max(0,j-ST):j+ST+1]:dep(i)
  hits=[H[i] for i in ks];bypart={};bylink={};bykf={}
  for h in hits:
   bykf[h['kf']]=bykf.get(h['kf'],0)+1
   for v in h['viol']:
    if h['depth_mm'] is None:bypart.setdefault(v['pair'][1],0.);bylink.setdefault(v['pair'][0],0.);continue
    bypart[v['pair'][1]]=max(bypart.get(v['pair'][1],0.),v['depth_mm']);bylink[v['pair'][0]]=max(bylink.get(v['pair'][0],0.),v['depth_mm'])
  hits=[h if h['depth_mm'] is not None else dict(h,viol=h['viol'][:2]) for h in hits]
  deep=max([h for h in hits if h['depth_mm'] is not None],key=lambda h:h['depth_mm']) if hits else None
  return dict(kind=kind,name=name,states=len(X),max_step_bound_mm=None if sp is None else round(sp*1e3,3),new_geoms=len(me.new),pairs=len(me.A),
   min_gate_mm=round(best[0]*1e3,2) if best[1] else None,min_dist_mm=round(best[2]*1e3,2) if best[1] else None,pair=best[1],state=arg_i,
   env_min_gap_mm=None if me.env_best[1] is None else round(me.env_best[0]*1e3,2),env_pair=me.env_best[1],env_cart=me.env_best[2],bounded_by_held_sphere=held_sphere,
   hit_states=len(hits),max_depth_mm=deep['depth_mm'] if deep else None,deepest=deep,depth_by_part_mm=bypart,depth_by_link_mm=bylink,hit_states_by_keyframe=bykf,
   hit_state_range=[hits[0]['state'],hits[-1]['state']] if hits else None,depth_stride=ST,hits_sample=[h for h in hits if h['depth_mm'] is not None][::max(1,len(hits)//(12*ST))][:14],elapsed_s=round(time.monotonic()-t0,1))
 except Exception:
  import traceback;return dict(kind=kind,name=name,error=traceback.format_exc()[-900:])
def tasks():
 kinds=KV.get('KINDS','prep').split(',');T=[]
 if 'prep' in kinds:
  for f in SETS:
   R=PS.J(f)
   if not R.get('ok'):continue
   nm=os.path.basename(f)[6:-5];T.append(('prep',nm,(f,'play')))
   for k,a in enumerate(R.get('approach_qs') or []):
    if a:T.append(('prep',f'{nm}@app{k}',(f,k)))
 rest=[k for k in kinds if k!='prep']
 if rest:
  S4.KV['KINDS']=','.join(rest);T+=[t for t in S4.tasks() if t[0]!='prep']
 return T
def main():
 import multiprocessing as mp
 T=tasks();t0=time.monotonic();print('tasks',len(T),flush=True)
 with mp.Pool(min(int(KV.get('WORKERS',16)),len(T)),maxtasksperchild=1) as pool:
  try:res=pool.map_async(run_path,T,chunksize=1).get(timeout=float(KV.get('TLIM',280)))   # own wall-clock limit: the pool is terminated cleanly (no orphaned workers)
  except mp.TimeoutError:pool.terminate();print('TIME LIMIT',KV.get('TLIM',280),'s: no result written',flush=True);return
 ok=[r for r in res if 'error' not in r];bad=[r for r in res if 'error' in r]
 worst=min(ok,key=lambda r:r['min_gate_mm'] if r.get('min_gate_mm') is not None else 1e9) if ok else None
 sets={}
 for r in ok:
  if r['kind']!='prep':continue
  s=r['name'].split('@')[0];e=sets.setdefault(s,dict(hit_states=0,max_depth_mm=0.,min_gate_mm=1e9,parts={}))
  e['hit_states']+=r['hit_states'];e['max_depth_mm']=max(e['max_depth_mm'],r['max_depth_mm'] or 0.);e['min_gate_mm']=min(e['min_gate_mm'],r['min_gate_mm'] if r['min_gate_mm'] is not None else 1e9)
  e['parts'][r['name']]=dict(states=r['states'],hits=r['hit_states'],max_depth_mm=r['max_depth_mm'])
 cfg,pre=parts_cfg()
 summ=dict(mode=MODE,parts_cfg=cfg,prefix=pre,paths=len(res),errors=len(bad),states=sum(r['states'] for r in ok),hit_paths=[r['name'] for r in ok if r.get('hit_states')],
  worst=None if worst is None else {k:worst.get(k) for k in ('kind','name','min_gate_mm','min_dist_mm','pair')},
  by_kind={k:min([r['min_gate_mm'] for r in ok if r['kind']==k and r.get('min_gate_mm') is not None],default=None) for k in ('prep','play','app','edge','other','stir')},
  prep_sets=sets,potzone=S4.POT)
 import arms;summ['arm']=arms.current()
 os.makedirs(OUT,exist_ok=True);fn=f"{OUT}/screen_{MODE}{('_'+KV['TAG']) if 'TAG' in KV else ''}.json";json.dump(dict(summary=summ,method=__doc__,rows=res),open(fn,'w'),indent=1,default=float)
 print(fn,json.dumps({k:v for k,v in summ.items() if k!='prep_sets'},default=float),flush=True)
 for s,e in sets.items():print('  SET',s,'hits',e['hit_states'],'max depth',e['max_depth_mm'],'min gate',e['min_gate_mm'],flush=True)
 for r in sorted(ok,key=lambda r:r['min_gate_mm'] if r.get('min_gate_mm') is not None else 1e9)[:12]:
  print('  ',r['kind'],r['name'],r['states'],'min gate',r.get('min_gate_mm'),r.get('pair'),'hits',r.get('hit_states'),'depth',r.get('max_depth_mm'),flush=True)
 for r in bad:print('  ERROR',r['name'],r['error'][-500:],flush=True)
 print('done',round(time.monotonic()-t0),'s')
if __name__=='__main__':main()
