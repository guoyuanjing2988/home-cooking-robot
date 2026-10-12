"""Independent R06 saved-witness review. Read-only upstream; bounded by run.py."""
import os
for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[n]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys,json,math,hashlib,ast,difflib,copy,argparse,time,csv
from pathlib import Path
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
UP=ROOT/'sim/r06/integrator'
sys.path.insert(0,str(UP))
import jobs as j
import cell as c
from distance import Bounds
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,allow_nan=False,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item() if isinstance(x,np.generic) else str(x)),encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def witnesses():
    out={}
    for p in sorted((UP/'results').glob('static_chunk_*.json'),key=lambda x:x.stat().st_mtime):
        for r in read(p)['rows']:
            if r['index']<len(j.JOBS) and r['job']['targets']==j.JOBS[r['index']]['targets']:out[r['index']]=r
    return out
W=witnesses()
CAP=read(UP/'results/torque_envelope.json')['envelope_Nm']

def own_required(ch,a,b):
    ma,mb=ch.robot[a],ch.robot[b]
    if not (ma or mb):return None
    wa,wb=map(int,(ch.weld[a],ch.weld[b]))
    if wa==wb or tuple(sorted((a,b))) in ch.acm:return None
    if ma and mb:
        if ch.m.body_weldid[ch.m.body_parentid[wa]]==wb or ch.m.body_weldid[ch.m.body_parentid[wb]]==wa:return None
        if ch.gripper(a) and ch.gripper(b) and ch.side(a)==ch.side(b):return None
        return (0.,'self') if ch.side(a)==ch.side(b) else (.01,'arm_arm')
    robot=a if ma else b
    return (.005,'held_gripper_environment') if ch.gripper(robot) or ch.held[robot] else (.010,'robot_environment')

SUPPORTS={'wash_basin':{'wash_lift_left','wash_lift_right'},'process_cell':{'cell_land_a','cell_land_b'},'inspection_dock':{'inspection_land'}}
def own_permissions(ch,q):
    # Independently validate OWN support/parts, face manifests and straight window.
    ch.pose(q);out=set();all_names=set(ch.gnames)
    p,rot=ch.pose(q)
    for w in ch.contact_windows:
        if w.get('kind') not in ('grasp_release_support','working_stroke') or w.get('object_id')!=ch.held_id:continue
        if w['kind']=='working_stroke' and not ch.working_stroke:continue
        owner=ch.held_id;sid=w.get('support_id')
        expected=SUPPORTS.get(sid,set())
        if sid=='dock_'+owner.removeprefix('output_'):expected={'dock_'+owner.removeprefix('output_')+'_land'}
        if w['face'] not in expected:continue
        pref='pan_'+owner.removeprefix('output_')+'_' if owner.startswith('output_') else 'clean_leaf_'
        axis=np.array(w['normal']);delta=p-np.array(w['tcp_origin_m']);t=float(delta@axis)
        if abs(np.linalg.norm(axis)-1)>1e-10 or np.linalg.norm(delta-t*axis)>2e-5 or not -2e-5<=t<=.05000001 or np.max(abs(rot-np.array(w['tcp_rotation'])))>.0002:continue
        for name in w['held_parts']:
            if not name.startswith(pref):continue
            pair=frozenset((w['face'],'R_held_'+name))
            if not pair<=all_names:continue
            a,b=(ch.gnames.index(n) for n in pair)
            if ch.bounds.pair(a,b)['lower_m']>=.005-1e-6:continue
            face=ch.gnames.index(w['face']);valid=ch.m.geom_type[face]==6
            for contact in ch.d.contact[:ch.d.ncon]:
                if contact.dist>0 or set(map(int,contact.geom))!={a,b}:continue
                R=ch.d.geom_xmat[face].reshape(3,3);local=R.T@(contact.pos-ch.d.geom_xpos[face]);normal=R.T@contact.frame[:3]
                valid &= abs(normal[2])>=.85 and local[2]>=ch.m.geom_size[face,2]-.00002
            if valid:out.add(pair)
    cw=getattr(ch,'capture_window',None)
    if cw and cw.get('kind')=='grasp_release_support' and cw.get('support_id')=='eoat_key_capture':
        owner=cw['object_id'];key='key_'+owner.removeprefix('output_') if owner.startswith('output_') else 'clean_leaf_key'
        axis=np.array(cw['normal']);delta=p-np.array(cw['tcp_origin_m']);t=delta@axis
        if np.linalg.norm(delta-t*axis)<=2e-5 and -2e-5<=t<=.05000001 and np.max(abs(rot-np.array(cw['tcp_rotation'])))<=.0002:
            for aa,bb in cw['pairs']:
                if aa not in (key,'R_held_'+key) or bb not in ('R_eoat_key_left','R_eoat_key_right'):continue
                a,b=(ch.gnames.index(n) for n in (aa,bb))
                if ch.bounds.pair(a,b)['lower_m']>=.005-1e-6:continue
                valid=True
                for contact in ch.d.contact[:ch.d.ncon]:
                    if contact.dist>0 or set(map(int,contact.geom))!={a,b}:continue
                    R=ch.d.geom_xmat[a].reshape(3,3);local=R.T@(contact.pos-ch.d.geom_xpos[a]);normal=R.T@contact.frame[:3]
                    valid &= abs(normal[0])>=.85 and abs(abs(local[0])-ch.m.geom_size[a,0])<=.00002
                if valid:out.add(frozenset((aa,bb)))
    return out

