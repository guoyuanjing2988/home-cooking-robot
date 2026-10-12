"""L31: full-size station swap guided by L29 wrist collision evidence."""
from pathlib import Path
import json,copy
H=Path(__file__).resolve().parent;O=H/'results'
c=json.loads((O/'layouts/L29.json').read_text())
c.update(id='L31',orientation='R07_v3_L31',reason='L29 peel witnesses reach both poses but wrist collides with adjacent BFP610 envelope. Swap full-size low peeling fixture and secondary cutter: peel left at(-1.17,.14), secondary right at(.05,.13). Preserve all solids, forces, thresholds and L29 rail/faucet geometry; map-guided station separation hypothesis.')
c['station_overrides']['peel']={'new_center':[-1.17,.14,-.147]}
c['station_overrides']['secondary']={'new_center':[.05,.13,0]}
(O/'layouts/L31.json').write_text(json.dumps(c,indent=2))
p=json.loads((O/'layouts/L29_park_full.json').read_text());p.update(config=c,pass_=False,warm_start_only=True)
(O/'layouts/L31_park_full.json').write_text(json.dumps(p,indent=2))
print('L31 full-size fixture swap created; warm park requires replay')
