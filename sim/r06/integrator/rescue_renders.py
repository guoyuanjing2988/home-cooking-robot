"""CPU collision-model renders of the revision2 executed prefix, never a meal mockup."""
from rescue_spec import *
from PIL import Image,ImageDraw,ImageFont
import ast
tree=ast.parse((H/'renders.py').read_text());src=(H/'renders.py').read_text()
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ('font','local_faces','load','render'):exec(compile(ast.Module(body=[node],type_ignores=[]),'<original CPU renderer>','exec'),globals())
CACHE={}
def render(xml,q,title,subtitle,size=(1440,1080),focus=(0,.44,1.04),scale=400,labels=False):
 # Orthographic CPU depth buffer. Centroid-only painter ordering can wrongly
 # hide a pan behind a large worktop polygon; rasterized depth resolves that.
 m,d,local=load(xml);d.qpos[:]=q;mujoco.mj_kinematics(m,d);w,h=size;rgb=np.empty((h,w,3),dtype=np.float32);rgb[:]=[239,242,245];depth=np.full((h,w),np.inf,dtype=np.float32)
 eye=np.array([2.7,-4,2.8]);forward=np.array(focus)-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);origin=np.array(focus);light=np.array([-.4,-.7,1]);light/=np.linalg.norm(light);transparent=[];edges=[]
 def project(v):return np.column_stack([w*.5+(v-origin)@right*scale,h*.56-(v-origin)@up*scale,(v-origin)@forward])
 def triangle(v,color,alpha=1.):
  x0=max(0,int(np.floor(v[:,0].min())));x1=min(w-1,int(np.ceil(v[:,0].max())));y0=max(80,int(np.floor(v[:,1].min())));y1=min(h-41,int(np.ceil(v[:,1].max())))
  if x1<x0 or y1<y0:return
  aa,bb,cc=v;den=(bb[1]-cc[1])*(aa[0]-cc[0])+(cc[0]-bb[0])*(aa[1]-cc[1])
  if abs(den)<1e-8:return
  yy,xx=np.mgrid[y0:y1+1,x0:x1+1].astype(np.float32);xx+=.5;yy+=.5
  b0=((bb[1]-cc[1])*(xx-cc[0])+(cc[0]-bb[0])*(yy-cc[1]))/den;b1=((cc[1]-aa[1])*(xx-cc[0])+(aa[0]-cc[0])*(yy-cc[1]))/den;b2=1-b0-b1;zz=b0*aa[2]+b1*bb[2]+b2*cc[2];buf=depth[y0:y1+1,x0:x1+1];mask=(b0>=-1e-6)&(b1>=-1e-6)&(b2>=-1e-6)&(zz<=buf+1e-6)
  pixels=rgb[y0:y1+1,x0:x1+1]
  if alpha>=.999:pixels[mask]=color;buf[mask]=zz[mask]
  else:pixels[mask]=pixels[mask]*(1-alpha)+np.array(color)*alpha
 for g in range(m.ngeom):
  name=m.geom(g).name;rgba=m.geom_rgba[g].copy();rotation=d.geom_xmat[g].reshape(3,3);position=d.geom_xpos[g]
  if name.startswith('R_geom_') and m.geom_type[g]!=7:rgba=np.array([.45,.62,.72,1])
  if 'lid_panel' in name:rgba[3]=.12
  if rgba[3]<.99:rgba[3]=min(rgba[3],.08)
  for face in local[g]:
   world=face@rotation.T+position;normal=np.cross(world[1]-world[0],world[2]-world[0]);norm=np.linalg.norm(normal);shade=.65+.35*abs(float(normal@light/max(norm,1e-9)));color=np.clip(rgba[:3]*shade*255,0,255);v=project(world)
   if rgba[3]<.99:transparent.append((float(v[:,2].mean()),v,color,float(rgba[3])))
   else:
    for i in range(1,len(v)-1):triangle(v[[0,i,i+1]],color)
   if m.geom_type[g]==6:
    for aa,bb in zip(v,np.roll(v,-1,axis=0)):edges.append((aa,bb,rgba[3]<.99))
 for dep,v,color,alpha in sorted(transparent,key=lambda x:-x[0]):
  for i in range(1,len(v)-1):triangle(v[[0,i,i+1]],color,alpha)
 for aa,bb,trans in edges:
  count=max(1,int(np.linalg.norm(bb[:2]-aa[:2])*1.2));u=np.linspace(0,1,count+1);p=aa[None,:]+u[:,None]*(bb-aa);xx=np.rint(p[:,0]).astype(int);yy=np.rint(p[:,1]).astype(int);valid=(xx>=0)&(xx<w)&(yy>=80)&(yy<h-40);xx=xx[valid];yy=yy[valid];zz=p[valid,2];front=zz<=depth[yy,xx]+.003;xx=xx[front];yy=yy[front];rgb[yy,xx]=.55*rgb[yy,xx]+.45*np.array([45,63,74])
 im=Image.fromarray(np.clip(rgb,0,255).astype(np.uint8));draw=ImageDraw.Draw(im);draw.rectangle((0,0,w,80),fill=(20,38,52));draw.text((24,15),title,font=font(27 if w>700 else 16),fill='white');draw.text((24,49),subtitle,font=font(17 if w>700 else 12),fill=(190,217,232));draw.rectangle((0,h-40,w,h),fill=(250,251,252));draw.text((18,h-30),'CPU depth-buffer geometry render. Guards/lids translucent for display only.',font=font(15 if w>700 else 10),fill=(44,64,80));return im
