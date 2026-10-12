"""Conservative usable supported counter projection in the populated park scene."""
import os,sys,json,hashlib
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v7_r07 as v
import numpy as np,mujoco
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=v.H;O=v.O;ID=v.ID;idle=json.loads((O/'layouts'/f'{ID}_idle.json').read_text());ch=v.scene(58)
ch.xml=(H/idle['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));v.rt.f.contacts(ch,np.array(idle['q']));b=ch.bounds
lo=np.zeros((ch.m.ngeom,3));hi=lo.copy()
for g in range(ch.m.ngeom):
 if ch.m.geom_type[g]==0:lo[g]=-1e6;hi[g]=1e6;continue
 for k,axis in enumerate(np.eye(3)):lo[g,k]=b.support(g,-axis)[k];hi[g,k]=b.support(g,axis)[k]
step=.005;xs=np.arange(-1.8,1.8,step);ys=np.arange(0,.60,step);free=np.zeros((len(ys),len(xs)),bool);supports=[];objects=[]
for g,n in enumerate(ch.gnames):
 if not n.startswith(('counter_','sink_front_rim','sink_back_rim')) or abs(hi[g,2]-.85)>1e-6:continue
 mx=(xs>=lo[g,0]-1e-9)&(xs+step<=hi[g,0]+1e-9);my=(ys>=lo[g,1]-1e-9)&(ys+step<=hi[g,1]+1e-9)
 free[np.ix_(my,mx)]=True;supports.append(n)
supported=free.copy()
for g,n in enumerate(ch.gnames):
 if n.startswith(('counter','north_wall','south_','floor','idle_full_sweep_cover','cabinet_door_sweep','outlet_access','r07_open_door_')):continue
 if hi[g,2]<=.855 or lo[g,2]>=1.35-1e-9:continue
 mx=(xs+step>lo[g,0]-.01)&(xs<hi[g,0]+.01);my=(ys+step>lo[g,1]-.01)&(ys<hi[g,1]+.01)
 if mx.any() and my.any():free[np.ix_(my,mx)]=False;objects.append(n)
def describe(mask,yy):
 heights=np.zeros(len(xs),int);best=(0,None)
 for j,row in enumerate(mask):
  heights=np.where(row,heights+1,0);stack=[]
  for x,h in enumerate(np.r_[heights,0]):
   start=x
   while stack and stack[-1][1]>h:
    a,hh=stack.pop();area=(x-a)*hh*step**2
    if area>best[0]:best=(area,[float(xs[a]),float(xs[x-1]+step),float(yy[j]-step*(hh-1)),float(yy[j]+step)])
    start=a
   if not stack or stack[-1][1]<h:stack.append((start,h))
 return dict(total_free_area_m2=float(mask.sum()*step**2),largest_rectangle_area_m2=best[0],xy_rectangle_m=best[1])
strip=ys+step<=.23000001
out=dict(layout=ID,model_xml=idle['model_xml'],model_sha256=hashlib.sha256(ch.xml.encode()).hexdigest(),park_snapshot_pass=idle['snapshot_pass'],connected_idle_qualified=False,grid_mm=5,object_expansion_mm=10,height_interval_m=[.855,1.35],whole_counter=describe(free,ys),front_strip=describe(free[strip],ys[strip]),supported_area_m2=float(supported.sum()*step**2),supports=supports,obstacles=objects,scope='Total supported clear cells and largest contiguous axis-aligned rectangle are separate. Full appliance, stored-object and parked-robot AABB projections through work height are excluded with10mm expansion. Open sink excluded; this conservative layout metric is not a gate or ergonomic qualification.')
(O/'counter_area_v7.json').write_text(json.dumps(out,indent=2))
fig,ax=plt.subplots(figsize=(12,3.8));ax.imshow(np.where(~supported,0,np.where(free,2,1)),origin='lower',extent=[xs[0],xs[-1]+step,0,.6],vmin=0,vmax=2,cmap=matplotlib.colors.ListedColormap(['#d9d9d9','#bf6464','#77b895']),aspect='equal');ax.axhline(.23,color='navy',ls='--',label='Cabinet front / front strip boundary')
r=out['whole_counter']['xy_rectangle_m']
if r:ax.add_patch(plt.Rectangle((r[0],r[2]),r[1]-r[0],r[3]-r[2],fill=False,ec='black',lw=2))
ax.set(xlabel='Counter x (m)',ylabel='Depth y (m)',title=f'{ID}: populated park snapshot; green = conservatively free supported counter\nRed = occupied; grey = unsupported/sink. Connected idle remains unqualified.');ax.legend(loc='upper right',fontsize=8);fig.tight_layout();fig.savefig(H/'renders/counter_free_area.png',dpi=120);plt.close(fig)
print('COUNTER',out['whole_counter'],out['front_strip'])
