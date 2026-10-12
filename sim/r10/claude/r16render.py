"""R16 stills of checked walk poses: python r16render.py out.png <walk name>:<path index>:<title> ...
(results/r16/walk_<name>.json; the scene is rebuilt with the walk's held object, grasp sense and
scene keys, in the final R16 design: kitchen16.set_design(**DESIGN)). Camera: CAM=az,el,dist LOOK=x,y,z."""
import sys,json,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
import chain
from scene import build
from dress import dress,HIDE
import kitchen16 as K
DESIGN=dict(pot_h=.12,rack=.04,lid_a=0.,car_a=45.,rack_ry=90.);K.set_design(**DESIGN)
KV=dict(a.split('=',1) for a in sys.argv[2:] if a.split('=')[0] in ('CAM','LOOK'))
specs=[a for a in sys.argv[2:] if a.split('=')[0] not in ('CAM','LOOK')]
cam=[float(x) for x in KV.get('CAM','120,-28,1.7').split(',')];look=[float(x) for x in KV.get('LOOK','1.05,.1,1.0').split(',')]
F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);ims=[]
for sp in specs:
 name,i,title=sp.split(':',2);w=json.load(open(f'results/r16/walk_{name}.json'));q=np.array(w['path'][int(i)]['q'])
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,r16=True,r16_held=dict(obj=w['obj'],T_tool_obj=K.T_tool_obj(w['obj'],w['jaw_sign']).tolist()),**w['scene'])
 tree,_=build(cfg,None);m=dress(tree);d=mujoco.MjData(m);d.qpos[:len(q)]=q;mujoco.mj_forward(m,d)
 rr=mujoco.Renderer(m,600,720);c=mujoco.MjvCamera();c.lookat[:]=look;c.azimuth,c.elevation,c.distance=cam
 o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0;rr.update_scene(d,c,o);im=Image.fromarray(rr.render())
 dr=ImageDraw.Draw(im);dr.rectangle([0,0,720,32],fill=(255,255,255));dr.text((8,4),title,fill=(0,0,0),font=F);ims.append(im);rr.close()
S=Image.new('RGB',(720*2,600*((len(ims)+1)//2)),(255,255,255))
for k,im in enumerate(ims):S.paste(im,(720*(k%2),600*(k//2)))
S.save(sys.argv[1]);print(sys.argv[1])
