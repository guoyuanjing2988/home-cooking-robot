from v2_common import *
import collections
p=read('process_v3.json');ledger=read('intended_contacts.json')['rows'];expected=[dict(phase=ph['id'],stroke=sg['label'],pose=i,side=side,**c) for ph in p['phases'] for sg in ph['segments'] for i,hands in enumerate(sg['poses']) for side,h in hands.items() for c in h.get('contacts',[])]
a=collections.Counter(json.dumps(r,sort_keys=True) for r in ledger);b=collections.Counter(json.dumps(r,sort_keys=True) for r in expected)
rows=[]
for i in (14,18,24):
    data=read(f'motion_v2/{v.ID}/internal_{i}.json');ch=v.scene(i);allq=np.array([q for e in data['edges'] for q in e['path']]);rows.append(dict(index=i,max_principal_joint_range_rad=float(max(np.ptp(allq[:,ch.qa[n]]) for n in s.ck.ARMS['R'])),principal_carriage_range_m=float(np.ptp(allq[:,ch.qa['R_carriage_x']])),helper_joint_range_rad=float(max(np.ptp(allq[:,ch.qa[n]]) for n in s.ck.ARMS['L']))))
schedule=read('schedule.json');times={x['index']:x['duration_s'] for x in schedule['accepted_internal_paths']};timing=[]
for i in (14,18,24):
    x=json.loads((O/f'internal_{i}.json').read_text());timing.append(dict(index=i,independent_s=x['duration_s'],submitted_s=times[i],delta_s=abs(times[i]-x['duration_s'])))
dump('metadata.json',dict(stale_ledger_rows=[json.loads(x) for x in (a-b).elements()],current_replacements=[json.loads(x) for x in (b-a).elements()],substantive_changed_declarations=sum((a-b).values()),active_declarations=len(expected),paired_motion=rows,timing=timing,local_duration_sum_s=sum(r['independent_s'] for r in timing)))
print('METADATA',rows,timing,flush=True)
