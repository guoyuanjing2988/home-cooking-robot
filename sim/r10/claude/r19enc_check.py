"""R19 #12: the stored UR5e paths re-checked with collision geoms that ENCLOSE the real arm (ARM=ur5e_enc).

ur5e_enc (arms.py, r19/arm_ur5e_enc.json from r19ur5e_encfit.py) is the UR5e with the same bodies, joints,
masses, limits, speeds and torque envelope; only its collision geoms differ: they contain every point of the
MuJoCo Menagerie visual meshes (certified in r19ur5e_encfit.py), while the Menagerie geoms that the sim uses
let the meshes stick out by up to 26.5 mm (r19ur5e_enclose.py).

Commands (each < 5 min with 24 workers, except as noted in R19_UR5E_ENC.md):
 python r19enc_check.py enclose              r19ur5e_enclose.py-style protrusion, measured in the SIM model (both arms)
 python r19enc_check.py self [N=2000]        random-pose self-collision rate (both arms)
 python r19enc_check.py recheck SET=<set> [WORKERS=24] [EDGES=A__B,C__D] [NEW=ur5e_enc|ur5e_enc2] [SUFFIX=_<arm>]
   (NEW = the enclosing arm checked next to ur5e, default ur5e_enc -> results/r19/enc; ur5e_enc2 -> results/r19/enc2;
    every command below takes NEW=; a chain with "ok": false or no play is skipped, not checked)
   SET = wok | wok_plate2b | lever | lid | spider | spatula   (results/r17/chain_*.json; SUFFIX=_ur5e_enc re-checks the
         re-planned chain_*_ur5e_enc.json instead, -> <set>_ur5e_enc.json)
         stir                                                (results/r19/stir/stirwalk2_h_scrape_dice_r17.json)
         hub                                                 (results/r19/hub/edge_*.json; EDGES= a subset -> hub_<i>.json lanes)
   -> results/r19/enc/<set>.json
 python r19enc_check.py summary              -> results/r19/enc/summary.json (+ the table printed)
 python r19enc_check.py meshgap              -> results/r19/enc/meshgap.json: for every ur5e_enc hit pair, at its worst state,
                                                the gap of the REAL arm surface (Menagerie visual meshes, 2 mm grid) to the fixture

Re-check (the r19smooth.py baseline re-check, run for BOTH arms on the same states):
 - stored states unwrapped (2pi label jumps in the arm joints removed), joint-linear between them, cut so that
   point_bound.segment_bound between consecutive states is <= 4 mm (with the ur5e_enc model, whose bound is
   the larger one); every resulting state goes through Checker.check(full=True): MuJoCo contacts + the GJK
   lower-bound certificate (distance.Bounds), 10 mm robot-environment, 5 mm gripper/held-environment, 0 mm
   self (non-adjacent links, as the checker does it), joint ranges;
 - scenes: chains as r19smooth.setup (R18b layout: spatula at (-1.15, .30), flipped; the plate-2 chain with a
   dish waiting at x .43 as r17chain PLATE2=.43); stir as r19stir_save.py SCENE=r17 (jaw sign of its passing
   attempt) plus its plume rule (r15 plume cylinder, distance of the arm geoms, must be >= 0); hub edges in
   r19hub.py's union scene;
 - the R11 mesh rule for the tool-side boxes (r19smooth.py MESHHELD) in every scene (both arms alike);
 - every hit pair is re-measured with the exact convex bound and classed real / artefact / unproven (see one()).
Loads, cart stability and joint limits do not depend on the collision geoms (same masses and kinematics)."""
import sys,os,json,time,math,glob
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
NEW=KV.get('NEW','ur5e_enc')   # the enclosing arm option compared with ur5e (ur5e_enc, or ur5e_enc2 -> results/r19/enc2)
OUT='results/r19/'+NEW[len('ur5e_'):]
CHAINS={'wok':('results/r17/chain_wok_s-1_final.json',False),'wok_plate2b':('results/r17/chain_wok_s-1_r18plate2b.json',True),
 'lever':('results/r17/chain_lever_s+1_final.json',False),'lid':('results/r17/chain_lid_s-1_final.json',False),
 'spider':('results/r17/chain_spider_s+1_final.json',False),'spatula':('results/r17/chain_spatula_s-1_r18roll-1.15_.30.json',False)}
