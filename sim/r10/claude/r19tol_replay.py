"""R19 tolerance (#13), measured in the sim: the error each stored path tolerates before any hit.

python r19tol_replay.py SET=actions|approaches|edges|all [PARTS=cart,fix,grasp] [EDGES=0:11]
       | SCENES=play:wok,app:lid:1,edge:WOK__H_WOK,...   [WORKERS=16] [SCEN=1] [ARM=<id>]
 -> results/r19/tol<arm tag>/scene_<key>__<part>.json
Scenes: play = an action's stored play (2pi-unwrapped, joint-linear, densified to <= 4 mm point bound as
r19smooth.py), app = one grasp approach / release retreat (empty gripper, object in the world, r17chain.py
approach()), edge = one R19 hub edge (stored states, union scene). The R18b layout throughout.
Parts (each a task in a fresh worker process):
  cart   nominal exact minimum (+ comparison with the checker-reported reserve), the 12 cart directions
         (x, y, z, yaw about J1, tilt_x, tilt_y; both signs), the grid (+-1/2/5/10 mm, yaw +-0.1/0.2/0.5/1 deg,
         tilts +-0.1/0.2/0.5 deg; min gate / contact over all states, reported up to 20 mm), the checker
         cross-check (Checker.check(full=True) with the error applied through the cart joints, just below
         and just above the x / y / yaw tolerance), SCEN=1: worst corner of each cart budget scenario;
  fix    every fixture group whose pairs come within 30 mm of the gate somewhere on the path: x / y / z, both signs;
  grasp  the held part in the tool frame: x / y / z and a turn about the jaw axis, both signs.
Tolerance = the largest perturbation with no state below the gate (planning gaps 10 / 5 mm) -- 'gate' -- and
with no state in contact (distance < 0.01 mm) -- 'contact'; exponential search (0.5 mm / 0.05 deg doubling,
up to 20 mm / 2 deg) then bisection (0.05 mm / 0.005 deg) on a subset of states, verified on all states;
the binding state (segment label) and pair at the first violation."""
import sys,os,json,time,math
sys.path.insert(0,'.')
import numpy as np
import r19tol_core as C
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
ACTS=['wok','spatula','lever','lid','spider']
def scene_list():
 if 'SCENES' in KV:return KV['SCENES'].split(',')
 S=KV.get('SET','actions');out=[]
 if S in ('actions','all'):out+=[f'play:{a}' for a in ACTS]
 if S in ('approaches','actions','all'):
  for a in ACTS:
   r=C.J(C.tagged(C.CHAINS[a]['file']))
   out+=[f'app:{a}:{k}' for k,q in enumerate(r['approach_qs']) if q]
 if S in ('edges','all'):
  import glob
  d=C.HUBDIR+C.TAG if C.TAG and os.path.isdir(C.HUBDIR+C.TAG) else C.HUBDIR
  E=['edge:'+os.path.basename(f)[5:-5] for f in sorted(glob.glob(f'{d}/edge_*.json')) if C.J(f).get('ok')]
  a,b=map(int,KV.get('EDGES',f'0:{len(E)}').split(':'));out+=E[a:b]
 return out
TR=dict(s0=.5*C.MM,smax=15*C.MM,res=.05*C.MM,unit=C.MM,u='mm')
AN=dict(s0=.05*C.DEG,smax=1.5*C.DEG,res=.005*C.DEG,unit=C.DEG,u='deg')
GRID_TR=[1,2,5,10];GRID_YAW=[.1,.2,.5,1.];GRID_TILT=[.1,.2,.5];GRID_CAP=10.   # mm: grid minima above this are reported as '>= 10' (the tolerance search covers larger values)
# cart budget scenarios for SCEN=1 (half-ranges: m, m, m, rad, rad, rad); R19_TOLERANCE.md section 1 gives the sources
SCENARIOS={   # cart pose half-ranges [x m, y m, z m, yaw rad, tilt_x rad, tilt_y rad]; derivation in R19_TOLERANCE.md section 1
 'R09_requirement':[2*C.MM,2*C.MM,1*C.MM,.2*C.DEG,0.,0.],                     # posts/r09/integrator.md: +-2 mm XY, +-0.2 deg yaw, +-1 mm height (a requirement, no tilt given)
 'as_designed':[6*C.MM,1.5*C.MM,1*C.MM,.3*C.DEG,.3*C.DEG,.15*C.DEG],           # estimated: bumper fixes y only, x from encoders, floor + load tilt, no calibration
 'dock_stops':[.5*C.MM,.5*C.MM,.5*C.MM,.05*C.DEG,.1*C.DEG,.05*C.DEG],          # estimated: indexed stops / V-block + stiff bumper at each station, calibrated
 'touch_off':[.3*C.MM,.3*C.MM,.3*C.MM,.03*C.DEG,.1*C.DEG,.03*C.DEG]}           # estimated: per-set re-localization; load tilt (posture-dependent) remains
