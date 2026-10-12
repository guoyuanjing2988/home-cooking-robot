"""Actual MJCF/q overview, open-door parking and 24-frame diagnostic strip."""
import json,numpy as np,mujoco
from scipy.spatial.transform import Rotation
import final_check as f,render_setup as re,motion_r05 as mo
s=f.s;H=s.HERE;O=H/'results';R=H/'renders';ws=json.loads((O/'static_all.json').read_text())['witnesses'];manifest=[]
ch=mo.scene(*mo.items[0][:2],0);q=np.array(s.PARK);q[ch.qa['L_carriage_x']]=.045;re.export(ch,q,'overview','R05: STATIC27/27 / CONNECTED MEAL UNVERIFIED',label='overview')
idle=json.loads((O/'idle_repair.json').read_text());ch.bind_model(mujoco.MjModel.from_xml_path(str(H/'models/idle_r05.xml')));re.export(ch,idle['parked_snapshot']['q'],'parked_doors_open','CONDITIONAL STORAGE SNAPSHOT / ROUTES UNVERIFIED',label='parked')
a=json.loads((R/'parked_doors_open.scene.json').read_text())
a['geoms']=[g for g in a['geoms'] if g['name']!='declared_ceiling'] # cutaway for visibility only; retained by every collision check
for ci,(lo,hi) in enumerate([(-1.8,-.7),(-.1,.69),(1.47,1.8)]):
 count=2 if hi-lo>.6 else 1;width=(hi-lo)/count
 for i in range(count):
  hinge=lo+i*width if i==0 else hi;angle=-90 if i==0 else 90
  a['geoms'].append(dict(name=f'open_cabinet_door_{ci}_{i}',type=6,size=[width/2,.009,.3],pos=[hinge+(-.009 if i==0 else .009),.230-width/2,1.65],rot=Rotation.from_euler('z',angle,degrees=True).as_matrix().tolist(),rgba=[.85,.71,.42,1]))
a.update(camera_scale=7.5,focus=[-.52,-.1,1.5],label='overview',resolution=[1200,800]);(R/'parked_doors_open.scene.json').write_text(json.dumps(a))
selected=[0,1,2,5,6,37,40,42,46,67,76,79,80,81,82,83,85,89,91,92,93,95,99,102]
for j,index in enumerate(selected):
 ph,sg,key=mo.items[index];ch=mo.scene(ph,sg,index);w=ws[key];name=f'frame_{j+1:02}';focus=sg['poses'][-1]['L' if sg['action']=='helper_index' else 'R']['pos'];re.export(ch,w['poses'][-1]['q'],name,'UNCONNECTED DIAGNOSTIC / '+ph['id']+' '+sg['label'][:28],focus=focus,label=name)
 a=json.loads((R/(name+'.scene.json')).read_text());a.update(resolution=[480,320],samples=2,camera_scale=2.7);(R/(name+'.scene.json')).write_text(json.dumps(a));manifest.append(dict(index=j+1,file=name+'.png',stroke=key,q=w['poses'][-1]['q'],source='Independently replayed R05 static witness; transition not executed'))
(R/'manifest.json').write_text(json.dumps(dict(overview='overview.png',parked='parked_doors_open.png',frames=manifest,frame_strip='full_meal_frame_strip.png',status='UNCONNECTED DIAGNOSTIC, NOT AN EXECUTED MEAL',CPU_only=True,door_geometry='Five18mm full-height leaves at90deg; sweep union audited separately',visual_omissions=['south wall/cabinets to expose view','declared ceiling cut away in parked render','logical door-sweep/outlet masks only; all retained in checker']),indent=2));print('Exported26 actual geometry scenes')
