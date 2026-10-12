"""Transactional conserved food states. No prospective geometry earns execution."""
import copy
import numpy as np
from scene import load,H,variants,build
class World:
 def __init__(self):
  cfg=load('results/selected.json')['config'] if (H/'results/selected.json').exists() else variants()[-1]
  _,meta=build(cfg);pp=np.array(meta['peeler_origin']);mp=np.array(meta['mandoline_origin'])
  self.objects={p['product']:dict(mass=p['input_mass_kg'],size=p['input_size_m'],pos=meta['raw_objects']['greens' if p['product']=='leafy_greens' else p['product']]['position'],support='raw_tray',state='raw',attached=False,bulk=False) for p in load('assets/process_contract.json')['finished_products']}
  def region(center,half):return [(center-np.array(half)).tolist(),(center+np.array(half)).tolist()]
  self.regions={'peeler':dict(input=region(pp+[0,-.045,.09],[.10,.045,.055]),output=region(pp+[0,-.045,.09],[.10,.045,.055]),scrap=region(pp+[0,-.045,.035],[.13,.075,.015])), 'mandoline':dict(input=region(mp+[0,0,.15],[.185,.06,.10]),output=region(mp+[0,0,.024],[.154,.074,.016]),scrap=region(mp+[0,0,.024],[.154,.074,.016]))}
  self.events=[];self.executed_connections=0
 def snapshot(self):return dict(objects=copy.deepcopy(self.objects),total_mass_kg=sum(o['mass'] for o in self.objects.values()),events=copy.deepcopy(self.events),executed_connections=self.executed_connections)
 def transform(self,name,operation,station,region,duration,edible_fraction=1,packing=.60):
  old=copy.deepcopy(self.objects);o=old[name]
  if operation not in ('washed','peeled','slices','sections','wedges'):raise ValueError('unknown operation')
  if o['attached'] or o['support']!=station:raise ValueError('real station ownership required')
  if duration is not None and duration<0:raise ValueError('negative duration')
  if station not in self.regions or not np.allclose(region,self.regions[station]['input'],atol=1e-10,rtol=0):raise ValueError('forged or unknown physical station region')
  low,high=np.array(region[0]),np.array(region[1]);p=np.array(o['pos']);half=np.array(o['size'])/2
  if np.any(p-half<low) or np.any(p+half>high):raise ValueError('full food not contained')
  if not 0<edible_fraction<=1 or not 0<packing<=1:raise ValueError('mass or packing')
  mass=o['mass']*edible_fraction;scrap=o['mass']-mass
  if operation in ('slices','sections','wedges'):
   low,high=map(np.array,self.regions[station]['output'])
   size=np.array([.14,.10,mass/(1000*packing*.14*.10)])
   if np.any(size>high-low):raise ValueError('bulk overflow')
   o.update(size=size.tolist(),pos=((low+high)/2).tolist(),bulk=True)
  o.update(mass=mass,state=operation)
  if scrap:
   sl,sh=map(np.array,self.regions[station]['scrap'])
   old[name+':scrap:'+station]=dict(mass=scrap,size=[.10,.10,scrap/(400*.01)],pos=((sl+sh)/2).tolist(),support=station,state='scrap',attached=False,bulk=True)
   s=old[name+':scrap:'+station]
   if np.any(np.array(s['size'])>sh-sl):raise ValueError('scrap overflow')
  if abs(sum(x['mass'] for x in old.values())-.57)>1e-9:raise ValueError('mass not conserved')
  self.objects=old;self.events.append(dict(object=name,operation=operation,station=station,duration_s=duration,food_mass_kg=mass,scrap_mass_kg=scrap))
 def attach(self,name,pose):
  o=self.objects[name]
  if o['bulk'] or any(x['attached'] for x in self.objects.values()):raise ValueError('invalid attachment')
  if np.linalg.norm(np.array(pose)-o['pos'])>1e-8:raise ValueError('binding teleport')
  o['attached']=True;o['support']='robot'
 def commit_path(self,name,path_result,positions):
  if not path_result['ok'] or len(positions)!=len(path_result['path']):raise ValueError('unreplayed path')
  if not self.objects[name]['attached']:raise ValueError('not attached')
  self.objects[name]['pos']=list(positions[-1]);self.executed_connections+=1
def regression():
 w=World();tests={};before=w.snapshot()
 cases=[('remote_transform',lambda:w.transform('carrot','slices','mandoline',[[0,0,0],[1,1,1]],1)),('teleport',lambda:w.attach('carrot',[9,9,9]))]
 for n,call in cases:
  try:call();tests[n]=False
  except ValueError:tests[n]=w.snapshot()==before
 # Successful contained transformation and transactional rollback probes are
 # synthetic state-machine unit tests, never represented as robot execution.
 w=World();region=w.regions['peeler']['input'];center=np.mean(region,axis=0).tolist();o=w.objects['carrot'];o.update(pos=center,support='peeler')
 w.transform('carrot','peeled','peeler',region,2823.529,.9)
 tests['contained_peel_mass_conserved']=abs(w.snapshot()['total_mass_kg']-.57)<1e-12
 for label,mutate,args in [
  ('partial_input_outside',lambda:o.update(pos=(np.array(center)+[.09,0,0]).tolist()),('carrot','slices','peeler',region,1)),
  ('held_transform',lambda:o.update(pos=center,attached=True),('carrot','slices','peeler',region,1)),
  ('unknown_transform',lambda:o.update(attached=False),('carrot','imaginary','peeler',region,1)),
  ('negative_duration',lambda:None,('carrot','slices','peeler',region,-1))]:
  o=w.objects['carrot'];mutate();before=w.snapshot()
  try:w.transform(*args);tests[label]=False
  except ValueError:tests[label]=w.snapshot()==before
 o=w.objects['carrot'];o.update(pos=center,attached=False)
 before=w.snapshot()
 try:w.transform('carrot','slices','peeler',region,1,packing=.00001);tests['bulk_overflow']=False
 except ValueError:tests['bulk_overflow']=w.snapshot()==before
 # Slices need the real larger catch-tray output; peeler is never relabelled a
 # remote collector. Synthetic relocation here is test setup only.
 o.update(pos=np.mean(w.regions['mandoline']['input'],axis=0).tolist(),support='mandoline')
 w.transform('carrot','slices','mandoline',w.regions['mandoline']['input'],1)
 before=w.snapshot()
 try:w.attach('carrot',w.objects['carrot']['pos']);tests['bulk_direct_grasp']=False
 except ValueError:tests['bulk_direct_grasp']=w.snapshot()==before
 w=World();w.objects['carrot'].update(pos=[9,9,9],support='peeler');before=w.snapshot()
 try:w.transform('carrot','peeled','peeler',[[8,8,8],[10,10,10]],1);tests['forged_station_region']=False
 except ValueError:tests['forged_station_region']=w.snapshot()==before
 return tests
