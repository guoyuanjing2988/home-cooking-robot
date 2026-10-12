from v4_common import *
from planner_r05 import Planner
from point_bound import PointBound
from oriented_motion_v4_r07 import install
install(mo)
import hashlib
started=time.monotonic();rank=[];rows=[];root=I/'results/motion_v4'/v.ID
verified=json.loads((O/'reverify.json').read_text())
previous=json.loads((O/'connections.json').read_text()) if (O/'connections.json').exists() else {'rows':[],'rank':[]}
done={r['index']:r for r in previous['rows']};oldrank={r['index']:r for r in previous['rank']}
def internal(i):
    p=root/f'internal_{i}.json'
    return json.loads(p.read_text()) if p.exists() else None
for i in range(len(v.items)-1):
    if i in done:
        rows.append(done[i]);rank.append(oldrank[i]);continue
    wa,wb=candidate(i),candidate(i+1)
    if not wa or not wb:continue
    ma,mb=internal(i),internal(i+1)
    a=np.array(ma['edges'][-1]['path'][-1] if ma and ma['ok'] else wa['poses'][-1]['q'])
    b=np.array(mb['edges'][0]['path'][0] if mb and mb['ok'] else wb['poses'][0]['q'])
    ch=v.scene(i);ib=IndependentBound(ch);D=ib.segment(a,b)
    margins=[x['reserve_mm'] for r in verified['rows'][i:i+2] for p in r['checks'] for x in p['min_clearance'].values() if x['required_mm']>0]
    rank.append(dict(index=i,point_displacement_bound_m=D,closest_endpoint_gate_mm=min(map(abs,margins),default=None),bound_delta_m=abs(D-PointBound(ch).segment_bound(a,b))))
    ch2=v.scene(i+1);ha=copy.deepcopy(v.items[i][1]['poses'][len(wa['poses'])-1]);hb=copy.deepcopy(v.items[i+1][1]['poses'][0])
    for hs in (ha,hb):
        for h in hs.values():
            h['contacts']=[c for c in h.get('contacts',[]) if c['kind']=='grasp_release_support']
            for level in ('nominal','check'):h[level+'_forces_N']=[[0,0,0]];h[level+'_moments_Nm']=[[0,0,0]]
    p=root/f'connection_{i}.json';saved=json.loads(p.read_text()) if p.exists() else {}
    path=saved.get('planner',{}).get('path') or [a.tolist(),b.tolist()];haspath=bool(saved.get('planner',{}).get('path'))
    windows=saved.get('contact_windows') if haspath else [w for w in mo.windows(ch,a,ha)+mo.windows(ch2,b,hb) if w['kind']=='grasp_release_support']
    chs=[ch,ch2];pls=[Planner(c,ha,seconds=65) for c in chs];ibs=[IndependentBound(c) for c in chs]
    for c in chs:c.working_stroke=False;c.contact_windows=windows
    states=0;bad=None;step=0.;mt=0.;mg=math.inf;minimum={};work_leaks=[]
    for endpoint,q in [('source',np.array(path[0])),('destination',np.array(path[-1]))]:
        for ci,(c,pl) in enumerate(zip(chs,pls)):
            states+=1
            hs=(ha if endpoint=='source' else hb) if haspath or mo.signature(ha)==mo.signature(hb) else (ha if ci==0 else hb)
            if not pl.state(q,hs):bad=dict(scene=ci,endpoint=endpoint,kind='gap',detail=pl.last);break
        if bad:break
    for si,(x,y) in enumerate(zip(np.array(path),np.array(path)[1:]) if bad is None else []):
        D=max(bb.segment(x,y) for bb in ibs);N=max(1,math.ceil(D/.004));step=max(step,D/N*1000)
        for k in range(N+1):
            q=x+(y-x)*k/N
            hs=ha if si==0 and k==0 else hb if si==len(path)-2 and k==N else {s:dict(h,contacts=[]) for s,h in ha.items()}
            for ci,(c,pl) in enumerate(zip(chs,pls)):
                states+=1
                # For changed attachments this remains a two-scene diagnostic,
                # not a permission to change physical ownership.
                hands=hs if haspath or mo.signature(ha)==mo.signature(hb) else (ha if ci==0 else hb)
                if not pl.state(q,hands):bad=dict(scene=ci,segment=si,grid=k,kind='gap',detail=pl.last);break
                work_leaks.extend(ca for ca in c.allowed if ca.get('kind')=='working_stroke')
                load=independent_pose(c,q,hands,0,geometry=False);mt=max(mt,load['torque']['check']);mg=min(mg,load['grip']['check'])
                if not load['ranges_ok'] or load['torque']['check']>1 or load['grip']['check']<1 or not all(p['chart_ok'] for p in load['payload']):bad=dict(kind='load/range',load=load);break
                for cat,ix in c.bounds.catids.items():
                    vv=(c.bounds.last_lower[ix]-c.bounds.need[ix])*1000;vv=vv[np.isfinite(vv)&(vv<1e6)]
                    if len(vv):minimum[cat]=min(minimum.get(cat,math.inf),float(min(vv)))
            if bad:break
        if bad:break
    source_hashes=[hashlib.sha256((I/p).read_bytes()).hexdigest() for p in saved.get('source_paths',[])]
    joined=None
    if haspath:
        downstream=read(str((root/f'internal_{i+1}.json').relative_to(I/'results')))
        if saved.get('rebased_downstream_bundle'):downstream=json.loads((I/saved['rebased_downstream_bundle']).read_text())
        joined=bool(np.max(abs(np.array(path[0])-a))<1e-9 and np.max(abs(np.array(path[-1])-np.array(downstream['edges'][0]['path'][0])))<1e-9)
    row=dict(index=i,saved_path_available=haspath,submitted_local_pass=saved.get('pass_',False),diagnostic_pass=bad is None,states_checked=states,max_point_step_mm=step,first_rejection=bad,max_torque_ratio=mt,min_grip_margin=None if math.isinf(mg) else mg,minimum_reserve_mm=minimum,source_terminal_available=len(wa['poses'])==len(v.items[i][1]['poses']),signature_compatible=mo.signature(ha)==mo.signature(hb),source_hashes_match=source_hashes==saved.get('source_sha256',[]),continuous_to_downstream=joined,working_permission_leaks=work_leaks,meal_pass=False,two_arm_overlap=False)
    rows.append(row);print('CONNECTION',i,haspath,bad is None,states,flush=True)
    dump('connections.json',dict(rows=rows,rank=rank,checked_connections=len(rows),states_checked=sum(r['states_checked'] for r in rows),longest_candidate_index=max(rank,key=lambda r:r['point_displacement_bound_m'])['index'],tightest_candidate_index=min(rank,key=lambda r:r['closest_endpoint_gate_mm'])['index'],scope='All available adjacent endpoint candidates. Fully replay all saved local paths; other entries are straight rejection diagnostics, not missing meal trajectories or new planner searches.',elapsed_s=time.monotonic()-started))
