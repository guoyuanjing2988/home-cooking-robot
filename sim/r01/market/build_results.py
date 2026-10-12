"""Deterministic, CPU-only market deliverables. No simulation/checker mutation."""
from pathlib import Path
import csv, json, math, hashlib, ast, time
from research_data import ARMS, SOURCES, RAILS, TOOLS, PREP_TOOLS
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]
OUT=ROOT/'results'
START=time.monotonic()

def dump(name, data):
    assert time.monotonic()-START < 60, 'build deadline'
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def flat(x):
    if x is None: return ''
    if isinstance(x,(list,dict)): return json.dumps(x,ensure_ascii=False,separators=(',',':'))
    return x
def write_csv(name, rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        w.writerows({k:flat(v) for k,v in r.items()} for r in rows)
def refs(ids): return '; '.join(SOURCES[i]['url'] for i in ids)
def citations(ids): return ', '.join(f"[{SOURCES[i]['title']}]({SOURCES[i]['url']})" for i in ids)

manifest=json.loads((OUT/'evidence_manifest.json').read_text(encoding='utf-8'))
supplement=json.loads((OUT/'supplement_manifest.json').read_text(encoding='utf-8'))
extra=json.loads((OUT/'model_excerpt_manifest.json').read_text(encoding='utf-8'))
repos={r['repo']:r for r in manifest['repositories']+supplement['repositories']+extra['repositories'] if 'commit' in r}
MODEL_CHOICES={
 'ur3e':('UniversalRobots/Universal_Robots_ROS2_Description','urdf/ur.urdf.xacro'),
 'ur5e':('google-deepmind/mujoco_menagerie','universal_robots_ur5e/ur5e.xml'),
 'xarm6':('xArm-Developer/xarm_ros','xarm_description/urdf/xarm6/xarm6.urdf.xacro'),
 'xarm7':('google-deepmind/mujoco_menagerie','ufactory_xarm7/xarm7_nohand.xml'),
 'lite6':('google-deepmind/mujoco_menagerie','ufactory_lite6/lite6.xml'),
 'uf850':('xArm-Developer/xarm_ros','xarm_description/urdf/uf850/uf850.urdf.xacro'),
 'fr3':('google-deepmind/mujoco_menagerie','franka_fr3/fr3.xml'),
 'gen3':('Kinovarobotics/ros_kortex','kortex_description/arms/gen3/7dof/urdf/GEN3-7DOF_BRAKES_NO-VISION_URDF_ARM_V01.urdf'),
 'jaka5':('JAKARobotics/jaka_ros2','src/jaka_description/urdf/jaka_zu5.urdf'),
 'jaka7':('JAKARobotics/jaka_ros2','src/jaka_description/urdf/jaka_zu7.urdf'),
 'cs66':('EliteRobots/Elite_Robots_CS_ROS2_Description','urdf/cs.urdf.xacro'),
 'auboi5':('AuboRobot/aubo_description','urdf/aubo_i5.urdf'),
 'cr5':('Dobot-Arm/TCP-IP-ROS-6AXis','dobot_description/urdf/cr5_robot.urdf'),
 'rm65':('RealManRobot/ros2_rm_robot','rm_description/urdf/rm_65.urdf'),
 'rokaecr7':('RokaeRobot/rokae_ros2','rokae_description/urdf/xMateCR7.urdf.xacro'),
}
for a in ARMS:
    repo,path=MODEL_CHOICES[a['arm_id']];r=repos[repo]
    assert path in r['paths'], (repo,path)
    a.update(model_exists=True,model_format='MuJoCo XML' if repo.endswith('mujoco_menagerie') else 'official URDF/xacro',
      model_repository=repo,model_commit=r['commit'],model_path=path,
      model_url=f"https://github.com/{repo}/blob/{r['commit']}/{path}",
      model_validation='Repository/tree existence only; meshes/xacro assembly and hardware revision not validated',
      specs_urls=refs(a['spec_source_ids']),price_urls=refs(a['price_source_ids']),retrieved_date='2026-10-07')
    if a['arm_id']=='cs66': a['model_validation']='Generic CS xacro;select cs66 config at pinned commit;not compiled/revision matched'
    if a['arm_id']=='ur3e': a['model_validation']='Generic official UR xacro;select ur_type=ur3e andmatching config;not compiled/revision matched'
    if a['arm_id']=='auboi5': a['model_validation']='Official legacy i5 URDF;current H-revision23.3kg inertias/geometry match not established'
    if a['arm_id']=='xarm6': a['model_validation']='Official xacro;current1305 arm needs matching kinematics/config revision'

SHORTLIST=['JAKA Zu7','Elite CS66','UR5e','UFACTORY 850']
lines=[
 ('arms_controllers','JAKA Zu7 complete arm/controller allowance',75000,'arm',2,3,[61000,100000],['jaka7price'],'Estimate;61k public low-confidence ad plus14k configuration/price margin. Controllers included here.'),
 ('carriages','Independent carriage,4 blocks,plate,geared servo,encoder,drive,spring brake',15000,'carriage',2,3,[10000,25000],['railbrake','cnBeltPrice'],'Engineering allowance;not a branded turnkey carriage quote. Mechanical guide clamp may consume upper allowance.'),
 ('rail','Wall load beam,two guides,fixed rack,wall brackets,end stops',6000,'metre',2.4,2.4,[4000,10000],['guidePrice','hepco','bosch'],'Engineering assembly allowance;bare-guide price is not a complete axis price.'),
 ('covers','Drainable stainless splash/grease covers and wipers',1500,'metre',2.4,2.4,[1000,2500],[],'Custom fabrication allowance;no exposed rack over food.'),
 ('cable_carriers','Separate enclosed cable carrier,flex cables,PE and glands',3000,'arm',2,3,[2000,5000],['chain','chainPrice'],'Installed package allowance;one-link catalogue total not extrapolated to metres.'),
 ('grippers_keys','Electric gripper plus washable fingers and unchanged key interface',12000,'arm',2,3,[10000,20000],['dhGrip','ufprice'],'Engineering allowance;15Nm keyed load path and wet-food approval NOT proven by commodity gripper.'),
 ('wrist_adapters','Light manual positive-lock adapter and release/dock interlock',4000,'arm',2,3,[2000,8000],[],'Manual changer fixed during prep;P15/P16 tool pickup by jaws.0.3kg target;not ATI QC18 price.'),
 ('prep_tools','Reference prep tools,keys,receivers,food-contact consumables',8000,'cell',1,1,[6000,15000],['nemcoPrice','mandolinePrice','peelerPrice','spinnerPrice','boardSpec'],'Itemised allowance inprep_tools.csv;foreign base-tool retail references do not include custom keys/receivers;existing layout unchanged.'),
 ('scanner','One SICK microScan3-class safety scanner',75000,'cell',1,1,[50000,90000],['sickprice','sicksafety'],'75k budget rounded from74129.3025 CNY public China listing;protective-field coverage must be validated.'),
 ('curtain','Type4 light-curtain complete pair,plugs,side access interlocks',25000,'cell',1,1,[20000,40000],['curtainprice','curtainsafety'],'Pair allowance,not sender-only quote;final14mm/field geometry required.Sender30mm comparator10077.50 CNY.'),
 ('safety_electrical','Safety PLC,dual-channel stop/STO/brake interfaces,RCD/PE,enclosure',14000,'cell',1,1,[10000,25000],[],'Estimate;arm controllers already counted in arms line.Three-axis drive interfaces included in base allowance.'),
 ('ipc','Industrial control PC,network and cameras',8000,'cell',1,1,[6000,15000],[],'Estimate;person detection is certified sensor hardware above,not an ordinary AI camera.'),
 ('mount_install','Wall survey,concrete/masonry brackets,anchors,mechanical/electrical installation',18000,'two-arm cell',1,1,[12000,30000],['concreteAnchor','brickAnchor'],'Three-arm version+3000;no structural-wall replacement or cabinet reconstruction included.'),
 ('commission','Safety integration,stop/brake verification and prep commissioning',20000,'two-arm cell',1,1,[15000,40000],[],'Three-arm version+5000.First one-off engineering estimate,not mass-produced sale price.'),
]
items=[]
for id,name,unit,measure,q2,q3,band,ids,note in lines:
    v2=unit*q2;v3=unit*q3
    if id=='mount_install':v3+=3000
    if id=='commission':v3+=5000
    items.append(dict(id=id,item=name,unit_cost_cny=unit,unit=measure,quantity_2=q2,quantity_3=q3,
      two_arm_cny=round(v2,2),three_arm_cny=round(v3,2),unit_sensitivity_low_high_cny=band,
      source_ids=ids,source_urls=[SOURCES[i]['url'] for i in ids],price_basis=note))
subtotal2=sum(i['two_arm_cny'] for i in items);subtotal3=sum(i['three_arm_cny'] for i in items)
contingency=.15
totals={str(n):dict(subtotal_cny=val,contingency_rate=contingency,contingency_cny=round(val*contingency,2),installed_estimate_cny=round(val*(1+contingency),2)) for n,val in [(2,subtotal2),(3,subtotal3)]}
assert totals['2']['installed_estimate_cny']==464600
assert totals['3']['installed_estimate_cny']==599150
sensitivity={}
for n in (2,3):
    low=high=0
    for i in items:
        q=i[f'quantity_{n}'];lo,hi=i['unit_sensitivity_low_high_cny'];low+=q*lo;high+=q*hi
        if n==3 and i['id']=='mount_install':low+=3000;high+=3000
        if n==3 and i['id']=='commission':low+=5000;high+=5000
    sensitivity[str(n)]={'low_cny':round(low*1.15),'high_cny':round(high*1.15),'meaning':'Independent allowance extremes incl15%;not statistical confidence interval or supplier quote'}
alternatives=[]
for model,unit,basis in [('Elite CS66',80000,'No numeric public China price;80k hypothetical complete-set allowance only'),('UR5e',180000,'2022 itemised complete-set benchmark;not current quotation'),('UFACTORY 850',116000,'2025 public-procurement item;included accessories unresolved')]:
    alternatives.append(dict(model=model,arm_unit_cny=unit,basis=basis,
      cost2_cny=round((subtotal2+2*(unit-75000))*1.15),cost3_cny=round((subtotal3+3*(unit-75000))*1.15),
      meaning='Replace arm line only;does not requalify safety,torques,tools or installation'))
costs=dict(schema_version='1.0',date='2026-10-07',currency='CNY',status='Conditional engineering installed-cost estimate;not an order-ready or compliance-approved design',
 reference_architecture='2.4m back-wall beam,independent rack-driven nonpassing carriages,mains via separate cable carriers;no torso/mobile base/battery/humanoid arm',
 shortlist=SHORTLIST,baseline_arm='JAKA Zu7',arm_controller_included=True,rail_length_m=2.4,
 foreign_price_conversion=dict(cny_per_usd=7.0,kind='explicit planning assumption;not live FX',domestic_price=False),
 tax_basis='Gross installed CNY allowances;historical procurement/ad VAT/accessories often unspecified.Foreign EXW comparators not used as domestic current prices.',
 items=items,totals=totals,cost2_cny=totals['2']['installed_estimate_cny'],cost3_cny=totals['3']['installed_estimate_cny'],
 incremental_third_arm_cny=totals['3']['installed_estimate_cny']-totals['2']['installed_estimate_cny'],sensitivity=sensitivity,
 same_hardware_alternative_arm_scenarios=alternatives,
 r1_pro_comparison=dict(reference_cny=470000,source='User-supplied approximate reference;not verified supplier quote',
    two_arm_difference_cny=totals['2']['installed_estimate_cny']-470000,
    three_arm_difference_cny=totals['3']['installed_estimate_cny']-470000,
    limitation='Installed custom fixed prep cell versus platform reference only;equal food tools/safety/installation scope not established'),
 optional_changes=dict(freestanding_static_portal_extra_cny=20000,curved_corner_extra_cny=[30000,80000],
  curved_corner_basis='Unquoted engineering add-on inclbogies,rack,cable corner routing andstructure,not a supplier price',
  automatic_qc18_per_arm_allowance_cny=25000,automatic_qc18_basis='Unquoted changer-only estimate;adds1.77kg and may force>=7kg arm;not in baseline'),
 exclusions=['Recurring subscriptions','Cabinet/sink/faucet relocation','Structural wall or floor reconstruction','L-corner track','Cooking/plating equipment','Automatic wrist tool changer','Additional F/T sensors pending force-control design','Software development for general-purpose autonomy beyond commissioning','Lifecycle service and consumables'],
 unresolved_requirements=['Public continuous joint-output torque limits for all shortlist axes unavailable','Exact all-axis spring-applied brake construction/holding torque not proven','Custom keyed-gripper15Nm capability/food suitability not qualified','Missing authoritative water-outlet and outlet/door surveys','IK/collision/P01-P16 not evaluated by market role'],
 source_registry='sources.json')

def anchor_record(a):
    g=9.81;df=1.5;e=.12;toolside=5.0;carriage=15.0;r=a['reach_mm']/1000;m=a['arm_mass_kg'];h=.25
    shear=df*g*(m+toolside+carriage)
    moment=df*g*(m*(e+r/2)+toolside*(e+r)+carriage*e)
    envelope=df*g*((m+toolside)*(e+r)+carriage*e)
    return dict(model=a['model'],reach_m=r,arm_mass_kg=m,food_mass_kg=3,eoat_allowance_kg=2,carriage_mass_kg=carriage,
     dynamic_factor=df,wall_standoff_m=e,assumed_arm_com_reach_fraction=.5,vertical_force_n=round(shear,3),
     wall_overturning_moment_nm=round(moment,3),all_arm_mass_at_full_reach_moment_nm=round(envelope,3),
     anchor_rows_vertical_spacing_m=h,anchor_count=4,top_anchors_count=2,
     top_anchor_tension_each_n=round(moment/(2*h),3),shear_each_anchor_n=round(shear/4,3),
     envelope_top_anchor_tension_each_n=round(envelope/(2*h),3),
     limitation='First-order1.5factored gravity only;armCOM assumed.Vendor stop/support loads,cable drag,carriage acceleration,beam/anchor-group distribution andprying govern finaldesign.')
anchor_rows=[anchor_record(a) for a in ARMS if a['arm_id'] in ('jaka7','cs66','ur5e','uf850')]
loads=dict(assumptions=dict(g_m_s2=9.81,dynamic_factor=1.5,food_per_arm_kg=3,eoat_budget_per_arm_kg=2,toolside_total_kg=5,
  eoat_breakdown_kg={'gripper':1.0,'manual_adapter':.3,'fingers_keys':.2,'largest_retained_tool_allowance':.5},
  tool_mass_rule='Hardware allowance for generic3kg capability;do not add3kg again to P06/P10 held masses when checker already includes food.'),
  formula='V=1.5*g*(m_arm+5+15);M=1.5*g*[m_arm*(0.12+R/2)+5*(0.12+R)+15*0.12];Ntop=M/(2*0.25);Vanchor=V/4',
  per_arm=anchor_rows,
  clustered_jaka={str(n):{'vertical_force_n':round(next(x['vertical_force_n'] for x in anchor_rows if x['model']=='Zu7')*n,3),
   'wall_moment_nm':round(next(x['wall_overturning_moment_nm'] for x in anchor_rows if x['model']=='Zu7')*n,3)} for n in (2,3)},
  vendor_stop_loads=dict(ur5e={'Mxy_nm':750,'Mz_nm':450,'Fz_n':1090,'Fxy_n':910,'vendor_safety_factor_included':2.5,'source_id':'urmount'},
   rokae_cr7={'Mxy_nm':889,'Mz_nm':743,'Fz_n':1103,'source_id':'rokaespec'},
   elite_cs66={'source_id':'eliteman','requirement':'Manual requires mounting stiffness/load design relative to10x maximum base overturning moment and5x arm weight;exact loads must come from matching manual revision'}),
  conservative_ur_anchor_screen={'pitch_m':.25,'top_anchor_count':2,'moment_tension_each_n':1500,
   'added_normal_force_each_n':272.5,'conservative_total_tension_each_n':1772.5,'meaning':'Illustrative envelope;real coordinate transformation/concurrent load case and prying must be designed'},
  mounting_recommendation='Concrete:engineered bonded anchors;tested solid/hollow brick:matched HY270+rod/screen under substrate approval.AAC/lightweight block orunknownwall:static floor-anchored portal behindcounter;do not attach to cabinet carcass.',
  source_ids=['urmount','rokaespec','eliteman','concreteAnchor','brickAnchor','brickLimits'],not_structural_approval=True)

scene=dict(units='m',purpose='Market installation obstacle proxies;not an IK witness or a replacement for authoritative checker scene',
 counter={'z':.85,'y_bounds':[0,.60],'free_x_bounds':[[-1.80,-.70],[-.11,.69]],'stove_protected_x_bounds':[.69,1.47]},
 proposed_rail={'length':2.4,'x_bounds':[-1.80,.60],'nominal_center_z':1.05,'back_wall_y':0,'mounting_interface_exception':'Only physical wall brackets/anchors contact wall;all other robot parts>=10mm environment gap',
  'finite_carriage_assumption':'~0.30m carriage envelope plus~0.10m end margins;~1.90m centre-travel estimate,not2.4m usable travel;nonpassing carriages'},
 upper_cabinets={'source_ids':['cabinet','cabinetHeight'],'proxy_x_bounds':[-1.8,1.47],'proxy_y_bounds':[0,.37],
  'underside_z':1.35,'top_z':2.15,'height_assumption':.8,'counter_to_underside_gap':.5,
  'door_leaf_width_assumption':.6,'hinge_at_front_y':.37,'door_sweep_deg':[0,90],
  'door_swept_y_upper_bound':.97,'state':'Closed-body and full-door-sweep obstacle;exact hinges/heights are survey-dependent'},
 faucet={'source_id':'faucet','typical_total_height':.36,'proxy_top_z':1.21,
  'base_x_assumption':-.405,'base_y_assumption':.10,'riser_radius_assumption':.035,
  'spout_sweep_radius_assumption':.25,'swivel_deg':120,
  'obstacle_primitives':[{'type':'vertical_cylinder','center':[-.405,.10,1.01],'radius':.035,'height':.32},
                         {'type':'swivel_envelope_cylinder','center':[-.405,.10,1.185],'radius':.25,'height':.05}],
  'placement_status':'Explicit market proxy centered in apparent sink gap,not authoritative.Swept cylinder conservatively includes allangles;actualwater-outlet pose must be restored from originalscene metadata,not inferred from spoutbox.'},
 outlets={'coordinates':None,'rule':'Keep plug/service envelopes clear;no mounting/drilling/cable-carrier run over unsurveyed outlets.No fabricated outlet coordinates.'},
 wedger={'authoritative_top_z':1.3326,'cabinet_bottom_gap_m':round(1.35-1.3326,4),'remaining_after_10mm_m':round(1.35-1.3326-.01,4)},
 required_gaps={'robot_environment_m':.010,'gripper_held_tool_m':.005},
 unresolved=['Faucet proxy overlaps low-rail height,so routing/standoff must resolve realfaucet geometry beforecontinuous rail canbe accepted','Cabinet doors need fullsweep clearance for robot,carriageandcablechain','No numericIK/gap acceptance claim made'])

torque=dict(rule='Only model-matched manufacturer continuous/rated JOINT-OUTPUT torques may populate checker;allcataloguevaluesnull pending that evidence',
  ufactory_published_motor_side={'uf850':[1.5,1.5,.955,.46,.15,.15],'xarm6_1305':[.955,.955,.46,.46,.15,.15]},
  ufactory_gear_ratio=100,
  ideal_rated_motor_times_ratio_not_checker_limits={'uf850':[150,150,95.5,46,15,15],'xarm6_1305':[95.5,95.5,46,46,15,15]},
  missing='Transmission efficiency,continuous thermal/duty output rating,orientation/payload derating andexact hardware revision',
  forbidden_substitutes=['URDF effort','MuJoCo actuator control range','peak/maximum torque','brake holding torque','old55/25/18Nm ceilings'],source_id='uftorque')

write_csv('catalog.csv',ARMS)
write_csv('rails.csv',[dict(r,source_urls=refs(r['source_ids'])) for r in RAILS])
write_csv('tools.csv',[dict(t,source_urls=refs(t['source_ids'])) for t in TOOLS])
assert sum(t['budget_installed_cny'] for t in PREP_TOOLS)==8000
write_csv('prep_tools.csv',[dict(t,public_china_price_cny=None,source_urls=refs(t['source_ids'])) for t in PREP_TOOLS])
dump('prep_tools.json',PREP_TOOLS)
dump('catalog.json',ARMS);dump('costs.json',costs);dump('sources.json',SOURCES)
dump('mounting_loads.json',loads);dump('scene_assumptions.json',scene);dump('torque_evidence.json',torque)
dump('model_sources.json',{'date':'2026-10-07','scope':'Pinned repository tree inspection only;not a complete runnable model installation','models':[{k:a[k] for k in ('arm_id','model_repository','model_commit','model_path','model_url','model_validation')} for a in ARMS]})

# Generated table snippets used by the bilingual post, with directly supporting links.
table=['| Arm | DOF / reach mm / payload kg / mass kg | Mount / protection | China price evidence CNY | Model |','|---|---|---|---|---|']
for a in ARMS:
    price=f"{a['public_china_price_cny']:,.0f}" if a['public_china_price_cny'] is not None else 'ND'
    if a.get('foreign_price_amount'):price+=f"; USD{a['foreign_price_amount']:,} EXW → {a['planning_converted_cny']:,} planning only"
    if a['arm_id']=='xarm6':price+=';2026 award76,900'
    if a['arm_id']=='auboi5':price+=';2026 package194,800'
    table.append(f"| [{a['model']}]({SOURCES[a['spec_source_ids'][0]]['url']}) | {a['dof']} / {a['reach_mm']} / {a['rated_payload_kg']} / {a['arm_mass_kg']} | {a['mounting_allowed']}; {a['ip_rating']} | {price}; {citations(a['price_source_ids'])} | [{a['model_format']}]({a['model_url']}) |")
(OUT/'catalog_table.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
table=['| Installed item | 2 arms CNY | 3 arms CNY | Basis |','|---|---:|---:|---|']
for i in items:table.append(f"| {i['item']} | {i['two_arm_cny']:,.0f} | {i['three_arm_cny']:,.0f} | {i['price_basis']} |")
table.extend([f'| Subtotal | {subtotal2:,.0f} | {subtotal3:,.0f} | |',f"| 15% contingency | {totals['2']['contingency_cny']:,.0f} | {totals['3']['contingency_cny']:,.0f} | Engineering reserve |",f"| **Installed estimate** | **{costs['cost2_cny']:,.0f}** | **{costs['cost3_cny']:,.0f}** | Conditional budget |"])
(OUT/'cost_table.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
table=['| Full-reach carriage | 1.5-factored vertical force N | Wall moment Nm, assumed arm COM at R/2 | Moment Nm, all arm mass at full reach envelope | Top-anchor tension each N, first model |','|---|---:|---:|---:|---:|']
for r in anchor_rows:table.append(f"| {r['model']} | {r['vertical_force_n']:.1f} | {r['wall_overturning_moment_nm']:.1f} | {r['all_arm_mass_at_full_reach_moment_nm']:.1f} | {r['top_anchor_tension_each_n']:.1f} |")
(OUT/'mount_table.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
table=['| Model-only substitution | 2 arms installed CNY | 3 arms installed CNY | Price basis |','|---|---:|---:|---|']
for a in alternatives:table.append(f"| {a['model']} | {a['cost2_cny']:,.0f} | {a['cost3_cny']:,.0f} | {a['basis']} |")
(OUT/'alternative_cost_table.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
assert len(ARMS)>=10
assert all(i in SOURCES for a in ARMS for i in a['spec_source_ids']+a['price_source_ids'])
current_hash={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (WORKSPACE/'inputs').iterdir() if p.is_file()}
assert current_hash==supplement['input_sha256'], 'input content changed during market research'
dump('validation.json',{'date':'2026-10-07','catalog_arm_count':len(ARMS),'model_paths_verified_in_pinned_trees':len(ARMS),
  'shortlist':SHORTLIST,'cost_arithmetic_verified':True,'input_hashes_unchanged_since_research_snapshot':True,
  'input_sha256':current_hash,'continuous_joint_output_limits_verified_count':0,'all_binding_requirements_verified_count':0,
  'checker_executed':False,'ik_executed':False,'reason':'Market role;missing copied authoritative scene metadata and continuous torque ratings. No market feasibility claim.',
  'elapsed_s':round(time.monotonic()-START,3),'sources_count':len(SOURCES)})
print(json.dumps({'arms':len(ARMS),'sources':len(SOURCES),'cost2_cny':costs['cost2_cny'],'cost3_cny':costs['cost3_cny'],'sensitivity':sensitivity},indent=2))
