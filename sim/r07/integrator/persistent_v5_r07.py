"""Executable, transactional world/attachment model. Nothing commits on failure.

Later connection attempts are explicitly conditional diagnostics when the
preceding prefix failed. A food transformation changes mass representation
inside its named station; it cannot move a container or a robot attachment.
"""
import copy,json,hashlib,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import runtime_v5_r07 as v

def T(pos,rot):
 a=np.eye(4);a[:3,3]=pos;a[:3,:3]=rot;return a
def matrix(node):
 return T(np.fromstring(node.get('pos','0 0 0'),sep=' '),Rotation.from_quat(np.fromstring(node.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]]).as_matrix())
def put(node,t):
 node.set('pos',v.s.model.fmt(t[:3,3]));node.set('quat',v.s.model.quat(Rotation.from_matrix(t[:3,:3])))
def identity(h):return None if h['held']=='empty' else v.rt.object_identity(h)
def fk(ch,q):
 ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d);sid=ch.m.site('R_prep').id
 return T(ch.d.site_xpos[sid].copy(),ch.d.site_xmat[sid].reshape(3,3).copy())
def zero(h):
 h=copy.deepcopy(h);h['contacts']=[c for c in h.get('contacts',[]) if c.get('kind')=='grasp_release_support']
 for n in ('nominal','check'):h[n+'_forces_N']=[[0,0,0]];h[n+'_moments_Nm']=[[0,0,0]]
 return h

def local_geoms(body):
 root=E.Element('mujoco');E.SubElement(root,'compiler',angle='radian');world=E.SubElement(root,'worldbody');world.append(copy.deepcopy(body));model=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));data=mujoco.MjData(model);mujoco.mj_forward(model,data)
 return {model.geom(i).name:dict(type=int(model.geom_type[i]),size=model.geom_size[i].copy(),transform=T(data.geom_xpos[i],data.geom_xmat[i].reshape(3,3))) for i in range(model.ngeom)}

