"""Render the R14 concept CAD (cad/r14/*.stl): seasoning station and staple module as
assemblies (cabinet translucent), plus the pour drum and the robot cup.
python cad_view_r14.py cad/r14 out.png"""
import sys,os,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
D=sys.argv[1];OUT=sys.argv[2];TW,TH=720,560
COL={'cabinet':'.75 .55 .35 .18','bottles':'.55 .35 .2 .9','pumps':'.25 .3 .35 1','paste_syringes':'.85 .3 .2 1','augers':'.85 .87 .9 1','nozzle_head':'.6 .62 .65 1',
 'scale_platform':'.3 .3 .32 1','cup_on_scale':'.95 .95 .95 1','cup_rack':'.9 .9 .92 1','rice_hopper':'.95 .93 .85 .9','flour_hopper':'.97 .97 .97 .9','outlets':'.6 .62 .65 1','pot_platform':'.3 .3 .32 1',
 'drum':'.85 .9 .95 1','cup':'.95 .95 .95 1'}
def tile(names,title,az=145,el=-22,scale=1.,label_lines=()):
 a='';g=''
 for i,n in enumerate(names):
  key=n.split('_',1)[1] if n.startswith(('station_','staples_')) else n
  a+=f'<mesh name="m{i}" file="{D}/{n}.stl" scale=".001 .001 .001"/>';g+=f'<geom type="mesh" mesh="m{i}" rgba="{COL.get(key,".8 .8 .8 1")}"/>'
 xml=f"""<mujoco><visual><headlight ambient=".5 .5 .5" diffuse=".45 .45 .45"/><global offwidth="{TW}" offheight="{TH}"/></visual><asset>{a}</asset>
<worldbody><light pos=".4 -.8 1.2" dir="-.3 .6 -1" diffuse=".5 .5 .5"/>{g}</worldbody></mujoco>"""
 m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 V=np.vstack([d.geom_xpos[k]+m.mesh_vert[m.mesh_vertadr[m.geom_dataid[k]]:m.mesh_vertadr[m.geom_dataid[k]]+m.mesh_vertnum[m.geom_dataid[k]]]@d.geom_xmat[k].reshape(3,3).T for k in range(m.ngeom)])
 c=(V.min(0)+V.max(0))/2;ext=np.linalg.norm(V.max(0)-V.min(0))
 r=mujoco.Renderer(m,TH,TW);cam=mujoco.MjvCamera();cam.lookat[:]=c;cam.azimuth,cam.elevation,cam.distance=az,el,1.5*ext*scale
 r.update_scene(d,cam);im=r.render().copy();im[im.sum(-1)<15]=(246,247,249);r.close()
 im=Image.fromarray(im);dr=ImageDraw.Draw(im);F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19);f2=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
 dr.rectangle([0,0,TW,30],fill=(255,255,255));dr.text((8,4),title,fill=(10,10,10),font=F)
 for i,l in enumerate(label_lines):dr.text((10,TH-22*(len(label_lines)-i)-6),l,fill=(30,30,30),font=f2)
 return im
st=[n[:-4] for n in os.listdir(D) if n.startswith('station_')];sp=[n[:-4] for n in os.listdir(D) if n.startswith('staples_')]
T=[tile(st,'吊柜调料站（80 cm 吊柜，概念）',labels:=None) if False else tile(st,'吊柜调料站（80 cm 吊柜，概念）',label_lines=('上层：12 瓶液体（盐水、糖浆、味精水、生抽、老抽、料酒、2 种醋、蚝油、香油、红油、水淀粉）','中层：12 个步进蠕动泵 + 2 个酱料推杆（豆瓣酱、甜面酱）','底层：4 个密封螺杆粉罐（鸡精、胡椒、花椒面、玉米淀粉）+ 花椒振动给料','柜下：出料头 + 称重/搅拌台（0.1 g）+ 料杯架；油从地柜 5 L 桶泵上来')),
 tile(sp,'吊柜米面料仓（60 cm 吊柜，概念）',label_lines=('左：5 kg 米仓 + 计量螺杆；右：2 kg 面粉/淀粉仓 + 螺杆','柜下：出料口 + 称重台（放淘米锅），淘米在水槽，煮饭用可远程启动的电饭煲')),
 tile(['drum'],'分格转筒料盒 Ø80×140（4 格，出料口错开 50°）',az=120,el=-35,label_lines=('机械臂握端头方块；转腕 120/170/220/270° 依次倒出 4 格','仿真：颗粒料 100% 进锅、按序，格间隔 ≥1.3 s')),
 tile(['cup'],'机器人料杯 Ø70×75（不锈钢，握持带）',az=120,el=-30)]
S=Image.new('RGB',(2*TW,2*TH),(255,255,255))
for i,im in enumerate(T):S.paste(im,((i%2)*TW,(i//2)*TH))
S.save(OUT);print(OUT)
