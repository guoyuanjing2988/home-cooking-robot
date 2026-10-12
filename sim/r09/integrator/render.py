"""CPU-only matplotlib projections of full checked collision geometry, <=1600px."""
import sys,math
import numpy as np,mujoco
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from scene import H,load,save,build
from checker import Checker
def polygons(ch,q,doors=False):
 ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);out=[]
 for g,n in enumerate(ch.gnames):
  typ=ch.m.geom_type[g];s=ch.m.geom_size[g];R=ch.d.geom_xmat[g].reshape(3,3);p=ch.d.geom_xpos[g]
  if typ==0:continue
  if typ==6:v=np.array([[a,b,c] for a in [-s[0],s[0]] for b in [-s[1],s[1]] for c in [-s[2],s[2]]])
  elif typ==7:v=ch.bounds.local[g]
  else:
   points=[]
   if typ in (3,5):
    for z in [-s[1],s[1]]:
     for a in np.linspace(0,2*np.pi,13)[:-1]:points.append([s[0]*np.cos(a),s[0]*np.sin(a),z])
    if typ==3:
     for z in [-s[1],s[1]]:
      for e in np.linspace(-np.pi/2,np.pi/2,7):
       for a in np.linspace(0,2*np.pi,13)[:-1]:points.append([s[0]*np.cos(e)*np.cos(a),s[0]*np.cos(e)*np.sin(a),z+s[0]*np.sin(e)])
   else:
    radii=np.ones(3)*s[0] if typ==2 else s
    for e in np.linspace(-np.pi/2,np.pi/2,7):
     for a in np.linspace(0,2*np.pi,13)[:-1]:points.append(radii*np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)]))
   v=np.array(points)
  try:faces=ConvexHull(v).simplices
  except Exception:continue
  v=v@R.T+p
  if doors and n.startswith('r07_closed_door'):
   odd=n.endswith('_1');hinge=p+np.array([s[0] if odd else -s[0],0,0]);rot=Rotation.from_euler('z',90 if odd else -90,degrees=True).as_matrix();v=(v-hinge)@rot.T+hinge
  color=ch.m.geom_rgba[g].copy();color[3]=.8 if ch.robot[g] else .65
  out.append((n,v,faces,color,ch.robot[g]))
 return out
def draw(ax,items,limits,focus=False):
 lo,hi=np.array(limits[0]),np.array(limits[1]);polys=[];colors=[]
 for n,v,f,col,robot in items:
  if np.any(v.max(axis=0)<lo) or np.any(v.min(axis=0)>hi):continue
  if n.startswith(('south_','north_wall','north_cabinet','sink_cabinet')):continue
  if not focus and n.startswith('upper_cabinet'):continue
  if n.startswith('outlet_'):col=np.array([.5,.5,.5,.25])
  for face in f:polys.append(v[face]);colors.append(col)
 ax.add_collection3d(Poly3DCollection(polys,facecolors=colors,edgecolors=(.15,.2,.25,.20),linewidths=.15))
 ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(26,-72)
 ax.set_xlabel('X (m)',fontsize=8);ax.set_ylabel('Y (m)',fontsize=8);ax.set_zlabel('Z (m)',fontsize=8);ax.tick_params(labelsize=7)