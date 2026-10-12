"""One persistent proposed meal state; unsupported transitions are explicit."""
import json,copy,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;p=json.loads((H/'results/process_v3.json').read_text())
state=dict(arms={s:dict(held=None,jaw='open',jaw_m=.09 if s=='R' else .11) for s in ['R','L']},objects={},supports=dict(peel_clamp='open',cassette_latch='open',secondary_lid='closed',brush_angle_deg=0,slicer_lid='closed',slicer_pusher='up',slicer_motor='off',sink_water_level_m=.65),food={})
for f in p['finished_products']:
 product=f['product'];state['food'][product]=dict(mass_kg=f['input_mass_kg'] if 'input_mass_kg' in f else dict(carrot=.12,potato=.20,leafy_greens=.1,tomato=.15)[product],owner='raw_'+product+'_land',condition='raw',bowl='bowl_'+product,quality_measured=False)
 state['objects']['bowl_'+product]=dict(owner='output_'+product+'_land',kind='carried_bowl',contents=[])
for typ in ['peeler','wash_pad','eye_core_spoon']:state['objects'][typ]=dict(owner='dock_'+typ+'_face',kind=typ)
for obj,kind,support in [('cup','food_cup','cup_storage'),('colander','colander','colander_storage'),('cassette','cut_cassette','cassette_storage'),('slicer_pusher','pusher','slicer'),('slicer_lid','lid','slicer'),('secondary_lid','lid','secondary'),('root_brush','brush','sink')]:state['objects'][obj]=dict(owner=support,kind=kind)
events=[];strokes=[];eid=0
def event(name,phase,changes,requires_motion=False,reason=None):
 global eid
 before=copy.deepcopy(state);changes();eid+=1
 events.append(dict(id=f'E{eid:04}',name=name,phase=phase,state_before=before,state_after=copy.deepcopy(state),motion_required=requires_motion,verified=False if requires_motion else None,reason=reason))
def release(side,phase,support):
 arm=state['arms'][side];obj=arm['held']
 if obj is None:return
 def mutate():
  if obj.startswith('food:'):state['food'][obj[5:]]['owner']=support
  else:state['objects'][obj]['owner']=support
  arm.update(held=None,jaw='open',jaw_m=.09 if side=='R' else .11)
 event('jaw_open_release_'+obj,phase,mutate,True,'Support approach and continuous jaw motion need certification; own-support permission is endpoint-only')
def acquire(side,obj,kind,phase,jaw):
 arm=state['arms'][side]
 if arm['held']==obj:return
 if arm['held'] is not None:release(side,phase,'dock_'+arm['held']+'_face' if arm['held'] in ['peeler','wash_pad','eye_core_spoon'] else 'transfer_work_support')
 source=state['food'][obj[5:]]['owner'] if obj.startswith('food:') else state['objects'][obj]['owner']
 def mutate():
  if obj.startswith('food:'):state['food'][obj[5:]]['owner']=side
  else:state['objects'][obj]['owner']=side
  arm.update(held=obj,jaw='closed',jaw_m=jaw)
 event('approach_close_pick_'+obj,phase,mutate,True,'Conserved object from '+source+'; no instantaneous pose transfer is credited')
