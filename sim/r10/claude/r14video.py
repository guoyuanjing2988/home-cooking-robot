"""Side-by-side video of R14 bench runs (doorbench.py / pourbox.py with FRAMES=1).
Usage: python r14video.py out.mp4 "<tag>|<title>|<lookat x,y,z>|<az,el,dist>" ..."""
import sys,shutil,subprocess,json,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
OUT=sys.argv[1];TW,TH,FPS=640,480,30
FFMPEG=shutil.which('ffmpeg') or r'C:\Users\admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe'
F1=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);F2=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
T=[]
for spec in sys.argv[2:]:
 tag,title,look,cam=spec.split('|');m=mujoco.MjModel.from_xml_string(open(f'results/r14/{tag}.xml',encoding='utf-8').read());d=mujoco.MjData(m)
 Q=np.load(f'results/r14/{tag}_frames.npy');res=json.load(open(f'results/r14/{tag}.json'))
 r=mujoco.Renderer(m,TH,TW);c=mujoco.MjvCamera();c.lookat[:]=[float(x) for x in look.split(',')];c.azimuth,c.elevation,c.distance=[float(x) for x in cam.split(',')]
 T.append(dict(m=m,d=d,Q=Q,r=r,c=c,title=title,res=res))
N=max(len(t['Q']) for t in T);W=TW*len(T);H=TH+30
p=subprocess.Popen([FFMPEG,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for k in range(N):
 fr=Image.new('RGB',(W,H),(255,255,255));ImageDraw.Draw(fr).text((8,4),'R14 物理仿真（MuJoCo）：左 = 夹爪拉开冰箱门；右 = 分格转筒按顺序倒料',fill=(0,0,0),font=F1)
 for i,t in enumerate(T):
  t['d'].qpos[:]=t['Q'][min(k,len(t['Q'])-1)];mujoco.mj_forward(t['m'],t['d']);t['r'].update_scene(t['d'],t['c']);im=Image.fromarray(t['r'].render());dr=ImageDraw.Draw(im)
  dr.rectangle([0,0,TW,28],fill=(255,255,255));dr.text((6,3),t['title'],fill=(10,10,10),font=F2);fr.paste(im,(i*TW,30))
 p.stdin.write(np.asarray(fr).tobytes())
p.stdin.close();p.wait();print(OUT,N/FPS,'s')