def gaps(ch,q):
    # Independent pair-policy implementation; retain original shapes and distance oracle.
    if not hasattr(ch,'review_bounds'):ch.review_bounds=Bounds(ch,own_required)
    ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d);mujoco.mj_comPos(ch.m,ch.d);mujoco.mj_collision(ch.m,ch.d)
    allowed=own_permissions(ch,q)
    mismatches=sorted([sorted(x) for x in allowed.symmetric_difference(c.permitted(ch))])
    for n,jid in ch.jid.items():
        if ch.m.jnt_type[jid] in (2,3) and ch.m.jnt_limited[jid]:
            lo,hi=ch.m.jnt_range[jid]
            if not lo-1e-9<=q[ch.qa[n]]<=hi+1e-9:return [{'pair':[n,'joint_limit']}],{},mismatches
    hits,mins,_=ch.review_bounds.check(frozenset(allowed))
    # Signed penetration witnesses are required even if dual lower bound is zero.
    for con in ch.d.contact[:ch.d.ncon]:
        a,b=map(int,con.geom);req=own_required(ch,a,b)
        if req is not None and frozenset((ch.gnames[a],ch.gnames[b])) not in allowed and con.dist<-.000001:
            hits.append(dict(pair=[ch.gnames[a],ch.gnames[b]],signed_gap_mm=float(con.dist*1000),required_mm=req[0]*1000))
    return hits,mins,mismatches

def loads(ch,q,hs):
    m,d=ch.m,ch.d;d.qpos[:]=q;d.qvel[:]=0;mujoco.mj_forward(m,d)
    bias=d.qfrc_bias.copy();jp=np.zeros((3,m.nv));jr=np.zeros_like(jp);jm=np.zeros_like(jp);jrm=np.zeros_like(jp)
    mujoco.mj_jacSite(m,d,jp,jr,m.site('R_work').id);mujoco.mj_jacSite(m,d,jm,jrm,m.site('R_mass').id)
    R=d.site_xmat[m.site('R_prep').id].reshape(3,3);h=hs['R'];gravity=np.array([0,0,-9.81*h['held_kg']]);rat=0.;gr=1e30;demand_rows=[]
    for force in h['check_forces_N']:
        F=np.array(force)
        for moment in h['check_moments_Nm']:
            M=np.array(moment);arm_M=M+np.cross(R@np.array(h['work_offset_m']),F)
            tau=bias-jp.T@F-jr.T@arm_M-jm.T@gravity
            demands={n:float(abs(tau[ch.da[n]])) for n in c.ARM}
            rat=max(rat,max(demands[n]/CAP[n] for n in c.ARM))
            netF=float(np.linalg.norm(F+gravity));netM=float(np.linalg.norm(np.cross(R@np.array(h['work_offset_m']),F)+np.cross(R@np.array(h['mass_offset_m']),gravity)+M))
            margin=min(150/(1.5*max(netF,1e-12)),15/(1.5*max(netM,1e-12)))
            gr=min(gr,margin);demand_rows.append(demands)
    return rat,gr,demand_rows

