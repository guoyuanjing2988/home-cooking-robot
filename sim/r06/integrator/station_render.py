"""CPU renders of exact selected geometry and checked prefix, not a complete meal."""
from station_spec import *
from PIL import Image,ImageDraw,ImageFont
import ast
for file,names in [('renders.py',('font','local_faces','load')),('rescue_renders.py',('render',))]:
 for node in ast.parse((H/file).read_text()).body:
  if isinstance(node,ast.FunctionDef) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),file,'exec'),globals())
CACHE={};prefix=json.loads((H/'results/executed_prefix.json').read_text());first=prefix['states'][0];xml=first['xml'];q0=np.array(first['q']);v=32
render(xml,q0,'R06 revision3: whole-pan workstation','1506 x 906 mm closed guards | UR5e | Processing remains blocked',focus=(0,.44,1.12),scale=385,labels=False).save(H/'renders/overview.png')
ch=Workcell(v);q=q0.copy();j=ch.jid['access_door_joint'];g=ch.gnames.index('access_door_panel');ch.pose(q);lever=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[j])+ch.m.geom_rbound[g];count=math.ceil(1.55*lever/.004);minimum=1e30;bad=None
for k in range(count+1):
 z=q.copy();z[ch.qa['access_door_joint']]=-1.55*k/count;hits,mins,pf=contacts(ch,z)
 if hits:bad=dict(sample=k,hits=hits[:4]);break
 minimum=min(minimum,min((x['reserve_mm'] for cat,x in mins.items() if cat!='self'),default=1e30))
write('results/service_door.json',dict(pass_=bad is None,states_checked=k+1,states_planned=count+1,point_step_mm=1.55*lever/count*1000,blocker=bad,min_reserve_mm=minimum,robot_stopped_brakes_applied=True,scope='Robot gaps during service sweep; hinge/jamb hardware and interlock implementation not qualified'))
q[ch.qa['access_door_joint']]=-1.55
render(xml,q,'Door open: stopped loading / unloading',('Robot clearance checked' if bad is None else 'Robot clearance FAIL')+' | Additional external service space',focus=(0,.28,1.12),scale=360,labels=False).save(H/'renders/door_open.png')
last=prefix['states'][-1];views=[('wash',(-.45,.62,.97),910),('process',(-.45,.64,1.50),760),('input_output',(0,.29,1.03),650),('waste',(-.43,.62,.40),880),('arm_mount',(0,.70,1.3),880)]
for name,focus,scale in views:render(last['xml'],last['q'],'Station: '+name.replace('_',' '),'Actual last checked state; all food still RAW; interfaces unqualified',focus=focus,scale=scale,labels=False).save(H/f'renders/station_{name}.png')
samples=[]
for path in prefix['paths']:
 if not path['ok']:break
 trace=path.get('load_replay',{}).get('trace',[]) or [dict(q=z) for z in path['path']]
 for i,t in enumerate(trace):samples.append(dict(path=path['id'],xml=path['xml'],q=t['q'],source_checked_sample=i,scope='Actual conserved raw-food prefix; no finished food'))
assert samples
strip=Image.new('RGB',(1440,1440),(230,234,237));frames=[]
for k,i in enumerate(np.linspace(0,len(samples)-1,24).round().astype(int)):
 sample=samples[i];im=render(sample['xml'],sample['q'],f'Frame{k+1:02d}: {sample["path"]}','Checked prefix only; food remains RAW',size=(720,480),focus=(0,.44,1.12),scale=180,labels=False);file=f'renders/frame_{k+1:02d}.png';im.save(H/file);strip.paste(im.resize((360,240)),((k%4)*360,(k//4)*240));frames.append(dict(frame=k+1,file=file,**sample))
strip.save(H/'renders/meal_prefix_24.png');write('renders/frame_manifest.json',dict(frames=frames,complete_meal=False,blocked_event=prefix['blocked'],renderer='CPU triangle depth-buffer of full collision primitives and original OEM base meshes; transparent guards for visibility only',max_pixels=1440));print('RENDERS',len(frames)+8)
