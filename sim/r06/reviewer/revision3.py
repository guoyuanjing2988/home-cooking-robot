"""Independent third-delivery replay. All output stays in reviewer/v3."""
import sys, types, json, math, copy, hashlib, difflib, itertools, csv
from pathlib import Path
import numpy as np
import mujoco
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]; UP=ROOT/'sim/r06/integrator'; OUT=HERE/'v3'; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(UP))
# Reuse reviewer-owned independent equations, not submitted acceptance calls.
src=(HERE/'revision2.py').read_text().split('task=sys.argv[1]')[0]
src=src.replace("OUT=HERE/'v2'","OUT=HERE/'v3'").replace('import rescue_cell as rc','import station_spec as rc').replace(';V=17',';V=32')
src=src.replace("base.SUPPORTS={'wash_basin':{'wash_open_land'},'process_cell':{'process_open_land'}}", "base.SUPPORTS={'wash_basin':{'wash_open_land_-1','wash_open_land_1'},'process_cell':{'process_open_land'}}")
src=src.replace("selected={'T01_grasp','T01_release','T04_grasp','T04_release','T08_grasp','T08_release','T11_grasp','T11_release'}", "selected={f'T{i:02d}_{a}' for i in (1,3,5,7) for a in ('grasp','release')}")
src=src.replace('obligations=150','obligations=140')
mod=types.ModuleType('review_v3_helpers');mod.__file__=str(HERE/'revision2.py');exec(compile(src,mod.__file__,'exec'),mod.__dict__)
rc=mod.rc;base=mod.base
# The new pan has real coplanar gland feet. Verify ancestry, not a name wildcard.
perm=(HERE/'review.py').read_text().split('def own_permissions(ch,q):')[1].split('\ndef gaps(')[0]
perm=perm.replace('if not name.startswith(pref):continue', '''canonical='R_held_'+name
            if canonical not in ch.gnames:continue
            b=int(ch.m.geom_bodyid[ch.gnames.index(canonical)]);owned=False
            while b:
                if ch.m.body(b).name=='R_held_'+owner:owned=True;break
                b=int(ch.m.body_parentid[b])
            if not owned:continue''')
exec('def own_permissions(ch,q):'+perm,base.__dict__)
PH=mod.PH; PRE=mod.PRE
PH['selected_witnesses']=[dict(r['witness'],stroke=r['id'],job=r['job']) for r in PH['obligations'] if r['pass_']]
read=mod.read;save=mod.save;sha=mod.sha

def physical_hits(ch,row,q):
    if row is None:return []
    active=row['active'];key=tuple(sorted(active))
    if getattr(ch,'review_active_key',None)!=key:
        ch.review_active_key=key
        ch.review_pairs=np.array([(a,b) for a in range(ch.m.ngeom) for b in range(a) if not ch.robot[a] and not ch.robot[b] and ch.weld[a]!=ch.weld[b] and (a in active or b in active)],dtype=int).reshape(-1,2)
    pairs=ch.review_pairs
    if not len(pairs):return []
    a,b=pairs.T;near=np.linalg.norm(ch.d.geom_xpos[a]-ch.d.geom_xpos[b],axis=1)<=ch.m.geom_rbound[a]+ch.m.geom_rbound[b]+.002
    bad=[]
    for g,h in pairs[near]:
        gap=mujoco.mj_geomDistance(ch.m,ch.d,int(g),int(h),.002,None)
        if gap < -1e-6 and ch.bounds.pair(int(g),int(h))['lower_m']<=1e-6:bad.append(dict(pair=[ch.gnames[g],ch.gnames[h]],signed_gap_mm=float(gap*1000)))
    return bad
mod.physical_hits=physical_hits
def active(ch,path):
    delta=np.max(np.abs(np.array(path)-path[0]),axis=0);roots={int(ch.m.jnt_bodyid[j]) for j in range(ch.m.njnt) if ch.m.jnt_type[j] in (2,3) and delta[ch.m.jnt_qposadr[j]]>1e-12};out=set()
    for g in range(ch.m.ngeom):
        b=int(ch.m.geom_bodyid[g])
        while b:
            if b in roots:out.add(g);break
            b=int(ch.m.body_parentid[b])
    return out