class IndependentBound:
    def __init__(self,ch):
        self.ch=ch;m=ch.m;self.rows=[];self.weights=np.zeros((m.ngeom,m.nq));self.slides=[]
        for geom in np.flatnonzero(ch.robot|ch.held):
            radius=float(np.linalg.norm(m.geom_pos[geom])+m.geom_rbound[geom]);body=int(m.geom_bodyid[geom]);distal=[]
            while body:
                for joint in range(int(m.body_jntadr[body]),int(m.body_jntadr[body]+m.body_jntnum[body])):
                    k=int(m.jnt_qposadr[joint]);typ=int(m.jnt_type[joint])
                    if typ==3:
                        self.weights[geom,k]=radius+np.linalg.norm(m.jnt_pos[joint]);self.rows.append((int(geom),joint,k,distal.copy()))
                    elif typ==2:self.weights[geom,k]=1
                    else:raise ValueError('Moving free/ball robot requires separate proof')
                    distal.append(k)
                local=list(range(int(m.body_jntadr[body]),int(m.body_jntadr[body]+m.body_jntnum[body])))
                radius+=np.linalg.norm(m.body_pos[body])+sum(max(abs(m.jnt_range[t])) for t in local if m.jnt_type[t]==2)+sum(2*np.linalg.norm(m.jnt_pos[t]) for t in local)
                body=int(m.body_parentid[body])
        self.slides=[int(m.jnt_qposadr[t]) for t in range(m.njnt) if m.jnt_type[t]==2]
    def segment(self,a,b):
        ch=self.ch;m=ch.m;dq=np.abs(np.array(b)-a);ch.pose(a);local=np.zeros(m.ngeom)
        for g,jid,k,distal in self.rows:
            radius=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[jid])+m.geom_rbound[g]
            radius+=sum(self.weights[g,t]*dq[t] for t in distal)
            local[g]+=radius*dq[k]
        local+=self.weights[:,self.slides]@dq[self.slides]
        return float(min(np.max(self.weights@dq),max(local)))

def replay(ch,path,hs,all_states=True):
    pb=IndependentBound(ch);orig=c.PointBound(ch);count=0;maxstep=0.;minreserve=1e30;maxratio=0.;mingrip=1e30;bad=None;bounderr=0.;reserve_values=[]
    for si,(a,b) in enumerate(zip(path,path[1:])):
        a=np.array(a);b=np.array(b);bound=pb.segment(a,b);bounderr=max(bounderr,abs(bound-orig.segment_bound(a,b)));n=max(1,math.ceil(bound/.004));maxstep=max(maxstep,bound/n)
        for k in range(n+1):
            q=a+(b-a)*k/n;count+=1;hits,mins,mismatch=gaps(ch,q);ratio,grip,_=loads(ch,q,hs)
            maxratio=max(maxratio,ratio);mingrip=min(mingrip,grip);rv=min((v['reserve_mm'] for cat,v in mins.items() if cat!='self'),default=0);minreserve=min(minreserve,rv);reserve_values.append(rv)
            if hits or mismatch or ratio>1 or grip<1:
                bad=dict(segment=si,k=k,q=q.tolist(),blockers=hits[:3],permission_mismatches=mismatch,torque_ratio=ratio,grip_margin=grip);break
        if bad:break
    return dict(pass_=bad is None,states_checked=count,max_point_step_mm=maxstep*1000,bound_disagreement_m=bounderr,min_reserve_mm=minreserve if reserve_values else None,max_torque_ratio=maxratio,min_grip_margin=mingrip,first_failure=bad,reserve_quantiles_mm={str(t):float(np.quantile(reserve_values,t/100)) for t in (0,5,25,50,75,95,100)} if reserve_values else {})

