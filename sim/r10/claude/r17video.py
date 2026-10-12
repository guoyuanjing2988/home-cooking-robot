"""R17 video of a checked whole action: python r17video.py results/r17/chain_<..>.json out.mp4 [CAM=az,el,dist] [LOOK=x,y,z] [SPEED=1]
Plays the chain's held path ('play', every checked step) with the same scene and grasp sense.
Frame times follow the chain's timing model approximately (cart <= 0.25 m/s, joints <= 60°/s, at
least 1/30 s per step); dwells are not shown. Needs ffmpeg on PATH."""
import sys,os,json,subprocess,tempfile,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
import chain
from scene import build
from dress import dress,HIDE
import kitchen16 as K,kitchen17 as K17
src,out=sys.argv[1],sys.argv[2];KV=dict(a.split('=',1) for a in sys.argv[3:])
r=json.load(open(src));K.set_design(**r['design'])
for k_,v in r.get('tool_xy',{}).items():K.TOOL_XY[k_]=tuple(v)
if r.get('wok_tilt'):K17.set_wok_tilt(r['wok_tilt'])
if r.get('wok_grasp')=='end':K17.set_wok_end_grasp()
cfg=chain.chain_cfg('SD',**{**dict(r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF)),**r.get('scene',json.loads(KV.get('SCENE','{}'))),**K17.held_cfg(r['obj'],r['grasp_sense'])})
tree,_=build(cfg,None);m=dress(tree);d=mujoco.MjData(m)
cam=[float(x) for x in KV.get('CAM','150,-22,2.2').split(',')];look=[float(x) for x in KV.get('LOOK','.3,.1,1.0').split(',')];speed=float(KV.get('SPEED',1))
Q=np.array(r['play']);F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
rr=mujoco.Renderer(m,540,960);c=mujoco.MjvCamera();c.lookat[:]=look;c.azimuth,c.elevation,c.distance=cam
o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0
tmp=tempfile.mkdtemp();t=0.;nf=0;fps=30
for i,q in enumerate(Q):
 dt=0. if i==0 else max(abs(q[0]-Q[i-1][0])/.25,np.degrees(np.max(abs(q[3:9]-Q[i-1][3:9])))/60.,1/fps)/speed
 t+=dt
 while nf<=t*fps or i==0:
  d.qpos[:len(q)]=q;mujoco.mj_forward(m,d);rr.update_scene(d,c,o);im=Image.fromarray(rr.render())
  dr=ImageDraw.Draw(im);dr.text((10,8),KV.get('TITLE',r['act'])+f'   t={nf/fps:5.1f} s',fill=(0,0,0),font=F);im.save(f'{tmp}/f{nf:05d}.png');nf+=1
  if i==0:break
rr.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',f'{tmp}/f%05d.png','-pix_fmt','yuv420p','-vf','scale=960:-2',out],check=True)
print(out,nf,'frames')
