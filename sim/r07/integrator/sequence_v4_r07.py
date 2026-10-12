"""Conserved proposed ledger. No owner update substitutes for a checked motion."""
import os,sys,json,copy,hashlib,xml.etree.ElementTree as E
os.environ['R07_LAYOUT']=sys.argv[1]
import runtime_v4_r07 as v
import mujoco
O=v.O;H=v.H;P=v.P
state={'arm':None,'owners':{},'food_mass_kg':{},'conditions':{},'appliances':{'peeler':'stopped_guard_closed','BFP610':'stopped_lid_closed','secondary':'stopped_guard_closed'},'water':'off'}
for f in P['finished_products']:
 p=f['product'];state['owners']['food:'+p]='raw_'+p+'_land';state['owners']['bowl_'+p]='output_'+p+'_land';state['food_mass_kg'][p]=f['input_mass_kg'];state['conditions'][p]='raw_unmeasured'
for obj in ('wash_pad','eye_core_spoon'):state['owners'][obj]='dock_'+obj+'_face'
for obj in ('cup','cassette','colander'):state['owners'][obj]=obj+'_storage'
initial=copy.deepcopy(state);events=[];strokes=[]
def event(name,change=None,reason='Persistent transform, motion, support and grasp binding required',kind=None,obj=None,support=None,duration=None):
 before=copy.deepcopy(state)
 if change:change()
 events.append(dict(id='N%04d'%len(events),name=name,state_before=before,state_after=copy.deepcopy(state),verified=False,motion_required=duration is None,status='BLOCKED_NOT_EXECUTED',reason=reason,contact_kind=kind,object_id=obj,support_id=support,duration_s=duration))
def move(obj,destination,name):
 source=state['owners'][obj]
 if source==destination:return
 def change():
  if state['arm']==obj:state['arm']=None
  state['owners'][obj]=destination
  if destination=='R':state['arm']=obj
 event(name,change,reason='Conserved '+obj+' from '+source+' to '+destination+'. Full approach, jaw, support and retreat states missing; no teleportation is accepted.',kind='grasp_release_support',obj=obj,support=source if destination=='R' else destination)
def release():
 obj=state['arm']
 if obj:move(obj,'dock_'+obj+'_face' if obj in ('wash_pad','eye_core_spoon') else 'registered_transfer_support','release_'+obj)
def acquire(obj):
 if state['arm']==obj:return
 release();move(obj,'R','approach_grasp_lift_'+obj)