STIR='results/r19/stir/stirwalk2_h_scrape_dice_r17.json'
ARMS_=('ur5e',NEW)
def meshheld(tree):
 """r19smooth.py MESHHELD: tool-side boxes -> identical 8-vertex box meshes (geometry unchanged)."""
 import xml.etree.ElementTree as E
 from scene import fmt
 asset=tree.getroot().find('asset');tool=tree.find(".//body[@name='R_tool']")
 for g in tool.iter('geom'):
  if g.get('type')!='box':continue
  h=np.fromstring(g.get('size'),sep=' ');mn='mb19_'+g.get('name')
  E.SubElement(asset,'mesh',name=mn,vertex=' '.join(fmt([sx*h[0],sy*h[1],sz*h[2]]) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)))
  g.set('type','mesh');g.set('mesh',mn);g.attrib.pop('size',None)
_CTX={}
def ctx(key,arm):
 """Scene + checker of a path set for one arm (cached per process)."""
 if (key,arm) in _CTX:return _CTX[(key,arm)]
 os.environ['ARM']=arm   # arms.current() reads it at build / checker time
 import chain,mujoco,arms
 from scene import build
 from checker import Checker
 import kitchen15 as K15,kitchen16 as K,kitchen17 as K17
 assert arms.current()==arm
 c=dict(arm=arm,plume=None)
 if key in CHAINS:   # r19smooth.setup, plus the plate-2 dish for the plate-2 chain
  K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.)
  f,plate2=CHAINS[key];f=f[:-5]+KV.get('SUFFIX','')+'.json';r=json.load(open(f))
  if r.get('wok_tilt'):K17.set_wok_tilt(r['wok_tilt'])
  for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
  K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.
  BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
  ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if plate2 else {}
  cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])})
  tree,meta=build(cfg,None);meshheld(tree);c['ch']=Checker(tree,meta)
 elif key=='stir':   # r19stir_save.py model(sign) with SCENE=r17
  import xml.etree.ElementTree as E
  from scene import fmt
  r=json.load(open(STIR));sign=[a for a in r['attempts'] if a['ok']][0]['jaw_sign'];GRIP=r['grip_m']
  K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spider']=(1.52,.36)
  SCN=dict(r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None,'spatula':None})
  cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r15_spatula=GRIP,r15_spatula_jaw=sign,**SCN);tree,meta=build(cfg,None);meshheld(tree);c['ch']=Checker(tree,meta)
  E.SubElement(tree.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K15.WOK0[0],K15.WOK0[1],(K15.RIM_Z+1.25)/2]),size=fmt([.20,(1.25-K15.RIM_Z)/2]),contype='0',conaffinity='0')
  pm=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));pd=mujoco.MjData(pm);pl=pm.geom('r15_plume').id
  rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(('R_gripper_spatula','R_cart','R_dock'))]
  def plume(q):
   pd.qpos[:]=q;mujoco.mj_forward(pm,pd);ft=np.zeros(6);best=(1e9,None)
   for g in rob:
    v=1000*mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft)
    if v<best[0]:best=(v,pm.geom(g).name)
   return best
  c['plume']=plume;c['sign']=sign
 elif key=='hub':   # r19hub.py union scene (lever closed + open, lid on the pot + in the rack, dishes at both plating spots)
  import r19hub
  tree,meta=r19hub.union_tree();meshheld(tree);c['ch']=Checker(tree,meta)
 else:raise KeyError(key)
 _CTX[(key,arm)]=c;return c
