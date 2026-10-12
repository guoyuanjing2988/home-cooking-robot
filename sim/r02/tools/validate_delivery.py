"""Finite schema, mechanics, geometry and provenance checks; not an IK verdict."""
from pathlib import Path
import csv, hashlib, itertools, json, math
from PIL import Image
R=Path(__file__).resolve().parent
W=R.parents[2]
p=json.loads((R/'results/process_v2.json').read_text(encoding='utf-8'))
cad=json.loads((R/'cad/cad_manifest.json').read_text(encoding='utf-8'))
sources=json.loads((R/'research/sources.json').read_text(encoding='utf-8'))
cost=json.loads((R/'results/cost_summary.json').read_text(encoding='utf-8'))
checks=[]
def check(name,ok,evidence):
    checks.append(dict(name=name,pass_=bool(ok),evidence=evidence))
def close(a,b):return abs(a-b)<.001
check('logical_phase_sequence',p['phase_count']==27 and [q['id'] for q in p['phases']]==[f'Q{i:02}' for i in range(1,28)],27)
check('ingredient_expansion',len(p['checker_instances'])==36 and len({q['instance_id'] for q in p['checker_instances']})==36,36)
check('finished_products',set(r['product'] for r in p['finished_products'])=={'carrot','potato','leafy_greens','tomato'},'four independent next-step bowls; transfer >=98%')
contract=p['checker_contract']
check('unchanged_checker_contract',contract['pose_tolerance_m']==.005 and contract['pose_tolerance_deg']==3 and contract['robot_environment_gap_m']==.010 and contract['gripper_held_tool_gap_m']==.005 and contract['mu']==.5 and contract['SF']==1.5 and contract['total_normal_N']==150 and contract['key_force_N']==150 and contract['key_moment_Nm']==15 and not contract['acm_changes'] and not contract['padding_changes'] and not contract['new_contact_exemptions'],'No relaxed gate or added contact exemption')
ids={s['id'] for s in sources}
check('force_provenance',all(f['source_ids'] and all(s in ids or s.startswith('physics:') for s in f['source_ids']) for f in p['force_models'].values()),'Every process load has source IDs and a stated margin/limitation')
f=p['force_models']
expected={'carrot_cut':2*67.59/31*35,'potato_cut':2*61.49/47*70,'greens_cut':2*67.59/31*80,'tomato_wedge':2*15/(math.pi*2**2)*(4*70)*.952,'peel_drag':1.5*1.68*25,'drawer_insert':1.5*(.5*1.1*9.81+1.1*.3+2),'water_jet':1.5*1000*(.006/60)**2/(math.pi*.01**2/4)}
expected['machine_index']=1.5*(.5*1.1*9.81+1.1*.3)
check('force_arithmetic',all(close(f[k]['design_N'],v) for k,v in expected.items()),{k:round(v,4) for k,v in expected.items()})
poses=[h for q in p['checker_instances'] for seg in q['segments'] for pp in seg['poses'] for h in pp.values()]
check('pose_fields_and_positive_masses',all(len(h['pos'])==3 and len(h['approach'])==3 and len(h['jaw_axis'])==3 and h['held'] in p['tools'] and h['held_kg']>=0 and h['force_model_ids'] for h in poses),len(poses))
check('powered_cycle_detachment',all(not q['appliance_action']['arm_contact_during_cycle'] and q['appliance_action']['arm_external_force_N']==[0,0,0] for q in p['checker_instances'] if q.get('appliance_action')),'Loading, gravity and brush reaction remain explicit arm loads')
side_max={s:max(h['held_kg'] for q in p['checker_instances'] for seg in q['segments'] for pp in seg['poses'] for side,h in pp.items() if side==s) for s in ('R','L')}
check('task_payload_budgets',side_max['R']<=3 and side_max['L']<=1 and 3+p['arms']['R']['end_effector_budget_kg']<=5,side_max)
check('valid_native_solids_and_step',len(cad['parts'])==18 and all(x['valid'] and x['solid_count']>=1 and x['volume_mm3']>0 and (R/'cad'/x['step_file']).stat().st_size>1000 for x in cad['parts']),{x['id']:x['solid_count'] for x in cad['parts']})
cm={x['id']:x['cad_mass_kg'] for x in cad['parts']}
check('carried_CAD_mass_within_budgets',cm['C04']<.30 and cm['C06']<.80 and cm['C13']<.90 and cm['C18']<.30,dict(bail=cm['C04'],insert=cm['C06'],root_cassette=cm['C13'],food_cup=cm['C18']))
slabs=[(-1.8,-.7),(-.11,.69)]
stations=[a for a in p['counter_layout'] if a['id']!='sink_insert']
check('station_footprints_in_T08_slabs',all(any(lo-1e-9<=a['bounds_counter_m'][0][0] and a['bounds_counter_m'][0][1]<=hi+1e-9 for lo,hi in slabs) and 0<=a['bounds_counter_m'][1][0] and a['bounds_counter_m'][1][1]<=.6 for a in stations),{a['id']:a['bounds_counter_m'] for a in stations})
def gap(bounds1,bounds2):
    return math.sqrt(sum(max(a[0]-b[1],b[0]-a[1],0)**2 for a,b in zip(bounds1,bounds2)))
