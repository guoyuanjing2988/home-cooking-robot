"""Reduce repeated hand peeling, preserving residual finishing obligations.

An appliance approach is never credited as an executed load/cycle/unload.
The unresolved OEM interfaces remain explicit blocking events in the sequence.
"""
import sys,json,copy,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1]
c=json.loads((O/'layouts'/f'{ID}.json').read_text());p=json.loads((O/'layouts'/f'{ID}_process.json').read_text());flat=[(ph,sg) for ph in p['phases'] for sg in ph['segments']]
out=[];index=0
removed=set(range(4,30))|set(range(44,66))
for old,(ph,sg) in enumerate(flat):
 if old in removed:continue
 sg=copy.deepcopy(sg);sg['source_stroke_index']=old
 if old in (3,43):
  prod='carrot' if old==3 else 'potato';x,y=c['m5_center_xy']
  small=c.get('peeler_model')=='Rotato Express';z=1.32 if small else 1.45
  sg.update(label=('Rotato' if small else 'M5')+'_load_approach_'+prod,station='appliance_approach',action='transfer',interface_qualified=False,
   qualification_blocker='OEM M5 lid twist/lift, interior dimensions, powered cycle and stopped retrieval require a matched interface model; external approach alone is not loading or peeling.')
  hand=copy.deepcopy(flat[1 if old==3 else 41][1]['poses'][-1]['R'])
  hand.update(pos=[x,y-.095,z],contacts=[],approach=[0,0,-1],jaw_axis=[0,1,0])
  sg['poses']=[{'R':dict(hand,pos=[x,y-.095,z+.03])},{'R':hand}]
  if small:
   sg['qualification_blocker']='Rotato commodity mechanism inside a declared full300x300x350mm interlocked design reservation. OEM says >140mm food must be halved; cartridge, holder rocking extraction and blade guard interface are not modelled/qualified. Carrot pre-halving and peel coverage remain blocking process events, not waived.'
  out.append(dict(id='V4_'+str(index).zfill(2),name=sg['label'],segments=[sg]));index+=1
  sg=copy.deepcopy(sg);sg['label']=('Rotato' if small else 'M5')+'_unload_approach_'+prod;sg['poses']=list(reversed(sg['poses']))
 out.append(dict(id='V4_'+str(index).zfill(2),name=sg['label'],segments=[sg]));index+=1
p['phases']=out
if c.get('horizontal_tool_docks'):
 import numpy as np
 from scipy.spatial.transform import Rotation
 r=Rotation.from_euler('x',90,degrees=True)
 for ph in p['phases']:
  for sg in ph['segments']:
   if sg['station']!='dock':continue
   for hands in sg['poses']:
    for h in hands.values():
     typ=h['held']
     if typ not in ('wash_pad','eye_core_spoon'):continue
     x,y,_=c['station_frames']['dock_'+typ]['new_center'];pivot=np.array([x,y,1.0]);h['pos']=(pivot+r.apply(np.array(h['pos'])-pivot)+[0,0,c.get('horizontal_dock_lift',0)]).tolist()
     for key in ('approach','jaw_axis'):h[key]=r.apply(h[key]).tolist()
     for key in ('nominal_forces_N','check_forces_N','nominal_moments_Nm','check_moments_Nm'):h[key]=[r.apply(a).tolist() for a in h[key]]
     for contact in h['contacts']:contact['face_geometry']='Same full dock rotated90deg aroundX: its local+Z mating face points toward world-Y; full own-object support contact only.'
p['night_process_change']=dict(original_strokes=105,retained_or_replaced_strokes=index,removed_original_indices=sorted(removed),appliance='Sammic M-5',quality_credit=False,
 essential_unqualified=['M5 lid opening, load, motor cycle and stopped unload','peel coverage/depth and loss for single120g carrot/200g potato','BFP610 lid/pusher/disc removal and batch unloading','food/container acquisition and support transitions'],
 retained_finishing=['carrot end trim, terminal10mm and final5mm slice','potato eye removal and2-3 fresh starch rinses,20-30s drain','bok choy root trim, every basal crease rubbed/inspected,600s soak,40mm sections and<=15mm stalk width','tomato core removal and eight radial wedges','>=98percent edible transfer and separate outputs for all four'])
(O/'layouts'/f'{ID}_process_v4.json').write_text(json.dumps(p,indent=2))
print(ID,index,'robot stroke templates; appliance interface events remain blocking')
