"""Independent transport, structure, power, timing and immutable-checker audit."""
import os,sys,json,copy,hashlib,difflib,ast,math,itertools,time
sys.dont_write_bytecode=True
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
from pathlib import Path
import numpy as np,mujoco
import xml.etree.ElementTree as ET
import model,adapter
H=model.HERE;ROOT=model.ROOT;O=H/'results';A=H/'audit';R=H/'renders'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
def config(cid='c0684'):return next(x['config'] for x in json.loads((O/'configs.json').read_text()) if x['id']==cid)

def audit():
    src=(ROOT/'sim/r01/concept/checker.py').read_text();ref=(H/'reference.py').read_text()
    (A/'reference.diff').write_text(''.join(difflib.unified_diff(src.splitlines(True),ref.splitlines(True),fromfile='r01/checker.py',tofile='r02/reference.py')))
    (A/'adapter.diff').write_text(''.join(difflib.unified_diff(src.splitlines(True),(H/'adapter.py').read_text().splitlines(True),fromfile='r01/checker.py',tofile='r02/adapter.py')))
    (A/'model.diff').write_text(''.join(difflib.unified_diff((ROOT/'sim/r01/concept/model.py').read_text().splitlines(True),(H/'model.py').read_text().splitlines(True),fromfile='r01/model.py',tofile='r02/model.py')))
    before=json.dumps(model.P['checker_instances'],indent=2).splitlines(True);after=json.dumps(adapter.process_instances(),indent=2).splitlines(True)
    (A/'phase_contract.diff').write_text(''.join(difflib.unified_diff(before,after,fromfile='process_v2/checker_instances',tofile='worldframe/instance_definitions')))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    inputs=['inputs/prep_checker.py','inputs/mandoline_golden.py','inputs/cook_ref.md','inputs/keypose_cook.md','inputs/t08_review_phases_layout.md','prompts/r02/common.md','posts/r01/concept.md','posts/r01/market.md','posts/r02/transport.md','posts/r02/tools.md','sim/r02/tools/results/process_v2.json','sim/r02/transport/results/transport_options.json','sim/r01/concept/checker.py','sim/r01/concept/model.py']
    functions=['forbidden','solve','bind_model','grip','target_rotation']
    def fn(txt,name):
        root=ast.parse(txt);cls=next(n for n in root.body if isinstance(n,ast.ClassDef) and n.name=='Checker');return ast.dump(next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
    write(A/'checker_contract.json',dict(reference_identical=src==ref,reference_hash=sha(H/'reference.py'),unchanged_core_AST={n:fn(src,n)==fn(ref,n) for n in functions},inputs={n:sha(ROOT/n) for n in inputs},tolerances=dict(position_mm=5,angle_deg=3,robot_environment_mm=10,gripper_held_mm=5,mu=.5,SF=1.5,normal_sum_N=150,key_force_N=150,key_moment_Nm=15,padding=0),new_ACM_pairs=[],new_contact_exemptions=[],differences=['Robot/model selection and explicit new geometry are in model.py','Phase source becomes36 process_v2 checker_instances, counter+0.85m conversion','Four-side taxonomy uses identical original gap thresholds','Frozen carriage X/Z/lane and parked unused joints','L-only and simultaneous hand loads: sum Jtransposed F and COM gravity for each hand','Grip equations use each active hand site with same constants','Existing intended-work surfaces are relocated by exact contact mapping','Door open/closed state at actual phase boundary; no whole guard contact permission','Long robot beam geometry becomes exact union of touching boxes; unchanged physical envelope'],missing_inputs=['posts/r01/reviewer.md','transport power-track addendum'],limitations=['Public torque values are reference diagnostics, not certified continuous output','R01 gripper is a1.2kg design proxy, not complete vendor PGC hardware geometry','No continuous path or quality simulation admitted']))
    # Explicit source-model file hashes; generated copies never modify these.
    files=[ROOT/'sim/r01/concept/models/xarm6.xml',ROOT/'sim/r01/concept/models/aubo_i5.xml',ROOT/'sim/r01/concept/sources/menagerie/universal_robots_ur5e/ur5e.xml',ROOT/'sim/r01/concept/sources/menagerie/ufactory_xarm7/xarm7.xml',ROOT/'sim/r01/concept/sources/menagerie/franka_fr3/fr3.xml']
    write(A/'source_models.json',{str(p.relative_to(ROOT)):sha(p) for p in files})
    data=json.loads((A/'checker_contract.json').read_text());data['differences'] += ['Inherited indexed rinse_basket workface expansion retained, rather than overwritten by literal names','World-frame supplied free moments: angular Jacobian and same keyed-grip moment rule','C06 held circular shorthand resolved to delivered CAD rectangular shell with retained mass/COM/key interface','Saved seed poses rechecked after these plumbing corrections;no new IK optimization or acceptance relaxation']
    write(A/'checker_contract.json',data)

def power_timing():
    sources=[dict(id='P01',url='https://docs.xarm.ufactory.cc/8.technical_specifications.html',facts='xArm typical200W;500W supply recommended;24V20.8A;AC controller100-240V;DC controller24-72V input and672Wmax output. A measured transient arm peak is not published.'),dict(id='P02',url='https://docs.supportarticle.ufactory.cc/support_articles/hardware/bend-radius-for-communication-and-power-cable.html',facts='xArm power10.4mm/radius78mm;data6mm/radius45mm;5 million cycles'),dict(id='P03',url='https://www.universal-robots.com/manuals/EN/TechSheets/UR5e_techsheet_pdf_online/UR5e_techsheet_en.pdf',facts='UR5e moderate200W, maximum570W,5kg,850mm,any-orientation,May2025'),dict(id='P04',url='https://eubiq.com/wp-content/uploads/2020/09/Eubiq-Catalog-2020-E-Size.pdf',facts='Aluminium/copper household power track;70x28mm section;13A250V British plug; adapters are stationary outlets'),dict(id='P05',url='https://www.eubiq-europe.com/Files/102724/E-Genesis-Power-Track-User-Guide-LR.pdf',facts='32A maximum track family is not blanket13A adapter approval'),dict(id='F01',url='https://iseki-food-ejournal.com/article/69/pdf',facts='Singh etal.2016 peaks at20/30/40mm per MINUTE, not per second. Width-scaling forces from process_v2 retain2x margin.'),dict(id='F02',url='https://www.qikan.com.cn/article/5dd020251220.html',facts='Peeling1.68N/mm inherited abstract;25mm engaged ribbon ->42N;1.5x=63N;not independent potato measurement')]
    write(O/'sources.json',sources)
    write(O/'power.json',dict(best_moving_power='one independent cable carrier per lane;fixed OEM AC controllers,dry;24V OEM arm lead in chain',wireless_safety=False,batteries=0,sink_side_preference='48V SELV for cutter/tools and switching-controller alternative;OEM24V arm supply on retained cable',per_arm=[dict(side=s,model='xArm6',typical_W=200,peak_W=None,peak_status='No measured peak in inspected OEM datasheet',recommended_supply_W=500,output_interface_limit_W=24*20.8,source='P01') for s in ('R','L')],nominal_arm_total_W=400,arm_supply_total_W=1000,EOAT_and_rail_allowance_per_arm_W=100,allowance_status='engineering budget,not OEM average/peak',tool_cutter_supply_W=150,supply_design_total_W=1350,design_current_at230V_A=1350/230,track_feed_limit_A=13,track_feed_power_at230V_W=2990,track_envelope_m=dict(section=[.070,.028],adapter_diameter_depth=[.067,.043],segments_x=[[-1.77,-.72],[-.10,.66]],center_y_z=[.566,1.125]),track_use='appliance/tool outlets; no arm sliding contact through a household adapter',alternative_48V_per_arm=dict(controller_output_ceiling_W=672,converter_efficiency_assumed=.9,current_A=672/(48*.9),recommended_collector_design_A=20,power_loss='SS1 thenSTO andspring brakes;dropout bridging andcontact continuity unqualified'),dock_and_charge='rejected:no batteries allowed',source_ids=['P01','P02','P03','P04','P05']))
    # One reference specimen of each ingredient, as cook_ref (no meal quantities supplied).
    durations={'Q01':45,'Q02.carrot':45,'Q03.carrot':25,'Q04.carrot':15,'Q05.carrot':90,'Q07.carrot':45,'Q08.carrot':30,'Q09.carrot':60,'Q10.carrot':32*(35/(40/60)+35/10+2+1),'Q12.carrot':30,
    'Q02.potato':45,'Q03.potato':25,'Q04.potato':15,'Q05.potato':96,'Q06.potato':40,'Q07.potato':45,'Q08.potato':30,'Q09.potato':60,'Q10.potato':18*(70/(40/60)+70/10+2+1),'Q11.potato':115,'Q12.potato':30,
    'Q13':35,'Q14':70/(40/60)+70/10+30,'Q15':45,'Q16':90,'Q17':30,'Q18':30/(40/60)+30/10+25,'Q19':4*(30/(40/60)+30/10+3)+30,'Q20':30,'Q21':45,'Q22':30,'Q23':60,'Q24':60/(40/60)+60/10+20,'Q25':30,'Q26':120,'Q27':180}
    # Explicit list schedule: prepare next ingredients while the detached cutter
    # runs; never load an occupied machine or use the same arms/sink twice.
    events=[];arm=0.;machine=0.
    def arms(ids,earliest=0):
        nonlocal arm
        arm=max(arm,earliest)
        for pid in ids:
            end=arm+durations[pid];events.append(dict(id=pid,start_s=arm,end_s=end,resource='arms/station',duration_s=durations[pid]));arm=end
        return arm
    def cut(pid,earliest=0,block_arms=False):
        nonlocal machine,arm
        start=max(machine,earliest);machine=start+durations[pid]
        events.append(dict(id=pid,start_s=start,end_s=machine,resource='fixedcutter;setupthenarmswithdrawn' if block_arms else 'fixedcutter;armswithdrawn',duration_s=durations[pid]))
        if block_arms:arm=max(arm,machine)
        return machine
    arms(['Q01','Q02.carrot','Q03.carrot','Q04.carrot','Q05.carrot','Q07.carrot','Q08.carrot','Q09.carrot'])
    carrot_end=cut('Q10.carrot',arm)
    arms(['Q02.potato','Q03.potato','Q04.potato','Q05.potato','Q06.potato','Q07.potato','Q08.potato','Q13','Q21','Q22'])
    arms(['Q12.carrot'],carrot_end);arms(['Q09.potato'])
    potato_end=cut('Q10.potato',arm)
    arms(['Q11.potato','Q12.potato'],potato_end)
    cut('Q14',arm,True);arms(['Q15','Q16','Q17'])
    cut('Q18',arm,True);cut('Q19',arm,True);arms(['Q20','Q23'])
    tomato_end=cut('Q24',arm);arms(['Q25','Q26','Q27'],tomato_end)
    events.sort(key=lambda e:(e['start_s'],e['id']))
    assert len(events)==36 and {e['id'] for e in events}=={p['id'] for p in adapter.process_instances()}
    write(O/'timeline.json',dict(status='PLANNING_ONLY;NO_EXECUTABLE_TIMELINE_BECAUSE_PHASE_CHAIN_FAILS',reference_meal='one160mm/.12kg carrot,one90mm/.20kg potato,one170mm/.10kg bokchoy,one70mm/.15kg tomato',validated_total_prep_time_s=None,validated_parallel_wash_cut=False,resource_schedule_can_overlap_in_principle=True,planning_serial_s=sum(durations.values()),planning_makespan_s=max(e['end_s'] for e in events),events=events,assumptions=['40mm/min engaged blade speed,the upper edge of the cited cutting study;do not claim20-60mm/s at these forces','10mm/s unloaded blade return;3s settle/index perrootcut','Carrot30edible slices plus2endtrims;potato16edible slices plus2trim/facet cuts;greensroottrim,widthsplit,4sectioncuts;tomatoone8-wedge stroke','Peel/rinse/inspection durations are engineering estimates with visible-quality endpoint;not measured','Washing/peeling next ingredient can overlap detached poweredcut;shared sink andtoolcleaning are serial','Armcarriage reposition/load times included in phase allowances;no verified trajectorytime','Faster commercial cutter may reducehours but needs its ownforce-speed-quality evidence'],slow_cut_total_s=sum(v for k,v in durations.items() if k in ('Q10.carrot','Q10.potato','Q14','Q18','Q19','Q24'))))

def mounting():
    # Whole-body worst-case envelope is deliberately broader than exact vendor COM.
    g=9.81;marm=12.5;meo=1.2;mpay=3.;mc=8.7;reach=.7;dy=1.5
    maxforce=max(np.linalg.norm(v) for q in model.P['checker_instances'] for s in q['segments'] for hands in s['poses'] for hd in hands.values() for v in hd['check_forces_N'])
    maxmoment=max(np.linalg.norm(v) for q in model.P['checker_instances'] for s in q['segments'] for hands in s['poses'] for hd in hands.values() for v in hd.get('check_moments_Nm',[[0,0,0]]))
    fg=(marm+meo+mpay+mc)*g;moment=(marm+meo+mpay)*g*reach+mc*g*.225+maxforce*reach+maxmoment
    F=dy*(fg+maxforce);M=dy*moment
    guide=F/4+M/(2*.34)+2*M/(2*.24)
    wallF=2*F+2*51.16944*g+18*g
    wallM=sum(M+F*abs(.6-y)+51.16944*g*abs(.6-(y+.225)) for y in (.12,-.40))+18*g*.7
    write(O/'loads.json',dict(status='CONSERVATIVE_SIZING_NOT_STRUCTURAL_RELEASE',per_carriage=dict(arm_kg=marm,EOAT_kg=meo,tool_payload_kg=mpay,transport_kg=mc,body_mass_treatment='all arm mass atfull700mm reach',max_new_arm_process_force_N=float(maxforce),static_gravity_N=fg,static_resultant_force_bound_N=fg+maxforce,static_moment_bound_Nm=moment,dynamic_factor=dy,factored_force_bound_N=F,factored_moment_bound_Nm=M,drive_force_bound_N=dy*((marm+meo+mpay+mc)*1+63+15),drive_drag_allowance_N=15,accel_m_s2=1),guide=dict(block='HGH25HA',block_C0_N=69070,block_reaction_bound_N=guide,required_static_safety=3,available_C0_div3_N=69070/3,selected_transport_envelope_N=900,selected_transport_moment_each_axis_Nm=650),wall=dict(two_lane_vertical_force_bound_N=wallF,two_lane_moment_bound_Nm=wallM,beam_mass_per_lane_kg=51.16944,support_x_m=[-1.80,1.04],net_wrench_is_not_anchor_distribution=True),fixed_appliance=dict(internal_design_thrust_N=1000,max_process_force_N=636.3651,frame_mass_budget_kg=14,vertical_operating_base_net_N=14*g+1*.45,one_foot_conservative_thrust_N=1000,bridge_offset_m=.2,bridge_internal_moment_bound_Nm=200,arm_cut_reaction_N=0,load_route='opposed blade/support reactions close internally;model1000Nstructural load even thoughnetstaticbase reaction ismostlyweight',no_rail_cut_load_transfer=True),brake=dict(candidate='MikiBXR05010LE',spring_applied=True,holding_N=3.2*10*.8/.02,carriage_translational_energy_J=.5*(marm+meo+mpay+mc)*.2**2,engagement_delay_s=.060,engagement_travel_m=.012,controlled_stop_distance_at1m_s2_m=.02,reserved_m=.05,rotor_inertia_and_certified_stop_validation='unclosed'),sources=['transport_options.json:HGH25HA,BXR,steelbeam','process_v2.json:peel/eye-forcephysicsandliterature','P01:xArm6massandreach'],limitations=['No bracket/anchor sharing or FEA certificate','Spring-loaded OEMarm brake mechanism not confirmed','Bearing/beam screening does not closeposecompliance','Per-carriagebound combines incompatible directions conservatively;not an observed workingload']))

def layout_audit():
    """Extra stationary-machine/mount audit; never modifies the phase checker."""
    tree,meta=model.build(config());m=mujoco.MjModel.from_xml_string(ET.tostring(tree.getroot(),encoding='unicode'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
    machine=[m.geom(a['name']).id for a in model.P['layout_geometry_primitives'] if a['name'].startswith(('cell_','front_','covered_tool_support'))]
    hardware=[m.geom(n).id for n in meta['infrastructure_names'] if not n.startswith(('R_','L_'))]
    env=[i for i in range(m.ngeom) if m.geom(i).name in ('north_wall','counter_left','counter_right','faucet_pipe','faucet_spout','faucet_base') or m.geom(i).name.startswith(('upper_cabinet_','cabinet_door_sweep_','outlet_access_'))]
    rows=[];mounts=[]
    for a in machine+hardware:
        for b in env:
            na,nb=m.geom(a).name,m.geom(b).name
            if na.startswith('cell_mount_') and nb=='counter_right':mounts.append([na,nb]);continue
            if na.startswith('wall_mount_') and nb=='north_wall':mounts.append([na,nb]);continue
            dist=float(mujoco.mj_geomDistance(m,d,a,b,.05,None))
            row=dict(pair=[na,nb],mujoco_gap_mm=dist*1000,required_mm=10,mujoco_clear=dist>=.01-1e-6)
            # Independent exact AABB distance only when both boxes are aligned;
            # this is numerical diagnosis, not a substitute acceptance rule.
            if m.geom_type[a]==mujoco.mjtGeom.mjGEOM_BOX and m.geom_type[b]==mujoco.mjtGeom.mjGEOM_BOX and np.allclose(d.geom_xmat[a],np.eye(3).ravel()) and np.allclose(d.geom_xmat[b],np.eye(3).ravel()):
                gaps=np.abs(d.geom_xpos[a]-d.geom_xpos[b])-m.geom_size[a]-m.geom_size[b]
                signed=float(np.linalg.norm(np.maximum(gaps,0))) if np.any(gaps>0) else float(max(gaps))
                row['exact_box_gap_mm']=signed*1000
            rows.append(row)
    write(O/'layout_audit.json',dict(status='SUPPLEMENTARY_LITERAL_GATE;NO_WAIVERS',pairs=rows,designated_mount_pairs=mounts,all_literal_pairs_clear=all(r['mujoco_clear'] for r in rows),minimum_exact_box_gap_mm=min(r['exact_box_gap_mm'] for r in rows if 'exact_box_gap_mm' in r),tool_bowls_trays_on_counter='kitchenware rests on its support;not a rail-environment exemption',door_access_model='full cabinet swing volume retained for transport;camera hides overlay only'))

def option_models():
    for cid in ('c0684','c0756','c0828','c0900','c1116','c0673','c0042'):
        c=config(cid);tree,meta=model.build(c)
        # Compilation verifies all referenced source meshes/joint definitions.
        m=mujoco.MjModel.from_xml_string(ET.tostring(tree.getroot(),encoding='unicode'))
        tree.write(H/'models'/f'{cid}_{c["transport"]}.xml',encoding='unicode')
        write(H/'models'/f'{cid}.json',dict(config=c,meta=meta,nq=m.nq,ngeom=m.ngeom,status='compiled_candidate;defaultpose_not_an_admission'))

def export(ch,q,label,status,focus=None):
    m,d=ch.m,ch.d;d.qpos[:]=q;mujoco.mj_forward(m,d);meshes={};geoms=[]
    for g in range(m.ngeom):
        n=m.geom(g).name
        if n in ('south_wall','south_cabinets') or n.startswith(('cabinet_door_sweep','outlet_access')):continue
        typ=int(m.geom_type[g]);a=dict(name=n,type=typ,size=m.geom_size[g].tolist(),pos=d.geom_xpos[g].tolist(),rot=d.geom_xmat[g].reshape(3,3).tolist(),rgba=m.geom_rgba[g].tolist())
        if m.geom_matid[g]>=0:a['rgba']=m.mat_rgba[m.geom_matid[g]].tolist()
        if typ==7:
            i=int(m.geom_dataid[g]);a['mesh']=str(i)
            if str(i) not in meshes:
                va,fa=m.mesh_vertadr[i],m.mesh_faceadr[i];meshes[str(i)]=dict(vertices=m.mesh_vert[va:va+m.mesh_vertnum[i]].tolist(),faces=m.mesh_face[fa:fa+m.mesh_facenum[i]].tolist())
        geoms.append(a)
    write(R/(label+'.scene.json'),dict(config=config(),label=label,status=status,focus=focus,geoms=geoms,meshes=meshes))

def transport():
    c=config();definition=dict(id='PARK',name='empty transport',products=['all']);hd=dict(pos=[0,.1,1.1],approach=[0,0,-1],jaw_axis=[0,1,0],roll_deg=0,held='key_handle',held_kg=.15,work_offset_m=[0,0,0],mass_offset_m=[.005,0,0],jaw_opening_m=.02,nominal_forces_N=[[0,0,0]],check_forces_N=[[0,0,0]],intended=[],grip='keyed',work_site='inspection')
    # Empty grippers: remove held geometry/sites after construction, preservinghand.
    seg=dict(label='park',station='inspection',poses=[{'R':hd},{'R':hd}],jaw_axes=[[0,1,0]])
    ch=adapter.Checker(definition,seg,c)
    root=ET.fromstring(ch.xml)
    for b in root.iter('body'):
        for e in list(b):
            if e.get('name','').startswith('R_held_'):b.remove(e)
    ch.xml=ET.tostring(root,encoding='unicode');ch.bind_model(mujoco.MjModel.from_xml_string(ch.xml))
    q,_=ch.initial(np.random.default_rng(2),2);rng=np.random.default_rng(8271)
    # Search arms separately at separatedX using literal referenceforbidden.
    parked={}
    for side,x in (('R',-.95),('L',.55)):
        q[ch.qa[side+'_carriage_x']]=x;names=adapter.ck.ARMS[side];bestq=q.copy();score=(999,999.)
        for k in range(4000):
            cand=q.copy()
            for nm in names:
                lo,hi=ch.m.jnt_range[ch.jid[nm]];cand[ch.qa[nm]]=rng.uniform(lo,hi)
            bad=[h for h in ch.forbidden(cand) if any(n.startswith(side+'_') for n in h['pair']) and not any(n.startswith(('L_' if side=='R' else 'R_')) for n in h['pair'])]
            ch.d.qpos[:]=cand;mujoco.mj_forward(ch.m,ch.d);ratio=max(abs(ch.d.qfrc_bias[ch.da[n]])/adapter.ck.LIM[n]['continuous_Nm'] for n in names)
            if (len(bad),ratio)<score:score=(len(bad),ratio);bestq=cand
            if not bad and ratio<.25:break
        q=bestq;parked[side]=dict(score=score,joints={n:float(q[ch.qa[n]]) for n in names})
    hits=ch.forbidden(q);write(O/'park.json',dict(config=c,q=q.tolist(),hits=hits,collision_free=not hits,parking_search=parked));export(ch,q,'parked','Clear sampled park; hardware unqualified' if not hits else 'REJECTED park: collision remains')
    states=[];frozen=q.copy()
    for x in np.linspace(-1.2,.7,41):
        qq=frozen.copy();qq[ch.qa['R_carriage_x']]=x;qq[ch.qa['L_carriage_x']]=-.5
        hits=ch.forbidden(qq);states.append(dict(R_x=float(x),L_x=-.5,hits=hits,ok=not hits))
    cross=frozen.copy();cross[ch.qa['R_carriage_x']]=cross[ch.qa['L_carriage_x']]=-.5
    crosshits=ch.forbidden(cross);export(ch,cross,'passing','Same-X pose clear; corridor check fails' if not crosshits else 'REJECTED passing: collision remains')
    write(O/'passing.json',dict(states=states,all_sampled_states_clear=all(s['ok'] for s in states),same_x_hits=crosshits,passes=len([s for s in states if s['ok']]),samples=len(states),continuous_path_certified=False,tools_parked=True,empty_grippers_retained=True,order_changes_on_different_lanes=True))
    p=H/'models/best_scene.xml';ET.ElementTree(root).write(p,encoding='unicode')
    # Keyframe contains exact actualpark or rejecteddiagnostic, labelledaccordingly.
    key=ET.SubElement(root,'keyframe');ET.SubElement(key,'key',name='park_checked',qpos=model.fmt(q));ET.ElementTree(root).write(p,encoding='unicode')
    write(H/'models/best_scene.json',dict(config=c,meta=adapter.ck.META,park_checked=not ch.forbidden(q)))

def phase_renders():
    for label,pid in [('overview','Q24'),('washing','Q02.carrot'),('peeling','Q05.carrot'),('eye_core','Q06.potato'),('root_cutting','Q10.carrot'),('greens_washing','Q16'),('greens_cutting','Q19'),('tomato_cutting','Q24'),('delivery','Q25')]:
        r=json.loads((O/'final_v4/c0684'/(pid+'.json')).read_text());pi=0
        if label=='washing':pi=1
        if label=='greens_washing':pi=1
        part=r['parts'][pi];ch=adapter.Checker(r['definition'],r['definition']['segments'][pi],r['config'])
        row=part['best'];pose=len(row['poses'])-1;ch.environment_pose(pose);q=row['poses'][pose]['q']
        status='Admitted keypose; torque reference unqualified' if row.get('ok') else 'REJECTED diagnostic pose: '+row.get('blocker',{}).get('kind','unknown')
        export(ch,q,label,status)
        # Save current door transforms and a reproducible actual pose keyframe.
        root=ET.fromstring(ch.xml)
        for a in model.P['moving_geometry_states']['front_doors']:
            g=root.find(f".//geom[@name='{a['id']}']");gid=ch.m.geom(a['id']).id
            g.set('pos',model.fmt(ch.m.geom_pos[gid]));g.set('quat',model.fmt(ch.m.geom_quat[gid]))
        keys=ET.SubElement(root,'keyframe');ET.SubElement(keys,'key',name='saved_checked_pose',qpos=model.fmt(q))
        ET.ElementTree(root).write(H/'models'/f'{label}.xml',encoding='unicode')

def observed_loads():
    maxima={};cases=0
    def put(name,value,witness):
        if name not in maxima or value>maxima[name]['value']:maxima[name]=dict(value=float(value),witness=witness)
    for file in sorted((O/'final_v4/c0684').glob('Q*.json')):
        r=json.loads(file.read_text())
        for si,part in enumerate(r['parts']):
            ch=adapter.Checker(r['definition'],r['definition']['segments'][si],r['config']);m,d=ch.m,ch.d
            desc=r['definition']['segments'][si]
            bodies={}
            for side in adapter.ck.ARMS:
                bid=m.body(side+'_carriage').id;ids=[]
                for b in range(m.nbody):
                    parent=b
                    while parent and parent!=bid:parent=int(m.body_parentid[parent])
                    if parent==bid:ids.append(b)
                bodies[side]=ids
            for row in part['rows']:
                for pi,po in enumerate(row['poses']):
                    if any(e['position_mm']>5 or e['orientation_deg']>3 for e in po['errors']):continue
                    q=np.array(po['q']);hands=desc['poses'][pi];ch.environment_pose(pi)
                    d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
                    for forces,moments in adapter.wrench_cases(hands,'check'):
                        case=dict(phase=r['id'],segment=si,seed=row['k'],pose=pi,nominal_admitted=row['ok'],payload_sizing_kg=3)
                        wallF=np.zeros(3);wallM=np.zeros(3);datum=np.array([0,.6,1.27])
                        for side,ids in bodies.items():
                            origin=d.body(side+'_carriage').xpos.copy();F=np.zeros(3);M=np.zeros(3)
                            points=[(d.xipos[b],np.array([0,0,-m.body_mass[b]*9.81])) for b in ids]
                            if side in hands:
                                points += [(d.site(side+'_work').xpos,np.array(forces[side])),(d.site(side+'_mass').xpos,np.array([0,0,-3*9.81]))]
                            else:points += [(d.site(side+'_prep').xpos,np.array([0,0,-3*9.81]))]
                            for p,f in points:F+=f;M+=np.cross(p-origin,f);wallF+=f;wallM+=np.cross(p-datum,f)
                            if side in hands:M+=np.array(moments[side]);wallM+=np.array(moments[side])
                            put('observed_carriage_force_N',np.linalg.norm(F),dict(case,side=side,F_N=F.tolist(),M_Nm=M.tolist()))
                            put('observed_carriage_moment_Nm',np.linalg.norm(M),dict(case,side=side,F_N=F.tolist(),M_Nm=M.tolist()))
                            put('observed_drive_static_N',abs(F[0]),dict(case,side=side))
                        railweight=(2*51.16944+18)*9.81;wallF += [0,0,-railweight]
                        put('observed_net_wall_force_N',np.linalg.norm(wallF),case);put('observed_net_wall_moment_Nm',np.linalg.norm(wallM),case)
                        tq=ch.torque_multi(q,hands,forces,payload=3,moments=moments)
                        # Size both arms at3kg, including an otherwise empty park.
                        tau=d.qfrc_bias.copy();jp=np.zeros((3,m.nv));jr=np.zeros_like(jp)
                        for side in bodies:
                            if side in hands:
                                mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_work').id);tau-=jp.T@np.array(forces[side])+jr.T@np.array(moments[side])
                            mujoco.mj_jacSite(m,d,jp,jr,m.site(side+'_mass' if side in hands else side+'_prep').id);tau-=jp.T@np.array([0,0,-3*9.81])
                        ratios={n:float(abs(tau[ch.da[n]])/adapter.ck.LIM[n]['continuous_Nm']) for n in adapter.ck.JOINTS};j=max(ratios,key=ratios.get)
                        tq=dict(ratio=ratios[j],joint=j,required_Nm=float(abs(tau[ch.da[j]])),reference_Nm=adapter.ck.LIM[j]['continuous_Nm'],joints=ratios)
                        put('IK_pose_3kg_design_force_torque_reference_ratio',tq['ratio'],dict(case,torque=tq))
                        if row['ok']:put('admitted_pose_3kg_design_force_torque_reference_ratio',tq['ratio'],dict(case,torque=tq))
                        cases+=1
    data=json.loads((O/'loads.json').read_text());data.update(observed_3kg_cases=cases,observed_maxima=maxima,observed_limits='Includes collision-rejectedIKposes; not a working-loadadmission. Explicit whole-body bounds remain thesizingbasis. Netwallmoment includes bodyforcesbut excludes actual beamstand-off moments, so use the conservativebound.');write(O/'loads.json',data)

if __name__=='__main__':
    for mode in sys.argv[1:]:globals()[mode]()
