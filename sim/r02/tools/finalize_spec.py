"""Close site/mass/geometry handover details using the delivered CAD manifest."""
from pathlib import Path
import json, math, csv, copy
R=Path(__file__).resolve().parent
p=json.loads((R/'results/process_v2.json').read_text(encoding='utf-8'))
cad=json.loads((R/'cad/cad_manifest.json').read_text(encoding='utf-8'))
p['work_sites']['peel_food'][2]=.100
p['work_sites']['carrot_peel_surface']=[-.935,.170,.1175]
p['work_sites']['potato_peel_surface']=[-.935,.170,.1350]
p['work_sites']['tomato_core_surface']=[-.935,.170,.1550]
p['work_sites']['peel_handle'][2]=.165
p['work_sites']['catch_handle'][2]=.21
p['work_sites']['root_blade']=[.490,.290,.220]
p['work_sites']['wedge_blade']=[.400,.290,.110]
p['tools']['carried_bowl']['geometry'][0]['center_m']=[.135,0,0]
p['tools']['carried_bowl']['com_local_m']=[.12,0,0]
p['tools']['peeler']['geometry'][1]['size_m']=[.025,.076,.025]
p['tools']['root_food']=dict(mass_kg=0,com_local_m=[0,0,0],work_local_m=[0,0,0],grip='friction',geometry=[dict(name='held_root',type='ingredient_box_or_ellipsoid',center_m=[0,0,0],size_from_product=True)],actual_grip_normal_total_N=80,normal_source='M14 minimum40Nperjaw; root-only padded grip. Verify no root damage, otherwise use force-limited sprung fingers or a lower-force food interface; never command DH below its minimum.')
p['tools']['peel_bin']=dict(mass_kg=.55,com_local_m=[.0315,-.08,0],work_local_m=[0,0,0],grip='keyed',geometry=[dict(name='closed_bin_envelope',type='box',center_m=[.0315,-.08,0],size_m=[.047,.160,.280]),dict(name='key',type='box',center_m=[0,0,0],size_m=[.060,.028,.020])])
mass_updates={'colander':.80,'cut_cassette':.90,'food_cup':.30}
for tool,mass in mass_updates.items():p['tools'][tool]['mass_kg']=mass
p['tools']['food_cup'].update(com_local_m=[.06,0,.08],work_local_m=[.10,0,.15],geometry=[dict(name='cup_floor',type='box',center_m=[.10,0,.15],size_m=[.008,.09,.09]),dict(name='cup_offset_beam',type='box',center_m=[.01,0,.075],size_m=[.012,.02,.15]),dict(name='cup_key',type='box',center_m=[0,0,0],size_m=[.06,.028,.02])])
p['force_models']['drawer_insert'].update(nominal_N=7.7255,design_N=11.58825,derivation='mu_slide.5*loadedcassette1.1kg*g +1.1kg*.3m/s2 +2N latch spring; multiply1.5; CAD bare rootcassette.639kg plus key/retention/boughtfittings budgeted.90kg')
p['force_models']['handle_carry'].update(nominal_N=.30,design_N=.45,derivation='Maximumwetcolander1.0kg*acceleration.3m/s2; multiply1.5; gravity separate. Per-pose actualmass is used for carry vectors.')
p['tools']['bowl_bail']=copy.deepcopy(p['tools']['key_handle'])
p['tools']['bowl_bail'].update(mass_kg=.30,com_local_m=[.06,0,0],geometry=[dict(name='key',type='box',center_m=[0,0,0],size_m=[.06,.028,.02]),dict(name='bail_bar',type='box',center_m=[.01,0,0],size_m=[.012,.178,.012]),dict(name='leg1',type='box',center_m=[.065,-.083,0],size_m=[.09,.012,.012]),dict(name='leg2',type='box',center_m=[.065,.083,0],size_m=[.09,.012,.012])])
requirements={r['product']:r for r in p['finished_products']}
for phase in p['phases']:
    for seg in phase['segments']:
        for pose in seg['poses']:
            for side,h in pose.items():
                site=h['work_site']
                if h['held'] in mass_updates:
                    old={'colander':.70,'cut_cassette':.60,'food_cup':.18}[h['held']]
                    h['held_kg']=round(h['held_kg']+mass_updates[h['held']]-old,5)
                if site=='peel_food':h['pos'][2]+= .030
                if site=='peel_handle':h['pos'][2]+= .015
                if site=='catch_handle':h['pos'][2]+= .11
                if h['held'] in ['eye_core_spoon','wash_pad'] and site in ['peel_food','wash_supported']:
                    # These sites denote actual contact; R01 hand.pos is grasp.
                    h['pos'][2]+=p['tools'][h['held']]['work_local_m'][0]
                if phase['id']=='Q06' and h['held']=='eye_core_spoon':h['pos'][2]+=.035;h['work_site']='potato_peel_surface'
                if phase['id']=='Q22' and h['held']=='eye_core_spoon':h['pos'][2]+=.055;h['work_site']='tomato_core_surface'
                if h['held']=='food_cup' and site=='wash_supported':h['pos'][0]+=.15;h['pos'][2]+=.10;h['work_offset_m']=[.10,0,.15];h['mass_offset_m']=[.06,0,.08]
                if h['held']=='carried_bowl':h['mass_offset_m']=[.12,0,0]
                for g in p['tools'][h['held']]['geometry']:
                    if g['name']=='land_a' or g['name']=='land_b':pass
                h['intended']=list(h['intended'])
        if seg['interpolation'].startswith('Cartesian'):
            a,b=seg['poses']
            for side in set(a)&set(b):
                if seg['label'].startswith(('insert_','close_')):
                    # Reconcile120mm drawer stroke with the named closed-handle site.
                    a[side]['pos'][1]+=.04;b[side]['pos'][1]+=.04
    phase['timing']='All appliance contact/load phases occur with drive isolated, blade mechanically parked, door open. Powered phases begin only after arms withdraw and door closes.'
