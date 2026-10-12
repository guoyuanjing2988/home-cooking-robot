"""Joint-independent fixed hardware obstruction certificates, without IK."""
import os,sys,json
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
ch=v.scene(104);q=ch.m.qpos0.copy();ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d)
def movable(g):
 b=int(ch.m.geom_bodyid[g]);names=[]
 while b:
  for j in range(ch.m.body_jntadr[b],ch.m.body_jntadr[b]+ch.m.body_jntnum[b]):names.append(mujoco.mj_id2name(ch.m,mujoco.mjtObj.mjOBJ_JOINT,j))
  b=int(ch.m.body_parentid[b])
 return names
hits,_,_=v.f.contacts(ch,q);rows=[]
for hit in hits:
 pair=hit['pair'];ids=[ch.gnames.index(n) for n in pair];anc=[movable(g) for g in ids]
 if all(not any(n not in ('rail_lock','anchor_lock') for n in a) for a in anc):
  gap=mujoco.mj_geomDistance(ch.m,ch.d,*ids,1.,None)
  rows.append(dict(pair=pair,gap_m=gap,required_gap_m=.010 if any(ch.robot[g] for g in ids) else .005,joint_ancestors=anc,proof='Both full solids have no movable joint ancestors. All arm and carriage coordinates leave this separation unchanged.'))
out=dict(layout=v.ID,global_fixed_obstructions=rows,all_poses_rejected=bool(rows),scope='A fixed obstruction excludes this exact installed layout, not alternative track, mount, station or arm designs.')
(v.O/'layouts'/f'{v.ID}_fixed_obstructions.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
