"""R19 hub roadmap contact sheet: the tuck at a hub station and the 7 free-move endpoints (empty
gripper, jaws open) in the union free-move scene of r19hub.py (lever shown closed AND open, lid on
the pot AND in the rack: that is how the free moves are checked).
python r19hub_render.py [OUT=results/r19/hub/hubs_sheet.png]"""
import sys;sys.path.insert(0,'.')
sys.argv=[sys.argv[0],'none']+sys.argv[1:]
import numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
import r19hub as R
from dress import dress,HIDE
KV=dict(a.split('=',1) for a in sys.argv[2:]);out=KV.get('OUT','results/r19/hub/hubs_sheet.png')
tree,_=R.union_tree();m=dress(tree);d=mujoco.MjData(m);H=R.load_tuck()
panels=[('H_WOK','tuck at hub H_WOK (cart .172)')]+[(e,f"{e} (cart {H['endpoints'][e]['q_shifted'][0]:.3f})") for e in R.ENDS]
W,Hh=640,420;F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
rr=mujoco.Renderer(m,Hh,W);o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0
sheet=Image.new('RGB',(W*4,Hh*2),(255,255,255))
for k,(n,lab) in enumerate(panels):
 q=R.node_q(n,H);d.qpos[:len(q)]=q;mujoco.mj_forward(m,d)
 c=mujoco.MjvCamera();c.lookat[:]=[q[0]+.35,.05,1.15];c.azimuth,c.elevation,c.distance=150,-18,2.3
 rr.update_scene(d,c,o);im=Image.fromarray(rr.render());ImageDraw.Draw(im).text((10,8),lab,fill=(0,0,0),font=F)
 sheet.paste(im,((k%4)*W,(k//4)*Hh))
rr.close();sheet.save(out);print(out)
