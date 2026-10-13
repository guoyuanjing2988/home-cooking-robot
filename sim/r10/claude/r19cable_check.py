"""R19 #36: re-check of the adopted paths with the PGC-140 cable connector + first cable section modelled
(arm options ur5e_enc2_pgcc*, r19cable.py). New file; writes only under results/r19/cable/.

The scenes and states are those of the existing re-check tools, run unchanged; only the arm option differs:
 chains  the adopted chains in the pot-zone layer, r19pot_check.py's scene and states (play cut to <= 4 mm with
         r19smooth.sample_poly + FastBound of the checked model, each approach_qs too, the lid's declared rack window).
         python r19cable_check.py chains FILES=<chain json>[,..] RACK=keyed SPX=1.56 SPY=.20 PY=.15 ARM=<arm> [WORKERS=20]
 hub     hub edges (edge_*.json of a folder), joint-linear between the stored states, cut to <= 4 mm with the checked model,
         in r19hub.py's union scene (PY=.15: plating spot), POT=1 with the pot-zone layer installed first (as r19pot_hub.py).
         python r19cable_check.py hub DIR=<edge folder> [EDGES=A__B,..] [POT=1 RACK=keyed SPX=1.56 SPY=.20] PY=.15 ARM=<arm> TAG=<t>
 stir    the stored stir library entry's certified states (results/r19/stir/lib_stir_cycle_<src>.json), cut to <= 4 mm with
         the checked model, in its own model (r19stir_cycle.model(-1): SCENE=r17, spatula 0.45 m, jaw sense -1) with the
         plume rule (every robot geom except the spatula / cart / dock >= 0 mm from the r 0.20 m plume cylinder).
         python r19cable_check.py stir LIB=<lib json> [PARTS=work|return] ARM=<arm>
 prep    a prep set (results/r19/prep/chain_*.json), r19prep_verify.py's scenes and states (play 2pi-unwrapped, densified with
         the checked model's point bound; approaches densified; its food window for R_finger_* / R_gripper_* only).
         python r19cable_check.py prep FILE=<chain json> ARM=<arm>
ARM=<base>c_ALL / <base>c_SEL (r19cable.SCREENS) put several routings on the gripper at once, each its own geom group
'cable.<routing>'; the per-routing verdict (cable_groups) counts a state as failed if it has a non-cable hit, is out of range,
or the group's bound reserve or MuJoCo-contact rule (or, stir, its plume distance) fails: the checker's own rules applied to
that routing's pairs. CABLEONLY=1 evaluates only the cable groups' pairs (same rules; every other pair is the one already
certified without the cable): a SCREEN for comparing routings. Certificates are runs with one routing and no CABLEONLY.
Every state: Checker.check(full=True) (MuJoCo contacts + GJK lower-bound certificate, 10 mm robot-environment, 5 mm
gripper / held-environment, 0 mm self, joint ranges), unchanged. In addition, per state, the reserve (lower bound -
required gap) of three geom groups against the environment and against the rest of the robot (self), from the same
checker's pair bounds (Bounds.last_lower; the 3 smallest of each group refined with the exact GJK bound):
 cable    R_pgc_cable_*  (connector, plug, bend, run; on R_tool, so the checker gives them the 5 mm gripper gate);
 gripper  R_gripper_oem_*, R_gripper_palm, R_finger_*;
 wrist    every robot geom on the wrist 1 / 2 / 3 bodies.
-> results/r19/cable/<mode>/<name>__<arm>.json"""
import sys,os,json,time,math,glob
sys.path.insert(0,'.')
import numpy as np
MODE=sys.argv[1]
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a)
ARM=KV['ARM'];os.environ['ARM']=ARM
OUT='results/r19/cable'
GROUPS=('cable','gripper','wrist')
_C={}
def groups_of(ch):
 """pair indices of Bounds.pairs per (group, env|self)."""
 m=ch.m;names=ch.gnames;wb={m.body(n).id for n in ('R_arm_wrist_1_link','R_arm_wrist_2_link','R_arm_wrist_3_link')}
 def grp(g):
  n=names[g]
  if n.startswith('R_pgc_cable.'):return 'cable.'+n.split('.')[1]   # screening model (routing ALL): one group per routing
  if n.startswith('R_pgc_cable'):return 'cable'
  if n.startswith(('R_gripper_oem','R_finger_')) or n=='R_gripper_palm':return 'gripper'
  if ch.robot[g] and int(m.geom_bodyid[g]) in wb:return 'wrist'
  return None
 out={}
 for i,(a,b,need,cat) in enumerate(ch.bounds.pairs):
  kind='self' if cat=='self' else 'env' if cat in ('robot_environment','held_gripper_environment') else None
  if kind is None:continue
  for g in {grp(a),grp(b)}-{None}:out.setdefault((g,kind),[]).append(i)
 G={k:np.array(v,int) for k,v in out.items()};G['_cable_of']={g:grp(g) for g in range(m.ngeom) if (grp(g) or '').startswith('cable')};return G