def provenance():
    copies=[]
    for p in read(UP/'audit/provenance.json'):
        a=ROOT/p['source'];b=UP/p['copy'];copies.append(dict(source=p['source'],copy=p['copy'],identical=a.read_bytes()==b.read_bytes(),sha256=digest(b)))
    # Explicit diffs against actual R04/R05, not a trust in a manifest.
    diffs=[]
    for round_ in ('r04','r05'):
        for b in (UP/('upstream_'+round_)).glob('*.py'):
            a=ROOT/'sim'/round_/'integrator'/b.name
            if not a.exists():continue
            text=''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True),fromfile=str(a),tofile=str(b)))
            (HERE/'audit'/f'{round_}_{b.name}.diff').write_text(text,encoding='utf-8');diffs.append(dict(round=round_,file=b.name,identical=not text))
    source=(ROOT/'inputs/prep_checker.py').read_text(encoding='utf-8-sig');ref=(UP/'upstream_r05/reference.py').read_text()
    (HERE/'audit/input_reference.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True),ref.splitlines(True),fromfile='inputs/prep_checker.py',tofile='R05 reference.py')),encoding='utf-8')
    ch=c.Cell(j.V);gxml={g.get('name'):g for g in c.E.fromstring(ch.xml).findall('.//worldbody//geom')};geometry=[]
    for body in c.SPEC['bodies']:
        for g in body['geometry']:
            n='R_mount_'+g['id'] if body['id']=='robot_pedestal' else g['id'];actual=gxml[n];wanted=np.array(g['size_m'])/2 if g['type']=='box' else np.array([g['radius_m'],g['height_m']/2]);size=np.fromstring(actual.get('size'),sep=' ')
            geometry.append(dict(name=n,source_size_m=wanted.tolist(),actual_size_m=size.tolist(),not_shrunk=bool(np.all(size>=wanted-1e-10)),same_type=actual.get('type')==g['type']))
    for g in c.SPEC['EOAT']['geometry']:
        actual=gxml['R_'+g['id']];geometry.append(dict(name='R_'+g['id'],not_shrunk=bool(np.allclose(np.fromstring(actual.get('size'),sep=' '),np.array(g['size_m'])/2))))
    raw=mujoco.MjModel.from_xml_path(str(UP/'sources/ur5e/ur5e.xml'));oem=[]
    for b in range(1,raw.nbody):
        rb=ch.m.body('R_arm_'+raw.body(b).name).id;oem.append(dict(body=raw.body(b).name,mass_equal=abs(raw.body_mass[b]-ch.m.body_mass[rb])<1e-12,inertia_equal=bool(np.allclose(raw.body_inertia[b],ch.m.body_inertia[rb],atol=1e-12)),com_equal=bool(np.allclose(raw.body_ipos[b],ch.m.body_ipos[rb],atol=1e-12))))
    declared=c.SPEC['intended_contacts'];windows=[]
    for job in j.JOBS:
        if job['held']:
            cc=j.load_cell(job)
            for w in cc.contact_windows:windows.append(dict(stroke=job['id'],**w))
    save('audit/provenance.json',dict(copies=copies,diffs=diffs,reference_sha256=digest(UP/'upstream_r05/reference.py'),station_and_eoat_geometry=geometry,oem_inertias=oem,acceptance=c.SPEC['acceptance'],source_window_count=len(declared),source_window_missing_fields=[w['id'] for w in declared if not all(k in w for k in ('kind','object_id','support_id'))],source_work_on_nonwork=[w['id'] for w in declared if w['kind']=='working_stroke' and w.get('non_working_paths_may_use')],expanded_windows=windows,working_retract_jobs=[x['id'] for x in j.JOBS if x['kind']=='working_stroke' and any(t in x.get('substep','') for t in ('retract','park'))],binding_hashes={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'DECISIONS.md',ROOT/'posts/r05/reviewer.md',ROOT/'posts/r04/reviewer.md',ROOT/'posts/r02/tools.md',ROOT/'inputs/cook_ref.md',ROOT/'inputs/keypose_cook.md',ROOT/'posts/r06/stations.md',ROOT/'posts/r06/integrator.md']}))
    print('PROVENANCE',len(copies),'copies',len(geometry),'geometry',len(windows),'windows',flush=True)

