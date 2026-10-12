from common import *
from point_bound import PointBound
from planner_r05 import Planner
started=time.monotonic();rank=[];verified=json.loads((O/'reverify_0_105.json').read_text())
for i in range(104):
    ph,sg,key=mo.items[i];ch=mo.scene(ph,sg,i)
    a=np.array(read('final_static/'+str(i)+'.json')['poses'][-1]['q']);b=np.array(read('final_static/'+str(i+1)+'.json')['poses'][0]['q'])
    ib=IndependentBound(ch);D=ib.segment(a,b);pb=PointBound(ch).segment_bound(a,b)
    margins=[v['reserve_mm'] for r in verified['rows'][i:i+2] for p in r['checks'] for cat,v in p['min_clearance'].items() if v['required_mm']>0]
    rank.append(dict(index=i,point_displacement_upper_bound_m=D,submitted_bound_m=pb,bound_delta_m=abs(D-pb),closest_endpoint_gate_reserve_abs_mm=min(map(abs,margins))))
longest=max(rank,key=lambda r:r['point_displacement_upper_bound_m'])['index'];tightest=min(rank,key=lambda r:r['closest_endpoint_gate_reserve_abs_mm'])['index']
ids=sorted(set([0,1,2,4,5,6,12,16,30,31,41,45,46,54,66,67,79,83,85,86,87,90,94,95,101,102,longest,tightest]));rows=[]
for i in ids:
    ph,sg,key=mo.items[i];ph2,sg2,key2=mo.items[i+1];ch=mo.scene(ph,sg,i);ch2=mo.scene(ph2,sg2,i+1)
    a=np.array(read('final_static/'+str(i)+'.json')['poses'][-1]['q']);b=np.array(read('final_static/'+str(i+1)+'.json')['poses'][0]['q']);ha=sg['poses'][-1];hb=sg2['poses'][0]
    ia=IndependentBound(ch);ib=IndependentBound(ch2);D=max(ia.segment(a,b),ib.segment(a,b));N=max(1,math.ceil(D/.004));pl=Planner(ch,ha,seed=807+i,seconds=65);pl2=Planner(ch2,hb,seed=907+i,seconds=65)
    wa=mo.windows(ch,a,ha);wb=mo.windows(ch2,b,hb);ch.contact_windows=wa+wb;ch2.contact_windows=wa+wb;ch.working_stroke=ch2.working_stroke=False
    endpoints=[]
    for scene,planner,q in [('departure',pl,a),('arrival',pl2,b)]:
        ok=planner.state(q);endpoints.append(dict(scene=scene,ok=ok,first_rejection=planner.last,work_permissions_remaining=[c for c in planner.ch.allowed if c.get('kind')=='working_stroke']))
    states=0;first=None;actual=0;previous=None
    for k in range(N+1):
        q=a+(b-a)*k/N
        if previous is not None:actual=max(actual,ia.actual(previous,q),ib.actual(previous,q))
        previous=q.copy()
        for scene,planner in [('departure',pl),('arrival',pl2)]:
            states+=1
            if not planner.state(q):first=dict(scene=scene,grid_index=k,grid_intervals=N,first_rejection=planner.last);break
        if first:break
    moving={side:bool(any(abs(a[ch.qa[n]]-b[ch.qa[n]])>1e-8 for n in s.ck.ARMS[side]+[side+'_carriage_x'])) for side in ('R','L')}
    rows.append(dict(index=i,from_stroke=key,to_stroke=key2,submitted_trajectory_available=False,replay_kind='Reconstructed straight joint-space diagnostic; stops at first failed state, not a replay of a nonexistent saved trajectory',endpoints=endpoints,states_checked=states,pass_=first is None,first_rejection=first,point_segment_bound_m=D,grid_intervals=N,maximum_grid_bound_mm=D/N*1000,maximum_actual_sphere_step_mm=actual*1000,moving_arms=moving,attachment_signature_compatible=mo.signature(ha)==mo.signature(hb),conserved_meal_pass=False))
    print('connection',i,'FAIL' if first else 'diagnostic clear','states',states,flush=True)
    dump('connections.json',dict(rows=rows,rank=rank,longest_candidate_index=longest,closest_gate_candidate_index=tightest,checked_connections=len(rows),states_checked=sum(r['states_checked']+len(r['endpoints']) for r in rows),two_arm_candidates=sum(all(r['moving_arms'].values()) for r in rows),elapsed_s=time.monotonic()-started,scope='R07 has zero submitted accepted or proposed meal paths. Endpoint and bounded-grid straight diagnostics independently confirm rejection, without claiming randomized-search reproduction or global impossibility. Longest ranks candidate endpoint displacement bounds; closest gate ranks diagnostic endpoints. There is no accepted longest/tightest meal trajectory.'))
# Full replay of the only saved diagnostic path, then both-arm passing rejection.
aux=read('aux_paths.json');root=__import__('xml.etree.ElementTree',fromlist=['ElementTree']).parse(I/aux['model_xml']);m=mujoco.MjModel.from_xml_string(__import__('xml.etree.ElementTree',fromlist=['ElementTree']).tostring(root.getroot(),encoding='unicode'))
ch=object.__new__(rt.Checker);ch.desc=s.ck.hand([0,0,1],jaw_axis=[0,1,0]);ch.bind_model(m);ch.hands={};ch.allowed=[];ch.contact_windows=[];ch.working_stroke=False
ib=IndependentBound(ch);pb=PointBound(ch);pl=Planner(ch,{},seed=1007,seconds=65);path=np.array(aux['path']);samples=[];maxstep=actual=delta=0;minreserve={}
for a,b in zip(path,path[1:]):
    D=ib.segment(a,b);delta=max(delta,abs(D-pb.segment_bound(a,b)));N=max(1,math.ceil(D/.004));maxstep=max(maxstep,D/N*1000)
    for k in range(N+1):
        q=a+(b-a)*k/N
        if k:actual=max(actual,ib.actual(a+(b-a)*(k-1)/N,q)*1000)
        ok=pl.state(q);tq=ch.torque_multi(q,{},{});hits,mins,_=f.contacts(ch,q)
        for cat,r in mins.items():
            if cat not in minreserve or r['reserve_mm']<minreserve[cat]['reserve_mm']:minreserve[cat]=r
        samples.append(dict(ok=ok and tq['ratio']<=1,torque_ratio=tq['ratio'],q=q.tolist(),hits=hits[:8]))
passing=read('passing.json');a=path[0];b=a.copy();ar=ch.qa['R_carriage_x'];al=ch.qa['L_carriage_x'];b[ar],b[al]=a[al],a[ar];D=ib.segment(a,b);N=max(1,math.ceil(D/.004));passed=True;first=None;states=0
for k in range(N+1):
    q=a+(b-a)*k/N;states+=1
    if not pl.state(q):passed=False;first=dict(grid_index=k,q=q.tolist(),rejection=pl.last);break
dump('aux_and_passing.json',dict(aux_pass=all(r['ok'] for r in samples),samples=samples,maximum_independent_grid_bound_mm=maxstep,maximum_sphere_step_mm=actual,maximum_bound_disagreement_m=delta,min_clearance=minreserve,passing=dict(submitted_pass=passing['pass_'],independent_direct_pass=passed,states_checked=states,grid_intervals=N,maximum_grid_bound_mm=D/N*1000,first_rejection=first,moving_arms=['R','L'],saved_randomized_rejection=passing['planner']['last_rejection']),scope=aux['scope']))
