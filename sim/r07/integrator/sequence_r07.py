"""Reduced, single-owner meal obligations; no event gets execution credit."""
import json,copy,runpy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
runpy.run_path(str(H/'state_sequence.py'))
old=json.loads((O/'state_sequence.json').read_text());events=[];skipped=[]
for e in old['events']:
 if e.get('state_before')==e.get('state_after') and e.get('motion_required') and not e['name'].startswith(('appliance_pusher','collect_')):
  skipped.append(dict(id=e['id'],name=e['name'],reason='Idempotent support state: already open/latched/held; no additional actuator command. Preconditions remain required.'));continue
 name=e['name'];stages=['actuator_path']
 if name.startswith('approach_close_pick'):stages=['straight_approach_le50mm','jaw_close','straight_lift_le50mm_then_full_gap']
 elif name.startswith('jaw_open_release'):stages=['straight_approach_le50mm','jaw_open','empty_gripper_departure']
 elif name.startswith('appliance_pusher'):stages=['pusher_down_guard_latched','motor_cut_stop','pusher_up_blade_stopped']
 elif 'lid' in name:stages=['blade_stop_verified','full_lid_sweep_latch']
 elif 'brush' in name:stages=['full_brush_hinge_sweep']
 if not e.get('motion_required'):stages=['process_timer']
 if name=='collect_root_slices_into_bowl':stages=[]
 for j,stage in enumerate(stages):
  x=copy.deepcopy(e);x.update(id=e['id']+'.'+str(j+1),parent_event=e['id'],stage=stage,verified=False,path_status='NOT_EXECUTED',geometric_model_status='Persistent approach/ownership/actuator binding required',contact_kind='grasp_release_support' if 'pick' in name or name.startswith('jaw_open_release') else 'working_stroke' if 'cut' in name else None)
  if len(stages)==3 and ('pick' in name or name.startswith('jaw_open_release')):
   x['state_before']=copy.deepcopy(e['state_before'] if j<2 else e['state_after']);x['state_after']=copy.deepcopy(e['state_before'] if j==0 else e['state_after'])
  elif 'state_before' in e:
   x['state_before']=copy.deepcopy(e['state_before']);x['state_after']=copy.deepcopy(e['state_after'] if j==len(stages)-1 else e['state_before'])
  events.append(x)
 # Unlike R211, BFP610 collects internally. Explicitly retain OEM-required
 # shutdown, unplugging, lid removal, disc removal and batch unloading.
 if name=='collect_root_slices_into_bowl':
  bfpstages=['motor_off_stop','unplug','unlock_remove_lid','remove_disc_by_hub','unlock_lift_batch_bowl','pour_collect_terminal_and_slices']
  for j,stage in enumerate(bfpstages):
   events.append(dict(id=e['id']+'.BFP.'+stage,parent_event=e['id'],name='bfp610_'+stage,phase=e['phase'],stage=stage,motion_required=True,verified=False,path_status='BLOCKED_OEM_INTERFACE_MODEL',state_before=copy.deepcopy(e['state_before']),state_after=copy.deepcopy(e['state_after'] if j==len(bfpstages)-1 else e['state_before']),reason='Exact OEM bowl/lid/pusher/disc geometry and continuous handoff still missing; no continuous-discharge substitution'))
seq=dict(old,schema='r07.persistent-conserved-meal-obligations',events=events,status='FAILED_NOT_EXECUTED',contact_discontinuity=None,removed_idempotent_commands=skipped,unverified_required_events=sum(e.get('motion_required',False) for e in events),decisions=dict(contact_window_mm=50,point_step_mm=4,planner_budget_s=65,contact_kind_required=True,working_contact_on_transit=False))
seq['expanded_connections']=[dict(index=i,from_stroke=a['id'],to_stroke=b['id'],from_template=a['template'],to_template=b['template'],pass_=False,status='Persistent transform/attachment and intervening event paths required') for i,(a,b) in enumerate(zip(seq['expanded_strokes'],seq['expanded_strokes'][1:]))]
seq['conservation_scope']='Each original complete input stays present until a witnessed partition, with one owner per object. No unverified cut deletes/shrinks a body; full source food remains in the persistent scene. The final proposed ownership ledger is not a geometric execution.'
previous=seq['initial_state'];errors=[]
for e in events:
 if e.get('state_before') is not None and e['state_before']!=previous:errors.append(e['id'])
 if e.get('state_after') is not None:previous=e['state_after']
seq['discrete_state_chain_errors']=errors
(O/'state_sequence.json').write_text(json.dumps(seq,indent=2))
print('events',len(events),'required',seq['unverified_required_events'],'idempotent removed',len(skipped),'connections',len(seq['expanded_connections']))
