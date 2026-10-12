"""Foreground numerical chunks; use bounded.py as the parent resource guard."""
import sys,time,csv,xml.etree.ElementTree as E
import numpy as np,mujoco
from scene import H,variants,build,targets,save,load
from checker import Checker
from solver import solve
def packing(ch):
 # Environment-to-environment collisions are never inferred to be OK merely
 # because the robot checker correctly ignores them. Native penetration screen.
 mujoco.mj_forward(ch.m,ch.d);hits=[]
 def owner(n):
  if n.startswith('raw_'):return 'raw'
  b=ch.m.geom_bodyid[ch.gnames.index(n)]
  while ch.m.body_parentid[b]:b=ch.m.body_parentid[b]
  return ch.m.body(b).name if b else n
 for c in ch.d.contact[:ch.d.ncon]:
  a,b=map(int,c.geom)
  if ch.robot[a] or ch.robot[b] or c.dist>=-1e-6:continue
  na,nb=ch.gnames[a],ch.gnames[b];oa,ob=owner(na),owner(nb)
  if oa==ob:continue
  if any(n.startswith(('counter_','north_cabinet','sink_','stove','protected_stove','upper_cabinet','south_','faucet_','r07_closed')) for n in (na,nb)) and all(n.startswith(('counter_','north_cabinet','sink_','stove','protected_stove','upper_cabinet','south_','faucet_','r07_closed','outlet_')) for n in (na,nb)):continue
  hits.append(dict(pair=[na,nb],owners=[oa,ob],penetration_mm=float(-c.dist*1000)))
 # Native collision masks intentionally suppress environment/environment pairs.
 # Explicit convex queries therefore check every new station against its peers
 # and the kitchen. A zero GJK upper witness denotes intersection/touch, never
 # a signed depth; native distance supplies a diagnostic only.
 env=[g for g in range(ch.m.ngeom) if not ch.robot[g] and ch.m.geom_type[g]!=0]
 lo={};hi={}
 for g in env:
  lo[g]=np.array([ch.bounds.support(g,-a)[k] for k,a in enumerate(np.eye(3))]);hi[g]=np.array([ch.bounds.support(g,a)[k] for k,a in enumerate(np.eye(3))])
 added=('mandoline_station','peeler_station','greens_station','tomato_station','wash_basket','stored_bowl_')
 for i,a in enumerate(env):
  na=ch.gnames[a];oa=owner(na)
  for b in env[i+1:]:
   nb=ch.gnames[b];ob=owner(nb)
   if oa==ob or not any(x.startswith(added) for x in (oa,ob)):continue
   overlap=np.minimum(hi[a],hi[b])-np.maximum(lo[a],lo[b])
   if min(overlap)<1e-5:continue
   gap=ch.bounds.pair(a,b)
   if gap['upper_m']<1e-6:
    native=float(mujoco.mj_geomDistance(ch.m,ch.d,a,b,.01,None))
    hits.append(dict(pair=[na,nb],owners=[oa,ob],convex_intersection=True,aabb_overlap_mm=(overlap*1000).tolist(),native_signed_mm=native*1000,reason='Intersecting complete fixed solids; support-face touching removed by strict AABB overlap test'))
 return hits
def station_audit(ch,meta):
 # Full shell support extents versus sink inner rectangle and jet ray.
 mouth=np.array(meta['wash_mouth']);jet=np.array(meta['jet']);normal=np.array(meta['wash_normal']);delta=mouth-jet
 ray_t=float(delta@normal/np.dot([0,0,-1],normal));intersection=jet+ray_t*np.array([0,0,-1])
 radial=float(np.linalg.norm(intersection-mouth));basket=[i for i,n in enumerate(ch.gnames) if n.startswith('wash_basket')]
 ext=[]
 for g in basket:
  ext.append(([float(ch.bounds.support(g,-axis)[k]) for k,axis in enumerate(np.eye(3))],[float(ch.bounds.support(g,axis)[k]) for k,axis in enumerate(np.eye(3))]))
 return dict(jet_axis_xy_m=jet[:2].tolist(),mouth_center_m=mouth.tolist(),radial_offset_mm=radial*1000,ray_distance_m=ray_t,jet_hits_opening=bool(ray_t>=0 and radial<.118),basket_aabb_m=[np.min([e[0] for e in ext],axis=0).tolist(),np.max([e[1] for e in ext],axis=0).tolist()],packing_hits=packing(ch))
def iteration(index):
 cfg=variants()[index];tree,meta=build(cfg);ch=Checker(tree,meta);audit=station_audit(ch,meta);probes=[]
 tree.write(H/'models'/f'{cfg["id"]}.xml',encoding='unicode')
 # Reach map is per real station corridor and includes ALL four fixed stations.
 for label in ['wash_load','peel_load','mandoline_work']:
  target=next(t for t in targets(cfg,meta) if t['name']==label);ht,hm=build(cfg,target['held']);hc=Checker(ht,hm)
  ht.write(H/'models'/f'{cfg["id"]}_{label}.xml',encoding='unicode')
  print(cfg['id'],label,'96 starts',flush=True)
  r=solve(hc,np.array(target['points'][0]),target['approach'],seed=800+index,target=target)
  save(f'results/iterations/{cfg["id"]}_{label}.json',r)
  probes.append(dict(target=label,ok=r['ok'],starts=r['starts'],counts=r['status_counts'],best=r['best'],elapsed_s=r['elapsed_s']))
 out=dict(config=cfg,audit=audit,probes=probes,clear_samples=sum(x['ok'] for x in probes),total_samples=len(probes),kind='full-scene corridor reach map; not executed strokes')
 save(f'results/iterations/{cfg["id"]}.json',out)
 rows=[]
 for c in variants():
  p=H/f'results/iterations/{c["id"]}.json'
  if p.exists():
   r=load(str(p.relative_to(H)));rows.append(dict(iteration=c['id'],change=c['change'],clear_samples=r['clear_samples'],samples=r['total_samples'],starts=sum(x['starts'] for x in r['probes']),jet_hits=r['audit']['jet_hits_opening'],packing_penetrations=len(r['audit']['packing_hits']),evidence=str(p.relative_to(H))))
 with (H/'results/iterations.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 print(cfg['id'],'complete',out['clear_samples'],'/',len(probes),'packing',len(audit['packing_hits']),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='iteration':iteration(int(sys.argv[2])-1)
