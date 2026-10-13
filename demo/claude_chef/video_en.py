"""Replay a closed chain (results/chain_<P>/full.json) as an MP4: every motion frame
is one checked state, rendered from the same collision geometry the checker uses.
Event frames (jaw open/close) and process holds are added between checked states
and captioned; the on-screen timer counts motion time only.
Usage: python video.py AS|AW out.mp4"""
import sys,json,subprocess,shutil,os
import numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
import sys as _s,os as _o;_s.path.insert(0,_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),"..","..","sim","r10","claude"));import chain
from scene import TOMATO_DZ,tomato_dz,build
from dress import dress,HIDE
P,OUT=sys.argv[1],sys.argv[2];W,H_,FPS=1280,720,30
FFMPEG=shutil.which('ffmpeg') or r'C:\Users\admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe'
d=json.load(open(f'results/chain_{P}/full.json'));Q=np.array(d['path']);L=d['labels']
OPEN=.025
CAP={'G1:raw_pick':'1  Pick the carrot from the raw tray','C1':'Transfer: fold the arm, cart drives to the sink','G2:wash_load':'2  Under the tap',
 'G2:wash_work':'2  Rinse and scrub','C2':'Transfer: fold the arm, cart drives to the peeler','G3:peel_load':'3  Into the peeler cradle','G3:release':'3  Release and retreat (carrot stays in the cradle)',
 'G3:return':'3  Come back after peeling','G3:peel_retrieve':'3  Grip and take out the peeled carrot','C3':'Transfer: fold the arm, cart drives to the cutter',
 'G4S:chute_load':'4  Drop it upright into the chute','G4S:chute_retreat':'4  Release and retreat',
 'GT1:raw_pick@tomato':'1  Pick the tomato with wide 3D-printed fingers','GT2:wash_load@tomato':'2  Rinse under the tap',
 'GT3:wedge_slide@tomato':'3  Slide in 6 mm above the 8-wedge blade','GT3:wedge_load@tomato':'3  Set it on the blade plate',
 'GT3:tomato_release_retreat':'3  Release and retreat (tomato stays on the blade)','GT4:pusher_grasp':'4  Reach the pusher knob from the front',
 'GT4:pusher_press':'5  Press 102 mm: the tomato is pushed through the blade into 8 wedges','GT4:pusher_return':'5  Pusher back up',
 'GT4:pusher_release_lift':'6  Release and lift away'}
if P=='AW':CAP.update(C2='Transfer: fold the arm, cart drives to the lever cutter',C3='Transfer: fold the arm, switch to the pusher grasp')
def config_for(label):
 """(held item, scene state) exactly as chain.py checked that segment."""
 g,_,s=label.partition(':')
 if g.startswith('C'):
  if chain.config(P).get('r11_tomato'):return ('tomato',{}) if g!='C3' else (None,chain.tstate(P,'pusher_grasp'))
  return 'carrot',{}
 if s in ('release','return'):return None,dict(carrot_at=list(chain.target(P,'peel_load')['points'][-1]))
 if s=='chute_retreat':return None,{}
 if s=='tomato_release_retreat':
  return None,dict(tomato_at=(np.array(chain.target(P,'wedge_load@tomato')['points'][-1])-[0,0,tomato_dz(chain.chain_cfg(P))]).tolist())
 if s=='pusher_release_lift':return None,dict(tomato_gone=True)
 t=chain.target(P,s);return t['held'],chain.tstate(P,s)
# Timeline: (q, label, caption, motion_dt). Motion states use the full.json pacing
# (leading arm joint 0.8 rad/s, base 0.25 m/s); inserted frames carry dt 0.
runs=[];i=0
while i<len(L):
 j=i
 while j+1<len(L) and L[j+1]==L[i]:j+=1
 runs.append((L[i],i,j));i=j+1
items=[]  # (label_for_config, q, caption, dt)
def motion(label,qs,cap):
 prev=items[-1][1] if items else qs[0]
 for q in qs:
  dt=max(np.max(abs(q[3:9]-prev[3:9]))/.8,abs(q[0]-prev[0])/.25,np.max(abs(q[9:11]-prev[9:11]))/.05);items.append((label,q,cap,dt));prev=q
