"""Lossless direct official JAKA URDF import; no effort torque admission."""
import xml.etree.ElementTree as E
import numpy as np
from scipy.spatial.transform import Rotation
import oem_model as o
original=o.source_root
def source(arm):
 if arm not in ['JAKA_Zu5','JAKA_Zu7']:return original(arm)
 name='jaka_zu'+arm[-1];folder=o.HERE/'sources/jaka_description';u=E.parse(folder/'urdf'/(name+'.urdf')).getroot();r=E.Element('mujoco',model=arm);E.SubElement(r,'compiler',angle='radian',autolimits='true');asset=E.SubElement(r,'asset');w=E.SubElement(r,'worldbody')
 links={a.get('name'):a for a in u.findall('link')};joints=u.findall('joint');children={}
 for j in joints:children.setdefault(j.find('parent').get('link'),[]).append(j)
 def walk(link,parent,j=None):
  attr=dict(name=link)
  if j is not None:
   org=j.find('origin');attr.update(pos=org.get('xyz','0 0 0'),quat=o.quat(Rotation.from_euler('xyz',np.fromstring(org.get('rpy','0 0 0'),sep=' '))))
  b=E.SubElement(parent,'body',**attr);l=links[link];it=l.find('inertial')
  if it is not None:
   org=it.find('origin');v=it.find('inertia');rt=Rotation.from_euler('xyz',np.fromstring(org.get('rpy','0 0 0'),sep=' ')).as_matrix();iv={k:float(v.get(k)) for k in ['ixx','iyy','izz','ixy','ixz','iyz']};tensor=rt@np.array([[iv['ixx'],iv['ixy'],iv['ixz']],[iv['ixy'],iv['iyy'],iv['iyz']],[iv['ixz'],iv['iyz'],iv['izz']]])@rt.T
   E.SubElement(b,'inertial',pos=org.get('xyz','0 0 0'),mass=it.find('mass').get('value'),fullinertia=o.fmt([tensor[0,0],tensor[1,1],tensor[2,2],tensor[0,1],tensor[0,2],tensor[1,2]]))
  if j is not None and j.get('type')!='fixed':
   lim=j.find('limit');E.SubElement(b,'joint',name=j.get('name'),axis=j.find('axis').get('xyz'),range=lim.get('lower')+' '+lim.get('upper'))
  for i,c in enumerate(l.findall('collision')):
   mesh=c.find('geometry/mesh');org=c.find('origin');file=folder/mesh.get('filename').split('jaka_description/')[-1];n=link+'_'+str(i);E.SubElement(asset,'mesh',name=n,file=str(file.resolve()));E.SubElement(b,'geom',name=n,type='mesh',mesh=n,pos=org.get('xyz','0 0 0') if org is not None else '0 0 0',quat=o.quat(Rotation.from_euler('xyz',np.fromstring(org.get('rpy','0 0 0') if org is not None else '0 0 0',sep=' '))))
  if link in children:
   for ch in children[link]:walk(ch.find('child').get('link'),b,ch)
  else:E.SubElement(b,'site',name='attachment_site',pos='0 0 0')
 root=next(n for n in links if n not in {j.find('child').get('link') for j in joints});walk(root,w);E.ElementTree(r).write(o.HERE/'models'/(name+'.xml'),encoding='unicode')
 o.RATINGS[arm]=dict(status='URDF effort diagnostic only; actual OEM allowed-CoM rated-payload envelope used',values=[float(j.find('limit').get('effort')) for j in joints if j.get('type')!='fixed'])
 return r,folder
o.source_root=source
