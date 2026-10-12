"""Find a narrow, horizontal folded UR5e posture; source models stay read-only."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json,copy,math
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np,mujoco
from scipy.optimize import differential_evolution
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
src=ROOT/'sim/r01/concept/sources/menagerie/universal_robots_ur5e/ur5e.xml'
r=ET.parse(src).getroot();r.find('compiler').set('meshdir',str(src.parent/'assets'))
base=r.find('worldbody/body');base.set('quat','0 1 0 0')
for b in r.findall('.//body'):
    for g in list(b.findall('geom')):
        if g.get('class')=='visual':b.remove(g)
attach=base.find(".//site[@name='attachment_site']")
parent=next(b for b in base.iter('body') if attach in list(b))
arot=Rotation.from_quat(np.array([-1,1,0,0])[[1,2,3,0]])
tool=ET.SubElement(parent,'body',name='transport_gripper',pos=' '.join(map(str,np.array([0,.1,0])+arot.apply([0,0,.14]))),quat=' '.join(map(str,(arot*Rotation.from_euler('y',-90)).as_quat()[[3,0,1,2]])))
ET.SubElement(tool,'geom',name='gripper_palm',type='box',pos='-.10 0 0',size='.035 .040 .020',mass='1.0')
for sign in [-1,1]:ET.SubElement(tool,'geom',name='gripper_finger_'+str(sign),type='box',pos=f'-.035 {sign*.019} 0',size='.0375 .004 .010',mass='.1')
used={g.get('mesh') for g in r.iter('geom') if g.get('mesh')}
for a in list(r.find('asset').findall('mesh')):
    if a.get('name') not in used:r.find('asset').remove(a)
model=mujoco.MjModel.from_xml_string(ET.tostring(r,encoding='unicode'));d=mujoco.MjData(model)
def boxes(q):
    d.qpos[:]=q;mujoco.mj_forward(model,d)
    lo=[];hi=[]
    for i in range(model.ngeom):
        R=d.geom_xmat[i].reshape(3,3);s=model.geom_size[i];typ=int(model.geom_type[i]);p=d.geom_xpos[i]
        if typ==3:ext=np.abs(R[:,2])*s[1]+s[0]
        elif typ==5:ext=np.sqrt(np.maximum(0,1-R[:,2]**2))*s[0]+np.abs(R[:,2])*s[1]
        elif typ==6:ext=np.abs(R)@s
        else:ext=np.full(3,s[0])
        lo.append(p-ext);hi.append(p+ext)
    return np.min(lo,axis=0),np.max(hi,axis=0)
def collision_penalty():
    total=0;worst=1
    for i in range(model.ngeom):
        for j in range(i+1,model.ngeom):
            b1=model.geom_bodyid[i];b2=model.geom_bodyid[j]
            w1=int(model.body_weldid[b1]);w2=int(model.body_weldid[b2])
            if w1==w2 or model.body_weldid[model.body_parentid[w1]]==w2 or model.body_weldid[model.body_parentid[w2]]==w1:continue
            dist=mujoco.mj_geomDistance(model,d,i,j,.05,None)
            worst=min(worst,dist)
            total+=max(0,-dist+.001)**2
    return total,worst
def fun(q):
    lo,hi=boxes(q);width=hi-lo
    penalty=max(0,-.41-lo[2])**2+max(0,hi[2]-.001)**2+max(0,width[1]-.30)**2+max(0,width[0]-.80)**2+max(0,hi[0]-.10)**2+max(0,hi[1]-.07)**2
    cp,_=collision_penalty()
    return 2000000*(penalty+cp)+width[1]+.12*width[2]+.08*width[0]
res=differential_evolution(fun,[(-math.pi,math.pi),(-math.pi,math.pi),(-3.1415,3.1415),(-math.pi,math.pi),(-math.pi,math.pi),(-math.pi,math.pi)],popsize=15,maxiter=450,seed=20261007,workers=1,tol=.002,polish=True)
lo,hi=boxes(res.x);cp,gap=collision_penalty()
record=dict(arm='UR5e',source=str(src.relative_to(ROOT)),orientation_wxyz=[0,1,0,0],q_rad=res.x.tolist(),local_aabb_min_m=lo.tolist(),local_aabb_max_m=hi.tolist(),extent_m=(hi-lo).tolist(),minimum_nonadjacent_self_gap_m=gap,objective=float(res.fun),success=bool(res.success),evaluations=res.nfev,admitted=bool(gap>=0 and hi[2]<=.002 and lo[2]>=-.411 and hi[1]-lo[1]<=.301 and hi[0]<=.101 and hi[1]<=.071),note='OEM collision primitives plus unchanged R01 gripper palm70x80x40mm and fingers75x8x20mm, empty15mm jaw opening, 1.2kg. Held tools/food parked before passing. No detachable gripper required. Not task IK or joint torque certification.')
out=HERE/'results';out.mkdir(exist_ok=True);(out/'folded_arm.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
