"""R14 overview stills: the docked cart + UR5e at checked R14 poses (r14reach results)
in the dressed kitchen with the R14 stations. python r14overview.py out.png"""
import sys,json,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
import chain
from scene import build
from dress import dress,HIDE
SHOTS=[('reach_cup_fill.json',dict(r14_cup=True),'调料站：料杯放到吊柜下的出料口（已通过碰撞检查）',(.5,.2,1.1),(115,-12,1.45)),
 ('reach_pt0.830_0.070_1.170_0.000_1.000_0.000_-0.940_0.000_0.342.json',dict(r14_drum=True),'灶台：从正面握分格转筒，转腕倒料（4 个角度都通过）',(.82,.15,1.05),(115,-14,1.45))]
F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);ims=[]
for fn,extra,title,look,cam in SHOTS:
 r=json.load(open('results/r14/'+fn));cfg=chain.chain_cfg('SD',r14=True,present=[],**extra);tree,_=build(cfg,None)
 m=dress(tree);d=mujoco.MjData(m);q=np.array(r['best_q']);d.qpos[:len(q)]=q;mujoco.mj_forward(m,d)
 rr=mujoco.Renderer(m,600,900);c=mujoco.MjvCamera();c.lookat[:]=look;c.azimuth,c.elevation,c.distance=cam;o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0
 rr.update_scene(d,c,o);im=Image.fromarray(rr.render());ImageDraw.Draw(im).rectangle([0,0,900,34],fill=(255,255,255));ImageDraw.Draw(im).text((8,4),title,fill=(0,0,0),font=F);ims.append(im);rr.close()
S=Image.new('RGB',(1800,600));[S.paste(im,(900*i,0)) for i,im in enumerate(ims)];S.save(sys.argv[1]);print(sys.argv[1])
