import json,math
from pathlib import Path
H=Path(__file__).resolve().parent;g=9.81;items=[]
for side,arm,mass,reach,wrench in [('R','UR5e',20.7,.96,math.hypot(63,7.5)),('L','xArm6',12.5,.81,8.58825)]:
 eoat=1.2 if side=='R' else 1.5;carriage=10.9;moving=mass+eoat+3+carriage
 F=1.5*(moving*g+wrench+moving*.45)
 M=1.5*((mass+eoat+3)*g*reach+carriage*g*.40+wrench*reach+.523277+moving*.45*.40)
 reaction=F/4+M/(2*.34)+2*M/(2*.24)
 items.append(dict(side=side,arm=arm,moving_mass_kg=moving,EOAT_kg=eoat,service_payload_kg=3,carriage_adapter_drive_kg=carriage,process_force_N=wrench,factored_force_N=F,factored_moment_Nm=M,rail_900N_ratio=F/900,rail_650Nm_ratio=M/650,guide_block_reaction_N=reaction,guide_C0_N=69070,guide_static_SF=69070/reaction,rail_brake_1280N_static_ratio=(wrench+moving*.45)/1280))
fixed=2*51.16944+8+3.2+20+9.42+16+1.7+.4;ys=[1.1,1.55]
wallF=sum(x['factored_force_N'] for x in items)+1.5*fixed*g
wallM=sum(x['factored_moment_Nm']+x['factored_force_N']*y for x,y in zip(items,ys))+1.5*fixed*g*max(ys)
L=2.02;EI=200e9*1.080584e-6
out=dict(schema='r04.structural-demand.v1',status='DEMAND_ONLY_NOT_SITE_QUALIFIED',method='R03 worst full-reach gravity/process/inertial bounds retained; adapter grows1.4kg per carriage and setback175mm; additional structural1.5 factor. No reduction of force proxy.',carriages=items,rail=dict(original_full_section_y_z_m=[.3,.05],support_x_m=[-1.84,.18],span_m=L,travel_x_m=[-1.7,.2],main_operating_max_m=.045,E_Pa=200e9,I_combined_m4=1.080584e-6,simply_supported_900N_midspan_deflection_mm=900*L**3/(48*EI)*1000,conservative_650Nm_couple_deflection_bound_mm=650*L**2/(8*EI)*1000,limits='Simple beam demand bound, not torsion/adapter/connection FEA, dynamics, support settlement or calibrated pose proof. Deflection must fit the unchanged5mm pose budget.'),wall=dict(fixed_structure_mass_kg=fixed,factored_force_bound_N=wallF,factored_moment_bound_Nm=wallM,plates=2,anchors_per_plate=4,row_spacing_m=.25,row_tension_bound_N=wallM/(2*.25),shear_per_anchor_N=wallF/8,qualification='Conditional reinforced-concrete/masonry engineering only: survey substrate, edge/spacing, group effects, prying, installation and pull tests. No generic household wall admits these loads.',isolated_anchor_source='https://assets.hilti.com/api/public/content/5001533-original?v=21685e67'),portal_fallback=dict(required_on_weak_wall=True,nominal_R03_structure_kg=160.65888,R04_geometry_allowance_cny=61000,status='Retained cost/load fallback; site floor/ceiling/anti-tip layout and new mounts not independently qualified'),brakes=dict(arm_policy='DECISIONS: documented OEM power-loss holding in installed orientation, not missing continuous torque',rail='de-energize-to-apply; R03 spring-applied1280N candidate; actual stop/holding test required',safety_package_cny=18000))
(H/'results/loads.json').write_text(json.dumps(out,indent=2));print('wall force',wallF,'moment',wallM,'row tension',wallM/.5)
