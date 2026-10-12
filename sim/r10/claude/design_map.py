"""Additional fixed-height design probes: actual sink low space and counter.

These are empty-gripper reach samples, separate from food-task success. No lift
is added on the strength of a collision-limited target.
"""
import sys,numpy as np
from scene import load,save,build
from checker import Checker
from solver import solve
def main():
 cfg=load('results/selected.json')['config'];records=[]
 for height in [.70,.85,1.00]:
  for name,p,approach in [('sink_low',[-.40,.30,.715],[0,0,-1]),('counter_front',[.22,.05,1.10],[0,1,0]),('rear_bowl',[-1.67,.46,1.12],[0,1,0])]:
   c=dict(cfg,mount_height=height);tree,meta=build(c);ch=Checker(tree,meta);target=dict(name=name,points=[p,p],held=None,kind='transfer',force=None,approach=approach)
   print(height,name,flush=True);r=solve(ch,np.array(p),approach,target=target,seed=950+int(height*100))
   save(f'results/maps/{height:.2f}_{name}.json',r);records.append(dict(mount_height_m=height,target=name,point_m=p,ok=r['ok'],starts=r['starts'],counts=r['status_counts'],best=r['best']))
 save('results/reachability.json',dict(station_maps='results/iterations/M01..M11.json',extra_design_probes=records,scope='Finite96-start counter/sink/bowl samples. Design height fixed per model; x,y,yaw sampled and frozen per start. No lift or reachability completeness inferred.'))
if __name__=='__main__':main()
