"""Park in wok video (render only; Mac 2026-10-13, new file): plays results/mac/park_in_wok_seq_<KEY>.json segment by
segment. Empty-gripper segments use the cup chain's scene with the cup on its pad; the held play uses the cup chain's
held scene (r17video.py setup). Both have the spatula left in the wok (the park_* geoms of the seq json).
Frame timing as r17video.py (cart <= .25 m/s, joints <= 60 deg/s, >= 1/30 s per state); dwells and the jaw open/close
time are not shown. python park_in_wok_video.py results/mac/park_in_wok_seq_work1.json renders/mac/park_in_wok.mp4 [CAM=az,el,dist] [LOOK=x,y,z]"""
import sys,os,json,subprocess,tempfile,numpy as np,mujoco,xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageFont
import cupobj   # noqa: F401
import dress
dress.RULES.insert(0,(('R_gripper_r19_cup','r19_cup'),'ceramic'));dress.RULES.insert(0,(('r19_scale',),'steel'))
import chain
from scene import build,fmt
from dress import HIDE
import kitchen16 as K,kitchen17 as K17
src,out=sys.argv[1],sys.argv[2];KV=dict(a.split('=',1) for a in sys.argv[3:])
S=json.load(open(src));r=json.load(open('results/mac/chain_cup_final.json'));K.set_design(**r['design'])
for k_,v in r.get('tool_xy',{}).items():K.TOOL_XY[k_]=tuple(v)
base=dict(r19_station=True,r14=True,present=[],r15=True,r16=True,r17=True,r16_lid='rack',r15_drum_taken=True,r16_tools=dict(K17.R17_TOOLS_OFF))
def model(held):
 cfg=chain.chain_cfg('SD',**{**base,**r['scene'],**(K17.held_cfg(r['obj'],r['grasp_sense']) if held else dict(r19_cup='port'))})
 tree,_=build(cfg,None);w=tree.find('worldbody')
 for g in S['spatula_geoms']:E.SubElement(w,'geom',name=g['name'],type=g['type'],size=fmt(g['size']),pos=fmt(g['pos']),quat=fmt(g['quat']),rgba='.35 .22 .12 1' if 'handle' in g['name'] else '.75 .76 .78 1',contype='0',conaffinity='0')
 return dress.dress(tree)
M={'empty':model(False),'held':model(True)};D={k:mujoco.MjData(v) for k,v in M.items()}
cam=[float(x) for x in KV.get('CAM','120,-30,2.0').split(',')];look=[float(x) for x in KV.get('LOOK','.5,.1,1.15').split(',')]
RR={k:mujoco.Renderer(v,540,960) for k,v in M.items()};c=mujoco.MjvCamera();c.lookat[:]=look;c.azimuth,c.elevation,c.distance=cam
o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0
F=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22);fps=30;tmp=tempfile.mkdtemp();t=0.;nf=0;prev=None
for sg in S['segments']:
 k=sg['scene'];m,d,rr=M[k],D[k],RR[k]
 for q in np.array(sg['qs']):
  # time-model sampling (the <=4 mm checked states are much denser than 30 fps): a frame whenever the clock passes a frame
  # time; a short pause of 1/fps where the joints do not move (jaw open/close)
  dt=1/fps if prev is None else max(abs(q[0]-prev[0])/.25,np.degrees(np.max(abs(q[3:9]-prev[3:9])))/60.)
  if dt<1e-9:dt=1/fps
  t+=dt;prev=q
  while nf<=t*fps:
   d.qpos[:len(q)]=q;mujoco.mj_forward(m,d);rr.update_scene(d,c,o);im=Image.fromarray(rr.render())
   dr=ImageDraw.Draw(im);dr.text((10,8),f"park the spatula in the wok, cup pour   t={nf/fps:5.1f} s",fill=(0,0,0),font=F);dr.text((10,36),sg['label'],fill=(0,0,0),font=F)
   im.save(f'{tmp}/f{nf:05d}.png');nf+=1
for v in RR.values():v.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',f'{tmp}/f%05d.png','-pix_fmt','yuv420p','-vf','scale=960:-2',out],check=True)
print(out,nf,'frames')