def group_reserves(ch,G):
 '''per group and env|self: the smallest (lower bound - required gap) over its pairs (as Bounds.check); and for the cable
 groups the checker's literal MuJoCo-contact rule (reference.forbidden: a contact distance < the required gap, with
 Checker.required not None, is a hit): '<group>_<kind>_mj' = smallest contact distance - required gap, when a contact exists.'''
 lo=ch.bounds.last_lower;P=ch.bounds.pairs;res={};CG=G['_cable_of']
 for c in ch.d.contact[:ch.d.ncon]:
  a,b=int(c.geom[0]),int(c.geom[1]);gs={CG.get(a),CG.get(b)}-{None}
  if not gs:continue
  req=ch.required(ch,a,b)
  if req is None:continue
  kind='self' if req[1]=='self' else 'env';x=(float(c.dist)-req[0])*1e3
  for g in gs:
   k=f'{g}_{kind}_mj'
   if k not in res or x<res[k][0]:res[k]=(round(x,3),[ch.gnames[a],ch.gnames[b]])
 for (g,kind),idx in ((k,v) for k,v in G.items() if k!='_cable_of'):
  v=lo[idx]-ch.bounds.need[idx];o=np.argsort(v)[:3];best=(1e9,None)
  for j in o:
   i=idx[j];a,b,need,_=P[i];x=v[j]
   if x<1e5:x=max(x,ch.bounds.pair(a,b)['lower_m']-need)   # refine (any valid lower bound may be used; the larger is tighter)
   if x<best[0]:best=(x,[ch.gnames[a],ch.gnames[b]])
  rest=np.delete(v,o);lb=float(rest.min()) if len(rest) else 1e9   # the unrefined rest is a valid lower bound too
  if lb<best[0]:best=(lb,None)
  res[f'{g}_{kind}']=(round(best[0]*1e3,3),best[1])
 return res
def prepmod():
 '''r19prep_verify.py imported unchanged; its argv parser wants KEY=VALUE only, so it sees argv without the mode word.'''
 if 'r19prep_verify' in sys.modules:return sys.modules['r19prep_verify']
 a=sys.argv;sys.argv=[a[0]]+a[2:]
 try:import r19prep_verify as RV
 finally:sys.argv=a
 return RV