def static():
    rows=[]
    for i,job in enumerate(j.JOBS):
        if job['admission']!='full_robot_static':continue
        ch=j.load_cell(job);poses=[]
        for target,pose in zip(job['targets'],W[i]['selected']['poses']):
            q=np.array(pose['q']);p,R=ch.pose(q);err=np.linalg.norm(p-target)*1000;ang=np.linalg.norm(Rotation.from_matrix(ch.rot.T@R).as_rotvec())*180/math.pi
            hits,mins,mismatch=gaps(ch,q);hs=c.hand(ch,target,job['load']);rat,gr,_=loads(ch,q,hs);oldrat,oldgr,_=j.check_load(ch,q,hs)
            payload=1.2+hs['R']['held_kg']<=5 and np.linalg.norm(ch.com)+.09<=.35
            poses.append(dict(pass_=err<=5 and ang<=3 and not hits and not mismatch and rat<=1 and gr>=1 and payload,position_mm=err,orientation_deg=ang,torque_ratio=rat,grip_margin=gr,torque_disagreement=abs(rat-oldrat),grip_disagreement=abs(gr-oldgr),clearance=mins,blockers=hits[:3],permission_mismatches=mismatch))
        row=dict(index=i,id=job['id'],pass_=all(p['pass_'] for p in poses),submitted_pass=next(x['pass_'] for x in read(UP/'results/phase_summary.json')['strokes'] if x['index']==i),poses=poses);rows.append(row)
        print('STATIC',i,job['id'],row['pass_'],flush=True)
        save('results/static_replay.json',dict(rows=rows,strokes_passed=sum(r['pass_'] for r in rows),full_geometry_strokes=len(rows),all_obligations=len(j.JOBS),conditional_held_assembly_only=True))

def strokes():
    candidates=[(i,x) for i,x in enumerate(j.JOBS) if x['admission']=='full_robot_static' and next(z['pass_'] for z in read(UP/'results/phase_summary.json')['strokes'] if z['index']==i)]
    selected=['A02_grasp','A03_release','A14_grasp','A15_release','A29_grasp','A30_release','A35_grasp','A36_release'] if args.lo==0 else ['A17_grasp','A18_release','A44_grasp','A45_release']
    # First/last and four ingredients, plus the longest joint endpoint arc.
    ranked=[]
    for i,job in candidates:
        ch=j.load_cell(job);pb=IndependentBound(ch);p=W[i]['selected']['poses'];ranked.append((pb.segment(np.array(p[0]['q']),np.array(p[-1]['q'])),job['id']))
    longest=max(ranked)[1]
    if args.lo==0 and longest not in selected:selected.append(longest)
    rows=[]
    for i,job in candidates:
        if job['id'] not in selected:continue
        ch=j.load_cell(job);start=np.array(W[i]['selected']['poses'][0]['q']);p0,R=ch.pose(start);goal=np.array(job['targets'][-1]);n=max(1,math.ceil(np.linalg.norm(goal-p0)/.001));path=[start];errors=[]
        for k in range(1,n+1):
            q,e=ch.solve(p0+(goal-p0)*k/n,R,path[-1]);errors.append(e);path.append(q)
        r=replay(ch,path,c.hand(ch,job['targets'][0],job['load']));r.update(id=job['id'],index=i,cartesian_max_error_mm=max(e['position_mm'] for e in errors),cartesian_max_orientation_deg=max(e['orientation_deg'] for e in errors),scope='Independent IK continuation and full bounded support stroke; already-held condition')
        r['pass_'] &= r['cartesian_max_error_mm']<=.01 and r['cartesian_max_orientation_deg']<=.01;rows.append(r)
        print('STROKE',job['id'],r['pass_'],r['states_checked'],flush=True);save('results/stroke_replay.json' if args.lo==0 else f'results/stroke_replay_{args.lo}.json',dict(rows=rows,longest_endpoint_arc=longest,ranking=sorted(ranked,reverse=True)))

