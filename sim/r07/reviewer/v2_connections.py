from v2_common import *
from planner_r05 import Planner
from point_bound import PointBound
verified=json.loads((O/'reverify.json').read_text());started=time.monotonic();rank=[];missing=[]
for i in range(104):
    wa,wb=candidate(i),candidate(i+1)
    if not wa or not wb:missing.append(i);continue
    ch=v.scene(i);a=np.array(wa['poses'][-1]['q']);b=np.array(wb['poses'][0]['q']);ib=IndependentBound(ch);D=ib.segment(a,b)
    margins=[vv['reserve_mm'] for r in verified['rows'][i:i+2] for p in r['checks'] for vv in p['min_clearance'].values() if vv['required_mm']>0]
    rank.append(dict(index=i,point_displacement_upper_bound_m=D,bound_delta_m=abs(D-PointBound(ch).segment_bound(a,b)),closest_endpoint_gate_reserve_abs_mm=min(map(abs,margins)),source_terminal_available=len(wa['poses'])==len(v.items[i][1]['poses'])))
longest=max(rank,key=lambda x:x['point_displacement_upper_bound_m'])['index'];tightest=min(rank,key=lambda x:x['closest_endpoint_gate_reserve_abs_mm'])['index']
available={r['index'] for r in rank};ids=sorted((set([0,1,2,3,4,5,6,12,13,14,15,16,17,18,19,20,23,24,30,31,41,45,46,54,66,67,69,82,83,85,86,87,90,91,92])&available)|{longest,tightest});rows=[]
for i in ids:
    wa,wb=candidate(i),candidate(i+1);a=np.array(wa['poses'][-1]['q']);b=np.array(wb['poses'][0]['q']);ch=v.scene(i);ch2=v.scene(i+1);ha=v.items[i][1]['poses'][len(wa['poses'])-1];hb=v.items[i+1][1]['poses'][0];ia=IndependentBound(ch);ib=IndependentBound(ch2);D=max(ia.segment(a,b),ib.segment(a,b));N=max(1,math.ceil(D/.004));pl=Planner(ch,ha,seconds=65);pl2=Planner(ch2,hb,seconds=65)
    windows=mo.windows(ch,a,ha)+mo.windows(ch2,b,hb)
    for cc in (ch,ch2):cc.contact_windows=windows;cc.working_stroke=False
    endpoints=[]
    for name,pp,q in [('departure',pl,a),('arrival',pl2,b)]:
        ok=pp.state(q);endpoints.append(dict(scene=name,pass_=ok,rejection=None if ok else pp.last,work_permissions=[c for c in pp.ch.allowed if c.get('kind')=='working_stroke']))
    first=None;states=0;actual=0.
    for k in range(N+1):
        q=a+(b-a)*k/N
        if k:actual=max(actual,ia.actual(a+(b-a)*(k-1)/N,q)*1000,ib.actual(a+(b-a)*(k-1)/N,q)*1000)
        for name,pp in [('departure',pl),('arrival',pl2)]:
            states+=1
            if not pp.state(q):first=dict(scene=name,grid_index=k,rejection=pp.last);break
        if first:break
    moving={side:bool(any(abs(a[ch.qa[n]]-b[ch.qa[n]])>1e-8 for n in s.ck.ARMS[side]+[side+'_carriage_x'])) for side in ('R','L')}
    rows.append(dict(index=i,from_stroke=v.items[i][2],to_stroke=v.items[i+1][2],source_terminal_available=len(wa['poses'])==len(v.items[i][1]['poses']),saved_connection_path_available=False,diagnostic_pass=first is None,meal_pass=False,states_checked=states,endpoints=endpoints,first_rejection=first,grid_intervals=N,maximum_grid_bound_mm=D/N*1000,maximum_sphere_step_mm=actual,moving_arms=moving,signature_compatible=mo.signature(ha)==mo.signature(hb)))
    print('CONNECTION',i,'FAIL' if first else 'diagnostic clear',states,flush=True)
    dump('connections.json',dict(rows=rows,rank=rank,longest_candidate_index=longest,closest_gate_candidate_index=tightest,missing_candidate_pairs=missing,checked_connections=len(rows),states_checked=sum(r['states_checked']+2 for r in rows),two_arm_candidates=sum(all(r['moving_arms'].values()) for r in rows),elapsed_s=time.monotonic()-started,scope='No saved meal trajectories exist. These are independent bounded-grid straight diagnostics and endpoint checks in both populated scenes. An incomplete source uses its last available pose, explicitly flagged, not an invented terminal pose. They cannot satisfy a demand to fully replay 20 saved connected meal paths.'))
