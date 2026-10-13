"""Re-check a stored R19 prep set (results/r19/prep/chain_*.json from r19prepchain.py) at <= 4 mm.
New file. r19prepchain.py (like r17chain.py) follows the object every <= 1 cm / 2 deg and runs the full
bound only every 5th step; R19 found that this does not meet the <= 4 mm state rule (README R19). Here the
stored playback is taken as the executed path, joint-linear between stored states, and subdivided so that
no robot or held point moves more than 4 mm between consecutive states (point_bound.segment_bound, the
planner.edge rule, as r19smooth.sample_poly). EVERY state gets the FULL unchanged check (MuJoCo contacts +
the GJK lower-bound certificate, 10 mm robot-environment, 5 mm gripper/held-environment, joint ranges).
Scenes, as r19prepchain.py checked them:
 - play (grasp ... release): the object held (r16_held), the set's union scene;
 - each grasp approach / release retreat (approach_qs): the empty gripper, jaws open, the object in the
   world where it lies (or gone, e.g. dropped into the slicer); for food the contact window of the rules:
   finger / gripper geoms may be closer than 5 mm to that food item inside this <= 50 mm straight line,
   never touching it (distance.py upper bound > 0).
The 8 mm seat lift / set-down between an approach end and play[0] / play[-1] is the support contact
window of the grasp (<= 50 mm along the support normal) and is not a checked held state (as r17chain.py).
python r19prep_verify.py FILE=results/r19/prep/chain_<..>.json [NPROC=16]   (the arm is the one recorded in FILE)
 -> <FILE>_verify4mm.json"""
import sys,os,json,math,time
sys.path.insert(0,'.')
import numpy as np,mujoco
KV=dict(a.split('=',1) for a in sys.argv[1:]);FN=KV['FILE'];STEP=.004
_C={}
def setup(R):
 os.environ['ARM']=R.get('arm','ur5e')   # the arm the set was planned with (arms.current: ARM=.. on the command line wins)
 import chain
 from scene import build
 from checker import Checker
 import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19 as K19
 import kitchen19p3   # R19 #38: registers the step-3 objects (basket, tub, bowl, catch tray)
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
 L=R['layout'];K19.LAYOUT.update({k:(tuple(v) if isinstance(v,list) and k!='drop_bowls' else v) for k,v in L.items()})
 BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools={'ladle':None},r14_fridge=True,r17_lever=0.,**K19.base_cfg())
 def model(extra,world_obj=None):
  cfg=chain.chain_cfg('SD',**{**BASE,**R['scene'],**extra})
  if world_obj is not None:cfg['r19']=dict(cfg['r19'],objs=list(cfg['r19'].get('objs',[]))+[world_obj])
  tree,meta=build(cfg,None);K19.add(tree,cfg)
  Rl,p=K17.lever_pose(K17.LEVER_OPEN);K._add(tree.find('worldbody'),'u_open_',K.OBJ['lever']['parts'],Rl,p,rgba='.75 .77 .8 1')
  return Checker(tree,meta)
 if R['obj'].startswith('pusher_y'):K19.pusher_turned(float(R['obj'][8:]))   # the turned knob adapter object (round 2)
 return model,K17,K19
def scene_for(R,key):
 """Checker for 'play' or ('app', i)."""
 if key in _C:return _C[key]
 model,K17,K19=setup(R)
 if key=='play':c=model(K17.held_cfg(R['obj'],R['grasp_sense']));win=None
 else:
  i=key[1];g=R['grasps'][i];kf=R['keyframes'][g['kf']];Rk=np.array(kf['R']);p=np.array(kf['p'])
  seat=kf.get('seat',.008 if R['obj'] in ('carrot','tomato') else 0.)   # food grasped / set down 8 mm above its support (r19prepchain kf seat)
  wo=[R['obj'],Rk.tolist(),(p-[0,0,seat]).tolist()] if g['object_in_world'] else None
  c=model(dict(r19=g['world']),wo);win=None
  if g['object_in_world'] and R['obj'] in ('carrot','tomato'):
   og=[k for k in range(c.m.ngeom) if c.m.geom(k).name==f"r19_{R['obj']}"];fg=[k for k in range(c.m.ngeom) if c.m.geom(k).name.startswith(('R_finger_','R_gripper_'))]
   win=(og,fg,{frozenset([c.m.geom(a).name,c.m.geom(b).name]) for a in og for b in fg})
   perm=c.permissions;c.permissions=lambda kind,perm=perm,w=win[2]:set(perm(kind))|w
 _C[key]=(c,win);return _C[key]