def ctx(key):
 if key in _C:return _C[key]
 import mujoco
 from checker import Checker
 from r19enc_check import meshheld
 import arms
 assert arms.current()==ARM,(arms.current(),ARM)
 plume=None
 if MODE=='chains':
  import r19pot_check as RP
  f,part=key;ch=RP.ctx(f,part)
 elif MODE=='hub':
  if KV.get('POT')=='1':
   import kitchen19pot as P;P.install(rack=KV.get('RACK'),spider=(KV['SPX'],KV['SPY']) if 'SPX' in KV else None)
  import r19hub as H
  tree,meta=H.union_tree();meshheld(tree);ch=Checker(tree,meta)
 elif MODE=='prep':
  RV=prepmod();R=json.load(open(KV['FILE']));ch,_=RV.scene_for(R,key if key=='play' else tuple(key))   # r19prep_verify's own scenes (incl. its food window for R_finger_* / R_gripper_*)
 elif MODE=='stir':
  import r19stir_cycle as C,mujoco,xml.etree.ElementTree as E,kitchen15 as K15
  from scene import fmt
  assert C.ARM==ARM;M=C.model(-1);ch=M['ch']
  # the plume rule of r19stir_cycle.model (every robot geom except R_gripper_spatula*, R_cart*, R_dock* >= 0 mm from the r 0.20 m cylinder
  # about the wok axis, rim .. 1.25 m), rebuilt here so that each cable group gets its own value; the non-cable minimum is the stored rule
  tr=E.ElementTree(E.fromstring(ch.xml));E.SubElement(tr.find('worldbody'),'geom',name='r15_plume',type='cylinder',pos=fmt([K15.WOK0[0],K15.WOK0[1],(K15.RIM_Z+1.25)/2]),size=fmt([C.PLUME,(1.25-K15.RIM_Z)/2]),contype='0',conaffinity='0')
  pm=mujoco.MjModel.from_xml_string(E.tostring(tr.getroot(),encoding='unicode'));pd=mujoco.MjData(pm);pl=pm.geom('r15_plume').id;ft=np.zeros(6)
  rob=[g for g in range(pm.ngeom) if pm.geom(g).name.startswith('R_') and not pm.geom(g).name.startswith(('R_gripper_spatula','R_cart','R_dock'))]
  def cg(n):return None if not n.startswith('R_pgc_cable') else 'cable.'+n.split('.')[1] if n.startswith('R_pgc_cable.') else 'cable'
  def plume(q):
   pd.qpos[:]=q;mujoco.mj_forward(pm,pd);best=(1e9,None);pg={}
   for g in rob:
    v=1000*mujoco.mj_geomDistance(pm,pd,g,pl,1.,ft);k=cg(pm.geom(g).name)
    if k:pg[k]=min(pg.get(k,1e9),v)
    elif v<best[0]:best=(v,pm.geom(g).name)
   for k,v in pg.items():   # a single routing: its cable is part of the rule's minimum too
    if not k.startswith('cable.') and v<best[0]:best=(v,'cable')
   return best[0],best[1],pg
 else:raise KeyError(MODE)
 assert any(n.startswith('R_pgc_cable') for n in ch.gnames)==bool(arms.ARMS[ARM].get('cable')),'cable geoms present iff the arm option has them'
 _C[key]=dict(ch=ch,G=groups_of(ch),plume=plume);return _C[key]