for ph in p['phases']:
 for sg in ph['segments']:
  loops=sg.get('loops',{});repeat=loops.get('repeat',1)
  conditional=None
  if not isinstance(repeat,int):conditional=repeat;repeat=3 if 'eyes' in str(repeat) else 6
  for ri in range(repeat):
   phase=ph['id'];key=phase+'__'+sg['label'].replace(' ','_');suffix=f'@{ri+1}/{repeat}'
   if sg['station']=='secondary':
    event('motor_off_open_secondary_lid',phase,lambda:state['supports'].update(secondary_lid='open'),True,'Full lid sliding sweep, including parked objects, required')
   if any(h['held']=='colander' for h in sg['poses'][0].values()) and state['supports']['brush_angle_deg']==0:
    event('pivot_full_brush_90deg',phase,lambda:state['supports'].update(brush_angle_deg=90),True,'Full stem/face/drive retained during hinge sweep')
   for side,h in sg['poses'][0].items():
    typ=h['held'];prod=h['product']
    if typ=='empty':release(side,phase,'transfer_work_support');continue
    obj='food:'+prod if typ=='root_food' else 'bowl_'+prod if typ=='carried_bowl' else 'cup' if typ=='food_cup' else 'cassette' if typ=='cut_cassette' else typ
    if typ in ('food_cup','cut_cassette','colander') and state['food'][prod]['owner']!=obj:
     def load(prod=prod,obj=obj):state['food'][prod]['owner']=obj;state['objects'][obj]['contents']=[prod]
     event('load_'+prod+'_into_'+obj,phase,load,True,'Necessary conserved food handoff; added motion has no supplied endpoint witness')
    if typ=='carried_bowl' and state['food'][prod]['owner']!=obj:
     def collect(prod=prod,obj=obj):
      state['food'][prod]['owner']=obj;state['objects'][obj]['contents']=[prod]
     event('collect_all_edible_'+prod+'_into_'+obj,phase,collect,True,'Necessary output collection; retain terminal slices, every wedge and all edible solids. Yield and path not verified.')
    acquire(side,obj,typ,phase,h['jaw_opening_m'])
   before=copy.deepcopy(state)
   if sg['station']=='peel' and sg['poses'][0]['R']['held'] in ('peeler','eye_core_spoon'):
    event('clamp_peel_food',phase,lambda:state['supports'].update(peel_clamp='latched'),True,'Actual latch travel/preload retained')
   if sg.get('action')=='helper_index':event('open_peel_clamp_for_helper_index',phase,lambda:state['supports'].update(peel_clamp='open'),True,'No changing support ownership without a modeled clamp action')
   strokes.append(dict(id=key+suffix,template=key,phase=phase,repeat_index=ri,conditional_count=conditional,state=before,pose_count=len(sg['poses']),jaw_motion_required=False,verified=False,roll_deg=ri*loops.get('roll_increment_deg',0),quality_gate=loops.get('coverage')))
   if sg.get('action')=='place':
    for side,h in sg['poses'][-1].items():
     if h['held']=='empty':continue
     face=next((c['face'] for c in h.get('contacts',[])),sg['station']+'_registered_support')
     release(side,phase,face)
   if sg['station']=='secondary' and sg.get('action')=='place':
    event('close_latch_detach_guarded_cut',phase,lambda:state['supports'].update(cassette_latch='latched',secondary_lid='closed'),True,'Blade reaction stays internal only after release, latch and lid interlock proof')
   if sg['label']=='load_slicer':
    event('appliance_pusher_down_cut_then_up',phase,lambda:state['supports'].update(slicer_pusher='up',slicer_motor='off'),True,'Includes downstroke, guarded motor run, stop and upstroke; OEM pusher force/interface unqualified')
    event('collect_root_slices_into_bowl',phase,lambda prod=sg['poses'][0]['R']['product']:state['food'][prod].update(owner='bowl_'+prod,condition='sliced'),True,'All edible slices and terminal pieces must be accounted, not teleported')
   if sg['label']=='soak_bok_choy':event('fill_soak_600s_drain',phase,lambda:state['supports'].update(sink_water_level_m=.65),False,'50.16L filling and600s soaking retained; drain required')
   if sg.get('action')=='helper_index':
    event('reclamp_before_helper_release',phase,lambda:state['supports'].update(peel_clamp='latched'),True,'Actual latch travel must pass before support transfer')
    release('L',phase,'peel_land')
for side in ['R','L']:release(side,'Q27','clean_storage')
events.append(dict(id='FINAL',name='quality_inspection_and_delivery',phase='Q26',state_after=copy.deepcopy(state),verified=False,reason='Physical wash/peel/cut/yield gates unmeasured; no claim of achieved final ownership'))
out=dict(schema='r04.persistent-meal.v1',status='PROPOSED_SEQUENCE_NOT_EXECUTABLE',initial_state=events[0]['state_before'],events=events,expanded_strokes=strokes,final_proposed_state=state,mass_input_kg=.57,mass_loss_measured_kg=None,assumptions=dict(basal_stalk_count=6,wide_stalks=2,potato_eyes=3,variable_count_policy='Inspect; if additional eyes/stalks, extend operations and replan; do not skip them.'),ownership_invariant='Exactly one owner per food/tool/vessel at each recorded discrete state; all changes require explicit events. No event with an unverified path is credited as executed.',contact_discontinuity=dict(gap_mm=5,permission='pickup/release endpoint only',proof='Distance from continuous rigid geometry to a support is continuous. From d(0)=0 to d(1)>=5mm, intermediate-value theorem requires 0<d(t)<5mm for some t>0. With no non-endpoint permission, the pickup edge cannot pass any continuous planner. Changing arms, forces or seeds cannot fix it.'),unverified_required_events=sum(e.get('motion_required',False) for e in events))
(H/'results/state_sequence.json').write_text(json.dumps(out,indent=2));print('events',len(events),'expanded strokes',len(strokes),'required unverified events',out['unverified_required_events'])