for i,(ph,sg,key) in enumerate(v.items):
 loops=sg.get('loops',{});repeat=loops.get('repeat',1);conditional=None
 if not isinstance(repeat,int):conditional=repeat;repeat=3 if 'eyes' in str(repeat) else 6
 for ri in range(repeat):
  h=sg['poses'][0]['R'];typ=h['held'];prod=h['product'];food='food:'+prod
  obj=None if typ=='empty' else food if typ=='root_food' else 'bowl_'+prod if typ=='carried_bowl' else 'cup' if typ=='food_cup' else 'cassette' if typ=='cut_cassette' else typ
  if typ in ('food_cup','cut_cassette','colander','carried_bowl') and state['owners'][food]!=obj:
   release();move(food,obj,'load_or_collect_all_'+prod+'_into_'+obj)
  if obj:acquire(obj)
  else:release()
  if i in (2,8,17,26,33,35,39,41,47) and state['water']=='off':event('water_on_for_'+prod,lambda:state.update(water='on'),reason='Normally closed valve must be opened before this wash/fill; flow and physical operation unverified')
  if i==39:event('fill_bok_choy_soak_basin',reason='Fill to declared soak level; flow rate, volume and fill/drain interface are unqualified')
  if i==43 and state['water']=='on':event('water_off_before_greens_drain',lambda:state.update(water='off'))
  if sg['station']=='secondary':event('secondary_stop_open_lid',lambda:state['appliances'].update(secondary='stopped_guard_open'),reason='Full stopped lid/guard sweep and latch path remain required')
  if sg['label'].startswith('Rotato_load_approach_'):
   if prod=='carrot':event('carrot_guarded_prehalve_for_140mm_holder_limit',reason='OEM Rotato manual requires food longer than140mm to be cut in half. Input160mm. New guarded cut, conserved pieces and peel quality not qualified; original finished slices retained.')
   event('peeler_open_guard_lower_holder_set_cutter',reason='Exact OEM holder, spike, cutter-height adjustment and complete interlocked retrofit geometry missing')
  strokes.append(dict(id=key+'@%d/%d'%(ri+1,repeat),template=key,index=i,repeat_index=ri,state=copy.deepcopy(state),events_before=len(events),verified=False,conditional_count=conditional,roll_deg=ri*loops.get('roll_increment_deg',0)))
  if sg['label'].startswith('Rotato_load_approach_'):
   release();move(food,'peeler_holder','seat_spike_and_close_upper_holder_'+prod)
   event('peeler_close_guard_start_stop_'+prod,lambda:state['appliances'].update(peeler='stopped_guard_closed'),reason='Cycle duration, peel thickness0.2-0.8mm, gouging, carrot suitability and edible loss unqualified; approaches receive no peeling credit')
   if prod=='carrot':
    for stage in ('raise_holder_remove_and_stage_first_half','load_second_half_adjust_holder_and_cutter','guard_close_second_half_peel_stop','unload_second_half_collect_both_halves'):
     event('carrot_two_half_'+stage,reason='Mandatory second Rotato holder cycle after140mm-limit prehalving. Two-piece geometry, masses and continuous separate ownership bindings are missing. The whole-carrot aggregate is retained unchanged as an unexecuted reservation; this event receives no physical or culinary credit.')
  if sg['label'].startswith('Rotato_unload_approach_'):event('peeler_raise_holder_rock_off_spike_'+prod,reason='Actual rocking extraction and regrasp geometry absent; food identity remains conserved in proposed ownership ledger')
  if sg['action']=='place':
   target=next((c['face'] for c in sg['poses'][-1]['R'].get('contacts',[])),sg['station']+'_registered_support')
   if state['arm']:move(state['arm'],target,'place_release_retreat_'+str(state['arm']))
  if sg['station']=='secondary' and sg['action']=='place':event('close_latch_guarded_cut_and_stop',lambda:state['appliances'].update(secondary='stopped_guard_closed'),reason='Full actuator path, sourced process force, food partitions and quality require checking')
  if sg['label']=='load_slicer':
   for stage in ('lid_pusher_latch','feed_guarded_motor_cycle','motor_off_stop','unplug','unlock_remove_lid','remove_disc_by_hub','unlock_lift_batch_bowl','pour_all_edible_and_terminal_slices'):
    event('BFP610_'+prod+'_'+stage,reason='OEM batch processor; exact lid/pusher/disc/bowl source-matched geometry and feed force remain missing. No R211 continuous-ejection substitution.')
  if sg['label']=='soak_bok_choy':
   event('water_off_after_soak_fill',lambda:state.update(water='off'))
   event('bok_choy_soak',duration=600,reason='Required600s soak; clock cannot run before verified washing/loading/fill')
  if sg['label']=='rinse_pieces':
   assert repeat==3
   event('potato_fresh_starch_rinse_%d'%(ri+1),reason='One fresh-water change per expanded rinse template; three total; inspect no white swirl; mass remains retained')
   if ri==repeat-1:
    event('water_off_before_potato_drain',lambda:state.update(water='off'))
    event('potato_drain',duration=30,reason='Upper end of required20-30s draining; no executed timer credit')
  if 'water_on'==sg['label']:event('water_on',lambda:state.update(water='on'),reason='Normally closed valve and qualified flow command required')
  if sg['label'] in ('water_off','water_off_final'):event('water_off',lambda:state.update(water='off'))
release()
for f in P['finished_products']:
 prod=f['product'];move('food:'+prod,'bowl_'+prod,'collect_inspect_98percent_'+prod);move('bowl_'+prod,'output_'+prod+'_land','present_'+prod)
