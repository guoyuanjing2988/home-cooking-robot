"""Diagnostic stored-bowl / fixed-appliance intersections, no exclusions."""
import os,sys,json
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v7_r07 as v
import mujoco
ch=v.scene(0);m,d=ch.m,ch.d;mujoco.mj_forward(m,d)
bowls=[i for i,n in enumerate(ch.gnames) if n.startswith('stored_bowl_')]
fixtures=[i for i,n in enumerate(ch.gnames) if n.startswith(('linear_peeler_','bfp610_','secondary_','dock_wash_pad','dock_eye_core_spoon'))]
hits=[]
for a in bowls:
 for b in fixtures:
  gap=float(mujoco.mj_geomDistance(m,d,a,b,.01,None))
  if gap<-.000001:hits.append(dict(pair=[ch.gnames[a],ch.gnames[b]],signed_gap_mm=gap*1000))
out=dict(layout=v.ID,pass_=not hits,penetrations=hits,scope='Stored full bowl solids against peeler/processor/secondary/tool docks. Fixed/fixed packing diagnosis, separate from robot gap rules; no operational credit.')
(v.O/'layouts'/f'{v.ID}_dock_packing_v7.json').write_text(json.dumps(out,indent=2));print('DOCK_PACKING',v.ID,len(hits))
