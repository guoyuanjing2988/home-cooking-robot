import os,sys,json
os.environ['R07_LAYOUT']=sys.argv[1]
import numpy as np,mujoco
import runtime_v7_r07 as v
from distance import Bounds
import itertools
ch=v.scene(0);m,d=ch.m,ch.d;a=m.geom('rail_beam_0').id;b=m.geom('R_geom_base_source1').id;ix=ch.qa['R_carriage_x'];lo,hi=m.jnt_range[ch.jid['R_carriage_x']];q=m.qpos0.copy();q[ix]=0;d.qpos[:]=q;mujoco.mj_forward(m,d);bounds=Bounds(ch,v.f.required);beamR=d.geom_xmat[a].reshape(3,3).copy();center=d.geom_xpos[a].copy();half=m.geom_size[a].copy();anc=[];body=int(m.geom_bodyid[b])
surface=bounds.local[b]@d.geom_xmat[b].reshape(3,3).T+d.geom_xpos[b] if b in bounds.local else np.array([bounds.support(b,np.array(axis,dtype=float)) for axis in itertools.product((-1,0,1),repeat=3) if any(axis)])
local_surface=(surface-center)@beamR;projected=np.clip(local_surface,-half,half)@beamR.T+center;distances=np.linalg.norm(surface-projected,axis=1);j=int(np.argmin(distances));points=np.r_[projected[j],surface[j]];gap=float(distances[j])
while body:
 for j in range(m.body_jntadr[body],m.body_jntadr[body]+m.body_jntnum[body]):anc.append(mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,j))
 body=int(m.body_parentid[body])
beam_points=np.array([points[:3]+[x,0,0] for x in (lo,hi)]);local=(beam_points-center)@beamR
invariant=bool(m.geom_type[a]==6 and np.max(abs(beamR-np.eye(3)))<1e-8 and all(n in ('R_carriage_x','rail_lock','anchor_lock') for n in anc) and np.all(abs(local)<=half+1e-7))
rows=[]
for x in np.linspace(lo,hi,33):
 q[ix]=x;d.qpos[:]=q;mujoco.mj_forward(m,d);cert=bounds.pair(a,b);rows.append(dict(carriage_x_m=float(x),gap_mm=cert['lower_m']*1000,upper_gap_mm=cert['upper_m']*1000))
q[ix]=lo;d.qpos[:]=q;mujoco.mj_forward(m,d);swept=bounds.pair(b,a,translation=np.array([hi-lo,0,0]));swept['full_carriage_range_clear']=bool(swept['lower_m']>=.010-1e-6)
out=dict(layout=v.ID,pair=[ch.gnames[a],ch.gnames[b]],required_mm=10,rows=rows,minimum_sampled_gap_mm=min(r['gap_mm'] for r in rows),all_sampled_clear=all(r['gap_mm']>=10 for r in rows),arm_joint_ancestors=anc,translation_witness=dict(valid_over_full_carriage_range=invariant,beam_point_at_zero=points[:3].tolist(),base_point_at_zero=points[3:].tolist(),constant_upper_witness_gap_mm=gap*1000,beam_points_at_travel_limits=beam_points.tolist()),all_poses_rejected_by_this_pair=bool(invariant and gap<.010-1e-6),full_swept_convex_distance=swept,scope='Negative proof uses actual material support points whose beam-side translates within the unchanged box over full travel. Positive proof uses the preserved distance checker on the full convex prismatic sweep of the base. Only this pair is certified; full robot admission is separate. Native distmax1 probes were discarded as numerically spurious.')
(v.O/'layouts'/f'{v.ID}_band_pair_v7.json').write_text(json.dumps(out,indent=2));print('BAND_PAIR',v.ID,out['minimum_sampled_gap_mm'],out['all_poses_rejected_by_this_pair'])
