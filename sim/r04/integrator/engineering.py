"""Traceable planning loads, power, cost and meal-time ledger; no supplier contact."""
import json,csv,math,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];O=H/'results';A=H/'audit'
def write(name,x): (O/name).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
costs=[
 ('UR5e complete main arm/controller',1,150000,'R03 planning allowance, not a current quotation'),
 ('xArm6 complete helper arm/controller',1,76900,'R01 historical award budget reproduced; not a current quotation'),
 ('Two independent lanes, guides, carriages, brakes, chains, frame',1,56000,'R02 reviewer home-tier reconciliation; includes changed adapters/hangers/anchors'),
 ('Retained food-contact tools and guarded auxiliary cassette cutter',1,12799.96,'R02 tools itemised base less duplicated B09 safety; retained conservatively, no tools contingency'),
 ('Sealed root-brush pivot, latch and drive',1,1500,'R03 allowance;10Nm design target exceeds1.5*(9.191N*.29m+1kg*9.81*.29m)=8.26Nm; prototype mass and seal qualification required'),
 ('Robot-Coupe R211 XL, 5mm disc and bowl discharge adapter',1,18000,'R03 planning allowance; OEM product publicly specified, matched China quote unavailable'),
 ('Electric grippers, washable fingers, keyed retention',2,12000,'R02 EOAT allowance'),
 ('IPC, vision and network',1,8000,'R02 allowance; presence sensor is in safety package'),
 ('Mounting and site electrical installation',1,18000,'R02 allowance; no safety component duplication'),
 ('Food, force, calibration and stop/holding qualification labour',1,20000,'R02 labour allowance; excludes hardware already charged'),
 ('Dry stationary household tracks and adapters',1,3000,'R02 allowance; moving arms use chains'),
 ('Inclusive home-safety package',1,18000,'Presence sensing, E-stop, RCD/PE, stop/brake interfaces, blade/lid interlocks and safety wiring; rail brakes in transport line; no B09/industrial scanner/PLC duplicate')]
