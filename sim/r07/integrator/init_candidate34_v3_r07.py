"""Repair concrete faucet/inspection target obstructions without altered gates."""
import json,sys,runpy
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
c=json.loads((O/'layouts/L33.json').read_text())
c.update(id='L34',orientation='R07_v3_L34',electric_water_standby=[-.4,.075,1.08],inspection_standbys=[[.02,-.10,1.15],[-1.69,-.10,1.15]],colander_wash_shift_m=[.12,0,0],reason='L33 full geometry retained. L29 exact target certificates identify faucet-reservation and stale inspection-target obstructions. Move colander washing120mm right within unchanged basin, place output-inspection vantages in front of relocated outputs, and replace unnecessary knob-approach motions by a fixed map-supported empty-hand standby for the real NC electric valve. Foods, forces, tools, tolerances and gaps unchanged. Nominal faucet angle is an explicit initial-state assumption, not an all-swivel guarantee.')
(O/'layouts/L34.json').write_text(json.dumps(c,indent=2))
p=json.loads((O/'layouts/L33_park_full.json').read_text());p.update(config=c,pass_=False,warm_start_only=True);(O/'layouts/L34_park_full.json').write_text(json.dumps(p,indent=2))
sys.argv=['candidate_v3_r07.py','L34'];runpy.run_path(str(H/'candidate_v3_r07.py'))
