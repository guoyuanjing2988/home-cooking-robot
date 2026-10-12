from common import *
import hashlib,difflib,collections,xml.etree.ElementTree as E,csv
import policy_r05 as pol
from planner_r05 import Planner
R05=I.parents[1]/'r05/integrator'
audit=H/'audit';audit.mkdir(exist_ok=True)
hashes=[]
for p in sorted((I/'upstream').glob('*.py')):
    paths=[R05/p.name,I/p.name,p];hs=[hashlib.sha256(q.read_bytes()).hexdigest() for q in paths]
    hashes.append(dict(name=p.name,sha256=hs,identical=len(set(hs))==1))
for name in ('reference.py','final_check.py','distance.py','solver.py','planner_r05.py','motion_r05.py','point_bound.py','model.py'):
    a=(R05/name).read_text();b=(I/name).read_text();(audit/(name+'.diff')).write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='r05/'+name,tofile='r07/'+name)),encoding='utf-8')
src=[]
for p in sorted((R05/'sources').rglob('*')):
    if p.is_file() and '__pycache__' not in str(p):
        q=I/'sources'/p.relative_to(R05/'sources')
        if q.exists():src.append(dict(file=str(p.relative_to(R05)),match=hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(q.read_bytes()).digest()))
p05=json.loads((R05/'results/process_v3.json').read_text());p07=read('process_v3.json')
groups={k:p05.get(k)==p07.get(k) for k in ('acceptance','tools','finished_products','force_models','forces','installed_geometry') if k in p05}
ledger=read('intended_contacts.json')['rows'];bad=[];expected=[]
for ph in p07['phases']:
    for sg in ph['segments']:
        for pi,hands in enumerate(sg['poses']):
            for side,h in hands.items():
                for c in h.get('contacts',[]):
                    if c.get('kind') not in ('grasp_release_support','working_stroke') or c.get('object_id')!=rt.object_identity(h) or c.get('support_id')!=c['face']:bad.append(dict(phase=ph['id'],stroke=sg['label'],pose=pi,side=side,contact=c))
                    expected.append(dict(phase=ph['id'],stroke=sg['label'],pose=pi,side=side,**c))
probes=[]
for typ in ('eye_core_spoon','wash_pad','root_food'):
    idx=next(i for i,(ph,sg,key) in enumerate(mo.items) if any(h['held']==typ and any(c['kind']=='working_stroke' for c in h.get('contacts',[])) for h in sg['poses'][0].values()))
    ph,sg,key=mo.items[idx];ch=mo.scene(ph,sg,idx);q=np.array(read('final_static/'+str(idx)+'.json')['poses'][0]['q']);hs=sg['poses'][0]
    ws=mo.windows(ch,q,hs);w=next(w for w in ws if w['kind']=='working_stroke');ch.contact_windows=ws
    ch.working_stroke=False;nonwork=pol.valid_window(ch,w);pl=Planner(ch,hs,seed=807,seconds=65);pl.state(q)
    leaks=[c for c in ch.allowed if c.get('face')==w['face'] and c.get('side')==w['side']]
    ch.working_stroke=True;working=pol.valid_window(ch,w);wrong=pol.valid_window(ch,dict(w,object_id='wrong'));forged=pol.valid_window(ch,dict(w,kind='grasp_release_support'))
    ch.working_stroke=False
    probes.append(dict(index=idx,tool=typ,work_window_on_transit=nonwork,actual_planner_work_leaks=leaks,valid_work=working,wrong_object=wrong,forged_support=forged,pass_=not nonwork and not leaks and working and not wrong and not forged))
ch=mo.scene(*mo.items[0][:2],0);q=np.array(read('park_full.json')['q']);ch.d.qpos[:]=q;mujoco.mj_forward(ch.m,ch.d);f.contacts(ch,q)
walls=[]
wall=ch.gnames.index('north_wall');wallface=ch.d.geom_xpos[wall,1]-ch.m.geom_size[wall,1]
for g,n in enumerate(ch.gnames):
    if ch.robot[g]:
        rear=ch.bounds.support(g,np.array([0.,1.,0.]))[1];allowed=pol.wall_mating(ch,g)
        if allowed:
            oldp=ch.d.geom_xpos[g].copy();oldr=ch.d.geom_xmat[g].copy();ch.d.geom_xpos[g,1]+=.001;penetration=pol.wall_mating(ch,g)
            ch.d.geom_xpos[g]=oldp;ch.d.geom_xmat[g]=Rotation.from_euler('z',.01).as_matrix().ravel();rotation=pol.wall_mating(ch,g);ch.d.geom_xmat[g]=oldr
        else:penetration=rotation=None
        walls.append(dict(name=n,wall_gap_mm=float((wallface-rear)*1000),mating_permission=allowed,one_mm_penetration_permission=penetration,rotation_permission=rotation))
# Compare compiled source arm geometry and inertia against unchanged R05 XML.
a=mujoco.MjModel.from_xml_path(str(R05/'models/witnesses/Q01__water_on.xml'));b=ch.m;geos=[];bodies=[]
an={mujoco.mj_id2name(a,mujoco.mjtObj.mjOBJ_GEOM,i):i for i in range(a.ngeom)}
for j,n in enumerate(ch.gnames):
    if n not in an or not n.startswith(('R_geom','L_geom','R_gripper','L_gripper','R_finger','L_finger')):continue
    i=an[n];same=a.geom_type[i]==b.geom_type[j] and np.array_equal(a.geom_size[i],b.geom_size[j])
    if a.geom_type[i]==7:
        mi=int(a.geom_dataid[i]);mj=int(b.geom_dataid[j]);va=a.mesh_vert[a.mesh_vertadr[mi]:a.mesh_vertadr[mi]+a.mesh_vertnum[mi]];vb=b.mesh_vert[b.mesh_vertadr[mj]:b.mesh_vertadr[mj]+b.mesh_vertnum[mj]];same &= np.array_equal(va,vb)
    geos.append(dict(name=n,unchanged=bool(same)))
