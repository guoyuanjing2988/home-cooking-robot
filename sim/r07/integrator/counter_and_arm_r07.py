import json
import numpy as np,mujoco
import os,sys
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v2_r07 as v
rt=v.rt
H=rt.H;O=rt.O
def load(path):
 ch=object.__new__(rt.Checker);ch.desc=rt.s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(mujoco.MjModel.from_xml_path(str(path)));ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
 return ch
idle=json.loads((O/'idle.json').read_text());ch=load(H/idle['doors_model_xml']);q=np.r_[idle['q'],np.zeros(len(idle['doors']))];rt.f.contacts(ch,q);b=ch.bounds
lo=np.zeros((ch.m.ngeom,3));hi=lo.copy()
for g in range(ch.m.ngeom):
 if ch.m.geom_type[g]==0:lo[g]=-1e6;hi[g]=1e6;continue
 for k,axis in enumerate(np.eye(3)):lo[g,k]=b.support(g,-axis)[k];hi[g,k]=b.support(g,axis)[k]
arms={}
for side in ('R','L'):
 ids=[g for g,n in enumerate(ch.gnames) if n.startswith(side+'_') and ch.robot[g]]
 mn=np.min(lo[ids],axis=0);mx=np.max(hi[ids],axis=0)
 arms[side]=dict(all_arm_carriage_EOAT_AABB_min_m=mn.tolist(),max_m=mx.tolist(),size_m=(mx-mn).tolist(),front_reserve_mm=(mn[1]-.24)*1000,cabinet_reserve_mm=(1.34-mx[2])*1000,scope='Full populated completed-meal geometry: snapshot '+('PASS' if idle['snapshot_pass'] else 'FAIL')+'. Full OEM solids, stored tools and retained output contents. Dimensions alone do not establish a connected fold or meal-end return.')
# Conservative whole-height front-strip occupancy: fixed/raw/stored objects
# projected with10mm person workspace separation. Counter surface is usable.
xs=np.arange(-1.8,1.8,.005);ys=np.arange(0,.23,.005);free=np.zeros((len(ys),len(xs)),bool);objects=[]
# A clear projection over the open sink is not usable countertop. Require
# every5mm cell to be fully supported by an actual original top/rim solid.
support_names=[]
for g,n in enumerate(ch.gnames):
 if not (n.startswith('counter_') or n.startswith(('sink_front_rim','sink_back_rim'))):continue
 if abs(hi[g,2]-.85)>1e-6:continue
 maskx=(xs>=lo[g,0]-1e-9)&(xs+.005<=hi[g,0]+1e-9);masky=(ys>=lo[g,1]-1e-9)&(ys+.005<=hi[g,1]+1e-9)
 if maskx.any() and masky.any():free[np.ix_(masky,maskx)]=True;support_names.append(n)
for g,n in enumerate(ch.gnames):
 if ch.robot[g] or n.startswith(('counter','north_wall','south_','floor','cabinet_door_sweep','outlet_access','r07_open_door_')):continue
 if hi[g,2]<=.855 or lo[g,2]>=1.35-1e-9:continue
 if hi[g,1]<-.01 or lo[g,1]>.24:continue
 maskx=(xs+.005>lo[g,0]-.01)&(xs<hi[g,0]+.01);masky=(ys+.005>lo[g,1]-.01)&(ys<hi[g,1]+.01)
 if maskx.any() and masky.any():free[np.ix_(masky,maskx)]=False;objects.append(n)
best=(0,None)
for a in range(len(ys)):
 cols=np.ones(len(xs),bool)
 for end in range(a,len(ys)):
  cols &=free[end];start=None
  for x in range(len(xs)+1):
   yes=x<len(xs) and cols[x]
   if yes and start is None:start=x
   if not yes and start is not None:
    area=(x-start)*(end-a+1)*.005**2
    if area>best[0]:best=(area,[xs[start],xs[x-1]+.005,ys[a],ys[end]+.005])
    start=None
rt.write('counter_and_arm_envelopes.json',dict(arms=arms,free_front_strip=dict(area_m2=best[0],xy_rectangle_m=best[1],objects_affecting_strip=objects,method='5mm conservative projected occupancy of full populated candidate scene, all heights0.855..1.35m,10mm expansion around objects, only cells fully supported by original countertop/rim solids admitted; the open sink is excluded. This gives a clear human work rectangle while appliances stay. No usable accepted idle is claimed.'),all_robot_strip_clear=all(r['front_strip_clear'] for r in idle['robot_parts'])))
print('arms',arms,'free area',best)