for item in p['counter_layout']:
    if item['id']=='peel_fixture':item['height_m']=.16;item['bounds_counter_m'][2]=[0,.16]
    if item['id']=='guarded_cutter':item['center_xy_m']=[.40,.285];item['full_footprint_m']=[.50,.55];item['bounds_counter_m']=[[.15,.65],[.01,.56],[0,.38]];item['geometry_reference_center_xy_m']=[.40,.30]
# Handled bowls use a detachable bail to avoid intersecting the feed tray/blade.
q09=next(a for a in p['phases'] if a['id']=='Q09')
bailpose=dict(pos=[.4,.11,.21],frame='counter',approach=[0,0,-1],jaw_axis=[0,1,0],roll_deg=0,held='bowl_bail',held_kg=.30,work_offset_m=[0,0,0],mass_offset_m=[.06,0,0],jaw_opening_m=.028,nominal_forces_N=[[0,0,0]],check_forces_N=[[0,0,0]],force_model_ids=[],intended=[],grip='keyed',work_site='catch_handle')
q09['segments'].append(dict(label='detach_bail_after_bowl_seated',station='catch_handle',poses=[{'R':bailpose},{'R':dict(bailpose,pos=[.4,.11,.34])}],jaw_axes=[[0,1,0]],interpolation='Lift130mm; place bail on covered front tool land while bowl remains seated',intended_contact_pairs=[]))
q09['tools'].append('bowl_bail')
q09['operations']+=' The bowl drawer is withdrawn to y=.11,bowl bottom z=.03, grasp z=.21. Detach the bail after seating; close bowl drawer with a fixed external key. No bail remains across the feed path during cutting. Reattach only after blade park and drawer withdrawal for unloading.'
for qid in ['Q11','Q12','Q20','Q25']:
    next(a for a in p['phases'] if a['id']==qid)['operations']+=' Before bowl lift, park blade, open door, withdraw bowl drawer and latch detachable bail. Latch insertion uses the sourced drawer spring/friction envelope; verify retention before lift.'
