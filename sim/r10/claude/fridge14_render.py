"""R14 fridge stills: checked poses from the docked cart (x = -1.48): handle at 0° and 35° (from
the continuous arc path, results/r14/fridge_arc_path.json) and the top-down pinch on the cold
box in the door bin with the door at 35° (r14reach). python fridge14_render.py out.png"""
import sys,json,glob,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
import chain
from scene import build
from dress import dress,HIDE
P=json.load(open('results/r14/fridge_arc_path.json'));A=P['angles']
box=json.load(open(glob.glob('results/r14/reach_pt*_1.060_0.000_0.000_-1.000_*_cx-1.48_cy-0.21_fr35_box_grasp.json')[0]))
SHOTS=[(0,P['q_path'][A.index(0.)],dict(),'① 握住把手（门关着，一根手指插在把手和门之间）'),
 (35,P['q_path'][A.index(35.)],dict(),'② 沿门的圆弧拉到 35°（0→35° 一条连续关节路径）'),
 (35,box['best_q'],dict(r14_held_box=True),'③ 松开把手，从上面夹门架料盒的提手')]
F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);ims=[]
for deg,q,extra,title in SHOTS:
 cfg=chain.chain_cfg('SD',r14=True,present=[],r14_fridge=True,r14_fridge_door_deg=deg,r14_rbin_z=.85,**extra);tree,_=build(cfg,None)
 m=dress(tree);d=mujoco.MjData(m);q=np.array(q);d.qpos[:len(q)]=q;mujoco.mj_forward(m,d)
 rr=mujoco.Renderer(m,620,760);c=mujoco.MjvCamera();c.lookat[:]=(-2.0,-.25,.95);c.azimuth,c.elevation,c.distance=127,-24,2.0
 o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0;rr.update_scene(d,c,o);im=Image.fromarray(rr.render())
 dr=ImageDraw.Draw(im);dr.rectangle([0,0,760,32],fill=(255,255,255));dr.text((8,4),title,fill=(0,0,0),font=F);ims.append(im);rr.close()
S=Image.new('RGB',(760*len(ims),620));[S.paste(im,(760*i,0)) for i,im in enumerate(ims)];S.save(sys.argv[1]);print(sys.argv[1])