event('meal_end_fold',reason='Connected final task to folded park with every door full sweep10mm, corridor and front strip checked')
errors=[];previous=initial
for e in events:
 if e['state_before']!=previous:errors.append(e['id']+': discontinuity')
 previous=e['state_after'];owners=previous['owners'];on_arm=[o for o,s in owners.items() if s=='R']
 if on_arm!=([previous['arm']] if previous['arm'] else []):errors.append(e['id']+': arm ownership')
 if previous['food_mass_kg']!=initial['food_mass_kg']:errors.append(e['id']+': mass changed')
connections=[dict(index=i,from_stroke=a['id'],to_stroke=b['id'],from_template_index=a['index'],to_template_index=b['index'],pass_=False,status='BLOCKED_PERSISTENT_BINDING_OR_INTERVENING_EVENTS',allocated_budget_s=65,planner_ran=False) for i,(a,b) in enumerate(zip(strokes,strokes[1:]))]
names=[e['name'] for e in events]
assert names.count('carrot_guarded_prehalve_for_140mm_holder_limit')==1
assert sum(n.startswith('carrot_two_half_') for n in names)==4
assert names.count('peeler_close_guard_start_stop_carrot')==1 and names.count('peeler_close_guard_start_stop_potato')==1
assert sum(n.startswith('potato_fresh_starch_rinse_') for n in names)==3
assert names.count('potato_drain')==names.count('bok_choy_soak')==1
out=dict(schema='r07.v4.proposed-conserved-sequence',layout=v.ID,status='NOT_EXECUTED',initial_state=initial,executed_state=initial,events=events,expanded_strokes=strokes,expanded_connections=connections,final_proposed_state=state,discrete_state_chain_errors=errors,mass_input_kg=sum(initial['food_mass_kg'].values()),mass_lost_measured_kg=None,finished_products=P['finished_products'],scope='Single symbolic proposal with exactly one owner per object and constant whole input mass. Every ownership change is blocked until continuous physical binding. Material partition/waste topology unqualified: full whole-food envelopes retained in initial model; no meal geometry or quality credit.',recipe_assumptions={'potato_eyes':3,'basal_stalks':6,'extra_eyes_or_stalks':'Inspect and extend/replan; never omit'},count_definition='59 robot template diagnostics plus explicit appliance/handoff events. Expanded connection denominator is recipe repeats of those templates, not59minus1; event paths are separate obligations.')
(O/'state_sequence.json').write_text(json.dumps(out,indent=2,allow_nan=False))
ch=v.scene(0);root=E.fromstring(ch.xml);w=root.find('worldbody');bindings={}
for g in list(w.findall('geom')):
 if not g.get('name','').startswith('staged_raw_'):continue
 prod=g.get('name')[11:];pos=g.get('pos');g.set('pos','0 0 0');g.set('mass',str(initial['food_mass_kg'][prod]));body=E.SubElement(w,'body',name='meal_food_'+prod,mocap='true',pos=pos);w.remove(g);body.append(g);bindings['food:'+prod]=dict(body=body.get('name'),mass_kg=initial['food_mass_kg'][prod],initial_owner=initial['owners']['food:'+prod],geometry='Full unchanged original input')
xml=E.tostring(root,encoding='unicode');m=mujoco.MjModel.from_xml_string(xml);(H/'models/persistent_meal.xml').write_text(xml)
(O/'persistent_model.json').write_text(json.dumps(dict(layout=v.ID,model='models/persistent_meal.xml',model_sha256=hashlib.sha256(xml.encode()).hexdigest(),ngeom=m.ngeom,bindings=bindings,unique_food_bodies=len(bindings),ownership_pass=not errors,executable=False,missing=['Source-matched appliance mechanisms and process force','Conserved cut pieces, waste and quality measurements','Continuous support/jaw/container binding','Connected full meal and fold'],scope='Initial conserved model only. Mocap is not executed to teleport food; all four raw inputs and real-sized fixed appliances remain.'),indent=2))
assert not errors and len(bindings)==4
print('SEQUENCE',len(strokes),len(connections),len(events),'events; zero executed')
