"""Full-geometry appliance/station adapter; food-only transformations are separate."""
import json,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import runtime_v4_r07 as base
H=base.H;O=base.O;ID=base.ID;cfg=base.cfg;P=base.P;items=base.items;rt=base.rt;s=base.s;f=base.f;Checker=base.Checker
original_scene=base.scene
from bowl_bail_v7_r07 import install as install_bail
import sys
position_bail_stores=install_bail(sys.modules[__name__])
def revise_arm(root):
 if cfg.get('remove_legacy_motion_sweeps'):
  for parent in root.iter():
   for geom in list(parent.findall('geom')):
    if geom.get('name','').startswith(('cabinet_door_sweep_','idle_full_sweep_cover_')):parent.remove(geom)
 for joint in root.findall('.//joint'):
  if joint.get('name')=='R_elbow_joint':joint.set('range',s.model.fmt(np.radians([-160,160])))
 mount=root.find(".//body[@name='R_mount']")
 if mount is not None and mount.find("geom[@name='R_current151mm_base_cover']") is None:
  E.SubElement(mount,'geom',name='R_current151mm_base_cover',type='cylinder',size='.0755 .004',pos='0 0 .004',mass='.03',contype='8',conaffinity='7',rgba='.2 .4 .8 1')
 return root
def add_peeler(root):
 w=root.find('worldbody');x,y,_=cfg['station_frames']['peel']['new_center']
 for g in list(w.findall('geom')):
  if g.get('name','').startswith(('rotato_','sammic_m5_','m5_water_drain')):w.remove(g)
 # Complete custom design: full480x50x50 actuator/guide enclosure exceeds
 # 247mm closed-hole length+200mm stroke+end fittings; bearing guide takes
 # 7.5N radial tool load, not the P16's4N lateral allowance.
 specs=[('linear_peeler_drive',[x,y+.18,.985],[.480,.050,.050]),('linear_peeler_guide',[x,y+.125,.955],[.36,.035,.025]),('linear_peeler_guard_back',[x,y+.10,1.015],[.36,.006,.20]),('linear_peeler_guard_left',[x-.18,y+.015,1.015],[.006,.17,.20]),('linear_peeler_guard_right',[x+.18,y+.015,1.015],[.006,.17,.20]),('linear_peeler_open_lid',[x,y+.19,1.125],[.36,.20,.006]),('linear_peeler_lid_handle',[x,y+.19,1.144],[.075,.022,.032]),('linear_peeler_scrap_floor',[x,y,.865],[.35,.17,.010])]
 for name,pos,size in specs:
  if cfg.get('peeler_lid_vertical') and name=='linear_peeler_open_lid':pos=[x,y+.10,1.215];size=[.36,.006,.20]
  if cfg.get('peeler_lid_vertical') and name=='linear_peeler_lid_handle':pos=[x,y+.081,1.215];size=[.075,.032,.022]
  if cfg.get('peeler_lid_front_hinge') and name=='linear_peeler_open_lid':pos=[x,y-.10,1.215]
  if cfg.get('peeler_lid_front_hinge') and name=='linear_peeler_lid_handle':pos=[x,y-.081,1.215]
  s.model.box(w,name,pos,size,robot=False)
 if cfg.get('peeler_lid_vertical'):
  s.model.box(w,'linear_peeler_full_hinge',[x,y+(-.10 if cfg.get('peeler_lid_front_hinge') else .10),1.115],[.36,.020,.020],robot=False)
 # Original complete peeler, inside the new enclosure. Its powered sweep
 # stays inside this guarded station; root input/output remain full sized.
 b=E.SubElement(w,'body',name='linear_peeler_cutter',pos=s.model.fmt([x,y+.07,.93]))
 h=copy.deepcopy(items[0][1]['poses'][0]['R']);h.update(held='peeler',held_kg=P['tools']['peeler']['mass_kg'],object_rotation_deg=[0,0,0]);s.held(b,h,'linear_peeler_')
 return root
def add_closed_doors(root):
 w=root.find('worldbody')
 for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
  count=2 if hi-lo>.6 else 1;width=(hi-lo)/count
  for j in range(count):
   hinge=lo if j==0 else hi;sign=1 if j==0 else -1
   s.model.box(w,f'r07_closed_door_{ci}_{j}',[hinge+sign*width/2,.221,1.65],[width,.018,.60],robot=False,mass=5.94)
   s.model.box(w,f'door_pause_sensor_{ci}_{j}',[hinge+sign*.025,.248,1.94],[.012,.016,.020],robot=False)
 return root

def scene(index):
 ch=original_scene(index);root=add_closed_doors(position_bail_stores(add_peeler(revise_arm(E.fromstring(ch.xml)))))
 if cfg.get('remove_legacy_motion_sweeps'):
  # Legacy R05 masks are full open-door swept volumes, not closed leaves.
  # Idle adds its separately named full-sweep covers after this constructor.
  for parent in root.iter():
   for geom in list(parent.findall('geom')):
    if geom.get('name','').startswith(('cabinet_door_sweep_','idle_full_sweep_cover_')):parent.remove(geom)
 if cfg.get('whole_bowl_yaw_deg'):
  yaw=Rotation.from_euler('z',cfg['whole_bowl_yaw_deg'],degrees=True)
  for body in root.find('worldbody').findall('body'):
   if body.get('name','').startswith('stored_bowl_'):
    r=Rotation.from_quat(np.fromstring(body.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]]);body.set('quat',s.model.quat(yaw*r))
 if cfg.get('lid_slot_override'):
  for g in root.findall(".//geom[@name='secondary_lid_storage_slot']"):g.set('pos',s.model.fmt(cfg['lid_slot_override']))
 for product,degrees in cfg.get('bowl_yaw_by_product',{}).items():
  yaw=Rotation.from_euler('z',degrees,degrees=True);center=np.array(cfg['station_frames']['output_'+product]['new_center'])
  body=root.find(".//body[@name='stored_bowl_"+product+"']")
  if body is not None:
   pos=np.fromstring(body.get('pos'),sep=' ');r=Rotation.from_quat(np.fromstring(body.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]])
   body.set('pos',s.model.fmt(center+yaw.apply(pos-center)));body.set('quat',s.model.quat(yaw*r))
 ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.set_contacts(items[index][1]['poses'][0]);return ch
base.scene=scene
def full_transport(c):
 tr,meta=s.model.build(dict(c,transport_only=True));revise_arm(tr.getroot());return tr,meta
