from v7_common import *
import hashlib,collections
R=H.parents[2];p05=json.loads((I.parents[1]/'r05/integrator/results/process_v3.json').read_text());p07=read('process_v7.json')
tool_diff=[]
for n,a in p05['tools'].items():
    b=p07['tools'][n]
    for key in set(a)|set(b):
        if a.get(key)!=b.get(key):tool_diff.append(dict(tool=n,field=key,old=a.get(key),new=b.get(key)))
src=[]
for n in ['DECISIONS.md','posts/r05/integrator.md','posts/r05/reviewer.md','posts/r04/reviewer.md','posts/r07/integrator.md']+[f'posts/r07/reviewer_v{i}.md' for i in range(1,7)]:
    file=R/n;src.append(dict(file=n,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
rows=[json.loads(f.read_text()) for f in (I/'results/connections_v7/L101').glob('*.json')];legs=[l for r in rows for l in r['legs']]
planner=dict(connections=len(rows),legs=len(legs),min_allocated_s=min(l['allocated_budget_s'] for l in legs),allocated_s=sum(l['allocated_budget_s'] for l in legs),actual_s=sum(r['actual_planner_s'] for r in rows),all_planners_ran=all(l['planner']['states_checked']>0 for l in legs),failed_min_restarts=min(l['planner']['seeds_tried'] for l in legs if not l['planner']['ok']),statuses=dict(collections.Counter(r['status'] for r in rows)),geometric_connections=sum(r['geometric_connection_pass'] for r in rows),conditional_pass=sum(r['pass_'] for r in rows),working_permission_counts=[r['working_permissions_on_connection'] for r in rows])
audit=read('delivery_audit.json');events=[]
for r in audit['slot_intervals']:events.extend([(r['acquired_unix'],1),(r['released_unix'],-1)])
active=peak=0
for _,d in sorted(events):active+=d;peak=max(peak,active)
code=(I/'safety_v7_r07.py').read_text();code=code[:code.index("(H/'results/safety_v7.json')")];space={'__file__':str(I/'safety_v7_r07.py')};exec(compile(code,'reviewer_safety','exec'),space)
wash=[]
for idx in (33,43):
    ch=v.scene(idx);h=v.items[idx][1]['poses'][0]['R'];rot=ch.target_rotation(h,0)@Rotation.from_euler('xyz',h.get('object_rotation_deg',[0,0,0]),degrees=True).as_matrix()
    shape=next(g for g in p07['tools']['colander']['geometry'] if g['name']=='colander_shell')
    offset=np.array(shape['center_m'])-np.array(shape['axis_local'])*shape['height_m']/2
    mouth=np.array(h['pos'])+rot@offset;jet=np.array(v.cfg['replacement_faucet']['wash_reference_pos_m']);radial=np.linalg.norm((mouth-jet)[:2]);radius=shape['radius_m']-shape['thickness_m'];tol=.005+2*np.linalg.norm(offset)*math.sin(math.radians(3)/2)
    wash.append(dict(index=idx,mouth_m=mouth.tolist(),jet_m=jet.tolist(),radial_offset_mm=float(radial*1000),radius_mm=radius*1000,pose_movement_mm=tol*1000,miss_even_with_tolerance=bool(radial-tol>radius)))
internal=read('motion.json')['internal_paths'];rank=[dict(index=r['index'],robot_reserve_mm=r['final_replay']['clearance_distribution'].get('robot_environment',{}).get('min_mm',1e9)) for r in internal if r['ok']]
dump('engineering.json',dict(source_hashes=src,tools_changes=tool_diff,planner=planner,integrator_max_workers=peak,safety_logic=space['out'],wash=wash,tightest_robot_internal=min(rank,key=lambda r:r['robot_reserve_mm']),internal_pass=sum(r['ok'] for r in internal),force_model_count=len(p07['force_models']),forces_unchanged=p05['force_models']==p07['force_models'],finished_products_unchanged=p05['finished_products']==p07['finished_products'],force_sources=[x for x in p07['source_catalog'] if x['id'] in ['F01','F02','F03','F04']]))
print('ENGINEERING',planner,'tools_changes',tool_diff,'worker_peak',peak,flush=True)
