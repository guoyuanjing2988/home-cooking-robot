"""Fin Ray PRB model check: one finger fixed, a rigid probe (cylinder along z or
sphere) pressed into the front strap at a given point along the finger. Prints
probe force vs indentation and the tip's sideways motion (the Fin Ray wrap).
Usage: python finray_cal.py <K N*m/rad> [probe=cyl|sphere] [r=.0175] [x_frac=.45]"""
import sys,numpy as np,mujoco,xml.etree.ElementTree as E
import fingers
K=float(sys.argv[1]);probe=sys.argv[2] if len(sys.argv)>2 else 'cyl';r=float(sys.argv[3]) if len(sys.argv)>3 else .0175;xf=float(sys.argv[4]) if len(sys.argv)>4 else .45
d=dict(fingers.DESIGNS['R'],K=K);s=-1
import os
for k_ in ('kroot','krib','rib_tilt'):
 if os.environ.get(k_.upper()):d[k_]=float(os.environ[k_.upper()])
root=E.fromstring('<mujoco><option timestep=".0005" gravity="0 0 0" cone="elliptic" impratio="10"/><asset/><worldbody/><equality/><actuator/></mujoco>')
wb=root.find('worldbody');jaw=E.SubElement(wb,'body',name='G_jaw_minus',pos='0 0 0')
E.SubElement(jaw,'geom',name='G_finger_minus',type='box',size='.001 .001 .001',contype='0',conaffinity='0')
fingers.dyn_parts(root,jaw,s,d,'.5 .002 .0001')
# probe on a slide along +y... the minus finger's pad faces +y; the probe starts on the item side
x=-d['D']+xf*d['P'];y0=fingers.local(d,s,x,0,0)[1]
pb=E.SubElement(wb,'body',name='probe',pos=f"{x-(.015-d['D'])} {y0+r+.002} {-d['c']}")
E.SubElement(pb,'joint',name='py',type='slide',axis='0 1 0',damping='5')
E.SubElement(pb,'geom',type='cylinder' if probe=='cyl' else 'sphere',size=f'{r} .04' if probe=='cyl' else f'{r}',mass='.1',contype='1',conaffinity='4',friction='0 0 0')
E.SubElement(root.find('actuator'),'position',joint='py',kp='20000',forcerange='-200 200')
m=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));dd=mujoco.MjData(m)
tip=m.body(f'G_jaw_minus_f{d["n"]-1}').id
mujoco.mj_forward(m,dd);tip0=dd.xpos[tip].copy()
def tipend():
 R=dd.xmat[tip].reshape(3,3);L=np.linalg.norm(np.diff([fingers.local(d,s,x_,0,0) for x_ in np.linspace(-d['D'],-d['D']+d['P'],d['n']+1)][-2:],axis=0));return dd.xpos[tip]+R@[L,0,0]
end0=tipend()
print('K',K,'probe',probe,'r',r,'x_frac',xf)
for ind in (.002,.005,.01,.015,.02,.025):
 dd.ctrl[0]=-(.002+ind)
 for _ in range(4000):mujoco.mj_step(m,dd)
 f=-dd.actuator_force[0];te=tipend()
 ncon=sum(1 for c in dd.contact[:dd.ncon])
 print(f' indent {1000*ind:4.0f} mm  force {f:7.2f} N  probe y {1000*(dd.qpos[m.jnt_qposadr[m.joint('py').id]]):6.1f} mm  tip moves toward item {1000*(te[1]-end0[1]):6.2f} mm  contacts {ncon}')