def motion(lo,hi):
    ds=read(UP/'results/motion.json')['isolated_loaded_connection_diagnostics'];ds.sort(key=lambda x:x['index']);rows=[]
    for r in ds[lo:hi]:
        job=next(x for x in j.JOBS if x['id']==r['from_']);ch=j.load_cell(job);ch.contact_windows=[]
        hs=c.hand(ch,job['targets'][-1],job['load']);q=np.array(r['last_rejection']['q']);hits,mins,mm=gaps(ch,q);rat,gr,_=loads(ch,q,hs)
        ja=next(i for i,x in enumerate(j.JOBS) if x['id']==r['from_']);jb=next(i for i,x in enumerate(j.JOBS) if x['id']==r['to']);dst=j.load_cell(j.JOBS[jb]);a=np.array(W[ja]['selected']['poses'][-1]['q']);destq=np.array(W[jb]['selected']['poses'][0]['q']);b=ch.q0.copy()
        for name in ch.qa:
            if name in dst.qa and ch.m.jnt_type[ch.jid[name]]==dst.m.jnt_type[dst.jid[name]]:
                count=7 if ch.m.jnt_type[ch.jid[name]]==0 else 1;b[ch.qa[name]:ch.qa[name]+count]=destq[dst.qa[name]:dst.qa[name]+count]
        direct=replay(ch,[a,b],hs);pb=IndependentBound(ch)
        row=dict(index=r['index'],from_=r['from_'],to=r['to'],reproduced_rejection=bool(hits or rat>1 or gr<1),hits=hits[:3],torque_ratio=rat,grip_margin=gr,permission_mismatches=mm,original_search_s=r['planner_time_s'],direct_endpoint_displacement_bound_m=pb.segment(a,b),independent_bounded_direct_replay=direct,scope='Saved full-scene rejected connection witness PLUS independent <=4mm direct endpoint route; no retained successful RRT route exists; no fresh RRT search claimed')
        rows.append(row);print('CONNECTION',r['index'],row['reproduced_rejection'],flush=True)
    save(f'results/connection_rejections_{lo}_{hi}.json',dict(rows=rows))