station_gap=min((gap(a['bounds_counter_m'][:2],b['bounds_counter_m'][:2]),a['id'],b['id']) for a,b in itertools.combinations(stations,2))
check('station_separation',station_gap[0]>=.010-1e-9,station_gap)
fixed=[x for x in cad['instances'] if x['name'].startswith(('Press','Crosshead','StraightBlade','LeftGuard','RightGuard'))]
cabinet_gap=.5-max(x['bounds_mm'][2][1]/1000 for x in fixed)
check('fixed_machine_cabinet_and_door_sweep',cabinet_gap>=.010,dict(minimum_vertical_gap_m=round(cabinet_gap,6),cabinet_bottom_counter_z_m=.5))
outlets=[[[x-.05,x+.05],[.52,.60],[.12,.20]] for x in (-.9,.15)]
outlet_gap=min(gap([[a/1000,b/1000] for a,b in x['bounds_mm']],o) for x in fixed for o in outlets)
check('fixed_machine_outlet_access',outlet_gap>=.010,dict(minimum_AABB_gap_m=round(outlet_gap,6),source='R01 representative outlet access boxes, not a site electrical survey'))
check('fixed_nonmount_machine_counter_gap',all(x['bounds_mm'][2][0]>=10 for x in fixed if x['name']!='PressBase'),'PressBase body underside12mm; four mount feet touch counter. Other fixed parts >=15mm.')
door_bounds=[d['sweep_bounds_m'] for d in p['moving_geometry_states']['front_doors']]
check('door_sweeps_inside_counter',all(.15<=b[0][0] and b[0][1]<=.65 and .010<=b[1][0] and b[1][1]<=.56 for b in door_bounds),door_bounds)
rows=list(csv.DictReader((R/'results/tools_bom.csv').open(encoding='utf-8-sig')))
subtotal=round(sum(float(r['line_cny']) for r in rows if r['scope']=='tools'),2)
check('BOM_total',close(subtotal,cost['tools_bom_cny']),subtotal)
check('appliance_and_part_counts',len(p['powered_appliances'])==1 and cost['custom_part_designs']==18,dict(appliances=1,custom_designs=18))
original=json.loads((R/'audit/input_hashes.json').read_text())
hashes={k:hashlib.sha256((W/k).read_bytes()).hexdigest() for k in original}
check('read_only_reference_hashes',hashes==original,hashes)
images={n:list(Image.open(R/'renders'/n).size) for n in ['layout_perspective.png','layout_plan.png']}
check('render_size',all(max(s)<=1600 for s in images.values()),images)
bytes_total=sum(x.stat().st_size for x in R.rglob('*') if x.is_file())
check('output_storage_bound',bytes_total<2_000_000_000,dict(total_bytes=bytes_total))
# Elastic sizing only: exact joint/guide and actuator qualification remains required.
E=193000 # MPa, engineering assumption for austenitic stainless at room temp
Ix=(45*40**3-41*36**3)/12
stress=1000*400/4*20/Ix
deflection=1000*400**3/(48*E*Ix)
report=dict(status='pass' if all(c['pass_'] for c in checks) else 'fail',checks=checks,beam_hand_calculation=dict(assumed_E_MPa=E,I_mm4=Ix,span_mm=400,central_load_N=1000,stress_MPa=stress,deflection_mm=deflection,limitations='Simply supported beam idealization; not joint/guide/brake or buckling qualification.'),not_evaluated=['IK or continuous arm paths','actual OEM output torque ratings','food quality and peel completeness','food-contact compliance of finished assemblies','Nemco fit and supported food handoff stroke','running drive torque, Category1 safety and brake evidence'],task_side_max_held_kg=side_max)
(R/'audit/delivery_validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(dict(status=report['status'],checks=len(checks),failures=[c['name'] for c in checks if not c['pass_']],parts=18,phases=27,instances=36,bom_cny=subtotal,output_MB=round(bytes_total/1e6,2))))
raise SystemExit(0 if report['status']=='pass' else 1)