def states(key):
 """{path name: stored states (unwrapped)} of a set."""
 from r19smooth import unwrap
 if key in CHAINS:
  r=json.load(open(CHAINS[key][0][:-5]+KV.get('SUFFIX','')+'.json'))
  if not r.get('ok') or not r.get('play'):return {}   # a failed (re-)plan has no path to check
  return {key:unwrap(r['play'])}
 if key=='stir':return {'stir':np.array(json.load(open(STIR))['states']['q'],float)}
 E_=[e for e in KV.get('EDGES','').split(',') if e] or sorted(f[len('results/r19/hub/edge_'):-5] for f in glob.glob('results/r19/hub/edge_*.json'))
 return {e:unwrap(json.load(open(f'results/r19/hub/edge_{e}.json'))['qs']) for e in E_}
def sample(ch,Q):
 """r19smooth.sample_poly: joint-linear between stored states, <= 4 mm point bound per step."""
 import r19smooth as S
 return S.sample_poly(Q,S.FastBound(ch))
def one(c,q):
 """Checker.check(full=True) of one state; every hit pair is re-measured with the exact convex bound
 (distance.Bounds.pair: GJK lower / upper bound on the true distance of the two primitives) and classed
   real      the upper bound is below the required gap, or the two intersect (upper ~ 0; self needs 0 mm)
   artefact  the lower bound clears the required gap: only MuJoCo's contact distance was short
             (its cylinder distances are 0.68-1.0x the true gap, R19_ARM_SWAP.md 7)
   unproven  neither (the bound could not decide)."""
 ch=c['ch'];r=ch.check(np.asarray(q),full=True,mass=0.)
 cl={k:(round(v['reserve_mm'],3),v['pair']) for k,v in r['clearance'].items()}
 hp={}
 for h in r['hits']:
  key=' | '.join(sorted(h['pair']))
  if key in hp:continue
  a_,b_=[ch.gnames.index(n) for n in h['pair']];need=float(h['required_gap_mm'])/1e3;v=ch.bounds.pair(a_,b_)
  k='real' if v['upper_m']<need-1e-6 or v['upper_m']<=1e-7 else 'artefact' if v['lower_m']>=need-1e-6 else 'unproven'
  hp[key]=[k,round(v['lower_m']*1e3,3),round(v['upper_m']*1e3,3),need*1e3,round(float(h['real_gap_mm']),3)]
 out=dict(cl=cl,hits=hp,ranges=bool(r['ranges']))
 if c['plume']:v,gn=c['plume'](q);out['plume']=[round(v,2),gn]
 return out
def _work(a):
 key,arm,Q=a;c=ctx(key,arm);return [one(c,q) for q in Q]
def recheck():
 import multiprocessing as mp
 key=KV['SET'];WK=int(KV.get('WORKERS',24));t0=time.monotonic();os.makedirs(OUT,exist_ok=True)
 lane=KV.get('LANE');fn=f"{OUT}/{key}{KV.get('SUFFIX','')}{'_'+lane if lane else ''}.json"
 P=states(key)
 if not P:
  json.dump(dict(set=key+KV.get('SUFFIX',''),skipped='chain not ok or no play states: nothing to re-check',paths={}),open(fn,'w'));print(key,'skipped: chain not ok / empty play ->',fn);return
 enc=ctx(key,NEW);jobs=[];meta={}
 for name,Q in P.items():
  QS,src,sp=sample(enc['ch'],Q);meta[name]=dict(stored_states=len(Q),states=len(QS),max_step_bound_mm=round(sp*1e3,3),src=src.tolist())
  for arm in ARMS_:
   for i in range(0,len(QS),40):jobs.append((name,arm,i,QS[i:i+40]))
 print(key,{n:(v['stored_states'],v['states'],v['max_step_bound_mm']) for n,v in meta.items()},'checks',sum(len(j[3]) for j in jobs),flush=True)
 pool=mp.Pool(WK);res=pool.map(_work,[(key,arm,Q) for name,arm,i,Q in jobs],chunksize=1);pool.close()
 per={n:{a:[] for a in ARMS_} for n in P}
 for (name,arm,i,Q),r in zip(jobs,res):per[name][arm]+=r
 out=dict(set=key+KV.get('SUFFIX',''),method=__doc__,paths={})
 for name in P:
  out['paths'][name]=dict(**{k:v for k,v in meta[name].items() if k!='src'},**{arm:summarize(per[name][arm],meta[name]['src']) for arm in ARMS_},
   per_state={arm:[dict(env=min([v[0] for k,v in s['cl'].items() if k!='self'],default=None),self=s['cl'].get('self',[None])[0],hits=s['hits'],**({'plume':s['plume'][0]} if 'plume' in s else {})) for s in per[name][arm]] for arm in ARMS_})
  print(name,json.dumps({arm:{k:v for k,v in out['paths'][name][arm].items() if k not in ('hit_runs',)} for arm in ARMS_}),flush=True)
 out['elapsed_s']=round(time.monotonic()-t0);json.dump(out,open(fn,'w'),default=float);print('saved',fn,out['elapsed_s'],'s')