def prefix():
    prefix=read(UP/'results/executed_prefix.json');ch=c.Cell(j.V);rows=[];target=np.array(j.JOBS[1]['targets'][0]);cw=dict(kind='grasp_release_support',object_id='output_carrot',support_id='eoat_key_capture',normal=[0,0,1],tcp_origin_m=target.tolist(),tcp_rotation=ch.rot.tolist(),pairs=[['key_carrot','R_eoat_key_left'],['key_carrot','R_eoat_key_right']]);ch.capture_window=cw
    for path in prefix['paths']:
        r=replay(ch,path['path'],c.hand(ch,target));r['id']=path['id'];r['submitted_ok']=path['ok'];rows.append(r);print('PREFIX',path['id'],r['pass_'],r['states_checked'],flush=True)
    q=np.array(prefix['blocked']['witness']['q']);hits,mins,mm=gaps(ch,q);rows.append(dict(id='lower_to_key_rejected_next_sample',pass_=not hits,blockers=hits[:3],permission_mismatches=mm))
    save('results/prefix_replay.json',dict(rows=rows,scope='All accepted prefix states, all retained partial descent states, and rejected next sample; no attachment committed'))
    # Geometry and logical conservation at each accepted boundary, including every joint.
    phys=[]
    for state in prefix['physical_states']:
        model=mujoco.MjModel.from_xml_path(str(UP/state['xml']));d=mujoco.MjData(model);d.qpos[:]=state['q'];mujoco.mj_kinematics(model,d);containers=[]
        for name,detail in state['containers'].items():
            b=model.body(name).id;containers.append(dict(name=name,max_pose_error_m=float(np.linalg.norm(d.xpos[b]-detail['world_position_m'])),lid=detail['lid_joint_rad'],attached=detail['attached_to']))
        food=[]
        for name,owner in state['food_owners'].items():
            b=model.body(name).id;ancestor=b;chain=[]
            while ancestor:chain.append(model.body(ancestor).name);ancestor=int(model.body_parentid[ancestor])
            food.append(dict(name=name,owner=owner,own_parent_present=owner in chain,body_instances=sum(model.body(z).name==name for z in range(model.nbody)),mass_kg=state['food_mass_kg'][name],raw=True))
        phys.append(dict(after=state['after_path'],containers=containers,food=food,mass_kg=sum(state['food_mass_kg'].values()),every_joint_recorded=len(state['every_joint'])==model.njnt))
    proposed=[]
    for state in read(UP/'sources/state_ledger_A.json'):
        proposed.append(dict(mass_kg=sum(x['mass_kg'] for x in state['food'].values()),tokens=len(state['food'])))
    save('results/conservation.json',dict(physical_states=phys,logical_states=len(prefix['states']),proposed_states=proposed,meal_complete=False,accepted_outputs=prefix['states'][-1]['accepted_bowls'],no_actual_food_splits=True))

def service():
    ch=c.Cell(j.V);q=np.array(W[0]['selected']['poses'][0]['q']);jid=ch.jid['access_door_joint'];g=ch.gnames.index('access_door_panel');ch.pose(q);lever=np.linalg.norm(ch.d.geom_xpos[g]-ch.d.xanchor[jid])+ch.m.geom_rbound[g];n=math.ceil(1.55*lever/.004);minimum=1e30;bad=None
    for k in range(n+1):
        z=q.copy();z[ch.qa['access_door_joint']]=-1.55*k/n;hits,mins,mm=gaps(ch,z)
        if hits or mm:bad=dict(k=k,blockers=hits[:3]);break
        minimum=min(minimum,min(v['reserve_mm'] for cat,v in mins.items() if cat!='self'))
    save('results/service_replay.json',dict(pass_=bad is None,states_checked=k+1,all_moving_door_point_step_mm=1.55*lever/n*1000,min_robot_reserve_mm=minimum,first_failure=bad,scope='617-state robot clearance replay only; no appliance/frame jamb contact or interlock certification'))
    print('SERVICE',bad is None,k+1,flush=True)

def policy_probe():
    job=next(x for x in j.JOBS if x['id']=='A02_grasp');ch=j.load_cell(job);q=np.array(W[j.JOBS.index(job)]['selected']['poses'][0]['q']);ch.forbidden_literal(q);orig=copy.deepcopy(ch.contact_windows);out=[]
    def probe(label):
        ch.forbidden_literal(q);out.append(dict(label=label,adapter_permissions=[sorted(x) for x in c.permitted(ch)],independent_permissions=[sorted(x) for x in own_permissions(ch,q)]))
    probe('actual_own_support')
    for w in ch.contact_windows:w['support_id']='wrong_support_identity'
    probe('wrong_support_id')
    ch.contact_windows=copy.deepcopy(orig)
    for w in ch.contact_windows:w['object_id']='output_tomato'
    probe('wrong_object_id')
    ch.contact_windows=copy.deepcopy(orig)
    for w in ch.contact_windows:w['kind']='working_stroke'
    ch.working_stroke=False;probe('working_on_nonworking_path')
    save('results/policy_probe.json',dict(rows=out))