p['assembly_states']=dict(loading=dict(door='open',blade_lowest_z_m=.315,bowl_drawer_center_xy_m=[.40,.11],bowl_bottom_z_m=.03,bail='attached only for transport'),root_cut=dict(door='closed',blade_plane_x_m=.490,bowl_center_xy_m=[.40,.29],bail='removed',food_bottom_z_m=.145,root_chute_upper_z_m=.112,max_initial_drop_m=.033,requirement='adjust chute3mm upward so initial drop<=30mm; CAD below includes revised raise'),tomato_cut=dict(door='closed',wedge_grid_z_m=.110,catch_pad_z_m=.100,bail='removed',max_free_drop_m=.010),after_cut=dict(door='open only after blade park',bowl_drawer='withdraw before bail reattachment'))
chute_top=next(a['bounds_mm'][2][1]/1000 for a in cad['instances'] if a['name']=='CatchNest')
p['assembly_states']['root_cut']['root_chute_upper_z_m']=round(chute_top,6)
p['assembly_states']['root_cut']['max_initial_drop_m']=round(.145-chute_top,6)
p['assembly_states']['root_cut']['requirement']='Root chute raised5mm in delivered CAD; initialdrop29.54mm fromnativegeometry; maximumrootposturemustrecheckactualmatchedknife.'
# Force vectors separate process direction from gravity. Never subtract fixed-machine forces from robot loads.
p['force_application']=dict(world_counter_axes_identical=True,peel=dict(R_nominal_force_N=[-42,0,5],R_design_force_N=[-63,0,7.5],work_offset_m=[.065,0,0],fixture_reaction_N=[63,0,-7.5]),eye_core=dict(design_force_directions_counter=[[52.33,0,0],[-52.33,0,0],[0,52.33,0],[0,-52.33,0],[0,0,52.33]],tool_edge_offset_m=[.080,0,0],spoon_local_rotation_torque_design_Nm=.524),powered_cut=dict(appliance_force_on_food_N={k:[0,0,-v['design_N']] for k,v in p['force_models'].items() if k in ['carrot_cut','potato_cut','greens_cut','tomato_wedge']},robot_force_during_cut_N=[0,0,0],load_route='Equal/opposite blade and food-support forces close internally in fixed C-frame. Base/mount design nevertheless checks full1000N envelope; arms are mechanically detached.'),carry=dict(gravity='automatic mj_rne + held mass COM; do not add gravity twice',acceleration_screen_m_s2=.45,maximum_colander_plus_wet_food_kg=1.0),drawer=dict(design_force_directions_counter=[[0,-11.58825,0],[0,11.58825,0]],do_not_apply_vertical_insertion_force=True))
# Correct insertion, localized scoop and free carry direction cases at their physical work points.
for phase in p['phases']:
    for seg in phase['segments']:
        for pose in seg['poses']:
            for side,h in pose.items():
                ids=h['force_model_ids']
                if 'drawer_insert' in ids:
                    f=p['force_models']['drawer_insert'];h['nominal_forces_N']=[[0,-f['nominal_N'],0],[0,f['nominal_N'],0]];h['check_forces_N']=[[0,-f['design_N'],0],[0,f['design_N'],0]]
                if 'eye_core' in ids:
                    f=p['force_models']['eye_core'];h['nominal_forces_N']=[[f['nominal_N'],0,0],[-f['nominal_N'],0,0],[0,0,f['nominal_N']]];h['check_forces_N']=[[f['design_N'],0,0],[-f['design_N'],0,0],[0,0,f['design_N']]];h['nominal_moments_Nm']=[[.262,0,0]];h['check_moments_Nm']=[[.524,0,0]]
                if h['held_kg']>p['tools'][h['held']]['mass_kg']:
                    foodkg=round(h['held_kg']-p['tools'][h['held']]['mass_kg'],4)
                    candidates=phase['products']
                    h['held_food']=dict(mass_kg=foodkg,product_candidates=candidates,size_from_finished_product_input=True,geometry='explicit ingredient box/ellipsoid at the cup or cassette support, with full flesh envelope; not a mass-only object',max_envelope_m=[.17,.10,.07],attachment='supported cup/bowl; never add contact exemption for full gripper or fixture')
                if not ids:
                    # Every free carry has a mass-derived acceleration wrench, gravity separate.
                    f=h['held_kg']*.3;h['nominal_forces_N']=[[f,0,0],[-f,0,0],[0,f,0],[0,0,f]];h['check_forces_N']=[[1.5*f,0,0],[-1.5*f,0,0],[0,1.5*f,0],[0,0,1.5*f]];h['force_model_ids']=['handle_carry'];h['acceleration_force_derived_from_this_mass']=True
                h['path_constraints']=dict(approach_clearance_m=.10,travel_above_left_fixtures_z_m=.30,travel_above_cutter_z_m=.575,exact_fixture_registration='5mm/3deg arm gate remains; passive lead-in and encoder establish<=.2mm feed without tightening robot checker',do_not_claim_continuous_path_collision_pass=True)
                h['pos']=[round(v,6) for v in h['pos']]
