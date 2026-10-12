"""RoboCasa food meshes resized to catalog dimensions for the R13 food bench.

Each RoboCasa object (objaverse / aigen_objs) has a textured visual OBJ and a convex
decomposition (collision OBJs). We bring both into the object frame exactly as
MuJoCo would (mesh scale, refquat, geom pos/quat), map the object's axes to the
world axes by size rank (long -> the requested long axis, etc.), scale each world
axis to the requested size, and write the transformed OBJs to assets/foods/<key>/.
Anisotropic scaling keeps every collision part convex."""
from pathlib import Path
import numpy as np,mujoco,xml.etree.ElementTree as E
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent
RC=H.parents[1]/'vendor/robocasa/robocasa/models/assets/objects'
OUT=H/'assets/foods'
def _quat(s):q=np.fromstring(s,sep=' ');return Rotation.from_quat(q[[1,2,3,0]]).as_matrix()
def _read_obj(p):
 V=[];rest=[]
 for line in open(p,encoding='utf-8',errors='ignore'):
  if line.startswith('v '):V.append([float(x) for x in line.split()[1:4]])
  elif line.startswith(('vt ','f ')):rest.append(line)
 return np.array(V),rest
def _asset_xf(m_el,base):
 """Mesh-asset transform file -> mesh frame, verified against MuJoCo's compiled mesh."""
 s=np.fromstring(m_el.get('scale','1 1 1'),sep=' ');R=_quat(m_el.get('refquat','1 0 0 0'));rp=np.fromstring(m_el.get('refpos','0 0 0'),sep=' ')
 return lambda V:(V*s-rp)@R  # MuJoCo: scale, subtract refpos, rotate by conj(refquat)
def load(src):
 """src 'aigen_objs/ginger/ginger_0' -> (collision parts, visual (verts, rest lines), texture)."""
 base=RC/src;x=E.parse(base/'model.xml').getroot()
 meshes={m.get('name'):m for m in x.iter('mesh')};tex={t.get('name'):t.get('file') for t in x.iter('texture')}
 mats={m.get('name'):m.get('texture') for m in x.iter('material')}
 col=[];vis=None;texfile=None
 for g in x.find('worldbody').iter('geom'):
  if g.get('type')!='mesh':continue
  me=meshes[g.get('mesh')];V,rest=_read_obj(base/me.get('file'))
  W=_asset_xf(me,base)(V)@_quat(g.get('quat','1 0 0 0')).T+np.fromstring(g.get('pos','0 0 0'),sep=' ')
  if g.get('group')=='1' or g.get('contype')=='0':
   vis=(W,rest);texfile=tex.get(mats.get(g.get('material')))
  else:col.append((W,rest))
 return col,vis,(base/texfile if texfile else None)
def check(src):
 """Compare our object-frame AABB with MuJoCo's own compiled model (sanity check)."""
 base=RC/src;col,vis,_=load(src);V=np.vstack([c[0] for c in col]);ours=(V.min(0),V.max(0))
 x=E.parse(base/'model.xml').getroot()
 for m_ in x.iter('mesh'):m_.set('file',str((base/m_.get('file')).as_posix()))
 for a in x.findall('asset'):
  for t in list(a):
   if t.tag in ('texture','material'):a.remove(t)
 for g in x.iter('geom'):g.attrib.pop('material',None)
 m=mujoco.MjModel.from_xml_string(E.tostring(x,encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 P=[]
 for g in range(m.ngeom):
  if m.geom_type[g]==mujoco.mjtGeom.mjGEOM_MESH and m.geom_group[g]!=1:
   mi=m.geom_dataid[g];v=m.mesh_vert[m.mesh_vertadr[mi]:m.mesh_vertadr[mi]+m.mesh_vertnum[mi]];P.append(d.geom_xpos[g]+v@d.geom_xmat[g].reshape(3,3).T)
 P=np.vstack(P);return ours,(P.min(0),P.max(0))
def make(key,src,dims):
 """Write resized meshes for catalog item `key` from RoboCasa `src`; dims = target
 world-frame size (x = grip width axis, y = long axis, z = height), m."""
 import json as _j
 out=OUT/key;mark=out/'done.json'
 if mark.exists():  # deterministic output already written (parallel runs only read it)
  r=_j.loads(mark.read_text())
  if r.get('src')==src and np.allclose(r['dims'],dims):return r
 col,vis,tex=load(src);V=np.vstack([c[0] for c in col]);lo,hi=V.min(0),V.max(0);c=(lo+hi)/2;e=hi-lo
 dims=np.asarray(dims,float);P=np.zeros((3,3))
 for oi,wi in zip(np.argsort(e),np.argsort(dims)):P[wi,oi]=1.  # object axis -> world axis by size rank
 if np.linalg.det(P)<0:P[np.argmax(dims)]*=-1  # keep a proper rotation (flip the long axis)
 S=dims/(abs(P)@e);A=np.diag(S)@P
 out=OUT/key;out.mkdir(parents=True,exist_ok=True);files=[]
 def write(p,W,rest,keep_vt):
  # parallel bench runs share the cache: write to a private temp file, then replace
  import os,tempfile
  fd,tmp=tempfile.mkstemp(dir=out,suffix='.tmp');os.close(fd)
  _write(tmp,W,rest,keep_vt);os.replace(tmp,p)
 def _write(p,W,rest,keep_vt):
  with open(p,'w') as f:
   for v in (W-c)@A.T:f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
   for line in rest:
    if line.startswith('vt '):
     if keep_vt:f.write(line)
    else:  # faces: drop normal indices (normals are recomputed after scaling)
     parts=[t.split('/') for t in line.split()[1:]]
     f.write('f '+' '.join((p_[0]+'/'+p_[1]) if keep_vt and len(p_)>1 and p_[1] else p_[0] for p_ in parts)+'\n')
 for i,(W,rest) in enumerate(col):
  p=out/f'col{i}.obj';write(p,W,rest,False);files.append(p)
 vp=None
 if vis is not None:vp=out/'vis.obj';write(vp,vis[0],vis[1],True)
 r=dict(col=[str(p.as_posix()) for p in files],vis=str(vp.as_posix()) if vp else None,tex=str(tex.as_posix()) if tex else None,dims=dims.tolist(),src=src)
 mark.write_text(_j.dumps(r));return r
if __name__=='__main__':
 import sys
 for s in sys.argv[1:]:o,m_=check(s);print(s,'ours',np.round(o,4).tolist(),'mujoco',np.round(m_,4).tolist())