class World:
 def __init__(self):
  self.base=v.scene(0);self.root=E.fromstring(self.base.xml);w=self.root.find('worldbody');self.objects={};self.events=[];self.contents={};self.attached=None;self.transforms=[]
  products={p['product']:p for p in v.P['finished_products']}
  # Canonical tool-frame geometry and actual initial world placements.
  for prod,p in products.items():
   g=w.find("geom[@name='staged_raw_"+prod+"']");pos=np.fromstring(g.get('pos'),sep=' ')
   h=next((copy.deepcopy(sg['poses'][0]['R']) for _,sg,_ in v.items if sg['poses'][0]['R']['product']==prod and sg['poses'][0]['R']['held']=='root_food'),copy.deepcopy(v.items[1][1]['poses'][0]['R']));h.update(product=prod,held='root_food')
   object_rotation=Rotation.from_euler('xyz',h.get('object_rotation_deg') or [0,0,0],degrees=True)
   raw_rotation=v.s.rot(dict(approach=[0,0,-1],jaw_axis=[0,1,0]));home_rotation=raw_rotation@object_rotation.as_matrix().T
   if prod=='leafy_greens' and h.get('object_rotation_deg')==[0,0,90]:
    # Initial staging is allowed to roll the intact bok choy, exposing its
    #70mm dimension to the90mm gripper. Whole box rotated, never scaled.
    home_rotation=raw_rotation;pos[2]+=(p['input_size_m'][1]-p['input_size_m'][2])/2
   size=np.array([p['input_size_m'][2],p['input_size_m'][1],p['input_size_m'][0]]);opening=float((abs(object_rotation.as_matrix())@size)[1])
   h.update(food_state='whole',food_tool_roll_deg=0,food_center_local_m=[0,0,0],held_kg=p['input_mass_kg'],jaw_opening_m=opening,approach=home_rotation[:,0].tolist(),jaw_axis=(-home_rotation[:,1]).tolist())
   body=E.Element('body');v.s.held(body,h,'object_');self.register('food:'+prod,body,T(pos,home_rotation),h,'raw_'+prod+'_land',p['input_mass_kg'])
  for b in list(w.findall('body')):
   n=b.get('name','')
   if n.startswith('stored_bowl_'):
    prod=n[len('stored_bowl_'):];h=next(copy.deepcopy(sg['poses'][0]['R']) for _,sg,_ in v.items if sg['poses'][0]['R']['held']=='carried_bowl' and sg['poses'][0]['R']['product']==prod);h.update(held_kg=v.P['tools']['carried_bowl']['mass_kg']);objrot=Rotation.from_euler('xyz',h.get('object_rotation_deg') or [0,0,0],degrees=True).as_matrix();home=matrix(b);home[:3,:3]=home[:3,:3]@objrot.T;canonical=E.Element('body');v.s.held(canonical,h,'object_');self.register('bowl_'+prod,canonical,home,h,'output_'+prod+'_land',h['held_kg'])
   elif n in ('stored_wash_pad','stored_eye_core_spoon'):
    typ=n[7:];h=next(copy.deepcopy(sg['poses'][0]['R']) for _,sg,_ in v.items if sg['poses'][0]['R']['held']==typ);self.register(typ,b,matrix(b),h,'dock_'+typ+'_face',h['held_kg'])
  # Full existing vessels get explicit storage poses and full support stands.
  for typ,name,pos in [('food_cup','cup',[-1.57,.10,1.13]),('cut_cassette','cassette',[-1.59,.275,1.07]),('colander','colander',[-.35,.30,.805])]:
   if name in v.cfg.get('retired_transfer_vessels',[]):continue
   pos=v.cfg.get('persistent_storage',{}).get(name,pos)
   h=next(copy.deepcopy(sg['poses'][0]['R']) for _,sg,_ in v.items if sg['poses'][0]['R']['held']==typ);h.update(held_kg=v.P['tools'][typ]['mass_kg']);objrot=Rotation.from_euler('xyz',h.get('object_rotation_deg') or [0,0,0],degrees=True).as_matrix();raw=v.s.rot(dict(approach=[0,0,-1],jaw_axis=[0,1,0]));home=raw@objrot.T;b=E.Element('body');v.s.held(b,h,'object_');self.register(name,b,T(pos,home),h,'persistent_'+name+'_storage',h['held_kg'])
  # Remove only movable copies; fixed kitchen, full appliances, supports and
  # robot solids remain. The same registry is used for every compiled state.
  for g in list(w.findall('geom')):
   if g.get('name','').startswith(('staged_raw_','clamped_food','wash_food')):w.remove(g)
  for b in list(w.findall('body')):
   if b.get('name','').startswith('stored_'):w.remove(b)
  self.initial_mass=sum(p['input_mass_kg'] for p in products.values());self.mass={p:pdata['input_mass_kg'] for p,pdata in products.items()};self.scrap={p:0. for p in products};self.conditions={p:'whole_raw' for p in products}
  self.supports=[]
  # Establish full plate/leg geometry under each additional storage object.
  for name in ('cup','cassette','colander'):
   if name not in self.objects:continue
   obj=self.objects[name];rr=E.Element('mujoco');E.SubElement(rr,'compiler',angle='radian');ww=E.SubElement(rr,'worldbody');bb=copy.deepcopy(obj['body']);put(bb,obj['pose']);ww.append(bb);mm=mujoco.MjModel.from_xml_string(E.tostring(rr,encoding='unicode'));dd=mujoco.MjData(mm);mujoco.mj_forward(mm,dd)
   from distance import Bounds
   bound=object.__new__(Bounds);bound.m=mm;bound.d=dd;bound.local={}
   low=np.array([[bound.support(g,-a)[k] for k,a in enumerate(np.eye(3))] for g in range(mm.ngeom)]).min(0);high=np.array([[bound.support(g,a)[k] for k,a in enumerate(np.eye(3))] for g in range(mm.ngeom)]).max(0)
   center=(low+high)/2;size=high-low;plate=E.Element('worldbody');v.s.model.box(plate,obj['support'],[center[0],center[1],low[2]-.005],[size[0]+.02,size[1]+.02,.01],robot=False)
   support_base=.85 if low[2]>.86 else .65;height=max(.001,low[2]-.01-support_base)
   for dx in (-1,1):
    v.s.model.box(plate,obj['support']+'_leg'+str(dx),[center[0]+dx*(size[0]/2-.015),center[1],support_base+height/2],[.02,.025,height],robot=False)
   self.supports.extend(list(plate))
 def register(self,name,body,pose,h,support,mass):
  b=copy.deepcopy(body);b.attrib={'name':'canonical_'+name.replace(':','_')}
  # Canonical part names remain stable across fixed/attached representations.
  for g in b.findall('.//geom'):
   n=g.get('name','');prefix=('stored_bowl_'+h['product']+'_' if name.startswith('bowl_') else 'stored_'+name+'_')
   part=n[len(prefix):] if n.startswith(prefix) else n.removeprefix('object_');g.set('name',part)
  self.objects[name]=dict(body=b,pose=pose.copy(),home=pose.copy(),h=zero(h),support=support,home_support=support,mass=mass)
  self.objects[name]['full_touch_body']=copy.deepcopy(b)
 def snapshot(self):
  return dict(objects={n:dict(pose=o['pose'].tolist(),mass_kg=o['mass'],support=o['support'],owner='R' if self.attached==n else o['support']) for n,o in self.objects.items()},attached=self.attached,food_mass_kg=self.mass.copy(),scrap_mass_kg=self.scrap.copy(),conditions=self.conditions.copy(),total_food_kg=sum(self.mass.values())+sum(self.scrap.values()))
 def build(self,index,attached=None,hand=None):
  ch=v.scene(index);root=copy.deepcopy(self.root);w=root.find('worldbody');tool=root.find(".//body[@name='R_tool']")
  for node in list(tool):
   if node.get('name','').startswith(('R_held_','R_work','R_mass')):tool.remove(node)
  for g in self.supports:w.append(copy.deepcopy(g))
  for name,obj in self.objects.items():
   isheld=name==attached
   # A bulk proxy is an appliance/container output, never a shrunken object
   # for direct robot manipulation. Retain the full input geometry if a
   # later conditional diagnostic proposes an unqualified direct regrasp.
   b=copy.deepcopy(obj.get('full_touch_body',obj['body']) if isheld else obj['body']);prefix='R_held_' if isheld else 'persistent_'+name.replace(':','_')+'_'
   b.set('name',prefix+'body')
   for j,bb in enumerate(b.findall('.//body')):bb.set('name',prefix+'partbody_'+str(j))
   for g in b.findall('.//geom'):
    g.set('name',prefix+g.get('name'));g.set('contype','8' if isheld else '1');g.set('conaffinity','7' if isheld else '15')
   if isheld:tool.append(b)
   else:put(b,obj['pose']);w.append(b)
  h=zero(hand or v.items[index][1]['poses'][0]['R'])
  if attached:h.update(held=self.objects[attached]['h']['held'],held_kg=self.objects[attached]['mass'])
  else:h.update(held='empty',held_kg=0,grip='key',work_offset_m=0,mass_offset_m=0,contacts=[])
  for label,key in [('work','work_offset_m'),('mass','mass_offset_m')]:E.SubElement(tool,'site',name='R_'+label,pos=v.s.model.fmt(v.s.ck.offset_vector(h[key])),size='.003')
  ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.hands={'R':h};ch.working_stroke=False;ch.contact_windows=[];ch.set_contacts(ch.hands)
  return ch,{'R':h}
 def rebind(self,name,new_owner,world_pose):
  obj=self.objects[name];err=np.max(abs(obj['pose']-world_pose))
  if err>1e-7:raise ValueError('Refuse object teleport at binding: '+name)
  if new_owner=='R':
   if obj.get('bulk_output'):raise ValueError('Direct robot attachment of a bulk output is forbidden; use its full container')
   if self.attached is not None:raise ValueError('Second object attachment')
   self.attached=name
  else:self.attached=None;obj['support']=new_owner
  return dict(object_id=name,world_transform_max_error=err,owner=new_owner,pass_=True)
 def reframe(self,name,new_hand,commit=False):
  """Find an alternative grasp frame without moving or scaling any solid.
  Actual commit is allowed only while supported, following a checked release.
  All corresponding parts must have identical type/size and a common rigid
  transform. A whole-to-leaf reduction therefore cannot masquerade as regrasp.
  """
  obj=self.objects[name]
  if obj.get('bulk_output'):raise ValueError('Bulk output requires a full container, not direct regrasp')
  h=zero(new_hand);h['held_kg']=obj['mass'];body=E.Element('body',name='canonical_'+name.replace(':','_'));v.s.held(body,h,'object_')
  for g in body.findall('.//geom'):g.set('name',g.get('name').removeprefix('object_'))
  old=local_geoms(obj.get('full_touch_body',obj['body']));new=local_geoms(body)
  if set(old)!=set(new):raise ValueError('Regrasp cannot change full part identities')
  first=next(iter(old));change=old[first]['transform']@np.linalg.inv(new[first]['transform']);maximum=0.
  for part in old:
   a,b=old[part],new[part]
   if a['type']!=b['type'] or np.max(abs(a['size']-b['size']))>1e-9:raise ValueError('Regrasp cannot resize a robot-touched object')
   maximum=max(maximum,float(np.max(abs(a['transform']-change@b['transform']))))
  if maximum>1e-7:raise ValueError('No common rigid transform for regrasp')
  required=float(np.max(abs(change-np.eye(4))))>1e-7
  if commit:
   if self.attached==name:raise ValueError('Release to support before changing grasp frame')
   obj['pose']=obj['pose']@change;obj['home']=obj['home']@change;obj['body']=body;obj['full_touch_body']=copy.deepcopy(body);obj['h']=h
  return dict(object_id=name,kind='rigid_grasp_frame_change',requires_release_and_regrasp=required,all_full_parts_preserved=True,max_local_matrix_error=maximum,frame_transform=change.tolist(),committed=commit)
 def transform(self,product,kind,station,duration_s,source,packing=None,density=None):
  """Transactional mass ledger; proxy position stays inside named station.
  Callable only with the food supported in that station and no attachment.
  Unknown durations are explicit unqualified events, never zero-time cycles.
  """
  name='food:'+product;obj=self.objects[name]
  packing=packing if packing is not None else .20 if product=='leafy_greens' else .60 if product=='tomato' else .55;density=density if density is not None else 1000 if product in ('leafy_greens','tomato') else 1030
  if self.attached==name or obj['support']!=station:raise ValueError('Food transformation outside station')
  if not (0 < packing <=1 and density>0):raise ValueError('Invalid bulk density/packing')
  before=self.mass[product]+self.scrap[product];m=self.mass[product]
  fraction=.04 if kind=='peeled' else .025 if kind in ('slices','wedges','sections') else 0.
  waste=m*fraction;self.mass[product]-=waste;self.scrap[product]+=waste;self.conditions[product]=kind
  volume=self.mass[product]/(density*packing);bed=[.16,.12,volume/(.16*.12)]
  if kind in ('slices','wedges','sections'):
   b=E.Element('body');v.s.model.box(b,'food_bulk',[0,0,0],bed,robot=False);obj['body']=b;obj['pose'][:3,:3]=np.eye(3);obj['bulk_output']=True
  obj['mass']=self.mass[product]
  if waste:
   b=E.Element('body');scrapbed=[.10,.08,self.scrap[product]/(density*.35*.10*.08)];v.s.model.box(b,'scrap_bulk',[0,0,0],scrapbed,robot=False);sp=obj['pose'].copy();sp[:3,:3]=np.eye(3);sp[2,3]=.875+scrapbed[2]/2;self.objects['scrap:'+product]=dict(body=b,pose=sp,home=sp.copy(),h=zero(obj['h']),support=station+'_scrap_tray',mass=self.scrap[product])
  event=dict(kind='declared_food_transformation',product=product,operation=kind,station=station,mass_before_kg=before,edible_after_kg=self.mass[product],scrap_after_kg=self.scrap[product],conserved=abs(before-self.mass[product]-self.scrap[product])<1e-12,duration_s=duration_s,duration_source=source,bulk_density_kg_m3=density,packing_fraction=packing,bed_size_m=bed,quality='assumed; finished product specification unchanged; physical validation deferred',duration_qualified=duration_s is not None)
  self.transforms.append(event);return event

def expanded():
 rows=[]
 for i,(_,sg,key) in enumerate(v.items):
  repeat=sg.get('loops',{}).get('repeat',1);repeat=repeat if isinstance(repeat,int) else 3 if 'eyes' in str(repeat) else 6
  for r in range(repeat):rows.append(dict(id=key+'@'+str(r+1),index=i,repeat_index=r,roll_deg=r*sg.get('loops',{}).get('roll_increment_deg',0)))
 return rows
