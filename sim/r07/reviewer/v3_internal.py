from v3_common import *
from planner_r05 import Planner
from point_bound import PointBound
idx=int(sys.argv[1]);saved=read(f'motion_v2/{v.ID}/internal_{idx}.json');w=candidate(idx);ph,sg,key=v.items[idx];ch=v.scene(idx);ib=IndependentBound(ch);pb=PointBound(ch)
static_seed=w['k'];w=copy.deepcopy(w)
# Later static search can select the opposite legal jaw-axis branch. Recover
# the saved path's declared branch, without changing any q, geometry or gate.
branch_scores=[]
for branch in (0,1):
    errors=[]
    for ei,e in enumerate(saved['edges']):
        for q,hands in ((e['path'][0],sg['poses'][ei]),(e['path'][-1],sg['poses'][ei+1])):
            ch.d.qpos[:]=q;mujoco.mj_kinematics(ch.m,ch.d)
            for side,h in hands.items():
                sid=ch.m.site(side+'_prep').id
                errors.append(np.linalg.norm(Rotation.from_matrix(ch.target_rotation(h,branch).T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec()))
    branch_scores.append(max(errors,default=0))
w['k']=int(np.argmin(branch_scores))
started=time.monotonic();rows=[];maxstep=delta=actual=maxtq=0.;mingrip=math.inf;minima={};endpoints=[];moving=[];bad=None;dur=0.;edge_arc=[]
for ei,e in enumerate(saved['edges']):
    if not e['ok']:bad=dict(edge=ei,kind='missing failed edge');break
    path=np.array(e['path']);ha,hb=sg['poses'][ei:ei+2]
    if ei and not np.allclose(saved['edges'][ei-1]['path'][-1],path[0],atol=1e-10,rtol=0):bad=dict(edge=ei,kind='continuity');break
    # Check reference endpoints without windows, then apply only the archived own-support windows.
    ch.contact_windows=[];ch.working_stroke=False
    for q,h in ((path[0],ha),(path[-1],hb)):
        p=independent_pose(ch,q,h,w['k']);endpoints.append(p)
        if not p['ok']:bad=dict(edge=ei,kind='endpoint');break
    if bad:break
    ch.working_stroke=sg['action']=='process';ch.contact_windows=e.get('contact_windows',[])
    common={side:dict(h,contacts=[c for c in h.get('contacts',[]) if c in hb.get(side,{}).get('contacts',[])]) for side,h in ha.items()}
    pl=Planner(ch,ha,seconds=65);arc=0.
    for si,(a,b) in enumerate(zip(path,path[1:])):
        D=ib.segment(a,b);delta=max(delta,abs(D-pb.segment_bound(a,b)));N=max(1,math.ceil(D/.004));maxstep=max(maxstep,D/N*1000);arc+=D
        moved={side:any(abs(a[ch.qa[n]]-b[ch.qa[n]])>1e-9 for n in s.ck.ARMS[side]+[side+'_carriage_x']) for side in ('R','L')};moving.append(moved)
        dq=abs(b-a);vs=[];acc=[]
        for side in ('R','L'):
            for n in s.ck.ARMS[side]:vs.append(dq[ch.qa[n]]/.35);acc.append(dq[ch.qa[n]]/.35)
            n=side+'_carriage_x';loaded=side in ha and ha[side]['held']!='empty';vs.append(dq[ch.qa[n]]/(.1 if loaded else .2));acc.append(dq[ch.qa[n]]/.3)
        vs.append(D/.05);acc.append(D/.3);vmax=1/max(vs,default=1e-30) if max(vs,default=0)>0 else math.inf;amax=1/max(acc,default=1e-30) if max(acc,default=0)>0 else math.inf
        dur+=2/math.sqrt(amax) if vmax*vmax>=amax else 1/vmax+vmax/amax
        for k in range(N+1):
            q=a+(b-a)*k/N;hands=ha if si==0 and k==0 else hb if si==len(path)-2 and k==N else common
            if k:actual=max(actual,ib.actual(a+(b-a)*(k-1)/N,q)*1000)
            if not pl.state(q,hands):bad=dict(edge=ei,segment=si,grid=k,kind='gap',detail=pl.last);break
            for cat,ix in ch.bounds.catids.items():
                vals=(ch.bounds.last_lower[ix]-ch.bounds.need[ix])*1000;finite=vals[np.isfinite(vals)]
                if len(finite):minima[cat]=min(minima.get(cat,math.inf),float(min(finite)))
            load=independent_pose(ch,q,hands,w['k'],geometry=False);maxtq=max(maxtq,load['torque']['check']);mingrip=min(mingrip,load['grip']['check'])
            if not load['ranges_ok'] or load['torque']['check']>1 or load['grip']['check']<1 or not all(p['chart_ok'] and p['helper_task_cap_ok'] for p in load['payload']):bad=dict(edge=ei,segment=si,grid=k,kind='range/load',load=load);break
            # These saved successful strokes are helper index (non-working) paths.
            if ch.working_stroke:
                from scipy.spatial.transform import Slerp
                alpha=(si+k/N)/(len(path)-1)
                for side in ha:
                    target=(1-alpha)*np.array(ha[side]['pos'])+alpha*np.array(hb[side]['pos'])
                    rot=Slerp([0,1],Rotation.from_matrix([ch.target_rotation(ha[side],w['k']),ch.target_rotation(hb[side],w['k'])]))(alpha).as_matrix()
                    sid=ch.m.site(side+'_prep').id
                    pe=np.linalg.norm(ch.d.site_xpos[sid]-target)*1000
                    oe=np.degrees(np.linalg.norm(Rotation.from_matrix(rot.T@ch.d.site_xmat[sid].reshape(3,3)).as_rotvec()))
                    if pe>5 or oe>3:bad=dict(kind='working line',side=side,position_mm=float(pe),orientation_deg=float(oe));break
                if bad:break
            rows.append(dict(edge=ei,segment=si,grid=k,intervals=N))
        if bad:break
    edge_arc.append(arc)
    if bad:break
dump(f'internal_{idx}.json',dict(index=idx,stroke=key,layout=v.ID,pass_=bad is None,blocker=bad,states_checked=len(rows),endpoints=endpoints,max_point_step_mm=maxstep,max_actual_sphere_step_mm=actual,max_bound_delta_m=delta,max_check_torque_ratio=maxtq,min_grip_margin=None if math.isinf(mingrip) else mingrip,minimum_clearance_reserve_mm=minima,point_arc_bound_m=sum(edge_arc),duration_s=dur,simultaneous_moving_segments=sum(all(x.values()) for x in moving),elapsed_s=time.monotonic()-started,method='Independent ancestor and local point bound, full saved trajectory interpolation, unchanged state collision policy, independently recomputed ranges/payload/Jacobian torque/grip, window-free endpoint pose checks.'))
print('INTERNAL',idx,bad,len(rows),maxstep,maxtq,dur,flush=True)
