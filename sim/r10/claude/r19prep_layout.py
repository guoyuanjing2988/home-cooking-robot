"""R19 prep layout fixes (issue #4 step 1; new file, nothing else changed).
Where can the prep stations stand in today's (R18b) kitchen without blocking the checked cooking motion,
and can the arm reach them?

Modes (python r19prep_layout.py MODE [KEY=VALUE ...], run from sim/r10/claude):
 map     free-space ceiling over the counters from the stored swept volumes: for every 2 cm column the
         lowest swept voxel above the counter top (the 84 stored segments of the 6 checked cooking chains,
         dilated 2 voxels, as r19prim_swept.py, plus the 22 checked hub edges, every 4th state, dilated 3,
         as r19prep_screen.py). A fixture lower than the ceiling everywhere under it cannot be hit
         (conservative). -> results/r19/prep/layout_map.json (+ .png)
 screen  every candidate spot (kitchen19.CANDIDATES): static overlap with the fixed items of today's
         kitchen (raw tray, spatula + pad, prep bowls, fridge, faucet, sink, power track, counter ends)
         and the voxel screen against all 106 stored segments -> results/r19/prep/layout_screen.json
 replay  ground truth for the named candidates (NAMES=a,b,..): every stored state of the 6 checked
         chains (plus their grasp approach states) and EVERY state of the hub edges the screen flagged,
         with the candidate's envelope boxes in the scene; fast checker (full=False, as
         r18spatreplay.py / r19prep_spotreplay.py): a SCREEN-LEVEL replay, not a full check.
         -> results/r19/prep/layout_replay_<name>.json   (NPAR=n parallel processes, one per name)
 reach   96-start collision-aware IK (solver.solve, unchanged checker, as r14reach.py) at the working
         poses of the named candidates (kitchen19.REACH_PROBES), with the station geometry in the scene
         and the cooking fixtures of today's kitchen -> results/r19/prep/layout_reach_<probe>.json
Gaps, checker and arm are unchanged (ARM=<id> as everywhere; default UR5e)."""
import sys,os,json,glob,time,collections,subprocess
sys.path.insert(0,'.')
import numpy as np,mujoco
from scipy import ndimage
import chain
from scene import build,save,box
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19 as K19
import arms
KV=dict(a.split('=',1) for a in sys.argv[2:]);MODE=sys.argv[1] if len(sys.argv)>1 else 'map'
OUT='results/r19/prep';os.makedirs(OUT,exist_ok=True)
VOX=.02;LO=np.array([-2.6,-1.2,-.2]);DIM=np.array([270,130,130])   # as r19prim_swept.py
def lin(ix):return (ix[:,0]*DIM[1]+ix[:,1])*DIM[2]+ix[:,2]
def unlin(L):return np.stack([L//(DIM[1]*DIM[2]),(L//DIM[2])%DIM[1],L%DIM[2]],1)
def vox(pts):
 ix=np.floor((pts-LO)/VOX).astype(int);ok=np.all((ix>=0)&(ix<DIM),1);return np.unique(lin(ix[ok]))
def dilate(L,k):
 if len(L)==0:return L
 ix=unlin(L);a=ix.min(0)-k;b=ix.max(0)+k+1;g=np.zeros(b-a,bool);g[tuple((ix-a).T)]=True
 g=ndimage.binary_dilation(g,structure=np.ones((3,3,3),bool),iterations=k);w=np.argwhere(g)+a
 w=w[np.all((w>=0)&(w<DIM),1)];return np.unique(lin(w))
def box_pts_local(h):
 ax=[np.linspace(-h[i],h[i],max(2,int(np.ceil(2*h[i]/VOX))+1)) for i in range(3)];return np.stack(np.meshgrid(*ax,indexing='ij'),-1).reshape(-1,3)
def box_vox(c,s):return vox(box_pts_local(np.asarray(s,float)/2)+np.asarray(c,float))
CHAINS=dict(wok_plate_rinse='wok_s-1_final',wok_plate2_rinse='wok_s-1_r18plate2b',faucet_open='lever_s+1_final',lid_off_to_rack='lid_s-1_final',spider_pot_to_plate='spider_s+1_final',spatula_fetch='spatula_s-1_r18roll-1.15_.30')
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)   # as r19prim_swept.py / r19prep_spotreplay.py
def r18b():
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=8.,0.,180.
def swept_all():
 """106 swept volumes: the 84 stored chain segments (dilated 2) + the 22 hub edges (every 4th state, dilated 3)."""
 r18b();Z=np.load('results/r19/prim/swept_voxels.npz');SW={k:dilate(Z[k].astype(np.int64),2) for k in Z.files}
 cfg=chain.chain_cfg('SD',**{**BASE,'r16_tools':{'ladle':None}});tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d
 rob=[g for g in range(m.ngeom) if m.geom(g).name.startswith('R_') and m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_PLANE]
 cache={g:box_pts_local(m.geom_aabb[g,3:])+m.geom_aabb[g,:3] for g in rob}
 for f in sorted(glob.glob('results/r19/hub/edge_*.json')):
  e=json.load(open(f))
  if not e.get('ok') or not e.get('qs'):continue
  acc=[]
  for q in e['qs'][::4]+[e['qs'][-1]]:
   d.qpos[:]=q;mujoco.mj_kinematics(m,d);acc.append(vox(np.concatenate([(d.geom_xmat[g].reshape(3,3)@cache[g].T).T+d.geom_xpos[g] for g in rob])))
  SW['hub_edge__'+os.path.basename(f)[5:-5]]=dilate(np.unique(np.concatenate(acc)),3)
 return SW
# ---------------------------------------------------------------------------------------------------
if MODE=='map':
 t0=time.monotonic();SW=swept_all();t_sw=time.monotonic()-t0
 xs=np.arange(-1.80,.72,.02)+.01;ys=np.arange(0.,.60,.02)+.01
 ix0=np.floor((np.array([xs[0],ys[0],.85])-LO)/VOX).astype(int)
 groups=collections.defaultdict(list)
 for k in SW:groups[k.split('__')[0]].append(k)
 ceil={};nz=DIM[2]
 for gname,keys in list(groups.items())+[('all',list(SW))]:
  occ=np.zeros(DIM,bool)
  for k in keys:occ[tuple(unlin(SW[k]).T)]=True
  occ=ndimage.binary_dilation(occ,structure=np.ones((3,3,3),bool),iterations=1)   # the fixture's own sampling (as the screen: fixture dilated 1)
  C=np.full((len(xs),len(ys)),np.nan)
  for i,x in enumerate(xs):
   for j,y in enumerate(ys):
    cx,cy=np.floor((np.array([x,y])-LO[:2])/VOX).astype(int);col=occ[cx,cy,:];z0=int(np.floor((.85-LO[2])/VOX))
    hit=np.nonzero(col[z0:])[0];C[i,j]=round(LO[2]+(z0+hit[0])*VOX-.85,2) if len(hit) else 1.2
  ceil[gname]=C
 res=dict(method=__doc__.split('\n')[4:9],xs=xs.round(3).tolist(),ys=ys.round(3).tolist(),swept_build_s=round(t_sw,1),
  ceiling_above_counter_m={g:np.nan_to_num(C,nan=-1).tolist() for g,C in ceil.items()},note='ceiling = height above the counter top (0.85 m) of the lowest dilated swept voxel in that 2 cm column; 1.2 = nothing swept below 2.05 m')
 save(f'{OUT}/layout_map.json',res)
 try:
  import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,ax=plt.subplots(2,1,figsize=(13,7))
  for a,(g,t) in zip(ax,(('all','all stored cooking segments + hub edges'),('spatula_fetch','spatula fetch only'))):
   im=a.imshow(ceil[g].T,origin='lower',extent=[xs[0]-.01,xs[-1]+.01,0,.60],vmin=0,vmax=.6,cmap='viridis',aspect='equal');a.set_title(f'free height above the counter (m): {t}')
   a.set_xlabel('x (m)');a.set_ylabel('y (m, wall = .60)');fig.colorbar(im,ax=a,fraction=.02)
  fig.tight_layout();os.makedirs('renders/r19',exist_ok=True);fig.savefig('renders/r19/prep_layout_map.png',dpi=110)
 except Exception as e:print('no plot',e)
 C=ceil['all'];print('swept build',round(t_sw,1),'s')
 for j in range(len(ys)-1,-1,-2):print(f'y {ys[j]:.2f} '+''.join(' ' if C[i,j]>=1.2 else '#' if C[i,j]<=.06 else str(min(9,int(C[i,j]*10))) for i in range(len(xs))))
 print('       '+''.join('|' if abs(x-round(x,1))<.011 else ' ' for x in xs),' (x -1.80 .. 0.71; digit = free decimetres above the counter, # <= 6 cm, blank = free)')
# ---------------------------------------------------------------------------------------------------
if MODE=='screen':
 t0=time.monotonic();SW=swept_all();t_sw=time.monotonic()-t0
 r18b();cfg=chain.chain_cfg('SD',**{**BASE,'r16_tools':{'ladle':None},'r14_fridge':True,'r17_lever':0.,'r16_lid':'on','r17_plate2':[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]]})
 tree,meta=build(cfg,None);ch=Checker(tree,meta);m,d=ch.m,ch.d;mujoco.mj_forward(m,d)
 fixed=[]
 for g in range(m.ngeom):
  n=m.geom(g).name
  if n.startswith('R_') or not n or m.geom_type[g]==mujoco.mjtGeom.mjGEOM_PLANE:continue
  ab=m.geom_aabb[g];R=d.geom_xmat[g].reshape(3,3);cen=d.geom_xpos[g]+R@ab[:3];ext=np.abs(R)@ab[3:];fixed.append((n,cen-ext,cen+ext))
 rows=[]
 for name,C in K19.CANDIDATES.items():
  boxes=K19.boxes(C);flag=set();static=[];off=[]
  for bn,c,s in boxes:
   lo,hi=np.asarray(c)-np.asarray(s)/2,np.asarray(c)+np.asarray(s)/2
   for n,a,b in fixed:
    if n.startswith(('counter_','north_cabinet','sink_cabinet','north_wall','floor','south_')):continue
    gap=max(np.max(a-hi),np.max(lo-b))   # AABB separation (<0: overlap)
    if gap<.005:static.append(dict(box=bn,fixture=n,gap_mm=round(gap*1000,1)))
   if not K19.on_counter(lo,hi):off.append(bn)
   F=dilate(box_vox(c,s),1)
   flag|={k for k,v in SW.items() if np.intersect1d(v,F,assume_unique=True).size}
  by=collections.Counter(k.split('__')[0] for k in flag)
  rows.append(dict(name=name,item=C['item'],desc=C['desc'],boxes=[dict(name=b,center=np.round(c,3).tolist(),size=list(s)) for b,c,s in boxes],
   static_overlaps=static,off_counter=off,flagged=len(flag),of=len(SW),by_action=dict(by),flagged_segments=sorted(flag)))
  print(f"{name:26s} {C['item']:9s} static {len(static):2d} {sorted({s['fixture'] for s in static})[:4]} off {off}  flagged {len(flag):3d}/{len(SW)} {dict(by)}",flush=True)
 save(f'{OUT}/layout_screen.json',dict(method=__doc__,swept_build_s=round(t_sw,1),segments=len(SW),rows=rows))
