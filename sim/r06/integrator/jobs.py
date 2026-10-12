"""Explicit static/motion obligations. Proposed states are not executed states."""
from cell import *
EVENTS=json.loads((H/'sources/events_A.json').read_text())
LEDGER=json.loads((H/'sources/state_ledger_A.json').read_text())
V=7
ORIG={b['id']:b['pose']['position_m'] for b in SPEC['bodies'] if b['parent']=='world'}
SEATS={'wash_basin':[-.49,.49,1.073],'process_cell':[.45,.505,.984],'inspection_dock':[0,.475,.974]}
def seating(obj,station):
 if station.startswith('dock_'):return np.array(ORIG[obj])
 if station=='output_bok_choy_at_wash':return np.array(SEATS['wash_basin'])+[0,0,.02]
 return np.array(SEATS[station])
def grip_pos(obj,origin):
 gp=np.array(next(x['pose_local']['position_m'] for x in SPEC['grasp_handles'] if x['object_id']==obj));gp[2]+=.02
 return np.array(origin)+gp
def windows(ch,station,origin):
 obj=ch.held_id
 if obj is None:return []
 prod=obj.removeprefix('output_');parts=['pan_'+prod+'_'+n for n in ('floor','left','right','front','rear')] if obj.startswith('output_') else ['clean_leaf_floor']
 faces=['dock_'+prod+'_land'] if station.startswith('dock_') else ['wash_lift_left','wash_lift_right'] if station=='wash_basin' else ['cell_land_a','cell_land_b'] if station=='process_cell' else ['inspection_land']
 return [dict(kind='grasp_release_support',object_id=obj,support_id=station,side='R',face=f,held_parts=parts,tcp_origin_m=grip_pos(obj,origin).tolist(),tcp_rotation=ch.rot.tolist(),normal=[0,0,1],reason='Own bottom surface and bottom wall rim on named top land; only straight <=50mm lift/approach; permission ends at 5mm') for f in faces]
