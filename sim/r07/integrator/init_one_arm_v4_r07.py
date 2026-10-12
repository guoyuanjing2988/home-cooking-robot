"""Remove the helper as an entire physical arm, not a scaled collision model."""
import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
c=json.loads((O/'layouts/L36.json').read_text());c.update(id='L42',orientation='R07_v4_L42',arm='UR5e',count=1,peeler_model='Rotato Express',m5_center_xy=[-1.635,.155],reason='After L36-L41 commodity/mount screens: helper-index strokes are eliminated by appliance concept, so remove entire helper arm/carriage/chain. Keep full UR5e and its3kg+1.2kg service capability. One lane, no passing needed. Native removed helper has no ghost geometry, mass or joints. Appliance interfaces still unqualified.')
c['station_overrides']['dock_wash_pad']={'new_center':[.285,.485,0]};c['station_overrides']['dock_eye_core_spoon']={'new_center':[.53,.485,0]}
(O/'layouts/L42.json').write_text(json.dumps(c,indent=2))
for script in ('setup_stations_v2_r07.py','process_v4_r07.py'):
 subprocess.run([sys.executable,'-B',script,'L42'],check=True,timeout=30)
env=json.loads((O/'layouts/L36_envelope.json').read_text());env['config']=c;env['envelope_Nm']={k:v for k,v in env['envelope_Nm'].items() if k.startswith('R_')};env['reuse_proof']=[env['reuse_proof'][0]]
(O/'layouts/L42_envelope.json').write_text(json.dumps(env,indent=2))
p=json.loads((O/'layouts/L34_park_full.json').read_text());p.update(config=c,q=p['q'][:11],pass_=False,warm_start_only=True)
(O/'layouts/L42_park_full.json').write_text(json.dumps(p,indent=2))
for src,dst in [('least_analytic_v2_r07.py','least_analytic_v4_r07.py'),('collision_ik_v2_r07.py','collision_ik_v4_r07.py'),('mink_v3_r07.py','mink_v4_r07.py')]:
 t=(H/src).read_text().replace("for s in ('R','L')","for s in v.s.model.SIDES").replace('from search_distance_v2_r07 import hits as proposal_hits','from robust_search_v4_r07 import hits as proposal_hits')
 (H/dst).write_text(t)
t=(H/'static_v4_r07.py').read_text().replace('from collision_ik_v2_r07','from collision_ik_v4_r07').replace('from least_analytic_v2_r07','from least_analytic_v4_r07').replace('from mink_v3_r07','from mink_v4_r07').replace("for side in ('R','L')","for side in v.s.model.SIDES").replace("for s in ('R','L')","for s in v.s.model.SIDES")
t=t.replace('start=time.monotonic();deadline=start+20;', 'start=time.monotonic();deadline=start+20;ch.night_robust=seed>=48;')
(H/'static_v4_r07.py').write_text(t)
print('L42 one physical UR5e, full-size EOAT,59 robot strokes')
