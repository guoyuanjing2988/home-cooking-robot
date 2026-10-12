"""CPU-only collision-geometry renderer (Pillow); no GPU or beauty-model substitution."""
from jobs import *
from PIL import Image,ImageDraw,ImageFont
def font(s):
 for p in ('C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/segoeui.ttf'):
  if Path(p).exists():return ImageFont.truetype(p,s)
 return ImageFont.load_default()
def local_faces(m,g):
 typ=int(m.geom_type[g]);sz=m.geom_size[g]
 if typ==6:
  v=np.array(list(itertools.product((-sz[0],sz[0]),(-sz[1],sz[1]),(-sz[2],sz[2]))));ix=[[0,4,6,2],[1,3,7,5],[0,1,5,4],[2,6,7,3],[0,2,3,1],[4,5,7,6]];return [v[a] for a in ix]
 if typ==7:
  mid=m.geom_dataid[g];va=m.mesh_vertadr[mid];v=m.mesh_vert[va:va+m.mesh_vertnum[mid]];fa=m.mesh_faceadr[mid];f=m.mesh_face[fa:fa+m.mesh_facenum[mid]].copy()
  if f.max(initial=0)>=len(v):f-=va
  return [v[a] for a in f]
 if typ in (2,3,5):
  rad=sz[0];height=sz[1] if typ!=2 else 0;levels=[]
  if typ==3:
   for a in np.linspace(-math.pi/2,0,5):levels.append((rad*math.cos(a),-height+rad*math.sin(a)))
   for a in np.linspace(0,math.pi/2,5):levels.append((rad*math.cos(a),height+rad*math.sin(a)))
  elif typ==2:
   for a in np.linspace(-math.pi/2,math.pi/2,9):levels.append((rad*math.cos(a),rad*math.sin(a)))
  else:levels=[(rad,-height),(rad,height)]
  rings=[np.array([[r*math.cos(a),r*math.sin(a),z] for a in np.linspace(0,2*math.pi,17)[:-1]]) for r,z in levels];faces=[]
  for a,b in zip(rings,rings[1:]):
   for i in range(16):j=(i+1)%16;faces.append(np.array([a[i],a[j],b[j],b[i]]))
  if typ==5:faces+=[rings[0],rings[-1]]
  return faces
 return []
CACHE={}
def load(xml):
 if xml not in CACHE:
  m=mujoco.MjModel.from_xml_path(str(H/xml));d=mujoco.MjData(m);CACHE[xml]=(m,d,[local_faces(m,g) for g in range(m.ngeom)])
 return CACHE[xml]
def render(xml,q,title,subtitle,size=(1440,1080),focus=(0,.375,1.03),scale=430,labels=True):
 m,d,local=load(xml);d.qpos[:]=q;mujoco.mj_kinematics(m,d);w,h=size;im=Image.new('RGB',size,(239,242,245));draw=ImageDraw.Draw(im,'RGBA')
 eye=np.array([2.7,-4,2.8]);forward=np.array(focus)-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);f=np.array(focus)
 def project(v):return np.column_stack([w*.5+(v-f)@right*scale,h*.56-(v-f)@up*scale])
 faces=[];light=np.array([-.4,-.7,1]);light/=np.linalg.norm(light)
 for g in range(m.ngeom):
  n=m.geom(g).name;rgba=m.geom_rgba[g].copy();rot=d.geom_xmat[g].reshape(3,3);p=d.geom_xpos[g]
  if n.startswith('R_geom_') and m.geom_type[g]!=7:rgba=np.array([.45,.62,.72,1])
  if 'lid_panel' in n:rgba[3]=.65
  for face in local[g]:
   v=face@rot.T+p;normal=np.cross(v[1]-v[0],v[2]-v[0]);nl=np.linalg.norm(normal)
   shade=.65+.35*abs(float(normal@light/max(nl,1e-9)));color=tuple(np.clip(rgba[:3]*shade*255,0,255).astype(int))+(int(rgba[3]*255),)
   faces.append((float((v-f).mean(axis=0)@forward),project(v),color))
 for depth,v,color in sorted(faces,key=lambda x:-x[0]):draw.polygon([tuple(a) for a in v],fill=color,outline=(45,63,74,min(100,color[3])))
 if labels:
  for name,p in [('Wash lift',[-.49,.49,1.24]),('Guarded process cell',[.45,.505,1.5]),('Input / output pans',[0,.18,.91]),('Waste bin',[.46,.5,.44]),('UR5e',[0,.53,1.78])]:
   x,y=project(np.array([p]))[0];draw.rounded_rectangle((x-6,y-5,x+font(16).getlength(name)+10,y+24),radius=4,fill=(255,255,255,225));draw.text((x,y),name,font=font(16),fill=(25,45,60,255))
 draw.rectangle((0,0,w,80),fill=(20,38,52,255));draw.text((24,15),title,font=font(27 if w>700 else 16),fill='white');draw.text((24,49),subtitle,font=font(17 if w>700 else 12),fill=(190,217,232,255))
 draw.rectangle((0,h-40,w,h),fill=(255,255,255,225));draw.text((18,h-30),'Full-size collision geometry. Guard/lid transparency is display only.',font=font(15 if w>700 else 10),fill=(44,64,80,255))
 return im
