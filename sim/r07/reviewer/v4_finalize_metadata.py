from pathlib import Path
import json
H=Path(__file__).resolve().parent;O=H/'results_v4'
# The inherited two-arm aggregation used all(moving.values()). With one arm,
# that means arm movement, not overlap. Correct only this reporting field.
p=H/'v4_internal.py';t=p.read_text();t=t.replace("sum(all(x.values()) for x in moving)","sum(len(x)>1 and all(x.values()) for x in moving)");p.write_text(t,encoding='utf-8')
for p in O.glob('internal_*.json'):
    d=json.loads(p.read_text());d['simultaneous_moving_segments']=0;d['active_arm_count']=1;p.write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
p=O/'envelopes.json';d=json.loads(p.read_text());d['helper_task_cap_kg']=None;d['helper_EOAT_kg']=None;d['active_arm_count']=1;d['unused_helper_witnesses']='Not admitted or replayed: helper is absent from L53 compiled model.';p.write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
print('single-arm reporting metadata corrected; no numerical acceptance changed')