CABLEONLY=KV.get('CABLEONLY')=='1'
def cable_only(ch,G,q):
 '''CABLEONLY=1 (a SCREEN of cable routings, never a certificate): only the pairs of the cable groups are evaluated, with the
 checker's own rules (lower bound - required gap from enclosing boxes, the close ones and the 3 smallest per group refined
 with the exact GJK bound distance.Bounds.pair; and the MuJoCo contact rule). Valid for comparing routings because every
 other pair is the same as in the arm option without the cable, whose certificate exists.'''
 import mujoco
 m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_kinematics(m,d);mujoco.mj_comPos(m,d);mujoco.mj_collision(m,d)
 A=m.geom_aabb;R=d.geom_xmat.reshape(-1,3,3);cw=d.geom_xpos+np.einsum('gij,gj->gi',R,A[:,:3]);hw=np.einsum('gij,gj->gi',np.abs(R),A[:,3:])
 lo,hi=cw-hw,cw+hw;B=ch.bounds;P=B.pairs;res={};CG=G['_cable_of']
 for c in d.contact[:d.ncon]:
  a,b=int(c.geom[0]),int(c.geom[1]);gs={CG.get(a),CG.get(b)}-{None}
  if not gs:continue
  req=ch.required(ch,a,b)
  if req is None:continue
  kind='self' if req[1]=='self' else 'env';x=(float(c.dist)-req[0])*1e3
  for g in gs:
   k=f'{g}_{kind}_mj'
   if k not in res or x<res[k][0]:res[k]=(round(x,3),[ch.gnames[a],ch.gnames[b]])
 for key,idx in G.items():
  if key=='_cable_of' or not key[0].startswith('cable'):continue
  g,kind=key
  aa=B.aa[idx];bb=B.bb[idx];need=B.need[idx]
  gap=np.linalg.norm(np.maximum(np.maximum(lo[aa]-hi[bb],lo[bb]-hi[aa]),0),axis=1)
  pl=(m.geom_type[aa]==0)|(m.geom_type[bb]==0);gap[pl]=1e9;v=gap-need
  ref=set(np.flatnonzero(v<.002).tolist())|set(np.argsort(v)[:3].tolist())|set(np.flatnonzero(pl).tolist());best=(1e9,None)
  for j in ref:
   i=idx[j];x=B.pair(int(aa[j]),int(bb[j]))['lower_m']-need[j]
   if not pl[j]:x=max(x,v[j])
   v[j]=x
   if x<best[0]:best=(x,[ch.gnames[aa[j]],ch.gnames[bb[j]]])
  if v.min()<best[0]:best=(float(v.min()),None)
  res[f'{g}_{kind}']=(round(best[0]*1e3,3),best[1])
 return res
def work(args):
 key,Q=args;c=ctx(tuple(key) if isinstance(key,list) else key);ch=c['ch'];out=[]
 for q in Q:
  if CABLEONLY:
   out.append(dict(h=[],nc=False,r=True,cl={},g=cable_only(ch,c['G'],np.asarray(q))))
   if c['plume']:
    v,gn,pg=c['plume'](np.asarray(q));out[-1]['pl']=(round(v,2),gn)
    for g,x in pg.items():out[-1]['g'][f'{g}_plume']=(round(x,2),None)
   continue
  r=ch.check(np.asarray(q),full=True,mass=0.)
  row=dict(h=[h['pair'] for h in r['hits']][:3],nc=any(not any(n.startswith('R_pgc_cable') for n in h['pair']) for h in r['hits']),r=bool(r['ranges']),cl={k:(round(v['reserve_mm'],3),v['pair']) for k,v in r['clearance'].items()},g=group_reserves(ch,c['G']))
  if MODE=='chains':row['w']=bool(getattr(ch,'_r19pot_in',False))
  if c['plume']:
   v,gn,pg=c['plume'](np.asarray(q));row['pl']=(round(v,2),gn)
   for g,x in pg.items():row['g'][f'{g}_plume']=(round(x,2),None)   # plume distance of each cable group (mm; the rule is >= 0)
  out.append(row)
 return out
def cable_group(R,g):
 '''verdict of one cable group (one routing in the screening model): a state fails if it has a non-cable hit or is out of
 range, or the group's bound reserve < 0, or its MuJoCo contact rule fails, or (stir) its plume distance < 0.'''
 G=lambda x,k:x['g'].get(f'{g}_{k}',(1e9,))[0]
 bad=[i for i,x in enumerate(R) if not x['r'] or x['nc'] or min(G(x,'env'),G(x,'self'))<-1e-3 or min(G(x,'env_mj'),G(x,'self_mj'))<-1e-3 or G(x,'plume')<0]
 d=dict(hit_states=len(bad),first_hit_states=bad[:5],min_env=min(G(x,'env') for x in R),min_self=min(G(x,'self') for x in R),min_env_mj=min(G(x,'env_mj') for x in R),min_self_mj=min(G(x,'self_mj') for x in R))
 envp=min(R,key=lambda x:G(x,'env'))['g'].get(f'{g}_env',(None,None))[1];selfp=min(R,key=lambda x:G(x,'self'))['g'].get(f'{g}_self',(None,None))[1]
 d.update(min_env_pair=envp,min_self_pair=selfp)
 if R and 'pl' in R[0]:d['min_plume']=min(G(x,'plume') for x in R)
 return d