def summarize(rs,src):
 hit=[i for i,r in enumerate(rs) if r['hits'] or not r['ranges']]
 pairs={}
 for r in rs:
  for p,(k,lo,up,need,mj) in r['hits'].items():
   o=pairs.setdefault(p,dict(states=0,kinds={},min_gap_lower_mm=1e9,min_gap_upper_mm=1e9,required_mm=need));o['states']+=1;o['kinds'][k]=o['kinds'].get(k,0)+1
   o['min_gap_lower_mm']=min(o['min_gap_lower_mm'],lo);o['min_gap_upper_mm']=min(o['min_gap_upper_mm'],up)
 env=[(v[0],k,v[1]) for r in rs for k,v in r['cl'].items() if k!='self']
 se=[(r['cl']['self'][0],r['cl']['self'][1]) for r in rs if 'self' in r['cl']]
 e=min(env,key=lambda x:x[0]) if env else None;s=min(se,key=lambda x:x[0]) if se else None
 # contiguous runs of hit states, with the stored-state index range
 runs=[];
 for i in hit:
  if runs and i==runs[-1][1]+1:runs[-1][1]=i
  else:runs.append([i,i])
 d=dict(ok=not hit,hit_states=len(hit),real_hit_states=sum(1 for r in rs if any(v[0]=='real' for v in r['hits'].values())),
  artefact_only_hit_states=sum(1 for r in rs if r['hits'] and all(v[0]=='artefact' for v in r['hits'].values())),out_of_range_states=sum(1 for r in rs if not r['ranges']),
  hit_pairs=dict(sorted(pairs.items(),key=lambda kv:-kv[1]['states'])),
  min_env_reserve_mm=None if e is None else round(e[0],2),min_env_category=None if e is None else e[1],min_env_pair=None if e is None else e[2],
  min_self_reserve_mm=None if s is None else round(s[0],2),min_self_pair=None if s is None else s[1],
  min_reserve_by_category={k:dict(mm=round(v[0],2),pair=v[2]) for k,v in sorted({c_:min((x for x in env+[(y[0],'self',y[1]) for y in se] if x[1]==c_),key=lambda x:x[0]) for c_ in set(x[1] for x in env)|({'self'} if se else set())}.items())},
  hit_runs=[dict(states=[a,b],stored=[round(float(src[a]),2),round(float(src[b]),2)]) for a,b in runs][:40])
 if rs and 'plume' in rs[0]:pm=min(rs,key=lambda r:r['plume'][0])['plume'];d.update(min_plume_mm=pm[0],min_plume_geom=pm[1],plume_violations=sum(1 for r in rs if r['plume'][0]<0))
 return d
