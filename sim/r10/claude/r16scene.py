"""R16 layout still: python r16scene.py out.png [cfg key=value ...] (no arm pose: the arm at q0)."""
import sys,json,numpy as np,mujoco
from PIL import Image
import chain
from scene import build
from dress import dress,HIDE
KV=dict(a.split('=',1) for a in sys.argv[2:])
extra={k:json.loads(v) for k,v in KV.items() if k.startswith('r1')}
cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,**extra);tree,_=build(cfg,None)
m=dress(tree);d=mujoco.MjData(m);d.qpos[0]=float(KV.get('CX',.3));mujoco.mj_forward(m,d)
ims=[]
for cam in [(125,-25,1.6),(90,-60,1.4),(180,-15,1.3)]:
 rr=mujoco.Renderer(m,560,700);c=mujoco.MjvCamera();c.lookat[:]=[1.3,.2,1.0];c.azimuth,c.elevation,c.distance=cam
 o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0;rr.update_scene(d,c,o);ims.append(Image.fromarray(rr.render()));rr.close()
S=Image.new('RGB',(700*len(ims),560));[S.paste(im,(700*i,0)) for i,im in enumerate(ims)];S.save(sys.argv[1]);print(sys.argv[1])