def summarize(R,meta):
 hit=[i for i,x in enumerate(R) if x['h'] or not x['r']];pairs={}
 for i in hit:
  for p in R[i]['h']:k=' | '.join(sorted(p));pairs[k]=pairs.get(k,0)+1
 cats={}
 for x in R:
  for k,(v,pr) in x['cl'].items():
   if k not in cats or v<cats[k]['reserve_mm']:cats[k]=dict(reserve_mm=v,pair=pr)
 grp={}
 for i,x in enumerate(R):
  for k,(v,pr) in x['g'].items():
   if k not in grp or v<grp[k]['reserve_mm']:grp[k]=dict(reserve_mm=v,pair=pr,state=i)
 runs=[]
 for i in hit:
  if runs and i==runs[-1][1]+1:runs[-1][1]=i
  else:runs.append([i,i])
 nch=sum(1 for x in R if not x['r'] or x['nc'])   # states with a hit that involves no cable geom (or out of range)
 d=dict(**meta,ok=not hit,hit_states=len(hit),noncable_hit_states=nch,hit_pairs=dict(sorted(pairs.items(),key=lambda kv:-kv[1])),hit_runs=runs[:30],out_of_range=sum(not x['r'] for x in R),
  min_reserve_by_category=cats,min_env_reserve_mm=min([v['reserve_mm'] for k,v in cats.items() if k!='self'],default=None),group_reserves=grp,
  cable_groups={g:cable_group(R,g) for g in sorted({__import__('re').sub(r'_(env|self)(_mj)?$|_plume$','',k) for x in R for k in x['g'] if k.startswith('cable')})})
 if R and 'w' in R[0]:d['window_states']=sum(x['w'] for x in R)
 if R and 'pl' in R[0]:pm=min(R,key=lambda x:x['pl'][0])['pl'];d.update(min_plume_mm=pm[0],min_plume_geom=pm[1],plume_violations=sum(x['pl'][0]<0 for x in R))
 return d
def run(parts,name,extra):
 """parts: {part name: (ctx key, stored states Q)}; cut to <= 4 mm with the checked model; check; save."""
 import multiprocessing as mp,r19smooth as S
 W=int(KV.get('WORKERS',20));t0=time.monotonic();jobs=[];meta={};X={}
 for p,(key,Q) in parts.items():
  if MODE=='chains':
   import r19pot_check as RP
   QS,sp=RP.states(*key);src=None
  elif MODE=='prep':   # as r19prep_verify main: the play 2pi-unwrapped, then densified with the checked model's point bound; approaches densified
   RV=prepmod();c=ctx(tuple(key) if isinstance(key,list) else key)['ch']
   QS,sp=RV.densify(c,RV.unwrap(c,Q)[0] if key=='play' else np.array(Q,float))
  else:
   QS,src,sp=S.sample_poly(np.asarray(Q,float),S.FastBound(ctx(key)['ch']))
  meta[p]=dict(stored_states=len(Q),states=len(QS),max_step_bound_mm=round(sp*1e3,3));X[p]=QS
  n=max(10,min(40,math.ceil(len(QS)/(W*2))));jobs+=[(p,key,QS[i:i+n].tolist()) for i in range(0,len(QS),n)]
 print(name,{p:(m['stored_states'],m['states'],m['max_step_bound_mm']) for p,m in meta.items()},'checks',sum(len(j[2]) for j in jobs),flush=True)
 with mp.Pool(W) as pool:res=pool.map(work,[(list(k) if isinstance(k,tuple) else k,Q) for p,k,Q in jobs],chunksize=1)
 rows={p:[] for p in parts}
 for (p,_,_),o in zip(jobs,res):rows[p]+=o
 rep={p:summarize(rows[p],meta[p]) for p in parts}
 out=dict(name=name,arm=ARM,options={k:v for k,v in KV.items() if k not in ('WORKERS',)},ok=all(v['ok'] for v in rep.values()),parts=rep,
  per_state={p:[dict(env=min([v[0] for k,v in x['cl'].items() if k!='self'],default=None),self=x['cl'].get('self',[None])[0],h=x['h'],**{k:v[0] for k,v in x['g'].items()},**({'pl':x['pl'][0]} if 'pl' in x else {})) for x in rows[p]] for p in parts},
  elapsed_s=round(time.monotonic()-t0),method=__doc__,**extra)
 d=f'{OUT}/{MODE}';os.makedirs(d,exist_ok=True);fn=f"{d}/{name}__{ARM}{'_cableonly' if CABLEONLY else ''}.json";json.dump(out,open(fn,'w'),default=float)
 print('saved',fn,'ok',out['ok'],'elapsed',out['elapsed_s'],'s',flush=True)
 for p,v in rep.items():
  print('  ',p,v['states'],'st, step',v['max_step_bound_mm'],'hits',v['hit_states'],list(v['hit_pairs'].items())[:3],'| min env',v['min_env_reserve_mm'],
   '| self',v['min_reserve_by_category'].get('self',{}).get('reserve_mm'),'|',{k:g['reserve_mm'] for k,g in sorted(v['group_reserves'].items())},
   ('| plume %s'%v.get('min_plume_mm')) if 'min_plume_mm' in v else '',flush=True)
  for g,cg in v['cable_groups'].items():print('      ',g,'hit states',cg['hit_states'],'env',cg['min_env'],'self',cg['min_self'],'mj',cg['min_env_mj'],cg['min_self_mj'],('plume %s'%cg['min_plume']) if 'min_plume' in cg else '',flush=True)
 return out
