"""Map-guided second station iteration; no tool or fixture sizes change."""
from pathlib import Path
import json,copy
H=Path(__file__).resolve().parent;O=H/'results'
c=json.loads((O/'layouts/L21.json').read_text());c.update(id='L26',orientation='R07_v3_L26',reason='L21 map admits low downward targets atY=.075/.22 on left counter. Move raw tray to front and three full output bowls behind it; move all three complete tool docks to left counter column. This frees top-down approach space and sink-centre parking after faucet replacement.')
c['station_overrides']={
 'raw':dict(new_center=[-1.63,.17,0]),
 'output_carrot':dict(new_center=[-1.69,.44,0]),
 'output_potato':dict(new_center=[-1.445,.44,0]),
 'output_leafy_greens':dict(new_center=[-1.17,.44,0]),
 'output_tomato':dict(new_center=[.02,.43,0]),
 'dock_peeler':dict(new_center=[-.90,.085,0]),
 'dock_wash_pad':dict(new_center=[-.90,.285,0]),
 'dock_eye_core_spoon':dict(new_center=[-.90,.485,0]),
}
(O/'layouts/L26.json').write_text(json.dumps(c,indent=2))
p=json.loads((O/'layouts/L18_park_full.json').read_text());p.update(config=c,pass_=False,warm_start_only=True)
(O/'layouts/L26_park_full.json').write_text(json.dumps(p,indent=2));print('L26 map-guided station revision created')
c=copy.deepcopy(c);c.update(id='L27',orientation='R07_v3_L27',reason='L21 exact fixed-part audit cleared principal but found helper/handle barrier. Shift the same complete swept faucet toY=.19 at left sink side; retain L26 map-guided front raw/rear bowls and left tool docks. Nominal outlet remains inside sink; full140deg sweep is retained even beyond counter front.')
c['replacement_faucet']['deck_xy_m']=[-.765,.19]
(O/'layouts/L27.json').write_text(json.dumps(c,indent=2));p.update(config=c);(O/'layouts/L27_park_full.json').write_text(json.dumps(p,indent=2));print('L27 forward-side faucet iteration created')
c=copy.deepcopy(c);c.update(id='L28',orientation='R07_v3_L28',chain_centres_z=[1.2905,1.3255],reason='L21 populated park missed10mm wrist/chain gap by2.287mm. Raise BOTH unchanged25mm chain covers by3mm, retaining10mm between chains and12mm below cabinet doors. Combine forward-side faucet and map-guided L26 station layout; all OEM solids and acceptance gates unchanged.')
(O/'layouts/L28.json').write_text(json.dumps(c,indent=2));p.update(config=c);(O/'layouts/L28_park_full.json').write_text(json.dumps(p,indent=2));print('L28 chain-height correction created')
