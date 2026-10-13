"""R19 pot zone (GitHub #37, #8): the binding <= 4 mm re-check of a chain in the pot-zone layout. New file.

As r19enc_check.py recheck / r19enc_adopt.py: the stored play (2pi-unwrapped, joint-linear between stored states,
cut so that the point bound between consecutive states is <= 4 mm, r19smooth.sample_poly) and each grasp approach /
release retreat (approach_qs, empty gripper, the object in the world as r17chain's GR worlds) go state by state
through Checker.check(full=True): MuJoCo contacts + the GJK lower-bound certificate, 10 mm robot-environment,
5 mm gripper / held-environment, self, joint ranges. Unchanged checker and gates. Scene: the R18b layout of
r19enc_check.py (plating spot PY, spatula on its rest left of the sink, ladle off) with the kitchen19pot layer:
the spider rest from the chain's own tool_xy, and RACK=keyed the keyed lid rack. For a lid chain with RACK=keyed the
declared insertion window (kitchen19pot.window()) is attached to its checker: in window states the held lid parts
vs the rack parts are the intended contact (Checker.permissions), nothing else changes; window states are counted.
python r19pot_check.py <chain json>[,<chain json>...] [RACK=keyed] [POTWIN=1] [SPX= SPY=] ARM=ur5e_enc2_pgc PY=.15 [WORKERS=16]
 -> results/r19/pot/check_<chain name>[_rack].json"""
import sys,os,json,time,math
sys.path.insert(0,'.')
import numpy as np
KV=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
FILES=[a for a in sys.argv[1:] if '=' not in a][0].split(',') if any('=' not in a for a in sys.argv[1:]) else []
import kitchen19pot as P
if KV.get('RACK')=='keyed':P.install(rack='keyed')
import checker as _chk
_orig_perm=_chk.Checker.permissions
def _perm(self,kind):
 allowed=_orig_perm(self,kind);Ws=getattr(self,'_r19pot_wins',None);self._r19pot_in=0
 if Ws:
  sid=self.m.site('R_prep').id;add,n=P.allowed_pairs(Ws,self.gnames,self.d.site_xpos[sid],self.d.site_xmat[sid].reshape(3,3))
  if n:allowed=set(allowed)|add;self._r19pot_in=n
 return allowed
_chk.Checker.permissions=_perm
BASE=dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True)
APP_WORLDS=dict(wok=lambda n:{0:{'r17_lever':30.},n-1:{'r17_lever':30.}},lever=lambda n:{0:{'r17_lever':0.},1:{'r17_lever':30.}},
 lid=lambda n:{0:{'r16_lid':'on'},n-1:{'r16_lid':'rack'}},spider=lambda n:{0:{},n-1:{}},spatula_b=lambda n:{0:{}})