# Replace guard front full block with the actual loading aperture primitives.
geoms=p['layout_geometry_primitives']
geoms[:]=[g for g in geoms if g['name']!='cell_guard_front']
for name,c,size in [('front_left',[.205,.18,.18],[.07,.004,.31]),('front_right',[.595,.18,.18],[.07,.004,.31]),('front_header',[.4,.18,.3225],[.32,.004,.025])]:
    geoms.append(dict(name=name,type='box',center_m=c,size_m=size,frame='counter',group='fixed_appliance_robot_part',mount_contact=False))
p['moving_geometry_states']=dict(front_doors=[dict(id='left_door',type='box',size_m=[.160,.004,.285],closed_center_m=[.32,.176,.1675],hinge_counter_m=[.24,.176,0],rotation_open_deg=-90,open_center_m=[.24,.096,.1675],sweep_bounds_m=[[.238,.402],[.014,.178],[.025,.310]],forbidden_to_robot=True),dict(id='right_door',type='box',size_m=[.160,.004,.285],closed_center_m=[.48,.176,.1675],hinge_counter_m=[.56,.176,0],rotation_open_deg=90,open_center_m=[.56,.096,.1675],sweep_bounds_m=[[.398,.562],[.014,.178],[.025,.310]],forbidden_to_robot=True)],drawer=dict(food_cassette_center_closed_m=[.40,.29,.132],food_cassette_center_open_m=[.40,.17,.132],stroke_m=.120,body_geometry='tools.cut_cassette plus actualfood',handles='must remain>=5mmfrompanel aperture boundaries'),warning='NativeCADshowsdoorleavesopen; libraryC12 includesclosedleaves. Sweepsareexplicitobstacles. Hinges/linkage/interlockandrunningdrivesstillrequirespecification; noaddedcontactexemption.')
p['powered_appliances'][0]['nominal_frame_mass_budget_kg']=14
p['tools']['colander']['wet_food_max_kg']=.20
p['arms']['L']['max_actual_held_kg']=.50
p['work_sites']['transit_right'][2]=.575
p['force_models']['end_cup_preload']=dict(nominal_N=10,design_N=15,margin_factor=1.5,derivation='Springtailstockk1000N/m*10mmcompression=10N;1.5factor. Oppositeaxialstopalsoevaluatedatpeeldrag63Nreaction.',source_ids=['physics:Hooke'],scope='internalfixturepreload; R clampactuationvia11.588Nhandleenvelope',limitations='Endcupscontactonlyfuture3–5mmtrimregion; foodindentationandsplinteringmustbechecked. Nofood-strengthproofinferredfromsteel/POMstrength.')
q03=next(a for a in p['phases'] if a['id']=='Q03')
q03['operations']='Two adjustable passive end cups at vegetable ends support a100mmhigh food axis. Diameter16mm cups touch only the3–5mmfuturetrimregion. Springtailstock10Nnominalpreload,15Nscreen; oppositepositiveaxialstop takes63Npeeldrag. Centre stays open for gripper. Carrotcentres+-80mm,potato+-45mm fromfixture centre; no rotating poweredlathe.'
q07=next(a for a in p['phases'] if a['id']=='Q07')
for seg in q07['segments']:
    for pose in seg['poses']:
        for h in pose.values():
            if seg['label']=='remove_closed_peel_bin':h.update(held='peel_bin',held_kg=.60,work_offset_m=[0,0,0],mass_offset_m=[.0315,-.08,0])
            if seg['label']=='wipe_dirty_support':h['pos'][2]-=.050
q07['tools']=['peel_bin','wash_pad']
q05=next(a for a in p['phases'] if a['id']=='Q05')
q05['operations']=q05['operations'].replace('fixture takes peel load','end cups and opposite axial stop take peel load')
# Root transport uses the normal gripper, not a cup trapped inside the end fixture.
for phase in p['phases']:
    if not any(f in ['carrot','potato'] for f in phase['products']):continue
    for seg in phase['segments']:
        for pose in seg['poses']:
            for side,h in pose.items():
                if h['held']=='food_cup':
                    food=h['held_kg']-.30;h['held']='root_food';h['held_kg']=round(food,4);h['grip']='friction';h['work_offset_m']=[0,0,0];h['mass_offset_m']=[0,0,0];h['jaw_opening_m']=.065;h['actual_normal_total_N']=80
    phase['tools']=sorted({h['held'] for s in phase['segments'] for pp in s['poses'] for h in pp.values()})