def main():
 if MODE=='chains':
  for f in KV['FILES'].split(','):
   r=json.load(open(f));parts={'play':((f,'play'),r['play'])}
   for k,a in enumerate(r['approach_qs']):
    if a:parts[f'app{k}']=((f,f'app{k}'),a)
   tag=os.path.basename(f)[:-5]+('_rack' if KV.get('RACK')=='keyed' else '')+(f"_sp{KV['SPX']}_{KV['SPY']}" if 'SPX' in KV else '')
   run(parts,tag,dict(file=f))
 elif MODE=='hub':
  from r19smooth import unwrap
  D=KV['DIR'];E_=[e for e in KV.get('EDGES','').split(',') if e] or sorted(os.path.basename(f)[5:-5] for f in glob.glob(f'{D}/edge_*.json'))
  parts={e:('hub',unwrap(json.load(open(f'{D}/edge_{e}.json'))['qs'])) for e in E_}
  run(parts,KV.get('TAG','hub'),dict(dir=D,edges=E_))
 elif MODE=='prep':
  R=json.load(open(KV['FILE']));assert R.get('ok') and R.get('play')
  parts={'play':('play',R['play'])}
  for i,aq in enumerate(R.get('approach_qs') or []):
   if aq:parts[f'app{i}']=(['app',i],aq)
  run(parts,os.path.basename(KV['FILE'])[:-5],dict(file=KV['FILE']))
 elif MODE=='stir':
  L=json.load(open(KV['LIB']));assert 'jaw sense -1' in L['verification']['certificate']['scene']
  Q=np.array(L['states']['q'],float);k=np.array(L['states']['kinds'])   # stored grouped by segment (works, then returns); hand-offs coincide exactly
  sel=[p for p in KV.get('PARTS','').split(',') if p]   # PARTS=work or PARTS=return: a subset of the segments (by name prefix), to keep each command short
  run({n:('stir',Q[k==n]) for n in dict.fromkeys(k) if not sel or n.startswith(tuple(sel))},os.path.basename(KV['LIB'])[:-5]+('_'+'_'.join(sel) if sel else ''),dict(lib=KV['LIB'],note='each stored segment (work_i, return_i->i+1) on its own: joint-linear between its consecutive certified states, cut further if the checked model needs it; segment ends coincide (0.0 rad)'))
if __name__=='__main__':main()
