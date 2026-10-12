"""Include all admitted selected-design reach-map poses in final audit."""
import numpy as np
from scene import H,load,save,build,targets
from checker import Checker,reference
def main():
 cfg=load('results/selected.json')['config'];_,meta=build(cfg);ts=targets(cfg,meta);rows=[]
 inputs=[]
 for label in ['wash_load','peel_load','mandoline_work']:
  t=next(x for x in ts if x['name']==label);inputs.append((f'M11/{label}',f'results/iterations/M11_{label}.json',t))
 for probe in load('results/reachability.json')['extra_design_probes']:
  if probe['mount_height_m']!=cfg['mount_height']:continue
  name=probe['target'];approach=[0,0,-1] if name=='sink_low' else [0,1,0]
  t=dict(name=name,points=[probe['point_m']]*2,held=None,force=None,kind='transfer',approach=approach)
  inputs.append((f'design/.85/{name}',f'results/maps/0.85_{name}.json',t))
 for label,path,t in inputs:
  tree,meta=build(cfg,t['held']);ch=Checker(tree,meta);mass={'carrot':.12,'holder':.55,None:0}[t['held']]
  app=t['approach'];jaws=([(0,0,1),(0,0,-1),(1,0,0),(-1,0,0)] if abs(app[1])>.9 else [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)])
  for old in load(path)['rows']:
   if old['status']!='ok':continue
   R=reference.rotation(app,jaws[old['start']%4]);ch.configure_target(t,R);q=old['q'];r=ch.check(q,kind=t['kind'],force=t['force'],mass=mass);pe,re=ch.pose_error(q,np.array(t['points'][0]),R)
   rows.append(dict(label=label,q=q,ok=bool(r['ok'] and pe<=.005 and re<=np.deg2rad(3)),tip=r['stability'],clearance=r['clearance'],load=r['load'],hits=r['hits'],mobile=r['mobile']))
  print('map replay',label,flush=True)
 save('results/replay/maps.json',dict(rows=rows,all_pass=all(x['ok'] for x in rows),scope='All selectedM11 and identical.85m-design accepted map poses; earlier geometries are not final admissions'))
 print('map states',len(rows),'failures',sum(not x['ok'] for x in rows))
if __name__=='__main__':main()