def unwrap(c,Q):
 """Same poses, continuous joint labels: each +-2pi joint takes the equivalent angle nearest the previous
 state that stays in its range (the stored playbacks of r17chain-style joins jump by exactly 2pi, R19)."""
 Q=np.array(Q,float);ids=c.arm_ids;lo=c.m.jnt_range[[c.m.jnt_qposadr.tolist().index(i) for i in ids],0];hi=c.m.jnt_range[[c.m.jnt_qposadr.tolist().index(i) for i in ids],1];n=0
 for i in range(1,len(Q)):
  for k,j in enumerate(ids):
   opts=[Q[i,j]+2*np.pi*m for m in (-2,-1,0,1,2) if lo[k]-1e-9<=Q[i,j]+2*np.pi*m<=hi[k]+1e-9];v=min(opts,key=lambda x:abs(x-Q[i-1,j]))
   if abs(v-Q[i,j])>1e-9:n+=1
   Q[i,j]=v
 return Q,n
def densify(c,Q):
 out=[Q[0]];sp=0.
 for a,b in zip(Q[:-1],Q[1:]):
  bd=c.point_bound.segment_bound(a,b);n=max(1,int(math.ceil(bd/STEP)));sp=max(sp,bd/n)
  for k in range(1,n+1):out.append(a+(b-a)*k/n)
 return np.array(out),sp
def work(args):
 key,Qs=args;R=json.load(open(FN));c,win=scene_for(R,tuple(key) if isinstance(key,list) else key);res=[]
 for q in Qs:
  q=np.asarray(q);r=c.check(q,full=True,mass=0.);rv={k:v['reserve_mm'] for k,v in r['clearance'].items()};touch=False
  if win:
   c.d.qpos[:]=q;mujoco.mj_kinematics(c.m,c.d);touch=min(c.bounds.pair(a,b)['upper_m'] for a in win[0] for b in win[1])<=1e-6
  res.append(dict(hits=[h['pair'] for h in r['hits']][:2],ranges=bool(r['ranges']),touch=touch,res=min([v for k,v in rv.items() if k!='self'],default=1e9),self_mm=rv.get('self',1e9)))
 return res
if __name__=='__main__':
 import multiprocessing as mp
 R=json.load(open(FN));t0=time.monotonic();NP=int(KV.get('NPROC',16))
 if not R.get('ok') or not R.get('play'):   # a failed or empty chain has nothing to re-check: record that and stop
  out=dict(file=FN,skipped=f"chain ok={R.get('ok')}, {len(R.get('play') or [])} play states: nothing to re-check",ok=False)
  json.dump(out,open(FN.replace('.json','_verify4mm.json'),'w'),indent=1);print(json.dumps(out));sys.exit(0)
 # seat heights of the grasp keyframes (r19prepchain: seat .008 at the pick / set-down keyframes of food; 0 for the pusher)
 jobs=[];meta=[]
 c,_=scene_for(R,'play');P,nwrap=unwrap(c,R['play']);QP,spP=densify(c,P);meta.append(('play',len(P),len(QP),spP))
 for i in range(0,len(QP),40):jobs.append(('play',QP[i:i+40].tolist()))
 for i,aq in enumerate(R.get('approach_qs') or []):
  if not aq:continue
  ca,_=scene_for(R,('app',i));QA,spA=densify(ca,np.array(aq));meta.append((f'approach {i} (kf {R["grasps"][i]["kf"]})',len(aq),len(QA),spA))
  for k in range(0,len(QA),40):jobs.append((['app',i],QA[k:k+40].tolist()))
 with mp.Pool(NP) as pool:outs=pool.map(work,jobs)
 rows={};
 for (key,_),o in zip(jobs,outs):rows.setdefault(str(key),[]).extend(o)
 summ={}
 for key,rs in rows.items():
  bad=[i for i,r in enumerate(rs) if r['hits'] or not r['ranges'] or r['touch']]
  summ[key]=dict(states=len(rs),hit_states=len(bad),first_hits=[(i,rs[i]['hits'],rs[i]['touch']) for i in bad[:4]],min_reserve_mm=round(min(r['res'] for r in rs),2),min_self_mm=round(min(r['self_mm'] for r in rs),2),ranges_ok=all(r['ranges'] for r in rs))
 out=dict(file=FN,rule='every state fully checked; consecutive states <= 4 mm apart (point bound); joint-linear between the stored states (2pi-unwrapped)',unwrapped_joint_labels=nwrap,
  segments=[dict(name=n,stored=a,checked=b,max_spacing_mm=round(s*1e3,3)) for n,a,b,s in meta],summary=summ,
  ok=all(v['hit_states']==0 and v['ranges_ok'] for v in summ.values()),elapsed_s=round(time.monotonic()-t0,1))
 json.dump(out,open(FN.replace('.json','_verify4mm.json'),'w'),indent=1)
 print(json.dumps({k:v for k,v in out.items()},default=str))
