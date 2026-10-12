"""Render the R13 printable parts (cad/r13/*.stl) as a labelled tile sheet (MuJoCo offscreen),
each part framed by its own bounding box.  python cad_view_r13.py cad/r13 out.png"""
import sys,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
D=sys.argv[1];OUT=sys.argv[2];TW,TH=480,400
PARTS=[('finger_P1','P1 手指：夹宽 5–45 mm'),('finger_P2','P2：29–69 mm'),('finger_P3','P3：53–93 mm'),('finger_P4','P4：77–117 mm'),
 ('finger_P5','P5：101–141 mm'),('finger_P6','P6：125–165 mm'),('finger_P7','P7：149–189 mm'),('fork_P2','托底叉指（两齿，走托盘槽）'),
 ('jaw_adapter','夹爪转接座（燕尾 + 锁销孔）'),('finger_rack_2pairs','换指架（每格一对手指）'),('slot_tray_section','V 肋托盘（一段 150×240）'),('food_basket','带提手小筐 Ø200（散料）')]
F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);tiles=[]
for n,t in PARTS:
 xml=f"""<mujoco><visual><headlight ambient=".5 .5 .5" diffuse=".45 .45 .45"/><global offwidth="{TW}" offheight="{TH}"/></visual>
<asset><mesh name="m" file="{D}/{n}.stl" scale=".001 .001 .001"/><material name="p" rgba="{'.25 .55 .78 1' if n.startswith(('finger','fork')) else '.84 .86 .9 1'}" specular=".4"/></asset>
<worldbody><light pos=".2 -.3 .5" dir="-.3 .5 -1" diffuse=".5 .5 .5"/><geom type="mesh" mesh="m" material="p"/></worldbody></mujoco>"""
 m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 v=m.mesh_vert[:m.mesh_vertnum[0]];w=d.geom_xpos[0]+v@d.geom_xmat[0].reshape(3,3).T;c=(w.min(0)+w.max(0))/2;ext=np.linalg.norm(w.max(0)-w.min(0))
 r=mujoco.Renderer(m,TH,TW);cam=mujoco.MjvCamera();cam.lookat[:]=c;cam.azimuth,cam.elevation,cam.distance=(225 if n.startswith(('finger_P','fork')) else 135),-28,1.9*ext
 r.update_scene(d,cam);im=r.render().copy();im[(im.sum(-1)<15)]=(246,247,249);r.close()
 im=Image.fromarray(im);dr=ImageDraw.Draw(im);dr.rectangle([0,TH-34,TW,TH],fill=(255,255,255));dr.text((10,TH-31),t,fill=(20,20,20),font=F);tiles.append(im)
cols=4;rows=(len(tiles)+cols-1)//cols;S=Image.new('RGB',(cols*TW,rows*TH+44),(255,255,255))
for i,im in enumerate(tiles):S.paste(im,((i%cols)*TW,44+(i//cols)*TH))
ImageDraw.Draw(S).text((12,8),'R13 打印件（概念 CAD，打印前需按大寰官方 STEP 核对夹爪孔位）：蓝 = 手指（PETG 主体 + TPU/硅胶软垫），灰 = 附件',fill=(0,0,0),font=F)
S.save(OUT);print(OUT)