# Ingredient instances are explicit so a generic pose never substitutes for both surfaces.
p['checker_instances']=[]
for food in ['carrot','potato']:
    for qid in p['root_call_plan'][food]:
        inst=copy.deepcopy(next(q for q in p['phases'] if q['id']==qid));inst['instance_id']=qid+'.'+food;inst['products']=[food]
        for seg in inst['segments']:
            if qid=='Q12' and food not in seg['label']:continue
            for pose in seg['poses']:
                for side,h in pose.items():
                    if h['held']=='root_food':h['held_kg']=requirements[food]['input_mass_kg'];h['jaw_opening_m']=.035 if food=='carrot' else .065;h['held_food']=dict(product=food,mass_kg=h['held_kg'],size_counter_m=requirements[food]['input_size_m'],size_local_m=[requirements[food]['input_size_m'][2],requirements[food]['input_size_m'][1],requirements[food]['input_size_m'][0]],long_axis_counter=[1,0,0],center_local_m=[0,0,0],mass_accounting='held_kgalreadyincludesfood;collisiongeometrydoesnotaddgravitytwice')
                    if qid=='Q05' and h['held']=='peeler':h['pos'][2]=p['work_sites'][food+'_peel_surface'][2]+.065;h['work_site']=food+'_peel_surface'
        if qid=='Q05':
            for seg in inst['segments']:
                if seg['label']=='longitudinal_peel' and food=='potato':
                    for index,pose in enumerate(seg['poses']):pose['R']['pos'][0]=-.935+(-.03 if index==0 else .03)
                if seg['label']=='index_supported_root':
                    for pose in seg['poses']:
                        pose['R']=dict(pos=[-.935,.170,p['work_sites'][food+'_peel_surface'][2]+.145],frame='counter',approach=[0,0,-1],jaw_axis=[0,1,0],roll_deg=0,held='peeler',held_kg=.25,work_offset_m=[.065,0,0],mass_offset_m=[.025,0,0],jaw_opening_m=.028,nominal_forces_N=[[0,0,0]],check_forces_N=[[0,0,0]],force_model_ids=['handle_carry'],intended=[],grip='keyed',work_site='parked_peeler80mm_above_surface')
        if qid=='Q12':inst['segments']=[s for s in inst['segments'] if food in s['label']]
        if qid=='Q10':inst['appliance_action']['force_model_ids']=[food+'_cut'];inst['appliance_action']['terminal_case']=dict(remaining_length_m=.010,last_cut_feed_m=.005,final_uncut_edible_slice_m=.005,follower_plane_gap_m=.005)
        p['checker_instances'].append(inst)
for q in p['phases']:
    if q['id']=='Q01' or q['id']>='Q13':
        inst=copy.deepcopy(q);inst['instance_id']=q['id']
        if q['id']=='Q22':
            for seg in inst['segments']:
                for pose in seg['poses']:
                    if 'R' in pose:pose['R']['work_site']='tomato_core_surface'
        p['checker_instances'].append(inst)
