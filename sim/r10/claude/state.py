"""Transactional conserved food states. No prospective geometry earns execution."""
import copy
import numpy as np
from scene import load,H,variants,build
class World:
 def __init__(self):
  cfg=load('results/selected.json')['config'] if (H/'results/selected.json').exists() else variants()[-1]
  self.config=copy.deepcopy(cfg)
  _,meta=build(cfg);pp=np.array(meta['peeler_origin']);mp=np.array(meta['mandoline_origin'])
  self.objects={p['product']:dict(mass=p['input_mass_kg'],size=p['input_size_m'],pos=meta['raw_objects']['greens' if p['product']=='leafy_greens' else p['product']]['position'],support='raw_tray',state='raw',attached=False,bulk=False) for p in load('assets/process_contract.json')['finished_products']}
  def region(center,half):return [(center-np.array(half)).tolist(),(center+np.array(half)).tolist()]
  self.regions={'peeler':dict(input=region(pp+[0,-.045,.09],[.10,.045,.055]),output=region(pp+[0,-.045,.09],[.10,.045,.055]),scrap=region(pp+[0,-.045,.035],[.13,.075,.015])), 'mandoline':dict(input=region(mp+[0,0,.15],[.185,.06,.10]),output=region(mp+[0,0,.024],[.154,.074,.016]),scrap=region(mp+[0,0,.024],[.154,.074,.016]))}
  self.events=[];self.executed_connections=0
 def snapshot(self):return dict(objects=copy.deepcopy(self.objects),total_mass_kg=sum(o['mass'] for o in self.objects.values()),events=copy.deepcopy(self.events),executed_connections=self.executed_connections)
 def transform(self,name,operation,station,region,duration,edible_fraction=1,packing=.60):
  old=copy.deepcopy(self.objects);o=old[name]
  capabilities={'peeler':{'peeled'},'mandoline':{'slices'}}
  if operation not in capabilities.get(station,set()):raise ValueError('operation incompatible with station')
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
  # Whole transaction rejects overlapping bulk allocations; no shared slice/
  # scrap region silently hides the missing mechanical scrap route.
  allocated=[v for v in old.values() if v.get('bulk') and v['support']==station]
  for i,a in enumerate(allocated):
   for b in allocated[i+1:]:
    overlap=(np.array(a['size'])+b['size'])/2-abs(np.array(a['pos'])-b['pos'])
    if np.all(overlap>1e-10):raise ValueError('aggregate food/scrap overlap')
  if abs(sum(x['mass'] for x in old.values())-.57)>1e-9:raise ValueError('mass not conserved')
  self.objects=old;self.events.append(dict(object=name,operation=operation,station=station,duration_s=duration,food_mass_kg=mass,scrap_mass_kg=scrap))
 def attach(self,name,pose):
  o=self.objects[name]
  if o['bulk'] or any(x['attached'] for x in self.objects.values()):raise ValueError('invalid attachment')
  if np.linalg.norm(np.array(pose)-o['pos'])>1e-8:raise ValueError('binding teleport')
  o['attached']=True;o['support']='robot'
 def commit_path(self,name,path_result,positions=None,*,checker=None,start_q=None,kind='transfer',target=None,rotation=None):
  # Caller-supplied OK flags and Cartesian positions are never certificates.
  # Recompile authoritative scene, replay all geometry/load/stability gates,
  # verify start continuity and every <=4mm bound, and derive final FK here.
  import mujoco
  from checker import Checker
  if positions is not None:raise ValueError('caller Cartesian positions forbidden')
  if type(checker) is not Checker or start_q is None:raise ValueError('authoritative checker and continuity required')
  if not path_result.get('ok') or not self.objects[name]['attached']:raise ValueError('unreplayed or unattached')
  if checker.meta.get('held')!=name:raise ValueError('attachment identity mismatch')
  cfg=checker.meta['config'];tree,meta=build(cfg,name);ch=Checker(tree,meta)
  if cfg!=self.config:raise ValueError('scene differs from state authority')
  if target is not None:
   if rotation is None:raise ValueError('stroke orientation missing')
   from scene import targets
   if target not in targets(cfg,meta):raise ValueError('forged stroke target')
   if kind!=target['kind']:raise ValueError('path kind differs from authorized stroke')
   ch.configure_target(target,np.array(rotation))
  elif kind!='transfer':raise ValueError('working target missing')
  qs=np.asarray(path_result.get('path'),float)
  if qs.ndim!=2 or qs.shape[1]!=ch.m.nq or len(qs)<2 or not np.all(np.isfinite(qs)):raise ValueError('invalid joint array')
  if np.max(abs(qs[0]-np.asarray(start_q)))>1e-9:raise ValueError('start discontinuity')
  # Last committed joint state, once established, is authoritative as well.
  if hasattr(self,'q') and np.max(abs(qs[0]-self.q))>1e-9:raise ValueError('state discontinuity')
  before=self.snapshot();o=self.objects[name]
  ch.d.qpos[:]=qs[0];mujoco.mj_forward(ch.m,ch.d);sid=ch.m.site('R_prep').id
  if np.linalg.norm(ch.d.site_xpos[sid]-o['pos'])>1e-8:raise ValueError('food FK start mismatch')
  for i,q in enumerate(qs):
   if i and ch.point_bound.segment_bound(qs[i-1],q)>.004+1e-12:raise ValueError('point displacement exceeds4mm')
   if i and np.max(abs(q[:3]-qs[i-1,:3]))>1e-10:
    from planner import carry_clear
    if np.max(abs(q[3:]-qs[i-1,3:]))>1e-10 or not carry_clear(ch,q) or not carry_clear(ch,qs[i-1]):raise ValueError('base moved without frozen safe carry')
   if kind=='working' and np.max(abs(q[:3]-qs[0,:3]))>1e-10:raise ValueError('base not frozen')
   r=ch.check(q,kind=kind,mass=o['mass'],force=target['force'] if target else None)
   if not r['ok']:raise ValueError('unchecked/rejected state')
   if target:
    p=ch.d.site_xpos[sid];a,b=np.array(target['points']);v=b-a;s=np.clip((p-a)@v/max(v@v,1e-12),0,1)
    pe,re=ch.pose_error(q,a+s*v,np.array(rotation))
    if pe>.005 or re>np.deg2rad(3):raise ValueError('stroke pose gate')
  o['pos']=ch.d.site_xpos[sid].tolist();self.q=qs[-1].copy();self.executed_connections+=1