def paths():
    rows=[]
    for p in PRE['paths']:
        ch=mod.from_xml(p)
        if not p['ok']:
            w=p['mechanical_blocker'];q=w['q'];hits,mins,mm=base.gaps(ch,np.array(q));bad=physical_hits(ch,{'active':set(range(ch.m.ngeom))},q)
            rows.append(dict(id=p['id'],scope='actual_rejected',complete_path_available=False,submitted_pass=False,collision_reproduced=bool(hits or bad),robot_hits=hits,physical_hits=bad,alternative_planner=p.get('alternative_planner')))
        else:
            mech={'active':active(ch,p['path'])} if p['id'].startswith('P') and p['id']!='P01_robot_park' else None
            rr=mod.replay(ch,p['path'],mech,True);rr.update(id=p['id'],scope='actual_prefix',submitted_pass=True,duration_s=p['duration_s']);rows.append(rr)
            print('PATH',p['id'],rr['pass_'],rr['states_checked'],flush=True)
        save('paths',rows)

def mechanisms():
    data=read(UP/'results/mechanism_motion.json');ch=mod.from_xml({'xml':data['xml']});rows=[]
    for i,r in enumerate(data['rows']):
        path=[r['start_q'],r['requested']];rr=mod.replay(ch,path,{'active':active(ch,path)},True);rr.update(id=r['id'],scope='conditional_diagnostic',submitted_pass=r['pass_'],actual_credit=False,predecessors_pass=r['predecessors_pass']);rows.append(rr)
        save('mechanisms',rows);print('MECH',i,r['id'],rr['pass_'],rr['states_checked'],flush=True)

def audit():
    files=[p for folder in ('sim/r06/integrator','sim/r06/stations','sim/r04/integrator','sim/r05/integrator','inputs') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/'DECISIONS.md',ROOT/'posts/r06/integrator.md',ROOT/'posts/r06/stations.md']
    save('source_hashes_before',{str(p.relative_to(ROOT)):sha(p) for p in files});diffs=[]
    for rnd in ('r04','r05'):
        for b in (UP/('upstream_'+rnd)).glob('*.py'):
            a=ROOT/'sim'/rnd/'integrator'/b.name
            if not a.exists():continue
            d=''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True)));(OUT/(rnd+'_'+b.name+'.diff')).write_text(d);diffs.append(dict(round=rnd,file=b.name,identical=not d,sha256=sha(b)))
    (OUT/'input_reference.diff').write_text(''.join(difflib.unified_diff((ROOT/'inputs/prep_checker.py').read_text(encoding='utf-8-sig').splitlines(True),(UP/'upstream_r04/reference.py').read_text().splitlines(True))))
    row=PH['selected_witnesses'][0];job=row['job'];loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];ch=rc.Workcell(32,job['object_id'],loc);q=np.array(next(p['q'] for p in row['poses'] if p['label']=='retained_on_own_support'));original=ch.window(job['object_id'],job['station'],job['origin']);probes=[]
    for label,change in [('baseline',{}),('wrong_support',{'support_id':'dock_tomato'}),('wrong_object',{'object_id':'output_tomato'}),('wrong_face',{'face':'process_open_land'}),('wrong_normal',{'normal':[1,0,0]}),('nonunit',{'normal':[0,0,2]}),('working_on_transit',{'kind':'working_stroke'})]:
        ch.contact_windows=copy.deepcopy(original)
        for w in ch.contact_windows:w.update(change)
        ch.pose(q);mujoco.mj_forward(ch.m,ch.d);probes.append(dict(label=label,allowed=[sorted(x) for x in rc.permitted(ch)]))
    old=mujoco.MjModel.from_xml_path(str(UP/'history/v2/models/overview.xml'));new=rc.Workcell(32).m;geom=[]
    for g in range(old.ngeom):
        name=old.geom(g).name
        if not name.startswith(('R_geom_','R_eoat_','pan_','food_','key_','lid_','insert_')):continue
        try:ng=new.geom(name).id
        except KeyError:geom.append(dict(name=name,replaced=True));continue
        geom.append(dict(name=name,replaced=False,type_equal=old.geom_type[g]==new.geom_type[ng],size_equal=bool(np.allclose(old.geom_size[g],new.geom_size[ng],atol=1e-12))))
    wins=[dict(stroke=r['stroke'],**w) for r in PH['selected_witnesses'] for w in rc.Workcell(32,r['job']['object_id'],r['job']['locations']).window(r['job']['object_id'],r['job']['station'],r['job']['origin'])]
    for p in PRE['paths']:
        wins.extend(dict(path=p['id'],**w) for w in p.get('contact_windows',[]))
        if p.get('capture_window'):wins.append(dict(path=p['id'],**p['capture_window']))
    save('audit',dict(reference_diffs=diffs,contact_probes=probes,geometry=geom,acceptance=rc.SPEC['acceptance'],windows=wins,missing_identity=[w for w in wins if not all(k in w for k in ('kind','object_id','support_id'))],working_windows=[w for w in wins if w['kind']=='working_stroke']))
    print('AUDIT',len(diffs),'reference files',len(wins),'windows',flush=True)

