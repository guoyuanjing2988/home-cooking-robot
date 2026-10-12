"""Recheck all passing route stages under the final cable and stability model."""
import sys
import numpy as np
from scene import H,load,save,build,targets
from checker import Checker
from planner import carry_clear
def replay(label,path,ch,mass):
 rows=[];previous=None
 for q in path:
  q=np.array(q);r=ch.check(q,mass=mass);bound=ch.point_bound.segment_bound(previous,q) if previous is not None else 0.
  carry=True
  if previous is not None and np.max(abs(q[:3]-previous[:3]))>1e-10:
   carry=carry_clear(ch,q) and np.max(abs(q[3:]-previous[3:]))<1e-10
  rows.append(dict(label=label,ok=bool(r['ok'] and carry and bound<=.004+1e-10),tip=r['stability'],clearance=r['clearance'],point_bound_m=bound,hits=r['hits'],mobile=r['mobile']))
  previous=q
 return rows
def main():
 cfg=load('results/selected.json')['config'];_,meta=build(cfg);ts=targets(cfg,meta);rows=[];stages=[]
 for i in range(10):
  r=load(f'results/connections/{i}.json');t=ts[i];tree,meta=build(cfg,t['held']);ch=Checker(tree,meta);mass={'carrot':.12,'holder':.55,'catch_tray':.55}[t['held']]
  for k in ['fold','base_move','unfold']:
   stage=r['planner'][k]
   if not stage['ok']:continue
   rr=replay(f'connection{i}/{k}',stage['path'],ch,mass);rows+=rr;stages.append(dict(label=f'connection{i}/{k}',states=len(rr),pass_=all(x['ok'] for x in rr)))
  print('route replay',i,flush=True)
 idle=load('results/idle.json');tree,meta=build(cfg);ch=Checker(tree,meta)
 for k in ['fold','drive_to_park','drive_from_park','unfold']:
  if idle[k]['ok']:
   rr=replay('idle/'+k,idle[k]['path'],ch,0);rows+=rr;stages.append(dict(label='idle/'+k,states=len(rr),pass_=all(x['ok'] for x in rr)))
 save('results/replay/routes.json',dict(rows=rows,stages=stages,all_pass=all(x['ok'] for x in rows),executed=False))
 print('all passing stages',len(stages),'states',len(rows),'failures',sum(not x['ok'] for x in rows))
if __name__=='__main__':main()
