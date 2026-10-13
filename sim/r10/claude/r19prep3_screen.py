"""R19 prep step 3 (#38): screen the new fixture spots of the step-3 sets against the stored cooking motion (new file;
r19prep_layout.py is imported for its helpers and is not changed; its result files are not written).
Same two-stage method as r19prep_layout.py screen + replay:
 1. voxel screen: the fixture's envelope boxes (every part's world AABB) against the 84 stored swept segments of the 6
    checked cooking chains and the edges of the hub roadmap HUBDIR (default: the PY=.15 ur5e_enc2_pgc roadmap);
 2. ground truth [screen level]: the fast checker (full=False, as r18spatreplay.py) on EVERY stored state of the 6
    chains (+ their grasp approaches) and EVERY state of each flagged hub edge, with the boxes in the scene; only hits
    with the fixture boxes are counted.
Fixtures (prep-time layout of R19_PREP_STEP3.md): tub (with the basket nested) at TUBP, the basket / prep bowl on the
front spot FRONTP, the staging bowl on plating spot 2, the catch tray under the lever blade plate.
python r19prep3_screen.py [NAMES=a,b] [NPAR=16] [ARM=ur5e_enc2_pgc] [HUBDIR=results/r19/hub_py.15_ur5e_enc2_pgc]
 -> results/r19/prep3/screen.json, results/r19/prep3/replay_<name>[_<edge>].json"""
import sys,os,json,time,subprocess,collections
sys.path.insert(0,'.')
KV=dict(a.split('=',1) for a in sys.argv[1:])
HUB=KV.get('HUBDIR','results/r19/hub_py.15_ur5e_enc2_pgc');ARMA='ARM='+KV.get('ARM','ur5e_enc2_pgc')
_argv=sys.argv;sys.argv=['r19prep_layout.py','lib',f'HUBDIR={HUB}',ARMA]
import r19prep_layout as LY   # MODE 'lib': only the helpers are defined
sys.argv=_argv
import numpy as np,mujoco,chain
from scene import build,save,box
from checker import Checker
import kitchen15 as K15,kitchen16 as K,kitchen17 as K17,kitchen19 as K19,kitchen19p3 as P3,r19prep3_actions as A3,arms
OUT='results/r19/prep3';os.makedirs(OUT,exist_ok=True)
def fixtures():
 Rt,pt=A3.tub_pose();Rn,pn=A3.nest_pose(A3.BYAW);Rf,pf=A3.front_pose();Rf=K.Rz(A3.BYAW);B=P3.pitched('basket_p30');T=P3.pitched('tub_p15')
 lx,ly,_=K19.LAYOUT['lever'];I=np.eye(3)
 return {'tub_nested':dict(desc='soak tub at TUBP with the wash basket nested (idle state of the soak set)',objs=[(T,Rt,pt),(B,Rn,pn)]),
  'front_basket':dict(desc='wash basket on the front spot FRONTP (prep-time only)',objs=[(B,Rf,pf)]),
  'front_bowl':dict(desc='prep bowl on the front spot FRONTP (prep-time only)',objs=[('bowl',Rf,pf)]),
  'p2_bowl':dict(desc='staging bowl on plating spot 2 (0.17, 0.15), knob toward -x (prep-time staging)',objs=[('bowl',K.Rz(180),np.array([.17,.15,K19.COUNTER_TOP]))]),
  'ctray':dict(desc='catch tray seated under the lever blade plate (lever base at the work spot)',objs=[('ctray',I,np.array([lx,ly,.862]))])}
def boxes(F):
 """World AABB of every part of the fixture objects (name, centre, size)."""
 out=[]
 for name,R,p in F['objs']:
  for n,t,q,s,Rp in K.OBJ[name]['parts']:
   R_=np.asarray(R)@np.asarray(Rp);c=np.asarray(R)@np.asarray(q)+np.asarray(p)
   h=np.array([s[0],s[0],s[1]]) if t=='cylinder' else np.asarray(s,float);ext=np.abs(R_)@h
   if t=='cylinder':ext=np.abs(R_)@np.array([s[0]/np.cos(np.pi/16),s[0]/np.cos(np.pi/16),s[1]])   # the circumscribed prism of mesh_held
   out.append((n,c,2*ext))
 return out
def screen():
 t0=time.monotonic();SW=LY.swept_all();rows=[]
 for nm,F in fixtures().items():
  flag=set()
  for bn,c,s in boxes(F):
   Fv=LY.dilate(LY.box_vox(c,s),1);flag|={k for k,v in SW.items() if np.intersect1d(v,Fv,assume_unique=True).size}
  by=collections.Counter(k.split('__')[0] for k in flag)
  rows.append(dict(name=nm,desc=F['desc'],flagged=len(flag),of=len(SW),by_action=dict(by),flagged_segments=sorted(flag)))
  print(nm,'flagged',len(flag),'/',len(SW),dict(by),flush=True)
 save(f'{OUT}/screen.json',dict(hub_dir=HUB,arm=arms.current(),swept_build_s=round(time.monotonic()-t0,1),rows=rows))