def jobs():
 out=[];locations={k:ORIG[k] for k in ('output_carrot','output_potato','output_bok_choy','output_tomato','clean_leaf_basket')};supports={k:'dock_'+k[7:] if k.startswith('output_') else 'inspection_dock' for k in locations}
 for e in EVENTS:
  obj=e['object_id'];act=e['action'];prior=copy.deepcopy(locations)
  if act in ('grasp','release'):
   station=supports[obj] if act=='grasp' else e['station'];origin=np.array(locations[obj]) if act=='grasp' else seating(obj,station);target=grip_pos(obj,origin)
   targets=[target,target+[0,0,.05]] if act=='grasp' else [target+[0,0,.05],target]
   out.append(dict(id=e['id']+'_'+act,macro=e['id'],kind='grasp_release_support',held=obj,station=station,origin=origin.tolist(),targets=[x.tolist() for x in targets],locations=prior,load='load_insert' if station=='process_cell' else 'carry',admission='unresolved_leaf_topology' if obj=='clean_leaf_basket' else 'full_robot_static',unresolved='Clean-basket food geometry requires the unverified six-leaf ownership transition; empty basket static poses do not admit loaded leaves.' if obj=='clean_leaf_basket' else None))
   if act=='release':locations[obj]=origin.tolist();supports[obj]=station
  elif act in ('grasp_leaf','work_basal_crease','release_leaf'):
   out.append(dict(id=e['id']+'_'+act,macro=e['id'],kind='working_stroke' if act=='work_basal_crease' else 'grasp_release_support',held=None,station=e['station'],targets=[[0,.24,1.32]],locations=prior,load='leaf_brush' if act=='work_basal_crease' else 'carry',admission='unresolved_leaf_topology',unresolved='Basal leaf pose/retained cup grasp not supplied; source six leaves require physically verified root separation. No whole-head replacement or remote leaf spawn admitted.'))
  else:
   steps=[]
   for step in e['substeps'] or [act]:
    if step=='feed_cut_repeats':
     count=28 if obj=='food_carrot' else 16
     if obj=='food_potato':steps+=['longitudinal_halving_and_supported_reorientation_required']
     for k in range(count):steps += [f'feed5mm_{k+1}',f'cut5mm_{k+1}',f'blade_retract_{k+1}']
    elif step=='last10mm_stub_two_cuts':steps += ['terminal_feed_1','terminal_cut_1','terminal_retract_1','terminal_feed_2','terminal_cut_2','terminal_retract_2','terminal_edible_piece_release']
    elif step=='rotary_peel':
     for k in range(8):steps += [f'root_rotate_index_{k+1}',f'peel_work_pass_{k+1}',f'peeler_retract_{k+1}']
    elif step=='fresh_fill_lift_drain_repeat3':
     for k in range(3):steps += [f'fresh_fill6L_{k+1}',f'lift_insert_{k+1}',f'drain_dirty_pan_{k+1}',f'fresh_spray_{k+1}',f'lower_insert_{k+1}']
    elif step=='length_balanced_section_repeats':
     for k in range(24):steps += [f'feed40p5mm_{k+1}',f'greens_section_cut_{k+1}',f'blade_retract_{k+1}']
    elif step=='split_wide_stalks2':steps += ['split_wide_stalk_1','split_retract_1','split_wide_stalk_2','split_retract_2']
    else:steps.append(step)
   for i,step in enumerate(steps):
    out.append(dict(id=e['id']+f'_{i:02d}_'+step,macro=e['id'],kind='working_stroke' if any(w in step for w in ('work','cut','peel','brush','split')) else 'grasp_release_support' if any(w in step for w in ('lift','lower','latch','clamp')) else 'mechanism_or_wait',held=None,station=e['station'],targets=[[0,.24,1.32]],locations=prior,load='carry',admission='robot_retracted_static_only',substep=step,unresolved='Appliance stroke, water/process feedback or food topology is a required independent obligation; parked-arm static success alone cannot admit it.'))
 # Expand the lid contract that is implicit in the station macros. These are
 # acceptance obligations even though no pan-lid actuator has been qualified.
 for e in EVENTS:
  if e['kind']=='appliance' and e['station'] in ('wash_basin','process_cell') and (e['object_id'].startswith('food_') or e['object_id']=='clean_leaf_basket'):
   pan='output_'+e['object_id'][5:] if e['object_id'].startswith('food_') else 'clean_leaf_basket'
   if pan not in locations:continue
   for mode in ('open_after_seating','close_before_transport'):
    prior=next(x['locations'] for x in out if x['macro']==e['id'])
    out.append(dict(id=e['id']+'_pan_lid_'+mode,macro=e['id'],kind='mechanism_or_wait',held=None,station=e['station'],targets=[[0,.24,1.32]],locations=copy.deepcopy(prior),load='carry',admission='robot_retracted_static_only',substep='pan_lid_'+mode,pan_id=pan,unresolved='Implicit container lid contract expanded; exact actuator/food interference and persistent intermediate states require checked motion.'))
 # Retract/park is an independent, non-working obligation. Preserve the
 # original 497 indices so completed random-start evidence remains traceable.
 extra=[]
 for j in out:
  t=j.get('substep','')
  if t.startswith(('peeler_retract','split_retract')):j['kind']='mechanism_or_wait'
  if '_and_retract_' in t or '_then_park' in t:
   r=copy.deepcopy(j);r['id']=j['id']+'_separate_retract';r['kind']='mechanism_or_wait';r['substep']=t.replace('_work_and_retract_','_retract_').replace('_work_then_park','_retract');r['unresolved']='Separate non-working retract; no working contact permission inherited.';extra.append(r)
   j['substep']=t.replace('_and_retract_','_').replace('_work_then_park','_work');j['kind']='working_stroke';j['split_original_substep']=t
 for e in EVENTS:
  if e['kind']=='appliance' and e['station']=='process_cell':
   parent=next(j for j in out if j['macro']==e['id'])
   for stage in ('close_before_process','open_after_process'):
    for cover in ('cell_roof','cell_front_header'):
     j=copy.deepcopy(parent);j.update(id=e['id']+'_'+cover+'_'+stage,kind='mechanism_or_wait',substep=cover+'_'+stage,admission='robot_retracted_static_only',unresolved='Added full guard actuator requires its own non-working sweep and lock-state proof.');extra.append(j)
 return out+extra
JOBS=jobs()
def load_cell(job):
 ch=Cell(V,job['held'],job['locations'])
 if job['held']:ch.contact_windows=windows(ch,job['station'],job['origin'])
 return ch
def check_load(ch,q,hands):
 maxratio=0;mingrip=1e30;cases=[]
 for force in hands['R']['check_forces_N']:
  for moment in hands['R']['check_moments_Nm']:
   _,rot=ch.pose(q)
   application_world=rot@np.array(hands['R']['work_offset_m'])
   arm_moment=np.array(moment)+np.cross(application_world,np.array(force))
   tq=ch.torque_multi(q,hands,{'R':force},{'R':arm_moment});gr=ch.grip_side(q,hands['R'],force,np.array(moment),'R');maxratio=max(maxratio,tq['ratio']);mingrip=min(mingrip,gr['margin']);cases.append(dict(torque=tq,grip=gr,force_N=force,moment_Nm=moment,equivalent_moment_at_R_work_Nm=arm_moment.tolist(),force_application_offset_prep_m=hands['R']['work_offset_m'],force_application=hands['R'].get('force_application','key_loading_point')))
 return maxratio,mingrip,cases