# ---------------------------------------------------------------------------------------------------
def replay_one(name):
 C=K19.CANDIDATES[name];boxes=K19.boxes(C);scr=json.load(open(f'{OUT}/layout_screen.json'));row=next(r for r in scr['rows'] if r['name']==name)
 seglab=json.load(open('results/r19/prim/segments.json'))['labels']
 def with_boxes(tree):
  for bn,c,s in boxes:box(tree.find('worldbody'),'cand_'+bn,c,s,(.9,.6,.1,1))
  return tree
 t0=time.monotonic();res={};n_states=0;mins={}
 for n,f in CHAINS.items():
  r=json.load(open(f'results/r17/chain_{f}.json'));r18b()
  for k,v in r.get('tool_xy',{}).items():
   if k!='spatula':K.TOOL_XY[k]=tuple(v)
  if r['obj']=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
  ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in n else {}
  cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])})
  tree,meta=build(cfg,None);ch=Checker(with_boxes(tree),meta);hit=collections.Counter();first=None
  qs=[(seglab[n][i] or seglab[n][1],q) for i,q in enumerate(r['play'])]+[(f"approach@{a['kf']}",q) for a,aq in zip(r['approaches'],r['approach_qs']) for q in aq]
  for lab,q in qs:
   c=ch.check(np.array(q),full=False,mass=0.);n_states+=1
   hs=[h for h in c['hits'] if any(g.startswith('cand_') for g in h['pair'])]
   if hs:
    hit[lab]+=1
    if first is None:first=dict(segment=lab,pair=hs[0]['pair'],gap_mm=hs[0].get('real_gap_mm'))
  res[n]=dict(states=len(qs),hit_segments=dict(hit),first=first);print(name,n,len(qs),'states; hit',dict(hit),first,flush=True)
 hub=[k for k in row['flagged_segments'] if k.startswith('hub_edge__')]
 r18b();cfg=chain.chain_cfg('SD',**{**BASE,'r16_tools':{'ladle':None},'r17_lever':0.,'r16_lid':'on','r17_plate2':[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]]})
 tree,meta=build(cfg,None);ch=Checker(with_boxes(tree),meta)
 for k in hub:
  e=json.load(open(f"results/r19/hub/edge_{k[10:]}.json"));h=0;g=None
  for q in e['qs']:
   c=ch.check(np.array(q),full=False,mass=0.);n_states+=1;hs=[x for x in c['hits'] if any(gg.startswith('cand_') for gg in x['pair'])]
   if hs:
    h+=1
    if g is None:g=dict(pair=hs[0]['pair'],gap_mm=hs[0].get('real_gap_mm'))
  res[k]=dict(states=len(e['qs']),hit_states=h,first=g);print(name,k,len(e['qs']),'states (every state); hit',h,g,flush=True)
 out=dict(name=name,candidate=C,boxes=[dict(name=b,center=np.round(c,3).tolist(),size=list(s)) for b,c,s in boxes],screen_flagged=row['flagged'],states=n_states,elapsed_s=round(time.monotonic()-t0,1),
  method='fast checker (full=False) on every stored state of the 6 checked chains + approaches and every state of each flagged hub edge; candidate envelope boxes in the scene: a SCREEN-LEVEL replay, not a full check',
  results=res,any_hit=any((v.get('hit_segments') or v.get('hit_states')) for v in res.values()))
 save(f'{OUT}/layout_replay_{name}.json',out);print(name,'any hit',out['any_hit'],'states',n_states,'elapsed',out['elapsed_s'],flush=True)