def conservation():
    mod.conservation()
    # FK verifies actual carrier motion, every lid/jaw/axis and ownership seams.
    rows=[]
    def physical(xml,q):
        m=mujoco.MjModel.from_xml_path(str(UP/xml));d=mujoco.MjData(m);d.qpos[:]=q;mujoco.mj_forward(m,d)
        return {m.geom(g).name.removeprefix('R_held_'):(d.geom_xpos[g].copy(),d.geom_xmat[g].copy()) for g in range(m.ngeom)}
    for p in PRE['paths']:
        if not p['ok']:continue
        i=next(i for i,s in enumerate(PRE['states']) if s['event']==p['id']);errors=[]
        for q,s in ((p['path'][0],PRE['states'][i-1]),(p['path'][-1],PRE['states'][i])):
            a=physical(p['xml'],q);b=physical(s['xml'],s['q']);assert a.keys()==b.keys();errors.append(dict(position_m=max(np.linalg.norm(a[n][0]-b[n][0]) for n in a),rotation_matrix=max(np.max(abs(a[n][1]-b[n][1])) for n in a)))
        rows.append(dict(id=p['id'],pass_=max(x[k] for x in errors for k in x)<1e-5,errors=errors))
    save('seams',rows);print('CONSERVATION',len(PRE['states']),'states',len(rows),'path seams')

def auxiliary():
    # Adapt the earlier independent timing/envelope audit to the five actual
    # actuator motions. Recompute synchronized rest-to-rest profiles; include
    # Hessian point-acceleration terms on every moving arm segment.
    source=(HERE/'revision2.py').read_text().split('def auxiliary():')[1].split('\ndef metrics():')[0]
    source=source.replace("if p.get('mechanism_evidence'):","if p['id'].startswith('P') and p['id']!='P01_robot_park':")
    start=source.index("    joint='lid_carrot_joint'")
    end=source.index('    continue',start)+len('    continue')
    source=source[:start]+'''    # Saved actuator paths contain tiny increments, but the submitted drive
    # timing is one synchronized profile over the complete commanded travel.
    continue'''+source[end:]
    at=source.index('  timing.append(')
    source=source[:at]+'''  if p['id'].startswith('P') and p['id']!='P01_robot_park':
   delta=abs(np.array(p['path'][-1])-p['path'][0]);limits=[]
   for j in range(ch.m.njnt):
    if ch.m.jnt_type[j] not in (2,3):continue
    x=delta[ch.m.jnt_qposadr[j]]
    if x>1e-14:limits.append((x,.15 if ch.m.jnt_type[j]==3 else .005,.30 if ch.m.jnt_type[j]==3 else .010))
   speed=min(v/x for x,v,a in limits);acc=min(a/x for x,v,a in limits)
   total=2/math.sqrt(acc) if 1<=speed*speed/acc else 1/speed+speed/acc
'''+source[at:]
    source=source.replace(" for p in PRE['paths']:\n", " for p in PRE['paths']:\n  if not p['ok']:continue\n")
    source=source.replace("None if p.get('mechanism_evidence') else maxacc", "None if p['id'].startswith('P') and p['id']!='P01_robot_park' else maxacc")
    exec('def aux3():'+source,mod.__dict__);mod.aux3()
    # Food contract verifies this particular partition; its generic transition
    # function is deliberately adversarially checked for missing geometry gates.
    import station_food as sf
    ledger=sf.Ledger();kids=copy.deepcopy(sf.carrot_partition())
    for child in kids:child['owner']='output_carrot';child['center_relative_original_m']=[100.,100.,100.]
    accepted=False
    try:ledger.transform('carrot',kids,{'id':'unbound_boolean','pass_':True},'test');accepted=True
    except ValueError:pass
    save('food_contract_probe',dict(remote_same_owner_children_accepted=accepted,scope='Isolated in-memory negative test, never a committed meal state',missing_checks=['Bind stroke identity/product/parent/plane to saved checked motion','Require nonnegative child mass, positive sizes, spatial containment and disjoint partition','Derive child pose/ownership from actual parent and retained support']))
    print('AUXILIARY complete; remote child geometry accepted:',accepted)

