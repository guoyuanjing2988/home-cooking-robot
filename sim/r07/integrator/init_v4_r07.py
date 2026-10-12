"""Six night studies. Source R05 modules and historical layouts are untouched."""
import json,copy,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
base=json.loads((O/'layouts/L35.json').read_text())
variants=[
 ('L36',{},[-.58,.60,.94],[-1.53,.205], 'Lower fixed spout at left basin; full chain covers down10mm/back10mm; M5 left-front.'),
 ('L37',dict(height=1.155,helper_height=1.182596),[-.22,.60,.94],[-1.53,.205], 'Lower both shoulders20mm and shift fixed jet to right; more door reserve.'),
 ('L38',dict(mount_deg=100,height=1.175,front_mount_y=.47),[-.58,.60,.94],[-1.53,.205], 'Principal100deg,30mm stand-off increase; test forward approaches.'),
 ('L39',dict(mount_deg=80,height=1.175,front_mount_y=.50),[-.22,.60,.92],[.43,.205], 'Principal80deg and low right jet; exchange full peeler and processor bays.'),
 ('L40',dict(mount_deg=120,height=1.15,front_mount_y=.46),[-.58,.60,.92],[.43,.205], 'Principal120deg lower/forward mount, appliance bay exchange.'),
 ('L41',dict(arm='xArm6+xArm6',arms=['xArm6','xArm6'],mount_deg=155.143,height=1.202596,front_mount_y=.49),[-.22,.60,.92],[-1.53,.205], 'Compact5kg xArm6 principal comparison; 3kg plus existing EOAT qualification retained as a separate required gate.'),
]
for ID,delta,faucet,m5,reason in variants:
 c=copy.deepcopy(base);c.update(height=1.175,helper_height=1.202596,front_mount_y=.50,helper_y=.49,chain_y=.3725,chain_centres_z=[1.2805,1.3155]);c.update(delta)
 c.update(id=ID,orientation='R07_v4_'+ID,reason=reason,night_v4=True,robustness_objective_extra_gap_mm=10)
 c['replacement_faucet']['wall_connection_m']=faucet;c['replacement_faucet']['wash_reference_pos_m']=[faucet[0],.43,faucet[2]-.045]
 c['m5_center_xy']=m5
 c['station_overrides'].update(raw={'new_center':[-.955,.16,0]},peel={'new_center':[-1.19,.135,-.147]},secondary={'new_center':[.035,.145,0]},slicer={'new_center':[-1.53,.205,0] if m5[0]>0 else [.425,.205,0]})
 # Full bowls/tools stay on counter; shift high rear objects away from fold band.
 for prod,x in [('carrot',-1.69),('potato',-1.445),('leafy_greens',-1.18),('tomato',.04)]:c['station_overrides']['output_'+prod]={'new_center':[x,.115,0]}
 for typ,y in [('peeler',.12),('wash_pad',.31),('eye_core_spoon',.49)]:c['station_overrides']['dock_'+typ]={'new_center':[-.865,y,0]}
 c['electric_water_standby']=[-.4,.075,1.08]
 (O/'layouts'/f'{ID}.json').write_text(json.dumps(c,indent=2))
 p=json.loads((O/'layouts/L34_park_full.json').read_text());p.update(config=c,pass_=False,warm_start_only=True)
 (O/'layouts'/f'{ID}_park_full.json').write_text(json.dumps(p,indent=2))
print('Created L36-L41; full geometry, no tolerance changes')