p['checker_instances'].sort(key=lambda i:(0 if i['id']=='Q01' else 1 if i.get('instance_id','').endswith('.carrot') else 2 if i.get('instance_id','').endswith('.potato') else 3,int(i['id'][1:])))
p['checker_contract']['preferred_phase_source']=f"checker_instances:{len(p['checker_instances'])} expanded records with ingredient-specific surface poses;27 Q templates are logical process definitions."
p['cut_index_algorithm']=dict(root='GivenediblelengthL,n=round(L/5mm);require4<=L/n<=6mm;explicit10mmstubtestretained.',greens='Chooseintegernwithceil(L/50mm)<=n<=floor(L/30mm),nearestL/40mm. If intervalempty,finishedspeccannotmetbylengthcutswithoutedibleloss;rejectbatchorflagqualityfailure,neverhideashortterminalpieceastrimmass.',edible_yield='>=98%ofallcutediblemass,includingedibleterminalremainders; noautomaticshort-piecewasteexemption')
p['material_and_mass_closure']=dict(cad_bare_parts={c['id']:c['cad_mass_kg'] for c in cad['parts']},carried_payload_budgets_kg={'colander_dry':.80,'colander_wet_loaded':1.00,'cassette_dry':.90,'cassette_loaded':1.10,'bowl_dry':.52,'bowl_max_loaded':.72,'food_cup_dry':.30,'food_cup_loaded':.50},cad_mass_limitations='Massbudgetsincludeallboughtparts/fasteners and retention not present inconceptCAD; noarbitrarysubtraction tofitpayload.')
p['cad']=dict(manifest='cad/cad_manifest.json',custom_part_designs=18,assemblies=['cad/custom_parts.FCStd','cad/counter_layout.FCStd'],design_stage='concept valid solids and STEP; release blanks explicitly flagged',mass_vs_budget='CAD volumes for barecustomparts; toolmasses includeunknownfasteners/retention/boughtpieces,conservativebudgets,not scale measurements')
p['checker_contract']['additional_real_hardware_check']='DH PGC14050 datasheet moment7Nm is a separate limit. Preserve checker150N/15Nm key proof targets; do notclaimcompleteEOAT15Nm proof from7Nmgripper. AllactualwrenchesmustalsofitOEMgripperloads; strongerEOATorwristloadbypassrequiredifproofscopeincludesgripper.'
p['food_grip_control']=dict(checker_mu=.5,checker_normal_total_N=150,real_food_operation='cradle-supported softfood, min squeeze. Loose0.1kggreens need SF1.5*.1g/.5=2.943N totalnormal. Use<=5N calibratedtotalfoodpadnormal and bottomsupport; ifslip, support/regrasp,notincreaseforce.',tomato='Bottom-support cup; nofruitfrictionloadcredited; padnormal1Nnominal and1.5Ndesign. Exact bruise threshold still must be measured.')
q02=next(q for q in p['phases'] if q['id']=='Q02');q02['operations']+=' During the brush stroke the root is parked in the sink insert and R releases/withdraws; the support takes brush reaction. R regrips only for supported orientation changes.'
q16=next(q for q in p['phases'] if q['id']=='Q16')
q16['operations']+=' Cup handle is150mm toside and100mm above floor so R does not occupy L brush approach. Opposite3Nbrush reaction is included on R if cup is lifted; use sink-supported cup where possible.'
for phase in p['phases']+p['checker_instances']:
    for seg in phase['segments']:
        for pose in seg['poses']:
            for side,h in pose.items():
                if h['force_model_ids']==['handle_carry']:
                    f=h['held_kg']*.3;h['nominal_forces_N']=[[f,0,0],[-f,0,0],[0,f,0],[0,0,f]];h['check_forces_N']=[[1.5*f,0,0],[-1.5*f,0,0],[0,1.5*f,0],[0,0,1.5*f]]
                if h['held']=='food_cup':
                    h['work_offset_m']=[.10,0,.15];h['mass_offset_m']=[.06,0,.08]
                    if h['work_site']!='wash_supported':h['pos'][0]+=.15
        if phase['id']=='Q15':
            for pose in seg['poses']:
                side=next(iter(pose));pose[side]['pos'][0]=-.46+.15 if side=='R' else -.34+.15
        if phase['id']=='Q16' and seg['label']=='rub_crease':
            for pose in seg['poses']:
                # True simultaneous support and brushing; skin/basecontact is above cupfloor.
                pose['L']['pos'][0]=-.40;pose['L']['pos'][2]+=.015
                pose['R']=dict(pos=[-.25,.30,.055],frame='counter',approach=[0,0,-1],jaw_axis=[0,1,0],roll_deg=0,held='food_cup',held_kg=.40,work_offset_m=[.10,0,.15],mass_offset_m=[.06,0,.08],jaw_opening_m=.028,nominal_forces_N=[[0,0,-2]],check_forces_N=[[0,0,-3]],force_model_ids=['leaf_rub'],intended=[],grip='keyed',work_site='wash_supported')
        if phase['id']=='Q21' and seg['label']=='wipe_tomato_skin':
            for pose in seg['poses']:
                pose['L']['pos'][0]=-.40;pose['L']['pos'][2]+=.060
                pose['R']=dict(pos=[-.25,.30,.055],frame='counter',approach=[0,0,-1],jaw_axis=[0,1,0],roll_deg=0,held='food_cup',held_kg=.45,work_offset_m=[.10,0,.15],mass_offset_m=[.06,0,.08],jaw_opening_m=.028,nominal_forces_N=[[0,0,-1]],check_forces_N=[[0,0,-1.5]],force_model_ids=['tomato_rub'],intended=[],grip='keyed',work_site='wash_supported')
