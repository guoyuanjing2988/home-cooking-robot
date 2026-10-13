"""R19 #5: the binding re-check of a cup chain (results/r19/cups/chain_*.json from r19cupchain.py). New file.

As r19smooth.py's baseline re-check: the stored states (`play`; the grasp approach / release retreats
`approach_qs` each on their own) are joined joint-linearly, the arm joints unwrapped first (a 2*pi label
jump is the same pose; the unwrapped values must stay inside the joint ranges, else the jump is kept and
reported), and subdivided so that no robot or held point moves more than 4 mm between consecutive checked
states (point_bound.PointBound.segment_bound). Every state gets Checker.check(full=True): MuJoCo contacts +
the GJK lower-bound certificate, 10 mm robot-environment / 5 mm gripper-held-environment, joint ranges; and
the R15 plume rule (kitchen19seas.plume_model, unless the chain ran with PLUME=0).
The chain's own scene is rebuilt from its stored cfg (r19.cfg_held / r19.cfg_approach and r19.k_state).
python r19cupw_recheck.py <chain json> [WORKERS=12] -> <chain>_recheck.json"""
import sys,os,json,math,time
sys.path.insert(0,'.')
import numpy as np
STEP=.004
_CTX={}
def setup(cfg,kst,plume_m):
 import kitchen16 as K,kitchen19seas as S
 S.setup_kitchen();K.set_design(**kst['design'])
 for k,v in kst['tool_xy'].items():K.TOOL_XY[k]=tuple(v)
 K.SPAT_ELEV,K.SPAT_YAW,K.SPAT_ROLL=kst['spat_elev'],kst['spat_yaw'],kst['spat_roll']
 import chain
 from scene import build
 from checker import Checker
 c=chain.chain_cfg('SD',**cfg);tree,meta=build(c,None);S.add(tree,c);S.meshheld(tree);ch=Checker(tree,meta)
 return ch,(S.plume_model(tree,plume_m) if plume_m>0 else None)
def _init(cfg,kst,plume_m):_CTX['ch'],_CTX['pl']=setup(cfg,kst,plume_m)
def _work(Q):
 ch,pl=_CTX['ch'],_CTX['pl'];out=[]
 for q in Q:
  c=ch.check(np.asarray(q),full=True,mass=0.);rv={k:v['reserve_mm'] for k,v in c['clearance'].items()}
  out.append(dict(hits=[h['pair'] for h in c['hits']][:2],ranges=bool(c['ranges']),res=min([v for k,v in rv.items() if k!='self'],default=1e9),self_mm=rv.get('self',1e9),plume=None if pl is None else pl(np.asarray(q))))
 return out
def unwrap(Q,ch):
 U=np.array(Q,float).copy();U[:,3:9]=np.unwrap(U[:,3:9],axis=0)
 lo=ch.m.jnt_range[[ch.m.jnt_qposadr.tolist().index(i) for i in range(3,9)],0];hi=ch.m.jnt_range[[ch.m.jnt_qposadr.tolist().index(i) for i in range(3,9)],1]
 ok=bool(np.all(U[:,3:9]>=lo-1e-9) and np.all(U[:,3:9]<=hi+1e-9));jumps=int(np.sum(np.abs(np.round((U[:,3:9]-np.array(Q)[:,3:9])/(2*np.pi)))>0))
 return (U if ok else np.array(Q,float)),ok,jumps
def sample(Q,pb):
 out=[Q[0]];sp=[]
 for i in range(len(Q)-1):
  b=pb.segment_bound(Q[i],Q[i+1]);n=max(1,int(math.ceil(b/STEP)))
  for k in range(1,n+1):out.append(Q[i]+(Q[i+1]-Q[i])*k/n)
  sp.append(b/n)
 return np.array(out),max(sp) if sp else 0.
def run(cfg,kst,plume_m,Q,workers,label):
 from multiprocessing import Pool
 ch,_=setup(cfg,kst,plume_m);U,ok,jumps=unwrap(Q,ch);S_,spmax=sample(U,ch.point_bound)
 chunks=[S_[i:i+40].tolist() for i in range(0,len(S_),40)];rs=[]
 with Pool(workers,initializer=_init,initargs=(cfg,kst,plume_m)) as pool:
  for r in pool.map(_work,chunks):rs+=r
 hit=[i for i,r in enumerate(rs) if r['hits'] or not r['ranges']];pls=[r['plume'] for r in rs if r['plume'] is not None]
 return dict(label=label,stored_states=len(Q),checked_states=len(rs),max_spacing_mm=round(spmax*1000,3),unwrapped=ok,label_jumps_2pi=jumps,
  hit_states=len(hit),first_hits=[(i,rs[i]['hits'],rs[i]['ranges']) for i in hit[:5]],min_reserve_mm=round(min(r['res'] for r in rs),2),min_self_mm=round(min(r['self_mm'] for r in rs),2),
  min_plume_mm=None if not pls else round(min(pls),1),plume_bad_states=sum(1 for p in pls if p<0))
if __name__=='__main__':
 fn=sys.argv[1];KV=dict(a.split('=',1) for a in sys.argv[2:]);W=int(KV.get('WORKERS',12));t0=time.monotonic()
 r=json.load(open(fn));x=r['r19'];kst=x['k_state'];out={}
 out['play']=run(x['cfg_held'],kst,x['plume_m'],r['play'],W,'play (held cup)');print(json.dumps(out['play']),flush=True)
 for i,(aq,cfg) in enumerate(zip(r.get('approach_qs') or [],x['cfg_approach'])):
  if aq:out[f'approach_{i}']=run(cfg,kst,x['plume_m'],aq,W,f'approach {i} (empty gripper, cup in its slot)');print(json.dumps(out[f'approach_{i}']),flush=True)
 tot=dict(ok=all(v['hit_states']==0 and v['plume_bad_states']==0 for v in out.values()),checked_states=sum(v['checked_states'] for v in out.values()),
  min_reserve_mm=min(v['min_reserve_mm'] for v in out.values()),min_plume_mm=min([v['min_plume_mm'] for v in out.values() if v['min_plume_mm'] is not None],default=None),
  max_spacing_mm=max(v['max_spacing_mm'] for v in out.values()),elapsed_s=round(time.monotonic()-t0,1))
 from scene import save
 save(fn[:-5]+'_recheck.json',dict(chain=fn,method=__doc__,total=tot,parts=out));print('RECHECK',json.dumps(tot))
