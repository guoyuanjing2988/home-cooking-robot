"""Lock full existing bail75deg toward front; keep bowl shell/collar unchanged.
All original solids retain their dimensions. Two full pins/stops are added.
"""
import copy,xml.etree.ElementTree as E
import numpy as np
from scipy.spatial.transform import Rotation

def install(v):
 if not v.cfg.get('bowl_bail_swing_deg'):return lambda root:root
 s=v.s;angle=v.cfg['bowl_bail_swing_deg'];rot=Rotation.from_euler('z',-angle,degrees=True);inverse=rot.inv();pivot=np.array([.093,0,0]);key=pivot-rot.apply(pivot);original=s.held
 def held(parent,h,prefix):
  before={id(g) for g in parent.findall('.//geom')};bodies={id(b) for b in parent.findall('.//body')};original(parent,h,prefix)
  if h['held']!='carried_bowl':return
  for g in parent.findall('.//geom'):
   if id(g) in before:continue
   part=g.get('name','').removeprefix(prefix)
   if part=='key' or part.startswith(('bail_','key_shoulder')):continue
   pos=np.fromstring(g.get('pos','0 0 0'),sep=' ');q=Rotation.from_quat(np.fromstring(g.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]])
   g.set('pos',s.model.fmt(inverse.apply(pos-key)));g.set('quat',s.model.quat(inverse*q))
  target=next((b for b in parent.findall('.//body') if id(b) not in bodies and b.get('name')==prefix+'object'),parent)
  for sign in (-1,1):
   point=inverse.apply(np.array([.093,0,sign*.0905])-key)
   E.SubElement(target,'geom',name=prefix+'bail_lock_pin'+str(sign),type='cylinder',pos=s.model.fmt(point),size='.003 .006',mass='.000001',contype='8' if prefix.startswith(('R_','L_')) else '1',conaffinity='7' if prefix.startswith(('R_','L_')) else '15')
   point=inverse.apply(np.array([.081,-.01,sign*.0905])-key)
   geom=s.model.box(target,prefix+'bail_lock_stop'+str(sign),point,[.010,.012,.014],mass=.000001,robot=prefix.startswith(('R_','L_')))
 s.held=held
 def stored(root):
  for body in root.findall(".//body"):
   if not body.get('name','').startswith('stored_bowl_') or body.get('name','').endswith('_object'):continue
   pos=np.fromstring(body.get('pos','0 0 0'),sep=' ');q=Rotation.from_quat(np.fromstring(body.get('quat','1 0 0 0'),sep=' ')[[1,2,3,0]])
   body.set('pos',s.model.fmt(pos+q.apply(key)));body.set('quat',s.model.quat(q*rot))
  return root
 return stored