# CAD-matched collision primitives in the R01 tool frame at a downward grasp.
# C04 CAD datum is bowl bottom; grasp=(0,0,180)mm. Local+X=-CAD Z,
# local+Y=-CAD Y, local+Z=-CAD X. No collision exemption is introduced.
bail_geometry=[dict(name='key',type='box',center_m=[0,0,0],size_m=[.020,.028,.060]),dict(name='bail_bridge',type='box',center_m=[.006,0,0],size_m=[.012,.012,.178])]
for sign in [-1,1]:
    bail_geometry.append(dict(name='bail_leg'+str(sign),type='box',center_m=[.0455,0,sign*.083],size_m=[.091,.012,.012]))
    bail_geometry.append(dict(name='collar_tab'+str(sign),type='box',center_m=[.093,0,sign*.0905],size_m=[.006,.012,.027]))
p['tools']['bowl_bail']['geometry']=copy.deepcopy(bail_geometry)
p['tools']['bowl_bail']['geometry'].append(dict(name='collar',type='cylinder_shell',center_m=[.094,0,0],radius_m=.104,height_m=.008,thickness_m=.003,axis_local=[1,0,0]))
p['tools']['carried_bowl']['geometry']=[p['tools']['carried_bowl']['geometry'][0]]+copy.deepcopy(p['tools']['bowl_bail']['geometry'])
p['collision_geometry_source']=dict(preferred='Delivered FreeCAD solids/STEP transformed by documented CAD/tool datums; primitive records are alternative conservative collision proxies.',cad_to_tool_bail=dict(cad_grasp_mm=[0,0,180],tool_x_in_cad=[0,0,-1],tool_y_in_cad=[0,-1,0],tool_z_in_cad=[-1,0,0]),state='All food and gripper geometry must be instantiated; primitive proxies do not waive missing vendor gripper geometry.')
geoms[:]=[g for g in geoms if not g['name'].startswith('peel_fixture_')]
geoms.extend([dict(name='peel_fixture_tray',type='box',center_m=[-.935,.17,.0485],size_m=[.31,.27,.003],frame='counter',group='environment_fixture',mount_contact=False)])
for sign in [-1,1]:
    geoms.append(dict(name='peel_endpost'+str(sign),type='box',center_m=[-.935+sign*.098,.17,.0765],size_m=[.016,.024,.053],frame='counter',group='environment_fixture',mount_contact=False))
    geoms.append(dict(name='peel_endcup'+str(sign),type='cylinder',center_m=[-.935+sign*.090,.17,.100],radius_m=.008,height_m=.020,axis_counter=[1,0,0],frame='counter',group='environment_fixture',mount_contact=False))
for g in geoms:
    if g['name']=='cell_base':g['center_m'][2]=.0135;g['size_m'][2]=.003
    if g['name'] in ['cell_left_post','cell_right_post']:g['center_m'][2]=.180