def transit():
    # Three additional DISTINCT required meal seams, in their proposed post-release
    # full scenes. These are independent proposals, never conserved-meal credit.
    motion=read(UP/'results/motion.json');ordered=read(UP/'results/state_sequence.json')['ordered_obligations'];byid={x['id']:x for x in ordered}
    seams=[x for x in motion['connections'] if x['from_'].endswith('_release')][:3];out=[]
    for seq,edge in enumerate(seams):
        if not args.lo<=seq<args.hi:continue
        source=byid[edge['from_']];dest=byid[edge['to']];ws=W[next(i for i,x in enumerate(j.JOBS) if x['id']==source['id'])];wg=W[next(i for i,x in enumerate(j.JOBS) if x['id']==dest['id'])]
        poses=copy.deepcopy(source['locations']);poses[source['held']]=source['origin'];ch=c.Cell(j.V,None,poses);src=j.load_cell(source);dst=j.load_cell(dest)
        def mapped(other,q):
            result=ch.q0.copy()
            for name in ch.qa:
                if name in other.qa and ch.m.jnt_type[ch.jid[name]]==other.m.jnt_type[other.jid[name]]:
                    n=7 if ch.m.jnt_type[ch.jid[name]]==0 else 1;result[ch.qa[name]:ch.qa[name]+n]=q[other.qa[name]:other.qa[name]+n]
            # The placed pan is at the declared seat. Preserve all other physical
            # appliance states; opening jaws is only an unverified prerequisite.
            for name in poses:
                if name+'_joint' in ch.qa:
                    k=ch.qa[name+'_joint'];result[k:k+7]=ch.q0[k:k+7]
            for name in ('R_jaw_minus','R_jaw_plus'):result[ch.qa[name]]=-.01
            return result
        a=mapped(src,np.array(ws['selected']['poses'][-1]['q']));b=mapped(dst,np.array(wg['selected']['poses'][0]['q']));hs=c.hand(ch,[0,.24,1.32]);c.s.PARK=np.array(b);planner=c.Planner(ch,hs,seed=9060+seq,seconds=65)
        for k,name in enumerate(planner.names):planner.limits[k]=ch.m.jnt_range[ch.jid[name]]
        stages=[]
        for target in ([0,.24,1.32],[-.2,.25,1.32],[0,.4,1.32]):
            q,e=ch.solve(np.array(target),ch.rot,a);hits,mins,mm=gaps(ch,q);rat,gr,_=loads(ch,q,hs);okay=e['position_mm']<=5 and e['orientation_deg']<=3 and not hits and not mm and rat<=1 and gr>=1
            stages.append(dict(target=target,pass_=okay))
            if okay:c.s.PARK=q
        result=planner.plan(a,b,hs,hs);independent=None
        if result['ok']:independent=replay(ch,result['path'],hs)
        rejection=None
        if result.get('last_rejection'):
            hits,mins,mm=gaps(ch,np.array(result['last_rejection']['q']));rejection=dict(hits=hits[:3],permission_mismatches=mm)
        pb=IndependentBound(ch);out.append(dict(index=seq,from_=edge['from_'],to=edge['to'],allocated_seconds=65,planner=result,independent_path_replay=independent,independent_rejection=rejection,stages=stages,direct_endpoint_displacement_bound_m=pb.segment(a,b),prerequisite_release_unverified=True,persistent_meal_admitted=False,scope='Independent 65s isolated proposal for a required post-release meal seam; source/goal food and capture states are unqualified'))
        save(f'results/additional_connections_{args.lo}_{args.hi}.json',dict(rows=out));print('EXTRA CONNECTION',edge['from_'],edge['to'],result['ok'],round(result['planner_time_s'],1),flush=True)

ap=argparse.ArgumentParser();ap.add_argument('task',choices=['provenance','static','strokes','motion','prefix','service','policy','transit']);ap.add_argument('--lo',type=int,default=0);ap.add_argument('--hi',type=int,default=17);args=ap.parse_args()
if args.task=='motion':motion(args.lo,args.hi)
else:{'provenance':provenance,'static':static,'strokes':strokes,'prefix':prefix,'service':service,'policy':policy_probe,'transit':transit}[args.task]()