# ------------------------------------------------------------------ enclosure in the sim model
def enclose():
 """r19ur5e_enclose.py's measurement, but on the SIM model as scene.build makes it (models/base.xml + arms.swap):
 the Menagerie visual meshes placed in the sim's R_arm_* bodies (same frames, asserted), max protrusion of any
 vertex outside the union of all the arm's capsule / cylinder geoms, over random arm configurations."""
 import mujoco,xml.etree.ElementTree as E,arms
 from scipy.spatial.transform import Rotation
 from scene import H
 MEN=str(H.parents[1]/'r01/concept/sources/menagerie/universal_robots_ur5e');mm=mujoco.MjModel.from_xml_path(MEN+'/ur5e.xml');md=mujoco.MjData(mm)
 N=int(KV.get('N',200));out={}
 for arm in ARMS_:
  tree=E.parse(H/'models/base.xml')
  if arm!='ur5e':arms.swap(tree,arm)
  m=mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m)
  B={b:m.body('R_arm_'+mujoco.mj_id2name(mm,mujoco.mjtObj.mjOBJ_BODY,b)).id for b in range(1,mm.nbody)}
  for b,sb in B.items():assert np.allclose(mm.body_pos[b],m.body_pos[sb]) and np.allclose(mm.body_quat[b],m.body_quat[sb]),b
  col=[g for g in range(m.ngeom) if (m.geom(g).name or '').startswith('R_geom_') and m.geom_type[g] in (mujoco.mjtGeom.mjGEOM_CAPSULE,mujoco.mjtGeom.mjGEOM_CYLINDER)]
  vis=[g for g in range(mm.ngeom) if mm.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH and mm.geom_bodyid[g]>1]
  arm_q=[m.jnt_qposadr[m.joint(n).id] for n in arms.JOINTS]
  def sdf(P,g):
   R=d.geom_xmat[g].reshape(3,3);L=(P-d.geom_xpos[g])@R;r,h=m.geom_size[g][:2]
   if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_CAPSULE:z=np.clip(L[:,2],-h,h);return np.linalg.norm(L-np.c_[0*z,0*z,z],axis=1)-r
   rad=np.linalg.norm(L[:,:2],axis=1)-r;ax=np.abs(L[:,2])-h
   return np.where((rad>0)&(ax>0),np.hypot(rad,ax),np.maximum(rad,ax))
  rng=np.random.default_rng(0);worst={}
  for k in range(N):
   d.qpos[:]=0
   if k:d.qpos[arm_q]=rng.uniform(-np.pi,np.pi,6)
   mujoco.mj_kinematics(m,d)
   for g in vis:
    sb=B[mm.geom_bodyid[g]];a,n=mm.mesh_vertadr[mm.geom_dataid[g]],mm.mesh_vertnum[mm.geom_dataid[g]];V=mm.mesh_vert[a:a+n]
    Rgeom=Rotation.from_quat(np.r_[mm.geom_quat[g][1:],mm.geom_quat[g][0]]).as_matrix();Xb=d.xmat[sb].reshape(3,3)
    P=d.xpos[sb]+Xb@mm.geom_pos[g]+V@(Xb@Rgeom).T
    s=np.min([sdf(P,c) for c in col],axis=0);nm=m.body(sb).name
    worst[nm]=max(worst.get(nm,-1),float(s.max()))
  out[arm]=dict(configs=N,collision_geoms=[m.geom(g).name for g in col],max_protrusion_mm={k:round(v*1e3,2) for k,v in worst.items()})
  print(arm,out[arm]['max_protrusion_mm'],flush=True)
 os.makedirs(OUT,exist_ok=True);json.dump(dict(method=enclose.__doc__,**out),open(f'{OUT}/enclose.json','w'),indent=1)