def hold(label,q,cap,sec):items.extend([(label,q,cap,0.)]*int(sec*FPS))
def jaws(label,q,to,cap,sec=.5):
 n=int(sec*FPS)
 for k in range(n):x=q.copy();x[9:11]=q[9:11]+(np.array(to)-q[9:11])*(k+1)/n;items.append((label,x,cap,0.))
for k,(lab,a,b) in enumerate(runs):
 qs=[Q[x] for x in range(a,b+1)];cap=CAP.get(lab,lab)
 if k==0:hold(lab,qs[0],cap,1.2)
 if lab=='G4S:chute_retreat':jaws(lab,items[-1][1],[OPEN,OPEN],'4  Release: carrot falls into the chute')
 if lab=='GT4:pusher_press':
  jaws('GT4:pusher_grasp',items[-1][1],qs[0][9:11],'4  Grip the pusher knob')
 if lab=='GT4:pusher_release_lift':jaws(lab,items[-1][1],[OPEN,OPEN],'6  Release the knob')
 if lab=='GT3:tomato_release_retreat':jaws(lab,items[-1][1],[OPEN,OPEN],'3  Release the tomato')
 if lab=='G3:peel_retrieve':
  # Checked in chain.py G3 (not stored in full.json): release at the seat, retreat
  # the open gripper back along peel_load, peeler works, return the same way.
  load=[Q[x] for x in range(runs[k-1][1],runs[k-1][2]+1)];op=[np.r_[q[:9],OPEN,OPEN] for q in load]
  jaws('G3:release',load[-1],[OPEN,OPEN],'3  Release the carrot')
  motion('G3:release',op[::-1],CAP['G3:release']);hold('G3:release',op[0],'Peeler working (time not counted)',1.5)
  motion('G3:return',op,CAP['G3:return']);jaws('G3:release',op[-1],qs[0][9:11],'3  Grip the carrot')
 motion(lab,qs,cap)
 if lab=='GT2:wash_load@tomato':hold(lab,qs[-1],'Rinsing (time not counted)',1.2)
 if lab=='GT4:pusher_press':hold(lab,qs[-1],'5  Press to the bottom (arm up to ~100 N)',1.0)
hold(items[-1][0],items[-1][1],'Done' if P=='AS' else 'Done: 8 wedges fall into the bowl below',1.0)
if P=='AS':hold(items[-1][0],items[-1][1],'Cutter slicing (time not counted); slices fall into the bowl',1.0)
# Resample motion to FPS; inserted frames are one frame each.
frames=[];acc=0.;t_motion=0.
for lab,q,cap,dt in items:
 if dt==0.:frames.append((lab,q,cap,t_motion));continue
 acc+=dt;t_motion+=dt
 if acc>=1/FPS:frames.append((lab,q,cap,t_motion));acc-=1/FPS*int(acc*FPS)
print(P,'states',len(Q),'items',len(items),'frames',len(frames),'motion_s',round(t_motion,1),flush=True)
# One checker model per scene configuration; two renderers (colour + depth) per view size.
IW,IH=464,348;IN=[float(x) for x in os.environ.get('INSET','.75,140,-30').split(',')]
cache={}
def model(lab):
 held,st=config_for(lab);key=json.dumps([held,st],sort_keys=True)
 if key not in cache:
  tree,_=build(chain.chain_cfg(P,**st),held);m=dress(tree);names=[m.geom(g).name for g in range(m.ngeom)]
  cache[key]=dict(m=m,d=mujoco.MjData(m),sid=m.site('R_prep').id,ghost=[g for g,n in enumerate(names) if n.startswith(('R_vis_','upper_cabinet','r07_closed_door'))])
 return cache[key]
OPT=mujoco.MjvOption();OPT.geomgroup[:]=1;OPT.geomgroup[HIDE]=0
def view(M,cam,h,w):
 if (h,w) not in M:M[(h,w)]=mujoco.Renderer(M['m'],h,w)
 r=M[(h,w)];r.update_scene(M['d'],camera=cam,scene_option=OPT);return r.render().copy()
def smooth(pts,sec):
 pts=np.array(pts);sig=max(sec*FPS,1.);n=3*int(sig);ker=np.exp(-.5*(np.arange(-n,n+1)/sig)**2);ker/=ker.sum()
 pad=np.pad(pts,((n,n),(0,0)),mode='edge');return np.stack([np.convolve(pad[:,c],ker,'valid') for c in range(3)],1)
