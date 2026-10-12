"""Audit sensor covers even though the source classifies them as environment."""
from v7_common import *
data=read('idle.json');ch=v.scene(0);ch.xml=(I/data['model_xml']).read_text();ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml));ch.d.qpos[:]=data['q'];mujoco.mj_forward(ch.m,ch.d);f.contacts(ch,np.array(data['q']))
rows=[]
for g,name in enumerate(ch.gnames):
    if 'sensor' not in name:continue
    lo=np.array([ch.bounds.support(g,-u)[k] for k,u in enumerate(np.eye(3))]);hi=np.array([ch.bounds.support(g,u)[k] for k,u in enumerate(np.eye(3))])
    # Original actual door hinge is at y=.230. Its points are local x in
    # [0,width] for left hinges or [-width,0] for right, local y in [-.018,0].
    # With either outward hinge sign and theta in [0,pi/2], y<=.230 always.
    gap=max(lo[1]-.230,1.35-hi[2]);strip=bool(np.all(hi>[-1.8,0,.85]) and np.all(lo<[1.8,.23,1.35]));corridor=bool(np.all(hi>[-1.6,-.75,.85]) and np.all(lo<[.6,-.05,1.85]))
    rows.append(dict(name=name,source_robot_classification=bool(ch.robot[g]),lo_m=lo.tolist(),hi_m=hi.tolist(),door_sweep_lower_gap_mm=float(gap*1000),front_strip_intersection=strip,corridor_intersection=corridor,wall_lower_gap_mm=float((.6-hi[1])*1000),pass_=bool(gap>=.01-1e-9 and not strip and not corridor)))
dump('auxiliary_idle.json',dict(rows=rows,pass_=all(r['pass_'] for r in rows),method='Exact source-shape support bounds. All outward-swing actual door points have y<=.230m throughout 0..90deg; rearward sensors use this separating plane rather than the moving-arm vertical certificate.'))
print('AUXILIARY_IDLE',rows)