bn={mujoco.mj_id2name(a,mujoco.mjtObj.mjOBJ_BODY,i):i for i in range(a.nbody)}
for j in range(b.nbody):
    n=mujoco.mj_id2name(b,mujoco.mjtObj.mjOBJ_BODY,j)
    if n in bn and n.startswith(('R_','L_')) and not any(x in n for x in ('carriage','mount')):
        i=bn[n];bodies.append(dict(name=n,unchanged=bool(a.body_mass[i]==b.body_mass[j] and np.array_equal(a.body_inertia[i],b.body_inertia[j]) and np.array_equal(a.body_ipos[i],b.body_ipos[j]))))
seq=read('state_sequence.json');previous=seq['initial_state'];chain=[];owners=[]
compiled=[]
for row in bodies:
    n=row['name'];ai=bn[n];bi=b.body(n).id;ag=np.flatnonzero(a.geom_bodyid==ai);bg=np.flatnonzero(b.geom_bodyid==bi);same=len(ag)==len(bg);details=[]
    for i,j in zip(ag,bg):
        ok=all(np.array_equal(getattr(a,key)[i],getattr(b,key)[j]) for key in ('geom_type','geom_size','geom_pos','geom_quat'))
        if a.geom_type[i]==7:
            mi=int(a.geom_dataid[i]);mj=int(b.geom_dataid[j]);va=a.mesh_vert[a.mesh_vertadr[mi]:a.mesh_vertadr[mi]+a.mesh_vertnum[mi]];vb=b.mesh_vert[b.mesh_vertadr[mj]:b.mesh_vertadr[mj]+b.mesh_vertnum[mj]];ok &= np.array_equal(va,vb)
        details.append(bool(ok));same &= ok
    compiled.append(dict(body=n,source_geom_count=len(ag),r07_geom_count=len(bg),all_unchanged=bool(same),geom_checks=details))
inst05={r['name']:r for r in p05['installed_geometry']};inst07={r['name']:r for r in p07['installed_geometry']};dimchanges=[];moves=[]
for n,g in inst05.items():
    if n in inst07:
        h=inst07[n]
        if any(g.get(k)!=h.get(k) for k in ('type','size','radius_m','height_m','thickness_m')):dimchanges.append(n)
        if g.get('pos')!=h.get('pos'):moves.append(dict(name=n,from_pos=g.get('pos'),to_pos=h.get('pos')))
def ownership(st,e):
    for side,r in st['arms'].items():
        obj=r['held']
        if obj:
            own=st['food'][obj[5:]]['owner'] if obj.startswith('food:') else st['objects'][obj]['owner']
            if own!=side:owners.append([e,side,obj,own])
    for prod,r in st['food'].items():
        if r['owner'] in ('R','L') and st['arms'][r['owner']]['held']!='food:'+prod:owners.append([e,prod])
    for obj,r in st['objects'].items():
        if r['owner'] in ('R','L') and st['arms'][r['owner']]['held']!=obj:owners.append([e,obj])
for e in seq['events']:
    if e.get('state_before') is not None:
        if e['state_before']!=previous:chain.append(e['id'])
        ownership(e['state_before'],e['id'])
    if e.get('state_after') is not None:previous=e['state_after'];ownership(previous,e['id'])
with (I/'results/costs.csv').open(encoding='utf-8-sig',newline='') as z:cost=list(csv.DictReader(z))
base=sum(float(r['total_cny']) for r in cost if r['item'] not in ('TOTAL','One15percent project reserve'));reserve=round(base*.15,2)
result=dict(code_hashes=hashes,code_match=all(r['identical'] for r in hashes),source_files=len(src),source_mismatches=[r for r in src if not r['match']],parsed_groups_equal=groups,reference_sha256=hashlib.sha256((I/'reference.py').read_bytes()).hexdigest(),contact_declarations=len(ledger),ledger_exact_match=ledger==expected,contact_errors=bad,contact_kinds=dict(collections.Counter(c['kind'] for c in ledger)),work_probes=probes,wall_robot_pairs=walls,source_geoms=geos,source_inertias=bodies,meal=dict(events=len(seq['events']),motion_events=sum(e.get('motion_required',False) for e in seq['events']),expanded_strokes=len(seq['expanded_strokes']),expanded_connections=len(seq['expanded_connections']),chain_errors=chain,ownership_errors=owners,initial_food_mass_kg=sum(p['input_mass_kg'] for p in p07['finished_products']),executable=read('persistent_model.json')['executable']),cost=dict(base_cny=round(base,2),reserve_cny=reserve,total_cny=round(base+reserve,2),safety_rows=[r for r in cost if r['item']=='Inclusive home-safety package'],safety_count=sum(r['item']=='Inclusive home-safety package' for r in cost)),active_forbidden_storage_geoms=[n for n in ch.gnames if any(x in n for x in ('elevator','pallet','header','front_leg','recess'))],process_top_keys=list(p07))
result.update(compiled_source_body_geoms=compiled,installed_dimension_changes=dimchanges,installed_moves=moves)
dump('rules.json',result);print('rules',result['code_match'],'windows',all(r['pass_'] for r in probes),'contacts',len(ledger),'owners',len(owners),'cost',result['cost']['total_cny'])