# Cameras: wide view between cart and tool (0.6 s smoothing), shifted so the robot
# sits left of the inset; inset follows the tool (0.25 s) from the front right, with
# arm links and upper cabinets drawn translucent there so they never hide the fingers.
pts=[];tcps=[]
for lab,q,cap,_ in frames:
 M=model(lab);M['d'].qpos[:]=q;mujoco.mj_kinematics(M['m'],M['d']);tcp=M['d'].site_xpos[M['sid']].copy()
 pts.append(np.array([.45*q[0]+.55*tcp[0],.10,.55*1.0+.45*np.clip(tcp[2],.85,1.35)])+.30*np.array([np.sin(np.radians(68)),-np.cos(np.radians(68)),0]))
 tcps.append(tcp+[0,0,-.03])
look=smooth(pts,.6);tlook=smooth(tcps,.25)
F=r'/System/Library/Fonts/STHeiti Medium.ttc';f1=ImageFont.truetype(F,30);f2=ImageFont.truetype(F,19)
foot=('Sim replay · every motion frame is a collision-checked state (checked on more conservative shapes) · timed at arm 0.8 rad/s, cart 0.25 m/s')
proc=subprocess.Popen([FFMPEG,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H_}','-r',str(FPS),'-i','-',
 '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.distance=2.35;cam.azimuth=68;cam.elevation=-33
tcam=mujoco.MjvCamera();tcam.type=mujoco.mjtCamera.mjCAMERA_FREE;tcam.distance,tcam.azimuth,tcam.elevation=IN
title={'AS':'Carrot: pick → rinse → peel → electric cutter','AW':'Tomato: pick → rinse → 8-wedge cutter → press'}[P]
PREVIEW=os.environ.get('PREVIEW')  # comma-separated frame fractions -> PNGs, no video
sel=[int(float(x)*(len(frames)-1)) for x in PREVIEW.split(',')] if PREVIEW else range(len(frames))
if PREVIEW:proc.stdin.close();proc.wait()
X0,Y0=W-IW-16,H_-40-IH-12
for k in sel:
 lab,q,cap,tm=frames[k]
 M=model(lab);M['d'].qpos[:]=q;mujoco.mj_forward(M['m'],M['d']);cam.lookat[:]=look[k];tcam.lookat[:]=tlook[k]
 img=Image.fromarray(view(M,cam,H_,W));mm=M['m'];rgba=mm.geom_rgba[M['ghost']].copy();mat=mm.geom_matid[M['ghost']].copy()
 mm.geom_matid[M['ghost']]=-1;mm.geom_rgba[M['ghost']]=(.75,.8,.86,.3)
 img.paste(Image.fromarray(view(M,tcam,IH,IW)),(X0,Y0));mm.geom_rgba[M['ghost']]=rgba;mm.geom_matid[M['ghost']]=mat
 ov=Image.new('RGBA',img.size,(0,0,0,0));dr=ImageDraw.Draw(ov)
 dr.rectangle([0,0,W,92],fill=(0,0,0,150));dr.rectangle([0,H_-40,W,H_],fill=(0,0,0,150))
 dr.rectangle([X0-3,Y0-3,X0+IW+2,Y0+IH+2],outline=(255,255,255,255),width=3);dr.rectangle([X0,Y0,X0+440,Y0+28],fill=(0,0,0,150))
 dr.text((X0+8,Y0+2),'Gripper close-up (arm and upper cabinets translucent)',font=f2,fill=(255,255,255,255))
 dr.text((24,8),title,font=f2,fill=(200,220,255,255));dr.text((24,38),cap,font=f1,fill=(255,255,255,255))
 dr.text((W-210,8),f'motion {tm:5.1f} s',font=f2,fill=(255,230,150,255));dr.text((24,H_-32),foot,font=f2,fill=(220,220,220,255))
 img=Image.alpha_composite(img.convert('RGBA'),ov).convert('RGB')
 if PREVIEW:img.save(OUT.replace('.mp4',f'_{k}.png'));continue
 proc.stdin.write(img.tobytes())
 if k%300==0:print(k,'/',len(frames),flush=True)
if not PREVIEW:proc.stdin.close();proc.wait();print('saved',OUT,proc.returncode)
