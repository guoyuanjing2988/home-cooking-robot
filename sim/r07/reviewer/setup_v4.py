from pathlib import Path
H=Path(__file__).resolve().parent
for name in ('common','reverify','internal','idle','envelopes','rules'):
    t=(H/f'v3_{name}.py').read_text()
    t=t.replace('v3_common','v4_common').replace('results_v3','results_v4').replace('audit_v3','audit_v4').replace("'L34'","'L53'").replace('L34 mount','L53 mount').replace('runtime_v2_r07','runtime_v4_r07').replace('static_v2','static_v4').replace('motion_v2','motion_v4').replace("for side in ('R','L')","for side in ('R',)").replace('v.scene(104)','v.scene(len(v.items)-1)')
    if name=='internal':
        t=t.replace("idx=int(sys.argv[1]);", "idx=int(sys.argv[1]);")
        t=t.replace("static_seed=w['k'];w=copy.deepcopy(w)","static_seed=w['k'];w=copy.deepcopy(saved.get('endpoint_witness',w))")
        t=t.replace("w['k']=int(np.argmin(branch_scores))", "w['k']=saved.get('jaw_axis_branch',int(np.argmin(branch_scores)))")
    if name=='rules':
        t=t.replace("p07=read('process_v3.json')", "p07=read('process_v4.json')")
        start=t.index('def ownership(st,e):');end=t.index("with (I/'results/costs.csv')",start)
        t=t[:start]+'''def ownership(st,e):
    held=st['arm']; own=st['owners']
    if held and own.get(held)!='R':owners.append([e,held,own.get(held)])
    for obj,owner in own.items():
        if owner=='R' and held!=obj:owners.append([e,obj,held])
for e in seq['events']:
    if e.get('state_before') is not None:
        if e['state_before']!=previous:chain.append(e['id'])
        ownership(e['state_before'],e['id'])
    if e.get('state_after') is not None:previous=e['state_after'];ownership(previous,e['id'])
''' +t[end:]
    (H/f'v4_{name}.py').write_text(t,encoding='utf-8')
print('v4 reviewer adapters created')