# ------------------------------------------------------------------ random-pose self-collision
def selfrate():
 """Share of random arm poses (joints uniform in [-pi, pi], elbow in its range) in which two arm parts of
 non-adjacent bodies (arm geoms, base mesh, gripper, as the checker's self rule) overlap (MuJoCo contact
 distance < 0); per pair too. Sim model, tool as built for the lid chain scene (empty-hand gripper)."""
 import mujoco,arms
 N=int(KV.get('N',2000));out={}
 for arm in ARMS_:
  c=ctx('lid',arm);ch=c['ch'];m,d=ch.m,ch.d
  arm_q=[ch.qa[n] for n in arms.JOINTS];lo=m.jnt_range[[m.joint(n).id for n in arms.JOINTS],0]
  rng=np.random.default_rng(0);n_hit=0;pairs={}
  for k in range(N):
   q=m.qpos0.copy();q[arm_q]=np.clip(rng.uniform(-np.pi,np.pi,6),m.jnt_range[[m.joint(n).id for n in arms.JOINTS],0],m.jnt_range[[m.joint(n).id for n in arms.JOINTS],1])
   d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_collision(m,d);hit=set()
   for cc in d.contact[:d.ncon]:
    a,b=int(cc.geom[0]),int(cc.geom[1])
    if not(ch.robot[a] and ch.robot[b]) or cc.dist>=0:continue
    req=ch.required(ch,a,b)
    if req is None or req[1]!='self':continue
    hit.add(' | '.join(sorted([ch.gnames[a],ch.gnames[b]])))
   n_hit+=bool(hit)
   for p in hit:pairs[p]=pairs.get(p,0)+1
  out[arm]=dict(poses=N,poses_with_self_contact=n_hit,share=round(n_hit/N,3),pairs=dict(sorted(pairs.items(),key=lambda kv:-kv[1])))
  print(arm,out[arm]['share'],list(out[arm]['pairs'].items())[:8],flush=True)
 os.makedirs(OUT,exist_ok=True);json.dump(dict(method=selfrate.__doc__,**out),open(f'{OUT}/self_random.json','w'),indent=1)
COVER_MM=1.7   # grid(step 2 mm): every surface point lies within (2*sqrt(2))/sqrt(3) = 1.63 mm of a sample
def meshgap():
 """Diagnosis of the ur5e_enc hits: at the state where the hit pair's exact lower bound is smallest, the
 distance from the Menagerie visual mesh (every vertex + a <= 2 mm grid on every triangle, r19ur5e_encfit.grid;
 the true surface lies within 1.7 mm of these points) of the link(s) the arm primitive covers to the other
 geom (box / cylinder / box-shaped mesh, exact point distance), minimum over EVERY hit state of the pair.
 real_arm: 'violates' (sampled gap < required: the true gap is smaller still), 'clear' (sampled gap - 1.7 mm
 >= required), else 'undecided'. Tells which link and how close the real arm (the Menagerie mesh) comes."""
 import mujoco,r19ur5e_encfit as F
 from scipy.spatial.transform import Rotation
 _,_,tris,_,_,_=F.load();P={'R_arm_'+L:F.grid(T,.002) for L,T in tris.items() if L in F.NAMES}
 import arms;J=json.load(open(arms.ARMS[NEW]['enclose']));cover={}
 for link,ps in J['candidates'].items():
  for p_ in ps:cover.setdefault(p_,[]).append(link)
 def dist(m,d,g,X):
  R=d.geom_xmat[g].reshape(3,3);L=(X-d.geom_xpos[g])@R;t=m.geom_type[g]
  if t==mujoco.mjtGeom.mjGEOM_MESH:
   a,n=m.mesh_vertadr[m.geom_dataid[g]],m.mesh_vertnum[m.geom_dataid[g]];V=m.mesh_vert[a:a+n];assert n==8,'only box-shaped meshes'
   c=(V.max(0)+V.min(0))/2;h=(V.max(0)-V.min(0))/2;L=L-c;t=mujoco.mjtGeom.mjGEOM_BOX;sz=h
  else:sz=m.geom_size[g]
  if t==mujoco.mjtGeom.mjGEOM_BOX:q=np.abs(L)-sz;return np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(q.max(1),0)
  if t==mujoco.mjtGeom.mjGEOM_CYLINDER:rad=np.linalg.norm(L[:,:2],axis=1)-sz[0];ax=np.abs(L[:,2])-sz[1];return np.where((rad>0)&(ax>0),np.hypot(rad,ax),np.maximum(rad,ax))
  raise ValueError(t)
 out=[]
 for f in sorted(glob.glob(f'{OUT}/*.json')):
  if os.path.basename(f) in ('summary.json','enclose.json','self_random.json','meshgap.json'):continue
  r=json.load(open(f));key=r['set'];sfx=''
  if r.get('skipped'):continue
  for a_ in ('_ur5e_enc2','_ur5e_enc'):
   if key.endswith(a_) and key[:-len(a_)] in CHAINS:key,sfx=key[:-len(a_)],a_;break
  KV['SUFFIX']=sfx
  for name,v in r['paths'].items():
   if not v[NEW]['hit_pairs']:continue
   KV['EDGES']=name;c=ctx('hub' if key.startswith('hub') else key,NEW);ch=c['ch'];m,d=ch.m,ch.d
   Q=list(states('hub' if key.startswith('hub') else key).values())[0];QS,src,sp=sample(ch,Q);ps=v['per_state'][NEW]
   for pair in v[NEW]['hit_pairs']:
    js=[j for j,s_ in enumerate(ps) if pair in s_['hits']];i=min(js,key=lambda j:ps[j]['hits'][pair][1]);a_,b_=pair.split(' | ')
    arm_g,other=(a_,b_) if a_.startswith('R_geom') else (b_,a_);g=m.geom(other).id
    best=(1e9,None,None)
    for j in js:   # every hit state of this pair
     d.qpos[:]=QS[j];mujoco.mj_kinematics(m,d)
     for link in cover.get(arm_g,[]):
      b=m.body(link).id;X=d.xpos[b]+P[link]@d.xmat[b].reshape(3,3).T;dd=float(dist(m,d,g,X).min())
      if dd<best[0]:best=(dd,link,j)
    hp=ps[i]['hits'][pair];need=hp[3];rg=best[0]*1e3
    out.append(dict(set=r['set'],path=name,pair=pair,hit_states=len(js),arm=NEW,stored_range=[round(float(src[min(js)]),2),round(float(src[max(js)]),2)],
     enc_min_gap_lower_mm=hp[1],enc_worst_state=i,required_mm=need,real_mesh_min_gap_mm=round(rg,1),real_mesh_state=best[2],real_mesh_stored_index=round(float(src[best[2]]),2),real_mesh_link=best[1],covered_links=cover.get(arm_g,[]),
     real_arm='violates' if rg<need else 'clear' if rg-COVER_MM>=need else 'undecided'))
    print(json.dumps(out[-1]),flush=True)
 json.dump(dict(method=meshgap.__doc__,rows=out),open(f'{OUT}/meshgap.json','w'),indent=1)
