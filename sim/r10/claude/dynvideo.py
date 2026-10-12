"""Render dyn.py runs (physics replays) as one captioned MP4 with the dressed look.
Usage: python dynvideo.py out.mp4 TAG:title[:seconds] [TAG:title[:seconds] ...]"""
import sys,json,shutil,subprocess,numpy as np,mujoco,xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageFont
from dress import dress,HIDE
OUT=sys.argv[1];W,H_,FPS=1280,720,30;IW,IH=464,348
FFMPEG=shutil.which('ffmpeg') or r'C:\Users\admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe'
CAP={'start':'夹紧','G1:raw_pick':'从原料盘拿起胡萝卜','C1':'转场：收臂，推车移到水槽','G2:wash_load':'送到水龙头下','G2:wash_work':'冲洗擦洗',
 'C2':'转场：推车移到下一工位','G3:peel_load':'放进削皮机托架','G3:release':'松手退出（胡萝卜留在托架里）','peeling (not simulated)':'削皮（未仿真）',
 'G3:return':'回来','G3:regrasp':'重新夹住','G3:peel_retrieve':'取出','C3':'转场：推车移到电动切菜机','G4S:chute_load':'竖着放进进料口',
 'G4S:chute_retreat':'松手：胡萝卜落进进料口','GT1:raw_pick@tomato':'从托垫上拿起番茄','GT2:wash_load@tomato':'送到水龙头下',
 'GT3:wedge_slide@tomato':'平移到刀板上方','GT3:wedge_load@tomato':'放到刀板上','GT3:tomato_release_retreat':'松手退出（番茄留在刀板上）','settle':'静置'}
F=r'C:\Windows\Fonts\msyh.ttc';f1=ImageFont.truetype(F,30);f2=ImageFont.truetype(F,19)
OPT=mujoco.MjvOption();OPT.geomgroup[:]=1;OPT.geomgroup[HIDE]=0
def smooth(pts,sec):
 pts=np.array(pts);sig=max(sec*FPS,1.);n=3*int(sig);ker=np.exp(-.5*(np.arange(-n,n+1)/sig)**2);ker/=ker.sum()
 pad=np.pad(pts,((n,n),(0,0)),mode='edge');return np.stack([np.convolve(pad[:,c],ker,'valid') for c in range(3)],1)
proc=subprocess.Popen([FFMPEG,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H_}','-r',str(FPS),'-i','-',
 '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
FOOT='物理仿真（MuJoCo 刚体动力学）：{grip}；菜是自由刚体（有质量、摩擦），不「焊」在夹爪上'
for spec in sys.argv[2:]:
 tag,title,*sec=spec.split(':',2);res=json.load(open(f'results/dyn_{tag}.json'))
 g_=res.get('grip','force 40 N');foot=FOOT.format(grip=f'夹爪按 {g_.split()[1]} N 力夹持' if g_.startswith('force') else f'夹爪位置控制，软垫压缩 {1000*float(g_.split(":")[1]):.0f} mm（每指约 {res.get("finger_N_median",0):.0f} N）')
 m=dress(E.ElementTree(E.fromstring(open(f'results/dyn_{tag}.xml',encoding='utf-8').read())));d=mujoco.MjData(m)
 Q=np.load(f'results/dyn_{tag}_frames.npy');L=json.load(open(f'results/dyn_{tag}_labels.json'))
 if sec:Q,L=Q[:int(float(sec[0])*FPS)],L[:int(float(sec[0])*FPS)]
 gt=m.body('G_tool').id;cx=m.jnt_qposadr[m.joint('R_carriage_x').id];pts=[];tps=[]
 for q in Q:
  d.qpos[:]=q;mujoco.mj_kinematics(m,d);p=d.xpos[gt].copy();pts.append([.45*q[cx]+.55*p[0]+.28,.0,.55+.45*np.clip(p[2],.85,1.35)]);tps.append(p)
 look=smooth(pts,.6);tlook=smooth(tps,.25)
 r=mujoco.Renderer(m,H_,W);ri=mujoco.Renderer(m,IH,IW)
 cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.distance,cam.azimuth,cam.elevation=2.35,68,-33
 tc=mujoco.MjvCamera();tc.type=mujoco.mjtCamera.mjCAMERA_FREE;tc.distance,tc.azimuth,tc.elevation=.75,140,-30
 ghost=[g for g in range(m.ngeom) if m.geom(g).name.startswith(('R_vis_','upper_cabinet','r07_closed_door'))]
 for k,(q,lab) in enumerate(zip(Q,L)):
  d.qpos[:]=q;mujoco.mj_forward(m,d);cam.lookat[:]=look[k];tc.lookat[:]=tlook[k]
  r.update_scene(d,camera=cam,scene_option=OPT);img=Image.fromarray(r.render())
  rgba=m.geom_rgba[ghost].copy();mat=m.geom_matid[ghost].copy();m.geom_matid[ghost]=-1;m.geom_rgba[ghost]=(.75,.8,.86,.3)
  ri.update_scene(d,camera=tc,scene_option=OPT);img.paste(Image.fromarray(ri.render()),(W-IW-16,H_-40-IH-12));m.geom_rgba[ghost]=rgba;m.geom_matid[ghost]=mat
  ov=Image.new('RGBA',img.size,(0,0,0,0));dr=ImageDraw.Draw(ov);X0,Y0=W-IW-16,H_-40-IH-12
  dr.rectangle([0,0,W,92],fill=(0,0,0,150));dr.rectangle([0,H_-40,W,H_],fill=(0,0,0,150));dr.rectangle([X0-3,Y0-3,X0+IW+2,Y0+IH+2],outline=(255,255,255,255),width=3)
  dr.text((24,8),title,font=f2,fill=(255,220,140,255));dr.text((24,38),CAP.get(lab,lab),font=f1,fill=(255,255,255,255))
  dr.text((W-200,8),f'时间 {k/FPS:5.1f} s',font=f2,fill=(220,220,220,255));dr.text((24,H_-32),foot,font=f2,fill=(220,220,220,255))
  dr.rectangle([X0,Y0,X0+250,Y0+28],fill=(0,0,0,150));dr.text((X0+8,Y0+2),'夹爪特写（机械臂、吊柜半透明）',font=f2,fill=(255,255,255,255))
  proc.stdin.write(Image.alpha_composite(img.convert('RGBA'),ov).convert('RGB').tobytes())
 r.close();ri.close()  # free GL contexts explicitly; GC-time frees break the next renderer
 print(tag,len(Q),'frames',flush=True)
proc.stdin.close();proc.wait();print('saved',OUT,proc.returncode)
