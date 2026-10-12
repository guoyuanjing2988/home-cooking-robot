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
def main():
 cfg=load('results/selected.json')['config'];tree,meta=build(cfg);ch=Checker(tree,meta);park=np.array(load('assets/park.json')['q']);items=polygons(ch,park)
 views=[('overview',f'R08 {cfg["id"]} diagnostic layout | no connected carrot execution',([-1.85,-.12,.80],[.75,.64,1.36])),('wash','Full tilted basket centred at jet | cradle/support design remains open',([-.76,.08,.62],[-.32,.57,.99])),('peel','Low P16 peeler | side drawer / roof interfaces unqualified',([-1.51,-.03,.83],[-.88,.36,1.08])),('mandoline','Golden holder station | 330 x 120 x 60 mm deck; horizontal stroke',([.19,-.04,.83],[.68,.32,1.11])),('greens','Low guillotine / splitter | custom fixture, no executed product',([-1.01,.01,.83],[-.67,.32,1.09])),('tomato','Low lever wedger | eight sectors; force sizing remains provisional',([-.12,-.02,.83],[.16,.30,1.09])),('bowls','Four original full bowls and bails | rigidly relocated',([-1.81,.23,.83],[-.70,.60,1.09]))]
 for name,title,limits in views:
  fig=plt.figure(figsize=(12,7),dpi=120);ax=fig.add_subplot(111,projection='3d');draw(ax,items,limits,focus=name!='overview');fig.suptitle(title,fontsize=13)
  if name=='wash':ax.plot([-.58,-.58],[.43,.43],[.91,meta['wash_mouth'][2]],color='blue',linewidth=3)
  fig.text(.04,.03,'CPU render of checked geometry. View is a cutaway; all kitchen solids remain in checks.',fontsize=9);fig.savefig(H/'renders'/f'{name}.png');plt.close(fig)
 fig=plt.figure(figsize=(12,7),dpi=120);ax=fig.add_subplot(111,projection='3d');draw(ax,polygons(ch,park,doors=True),([-1.85,-.38,.80],[.75,.64,2.0]));fig.suptitle('Parked proposal with doors open 90 degrees | full idle verdict in idle.json');fig.savefig(H/'renders/parked_doors_open.png');plt.close(fig)
 # Honest strip: no executed carrot sequence exists, so show rejected candidate
 # states with identifiers; never interpolate a fictional successful sequence.
 rows=load('results/statics/1_0.json')['rows'];qs=[r for r in rows if 'q' in r][:24]
 tree,meta=build(cfg,'carrot');cc=Checker(tree,meta)
 fig=plt.figure(figsize=(16,11),dpi=100)
 for i,r in enumerate(qs):
  ax=fig.add_subplot(4,6,i+1,projection='3d');draw(ax,polygons(cc,r['q']),([-1.8,-.2,.7],[.7,.6,1.6]));ax.set_axis_off();ax.set_title(f'IK start {r["start"]}: {r["status"]}',fontsize=8)
 fig.suptitle('24 carrot wash candidate configurations | NOT an executed sequence',fontsize=15);fig.text(.03,.02,'No connected carrot execution exists. These separate IK attempts cannot be read as a motion trajectory.',fontsize=11);fig.savefig(H/'renders/carrot_diagnostic_strip.png');plt.close(fig)
 # Conservative plan-view free area: full projections of occupied equipment and
 # parked robot below cabinet bottom; sink/stove remain unavailable.
 ch.d.qpos[:]=park;mujoco.mj_forward(ch.m,ch.d);xs=np.arange(-1.7975,.69,.005);ys=np.arange(.0025,.6,.005);X,Y=np.meshgrid(xs,ys);free=np.ones(X.shape,dtype=bool)
 free &= ~((X>-.70)&(X<-.10)&(Y>.08)&(Y<.52))
 for g,n in enumerate(ch.gnames):
  if n.startswith(('floor','counter_','north_cabinet','sink_cabinet','sink_','south_','upper_cabinet','north_wall','r07_closed','faucet_v3_concealed','faucet_v3_under','faucet_v3_water')):continue
  lo=np.array([ch.bounds.support(g,-a)[k] for k,a in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,a)[k] for k,a in enumerate(np.eye(3))])
  if hi[2]<=.85 or lo[2]>=1.35:continue
  free &= ~((X>=lo[0]-.01)&(X<=hi[0]+.01)&(Y>=lo[1]-.01)&(Y<=hi[1]+.01))
 area=float(free.sum()*.005**2);front=float((free&(Y<.23)).sum()*.005**2)
 save('results/counter_area.json',dict(free_counter_m2=area,free_front_strip_m2=front,grid_m=.005,obstacle_expansion_m=.01,scope='Conservative full AABB projections below 1.35m at prospective park. Excludes sink and stove. Not ergonomic or installation acceptance.'))
 fig,ax=plt.subplots(figsize=(13,4),dpi=100);ax.pcolormesh(X,Y,free,cmap='RdYlGn',shading='nearest',vmin=0,vmax=1);ax.set_aspect('equal');ax.set_title(f'Idle free counter proposal: {area:.3f} m2; front strip {front:.3f} m2');ax.set_xlabel('X / m');ax.set_ylabel('Y / m');fig.savefig(H/'renders/counter_free_area.png');plt.close(fig)
 print('renders complete, free counter',area,front,flush=True)
if __name__=='__main__':main()