def summary():
 rows=[]
 for f in sorted(glob.glob(f'{OUT}/*.json')):
  if os.path.basename(f) in ('summary.json','enclose.json','self_random.json','meshgap.json'):continue
  r=json.load(open(f))
  if r.get('skipped'):rows.append(dict(set=r['set'],skipped=r['skipped']));continue
  for name,v in r['paths'].items():
   rows.append(dict(set=r['set'],path=name,states=v['states'],stored_states=v['stored_states'],max_step_bound_mm=v['max_step_bound_mm'],
    **{f'{a}_{k}':v[a].get(k) for a in ARMS_ for k in ('ok','hit_states','real_hit_states','artefact_only_hit_states','min_env_reserve_mm','min_env_pair','min_self_reserve_mm','min_self_pair','min_reserve_by_category','min_plume_mm','plume_violations')},
    enc_hit_pairs=v[NEW]['hit_pairs'],enc_hit_runs=v[NEW]['hit_runs']))
 json.dump(rows,open(f'{OUT}/summary.json','w'),indent=1)
 for r in rows:
  if r.get('skipped'):print(f"{r['set']:12s} skipped: {r['skipped']}");continue
  n=NEW;print(f"{r['set']:12s} {r['path']:16s} {r['states']:5d}  ur5e ok={r['ur5e_ok']!s:5s} hits={r['ur5e_hit_states']:4d} env {r['ur5e_min_env_reserve_mm']} self {r['ur5e_min_self_reserve_mm']} | {n} ok={r[n+'_ok']!s:5s} hits={r[n+'_hit_states']:4d} (real {r[n+'_real_hit_states']}, artefact-only {r[n+'_artefact_only_hit_states']}) env {r[n+'_min_env_reserve_mm']} self {r[n+'_min_self_reserve_mm']} pairs {list(r['enc_hit_pairs'])[:3]}")
if __name__=='__main__':
 {'recheck':recheck,'enclose':enclose,'self':selfrate,'summary':summary,'meshgap':meshgap}[sys.argv[1]]()
