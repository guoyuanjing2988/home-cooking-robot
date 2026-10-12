from rescue_cell import *
ROUTES={
 'carrot':['dock_carrot','wash_basin','process_cell','dock_carrot'],
 'potato':['dock_potato','wash_basin','process_cell','wash_basin','dock_potato'],
 'tomato':['dock_tomato','wash_basin','process_cell','dock_tomato'],
 'bok_choy':['dock_bok_choy','wash_basin','process_cell','wash_basin','process_cell','dock_bok_choy']}
def recipe(v):
 cfg=config(v);locations=initial_locations(cfg);events=[dict(id='E00',kind='initialise',action='Home, guards locked, raw food identity and mass checked')];transfers=[];statics=[];t=0
 for prod,route in ROUTES.items():
  obj='output_'+prod
  for seq,(src,dst) in enumerate(zip(route,route[1:])):
   t+=1;origin=list(locations[obj]);dest=initial_locations(cfg)[obj] if dst.startswith('dock_') else seats(cfg)[dst]
   tr=dict(id=f'T{t:02d}',kind='whole_pan_transfer',product=prod,object_id=obj,source=src,destination=dst,origin=origin,dest=dest,locations=copy.deepcopy(locations),required_paths=['empty_approach','key_descent','jaw_close','loaded_lift','loaded_transfer','seat','jaw_open','empty_retreat'],food_transformation=False)
   transfers.append(tr);events.append(tr)
   statics.append(dict(id=tr['id']+'_grasp',transfer=tr['id'],action='grasp',object_id=obj,station=src,origin=origin,locations=copy.deepcopy(locations)))
   statics.append(dict(id=tr['id']+'_release',transfer=tr['id'],action='release',object_id=obj,station=dst,origin=dest,locations=copy.deepcopy(locations)))
   locations[obj]=list(dest)
   if not dst.startswith('dock_'):
    if dst=='wash_basin':
     operation='raw_wash' if seq==0 else 'post_cut_starch_rinse' if prod=='potato' else 'separated_leaf_crease_wash'
     internal=['retain_pan','open_pan_lid','lift_insert','fresh_water_and_surface_brush','inspect_all_surfaces','lift_before_dirty_drain','fresh_rinse','drain','lower_insert','close_pan_lid','release_retention']
     if operation=='separated_leaf_crease_wash':internal[3:3]=['600s_cold_soak','every_leaf_2_to_5N_crease_rub_until_no_grit']
     if operation=='post_cut_starch_rinse':internal[3:3]=['three_fresh_2L_changes_until_no_white_swirl','30s_drain_no_puddle']
    else:
     operation='peel_trim_rinse_slice' if prod in ('carrot','potato') else 'core_and_eight_wedges' if prod=='tomato' else 'root_trim_and_separate_every_leaf' if seq==1 else 'split_wide_stalks_and_section'
     internal=['retain_pan','open_pan_lid','raise_supported_food_cradle','engage_retention','guarded_work_cycle','park_all_work_tools','inspect_finished_dimensions_and_all_scraps','lower_food_and_clean_insert','close_pan_lid','release_retention']
    events.append(dict(id=f'P{t:02d}',kind='appliance_cycle',product=prod,object_id=obj,station=dst,operation=operation,locations=copy.deepcopy(locations),internal_paths=internal,gate='All internal paths, physical retention and food transformations must pass before this event commits',status='unverified'))
 events.append(dict(id='E99',kind='finalise',action='Four separate finished bowls,>=98% edible transfer and person-safe output access'))
 return dict(events=events,transfers=transfers,statics=statics,supervisory_events=len(events),handling_strokes=len(statics),quality_rules_source='inputs/cook_ref.md',original_supervisory_events=79,old_expanded_obligations=530,scope='Repeated appliance strokes remain inside checked cycle programs; no necessary cut, rinse, eye, leaf or terminal recovery is deleted.')
def interface_spec(v):
 cfg=config(v)
 return dict(config=cfg,nominal_pan_external_m=[.265,.163,.100],approach='Vertical80mm above exposed top key then straight descent; no station pocket or robot insertion/pushing',open_dock_land_m=[.330,.245,.024],support_registry=Workcell(v).support_registry,key=dict(open_jaw_inner_gap_m=.110,closed_gap_m=.060,capacity_N=150,capacity_Nm=15,mu=.5,SF=1.5,nonjaw_contacts_allowed=False,owning_support='eoat_key_capture',complete_cup_relocated_m=[0,-.14,0]),wash=dict(station='wash_basin',water_charge_L=2,basin='360x280x100mm catch basin, fresh flow plus screened drain',opening='No cage above pan;330x245mm land',lid='Existing full pan hinge plus named powered opener and retention interface',pusher='None required for washing',retention='process/wash_retention_x shoe engages only its own named pan side face',robot_withdrawal='Arm must retreat before any lid/head motion',quality_feedback=['visible_dirt','surface_coverage','grit','white_starch_swirl','free_water'],unknowns=['brush/cradle coverage trajectory','water exchange and food retention proof']),process=dict(station='process_cell',opening='Exposed330x245mm pan land',blade_full_m=[.003,.140,.110],carriage_full_m=[.040,.180,.030],pusher_full_m=[.020,.080,.090],blade_down_m=.275,pusher_feed_m=.20,retention='Side clamp plus supported carrier required before any working force',guard='Module enclosure interlocked; complete rear blade guard and pan lid states tracked',dock='Own registered process_open_land top face',work_contact='Named food and its active tool face, exact axis and<=50mm local working windows only; no permission on park/retract',unknowns=['food cradle lift and retention','every peel/end/eye access path','continuous cut child/scrap geometry','blade clearance through insert','terminal recovery','leaf separation and individual rubbing','core-only removal and wedge damage']),safety=dict(one_package=True,household_feed_A=13,NC_water=True,gravity_axes='deenergise-to-apply brake plus mechanical parked catch',guarded_work=True,person_inside_while_running=False),preparation_acceptance=False)
