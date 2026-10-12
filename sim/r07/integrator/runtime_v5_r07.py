"""Full-geometry appliance/station adapter; food-only transformations are separate."""
import json,copy,xml.etree.ElementTree as E
import numpy as np,mujoco
from scipy.spatial.transform import Rotation
import runtime_v4_r07 as base
H=base.H;O=base.O;ID=base.ID;cfg=base.cfg;P=base.P;items=base.items;rt=base.rt;s=base.s;f=base.f;Checker=base.Checker
original_scene=base.scene
from bowl_bail_v5_r07 import install as install_bail
import sys
position_bail_stores=install_bail(sys.modules[__name__])
def revise_arm(root):
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
def scene(index):
 ch=original_scene(index);root=position_bail_stores(add_peeler(revise_arm(E.fromstring(ch.xml))));ch.xml=E.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.set_contacts(items[index][1]['poses'][0]);return ch
base.scene=scene
def full_transport(c):
 tr,meta=s.model.build(dict(c,transport_only=True));revise_arm(tr.getroot());return tr,meta