subtotal=sum(q*v for _,q,v,_ in costs);total=round(subtotal*1.15,2)
with (O/'costs.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['item','quantity','unit_cny','total_cny','basis'])
 for n,q,v,b in costs:w.writerow([n,q,v,round(q*v,2),b])
 w.writerow(['One 15 percent project contingency',1,round(.15*subtotal,2),round(.15*subtotal,2),'Applied once to pre-reserve subtotal'])
 w.writerow(['TOTAL',1,total,total,'Home-tier planning budget, not procurement approval'])
write('cost_summary.json',dict(subtotal_cny=subtotal,contingency_fraction=.15,total_cny=total,home_safety_package_cny=18000,no_purchase_or_contact=True,quote_status='Engineering allowances; current matched quotations unavailable'))

g=9.81;force=math.hypot(63,7.5);cm=9.5;items=[]
for side,arm,mass,reach,wrench in [('R','UR5e',20.7,.96,force),('L','xArm6',12.5,.81,8.58825)]:
 eoat=1.2 if side=='R' else 1.5
 moving=mass+eoat+3+cm
 staticF=moving*g+wrench+moving*.45
 staticM=(mass+eoat+3)*g*reach+cm*g*.225+wrench*reach+.523277+moving*.45*.225
 F=1.5*staticF;M=1.5*staticM
 reaction=F/4+M/(2*.34)+M/(2*.24)+M/(2*.24)
 items.append(dict(side=side,arm=arm,catalog_arm_mass_kg=mass,EOAT_kg=eoat,service_payload_kg=3,carriage_mass_kg=cm,moving_mass_kg=moving,lever_bound_m=reach,process_design_force_N=wrench,static_force_N=staticF,static_moment_Nm=staticM,factored_force_N=F,factored_moment_Nm=M,rail_900N_ratio=F/900,rail_650Nm_ratio=M/650,guide_block_combined_reaction_N=reaction,guide_C0_N=69070,guide_static_SF=69070/reaction,brake_1280N_static_ratio=(wrench+moving*.45)/1280,translational_energy_at_point2m_s_J=.5*moving*.2**2))
fixed_mass=2*51.16944+8+3.2+2*10+2*4.71+16+2*.85
wallF=sum(i['factored_force_N'] for i in items)+1.5*fixed_mass*g
# Conservative sum of absolute moments, not a signed FEA equilibrium solution.
ys=[.925,1.375]
wallM=sum(i['factored_moment_Nm']+i['factored_force_N']*y for i,y in zip(items,ys))+1.5*fixed_mass*g*max(ys)
padspan=.25
write('loads.json',dict(method='Whole-arm/EOAT/payload mass at full-reach lever; process proxy margin unchanged; additional 1.5 structural load factor. Absolute wrench sums are conservative demand bounds.',carriages=items,rail_geometry=dict(tubes_per_lane=2,each_section_y_z_wall_m=[.15,.05,.003],combined_envelope_m=[2.8,.30,.05],mass_each_lane_kg=51.16944,E_Pa=200e9,I_combined_m4=1.080584e-6,J_combined_m4=2.952635938e-6,support_x_m=[-1.82,-.62],travel_x_m=[-1.7,.2],operating_main_x_max_m=.045,largest_operating_overhang_m=.82),beam_bounds=dict(cantilever_end_F900N_sag_mm=900*.82**3/(3*200e9*1.080584e-6)*1000,cantilever_end_M650Nm_slope_deflection_mm=650*.82**2/(2*200e9*1.080584e-6)*1000,twist_650Nm_over_point82m_deg=math.degrees(650*.82/(77e9*2.952635938e-6))),wall=dict(fixed_structure_mass_kg=fixed_mass,force_bound_N=wallF,moment_bound_Nm=wallM,anchor_pads=2,anchors_per_pad=4,plate_size_m=[.10,.02,.30],anchor_row_spacing_m=padspan,conservative_pad_row_tension_N=wallM/(2*padspan),conservative_shear_per_anchor_N=wallF/8,anchor_status='Demand only: no substrate survey, concrete edge-distance/prying/pullout proof or anchor allowable capacity is claimed.'),brakes=dict(rail_candidate='Miki BXR-050-10LE spring-applied',motor_holding_Nm=3.2,reduction=10,pinion_m=.02,efficiency=.8,holding_N=1280,engagement_s=.06,engagement_status='R02 estimate, not certified timing',speed_m_s=.2,controlled_deceleration_m_s2=1,delay_travel_mm=12,controlled_stop_mm=20,reserved_stop_mm=50,arm_policy='OEM documented joint-brake/power-loss holding suffices under DECISIONS.md; rail brake and stopping test remain required'),limits='3kg is structural service sizing, not a claim every recipe pose or CoM is qualified at an extra3kg. Motor/gear/rotor inertia, support stiffness and exact joint mounting reaction require prototype proof.'))

power=[dict(item='UR5e main arm including OEM control box',moderate_W=200,design_W=570,basis='OEM datasheet moderate and maximum'),dict(item='xArm6 helper including OEM controller',moderate_W=200,design_W=500,basis='OEM typical and recommended supply; measured peak unavailable'),dict(item='R211 XL appliance',moderate_W=550,design_W=550,basis='OEM nameplate'),dict(item='Auxiliary cutter drive',moderate_W=150,design_W=150,basis='R02 drive allowance, unmeasured'),dict(item='Rails, EOAT, IPC, cameras and safety electronics',moderate_W=200,design_W=200,basis='R03 combined allowance, excludes arm controllers')]
peak=sum(x['design_W'] for x in power)
write('power.json',dict(items=power,simultaneous_nameplate_budget_W=peak,at230V_A=peak/230,at230V_current_with_point8_pf_A=peak/(230*.8),track='Dry fixed household track only for stationary appliances; OEM arm AC controllers fixed and OEM flex cables in independent covered chains',chain=dict(swept_cover_m=[2.4,.245,.025],horizontal_return_radius_m=.110,UR5e_selected_cable='166100 e-Series 6m hiflex,13.4mm OD',UR_dynamic_min_m=8*.0134,xArm_power_dynamic_min_m=.078,xArm_data_dynamic_min_m=.045,source='https://www.universal-robots.com/manuals/EN/HTML/SW10_14/Content/prod-cable/cable-product-description.htm',qualification='110mm exceeds107.2mm minimum; actual chain side-mount route, strains, thermal derating and OEM base-connector revision require installation proof'),protection='One inclusive home package: RCD/PE, E-stop, person pause/speed reduction and guarded appliance interlocks; no household moving pickup',unknowns=['Simultaneous acceleration/startup current, PF and harmonics','Track and circuit matched SKU/plug ampacity','Splash/grease ingress of full assembly','Wired stop integration and restart inhibition']))

# Serial planning ledger. No claimed measured or connected-motion preparation time.
timeline=[
 ('Stage/inspect raw inputs and enable water',60,'handling estimate'),
 ('Wash carrot, load nest and pick peeler',120,'handling/washing estimate; all surfaces'),
 ('Carrot12 peel strokes and12 helper indices',12*(.15/.02+15),'20mm/s peel speed assumption,15s/index handling'),
 ('Rinse carrot, clean peel land, install bowl',120,'handling estimate; dirty/clean separation'),
 ('Carrot end trims and terminal two5mm slices',4*.035/.0005,'Retained low-speed proxy qualification envelope0.5mm/s'),
 ('Carrot OEM disc feed and deliver',90,'OEM1500rpm;90s handling/output estimate, no inferred cutting force'),
 ('Wash potato, load nest and pick peeler',120,'handling/washing estimate'),
 ('Potato10 peel strokes and10 helper indices',10*(.08/.02+15),'20mm/s peel speed assumption,15s/index'),
 ('Potato eyes, rinse, clean and bowl install',180,'60s eyes assumption; variable vision count'),
 ('Potato end trims, longitudinal split, terminal slices',2*.070/.0005+.090/.0005+4*.070/.0005,'Retained low-speed auxiliary0.5mm/s; two halves'),
 ('Potato OEM disc feed and collection',90,'handling/output estimate'),
 ('Potato three fresh-water rinses and drain',3*30+30,'Three changes;30s drain, retain all edible solids'),
 ('Bok choy coarse wash and root-disk trim',90+.070/.0005,'R02 greens force proxy; low-speed auxiliary'),
 ('Separate leaves and expose every crease',90,'reference meal handling assumption'),
 ('Fill inherited sink for submerged bok-choy soak',.6*.44*(.84-.65)*1000/6*60,'50.16L at6L/min, floor0.65m and water0.84m; serial conservative fill time'),
 ('Bok choy soak',600,'Ten minutes retained from reference'),
 ('Rub/inspect each crease, rinse and drain',150,'120s rub/inspection plus30s draining assumption'),
 ('Split wide stalks lengthwise',2*.170/.0005,'Reference planning assumption two wide stalks; vision-dependent count; all>15mm must be split'),
 ('Five40mm section cycles and bowl transfer',5*.030/.0005+60,'<=30mm bundle;0.5mm/s auxiliary proxy speed'),
 ('Wash tomato, remove hard core and load nest',150,'Handling/eye-core proxy retained'),
 ('Guarded eight-wedge cycle and bowl transfer',.060/.0005+60,'R02 tomato force proxy;0.5mm/s auxiliary'),
 ('Inspect all outputs, account edible yield',90,'All wedges/creases; ten distributed root slices;>=98percent yield'),
 ('Disassemble food parts, rinse/drain, clean, tool return and park',300,'Cleaning estimate includes blade underside, trough, nests, spoon, cups and bowls')]
t=0;rows=[]
for name,seconds,basis in timeline:rows.append(dict(operation=name,start_s=t,end_s=t+seconds,duration_s=seconds,basis=basis));t+=seconds
write('timeline.json',dict(reference_meal_kg=.57,reference_meal='one0.12kg carrot, one0.20kg potato,0.10kg bok choy, one0.15kg tomato',serial_planning_s=t,prep_min=round(t/60,2),verified_prep_min=None,rows=rows,parallel_schedule_claimed=False,status='Planning estimate; connected motion and physical cut/wash quality must pass before executable timing can be claimed.',sensitivity='Each additional wide stalk adds340s plus handling; each additional eye adds measured cycle time; soaking is included600s, not hidden overlap.'))

hashes={}
for source,copy in [('sim/r02/concept2/reference.py','sim/r03/integrator/reference.py'),('sim/r01/concept/model.py','sim/r03/integrator/oem_model.py')]:
 a=(ROOT/source).read_bytes();b=(ROOT/copy).read_bytes();hashes[source]=dict(source_sha256=hashlib.sha256(a).hexdigest(),copy_sha256=hashlib.sha256(b).hexdigest(),unchanged=a==b)
for source in ['DECISIONS.md','posts/r02/reviewer.md','posts/r02/concept2.md','posts/r02/tools.md','posts/r02/transport.md','posts/r01/reviewer.md']:
 hashes[source]=dict(sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),read_first=True)
(A/'source_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print('cost',total,'prep planning min',round(t/60,2),'power W',peak)