prefix=json.loads((H/'results/executed_prefix.json').read_text());first=prefix['states'][0];xml=first['xml'];q0=np.array(first['q']);cfg=prefix['config'];v=cfg['id']
(H/'renders').mkdir(exist_ok=True)
render(xml,q0,'R06 revision2: open pan-transfer workstation','1606 x 906 mm enclosure | Fixed UR5e | Complete meal FAIL',focus=(0,.44,1.04),scale=400,labels=False).save(H/'renders/overview.png')
ch=Workcell(v);q=names_to_q(ch,ch,q0);j=ch.jid['access_door_joint'];g=ch.gnames.index('access_door_panel');ch.pose(q);lever=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g];count=math.ceil(1.55*lever/.004);minimum=1e30;bad=None
for k in range(count+1):
 z=q.copy();z[ch.qa['access_door_joint']]=-1.55*k/count;hits,mins,pf=contacts(ch,z)
 if hits:bad=dict(sample=k,hits=hits[:4]);break
 minimum=min(minimum,min((x['reserve_mm'] for cat,x in mins.items() if cat!='self'),default=1e30))
write('results/service_door.json',dict(pass_=bad is None,states_checked=k+1,states_planned=count+1,point_step_mm=1.55*lever/count*1000,blocker=bad,min_reserve_mm=minimum,robot_stopped_brakes_applied=True,scope='Robot gaps during service sweep; hinge/jamb hardware and interlock implementation not qualified'))
q[ch.qa['access_door_joint']]=-1.55
render(xml,q,'Door open: stopped loading / unloading access',('Robot clearance checked' if bad is None else 'Robot clearance FAIL')+' | External service sweep required',focus=(0,.28,1.04),scale=370,labels=False).save(H/'renders/door_open.png')
views=[('wash',(-.47,.62,1.02),920),('process',(.47,.62,1.08),860),('input_output',(0,.29,1.03),650),('waste',(.47,.62,.34),900),('arm_mount',(0,.70,1.3),950)]
for name,focus,scale in views:render(xml,q0,'Station: '+name.replace('_',' '),'Full-size proposed interface; processing is NOT qualified',focus=focus,scale=scale,labels=False).save(H/f'renders/station_{name}.png')
samples=[]
for p in prefix['paths']:
 if not p['ok']:break
 trace=p.get('load_replay',{}).get('trace',[]) or [dict(q=z) for z in p['path']]
 for i,t in enumerate(trace):samples.append(dict(path=p['id'],xml=p['xml'],q=t['q'],source_checked_sample=i,scope='Actual conserved raw-food prefix; no finished food'))
assert samples
strip=Image.new('RGB',(1440,1440),(230,234,237));frames=[]
for k,i in enumerate(np.linspace(0,len(samples)-1,24).round().astype(int)):
 sample=samples[i];im=render(sample['xml'],sample['q'],f'Frame{k+1:02d}: {sample["path"]}','Checked prefix only; food remains RAW',size=(720,480),focus=(0,.44,1.05),scale=180,labels=False);file=f'renders/frame_{k+1:02d}.png';im.save(H/file);strip.paste(im.resize((360,240)),((k%4)*360,(k//4)*240));frames.append(dict(frame=k+1,file=file,**sample))
strip.save(H/'renders/meal_prefix_24.png');write('renders/frame_manifest.json',dict(frames=frames,complete_meal=False,blocked_event=prefix['blocked'],renderer='CPU triangle depth-buffer of full collision primitives and original OEM base meshes; transparent guards for visibility only',max_pixels=1440));print('RENDERS',len(frames)+8)