# Logical support surfaces retain existing contact semantics, never whole-fixture permission.
p['contact_mapping']=dict(board_clamp='food contact at two16mmendcupfaces/positiveaxialstop only',cutting_board='actual slottedtray cleaning surface only',rinse_basket_bottom='actual C06food/support surface',knife_dock='covered cartridge bottom lands only',catch_dock='bowl floor lands only',new_exemptions=[])
p['force_models']['machine_index']=dict(nominal_N=5.7255,design_N=8.58825,margin_factor=1.5,derivation='mu_slide.5*loadedmovingtray1.1kg*g +1.1kg*.3m/s2; multiply1.5. Feed pauses during blade engagement; no cutting side force credited to index motor.',source_ids=['physics:Coulomb','physics:Newton'],scope='internalapplianceindexdrive, equaloppositehorizontalreactiontocountermount',limitations='Wetfrictionandtraymass assumptions; friction/encoderandcut-interlock testsrequired.')
for phase in p['phases']+p['checker_instances']:
    if phase['id']=='Q03':
        for seg in phase['segments']:
            if seg['label']=='support_root':
                for pose in seg['poses']:
                    for h in pose.values():h['intended']=['board_clamp']
    if phase['id']=='Q07':phase['operations']=phase['operations'].replace('V-support','end-cup tray')
    if phase['id']=='Q02':phase['operations']=q02['operations']
    if phase['id']=='Q16':phase['operations']=q16['operations']
    if phase['id']=='Q18':
        phase['operations']+=' Delivered comb has15mmwallpitch and3mmwallthickness:12mmclearspan. Set stripwidth<=12mm before slotloading, which satisfiesfinishedstalkwidth<=15mm. Do notforce15mmstalk into12mmslot.'
    if phase.get('appliance_action') and phase['id']!='Q24':
        phase['appliance_action']['index_force_model_id']='machine_index'
        phase['appliance_action']['index_reaction_counter_N']=[8.58825,0,0]
    for seg in phase['segments']:
        for pose in seg['poses']:
            for h in pose.values():
                if h['held']=='food_cup' and h['work_site']=='cutter_load':
                    # Front-pointing cup handle avoids the right opened door.
                    # This is an approach/withdrawal datum, not a claim that fruit
                    # can be released unsupported across the remaining height.
                    above=round(h['pos'][2]-.16,6)
                    h['pos']=[.40,.14,round(.28+above,6)];h['jaw_axis']=[1,0,0]
                    h['food_handoff']=dict(cup_floor_counter_m=[.40,.29,.18],requirement='Cassette loading support must meet food before cup withdrawal; no unsupported70mm tomato drop. Loading support stroke/datum is a hardware qualification gate.',status='concept loading approach; complete continuous placement path must be solved against measured cartridge')
(R/'results/process_v2.json').write_text(json.dumps(p,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
# Quantitative engineering comparisons accompany the score table.
options=json.loads((R/'results/options_scores.json').read_text(encoding='utf-8'))
for o in options['options']:
    step=o['step'];kind=o['strategy']
    if step=='peel':metrics=(63 if kind=='adapt' else 10,'surface tracking<=.5mm depth; fixture index45deg' if kind=='adapt' else 'loadpose5mm/3deg', '8–12 indexed orientations;2–3 strokes perface' if kind=='adapt' else '2–4 grasps plus end/eye touchup')
    elif step.startswith('cut'):metrics=(0 if kind in ['buy','build'] or step=='cut_tomato' and kind=='adapt' else 183,'cellfeed<=.2mm; armloading5mm/3deg','3–5 handlegrasps percartridgebatch; poweredcutsnobarefoodgrasps' if kind=='build' or step=='cut_tomato' and kind=='adapt' else 'manualmandoline/knife repeatedfeeds; terminalregrasp')
    elif step=='wash':metrics=(9,'supportedpad±5mm; visualcreaseinspection','2grasp/leaf forbasalrub;1root plus4–8supportedturns')
    elif step=='hold':metrics=(0,'positivefoodcup/stop;gripmu.5','1–2grasp pertransfer; rootindex8–12regrasps')
    elif step=='transfer' or step=='deliver':metrics=(11.58825,'handle5mm/3deg; noediblepieceteleport','2grasps perbowllift/park;wholecontainer')
    elif step=='dispose_peel':metrics=(.3,'gravitybin;handle5mm/3deg','1coveredbinlift and1park perroot')
    else:metrics=(11.58825,'keyregistration3mm/1deg inheritedproofdatum','toolpick+return2grasps; wristmanualduringmaintenanceonly')
    o.update(robot_design_force_envelope_N=metrics[0],precision=metrics[1],grasps_regrasps_estimate=metrics[2],metric_status='engineering comparison;poweredarm0Nexcludesgravityandloading;unselectedmanual183Nrootwidthscreennotmeasurement')
    if o.get('cny_cost')==7800:o['cny_cost']=8100
(R/'results/options_scores.json').write_text(json.dumps(options,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'results/options_scores.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(options['options'][0]));w.writeheader();w.writerows(options['options'])
print('FINALIZE_DONE')
