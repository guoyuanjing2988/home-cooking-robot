"""Grid video of food-bench runs (foodbench.py / softbench.py with FRAMES=1).
Usage: python benchvideo.py out.mp4 spec.txt   where each spec line is
   <bench> | <tile title> | <item> KEY=VALUE ...      (bench = foodbench or softbench)
The runs are executed in parallel (if their frames are missing), then rendered as a
4-column grid, 30 fps; each tile follows its item; footer = verdict from the result."""
import sys,os,json,glob,subprocess,shutil,numpy as np,mujoco,xml.etree.ElementTree as E
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw,ImageFont
OUT,SPEC=sys.argv[1],sys.argv[2];COLS=4;TW,TH=480,300;FPS=30
FFMPEG=shutil.which('ffmpeg') or r'C:\Users\admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe'
rows=[[x.strip() for x in l.split('|')] for l in open(SPEC,encoding='utf-8') if l.strip() and not l.startswith('#')]
def run(ir):
 i,(bench,title,args)=ir;d=('results/r13s' if bench=='softbench' else 'results/r13')
 cands=glob.glob(f'{d}/{args.split()[0]}_*_vid{i}.json')
 if not (cands and os.environ.get('NORUN')):subprocess.run([sys.executable,bench+'.py']+args.split()+['FRAMES=1',f'TAG=_vid{i}'],capture_output=True,text=True)
 cands=sorted(glob.glob(f'{d}/{args.split()[0]}_*_vid{i}.json'),key=os.path.getmtime)
 return cands[-1] if cands else None
with ThreadPoolExecutor(8) as ex:paths=list(ex.map(run,enumerate(rows)))
F1=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19);F2=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
tiles=[]
for (bench,title,args),p in zip(rows,paths):
 if not p:print('missing',args);continue
 res=json.load(open(p));tag=p[:-5]
 root=E.fromstring(open(tag+'.xml',encoding='utf-8').read())
 for g in root.iter('global'):g.set('offwidth','960');g.set('offheight','600')
 m=mujoco.MjModel.from_xml_string(E.tostring(root,encoding='unicode'));d=mujoco.MjData(m);Q=np.load(tag+'_frames.npy')
 ok=res.get('ok');why='、'.join({'dropped':'掉落','slip>=10mm':'滑移超 10 mm','not in target':'没放进碗','force>damage':'夹力超损伤上限','moment>allow':'超夹爪力矩'}.get(f,f) for f in res.get('fail',[]))
 F=res.get('F',0);mode=res.get('mode');foot=('成功' if ok else '失败：'+why)+f"  ·  {'力控' if mode=='force' else '力反馈'} {F:.0f} N/指，实测峰值 {res.get('finger_N_10ms_max',0):.0f}"
 tiles.append(dict(m=m,d=d,Q=Q,title=title,foot=foot,ok=ok,fb=m.body('food').id,gt=m.body('G_tool').id))
N=max(len(t['Q']) for t in tiles);R_=(len(tiles)+COLS-1)//COLS;W,H=COLS*TW,R_*TH+40
proc=subprocess.Popen([FFMPEG,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','21','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for t in tiles:
 t['r']=mujoco.Renderer(t['m'],TH,TW);t['cam']=mujoco.MjvCamera();t['cam'].azimuth,t['cam'].elevation,t['cam'].distance=130,-26,.72;t['look']=None
 t['m'].vis.headlight.ambient[:]=.42;t['m'].vis.headlight.diffuse[:]=.5
head=Image.new('RGB',(W,40),(255,255,255));ImageDraw.Draw(head).text((10,8),'R13 各种食材的物理仿真（MuJoCo；只画夹爪，菜是自由刚体/多体，不「焊」在手上）：每格一种食材和它的抓法；μ = 湿滑摩擦系数（按偏不利取值）',fill=(0,0,0),font=F1)
for k in range(N):
 frame=Image.new('RGB',(W,H),(255,255,255));frame.paste(head,(0,0))
 for i,t in enumerate(tiles):
  q=t['Q'][min(k,len(t['Q'])-1)];t['d'].qpos[:]=q;mujoco.mj_forward(t['m'],t['d'])
  tgt=.6*t['d'].xpos[t['fb']]+.4*t['d'].xpos[t['gt']]
  t['look']=tgt if t['look'] is None else .9*t['look']+.1*tgt;t['cam'].lookat[:]=t['look']
  t['r'].update_scene(t['d'],t['cam']);im=Image.fromarray(t['r'].render());dr=ImageDraw.Draw(im)
  dr.rectangle([0,0,TW,26],fill=(255,255,255));dr.text((6,2),t['title'],fill=(10,10,10),font=F1)
  dr.rectangle([0,TH-24,TW,TH],fill=(232,246,236) if t['ok'] else (252,232,230));dr.text((6,TH-22),t['foot'],fill=(10,10,10),font=F2)
  frame.paste(im,((i%COLS)*TW,40+(i//COLS)*TH))
 proc.stdin.write(np.asarray(frame).tobytes())
proc.stdin.close();proc.wait();print(OUT,N/FPS,'s')
