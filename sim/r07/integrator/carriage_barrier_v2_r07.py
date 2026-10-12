"""Configuration-independent fixed-base and axisymmetric-shoulder rail barriers."""
import os,sys,json,xml.etree.ElementTree as E,time
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v2_r07 as v
began=time.monotonic();cfg=v.cfg
tree,meta=v.build(dict(cfg,transport_only=True));ch=object.__new__(v.Checker);ch.desc=v.s.ck.hand([0,0,1]);ch.bind_model(mujoco.MjModel.from_xml_string(E.tostring(tree.getroot(),encoding='unicode')));m,d=ch.m,ch.d
rows=[];fixed_by_side={}
for side in ('R','L'):
 arm=v.s.ck.ARMS[side];fixed=[];symmetric=[]
 for g,n in enumerate(ch.gnames):
  if not n.startswith(side+'_'):continue
  body=int(m.geom_bodyid[g]);deps=[]
  while body:
   for j in range(m.body_jntadr[body],m.body_jntadr[body]+m.body_jntnum[body]):
    name=m.joint(j).name
    if name in arm:deps.append(name)
   body=int(m.body_parentid[body])
  if not deps:fixed.append(g)
  elif side=='R' and deps==[arm[0]] and m.geom_type[g]==3:
   # Source shoulder capsule local centre and longitudinal axis lie on J1.
   body=int(m.geom_bodyid[g]);j=ch.jid[arm[0]]
   axis=m.jnt_axis[j];offset=m.geom_pos[g]-m.jnt_pos[j];rot=np.empty(9);mujoco.mju_quat2Mat(rot,m.geom_quat[g])
   if np.linalg.norm(np.cross(offset,axis))<1e-9 and np.linalg.norm(np.cross(rot.reshape(3,3)[:,2],axis))<1e-9:symmetric.append(g)
 fixed_by_side[side]=fixed
 obstacles=[g for g,n in enumerate(ch.gnames) if 'faucet' in n]
 samples=[];q=m.qpos0.copy();ix=ch.qa[side+'_carriage_x']
 for x in np.linspace(*m.jnt_range[ch.jid[side+'_carriage_x']],2011):
  q[ix]=x;d.qpos[:]=q;mujoco.mj_forward(m,d);worst=None
  for g in fixed+symmetric:
   for e in obstacles:
    gap=float(mujoco.mj_geomDistance(m,d,g,e,.2,None))
    if worst is None or gap<worst['gap_m']:worst=dict(pair=[ch.gnames[g],ch.gnames[e]],gap_m=gap)
  samples.append(dict(carriage_x_m=float(x),**worst))
 blocked=[s for s in samples if s['gap_m']<.01-1e-6]
 rows.append(dict(side=side,fixed_geoms=[ch.gnames[g] for g in fixed],axisymmetric_geoms=[ch.gnames[g] for g in symmetric],samples=samples,blocked_sample_count=len(blocked),worst=min(samples,key=lambda s:s['gap_m']),barrier_exists=bool(blocked),proof='Fixed geoms have no arm-joint ancestors. The principal shoulder capsule is coaxial with J1 and axisymmetric; its shape is unchanged by every arm joint. At any rejected carriage X all arm configurations fail the10mm faucet gap. Continuity forbids a carriage path crossing that X. This is an exact forbidden separating X plane, not an interval claim or an under-cabinet architecture impossibility proof.'))
q=m.qpos0.copy()
for side in ('R','L'):q[ch.qa[side+'_carriage_x']]=0
d.qpos[:]=q;mujoco.mj_forward(m,d);cross=[]
for a in fixed_by_side['R']:
 for b in fixed_by_side['L']:
  gap=float(mujoco.mj_geomDistance(m,d,a,b,.02,None))
  if gap<.01-1e-6:cross.append(dict(pair=[ch.gnames[a],ch.gnames[b]],gap_mm=gap*1000,required_mm=10))
passing=dict(impossible_order_swap=bool(cross),at_equal_carriage_x=cross,proof='Both solids are rigid to their respective X-only carriages and independent of every arm joint. Their relative transform at equal carriage X is independent of the common X value. An order swap must cross equality by the intermediate-value theorem. Any forbidden fixed pair therefore rules out passing for this hardware; this does not rule out meals with preserved carriage order.')
(v.O/'layouts'/f'{v.ID}_carriage_barriers.json').write_text(json.dumps(dict(layout=v.ID,rows=rows,passing=passing,elapsed_s=time.monotonic()-began),indent=2))
print(v.ID,[(r['side'],r['blocked_sample_count'],r['worst']) for r in rows],flush=True)