NONE=dict(kind='none')
def states_order(noms,pert,measure,sub=None):
 idx=np.arange(len(noms)) if sub is None else np.asarray(sub)
 key=np.array([C.lower_key(noms[i],pert,measure) for i in idx]);D=np.array([C.disp_bound(noms[i],pert) for i in idx]);kv=np.full(len(noms),np.inf);kv[idx]=key-D
 return kv,idx[np.argsort(kv[idx],kind='stable')]
def feasible(ev,Q,noms,pert,measure,sub=None):
 """True if no state (of sub, default all) goes below the gate (or into contact) under pert; else the first violation."""
 kv,order=states_order(noms,pert,measure,sub);n=0;thr=0. if measure=='gate' else C.CONTACT_EPS
 for i in order:
  if kv[i]>=thr:break
  g,gp,c,cp=ev.value(Q[i],pert,stop=thr,measure=measure,nom=noms[i]);n+=1
  v=g if measure=='gate' else c
  if v<thr*1e3:return False,dict(state=int(i),value_mm=round(v,3),pair=gp if measure=='gate' else cp),n
 return True,None,n
def minimum(ev,Q,noms,pert,measure,init=None):
 """Exact min over states (mm) by branch and bound; with init (mm) only values below init are resolved."""
 kv,order=states_order(noms,pert,measure);best=1e9 if init is None else init;arg=None;n=0
 for i in order:
  if kv[i]*1e3>=best:break
  g,gp,c,cp=ev.value(Q[i],pert,measure=measure,cap=best/1e3 if best<1e8 else None,nom=noms[i]);n+=1
  v=g if measure=='gate' else c
  if v<best:best=v;arg=dict(state=int(i),pair=gp if measure=='gate' else cp)
 return best,arg,n
def _search(ev,Q,noms,mk,st,measure,sub,good=0.,bad=None,bind=None):
 evals=0
 if bad is None:
  s=st['s0']
  while True:
   ok,b,n=feasible(ev,Q,noms,mk(s),measure,sub);evals+=n
   if not ok:bad=s;bind=b;break
   good=s
   if s>=st['smax']-1e-12:break
   s=min(2*s,st['smax'])
 while bad is not None and bad-good>st['res']:
  mid=(good+bad)/2;ok,b,n=feasible(ev,Q,noms,mk(mid),measure,sub);evals+=n
  if ok:good=mid
  else:bad=mid;bind=b
 return good,bad,bind,evals