def replay(nm,edge=None):
 F=fixtures()[nm];bx=boxes(F);seglab=json.load(open('results/r19/prim/segments.json'))['labels']
 def with_boxes(tree):
  for bn,c,s in bx:box(tree.find('worldbody'),'cand_'+bn,c,s,(.9,.6,.1,1))
  return tree
 res={};n_states=0
 if edge is None:
  for n,f in LY.CHAINS.items():
   r=json.load(open(f'results/r17/chain_{f}.json'));LY.r18b()
   for k,v in r.get('tool_xy',{}).items():
    if k!='spatula':K.TOOL_XY[k]=tuple(v)
   if r['obj']=='wok':K17.set_wok_tilt(r.get('wok_tilt',0.))
   ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in n else {}
   cfg=chain.chain_cfg('SD',**{**LY.BASE,**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**K17.held_cfg(r['obj'],r['grasp_sense'])})
   tree,meta=build(cfg,None);ch=Checker(with_boxes(tree),meta);hit=collections.Counter();first=None
   qs=[(seglab[n][i] or seglab[n][1],q) for i,q in enumerate(r['play'])]+[(f"approach@{a['kf']}",q) for a,aq in zip(r['approaches'],r['approach_qs']) for q in aq]
   for lab,q in qs:
    c=ch.check(np.array(q),full=False,mass=0.);n_states+=1;hs=[h for h in c['hits'] if any(g.startswith('cand_') for g in h['pair'])]
    if hs:
     hit[lab]+=1
     if first is None:first=dict(segment=lab,pair=hs[0]['pair'],gap_mm=hs[0].get('real_gap_mm'))
   res[n]=dict(states=len(qs),hit_segments=dict(hit),first=first)
 else:
  LY.r18b();cfg=chain.chain_cfg('SD',**{**LY.BASE,'r16_tools':{'ladle':None},'r17_lever':0.,'r16_lid':'on','r17_plate2':[.17,K15.PLATE['c'][1],K15.PLATE['c'][2]]})
  tree,meta=build(cfg,None);ch=Checker(with_boxes(tree),meta);e=json.load(open(f"{HUB}/edge_{edge[10:]}.json"));h=0;g=None
  for q in e['qs']:
   c=ch.check(np.array(q),full=False,mass=0.);n_states+=1;hs=[x for x in c['hits'] if any(gg.startswith('cand_') for gg in x['pair'])]
   if hs:
    h+=1
    if g is None:g=dict(pair=hs[0]['pair'],gap_mm=hs[0].get('real_gap_mm'))
  res[edge]=dict(states=len(e['qs']),hit_states=h,first=g)
 out=dict(name=nm,desc=F['desc'],boxes=[dict(name=b,center=np.round(c,3).tolist(),size=np.round(s,4).tolist()) for b,c,s in bx],states=n_states,arm=arms.current(),hub_dir=HUB,
  method='fast checker (full=False) on every stored state; fixture envelope boxes in the scene; hits with the boxes only: a SCREEN-LEVEL replay, not a full check',
  results=res,any_hit=any((v.get('hit_segments') or v.get('hit_states')) for v in res.values()))
 save(f"{OUT}/replay_{nm}{'_'+edge if edge else '_chains'}.json",out);print(nm,edge or 'chains','states',n_states,'any hit',out['any_hit'],json.dumps(res)[:300],flush=True)
if __name__=='__main__':
 if 'ONE' in KV:nm,_,edge=KV['ONE'].partition('|');replay(nm,edge or None);sys.exit()
 names=KV['NAMES'].split(',') if 'NAMES' in KV else list(fixtures())
 if KV.get('MODE','screen')=='screen':screen()
 else:
  scr=json.load(open(f'{OUT}/screen.json'));jobs=[]
  for r in scr['rows']:
   if r['name'] in names:jobs+=[r['name']]+[r['name']+'|'+k for k in r['flagged_segments'] if k.startswith('hub_edge__')]
  from concurrent.futures import ThreadPoolExecutor
  def one(j):
   p=subprocess.run([sys.executable,__file__,f'ONE={j}']+[a for a in sys.argv[1:] if a.startswith(('ARM=','HUBDIR='))],capture_output=True,text=True)
   return (p.stdout.strip().splitlines() or [j+' ERR '+p.stderr[-300:]])[-1]
  with ThreadPoolExecutor(int(KV.get('NPAR',16))) as ex:
   for o in ex.map(one,jobs):print(o,flush=True)