prefix=json.loads((H/'results/executed_prefix.json').read_text());summary=json.loads((H/'results/phase_summary.json').read_text());q0=np.array(json.loads(next((H/'results').glob('static_chunk_0_*.json')).read_text())['rows'][0]['selected']['poses'][0]['q'])
overview='models/overview.xml';render(overview,q0,'R06 dedicated prep workstation','1450 x 750 mm | One fixed UR5e | Complete meal FAIL').save(H/'renders/overview.png')
service=E.parse(H/overview);joint=service.getroot().find(".//joint[@name='access_door_joint']");joint.set('range','-1.6 0');service.write(H/'models/service_door.xml',encoding='unicode');m,d,_=load('models/service_door.xml');q=q0.copy();j=m.joint('access_door_joint').id;q[m.jnt_qposadr[j]]=-1.55
ch=Cell(V);j=ch.jid['access_door_joint'];g=ch.gnames.index('access_door_panel');ch.pose(q0);lever=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g];count=math.ceil(1.55*lever/.004);minres=1e30;first=None
for k in range(count+1):
 z=q0.copy();z[ch.qa['access_door_joint']]=-1.55*k/count;hits,mins,proof=contacts(ch,z)
 if hits:first=dict(k=k,blockers=hits[:3]);break
 minres=min(minres,min(v['reserve_mm'] for cat,v in mins.items() if cat!='self'))
write('results/service_door.json',dict(pass_=first is None,states_checked=k+1,samples_planned=count+1,door_point_step_bound_mm=1.55*lever/count*1000,minimum_robot_reserve_mm=minres if first is None else None,first_blocker=first,door_open_rad=-1.55,robot_stopped_brakes_applied=True,scope='Robot clearance during human service; frame hinge/jamb design and interlock hardware are unqualified'))
render('models/service_door.xml',q,'Stopped loading / unloading access',('Robot door sweep checked' if first is None else 'Door sweep FAIL')+' | Interlock hardware unqualified').save(H/'renders/door_open.png')
views=[('wash',(-.49,.49,1.15),780),('process',(.45,.505,1.24),790),('input_output',(0,.2,1.07),680),('waste',(.46,.5,.40),840),('arm_mount',(0,.6,1.76),900)]
for name,focus,scale in views:render(overview,q0,'Station: '+name.replace('_',' '),'Design geometry; process execution is unqualified',focus=focus,scale=scale).save(H/f'renders/station_{name}.png')
samples=[]
for path in prefix['paths']:
 if not path['ok']:break
 trace=path.get('load_replay',{}).get('trace',[])
 if not trace:trace=[dict(q=x) for x in path['path']]
 for k,t in enumerate(trace):samples.append(dict(path=path['id'],xml=path['xml'],q=t['q'],source_checked_sample=k,scope='Executed simulation prefix only; raw food retained'))
if not samples:samples=[dict(path='stopped_initial',xml=overview,q=q0.tolist(),source_checked_sample=0,scope='Checked initial static state; no meal motion executed')]
frames=[];strip=Image.new('RGB',(1440,1440),(230,234,237))
for k,index in enumerate(np.linspace(0,len(samples)-1,24).round().astype(int)):
 sample=samples[index];frame=render(sample['xml'],sample['q'],f'Frame {k+1:02d}: {sample["path"]}','Checked prefix; later meal NOT EXECUTED',size=(720,480),scale=180,labels=False);frame.save(H/f'renders/frame_{k+1:02d}.png');strip.paste(frame.resize((360,240)),((k%4)*360,(k//4)*240));frames.append(dict(frame=k+1,file=f'renders/frame_{k+1:02d}.png',**sample))
strip.save(H/'renders/meal_prefix_24.png');write('renders/frame_manifest.json',dict(frames=frames,complete_meal=False,blocked_event=prefix['blocked'],renderer='CPU Pillow painter of compiled MuJoCo collision primitives and original base meshes',max_pixels=1440));print('RENDERS',len(frames)+8)