def tolerance(ev,Q,noms,mk,st,measure):
 """Exponential search + bisection on a subset (every 4th state + the 2 % with the lowest nominal bound),
 then verified on ALL states (bisection repeated on all states if the subset missed the binding state)."""
 n=len(Q);p0=mk(st['s0']);key=np.array([C.lower_key(x,p0,measure) for x in noms])
 sub=np.union1d(np.arange(0,n,4),np.argsort(key)[:max(20,n//50)])
 good,bad,bind,evals=_search(ev,Q,noms,mk,st,measure,sub)
 if good>0:
  ok,b,k=feasible(ev,Q,noms,mk(good),measure);evals+=k
  if not ok:good,bad,bind,e2=_search(ev,Q,noms,mk,st,measure,None,0.,good,b);evals+=e2
 if bad is None:return dict(tol=round(good/st['unit'],3),bounded=False,note=f"no violation up to {good/st['unit']:.3g} {st['u']}",evals=evals)
 return dict(tol=round(good/st['unit'],3),bounded=True,violation_at=round(bad/st['unit'],3),binding=bind,evals=evals)
def label(info,src,i):
 j=int(math.floor(src[i]+1e-9));return info['labels'][min(j,len(info['labels'])-1)]
def directions(ev,Q,noms,info,src,dirs,key,t0):
 out=[]
 for kind,ax,sg,gn,st in dirs:
  mk=lambda s,kind=kind,ax=ax,sg=sg,gn=gn:C.pert_of(kind,ax,sg*s,gn)
  rec=dict(kind=kind,axis=ax,sign=sg,group=gn,unit=st['u'])
  for meas in ('gate','contact'):
   t=tolerance(ev,Q,noms,mk,st,meas)
   if t.get('binding'):b=t['binding'];b['label']=label(info,src,b['state']);b['src_index']=round(float(src[b['state']]),3)
   rec[meas]=t
  out.append(rec)
  print(key,kind,ax,sg,gn,'gate',rec['gate']['tol'],'contact',rec['contact']['tol'],st['u'],(rec['gate'].get('binding') or {}).get('pair'),f'{time.monotonic()-t0:.0f}s',flush=True)
 return out
def load_nominal(key,ch,Q,ev):
 """Per-state nominal records, cached in results/r19/tol*/cache (keyed by the scene, its states and the model)."""
 import pickle,hashlib
 h=hashlib.sha1(np.ascontiguousarray(Q).tobytes()+ch.xml.encode()).hexdigest()[:16]
 d=f'{C.OUT}/cache';os.makedirs(d,exist_ok=True);f=f"{d}/nom_{key.replace(':','_')}_{h}.pkl"
 if os.path.exists(f):
  try:return pickle.load(open(f,'rb')),True
  except Exception:pass
 noms=[ev.nominal(q) for q in Q];tmp=f+f'.{os.getpid()}';pickle.dump(noms,open(tmp,'wb'),protocol=4);os.replace(tmp,f);return noms,False
CART_PARTS={'cartT':('x','y','z'),'cartR':('yaw','tilt_x','tilt_y')}
def run(task):
 try:return _run(task)
 except Exception as e:
  import traceback;print('FAILED',task,traceback.format_exc(),flush=True);return f'FAILED {task}: {e!r}'
def _run(task):
 key,part=task;t0=time.monotonic()
 ch,Q0,info=C.build_scene(key)
 if info['kind']=='edge':Q,src=Q0,np.arange(len(Q0),dtype=float)
 else:Q,src=C.densify(ch,Q0)
 ev=C.Ev(ch);noms,cached=load_nominal(key,ch,Q,ev);tn=time.monotonic()-t0
 out=dict(scene=key,part=part,arm=C.ARM,info={k:v for k,v in info.items() if k!='labels'},states=len(Q),stored_states=len(Q0),nominal_s=round(tn,1),nominal_cached=cached,held=bool(len(ev.hg)))
 if part=='nom':print('nominal',key,len(Q),'states',f'{tn:.0f}s',flush=True);return None
 if part in CART_PARTS or part.startswith('cart-'):
  axes=CART_PARTS[part] if part in CART_PARTS else tuple(part[5:].split('+'))   # cart-x, cart-yaw+tilt_x, ... (one task per axis set)
  dirs=[('cart',ax,sg,None,TR if ax in ('x','y','z') else AN) for ax in axes for sg in (1,-1)]
  out['directions']=directions(ev,Q,noms,info,src,dirs,key,t0)
  out['validation']=validate(ch,ev,Q,out['directions'])
 elif part=='grid' or part.startswith('grid-'):
  g0,ga,_=minimum(ev,Q,noms,NONE,'gate');c0,ca,_=minimum(ev,Q,noms,NONE,'contact')
  if ga is None:g0,ga=C.LIM*1e3,dict(state=0,pair=None)   # no pair within LIM (80 mm) of its gate anywhere: reported as >= LIM
  if ca is None:c0,ca=C.LIM*1e3,dict(state=0,pair=None)
  out['nominal']=dict(min_gate_mm=round(g0,3),gate_state=ga['state'],gate_label=label(info,src,ga['state']),gate_pair=ga['pair'],
   min_contact_mm=round(c0,3),contact_state=ca['state'],contact_label=label(info,src,ca['state']),contact_pair=ca['pair'],at_least=ga['pair'] is None,
   rho_m={k:round(max(n[k] for n in noms),3) for k in ('yaw','tilt_x','tilt_y','held') if k in noms[0]},
   note='exact minimum of the GJK certificate over robot-environment pairs; Checker.check reports an AABB bound for pairs > 2 mm past the gate, so its reserve can be lower')
  if len(ev.hg):
   hg,ha,_=minimum(ev,Q,noms,C.pert_of('grasp','x',0.),'gate');out['nominal'].update(min_held_gate_mm=round(hg,3),held_pair=ha['pair'] if ha else None)
  # the reserve the checker reported for the same path (AABB-bound effect)
  if info['kind']=='play':
   bf=f"results/r19/smooth/{info['act']}_baseline.json"
   if os.path.exists(bf):
    b=C.J(bf);bs=np.array(b['src']);br=np.array([r['res'] for r in b['rb']])
    if len(bs)==len(src) and np.max(abs(bs-src))<1e-9:
     i=int(np.argmin(br));ev.pose(Q[i]);g_,gp_,_,_=ev.value(Q[i],NONE,measure='gate')
     out['checker_reported']=dict(file=bf,min_reserve_mm=float(br.min()),state=i,label=label(info,src,i),exact_gate_there_mm=round(g_,3),exact_pair_there=gp_,
      note='r19smooth baseline: Checker.check(full=True), min over non-self categories')
  elif info['kind']=='edge':out['checker_reported']=dict(min_reserve_mm=info.get('reported_min_reserve_mm'),note='r19hub edge file')
  else:out['checker_reported']=dict(min_reserve_mm=info.get('r17_min_reserve_mm'),note='r17chain approach (every 3rd step full check)')
  grid=[]
  for ax in (C.CART_AXES if part=='grid' else tuple(part[5:].split('+'))):
   vals=GRID_TR if ax in ('x','y','z') else GRID_YAW if ax=='yaw' else GRID_TILT;unit=C.MM if ax in ('x','y','z') else C.DEG
   for sg in (1,-1):
    for v in vals:
     p=C.pert_of('cart',ax,sg*v*unit);row=dict(axis=ax,value=sg*v,unit='mm' if unit==C.MM else 'deg')
     for meas in ('gate','contact'):
      m_,a_,n_=minimum(ev,Q,noms,p,meas,init=GRID_CAP);row[meas+'_min_mm']=round(m_,3) if a_ else f'>={GRID_CAP:g}'
      if a_:row[meas+'_pair']=a_['pair'];row[meas+'_label']=label(info,src,a_['state'])
     grid.append(row)
  out['grid']=grid
 elif part=='scen' or part.startswith('scen-'):out['scenarios']=scenarios(ev,Q,noms,info,src,key,None if part=='scen' else part[5:].split('+'))
 elif part=='fix' or part.startswith('fix-'):
  dirs=[];out['groups']={}
  for gn in ev.groups:
   lb=min(n['group_gate_lb'].get(gn,1e9) for n in noms);out['groups'][gn]=dict(min_gate_lb_mm=round(lb*1e3,2),searched=bool(lb<.030 and (part=='fix' or gn in part[4:].split('+'))))
   if lb<.030 and (part=='fix' or gn in part[4:].split('+')):dirs+=[('fix',ax,sg,gn,TR) for ax in 'xyz' for sg in (1,-1)]
  out['directions']=directions(ev,Q,noms,info,src,dirs,key,t0)
 elif part=='grasp' or part.startswith('grasp-'):
  out['jaw_axis_tool']=ev.jaw_axis.round(4).tolist()
  ANG=dict(AN,smax=float(KV.get('ROTMAX',1.5))*C.DEG)   # ROTMAX=<deg>: larger cap for the grasp turn
  dirs=[('grasp',ax,sg,None,ANG if ax=='rot' else TR) for ax in (('x','y','z','rot') if part=='grasp' else tuple(part[6:].split('+'))) for sg in (1,-1)] if len(ev.hg) else []
  out['directions']=directions(ev,Q,noms,info,src,dirs,key,t0)
 out['elapsed_s']=round(time.monotonic()-t0,1)
 os.makedirs(C.OUT,exist_ok=True);fn=f"{C.OUT}/scene_{key.replace(':','_')}__{part}.json"
 json.dump(out,open(fn,'w'),indent=1,default=float);print('saved',fn,out['elapsed_s'],'s',flush=True)
 return fn
def scenarios(ev,Q,noms,info,src,key,names=None):
 """Worst sign corner of each cart budget box (all 2^6 corners), min over states (branch and bound)."""
 import itertools
 sc={}
 for name,half in SCENARIOS.items():
  if names and name not in names:continue
  res={};corners=[]
  for sg in itertools.product((1,-1),repeat=6):
   c=np.array(sg)*np.array(half)
   if not any(np.allclose(c,c2) for c2 in corners):corners.append(c)
  Dv=np.array([C.disp_bound(n_,dict(kind='cart',v=list(half))) for n_ in noms])
  for meas in ('gate','contact'):
   key_=np.array([n_[meas] for n_ in noms]);kv=key_-Dv;order=np.argsort(kv);best=GRID_CAP;arg=None;n=0
   for i in order:
    if kv[i]*1e3>=best:break
    for c in corners:
     g,gp,cc,cp=ev.value(Q[i],dict(kind='cart',v=list(c)),measure=meas,cap=best/1e3,nom=noms[i]);n+=1;v=g if meas=='gate' else cc
     if v<best:best=v;arg=dict(state=int(i),label=label(info,src,int(i)),pair=gp if meas=='gate' else cp,corner=[round(x/C.MM,3) for x in c[:3]]+[round(x/C.DEG,3) for x in c[3:]])
   res[meas]=dict(min_mm=round(best,3) if arg else f'>={GRID_CAP:g}',**(arg or {}),evals=n)
  sc[name]=dict(half_range_mm_deg=[round(x/C.MM,3) for x in half[:3]]+[round(x/C.DEG,3) for x in half[3:]],**res)
  print(key,'scenario',name,'gate',res['gate']['min_mm'],'contact',res['contact']['min_mm'],flush=True)
 return sc
def joint_offset(ch,q,axis,val):
 """The cart perturbation through the cart joints (x, y; yaw about the J1 axis), for Checker.check."""
 import mujoco
 q=np.array(q,float)
 if axis=='x':q[0]+=val
 elif axis=='y':q[1]+=val
 elif axis=='yaw':
  ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d);pm=ch.d.xpos[ch.m.body('R_mount').id][:2];pc=ch.d.xpos[ch.m.body('rail_structure').id][:2]
  r=pm-pc;c,s=math.cos(val),math.sin(val);dlt=r-np.array([c*r[0]-s*r[1],s*r[0]+c*r[1]]);q[0]+=dlt[0];q[1]+=dlt[1];q[2]+=val
 return q
def validate(ch,ev,Q,dirs):
 """Checker.check(full=True) just below / above the gate tolerance of cart x, y, yaw, at the binding state."""
 rows=[]
 for rec in dirs:
  if rec['kind']!='cart' or rec['axis'] not in ('x','y','yaw') or not rec['gate'].get('bounded'):continue
  i=rec['gate']['binding']['state'];unit=C.MM if rec['axis']!='yaw' else C.DEG
  for f,base in ((.97,rec['gate']['tol']),(1.03,rec['gate']['violation_at'])):
   v=rec['sign']*base*f*unit;q=joint_offset(ch,Q[i],rec['axis'],v);r=ch.check(q,full=True,mass=0.)
   env=[(x['reserve_mm'],x['pair']) for k,x in r['clearance'].items() if k!='self']
   g,gp,c,cp=ev.value(Q[i],C.pert_of('cart',rec['axis'],v))
   rows.append(dict(axis=rec['axis'],sign=rec['sign'],state=i,value=round(v/unit,4),checker_hits=[h['pair'] for h in r['hits']][:4],
    checker_hit_reasons=sorted(set(h.get('reason','mujoco contact') for h in r['hits'])),checker_min_reserve_mm=round(min(env)[0],3) if env else None,
    checker_pair=min(env)[1] if env else None,evaluator_gate_mm=round(g,3),evaluator_pair=gp))
 return rows
def main():
 import multiprocessing as mp
 parts=KV.get('PARTS','cartT,cartR,grid,fix,grasp').split(',')
 tasks=[(k,p) for k in scene_list() for p in parts if not (p.startswith('grasp') and not k.startswith('play:'))]
 W=int(KV.get('WORKERS',16));DL=float(KV.get('DEADLINE',270));t0=time.monotonic()
 print('tasks',len(tasks),'deadline',DL,'s',flush=True)
 if W<=1:
  for t in tasks:run(t)
 else:
  pool=mp.Pool(min(W,len(tasks)),maxtasksperchild=1);it=pool.imap_unordered(run,tasks);n=0
  try:
   while n<len(tasks):
    left=DL-(time.monotonic()-t0)
    if left<=0:raise mp.TimeoutError
    fn=it.next(timeout=left);n+=1;print('done',fn,f'{time.monotonic()-t0:.0f}s',flush=True)
   pool.close()
  except mp.TimeoutError:
   print(f'DEADLINE {DL:.0f}s: {len(tasks)-n} of {len(tasks)} tasks unfinished (no output written for them); re-run them as separate commands',flush=True)
   pool.terminate()
  pool.join()
 print('all done',f'{time.monotonic()-t0:.0f}s')
if __name__=='__main__':main()
