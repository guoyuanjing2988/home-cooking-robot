"""Render the dual-zone finger CAD (cad/*.stl) on a PGC-140-50 envelope with a tomato
and a carrot, MuJoCo offscreen.  python cad_view.py cad out.png"""
import sys,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
D=sys.argv[1];OUT=sys.argv[2];C=20;Q=35+1-4  # finger datum distance from the item centre (70 mm tomato, 4 mm squeeze)
def scene(item):
 it=('<geom type="ellipsoid" size=".035 .035 .03" pos=".045 0 0" rgba=".85 .18 .12 1" material="food"/>' if item=='tomato' else
     '<geom type="capsule" size=".0175 .07" pos=".045 0 0" rgba=".93 .5 .12 1" material="food"/>')
 q=Q if item=='tomato' else 17.5
 return f"""<mujoco><compiler meshdir="{D}"/>
<visual><rgba haze=".93 .94 .95 1"/><headlight ambient=".35 .35 .35" diffuse=".5 .5 .5"/><quality shadowsize="4096"/><global offwidth="1600" offheight="1000"/></visual>
<asset><mesh name="b" file="finger_body_minus.stl" scale=".001 .001 .001"/><mesh name="c" file="pad_carrier_minus.stl" scale=".001 .001 .001"/><mesh name="s" file="pad_skin_minus.stl" scale=".001 .001 .001"/>
<mesh name="bp" file="finger_body_plus.stl" scale=".001 .001 .001"/><mesh name="cp" file="pad_carrier_plus.stl" scale=".001 .001 .001"/><mesh name="sp" file="pad_skin_plus.stl" scale=".001 .001 .001"/>
<material name="petg" rgba=".88 .9 .93 1" specular=".4" shininess=".5"/><material name="tpu" rgba=".2 .55 .75 1" specular=".2"/><material name="carr" rgba=".95 .75 .2 1"/>
<material name="food" specular=".5" shininess=".6"/><material name="pgc" rgba=".25 .27 .3 1" specular=".5"/>
<texture name="sky" type="skybox" builtin="gradient" rgb1=".97 .97 .98" rgb2=".86 .88 .9" width="64" height="256"/><texture name="g" type="2d" builtin="checker" rgb1=".93 .93 .93" rgb2=".86 .86 .86" width="64" height="64"/><material name="floor" texture="g" texrepeat="20 20"/></asset>
<worldbody><light pos=".1 -.3 .4" dir="-.2 .6 -.8" diffuse=".6 .6 .6" castshadow="true"/><geom type="plane" size="1 1 .01" pos="0 0 -.06" material="floor"/>
<geom type="box" size=".06925 .0375 .0375" pos="-.06925 0 {C/1000}" material="pgc"/>
<body pos="0 {-q/1000} 0"><geom type="mesh" mesh="b" material="petg"/><geom type="mesh" mesh="c" material="carr"/><geom type="mesh" mesh="s" material="tpu"/></body>
<body pos="0 {q/1000} 0"><geom type="mesh" mesh="bp" material="petg"/><geom type="mesh" mesh="cp" material="carr"/><geom type="mesh" mesh="sp" material="tpu"/></body>
{it}</worldbody></mujoco>"""
ims=[]
for item,views in (('tomato',((150,-25,.33),(200,-60,.30))),('carrot',((120,-15,.33),))):
 m=mujoco.MjModel.from_xml_string(scene(item));d=mujoco.MjData(m);mujoco.mj_forward(m,d);r=mujoco.Renderer(m,500,640)
 for az,el,dist in views:
  cam=mujoco.MjvCamera();cam.lookat[:]=[.02,0,.005];cam.azimuth,cam.elevation,cam.distance=az,el,dist;r.update_scene(d,cam);ims.append(r.render().copy())
 r.close()
img=Image.fromarray(np.concatenate(ims,1));dr=ImageDraw.Draw(img);f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
for i,t in enumerate(('番茄：软中带轻夹（每指约 5 N）','番茄（俯视）','胡萝卜：硬边夹紧（40 N）')):
 dr.rectangle([8+640*i,6,8+640*i+16+int(f.getlength(t)),40],fill=(255,255,255));dr.text((16+640*i,8),t,fill=(20,20,20),font=f)
img.save(OUT);print(OUT)