if MODE=='replay':
 names=KV['NAMES'].split(',');npar=int(KV.get('NPAR',1))
 if len(names)==1 or npar==1:
  for nm in names:replay_one(nm)
 else:
  procs=[subprocess.Popen([sys.executable,__file__,'replay',f'NAMES={nm}']+[a for a in sys.argv[2:] if a.startswith('ARM=')]) for nm in names]
  for p in procs:p.wait()
# ---------------------------------------------------------------------------------------------------
def reach_one(probe):
 from solver import solve
 P=K19.REACH_PROBES[probe];r18b()
 held=P.get('held')
 cfg=chain.chain_cfg('SD',**{**BASE,'r16_tools':{'ladle':None},'r14_fridge':True,'r17_lever':float(P.get('lever',0.)),'r16_lid':'on','r17_plate2':[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]],
  **K19.base_cfg(),'r19':dict(P['scene']),**(K17.held_cfg(held,P.get('sign',1)) if held else {})})
 tree,meta=build(cfg,None);K19.add(tree,cfg);ch=Checker(tree,meta)
 t=dict(name=probe,points=[list(P['p'])]*2,held=None,kind='transfer',force=None,approach=list(P['a']),jaws=[tuple(P['j'])],jaw_q=P.get('jaw_q',.015))
 if 'cart_x' in P:t['cart_x']=P['cart_x']
 best=None;stat=collections.Counter();cands=[]
 for seed in [int(s) for s in KV.get('SEEDS','14,15').split(',')]:
  r=solve(ch,np.array(P['p'],float),list(P['a']),target=t,seed=seed)
  stat.update(r['status_counts']);cands+=r['candidates']
  if not r['ok'] and (best is None or 'q' not in best):best=r['best']
 cands=sorted(cands,key=lambda c:-c['reserve_mm'])
 blockers=collections.Counter()
 if not cands:
  r=solve(ch,np.array(P['p'],float),list(P['a']),target=t,seed=99)
  for row in r['rows']:
   for h in (row.get('check') or {}).get('hits',[]):blockers[' | '.join(sorted(h['pair']))]+=1
 out=dict(probe=probe,desc=P['desc'],point=list(P['p']),approach=list(P['a']),jaw=list(P['j']),held=held,scene=P['scene'],ok=bool(cands),status_counts=dict(stat),
  n_ok=len(cands),best_reserve_mm=round(cands[0]['reserve_mm'],1) if cands else None,carts=sorted({round(c['q'][0],2) for c in cands}),best_q=cands[0]['q'] if cands else None,
  blockers=blockers.most_common(8),arm=arms.current())
 save(f"{OUT}/layout_reach_{probe}{arms.tag()}.json",out)
 print(f"{probe:28s} ok {out['ok']} n_ok {out['n_ok']} reserve {out['best_reserve_mm']} carts {out['carts'][:6]} {dict(stat)} {out['blockers'][:3]}",flush=True)
if MODE=='reach':
 names=KV['PROBES'].split(',') if 'PROBES' in KV else list(K19.REACH_PROBES)
 npar=int(KV.get('NPAR',1))
 if len(names)==1 or npar==1:
  for nm in names:reach_one(nm)
 else:
  from concurrent.futures import ThreadPoolExecutor
  def run(nm):
   r=subprocess.run([sys.executable,__file__,'reach',f'PROBES={nm}']+[a for a in sys.argv[2:] if a.startswith(('ARM=','SEEDS='))],capture_output=True,text=True)
   return (r.stdout.strip().splitlines() or [r.stderr[-400:]])[-1]
  with ThreadPoolExecutor(npar) as ex:
   for o in ex.map(run,names):print(o,flush=True)
