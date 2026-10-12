from pathlib import Path
import json
H=Path(__file__).resolve().parent
for name in ('common','reverify','internal','idle','envelopes','rules'):
 t=(H/f'v4_{name}.py').read_text().replace('v4_common','v5_common').replace('results_v4','results_v5').replace('audit_v4','audit_v5').replace("'L53'","'L73'").replace('runtime_v4_r07','runtime_v5_r07').replace('static_v4','static_v5').replace('motion_v4','motion_v5').replace('process_v4.json','process_v5.json')
 if name=='rules':
  t=t.replace("sg['poses'][0].values()", "[h for pose in sg['poses'] for h in pose.values()]")
  t=t.replace("q=np.array(witness['poses'][0]['q']) if witness else ch.m.qpos0.copy();hs=sg['poses'][0]", "pi=next(pi for pi,hs in enumerate(sg['poses']) if any(h['held']==typ and any(c['kind']=='working_stroke' for c in h.get('contacts',[])) for h in hs.values()));q=np.array(witness['poses'][pi]['q']) if witness else ch.m.qpos0.copy();hs=sg['poses'][pi]")
  t=t.replace("seq=read('state_sequence.json');previous=seq['initial_state'];chain=[];owners=[]", "seq=read('state_sequence.json');previous=seq.get('initial_state');chain=[];owners=[]")
 if name=='idle':t=t.replace("data['fold_paths']", "data.get('fold_paths',[])")
 (H/f'v5_{name}.py').write_text(t,encoding='utf-8')
(H/'results_v5').mkdir(exist_ok=True);(H/'audit_v5').mkdir(exist_ok=True)
I=H.parent/'integrator'
for n in ('idle.json','state_sequence.json','persistent_model.json','schedule.json','clearance.json','fresh_admission.json'):
 d=json.loads((I/'results'/n).read_text());print(n, list(d))
print('created v5 adapters')
