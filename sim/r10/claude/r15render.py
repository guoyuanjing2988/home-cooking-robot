"""R15 stills of checked poses: python r15render.py out.png <reach json>[:title | @dp.json#i:title] ... (cfg rebuilt from
the probe type; the best candidate's q). Camera: CAM=az,el,dist LOOK=x,y,z."""
import sys,json,numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
import chain
from scene import build
from dress import dress,HIDE
import kitchen15 as K
from checker import reference
KV=dict(a.split('=',1) for a in sys.argv[2:] if '=' in a and not a.endswith('.json') and ':' not in a.split('=')[0])
specs=[a for a in sys.argv[2:] if '.json' in a]
cam=[float(x) for x in KV.get('CAM','125,-25,1.5').split(',')];look=[float(x) for x in KV.get('LOOK','.83,.1,1.05').split(',')]
F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);ims=[]
for sp in specs:
 fn,_,title=sp.partition('.json');fn+='.json';title=title.lstrip(':');r=json.load(open(fn));b=r['best'];extra={}
 if title.startswith('@'):   # '@dp.json#i:title' -> use the continuity path's pose i instead of the best candidate
  ref,_,title=title[1:].partition(':');dpf,_,i=ref.partition('#');dpd=json.load(open(dpf));b=dict(q=dpd['q_path'][int(i)],jaw_sign=dpd['jaw_path'][int(i)])
 if r['probe'] in ('stir','stand'):extra=dict(r15_spatula=r.get('grip_m',.45),r15_spatula_jaw=b['jaw_sign'])
 if r['probe']=='rim':extra=dict(r14_cup=True)
 if r['probe']=='drum':extra=dict(r14_drum=True,r15_drum_taken=True,**({'r15_drum_c':r['drum_c']} if r.get('drum_c') and r['drum_c']!=list(K.DRUM_HOLD['c']) else {}))
 if r['probe']=='pour':
  a_w,j_w=((0,0,-1.),(0,1.,0)) if r['grasp']=='top' else ((1.,0,0),(0,0,1.))
  Rwt=reference.rotation(a_w,b['jaw_sign']*np.array(j_w));bc=K.GRIP['c']-K.WOK0;T=np.eye(4);T[:3,:3]=Rwt.T;T[:3,3]=-Rwt.T@bc
  extra=dict(r15_wok_held=dict(T_tool_wok=T.tolist()))
 cfg=chain.chain_cfg('SD',r14=True,present=[],r15=True,**extra);tree,_=build(cfg,None)
 m=dress(tree);d=mujoco.MjData(m);q=np.array(b['q']);d.qpos[:len(q)]=q;mujoco.mj_forward(m,d)
 rr=mujoco.Renderer(m,620,760);c=mujoco.MjvCamera();c.lookat[:]=look;c.azimuth,c.elevation,c.distance=cam
 o=mujoco.MjvOption();o.geomgroup[:]=1;o.geomgroup[HIDE]=0;rr.update_scene(d,c,o);im=Image.fromarray(rr.render())
 dr=ImageDraw.Draw(im);dr.rectangle([0,0,760,32],fill=(255,255,255));dr.text((8,4),title or fn,fill=(0,0,0),font=F);ims.append(im);rr.close()
S=Image.new('RGB',(760*len(ims),620));[S.paste(im,(760*i,0)) for i,im in enumerate(ims)];S.save(sys.argv[1]);print(sys.argv[1])
