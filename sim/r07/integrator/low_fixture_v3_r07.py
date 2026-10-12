"""Reorient full180mm supports; do not shorten fixture or arm collision solids."""
from pathlib import Path
import json,copy
H=Path(__file__).resolve().parent;O=H/'results';c=json.loads((O/'layouts/L28.json').read_text())
c.update(id='L29',orientation='R07_v3_L29',reason='L28 preserves the original raised peel fixture whose TCP1.205m leaves little wrist room below cabinet. Reorient all four unchanged180x18x18mm support bars horizontally on counter; tray bottom .868m, top .888m, peel land top .958m. Full working assembly and all targets translate down147mm; sourced63N peel force and arm/tool solids unchanged.',peel_horizontal_supports=True)
c['station_overrides']['peel']={'new_center':[.05,.13,-.147]}
(O/'layouts/L29.json').write_text(json.dumps(c,indent=2))
p=json.loads((O/'layouts/L21_park_full.json').read_text());p.update(config=c,pass_=False,warm_start_only=True)
(O/'layouts/L29_park_full.json').write_text(json.dumps(p,indent=2));print('L29 full-size horizontal-support fixture created')
c=copy.deepcopy(c);c.update(id='L30',orientation='R07_v3_L30',front_mount_y=.545,height=1.17,rail_centres_z=[1.295,1.295],reason='Move90deg principal mount55mm rearward and15mm down relative L28, raise rail5mm within band. This separates the fixed shoulder from full-height counter fixtures while keeping OEM base below rail beam. Retain full-size horizontal peel supports, front raw/rear output stations and forward-side faucet. Hypothesis needs paired maps and full scene replay; no geometry shrunk.')
(O/'layouts/L30.json').write_text(json.dumps(c,indent=2));p.update(config=c);(O/'layouts/L30_park_full.json').write_text(json.dumps(p,indent=2));print('L30 rear/lower mount with higher rail created')
