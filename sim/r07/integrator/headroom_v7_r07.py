"""Full terminal-body headroom at the proposed pose; not an IK certificate."""
import os,sys,json
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v7_r07 as v
from distance import Bounds
rows=[]
for index in (10,12,13,15,28,30,31,33,34,43,46,53):
 ch=v.scene(index);m,d=ch.m,ch.d;b=Bounds(ch,v.f.required);sg=v.items[index][1]
 for pi,hands in enumerate(sg['poses']):
  h=hands['R'];q=m.qpos0.copy()
  for label in ('minus','plus'):q[ch.qa['R_jaw_'+label]]=h['jaw_opening_m']/2
  d.qpos[:]=q;mujoco.mj_forward(m,d);site=m.site('R_prep').id;origin=d.site_xpos[site].copy();R=d.site_xmat[site].reshape(3,3).copy()
  for k in (0,1):
   desired=ch.target_rotation(h,k);parts=[]
   for g,name in enumerate(ch.gnames):
    rigid=m.body_weldid[m.geom_bodyid[g]]==m.body_weldid[m.site_bodyid[site]]
    if not name.startswith('R_') or not(ch.gripper(g) or ch.held[g] or rigid):continue
    # Transform all support extrema in desired world axes, retaining shapes.
    low=[];high=[]
    for axis in np.eye(3):
     axis_old=R@desired.T@axis
     low.append(float(((b.support(g,-axis_old)-origin)@R@desired.T+np.array(h['pos']))@axis))
     high.append(float(((b.support(g,axis_old)-origin)@R@desired.T+np.array(h['pos']))@axis))
    cabinet_overlap=any(high[0]>=a and low[0]<=z for a,z in ((-1.8,-.7),(-.1,.69),(1.47,1.8))) and high[1]>=.212 and low[1]<=.6 and high[2]>=1.35
    parts.append(dict(name=name,lo_m=low,hi_m=high,aabb_overlaps_closed_cabinet=cabinet_overlap))
   rows.append(dict(index=index,pose=pi,k=k,full_terminal_parts=parts,above_bottom_but_entirely_front=all(a['hi_m'][1]<.212 or a['hi_m'][2]<1.35 for a in parts),possible_cabinet_interference=[a['name'] for a in parts if a['aabb_overlaps_closed_cabinet']]))
out=dict(layout=v.ID,rows=rows,scope='Exact support extrema of full terminal/gripper/food solids transformed to declared target. AABB overlap is a screening flag, not penetration or impossibility proof. Full arm IK, static rules and motion still required.',closed_leaf_front_y_m=.212,cabinet_bottom_z_m=1.35)
(v.O/'layouts'/f'{v.ID}_headroom_v7.json').write_text(json.dumps(out,indent=2));print('HEADROOM',v.ID,len(rows),sum(not r['possible_cabinet_interference'] for r in rows))
