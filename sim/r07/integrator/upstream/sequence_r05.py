"""Explicit connected-meal requirements, never crediting a missing handoff."""
import json,copy,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';old=json.loads((H/'upstream_r04/results/state_sequence.json').read_text());p=json.loads((O/'process_v3.json').read_text());events=[]
for e in old['events']:
 if not e.get('motion_required'):events.append(dict(e,binding_contact_window=True));continue
 name=e['name'];stages=['actuator_path']
 if name.startswith('approach_close_pick'):stages=['straight_approach_le50mm','jaw_close','straight_lift_le50mm_then_full_gap']
 elif name.startswith('jaw_open_release'):stages=['straight_approach_le50mm','jaw_open','empty_gripper_departure']
 elif name.startswith('appliance_pusher'):stages=['pusher_down_with_guard_latched','motor_cut_and_stop','pusher_up_with_blade_stopped']
 elif 'lid' in name:stages=['blade_stop_verified','full_lid_sweep_and_latch']
 elif 'brush' in name:stages=['full_brush_hinge_sweep']
 for j,stage in enumerate(stages):
  x=copy.deepcopy(e);x.update(id=e['id']+'.'+str(j+1),parent_event=e['id'],stage=stage,verified=False,path_status='NOT_EXECUTED',geometric_model_status='Requires continuous pose and persistent-body binding; template substitution is not execution',binding_contact_window=True)
  if len(stages)==3 and ('pick' in name or name.startswith('jaw_open_release')):
   x['state_before']=copy.deepcopy(e['state_before'] if j<2 else e['state_after']);x['state_after']=copy.deepcopy(e['state_before'] if j==0 else e['state_after'])
  x['reason']='Explicit '+stage+' for '+name+'. Specific own-support permission lasts only along the declared straight <=50mm normal/insertion axis until the pair reaches 5mm. No fixture/guard/wall exemption.'
  events.append(x)
seq=dict(old,schema='r05.persistent-meal.v2',events=events,contact_discontinuity=None,status='EXPLICIT_REQUIRED_SEQUENCE_PENDING_PATHS',unverified_required_events=sum(e.get('motion_required',False) for e in events),decisions=dict(contact_window_mm=50,point_step_mm=4,planner_budget_s=65,wall_faces=['wall_mount_-1.84 rear +Y','wall_mount_0.18 rear +Y']))
seq['expanded_connections']=[dict(index=i,from_stroke=a['id'],to_stroke=b['id'],from_template=a['template'],to_template=b['template'],pass_=False,status='Requires recipe-expanded persistent state, intervening events and continuous object transforms') for i,(a,b) in enumerate(zip(seq['expanded_strokes'],seq['expanded_strokes'][1:]))]
seq['food_partition_plan']={'carrot':dict(input_kg=.12,ends_mm=4,slice_pitch_mm=5,terminal_stub_mm=10,geometry='Partition full source box at registered cut planes; retain both 5mm terminal pieces and scraps'), 'potato':dict(input_kg=.20,ends_mm=4,longitudinal_halves=2,slice_pitch_mm=5,eyes=3,fresh_rinses=3,drain_s=30),'leafy_greens':dict(input_kg=.1,root_trim_mm=8,stalks=6,wide_stalks=2,split_width_mm=12,sections_mm=40,soak_s=600),'tomato':dict(input_kg=.15,sectors=8,nominal_angle_deg=45,core='Depth-limited spoon; preserve seed cavity and measured waste')}
seq['food_partition_execution']='Not executed: a partition specification does not prove geometry, material loss or yield. Full input envelope remains in persistent model until a witnessed cut and collection.'
(O/'state_sequence.json').write_text(json.dumps(seq,indent=2))
ledger=json.loads((H/'upstream_r04/results/intended_contacts.json').read_text())
for row in ledger['rows']:
 row['policy']='Specific named food/tool working face along its working stroke' if any(x in row['face'] for x in ['work_face','clamped_food','wash_food','crease']) or row['held']=='wash_pad' and row['face']=='peel_food_land' else 'Own named support face: grasp/release and declared straight <=50mm approach/retreat, only until5mm gap'
 row['window_max_mm']=50 if 'Own' in row['policy'] else None;row['insertion_axis']=[0,0,1] if 'Own' in row['policy'] else None
ledger['wall_faces']=[dict(bracket=x,face='rear +Y',reason='Full unrotated plate lies wholly on room side of north-wall front plane; only this planar face meets the wall') for x in ['wall_mount_-1.84','wall_mount_0.18']]
ledger['policy_source']='DECISIONS.md 2026-10-08 Contact windows and path checking';(O/'intended_contacts.json').write_text(json.dumps(ledger,indent=2))
print('sequence events',len(events),'required internal events',seq['unverified_required_events'],'expanded strokes',len(seq['expanded_strokes']),'connections',len(seq['expanded_connections']))
