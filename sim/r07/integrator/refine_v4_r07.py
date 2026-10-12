"""React to full machine/chain conflict: far-right M5 and smaller guard studies."""
import json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results'
for i in range(36,42):
 ID='L'+str(i);f=O/'layouts'/f'{ID}.json';c=json.loads(f.read_text())
 c['station_overrides']['raw']={'new_center':[-.875,.16,0]}
 c['station_overrides']['peel']={'new_center':[-1.22,.145,-.147]}
 for prod,x in [('carrot',-1.69),('potato',-1.445),('leafy_greens',-1.18),('tomato',.04)]:c['station_overrides']['output_'+prod]={'new_center':[x,.487,0]}
 if i<38:c['m5_center_xy']=[-1.62,.19]
 elif i<40:
  c['m5_center_xy']=[1.6325,.205];c['station_overrides']['slicer']={'new_center':[.425,.205,0]}
  c['reason']+='; move full M5 to333mm far-right counter bay beyond rail/chain, test long reach instead of retaining known rail interference.'
 else:
  c['peeler_model']='Rotato Express';c['m5_center_xy']=[-1.635,.155];c['station_overrides']['slicer']={'new_center':[.425,.205,0]}
  c['reason']+='; substitute actual Rotato Express commodity candidate within a full300x300x350mm guarded design reservation; supplier dimensions and OEM loading limits separately sourced, interface unqualified.'
 f.write_text(json.dumps(c,indent=2))
 for script in ('setup_stations_v2_r07.py','process_v4_r07.py'):subprocess.run([sys.executable,'-B',script,ID],check=True,timeout=30)
print('Six commodity and mount studies updated before static work')
