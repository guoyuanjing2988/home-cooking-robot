"""Correct event expansion without discarding unchanged path measurements."""
import json,sys,subprocess,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'results';ID=sys.argv[1]
def read(n):return json.loads((O/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={p:sha(p) for p in (O/'motion_v4'/ID).glob('*.json')}
schedule=read('schedule.json');clear=read('clearance.json');initial_hash=sha(H/'models/persistent_meal.xml')
assert schedule['layout']==clear['layout']==ID
for script in ('sequence_v4_r07.py','prepare_delivery_v4_r07.py'):subprocess.run([sys.executable,'-B',str(H/script),ID],check=True,timeout=120)
assert initial_hash==sha(H/'models/persistent_meal.xml') and all(sha(p)==s for p,s in before.items())
new=read('schedule.json')
for key in ('accepted_internal_paths','isolated_path_sum_s','timing_method'):new[key]=schedule[key]
(O/'schedule.json').write_text(json.dumps(new,indent=2,allow_nan=False))
new=read('clearance.json')
for key in ('path_state_minimum_reserve_distributions','selected_path_fresh_replay','refined_reserve_assessment'):
 if key in clear:new[key]=clear[key]
(O/'clearance.json').write_text(json.dumps(new,indent=2,allow_nan=False))
(O/'sequence_revision_v4.json').write_text(json.dumps(dict(layout=ID,corrections=['Exact load/unload matching prevents duplicate peeler cycles','Three expanded potato rinses produce three water-change events and one drain','Explicit valve ordering for washes, soaking and draining'],events=len(read('state_sequence.json')['events']),initial_geometry_and_all_motion_hashes_unchanged=True,meal_executed=False),indent=2))
print('LEDGER_REFRESH_COMPLETE',len(read('state_sequence.json')['events']))