def loading():
    rows=[]
    for r in PH['selected_witnesses']:
        job=r['job'];loc=copy.deepcopy(job['locations']);loc[job['object_id']]=job['origin'];ch=rc.Workcell(32,job['object_id'],loc)
        p=next(p for p in r['poses'] if p['label']=='retained_on_own_support');q=np.array(p['q'])
        for case in ('load_insert','key_latch'):
            hs=rc.hand(ch,ch.pose(q)[0],case);ratio,grip,_=base.loads(ch,q,hs)
            rows.append(dict(stroke=r['stroke'],case=case,torque_ratio=ratio,grip_margin=grip,pass_=ratio<=1 and grip>=1))
    save('supplemental_loading',dict(scope='Independent endpoint sensitivity using the unchanged stations loading/latch design forces; no executed process qualification',rows=rows,max_torque_ratio=max(r['torque_ratio'] for r in rows),min_grip_margin=min(r['grip_margin'] for r in rows)))
    # Read-only manufacturer PDF review, no document editing.
    sys.path.insert(0,str(ROOT/'sim/r04/integrator/vendor/pdfdeps'))
    import fitz
    d=fitz.open(UP/'v3/vendor/xarm_manual_v230.pdf');d[192].get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(OUT/'xarm_payload_page193.png')
    save('catalog_pages',dict(smc_url='https://www.smcworld.com/catalog/Electric-en/mpv/Electric-LEF_en/data/Electric-LEF_en.pdf',smc_sha256=sha(UP/'v3/vendor/smc_lefs.pdf'),xarm_url='https://www.ufactory.cc/wp-content/uploads/2024/01/xArm-User-Manual-V2.3.0.pdf',xarm_sha256=sha(UP/'v3/vendor/xarm_manual_v230.pdf'),xarm_payload_pdf_page_1based=193))
    print('LOADING',len(rows),'rows',max(r['torque_ratio'] for r in rows),min(r['grip_margin'] for r in rows))

def metrics():
    paths=read(OUT/'paths.json');mechs=read(OUT/'mechanisms.json');stat=read(OUT/'statics.json');strokes=read(OUT/'strokes.json');ok=[p for p in paths if p.get('pass_')];allok=ok+[p for p in mechs if p['pass_']]
    def dist(vals):return dict(n=len(vals),min_mm=min(vals),p5_mm=float(np.percentile(vals,5)),median_mm=float(np.median(vals)),p95_mm=float(np.percentile(vals,95)),fraction_ge10=sum(x>=10-1e-5 for x in vals)/len(vals))
    costs=list(csv.DictReader((UP/'results/costs.csv').open()));total=sum(float(r['line_cny']) for r in costs);before=read(OUT/'source_hashes_before.json')
    save('metrics',dict(static_score=[stat['passed'],PH['total']],stroke_replays=[sum(r['pass_'] for r in strokes),len(strokes)],prefix_connections=[len(ok),188],complete_trajectories_replayed=len(ok)+len(mechs),rejected_saved_state_replays=1,conditional_replay_passed=sum(r['pass_'] for r in mechs),nonstationary_replayed=sum(r['total_displacement_bound_m']>1e-8 for r in ok+mechs),states_checked=sum(p['states_checked'] for p in ok+mechs+strokes),max_point_step_mm=max(p['max_point_step_mm'] for p in allok+strokes),longest_prefix=max(ok,key=lambda p:p['total_displacement_bound_m'])['id'],longest_duration_prefix=max(ok,key=lambda p:p['duration_s'])['id'],tightest_prefix=min(ok,key=lambda p:p['minimum_reserve_mm'])['id'],static_reserve=dist([p['reserve_mm'] for r in stat['rows'] for p in r['poses']]),prefix_reserve=dist([v for p in ok for v in p['reserve_samples_mm']]),cost_cny=total,prefix_s=20+sum(p['duration_s'] for p in ok),prep_min=None,max_static_torque_ratio=max(p['torque_ratio'] for r in stat['rows'] for p in r['poses']),min_static_grip_margin=min(p['grip_margin'] for r in stat['rows'] for p in r['poses']),max_path_torque_ratio=max(p['max_torque_ratio'] for p in ok),upstream_files_changed=[p for p,h in before.items() if sha(ROOT/p)!=h]))
    print((OUT/'metrics.json').read_text())