def J(f):return json.load(open(f,encoding='utf-8'))
_CTX={}
def ctx(f,part):
 if (f,part) in _CTX:return _CTX[(f,part)]
 import chain,kitchen15 as K15,kitchen16 as K,kitchen17 as K17
 from scene import build
 from checker import Checker
 from r19enc_check import meshheld
 r=J(f);py=float(KV['PY']) if 'PY' in KV else r.get('plate_y')
 if py is not None:K15.PLATE['c'][1]=py
 K.set_design(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K17.set_wok_tilt(float(r.get('wok_tilt') or 0.))
 for k,v in r.get('tool_xy',{}).items():K.TOOL_XY[k]=tuple(v)
 if 'SPX' in KV:K.TOOL_XY['spider']=(float(KV['SPX']),float(KV['SPY']))   # the spider rest of the layout under test (else the chain's own)
 K.TOOL_XY['spatula']=(-1.15,.30);K.SPAT_ELEV=8.;K.SPAT_YAW=0.;K.SPAT_ROLL=180.
 ex={'r17_plate2':[.43,K15.PLATE['c'][1],K15.PLATE['c'][2]]} if 'plate2' in os.path.basename(f) else {}
 if part=='play':world=K17.held_cfg(r['obj'],r['grasp_sense'])
 else:k=int(part[3:]);world=APP_WORLDS.get(r['obj'],lambda n:{})(len(r['keyframes'])).get(r['approaches'][k]['kf'],{})
 cfg=chain.chain_cfg('SD',**{**BASE,**r.get('scene',{}),**ex,'r16_tools':{'ladle':None},**world});tree,meta=build(cfg,None);meshheld(tree);ch=Checker(tree,meta)
 if part=='play' and r['obj']=='lid':ch._r19pot_wins=P.windows(r['grasp_sense'],rack=KV.get('RACK')=='keyed',pot=KV.get('POTWIN')=='1')
 _CTX[(f,part)]=ch;return ch
def states(f,part):
 import r19smooth as S
 r=J(f);ch=ctx(f,part);Q=r['play'] if part=='play' else r['approach_qs'][int(part[3:])]
 X,src,sp=S.sample_poly(S.unwrap(np.array(Q,float)),S.FastBound(ch));return X,sp
def work(args):
 f,part,Q=args;ch=ctx(f,part);out=[]
 for q in Q:
  c=ch.check(np.asarray(q),full=True,mass=0.)
  cl={k:(round(v['reserve_mm'],3),v['pair']) for k,v in c['clearance'].items()}
  out.append(dict(hits=[h['pair'] for h in c['hits']][:3],ranges=bool(c['ranges']),cl=cl,win=bool(getattr(ch,'_r19pot_in',False))))
 return out
def main():
 import multiprocessing as mp
 W=int(KV.get('WORKERS',16));os.makedirs('results/r19/pot',exist_ok=True)
 for f in FILES:
  t0=time.monotonic();r=J(f);parts=['play']+[f'app{k}' for k,a in enumerate(r['approach_qs']) if a]
  jobs=[];meta={}
  for part in parts:
   X,sp=states(f,part);meta[part]=dict(states=len(X),max_step_bound_mm=round(sp*1e3,3))
   n=max(1,math.ceil(len(X)/(W*3)));jobs+=[(f,part,X[i:i+n].tolist()) for i in range(0,len(X),n)]
  with mp.Pool(W,maxtasksperchild=4) as pool:res=pool.map(work,jobs,chunksize=1)
  rows={p:[] for p in parts}
  for (ff,part,_),o in zip(jobs,res):rows[part]+=o
  rep={}
  for part in parts:
   R=rows[part];hit=[i for i,x in enumerate(R) if x['hits'] or not x['ranges']];cats={}
   for x in R:
    for k,(v,pr) in x['cl'].items():
     if k not in cats or v<cats[k]['reserve_mm']:cats[k]=dict(reserve_mm=v,pair=pr)
   rep[part]=dict(**meta[part],hit_states=len(hit),hit_pairs=sorted({tuple(p) for i in hit[:50] for p in R[i]['hits']})[:6],out_of_range=sum(not x['ranges'] for x in R),
    window_states=sum(x['win'] for x in R),min_reserve_by_category=cats,
    min_env_reserve_mm=min([v['reserve_mm'] for k,v in cats.items() if k!='self'],default=None))
  ok=all(v['hit_states']==0 for v in rep.values())
  out=dict(file=f,ok=ok,spider_rest=list(__import__('kitchen16').TOOL_XY['spider']),arm=os.environ.get('ARM') or next((a[4:] for a in sys.argv if a.startswith('ARM=')),'ur5e'),rack=KV.get('RACK'),tool_xy=r.get('tool_xy'),
   windows=[{k:(v.tolist() if hasattr(v,'tolist') else v) for k,v in W.items()} for W in (P.windows(r['grasp_sense'],rack=KV.get('RACK')=='keyed',pot=KV.get('POTWIN')=='1') if r['obj']=='lid' else [])],parts=rep,elapsed_s=round(time.monotonic()-t0),method=__doc__)
  fn=f"results/r19/pot/check_{os.path.basename(f)[:-5]}{'_rack' if KV.get('RACK')=='keyed' else ''}{'_potwin' if KV.get('POTWIN')=='1' else ''}{'_sp%s_%s'%(KV['SPX'],KV['SPY']) if 'SPX' in KV else ''}.json";json.dump(out,open(fn,'w'),indent=1,default=float)
  print(fn,'ok',ok,'elapsed',out['elapsed_s'],flush=True)
  for p,v in rep.items():print('  ',p,v['states'],'states, step',v['max_step_bound_mm'],'mm, hits',v['hit_states'],v['hit_pairs'][:2],'window',v['window_states'],'min env',v['min_env_reserve_mm'],{k:(c['reserve_mm'],c['pair']) for k,c in v['min_reserve_by_category'].items()},flush=True)
if __name__=='__main__':main()
