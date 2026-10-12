"""Station-local containment transactions. No name-only transformation permit."""
import copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from distance import Bounds

def install(p):
 v=p.v
 def regions(self,station):
  if station=='BFP610_processing_bowl':
   mujoco.mj_forward(self.base.m,self.base.d)
   gid=self.base.m.geom('bfp610_complete_envelope').id;center=self.base.d.geom_xpos[gid].copy();rot=self.base.d.geom_xmat[gid].reshape(3,3).copy();half=self.base.m.geom_size[gid].copy()
   # The unchanged full OEM exterior reservation is the necessary input
   # containment boundary. A conservative1.92L modeled bowl cavity is
   # nested inside it; its exact OEM shape/access remains unqualified.
   cavity=center+rot@np.array([0,0,.0325]);output=dict(center=cavity,rotation=rot,half=np.array([.08,.06,.05]))
   input_=dict(center=center,rotation=rot,half=half-.010)
   basis='Unchanged395x295x395mm exterior,10mm inner inset; declared160x120x100mm1.92L bowl subregion. Exact regional OEM cavity/access geometry not qualified.'
  elif station=='linear_peeler_holder':
   x,y,_=v.cfg['station_frames']['peel']['new_center'];input_=dict(center=np.array([x,y,1.0075]),rotation=np.eye(3),half=np.array([.17,.075,.1175]));output=input_;basis='Custom full guard interior and full holder; top below retained open lid.'
  elif station=='secondary_work_face':
   x,y,_=v.cfg['station_frames']['secondary']['new_center'];input_=dict(center=np.array([x,y,1.005]),rotation=np.eye(3),half=np.array([.14,.115,.065]));output=dict(center=np.array([x,y,.985]),rotation=np.eye(3),half=np.array([.10,.075,.035]));basis='Declared custom guarded station interior; full guard/fixture solids retained.'
  else:raise ValueError('Unknown geometric station interior: '+station)
  x,y,_=v.cfg['station_frames']['peel']['new_center'];scrap=dict(center=np.array([x,y,.915]),rotation=np.eye(3),half=np.array([.175,.085,.045])) if station=='linear_peeler_holder' else copy.deepcopy(output)
  return dict(input=input_,output=output,scrap=scrap,basis=basis,container_identity=station,interior_qualified=False)

 def contains(body,pose,region):
  root=E.Element('mujoco');E.SubElement(root,'compiler',angle='radian');world=E.SubElement(root,'worldbody');b=copy.deepcopy(body);p.put(b,pose);world.append(b);m=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_forward(m,d);bounds=object.__new__(Bounds);bounds.m=m;bounds.d=d;bounds.local={};c=region['center'];r=region['rotation'];half=region['half'];lo=np.full(3,np.inf);hi=-lo
  for g in range(m.ngeom):
   for j in range(3):
    axis=r[:,j];lo[j]=min(lo[j],float(axis@(bounds.support(g,-axis)-c)));hi[j]=max(hi[j],float(axis@(bounds.support(g,axis)-c)))
  margins=np.r_[lo+half,half-hi];return dict(pass_=bool(np.min(margins)>=-1e-9),minimum_containment_margin_m=float(np.min(margins)),local_min_m=lo.tolist(),local_max_m=hi.tolist(),region_center_m=c.tolist(),region_rotation=r.tolist(),region_half_m=half.tolist())

 def transform(self,product,kind,station,duration_s,source,packing=None,density=None):
  name='food:'+product;obj=self.objects[name]
  if kind not in ('washed','peeled','slices','wedges','sections','basal_root_trim'):raise ValueError('Unknown declared food transformation')
  if self.attached==name or obj['support']!=station:raise ValueError('Food transformation outside supported station')
  regions_=regions(self,station);entry=contains(obj['body'],obj['pose'],regions_['input'])
  if not entry['pass_']:raise ValueError('Full input geometry outside station interior: '+str(entry))
  packing=packing if packing is not None else .20 if product=='leafy_greens' else .60 if product=='tomato' else .55;density=density if density is not None else 1000 if product in ('leafy_greens','tomato') else 1030
  if not (0<packing<=1 and density>0):raise ValueError('Invalid bulk density/packing')
  if duration_s is not None and (not np.isfinite(duration_s) or duration_s<0):raise ValueError('Invalid appliance duration')
  before=self.mass[product]+self.scrap[product];fraction=.04 if kind=='peeled' else .025 if kind in ('slices','wedges','sections') else 0.;waste=self.mass[product]*fraction;edible=self.mass[product]-waste;scrap=self.scrap[product]+waste;volume=edible/(density*packing);bed=[.16,.12,volume/(.16*.12)]
  newobj=copy.deepcopy(obj);newobj['mass']=edible;output_check=entry
  if kind in ('slices','wedges','sections'):
   if any(n!=name and o.get('bulk_output') and o.get('container_identity')==station for n,o in self.objects.items()):raise ValueError('Station container has an untransferred bulk batch; full container unloading must occur first')
   b=E.Element('body');v.s.model.box(b,'food_bulk',[0,0,0],bed,robot=False);region=regions_['output'];offset=np.array([0,0,-region['half'][2]+bed[2]/2]);pose=p.T(region['center']+region['rotation']@offset,region['rotation']);output_check=contains(b,pose,region)
   if not output_check['pass_']:raise ValueError('Bulk output exceeds station container capacity: '+str(output_check))
   newobj.update(body=b,pose=pose,bulk_output=True,container_identity=station,container_local_pose=p.T(offset, np.eye(3)).tolist())
  scrapobj=None;scrap_check=None;scrap_id='scrap:'+product+':'+station
  if waste:
   local_scrap=self.objects.get(scrap_id,{}).get('mass',0)+waste;region=regions_['scrap'];cell=list(self.mass).index(product);scrapbed=[.075,.07,local_scrap/(density*.35*.075*.07)];offset=np.array([-.12+cell*.08,0,-region['half'][2]+scrapbed[2]/2]) if station=='linear_peeler_holder' else np.array([0,0,-region['half'][2]+bed[2]+scrapbed[2]/2]);pose=p.T(region['center']+region['rotation']@offset,region['rotation']);body=E.Element('body');v.s.model.box(body,'scrap_bulk',[0,0,0],scrapbed,robot=False);scrap_check=contains(body,pose,region)
   if not scrap_check['pass_']:raise ValueError('Scrap exceeds full tray capacity')
   scrapobj=dict(body=body,pose=pose,home=pose.copy(),h=p.zero(obj['h']),support='linear_peeler_scrap_floor' if station=='linear_peeler_holder' else station,container_identity=station,mass=local_scrap)
  event=dict(kind='declared_food_transformation',product=product,operation=kind,station=station,mass_before_kg=before,edible_after_kg=edible,scrap_after_kg=scrap,conserved=abs(before-edible-scrap)<1e-12,duration_s=duration_s,duration_source=source,duration_qualified=False,duration_status='Sourced component-data design allowance; exact food-processing cycle unqualified' if duration_s is not None else 'Exact batch duration unknown; not replaced with zero',bulk_density_kg_m3=density,packing_fraction=packing,bed_size_m=bed,input_containment=entry,output_containment=output_check,scrap_containment=scrap_check,station_geometry_basis=regions_['basis'],interior_qualified=regions_['interior_qualified'],quality='Declared unchanged finished products; future physical quality testing',executed=False)
  # All validation precedes every mutation, including the mass ledger.
  self.objects[name]=newobj;self.mass[product]=edible;self.scrap[product]=scrap;self.conditions[product]=kind
  if scrapobj:self.objects[scrap_id]=scrapobj
  self.transforms.append(event);return event
 p.World.station_regions=regions;p.World.transform=transform;p.World.contains=staticmethod(contains)