def delivery():
    import re
    post=ROOT/'posts/r06/reviewer.md';text=post.read_text(encoding='utf-8-sig');checks=[]
    def check(name,ok,details=None):checks.append(dict(name=name,pass_=bool(ok),details=details))
    check('Chinese_summary_first',text.startswith('中文摘要'))
    check('nine_numbered_findings',len(re.findall(r'^\d+\. \*\*(?:BLOCKING|HIGH|MEDIUM)',text,re.M))==9)
    missing=[]
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if not target.startswith(('http','#','C:')) and not (post.parent/target.split('#')[0]).exists():missing.append(target)
    check('local_links_exist',not missing,missing)
    check('eight_strokes',len(read(OUT/'strokes.json'))==8 and all(r['pass_'] for r in read(OUT/'strokes.json')))
    check('sixteen_static_obligations',read(OUT/'statics.json')['passed']==16)
    paths=read(OUT/'paths.json');mechs=read(OUT/'mechanisms.json')
    check('fourteen_prefix_connections',sum(r.get('pass_',False) for r in paths)==14)
    check('thirty_diagnostics_five_failures',len(mechs)==30 and sum(r['pass_'] for r in mechs)==25)
    check('conservation_and_seams',read(OUT/'conservation.json')['pass_'] and all(r['pass_'] for r in read(OUT/'seams.json')))
    check('point_displacement',all(r['max_point_step_mm']<=4.000000001 for r in paths+mechs+read(OUT/'strokes.json') if 'max_point_step_mm' in r))
    before=read(OUT/'source_hashes_before.json');changed=[p for p,h in before.items() if sha(ROOT/p)!=h];check('upstream_unchanged',not changed,changed)
    source_diff=[];source_count=0
    for p in (UP/'sources/ur5e').rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        old=UP/'history/v2/sources/ur5e'/p.relative_to(UP/'sources/ur5e')
        if old.exists():
            source_count+=1
            if sha(old)!=sha(p):source_diff.append(str(p.relative_to(UP)))
    check('arm_source_files_unchanged_from_v2',not source_diff,dict(files=source_count,differences=source_diff))
    # Full non-welded appliance assembly check in the actual initial scene.
    ch=mod.from_xml(PRE['states'][0]);q=np.array(PRE['states'][0]['q']);base.gaps(ch,q);bad=physical_hits(ch,{'active':set(range(ch.m.ngeom))},q);check('actual_initial_appliance_assembly_nonpenetrating',not bad,bad)
    size=sum(p.stat().st_size for p in (ROOT/'sim/r06').rglob('*') if p.is_file());check('total_R06_under_3GiB',size<3*1024**3,size)
    logs=[read(p) for p in (HERE/'audit').glob('v3_*_run.json')];check('numerical_resource_limits',all(r['exit_code']==0 and r['peak_process_MiB']<1900 and r['elapsed_s']<1100 and r['cpu_only'] for r in logs))
    edges=sorted([(r['start_monotonic_s'],1) for r in logs]+[(r['end_monotonic_s'],-1) for r in logs]);running=peak=0
    for t,delta in edges:running+=delta;peak=max(peak,running)
    check('at_most_four_workers',peak<=4,peak)
    save('delivery',dict(pass_=all(c['pass_'] for c in checks),checks=checks,post_sha256=sha(post),post=str(post.relative_to(ROOT)),numerical_runs=len(logs),total_R06_bytes=size,summary=dict(strokes='16/140',connections='14/188',meal='fail',prep_min=None,cost_cny=354775,proceed=False,findings=9)))
    print(json.dumps(dict(pass_=all(c['pass_'] for c in checks),failed=[c for c in checks if not c['pass_']],total_R06_GiB=size/1024**3,max_concurrent_workers=peak)))

{'audit':audit,'statics':mod.statics,'paths':paths,'mechanisms':mechanisms,'conservation':conservation,'auxiliary':auxiliary,'loading':loading,'metrics':metrics,'delivery':delivery}[sys.argv[1]]()
